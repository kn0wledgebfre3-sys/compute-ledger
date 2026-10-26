# Final review: "Datacenters for Climate TRACE" package, 21 Oct 2026

Reviewer: same sceptical methodology reviewer as `hostile_review.md`. Scope: `site/brief.html` against every file in `data/climate_trace_seed/`, the Virginia re-read working directory, the ledger entries in `registry/north_america.json`, and my earlier findings. No web checks.

## Verdict: fix, then send

The substance has improved a great deal and most of what I flagged last time was fixed rather than papered over: the Ireland check is now a bounds table and the brief says so; the five worked rows are withdrawn and the brief admits why; the supply column was reclassified and the brief's counts match the JSON; the Virginia re-read is real work, its resolution notes are row-specific, and 33.7 GW is defensible as a stated-rating central value with the 33.4–33.9 band. But the brief as it stands would embarrass the sender in four places a Climate TRACE methodology lead will hit within minutes: (1) the page contradicts itself on its own headline number, saying 182 sites / 13,973 units / 33.7 GW in the Virginia section and then "153 with generator MW, one per generator unit (857)" in the handover list and "estimate those 153 sites" in the ask; (2) the "Virginia bounding box" figure (97.4 Mt, 55% coal) is not Virginia: the box as stated contains Gavin (Ohio) and Harrison (West Virginia), which between them are 23 Mt of the 97, and anyone who knows Virginia's fuel mix will stop reading there; (3) the "175 geocoded Virginia permit sites, 104 found" file is actually 175 geocoded sites worldwide (Chile, Taiwan and Japan included), only 4 of which carry permit MW, so the sentence describing it is wrong three times; (4) seven files the brief and the notes point to (`climate_trace_matches.csv`, `virginia_nearest_generation.csv`, `va_permits.csv`, `va_generator_rows.csv`, the three `tx_*.csv`) are not in the package directory, and the README still describes the pre-Virginia package. Each is an hour's work. Fix the items marked "blocks send" and "fix before send" below, and send.

## Findings

Severity: **blocks send** | **fix before send** | **caveat** | **fine**.

### A. Internal consistency of the brief

**A1 — Stale first-reading numbers on the same page as the re-read. Blocks send.**
Text: handover list item 5, "Virginia: 183 permits read, 153 with generator MW, one row per site and one per generator unit (857), with the pipeline that produced them"; and the ask, "estimate those 153 sites as ranges". The Virginia section says 182 sites, 13,973 units, 33,693 MW. 153 and 857 are the pipeline's first reading (`va_permits.csv`: 153 non-null MW; `va_generator_rows.csv`: 857 table rows, not units). Change: item 5 → "Virginia: 183 registrations, 182 read with a generator inventory, 13,973 units, 33.7 GW; both readings, the comparison and the hand decisions (`va_permits_resolved.csv`, `va_reread_comparison.csv`, `va_reread_decisions.csv`, `VIRGINIA_REREAD_REPORT.md`)". Ask → "those 182 sites".

**A2 — "127 geocoded" and "154 street addresses" trace to nothing in the package. Fix before send.**
Text: "154 street addresses, 127 geocoded". 154 is `facility_street` in the pipeline's `va_permits.csv` (not in the package); `va_permits_resolved.csv` has `site_street` on 180 of 182 rows. 127 appears in no file: `handover_summary.json` (other copy) says 116 Virginia rows with coordinates; `virginia_nearest_generation.csv` has 119 Virginia registrations with coordinates. Change: state the numbers from a file that ships, e.g. "180 with a site street in the resolved file (metadata read once, not twice); 119 geocoded", or drop the geocode count until the resolved file is geocoded.

**A3 — "183/182/181" reconciliation. Fix before send (one word).**
`VIRGINIA_REREAD_REPORT.md` headline says "across 181 readable registrations (177 high-confidence, 5 medium, 2 unreadable)"; 177 + 5 = 182, the resolved CSV has 182 rows with MW, the totals table sums 24 + 22 + 107 + 29 = 182, and `VIRGINIA.md` and the brief say 182. The 183 is the DEQ list; the two "unreadable" are 74331 (no PDF) and `5.pdf` (an Access-Denied page, not a registration). Change: report headline → "182 readable registrations"; brief "opened all 183 permit PDFs" → "182 of the 183 permits on the list (one would not download)".

