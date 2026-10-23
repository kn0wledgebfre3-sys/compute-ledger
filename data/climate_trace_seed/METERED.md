# Metered load and actual generator use: what regulators and public utilities hold

Added 2026-10-23. Everything below is a figure a regulator or a public utility published; the ledger converts units and does nothing else. Files: `ireland_aer_metered.csv`, `va_nei_generator_emissions.csv`, `benchmarking_datacenters.csv`, `public_power_loads.csv`, `metered_summary.json`. Built by `pipeline/build_metered.py` from the transcriptions in `sites/metered/`, which carry the document URL on every row.

## Ireland: eleven licensed installations, metered, two years

Every installation licensed by the EPA under the industrial-emissions regime files an Annual Environmental Report (AER). Table 3 gives energy used in gigajoules by fuel (electricity, light fuel oil, natural gas, "renewable biomass", which for these sites is HVO); Table 5 gives water used in m3 by source. AERs for 2025 were loaded to the EPA's LEAP system in April 2026. Eleven of the 40 Irish sites in the ledger hold such a licence: nine Amazon installations, Microsoft DUB14/DUB15 (P1187-01) and Equinix DB5 (P1168-01). The other 29 hold GHG permits or planning permissions only, which carry no annual report.

| Year | Licences | Electricity (GWh) | Share of CSO national metered total | Amazon, nine licences (GWh) | Amazon share | Water (m3) | Generator fuel, diesel and HVO (GJ) | Natural gas (GJ) |
|---|---|---|---|---|---|---|---|---|
| 2024 | 11 | 3,585 | 51.4% of 6,973 | 3,389 | 48.6% | 187,328 | 38,184 | 510,550 |
| 2025 | 11 | 4,109 | 53.6% of 7,663 | 3,720 | 48.5% | 427,205 | 35,706 | 10,322 |

Largest installation: Amazon Clonshaugh (P1171-01), 3,673,332 GJ in 2025 = 1,020 GWh = 116 MW average. Amazon Cruiserath Road (P1182-01) 671 GWh. Microsoft DUB14/15 226 GWh (up 103% on 2024). Equinix DB5 162 GWh of grid electricity in 2025.

Generator use is small everywhere except one site. At Amazon Grange Castle South (P1170-01), 1,689 GJ of diesel and HVO in 2025 is about one hour of the 460.87 MWth permitted fleet at full rating; the 2025 range across the eight Amazon licences with a rated fleet is 0.6 to 6.4 fleet-hours. Equinix DB5's 2024 AER states that with full grid capacity delayed the site ran its generators "as prime from February 2024 to November 2024 to support the IT load", on gas: 510,550 GJ of natural gas against 303,804 GJ of electricity, about 850 hours of its 167.8 MWth fleet at full rating. No AER reports run hours directly.

What this does to the handover's Ireland estimate: the earlier method allocated the national metered total across sites in proportion to permitted standby capacity, as a bound. For eleven sites the per-site figure is now the regulator's, and the other half of the national total belongs to the 29 unlicensed sites together. The 2025 share of the national total (53.6%) is consistent with the earlier assumption that the largest 16 to 17 sites carry 50 to 70% of national load.

Reader traps, from the transcription notes: figures are per licensed installation, not per operator campus (Grange Castle South and Clonshaugh are each two licences; Microsoft P1187 is DUB14/15 only); P1181-01's 2024 report covers 8 August to 31 December only; several AERs' percentage-change columns contradict their own comment text, so absolute values are used; Microsoft's 2024 water total includes about 20,000 m3 of rainwater. Five of the 22 reports were re-read directly before publication and matched the transcription in every figure.

## Virginia: what the permitted generators emitted

EPA's National Emissions Inventory (triennial; 2023 is the latest) reports annual facility-wide emissions per pollutant, queryable without a login through Envirofacts (`data.epa.gov/dmapservice/nei.vw_facility_summaries_2023/...`). It does not report hours or fuel. Under NAICS 518210 Virginia has 23 facilities with NOx in 2023; four more datacenter facilities file under other codes. Together: 27 facilities, 393 tons of NOx. Twenty-one carry a DEQ registration number in the handover's permit list, several embedded in the NEI facility name (for example "Amazon Data Services, Inc. IAD 50 IAD 60 IAD-71 IAD-78 IAD-79 IAD-80 (74049)").

| Facility (NEI name) | County | NOx 2023 (t) | NOx 2020 (t) |
|---|---|---|---|
| Amazon Data Services IAD-132/133 | Prince William | 77.6 | |
| DuPont Fabros Tech, Ashburn Corporate Center | Loudoun | 47.7 | 19.5 |
| CyrusOne Shaw Road (74109) | Loudoun | 31.7 | |
| Microsoft East Coast Data Center, Boydton (21527) | Mecklenburg | 28.8 | 20.8 |
| CyrusOne Kincora (74114) | Loudoun | 27.1 | |
| Vantage Data Centers (74162) | Loudoun | 18.7 | |
| QTS Richmond (51232) | Henrico | 17.9 | |
| Digital Loudoun II | Loudoun | 17.1 | 6.9 |

