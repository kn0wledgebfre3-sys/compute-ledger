# AI Hardware Chain: Upstream Minerals & Fabs (A) and Downstream E-waste (B)

Scope: public record (USGS, UN/ITU/UNITAR, Basel Secretariat, Cochilco, SMA Chile, Eurostat, EPA, SEC filings, peer-reviewed journals) vs. company/government claims. Neutral tone; numbers always carry a URL. Checked 2026-10-19. Older sources (pre-2024) are flagged "[older]".

Method note: ~45 search/fetch calls. The per-turn web-search budget was exhausted near the end, so a few planned lookups (Taiwan WRA primary drought bulletins, Argentine provincial lithium regulators, Korean Ministry of Environment withdrawal records, Amazon/Alphabet 10-K Note 1 text directly from EDGAR, GEM 2024 server-specific text) could not be completed and are listed under Gaps.

---

## A1. Cobalt — DRC share, export quotas, ASM, water (what the record says vs. buyer claims)

### Takeaway
USGS puts DRC at ~73% of 2025 world mined cobalt (230,000 t of 310,000 t) and records a 2025 DRC export ban replaced by quotas; ASM share estimates in institutional sources range from 15–30% (historical) to ~2% (2024). Hardware buyers' SEC Form SD filings cover only 3TG, so cobalt traceability is asserted in voluntary reports, not statutory filings.

