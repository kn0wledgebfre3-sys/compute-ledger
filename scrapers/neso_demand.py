#!/usr/bin/env python3
"""GB transmission-connected demand from NESO's Existing Agreement (EA) Register, filtered to data centres.

WHAT NESO PUBLISHES (inspected 2026-10-20)
------------------------------------------
* NESO says it "does not maintain a demand connections register" (FOI/25/174, 2025-12-18,
  https://www.neso.energy/document/374976/download) and has no "single register of demand
  connections" (FOI/25/186, https://www.neso.energy/document/375161/download).
* The same FOI/25/174 response points to the EA Register as the public place to find
  data-centre demand: filter "Technology Type" (column F) = "Transmission Connected Demand"
  and "Project Name" (column A) containing "Data Centre".
  EA register link (anchor text "EA register" on
  https://www.neso.energy/industry-information/connections-reform):
      https://www.neso.energy/document/373996/download
  It lists projects that applied for Gate 2 AND consented to inclusion (FOI/25/199,
  https://www.neso.energy/document/378646/download), so it is NOT a complete census.
* The TEC Register (CSV, CKAN dataset 'transmission-entry-capacity-tec-register', latest
  resource at inspection:
  https://api.neso.energy/dataset/cbd45e54-e6e2-4a38-99f1-8de6fd96d7c1/resource/17becbab-e3e8-473f-b303-3806f43a6a10/download/tec-register-16-october-2026.csv)
  covers GENERATION contracts only. With --with-tec the script scans it for project names
  mentioning data centres (on-site / co-located generation).
* Context only, not parsed: NESO's Demand Call for Input summary (March 2026,
  https://www.neso.energy/document/378226/download) reports ~50.8 GW of data-centre demand
  in 152 "project phases" (55% of 92.9 GW of CFI demand). That is aggregate PDF text, with no
  site list.

COLUMNS FOUND
-------------
EA register: the file is binary (XLSX presumed) and could NOT be opened from the sandbox.
Only two columns are confirmed, by NESO's own FOI text: column A "Project Name" and
column F "Technology Type" (value "Transmission Connected Demand"). The MW column name is
UNKNOWN. The script picks the first header containing "MW" and records which one it used
(``mw_column_used``, ``mw_column_verified: false``), or takes --mw-column.
TEC register (from the data-portal data dictionary): Project Name, Customer Name,
Connection Site, Stage, MW Connected, MW Increase / Decrease, Cumulative Total Capacity (MW),
MW Effective From, Project Status, Agreement Type, HOST TO, Plant Type, Project ID,
Project Number, Gate. (The CSV itself is robots-blocked for WebFetch, so values were not seen.)

DATA-CENTRE FLAG
----------------
Project Name matches /data[ _-]?cent(er|re)s?|datacent(er|re)|hyperscale/i. This is a LOWER
BOUND: many data-centre connections sit under SPV or company names. Ofgem's July 2026
consultation reports 315 data-centre projects (~73 GW) in the GB demand queue, far more than
any name filter will find.

OUTPUTS
-------
  neso_ea_demand_projects.csv     all 'Transmission Connected Demand' rows + is_data_centre_name
  neso_data_centre_demand.csv     the subset whose name says data centre
  neso_tec_data_centre_named.csv  (--with-tec) TEC rows whose name says data centre
  neso_demand_summary.json

USAGE
-----
  python neso_demand.py --out out/
  python neso_demand.py --with-tec --out out/
  python neso_demand.py --ea-file ~/Downloads/EA_register.xlsx --mw-column "Demand MW" --out out/
  python neso_demand.py --fixture --out out/fixture_run     # SYNTHETIC fixtures, parser test
"""

from __future__ import annotations

import io
import re
from pathlib import Path

import pandas as pd

from _common import (
    DC_NAME_RE,
    FIXTURES,
    SchemaChangedError,
    SourceError,
    SourceMovedError,
    base_parser,
    fetch,
    find_header_row,
    is_data_centre_name,
    log,
    require_columns,
    round_mw,
    run_main,
    run_meta,
    write_csv,
    write_json,
)

EA_LANDING = "https://www.neso.energy/industry-information/connections-reform"
EA_URL_FALLBACK = "https://www.neso.energy/document/373996/download"
TEC_LANDING = "https://www.neso.energy/data-portal/transmission-entry-capacity-tec-register"
TEC_CKAN = "https://api.neso.energy/api/3/action/package_show?id=transmission-entry-capacity-tec-register"
TEC_URL_FALLBACK = ("https://api.neso.energy/dataset/cbd45e54-e6e2-4a38-99f1-8de6fd96d7c1/resource/"
                    "17becbab-e3e8-473f-b303-3806f43a6a10/download/tec-register-16-october-2026.csv")
