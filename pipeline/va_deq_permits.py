#!/usr/bin/env python3
"""Virginia DEQ data-center air permits -> va_permits.csv

What the DEQ list page looks like (inspected with WebFetch on 2026-10-20)
--------------------------------------------------------------------------
URL (the source_url column of registry/seed_sites_unlocated.csv):
  https://www.deq.virginia.gov/news-info/shortcuts/permits/air/issued-air-permits-for-data-centers
  (the same page is also served at /permits/air/issued-air-permits-for-data-centers).
Content: heading "Issued Air Permits for Data Centers", intro paragraph, three clarification-memo
links, then ONE table headed "Issued Air Permits for Data Centers as of 11/17/2025" with columns

  Air Site Name | Registration No | Permit Issuance Date | Program Type | City/County | Regional Office

184 rows, 173 distinct registration numbers (a registration with several permits appears once
per permit, e.g. 21527 Title V 04/24/2024 and mNSR 09/19/2023). Dates are mm/dd/yyyy. Long site
names wrap. No addresses, coordinates, generator data or CSV/XLSX export.

PDF links: the fetch tool strips <a href>, so whether each row links its permit PDF could NOT be
verified tonight. Circumstantial evidence says yes: the Virginia Mercury (2024-11-13) article
about this page links individual permits as deq.virginia.gov/home/showpublisheddocument/<id>/<ticks>
and the ~180 permit PDFs were uploaded to that document store in Sept-Oct 2024, just before the
page launched. This script therefore (1) parses every <a href> inside each table row and (2) falls
back to other locators when a row has none:

  locator order           source                                          verified tonight?
  page_link               href inside the table row                        structure assumed
  known_documents         fixtures/va_known_documents.csv (8 regs mapped   yes, PDFs opened
                          by web search tonight)
  manual_dir              --pdf-dir DIR with files named <reg>*.pdf          n/a
  search                  DuckDuckGo HTML search "site:deq.virginia.gov      no (fragile)
                          showpublisheddocument <reg> <site name>", then
                          download candidates and verify the registration
                          number printed in the PDF
  enumerate               --enumerate A-B tries /home/showpublisheddocument/  no (the tick-less
                          <id> for every id in the range and keeps PDFs whose URL could not be
                          registration number is on the list                 fetched tonight)

The URL pattern is https://deq.virginia.gov/home/showpublisheddocument/<docid>/<ticks> where
docid is a 5-digit document-store id (25698..26117 for the batch uploaded 2024) and ticks is a
.NET timestamp. Nothing in the registration number predicts docid.

What the permit PDFs look like: see permit_text.py (cover page with "located at" facility
address; equipment tables with Ref. Nos. / description / "3,634 bhp 2,500 ekW (each unit)";
hours-per-year and fuel conditions). Caveats found tonight: the first Virginia address on the
cover is the permittee's MAILING address (Amazon = Herndon), the list's Air Site Name can differ
from the permittee in the PDF (list "Cloud HQ" = permittee "Abteen Ventures LLC", reg 74107) and
the PDF posted may be an older permit than the list's latest date (reg 73743: PDF 2022, list 2025).

Outputs (in --out, default ./out):
  va_permits.csv          one row per registration number
  va_generator_rows.csv   one row per equipment-table row found (audit trail for spot checks)
  va_pdfs/<reg>.pdf       downloaded permits (live mode)
  va_text/<reg>.txt       extracted text (live mode) - what the regexes actually saw
  va_permits_summary.json counts + provenance
"""

from __future__ import annotations

import csv
import html
import io
import json
import re
import sys
import time
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C  # noqa: E402
import permit_text as PT  # noqa: E402

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
LIST_URL = "https://www.deq.virginia.gov/news-info/shortcuts/permits/air/issued-air-permits-for-data-centers"
BACKLOG_CSV = Path(__file__).resolve().parent.parent / "sites" / "seed_sites_unlocated.csv"
REQUIRED_HEADERS = ["Air Site Name", "Registration No", "Permit Issuance Date", "Program Type", "City/County", "Regional Office"]
DDG_HTML = "https://html.duckduckgo.com/html/"
REQUEST_PAUSE = 1.5  # seconds between DEQ downloads: polite, and the site is a public agency's

# --------------------------------------------------------------------------------------
# HTML table parsing (stdlib only; no bs4 dependency)
# --------------------------------------------------------------------------------------


