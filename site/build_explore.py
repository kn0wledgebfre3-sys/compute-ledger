#!/usr/bin/env python3
"""The interactive pages and the downloads: docs/explore.html, docs/map.html and docs/data/.

- docs/explore.html: every figure in measurements.csv, searchable and filterable by country, topic, kind of figure,
  record or claim, kind of document and year. Each figure links its source, has a permanent link
  (explore.html#<measurement_id>, which follows measurement_id_aliases.csv when a figure was corrected) and a citation.
  The rows a reader filtered download as CSV with the same columns as measurements.csv.
- docs/map.html: every site with coordinates on a map (Leaflet, kept in docs/vendor/ so the page loads no script from
  another site), filterable, with the full list of sites below it and a CSV download of the filtered list.
- docs/data/figures.json and docs/data/sites.json: what the two pages read; also offered as downloads.
- docs/data/compute-ledger.xlsx: every table in data/datapackage.json on its own sheet, with a sheet describing the
  columns. Written with the standard library.

Output is deterministic (no build time). The workbook is a zip file whose compressed bytes depend on the zlib version,
so --check compares the workbook's contents part by part, and every other file byte for byte.

    python3 site/build_explore.py            # write the files
    python3 site/build_explore.py --check    # exit 1 if a committed file differs from what the build makes
"""
import argparse
import datetime as dt
import csv
import html
import io
import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_sites as bs  # noqa: E402  (labels, periods, country names and the stylesheet are shared with the site pages)

ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "data" / "climate_trace_seed"
DOCS = ROOT / "docs"
SITE_URL = bs.SITE_URL
REPO_URL = bs.REPO_URL

# Countries named in entries.csv that no site sits in yet, and the two groupings entries use.
EXTRA_COUNTRY = {"COD": "Democratic Republic of the Congo", "GHA": "Ghana", "MAR": "Morocco", "MMR": "Myanmar",
                 "RUS": "Russia", "EUU": "European Union (EU-wide)", "WLD": "Global"}

# Topics for the Explore page's filter: every metric in the vocabulary sits in one. A metric not listed falls in the last.
TOPICS = [
    ("Electricity used", ["electricity_consumed", "energy_consumed_total", "average_load", "load_factor", "pue", "electricity_sales"]),
    ("Grid connection and capacity", ["connected_capacity", "contracted_capacity", "approved_capacity", "requested_capacity",
                                      "planned_capacity", "it_capacity", "peak_demand", "forecast_demand", "electricity_share"]),
    ("Clean-energy purchases and certificates", ["certificates_used", "cfe_share", "electricity_by_sourcing_method",
                                                 "carbon_credits", "emissions_avoided"]),
    ("Greenhouse gases", ["emissions_co2", "emissions_co2e", "emissions_scope1", "emissions_scope2_location",
                          "emissions_scope2_market", "emissions_scope3"]),
    ("Generators, fuel and air pollution", ["generator_count", "generator_hours", "generator_fuel_burned", "natural_gas_burned",
                                            "permitted_standby_generation", "permitted_generation_thermal_input",
                                            "permitted_generation_as_stated", "generation_capacity", "electricity_generated",
                                            "emissions_nox", "emissions_co", "emissions_voc", "emissions_so2", "emissions_pm10",
                                            "emissions_pm25", "emissions_hap", "emissions_limit", "concentration"]),
    ("Water", ["water_withdrawn", "water_consumed", "water_allocation", "water_discharged", "water_rate"]),
    ("Money, jobs and prices", ["investment", "public_money", "jobs", "cost_to_customers", "price_or_tariff", "customer_count"]),
    ("Land, buildings and number of sites", ["land_area", "floor_area", "site_count", "distance", "noise_level"]),
    ("Minerals, fuel supply, hardware and waste", ["production_mineral", "uranium_purchased", "spent_fuel_stored",
                                                   "hardware_lifetime", "waste_generated", "waste_recycled", "heat_delivered"]),
    ("Other counts, shares and durations", []),
]
WORKBOOK_SHEETS = {  # data/datapackage.json path -> sheet name, in the order the workbook shows them
    "climate_trace_seed/measurements.csv": "Figures",
    "climate_trace_seed/site_register.csv": "Sites",
    "climate_trace_seed/entries.csv": "Entries",
    "climate_trace_seed/entry_sources.csv": "Entry sources",
    "climate_trace_seed/entity_register.csv": "Companies and bodies",
    "chain/edges.csv": "Chain links",
    "climate_trace_seed/checks.csv": "Checks",
    "climate_trace_seed/findings.csv": "Findings",
    "climate_trace_seed/measurement_id_aliases.csv": "Figure id changes",
    "climate_trace_seed/site_id_aliases.csv": "Site id changes",
    "graph/nodes.csv": "Graph nodes",
    "graph/links.csv": "Graph links",
}


def read_csv(p: Path) -> list[dict]:
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def jdump(obj) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def citation_meta() -> dict:
    cff = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    field = lambda k: (re.search(rf'^{k}:\s*"?([^"\n]*)"?\s*$', cff, re.M) or [None, ""])[1].strip()  # noqa: E731
    version, doi, released = field("version"), field("doi"), field("date-released")
    year = released[:4]
    if not year:  # before the release is dated, the year of the changelog heading for this version
        m = re.search(rf"^## {re.escape(version)} \((\d{{4}})-", (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), re.M)
        year = m.group(1) if m else "n.d."
    # changes made since the release are under '## Unreleased', each round under its date: the live data are the release plus those
    ch = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    un = ch.split("## Unreleased", 1)[1].split("\n## ", 1)[0] if "## Unreleased" in ch else ""
    m = re.search(r"^### (\d{1,2} [A-Z][a-z]+ \d{4})\s*$", un, re.M)
    since = m.group(1) if m else ""
    return {"authors": "Compute Ledger contributors", "year": year, "title": "Compute Ledger", "version": version,
            "label": f"{version}, with changes to {since}" if since else version,
            "file_tag": version + (f"-with-changes-to-{dt.datetime.strptime(since, '%d %B %Y').date().isoformat()}" if since else ""),
            "doi": doi, "site": SITE_URL, "repo": REPO_URL}


def entry_countries(text: str, names: dict) -> list[str]:
    t = text.strip()
    m = re.fullmatch(r"Multiple \((.*)\)", t)
    out = []
    for p in (m.group(1) if m else t).split(";"):
        p = p.strip()
        if p in names:
            code = names[p]
        elif p.startswith("Global"):
            code = "WLD"
        elif p in ("EU", "European Union"):
            code = "EUU"
        elif re.match(r"US[- ]", p):
            code = "USA"
        else:
            raise SystemExit(f"entries.csv: no country code for {p!r} (in {text!r}); add it to EXTRA_COUNTRY in site/build_explore.py")
        if code not in out:
            out.append(code)
    return out


def org_subjects() -> dict:
    """For each organisation with figures: its name and the subjects its page counts (site_graph's org_subjects), in the
    measurements table's own terms (site:, entity:, entry:), so Explore's ?org= shows the same figures as the page."""
    from graphdata import graph
    g = graph()
    back = {"site": "site", "org": "entity", "entry": "entry"}
    have = {(r["subject_type"], r["subject_id"]) for r in read_csv(PKG / "measurements.csv")}
    out = {}
    for nid, n in sorted(g.nodes.items()):
        if n["type"] != "org":
            continue
        subj = sorted(f"{back[x.split(':', 1)[0]]}:{x.split(':', 1)[1]}" for x in g.org_subjects(nid) if x.split(":", 1)[0] in back)
        subj = [x for x in subj if tuple(x.split(":", 1)) in have]
        if subj:
            out[nid[4:]] = [n["name"], subj]
    return out


# A site's status, as a class for the map's filter. The register's own wording stays in the status column and on the map.
STATUS = {"operating": "Operating", "permitted": "Permitted (the register's word)", "under_construction": "Under construction",
          "announced": "Announced", "refused": "Refused", "other": "Other wording, as the record gives it (for example a Texas permit's status)",
          "none": "Not stated"}
PLURAL = {"datacenter": "datacenters", "telecom_exchange": "telephone exchanges filed as datacenters",
          "mixed_building_with_datacenter": "buildings that contain a datacenter", "smelter_refiner": "smelters and refiners",
          "fab": "chip fabs", "crypto_mining": "crypto mining sites", "crypto_to_ai_conversion": "crypto mining sites moving to AI or hosting",
          "nuclear_plant": "nuclear plants"}


def words(xs, last="and"):
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + f" {last} " + xs[-1]


def status_class(s: str) -> str:
    s = s.strip()
    return "none" if not s else s if s in STATUS else "other"


def org_sites(register_ids: set) -> dict:
    """For each organisation with sites: its name and the sites its page lists (its own and its documented group's)."""
    from graphdata import graph
    g = graph()
    out = {}
    for nid, nd in sorted(g.nodes.items()):
        if nd["type"] != "org":
            continue
        ss = sorted({s[5:] for s, _, _ in g.org_sites(nid)} & register_ids)
        if ss:
            out[nid[4:]] = [nd["name"], ss]
    return out


def doc_urls() -> dict:
    from graphdata import graph
    return {n["node_id"][4:]: [n["name"], n["detail"]] for n in sorted(graph().nodes.values(), key=lambda n: n["node_id"]) if n["type"] == "doc"}


