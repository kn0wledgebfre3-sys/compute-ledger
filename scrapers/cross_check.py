#!/usr/bin/env python3
"""Cross-checks: one neutral sentence per region, built only from the other scripts' summaries.

Reads (from --in, default out/):
  ercot_large_load_summary.json   (ercot_large_load.py)
  pjm_queue_summary.json          (pjm_queue.py)
  iso_queues_summary.json         (miso_spp_nyiso_queues.py)
  eia_summary.json                (eia_860_923.py)
  neso_demand_summary.json        (neso_demand.py)
Writes: cross_checks.json (to --out).

Sentences state quantities and their sources side by side. They make no causal claim
(nothing says gas was built "for" data centres). Every figure is copied from a summary
file, with that file's mode (live/fixture) and source URLs attached.

--fixture: runs every scraper in --fixture mode into <out>/fixture_inputs/ first, then
builds the sentences from those outputs. Every sentence is then prefixed
"[FIXTURE DATA - NOT REAL]" and the file's top-level data_mode is "fixture". The same label
applies whenever ANY input summary was produced in fixture mode ("mixed").

USAGE
-----
  python cross_check.py --in out/ --out out/
  python cross_check.py --fixture --out out/fixture_run
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from _common import HERE, base_parser, log, run_main, write_json

INPUTS = {
    "ercot": "ercot_large_load_summary.json",
    "pjm": "pjm_queue_summary.json",
    "iso": "iso_queues_summary.json",
    "eia": "eia_summary.json",
    "neso": "neso_demand_summary.json",
}
SCRIPTS = ["ercot_large_load.py", "pjm_queue.py", "miso_spp_nyiso_queues.py", "eia_860_923.py", "neso_demand.py"]
FIXTURE_LABEL = "[FIXTURE DATA - NOT REAL] "


def fmt(mw) -> str:
    if mw is None:
        return "n/a"
    mw = float(mw)
    return f"{mw / 1000:,.1f} GW" if abs(mw) >= 1000 else f"{mw:,.0f} MW"


def load_inputs(src: Path) -> dict:
    data = {}
    for k, name in INPUTS.items():
        p = src / name
        data[k] = json.loads(p.read_text()) if p.exists() else None
        if data[k] is None:
            log(f"  missing input {p}")
    return data


def _active_gas(rows: list[dict] | None, state: str, mw_key: str) -> float:
    return sum((r.get(mw_key) or 0.0) for r in (rows or [])
               if r.get("state") == state and r.get("fuel_group") == "gas")


def _eia_state(eia: dict | None, st: str) -> dict | None:
    if not eia:
        return None
    return (eia.get("capacity_860m") or {}).get("by_state", {}).get(st)


def _eia_phrase(eia: dict | None, st: str, name: str) -> tuple[str, dict]:
    s = _eia_state(eia, st)
    if s is None:
        return f"EIA-860M figures for {name} not available", {}
    since = eia["capacity_860m"]["since_year"]
    planned = sum(v or 0 for v in s.get("planned_gas_nameplate_mw_by_year", {}).values())
    phrase = (f"{fmt(s['gas_nameplate_mw_added_since'])} of natural-gas generating capacity (nameplate) added in "
              f"{name} since {since}, plus {fmt(planned)} planned (EIA-860M)")
    return phrase, {"eia_gas_added_since_mw": s["gas_nameplate_mw_added_since"],
                    "eia_gas_added_by_year_mw": s.get("gas_nameplate_mw_added_by_year"),
                    "eia_planned_gas_mw": round(planned, 1), "eia_since_year": since}


def build(data: dict) -> list[dict]:
    ercot, pjm, iso, eia, neso = (data[k] for k in ("ercot", "pjm", "iso", "eia", "neso"))
    regions = []

    def add(region, sentence, figures, used):
        modes = sorted({data[u]["mode"] for u in used if data.get(u)})
        srcs = []
        for u in used:
            if data.get(u):
                srcs += [s.get("url") or s.get("url_or_file") or s.get("file") for s in data[u].get("sources", [])]
        regions.append({"region": region, "sentence": sentence, "figures": figures,
                        "inputs": used, "input_modes": modes, "sources": [s for s in srcs if s]})

    # --- Texas: ERCOT large-load queue vs EIA gas additions ---
    eia_p, eia_f = _eia_phrase(eia, "TX", "Texas")
    tot = (ercot or {}).get("latest_total_large_load_requests")
    dc = (ercot or {}).get("latest_data_centre_share_pct")
    if tot:
        approx = "approximately " if tot.get("approximate") else ""
        dc_txt = (f"; an ERCOT deck posted {dc['posted_date']} described "
                  f"{'~' if dc.get('approximate') else ''}{dc['value_pct']:g}% of the queue as data centres"
                  if dc else "")
        s = (f"Texas: {approx}{fmt(tot['value_mw'])} of large-load interconnection requests in ERCOT's queue "
             f"(ERCOT PDF posted {tot['posted_date']}){dc_txt}, vs {eia_p}.")
        f = {"ercot_large_load_requests_mw": tot["value_mw"], "ercot_source": tot["source_url"],
             "ercot_data_centre_share_pct": dc["value_pct"] if dc else None, **eia_f}
        snap = (ercot or {}).get("status_snapshot")
        if snap:
            f["ercot_mw_by_status"] = snap["mw_by_status"]
            f["ercot_status_snapshot_date"] = snap["posted_date"]
    else:
        s, f = f"Texas: ERCOT large-load figures not available; {eia_p}.", eia_f
    add("Texas", s, f, ["ercot", "eia"])

    # --- PJM states: gas generation requests in queue vs EIA additions ---
    for st, name in [("VA", "Virginia"), ("OH", "Ohio"), ("PA", "Pennsylvania")]:
        eia_p, eia_f = _eia_phrase(eia, st, name)
        if pjm:
            gas = _active_gas(pjm.get("active_mw_by_state_and_fuel_group"), st, "mw_energy")
            s = (f"{name}: {fmt(gas)} of natural-gas generation requests are active in PJM's interconnection "
                 f"queue in {name} (MW Energy), vs {eia_p}.")
            f = {"pjm_active_gas_mw_energy": round(gas, 1), **eia_f}
        else:
            s, f = f"{name}: PJM queue figures not available; {eia_p}.", eia_f
        add(name, s, f, ["pjm", "eia"])

    # --- MISO / SPP states ---
    by_iso = (iso or {}).get("by_iso", {})
    for st, name, isos in [("WI", "Wisconsin", ["MISO"]), ("LA", "Louisiana", ["MISO", "SPP"])]:
        eia_p, eia_f = _eia_phrase(eia, st, name)
        parts, f = [], dict(eia_f)
        for i in isos:
            if i in by_iso:
                gas = _active_gas(by_iso[i].get("active_mw_by_state_and_fuel_group"), st, "mw")
                parts.append(f"{fmt(gas)} in {i}'s")
                f[f"{i.lower()}_active_gas_mw"] = round(gas, 1)
                if i == "MISO":
                    f["miso_active_mw_without_state"] = by_iso[i].get("active_mw_without_state")
        if parts:
            nostate = f.get("miso_active_mw_without_state") or 0
            caveat = (f" (MISO also lists {fmt(nostate)} of active requests with no state)" if nostate > 0 else "")
            s = (f"{name}: active natural-gas generation requests total {' and '.join(parts)} interconnection "
                 f"queue{'s' if len(parts) > 1 else ''}{caveat}, vs {eia_p}.")
        else:
            s = f"{name}: ISO queue figures not available; {eia_p}."
        add(name, s, f, ["iso", "eia"])

    # --- States with no ISO queue in this ledger ---
    for st, name in [("GA", "Georgia"), ("AZ", "Arizona")]:
        eia_p, eia_f = _eia_phrase(eia, st, name)
        s = (f"{name}: {eia_p}; no public interconnection-queue or large-load file for {name} is scraped by "
             f"this ledger yet.")
        add(name, s, eia_f, ["eia"])

    # --- New York: NYISO is the one queue that lists load facilities ---
    ny = by_iso.get("NYISO")
    if ny:
        gas = _active_gas(ny.get("active_mw_by_state_and_fuel_group"), "NY", "mw")
        load = ny.get("load_requests", {})
        s = (f"New York: {fmt(load.get('mw_active'))} of load interconnection requests ({load.get('projects', 0)} "
             f"load projects, all statuses) and {fmt(gas)} of natural-gas generation requests are active in "
             f"NYISO's queue.")
        add("New York", s, {"nyiso_active_load_mw": load.get("mw_active"), "nyiso_load_projects": load.get("projects"),
                            "nyiso_active_gas_mw": round(gas, 1)}, ["iso"])

    # --- Great Britain: NESO EA register ---
    ea = (neso or {}).get("ea_register")
    if ea:
        mw_txt = (f" ({fmt(ea['data_centre_named_mw_total'])} of {fmt(ea['demand_mw_total'])}, MW column "
                  f"'{ea['mw_column_used']}' not verified)" if ea.get("mw_column_used") else " (no MW column identified)")
        s = (f"Great Britain: {ea['data_centre_named_projects']} of {ea['demand_projects']} transmission-connected "
             f"demand projects in NESO's Existing Agreement Register are named as data centres{mw_txt}; the register "
             f"lists only consenting Gate 2 applicants, so this is a lower bound.")
        add("Great Britain", s, {k: ea.get(k) for k in ("demand_projects", "data_centre_named_projects",
                                                        "demand_mw_total", "data_centre_named_mw_total",
                                                        "mw_column_used")}, ["neso"])
    return regions


def run_fixture_inputs(dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for script in SCRIPTS:
        log(f"  running {script} --fixture")
        r = subprocess.run([sys.executable, str(HERE / script), "--fixture", "--out", str(dest)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            log(r.stderr)
            raise SystemExit(f"{script} --fixture failed (exit {r.returncode})")


def main() -> None:
    p = base_parser(__doc__.split("\n\n")[0])
    p.add_argument("--in", dest="inp", type=Path, help="directory holding the scrapers' summaries (default: --out)")
    args = p.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=True)
    src = args.inp or out
    if args.fixture:
        src = out / "fixture_inputs"
        run_fixture_inputs(src)

    data = load_inputs(src)
    present = [k for k, v in data.items() if v]
    modes = {data[k]["mode"] for k in present}
    data_mode = "fixture" if modes == {"fixture"} else ("live" if modes == {"live"} else ("mixed" if modes else "none"))
    regions = build(data)
    for r in regions:
        r["data_mode"] = "fixture" if "fixture" in r["input_modes"] else ("live" if r["input_modes"] else "none")
        if r["data_mode"] == "fixture":
            r["sentence"] = FIXTURE_LABEL + r["sentence"]

    result = {
        "data_mode": data_mode,
        "label": (
            "FIXTURE-BASED: built from the small sample files in fixtures/ (several of them synthetic). "
            "These sentences prove the pipeline runs; their numbers are not real totals."
            if data_mode == "fixture" else
            "MIXED: some inputs are fixture-based; sentences marked [FIXTURE DATA - NOT REAL] must not be quoted."
            if data_mode == "mixed" else
            "Built from live downloads; see each region's sources and each input summary's retrieved_at."
        ),
        "inputs": {k: {"file": INPUTS[k], "present": bool(data[k]),
                       "mode": data[k]["mode"] if data[k] else None,
                       "retrieved_at": data[k].get("retrieved_at") if data[k] else None} for k in INPUTS},
        "method_note": ("Sentences juxtapose figures from different public files without implying causation. "
                        "Queue MW is requested, not built; EIA-860M MW is nameplate of generators in operation."),
        "regions": regions,
    }
    write_json(result, out / "cross_checks.json")
    log(f"Wrote {out/'cross_checks.json'} (data_mode={data_mode}, {len(regions)} regions)")
    for r in regions:
        log("  " + r["sentence"])


if __name__ == "__main__":
    run_main(main)
