#!/usr/bin/env python3
"""Build the ledger's measurements table: every figure, one row, one vocabulary.

Outputs (default into data/climate_trace_seed/, or --out DIR for CI comparison):
  measurements.csv          one row per figure, from every feed below
  site_register.csv         every site any figure refers to, with its id in the Climate TRACE seed and the backlog
  entity_register.csv       utilities, registers and other non-site subjects (copied from sites/entity_register.csv)
  measurements_summary.json counts and the cross-checks the table makes possible

Feeds (each row keeps the file it came from in `feed`):
  registry/*.json                                figures in the entries' record and claim text (sites/measurements_from_registry/*.csv)
  sites/metered/ireland_aer_transcribed.csv      Irish EPA Annual Environmental Reports
  sites/metered/ireland_emission_factors.csv     SEAI factors, for the emissions computed from those reports
  sites/metered/va_nei_transcribed.csv           EPA National Emissions Inventory, Virginia
  sites/metered/benchmarking_transcribed.csv     city benchmarking disclosures
  sites/metered/filed_figures_curated.csv        utility filings and public-utility documents, mapped by hand
  sites/paper/company_figures.csv                companies' own Scope 1 and 2 figures (location- and market-based), certificates, credits
  sites/paper/rule_figures.csv                   figures in the rules and raters entries
  sites/topics/<topic>/sites.csv, figures.csv     a topic's own sites (with a kind) and figures, e.g. crypto mining
  data/climate_trace_seed/va_permits_resolved.csv  Virginia permits, two readings resolved
  data/climate_trace_seed/tx_issued_sites.csv      Texas facilities
  sites/ireland_sites.json, sites/seed_sites.json  permit and licence figures in the site lists

Rules enforced here (and again by validate_measurements.py):
  every metric, unit and basis is in measurement_vocab.json;
  every value_as_published occurs verbatim in the text it was taken from;
  conversions only through units.py, with the factor in the vocabulary.
"""
import argparse
import csv
import hashlib
import json
import re
from collections import defaultdict
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import units  # noqa: E402
from build_handover_assets import DUPLICATES, SEED_GEN, VA_LIST_URL  # noqa: E402
from build_metered import LICENCE_SITE  # noqa: E402

PKG = ROOT / "data" / "climate_trace_seed"
MET = ROOT / "sites" / "metered"
FROM_REG = ROOT / "sites" / "measurements_from_registry"
V = units.VOCAB

COLS = ["measurement_id", "subject_type", "subject_id", "entry_id", "metric", "metric_detail",
        "value", "value_high", "unit", "value_canonical", "value_high_canonical", "canonical_unit",
        "value_as_published", "qualifier", "period_start", "period_end", "basis", "side",
        "source_url", "source_title", "source_publisher", "source_date",
        "feed", "extraction", "second_read", "notes"]
SITE_COLS = ["site_id", "name", "operator", "kind", "country", "admin_region", "locality", "lat", "lon", "status",
             "ct_source_id", "backlog_id", "register_source", "also_known_as", "notes"]

# Site ids are never reused or silently dropped (CONTRIBUTING). An id that turns out to be a second id for one site is
# retired here, pointing to the id kept; the builder writes them all to site_id_aliases.csv and the site pages redirect.
RETIRED_SITE_IDS = {
    "usa-va-nei-21504711": ("usa-va-deq-74086", "inventory facility matched to its DEQ permit by street address (21111 Ridgetop Circle), 2026-10-24"),
}

# the document behind each seed-list generation figure (SEED_GEN in build_handover_assets.py)
SEED_GEN_SOURCE = {
    "usa-xai-colossus-1-south-memphis": dict(
        url="https://cdn.arstechnica.net/wp-content/uploads/2025/07/NAACP-and-YGGs-xAI-Air-Permit-Appeal-7-15-2025.pdf",
        title="Appeal of Shelby County Health Department Air Permit No. 01156-01PC, NAACP and Young, Gifted & Green to the Memphis and Shelby County Air Pollution Control Board",
        publisher="Southern Environmental Law Center for the appellants (copy hosted by Ars Technica)", date="2025-07-16",
        entry="us-tn-memphis-xai-colossus-turbines", basis="derived", vap="247.5 MW (computed)", second_read="yes",
        detail=("computed: 15 SMT-130 turbines permitted by Shelby County Health Department Air Permit No. 01156-01PC (issued 2 July 2025) "
                "x 16.5 MW per Solar SMT-130 (the appeal's Table 2); on-site gas generation, primary supply (not standby)"),
        count=15, count_detail="gas turbines (Solar SMT-130) authorized by Air Permit No. 01156-01PC",
        count_note=("The appeal quotes the permit: 'authorizes the construction and permanent operation of 15 SMT-130 turbines' and "
                    "'the Health Department issued the CTC Permit on July 2, 2025'. The permit itself is not online.")),
    "usa-xai-colossus-2-mzx-tech-southaven-turbine-site": dict(
        url="https://opc.deq.state.ms.us/get_doc.aspx?dt=finalp&id=1834338",
        title="PSD Air Construction Permit No. 0680-00119, MZX Tech LLC, 2875 Stanton Road, Southaven (AI 12592)",
        publisher="Mississippi Department of Environmental Quality (enSearch Online)", date="2026-03-11", entry="us-ms-southaven-xai-1.2gw-gas",
        second_read="yes"),
    "usa-homer-city-energy-campus-former-coal-plant": dict(
        url="https://files.dep.state.pa.us/regionalresources/NWRO/NWROPortalFiles/Homer-City/Air/Final-AQ-Plan-Approval/Tech%20Review%20Memo%20Signed%2020251118.pdf",
        title="Technical review memorandum, Plan Approval 32-00457A, Homer City Redevelopment", publisher="Pennsylvania Department of Environmental Protection",
        date="2025-11-18", entry="us-pa-homer-city-gas-campus", second_read="yes"),
    "usa-microsoft-west-des-moines-willow-creek-ginger-east-data-centers": dict(
        url="https://iowadnr.gov/portals/idnr/uploads/air/operpermit/draftpermits/7016d.pdf",
        title="Draft Title V operating permit, Microsoft data centers, West Des Moines (file 77-02-040)", publisher="Iowa Department of Natural Resources",
        date="2024-11-07", entry="", detail="standby generators, sum of unit ratings in the draft permit's tables (128 diesel engines)"),
}

FEED_ENTRY = {
    "aer": "ie-epa-aer-metered-2025",
    "nei": "us-va-nei-2023-datacenter-generator-emissions",
    "bench": "us-city-benchmarking-datacenter-metered-electricity",
    "va_filed": "us-va-dominion-datacenter-demand-filed-2026",
    "va_permits": "us-va-loudoun-diesel-backup-generators",
}
PP_ENTRY = {"us-utility-mlgw": "us-tn-memphis-xai-colossus-turbines", "us-federal-tva": "us-tn-memphis-xai-colossus-turbines",
            "us-utility-grant-pud": "us-wa-grant-pud-datacenter-load-2025", "us-utility-svp": "us-ca-santa-clara-svp-datacenter-share-2025"}

# documents re-read directly before publication (see METERED.md and the entries' verification notes)
AER_REREAD = {("P1170-01", "2025"), ("P1171-01", "2025"), ("P1182-01", "2025"), ("P1187-01", "2025"), ("P1168-01", "2024")}
NEI_NAICS_REREAD = {"21510611", "15410111", "21519111", "17626111", "21496611", "21506611", "21508611", "21518611", "21518811",
                    "21519211", "21504811", "21519011", "21504711", "21504611", "21504911", "6744011", "21519611", "21518711",
                    "21512611", "21518911", "21496711", "21512711", "21519511"}
FILED_REREAD = {("va_datacenter_class_demand.csv", i) for i in (12, 13, 14, 15, 16, 17, 18, 48, 49, 50)} | \
               {("public_power_loads.csv", i) for i in (5, 6, 8, 11, 13, 14)}
