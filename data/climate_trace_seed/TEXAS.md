# Texas, rebuilt from issued authorizations, 2026-10-22

This replaces the Texas run of 2026-10-21. That run joined the Comptroller's datacenter register (the sales-tax exemption list, which has no addresses) to TCEQ's two indexes of *pending* air-permit applications. An application drops off those indexes once its permit issues, so only 17 of 153 rows matched and 12 had coordinates. Its files (`tx_permits.csv`, `tx_index_rows.csv`, `tx_unmatched_tceq_packages.csv`) are kept as a record of the pending indexes.

Today's rebuild uses records that stay public after issuance:

- **EPA's Facility Registry Service** (public ArcGIS service). It ties each Texas facility to its ICIS-Air id, TCEQ Central Registry number (RN), emissions-inventory and engine-report ids, and TCEQ construction-stormwater coverage, each with a lat/lon.
- **TCEQ Title V public-notice PDFs.** The statement of basis (SOB) and the draft or effective permit (SOP) stay at their URL after issuance.
- **TCEQ air-permit project numbers** for PBR registrations, PBR certifications and standard permits, as transcribed by FracTracker from TCEQ's air-permit database. TCEQ's database refuses the fetch tool, so these were not checked against TCEQ itself and are labelled as such below.
- **Searches under the Amazon, Google and Meta LLC names** in TCEQ, utility-commission and state building-registration (TDLR) records.

Every coordinate comes from a TCEQ document or an FRS record. Generator MW is given only where a document states unit ratings, except Meta El Paso, where 366 MW is a plant total from a city release. Source forms, URLs and what blocked what are in `tx_sources.md`. An independent check of the headline figures against their documents was run before sending; its corrections are applied here.

## Counts

All counts are produced by `pipeline/tx_fetch.py --fixture` and match `tx_fetch_summary.json`.

