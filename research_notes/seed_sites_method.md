# Datacenter seed-site list for Climate TRACE: method and provenance

Session date: 2026-10-20. Tools: WebSearch and WebFetch only (shell network blocked). Outputs:

- `sites/seed_sites.csv` and `sites/seed_sites.json`: **56 located sites** (every row has a coordinate and a source URL).
- `sites/seed_sites_unlocated.csv`: **333 register-named sites/records without an open coordinate** (Virginia DEQ air-permit registrations, Texas Comptroller registrations, Irish EPA licences, TCEQ/NDEP/SC/NC permit records, Singapore IMDA/EDB awards). This is the geocoding backlog.
- Build script (all values embedded, reproducible): `sites/build/build_seed.py` (writes to `sites/`; set `SITES_OUT` to write elsewhere).

The target was 200-400 sites. **56 is what could be located to the standard "every row needs a source URL and a coordinate, no invented coordinates"** under this session's network constraints (below). The 333-row backlog is the larger asset: it is register-grade and only lacks coordinates.

## 1. What blocked the bulk open-geodata routes

The fetch proxy only releases URLs that (a) appear verbatim in WebSearch results or in the user's files, or (b) the user approves interactively. No one answered the permission prompts, so every composed URL (any API query, any link found inside a fetched page) was refused with `PROVENANCE_REQUIRED`. Consequences:

| Source (task priority) | Result | Blocked URL(s) to approve for a re-run |
|---|---|---|
| OpenStreetMap Overpass API | **Unreachable.** Both the exact task URL and an area-scoped variant refused. | `https://overpass-api.de/api/interpreter?data=[out:json];node["telecom"="data_center"];out;` and the `area["ISO3166-1"="IE"]` variant |
| OSM taginfo | `ROBOTS_DISALLOWED` | `https://taginfo.openstreetmap.org/tags/telecom=data_center` |
| OSM wiki tag page | Fetched (URL is in `sources.json`); confirms `telecom=data_center` + `building=data_center`; no feature list, taginfo counts not rendered. | - |
| Wikidata SPARQL | **Unreachable.** First attempt rejected by proxy as "url exceeds the maximum fetchable length"; shortened query then refused for provenance. Wikidata item pages and `Special:WhatLinksHere/Q1193326` also refused; the search engine never surfaces wikidata.org pages. | `https://query.wikidata.org/sparql?format=json&query=SELECT ?item ?itemLabel ?coord WHERE{?item wdt:P31 wd:Q1193326;wdt:P625 ?coord. SERVICE wikibase:label{bd:serviceParam wikibase:language "en"}}` ; `https://www.wikidata.org/wiki/Special:WhatLinksHere/Q1193326` |
| Prince William County GIS "Data Center Buildings" layer (point layer with BuildingName, Address, BuildingStatus, YearBuilt, GFA, PermitCase; WKID 2283) | Layer metadata fetched; **query endpoint refused**. This single endpoint would locate every PWC data-center building. | `https://gisweb.pwcva.gov/arcgis/rest/services/Planning/Build_Out_Analysis/MapServer/9/query?where=1%3D1&outFields=*&outSR=4326&returnGeometry=true&f=json` |
| Loudoun County GeoHub | Refused (`https://geohub-loudoungis.opendata.arcgis.com/`); no data-center dataset surfaced via catalog.data.gov searches. | as listed |
| EPA Envirofacts FRS (would geocode every Virginia DEQ registration) | One surfaced URL fetched (`frs_facility_site` for "IAD-62": registry_id 110069993200, Sterling VA, **no lat/lon in that table**). The geo table could not be composed. | `https://data.epa.gov/efservice/frs_facility_site/...` (geo table / state filter) |
| Epoch AI "AI data centers" dataset (CC-BY 4.0, ~95 frontier sites with coordinates) | Documentation, directory and per-site pages fetched; **CSV refused**; per-site and satellite-explorer pages do not expose coordinates. Used only as corroboration in notes. | `https://epoch.ai/data/data_centers/data_centers.csv` |
| Ireland EPA licensed-facilities point layer (data.gov.ie, CC BY 4.0, TM65) | Dataset page fetched; layer last updated 2020 (period to 2016, predating most data-centre licences); WFS URL not fetchable. | `https://gis.epa.ie/geoserver/EPA/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=EPA:LEMA_Facilities_IEL&outputFormat=application%2Fjson&srsName=EPSG:4326` |
| Chile e-SEIA, Utah DEQ documents, Washoe County (NNPH), Clark County NV | `ROBOTS_DISALLOWED` | - |
| PeeringDB (facility pages carry lat/lon) | Fetched one page (fac/1, Equinix Ashburn) but **AUP says "All Rights Reserved", no bulk redistribution** - excluded as not open-licensed. | - |
| Wikipedia individual articles | WebFetch's HTML-to-text conversion strips the infobox/title-bar coordinates (verified on *Utah Data Center* and *One Wilshire*). Only coordinates embedded in wikitables survive. | - |