**A4 — "Per-unit ratings run 1.5 to 3.7 MW, median 2.47." Fix before send.**
This is the per-site average unit size (site MW ÷ site count: median 2.474, max 3.653), not per-unit ratings, and its minimum is 0.43 MW, not 1.5. Individual units in the resolved notes go down to 250 kW (30142, 52403) and 563 kW. Change: "site-average unit size 0.4–3.7 MW, median 2.5 MW; most units are 2.0–3.0 MW".

**A5 — Supply split counts. Fine.**
Bar: 19 / 5 / 3 / 5 / 4 / 7 matches `dedicated_supply.json` (grid_only 19, system_fossil_dc_driven 5, dedicated_fossil 3, dedicated_clean_firm 5, certificates_only 4, wheeled 3 + mixed 2 + unpermitted 1 + bring_your_own 1 = 7). "30 rows on a document, 13 on press" matches confidence high 18 + medium 12 = 30, low 13.

**A6 — Climate TRACE table values. Fine.**
All five 2025 tCO2e figures equal the twelve 2025 months of `climate_trace_matched_plants_monthly.csv` summed (922,444; 6,952,400; 2,173,970; 1,376,900; 0). Emissions-confidence words match the file. Chesterfield Oct/Nov 2025 = 1,349 and 3,715 tCO2e as stated. Bbox 2025 total 97,408,100 and coal-only share 55.2% match the by-fuel file.

**A7 — Handover item 1 (96 / 78 / 28). Fine, with a duplicate.**
Matches `README.json` and the seed CSV. But the seed carries Google Grange Castle twice (`ledger-dc-irl-google-dublin-grange-castle-data-center`, Wikipedia point, and `irl-google-grange-castle-ghg170`, 0.7 km apart) although `ireland_regional_check.md` §3 says the Wikipedia row is superseded; Vantage Profile Park also appears as a campus row plus the Ireland-list rows. Change (fix before send): drop the superseded rows and restate the count, or mark them `superseded_by` in `other7`.

### B. Virginia

**B1 — Is 33.7 GW defensible? Caveat (yes, with two sentences added).**
I sampled seven `disagree` rows (74118, 73199, 74154, 74264, 52299, 53198, 74337) plus the largest site (51232): every resolution note names the rows (count × kW) and the pipeline's specific failure, and 51232's cached text shows EG IDs running to EG547 at 2,500/2,250 kW, consistent with 544 units / 1,331 MW. The 98-low / 9-high split is reproducible from the comparison CSV. Two things the brief should say: (a) the second reader resolved all 129 disagreements in its own favour (the report admits this); the sender should state that and that the ten spot-checks were the reader's own, or have someone else open five PDFs tonight; (b) 2,913 of the 13,973 units are permitted as non-emergency (demand-response, SCR-controlled) and 80.6 MW are gas engines, so "standby" is a label of convenience and part of this fleet is Scope 1 generation, not backup.

**B2 — "traced the cause to one parser bug". Fix before send.**
The report lists eight pipeline error patterns; the first-row-dropped bug explains 70 of 129 wrong permits (75 notes mention it). Change: "traced most of it to one parser bug".

**B3 — "Dominion Energy told its regulator it has about 40,000 MW of datacenter capacity under contract." Fix before send.**
The ledger entry's claim source is a Data Center Dynamics article quoting Dominion's "~40 GW in various stages of contracting" (Dec 2024); nothing in the package is an SCC filing saying "under contract". `VIRGINIA.md` says "(SCC filings, Dec 2024)" with no such filing linked. Change: "Dominion reported about 40 GW of datacenter capacity 'in various stages of contracting' as of December 2024 (earnings/IRP, via DCD)".

**B4 — "33.7 GW of permitted standby puts the physically permitted fleet in the same order as the contracted figure." Caveat.**
Fair only in the loose sense the brief's own Ireland paragraph sets out: standby MW ≥ design load under any redundancy design, so 33.7 GW permitted implies a design load of roughly 28–33 GW under N+1 and roughly 17 GW under 2N. "Same order" survives either way; "physically permitted" does not mean built (many permits are for phases not yet constructed), and the 40 GW is a pipeline that includes sites not yet permitted, in one utility's territory, while DEQ permits cover the whole state. Change: add "under N+1; about half that under 2N; permitted is not built" or cut the sentence to "the two figures are consistent with each other". Also "That is the Ireland check" overstates: Ireland is checked against a meter; Virginia against a utility's contracting pipeline. Say "the Virginia analogue of the Ireland check, with a contract figure standing in for a meter".