class _TableParser(HTMLParser):
    """Collects every <table> as rows of cells; each cell = {'text': str, 'links': [href...]}."""

    def __init__(self):
        super().__init__()
        self.tables: list[list[list[dict[str, Any]]]] = []
        self._in_table = 0
        self._row: list[dict[str, Any]] | None = None
        self._cell: dict[str, Any] | None = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "table":
            self._in_table += 1
            self.tables.append([])
        elif tag == "tr" and self._in_table:
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = {"text": "", "links": [], "tag": tag}
        elif tag == "a" and self._cell is not None and a.get("href"):
            self._cell["links"].append(a["href"])
        elif tag == "br" and self._cell is not None:
            self._cell["text"] += " "

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._cell is not None and self._row is not None:
            self._row.append(self._cell)
            self._cell = None
        elif tag == "tr" and self._row is not None and self._in_table:
            if self._row:
                self.tables[-1].append(self._row)
            self._row = None
        elif tag == "table" and self._in_table:
            self._in_table -= 1

    def handle_data(self, data):
        if self._cell is not None:
            self._cell["text"] += data


def parse_html_tables(page: str) -> list[list[list[dict[str, Any]]]]:
    p = _TableParser()
    p.feed(page)
    for t in p.tables:
        for row in t:
            for c in row:
                c["text"] = re.sub(r"\s+", " ", html.unescape(c["text"])).strip()
    return p.tables


def parse_list_page(page: str, base_url: str = LIST_URL) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Rows of the permit table with their links. Raises SchemaChangedError if the table is not found."""
    from urllib.parse import urljoin

    tables = parse_html_tables(page)
    target = None
    header_idx: dict[str, int] = {}
    for t in tables:
        for ri, row in enumerate(t[:3]):
            cells = [c["text"] for c in row]
            if all(any(h.lower() == c.lower() for c in cells) for h in REQUIRED_HEADERS[:2]):
                target = t[ri + 1:]
                header_idx = {h: next(i for i, c in enumerate(cells) if c.lower() == h.lower()) for h in REQUIRED_HEADERS if any(c.lower() == h.lower() for c in cells)}
                break
        if target is not None:
            break
    if target is None:
        found = [[c["text"] for c in t[0]] for t in tables if t]
        raise C.SchemaChangedError(
            f"DEQ list page: no table with headers {REQUIRED_HEADERS[:2]} found. Tables seen (first rows): {found[:5]}. "
            "The page layout changed (or it is now rendered by JavaScript); save the page from a browser and pass --html-file."
        )
    m = re.search(r"as of\s+(\d{1,2}/\d{1,2}/\d{4})", page)
    meta = {"as_of": PT.us_date_to_iso(m.group(1)) if m else None, "columns": list(header_idx), "rows": 0, "rows_with_links": 0}
    rows = []
    for row in target:
        if len(row) < len(header_idx):
            continue
        rec = {h: row[i]["text"] for h, i in header_idx.items()}
        if not re.fullmatch(r"\d{4,6}", rec.get("Registration No", "")):
            continue
        links = [urljoin(base_url, l) for c in row for l in c["links"]]
        rec["links"] = links
        rows.append(rec)
        meta["rows"] += 1
        meta["rows_with_links"] += bool(links)
    return rows, meta


def group_by_registration(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One record per registration number: latest permit date kept, all dates/programs listed."""
    by: dict[str, list[dict[str, Any]]] = {}
    for r in rows:
        by.setdefault(r["Registration No"], []).append(r)
    out = []
    for reg, rs in by.items():
        rs_sorted = sorted(rs, key=lambda r: PT.us_date_to_iso(r.get("Permit Issuance Date")) or "", reverse=True)
        top = rs_sorted[0]
        links = []
        for r in rs_sorted:
            for l in r["links"]:
                if l not in links:
                    links.append(l)
        out.append({
            "registration_no": reg,
            "facility_name_list": top.get("Air Site Name"),
            "locality_list": top.get("City/County"),
            "regional_office": top.get("Regional Office"),
            "permit_date_list": PT.us_date_to_iso(top.get("Permit Issuance Date")),
            "program_list": top.get("Program Type"),
            "all_permits_list": "; ".join(f"{PT.us_date_to_iso(r.get('Permit Issuance Date'))} {r.get('Program Type')}" for r in rs_sorted),
            "page_links": links,
        })
    return sorted(out, key=lambda r: r["registration_no"])


# --------------------------------------------------------------------------------------
# PDF locators
# --------------------------------------------------------------------------------------


