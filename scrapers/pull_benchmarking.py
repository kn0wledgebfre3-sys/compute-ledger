#!/usr/bin/env python3
"""Pull datacenter rows from city building-energy benchmarking portals (Socrata and ArcGIS).

What it does
  For each portal in config/benchmarking_portals.json, selects rows typed Data Center (and the known
  datacenter addresses filed under another type) and writes them in the column layout of
  sites/metered/benchmarking_transcribed.csv:
    benchmarking_pull.csv      every row returned, electricity as published (unit in notes)
    benchmarking_changes.csv   building-years not yet in the ledger, or whose electricity differs
    benchmarking_summary.json  counts per portal and failures
  Nothing enters the ledger from here; a person checks the new rows (telephone exchanges and
  mixed buildings are common among 'Data Center' rows) and appends them to the transcription.

Sources: field names inspected 2026-10-23 (sites/metered/benchmarking_notes.md).
  Socrata: https://<domain>/resource/<dataset>.json?$select=...&$where=...&$limit=5000
  ArcGIS:  <layer>/query?where=...&outFields=*&returnGeometry=false&f=json
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from urllib.parse import quote

from _common import FIXTURES, SourceError, base_parser, fetch, log, run_main, run_meta, write_json

HERE = Path(__file__).resolve().parent
CFG = json.load(open(HERE / "config" / "benchmarking_portals.json", encoding="utf-8"))
LEDGER = HERE.parent / "sites" / "metered" / "benchmarking_transcribed.csv"
COLS = ["jurisdiction", "dataset_name", "dataset_id_or_url", "report_year", "property_name", "address", "primary_property_type",
        "gross_floor_area_sqft", "electricity_kwh", "natural_gas_or_district_energy", "site_eui_kbtu_sqft", "energy_star_score",
        "query_url", "notes"]


def norm(a: str) -> str:
    a = (a or "").split(",")[0]  # the ledger sometimes carries city and zip after the street
    a = re.sub(r"[^a-z0-9 ]", " ", a.lower())
    a = re.sub(r"\b(street|st)\b", "st", a)
    a = re.sub(r"\b(avenue|av|ave)\b", "ave", a)
    return " ".join(a.split())


def to_row(p: dict, rec: dict, url: str, year: str) -> dict:
    g = lambda k: "" if not k or rec.get(k) in (None, "") else str(rec.get(k))
    elec = g(p["elec"])
    if elec and p["elec_unit"] != "kWh":
        elec = f"{p['elec']}={elec} ({p['elec_unit']}, NOT kWh)"
    return {"jurisdiction": p["jurisdiction"], "dataset_name": p.get("dataset") or p.get("layer"),
            "dataset_id_or_url": p.get("dataset") or p.get("layer"), "report_year": year or g(p.get("year")),
            "property_name": g(p["name"]), "address": g(p["address"]), "primary_property_type": g(p["type"]),
            "gross_floor_area_sqft": g(p.get("gfa")), "electricity_kwh": elec or "not found", "natural_gas_or_district_energy": "",
            "site_eui_kbtu_sqft": g(p.get("eui")), "energy_star_score": g(p.get("star")), "query_url": url,
            "notes": f"automated pull; unit {p['elec_unit']}" + (f"; {p['note']}" if p.get("note") else "")}


def socrata(p: dict, fixture: bool) -> list[dict]:
    where = p["type_filter"]
    if p["known_addresses"]:
        where = f"({where}) OR {p['address']} in(" + ",".join("'" + a.replace("'", "''") + "'" for a in p["known_addresses"]) + ")"
    url = f"https://{p['domain']}/resource/{p['dataset']}.json?$where={quote(where)}&$limit=5000"
    if fixture:
        f = FIXTURES / "benchmarking" / f"{p['dataset']}.json"
        data = json.load(open(f, encoding="utf-8")) if f.exists() else []
    else:
        data = fetch(url, expect="json").json()
    return [to_row(p, r, url, "") for r in data]


def arcgis(p: dict, fixture: bool) -> list[dict]:
    out = []
    years = p.get("years") or [None]
    for y in years:
        layer = p["layer"].format(year=y) if y else p["layer"]
        url = f"{layer}/query?where={quote(p['where'])}&outFields=*&returnGeometry=false&f=json"
        if fixture:
            f = FIXTURES / "benchmarking" / (re.sub(r"[^A-Za-z0-9]+", "_", p["jurisdiction"]) + (f"_{y}" if y else "") + ".json")
            data = json.load(open(f, encoding="utf-8")) if f.exists() else {"features": []}
        else:
            data = fetch(url, expect="json").json()
        if "error" in data:
            raise SourceError(f"{p['jurisdiction']}: ArcGIS error {data['error']}")
        for feat in data.get("features", []):
            out.append(to_row(p, feat.get("attributes", {}), url, p.get("fixed_year", "")))
    return out


def main() -> None:
    ap = base_parser(__doc__)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    rows, failures, counts = [], [], {}
    for kind, fn in (("socrata", socrata), ("arcgis", arcgis)):
        for p in CFG[kind]:
            try:
                got = fn(p, a.fixture)
            except SourceError as exc:
                failures.append(f"{p['jurisdiction']}: {exc}")
                log(f"{p['jurisdiction']}: {exc}")
                continue
            counts[p["jurisdiction"]] = len(got)
            rows += got
    rows.sort(key=lambda r: (r["jurisdiction"], r["report_year"], norm(r["address"])))
    with open(a.out / "benchmarking_pull.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    num = lambda s: (re.search(r"\d[\d,]*\.?\d*", s or "") or [None])[0]
    known = {}
    for r in csv.DictReader(open(LEDGER, encoding="utf-8")):
        known[(r["jurisdiction"].split(",")[0], r["report_year"][:4], norm(r["address"]))] = num(r["electricity_kwh"])
    changes = []
    for r in rows:
        k = (r["jurisdiction"].split(",")[0], r["report_year"][:4], norm(r["address"]))
        v = num(r["electricity_kwh"])
        if k not in known:
            changes.append({**r, "change": "new to the ledger"})
        elif v and known[k] and abs(float(v.replace(",", "")) - float(known[k].replace(",", ""))) > 0.5:
            changes.append({**r, "change": f"ledger has {known[k]}"})
    with open(a.out / "benchmarking_changes.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS + ["change"], lineterminator="\n")
        w.writeheader()
        w.writerows(changes)
    write_json({**run_meta(a.fixture, [{"name": "city benchmarking portals", "config": "config/benchmarking_portals.json"}]),
                "rows": len(rows), "per_portal": counts, "changes_vs_ledger": len(changes), "failures": failures},
               a.out / "benchmarking_summary.json")
    log(f"benchmarking: {len(rows)} rows, {len(changes)} new or changed vs the ledger")


if __name__ == "__main__":
    run_main(main)
