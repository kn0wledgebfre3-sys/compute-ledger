# NEI / DEQ generator-activity search — Virginia top-60 datacenter sites (run 2026-10-23)

## Bottom line
- A working route exists: EPA Envirofacts "DMAP" REST service, tables `nei.vw_facility_summaries_2020` and `nei.vw_facility_summaries_2023`. Returns JSON or CSV with no login.
- It gives **annual facility-wide emissions per pollutant only**. No SCC, no unit/process breakdown, **no hours operated, no fuel burned**. Hours cannot be read from this source; they can only be derived (not done here).
- Of the 60 registrations: 13 matched with confidence (name, address, or DEQ registration number embedded in the NEI site name), 3 more are flagged UNCONFIRMED (same street, different number/entity), 44 not found in either NEI year.
- Latest inventory year available: **2023 NEI** (view `nei.vw_facility_summaries_2023` exists and is populated). 2020 is the prior triennial year. Nothing newer.

## Routes tried
| Route | Result |
|---|---|
| `https://data.epa.gov/dmapservice/nei.vw_facility_summaries_2020/...` and `..._2023/...` | WORKS (JSON and CSV). Table name found on https://www.epa.gov/enviro/envirofacts-data-service-api (only NEI example there is `nei.vw_facility_summaries_2020`; `_2023` was a guess that resolved). |
| `https://data.epa.gov/dmapservice/nei.nei_facility_summary/...` (guessed name) | client error (table does not exist). |
| `https://echodata.epa.gov/echo/air_rest_services.get_facilities?...` (ECHO REST) | Blocked for this tooling (robots disallowed); shell has no outbound internet (proxy 403 to echodata.epa.gov and data.epa.gov). |
| `https://enviro.epa.gov/envirofacts/metadata/search` and `/nei/search` | Blocked (robots disallowed). |
| EPA 2020 NEI data page https://www.epa.gov/air-emissions-inventories/2020-national-emissions-inventory-nei-data | Lists only the Qlik "Data Retrieval Tool" (JS app, unreadable here) and bulk ZIPs at gaftp.epa.gov (binary, unreadable here). The process-level file that WOULD carry SCC and per-unit emissions is `https://gaftp.epa.gov/air/nei/2020/data_summaries/2020nei_facility_process_byregions.zip` (421 MB) — not retrievable in this session. |
| Virginia DEQ emissions-inventory page https://www.deq.virginia.gov/permits/air/emissions-inventory | client error (not retrieved). No DEQ statewide point-source spreadsheet located within budget. |
| ECHO "Air Emissions Download" summary https://echo.epa.gov/tools/data-downloads/air-emissions-download-summary | Describes a nationwide facility-level file with columns REPORTING_YEAR, REGISTRY_ID, PGM_SYS_ACRNM, PGM_SYS_ID, POLLUTANT_NAME, ANNUAL_EMISSION, UNIT_OF_MEASURE, NEI_TYPE, NEI_HAP_VOC_FLAG — facility-level only, same limitation. Not downloaded. |

## Exact endpoint patterns that worked
```
https://data.epa.gov/dmapservice/nei.vw_facility_summaries_2023/state_abbr/equals/VA/naics_code/equals/518210/pollutant_code/equals/NOX/1:500/JSON
https://data.epa.gov/dmapservice/nei.vw_facility_summaries_2023/state_abbr/equals/VA/county_fips/equals/51107/pollutant_code/equals/NOX/1:500/CSV
https://data.epa.gov/dmapservice/nei.vw_facility_summaries_2023/eis_facility_id/equals/21504811/pollutant_type/equals/CAP/1:200/CSV
https://data.epa.gov/dmapservice/nei.vw_facility_summaries_2020/eis_facility_id/equals/17626111/pollutant_type/equals/CAP/1:200/CSV
```
- Column names in the view: `address, address_postal_code, city_name, code_description, county_fips, county_name, description, eis_facility_id, emissions, facility_type, fips, latitude, longitude, naics_code, pollutant_code, pollutant_type, site_name, state_abbr, state_fips, uom`.
- Filter column for state is `state_abbr` (not `state_code`). `pollutant_type` values seen: CAP, HAP, GHG, Other, CAP/HAP. CAP rows are in TON; HAP rows are in LB.
- Pagination `first:last` is positional; results appear sorted by `emissions` descending.
- Datacenters are NOT all under NAICS 518210: Equinix (73946), Digital Loudoun 3&4 (74126), Digital Loudoun II and QTS Richmond are coded 541513. County-level NOx queries were needed to catch them.
- Counties queried (both years, NOx): Loudoun 51107, Prince William 51153, Manassas city 51683, Mecklenburg 51117, Henrico 51087, Fairfax 51059, Chesterfield 51041, Spotsylvania 51177, Louisa 51109, Culpeper 51047, Caroline 51033.

