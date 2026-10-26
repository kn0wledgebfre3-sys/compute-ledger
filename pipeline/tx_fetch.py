#!/usr/bin/env python3
"""Texas datacenters from sources where ISSUED air authorizations stay public.

    python3 tx_fetch.py --fixture --out out_tx  # rebuild tx_issued_sites.csv + BROWSER_LIST.csv from fixtures/tx_issued/ (no network)
    python3 tx_fetch.py --out out              # live: EPA FRS (ArcGIS) + TCEQ PDFs + TCEQ airperm project reports
    python3 tx_fetch.py --out out --echo       #   + EPA ECHO air_rest_services (TX, NAICS 518210 / SIC 7374)
    python3 tx_fetch.py --out out --echo-exporter ~/Downloads/echo_exporter.zip   # filter the 392 MB ECHO Exporter
    python3 tx_fetch.py --out out --icis-air ~/Downloads/ICIS-AIR_downloads.zip   # filter the ICIS-Air dataset
    python3 tx_fetch.py --airperm-dump-form    # print the TCEQ airperm search form fields (to wire up a search)

Sources (details and what is blocked: SOURCES.md)
-------------------------------------------------
1. EPA Facility Registry Service, public ArcGIS feature service (no token, maxRecordCount 2000):
   https://services.arcgis.com/cJ9YHowT8TU7DUyn/ArcGIS/rest/services/FRS_INTERESTS/FeatureServer
   layer 0 = FRS_INTERESTS (one row per facility x program: AIR = ICIS-Air id, TX-TCEQ ACR = TCEQ Central Registry
   RN, EIS = emissions inventory, CEDRI = NSPS/NESHAP e-reports, NPDES = permits incl. TCEQ construction stormwater
   TXR15xxxx), table 1 = FRS_NAICS, table 2 = FRS_SIC (joined to layer 0 on KEY_FIELD = PGM_SYS_ACRNM + PGM_SYS_ID).
   Verified working 2026-10-22.
2. TCEQ Title V public-notice documents, which stay at their URL after issuance:
   https://www.tceq.texas.gov/assets/public/permitting/air/publicnotice/<project>sob.pdf  (statement of basis)
   .../<project>sop.pdf (draft or effective permit), .../<project>pa.pdf (announcement)
   and applications https://www.tceq.texas.gov/assets/public/permitting/air/reports/applications/<project>-ac|tc.pdf
3. TCEQ NSR air-permits database ("airperm"), which keeps PBR registrations, PBR certifications (APD-CERT),
   standard permits and NSR permits after issuance:
   https://www2.tceq.texas.gov/airperm/index.cfm?fuseaction=airpermits.project_report&proj_id=<project>
   https://www2.tceq.texas.gov/airperm/index.cfm?fuseaction=airpermits.start   (search form)
   robots.txt blocks it for the fetch tool used to build the fixtures, so the report parser here is UNTESTED; raw
   HTML is saved so it can be checked.
4. EPA ECHO air_rest_services (robots-blocked for the fetch tool; documented form):
   https://echodata.epa.gov/echo/air_rest_services.get_facilities?output=JSON&p_st=TX&p_ncs=518210
   -> Results.QueryID -> https://echodata.epa.gov/echo/air_rest_services.get_download?output=CSV&qid=<QueryID>
5. ECHO bulk files: https://echo.epa.gov/files/echodownloads/echo_exporter.zip and .../ICIS-AIR_downloads.zip
6. --psei YEAR: TCEQ Point Source Emissions Inventory workbooks (account level, ~54 MB each; needs openpyxl)
   https://www.tceq.texas.gov/downloads/air-quality/point-source/<year>.xlsx and .../2010-2024-state-sum.xlsx
7. --central-registry-coastal: TCEQ Central Registry Files - Coastal & East Texas on the Texas Socrata network
   https://data.austintexas.gov/api/v3/views/tzyg-j7q4/export.csv?accessType=DOWNLOAD (columns not verified)

Permit documents themselves (PBR registration files, standard-permit registrations, NSR permits) sit in TCEQ
Records Online (CFR), which only works in a browser; they are written to BROWSER_LIST.csv.

Outputs: tx_issued_sites.csv, BROWSER_LIST.csv, tx_fetch_summary.json (+ raw/ in live mode).
Nothing here invents coordinates or MW: lat/lon come from a TCEQ document or an FRS record, MW only where a
document states unit kW.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import zipfile
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
FIX = HERE / "fixtures" / "tx_issued"
LINKS_CSV = HERE.parent / "sites" / "tx_site_links.csv"
DEFAULT_BACKLOG = HERE.parent / "sites" / "seed_sites_unlocated.csv"
COMPTROLLER_URL = "https://comptroller.texas.gov/taxes/data-centers/data-center-lists.php"

FRS = "https://services.arcgis.com/cJ9YHowT8TU7DUyn/ArcGIS/rest/services/FRS_INTERESTS/FeatureServer"
ECHO = "https://echodata.epa.gov/echo/air_rest_services"
TCEQ_PN = "https://www.tceq.texas.gov/assets/public/permitting/air/publicnotice/{p}{kind}.pdf"
TCEQ_APP = "https://www.tceq.texas.gov/assets/public/permitting/air/reports/applications/{p}-{kind}.pdf"
AIRPERM_REPORT = "https://www2.tceq.texas.gov/airperm/index.cfm?fuseaction=airpermits.project_report&proj_id={p}"
AIRPERM_START = "https://www2.tceq.texas.gov/airperm/index.cfm?fuseaction=airpermits.start"
CFR_SEARCH = "https://records.tceq.texas.gov/cs/idcplg?IdcService=TCEQ_SEARCH"
UA = "Mozilla/5.0 (compatible; tx-datacenter-ledger/1.0; research use; contact via repository)"
PAUSE = 1.0

# Name patterns used against FRS PRIMARY_NAME (STATE_CODE='TX'). Operator words are only used for AIR/EIS/CEDRI
# interests unless they are distinctive enough to query across all programs.
FRS_NAME_QUERIES_ALL_PROGRAMS = [
    "%DATA CENTER%", "%DATACENTER%", "%DATA CTR%", "%MICROSOFT%", "%QTS%", "%CYRUS%", "%LANCIUM%", "%ALIGNED%",
    "%EDGECONN%", "%VANTAGE DATA%", "%VANTAGE TX%", "%VANTAGE DC%", "%SABEY%", "%HYPERSCALE%", "%CRUSOE%",
    "%STARGATE%", "%CORE SCIENTIFIC%", "%RIOT PLATFORMS%", "%WHINSTONE%", "%BITDEER%", "%IREN %", "%HELIOS%",
    "%POOLSIDE%", "%FERMI AMERICA%", "%NEXUS DATA%", "%COMPASS DATA%", "%STACK INFRA%", "%SWITCH LTD%",
    "%DIGITAL REALTY%", "%DATABANK%", "%EQUINIX%", "%RACKSPACE%",
    # names from TCEQ airperm records (FracTracker sheet) whose FRS records were not looked up on 2026-10-22
    "%TECHNICAL REALTY%", "%TRG %", "%BIG WATT%", "%DECENNIAL%", "%STREAM HOUSTON%", "%VANTAGE FRONTIER%",
    "%EDGED%", "%VOLTAGRID%", "%GALAXY%", "%ARGO %", "%STACK %", "%YONDR%", "%TRACT %",
]
DC_NAME_RE = re.compile(
    r"DATA ?CENT|DATACENT|DATA CTR|HOSTING|HYPERSCALE|\bSAT ?\d|\bDFW ?\d|\bAUS ?\d|\bTX ?\d{1,3}\b|\bSN\d|"
    r"EQUINIX|RACKSPACE|CYRUS|VANTAGE (?:DATA|TX|DC)|COMPASS DATA|\bQTS\b|ALIGNED|STACK INFRA|SABEY|EDGECONNEX|"
    r"\bNTT\b|DATABANK|MICROSOFT|GOOGLE|AMAZON DATA|AMAZON WEB|META PLATFORMS|ORACLE|LANCIUM|CRUSOE|STARGATE|"
    r"CORE SCIENTIFIC|RIOT PLATFORMS|WHINSTONE|BITDEER|HELIOS|\bIREN\b|CIPHER|SHARKA|ALAMO MISSION|\bSTA1\b",
    re.IGNORECASE)
# FRS records that are construction support for a campus, not the campus (kept only when a curated link names them)
SUPPORT_RE = re.compile(
    r"SUBSTATION|BATCH PLANT|REDI-MIX|LAYDOWN|SWITCH STATION|BORROW PIT|TRANSMISSION|OFFSITES|GRADING|TEMPORARY|"
    r"UNDERGROUND DESIGN|PARKING|DATA CENTER BP\b", re.IGNORECASE)
NOT_DC_RE = re.compile(r"EDWARDS AQUIFER RESEARCH|ENERGY CONTROL AND DATA CENTER|LUFKIN PAPER|STORE AND DATA CENTER",
                       re.IGNORECASE)
# FRS coordinates that contradict the record's own address (checked by hand); not used
COORD_REJECT = {
    "110070383621": "FRS point (33.2008,-97.1851) is ~35 km from the stated Garland address",
}

OUT_COLUMNS = [
    "facility_key", "facility_name", "operator", "permittee", "address", "city", "county", "lat", "lon",
    "coord_source", "tceq_rn", "tceq_permit_numbers", "tceq_project_numbers", "authorization_type",
    "authorization_status", "air_record", "generator_count", "generator_mw", "generator_basis", "frs_registry_ids",
    "icis_air_ids", "other_epa_ids", "source_urls", "backlog_id", "backlog_confidence", "backlog_basis",
    "backlog_candidates", "notes",
]


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


# --------------------------------------------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------------------------------------------


def http(url: str, data: dict | None = None, timeout: int = 120, binary: bool = False):
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        return raw if binary else raw.decode(r.headers.get_content_charset() or "utf-8", "replace")


def arcgis_query(layer: int, where: str, out_fields: str = "*", page: int = 2000) -> list[dict[str, Any]]:
    """All rows of an ArcGIS FeatureServer query, paged by resultOffset (POST, so long IN lists work)."""
    rows, offset = [], 0
    while True:
        params = {"where": where, "outFields": out_fields, "returnGeometry": "false", "orderByFields": "OBJECTID",
                  "resultOffset": offset, "resultRecordCount": page, "f": "json"}
        js = json.loads(http(f"{FRS}/{layer}/query", data=params))
        if "error" in js:
            raise RuntimeError(f"ArcGIS error for {where!r}: {js['error']}")
        feats = [f["attributes"] for f in js.get("features", [])]
        rows.extend(feats)
        if not js.get("exceededTransferLimit") or not feats:
            return rows
        offset += len(feats)
        time.sleep(PAUSE)


def epoch_to_date(v: Any) -> str | None:
    if v in (None, "", "null"):
        return None
    try:
        return time.strftime("%Y-%m-%d", time.gmtime(int(v) / 1000))
    except (TypeError, ValueError):
        return str(v)


# --------------------------------------------------------------------------------------------------------------
# FRS: live pull and fixture load -> list of interest rows (dicts with the layer-0 field names)
# --------------------------------------------------------------------------------------------------------------

FRS_FIELDS = ["REGISTRY_ID", "PRIMARY_NAME", "LOCATION_ADDRESS", "CITY_NAME", "COUNTY_NAME", "POSTAL_CODE",
              "LATITUDE83", "LONGITUDE83", "PGM_SYS_ACRNM", "PGM_SYS_ID", "ACTIVE_STATUS", "CREATE_DATE", "query"]


def frs_live(raw_dir: Path) -> list[dict[str, Any]]:
    raw_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []

    def keep(rs: Iterable[dict], q: str) -> None:
        for r in rs:
            r = dict(r)
            r["query"] = q
            r["CREATE_DATE"] = epoch_to_date(r.get("CREATE_DATE"))
            rows.append(r)

    # a) NAICS 518210 / SIC 7374 program records with Texas ids (AIR TX..., NPDES TX..., Central Registry RN...)
    keys: set[str] = set()
    for layer, where in ((1, "NAICS_CODE='518210' AND (PGM_SYS_ID LIKE 'TX%' OR PGM_SYS_ID LIKE 'RN%')"),
                         (2, "SIC_CODE='7374' AND (PGM_SYS_ID LIKE 'TX%' OR PGM_SYS_ID LIKE 'RN%')")):
        got = arcgis_query(layer, where)
        (raw_dir / f"frs_layer{layer}_codes.json").write_text(json.dumps(got, indent=1))
        keys |= {g["KEY_FIELD"] for g in got if g.get("KEY_FIELD")}
        log(f"FRS layer {layer}: {len(got)} code rows ({where})")
    keys = sorted(keys)
    for i in range(0, len(keys), 150):
        chunk = ",".join("'" + k.replace("'", "''") + "'" for k in keys[i:i + 150])
        keep(arcgis_query(0, f"KEY_FIELD IN ({chunk})"), "naics518210_or_sic7374")
    # b) name patterns, all programs, Texas
    for pat in FRS_NAME_QUERIES_ALL_PROGRAMS:
        got = arcgis_query(0, f"STATE_CODE='TX' AND PRIMARY_NAME LIKE '{pat}'")
        keep(got, f"name {pat}")
        log(f"FRS name {pat}: {len(got)}")
        time.sleep(PAUSE)
    # c) every Texas ICIS-Air interest (about 6,100), kept when the name looks like a data center
    air = arcgis_query(0, "STATE_CODE='TX' AND PGM_SYS_ACRNM='AIR'")
    (raw_dir / "frs_tx_air_all.json").write_text(json.dumps(air))
    keep([a for a in air if DC_NAME_RE.search(a.get("PRIMARY_NAME") or "")], "tx_air_name_filter")
    log(f"FRS Texas AIR interests: {len(air)}; name-filtered kept")
    # d) every interest of every registry id found so far (adds RN, EIS, CEDRI, stormwater ids)
    regs = sorted({str(r["REGISTRY_ID"]) for r in rows if r.get("REGISTRY_ID")})
    for i in range(0, len(regs), 150):
        chunk = ",".join(f"'{x}'" for x in regs[i:i + 150])
        keep(arcgis_query(0, f"REGISTRY_ID IN ({chunk})"), "registry_expand")
    (raw_dir / "frs_rows.json").write_text(json.dumps(rows, indent=1))
    return rows


def frs_fixture() -> list[dict[str, Any]]:
    rows = []
    for p in sorted((FIX / "frs").glob("*.psv")):
        lines = [ln for ln in p.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
        for r in csv.DictReader(lines, delimiter="|"):
            r = {k: (None if v in ("", "null") else v) for k, v in r.items()}
            r.setdefault("query", p.stem)
            if r.get("PRIMARY_NAME") is None:  # code-table rows (NAICS/SIC) have no facility fields
                continue
            rows.append(r)
    return rows


# --------------------------------------------------------------------------------------------------------------
# TCEQ: Title V documents, airperm project reports (live), authorizations table (fixture + live)
# --------------------------------------------------------------------------------------------------------------


def pdf_text(path: Path) -> str | None:
    if shutil.which("pdftotext"):
        try:
            return subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, timeout=300,
                                  check=True).stdout.decode("utf-8", "replace")
        except Exception as exc:  # noqa: BLE001
            log(f"  pdftotext failed on {path.name}: {exc}")
    try:
        from pypdf import PdfReader  # type: ignore

        return "\n".join((pg.extract_text() or "") for pg in PdfReader(str(path)).pages)
    except Exception:  # noqa: BLE001
        return None


DMS_RE = re.compile(r"Latitude\s+(\d{2})\D{1,3}(\d{1,2})\D{1,3}(\d{1,2}(?:\.\d+)?)\D{1,6}Longitude\s+-?(\d{2,3})\D{1,3}"
                    r"(\d{1,2})\D{1,3}(\d{1,2}(?:\.\d+)?)", re.IGNORECASE | re.DOTALL)


def extract_title_v(text: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    m = re.search(r"Permit (?:Number|No\.?)\s*:?\s*O-?0*(\d{3,5})", text)
    out["o_permit"] = f"O{m.group(1)}" if m else None
    m = re.search(r"\bRN\s?(\d{9})\b", text)
    out["rn"] = f"RN{m.group(1)}" if m else None
    m = re.search(r"\b(\d{1,4})\s+(?:stationary\s+RICE\s+)?diesel(?:-fired)?\s+emergency\s+generators", text, re.I)
    out["generator_count_stated"] = int(m.group(1)) if m else None
    out["pbr_registrations"] = sorted(set(re.findall(r"106\.\d{3}/\d{2}/\d{2}/\d{4}\s*\[(\d{4,6})\]", text)))
    out["nsr_permits"] = sorted(set(re.findall(r"Authorization No\.?:?\s*(\d{4,6})", text)))
    out["naics"] = (re.search(r"\b(5182\d0|5415\d\d)\b", text) or [None])[0]
    m = DMS_RE.search(text)
    if m:
        d = [float(x) for x in m.groups()]
        out["lat"] = round(d[0] + d[1] / 60 + d[2] / 3600, 6)
        out["lon"] = -round(d[3] + d[4] / 60 + d[5] / 3600, 6)
    out["unit_kw_mentions"] = sorted(set(re.findall(r"\b(\d{3,4}(?:\.\d)?)\s?(?:e?kW)\b", text, re.I)))[:40]
    return out


def tceq_docs_live(auths: list[dict[str, str]], raw_dir: Path) -> list[dict[str, Any]]:
    """Download SOB/SOP/application PDFs for every Title V project in the authorizations table."""
    d = raw_dir / "tceq_docs"
    d.mkdir(parents=True, exist_ok=True)
    out = []
    projects = sorted({a["project_no"] for a in auths if a.get("project_no") and len(a["project_no"]) == 5})
    for p in projects:
        for kind, url in (("sob", TCEQ_PN.format(p=p, kind="sob")), ("sop", TCEQ_PN.format(p=p, kind="sop")),
                          ("ac", TCEQ_APP.format(p=p, kind="ac")), ("tc", TCEQ_APP.format(p=p, kind="tc"))):
            dest = d / f"{p}{kind}.pdf"
            rec = {"project": p, "kind": kind, "url": url, "status": None}
            try:
                if not dest.exists():
                    dest.write_bytes(http(url, binary=True))
                    time.sleep(PAUSE)
                txt = pdf_text(dest)
                rec["status"] = "ok" if txt else "no_text"
                if txt:
                    (d / f"{p}{kind}.txt").write_text(txt, encoding="utf-8")
                    rec.update(extract_title_v(txt))
            except Exception as exc:  # noqa: BLE001
                rec["status"] = f"error:{type(exc).__name__}:{str(exc)[:80]}"
            out.append(rec)
            log(f"  TCEQ {p}{kind}: {rec['status']}")
    seen_urls = {r["url"] for r in out}
    for a in auths:
        for url in re.findall(r"https?://\S+?\.pdf", (a.get("source_url") or "") + " " + (a.get("note") or ""), re.I):
            if url in seen_urls:
                continue
            seen_urls.add(url)
            dest = d / re.sub(r"[^A-Za-z0-9._-]+", "_", url.split("//", 1)[1])[-120:]
            rec = {"project": a.get("project_no"), "kind": "linked_pdf", "url": url, "status": None, "auth_key": a["auth_key"]}
            try:
                if not dest.exists():
                    dest.write_bytes(http(url, binary=True))
                    time.sleep(PAUSE)
                txt = pdf_text(dest)
                rec["status"] = "ok" if txt else "no_text"
                if txt:
                    dest.with_suffix(".txt").write_text(txt, encoding="utf-8")
                    rec.update(extract_title_v(txt))
            except Exception as exc:  # noqa: BLE001
                rec["status"] = f"error:{type(exc).__name__}:{str(exc)[:80]}"
            out.append(rec)
            log(f"  linked PDF {url}: {rec['status']}")
    with open(raw_dir / "tceq_docs_extracted.csv", "w", newline="", encoding="utf-8") as f:
        cols = sorted({k for r in out for k in r})
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in out:
            w.writerow({k: (";".join(v) if isinstance(v, list) else v) for k, v in r.items()})
    return out


class _Cells(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[str]] = []
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._row is not None and self._cell is not None:
            self._row.append(re.sub(r"\s+", " ", "".join(self._cell)).strip())
            self._cell = None
        elif tag == "tr" and self._row is not None:
            if any(self._row):
                self.rows.append(self._row)
            self._row = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)


def airperm_live(auths: list[dict[str, str]], raw_dir: Path) -> list[dict[str, Any]]:
    """Fetch TCEQ airperm project reports for every IMS project number we hold (6-digit projects)."""
    d = raw_dir / "airperm"
    d.mkdir(parents=True, exist_ok=True)
    out = []
    for p in sorted({a["project_no"] for a in auths if a.get("project_no") and len(a["project_no"]) == 6}):
        url = AIRPERM_REPORT.format(p=p)
        rec: dict[str, Any] = {"project": p, "url": url}
        try:
            html = http(url)
            (d / f"project_{p}.html").write_text(html, encoding="utf-8")
            cp = _Cells()
            cp.feed(html)
            pairs = {r[0].rstrip(":"): r[1] for r in cp.rows if len(r) >= 2 and len(r[0]) < 60}
            rec.update({"status": "ok", "fields": pairs})
        except Exception as exc:  # noqa: BLE001
            rec["status"] = f"error:{type(exc).__name__}:{str(exc)[:80]}"
        out.append(rec)
        log(f"  airperm {p}: {rec['status']}")
        time.sleep(PAUSE)
    (raw_dir / "airperm_project_reports.json").write_text(json.dumps(out, indent=1))
    return out


def airperm_dump_form() -> None:
    class F(HTMLParser):
        def handle_starttag(self, tag, attrs):
            a = dict(attrs)
            if tag in ("form", "input", "select", "option", "textarea"):
                print(tag, {k: a.get(k) for k in ("action", "method", "name", "id", "value", "type") if a.get(k)})

    F().feed(http(AIRPERM_START))


# --------------------------------------------------------------------------------------------------------------
# ECHO (optional)
# --------------------------------------------------------------------------------------------------------------


def echo_live(raw_dir: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for label, params in (("naics518210", {"p_ncs": "518210"}), ("sic7374", {"p_sic": "7374"}),
                          ("sic7374_alt", {"p_sic4": "7374"})):
        try:
            js = json.loads(http(f"{ECHO}.get_facilities?" + urllib.parse.urlencode(
                {"output": "JSON", "p_st": "TX", **params})))
            res = js.get("Results", {})
            qid = res.get("QueryID")
            log(f"ECHO {label}: QueryRows={res.get('QueryRows')} QueryID={qid} {res.get('Error') or ''}")
            if not qid:
                continue
            text = http(f"{ECHO}.get_download?" + urllib.parse.urlencode({"output": "CSV", "qid": qid}))
            (raw_dir / f"echo_{label}.csv").write_text(text, encoding="utf-8")
            for r in csv.DictReader(io.StringIO(text)):
                r["echo_query"] = label
                rows.append(r)
            if label == "sic7374":
                break
        except Exception as exc:  # noqa: BLE001
            log(f"ECHO {label}: {type(exc).__name__}: {str(exc)[:160]}")
    return rows


def filter_zip_csv(zip_path: Path, name_hint: str, raw_dir: Path, out_name: str) -> int:
    """Stream a CSV inside an ECHO ZIP and keep Texas rows with NAICS 518210 / SIC 7374 or a data-center name."""
    n = 0
    with zipfile.ZipFile(zip_path) as z:
        members = [m for m in z.namelist() if m.lower().endswith(".csv") and name_hint.lower() in m.lower()]
        if not members:
            log(f"{zip_path.name}: no CSV matching {name_hint!r}; members: {z.namelist()[:20]}")
            return 0
        with z.open(members[0]) as fh, open(raw_dir / out_name, "w", newline="", encoding="utf-8") as fo:
            rd = csv.DictReader(io.TextIOWrapper(fh, encoding="latin-1"))
            cols = rd.fieldnames or []
            st = next((c for c in cols if c.upper() in ("FAC_STATE", "STATE", "STATE_CODE")), None)
            nm = next((c for c in cols if c.upper() in ("FAC_NAME", "FACILITY_NAME", "PRIMARY_NAME")), None)
            codes = [c for c in cols if "NAICS" in c.upper() or "SIC" in c.upper()]
            w = csv.DictWriter(fo, fieldnames=cols)
            w.writeheader()
            for r in rd:
                if st and (r.get(st) or "").upper() != "TX":
                    continue
                code_txt = " ".join(r.get(c) or "" for c in codes)
                if "518210" in code_txt or re.search(r"\b7374\b", code_txt) or DC_NAME_RE.search(r.get(nm) or ""):
                    w.writerow(r)
                    n += 1
    log(f"{zip_path.name}:{members[0]} -> {raw_dir / out_name}: {n} Texas rows")
    return n


PSEI_ACCOUNT = "https://www.tceq.texas.gov/downloads/air-quality/point-source/{year}.xlsx"
PSEI_STATE_SUM = "https://www.tceq.texas.gov/downloads/air-quality/point-source/2010-2024-state-sum.xlsx"
CR_COASTAL_CSV = "https://data.austintexas.gov/api/v3/views/tzyg-j7q4/export.csv?accessType=DOWNLOAD"


def psei_live(raw_dir: Path, year: int) -> int:
    """TCEQ Point Source Emissions Inventory (sites above 30 TAC 101.10 thresholds): keep data-center-looking rows.
    Column names are not documented on the TCEQ page, so every sheet is scanned and every column is searched."""
    try:
        import openpyxl  # type: ignore
    except ImportError:
        log("PSEI: pip install openpyxl to read the inventory workbooks")
        return 0
    n = 0
    with open(raw_dir / f"psei_{year}_dc_rows.csv", "w", newline="", encoding="utf-8") as fo:
        w = None
        for url in (PSEI_ACCOUNT.format(year=year), PSEI_STATE_SUM):
            dest = raw_dir / url.rsplit("/", 1)[1]
            try:
                if not dest.exists():
                    dest.write_bytes(http(url, binary=True, timeout=600))
                wb = openpyxl.load_workbook(dest, read_only=True, data_only=True)
            except Exception as exc:  # noqa: BLE001
                log(f"PSEI {url}: {type(exc).__name__}: {str(exc)[:120]}")
                continue
            for ws in wb.worksheets:
                header = None
                for row in ws.iter_rows(values_only=True):
                    cells = ["" if v is None else str(v) for v in row]
                    if header is None:
                        if sum(1 for c in cells if c) >= 3:
                            header = cells
                        continue
                    txt = " ".join(cells)
                    if "518210" in txt or re.search(r"\b7374\b", txt) or DC_NAME_RE.search(txt):
                        if w is None:
                            w = csv.writer(fo)
                            w.writerow(["source_file", "sheet"] + header)
                        w.writerow([dest.name, ws.title] + cells)
                        n += 1
    log(f"PSEI: {n} data-center-looking rows -> psei_{year}_dc_rows.csv (check by hand: names like 'SAT' or 'TX 1' over-match)")
    return n


def cr_coastal_live(raw_dir: Path) -> int:
    """TCEQ Central Registry Files - Coastal & East Texas (Socrata tzyg-j7q4, regions 5/10/12/14). Columns unverified."""
    try:
        text = http(CR_COASTAL_CSV, timeout=600)
    except Exception as exc:  # noqa: BLE001
        log(f"Central Registry (Socrata tzyg-j7q4): {type(exc).__name__}: {str(exc)[:120]}")
        return 0
    rd = csv.DictReader(io.StringIO(text))
    n = 0
    with open(raw_dir / "central_registry_coastal_dc_rows.csv", "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=rd.fieldnames or [])
        w.writeheader()
        for r in rd:
            txt = " ".join(str(v) for v in r.values())
            if "518210" in txt or re.search(r"\b7374\b", txt) or DC_NAME_RE.search(txt):
                w.writerow(r)
                n += 1
    log(f"Central Registry coastal: {n} rows kept")
    return n


# --------------------------------------------------------------------------------------------------------------
# Merge
# --------------------------------------------------------------------------------------------------------------


def read_csv(p: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(open(p, encoding="utf-8"))) if p.exists() else []


def county_clean(s: str | None) -> str | None:
    if not s:
        return None
    s = re.sub(r"\s+COUNTY$", "", s.strip(), flags=re.I)
    return s.title() if s else None


GENERIC = {"data", "center", "centers", "datacenter", "llc", "inc", "lp", "l", "p", "co", "corp", "corporation",
           "the", "of", "and", "texas", "tx", "holdings", "services", "project", "site", "campus", "phase", "dc",
           "owner", "operator", "propco", "opco", "development", "group", "company", "technologies", "us", "america",
           "north", "south", "east", "west", "i", "ii", "iii", "iv", "v", "1", "2", "3", "4", "5", "6", "7", "8", "9",
           "10", "11", "12", "san", "antonio", "dallas", "austin", "houston", "fort", "worth", "el", "paso", "data",
           "building", "addition", "expansion", "new", "technology", "power", "energy", "digital", "cloud", "ltd"}


def toks(s: str) -> set[str]:
    return {t for t in re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).split() if t not in GENERIC and len(t) > 2}


def load_backlog(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        log(f"backlog {path} not found: Comptroller suggestions skipped")
        return []
    rows = [r for r in csv.DictReader(open(path, encoding="utf-8")) if r.get("admin_region") == "Texas"]
    for r in rows:
        r["_toks"] = toks(" ".join([r.get("name", ""), r.get("operator_or_owner", ""), r.get("occupant_or_tenant", "")]))
    return rows


def suggest(name: str, backlog: list[dict[str, str]], k: int = 3) -> str:
    t = toks(name)
    scored = []
    for b in backlog:
        sh = t & b["_toks"]
        if sh:
            scored.append((len(sh), b["backlog_id"], sorted(sh)))
    scored.sort(key=lambda x: -x[0])
    seen, out = set(), []
    for n, bid, sh in scored:
        if bid not in seen:
            seen.add(bid)
            out.append(f"{bid} [{'/'.join(sh)}]")
        if len(out) == k:
            break
    return "; ".join(out)


def frs_groups(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group interest rows by REGISTRY_ID; rows without one join the registry id that carries the same name."""
    name_to_reg: dict[str, str] = {}
    for r in rows:
        if r.get("REGISTRY_ID") and r.get("PRIMARY_NAME"):
            name_to_reg.setdefault(r["PRIMARY_NAME"], str(r["REGISTRY_ID"]))
    g: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        reg = str(r["REGISTRY_ID"]) if r.get("REGISTRY_ID") else name_to_reg.get(r.get("PRIMARY_NAME") or "")
        g[reg or f"name:{r.get('PRIMARY_NAME')}"].append(r)
    return g


