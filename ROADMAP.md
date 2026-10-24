# Roadmap

Written 2026-10-23 and reorganised the same evening. The Climate TRACE emails go out on Monday 26 October. From here the work is organised by what each item is waiting for: data the ledger can mine now (section 4), a person with a browser, a records request or a setting (section 5), or time (section 6). `review/INTAKE.csv` is the working list of every awaited dataset, with its status and the file it lands in; this file says why and in what order. Every item names the public record it rests on and an estimate in working days.

The rule does not change: a company's statement enters as a claim, a regulator's, court's, grid operator's, statistical office's, auditor's or customs authority's document enters as a record, and nothing enters without a URL.

## 0. Structure and automation (done 2026-10-23)

- ~~One table for every figure~~: `data/climate_trace_seed/measurements.csv`, built by `pipeline/build_measurements.py` from the registry text and every transcription, with `site_register.csv` and `entity_register.csv`; one vocabulary (`pipeline/measurement_vocab.json`) and one conversion module (`pipeline/units.py`).
- ~~Validation in CI~~: `pipeline/validate_measurements.py` and the rebuild-identity checks in `.github/workflows/validate.yml`; `ci_local.sh` runs the same checks locally.
- ~~Scheduled pulls and watchers~~: `.github/workflows/weekly-pulls.yml` with `scrapers/pull_nei.py`, `pull_ie_aer.py`, `pull_benchmarking.py`, `watch_pages.py`; every result arrives as a pull request for review. First live run: the first Monday after the push (needs the Actions setting in `scrapers/README.md`).
- ~~Growth structure~~: `CONTRIBUTING.md` (how a figure enters, the two-reading rule, id and correction rules), `JURISDICTION_TEMPLATE.md`, status columns on `review/BROWSER_FETCH_LIST.csv`.
- ~~Found by the extraction~~ (fixed 2026-10-23): `review/registry_source_gaps.csv` (75 figures whose document was not among their entry's sources; the PJM market monitor entry's "+262.3%" against its own figures).
- ~~Independent check of the table~~ (2026-10-23): 56 figures drawn at random and fetched by a reviewer who had not seen the build; 53 found as stated. Corrections, applied wherever the pattern occurred, in `data/climate_trace_seed/review_5_measurements_check.md`; the reviewer's files in `review/measurements_check_2026-10-23/`. Repeat on a fresh sample whenever a new feed is added.
- ~~The chain as a table~~ (2026-10-23): `sites/chain/edges.csv`, one row per link the documents state (supplies power to, leases site to, contracts power from, refines for...), checked by `pipeline/build_chain.py` in CI; `data/chain/summary.json` lists the legs with no link yet. 14 links so far.
- ~~Intake for what is still missing~~ (2026-10-23): ready-to-fill folders for refiners, fabs, chip trade and hardware life (`sites/topics/*/README.md` says which record feeds each); `sites/metered/va_permit_unit_rates.csv` for generator hours; trackers `review/INTAKE.csv`, `review/RECORDS_REQUESTS.csv` and `review/JURISDICTIONS.csv`.
- Still to automate: EIA (needs the `EIA_API_KEY` secret); the Texas Comptroller register (no stable URL yet); Germany's register and the SCC docket (refuse automated reading; browser).

## 1. Done in the round of 23 October

