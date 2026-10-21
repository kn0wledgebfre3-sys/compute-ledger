#!/usr/bin/env python3
"""Texas Comptroller data-center registrations -> TCEQ air permit packages -> tx_permits.csv

Inputs
------
* registry/seed_sites_unlocated.csv rows with admin_region == Texas (152 Comptroller registrations:
  name, effective date, owner / operator / occupant; NO address, NO county - the Comptroller's
  list does not give one, despite what older notes say - plus one TCEQ-sourced row).
* TCEQ application PDFs at
  https://www.tceq.texas.gov/assets/public/permitting/air/reports/applications/<project>-ac.pdf (administratively
  complete) or <project>-tc.pdf (technically complete). Title V projects have 5-digit ids (38509),
  NSR projects 6-digit ids (407086). Once a permit is issued the PDF stays at its URL but the row
  leaves the index pages below, so an issued permit can only be found by a known URL or a web search.

How the TCEQ PDFs are indexed (inspected with WebFetch on 2026-10-20)
---------------------------------------------------------------------
Two static HTML index pages, each an A-Z sectioned table (letter rows link "Back to top"):
  https://www.tceq.texas.gov/assets/public/permitting/air/reports/applications/titlev-pending-permits.html
      "Data Updated: 9/16/2026"; columns Applicant Name | Area Name | Permit Number | Received Date |
      Application Link (anchor text "Technically Complete Application" / "Administrative Complete
      Application", href = the PDF). ~300 rows. Data-center rows seen: CyrusOne LLC / Dfw10 Dfw11 Dfw17A..
      (40584-ac.pdf), Ie US Development Holdings 3 Inc. / Childress Data Center (40835-ac.pdf), Sharka LLC /
      Sharka Data Center (39571-ac.pdf), Vantage Data Centers TX11, LLC / Vantage Tx 11 (38602-tc.pdf).
  https://www.tceq.texas.gov/assets/public/permitting/air/reports/applications/nsr-pending-permits.html
      "Data Updated: 8/28/2026"; columns Applicant Name | Facility Name | Permit Number | Received Date |
      Application Link; applicant cells may also hold a "Plain Language Notice" link; permit numbers can
      be lists ("182126, GHGPSDTX263, PSDTX1688"). Data-center rows seen: ALIGNED DATA CENTERS REIT LLC /
      ADC PLANO (407086-tc.pdf), CRUSOE ENERGY SYSTEMS LLC / LONGHORN DATA CENTER (400428-tc.pdf) and
      GOODNIGHT DATA CENTER (404507-ac.pdf), NEXUS HUBBARD POWER, LLC / NEXUS DATA CENTER HUBBARD.
      Note AMAZONCOM SERVICES LLC - TXZ5 is a warehouse, not a data center: a hyperscaler name alone is
      not a match.
TCEQ Central Registry (https://www.tceq.texas.gov/goto/centralregistry -> www15.tceq.texas.gov/crpub) and
the air-permit database (https://www2.tceq.texas.gov/airperm/index.cfm, "pending and completed permits")
are robots-blocked for the fetch tool used tonight, so their forms were NOT inspected. --central-registry
turns on a best-effort client that reads the search form's field names at run time; treat its output as
untested.

What the PDFs contain: see permit_text.py. Coordinates come from the Core Data Form ("27. Latitude (N) In
Decimal: 29.480036 28. Longitude (W) In Decimal: -98.692555"), the STEERS site block ("Latitude (N)
(##.######) 32.537981"), OP-1 Section X (DMS) or, last resort, the "marker=lon,lat" map link in TCEQ's
letters. Generator inventory from Form OP-SUM rows ("2.5MW1-1 OP-UA2 SN1-1/ 3516C 2500KW GENERATOR-ENGINE").
Some packages list only emission groups (Alamo Mission: GRP-1..GRP-4A) or units without kW (Compass Red Oak:
EMGEN1..390) and one (CyrusOne 40584-ac.pdf) extracts as glyph garbage.

Matching rule (name only, since the register has no county): tokens of the Comptroller name, owner,
operator and occupant vs tokens of the TCEQ applicant + area/facility name, after dropping generic
words (data, center, llc, inc, texas, ...). A match needs a shared DISTINCTIVE token (not just
amazon/microsoft/google/oracle/coreweave/meta) or, for a hyperscaler-only match, a data-center-like area
name AND a unique Comptroller candidate. After download the package must say NAICS 518210 or "data
center" or the match is rejected (reason recorded). Rows with no match are written with nulls and a reason.

Outputs: tx_permits.csv, tx_permits_summary.json, tx_pdfs/, tx_text/, tx_index_rows.csv (both index pages).
"""

