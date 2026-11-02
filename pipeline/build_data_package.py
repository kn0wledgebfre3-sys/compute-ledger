#!/usr/bin/env python3
"""Flat entry tables, schema check and data dictionary.

1. Writes data/climate_trace_seed/entries.csv and entry_sources.csv from registry/*.json (the entries as tables).
2. Checks every table listed in data/datapackage.json against its schema: the header must match the listed fields in
   order, required fields must be filled, enum fields must hold a listed value, vocab fields a key of
   pipeline/measurement_vocab.json, number/integer/date fields must parse. Any problem fails the build.
3. Writes data/DICTIONARY.md, the readable version of data/datapackage.json.

Standard library only. With --out DIR it writes the three files to DIR instead (CI compares them with the committed ones).
"""
import argparse
import csv
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REG = ROOT / "registry"
NOT_ENTRIES = ("sources.json", "guide.json", "standard.json")
ENTRY_COLS = ["id", "registry_file", "country", "region", "site_or_subject", "operator", "lat", "lon", "category", "record",
              "claim", "gap", "confidence", "verification_status", "verification_note", "last_checked", "receipt",
              "n_record_sources", "n_claim_sources"]
SOURCE_COLS = ["entry_id", "side", "title", "url", "publisher", "date", "date_note"]
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def entries():
    out, srcs = [], []
    for f in sorted(REG.glob("*.json")):
        if f.name in NOT_ENTRIES:
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        for e in (d if isinstance(d, list) else d.get("entries", [])):
            rs, cs = e.get("record_sources") or [], e.get("claim_sources") or []
            row = {c: e.get(c, "") for c in ENTRY_COLS if c not in ("registry_file", "n_record_sources", "n_claim_sources")}
            row.update(registry_file=f"registry/{f.name}", n_record_sources=len(rs), n_claim_sources=len(cs))
            row = {c: ("" if row[c] is None else row[c]) for c in ENTRY_COLS}
            out.append(row)
            for side, lst in (("record", rs), ("claim", cs)):
                for s in lst:
                    srcs.append({"entry_id": e["id"], "side": side, **{k: s.get(k, "") for k in SOURCE_COLS[2:]}})
    out.sort(key=lambda r: r["id"])
    return out, srcs


def to_csv(rows, cols):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=cols, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def check(pkg, vocab, override):
    problems = []
    for res in pkg["resources"]:
        path = DATA / res["path"]
        text = override.get(res["path"])
        if text is None:
            if not path.exists():
                problems.append(f"{res['path']}: file missing")
                continue
            text = path.read_text(encoding="utf-8")
        rows = list(csv.reader(io.StringIO(text)))
        header, body = rows[0], rows[1:]
        fields = res["schema"]["fields"]
        names = [f["name"] for f in fields]
        if header != names:
            problems.append(f"{res['path']}: columns {header} do not match the schema {names} (data/datapackage.json)")
            continue
        for i, r in enumerate(body, start=2):
            if len(r) != len(names):
                problems.append(f"{res['path']} line {i}: {len(r)} cells for {len(names)} columns")
                continue
            for f, v in zip(fields, r):
                where = f"{res['path']} line {i}, {f['name']}"
                if not v.strip():
                    if f.get("required"):
                        problems.append(f"{where}: required but empty")
                    continue
                if "enum" in f and v not in f["enum"]:
                    problems.append(f"{where}: {v!r} is not one of {f['enum']}")
                if "vocab" in f and v not in vocab[f["vocab"]]:
                    problems.append(f"{where}: {v!r} is not in measurement_vocab.json '{f['vocab']}'")
                t = f.get("type")
                try:
                    if t == "number":
                        float(v)
                    elif t == "integer":
                        int(v)
                except ValueError:
                    problems.append(f"{where}: {v!r} is not a {t}")
                if t == "date" and not DATE.match(v):
                    problems.append(f"{where}: {v!r} is not an ISO date")
        pk = res["schema"].get("primaryKey")
        if pk:
            k = names.index(pk)
            seen = {}
            for i, r in enumerate(body, start=2):
                if r[k] in seen:
                    problems.append(f"{res['path']} line {i}: {pk} {r[k]!r} repeats line {seen[r[k]]}")
                seen[r[k]] = i
    return problems


def dictionary(pkg, counts):
    L = ["# Data dictionary", "",
         "Generated from `data/datapackage.json` by `pipeline/build_data_package.py`; do not edit by hand. "
         "Every table below is checked against this schema on every build. Controlled values for `metric`, `unit`, `basis` "
         "and `relation` are listed, with definitions, in `pipeline/measurement_vocab.json`.", ""]
    for res in pkg["resources"]:
        L += [f"## `data/{res['path']}` ({counts.get(res['path'], 0):,} rows)", "", res["description"], "",
              "| Column | Type | Required | Values | Meaning |", "|---|---|---|---|---|"]
        for f in res["schema"]["fields"]:
            vals = ", ".join(f"`{x}`" for x in f["enum"] if x) + (" or empty" if "" in f.get("enum", []) else "") if "enum" in f else \
                (f"key of `{f['vocab']}` in the vocabulary" if "vocab" in f else "")
            L.append(f"| `{f['name']}` | {f['type']} | {'yes' if f.get('required') else ''} | {vals} | {f['description']} |")
        L.append("")
    return "\n".join(L).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="write the outputs here instead of data/ (CI compares)")
    a = ap.parse_args()
    pkg = json.loads((DATA / "datapackage.json").read_text(encoding="utf-8"))
    vocab = json.loads((ROOT / "pipeline" / "measurement_vocab.json").read_text(encoding="utf-8"))
    ents, srcs = entries()
    files = {"climate_trace_seed/entries.csv": to_csv(ents, ENTRY_COLS),
             "climate_trace_seed/entry_sources.csv": to_csv(srcs, SOURCE_COLS)}
    problems = check(pkg, vocab, files)
    ids = {r["measurement_id"] for r in csv.DictReader(open(DATA / "climate_trace_seed" / "measurements.csv", encoding="utf-8"))}
    for r in csv.DictReader(open(DATA / "climate_trace_seed" / "measurement_id_aliases.csv", encoding="utf-8")):
        if r["retired_measurement_id"] in ids:
            problems.append(f"measurement_id_aliases.csv: {r['retired_measurement_id']} is retired but still in measurements.csv")
        if r["measurement_id"] not in ids:
            problems.append(f"measurement_id_aliases.csv: {r['measurement_id']} (replacing {r['retired_measurement_id']}) is not in measurements.csv; "
                            "if it was corrected again, point the alias at the current id")
    counts = {}
    for res in pkg["resources"]:
        text = files.get(res["path"]) or (DATA / res["path"]).read_text(encoding="utf-8")
        counts[res["path"]] = sum(1 for _ in csv.reader(io.StringIO(text))) - 1
    files["DICTIONARY.md"] = dictionary(pkg, counts)
    out = Path(a.out) if a.out else DATA
    for rel, text in files.items():
        p = out / (Path(rel).name if a.out else rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    if problems:
        print(f"{len(problems)} schema problems:")
        for p in problems[:50]:
            print(" ", p)
        sys.exit(1)
    print(f"0 schema problems in {len(pkg['resources'])} tables ({sum(counts.values()):,} rows); {len(ents)} entries, {len(srcs)} entry sources")


if __name__ == "__main__":
    main()
