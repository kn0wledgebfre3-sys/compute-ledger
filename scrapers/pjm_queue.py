#!/usr/bin/env python3
"""PJM interconnection queue -> normalised CSV + summary (MW by fuel and status).

SOURCE (inspected 2026-10-20)
-----------------------------
* The registry pointer https://www.pjm.com/planning/service-requests/serial-service-request-status
  now says Transition Cycle 2 data there "is no longer current" and links the Cycle page:
  https://www.pjm.com/planning/m/cycle-service-request-status
  That page lists 1,792 projects with "Full Export" / "Filtered Export" buttons (XLS or XML).
  The buttons are javascript:void(0). The XLS they produce is served by:
      POST https://services.pjm.com/PJMPlanningApi/api/Queue/ExportToXls
      header  api-subscription-key: <public key embedded in pjm.com's queue page JavaScript>
  NOT verified from the build environment (pjm.com is blocked here). Endpoint, headers and key are
  taken from gridstatus (gridstatus/pjm.py, commit 8a4d099, 2026-10-16), which calls this
  export in production. If PJM rotates the key, the request fails with a clear 401/403
  message. Then click "Full Export -> XLS" on the Cycle page and pass the file with --xlsx.

COLUMNS
-------
Seen on the Cycle page table (the fetcher, 2026-10-20):
  Project ID | Name | State | Status | TO | MFO | MW Energy | MW Capacity | MW In Service | Fuel
In the XLS export, per gridstatus' parser (not seen directly):
  Project ID, Name, Commercial Name, County, State, Transmission Owner, Submitted Date,
  Withdrawal Date, Withdrawn Remarks, Status, Projected In Service Date, Actual In Service Date,
  Fuel, MW Capacity, MW Energy, MFO, MW In Service, + study/agreement status columns.
Required by this parser: Project ID, State, Status, Fuel, MW Energy. Optional (used when
present): Name, County, Transmission Owner|TO, MFO, MW Capacity, MW In Service, Submitted Date.
Status values seen: Withdrawn, EP, UC, UC-ISP, Pending Termination; the page's filter list
also offers Cancelled, IS, Pending. Fuel values seen: Natural Gas, Solar, Wind, Storage,
Offshore Wind, Not Specified (a multi-fuel project shows two icons on the page).

MW MEASURE
----------
``mw`` = MW Energy (the incremental energy injection requested). MFO (maximum facility
output) includes existing capacity at uprate sites. Example from the page: AE1-070 Elwood,
MFO 1,610 / MW Energy 0 / MW Capacity 135. The summary reports MW Energy, MFO and MW
Capacity sums side by side.

STATUS GROUPS (auditable; the raw status is kept in every row)
  completed: IS / In Service / Partially in Service
  withdrawn: Withdrawn, Cancelled, Retracted, Deactivated, Annulled, Terminated
  active:    everything else (EP, UC, UC-ISP, Active, Pending, Pending Termination, ...)

LARGE-LOAD FORECAST (separate source, optional --with-load-adjustments)
-----------------------------------------------------------------------
PJM publishes load-forecast large-load adjustments as XLSX on
https://www.pjm.com/planning/resource-adequacy-planning/load-forecast-dev-process.aspx, e.g.
  https://www.pjm.com/-/media/DotCom/planning/res-adeq/load-forecast/total-load-adjustments-breakdown.xlsx
  (dated 2026-01-14 on that page)
The file's columns could NOT be inspected (binary; host blocked). With the flag the script
saves every sheet as raw CSV, uninterpreted, and records sheet names and shapes. Nothing
from it is summed until someone has looked at the columns.

OUTPUTS
-------
  pjm_queue.csv            one row per queue project (normalised columns + raw values)
  pjm_queue_summary.json   MW by fuel_group x status_group, by raw fuel x raw status,
                           active MW by state x fuel_group, data-centre-named projects
  pjm_load_adjustments_raw__<sheet>.csv  (only with --with-load-adjustments)

CAVEATS
-------
* Queue MW is requested capacity, not built capacity. Most queued projects historically withdraw.
* The PJM queue covers generation/transmission requests. Data-centre LOADS do not appear
  in it. ``is_data_centre_name`` only flags projects whose name says so, for co-located supply.

USAGE
-----
  python pjm_queue.py --out out/
  python pjm_queue.py --xlsx ~/Downloads/PlanningQueues.xlsx --out out/
  python pjm_queue.py --fixture --out out/fixture_run
"""

