# Texas datacenter air authorizations: sources (checked 2026-10-22)

The 2026-10-21 run used TCEQ's two pending-application indexes, which drop a permit once it issues. The sources below keep issued authorizations. For each source: what it holds, whether it can be scripted, the exact URL and query form, and what was blocked here. Direct downloads were off in the build, so everything was read through the fetch tool. The web-search budget ran out in the first pass. A same-day follow-up pass covered data.texas.gov, the emissions inventory and the Amazon/Google/Meta LLC names (sections 10-12).

## Summary

| # | Source | Holds issued air authorizations? | Scriptable | Status here |
|---|---|---|---|---|
| 1 | EPA FRS, public ArcGIS feature service | Links each facility to its ICIS-Air id, TCEQ Central Registry RN, EIS, CEDRI and TCEQ stormwater ids, with lat/lon | Yes, no token | **Used.** 286 Texas interest rows captured |
| 2 | TCEQ Title V public-notice PDFs (statement of basis, draft or effective permit) | Yes: unit groups, NSPS kW classes, NSR authorization references, sometimes PBR registration numbers and counts | Yes (static PDFs) | **Used.** 10 datacenter Title V projects read |
| 3 | TCEQ NSR air-permits database ("airperm") | Yes: PBR registrations, PBR certifications (APD-CERT), standard permits and NSR permits, pending and complete | Yes from a laptop (plain ColdFusion pages) | Robots-blocked for the fetch tool. Project numbers came from a FracTracker sheet (FracTracker's transcription; the rendered sheet shows no TCEQ links) |
| 4 | TCEQ Records Online / Central File Room (CFR) | Yes: the documents themselves (registrations, permits, technical reviews) | **No** (JavaScript search) | Reachable but needs a browser, so these go in tx_browser_list.csv |
| 5 | EPA ECHO air_rest_services | Texas ICIS-Air facilities (majors and synthetic minors) | Yes from a laptop | Robots-blocked for the fetch tool |
| 6 | ECHO Exporter and ICIS-Air bulk ZIPs | Same as 5, in bulk | Yes (download plus filter) | Too large for the fetch tool; pipeline/tx_fetch.py filters them locally |
| 7 | TCEQ Central Registry (crpub) | RN, name, address, NAICS/SIC per regulated entity | Form POST from a laptop | Robots-blocked for the fetch tool |
| 8 | TCEQ pending indexes (Title V, NSR) | Pending applications only | Yes | Used yesterday. Still useful for applications in process |
| 9 | TCEQ eCID (Commissioners' Integrated Database) | Notices and decisions for major permits | Yes | Links captured, pages not opened |
| 10 | data.texas.gov / Texas Socrata network | No TCEQ air-permit, PBR or standard-permit dataset. TCEQ publishes complaints, violations, enforcement, spills, waste and water permits, and one regional Central Registry file. | Yes (Socrata API) | Checked in the follow-up; the Central Registry file's columns were not verifiable |
| 11 | TCEQ Point Source Emissions Inventory | Annual site/account emissions for the ~2,000 sites above 30 TAC 101.10 thresholds. Large datacenter generator fleets may report. | Yes (xlsx download) | 54 MB workbooks, not readable through the fetch tool; `--psei` in pipeline/tx_fetch.py |
| 12 | PUC of Texas (utility certificate cases), plus TDLR building registrations for LLC names and addresses | PUC: dedicated generation for a named datacenter (Meta El Paso). TDLR: owner LLC and street address per building project. | PUC Interchange PDFs: yes. TDLR: per-project pages. | PUC document blocked here (fetch refused); TDLR pages read |

No source publishes a statewide list of datacenter air permits the way Virginia DEQ does. The closest is the airperm database (3), which holds every registration but has to be searched by RN, permit number or project number.

## 1. EPA Facility Registry Service (FRS), public ArcGIS feature service

- Service: `https://services.arcgis.com/cJ9YHowT8TU7DUyn/ArcGIS/rest/services/FRS_INTERESTS/FeatureServer`. No token is needed, maxRecordCount is 2000, and the layer's lastEditDate is 2026-10-04.
  - Layer 0 `FRS_INTERESTS`: one point per facility per program. Fields: `REGISTRY_ID, PRIMARY_NAME, LOCATION_ADDRESS, CITY_NAME, COUNTY_NAME, FIPS_CODE, STATE_CODE, POSTAL_CODE, LATITUDE83, LONGITUDE83, ACCURACY_VALUE, COLLECT_MTH_DESC, REF_POINT_DESC, CREATE_DATE, UPDATE_DATE, PGM_SYS_ID, PGM_SYS_ACRNM, INTEREST_TYPE, ACTIVE_STATUS, KEY_FIELD, ...`
  - Table 1 `FRS_NAICS` and table 2 `FRS_SIC`: `PGM_SYS_ACRNM, PGM_SYS_ID, NAICS_CODE|SIC_CODE, PRIMARY_INDICATOR, KEY_FIELD`. `KEY_FIELD` = acronym + id, and it joins to layer 0.
- Program acronyms that matter in Texas:
  - `AIR` is the ICIS-Air id. Format: `TX000000` + county FIPS + sequence, e.g. `TX0000004802900724` is Bexar County.
  - `TX-TCEQ ACR` is the TCEQ Central Registry, with `PGM_SYS_ID` = the RN.
  - `EIS` is the national emissions inventory.
  - `CEDRI` is NSPS/NESHAP electronic reports; datacenter engine notifications land here.
  - `NPDES` includes TCEQ construction-stormwater coverages (`TXR15xxxx`), which give a site point for new campuses.
- Query form. GET works, and POST works for long `IN` lists:
  - `.../FeatureServer/0/query?where=STATE_CODE='TX' AND PRIMARY_NAME LIKE '%DATA CENTER%'&outFields=*&returnGeometry=false&orderByFields=OBJECTID&resultOffset=0&resultRecordCount=2000&f=json`
  - `.../FeatureServer/1/query?where=NAICS_CODE='518210' AND (PGM_SYS_ID LIKE 'TX%' OR PGM_SYS_ID LIKE 'RN%')&outFields=*&f=json`
  - `.../FeatureServer/2/query?where=SIC_CODE='7374' AND PGM_SYS_ID LIKE 'TX%'&outFields=*&f=json`
  - `.../FeatureServer/0/query?where=STATE_CODE='TX' AND PGM_SYS_ACRNM='AIR'&...`: 6,064 Texas ICIS-Air interests, about 4 pages.
- What the captures showed:
  - `PRIMARY_NAME LIKE '%DATA CENTER%'` in TX: 213 interest rows.
  - NAICS 518210 with a Texas id: 9 AIR, 6 RCRA and 6 Central Registry rows.
  - SIC 7374: 1 AIR (Rackspace) and 1 NPDES (Hockley).
  - A scan of Bexar's recent ICIS-Air sequence (`PGM_SYS_ID > 'TX0000004802900640'`) found six datacenters: STA1, Microsoft, Microsoft SAT15, CyrusOne SAT2-4, Vantage TX11 and Vantage TX2.
- Limits:
  - FRS has ICIS-Air records only for sources TCEQ reports to EPA, i.e. majors and synthetic minors such as Title V datacenters. A site authorized only by PBR 106.511 has no `AIR` record.
  - The `TX-TCEQ ACR` (RN) link is present for older entities (2008-2018 RNs) but missing for most new campuses.
  - NAICS coding is sparse.
  - FRS geocodes are usually address matches, and one was ~35 km off (rejected, see `COORD_REJECT` in pipeline/tx_fetch.py).
  - Amazon, Google and Meta datacenters do not appear under those names. They file under shell LLCs or contractors.
- Capture note: the fetch tool layer cached by URL path and ignored the query string, so each query here used a different letter-case of `ArcGIS/rest/services`. Responses with no features also came back as "server error" through that layer. Neither applies to a normal client.

## 2. TCEQ Title V public-notice documents (stay public after issuance)

- `https://www.tceq.texas.gov/assets/public/permitting/air/publicnotice/<project>sob.pdf`: statement of basis
- `.../publicnotice/<project>sop.pdf`: draft or effective permit. The page header says "Initial Issuance- Draft" or "Effective".
- `.../publicnotice/<project>pa.pdf`: announcement
- Applications: `https://www.tceq.texas.gov/assets/public/permitting/air/reports/applications/<project>-ac.pdf` and `-tc.pdf`. Some stay up; four returned 404 yesterday.
- Datacenter Title V projects found:

| Project | Permit | Site | Notes |
|---|---|---|---|
| 37072 | O4679 | Compass Red Oak | |
| 37459 | O4709 | Alamo Mission | |
| 37589 | O4721 | Longhorn Data Center, Abilene | NSR 177263 |
| 38315 | O4771 | QTS Irving | |
| 38479, 39571 | O4262 | Sharka | PBR reg 153622 |
| 38509 | O4780 | Microsoft SN | |
| 38511 | O4782 | Microsoft SAT09-13/40/46 | |
| 38600 | O4790 | Vantage TX2 | |
| 38602 | O4791 | Vantage TX11 | |
| 38610 | O4794 | CyrusOne SAT2-4 | |
| 40584 | 4941 | CyrusOne DFW | pending |
| 40835 | 4951 | IREN Childress | pending |

- Content:
  - Unit IDs and groups, and NSPS IIII power classes (e.g. ">2,237 kW", which is a class, not a rating).
  - The "NSR Authorization References" table, which lists PBR 106.511 and sometimes the registration number in brackets.
  - Site lat/long in DMS in the permit.
  - Sometimes the unit count ("86 diesel emergency generators at full build-out").
  - Unit kW is usually absent. It appears in the application's OP-SUM table (Microsoft SN) or equipment list (CyrusOne).
- There is no index of issued Title V projects. Project numbers come from the pending index while pending, or from web search afterwards. pipeline/tx_fetch.py downloads the SOB, SOP and application for every project number it holds.

## 3. TCEQ NSR air-permits database ("airperm")

- Start page: `https://www2.tceq.texas.gov/airperm/index.cfm?fuseaction=airpermits.start`. TCEQ calls it the "Status of Air New Source Review Permit Applications and Federal Air Operating Permit Applications" and says it covers *pending and completed* applications.
- Project report: `https://www2.tceq.texas.gov/airperm/index.cfm?fuseaction=airpermits.project_report&proj_id=<IMS project number>`. This URL form appears in TCEQ links cited by Inside Climate News and FracTracker.
- TCEQ guides 6433 and 6434 give the search recipe:
  - Enter the RN, set Status = Complete, and set Permit Type = "Permit by Rule" to list PBR registrations. The "Permit Number" column holds the registration number, which is what CFR is searched by.
  - `https://www.tceq.texas.gov/assets/public/permitting/air/Guidance/Title_V/titlev-nsr-guide6433.pdf`
  - `https://www.tceq.texas.gov/assets/public/permitting/air/Guidance/Title_V/titlev-pbr-guide6434.pdf`
- PBR 106.511 itself does not require registration. Sites register when they certify emissions (APD-CERT), and many large datacenters do. Unregistered PBR use leaves no record anywhere public.
- **Blocked here:** robots.txt disallows www2.tceq.texas.gov/airperm for the fetch tool. From a laptop it is ordinary HTML.
  - `pipeline/tx_fetch.py` fetches the project report for every IMS project number it holds and saves the raw HTML. The parser is untested.
  - `--airperm-dump-form` prints the search form's field names so an RN or permit-type search can be wired up.
- Project and permit numbers for 25 datacenter-related actions (APD-CERT, 106.511 registrations, standard permits, PSD notices) came from FracTracker's sheet "TCEQ data center permits since the Sept 21 halt", which transcribes these TCEQ actions (the rendered sheet shows no TCEQ URLs, so the numbers are FracTracker's): `https://docs.google.com/spreadsheets/d/1O8F1erF3yiHnDjWpXgC5GI5bp66H-kAYqyXAatxw4lE/edit#gid=1531514719`. That sheet covers only actions after 2026-09-21. Older registrations need the airperm RN search or CFR. FracTracker records seven PBR certifications as issued after the governor's 2026-09-21 directive; TCEQ told 404 Media it has not issued data-center permits since then. Neither was checked against TCEQ's own records.

## 4. TCEQ Records Online / Central File Room (CFR Online)

- `https://records.tceq.texas.gov/cs/idcplg?IdcService=TCEQ_SEARCH` (WebCenter Content). The page loads, but search and results run in JavaScript, and a guessed `GET_SEARCH_RESULTS` URL returned only the "enable JavaScript" notice.
- Record series: "AIR / New Source Review Permit" (NSR permits, PBR registrations and certifications, standard permits) and "AIR / Federal Operating Permit".
- Search fields: Central Registry RN, Primary ID (permit or registration number, no leading zeros, no "O"), Secondary ID (project number, post-2014), Regulated Entity Name, Address, and Quick Search (full text).
- Results can be exported as CSV or XLS. One search is capped at 2,000 records. Pre-2012 files may be paper only.
- Guides:
  - `https://www.tceq.texas.gov/downloads/permitting/air/guidance/cfr-quickguide.pdf`
  - `https://www.tceq.texas.gov/downloads/agency/data/records-services/how-to-search-tceq-records-online.pdf`
- **Browser only.** tx_browser_list.csv has one row per search: a permit or registration number to pull, or an RN whose NSR file list should be exported. A Regulated Entity Name search for "DATA CENTER" in the NSR series, exported to CSV, is the closest thing to a statewide list and is worth one manual run.

## 5. EPA ECHO air_rest_services

- Documented form, used by pipeline/tx_fetch.py `--echo`:
  - `https://echodata.epa.gov/echo/air_rest_services.get_facilities?output=JSON&p_st=TX&p_ncs=518210` returns `Results.QueryID`
  - `https://echodata.epa.gov/echo/air_rest_services.get_download?output=CSV&qid=<QueryID>`
  - `get_qid?qid=<QueryID>&pageno=N` pages through JSON.
- The base URL and endpoints (`get_facilities, get_facility_info, get_qid, get_map, get_download, get_geojson, metadata`) are confirmed from EPA's docs and API catalogs. The all-data service documents `p_sic2`/`p_sic4` for SIC. The SIC parameter name for the air service was not confirmed, so the script tries `p_sic` and then `p_sic4`.
- **Blocked here:** echodata.epa.gov answers `robots_disallowed` to the fetch tool, and ECHO's detailed facility reports are robots-disallowed too.
- The ECHO ArcGIS layer `oeca__echo__facilities_air` needs a token.
- ECHO covers the same ICIS-Air universe as FRS `AIR`, so it adds no PBR-only sites.

## 6. ECHO bulk downloads (weekly)

- `https://echo.epa.gov/files/echodownloads/echo_exporter.zip` (392 MB): one row per facility with `FAC_NAME, FAC_STREET, FAC_CITY, FAC_STATE, FAC_COUNTY, FAC_LAT, FAC_LONG, AIR_IDS, CAA_PERMIT_TYPES, FAC_NAICS_CODES, FAC_SIC_CODES, ...`. The column list is at `https://echo.epa.gov/system/files/echo_exporter_columns_7-16-2025_0.xlsx`.
- `https://echo.epa.gov/files/echodownloads/ICIS-AIR_downloads.zip` (64 MB)
- `https://echo.epa.gov/files/echodownloads/frs_downloads.zip` (318 MB)
- Run `pipeline/tx_fetch.py --echo-exporter <zip>` or `--icis-air <zip>` to keep Texas rows with NAICS 518210, SIC 7374 or a datacenter-like name. This was tested here on a synthetic ZIP only.

## 7. TCEQ Central Registry

- `https://www15.tceq.texas.gov/crpub/` (also `https://www.tceq.texas.gov/goto/centralregistry`). Use it for RN, CN, regulated-entity name and address, and NAICS/SIC. There is a "Program ID Search" for permit to RN.
- **Blocked here** (robots). The repo's `pipeline/tx_permits.py --central-registry` client remains untested. tx_browser_list.csv asks for RNs for the four ICIS-Air sites that lack one.

## 8. Other regulator sources

- TCEQ eCID notices for the major-source datacenter power permits (preliminary decision mailed 2026-09-22):
  - Nexus Hubbard: `https://www14.tceq.texas.gov/epic/eCID/index.cfm?fuseaction=main.detail&item_id=389559692026054&detail=action`
  - VoltaGrid ABI-1: `...item_id=506476502025352...`
  - NRG Prairie: `...item_id=344398782026099...`
- TCEQ bilingual notices: `https://www.tceq.texas.gov/downloads/permitting/air/bilingual/pending-permit-notices/<permit>-{nori,napd,pls}-english.pdf`. These were used for Crusoe Longhorn 182126 (RN112029061, 32.50792, -99.77722) and Aligned ADC Plano 131651. `182267-nori-english.pdf` returned a client error.
- TCEQ stormwater permit summaries: `https://www2.tceq.texas.gov/wq_dpa/index.cfm?fuseaction=home.permit_summary&...`. These are on the same robots-blocked host. FRS carries the same TXR15 coverages with coordinates.
- City of Fort Worth layer `ENV_AQ_NSR_PBR_FACILITIES` (`https://testmapitwest.fortworthtexas.gov/ags/rest/services/CodeComp/Air_Quality/MapServer/3`) is a local air program's list of NSR/PBR facilities. It was seen in search results only, not opened, and may help with Fort Worth sites.
- Apart from El Paso Electric's certificate case for a plant serving Meta's El Paso campus (section 10), no public utility-regulator (PUCT/ERCOT) source tying a named datacenter to its generation was found. The governor's August 2026 audit directive has PUCT/ERCOT collect on-site generation plans but does not say they will be published.

## 10. data.texas.gov and the Texas Socrata network (follow-up pass)

- TCEQ's own data index lists these Socrata datasets:
  - Complaints `tdzs-qqjn`
  - Notices of Violation `mwzi-gyw7`
  - Notices of Enforcement `rua3-iswk`
  - Spills `xagr-a3x2`
  - IHW Notice of Registration datasets
  - Water Quality Individual Permits
  - The TCEQ index is at `https://www.tceq.texas.gov/agency/data/lookup-data/download-data.html`. Its only air-permit entry points back to the airperm database.
- The one Central Registry extract is "Texas Commission on Environmental Quality - Central Registry Files - Coastal & East Texas".
  - Socrata `tzyg-j7q4`, hosted on data.austintexas.gov. TCEQ regions 5, 10, 12 and 14 (Tyler, Beaumont, Houston, Corpus Christi). Updated 2026-09-26.
  - Export: `https://data.austintexas.gov/api/v3/views/tzyg-j7q4/export.csv?accessType=DOWNLOAD`
  - Catalog entry: `https://catalog.data.gov/dataset/texas-commission-on-environmental-quality-central-registry-files-coastal-east-texas`
  - Its column list (`/api/views/tzyg-j7q4/columns.json`) could not be opened for this package (not retrievable from the build environment), so whether it carries NAICS/SIC or program ids is unknown. `pipeline/tx_fetch.py --central-registry-coastal` downloads it and keeps rows with 518210, 7374 or a datacenter-like name.
  - "Central Registry Search Portal" (`6cbq-tcyi`) is only a link to crpub.
- `site:data.texas.gov` searches for TCEQ air or Central Registry returned nothing further.

## 11. TCEQ Point Source Emissions Inventory

- Page: `https://www.tceq.texas.gov/airquality/point-source-ei/point-source-emissions-data`
- Account-level workbooks: `https://www.tceq.texas.gov/downloads/air-quality/point-source/<year>.xlsx` for 2016-2024, about 54 MB each.
- Site summary: `https://www.tceq.texas.gov/downloads/air-quality/point-source/2010-2024-state-sum.xlsx`
- Column names are not documented on the page, and the fetch tool returns "[binary data]" for xlsx. `pipeline/tx_fetch.py --psei 2024` scans every sheet and column for 518210, 7374 or a datacenter name (needs openpyxl).
- The EPA side of the same inventory shows EIS ids for Microsoft SN (23058611), Sharka (19128811), SDC DFW-VII (21604811) and a "Plano Data Center" (21606411).

## 12. Utility regulator and LLC-name sources (follow-up pass)

### Meta El Paso

- **Wurldwide LLC** is the Comptroller's "Wurldwide LLC DBA Statue LLC". The City of El Paso's release on El Paso Electric's PUC certificate case for the **McCloud Generation facility** names "Wurldwide (Meta)" as the data-center customer: 366 MW of natural gas, intended to serve it for a bridge period of up to five years. Press reports of the SOAH proposal for decision give 813 Enchanted Rock 450 kW modular generators and exclusive supply to the campus; the proposal itself was not read.
- Sources:
  - City of El Paso release: `https://www.elpasotexas.gov/assets/Press-Releases/2026.06.18-NEWS-RELEASE_City-Opposes-Proposed-McCloud-Generation-CCN-Cites-Deficient-Analysis-and-Risks-to-Ratepayers.pdf`
  - The proposal for decision, linked from San Antonio Current and Inside Climate News: `https://interchange.puc.texas.gov/Documents/59076_176_1686197.PDF`. Not read for this package (not retrievable from the build environment). The file name suggests docket 59076; not confirmed.
- PUC Interchange PDFs are plain downloads. `pipeline/tx_fetch.py` fetches every PDF URL named in the authorizations table.

### Google

- Project Roman (Hereford, Deaf Smith County per press) may pair with **ROMAN Energy Center**:
  - Applicant: IP Roman III Gas LLC, an Intersect Power entity. Alphabet acquired Intersect (closed 2026-03-10) but not Intersect's existing operating Texas assets, which stay with an independent company, so this applicant's ownership is not established. The pairing with Project Roman rests on the shared name only, so it is kept as a candidate, not a match.
  - Permits: NSR 184403 / PSDTX1712 / GHGPSDTX276, application `https://www.tceq.texas.gov/assets/public/permitting/air/reports/applications/411006-ac.pdf`. That PDF was not read for this package (not retrievable from the build environment).
- Meitner (IP Meitner DTC LLC) is reported in Gray and Roberts counties with wind, solar and storage only. No TCEQ record was found.
- Hutto: TDLR building registrations name **Hutto Data Center Campus, LLC** at 4200 County Road 132 (`https://www.tdlr.texas.gov/TABS/Search/Print/TABS2024015381`, `.../TABS2025026905`) and **Hutto Data Center 3, LLC** at 3399 County Road 132 (`.../TABS2024018308`), Williamson County, developer Skybox.
- Thelma (Homebound Group LLC) and Rise (Platon Investments LLC): no TCEQ record found by search.

### Amazon

- Searches under Amazon Data Services, COPT and Cipher Stingray/Black Pearl found no datacenter air record.
- NSR 183703 (Amazon.com Services LLC, 1221 W Industrial Blvd, Cleburne, RN112039821, 30 generators) is a **warehouse**, `https://www.tceq.texas.gov/downloads/permitting/air/bilingual/pending-permit-notices/183703-pls-english.pdf`.
- TDLR filings for Amazon datacenter buildings, as reported by DCD. None is tied to a Comptroller project name.
  - Amazon Data Services "Bitter Blue", 12807 Donop Rd, San Antonio: TABS2026014987.
  - COPT "Potranco", 1535 NW Crossroads: TABS2026014988.
  - "Project Eagle", Boling, Wharton County: TABS2026023825, -826, -832, -834.

### Riot, Whinstone, Bitdeer, Galaxy, Edged, Stack and Switch

- Searches restricted to tceq.texas.gov returned no documents for these names. Their authorizations, if registered, are in airperm/CFR, not on tceq.texas.gov.

### VoltaGrid

- ABI-1, serving the Vantage Frontier campus: RN112247101, CN606076008, 299 FM 604, Abilene. Jenbacher J620/J624 gas engines and Caterpillar C32B black-start units. Source: `https://www.tceq.texas.gov/downloads/permitting/air/bilingual/pending-permit-notices/182467-pls-english.pdf`

### FRS operator-name searches

- Stack, Riot, Bitdeer, Edged, VoltaGrid, Galaxy, TRG, Big Watt, Decennial, Yondr, plus the Google and Amazon LLC names: **not run from the build.**
- The fetch tool caches by URL path. Every FRS path already used still returned its first response more than 40 minutes later, and new path spellings was not retrievable from the build environment that went unanswered.
- All of these names are in `FRS_NAME_QUERIES_ALL_PROGRAMS` in pipeline/tx_fetch.py for a laptop run.

## Blocked or not reached

| Source | Why |
|---|---|
| `echodata.epa.gov/*` | robots_disallowed |
| ECHO detailed facility reports | robots-disallowed |
| ECHO air ArcGIS layer | token required |
| `www2.tceq.texas.gov/airperm/*` | robots_disallowed |
| `www15.tceq.texas.gov/crpub/*` | robots_disallowed |
| `records.tceq.texas.gov` search | JavaScript only |
| `frs-public.epa.gov/ords/frs_public2/frs_rest_services.*` | access to this host was not available from the build environment. The ArcGIS service was used instead. |
| Other tabs of the FracTracker sheet | not rendered |
| FRS operator and LLC-name queries (follow-up pass) | fetch-tool path cache, and new paths not retrievable from the build environment. The queries are in pipeline/tx_fetch.py. |
| `data.austintexas.gov/api/views/tzyg-j7q4/columns.json`, `data.austintexas.gov/d/tzyg-j7q4` | not retrievable from the build environment |
| `interchange.puc.texas.gov/Documents/59076_176_1686197.PDF` | not retrievable from the build environment |
| `tceq.texas.gov/.../applications/411006-ac.pdf` (ROMAN Energy Center) | not retrievable from the build environment |
| TCEQ emissions-inventory xlsx | binary, not readable through the fetch tool |