from __future__ import annotations

import csv
import re
import sys
import time
from pathlib import Path
from typing import Any

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C  # noqa: E402
import permit_text as PT  # noqa: E402
from va_deq_permits import parse_html_tables  # noqa: E402

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
BACKLOG_CSV = Path(__file__).resolve().parent.parent / "sites" / "seed_sites_unlocated.csv"
COMPTROLLER_URL = "https://comptroller.texas.gov/taxes/data-centers/data-center-lists.php"
TITLEV_INDEX = "https://www.tceq.texas.gov/assets/public/permitting/air/reports/applications/titlev-pending-permits.html"
NSR_INDEX = "https://www.tceq.texas.gov/assets/public/permitting/air/reports/applications/nsr-pending-permits.html"
CR_SEARCH = "https://www15.tceq.texas.gov/crpub/index.cfm?fuseaction=regent.RNSearch"
REQUEST_PAUSE = 1.5

GENERIC = {
    "data", "center", "centers", "centre", "datacenter", "datacenters", "llc", "l", "c", "inc", "corp", "corporation",
    "co", "company", "lp", "ltd", "limited", "the", "of", "and", "texas", "tx", "holdings", "holding", "group",
    "services", "service", "america", "americas", "management", "propco", "opco", "site", "campus", "project",
    "dc", "i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "per", "owner", "operator", "partners",
    "investments", "properties", "property", "development", "clean", "energy", "power", "reit", "fund", "cloud",
    "technologies", "technology", "systems", "us", "usa", "global", "international", "acquisition", "compute",
    "hardware", "financing", "lot", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12",
    # region labels and big-city names: shared by unrelated operators, so never evidence on their own
    "dfw", "sat", "aus", "hou", "iah", "san", "antonio", "dallas", "houston", "austin", "fort", "worth", "el", "paso",
    "north", "south", "east", "west", "central",
}
HYPERSCALERS = {"amazon", "amazoncom", "microsoft", "google", "oracle", "coreweave", "meta", "apple", "design", "lambda", "aws"}
DC_LIKE_RE = re.compile(r"data\s*cent|datacent|\bdc\b|hyperscale|campus", re.IGNORECASE)


def tokens(s: str) -> set[str]:
    s = (s or "").lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    words = s.split()
    toks = set()
    for i, t in enumerate(words):
        toks.add(t)
        m = re.fullmatch(r"([a-z]+)(\d+)", t)  # "dfw10" -> dfw, 10, dfw10
        if m:
            toks.add(m.group(1))
            toks.add(m.group(2).lstrip("0") or "0")
            toks.add(m.group(1) + (m.group(2).lstrip("0") or "0"))
        if i + 1 < len(words) and t.isalpha() and words[i + 1].isdigit():  # "tx 11" -> tx11
            toks.add(t + (words[i + 1].lstrip("0") or "0"))
    return toks


def distinctive(toks: set[str]) -> set[str]:
    return {t for t in toks if t not in GENERIC and not t.isdigit() and len(t) > 1}


REGIONS = {"dfw": {"dfw", "dallas", "worth", "irving", "plano", "richardson", "garland", "lancaster", "midlothian", "red", "oak", "hutto"},
           "sat": {"sat", "antonio"}, "aus": {"aus", "austin", "hutto", "taylor", "pflugerville", "round", "rock"},
           "hou": {"hou", "houston", "iah"}, "abi": {"abilene"}, "odessa": {"odessa", "midland"}, "chi": {"childress"},
           "lbb": {"lbb", "lubbock", "abernathy"}, "elp": {"elp", "paso"}, "temple": {"temple", "belton"}, "waco": {"waco"}}