def resolve_key(k: str, groups: dict[str, list[dict[str, Any]]]) -> str:
    """A curated 'name:X' key points at the registry group when the name was resolved to one."""
    if k.startswith("name:") and k not in groups:
        for gk, rs in groups.items():
            if not gk.startswith("name:") and any(r.get("PRIMARY_NAME") == k[5:] for r in rs):
                return gk
    return k


def frs_coord(rs: list[dict[str, Any]], key: str) -> tuple[float, float, str] | None:
    if key in COORD_REJECT:
        return None
    rank = {"AIR": 0, "EIS": 1, "CEDRI": 2, "TX-TCEQ ACR": 3, "NPDES": 4}
    best = None
    for r in rs:
        try:
            lat, lon = float(r["LATITUDE83"]), float(r["LONGITUDE83"])
        except (TypeError, ValueError, KeyError):
            continue
        rk = rank.get(r.get("PGM_SYS_ACRNM"), 9)
        if best is None or rk < best[0]:
            best = (rk, round(lat, 6), round(lon, 6), r.get("PGM_SYS_ACRNM"), r.get("PGM_SYS_ID"))
    if not best:
        return None
    _, lat, lon, prog, pid = best
    desc = {"AIR": "EPA FRS point for ICIS-Air record", "EIS": "EPA FRS point for EIS record",
            "CEDRI": "EPA FRS point for CEDRI record", "TX-TCEQ ACR": "EPA FRS point for TCEQ Central Registry RN",
            "NPDES": "EPA FRS point for TCEQ stormwater/NPDES record"}.get(prog, "EPA FRS point")
    return lat, lon, f"{desc} {pid} (FRS {key})"