**B5 — "182 sites". Caveat.**
182 registrations. 101 Herbert Drive carries five Microsoft registrations (fine, separate buildings); 7900 Telegraph Road carries 74154 (ADF-E, 2026, 40.6 MW) and 74207 (Amazon, 2024, 38.0 MW), which may be one facility re-permitted; 7471 Bear Wallow Rd carries an Amazon and a Microsoft registration at the same street, which looks like a metadata error. Change: "182 registrations" and a note that same-address pairs were not deduplicated.

### C. Climate TRACE plants and the bounding box

**C1 — "The 126 electricity assets inside a Virginia bounding box emitted 97.4 million tCO2e in 2025, 55% from coal; that is the generation the permitted standby fleet sits beside." Blocks send.**
The box (36.5–39.5 N, 83.7–75.2 W) is Virginia's extent, which also contains most of West Virginia, Maryland south of 39.5, DC, Delaware, eastern Kentucky and the Ohio River plants south of 39.5. From `climate_trace_top_assets.csv` (Climate TRACE's own coordinates): Gavin, OH (38.93, −82.12; 12.4 Mt) and FirstEnergy Harrison, WV (39.38, −80.33; 10.4 Mt) are inside the box, and John Amos, Mountaineer, Mitchell and Brandon Shores will be too. Virginia's own power sector is a fraction of 97 Mt and is gas and nuclear, not 55% coal. `CLIMATE_TRACE_SERIES.md` says the box "overlaps neighbouring states at the edges"; it is not the edges, it is the bulk of the coal. Change: clip to the state polygon (or filter the export on the state field if it has one) and restate, or relabel honestly: "a box spanning Virginia, most of West Virginia and Maryland and the Ohio River plants", drop "55% coal", and drop "the generation the standby fleet sits beside". Do not call it Virginia.

**C2 — "We matched your October 2025 asset-level estimates (release 5.11.0 …)". Fix before send.**
The series runs to July 2026 and `CLIMATE_TRACE_SERIES.md` says downloaded 21 Oct 2026. An October 2025 release cannot contain July 2026. Change: "your 5.11.0 asset-level estimates, downloaded 21 October 2026".

**C3 — Elm Road: "Microsoft the stated driver". Fix before send.**
The ledger record says We Energies cited "energy-intensive data centers"; the elements tying the plant to Microsoft are press-sourced, and the supply row is now `confidence: low` with a review note saying exactly that. Change: "data-center load the stated driver; Microsoft's 15-year contract is press-sourced".

**C4 — Southaven: "xAI's 41-turbine, 1.2 GW permitted plant (MDEQ, 2026)". Caveat.**
The ledger entry's `verification_note` says the MDEQ permit could not be retrieved and the 41/1.2 GW figures are press; what was retrieved is the Agreed Order on the 69 temporary turbines. Change: "(MDEQ permit reported March 2026, not retrieved; the MDEQ Agreed Order on the 69 temporary turbines is in the ledger)". Also the more useful sentence for Climate TRACE is that the 69 mobile turbines running since 2025 do not appear in their inventory either.

**C5 — Moxie Freedom / Susquehanna. Fix before send (in the file the brief points to).**
`CLIMATE_TRACE_SERIES.md` describes the Moxie row honestly ("nearest fossil asset; not the plant in the record"). But `climate_trace_matches.csv` (the file the brief names, present only in the other copy) carries a generated `sentence` field reading "Susquehanna: Climate TRACE estimates 1,235,680 tCO2e in 2025 for 'Moxie Freedom Generation Plant'", which pairs a nuclear PPA campus with a gas plant's emissions, and its `trace_confidence` column is empty ("confidence n/a") while the brief says "Your per-asset confidence ratings are carried through from the export". Change: ship `climate_trace_matched_plants_monthly.csv` as the match table (it has the confidence), rewrite the Moxie sentence or drop the row, and point the brief at the file that is actually in the package. Also check the export for the Susquehanna nuclear asset itself under a short name; a name match on "Susquehanna" alone would settle whether it is absent or merely mis-named.

