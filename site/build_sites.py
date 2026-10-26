#!/usr/bin/env python3
"""One page per site: docs/sites/<site_id>.html, plus docs/sites/index.html.

Each page lays out what the ledger's tables hold for one site, from the register, the measurements table, the chain
table and the registry: records first, then what the ledger computed from them, then claims, then documented supply
links, then the entries that discuss it. It also says plainly which kinds of public record the ledger has not found yet.

Inputs: data/climate_trace_seed/site_register.csv, measurements.csv, water_stress.csv (if present), data/chain/edges.csv,
registry/*.json. Output is deterministic (no build time), so CI can rebuild and compare byte for byte.

    python3 site/build_sites.py [--out docs/sites]
"""
import argparse
import csv
import html
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "data" / "climate_trace_seed"
REPO_URL = "https://github.com/kn0wledgebfre3-sys/compute-ledger"

COUNTRY = {"ARE": "United Arab Emirates", "AUS": "Australia", "AUT": "Austria", "BEL": "Belgium", "BRA": "Brazil",
           "BTN": "Bhutan", "CAN": "Canada", "CHL": "Chile", "CHN": "China", "DEU": "Germany", "DNK": "Denmark",
           "EST": "Estonia", "ETH": "Ethiopia", "FIN": "Finland", "FRA": "France", "GBR": "United Kingdom", "IND": "India",
           "IRL": "Ireland", "ISR": "Israel", "JPN": "Japan", "KAZ": "Kazakhstan", "KEN": "Kenya", "KOR": "South Korea",
           "MEX": "Mexico", "MYS": "Malaysia", "NLD": "Netherlands", "NOR": "Norway", "PHL": "Philippines", "RWA": "Rwanda",
           "SAU": "Saudi Arabia", "SGP": "Singapore", "SWE": "Sweden", "THA": "Thailand", "TWN": "Taiwan", "URY": "Uruguay",
           "USA": "United States", "VNM": "Vietnam", "IDN": "Indonesia", "ESP": "Spain", "ITA": "Italy", "POL": "Poland",
           "ZAF": "South Africa", "NZL": "New Zealand", "CHE": "Switzerland", "ISL": "Iceland", "PRY": "Paraguay",
           "ARG": "Argentina", "EGY": "Egypt", "NGA": "Nigeria", "QAT": "Qatar", "OMN": "Oman", "KWT": "Kuwait"}
KIND = {"datacenter": "Datacenter", "telecom_exchange": "Telephone exchange filed as a datacenter",
        "mixed_building_with_datacenter": "Building that contains a datacenter", "smelter_refiner": "Smelter or refiner",
        "fab": "Chip fab or packaging plant", "crypto_mining": "Crypto mining site",
        "crypto_to_ai_conversion": "Crypto mining site moving to AI or hosting", "nuclear_plant": "Nuclear plant"}

# what a reader would ask of any site, and the metrics that answer it
QUESTIONS = [
    ("Electricity actually used", {"electricity_consumed", "energy_consumed_total"}),
    ("Grid connection and capacity", {"connected_capacity", "contracted_capacity", "approved_capacity", "requested_capacity",
                                      "planned_capacity", "it_capacity", "peak_demand", "forecast_demand", "electricity_share"}),
    ("Water", {"water_withdrawn", "water_consumed", "water_allocation", "water_discharged"}),
    ("Generators, fuel and air emissions", None),  # generator_*, permitted_*, natural_gas_burned, emissions_*
]


def gen_or_emissions(metric: str) -> bool:
    return bool(re.match(r"(generator_|permitted_|emissions_|natural_gas_burned|generation_capacity|electricity_generated)", metric))


def question_of(metric: str) -> str:
    for q, ms in QUESTIONS:
        if ms is None and gen_or_emissions(metric) or ms and metric in ms:
            return q
    return "Other figures"


def e(s) -> str:
    return html.escape(str(s or ""), quote=True)