def build_data():
    vocab = json.loads((ROOT / "pipeline" / "measurement_vocab.json").read_text(encoding="utf-8"))
    countries = {**bs.COUNTRY, **EXTRA_COUNTRY}
    names = {v: k for k, v in countries.items()}
    names["European Union"] = "EUU"
    with open(PKG / "measurements.csv", newline="", encoding="utf-8") as f:
        rd = csv.reader(f)
        cols = next(rd)
        rows = list(rd)
    M = [dict(zip(cols, r)) for r in rows]
    sites = read_csv(PKG / "site_register.csv")
    entries = read_csv(PKG / "entries.csv")
    entities = read_csv(PKG / "entity_register.csv")
    for s in sites + entities:
        if s["country"] not in countries and not (s in entities and not s["country"]):
            raise SystemExit(f"{s.get('site_id') or s.get('entity_id')}: no country name for {s['country']!r}")

    topic_of = {}
    for i, (_, ms) in enumerate(TOPICS):
        for m in ms:
            topic_of[m] = i
    used_metrics = sorted({r["metric"] for r in M})
    metrics = {m: [bs.metric_label(m), topic_of.get(m, len(TOPICS) - 1), vocab["metrics"].get(m, "")] for m in used_metrics}

    site_ref = {r["subject_id"] for r in M if r["subject_type"] == "site"}
    entry_ref = {r["subject_id"] for r in M if r["subject_type"] == "entry"} | {r["entry_id"] for r in M if r["entry_id"]}
    entity_ref = {r["subject_id"] for r in M if r["subject_type"] == "entity"}
    D_sites = {s["site_id"]: [s["name"], [s["country"]]] for s in sorted(sites, key=lambda s: s["site_id"]) if s["site_id"] in site_ref}
    D_entries = {e["id"]: [e["site_or_subject"], entry_countries(e["country"], names)] for e in entries if e["id"] in entry_ref}
    D_entities = {x["entity_id"]: [x["name"], [x["country"]]] for x in sorted(entities, key=lambda x: x["entity_id"]) if x["entity_id"] in entity_ref}
    missing = (site_ref - set(D_sites)) | (entry_ref - set(D_entries)) | (entity_ref - set(D_entities))
    if missing:
        raise SystemExit(f"measurements.csv names subjects that are in no register: {sorted(missing)[:5]}")
    used_cc = {c for d in (D_sites, D_entries, D_entities) for v in d.values() for c in v[1]}
    feeds = sorted({r["feed"] for r in M if (ROOT / r["feed"]).is_file()})
    aliases = {a["retired_measurement_id"]: a["measurement_id"] for a in read_csv(PKG / "measurement_id_aliases.csv")}
    cite = citation_meta()
    figures = {
        "about": "Every figure in the Compute Ledger: the rows of data/climate_trace_seed/measurements.csv, same columns, same "
                 "order. sites, entries and entities give each subject's name and countries (ISO 3166 alpha-3; EUU is EU-wide, "
                 "WLD global); metrics give each metric's label, topic (an index into topics) and definition; aliases map a "
                 "corrected figure's retired id to its current one. Columns are described in data/DICTIONARY.md.",
        "licence": "CC BY 4.0", "cite": cite, "columns": cols, "rows": rows,
        "sites": D_sites, "entries": dict(sorted(D_entries.items())), "entities": D_entities,
        "countries": {c: countries[c] for c in sorted(used_cc)}, "topics": [t for t, _ in TOPICS], "metrics": metrics,
        "bases": {b: vocab["bases"][b] for b in sorted({r["basis"] for r in M})}, "feeds": feeds, "aliases": dict(sorted(aliases.items())),
        "orgs": org_subjects(), "docs": doc_urls(),
    }

    # sites: the register's columns, then what the ledger holds for each, in all and topic by topic
    n = defaultdict(Counter)
    bt = defaultdict(lambda: [[0, 0, 0] for _ in TOPICS])
    for r in M:
        if r["subject_type"] == "site":
            w = "calc" if r["basis"] == "derived" else r["side"]
            n[r["subject_id"]][w] += 1
            bt[r["subject_id"]][metrics[r["metric"]][1]][{"record": 0, "calc": 1, "claim": 2}[w]] += 1
    for e_ in read_csv(ROOT / "data" / "chain" / "edges.csv"):
        for side in ("from", "to"):
            if e_[f"{side}_type"] == "site":
                n[e_[f"{side}_id"]]["links"] += 1
    with open(PKG / "site_register.csv", newline="", encoding="utf-8") as f:
        rd = csv.reader(f)
        scols = next(rd)
        si = scols.index("status")
        srows = [r + [n[r[0]]["record"], n[r[0]]["calc"], n[r[0]]["claim"], n[r[0]]["links"], status_class(r[si]),
                      ";".join(f"{i}:{a}/{b}/{c}" for i, (a, b, c) in enumerate(bt[r[0]]) if a or b or c)] for r in rd]
    register_ids = {s["site_id"] for s in sites}
    sites_json = {
        "about": "Every site in the Compute Ledger: the rows of data/climate_trace_seed/site_register.csv, same columns, then "
                 "the number of figures from records, computed by the ledger from records, and claimed, the number of "
                 "documented links in the chain, the site's status as a class (statuses), and the same three counts topic by "
                 "topic (by_topic: topic index, then records/computed/claimed, for each topic with any). orgs gives, for each "
                 "organisation, its name and the sites listed under it or a company a document says belongs to its group. "
                 "Columns are described in data/DICTIONARY.md.",
        "licence": "CC BY 4.0", "cite": cite,
        "columns": scols + ["n_record_figures", "n_computed_figures", "n_claimed_figures", "n_chain_links", "status_class", "by_topic"],
        "n_register_columns": len(scols), "rows": srows,
        "countries": {c: countries[c] for c in sorted({s["country"] for s in sites})}, "kinds": bs.KIND,
        "topics": [t for t, _ in TOPICS], "statuses": STATUS, "orgs": org_sites(register_ids),
    }
    kp = Counter(s["kind"] for s in sites if s["lat"] and s["lon"])
    stats = {"placed_kinds": [PLURAL.get(k, k) for k in PLURAL if kp[k]], "unplaced_kinds": [PLURAL.get(k, k) for k in PLURAL if not kp[k] and any(s["kind"] == k for s in sites)],
             "n_figures": len(M), "n_sites": len(sites), "n_placed": sum(1 for s in sites if s["lat"] and s["lon"]),
             "n_claims": sum(1 for r in M if r["side"] == "claim")}
    return figures, sites_json, cite, stats


# ---------------------------------------------------------------------------------------------------------------- pages

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@75..100,400..800&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=IBM+Plex+Mono:wght@400;500&display=swap">\n')

PAGE_CSS = """
.getdata{font-family:var(--mono);font-size:13px;line-height:1.9;margin:14px 0 0;color:var(--ink-2)}
.filters select{font:inherit;font-size:15px;padding:7px 9px;border:1px solid var(--rule);background:var(--paper);color:var(--ink);flex:1 1 180px;max-width:100%}
.filters{align-items:center}
.chk{display:flex;align-items:center;gap:7px;font-family:var(--mono);font-size:13px;color:var(--ink-2);flex:0 0 auto}
.filters .chk input{flex:none;width:16px;height:16px;min-width:0;padding:0;margin:0;accent-color:var(--accent)}
.bar{display:flex;flex-wrap:wrap;gap:10px 14px;align-items:center;margin:16px 0 4px}
.bar .count{font-family:var(--mono);font-size:13px;color:var(--ink-2);flex:1 1 280px}
.bar .count b{color:var(--ink);font-weight:500}
.btn{font-family:var(--mono);font-size:13px;line-height:1.3;padding:7px 11px;border:1px solid var(--accent);background:var(--accent);color:var(--paper);cursor:pointer}
.btn.ghost{background:transparent;color:var(--accent)}
.btn:disabled{opacity:.45;cursor:default}
.btn:focus-visible,button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.banner{background:var(--paper-2);border-left:4px solid var(--accent);padding:10px 14px;margin:16px 0 0;max-width:820px}
.banner:empty{display:none}
p#status,#loading{font-family:var(--mono);font-size:13px;color:var(--ink-2);margin:14px 0}
.kind{display:inline-block;font-family:var(--mono);font-size:11.5px;padding:0 6px;border:1px solid currentColor;margin-bottom:2px}
.k-record{color:var(--rec)} .k-computed{color:var(--calc)} .k-claim{color:var(--claim)}
button.cite{font-family:var(--mono);font-size:12px;background:none;border:1px solid var(--rule);color:var(--accent);padding:5px 8px;cursor:pointer;white-space:nowrap}
button.cite[aria-expanded="true"]{border-color:var(--accent)}
tr.det > td{background:var(--paper-2);padding:14px 16px}
.detail .citebox{margin:0 0 6px}
.detail p.ct{font-size:15px;margin:4px 0 10px;max-width:none}
.detail dl.facts{margin-top:14px}
.more{margin:16px 0 0}
.empty{padding:18px 0;color:var(--ink-2)}
code{font-family:var(--mono);font-size:.9em}
@media (max-width:760px){
  table.fig thead{display:none}
  table.fig tr.fr{display:block;border-top:1px solid var(--rule);padding:10px 0 12px}
  table.fig tr.fr > td{display:block;border:0;padding:3px 0}
  table.fig tr.fr > td[data-l]::before{content:attr(data-l);display:block;font-family:var(--mono);font-size:11.5px;color:var(--ink-2)}
  table.fig tr.det{display:block}
  table.fig tr.det > td{display:block}
  .filters select{flex-basis:100%}
}
"""


def nav(current: str, prefix: str = "") -> str:
    links = bs.NAV
    out = []
    for href, text in links:
        cur = ' aria-current="page"' if href == current else ""
        out.append(f'<a href="{prefix}{href}"{cur}>{text}</a>')
    return (f'<nav class="top"><span><a href="{prefix}index.html">Compute Ledger</a> / {bs.e(dict(links).get(current, ""))}</span>'
            f'<span class="links">{"".join(out)}</span></nav>'
            f'<div class="gsearch" data-base="{prefix}"><input type="search" placeholder="Search sites, organisations, countries, documents" '
            'aria-label="Search the ledger" autocomplete="off"><ul role="listbox"></ul></div>')


