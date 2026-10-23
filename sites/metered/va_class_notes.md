# Virginia data center consumption by class — research notes (2026-10-23)

Companion to `va_datacenter_class_sales.csv` (63 rows). Shell had no internet (curl to pjm.com: CONNECT 403); everything was read through WebFetch's text layer, so chart-only values are reported as "not found" rather than read off images.

## Headline result

**No regulator-side document read today publishes Dominion's annual data center sales in GWh/MWh.** Dominion's SCC and PJM filings publish data center *demand* (billing MW and coincident MW), customer counts, campus connections and contracted capacity, but describe energy only as "modeled from billing demand and load factor". The only public share-of-sales numbers for Dominion are company statements (10-K: 28% of Virginia Power sales in 2025, 26% in 2024). For NOVEC, the co-op's own PJM submissions give data center share of energy (64% Oct-23–Sep-24; 75% Aug-25–Jul-26) and total 2025 sales of 14.6 TWh, but no data-center GWh line.

Ledger rule applied: nothing derived (e.g. 28% x total sales, or peak MW x load factor) was written as a figure.

## Documents read (with what they yielded)

| Document | URL | Yield |
|---|---|---|
| Dominion 2025 Update to the 2024 IRP, PUR-2025-00184, filed 15 Oct 2025 (Dominion-hosted copy) | cdn-dominionenergy-prd-001.azureedge.net/.../2025-integrated-resource-plan-update.pdf | Ch. 2: campus connections (8 in 2025 / 561 MW; 15 in 2024 / 977 MW), Figure 2.1.15 contract table (firm 16,913 MW; ELOA 30,132 MW; total 47,045 MW at end-July 2025), DOM LSE total energy forecast (Fig 2.1.9). No data-center GWh or MW series. |
| Dominion SCC-Directed 2024 IRP Supplement, PUR-2024-00184, 15 Nov 2024 | scc.virginia.gov/docketsearch/DOCS/82l101!.PDF | Method only ("froze the volume of energy attributable to data centers at the forecasted 2024 levels"); Figure 2.1.1 'Comparison of Energy Forecast – DOM LSE' values are image-only. |
| SCC Order, PUR-2024-00184, 11 Oct 2024 (directing the supplement) | scc.virginia.gov/docketsearch/DOCS/81xf01!.PDF | No data center figures. |
| PEC (Abbott) direct testimony, PUR-2025-00058, 16 Jul 2025 | pecva.org/.../PUR-2025-00058-PEC-Direct-Testimony-7.16.25.pdf | Quotes Dominion witness Blackwell's table (2013: 29 customers / 462 MW; 2024: 51 customers / 3,583 MW), VCFUR interrogatory 02-03 (131 data center customers to GS-5, contract demand 4,664.9 MW, measured peak 2,782.2 MW), load factor 92–93%, and that data centers sit in GS-3 and GS-4. |
| SCC Status Report on the Virginia Electric Utility Regulation Act, 31 Oct 2025 (RD716) | rga.lis.virginia.gov/Published/2025/RD716/PDF | GS-5 / "high load" definition (>=25 MW, >=75% load factor). No data center load or sales figure. |
| Dominion 2025 20-Year Data Center Forecast, PJM LAS 16 Sep 2025 | pjm.com/.../20250916-item-04ai---dominion-data-center-large-load-request.pdf | Billing demand series 2013A–2030P (2024A 3,584 MW; 2025F 4,149 MW); 54 customers; ELOA 30,132 MW. |
| Dominion 2024 20-Year Data Center Forecast, PJM LAS 25 Oct 2024 | pjm.com/.../20241025-item-03ai---dominion-data-center-large-load-request.ashx | Billing demand 2013A–2023A (2022A 2,767; 2023A 3,183), 2024F 3,562; 53 customers; SELOA 7,570 MW. |
| Dominion LSE 20-Year Data Center Forecast, PJM LAS 29 Sep 2026 | pjm.com/.../20260929-item-5ai---dominion_energy.pdf | 'Historical Data Center Demand' chart: billing 2024 3,636 / 2025 4,237 / 2026F 4,838 MW; coincident 3,410 / 3,999 / 4,559 MW; "4.8 GW" billing peak Aug 2026; 55 companies; ~500 metered accounts; ~54 GW under contract; DOMZONE demand 2027 5,075 MW … 2047 19,466 MW. No GWh. |
| Dominion letter to PJM Load Analysis Team, 6 Jan 2026 (Manual 19 Att. B documentation) | pjm.com/.../dominion-documentation.pdf | "2025 coincident peak of 4 GW"; 47 GW contracts (9.8 ESA + 7.1 CLOA + 30.1 ELOA); 16.6 GW demand by 2046; year table values are image-only. |
| PJM 2026 Long-Term Load Forecast Report | pjm.com/.../2026-load-report.pdf | Text layer is 34,520 chars (narrative only). Only DOM line: "DOM Growth in data center load and a voltage optimization program". Tables B-9/B-9b live in 2026-load-report-tables.xlsx (binary; unreadable here). |
| PJM 2025 Long-Term Load Forecast Report | pjm.com/.../2025-load-report.pdf | Same structure, 35,798 chars; no table values. |
| PJM Load Forecast Supplement 2026 | pjm.com/.../load-forecast-supplement-2026.pdf | Dominion section pp. 34–37: firm/non-firm breakdown and history+forecast charts, values image-only. |
| PJM 2026 Load Forecast (Data Center) Accuracy Report | pjm.com/.../2026-load-forecast-accuracy-report.pdf | DOM pages are charts; REC: "This zone does not have historical large load data." DOM = 64.3% of July-2025 actual large-load distribution (share, not MW). |
| PJM LAS 23 Jan 2026 LTLF presentation; PJM RBPW 25 Feb 2026 presentation; PJM LAS 9 Dec 2024 preliminary forecast | pjm.com | Zone lists only; no DOM MW values in text. |
| NOVEC Data Center Load Forecast, PJM LAS 25 Oct 2024 | pjm.com/.../20241025-item-03b---novec-large-load-request.ashx | 50+ data centers, ~1,000 MW; Energy 64% (Oct 23–Sep 24); summer peak 51%; count/CP table 2020–2029. |
| NOVEC 2026 PJM forecast documentation (Aug 2025 forecast) | pjm.com/.../novec-documentation.pdf | Actual 2025 CP 1,387 MW; forecast to 13,380 MW (2046); ~17,000 MW totalized capacity. |
| NOVEC Large Load Adjustment Request, PJM LAS 29 Sep 2026 | pjm.com/.../20260929-item-5b---novec.pdf | 88 buildings, ~1,750 MW; 75% of energy Aug 25–Jul 26; 64% of July-2026 peak; total 2025 sales 14.6 TWh; table 2022A–2047. |
| REC 2026 PJM forecast documentation | pjm.com/.../rec-documentation.pdf | Firm 4.5 GW / non-firm 13.9 GW; CP forecast 2026 418 MW → 2046 8,228 MW; no actuals. |
| REC 2026 Large Load Adjustment, PJM LAS 29 Sep 2026 | pjm.com/.../20260929-item-5c---rappahannock.pdf | Requested capacity 7,423 (2024) / 17,367 (2025) / 22,426 MW (2026); demand 2027 331 MW → 2047 8,341 MW. |
| ODEC 2027 Large Load Adjustments, PJM LAS 29 Sep 2026 | pjm.com/.../20260929-item-5d---odec.pdf | 2027 demand submission 1,851 MW; 16,544 MW tracked. |
| Dominion Energy 10-K FY2025 (SEC) and ARS | sec.gov | "Data centers represent 28% and 26% of Virginia Power's electricity sales for the years ended December 31, 2025 and 2024, respectively." Total GWh not in fetched portion. |
| Dominion IRP stakeholder Q&A page | devirp.dominionenergy.com | "approximately 85%" of 20-year load-forecast increase is data centers. |
| Virginia Mercury 25 Nov 2025 and 21 Jul 2025; SELC 25 Nov 2025 press release | — | Press: "Dominion serves about 450 data centers in Virginia"; links to the two SCC orders. |
| 2023 IRP intervenor testimonies (Levi/DCC, Glick/Sierra Club, Abbott/PEC), PUR-2023-00066 | scc.virginia.gov/docketsearch/DOCS/7tyy01!, 7ty_01!, 7%h101!, 7ty%2501! | No data center sales/MW tables. |