def program_summary(rs: list[dict[str, Any]]) -> dict[str, str]:
    by: dict[str, set[str]] = defaultdict(set)
    for r in rs:
        if r.get("PGM_SYS_ACRNM") and r.get("PGM_SYS_ID"):
            by[r["PGM_SYS_ACRNM"]].add(r["PGM_SYS_ID"])
    other = []
    for prog in ("EIS", "CEDRI", "NPDES", "RCRAINFO", "ICIS"):
        if by.get(prog):
            other.append(f"{prog}:" + ",".join(sorted(by[prog])))
    return {"icis_air_ids": ";".join(sorted(by.get("AIR", []))), "rns": ";".join(sorted(by.get("TX-TCEQ ACR", []))),
            "other": "; ".join(other), "programs": ",".join(sorted(by))}


def auth_kind_from_programs(progs: str) -> str:
    p = set(progs.split(",")) if progs else set()
    if "AIR" in p:
        return "ICIS-Air record (TCEQ authorization type not in FRS)"
    if "EIS" in p or "CEDRI" in p:
        return "air emissions/engine reporting record (EIS/CEDRI); authorization not identified"
    if "NPDES" in p:
        return "construction stormwater/NPDES only; no air record in FRS"
    if "TX-TCEQ ACR" in p:
        return "TCEQ Central Registry RN only; no air record in FRS"
    return "other EPA program record"


