# Roadmap

As of 2026-10-23, the day the Climate TRACE emails went out. Two parts: what the package already states as open, and the legs of the chain the ledger was built to trace that are not yet traced. Every item names the public record it would rest on, what the ledger gains, and an estimate in working days. The schedule at the end assumes daily work for three weeks after the emails; what slides when a reply arrives is said there.

The rule does not change: a company's statement enters as a claim, a regulator's, court's, grid operator's, statistical office's, auditor's or customs authority's document enters as a record, and nothing enters without a URL.

## 1. Open items already stated in the package

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

## 2. The paper layer: how a footprint is cancelled on paper

Not yet a theme on the ledger. The cancelling is done by four instruments and the rule that lets them count: unbundled certificates (RECs, GOs, I-RECs); PPAs with the certificate attached, usually annual and often on another grid; offsets and removals retired against residual emissions; and the GHG Protocol's market-based Scope 2 method. Raters score the reported number. What the ledger holds today is scaffolding: the standard's supply requirement, the guide's note on water offsets, eGRID listed as the location-based factor independent of market-based claims, EnergyTag and Google's hourly region data as verification sources, Nevada's tariff, and claims such as Scala's I-REC statement recorded as claims.

| # | Step | Record | Days | What the ledger gains |
|---|---|---|---|---|
| 1 | The two-number gap. For Microsoft, Alphabet, Amazon, Meta, Oracle, Equinix and Digital Realty: location-based and market-based Scope 2 for the latest two years, the assurance statement, and the headline claim beside them. One entry per company. | The company's own report data tables and the third-party assurance letter inside them; the assured figure is the record, the headline is the claim | 2 | Seven entries built from each company's own assured numbers |
| 2 | The rule. One entry on the GHG Protocol Scope 2 revision (hourly matching and deliverability are the contested points), its status, and what changes if adopted; and that ESRS E1 already requires both figures. | GHG Protocol consultation documents; ESRS E1 | 1 | The ledger can say which claims survive the new rule |
| 3 | Raters. One entry on what MSCI, Sustainalytics and ISSB-based reporting take as input. | Published methodologies | 1 | Shows why the paper works |
| 4 | Certificate volumes: MWh from unbundled certificates, PPAs and on-site supply, per company per year. | CDP responses, report appendices | 3 | Who leans on paper most |
| 5 | Offset and removal retirements: which company retired what, against which year. | Verra, Gold Standard, Puro and Isometric registries | 2 | Registry entries instead of press releases |

Nine days. Steps 1 to 3 first. None of this belongs in the Climate TRACE handover; it is a theme for the public page.

## 3. The chain, leg by leg

The ledger was built to trace one chain: mine, refiner, fab, chip buyer, datacenter, its power, water and heat, and the hardware's end. Today it is islands. Each leg below says what exists, what is missing, and the record that would make it an edge.

