# Independent check of the measurements table, 2026-10-23

A reviewer who had not seen how `measurements.csv` was built was given 56 rows drawn at random, stratified by source file, and asked to fetch each row's document, find the figure, and test the row's own logic (value, unit, conversion, period, basis, record or claim). The brief, the sample and the reviewer's results are in the repository under `review/measurements_check_2026-10-23/`, unedited apart from local file paths. Measurement ids there are the ids at the time of the check; an id is a hash of the row's content, so a corrected row has a new id.

## Result

| Verdict | Rows |
|---|---|
| Found in the document as stated | 53 |
| Found, but different from the row | 2 |
| Not in the linked document | 1 |

Of the 53 found, 29 had no logic problem. The rest, and the three that did not match, are below with what was done. Where the reviewer named a pattern, the fix was applied to every row with that pattern, not only to the sampled row.

## Problems and corrections

**Not in the document.** An Irish site's generator figures (Amazon, Leixlip) came from a greenhouse-gas permit, but the row linked the licence application, which names no generators. The figures are withheld from the table until the permit itself is linked; it is on `review/BROWSER_FETCH_LIST.csv`.

**Different from the document.**
- Rochester Lateral (Wisconsin): the row gave $217.1M, a rounding; the filing states $217,093,529 and $210,942,310 for the two estimates. Both are now recorded exactly.
- Aragón water: the row attributed about 1 million m³ a year to Amazon's datacentres alone; the article's estimate covers four Amazon expansions and Blackstone's project together. The row now says so, is recorded as a rate (m³ per year) and is marked approximate.

**Wrong metric.**
- Three on-site gas plants (xAI Colossus 1 and 2, and Homer City) were labelled standby generation. Cause: a test for the word "standby" also matched "not standby". Fixed in the builder; they are now generation capacity, primary supply.
- Equinix's total energy consumption (2023 and 2024) was labelled electricity. Now total energy.
- Dominion's 30,132 MW at the engineering-letter stage was labelled contracted capacity. The filing separates 16,913 MW under firm contracts from 30,132 MW still being studied; the second is now requested capacity, and the brief gives the split.

**Wrong period.** Australian (AEMO) and Japanese (OCCTO) fiscal-year figures were given calendar years. Every fiscal-year row now has its fiscal period (Australia July to June; Japan and India April to March; Virginia, Georgia and Microsoft July to June; Oracle June to May). A cumulative count was given a whole year; it now has its as-of date. Amazon's expected annual generation of its carbon-free portfolio (as of January 2025) was given calendar 2024; it now has no calendar period and its note says what it is.