### Cited Findings
- World mine production 302,000 t (2024), 310,000 t (2025e); Congo (Kinshasa) 226,000 t (2024), 230,000 t (2025e), "an estimated 73% of world total mined cobalt." Indonesia 35,000 t (2024), 44,000 t (2025e), 14% share, second-largest. — [USGS MCS 2026 Cobalt](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-cobalt.pdf)
- DRC temporarily banned cobalt exports in February 2025; in October 2025 the ban was replaced by quotas of 18,125 t contained cobalt for the rest of 2025 and up to 96,600 t/yr for 2026–2027 (incl. 9,600 t for national strategic reserves). — [USGS MCS 2026 Cobalt](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-cobalt.pdf)
- ASM share of DRC cobalt: historical estimates 15–30%; a 2025 analysis citing Cobalt Institute/Gulley puts ASM at ~2% of global cobalt production in 2024, down from ~10% in 2020. ASM workforce 500,000–2,000,000 "directly or indirectly employed" (2023, Delve). Tree cover loss 1,400,000 ha/yr in 2023 (GFW). No water-quality figures in this profile. — [IISD DRC Country Profile, June 2026](https://www.iisd.org/system/files/2026-06/country-profile-democratic-republic-congo_0.pdf)
- RAID/AFREWATCH (March 2024): 172 interviews incl. 144 fenceline residents around five industrial cobalt-copper mines; fieldwork July 2022–Feb 2024 in 25 villages; cites ≥22 scientific studies and 20 civil-society reports documenting pollution of rivers/lakes/groundwater (copper, cobalt, lead, arsenic, cadmium, uranium, manganese, mercury). Companies responded that historic pollution and artisanal mining are largely to blame and that mines run "closed circuits"; "none provided audits or third-party assessments." (Key-findings PDF does not include the raw sampling table.) — [RAID Key Findings PDF](https://raid-uk.org/wp-content/uploads/2024/03/KEY-FINDINGS-DRC_Raid_Report_English_27-March.pdf)
- Apple Form SD for calendar 2025 (signed 28 May 2026) covers tin, tantalum, tungsten, gold only; "cobalt is not mentioned." States 100% of 3TG smelters/refiners are required to participate in annual third-party audit, and "found no reasonable basis for concluding" any financed armed groups in DRC/adjoining countries. — [Apple Conflict Minerals Filing 2026](https://s203.q4cdn.com/367071867/files/doc_downloads/2026/05/Conflict-Minerals-Filing.pdf)

### Inferences
- The statutory traceability record (Form SD) does not reach cobalt; cobalt traceability claims by hardware buyers live in voluntary reports that this research did not independently verify.

### Gaps
- No OECD or UN document with a 2024–2026 quantified water-contamination dataset around Kolwezi/Lualaba was retrieved (RAID full report with lab results not fetched).
- Could not retrieve a specific chip/GPU vendor's (e.g., Nvidia/AMD) cobalt refiner list and audit percentage.

---

## A2. Copper — Chile water use and desalination shift (Cochilco, regulator-published)

### Takeaway
Cochilco's June 2025 projection records a documented shift: seawater rose from 36.2% (2023) to 43.1% (2024) of copper-mining water and is projected at ~66% by 2034, with continental water falling from 12.02 to 7.6 m³/s. This is a positive, government-documented trend, though the same report shows internal figure inconsistencies.

### Cited Findings
- "Proyección de la Demanda de Agua en la Minería del Cobre 2024–2034" (DEEP 06/2025, RPI 2025-A-4407, Cochilco DEPP, June 2025): total water 18.8 m³/s (2023), 18.9 m³/s (2024), 22.1 m³/s (2034, +1.5%/yr). Continental 12.02 m³/s (63.8%) in 2023 → 10.76 m³/s (56.9%) in 2024 → 7.6 m³/s in 2034; seawater 6.81 m³/s (36.2%) → 8.16 m³/s (43.1%) → 14.5 m³/s (66%). Antofagasta Region: continental 3.82 → 2.84 m³/s (−25%), seawater 6.03 → 8.04 m³/s. 16 desalination plants operating/under construction, 6 further projects. Report shows internal inconsistencies (continental reduction 36.7% vs 35%; seawater share 66% vs 65.6%). — [Cochilco PDF](https://www.cochilco.cl/web/download/991/2025/13626/proyeccion-de-la-demanda-de-agua-en-la-mineria-del-cobre-periodo-2024-2034.pdf)
- A March 2026 Cochilco update (press summary): seawater 40.7% (2024) → 67.6% (2034); seawater 7.5 → 13.9 m³/s; total 18.5 → 20.6 m³/s. Figures differ slightly from the June 2025 PDF. — [Kitco/Reuters, 18 Mar 2026](https://www.kitco.com/news/off-the-wire/2026-03-18/chilean-miners-use-more-seawater-meet-rising-demand-2034)

### Inferences
- Two Cochilco vintages (June 2025 PDF; March 2026 update) disagree by 1–3 percentage points; the ledger should cite the primary PDF and flag the later update.

### Gaps
- Chilean DGA (Dirección General de Aguas) water-rights records and SEA RCA documents for specific Atacama mines were not retrieved (search budget exhausted). Peru and DRC copper water records not covered.

---

## A3. Lithium — Salar de Atacama brine extraction (SMA sanction record vs SQM claims)

### Takeaway
Chile's SMA began a sanction proceeding against SQM in November 2016 for brine over-extraction and incomplete information; the compliance program approved 30 Aug 2022 (>CLP 46 bn) staggers brine extraction down to 822 L/s by 2027 and industrial freshwater to 120 L/s. SQM separately claims a 50% brine cut by 2030 and 40%/65% water cuts by 2030/2040.

### Cited Findings
- SMA approved SQM Salar's compliance program (reported 30 Aug 2022) costing >CLP 46,000 million, addressing six infractions found in a proceeding begun November 2016; staged reduction of brine extraction to a maximum 822 L/s from 2027 ("slightly under 50%" of the limit authorised by RCA N°226/2006); total industrial water to 120 L/s (−50% vs RCA 226/2006). — [Diario Financiero](https://www.df.cl/sma-aprueba-programa-de-cumplimiento-para-sqm-salar-por-mas-de-46-000); corroborated by [Mining.com/Reuters, 30 Aug 2022](https://www.mining.com/web/chile-lithium-producer-sqm-gets-green-light-on-environmental-plan/) (USD 52 million; audit from 2016 found over-extraction and incomplete information; an environmental court mandated the earlier plan in 2020). [older]
- SQM claim (14 Oct 2020): cut brine extraction 50% by 2030 after an immediate 20% cut; cut water consumption 40% by 2030 and 65% by 2040 across all operations; 2019 comparison year; >USD 200 million Sustainability Plan (water ~USD 40 m phase 1 + USD 65 m phase 2). — [SQM press release](https://sqm.com/en/?p=6706) [older]
- SQM 20-F FY2024 restates "reducing water by 65% and brine extraction by 50% of our authorized limits" (no year in excerpt) and reports the 31 May 2024 Codelco partnership agreement (Minera Tarar exploitation rights 2031–2060; subject to indigenous consultation). — [SQM Form 20-F FY2024](https://www.sec.gov/Archives/edgar/data/909037/000090903725000020/sqm-20241231.htm)

### Inferences
- Regulator record and company claim are directionally consistent (≈50% brine cut); the regulator's number is in L/s and binds from 2027, while SQM's is a percentage with a 2030 horizon.

### Gaps
- Actual 2024 measured brine and freshwater extraction (L/s) from SMA/DGA monitoring not retrieved. Argentina (Catamarca/Jujuy/Salta) and Australia records not covered.

---

## A4. Nickel — Indonesia production, captive coal, deforestation

### Takeaway
USGS records Indonesia at 2.31 Mt (2024) and 2.6 Mt (2025e) of 3.71/3.9 Mt world nickel (~62–67%). GEM records 16.6 GW of captive coal in Indonesia at end-2024 (mostly nickel), and Climate Rights International's geospatial work records ≥5,331 ha cleared in Halmahera nickel concessions. No ESDM figures were retrieved.

### Cited Findings
- World nickel mine production 3,710,000 t (2024), 3,900,000 t (2025e); Indonesia 2,310,000 t (2024), 2,600,000 t (2025e); "Production in Indonesia increased by an estimated 13% as new operations continued to ramp up." — [USGS MCS 2026 Nickel](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-nickel.pdf)
- S&P Global: Indonesia produced 2.28 Mt nickel in 2024 (unreconciled "over 60%" vs "more than half" of world); Indonesia moved to one-year production-quota approvals for 2026. — [S&P Global, 6 Jan 2026](https://www.spglobal.com/market-intelligence/en/news-insights/research/2026/01/indonesia-mining-by-the-numbers-2024)
- Global Energy Monitor "Boom-Bust Coal 2025": Indonesia captive coal fleet 16.6 GW at end-2024 (~3× 2019), mostly tied to nickel processing; 160 MW newly proposed in 2024, all captive; 1.1 GW began construction in 2024. — [Eco-Business summary, 8 Apr 2025](https://www.eco-business.com/news/indonesia-stands-alone-in-southeast-asia-with-new-coal-proposals-in-2024-report/)
- Climate Rights International / UC Berkeley geospatial analysis: ≥5,331 ha forest cleared within nickel concessions on Halmahera; Weda Bay Nickel concession 1,456 ha forest loss as of 2022; IWIP has built 11 coal plants with 3 more planned (GEM). Eramet responded that WBN holds a permit and met compensation/rehabilitation requirements; Tsingshan and WBN did not respond. — [Mongabay, Feb 2024, summarising CRI report](https://news.mongabay.com/2024/02/indonesian-nickel-project-harms-environment-and-human-rights-report-says/)

### Inferences
- The captive-coal figure is from an NGO dataset (GEM) that is widely used by IEA/agencies; no Indonesian ministry figure was found to confirm or contradict.

### Gaps
- No ESDM/KLHK official tailings, HPAL, or deforestation figures retrieved. No peer-reviewed deep-sea-tailings study fetched.

---

## A5. Rare earths — China/Myanmar

### Takeaway
USGS records China at 270,000 t REO (2024 and 2025e, ~70% of world) and Burma at 27,000 t (2024) / 22,000 t (2025e), explicitly "estimated based on reported import data for China." Global Witness (May 2024) records >300 mining sites in Kachin Special Region 1 and China import data of 41,700 t heavy REO from Myanmar in 2023 (US$1.4 bn).

### Cited Findings
- World REO 380,000 t (2024), 390,000 t (2025e); China 270,000 t both years; Burma 27,000 t (2024), 22,000 t (2025e) "estimated based on reported import data for China"; US imports 2021–24: China 71%, Malaysia 13%. April 2025 China controls on Sm, Gd, Tb, Dy, Lu, Sc, Y; October 2025 expansion (Eu, Ho, Er, Tm, Yb); November 2025 one-year suspension of October controls, April controls remain. — [USGS MCS 2026 Rare Earths](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-rare-earths.pdf)
- Global Witness (23 May 2024): >300 sites in Kachin Special Region 1 by 2023 (+40% 2021–23); Momauk Township 9 sites (2021) → >40 (end-2023); China imports of heavy REO from Myanmar 19,500 t (2021) → 41,700 t (2023), US$1.4 bn in 2023; streams in Special Region 1 "highly acidic" with elevated arsenic (no numeric values given). — [Global Witness report](https://www.globalwitness.org/en/campaigns/natural-resource-governance/fuelling-the-future-poisoning-the-present-myanmars-rare-earth-boom/)

### Inferences
- The only official production figure for Myanmar is a USGS back-calculation from Chinese customs data; there is no Myanmar government record.

### Gaps
- UN (OHCHR/UNEP) documentation of Kachin mining impacts not retrieved; no peer-reviewed water-chemistry dataset fetched.

---

## A6. Gallium/germanium export controls

### Takeaway
USGS records China at 99% of world primary low-purity gallium (839,000 kg of 848,000 kg in 2024), August 2023 export controls, a December 2024 ban on exports to the US, and a one-year lifting in November 2025.

### Cited Findings
- China primary gallium 839,000 kg (2024), 900,000 kg (2025e); world 848,000 / 900,000 kg; "China accounted for 99% of worldwide primary low-purity gallium production." US metal imports 2021–24: Canada 28%, Japan 22%, China 18%, Germany 16%. Export controls August 2023; "China's ban of all gallium exports to the United States in December 2024"; "In November 2025, China lifted its ban on gallium exports to the United States for 1 year." — [USGS MCS 2026 Gallium](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-gallium.pdf)

### Gaps
- Germanium MCS 2026 chapter not fetched; Chinese MOFCOM announcement texts not fetched.

---

## A7. Chip fabrication — Taiwan 2021 drought, TSMC water, Arizona, Korea

### Takeaway
Taiwan's WRA recorded Baoshan Second Reservoir (Hsinchu Science Park supply) at 12% on 7 March 2021 and imposed 15% (rising to a conditional 17%) industrial water-saving requirements in Hsinchu/Taichung; TSMC said it relied on water trucks. TSMC's own 2025 report claims an 88.1% process-water recycling rate, 153.3 L per mask layer (above its 140.9 L 2010 baseline), and 18.2 Mm³ (Taiwan) + 108.9 Mm³ (overseas) tap water — figures not stated as externally assured. Arizona: 4.75 MGD, 65% recycled now, 90% claimed after a 2028 plant. Samsung's Korea fabs withdrew ~125 Mt (2022), with no reuse % published.

### Cited Findings
- WRA data 7 Mar 2021: Baoshan Second Reservoir 12%; Liyutan and Zengwen 15% each; water trucked from Taoyuan to Hsinchu; science parks allowed temporary wells. — [Taipei Times, 8 Mar 2021](https://www.taipeitimes.com/News/biz/archives/2021/03/08/2003753428) [older]
- WRA (19–20 May 2021): Hsinchu and Taichung park firms' water-saving rate to rise from 15% to 17% if supplies tightened after 1 June; WRA Deputy DG Wang Yi-feng: "Unless we get 100mm of total rainfall in reservoir catchment areas by May 31, Hsinchu is going on red alert." TSMC: "would rely more on water trucks." — [Taipei Times, 20 May 2021](https://taipeitimes.com/News/front/archives/2021/05/20/2003757719) [older]; central/southern reservoirs below 5%; 160 wells + desalination; TSMC buying tanker water. — [CNBC/Reuters, 19 May 2021](https://www.cnbc.com/2021/05/19/taiwan-steps-up-curbs-on-water-use-by-chip-hub-hsinchu-during-drought.html) [older]
- Sector water shares cited: agriculture ~70%, domestic ~20%, industry ~10%; Hsinchu tech firms asked to cut municipal water 13% (April 2021). — [AmCham Taiwan, May 2021](https://topics.amcham.com.tw/2021/05/water-shortage-threatens-taiwan-tech-industry-development/) [older]
- TSMC 2025 Sustainability Report (data year 2025): tap water Taiwan fabs 18.2 Mm³; overseas subsidiaries 108.9 Mm³; process water recycling rate 88.1%; total recycled water 318.94 Mm³ (+12% vs 2024); 153.3 L per 12-inch-equivalent mask layer (2024: 161.0 L; 2010 baseline 140.9 L; 122.3 L excluding new fabs). No ISAE/AA1000 assurance statement located in fetched text; AWS certification and ISO 14046 product water footprint verification mentioned. — [TSMC report PDF](https://esg.tsmc.com/en-US/file/public/e-APractitionerofGreenPower.pdf)
- TSMC 2024 Annual Report p.159: total water use (city + reclaimed) 114 Mm³ (2023) → 129 Mm³ (2024) for Taiwan fabs/subsidiaries; 2024 unit-water target −2.7% vs actual +14.3%, marked "Unachieved"; reclaimed water >67,000 m³/day cumulative supply, reduced city water 31% at Tainan. — [TSMC 2024 Annual Report p.159](https://investor.tsmc.com/static/annualReports/2024/english/ebook/files/basic-html/page159.html)
- TSMC Arizona (24 Aug 2026): 4.75 million gallons/day; 65% recycled (~3.5 MGD); supplied via City of Phoenix portfolio (mostly reclaimed, small groundwater share); Industrial Reclamation Water Plant to raise reuse "to 90% or better" but not fully operational until 2028; operates under City of Phoenix industrial pretreatment permit. No ADWR figure in article. — [AZFamily](https://www.azfamily.com/2026/08/24/arizonas-chip-footprint-grows-tsmcs-water-demand-sparks-questions/)
- Samsung Semiconductor Water Stewardship (data 2022): Korea sites 344,000 t/day; Hwaseong 51.038 Mt/yr, Giheung 22.450 Mt, Pyeongtaek 46.909 Mt (+9.931 Mt YoY), Onyang+Cheonan 4.985 Mt; China 17.601 Mt; US 10.190 Mt; water reused 235,000 t (Korea, 2022); Osan Stream discharge agreement 45,000 t/day; 2030 target hold withdrawal at 2021 level (0.3 Mt/day); AWS Platinum at Hwaseong 2022. No reuse rate % stated. — [Samsung PDF](https://download.semiconductor.samsung.com/resources/others/Samsung_Semiconductors_Water_Stewardship_ENG.pdf)

### Inferences
- The TSMC per-mask-layer figure (153.3 L in 2025) is above the 2010 baseline (140.9 L), so the 30%-reduction-by-2030 goal is further away than in 2010 on the reported metric.
- The Arizona 65% vs 90% figures are both company statements; the regulator-held record is a discharge permit, not a published withdrawal volume.

### Gaps
- Primary WRA bulletins (wra.gov.tw) not fetched. ADWR records for TSMC Arizona not fetched. Korean Ministry of Environment withdrawal records not fetched (Samsung's PDF cites MoE's National Water Management Master Plan only as a target-setting reference). SK Hynix not covered.

---

## B1. UN Global E-waste Monitor 2024

### Takeaway
GEM 2024 (ITU/UNITAR, 20 March 2024) records 62 billion kg generated in 2022, 22.3% formally collected/recycled, 5 billion kg of "small IT and telecommunication equipment" with 22% documented collection, and 5.1 billion kg moved across borders, of which 1.86 billion kg (35%) were controlled movements.

### Cited Findings
- 62 billion kg generated in 2022 (7.8 kg/capita); 13.8 billion kg (22.3%) documented as formally collected and recycled; Europe 42.8% documented rate, Africa <1%; 82 billion kg projected 2030 with rate falling to 20% BAU; 81 countries have e-waste legislation. — [ITU GEM 2024 page](https://www.itu.int/en/ITU-D/Environment/Pages/Publications/The-Global-E-Waste-Monitor-2024.aspx)
- Full report: "A total of 5.1 billion kg of e-waste were shipped across borders in 2022"; "an estimated 3.3 billion kg were shipped from high-income to middle- and low-income countries" (Exec. Summary p.17); "The remaining 1.86 billion kg (35 per cent of total transboundary movements) are shipped in the form of controlled movements" (p.42). Small IT & telecom equipment "totaled 5 billion kg in 2022" (p.29; table p.30 lists 4.6, figure 4.9) with "only 22 per cent... documented as formally collected and recycled" (p.14). Metals value USD 91 billion (p.16). Report is internally inconsistent on whether 5.1 bn kg refers to 2019 or 2022 (p.41 / Fig.16 say 2019). — [GEM 2024 PDF](https://ewastemonitor.info/wp-content/uploads/2024/12/GEM_2024_EN_11_NOV-web.pdf)

### Gaps
- GEM 2024 does not break out servers/data-center equipment as a category; "small IT" is the nearest proxy and excludes large servers (dimension >50 cm).

---

## B2. Basel Convention e-waste amendments and GPS-tracked leakage

### Takeaway
Decision BC-15/18 (2022) brought all e-waste (A1181 hazardous, Y49 non-hazardous) under prior-informed-consent from 1 January 2025. BAN's GPS studies recorded 34% of 205 US-deployed devices exported (2016) and 6% of 314 EU devices (2019, 3.5% to developing countries); BAN's October 2025 trade-data extrapolation claims 395,352 t/yr of US exports. Eighteen months after entry into force, BAN/Nexus3 presentations to the Basel OEWG-15 (June 2026) document 914 US containers at Batam, Indonesia.

### Cited Findings
- Amendments adopted by Decision BC-15/18 (COP-15, 2022); Annex VIII A1180 replaced by A1181 (hazardous e-waste), Annex II Y49 (all other e-waste); entry into force 1 January 2025; all e-waste movements subject to PIC. — [Basel Secretariat FAQ](https://www.basel.int/Implementation/Ewaste/EwasteAmendments/EwasteAmendmentsFAQs/tabid/10107/Default.aspx); status page: took effect for Parties that had not notified non-acceptance within six months of 1 July 2024. — [Basel status page](https://www.basel.int/Countries/StatusofRatifications/EwasteAmendments/tabid/10103/Default.aspx)
- BAN "Scam Recycling" (15 Sep 2016): 205 GPS trackers in US; 69 (34%) exported; 66 (96%) likely illegal; 37 of 69 to Hong Kong (mostly New Territories), 11 mainland China, 5 Taiwan, 4 Pakistan, 3 Mexico, 2 Canada; of 61 exports traced from recyclers, 23 from R2-certified and 3 from e-Stewards-certified. Internal inconsistency: 87% vs 84% to Asia. — [Report PDF (mirror)](https://resource-recycling.com/e-scrap/wp-content/uploads/sites/2/2016/09/BANReportTwo.pdf) [older]
- BAN "Holes in the Circular Economy: WEEE Leakage from Europe" (Feb 2019): 314 devices in 10 EU countries (Apr–Sep 2017); 19 (6%) exported, 11 (3.5%) to developing countries (Nigeria 5; Ghana, Hong Kong, Pakistan, Tanzania, Thailand, Ukraine 1 each); UK largest source (5); extrapolated 352,474 t/yr EU→developing countries. — [BAN release](https://www.ban.org/news-new/2019/2/6/gps-trackers-discover-illegal-e-waste-exports-to-africa-and-asia); report PDF: http://wiki.ban.org/images/f/f4/Holes_in_the_Circular_Economy-_WEEE_Leakage_from_Europe.pdf [older]
- BAN "Brokers of Shame" (22 Oct 2025): 10 US brokers exported >10,000 40-ft containers over 26 months; industry-wide extrapolation 32,947 t/month, 395,352 t/yr, 23,376 containers, USD 2.45 bn; 8 of 10 brokers R2V3-certified; >25 junkyards found in Hong Kong by trackers. (NGO extrapolation from trade data, not a government record.) — [Report PDF](https://wiki.ban.org/images/f/f7/Brokers_of_Shame_-_Report.pdf)
- Basel OEWG-15 side-event decks (25 June 2026): Batam, Indonesia 914 containers from US, 782 still at port, >650 slated for destruction (Apr 2026), 4 returned to US; Philippines ~234 suspected e-waste containers (by June 2026); Indonesia official e-waste generation 6,345.19 t (2023), 4,995.03 t (2024). — [Geneva Environment Network PDF](https://www.genevaenvironmentnetwork.org/wp-content/uploads/2026/06/Presentation-26June26_BaselOEWG-Ewaste.pdf)
- Basel national-reporting export dataset exists at parties' reporting archive (not parsed here). — [Basel export data page](https://www.basel.int/Countries/NationalReporting/NationalReportingArchives/Exportdataonhazardouswastes/tabid/1418/Default.aspx)

### Inferences
- The tracked-flow numbers (34% US, 6% EU) are sample-based and from an advocacy organisation; the underlying PDFs are cited directly as the task required. No government dataset was found that reconciles declared exports with tracked flows.

### Gaps
- Parsed Basel national-report export tonnages by country for 2022–2024 not extracted (dataset page located only). US is not a Party; no US federal export reporting dataset found.

---

## B3. EU WEEE collection rates (Eurostat)

### Takeaway
Eurostat (data extracted 28 Aug 2026) records 5.2 Mt WEEE collected in 2023 (11.6 kg/inhabitant), a 37.5% EU collection rate against the 65% legal target; only Bulgaria, Latvia and Slovakia met the target.

### Cited Findings
- EEE placed on market peaked at 14.4 Mt (2022 and 2023); WEEE collected 5.2 Mt (2023), 11.6 kg/inhabitant; collection rate 37.5% (2023) vs 65% target (rate = collected / average POM of 2020–2022); Bulgaria, Latvia, Slovakia met target; Czechia 61.7%. Category 6 "small IT and telecommunication equipment" (≤50 cm) defined but no category-level figure on page. — [Eurostat Statistics Explained PDF](https://ec.europa.eu/eurostat/statistics-explained/SEPDF/cache/32212.pdf)

### Gaps
- Category-6 (small IT) collection tonnage requires the env_waselee dataset, not fetched.

---

## B4. United States — no federal law; EPA figures; export destinations

### Takeaway
EPA's most recent national figures stop at 2018: 2.7 million short tons of selected consumer electronics generated and ~1 million tons recycled (~37%, calculated). No federal e-waste statute; BAN tracking and trade-data studies document Hong Kong, mainland China, Taiwan, Pakistan, Mexico and SE Asia as destinations.

### Cited Findings
- EPA: 2.7 million tons selected consumer electronics generated and about 1 million tons recycled in 2018; data "current through calendar year 2018"; no statement on a federal law. — [EPA Facts and Figures](https://www.epa.gov/facts-and-figures-about-materials-waste-and-recycling/national-overview-facts-and-figures-materials) [older]
- Destinations: see B2 (BAN 2016: Hong Kong 37/69; 2025: Batam 914 containers; Philippines ~234 containers).

### Gaps
- No state-level (e.g., California CalRecycle, Washington E-Cycle) datasets fetched (search budget). Absence of federal law is well known but no primary citation was retrieved in this run.

---

## B5. Destination sites — Agbogbloshie, Guiyu, Lagos, Delhi

### Takeaway
Agbogbloshie scrapyard (20 acres within ~80 acres reclaimed) was demolished 1 July 2021 under GARCC's "Let's Make Accra Work"; 15 acres earmarked for a hospital; by Jan 2025 ~100 unauthorised structures had reappeared. Guiyu's informal processors were ordered into a USD 230 m industrial park by start-2016 (≈400 large workshops moved, ~3,000 small ones pending in Nov 2015); a 2021 peer-reviewed study (2014 sampling) still found median child blood lead 8.5 vs 6.0 µg/dL in a control area. Lagos: UNU/BCCC-Africa "Person in the Port" recorded 60,000 t used EEE in 2015–16, ≥15,400 t non-functional, ~70% inside used vehicles, ~77% from EU (Germany, UK). Delhi: Toxics Link (2019) mapped 14–15 informal hotspots incl. Seelampur; no measured concentrations.

### Cited Findings
- Agbogbloshie: GARCC "stormed the Agbogbloshie Scrapyard" 1 July 2021 with police; scrapyard 20 acres within >80 acres reclaimed; ~15 acres for Ablekuma Central Municipal Hospital; onion traders to relocate to Adjen Kotoku; by 24 Jan 2025 ~100 unauthorised structures rebuilt. — [Daily Graphic, 24 Jan 2025](https://www.graphic.com.gh/news/general-news/ghana-news-agbogbloshie-reclaimed-land-under-siege-scrap-dealers-onion-sellers-occupy-80-acre-land.html); peer-reviewed study of 350 displaced workers (Sarpong, Müller-Mahn, Amankwaa, Mensah), IJURR. — [IJURR article](https://www.ijurr.org/article/behind-the-curtain-of-agbogbloshies-demolition-a-victims-perspective-beyond-revanchism/)
- Guiyu: all informal processors ordered to move to a USD 230 m park by start of 2016; ~400 large workshops moved by late Nov 2015, ~3,000 small businesses not yet (Xinhua/ecns, 10 Dec 2015; BAN visit 16 Dec 2015). — [E-Scrap News, 17 Dec 2015](http://resource-recycling.com/e-scrap/2015/12/17/chinas-guiyu-shifts-away-crude-processing/) [older]; children's blood lead (2014 sampling, 222 exposed vs 204 control): median 8.5 (IQR 6.6–10.9) vs 6.0 (4.8–7.9) µg/dL, P<0.01, Int Arch Occup Environ Health 94:911–918 (2021). — [PMC8238723](https://pmc.ncbi.nlm.nih.gov/articles/PMC8238723)
- Lagos (Person in the Port, UNU-SCYCLE & BCCC-Africa, 27 Apr 2018): 60,000 t UEEE imported 2015–2016; ≥15,400 t non-functional (≥15,600 t/yr best case); ~70% (41,500 t) inside used vehicles, mostly undeclared; ~77% from EU (Ro-Ro 98% EU); Germany and UK top origins; 3,622 import documents, 2,184 Ro-Ro vehicles, 201 containers inspected. — [Down To Earth summary](https://www.downtoearth.org.in/amp/story/waste/stuffed-inside-used-vehicles-thousands-of-tonnes-of-e-waste-reach-nigeria-every-year-60340) [older]; project flyer (UNU, US-EPA, BCCC Nigeria, ERI; from Jan 2015). — [UNU flyer](https://i.unu.edu/media/ias.unu.edu-en/news/5651/Flyer_Person_in_the_Port_Project.pdf) [older]
- Delhi: Toxics Link study (17 Oct 2019) lists hotspots incl. New & Old Seelampur, Mustafabad, Loni, Mayapuri, Seemapuri; Delhi-NCR generation 85,000 t (Assocham); no measured concentrations or worker counts. — [Down To Earth](https://www.downtoearth.org.in/news/waste/study-identifies-15-e-waste-processing-hotspots-in-delhi-operating-without-safeguards-67309) [older]

### Gaps
- No post-2021 Ghana EPA or UNEP site-monitoring data for the Agbogbloshie replacement site retrieved. No 2023+ Guiyu government monitoring data. Alaba market-specific (vs port) data not found.

---

## B6. Server/GPU lifecycle — depreciation lives vs circularity claims

### Takeaway
Amazon lengthened server lives 4→5 (2022) and 5→6 years (2024), then shortened a subset 6→5 years from 1 Jan 2025 citing AI/ML pace (+USD 1.4 bn depreciation); Alphabet moved servers 4→6 years from FY2023. Microsoft reports a 90.9% reuse-and-recycle rate for servers/components (FY24) with Deloitte limited assurance on its Section-1 waste/circularity tables; Google reports 7.5 M components harvested and 2.6 M resold in 2025 with UL 2799 validation only for zero-waste sites. No public filing states a physical lifespan for GPUs.

### Cited Findings
- Amazon: 1 Jan 2022 servers 4→5 yrs, networking 5→6 (depreciation −USD 3.6 bn); 1 Jan 2024 servers 5→6 (−USD 3.2 bn, net income +USD 2.5 bn); 1 Jan 2025 "a subset of servers and networking equipment" 6→5 yrs due to "the increased pace of technology development" in AI/ML (depreciation +USD 1.4 bn, net income −USD 1.0 bn, primarily AWS). — [Hudson Labs summary of 10-K language](https://www.hudson-labs.com/research/amazon-server-depreciation-amzn); primary filing: [Amazon 10-K FY2025](https://www.sec.gov/Archives/edgar/data/1018724/000101872426000004/amzn-20251231.htm) (Note 1 not reachable in fetched excerpt).
- Alphabet: servers 4→6 yrs, certain network equipment 5→6 yrs "beginning in fiscal year 2023"; Q1-2023 depreciation −USD 988 m, net income +USD 770 m. — [Converge Digest, 25 Apr 2023](https://convergedigest.com/google-extends-estimated-life-of-network-equipment-to-6-years/) [older]; primary filing: [Alphabet 10-K FY2025](https://www.sec.gov/Archives/edgar/data/1652044/000165204426000018/goog-20251231.htm) (Note 1 not reachable in fetched excerpt).
- Microsoft claim: "surpassed our target for our reuse and recycling rate for servers and components, reaching 90.9%"; packaging from >30,000 server racks recycled, >2,500 t diverted (FY24). — [Microsoft blog, 29 May 2025](https://blogs.microsoft.com/on-the-issues/2025/05/29/environmental-sustainability-report/); six Circular Centers (Amsterdam 2020; US, Ireland, Singapore), three more under construction; 3.2 M components reused. — [ESG News](https://esgnews.com/?p=35392)
- Microsoft assurance: 2025 Environmental Data Fact Sheet — Deloitte & Touche LLP review engagement (limited assurance) on Section 1 for FY24, covering GHG, energy, water, and "waste and circularity" Tables 10–12; "Microsoft obtains limited third-party assurance for the most recent year (FY24)"; diverted waste subtotal 17,149 t (FY22), 24,663 t (FY23), 28,285 t (FY24). The 90.9% server metric itself was not found in the fact-sheet excerpt, so its inclusion in the assured tables is unconfirmed. — [Microsoft Fact Sheet PDF](https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/microsoft/msc/documents/presentations/CSR/2025-Microsoft-Environmental-Data-Fact-Sheet-PDF.pdf)
- Google: 84% operational waste diverted across data centers (2024); ~8.8 M components harvested for reuse/resale (2024); two data centers + one warehouse UL 2799 validated as of 2025. — [Google Data Centers circularity page](https://datacenters.google/circularity); 2026 report (2025 data): >7.5 M components harvested, 2.6 M resold (>54 M since 2015), ZWL campuses 23% (2022) → 50% (2025); UL 2799 is the only named third-party check; no verifier named for component counts. — [E-Scrap News, 8 Jul 2026](https://resource-recycling.com/e-scrap/2026/07/08/what-googles-latest-report-means-for-itad/); report: https://sustainability.google/google-2026-environmental-report/

### Inferences
- Accounting lives (5–6 years) are management estimates for depreciation, not measured physical lifespans; the 2025 Amazon reversal is the only filing-level signal retrieved that AI hardware is treated as shorter-lived.
- Hyperscaler circularity figures are component counts and percentages without a public denominator in tonnes; assurance where present is "limited."

### Gaps
- No public filing or assured dataset giving GPU physical lifespan, GPU resale/refurbishment volumes, or Nvidia/AMD take-back figures was found. Could not confirm from EDGAR text directly (fetch truncation) the Amazon/Alphabet Note 1 wording; secondary summaries used and flagged.