| Leg | Exists (entries) | Missing | Record that would close it | Days |
|---|---|---|---|---|
| Mines | Cobalt (USGS, DRC quotas, RAID fieldwork), nickel (Halmahera), copper water (Cochilco): 7 | Any link from a mine region to a named buyer | See refiners | |
| Refiners | 0 | The whole leg | Form SD filings by Nvidia, AMD, Intel, Dell, Supermicro, HPE, Apple and Microsoft name their smelters and refiners for tin, tantalum, tungsten and gold; the Responsible Minerals Initiative publishes audit status. Cobalt and nickel are outside the statute; where a filer reports them voluntarily, the entry says so. | 5 |
| Fabs | TSMC Hsinchu drought, TSMC Phoenix water, Samsung water: 3 | Fab to chip buyer | TSMC 20-F customer concentration; Nvidia 10-K naming TSMC and Samsung as fabs and SK Hynix, Micron and Samsung for memory; ADWR for Arizona withdrawals; Taiwan Water Resources Agency bulletins; Korean Ministry of Environment | 3 |
| Chips in motion | UN Comtrade and USA Trade Online listed as sources: 0 used | Anything past a border | Taiwan Ministry of Finance monthly server exports by destination; US imports by port of entry. The series ends at the country and port; the ledger states that limit as a finding and lays the series beside the permit series. | 3 |
| Datacenters: metered power and water | ~~0 site-level anywhere~~ Done 2026-10-23 for Ireland's 11 licensed installations (`ie-epa-aer-metered-2025`, `ie-equinix-db5-prime-power-gas-2024`): AERs give electricity, water and generator fuel per site for 2024 and 2025. US public utilities publish cluster figures (`us-wa-grant-pud-datacenter-load-2025`, `us-ca-santa-clara-svp-datacenter-share-2025`; TVA memo added to the Memphis entry), and city benchmarking laws give metered electricity for urban datacenters (`us-city-benchmarking-datacenter-metered-electricity`, 263 building-years). | Site-level figures in the US; the 29 unlicensed Irish sites | Public-records requests to MLGW, CPS Energy, Silicon Valley Power, Grant County PUD (the request text is in `sites/metered/public_power_notes.md`); Germany's register by browser (319 sites publish PUE and connected load) | 2 to file, then a month of waiting |
| Power | 282 located sites, 43 documented supply rows, Climate TRACE plant matches, the Wisconsin decision | Other jurisdictions | Reuse the Virginia pipeline where regulators post permit PDFs: Maricopa County (Arizona), Oregon DEQ, Georgia EPD, Ohio EPA; then the three promised above | 4 per jurisdiction |
| Water, heat, land, noise, money, jobs | Entries in every category | Mostly single cases where a court or council forced a number out | Priority-2 fetch list; water-rights registers already in `sources.json` | in part 1 |
| Generators: actual use | ~~Nothing~~ Done in part 2026-10-23 (`us-va-nei-2023-datacenter-generator-emissions`): EPA's 2023 inventory gives emissions for 27 Virginia facilities; Irish AERs give fuel burned. | Hours: the inventory has emissions only | Read each permit's per-unit NOx rate into the extractor (`pipeline/va_deq_permits.py`) so tons convert to hours; DEQ annual compliance certifications by records request | 3 |
| Hardware life and e-waste | 13, including the hyperscalers' server useful-life changes | Assured reuse: the standard records it as met nowhere | Quote the exact 10-K depreciation notes; R2v3 and e-Stewards certified-facility lists; Eurostat WEEE category data; Basel national reports | 3 |
| Standard | 12 requirements, 8 met somewhere | No buyer references it | A one-page procurement clause; three public buyers to take it to | 2, then meetings |

What public records do not reach, as far as this work can tell: a chip to the site it runs in, and metered site-level power outside a regulator's register or a records request. Both limits are to be stated on the page, not left implicit.

## 4. Schedule: three weeks after the emails

Assumes daily sessions. Items marked (browser) need a person with a browser; everything else runs here.

**Week 1.** Paper layer 1 to 3. El Paso proposal for decision read (browser). TCEQ public information request filed. ~~Irish AER check on one site, then all 40 if it holds~~ (done 23 Oct: 11 licensed sites, 22 site-years). `EIA_API_KEY` set. Comptroller rerun. Climate TRACE follow-up drafted for day 8 if no reply.

**Week 2.** Refiners and fabs from filings. Hardware life from the 10-Ks. Arizona permit extraction. Priority-2 fetch list, first half (browser).

**Week 3.** Trade series. Paper layer 4 and 5. Virginia and Ireland geocoding backlog. Singapore begun. Procurement clause drafted. Priority-2 fetch list, second half (browser).

If Climate TRACE replies, their questions come first and the week they land in slides by the days spent. Johor and Amsterdam follow Singapore in the fourth and fifth weeks whatever happens, because the email promised them.

## 5. How progress is recorded

Each finished item becomes entries in `registry/`, with `last_checked` set, and the page is rebuilt with `site/build_page.py` so `docs/` and the README counts move together. This file is updated in the same commit; a finished row is struck through, not deleted, with the date and the entry ids it produced.