| | 2026-10-22 | 2026-10-21 |
|---|---|---|
| Texas datacenter facilities identified from regulator records | **129** | 17 matched |
| with a TCEQ air authorization or an EPA ICIS-Air record | **38** (19 with coordinates) | |
| of which issued, effective, or an existing registration | **14** (7 with coordinates); split by source below | |
| of which Title V at draft (Vantage TX2, TX11) | 2 | |
| of which Title V with SOB or SOP published, status not read (Compass Red Oak, Alamo Mission, QTS Irving) | 3 | |
| of which an ICIS-Air operating record only (Equinix Dallas, Rackspace Grapevine, "STA1", Microsoft SAT15) | 4 | |
| of which pending, under review or at notice | 15 | |
| tied to its generation through a utility regulator only (Meta El Paso) | 1 | |
| with an EPA emissions-inventory or engine-report record only | 8 | |
| known only from TCEQ stormwater or Central Registry records | 82 | |
| facilities with coordinates | **109** | 12 |
| facilities with a generator count | **7** (one is Meta El Paso's 813 units, as reported by press) | 3 |
| facilities with generator MW | **3** (two on-site fleets, and Meta's 366 MW utility plant) | 2 partial reads |
| Comptroller register rows matched (of the 152 rows captured on 2026-10-20, 149 distinct ids; the full register has 175, see below) | **55 rows / 54 ids** (34 high, 20 medium confidence) | 17 |
| matched rows with coordinates | 48 | 12 |
| matched rows tied to an air record | 32 (18 to an issued, effective or registered authorization) | |
| matched rows with a generator count / with generator MW | 10 / 3 | |

The 153 rows quoted on 2026-10-21 were 152 Comptroller registrations plus one TCEQ-sourced row. Three Comptroller ids appear twice (Cipher Black Pearl, Giga Texas, Hockley). **The register, captured in full on 2026-10-22.** The matching above used the 152 rows captured on 2026-10-20, which missed the large-projects list's rows from A to "Cipher". The full page was copied on 2026-10-22 (`tx_comptroller_register_2026-10-22.txt`, parsed in `tx_comptroller_register_2026-10-22.csv`): **175 rows**, 67 on the qualifying list and 108 on the large-projects list. Fourteen were not in the matching run: Alamo Data Center (owner Alamo Mission LLC, operator Google LLC), AUS 01 02 03, Beacon Point 1, Borden County Data Center and Phase 2, Bull Data Center (IE US Development Holdings 5), C1 Bosque I and II, C1 Fort Worth, Cedarvale (large-projects entry), Childress Data Center (IE US Development Holdings 3), Cinco Data Center (operator Google LLC), Cipher Barber Lake (occupant Anthropic, PBC; operator Fluidstack USA II) and HEL05 (Galaxy Helios III, registered 2026-08-21). The register lists TX 301 to TX 310 as ten rows where the earlier capture had one, and Nexus as "Nexus Data Centers". By owner or operator entity, four of the fourteen correspond to facilities already in `tx_issued_sites.csv`: Alamo Data Center to the Alamo Mission site (TCEQ Title V O4709), Childress Data Center to IREN Childress, Borden County Data Center to Borden DC, and HEL05 to the Galaxy Helios campus. They are not counted as matches above until the next run of `pipeline/tx_fetch.py` takes the full register as input.

**The 14 issued, effective or registered, by source:**
- Read in a TCEQ permit document or index (6): Microsoft SN campus (Title V O4780, effective), CyrusOne SAT2-4 (O4794, effective, issued 2026-07-08), Microsoft SAT09-13 on Lambda Dr (O4782, effective), Sharka, Midlothian (O4262, issued 2021, revised 2026), Longhorn, Abilene (O4721 effective; NSR 177263 issued 2025-01-22), Aligned ADC Plano (NSR 131651, previously issued, renewal pending).
- Per FracTracker's transcription of TCEQ's database, not checked against TCEQ (8): PBR certifications recorded as issued for Galaxy Helios (185449, 185450, 2026-09-23), Big Watt Taylor (185746), Decennial SA01 (185751), Stream Houston I (185478), TRG DFW1 (185581) and TRG-TX (185580); existing registrations for Vantage Frontier (182627) and VoltaGrid SAT-1/2 (177637, 181707).

## Sites with permit-grade generator data

| Site | County | Coordinates | Authorization | Generators | Comptroller row |
|---|---|---|---|---|---|
| Microsoft SN campus (SN1, 2, 4, 7), 5150 Rogers Rd | Bexar | 29.480036, -98.692555 (Core Data Form; agrees with the SOP's 29°28′48″ N, 98°41′33″ W) | Title V O4780 (project 38509), effective; PBR 106.511 registration 82486 per the application | **73 units** (SOP Unit Summary), **176.5 MW** summed from the unit IDs, which carry the rating: 34 x 2.5, 20 x 2, 16 x 3, 2 x 1.5, 1 x 0.5 MW. One ID in the 3 MW group is misprinted "2MW7-2"; it is counted at 3 MW. The 2026-10-21 "9 units, 24.5 MW" was a partial read. | not established (candidates: "Microsoft Corporation" 2013, "NADC") |
| CyrusOne SAT2, SAT3, SAT4, 9554 Westover Hills Blvd | Bexar | 29.473781, -98.670945 (FRS, ICIS-Air) | Title V O4794 (project 38610), effective, issued 2026-07-08 | **35 units, 82.6 MW** per application Attachment B (32 x MTU 16V4000G83 at 2,499 kW + 3 x 12V2000G85 at 890 kW). Table 1 of the same application lists 30 + 5 of those models (79.4 MW); 82.6 MW is the higher of the application's two readings. | San Antonio Data Center II, III (medium) |
| Compass Red Oak | Ellis | 32.537981, -96.804371 | Title V O4679 (project 37072), PBR 106.511 | 390 units (application OP-SUM, EMGEN1-EMGEN390); kW not stated (SOB class 560-2,237 kW) | Red Oak Texas DC, DC 2 |
| QTS Irving DC3-DC6, 6431 Longhorn Dr | Dallas | 32.89607, -96.98123 (stormwater record) | Title V O4771 (project 38315), PBR 106.511 | 120 emergency + 4 house units (SOB); kW not stated | QTS Irving DC3, QTS Irving 1 |
| Vantage TX11, 14720 Omicron Dr | Bexar | 29.416975, -98.791595 | Title V O4791 (project 38602), draft | 86 at full build-out (SOB); each in the >2,237 kW class | TX11, TX11-12 |
| Vantage TX2 (TX21-22), 5207 Rogers Rd | Bexar | 29.483403, -98.700551 | Title V O4790 (project 38600), draft | 65 at full build-out (SOB); each in the >2,237 kW class. Replaces the 2026-10-21 "1 unit, 3.0 MW", a partial read. | TX21-22 |

## A utility-regulator link: Meta El Paso

| Site | Record | Generation | Comptroller row |
|---|---|---|---|
| Meta El Paso campus (northeast El Paso), customer Wurldwide LLC | El Paso Electric's application to the Public Utility Commission of Texas for a certificate for its McCloud generation facility. The State Office of Administrative Hearings proposal for decision is filed; the PUC decision is pending. The proposal's file name (`59076_176_1686197.PDF`) suggests docket 59076; not confirmed. | **366 MW natural gas**, intended to serve the Wurldwide (Meta) data center during a bridge period of up to five years (City of El Paso release, 2026-06-18; the city opposes the certificate). Inside Climate News and San Antonio Current report, from the proposal for decision, 813 modular generators of 450 kW and exclusive supply to the campus; not read for this package. A TCEQ air permit is reported; its number was not found. | Wurldwide LLC DBA Statue LLC (high) |

This is the one public regulator proceeding found that ties a named Texas datacenter to dedicated generation outside TCEQ's air program. The proposal for decision is first in the browser list.

## Other datacenters with an issued, effective or registered authorization

| Site | Coordinates | Authorization |
|---|---|---|
| Sharka (Midlothian) | yes | Title V O4262, issued 2021, revised 2026 |
| Microsoft SAT09-13 (Lambda Dr) | yes | Title V O4782, effective |
| Longhorn Data Center, Abilene (Crusoe/Lancium) | yes | Title V O4721, effective; NSR 177263 issued 2025-01-22, 7 diesel generator groups and 2 gas turbine groups >30 MW each; Crusoe's PSD expansion 182126 pending |
| Aligned ADC Plano | yes | NSR 131651, renewal pending |
| Galaxy Helios (Afton) | yes | PBR certifications 185449 and 185450, recorded as issued 2026-09-23 (FracTracker) |
| Stream Houston I; TRG DFW1 (Farmers Branch); TRG-TX (Spring); Big Watt Taylor; Decennial SA01 | no | PBR certifications recorded as issued (FracTracker) |
| Vantage Frontier campus (TX301-310) | no | PBR 106.511 registration 182627 (FracTracker). Its gas plant, VoltaGrid ABI-1 (NSR 182467, RN112247101, 299 FM 604, Shackelford County; Jenbacher J620/J624 engines, counts not stated), is at notice: TCEQ's notice says it serves "a nearby data center", and FracTracker identifies that as Frontier. |
| VoltaGrid SAT-1 and SAT-2 | no | standard-permit registrations 177637, 181707 (FracTracker) |

## Pending, under review or at notice (15)

- IREN Childress (Title V 4951); CyrusOne DFW10/11/17 (Title V 4941)
- Nexus Hubbard (183046/PSDTX1700); Goodnight (182880)
- Fermi Matador (183462). The University of Houston EENR Center reports commission approval in February 2026 (90 Siemens turbines); not verified on a TCEQ page.
- ROMAN Energy Center (NSR 184403 / PSDTX1712 / GHGPSDTX276, application 411006), applicant IP Roman III Gas LLC, an Intersect Power entity. Alphabet acquired Intersect (closed 2026-03-10) but not Intersect's existing operating Texas assets, so the applicant's ownership is not established. It shares a name with the Comptroller row "ROMAN" (Google's reported Project Roman at Hereford); that is a candidate match only, not counted above.
- Edged Irving (106.511 registration 185610); Edged Caldwell power plant (standard permit 185697); Borden DC (185712); Vector Lightning (185723); Bastrop 1 (185558); and four gas standard permits or engine registrations under review (AIUS Cottle 185613, Kilby 185498, MARA Pecos 185543, SMS Horizon 185685).

**The governor's pause.** On 2026-09-21 the Governor of Texas wrote to TCEQ: "I direct the TCEQ to pause the issuance of all permits related to data center projects", until ERCOT completes its review (letter published on gov.texas.gov). TCEQ's interim executive director replied on 2026-10-19 that TCEQ "has paused the issuance of all permits related to the construction or development of infrastructure" for data centers, is screening pending applications, and, "where possible, is suspending" claimed authorizations that need no affirmative permit. FracTracker reports seven emission-limit certifications recorded as issued after the directive (the PBR certification rows above); TCEQ told 404 Media it "has not issued any permits related to data centers". The ledger has not checked this against TCEQ's own records; see ledger entry `us-tx-tceq-datacenter-permit-pause`.

## Corrections to 2026-10-21

- **Microsoft SAT rows re-pointed.** All six were pointed at the SN campus. FRS puts "SAT 11 & 12" on Lambda Dr (Title V O4782, whose site name lists SAT09-SAT13), so SAT09-13 now points there; "SAT14" has its own stormwater record on Rogers Rd; "SAT15" its own ICIS-Air record at 3555 Westover Link; "SAT 89/90" is a project site in Castroville, Medina County. The SN campus is now matched to no row.
- **Power-plant permits now matched.** Nexus Hubbard, Goodnight and Fermi were rejected as "not a data center"; their packages are the campuses' own power-plant permits.
- **Hutto Data Center 3 matched (medium).** TDLR building registrations put Hutto Data Center 3 LLC (3399 County Road 132) and Hutto Data Center Campus LLC (4200 County Road 132) on the same campus.
- **DFW-04 matched to its own building** ("Aligned Plano DFW04" stormwater record) instead of the ADC Plano package.
- **Dropped figures.** Alamo Mission's "9 x 560 kW, 5.04 MW" (560 kW is an NSPS class boundary, not a rating) and Vantage TX2's "1 unit, 3.0 MW" (partial read).

## What still needs a browser or a records request

1. **Generator inventories for the PBR and standard-permit sites.** Unit count, kW and hours are in the registration files, which sit in TCEQ Records Online behind a JavaScript search. `tx_browser_list.csv` lists 88 searches: 13 issued registrations or permits by number (priority 1, the files that carry unit kW), 27 Title V permits and RN lookups (2), 19 pending or unconfirmed items (3) and 29 RNs of non-air sites (4).
2. **97 Comptroller rows unmatched**: 12 Amazon-operated or -occupied (ALE60-62, Bexar 1, Flamingo, Gulf Horizon, Pecos Ranch, Spectrum, Stingray, Cipher Black Pearl, NTT TX2/TX3), 7 Google entities (SDC DFW VIII, Meitner, Thelma, Rise, PowerCampus Lancaster, Hutto DC 4, ROMAN), 28 bitcoin-mining or crypto sites, 50 others. 29 have a candidate site in `tx_issued_sites.csv` (`backlog_candidates`) that needs one confirming document.
   - Amazon: no TCEQ air record found under Amazon Data Services, COPT or Cipher; the only Amazon NSR application (183703, Cleburne) is a warehouse. TDLR registrations give Amazon Data Services addresses at 12807 Donop Rd, San Antonio (TABS2026014987), COPT "Potranco" at 1535 NW Crossroads (TABS2026014988) and "Project Eagle" in Boling, Wharton County (TABS2026023825/-826/-832/-834); no document ties them to a Comptroller project name.
   - These operators file under LLCs without "data center" in the name, and most hold only PBR 106.511 authority, which leaves no FRS air record.
3. **A Public Information Request to TCEQ** (Air Permits Division) would close the gap in one step:
   > An export from the NSR permits database of all authorizations 2015-present for regulated entities with NAICS 518210 or SIC 7374, or whose regulated-entity name contains "data center": PBR registrations and certifications under 30 TAC 106.511/106.512/106.6, Air Quality Standard Permit for Electric Generating Units registrations, and NSR permits. Fields: permit number, project number, RN, CN, regulated-entity name and address, county, permit type, rule, received, issued and status dates. Plus the engine and turbine tables (count, make/model, kW or hp, fuel, annual hours) from each registration.
4. **A live run of `pipeline/tx_fetch.py` from a laptop.** It pulls all Texas ICIS-Air records and the full FRS operator-name list (now including Stack, Riot, Whinstone, Bitdeer, Edged, VoltaGrid, Galaxy, TRG, Big Watt, Decennial and Yondr), filters the ECHO Exporter, fetches TCEQ air-permit project reports, and downloads every PDF named in the authorizations table; `--psei 2024` and `--central-registry-coastal` add the TCEQ point-source emissions inventory and the Central Registry file. The fetch tool used to build these files could not re-query FRS (it cached responses by URL path), so a live run should fill the 19 air sites still without coordinates. The air-permit report parser and the ECHO SIC parameter are untested.

## Files

- `tx_issued_sites.csv`: 129 facilities with identity, coordinates and their source, TCEQ and EPA ids, authorization type and status, generator count and MW with basis, source URLs, and the Comptroller match (`backlog_id`, confidence, basis) or unconfirmed candidates.
- `tx_site_links.csv`: the curated joins (site to FRS ids to TCEQ authorizations to Comptroller rows). Edit it to accept a candidate; the repository copy is `sites/tx_site_links.csv`.
- `tx_browser_list.csv`, `tx_sources.md`, `tx_fetch_summary.json`.
- `tx_comptroller_register_2026-10-22.txt` (the register page as copied from a browser) and `tx_comptroller_register_2026-10-22.csv` (175 rows, with a flag for rows missing from the 2026-10-20 capture).
- The script and its fixtures are in the repository: `pipeline/tx_fetch.py`, `pipeline/fixtures/tx_issued/`. `python3 tx_fetch.py --fixture` reproduces these files byte for byte; the repository's CI checks that it does.