**Wrong basis or side.**
- AEMO's figures are a grid operator's own publication, not a statistics office's: basis now `utility_published`.
- Statnett's presentation is the grid operator's own document, not a filing: `utility_published`.
- A Brazilian rapporteur's opinion on a bill is not a regulator's decision: a new basis, `legislative_document` (a bill, rapporteur's opinion or committee report, not enacted law), now covers it and the Senate consultancy's revenue estimate.
- The forecast emissions in a British Columbia utility commission decision come from the applicant's screening study that the decision recites: basis `filed`.
- Sustainability figures in Equinix's and Digital Realty's SEC filings are the companies' own statements: `company_statement`, claim. Outside the entries' text, any row with basis `company_statement` is now a claim by rule.
- Company figures in the record of 21 entries (Fortum's heat-pump and storage figures and others): see the last section.
- The El Paso plant row named the state agencies as publisher; the document is a City of El Paso news release describing El Paso Electric's application. Publisher, title, date and basis (`press_report`) corrected, and the figure is recorded as the release prints it ("366-megawatt").

**The figure as written.** The documentation said `value_as_published` holds "the exact characters of the source". That was wrong in two ways the reviewer found: for figures from the ledger's entries it holds the figure as the entry's sentence writes it (584,125 GJ where the report prints 584125), and for some Irish permit figures it held a sum the ledger computed. The documentation now says what the column is: the figure exactly as written in the text it was taken from (the document's line or cell, or the entry's own sentence). Sums the ledger computed have basis `derived` and say so in their notes.

**Bounds not marked.** "At least 50%" and similar were stored without the qualifier. A `qualifier` column now records `lower_bound`, `upper_bound` or `approximate`, read from the figure and the words immediately before it ("not more than" is an upper bound; "over 30 years" is a period, not a bound). Malaysia's local-content rule, which the source states as "at least 30%", is now worded that way in its entry.

**Dates.** Notes on 38 rows said documents were re-read on 2026-10-24, a day after the check. The re-reading was done on 2026-10-23; every such date is corrected.

**Smaller corrections.** Notes are no longer cut at 200 characters. An Irish report row said "(HVO)" where the table says only "Renewable Biomass"; removed. A Brazilian row said "phase-1" where the article does not; removed. A Norwegian row named a sub-area the slide does not; removed. A GHG Protocol note presented a paraphrase as a quotation; now marked as paraphrase. Homer City's source now carries the article's current headline and date (3 April 2025). The Brazilian rapporteur's opinion is undated; its source now says so instead of giving the upload month.

**Left as they were, with the reason.**
- Telephone exchanges in New York and Philadelphia that file as "Data Center" (two sampled): already marked `telecom_exchange`. Checking this found that the classifier read notes about other buildings and missed New England Telephone's name forms; it now reads only the building's own name and owner. 95 exchanges, 36 buildings filed as datacenters and 29 larger buildings that contain one have metered electricity; the brief and README now give these counts instead of calling all 263 building-years datacenters.
- 2020 inventory rows linked to the 2023 inventory entry: the entry covers the inventory and cites the 2020 figures; each row's period says 2020.
- A public utility's figure with no entry (CPS Energy): no entry covers it yet; `entry_id` is empty by design.
- A Boston row with no period: Boston's layer gives a reporting year but not the year of use; the row has no period and its note says so.

## Company figures moved from record to claim

The ledger's founding rule is that a company's statement is a claim and a regulator's, court's, grid operator's, statistics office's, auditor's or customs authority's document is a record. Building the table showed 77 figures marked as company statements sitting in the record of 21 entries. A second reviewer rewrote those 21 entries under a fixed brief: move each listed figure, with the clause that states it, into the claim and name who says it; keep every other word of the record and the claim; move a source only when it now supports the claim alone; change a gap only so it stays true. A script checked that no number was lost and nothing else changed. The brief, the reviewer's notes, and the text of the 21 entries before and after are in `review/sides_2026-10-23/`.

71 figures moved. The reviewer left six in place, and the maintainers then settled them:
- Dominion's 10-K shares of Virginia sales (28% in 2025, 26% in 2024) were already in the claim; they are now removed from the record, and the 10-K is cited for the claim only.
- Stockholm Exergi's four figures (117 GWh of recovered heat in 2023, its two 50% owners, 98% renewable or recovered) come from the statutory annual report of a district-heating utility half-owned by the City of Stockholm. They stay in the record with basis `utility_published`.

Two further adjustments were made on review. Microsoft's diverted waste (28,285 t, FY24) sits inside Deloitte & Touche's limited assurance of the fact sheet's Section 1, so, as in the reporting layer, it stays in the record with basis `assured_disclosure`. And the same rule moved company sentences that carried no listed figure: Teraco's announcements about its solar plant and its chief executive's remark on diesel spend, TSMC engineers' statement about the site's water supply, Google's statement on seawater cooling (already in the claim), and EcoCloud's capacity, tariff and PUE figures, known only through press reports. Checking the EcoCloud entry also corrected a status sentence: DCD's May 2026 report mentions EcoCloud's 2023 groundbreaking but gives no later status, and the entry now says that and cites it.

After the move, no row with basis `company_statement` sits on the record side of the table.

## A second check, the same evening: figures added on 23 October

The same kind of reviewer checked 30 figures drawn at random from those added later on 23 October (nuclear plants and deals, crypto-mining sites and records, companies' renewable-electricity and carbon-credit disclosures) and all 14 links in the new chain table (`sites/chain/edges.csv`). Files: `review/measurements_check_2026-10-23b/`.

**Result.** 29 of 30 figures were found as stated, with every value, conversion and qualifier correct; 11 of 14 links were found, 2 differed, and 1 document (the Wisconsin decision viewer) did not load for the reviewer. The pattern: the numbers were right, but four of them were attached to the wrong thing, and the second reading had checked the value, not the subject.

**Corrections.**
- Google's "up to 500 MW" agreement with Kairos covers a fleet and does not name Hermes 2; it was recorded against the Hermes 2 site. It is now recorded against the entry, and the Hermes 2 link in the chain is TVA's power purchase agreement for up to 50 MW (press report), not Google's.
- Meta's 2,176 MW purchase is from Perry and Davis-Besse only; the link to Beaver Valley now rests on the 433 MW of uprates across all three plants, with the note that the release does not break out Beaver Valley's share. Figures for more than one plant (2,176 MW, 433 MW, 2,609 MW) are now recorded against the entry, not one plant.
- Beaver Valley's 2,900 MWt is Unit 1's licence; the row now says so.
- Meta's ">99%" is the share of electricity physically from the grid, not a renewable-matching method; it is now a plain share with that description.
- Core Scientific's lease link no longer names all ten of its sites as leased to CoreWeave.
- Equinix's nuclear pre-orders and letters of intent are now planned capacity, like Switch's non-binding agreement with Oklo, and the 500 MWe pre-order names Stellaria.
- Dates the documents give are now in the period fields (CleanSpark's count as of 30 September 2025; the Massillon fire in November 2025), companies are named on multi-company rows (Bitdeer, CleanSpark), Knoxville's two phases are labelled, and DOE's spent-fuel inventory has basis `official_statistic` rather than `inventory`.

**Settled.** The reviewer asked whether a company figure covered by an auditor's assurance is a record or a claim, since the code and `CONTRIBUTING.md` read differently. It is a record with basis `assured_disclosure`, because the auditor's statement is the record; `CONTRIBUTING.md` now says so, and says that the second reading checks what a figure is attached to as well as the figure.

**Left.** The British Columbia ministry's count of 21 mining projects keeps basis `official_statistic` (a government aggregate). The Wisconsin link stands on the decision cited in the ledger entry, which was read when the entry was written.

## A third check, 24 October: the chip legs

A third reviewer checked 15 figures drawn at random from the conflict-minerals reports and the chip makers' filings, and 16 chain links (smelter to company; foundry, memory, packaging and assembly to buyer). Files: `review/measurements_check_2026-10-24/`.

**Result.** All 31 were found in their documents, and every smelter link named the right metal and country in the right company's list. As in the second check, the faults were in labels and parties, not numbers.

**Corrections.** TSMC's capacity is now recorded as written, "exceeded 17 million wafers", with qualifier `lower_bound`, and the builder now reads "exceeded" as a lower bound. The packager for AMD is the two joint ventures it holds with Tongfu, now an entity of its own, with AMD and Tongfu each linked to it as owners (the chain's first ownership links). Broadcom's "Foxconn Technology Group" keeps its link to Hon Hai's group, with a note that the filing does not say which entity does the work. Links taken from annual filings now carry the fiscal year as their period. AMD's 219 is recorded as the denominator of its covered-countries sentence, Dell's 219 as a count on 31 December 2025, and Super Micro is named on its purchase-share row. Notes that called a re-opening with the same tool a "re-read" now say it is not a second reading. Two Japanese smelters that may be one company under two names are flagged until the RMI list resolves them.

## A fourth check, 24 October: water and fuel links, and generator hours

A fourth reviewer checked all 30 water and fuel links in the chain table and re-derived the generator hours for six Virginia permits from the permit texts. Files: `review/measurements_check_2026-10-24b/`.

**Result.** 29 of 30 links were found as stated, with every quoted phrase in its document and every planned link marked planned. For the six permits, the reviewer's own reading gave the same engine counts and NOx limits, the same hours, and the same inventory values as EPA's Envirofacts.

**Corrections.** The Energy Transfer release does not name the plants that serve Meta's Louisiana site; the link now says what the release says and points to the Louisiana PSC docket for the rest. The Rochester Lateral links rest on the PSC case page's summary of the application, so their basis is now the applicant's filing, and the plants' MW, which come from other decisions, are no longer written into the link. The Homer City pipeline route is the trade journal's own wording, now `press_report`, with a note that a pipeline carries gas and EQT supplies it. Equinix DB5's gas link now gives both connections in 2024 (low pressure until November, high pressure from 29 November). The TSMC water link has a new basis, `government_document`, for a statement of fact in an agency's environmental assessment that is neither a decision nor an estimate. The Irish water links now use basis `filed`, like the other links from the same reports; Equinix's note now gives recycled water, not rainwater, and Microsoft's notes that the report's total leaves out its rainwater. The Dalles and Cerrillos notes now say only what their documents say.

**Generator hours.** All six confirmed. Caveats added for Microsoft's Boydton permit, whose unit numbers skip several engines without explanation, and for the LC data centers, where the inventory's facility name covers two of the permit's four buildings. Where a permit was issued years before or after the inventory year, the caveats already say so; the published figures remain minimums.
