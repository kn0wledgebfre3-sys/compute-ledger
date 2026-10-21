#!/usr/bin/env python3
"""Combine va_permits.csv + tx_permits.csv (+ geocoded.csv) with registry/seed_sites.json into
seed_sites_v2.json (seed_sites schema, 23 keys, plus a few additive keys), then write the two
Climate TRACE asset CSVs with the row logic of scrapers/to_climate_trace.py, and a summary.

Rules
-----
* Existing seed_sites.json rows are kept as they are. A permit row whose TCEQ application URL equals
  an existing row's source_url UPDATES that row (fills generator_mw_permitted / notes) instead of
  adding a duplicate.
* A new row gets lat/lon only from (a) the permit's own coordinates (Texas Core Data Form / STEERS) or
  (b) geocoded.csv with confidence high or medium. Street-level geocodes (confidence low) and weak /
  unverified TCEQ name matches are written with lat/lon null and the reason in notes, unless
  --include-weak is given. Nothing is ever estimated.
* status = "permitted" for every permit-derived row (an air permit proves the permit, not operation).
  TX Comptroller rows without a permit get status "registered" (an addition to the seed enum, as
  seed_sites_method.md already extends enums where honesty requires it).
* generator_mw_permitted = total_standby_mw from the permit (sum of per-unit ekW ratings); the
  confidence and min/max range go to notes. capacity_mw_it stays null (no IT-load figure in permits).
* Climate TRACE CSVs (datacenters_emissions_seed.csv / datacenters_ownership_seed.csv) follow
  scrapers/to_climate_trace.py exactly: same columns, same 'otherN' slots, only rows with coordinates.
  The column lists are imported from that script when it is present, else read from
  registry/climate_trace_schema.json, else the embedded copy below.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C  # noqa: E402

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
ROOT = Path(__file__).resolve().parent.parent
SEED_SITES = ROOT / "registry" / "seed_sites.json"
SCHEMA_JSON = ROOT / "registry" / "climate_trace_schema.json"
TO_CT = ROOT / "scrapers"

EMIS_EMBEDDED = ['source_id', 'source_name', 'source_type', 'iso3_country', 'sector', 'subsector', 'start_time', 'end_time', 'lat', 'lon', 'geometry_ref', 'gas', 'emissions_quantity', 'temporal_granularity', 'activity', 'activity_units', 'emissions_factor', 'emissions_factor_units', 'capacity', 'capacity_units', 'capacity_factor', 'capacity_factor_units', 'other1', 'other1_def', 'other2', 'other2_def', 'other3', 'other3_def', 'other4', 'other4_def', 'other5', 'other5_def', 'other6', 'other6_def', 'other7', 'other7_def', 'other8', 'other8_def', 'other9', 'other9_def', 'other10', 'other10_def', 'created_date', 'modified_date']
OWN_EMBEDDED = ['parent_name', 'parent_entity_id', 'parent_entity_type', 'parent_lei', 'parent_permid', 'parent_registration_country', 'parent_headquarter_country', 'overall_share_percent', 'ownership_path', 'ownership_path_datasource_ids', 'immediate_source_owner', 'immediate_source_owner_entity_id', 'source_operator', 'source_operator_id', 'percentage_of_operation', 'source_id', 'source_name', 'source_sector', 'source_subsector']

SEED_KEYS = ["site_id", "name", "operator", "parent_company", "country", "admin_region", "city", "lat", "lon", "status",
             "capacity_mw_it", "capacity_source", "generator_mw_permitted", "cooling", "first_year", "source_url",
             "source_type", "licence", "ledger_entry_id", "confidence", "last_checked", "coord_source_url", "notes"]
EXTRA_KEYS = ["backlog_id", "registration_id", "address", "generator_count", "coord_method", "coord_confidence", "located", "needs_review"]

OPERATORS = [  # (regex on facility / permittee names, operator, parent)
    (r"amazon|aws\b|vadata", "Amazon Web Services", "Amazon.com, Inc."),
    (r"microsoft", "Microsoft", "Microsoft Corporation"),
    (r"google", "Google", "Alphabet Inc."),
    (r"\bmeta\b|facebook", "Meta", "Meta Platforms, Inc."),
    (r"oracle", "Oracle", "Oracle Corporation"),
    (r"qts", "QTS", "QTS (Blackstone)"),
    (r"equinix", "Equinix", "Equinix, Inc."),
    (r"digital realty|dupont fabros|\bdlr\b", "Digital Realty", "Digital Realty Trust"),
    (r"cyrusone", "CyrusOne", "CyrusOne (KKR/GIP)"),
    (r"vantage", "Vantage Data Centers", "Vantage Data Centers"),
    (r"iron mountain", "Iron Mountain", "Iron Mountain Inc."),
    (r"cloud ?hq|abteen|bourzou|manuchehr", "CloudHQ", "CloudHQ"),
    (r"\bstack\b", "STACK Infrastructure", "STACK Infrastructure"),
    (r"compass", "Compass Datacenters", "Compass Datacenters"),
    (r"aligned", "Aligned Data Centers", "Aligned Data Centers"),
    (r"sabey", "Sabey", "Sabey Data Centers"),
    (r"\bntt\b", "NTT", "NTT Ltd."),
    (r"cologix", "Cologix", "Cologix"),
    (r"databank", "DataBank", "DataBank"),
    (r"zayo|zcolo", "Zayo", "Zayo Group"),
    (r"verizon", "Verizon", "Verizon Communications"),
    (r"coreweave", "CoreWeave", "CoreWeave, Inc."),
    (r"crusoe", "Crusoe", "Crusoe Energy Systems"),
    (r"lancium", "Lancium", "Lancium LLC"),
    (r"\biren\b|ie us", "IREN", "IREN Ltd"),
    (r"nexus", "Nexus Data Centers", "Nexus Data Centers"),
    (r"edgecore|edge core", "EdgeCore", "EdgeCore Digital Infrastructure"),
    (r"cipher", "Cipher Mining", "Cipher Mining Inc."),
    (r"core scientific", "Core Scientific", "Core Scientific, Inc."),
    (r"switch", "Switch", "Switch, Inc."),
    (r"lambda", "Lambda", "Lambda, Inc."),
    (r"tecfusions", "TECfusions", "TECfusions"),
    (r"northrop", "Northrop Grumman", "Northrop Grumman Corporation"),
]


def guess_operator(*names: str) -> tuple[str | None, str | None]:
    blob = " ".join(n for n in names if n)
    for rx, op, parent in OPERATORS:
        if re.search(rx, blob, re.IGNORECASE):
            return op, parent
    first = next((n for n in names if n), None)
    if first:
        op = re.split(r"\s+-\s+|\s+\(|,\s*(?:Inc|LLC|L\.L\.C)", first)[0].strip()
        return op or None, None
    return None, None


def slug(s: str, n: int = 80) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return s[:n].rstrip("-")


def fnum(x) -> float | None:
    try:
        if x is None or (isinstance(x, float) and pd.isna(x)) or x == "":
            return None
        return float(x)
    except (TypeError, ValueError):
        return None


def sval(x) -> str | None:
    if x is None or (isinstance(x, float) and pd.isna(x)) or x == "":
        return None
    return str(x)


def load_ct_columns() -> tuple[list[str], list[str]]:
    try:
        sys.path.insert(0, str(TO_CT))
        import to_climate_trace as ct  # type: ignore

        return list(ct.EMIS), list(ct.OWN)
    except Exception:  # noqa: BLE001
        pass
    if SCHEMA_JSON.exists():
        s = json.loads(SCHEMA_JSON.read_text())
        return list(s["emissions_csv_columns"]), list(s["ownership_csv_columns"])
    return EMIS_EMBEDDED, OWN_EMBEDDED


def ct_rows(site: dict[str, Any], led: dict[str, Any] | None, emis_cols: list[str], own_cols: list[str], today: str):
    """Same mapping as scrapers/to_climate_trace.py main()."""
    s = site
    sid = f"ledger-dc-{s['site_id']}"
    row = {k: "" for k in emis_cols}
    row.update({"source_id": sid, "source_name": s["name"], "source_type": "datacenter", "iso3_country": s["country"],
                "sector": "power", "subsector": "electricity-consumption-datacenters (proposed)",
                "start_time": "", "end_time": "", "lat": s["lat"], "lon": s["lon"], "gas": "co2e_100yr", "emissions_quantity": "",
                "temporal_granularity": "annual", "activity": "", "activity_units": "MWh",
                "capacity": s.get("capacity_mw_it") or "", "capacity_units": "MW IT load" if s.get("capacity_mw_it") else "",
                "other1": s.get("generator_mw_permitted") or "", "other1_def": "Backup generator capacity permitted (MW), from the air permit; a floor on site load",
                "other2": s.get("cooling") or "unknown", "other2_def": "Cooling type from permit or environmental assessment: air|evaporative|closed_loop|seawater|unknown",
                "other3": s.get("status") or "", "other3_def": "Site status: operating|under_construction|permitted|announced",
                "other4": s.get("capacity_source") or "", "other4_def": "Where capacity came from: permit|register|operator|osm",
                "other5": s.get("source_url") or "", "other5_def": "URL of the public record that establishes the site",
                "other6": (led or {}).get("claim", "")[:400] if led else "", "other6_def": "Operator's public claim about the site's energy or water, from the ledger entry",
                "other7": (led or {}).get("gap", "")[:400] if led else "", "other7_def": "Ledger gap line: where record and claim differ",
                "other8": s.get("ledger_entry_id") or "", "other8_def": "Compute Ledger entry id with full sources",
                "other9": s.get("confidence") or "", "other9_def": "Seed-list confidence in site identity and coordinates: high|medium|low",
                "other10": s.get("licence") or "", "other10_def": "Licence of the source record: public_record|ODbL|CC0|operator_site",
                "created_date": today, "modified_date": today})
    o = {k: "" for k in own_cols}
    o.update({"parent_name": s.get("parent_company") or s.get("operator") or "", "source_operator": s.get("operator") or "",
              "percentage_of_operation": "100" if s.get("operator") else "", "overall_share_percent": "", "ownership_path": "",
              "source_id": sid, "source_name": s["name"], "source_sector": "power", "source_subsector": "electricity-consumption-datacenters (proposed)"})
    return row, o


def main() -> None:
    ap = C.base_parser(__doc__)
    ap.add_argument("--seed-sites", type=Path, default=SEED_SITES)
    ap.add_argument("--include-weak", action="store_true", help="also take coordinates from street-level geocodes and weak TCEQ name matches")
    ap.add_argument("--include-unmatched-tceq", action="store_true", default=True,
                    help="add TCEQ data-center packages that matched no Comptroller row (tx_unmatched_tceq_packages.csv) as sites")
    args = ap.parse_args()
    out_dir = Path(args.out)
    today = "2026-10-20" if args.fixture else dt.date.today().isoformat()
    seed_path = args.seed_sites if args.seed_sites.exists() else FIXTURES / "seed_sites.json"
    sites: list[dict[str, Any]] = json.loads(seed_path.read_text(encoding="utf-8"))
    by_url = {s.get("source_url"): s for s in sites}
    ledger_entries: dict[str, Any] = {}
    for f in (ROOT / "registry").glob("*.json") if (ROOT / "registry").exists() else []:
        if f.name in ("sources.json", "guide.json", "standard.json", "climate_trace_schema.json", "seed_sites.json"):
            continue
        try:
            for e in json.loads(f.read_text(encoding="utf-8")):
                if isinstance(e, dict) and "id" in e:
                    ledger_entries[e["id"]] = e
        except Exception:  # noqa: BLE001
            pass

    geo = {}
    gp = out_dir / "geocoded.csv"
    if gp.exists():
        for _, r in pd.read_csv(gp, dtype=str, keep_default_na=False).iterrows():
            geo[r["row_key"]] = r

    def coords_from_geocode(key: str) -> tuple[float | None, float | None, str | None, str | None, str | None]:
        g = geo.get(key)
        if g is None or not g.get("lat"):
            return None, None, None, None, (g["reason"] if g is not None and g.get("reason") else "no geocode")
        conf = g["confidence"]
        if conf in ("high", "medium") or (args.include_weak and conf == "low"):
            return float(g["lat"]), float(g["lon"]), f"geocode:{g['geocoder']}:{g['match_quality']}", conf, g.get("reason") or None
        return None, None, None, None, f"geocode withheld ({g['match_quality']}, confidence {conf}): {g.get('reason') or ''}".strip()

    new_rows: list[dict[str, Any]] = []
    updated = 0

    # ---- Virginia
    va = out_dir / "va_permits.csv"
    if va.exists():
        for _, r in pd.read_csv(va, dtype=str, keep_default_na=False).iterrows():
            name_list = r["facility_name_list"]
            op, parent = guess_operator(name_list, r.get("permittee_pdf"))
            lat, lon, method, cconf, creason = coords_from_geocode(r["backlog_id"])
            mw = fnum(r.get("total_standby_mw"))
            notes = [f"VA DEQ registration {r['registration_no']}; list: {name_list}, {r['locality_list']}, latest permit {r['permit_date_list']} ({r['program_list']})"]
            if r.get("permittee_pdf"):
                notes.append(f"PDF permittee: {r['permittee_pdf']}; approved {r.get('approved_on') or '?'}" + (f", amended {r['last_amended']}" if r.get("last_amended") else ""))
            if r.get("facility_address_raw"):
                notes.append(f"facility address (permit): {r['facility_address_raw']} [{r.get('address_confidence')}]")
            if mw is not None:
                notes.append(f"{r.get('generator_count')} gen-sets, {mw} MW standby summed from per-unit ekW ratings "
                             f"(range {r.get('total_standby_mw_min')}-{r.get('total_standby_mw_max')}; confidence {r.get('total_mw_confidence')}); units: {r.get('unit_kw_list')}")
            if r.get("hours_all_purpose_per_year") or r.get("hours_maint_per_year"):
                notes.append(f"hours/yr limits: all purposes {r.get('hours_all_purpose_per_year') or '?'}, maintenance/testing {r.get('hours_maint_per_year') or '?'}"
                             + (f", combined {r['hours_combined_per_year']}" if r.get("hours_combined_per_year") else ""))
            if r.get("fuel"):
                notes.append(f"fuel: {r['fuel']}")
            if r.get("registration_match") and r["registration_match"] != "match":
                notes.append(f"registration check: {r['registration_match']}")
            if r.get("extract_reason"):
                notes.append(f"extraction: {r['extract_reason']}")
            if creason:
                notes.append(f"coordinates: {creason}")
            conf = "high" if (lat is not None and cconf == "high" and r.get("address_confidence") == "high") else ("medium" if lat is not None else "low")
            new_rows.append({
                "site_id": slug(f"usa-va-deq-{r['registration_no']}-{name_list}"),
                "name": f"{name_list} (VA DEQ reg. {r['registration_no']})",
                "operator": op, "parent_company": parent, "country": "USA", "admin_region": "Virginia",
                "city": sval(r.get("facility_city")) or re.sub(r"\s+County$", "", r["locality_list"] or "") or None,
                "lat": lat, "lon": lon, "status": "permitted", "capacity_mw_it": None, "capacity_source": "permit" if mw is not None else None,
                "generator_mw_permitted": mw, "cooling": "unknown", "first_year": None,
                "source_url": sval(r.get("pdf_url")) or r["source_url"], "source_type": "permit", "licence": "public_record",
                "ledger_entry_id": None, "confidence": conf, "last_checked": today,
                "coord_source_url": ("https://nominatim.openstreetmap.org/" if method and "nominatim" in method else
                                     "https://geocoding.geo.census.gov/" if method else None),
                "notes": " | ".join(notes),
                "backlog_id": r["backlog_id"], "registration_id": f"DEQ registration {r['registration_no']}",
                "address": sval(r.get("facility_address_raw")), "generator_count": fnum(r.get("generator_count")),
                "coord_method": method, "coord_confidence": cconf, "located": lat is not None,
                "needs_review": bool(r.get("extract_reason")) or r.get("total_mw_confidence") == "low",
            })

    # ---- Texas
    tx = out_dir / "tx_permits.csv"
    seen_tx: set[str] = set()
    if tx.exists():
        for _, r in pd.read_csv(tx, dtype=str, keep_default_na=False).iterrows():
            if r["backlog_id"] in seen_tx:  # Giga Texas, Hockley, Cipher Black Pearl are on both Comptroller lists
                continue
            seen_tx.add(r["backlog_id"])
            url = sval(r.get("application_url"))
            weak = bool(url) and any(w in (r.get("match_method") or "") for w in ("weak", "unverified", "ambiguous"))
            mw = fnum(r.get("total_standby_mw"))
            lat = fnum(r.get("lat"))
            lon = fnum(r.get("lon"))
            method = f"permit:{r['coord_source']}" if lat is not None else None
            cconf = r.get("coord_confidence") if lat is not None else None
            creason = None
            if lat is not None and weak and not args.include_weak:
                creason = f"coordinates withheld: TCEQ match is {r['match_method']} (name-only evidence) - confirm by hand"
                lat = lon = method = cconf = None
            if lat is None:
                lat, lon, method, cconf, creason2 = coords_from_geocode(r["backlog_id"])
                creason = creason or creason2
            notes = [f"Texas Comptroller registration '{r['comptroller_name']}' effective {r.get('record_date')}; owner: {r.get('owner')}; operator: {r.get('operator')}; occupant: {r.get('occupant')}"]
            if url:
                notes.append(f"TCEQ match ({r['match_method']}): {r.get('match_applicant')} / {r.get('match_area_name')}; permit {r.get('tceq_permit_no')}; project {r.get('tceq_project_id')}; "
                             f"{r.get('rn') or ''} {r.get('regulated_entity_name') or ''}".strip())
                if r.get("street"):
                    notes.append(f"address (TCEQ): {r['street']}, {r.get('city')}, TX {r.get('zip')} ({r.get('county')} County); NAICS {r.get('naics')}")
            elif r.get("street"):
                notes.append(f"address (register): {r['street']}, {r.get('city')} ({r.get('county')} County)")
            if mw is not None:
                notes.append(f"{r.get('generator_count')} generators, {mw} MW standby from OP-SUM unit kW (confidence {r.get('total_mw_confidence')}); units: {r.get('unit_kw_list')}")
            elif r.get("generator_count"):
                notes.append(f"{r['generator_count']} generator units listed, kW not stated")
            if r.get("reason"):
                notes.append(f"status: {r['reason']}")
            if creason:
                notes.append(f"coordinates: {creason}")
            op, parent = guess_operator(r.get("occupant"), r.get("operator"), r.get("owner"), r["comptroller_name"])
            row = {
                "site_id": slug(f"usa-tx-{r['comptroller_name']}-{r['backlog_id'].split('-')[-1]}"),
                "name": f"{r['comptroller_name']} (Texas Comptroller registration)",
                "operator": op, "parent_company": parent, "country": "USA", "admin_region": "Texas",
                "city": sval(r.get("city")), "lat": lat, "lon": lon,
                "status": "permitted" if url and not weak else "registered",
                "capacity_mw_it": None, "capacity_source": "permit" if mw is not None else None, "generator_mw_permitted": mw,
                "cooling": "unknown", "first_year": None, "source_url": url or r["source_url"], "source_type": "permit" if url else "register",
                "licence": "public_record", "ledger_entry_id": None,
                "confidence": "high" if (lat is not None and cconf == "high" and not weak) else ("medium" if lat is not None else "low"),
                "last_checked": today, "coord_source_url": url if (method or "").startswith("permit") and not weak else (
                    "https://nominatim.openstreetmap.org/" if method and "nominatim" in method else "https://geocoding.geo.census.gov/" if method else None),
                "notes": " | ".join(notes),
                "backlog_id": r["backlog_id"], "registration_id": sval(r.get("rn")), "address": (f"{r['street']}, {r.get('city')}, TX {r.get('zip')}" if r.get("street") else None),
                "generator_count": fnum(r.get("generator_count")), "coord_method": method, "coord_confidence": cconf,
                "located": lat is not None, "needs_review": weak or bool(r.get("reason")),
            }
            existing = by_url.get(url) if url else None
            if existing is not None:
                if existing.get("generator_mw_permitted") is None and mw is not None:
                    existing["generator_mw_permitted"] = mw
                    existing["capacity_source"] = "permit"
                existing["notes"] = (existing.get("notes") or "") + f" | v2 merge: Comptroller row {r['backlog_id']} ({r['comptroller_name']}) maps to this permit."
                existing["last_checked"] = today
                existing.setdefault("backlog_ids", [])
                existing["backlog_ids"].append(r["backlog_id"])
                updated += 1
                continue
            new_rows.append(row)

    # ---- TCEQ packages with no Comptroller row
    un = out_dir / "tx_unmatched_tceq_packages.csv"
    if un.exists() and args.include_unmatched_tceq:
        for _, r in pd.read_csv(un, dtype=str, keep_default_na=False).iterrows():
            url = r["application_url"]
            if url in by_url or r.get("text_quality") != "ok":
                continue
            lat, lon = fnum(r.get("lat")), fnum(r.get("lon"))
            mw = fnum(r.get("total_standby_mw"))
            op, parent = guess_operator(r.get("applicant"), r.get("area_name"))
            new_rows.append({
                "site_id": slug(f"usa-tx-tceq-{r.get('tceq_project_id')}-{r.get('site_name') or r.get('area_name')}"),
                "name": f"{r.get('site_name') or r.get('area_name')} ({r.get('applicant')}; TCEQ project {r.get('tceq_project_id')})",
                "operator": op, "parent_company": parent, "country": "USA", "admin_region": "Texas", "city": sval(r.get("city")),
                "lat": lat, "lon": lon, "status": "permitted", "capacity_mw_it": None, "capacity_source": "permit" if mw is not None else None,
                "generator_mw_permitted": mw, "cooling": "unknown", "first_year": None, "source_url": url, "source_type": "permit",
                "licence": "public_record", "ledger_entry_id": None,
                "confidence": "high" if lat is not None and r.get("coord_confidence") == "high" else ("medium" if lat is not None else "low"),
                "last_checked": today, "coord_source_url": url if lat is not None else None,
                "notes": f"TCEQ application ({r.get('source')}) not in the Texas Comptroller list under this name; {r.get('rn') or ''} {r.get('regulated_entity_name') or ''}; "
                         f"address {r.get('street')}, {r.get('city')}, TX {r.get('zip')} ({r.get('county')} County); NAICS {r.get('naics')}; "
                         f"generators: {r.get('generator_count') or '?'} units, {mw if mw is not None else 'MW not stated'}",
                "backlog_id": None, "registration_id": sval(r.get("rn")), "address": f"{r.get('street')}, {r.get('city')}, TX {r.get('zip')}" if r.get("street") else None,
                "generator_count": fnum(r.get("generator_count")), "coord_method": f"permit:{r.get('coord_source')}" if lat is not None else None,
                "coord_confidence": sval(r.get("coord_confidence")) if lat is not None else None, "located": lat is not None, "needs_review": True,
            })

    # possible duplicates of existing rows (same operator word + same admin_region + close coordinates)
    for n in new_rows:
        for s in sites:
            if n["lat"] is None or s.get("lat") is None or s.get("admin_region") != n["admin_region"]:
                continue
            if abs(s["lat"] - n["lat"]) < 0.02 and abs(s["lon"] - n["lon"]) < 0.02:
                n["notes"] += f" | possible duplicate of existing seed row {s['site_id']} (within ~2 km)"
                n["needs_review"] = True

    all_sites = sites + new_rows
    C.write_json(all_sites, out_dir / "seed_sites_v2.json")
    flat = pd.DataFrame([{k: s.get(k) for k in SEED_KEYS + EXTRA_KEYS} for s in all_sites])
    C.write_csv(flat, out_dir / "seed_sites_v2.csv")

    emis_cols, own_cols = load_ct_columns()
    ct_dir = out_dir / "climate_trace"
    er, orr = [], []
    for s in all_sites:
        if s.get("lat") is None or s.get("lon") is None:
            continue
        row, o = ct_rows(s, ledger_entries.get(s.get("ledger_entry_id") or ""), emis_cols, own_cols, today)
        er.append(row)
        orr.append(o)
    ct_dir.mkdir(parents=True, exist_ok=True)
    for name, cols, rows in (("datacenters_emissions_seed.csv", emis_cols, er), ("datacenters_ownership_seed.csv", own_cols, orr)):
        buf = []
        import io

        sio = io.StringIO()
        w = csv.DictWriter(sio, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
        C.write_bytes(sio.getvalue().encode("utf-8"), ct_dir / name)

    def count(rows, pred):
        return sum(1 for s in rows if pred(s))

    by_state = {}
    groups = {"Virginia": lambda s: s.get("admin_region") == "Virginia", "Texas": lambda s: s.get("admin_region") == "Texas",
              "other (v1 rows)": lambda s: s.get("admin_region") not in ("Virginia", "Texas")}
    for st, pred in groups.items():
        rows = [s for s in all_sites if pred(s)]
        by_state[st] = {"sites": len(rows), "with_coordinates": count(rows, lambda s: s.get("lat") is not None),
                        "with_generator_mw": count(rows, lambda s: s.get("generator_mw_permitted") is not None),
                        "generator_mw_sum": C.round_mw(sum(s.get("generator_mw_permitted") or 0 for s in rows), 1),
                        "needs_review": count(rows, lambda s: s.get("needs_review"))}
    summary = {
        **C.run_meta(args.fixture, [{"name": "seed_sites.json (v1)", "path": str(seed_path), "rows": len(sites)}]),
        "sites_total": len(all_sites), "sites_v1_kept": len(sites), "sites_v1_updated_from_permits": updated, "sites_added": len(new_rows),
        "with_coordinates": len(er), "with_generator_mw": count(all_sites, lambda s: s.get("generator_mw_permitted") is not None),
        "with_coordinates_and_generator_mw": count(all_sites, lambda s: s.get("lat") is not None and s.get("generator_mw_permitted") is not None),
        "by_state": by_state,
        "by_coord_method": pd.Series([s.get("coord_method") or ("v1" if s.get("lat") is not None else "none") for s in all_sites]).value_counts().to_dict(),
        "climate_trace": {"emissions_rows": len(er), "ownership_rows": len(orr), "columns_emissions": len(emis_cols), "columns_ownership": len(own_cols),
                          "schema": "Climate TRACE v5.11.0 asset files (to_climate_trace.py mapping)"},
        "weak_matches_included": args.include_weak,
    }
    C.write_json(summary, out_dir / "handover_summary.json")
    C.log(f"seed_sites_v2.json: {summary['sites_total']} sites ({summary['sites_added']} added, {updated} updated), "
          f"{summary['with_coordinates']} with coordinates, {summary['with_generator_mw']} with generator MW; Climate TRACE rows: {len(er)}")


if __name__ == "__main__":
    C.run_main(main)
