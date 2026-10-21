#!/usr/bin/env python3
"""Match the ledger's named generators and the Virginia permit sites against Climate TRACE asset emissions.

Accepts whatever the Climate TRACE download builder exports (2026 wizard at climatetrace.org/downloads):
  a ZIP or a folder or a CSV; monthly or annual rows; many gases; several sectors; an optional confidence
  file. The loader finds the asset-level emissions CSV(s), keeps electricity-generation rows, keeps the
  CO2e-100yr gas, sums months to a year per asset, and reads the confidence file if present.

Column names are located by substring (source_id / source_name / lat / lon / gas / emissions_quantity /
start_time / subsector / sector / capacity / activity), per the v5.11.0 schema:
  https://climatetrace.org/news/beyond-the-ui-what039s-in-the-asset-metadata

Two match passes:
  1. Named plants from the ledger (PLANTS below): name-token overlap first, then nearest within --radius-km.
  2. Virginia permit sites (pipeline/out/va_permits.csv, if present): for each site, the nearest Climate TRACE
     power asset within --radius-km, as a "neighbouring generation" context, not an attribution.

Every output row says how it matched (name|nearest) and the distance. 'nearest' rows are leads, not confirmations.

Usage:
  python3 climate_trace_match.py --input ~/Downloads/<export>.zip --out ../data/climate_trace_seed/
  python3 climate_trace_match.py --fixture --out out/
"""
import argparse, csv, io, json, math, os, re, sys, zipfile, glob, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

PLANTS = [
  {"entry":"us-va-chesterfield-dominion-cerc-gas","plant":"Chesterfield","alt":["Chesterfield Power Station","Chesterfield Energy Reliability"],"lat":37.38,"lon":-77.38,"permit_mw":944,"note":"944 MW peaker approved 2025 (SCC PUR-2025-00037); existing Chesterfield station on same site"},
  {"entry":"us-tn-memphis-xai-colossus-turbines","plant":"xAI Colossus","alt":["Colossus","Southwest Memphis","Allen"],"lat":35.07,"lon":-90.13,"permit_mw":247,"note":"on-site turbines; TVA Allen plant is the nearest grid asset"},
  {"entry":"us-ms-southaven-xai-1.2gw-gas","plant":"xAI Southaven","alt":["Southaven","MZX"],"lat":34.97,"lon":-90.0,"permit_mw":1200,"note":"permitted 2026, may not be in inventory yet"},
  {"entry":"us-la-richland-meta-entergy-gas","plant":"Entergy Richland Parish","alt":["Holly Ridge","Richland","Delhi"],"lat":32.44,"lon":-91.5,"permit_mw":2262,"note":"approved 2025, COD later; may not be in inventory"},
  {"entry":"us-pa-homer-city-gas-campus","plant":"Homer City","alt":["Homer City Generating"],"lat":40.51,"lon":-79.19,"permit_mw":4678,"note":"former coal plant; gas campus permitted 2025"},
  {"entry":"us-wi-mount-pleasant-microsoft-we-energies","plant":"Oak Creek","alt":["Oak Creek Power Plant","Elm Road","Paris"],"lat":42.86,"lon":-87.85,"permit_mw":1100,"note":"existing Oak Creek/Elm Road units; new simple-cycle approved 2025"},
  {"entry":"us-pa-susquehanna-talen-aws-colocation","plant":"Susquehanna","alt":["Susquehanna Steam Electric"],"lat":41.09,"lon":-76.15,"permit_mw":1920,"note":"existing nuclear under PPA (should show ~0 CO2e)"},
]

def hav(lat1,lon1,lat2,lon2):
    R=6371.0; p1,p2=math.radians(lat1),math.radians(lat2)
    d=math.sin((p2-p1)/2)**2+math.cos(p1)*math.cos(p2)*math.sin(math.radians(lon2-lon1)/2)**2
    return 2*R*math.asin(math.sqrt(d))

def col(headers,*needles,exclude=()):
    for h in headers:
        hl=h.lower()
        if all(n in hl for n in needles) and not any(x in hl for x in exclude): return h
    return None

def tokens(s): return {t for t in re.split(r"[^a-z0-9]+",str(s).lower()) if len(t)>2 and t not in {"the","and","power","plant","station","energy","center","generating","llc","inc","unit","units","facility","electric"}}

def open_sources(path):
    """Yield (name, text) for every CSV inside a zip/folder/csv."""
    if os.path.isdir(path):
        for f in sorted(glob.glob(os.path.join(path,"**","*.csv"),recursive=True)): yield f, open(f,encoding="utf-8-sig",errors="replace").read()
    elif path.lower().endswith(".zip"):
        z=zipfile.ZipFile(path)
        for n in z.namelist():
            if n.lower().endswith(".csv"): yield n, io.TextIOWrapper(z.open(n),encoding="utf-8-sig",errors="replace").read()
            elif n.lower().endswith(".zip"):
                inner=zipfile.ZipFile(io.BytesIO(z.read(n)))
                for m in inner.namelist():
                    if m.lower().endswith(".csv"): yield f"{n}/{m}", io.TextIOWrapper(inner.open(m),encoding="utf-8-sig",errors="replace").read()
    else:
        yield path, open(path,encoding="utf-8-sig",errors="replace").read()