def link(url: str, text: str) -> str:
    if re.match(r"https?://", url or ""):
        return f'<a href="{e(url)}" rel="noopener">{e(text or url)}</a>'
    return e(text)


def read_csv(p: Path) -> list[dict]:
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def period(r: dict) -> str:
    s, t = r.get("period_start", ""), r.get("period_end", "")
    if s and t and s[5:] == "01-01" and t[5:] == "12-31" and s[:4] == t[:4]:
        return s[:4]
    if s and t and s[:7] == "%s-07" % s[:4] and t[5:] == "06-30" and int(t[:4]) == int(s[:4]) + 1:
        return f"FY to {t}"
    if s and t:
        return f"{s} to {t}"
    return s or t or "not stated"


LABEL = {
    "electricity_consumed": "Electricity used", "energy_consumed_total": "Energy used, all fuels", "electricity_generated": "Electricity generated",
    "electricity_share": "Share of an electricity total", "peak_demand": "Peak demand", "forecast_demand": "Forecast demand",
    "connected_capacity": "Grid capacity connected", "contracted_capacity": "Grid capacity contracted", "approved_capacity": "Capacity approved",
    "requested_capacity": "Capacity requested", "planned_capacity": "Capacity planned", "it_capacity": "IT capacity",
    "generation_capacity": "Generating capacity", "generator_count": "Generators", "generator_hours": "Generator hours",
    "generator_fuel_burned": "Generator fuel burned", "natural_gas_burned": "Natural gas burned",
    "permitted_standby_generation": "Standby generation permitted", "permitted_generation_thermal_input": "Generation permitted (thermal input)",
    "permitted_generation_as_stated": "Generation permitted (as stated)", "water_withdrawn": "Water withdrawn", "water_consumed": "Water consumed",
    "water_allocation": "Water allocation", "emissions_nox": "NOx emitted", "emissions_co": "CO emitted", "emissions_voc": "VOC emitted",
    "emissions_so2": "SO2 emitted", "emissions_pm10": "PM10 emitted", "emissions_pm25": "PM2.5 emitted", "emissions_hap": "Hazardous air pollutants emitted",
    "emissions_co2": "CO2 emitted", "emissions_co2e": "Greenhouse gases emitted (CO2e)", "emissions_scope1": "Scope 1 emissions",
    "emissions_scope2_location": "Scope 2 emissions, location-based", "emissions_scope2_market": "Scope 2 emissions, market-based",
    "share_other": "Share", "duration_other": "Duration", "count_other": "Count", "site_count": "Sites", "land_area": "Land area",
    "spent_fuel_stored": "Spent fuel stored", "public_money": "Public money", "other": "Other figure",
}


def metric_label(m: str) -> str:
    return LABEL.get(m) or m.replace("_", " ").capitalize()


UNIT_SHOW = {"pct": "%", "m3": "m³", "short_ton": "short tons", "count": ""}


def as_published(r: dict) -> str:
    """The value as the document printed it; when it printed a bare number, the unit the ledger recorded beside it."""
    v = r["value_as_published"]
    if re.fullmatch(r"[\d.,\s~<>≈-]+", v or ""):
        u = UNIT_SHOW.get(r["unit"], r["unit"].replace("_", " "))
        return f"{v} {u}".strip()
    return v


def figure_table(rows: list[dict], vocab_bases: dict) -> str:
    out = ['<div class="tw"><table><thead><tr><th>Figure</th><th>As published</th><th>Period</th><th>Kind of document</th>'
           '<th>Source</th></tr></thead><tbody>']
    for r in rows:
        src = link(r["source_url"], r["source_title"] or r["source_url"])
        pub = " · ".join(x for x in (r["source_publisher"], r["source_date"]) if x)
        twice = (' <span class="tag" title="read a second time, independently">' + ("inputs read twice" if r["basis"] == "derived" else "read twice")
                 + "</span>") if r["second_read"] == "yes" else ""
        qual = f'<div class="m">{e(r["qualifier"].replace("_", " "))}</div>' if r["qualifier"] and r["qualifier"] != "exact" else ""
        out.append(f'<tr><td><strong>{e(metric_label(r["metric"]))}</strong><div class="m">{e(r["metric_detail"])}</div></td>'
                   f'<td class="v">{e(as_published(r))}{qual}{twice}</td><td class="m">{e(period(r))}</td>'
                   f'<td class="m" title="{e(vocab_bases.get(r["basis"], ""))}">{e(r["basis"].replace("_", " "))}</td>'
                   f'<td>{src}<div class="m">{e(pub)}</div></td></tr>')
    out.append("</tbody></table></div>")
    return "".join(out)


