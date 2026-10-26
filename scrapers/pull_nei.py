#!/usr/bin/env python3
"""Pull datacenter facility emissions from EPA's National Emissions Inventory (Envirofacts DMAP).

What it does
  For each state in --states and each NEI year that exists, queries the facility-summary view for
  NAICS 518210 (data processing, hosting) criteria pollutants, and writes:
    nei_facilities.csv     one row per facility, year and pollutant, with the query URL
    nei_changes.csv        rows that are new or differ from sites/metered/va_nei_transcribed.csv
    nei_summary.json       counts, years found, failures
  Nothing is written to the ledger's tables. A person reads nei_changes.csv, checks the
  facilities against permits, and adds them to sites/metered/va_nei_transcribed.csv.

Source (inspected 2026-10-23)
  https://data.epa.gov/dmapservice/nei.vw_facility_summaries_<year>/state_abbr/equals/<ST>/naics_code/equals/518210/pollutant_type/equals/CAP/1:5000/CSV
  Columns: address, address_postal_code, city_name, code_description, county_fips, county_name, description,
  eis_facility_id, emissions, facility_type, fips, latitude, longitude, naics_code, pollutant_code,
  pollutant_type, site_name, state_abbr, state_fips, uom.  uom is TON (US short tons) for criteria pollutants.
  NEI is triennial; the view for a year exists only once EPA has released it, so later years are probed.
  Datacenters filed under another NAICS code (several in Virginia) are not found by this query.
"""
from __future__ import annotations

import csv
import io
from pathlib import Path

from _common import FIXTURES, SchemaChangedError, SourceError, base_parser, fetch, log, run_main, run_meta, write_json

BASE = "https://data.epa.gov/dmapservice/nei.vw_facility_summaries_{year}/state_abbr/equals/{st}/naics_code/equals/518210/pollutant_type/equals/CAP/1:5000/CSV"
YEARS = [2020, 2023, 2026, 2029]
LATEST_RELEASED = 2023  # later years are probed each week; until EPA publishes one, its view does not exist
STATES = ["VA", "TX", "GA", "AZ", "OH", "OR", "IA", "NE", "NC", "SC", "IL", "WA", "NV", "TN", "MS", "PA"]
NEED = ["eis_facility_id", "site_name", "address", "city_name", "county_name", "pollutant_code", "emissions", "uom", "latitude", "longitude"]
LEDGER = Path(__file__).resolve().parents[1] / "sites" / "metered" / "va_nei_transcribed.csv"
COLS = ["state", "year", "eis_facility_id", "site_name", "address", "city_name", "county_name", "latitude", "longitude",
        "pollutant_code", "emissions", "uom", "query_url"]


def parse(text: str, st: str, year: int, url: str) -> list[dict]:
    rows = list(csv.DictReader(io.StringIO(text)))
    if not rows:
        return []
    missing = [c for c in NEED if c not in rows[0]]
    if missing:
        raise SchemaChangedError(f"NEI view {year} {st}: columns missing {missing}; found {list(rows[0])}")
    return [{"state": st, "year": str(year), **{c: r[c] for c in NEED if c in r}, "query_url": url} for r in rows]


def main() -> None:
    ap = base_parser(__doc__)
    ap.add_argument("--states", default=",".join(STATES))
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    out, failures, notes, years_found = [], [], [], set()
    if a.fixture:
        for p in sorted((FIXTURES / "nei").glob("*.csv")):
            st, year = p.stem.split("_")[0], int(p.stem.split("_")[1])
            out += parse(p.read_text(encoding="utf-8"), st, year, BASE.format(year=year, st=st))
            years_found.add(year)
    else:
        for year in YEARS:
            for st in a.states.split(","):
                url = BASE.format(year=year, st=st)
                try:
                    got = fetch(url, expect="csv", allow_empty=True)
                except SourceError as exc:
                    if st == a.states.split(",")[0] and year > LATEST_RELEASED:
                        notes.append(f"{year}: not released by EPA yet (the {year} view does not exist); checked again next week")
                        log(f"{year}: not released yet")
                        break
                    failures.append(f"{year} {st}: {exc}")
                    log(f"{year} {st}: {exc}")
                    continue
                if not got.content.strip():
                    notes.append(f"{year} {st}: the query returned an empty file (no rows); check by hand if a datacenter facility is expected there")
                    log(f"{year} {st}: no rows")
                    continue
                rows = parse(got.text(), st, year, url)
                years_found.add(year)
                out += rows
    out.sort(key=lambda r: (r["state"], r["year"], r["eis_facility_id"], r["pollutant_code"]))
    with open(a.out / "nei_facilities.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    known = {}
    for r in csv.DictReader(open(LEDGER, encoding="utf-8")):
        known[(r["eis_facility_id_or_deq_id"], r["year"], r["pollutant"])] = r["tons_per_year"]
    changes = []
    for r in out:
        k = (r["eis_facility_id"], r["year"], r["pollutant_code"])
        if k not in known:
            changes.append({**r, "change": "new to the ledger"})
        elif abs(float(known[k]) - float(r["emissions"])) > 1e-6:
            changes.append({**r, "change": f"ledger has {known[k]}"})
    with open(a.out / "nei_changes.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS + ["change"], lineterminator="\n")
        w.writeheader()
        w.writerows(changes)
    write_json({**run_meta(a.fixture, [{"name": "EPA NEI facility summaries (Envirofacts DMAP)", "url": BASE}]),
                "rows": len(out), "facilities": len({r["eis_facility_id"] for r in out}), "years_found": sorted(years_found),
                "changes_vs_ledger": len(changes), "failures": failures, "notes": notes}, a.out / "nei_summary.json")
    log(f"NEI: {len(out)} rows, {len(changes)} new or changed vs the ledger")


if __name__ == "__main__":
    run_main(main)