**C6 — "Chesterfield drops to near zero in October and November 2025 … the seasonal baseline". Caveat.**
A two-month zero is an autumn outage, not a season. Say "outage pattern".

**C7 — "Correct: the coal plant is gone". Caveat (tone).**
Grading their zero is fine once; "Your series will show it arrive" is fine. Leave, but do not add more of this register.

### D. The nearest-generation file

**D1 — "A second file lists, for each of 175 geocoded Virginia permit sites, the nearest asset in your inventory within 15 km (104 found) … the pairing of permitted standby MW with your nearest estimated plant". Blocks send as written.**
`virginia_nearest_generation.csv` (not in the package directory) has 175 rows = every geocoded seed site worldwide: 119 Virginia registrations and 56 others including Google Cerrillos (Chile), Changhua (Taiwan), Inzai (Japan) and Eemshaven. Only 4 of 175 rows carry `permit_mw`, so the "pairing of permitted standby MW with the nearest plant" does not exist in the file. It was built from the pipeline's first reading, not the resolved one. Change: rebuild from `va_permits_resolved.csv` geocodes with the resolved MW on every row, restrict to Virginia, restate the counts, and ship it; or delete the paragraph.

### E. Ireland

**E1 — Brief wording vs revised method. Fine.**
"bounds load from above once the redundancy design is known", "0.54–0.71 … plausibly 0.3–0.5; under 2N it imposes no bound", "0.12–0.23 … campus ramping", "3,830 by licence cap, 4,279 by sum of units", "40 sites, 22 located, most from grid references in EPA documents", "sixteen operating sites" all match §4 and the CSV (40 rows, 22 with lat, 17 operating with a MW figure of which DB5 is primary gas).

**E2 — Two numbers the brief uses that depend on an unstated assumption. Caveat.**
"plausibly puts it at 0.3–0.5" assumes the 16 sites carry 50–70% of national load (§4 table, last column). Say so in the brief in six words. And "0.54–0.71" is the N+1 bound at ÷1.01–1.2; the §4 table's ÷1.5 row gives 0.80. Either say "0.54–0.80" or say "fleet or per-block N+1".

**E3 — §4 "Recommended procedure" still uses the withdrawn 97% and the single ÷1.2. Fix before send (method note).**
Text: "(i) take the 7,663 GWh (2025) total, scale 97% to Dublin; (ii) allocate … (0.385 x MWth / 1.2)". The paragraph above it withdraws 97% and the sensitivity table replaces ÷1.2. This is the one place an earlier finding was papered over rather than fixed. Change: "(i) take the national total (no regional split is documented); (ii) allocate in proportion to standby MWe under an explicit redundancy assumption, carried as a column".

**E4 — MWth and MW mixed inside 4,279. Caveat.**
Equinix DB4 (21.8), DB1 (39.0), K2 Dublin 21 (34.8) and EdgeConneX (533.6) are "MW" per GHG permit in `generator_mw_basis`; the rest are MWth. About 630 of the 4,279 may be electrical. The 3,830 licence-cap figure is not reproducible from the CSV (caps live inside the free-text basis column). Change: a `generator_mw_cap` column, and flag the four rows.

**E5 — "Ireland is the only country whose statistics office meters datacenter electricity nationally". Caveat.**
Statistics Netherlands has published datacenter electricity consumption, and Denmark and Singapore publish official figures. "The only country" is the kind of claim a coalition lead enjoys correcting. Change: "one of very few countries" or "the only country we know of".

### F. Supply column and method note

**F1 — "five more where a utility's system gas plant was approved with datacenter growth as the stated reason". Fix before send.**
Of the five `system_fossil_dc_driven` rows, Chesterfield, Wisconsin and Batam fit. The other two do not: the AESO BYOG policy row (a connection policy, no plant) and Greenlight (a merchant CCGT with a tolling contract to an unnamed datacenter customer, AUC-approved; not a utility system plant). Both carry the same copy-pasted review note ("Customer reported but unconfirmed; category requires a named load"), which makes sense for Greenlight and not for the policy row, which was `bring_your_own` and should still be. Change: AESO policy row back to `bring_your_own` (bring_your_own 2, system 4); Greenlight either `dedicated_fossil` with "customer unnamed" in `resource` (gas 4) or a one-off `dedicated_fossil_unassigned`; brief sentence and bar to follow.