def head(title: str, desc: str, extra: str = "", path: str = "") -> str:
    return ('<!doctype html>\n<html lang="en">\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'<title>{bs.e(title)}</title>\n<meta name="description" content="{bs.e(desc)}">\n' + bs.share_meta(title, desc, path, "") + FONTS
            + '<link rel="stylesheet" href="sites/site.css">\n<link rel="stylesheet" href="assets/graph.css">\n' + extra + f"<style>{PAGE_CSS}</style>\n<body>\n<div class=\"wrap\">\n")


def foot(path: str, name: str, about: bool = False) -> str:
    return ('<footer><p>Records are documents from regulators, courts, grid operators, statistics offices, auditors, registries or customs. '
            'Claims are what companies and governments say. Figures computed by the ledger show their formula. A gap means the ledger has not '
            'found or read a public record yet, not that none exists or that anything is wrong.</p>'
            f'<p>{bs.report_links(path, name, about)}</p>'
            f'<p>Data CC BY 4.0. <a href="{REPO_URL}#how-to-cite">Cite</a> · <a href="changes.html">What changed</a> (<a href="feed.xml">feed</a>) · '
            f'<a href="{REPO_URL}">Repository</a> · <a href="index.html">The ledger</a></p></footer>\n</div>\n<script src="assets/graph.js" defer></script>\n')


# The tables a reader can query with SQL in the browser, through Datasette Lite (lite.datasette.io, an open-source tool that
# runs in the reader's browser; it reads the CSV files from the repository and uploads nothing). Each loads as a table named
# after its file; data/datasette-metadata.json gives the tables' and columns' descriptions from data/datapackage.json.
QUERY_TABLES = ["climate_trace_seed/measurements.csv", "climate_trace_seed/site_register.csv", "climate_trace_seed/entries.csv",
                "climate_trace_seed/entry_sources.csv", "climate_trace_seed/entity_register.csv", "chain/edges.csv"]
RAW = "https://raw.githubusercontent.com/kn0wledgebfre3-sys/compute-ledger/main/data/"


def query_mb() -> str:
    return f"{sum((ROOT / 'data' / p).stat().st_size for p in QUERY_TABLES) / 1e6:.0f}"


def query_url() -> str:
    from urllib.parse import quote
    q = "&".join(f"csv={quote(RAW + p, safe='')}" for p in QUERY_TABLES)
    return f"https://lite.datasette.io/?{q}&metadata={quote(SITE_URL + 'data/datasette-metadata.json', safe='')}"


def datasette_metadata(cite: dict) -> dict:
    pkg = json.loads((ROOT / "data" / "datapackage.json").read_text(encoding="utf-8"))
    res = {r["path"]: r for r in pkg["resources"]}
    tables = {}
    for p in QUERY_TABLES:
        r = res[p]
        tables[Path(p).stem] = {"description": r["description"], "columns": {fl["name"]: fl["description"] for fl in r["schema"]["fields"]}}
    return {"title": f"Compute Ledger, version {cite['label']} (the latest tables)",
            "description": "Public records on the footprint of AI compute, with what companies and governments say kept apart (the column side). "
                           "Start with the table measurements.",
            "license": "CC BY 4.0", "license_url": "https://creativecommons.org/licenses/by/4.0/",
            "source": "Compute Ledger", "source_url": cite["repo"], "databases": {"data": {"tables": tables}}}


def get_data_line(cite: dict) -> str:
    v = bs.e(cite["label"])
    return (f'<p class="getdata" id="get-the-data">Get the data (version {v}): '
            '<a href="data/compute-ledger.xlsx" download>Excel workbook, every table</a>&#160;· '
            '<a href="data/figures.json">Figures as JSON</a>&#160;· <a href="data/sites.json">Sites as JSON</a>&#160;· '
            f'<a href="{REPO_URL}#get-the-data">Every table as CSV</a>&#160;· '
            f'<a href="{bs.e(query_url())}" rel="noopener">Query the six main tables with SQL in your browser</a> '
            f'<span class="m">(Datasette Lite, another site; it loads the latest tables, about {query_mb()} MB, into your browser and uploads nothing)</span>&#160;· '
            f'<a href="{REPO_URL}/blob/main/data/DICTIONARY.md">What each column means</a>&#160;· '
            f'<a href="{REPO_URL}#how-to-cite">How to cite</a></p>')


