#!/usr/bin/env python3
"""ERCOT large-load interconnection queue: status totals from ERCOT's own published PDFs.

WHAT ERCOT ACTUALLY PUBLISHES (inspected 2026-10-20)
-----------------------------------------------------
ERCOT does NOT publish a per-project, per-county, or machine-readable large-load queue
file. NPRR1267 ("Large Load Interconnection Status Report", approved by PUCT 2025-07-31,
https://www.ercot.com/mktrules/issues/NPRR1267) requires aggregate reporting only. The
ERCOT pages checked (https://www.ercot.com/services/rq/large-load-integration,
https://www.ercot.com/committees/tac/llwg, http://www.ercot.com/gridinfo/resource) link
no LLIS file or data product. The only public numbers are aggregate figures printed as
text in monthly PDFs and board/TAC decks. This script pulls those printed figures out of
the PDF text with fixed regexes, so the ledger's ERCOT numbers trace to a specific
sentence in a specific ERCOT PDF.

Documents inspected (all via the fetcher, 2026-10-20):
  * ERCOT Monthly, April 2026 (posted 2026-05-13), p.4 "Batch Study Process for Large Load
    Interconnections":
    https://www.ercot.com/files/docs/2026/05/13/ERCOT-Monthly-April-2026-FINAL.pdf
    -> total 445.8 GW; No Studies Submitted 321 GW; Under ERCOT Review 93.7 GW;
       Section 9.5 Requirements Met 22 GW; Observed Energized 5.9 GW;
       Approval to Energize but not Operational 3.2 GW.
  * Board "Interconnection and Grid Analysis Update", 2026-04-13, slides 2-3:
    https://www.ercot.com/files/docs/2026/04/13/9-Interconnection-and-Grid-Analysis-Update.pdf
    -> "approximately 410 GW of Large Loads seeking interconnection, of which ~87% are
       data centers" (as of March 26, 2026).
  * Monthly Operational Overview, August 2026 (posted 2026-09-16), p.9:
    https://www.ercot.com/files/docs/2026/09/16/ERCOT-Monthly-Operational-Overview-August-2026.pdf
    -> 9,456 MW received Approval to Energize; 4,316 MW non-simultaneous monthly peak.
  * Later "ERCOT Monthly" issues (e.g. June 2026,
    https://www.ercot.com/files/docs/2026/07/10/ERCOT-Monthly-June-2026-FINAL.pdf) switched
    to Batch Zero wording ("roughly 450+ gigawatts (GW) of requested load") with no
    status split. The September 2026 board "Interconnection and Grid Analysis Update"
    says large-load figures moved to a separate "Item 14: Batch Zero Update" deck.

"COLUMNS" FOUND
---------------
No table columns exist. Status labels as printed (they changed over time):
  2026: No Studies Submitted | Under ERCOT Review | Section 9.5 Requirements Met |
        Observed Energized | Approval to Energize but are not Operational
  2024 decks (LLI Queue Status Update PDFs): Planning Studies Approved | Approved to Energize
        (values appear only as chart labels there, so they are not parsed)

OUTPUTS
-------
  ercot_large_load_metrics.csv   one row per (document, metric): value in MW, the printed
                                 value and unit, and the matched sentence fragment
  ercot_large_load_summary.json  MW by status from ONE document (statuses from different
                                 documents are never mixed), latest total, latest
                                 data-centre share, latest approved-to-energize. by_county
                                 and data_centre_project_count are null because ERCOT
                                 does not publish them.

CAVEATS
-------
* Regex extraction from prose. The rules are built to drop a metric rather than attach a
  number to the wrong label: the nearest number in the same clause, each number used once,
  no other label in between. Every value is stored with the text it came from, so check
  ``matched_text`` when ERCOT changes wording.
* "Data-centre share" is ERCOT's own percentage. ERCOT publishes no per-project
  data-centre flag, so the ledger cannot count data-centre projects.
* No county breakdown is published (zone-level charts exist only as images).
* Discovery of new PDFs scrapes ERCOT index pages for /files/docs/YYYY/MM/DD/*.pdf links.
  Those pages are partly JS-rendered, and whether they list these PDFs was NOT verified
  from the build environment, so the verified PDFs above are always parsed as well. Pass --url for
  newer PDFs.

USAGE
-----
  python ercot_large_load.py --out out/                       # discover + known PDFs
  python ercot_large_load.py --url https://www.ercot.com/files/docs/.../X.pdf
  python ercot_large_load.py --fixture --out out/fixture_run  # offline parser test
"""