BENCH_REREAD = {("San Francisco", "200 PAUL AVE"), ("San Francisco", "365 MAIN ST"), ("New York City", "60 Hudson Street")}

NEI_METRIC = {"NOX": "emissions_nox", "CO": "emissions_co", "VOC": "emissions_voc", "SO2": "emissions_so2",
              "PM10-PRI": "emissions_pm10", "PM25-PRI": "emissions_pm25"}
EXTRA_SITES = [
    {"site_id": "usa-xai-tulane-road-memphis", "name": "xAI Tulane Road site (second Memphis site)", "operator": "xAI", "kind": "datacenter",
     "country": "USA", "admin_region": "Tennessee", "locality": "Memphis", "register_source": "MLGW xAI Update, 5 May 2025",
     "notes": "named in MLGW's update; no coordinate from a record yet"},
    {"site_id": "usa-microsoft-malaga-chelan", "name": "Microsoft datacenter, Malaga (Chelan County PUD)", "operator": "Microsoft", "kind": "datacenter",
     "country": "USA", "admin_region": "Washington", "locality": "Malaga", "register_source": "Chelan County PUD large-load framework, June 2025",
     "notes": "named in the PUD's agreements; no coordinate from a record yet"},
]


QUAL = [("lower_bound", r"\b(at least|more than|over|above|exceeds?|exceeded|greater than|minimum of|no less than)\b|[>≥]|\+\s*$"),
        ("upper_bound", r"\b(up to|at most|maximum|max\.?|no more than|not more than|below|under|less than|capped at)\b|[<≤]"),
        ("approximate", r"\b(about|approximately|approx\.?|around|nearly|almost|roughly|some|circa|c\.)\b|~|≈")]


PREFIX_QUAL = [("upper_bound", r"(no more than|not more than|not above|not to exceed|no greater than)\s*$"),
               ("lower_bound", r"(no less than|not less than|not below)\s*$"),
               ("lower_bound", r"(at least|more than|over|above|exceeding|exceeded|greater than|minimum of|[>≥])\s*$"),
               ("upper_bound", r"(up to|at most|maximum of|below|under|less than|capped at|[<≤])\s*$"),
               ("approximate", r"(about|approximately|approx\.|around|nearly|almost|roughly|some|circa|[~≈])\s*$")]
DURATION = re.compile(r"\b(years?|months?|weeks?|days?|hours?)\b", re.I)


def qualifier_in_context(value_as_published: str, published_text) -> str:
    """The qualifier from the figure itself, or else from the words immediately before it in the text it was taken from."""
    q = qualifier(value_as_published)
    if q or not published_text or not value_as_published or value_as_published not in published_text:
        return q
    before = published_text[:published_text.index(value_as_published)][-24:].lower()
    if DURATION.search(value_as_published):
        before = re.sub(r"\bover\s*$", "", before)  # 'over 30 years' is a period, not a bound
    for name, pat in PREFIX_QUAL:
        if re.search(r"(^|[\s(])" + pat, before):
            return name
    return ""


def qualifier(text: str, notes: str = "") -> str:
    """'lower_bound', 'upper_bound', 'approximate' or '' from the words around the figure as published."""
    t = (text or "").lower()
    t = re.sub(r"\bover (the )?(next |past )?\d+\s*(years?|months?|days?|hours?)\b", "", t)  # 'over 5 years' is a period
    if re.search(r"\b(not above|not more than|no more than|not exceed\w*|not to exceed|no greater than)\b", t):
        return "upper_bound"
    if re.search(r"\b(not below|not less than|no less than)\b", t):
        return "lower_bound"
    for name, pat in QUAL:
        if re.search(pat, t):
            return name
    return ""


def read_csv(p: Path) -> list[dict]:
    return list(csv.DictReader(open(p, encoding="utf-8")))


def slug(s: str, n: int = 60) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")[:n].strip("-")


def year_period(y: str) -> tuple[str, str]:
    y = (y or "").strip()
    return (f"{y}-01-01", f"{y}-12-31") if re.fullmatch(r"\d{4}", y) else ("", "")