Converting tons to hours needs each permit's NOx rate per unit, which the permits state in their emission tables and the ledger's extractor does not yet read; that is on the roadmap. Most of the 182 permitted facilities, including every permit issued from 2024 on, are absent from the 2023 inventory; the applicability rule that decides who reports was not established from the regulation text and is recorded as not found.

## Public utilities: cluster figures already published

| Utility | Figure | Document |
|---|---|---|
| Tennessee Valley Authority (federal) | Board memo, 7 Oct 2024: 150 MW of firm power approved for CTC Property LLC, "an xAI subsidiary"; "xAI was already operating at over 50 MW with a combination of limited MLGW power and xAI gas turbines" by August 2024 | TVA board reading room, resolution and memo |
| Memphis Light, Gas and Water | 5 May 2025 update: 8 MW from a pre-existing substation, 142 MW from a newly constructed one; 300 MW requested; Tulane Road "260MW to 1.1GW" | MLGW xAI Update PDF |
| Grant County PUD (Washington) | 2025: eight datacenter operators, about 280 average MW, 37% of a 757 aMW county load | PUD data-center FAQ page |
| Silicon Valley Power (Santa Clara) | 60% of power use and sales from 55 datacenters; 714 MW peak demand; requests to add 500+ MW | Utility director's NCPA presentation, 25 Sep 2025 |
| CPS Energy (San Antonio) | Board update, 4 Mar 2026: 335 MW contracted large load, 1,411 MW in process, 26,146 MW requested (59 projects); commercial is 56% of system sales 'with 9% from large load' | CPS Energy board session |
| Salt River Project (Arizona) | Datacenters 5.1% of SRP's summer 2025 peak | SRP data-center facts page |

Nothing public with a datacenter figure: OPPD, NPPD, Lincoln Electric System, Northern Wasco County PUD (a 2010 press figure only), Austin Energy, Seattle City Light, Tacoma Power, LADWP. Each is a public body under its state's records law; the request to file is named in `sites/metered/public_power_notes.md`.

Germany's datacenter register (EnEfG §13 and §14, published 14 August 2026) shows per-site PUE, connected load and renewable share for the 319 sites that chose to publish, out of roughly a thousand that should report; the portal refuses automated reading and needs a browser. Whether absolute consumption is shown per site is unconfirmed.

## City benchmarking laws: metered electricity for urban datacenters

Cities with building energy-disclosure ordinances publish each large building's metered energy by address, with its ENERGY STAR property type; "Data Center" is one type. `benchmarking_datacenters.csv` holds 218 building-years from eight portals (New York City Local Law 84, San Francisco, Seattle, Chicago, Washington DC, Philadelphia, Cambridge MA, Montgomery County MD), each row with the query that returned it. Largest, in kWh as published:

| Building | City | Type as filed | Electricity 2023 | Electricity 2024 | 2025 |
|---|---|---|---|---|---|
| 111 8th Avenue (Google; datacenter sub-use about 530,000 to 615,000 sq ft) | New York | Office, whole building | 148.1 GWh | 130.8 GWh | |
| 200 Paul Avenue (Digital Realty) | San Francisco | Data Center | 112.4 GWh | 111.4 GWh | 104.0 GWh |
| 60 Hudson Street (carrier hotel) | New York | Data Center | 87.2 GWh | 85.5 GWh | |
| 2001 6th Avenue, Westin Building Exchange | Seattle | Data Center | | 77.4 GWh | 73.5 GWh |
| 375 Pearl Street | New York | Office, whole building | 39.7 GWh | 41.3 GWh | |
| 365 Main Street | San Francisco | Data Center | 30.6 GWh | 29.0 GWh | 28.6 GWh |

Two rows (200 Paul Avenue 2024 and 60 Hudson Street 2023) were re-read directly from the portals and matched. Traps: most rows typed "Data Center" in New York and Philadelphia are telephone central offices; the carrier hotels (111 8th, 375 Pearl, 85 10th, 325 Hudson) are typed Office and report the whole building; Chicago and Philadelphia publish kBtu only, left unconverted; 350 East Cermak (Chicago) reports 1,114 million kBtu of electricity for 2022 and is absent from the 2023 file; New York's 2024 row for 60 Hudson carries the address "56 Hudson Street". No jurisdiction was found to exempt datacenters, but California's statewide disclosure (which would cover Santa Clara) is an xlsx download not read here, and Boston, Ontario, Denver, Portland, San Jose and Minneapolis need a browser or a download; Los Angeles publishes compliance status only.