## Could not be reached

- SCC Final Order, PUR-2025-00058 (25 Nov 2025): `https://www.scc.virginia.gov/docketsearch/DOCS/89g501!.PDF` — WebFetch returned `robots_disallowed` on both www and non-www hosts and with `%21` encoding.
- SCC Final Order, PUR-2024-00184 (15 Jul 2025): `https://www.scc.virginia.gov/docketsearch/DOCS/86qq01!.PDF` — not attempted after the same-host failures; press says it does not mention data centers.
- Data Center Coalition proposal in PUR-2025-00058: `scc.virginia.gov/docketsearch/DOCS/87_%4001!.PDF` — robots_disallowed.
- SCC news release on the biennial review order — robots_disallowed.
- Dominion's own biennial-review testimony (Blackwell Direct, Baine Direct) and schedules with GS-4 kWh (PUR-2025-00058) — not located outside scc.virginia.gov; the SCC docket search is JavaScript-driven and could not be queried.
- PJM table workbooks (2026-load-report-tables.xlsx; total-load-adjustments-breakdown.xlsx; 2026-load-adjustment-breakdown-for-capacity-obligations.xlsx) — binary, WebFetch cannot parse.
- NOVEC and REC annual reports — not surfaced by search; co-op figures come from their PJM submissions instead.
- Oddity: some scc.virginia.gov/docketsearch/DOCS/ PDFs fetched fine (82l101!, 81xf01!, 7tyy01!, 7ty_01!, 7%h101!, 7ty%2501!) while others were refused; cause unknown.