def iso_date(s: str) -> str:
    for fmt in ("%B %d, %Y", "%b %d, %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime((s or "").strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return ""


MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"


def date_in(title: str) -> str:
    """A full date printed in a document title ('dated August 30, 2024', 'filed 15 Oct 2025', '2026-09-29'); else ''."""
    t = title or ""
    m = re.search(rf"\b({MONTHS}) (\d{{1,2}}), (\d{{4}})\b", t)
    if m:
        return iso_date(m.group(0))
    m = re.search(rf"\b(\d{{1,2}}) ({MONTHS}|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec) (\d{{4}})\b", t)
    if m:
        for fmt in ("%d %B %Y", "%d %b %Y"):
            try:
                return datetime.strptime(m.group(0).replace("Sept", "Sep"), fmt).strftime("%Y-%m-%d")
            except ValueError:
                pass
    m = re.search(r"\b(\d{2})\.(\d{2})\.(20\d{2})\b", t)
    if m:
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    m = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", t)
    return m.group(1) if m else ""


def first_number(cell: str) -> str:
    m = re.search(r"-?\d[\d,]*\.?\d*", cell or "")
    return m.group(0) if m else ""


def num(s: str):
    return float(s.replace(",", "")) if s else None


class Table:
    def __init__(self):
        self.rows: list[dict] = []
        self.problems: list[str] = []

    def add(self, *, feed, subject_type, subject_id, metric, metric_detail, value, unit, value_as_published, source_url,
            entry_id="", value_high="", period_start="", period_end="", basis, side="record", source_title="",
            source_publisher="", source_date="", extraction, second_read="no", notes="", published_text=None):
        if metric not in V["metrics"]:
            self.problems.append(f"{feed}: metric {metric!r} not in vocabulary")
        if unit not in V["units"]:
            self.problems.append(f"{feed}: unit {unit!r} not in vocabulary")
        if basis not in V["bases"]:
            self.problems.append(f"{feed}: basis {basis!r} not in vocabulary")
        if not re.match(r"^https?://[^\s<>\"\\]+$", source_url or ""):
            self.problems.append(f"{feed}: source_url is not a single well-formed URL ({subject_id}, {metric}): {source_url[:80]!r}")
        if source_date and not re.fullmatch(r"\d{4}(-\d{2}(-\d{2})?)?", source_date):
            self.problems.append(f"{feed}: source_date {source_date!r} is not YYYY, YYYY-MM or YYYY-MM-DD ({subject_id}, {metric})")
        if not feed.startswith("registry/") and basis == "company_statement":
            side = "claim"  # outside the registry text, a company's figure is a claim wherever it was transcribed
        if published_text is not None and value_as_published not in published_text:
            self.problems.append(f"{feed}: {value_as_published!r} not found verbatim in its source text ({subject_id}, {metric})")
        value, value_high = units.fmt(value), units.fmt(value_high)  # the stored value is the one converted
        vc, cu = units.to_canonical(value, unit)
        vhc, _ = units.to_canonical(value_high, unit) if value_high else (None, None)
        key = "|".join(str(x) for x in (feed, subject_id, metric, metric_detail, period_start, period_end, value_as_published, source_url, side, entry_id))
        self.rows.append({
            "measurement_id": "m-" + hashlib.sha1(key.encode()).hexdigest()[:10],
            "subject_type": subject_type, "subject_id": subject_id, "entry_id": entry_id, "metric": metric,
            "metric_detail": metric_detail, "value": units.fmt(value), "value_high": units.fmt(value_high), "unit": unit,
            "value_canonical": units.fmt(vc), "value_high_canonical": units.fmt(vhc), "canonical_unit": cu or "",
            "value_as_published": value_as_published, "qualifier": qualifier_in_context(value_as_published, published_text), "period_start": period_start, "period_end": period_end,
            "basis": basis, "side": side, "source_url": source_url, "source_title": source_title,
            "source_publisher": source_publisher, "source_date": source_date, "feed": feed, "extraction": extraction,
            "second_read": second_read, "notes": notes,
        })


# ---------------------------------------------------------------- site register
def build_sites() -> tuple[list[dict], dict]:
    ct_rows = {r["source_id"]: r for r in read_csv(PKG / "datacenters_emissions_seed.csv")}
    ct = set(ct_rows)
    backlog = {r["backlog_id"] for r in read_csv(PKG / "datacenters_register_backlog_unlocated.csv")}
    sites: dict[str, dict] = {}

    def put(s):
        s = {c: ("" if s.get(c) is None else s.get(c)) for c in SITE_COLS}
        if s["site_id"] in sites:
            raise SystemExit(f"duplicate site id {s['site_id']}")
        sites[s["site_id"]] = s

    for src, path in (("seed list", ROOT / "sites" / "seed_sites.json"), ("Ireland site list", ROOT / "sites" / "ireland_sites.json")):
        for r in json.load(open(path, encoding="utf-8")):
            sid = r["site_id"]
            ctid = f"ledger-dc-{sid}"
            if sid in DUPLICATES:  # the same site is in the register from a permit or licence; keep its name as an alias there
                continue
            put({"site_id": sid, "name": r["name"], "operator": r.get("operator"), "kind": "datacenter", "country": r["country"],
                 "admin_region": r.get("admin_region"), "locality": r.get("city"), "lat": r.get("lat"), "lon": r.get("lon"),
                 "status": r.get("status"), "ct_source_id": ctid if ctid in ct else "",
                 "backlog_id": f"ie-{sid}" if f"ie-{sid}" in backlog else "", "register_source": src})
    ct_va = {}
    for c in ct:
        m = re.match(r"ledger-dc-usa-va-deq-(\d+)-", c)
        if m:
            ct_va[m.group(1)] = c
    for r in read_csv(PKG / "va_permits_resolved.csv"):
        reg = r["registration"]
        if reg == "5":
            continue
        put({"site_id": f"usa-va-deq-{reg}", "name": r["facility_name"] or r["permittee"] or f"VA DEQ registration {reg}",
             "operator": r["permittee"], "kind": "datacenter", "country": "USA", "admin_region": "Virginia",
             "locality": (r["site_county"] or "").replace(", VA", ""), "status": "permitted", "ct_source_id": ct_va.get(reg, ""),
             "lat": ct_rows[ct_va[reg]]["lat"] if reg in ct_va else "", "lon": ct_rows[ct_va[reg]]["lon"] if reg in ct_va else "",
             "backlog_id": f"va-deq-{reg}" if f"va-deq-{reg}" in backlog else "", "register_source": "Virginia DEQ issued air permits for data centers",
             "also_known_as": f"DEQ registration {reg}", "notes": f"site address in the permit: {r['site_street'] or 'not read'}"})
    for t in read_csv(PKG / "tx_issued_sites.csv"):
        sid = f"usa-tx-{t['facility_key']}"
        put({"site_id": sid, "name": t["facility_name"], "operator": t["operator"] or t["permittee"], "kind": "datacenter", "country": "USA",
             "admin_region": "Texas", "locality": t["city"] or t["county"], "lat": t["lat"], "lon": t["lon"], "status": t["authorization_status"],
             "ct_source_id": f"ledger-dc-{sid}" if f"ledger-dc-{sid}" in ct else "",
             "backlog_id": f"tx-site-{t['facility_key']}" if f"tx-site-{t['facility_key']}" in backlog else "",
             "register_source": "Texas facilities from TCEQ, EPA and PUC records", "also_known_as": t["tceq_rn"]})
    for s in EXTRA_SITES:
        put(s)
    for seed_id, (kind, key) in sorted(DUPLICATES.items()):
        target = f"usa-tx-{key}" if kind == "tx" else key
        if target not in sites:
            raise SystemExit(f"DUPLICATES: {seed_id} points to {target}, which is not in the register")
        RETIRED_SITE_IDS[seed_id] = (target, "seed-list row for a site already in the register from a permit or licence")
        aka = sites[target]["also_known_as"]
        sites[target]["also_known_as"] = "; ".join(x for x in (aka, f"seed list id {seed_id}") if x)
    return list(sites.values()), sites


# ---------------------------------------------------------------- feeds
def feed_registry(T: Table, entries: dict):
    for p in sorted(FROM_REG.glob("rows_*.csv")):
        for r in read_csv(p):
            e = entries[r["entry_id"]]
            side = r["side"]
            src = next((s for s in e.get("record_sources" if side == "record" else "claim_sources", []) if s["url"] == r["source_url"]), {})
            T.add(feed=f"registry/{p.stem.replace('rows_', '')}.json", subject_type="entry", subject_id=r["entry_id"], entry_id=r["entry_id"],
                  metric=r["metric"], metric_detail=r["metric_detail"], value=r["value"], value_high=r["value_high"],
                  unit=r["unit_as_published"], value_as_published=r["value_as_published"], period_start=r["period_start"],
                  period_end=r["period_end"], basis=r["basis"], side=side, source_url=r["source_url"],
                  source_title=src.get("title", ""), source_publisher=src.get("publisher", ""), source_date=src.get("date", ""),
                  extraction="registry_prose", second_read="yes" if e.get("verification_status") == "verified" else "no",
                  notes=r["notes"], published_text=e.get(side, ""))


def feed_aer(T: Table):
    for r in read_csv(MET / "ireland_aer_transcribed.csv"):
        lic, yr = r["licence_no"], r["report_year"]
        site = LICENCE_SITE[lic][0]
        ps, pe = year_period(yr)
        if (lic, yr) == ("P1181-01", "2024"):
            ps = "2024-08-08"
        common = dict(feed="sites/metered/ireland_aer_transcribed.csv", subject_type="site", subject_id=site, entry_id=FEED_ENTRY["aer"],
                      period_start=ps, period_end=pe, basis="metered", source_url=r["document_url"],
                      source_title=r["document_title_and_date"], source_publisher="Environmental Protection Agency (Ireland), LEAP",
                      extraction="hand_transcribed", second_read="yes" if (lic, yr) in AER_REREAD else "no")
        for col, metric, detail in (("electricity_gj", "electricity_consumed", "electricity used, AER Table 3 'Energy Used'"),
                                    ("light_fuel_oil_gj", "generator_fuel_burned", "light fuel oil (diesel), AER Table 3"),
                                    ("renewable_biomass_hvo_gj", "generator_fuel_burned", "renewable biomass, AER Table 3"),
                                    ("natural_gas_gj", "natural_gas_burned", "natural gas, AER Table 3")):
            vap = first_number(r[col])
            if vap:
                T.add(metric=metric, metric_detail=detail, value=num(vap), unit="GJ", value_as_published=vap,
                      notes=r["notes"], published_text=r[col], **common)
        vap = first_number(r["water_m3"])
        if vap:
            T.add(metric="water_withdrawn", metric_detail="total water used, all sources, AER Table 5 'Water Used'", value=num(vap),
                  unit="m3", value_as_published=vap, notes=r["notes"], published_text=r["water_m3"], **common)


def feed_aer_emissions(T: Table):
    """Emissions computed by the ledger for each licensed Irish site from its metered energy (the AER rows above)
    and published factors (sites/metered/ireland_emission_factors.csv): SEAI's grid factor for location-based Scope 2, and the
    EPA's EU ETS factors for the diesel and natural gas burned on site. HVO is biogenic and counted as zero CO2."""
    F = {}
    for f in read_csv(MET / "ireland_emission_factors.csv"):
        if f["components"]:
            s = sum(float(x) for x in f["components"].split(";"))
            if abs(s - float(f["value"])) > 0.006:
                T.problems.append(f"ireland_emission_factors: {f['factor_id']} components sum to {s:.4f}, value says {f['value']}")
        F[f["factor_id"]] = f
    for r in read_csv(MET / "ireland_aer_transcribed.csv"):
        lic, yr = r["licence_no"], r["report_year"]
        site = LICENCE_SITE[lic][0]
        ps, pe = year_period(yr)
        if (lic, yr) == ("P1181-01", "2024"):
            ps = "2024-08-08"
        base = dict(feed="sites/metered/ireland_emission_factors.csv", subject_type="site", subject_id=site, entry_id=FEED_ENTRY["aer"],
                    period_start=ps, period_end=pe, basis="derived", source_url=r["document_url"],
                    source_title=r["document_title_and_date"] + "; with SEAI factors",
                    source_publisher="Environmental Protection Agency (Ireland), LEAP; SEAI", extraction="pipeline_and_second_reading",
                    second_read="yes" if (lic, yr) in AER_REREAD else "no", published_text=None)
        el = first_number(r["electricity_gj"])
        ef = F.get(f"ie-elec-{yr}")
        if el and ef:
            t = num(el) / 3.6 * float(ef["value"]) / 1000
            T.add(metric="emissions_scope2_location", metric_detail=(
                      f"computed: metered electricity {el} GJ / 3.6 = {num(el) / 3.6:,.0f} MWh x SEAI {yr} factor {ef['value']} gCO2e/kWh "
                      "(Irish average for electricity consumed); location-based, so it ignores any contracts or certificates"),
                  value=round(t), unit="t", value_as_published=f"{t:,.0f} t CO2e (computed)",
                  notes=f"Factor: {ef['source_url']} ({ef['notes']})", **base)
        oil = first_number(r["light_fuel_oil_gj"])
        gas = first_number(r["natural_gas_gj"])
        if not (oil or gas):
            continue
        go, gf, g2n = F[f"ie-gasoil-{yr}"], F[f"ie-gas-{yr}"], F[f"ie-gas-g2n-{yr}"]
        t_oil = num(oil) * float(go["value"]) / 1000 if oil else 0.0
        hi = t_oil + (num(gas) * float(gf["value"]) / 1000 if gas else 0.0)
        lo = t_oil + (num(gas) * float(g2n["value"]) * float(gf["value"]) / 1000 if gas else 0.0)
        parts = ([f"gas oil {oil} GJ x {go['value']} t CO2/TJ"] if oil else []) + \
                ([f"natural gas {gas} GJ x {gf['value']} t CO2/TJ, the GJ taken as net (high) or as gross and multiplied by {g2n['value']} (low)"] if gas else [])
        rd = (lambda x: round(x, 1)) if hi < 10 else round
        lo_s, hi_s = (f"{lo:,.1f}", f"{hi:,.1f}") if hi < 10 else (f"{lo:,.0f}", f"{hi:,.0f}")
        T.add(metric="emissions_co2", metric_detail=(
                  "computed: CO2 from fuel burned on site (the fuel part of Scope 1; refrigerant losses and other gases not included): "
                  + "; ".join(parts) + f"; EPA's {yr} factors for EU ETS reports; HVO counted as zero (biogenic)"),
              value=rd(lo), value_high=rd(hi) if gas else "", unit="t",
              value_as_published=(f"{lo_s} to {hi_s} t CO2 (computed)" if gas else f"{lo_s} t CO2 (computed)"),
              notes=("The annual report does not say whether its gas GJ are gross or net, hence the range. " if gas else "")
                    + f"Factors: {go['source_url']}. {go['notes']}", **base)


def feed_nei(T: Table, sites: dict):
    for r in read_csv(MET / "va_nei_transcribed.csv"):
        metric = NEI_METRIC.get(r["pollutant"])
        if not metric or r["tons_per_year"] in ("", "not found"):
            continue
        reg = r["registration"]
        weak = re.search(r"NOT con|fragment only|not matched", r["how_matched"])
        subject = f"usa-va-deq-{reg}" if (reg.isdigit() and not weak and f"usa-va-deq-{reg}" in sites) else f"usa-va-nei-{r['eis_facility_id_or_deq_id']}"
        if subject not in sites:
            sites[subject] = {c: "" for c in SITE_COLS} | {
                "site_id": subject, "name": r["facility_name_in_inventory"], "kind": "datacenter", "country": "USA", "admin_region": "Virginia",
                "register_source": f"EPA National Emissions Inventory, EIS facility {r['eis_facility_id_or_deq_id']}",
                "also_known_as": f"EIS {r['eis_facility_id_or_deq_id']}",
                "notes": ("candidate DEQ registration " + reg + "; " if reg.isdigit() else "") + r["how_matched"][:200]}
        ps, pe = year_period(r["year"])
        rer = r["eis_facility_id_or_deq_id"] in NEI_NAICS_REREAD and r["pollutant"] == "NOX" and r["year"] == "2023" \
            or r["eis_facility_id_or_deq_id"] == "21518811" and r["year"] == "2023"
        T.add(feed="sites/metered/va_nei_transcribed.csv", subject_type="site", subject_id=subject, entry_id=FEED_ENTRY["nei"],
              metric=metric, metric_detail=f"{r['pollutant']}, facility-wide annual total ({r['inventory_source']})",
              value=float(r["tons_per_year"]), unit="short_ton", value_as_published=r["tons_per_year"],
              period_start=ps, period_end=pe, basis="inventory", source_url=r["document_or_endpoint_url"],
              source_title=f"{r['inventory_source']} facility summary, EIS {r['eis_facility_id_or_deq_id']}",
              source_publisher="US EPA Envirofacts", extraction="api_query", second_read="yes" if rer else "no",
              notes=r["how_matched"], published_text=r["tons_per_year"])



def feed_generator_hours(T: Table, sites: dict):
    """Minimum full-load-equivalent hours per generator from the inventory's NOx and the permits' NOx limits.
    The arithmetic is redone here from the transcribed unit rates and checked against the reviewed table."""
    lbhr = {}
    for u in read_csv(MET / "va_permit_unit_rates.csv"):
        if u["nox_rate_unit"] != "lb/hr":
            T.problems.append(f"va_permit_unit_rates: {u['registration']} {u['unit_group']}: rate unit {u['nox_rate_unit']} not converted")
            continue
        lbhr[u["registration"]] = lbhr.get(u["registration"], 0.0) + float(u["unit_count"]) * float(u["nox_rate_each"])
    nei = {(r["registration"], r["year"]): r for r in read_csv(MET / "va_nei_transcribed.csv") if r["pollutant"] == "NOX"}
    for h in read_csv(MET / "va_generator_hours.csv"):
        if h["include"] != "yes":
            continue
        reg, yr = h["registration"], h["year"]
        n = nei.get((reg, yr))
        if not n:
            T.problems.append(f"va_generator_hours: no inventory row for {reg} {yr}")
            continue
        total = lbhr.get(reg, 0.0)
        hours = float(n["tons_per_year"]) * 2000 / total if total else 0.0
        if abs(hours - float(h["min_full_load_equivalent_hours"])) > 0.01 or abs(total - float(h["sum_nox_lb_per_hour_all_units"])) > 0.01:
            T.problems.append(f"va_generator_hours: {reg} {yr} recomputes to {hours:.2f} h from {total:.2f} lb/hr, table says {h['min_full_load_equivalent_hours']}")
            continue
        weak = re.search(r"NOT con|fragment only|not matched", n["how_matched"])
        subject = f"usa-va-deq-{reg}" if (not weak and f"usa-va-deq-{reg}" in sites) else f"usa-va-nei-{n['eis_facility_id_or_deq_id']}"
        ps, pe = year_period(yr)
        common = dict(feed="sites/metered/va_generator_hours.csv", subject_type="site", subject_id=subject, entry_id=FEED_ENTRY["nei"],
                      period_start=ps, period_end=pe, basis="derived", source_url=n["document_or_endpoint_url"],
                      source_title=f"{n['inventory_source']} facility summary, EIS {n['eis_facility_id_or_deq_id']}, with Virginia DEQ permit {reg}",
                      source_publisher="US EPA Envirofacts; Virginia DEQ", extraction="pipeline_and_second_reading", second_read="yes",
                      notes=f"Match: {h['match_quality']}. {h['caveats']}")
        hv = f"{hours:.1f}"
        T.add(metric="generator_hours", metric_detail=("minimum full-load-equivalent hours per generator: inventory NOx (short tons) x 2,000 / "
                      f"sum of the permit's NOx limits for all {reg} units ({total:,.1f} lb/hr); permitted hours per unit: {h['permitted_hours_per_unit']}"),
              value=float(hv), unit="h", value_as_published=f"at least {hv} hours", published_text=None, **common)
        if h["share_of_facility_nox_limit"] and h["facility_nox_limit_tpy"]:
            sh = f"{float(h['share_of_facility_nox_limit']) * 100:.1f}"
            T.add(metric="share_other", metric_detail=f"inventory NOx as a share of the permit's facility-wide NOx limit ({h['facility_nox_limit_tpy']} tons/yr)",
                  value=float(sh), unit="pct", value_as_published=f"{sh}%", published_text=None, **common)

# Benchmarking jurisdictions outside the USA (every earlier jurisdiction is in the USA, so their ids are unchanged)
BENCH_COUNTRY = {"Ontario": "CAN"}
# Disclosures published as files rather than through an open-data portal
BENCH_PUBLISHER = {"California (statewide)": "California Energy Commission (Building Energy Benchmarking Program, AB 802)",
                   "Portland OR": "City of Portland, Bureau of Planning and Sustainability"}


def bench_site_id(r: dict) -> str:
    """The id scheme used since the first release (kept, so published ids do not change)."""
    addr = r["address"]
    if r["jurisdiction"] == "New York City" and re.match(r"56 Hudson", addr):
        addr = "60 Hudson Street"
    a = re.sub(r"\b(street|st)\b", "st", addr.lower())
    a = re.sub(r"\b(avenue|av|ave)\b", "ave", a)
    return f"{BENCH_COUNTRY.get(r['jurisdiction'], 'USA').lower()}-bench-{slug(r['jurisdiction'], 20)}-{slug(a, 50)}"


def bench_building_key(r: dict) -> str:
    """One key per building, whichever way a year's filing spells the address (73rd/73 St, Ctr/Center, 140-10/14010)."""
    addr = r["address"]
    if r["jurisdiction"] == "New York City" and re.match(r"56 Hudson", addr):
        addr = "60 Hudson Street"
    a = addr.lower()
    if r["jurisdiction"] == "New York City":  # Queens house numbers; elsewhere 218-230 is a range and stays
        a = re.sub(r"(?<=\d)-(?=\d)", "", a)
    a = re.sub(r"\b(\d+)(st|nd|rd|th)\b", r"\1", a)
    for pat, rep in ((r"street|st", "st"), (r"avenue|av|ave", "ave"), (r"road|rd", "rd"), (r"center|ctr|centre", "center"),
                     (r"boulevard|blvd", "blvd"), (r"place|pl", "pl"), (r"drive|dr", "dr"), (r"east|e", "e"), (r"west|w", "w"),
                     (r"north|n", "n"), (r"south|s", "s"), (r"square|sq", "sq"), (r"plaza|plz", "plz")):
        a = re.sub(rf"\b({pat})\b\.?", rep, a)
    return f"{r['jurisdiction']}|{slug(a, 80)}"


def bench_ids(rows: list[dict]) -> tuple[dict, dict]:
    """Row id per filing, and the ids retired when two spellings of one building were merged (kept: the smallest id)."""
    groups = defaultdict(set)
    for r in rows:
        groups[bench_building_key(r)].add(bench_site_id(r))
    keep, retired = {}, {}
    for ids in groups.values():
        k = min(ids)
        for i in ids:
            keep[i] = k
            if i != k:
                retired[i] = (k, "the same building filed under another spelling of its address")
    return keep, retired


TELECOM = re.compile(r"^[^/]+/[A-Z .]+/(NY|PA|NJ)\s*$|\bCO/|NTWK/|/VZ[TW]/|verizon|new eng(land)? tel|\bn\.? ?e\.? tel\b|tel [&*] tel|central office|centurylink|lumen|at&t", re.I)
# Portland files its telephone exchanges under Lumen's office names ("BELMONT CO", "ATLANTIC MAIN"); the 2023 file names three of them Centurylink
TELECOM_PDX = re.compile(r"^[A-Z][A-Z .]+ (CO|MAIN)$")


def bench_kind(r: dict) -> str:
    """From the building's own name and owner fields, never from notes about other buildings."""
    t = (r["primary_property_type"] or "").lower()
    owner = re.search(r"owner(?:_company)?[=:]\s*([^;]+)", r["notes"] or "")
    name = (r["property_name"] or "") + " " + (owner.group(1) if owner else "")
    if TELECOM.search((r["property_name"] or "").strip()) or TELECOM.search(name):
        return "telecom_exchange"
    if r["jurisdiction"] == "Portland OR" and TELECOM_PDX.search((r["property_name"] or "").strip()):
        return "telecom_exchange"
    if t.startswith("data center") or re.search(r"data ?cent(er|re)", r["property_name"] or "", re.I):
        return "datacenter"
    return "mixed_building_with_datacenter"


def feed_bench(T: Table, sites: dict):
    rows = read_csv(MET / "benchmarking_transcribed.csv")
    keep, retired = bench_ids(rows)
    RETIRED_SITE_IDS.update(retired)
    for r in rows:
        cell = r["electricity_kwh"]
        vap = first_number(cell)
        if not vap:
            continue
        unit = "kBtu" if ("kbtu=" in cell.lower() or r["notes"].startswith("UNIT:")) else "kWh"
        sid = keep[bench_site_id(r)]
        if sid not in sites:
            sites[sid] = {c: "" for c in SITE_COLS} | {
                "site_id": sid, "name": r["property_name"] or r["address"], "kind": bench_kind(r), "country": BENCH_COUNTRY.get(r["jurisdiction"], "USA"),
                "admin_region": r["jurisdiction"], "locality": r["jurisdiction"], "register_source": f"{r['jurisdiction']} benchmarking disclosure",
                "also_known_as": r["address"], "notes": f"type as filed: {r['primary_property_type']}"}
        ps, pe = year_period(r["report_year"])
        T.add(feed="sites/metered/benchmarking_transcribed.csv", subject_type="site", subject_id=sid, entry_id=FEED_ENTRY["bench"],
              metric="electricity_consumed", metric_detail=f"grid electricity, whole building as filed (type: {r['primary_property_type']})",
              value=num(vap), unit=unit, value_as_published=vap, period_start=ps, period_end=pe, basis="metered",
              source_url=r["dataset_id_or_url"] if " | " in r["query_url"] else r["query_url"], source_title=r["dataset_name"],
              source_publisher=BENCH_PUBLISHER.get(r["jurisdiction"], f"{r['jurisdiction']} open data portal"),
              extraction="api_query", second_read="yes" if (r["jurisdiction"], r["address"]) in BENCH_REREAD else "no",
              notes=("year semantics unconfirmed; " if not ps else "") + r["notes"]
                    + (f" Joined from these queries: {r['query_url']}" if " | " in r["query_url"] else ""), published_text=cell)


# who published the document, where that is not the utility the figure is about ({} is that utility)
FILED_PUBLISHER = {"pecva.org": "Piedmont Environmental Council (testimony filed with the Virginia SCC)", "virginiamercury.com": "Virginia Mercury",
                   "oregonbusiness.com": "Oregon Business", "publicpower.org": "American Public Power Association",
                   "ncpa.com": "Northern California Power Agency (presentation by {})", "sec.gov": "Dominion Energy, Inc. (SEC filing)",
                   "pjm.com": "{} (submitted to PJM)", "memphistn.gov": "City of Memphis (presentation by {} to the City Council)",
                   "umweltbundesamt.de": "Umweltbundesamt"}


def feed_filed(T: Table):
    files = {"va_datacenter_class_demand.csv": read_csv(PKG / "va_datacenter_class_demand.csv"),
             "public_power_loads.csv": read_csv(PKG / "public_power_loads.csv")}
    for c in read_csv(MET / "filed_figures_curated.csv"):
        src = files[c["feed_file"]][int(c["feed_row"])]
        title = src.get("document_title") or src.get("document_title_and_date") or ""
        pub = src.get("entity") or src.get("utility") or ""
        dom = re.sub(r"^https?://(www\.)?([^/]+)/.*", r"\2", src["document_url"])
        pub = FILED_PUBLISHER.get(dom, "{}").format(pub)
        entry = FEED_ENTRY["va_filed"] if c["feed_file"].startswith("va_") else PP_ENTRY.get(c["subject_id"], "")
        if c["subject_id"].startswith("usa-xai-colossus-1"):
            entry = "us-tn-memphis-xai-colossus-turbines"
        T.add(feed=f"sites/metered/filed_figures_curated.csv ({c['feed_file']} row {c['feed_row']})", subject_type=c["subject_type"],
              subject_id=c["subject_id"], entry_id=entry, metric=c["metric"], metric_detail=c["metric_detail"], value=c["value"],
              value_high=c["value_high"], unit=c["unit_as_published"], value_as_published=c["value_as_published"],
              period_start=c["period_start"], period_end=c["period_end"], basis=c["basis"], side=c["side"],
              source_url=src["document_url"], source_title=title, source_publisher=pub, source_date=date_in(title), extraction="hand_transcribed",
              second_read="yes" if (c["feed_file"], int(c["feed_row"])) in FILED_REREAD else "no", notes=c["notes"],
              published_text=src["quoted_line"] + " | " + src["figure"])


COMPANY_ENTITY = {"Microsoft": "co-microsoft", "Alphabet": "co-alphabet", "Google": "co-alphabet", "Alphabet (Google)": "co-alphabet",
                  "Amazon": "co-amazon", "Meta": "co-meta", "Oracle": "co-oracle", "Equinix": "co-equinix",
                  "Digital Realty": "co-digital-realty"}
PAPER = ROOT / "sites" / "paper"


def feed_paper(T: Table):
    p = PAPER / "company_figures.csv"
    if p.exists():
        for r in read_csv(p):
            ent = COMPANY_ENTITY[r["company"]]
            fy = re.fullmatch(r"(FY|CY)(\d{4})", r["fiscal_year"] or "")
            if fy and r["period_end"] and r["period_end"][:4] != fy.group(2):
                # every fiscal year in this file is named for the year it ends in (Microsoft July-June, Oracle June-May)
                T.problems.append(f"company_figures: {r['company']} {r['fiscal_year']} has period {r['period_start']}..{r['period_end']}")
            T.add(feed="sites/paper/company_figures.csv", subject_type="entity", subject_id=ent, entry_id=r["entry_id"],
                  metric=r["metric"], metric_detail=r["metric_detail"], value=r["value"], unit=r["unit"],
                  value_as_published=r["value_as_published"], period_start=r["period_start"], period_end=r["period_end"],
                  basis=r["basis"], side="record" if r["basis"] in ("assured_disclosure", "filed") else "claim",
                  source_url=r["document_url"], source_title=r["document_title"], source_publisher=r["publisher"],
                  source_date=r["document_date"], extraction="hand_transcribed", second_read=r.get("second_read", "no"),
                  notes=(r["page_or_table"] + "; " + r["notes"]).strip("; "), published_text=r["quoted_line"])
    p = PAPER / "rule_figures.csv"
    if p.exists():
        for r in read_csv(p):
            T.add(feed="sites/paper/rule_figures.csv", subject_type="entry", subject_id=r["entry_id"], entry_id=r["entry_id"],
                  metric=r["metric"], metric_detail=r["metric_detail"], value=r["value"], unit=r["unit"],
                  value_as_published=r["value_as_published"], period_start=r["period_start"], period_end=r["period_end"],
                  basis=r["basis"], source_url=r["document_url"], source_title=r["document_title"], source_publisher=r["publisher"],
                  source_date=r["document_date"], extraction="hand_transcribed", second_read=r.get("second_read", "no"),
                  notes=r["notes"], published_text=r["quoted_line"])


TOPICS = ROOT / "sites" / "topics"


def topic_sites(sites: dict):
    """Each topic folder may list its own sites; they join the register with their kind."""
    for folder in sorted(TOPICS.glob("*")):
        f = folder / "sites.csv"
        if not f.exists():
            continue
        for r in read_csv(f):
            if r["site_id"] in sites:
                raise SystemExit(f"{f}: site id {r['site_id']} already in the register")
            sites[r["site_id"]] = {c: "" for c in SITE_COLS} | {
                "site_id": r["site_id"], "name": r["site_name"], "operator": r["operator"], "kind": r["kind"],
                "country": r["country"], "admin_region": r["state_or_region"], "locality": r["locality"],
                "lat": r["lat"], "lon": r["lon"], "register_source": f"{folder.name}: " + r["source_url"],
                "notes": r["notes"][:300]}


def topic_side(r: dict, entries: dict) -> str:
    """A company's own document is a claim. Otherwise the entry decides: a figure its text gives only as a claim
    (e.g. a deal size known from a press report of the companies' announcement) is a claim here too."""
    if r["basis"] == "company_statement":
        return "claim"
    e = entries.get(r["entry_id"]) or {}
    v = r["value_as_published"]
    if v and v in (e.get("claim") or "") and v not in (e.get("record") or ""):
        return "claim"
    return "record"


def feed_topics(T: Table, entries: dict):
    for folder in sorted(TOPICS.glob("*")):
        f = folder / "figures.csv"
        if not f.exists():
            continue
        for r in read_csv(f):
            site = r.get("subject_site_id", "")
            T.add(feed=f"sites/topics/{folder.name}/figures.csv", subject_type="site" if site else "entry",
                  subject_id=site or r["entry_id"], entry_id=r["entry_id"], metric=r["metric"], metric_detail=r["metric_detail"],
                  value=r["value"], unit=r["unit"], value_as_published=r["value_as_published"], period_start=r["period_start"],
                  period_end=r["period_end"], basis=r["basis"], side=topic_side(r, entries),
                  source_url=r["document_url"], source_title=r["document_title"], source_publisher=r["publisher"],
                  source_date=r["document_date"], extraction="hand_transcribed", second_read=r.get("second_read", "no"),
                  notes=r["notes"], published_text=r["quoted_line"])


# The 13 registrations whose later action on DEQ's list was read on 2026-10-24 (data/climate_trace_seed/VIRGINIA.md, last addendum)
VA_LATER_READ = {
    "52629": "the 2019-06-27 permit was read on 2026-10-24: same 92 units and 272 MW as the 2018 permit, with SCR on EG57-EG92 and per-unit hour and fuel limits added.",
    "71804": "the 2016-11-09 permit was read on 2026-10-24: all eight engines replaced (8 units, 8.595 MW, was 7.35 MW); permittee now Meridian Science 7990, LLC.",
    "73200": "the 2007-10-18 document read on 2026-10-24 is an amendment of opacity limits that names the same seven generators; figures from the 2006 permit as amended.",
    "73240": "DEQ's list dates an action 2024-09-24; the file it serves, read on 2026-10-24, is the permit dated 2024-09-20 already read, with the same 12 units.",
    "73370": "registration total: the 2013 permits for ACC2-ACC7 (147 units, 316.98 MW) plus the 2017-08-23 permit for ACC10 at 21744 Sir Timothy Drive (18 units, 40.5 MW), read on 2026-10-24; the site point is the ACC3 address.",
    "73643": "the 2011-10-13 document read on 2026-10-24 is a DEQ letter, not a permit; it names a governing permit of 2009-08-28 (amended 2010-04-29) that has not been read, so the figures are from the 2007 permit and may be out of date.",
    "73670": "from the renewal Title V operating permit effective 2025-03-14, read on 2026-10-24 (139 units, 274.675 MW); the 2017 construction permit listed four more units (143, 283.175 MW) and the Title V permit gives no reason for their absence.",
    "73717": "registration total: the 2009 permit (5 units, 4.275 MW) plus the 2019-05-29 permit for EG5-EG7 (3 units, 6.75 MW), read on 2026-10-24; the 2019 permit does not restate the 2009 units, so their continuing is assumed (if removed: 3 units, 6.75 MW).",
    "73977": "the 2013-08-19 document read on 2026-10-24 is an administrative amendment naming the same four generators; figures from the 2012 permit as amended.",
    "74079": "the file downloaded for the 2025-08-21 action on 2026-10-24 was the 2021 permit already read; the 2025 action has not been read and may change these figures.",
    "74156": "the permit is dated 2018-11-08 (the earlier date recorded was its application-completeness date); read again on 2026-10-24, same 24 units.",
    "74190": "the permit is dated 2020-07-16 (the earlier date recorded was the date it supersedes); read again on 2026-10-24, same 17 units.",
    "74265": "the permit is dated 2026-08-13 (the earlier date recorded was the date it supersedes); read again on 2026-10-24, same 121 units.",
}


def feed_va_permits(T: Table):
    listed = {r["registration_no"]: r for r in read_csv(PKG / "va_permits.csv")}
    for r in read_csv(PKG / "va_permits_resolved.csv"):
        reg = r["registration"]
        if reg == "5" or not r["total_standby_mw"]:
            continue
        d = iso_date(r["permit_date"])
        dates = sorted(x for x in (listed.get(reg, {}).get("permit_date_list") or "").split("; ") if x)
        later = (f" DEQ's list (retrieved 2026-10-21) shows a later action for this registration ({dates[-1]}); "
                 "the figures are from the permit dated as given, which a later permit may have changed.") if dates and d and dates[-1] > d else ""
        if reg in VA_LATER_READ:
            later = " " + VA_LATER_READ[reg][0].upper() + VA_LATER_READ[reg][1:]
        common = dict(feed="data/climate_trace_seed/va_permits_resolved.csv", subject_type="site", subject_id=f"usa-va-deq-{reg}",
                      entry_id=FEED_ENTRY["va_permits"], period_start=d, period_end=d, basis="permitted", source_url=VA_LIST_URL,
                      source_title=f"Virginia DEQ air permit, registration {reg}, dated {d or 'as read'} (opened from the link on DEQ's list of issued data-center air permits)",
                      source_publisher="Virginia Department of Environmental Quality",
                      source_date=d, extraction="pipeline_and_second_reading", second_read="yes",
                      notes=f"resolved confidence {r['resolved_confidence']}; permit date as period. DEQ serves each permit only through its list's links, "
                            "so the list is cited; the permit text was read twice (data/climate_trace_seed/VIRGINIA.md)." + later)
        T.add(metric="permitted_standby_generation", metric_detail="computed: sum of the standby generator unit ratings the permit lists",
              value=float(r["total_standby_mw"]), unit="MWe", value_as_published=r["total_standby_mw"],
              published_text=None, **(common | {"basis": "derived"}))
        if r["generator_count"]:
            T.add(metric="generator_count", metric_detail="permitted standby generator units", value=float(r["generator_count"]),
                  unit="count", value_as_published=r["generator_count"], published_text=r["generator_count"], **common)


# Texas figures whose document was read for the exact wording (independent check, 2026-10-23)
TX_DOC = {"meta-el-paso": {"value_as_published": "366-megawatt", "date": "2026-06-18",
                           "title": "City Opposes Proposed McCloud Generation CCN, Cites Deficient Analysis and Risks to Ratepayers (news release)",
                           "quoted": "The proposed $551.8 million, 366-megawatt natural gas facility"}}


def feed_tx(T: Table):
    for t in read_csv(PKG / "tx_issued_sites.csv"):
        if not t["generator_mw"]:
            continue
        urls = [u.split(" (")[0] for u in t["source_urls"].split(" ; ") if u]
        named = re.findall(r"(\d+(?:-ac\.pdf|sob\.pdf))", t["generator_basis"])
        url = next((u for u in urls for f in named[:1] if u.endswith(f)), urls[0] if urls else "")
        standby = t["air_record"] == "yes"
        pub = publisher_for(url)
        common = dict(feed="data/climate_trace_seed/tx_issued_sites.csv", subject_type="site", subject_id=f"usa-tx-{t['facility_key']}",
                      basis="permitted" if standby else "government_document", source_url=url, source_title=t["facility_name"],
                      source_publisher=pub, extraction="hand_transcribed", second_read="yes" if standby else "no",
                      notes=("" if standby else "the City of El Paso's own release (the city is a party opposing the application), describing El Paso Electric's application to the PUC; the application itself was not read, so the figure is the city's statement; ") + t["generator_basis"])
        doc = TX_DOC.get(t["facility_key"])
        if doc:
            common |= {"source_title": doc["title"], "source_date": doc["date"]}
        vap = doc["value_as_published"] if doc else t["generator_mw"]
        two = re.search(r"lists [^;]*?\(([\d.]+) MW\), so ([\d.]+) MW is the higher", t["generator_basis"])
        if standby:
            lo, hi = (float(two.group(1)), float(two.group(2))) if two else (float(t["generator_mw"]), None)
            T.add(metric="permitted_standby_generation",
                  metric_detail="computed: sum of the standby generator unit ratings in the document" + (" (its two tables give two totals)" if two else ""),
                  value=lo, value_high=hi or "", unit="MW",
                  value_as_published=(f"{units.fmt(lo)} to {units.fmt(hi)} MW (computed)" if two else f"{vap} MW (computed)"),
                  published_text=None, **(common | {"basis": "derived"}))
        else:
            T.add(metric="generation_capacity", metric_detail="utility generating plant proposed to serve the site",
                  value=float(t["generator_mw"]), unit="MW", value_as_published=vap, published_text=doc["quoted"] if doc else t["generator_mw"],
                  **(common | {"side": "claim"}))
        if t["generator_count"] and standby:
            T.add(metric="generator_count", metric_detail="standby generator units", value=float(t["generator_count"]), unit="count",
                  value_as_published=t["generator_count"], published_text=t["generator_count"], **common)


DOMAIN_PUBLISHER = [("tceq.texas.gov", "Texas Commission on Environmental Quality"), ("elpasotexas.gov", "City of El Paso"),
                    ("epa.gov", "US EPA"), ("puc.texas.gov", "Public Utility Commission of Texas"),
                    ("epa.ie", "Environmental Protection Agency (Ireland)"), ("pleanala.ie", "An Bord Pleanála"),
                    ("deq.virginia.gov", "Virginia DEQ"), ("arcgis.com", "US EPA Facility Registry Service (ArcGIS)")]


def publisher_for(url: str) -> str:
    return next((name for dom, name in DOMAIN_PUBLISHER if dom in (url or "")), "as named in the document")


def irish_metric(basis: str) -> tuple[str, str, str]:
    b = basis or ""
    if "MWth" in b or "thermal input" in b:
        return "permitted_generation_thermal_input", "MWth", "permitted"
    if "electrical output" in b:
        return "generation_capacity", "MW", "press_report"
    if "stated by applicant" in b:
        return "generation_capacity", "MW", "company_statement"
    return "permitted_generation_as_stated", "MW_unspecified", "permitted"


# Site-list figures withheld from the table because the linked document does not contain them.
WITHHELD: dict[str, str] = {}  # irl-amazon-leixlip-kic-b1-p1222 was withheld until GHG permit IE-GHG628-01 was read and linked (2026-10-24)


def feed_site_lists(T: Table):
    for r in json.load(open(ROOT / "sites" / "ireland_sites.json", encoding="utf-8")):
        if not r.get("generator_mw_permitted") or r["site_id"] in WITHHELD:
            continue
        metric, unit, basis = irish_metric(r.get("generator_mw_basis"))
        b = r.get("generator_mw_basis") or ""
        if basis == "permitted" and re.search(r"\bsum of\b|ledger's sum|\d\s*x\s*\d|\s\+\s", b):
            basis = "derived"
        lic = re.search(r"P\d{4}-\d{2}", r.get("notes") or "")
        common = dict(feed="sites/ireland_sites.json", subject_type="site", subject_id=r["site_id"], basis=basis,
                      entry_id="ie-epa-aer-metered-2025" if lic and lic.group(0) in LICENCE_SITE else "",
                      source_url=r["source_url"], source_title=f"{r['name']}: document cited in the Ireland site list",
                      source_publisher=publisher_for(r["source_url"]), extraction="hand_transcribed", second_read="no",
                      notes=b + ("; computed by the ledger as the sum of the unit ratings the document lists" if basis == "derived" else ""))
        v = str(r["generator_mw_permitted"])
        T.add(metric=metric, metric_detail="generator capacity in the licence, GHG permit or application", value=float(v), unit=unit,
              value_as_published=v, published_text=v, **common)
        if r.get("generator_count"):
            c = str(r["generator_count"])
            T.add(metric="generator_count", metric_detail="generating units named in the document", value=float(c), unit="count",
                  value_as_published=c, published_text=c, **common)
    for r in json.load(open(ROOT / "sites" / "seed_sites.json", encoding="utf-8")):
        sid = r["site_id"]
        if sid in DUPLICATES:
            continue
        if sid in SEED_GEN:
            mw, basis = SEED_GEN[sid]
            standby = "standby" in basis and "not standby" not in basis and "primary" not in basis
            src = SEED_GEN_SOURCE[sid]
            T.add(feed="sites/seed_sites.json", subject_type="site", subject_id=sid,
                  metric="permitted_standby_generation" if standby else "generation_capacity",
                  metric_detail=src.get("detail") or ("standby generators, sum of unit ratings" if standby else "on-site gas generation, primary supply (not standby)"),
                  value=mw, unit="MWe" if "MWe" in basis else "MW", value_as_published=src.get("vap") or units.fmt(mw), basis=src.get("basis", "permitted"),
                  source_url=src["url"], source_title=src["title"], source_publisher=src["publisher"], source_date=src["date"],
                  entry_id=src["entry"], extraction="hand_transcribed", second_read=src.get("second_read", "no"), notes=basis[:300],
                  published_text=None if src.get("basis") == "derived" else units.fmt(mw))
            if src.get("count"):
                T.add(feed="sites/seed_sites.json", subject_type="site", subject_id=sid, metric="generator_count",
                      metric_detail=src["count_detail"], value=float(src["count"]), unit="count", value_as_published=str(src["count"]),
                      basis="permitted", source_url=src["url"], source_title=src["title"], source_publisher=src["publisher"],
                      source_date=src["date"], entry_id=src["entry"], extraction="hand_transcribed", second_read="yes",
                      notes=src["count_note"], published_text=None)
        if r.get("capacity_mw_it"):
            v = units.fmt(r["capacity_mw_it"])
            T.add(feed="sites/seed_sites.json", subject_type="site", subject_id=sid, metric="it_capacity",
                  metric_detail=f"IT capacity as stated ({r.get('capacity_source')})", value=float(r["capacity_mw_it"]), unit="MW",
                  value_as_published=v, basis="company_statement" if r.get("capacity_source") == "operator" else "filed",
                  source_url=r["source_url"], extraction="hand_transcribed", second_read="no", notes="", published_text=v)


# ---------------------------------------------------------------- summary
def summarise(rows: list[dict], sites: list[dict]) -> dict:
    from collections import Counter, defaultdict
    by_site = defaultdict(set)
    for r in rows:
        if r["subject_type"] == "site":
            by_site[r["subject_id"]].add(r["metric"])
    cap = {"permitted_standby_generation", "permitted_generation_thermal_input", "permitted_generation_as_stated", "generation_capacity"}
    both = sorted(s for s, m in by_site.items() if m & cap and m & {"electricity_consumed"})
    cap_and_emis = sorted(s for s, m in by_site.items() if m & cap and any(x.startswith("emissions_") for x in m))
    return {
        "rows": len(rows), "sites_in_register": len(sites), "sites_with_figures": len(by_site),
        "entries_with_figures": len({r["entry_id"] for r in rows if r["entry_id"]}),
        "by_feed": dict(Counter(r["feed"].split(" (")[0] for r in rows).most_common()),
        "by_basis": dict(Counter(r["basis"] for r in rows).most_common()),
        "by_metric": dict(Counter(r["metric"] for r in rows).most_common()),
        "second_read_yes": sum(1 for r in rows if r["second_read"] == "yes"),
        "sites_with_permitted_capacity_and_metered_electricity": both,
        "sites_with_permitted_capacity_and_inventory_emissions": len(cap_and_emis),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=PKG)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    entries = {}
    for p in sorted((ROOT / "registry").glob("*.json")):
        if p.stem in ("guide", "standard", "sources"):
            continue
        for e in json.load(open(p, encoding="utf-8")):
            entries[e["id"]] = e
    site_list, sites = build_sites()
    topic_sites(sites)
    T = Table()
    feed_registry(T, entries)
    feed_aer(T)
    feed_aer_emissions(T)
    feed_nei(T, sites)
    feed_generator_hours(T, sites)
    feed_bench(T, sites)
    feed_filed(T)
    feed_paper(T)
    feed_topics(T, entries)
    feed_va_permits(T)
    feed_tx(T)
    feed_site_lists(T)
    for s in sites.values():
        if not re.fullmatch(r"[A-Z]{3}", s["country"] or ""):
            T.problems.append(f"site {s['site_id']}: country '{s['country']}' is not an ISO 3166 alpha-3 code")
    for r in T.rows:
        if r["subject_type"] == "site" and r["subject_id"] not in sites:
            T.problems.append(f"site id {r['subject_id']} not in the site register")
    if T.problems:
        for p in T.problems[:50]:
            print("PROBLEM", p)
        raise SystemExit(f"{len(T.problems)} problems")
    ids = [r["measurement_id"] for r in T.rows]
    if len(ids) != len(set(ids)):
        from collections import Counter
        raise SystemExit(f"duplicate measurement ids: {[k for k, v in Counter(ids).items() if v > 1][:5]}")
    rows = sorted(T.rows, key=lambda r: (r["feed"], r["subject_id"], r["metric"], r["period_start"], r["measurement_id"]))
    with open(a.out / "measurements.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    site_rows = sorted(sites.values(), key=lambda s: s["site_id"])
    with open(a.out / "site_register.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SITE_COLS)
        w.writeheader()
        w.writerows(site_rows)
    for old, (new, why) in RETIRED_SITE_IDS.items():
        if old in sites or new not in sites:
            raise SystemExit(f"retired site id {old}: still in the register, or its target {new} is not")
    with open(a.out / "site_id_aliases.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["retired_site_id", "site_id", "reason"])
        w.writerows([old, new, why] for old, (new, why) in sorted(RETIRED_SITE_IDS.items()))
    (a.out / "entity_register.csv").write_text((ROOT / "sites" / "entity_register.csv").read_text(encoding="utf-8"), encoding="utf-8")
    summ = summarise(rows, site_rows)
    json.dump(summ, open(a.out / "measurements_summary.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in summ.items() if k not in ("by_metric",)}, indent=1))


if __name__ == "__main__":
    main()
