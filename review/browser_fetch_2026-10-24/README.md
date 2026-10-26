# Browser fetch, 24 October 2026

The documents on `review/BROWSER_FETCH_LIST.csv` are those that scripts could not reach: sites that refuse automated readers, search forms, viewers and dashboards. On 24 October a person opened them in a browser and saved what they found: 54 files, the texts of seven pages, and KenGen's annual report. Readers who had not built the ledger read them against the rules in `readers/RULES.md` and proposed changes (`readers/`). Each proposal was then checked against its document and applied, with the decisions noted below. Every row of the fetch list now has a status and a dated result.

## What was read and what changed

| Document | Entry or file | What changed |
|---|---|---|
| Later permits for 13 Virginia registrations | `va_permits_resolved.csv` | Five change the figures: 71804 (engines replaced, 8.595 MW), 73370 (new building ACC10, +18 units, +40.5 MW), 73670 (Title V renewal, 139 units, 274.675 MW), 73717 (EG5-EG7 added, 11.025 MW, medium confidence), 52629 (limits only). Three were the permits already read, with wrong dates recorded; one was a letter naming an unread permit; one download was the wrong file. Statewide: 182 permits, 13,990 units, 33,733 MW (was 13,973 and 33,693). `VIRGINIA.md`, last addendum. |
| EPA GHG permit IE-GHG628-01 | `irl-amazon-leixlip-kic-b1-p1222` (Ireland site list) | Confirms 14 x 7.73 MW + 2.5 MW + 2 x 0.36 MW = 111.44 MW; the site now cites the permit, and its figures enter the measurements table. |
| Amazon 10-Ks, FY2021 to FY2025 | `us-hyperscaler-server-lifespan-circularity` | Full-year effects of the server-life changes are in Amazon's own notes (2022 -USD 3.6 bn, 2024 -USD 3.2 bn, 2025 +USD 1.4 bn), so they move from a research firm's reading (claim) to record; adds the 2020 change and about USD 920 m of accelerated depreciation from retiring servers early in Q4 2024. |
| Google 2025 Environmental Report, with EY's FY2024 review | `alphabet-google-scope2-two-numbers` | 2024 Scope 2 (11,283,200 t location-based, 3,059,100 t market-based) and electricity are now records under limited assurance; the secondary source is dropped. |
| Microsoft 2026 Environmental Sustainability Report, endnote 2 | `microsoft-scope2-two-numbers` | The 100% counts long-term contracts (more than 90%) plus renewable power already in the grid; the fact sheet's 93.3% leaves out the grid share. Claim and gap say so. |
| California (AB 802) and Portland benchmarking files; Ontario 2022 | `us-city-benchmarking-datacenter-metered-electricity`, `sites/metered/benchmarking_transcribed.csv` | 178 building-years added (California 169, Portland 9). Left out: San Francisco rows (already in the city's data) and offices whose data-centre use is under 40% of their floor area; one California value about 1,000 times its next-year value is not ingested. Ontario publishes no addresses, so no row. `sites/metered/benchmarking_notes.md`, last section. |
| Hertsmere officer report, decision notice, Section 106 agreement | `uk-south-mimms-dc01uk` | Conditions read (10% biodiversity net gain, generators for outages and testing only, cooling with no harm to local water, PUE reporting); the S106 secures £2,000,000 for buses and £38,500 for skills; no job number is secured; the 10,900 indirect jobs in the council's release appear in none of the documents (the applicant's statement gives 12,741). |
| City of Cape Town tribunal resolution | `za-capetown-580mw-objection` | The approval of 14 Jul 2026 and its one added condition (minimise drinking-water use) now rest on the City's own record. |
| CONAGUA water-rights register, title 855979 | `mx-qro-queretaro-colon-water-grid` | Microsoft 6394 México, 25,000 m³/yr of groundwater, registered 23 Oct 2023: confirmed in the register. |
| Finnish ministry release and annex, 2 Jul 2021 | `fi-espoo-kirkkonummi-microsoft-fortum-heat` | First record for the entry: EUR 8,234,000 of state aid to Fortum for data-centre heat recovery, about 60 MW of heat pumps. |
| EU data-centre dashboard export (reporting period 2025) | `eu-eed-datacentre-reporting-2024-period` | 773 data centres in 11 countries, 20.7 TWh, 4.4 GW, PUE 1.27, read directly; the press figures describe another view. |
| Egyptian ministry statement | `eg-national-dc-pipeline-grid` | The Africa Data Centres Egypt terms (20 MW in three years, 200 MW target) are the government's statement; no site, power or water terms. |
| Humain CEO's post on X | `sa-humain-pif-datacenters` | The post DCD linked gives none of the figures attributed to it. |
| KenGen annual report, year to June 2025 | both Kenya entries | The Green Energy Park was gazetted as a special economic zone; the report does not mention the data centre, Microsoft or G42. |
| Nevada docket filings (the orders were not obtained) | `us-nv-google-nv-energy-clean-transition-tariff` | Order dates (11 Mar and 14 May 2025) and the filed contract terms (115 MW, 15 years, operation from 2030) added; the orders are still to be read. |
| AESO's proposed process and September 2025 update | `ca-ab-aeso-large-load-byog-greenlight` | 1600 MW bridging cap and the gas-only first intake from AESO's own proposal; a press phrase not in the document removed. |
| NERC 2025 Q4 report | `ng-lagos-diesel-gas-dependence` | None of the quarter's 11 captive generation permits went to a Lagos data-centre operator. |
| Thames Water annual report 2024-25 | `uk-thames-affinity-water-datacentres` | No data-centre passage in it; the figures stay press-sourced. |
| Global E-waste Monitor 2024 | `global-gem-2024-ewaste` | Every figure confirmed as printed, with pages; verified. |
| Primer Tribunal Ambiental ruling R-21-2019 | `cl-lithium-atacama-sqm-sma` | The ruling concerns a different SQM programme (Pampa Hermosa), not the Atacama one the press linked it to; the entry now says so. |
| Viksit Gujarat Data Center Policy (2026-29) | `in-gujarat-jamnagar-policy` | The policy's terms read from the resolution itself; it does not mention Jamnagar. |
| Argentina RIGI site | `ar-stargate-argentina-rigi` | 26 approved and 22 projects under evaluation; no Stargate or data-centre project shown. |
| Taipower sustainability reports 2022, 2024, 2025 | `tw-taipower-north-5mw-cap` | They do not mention the 5 MW rule; the 2025 report's "Power Couple" statements added as Taipower's claim. |

## After this round

202 entries: 73 verified, 104 partial, 25 not found; confidence 73 high, 107 medium, 22 low. 718 distinct linked documents. 2,984 figures (663 of them claims). 853 sites. Twenty-two documents are still to fetch (status `not_obtained` or `open` on the fetch list), among them the El Paso proposal for decision, the Equinix, Digital Realty and Oracle reports and the two Nevada orders; sixteen are blocked to a browser and need records requests.

## Independent check

A reader who had not done the work re-read the applied changes against the documents: the Virginia permits that changed, the entries changed from documents, a random sample of 12 of the benchmarking rows added, and the outward text. No figure was found wrong. Six inconsistencies were corrected: an AESO sentence that had lost its press tag; a proposed AESO cap filed as approved capacity; the basis of the Finnish ministry's expected coal reduction; two Hertsmere figures entered twice (from the council's release and from the signed documents; the release rows were removed); and the ACC10 address for Virginia registration 73370, now in the figure's notes. Microsoft's FY25 circularity figures (92%, seven Circular Centers) from the 2026 report were added beside the FY24 ones. Not changed: Cape Town's 34% is Daily Maverick's own figure; buildings that their filers typed Data Center keep that type, whatever their energy intensity.