## Definitions used

- **Dominion "data center customer"** (PJM decks, Jan-2026 letter): a data center *company* with metered accounts; "55 discreet data center companies connected" and "Approximately 500 data center metered accounts" (Sep 2026). The Jan-2026 letter models the 7 largest companies individually and "approximately 45" others as an eighth segment. Dominion "has collected detailed metering information on its data center customers since 2013" — i.e. the series is metered data-center load, aggregated by Dominion's own customer tagging, not a tariff class.
- **"Billing demand" vs "coincident demand"**: billing demand (MW) is the sum of customer billing demands (non-coincident); the Sep-2026 deck also gives coincident demand (~94% of billing). The Jan-2026 letter's "2025 coincident peak of 4 GW" matches the 3,999 MW coincident value.
- **Restatement**: 2024 actual billing demand is 3,584 MW in the Sep-2025 deck and 3,583 MW in Blackwell's biennial-review table (per PEC), but 3,636 MW in the Sep-2026 deck. Both are recorded; the ledger should cite the vintage.
- **Campus connections** (IRP): "data center connections (i.e., data center campuses)" — 15 in 2024 (977 MW ultimate), 8 expected in 2025 (561 MW ultimate). Count of *campuses*, not buildings or accounts.
- **Contract stages**: ELOA (engineering, $250k deposit, non-firm) → CLOA (firm, reserves capacity) → ESA (service agreement, meter set). "Firm" = ESA + CLOA. 47,045 MW total at end-July 2025 (IRP) = the "47 GW" in the PJM letter; ~54 GW at July 2026.
- **GS-4**: Dominion's large general service class (>= ~5 MW historically) — it is **not** a data-center-only class. PEC testimony (citing Baine Direct) says data centers are "subsumed into Dominion's GS-3 and GS-4 rate classes", and the GS-5 migration list has "131 data center customers and 8 non-data center customers". No GS-4 kWh value was found in any readable document.
- **GS-5 / high load** (SCC Status Report p. 31; biennial review order): customers with measured or contracted demand >= 25 MW and load factor >= 75%; applies to "most of its data center customers" but is defined by size/load factor, not by industry.
- **131 vs 51–55 customers**: the biennial-review count (131) is at account/premise level for GS-5 eligibility; the PJM-deck count (51–55) is data center companies. Press "about 450 data centers" and Dominion "~500 metered accounts" are a third unit (sites/accounts).
- **NOVEC**: counts are "data center buildings" (88 in 2026) with a dedicated data center rate classification since 1999; "energy share" is the data center class share of NOVEC retail kWh for a trailing 12-month window.
- **REC**: no historical data center load (PJM accuracy report); all REC figures are requested/contracted capacity and forecasts.
- **PJM DOM zone**: the DOM zone includes Dominion LSE plus NOVEC, ODEC/REC and others; PJM's "data center adjustment" for DOM is the sum of these LSE submissions, firm plus probability-weighted non-firm. Values by year are in Tables B-9/B-9b (xlsx), not read.

## Suggested next steps (not done, outside budget/tooling)

1. Obtain the Excel tables for the PJM 2025 and 2026 reports (Table B-9/B-9b, DOM rows) with a tool that can read xlsx.
2. Pull Dominion's PUR-2025-00058 Blackwell Direct (table p. 5) and the class cost-of-service schedules (GS-3/GS-4 kWh, test year 2024) directly from the SCC docket with a browser.
3. FERC Form 1 (Virginia Electric and Power Co.) p. 304 "Sales of electricity by rate schedule" gives GS-4 MWh by year — a regulator record that would give the class total if not the data-center line.
