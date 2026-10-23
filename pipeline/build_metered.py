#!/usr/bin/env python3
"""Build the metered-load files of the handover from the transcribed regulator figures.

Inputs (checked by hand against the documents named in each row):
  sites/metered/ireland_aer_transcribed.csv   Irish EPA Annual Environmental Reports, Table 3 (Energy Used, GJ) and Table 5 (Water Used, m3)
  sites/metered/va_nei_transcribed.csv        EPA National Emissions Inventory facility summaries (Envirofacts DMAP), Virginia NAICS 518210 and matched datacenter facilities
  sites/metered/benchmarking_transcribed.csv  City and county building-energy benchmarking disclosures, rows typed Data Center (electricity as published; kBtu where the portal gives kBtu only)

Outputs:
  data/climate_trace_seed/ireland_aer_metered.csv
  data/climate_trace_seed/va_nei_generator_emissions.csv
  data/climate_trace_seed/benchmarking_datacenters.csv
  data/climate_trace_seed/metered_summary.json

Only unit conversions are applied (1 GJ = 1/3.6 MWh; average MW = MWh / hours in the year).
Nothing is estimated. A fuel figure is thermal energy, not electricity generated.
"""
import argparse
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "sites" / "metered"
OUT = ROOT / "data" / "climate_trace_seed"

CSO_2025_GWH = 7663.0   # ledger entry ie-national-cso-share-2025 (CSO release 7 Jul 2026, as reported)
CSO_2024_GWH = 6973.0

# licence -> (ledger site_id, permitted standby fleet MWth from sites/ireland_sites.json, part-year note)
LICENCE_SITE = {
    "P1170-01": ("irl-amazon-grange-castle-south-abc-p1170", 460.87),
    "P1184-01": ("irl-amazon-grange-castle-south-cyrusone-plot-p1184", 103.84),
    "P1173-01": ("irl-amazon-airton-road-tallaght-dub56-p1173", 343.16),
    "P1177-01": ("irl-amazon-greenhills-road-tallaght-p1177", 251.43),
    "P1172-01": ("irl-amazon-blanchardstown-snugborough-road-p1172", 416.52),
    "P1182-01": ("irl-amazon-cruiserath-road-dub58-p1182", 432.72),
    "P1186-01": ("irl-amazon-clonshaugh-buildings-uvwxy-p1186", 288.29),
    "P1171-01": ("irl-amazon-clonshaugh-campus-p1171", None),
    "P1181-01": ("irl-amazon-drogheda-ida-park-dub62-p1181", 358.17),
    "P1187-01": ("irl-microsoft-grange-castle-dub14-15-p1187", 342.8),
    "P1168-01": ("irl-equinix-db5-blanchardstown-p1168", 167.8),
}
PART_YEAR = {("P1181-01", "2024"): "AER covers 8 Aug to 31 Dec 2024 (part year); average MW uses 146 days"}


def num(s):
    """First number in a cell such as '1,586,892.15 +47.84%' or '60.20 -79.14%'; None for '-', 'N/A', 'blank', ''."""
    if s is None:
        return None
    s = s.strip()
    if s in ("", "-", "N/A", "blank", "not found", "0"):
        return 0.0 if s == "0" else None
    m = re.match(r"-?[\d,]*\.?\d+", s)
    return float(m.group(0).replace(",", "")) if m else None


