#!/usr/bin/env python3
"""Pull new Annual Environmental Reports (AERs) for Irish datacentre licences from the EPA's LEAP API.

What it does
  1. For every licence GUID in config/ie_leap_licences.json, lists documents classified
     'Annual Environmental Report' and compares their URLs with sites/metered/ireland_aer_transcribed.csv.
  2. Downloads each report the ledger has not read and makes a FIRST READING of Table 3 (Energy Used,
     GJ) and Table 5 (Water Used, m3) from the PDF text. Every value is written beside the line it came from.
  3. Searches licence profiles by operator name and lists licences that are not in the config yet.
  Outputs: ie_aer_new_documents.csv, ie_aer_first_reading.csv, ie_leap_unlisted_profiles.csv, ie_aer_summary.json.
  Nothing enters the ledger from here: a second reading by a person, against the PDF, is required
  before a row is added to sites/metered/ireland_aer_transcribed.csv (CONTRIBUTING.md, two-reading rule).

Source (inspected 2026-10-23; see sites/metered/ireland_aer_notes.md)
  GET {api_base}/Document/listbylicenceidfiltered?licence_id=<GUID>&classification=Annual%20Environmental%20Report
  GET {api_base}/LicenceProfile/licenceprofilesearchlist?search_term=<name>
  Report PDFs at https://leap.epa.ie/docs/<document id>.pdf. Only the `url` key of a document record
  has been confirmed; other keys are read if present.
"""
from __future__ import annotations

import csv
import io
import json
import re
from pathlib import Path
from urllib.parse import quote

from _common import FIXTURES, SourceError, base_parser, fetch, log, run_main, run_meta, write_json

HERE = Path(__file__).resolve().parent
CFG = json.load(open(HERE / "config" / "ie_leap_licences.json", encoding="utf-8"))
LEDGER = HERE.parent / "sites" / "metered" / "ireland_aer_transcribed.csv"
DOC_RE = re.compile(r"https?://leap\.epa\.ie/docs/[0-9A-Za-z-]+\.pdf")
LINES = {
    "electricity_gj": r"^\s*Electricity\s+([\d,]+(?:\.\d+)?)",
    "light_fuel_oil_gj": r"^\s*Light Fuel Oil\s+([\d,]+(?:\.\d+)?)",
    "natural_gas_gj": r"^\s*Natural Gas\s+([\d,]+(?:\.\d+)?)",
    "renewable_biomass_hvo_gj": r"^\s*Renewable Biomass\s+([\d,]+(?:\.\d+)?)",
    "total_energy_gj": r"^\s*Total Energy Used\s+([\d,]+(?:\.\d+)?)",
    "water_m3": r"^\s*Total Water Used\s+([\d,]+(?:\.\d+)?)",
}


def records(obj) -> list[dict]:
    """Every dict in a JSON response that carries a LEAP document URL."""
    out = []
    if isinstance(obj, dict):
        if any(isinstance(v, str) and DOC_RE.search(v) for v in obj.values()):
            out.append(obj)
        for v in obj.values():
            out += records(v)
    elif isinstance(obj, list):
        for v in obj:
            out += records(v)
    return out


def first_reading(text: str) -> dict:
    got = {}
    for k, pat in LINES.items():
        m = re.search(pat, text, re.M)
        got[k] = m.group(1) if m else ""
        got[k + "_line"] = m.group(0).strip() if m else ""
    m = re.search(r"Licen[cs]e Number:?\s*(P\d{4}-\d{2})", text)
    got["licence_in_text"] = m.group(1) if m else ""
    m = re.search(r"(?:reporting (?:year|period)[^\d]{0,40}|^)(20\d\d)\b", text, re.I | re.M)
    got["year_in_text"] = m.group(1) if m else ""
    return got


def pdf_text(data: bytes) -> str:
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            return "\n".join((p.extract_text() or "") for p in pdf.pages)
    except ImportError:
        from pypdf import PdfReader
        return "\n".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(data)).pages)


def main() -> None:
    ap = base_parser(__doc__)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    known = {r["document_url"] for r in csv.DictReader(open(LEDGER, encoding="utf-8"))}
    known_lic = set(CFG["licences"])
    new_docs, readings, unlisted, failures = [], [], [], []
    for lic, guids in CFG["licences"].items():
        for g in guids:
            url = f"{CFG['api_base']}/Document/listbylicenceidfiltered?licence_id={g}&classification=Annual%20Environmental%20Report"
            try:
                if a.fixture:
                    p = FIXTURES / "ie_leap" / f"{lic}_{g}.json"
                    if not p.exists():
                        continue
                    data = json.load(open(p, encoding="utf-8"))
                else:
                    data = fetch(url, expect="json").json()
            except SourceError as exc:
                failures.append(f"{lic} {g}: {exc}")
                continue
            for rec in records(data):
                doc = next(DOC_RE.search(v).group(0) for v in rec.values() if isinstance(v, str) and DOC_RE.search(v))
                if doc in known:
                    continue
                title = rec.get("title") or rec.get("document_name") or rec.get("name") or ""
                new_docs.append({"licence_no": lic, "licence_guid": g, "document_url": doc, "title": title,
                                 "record": json.dumps({k: v for k, v in rec.items() if isinstance(v, (str, int, float))}, sort_keys=True)})
    for d in new_docs:
        try:
            if a.fixture:
                p = FIXTURES / "ie_leap" / (d["document_url"].rsplit("/", 1)[1].replace(".pdf", ".txt"))
                text = p.read_text(encoding="utf-8")
            else:
                text = pdf_text(fetch(d["document_url"], expect="pdf").content)
        except (SourceError, OSError) as exc:
            failures.append(f"{d['document_url']}: {exc}")
            continue
        r = first_reading(text)
        readings.append({"licence_no": d["licence_no"], "document_url": d["document_url"], **r,
                         "status": "first reading only: a person must check every value against the PDF before it enters sites/metered/ireland_aer_transcribed.csv"})
    if not a.fixture:
        for term in CFG["search_terms"]:
            url = f"{CFG['api_base']}/LicenceProfile/licenceprofilesearchlist?search_term={quote(term)}"
            try:
                data = fetch(url, expect="json").json()
            except SourceError as exc:
                failures.append(f"search {term}: {exc}")
                continue
            for txt in re.findall(r"P\d{4}-\d{2}", json.dumps(data)):
                if txt not in known_lic and txt not in {u["licence_no"] for u in unlisted}:
                    unlisted.append({"licence_no": txt, "found_by_search_term": term})
    for name, rows in (("ie_aer_new_documents.csv", new_docs), ("ie_aer_first_reading.csv", readings), ("ie_leap_unlisted_profiles.csv", unlisted)):
        cols = list(rows[0].keys()) if rows else ["none"]
        with open(a.out / name, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
    write_json({**run_meta(a.fixture, [{"name": "EPA Ireland LEAP Open Data API", "url": CFG["api_base"]}]),
                "licences": len(CFG["licences"]), "new_documents": len(new_docs), "first_readings": len(readings),
                "unlisted_licence_profiles": len(unlisted), "failures": failures}, a.out / "ie_aer_summary.json")
    log(f"LEAP: {len(new_docs)} new reports, {len(readings)} first readings, {len(unlisted)} licences not yet listed")


if __name__ == "__main__":
    run_main(main)
