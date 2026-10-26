# Europe: Datacenter and AI-Compute Physical Footprint (public-record ledger notes)

Scope: Ireland, Netherlands, Nordics, Germany, UK, Spain, France, Italy, Poland, Switzerland. As of 2026-10-19. Sources prioritised: statistical offices, regulators, grid operators, courts, planning boards, utilities, municipalities, and the operators' own statements. Trade-press items (DCD, NL Times, Energías Renovables) are used only where they quote or link a primary document; those cases are flagged. Items older than 2024 are marked **[older]**.

Method note: Several primary PDFs could not be fetched directly in this session (gesetze-im-internet.de EnEfG §11 was refused; the Foxglove-hosted Portsmouth Water PDF and the Business & Human Rights Resource Centre page returned fetch errors). Where that happened, the figures are taken from a secondary document that cites the primary, and the gap is recorded.

---

## Ireland: CSO datacenter share, EirGrid/CRU connection policy, on-site gas generation

### Takeaway
The CSO's official metered-consumption series puts data centres at 23% of Ireland's metered electricity in 2025 (7,663 GWh), up from 22% in 2024 and 5% in 2015. The CRU's December 2025 Large Energy Users decision (CRU/2025236) now requires new data-centre connections ≥10 MVA to bring dispatchable on-site/proximate generation or storage equal to their import capacity, plus an 80% Irish-renewables matching requirement; An Bord Pleanála refused a Vantage Dublin data hall in 2025 because, without a grid agreement, on-site gas could become the primary supply ("islanded"), which conflicts with the 2022 Government Statement.

