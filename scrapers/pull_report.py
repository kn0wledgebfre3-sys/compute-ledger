#!/usr/bin/env python3
"""Summarise a dated pulls folder as SUMMARY.md for the weekly pull request.

Usage: python3 scrapers/pull_report.py data/pulls/<date>
Prints the summary. If nothing is new and nothing failed, deletes the folder so no pull request is opened.
"""
import csv
import json
import shutil
import sys
from pathlib import Path

D = Path(sys.argv[1])
PARTS = [
    ("nei", "nei_summary.json", "nei_changes.csv", "EPA emissions inventory: datacenter facilities new to the ledger or changed",
     "Match each facility to a permit (site address, registration number in the name), then add it to sites/metered/va_nei_transcribed.csv."),
    ("ie_aer", "ie_aer_summary.json", "ie_aer_first_reading.csv", "Irish annual environmental reports not yet read (first reading attached)",
     "Open each PDF and check every value against Table 3 and Table 5 before adding the row to sites/metered/ireland_aer_transcribed.csv."),
    ("benchmarking", "benchmarking_summary.json", "benchmarking_changes.csv", "Benchmarking rows new to the ledger or changed",
     "Drop telephone exchanges and mixed buildings unless named datacenters; append the rest to sites/metered/benchmarking_transcribed.csv."),
    ("watch", "watch_summary.json", "watch_new.csv", "Watched pages: new items", "Follow the action column for each item."),
]


def count(p: Path) -> int:
    if not p.exists():
        return 0
    rows = list(csv.DictReader(open(p, encoding="utf-8")))
    return sum(1 for r in rows if list(r.keys()) != ["none"])


lines = [f"# Weekly pulls, {D.name}", "",
         "Nothing in this pull request changes the ledger's tables. Each item needs a person to read it against its document "
         "(the two-reading rule in CONTRIBUTING.md) and then edit the transcription named below; CI rebuilds everything from there.", ""]
total, failed, notes = 0, [], []
for sub, summ, changes, title, todo in PARTS:
    s = D / sub / summ
    n = count(D / sub / changes)
    total += n
    if s.exists():
        summary = json.load(open(s, encoding="utf-8"))
        failed += [f"{sub}: {f}" for f in summary.get("failures", [])]
        notes += [f"{sub}: {n}" for n in summary.get("notes", [])]
    lines += [f"## {title}: {n}", "", f"File: `{sub}/{changes}`. {todo}", ""]
if (D / "failures.txt").exists():
    failed += (D / "failures.txt").read_text().splitlines()
lines += ["## Failures", ""] + ([f"- {f}" for f in failed] or ["None."]) + [""]
if notes:
    lines += ["## Notes (not failures)", ""] + [f"- {n}" for n in notes] + [""]
if total == 0 and not failed:
    shutil.rmtree(D, ignore_errors=True)
    print("nothing new")
else:
    text = "\n".join(lines)
    (D / "SUMMARY.md").write_text(text, encoding="utf-8")
    print(text)
