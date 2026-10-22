# Review of the public "Compute Ledger" page, 22 Oct 2026

Reviewer: sceptical methodology reviewer, coalition side. Scope: the page as built (`site/index.html`, compiled 2026-10-21, byte-identical to `the published ledger page`). I checked it against the files it renders: `registry/guide.json`, `registry/standard.json`, the static text in `site/build_page.py`, the 117 entries in the six registry files, and the three receipts. I compared all of it with the corrected package (`data/climate_trace_seed/` README, VIRGINIA, TEXAS, CLIMATE_TRACE_SERIES and dedicated_supply_method, plus `brief.html` and `review_2_final.md`). The built page's embedded data matches the current registry files exactly. No web checks were made.

## Verdict: fix, then link

Most of the entries hold up, and most of them carry their own caveats honestly. The page's own prose does not. The guide's why and ask text, the standard's notes and status labels, and the lede and method were written before verification, and they say more than the entries do. A Climate TRACE reader following the brief's link will hit five things within minutes:

1. **The Virginia entry.** This is the page's only home for the package's headline number. It still carries the per-unit range the package corrected. It says Dominion's 40 GW is "contracted". Its check note says the generator counts "remain third-party (PEC) tallies, not DEQ figures". It links the 33.7 GW to the pipeline code that produced the superseded 19,186 MW reading.
2. **The Chesterfield headline card** says "~40 GW of contracted data center capacity".
3. **The Ireland benchmark entry** still carries the withdrawn "97% … in Dublin".
4. **Microsoft and Wisconsin gas.** The guide sets Microsoft beside the Wisconsin gas build "about the same site", but the package marks that link as press-sourced and classes the plant as a utility system plant.
5. **The Middenmeer headline card** calls Microsoft's reported 84 million litres "the 2021 metered figure". The receipt says it is not known who metered it.

Behind those five, the standard claims "every requirement … is already met" and "each is met somewhere" while its own notes say otherwise. Ten of its twelve proof lists include at least one counter-example, a press-only entry, or an entry that does not meet the requirement. One of these is an Irish rule that may itself produce new on-site gas. Several guide sentences are contradicted by the ledger's own document-grade entries:

- "usually well under one job per megawatt"
- "the audited figures count what is on site"
- "three to five years later it is e-waste"

Every fix below is a text edit to JSON or the page template; none needs new research. Apply the blocks-send and fix-before-send items, rebuild, then reread the rendered Virginia, Chesterfield, Ireland CSO, Middenmeer and Wisconsin entries and the standard section before linking. If that cannot be done before the send, send the brief without the ledger link.

Severity: **blocks send** | **fix before send** | **caveat** | **fine**.

---

## A. Blocks send

### 1. Virginia generator entry is stale against the package and links to the defective pipeline. **Blocks send.**

File: `registry/north_america.json`, `us-va-loudoun-diesel-backup-generators`.

- `record`, last clause: "per-unit 1.5-3.7 MW". The package corrected this (review_2 A4, VIRGINIA.md). The 1.5–3.7 is a site-average range with the wrong minimum. Actual: site-average 0.4–3.7 MW, median 2.5; individual units from 250 kW.
- `record`, earlier: "Press accounts citing PEC tallies of DEQ permits count ~9,000 data center generators statewide". This now sits beside 13,973 units with nothing reconciling the two.
- `gap`: "…of the same order as the roughly 40 GW Dominion reports as contracted." The package says "in various stages of contracting" (company statement via DCD, not an SCC filing). It adds that 33.7 GW permitted implies roughly 28–33 GW of design load under N+1 and about 17 GW under 2N, and that permitted is not built.
- `verification_note`: "generator counts remain third-party (PEC) tallies, not DEQ figures." This contradicts the entry's own record, and it sits under a "verified against primary" tag. That tag predates the new figure, which is the ledger's own extraction.
- `record_sources[0]`: "Virginia DEQ issued air permits for data centers (statewide list) and permit PDFs, extracted by the Compute Ledger pipeline", linked to `…/compute-ledger/tree/main/pipeline`. Per VIRGINIA.md, the pipeline is the reader that gave 19,186 MW and was wrong in 129 permits. The 33,693 MW comes from the independent second reading. The DEQ list itself is not linked.

Replacements:

- `record`, replace from "On 2026-10-21…" to the end with: "On 2026-10-21 the Compute Ledger opened the permits on DEQ's statewide list of issued datacenter air permits and read each a second time by an independent method, resolving every disagreement against the permit text: 182 sites, 13,973 permitted standby generator units, 33,693 MW (band about 33.4–33.9 GW; 177 sites high confidence; median site 129 MW; largest 1,331 MW; site-average unit size 0.4–3.7 MW, median 2.5 MW; 2,913 units permitted for non-emergency use). This supersedes the PEC-based tallies above. Permitted is not built: many permits cover phases not yet constructed."
- `gap`: "DEQ publishes the permits but no consolidated total. The ledger's two-reading extraction gives about 33.7 GW of permitted standby across 182 sites. Standby is sized to design load with redundancy, so this implies roughly 28–33 GW of design load under N+1 and about 17 GW under 2N. Dominion reported about 40 GW of datacenter capacity 'in various stages of contracting' as of December 2024: one utility's pipeline, set against a statewide permit list. The two figures are of the same order."
- `verification_note`: "DEQ memo APG-578 (Town Hall PDF) confirms the 14-calendar-day planned-outage provision but is dated 2025-10-01, not 2025-09-30 as in press; JLARC report page and summary confirm <4% of regional NOx and ~5,050 MW. The ~9,000 generator count is a press-reported PEC tally, superseded by the 2026-10-21 extraction (13,973 units). The extraction is the ledger's own reading of the DEQ permits and is documented in the re-read files; it is not covered by this check."
- `record_sources[0]`: replace with two sources.
  - The DEQ statewide list URL itself (publisher "Virginia DEQ").
  - "Compute Ledger: Virginia DEQ datacenter permits, resolved second reading (va_permits_resolved.csv, VIRGINIA_REREAD_REPORT.md)", linked to `…/blob/main/data/climate_trace_seed/va_permits_resolved.csv`. First confirm that path is pushed and public: no remote is configured in the local repo.

### 2. Chesterfield headline card: "contracted". **Blocks send.**

File: `registry/north_america.json`, `us-va-chesterfield-dominion-cerc-gas`, `gap` (rendered on the first card of the "What actually burns" panel): "Utility cites ~40 GW of contracted data center capacity, while the regulator's approval order declines to quantify the data center share of the need the plant serves."

The entry's own `claim` correctly says "in various stages of contracting". The gap converts it to "contracted", which is the exact correction the package made.

Replacement: "Dominion reported about 40 GW of datacenter capacity 'in various stages of contracting' (December 2024, company statement via DCD); the SCC's approval order calls datacenter development 'not an insignificant contributing factor' but gives no datacenter MW for the need the plant serves."