from __future__ import annotations

import io
import os
import re
from pathlib import Path

import pandas as pd

from _common import (
    FIXTURES,
    SchemaChangedError,
    base_parser,
    fetch,
    find_header_row,
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

LANDING = "https://www.pjm.com/planning/m/cycle-service-request-status"
EXPORT_URL = "https://services.pjm.com/PJMPlanningApi/api/Queue/ExportToXls"
# Public key that pjm.com's own queue page sends (recorded by gridstatus, pjm.py @ 8a4d099).
DEFAULT_PUBLIC_KEY = "E29477D0-70E0-4825-89B0-43F460BF9AB4"
LOAD_ADJ_URL = (
    "https://www.pjm.com/-/media/DotCom/planning/res-adeq/load-forecast/total-load-adjustments-breakdown.xlsx"
)
LOAD_ADJ_LANDING = "https://www.pjm.com/planning/resource-adequacy-planning/load-forecast-dev-process.aspx"
FIXTURE_XLSX = FIXTURES / "pjm" / "pjm_queue_export_sample.xlsx"

REQUIRED = ["Project ID", "State", "Status", "Fuel", "MW Energy"]


def status_group(raw) -> str:
    s = str(raw or "").strip().lower()
    if re.match(r"^(is|in service|partially in service)\b", s):
        return "completed"
    if re.match(r"^(withdrawn|cancel|retract|deactivat|annul|terminated)", s):
        return "withdrawn"
    return "active" if s else "unknown"


def read_export(content: bytes) -> pd.DataFrame:
    xls = pd.ExcelFile(io.BytesIO(content), engine="openpyxl")
    for sheet in xls.sheet_names:
        raw = pd.read_excel(xls, sheet_name=sheet, header=None, dtype=object)
        hdr = find_header_row(raw.values.tolist(), ["Project ID"])
        if hdr >= 0:
            df = raw.iloc[hdr + 1:].copy()
            df.columns = [str(c).strip() for c in raw.iloc[hdr].tolist()]
            df = df.dropna(how="all")
            return df
    raise SchemaChangedError(
        f"PJM export: no sheet has a 'Project ID' header (sheets: {xls.sheet_names}). The export layout "
        f"changed; open the file and update pjm_queue.py."
    )


def normalise(df: pd.DataFrame) -> pd.DataFrame:
    if "Transmission Owner" not in df.columns and "TO" in df.columns:
        df = df.rename(columns={"TO": "Transmission Owner"})
    require_columns(df.columns, REQUIRED, source="PJM queue export", hint=f"Landing page: {LANDING}")
    df = df[df["Project ID"].notna() & (df["Project ID"].astype(str).str.strip() != "")]

    def col(name):
        return df[name] if name in df.columns else pd.Series([None] * len(df), index=df.index)

    def num(name):
        return pd.to_numeric(col(name), errors="coerce")

    out = pd.DataFrame({
        "project_id": col("Project ID").astype(str).str.strip(),
        "project_name": col("Name"),
        "state": col("State").astype(str).str.strip().replace({"nan": None, "None": None}),
        "county": col("County"),
        "transmission_owner": col("Transmission Owner"),
        "status_raw": col("Status").astype(str).str.strip(),
        "fuel_raw": col("Fuel"),
        "mw_energy": num("MW Energy"),
        "mw_capacity": num("MW Capacity"),
        "mfo": num("MFO"),
        "mw_in_service": num("MW In Service"),
        "submitted_date": pd.to_datetime(col("Submitted Date"), errors="coerce").dt.date,
    })
    out["mw"] = out["mw_energy"]
    out["status_group"] = out["status_raw"].map(status_group)
    out["fuel_group"] = out["fuel_raw"].map(fuel_group)
    out["is_data_centre_name"] = out["project_name"].map(is_data_centre_name)
    return out.sort_values("project_id", kind="mergesort").reset_index(drop=True)


def summarise(q: pd.DataFrame) -> dict:
    def table(keys):
        g = q.groupby(keys, dropna=False).agg(
            projects=("project_id", "count"),
            mw_energy=("mw_energy", "sum"),
            mfo=("mfo", "sum"),
            mw_capacity=("mw_capacity", "sum"),
        ).reset_index()
        recs = []
        for r in g.to_dict("records"):
            recs.append({**{k: r[k] for k in keys}, "projects": int(r["projects"]),
                         "mw_energy": round_mw(r["mw_energy"]), "mfo": round_mw(r["mfo"]),
                         "mw_capacity": round_mw(r["mw_capacity"])})
        return recs

    active = q[q.status_group == "active"]
    return {
        "projects": int(len(q)),
        "mw_measure": "MW Energy (incremental energy requested); MFO and MW Capacity shown alongside",
        "status_group_map": {s: status_group(s) for s in sorted(q.status_raw.dropna().unique())},
        "mw_by_fuel_group_and_status_group": table(["fuel_group", "status_group"]),
        "mw_by_fuel_raw_and_status_raw": table(["fuel_raw", "status_raw"]),
        "active_mw_by_state_and_fuel_group": summarise_active(active),
        "data_centre_named_projects": q[q.is_data_centre_name][["project_id", "project_name", "status_raw", "mw"]]
        .to_dict("records"),
    }


def summarise_active(active: pd.DataFrame) -> list[dict]:
    g = active.groupby(["state", "fuel_group"], dropna=False).agg(
        projects=("project_id", "count"), mw_energy=("mw_energy", "sum")).reset_index()
    return [{"state": r["state"], "fuel_group": r["fuel_group"], "projects": int(r["projects"]),
             "mw_energy": round_mw(r["mw_energy"])} for r in g.to_dict("records")]


def load_adjustments(content: bytes, out: Path) -> dict:
    xls = pd.ExcelFile(io.BytesIO(content), engine="openpyxl")
    sheets = []
    for sheet in xls.sheet_names:
        raw = pd.read_excel(xls, sheet_name=sheet, header=None, dtype=object)
        safe = re.sub(r"[^A-Za-z0-9]+", "_", sheet).strip("_") or "sheet"
        path = out / f"pjm_load_adjustments_raw__{safe}.csv"
        write_csv(raw, path)
        sheets.append({"sheet": sheet, "rows": int(raw.shape[0]), "cols": int(raw.shape[1]), "file": path.name})
    return {
        "source_url": LOAD_ADJ_URL,
        "interpreted": False,
        "note": "Columns not inspected before this run; saved raw. Inspect and extend the parser before using.",
        "sheets": sheets,
    }


def main() -> None:
    p = base_parser(__doc__.split("\n\n")[0])
    p.add_argument("--xlsx", type=Path, help="use a manually exported queue XLS(X) instead of the API")
    p.add_argument("--with-load-adjustments", action="store_true",
                   help="also download PJM's total-load-adjustments-breakdown.xlsx (saved raw)")
    args = p.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=True)

    if args.fixture:
        content, src = FIXTURE_XLSX.read_bytes(), {"url": LANDING, "file": str(FIXTURE_XLSX.relative_to(FIXTURES.parent))}
    elif args.xlsx:
        content, src = args.xlsx.read_bytes(), {"url": LANDING, "file": str(args.xlsx)}
    else:
        key = os.environ.get("PJM_QUEUE_SUBSCRIPTION_KEY", DEFAULT_PUBLIC_KEY)
        log(f"POST {EXPORT_URL}")
        f = fetch(EXPORT_URL, method="POST", expect="xlsx", landing_page=LANDING, headers={
            "api-subscription-key": key, "Origin": "https://www.pjm.com", "Referer": "https://www.pjm.com/"})
        content, src = f.content, {"url": EXPORT_URL, "landing_page": LANDING}

    # All downloads happen before anything is written, so a failure leaves earlier outputs intact.
    adj_bytes = None
    if args.with_load_adjustments and not args.fixture:
        log(f"GET {LOAD_ADJ_URL}")
        adj_bytes = fetch(LOAD_ADJ_URL, expect="xlsx", landing_page=LOAD_ADJ_LANDING).content

    q = normalise(read_export(content))
    write_csv(q, out / "pjm_queue.csv")
    summary = {**run_meta(args.fixture, [src]), **summarise(q)}
    if adj_bytes is not None:
        summary["large_load_forecast"] = load_adjustments(adj_bytes, out)
    else:
        summary["large_load_forecast"] = {
            "source_url": LOAD_ADJ_URL,
            "interpreted": False,
            "note": "Not fetched (run live with --with-load-adjustments). No fixture exists: columns never seen.",
        }
    write_json(summary, out / "pjm_queue_summary.json")
    log(f"Wrote {out/'pjm_queue.csv'} ({len(q)} projects) and {out/'pjm_queue_summary.json'}")


if __name__ == "__main__":
    run_main(main)