EXPLORE_JS = r"""
(()=>{'use strict';
const $=id=>document.getElementById(id);
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const href=u=>/^https?:\/\//i.test(u||'')?u:'';
const fmt=n=>n.toLocaleString('en-GB');
const PAGE=100, UNIT={pct:'%',m3:'m³',short_ton:'short tons',count:''};
const WHAT={record:'Record',computed:'Computed',claim:'Claim'};
const KEYS=['country','topic','metric','what','basis','year'];
let D,R=[],ids=new Set(),view=[],shown=PAGE,single=null;
function asPub(r){let v=r.value_as_published;if(/^-?\d+(\.\d+)?[eE][-+]?\d+$/.test(v||''))v=String(Number(v));if(/^[\d.,\s~<>≈-]+$/.test(v||'')){const u=(r.unit in UNIT)?UNIT[r.unit]:r.unit.replace(/_/g,' ');return (v+' '+u).trim();}return v;}
function period(r){const s=r.period_start,t=r.period_end;
  if(s&&t&&s.slice(5)==='01-01'&&t.slice(5)==='12-31'&&s.slice(0,4)===t.slice(0,4))return s.slice(0,4);
  if(s&&t&&s.slice(0,7)===s.slice(0,4)+'-07'&&t.slice(5)==='06-30'&&+t.slice(0,4)===+s.slice(0,4)+1)return 'FY to '+t;
  if(s&&t)return s+' to '+t;return s||t||'not stated';}
function cite(r){const c=D.cite,p=period(r);
  return c.authors+' ('+c.year+'). '+c.title+', version '+c.label+(c.doi?', https://doi.org/'+c.doi:'')+'. Figure '+r.measurement_id+': '
    +r._label+(r.metric_detail?' ('+r.metric_detail+')':'')+', '+r._name+': '+asPub(r)+(p!=='not stated'?', '+p:'')+'. '
    +c.site+'explore.html#'+r.measurement_id+'. Original source: '+[r.source_publisher,r.source_title?'“'+r.source_title+'”':'',r.source_date].filter(Boolean).join(', ')
    +(href(r.source_url)?', '+r.source_url:'')+'.';}
function state(){const s={};for(const k of KEYS)s[k]=$(k).value;s.q=$('q').value.trim();s.qw=s.q.toLowerCase().split(/\s+/).filter(Boolean);
  s.twice=$('twice').checked;s.sort=$('sort').value;s.subject=subject;s.org=org;s.doc=doc;return s;}
let subject='',org='',doc='',orgSet=null,bnote='';
function match(r,s,skip){
  if(s.subject&&r.subject_id!==s.subject&&r.entry_id!==s.subject)return false;
  if(s.org&&!(orgSet&&orgSet.has(r.subject_type+':'+r.subject_id)))return false;
  if(s.doc&&!(D.docs[s.doc]&&r.source_url===D.docs[s.doc][1]))return false;
  if(skip!=='country'&&s.country&&!r._cc.includes(s.country))return false;
  if(skip!=='topic'&&s.topic&&r._topic!==s.topic)return false;
  if(skip!=='metric'&&s.metric&&r.metric!==s.metric)return false;
  if(skip!=='what'&&s.what&&r._what!==s.what)return false;
  if(skip!=='basis'&&s.basis&&r.basis!==s.basis)return false;
  if(skip!=='year'&&s.year&&(r._year||'none')!==s.year)return false;
  if(s.twice&&r.second_read!=='yes')return false;
  for(const w of s.qw)if(!r._text.includes(w))return false;
  return true;}
function facetVals(r,k){return k==='country'?r._cc:[k==='topic'?r._topic:k==='metric'?r.metric:k==='what'?r._what:k==='basis'?r.basis:(r._year||'none')];}
function facets(s){for(const k of KEYS){const cnt=new Map();let tot=0;
  for(const r of R){if(!match(r,s,k))continue;tot++;for(const v of facetVals(r,k))cnt.set(v,(cnt.get(v)||0)+1);}
  const sel=$(k);for(const o of sel.options){const n=o.value?(cnt.get(o.value)||0):tot;o.textContent=o.dataset.t+' ('+fmt(n)+')';o.disabled=!!o.value&&n===0&&sel.value!==o.value;}}}
function sortView(how){const k=how==='recent'?(r=>(r._year?String(9999-+r._year):'9999')+'\u0001'+r._pk):how==='published'?(r=>(r.source_date?String(99999999-+(r.source_date+'-00-00').slice(0,10).replace(/-/g,'')).padStart(8,'0'):'99999999')+'\u0001'+r._pk):(r=>r._pk);
  const keyed=view.map(r=>[k(r),r]);keyed.sort((a,b)=>a[0]<b[0]?-1:a[0]>b[0]?1:0);view=keyed.map(x=>x[1]);}
function row(r){const id=esc(r.measurement_id),u=href(r.source_url),open=single===r.measurement_id;
  const src=u?'<a href="'+esc(u)+'" rel="noopener">'+esc(r.source_title||u)+'</a>':esc(r.source_title);
  const pub=[r.source_publisher,r.source_date].filter(Boolean).map(esc).join(' · ');
  const where=r._page?'<a href="'+esc(r._page)+'">'+esc(r._name)+'</a>':esc(r._name);
  const qual=r.qualifier&&r.qualifier!=='exact'?'<div class="m">'+esc(r.qualifier.replace(/_/g,' '))+'</div>':'';
  return '<tr class="fr" id="'+id+'"><td data-l="Where">'+where+'<div class="m">'+esc(r._ctry)+'</div></td>'
   +'<td data-l="Figure"><strong>'+esc(r._label)+'</strong><div class="m">'+esc(r.metric_detail)+'</div></td>'
   +'<td data-l="As published" class="v">'+esc(asPub(r))+qual+'<div class="m">'+esc(period(r))+'</div></td>'
   +'<td data-l="What it is"><span class="kind k-'+r._what+'">'+WHAT[r._what]+'</span><div class="m" title="'+esc(D.bases[r.basis]||'')+'">'+esc(r.basis.replace(/_/g,' '))+'</div></td>'
   +'<td data-l="Source">'+src+'<div class="m">'+pub+'</div></td>'
   +'<td><button type="button" class="cite" data-id="'+id+'" aria-expanded="'+open+'" aria-controls="d-'+id+'">Cite · details</button></td></tr>'
   +'<tr class="det" id="d-'+id+'"'+(open?'':' hidden')+'><td colspan="6">'+(open?detail(r):'')+'</td></tr>';}
function detail(r){const id=r.measurement_id,c=D.cite,link=c.site+'explore.html#'+id;
  const cu=(r.canonical_unit in UNIT)?UNIT[r.canonical_unit]:r.canonical_unit.replace(/_/g,' ');
  const canon=r.value_canonical?(r.value_canonical+(r.value_high_canonical?' to '+r.value_high_canonical:'')+' '+cu).trim():'';
  const ent=r.entry_id&&r.subject_type!=='entry'&&D.entries[r.entry_id]?'<dt>Ledger entry</dt><dd><a href="index.html#'+esc(r.entry_id)+'">'+esc(D.entries[r.entry_id][0])+'</a></dd>':'';
  const held=D.feeds.includes(r.feed)?'<a href="'+esc(c.repo+'/blob/main/'+r.feed)+'">'+esc(r.feed)+'</a>':esc(r.feed);
  const issue=c.repo+'/issues/new?template=correction.yml&title='+encodeURIComponent('Correction: '+id+' ('+r._label+', '+r._name+')')+'&figure='+encodeURIComponent(id);
  return '<div class="detail"><div class="citebox"><div class="m">Cite this figure</div><p class="ct" id="ct-'+esc(id)+'">'+esc(cite(r))+'</p>'
   +'<button type="button" class="btn" data-copy="ct-'+esc(id)+'">Copy citation</button> <button type="button" class="btn ghost" data-copytext="'+esc(link)+'">Copy link to this figure</button></div>'
   +'<dl class="facts"><dt>Figure id</dt><dd><code>'+esc(id)+'</code></dd>'
   +(canon?'<dt>In the ledger’s standard unit</dt><dd>'+esc(canon)+'</dd>':'')
   +'<dt>Kind of document</dt><dd>'+esc(r.basis.replace(/_/g,' '))+': '+esc(D.bases[r.basis]||'')+'</dd>'
   +'<dt>Reading</dt><dd>'+(r.second_read==='yes'?'Read a second time, independently':'Read once')+'; '+esc(r.extraction.replace(/_/g,' '))+'</dd>'
   +(r.notes?'<dt>Notes</dt><dd>'+esc(r.notes)+'</dd>':'')+ent
   +'<dt>Held in</dt><dd>'+held+' <span class="m">(the file a correction changes)</span></dd></dl>'
   +'<p class="m" style="margin-top:12px"><a href="'+esc(issue)+'" rel="noopener">Report an error in this figure</a>: the form asks for the document and the page that show it.</p></div>';}
function render(reset){const s=state();if(reset)shown=PAGE;
  view=single?R.filter(r=>r.measurement_id===single):R.filter(r=>match(r,s,''));sortView(s.sort);
  const n={record:0,computed:0,claim:0};for(const r of view)n[r._what]++;
  $('count').innerHTML='<b>'+fmt(view.length)+'</b> of '+fmt(R.length)+' figures · '+fmt(n.record)+' from records · '+fmt(n.computed)+' computed · '+fmt(n.claim)+' claims';
  $('rows').innerHTML=view.slice(0,shown).map(row).join('');
  $('empty').hidden=view.length>0;
  const left=view.length-shown;$('more').hidden=left<=0;if(left>0)$('more').textContent='Show '+fmt(Math.min(PAGE,left))+' more ('+fmt(left)+' not shown yet)';
  $('dl').disabled=!view.length;$('dl').textContent=view.length===1?'Download this row (CSV)':'Download these '+fmt(view.length)+' rows (CSV)';
  if(!single)facets(s);}
function sync(){const p=new URLSearchParams();const s=state();for(const k of KEYS)if(s[k])p.set(k,s[k]);if(s.q)p.set('q',s.q);if(s.twice)p.set('twice','1');
  if(s.sort!=='place')p.set('sort',s.sort);if(subject)p.set('subject',subject);if(org)p.set('org',org);if(doc)p.set('doc',doc);const q=p.toString();history.replaceState(null,'',location.pathname+(q?'?'+q:''));}
function setBanner(){let h=bnote;if(single)h='Showing one figure.'+bnote+' <a href="explore.html">Show every figure</a>';
  else if(subject){const nm=(D.sites[subject]||D.entries[subject]||D.entities[subject]||[subject])[0];h=(bnote?bnote+' ':'')+'Showing the figures for <b>'+esc(nm)+'</b>. <a href="#" id="unsubject">Show every figure</a>';}
  else if(org){const o=D.orgs[org];h=(bnote?bnote+' ':'')+'Showing the figures for <b>'+esc(o?o[0]:org)+'</b>, its sites and the entries about it alone (<a href="org/'+esc(encodeURIComponent(org))+'.html">its page</a>). <a href="#" id="unsubject">Show every figure</a>';}
  else if(doc){const d=D.docs[doc];h=(bnote?bnote+' ':'')+'Showing the figures read from <b>'+esc(d?d[0]:doc)+'</b> (<a href="doc/'+esc(encodeURIComponent(doc))+'.html">its page</a>). <a href="#" id="unsubject">Show every figure</a>';}
  $('banner').innerHTML=h;}
function changed(){if(single||bnote){single=null;bnote='';}setBanner();sync();render(true);}
function readUrl(){const p=new URLSearchParams(location.search);
  for(const k of KEYS){const v=p.get(k)||'';if(v&&![...$(k).options].some(o=>o.value===v))continue;$(k).value=v;}
  $('q').value=p.get('q')||'';$('twice').checked=p.get('twice')==='1';$('sort').value=['recent','published'].includes(p.get('sort'))?p.get('sort'):'place';
  subject=p.get('subject')||'';org=D.orgs[p.get('org')]?p.get('org'):'';doc=D.docs[p.get('doc')]?p.get('doc'):'';orgSet=org?new Set(D.orgs[org][1]):null;
  const h=decodeURIComponent(location.hash.slice(1));single=null;bnote='';
  if(/^m-[0-9a-f]{10}$/.test(h)){let id=h;if(!ids.has(id)&&D.aliases[id]){id=D.aliases[id];bnote=' It was corrected: its earlier id '+esc(h)+' now points to '+esc(id)+'.';}
    if(ids.has(id))single=id;else bnote='No figure has the id '+esc(h)+'.';}
  setBanner();}
function csvCell(v){v=v==null?'':String(v);return /[",\r\n]/.test(v)?'"'+v.replace(/"/g,'""')+'"':v;}
function download(){const C=D.columns,lines=[C.map(csvCell).join(',')];for(const r of view)lines.push(C.map(c=>csvCell(r[c])).join(','));
  const b=new Blob([lines.join('\r\n')+'\r\n'],{type:'text/csv;charset=utf-8'}),a=document.createElement('a');
  a.href=URL.createObjectURL(b);a.download='compute-ledger-'+D.cite.file_tag+'-figures'+(view.length<R.length?'-selected':'')+'.csv';
  document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove();},0);}
async function copy(text,btn){try{await navigator.clipboard.writeText(text);}catch(e){const t=document.createElement('textarea');t.value=text;t.style.position='fixed';t.style.opacity='0';document.body.appendChild(t);t.select();try{document.execCommand('copy');}catch(_){}t.remove();}
  const o=btn.textContent;btn.textContent='Copied';setTimeout(()=>{btn.textContent=o;},1600);}
function opt(sel,v,t){const o=document.createElement('option');o.value=v;o.dataset.t=t;o.textContent=t;sel.appendChild(o);return o;}
function init(data){D=data;const C=D.columns;
  R=D.rows.map(a=>{const r={};C.forEach((c,i)=>{r[c]=a[i];});const t=r.subject_type;
    const s=(t==='site'?D.sites:t==='entry'?D.entries:D.entities)[r.subject_id]||[r.subject_id,[]];
    r._name=s[0];r._cc=s[1];r._ctry=r._cc.map(c=>D.countries[c]||c).join(', ');
    r._page=t==='site'?'sites/'+encodeURIComponent(r.subject_id)+'.html':t==='entry'?'index.html#'+encodeURIComponent(r.subject_id):'';
    r._what=r.basis==='derived'?'computed':r.side;r._year=(r.period_end||r.period_start).slice(0,4);
    const m=D.metrics[r.metric]||[r.metric,D.topics.length-1,''];r._label=m[0];r._topic=String(m[1]);
    r._pk=[(r._ctry||'~').toLowerCase(),r._name.toLowerCase(),String(m[1]).padStart(2,'0'),r._label.toLowerCase(),r._year?String(9999-+r._year):'9999',r.measurement_id].join('\u0001');
    r._text=[r._name,r.subject_id,r._label,r.metric,r.metric_detail,r.value_as_published,r.source_title,r.source_publisher,r.notes,r.measurement_id,r._ctry,r.entry_id].join(' ').toLowerCase();
    ids.add(r.measurement_id);return r;});
  const cc=new Set();R.forEach(r=>r._cc.forEach(c=>cc.add(c)));
  [...cc].sort((a,b)=>(D.countries[a]||a).localeCompare(D.countries[b]||b)).forEach(c=>opt($('country'),c,D.countries[c]||c));
  D.topics.forEach((t,i)=>opt($('topic'),String(i),t));
  D.topics.forEach((t,i)=>{const g=document.createElement('optgroup');g.label=t;
    Object.keys(D.metrics).filter(m=>D.metrics[m][1]===i).sort((a,b)=>D.metrics[a][0].localeCompare(D.metrics[b][0])).forEach(m=>opt(g,m,D.metrics[m][0]).title=D.metrics[m][2]);
    if(g.children.length)$('metric').appendChild(g);});
  Object.keys(D.bases).sort().forEach(b=>opt($('basis'),b,b.replace(/_/g,' ')).title=D.bases[b]);
  [...new Set(R.map(r=>r._year).filter(Boolean))].sort().reverse().forEach(y=>opt($('year'),y,y));opt($('year'),'none','Year not stated');
  for(const sel of document.querySelectorAll('#filters select'))for(const o of sel.options)if(!o.dataset.t)o.dataset.t=o.textContent;
  readUrl();
  for(const k of KEYS)$(k).addEventListener('change',changed);
  $('sort').addEventListener('change',()=>{sync();render(true);});
  let tm;$('q').addEventListener('input',()=>{clearTimeout(tm);tm=setTimeout(changed,180);});
  $('twice').addEventListener('change',changed);
  $('clear').addEventListener('click',()=>{for(const k of KEYS)$(k).value='';$('q').value='';$('twice').checked=false;subject='';org='';doc='';orgSet=null;changed();});
  $('banner').addEventListener('click',e=>{if(e.target.id==='unsubject'){e.preventDefault();subject='';org='';doc='';orgSet=null;changed();}});
  $('more').addEventListener('click',()=>{shown+=PAGE;render(false);});
  $('dl').addEventListener('click',download);
  $('share').addEventListener('click',e=>copy(location.href,e.currentTarget));
  $('rows').addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;
    if(b.classList.contains('cite')){const id=b.dataset.id,tr=$('d-'+id),open=b.getAttribute('aria-expanded')!=='true';
      if(open&&!tr.firstChild.innerHTML)tr.firstChild.innerHTML=detail(R.find(r=>r.measurement_id===id));tr.hidden=!open;b.setAttribute('aria-expanded',String(open));}
    else if(b.dataset.copy)copy($(b.dataset.copy).textContent,b);else if(b.dataset.copytext)copy(b.dataset.copytext,b);});
  window.addEventListener('hashchange',()=>{readUrl();render(true);$('banner').scrollIntoView({block:single?'start':'nearest'});});
  $('status').hidden=true;$('app').hidden=false;render(true);
  if(single)setTimeout(()=>$('banner').scrollIntoView({block:'start'}),0);}
fetch('data/figures.json').then(r=>{if(!r.ok)throw new Error('HTTP '+r.status);return r.json();}).then(init)
  .catch(e=>{$('status').textContent='The figures could not be loaded ('+e.message+'). The same figures are in the Excel workbook and in measurements.csv, linked above.';});
})();
"""