from __future__ import annotations

import io
import json
import re
from pathlib import Path

import pandas as pd

from _common import (
    FIXTURES,
    SchemaChangedError,
    SourceError,
    base_parser,
    fetch,
    log,
    run_main,
    run_meta,
    write_csv,
    write_json,
)

LANDING = "https://www.ercot.com/services/rq/large-load-integration"
KNOWN_PDFS = [
    "https://www.ercot.com/files/docs/2026/05/13/ERCOT-Monthly-April-2026-FINAL.pdf",
    "https://www.ercot.com/files/docs/2026/04/13/9-Interconnection-and-Grid-Analysis-Update.pdf",
    "https://www.ercot.com/files/docs/2026/09/16/ERCOT-Monthly-Operational-Overview-August-2026.pdf",
]
INDEX_PAGES = [
    "https://www.ercot.com/news/presentations",
    "https://www.ercot.com/committees/tac/llwg",
    "https://www.ercot.com/services/rq/large-load-integration",
]
DOC_NAME_RE = re.compile(
    r"(ERCOT-Monthly|Large-?Load|LLI|Interconnection-and-Grid-Analysis|Batch-Zero)", re.IGNORECASE
)
DOC_LINK_RE = re.compile(r"""(?:https?://(?:www\.)?ercot\.com)?(/files/docs/\d{4}/\d{2}/\d{2}/[^"'\s<>]+?\.pdf)""")

# ---------------------------------------------------------------------------------------
# Extraction rules
# ---------------------------------------------------------------------------------------

NUM = (
    r"(?P<num>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)(?P<plus>\+)?\s*"
    r"(?P<unit>gigawatts|megawatts|GW|MW)\b"
)
NUM_RE = re.compile(NUM, re.IGNORECASE)

# Order matters only for overlap resolution: longer, more specific labels win.
STATUS_LABELS = [
    ("approved_to_energize_not_operational",
     r"Approv(?:al|ed) to Energize,?\s+but\s+(?:are\s+|is\s+)?not\s+(?:yet\s+)?Operational"),
    ("approved_to_energize", r"Approv(?:al|ed) to Energize"),
    ("no_studies_submitted", r"No Studies Submitted"),
    ("under_ercot_review", r"Under ERCOT Review"),
    ("section_9_5_requirements_met", r"Section 9\.5 Requirements Met"),
    ("planning_studies_approved", r"Planning Studies Approved"),
    ("observed_energized", r"Observed Energized"),
]
STATUS_METRICS = {
    "no_studies_submitted",
    "under_ercot_review",
    "section_9_5_requirements_met",
    "planning_studies_approved",
    "observed_energized",
    "approved_to_energize_not_operational",
}

TOTAL_PATTERNS = [
    re.compile(r"totall?ing\s+(?P<approx>approximately\s+|roughly\s+|about\s+|~)?" + NUM, re.I),
    re.compile(r"(?P<approx>approximately\s+|roughly\s+|about\s+|~)?" + NUM
               + r"\s+of\s+Large\s+Loads?\s+seeking\s+interconnection", re.I),
    re.compile(r"(?P<approx>approximately\s+|roughly\s+|about\s+|~)?" + NUM
               + r"(?:\s*\((?:GW|MW)\))?\s+of\s+requested\s+load", re.I),
]
DC_SHARE_RE = re.compile(r"~?(?P<pct>\d+(?:\.\d+)?)\s*%\s*(?:are|were|is)?\s*data\s*cent(?:er|re)s?", re.I)
PEAK_RE = re.compile(r"non-simultaneous\s+monthly\s+peak\s+consumption\s+of\s+" + NUM, re.I)
NEW_REQ_RE = re.compile(r"received\s+(?P<n>\d[\d,]*)\s+new\s+LLI\s+(?:requests|submissions)", re.I)
AS_OF_RE = re.compile(r"as of (?P<d>[A-Z][a-z]+ \d{1,2}, \d{4})")


