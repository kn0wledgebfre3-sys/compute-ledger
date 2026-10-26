# Ireland (Dublin region) datacenter site list for the Climate TRACE handover: method, provenance and regional check

Built 2026-10-20/21 with web search and page fetches only (no direct downloads). Outputs:

- `sites/ireland_sites.json` and `sites/ireland_sites.csv`: **40 rows, 22 with an open-source coordinate**, in the `seed_sites` schema (`site_id, name, operator, parent_company, country, admin_region, city, lat, lon, status, capacity_mw_it, capacity_source, generator_mw_permitted, cooling, first_year, source_url, source_type, licence, ledger_entry_id, confidence, last_checked`) plus the two trailing columns the seed file already carries (`coord_source_url`, `notes`) and two new trailing columns (`generator_mw_basis`, `generator_count`, placed after `notes` so the seed columns are an exact prefix) that say exactly what the MW figure is. `last_checked` is `2026-10-20` on every row.
- Build script with every value embedded (reproducible, converts grid references to WGS84): `sites/build/build_ireland.py` (writes to `sites/`; set `SITES_OUT` to write elsewhere). JSON validated with `python3 -I`.

The target was 40-80 sites; 40 were reached before the fetch tool's usage limit was hit (reset 01:40 UTC 2026-10-21), and the files were written from what had been gathered. Section 6 lists the exact documents that would add coordinates or rows on a re-run.

## 1. Sources, in the order the brief set, and what each yielded

### 1a. EPA Industrial Emissions (IE) licences (epawebapp.epa.ie) - 12 rows, the best MW data
The EPA licence search is a JavaScript app (LEAP) and cannot be enumerated here; licence documents were reached only through web search hits on `epawebapp.epa.ie/licences/lic_eDMS/<id>.pdf`. The search index is dominated by Amazon Data Services Ireland Ltd (ADSIL), whose nine Dublin-region licences/applications were all found:

| Licence | Site | Generators (MWth) | Licence cap (MWth operating at once) | Coordinate source |
|---|---|---|---|---|
| P1170-01 (granted 6 Jul 2023) | Grange Castle South, Buildings A-C | 70 x 6.49 + 3 x 2.19 = 460.87 | 421.93 | application form LA007494 site centre, Irish Grid 303185/230885 |
| P1184-01 (20 Jun 2023) | Grange Castle South, CyrusOne-leased plot | 16 x 6.49 = 103.84 | ~90.86 (OCR garbled) | attachment 7.4.2 stack A3-01, ITM 702828/730760 |
| P1173-01 (13 Jun 2023) | Airton Road, Tallaght (GHG "DUB 56") | 27 x 6.46 + 26 x 6.49 = 343.16 | 317.26 | attachment 7.4.2 stack A3-1, ITM 708808/728572 |
| P1177-01 (14 Jun 2023) | Greenhills Road, Tallaght | 37 x 5.19 + 9 x 6.60 = 251.43 | 251.43 | attachment 7.4.2 stack A3-1, ITM 709922/728392 |
| P1172-01 (19 Jul 2023) | Blanchardstown Industrial Park, Snugborough Rd | 70 units, 416.52 incl. pumps | 374.17 | attachment 7.4.2 stack A3-01, ITM 708769.7/740534.3 |
| P1182-01 (21 Jun 2023) | Cruiserath Road, Dublin 15 (GHG "DUB 58") | 66 x 6.49 + 2 x 2.19 = 432.72 | 393.78 | GHG permit IE-GHG197 main entrance, Irish Grid 307625/242020 |
| P1186-01 (15 Jun 2023) / P1186-02 review | Clonshaugh, Buildings W/X/Y (+U, V) | 40 x 5.44 (+10 x 6.49 + 2.19 + 3.6) = 288.29 | 190.40 (original) | attachment 7.4.2 stack A3-1, ITM 718406/740436 |
| P1171-01 (application, 2022-23) | Clonshaugh (planning 3634/15), 105 stacks | not rated in the attachment | - | attachment 7.4.2 stack A3-1, ITM 718047/741136 |
| P1181-01 (8 Aug 2024) / review LA015550 | Drogheda IDA park (GHG "DUB 62") | 26 x 6.82 + 1.55 + 26 x 6.79 + 2.02 = 358.17 | 165.87 (Building A) | application form LA009977 site centre, Irish Grid 306705/274070 |
| P1222-01 (application Feb 2025) | Leixlip, Kildare Innovation Campus B1 | GHG permit: 14 x 7.73 + 2.5 = 111.44 | - | application form LA016198 site centre, Irish Grid 298631/235069 |