def build(frs_rows: list[dict[str, Any]], auths: list[dict[str, str]], links: list[dict[str, str]],
          backlog: list[dict[str, str]]) -> list[dict[str, Any]]:
    groups = frs_groups(frs_rows)
    auth_by = {a["auth_key"]: a for a in auths}
    used_frs: set[str] = set()
    used_auth: set[str] = set()
    out = []
    for L in links:
        fkeys = [resolve_key(k.strip(), groups) for k in (L.get("frs_keys") or "").split(";") if k.strip()]
        akeys = [k.strip() for k in (L.get("auth_keys") or "").split(";") if k.strip()]
        rs = [r for k in fkeys for r in groups.get(k, [])]
        used_frs.update(fkeys)
        used_auth.update(akeys)
        A = [auth_by[k] for k in akeys if k in auth_by]
        missing = [k for k in akeys if k not in auth_by]
        rec = {c: None for c in OUT_COLUMNS}
        rec.update({"facility_key": L["facility_key"], "facility_name": L["facility_name"], "operator": L["operator"],
                    "backlog_id": L.get("backlog_ids") or None, "backlog_confidence": L.get("backlog_confidence") or None,
                    "backlog_basis": L.get("backlog_basis") or None, "backlog_candidates": L.get("backlog_candidates") or None})
        notes = [L.get("notes") or ""]
        if missing:
            notes.append("missing auth rows: " + ",".join(missing))
        # coordinates: TCEQ document first (Core Data Form / STEERS / permit DMS / plain-language summary), then FRS
        coord = None
        for a in A:
            if a.get("doc_lat") and a.get("doc_lon") and "courtesy" not in (a.get("doc_coord_basis") or "") \
                    and "marker" not in (a.get("doc_coord_basis") or ""):
                coord = (float(a["doc_lat"]), float(a["doc_lon"]), f"TCEQ {a['auth_key']}: {a['doc_coord_basis']}")
                break
        if coord is None:
            best = None
            for k in fkeys:
                c = frs_coord(groups.get(k, []), k)
                if c and (best is None or c[2].startswith("EPA FRS point for ICIS") and not best[2].startswith("EPA FRS point for ICIS")):
                    best = c
            coord = best
        if coord is None:
            for a in A:
                if a.get("doc_lat") and a.get("doc_lon"):
                    coord = (float(a["doc_lat"]), float(a["doc_lon"]), f"TCEQ {a['auth_key']}: {a['doc_coord_basis']}")
                    break
        if coord:
            rec["lat"], rec["lon"], rec["coord_source"] = coord
        ps = program_summary(rs)
        rns = [a["rn"] for a in A if a.get("rn")] + [x for x in ps["rns"].split(";") if x]
        rec["tceq_rn"] = ";".join(dict.fromkeys(rns)) or None
        rec["tceq_permit_numbers"] = "; ".join(f"{a['permit_no']}" for a in A if a.get("permit_no")) or None
        rec["tceq_project_numbers"] = ";".join(a["project_no"] for a in A if a.get("project_no")) or None
        rec["authorization_type"] = " | ".join(a["auth_type"] for a in A) or auth_kind_from_programs(ps["programs"])
        rec["authorization_status"] = " | ".join(f"{a['permit_no']}: {a['status']}" for a in A if a.get("status")) or None
        rec["permittee"] = "; ".join(dict.fromkeys(a["permittee"] for a in A if a.get("permittee"))) or None
        air_auths = [a for a in A if "stormwater" not in a["auth_type"] and not a["auth_type"].startswith("PUCT")]
        rec["air_record"] = "yes" if air_auths or ps["icis_air_ids"] else "utility regulator (PUCT) link" if A else (
            "reporting only (EIS/CEDRI)" if ("EIS" in ps["programs"] or "CEDRI" in ps["programs"]) else "no")
        gc = [a for a in A if a.get("generator_count")]
        rec["generator_count"] = sum(int(a["generator_count"]) for a in gc) if gc else None
        gm = [a for a in A if a.get("generator_mw")]
        rec["generator_mw"] = round(sum(float(a["generator_mw"]) for a in gm), 3) if gm else None
        rec["generator_basis"] = " | ".join(f"{a['auth_key']}: {a['unit_kw_basis']}" for a in A if a.get("unit_kw_basis")) or None
        first = rs[0] if rs else {}
        addr = next((a for a in A if a.get("address")), None)
        rec["address"] = (addr or {}).get("address") or first.get("LOCATION_ADDRESS")
        rec["city"] = next((a["city"] for a in A if a.get("city")), None) or (first.get("CITY_NAME") or "").title() or None
        rec["county"] = next((a["county"] for a in A if a.get("county")), None) or next(
            (county_clean(r.get("COUNTY_NAME")) for r in rs if r.get("COUNTY_NAME")), None) or (L.get("county") or None)
        rec["frs_registry_ids"] = ";".join(k for k in fkeys if not k.startswith("name:")) or None
        rec["icis_air_ids"] = ps["icis_air_ids"] or None
        rec["other_epa_ids"] = ps["other"] or None
        urls = [a["source_url"] for a in A if a.get("source_url")]
        for a in A:
            urls += re.findall(r"https?://\S+?\.pdf", a.get("note") or "")
        if rs:
            urls.append(f"{FRS}/0 (REGISTRY_ID {', '.join(k for k in fkeys if not k.startswith('name:')) or fkeys[0]})")
        rec["source_urls"] = " ; ".join(dict.fromkeys(urls)) or None
        rec["notes"] = "; ".join(n for n in notes if n) or None
        out.append(rec)
    # FRS facilities not covered by a curated link
    for key, rs in groups.items():
        if key in used_frs:
            continue
        name = rs[0].get("PRIMARY_NAME") or ""
        if SUPPORT_RE.search(name) or NOT_DC_RE.search(name) or not (DC_NAME_RE.search(name) or any(
                r.get("query", "").startswith(("naics", "L1", "L2")) for r in rs)):
            continue
        rec = {c: None for c in OUT_COLUMNS}
        ps = program_summary(rs)
        c = frs_coord(rs, key)
        if c:
            rec["lat"], rec["lon"], rec["coord_source"] = c
        rec.update({"facility_key": "frs-" + (key if not key.startswith("name:") else re.sub(r"\W+", "-", key[5:].lower()).strip("-")),
                    "facility_name": name.title(), "address": rs[0].get("LOCATION_ADDRESS"),
                    "city": (rs[0].get("CITY_NAME") or "").title() or None,
                    "county": next((county_clean(r.get("COUNTY_NAME")) for r in rs if r.get("COUNTY_NAME")), None),
                    "tceq_rn": ps["rns"] or None, "authorization_type": auth_kind_from_programs(ps["programs"]),
                    "air_record": "yes" if ps["icis_air_ids"] else ("reporting only (EIS/CEDRI)" if ("EIS" in ps["programs"] or "CEDRI" in ps["programs"]) else "no"),
                    "frs_registry_ids": key if not key.startswith("name:") else None, "icis_air_ids": ps["icis_air_ids"] or None,
                    "other_epa_ids": ps["other"] or None, "source_urls": f"{FRS}/0 ({key})",
                    "backlog_candidates": suggest(name, backlog) or None,
                    "notes": COORD_REJECT.get(key)})
        out.append(rec)
    # authorizations not attached to any curated facility (should be none; kept so nothing is lost)
    for a in auths:
        if a["auth_key"] not in used_auth:
            rec = {c: None for c in OUT_COLUMNS}
            rec.update({"facility_key": "auth-" + a["auth_key"], "facility_name": a["site_name"], "permittee": a["permittee"],
                        "county": a.get("county"), "tceq_permit_numbers": a.get("permit_no"), "authorization_type": a["auth_type"],
                        "authorization_status": a.get("status"), "air_record": "yes", "source_urls": a.get("source_url"),
                        "backlog_candidates": suggest(a["site_name"] + " " + a["permittee"], backlog) or None})
            out.append(rec)
    return out