def _to_mw(num: str, unit: str) -> float:
    v = float(num.replace(",", ""))
    return v * 1000.0 if unit.lower() in ("gw", "gigawatts") else v


def _snip(text: str, a: int, b: int, pad: int = 60) -> str:
    return text[max(0, a - pad): min(len(text), b + pad)].strip()


def normalise_text(raw: str) -> str:
    t = raw.replace(" ", " ").replace("–", "-").replace("—", "-")
    t = re.sub(r"-\s*\n\s*", "-", t)  # re-join words split at a hyphenated line break
    return re.sub(r"\s+", " ", t).strip()


def extract_metrics(text: str) -> list[dict]:
    """Return metric dicts found in already-normalised text."""
    rows: list[dict] = []

    # --- status labels: resolve overlaps (longest label wins) ---
    hits = []
    for metric, pat in STATUS_LABELS:
        for m in re.finditer(pat, text, re.I):
            hits.append((m.start(), m.end(), metric))
    hits.sort(key=lambda h: (h[0], -(h[1] - h[0])))
    labels, last_end = [], -1
    for s, e, metric in hits:
        if s >= last_end:
            labels.append((s, e, metric))
            last_end = e

    nums = [(m.start(), m.end(), m) for m in NUM_RE.finditer(text)]
    used: set[int] = set()
    label_spans = [(s, e) for s, e, _ in labels]

    def label_between(a: int, b: int) -> bool:
        return any(a <= ls and le <= b for ls, le in label_spans)

    for s, e, metric in labels:
        window_start = max(0, s - 140)
        # do not reach back across a sentence boundary (". " followed by a capital)
        cut = [m.end() for m in re.finditer(r"[.;:]\s+(?=[A-Z])", text[window_start:s])]
        if cut:
            window_start += cut[-1]
        chosen = None
        for ns, ne, m in reversed(nums):
            if ne <= s and ns >= window_start and ns not in used and not label_between(ne, s):
                chosen = (ns, ne, m)
                break
        if chosen is None:  # table-like layout: number directly follows the label
            for ns, ne, m in nums:
                if ns >= e and ns not in used and re.fullmatch(r"[\s:,=()\-]{0,6}", text[e:ns]):
                    chosen = (ns, ne, m)
                    break
        if chosen is None:
            continue
        ns, ne, m = chosen
        used.add(ns)
        rows.append({
            "metric": metric,
            "value_mw": _to_mw(m.group("num"), m.group("unit")),
            "value_as_published": m.group("num") + (m.group("plus") or ""),
            "unit_as_published": m.group("unit"),
            "approximate": bool(m.group("plus")),
            "matched_text": _snip(text, min(ns, s), max(ne, e), pad=0),
        })

    for pat in TOTAL_PATTERNS:
        for m in pat.finditer(text):
            rows.append({
                "metric": "total_large_load_requests",
                "value_mw": _to_mw(m.group("num"), m.group("unit")),
                "value_as_published": m.group("num") + (m.group("plus") or ""),
                "unit_as_published": m.group("unit"),
                "approximate": bool(m.group("plus") or m.group("approx")),
                "matched_text": _snip(text, m.start(), m.end(), pad=40),
            })
    for m in DC_SHARE_RE.finditer(text):
        rows.append({
            "metric": "data_centre_share_pct",
            "value_mw": None,
            "value_pct": float(m.group("pct")),
            "value_as_published": m.group(0).strip(),
            "unit_as_published": "%",
            "approximate": m.group(0).strip().startswith("~"),
            "matched_text": _snip(text, m.start(), m.end(), pad=80),
        })
    for m in PEAK_RE.finditer(text):
        rows.append({
            "metric": "observed_non_simultaneous_peak",
            "value_mw": _to_mw(m.group("num"), m.group("unit")),
            "value_as_published": m.group("num"),
            "unit_as_published": m.group("unit"),
            "approximate": False,
            "matched_text": _snip(text, m.start(), m.end(), pad=40),
        })
    for m in NEW_REQ_RE.finditer(text):
        rows.append({
            "metric": "new_requests_count",
            "value_mw": None,
            "value_count": int(m.group("n").replace(",", "")),
            "value_as_published": m.group("n"),
            "unit_as_published": "requests",
            "approximate": False,
            "matched_text": _snip(text, m.start(), m.end(), pad=20),
        })
    as_of = AS_OF_RE.search(text)
    for r in rows:
        r["as_of_in_text"] = as_of.group("d") if as_of else None
    return rows