Commercial aggregators that dominate search results (DatacenterMap, Baxtel, Inflect, Cloudscene, Cleanview, mlq.ai, ocolo) were never used.

## 2. What yielded located rows (56)

### 2a. Wikipedia "Google data centers" table + Google operator list (32 rows, `source_type=wikipedia`, licence CC-BY-SA-4.0)
- `https://en.wikipedia.org/wiki/Google_data_centers` has a 74-row location table with DMS coordinates for 36 sites. DMS were converted to decimal degrees (6 dp) in the build script.
- Existence and status were corroborated against Google's own list `https://datacenters.google/locations/` (operator source, used only for corroboration/status, as the brief allows). Entries Google does not list as its own sites (Madrid, Turin, Zurich - leased colocation) were dropped; Cerrillos (withdrawn RCA, new air-cooled design pending) kept as `announced` with the ledger link.
- Status mapping: Google list without "in development" tag => `operating`; Wikipedia timeline "launched" year => `first_year`. Canelones kept `under_construction` (Wikipedia: inauguration expected 2026).
- Confidence `medium`: coordinates are community-placed, not register-verified. Wikipedia coordinates are normally the same P625 values held in Wikidata (the CC0 source the brief prefers) but that could not be verified because Wikidata was unreachable; licence is therefore recorded as CC-BY-SA-4.0, not CC0.
- Extra permit facts attached in `notes`: Google Lenoir = NC DAQ Title V 09733T10 to Tapaha Dynamics LLC (163 generators; new units 111.25 MW).