def explore_page(cite: dict, stats: dict) -> str:
    body = [nav("explore.html"),
            f'<p class="eyebrow">Compute Ledger · version {bs.e(cite["label"])}</p><h1>Explore every figure</h1>',
            f'<p class="lede">Every figure the ledger holds, {stats["n_figures"]:,} of them, one row each, as the document printed it and with '
            'its source. <b>Records</b> are documents from regulators, courts, grid operators, statistics offices, auditors, registries or customs. '
            '<b>Claims</b> are what companies and governments say. <b>Computed</b> figures are the ledger’s own arithmetic on records, with the formula '
            'in the details. Filter, then download the rows you chose, or open a figure’s details to cite it or report an error.</p>',
            get_data_line(cite),
            '<div class="banner" id="banner" role="status"></div>',
            f'<p id="status">Loading {stats["n_figures"]:,} figures…</p>',
            '<noscript><p>This page needs JavaScript to filter the figures. The same figures are in the '
            '<a href="data/compute-ledger.xlsx">Excel workbook</a> and in <a href="data/figures.json">figures.json</a>.</p></noscript>',
            '<div id="app" hidden>',
            '<div class="filters" id="filters">',
            '<input id="q" type="search" placeholder="Search a site, company, place, document or figure id" aria-label="Search the figures">',
            '<select id="country" aria-label="Country"><option value="">Every country</option></select>',
            '<select id="topic" aria-label="Topic"><option value="">Every topic</option></select>',
            '<select id="metric" aria-label="Kind of figure"><option value="">Every kind of figure</option></select>',
            '<select id="what" aria-label="Record, computed or claim"><option value="">Records, computed and claims</option>'
            '<option value="record">Records only</option><option value="computed">Computed by the ledger</option><option value="claim">Claims only</option></select>',
            '<select id="basis" aria-label="Kind of document"><option value="">Every kind of document</option></select>',
            '<select id="year" aria-label="Year the figure covers"><option value="">Any year</option></select>',
            '<select id="sort" aria-label="Order"><option value="place">Order: by country and site</option>'
            '<option value="recent">Order: most recent period first</option><option value="published">Order: most recent document first</option></select>',
            '<label class="chk"><input type="checkbox" id="twice"> Only figures read twice</label>',
            '<button class="btn ghost" id="clear" type="button">Clear</button>',
            '</div>',
            '<div class="bar"><span class="count" id="count" aria-live="polite"></span>'
            '<button class="btn" id="dl" type="button">Download these rows (CSV)</button>'
            '<button class="btn ghost" id="share" type="button">Copy link to this view</button></div>',
            '<div class="tw"><table class="fig"><thead><tr><th>Where</th><th>Figure</th><th>As published</th><th>What it is</th><th>Source</th>'
            '<th><span class="m">Cite</span></th></tr></thead><tbody id="rows"></tbody></table></div>',
            '<p class="empty" id="empty" hidden>No figure matches. Clear a filter, or search for fewer words.</p>',
            '<p class="more"><button class="btn ghost" id="more" type="button" hidden>Show more</button></p>',
            '<p class="m" style="margin-top:18px">The download has the columns of <code>measurements.csv</code>, described in '
            f'<a href="{REPO_URL}/blob/main/data/DICTIONARY.md">the data dictionary</a>. A figure corrected after you cite it keeps its old link: '
            'the page sends it to the corrected figure.</p>',
            '</div>',
            foot("explore.html", "Explore"), f"<script>{EXPLORE_JS}</script>\n</body>\n</html>\n"]
    return head("Explore every figure · Compute Ledger",
                "Search, filter, download and cite every figure in the Compute Ledger, each with its public source.", path="explore.html") + "\n".join(body)


MAP_CSS = """
:root{--mk-rec:#00806A;--mk-claim:#C2491A;--mk-none:#4B5955}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){--mk-rec:#1E9A84;--mk-claim:#D45A28;--mk-none:#A3B0AB} }
:root[data-theme="dark"]{--mk-rec:#1E9A84;--mk-claim:#D45A28;--mk-none:#A3B0AB}
#map{height:min(64vh,640px);min-height:360px;margin:12px 0 0;border:1px solid var(--rule);background:var(--paper-2)}
.leaflet-container{font-family:var(--body);font-size:15px;background:var(--paper-2)}
.leaflet-popup-content-wrapper,.leaflet-popup-tip{background:var(--paper);color:var(--ink);border-radius:2px;box-shadow:0 2px 10px rgba(0,0,0,.25)}
.leaflet-popup-content{margin:12px 14px;line-height:1.45}
.leaflet-popup-content b{font-family:var(--display);font-size:16px}
.leaflet-container a.leaflet-popup-close-button{color:var(--ink-2)}
.leaflet-tooltip{background:var(--paper);color:var(--ink);border:1px solid var(--rule);font-family:var(--mono);font-size:12px;box-shadow:none}
.leaflet-control-attribution{font-family:var(--mono);font-size:10.5px}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]) .leaflet-tile-pane{filter:invert(1) hue-rotate(180deg) brightness(.9) contrast(.9) saturate(.5)}
  :root:not([data-theme="light"]) .leaflet-control-attribution{background:rgba(18,24,22,.8);color:var(--ink-2)} }
:root[data-theme="dark"] .leaflet-tile-pane{filter:invert(1) hue-rotate(180deg) brightness(.9) contrast(.9) saturate(.5)}
.legend{display:flex;flex-wrap:wrap;gap:6px 22px;font-family:var(--mono);font-size:12.5px;color:var(--ink-2);margin:10px 0 0;padding:0;list-style:none}
.legend li{display:flex;align-items:center;gap:7px}
.legend svg{flex:none}
.legend b{color:var(--ink);font-weight:500}
td.n{font-variant-numeric:tabular-nums;font-family:var(--mono);font-size:13.5px}
button.show{font-family:var(--mono);font-size:12px;background:none;border:1px solid var(--rule);color:var(--accent);padding:4px 8px;cursor:pointer;white-space:nowrap}
.leaflet-popup-content ul.bt{list-style:none;padding:0;margin:8px 0 0;font-size:13.5px}
.leaflet-popup-content ul.bt li{margin:0 0 3px}
.leaflet-container a{color:var(--accent)}
.leaflet-bar a,.leaflet-bar a:hover{background:var(--paper);color:var(--ink);border-bottom-color:var(--rule)}
.skip{position:absolute;left:-9999px}.skip:focus{position:static;display:inline-block;margin:10px 0 0;font-family:var(--mono);font-size:13px}
#mapwrap{position:relative}
#mapnote{position:absolute;left:12px;right:12px;bottom:12px;z-index:500;background:var(--paper);border:1px solid var(--rule);padding:10px 12px;font-family:var(--mono);font-size:13px;color:var(--ink-2)}
@media (max-width:760px){
  table.sites thead{display:none}
  table.sites,table.sites tbody,table.sites tr,table.sites td{display:block;width:auto}
  table.sites tr{border-top:1px solid var(--rule);padding:10px 0}
  table.sites td{border:0;padding:2px 0}
  table.sites th:nth-child(3),table.sites td:nth-child(3){display:block}
  button.show{min-height:40px;padding:8px 12px;margin-top:4px}
  .leaflet-popup-content{max-width:calc(100vw - 110px)}
}
"""

