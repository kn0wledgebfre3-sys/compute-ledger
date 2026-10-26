#!/usr/bin/env python3
"""MISO + SPP + NYISO interconnection queues -> one normalised CSV + summary.

Normalised columns: iso, project_id, project_name, state, county, zone, fuel_raw, fuel_group,
mw, status_raw, status_detail, status_group, queue_date, is_load, is_data_centre_name.

SOURCES AND COLUMNS (inspected 2026-10-20)
------------------------------------------
MISO  GET https://www.misoenergy.org/api/giqueue/getprojects   (JSON array of projects)
      Landing page: https://www.misoenergy.org/planning/resource-utilization/GI_Queue/
      NOT seen directly: the fetcher got a client error from this endpoint. Raw keys are taken
      from gridstatus/miso.py (commit 8a4d099, 2026-10-16), which parses the live endpoint:
        projectNumber, county, state, transmissionOwner, poiName, queueDate, withdrawnDate,
        applicationStatus, summerNetMW, winterNetMW, negInService, fuelType, facilityType,
        postGIAStatus, doneDate, inService, giaToExec, studyCycle, studyGroup, studyPhase,
        svcType, dp1ErisMw, dp1NrisMw, dp2ErisMw, dp2NrisMw, sisPhase1
      Values seen in gridstatus' rendered docs: applicationStatus 'Done', 'Withdrawn';
      fuelType 'Gas', 'Hydro', 'Hybrid', blank; studyGroup 'South', 'East (ATC)'.
      Note: recent DPP-2025/2026 and ERAS entries show blank county/state/fuelType, so MW
      for those rows cannot be placed in a state from this file.
      mw = max(summerNetMW, winterNetMW) (as gridstatus does). zone = studyGroup.

SPP   GET https://opsportal.spp.org/Studies/GenerateSummaryCSV   (CSV)
      SEEN via the fetcher: line 1 is `"Last Updated On",10/19/2026,`; line 2 is a 27-column
      header: Generation Interconnection Number, IFS Queue Number, Current Cluster,
      Cluster Group, Nearest Town or County (gridstatus shows a leading space), State,
      TO at POI, In-Service Date, Commercial Operation Date, Cessation Date, Original
      Generator Commercial Op Date, Capacity, MAX Summer MW, MAX Winter MW, Service Type,
      Requested Maximum Injection Capability (MW), Requested Network Resource
      Deliverability (MW), Nameplate Capacity, Generation Type, Fuel Type, Substation or
      Line, Request Received, Date Withdrawn, Status, JTIQ Participant, JTIQ Commitment,
      Cause of Delay.
      Status values: IA FULLY EXECUTED/COMMERCIAL OPERATION, IA FULLY EXECUTED/ON SCHEDULE,
      IA FULLY EXECUTED/ON SUSPENSION, IA PENDING, FACILITY STUDY STAGE, SPECIAL STUDY,
      DISIS STAGE, WITHDRAWN. Fuel Type values: Wind, Photovoltaic, Solar/Storage, Battery,
      Gas, Solar/Wind/Storage, Wind/Storage, CTG, blank. Dates are M/D/YYYY.
      mw = Capacity. zone = Cluster Group. fuel_raw = Fuel Type, or Generation Type when blank.

NYISO GET https://www.nyiso.com/documents/20142/1407078/NYISO-Interconnection-Queue.xlsx
      Landing page: https://www.nyiso.com/interconnections (the fetcher could not see the link)
      NOT seen directly (binary). Sheet and column names from gridstatus/nyiso.py @ 8a4d099:
        sheets 'Interconnection Queue', ' Cluster Projects' (leading space), 'Withdrawn',
        'Cluster Projects-Withdrawn', 'In Service' (two-row merged header)
        columns Queue Pos., Project Name, Date of IR, SP (MW), WP (MW), Type/ Fuel, County,
        State, Z (zone), Points of Interconnection, Utility, S (milestone step),
        Last Updated Date / Last Update, Availability of Studies, Proposed COD, ...
      Type/ Fuel is a code (S, W, ES, CT, CC, CC-NG, L = Load, ...), decoded with gridstatus' map.
      Load requests (code L) are kept and flagged is_load=True: NYISO's queue is the only
      one of the three that includes load facilities.
      mw = max(SP (MW), WP (MW)). status_raw = sheet name; status_detail = S.

STATUS GROUPS (raw status kept in every row; summary prints the mapping actually applied)
  completed: MISO Done | SPP IA FULLY EXECUTED/COMMERCIAL OPERATION | NYISO 'In Service' sheet
  withdrawn: anything containing 'withdraw' | NYISO withdrawn sheets
  active:    everything else, including SPP 'IA FULLY EXECUTED/ON SCHEDULE' (signed but not built)

CAVEATS
-------
* Queue MW is requested capacity. Most of it historically never gets built.
* MISO's live JSON was never seen from the build environment. On a live run the script checks for
  the required keys and stops with the list of keys it did find.
* NYISO sheet column ORDER for active/withdrawn sheets was not verified. Columns are matched by name.

USAGE
-----
  python miso_spp_nyiso_queues.py --out out/
  python miso_spp_nyiso_queues.py --only spp,nyiso --out out/
  python miso_spp_nyiso_queues.py --fixture --out out/fixture_run
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
    fuel_group,
    is_data_centre_name,
    log,
    require_columns,
    round_mw,
    run_main,
    run_meta,
    write_csv,
    write_json,
)

SOURCES = {
    "MISO": {
        "url": "https://www.misoenergy.org/api/giqueue/getprojects",
        "landing": "https://www.misoenergy.org/planning/resource-utilization/GI_Queue/",
        "expect": "json",
        "fixture": FIXTURES / "miso" / "miso_getprojects_sample.json",
    },
    "SPP": {
        "url": "https://opsportal.spp.org/Studies/GenerateSummaryCSV",
        "landing": "https://www.spp.org/engineering/generator-interconnection/",
        "expect": "csv",
        "fixture": FIXTURES / "spp" / "spp_GenerateSummaryCSV_sample.csv",
    },
    "NYISO": {
        "url": "https://www.nyiso.com/documents/20142/1407078/NYISO-Interconnection-Queue.xlsx",
        "landing": "https://www.nyiso.com/interconnections",
        "expect": "xlsx",
        "fixture": FIXTURES / "nyiso" / "NYISO-Interconnection-Queue_sample.xlsx",
    },
}

NORMAL_COLS = [
    "iso", "project_id", "project_name", "state", "county", "zone", "fuel_raw", "fuel_group", "mw",
    "status_raw", "status_detail", "status_group", "queue_date", "is_load", "is_data_centre_name",
]

# NYISO Type/ Fuel codes -> labels. Copied from gridstatus/nyiso.py (BSD-3-Clause,
# Copyright 2022 James Max Kanter); stray '=' removed from "Solid Waste". Unmapped codes are kept as-is.
NYISO_FUEL_CODES = {
    "S": "Solar", "ES": "Energy Storage", "W": "Wind", "AC": "AC Transmission", "DC": "DC Transmission",
    "CT": "Combustion Turbine", "CC": "Combined Cycle", "M": "Methane", "H": "Hydro", "L": "Load",
    "ST": "Steam Turbine", "CC-NG": "Natural Gas", "FC": "Fuel Cell", "PS": "Pumped Storage",
    "NU": "Nuclear", "D": "Dual Fuel", "NG": "Natural Gas", "Wo": "Wood", "F": "Flywheel",
    "CC-D": "Combined Cycle - Dual Fuel", "SW": "Solid Waste", "CT-NG": "Combustion Turbine - Natural Gas",
    "DC/AC": "DC/AC Transmission", "CT-D": "Combustion Turbine - Dual Fuel",
    "CS-NG": "Steam Turbine & Combustion Turbine - Natural Gas", "ST-NG": "Steam Turbine - Natural Gas",
}


def _blank_to_none(s: pd.Series) -> pd.Series:
    return s.map(lambda v: None if v is None or (isinstance(v, float) and pd.isna(v)) or str(v).strip() in ("", "nan", "NaT") else str(v).strip())


def _date(s: pd.Series, fmt: str | None = None) -> pd.Series:
    d = pd.to_datetime(s, errors="coerce", format=fmt, utc=True)
    return d.dt.strftime("%Y-%m-%d").where(d.notna(), None)


def generic_status_group(raw) -> str:
    s = "" if raw is None or (not isinstance(raw, str) and pd.isna(raw)) else str(raw).strip().lower()
    if not s:
        return "unknown"
    if "withdraw" in s:
        return "withdrawn"
    if s in ("done", "in service", "completed") or "commercial operation" in s:
        return "completed"
    return "active"


# ---------------------------------------------------------------------------------------
# MISO
# ---------------------------------------------------------------------------------------

MISO_REQUIRED = ["projectNumber", "state", "county", "fuelType", "summerNetMW", "winterNetMW",
                 "applicationStatus", "queueDate"]


def parse_miso(content: bytes) -> pd.DataFrame:
    data = json.loads(content.decode("utf-8-sig"))
    if isinstance(data, dict):  # tolerate a wrapper object, but say so if keys are unexpected
        for k in ("projects", "data", "items"):
            if isinstance(data.get(k), list):
                data = data[k]
                break
    if not isinstance(data, list) or not data:
        raise SchemaChangedError(f"MISO: expected a non-empty JSON array, got {type(data).__name__}")
    raw = pd.DataFrame(data)
    require_columns(raw.columns, MISO_REQUIRED, source="MISO getprojects JSON",
                    hint=f"Landing page: {SOURCES['MISO']['landing']}")
    mw = pd.concat([pd.to_numeric(raw["summerNetMW"], errors="coerce"),
                    pd.to_numeric(raw["winterNetMW"], errors="coerce")], axis=1).max(axis=1)
    status = _blank_to_none(raw["applicationStatus"])
    out = pd.DataFrame({
        "iso": "MISO",
        "project_id": raw["projectNumber"].astype(str),
        "project_name": None,  # MISO publishes no project names
        "state": _blank_to_none(raw["state"]),
        "county": _blank_to_none(raw["county"]),
        "zone": _blank_to_none(raw["studyGroup"]) if "studyGroup" in raw else None,
        "fuel_raw": _blank_to_none(raw["fuelType"]),
        "mw": mw,
        "status_raw": status,
        "status_detail": _blank_to_none(raw["studyPhase"]) if "studyPhase" in raw else None,
        "queue_date": _date(raw["queueDate"]),
        "is_load": False,
    })
    out["fuel_group"] = out["fuel_raw"].map(fuel_group)
    out["status_group"] = out["status_raw"].map(generic_status_group)
    out["is_data_centre_name"] = False
    return out


# ---------------------------------------------------------------------------------------
# SPP
# ---------------------------------------------------------------------------------------

SPP_REQUIRED = ["Generation Interconnection Number", "Nearest Town or County", "State", "Capacity",
                "Generation Type", "Fuel Type", "Request Received", "Status"]


def parse_spp(content: bytes) -> pd.DataFrame:
    text = content.decode("utf-8-sig", errors="replace")
    first = text.splitlines()[0] if text else ""
    skip = 1 if first.lower().lstrip('"').startswith("last updated") else 0
    raw = pd.read_csv(io.StringIO(text), skiprows=skip, dtype=str, keep_default_na=False)
    raw.columns = [c.strip() for c in raw.columns]
    require_columns(raw.columns, SPP_REQUIRED, source="SPP GenerateSummaryCSV",
                    hint=f"Landing page: {SOURCES['SPP']['landing']}")
    raw = raw[raw["Generation Interconnection Number"].str.strip() != ""]
    fuel = _blank_to_none(raw["Fuel Type"])
    fuel = fuel.where(fuel.notna(), _blank_to_none(raw["Generation Type"]))
    out = pd.DataFrame({
        "iso": "SPP",
        "project_id": raw["Generation Interconnection Number"].str.strip(),
        "project_name": None,
        "state": _blank_to_none(raw["State"]),
        "county": _blank_to_none(raw["Nearest Town or County"]).map(
            lambda v: v.rstrip(",").strip() if isinstance(v, str) else v),
        "zone": _blank_to_none(raw["Cluster Group"]) if "Cluster Group" in raw else None,
        "fuel_raw": fuel,
        "mw": pd.to_numeric(raw["Capacity"].str.replace(",", ""), errors="coerce"),
        "status_raw": _blank_to_none(raw["Status"]),
        "status_detail": _blank_to_none(raw["Current Cluster"]) if "Current Cluster" in raw else None,
        "queue_date": _date(raw["Request Received"], fmt="%m/%d/%Y"),
        "is_load": False,
    })
    out["fuel_group"] = out["fuel_raw"].map(fuel_group)
    out["status_group"] = out["status_raw"].map(generic_status_group)
    out["is_data_centre_name"] = False
    meta = {"last_updated_line": first.strip()}
    out.attrs["meta"] = meta
    return out


# ---------------------------------------------------------------------------------------
# NYISO
# ---------------------------------------------------------------------------------------

NYISO_ALIASES = {
    "Queue Pos.": "Queue Pos.", "Queue Pos": "Queue Pos.",
    "Queue Owner/Developer": "Developer", "Owner/Developer": "Developer",
    "Queue Project Name": "Project Name", "Location County": "County", "Location State": "State",
    "Interconnection Point": "Interconnection Point", "Points of Interconnection": "Interconnection Point",
    "Interconnection Utility": "Utility", "Interconnection S": "S", "Last Update": "Last Updated Date",
    "Type/Fuel": "Type/ Fuel", "Date of IR": "Date of IR",
}
NYISO_REQUIRED = ["Queue Pos.", "Project Name", "Type/ Fuel", "SP (MW)", "County", "State"]
NYISO_SHEETS = {  # normalised sheet name -> status_raw
    "interconnection queue": "Active",
    "cluster projects": "Active (Cluster)",
    "withdrawn": "Withdrawn",
    "cluster projects-withdrawn": "Withdrawn (Cluster)",
    "in service": "In Service",
}


def _canon(c) -> str:
    c = re.sub(r"\s+", " ", str(c)).strip()
    return NYISO_ALIASES.get(c, c)


def _nyiso_frame(raw: pd.DataFrame) -> pd.DataFrame | None:
    """Locate a one- or two-row header on a NYISO sheet and return data with canonical columns."""
    rows = raw.values.tolist()
    for i, row in enumerate(rows[:6]):
        cells = [str(v).strip() if v is not None and not (isinstance(v, float) and pd.isna(v)) else "" for v in row]
        if "Queue Pos." in cells or "Queue Pos" in cells:
            df = raw.iloc[i + 1:].copy()
            df.columns = [_canon(c) if c else f"col{j}" for j, c in enumerate(cells)]
            return df
        if "Queue" in cells and i + 1 < len(rows):  # two-row merged header (In Service sheet)
            sub = [str(v) if v is not None and not (isinstance(v, float) and pd.isna(v)) else "" for v in rows[i + 1]]
            top, names, last = cells, [], ""
            for j, (t, s) in enumerate(zip(top, sub)):
                if t:
                    last = t
                # carry a merged top-row label across columns that only have a sub-label
                head = t if t else (last if s.strip() else "")
                name = f"{head} {s.strip()}".strip() if s.strip() else head
                names.append(_canon(name) if name else f"col{j}")
            df = raw.iloc[i + 2:].copy()
            df.columns = names
            return df
    return None


def parse_nyiso(content: bytes) -> pd.DataFrame:
    xls = pd.ExcelFile(io.BytesIO(content), engine="openpyxl")
    frames, seen_sheets = [], []
    for sheet in xls.sheet_names:
        key = re.sub(r"\s+", " ", sheet).strip().lower()
        if key not in NYISO_SHEETS:
            continue
        seen_sheets.append(sheet)
        raw = pd.read_excel(xls, sheet_name=sheet, header=None, dtype=object)
        if raw.dropna(how="all").empty:
            continue
        df = _nyiso_frame(raw)
        if df is None:
            raise SchemaChangedError(f"NYISO sheet {sheet!r}: no 'Queue Pos.' header found in the first rows.")
        df = df[df["Queue Pos."].notna() & df["Project Name"].notna()] if "Project Name" in df else df.iloc[0:0]
        if df.empty:
            continue
        require_columns(df.columns, NYISO_REQUIRED, source=f"NYISO sheet {sheet!r}",
                        hint=f"Landing page: {SOURCES['NYISO']['landing']}")
        df["__status"] = NYISO_SHEETS[key]
        frames.append(df)
    if "interconnection queue" not in {re.sub(r"\s+", " ", s).strip().lower() for s in seen_sheets}:
        raise SchemaChangedError(f"NYISO workbook has no 'Interconnection Queue' sheet (sheets: {xls.sheet_names}).")
    raw = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=NYISO_REQUIRED + ["__status"])

    def col(name):
        return raw[name] if name in raw.columns else pd.Series([None] * len(raw), index=raw.index)

    code = _blank_to_none(col("Type/ Fuel"))
    decoded = code.map(lambda c: NYISO_FUEL_CODES.get(c, c) if c else None)
    sp = pd.to_numeric(col("SP (MW)"), errors="coerce")  # 'TBD' / blanks become NaN
    wp = pd.to_numeric(col("WP (MW)"), errors="coerce")
    out = pd.DataFrame({
        "iso": "NYISO",
        "project_id": col("Queue Pos.").map(lambda v: str(v).strip()),
        "project_name": _blank_to_none(col("Project Name")),
        "state": _blank_to_none(col("State")),
        "county": _blank_to_none(col("County")),
        "zone": _blank_to_none(col("Z")),
        "fuel_raw": decoded.where(decoded.isna(), decoded + " [" + code.fillna("") + "]"),
        "mw": pd.concat([sp, wp], axis=1).max(axis=1),
        "status_raw": raw["__status"],
        "status_detail": col("S").map(lambda v: None if v is None or (isinstance(v, float) and pd.isna(v)) else f"S={v}"),
        "queue_date": _date(col("Date of IR")),
        "is_load": code.eq("L"),
    })
    out["fuel_group"] = decoded.map(fuel_group)
    out["status_group"] = out["status_raw"].map(
        lambda s: "completed" if s == "In Service" else ("withdrawn" if s.startswith("Withdrawn") else "active"))
    out["is_data_centre_name"] = out["project_name"].map(is_data_centre_name)
    return out


PARSERS = {"MISO": parse_miso, "SPP": parse_spp, "NYISO": parse_nyiso}


# ---------------------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------------------

def summarise(q: pd.DataFrame) -> dict:
    res: dict = {}
    for iso, g in q.groupby("iso", sort=True):
        t = g.groupby(["fuel_group", "status_group"], dropna=False).agg(
            projects=("project_id", "count"), mw=("mw", "sum")).reset_index()
        active = g[g.status_group == "active"]
        st = active.groupby(["state", "fuel_group"], dropna=False).agg(
            projects=("project_id", "count"), mw=("mw", "sum")).reset_index()
        res[iso] = {
            "projects": int(len(g)),
            "status_group_map": {str(k): str(v) for k, v in sorted(
                g[["status_raw", "status_group"]].astype(object).fillna("(blank)")
                .drop_duplicates().values.tolist())},
            "mw_by_fuel_group_and_status_group": [
                {"fuel_group": r.fuel_group, "status_group": r.status_group, "projects": int(r.projects),
                 "mw": round_mw(r.mw)} for r in t.itertuples()],
            "active_mw_by_state_and_fuel_group": [
                {"state": None if pd.isna(r.state) else r.state, "fuel_group": r.fuel_group,
                 "projects": int(r.projects), "mw": round_mw(r.mw)} for r in st.itertuples()],
            "active_mw_without_state": round_mw(active[active.state.isna()].mw.sum()),
            "load_requests": {
                "projects": int(g.is_load.sum()),
                "mw_all_statuses": round_mw(g[g.is_load].mw.sum()),
                "mw_active": round_mw(active[active.is_load].mw.sum()),
            },
            "data_centre_named_projects": g[g.is_data_centre_name][
                ["project_id", "project_name", "status_raw", "mw"]].to_dict("records"),
        }
    return res


def main() -> None:
    p = base_parser(__doc__.split("\n\n")[0])
    p.add_argument("--only", default="MISO,SPP,NYISO", help="comma list of ISOs (default all three)")
    p.add_argument("--allow-partial", action="store_true",
                   help="if some ISOs fail, still write the others (summary lists the errors)")
    args = p.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=True)
    wanted = [s.strip().upper() for s in args.only.split(",") if s.strip()]

    frames, sources, errors, extra = [], [], {}, {}
    for iso in wanted:
        cfg = SOURCES[iso]
        try:
            if args.fixture:
                content = cfg["fixture"].read_bytes()
                sources.append({"iso": iso, "url": cfg["url"], "file": str(cfg["fixture"].relative_to(FIXTURES.parent))})
            else:
                log(f"GET {cfg['url']}")
                content = fetch(cfg["url"], expect=cfg["expect"], landing_page=cfg["landing"]).content
                sources.append({"iso": iso, "url": cfg["url"], "landing_page": cfg["landing"]})
            df = PARSERS[iso](content)
            if df.attrs.get("meta"):
                extra[iso] = df.attrs["meta"]
            log(f"  {iso}: {len(df)} projects")
            frames.append(df)
        except SourceError as exc:  # keep going so every failure is reported in one run
            log(f"  {iso} FAILED: {exc}")
            errors[iso] = f"{type(exc).__name__}: {exc}"

    # Never replace a previous good output with a partial one unless explicitly asked to.
    if errors and (not frames or not args.allow_partial):
        raise SourceError(
            f"{len(errors)} ISO(s) failed ({', '.join(errors)}); nothing written so earlier outputs stay intact. "
            "Re-run with --only for the ISOs that work, or --allow-partial to write what succeeded."
        )

    q = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=NORMAL_COLS)
    q = q.reindex(columns=NORMAL_COLS).sort_values(["iso", "project_id"], kind="mergesort")
    write_csv(q, out / "iso_queues_normalised.csv")
    summary = {**run_meta(args.fixture, sources), "errors": errors or None, "source_notes": extra or None,
               "by_iso": summarise(q)}
    write_json(summary, out / "iso_queues_summary.json")
    log(f"Wrote {out/'iso_queues_normalised.csv'} ({len(q)} rows) and {out/'iso_queues_summary.json'}")
    if errors:
        raise SourceError(f"{len(errors)} ISO(s) failed: {', '.join(errors)} (--allow-partial: others were written)")


if __name__ == "__main__":
    run_main(main)