def load_assets(path, verbose=True):
    assets={}; conf={}; files_seen=[]
    for name,text in open_sources(path):
        rows=list(csv.DictReader(io.StringIO(text)))
        if not rows: continue
        hdr=list(rows[0].keys()); low=name.lower()
        files_seen.append((name,len(rows)))
        sid=col(hdr,"source_id") or col(hdr,"asset_id") or col(hdr,"asset","id")
        # confidence file: has source_id and per-field ratings, no emissions_quantity
        if sid and ("confidence" in low) and not col(hdr,"emissions_quantity"):
            tc=col(hdr,"total_co2e_100") or col(hdr,"co2e_100") or col(hdr,"emissions")
            for r in rows:
                if r.get(sid): conf[r[sid]]=r.get(tc) or ""
            continue
        q=col(hdr,"emissions_quantity") or col(hdr,"emissions","quantity")
        if not (sid and q): continue
        c={"id":sid,"name":col(hdr,"source_name") or col(hdr,"asset_name") or col(hdr,"name"),"lat":col(hdr,"lat"),"lon":col(hdr,"lon"),
           "gas":col(hdr,"gas"),"q":q,"sub":col(hdr,"subsector"),"sec":col(hdr,"sector",exclude=("subsector",)),"start":col(hdr,"start_time") or col(hdr,"start"),
           "cap":col(hdr,"capacity",exclude=("factor","units")),"act":col(hdr,"activity",exclude=("units",)),"capu":col(hdr,"capacity_units"),"country":col(hdr,"iso3") or col(hdr,"country"),"type":col(hdr,"source_type") or col(hdr,"asset_type")}
        if not (c["lat"] and c["lon"]): continue
        kept=0
        for r in rows:
            sub=(r.get(c["sub"]) or "").lower(); sec=(r.get(c["sec"]) or "").lower()
            if sub and "electricity" not in sub and "power" not in sec: continue
            if not sub and sec and "power" not in sec: continue
            g=(r.get(c["gas"]) or "").lower().replace(" ","").replace("-","").replace("_","")
            if c["gas"] and g and not ("co2e100" in g or g in ("co2e","co2e100yr")): continue
            try: lat,lon=float(r[c["lat"]]),float(r[c["lon"]])
            except Exception: continue
            try: qty=float(r.get(c["q"]) or 0)
            except Exception: qty=0.0
            yr=(r.get(c["start"]) or "")[:4]
            a=assets.setdefault(r[c["id"]],{"id":r[c["id"]],"name":r.get(c["name"],""),"lat":lat,"lon":lon,"subsector":r.get(c["sub"],""),"country":r.get(c["country"],""),"type":r.get(c["type"],""),
                                             "capacity":r.get(c["cap"],""),"capacity_units":r.get(c["capu"],""),"by_year":collections.defaultdict(float),"activity_by_year":collections.defaultdict(float),"months":collections.defaultdict(int)})
            a["by_year"][yr]+=qty; a["months"][yr]+=1; kept+=1
            try: a["activity_by_year"][yr]+=float(r.get(c["act"]) or 0)
            except Exception: pass
        if verbose: print(f"  {name}: {len(rows)} rows, kept {kept} electricity/CO2e rows")
    for a in assets.values():
        yrs=sorted(a["by_year"]);
        a["years"]={y:{"tco2e":round(a["by_year"][y]),"months":a["months"][y],"activity":round(a["activity_by_year"][y])} for y in yrs}
        full=[y for y in yrs if a["months"][y]>=12]
        a["latest_full_year"]=full[-1] if full else (yrs[-1] if yrs else "")
        a["tco2e_latest"]=a["years"][a["latest_full_year"]]["tco2e"] if a["latest_full_year"] else 0
        a["partial"]=bool(a["latest_full_year"]) and a["months"][a["latest_full_year"]]<12
        a["confidence"]=conf.get(a["id"],"")
        for k in ("by_year","activity_by_year","months"): a.pop(k)
    if not assets: sys.exit(f"No asset-level electricity rows found. CSVs seen: {files_seen}")
    return list(assets.values()), files_seen