### 3. Ireland benchmark entry still carries the withdrawn 97% Dublin share. **Blocks send.**

File: `registry/europe.json`, `ie-national-cso-share-2025`, `claim`: "none found (no single operator claim applies to the national figure); CRU notes 97% of Irish data centres are located in Dublin."

The package withdrew this figure (review_of_this_handover 1.5; ireland_regional_check §4). No CRU document gives it, and the cited source is a Matheson summary. This entry is the "bills" headline and the benchmark the brief's Ireland section rests on.

Replacement `claim`: "none found (no single operator claim applies to the national figure)." Drop the Matheson `claim_sources` row. If a regional figure is wanted, add EirGrid's Dáil answer (8 May 2024: 14 of 16 transmission-connected data centres in Dublin) as a record source and state it as that.

### 4. Microsoft placed beside Wisconsin gas "about the same site". **Blocks send.**

Files and text:

- `registry/guide.json`, fuel `why[1]`: "…a 1.2 GW gas build in Wisconsin, … Each sits beside the operator's public statement about the same site."
- `registry/north_america.json`, `us-wi-mount-pleasant-microsoft-we-energies`, `gap`: "Operator's public claims focus on water (closed-loop pilot); the regulator-approved supply additions are ~1,228 MW of new gas capacity plus a proposed $1.8B gas plant purchase."

What the package says:

- The entry is medium/partial. The PSC case page confirms 1,100 MW at Oak Creek and does not name Microsoft.
- The 128 MW Paris unit, the Microsoft contract terms and the Red Oak Ridge purchase are press-sourced.
- The package classes the plant as `system_fossil_dc_driven`: alpha 0 at the site, confidence low.
- The brief says "1,100 MW … data-center load the stated driver; Microsoft's 15-year contract is press-sourced".

The guide's "1.2 GW" adds the press-only Paris unit. "Regulator-approved supply additions" for Microsoft's site goes further than the PSC record.

Replacement for fuel `why[1]`, which also covers finding 10:

> "The clearest records in the ledger are regulator orders and permits: a 944 MW gas peaker approved in Virginia, with datacenter growth named as a contributing factor; 15 turbines (247 MW) permitted in Memphis in July 2025 after xAI had run turbines on site for about a year under an exemption it claimed; a 41-turbine, 1.2 GW plant reported permitted across the state line in Mississippi (press; the state's order retiring 69 temporary turbines is in the ledger); 1,100 MW of gas approved in Wisconsin with datacenter load the utility's stated driver (its link to Microsoft's Mount Pleasant site is press-sourced); and three Entergy gas plants approved for Meta's site in Louisiana (2,262 MW as reported from Entergy's filings). Each entry sets the record beside what the operator says in public."

Replacement Wisconsin `gap`: "We Energies cited 'energy-intensive data centers' for 1,100 MW of simple-cycle gas at Oak Creek, approved by the PSC in docket 6630-CE-317; the PSC case page does not name Microsoft, and the Paris unit, the Microsoft contract terms and the Red Oak Ridge purchase are press-sourced. Microsoft's public claims for the site concern water."

### 5. Middenmeer: "metered" and "municipal audit". **Blocks send.**

Files and text:

- `registry/europe.json`, `nl-middenmeer-microsoft-water`, `gap` (rendered on a "Water" headline card): "The 2021 metered figure is 4.2 to 7 times the figure given to residents the same year…"
- `registry/guide.json`, water `why[1]`: "…Middenmeer after a municipal audit."

The receipt contradicts both. It says (limits, and §"Who metered the 84 million litres"): "Press describes the 84 million litres as reported by Microsoft to the municipality, not as a PWN meter reading". The figure itself is [press], and the entry is medium/not_found. No audit appears anywhere in the receipt. The figure came out through Microsoft's report to the municipality, the newspaper and a Wob request. This is a named company, on a headline card, contradicted by the sender's own receipt.

Replacement `gap` opening: "The 2021 volume Microsoft reported to the municipality (84 million litres [press]; who metered it is not documented) is 4.2 to 7 times the figure given to residents the same year; …" Keep the rest unchanged.

For the water `why[1]` replacement, see finding 8.

---

## B. Fix before send: guide and page prose

### 6. Lede overclaims. **Fix before send.**

File: `site/build_page.py`, lede: "Nothing here is an opinion; every number links to the document it came from."

The guide and standard prose holds opinions ("the most important", "among the most subsidised buildings on earth", "decorative") and numbers with no link (99%, 60 times, 70%). The 33.7 GW links to code, not a document.

Replacement: "Each entry lays the public record beside what the operator or government says in public, links every figure to the document it came from, and marks figures confirmed only through press reports of the document. The theme introductions and the standard are the ledger's own summaries of those entries. Good cases are entries too." This replaces both sentences from "Each entry lays…" to "…Good cases are entries too."

### 7. "Your electricity bill" theme. **Fix before send.**

File: `registry/guide.json`, key `bills`.

- `ask[0][1]`: "Ohio and Ontario have written minimum-payment rules; most places have not."
  - Ontario has no minimum-payment rule in the record. Bill 40 restricts connections pending regulation, and the Playbook is a proposal. The cost-responsibility statement "is not in the ERO notice and is attributed to Torys" (entry vnote).
  - Ohio's 85%, 25 MW and 12-year terms are press-sourced (partial).
  - Virginia's SCC order in the Chesterfield entry does create a large-load class with minimum demand charges, at document grade.

  Replacement: "Ask the utility commission docket whether large-load customers carry their own transmission and generation costs, or whether they are socialised. Virginia's regulator (in its November 2025 Chesterfield order) and Ohio's have adopted minimum-demand terms for large loads; Ontario has legislated connection restrictions and proposed a separate rate class. Most places in the ledger have not."
- `ask[1][1]`: "In regions with a capacity market, the market monitor's report says how much of the clearing price is attributable to datacenter load. That is the closest thing to a receipt for a bill increase."
  - Only PJM's monitor has done this.
  - It attributed auction revenue, not clearing price, in a counterfactual.
  - The entry's gap says "not an audited bill impact; PJM's own report does not quantify a datacenter share".
  - "Receipt" is the page's term of art for document-grade cases.

  Replacement: "In PJM, the independent market monitor has estimated, as a counterfactual, how much capacity-auction revenue is attributable to datacenter load ($16.6 billion across two auctions). PJM has not adopted the figure, and it is an estimate of market revenue, not a measured bill impact."
- `ask[2][1]`: "Legislative auditors in Virginia and Georgia have modelled bill impacts and jobs." No Georgia bill-impact model is in the ledger.

  Replacement: "Virginia's legislative auditor (JLARC) has modelled residential bill impacts ($14–37 a month by 2040 under unconstrained demand) and counted jobs; Georgia's audit office has evaluated its sales-tax exemption's cost and jobs. Both reports are public."