def load_known_documents() -> dict[str, str]:
    known = {}
    p = FIXTURES / "va_known_documents.csv"
    if p.exists():
        for r in csv.DictReader(open(p, encoding="utf-8")):
            if re.fullmatch(r"\d{4,6}", r["registration_no"] or ""):
                known[r["registration_no"]] = r["document_url"]
    return known


def pick_pdf_links(links: list[str]) -> list[str]:
    pref = [l for l in links if "showpublisheddocument" in l or l.lower().endswith(".pdf")]
    return pref or [l for l in links if "deq.virginia.gov" in l and "#" not in l]


def ddg_search_candidates(reg: str, name: str, max_results: int = 3) -> list[str]:
    """DuckDuckGo HTML endpoint; returns deq.virginia.gov showpublisheddocument URLs. Fragile:
    rate-limited, may return a CAPTCHA page, and depends on the PDF having been indexed."""
    import requests
    from urllib.parse import parse_qs, unquote, urlparse

    words = " ".join(re.findall(r"[A-Za-z]{3,}", name)[:3])
    q = f'site:deq.virginia.gov showpublisheddocument "Registration No" {reg} {words}'
    try:
        resp = requests.get(DDG_HTML, params={"q": q}, headers={"User-Agent": C.USER_AGENT}, timeout=60)
    except requests.RequestException as exc:
        C.log(f"  search failed for {reg}: {exc}")
        return []
    if resp.status_code != 200:
        C.log(f"  search HTTP {resp.status_code} for {reg} (rate-limited?)")
        return []
    urls = []
    for href in re.findall(r'href="([^"]+)"', resp.text):
        u = html.unescape(href)
        if "duckduckgo.com/l/" in u:
            qs = parse_qs(urlparse(u).query)
            u = unquote(qs.get("uddg", [""])[0])
        if "deq.virginia.gov/home/showpublisheddocument" in u and u not in urls:
            urls.append(u)
    return urls[:max_results]


def download_pdf(url: str, dest: Path) -> Path:
    f = C.fetch(url, expect="pdf", landing_page=LIST_URL)
    C.write_bytes(f.content, dest)
    return dest


def _cache_tables(pdf: Path, dest: Path) -> list[dict[str, Any]]:
    tables = PT.pdf_to_tables(pdf)
    C.write_bytes(json.dumps(tables, ensure_ascii=False).encode("utf-8"), dest)
    return tables


def tables_for(reg: str, out_dir: Path, pdf: Path | None = None) -> list[dict[str, Any]] | None:
    """Ruled tables of the permit (cached next to the text as va_text/<reg>.tables.json). None when
    neither the cache nor the PDF is available (the extractor then uses the text read alone)."""
    cached = out_dir / "va_text" / f"{reg}.tables.json"
    if cached.exists() and (pdf is None or cached.stat().st_mtime >= pdf.stat().st_mtime):
        return json.loads(cached.read_text(encoding="utf-8"))
    pdf = pdf or (out_dir / "va_pdfs" / f"{reg}.pdf")
    if pdf.exists():
        return _cache_tables(pdf, cached)
    return None


def text_for(reg: str, url: str | None, args, out_dir: Path) -> tuple[str | None, str | None, str]:
    """Return (text, pdf_url_used, status). Live mode downloads and extracts; cached text is reused."""
    text_dir = out_dir / "va_text"
    pdf_dir = out_dir / "va_pdfs"
    cached = text_dir / f"{reg}.txt"
    if cached.exists() and not args.refresh:
        return cached.read_text(encoding="utf-8"), url, "cached_text"
    if args.pdf_dir:
        for cand in sorted(Path(args.pdf_dir).glob(f"{reg}*.pdf")):
            text = PT.pdf_to_text(cand)
            C.write_bytes(text.encode("utf-8"), cached)
            _cache_tables(cand, text_dir / f"{reg}.tables.json")
            # Record the public URL if the list page gave one; never a local path (it would leak into
            # the handover files). The local file is identified by name in pdf_locator.
            return text, url, "manual_dir"
    if not url:
        return None, None, "no_url"
    dest = pdf_dir / f"{reg}.pdf"
    if not dest.exists() or args.refresh:
        try:
            download_pdf(url, dest)
        except C.SourceError as exc:
            C.log(f"  {reg}: {type(exc).__name__}: {str(exc)[:160]}")
            return None, url, f"download_failed:{type(exc).__name__}"
        time.sleep(REQUEST_PAUSE)
    text = PT.pdf_to_text(dest)
    C.write_bytes(text.encode("utf-8"), cached)
    _cache_tables(dest, text_dir / f"{reg}.tables.json")
    return text, url, "downloaded"


