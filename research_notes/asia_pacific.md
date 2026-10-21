# Asia-Pacific datacenter and AI-compute footprint (public record vs. claims)

Scope: Singapore, Malaysia (Johor), Indonesia (Batam), India, Japan, South Korea, Taiwan, China, Australia. Research date 2026-10-19. Sources are government, regulator, grid-operator, statistical/planning portals, state-media reports of official statements, and established institutional research (ISEAS). Where only a news report of an official statement was reachable (not the underlying document), this is flagged. No figures were estimated; all numbers carry a URL. Vietnam, Thailand and the Philippines were not researched within the tool budget and are listed under Gaps.

Companion data file: `/home/claude/registry/asia_pacific.json` (14 entries).

---

## Singapore: moratorium, capacity allocated since 2022, conditions, roadmap figures

### Takeaway
Singapore lifted a "temporary pause" on new data centres in 2022, awarded ~80 MW in a 2023 pilot call and a further 200 MW in August 2026 (Jurong Island, >50% green energy), and in May 2024 published a Green DC Roadmap promising at least 300 MW near-term with a PUE ≤1.3 target. A tropical-climate operating standard (SS 697:2023) documents operator-reported cooling savings. This is largely a positive, well-documented example; the main gap is that the IMDA roadmap gives no deadline for the PUE target and the 200 MW award page states no numeric PUE or WUE condition.

