#!/usr/bin/env python3
"""EIA-860M plant capacity by fuel + EIA-923 monthly net generation by fuel, for the data-centre states.

States (default): VA, TX, GA, OH, AZ, PA, WI, LA. Change with --states.

PART A: capacity (Form EIA-860M monthly generator inventory, XLSX, no key needed)
--------------------------------------------------------------------------------------
Landing page (inspected 2026-10-20): https://www.eia.gov/electricity/data/eia860m/
  Latest file at inspection: August 2026, released 2026-09-24 (next release 2026-10-23):
    https://www.eia.gov/electricity/data/eia860m/xls/august_generator2026.xlsx
  Older months move to:  https://www.eia.gov/electricity/data/eia860m/archive/xls/<month>_generator<year>.xlsx
  The script tries the current month and goes back up to 7 months, on both paths.
Sheets used: Operating, Planned, Retired (each has a title row above the header and a note
row below the data).
Columns (names from gridstatus/eia.py + eia_constants.py, commit 8a4d099, 2026-10-16, which
parses these files monthly. The XLSX itself is binary and was not readable via WebFetch):
  Entity ID, Entity Name, Plant ID, Plant Name, Plant State, County, Balancing Authority Code,
  Sector, Generator ID, Unit Code, Nameplate Capacity (MW), Net Summer Capacity (MW),
  Net Winter Capacity (MW), Technology, Energy Source Code, Prime Mover Code,
  Operating Month, Operating Year, [Planned Retirement Month/Year], Status, ... Latitude, Longitude
  Planned sheet: Planned Operation Month, Planned Operation Year
  Retired sheet: Operating Month/Year, Retirement Month, Retirement Year
Why the XLSX and not the API route electricity/operating-generator-capacity: that route's
response field names for plant id and operating date could not be confirmed from the sandbox.
The XLSX column names are confirmed by a parser that runs against the live files.

PART B: monthly net generation by fuel (EIA API v2, free key in env EIA_API_KEY)
--------------------------------------------------------------------------------------
  GET https://api.eia.gov/v2/electricity/electric-power-operational-data/data/
      ?api_key=...&frequency=monthly&data[0]=generation&facets[location][]=TX&...
      &facets[sectorid][]=99&start=2022-01&offset=0&length=5000
  Register a key: https://www.eia.gov/opendata/register.php
Verified: facet ids location / sectorid / fueltypeid and data id 'generation' (from
third-party code that calls the live API, and a public query string using
location=US&fueltypeid=NG&sectorid=99&data=generation). The envelope (response.total,
response.data, 5,000-row page limit, offset/length) is from EIA's API documentation.
Response row keys are assumed to equal the facet/data ids (period, location, sectorid,
fueltypeid, generation, generation-units). EIA documents this convention, and gridstatus'
facility-fuel parser relies on it. The script first fetches the route metadata and stops
with a clear message if those facets or the data column are missing.
fueltypeid contains overlapping aggregates (e.g. ALL vs NG), so values are NEVER summed
across fuel types. The summary uses only ALL and NG.

OUTPUTS
-------
  eia860m_plant_capacity_by_fuel.csv     plant x energy source code: generators, nameplate/summer MW
  eia860m_gas_additions_by_state_year.csv NG generators with Operating Year >= --since (default 2022),
                                          from Operating + Retired sheets, by state/year/technology
  eia860m_planned_gas_by_state_year.csv   NG generators on the Planned sheet
  eia923_monthly_generation_by_fuel.csv   period x state x fueltypeid, thousand MWh (Part B)
  eia_summary.json

CAVEATS
-------
* "New gas capacity added" = nameplate MW of generators whose Energy Source Code is NG and
  whose Operating Year >= 2022, in the latest 860M inventory, including units that have
  since retired. Other gas codes (e.g. OG, BFG) are excluded. Capacity uprates of
  existing units are not additions in this table.
* 860M is preliminary monthly data, revised in the annual EIA-860.
* Electric-power-operational-data covers all sectors (sectorid 99) and has a lag of ~2-3 months.

USAGE
-----
  EIA_API_KEY=... python eia_860_923.py --out out/
  python eia_860_923.py --skip-generation --out out/          # capacity only, no key
  python eia_860_923.py --month 2026-08 --out out/
  python eia_860_923.py --fixture --out out/fixture_run       # SYNTHETIC fixtures, parser test
"""