def pdf_text(data: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(data))
    return "\n".join((p.extract_text() or "") for p in reader.pages)


def posted_date(url: str) -> str | None:
    m = re.search(r"/files/docs/(\d{4})/(\d{2})/(\d{2})/", url)
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else None


def discover(limit: int) -> list[str]:
    found: set[str] = set()
    for page in INDEX_PAGES:
        try:
            html = fetch(page, expect="html").text()
        except SourceError as exc:
            log(f"  discovery: could not read {page}: {exc}")
            continue
        for m in DOC_LINK_RE.finditer(html):
            path = m.group(1)
            if DOC_NAME_RE.search(path):
                found.add("https://www.ercot.com" + path)
    ordered = sorted(found, key=lambda u: (posted_date(u) or "", u), reverse=True)
    log(f"  discovery: {len(ordered)} candidate PDFs on index pages; keeping newest {limit}")
    return ordered[:limit]


def build_outputs(docs: list[tuple[str, str, str]], fixture: bool, out: Path) -> dict:
    """docs: list of (source_url, local_label, normalised_text)."""
    rows = []
    for url, label, text in docs:
        metrics = extract_metrics(text)
        log(f"  {label}: {len(metrics)} metric(s)")
        for r in metrics:
            rows.append({"source_url": url, "posted_date": posted_date(url), "document": label, **r})
    cols = [
        "posted_date", "source_url", "document", "metric", "value_mw", "value_pct", "value_count",
        "value_as_published", "unit_as_published", "approximate", "as_of_in_text", "matched_text",
    ]
    df = pd.DataFrame(rows).reindex(columns=cols)
    df["value_count"] = df["value_count"].astype("Int64")
    df = df.sort_values(["posted_date", "document", "metric", "matched_text"], kind="mergesort")
    df = df.drop_duplicates(subset=["source_url", "metric", "value_as_published"])
    if df.empty:
        raise SchemaChangedError(
            "No large-load figures were found in any document. ERCOT has changed its wording "
            "or the PDFs are image-only. Inspect the PDFs and update the regexes in ercot_large_load.py."
        )
    write_csv(df, out / "ercot_large_load_metrics.csv")

    def latest(metric: str):
        sub = df[df.metric == metric].sort_values("posted_date", kind="mergesort")
        if sub.empty:
            return None
        r = sub.iloc[-1]
        return {
            "value_mw": r.value_mw if pd.notna(r.value_mw) else None,
            "value_pct": r.value_pct if pd.notna(r.value_pct) else None,
            "value_count": int(r.value_count) if pd.notna(r.value_count) else None,
            "as_published": (
                str(r.value_as_published) if r.unit_as_published == "%"
                else f"{r.value_as_published} {r.unit_as_published}"
            ),
            "approximate": bool(r.approximate),
            "as_of_in_text": r.as_of_in_text if pd.notna(r.as_of_in_text) else None,
            "posted_date": r.posted_date,
            "source_url": r.source_url,
            "matched_text": r.matched_text,
        }

    # Status snapshot: the newest single document carrying >=3 status metrics.
    snap = None
    for (url, pdate), g in sorted(
        df[df.metric.isin(STATUS_METRICS)].groupby(["source_url", "posted_date"]),
        key=lambda kv: kv[0][1] or "",
    ):
        if g.metric.nunique() >= 3:
            total = df[(df.source_url == url) & (df.metric == "total_large_load_requests")]
            stated = float(total.value_mw.iloc[0]) if not total.empty else None
            ssum = round(float(g.value_mw.sum()), 1)
            snap = {
                "source_url": url,
                "posted_date": pdate,
                "mw_by_status": {r.metric: r.value_mw for r in g.itertuples()},
                "sum_of_statuses_mw": ssum,
                "stated_total_mw_same_document": stated,
                # self-check: the parsed statuses should add up to the total printed in the same PDF
                "statuses_reconcile_with_stated_total": (
                    None if stated is None else abs(ssum - stated) <= 0.005 * stated
                ),
            }
    summary = {
        **run_meta(fixture, [{"url": u, "document": lbl} for u, lbl, _ in docs]),
        "what_this_is": "Aggregate large-load queue figures printed in ERCOT PDFs (no per-project file exists).",
        "status_snapshot": snap,
        "latest_total_large_load_requests": latest("total_large_load_requests"),
        "latest_data_centre_share_pct": latest("data_centre_share_pct"),
        "latest_approved_to_energize_cumulative": latest("approved_to_energize"),
        "latest_observed_non_simultaneous_peak": latest("observed_non_simultaneous_peak"),
        "by_county": None,
        "by_county_reason": "ERCOT publishes no county-level large-load figures (checked 2026-10-20).",
        "data_centre_project_count": None,
        "data_centre_project_count_reason": (
            "ERCOT publishes no per-project data-centre flag; only an aggregate percentage of MW."
        ),
        "outputs": ["ercot_large_load_metrics.csv"],
    }
    write_json(summary, out / "ercot_large_load_summary.json")
    return summary


