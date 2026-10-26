#!/usr/bin/env python3
"""Build the Compute Ledger page from registry/*.json files.

Reads every entries file (north_america.json, europe.json, ...) and sources.json,
validates the schema, and writes ledger.html. Data is embedded as JSON and rendered
client-side so the page can be filtered without a server. A correction suggested on
the page opens a public GitHub issue; corrections are reviewed into the registry by hand.
"""
import json, glob, os, re, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "registry")
OUT = os.path.join(ROOT, "site", "index.html")
GUIDE_FILE = os.path.join(HERE, "guide.json")
RECEIPTS_DIR = os.path.join(ROOT, "receipts")

ENTRY_FILES = [f for f in sorted(glob.glob(os.path.join(HERE, "*.json")))
               if not f.endswith(("sources.json", "guide.json", "standard.json"))]
SOURCES_FILE = os.path.join(HERE, "sources.json")

REQUIRED = ["id", "country", "site_or_subject", "category", "record", "gap", "confidence"]
CATS = ["power", "fuel", "water", "heat_reuse", "moratorium", "grid_policy", "minerals", "fab", "ewaste",
        "land_biodiversity", "community", "public_money", "labor", "circularity", "accounting"]

entries, problems = [], []
for f in ENTRY_FILES:
    try:
        data = json.load(open(f))
    except Exception as e:
        problems.append(f"{os.path.basename(f)}: cannot parse ({e})"); continue
    for e in data:
        missing = [k for k in REQUIRED if k not in e or e[k] in (None, "", [])]
        if missing:
            problems.append(f"{e.get('id','?')} ({os.path.basename(f)}): missing {missing}"); continue
        if e["category"] not in CATS:
            problems.append(f"{e['id']}: unknown category {e['category']}"); continue
        if not any(s.get("url") for s in e["record_sources"]) and not (
                e.get("verification_status") == "not_found" and e["record"].startswith("No record found yet")):
            problems.append(f"{e['id']}: no record source URL (an entry with no record says 'No record found yet' and is not_found)"); continue
        if e.get("verification_status") not in ("verified", "partial", "not_found"):
            problems.append(f"{e['id']}: verification_status must be verified, partial or not_found"); continue
        for _k in ("record_sources", "claim_sources"):
            for _s in e.get(_k) or []:
                _u = _s.get("url", "") if isinstance(_s, dict) else _s
                if not re.match(r"^https?://[^\s<>\"\\]+$", _u or ""):
                    problems.append(f"{e['id']}: {_k} URL is not well formed: {_u[:80]!r}")
        e["_file"] = os.path.basename(f).replace(".json", "")
        entries.append(e)

sources = []
if os.path.exists(SOURCES_FILE):
    try:
        sources = json.load(open(SOURCES_FILE))
    except Exception as e:
        problems.append(f"sources.json: cannot parse ({e})")

guide = json.load(open(GUIDE_FILE)) if os.path.exists(GUIDE_FILE) else []
STANDARD_FILE = os.path.join(HERE, "standard.json")
standard = json.load(open(STANDARD_FILE)) if os.path.exists(STANDARD_FILE) else None
ids = {e["id"] for e in entries}
if standard:
    for r in standard["requirements"]:
        for i in r["proven_by"]:
            if i not in ids: problems.append(f"standard {r['key']}: unknown entry id {i}")
for g in guide:
    for k in ("headline", "all"):
        for i in g.get(k, []):
            if i not in ids:
                problems.append(f"guide {g['key']}: unknown entry id {i}")

receipts = []
if os.path.isdir(RECEIPTS_DIR):
    for f in sorted(glob.glob(os.path.join(RECEIPTS_DIR, "*.json"))):
        try:
            r = json.load(open(f)); r["_slug"] = os.path.basename(f).replace(".json", ""); receipts.append(r)
        except Exception as e:
            problems.append(f"receipt {os.path.basename(f)}: cannot parse ({e})")

seen = set()
for e in entries:
    if e["id"] in seen: problems.append(f"duplicate id {e['id']}")
    seen.add(e["id"])

countries = sorted({e["country"] for e in entries} - {"Global", "European Union"})  # EU-wide and global entries are not countries
n_sources = len({x["url"].strip() for e in entries for x in (e["record_sources"] + (e.get("claim_sources") or [])) if not x.get("self") and x.get("url")})  # distinct documents
n_verified = sum(1 for e in entries if e.get("verification_status") == "verified")
# the page is dated by its data (the latest last_checked), not by the build day, so a rebuild on any day gives the same bytes
today = max((e.get("last_checked") or "") for e in entries) or "undated"

# checks run on the ledger and what they found (pipeline/build_checks.py)
REPO_URL = "https://github.com/kn0wledgebfre3-sys/compute-ledger/blob/main/"
CHK_DIR = os.path.join(ROOT, "data", "climate_trace_seed")
checks, chk_summary = [], {}
if os.path.exists(os.path.join(CHK_DIR, "checks.csv")):
    import csv as _csv
    with open(os.path.join(CHK_DIR, "checks.csv"), encoding="utf-8", newline="") as _f:
        checks = list(_csv.DictReader(_f))
    chk_summary = json.load(open(os.path.join(CHK_DIR, "checks_summary.json"), encoding="utf-8"))
    _names = {c["check_id"]: [c["name"], c["date"]] for c in checks}
    for e in entries:
        got = chk_summary.get("per_entry", {}).get(e["id"])
        if got:
            e["checks"] = [[_names[k][0], _names[k][1], n] for k, n in got.items() if k in _names]


def _h(x):
    return (str(x).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))