def regions(toks: set[str]) -> set[str]:
    return {r for r, aliases in REGIONS.items() if toks & aliases}


def codes(toks: set[str]) -> set[str]:
    """Facility codes such as tx11, sat14, dfw10, holdings3: sibling sites differ only by these."""
    return {t for t in toks if re.fullmatch(r"[a-z]{2,10}\d{1,3}", t) and t not in GENERIC}


# --------------------------------------------------------------------------------------
# Inputs
# --------------------------------------------------------------------------------------


def load_comptroller_rows(path: Path) -> list[dict[str, Any]]:
    rows = []
    for r in csv.DictReader(open(path, encoding="utf-8")):
        if r.get("admin_region") != "Texas":
            continue
        oo = r.get("operator_or_owner") or ""
        owner = operator = ""
        m = re.search(r"owner:\s*(.*?);\s*operator:\s*(.*)$", oo)
        if m:
            owner, operator = m.group(1).strip(), m.group(2).strip()
        else:
            operator = oo
        rows.append({
            "backlog_id": r["backlog_id"], "comptroller_name": r["name"], "owner": owner, "operator": operator,
            "occupant": r.get("occupant_or_tenant") or "", "record_date": r.get("record_date"),
            "register": r.get("register"), "locality_register": r.get("locality") or "", "record_id_register": r.get("record_id") or "",
            "generator_info_register": r.get("generator_info") or "", "source_url": r.get("source_url") or COMPTROLLER_URL,
        })
    return rows


def load_known_documents() -> list[dict[str, Any]]:
    p = FIXTURES / "tx_known_documents.csv"
    return list(csv.DictReader(open(p, encoding="utf-8"))) if p.exists() else []


def parse_index(page: str, which: str) -> list[dict[str, Any]]:
    """Rows of a TCEQ pending-permits index page. Letter-divider rows are skipped."""
    from urllib.parse import urljoin

    base = TITLEV_INDEX if which == "titlev" else NSR_INDEX
    out = []
    for t in parse_html_tables(page):
        if not t:
            continue
        head = [c["text"].lower() for c in t[0]]
        if not any("applicant" in h for h in head):
            continue
        for row in t[1:]:
            if len(row) < 5:
                continue
            links = [urljoin(base, l) for l in row[4]["links"] if "/applications/" in l]
            if not links:
                continue
            applicant = re.sub(r"\s*Plain Language Notice\s*$", "", row[0]["text"]).strip()
            out.append({
                "index": which, "applicant": applicant, "area_name": row[1]["text"], "permit_number": row[2]["text"],
                "received_date": PT.us_date_to_iso(row[3]["text"]), "application_type": row[4]["text"],
                "application_url": links[0],
            })
    m = re.search(r"Data Updated:\s*(\d{1,2}/\d{1,2}/\d{4})", page)
    for r in out:
        r["index_data_updated"] = PT.us_date_to_iso(m.group(1)) if m else None
    return out


# --------------------------------------------------------------------------------------
# Matching
# --------------------------------------------------------------------------------------


