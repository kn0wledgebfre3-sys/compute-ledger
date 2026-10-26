#!/usr/bin/env python3
"""Run the Virginia extractor on every real DEQ permit PDF and compare with the resolved figures.

What it runs: ``va_deq_permits.extract_from_pdf`` (PDF -> text layer -> quality gate ->
``extract_from_text``), i.e. the pipeline's own per-PDF code path. No list page, no network.

What it compares against: ``va_resolved.csv`` from the independent second read
(review/va_reread/), whose disagreements were resolved by hand against the permit text.

Classes (same rule as the second reader's comparison, review/va_reread/assemble.py, which produced
the 24 / 22 / 107 figures in REREAD_REPORT.md):
  agree          count equal and MW within 2 %
  minor          not agree, but (MW within 10 % and count within 2) or (MW within 2 % and count
                 within 2) or (MW within 10 % and count equal)
  disagree       anything else with both sides non-null
  pipeline-null  the extractor returned no count or no MW but the resolved file has figures
  resolved-null  no resolved figures (not a permit, or unreadable)
The summary also prints the looser reading "minor = MW within 10 % OR count within 2".

Usage:
  python3 tests/test_va_extraction.py                       # all PDFs, writes tests/va_extraction_vs_resolved.csv
  python3 tests/test_va_extraction.py --text-cache DIR      # cache PDF text (keyed by size+mtime) to iterate fast
  python3 tests/test_va_extraction.py --only 74272 74120    # a few registrations, prints their rows
  VA_PDF_DIR=... VA_RESOLVED_CSV=... python3 tests/test_va_extraction.py
It is also collected by pytest (test_va_extraction_against_resolved), which skips when the PDFs or
the resolved file are not present.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
PIPELINE = HERE.parent
sys.path.insert(0, str(PIPELINE))

import permit_text as PT  # noqa: E402
import va_deq_permits as VA  # noqa: E402

PDF_DIR = Path(os.environ.get("VA_PDF_DIR", str(PIPELINE / "pdfs_va")))
RESOLVED_CSV = Path(os.environ.get("VA_RESOLVED_CSV", str(PIPELINE.parent / "review" / "va_reread" / "va_resolved.csv")))
OUT_CSV = HERE / "va_extraction_vs_resolved.csv"

OUT_FIELDS = [
    "registration", "status", "status_loose",
    "pipeline_count", "pipeline_mw", "pipeline_mw_min", "pipeline_mw_max",
    "resolved_count", "resolved_mw", "count_diff", "mw_diff", "mw_diff_pct",
    "generator_count_confidence", "total_mw_confidence", "resolved_confidence",
    "text_quality", "generator_rows_uncounted", "unit_kw_list", "extract_reason", "resolved_basis",
]


def _f(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return None if v != v else v  # NaN -> None


def classify(pc, pm, rc, rm) -> tuple[str, str]:
    """(status, status_loose). See module docstring."""
    if rc is None or rm is None:
        return "resolved-null", "resolved-null"
    if pc is None or pm is None:
        return "pipeline-null", "pipeline-null"
    tol = max(rm, 1e-9)
    mw2 = abs(pm - rm) <= 0.02 * tol
    mw10 = abs(pm - rm) <= 0.10 * tol
    dc = abs(pc - rc)
    if mw2 and dc == 0:
        return "agree", "agree"
    loose = "minor" if (mw10 or dc <= 2) else "disagree"
    if (mw10 and dc <= 2) or (mw2 and dc <= 2) or (mw10 and dc == 0):
        return "minor", loose
    return "disagree", loose


def load_resolved(path: Path = RESOLVED_CSV) -> dict[str, dict]:
    out = {}
    with open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            out[str(r["registration"]).strip()] = r
    return out


def is_pdf(path: Path) -> bool:
    with open(path, "rb") as fh:
        return fh.read(5).startswith(b"%PDF")


def _inputs_for(pdf: Path, cache_dir: Path | None) -> tuple[str, list]:
    """(text, tables) exactly as the pipeline reads them from the PDF; optionally cached on disk,
    keyed by the PDF's size/mtime and the bytecode of the two PDF readers."""
    if cache_dir is None:
        return PT.pdf_to_text(pdf), PT.pdf_to_tables(pdf)
    st = pdf.stat()
    code = PT.pdf_to_text.__code__.co_code.hex() + PT.pdf_to_tables.__code__.co_code.hex()
    key = hashlib.sha1(f"{pdf.resolve()}|{st.st_size}|{st.st_mtime_ns}|{code}".encode()).hexdigest()[:16]
    cp = cache_dir / f"{pdf.stem}.{key}.json"
    if cp.exists():
        d = json.loads(cp.read_text(encoding="utf-8"))
        return d["text"], d["tables"]
    text, tables = PT.pdf_to_text(pdf), PT.pdf_to_tables(pdf)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cp.write_text(json.dumps({"text": text, "tables": tables}), encoding="utf-8")
    return text, tables