- ~~Reporting layer steps 4 and 5~~, as far as the documents allow: Alphabet's assured 2025 electricity split by instrument (the only one of the seven); Meta's >99% grid share; Microsoft, Amazon and Oracle publish no split. No registry record names any of the seven as beneficiary of a credit retirement; the companies' California AB 1305 disclosures give purchased volumes (Microsoft 605,354 t for FY23, Meta 368,050 t for 2020–2023) that cannot be matched to a retirement. Entries `scope2-renewable-claims-by-instrument`, `carbon-credits-retired-by-company-disclosures`.
- ~~Geocoding, US Census run~~: 23 Virginia permits placed on their site address (125 of 182 located, up from 102); seven permits' site addresses corrected from the permit text, where a mailing address had been recorded. 56 Virginia permits and all 18 Irish sites remain: they need county address points and the EPA's licence maps, both by browser (section 5).
- ~~Crypto mining, second pass~~: 22 entries, 68 sites, 147 figures; regulator records from Kentucky, Manitoba, British Columbia, Québec, Pennsylvania, Denton and Plattsburgh; the miners' SEC figures recorded as claims, with the PUCT's non-public register and Denton's council item as the records beside them.
- ~~Nuclear, first and second pass~~: 16 entries, 12 plants, 80 figures, theme 'Nuclear supply'. Every deal carries its regulator record (NRC licences, pre-application lists, construction permits, the basin commission's water approval for Crane), the national uranium origin (EIA), and spent fuel for Crane and Duane Arnold (DOE). Per-site spent fuel for the operating plants is in PNNL-33938 Appendix B, which the fetch tool cannot reach (section 5).

## 2. Open items stated in the package (kept for the record; each now sits in section 4 or 5)

| Item | Where it is stated | Record source | Days |
|---|---|---|---|
| El Paso: the PUC proposal for decision on El Paso Electric's 366 MW application has not been read; the ledger carries the City's release and the docket number. | `data/climate_trace_seed/TEXAS.md`, `review/BROWSER_FETCH_LIST.csv` priority 1 | PUC of Texas Interchange, docket document | 0.5, by browser |
| Texas: permit-by-rule generator files for the issued authorizations are not online; 13 priority-1 rows in the fetch list point at TCEQ Records Online. | `TEXAS.md` section "What still needs a browser or a records request" | TCEQ public information request (Texas Public Information Act) | 1 to file; 10 business days to answer |
| Texas: rerun `pipeline/tx_fetch.py` against the full Comptroller register copied on 22 October (175 rows; 97 registrations unmatched, 29 with a candidate). | `TEXAS.md`, `tx_comptroller_register_2026-10-22.csv` | Comptroller register, EPA FRS | 1 |
| Virginia: registration 74331 has no PDF; 81 permits carry a site address but no accepted geocode. | `VIRGINIA.md`, `datacenters_register_backlog_unlocated.csv` | DEQ; county GIS parcel lookups for the 81 addresses | 2 |
| Ireland: 18 licensed sites without coordinates. | `ireland_regional_check.md` | EPA licence maps, planning files | 1 |
| 34 priority-2 documents in the browser fetch list (Nevada PUC order, Ohio PUCO tariff, Hertsmere planning file, AESO documents, Amazon 10-K useful-life notes, Arizona ADWR, Taiwan MOEA, and others). Each closes a `partial` entry. | `review/BROWSER_FETCH_LIST.csv` | Named in the list | 3, by browser |
| Monthly scrapers: `EIA_API_KEY` secret not set, so the EIA pulls report "missing credential". | `scrapers/README.md` | EIA open data | 0.1 |
| Promised in the email: the permit extraction extended to Singapore, Johor and Amsterdam. | `data/climate_trace_seed/README.md`, email 2 | IMDA and NEA (Singapore), Johor DOE and SPAN (Malaysia), Omgevingsloket and Noord-Holland (Netherlands) | 4 per jurisdiction |

## 3. The paper layer: how a footprint is cancelled on paper

Now a theme on the ledger ('What the certificates do', `registry/paper_layer.json`, 2026-10-23); steps 1 to 3 are done and 4 and 5 in part. The cancelling is done by four instruments and the rule that lets them count: unbundled certificates (RECs, GOs, I-RECs); PPAs with the certificate attached, usually annual and often on another grid; offsets and removals retired against residual emissions; and the GHG Protocol's market-based Scope 2 method. Raters score the reported number. What the ledger holds today is scaffolding: the standard's supply requirement, the guide's note on water offsets, eGRID listed as the location-based factor independent of market-based claims, EnergyTag and Google's hourly region data as verification sources, Nevada's tariff, and claims such as Scala's I-REC statement recorded as claims.

| # | Step | Record | Days | What the ledger gains |
|---|---|---|---|---|
| 1 | ~~The two-number gap.~~ Done 2026-10-23 (`microsoft-`, `alphabet-google-`, `amazon-`, `meta-`, `oracle-`, `equinix-`, `digital-realty-scope2-two-numbers`). For Microsoft, Alphabet, Amazon, Meta, Oracle, Equinix and Digital Realty: location-based and market-based Scope 2 for the latest two years, the assurance statement, and the headline claim beside them. One entry per company. | The company's own report data tables and the third-party assurance letter inside them; the assured figure is the record, the headline is the claim | 2 | Seven entries built from each company's own assured numbers |
| 2 | ~~The rule.~~ Done 2026-10-23 (`ghg-protocol-scope2-revision`, `scope2-disclosure-rules-esrs-issb-sb253`, `sbti-netzero-scope2`). One entry on the GHG Protocol Scope 2 revision (hourly matching and deliverability are the contested points), its status, and what changes if adopted; and that ESRS E1 already requires both figures. | GHG Protocol consultation documents; ESRS E1 | 1 | The ledger can say which claims survive the new rule |
| 3 | ~~Raters.~~ Done 2026-10-23 (`raters-scope2-inputs-msci-sustainalytics-cdp`; MSCI's choice not found). One entry on what MSCI, Sustainalytics and ISSB-based reporting take as input. | Published methodologies | 1 | Shows why the paper works |
| 4 | ~~In part 2026-10-23~~ Done as far as published (Equinix 47% unbundled, Digital Realty 11%, Alphabet's assured MWh split; `scope2-renewable-claims-by-instrument`). Remaining: CDP responses that refuse automated reading (Alphabet 2025) and Digital Realty's 2025 chart, by browser. Certificate volumes: MWh from unbundled certificates, PPAs and on-site supply, per company per year. | CDP responses, report appendices | 3 | Who leans on paper most |
| 5 | ~~In part 2026-10-23~~ Done as far as the registries allow (`carbon-credits-retired-by-company-disclosures`): AB 1305 disclosures name projects and volumes; Verra, ACR and Puro could not be searched by beneficiary without a browser or login. Offset and removal retirements: which company retired what, against which year. | Verra, Gold Standard, Puro and Isometric registries | 2 | Registry entries instead of press releases |

Steps 1 to 5 are done as far as the published documents allow; what remains waits on documents in section 5. The theme is on the public page; the figures are in the measurements table.

## 4. Available now: what to mine next, in order of value

Each runs here, from records that exist today. Statuses and target files are in `review/INTAKE.csv`.

| # | Item | Record | Lands in | Days |
|---|---|---|---|---|
| 1 | ~~Refiners: smelters and refiners named by chip and server makers~~ Done 2026-10-24 for 12 filers (`registry/supply_chain.json`); Nvidia's and Intel's 75 tantalum and tungsten smelters with 139 links. Remaining: Broadcom's 2025 Form SD, the RMI smelter list to join ids, the other metals | SEC Form SD and conflict-minerals reports (filed May 2026 for 2025) | `sites/topics/refiners/`; `refines_for` links | 3 |
| 2 | ~~Fabs to buyers~~ Done 2026-10-24: 22 links (foundry, memory, packaging, assembly), 24 fab sites, 19 figures, all as filed. Remaining: the parts of the 10-Ks after Item 1A (audited notes, purchase obligations), which the fetch tool does not reach; Samsung's DART filing on its Tesla contract | Nvidia and AMD 10-K, TSMC 20-F | `sites/topics/fabs/`; `fabricates_for`, `supplies_memory_to` links | 2 |
| 3 | ~~Generator hours from the inventory~~ Done 2026-10-24: 137 engine groups from 21 permits (`sites/metered/va_permit_unit_rates.csv`), minimum full-load hours for 20 facilities (`va_generator_hours.csv`), recomputed by the builder. Remaining: DEQ's run-hour logs by records request, which give actual hours | Per-unit NOx rates and hour limits in the DEQ permits matched to EPA's inventory | `sites/metered/va_permit_unit_rates.csv`, then `generator_hours` rows | 3 |
| 4 | Singapore, then Johor and Amsterdam (promised in the email) | IMDA and EDB calls, NEA; Johor DOE and SPAN; Omgevingsloket and Noord-Holland | `review/JURISDICTIONS.csv`, new site and registry files | 4 each |
| 5 | Hardware life: exact 10-K useful-life notes; certified recyclers | SEC EDGAR; R2v3 and e-Stewards lists | `sites/topics/hardware_life/` | 2 |
| 6 | Texas: rerun the facility matching on the full Comptroller register | Register copied 2026-10-22; EPA FRS | `tx_issued_sites.csv` | 1 |
| 7 | Fab water | Taiwan Water Resources Agency, ADWR, City of Phoenix, Korean Ministry of Environment | `sites/topics/fabs/figures.csv` | 2 |
| 8 | Arizona, Oregon, Georgia, Ohio permits through the Virginia pipeline | County and state air-permit PDFs | site lists and permits | 4 each |

## 5. Waiting on a person

| Item | Who | What it unlocks |
|---|---|---|
| 46 open documents on `review/BROWSER_FETCH_LIST.csv` (El Paso proposal for decision, Leixlip GHG permit, reporting-layer documents, priority-2 documents) | you, by browser | closes `partial` entries |
| County address points (Loudoun, Prince William, Spotsylvania) or Virginia's statewide address points for 56 permits; the EPA's licence maps for 18 Irish sites | you, by browser | locates the remaining Virginia and Irish sites |
| PNNL-33938 Appendix B; EIA-923 cooling-water spreadsheets; EIA-860 plant coordinates | you, by browser (spreadsheet and PDF downloads) | spent fuel and water per nuclear plant; plant coordinates |
| Chip trade series: Taiwan Ministry of Finance, USA Trade Online (free login) | you, by browser | the `chips_across_borders` leg |
| Germany's datacenter register (319 sites, PUE and connected load) | you, by browser | a second country with site-level figures |
| 12 records requests (`review/RECORDS_REQUESTS.csv`): TCEQ, the PUCT (mining register), MLGW, TVA, CPS Energy, Silicon Valley Power, the Nebraska utilities, SRP, Grant and Chelan PUDs, Northern Wasco PUD, Virginia DEQ | you file; agencies answer in 10 business days to a month | site-level US loads, Texas generator files, generator run-hours |
| `EIA_API_KEY` secret; the Actions setting for pull requests | you, five minutes | monthly EIA pulls; the weekly pull request |

## 6. Waiting on time

| Item | When |
|---|---|
| First weekly pull request (EPA inventory, Irish reports, benchmarking, watched pages) | Monday 26 October, 06:41 UTC, then weekly |
| Climate TRACE's reply | from Monday; their questions come first |
| EU consultation on minimum performance standards for datacentres | closes 14 December 2026; a submission built from the Irish per-site data |
| GHG Protocol consolidated Scope 2 consultation | planned for Q2 2027; the page is watched |

**Order of work after Monday.** Week 1: items 1, 2 and 6 of section 4, and the first records requests filed. Week 2: items 3 and 5, Singapore begun, the first half of the browser list. Week 3: item 7, Singapore finished, Johor begun, the second half of the browser list. Johor and Amsterdam follow in weeks 4 and 5 whatever happens, because the email promised them. When a reply, a pull request or a records response lands, it goes ahead of the next item in the week it lands.

## 7. The chain, leg by leg

The ledger was built to trace one chain: mine, refiner, fab, chip buyer, datacenter, its power, water and heat, and the hardware's end. Today it is islands. Each leg below says what exists, what is missing, and the record that would make it an edge.

| Leg | Exists (entries) | Missing | Record that would close it | Days |
|---|---|---|---|---|
| Mines | Cobalt (USGS, DRC quotas, RAID fieldwork), nickel (Halmahera), copper water (Cochilco): 7 | Any link from a mine region to a named buyer | See refiners | |
| Refiners | ~~0~~ 12 filers, 75 smelters, 139 links (2026-10-24) | Mine-to-smelter links; other metals | Form SD filings by Nvidia, AMD, Intel, Dell, Supermicro, HPE, Apple and Microsoft name their smelters and refiners for tin, tantalum, tungsten and gold; the Responsible Minerals Initiative publishes audit status. Cobalt and nickel are outside the statute; where a filer reports them voluntarily, the entry says so. | 5 |
| Fabs | TSMC Hsinchu drought, TSMC Phoenix water, Samsung water: 3 | Fab to chip buyer | TSMC 20-F customer concentration; Nvidia 10-K naming TSMC and Samsung as fabs and SK Hynix, Micron and Samsung for memory; ADWR for Arizona withdrawals; Taiwan Water Resources Agency bulletins; Korean Ministry of Environment | 3 |
| Chips in motion | UN Comtrade and USA Trade Online listed as sources: 0 used | Anything past a border | Taiwan Ministry of Finance monthly server exports by destination; US imports by port of entry. The series ends at the country and port; the ledger states that limit as a finding and lays the series beside the permit series. | 3 |
| Datacenters: metered power and water | ~~0 site-level anywhere~~ Done 2026-10-23 for Ireland's 11 licensed installations (`ie-epa-aer-metered-2025`, `ie-equinix-db5-prime-power-gas-2024`): AERs give electricity, water and generator fuel per site for 2024 and 2025. US public utilities publish cluster figures (`us-wa-grant-pud-datacenter-load-2025`, `us-ca-santa-clara-svp-datacenter-share-2025`; TVA memo added to the Memphis entry), and city benchmarking laws give metered electricity for 36 buildings filed as datacenters and 29 larger buildings that contain one (`us-city-benchmarking-datacenter-metered-electricity`; 95 telephone exchanges that file as datacenters are marked separately). | Site-level figures in the US; the 29 unlicensed Irish sites | Public-records requests to MLGW, CPS Energy, Silicon Valley Power, Grant County PUD (the request text is in `sites/metered/public_power_notes.md`); Germany's register by browser (319 sites publish PUE and connected load) | 2 to file, then a month of waiting |
| Power | 305 located sites, 43 documented supply rows, Climate TRACE plant matches, the Wisconsin decision; 9 power links in `sites/chain/edges.csv` | Other jurisdictions | Reuse the Virginia pipeline where regulators post permit PDFs: Maricopa County (Arizona), Oregon DEQ, Georgia EPD, Ohio EPA; then the three promised above | 4 per jurisdiction |
| Water, heat, land, noise, money, jobs | Entries in every category | Mostly single cases where a court or council forced a number out | Priority-2 fetch list; water-rights registers already in `sources.json` | in part 1 |
| Generators: actual use | ~~Nothing~~ Done in part 2026-10-23 (`us-va-nei-2023-datacenter-generator-emissions`): EPA's 2023 inventory gives emissions for 27 Virginia facilities; Irish AERs give fuel burned. | Hours: the inventory has emissions only | Read each permit's per-unit NOx rate into the extractor (`pipeline/va_deq_permits.py`) so tons convert to hours; DEQ annual compliance certifications by records request | 3 |
| Crypto mining: same grids, same queues, often the same sites | Done in part 2026-10-23: 22 entries (`registry/crypto_mining.json`), 68 sites and 147 figures in `sites/topics/crypto/`; 5 lease links in the chain table | Annual MWh per site (no filing read states it); the PUCT register | Public Information Act request to the PUCT for the count and MW of registered mining facilities; the last sections of the miners' 10-Ks by browser | 2 |
| Supply behind 'clean' claims: nuclear | ~~Susquehanna as supply only~~ Done in part 2026-10-23: 16 entries (`registry/nuclear.json`), 12 plants (`sites/topics/nuclear/`), 7 contract links in the chain table | Spent fuel per operating plant; cooling-water withdrawals per plant; licence records outside the US | PNNL-33938 Appendix B and EIA-923 cooling data (spreadsheets, by browser); STUK and the Finnish Government for Loviisa | 2 |
| Hardware life and e-waste | 13, including the hyperscalers' server useful-life changes | Assured reuse: the standard records it as met nowhere | Quote the exact 10-K depreciation notes; R2v3 and e-Stewards certified-facility lists; Eurostat WEEE category data; Basel national reports | 3 |
| Standard | 12 requirements, 8 met somewhere | No buyer references it | A one-page procurement clause; three public buyers to take it to | 2, then meetings |

What public records do not reach, as far as this work can tell: a chip to the site it runs in, and metered site-level power outside a regulator's register or a records request. Both limits are to be stated on the page, not left implicit.

## 8. How progress is recorded

Each finished item becomes entries in `registry/`, with `last_checked` set, and the page is rebuilt with `site/build_page.py` so `docs/` and the README counts move together. This file and `review/INTAKE.csv` are updated in the same commit; a finished row is struck through, not deleted, with the date and the entry ids it produced.