**F2 — "five documented clean-firm arrangements". Fix before send.**
Three of the five `dedicated_clean_firm` rows are `confidence: low` by the method's own rule (Nevada: category rests on press, docket not linked; EcoCloud: DCD only; Microsoft/G42 Olkaria: a KenGen press release, `mw: None`, "stalled"). Documented clean firm is two (Susquehanna, Hydro-Québec). Change: "two documented clean-firm arrangements and three reported ones" and keep the bar at 5 with the legend unchanged.

**F3 — `dedicated_supply_method.md` was not updated after the reclassification. Fix before send.**
It still reads grid_only 17, dedicated_fossil 9, bring_your_own 2, confidence medium 14 / low 11; has no `system_fossil_dc_driven` category; and still lists Greenlight among "α = 1 rows … with a regulator or permit document behind it". README says "Six rows reclassified"; eight rows carry `review_note`. Change: rewrite the Categories and Counts sections from the JSON (19/5/5/4/3/3/2/1/1; 18/12/13), add the new category with its α rule (0 at site, incremental at cluster), and say "seven reclassified, one confidence lowered".

**F4 — Attributional vs consequential (my 2.5). Caveat, still open.**
The brief's method paragraph gives the α formula and "your 5.11.0 facility Scope 2 pattern with one added field"; neither it nor `attribution_method.md` says whether the headline is attributional (average factor) with the dedicated-supply fields enabling a separately reported consequential variant. One sentence.

### G. Package hygiene and README

**G1 — Files referenced but not in the package directory. Blocks send (or delete the references).**
Referenced in the brief: `climate_trace_matches.csv`, the nearest-generation "second file". Referenced in `VIRGINIA.md`: `va_permits.csv`, `va_generator_rows.csv`, `virginia_nearest_generation.csv`. Referenced in `TEXAS.md`: `tx_permits.csv`, `tx_index_rows.csv`, `tx_unmatched_tceq_packages.csv`. None is in `data/climate_trace_seed/`; they exist only in `[a local working copy]` (older copy, 20:52). Change: copy them in or strip the references.

**G2 — README is the pre-Virginia README. Fix before send.**
It lists no Virginia, Texas or Climate TRACE series files; still says the backlog CSV holds "325 register-identified sites … awaiting permit extraction" (the CSV has 333 rows, as I noted last time; and the Virginia 183 are now extracted); still says "Six rows reclassified". Change: add rows for `VIRGINIA.md`, `VIRGINIA_REREAD_REPORT.md`, the three `va_*` CSVs, `TEXAS.md`, `CLIMATE_TRACE_SERIES.md`, the two `climate_trace_*` CSVs; fix 325 → 333 and "awaiting" → "Virginia extracted; Texas 17 matched".

**G3 — Texas: "57 matched, 12 with coordinates". Fix before send.**
`tx_permits.csv`: 57 is every name hit, including the 39 that `TEXAS.md` says are not datacenters ("fields cleared rather than trusted"). Verified datacenter matches are 17 (10 by known URL, 7 on the index). 12 with coordinates is right. Change: "17 verified matches (39 further name hits rejected), 12 with coordinates".

**G4 — Footer: "every figure on this page traces to a file in the attached package". Fix before send.**
False by the footer's own numbers (117 entries, 40 countries, 397 documents, 3 receipts are in no package file; README says "available on request"), by A2, D1, the 857, the Lawfare quote, and the Dominion 40 GW (ledger not shipped). Change: ship a ledger export (`north_america.json` et al. are 300 KB) and the footer is true; or delete the sentence.

**G5 — "Gavin said on Lawfare in April …". Caveat (cite it; fix the voice).**
The Lawfare URL exists in `registry/climate_trace_schema.json` but not in the package or `attribution_method.md`. And the page is going to Gavin: "Gavin said … that your database holds" in the third person, on a page addressed to him, reads oddly. Change: "You said on Lawfare in April (link) …", and put the URL in the method note. Keep "If it already covers this, tell us what it lacks", which is the right register.

