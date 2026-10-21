# North America: datacenter / AI-compute physical footprint (public record vs. public claims)

Scope: United States, Canada, Mexico. Research date: 2026-10-19. Sources are regulator orders, permits, court records, utility filings, SEC filings, and news outlets that quote or link those documents. Where a figure comes only from a news account of a document (rather than the document itself), that is noted. Advocacy-group figures are flagged as such and are never the sole source for a number used in the registry.

General caveat: Many primary PDFs (SCC, LPSC, PUCT, MDEQ, SCHD, Régie) were reachable only through secondary reporting or partially; the specific document link is given wherever one was found.

---

## Key Question 1: Northern Virginia / Dominion (IRP, SCC dockets, gas generation, backup generators)

### Takeaway
The SCC approved Dominion's 944 MW Chesterfield gas peaker (PUR-2025-00037) on 2025-11-25 at $1.47B, finding an "imminent reliability threat"; the order says data centers are "not an insignificant contributing factor" but declines to put a MW number on data center demand. Dominion's own reporting put ~40 GW of data center capacity "in various stages of contracting" as of Dec 2024. Separately, a 2025 DEQ proposal would let ~9,000 Tier II diesel backup generators (≈4,700 in Loudoun, per PEC counts cited in press) run during utility "planned outages."

### Cited Findings
- SCC Final Order, Case PUR-2025-00037 (2025-11-25): approves Chesterfield Energy Reliability Center (CERC), ~944 MW nominal, four GE Vernova 7F combustion turbines at Chesterfield Power Station, $1.47B excluding financing; commercial operation by 2029-06-01; Rider CERC $35.7M revenue requirement effective 2026-01-01. Order says data center development is "not an insignificant contributing factor" but "not the only factor"; projects Dominion territory load growth 2.9%/yr and DOM Zone ~5%/yr 2025–2039. — [SCC Final Order PDF (mirrored by VPM/NPR)](https://npr.brightspotcdn.com/3a/5d/aa4657d64958974419dd9cfb55c0/cerc-scc.pdf)
- Same order quoted: "there is an imminent reliability threat for Dominion and its customers and that the CERC project addresses that threat." Plant expected to run ~37% of the year. Also created new large-load rate class: >25 MW and >75% load factor; 14-year contracts; minimum demand charges 85% transmission / 85% distribution / 60% generation. — [Virginia Mercury, 2025-11-25](https://virginiamercury.com/2025/11/25/scc-approves-chesterfield-gas-plant-and-dominion-rate-hike-creates-new-rate-class-for-data-centers/)
- DEQ air permit for CERC approved 2025-12-19; appeal filed in Richmond Circuit Court by Appalachian Voices, Mothers Out Front, Chesterfield NAACP (SELC). SCC denied reconsideration (reported 2026-02-16). — [Virginia Mercury, 2026-02-16](https://virginiamercury.com/2026/02/16/scc-declines-to-reconsider-chesterfield-gas-plant-approval-advocacy-groups-appeal-air-permit/)
- Dominion reported ~40 GW of data center capacity "in various stages of contracting" as of Dec 2024, up from 21 GW in July 2024; CERC originally described as ~1 GW (4×250 MW); Possum Point +44 MW expansion. — [DCD, 2025](https://datacenterdynamics.com/en/news/dominion-energy-seeks-approval-for-1gw-virginia-gas-plant-amid-data-center-boom)
- SCC Order for Notice and Hearing, PUR-2024-00184 (2024-11-18): Dominion's 2024 IRP forecasts 5.5%/yr demand growth and demand doubling by 2039 in DOM Zone; SCC ordered a supplemental filing modeling plans with data center load removed and flagging which transmission projects are data-center-driven. — [SCC order](https://scc.virginia.gov/getdoc/d163dee3-ab9b-4102-be06-12efef93fab9/nr240184)
- Dominion 2024-11-15 supplemental filing (as reported): peak demand WITHOUT new data centers 17,353 MW (2024) → 18,608 MW (2039); data center growth raises utility spending ~20%; ~half of ~200 planned transmission projects are solely data-center-driven; data centers ≈ a quarter of Dominion sales. — [Virginia Mercury, 2024-11-26](https://virginiamercury.com/2024/11/26/under-pressure-from-the-scc-dominion-reveals-the-true-cost-of-data-centers/); SCC doc link [82l101](https://scc.virginia.gov/docketsearch/DOCS/82l101!.PDF)
- JLARC (2024-12-09): current Virginia data center load ~5,050 MW; backup generators <4% of regional NOx, ~0.1% of CO and PM; data centers could be ≥80% of annual sales in three co-ops by 2030 (half-unconstrained scenario); recommends localities be able to require water-use estimates. — [JLARC summary (Prince William County)](https://pwcva.gov/assets/2024-12/JLARC%20Report%20Summary_12-16-2024.pdf)
- DEQ memo (Mike Dowd to Director Rolband, 2025-09-30) proposes adding utility "planned outage" (notice ≤14 days) to the emergencies in which Tier II generators may run. ~9,000 generators statewide, ~4,700 in Loudoun, ~8,000 Tier II (counts attributed to PEC's Julie Bolthouse). Summer 2025 substation fire ran Loudoun generators 4–5 days. Legislative research estimate of up to 9,000 tons NOx regional worst case. — [VPM, 2025-12-17](https://www.vpm.org/news/2025-12-17/virginia-data-centers-diesel-backup-generators-deq-loudoun-turner-dowd); DEQ memo on Town Hall: GDoc_DEQ_8407_20251003.pdf (linked in article)
- Prince William Digital Gateway (2,100+ acres, 22M sq ft, 37 data centers; rezoned Dec 2023): Prince William Circuit Court Judge Kimberly Irving voided the rezoning (Aug 2025) for defective public notice; Virginia Court of Appeals upheld 2026-03-31; Compass Datacenters withdrew its appeal 2026-04-28. — [WTOP, Aug 2025](https://wtop.com/prince-william-county/2025/08/judge-voids-digital-gateway-rezoning-in-prince-william-county/); [InsideNoVa, 2026-04-29](https://www.insidenova.com/news/prince_william/updated-developer-to-end-appeal-in-digital-gateway-data-center-case-putting-the-massive-project/article_d17048b9-8d0a-47ad-aeec-1cbd02f73f47.html)

### Inferences
- Dominion's public "40 GW contracting" figure and the SCC's refusal to quantify data center demand in the CERC order mean the record contains a utility-side number but no regulator-endorsed data-center MW figure for the plant's need.
- Backup generator counts in the public record come via PEC tallies of DEQ permits; DEQ itself did not publish a consolidated MW figure in the sources found.

### Gaps
- Could not retrieve the Dominion 2025 IRP update text or a total "new gas MW by 2039" figure from a primary document.
- No consolidated DEQ figure for total permitted backup generator MW in Loudoun.
- Operator (hyperscaler) renewable claims specific to Loudoun were not located in a primary filing; Dominion describes its approach as "all of the above."

---

## Key Question 2: Texas / ERCOT and xAI Memphis–Southaven on-site gas

### Takeaway
ERCOT told the Texas Senate (2026-07-29) it is tracking ~474 GW of large-load interconnection requests (~90% data centers, >1,800 projects), more than 5× record peak; Gov. Abbott ordered an audit/pause 2026-08-03 and ERCOT paused Batch Zero. Only ~7.5 GW of large load had actually connected as of early 2026 (BIC/ERCOT briefing). For xAI, the Shelby County Health Department permitted 15 permanent turbines (247 MW, 87 tpy NOx) on 2025-07-02 after ~a year of unpermitted temporary turbines; MDEQ approved 41 turbines / 1.2 GW in Southaven in March 2026 while 69 temporary units run to a 2027 retirement schedule; EPA's Jan 2026 NSPS rule states trailer-mounted turbines are still "stationary."

### Cited Findings
- ERCOT Senate testimony (2026-07-29): "ERCOT is tracking approximately 474 GW of Large Loads seeking interconnection" (as of June 2026), ~90% data centers; ~205 GW preliminarily eligible for Batch Zero (as of 2026-07-28). — [ERCOT PDF](https://www.ercot.com/files/docs/2026/07/29/ERCOT-Senate-July-29-Panel-1-Assessing-The-Grid.pdf)
- Abbott directive 2026-08-03: audit all data centers in ERCOT queue (disclose tax breaks, power use/generation, water use and cooling, ownership); >1,800 projects, >474 GW, >5× record peak; ERCOT paused Batch Zero. — [Texas Tribune, 2026-08-03](https://www.texastribune.org/2026/08/03/texas-data-center-project-audit-greg-abbott/)
- PUCT open meeting 2026-08-20: 17 large loads (~6.6 GW) have passed stability assessment but not yet approved to energize; ~300 data centers ≥75 MW in Batch Zero; audit report targeted for 2026-12-10; ERCOT Market Notice M-A080326-01. — [Utility Dive, 2026-08-21](https://utilitydive.com/news/ercot-texas-puc-data-center-audit/828472); [Troutman](https://www.troutman.com/insights/texas-hits-pause-on-data-center-grid-connections-amid-growing-oversight-push/)
- Earlier snapshot: >233 GW requests (>70% data centers) as of Dec 2025 briefing, up from 63 GW 14 months earlier; ~128 GW without studies; ~7.5 GW actually connected; SB 6 (2025) sets 75 MW large-load threshold, $100k fee, duplicate-request disclosure, backup-generation disclosure, emergency curtailment. — [BIC Magazine, 2026-03-06](https://www.bicmagazine.com/industry/powergen/texas-grid-sees-233-gw-data-center-requests-much-real/)
- ERCOT Sept 2026 board deck: large-load queue data moved to separate "Batch Zero Update" item; draft NOGRR proposes 10 MW / 5 s ramp limit for large computational loads. — [ERCOT PDF 2026-09-17](https://www.ercot.com/files/docs/2026/09/17/10-Interconnection-and-Grid-Analysis-Update-REVISED.pdf)

xAI Memphis (Shelby County, TN):
- SELC letter to SCHD (2024-08-26) on behalf of Memphis Community Against Pollution, Young Gifted & Green, Sierra Club: observed ≥18 turbines (four 16 MW Solar SMT-130 + ≥14 ~2.5 MW), ~100 MW, est. ~130 tpy NOx; argues NSPS KKKK applies (SMT-130 ≈155 MMBtu/hr) so "nonroad" 364-day exemption does not. — [Letter PDF](https://interactive.localmemphis.com/pdfs/2024-08-26-Letter-to-SCHD-re-xAI-operating-without-permits.pdf)
- SCHD permit (2025-07-02): 15 Solar SMT-130 turbines, up to 247 MW; rolling 12-month caps: NOx 87 t, CO 94 t, VOC 85 t, PM 73 t, HAPs ~14 t (9.8 t formaldehyde); xAI must keep records. SELC says up to 35 turbines (up to 421 MW) had operated without permits. SCHD had earlier said it lacked authority over "mobile" turbines operating <364 days. — [TechCrunch, 2025-07-03](https://techcrunch.com/2025/07/03/xai-gets-permits-for-15-natural-gas-generators-at-memphis-data-center); [Action News 5, 2025-07-02](https://www.actionnews5.com/2025/07/02/health-dept-grants-permit-xai-turbines/)
- xAI claim (via SCHD/Action News 5): on-site generation will use "state-of-the-art emissions control technology" making it "the lowest emitting of its kind in the country"; temporary turbines to be removed by end of July 2025. — [Action News 5](https://www.actionnews5.com/2025/07/02/health-dept-grants-permit-xai-turbines/)
- Memphis-Shelby County Air Pollution Control Board upheld permit 6–1 on 2025-12-15 after ~7-hour hearing; xAI counsel: temporary-turbine rules "clear as mud"; SCHD attorney said EPA discussions indicated temporary turbines didn't need permits; >30 temporary turbines had run under 364-day theory. — [Tri-State Defender, 2025-12-19](https://tri-statedefender.com/xai-permit-upheld-after-intense-shelby-county-air-pollution-control-board-hearing/12/19/)
- EPA final NSPS rule (signed 2026-01-09, Docket EPA-HQ-OAR-2024-0419): "Combustion turbines may, however, be mounted on a vehicle (or trailer) for portability and still be considered stationary"; creates new subcategory for "stationary temporary combustion turbines." — [EPA preamble PDF](https://www.epa.gov/system/files/documents/2026-01/for-website_preamble-clean-san11542-combustion-turbines-frm-20260108-eo-12866.pdf); NAACP/SELC characterization: [NAACP, 2026-01](https://naacp.org/articles/naacp-responds-epa-confirmation-large-methane-gas-turbines-require-permits)

xAI Southaven (DeSoto County, MS):
- MDEQ approved Clean Air Act construction permit for 41 turbines / 1.2 GW (meeting ~2026-03-10); xAI on X: "thrilled that MDEQ approved our permanent construction permit unlocking 1.2GW of self-generating power capacity." — [DCD, 2026-03-11](https://www.datacenterdynamics.com/en/news/musks-xai-gets-go-ahead-for-41-natural-gas-turbines-in-mississippi-to-power-colossus-data-centers)
- MDEQ retirement schedule for 69 trailer-mounted temporary generators (grew from 18 in Aug 2025 to 46 by May 2026): retirements begin 2026-08-18; majority retired by April 2027; 13 may exceed original 12-month deadline; newest units off by 2027-07-14. xAI says it is "rapidly removing" mobile turbines as the 1.2 GW plant comes online. — [Mississippi Today, 2026-07-31](https://mississippitoday.org/2026/07/31/southaven-xai-turbines-deadline/)

### Inferences
- The ERCOT queue figure tripled across 2025–mid 2026 (63 → 233 → 474 GW) while energized large load stayed single-digit GW; regulators themselves describe the queue as partly speculative.
- For xAI the record documents a ~12–18 month period of on-site gas generation before the first permit, and continuing temporary generation in Mississippi through 2027 under a state-set schedule.

### Gaps
- MDEQ's 41-turbine permit document (emissions limits, tpy) was not retrieved directly.
- No ERCOT-published figure for on-site/BYOG gas at Texas AI sites specifically; SB 6 requires disclosure but aggregated data not found.

---

## Key Question 3: Arizona / Nevada / Utah water and "water positive" claims

### Takeaway
Site-level withdrawals are mostly not public: City of Mesa reports industrial users at ~6% of potable use (2024) without naming companies; Goodyear's 2023 development agreement with Microsoft caps industrial discharge at 500,000 gal/day and requires air cooling after PHX-12. Operator claims (Microsoft "zero-water" designs since Aug 2024, >125 million L/yr avoided per site; Google 115 MW geothermal under Nevada's Clean Transition Tariff approved by PUCN May 2025) are documented but without facility-level public verification.

### Cited Findings
- City of Mesa (2024, document on ADWR-hosted infoshare, as cited by Grist): industrial water ≈6% of potable use; large users supplied ~7,800 acre-feet of supplemental supplies; city would not name companies. Ceres estimate: Phoenix-area data centers ~385M gal/yr. Microsoft: Arizona water-cooled sites consume water on net only >85°F; will build only zero-water sites in Arizona going forward. — [Grist, 2026-03-04](https://grist.org/technology/arizona-water-data-centers-semiconducters/)
- Goodyear development agreement (approved early March 2023): original plan five DCs each ≤1M gal/day evaporative; current limit 500,000 gal/day industrial discharge (TDS <1,400 mg/L); all DCs after PHX-12 air-cooled; Microsoft pays $36M toward ~$90M wastewater plant expansion. — [DCD, 2023-03-16](https://www.datacenterdynamics.com/en/news/microsoft-swapping-water-for-air-cooling-at-campus-in-phoenix-arizona/) (older than 2024 — marked)
- Microsoft claim (2024-12-09): all new designs since Aug 2024 use closed-loop chip-level cooling with zero evaporative water; avoids ">125 million liters of water per year per datacenter"; FY2024 WUE 0.30 L/kWh (vs 0.49 in 2021); Phoenix AZ and Mt. Pleasant WI pilots in 2026; new sites online from late 2027; "nominal increase" in energy. — [Microsoft blog](https://microsoft.com/en-us/microsoft-cloud/blog/2024/12/09/sustainable-by-design-next-generation-datacenters-consume-zero-water-for-cooling)
- Nevada CTT: Google/NV Energy (Sierra Pacific) filed ESA 2024-06-07; CTT docket 24-05023; Fervo 115 MW enhanced geothermal (Corsac Station) for Google's Storey County operations; NV Energy CEO: "will not be paid for by NV Energy's other customers." PUCN approved CTT week of 2025-05-15; ESA still required separate approval. — [Public Power](https://www.publicpower.org/node/23810); [Utility Dive, 2024-06-21](https://www.utilitydive.com/news/google-fervo-nv-energy-nevada-puc-clean-energy-tariff/719472); [Latitude Media, 2025-05-15](https://www.latitudemedia.com/news/the-clean-transition-tariff-won-approval-in-nevada-whats-next-for-fervo/)
- Google claim (2024-06-11): 115 MW new enhanced geothermal via CTT, "round-the-clock clean power" to the grid serving Nevada data centers; goal of 24/7 CFE by 2030. No hourly-matching verification mechanism described. — [Google blog](https://blog.google/outreach-initiatives/sustainability/google-clean-energy-partnership/)

### Inferences
- Arizona water records exist at city level (Mesa, Goodyear agreements) but not per-facility; "water positive" claims are corporate-global and are not reconcilable against local withdrawal data in the public record.
- Nevada CTT is a regulator-approved mechanism for firm clean supply, but the record contains no public hourly-matching audit.

### Gaps
- No ADWR permit or withdrawal figure per data center found for Arizona, Nevada, or Utah.
- PUCN order number/date for CTT approval not retrieved from PUCN's site directly.
- Utah-specific records not found within tool budget.

---

## Key Question 4: Georgia, Ohio, Indiana, Pennsylvania, Wisconsin, Louisiana, Oregon, Iowa

### Takeaway
Multiple state commissions approved large gas builds explicitly tied to large-load growth in 2025–2026: Georgia PSC (Dockets 56002/56003 and a 2025-12-19 certification of 9,885 MW, 5–0), LPSC (Docket U-37425, 3×754 MW CTs for Meta, 4–1, 2025-08-20), Wisconsin PSC (1,100 MW Oak Creek + 128 MW Paris, May 2025), PA DEP (Homer City air permit Nov 2025, up to 4.4–4.5 GW). PUCO's AEP Ohio tariff (2025-07-09) imposes 85% minimum bills. Court-ordered records in The Dalles show Google at ~29% (2021) rising to ~a third (2024) of city water. Positive counter-examples are documented in Seattle (Amazon/Westin heat recovery, ~4M kWh/yr) and Vancouver (TELUS Garden), though both predate 2024.

### Cited Findings
Georgia:
- Georgia PSC 2025 IRP stipulation (Dockets 56002 / 56003; agreed 2025-07-08): Georgia Power may seek certification of up to 8,500 MW from the 2029–2031 All-Source RFP; up to 4,000 MW renewables; forecast "depends largely on one customer class with limited historical data"; quarterly Large Load Economic Development Reports required. — [PSC stipulation PDF](https://services.psc.ga.gov/api/v1/External/Public/Get/Document/DownloadFile/223391/104616)
- PSC approved IRP 2025-07-15 (unanimous): 268 MW gas upgrades at McIntosh, >1,500 MW batteries, Scherer/Bowen coal to 2038; Georgia Power expects ~8,500 MW load growth over six years. — [Utility Dive, 2025-07-16](https://www.utilitydive.com/news/georgia-power-irp-coal-gas-plants-data-centers/753170/)
- Georgia Power certification request (2025-07-31): ~9,900 MW incl. five new company-owned combined cycles totaling 3,692 MW (Bowen 1,482; McIntosh 757; Wansley 1,453), 3,022.5 MW BESS, eleven PPAs 2,821 MW (gas + BESS). — [Georgia Power release via Finviz](https://finviz.com/news/123120/georgia-power-requests-certification-of-approximately-9900-mw-of-new-resources-from-the-georgia-public-service-commission)
- PSC media advisory 2025-12-19: 5–0 vote certifying 9,885 MW; "most of the new energy is intended to serve large new customers, such as data centers"; Georgia Power to backstop 2029–2031 project costs; rate freeze through 2028. — [PSC PDF](https://psc.ga.gov/site/assets/files/9176/media_advisory_dec_19_decision.pdf)

Ohio:
- PUCO order 2025-07-09 (AEP Ohio data center tariff): loads >25 MW pay ≥85% of subscribed capacity monthly, up to 12-year contracts, 4-year ramp; AEP Ohio had inquiries from >50 customers at >90 sites totaling >30 GW; central Ohio DC load ~100 MW (2020) → ~600 MW (2024) → ~5 GW projected 2030; moratorium since March 2023 ended. — [POWER, 2025-07-10](https://www.powermag.com/regulator-approves-aep-ohios-landmark-data-center-tariff/)

Indiana:
- IURC approved NiSource/NIPSCO Amazon data center power arrangement (reported 2026-06-23) and separately cleared NiSource CCGT and battery projects; article gives no MW. — [RTTNews, 2026-06-23](https://www.rttnews.com/3662043/nisource-wins-regulatory-approval-for-amazon-data-center-power-deal-in-northern-indiana.aspx)

Pennsylvania:
- Homer City (Indiana County): PA DEP issued air quality permit to Homer City Generation ~2025-11-18 (157 days vs 285 projected); 3,200-acre former coal site; $10B; "up to 4.4 GW" for data centers and homes; developer claims up to 65% lower emissions than former coal plant. — [Technical.ly, 2025-11-19](https://technical.ly/civics/homer-city-indiana-county-pennsylvania-data-center-permit-approval/)
- Project detail: up to 4.5 GW, seven GE Vernova turbines, first deliveries 2026, power from 2027; gas from Texas Eastern; $5M state grant; Knighthead ~75% owner per FERC filing; interconnections to PJM and NYISO. — [Utility Dive, 2025](https://www.utilitydive.com/news/homer-city-gas-fired-power-station-data-center-firstenergy/744332/)
- Talen/AWS Susquehanna: FERC denied amended ISA (300 → 480 MW co-located) 2–1 on 2024-11-01 (accession 20241101-3061), Christie and See voting no, Phillips dissenting; denied rehearing April 2025 (accession 20250410-3081). Talen 10-K FY2025: amended PPA June 2025, "up to 1,920 MW ... through 2042," transition to front-of-the-meter starting spring 2026, full by spring 2027, full volume no later than 2032. — [Power Engineering, 2024-11-04](https://www.power-eng.com/business/policy-and-regulation/ferc-rejects-amended-interconnection-agreement-for-amazon-data-center-at-susquehanna-nuclear-plant/); [ANS, 2025-04-16](https://www.ans.org/news/2025-04-16/article-6937); [Talen 10-K](https://www.sec.gov/Archives/edgar/data/1622536/000162253626000017/tln-20251231.htm)

Wisconsin:
- PSC Wisconsin approved 2025-05-22: Oak Creek 1,100 MW (five simple-cycle CTs, ~$1.2B) and Paris 128 MW RICE peaker; $456M LNG storage and $186M 33-mile pipeline also sought; We Energies cites "energy-intensive data centers." — [POWER, 2025-05-29](https://www.powermag.com/regulators-approve-plans-for-two-new-gas-fired-plants-in-wisconsin)
- Microsoft Mount Pleasant: 15-year contract signed 2025-07-16 after PSC (May) struck a provision requiring supply plants be in eastern WI/UP Michigan; contract retains struck language, We Energies says PSC order governs; We Energies seeking to buy Red Oak Ridge gas plant from Invenergy for $1.8B, Microsoft already contracted. — [Wisconsin Watch, 2026-08](https://wisconsinwatch.org/2026/08/wisconsin-we-energies-microsoft-data-center-contract-terms-conflict-psc-regulators-electricity/)
- Microsoft claim: Mt. Pleasant to pilot zero-water-evaporation cooling in 2026. — [Microsoft blog, 2024-12-09](https://microsoft.com/en-us/microsoft-cloud/blog/2024/12/09/sustainable-by-design-next-generation-datacenters-consume-zero-water-for-cooling)

Louisiana:
- LPSC minutes 2025-08-20, Docket U-37425 (Entergy Louisiana ex parte): settlement (Entergy, Staff, Sierra Club, Walmart, SREA) accepted 4–1 (Lewis objecting) authorizing generation and transmission for Meta's Holly Ridge data center, with "numerous protective conditions." — [LPSC minutes PDF](https://lpsc.louisiana.gov/docs/minutes/August-20-2025-Minutes.pdf)
- Terms as reported: three 754 MW CT plants (2,262 MW), $3.2B plants / ~$5B total incl. 500-kV line; 15-year contract with Meta subsidiary Laidley LLC; minimum bills to cover "100% of the cost of these three new generators"; Meta to pay for 1,500 MW solar/solar+storage; Meta may need 2.2 GW. — [S&P Global, 2025-08](https://www.spglobal.com/commodity-insights/en/news-research/latest-news/natural-gas/082025-louisiana-regulators-approve-new-entergy-infrastructure-for-10-bil-meta-data-center); [DCD](https://www.datacenterdynamics.com/en/news/entergy-obtains-approval-to-construct-three-gas-facilities-to-serve-metas-2gw-data-center-in-louisiana)
- LDEQ site permit: initial minor-source permit July 2025 (Laidley LLC) for 31 emergency diesel generators; amended 2026-06-06 to add 44 gas boilers; permitted 96.83 tpy NOx and 98.94 tpy CO (just under 100 tpy major-source threshold); Entergy's 10 turbines permitted separately. Sierra Club comments argue generator hours understate PTE. — [Louisiana Illuminator, 2026-08-04](https://lailluminator.com/2026/08/04/meta-data-center-pollution-permit-doesnt-account-for-all-its-emissions-sierra-club-says/)
- Meta claim (2025-12-19): ~4M sq ft campus; water restoration projects "will return 100% of the center's water consumption" to Boeuf/Tensas/Lower Mississippi watersheds; supporting three new clean energy projects in Louisiana; Entergy arrangement saves customers ~$650M over 15 years. — [Meta newsroom](https://about.fb.com/news/2025/12/metas-richland-parish-data-center-supports-louisiana-economy-875-million-in-contracts/)

Oregon (The Dalles):
- City sued The Oregonian in Wasco County Circuit Court (2021) to keep Google water data secret; settled Dec 2022 after 13 months; city to release 10 years of data and annual figures; city paid $53,000 to Reporters Committee, covered by Google. — [Courthouse News/AP, 2022-12-15](https://www.courthousenews.com/oregon-city-drops-fight-to-keep-google-water-use-private/)
- Released records: Google used 355 million gallons (2021), 29% of city consumption, roughly tripled since 2017; Google claim: equivalent to "1.8 golf courses," $28.5M water system upgrade adequate. — [WaterWatch summarizing Oregonian, 2022-12](https://waterwatch.org/googles-water-use-is-soaring-in-the-dalles-records-show-with-two-more-data-centers-to-come) (marked: 2022)
- 2026 update (OPB via Oregon Capital Chronicle, 2026-01-19): ~a third of city water to Google's three sites in 2024 (12% in 2012); ~1M gal/day; former smelter groundwater right up to 3.88M gal/day; city plans reservoir 900 → ~3,000 acre-feet (~$70M, ~2040); H.R. 655 would transfer forest land to city; Google says it offsets use via watershed projects and is not behind land transfer; Google paid $7.3M property tax in 2025 after 92% discount. — [Oregon Capital Chronicle](https://oregoncapitalchronicle.com/?p=19760)

Iowa:
- West Des Moines Water Works: Microsoft's five sites use 2–7% of monthly pumped water; 48,751,325 gallons Jan–Sep 2025; evaporative cooling per Water Works spokesperson. Microsoft 2025 sustainability report claims newer sites use closed-loop cooling and "water positive by 2030." Google says it replenishes 120% target, ~66% there. DNR permit required >25,000 gal/day. — [Business Record, 2025-11-28](https://www.businessrecord.com/energy-water-use-under-close-watch-as-data-centers-expand-in-iowa/)

Positive cases (heat reuse):
- Seattle: Westin Building Exchange (~400k sq ft, 70% data center) transfers up to 5 MW of heat to Amazon's Denny Triangle campus (~4M sq ft); ~4M kWh/yr saved; up to 3,000 gpm; McKinstry/Clise "Eco District"; first phase opened Dec 2015. — [BD+C, 2015-11-16](https://www.bdcnetwork.com/energy-efficiency/article/55148128/amazon-will-heat-its-new-seattle-campus-with-waste-heat-from-next-door-data-centers) (marked: 2015)
- Vancouver: TELUS Garden district energy centre owned/operated by FortisBC Alternative Energy Services, heat pumps + waste heat recovery from TELUS data centre, Creative Energy steam for peaking/backup (IDEA 2018 presentation). FortisBC projected ~1,000 t CO2/yr reduction (2013). — [IDEA document listing, 2018](https://www.districtenergy.org/viewdocument/the-faes-energy-centre-at-telus-gar); [DCD, 2013](https://www.datacenterdynamics.com/en/news/offices-and-homes-to-use-waste-heat-from-telus-data-center/) (marked: 2013/2018)
- Buffalo NY (Empire AI / University at Buffalo) and Kamloops BC (TRU/Bell AI Fabric) announced heat-reuse designs; no MW or verified figures. — [IDEA data center topic page](https://connect.districtenergy.org/topics/datacenters)

### Inferences
- In GA, LA, WI the regulator-approved gas additions are explicitly justified by large-load forecasts, and in each case the commission added ratepayer-protection conditions (minimum bills, backstops, 15-year contracts) rather than capping load.
- The Dalles is the clearest case of a public record created by litigation; the data show rising share of municipal supply alongside Google's "offset" claims.

### Gaps
- LPSC settlement document itself (conditions, in-service dates) not retrieved; MW/cost figures are from S&P/DCD reporting of Entergy filings.
- PSC Wisconsin docket numbers and the LDEQ permit PDF not retrieved.
- No verified post-2018 operating data for the Seattle or Vancouver heat reuse systems.

---

## Key Question 5: Canada (Alberta, Quebec, Ontario)

### Takeaway
Alberta: AESO capped near-term large-load connections at 1.2 GW (June 2025) against ~20.7 GW of proposals (33 projects, Sept 2025; 15/4.8 GW judged viable), and in June 2026 proposed a gas-only "bring your own generation" bridging pool of ~1.6 GW; AUC approved and Pembina took FID (2026-07-02) on the 932 MW Greenlight gas plant (C$4.6B, COD 2H 2030) for an unnamed data center customer. Quebec: Hydro-Québec proposed a ~13 ¢/kWh data-center tariff (Régie R-4333-2026; effective 2026-11-01 if approved) for ≥5 MW loads; 2025 data-center subscriptions total 187 MW peak / 662 MVA; sector forecast >1,000 MW by 2035; allocation by ministerial block process. Ontario: Bill 40 (Dec 2025) removed non-discriminatory access and let the Minister approve large-load connections; Aug 2026 Playbook proposes full-cost responsibility and a new GA rate class for data centers >1 MW.

### Cited Findings
- AESO interim approach (2025-06): up to 1.2 GW of large loads (≥75 MW) connectable to 2028; 29 data center projects, >1.4 GW in queue at that time; AESO CEO: connecting all would impair reliability. — [DCD, 2025-06-05](https://www.datacenterdynamics.com/en/news/alberta-grid-operator-launches-interim-plan-to-connect-up-to-12gw-of-data-centers-by-2028/)
- AESO BYOG draft (2026-06): 1.6 GW interruptible bridging pool, up to 3 years, gas-fired only ("renewables and hybrid facilities are not eligible for now"), electrical-island test, milestones; AESO reported 33 proposals / ~20.7 GW in Sept 2025, 15 / ~4.8 GW viable; Greenlight one of two projects allocated under the 1.2 GW cap; AUC approved Greenlight (1.8–1.9 GW ultimate) week before 2026-06-24. — [The Logic, 2026-06-24](https://thelogic.co/news/alberta-byog-large-load-plan/)
- Pembina FID (2026-07-02): Greenlight Electricity Centre 932 MW (2× Siemens SGT6-8000H CC), C$4.6B, Sturgeon County, ~150 MMcf/d gas, COD 2H 2030, tolling agreement with unnamed data center customer, expandable to 1,864 MW; no carbon capture claims. — [P&GJ, 2026-07](https://pgjonline.com/news/2026/july/pembina-reaches-fid-on-32-billion-alberta-gas-power-project-for-data-center); [Pembina release PDF](https://mms.businesswire.com/media/20260701575540/en/2844087/1/July_2%2C_2026_Press_Release_vF.pdf?download=1)
- Hydro-Québec release (2026-02-19): proposed data-centre rate ~13 ¢/kWh (≈double large-power rate) for new >5 MW customers; sector peak ~190 MW of 200 MW subject; >1,000 MW by 2035; crypto rate 19.5 ¢/kWh; government Orders in Council back it; existing DCs get 5-year transition. — [Hydro-Québec](https://news.hydroquebec.com/news/press-releases/all-quebec/hydro-quebec-proposing-regie-energie-new-rate-large-data-centres-adjustment-rate-cryptographic-use-applied-blockchains.html)
- Régie docket R-4333-2026, HQ response 2026-06-22: CD tariff ~13 ¢/kWh at 95% load factor (12 ¢ energy + ~2 ¢ capacity avoided cost); threshold ≥5 MW (block allocation starts there); 2025 DC subscriptions 187 MW peak, 662 MVA authorized (~93% of DC consumption); draft regulation 2026-05-13 aggregates requests over 4 years; proposed effective 2026-11-01; HQ would not disclose project-level pipeline. — [Régie PDF](https://www.regie-energie.qc.ca/fr/participants/dossiers/R-4333-2026/doc/R-4333-2026-B-0035-DDR-RepDDR-2026_06_22.pdf)
- Quebec framework: Bill 69 (June 2025); ministerial authorization for ≥5 MW; Decrees 88-2026 and 89-2026 (Jan 2026) set government concerns; selection criteria include heat-rejection recovery and benefits per MW; Rate LG under challenge in Superior Court. — [BLG, 2026-07](https://www.blg.com/en/insights/2026/07/data-centre-regulation-in-quebec-from-honeyed-promise-to-iron-control)
- QScale Lévis Q01: 96 MW IT design, 142 MW HQ reservation, Énergir heat recovery within 10 km (claimed enough for >15,000 households, projected not verified), 12 MW installed as of March 2023. — [SustainableBiz, 2023-03-23](https://sustainablebiz.ca/qscale-partners-with-energir-for-waste-heat-recovery-projects) (marked: 2023)
- Ontario: Bill 40 (Dec 2025) adds economic-growth mandate for IESO/OEB, removes non-discrimination principle, enables LGIC eligibility rules for large-load facilities and Minister approval of connections; Data Centre Playbook and draft GA rate class released 2026-08-13 (consultation to 2026-09-12): data centres >1 MW pay higher GA class, lose ICI eligibility, bear full generation/transmission upgrade cost; O. Reg. 429/04 amendment contemplated. — [Torys, 2026-08](https://www.torys.com/our-latest-thinking/publications/2026/08/new-framework-for-data-centre-grid-connections)

### Inferences
- Alberta is the only North American jurisdiction found where the grid operator has formally restricted a large-load bridging program to gas-fired generation.
- Quebec's record is unusually transparent on tariff cost basis but opaque on allocated MW per project.

### Gaps
- AUC decision number for Greenlight not retrieved.
- IESO connection-request GW totals for Ontario not located.
- Alberta government "strategy" dollar targets were not found in primary documents.

---

## Key Question 6: Mexico (Querétaro)

### Takeaway
CONAGUA data cited by Thomson Reuters Foundation (Sept 2024) show Microsoft holds a purchased concession of 25 million litres/yr in Colón (≈24% of the municipality's public-use allocation) in an aquifer (Valle de San Juan del Río) with a 56.8 billion-litre deficit; the state official said he had no data on data center water allocations. MEXDC/CFE figures (2026): Querétaro holds 72% of Mexico's 279 MW installed; CFE's transmission program adds up to 800 MW; some projects reportedly waited up to two years for connection.

### Cited Findings
- Microsoft concession 25 million L/yr in Colón = 24% of municipality's public/urban allocation (CONAGUA data); aquifer deficit 56.8 billion L (CONAGUA analysis); CONAGUA says no new concessions granted, Microsoft bought an existing one; Microsoft claim: water used "<5% of the year"; AWS claim: air-cooled design "will not require the ongoing use of cooling water"; state official del Prete: no data on allocations; 20 data centers statewide; Colón in "exceptional" drought Apr–Jul 2024. — [Context / Thomson Reuters Foundation, 2024-09-06](https://www.context.news/ai/thirsty-data-centres-spring-up-in-water-poor-mexican-town)
- CFE transmission reinforcement program for Querétaro adds up to 800 MW; CloudHQ campus US$4.8B, up to 900 MW, first 200 MW secured with CFE/CENACE; ODATA QR03 200 MW energized, 400 MW planned; MEXDC: national DC demand could exceed 1,400–1,500 MW. — [DCD (es), 2026-01-13](https://www.datacenterdynamics.com/es/noticias/la-cfe-fortalece-el-suministro-el%C3%A9ctrico-para-el-auge-de-centros-de-datos-en-quer%C3%A9taro/)
- MEXDC via Diario Rotativo (May 2026): Querétaro = 72% of 279 MW installed nationally; ~10 installed, 12 in development; ex-CRE chair García Alcocer: some DCs waiting "up to two years" for connection, bottleneck is transmission/distribution; CFE (Jan 2026) energizing two substations adding 26.8 MW; Governor Kuri denies DCs cause energy deficit. — [Xataka México, 2026-09-09](https://www.xataka.com.mx/robotica-e-ia/hay-centros-datos-queretaro-que-llevan-dos-anos-esperando-algo-basico-poder-conectarse-a-red-electrica)

### Inferences
- The only hard water number in the Querétaro record is a single Microsoft concession; the state itself reports no aggregate allocation data for the ~20 facilities.

### Gaps
- No CONAGUA concession document or CFE/CENACE interconnection list retrieved directly; figures are via TRF and DCD/Xataka citing them.
- No operator-reported facility water use for Querétaro.
