#!/usr/bin/env python3
"""Watch pages that have no API and report what is new since the last run.

Config: config/watch_pages.json. State: one JSON file per page in --state-dir (default data/watch/),
holding the items seen so far. Each run writes:
  watch_new.csv       page, item, what a person should do with it
  watch_summary.json  items per page, failures
and updates the state files, so the next run reports only newer items. A first run on a page
records its current items as the baseline and reports none of them as new.

Modes
  links      every href matching `pattern` (and, if given, containing one of `keywords`)
  sentences  every sentence containing one of `keywords` and a digit; a changed figure shows as a new sentence
  probe      whether a URL built from `url` and each year in `years` answers with a page
"""
from __future__ import annotations

import csv
import html as htmllib
import json
import re
from pathlib import Path

from _common import FIXTURES, SourceError, base_parser, fetch, log, run_main, run_meta, write_json

HERE = Path(__file__).resolve().parent
CFG = json.load(open(HERE / "config" / "watch_pages.json", encoding="utf-8"))


def page_text(raw: str) -> str:
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    return " ".join(htmllib.unescape(re.sub(r"<[^>]+>", " ", raw)).split())


def items_for(p: dict, raw: str) -> set[str]:
    if p["mode"] == "links":
        found = set(re.findall(p["pattern"], raw))
        if p.get("keywords"):
            found = {f for f in found if any(k in f.lower() for k in p["keywords"])}
        return found
    if p["mode"] == "sentences":
        sents = re.split(r"(?<=[.!?])\s+", page_text(raw))
        return {s for s in sents if re.search(r"\d", s) and any(k in s.lower() for k in p["keywords"])}
    raise ValueError(p["mode"])


def main() -> None:
    ap = base_parser(__doc__)
    ap.add_argument("--state-dir", type=Path, default=HERE.parent / "data" / "watch")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    state_dir = a.out / "watch_state" if a.fixture else a.state_dir
    state_dir.mkdir(parents=True, exist_ok=True)
    new_rows, summary, failures = [], {}, []
    for p in CFG["pages"]:
        sf = state_dir / f"{p['name']}.json"
        seen = set(json.load(open(sf, encoding="utf-8"))["items"]) if sf.exists() else None
        try:
            if p["mode"] == "probe":
                now = set()
                for y in p["years"]:
                    url = p["url"].format(year=y)
                    if a.fixture:
                        continue
                    try:
                        fetch(url, expect="html")
                        now.add(url)
                    except SourceError:
                        pass
            elif a.fixture:
                f = FIXTURES / "watch" / f"{p['name']}.html"
                if not f.exists():
                    continue
                now = items_for(p, f.read_text(encoding="utf-8"))
            else:
                now = items_for(p, fetch(p["url"], expect="html").text())
        except SourceError as exc:
            failures.append(f"{p['name']}: {exc}")
            log(f"{p['name']}: {exc}")
            continue
        fresh = sorted(now - seen) if seen is not None else []
        for it in fresh:
            new_rows.append({"page": p["name"], "item": it, "action": p["action"]})
        summary[p["name"]] = {"items_now": len(now), "new": len(fresh), "baseline_run": seen is None}
        merged = sorted(now | (seen or set()))
        sf.write_text(json.dumps({"url": p["url"], "items": merged}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    with open(a.out / "watch_new.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["page", "item", "action"], lineterminator="\n")
        w.writeheader()
        w.writerows(new_rows)
    write_json({**run_meta(a.fixture, [{"name": "watched pages", "config": "config/watch_pages.json"}]),
                "pages": summary, "new_items": len(new_rows), "failures": failures}, a.out / "watch_summary.json")
    log(f"watch: {len(new_rows)} new items across {len(summary)} pages")


if __name__ == "__main__":
    run_main(main)
