# Hostile methodology review: "Datacenters for Climate TRACE" handover

Reviewer stance: power-sector methodology lead at a satellite-emissions coalition, reading to find the reason to file this under "later". Files reviewed: `ireland_sites_method.md` (section 4), `ireland_sites.json`, `worked_example_estimates.json`, `attribution_method.md`, `dedicated_supply.json`, `dedicated_supply_method.md`, `brief.html`, plus `README.md`, `climate_trace_schema.json` and the backlog CSV for traceability checks. Eight web checks used (Cat 3516C spec sheet, AP-42 3.1 background doc, eGRID2023 summary tables rev2, DCD/CSO coverage, DCK 2022 utilisation piece, Dublin-share search).

## Verdict

I would reply, but not to the brief as written: I would reply to the Ireland site list and the dedicated-supply column, which are genuinely useful and better sourced than anything we have on the consumer side, and I would tell the sender that the headline "regional check" and the five worked rows would not survive our internal review in their current form. The Ireland arithmetic is honest about its factors but its conclusion (u ≈ 0.3–0.4) is an artefact of one undefended assumption (÷1.2 for N+1); under 2N the same metered total supports u ≈ 0.5–0.8, so the check does not discriminate between the "0.3" the brief recommends and the "0.6" it says fails. The five worked rows have a structural flaw a Climate TRACE reviewer will see in thirty seconds: the "load" of each site is set equal to the MW of the supply document (a 944 MW peaker that does not exist until 2029, a 1,920 MW PPA that is 300 MW physical today), reported as 2025 annual activity under `sector: power`, which both invents activity and double counts against the plant-side inventory. The brief then overclaims provenance ("40 sites from EPA licence applications", "22 coordinates from per-stack grid references", "regulator's or court's document" for all 43 supply rows) in ways the handover's own method notes contradict. What would make it survive: (1) present the Ireland check as a bound, not a point, with the redundancy factor as an explicit scenario axis and the licence-cap figures as the base case; (2) rebuild the five rows with a site load that is independent of the supply MW, a time period in which the supply exists, and a Scope 2 field rather than a power-sector row; (3) rewrite the brief so every sentence matches the method notes, which are more careful than the brief. Send the list and the column now; send the estimate after the fixes.

## Findings

Severity scale: **blocks send** | **fix before send** | **caveat** | **fine**.

### 1. Ireland regional check (method §4; brief "One country, one check")

**1.1 — 0.385 MWe/MWth. Severity: fine (add the citation).**
Text: "diesel gensets of this size deliver about 0.385 MWe per MWth (e.g. a 6.49 MWth unit is a ~2.5 MWe set)". Checked against the Cat 3516C 2500 ekW standby spec sheet (Hanover County VA copy): 656.8 L/hr at 100% standby load, fuel 838.9 g/L, LHV 42,780 kJ/kg → 6.55 MWth → 2.5/6.55 = **0.382**. The IED/EPA "rated thermal input" is on net calorific value, so the basis matches. The factor survives. Change wanted: cite the spec sheet (or any ISO 8528-1 standby-rated 2–3 MWe unit) in the method and say "LHV, standby rating, with fan". Note that the 0.36–0.42 band moves u_max only from 0.58 to 0.68; this is not where the uncertainty lives.

**1.2 — ÷1.2 for N+1. Severity: blocks send (as the basis for the headline).**
Text: "fleets are sized N+1 (and sometimes 2N) over the total facility load, so facility design load ~ standby / 1.2". Three problems. (a) ÷1.2 is N+1 with N=5; the fleets in the file are 40–105 units, so N+1 at fleet level is ÷1.01–1.03, which pushes design load *up* and u *down* (u_max 0.54). (b) Colocation operators (Equinix, Digital Realty, K2, KDCR) commonly design 2N or N+1 per block with 2N distribution; hyperscalers sometimes carry N+2. Under 2N design load halves (824 MW), 100%-utilisation energy is 7,216 GWh, and the check **imposes no constraint at all** (u_max 1.06). (c) Fleets are permitted for full build-out and standby MWth also covers mechanical/cooling load, so "utilisation of permitted standby" conflates installed fraction, built-out fraction and IT load factor; it is not the quantity anyone else means by "utilisation" (the 0.6–0.8 the brief contrasts it with is load factor of contracted or IT MW).