def _run_one(args) -> tuple[str, dict, list]:
    pdf, cache_dir = args
    if cache_dir is None:
        rec, rows = VA.extract_from_pdf(pdf)
    else:
        text, tables = _inputs_for(pdf, cache_dir)
        rec, rows = VA.extract_permit_text(text, tables)
    return pdf.stem, rec, rows


def run(pdf_dir: Path = PDF_DIR, resolved_csv: Path = RESOLVED_CSV, cache_dir: Path | None = None,
        only: list[str] | None = None, jobs: int = 2, out_csv: Path | None = OUT_CSV, verbose: bool = False) -> dict:
    resolved = load_resolved(resolved_csv)
    pdfs = sorted(p for p in pdf_dir.glob("*.pdf") if not only or p.stem in only)
    skipped = [p.name for p in pdfs if not is_pdf(p)]
    pdfs = [p for p in pdfs if is_pdf(p)]
    t0 = time.time()
    if jobs > 1 and len(pdfs) > 4:
        with ProcessPoolExecutor(max_workers=jobs) as ex:
            results = list(ex.map(_run_one, [(p, cache_dir) for p in pdfs], chunksize=2))
    else:
        results = [_run_one((p, cache_dir)) for p in pdfs]
    out_rows = []
    for reg, rec, rows in results:
        res = resolved.get(reg, {})
        pc, pm = _f(rec.get("generator_count")), _f(rec.get("total_standby_mw"))
        rc, rm = _f(res.get("generator_count")), _f(res.get("total_standby_mw"))
        st, st_loose = classify(pc, pm, rc, rm)
        out_rows.append({
            "registration": reg, "status": st, "status_loose": st_loose,
            "pipeline_count": None if pc is None else int(pc), "pipeline_mw": pm,
            "pipeline_mw_min": _f(rec.get("total_standby_mw_min")), "pipeline_mw_max": _f(rec.get("total_standby_mw_max")),
            "resolved_count": None if rc is None else int(rc), "resolved_mw": rm,
            "count_diff": None if pc is None or rc is None else int(pc - rc),
            "mw_diff": None if pm is None or rm is None else round(pm - rm, 3),
            "mw_diff_pct": None if pm is None or not rm else round(100 * (pm - rm) / rm, 1),
            "generator_count_confidence": rec.get("generator_count_confidence"),
            "total_mw_confidence": rec.get("total_mw_confidence"),
            "resolved_confidence": res.get("resolved_confidence"),
            "text_quality": rec.get("text_quality"),
            "generator_rows_uncounted": rec.get("generator_rows_uncounted"),
            "unit_kw_list": rec.get("unit_kw_list"),
            "extract_reason": rec.get("extract_reason"),
            "resolved_basis": (res.get("basis") or "")[:300],
        })
        if verbose:
            print(f"\n=== {reg}: pipeline {pc} / {pm} MW  vs resolved {rc} / {rm} MW -> {st}")
            for r in rows:
                print(f"   {r['count']!s:>4} x {r['kw_each']!s:>7} [{r['kw_min']}-{r['kw_max']}] src={r['count_source']:<15} "
                      f"conf={r['count_confidence']:<6} refs={r['refs']!r}  desc={r['description'][:90]!r}")
    if out_csv is not None:
        out_csv.parent.mkdir(parents=True, exist_ok=True)
        with open(out_csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=OUT_FIELDS, lineterminator="\n")
            w.writeheader()
            for r in out_rows:
                w.writerow(r)

    def tally(key):
        c: dict[str, int] = {}
        for r in out_rows:
            c[r[key]] = c.get(r[key], 0) + 1
        return c

    both = [r for r in out_rows if r["resolved_mw"] is not None]
    summary = {
        "pdfs": len(pdfs) + len(skipped), "skipped_not_pdf": skipped, "compared": len(out_rows),
        "status": tally("status"), "status_loose": tally("status_loose"),
        "pipeline_mw_sum": round(sum(r["pipeline_mw"] or 0 for r in out_rows), 1),
        "pipeline_count_sum": int(sum(r["pipeline_count"] or 0 for r in out_rows)),
        "resolved_mw_sum": round(sum(r["resolved_mw"] or 0 for r in both), 1),
        "resolved_count_sum": int(sum(r["resolved_count"] or 0 for r in both)),
        "mw_confidence": tally("total_mw_confidence"),
        "seconds": round(time.time() - t0, 1),
        "rows": out_rows,
    }
    # how honest is the confidence? status by total_mw_confidence
    by_conf: dict[str, dict[str, int]] = {}
    for r in out_rows:
        d = by_conf.setdefault(str(r["total_mw_confidence"]), {})
        d[r["status"]] = d.get(r["status"], 0) + 1
    summary["status_by_confidence"] = by_conf
    hi = [r for r in out_rows if r["total_mw_confidence"] == "high" and r["resolved_mw"] is not None]
    summary["high_conf_agree"] = f"{sum(r['status'] == 'agree' for r in hi)}/{len(hi)}"
    return summary