def order(rows: list[dict]) -> list[dict]:
    qi = {q: i for i, (q, _) in enumerate(QUESTIONS)}
    return sorted(rows, key=lambda r: (qi.get(question_of(r["metric"]), 9), r["metric"], -int((r["period_end"] or r["period_start"] or "0")[:4] or 0),
                                       r["metric_detail"], r["measurement_id"]))


HEAD = ('<!doctype html>\n<html lang="en">\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>{title}</title>\n<meta name="description" content="{desc}">\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@75..100,400..800&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=IBM+Plex+Mono:wght@400;500&display=swap">\n'
        '<link rel="stylesheet" href="site.css">\n<body>\n<div class="wrap">\n')
FOOT = ('<footer><p>Records are documents from regulators, courts, grid operators, statistics offices, auditors, registries or customs. '
        'Claims are what companies and governments say. Figures computed by the ledger show their formula. A gap here means the ledger has not '
        'found or read a public record yet, not that none exists or that anything is wrong.</p>'
        f'<p>Data CC BY 4.0. <a href="{REPO_URL}">Repository</a> · <a href="{REPO_URL}/issues">Report an error or a missing record</a> · '
        '<a href="../index.html">The ledger</a> · <a href="../brief.html">Brief</a></p></footer>\n</div>\n</body>\n</html>\n')

