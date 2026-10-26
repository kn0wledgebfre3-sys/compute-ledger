# Singapore, begun from allocation records, 2026-10-24

First run for Singapore under `JURISDICTION_TEMPLATE.md`, parts 1 to 4. Singapore has no datacenter permit, licence or tax register comparable to Virginia's DEQ list or Texas's Comptroller register. The government records that name datacenters are the capacity allocation calls run by IMDA and EDB. This run read those calls, the Green Data Centre Roadmap, parliamentary replies, NEA's Energy Conservation Act pages and JTC's Jurong Island page. Every figure has a URL fetched on 2026-10-24.

## What was read

| Document | Publisher, date | What it gives |
|---|---|---|
| Launch of pilot DC-CFA | IMDA and EDB, 2022-07-20 | Pause in DC growth announced to industry in 2019. No MW for the pilot. |
| Four proposals selected, pilot DC-CFA (IMDA copy and EDB copy) | IMDA and EDB, 2023-07-14 (date from EDB copy) | about 80 MW provisionally awarded to AirTrunk-ByteDance, Equinix, GDS and Microsoft; more than 20 proposals; Green Mark DC Platinum. No per-awardee MW, no sites. |
| Launch of DC-CFA2 (IMDA factsheet; EDB PDF; IMDA submission page) | IMDA and EDB, 2025-12-01 | At least 200MW to be made available; PUE 1.25 at 100% IT load or better; at least 50% eligible green energy; Green Mark for DCs 2024 Platinum; SS 715:2025 IT equipment. Registration of interest closed 2025-12-05. No location. |
| Fact sheet, four proposals selected, DC-CFA2 | EDB and IMDA, 2026-08-21 | 200 MW provisionally allocated, 50MW each to Digital Realty, Equinix, Keppel Data Centres, ST Telemedia Global Data Centres; Jurong Island; more than 50% green energy; more than 20 proposals. No parcels. |
| About the Green Data Centre Roadmap | IMDA, undated page (roadmap factsheet dated 2024-05-30) | Total capacity exceeding 1.4 gigawatts; at least 300 MW more in the near term; PUE 1.3 or lower target. |
| MCI written reply on DC carbon emissions | MCI, 2021-07-27 | DC electricity: 2.75 TWh (about 5.3%) in 2019; 3.40 TWh (about 7%) in 2020. |
| MDDI reply on limits to total DC capacity | MDDI, 2026-03-03 | No pre-determined upper limit to DC capacity; capacity allocated mainly through the calls. No figures. |
| Jurong Island to host largest green DC park | Straits Times article republished on JTC's site, 2025-10-27 | 20ha reserved for the park; up to 700MW; more than 70 data centres in Singapore. Press report. |
| NEA registration of companies (Energy Conservation Act) | NEA, undated | 54 TJ threshold; three industrial sectors; data centres not named. |
| EMA Singapore Energy Statistics 2026, chapter 3 | EMA | The page text has no DC or information-and-communications figure. The chart and downloads were not read. |
| BCA-IDA Green Mark for Data Centres fact sheet | IMDA (IDA), 2012 | Describes the scheme. Lists no datacenters. |

## Counts

| | |
|---|---|
| Site rows (`sites.csv`) | **9**: 4 pilot awardees, 4 DC-CFA2 awardees, 1 JTC park |
| with coordinates | **0**. No document read gives a coordinate or a geocodable site address. |
| with a locality | 5 (Jurong Island) |
| with a capacity from a government allocation | **4** (50 MW each, DC-CFA2) |
| with capacity from a press report | 1 (JTC park, up to 700 MW of power capacity, not an allocation) |
| pilot awardees with per-site MW | 0 (the award gives a combined "about 80 MW") |
| Figures (`figures.csv`) | **23**, of which 17 re-read verbatim (`second_read` yes) |
| New registry entries (now in `registry/asia_pacific.json`) | 4 |
| Updates to existing entries (applied in `registry/asia_pacific.json`) | 2 |

## Part 1: site list

The allocation records name awardees, not facilities. The pilot award (2023) names four companies and no locations. The DC-CFA2 award (2026) places all four allocations on Jurong Island and says JTC is developing a low-carbon DC park there, but gives no parcel. The site ids for the pilot rows (`sgp-<operator>-dccfa-pilot`) refer to an allocation whose site is unknown. They should be joined to a facility once a record names one. The backlog rows `sg-imda-dc-cfa-2023` and `sg-edb-dc-cfa2-2026` in `datacenters_register_backlog_unlocated.csv` stay as they are; the nine rows here split them by awardee.

Searches for other planning records:
- **JTC datacenter parks** in Jurong West, Loyang, Tuas and Sembawang: searches found only the Jurong Island park.
- **URA**: a search for URA Master Plan or circular records naming datacenter sites returned no URA document.
- **Kim Chuan, Tai Seng**: no government record read names them as datacenter sites. ST Telemedia's Loyang facility appears only in a photo caption of a Straits Times article republished on EDB's site. That is not recorded as a site.
- **NEA's Energy Conservation Act**: registration covers manufacturing, utilities and water/waste corporations at 54 TJ a year or more. The page does not mention data centres, and no published list of registered corporations was found.
- **BCA's Green Mark for Data Centres**: the 2012 scheme fact sheet lists no certified datacenters. A directory of certified buildings was not found.

Result: the more than 70 existing datacenters (a press figure) and their 1.4 GW have no public government register that this run could find.

## Part 2: capacity per site