def score_match(comp: dict[str, Any], idx: dict[str, Any]) -> dict[str, Any]:
    comp_strings = [comp["comptroller_name"], comp["owner"], comp["operator"], comp["occupant"]]
    ctoks = set().union(*(tokens(s) for s in comp_strings))
    atoks = tokens(idx["applicant"])
    itoks = atoks | tokens(idx["area_name"])
    shared = distinctive(ctoks) & distinctive(itoks)
    shared_non_hyper = shared - HYPERSCALERS
    ccodes, icodes = codes(ctoks), codes(itoks)
    shared_words = {t for t in shared_non_hyper if t not in ccodes}  # codes (dfw10, tx11) are not evidence by themselves
    shared_applicant = shared_words & distinctive(atoks)
    code_conflict = bool(ccodes) and bool(icodes) and not (ccodes & icodes)
    creg, ireg = regions(ctoks), regions(itoks)
    if creg and ireg and not (creg & ireg):
        code_conflict = True  # same company, different metro (CyrusOne Houston vs CyrusOne DFW)
    denom = max(1, min(len(distinctive(ctoks) - HYPERSCALERS), len(distinctive(itoks) - HYPERSCALERS)))
    dc_like = bool(DC_LIKE_RE.search(idx["area_name"] or "") or DC_LIKE_RE.search(idx["applicant"] or ""))
    if not shared_words:
        strength = "hyper_only" if (shared and dc_like) else "none"
    elif code_conflict:
        strength = "code_conflict"
    elif len(shared_words) >= 2 or (shared_applicant and dc_like):
        strength = "strong"
    elif shared_applicant:
        strength = "unverified"  # one shared company word, TCEQ names do not say data center: NAICS check after download
    elif dc_like:
        strength = "weak_area"  # the only shared word is in a data-center-like TCEQ area name (often a place name)
    else:
        strength = "none"
    return {"shared": sorted(shared), "shared_non_hyper": sorted(shared_non_hyper), "shared_codes": sorted(ccodes & icodes),
            "score": round(len(shared_words) / denom, 3), "strength": strength, "dc_like_area": dc_like}