from __future__ import annotations

import datetime as dt
import io
import json
import os
from pathlib import Path

import pandas as pd

from _common import (
    FIXTURES,
    MissingCredentialError,
    SchemaChangedError,
    SourceError,
    SourceMovedError,
    base_parser,
    fetch,
    find_header_row,
    log,
    require_columns,
    round_mw,
    run_main,
    run_meta,
    write_csv,
    write_json,
)

STATES = ["VA", "TX", "GA", "OH", "AZ", "PA", "WI", "LA"]
LANDING_860M = "https://www.eia.gov/electricity/data/eia860m/"
URL_860M = "https://www.eia.gov/electricity/data/eia860m/xls/{m}_generator{y}.xlsx"
URL_860M_ARCHIVE = "https://www.eia.gov/electricity/data/eia860m/archive/xls/{m}_generator{y}.xlsx"
API_ROUTE = "https://api.eia.gov/v2/electricity/electric-power-operational-data/"
API_DOCS = "https://www.eia.gov/opendata/documentation.php"

FIX_860M = FIXTURES / "eia" / "august_generator2026_SYNTHETIC.xlsx"
FIX_API_DATA = FIXTURES / "eia" / "eia_v2_electric_power_operational_data_SYNTHETIC.json"
FIX_API_META = FIXTURES / "eia" / "eia_v2_route_metadata_SYNTHETIC.json"

BASE_COLS = ["Plant ID", "Plant Name", "Plant State", "County", "Generator ID", "Nameplate Capacity (MW)",
             "Net Summer Capacity (MW)", "Technology", "Energy Source Code"]
SHEET_COLS = {
    "Operating": BASE_COLS + ["Operating Month", "Operating Year"],
    "Planned": BASE_COLS + ["Planned Operation Month", "Planned Operation Year"],
    "Retired": BASE_COLS + ["Operating Month", "Operating Year", "Retirement Year"],
}
GAS_CODES = {"NG"}


# ---------------------------------------------------------------------------------------
# Part A: EIA-860M
# ---------------------------------------------------------------------------------------

def _month_candidates(month: str | None, back: int = 7):
    if month:
        y, m = (int(x) for x in month.split("-"))
        return [(y, m)]
    today = dt.date.today()
    out, y, m = [], today.year, today.month
    for _ in range(back + 1):
        out.append((y, m))
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    return out


def download_860m(month: str | None) -> tuple[bytes, str]:
    tried = []
    for y, m in _month_candidates(month):
        name = dt.date(y, m, 1).strftime("%B").lower()
        for tmpl in (URL_860M, URL_860M_ARCHIVE):
            url = tmpl.format(m=name, y=y)
            try:
                f = fetch(url, expect="xlsx", landing_page=LANDING_860M)
                log(f"  using {url}")
                return f.content, url
            except SourceMovedError:
                tried.append(url)
    raise SourceMovedError(
        "No EIA-860M generator file found at any of: " + ", ".join(tried)
        + f". EIA may have changed its file naming; check {LANDING_860M} and pass --month or --xlsx."
    )