def browser_list(sites: list[dict[str, Any]], auths: list[dict[str, str]]) -> list[dict[str, str]]:
    """One row per document (or document set) that only TCEQ Records Online (CFR, JavaScript) serves."""
    by_key = {s["facility_key"]: s for s in sites}
    links = read_csv(LINKS_CSV)
    auth_site = {}
    for L in links:
        for k in (L.get("auth_keys") or "").split(";"):
            if k.strip():
                auth_site[k.strip()] = L["facility_key"]
    rows = []

    def add(site_key: str | None, series: str, field: str, value: str, wanted: str, priority: int, why: str):
        s = by_key.get(site_key or "", {})
        rows.append({"priority": priority, "url": CFR_SEARCH, "record_series": series, "search_field": field,
                     "search_value": value, "document_wanted": wanted, "facility_key": site_key or "",
                     "facility_name": s.get("facility_name") or "", "backlog_id": s.get("backlog_id") or "", "why": why})

    for a in auths:
        site = auth_site.get(a["auth_key"])
        nums = [n.strip() for n in re.split(r"[;,]", a.get("permit_no") or "") if n.strip()]
        for n in nums:
            n2 = re.sub(r"^(?:PBR reg|NSR)\s*", "", n)
            if n2.upper().startswith("O") and n2[1:].isdigit():
                add(site, "AIR / Federal Operating Permit", "Primary ID", n2[1:].lstrip("0"),
                    f"issued Title V permit {n2} (final permit, SOB, technical review)", 2,
                    "Title V permit text and unit list; SOB/SOP on tceq.texas.gov may be the draft")
            elif n2.isdigit():
                issued = "issued" in (a.get("status") or "") or "exists" in (a.get("status") or "")
                add(site, "AIR / New Source Review Permit", "Primary ID", n2.lstrip("0"),
                    f"{a['auth_type']} {n2}: registration/permit file incl. engine table (count, kW, hours)",
                    1 if issued else 3, "generator count and kW are in the registration (PI-7/APD-CERT/PBR forms), not in any index")
            # PSD/GHG ids are covered by the NSR number of the same project
    for s in sites:
        for rn in [r for r in (s.get("tceq_rn") or "").split(";") if r]:
            add(s["facility_key"], "AIR / New Source Review Permit", "Central Registry RN", rn,
                "every NSR/PBR/standard-permit record filed under this RN", 2 if s.get("air_record") == "yes" else 4,
                "finds 106.511 registrations not listed anywhere else")
    # sites with an ICIS-Air id but no RN: first find the RN
    for s in sites:
        if s.get("icis_air_ids") and not s.get("tceq_rn"):
            rows.append({"priority": 2, "url": "https://www15.tceq.texas.gov/crpub/", "record_series": "Central Registry",
                         "search_field": "Regulated Entity name / address", "search_value": f"{s['facility_name']} | {s.get('address') or ''}",
                         "document_wanted": "RN number (then search CFR by RN)", "facility_key": s["facility_key"],
                         "facility_name": s["facility_name"], "backlog_id": s.get("backlog_id") or "",
                         "why": "ICIS-Air id known, RN not in FRS"})
    seen, uniq = set(), []
    for r in sorted(rows, key=lambda r: (r["priority"], r["facility_key"], r["search_value"])):
        k = (r["record_series"], r["search_field"], r["search_value"])
        if k not in seen:
            seen.add(k)
            uniq.append(r)
    return uniq


