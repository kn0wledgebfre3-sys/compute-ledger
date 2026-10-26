#!/usr/bin/env python3
"""Compile every check run on the ledger, and every finding they made, into three files.

  review/CHECKS.csv                       hand-kept register: one row per check (who, what, how, where its findings are)
  -> data/climate_trace_seed/checks.csv   the register, with each check's counts computed from its findings file
  -> data/climate_trace_seed/findings.csv one row per finding, with what the data show now
  -> data/climate_trace_seed/checks_summary.json  totals, the random-sample results, findings per entry

`status_now` is computed from the current files at every build, except in two checks where it is recorded with the
finding: the documents fetched in a browser (the status on the fetch list) and the check of that work (its `resolution`
column). Elsewhere:
  - a finding that quotes entry or page text: whether that quoted text is still present where it was found;
  - a figure or link: whether a row with the same id (a hash of its value, subject, period, source and side) is still in
    the table; "confirmed at the check" when the reader found it as published with no problem noted;
  - a record-or-claim decision: which side the figure is on now (and its basis, for unattributed or wrong-basis figures);
  - a second reading of an entry: the entry's verification status now;
  - a Virginia permit: whether it now has resolved figures (the figures are in the finding).

Text no longer present means the passage was changed, not necessarily that the finding was right; text still present
means it was kept, either because the finding was answered another way or because it was not acted on. A figure "no
longer in the table in the form checked" changed in its value, subject, period, source, side or description, which may
be an unrelated later edit; one "still in the table as checked" was not changed. Checks recorded only as prose (the three
hostile reviews, the Texas check) have counts in the register, not rows here.
"""
import argparse
import csv
import glob
import hashlib
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REVIEW = ROOT / "review"
PKG = ROOT / "data" / "climate_trace_seed"
OUT = PKG

# entries whose company figures were left on the record side because they come from statutory filings (review/sides_2026-10-23/notes.md)
SIDES_KEPT = {"us-va-dominion-datacenter-demand-filed-2026", "se-stockholm-exergi-heat"}

COLS = ["finding_id", "check_id", "date", "subject_type", "subject_id", "entry_id", "location", "quoted", "finding",
        "severity", "status_now"]