def match_rows(comp_rows: list[dict[str, Any]], idx_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """backlog_id -> chosen index row (+ match meta).

    strong:      a distinctive token shared with the TCEQ applicant name (or >= 2 shared tokens)
    weak_area:   only a word in the TCEQ area/facility name is shared (place names: Childress, Goodnight);
                 extracted, but merge_to_handover does not trust its coordinates unless told to
    hyper_only:  only amazon/microsoft/google/... shared; accepted as weak only when the area name looks like
                 a data center and no other registration competes for that index row
    code_conflict: facility codes differ (TX21 vs TX11, Holdings 7 vs Holdings 3): never matched
    """
    cands: dict[str, list[tuple[dict, dict]]] = {}
    for comp in comp_rows:
        for idx in idx_rows:
            s = score_match(comp, idx)
            if s["strength"] in ("strong", "unverified"):
                cands.setdefault(comp["backlog_id"], []).append((idx, s))
            elif s["strength"] == "weak_area":
                cands.setdefault(comp["backlog_id"], []).append((idx, s))
            elif s["strength"] == "hyper_only" and s["dc_like_area"]:
                cands.setdefault(comp["backlog_id"], []).append((idx, s))
    idx_users: dict[str, set[str]] = {}
    for bid, lst in cands.items():
        for idx, s in lst:
            idx_users.setdefault(idx["application_url"], set()).add(bid)
    rank = {"strong": 3, "unverified": 2, "weak_area": 1, "hyper_only": 0}
    chosen = {}
    for bid, lst in cands.items():
        lst.sort(key=lambda x: (rank[x[1]["strength"]], len(x[1]["shared_non_hyper"]), len(x[1]["shared_codes"]), x[1]["score"]), reverse=True)
        idx, s = lst[0]
        if s["strength"] == "hyper_only" and len(idx_users[idx["application_url"]]) > 1:
            chosen[bid] = {"ambiguous": True, "candidates": [i["application_url"] for i, _ in lst], "meta": s}
            continue
        method = {"strong": f"{idx['index']}_index", "unverified": f"{idx['index']}_index_unverified", "weak_area": f"{idx['index']}_index_weak_area",
                  "hyper_only": f"{idx['index']}_index_weak_hyperscaler"}[s["strength"]]
        chosen[bid] = {"ambiguous": False, "idx": idx, "meta": s, "method": method}
    return chosen


# --------------------------------------------------------------------------------------
# Central Registry (opt-in, untested: the form could not be inspected tonight)
# --------------------------------------------------------------------------------------


def central_registry_lookup(name: str, session) -> dict[str, Any] | None:
    """Best effort: GET the search form, find text inputs whose name mentions 'name', POST the company
    name, follow RN links on the result page and regex lat/long + address from the detail page."""
    from html.parser import HTMLParser

    class FormParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.forms: list[dict[str, Any]] = []

        def handle_starttag(self, tag, attrs):
            a = dict(attrs)
            if tag == "form":
                self.forms.append({"action": a.get("action"), "method": (a.get("method") or "get").lower(), "fields": {}})
            elif tag in ("input", "select") and self.forms:
                if a.get("name"):
                    self.forms[-1]["fields"][a["name"]] = a.get("value", "")

    try:
        r = session.get(CR_SEARCH, timeout=60)
        fp = FormParser()
        fp.feed(r.text)
        form = next((f for f in fp.forms if any("name" in k.lower() for k in f["fields"])), None)
        if not form:
            return {"error": "search form not recognised; inspect " + CR_SEARCH}
        data = dict(form["fields"])
        for k in data:
            if "name" in k.lower() and "type" not in k.lower():
                data[k] = name
        from urllib.parse import urljoin

        action = urljoin(CR_SEARCH, form["action"] or CR_SEARCH)
        r2 = session.post(action, data=data, timeout=60) if form["method"] == "post" else session.get(action, params=data, timeout=60)
        links = re.findall(r'href="([^"]*(?:re_id|RN\d{9})[^"]*)"', r2.text)
        if not links:
            return {"error": "no RN result links"}
        r3 = session.get(urljoin(action, links[0].replace("&amp;", "&")), timeout=60)
        txt = re.sub(r"<[^>]+>", "\n", r3.text)
        coords = PT.extract_tx_coordinates(txt)
        rn = PT.RN_RE.search(txt)
        return {"rn": "RN" + rn.group(1) if rn else None, **coords, "detail_url": r3.url}
    except Exception as exc:  # noqa: BLE001
        return {"error": f"{type(exc).__name__}: {exc}"[:200]}


# --------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------

OUT_COLUMNS = [
    "backlog_id", "comptroller_name", "owner", "operator", "occupant", "record_date", "register", "match_method",
    "match_applicant", "match_area_name", "match_shared_tokens", "match_score", "tceq_permit_no", "tceq_project_id",
    "application_url", "application_type", "received_date", "pdf_status", "text_quality", "regulated_entity_name",
    "site_name", "rn", "cn", "street", "city", "zip", "county", "naics", "is_datacenter_naics", "lat", "lon",
    "coord_source", "coord_confidence", "generator_count", "generator_count_confidence", "unit_kw_list", "unit_kw_min",
    "unit_kw_max", "total_standby_mw", "total_standby_mw_min", "total_standby_mw_max", "total_mw_confidence",
    "generator_inventory_source", "fuel", "fuel_confidence", "hours_all_purpose_per_year", "hours_maint_per_year",
    "submittal_date", "reason", "source_url", "retrieved_at",
]


def text_for(key: str, url: str, args, out_dir: Path) -> tuple[str | None, str]:
    cached = out_dir / "tx_text" / f"{key}.txt"
    if cached.exists() and not args.refresh:
        return cached.read_text(encoding="utf-8"), "cached_text"
    if args.fixture:
        fx = FIXTURES / "tx_applications" / f"{key}.txt"
        if fx.exists():
            return fx.read_text(encoding="utf-8"), "fixture_text"
        return None, "no_fixture_text"
    dest = out_dir / "tx_pdfs" / f"{key}.pdf"
    if not dest.exists() or args.refresh:
        try:
            f = C.fetch(url, expect="pdf", landing_page=TITLEV_INDEX)
        except C.SourceError as exc:
            C.log(f"  {key}: {type(exc).__name__}: {str(exc)[:160]}")
            return None, f"download_failed:{type(exc).__name__}"
        C.write_bytes(f.content, dest)
        time.sleep(REQUEST_PAUSE)
    text = PT.pdf_to_text(dest)
    C.write_bytes(text.encode("utf-8"), cached)
    return text, "downloaded"


def main() -> None:
    ap = C.base_parser(__doc__)
    ap.add_argument("--backlog", type=Path, default=BACKLOG_CSV)
    ap.add_argument("--central-registry", action="store_true", help="also query TCEQ Central Registry by name (UNTESTED client)")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--refresh", action="store_true")
    args = ap.parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    retrieved_at = None if args.fixture else time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    comp_rows = load_comptroller_rows(args.backlog)
    if args.limit:
        comp_rows = comp_rows[: args.limit]
    C.log(f"{len(comp_rows)} Texas rows from {args.backlog}")

    # index pages
    idx_rows: list[dict[str, Any]] = []
    sources = []
    for which, url, fx in (("titlev", TITLEV_INDEX, "tx_pending_titlev.html"), ("nsr", NSR_INDEX, "tx_pending_nsr.html")):
        if args.fixture:
            page = (FIXTURES / fx).read_text(encoding="utf-8")
        else:
            try:
                page = C.fetch(url, expect="html").text()
                C.write_bytes(page.encode("utf-8"), out_dir / fx)
            except C.SourceError as exc:
                C.log(f"WARNING: {which} index unavailable: {exc}")
                sources.append({"name": f"TCEQ {which} pending index", "url": url, "error": str(exc)[:200]})
                continue
        rows = parse_index(page, which)
        if not rows:
            raise C.SchemaChangedError(f"TCEQ {which} index at {url}: no applicant table with application links found; layout changed?")
        idx_rows.extend(rows)
        sources.append({"name": f"TCEQ {which} pending index", "url": url, "rows": len(rows), "data_updated": rows[0]["index_data_updated"]})
        C.log(f"{which} index: {len(rows)} rows (data updated {rows[0]['index_data_updated']})")
    C.write_csv(pd.DataFrame(idx_rows), out_dir / "tx_index_rows.csv")

    known = load_known_documents()
    chosen = match_rows(comp_rows, idx_rows)
    session = None
    if args.central_registry and not args.fixture:
        import requests

        session = requests.Session()
        session.headers["User-Agent"] = C.USER_AGENT

    records = []
    for i, comp in enumerate(comp_rows, 1):
        rec = {k: None for k in OUT_COLUMNS}
        rec.update({k: comp.get(k) for k in ("backlog_id", "comptroller_name", "owner", "operator", "operator", "occupant", "record_date", "register", "source_url")})
        rec["retrieved_at"] = retrieved_at
        url = None
        # 1. known documents: comptroller_match is a regex tested against the backlog_id and the Comptroller name
        for k in known:
            pat = (k.get("comptroller_match") or "").strip()
            if pat and (re.search(pat, comp["backlog_id"], re.IGNORECASE) or re.search(pat, comp["comptroller_name"], re.IGNORECASE)):
                url = k["application_url"]
                rec.update({"match_method": "known_documents", "match_applicant": k["applicant"], "match_area_name": k["area_name"],
                            "tceq_permit_no": k["tceq_permit_no"], "tceq_project_id": k["project_id"], "match_shared_tokens": k["found_via"]})
                break
        # 2. index match
        if not url and comp["backlog_id"] in chosen:
            ch = chosen[comp["backlog_id"]]
            if ch["ambiguous"]:
                rec["match_method"] = "ambiguous"
                rec["reason"] = "hyperscaler name only; index row also fits other registrations: " + "; ".join(ch["candidates"][:3])
            else:
                idx = ch["idx"]
                url = idx["application_url"]
                rec.update({"match_method": ch["method"], "match_applicant": idx["applicant"], "match_area_name": idx["area_name"],
                            "match_shared_tokens": ",".join(ch["meta"]["shared"]), "match_score": ch["meta"]["score"],
                            "tceq_permit_no": idx["permit_number"], "application_type": idx["application_type"],
                            "received_date": idx["received_date"]})
        if url:
            rec["application_url"] = url
            m = re.search(r"/applications/(\d+)-(ac|tc)\.pdf", url)
            rec["tceq_project_id"] = rec["tceq_project_id"] or (m.group(1) if m else None)
            key = f"{m.group(1)}-{m.group(2)}" if m else re.sub(r"\W+", "_", url)[-40:]
            text, status = text_for(key, url, args, out_dir)
            rec["pdf_status"] = status
            if text is None:
                rec["text_quality"] = "none"
                rec["reason"] = f"application PDF not read ({status})"
            else:
                q = PT.text_quality(text)
                rec["text_quality"] = q
                if q != "ok":
                    rec["reason"] = f"PDF text {q}: font encoding broken; needs OCR or manual reading"
                else:
                    ext = PT.extract_tx_fields(text)
                    ext.update(PT.extract_fuel(text))
                    ext.update(PT.extract_hours(text))
                    rec.update({k: v for k, v in ext.items() if k in rec})
                    dc_ok = ext.get("is_datacenter_naics") or bool(re.search(r"data\s*cent", text[:60000], re.IGNORECASE))
                    if not dc_ok and rec["match_method"] != "known_documents":
                        rec["reason"] = "name matched but package is not a data center (no NAICS 518210 / 'data center' in text); fields cleared"
                        for k in ("lat", "lon", "coord_source", "generator_count", "total_standby_mw", "unit_kw_list", "street", "city", "zip", "county"):
                            rec[k] = None
                        rec["coord_confidence"] = "none"
                    else:
                        notes = []
                        if rec["lat"] is None:
                            notes.append("no coordinates in package text")
                        if rec["generator_count"] is None:
                            notes.append("generator units not itemised (groups only)" if ext.get("generator_inventory_source") == "op_sum_groups_only" else "no generator inventory recognised")
                        elif rec["total_standby_mw"] is None:
                            notes.append("unit kW not stated in OP-SUM descriptions")
                        rec["reason"] = "; ".join(notes) or None
        elif not rec["reason"]:
            rec["match_method"] = "none"
            rec["reason"] = "no TCEQ application matched by name on the pending Title V/NSR indexes; permit may be issued (off the index) or under another entity name"
        # address/identifiers already carried by the register row (e.g. the TCEQ statement-of-basis row)
        if rec["street"] is None and comp["locality_register"]:
            am = re.match(r"\s*(\d+[^,]+),\s*([A-Za-z .]+?)(?:,\s*([A-Za-z .]+County))?\s*$", comp["locality_register"])
            if am:
                rec["street"], rec["city"] = am.group(1).strip(), am.group(2).strip()
                rec["county"] = rec["county"] or (am.group(3).replace(" County", "").strip() if am.group(3) else None)
                rec["reason"] = ((rec["reason"] + "; ") if rec["reason"] else "") + "street address taken from the register row (not from a PDF)"
            if rec["rn"] is None:
                rm = PT.RN_RE.search(comp["record_id_register"] or "")
                rec["rn"] = "RN" + rm.group(1) if rm else None
        # 3. Central Registry (opt-in)
        if session is not None and rec["lat"] is None:
            for nm in (comp["comptroller_name"], comp["owner"], comp["operator"]):
                if not nm:
                    continue
                cr = central_registry_lookup(nm, session)
                time.sleep(2.0)
                if cr and cr.get("lat"):
                    rec.update({"lat": cr["lat"], "lon": cr["lon"], "coord_source": "central_registry", "coord_confidence": "medium",
                                "rn": rec["rn"] or cr.get("rn")})
                    rec["match_method"] = (rec["match_method"] or "none") + "+central_registry"
                    rec["reason"] = (rec["reason"] or "") + f"; Central Registry hit for {nm!r} ({cr.get('detail_url')}) - verify it is the data center"
                    break
                if cr and cr.get("error"):
                    rec["reason"] = (rec["reason"] or "") + f"; central registry: {cr['error']}"
                    break
        for k in ("coord_confidence", "generator_count_confidence", "total_mw_confidence", "fuel_confidence"):
            rec[k] = rec[k] or "none"
        records.append(rec)
        C.log(f"[{i}/{len(comp_rows)}] {comp['comptroller_name'][:40]!r}: {rec['match_method']} {rec['lat']},{rec['lon']} "
              f"{rec['generator_count']} gens {rec['total_standby_mw']} MW; {rec['reason'] or ''}")

    df = pd.DataFrame(records, columns=OUT_COLUMNS)
    C.write_csv(df, out_dir / "tx_permits.csv")

    # Data-center-looking TCEQ packages that matched no Comptroller row: real Texas sites too, kept separately
    used = set(df["application_url"].dropna())
    extra_rows = []
    extra_urls = {}
    for idx in idx_rows:
        if idx["application_url"] not in used and DC_LIKE_RE.search(idx["applicant"] + " " + idx["area_name"]):
            extra_urls.setdefault(idx["application_url"], {"applicant": idx["applicant"], "area_name": idx["area_name"],
                                                           "tceq_permit_no": idx["permit_number"], "source": f"{idx['index']}_index"})
    for k in known:
        if k["application_url"] not in used and not (k.get("comptroller_match") or "").strip():
            extra_urls.setdefault(k["application_url"], {"applicant": k["applicant"], "area_name": k["area_name"],
                                                         "tceq_permit_no": k["tceq_permit_no"], "source": "known_documents"})
    for url, info in extra_urls.items():
        m = re.search(r"/applications/(\d+)-(ac|tc)\.pdf", url)
        key = f"{m.group(1)}-{m.group(2)}" if m else re.sub(r"\W+", "_", url)[-40:]
        text, status = text_for(key, url, args, out_dir)
        row = {"application_url": url, "tceq_project_id": m.group(1) if m else None, "pdf_status": status, **info}
        if text is not None:
            q = PT.text_quality(text)
            row["text_quality"] = q
            if q == "ok":
                ext = PT.extract_tx_fields(text)
                row.update({k: ext.get(k) for k in ("regulated_entity_name", "site_name", "rn", "street", "city", "zip", "county", "naics",
                                                     "lat", "lon", "coord_source", "coord_confidence", "generator_count", "unit_kw_list",
                                                     "total_standby_mw", "total_mw_confidence")})
        else:
            row["text_quality"] = "none"
        extra_rows.append(row)
    extra_cols = ["application_url", "tceq_project_id", "source", "applicant", "area_name", "tceq_permit_no", "pdf_status", "text_quality",
                  "regulated_entity_name", "site_name", "rn", "street", "city", "zip", "county", "naics", "lat", "lon", "coord_source",
                  "coord_confidence", "generator_count", "unit_kw_list", "total_standby_mw", "total_mw_confidence"]
    C.write_csv(pd.DataFrame(extra_rows, columns=extra_cols), out_dir / "tx_unmatched_tceq_packages.csv")
    summary = {
        **C.run_meta(args.fixture, [{"name": "Texas Comptroller data center lists (via registry/seed_sites_unlocated.csv)", "url": COMPTROLLER_URL}] + sources),
        "rows": len(df),
        "matched": int(df["application_url"].notna().sum()),
        "with_coordinates": int(df["lat"].notna().sum()),
        "with_generator_count": int(df["generator_count"].notna().sum()),
        "with_generator_mw": int(df["total_standby_mw"].notna().sum()),
        "by_match_method": df["match_method"].fillna("none").value_counts().to_dict(),
        "by_coord_source": df["coord_source"].fillna("none").value_counts().to_dict(),
        "unmatched_datacenter_packages": len(extra_rows),
        "unmatched_packages_with_coordinates": sum(1 for r in extra_rows if r.get("lat") is not None),
    }
    C.write_json(summary, out_dir / "tx_permits_summary.json")
    C.log(f"wrote {out_dir / 'tx_permits.csv'}: {summary['rows']} rows, {summary['matched']} matched, {summary['with_coordinates']} with coordinates")


if __name__ == "__main__":
    C.run_main(main)
