# Ledger scrapers: the physical footprint of AI compute

First scrapers for the public ledger. Each script downloads one publisher's structured file,
or the most structured thing that publisher offers. It writes a CSV and a summary JSON
whose numbers trace back to a URL, not to anyone's reading of a report.

Source formats were inspected on **2026-10-20** from a build environment that could not reach the
publishers' hosts. The proxy refused ERCOT, PJM, EIA, MISO, SPP, NYISO and NESO, so formats
were read with web search and page fetches and checked against the open-source `gridstatus` parsers.
**No script has yet been run against a live source.** See [Test status](#test-status).

```
scrapers/
  _common.py                 shared helpers: fetch with "file moved" detection, schema checks, atomic writes
  ercot_large_load.py        ERCOT large-load queue figures from ERCOT PDFs
  pjm_queue.py               PJM interconnection queue (+ optional load-forecast adjustments, raw)
  miso_spp_nyiso_queues.py   MISO + SPP + NYISO queues -> one normalised CSV
  eia_860_923.py             EIA-860M capacity by plant/fuel + EIA-923 monthly generation by fuel
  neso_demand.py             GB transmission-connected demand (NESO EA register), data-centre subset
  cross_check.py             one neutral sentence per region from the outputs above
  fixtures/                  sample inputs for offline tests + make_fixtures.py + provenance.json
  requirements.txt
```

## What each script reveals

| Script | Source | What it shows | Main outputs |
|---|---|---|---|
| `ercot_large_load.py` | ERCOT monthly reports and board decks (PDF) | Texas large-load requests by stage (No Studies Submitted, Under ERCOT Review, Section 9.5 Requirements Met, Observed Energized, Approved but not operational), total GW, ERCOT's stated data-centre share, MW approved to energize, observed peak | `ercot_large_load_metrics.csv`, `ercot_large_load_summary.json` |
| `pjm_queue.py` | PJM queue XLS export | Generation requests in the 13-state PJM footprint (VA, OH, PA...) by fuel and status; gas MW queued per state | `pjm_queue.csv`, `pjm_queue_summary.json` |
| `miso_spp_nyiso_queues.py` | MISO JSON, SPP CSV, NYISO XLSX | Same as above for MISO (WI, LA...), SPP (LA, OK, TX panhandle...) and NYISO. NYISO is the only queue that also lists **load** requests | `iso_queues_normalised.csv`, `iso_queues_summary.json` |
| `eia_860_923.py` | EIA-860M XLSX; EIA API v2 | Plant-level capacity by fuel in VA, TX, GA, OH, AZ, PA, WI, LA; natural-gas capacity added per state per year since 2022 (and planned); monthly net generation, all fuels vs natural gas | `eia860m_*.csv`, `eia923_monthly_generation_by_fuel.csv`, `eia_summary.json` |
| `neso_demand.py` | NESO Existing Agreement (EA) register; TEC register (optional) | GB transmission-connected demand projects and the subset whose name says data centre / hyperscale (a lower bound) | `neso_ea_demand_projects.csv`, `neso_data_centre_demand.csv`, `neso_demand_summary.json` |
| `cross_check.py` | the summaries above | `cross_checks.json`: e.g. "Texas: X GW of large-load requests in ERCOT's queue vs Y GW of natural-gas capacity added since 2022 (EIA-860M)" | `cross_checks.json` |

Not scripted: the **EU EED data-centre database** (Delegated Reg. 2024/1364). As of
2026-10-19 it is EU-Login only, with no public per-site extract (see `registry/sources.json`).

## Confirmed URLs and real column names (2026-10-20)

"Seen" means the fetcher returned the file or page and the columns below were read from it.
"Via gridstatus" means the names come from the parser in `gridstatus` (commit `8a4d099`,
2026-10-16), which runs against the live file, but the file itself was not seen here.

| Source | URL | Status | Columns / fields |
|---|---|---|---|
| SPP queue | `https://opsportal.spp.org/Studies/GenerateSummaryCSV` | **Seen** (file dated 10/19/2026) | Line 1 `"Last Updated On",10/19/2026,`; header: Generation Interconnection Number, IFS Queue Number, Current Cluster, Cluster Group, Nearest Town or County (leading space per gridstatus), State, TO at POI, In-Service Date, Commercial Operation Date, Cessation Date, Original Generator Commercial Op Date, Capacity, MAX Summer MW, MAX Winter MW, Service Type, Requested Maximum Injection Capability (MW), Requested Network Resource Deliverability (MW), Nameplate Capacity, Generation Type, Fuel Type, Substation or Line, Request Received, Date Withdrawn, Status, JTIQ Participant, JTIQ Commitment, Cause of Delay |
| PJM queue (page) | `https://www.pjm.com/planning/m/cycle-service-request-status` | **Seen** (1,792 projects). The old Serial page says its data "is no longer current" | Table: Project ID, Name, State, Status, TO, MFO, MW Energy, MW Capacity, MW In Service, Fuel |
| PJM queue (export) | `POST https://services.pjm.com/PJMPlanningApi/api/Queue/ExportToXls` (header `api-subscription-key`) | Via gridstatus | Project ID, Name, Commercial Name, County, State, Transmission Owner, Submitted Date, Withdrawal Date, Withdrawn Remarks, Status, Projected In Service Date, Actual In Service Date, Fuel, MW Capacity, MW Energy, MFO, MW In Service, + study columns |
| PJM load-forecast adjustments | `https://www.pjm.com/-/media/DotCom/planning/res-adeq/load-forecast/total-load-adjustments-breakdown.xlsx` | Link seen on the [load-forecast page](https://www.pjm.com/planning/resource-adequacy-planning/load-forecast-dev-process.aspx); file not opened | **Unknown**: saved raw, not interpreted |
| MISO queue | `https://www.misoenergy.org/api/giqueue/getprojects` | Via gridstatus (the fetcher got a client error) | projectNumber, county, state, transmissionOwner, poiName, queueDate, withdrawnDate, applicationStatus, summerNetMW, winterNetMW, negInService, fuelType, facilityType, postGIAStatus, doneDate, inService, giaToExec, studyCycle, studyGroup, studyPhase, svcType, dp1ErisMw, dp1NrisMw, dp2ErisMw, dp2NrisMw, sisPhase1 |
| NYISO queue | `https://www.nyiso.com/documents/20142/1407078/NYISO-Interconnection-Queue.xlsx` | Via gridstatus (binary) | Sheets: Interconnection Queue, " Cluster Projects", Withdrawn, Cluster Projects-Withdrawn, In Service (two-row header). Columns: Queue Pos., Project Name, Date of IR, SP (MW), WP (MW), Type/ Fuel, County, State, Z, Points of Interconnection, Utility, S, Last Updated Date, Availability of Studies, Proposed COD... (order unverified) |
| EIA-860M | `https://www.eia.gov/electricity/data/eia860m/xls/august_generator2026.xlsx` (latest; released 2026-09-24, next 2026-10-23); older months under `.../eia860m/archive/xls/` | **Landing page seen**; columns via gridstatus | Entity ID, Entity Name, Plant ID, Plant Name, Plant State, County, Balancing Authority Code, Sector, Generator ID, Unit Code, Nameplate Capacity (MW), Net Summer Capacity (MW), Net Winter Capacity (MW), Technology, Energy Source Code, Prime Mover Code, Operating Month, Operating Year, ..., Status, Latitude, Longitude; Planned sheet: Planned Operation Month/Year; Retired sheet: Retirement Month/Year |
| EIA API v2 | `https://api.eia.gov/v2/electricity/electric-power-operational-data/data/` | Facet ids and data id confirmed by third-party code that calls the live API; envelope from [EIA docs](https://www.eia.gov/opendata/documentation.php) | Facets `location`, `sectorid`, `fueltypeid`; data `generation`; row keys assumed to equal those ids (checked at runtime against route metadata) |
| ERCOT large load | e.g. `https://www.ercot.com/files/docs/2026/05/13/ERCOT-Monthly-April-2026-FINAL.pdf`, `.../2026/04/13/9-Interconnection-and-Grid-Analysis-Update.pdf`, `.../2026/09/16/ERCOT-Monthly-Operational-Overview-August-2026.pdf` | **Seen** (text) | No table or file. Figures are printed in prose; status labels as listed above. No county, no per-project data, no data-centre flag (only a % share) |
| NESO EA register | `https://www.neso.energy/document/373996/download` (anchor "EA register" on `https://www.neso.energy/industry-information/connections-reform`) | Link seen; file binary, not opened | Only **Project Name (col A)** and **Technology Type (col F) = "Transmission Connected Demand"** are confirmed (NESO FOI/25/174). MW column name **unknown** |
| NESO TEC register | `https://api.neso.energy/dataset/cbd45e54-e6e2-4a38-99f1-8de6fd96d7c1/resource/17becbab-e3e8-473f-b303-3806f43a6a10/download/tec-register-16-october-2026.csv` | Data dictionary seen; CSV robots-blocked | Project Name, Customer Name, Connection Site, Stage, MW Connected, MW Increase / Decrease, Cumulative Total Capacity (MW), MW Effective From, Project Status, Agreement Type, HOST TO, Plant Type, Project ID, Project Number, Gate |

What the pointers in `registry/sources.json` turned into:
* **ERCOT**: no monthly large-load *status report file* is published. NPRR1267 (approved
  2025-07-31) requires aggregate reporting only. The figures live in the "ERCOT Monthly",
  "Monthly Operational Overview" and board-deck PDFs.
* **PJM**: the queue now lives on the *Cycle* Service Request Status page, not the Serial one.
* **NESO**: NESO states it "does not maintain a demand connections register". The EA
  register is the public route it points to, and it covers only consenting Gate 2 applicants.

## Running from an ordinary connection

```bash
cd scrapers
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export EIA_API_KEY=...            # free key: https://www.eia.gov/opendata/register.php
# optional:
# export PJM_QUEUE_SUBSCRIPTION_KEY=...   # if PJM rotates the public key its own web page uses
# export LEDGER_USER_AGENT="your-project/1.0 (contact@example.org)"
```

### Run order

Steps 1 to 5 are independent and can run in any order or in parallel. `cross_check.py` must
run last because it reads their summaries from `out/`.

```bash
python ercot_large_load.py        --out out/   # 1  (add --url <pdf> for newer ERCOT PDFs)
python pjm_queue.py               --out out/   # 2  (--with-load-adjustments to save PJM's raw XLSX too)
python miso_spp_nyiso_queues.py   --out out/   # 3  (--only SPP,NYISO / --allow-partial)
python eia_860_923.py             --out out/   # 4  (--skip-generation if no EIA key; --month 2026-08)
python neso_demand.py             --out out/   # 5  (--with-tec; --mw-column "<name>" once you've seen the file)
python cross_check.py --in out/   --out out/   # 6  last
```

Manual fallbacks when an automated download is blocked or moved:
`pjm_queue.py --xlsx <file from the Cycle page "Full Export -> XLS">`,
`eia_860_923.py --xlsx <860M file>`, `neso_demand.py --ea-file <EA register>`,
`ercot_large_load.py --url <pdf>`.

**First live run checklist** (things that could not be confirmed from here):
1. `neso_demand.py`: open the EA register, confirm the MW column, and pin it with `--mw-column`.
2. `pjm_queue.py --with-load-adjustments`: look at the raw CSVs before using any number from them.
3. `miso_spp_nyiso_queues.py`: confirm MISO's `applicationStatus` values in `status_group_map`.
4. `ercot_large_load.py`: check that `status_snapshot.statuses_reconcile_with_stated_total` is `true`.

### Behaviour

* **Idempotent:** outputs are overwritten atomically, never appended. Downloads happen
  before anything is written, so a failed run leaves the previous outputs intact.
  Fixture runs are byte-identical across runs (checked).
* **Moved files:** publishers usually redirect a moved file to an HTML page rather than
  returning 404. `fetch()` checks magic bytes (xlsx/pdf), parses JSON, and rejects HTML for
  CSV. Any mismatch raises `SourceMovedError` naming the landing page to check.
* **Changed columns:** each parser lists the columns it needs. If one is missing it stops
  with `SchemaChangedError` and prints the columns it did find. It never guesses a replacement.
* **Exit codes:** 0 ok · 2 source error · 3 file moved / access denied · 4 host unreachable ·
  5 schema changed · 6 missing credential (`EIA_API_KEY`).

## Fixture tests (offline)

```bash
python ercot_large_load.py       --fixture --out out/fixture_run
python pjm_queue.py              --fixture --out out/fixture_run
python miso_spp_nyiso_queues.py  --fixture --out out/fixture_run
python eia_860_923.py            --fixture --out out/fixture_run
python neso_demand.py            --fixture --out out/fixture_run
python cross_check.py            --fixture --out out/fixture_run   # also runs all five above itself
python fixtures/make_fixtures.py   # rebuilds fixtures/ byte-identically (needs reportlab)
```

Every fixture-mode summary has `"mode": "fixture"` and a `fixture_warning`. In
`cross_checks.json`, `data_mode` is `fixture` (or `mixed`) and every affected sentence
starts with **`[FIXTURE DATA - NOT REAL]`**. Fixture numbers test parsing only.

## Test status

Run in the build environment on 2026-10-20. **Live mode was not run for any script** (hosts blocked).
Live attempts from here fail cleanly, as designed: exit code 4 with the proxy's 403, or exit
code 2 where a script collects several failed downloads (ERCOT, MISO/SPP/NYISO). Nothing is written.

| Script | Live run | Fixture run | Fixture provenance (`fixtures/provenance.json`) | Parsed values checked by hand |
|---|---|---|---|---|
| `ercot_large_load.py` | not run | **passed** | REAL-VERBATIM: text from 3 ERCOT PDFs; April 2026 excerpt re-typeset as a PDF to test pypdf | yes: 5 statuses sum to the stated 445.8 GW |
| `pjm_queue.py` | not run | **passed** | REAL-VERBATIM: 15 rows from the Cycle page table, under gridstatus' export column names | yes |
| `miso_spp_nyiso_queues.py` (SPP) | not run | **passed** | REAL-VERBATIM: 16 rows of the live CSV | yes |
| `miso_spp_nyiso_queues.py` (MISO) | not run | **passed** | REAL-VIA-GRIDSTATUS: 13 rows; status/date hidden for 10 of them (null) | yes |
| `miso_spp_nyiso_queues.py` (NYISO) | not run | **passed** | REAL-VIA-GRIDSTATUS: 9 rows; column order assumed; no load rows | yes |
| `eia_860_923.py` | not run | **passed** | **SYNTHETIC** values in the gridstatus-verified 860M layout; synthetic API JSON | yes |
| `neso_demand.py` | not run | **passed** | **SYNTHETIC**: only EA columns A/F verified; TEC header from data dictionary | yes |
| `cross_check.py` | not run | **passed** | consumes the above | n/a |

Also exercised: moved-file detection (404, and HTML served in place of XLSX/JSON, against a
local HTTP server); schema-change errors for every parser (renamed or missing column, sheet
or label); ERCOT table-layout wording; idempotent re-runs.

## Judgement calls (audit these)

All are applied in code and visible in the outputs, never hidden:
* `fuel_group` (`_common.py`): raw labels are mapped to gas/solar/wind/storage/hybrid/...
  Dual-fuel gas/oil counts as gas, and multi-technology labels count as hybrid. `fuel_raw`
  is kept in every row.
* Data-centre flag: the project name must match `data[ _-]?cent(er|re)|datacent(er|re)|hyperscale`.
  This is a lower bound everywhere.
* Status groups: each summary prints the `status_group_map` it actually applied. SPP
  "IA FULLY EXECUTED/ON SCHEDULE" counts as *active* (signed, not built).
* Queue MW: PJM uses MW Energy (MFO and MW Capacity are reported too). MISO uses
  max(summer, winter). SPP uses Capacity. NYISO uses max(SP, WP).
* "Gas capacity added since 2022": EIA-860M Energy Source Code `NG`, Operating Year ≥ 2022,
  nameplate MW, including units that have since retired. Uprates are excluded.
* EIA generation: never summed across `fueltypeid`, because codes overlap (ALL ⊃ NG).

## Credits

Raw column names for MISO, NYISO, PJM's export and EIA-860M were cross-checked against
[gridstatus](https://github.com/gridstatus/gridstatus) (BSD-3-Clause, © 2022 James Max Kanter).
NYISO's fuel-code map is copied from it with attribution in the code.

## Climate TRACE cross-check (added 2026-10-20)

`climate_trace_match.py` matches the generators named in ledger entries (Chesterfield, Memphis, Southaven,
Richland Parish, Homer City, Oak Creek) against Climate TRACE's asset-level electricity-generation
emissions file (power sector package, CC BY 4.0, monthly). Climate TRACE estimates plant emissions
from satellites and sensors, independently of the operator, so a matched plant gets an emissions
number nobody in the industry controls. It does not cover datacenters themselves.

Run: `python3 climate_trace_match.py --power-zip power.zip --out out/` after downloading the power
package from https://climatetrace.org/downloads. Offline test: `--fixture` (synthetic rows).

Read the `method` column: `name` means the asset name shared a token with the ledger plant; `nearest`
means only proximity matched, which can pick up a neighbouring plant (the fixture run shows this for
Memphis). Treat `nearest` matches as leads, not confirmations. New plants may not appear until they
have operated for a reporting period.

## Weekly pulls and page watch (added 2026-10-23)

`.github/workflows/weekly-pulls.yml` runs every Monday and opens a pull request when anything is new. Nothing it finds enters the ledger's tables directly: each item is a first reading for a person to check against its document (CONTRIBUTING.md, two-reading rule), after which the person edits the transcription in `sites/metered/` and CI rebuilds everything.

| Script | Source | Config | What it reports |
|---|---|---|---|
| `pull_nei.py` | EPA National Emissions Inventory facility summaries (Envirofacts DMAP), NAICS 518210, 16 states, every released NEI year | in the script | facilities and pollutant totals new to `sites/metered/va_nei_transcribed.csv` or changed |
| `pull_ie_aer.py` | Ireland's EPA LEAP Open Data API | `config/ie_leap_licences.json` | annual environmental reports not yet read, with a first reading of Table 3 and Table 5; licence profiles found by operator name and not yet listed |
| `pull_benchmarking.py` | city benchmarking portals (Socrata and ArcGIS) | `config/benchmarking_portals.json` | Data Center rows (and known datacenter addresses filed as Office) new to `sites/metered/benchmarking_transcribed.csv` or changed |
| `watch_pages.py` | pages with no API: DEQ's datacenter permit list, PJM's load-analysis materials, Grant County PUD and SRP datacenter pages, the CSO's annual release | `config/watch_pages.json`, state in `data/watch/` | new links, changed sentences with figures, a new year's release |
| `pull_report.py` | the dated folder | | `SUMMARY.md` for the pull request; deletes the folder when nothing is new |

All four have `--fixture` modes that CI runs on every push; fixture provenance is in `fixtures/provenance.json` (real values in assembled layouts are labelled as such, synthetic files as synthetic). None has been run live from the build environment, which has no route to these hosts; the first live run is the first Monday after the push, or any time from the Actions tab (Run workflow). One-time setting: Settings > Actions > General > Workflow permissions > "Allow GitHub Actions to create and approve pull requests".