def print_summary(s: dict) -> None:
    order = ["agree", "minor", "disagree", "pipeline-null", "resolved-null"]
    print(f"PDFs: {s['pdfs']} (skipped, not a PDF: {', '.join(s['skipped_not_pdf']) or 'none'}); compared: {s['compared']}")
    print("status:       " + "  ".join(f"{k} {s['status'].get(k, 0)}" for k in order))
    print("status_loose: " + "  ".join(f"{k} {s['status_loose'].get(k, 0)}" for k in order)
          + "   (minor = MW within 10% OR count within 2)")
    print(f"fleet: pipeline {s['pipeline_mw_sum']:,} MW / {s['pipeline_count_sum']:,} units;"
          f" resolved {s['resolved_mw_sum']:,} MW / {s['resolved_count_sum']:,} units")
    print("total_mw_confidence: " + ", ".join(f"{k} {v}" for k, v in sorted(s["mw_confidence"].items(), key=lambda kv: str(kv[0]))))
    print(f"high-confidence permits that agree: {s['high_conf_agree']}")
    for conf in ("high", "medium", "low", "none"):
        d = s["status_by_confidence"].get(conf, {})
        if d:
            print(f"  {conf:<7} " + "  ".join(f"{k} {v}" for k, v in sorted(d.items())))
    bad = [r for r in s["rows"] if r["status"] in ("disagree", "pipeline-null", "minor")]
    if bad:
        print("\nnot agreeing (registration: pipeline count/MW vs resolved count/MW [status, pipeline MW confidence]):")
        for r in sorted(bad, key=lambda r: (r["status"], r["registration"])):
            print(f"  {r['registration']}: {r['pipeline_count']}/{r['pipeline_mw']} vs {r['resolved_count']}/{r['resolved_mw']}"
                  f" [{r['status']}, {r['total_mw_confidence']}]")
    print(f"\n({s['seconds']} s)")


def test_va_extraction_against_resolved():
    """pytest entry point: skips without the real PDFs; otherwise checks the fixed extractor has not
    regressed below the agreement recorded in README.md (Fixed 2026-10-22)."""
    try:
        import pytest  # noqa: F401
    except ImportError:  # pragma: no cover
        pytest = None
    if not PDF_DIR.is_dir() or not RESOLVED_CSV.exists():
        if pytest:
            pytest.skip("real VA permit PDFs / resolved CSV not available")
        return
    s = run(out_csv=None)
    st = s["status"]
    assert st.get("agree", 0) >= MIN_AGREE, st
    assert st.get("pipeline-null", 0) <= MAX_PIPELINE_NULL, st
    assert st.get("disagree", 0) == 0, st
    hi_ok, hi_n = (int(x) for x in s["high_conf_agree"].split("/"))
    assert hi_ok == hi_n, f"a high-confidence figure disagrees with the resolved one: {s['high_conf_agree']}"


# floor for the regression test: the agreement reached on 2026-10-22 (README "Fixed 2026-10-22")
MIN_AGREE = 178
MAX_PIPELINE_NULL = 2


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pdf-dir", type=Path, default=PDF_DIR)
    ap.add_argument("--resolved", type=Path, default=RESOLVED_CSV)
    ap.add_argument("--text-cache", type=Path, help="cache extracted PDF text here (speeds up repeated runs)")
    ap.add_argument("--only", nargs="*", help="registrations to run (prints their generator rows)")
    ap.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1))
    ap.add_argument("--out", type=Path, default=OUT_CSV, help="comparison CSV (default tests/va_extraction_vs_resolved.csv)")
    a = ap.parse_args()
    out_csv = None if a.only else a.out
    s = run(a.pdf_dir, a.resolved, a.text_cache, a.only, a.jobs, out_csv, verbose=bool(a.only))
    print_summary(s)
    if out_csv:
        print(f"wrote {out_csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