### 2b. Texas TCEQ Title V application packages (4 rows, `source_type=permit`, public_record)
TCEQ "reports/applications/<project>-ac.pdf" packages include the Core Data Form with decimal latitude/longitude, NAICS 518210, and OP-SUM generator tables. Found by web search only (the TCEQ directory is not browsable here); the search index surfaced about a dozen packages of which four were data centers:
- Microsoft SN Campus SN1/2/4/7, San Antonio (29.480036, -98.692555; 73 gensets, 176.5 MW summed) - confidence high.
- Compass Red Oak Datacenter DFW III (32.537981, -96.804371; 390 gensets; Microsoft tenant per Texas Comptroller register) - high.
- Alamo Mission LLC, Red Oak (32.531786, -96.792527; permit O4709) - medium; registrant's parent undisclosed.
- Childress Data Center, IREN (34.383232, -100.056272 from the TCEQ letter's map-marker link, not the Core Data Form) - medium.
Other surfaced TCEQ packages were not data centers (Kuraray, BASF, Conduit Edge) or were PDF portfolios whose attachments WebFetch cannot open (six-digit NSR project numbers). CyrusOne SAT2-4 had blank coordinate fields and went to the backlog.

### 2c. Sites carried from the Global AI compute ledger (20 rows, confidence low)
Rows whose coordinates are the ledger entry's 2-decimal `lat`/`lon` from `registry/{north_america,europe,asia_pacific,latam_mena_africa}.json`. These were **not re-derived or verified this session**; precision is about +/-0.5 km and in two cases the coordinate may sit on an associated power site rather than the data halls (xAI Southaven; Microsoft WDM cluster centroid). `source_url` is the most official record cited by the ledger entry (LPSC minutes, PA DEP plan approval, PSC Wisconsin docket, An Bord Pleanala order, MME portaria, MPF filing, NSW Planning Portal, Iowa DNR draft Title V, MDEQ agreed order) and `source_type`/`licence` follow that document; where the ledger's best source is press, `source_type=ledger`, `licence=ledger`. `ledger_entry_id` is filled on every such row and on the Google rows that overlap ledger subjects (The Dalles, Hamina, Storey County, Cerrillos, Canelones).
Ledger subjects that are policies, clusters, portfolios or cancelled projects (Digital Gateway voided rezoning, Zeewolde, Aragon four sites, Cape Town four sites, Humain 211 plots, Stargate Argentina with no site, Johor, Batam, Queretaro, Lagos, Teraco) were not turned into rows because no single site coordinate exists.

### 2d. Schema notes
Columns are as specified plus two trailing columns: `coord_source_url` (where the coordinate came from when it differs from `source_url`) and `notes` (corroborating records, generator inventories, caveats). Enumerations were extended where honesty required it: `source_type` adds `wikipedia` and `ledger`; `licence` adds `CC-BY-SA-4.0` and `ledger`. `generator_mw_permitted` holds diesel backup MW where a permit lists it and, for xAI Memphis/Southaven and Homer City, on-site gas-turbine MW (flagged in `notes`). `capacity_mw_it` is filled only from a register/permit/operator figure (AWS Susquehanna 300 MW is the ISA co-located load, not IT load - noted).

## 3. Registers harvested into the unlocated backlog (333 rows)
- **Virginia DEQ "Issued Air Permits for Data Centers"** (`https://www.deq.virginia.gov/news-info/shortcuts/permits/air/issued-air-permits-for-data-centers`, list dated 2025-11-17, 184 permit rows => **173 registrations** after deduplicating by registration number; columns: Air Site Name, Registration No, Permit Issuance Date, Program Type, City/County, Regional Office). The page has no addresses, coordinates, generator data or CSV. Permit PDFs (deq.virginia.gov/home/showpublisheddocument/...) do carry street address and full generator inventories (checked: reg 74129 Amazon IAD-100..103, 10261-10321 Tanner Way, Manassas, 97 gensets ~236 MW, 500 h/yr cap), so geocoding is a matter of pulling ~170 PDFs and running an address geocoder or joining to EPA FRS. The list includes a few non-data-center registrations (PWCSA pumping station, Sentara, NOAA Wallops); they were kept so the register is reproduced faithfully.
- **Texas Comptroller "Data Center Lists"** (`https://comptroller.texas.gov/taxes/data-centers/data-center-lists.php`): 67 Qualifying Data Center Projects (complete) + 85 Qualifying Large Data Center Projects (rows alphabetically before "Cipher Black Pearl" in the large list were not captured because of fetch windowing; the TX 301-310 Vantage/Oracle rows were collapsed to one). Columns: name, effective date, owner, occupant, operator. No addresses. Occupant column is valuable (Microsoft, Google via "Design, LLC", Oracle, Amazon, CoreWeave, Anthropic, Lambda, LinkedIn); several entries are crypto miners or shell names.
- **EPA Ireland IE licences**: ADSIL Tallaght P1177-01 (46 gensets, 251.43 MWth cap) and ADSIL Drogheda P1181-01 review (53 gensets, 306 MWth). Licence documents carry no grid reference.
- **TCEQ** CyrusOne SAT2-4 (RN110660743; 35 gensets ~82.6 MW; coordinate fields blank). **NDEP** Amazon TRIC AP7374-4768 (358 gensets; location given as PLSS sections T19N R22E). **SC DES** Autumn Timber CP-50000183 (generator data confidential). **NC DAQ** Tapaha Dynamics/Google Lenoir (located in main file; permit tracked here).
- **IMDA/EDB Singapore** DC-CFA (2023, ~80 MW) and DC-CFA2 (2026, 200 MW on Jurong Island) awards - awardees named, parcels not.

## 4. Sources tried that gave no site-level yield
Loudoun/PWC news and GIS directory pages; catalog.data.gov Loudoun datasets; NVE Norway (reports only); Epoch AI (see above); data.gov.ie EPA layer (stale); EEA Industrial Emissions Portal facility pages (never surfaced); Wikimedia Commons categories (never surfaced); DBpedia (never surfaced); Iowa DNR draft Title V for Microsoft WDM (address and 128 gensets, no coordinates); SC DES statement of basis; UK EA permit consultations (surfaced for NTT Hemel Hempstead but postcodes need a geocoder); operator pages (Equinix/Digital Realty never surfaced through the search engine). Not attempted for lack of budget: Johor state approvals, Chile SEA (robots), Noord-Holland/Amsterdam annexes, Hollands Kroon, UK planning registers, Taiwan/Korea/Japan siting announcements, Maricopa AQD, Georgia EPD, Ohio EPA.

## 5. Duplicate handling
- Virginia DEQ rows deduplicated on Registration No (latest permit date kept; earlier program/dates appended).
- Google: two Council Bluffs campuses kept as two rows (distinct Wikipedia entries); Wikipedia "Frankfurt" mapped to Google's "Hanau"; "Atlanta" to "Douglas County"; "Reno" to "Storey County"; "Widows Creek" to "Jackson County".
- Ledger overlaps with Google rows were merged into the Google row via `ledger_entry_id` rather than creating a second row.
- xAI Colossus 1 (Memphis, TN) and the Southaven (MS) turbine/Colossus 2 record are kept as two rows because the ledger holds two coordinates; the MS row is flagged as possibly the power site.
- Texas Comptroller large-list rows that duplicate the qualifying list (Giga Texas, Hockley, Cipher Black Pearl) are kept once per list with different `backlog_id` suffixes derived from the name; de-duplicate on name when consuming.

## 6. Recommended next steps for a re-run with URL approval
1. Approve the Overpass and Wikidata URLs above: one Overpass call per country (`area["ISO3166-1"="XX"]`, nodes+ways with `out center`) and one SPARQL call give several thousand ODbL/CC0 points in minutes.
2. Approve the PWC `MapServer/9/query` URL (complete Prince William inventory with status and GFA) and locate the equivalent Loudoun layer.
3. For the 173 Virginia DEQ registrations, fetch each permit PDF for the street address, then geocode (Census geocoder) or join to EPA FRS by name.
4. Approve `https://epoch.ai/data/data_centers/data_centers.csv` (CC-BY) for ~95 frontier-AI sites with satellite-verified coordinates and power.
5. TCEQ: use the Central Registry (RN) search for every Texas Comptroller entry; RN records carry lat/lon.