The only per-site capacity in a government record is the DC-CFA2 allocation: 50 MW to each of four operators, provisional (fact sheet, 2026-08-21). The vocabulary metric is `approved_capacity` with basis `regulator_decision`. The pilot's about 80 MW is a combined figure for four awardees and is not split. No planning approval, grid connection or generator figure was found for any Singapore site.

## Part 3: totals the sites must respect

| Total | Value | Basis | Period |
|---|---|---|---|
| National DC capacity (IMDA roadmap) | exceeding 1.4 GW; IT or facility power not stated | government_document | undated (roadmap 2024-05-30) |
| DC electricity (MCI reply) | 2.75 TWh, about 5.3% of national | official_statistic | 2019 |
| DC electricity (MCI reply) | 3.40 TWh, about 7% of national | official_statistic | 2020 |
| Near-term addition (IMDA roadmap) | at least 300 MW | government_document, target | none given |
| Cap (MDDI reply) | none: "does not have a pre-determined upper limit" | government_document | 2026-03-03 |

Tests (derived by the ledger; not in `figures.csv`):
- **Allocations against the target.** About 80 MW plus 200 MW is about 280 MW provisionally allocated since 2022, against the roadmap's "at least 300 MW". DC-CFA2's launch said "potentially more" through green energy pathways.
- **Electricity against capacity.** 2.75 TWh over 8,760 hours is an average load of about 314 MW in 2019. 3.40 TWh over 8,784 hours is about 387 MW in 2020. Both are below the 1.4 GW stated later. The figures are for different years, and the 1.4 GW is not defined as IT or facility capacity, so no utilisation ratio is computed.
- **No total for 2021 to 2025 was read.** MTI's January 2025 written reply on DC electricity consumption is the likely source. It redirects to meti.gov.sg, which could not be fetched (see below).

## Part 4: records law and requests

Singapore has no freedom-of-information law of general application. There is no statute giving the public a right to obtain government documents on request. What is public comes from agency publications, parliamentary questions and answers, and statistics releases. The requests below are therefore letters to the agency, which it may answer or decline. Parliamentary questions, asked by a Member of Parliament, have been the channel that produced the 2019 and 2020 electricity figures and the 2026 statement that there is no capacity limit.

| Addressee | Document or data to ask for |
|---|---|
| IMDA (with EDB) | For each pilot DC-CFA award (2023): the MW allocated, site address or land lot, and operational status. For each DC-CFA2 award: the Jurong Island lot. The definition (IT or facility) and as-of date of the "exceeding 1.4 gigawatts" figure, and its breakdown by facility. Any PUE data collected under the Green DC Roadmap. |
| EMA | Annual electricity consumption of data centres, 2019 to 2025, and its definition (sub-sector or SSIC code). The source of the 2019 and 2020 figures in MCI's 2021 reply. Peak demand of data centres. Grid connection capacity granted to data centres (with SP Group as grid owner). |
| NEA | Whether any data centre is a registered corporation under the Energy Conservation Act, and the aggregate energy use and emissions reported by data centres. Whether the Act's registration scope will cover data centres. |
| JTC | Parcels, lot numbers and area of the Jurong Island DC park; JTC's own document for the 20ha and up to 700MW figures; tender or allocation documents for the park. |
| URA | Planning permissions (written permissions) granted for data centre developments, by address and gross floor area. |
| BCA | List of buildings certified under Green Mark for Data Centres, with address and rating. |

### Needs a browser (could not be fetched by the tool)

| URL | Why | What it should contain |
|---|---|---|
| https://www.meti.gov.sg/newsroom/written-reply-to-pq-on-electricity-consumption-when-data-centres--capacities-rise-by-a-third-and-impact-on-singapore-s-greenhouse-emissions/ | fetch permission not granted (redirect from mti.gov.sg) | MTI's January 2025 reply on DC electricity if capacity rises by a third; likely recent DC electricity share |
| https://www.meti.gov.sg/newsroom/written-reply-to-pq-on-data-centres/ | redirect from mti.gov.sg, not followed | an MTI written reply on data centres |
| https://mddi.gov.sg/files/Speeches 2024/1__Factsheet_IMDA_Green_DC_Roadmap.pdf | site returned a client error (URL contains spaces) | the roadmap factsheet with its figures and date |
| EDB PDFs of the pilot launch (2022) and pilot award (2023) | URL longer than the proxy accepts | the same releases as the IMDA pages, possibly with dates and footnotes |
| https://ema.gov.sg/resources/singapore-energy-statistics/chapter3 (Tabular Data / Tidy Data downloads) | values are in an interactive chart | electricity consumption by sub-sector, including information and communications |

## Not done (part 5)

Supply and emissions were not attempted. No document read names the plant or supply arrangement serving any Singapore datacenter. The JTC-hosted article mentions a hydrogen-ready gas plant and an ammonia power project on Jurong Island, but it does not tie either to the DC park.

## Files

- `sites.csv`: 9 rows, columns as `sites/topics/crypto/sites.csv`.
- `figures.csv`: 23 rows, columns as `sites/topics/crypto/figures.csv`. Every `value_as_published` occurs in its `quoted_line` and in its entry's text.
- The four new entries (`sg-mci-dc-electricity-2019-2020`, `sg-mddi-no-dc-capacity-limit-2026`, `sg-jtc-jurong-island-dc-park`, `sg-nea-eca-registration-scope`) and the two updated ones (`sg-imda-moratorium-capacity`, `sg-imda-green-dc-roadmap-pue`) are in `registry/asia_pacific.json`; each entry's `verification_note` records its second reading.