def read(p):
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def norm(s):
    s = (s or "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace("—", "-").replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip().lower()


def short(s, n=300):
    s = re.sub(r"\s+", " ", s or "").strip()
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def quote_present(quoted, text):
    q = norm(quoted).strip("'\" ")
    parts = [p.strip(" '\".") for p in re.split(r"\.\.\.|…|\s\|\s", q) if len(p.strip(" '\".")) >= 12]
    if not parts:
        return None
    t = norm(text)
    return all(p in t for p in parts)


def load_entries():
    out = {}
    for f in sorted((ROOT / "registry").glob("*.json")):
        if f.name in ("guide.json", "standard.json", "sources.json"):
            continue
        d = json.load(open(f, encoding="utf-8"))
        for e in (d if isinstance(d, list) else d.get("entries", [])):
            if isinstance(e, dict) and e.get("id"):
                out[e["id"]] = e
    return out


def main():
    global OUT
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="write here instead of data/climate_trace_seed (CI compares)")
    a = ap.parse_args()
    if a.out:
        OUT = Path(a.out)
        OUT.mkdir(parents=True, exist_ok=True)

    register = read(REVIEW / "CHECKS.csv")
    dates = {c["check_id"]: c["date"] for c in register}
    entries = load_entries()
    meas = read(PKG / "measurements.csv")
    meas_ids = {r["measurement_id"] for r in meas}
    sides = defaultdict(set)
    for r in meas:
        if r["entry_id"]:
            sides[(r["entry_id"], r["value_as_published"])].add(r["side"])
    edges = {r["edge_id"]: r for r in read(ROOT / "data" / "chain" / "edges.csv")}
    meas_by_id = {r["measurement_id"]: r for r in meas}
    va_now = {r["registration"]: r for r in read(PKG / "va_permits_resolved.csv")}
    texts = {}

    def file_text(path):
        if path not in texts:
            p = ROOT / path
            texts[path] = p.read_text(encoding="utf-8") if p.is_file() else None
        return texts[path]

    rows = []

    def add(check, **k):
        r = {c: "" for c in COLS} | {"check_id": check, "date": dates[check]} | k
        r["quoted"] = short(r["quoted"], 240)
        r["finding"] = short(r["finding"], 400)
        rows.append(r)

    def trivial(problems):
        return not (problems or "").strip() or re.match(r"(none|no problem)\b", (problems or "").strip(), re.I)

    def fig_status(verdict, problems, mid, is_link=False):
        if verdict in ("found", "confirmed") and trivial(problems):
            return "confirmed at the check"
        present = (mid in edges) if is_link else (mid in meas_ids)
        return "still in the table as checked" if present else "no longer in the table in the form checked"

    # random samples and link reviews (measurements checks)
    for check, folder in (("measurements-2026-10-23", "measurements_check_2026-10-23"),
                          ("measurements-2026-10-23b", "measurements_check_2026-10-23b"),
                          ("measurements-2026-10-24", "measurements_check_2026-10-24"),
                          ("measurements-2026-10-24b", "measurements_check_2026-10-24b")):
        samp = {}
        for sp in glob.glob(str(REVIEW / folder / "*.csv")):
            if not sp.endswith("result.csv"):
                for s in read(sp):
                    samp[s.get("measurement_id") or s.get("edge_id")] = s
        by_row = {}
        if (REVIEW / folder / "links.csv").exists():  # this check numbers its links by row and its hours by registration
            for i, s in enumerate(read(REVIEW / folder / "links.csv"), start=1):
                by_row[("link", str(i))] = s
        if (REVIEW / folder / "hours.csv").exists():
            for s in read(REVIEW / folder / "hours.csv"):
                by_row[("hours", s["subject_id"].replace("usa-va-deq-", ""))] = s
        for r in read(REVIEW / folder / "result.csv"):
            kind = r.get("row_type") or r.get("part") or "figure"
            mid = r.get("measurement_id") or r.get("id")
            if (kind, mid) in by_row:
                s = by_row[(kind, mid)]
                mid = s.get("edge_id") or s.get("measurement_id")
            prob = r.get("logic_problems") or r.get("problems") or ""
            s = samp.get(mid, {}) or (edges.get(mid, {}) if kind == "link" else meas_by_id.get(mid, {}))
            subject = "link" if kind == "link" else ("generator hours" if kind == "hours" else "figure")
            add(check, subject_type=subject, subject_id=mid, entry_id=s.get("entry_id", ""),
                location=s.get("value_as_published") or (f"{s.get('from_name','')} {s.get('relation','')} {s.get('to_name','')}".strip()),
                quoted=r.get("quoted_from_document", ""), finding=r["verdict"] + ("" if trivial(prob) else f": {prob}"),
                severity=r["verdict"], status_now=fig_status(r["verdict"], prob, mid, kind == "link"))

    # system check B: fresh random sample (two readers)
    for half in ("B1", "B2"):
        smap = {}
        for sp in glob.glob(str(REVIEW / "system_check_2026-10-24" / "*.csv")):
            for s in read(sp):
                smap[s.get("measurement_id") or s.get("edge_id")] = s
        for r in read(REVIEW / "system_check_2026-10-24" / half / "result.csv"):
            s = smap.get(r["id"], {}) or edges.get(r["id"], {}) or meas_by_id.get(r["id"], {})
            add("system-check-B-2026-10-24", subject_type="link" if r["kind"] == "link" else "figure", subject_id=r["id"],
                entry_id=s.get("entry_id", ""), location=s.get("value_as_published", ""), quoted=r.get("quoted_from_document", ""),
                finding=r["verdict"] + ("" if trivial(r.get("problems")) else f": {r['problems']}") + (f" (severity given: {r['severity']})" if r.get("severity") else ""),
                severity=r["verdict"], status_now=fig_status(r["verdict"], r.get("problems"), r["id"], r["kind"] == "link"))

    # system check C: every entry
    for half in ("C1", "C2"):
        for r in read(REVIEW / "system_check_2026-10-24" / half / "result.csv"):
            named = [x for x in re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)+", r["entry_id"]) if x in entries]
            fld = r["field"].split("/")[0].strip()
            if not named:
                st = "not checkable (several entries named)"
            else:
                cur = " ".join((entries[x].get(fld) if isinstance(entries[x].get(fld), str) else json.dumps(entries[x], ensure_ascii=False)) for x in named)
                p = quote_present(r["quoted_text"], cur)
                st = "not checkable (no quotation)" if p is None else ("quoted text still present" if p else "quoted text no longer present")
            one = named[0] if len(named) == 1 and named[0] == r["entry_id"] else ""
            add("system-check-C-2026-10-24", subject_type="entry", subject_id=r["entry_id"], entry_id=one,
                location=r["field"], quoted=r["quoted_text"], finding=r["problem"], severity=r["severity"], status_now=st)

    # system check A and F: outward text
    def text_check(check, path_field, r, entry_id=""):
        paths = re.findall(r"[\w./-]+\.(?:md|html|json|csv|py)", r[path_field])
        repo = [p for p in paths if file_text(p) is not None]
        named = [x for x in re.findall(r"[a-z0-9]+(?:-[a-z0-9]+){2,}", r[path_field]) if x in entries]
        if named and not entry_id:
            entry_id = named[0]
            repo = repo + ["registry/" + next(f.name for f in (ROOT / "registry").glob("*.json") if f'"{named[0]}"' in f.read_text(encoding="utf-8"))]
        if not repo:
            st = "outside the repository (email drafts or the live page)"
        else:
            hits = [quote_present(r.get("quoted_text", ""), file_text(p)) for p in repo]
            st = "not checkable (no quotation)" if all(h is None for h in hits) else (
                "quoted text still present" if any(hits) else "quoted text no longer present")
        add(check, subject_type="text", subject_id=r[path_field], entry_id=entry_id, location=r.get("location", ""),
            quoted=r.get("quoted_text", ""), finding=r["problem"], severity=r.get("severity", ""), status_now=st)

    for r in read(REVIEW / "system_check_2026-10-24" / "A" / "result.csv"):
        text_check("system-check-A-2026-10-24", "file", r)
    for r in read(REVIEW / "system_check_2026-10-24" / "F" / "result.csv"):
        m = re.match(r"(error|inconsistency|weak)", r["problem"].lower())
        r = dict(r, severity=m.group(1) if m else "")
        text_check("system-check-F-2026-10-24", "file", r, r.get("entry_id", ""))

    # system check V: second reading of 40 entries
    for half in ("V1", "V2"):
        for r in read(REVIEW / "system_check_2026-10-24" / half / "result.csv"):
            e = entries.get(r["entry_id"], {})
            add("system-check-V-2026-10-24", subject_type="entry", subject_id=r["entry_id"], entry_id=r["entry_id"],
                location="second reading", finding=f"{r['status']}: {r.get('problems','')}".rstrip(": "), severity=r["status"],
                status_now=f"entry status now {e.get('verification_status', 'entry not found')}")

    # system check P: press and NGO figures on the record side
    for half in ("P1", "P2"):
        for r in read(REVIEW / "system_check_2026-10-24" / half / "result.csv"):
            row = meas_by_id.get(r["measurement_id"])
            now = {row["side"]} if row else sides.get((r["entry_id"], r["value_as_published"]), set())
            how = ""
            if not now:
                num = re.findall(r"\d[\d,.]*", r["value_as_published"])
                if num:
                    now = {x["side"] for x in meas if x["entry_id"] == r["entry_id"] and num[0] in x["value_as_published"]}
                    how = " (wording of the figure changed)" if now else ""
            st = ("now on the " + " and ".join(sorted(now)) + " side" + how) if now else "no longer in the table"
            if now and r["decision"] in ("unattributed", "mislabelled_basis"):
                bases = sorted({x["basis"] for x in meas if x["entry_id"] == r["entry_id"] and (x["measurement_id"] == r["measurement_id"] or x["value_as_published"] == r["value_as_published"])})
                st += (", basis " + "/".join(bases)) if bases else ""
            add("system-check-P-2026-10-24", subject_type="figure", subject_id=r["measurement_id"], entry_id=r["entry_id"],
                location=r["value_as_published"], quoted=r.get("quote", ""),
                finding=f"{r['decision']}: {r.get('whose_document_or_statement','')}".rstrip(": "), severity=r["decision"], status_now=st)

    # company statements on the record side (2026-10-23)
    for r in read(REVIEW / "sides_2026-10-23" / "company_in_record.csv"):
        now = sides.get((r["entry_id"], r["value_as_published"]), set())
        kept = r["entry_id"] in SIDES_KEPT
        add("sides-2026-10-23", subject_type="figure", subject_id=r["entry_id"], entry_id=r["entry_id"],
            location=r["value_as_published"], finding="company statement on the record side: " + r["metric_detail"]
            + ("; kept on the record because it comes from a statutory filing" if kept else ""),
            severity="keep_record" if kept else "move_to_claim", status_now=("now on the " + " and ".join(sorted(now)) + " side") if now else "no longer in the table")

    # Virginia: every permit where the two readings did not agree
    for r in read(PKG / "va_reread_comparison.csv"):
        if r["status"] == "agree":
            continue
        now = va_now.get(r["registration"], {})
        add("va-reread-2026-10-21", subject_type="permit", subject_id=r["registration"], entry_id="us-va-loudoun-diesel-backup-generators",
            location=f"registration {r['registration']}",
            finding=f"{r['status']}: first reading {r['pipeline_count'] or 'none'} units / {r['pipeline_mw'] or 'none'} MW; second reading {r['reread_count'] or 'none'} / {r['reread_mw'] or 'none'} MW; now {now.get('generator_count') or 'none'} units / {now.get('total_standby_mw') or 'none'} MW. {r['resolution_note']}",
            severity=r["status"],
            status_now="resolved against the permit text" if now.get("total_standby_mw") else "no figures (not a permit, or no document)")

    # documents fetched in a browser
    for r in read(REVIEW / "BROWSER_FETCH_LIST.csv"):
        if r["status_date"] == dates["browser-fetch-2026-10-24"] and r["status"] in ("obtained", "partial", "contradicts"):
            ent = r["ledger_entry_or_site"].split(" ")[0]
            add("browser-fetch-2026-10-24", subject_type="document", subject_id=r["save_as"],
                entry_id=ent if ent in entries else "", location=r["ledger_entry_or_site"], finding=r["result"],
                severity={"obtained": "document read", "partial": "document partly read", "contradicts": "document contradicts the entry"}[r["status"]],
                status_now="as recorded on the fetch list: " + r["status"])

    # checks whose findings file records each finding's resolution
    for check, path in (("browser-fetch-check-2026-10-24", "browser_fetch_2026-10-24/check_result.csv"),
                        ("checks-log-check-2026-10-24", "checks_log_check_2026-10-24/check_result.csv")):
        for r in read(REVIEW / path):
            m = re.match(r"([a-z0-9-]+-[a-z0-9-]+)", r["location"])
            ent = m.group(1) if m and m.group(1) in entries else ""
            add(check, subject_type="text", subject_id=r["file"], entry_id=ent, location=r["location"],
                finding=r["what_is_wrong"] + " Resolution: " + r["resolution"].split(": ", 1)[-1], severity=r["severity"],
                status_now="as recorded with the finding: " + r["resolution"].split(":")[0])

    seen = Counter()
    for r in rows:  # a hash of what was found, so the id does not change when status_now does
        fid = "f-" + hashlib.sha1("|".join(r[c] for c in COLS[1:-1]).encode("utf-8")).hexdigest()[:10]
        seen[fid] += 1
        r["finding_id"] = fid if seen[fid] == 1 else f"{fid}-{seen[fid]}"

    # per-check counts, written into the register's result where the register leaves it blank
    by_check = defaultdict(list)
    for r in rows:
        by_check[r["check_id"]].append(r)

    LABEL = {"found": "found as published", "found_different": "found with a different value", "not_in_document": "not in the cited document",
             "unreachable": "document not reached by the reader", "confirmed": "confirmed", "keep_record": "kept as reports of records",
             "move_to_claim": "moved to the claim", "unattributed": "unattributed", "mislabelled_basis": "wrong basis",
             "not_found": "primary not found", "contradicted": "contradicted", "verified": "verified", "partial": "partly verified",
             "error": "errors", "inconsistency": "inconsistencies", "weak": "weak", "style": "style", "obtained": "obtained",
             "contradicts": "contradicts the entry"}

    def counts(rs, key):
        return ", ".join(f"{n} {LABEL.get(k, k) if key == 'severity' else k}" for k, n in Counter(x[key] for x in rs).most_common())

    out_reg = []
    for c in register:
        rs = by_check.get(c["check_id"], [])
        c = dict(c)
        c["n_findings_in_table"] = str(len(rs)) if rs else ""
        c["findings_by_severity"] = counts(rs, "severity") if rs else ""
        c["status_now"] = counts(rs, "status_now") if rs else ""
        if not c["result"] and rs:
            c["result"] = f"{len(rs)} {'finding' if len(rs) == 1 else 'findings'}: " + counts(rs, "severity")
        out_reg.append(c)

    # random samples: figures and links drawn at random and re-read in their documents
    RANDOM_FIG = {"measurements-2026-10-23", "measurements-2026-10-23b", "measurements-2026-10-24", "system-check-B-2026-10-24"}
    RANDOM_LINK = {"measurements-2026-10-24", "system-check-B-2026-10-24"}
    figs = [r for r in rows if r["check_id"] in RANDOM_FIG and r["subject_type"] == "figure"]
    links = [r for r in rows if r["check_id"] in RANDOM_LINK and r["subject_type"] == "link"]

    def verdicts(rs):
        v = Counter(r["severity"] for r in rs)  # these checks' severity is the reader's verdict
        diff = [r for r in rs if r["severity"] in ("found_different", "not_in_document")]
        return {"n": len(rs), "verdicts": dict(v), "found_as_published": v.get("found", 0),
                "found_with_another_problem_noted": sum(1 for r in rs if r["severity"] == "found" and r["status_now"] != "confirmed at the check"),
                "differences": len(diff),
                "differences_no_longer_in_the_form_checked": sum(1 for r in diff if r["status_now"] == "no longer in the table in the form checked"),
                "differences_still_as_checked": sum(1 for r in diff if r["status_now"] == "still in the table as checked")}

    per_entry = defaultdict(lambda: defaultdict(int))
    for r in rows:
        if r["entry_id"]:
            per_entry[r["entry_id"]][r["check_id"]] += 1
    summary = {
        "checks": len(register), "findings_in_table": len(rows),
        "random_sample_figures": verdicts(figs), "random_sample_links": verdicts(links),
        "status_now": dict(Counter(r["status_now"] for r in rows).most_common()),
        "entries_with_findings": len(per_entry),
        "per_entry": {k: dict(sorted(v.items())) for k, v in sorted(per_entry.items())},
        "method": "\n\n".join(__doc__.split("\n\n")[2:]).strip(),
    }

    with open(OUT / "findings.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    with open(OUT / "checks.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out_reg[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(out_reg)
    with open(OUT / "checks_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1, ensure_ascii=False)
    print(f"{len(register)} checks, {len(rows)} findings; random figures {summary['random_sample_figures']['n']}, links {summary['random_sample_links']['n']}")


if __name__ == "__main__":
    main()