### Cited Findings
- CSO "Data Centres Metered Electricity Consumption 2025" (published 7 July 2026): data centres = 23% of metered electricity in 2025, up from 22% in 2024 and 5% in 2015; urban dwellings 18% and rural dwellings 9% (down from 22%/12% in 2015). Source is ESB Networks meter data (~2.6 million meters). — [CSO release](https://www.cso.ie/en/releasesandpublications/ep/p-dcmec/datacentresmeteredelectricityconsumption2025/)
- Absolute figures reported from the same CSO release: 7,663 GWh in 2025 vs 6,973 GWh in 2024 (+10%); 1,240 GWh in 2015 (+518% over 2015–2025); non-datacentre consumption 23,360 GWh (2015) to 25,324 GWh (2025) (+8.4%); quarterly consumption 291 GWh (Q1 2015) to 1,991 GWh (Q4 2025). — [Irish Times, 7 Jul 2026](https://www.irishtimes.com/business/2026/07/07/data-centres-account-for-almost-one-quarter-of-irish-electricity-usage-in-2025/); [FactCheckNI (links the CSO release)](https://factcheckni.org/articles/energy-on-this-island-do-irelands-data-centres-now-consume-nearly-a-quarter-of-all-electricity-in-the-south/)
- CRU Large Energy Users Connection Policy Decision CRU/2025236, 12 December 2025: applies to new data-centre connection applications made after that date. 1–<10 MVA: on-site generation covering 100% of MIC (de-rated), registered as behind-the-meter autoproducer. ≥10 MVA: dispatchable on-site or "proximate" generation and/or storage ≥ MIC, separately metered, participating in wholesale and capacity markets; connection cannot ramp to full MIC until delivered. All ≥1 MVA: ≥80% of annual demand from additional Irish renewable electricity (CPPA or own build), 6-year glide path. CRU notes 97% of Irish data centres are in Dublin, where grid constraints are "particularly prevalent". "Islanded" gas-only data centres are "not consistent with national policy". System Operators must publish locational capacity/constraint maps; initial proposals due 31 March 2026. New data centres may only bid one-year capacity contracts. — [Matheson summary of CRU/2025236 (PDF)](https://media.matheson.com/wp-content/uploads/2026/02/Large-Energy-Users-Connection-Policy-Decision-3.pdf); proposed decision text: [CRU202504 (PDF)](https://consult.cru.ie/en/system/files/materials/200/CRU202504%20LEU%20connection%20policy%20proposed%20decision_0.pdf)
- Government Large Energy User Action Plan (LEAP) published 13 January 2026 supporting plan-led siting near renewables / "green energy parks", especially from 2030. — [Matheson (PDF)](https://media.matheson.com/wp-content/uploads/2026/02/Large-Energy-Users-Connection-Policy-Decision-3.pdf)
- An Bord Pleanála case ABP-317446-23 (South Dublin ref SD22A/0420), Vantage Data Centers DUB 11 Ltd, Profile Park, Clondalkin: 12,893 m² data hall "DUB 13", 13 emergency backup generators, referencing "permitted on-site gas powered generation". Decision: REFUSE (2025), against the Inspector's recommendation to grant. Reasons: no fixed grid connection agreement demonstrated; without it the Board could not rule out on-site gas becoming the primary energy source, conflicting with the 2022 Government Statement on Data Centres ("islanded" developments not in line with national policy) and Climate Action Plan 2024; EIAR did not assess the no-grid-connection scenario. — [ABP Board Order (PDF)](https://www.pleanala.ie/anbordpleanala/media/abp/cases/orders/317/d317446.pdf); [ABP Board Direction (PDF)](https://www.pleanala.ie/anbordpleanala/media/abp/cases/directions/317/s317446.pdf)
- **[older, 2022]** EirGrid spokesperson statement: greater Dublin "is a constrained area and will remain so for the foreseeable future"; press reports gave 2028 as the earliest date for new Dublin connection agreements. — [DCD, 11 Jan 2022](https://www.datacenterdynamics.com/en/news/eirgrid-says-no-new-applications-for-data-centers-in-dublin-till-2028); [Business Post](https://www.businesspost.ie/energy/new-dublin-data-centres-barred-from-connecting-to-national-grid-dca6ab74)
- **[older, 2022]** EirGrid closed out just under 30 data-centre connection applications "in line with the CRU direction"; in June 2021 EirGrid had approved 1,800 MW of future data-centre capacity against 2,000 MW of applications. — [DCD, 24 May 2022](https://www.datacenterdynamics.com/en/news/eirgrid-pulls-plug-on-30-irish-data-center-projects/)
- Operator/industry claim: the EU EED first report indicates Irish data-centre operators reported to the EU database at a rate of roughly 1 in 6 of expected facilities. — [Green Web Foundation summary of EC report](https://www.thegreenwebfoundation.org/news/what-weve-learned-about-the-sustainability-of-datacentres-in-europe-from-the-eed/)

### Inferences
- The CSO 23% share is a metered-consumption share (ESB Networks meters), not a share of generation or of total final energy; it is the most defensible single national figure in Europe.
- The 2025 CRU decision effectively converts the 2021 "constrained-area" criteria into a firm requirement for dispatchable on-site capacity, which may increase on-site gas/storage footprints unless operators choose storage.

### Gaps
- The CSO release page fetched did not expose the GWh table directly; GWh figures are taken from the Irish Times and FactCheckNI, both of which cite the CSO release. The CSO "Key Findings" sub-page should be checked for the 7,663 GWh figure.
- No 2024–2026 primary EirGrid document stating the current Dublin connection status was located; the "2028" figure is 2022 press reporting.
- No operator public claim specific to the Vantage DUB 13 refusal was found.

---

## Netherlands: Amsterdam/Haarlemmermeer policy, TenneT congestion, Zeewolde Meta, Middenmeer Microsoft water

### Takeaway
Amsterdam's revised Vestigingsbeleid (first revision, 2024–2026) removes the earlier 67 MW/yr growth allowance (670 MVA by 2030) so no further growth is currently possible under the policy; TenneT's congestion in Noord-Holland was upheld in court in April 2026 (ECLI:NL:RBGEL:2026:3358) when Goodman's 70 MW Vijfhuizen connection claim was dismissed. The Zeewolde Meta campus (200 MW) was cancelled in 2022 after the national government declined to sell the land and introduced a national hyperscale siting rule (>10 ha, ≥70 MW limited to Hollands Kroon and Het Hogeland). Microsoft Middenmeer's 2021 drinking-water use (84 million litres, vs a 12–20 million litre estimate) remains the best-documented water discrepancy in the region.

### Cited Findings
- Amsterdam Vestigingsbeleid datacenters 2020–2030, eerste herziening (hosted by Omgevingsdienst Noordzeekanaalgebied): original 2020 policy capped growth at 67 MW/yr (670 MVA total by 2030); revised policy removes the growth allowance so no further growth is currently possible. 2024 contracted capacity in Amsterdam ≈150 MW, recorded peak ≈100 MW. Designated areas: Haven, Schinkelkwartier, Amstel III, Sciencepark, Weesp. Residual-heat use mandatory (no %); groundwater extraction prohibited; drinking-water use ≈1–1.5% of supply, Waternet expects to stay below 5%. Preparatory decision 8 Nov 2023; draft published 28 Dec 2023. — [Vestigingsbeleid eerste herziening (PDF)](https://odnzkg.nl/wp-content/uploads/2026/07/Vestigingsbeleid-datacenters-2020-2030-Amsterdam-Duurzaam-Digitaal-eerste-herziening.pdf)
- Rechtbank Gelderland, kort geding, ECLI:NL:RBGEL:2026:3358, published 29 April 2026: Goodman's claims against TenneT dismissed. Grid in the Vijfhuizen focus area is full; several applicants including Goodman placed on a waiting list; Goodman was not a "contracted customer" (no ATO concluded); TenneT paused the connection process in early 2026; Goodman stays on the waiting list until capacity is available. — [Rechtspraak.nl news release](https://www.rechtspraak.nl/organisatie-en-contact/organisatie/rechtbanken/rechtbank-gelderland/nieuws/2026/04/tennet-niet-gehouden-tot-hervatten-aansluittraject-projectontwikkelaar)
- Same case, press detail: Goodman requested a 70 MW connection at the Vijfhuizen substation near Schiphol; sought €500,000/day penalty from 1 June 2026; constraints may persist until around 2035. — [NL Times, 29 Apr 2026](https://nltimes.nl/2026/04/29/judge-rules-electricity-grid-haarlemmermeer-full-data-centre-connection-delayed)
- Trade-press summary (not primary): ~1,340 MW operational IT load in Amsterdam metro; TenneT congestion declared across large parts of Noord-Holland/Flevoland from 2021; ~4.6 GW unmet connection requests (all sectors) in the province by mid-2026; new 380 kV Wieringermeer–Ens line targeted 2029; 2019 Amsterdam/Haarlemmermeer moratorium on >10 MW campuses lifted 2022; requests >50 MVA effectively paused since 2023. — [datacentres.com, 8 Sep 2026](https://www.datacentres.com/news/amsterdam-data-centre-market-1-340-mw-live-as-tennet-s-grid-congestion-locks-out-slot2-2026-09-08)
- Province of Noord-Holland commissioned Dialogic report: 67 data centres in 2025, 83 by 2030, 92 by 2035 if ~20 pending permits proceed. — [Dutch IT Channel, 3 Jul 2026](https://www.dutchitchannel.nl/news/754916/aantal-datacenters-in-noord-holland-stijgt-naar-92-in-2035)
- **[older, 2022]** National hyperscale rule: cabinet agreed 10 June 2022 to Minister De Jonge's draft decision restricting new hyperscale data centres (>10 ha and ≥70 MW) to Hollands Kroon and Het Hogeland, applying to applications after the 16 Feb 2022 temporary stop; Zeewolde Meta was the one exception; Rijksvastgoedbedrijf did not want to sell the required land. — [NOS, 10 Jun 2022](https://nos.nl/l/2432219)
- **[older, 2022]** Meta cancelled Zeewolde (five data halls, 200 MW at full build) after a March 2022 Senate vote to halt site works; Meta said building in Zeewolde "is not the right investment". — [DCD, 1 Jul 2022](https://datacenterdynamics.com/en/news/facebook-parent-meta-officially-kills-zeewolde-data-center-after-pushback-in-the-netherlands)
- **[older, 2021 data / 2022 reporting]** Microsoft Middenmeer: 84 million litres of drinking water in 2021 (municipality Hollands Kroon figures: 75 million for cooling, 9 million other) versus a 12–20 million litre/yr estimate given by Microsoft and the municipality. Microsoft response: figure includes construction water; mature site on track for ~10 million litres/yr; 36 million litres were discharged back, net ≈48 million. — [DCD, 16 Aug 2022](https://datacenterdynamics.com/en/news/drought-stricken-holland-discovers-microsoft-data-center-slurped-84m-liters-of-drinking-water-last-year)
- Microsoft AMS13/14 Middenmeer permit (OD NZKG, April 2023): two 36 MW buildings, 14.4 ha, cooling "direct air system with an evaporation system", estimated PUE 1.18, 40 × 3.3 MW + 2 × 1 MW backup generators. — [DCD, 21 Apr 2023](https://datacenterdynamics.com/en/news/microsoft-gains-construction-permission-for-data-center-in-hollands-kroon)

### Inferences
- The Amsterdam policy is a case of a municipal cap that was tightened rather than relaxed; combined with TenneT congestion it has produced a de facto freeze on large new connections in the metro.

### Gaps
- No TenneT congestion-map document with a stable URL and MW figures was captured; the 4.6 GW figure is trade-press. The TenneT "capaciteitskaart" should be cited directly.
- The Vestigingsbeleid first-revision adoption date was not in the fetched text.
- No 2024–2026 municipal water figures for Middenmeer were found; the water record is 2021.

---

## Nordics: Finland (Espoo, Hamina), Denmark, Norway, Sweden

### Takeaway
The two best-documented positive heat-reuse cases in Europe are Finnish: Fortum's Espoo/Kirkkonummi plants (Microsoft) started operation in May 2026 with 180 MW of water-to-water heat pumps, 200 MW electric boilers and 800 MWh storage, with data-centre waste heat expected to cover ~40% of a 2 TWh/yr district-heat demand once recovery phases in from 2027; Google/Haminan Energia's heat-recovery plant delivered first heat in Q4 2025 and is stated to cover 70–75% (Google claim: 80%) of Hamina's district heat. Denmark's Energy Agency counts only ~4 of ~50 data centres actually reusing waste heat and forecasts 6.0 TWh data-centre consumption by 2030. Norway's Statnett reports 334 MW of data-centre capacity reserved north of Svartisen.

### Cited Findings
- Fortum press release, 6 May 2026: heat production started at Kolabacken (Kirkkonummi) and Hepokorpi (Espoo); 72 water-to-water heat pumps up to 180 MW district heat; 40 air-to-water heat pumps; 200 MW electric boilers (4 units); 20,000 m³ / 800 MWh thermal storage; ~€225 million investment with NextGenerationEU and Finnish state support; ~250,000 heat users; waste-heat recovery starts in phases in 2027; once fully implemented data-centre waste heat "expected to cover approximately 40 per cent" of the area's ~2 TWh/yr district-heat demand. — [Fortum](https://www.fortum.com/media/2026/05/fortum-has-started-heat-production-two-large-data-centre-sites-finland)
- City of Espoo, 17 March 2022 (claim at announcement): waste heat to cover ~40% of heat demand of 250,000 district-heat users in Espoo, Kauniainen and Kirkkonummi; CO2 of district heat to fall by ~400,000 t/yr; quoted: Mayor Jukka Mäkelä, PM Sanna Marin, Fortum CEO Markus Rauramo, Fingrid CEO Jukka Ruusunen, Microsoft's Cindy Rose. **[older, 2022]** — [Espoo.fi](https://www.espoo.fi/en/news/2022/03/microsoft-and-fortum-collaborate-espoo-microsofts-planned-data-centre-region-espoo-will-produce-zero)
- Eurelectric summary (industry body, not primary): ~75% of the data centres' waste heat used annually for district heating. — [Eurelectric](https://www.eurelectric.org/stories/microsoft-data-centers-provide-40-of-fortums-electricity-based-district-heating-in-espoo-finland/)
- Business Finland (state agency), 20 May 2024: Google €1 billion Hamina expansion; recovered heat estimated to cover ~80% of Hamina's district-heating needs; expected to begin contributing by late 2025; partner Haminan Energia and the municipality. — [Business Finland](https://businessfinland.fi/en/News/news/2024/google-announced-an-expansion-of-its-hamina-data-center)
- CapMan Infra (owner of Haminan Energia), 18 May 2026: heat-recovery pump plant inaugurated 12 May 2026; first heat supplied Q4 2025; once fully operational covers ~70–75% of Hamina's district-heating energy, roughly 2,000 residential apartments. — [CapMan](https://capman.com/stories/capman-infras-portfolio-company-haminan-energia-new-heat-recovery-facility/)
- Hamina site uses seawater cooling (Google statement via DCD, May 2024). — [DCD](https://datacenterdynamics.com/en/news/google-launches-heat-recovery-project-at-data-center-in-hamina-finland)
- Energistyrelsen, "Analyseforudsætninger til Energinet 2025 – Datacentre" (background note, Nov 2025): data-centre electricity consumption forecast 6.0 TWh in 2030, 26.8 TWh in 2040, 35.9 TWh in 2050. — [ENS (PDF)](https://ens.dk/media/7603/download)
- Dansk Fjernvarme consultation response to AF25 (14 Oct 2025): 2024 data-centre consumption ≈2.6 TWh (Datacenter Industrien analysis, 7% of Danish consumption); a Børsen article cited 3 TWh attributed to ENS; AF25's 2025 figure ≈1.2 TWh which Dansk Fjernvarme considers probably low. — [ENS consultation PDF](https://ens.dk/media/7620/download)
- Ingeniøren, 17 Aug 2026 (paywalled): Energistyrelsen count shows ~4 of ~50 Danish data centres using waste heat (~8%); industry body Datacenterindustrien says 7. — [ing.dk](https://ing.dk/artikel/naesten-al-overskudsvarme-fra-datacentre-gaar-tabt-vanskeligere-end-de-fleste-forestillede-sig)
- Norway: Statnett capacity-management presentation (11 Nov 2025) confirms continued data-centre demand growth qualitatively; Green Mountain connected 110 MW total with 37 MW reserved at Vang/Vardal/Nedre Vinstra (3 Nov 2025). — [NVE-hosted Statnett slides (PDF)](https://www.nve.no/media/19347/4-statnett-tilknytning.pdf)
- Norway north: data centres north of Svartisen hold 334 MW reserved (largest: Aker outside Narvik); Salten-and-north 1,150 MW reserved with ~1,100 MW queued; NO4 reservations 2,375 MW. (Commentary citing Statnett figures.) — [TU.no, 5 May 2026](https://www.tu.no/artikler/er-det-egentlig-krise-i-nord/571604)
- Sweden: Energimyndigheten hosts the national EED data-centre reporting page; the fetched URL returned 404 and redirected to [this page](https://www.energimyndigheten.se/en/climate/climate/data-centre-energy-performance-reporting/) (not fetched).

### Inferences
- Espoo and Hamina are "claim then delivered" cases where the delivered share (Hamina 70–75% per owner) is slightly below the announced claim (80%), and Espoo's 40% remains a forward expectation pending 2027 recovery phases.

### Gaps
- No Fortum/municipal figure for the actual MWh of data-centre heat delivered in 2026 (recovery only starts 2027).
- No Haminan Energia primary document with MW capacity.
- Danish ENS 2024/2025 actual TWh were not in the fetched text (figure only in a chart).
- No Swedish aggregate EED results retrieved.

---

## Germany: EnEfG heat-reuse and PUE obligations; Frankfurt grid

### Takeaway
Germany's Energy Efficiency Act (EnEfG) requires new data centres commissioned from 1 July 2026 to achieve PUE ≤1.2 and to reuse 10% of waste heat (15% from 1 July 2027, 20% from 1 July 2028); existing data centres must reach PUE ≤1.5 from 1 July 2027 and ≤1.3 from 1 July 2030; 50% renewable electricity from 2024 and 100% from 2027; and operators must report to the national Energieeffizienzregister für Rechenzentren. Frankfurt's grid peak load exceeded 900 MW on 25–26 June 2026 (Mainova), up from >850 MW a year earlier.

### Cited Findings
- EnEfG requirements (consultancy summary of the statute; statute text at gesetze-im-internet.de was not fetchable in this session): new data centres from 1 Jul 2026 PUE ≤1.2; existing PUE ≤1.5 from 1 Jul 2027 and ≤1.3 from 1 Jul 2030; new data centres waste-heat reuse ≥10% from 1 Jul 2026, ≥15% from 1 Jul 2027, ≥20% from 1 Jul 2028; renewable electricity ≥50% from 1 Jan 2024, 100% from 1 Jan 2027; reporting to Energieeffizienzregister für Rechenzentren (RZReg). — [TÜV Rheinland Consulting](https://consulting.tuv.com/aktuelles/datacenter/enefg-im-rechenzentrum); statute (not fetched): https://www.gesetze-im-internet.de/enefg/__11.html
- Mainova press release, 30 June 2026: Frankfurt daily peak load exceeded 900 MW on 25 and 26 June 2026; prior year clearly above 850 MW; preceding years just above 800 MW; grid capacity expected to more than double in coming years. Data centres are not named in the release. — [Mainova PDF](https://www.mainova.de/resource/blob/170090/b25e161948b42535e3c0587eb0ce0906/20260630-tageshoechstlast-data.pdf)
- EU EED first report: Germany has the most reporting data centres and the highest installed IT power in the EU (reported via DCD, see EU section).

### Inferences
- Germany is the only EU state with statutory numeric ERF (heat-reuse) targets; whether the first 2026 threshold is met will only be visible via RZReg/EU database reporting in 2027.

### Gaps
- Could not fetch the EnEfG statute text (provenance block); thresholds are from a consultancy summary and should be verified against §11 EnEfG.
- No public RZReg aggregate data located.
- Mainova does not attribute the peak load to data centres; no Frankfurt-specific data-centre share figure with a primary URL was found.

---

## UK: West London grid, NESO connection reform, Thames/Affinity Water

### Takeaway
NESO's March 2026 Demand Call-for-Input summary shows data centres at 50,802 MW (~55%) of ~93 GW of transmission-level demand responses, with only 32% having an off-taker. Affinity Water's parliamentary evidence counts ~125 proposed/under-construction data centres in its region with individual requests up to 35 l/s and one proposal for 21 Ml/d; Thames Water's annual report identifies 108 hyper/large data centres and its strategy director says planned data centres equal ~1.68 million additional homes. The 2022 GLA West London capacity constraint (Hillingdon, Ealing, Hounslow; connections not before 2035) remains the foundational record.

### Cited Findings
- NESO "Demand Call for Input (CFI) High Level Summary", March 2026 (CFI issued 6 Nov 2025): 243 responses >90 GW; data centres 50,802 MW (~55%), 152 of 279 project phases; 32% of data-centre projects have an off-taker, 68% do not; figures "indicative only". — [NESO document](https://www.neso.energy/document/378226/download)
- Affinity Water written evidence DCU0083 (UK Parliament committee): ~125 data centres proposed or under construction in its region; requests up to 35 l/s (peak demand of 3,500 homes); one proposal 21 Ml/d (~147,000 people); volume available for data centres in AMP8 (2025–30) 6.90 Ml/d Central, 7.68 Ml/d company-wide; recommends government guidance on potable water for data centres; data centres designated CNI in Sept 2024. — [UK Parliament](https://committees.parliament.uk/writtenevidence/166455/html/)
- Thames Water annual report (via press): 108 "hyper or large" data centres identified in pipeline; spokesman: "equivalent to the usage of thousands of homes at peak draw". — [Yahoo/Telegraph syndication](https://www.yahoo.com/news/articles/thames-water-faces-rocketing-demand-150415291.html)
- Thames Water strategy director Cathryn Ross: planned data centres equal serving 1.68 million additional homes. — [Utility Week](https://staging4.utilityweek.co.uk/thames-planned-data-centres-like-adding-1-7m-homes-in-our-region/?amp=true)
- **[older, 2022]** Thames Water launched a targeted exercise on data-centre water use in London/Slough; a proposed Slough data centre applied for 25 l/s and Thames reduced it by requiring on-site storage; "It isn't necessary for data centers to use drinking quality water for cooling" (John Hernon). — [DCD, 23 Aug 2022](https://datacenterdynamics.com/en/news/thames-water-launches-data-center-water-probe-in-london-slough-amid-drought)
- **[older, 2022]** GLA note: Hillingdon, Ealing, Hounslow; developments >25 units affected; applicants told no capacity until 2035; data-centre demand "now equals the total of all other users in the area"; NGET substations Iver, Willesden, Laleham, North Hyde; SSEN/NGET upgrades "will take many years". — [DCD, 4 Aug 2022](https://www.datacenterdynamics.com/en/news/gla-wants-to-change-applications-process-to-ease-west-london-power-crisis)

### Inferences
- The NESO 50.8 GW figure is self-reported developer intent, not contracted capacity; it is an order of magnitude above current UK data-centre load (NESO's Jan 2025 estimate cited by FactCheckNI: ~7 TWh in 2025).

### Gaps
- Could not retrieve the Thames Water annual report page/number directly; figure is via press.
- The Foxglove-hosted Portsmouth Water statement PDF (28 May 2025) could not be fetched.
- No DNO (SSEN) 2024–2026 West London capacity document with MW numbers retrieved.

---

## Spain: Aragón approvals, REE capacity map, water

### Takeaway
Red Eléctrica's demand capacity map (1 Oct 2026) shows 18.52 GW of granted transmission-level demand access, of which data centres hold 6,329 MW (34.2%), none yet in service. Aragón's PIGA approval for Amazon's four expansions was published in the BOA on 25 Aug 2025; regional press citing official filings puts the five largest projects (Amazon ×4 + Blackstone Calatorao) at >2,000 MW and ~16,000 GWh/yr vs ~10,000 GWh/yr consumed by all of Aragón, with Amazon's four centres at ~1 million m³/yr of water.

### Cited Findings
- REE press release, 1 Oct 2026: 18.52 GW granted demand access on the transmission network; 11.05 GW not yet in service; data centres 6,329 MW (34.2%), none in service; industry 5,838 MW (4,346 MW in service); rail 19.2%; hydrogen/renewable gas 13.2%; excludes distribution-level requests. — [REE](https://www.ree.es/es/sala-de-prensa/actualidad/nota-de-prensa/2026/10/red-electrica-publica-el-mapa-de-capacidades-de-demanda-tipo-consumo); map: https://www.ree.es/es/clientes/consumidor/acceso-conexion/conoce-la-capacidad-de-acceso
- Cumulative data-centre connection requests in Spain ≈22 GW (El Periódico de la Energía via DCD, 5 Oct 2026); SpainDC estimates 2.6–3 GW operational by 2030. — [DCD ES](https://www.datacenterdynamics.com/es/noticias/espa%C3%B1a-afronta-22-gw-de-solicitudes-de-centros-de-datos/)
- aelēc (utility association) 2025: ~40 GW of all access/connection requests, 12% (4.5 GW) granted, 66% (25 GW) unservable, 22% in process. — [Energías Renovables, 22 Dec 2025](https://www.renewableenergymagazine.com/panorama/solo-el-12-de-las-solicitudes-de-20251223)
- Aragón (eldiario.es, 27–28 Aug 2025, citing BOA and regional energy directorate): PIGA approval for Amazon published in BOA 25 Aug 2025; five projects >2,000 MW and ~16,000 GWh/yr average vs ~10,000 GWh Aragón annual consumption; access requests in Aragón rose from 3,000 MW to 7,400 MW over five months (late 2024–2025); ten bottlenecked nodes total 2,380 MW; Amazon's four centres ≈1 million m³/yr water (≈ population of 9,000); Amazon investment €15,700 million; Blackstone Calatorao initial approval; ACS La Puebla de Alfindén DIGA challenged by Ecologistas en Acción/Ansar. — [eldiario.es](https://www.eldiario.es/aragon/politica/explosion-centros-datos-aragon-opacidad-choque-institucional-riesgo-colapso_1_12559021.html)
- Amazon received environmental clearance for its largest Aragón data centre in July 2026 (press). — [Merca2, 16 Jul 2026](https://www.merca2.es/2026/07/16/centro-datos-amazon-aragon-permiso-ambiental-2418205/)

### Inferences
- The REE 6,329 MW figure is granted-but-not-in-service capacity, so Spain's documented operating data-centre load is far lower; the 22 GW figure is requests.

### Gaps
- The BOA PIGA resolution itself was not fetched; numbers come from regional press citing it. The BOA URL should be added.
- No CHE (Ebro basin authority) water concession document for the Amazon sites was located.
- No Microsoft Aragón primary approval document fetched.

---

## France: RTE statements

### Takeaway
RTE's Île-de-France 2025 electricity review (9 July 2026) records 6 data centres connected to the transmission grid (640 MW), ~8 GW across ~50 sites in the connection process and ~7 GW across ~30 sites under study, against a regional consumption of 66.3 TWh (14.7% of national).

### Cited Findings
- RTE Bilan électrique Île-de-France 2025 (9 Jul 2026): 6 data centres connected to RTE's network at end-2025, 640 MW; ~8 GW/~50 sites in connection process; ~7 GW/~30 sites under study; regional consumption 66.3 TWh (+1.1%), 14.7% of national; RTE investment up to €6 billion in IdF over 15 years (not data-centre-specific); figures are a snapshot that "evolves daily". — [RTE PDF](https://assets.rte-france.com/prod/public/2026-07/2026-07-09-bilan-electrique-idf-2026.pdf)

### Gaps
- No national RTE data-centre TWh consumption figure for 2025 retrieved; the national Bilan électrique should be checked.

---

## Italy

### Cited Findings
- Terna connection requests for new data centres: 42 GW (March 2025) rising to nearly 50 GW by June 2025, per Reuters as cited by QualEnergia; QualEnergia's own estimate (not Terna) of realistic IT load is 1.4–2.0 GW by 2030. — [QualEnergia, 2 Sep 2025](https://www.qualenergia.it/articoli/data-center-italia-da-50-gw-rumore-a-5-gw-realta/)

### Gaps
- No Terna primary document with the GW request figure located; treat as secondary. Poland and Switzerland: no primary-source entries located in the time available; flagged as gaps.

---

## EU-level: Energy Efficiency Directive datacenter reporting

### Takeaway
The Commission published its first technical assessment of EED data-centre reporting in July 2025 (2024 reporting period): 776 data centres across 18 member states reported 6.4 GW installed IT power demand, 16.7 TWh consumption and a weighted average PUE of 1.36; participation was ~36% of expected operators. A public dashboard exists. The Commission proposed a common rating scheme on 21 Sept 2026 and minimum performance standards are planned for Q2 2027.

### Cited Findings
- EC EED data-centre page: Delegated Regulation (EU) 2024/1364 sets KPIs; European database at policy-reporting-platform.ec.europa.eu; public dashboard; first Commission report July 2025 (2024 data); report on 2025 period "under preparation"; rating scheme proposed 21 Sept 2026 (feedback 26 Mar–23 Apr 2026); minimum performance standards consultation to 14 Dec, proposal Q2 2027. — [EC](https://energy.ec.europa.eu/topics/energy-efficiency/energy-efficiency-targets-directive-and-rules/energy-efficiency-directive/energy-performance-data-centres_en)
- Report: "Assessment of the energy performance and sustainability of data centres in EU – First technical report". — [Publications Office](https://op.europa.eu/en/publication-detail/-/publication/83be4c3e-5c79-11f0-a9d0-01aa75ed71a1/language-en)
- Aggregate figures (DCD summarising the EC report/dashboard, 17 Apr 2026): 776 data centres; 6.4 GW installed IT power; 16.7 TWh; weighted PUE 1.36; 224 large (28%), 52 very large (7.3%); 18 member states; Germany largest; water totals and ERF/REF averages not given in text. Dashboard URL in article. — [DCD](https://www.datacenterdynamics.com/en/news/european-commission-releases-aggregate-eed-data-center-data-operators-report-64gw-of-installed-capacity-across-the-eu/)
- Green Web Foundation reading of the report (31 Jul 2025): ~36% of obligated operators reported; Czechia zero; Ireland ~1 in 6; REF ≥85% for small, >96% second-largest band, ~92% hyperscale; renewable claims ~70% GOs, ~29% PPAs, <0.5% on-site; WUE rises with facility size. — [Green Web Foundation](https://www.thegreenwebfoundation.org/news/what-weve-learned-about-the-sustainability-of-datacentres-in-europe-from-the-eed/)

### Inferences
- The EU database is the first pan-European primary data source, but with ~36% compliance and 18 of 27 states, it under-counts; Ireland's CSO figure (7.66 TWh) alone is ~46% of the EU-reported 16.7 TWh, illustrating the coverage gap.

### Gaps
- Direct dashboard fetch not attempted; aggregate numbers are via DCD and GWF citing the EC report. Water (WUE) and ERF totals were not extracted.