MAP_JS = r"""
(()=>{'use strict';
const $=id=>document.getElementById(id);
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=n=>n.toLocaleString('en-GB');
const PAGE=100, KEYS=['topic','holds','kind','status','country','org'];
const HOLD={rec:'Records found',claim:'Claims only',none:'No figures yet'};
let D,S=[],view=[],shown=PAGE,map=null,layer=null,first=true,lastTopic=null,orgSet=null,badSite='',badKnown=null,opener=null;
function css(v){return getComputedStyle(document.documentElement).getPropertyValue(v).trim();}
function topic(){return $('topic').value;}
function holdOf(s,t){if(t==='')return s._hold;const v=s._bt[t];return !v?'none':(v[0]+v[1])>0?'rec':v[2]>0?'claim':'none';}
function style(s){const paper=css('--paper'),h=holdOf(s,topic());
  if(h==='none')return {radius:5,weight:2,color:css('--mk-none'),fillColor:paper,fillOpacity:.85,opacity:1};
  return {radius:h==='rec'?6.5:6,weight:1.5,color:paper,fillColor:css(h==='rec'?'--mk-rec':'--mk-claim'),fillOpacity:1,opacity:1};}
function where(s){return [s.locality,s.admin_region,s._country].filter(Boolean).join(', ');}
function plural(n,w){return fmt(n)+' '+w+(n===1?'':'s');}
function counts3(a,b,c,links){const p=[];if(a)p.push(fmt(a)+' from records');if(b)p.push(fmt(b)+' computed');if(c)p.push(fmt(c)+' claimed');
  if(links)p.push(plural(links,'chain link'));return p.join(' · ');}
function counts(s,t){if(t!==''){const v=s._bt[t];return v?counts3(v[0],v[1],v[2],0):'No figures on this topic yet';}
  return counts3(+s.n_record_figures,+s.n_computed_figures,+s.n_claimed_figures,+s.n_chain_links)||'No figures yet';}
function status(s){return s.status_class==='other'?s.status.replace(/^[:\s]+/,''):D.statuses[s.status_class];}
function holdCell(s,t){const h=holdOf(s,t);if(t!==''&&h==='none')return esc('No figures on '+D.topics[+t].toLowerCase()+' yet');
  return esc(HOLD[h]+(t===''?'':' ('+D.topics[+t]+')'))+'<div>'+esc(counts(s,t))+'</div>';}
function approx(s){const d=x=>(String(x).split('.')[1]||'').length,n=Math.min(d(s.lat),d(s.lon));
  if(/to the nearest 100 m/.test(s.notes||''))return 'the nearest 100 m';  // a grid reference printed to 100 m, converted
  return n<=1?'about 10 km':n===2?'about 1 km':'';}
function popup(s){const id=encodeURIComponent(s.site_id);
  const bt=Object.keys(s._bt).map(Number).sort((a,b)=>a-b).map(i=>{const v=s._bt[i];
    return '<li><a href="explore.html?subject='+id+'&amp;topic='+i+'">'+esc(D.topics[i])+'</a>: '+esc(counts3(v[0],v[1],v[2],0))+'</li>';}).join('');
  return '<b>'+esc(s.name)+'</b><div class="m">'+esc(s._kind)+(s.status_class!=='none'?' · '+esc(status(s)):'')+'</div><div>'+esc(where(s))+'</div>'
   +(s.operator?'<div class="m">Operator: '+esc(s.operator)+'</div>':'')+(s._ll&&approx(s)?'<div class="m">Approximate position: the document gives it to '+approx(s)+'.</div>':'')
   +(bt?'<ul class="bt">'+bt+'</ul>':'<div class="m" style="margin-top:6px">No figures yet</div>')
   +(+s.n_chain_links?'<div class="m">'+esc(plural(+s.n_chain_links,'chain link'))+'</div>':'')
   +'<div style="margin-top:8px"><a href="sites/'+id+'.html">Open the site page</a>'+(s._n?' · <a href="explore.html?subject='+id+'">All its figures</a>':'')+'</div>';}
function state(){const s={};for(const k of KEYS)s[k]=$(k).value;s.q=$('q').value.trim();s.qw=s.q.toLowerCase().split(/\s+/).filter(Boolean);s.placed=$('placed').checked;return s;}
function match(s,st){if(st.kind&&s.kind!==st.kind)return false;if(st.country&&s.country!==st.country)return false;if(st.status&&s.status_class!==st.status)return false;
  if(st.org&&!(orgSet&&orgSet.has(s.site_id)))return false;if(st.holds&&holdOf(s,st.topic)!==st.holds)return false;
  if(st.placed&&!s._ll)return false;for(const w of st.qw)if(!s._text.includes(w))return false;return true;}
function legend(t){const tl=t===''?'':D.topics[+t].toLowerCase();
  $('l-rec').textContent=t===''?'at least one figure from a record, or computed by the ledger from records':'at least one figure on '+tl+' from a record, or computed from records';
  $('l-claim').textContent=t===''?'only what the company or a government says':'only claims on '+tl;
  $('l-none').textContent=t===''?'listed from a register or a list of sites, no figure read yet':'no figure on '+tl+' yet';}
function render(reset,fit){const st=state();if(reset)shown=PAGE;orgSet=st.org&&D.orgs[st.org]?new Set(D.orgs[st.org][1]):null;
  if(st.topic!==lastTopic){lastTopic=st.topic;legend(st.topic);if(map)restyle();}
  view=S.filter(s=>match(s,st));
  const placed=view.filter(s=>s._ll),n={rec:0,claim:0,none:0};placed.forEach(s=>n[holdOf(s,st.topic)]++);
  $('count').innerHTML='<b>'+fmt(view.length)+'</b> of '+fmt(S.length)+' sites · '+fmt(placed.length)+' on the map';
  for(const k in n)$('n-'+k).textContent=fmt(n[k]);
  $('mapnote').hidden=!(map&&view.length&&!placed.length);if(!$('mapnote').hidden)$('mapnote').textContent=(view.length===1?'This site is not placed yet: no document read gives its location. It is listed below.':'None of these '+fmt(view.length)+' sites is placed yet: no document read gives their location. They are listed below.');
  if(layer){layer.clearLayers();for(const h of ['none','claim','rec'])for(const s of placed)if(holdOf(s,st.topic)===h)layer.addLayer(s._mk);
    for(const s of placed){const el=s._mk.getElement&&s._mk.getElement();if(el){el.setAttribute('tabindex','-1');el.removeAttribute('role');}}
    if(fit&&placed.length){const b=L.latLngBounds(placed.map(s=>s._ll));map.fitBounds(b.pad(0.08),{maxZoom:10,animate:!first});first=false;}}
  $('banner').innerHTML=badSite?(badKnown?'<b>'+esc(badKnown.name)+'</b> is not placed yet: no document read gives its location. <a href="sites/'+esc(encodeURIComponent(badKnown.site_id))+'.html">Its page</a> · ':'No site has the id '+esc(badSite)+'. ')+'<a href="#" id="unbad">Close</a>':orgSet?'Showing the sites of <b>'+esc(D.orgs[st.org][0])+'</b> and of the companies a document says belong to its group (<a href="org/'+esc(encodeURIComponent(st.org))+'.html">its page</a>). <a href="#" id="unorg">Show every site</a>':'';
  $('rows').innerHTML=view.slice(0,shown).map(s=>'<tr><td><a href="sites/'+encodeURIComponent(s.site_id)+'.html">'+esc(s.name)+'</a><div class="m">'+esc(s.operator)+'</div></td>'
    +'<td class="m">'+esc(s._kind)+(s.status_class!=='none'?'<div>'+esc(status(s))+'</div>':'')+'</td><td>'+esc(where(s))+'</td>'
    +'<td class="m">'+holdCell(s,st.topic)+'</td>'
    +'<td>'+(s._ll&&map?'<button type="button" class="show" data-id="'+esc(s.site_id)+'">Show on map</button>':'<span class="m">'+(s._ll?'':'Not placed yet')+'</span>')+'</td></tr>').join('');
  const left=view.length-shown;$('more').hidden=left<=0;if(left>0)$('more').textContent='Show '+fmt(Math.min(PAGE,left))+' more ('+fmt(left)+' not shown yet)';
  $('empty').hidden=view.length>0;$('dl').disabled=!view.length;$('dl').textContent=view.length===1?'Download this site (CSV)':'Download these '+fmt(view.length)+' sites (CSV)';}
function sync(){const p=new URLSearchParams(),st=state();for(const k of KEYS)if(st[k])p.set(k,st[k]);if(st.q)p.set('q',st.q);if(st.placed)p.set('placed','1');
  const q=p.toString();history.replaceState(null,'',location.pathname+(q?'?'+q:''));}
function csvCell(v){v=v==null?'':String(v);return /[",\r\n]/.test(v)?'"'+v.replace(/"/g,'""')+'"':v;}
function download(){const C=D.columns.slice(0,D.n_register_columns),lines=[C.join(',')];for(const s of view)lines.push(C.map(c=>csvCell(s[c])).join(','));
  const b=new Blob([lines.join('\r\n')+'\r\n'],{type:'text/csv;charset=utf-8'}),a=document.createElement('a');
  a.href=URL.createObjectURL(b);a.download='compute-ledger-'+D.cite.file_tag+'-sites'+(view.length<S.length?'-selected':'')+'.csv';document.body.appendChild(a);a.click();
  setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove();},0);}
function showSite(id,btn){const s=S.find(x=>x.site_id===id);if(!s||!s._ll||!map)return;layer.addLayer(s._mk);map.setView(s._ll,Math.max(map.getZoom(),12));s._mk.openPopup();
  $('map').scrollIntoView({block:'center'});opener=btn||null;
  if(btn)setTimeout(()=>{const a=document.querySelector('.leaflet-popup-content a');if(a)a.focus({preventScroll:true});},60);}
function opt(sel,v,t){const o=document.createElement('option');o.value=v;o.textContent=t;sel.appendChild(o);}
function init(data){D=data;const C=D.columns;
  S=D.rows.map(a=>{const s={};C.forEach((c,i)=>{s[c]=a[i];});s._country=D.countries[s.country]||s.country;s._kind=D.kinds[s.kind]||s.kind;
    s._n=+s.n_record_figures+ +s.n_computed_figures+ +s.n_claimed_figures;s._hold=(+s.n_record_figures+ +s.n_computed_figures)>0?'rec':+s.n_claimed_figures>0?'claim':'none';
    s._bt={};for(const x of (s.by_topic||'').split(';').filter(Boolean)){const [i,v]=x.split(':');s._bt[i]=v.split('/').map(Number);}
    const la=parseFloat(s.lat),lo=parseFloat(s.lon);s._ll=s.lat&&s.lon&&isFinite(la)&&isFinite(lo)?[la,lo]:null;
    s._text=[s.name,s.operator,s.site_id,s.locality,s.admin_region,s._country,s.also_known_as,s._kind,s.status].join(' ').toLowerCase();return s;});
  S.sort((a,b)=>a.name.localeCompare(b.name));
  D.topics.forEach((t,i)=>{if(S.some(s=>s._bt[i]))opt($('topic'),String(i),t);});
  Object.keys(D.kinds).forEach(k=>opt($('kind'),k,D.kinds[k]));
  Object.keys(D.statuses).forEach(k=>{if(S.some(s=>s.status_class===k))opt($('status'),k,D.statuses[k]);});
  Object.keys(D.countries).sort((a,b)=>D.countries[a].localeCompare(D.countries[b])).forEach(c=>opt($('country'),c,D.countries[c]));
  Object.keys(D.orgs).sort((a,b)=>D.orgs[a][0].localeCompare(D.orgs[b][0])).forEach(o=>opt($('org'),o,D.orgs[o][0]+' ('+plural(D.orgs[o][1].length,'site')+')'));
  const p=new URLSearchParams(location.search);for(const k of KEYS){const v=p.get(k)||'';if([...$(k).options].some(o=>o.value===v))$(k).value=v;}
  $('q').value=p.get('q')||'';$('placed').checked=p.get('placed')==='1';
  if(window.L){map=L.map('map',{scrollWheelZoom:false,worldCopyJump:true,minZoom:2});map.attributionControl.setPrefix('<a href="https://leafletjs.com">Leaflet</a>');
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:18,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors · sites: Compute Ledger, CC BY 4.0'}).addTo(map);
    map.setView([30,0],2);layer=L.layerGroup().addTo(map);
    map.on('click',()=>map.scrollWheelZoom.enable());map.on('mouseout',()=>map.scrollWheelZoom.disable());
    for(const s of S)if(s._ll){s._mk=L.circleMarker(s._ll,style(s)).bindTooltip(s.name,{direction:'top',offset:[0,-6]}).bindPopup(popup(s),{maxWidth:300,autoPanPaddingTopLeft:[52,16],autoPanPaddingBottomRight:[16,16]});}
    map.on('popupopen',e=>{const w=$('map').clientWidth,narrow=w<520,o=e.popup.options;  // measured when shown: the map is hidden while it loads
      o.maxWidth=narrow?Math.max(180,w-90):300;o.minWidth=Math.min(200,o.maxWidth);o.autoPanPaddingTopLeft=L.point(narrow?[16,16]:[52,16]);e.popup.update();});
    const mq=matchMedia('(prefers-color-scheme: dark)');(mq.addEventListener?mq.addEventListener('change',restyle):mq.addListener(restyle));}
  else{$('map').innerHTML='<p class="m" style="padding:16px">The map could not load. Every site is in the list below.</p>';}
  const ch=()=>{sync();render(true,true);};
  for(const k of KEYS)$(k).addEventListener('change',k==='topic'?()=>{sync();render(true,false);}:ch);$('placed').addEventListener('change',ch);
  let tm;$('q').addEventListener('input',()=>{clearTimeout(tm);tm=setTimeout(ch,180);});
  $('clear').addEventListener('click',()=>{for(const k of KEYS)$(k).value='';$('q').value='';$('placed').checked=false;ch();});
  $('banner').addEventListener('click',e=>{if(e.target.id==='unorg'){e.preventDefault();$('org').value='';ch();$('org').focus();}
    else if(e.target.id==='unbad'){e.preventDefault();badSite='';badKnown=null;sync();render(false,false);$('q').focus();}});
  $('more').addEventListener('click',()=>{shown+=PAGE;render(false,false);});
  $('dl').addEventListener('click',download);
  $('rows').addEventListener('click',e=>{const b=e.target.closest('button.show');if(b)showSite(b.dataset.id,b);});
  if(map){map.on('popupclose',()=>{const o=opener;opener=null;if(o&&document.body.contains(o)&&document.activeElement&&(document.activeElement===document.body||document.activeElement.closest('.leaflet-container')))o.focus();});
    document.addEventListener('keydown',e=>{if(e.key==='Escape'&&document.activeElement&&document.activeElement.closest('.leaflet-popup')){map.closePopup();}});}
  $('loading').hidden=true;$('app').hidden=false;if(map)map.invalidateSize();render(true,true);
  const site=p.get('site');if(site){const s=S.find(x=>x.site_id===site);if(s&&s._ll)showSite(site);else{badSite=site;badKnown=s||null;render(false,false);}}}
function restyle(){for(const s of S)if(s._mk)s._mk.setStyle(style(s));}
fetch('data/sites.json').then(r=>{if(!r.ok)throw new Error('HTTP '+r.status);return r.json();}).then(init)
  .catch(e=>{$('loading').textContent='The sites could not be loaded ('+e.message+'). They are in the Excel workbook and in sites.json, linked above.';});
})();
"""