### Cited Findings
- IMDA Green DC Roadmap: aims to provide "at least 300 megawatts (MW) of additional capacity in the near term"; existing total capacity "exceeding 1.4 gigawatts"; "We aim for all DCs to operate at Power Usage Effectiveness (PUE) of 1.3 or lower" (no deadline stated); Digital Connectivity Blueprint launched June 2023; roadmap described as a "living document" — [IMDA Green DC Roadmap](https://imda.gov.sg/how-we-can-help/green-dc-roadmap)
- Pilot DC-CFA (2023): "temporary pause in the growth of DCs" was lifted in 2022; four proposals provisionally awarded ~80 MW total: AirTrunk-ByteDance consortium, Equinix, GDS, Microsoft; awarded proposals include comprehensive liquid cooling, energy-efficient core IT, Green Mark DC Platinum. Page does not state PUE/WUE thresholds or a 2019 moratorium date — [IMDA press release 2023](https://imda.gov.sg/resources/press-releases-factsheets-and-speeches/press-releases/2023/four-data-centre-proposals-selected-as-part-of-pilot-data-centre-call-for-application)
- Second call (DC-CFA2): launched 1 Dec 2025; announcement 21 Aug 2026; Digital Realty 50 MW, Equinix 50 MW, Keppel 50 MW, ST Telemedia GDC 50 MW = 200 MW provisional; each "will power more than 50% of its capacity from green energy sources, exceeding the minimum requirement"; sited on Jurong Island (JTC low-carbon DC park); green pathways listed: biomethane, low-carbon ammonia/hydrogen, vertical BIPV/BAPV; footnote: liquid cooling can cut DC energy use by >30% vs air. No PUE/WUE number on the page; no cumulative total since the pause — [EDB fact sheet, DC-CFA2](https://www.edb.gov.sg/content/dam/edb-en/about-edb/media-releases/news/four-data-centre-proposals-selected-as-part-of-second-data-centre/Fact%20Sheet%20-Four%20data%20centre%20proposals%20selected%20as%20part%20of%20second%20data%20centre.pdf)
- DC-CFA2 call terms (law-firm summary, secondary): at least 200 MW offered; window closed 31 Mar 2026; ≥50% green energy; roadmap PUE <1.3 for new builds — [Morgan Lewis, Mar 2026](https://www.morganlewis.com/de/pubs/2026/03/singapore-announces-data-center-capacity-allocation-call)
- Tropical DC Standard SS 697:2023: methodology to raise operating temperatures to 26°C and above; "cooling energy savings of 2% to 5% for every 1°C increase"; reported adoptions: GovTech 24→26°C, up to 40% savings on in-hall cooling fans; BDx 7% cooling-energy cut; Digital Realty 2–3% total-energy cut across two 4.5 MW halls; Ready Server 160 kW at 29°C. Page last updated 23 Sep 2025 — [IMDA Tropical DC Standard](https://www.imda.gov.sg/how-we-can-help/green-dc-roadmap/tropical-dc-standard); [IMDA press release June 2023](https://imda.gov.sg/resources/press-releases-and-factsheets/press-releases/2023/imda-introduces-sustainability-standard-for-data-centres-operating-in-tropical-climates)

### Inferences
- Documented awards since the pause lifted: ~80 MW (2023) + 200 MW (2026) = ~280 MW provisional, slightly under the "at least 300 MW" roadmap figure; IMDA has not published a reconciliation.

### Gaps
- Exact moratorium start date (2019) and lifting date (Jan 2022) are not stated on the IMDA pages fetched; they appear only in secondary sources.
- No official page fetched gives numeric WUE conditions or the "minimum" green-energy share that the 200 MW awardees "exceed".
- No official statement found on cross-border low-carbon electricity imports being tied to DC awards.

---

## Malaysia / Johor: approved capacity, water and power concerns, 2024–2025 rejections, TNB tariff, claims

### Takeaway
TNB's own AGM materials record 5.9 GW of maximum demand secured from 38 data-centre projects as of Dec 2024, of which 1.9 GW (18 projects) was energised; actual December-2024 load was only 405 MW per ISEAS citing TNB. Johor's coordinating committee says it rejected nearly 30% of applications in Jun–Nov 2024 on water/energy grounds, stopped approving Tier 1/2 facilities in Nov 2025, and set a WUE threshold of 1.8; SPAN recorded 440 MLD of Johor data-centre water requests through 2035 (Ranhill SAJ estimate up to 614 MLD). The gap is between contracted capacity (5.9 GW) and realised load (405 MW), and between state assurances and the regulator's three-to-five-year sustainability warning.

### Cited Findings
- TNB AGM 2025 Appendix B: 5.9 GW maximum demand secured from 38 projects "as of December 2024"; 18 projects / 1.9 GW "already in the system"; 18 data centres commissioned under Green Lane Pathway in 2024; target of 5 projects / ~1.3 GW by end-2025; "remaining 2.7GW expected to come onstream in 2026" — [TNB AGM Presentation 2025 Appendix B](https://www.tnb.com.my/assets/energy_watch/AGM_Presentation_2025_Appendix_B.pdf)
- ISEAS Perspective 2025/43 (citing TNB report): 38 ESAs, 5.9 GW ≈ 43% of TNB supply; actual load utilisation Dec 2024 = 405 MW (~3%); 9 projects completed in 2024 with 1.3 GW max demand; TNB contracted capacity 13.76 GW; Green Lane Pathway cuts connection from 36–48 months to 12 months; proposed base tariff 39.95→45.62 sen/kWh (14.2%) for Jul 2025, PM denied that magnitude but confirmed a "slight increase"; RP4 grid capex RM26.5bn; renewables 8.3% of TNB output in 2023; MIDA/Johor guideline PUE ≤1.4 for hyperscale >21 MW (recommendation, not enforceable) — [ISEAS 2025/43](https://www.iseas.edu.sg/articles-commentaries/iseas-perspective/2025-43-data-centres-energy-demand-and-sustainability-can-malaysia-strike-the-right-balance-by-sara-loo/)
- Johor DCDCC (Lee Ting Han, vice-chairman): committee began scrutiny June 2024; nearly 30% of applications rejected in five months; 4 of 14 foreign-operator applications rejected; primary reason: failure to show sustainable water/energy practices, sites lacking utility infrastructure; Johor capacity 10 MW (2021) → ~1.3 GW (Nov 2024) → 2.7 GW projected 2027 — [NST, 19 Nov 2024](https://www.nst.com.my/amp/news/nation/2024/11/1136609/johor-rejects-30-cent-data-centre-bids)
- Johor (Datuk Mohd Jafni Md Shukor, 27 Nov 2025): 51 approved projects (17 operational, 11 under construction, 23 approved not built); state "will no longer approve Tier 1 and Tier 2" facilities; Tier 1/2 can use up to 50 million litres/day vs ~200,000 L/day for Tier 3/4; data centres must use reclaimed water rather than Syarikat Air Johor supply; committee reviews water/electricity use, WUE/PUE, cooling tech, alternative water; RM182.96bn investment — [NST, 27 Nov 2025](https://www.nst.com.my/amp/news/nation/2025/11/1324188/johor-tightens-approvals-data-centres)
- Johor (Mohamad Fazli Mohamad Salleh, 5 Jan 2026): WUE threshold 1.8 (same as Singapore); meeting it does not guarantee approval; Bridge Data Centres and Computility Technology told to use treated recycled sewage water; some projects directed to Johor Special Water for cooling-tower supply — [Malay Mail/Bernama, 5 Jan 2026](https://www.malaymail.com/news/malaysia/2026/01/05/how-johor-vets-data-centres-water-efficiency-utilities-and-location/204328)
- Johor (Fazli, 7 Feb 2026): 42 projects approved as of Q2 2025; earlier (~5-year-old) study found Johor groundwater "limited"; new groundwater study proposed; MoU with IWK for wastewater reuse — [Malay Mail, 7 Feb 2026](https://www.malaymail.com/news/malaysia/2026/02/07/with-data-centres-booming-johor-looking-into-groundwater-for-industry-needs/208322)
- SPAN (chairman Charles Santiago, 21 Jan 2025): Johor data-centre water requests 440 MLD through 2035 (+23% vs 2023); Ranhill SAJ estimates up to 614 MLD; Selangor 79 MLD to 2032; 52 data centres in Johor, 27 in Selangor; treated-water cooling "could become unsustainable within three to five years"; councils should require alternative supply plans — [Malay Mail, 21 Jan 2025](https://www.malaymail.com/news/malaysia/2025/01/21/with-data-centres-thirst-for-cooling-threatening-water-supply-span-pushes-for-urgent-conservation-measures-and-alternative-sources/164076)
- TNB target (Nov 2025, press): TNB eyes 5,000 MW of data-centre supply by 2035 — [NST, Nov 2025](https://www.nst.com.my/amp/news/nation/2025/11/1327006/tnb-eyes-5000mw-2035-support-malaysias-data-centre-expansion)

### Inferences
- Approved-project counts differ across state statements (42 as of Q2 2025; 51 as of Nov 2025) — consistent with continued approvals, but the state has not published a single reconciled register with MW.
- Johor "1.3 GW" (Nov 2024) likely refers to approved/pipeline capacity, not live IT load; ISEAS notes an unreconciled 1.6 GW figure and Knight Frank's 396.9 MW live IT figure.

### Gaps
- No primary SAJ/Johor water-approval documents were reachable; water figures rest on SPAN's press statements as reported.
- No Energy Commission (Suruhanjaya Tenaga) primary document on data-centre demand was located within budget; the 5,000 MW-by-2035 figure comes via press.
- Federal "sustainable data centre guidelines" (due end-2024) text not located.

---

## Indonesia (Batam)

### Takeaway
Government-side records are thin: a 2022 joint review by BP Batam, the Energy Ministry, BPKP and PLN Batam stated 11 data centres would require ~500 MW, and in July 2026 PLN Batam signed a PPA for two 150 MW gas combined-cycle units with Nongsa Digital Park data centres cited as a driver. No official PUE, water or renewable conditions were found.

### Cited Findings
- 24 Sep 2022 joint review (BP Batam, ESDM Ministry, BPKP, PLN Batam): "If 11 data centers have been realized, it will require 500 MW"; planned solar ≥40 MW (Tembesi) and 720 MW (Duriangkang reservoirs); long-term Sumatra–Batam interconnection 2,000–3,000 MW; Rempang could need 2,000 MW — [Antara, 24 Sep 2022](https://en.antaranews.com/news/251469/joint-review-conducted-on-batams-electrical-energy-security) (older than 2024 — flagged)
- 16 Jul 2026 PPA: Dalle Energy Batam and PLN Batam signed for two 150 MW gas/steam combined-cycle units (Batam 3 and 4); city secretary Firmansyah cited Nongsa Digital Park data centres as a major demand driver — [RRI (state broadcaster), 17 Jul 2026](https://www.rri.co.id/en/business/2575935/batam-secures-300-mw-power-boost-to-support-industrial-growth)

### Gaps
- No PLN Batam current installed-capacity figure, no data-centre load actuals, no water data found.
- The 2022 reservoir-floating-solar plans: no 2024–2026 official status update located.

---

## India: CEA/Ministry projections, state approvals, water records, Jamnagar

### Takeaway
The Ministry of Power told the Rajya Sabha (Jul 2026) that data centres are projected to consume 26.3 GW by FY2031-32 and will be included in the next National Electricity Plan (FY28–37); CEA is assessing emerging loads under the 21st EPS. State-level MW approvals and groundwater permits for Hyderabad/Mumbai/Chennai were not located in primary form; the AWS Telangana site (Jul 2026) has disclosed land and investment but not MW; Gujarat's 2026 policy requires ≥51% renewable sourcing and the Reliance-Meta Jamnagar site is reported at 168 MW initial with desalinated-seawater cooling (press-derived).

### Cited Findings
- MoS Power Shripad Naik, written Rajya Sabha reply (reported 31 Jul 2026): data centres projected to consume 26.3 GW by FY32; peak demand 270.8 GW reached, 300 GW projected next fiscal; transmission capex ~Rs 9.16 tn by FY32; data-centre demand to be included in NEP FY28–37 (expected Mar 2027); CEA assessing emerging loads under 21st EPS — [Construction World, 31 Jul 2026](https://www.constructionworld.in/policy-updates-and-economic-news/government-projects-26-gw-data-centre-demand-by-fy32/95339) (report of parliamentary reply; underlying PIB/Rajya Sabha text not fetched)
- CEA (per Mint, cited by Outlook Business): CEA "is set to direct states and power distribution companies" to include data-centre demand in resource adequacy plans; government "hopes" for ~$200bn investment and ~10 GW by 2030 from ~1.2 GW in 2025 — [Outlook Business](https://www.outlookbusiness.com/industry/india-data-centre-boom-power-demand-grid-planning) (secondary; no CEA document named)
- AWS Telangana: foundation stone ~15 Jul 2026 at Bharat Future City; ~Rs 60,000 crore (~$6.23bn) across phases; 202 acres Future City + 98 acres Chandanvelly = 300 acres; MW and building count "not disclosed"; minister D. Sridhar Babu cited "abundant clean energy" — [DCD, Jul 2026](https://www.datacenterdynamics.com/en/news/foundation-stone-laid-for-aws-data-center-development-in-telangana-india/)
- Gujarat "Viksit Gujarat Data Center Policy 2026-29": 7.5 GW target, ~Rs 6 lakh crore investment; ≥51% of core-operations electricity from green/renewable sources; electricity duty 100% reimbursed 20 years, Re 1/unit subsidy 20 years; essential-service status; Reliance-Meta Jamnagar initial 168 MW, renewable power and desalinated seawater cooling — [SuperKalam summary of Indian Express, 16 Jul 2026](https://superkalam.com/current-affairs/16-07-2026/green-energy-push-7-5-gw-capacity-target-gujarat-s-data-centre-policy-pg12-037f6c10-3313-4b69-8308-f866201d86b5) (tertiary; government notification not fetched — low confidence)
- CGWA NOC regime exists for groundwater extraction (amendment notice) — [CGWA amendment PDF](https://cgwa-noc.gov.in/landingpage/LatestUpdate/AmendmentforNOCs.pdf) — but no data-centre-specific NOC records for Hyderabad/Mumbai/Chennai were found.

### Gaps
- No primary CEA document with data-centre GW figures located; the 26.3 GW rests on a reported parliamentary reply.
- No state cabinet approval documents with MW for Telangana/Maharashtra/Tamil Nadu found within budget.
- Reliance Jamnagar "gigawatt" claim: only the 168 MW initial figure (press-derived) found; no Gujarat approval document.
- Groundwater permit records for specific data centres: none found.

---

## Japan: OCCTO/METI grid data and Hokkaido/Kyushu siting

### Takeaway
OCCTO's FY2025 national demand assumption (22 Jan 2025) individually counts +7.15 GW of peak demand by FY2034 from data centres and fabs (6.16 GW data centres), and +51.4 TWh/yr (44.0 TWh data centres), with notable increases in Hokkaido, Tokyo and Chugoku. METI/MIC's Watt-Bit roundtable summary 1.0 (12 Jun 2025) frames siting coordination. SoftBank's Tomakomai (Hokkaido) site claims >300 MW receiving capacity on 100% Hokkaido renewables from FY2026 (operator claim).

### Cited Findings
- OCCTO 需要想定 FY2025 (22 Jan 2025): "2034年度では＋715万kW が個別計上" (data centres 616万kW, fabs 99万kW); electricity 514億kWh (data centres 440億kWh, fabs 73億kWh); areas: Hokkaido, Tohoku, Tokyo, Chubu, Kansai, Chugoku, Kyushu; national peak FY2034 164,591 MW; national demand 852,438 GWh — [OCCTO PDF](https://www.occto.or.jp/juyousoutei/2024/files/250122_juyousoutei.pdf)
- METI/MIC Watt-Bit Collaboration Public-Private Roundtable Summary 1.0, 12 Jun 2025; roundtable launched Mar 2025; references GX2040 Vision (Cabinet decision Feb 2025) — [METI press release](https://www.meti.go.jp/press/2025/06/20250612001/20250612001.html) (siting specifics are in the linked PDF, not fetched)
- SoftBank Tomakomai: site 700,000 m²; "受電容量が300MW超まで拡大する見込み"; "北海道内の再生可能エネルギーを100％利用する"; FY2026 opening; industrial water cited for liquid cooling — [SoftBank site page](https://www.softbank.jp/business/service/platform/datacenter/tomakomai) (operator claim)

### Gaps
- Area-level FY2034 breakdown (table 2 of OCCTO) not extracted; Kyushu-specific figures not captured.
- No Hokkaido Electric Power record of the Tomakomai connection or of its renewable supply contract found.

---

## South Korea: KEPCO constraints and the 2024 distributed-energy law

### Takeaway
MOTIE's 11th Basic Plan projects data-centre consumption of 30 TWh and peak demand of 6.2 GW by 2038; KEPCO had 117 applications / 7,343 MW as of Aug 2023 and could supply 76 (4,718 MW). Under the grid impact assessment introduced Aug 2024 (Distributed Energy Act), lawmaker-released MOTIE/KEPCO data show 195 of 290 applications (Aug 2024–Jun 2025) were in the Seoul metropolitan area requesting ~20 GW; of 19 metro cases reaching MOTIE review, 4 passed (21%) vs 10 of 14 (71%) outside the metro area.

### Cited Findings
- 11th Basic Plan for Electricity Supply and Demand (MOTIE): data-centre consumption 30 TWh by 2038 (5.5% of 2023's 546 TWh; vs 8.2 TWh projected 2025); peak data-centre demand 6.2 GW by 2038; KEPCO: 117 applications, 7,343 MW as of Aug 2023, 76 cases / 4,718 MW suppliable; 2023 contracted 776 MW; 56 trillion won grid investment needed by 2036 (10th transmission plan) — [Asia Economy, 17 Mar 2025](https://asiae.co.kr/en/article/2025031717174507098)
- Rep. Kim Seong-won (MOTIE/KEPCO data), 29–30 Jul 2025: 290 applications nationwide Aug 2024–Jun 2025, 195 (67%) metro; metro requests ~20 GW (~20 reactors); 33 reached MOTIE review; metro 4/19 passed (21%), non-metro 10/14 (71%); grid impact assessment introduced Aug 2024 — [Dong-A via Daum, 30 Jul 2025](https://v.daum.net/v/20250730030438757)
- Grid impact assessment scoring: technical 60 / non-technical 20 / policy 20 points; 72.9% of private and 41.2% of public data centres in metro area; MOTIE (Choi Sung-jun) aims "to induce the establishment of large-scale power demand facilities in local areas"; Korea Data Center Association calls it a de facto "Data Center Prohibition Act"; agency fees >100m KRW per 10 MW reported — [Asia Economy, 5 Dec 2024](https://view.asiae.co.kr/en/article/2024120508501173795)

### Gaps
- MOTIE's own press release on the 11th plan and the assessment notice were not fetched; figures rest on press reports of official data.
- Fate of the 162 metro applications that did not reach MOTIE review is not stated.

---

## Taiwan: Taipower restrictions on northern data centres

### Takeaway
Taipower stopped accepting grid-supply applications for data centres ≥5 MW north of Taoyuan from August 2023 (sources differ: Aug vs Sep 2023), citing a northern generation shortfall (2023: 93 TWh demand vs 75 TWh generation per Executive Yuan data). In July 2026 the Economics Minister said the government is willing to relax the cap for sites near power plants (e.g., Taoyuan's planned AI zone near Datan), and Taipower said it would assess grid loading case by case.

### Cited Findings
- Taipower spokesperson Tsai Chih-meng (Aug 2024): applications ≥5 MW north of Taoyuan suspended from early Aug 2024 [sic, article dates the policy after Maanshan-1 retirement Jul 2024]; northern 2023 demand 93 billion kWh vs generation 75 billion kWh; 5 MW ≈ 2,500–3,500 households; "假如資料中心一直設置在北部，電網就會加速惡化…只好暫停受理"; Taipower encourages siting in central/south — [Business Next, 26 Aug 2024](https://www.bnext.com.tw/article/80273/taipower-denied-power-provide-to-data-centre-north-of-taoyuan)
- Economic Daily (27 Apr 2026): Taipower has refused >5 MW data-centre applications north of Taoyuan since Aug 2023; data-centre/AI capacity expected ~1 GW by 2030; MOEA strengthening planning/review with IDA and Energy Administration — [UDN, 27 Apr 2026](https://udn.com/news/story/7238/9465799)
- Taipei Times (16 Jul 2026): Taipower chair Tseng Wen-sheng says Taipower will support local AI DC zones near northern plants after grid/substation assessment; MOEA Minister Kung Ming-hsin willing to relax the 5 MW ban; Taoyuan plans AI computing centre near Datan plant; Datan gas units coming online; Concord (Xiehe) redevelopment cleared EIA; article dates suspension to Sep 2023 — [Taipei Times, 16 Jul 2026](https://www.taipeitimes.com/News/biz/archives/2026/07/16/2003860797)

### Inferences
- Dates for the start of the suspension conflict across sources (Aug 2023 / Sep 2023 / Aug 2024); no Taipower primary notice fetched to resolve.

### Gaps
- No Taipower primary document, application counts, or MW totals for refused applications located.

---

## China: PUE caps, green-electricity share, East Data West Computing, western hubs

### Takeaway
The July 2024 State Council–issued Data Centre Green and Low-Carbon Development Special Action Plan sets end-2025 targets: national average PUE <1.5, new/expanded large and super-large DCs ≤1.25, national hub-node projects ≤1.2, hub-node new DCs >80% green electricity, and a 2030 heat-reuse goal for northern heating regions. Official reporting puts 2024 national compute at 246 EFLOPS, 8.3m racks, average PUE 1.47. For western hubs, Xinhua reports Inner Mongolia's Helinger cluster at 84.57% green power in Q1 2025 and People's Daily reports Zhongwei (Ningxia) at 331,000 racks with a 1.5 GW wind + 500 MW solar direct-supply project; coal shares for these clusters were not reported in the sources fetched.

### Cited Findings
- 数据中心绿色低碳发展专项行动计划 (gov.cn, Jul 2024): "平均电能利用效率降至 1.5 以下" (end-2025); "新建及改扩建大型和超大型数据中心电能利用效率降至 1.25 以内"; "国家枢纽节点数据中心项目电能利用效率不得高于 1.2"; "可再生能源利用率年均增长 10%"; "国家枢纽节点新建数据中心绿电占比超过 80%"; by 2030 "北方采暖地区新建大型及以上数据中心余热利用率明显提升"; no numeric WUE; no coal data — [gov.cn PDF](https://www.gov.cn/zhengce/zhengceku/202407/P020240724272072479001.pdf); [gov.cn HTML](https://www.gov.cn/zhengce/zhengceku/202407/content_6964165.htm)
- Xinhua (21 Dec 2024): all 8 national hub nodes approved early 2022, 10 clusters; 2025 target >300 EFLOPS; 2024: 246 EFLOPS, >8.3m standard racks, national average PUE 1.47, 246 national green DCs; Ningxia Zhongwei target by 2025: PUE ≤1.2, renewable utilisation 65% — [Xinhua](https://www.news.cn/tech/20241221/14cb8d01f42d4964a7da90be593a30d5/c.html)
- Xinhua (30 May 2025), Inner Mongolia: cluster data centres 84.57% green power in Q1 2025 on 12.2亿kWh consumed; Inner Mongolia Energy Bureau director Cao Siyang: wind+solar capacity >1.35亿kW in 2024, surpassing thermal installed capacity; 79 DC projects, 2800亿元 investment; Ulanqab Ucloud recovers ~78,000 GJ/yr waste heat — [Xinhua](https://www.news.cn/politics/20250530/e5da7c9099b04454a53b00502b5c6fca/c.html)
- People's Daily (28 Jul 2026), Zhongwei: 331,000 standard racks citywide; 8 signed ultra-large AI projects, 1,885亿元; RMB 8.7bn green direct-supply project operational May 2026; 1.5 GW wind + 500 MW solar, 4.3 bn kWh/yr "basically sufficient" for cluster; losses <3% via dedicated lines; electricity >60% of operating cost — [People's Daily](https://cpc.people.com.cn/n1/2026/0728/c64387-40769368.html)
- Carbon Brief explainer (institutional, citing primary): 2022 DC consumption 77 TWh (DRC); IEA 100 TWh in 2024; most DCs in east where ~70% of electricity is coal (IEA); 2021 action plan cut average PUE 1.54→1.48 (CAICT) — [Carbon Brief](https://www.carbonbrief.org/explainer-how-china-is-managing-the-rising-energy-demand-from-data-centres/)

### Inferences
- The hub-node 80% green-electricity target is a share-of-supply metric; Inner Mongolia's reported 84.57% applies to one cluster in Q1 2025 and is not an annual or provincial coal-share figure.

### Gaps
- No NBS/provincial statistical bureau coal-generation share for Inner Mongolia, Ningxia, Guizhou located within budget; Inner Mongolia's "wind+solar > thermal installed capacity" is a capacity figure, not generation.
- Guizhou cluster official PUE/green-share data not fetched.

---

## Australia: AEMO forecasts, Sydney water and grid

### Takeaway
AEMO's 2026 ESOO data-centre overview records ~5 TWh (3% of NEM consumption) from ~165 data centres in FY26, rising to ~15 TWh (7.8%) by FY30 and ~34 TWh (13%) by FY36 under Step Change; 225 projects / 67 GW in development with 36% of 2025-ESOO projects cancelled and ~27% grid-connection utilisation. NSW Planning confirmed 10 state-significant data centre approvals (all approved) projecting up to 9.6 GL/yr potable water; Sydney Water projected up to 135 GL (a quarter of available supply) by 2035. NSW has no numeric water-use rule beyond "minimise potable water".

### Cited Findings
- AEMO 2026 ESOO data-centre forecasting overview: FY26 ~5 TWh (~3%), ~165 data centres; monthly average demand ~200 MW (Jan 2018) → >700 MW (Jun 2026); Step Change: ~15 TWh (7.8%) FY30, ~34 TWh (13%) FY36; 225 projects / 67 GW in development; 36% of 2025 ESOO projects cancelled; connection utilisation ~27% FY26; NSW 66%, Vic 30% of FY26 demand — [AEMO PDF](https://www.aemo.com.au/-/media/files/electricity/nem/planning_and_forecasting/nem_esoo/2026/2026-esoo-data-centre-forecasting-overview.pdf); methodology note — [AEMO news](https://www.aemo.com.au/newsroom/news-updates/aemos-updated-forecasting-methodology-targets-rapidly-growing-electricity-loads)
- NSW Planning / Sydney Water (Reuters via Malay Mail, 15 Sep 2025): 10 applications ruled on since 2021, all approved, A$6.6bn; up to 9.6 GL/yr clean water (~2% of Sydney max supply); Sydney Water: up to 135 GL (a quarter of available water) by 2035; AirTrunk 320 MW, rainwater cuts potable use 0.4%; two Amazon centres 195.2 MW, up to 92 ML/yr; state rule: must be "satisfied that the development contains measures designed to minimise the consumption of potable water"; Ryde council 11 centres ~3% of its supply, called for moratorium; AirTrunk says later modelling shows "significantly lower" usage — [Reuters/Malay Mail](https://malaymail.com/news/world/2025/09/15/data-centres-are-booming-in-sydney-but-whos-keeping-track-of-how-much-drinking-water-theyre-using/191230)
- NSW Planning Portal, Road 1 Data Centre (SSD-80814238), Macquarie Park, 34.3 MW, approved 1 Oct 2026 by Director, DPE; Sydney Water Growth Data Form attached; no water volumes on page — [NSW Planning Portal](https://www.planningportal.nsw.gov.au/major-projects/projects/road-1-data-centre)

### Gaps
- Determination conditions (water/power) for Road 1 not extracted (attachment).
- Victoria/Melbourne water and grid records not researched.

---

## Not researched (budget)
- Vietnam, Thailand, Philippines: no entries.
- Japan Kyushu site-level data; Korea KEPCO primary notice; India primary CEA/CGWA records; Guizhou provincial data.