def best_match(lat,lon,names,assets,radius):
    ptoks=set().union(*[tokens(n) for n in names]) if names else set()
    best=None
    for a in assets:
        d=hav(lat,lon,a["lat"],a["lon"])
        if d>radius: continue
        ov=len(ptoks & tokens(a["name"])) if ptoks else 0
        score=(ov,-d)
        if best is None or score>best[0]: best=(score,a,d,ov)
    return best

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",help="Climate TRACE export: zip, folder or csv")
    ap.add_argument("--power-zip",help="alias for --input")
    ap.add_argument("--csv",help="alias for --input")
    ap.add_argument("--fixture",action="store_true")
    ap.add_argument("--radius-km",type=float,default=15.0)
    ap.add_argument("--va-permits",default=os.path.join(ROOT,"pipeline","out","va_permits.csv"))
    ap.add_argument("--out",default="out")
    a=ap.parse_args(); os.makedirs(a.out,exist_ok=True)
    src=a.input or a.power_zip or a.csv
    if a.fixture: src=os.path.join(HERE,"fixtures","climate_trace","electricity_generation_emissions_SYNTHETIC.csv"); mode="fixture"
    elif src: mode="live"
    else: sys.exit("Give --input <zip|folder|csv> or --fixture")
    print(f"loading {src}")
    assets,files=load_assets(src)
    print(f"{len(assets)} electricity-generation assets with coordinates")
    label="[FIXTURE DATA - NOT REAL] " if mode=="fixture" else ""

    # pass 1: named plants
    res=[]
    for p in PLANTS:
        b=best_match(p["lat"],p["lon"],[p["plant"]]+p.get("alt",[]),assets,a.radius_km)
        if b:
            _,x,d,ov=b
            res.append({**p,"matched":True,"method":"name" if ov else "nearest","asset_id":x["id"],"asset_name":x["name"],"distance_km":round(d,1),
                        "trace_year":x["latest_full_year"],"trace_tco2e":x["tco2e_latest"],"trace_partial_year":x["partial"],"trace_capacity":x["capacity"],"trace_capacity_units":x["capacity_units"],"trace_confidence":x["confidence"],"trace_years":json.dumps(x["years"]),
                        "sentence":label+f"{p['plant']}: Climate TRACE estimates {x['tco2e_latest']:,.0f} tCO2e in {x['latest_full_year'] or 'n/a'}{' (partial year)' if x['partial'] else ''} for '{x['name']}' ({d:.1f} km, matched by {'name' if ov else 'proximity'}; confidence {x['confidence'] or 'n/a'}); ledger record: {p['permit_mw']} MW, {p['note']}."})
        else:
            res.append({**p,"matched":False,"sentence":label+f"{p['plant']}: no Climate TRACE electricity asset within {a.radius_km} km; {p['note']}."})
    # pass 2: Virginia permit sites -> nearest generation asset (context only)
    va=[]
    if os.path.exists(a.va_permits):
        rows=list(csv.DictReader(open(a.va_permits)))
        hdr=rows[0].keys() if rows else []
        latc=col(hdr,"lat"); lonc=col(hdr,"lon"); mwc=col(hdr,"total_standby_mw") or col(hdr,"mw"); namec=col(hdr,"site_name") or col(hdr,"name"); regc=col(hdr,"registration")
        for r in rows:
            try: lat,lon=float(r[latc]),float(r[lonc])
            except Exception: continue
            b=best_match(lat,lon,[],assets,a.radius_km)
            if b:
                _,x,d,_=b
                va.append({"registration":r.get(regc),"site":r.get(namec),"permit_mw":r.get(mwc),"nearest_asset":x["name"],"asset_id":x["id"],"distance_km":round(d,1),"asset_tco2e":x["tco2e_latest"],"asset_year":x["latest_full_year"],"asset_capacity":x["capacity"],"asset_confidence":x["confidence"]})
            else:
                va.append({"registration":r.get(regc),"site":r.get(namec),"permit_mw":r.get(mwc),"nearest_asset":"","asset_id":"","distance_km":"","asset_tco2e":"","asset_year":"","asset_capacity":"","asset_confidence":""})
        print(f"Virginia: {len(va)} geocoded permit sites, {sum(1 for v in va if v['asset_id'])} with a Climate TRACE generation asset within {a.radius_km} km")

    json.dump({"data_mode":mode,"source":src,"files_seen":files,"assets_loaded":len(assets),"radius_km":a.radius_km,"named_plants":res,"virginia_sites":va},open(os.path.join(a.out,"climate_trace_matches.json"),"w"),indent=1)
    with open(os.path.join(a.out,"climate_trace_matches.csv"),"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=sorted({k for r in res for k in r})); w.writeheader(); [w.writerow(r) for r in res]
    if va:
        with open(os.path.join(a.out,"virginia_nearest_generation.csv"),"w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(va[0].keys())); w.writeheader(); w.writerows(va)
    # a compact list of the top emitting assets loaded, for sanity
    top=sorted(assets,key=lambda x:-x["tco2e_latest"])[:15]
    with open(os.path.join(a.out,"climate_trace_top_assets.csv"),"w",newline="") as f:
        w=csv.writer(f); w.writerow(["name","id","year","tco2e","capacity","units","lat","lon","confidence"])
        for x in top: w.writerow([x["name"],x["id"],x["latest_full_year"],x["tco2e_latest"],x["capacity"],x["capacity_units"],x["lat"],x["lon"],x["confidence"]])
    print()
    for r in res: print(" ",r["sentence"])
    print(f"\nwrote {a.out}/climate_trace_matches.csv, virginia_nearest_generation.csv, climate_trace_top_assets.csv ({sum(r['matched'] for r in res)}/{len(res)} named plants matched, mode={mode})")

if __name__=="__main__": main()