def write_csv(rows: list[dict[str, Any]], path: Path, cols: list[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in cols})


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fixture", action="store_true", help="no network: use fixtures/ captured 2026-10-22")
    ap.add_argument("--out", type=Path, default=HERE / "out")
    ap.add_argument("--backlog", type=Path, default=DEFAULT_BACKLOG, help="seed_sites_unlocated.csv (Comptroller rows)")
    ap.add_argument("--echo", action="store_true", help="also query EPA ECHO air_rest_services")
    ap.add_argument("--echo-exporter", type=Path, help="local echo_exporter.zip to filter")
    ap.add_argument("--icis-air", type=Path, help="local ICIS-AIR_downloads.zip to filter")
    ap.add_argument("--no-docs", action="store_true", help="live: skip TCEQ PDF downloads")
    ap.add_argument("--no-airperm", action="store_true", help="live: skip TCEQ airperm project reports")
    ap.add_argument("--psei", type=int, metavar="YEAR", help="also filter the TCEQ point-source emissions inventory (e.g. 2024)")
    ap.add_argument("--central-registry-coastal", action="store_true",
                    help="also filter TCEQ Central Registry Files - Coastal & East Texas (Socrata tzyg-j7q4)")
    ap.add_argument("--airperm-dump-form", action="store_true")
    args = ap.parse_args()

    if args.airperm_dump_form:
        airperm_dump_form()
        return
    args.out.mkdir(parents=True, exist_ok=True)
    raw = args.out / "raw"
    auths = read_csv(FIX / "tceq" / "tceq_authorizations.csv")
    links = read_csv(LINKS_CSV)
    backlog = load_backlog(args.backlog)
    summary: dict[str, Any] = {"mode": "fixture" if args.fixture else "live",
                               "run_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if args.fixture:
        frs_rows = frs_fixture()
    else:
        raw.mkdir(parents=True, exist_ok=True)
        frs_rows = frs_live(raw)
        if not args.no_docs:
            summary["tceq_docs"] = len(tceq_docs_live(auths, raw))
        if not args.no_airperm:
            rep = airperm_live(auths, raw)
            summary["airperm_reports_ok"] = sum(1 for r in rep if r["status"] == "ok")
        if args.echo:
            summary["echo_rows"] = len(echo_live(raw))
        if args.psei:
            summary["psei_rows"] = psei_live(raw, args.psei)
        if args.central_registry_coastal:
            summary["central_registry_coastal_rows"] = cr_coastal_live(raw)
    if args.echo_exporter:
        raw.mkdir(parents=True, exist_ok=True)
        summary["echo_exporter_rows"] = filter_zip_csv(args.echo_exporter, "ECHO_EXPORTER", raw, "echo_exporter_tx_dc.csv")
    if args.icis_air:
        raw.mkdir(parents=True, exist_ok=True)
        summary["icis_air_rows"] = filter_zip_csv(args.icis_air, "FACILIT", raw, "icis_air_tx_dc.csv")

    sites = build(frs_rows, auths, links, backlog)
    sites.sort(key=lambda s: (s["air_record"] != "yes", s["lat"] is None, s["facility_key"]))
    write_csv(sites, args.out / "tx_issued_sites.csv", OUT_COLUMNS)
    bl = browser_list(sites, auths)
    write_csv(bl, args.out / "BROWSER_LIST.csv", ["priority", "url", "record_series", "search_field", "search_value",
                                                   "document_wanted", "facility_key", "facility_name", "backlog_id", "why"])

    def ids(field: str, conf: set[str] | None = None) -> set[str]:
        got = set()
        for s in sites:
            b = [x for x in (s.get(field) or "").split(";") if x]
            c = (s.get("backlog_confidence") or "").split(";")
            for i, x in enumerate(b):
                cc = c[i] if i < len(c) and c[i] else (c[0] if c else "")
                if conf is None or cc in conf:
                    got.add(x.strip())
        return got

    air = [s for s in sites if s["air_record"] == "yes"]
    comp_rows = [b for b in backlog if "Comptroller" in (b.get("register") or "")]
    comp_ids = {b["backlog_id"] for b in comp_rows}
    matched = ids("backlog_id") & comp_ids if comp_ids else ids("backlog_id")
    with_xy = {x for s in sites if s["lat"] is not None for x in (s.get("backlog_id") or "").split(";") if x}
    with_mw = {x for s in sites if s["generator_mw"] for x in (s.get("backlog_id") or "").split(";") if x}
    with_air = {x for s in air for x in (s.get("backlog_id") or "").split(";") if x}
    with_gc = {x for s in sites if s["generator_count"] for x in (s.get("backlog_id") or "").split(";") if x}
    issued_re = re.compile(r"issued|effective|exists|renewal", re.I)
    with_issued = {x for s in sites if issued_re.search(s.get("authorization_status") or "")
                   for x in (s.get("backlog_id") or "").split(";") if x}
    summary.update({
        "comptroller_register_rows": len(comp_rows), "comptroller_distinct_ids": len(comp_ids),
        "comptroller_rows_matched_rowcount": sum(1 for b in comp_rows if b["backlog_id"] in matched),
        "comptroller_rows_matched_to_air_record_rowcount": sum(1 for b in comp_rows if b["backlog_id"] in with_air),
        "comptroller_rows_matched_with_coordinates_rowcount": sum(1 for b in comp_rows if b["backlog_id"] in with_xy),
        "comptroller_rows_matched_with_generator_mw_rowcount": sum(1 for b in comp_rows if b["backlog_id"] in with_mw),
        "comptroller_rows_matched_with_generator_count_rowcount": sum(1 for b in comp_rows if b["backlog_id"] in with_gc),
        "comptroller_rows_matched_to_issued_air_authorization_rowcount": sum(1 for b in comp_rows if b["backlog_id"] in with_issued),
    })
    summary.update({
        "frs_interest_rows": len(frs_rows), "facilities": len(sites),
        "facilities_with_air_authorization_or_icis_air": len(air),
        "air_facilities_with_coordinates": sum(1 for s in air if s["lat"] is not None),
        "facilities_with_coordinates": sum(1 for s in sites if s["lat"] is not None),
        "facilities_with_generator_count": sum(1 for s in sites if s["generator_count"]),
        "facilities_with_generator_mw": sum(1 for s in sites if s["generator_mw"]),
        "issued_air_authorizations": sum(1 for a in auths if re.search(r"issued|effective|exists|renewal", a.get("status") or "", re.I)),
        # facility level: an authorization whose status reads issued, effective, an existing registration,
        # or a renewal of an issued permit (drafts, pending and under-review do not count)
        "air_facilities_issued_effective_or_registered": sum(1 for s in air if issued_re.search(s.get("authorization_status") or "")),
        "air_facilities_issued_effective_or_registered_with_coordinates": sum(
            1 for s in air if issued_re.search(s.get("authorization_status") or "") and s["lat"] is not None),
        "comptroller_ids_matched": len(matched),
        "comptroller_ids_matched_high": len(ids("backlog_id", {"high"}) & (comp_ids or ids("backlog_id"))),
        "comptroller_ids_matched_with_coordinates": len(with_xy & (comp_ids or matched)),
        "browser_list_rows": len(bl),
    })
    (args.out / "tx_fetch_summary.json").write_text(json.dumps(summary, indent=1))
    log(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
