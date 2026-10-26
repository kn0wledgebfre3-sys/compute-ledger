#!/usr/bin/env python3
"""Build the Climate TRACE asset files of the handover from the reviewed sources in this repository.

Writes, into data/climate_trace_seed/ (or --out):
  datacenters_emissions_seed.csv          Climate TRACE v5.11.0 asset emissions columns, one row per LOCATED site
  datacenters_ownership_seed.csv          v5.11.0 asset ownership columns, same rows
  datacenters_register_backlog_unlocated.csv   register-identified sites without a usable coordinate
  assets_summary.json                     counts by source

Sources, in this order (no network, no estimates):
  1. sites/seed_sites.json       worldwide seed list (56 located sites); rows superseded by a permit or
                                 licence row below are dropped (DUPLICATES)
  2. sites/ireland_sites.json    40 Irish sites from EPA licences, ETS permits and planning appeals
  3. data/climate_trace_seed/va_permits_resolved.csv + virginia_nearest_generation.csv
                                 Virginia DEQ permits, figures as resolved by the second reading;
                                 coordinates from the 2026-10-21 geocode of the permit's site address
  4. data/climate_trace_seed/tx_issued_sites.csv   Texas facilities from regulator records (tx_fetch.py)
Claim and gap slots (other6, other7) are copied from the current registry entry named in other8.

Coordinate rule. Document coordinates (EPA licence grid references, TCEQ Core Data Forms and permits)
and EPA FRS points are used as given. A Virginia geocode (va_geocodes.csv, run on 2026-10-21 on the
first reading's address; va_geocodes_2026-10-23.csv, a second run of the US Census single-address
geocoder on the permits' site addresses) is used only when (a) the geocoder matched the street address (rooftop,
census_exact, census_non_exact) and (b) the address it geocoded is the permit's site address as resolved
by the second reading, not the permittee's mailing address. Other sites go to the backlog with their
resolved MW and the reason.

Usage:  python3 pipeline/build_handover_assets.py [--out DIR]
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "data" / "climate_trace_seed"
TODAY = "2026-10-22"
VA_LIST_URL = "https://www.deq.virginia.gov/news-info/shortcuts/permits/air/issued-air-permits-for-data-centers"
TX_COMPTROLLER_URL = "https://comptroller.texas.gov/taxes/data-centers/data-center-lists.php"
SUBSECTOR = "electricity-consumption-datacenters (proposed)"

EMIS = ['source_id', 'source_name', 'source_type', 'iso3_country', 'sector', 'subsector', 'start_time', 'end_time', 'lat', 'lon',
        'geometry_ref', 'gas', 'emissions_quantity', 'temporal_granularity', 'activity', 'activity_units', 'emissions_factor',
        'emissions_factor_units', 'capacity', 'capacity_units', 'capacity_factor', 'capacity_factor_units', 'other1', 'other1_def',
        'other2', 'other2_def', 'other3', 'other3_def', 'other4', 'other4_def', 'other5', 'other5_def', 'other6', 'other6_def',
        'other7', 'other7_def', 'other8', 'other8_def', 'other9', 'other9_def', 'other10', 'other10_def', 'created_date', 'modified_date']
OWN = ['parent_name', 'parent_entity_id', 'parent_entity_type', 'parent_lei', 'parent_permid', 'parent_registration_country',
       'parent_headquarter_country', 'overall_share_percent', 'ownership_path', 'ownership_path_datasource_ids', 'immediate_source_owner',
       'immediate_source_owner_entity_id', 'source_operator', 'source_operator_id', 'percentage_of_operation', 'source_id', 'source_name',
       'source_sector', 'source_subsector']
DEFS = {
    "other1_def": "Permitted on-site generator capacity (MW) from the permit or licence. other4 gives the unit and basis: standby fleets (an upper bound on site load once redundancy is known) are distinguished from primary on-site generation and from thermal-input figures",
    "other2_def": "Cooling type from permit or environmental assessment: air|evaporative|closed_loop|seawater|unknown",
    "other3_def": "Site status: operating|under_construction|permitted|pending|refused|announced; blank where no record establishes it",
    "other4_def": "Basis of other1: document, unit (MWe, MW as stated, or MWth rated thermal input), standby or primary generation, and how the figure was summed",
    "other5_def": "URL of the public record that establishes the site",
    "other6_def": "Operator's public claim about the site's energy or water, from the ledger entry",
    "other7_def": "Ledger gap line: where record and claim differ",
    "other8_def": "Compute Ledger entry id with full sources",
    "other9_def": "Confidence in site identity and coordinates: high (coordinate from the regulator's document) | medium (EPA registry point, or a geocode of the permit's street address) | low",
    "other10_def": "Licence of the source record: public_record|ODbL|CC0|operator_site",
}

# Seed-list rows that describe the same site as a permit or licence row from a later source.
DUPLICATES = {
    "usa-microsoft-sn-campus-sn1-sn2-sn4-sn7-san-antonio": ("tx", "ms-sn-campus"),
    "usa-childress-data-center-iren": ("tx", "iren-childress"),
    "usa-compass-red-oak-datacenter-dfw-iii": ("tx", "compass-red-oak"),
    "usa-alamo-mission-data-center-red-oak": ("tx", "alamo-mission"),
    "usa-google-midlothian-data-center": ("tx", "sharka"),  # Sharka LLC, Google per the Comptroller; 0.3 km apart
    "irl-google-dublin-grange-castle-data-center": ("ie", "irl-google-grange-castle-ghg170"),
    "irl-vantage-data-centers-profile-park-campus-dub1x-dub13-refused": ("ie", "irl-vantage-dub13-profile-park-abp317446-refused"),
}
VA_GEOCODE_OK = {"rooftop", "census_exact", "census_non_exact"}

# Facility names as printed in the permit text, where OCR garbled them or the name field held an address
# or boilerplate. The permit's own permittee line supplies the corrected spelling in every case.
VA_NAME_FIX = {
    "71804": "Science Applications International Corporation", "73567": "Digital Reston, LLC",
    "73813": "Northrop Grumman Systems Corporation", "74060": "U.S. Customs and Border Protection",
    "74064": "VADATA, Inc.", "74094": "RagingWire VA2 Data Center", "73823": "Level 3 Communications",
    "73158": "Qwest Communications Corporation", "73995": "VADATA, Inc. IAD-14/52/59",
    "73853": "Amazon Data Services, Inc. IAD-10", "73717": "Visa, Inc.",
}
VA_PERMITTEE_FIX = {"72368": "AOL, LLC", "73717": "Visa, Inc."}  # permittee field held permit boilerplate
ADDRESS_LIKE = re.compile(r"^\d+[\s,]+(?!.*\b(LLC|L\.P\.|LP|Inc|Corporation)\b)")

# Seed-list rows that carry a generator figure: the basis is stated explicitly (and Southaven updated
# to the MDEQ permit read on 2026-10-22). A seed row with a generator figure not listed here stops the build.
SEED_GEN = {
    "usa-xai-colossus-1-south-memphis": (247.5, "permit, MW on-site gas turbines (primary generation, not standby): Shelby County Health Department Air Permit No. 01156-01PC (2025-07-02), 15 Solar SMT-130 units; 15 x 16.5 MW per unit = 247.5 MW, computed (the permit is not online; its terms are quoted in the appeal of 2025-07-16)"),
    "usa-xai-colossus-2-mzx-tech-southaven-turbine-site": (1240.0, "permit, MW on-site gas turbines (primary generation, not standby): MDEQ PSD Air Construction Permit 0680-00119 (2026-03-11), 41 units, about 1,240 MW"),
    "usa-homer-city-energy-campus-former-coal-plant": (4678.0, "plan approval, MWe on-site gas generation (primary supply, not standby): PA DEP Plan Approval 32-00457A, 7 GE 7HA.02 + 10 FT8 MOBILEPAC"),
    "usa-microsoft-west-des-moines-willow-creek-ginger-east-data-centers": (340.8, "permit, MWe standby: sum of unit ratings in the Iowa DNR draft Title V tables (128 diesel engines); 20 units assumed 3,000 kW where the text was truncated"),
}

OPERATORS = [
    (r"amazon|aws\b|vadata|corporate office properties|copt\b", "Amazon Web Services", "Amazon.com, Inc."),
    (r"microsoft", "Microsoft", "Microsoft Corporation"),
    (r"google|sharka", "Google", "Alphabet Inc."),
    (r"\bmeta\b|facebook", "Meta", "Meta Platforms, Inc."),
    (r"oracle", "Oracle", "Oracle Corporation"),
    (r"\bqts\b", "QTS", "QTS (Blackstone)"),
    (r"equinix", "Equinix", "Equinix, Inc."),
    (r"digital realty|dupont fabros|\bdlr\b", "Digital Realty", "Digital Realty Trust"),
    (r"cyrusone", "CyrusOne", "CyrusOne (KKR/GIP)"),
    (r"vantage", "Vantage Data Centers", "Vantage Data Centers"),
    (r"iron mountain", "Iron Mountain", "Iron Mountain Inc."),
    (r"cloud ?hq", "CloudHQ", "CloudHQ"),
    (r"\bstack\b", "STACK Infrastructure", "STACK Infrastructure"),
    (r"compass", "Compass Datacenters", "Compass Datacenters"),
    (r"aligned", "Aligned Data Centers", "Aligned Data Centers"),
    (r"sabey", "Sabey", "Sabey Data Centers"),
    (r"\bntt\b|raging wire", "NTT", "NTT Ltd."),
    (r"coreweave", "CoreWeave", "CoreWeave, Inc."),
    (r"edgecore|edge core", "EdgeCore", "EdgeCore Digital Infrastructure"),
]


def guess_operator(*names: str) -> tuple[str, str]:
    blob = " ".join(n for n in names if n)
    for rx, op, parent in OPERATORS:
        if re.search(rx, blob, re.IGNORECASE):
            return op, parent
    return "", ""


def slug(s: str, n: int = 70) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")[:n].rstrip("-")


def num(x):
    try:
        if x in (None, "", "None"):
            return None
        return float(x)
    except (TypeError, ValueError):
        return None


def fmt_mw(x) -> str:
    v = num(x)
    if v is None:
        return ""
    return f"{v:.3f}".rstrip("0").rstrip(".")


def read_csv(p: Path) -> list[dict]:
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_registry() -> dict[str, dict]:
    out = {}
    for f in sorted(glob.glob(str(ROOT / "registry" / "*.json"))):
        if os.path.basename(f) in ("sources.json", "guide.json", "standard.json"):
            continue
        for e in json.load(open(f, encoding="utf-8")):
            out[e["id"]] = e
    return out


def row(site: dict, reg: dict[str, dict]) -> tuple[dict, dict]:
    led = reg.get(site.get("ledger_entry_id") or "")
    e = {k: "" for k in EMIS}
    e.update({
        "source_id": f"ledger-dc-{site['site_id']}", "source_name": site["name"], "source_type": "datacenter",
        "iso3_country": site["country"], "sector": "power", "subsector": SUBSECTOR, "lat": site["lat"], "lon": site["lon"],
        "gas": "co2e_100yr", "temporal_granularity": "annual", "activity_units": "MWh",
        "capacity": site.get("capacity_mw_it") or "",
        "capacity_units": (f"MW IT load ({site['capacity_source']})" if site.get("capacity_source") else "MW IT load") if site.get("capacity_mw_it") else "",
        "other1": fmt_mw(site.get("generator_mw_permitted")), "other2": site.get("cooling") or "unknown",
        "other3": site.get("status") or "", "other4": site.get("gen_basis") or "",
        "other5": site.get("source_url") or "",
        "other6": (led["claim"][:400] if led else ""), "other7": (led["gap"][:400] if led else ""),
        "other8": site.get("ledger_entry_id") or "", "other9": site.get("confidence") or "",
        "other10": site.get("licence") or "public_record", "created_date": TODAY, "modified_date": TODAY,
    })
    e.update(DEFS)
    o = {k: "" for k in OWN}
    parent = site.get("parent_company") or site.get("operator") or ""
    if parent.startswith("Amazon.com Inc. (AWS); landlord"):
        parent = "Amazon.com, Inc."
    parent = PARENTS.get(parent, parent)
    o.update({"parent_name": parent, "source_operator": "" if site.get("operator") == "unknown" else (site.get("operator") or ""),
              "percentage_of_operation": "100" if site.get("operator") else "", "source_id": e["source_id"],
              "source_name": site["name"], "source_sector": "power", "source_subsector": SUBSECTOR})
    return e, o


FRS_LAYER = "https://services.arcgis.com/cJ9YHowT8TU7DUyn/ArcGIS/rest/services/FRS_INTERESTS/FeatureServer/0"


def tx_url(t: dict) -> str:
    """A bare public URL for a Texas facility: the TCEQ document, or the EPA FRS record its coordinates came from."""
    first = (t.get("source_urls") or "").split(" ; ")[0].strip()
    ids = [x for x in re.split(r"[;,\s]+", t.get("frs_registry_ids") or "") if x]
    if "FRS_INTERESTS" in first or not first:
        # the EPA FRS service the coordinates were read from, queried for this facility's record
        base = FRS_LAYER
        if ids:
            return f"{base}/query?where=REGISTRY_ID%3D%27{ids[0]}%27&outFields=*&f=html"
        m = re.search(r"(?:record|RN) (RN\d+|[A-Z0-9]{6,})", t.get("coord_source") or "")
        if m:
            return f"{base}/query?where=PGM_SYS_ID%3D%27{m.group(1)}%27&outFields=*&f=html"
        return first.split(" ")[0]
    return first.split(" ")[0]


PARENTS = {  # one spelling per parent in the ownership file
    "Amazon.com Inc. (AWS)": "Amazon.com, Inc.", "Amazon.com Inc.": "Amazon.com, Inc.",
    "Microsoft Corp.": "Microsoft Corporation", "Meta Platforms": "Meta Platforms, Inc.",
    "Meta Platforms Inc.": "Meta Platforms, Inc.", "unknown": "",
}


def clean(v):
    return None if v in (None, "", "None") else v


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=PKG)
    a = ap.parse_args()
    reg = load_registry()
    located: list[dict] = []
    backlog: list[dict] = []
    counts = Counter()
    dropped = []

    # 1 + 2: seed list and Ireland (seed_sites schema)
    ire = json.load(open(ROOT / "sites" / "ireland_sites.json", encoding="utf-8"))
    ire_by_id = {r["site_id"]: r for r in ire}
    for s in json.load(open(ROOT / "sites" / "seed_sites.json", encoding="utf-8")):
        if s["site_id"] in DUPLICATES:
            src, key = DUPLICATES[s["site_id"]]
            if src == "ie" and s.get("ledger_entry_id") and not ire_by_id[key].get("ledger_entry_id"):
                ire_by_id[key]["ledger_entry_id"] = s["ledger_entry_id"]
            dropped.append({"seed_site_id": s["site_id"], "replaced_by": f"{src}:{key}"})
            continue
        s = {k: clean(v) for k, v in s.items()}
        if s.get("lat") is None:
            continue
        s.setdefault("licence", "public_record")
        if s["site_id"] in SEED_GEN:
            s["generator_mw_permitted"], s["gen_basis"] = SEED_GEN[s["site_id"]]
        elif s.get("generator_mw_permitted"):
            raise SystemExit(f"seed row {s['site_id']} has a generator figure without a stated basis; add it to SEED_GEN")
        located.append(s)
        counts["seed_list"] += 1
    for s in ire:
        s = {k: clean(v) for k, v in s.items()}
        if s.get("lat") is None:
            backlog.append({"backlog_id": f"ie-{s['site_id']}", "register": "Ireland site list (EPA licences, ETS permits, planning appeals)",
                            "name": s["name"], "operator_or_owner": s.get("operator") or "", "country": "IRL",
                            "admin_region": s.get("admin_region") or "", "locality": s.get("city") or "", "record_id": s["site_id"],
                            "generator_info": (f"{fmt_mw(s.get('generator_mw_permitted'))} MW permitted" if s.get("generator_mw_permitted") else ""),
                            "source_url": s.get("source_url") or "", "licence": "public_record",
                            "notes": "No open-source coordinate in the documents read; see ireland_regional_check.md"})
            counts["ireland_unlocated"] += 1
            continue
        s.setdefault("licence", "public_record")
        if s.get("generator_mw_permitted"):
            s["gen_basis"] = "licence or GHG permit: " + (s.get("generator_mw_basis") or "basis not recorded")
        located.append(s)
        counts["ireland"] += 1

    # 3: Virginia, resolved figures
    geo = {r["registration"]: r for r in read_csv(PKG / "virginia_nearest_generation.csv")}
    gq = {r["row_key"].replace("va-deq-", ""): r for r in read_csv(PKG / "va_geocodes.csv")}
    # second run, 2026-10-23: US Census single-address geocoder on the permits' site addresses
    gq2 = {r["row_key"].replace("va-deq-", ""): r for r in read_csv(PKG / "va_geocodes_2026-10-23.csv")}

    def same_address(reg_no: str, r: dict, src: dict | None = None) -> tuple[bool, str]:
        """The geocoder ran on the first reading's address, which was sometimes the permittee's mailing
        address. Accept the point only if its query (house number and first street word) appears in the
        site address that the second reading resolved."""
        q = (src if src is not None else gq).get(reg_no)
        if not q:
            return False, "no geocode record"
        norm = lambda x: re.sub(r"[^a-z0-9 ]", " ", (x or "").lower()).split()
        m = re.match(r"\s*(\d+)\s+(\w+)", " ".join(norm(q["query_street"])))
        site = norm(r["site_street"] + " " + r["site_city_line"])
        if m and m.group(1) in site and m.group(2) in site:
            return True, ""
        return False, f"the address sent to the geocoder was {q['query_street']}, {q['query_city']}, not the permit's site address"
    for r in read_csv(PKG / "va_permits_resolved.csv"):
        reg_no = r["registration"]
        if reg_no == "5":  # an 'Access Denied' page saved as 5.pdf, not a registration
            continue
        permittee = VA_PERMITTEE_FIX.get(reg_no, r["permittee"])
        name0 = VA_NAME_FIX.get(reg_no) or (permittee if ADDRESS_LIKE.match(r["facility_name"] or "") else None) \
            or r["facility_name"] or permittee or f"VA DEQ registration {reg_no}"
        op, parent = guess_operator(name0, permittee)
        mw = fmt_mw(r["total_standby_mw"])
        g = geo.get(reg_no)
        county = (r["site_county"] or "").replace(", VA", "")
        addr_ok, addr_why = same_address(reg_no, r)
        if not (g and g["geocode_quality"] in VA_GEOCODE_OK and addr_ok):
            # a usable point from either geocode run whose query is the resolved site address
            for src in (gq, gq2):
                q = src.get(reg_no)
                if q and q["lat"] and q["match_quality"] in VA_GEOCODE_OK | {"census_interpolated"} \
                        and q["confidence"] in ("high", "medium") and same_address(reg_no, r, src)[0]:
                    g = {"lat": q["lat"], "lon": q["lon"], "geocode_quality": q["match_quality"]}
                    addr_ok, addr_why = True, ""
                    break
        if g and g["geocode_quality"] in VA_GEOCODE_OK | {"census_interpolated"} and addr_ok:
            located.append({
                "site_id": f"usa-va-deq-{reg_no}-{slug(name0, 50)}", "name": f"{name0} (VA DEQ reg. {reg_no})",
                "operator": op or permittee, "parent_company": parent, "country": "USA", "admin_region": "Virginia",
                "lat": round(float(g["lat"]), 6), "lon": round(float(g["lon"]), 6), "status": "permitted",
                "generator_mw_permitted": mw or None, "capacity_source": None, "cooling": "unknown",
                "gen_basis": (f"permit, MWe standby: sum of unit ratings, {int(float(r['generator_count']))} units (Virginia DEQ registration {reg_no}; figures resolved by two independent readings, {r['resolved_confidence']} confidence)" if mw else ""),
                "source_url": VA_LIST_URL, "licence": "public_record", "ledger_entry_id": None,
                "confidence": "medium" if g["geocode_quality"] in ("rooftop", "census_exact", "census_interpolated") else "low",
            })
            counts["virginia"] += 1
        else:
            why = (addr_why if (reg_no in gq and not addr_ok) else
                   f"geocode match type '{g['geocode_quality']}' not used" if g else "site address not geocoded")
            backlog.append({"backlog_id": f"va-deq-{reg_no}", "register": "Virginia DEQ issued air permits for data centers",
                            "name": name0, "operator_or_owner": permittee, "country": "USA", "admin_region": "Virginia",
                            "locality": county, "record_id": f"DEQ registration {reg_no}", "record_date": r["permit_date"],
                            "generator_info": (f"{int(float(r['generator_count']))} units, {mw} MW permitted standby (resolved, {r['resolved_confidence']} confidence)"
                                               if mw and r["generator_count"] else (f"{mw} MW permitted standby (resolved)" if mw else "no inventory read")),
                            "source_url": VA_LIST_URL, "licence": "public_record",
                            "notes": f"Street address in the permit: {r['site_street'] or 'not read'}; {why}."})
            counts["virginia_unlocated"] += 1

    # 4: Texas facilities from regulator records
    issued_re = re.compile(r"issued|effective|exists|renewal", re.I)
    pending_re = re.compile(r"pending|under review|notice|draft|deficienc|initial review|administratively complete|preliminary", re.I)
    tx_unmatched_ids = set()
    tx_rows = read_csv(PKG / "tx_issued_sites.csv")
    for t in tx_rows:
        st = t["authorization_status"] or ""
        status = "permitted" if issued_re.search(st) else ("pending" if pending_re.search(st) else "")
        on_site_mw = t["generator_mw"] if t["air_record"] == "yes" else ""  # Meta El Paso's 366 MW is a utility plant, not standby
        op = (t["operator"] or "").split(" (")[0].strip()
        op2, parent = guess_operator(t["operator"], t["permittee"], t["facility_name"])
        site = {
            "site_id": f"usa-tx-{t['facility_key']}", "name": t["facility_name"], "operator": op or op2 or t["permittee"],
            "parent_company": parent, "country": "USA", "admin_region": "Texas", "status": status,
            "generator_mw_permitted": fmt_mw(on_site_mw) or None, "capacity_source": None,
            "gen_basis": ("permit, MWe standby: " + re.sub(r"^[a-z0-9-]+: ", "", t["generator_basis"] or "")[:300]) if on_site_mw else "",
            "cooling": "unknown", "source_url": tx_url(t), "licence": "public_record",
            "ledger_entry_id": None,
            "confidence": "high" if (t["coord_source"] or "").startswith("TCEQ") else "medium",
        }
        if t["lat"]:
            site["lat"], site["lon"] = round(float(t["lat"]), 6), round(float(t["lon"]), 6)
            located.append(site)
            counts["texas"] += 1
        else:
            backlog.append({"backlog_id": f"tx-site-{t['facility_key']}", "register": "Texas facilities from TCEQ / EPA / PUC records (tx_issued_sites.csv)",
                            "name": t["facility_name"], "operator_or_owner": t["operator"] or t["permittee"], "country": "USA",
                            "admin_region": "Texas", "locality": t["county"], "record_id": t["tceq_permit_numbers"] or t["tceq_rn"],
                            "generator_info": (f"{t['generator_count']} units" if t["generator_count"] else "") +
                                              (f", {t['generator_mw']} MW ({t['generator_basis'][:80]})" if t["generator_mw"] else ""),
                            "source_url": tx_url(t), "licence": "public_record",
                            "notes": "No coordinate in the records read; a live run of pipeline/tx_fetch.py should locate it."})
            counts["texas_unlocated"] += 1

    # Texas Comptroller rows not matched to any facility, and the other register rows still unlocated
    matched = {x for t in tx_rows for x in (t["backlog_id"] or "").split(";") if x}
    cand = {}
    for t in tx_rows:
        for c in (t["backlog_candidates"] or "").split(";"):
            c = c.strip().split(" [")[0]
            if c:
                cand.setdefault(c, []).append(t["facility_key"])
    for b in read_csv(ROOT / "sites" / "seed_sites_unlocated.csv"):
        if b["register"].startswith("Virginia DEQ"):
            continue  # replaced by the resolved Virginia rows above
        if b["backlog_id"] == "tx-tceq-O4794":
            continue  # CyrusOne SAT2-4, now located through EPA FRS (usa-tx-cyrusone-sat2-4)
        m = re.match(r"ie-epa-(P\d+)-", b["backlog_id"])
        if m and any(m.group(1).lower() in r["site_id"] and r.get("lat") not in (None, "", "None") for r in ire):
            continue  # located in the Ireland list from the licence's own grid reference
        if b["register"].startswith("Texas Comptroller"):
            if b["backlog_id"] in matched:
                continue
            if b["backlog_id"] in cand:
                b["notes"] = (b["notes"] + " " if b["notes"] else "") + "Candidate facility in tx_issued_sites.csv: " + ", ".join(cand[b["backlog_id"]]) + " (needs one confirming document)."
            counts["texas_comptroller_unmatched"] += 1
        else:
            counts["other_registers_unlocated"] += 1
        backlog.append(b)

    emis, own = [], []
    seen = set()
    for s in located:
        e, o = row(s, reg)
        assert e["source_id"] not in seen, e["source_id"]
        seen.add(e["source_id"])
        emis.append(e)
        own.append(o)

    a.out.mkdir(parents=True, exist_ok=True)
    for name, cols, rows in (("datacenters_emissions_seed.csv", EMIS, emis), ("datacenters_ownership_seed.csv", OWN, own)):
        with open(a.out / name, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
    bcols = ["backlog_id", "register", "name", "operator_or_owner", "occupant_or_tenant", "country", "admin_region", "locality",
             "record_id", "record_date", "program_or_type", "generator_info", "source_url", "licence", "notes"]
    with open(a.out / "datacenters_register_backlog_unlocated.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=bcols, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        for b in backlog:
            w.writerow({k: b.get(k, "") for k in bcols})
    by_country = Counter(e["iso3_country"] for e in emis)
    summary = {
        "built": TODAY, "schema": "Climate TRACE v5.11.0 asset emissions and ownership columns",
        "located_sites": len(emis),
        "with_generator_capacity": sum(1 for e in emis if e["other1"]),
        "with_generator_capacity_by_basis": dict(Counter(
            ("standby MWe (permit)" if e["other4"].startswith("permit, MWe standby") else
             "primary on-site generation" if "primary" in e["other4"] else
             "Irish licence or GHG permit (mostly MWth input)" if e["other4"].startswith("licence") else "other")
            for e in emis if e["other1"])),
        "virginia_located_standby_mw": round(sum(float(e["other1"]) for e in emis if e["other1"] and "-va-deq-" in e["source_id"]), 1),
        "with_ledger_entry": sum(1 for e in emis if e["other8"]), "countries": len(by_country),
        "by_source": dict(counts), "by_country": dict(sorted(by_country.items(), key=lambda kv: -kv[1])),
        "backlog_unlocated_rows": len(backlog), "seed_rows_dropped_as_duplicates": dropped,
    }
    with open(a.out / "assets_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1)
        f.write("\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "by_country"}, indent=1))


if __name__ == "__main__":
    main()
