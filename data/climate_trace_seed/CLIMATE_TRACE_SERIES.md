# Climate TRACE series, release 5.11.0, USA electricity generation, monthly, Jan 2025 to Jul 2026

Source: Climate TRACE download builder, pulled 21 Oct 2026 (release 5.11.0; series Jan 2025 to Jul 2026), emissions (CO2e 100yr), individual sources, USA, Power sector; 48,032 electricity-generation rows for 2,528 assets. Their per-field confidence ratings are columns in the export and are carried through.

## Matched plants, monthly (climate_trace_matched_plants_monthly.csv)

Six assets the ledger's regulatory records name, with Climate TRACE's own monthly estimate and confidence:

| Plant | 2025 total tCO2e | Their confidence | What the record ties it to |
|---|---|---|---|
| Chesterfield, VA | 922,444 | high | SCC order PUR-2025-00037: 944 MW gas peaker approved here, citing datacenter load; COD 2029 |
| Elm Road Generating Station, WI | 6,952,400 | high | PSC final decision 6630-CE-317 (July 2025): 1,100 MW simple-cycle gas approved directly west of this station, 'necessary to satisfy the significant probable future requirements of one customer, the Very Large Customer', identified in the decision as Microsoft's Mount Pleasant data center |
| TVA Southaven Combined Cycle, MS | 2,173,970 | high | 4 km from xAI's permitted turbine plant of about 1,240 MW (MDEQ permit 0680-00119, March 2026) |
| Allen, TN | 1,376,900 | medium | 1.3 km from xAI Colossus (on-site gas turbines from mid-2024; county permit for 247 MW, July 2025) |
| Homer City, PA | 0 | low | Coal plant demolished; 4,678 MW gas campus permitted (PA DEP 2025), not built |
| Moxie Freedom, PA | 1,235,680 | medium | Not a match: Climate TRACE lists no CO2e for the Susquehanna nuclear plant (correct); this is the nearest unrelated gas asset, shown so the non-match is visible |

Chesterfield's series drops to near zero in October and November 2025 (1,349 and 3,715 tCO2e) and returns in December, consistent with a seasonal outage; that series is the baseline against which a new peaker's arrival is visible in their data.

## Virginia sites and their nearest estimated plant (virginia_nearest_generation.csv)

For each of the 102 Virginia permit sites geocoded to the permit's own site address, the nearest Climate TRACE electricity asset within 15 km (80 found), with its 2025 estimate, fuel and confidence. Context for siting only: a datacenter's electricity comes from the grid, not the plant next door. An earlier bounding-box aggregate labelled "Virginia" was withdrawn after review because the box contained Ohio and West Virginia coal plants. On 2026-10-22, thirteen rows were removed because the geocoder had placed the permittee's mailing address, not the site, and eleven because the geocoder matched only the street, not the address (`va_geocodes.csv` holds every geocode with the address it was given).

## Limits

Confidence is Climate TRACE's own per-asset rating. Monthly values are their estimates, not metered.