def checks_html():
    if not checks:
        return ""
    fs, ls = chk_summary["random_sample_figures"], chk_summary["random_sample_links"]
    v = fs["verdicts"]
    fl = "findings.csv"
    out = [f'<p class="prose">Every check run on the ledger is listed below: what was checked, how, by whom and what it found. The readers\' briefs and findings are kept in the repository as written, except that local file paths and the names of the fetch and search tools were replaced, and resolutions added. The four reviews written as prose give their counts here; every finding from the other checks is a row of <a href="{REPO_URL}data/climate_trace_seed/{fl}">{fl}</a>, with what the data show now, computed at each build (for the browser fetch and its check, the status recorded with the finding): whether the quoted text is still there, whether the figure is still in the table as checked, and on which side. Text no longer present or a figure no longer in its checked form means it changed, not necessarily that the finding was right. A check that finds nothing wrong is listed too.</p>']
    out.append(f'<div class="prose" style="border-left:3px solid var(--rule);padding-left:14px;margin-block:8px 14px"><p style="font-size:16px;margin:0"><b>Random samples.</b> {fs["n"]} figures drawn at random on four occasions and re-read in their documents: {v.get("found",0)} found with the value as published ({fs["found_with_another_problem_noted"]} of them with another problem noted, such as the period, basis or description), {v.get("found_different",0)} found with a different value, {v.get("not_in_document",0)} not in the cited document, and {v.get("unreachable",0)} whose document the reader could not reach. Of the {fs["differences"]} that differed or were missing, {fs["differences_no_longer_in_the_form_checked"]} are no longer in the table in the form checked and {fs["differences_still_as_checked"]} are as they were and remain open. {ls["n"]} chain links drawn at random: {ls["found_as_published"]} found as stated, {ls["differences"]} with a difference ({ls["differences_still_as_checked"]} still as checked). On 24 October a further 12 of the 178 benchmarking rows added that day were drawn at random and all were as published.</p></div>')
    rows = []
    for c in sorted(checks, key=lambda c: (c["date"], checks.index(c))):  # by date, then in the order the register lists them
        files = [x.strip() for x in c["findings_file"].split(";") if x.strip()]
        links = " ".join(f'<a href="{REPO_URL}{_h(x)}">{_h(x.split("/")[-1] if not x.endswith("/") else x)}</a>' for x in files)
        rows.append(f'<tr><td>{_h(c["date"])}</td><td><b>{_h(c["name"])}</b><br><span class="vnote">{_h(c["what_was_checked"])}. {_h(c["method"])}.</span></td><td>{_h(c["result"])}</td><td class="vnote">{_h(c["status_now"] or "counts in the review file")}<br>{links}</td></tr>')
    out.append('<div class="tabwrap"><table class="tl chktab"><thead><tr><th>Date</th><th>Check</th><th>What it found</th><th>Now, and where</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table></div>")
    return "\n".join(out)

def j(x):
    return json.dumps(x, ensure_ascii=False).replace("</", "<\\/")

page = r"""<title>Compute Ledger</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@75..100,400..800&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: a public-records ledger. A guided path at the top (pick what you care about → why it matters →
   what the record shows → what to ask), then a dot map, then the full ruled register of entries, receipts,
   the open-data catalog, and method. Colour is reserved for category marks. */
:root{
  --paper:#F4F6F3; --paper-2:#E9EDE8; --paper-3:#DFE5E0; --ink:#17211E; --ink-2:#4B5955; --rule:#C9D1CC;
  --accent:#1C6B5F; --accent-ink:#FFFFFF;
  --c-power:#B2481F; --c-fuel:#7A3B2E; --c-water:#1F6CA8; --c-heat:#2E8B57; --c-morat:#6B5B95;
  --c-grid:#8A6D1F; --c-min:#5C4A3A; --c-fab:#3F5B7A; --c-ew:#8C2D4F;
  --c-land:#4E7A2E; --c-comm:#9A4F9E; --c-money:#A3761A; --c-labor:#B04A5A; --c-circ:#1F7A74; --c-acct:#4A5A8C;
  --ok:#2E8B57; --warn:#B2481F;
  --display:"Archivo","Helvetica Neue",Arial,sans-serif;
  --body:"Source Serif 4",Georgia,"Times New Roman",serif;
  --mono:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --paper:#121816; --paper-2:#1A2320; --paper-3:#22302B; --ink:#E6ECE8; --ink-2:#A3B0AB; --rule:#2E3B36;
  --accent:#4FB3A3; --accent-ink:#0E1513;
  --c-power:#E07A4E; --c-fuel:#C9735F; --c-water:#5FA5E0; --c-heat:#5BC58A; --c-morat:#A292D6;
  --c-grid:#D0A94C; --c-min:#B8977C; --c-fab:#7FA0C6; --c-ew:#D66A90;
  --c-land:#8FC45E; --c-comm:#CF8FD3; --c-money:#D9AE4C; --c-labor:#E08090; --c-circ:#58BDB6; --c-acct:#9AA8D8;
  --ok:#5BC58A; --warn:#E07A4E; color-scheme:dark } }
:root[data-theme="dark"]{
  --paper:#121816; --paper-2:#1A2320; --paper-3:#22302B; --ink:#E6ECE8; --ink-2:#A3B0AB; --rule:#2E3B36;
  --accent:#4FB3A3; --accent-ink:#0E1513;
  --c-power:#E07A4E; --c-fuel:#C9735F; --c-water:#5FA5E0; --c-heat:#5BC58A; --c-morat:#A292D6;
  --c-grid:#D0A94C; --c-min:#B8977C; --c-fab:#7FA0C6; --c-ew:#D66A90;
  --c-land:#8FC45E; --c-comm:#CF8FD3; --c-money:#D9AE4C; --c-labor:#E08090; --c-circ:#58BDB6; --c-acct:#9AA8D8;
  --ok:#5BC58A; --warn:#E07A4E; color-scheme:dark }

*{box-sizing:border-box}
body{background:var(--paper);color:var(--ink);font-family:var(--body);font-size:17px;line-height:1.55;
  padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:0 64px}
a{color:var(--accent);text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:3px}
a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.wrap{max-width:1180px;margin:0 auto}
.prose{max-width:68ch}
h1,h2,h3,h4{font-family:var(--display);font-stretch:85%;text-wrap:balance;line-height:1.1;margin:0}
h1{font-size:clamp(40px,7vw,76px);font-weight:800;letter-spacing:-0.02em}
h2{font-size:clamp(24px,3.2vw,34px);font-weight:700;margin-block:56px 14px}
h3{font-size:19px;font-weight:700}
h4{font-size:15px;font-weight:700}
.eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2)}
.mono{font-family:var(--mono);font-size:13px}
p{margin:0 0 1em}
button{font:inherit;cursor:pointer}
.btn{font-family:var(--mono);font-size:12px;letter-spacing:.04em;border:1px solid var(--ink);background:var(--ink);color:var(--paper);padding:8px 14px;border-radius:4px}
.btn.ghost{background:transparent;color:var(--ink)}
.btn:disabled{opacity:.5;cursor:default}

header{padding-block:40px 24px}
.masthead{display:flex;flex-wrap:wrap;gap:24px 48px;align-items:flex-end;justify-content:space-between}
.counts{display:flex;gap:28px;flex-wrap:wrap;font-family:var(--display);font-stretch:85%}
.counts div{display:flex;flex-direction:column}
.counts b{font-size:36px;font-weight:800;line-height:1;font-variant-numeric:tabular-nums}
.counts span{font-family:var(--mono);font-size:12px;color:var(--ink-2);letter-spacing:.06em;text-transform:uppercase;margin-top:6px}
.lede{font-size:20px;max-width:62ch;margin-top:18px}

/* guided path */
.guide{border-top:1px solid var(--ink);padding-top:22px}
.guide .step{font-family:var(--mono);font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2);margin-bottom:10px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}
.tile{text-align:left;border:1px solid var(--rule);background:var(--paper-2);color:var(--ink);padding:14px 14px 12px;border-radius:4px;display:flex;flex-direction:column;gap:8px;min-height:112px;border-top:4px solid var(--cat)}
.tile b{font-family:var(--display);font-stretch:85%;font-weight:700;font-size:18px;line-height:1.1}
.tile span{font-size:14px;color:var(--ink-2);line-height:1.35}
.tile small{font-family:var(--mono);font-size:11px;color:var(--ink-2);margin-top:auto}
.tile[aria-pressed="true"]{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.tile[aria-pressed="true"] span,.tile[aria-pressed="true"] small{color:var(--paper);opacity:.8}
.panel{margin-top:18px;border:1px solid var(--rule);border-left:5px solid var(--cat);background:var(--paper-2);padding:22px 22px 18px;display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:18px 36px}
.panel h3{font-size:24px;margin-bottom:8px}
.panel .why p{font-size:17px}
.panel .ask{min-width:0}
.panel .ask ol{margin:8px 0 0;padding-left:20px;font-size:16px}
.panel .ask li{margin-bottom:8px}
.panel .ask li b{font-family:var(--display);font-stretch:90%}
.cases{grid-column:1/-1;display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px;margin-top:4px}
.case{background:var(--paper);border:1px solid var(--rule);border-radius:4px;padding:12px 14px;display:flex;flex-direction:column;gap:6px;text-align:left;color:var(--ink);min-width:0}
.case .w{font-family:var(--mono);font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2)}
.case .s{font-family:var(--display);font-stretch:85%;font-weight:700;font-size:16px;line-height:1.15}
.case .g{font-size:14px;color:var(--ink-2);line-height:1.4}
.case:hover{border-color:var(--accent)}
.panel .foot{grid-column:1/-1;display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-top:6px}
.places{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}

/* map */
.map{margin-top:28px;border:1px solid var(--rule);background:var(--paper-2);border-radius:4px;overflow:hidden}
.map svg{display:block;width:100%;height:auto;max-width:100%}
.map .grat{stroke:var(--rule);stroke-width:.6;fill:none}
.map .lbl{font-family:var(--mono);font-size:9px;fill:var(--ink-2);letter-spacing:.08em}
.map circle{stroke:var(--paper);stroke-width:1;cursor:pointer;transition:r .15s}
.map circle:hover{r:7}
.map circle.dim{opacity:.18}
.map-tip{font-family:var(--mono);font-size:12px;color:var(--ink-2);padding:8px 12px;border-top:1px solid var(--rule);min-height:36px}

/* filters */
.filters{display:flex;flex-wrap:wrap;gap:8px 10px;align-items:center;margin-block:20px 10px;position:sticky;top:env(safe-area-inset-top,0px);background:var(--paper);padding-block:10px;z-index:5;border-bottom:1px solid var(--rule)}
.chip{font-family:var(--mono);font-size:12px;letter-spacing:.04em;border:1px solid var(--rule);background:transparent;color:var(--ink);padding:6px 10px;border-radius:999px;cursor:pointer;display:inline-flex;gap:7px;align-items:center}
.chip .dot{width:9px;height:9px;border-radius:50%;background:var(--cat)}
.chip[aria-pressed="true"]{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.filters input,.filters select{font-family:var(--mono);font-size:13px;padding:7px 10px;border:1px solid var(--rule);background:var(--paper);color:var(--ink);border-radius:4px;min-width:0}
.filters input{flex:1 1 180px}
.filters .count{font-family:var(--mono);font-size:12px;color:var(--ink-2);margin-left:auto}

/* ledger rows */
.ledger{display:flex;flex-direction:column}
.row{display:grid;grid-template-columns:160px minmax(0,1fr);gap:8px 28px;padding-block:22px;border-bottom:1px solid var(--rule);scroll-margin-top:80px}
.row .meta{display:flex;flex-direction:column;gap:6px;min-width:0}
.row .where{font-family:var(--display);font-stretch:85%;font-weight:700;font-size:18px;line-height:1.15}
.row .cat{font-family:var(--mono);font-size:11px;letter-spacing:.06em;text-transform:uppercase;display:inline-flex;align-items:center;gap:7px;color:var(--ink-2)}
.row .cat::before{content:"";width:9px;height:9px;border-radius:50%;background:var(--cat)}
.row .main{min-width:0;display:flex;flex-direction:column;gap:10px}
.row .subject{font-family:var(--display);font-stretch:85%;font-weight:700;font-size:21px;line-height:1.15}
.row .op{font-family:var(--mono);font-size:12px;color:var(--ink-2)}
.field{display:grid;grid-template-columns:72px minmax(0,1fr);gap:12px;align-items:baseline}
.field .k{font-family:var(--mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2);padding-top:4px}
.field .v{min-width:0}
.field.gap .v{font-family:var(--display);font-stretch:90%;font-weight:600;font-size:16px}
.srcs{display:flex;flex-wrap:wrap;gap:6px 14px;margin-top:4px}
.srcs a{font-family:var(--mono);font-size:12px;text-decoration:none;border-bottom:1px solid var(--rule)}
.srcs a:hover{border-color:var(--accent)}
.conf{font-family:var(--mono);font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2)}
.conf b{font-weight:500;color:var(--ink)}
.tag{display:inline-block;font-family:var(--mono);font-size:10px;letter-spacing:.06em;text-transform:uppercase;border:1px solid var(--ok);color:var(--ok);padding:2px 6px;border-radius:3px;margin-top:2px}
.tag.part{border-color:var(--c-money);color:var(--c-money)}
.tag.no{border-color:var(--rule);color:var(--ink-2)}
.vnote{font-size:13px;color:var(--ink-2)}
.chk{margin-top:6px;font-family:var(--mono);font-size:11px;color:var(--ink-2)}
.chktab{width:100%;border-collapse:collapse;font-size:15px}
@media (max-width:700px){.tl.chktab thead{display:none}.tl.chktab tr{display:block;padding:10px 0;border-bottom:1px solid var(--rule)}.tl.chktab td{display:block;border:0;padding:2px 0}}
.pos .field.gap .v{color:var(--ok)}
.empty{padding:40px 0;color:var(--ink-2);font-family:var(--mono);font-size:13px}
.row .tools{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:4px}
.row .tools button{font-family:var(--mono);font-size:11px;letter-spacing:.04em;background:transparent;border:1px solid var(--rule);color:var(--ink-2);padding:4px 9px;border-radius:3px}
.row .tools button:hover{border-color:var(--accent);color:var(--accent)}
.pend{font-family:var(--mono);font-size:11px;color:var(--c-money)}
.cform{display:grid;gap:8px;border:1px solid var(--rule);background:var(--paper-2);padding:12px;border-radius:4px;margin-top:6px;max-width:640px}
.cform label{font-family:var(--mono);font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2);display:grid;gap:4px}
.cform input,.cform select,.cform textarea{font:inherit;font-size:14px;padding:7px 9px;border:1px solid var(--rule);background:var(--paper);color:var(--ink);border-radius:3px;min-width:0;width:100%}
.cform textarea{min-height:70px;resize:vertical}
.cform .act{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.cform .msg{font-family:var(--mono);font-size:12px;color:var(--ink-2)}

/* standard */
.std{display:flex;flex-direction:column;border-top:1px solid var(--ink)}
.req{display:grid;grid-template-columns:44px minmax(0,1fr);gap:6px 18px;padding-block:18px;border-bottom:1px solid var(--rule)}
.req .n{font-family:var(--mono);font-size:13px;color:var(--ink-2);padding-top:5px}
.req h3{font-size:20px;margin-bottom:6px}
.req .ask{font-size:16px}
.req .proof{font-family:var(--mono);font-size:12px;color:var(--ink-2);margin-top:6px}
.req .proof b{font-weight:500;color:var(--ink)}
.req .note{font-size:15px;color:var(--ink-2);margin-top:8px;max-width:72ch}
.req .by{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
.req .by button{font-family:var(--mono);font-size:11px;background:transparent;border:1px solid var(--rule);color:var(--ink);padding:4px 9px;border-radius:999px;text-align:left}
.req .by button:hover{border-color:var(--accent);color:var(--accent)}
.req .status{display:inline-block;font-family:var(--mono);font-size:10px;letter-spacing:.06em;text-transform:uppercase;padding:2px 7px;border-radius:3px;border:1px solid var(--rule);color:var(--ink-2);margin-left:8px;vertical-align:middle}
.req .status.met{border-color:var(--ok);color:var(--ok)}
.req .status.half{border-color:var(--c-money);color:var(--c-money)}

/* receipts */
.receipt{border:1px solid var(--rule);border-radius:4px;padding:20px 22px;background:var(--paper-2);display:grid;grid-template-columns:minmax(0,1fr);gap:12px}
.receipt .sum{font-size:17px}
.tl{width:100%;border-collapse:collapse;font-size:14px}
.tl th{font-family:var(--mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2);text-align:left;padding:6px 10px 6px 0;border-bottom:1px solid var(--ink)}
.tl td{padding:8px 10px 8px 0;border-bottom:1px solid var(--rule);vertical-align:top}
.tl td:first-child{font-family:var(--mono);font-size:12px;white-space:nowrap}
.receipt ul{margin:0;padding-left:18px;font-size:15px}
.receipt li{margin-bottom:6px}
details summary{cursor:pointer;font-family:var(--mono);font-size:12px;letter-spacing:.04em;color:var(--accent)}

/* sources table */
.srctab{width:100%;border-collapse:collapse;font-size:15px}
.srctab th{font-family:var(--mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2);text-align:left;padding:8px 10px 8px 0;border-bottom:1px solid var(--ink)}
.srctab td{padding:10px 10px 10px 0;border-bottom:1px solid var(--rule);vertical-align:top}
.srctab td:first-child{font-family:var(--display);font-stretch:85%;font-weight:700;min-width:160px}
.srctab .m{font-family:var(--mono);font-size:12px;color:var(--ink-2);white-space:nowrap}
.tabwrap{overflow-x:auto}
.srcgroup{margin-top:28px}
.srcgroup h3{margin-bottom:8px;display:flex;gap:10px;align-items:center}
.srcgroup h3 .dot{width:10px;height:10px;border-radius:50%;background:var(--cat)}

.method{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:28px 40px;margin-top:8px}
.method h3{margin-bottom:8px}
.method p{font-size:16px}
footer{margin-top:56px;padding-top:20px;border-top:1px solid var(--rule);font-family:var(--mono);font-size:12px;color:var(--ink-2)}
@media (max-width:720px){
  .row{grid-template-columns:1fr}
  .field{grid-template-columns:1fr;gap:4px}
  .masthead{align-items:flex-start}
  .panel{grid-template-columns:1fr}
}
@media (prefers-reduced-motion:reduce){ .map circle{transition:none} }
</style>

<div class="wrap">
<header>
  <div class="eyebrow">Public records of the physical, social and economic footprint of AI compute · compiled __TODAY__</div>
  <div class="masthead">
    <h1>Compute Ledger</h1>
    <div class="counts">
      <div><b>__N_ENTRIES__</b><span>entries</span></div>
      <div><b>__N_COUNTRIES__</b><span>countries and territories</span></div>
      <div><b>__N_SOURCES__</b><span>linked documents</span></div>
      <div><b>__N_DATASETS__</b><span>open datasets</span></div>
    </div>
  </div>
  <p class="lede">What permits, grid filings, court records, statistical offices, budgets and trade data say about where AI compute draws its power, burns its fuel, takes its water, uses its land, spends public money, employs people, and sends its hardware. Each entry lays the public record beside what the operator or government says in public, links every figure to the document it came from, and marks figures confirmed only through press reports of the document. The theme introductions and the standard are the ledger's own summaries of those entries. Good cases are entries too.</p>
  <p class="mono" style="margin-top:10px"><a href="https://kn0wledgebfre3-sys.github.io/compute-ledger/sites/">Every site, one page each</a> · <a href="https://kn0wledgebfre3-sys.github.io/compute-ledger/brief.html">Brief</a> · <a href="https://github.com/kn0wledgebfre3-sys/compute-ledger">Repository and data</a></p>
</header>

<section class="guide" id="guide">
  <div class="step">Start here · pick what you care about</div>
  <div class="tiles" id="tiles"></div>
  <div id="panel" hidden></div>
  <div class="step" style="margin-top:22px">Or pick a region or part of the chain</div>
  <div class="places" id="places"></div>
  <div class="map" id="map"></div>
</section>

<div id="standard-wrap" hidden>
<h2 id="standard">The standard</h2>
<p class="prose" id="std-intro"></p>
<div class="std" id="std-list"></div>
<p class="prose" id="std-closing" style="font-family:var(--display);font-stretch:90%;font-weight:600;font-size:18px;margin-top:18px"></p>
</div>

<h2 id="ledger-h">The ledger</h2>
<p class="prose">Every entry: what the record says, what is claimed, and the gap in one line. Filter by category, region or text. Where a correction has been submitted it shows on the entry until a newer document settles it.</p>
<div class="filters" id="filters">
  <input id="q" type="search" placeholder="Search country, site, operator, text" aria-label="Search entries">
  <select id="region" aria-label="Filter by region or part of the chain"><option value="">All regions and parts</option></select>
  <select id="vstat" aria-label="Filter by evidence"><option value="">Any evidence level</option><option value="high">High confidence only</option><option value="verified">Re-checked against primary</option><option value="weak">Not yet confirmed at source</option></select>
  <span id="chips"></span>
  <button class="btn ghost" id="clear" type="button" style="display:none">Clear</button>
  <span class="count" id="count"></span>
</div>
<section class="ledger" id="ledger" aria-live="polite"></section>

<div id="receipts-wrap" hidden>
<h2 id="receipts">Receipts</h2>
<p class="prose">A receipt is one case worked all the way down: the claim, the dated record and the gap, each figure tied to the document it came from, with [press] marking figures confirmed only through news reports of the document and [arithmetic] marking figures computed from two documented ones.</p>
<div id="receipts-list"></div>
</div>

<h2 id="sources">Where the records come from</h2>
<p class="prose">Open datasets anyone can pull without asking the industry. Grouped by what they reveal. The last column is the shortest route from the portal to a number.</p>
<div class="prose" style="border-left:3px solid var(--rule);padding-left:14px;margin-block:8px 4px">
  <h4 style="margin-bottom:6px">What is not published</h4>
  <p style="font-size:16px;margin-bottom:6px">Building scrapers for these sources showed where the public record stops:</p>
  <ul style="font-size:16px;margin:0;padding-left:18px">
    <li>Texas's grid operator publishes no file of its large-load queue. The totals appear only as numbers printed in monthly reports and board slides, with no breakdown by county or project.</li>
    <li>Great Britain's system operator stated in a freedom-of-information response that it does not keep a register of demand connections. The nearest public list covers only applicants who agreed to be listed.</li>
    <li>The EU's datacenter reporting database is behind an operator login. Only an aggregate report is public; there is no per-site data.</li>
    <li>Texas's environmental regulator lists datacenter air-permit applications only while they are pending, and the state's datacenter register (the Comptroller's tax-exemption list) has no addresses. Once a permit is issued, the generator inventory sits in a records system that needs a browser. The ledger rebuilt Texas from EPA's facility registry and TCEQ permit notices instead: 129 facilities, generator inventories for two.</li>
  </ul>
  <p style="font-size:16px;margin-top:8px">Scripts that pull the queues of PJM, MISO, SPP and NYISO, US federal plant and fuel data, and the British figures exist and pass offline tests; their live numbers will appear here once run. The Virginia DEQ permit extraction (all permits on the statewide list, read twice) was completed on 21 October 2026 and the Texas rebuild on 22 October; the Virginia figures are in the Virginia generator entry, and both are in the Climate TRACE handover package in the repository.</p>
</div>
<div id="srcs"></div>

<h2 id="checks">How it is checked</h2>
__CHECKS__

<h2 id="method">Method</h2>
<div class="method prose" style="max-width:none">
  <div><h3>What counts as a record</h3><p>A document produced by a regulator, court, grid operator, statistical office, auditor, UN body, customs authority, or a legally bound corporate filing. A company's sustainability report is a claim, not a record, unless a figure is third-party assured and the assurance statement is public.</p></div>
  <div><h3>What a gap means</h3><p>A one-line statement of where the record and the claim differ, written without adjectives. "None documented" means the record and the claim agree or no claim was found. "Positive example" means the record shows a practice worth copying.</p></div>
  <div><h3>Confidence and verification</h3><p>High means the record's figures were read in record holders' documents or a mirror of them. Medium means at least one key figure comes from a press report of a record, or the documents were only partly read; an entry whose content is a company's own statements is at most medium, however carefully it was transcribed. Low means the record rests mainly on press, NGO or company material. Every entry has had a second reading against its original documents, or carries a note of which could not be read (the last pass was an independent check on 24 October 2026); inside the record, [press: …], [NGO: …] and [study: …] mark what rests on a press report of a record, an NGO's documented finding or a study, and statements by companies and governments in their own voice are under Claim. 'Verified against primary' means the original confirmed the figures; 'partly verified' means it confirmed some but not a key figure; 'primary not found' means the note says what was searched and what was missing. Mirrors of the actual document (a law firm's copy of a regulator decision, a library copy of a UN report) count as primary; company press releases and law-firm summaries do not. Figures the ledger produced itself from public documents (the Virginia permit extraction) link to the extraction files, which link to each document.</p></div>
  <div><h3>What is excluded</h3><p>Estimates the ledger would have to make itself, modelled footprints, advocacy press releases cited on their own, and anything without a URL to the underlying document. Estimates published by a public body or the cited author (a market monitor's counterfactual, an auditor's projection, a grid operator's forecast, a tracking study's extrapolation) are included and labelled as estimates.</p></div>
  <div><h3>Corrections</h3><p>Anyone with contributor access can submit a correction on an entry with a source. The correct response to an entry is a newer document, not a rebuttal. Entries change when the record changes, and every entry carries a last-checked date. Every check the ledger has had, and every finding from them, is listed under How it is checked.</p></div>
  <div><h3>Scope</h3><p>Datacenters, the grids and water systems they sit on, the public money and land they use, and both ends of the hardware chain: the mines and fabs upstream, the recyclers and dumps downstream. Labor appears where a court or ministry has recorded it.</p></div>
</div>

<footer>Compiled from public sources as of __TODAY__. Entries are descriptions of documents, not findings of fact about any company. Coordinates are approximate and mark the county or region, not an exact address.</footer>
</div>

<script id="data" type="application/json">__DATA__</script>
<script>
(function(){
  const D = JSON.parse(document.getElementById('data').textContent);
  const E = D.entries, S = D.sources, G = D.guide, R = D.receipts;
  const byId = Object.fromEntries(E.map(e=>[e.id,e]));
  const CAT = {power:['Power','--c-power'],fuel:['Fuel','--c-fuel'],water:['Water','--c-water'],heat_reuse:['Heat reuse','--c-heat'],moratorium:['Moratorium','--c-morat'],grid_policy:['Grid policy','--c-grid'],minerals:['Minerals','--c-min'],fab:['Fabrication','--c-fab'],ewaste:['E-waste','--c-ew'],land_biodiversity:['Land & biodiversity','--c-land'],community:['Community','--c-comm'],public_money:['Public money','--c-money'],labor:['Labor','--c-labor'],circularity:['Circularity','--c-circ'],accounting:['Carbon accounting','--c-acct']};
  const REG = {north_america:'North America',europe:'Europe',asia_pacific:'Asia-Pacific',latam_mena_africa:'Latin America, Middle East, Africa',minerals_ewaste:'Minerals and e-waste',supply_chain:'Chips and the supply chain',people_land_money:'People, land, money',crypto_mining:'Crypto mining',nuclear:'Nuclear supply',paper_layer:'Reporting and certificates'};
  const esc = s => String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const state = {q:'',region:'',cats:new Set(),ids:null,theme:null,v:''};
  const corrections = {}; // entry id -> count

  /* ---------- guided path ---------- */
  const tiles = document.getElementById('tiles'), panel = document.getElementById('panel');
  G.forEach(g=>{
    const b=document.createElement('button');b.className='tile';b.type='button';b.setAttribute('aria-pressed','false');b.style.setProperty('--cat',`var(${g.color})`);
    const n = g.all.filter(i=>byId[i]).length;
    b.innerHTML=`<b>${esc(g.title)}</b><span>${esc(g.blurb)}</span><small>${n} entries</small>`;
    b.addEventListener('click',()=>{selectTheme(state.theme===g.key?null:g.key);});
    tiles.appendChild(b);
  });
  function selectTheme(key){
    state.theme=key;
    tiles.querySelectorAll('.tile').forEach((t,i)=>t.setAttribute('aria-pressed',String(G[i].key===key)));
    if(!key){panel.hidden=true;panel.innerHTML='';state.ids=null;render();return;}
    const g=G.find(x=>x.key===key);
    state.ids=new Set(g.all.filter(i=>byId[i]));state.cats.clear();state.region='';document.getElementById('region').value='';
    document.querySelectorAll('#chips .chip').forEach(c=>c.setAttribute('aria-pressed','false'));
    panel.style.setProperty('--cat',`var(${g.color})`);
    panel.innerHTML=`<div class="why"><h3>${esc(g.title)}</h3>${g.why.map(p=>`<p>${esc(p)}</p>`).join('')}</div>
      <div class="ask"><h4>What to ask, and where</h4><ol>${g.ask.map(a=>`<li><b>${esc(a[0])}</b> ${esc(a[1])}</li>`).join('')}</ol></div>
      <div class="cases">${g.headline.filter(i=>byId[i]).map(i=>{const e=byId[i];return `<button type="button" class="case" data-id="${esc(e.id)}"><span class="w">${esc(e.country)} · ${(CAT[e.category]||[e.category])[0]}</span><span class="s">${esc(e.site_or_subject)}</span><span class="g">${esc(e.gap)}</span></button>`;}).join('')}</div>
      <div class="foot"><button type="button" class="btn" id="seeall">See all ${state.ids.size} entries in the ledger</button><span class="mono" style="color:var(--ink-2)">The ledger below is now filtered to this theme.</span></div>`;
    panel.hidden=false;
    panel.querySelectorAll('.case').forEach(c=>c.addEventListener('click',()=>jump(c.dataset.id)));
    document.getElementById('seeall').addEventListener('click',()=>document.getElementById('ledger-h').scrollIntoView({behavior:'smooth'}));
    render();
  }
  function jump(id){const t=document.getElementById(id); if(!t){state.ids=null;state.theme=null;tiles.querySelectorAll('.tile').forEach(t=>t.setAttribute('aria-pressed','false'));panel.hidden=true;render();} const t2=document.getElementById(id); if(t2) t2.scrollIntoView({behavior:'smooth',block:'start'});}

  // places
  const places=document.getElementById('places');
  const regions=[...new Set(E.map(e=>e._file))];
  regions.forEach(r=>{const b=document.createElement('button');b.type='button';b.className='chip';b.setAttribute('aria-pressed','false');b.textContent=(REG[r]||r)+' · '+E.filter(e=>e._file===r).length;
    b.addEventListener('click',()=>{const on=state.region===r;state.region=on?'':r;document.getElementById('region').value=state.region;places.querySelectorAll('.chip').forEach(c=>c.setAttribute('aria-pressed','false'));if(!on)b.setAttribute('aria-pressed','true');render();if(!on)document.getElementById('ledger-h').scrollIntoView({behavior:'smooth'});});
    places.appendChild(b);});

  /* ---------- filters ---------- */
  const regSel = document.getElementById('region');
  regions.forEach(r=>{const o=document.createElement('option');o.value=r;o.textContent=REG[r]||r;regSel.appendChild(o);});
  regSel.addEventListener('change',()=>{state.region=regSel.value;places.querySelectorAll('.chip').forEach(c=>c.setAttribute('aria-pressed','false'));render();});
  document.getElementById('q').addEventListener('input',ev=>{state.q=ev.target.value.toLowerCase();render();});
  document.getElementById('vstat').addEventListener('change',ev=>{state.v=ev.target.value;render();});
  document.getElementById('clear').addEventListener('click',()=>{state.q='';state.region='';state.v='';state.cats.clear();document.getElementById('q').value='';regSel.value='';document.getElementById('vstat').value='';document.querySelectorAll('.chip').forEach(c=>c.setAttribute('aria-pressed','false'));selectTheme(null);});
  const chips = document.getElementById('chips');
  Object.entries(CAT).forEach(([k,[name,v]])=>{
    const n = E.filter(e=>e.category===k).length; if(!n) return;
    const b=document.createElement('button');b.type='button';b.className='chip';b.setAttribute('aria-pressed','false');b.style.setProperty('--cat',`var(${v})`);
    b.innerHTML=`<span class="dot"></span>${name} <span style="opacity:.6">${n}</span>`;
    b.addEventListener('click',()=>{if(state.cats.has(k))state.cats.delete(k);else state.cats.add(k);b.setAttribute('aria-pressed',String(state.cats.has(k)));render();});
    chips.appendChild(b);
  });

  function visible(){
    return E.filter(e=>{
      if(state.ids && !state.ids.has(e.id)) return false;
      if(state.region && e._file!==state.region) return false;
      if(state.cats.size && !state.cats.has(e.category)) return false;
      if(state.v==='high' && e.confidence!=='high') return false;
      if(state.v==='verified' && e.verification_status!=='verified') return false;
      if(state.v==='weak' && !(e.confidence!=='high' && e.verification_status!=='verified')) return false;
      if(state.q){const t=[e.country,e.region,e.site_or_subject,e.operator,e.record,e.claim,e.gap].join(' ').toLowerCase(); if(!t.includes(state.q)) return false;}
      return true;
    });
  }
  function srcs(list){ return (list||[]).filter(s=>s&&s.url).map(s=>`<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.title||s.publisher||s.url)}${s.publisher&&s.title?` · ${esc(s.publisher)}`:''}${s.date?` · ${esc(s.date)}`:(s.date_note?` · ${esc(s.date_note)}`:'')}</a>`).join(''); }
  function render(){
    const list = visible();
    const filtered = !!(state.ids||state.region||state.cats.size||state.q||state.v);
    document.getElementById('clear').style.display=filtered?'':'none';
    document.getElementById('count').textContent = `${list.length} of ${E.length}`;
    const L = document.getElementById('ledger');
    const vis=new Set(list.map(e=>e.id));
    document.querySelectorAll('#map circle').forEach(c=>c.classList.toggle('dim',filtered&&!vis.has(c.dataset.id)));
    if(!list.length){L.innerHTML='<div class="empty">No entries match. Clear a filter.</div>';return;}
    L.innerHTML = list.map(e=>{
      const [name,v]=CAT[e.category]||[e.category,'--ink-2'];
      const pos=/^positive/i.test(e.gap||'');
      const claim = e.claim && !/^none found/i.test(e.claim);
      const nc = corrections[e.id]||0;
      return `<article class="row${pos?' pos':''}" id="${esc(e.id)}" style="--cat:var(${v})">
        <div class="meta">
          <div class="where">${esc(e.country)}${e.region?`<br><span style="font-weight:400;color:var(--ink-2)">${esc(e.region)}</span>`:''}</div>
          <div class="cat">${name}</div>
          <div class="conf">confidence <b>${esc(e.confidence)}</b><br>checked ${esc(e.last_checked||'')}</div>
          ${({verified:'<span class="tag">verified against primary</span>',partial:'<span class="tag part">partly verified</span>',not_found:'<span class="tag no">primary not found</span>'})[e.verification_status]||''}
        </div>
        <div class="main">
          <div class="subject">${esc(e.site_or_subject)}</div>
          ${e.operator?`<div class="op">${esc(e.operator)}</div>`:''}
          <div class="field"><div class="k">Record</div><div class="v">${esc(e.record)}<div class="srcs">${srcs(e.record_sources)}</div></div></div>
          <div class="field"><div class="k">Claim</div><div class="v">${claim?esc(e.claim):'<span style="color:var(--ink-2)">None found</span>'}${claim?`<div class="srcs">${srcs(e.claim_sources)}</div>`:''}</div></div>
          <div class="field gap"><div class="k">Gap</div><div class="v">${esc(e.gap)}</div></div>
          ${e.verification_note?`<div class="field"><div class="k">Check</div><div class="v vnote">${esc(e.verification_note)}${e.checks?`<div class="chk">Checks that concern this entry: ${e.checks.map(c=>`${esc(c[0])} (${esc(c[1])}): ${c[2]}`).join(' · ')}. <a href="#checks">How it is checked</a></div>`:''}</div></div>`:''}
          <div class="tools">${e.receipt?`<button type="button" data-receipt="r-${esc(e.receipt)}" style="border-color:var(--accent);color:var(--accent)">Read the full receipt</button>`:''}<button type="button" data-fix="${esc(e.id)}">Suggest a correction</button>${nc?`<span class="pend">${nc} correction${nc>1?'s':''} pending</span>`:''}</div>
          <div class="cform" id="cf-${esc(e.id)}" hidden></div>
        </div></article>`;
    }).join('');
    L.querySelectorAll('[data-fix]').forEach(b=>b.addEventListener('click',()=>openForm(b.dataset.fix)));
    L.querySelectorAll('[data-receipt]').forEach(b=>b.addEventListener('click',()=>{const t=document.getElementById(b.dataset.receipt);if(t)t.scrollIntoView({behavior:'smooth',block:'start'});}));
  }

  /* ---------- corrections (GitHub issues) ---------- */
  function openForm(id){
    const box=document.getElementById('cf-'+id); if(!box) return;
    if(!box.hidden){box.hidden=true;return;}
    const gh='https://github.com/kn0wledgebfre3-sys/compute-ledger/issues/new?title='+encodeURIComponent('Correction: '+id)+'&body='+encodeURIComponent('Entry: '+id+'\nWhat is wrong (record, claim, gap line, source link, or a newer document):\nDocument URL:\nWhat the document says (figures and dates, no adjectives):\n');
    box.innerHTML=`<div class="msg">Send the correction as a public GitHub issue, with the document's URL: <a href="${gh}" target="_blank" rel="noopener">open a correction for this entry</a>. Corrections are reviewed into the registry by hand.</div>`;
    box.hidden=false;
  }

  /* ---------- map ---------- */
  (function map(){
    const W=1000,H=440, X=lon=>(lon+180)/360*W, Y=lat=>(90-lat)/180*H*0.98+4;
    let g='';
    for(let lon=-180;lon<=180;lon+=30) g+=`<line class="grat" x1="${X(lon)}" y1="0" x2="${X(lon)}" y2="${H}"/>`;
    for(let lat=-60;lat<=90;lat+=30) g+=`<line class="grat" x1="0" y1="${Y(lat)}" x2="${W}" y2="${Y(lat)}"/>`;
    const labels=[['NORTH AMERICA',-100,50],['SOUTH AMERICA',-60,-18],['EUROPE',15,60],['AFRICA',20,2],['MIDDLE EAST',45,20],['SOUTH ASIA',78,12],['EAST ASIA',112,45],['SOUTHEAST ASIA',112,-5],['OCEANIA',135,-30]];
    labels.forEach(([t,lo,la])=>{g+=`<text class="lbl" x="${X(lo)}" y="${Y(la)}" text-anchor="middle">${t}</text>`;});
    // spread dots that would sit on top of each other
    const placed=[];
    E.filter(e=>e.lat!=null&&e.lon!=null).forEach(e=>{
      const v=(CAT[e.category]||[0,'--ink-2'])[1];
      let cx=X(e.lon),cy=Y(e.lat),k=0;
      while(placed.some(p=>Math.hypot(p[0]-cx,p[1]-cy)<9)&&k<12){const a=k*2.4;cx=X(e.lon)+Math.cos(a)*(9+k*1.5);cy=Y(e.lat)+Math.sin(a)*(9+k*1.5);k++;}
      placed.push([cx,cy]);
      g+=`<circle data-id="${esc(e.id)}" cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="5" fill="var(${v})"><title>${esc(e.country)} · ${esc(e.site_or_subject)}</title></circle>`;
    });
    const m=document.getElementById('map');
    m.innerHTML=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Dot map of ledger entries by coordinates">${g}</svg><div class="map-tip" id="tip">Each dot is one entry. Hover or tap for the site; click to jump to it.</div>`;
    m.querySelectorAll('circle').forEach(c=>{
      const e=byId[c.dataset.id];
      c.addEventListener('mouseenter',()=>{document.getElementById('tip').textContent=`${e.country} · ${e.site_or_subject} · ${(CAT[e.category]||[e.category])[0]}`;});
      c.addEventListener('click',()=>jump(e.id));
    });
  })();

  /* ---------- standard ---------- */
  (function(){
    const ST=D.standard; if(!ST) return;
    document.getElementById('standard-wrap').hidden=false;
    document.getElementById('std-intro').textContent=ST.intro;
    document.getElementById('std-closing').textContent=ST.closing;
    const STATUS={disclose:'part',noise:'part',money:'part',hardware:'none'};
    document.getElementById('std-list').innerHTML=ST.requirements.map((r,i)=>`<div class="req" id="std-${esc(r.key)}">
      <div class="n">${String(i+1).padStart(2,'0')}</div>
      <div><h3>${esc(r.title)}<span class="status ${(STATUS[r.key]||'met')==='met'?'met':'half'}">${({met:'met somewhere',part:'met in part',none:'not yet met'})[STATUS[r.key]||'met']}</span></h3>
        <div class="ask">${esc(r.ask)}</div>
        <div class="proof"><b>Proof:</b> ${esc(r.proof)}</div>
        <div class="note">${esc(r.note)}</div>
        <div class="by">${r.proven_by.filter(id=>byId[id]).map(id=>`<button type="button" data-jump="${esc(id)}">${esc(byId[id].country)} · ${esc(byId[id].site_or_subject).slice(0,60)}${byId[id].site_or_subject.length>60?'…':''}</button>`).join('')}</div>
      </div></div>`).join('');
    document.querySelectorAll('#std-list [data-jump]').forEach(b=>b.addEventListener('click',()=>jump(b.dataset.jump)));
  })();

  /* ---------- receipts ---------- */
  (function(){
    if(!R.length) return;
    document.getElementById('receipts-wrap').hidden=false;
    document.getElementById('receipts-list').innerHTML=R.map(r=>`<article class="receipt" id="r-${esc(r._slug)}" style="scroll-margin-top:80px">
      <div><div class="eyebrow">${esc(r.jurisdiction||'')} · checked ${esc(r.last_checked||'')}</div><h3>${esc(r.title)}</h3></div>
      <p class="sum">${esc(r.summary)}</p>
      ${r.claim?`<div class="field"><div class="k">Claim</div><div class="v">${esc(r.claim.who)} · ${esc(r.claim.date)}: ${esc(r.claim.what)}${r.claim.url?` <a href="${esc(r.claim.url)}" target="_blank" rel="noopener" class="mono">source</a>`:''}</div></div>`:''}
      <div class="tabwrap"><table class="tl"><thead><tr><th>Date</th><th>Document</th><th>Figure</th><th>Where</th></tr></thead><tbody>
      ${(r.timeline||[]).map(t=>`<tr><td>${esc(t.date)}</td><td>${t.url?`<a href="${esc(t.url)}" target="_blank" rel="noopener">${esc(t.document)}</a>`:esc(t.document)}</td><td>${esc(t.figure)}</td><td class="mono" style="color:var(--ink-2)">${esc(t.locator||'')}</td></tr>`).join('')}
      </tbody></table></div>
      <div><h4>The gap</h4><ul>${(r.gaps||[]).map(x=>`<li>${esc(x)}</li>`).join('')}</ul></div>
      ${(r.limits||[]).length?`<details><summary>What the record does not show</summary><ul>${r.limits.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></details>`:''}
      ${(r.sources||[]).length?`<details><summary>All ${r.sources.length} sources</summary><div class="srcs" style="flex-direction:column;gap:6px;margin-top:8px">${srcs(r.sources)}</div></details>`:''}
      <p class="mono" style="color:var(--ink-2);margin:0">[press] marks a figure confirmed only through news reports of the document; [arithmetic] marks a figure computed from two documented figures.</p>
    </article>`).join('');
  })();

  /* ---------- sources ---------- */
  (function(){
    if(!S.length){document.getElementById('sources').hidden=true;document.getElementById('srcs').previousElementSibling.hidden=true;document.getElementById('srcs').hidden=true;return;}
    const groups={};
    S.forEach(s=>{(groups[s.category]=groups[s.category]||[]).push(s);});
    const NAMES={power:['Power and grid','--c-power'],air_permits:['Air permits (generator capacity)','--c-fuel'],water:['Water','--c-water'],planning:['Planning and zoning','--c-grid'],satellite:['Satellite imagery','--ink-2'],trade:['Trade and customs','--c-ew'],minerals:['Minerals','--c-min'],ewaste:['E-waste','--c-ew'],filings:['Corporate filings','--c-fab'],courts:['Courts and freedom of information','--c-morat'],heat_reuse:['Heat reuse','--c-heat'],verification:['Verification registries','--c-heat']};
    const order=Object.keys(NAMES).concat(Object.keys(groups).filter(k=>!NAMES[k]));
    document.getElementById('srcs').innerHTML = order.filter(k=>groups[k]).map(k=>{
      const [name,v]=NAMES[k]||[k,'--ink-2'];
      return `<div class="srcgroup" style="--cat:var(${v})"><h3><span class="dot"></span>${esc(name)} <span class="mono" style="color:var(--ink-2)">${groups[k].length}</span></h3>
      <div class="tabwrap"><table class="srctab"><thead><tr><th>Dataset</th><th>Scope</th><th>Reveals</th><th>Access</th><th>How to pull</th></tr></thead><tbody>
      ${groups[k].map(s=>`<tr><td><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.name)}</a><div class="m">${esc(s.publisher||'')}${s.verified===false?' · unverified':''}</div></td><td class="m" style="white-space:normal">${esc(s.country_or_scope||'')}</td><td>${esc(s.reveals||'')}</td><td class="m">${esc(s.format||'')} · ${esc(s.cost||'')}${s.update_frequency?`<br>${esc(s.update_frequency)}`:''}<br>${esc(s.scrape_difficulty||'')}</td><td style="font-size:14px">${esc(s.scrape_hint||'')}</td></tr>`).join('')}
      </tbody></table></div></div>`;
    }).join('');
  })();

  render();
  // a link such as index.html#<entry-id> (from the site pages) opens on that entry once the list is drawn
  if(location.hash.length>1){const t=document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if(t){t.style.scrollMarginTop='80px';t.scrollIntoView({block:'start'});}}
})();
</script>
"""

page = (page.replace("__TODAY__", today)
            .replace("__N_ENTRIES__", str(len(entries)))
            .replace("__N_COUNTRIES__", str(len(countries)))
            .replace("__N_SOURCES__", str(n_sources))
            .replace("__N_DATASETS__", str(len(sources)))
            .replace("__CHECKS__", checks_html())
            .replace("__DATA__", j({"entries": entries, "sources": sources, "guide": guide, "receipts": receipts, "standard": standard})))

open(OUT, "w").write(page)
# GitHub Pages serves docs/: the ledger at the site root and the brief beside it
DOCS = os.path.join(ROOT, "docs")
os.makedirs(DOCS, exist_ok=True)
_SKELETON = '<!doctype html>\n<html lang="en">\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
open(os.path.join(DOCS, "index.html"), "w").write(_SKELETON + page)
_brief = os.path.join(ROOT, "site", "brief.html")
if os.path.exists(_brief):
    open(os.path.join(DOCS, "brief.html"), "w").write(_SKELETON + open(_brief, encoding="utf-8").read())
open(os.path.join(DOCS, ".nojekyll"), "w").close()
print(f"wrote {OUT}: {len(entries)} entries ({n_verified} verified against primary), {len(countries)} countries and territories (+ EU-wide and global), {n_sources} distinct linked docs, {len(sources)} datasets, {len(guide)} themes, {len(receipts)} receipts")
if problems:
    print("PROBLEMS:"); [print(" -", p) for p in problems]
    sys.exit(1 if not entries else 0)