DEMAND_VALUE = "transmission connected demand"
TEC_COLUMNS = ["Project Name", "Customer Name", "Connection Site", "Stage", "MW Connected",
               "MW Increase / Decrease", "Cumulative Total Capacity (MW)", "MW Effective From",
               "Project Status", "Agreement Type", "HOST TO", "Plant Type", "Project ID", "Project Number", "Gate"]

FIX_EA = FIXTURES / "neso" / "ea_register_SYNTHETIC.xlsx"
FIX_TEC = FIXTURES / "neso" / "tec_register_SYNTHETIC.csv"


def discover_ea_url() -> str:
    """Find the current 'EA register' link on the Connections Reform page (document ids change on republish)."""
    try:
        html = fetch(EA_LANDING, expect="html").text()
    except SourceError as exc:
        log(f"  could not read {EA_LANDING} ({exc}); using known link")
        return EA_URL_FALLBACK
    m = re.search(r'href="([^"]*?/document/\d+/download)"[^>]*>\s*(?:<[^>]+>\s*)*EA register', html, re.I)
    if not m:
        log("  'EA register' link not found on the landing page; using known link")
        return EA_URL_FALLBACK
    href = m.group(1)
    return href if href.startswith("http") else "https://www.neso.energy" + href


def read_ea(content: bytes) -> tuple[pd.DataFrame, str]:
    """Return (rows with header applied, sheet name). Accepts XLSX or CSV."""
    if content.startswith(b"PK\x03\x04"):
        xls = pd.ExcelFile(io.BytesIO(content), engine="openpyxl")
        for sheet in xls.sheet_names:
            raw = pd.read_excel(xls, sheet_name=sheet, header=None, dtype=object)
            hdr = find_header_row(raw.values.tolist(), ["Project Name", "Technology Type"])
            if hdr >= 0:
                df = raw.iloc[hdr + 1:].copy()
                df.columns = [str(c).strip() if c is not None and str(c) != "nan" else f"col{j}"
                              for j, c in enumerate(raw.iloc[hdr].tolist())]
                return df.dropna(how="all"), sheet
        raise SchemaChangedError(
            f"NESO EA register: no sheet has both 'Project Name' and 'Technology Type' headers "
            f"(sheets: {xls.sheet_names}). See {EA_LANDING}.")
    text = content.decode("utf-8-sig", errors="replace")
    if text.lstrip().lower().startswith("<"):
        raise SourceMovedError(f"NESO EA register link returned an HTML page, not a spreadsheet: the document "
                               f"has probably been republished under a new id. See {EA_LANDING}.")
    raw = pd.read_csv(io.StringIO(text), header=None, dtype=object)
    hdr = find_header_row(raw.values.tolist(), ["Project Name", "Technology Type"])
    if hdr < 0:
        raise SchemaChangedError("NESO EA register (CSV): header with 'Project Name' and 'Technology Type' not found.")
    df = raw.iloc[hdr + 1:].copy()
    df.columns = [str(c).strip() for c in raw.iloc[hdr].tolist()]
    return df.dropna(how="all"), "csv"


def pick_mw_column(columns: list[str], override: str | None) -> str | None:
    if override:
        if override not in columns:
            raise SchemaChangedError(f"--mw-column {override!r} not in EA register columns {columns}")
        return override
    for c in columns:
        if re.search(r"\bMW\b", c, re.I) and not re.search(r"MVA|date|effective", c, re.I):
            return c
    return None


def process_ea(content: bytes, mw_override: str | None, out: Path) -> dict:
    df, sheet = read_ea(content)
    require_columns(df.columns, ["Project Name", "Technology Type"], source="NESO EA register")
    cols = list(df.columns)
    tech = df["Technology Type"].map(lambda v: re.sub(r"\s+", " ", str(v)).strip().lower() if pd.notna(v) else "")
    demand = df[tech == DEMAND_VALUE].copy()
    tech_values = sorted({t for t in tech if t})
    if demand.empty:
        raise SchemaChangedError(
            f"NESO EA register: no rows with Technology Type 'Transmission Connected Demand'. "
            f"Values present: {tech_values[:40]}")
    mw_col = pick_mw_column(cols, mw_override)
    demand["is_data_centre_name"] = demand["Project Name"].map(is_data_centre_name)
    demand["mw"] = pd.to_numeric(demand[mw_col], errors="coerce") if mw_col else None
    demand = demand.sort_values("Project Name", kind="mergesort")
    lead = ["Project Name", "Technology Type", "is_data_centre_name", "mw"]
    demand = demand[lead + [c for c in demand.columns if c not in lead]]
    write_csv(demand, out / "neso_ea_demand_projects.csv")
    dc = demand[demand.is_data_centre_name]
    write_csv(dc, out / "neso_data_centre_demand.csv")
    return {
        "sheet": sheet,
        "columns_found": cols,
        "technology_type_values": tech_values,
        "demand_projects": int(len(demand)),
        "data_centre_named_projects": int(len(dc)),
        "mw_column_used": mw_col,
        "mw_column_verified": False if not mw_override else "user-specified",
        "demand_mw_total": round_mw(demand["mw"].sum()) if mw_col else None,
        "data_centre_named_mw_total": round_mw(dc["mw"].sum()) if mw_col else None,
        "data_centre_name_pattern": DC_NAME_RE.pattern,
        "data_centre_named_list": dc[["Project Name"] + (["mw"] if mw_col else [])].to_dict("records"),
    }