**G6 — Commitments a named person must stand behind. Caveat.**
"We will keep the permits current and extend the same extraction to Singapore, Johor and Amsterdam next", "keep them current", "the ledger will fill that instead". `TEXAS.md` shows what a jurisdiction without a DEQ-style list costs. The sender should be willing to be held to this or soften to "we intend to".

**G7 — "A datacenter has no chimney". Caveat.**
The package's own Virginia count is 13,973 diesel units, 2,913 of them permitted for non-emergency running, plus Memphis and Southaven turbines. A combustion-side reviewer will enjoy that. Change: "almost no chimney of its own" or "its stack emissions are backup diesel; its footprint is the plant that serves it".

**G8 — "the one region where you would pilot". Caveat (tone).**
Presumes their roadmap. "the region we would pilot" or "a natural pilot region".

### H. Earlier findings: status

| Earlier | Status |
|---|---|
| 1.1 cite η | fixed (Cat 3516C spec cited) |
| 1.2 ÷1.2 headline | fixed (bounds table, brief rewritten); E2, E3 remain |
| 1.3 DUB14/15 "agrees" | fixed |
| 1.4 cap vs sum | fixed (both carried); E4 reproducibility |
| 1.5 97% Dublin | withdrawn in benchmark, still used in §4 procedure → E3 |
| 1.6 P1171 | notes now say stacks are 700 m from P1186; still `operating` low; acceptable |
| 1.7 16 vs 17 | fixed in brief |
| 2.1–2.8 worked rows | withdrawn; honestly stated in brief and README |
| 3.1 Chesterfield | reclassified |
| 3.2 Wisconsin | reclassified, low; brief C3 still overclaims |
| 3.3 Nevada | confidence lowered, docket not linked; brief F2 still says "documented" |
| 3.5 Vantage DUB13 | reclassified grid_only |
| 3.6 Greenlight/Batam/Lagos | reclassified; Greenlight to the wrong category and the AESO policy row collaterally → F1 |
| 4.1, 4.2, 4.3, 4.5, 4.6, 4.7, 4.8, 4.10 | fixed |
| 4.9 "for the load" | fixed for Chesterfield; C3 for Wisconsin |
| 4.12 backlog 325/333, "eight opened" | "eight opened" gone; 325 still in README → G2 |
| 4.13 footer / "every figure traces" | unchanged → G4 |
| 4.14 Gavin quote uncited | now "on Lawfare in April", still uncited → G5 |
| 2.5 attributional vs consequential | unchanged → F4 |

### Summary by severity

- **Blocks send:** A1 (153/857 vs 182/13,973 on one page), C1 (the "Virginia" box is Ohio and West Virginia coal), D1 (nearest-generation sentence wrong three ways), G1 (referenced files absent).
- **Fix before send:** A2, A3, A4, A7, B2, B3, C2, C3, C5, E3, F1, F2, F3, G2, G3, G4.
- **Caveat:** B1, B4, B5, C4, C6, C7, E2, E4, E5, F4, G5, G6, G7, G8.
- **Fine:** A5, A6, E1, the re-read notes, the withdrawn rows, the review shipped unedited.

### What to do tonight, in order

1. Replace 153 and 857 with 182 and 13,973 in the handover list and the ask.
2. Clip or relabel the bounding box; remove "55% from coal" and "sits beside".
3. Rebuild or delete the nearest-generation paragraph; copy the referenced files into the package or strip the references; update the README table.
4. Fix the date (October 2026), the Dominion wording, "Microsoft the stated driver", "five documented clean-firm", "five utility system plants", the per-unit range, 181 → 182, "one parser bug" → "most of it to one bug".
5. Recategorise the AESO policy row and Greenlight; regenerate `dedicated_supply_method.md` counts from the JSON.
6. Delete the §4 "scale 97% … / 1.2" procedure sentence; delete or make true the footer's traceability sentence; cite Lawfare and write it in the second person.
7. Then send. The Virginia re-read, the Ireland bounds and the supply column are worth their attention.

_Local file paths in this review were replaced with repository-relative paths on 2026-10-22; nothing else was changed._