- `why[1]`, "The record on this is thinner than it should be" is a caveat (tone). Replacement: "The record on this is thin."

### 8. "Water" theme. **Fix before send.**

File: `registry/guide.json`, key `water`.

- `why[0]`: "Most datacenters cool with water because it is cheap. Evaporative cooling in a dry basin takes drinking water out of the ground and sends it into the air. … it is usually only disclosed when a court or a council forces it." No entry supports "most", "because it is cheap", "out of the ground" as a general rule, or "usually".

  Replacement: "Many datacenters cool with water. Evaporative cooling consumes water, and in a dry basin that water may come from the same aquifers or reservoirs as drinking supply. Air cooling uses more electricity and little water. Which one a site uses is a design choice, and in the cases in this ledger the volume became public only through a court, a council or a records request."
- `why[1]`: "The Dalles after a lawsuit, Uruguay after a court order, Chile after an environmental tribunal, Middenmeer after a municipal audit."
  - Chile: the 169 L/s was in the 2020 RCA, reported by CIPER in May 2020. The tribunal (2024) partly annulled the approval; it did not release the number.
  - Middenmeer: no audit (finding 5).
  - The Dalles: the city sued the requester, and the records came out at settlement.

  Replacement: "The ledger holds the cases where the number got out: The Dalles after the city's lawsuit against a reporter was settled, Uruguay after a court ordered disclosure, Chile in the environmental approval that a tribunal later partly annulled, Middenmeer after a regional newspaper published the figure Microsoft had reported to the municipality. It also holds the designs that changed afterwards."
- `ask[0][1]`, "Withdrawal permits are public in most jurisdictions" is an unsupported generalisation (caveat). Replacement: "Withdrawal permits are public in many jurisdictions."

### 9. "What actually burns" blurb and asks. **Fix before send.**

File: `registry/guide.json`, key `fuel`.

- `blurb`: "Gas plants, diesel generators and turbines attached to sites that are described as clean."
  - Chesterfield and Oak Creek are utility system plants, not attached to a site.
  - xAI does not describe its sites as clean: its claim is "lowest emitting of its kind".

  Replacement: "Gas plants, turbines and diesel generators built or approved for datacenter load, beside what the operator says about the same site."
- `ask[0][1]`: "Every site must permit its backup generators. The permitted capacity is the truest public number for how big a site is…"
  - The package's own Virginia and Ireland work says permitted standby is an upper bound on design load (N+1 or 2N), and that permitted is not built.
  - "Truest" is an adjective doing a finding's work.
  - "Every site must" is not true in every jurisdiction.

  Replacement: "Large standby generator fleets need an air permit in most jurisdictions, and the permit lists each unit. Permitted capacity is an upper bound on a site's design load, not its load: generators are sized with redundancy, and permits often cover phases not yet built. It is often public before any announcement."
- `ask[1][1]`: "Grid operators publish what is waiting to connect…" The page's own "What is not published" box says Texas and Great Britain do not.

  Replacement: "Some grid operators publish what is waiting to connect and, for generators, what fuel (PJM, MISO, SPP and NYISO do). Texas and Great Britain publish no project-level file of large-load requests. Load growth with gas attached shows up in these queues and in utility resource filings."

### 10. xAI wording. **Fix before send.**

File: `registry/guide.json`, fuel `why[1]`: "15 turbines permitted in Memphis after a year of unpermitted running, 41 more across the state line".

- Memphis: the entry records that xAI claimed a 364-day nonroad exemption, and that "the local regulator and EPA's later rule text differ on whether trailer-mounted turbines were exempt". The brief's own wording is the neutral "ran its own turbines for a year before its 247 MW permit".
- Southaven: the 41-turbine, 1.2 GW permit was not retrieved (medium/partial, press). The document-grade fact is the Agreed Order on 69 temporary turbines.

Replacement: covered in the finding 4 text. The standard's matching phrase "turbines run for a year before permitting in Memphis" is acceptable.

### 11. "The grid queue" theme. **Fix before send.**

File: `registry/guide.json`, key `grid`.

- `why[0]`: "Across every region with public data … roughly 60 times in Texas … Most of it will never be built."
  - "Every region" is contradicted by the ledger's own Amsterdam entry (about 150 MW contracted against a 100 MW peak).
  - The Texas ratio is all large loads (about 90% datacenters), and its 7.5 GW denominator comes from BIC Magazine (press).
  - Paris is transmission-connected capacity only.
  - "Most of it will never be built" is a forecast with no source.

  Replacement: "Where grid operators publish both numbers, the load asking to connect is many times what is connected: about 474 GW of large-load requests in Texas (about 90% datacenters) against about 7.5 GW of large load connected, roughly 60 times; about 15 GW in the Paris region's connection pipeline against 640 MW connected to the transmission network, about 23 times; 5.9 GW of contracted maximum demand in Malaysia against 405 MW of recorded load, about 14 times. Operators report high attrition (AEMO: 36% of projects in its 2025 forecast cancelled). Grids plan, and sometimes build, against the queue."
- `why[1]`, caveat:
  - "Ireland requires sites to bring their own dispatchable supply" applies only to sites of 10 MVA or more.
  - "rationed" is loaded.

  Replacement: "…Ireland requires new sites of 10 MVA or more to bring dispatchable capacity equal to their import, Singapore paused new capacity and now allocates it by call for applications, Israel froze new applications for 140 days, Texas ordered an audit, Amsterdam removed its growth allowance…"
- Entry `us-tx-ercot-large-load-queue-audit`, `gap` (headline card): "the regulator itself describes the queue as partly speculative". The record contains no such statement from ERCOT or the PUCT.

  Replacement: "Queue requests (~474 GW) exceed connected large load (~7.5 GW, press-reported) by roughly 60x; ERCOT found ~205 GW preliminarily eligible for its first batch, none of it approved to energize as of August 2026, and the audit is pending."

### 12. "Public money and jobs" theme. **Fix before send.**

File: `registry/guide.json`, key `money`.

- `why[0]`: "Datacenters are among the most subsidised buildings on earth and among the least staffed. A hyperscale campus can receive hundreds of millions in sales-tax exemptions and employ a few dozen people once built. … the audited figures count what is on site."
  - The superlatives are unsourced advocacy.
  - No entry records one campus receiving "hundreds of millions" (JLARC: median $5.4 million per company).
  - "A few dozen people" is contradicted by Abbots Langley (201 FTE operational) and Alto Jahuel (about 307 operating staff).
  - "Audited figures count what is on site" is contradicted twice. JLARC counts about 74,000 jobs a year including construction and indirect jobs. Georgia's figures are model outputs, and the receipt says "No public count of jobs actually created at certified data centers was found."

  Replacement: "Datacenter tax exemptions are large and the jobs attached to them are hard to count. Virginia's legislative auditor put the sales-tax exemption at about $929 million in FY2023 and counted more than 8,000 operations jobs alongside construction and indirect jobs; Georgia's evaluation reports model estimates, not head-counts. Announcements and evaluations alike usually include construction and indirect jobs; ask for the permanent on-site figure."
