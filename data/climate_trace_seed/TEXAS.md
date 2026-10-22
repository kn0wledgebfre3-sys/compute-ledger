# Texas, run 2026-10-21

Texas has no equivalent of Virginia's statewide list of datacenter air permits. What exists in public: the Comptroller's register of datacenter projects certified for the sales-tax exemption (153 rows, no addresses), and TCEQ's indexes of *pending* air-permit applications (Title V and New Source Review), which list an applicant's PDF while the application is under review and drop it once the permit is issued. So the join from "a registered datacenter" to "its generator inventory" works only for sites whose application is still pending or whose package URL is already known.

Result of running the 153 Comptroller rows against the two TCEQ indexes (339 and 337 rows, updated 2026-10-21 and 2026-08-28):

- 95 rows: no application on the pending indexes. The permit is most likely issued and off the index, or filed under another entity name.
- 39 rows: a name match on an index whose package text does not identify a datacenter (no NAICS 518210, no "data center" in the text); fields cleared rather than trusted.
- 10 rows: matched through known document URLs; 7 with coordinates from the application's Core Data Form.
- 7 rows: matched on an index and verified as datacenter applications.

Verified matches: 17 (10 by known document, 7 on an index); 39 further name hits were rejected; 12 sites have coordinates.

Sites with permit-grade data:

| Site | County | Coordinates | Generators | Source |
|---|---|---|---|---|
| Microsoft SN Campus (SN1, 2, 4, 7; registered as SAT09-17, 80-90) | Bexar | 29.480036, -98.692555 | 9 units, 24.5 MW in the package read; the campus is far larger and the application covers one phase | TCEQ application 38509 |
| Compass Red Oak Datacenter | Ellis | 32.537981, -96.804371 | 390 units; unit kW not stated in the summary table | TCEQ application 37072 |
| Vantage TX2 (TX21-22) | Bexar | 29.483403, -98.700551 | 1 unit read, 3.0 MW; inventory not itemised | TCEQ application 38600 |

Four application PDFs referenced by the indexes returned HTTP 404 (taken down after issuance). One (CyrusOne 40584) extracts as glyph garbage and is flagged `garbled`.

What this says about the record: Texas, the fastest-growing datacenter market in the country by queue (ERCOT large-load requests of roughly 445 GW), has no public register that connects a datacenter to its permitted generation once the permit is issued. TCEQ's Central Registry holds the issued permits but blocks scripted access. A complete Texas extraction needs either a records request for issued datacenter permits by NAICS 518210 or a browser-driven pull from the Central Registry, both of which are feasible and neither of which was attempted today.

Files: tx_permits.csv (153 rows, one per Comptroller registration, with match method and reason), tx_index_rows.csv (the two indexes as read), tx_unmatched_tceq_packages.csv.