## Full example record (quoted verbatim from the JSON response)
From `https://data.epa.gov/dmapservice/nei.vw_facility_summaries_2023/state_abbr/equals/VA/naics_code/equals/518210/pollutant_code/equals/NOX/1:500/JSON`:
```json
{
  "address": "21271 Smith Switch Rd",
  "address_postal_code": "20147",
  "city_name": "Ashburn",
  "code_description": "Computing Infrastructure Providers, Data Processing, Web Hosting, And Related Services",
  "county_fips": "51107",
  "county_name": "Loudoun",
  "description": "Nitrogen Oxides",
  "eis_facility_id": 21518811,
  "emissions": 10.503775,
  "facility_type": null,
  "fips": "51107",
  "latitude": 39.02533,
  "longitude": -77.46234,
  "naics_code": 518210,
  "pollutant_code": "NOX",
  "pollutant_type": "CAP",
  "site_name": "Amazon Data Services, Inc. IAD 50 IAD 60 IAD-71 IAD-78 IAD-79 IAD-80 (74049)",
  "state_abbr": "VA",
  "state_fips": "51",
  "uom": "TON"
}
```
Note the DEQ registration number "(74049)" embedded in `site_name` — DEQ appears to have started appending registration numbers to facility names for facilities first reported in 2023 (also seen: 73860, 74155, 73946, 74126, 52903, 74109, 73158, 73160, 74130, 74181).

## Which facilities appear (threshold) and lag
- Virginia point-source reporting rule located: 9VAC5-20-160.B (quoted from https://www.law.cornell.edu/regulations/virginia/9VAC5-20-160): "The owner of any stationary source emitting 25 tons per year or more of volatile organic compounds or nitrogen oxides" in "any emissions control area designated in 9VAC5-20-206" "shall submit an emissions statement to the board by April 15 of each year". This is the emission-statement rule; the broader DEQ inventory applicability (Title V / synthetic minor) text was not retrieved in this session, so the exact rule that puts a 1.4-ton-NOx datacenter (e.g. Timber, 52903) into the NEI is **not found** here. Observed: facilities with NOx as low as 1.36 tons appear in 2023 NEI, so the inclusion criterion is not the 25-ton emission-statement threshold alone.
- Observed coverage: 2020 NEI has only 3 Virginia datacenter-type point sources among the counties queried (Microsoft ECDC 17626111, DuPont Fabros 15410111, Digital Loudoun II 17632111). 2023 NEI has ~27 datacenter-type facilities statewide (23 under NAICS 518210 plus at least 4 under 541513). Most of the 60 permitted sites, including every Amazon site except 74049/73860/73853, are absent from both years.
- Lag: 2023 is the latest NEI year (triennial). Permits dated 2024-2026 in the input cannot have a 2023 inventory record for the permitted units.

## Limits
- Hours operated: NOT reported in this source for any facility. Fuel quantity: NOT reported.
- SCC / unit-level emissions: NOT in the facility-summary view. They exist in the process-level bulk ZIP (above) and in EIS (login), neither readable here.
- CO2/GHG: no GHG rows were returned for these datacenters (GHG rows in the view appear for EGUs only).
- Derivation warning: hours could be derived from tons NOx / (permitted lb/hr per unit × unit count) but that is an estimate, not a record; none was computed. If the parent wants it, label it "derived".
- Match caveats: three rows flagged UNCONFIRMED (73370 vs EIS 15410111; 73670 vs EIS 17632111; 74120 vs EIS 21512711). Two registrations (52973, 53198) share the street address 101 Herbert Drive with EIS 17626111 and are listed as not found with a note.
- QTS Richmond (4004611) 2023 values are rounded (17.9, 3.5, 1.1) unlike other facilities — quoted as given.
- NAICS/county NOx queries find only facilities reporting NOx; a facility reporting only other pollutants would be missed (unlikely for diesel generators).

## Files
- `/tmp/claude-0/-home-claude/bd7e6ebd-b0e6-53fb-80f0-fee6cd3e5e1b/scratchpad/metered/nei/va_generator_activity.csv` (205 rows: 161 data rows across 16 registrations, 44 not-found rows)
- `/tmp/claude-0/-home-claude/bd7e6ebd-b0e6-53fb-80f0-fee6cd3e5e1b/scratchpad/metered/nei/build_csv.py` (generator script; values are hand-transcribed from the fetched responses, each row carries its endpoint URL)