def swatch(kind: str) -> str:
    if kind == "none":
        return '<svg width="14" height="14" aria-hidden="true"><circle cx="7" cy="7" r="5" fill="var(--paper)" stroke="var(--mk-none)" stroke-width="2"/></svg>'
    return f'<svg width="14" height="14" aria-hidden="true"><circle cx="7" cy="7" r="6" fill="var(--mk-{kind})"/></svg>'


def map_page(cite: dict, stats: dict) -> str:
    extra = '<link rel="stylesheet" href="vendor/leaflet-1.9.4/leaflet.css">\n'
    body = [nav("map.html"),
            f'<p class="eyebrow">Compute Ledger · version {bs.e(cite["label"])}</p><h1>Map of sites</h1>',
            f'<p class="lede">Every site the ledger holds with coordinates from a public document: {words(stats["placed_kinds"])}. '
            + (f'None of the {words(stats["unplaced_kinds"], "or")} is placed yet: '
               'they are in the list below the map until a document gives their location. ' if stats["unplaced_kinds"] else "")
            + 'The colour shows what the ledger has found for a site so far, '
            'not anything about the site itself. Choose a topic to colour the map by what is found on that topic alone, or an organisation to see '
            'its sites. Click a site for its page and its figures, topic by topic.</p>',
            get_data_line(cite),
            f'<p id="loading">Loading {stats["n_sites"]:,} sites…</p>',
            '<noscript><p>This page needs JavaScript. Every site is listed on <a href="sites/">the sites page</a>.</p></noscript>',
            '<div id="app" hidden>',
            '<div class="filters" id="filters">',
            '<input id="q" type="search" placeholder="Search a site, operator or place" aria-label="Search the sites">',
            '<select id="topic" aria-label="Topic: colours the map by what is found on it"><option value="">Every topic</option></select>',
            '<select id="holds" aria-label="What the ledger has found"><option value="">Anything found or not</option>'
            '<option value="rec">Records found</option><option value="claim">Claims only</option><option value="none">No figures yet</option></select>',
            '<select id="kind" aria-label="Kind of site"><option value="">Every kind of site</option></select>',
            '<select id="status" aria-label="Status"><option value="">Any status</option></select>',
            '<select id="country" aria-label="Country"><option value="">Every country</option></select>',
            '<select id="org" aria-label="Organisation"><option value="">Every organisation</option></select>',
            '<label class="chk"><input type="checkbox" id="placed"> Only sites on the map</label>',
            '<button class="btn ghost" id="clear" type="button">Clear</button>',
            '</div>',
            '<div class="banner" id="banner" role="status"></div>',
            '<a class="skip" href="#sitelist">Skip the map, go to the list of sites</a>',
            '<div id="mapwrap"><div id="map" role="region" aria-label="Map of the sites; the same sites are listed in the table below"></div><p id="mapnote" hidden></p></div>',
            '<ul class="legend">'
            f'<li>{swatch("rec")}<span><b>Records found</b> (<span id="n-rec"></span>): <span id="l-rec">at least one figure from a record, or computed by the ledger from records</span></span></li>'
            f'<li>{swatch("claim")}<span><b>Claims only</b> (<span id="n-claim"></span>): <span id="l-claim">only what the company or a government says</span></span></li>'
            f'<li>{swatch("none")}<span><b>No figures yet</b> (<span id="n-none"></span>): <span id="l-none">listed from a register or a list of sites, no figure read yet</span></span></li></ul>',
            f'<p class="m" style="margin-top:10px">{stats["n_placed"]:,} of {stats["n_sites"]:,} sites are placed from a document. The other '
            f'{stats["n_sites"] - stats["n_placed"]:,} are in the list below but not on the map until a document gives their location.</p>',
            '<div class="bar"><span class="count" id="count" aria-live="polite"></span>'
            '<button class="btn" id="dl" type="button">Download these sites (CSV)</button></div>',
            '<div class="tw" id="sitelist" tabindex="-1"><table class="sites"><thead><tr><th>Site</th><th>Kind</th><th>Where</th><th>What the ledger holds</th><th></th></tr></thead>'
            '<tbody id="rows"></tbody></table></div>',
            '<p class="empty" id="empty" hidden>No site matches. Clear a filter, or search for fewer words.</p>',
            '<p class="more"><button class="btn ghost" id="more" type="button" hidden>Show more</button></p>',
            '</div>',
            foot("map.html", "the map of sites"), '<script src="vendor/leaflet-1.9.4/leaflet.js"></script>\n', f"<script>{MAP_JS}</script>\n</body>\n</html>\n"]
    return head("Map of sites · Compute Ledger", "Every site in the Compute Ledger on a map, with what public records show for each.",
                extra + f"<style>{MAP_CSS}</style>\n", path="map.html") + "\n".join(body)