Non-Amazon IE licences found: Equinix DB5 **P1168-01** (9 dual-fuel gas turbines x 18.64 MWth, a primary power plant, inspector's report 30 Aug 2022); Microsoft DUB14/15 **P1187-01** (22-unit standby gas plant + 21 diesel; found via its 2024 Annual Environmental Report on leap.epa.ie, which reports **402,946.82 GJ = 111.93 GWh** total energy used in 2024); Microsoft applications LA010453 (DB3-5, 212.58 MWth) and LA010454 (DUB6-13, 579.28 MWth) whose P-numbers were not retrieved; Vantage **P1203-01** (EPA memo 14 Apr 2025 that it could not consider the application; re-filed Aug 2025); South Dublin Routing 4 No. 2 Ltd LA011399 (Orion Business Campus, 9 x 21.64 MWth gas/HVO engines). The Journal reported (Nov 2024) that the EPA had approved 15 IE licences for data centres (13 in Dublin) with 9 pending; this list reaches 13 of the 15 by P-number or application number.

**Key finding on geocoding:** the licence PDFs, inspector's reports and non-technical summaries carry no grid reference, but (a) the EDEN **application form** gives a "site centre point" Easting/Northing (Irish Grid), and (b) **attachment 7.4.2 "Emissions to Atmosphere - Minor and Potential Emissions"** lists every generator stack with Easting/Northing. The attachments label the columns "Six Digit GPS Irish National Grid Reference" but the values are ITM (E ~7xx,xxx); one application (LA011866) supplies the same stack in both systems (ITM 718406/740436 = Irish Grid 318465/240412), which was used as the conversion check (agreement within 50 m).

### 1b. EPA greenhouse-gas (EU ETS) permits - 15 rows, the best site register
Not in the brief, but the single most useful register found: the EPA "Access to current permits - ETS1 Stationary Installations" page lists every GHG permit, including **27 held by data-centre operators** (Amazon x10, EdgeConneX x2, Echelon, Equinix x4, Google, Microsoft, Digital Netherlands VIII/Digital Realty, K2 x3, KDCR/Keppel x2, Runways Information Services/Meta, Vantage) plus Waspar Ltd "DUB10" and Vodafone CDC, which the permits describe as data centres. The permits give the installation address and the generator inventory, and the older epa.ie-hosted versions give a **"site main entrance" grid reference** (Irish Grid), which located Google, Microsoft (two blocks), Meta Clonee, Digital Realty DUB14, K2 Ballycoolin, KDCR DUB2, Waspar DUB10, Vodafone CDC, Amazon DUB 58 and DUB 56. The newer epawebapp-hosted permits (2024-26) drop the grid reference.

Ten permit PDFs are linked from the register over **http only** and the fetch tool refused the https->http redirect: Amazon Dub 8 (IE-GHG171), Dub 9 (172), DUB10 (173), DUB54 (183), DUB56 (184, older version retrieved instead), DUB58 (197, older version retrieved), GCC1 (201), EdgeConneX EDCDUB (186), Equinix DB5 (600), K2 Dublin 1 (188). Five Amazon installations (Dub 8, Dub 9, DUB10, DUB54, GCC1) therefore have no address in this file and are not rows.

### 1c. An Bord Pleanala / An Coimisiun Pleanala - 12 rows or row-level corroboration
Case pages (`pleanala.ie/en-ie/case/<n>`) and inspector's reports (`.../media/abp/cases/reports/<nnn>/r<n>.pdf`) fetch cleanly, but the case search is client-side, so cases were found by web search only. Cases used: ABP-317446-23 (Vantage DUB13, refused; in ledger), 313787 (Vantage DUB11/12, withdrawn), 317936-23 (Equinix DB8 gas compound), 302813-18 (CyrusOne), 300752-18 / 305948-19 / 317802-23 (EdgeConneX), 300305 (Microsoft DUB08 18 MW gas generators, invalid), 303517 (Crag Digital, now Echelon DUB10), 318180-23 (Amazon/Universal Developers Cruiserath F/G, granted Dec 2025), 312424 (Parslickstown), 318790 (Servecentric), 501133 (SDR4 contribution appeal), 305962 (OGCIO Backweston), 314474-22 (Art Data Centres Ennis). Inspector's reports give generator counts, floor areas and sometimes MW (DB8: 27.48 MW output / 9 MW grid request; Ennis: 200 MW = 83 grid + 120 on-site) but **never coordinates**; the case map is an ArcGIS instant app that cannot be queried here.

### 1d. EirGrid / ESB Networks connection lists
No public site-level list exists. Dail written answer of 8 May 2024 (oireachtas.ie): "There is currently no official state register of data centres operating in Ireland"; EirGrid counts 14 transmission-connected data centres in Dublin (11 connected, 3 contracted), 1 in Louth, 1 in Meath, and cannot give distribution-connected sites. EirGrid's Data Centre Constrained Area Overview and Generation Capacity Statement (already in `open_data_sources.md`) give aggregate MVA only.

### 1e. CRU connection policy
Ledger entry `ie-cru-leu-connection-policy-2025` (CRU/2025236) (known from a law firm's summary) requires, without prescribing the fuel,: new sites >= 10 MVA must bring dispatchable on-site/proximate generation at least equal to their MIC. The on-site gas fleets in this file (Microsoft DUB14/15 standby gas plant, Equinix DB5 turbines, EdgeConneX 20 gas plants, Vantage 11 dual-fuel engines, Echelon Crag Avenue 10 gas turbines, SDR4 9 engines, Ennis 18 engines) were licensed or permitted before that decision; no record ties them to it.

### 1f. Bitpower / Host in Ireland
Used only once, second-hand: South Dublin County Council's written reply of 8 Nov 2021 (meetings.southdublin.ie/Home/ViewReply/72725) reproduces a Bitpower table of 34 operational / 3 under construction / 12 approved / 4 in planning data centres in Grange Castle-Profile Park-Dublin 22 and Citywest-Park West-Dublin 24 (May 2021). That table is a count check, not a site list.

### 1g. Wikipedia / Wikidata
Wikidata is unreachable from this environment (entity pages, EntityData JSON, SPARQL, Special:Search all refused). Wikipedia article HTML fetches but the converter strips infobox coordinates; only the `Google data centers` table coordinate (53.3201083, -6.4420639, CC-BY-SA-4.0) was available and is recorded in the Google row's notes; the row itself is now located from the GHG permit (c. 0.7 km apart, same campus).

### 1h. Geocoding fallbacks tested
Overpass, Nominatim, Photon, geocode.maps.co, openstreetmap.org and logainm.ie are all `ROBOTS_DISALLOWED`. **townlands.ie** (OpenStreetMap-derived townland boundaries, ODbL) does fetch and gives a townland centre for every Irish townland (e.g. Ballybane, Co. Dublin: 53 19 11 N, 6 26 47 W, relation 4546397); it was used once (Vantage DUB11/12, flagged as a +/-1 km townland centre). It would locate every remaining Dublin row whose record names a townland (Ballymakaily, Kilbride, Ballybane, Tooreen) on a re-run.

## 2. Coordinate conversion
Irish Grid (EPSG:29903, Airy Modified ellipsoid, Ireland 1965 datum) and ITM (EPSG:2157, GRS80/ETRS89) values were converted in the build script with the OSi Redfearn inverse-TM series and, for Irish Grid, the OSi 7-parameter Helmert shift (tx 482.530, ty -130.596, tz 564.557, rx -1.042", ry -0.214", rz -0.631", s 8.150 ppm). Checks: the same Clonshaugh stack quoted in both systems agrees within 50 m; the Google main-entrance point falls 0.7 km from the Wikipedia campus point. Precision of located rows: generator-stack or site-centre points, c. 10-100 m (confidence high/medium); townland centre (Vantage DUB11/12) c. 1 km; ledger 2-decimal point (Vantage DUB13) c. 0.5 km.

## 3. Schema notes and conventions
- `generator_mw_permitted` holds the figure the record gives, which in Ireland is almost always **rated thermal input (MWth)**, not electrical MW. `generator_mw_basis` states the basis for every row (sum of units vs licence cap; MWth vs MW; standby vs primary gas plant). Where the row is a gas-fired primary plant (Equinix DB5, Echelon Crag Avenue, EdgeConneX gas plants, Vantage MFGP, SDR4, Ennis) this is said explicitly, because such plants are generation, not backup, for the emissions model.
- `capacity_mw_it` is null on every row: no Irish public record retrieved states an IT load. Facility power figures that do appear (Equinix DB8 27.48 MW; Ennis 200 MW; Amazon Cruiserath appellants' 73 MW) are in `notes`.
- `cooling`: `evaporative` where the licence names evaporative cooling in the air-handling units (Amazon; these sites free-cool most of the year and use mains water above c. 30 C, about 5 days/yr per the inspectors' reports); `air` where the record says dry free cooling ~95% of the year (Microsoft) or free-cooling chillers (Vantage); `closed_loop` for chilled-water glycol loops (Amazon P1184, SDR4); `evaporative` for Equinix DB5's 13 cooling towers.
- `status` values follow the seed file; `refused` was added for two rows (Vantage DUB13, EdgeConneX DUB06) rather than folding refusals into a campus row. Several `operating` statuses are inferred from the licence/permit stage (noted and set to medium/low confidence).
- `source_type`/`licence`: `permit`/`public_record` for EPA documents, `register`/`public_record` for ABP case pages and reports, and `press`/`press` for the two rows (Echelon Peamount Road; Red Admiral Rochfortbridge) whose only retrieved record is a newspaper report. Those two should be replaced with the EPA licence and the Westmeath CC file.
- Duplicates and campus logic: Amazon Cruiserath Buildings E/F/G (ABP-318180-23) is a separate `permitted` row with the same campus coordinate as the operating P1182 row and a do-not-double-count note; Vantage DUB13 and EdgeConneX DUB06 are refused halls on campuses that have their own rows; CyrusOne's Dublin site is the Amazon P1184 row (the licence says the plot is leased from CyrusOne); Crag Digital's permission is the Echelon DUB10 Energy Centre row; Amazon "DUB 56" (GHG) is the Airton Road licence site (points 340 m apart) and "DUB 58" is Cruiserath; the Google Wikipedia row in `seed_sites.json` is superseded by `irl-google-grange-castle-ghg170`.

## 4. Regional check against the CSO metered figure

**Benchmark (ledger entry `ie-national-cso-share-2025`):** CSO "Data Centres Metered Electricity Consumption 2025" (7 Jul 2026): data centres used **23% of Ireland's metered electricity in 2025 = 7,663 GWh** (6,973 GWh in 2024). EirGrid told the Dáil (8 May 2024) that 14 of 16 transmission-connected data centres are in Dublin; no CRU figure for a regional share was located, and the earlier '97%' is withdrawn. This is a metered, operator-independent total: any site-level estimate must sum to no more than it.

**What this file gives for the estimate:** 17 operating rows carry a generator figure, summing to **4,652 MWth** (Amazon 2,655; Microsoft 1,135; EdgeConneX 534; Equinix DB5 168; Equinix DB1/DB4 61; K2 100). Of that, 373 MWth (Equinix DB5 turbines, EdgeConneX gas plants) is primary gas generation, leaving **4,279 MWth of standby plant** (including Microsoft's 167 MWth standby gas plant). Nine operating rows have no MW (Google "<200 MW", Meta 55 generators, Digital Realty "<50 MW", KDCR x2, Waspar, Vodafone, Equinix DB3, Amazon P1171's 105 stacks), so the located fleet is an undercount of the operating stock.

**Chain from permitted MWth to annual GWh, as a bound not a point** (revised after an independent review on 2026-10-21; the earlier single-factor version is superseded):
1. Thermal to electrical: 0.385 MWe per MWth, checked against a Cat 3516C 2,500 ekW standby unit (656.8 L/h at 100% load, 838.9 g/L, LHV 42.78 MJ/kg = 6.55 MWth; 2.5/6.55 = 0.382; spec sheet: https://www.hanovercounty.gov/DocumentCenter/View/5983/CAT-3516C-2500KW-Cut). The EPA "rated thermal input" is on net calorific value, so the basis matches. Varying 0.36-0.42 moves the bound little.
2. Standby to design load depends on the redundancy architecture, which the licences do not state and which differs by operator: fleet-level N+1 on 40-105-unit fleets is about 1.01; N+1 per block with headroom about 1.2-1.5; 2N (common for colocation and some hyperscale blocks) is 2.0. This factor, not the efficiency, is where the uncertainty lives.
3. Two standby bases: sum of units from inspector's reports (4,279 MWth, which includes two review applications not yet granted) and the granted licence caps (3,830 MWth). The cap is the better base case.
4. Result, against the 7,663 GWh national total (and assuming these 16-17 sites carry 50-70% of national load):

| Standby basis (MWth) | Redundancy | Design MW | 100% GWh | u_max | u if sites = 50-70% of national |
|---|---|---|---|---|---|
| 4,279 | 1.01 (fleet N+1) | 1,625 | 14,235 | 0.54 | 0.27-0.38 |
| 4,279 | 1.2 | 1,373 | 12,026 | 0.64 | 0.32-0.45 |
| 4,279 | 1.5 | 1,098 | 9,618 | 0.80 | 0.40-0.56 |
| 4,279 | 2.0 (2N) | 824 | 7,216 | 1.06 | 0.53-0.74 |
| 3,830 (licence caps) | 1.2 | 1,229 | 10,766 | 0.71 | 0.36-0.50 |
| 3,830 | 2.0 | 737 | 6,456 | 1.19 | 0.59-0.83 |

What the check supports: under N+1 designs, utilisation of permitted standby capacity is bounded at roughly 0.54-0.71 and plausibly sits at 0.3-0.5; under 2N the metered total imposes no bound. The earlier statement that "0.6 fails and 0.3 passes" held only for the single 1.2 factor and is withdrawn. What survives is narrower and still useful: a permit-based estimate must carry the redundancy design as an explicit input, and the national metered total is the test it must pass in aggregate.
5. The one metered site, Microsoft DUB14/15 (2024 AER, 402,946.82 GJ = 111.93 GWh, all energy): against its 175.6 MWth diesel standby alone, u = 0.23; counting the 167.2 MWth standby gas plant as a second layer (2N-like), u = 0.12-0.19. The campus was ramping in 2024, so this is a lower bound on steady state, not a confirmation of any range.

**Recommended procedure for the handover (revised):** (i) take the national metered total (7,663 GWh for 2025; no regional split is documented in a primary source); (ii) allocate it across sites in proportion to standby MWe (0.385 x licence-cap MWth) under an explicit redundancy assumption carried as a column (N+1 fleet-level 1.01, N+1 with headroom 1.2-1.5, 2N 2.0), after excluding primary gas plants and adding the unrated sites once their MWth are read; (iii) treat the result as a bound, not an estimate, and the AER energy figures on leap.epa.ie as the per-site truth where they exist; (iv) for pipeline rows add energy only from their energisation year, and model gas plants as generation with their own fuel.

## 5. What could not be reached (stated plainly)
- **Coordinates for 18 rows** (null, with the reason in `notes`): Microsoft DUB14/15 (no grid reference in licence NTS or AER), Equinix DB5/DB3/DB4/DB1, K2 Dublin 21, KDCR DUB1 (newer GHG permits carry addresses only), Echelon Crag Avenue and Peamount Road, EdgeConneX campus and DUB06, Equinix DB8, SDR4 Orion, Servecentric, OGCIO Backweston, Ennis, Rochfortbridge, Parslickstown. Townland centres (townlands.ie) could place the EdgeConneX, DUB06 and Ennis rows at +/-1 km; the Citywest/Northwest Business Park rows need the older epa.ie permit versions (IE-GHG188-10512, 191, 192, 195 earlier revisions) or the EPA Maps layer.
- **The EPA IE facilities point layer** (data.gov.ie "Industrial Emissions (IE) Facilities", CC-BY 4.0, updated 9 Nov 2025) exists and would geocode every P-number at once, but its only access URL is the EPA Geoportal download form (`gis.epa.ie/Geoportal/GetData/Download`), which cannot be driven from here. No ArcGIS REST endpoint for it was surfaced.
- **Ten http-only GHG permit PDFs** (list in 1b), including the five unlocated Amazon installations (Dub 8, Dub 9, DUB10, DUB54, GCC1 - some may be alternative names of licensed sites already listed).
- **Microsoft P-numbers** for LA010453/LA010454; Echelon/Data and Power Hub Services licence number (July 2025); Westmeath CC reference for Red Admiral; the Board's decisions on ABP-317936-23, 317802-23; EngineNode Meath, Apple Athenry (withdrawn), Echelon Arklow, Pure DC and Interxion/Digital Realty's other Dublin buildings (no record surfaced before the limit).
- **Wikidata** (all endpoints), Overpass/Nominatim/Photon/OSM site, logainm.ie: blocked by robots or proxy.
- **Fetch-tool usage limit** reached at about 23:00 UTC on 2026-10-20 (reset 01:40 UTC); the files were then written from the material already gathered.

## 6. Re-run checklist (ordered by yield per fetch)
1. `https://www.epa.ie/publications/licensing--permitting/climate-change/4/` and `/3/`, `/2/`, `/5/`, `/6/`: the paginated permit list on epa.ie, whose older permit versions carry the main-entrance grid reference for K2 Dublin 1, Equinix DB1/DB3/DB5, EdgeConneX, Amazon Dub 8/9/10/54/GCC1.
2. townlands.ie pages for Ballymakaily and Kilbride (Co. Dublin), Tooreen and Cahernalough (Co. Clare), Castlelost (Westmeath).
3. EPA Geoportal IE-facilities download (needs a browser) or the LEAP API behind `leap.epa.ie`.
4. Annual Environmental Reports on leap.epa.ie for every P-number above: each gives total energy used (GJ), the only metered per-site figure available, and the direct test of step 4 of the regional check.
5. ETS verified emissions table (EU Transaction Log / EPA) for the 27 data-centre permits: tCO2 from backup generators per installation per year.


## Addendum, 2026-10-23: the AER figures now exist for eleven sites

The procedure above allocated the national metered total across sites as a bound. The EPA's Annual Environmental Reports have since been read for the eleven licensed installations (nine Amazon, Microsoft DUB14/15, Equinix DB5): for 2025 they report 4,109 GWh of metered electricity, 53.6% of the CSO total, and for 2024 3,585 GWh, 51.4%. Those per-site figures replace the allocation for the eleven; the remaining 46 to 49% of the national total belongs to the 29 sites that hold GHG permits or planning permissions only. See `METERED.md` and `ireland_aer_metered.csv`.