def tec_csv_url() -> str:
    try:
        pkg = fetch(TEC_CKAN, expect="json", landing_page=TEC_LANDING).json()
        res = [r for r in pkg["result"]["resources"] if str(r.get("format", "")).lower() == "csv"]
        res.sort(key=lambda r: r.get("last_modified") or r.get("created") or "", reverse=True)
        if res:
            return res[0]["url"]
    except (SourceError, KeyError, TypeError) as exc:
        log(f"  CKAN lookup failed ({exc}); using known TEC link")
    return TEC_URL_FALLBACK


def process_tec(content: bytes, out: Path) -> dict:
    df = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
    df.columns = [c.strip() for c in df.columns]
    require_columns(df.columns, ["Project Name", "Plant Type", "MW Connected", "MW Increase / Decrease"],
                    source="NESO TEC register", hint=f"Landing page: {TEC_LANDING}")
    hit = df[df["Project Name"].map(is_data_centre_name) | df.get("Customer Name", pd.Series("", index=df.index))
             .map(is_data_centre_name)].copy()
    write_csv(hit, out / "neso_tec_data_centre_named.csv")
    return {
        "rows": int(len(df)),
        "data_centre_named_rows": int(len(hit)),
        "plant_types_of_named_rows": sorted(hit["Plant Type"].unique().tolist()),
        "note": "TEC covers generation contracts; matches indicate on-site/co-located generation, not demand.",
    }


def main() -> None:
    p = base_parser(__doc__.split("\n\n")[0])
    p.add_argument("--ea-file", type=Path, help="local copy of the EA register (xlsx or csv)")
    p.add_argument("--mw-column", help="EA register column to use for MW (default: first header containing 'MW')")
    p.add_argument("--with-tec", action="store_true", help="also scan the TEC register for data-centre names")
    args = p.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=True)

    sources = []
    if args.fixture:
        ea_bytes = FIX_EA.read_bytes()
        sources.append({"dataset": "EA register (SYNTHETIC fixture)", "file": str(FIX_EA.relative_to(FIXTURES.parent)),
                        "real_url": EA_URL_FALLBACK})
    elif args.ea_file:
        ea_bytes = args.ea_file.read_bytes()
        sources.append({"dataset": "EA register", "file": str(args.ea_file)})
    else:
        url = discover_ea_url()
        log(f"GET {url}")
        f = fetch(url, expect="html", landing_page=EA_LANDING)  # format unknown: validated in read_ea
        ea_bytes = f.content
        sources.append({"dataset": "EA register", "url": url, "final_url": f.final_url, "landing_page": EA_LANDING})

    # All downloads happen before anything is written, so a failure leaves earlier outputs intact.
    tec_bytes = None
    if args.with_tec or args.fixture:
        if args.fixture:
            tec_bytes = FIX_TEC.read_bytes()
            sources.append({"dataset": "TEC register (SYNTHETIC fixture)", "file": str(FIX_TEC.relative_to(FIXTURES.parent))})
        else:
            url = tec_csv_url()
            log(f"GET {url}")
            tec_bytes = fetch(url, expect="csv", landing_page=TEC_LANDING).content
            sources.append({"dataset": "TEC register", "url": url, "landing_page": TEC_LANDING})

    ea = process_ea(ea_bytes, args.mw_column, out)
    tec = process_tec(tec_bytes, out) if tec_bytes is not None else None

    meta = run_meta(args.fixture, sources)
    if args.fixture:
        meta["fixture_warning"] += " NESO fixtures are SYNTHETIC (only two EA columns are verified)."
    summary = {
        **meta,
        "coverage_warning": ("EA register lists only Gate 2 applicants that consented to publication; name-based "
                             "data-centre flag is a lower bound."),
        "ea_register": ea,
        "tec_register": tec,
    }
    write_json(summary, out / "neso_demand_summary.json")
    log(f"Wrote NESO outputs to {out}: {ea['demand_projects']} demand rows, "
        f"{ea['data_centre_named_projects']} named as data centres")


if __name__ == "__main__":
    run_main(main)