# ------------------------------------------------------------------------------------------------------------- workbook

XML_BAD = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f￾￿]")
NUM = re.compile(r"-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")
NS = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
DECL = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'


def col_letter(i: int) -> str:
    s, i = "", i + 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def xt(s: str) -> str:
    return html.escape(XML_BAD.sub("", s), quote=False)


def sheet(header: list, rows: list, numeric: set, wrap_first: bool = False) -> tuple[str, str]:
    widths = []
    for i in range(len(header)):
        w = max([len(header[i])] + [len(r[i]) if i < len(r) else 0 for r in rows[:4000]])
        widths.append(110 if wrap_first and i == 0 else max(8, min(60, w + 2)))
    out = [DECL, f"<worksheet {NS}>"]
    if rows and not wrap_first:
        out.append('<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>')
    out.append('<sheetFormatPr defaultRowHeight="15"/><cols>' + "".join(
        f'<col min="{i + 1}" max="{i + 1}" width="{w}" customWidth="1"/>' for i, w in enumerate(widths)) + "</cols><sheetData>")
    for ri, r in enumerate([header] + rows, start=1):
        cells = []
        for ci, v in enumerate(r):
            if v == "":
                continue
            ref = f"{col_letter(ci)}{ri}"
            if ri > 1 and ci in numeric and NUM.fullmatch(v):
                cells.append(f'<c r="{ref}"><v>{v}</v></c>')
            else:
                st = ' s="1"' if ri == 1 and not wrap_first else (' s="2"' if wrap_first else "")
                cells.append(f'<c r="{ref}" t="inlineStr"{st}><is><t xml:space="preserve">{xt(v)}</t></is></c>')
        out.append(f'<row r="{ri}">{"".join(cells)}</row>')
    out.append("</sheetData>")
    ref = f"A1:{col_letter(len(header) - 1)}{len(rows) + 1}"
    if rows and not wrap_first:
        out.append(f'<autoFilter ref="{ref}"/>')
    out.append("</worksheet>")
    return "".join(out), ref


def workbook(cite: dict) -> bytes:
    pkg = json.loads((ROOT / "data" / "datapackage.json").read_text(encoding="utf-8"))
    res = {r["path"]: r for r in pkg["resources"]}
    missing = sorted(set(res) - set(WORKBOOK_SHEETS))
    if missing:
        raise SystemExit(f"data/datapackage.json lists tables with no workbook sheet: {missing}; add them to WORKBOOK_SHEETS in site/build_explore.py")
    sheets = []  # (name, xml, ref or None)
    tables = []
    for path, name in WORKBOOK_SHEETS.items():
        r = res[path]
        with open(ROOT / "data" / path, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        names = [fl["name"] for fl in r["schema"]["fields"]]
        numeric = {i for i, fl in enumerate(r["schema"]["fields"]) if fl["type"] in ("number", "integer")}
        xml, ref = sheet(rows[0], rows[1:], numeric)
        tables.append((name, path, r, len(rows) - 1, names))
        sheets.append((name, xml, ref))
    doi = f" https://doi.org/{cite['doi']}." if cite["doi"] else ""
    readme = [
        ["Compute Ledger: public records on the physical, social and economic footprint of AI compute"],
        [f"Version {cite['label']}. Data and text: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Code: MIT."],
        [f"Cite as: {cite['authors']} ({cite['year']}). Compute Ledger: public records on the physical, social and economic footprint of AI compute, "
         f"version {cite['label']}.{doi} {cite['repo']}"],
        [""],
        ["Records (documents from regulators, courts, grid operators, statistics offices, auditors, registries or customs) are kept apart from claims "
         "(what companies and governments say): see the column side on the sheet Figures. A figure the ledger computed from records has basis "
         "'derived' and gives its formula in notes. A gap means the ledger has not found or read a public record yet, not that none exists."],
        ["Start with the sheet Figures: every figure, one row each, with its source. The sheet Columns says what each column means. "
         "Controlled values for metric, unit, basis and relation are defined in pipeline/measurement_vocab.json in the repository."],
        [""],
        ["Sheets:"],
    ]
    for name, path, r, n, _ in tables:
        readme.append([f"{name} ({n:,} rows), from data/{path}: {r['description']}"])
    readme += [[""], [f"Explore and filter every figure, and cite one: {cite['site']}explore.html"], [f"Map of sites: {cite['site']}map.html"],
               [f"Repository, with every table as CSV and the code that builds them: {cite['repo']}"],
               ["This workbook is generated from the repository's CSV tables by site/build_explore.py and changes only when they do."]]
    rm_xml, _ = sheet(["Read me"], readme[1:], set(), wrap_first=True)
    rm_xml = rm_xml.replace('<c r="A1" t="inlineStr" s="2"><is><t xml:space="preserve">Read me</t></is></c>',
                            f'<c r="A1" t="inlineStr" s="1"><is><t xml:space="preserve">{xt(readme[0][0])}</t></is></c>')
    cols_rows = []
    for name, path, r, _, _ in tables:
        for fl in r["schema"]["fields"]:
            vals = ", ".join(x for x in fl.get("enum", []) if x) + (" or empty" if "" in fl.get("enum", []) else "") if "enum" in fl else \
                (f"a key of '{fl['vocab']}' in pipeline/measurement_vocab.json" if "vocab" in fl else "")
            cols_rows.append([name, fl["name"], fl["type"], "yes" if fl.get("required") else "", vals, fl["description"]])
    cx, cref = sheet(["Sheet", "Column", "Type", "Required", "Allowed values", "Meaning"], cols_rows, set())
    sheets = [("Read me", rm_xml, None)] + sheets + [("Columns", cx, cref)]

    files = {}
    files["[Content_Types].xml"] = (DECL + '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        + "".join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                  for i in range(1, len(sheets) + 1))
        + '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/></Types>')
    files["_rels/.rels"] = (DECL + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/></Relationships>')
    files["docProps/core.xml"] = (DECL + '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        f'<dc:title>Compute Ledger {xt(cite["version"])}</dc:title><dc:creator>{xt(cite["authors"])}</dc:creator>'
        '<dc:description>Public records on the physical, social and economic footprint of AI compute. CC BY 4.0.</dc:description></cp:coreProperties>')
    defined = "".join(f'<definedName name="_xlnm._FilterDatabase" localSheetId="{i}" hidden="1">\'{xt(n)}\'!{re.sub(r"([A-Z]+)(\d+)", r"$\1$\2", ref)}</definedName>'
                      for i, (n, _, ref) in enumerate(sheets) if ref)
    files["xl/workbook.xml"] = (DECL + f'<workbook {NS}><bookViews><workbookView activeTab="0"/></bookViews><sheets>'
        + "".join(f'<sheet name="{xt(n)}" sheetId="{i}" r:id="rId{i}"/>' for i, (n, _, _) in enumerate(sheets, start=1))
        + f"</sheets><definedNames>{defined}</definedNames></workbook>")
    files["xl/_rels/workbook.xml.rels"] = (DECL + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        + "".join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>'
                  for i in range(1, len(sheets) + 1))
        + f'<Relationship Id="rId{len(sheets) + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>')
    files["xl/styles.xml"] = (DECL + '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts>'
        '<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>'
        '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="3"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
        '<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/>'
        '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf></cellXfs>'
        '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>')
    for i, (_, xml, _) in enumerate(sheets, start=1):
        files[f"xl/worksheets/sheet{i}.xml"] = xml
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, text in files.items():
            zi = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.create_system = 3
            zi.external_attr = 0o644 << 16
            z.writestr(zi, text.encode("utf-8"), compresslevel=6)
    return buf.getvalue()


def zip_parts(b: bytes) -> dict:
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        return {n: z.read(n) for n in z.namelist()}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="compare with the committed files instead of writing them")
    a = ap.parse_args()
    figures, sites_json, cite, stats = build_data()
    out = {
        "explore.html": explore_page(cite, stats).encode("utf-8"),
        "map.html": map_page(cite, stats).encode("utf-8"),
        "data/figures.json": jdump(figures),
        "data/sites.json": jdump(sites_json),
        "data/compute-ledger.xlsx": workbook(cite),
        "data/datasette-metadata.json": jdump(datasette_metadata(cite)),
    }
    if a.check:
        stale = []
        for rel, b in out.items():
            p = DOCS / rel
            if not p.exists():
                stale.append(rel)
            elif rel.endswith(".xlsx"):
                if zip_parts(p.read_bytes()) != zip_parts(b):
                    stale.append(rel)
            elif p.read_bytes() != b:
                stale.append(rel)
        if stale:
            print(f"stale: {', '.join('docs/' + s for s in stale)}: run python3 site/build_explore.py (or ./rebuild.sh) and commit")
            sys.exit(1)
        print(f"explore, map and downloads match the build ({len(out)} files)")
        return
    for rel, b in out.items():
        p = DOCS / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if not p.exists() or (zip_parts(p.read_bytes()) != zip_parts(b) if rel.endswith(".xlsx") else p.read_bytes() != b):
            p.write_bytes(b)
    print(f"wrote docs/explore.html, docs/map.html and docs/data/ ({stats['n_figures']:,} figures, {stats['n_sites']:,} sites, "
          f"{stats['n_placed']:,} on the map)")


if __name__ == "__main__":
    main()
