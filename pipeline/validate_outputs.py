#!/usr/bin/env python3
"""Validate every CSV/JSON the pipeline wrote in --out. Exit 1 on any failure.

Checks: files exist and parse; required columns; enum values; lat/lon numeric and inside the
state's bounding box; no coordinate without a recorded method; Climate TRACE CSVs have exactly the
schema's columns and only rows with coordinates; seed_sites_v2 keeps the 23 v1 keys; summaries agree
with the files they describe.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from merge_to_handover import SEED_KEYS, load_ct_columns  # noqa: E402

CONF = {"high", "medium", "low", "none"}
BBOX = {"Virginia": (36.5, 39.5, -83.7, -75.2), "Texas": (25.6, 36.7, -106.8, -93.3)}
fails: list[str] = []


def fail(msg: str) -> None:
    fails.append(msg)


def check_csv(path: Path, required: list[str]) -> pd.DataFrame | None:
    if not path.exists():
        fail(f"missing {path}")
        return None
    try:
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
    except Exception as exc:  # noqa: BLE001
        fail(f"{path}: cannot parse: {exc}")
        return None
    missing = [c for c in required if c not in df.columns]
    if missing:
        fail(f"{path}: missing columns {missing}")
    if "nan" in set(df.values.flatten().tolist()):
        fail(f"{path}: literal 'nan' strings present")
    print(f"ok  {path.name}: {len(df)} rows, {len(df.columns)} columns")
    return df


def check_json(path: Path):
    if not path.exists():
        fail(f"missing {path}")
        return None
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(f"{path}: invalid JSON: {exc}")
        return None
    print(f"ok  {path.name}")
    return obj


def enum_ok(df, col, allowed, path):
    bad = sorted(set(df[col]) - allowed - {""})
    if bad:
        fail(f"{path}: column {col} has unexpected values {bad}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("out", type=Path)
    args = ap.parse_args()
    o = args.out

    va = check_csv(o / "va_permits.csv", ["backlog_id", "registration_no", "facility_name_list", "pdf_url", "pdf_locator", "text_quality",
                                          "facility_street", "address_confidence", "generator_count", "total_standby_mw", "total_mw_confidence",
                                          "fuel", "hours_all_purpose_per_year", "extract_reason", "source_url"])
    if va is not None:
        for c in ("total_mw_confidence", "address_confidence", "fuel_confidence", "hours_confidence", "generator_count_confidence"):
            enum_ok(va, c, CONF, "va_permits.csv")
        if va["registration_no"].duplicated().any():
            fail("va_permits.csv: duplicate registration numbers")
        for _, r in va.iterrows():
            if r["total_standby_mw"] and not r["generator_count"]:
                fail(f"va_permits.csv {r['registration_no']}: MW without generator count")
            if r["total_standby_mw"] and not (0 < float(r["total_standby_mw"]) < 2000):
                fail(f"va_permits.csv {r['registration_no']}: implausible MW {r['total_standby_mw']}")
            if r["text_quality"] == "ok" and r["total_mw_confidence"] == "none" and not r["extract_reason"]:
                fail(f"va_permits.csv {r['registration_no']}: no MW and no reason")
    check_csv(o / "va_generator_rows.csv", ["registration_no", "refs", "count", "kw_each", "description"])
    vs = check_json(o / "va_permits_summary.json")
    if va is not None and vs and vs.get("registrations") != len(va):
        fail("va_permits_summary.json: registrations != rows in va_permits.csv")

    tx = check_csv(o / "tx_permits.csv", ["backlog_id", "comptroller_name", "match_method", "application_url", "lat", "lon", "coord_source",
                                          "coord_confidence", "generator_count", "total_standby_mw", "reason", "source_url"])
    if tx is not None:
        enum_ok(tx, "coord_confidence", CONF, "tx_permits.csv")
        enum_ok(tx, "total_mw_confidence", CONF, "tx_permits.csv")
        for _, r in tx.iterrows():
            if r["lat"]:
                lat, lon = float(r["lat"]), float(r["lon"])
                b = BBOX["Texas"]
                if not (b[0] <= lat <= b[1] and b[2] <= lon <= b[3]):
                    fail(f"tx_permits.csv {r['backlog_id']}: coordinates outside Texas")
                if not r["coord_source"]:
                    fail(f"tx_permits.csv {r['backlog_id']}: coordinate without coord_source")
            if not r["application_url"] and not r["reason"]:
                fail(f"tx_permits.csv {r['backlog_id']}: unmatched row without a reason")
    check_csv(o / "tx_index_rows.csv", ["index", "applicant", "area_name", "application_url"])
    check_csv(o / "tx_unmatched_tceq_packages.csv", ["application_url", "applicant", "text_quality"])
    ts = check_json(o / "tx_permits_summary.json")
    if tx is not None and ts and ts.get("rows") != len(tx):
        fail("tx_permits_summary.json: rows != tx_permits.csv")

    ge = check_csv(o / "geocoded.csv", ["row_key", "state", "query_street", "lat", "lon", "geocoder", "match_quality", "confidence", "reason"])
    if ge is not None:
        enum_ok(ge, "confidence", CONF, "geocoded.csv")
        for _, r in ge.iterrows():
            if r["lat"] and not r["geocoder"]:
                fail(f"geocoded.csv {r['row_key']}: coordinate without geocoder")
            if not r["lat"] and not r["reason"]:
                fail(f"geocoded.csv {r['row_key']}: no coordinate and no reason")
    check_json(o / "geocode_summary.json")

    sites = check_json(o / "seed_sites_v2.json")
    if sites is not None:
        ids = [s.get("site_id") for s in sites]
        if len(ids) != len(set(ids)):
            fail("seed_sites_v2.json: duplicate site_id")
        for s in sites:
            missing = [k for k in SEED_KEYS if k not in s]
            if missing:
                fail(f"seed_sites_v2.json {s.get('site_id')}: missing keys {missing}")
            if (s.get("lat") is None) != (s.get("lon") is None):
                fail(f"seed_sites_v2.json {s.get('site_id')}: lat/lon half null")
            if s.get("lat") is not None:
                if not (-90 <= s["lat"] <= 90 and -180 <= s["lon"] <= 180):
                    fail(f"seed_sites_v2.json {s.get('site_id')}: bad coordinates")
                b = BBOX.get(s.get("admin_region"))
                if b and s.get("backlog_id") and not (b[0] <= s["lat"] <= b[1] and b[2] <= s["lon"] <= b[3]):
                    fail(f"seed_sites_v2.json {s.get('site_id')}: outside {s.get('admin_region')}")
                if s.get("backlog_id") and not s.get("coord_method"):
                    fail(f"seed_sites_v2.json {s.get('site_id')}: new row has coordinates but no coord_method")
            if s.get("confidence") not in ("high", "medium", "low"):
                fail(f"seed_sites_v2.json {s.get('site_id')}: confidence {s.get('confidence')}")
            if not s.get("source_url"):
                fail(f"seed_sites_v2.json {s.get('site_id')}: no source_url")
    check_csv(o / "seed_sites_v2.csv", SEED_KEYS)

    emis_cols, own_cols = load_ct_columns()
    e = check_csv(o / "climate_trace" / "datacenters_emissions_seed.csv", emis_cols)
    w = check_csv(o / "climate_trace" / "datacenters_ownership_seed.csv", own_cols)
    if e is not None:
        if list(e.columns) != emis_cols:
            fail("emissions CSV: column order differs from schema")
        if (e["lat"] == "").any() or (e["lon"] == "").any():
            fail("emissions CSV: row without coordinates")
        if sites is not None and len(e) != sum(1 for s in sites if s.get("lat") is not None):
            fail("emissions CSV: row count != located sites")
    if w is not None and list(w.columns) != own_cols:
        fail("ownership CSV: column order differs from schema")
    if e is not None and w is not None and set(e["source_id"]) != set(w["source_id"]):
        fail("ownership CSV: source_ids differ from emissions CSV")
    hs = check_json(o / "handover_summary.json")
    if hs and e is not None and hs.get("with_coordinates") != len(e):
        fail("handover_summary.json: with_coordinates != emissions rows")

    if fails:
        print("\nFAILED checks:")
        for f in fails:
            print("  - " + f)
        sys.exit(1)
    print("\nall outputs valid")


if __name__ == "__main__":
    main()