def main() -> None:
    p = base_parser(__doc__.split("\n\n")[0])
    p.add_argument("--url", action="append", default=[], help="parse this ERCOT PDF (repeatable)")
    p.add_argument("--no-discover", action="store_true", help="do not scrape ERCOT index pages for new PDFs")
    p.add_argument("--max-docs", type=int, default=8, help="newest N discovered PDFs to parse (default 8)")
    args = p.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=True)

    docs: list[tuple[str, str, str]] = []
    if args.fixture:
        manifest = json.loads((FIXTURES / "ercot" / "manifest.json").read_text())
        for d in manifest["documents"]:
            if d.get("file") and (FIXTURES / "ercot" / d["file"]).exists():
                raw = pdf_text((FIXTURES / "ercot" / d["file"]).read_bytes())
                label = d["file"]
            else:
                raw = (FIXTURES / "ercot" / d["text_file"]).read_text()
                label = d["text_file"]
            docs.append((d["source_url"], label, normalise_text(raw)))
    else:
        urls = list(dict.fromkeys(args.url or []))
        if not args.url:
            if not args.no_discover:
                urls += discover(args.max_docs)
            urls += KNOWN_PDFS
            urls = list(dict.fromkeys(urls))
        failures = []
        for u in urls:
            log(f"Fetching {u}")
            try:
                f = fetch(u, expect="pdf", landing_page=LANDING)
            except SourceError as exc:
                log(f"  skipped: {exc}")
                failures.append(str(exc))
                continue
            docs.append((u, u.rsplit("/", 1)[-1], normalise_text(pdf_text(f.content))))
        if not docs:
            raise SourceError("No ERCOT PDF could be downloaded:\n  " + "\n  ".join(failures))

    summary = build_outputs(docs, args.fixture, out)
    snap = summary["status_snapshot"]
    log(f"Wrote {out/'ercot_large_load_metrics.csv'} and {out/'ercot_large_load_summary.json'}")
    if snap:
        log(f"  status snapshot from {snap['posted_date']}: {snap['mw_by_status']}")


if __name__ == "__main__":
    run_main(main)