- `why[1]`: "Georgia's auditor cutting its own job estimate by 70% while the cost stood".
  - The receipt shows the revised figures are exactly the evaluation's 30% attribution applied: the originals were totals for all datacenter activity. No reason was given for the revision.
  - The estimate was the Carl Vinson Institute's evaluation, summarised by DOAA, not the auditor's "own".
  - "While the cost stood" implies an inconsistency that does not exist. Forgone revenue is the whole exemption whatever share is attributable.
  - Brazil: R$7.25 billion over 2026–28.

  Replacement: "The ledger records the evaluations: Virginia's $928.6 million in FY2023 sales-tax savings; Georgia's audit office reissuing its summary with job figures at 30% of the originals, the share of activity its evaluator attributes to the exemption (the originals counted all datacenter activity), with the $474 million FY2025 cost unchanged and no reason given; Brazil's official estimate of R$7.25 billion in forgone revenue for 2026–28, with no job commitment attached."
- `ask[1][1]`: "Their reports are the only independent count of jobs and cost." Georgia's are model estimates, and the Texas SAO audit has no job figures.

  Replacement: "State and national auditors evaluate these programmes. Their reports are the main independent estimate of jobs and cost; in the ledger they are model estimates, not counts of people on site."
- `ask[2][1]`: "It is usually well under one job per megawatt." The ledger's own document-grade entries say otherwise:
  - JLARC: more than 8,000 operations jobs against about 5,050 MW statewide.
  - Abbots Langley: 201 FTE for 96 MW IT.
  - Alto Jahuel: about 307 staff for a 92.7 MW substation.

  Replacement: "Divide the permanent on-site jobs by the site's capacity, and compare with what the incentive costs. The ledger's records do not support a single rule: Virginia's auditor counts more than 8,000 operations jobs against about 5,050 MW statewide, and English and Chilean planning records give 201 jobs for 96 MW and about 307 staff for a 92.7 MW substation."

### 13. "Land, noise and neighbours" theme. **Fix before send.**

File: `registry/guide.json`, key `land`.

- `why[0]`: "A campus takes hundreds of hectares … runs cooling fans and generators around the clock … either enforceable or decorative."
  - Abbots Langley is about 31 ha.
  - Generators do not run around the clock. The package treats them as standby, with 2,913 Virginia units permitted for non-emergency use.
  - "Decorative" is an adjective doing a finding's work.

  Replacement: "A hyperscale campus can take tens to hundreds of hectares of farmland or green belt (about 31 ha at Abbots Langley; 2,100 acres in the voided Prince William rezoning), runs cooling plant around the clock, tests its backup generators on a schedule, and sits next to people. Planning records are where land take, biodiversity conditions and noise limits are written down, and where it shows whether a condition has a metric, a monitoring duty and an enforcement body."
- `why[1]`: "a noise ordinance in Arizona that mandates studies nobody has published." The entry says only "no city-published results … were found".

  Replacement for that clause: "a noise ordinance in Arizona that requires annual third-party studies whose results the city has not published."
- `ask[2][1]`, caveat: "Most ordinances cap dBA. The complaints are usually about low-frequency tonal noise". The ledger has two ordinances, and Chandler sets no dB figure.

  Replacement: "The ordinances in the ledger cap dBA or set no number. Loudoun County reports that complaints often involve tonal noise and that it has no rule specific to tonal or low-frequency noise. Ask whether your standard addresses it."

### 14. "What good looks like" theme. **Fix before send.**

File: `registry/guide.json`, key `heat`.

- `blurb`: "…with the numbers to prove it." Several entries in the theme have no delivered figure:
  - Espoo: recovery starts in 2027.
  - Seattle: 2015 projections, not_found.
  - EcoCloud: not_found.
  - Teraco: plant not commissioned.

  Replacement: "Sites and rules where the record shows a practice worth copying, and what has been measured so far."
- `why[0]`, last sentence: "all of it is documented somewhere in this ledger with a published figure." Replacement: "all of it is documented somewhere in this ledger, some with a delivered figure and some still as a plan."
- `why[1]`: "Uruguay's court order produced a redesign that cut stated water use by 99%." The court ordered disclosure. The record shows the redesign followed, not that the order produced it. The 99% compares a two-building design with a one-building redesign. The entry is labelled high, but all four of its sources are press (see finding 30).

  Replacement for the last three sentences: "Stockholm's half-municipal utility publishes recovered heat in its statutory annual report. The state energy agency publishes cumulative MWh for Tallaght's council-owned network. Denmark made surplus-heat analysis mandatory for new and substantially renovated sites above 1 MW. In Uruguay, after a court ordered the water figures released, Google redesigned the project as one air-cooled building stating 48 m³ a day, against 7,600 m³ a day of potable water in the original two-building design."

### 15. "The hardware chain" theme. **Fix before send.**

File: `registry/guide.json`, key `chain`.

- `why[0]`: "A GPU is cobalt from Congo … Three to five years later it is e-waste … The rest is tracked, when it is tracked at all, by GPS beacons hidden in discarded equipment."
  - The ledger's own filings entry gives five-to-six-year accounting lives and "No public filing stating a physical lifespan for GPUs".
  - GPS trackers are an advocacy group's sample studies, not how "the rest" is tracked.

  Replacement: "The hardware in a datacenter draws on cobalt mined in Congo, copper from Chile, nickel from Indonesia, rare earths from Myanmar and gallium refined in China, and on chip fabs that need water in Taiwan, with labour at every step. Companies depreciate servers over five to six years in their filings, and no filing states a physical life for a GPU. The world formally collects less than a quarter of the e-waste it generates; what happens to much of the rest is known mainly from sample studies, including GPS trackers an advocacy group placed in discarded equipment."
- `why[1]`: "the least documented and the most important, because it is where the cost gets exported to places with the weakest records." This is opinion.

  Replacement: "This end of the ledger is the least documented, and the gaps fall where public records are thinnest. It holds what the UN, the USGS, the Basel Convention and national regulators have published, and it says plainly where nothing has."
- `ask[2][1]`, caveat: "The gap between them is the undeclared flow." Replacement: "A gap between them is a question for the customs and environment agencies; it can reflect undeclared flows or differences in classification."

---

## C. Fix before send: the standard (`registry/standard.json` and the status labels in `site/build_page.py`)

Proof grade per requirement. "Doc" means the entry is high or verified and its sources are a regulator, court or statute.

