#!/usr/bin/env python3
"""Validate the chain's edges and write the built table.

The ledger traces one chain: mine, refiner, fab, chip buyer, datacenter, its power, water and fuel, and the
hardware's end. Each link between two parties is one row of sites/chain/edges.csv, with the document that
states it. This script checks every row and writes data/chain/edges.csv (with a content-hashed edge_id and
the side, record or claim) and data/chain/summary.json (edges per leg, and which legs are still empty).

Usage: python3 pipeline/build_chain.py [--out DIR]
"""
from __future__ import annotations

import argparse
import csv
import glob
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V = json.load(open(ROOT / "pipeline" / "measurement_vocab.json", encoding="utf-8"))
SRC = ROOT / "sites" / "chain" / "edges.csv"
LEGS = ["mine_to_refiner", "refiner_to_maker", "fab_to_buyer", "memory_to_maker", "packaging_to_maker", "assembly_to_buyer", "chips_across_borders",
        "power_to_site", "fuel_to_site", "water_to_site", "site_to_tenant", "ownership", "hardware_to_end_of_life"]
COLS = ["edge_id", "leg", "from_type", "from_id", "from_name", "relation", "to_type", "to_id", "to_name", "period_start",
        "period_end", "basis", "side", "document_title", "document_url", "publisher", "document_date", "quoted_line",
        "entry_id", "notes", "second_read"]
IN_COLS = [c for c in COLS if c not in ("edge_id", "side")]
NODE_TYPES = {"site", "entity", "entry", "named"}
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def known_ids() -> dict:
    seed = ROOT / "data" / "climate_trace_seed"
    sites = {r["site_id"] for r in csv.DictReader(open(seed / "site_register.csv", encoding="utf-8"))}
    ents = {r["entity_id"] for r in csv.DictReader(open(ROOT / "sites" / "entity_register.csv", encoding="utf-8"))}
    entries = set()
    for f in glob.glob(str(ROOT / "registry" / "*.json")):
        d = json.load(open(f, encoding="utf-8"))
        if isinstance(d, list):
            entries |= {e["id"] for e in d if isinstance(e, dict) and "id" in e}
    return {"site": sites, "entity": ents, "entry": entries}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "data" / "chain"))
    a = ap.parse_args()
    ids = known_ids()
    rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
    header = next(csv.reader(open(SRC, encoding="utf-8")))
    probs = [] if header == IN_COLS else [f"edges.csv header must be {IN_COLS}"]
    out = []
    for i, r in enumerate(rows, 2):
        w = f"edges.csv line {i}"
        if r["leg"] not in LEGS:
            probs.append(f"{w}: leg {r['leg']!r} not one of {LEGS}")
        if r["relation"] not in V["relations"] or r["relation"].startswith("_"):
            probs.append(f"{w}: relation {r['relation']!r} not in the vocabulary")
        if r["basis"] not in V["bases"]:
            probs.append(f"{w}: basis {r['basis']!r} not in the vocabulary")
        for end in ("from", "to"):
            t, nid, name = r[f"{end}_type"], r[f"{end}_id"], r[f"{end}_name"]
            if t not in NODE_TYPES:
                probs.append(f"{w}: {end}_type {t!r} not one of {sorted(NODE_TYPES)}")
            elif t != "named" and nid not in ids[t]:
                probs.append(f"{w}: {end}_id {nid!r} not in the {t} register")
            if not name:
                probs.append(f"{w}: {end}_name is empty")
        if r["entry_id"] and r["entry_id"] not in ids["entry"]:
            probs.append(f"{w}: entry_id {r['entry_id']!r} not in the registry")
        for c in ("period_start", "period_end", "document_date"):
            if r[c] and not DATE.match(r[c]) and not (c == "document_date" and re.match(r"^\d{4}(-\d{2})?$", r[c])):
                probs.append(f"{w}: {c} {r[c]!r} is not a date")
        if not r["document_url"].startswith(("http://", "https://")):
            probs.append(f"{w}: no document URL")
        if not r["quoted_line"].strip() and r["basis"] != "derived":
            probs.append(f"{w}: quoted_line is empty (the phrase in the document that states the link)")
        side = "claim" if r["basis"] == "company_statement" else "record"
        key = "|".join(r[c] for c in IN_COLS if c not in ("notes", "second_read"))
        out.append({"edge_id": "e-" + hashlib.sha1(key.encode()).hexdigest()[:10], "side": side} | r)
    dup = [k for k, n in Counter(o["edge_id"] for o in out).items() if n > 1]
    if dup:
        probs.append(f"duplicate edges: {dup[:5]}")
    for p in probs[:100]:
        print(p)
    if probs:
        print(f"{len(probs)} problems in {len(rows)} edges")
        return 1
    od = Path(a.out)
    od.mkdir(parents=True, exist_ok=True)
    with open(od / "edges.csv", "w", encoding="utf-8", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
        wr.writeheader()
        wr.writerows(sorted(out, key=lambda o: (LEGS.index(o["leg"]), o["from_name"], o["to_name"], o["edge_id"])))
    by_leg = Counter(o["leg"] for o in out)
    summary = {"edges": len(out), "by_leg": {leg: by_leg.get(leg, 0) for leg in LEGS},
               "by_side": dict(sorted(Counter(o["side"] for o in out).items())),
               "legs_without_edges": [leg for leg in LEGS if not by_leg.get(leg)]}
    json.dump(summary, open(od / "summary.json", "w", encoding="utf-8"), indent=1)
    print(f"0 problems in {len(out)} edges; legs without edges: {', '.join(summary['legs_without_edges']) or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
