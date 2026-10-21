#!/usr/bin/env python3
"""Write the datacenter seed list in Climate TRACE's asset schema.

Produces two CSVs in the column order of Climate TRACE Emissions Inventory
v5.11.0 (per the 'About the data' guide, media.climatetrace.org, read 2026-10-20):
  datacenters_emissions_seed.csv   44 columns of the asset emissions file
  datacenters_ownership_seed.csv   19 columns of the asset ownership file

No emissions are estimated here. emissions_quantity is left empty; the point is
to hand over sites, coordinates, permit-derived capacity and documented supply
in the shape their pipeline already reads. 'other' slots carry the ledger's
extra fields with definitions, as their schema intends.

Input: registry/seed_sites.json (see its method note) and registry/*.json entries.
"""
import csv, json, os, sys, glob, argparse, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(ROOT, "registry")

EMIS = ['source_id','source_name','source_type','iso3_country','sector','subsector','start_time','end_time','lat','lon','geometry_ref','gas','emissions_quantity','temporal_granularity','activity','activity_units','emissions_factor','emissions_factor_units','capacity','capacity_units','capacity_factor','capacity_factor_units','other1','other1_def','other2','other2_def','other3','other3_def','other4','other4_def','other5','other5_def','other6','other6_def','other7','other7_def','other8','other8_def','other9','other9_def','other10','other10_def','created_date','modified_date']
OWN = ['parent_name','parent_entity_id','parent_entity_type','parent_lei','parent_permid','parent_registration_country','parent_headquarter_country','overall_share_percent','ownership_path','ownership_path_datasource_ids','immediate_source_owner','immediate_source_owner_entity_id','source_operator','source_operator_id','percentage_of_operation','source_id','source_name','source_sector','source_subsector']

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out",default=os.path.join(ROOT,"data","climate_trace_seed")); a=ap.parse_args()
    os.makedirs(a.out,exist_ok=True)
    sites=json.load(open(os.path.join(ROOT,"sites","seed_sites.json")))
    entries={}
    for f in glob.glob(os.path.join(REG,"*.json")):
        if os.path.basename(f) in ("sources.json","guide.json","standard.json","climate_trace_schema.json","seed_sites.json"): continue
        for e in json.load(open(f)): entries[e["id"]]=e
    today=datetime.date.today().isoformat()
    er,orr=[],[]
    for s in sites:
        if s.get("lat") is None or s.get("lon") is None: continue
        led=entries.get(s.get("ledger_entry_id") or "")
        sid=f"ledger-dc-{s['site_id']}"
        row={k:"" for k in EMIS}
        row.update({"source_id":sid,"source_name":s["name"],"source_type":"datacenter","iso3_country":s["country"],
                    "sector":"power","subsector":"electricity-consumption-datacenters (proposed)",
                    "start_time":"","end_time":"","lat":s["lat"],"lon":s["lon"],"gas":"co2e_100yr","emissions_quantity":"",
                    "temporal_granularity":"annual","activity":"","activity_units":"MWh",
                    "capacity":s.get("capacity_mw_it") or "","capacity_units":"MW IT load" if s.get("capacity_mw_it") else "",
                    "other1":s.get("generator_mw_permitted") or "","other1_def":"Backup generator capacity permitted (MW), from the air permit; a floor on site load",
                    "other2":s.get("cooling") or "unknown","other2_def":"Cooling type from permit or environmental assessment: air|evaporative|closed_loop|seawater|unknown",
                    "other3":s.get("status") or "","other3_def":"Site status: operating|under_construction|permitted|announced",
                    "other4":s.get("capacity_source") or "","other4_def":"Where capacity came from: permit|register|operator|osm",
                    "other5":s.get("source_url") or "","other5_def":"URL of the public record that establishes the site",
                    "other6":(led or {}).get("claim","")[:400] if led else "","other6_def":"Operator's public claim about the site's energy or water, from the ledger entry",
                    "other7":(led or {}).get("gap","")[:400] if led else "","other7_def":"Ledger gap line: where record and claim differ",
                    "other8":s.get("ledger_entry_id") or "","other8_def":"Compute Ledger entry id with full sources",
                    "other9":s.get("confidence") or "","other9_def":"Seed-list confidence in site identity and coordinates: high|medium|low",
                    "other10":s.get("licence") or "","other10_def":"Licence of the source record: public_record|ODbL|CC0|operator_site",
                    "created_date":today,"modified_date":today})
        er.append(row)
        o={k:"" for k in OWN}
        o.update({"parent_name":s.get("parent_company") or s.get("operator") or "","source_operator":s.get("operator") or "","percentage_of_operation":"100" if s.get("operator") else "",
                  "overall_share_percent":"","ownership_path":"","source_id":sid,"source_name":s["name"],"source_sector":"power","source_subsector":"electricity-consumption-datacenters (proposed)"})
        orr.append(o)
    for name,cols,rows in (("datacenters_emissions_seed.csv",EMIS,er),("datacenters_ownership_seed.csv",OWN,orr)):
        with open(os.path.join(a.out,name),"w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); w.writerows(rows)
    json.dump({"sites":len(er),"with_capacity":sum(1 for r in er if r["capacity"]!=""),"with_permit_mw":sum(1 for r in er if r["other1"]!=""),
               "with_ledger_entry":sum(1 for r in er if r["other8"]),"countries":len({r["iso3_country"] for r in er}),"schema":"Climate TRACE v5.11.0 asset files","generated":today},
              open(os.path.join(a.out,"README.json"),"w"),indent=1)
    print(f"{len(er)} sites -> {a.out}; {sum(1 for r in er if r['capacity']!='')} with capacity, {sum(1 for r in er if r['other1']!='')} with permitted generator MW, {len({r['iso3_country'] for r in er})} countries")

if __name__=="__main__": main()