| # | Requirement | Page label | proven_by and grade | What actually meets it at document grade | Label it should carry |
|---|---|---|---|---|---|
| 1 | disclose | met somewhere | EU EED (doc; aggregate only, and the page's own box says there is no per-site data); EnEfG (verified; register reporting per a TÜV summary, publicness not shown); The Dalles (high label, record sources all press; binds the city, on request) | nothing site-level, public and metered | met in part |
| 2 | water | met somewhere | Uruguay (high label, all-press sources); Cerrillos (doc; approval annulled, air-cooled design announced, not filed); Hamina (seawater is Google's statement); Amsterdam (doc); Pecém (medium/partial; volumes press; licensing contested by federal prosecutors) | Amsterdam policy; Uruguay revised EIA (press-reported) | met somewhere; drop Pecém |
| 3 | heat | met somewhere | Stockholm (doc; combined figure); Tallaght (verified); Espoo (company release; no delivered MWh until 2027); Denmark BEK 1167 (doc); EnEfG (verified) | Tallaght, Denmark, Germany | met somewhere; drop Espoo |
| 4 | supply | met somewhere | Nevada (medium/partial; approval and 115 MW press-only); Susquehanna (doc; existing plant, not additional); Québec (doc; allocation by decree, tariff only proposed); EcoCloud (medium/not_found); CRU (high label; law-firm summary plus the proposed decision); Teraco (medium/not_found; company release) | Québec allocation; CRU obligation | met somewhere; mark three as reported |
| 5 | no_gas | met somewhere | Vantage refusal (doc); CRU policy (doc, but it *requires* on-site dispatchable generation of unprescribed fuel); Haarlemmermeer ruling (doc; congestion, not fossil) | Vantage refusal only | met somewhere; drop CRU and Haarlemmermeer |
| 6 | cost | met somewhere | Ohio (medium/partial; terms press); Ontario (verified; no cost rule in statute); Québec (tariff proposed, not ordered); PJM IMM and JLARC rates (counter-evidence, not proof) | none as listed. The SCC Chesterfield order (in the ledger, not listed) creates a large-load class with 14-year contracts and 85/85/60% minimum demand charges | met somewhere only if Chesterfield is added; otherwise met in part |
| 7 | land | met somewhere | Abbots Langley, Zeewolde, Amsterdam (all doc) | all three | met somewhere |
| 8 | noise | met in part | Chandler (doc), Loudoun (verified) | ordinance yes, results no | met in part |
| 9 | money | met in part | Georgia DOAA and JLARC (doc); Uttar Pradesh and Redata (doc, but both show *no* jobs condition: counter-examples) | the evaluation half only | met in part; move Uttar Pradesh and Redata out |
| 10 | hardware | met in part | Microsoft (rate not assured); hyperscaler filings (medium/partial); USGS cobalt (shows cobalt is *not* covered) | nothing | not yet met |
| 11 | forecast | met somewhere | AEMO (doc); REE (doc; granted access only, "requested" is press); RTE IDF (doc); CSO Ireland (consumption, not a forecast or queue) | AEMO, RTE | met somewhere; drop CSO |
| 12 | upstream | met somewhere | Cochilco (doc); SQM/SMA (verified); TSMC (medium/partial; unit water up 14.3% against target, a counter-example) | Cochilco, SMA | met somewhere; drop TSMC |

No proof rests on a low-confidence entry. Seven rest on medium entries that are partial or not_found (Ohio, Nevada, Pecém, EcoCloud, Teraco, the hyperscaler filings, TSMC). Two more rest on high-labelled entries whose sources are press only (Uruguay, The Dalles).

### 16. Intro, how-to-read, closing and status labels contradict the notes. **Fix before send.**

- `intro`: "Every requirement below is already met by a real site or written into a real rule somewhere in this ledger … Nothing here is a wish. … rather than judged as a sin." The hardware note says no company meets it, and the money note says the condition "does not" exist. "Judged as a sin" is moralising.
- `closing`: "Each is met somewhere. None is met everywhere, and three … are met only in part anywhere." This contradicts itself within one sentence.
- `how_to_read`: "'Proof' always means a document someone outside the operator produced or assured." This fails for Hamina, Teraco, EcoCloud and Nevada.
- `build_page.py`: `const HALF=new Set(['noise','money','hardware']);` hard-codes "met somewhere" for everything else.

Replacements, assuming Chesterfield is added to `cost` (finding 22):

- `intro`: "Every requirement below is drawn from a practice or a rule that exists somewhere in this ledger, with the document that shows it. Eight are met somewhere by a site or a binding rule; three are met only in part; one, assured hardware reuse, is not yet met anywhere in the record. The standard is the sum of practices that exist today, assembled in one place so that any site can be measured as a distance from it. Where a requirement is met by a rule rather than a site, the rule is cited; where the record shows the practice but not yet the measured result, that is said; where a proof rests on a press report of the document, the entry is marked."
- `how_to_read`: "Each requirement names what to ask for, what counts as proof, and which entries in the ledger show it being done. 'Proof' means a document someone outside the operator produced or assured; an entry listed under a requirement that rests on press reports or company statements is marked 'partly verified' or 'primary not found'."
- `closing`: "Twelve requirements. Eight are met somewhere; three (site-level disclosure, noise results, jobs clawbacks) only in part; one (assured hardware reuse) nowhere yet. None is met everywhere. A site that meets all twelve does not exist yet."
- `build_page.py`, replace the `HALF` line and the status span with:

  ```js
  const STATUS={disclose:'part',noise:'part',money:'part',hardware:'none'};
  ```

  ```js
  <span class="status ${(STATUS[r.key]||'met')==='met'?'met':'half'}">${({met:'met somewhere',part:'met in part',none:'not yet met'})[STATUS[r.key]||'met']}</span>
  ```

### 17. `disclose`: The Dalles settlement binds the city, not Google. **Fix before send.**

`note`: "The Dalles settlement binds one operator at one site to annual disclosure."

The receipt (T15) says: "City to … disclose future annual data on request". Google is not bound. The terms are [press], and the settlement PDF was not read. This is a named-company misstatement, even though it is a favourable one.

Replacement `note`: "The EU register exists, but per-site data sit behind an operator login and only an aggregate report is public; only 36% of in-scope sites reported in the first period. Germany's law requires reporting to a national register. At The Dalles, a settlement between the city and a newspaper released ten years of Google's annual water use and commits the city to disclose future annual figures on request ([press]; the settlement text was not read). The rule is written; public site-level disclosure is not yet practice anywhere in the ledger."

### 18. `water`: "permits and policies, not promises". **Fix before send.**

`note`: "Hamina cools with seawater. … These are permits and policies, not promises."

- Hamina's seawater cooling is Google's statement.
- Uruguay's 48 m³ is a press report of the revised EIA.
- Cerrillos has an announced design and no filing.
- Pecém's 18–30 m³/day is press, and its licensing is before a federal court on EIA and ILO 169 grounds. Holding up a ByteDance-linked project as proof of good water practice while federal prosecutors contest its licence would embarrass the sender.

Replacement `note`: "Uruguay's redesign states 48 m³ a day for one air-cooled building, against 7,600 m³ a day of potable water in the original two-building design (revised EIA, as reported in press). Amsterdam's siting policy prohibits groundwater extraction. Noord-Holland's provincial strategy records that its water company in practice now connects datacenters for office use only. Google states that Hamina cools with seawater. In Chile an environmental tribunal partly annulled the approval of a groundwater-cooled design in a restricted aquifer; Google has announced an air-cooled redesign that is not yet filed."

`proven_by`: remove `br-pecem-casadosventos-bytedance`. Add `nl-middenmeer-microsoft-water`, which holds the PWN office-use statement from the provincial strategy.

### 19. `heat`: Stockholm figure, Denmark scope, Espoo. **Fix before send.**

- `note`: "Stockholm's half-municipal utility reports 117 GWh of recovered heat". The entry says the figure "combines datacenters with other Öppen Fjärrvärme sources".
- "Denmark now requires every datacenter above 1 MW…" The order applies only when a site is built or substantially renovated.
- The 1.8% figure covers only the 36% of sites that reported.
- `proven_by` includes `fi-espoo-kirkkonummi-microsoft-fortum-heat`, which has no delivered figure until 2027. Its sole source is a Fortum press release, yet it is labelled high.

Replacement `note`: "Stockholm's half-municipal utility reports, in its statutory accounts, 117 GWh of heat recovered in 2023 from Stockholm Data Parks and other Öppen Fjärrvärme sources combined. SEAI publishes cumulative MWh and tonnes for Tallaght's council-owned network. Denmark requires datacenters above 1 MW that are built or substantially renovated to analyse surplus heat and use it unless infeasible; Germany sets 10% reuse for sites commissioned from July 2026, rising to 20%. Across the EU, the sites that reported in the first period (about 36% of those in scope) reused about 1.8% of their heat, so the gap between the rule and the practice is the distance to close."

`proven_by`: remove `fi-espoo-kirkkonummi-microsoft-fortum-heat`.

### 20. `supply`: Nevada, Susquehanna "additional", press-only proofs. **Fix before send.**

- `note`: "Nevada's regulator approved firm geothermal for a datacenter under a tariff stated not to shift cost to other customers." The entry is medium/partial: the PUCN notice "does not mention Fervo or 115 MW, and no PUCN order approving the CTT was found", and the ESA and PPA "still requir[ed] approval". The package downgraded Nevada to low and says "the honest count of documented clean-firm supply is two".
- `ask`: "…a contracted clean source that would not otherwise have been built (… existing nuclear restructured to pay grid charges)". An existing plant is, by definition, already built. The package's alpha rule 9 calls Susquehanna "existing, non-additional".

Replacement `ask`: "Electricity from a contracted firm clean source named in a regulator-approved agreement, preferably one that would not otherwise have been built (geothermal, a hydro allocation), or the obligation to bring dispatchable supply before connecting. Existing nuclear contracted front-of-meter, so that the load pays grid charges, is firm and clean but not additional. Annual renewable certificates do not meet this."

Replacement `note`: "Québec allocates hydro to datacenters by ministerial authorisation and scores projects on heat recovery; its proposed datacenter tariff awaits the Régie. Ireland requires new sites of 10 MVA or more to bring dispatchable capacity equal to their import, and all sites above 1 MVA to source 80% of annual demand from additional Irish renewables over six years. Amazon contracts up to 1,920 MW from the existing Susquehanna nuclear plant, restructured after FERC's rejection so that the load pays grid charges; it is firm and clean but not additional. In Nevada, Google and NV Energy filed a 115 MW geothermal supply agreement under a tariff stated not to shift costs to other customers; the approval and the 115 MW are confirmed only through press. Kenya's EcoCloud geothermal tariff and Teraco's wheeled solar rest on press and company statements. None of these has hourly matching verified by a third party on the public record; that is the next bar."

### 21. `no_gas`: the Irish connection policy is cited as proof against on-site gas. **Fix before send.**

- `proven_by` includes `ie-cru-leu-connection-policy-2025`. That policy *requires* new sites to install dispatchable on-site or proximate capacity equal to their import, and the entry's gap says the "fuel type (gas vs storage) is not prescribed". The same entry is cited under `supply` as "bring your own".
- `note`: "A Dutch court upheld the grid operator's right to pause connections rather than overbuild." This was summary proceedings on congestion; "rather than overbuild" is not in the record, and the case is not about fossil generation.
- "4,678 MW of gas in Pennsylvania" should say permitted, not built.

Replacement `note`: "Ireland's planning board refused a datacenter, among other reasons because without a grid agreement on-site gas could become its primary supply, contrary to the government's statement that 'islanded' datacenters are not in line with national policy. The counter-examples in the ledger (a 944 MW peaker approved in Virginia, turbines run in Memphis for about a year before the first permit, 4,678 MW of gas permitted but not yet built in Pennsylvania) are what this requirement is measured against. Ireland's connection policy requires new sites to bring dispatchable on-site capacity without prescribing the fuel, so it is listed under supply, not here."

`proven_by`: `["ie-dublin-vantage-dub13-abp-refusal"]`.

### 22. `cost`: Ontario statute, Ohio terms, PJM and JLARC framing. **Fix before send.**

- `note`: "Ontario wrote cost responsibility into statute." The entry's vnote says the cost-responsibility statement "is not in the ERO notice and is attributed to Torys"; Bill 40 restricts connections pending regulation.
- "Ohio requires…" states press-sourced terms as fact.
- "The PJM market monitor's $16.6 billion and Virginia's auditor's $14–37 a month are the measure of what happens without such rules." One is a counterfactual revenue estimate; the other is a 2040 projection under unconstrained demand.

Replacement `note`: "Virginia's regulator, in its November 2025 Chesterfield order, created a large-load class (above 25 MW) with 14-year contracts and minimum demand charges of 85%, 85% and 60%. Ohio's regulator approved a datacenter tariff in July 2025; press reports of the order give loads above 25 MW paying for at least 85% of subscribed capacity for up to 12 years (the order text was not retrieved). Ontario's Bill 40 lets regulations restrict large-load connections, and a proposed framework would put new datacenters in a separate rate class; Hydro-Québec has proposed a datacenter tariff that awaits the Régie. The PJM market monitor's counterfactual estimate ($16.6 billion of capacity-auction revenue across two auctions attributable to datacenter load) and Virginia's legislative auditor's projection ($14–37 a month on a typical residential bill by 2040 under unconstrained demand) are estimates of what is at stake without such rules."

`proven_by`: add `us-va-chesterfield-dominion-cerc-gas` first. Keep Ohio, Ontario and Québec. Remove `us-pjm-imm-capacity` and `us-va-jlarc-rates`, which are evidence of the problem, not proof of the practice; the note still cites them.

### 23. `land`: Zeewolde. **Fix before send.**

`note`: "The Netherlands confined hyperscale siting to two named areas by decree and the state refused to sell the Zeewolde land." Read together, this implies the decree stopped Zeewolde. The verified entry says "the rule expressly did not cover Zeewolde".

Replacement for that sentence: "The Netherlands confined new hyperscale datacenters to two named areas by national rule (draft approved June 2022; in force 1 January 2024, Stb. 2023, 492). That rule did not apply to Zeewolde, whose zoning plan was already adopted; there the state declined to sell the land the project needed, and Meta cancelled the campus in July 2022."

Two related entry fixes:

- `registry/people_land_money.json`, `nl-zeewolde-meta-land`, `record`: "The Eerste Kamer adopted a motion in Dec 2021 that the State may not sell land for large-scale datacenters". This overstates the motion. Replacement: "The Eerste Kamer adopted a motion on 21 Dec 2021 (35925 XIV, H) asking the government to have the Rijksvastgoedbedrijf suspend sales of agricultural land for hyperscale datacenters".
- `nl-zeewolde-meta-cancelled` still calls the rule a "draft decree". This is a caveat: add "(in force 1 January 2024, Stb. 2023, 492, per the Middenmeer receipt)".

### 24. `noise`. **Fix before send.**

`note`: "No city has yet published the results, and no ordinance in the ledger addresses tonal noise, which is what residents actually complain about." Only Chandler was checked, and the evidence on complaints comes from one county.

Replacement `note`: "Chandler, Arizona wrote baseline, post-construction and five annual third-party studies into its ordinance; no city-published results were found. Loudoun County reports that complaints often involve tonal noise, and states that it has no rule specific to tonal or low-frequency noise; amendments are anticipated in 2027. This requirement is met in part."

### 25. `money`: "70% overcount" and counter-examples listed as proof. **Fix before send.**

- `note`: "Georgia and Virginia at least evaluate their exemptions by law, which is how Georgia's 70% overcount came to light."
  - "At least" is tone.
  - "Overcount" goes further than the receipt, which says the originals equal the statewide totals for all datacenter activity, the revision equals the evaluation's 30% attribution, and no reason was given.
- `proven_by` includes `in-up-dc-policy-2026` and `br-redata-renuncia`. Both show the absence of a jobs condition, but they render as proof buttons.

Replacement `note`: "Georgia and Virginia evaluate their exemptions by statute. Georgia's evaluation attributes 30% of datacenter activity to the exemption; its audit office first summarised job figures for all datacenter activity, then reissued them at 30% with no stated reason. No programme in the ledger ties the money to a jobs floor with a clawback: Uttar Pradesh's 2026 policy and Brazil's Redata regime set none. This requirement is met only in its first half: the evaluation exists; the condition does not."

`proven_by`: `["us-ga-doaa-exemption-correction", "us-va-jlarc-sales-tax"]`.

### 26. `hardware`: Microsoft's figure misnamed; not met anywhere. **Fix before send.**

`note`: "Microsoft publishes a 90.9% reuse rate". The figure is a reuse-*and-recycling* rate for servers and components (entry record).

Replacement `note`: "Microsoft publishes a 90.9% reuse-and-recycling rate for cloud servers and components, with a method; its third-party review covers waste tonnage, not that rate. Companies state accounting lives for servers (five to six years) in their filings; none states a physical life for GPUs. No company in the ledger has an assured hardware reuse figure, and statutory conflict-minerals filings do not cover cobalt, nickel or rare earths. No site or rule in the ledger meets this requirement yet."

The label becomes "not yet met" (finding 16).

### 27. `forecast`: Texas number, CSO, REE. **Fix before send.**

`note` problems:

- "Texas, by contrast, publishes no file of its 445 GW queue." The ledger entry says ~474 GW (June 2026, ERCOT testimony). TEXAS.md says 445: align the package too (finding 37).
- "Ireland's statistics office meters the share." ESB Networks meters and the CSO publishes. CSO data is consumption, not a queue or a forecast.
- "Spain's grid operator maps granted and requested access." The "requested" figure is from trade press.

Replacement `note`: "Australia's AEMO publishes a project-reconciled forecast showing 67 GW in development, 27% connection utilisation and a 36% cancellation rate. RTE publishes, for the Paris region, connected datacenter capacity separately from capacity in the connection process and under study. Spain's grid operator publishes granted demand access by type and how much of it is in service. Texas, by contrast, publishes no file of its large-load queue (about 474 GW of requests in June 2026, per ERCOT testimony)."

`proven_by`: remove `ie-national-cso-share-2025`.

### 28. `upstream`: TSMC is a counter-example. **Fix before send.**

`proven_by` includes `tw-tsmc-hsinchu-2021-drought`. That entry is medium/partial, and it shows unit water 14.3% above target and above the 2010 baseline: the opposite of "moving off inland water".

Replacement `note`: "Chile's copper commission records inland water use by copper mining falling from 12.0 to 10.8 m³/s between 2023 and 2024, and projects 7.6 m³/s by 2034 as desalination grows to about two thirds of supply. Chile's environmental regulator has capped SQM's brine and freshwater extraction at the Salar de Atacama under a compliance programme. That is two minerals in one country; there is no equivalent regulator figure for nickel in Indonesia or rare earths in Myanmar, and TSMC's own reports show its unit water use above its 2010 baseline."

`proven_by`: `["cl-copper-cochilco-seawater", "cl-lithium-atacama-sqm-sma"]`.

---

## D. Fix before send: page frame and method (`site/build_page.py`)

### 29. Receipts intro. **Fix before send.**

Text: "…every figure tied to a page of a document. These are the entries that cannot be waved away."

In the Middenmeer receipt every volume is [press], and Georgia's original summary and The Dalles' settlement terms are [press]. "Cannot be waved away" is advocacy.

Replacement: "A receipt is one case worked all the way down: the claim, the dated record and the gap, each figure tied to the document it came from, with [press] marking figures confirmed only through news reports of the document and [arithmetic] marking figures computed from two documented ones."

### 30. Method, "Confidence and verification": high labels on press-only entries. **Fix before send.**

Text: "High means the primary document was read directly. Medium means the figure comes from a press report of the document. … A second pass went back to the original file for every medium and low entry. … company press releases do not [count as primary]."

48 high entries were never re-checked, and several have no primary source at all:

- `uy-canelones-google-water`: four press sources.
- `il-electricity-authority-dc-freeze-2026`: CTech and DCD.
- `us-va-prince-william-digital-gateway-court`: WTOP and InsideNoVa.
- `us-or-the-dalles-google-water-records`: record sources all press.
- `fi-espoo-kirkkonummi-microsoft-fortum-heat`: Fortum press release only.
- `ie-cru-leu-connection-policy-2025`: Matheson summary plus the *proposed* decision.

Three of these are Google or Microsoft headline or proof entries.

Fix: either lower those six to medium, or add the primaries. Replacement method paragraph:

> "High means the figures were read in the primary document or a mirror of it. Medium means at least one key figure comes from a press report of the document. Low means the figure is second-hand, from a company statement, or older. A second pass went back to the original document for every medium and low entry and for some high ones; an entry with no verification tag was not re-checked in that pass. 'Verified against primary' means the original confirmed the figures; 'partly verified' means it confirmed some but not a key figure; 'primary not found' means the note says what was searched and what was missing. Mirrors of the actual document (a law firm's copy of a regulator decision, a library copy of a UN report) count as primary; company press releases and law-firm summaries do not. Figures the ledger produced itself from public documents (the Virginia permit extraction) link to the extraction files, which link to each document."

### 31. Method, "What is excluded": estimates are excluded but the page is full of them. **Fix before send.**

Text: "Estimates, modelled footprints, advocacy press releases cited on their own…" The page includes the PJM counterfactual, JLARC projections, Georgia model jobs, AEMO forecasts and BAN extrapolations.

Replacement: "Estimates the ledger would have to make itself, modelled footprints, advocacy press releases cited on their own, and anything without a URL to the underlying document. Estimates published by a public body or the cited author (a market monitor's counterfactual, an auditor's projection, a grid operator's forecast, a tracking study's extrapolation) are included and labelled as estimates."

### 32. "What is not published" box is stale. **Fix before send.**

Text: "Scripts that pull the queues of PJM, MISO, SPP and NYISO, US federal plant and fuel data, and the Texas and British figures exist and pass offline tests. Live numbers from them will appear here once they have been run outside the build environment."

The Virginia DEQ extraction and the Texas TCEQ index run were done on 2026-10-21, and the Virginia figure is already in an entry. TEXAS.md also adds a finding that belongs in this box.

Replacement paragraph: "Scripts that pull the queues of PJM, MISO, SPP and NYISO, US federal plant and fuel data, and the British figures exist and pass offline tests; their live numbers will appear here once run. The Virginia DEQ permit extraction (all permits on the statewide list, read twice) and a run of Texas's permit indexes were completed on 21 October 2026; the Virginia figures are in the Virginia generator entry."

Add a bullet: "Texas's environmental regulator lists datacenter air-permit applications only while they are pending. Once a permit is issued the application leaves the public index, so no public register links a Texas datacenter to its permitted generation."

---

## E. Caveats

33. **Header count.** The page says 398 linked documents and the brief's footer says 397. The extra one is the ledger's own GitHub link added to the Virginia entry. Either update the brief or stop counting self-citations as "linked documents".
34. **Duplicate entries render twice, two of them with conflicting numbers.**
    - CRU decision: `ie-cru-leu-policy` and `ie-cru-leu-connection-policy-2025`.
    - AEMO ESOO: `au-aemo-2026-esoo-dc-forecast` and `au-aemo-esoo-2026`.
    - EU EED first period: `eu-eed-datacentre-reporting-2024-period` (776 sites, "18 member states") against `eu-eed-dc-reporting-2026` (770 sites, "six Member States reporting none").
    - Zeewolde: two entries.

    Merge them, or have each point to the other.
35. **Ireland CSO gap**, "the highest documented national share in Europe": no source. This is the kind of superlative review_2 E5 warned about. Replacement: "none documented; the 23% figure is an official metered share."
36. **Grid ratios.** Even after finding 11, the Texas denominator (~7.5 GW) is from BIC Magazine and Malaysia's 405 MW is ISEAS citing TNB. Both sit in "high" entries. Mark them [press], or lower the entries to medium.
37. **Package-side mismatch.** TEXAS.md and the brief say ERCOT requests are "roughly 445 GW"; the ledger entry says ~474 GW (June 2026). Pick one figure with its date in both places.
38. **Grid ask, "Ireland's and Ontario's rules are written down."** Ontario's connection requirements are to be set by regulation, and the Playbook is a proposal. Replacement: "Ireland's rule is in force; Ontario has legislated the power to set one."
39. **EED 2024-period entry gap** compares a partial, 36%-coverage EU 2024 reporting period (16.7 TWh) with Ireland's full-year 2025 metered total. The years and scope differ, so state both or drop the ratio.
40. **Amsterdam entry**: the revision is a draft (preparatory decision Nov 2023, draft Dec 2023). Say whether it has been adopted before calling it "tightened".
41. **Meta Hyperion**: the 2,262 MW is "as reported from Entergy filings" (S&P) in a high entry. Mark it [press], or cite the Entergy filing.
42. **Tallaght verification_note** ends with a sentence on "Circularity figures … assurance scope" that belongs to a different entry. Delete it.
43. **Bills `why[0]`**: "people who never use the service" leans toward advocacy. Replacement: "including customers with no datacenter load".
44. **Source titles**: DCD's "slurped" and Context's "Thirsty data centres" are the publishers' real titles, so leave them. They are the first words a reader sees on two Microsoft entries, which is a further reason the gap lines next to them must be flat (finding 5).

## F. Fine

- **Entries that hold up:** the PJM IMM, JLARC and Georgia DOAA entries all state their caveats, and the Georgia gap already matches the receipt's framing.
- **Homer City** is 4,678 MW everywhere on the page, consistent with the PA DEP memo and the package.
- **The Zeewolde "cancelled" entry**'s gap correctly says the national rule did not apply.
- **The headline cards** for Memphis (gap notes the regulator and EPA disagreement), Vantage DUB13, Abbots Langley, Espoo and Stockholm are fine.
- **The Alberta entry** marks Meta as an unconfirmed customer.
- **The three receipts'** gaps and limits are carefully stated.
- **The footer** ("Entries are descriptions of documents, not findings of fact about any company") is the right line. The guide and standard prose has to live up to it, which is what sections B and C are for.

---

### Order of work

1. Findings 1–5: Virginia, Chesterfield, Ireland CSO, Wisconsin, Middenmeer.
2. Findings 16–28, the standard: labels, intro and closing first, then each note and `proven_by` list.
3. Findings 6–15, the guide prose, one theme at a time.
4. Findings 29–32, the receipts intro, method and "not published" box. Re-grade the six press-only "high" entries.
5. Rebuild, then reread the rendered standard and the five headline panels with the most changes: bills, water, fuel, money, chain. Then link.

_Local file paths in this review were replaced with repository-relative paths on 2026-10-22; nothing else was changed._