def build_ireland():
    rows = list(csv.DictReader(open(SRC / "ireland_aer_transcribed.csv", encoding="utf-8")))
    out = []
    for r in rows:
        lic = r["licence_no"]
        yr = r["report_year"]
        site_id, fleet_mwth = LICENCE_SITE[lic]
        el_gj = num(r["electricity_gj"])
        lfo = num(r["light_fuel_oil_gj"]) or 0.0
        hvo = num(r["renewable_biomass_hvo_gj"]) or 0.0
        gas = num(r["natural_gas_gj"]) or 0.0
        water = num(r["water_m3"])
        hours = 8760 if yr != "2024" else 8784
        note = PART_YEAR.get((lic, yr), "")
        if note:
            hours = 146 * 24
        el_mwh = round(el_gj / 3.6, 1) if el_gj is not None else None
        gen_fuel_gj = lfo + hvo + gas
        out.append({
            "licence_no": lic,
            "site_id": site_id,
            "operator": r["operator"],
            "report_year": yr,
            "electricity_gj": el_gj,
            "electricity_mwh": el_mwh,
            "average_load_mw": round(el_mwh / hours, 2) if el_mwh is not None else None,
            "water_m3": water,
            "generator_fuel_light_fuel_oil_gj": lfo,
            "generator_fuel_hvo_gj": hvo,
            "natural_gas_gj": gas,
            "generator_fuel_total_gj": round(gen_fuel_gj, 2),
            "generator_fuel_total_mwh_thermal": round(gen_fuel_gj / 3.6, 1),
            "permitted_fleet_mwth": fleet_mwth,
            "fuel_as_hours_at_full_fleet_thermal_rating": round(gen_fuel_gj / 3.6 / fleet_mwth, 2) if fleet_mwth else None,
            "document_url": r["document_url"],
            "document": r["document_title_and_date"],
            "table_and_page": r["page_or_section"],
            "note": (note + ("; " if note and r["notes"] else "") + r["notes"]).strip(),
        })
    cols = list(out[0].keys())
    with open(OUT / "ireland_aer_metered.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(out)
    summ = {}
    for yr in ("2024", "2025"):
        sel = [o for o in out if o["report_year"] == yr and o["electricity_mwh"] is not None]
        tot = sum(o["electricity_mwh"] for o in sel)
        amz = sum(o["electricity_mwh"] for o in sel if o["operator"].startswith("Amazon"))
        nat = CSO_2025_GWH if yr == "2025" else CSO_2024_GWH
        summ[yr] = {
            "licences": len(sel),
            "electricity_gwh": round(tot / 1000, 1),
            "share_of_cso_national_metered_total": round(tot / 1000 / nat, 3),
            "amazon_licences": sum(1 for o in sel if o["operator"].startswith("Amazon")),
            "amazon_electricity_gwh": round(amz / 1000, 1),
            "amazon_share_of_cso_national_metered_total": round(amz / 1000 / nat, 3),
            "water_m3": round(sum(o["water_m3"] or 0 for o in sel)),
            "generator_fuel_gj": round(sum(o["generator_fuel_total_gj"] for o in sel)),
            "natural_gas_gj": round(sum(o["natural_gas_gj"] for o in sel)),
        }
    return out, summ


def build_virginia():
    rows = list(csv.DictReader(open(SRC / "va_nei_transcribed.csv", encoding="utf-8")))
    cols = list(rows[0].keys())
    with open(OUT / "va_nei_generator_emissions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    nox23 = [r for r in rows if r["year"] == "2023" and r["pollutant"] == "NOX"]
    nox20 = [r for r in rows if r["year"] == "2020" and r["pollutant"] == "NOX"]
    return {
        "facilities_2023_nox": len(nox23),
        "nox_tons_2023_total": round(sum(float(r["tons_per_year"]) for r in nox23), 1),
        "facilities_2020_nox": len(nox20),
        "nox_tons_2020_total": round(sum(float(r["tons_per_year"]) for r in nox20), 1),
        "matched_to_deq_registration": sum(1 for r in nox23 if r["registration"] not in ("", "not matched")),
        "largest_2023": sorted(((r["facility_name_in_inventory"], float(r["tons_per_year"])) for r in nox23), key=lambda x: -x[1])[:5],
    }


def build_benchmarking():
    """City and state benchmarking disclosures: rows typed Data Center (or known datacenters typed Office), as published."""
    rows = list(csv.DictReader(open(SRC / "benchmarking_transcribed.csv", encoding="utf-8")))
    cols = list(rows[0].keys())
    with open(OUT / "benchmarking_datacenters.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    def kwh(r):
        try:
            return float(str(r["electricity_kwh"]).replace(",", ""))
        except ValueError:
            return None
    by_j = {}
    for r in rows:
        by_j.setdefault(r["jurisdiction"], set()).add(r["report_year"])
    top = sorted(((r["jurisdiction"], r["report_year"], r["address"], r["primary_property_type"], kwh(r)) for r in rows if kwh(r)), key=lambda x: -x[4])[:8]
    return {"rows": len(rows), "jurisdictions": {k: sorted(v) for k, v in by_j.items()}, "largest_kwh": top}


def main():
    global OUT
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="write outputs here instead of data/climate_trace_seed (CI compares)")
    a = ap.parse_args()
    if a.out:
        OUT = Path(a.out)
        OUT.mkdir(parents=True, exist_ok=True)
    ie, ie_summ = build_ireland()
    va_summ = build_virginia()
    bm_summ = build_benchmarking()
    json.dump({"ireland_aer": ie_summ, "virginia_nei": va_summ, "benchmarking": bm_summ,
               "method": "Unit conversions only: 1 GJ = 1/3.6 MWh; average MW = MWh / hours in the reporting period. Fuel figures are thermal energy burned, not electricity generated. 'fuel_as_hours_at_full_fleet_thermal_rating' = fuel GJ / 3.6 / permitted fleet MWth; it is the number of hours the whole permitted fleet would take to burn that fuel at full rating, a scale for how little the generators ran, not a count of actual hours."},
              open(OUT / "metered_summary.json", "w"), indent=1)
    print(json.dumps({"ireland_aer": ie_summ, "virginia_nei": va_summ, "benchmarking": bm_summ}, indent=1))


if __name__ == "__main__":
    main()