def read_860m_sheet(xls: pd.ExcelFile, sheet: str) -> pd.DataFrame:
    if sheet not in xls.sheet_names:
        raise SchemaChangedError(f"EIA-860M: sheet {sheet!r} missing (sheets: {xls.sheet_names}).")
    raw = pd.read_excel(xls, sheet_name=sheet, header=None, dtype=object)
    hdr = find_header_row(raw.values.tolist(), ["Plant ID", "Plant State"])
    if hdr < 0:
        raise SchemaChangedError(f"EIA-860M sheet {sheet!r}: no header row containing 'Plant ID' and 'Plant State'.")
    df = raw.iloc[hdr + 1:].copy()
    df.columns = [str(c).strip() for c in raw.iloc[hdr].tolist()]
    require_columns(df.columns, SHEET_COLS[sheet], source=f"EIA-860M sheet {sheet!r}",
                    hint=f"Landing page: {LANDING_860M}")
    # Footer notes have no numeric Plant ID; drop them (gridstatus does the same via dropna/skipfooter).
    df["Plant ID"] = pd.to_numeric(df["Plant ID"], errors="coerce")
    df = df[df["Plant ID"].notna()].copy()
    df["Plant ID"] = df["Plant ID"].astype("int64")
    for c in ("Nameplate Capacity (MW)", "Net Summer Capacity (MW)"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    for c in ("Operating Year", "Planned Operation Year", "Retirement Year", "Operating Month",
              "Planned Operation Month"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")
    for c in ("Plant State", "Energy Source Code", "Technology", "Plant Name", "County", "Generator ID"):
        df[c] = df[c].map(lambda v: None if v is None or (isinstance(v, float) and pd.isna(v)) else str(v).strip())
    return df


def part_a(content: bytes, states: list[str], since: int, out: Path) -> dict:
    xls = pd.ExcelFile(io.BytesIO(content), engine="openpyxl")
    op = read_860m_sheet(xls, "Operating")
    pl = read_860m_sheet(xls, "Planned")
    rt = read_860m_sheet(xls, "Retired")
    op_s = op[op["Plant State"].isin(states)]

    cap = (op_s.groupby(["Plant State", "Plant ID", "Plant Name", "County", "Energy Source Code"], dropna=False)
           .agg(generators=("Generator ID", "count"),
                nameplate_mw=("Nameplate Capacity (MW)", "sum"),
                net_summer_mw=("Net Summer Capacity (MW)", "sum"),
                technologies=("Technology", lambda s: "; ".join(sorted({t for t in s if t}))))
           .reset_index()
           .sort_values(["Plant State", "Plant ID", "Energy Source Code"], kind="mergesort"))
    write_csv(cap, out / "eia860m_plant_capacity_by_fuel.csv")

    def gas_since(df: pd.DataFrame, still_operating: bool) -> pd.DataFrame:
        g = df[df["Plant State"].isin(states) & df["Energy Source Code"].isin(GAS_CODES)
               & (df["Operating Year"] >= since)].copy()
        g["still_operating"] = still_operating
        return g

    adds = pd.concat([gas_since(op, True), gas_since(rt, False)], ignore_index=True)
    adds_t = (adds.groupby(["Plant State", "Operating Year", "Technology"], dropna=False)
              .agg(generators=("Generator ID", "count"),
                   nameplate_mw=("Nameplate Capacity (MW)", "sum"),
                   net_summer_mw=("Net Summer Capacity (MW)", "sum"),
                   generators_since_retired=("still_operating", lambda s: int((~s).sum())))
              .reset_index().sort_values(["Plant State", "Operating Year", "Technology"], kind="mergesort"))
    write_csv(adds_t, out / "eia860m_gas_additions_by_state_year.csv")

    plg = pl[pl["Plant State"].isin(states) & pl["Energy Source Code"].isin(GAS_CODES)]
    pl_t = (plg.groupby(["Plant State", "Planned Operation Year", "Technology"], dropna=False)
            .agg(generators=("Generator ID", "count"),
                 nameplate_mw=("Nameplate Capacity (MW)", "sum"),
                 net_summer_mw=("Net Summer Capacity (MW)", "sum"))
            .reset_index().sort_values(["Plant State", "Planned Operation Year"], kind="mergesort"))
    write_csv(pl_t, out / "eia860m_planned_gas_by_state_year.csv")

    by_state = {}
    for st in states:
        a = adds[adds["Plant State"] == st]
        p = plg[plg["Plant State"] == st]
        o = op_s[op_s["Plant State"] == st]
        by_state[st] = {
            "operating_nameplate_mw_by_energy_source": {
                k: round_mw(v) for k, v in o.groupby("Energy Source Code")["Nameplate Capacity (MW)"].sum().items()},
            "gas_nameplate_mw_added_by_year": {
                int(k): round_mw(v) for k, v in a.groupby("Operating Year")["Nameplate Capacity (MW)"].sum().items()},
            "gas_nameplate_mw_added_since": round_mw(a["Nameplate Capacity (MW)"].sum()),
            "gas_generators_added_since": int(len(a)),
            "planned_gas_nameplate_mw_by_year": {
                int(k): round_mw(v) for k, v in p.groupby("Planned Operation Year")["Nameplate Capacity (MW)"].sum().items()
                if pd.notna(k)},
        }
    return {"since_year": since, "gas_energy_source_codes": sorted(GAS_CODES), "by_state": by_state,
            "rows": {"operating": int(len(op)), "planned": int(len(pl)), "retired": int(len(rt))}}


# ---------------------------------------------------------------------------------------
# Part B: EIA API v2 electric-power-operational-data
# ---------------------------------------------------------------------------------------

API_ROW_KEYS = ["period", "location", "sectorid", "fueltypeid", "generation"]


def _api_check_metadata(meta: dict) -> None:
    resp = meta.get("response") or {}
    facets = {f.get("id") for f in resp.get("facets", []) if isinstance(f, dict)}
    data_cols = set((resp.get("data") or {}).keys())
    missing = [f for f in ("location", "sectorid", "fueltypeid") if f not in facets]
    if missing or "generation" not in data_cols:
        raise SchemaChangedError(
            f"EIA route {API_ROUTE}: expected facets location/sectorid/fueltypeid and data 'generation'; "
            f"got facets {sorted(x for x in facets if x)} and data {sorted(data_cols)}. See {API_DOCS}."
        )


def _api_get(url: str, params: list[tuple[str, str]]) -> dict:
    payload = fetch(url, expect="json", params=params, landing_page=API_DOCS).json()
    if "error" in payload or ("response" not in payload):
        msg = payload.get("error") or payload
        raise SourceError(f"EIA API error from {url}: {str(msg)[:400]}")
    return payload


def fetch_generation_live(states: list[str], since: int) -> tuple[dict, list[dict]]:
    key = os.environ.get("EIA_API_KEY")
    if not key:
        raise MissingCredentialError(
            "EIA_API_KEY is not set. Get a free key at https://www.eia.gov/opendata/register.php and export "
            "EIA_API_KEY=..., or run with --skip-generation for capacity only."
        )
    meta = _api_get(API_ROUTE, [("api_key", key)])
    _api_check_metadata(meta)
    base = [("api_key", key), ("frequency", "monthly"), ("data[0]", "generation"), ("facets[sectorid][]", "99"),
            ("start", f"{since}-01"), ("sort[0][column]", "period"), ("sort[0][direction]", "asc"),
            ("sort[1][column]", "location"), ("sort[1][direction]", "asc"),
            ("sort[2][column]", "fueltypeid"), ("sort[2][direction]", "asc")]
    base += [("facets[location][]", s) for s in states]
    rows, offset, total = [], 0, None
    while total is None or offset < total:
        page = _api_get(API_ROUTE + "data/", base + [("offset", str(offset)), ("length", "5000")])
        resp = page["response"]
        total = int(resp.get("total") or 0)
        data = resp.get("data") or []
        log(f"  EIA API page offset={offset}: {len(data)} rows of {total}")
        if not data:
            break
        rows.extend(data)
        offset += len(data)
    return meta, rows


def part_b(meta: dict, rows: list[dict], states: list[str], out: Path) -> dict:
    _api_check_metadata(meta)
    if not rows:
        raise SchemaChangedError("EIA API returned no rows for the requested states/period.")
    df = pd.DataFrame(rows)
    require_columns(df.columns, API_ROW_KEYS, source="EIA API v2 electric-power-operational-data rows",
                    hint=f"Row keys seen: {list(df.columns)}. See {API_DOCS}.")
    df["generation"] = pd.to_numeric(df["generation"], errors="coerce")
    desc_col = next((c for c in ("fuelTypeDescription", "fueltypeDescription", "fuelTypeName") if c in df.columns), None)
    units_col = "generation-units" if "generation-units" in df.columns else None
    tidy = pd.DataFrame({
        "period": df["period"].astype(str),
        "state": df["location"].astype(str),
        "sectorid": df["sectorid"].astype(str),
        "fueltypeid": df["fueltypeid"].astype(str),
        "fuel_description": df[desc_col] if desc_col else None,
        "generation": df["generation"],
        "units": df[units_col] if units_col else None,
    }).sort_values(["state", "period", "fueltypeid"], kind="mergesort")
    tidy = tidy[tidy.state.isin(states)]
    write_csv(tidy, out / "eia923_monthly_generation_by_fuel.csv")

    summary = {"units": sorted(tidy.units.dropna().unique().tolist()) if units_col else None,
               "fueltypeids_present": sorted(tidy.fueltypeid.unique().tolist()),
               "note": "Never summed across fueltypeid (codes overlap, e.g. ALL contains NG).",
               "by_state": {}}
    for st, g in tidy.groupby("state"):
        piv = g[g.fueltypeid.isin(["ALL", "NG"])].pivot_table(index="period", columns="fueltypeid",
                                                               values="generation", aggfunc="first")
        piv = piv.sort_index()
        last12 = piv.tail(12)
        st_sum = {"latest_period": piv.index.max() if len(piv) else None, "months_in_last12_window": int(len(last12))}
        if "ALL" in piv and "NG" in piv:
            all12, ng12 = float(last12["ALL"].sum()), float(last12["NG"].sum())
            st_sum.update({"last12_all_fuels": round(all12, 1), "last12_natural_gas": round(ng12, 1),
                           "last12_gas_share_pct": round(100 * ng12 / all12, 1) if all12 else None})
            yearly = piv.groupby(piv.index.str[:4]).sum(min_count=1)
            st_sum["by_year"] = {y: {"all_fuels": round_mw(r["ALL"]), "natural_gas": round_mw(r["NG"]),
                                     "months": int(piv.index.str[:4].tolist().count(y))}
                                 for y, r in yearly.iterrows()}
        else:
            st_sum["note"] = "ALL and/or NG fueltypeid not present; no share computed."
        summary["by_state"][st] = st_sum
    return summary


def main() -> None:
    p = base_parser(__doc__.split("\n\n")[0])
    p.add_argument("--states", default=",".join(STATES), help="comma list of state codes")
    p.add_argument("--since", type=int, default=2022, help="first operating year counted as 'added' (default 2022)")
    p.add_argument("--month", help="EIA-860M month to use, YYYY-MM (default: newest available)")
    p.add_argument("--xlsx", type=Path, help="use a local EIA-860M generator XLSX")
    p.add_argument("--skip-generation", action="store_true", help="skip Part B (EIA API, needs EIA_API_KEY)")
    args = p.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=True)
    states = [s.strip().upper() for s in args.states.split(",") if s.strip()]

    sources = []
    if args.fixture:
        content, src860 = FIX_860M.read_bytes(), str(FIX_860M.relative_to(FIXTURES.parent))
    elif args.xlsx:
        content, src860 = args.xlsx.read_bytes(), str(args.xlsx)
    else:
        content, src860 = download_860m(args.month)
    sources.append({"part": "A", "dataset": "EIA-860M", "url_or_file": src860, "landing_page": LANDING_860M})

    # All downloads happen before anything is written, so a failure leaves earlier outputs intact.
    meta = rows = None
    if not args.skip_generation:
        if args.fixture:
            meta = json.loads(FIX_API_META.read_text())
            rows = json.loads(FIX_API_DATA.read_text())["response"]["data"]
            sources.append({"part": "B", "dataset": "EIA API v2 electric-power-operational-data (SYNTHETIC fixture)",
                            "url_or_file": str(FIX_API_DATA.relative_to(FIXTURES.parent))})
        else:
            meta, rows = fetch_generation_live(states, args.since)
            sources.append({"part": "B", "dataset": "EIA API v2 electric-power-operational-data",
                            "url_or_file": API_ROUTE + "data/"})

    a = part_a(content, states, args.since, out)
    b = part_b(meta, rows, states, out) if rows is not None else None

    meta_block = run_meta(args.fixture, sources)
    if args.fixture:
        meta_block["fixture_warning"] += " EIA fixtures are SYNTHETIC values in the real layout."
    summary = {**meta_block, "states": states, "capacity_860m": a, "generation_923": b,
               "generation_923_skipped": bool(args.skip_generation)}
    write_json(summary, out / "eia_summary.json")
    log(f"Wrote EIA outputs to {out}")


if __name__ == "__main__":
    run_main(main)
