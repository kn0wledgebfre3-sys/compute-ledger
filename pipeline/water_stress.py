#!/usr/bin/env python3
"""Baseline water stress (WRI Aqueduct 4.0) for every located site in the register.

Run this on a computer with internet access, once WRI's data file is downloaded:

    1. Download https://files.wri.org/aqueduct/aqueduct-4-0-water-risk-data.zip
       (from https://www.wri.org/data/aqueduct-global-maps-40-data; CC BY 4.0).
    2. pip install geopandas
    3. python3 pipeline/water_stress.py --data ~/Downloads/aqueduct-4-0-water-risk-data.zip
    4. python3 site/build_sites.py      (the site pages then show each site's water stress)
    5. commit data/climate_trace_seed/water_stress.csv and docs/sites/

It finds the "baseline annual" polygon layer inside the zip (a file geodatabase, GeoPackage or shapefile), places every
site with coordinates in data/climate_trace_seed/site_register.csv inside its polygon, and writes
data/climate_trace_seed/water_stress.csv with WRI's own fields: pfaf_id (the HydroBASINS level 6 sub-basin), bws_raw,
bws_score (0 to 5), bws_cat and bws_label. A raw value of 9999 is WRI's "Arid and Low Water Use"; -9999 is no data.
A site that falls in no polygon (on a coastline, say) is written with a note and no value; nothing is guessed.

Citation (WRI): Kuzma, S. et al. 2023. "Aqueduct 4.0: Updated decision-relevant global water risk indicators."
Technical Note. Washington, DC: World Resources Institute. https://doi.org/10.46830/writn.23.00061
"""
import argparse
import csv
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "data" / "climate_trace_seed"
FIELDS = ["pfaf_id", "bws_raw", "bws_score", "bws_cat", "bws_label"]
COLS = ["site_id", "lat", "lon"] + FIELDS + ["aqueduct_version", "source_layer", "notes"]


def find_layer(root: Path):
    """Return (path, layer) for the baseline annual polygons."""
    import pyogrio
    candidates = []
    for p in sorted(root.rglob("*")):
        if p.suffix.lower() == ".gdb" and p.is_dir() or p.suffix.lower() in (".gpkg", ".shp"):
            try:
                layers = [l[0] for l in pyogrio.list_layers(p)]
            except Exception:
                continue
            for l in layers:
                name = f"{p.name}/{l}".lower()
                if "baseline" in name and "annual" in name and "month" not in name:
                    candidates.append((p, l))
    if not candidates:
        seen = []
        for p in sorted(root.rglob("*")):
            if p.suffix.lower() in (".gdb", ".gpkg", ".shp"):
                try:
                    seen += [f"{p}::{l[0]}" for l in pyogrio.list_layers(p)]
                except Exception as e:
                    seen.append(f"{p}: {e}")
        sys.exit("no baseline annual layer found. Layers seen:\n  " + "\n  ".join(seen[:60]) + "\nRe-run with --layer PATH::LAYER")
    if len(candidates) > 1:
        print("several candidate layers; using the first:", *[f"{p.name}::{l}" for p, l in candidates], sep="\n  ")
    return candidates[0]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", type=Path, required=True, help="WRI's zip, or the folder it unzips to")
    ap.add_argument("--layer", help="PATH::LAYER, if the automatic search picks the wrong layer")
    ap.add_argument("--points", type=Path, default=PKG / "site_register.csv", help="CSV with site_id, lat, lon (default: the site register)")
    ap.add_argument("--out", type=Path, default=PKG / "water_stress.csv")
    a = ap.parse_args()
    import geopandas as gpd

    with tempfile.TemporaryDirectory() as tmp:
        root = a.data
        if a.data.suffix.lower() == ".zip":
            zipfile.ZipFile(a.data).extractall(tmp)
            root = Path(tmp)
        if a.layer:
            p, l = a.layer.split("::")
            path, layer = Path(p), l
        else:
            path, layer = find_layer(root)
        print(f"reading {path.name} :: {layer}")
        poly = gpd.read_file(path, layer=layer)
        cols = {c.lower(): c for c in poly.columns}
        missing = [f for f in FIELDS if f not in cols]
        if missing:
            sys.exit(f"layer lacks {missing}; columns are {list(poly.columns)[:40]}")
        poly = poly[[cols[f] for f in FIELDS] + ["geometry"]].rename(columns={cols[f]: f for f in FIELDS})
        if poly.crs is None or poly.crs.to_epsg() != 4326:
            poly = poly.to_crs(4326)
        source_layer = f"{a.data.name} :: {path.name} :: {layer}"

    with open(a.points, newline="", encoding="utf-8") as f:
        sites = [r for r in csv.DictReader(f) if r["lat"] and r["lon"]]
    pts = gpd.GeoDataFrame(sites, geometry=gpd.points_from_xy([float(r["lon"]) for r in sites], [float(r["lat"]) for r in sites]), crs=4326)
    j = gpd.sjoin(pts, poly, how="left", predicate="within")
    rows = {}
    for _, r in j.iterrows():
        sid = r["site_id"]
        if sid in rows:  # a point on a shared boundary: keep it only if both polygons agree
            if str(rows[sid]["pfaf_id"]) != str(r["pfaf_id"]):
                rows[sid].update({f: "" for f in FIELDS}, notes="on the boundary of two sub-basins; not assigned")
            continue
        found = r["pfaf_id"] == r["pfaf_id"] and r["pfaf_id"] is not None  # not NaN
        rec = {"site_id": sid, "lat": r["lat"], "lon": r["lon"], "aqueduct_version": "4.0", "source_layer": source_layer, "notes": ""}
        for fld in FIELDS:
            v = r[fld] if found else ""
            if fld == "pfaf_id" and found:
                v = str(int(float(v)))
            rec[fld] = "" if v is None else str(v)
        if not found:
            rec["notes"] = "point falls in no polygon of the layer"
        elif rec["bws_raw"] in ("-9999", "-9999.0"):
            rec["notes"] = "no data in Aqueduct for this sub-basin"
        rows[sid] = rec
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        for sid in sorted(rows):
            w.writerow(rows[sid])
    n = sum(1 for r in rows.values() if r["bws_label"])
    print(f"wrote {a.out}: {len(rows)} located sites, {n} with a water stress value")
    from collections import Counter
    for label, c in Counter(r["bws_label"] or "(none)" for r in rows.values()).most_common():
        print(f"  {c:4d}  {label}")


if __name__ == "__main__":
    main()