Range the check actually supports (national 7,663 GWh; 17 sites assumed to be 50–70% of national load, which is plausible given they hold Amazon, Microsoft, EdgeConneX and Equinix DB5 but miss Google, Meta, Digital Realty and all of the "<50 MW" colos):

| Standby basis | η | Redundancy | Design MW | u_max (hard bound) | u if 17 sites = 50–70% of national |
|---|---|---|---|---|---|
| 4,279 (sum of units, as used) | 0.385 | ÷1.01 (fleet N+1) | 1,625 | 0.54 | 0.27–0.38 |
| 4,279 | 0.385 | ÷1.2 (as used) | 1,373 | 0.64 | 0.32–0.45 |
| 4,279 | 0.385 | ÷1.5 (N+1 + build-out headroom) | 1,098 | 0.80 | 0.40–0.56 |
| 4,279 | 0.385 | ÷2 (2N) | 824 | 1.06 | 0.53–0.74 |
| 3,830 (licence caps, see 1.4) | 0.385 | ÷1.2 | 1,229 | 0.71 | 0.36–0.50 |
| 3,830 | 0.385 | ÷2 | 737 | 1.19 | 0.59–0.83 |

So the metered total supports anything from **u ≈ 0.27 to ≈ 0.8** depending on the redundancy architecture, and the only statement that is robust is "a naive permitted-MWe × 0.6 for these 17 sites alone exceeds the national total *if* fleets are N+1 at ÷1.2". Change wanted: present the table above (or equivalent) in §4, drop the single ÷1.2, and either (i) read the redundancy topology from the licence operational reports (Amazon's inspector's reports state generator-per-building counts; Microsoft's NTS describes the gas plant as a second layer, which is 2N-like), or (ii) state the conclusion as "u ≤ 0.54–0.71 under N+1; unconstrained under 2N". The brief's "needs a utilisation near 0.3" must go.

**1.3 — Microsoft DUB14/15 "u = 0.23 ... the only metered site agrees". Severity: fix before send.**
Text (method step 5; brief last table row). The 0.23 is computed on the 175.6 MWth diesel fleet only. The same licence lists a 167.2 MWth standby gas plant for the same campus; if both are standby for the same load the fleet is ~2N and the same arithmetic gives u = 0.19 (2N) or 0.12 (÷1.2 on 342.8 MWth). The method itself says the campus "was still ramping", which means the 2024 figure is not a steady-state utilisation and cannot "agree" with a steady-state range. Also the AER "total energy used 402,946.82 GJ" is an all-energy figure (electricity plus gas plus diesel); the method says "mainly purchased electricity" without the split. Change wanted: report the DUB14/15 point as "111.9 GWh in 2024 against a diesel-only design load of 56 MW (0.23) or a combined standby of 110 MW (0.12), campus ramping" and delete "agrees" from the brief. Separately, the press figure "170 MW gas plant" and your 22 × 7.6 = 167.2 MWth cannot both be right (167 MWth is ~65 MWe); say which.

**1.4 — "Permitted MWth": sum of units vs licence cap vs applications under review. Severity: fix before send.**
The 4,279 MWth uses sum-of-units from inspector's reports and, for two rows, from **review applications not yet granted** (P1186-02 adds 97.9 MWth for Buildings U/V; LA015550 adds 192.3 MWth for Drogheda Building B). The licences themselves cap simultaneous operation lower (Amazon licence caps sum to 2,206 MWth vs 2,655 sum of units; difference 449 MWth, 10% of the total). "Permitted" should mean the granted licence cap. Yes, the EPA figure is nameplate rated thermal input (net CV) of each unit; that part is right. Change wanted: carry both columns (sum of units; licence cap) and run the check on the cap as the base case (standby 3,830 MWth). The `generator_mw_basis` field already has the information; the aggregate just uses the wrong one.

**1.5 — "97% of Irish data centres are in Dublin" (CRU). Severity: caveat.**
Text: method §4 and ledger entry `ie-national-cso-share-2025` ("97% Dublin region"). No CRU document or page is cited anywhere in the handover; the CSO release has no regional split; EirGrid's Dáil answer in your own §1d (14 of 16 transmission-connected sites in Dublin, 87.5%) does not give 97%; press coverage says "overwhelming majority" with no number. The figure is not load-bearing for the national check but it is in the recommended procedure (step i). Change wanted: cite the CRU document and page, or replace with "most (EirGrid: 14 of 16 transmission-connected)". Also note that three of your 17 sites (Drogheda, Clonee; Leixlip in the pipeline) are outside Dublin, so "Dublin region" is already stretched.

**1.6 — Double counting across the 17. Severity: fine, with one open item.**
Checked: Amazon rows are from distinct IE licences with distinct generator inventories (P1170 73 units vs P1184 16 units at the same address are separate licences); GHG permits were used only for coordinates on Amazon rows, so no GHG/IE overlap enters the sum. Microsoft DB3-5 + DUB06-13 = 138 units matches the GHG permit's 139 for DB3-13, and DUB14/15 is a separate licence. Cruiserath E/F/G and the two refused halls carry null MW. Open item: P1171 (105 stacks, Clonshaugh, null MW, "operating" inferred) was applied for before P1186 at the same campus; it may be the campus-wide application that P1186's Buildings W/X/Y sit inside. It does not affect the sum but it affects the "9 operating rows have no MW" undercount argument. Change wanted: mark P1171 as "possible superset of P1186; not counted" and lower its status confidence to the same "verify" language used elsewhere.

**1.7 — "17 operating sites with permitted standby generation totalling 4,279 MW thermal". Severity: caveat.**
Equinix DB5 contributes 0 to the 4,279 (its 168 MWth is all primary gas and is excluded); so it is 16 sites with standby plus one with none. Trivial, but a reviewer who sums the JSON will notice.

### 2. The five worked rows (`worked_example_estimates.json`; brief "Five sites, estimated your way")

**2.1 — Load is set equal to the supply document's MW. Severity: blocks send.**
Every row's `capacity` is the MW of the *supply* document, not of the site: Chesterfield 944 MW is a peaker's nameplate (`capacity_units: "MW (contracted)"` is simply wrong; nothing is contracted); Wisconsin 1,100 MW is Oak Creek's nameplate; Susquehanna 1,920 MW is the 2032 PPA ceiling for a campus that is 300 MW behind-the-meter today; Nevada 115 MW is the geothermal PPA, not Google's Storey County load. The load range (×0.30–0.80) is then applied to that number. Consequences: (a) Susquehanna reports 9.25 TWh of 2025 activity (midpoint) for a campus drawing a fraction of that; (b) the two "clean firm" rows are guaranteed zero because load can never exceed the dedicated supply by construction; (c) Chesterfield is a row for a facility that does not exist (lat/lon 37.38, -77.38 is the power station). Change wanted: site load must come from a signal independent of the supply document (permit generator MW, interconnection MW, utility large-load filings, imagery footprint), and alpha = min(1, supply MWh / load MWh) as your own method note (§α rule 2) says. Where no independent load signal exists, say so and leave `activity` blank rather than fill it from the supply MW.

**2.2 — Time period vs existence of the supply. Severity: blocks send.**
All five rows are `start_time 2025-01-01, end_time 2025-12-31`. CERC's COD is 2029-06-01 (your own `dedicated_supply.json`); Oak Creek was approved 2025-07 and is not built; Susquehanna front-of-meter begins 2026; Fervo Corsac delivery date not confirmed in the record. A 2025 annual row cannot carry an "incremental range" from a 2029 plant. Change wanted: either date the rows to the first year the arrangement is physically in service, or (for 2025) report alpha=0 grid-factor rows only, with the dedicated-supply fields as forward-looking metadata.

**2.3 — `sector: power` double counts the plant side. Severity: fix before send.**
`attribution_method.md` correctly says this is a Scope 2 reallocation of plant emissions Climate TRACE already estimates, and that 5.11.0 reports facility Scope 2 as a separate field. The rows nonetheless go out under `sector: power`, `subsector: electricity-consumption-datacenters (proposed)` with `emissions_quantity` populated, which, if ingested, adds 1.2 Mt (Chesterfield) and 2.2 Mt (Wisconsin) on top of the plant rows. Change wanted: put the figure in the Scope 2 field/convention 5.11.0 uses for other facility types, and state in the README that `emissions_quantity` here is Scope 2, non-additive to the power sector.

**2.4 — Load-range rules (permit × 0.35–0.75; contracted × 0.30–0.80). Severity: fix before send.**
Nothing in the handover derives these bands. The Ireland check, which the brief presents as the lesson, concludes 0.3–0.4 on permitted standby; the Memphis row then applies 0.35–0.75 to "permit" MW (which in Memphis is turbine MWe, i.e. primary generation, a different denominator again). AEMO's 27% of connection capacity, the 2022 DCK estimate of ~25% of Irish MIC, and AEP Ohio's 85% minimum-take are all in your own files and all point to a lower band for *connected/contracted* MW. Change wanted: one table that states, per capacity signal (standby permit MWth, primary-gen permit MWe, contracted/MIC, IT MW), the utilisation band used and the two or three documents it rests on; then apply it consistently to Ireland and the five rows.

**2.5 — Annual-average eGRID for a flat load. Severity: caveat (but pick one story).**
Using annual average subregion factors for a flat load is arithmetically fine and matches Climate TRACE's 5.11.0 attributional Scope 2 practice. The eGRID2023 values check (rev2 Table 1: SRVC 596.3, RFCE 599.2, RFCW 916.1, ERCT 736.6, US 770.9 lb CO2e/MWh; conversions to t/MWh correct). Two caveats: 2023 factors for a 2025 period (say so); and the brief's narrative ("which plant serves it sits in dockets", "gas outnumbers clean") is a consequential/marginal story, while the headline numbers are attributional/average. You cannot sell the column on the marginal story and compute the rows on the average one without saying which the coalition should adopt. Change wanted: one sentence in the method note: "headline = attributional (average factor, consistent with 5.11.0); the dedicated-supply fields enable a consequential variant, reported separately and never summed."

**2.6 — alpha = 0 for system plants with an "incremental" range alongside (Chesterfield, Wisconsin). Severity: fix before send; as written it has it both ways.**
The alpha=0 decision is defensible on its own (retail customer, plant not contracted to the load; consistent with your Georgia and Batam rows). The "incremental (alpha=1) range" is not: it takes 944 MW × 0.30–0.80 CF × simple-cycle EF, i.e. it assumes the *peaker* runs at 30–80% capacity factor. A simple-cycle peaker runs 5–15%; at 10% CERC emits ~0.43 Mt/yr, not 1.3–3.4 Mt. The incremental figure is therefore not "what the plant will emit because of this load", it is "what this load would emit if it were served entirely by a peaker running flat out", which is neither attributional nor consequential. Change wanted: either drop the incremental figures from the worked rows (keep the qualitative flag in `dedicated_supply.json`, which is fine), or compute them as load × a long-run marginal factor for the balancing area, or as the plant's expected generation × its EF allocated by the regulator's stated DC share (the SCC order gives none, as your alpha_note says). Also reconcile: the Wisconsin `dedicated_supply` alpha_note says "alpha=1 on an incremental basis ... recommend 1 for the Red Oak Ridge contracted output", the worked row says alpha=0. Pick one and say why.

**2.7 — AP-42 "1,135 lb CO2/MWh" for simple-cycle gas. Severity: fix before send (citation), fine (value).**
AP-42 Section 3.1 does not give a lb/MWh figure. It gives CO2 = 110 lb/MMBtu for natural-gas turbines (Table 3.1-2a; the background document derives it by mass balance, 99.5% carbon conversion). 1,135 lb/MWh = 110 × 10.32 MMBtu/MWh, i.e. an unstated ~10,300 Btu/kWh heat rate. That heat rate suits the Solar SMT-130 mobile units at Memphis (~33% efficient) but is high for the frame CTs at Chesterfield/Oak Creek (~9,000–9,700) and simply wrong for any combined-cycle use (Homer City, Greenlight, Hyperion are CC or CT at ~6,500–7,000 for CC). AP-42 is also CO2 only; the rows are labelled CO2e and blended with eGRID CO2e. Change wanted: cite "AP-42 3.1, 110 lb/MMBtu × assumed heat rate H (stated per plant class)", give H per row, and add CH4/N2O or relabel as CO2.

**2.8 — Memphis alpha = 0.5. Severity: fix before send.**
`dedicated_supply.json` gives the rule: alpha=1 for turbine-served load through the 2025 permit, then alpha = min(1, 247 MW × turbine CF / site load). The worked row uses a flat 0.5 for calendar 2025 with the justification "documented partial self-supply", i.e. a round number. There is a defensible route to ~0.5 (MLGW's 150 MW grid connection approved Nov 2024 vs ~150 MW of turbines) but it is not the one stated and the 150 MW grid figure is not in the file. Also, site load = 247 MW permit (the turbine permit), so the alpha denominator is the alpha numerator again (see 2.1). And on-site turbine combustion is Scope 1 of the site and will appear in the coalition's power-plant inventory once detected; the method note says not to double count, the row does. Change wanted: alpha from (turbine MW × CF)/(independent site load), time-split at 2025-07, with the grid tranche documented; turbine emissions reported as Scope 1 on the site, not inside the Scope 2 blend.

### 3. Dedicated-supply classifications (`dedicated_supply.json`; five rows checked strictly against the cited document, plus three that fail the same test)

**3.1 — `us-va-chesterfield-dominion-cerc-gas` = `dedicated_fossil`. Severity: fix before send.**
The cited SCC order approves a system peaker on a reliability finding that names data centres as a contributing factor; the row's own `alpha_note` says "plant is a system peaker, not contracted to a named load". The category definition was stretched ("or the only capacity addition a utility documents for a data-center-driven need") to admit it. By the method's own strictness rule (Pecém stays `grid_only` because no plant is tied to the load) this is `grid_only` with an incremental note. Change wanted: reclassify, or split the category into `dedicated_fossil` (named load) and `system_fossil_dc_driven`. This matters because the brief's "gas 9 vs clean firm 5" counts it.

**3.2 — `us-wi-mount-pleasant-microsoft-we-energies` = `dedicated_fossil`. Severity: fix before send.**
The regulator document (PSC 6630-CE-317) approves a system plant for large-load growth. The elements that make it "dedicated" (Microsoft 15-year service contract 2026-07-16; Red Oak Ridge contracted output; Paris RICE) are all marked press-sourced in the row itself. Category rests on press; confidence "medium" is generous under your own rule ("key figure rests on press" is the medium definition, but the *category* resting on press should be low or the category should follow the docket). Change wanted: `grid_only` with incremental note until the PSC May 2026 ruling on the Microsoft contract is retrieved, or retrieve it.

**3.3 — `us-nv-google-nv-energy-clean-transition-tariff` = `dedicated_clean_firm`, confidence medium. Severity: fix before send.**
`document_url` is a Record-Courier newspaper article; `documented_by` admits "ESA and Fervo PPA approvals press-sourced" and `alpha_note` says "the ESA approval was not confirmed". By the method's confidence rule this is `low`, and the category (regulator-approved tariff) is inferred from press reporting of a filing. Change wanted: link the PUCN docket 24-06014 document (the filing exists and is public) and keep the category; otherwise confidence low and the brief's "regulator-approved tariff" becomes "tariff applied for".

**3.4 — `us-pa-susquehanna-talen-aws-colocation` = `dedicated_clean_firm`. Severity: fine for the row, blocks the worked example.**
The FERC order and the 10-K support the category and the figures. But the row's `alpha_note` (alpha=1 only for the 300 MW BTM tranche; front-of-meter alpha=1 only if the method credits hourly bilateral PPAs with a non-additional plant, "the handover should carry both values") is contradicted by the worked row, which takes alpha=1 on 1,920 MW for 2025. The column is right; the estimate ignores it.

**3.5 — `ie-dublin-vantage-dub13-abp-refusal` = `dedicated_fossil`. Severity: fix before send.**
The cited document is a planning *refusal* whose reasoning is that the Board "could not rule out" on-site gas becoming primary supply because no grid connection agreement was shown. A document that says a thing cannot be excluded is not a document that says the thing is so; nothing in it names a plant, MW or contract. The alpha=0.5 "placeholder" is invented. Change wanted: `bring_your_own` or `grid_only` with the refusal recorded in `operator_claim`/notes, alpha unresolved; or merge into the P1203 DUB11/12 row where the GHG permit does document an 11-engine MFGP (that is the document that supports `dedicated_fossil` for the campus, and it is in `ireland_sites.json`, not here).

**3.6 — Three more that fail the same test (brief count impact).** `ca-ab-...-greenlight` is `dedicated_fossil` for a customer "reported as Meta, unconfirmed", against a category definition requiring a *named* load. `id-batam-nongsa-power` is `dedicated_fossil` on a state-broadcaster report of a utility PPA, with its own alpha_note saying "alpha=0 at site level (utility system plant)". `ng-lagos-diesel-gas-dependence` is `dedicated_fossil` on a CEO interview and a sector survey. With 3.1, 3.2, 3.5 and these three removed or reclassified, "gas plant built or certified for the load" is 3–4 rows (Hyperion, Homer City, Southaven with press MW, Memphis), against 3 documented clean-firm rows (Susquehanna, Fervo if the docket is linked, Hydro-Québec). The brief's "gas outnumbers firm clean supply nearly two to one" becomes roughly one to one.

### 4. The brief (`brief.html`)

**4.1 — "From EPA licence applications we located 40 Irish sites, 22 with coordinates taken from the per-stack grid references in the applications themselves." Severity: fix before send (overclaim).**
Per the method: 12 rows from IE licences, 15 from GHG permits, 12 from ABP cases, 2 from press. Of the 22 coordinates: ~6 from attachment 7.4.2 stack references, 3 from application-form site centres, ~10 from GHG-permit main-entrance references, 1 townland centre (±1 km), 1 ledger 2-decimal point (±0.5 km). The README repeats the overclaim. Change wanted: "40 Irish sites from EPA licences, EU ETS permits and planning appeals; 22 located, mostly from grid references in EPA documents (stack, site-centre or main-entrance), two at ±0.5–1 km."

**4.2 — "Generators are sized to carry full load, so permitted MW is a ceiling on load." Severity: fix before send.**
True only for installed units; licences permit phased fleets and review applications are included (1.4). And the ceiling on *load* is standby MWe ÷ redundancy, which is the contested factor (1.2). Change wanted: "permitted standby MW bounds design load from above once the redundancy design is known; we assume N+1 (÷1.2) and show 2N."

**4.3 — "'Permitted MW × 0.6', a common shortcut" and "not the 0.6–0.8 often assumed". Severity: caveat.**
Neither is cited to anyone. If you are contrasting with a specific published method (e.g. an IEA or LBNL load-factor assumption on IT or contracted MW), name it; otherwise it is a straw man on a different denominator.

**4.4 — "the only metered site agrees" / "u = 0.23". Severity: fix before send.** See 1.3.

**4.5 — "National metered total, all ~90 sites". Severity: caveat.**
The CSO release carries no site count; "~90" is The Journal, "82" is Gardiner (via Silicon Canals), ">80" is DCD. Attribute it or drop the count.

**4.6 — "For 43 sites and clusters in the ledger, the regulator's or court's document says how electricity actually arrives." Severity: fix before send (overclaim).**
`dedicated_supply_method.md` says 11 of 43 rows are "press or operator statement only" and lists four dedicated rows as placeholders. Change wanted: "For 43 sites and clusters: 32 with a regulator, court, grid-operator or statutory document, 11 with press or operator statements only, flagged."

**4.7 — "Where a supply arrangement is documented at all, gas outnumbers firm clean supply nearly two to one." Severity: fix before send.** See 3.6; on documented rows it is about 1:1.

**4.8 — "Several of the gas sites carry a public '100% renewable' claim." Severity: fix before send (internal contradiction).**
The worked row for Mount Pleasant says "Microsoft: 100% renewable matching via PPAs/certificates"; the `dedicated_supply` row for the same site says "water claims only; no supply claim found". Chesterfield's claim is attributed to "operators in the cluster", not a site. Hyperion's is "three clean energy projects", not "100% renewable". Change wanted: name the sites and quote the claim with its URL, or soften to "some".

**4.9 — "1,100 MW gas approved for the load (PSC docket 6630-CE-317)" and "944 MW gas peaker approved citing datacenter load". Severity: fix before send.**
The JSON says "System plant, not site-dedicated" for both. "For the load" is the one phrase a utility-regulation reader will test first. Use the JSON wording.

**4.10 — "AWS at Susquehanna ... 0" and "Google, Storey County ... 0". Severity: blocks send.** See 2.1/2.2: zero is produced by setting load = contracted supply.

**4.11 — "in your 44-column asset format" / "attached worked_example_estimates.csv". Severity: caveat.**
The worked CSV has 43 columns; `geometry_ref` from your own `climate_trace_schema.json` is missing. The seed CSV has 44. Trivial but it is the first thing an ingest script reports.

**4.12 — "A 325-site register backlog ... Eight Virginia permits opened so far; one lists 97 generators at 236 MW." Severity: caveat (traceability).**
The backlog CSV has 333 rows, not 325. "Eight permits opened" is not in any file. The "97 generators, ~236 MW" (reg 74129) appears only as a boilerplate example string repeated in every backlog row's `generator_info`, not as an extracted field on an identified site. Change wanted: fix the count, drop "eight opened" or list them, and attach the one extracted permit as a row.

**4.13 — "Compute Ledger · 117 entries, 40 countries, 397 linked documents, 3 receipts" and "every figure on this page links to a public document in the attached files". Severity: caveat.**
The supply method says 99 entries were the input; 117/397 are not derivable from the handover files (README says "available on request"). The second sentence is false by 4.3, 4.5, 4.12 and the 97% in 1.5. Change wanted: either attach the ledger export or delete the sentence.

**4.14 — "Gavin said in April that your database holds the world's datacenters". Severity: caveat.**
`attribution_method.md` gives the same quote with no URL. First-naming the co-founder in a cold brief is a tone risk; the uncited quote is a substance risk. Cite the talk or interview.

**4.15 — "Sites in your v5.11.0 emissions and ownership column order" / 5.11.0 Scope 2 claim. Severity: fine.** Schema file matches; the Scope 2 reference is consistent with the attribution note. No change.

### Summary by severity

- **Blocks send:** 1.2 (÷1.2 drives the headline), 2.1 (load = supply MW), 2.2 (2025 rows for 2029 plants), 4.10 (the two zeros).
- **Fix before send:** 1.3, 1.4, 2.3, 2.4, 2.6, 2.7 (citation), 2.8, 3.1, 3.2, 3.3, 3.5, 4.1, 4.2, 4.4, 4.6, 4.7, 4.8, 4.9.
- **Caveat:** 1.5, 1.7, 2.5, 3.6 (as it affects the brief), 4.3, 4.5, 4.11, 4.12, 4.13, 4.14.
- **Fine:** 1.1 (cite it), 1.6 (one open item), 3.4 (row), 4.15.

### What would make it survive, in order

1. Replace the Ireland point estimate with the sensitivity table (standby basis × redundancy), base case = licence caps, and state the result as a bound: "u ≤ 0.54–0.71 under N+1; unconstrained under 2N; the one metered campus (ramping) sits at 0.12–0.23".
2. Rebuild the five rows: independent load signal, alpha = min(1, supply/load), period = first year the supply is physically in service, Scope 2 field not `sector: power`, AP-42 110 lb/MMBtu × stated heat rate, incremental figures removed or computed on a marginal factor.
3. Reclassify Chesterfield, Wisconsin, Vantage DUB13, Greenlight, Batam, Lagos (or split the category), relink Nevada to the PUCN docket, and recount for the brief.
4. Rewrite the brief from the method notes, which are already more honest than the page.
5. Send the Ireland list, the supply column and the method note now, with the estimate labelled "illustrative, under revision". Those three are what a coalition reviewer would actually want.