CSS = """:root{
  --paper:#F4F6F3; --paper-2:#E9EDE8; --ink:#17211E; --ink-2:#4B5955; --rule:#C9D1CC; --accent:#1C6B5F;
  --rec:#1C6B5F; --calc:#4A5A8C; --claim:#B2481F; --gap:#8A6D1F;
  --display:"Archivo","Helvetica Neue",Arial,sans-serif; --body:"Source Serif 4",Georgia,"Times New Roman",serif;
  --mono:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace }
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --paper:#121816; --paper-2:#1A2320; --ink:#E6ECE8; --ink-2:#A3B0AB; --rule:#2E3B36; --accent:#4FB3A3;
  --rec:#4FB3A3; --calc:#9AA8D8; --claim:#E07A4E; --gap:#D0A94C; color-scheme:dark } }
:root[data-theme="dark"]{ --paper:#121816; --paper-2:#1A2320; --ink:#E6ECE8; --ink-2:#A3B0AB; --rule:#2E3B36; --accent:#4FB3A3;
  --rec:#4FB3A3; --calc:#9AA8D8; --claim:#E07A4E; --gap:#D0A94C; color-scheme:dark }
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--body);font-size:17px;line-height:1.55;
  padding:0 max(16px,env(safe-area-inset-right,0px)) 64px max(16px,env(safe-area-inset-left,0px))}
a{color:var(--accent);text-decoration-thickness:1px;text-underline-offset:3px;overflow-wrap:anywhere}
a:focus-visible,input:focus-visible,select:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.wrap{max-width:1100px;margin:0 auto}
nav.top{font-family:var(--mono);font-size:13px;padding:20px 0;border-bottom:1px solid var(--rule)}
h1,h2{font-family:var(--display);font-stretch:85%;line-height:1.1;text-wrap:balance;margin:0}
h1{font-size:clamp(30px,5vw,52px);font-weight:800;letter-spacing:-0.015em;margin:28px 0 8px}
h2{font-size:clamp(21px,2.6vw,27px);font-weight:700;margin:44px 0 6px;padding-left:12px;border-left:4px solid var(--bar,var(--rule))}
h2 + p.lede{margin-top:4px}
.eyebrow,.m,th{font-family:var(--mono);font-size:12.5px;color:var(--ink-2)}
.eyebrow{letter-spacing:.06em;text-transform:uppercase;margin-top:28px}
p{margin:0 0 1em;max-width:72ch}
.lede{color:var(--ink-2)}
dl.facts{display:grid;grid-template-columns:max-content minmax(0,1fr);gap:6px 18px;margin:18px 0 0;max-width:820px}
dl.facts dt{font-family:var(--mono);font-size:12.5px;color:var(--ink-2);padding-top:3px}
dl.facts dd{margin:0;overflow-wrap:anywhere;min-width:0}
td,.m,h1{overflow-wrap:anywhere}
ul.q{list-style:none;padding:0;margin:12px 0 0;display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px}
ul.q li{background:var(--paper-2);border-top:3px solid var(--rec);padding:10px 12px}
ul.q li.no{border-top-color:var(--gap)}
ul.q b{display:block;font-family:var(--display);font-size:15px}
ul.q span{font-size:14.5px;color:var(--ink-2)}
.tw{overflow-x:auto;margin:10px 0 0;border-top:1px solid var(--rule)}
table{border-collapse:collapse;width:100%;font-size:15px}
th{text-align:left;font-weight:500;padding:8px 10px 6px 0;border-bottom:1px solid var(--rule);white-space:nowrap}
td{vertical-align:top;padding:9px 10px 9px 0;border-bottom:1px solid var(--rule)}
td.v{font-variant-numeric:tabular-nums;min-width:9ch}
.tag{display:inline-block;font-family:var(--mono);font-size:11px;border:1px solid var(--rule);padding:0 5px;margin-top:4px;color:var(--ink-2)}
.rec{--bar:var(--rec)} .calc{--bar:var(--calc)} .claim{--bar:var(--claim)} .gapc{--bar:var(--gap)}
blockquote{margin:4px 0 0;font-style:italic;color:var(--ink-2);font-size:14.5px}
.filters{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0 8px}
.filters input,.filters select{font:inherit;font-size:15px;padding:7px 9px;border:1px solid var(--rule);background:var(--paper);color:var(--ink);min-width:0}
.filters input{flex:1 1 260px}
footer{margin-top:56px;border-top:1px solid var(--rule);padding-top:16px;font-size:14.5px;color:var(--ink-2)}
@media (max-width:640px){ dl.facts{grid-template-columns:1fr} dl.facts dt{padding-top:8px} }
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=ROOT / "docs" / "sites")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)

    sites = read_csv(PKG / "site_register.csv")
    vocab = json.load(open(ROOT / "pipeline" / "measurement_vocab.json", encoding="utf-8"))
    bases = vocab["bases"]
    by_site = defaultdict(list)
    for r in read_csv(PKG / "measurements.csv"):
        if r["subject_type"] == "site":
            by_site[r["subject_id"]].append(r)
    edges = defaultdict(list)
    for r in read_csv(ROOT / "data" / "chain" / "edges.csv"):
        for side in ("from", "to"):
            if r[f"{side}_type"] == "site":
                edges[r[f"{side}_id"]].append(r)
    ws = {}
    if (PKG / "water_stress.csv").exists():
        rows_ws = read_csv(PKG / "water_stress.csv")
        stray = sorted({r["site_id"] for r in rows_ws} - {s["site_id"] for s in sites})
        if stray:
            raise SystemExit(f"water_stress.csv has site ids not in the register (rerun pipeline/water_stress.py): {stray[:5]}")
        ws = {r["site_id"]: r for r in rows_ws if r.get("bws_label")}
    entries = {}
    for p in sorted((ROOT / "registry").glob("*.json")):
        if p.stem in ("guide", "standard", "sources"):
            continue
        for x in json.load(open(p, encoding="utf-8")):
            entries[x["id"]] = x
    ids = {s["site_id"] for s in sites}
    problems = []
    for s in sites:
        if s["country"] not in COUNTRY:
            problems.append(f"{s['site_id']}: no country name for {s['country']}")
    if problems:
        raise SystemExit("\n".join(problems))

    index_rows = []
    for s in sorted(sites, key=lambda s: s["site_id"]):
        sid = s["site_id"]
        rows = by_site.get(sid, [])
        rec = order([r for r in rows if r["side"] == "record" and r["basis"] != "derived"])
        calc = order([r for r in rows if r["basis"] == "derived"])
        claim = order([r for r in rows if r["side"] == "claim"])
        eds = sorted(edges.get(sid, []), key=lambda r: (r["leg"], r["from_name"], r["to_name"], r["edge_id"]))
        kind = KIND.get(s["kind"], s["kind"].replace("_", " ").capitalize())
        country = COUNTRY[s["country"]]
        place = ", ".join(x for x in (s["locality"], s["admin_region"], country) if x)

        # what is there and what is not
        found = defaultdict(lambda: [0, 0])
        for r in rows:
            q = question_of(r["metric"])
            found[q][0 if r["side"] == "record" else 1] += 1
        qs = []
        for q, _ in QUESTIONS:
            n_rec, n_cl = found.get(q, [0, 0])
            if n_rec:
                qs.append(f'<li><b>{e(q)}</b><span>{n_rec} figure{"s" if n_rec != 1 else ""} from records'
                          f'{f", {n_cl} claimed" if n_cl else ""}</span></li>')
            elif n_cl:
                qs.append(f'<li class="no"><b>{e(q)}</b><span>Only what the company says ({n_cl}); no record found yet</span></li>')
            else:
                qs.append(f'<li class="no"><b>{e(q)}</b><span>No public record found yet</span></li>')
        no = ' class="no"'
        qs.append(f'<li{"" if eds else no}><b>Who supplies it, and whom it serves</b><span>'
                  + (f'{len(eds)} documented link{"s" if len(eds) != 1 else ""}' if eds else "No documented link yet") + "</span></li>")
        qs.append(f'<li{"" if s["lat"] else no}><b>Location</b><span>'
                  + ("Placed from a document" if s["lat"] else "Not yet placed on a map") + "</span></li>")

        facts = [("Kind", e(kind)), ("Operator", e(s["operator"]) or "not named in the records read"), ("Where", e(place))]
        if s["lat"] and s["lon"]:
            lat, lon = float(s["lat"]), float(s["lon"])
            facts.append(("Coordinates", f'{lat:.5f}, {lon:.5f} · <a href="https://www.openstreetmap.org/?mlat={lat:.5f}&amp;mlon={lon:.5f}#map=15/{lat:.5f}/{lon:.5f}" rel="noopener">map</a>'))
        if s["status"]:
            facts.append(("Status in the records", e(s["status"])))
        if sid in ws:
            w = ws[sid]
            facts.append(("Water stress where it sits", f'{e(w["bws_label"])} <span class="m">baseline water stress of sub-basin {e(w["pfaf_id"])}, '
                          f'<a href="https://www.wri.org/data/aqueduct-global-maps-40-data" rel="noopener">WRI Aqueduct {e(w["aqueduct_version"])}</a> (CC BY 4.0)</span>'))
        facts.append(("Listed from", e(s["register_source"])))
        if s["also_known_as"]:
            facts.append(("Also known as", e(s["also_known_as"])))
        if s["notes"]:
            facts.append(("Notes", e(s["notes"])))

        body = [f'<nav class="top"><a href="../index.html">Compute Ledger</a> / <a href="index.html">Sites</a></nav>',
                f'<p class="eyebrow">{e(kind)} · {e(country)}</p><h1>{e(s["name"])}</h1>',
                '<dl class="facts">' + "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in facts) + "</dl>",
                '<h2 class="gapc">What the public record holds</h2>',
                '<p class="lede">The questions anyone would ask of this site, and whether the ledger has found a public record that answers them.</p>',
                '<ul class="q">' + "".join(qs) + "</ul>"]
        if rec:
            body += ['<h2 class="rec">Records</h2><p class="lede">Figures from regulators, grid operators, utilities, statistics offices and other record holders, each as published.</p>',
                     figure_table(rec, bases)]
        if calc:
            body += ['<h2 class="calc">Computed by the ledger from those records</h2><p class="lede">Each row gives its formula; the inputs are records above or in the linked documents.</p>',
                     figure_table(calc, bases)]
        if claim:
            body += ['<h2 class="claim">Claims</h2><p class="lede">What the operator or another party says, kept apart from the records.</p>',
                     figure_table(claim, bases)]
        if eds:
            t = ['<div class="tw"><table><thead><tr><th>Link</th><th>Period</th><th>Kind of document</th><th>Source and the line that states it</th></tr></thead><tbody>']
            for r in eds:
                def node(side):
                    i, n = r[f"{side}_id"], r[f"{side}_name"]
                    if r[f"{side}_type"] == "site" and i in ids and i != sid:
                        return f'<a href="{e(i)}.html">{e(n or i)}</a>'
                    return f"<strong>{e(n or i)}</strong>"
                planned = ' <span class="tag">planned</span>' if re.search(r"\bplanned\b", r["notes"], re.I) else ""
                t.append(f'<tr><td>{node("from")} {e(r["relation"].replace("_", " "))} {node("to")}{planned}<div class="m">{e(r["leg"].replace("_", " "))}</div></td>'
                         f'<td class="m">{e(period(r))}</td><td class="m">{e(r["basis"].replace("_", " "))}</td>'
                         f'<td>{link(r["document_url"], r["document_title"])}<div class="m">{e(" · ".join(x for x in (r["publisher"], r["document_date"]) if x))}</div>'
                         f'<blockquote>{e(r["quoted_line"])}</blockquote></td></tr>')
            t.append("</tbody></table></div>")
            body += ['<h2 class="rec">Supply links</h2><p class="lede">Who supplies this site, or whom it serves, as a document states it.</p>', "".join(t)]
        ents = sorted({r["entry_id"] for r in rows + eds if r.get("entry_id") in entries})
        if ents:
            body += ['<h2>Ledger entries that discuss it</h2><ul>'
                     + "".join(f'<li><a href="../index.html#{e(i)}">{e(entries[i]["site_or_subject"])}</a> <span class="m">{e(entries[i]["country"])}</span></li>' for i in ents)
                     + "</ul>"]
        desc = f"{s['name']}: {kind} in {place}. What public records show, from the Compute Ledger."
        page = HEAD.format(title=e(f"{s['name']} · Compute Ledger"), desc=e(desc)) + "\n".join(body) + "\n" + FOOT
        (a.out / f"{sid}.html").write_text(page, encoding="utf-8")
        index_rows.append((s, kind, country, len(rec), len(calc), len(claim), len(eds)))

    # index
    kinds = sorted({k for _, k, *_ in index_rows})
    countries = sorted({c for _, _, c, *_ in index_rows})
    trs = []
    for s, kind, country, nr, nc, ncl, ne in sorted(index_rows, key=lambda x: (x[2], x[0]["name"].lower(), x[0]["site_id"])):
        trs.append(f'<tr data-k="{e(kind)}" data-c="{e(country)}"><td><a href="{e(s["site_id"])}.html">{e(s["name"])}</a>'
                   f'<div class="m">{e(s["operator"])}</div></td><td class="m">{e(kind)}</td>'
                   f'<td class="m">{e(country)}{("<br>" + e(s["admin_region"])) if s["admin_region"] else ""}</td>'
                   f'<td class="v">{nr or ""}</td><td class="v">{nc or ""}</td><td class="v">{ncl or ""}</td><td class="v">{ne or ""}</td>'
                   f'<td class="m">{"yes" if s["lat"] else ""}</td></tr>')
    n_rec = sum(1 for x in index_rows if x[3])
    idx = [f'<nav class="top"><a href="../index.html">Compute Ledger</a> / Sites</nav>',
           f'<p class="eyebrow">{len(index_rows)} sites · {len(countries)} countries and territories</p><h1>Sites</h1>',
           f'<p>One page for every site in the ledger\'s register: datacenters, the buildings and exchanges that file as datacenters, '
           f'crypto mining sites, nuclear plants, chip fabs and the smelters and refiners in the chain. {n_rec} have at least one figure from a record. '
           'Each page shows the records, what the ledger computed from them, the claims, the documented supply links, and what is still missing.</p>',
           '<div class="filters"><input id="q" type="search" placeholder="Search name, operator, place" aria-label="Search sites">'
           '<select id="k" aria-label="Kind"><option value="">All kinds</option>' + "".join(f'<option>{e(k)}</option>' for k in kinds) + '</select>'
           '<select id="c" aria-label="Country"><option value="">All countries</option>' + "".join(f'<option>{e(c)}</option>' for c in countries) + '</select></div>',
           '<p class="m" id="n" aria-live="polite"></p>',
           '<div class="tw"><table><thead><tr><th>Site</th><th>Kind</th><th>Where</th><th>Records</th><th>Computed</th><th>Claims</th><th>Links</th><th>Placed</th></tr></thead><tbody id="rows">'
           + "".join(trs) + "</tbody></table></div>",
           """<script>
