#!/usr/bin/env python3
"""Validate data/climate_trace_seed/measurements.csv against the vocabulary, the registers and the registry.

Run in CI after build_measurements.py. Prints every problem and exits non-zero if there is one.
Checks:
  header and unique measurement ids
  metric, unit and basis are in pipeline/measurement_vocab.json
  the unit's dimension is one the metric allows (metric descriptions start with their dimension names)
  value and value_high are plain numbers; value_canonical is what units.py gives
  periods are YYYY-MM-DD with start <= end
  source_url is an http(s) URL
  subject ids exist: site -> site_register.csv, entity -> entity_register.csv, entry -> registry
  entry_id, when given, exists in the registry
  registry-derived rows: value_as_published occurs verbatim in the entry's record or claim, and source_url is one of that side's sources
  site register: unique ids; every ct_source_id exists in the Climate TRACE seed file
"""
import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import units  # noqa: E402
from build_measurements import COLS, SITE_COLS  # noqa: E402

PKG = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "climate_trace_seed"
V = units.VOCAB
DIMS = set(V["dimensions"])
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def allowed_dims(metric: str) -> set:
    head = V["metrics"][metric].split(":")[0]
    found = {d for d in DIMS if re.search(rf"\b{d}\b", head)}
    return found


def main() -> int:
    probs = []
    rows = list(csv.DictReader(open(PKG / "measurements.csv", encoding="utf-8")))
    sites = list(csv.DictReader(open(PKG / "site_register.csv", encoding="utf-8")))
    ents = {r["entity_id"] for r in csv.DictReader(open(PKG / "entity_register.csv", encoding="utf-8"))}
    ct = {r["source_id"] for r in csv.DictReader(open(PKG / "datacenters_emissions_seed.csv", encoding="utf-8"))}
    entries = {}
    for p in (ROOT / "registry").glob("*.json"):
        if p.stem in ("guide", "standard", "sources"):
            continue
        for e in json.load(open(p, encoding="utf-8")):
            entries[e["id"]] = e
    if rows and list(rows[0].keys()) != COLS:
        probs.append("measurements.csv header differs from build_measurements.COLS")
    if sites and list(sites[0].keys()) != SITE_COLS:
        probs.append("site_register.csv header differs from build_measurements.SITE_COLS")
    site_ids = [s["site_id"] for s in sites]
    if len(site_ids) != len(set(site_ids)):
        probs.append("duplicate site ids in site_register.csv")
    for s in sites:
        if s["ct_source_id"] and s["ct_source_id"] not in ct:
            probs.append(f"site {s['site_id']}: ct_source_id {s['ct_source_id']} not in datacenters_emissions_seed.csv")
    site_ids = set(site_ids)
    seen = set()
    for i, r in enumerate(rows, 2):
        where = f"measurements.csv line {i} ({r['measurement_id']})"
        if r["measurement_id"] in seen:
            probs.append(f"{where}: duplicate measurement_id")
        seen.add(r["measurement_id"])
        m, u, b = r["metric"], r["unit"], r["basis"]
        if m not in V["metrics"]:
            probs.append(f"{where}: metric {m!r} not in vocabulary")
            continue
        if u not in V["units"]:
            probs.append(f"{where}: unit {u!r} not in vocabulary")
            continue
        if b not in V["bases"]:
            probs.append(f"{where}: basis {b!r} not in vocabulary")
        dims = allowed_dims(m)
        if dims and units.dimension(u) not in dims and m not in ("other",):
            probs.append(f"{where}: unit {u} ({units.dimension(u)}) does not fit metric {m} ({', '.join(sorted(dims))})")
        if m in ("other", "share_other", "count_other", "duration_other") and len(r["metric_detail"]) < 8:
            probs.append(f"{where}: metric {m} needs a metric_detail")
        try:
            float(r["value"])
        except ValueError:
            probs.append(f"{where}: value {r['value']!r} is not a number")
            continue
        if r["value_high"]:
            try:
                if float(r["value_high"]) < float(r["value"]):
                    probs.append(f"{where}: value_high below value")
            except ValueError:
                probs.append(f"{where}: value_high {r['value_high']!r} is not a number")
        vc, cu = units.to_canonical(r["value"], u)
        if units.fmt(vc) != r["value_canonical"] or (cu or "") != r["canonical_unit"]:
            probs.append(f"{where}: canonical value {r['value_canonical']} {r['canonical_unit']} differs from units.py ({units.fmt(vc)} {cu})")
        for k in ("period_start", "period_end"):
            if r[k] and not DATE.match(r[k]):
                probs.append(f"{where}: {k} {r[k]!r} not YYYY-MM-DD")
        if bool(r["period_start"]) != bool(r["period_end"]):
            probs.append(f"{where}: give both period dates or neither")
        elif r["period_start"] and r["period_start"] > r["period_end"]:
            probs.append(f"{where}: period starts after it ends")
        if not re.match(r"https?://", r["source_url"] or ""):
            probs.append(f"{where}: source_url is not a URL")
        st, sid = r["subject_type"], r["subject_id"]
        if st == "site" and sid not in site_ids:
            probs.append(f"{where}: site {sid} not in site_register.csv")
        elif st == "entity" and sid not in ents:
            probs.append(f"{where}: entity {sid} not in entity_register.csv")
        elif st == "entry" and sid not in entries:
            probs.append(f"{where}: entry {sid} not in the registry")
        elif st not in ("site", "entity", "entry"):
            probs.append(f"{where}: subject_type {st!r}")
        if r["entry_id"] and r["entry_id"] not in entries:
            probs.append(f"{where}: entry_id {r['entry_id']} not in the registry")
        if r["feed"].startswith("registry/"):
            e = entries.get(r["entry_id"], {})
            text = e.get(r["side"], "") or ""
            if r["value_as_published"] not in text:
                probs.append(f"{where}: {r['value_as_published']!r} not found verbatim in {r['entry_id']}.{r['side']}")
            srcs = {s["url"] for s in e.get("record_sources" if r["side"] == "record" else "claim_sources", [])}
            if r["source_url"] not in srcs:
                probs.append(f"{where}: source_url not among {r['entry_id']} {r['side']} sources")
    for p in probs[:200]:
        print(p)
    print(f"{len(probs)} problems in {len(rows)} measurements, {len(sites)} sites")
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main())