# --------------------------------------------------------------------------------------
# Extraction per registration
# --------------------------------------------------------------------------------------

OUT_COLUMNS = [
    "backlog_id", "registration_no", "facility_name_list", "locality_list", "regional_office", "permit_date_list",
    "program_list", "all_permits_list", "pdf_url", "pdf_locator", "pdf_status", "text_quality", "registration_match",
    "permittee_pdf", "registration_no_pdf", "registration_nos_pdf_all", "approved_on", "last_amended", "facility_street", "facility_city",
    "facility_zip", "facility_county_pdf", "facility_address_raw", "address_confidence", "address_method",
    "generator_count", "generator_count_confidence", "unit_kw_list", "unit_kw_min", "unit_kw_max",
    "total_standby_mw", "total_standby_mw_min", "total_standby_mw_max", "total_mw_confidence",
    "generator_rows_uncounted", "generator_units_without_kw", "generator_read", "generator_crosscheck", "fuel", "fuel_confidence", "fuel_sulfur_ppm", "fuel_gallons_per_year_limits",
    "fuel_gallons_per_year_total", "hours_maint_per_year", "hours_all_purpose_per_year", "hours_combined_per_year",
    "hours_confidence", "extract_reason", "source_url", "list_as_of", "retrieved_at",
]


def extract_from_text(text: str, tables: list[dict[str, Any]] | None = None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """All fields from one permit. ``tables`` (pdfplumber ruled tables, see PT.pdf_to_tables) feed the
    table read of the equipment list; the text read always runs and is the cross-check (or the only
    read for scans, prose permits and the text-only fixtures)."""
    rec: dict[str, Any] = {}
    rec.update(PT.extract_va_cover(text))
    inv = PT.read_generator_inventory(text, tables)
    rec.update(inv.summary)
    rec.update(PT.extract_fuel(text))
    rec.update(PT.extract_hours(text))
    return rec, PT.genrows_as_dicts(inv.rows)


CONFIDENCE_FIELDS = ("generator_count_confidence", "total_mw_confidence", "address_confidence", "fuel_confidence", "hours_confidence")


def extract_permit_text(text: str, tables: list[dict[str, Any]] | None = None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Text-quality gate + field extraction for one permit. Used by main() and by
    extract_from_pdf(); no list page, no network."""
    q = PT.text_quality(text)
    if q != "ok":
        rec = {k: None for k in OUT_COLUMNS}
        rec["text_quality"] = q
        rec["extract_reason"] = f"PDF text {q}: needs OCR or manual reading"
        for k in CONFIDENCE_FIELDS:
            rec[k] = "none"
        return rec, []
    rec, rows = extract_from_text(text, tables)
    rec["text_quality"] = q
    return rec, rows


def extract_from_pdf(pdf_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Per-PDF extraction (the unit tested by tests/test_va_extraction.py on the real permits)."""
    pdf_path = Path(pdf_path)
    return extract_permit_text(PT.pdf_to_text(pdf_path), PT.pdf_to_tables(pdf_path))


def main() -> None:
    ap = C.base_parser(__doc__)
    ap.add_argument("--html-file", type=Path, help="parse this saved copy of the DEQ list page instead of fetching it")
    ap.add_argument("--pdf-dir", type=Path, help="directory of manually downloaded permits named <registration>*.pdf")
    ap.add_argument("--no-search", action="store_true", help="do not query DuckDuckGo for PDFs the page does not link")
    ap.add_argument("--enumerate", metavar="A-B", help="UNTESTED fallback: try showpublisheddocument/<id> for id in A..B")
    ap.add_argument("--limit", type=int, help="process only the first N registrations (smoke test)")
    ap.add_argument("--refresh", action="store_true", help="re-download PDFs even if cached in --out")
    ap.add_argument("--backlog", type=Path, default=BACKLOG_CSV, help="seed_sites_unlocated.csv (for backlog_id join)")
    args = ap.parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    retrieved_at = None if args.fixture else time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # 1. list page
    if args.fixture:
        page = (FIXTURES / "va_deq_list_page.html").read_text(encoding="utf-8")
        page_src = "pipeline/fixtures/va_deq_list_page.html"
    elif args.html_file:
        page = args.html_file.read_text(encoding="utf-8", errors="replace")
        page_src = Path(args.html_file).name  # file name only: no local paths in outputs
    else:
        f = C.fetch(LIST_URL, expect="html")
        page = f.text()
        page_src = f.final_url
        C.write_bytes(f.content, out_dir / "va_deq_list_page.html")
    rows, meta = parse_list_page(page, base_url=LIST_URL)
    regs = group_by_registration(rows)
    C.log(f"list page: {meta['rows']} permit rows, {len(regs)} registrations, {meta['rows_with_links']} rows with links, as of {meta['as_of']}")
    if not args.fixture and meta["rows_with_links"] == 0:
        C.log("WARNING: the list page rows carry no hyperlinks. PDFs will be located via known_documents, --pdf-dir, "
              "search and/or --enumerate only. Open the page in a browser to check whether names are links.")
    if args.limit:
        regs = regs[: args.limit]

    # backlog ids
    backlog = {}
    if args.backlog.exists():
        for r in csv.DictReader(open(args.backlog, encoding="utf-8")):
            m = re.search(r"DEQ registration (\d+)", r.get("record_id", ""))
            if m:
                backlog[m.group(1)] = r["backlog_id"]

    known = load_known_documents()
    enumerated: dict[str, str] = {}
    if args.enumerate and not args.fixture:
        a, b = (int(x) for x in args.enumerate.split("-"))
        C.log(f"enumerating document ids {a}..{b} (UNTESTED tick-less URL form)")
        for did in range(a, b + 1):
            url = f"https://deq.virginia.gov/home/showpublisheddocument/{did}"
            dest = out_dir / "va_enum" / f"{did}.pdf"
            if not dest.exists():
                try:
                    download_pdf(url, dest)
                except C.SourceError as exc:
                    C.log(f"  {did}: {type(exc).__name__}")
                    time.sleep(REQUEST_PAUSE)
                    continue
                time.sleep(REQUEST_PAUSE)
            t = PT.pdf_to_text(dest, max_pages=4)
            m = PT.REG_RE.search(t)
            if m:
                enumerated[m.group(1)] = url

    records = []
    genrows = []
    for i, g in enumerate(regs, 1):
        reg = g["registration_no"]
        url, locator = None, None
        cands = pick_pdf_links(g["page_links"])
        if cands:
            url, locator = cands[0], "page_link"
        elif reg in known:
            url, locator = known[reg], "known_documents"
        elif reg in enumerated:
            url, locator = enumerated[reg], "enumerate"
        rec = {k: None for k in OUT_COLUMNS}
        rec.update({
            "backlog_id": backlog.get(reg, f"va-deq-{reg}"), "registration_no": reg,
            "facility_name_list": g["facility_name_list"], "locality_list": g["locality_list"],
            "regional_office": g["regional_office"], "permit_date_list": g["permit_date_list"],
            "program_list": g["program_list"], "all_permits_list": g["all_permits_list"],
            "source_url": LIST_URL, "list_as_of": meta["as_of"], "retrieved_at": retrieved_at,
        })
        text = None
        tables = None  # fixture texts have no PDF behind them: text read only
        status = "no_url"
        if args.fixture:
            fx = FIXTURES / "va_permits" / f"{reg}.txt"
            if fx.exists():
                text, status = fx.read_text(encoding="utf-8"), "fixture_text"
                url = url or known.get(reg)
                locator = locator or ("known_documents" if reg in known else None)
        else:
            text, url, status = text_for(reg, url, args, out_dir)
            if text is None and args.pdf_dir is None and not args.no_search and status == "no_url":
                for cu in ddg_search_candidates(reg, g["facility_name_list"] or ""):
                    time.sleep(2.0)
                    t2, u2, s2 = text_for(reg, cu, args, out_dir)
                    if t2 and PT.REG_RE.search(t2) and PT.REG_RE.search(t2).group(1) == reg:
                        text, url, status, locator = t2, u2, s2, "search"
                        break
                    if t2:  # wrong registration: discard the cached text
                        (out_dir / "va_text" / f"{reg}.txt").unlink(missing_ok=True)
                        (out_dir / "va_pdfs" / f"{reg}.pdf").unlink(missing_ok=True)
            if status == "manual_dir":
                locator = f"manual_dir:{reg}.pdf"
            if text is not None:
                src_pdf = None
                if args.pdf_dir:
                    src_pdf = next(iter(sorted(Path(args.pdf_dir).glob(f"{reg}*.pdf"))), None)
                tables = tables_for(reg, out_dir, src_pdf)
        rec["pdf_url"], rec["pdf_locator"], rec["pdf_status"] = url, locator, status
        if text is None:
            rec["text_quality"] = "none"
            rec["extract_reason"] = {
                "no_url": "no PDF located (no row link, not in known_documents, search found nothing)",
            }.get(status, status)
            for k in CONFIDENCE_FIELDS:
                rec[k] = "none"
            records.append(rec)
            C.log(f"[{i}/{len(regs)}] {reg} {g['facility_name_list'][:40]!r}: {rec['extract_reason']}")
            continue
        ext, rows_found = extract_permit_text(text, tables)
        if ext["text_quality"] != "ok":
            for k in ("text_quality", "extract_reason", *CONFIDENCE_FIELDS):
                rec[k] = ext[k]
            records.append(rec)
            continue
        rec.update({k: v for k, v in ext.items() if k in rec})
        all_regs = (ext.get("registration_nos_pdf_all") or "").split(";")
        if reg in all_regs:
            rec["registration_match"] = "match" if len(all_regs) == 1 else "match_with_other_numbers_printed"
            rec["registration_no_pdf"] = reg
        else:
            rec["registration_match"] = "mismatch" if ext.get("registration_no_pdf") else "not_found"
        reasons = []
        if rec["registration_match"] == "mismatch":
            reasons.append(f"PDF says registration {ext.get('registration_no_pdf')}, list says {reg}")
        elif rec["registration_match"] == "match_with_other_numbers_printed":
            reasons.append(f"PDF also prints registration number(s) {[r for r in all_regs if r != reg]} (typo in page headers?)")
        if rec["generator_count"] is None:
            reasons.append("no generator rating rows recognised")
        elif rec["total_standby_mw"] is None:
            reasons.append("generator units listed with bhp only: no kW rating printed, MW not estimated")
        elif rec.get("generator_units_without_kw"):
            reasons.append(f"{rec['generator_units_without_kw']} unit(s) have no kW rating in the text: MW is a partial sum")
        if rec["facility_street"] is None:
            reasons.append("no facility street address recognised")
        rec["extract_reason"] = "; ".join(reasons) or None
        for r in rows_found:
            r["registration_no"] = reg
            genrows.append(r)
        records.append(rec)
        C.log(f"[{i}/{len(regs)}] {reg} {g['facility_name_list'][:40]!r}: {rec['generator_count']} gens, "
              f"{rec['total_standby_mw']} MW ({rec['total_mw_confidence']}), {rec['facility_street']}, {rec['facility_city']}")

    df = pd.DataFrame(records, columns=OUT_COLUMNS)
    C.write_csv(df, out_dir / "va_permits.csv")
    gcols = ["registration_no", "read", "section", "refs", "count", "count_source", "count_confidence", "kw_each", "kw_min", "kw_max",
             "bhp_each", "maker", "model", "each_flag", "note", "description", "snippet"]
    C.write_csv(pd.DataFrame(genrows, columns=gcols), out_dir / "va_generator_rows.csv")
    summary = {
        **C.run_meta(args.fixture, [{"name": "VA DEQ issued air permits for data centers", "url": LIST_URL, "page_source": page_src,
                                     "list_as_of": meta["as_of"], "list_rows": meta["rows"], "rows_with_links": meta["rows_with_links"]}]),
        "registrations": len(df),
        "with_pdf_text": int((df["text_quality"] == "ok").sum()),
        "with_generator_mw": int(df["total_standby_mw"].notna().sum()),
        "with_street_address": int(df["facility_street"].notna().sum()),
        "total_standby_mw_sum": C.round_mw(df["total_standby_mw"].sum(), 1),
        "by_locator": df["pdf_locator"].fillna("none").value_counts().to_dict(),
        "by_mw_confidence": df["total_mw_confidence"].fillna("none").value_counts().to_dict(),
        "by_address_confidence": df["address_confidence"].fillna("none").value_counts().to_dict(),
    }
    C.write_json(summary, out_dir / "va_permits_summary.json")
    C.log(f"wrote {out_dir / 'va_permits.csv'}: {summary['registrations']} registrations, "
          f"{summary['with_generator_mw']} with MW, {summary['with_street_address']} with street address")


if __name__ == "__main__":
    C.run_main(main)