(()=>{const q=document.getElementById('q'),k=document.getElementById('k'),c=document.getElementById('c'),n=document.getElementById('n');
const rows=[...document.querySelectorAll('#rows tr')];
function f(){const t=q.value.trim().toLowerCase();let v=0;
rows.forEach(r=>{const ok=(!k.value||r.dataset.k===k.value)&&(!c.value||r.dataset.c===c.value)&&(!t||r.textContent.toLowerCase().includes(t));r.hidden=!ok;if(ok)v++;});
n.textContent=v+' of '+rows.length+' sites';}
[q,k,c].forEach(x=>x.addEventListener('input',f));f();})();
</script>"""]
    (a.out / "index.html").write_text(HEAD.format(title="Sites · Compute Ledger", desc=e("Every site in the Compute Ledger, with what public records show.")) + "\n".join(idx) + "\n" + FOOT, encoding="utf-8")
    (a.out / "site.css").write_text(CSS, encoding="utf-8")
    # a retired id keeps its address: a short page that sends the reader to the site's current page
    aliases = {r["retired_site_id"]: r for r in read_csv(PKG / "site_id_aliases.csv")}
    for old, r in sorted(aliases.items()):
        new = e(r["site_id"])
        (a.out / f"{old}.html").write_text(
            HEAD.format(title="Moved · Compute Ledger", desc=e(f"{old} is now {r['site_id']}")).replace(
                '<link rel="stylesheet" href="site.css">', f'<link rel="stylesheet" href="site.css">\n<meta http-equiv="refresh" content="0; url={new}.html">\n<link rel="canonical" href="{new}.html">')
            + f'<nav class="top"><a href="../index.html">Compute Ledger</a> / <a href="index.html">Sites</a></nav>\n'
            f'<h1>This site has one page</h1><p>The id <code>{e(old)}</code> was retired: {e(r["reason"])}. '
            f'Its records are on <a href="{new}.html">{new}</a>.</p>\n' + FOOT, encoding="utf-8")
    stale = sorted(p.name for p in a.out.glob("*.html") if p.stem not in ids and p.stem not in aliases and p.name != "index.html")
    for name in stale:
        (a.out / name).unlink()
    print(f"wrote {len(index_rows)} site pages and the index to {a.out}" + (f"; removed {len(stale)} stale pages" if stale else ""))


if __name__ == "__main__":
    main()
