# Independent check of the Texas figures, 2026-10-22

Checker: a separate reviewer who had not built the Texas files, asked to check the headline claims of `TEXAS.md` against the original documents and to treat anything confirmed only by press as not confirmed. Its report follows, lightly edited (one working-file path removed). Every correction below is applied in `data/climate_trace_seed/TEXAS.md`, `tx_issued_sites.csv`, `tx_site_links.csv` and `tx_sources.md`; the one change of substance to the counts is that the Google "ROMAN" match was demoted to a candidate (55 matched rows / 54 ids, from 56 / 55), and "22 issued or in force" was replaced by a count the script derives (14 issued, effective or registered, 8 of them per FracTracker's transcription).

---

I couldn't confirm 3 of the 9 claims from a primary document. Two more are confirmed only in part. One count in the report's table, "22 issued or in force", is wrong as stated.

I didn't edit any files. Shell access to tceq.texas.gov was denied by the proxy, so all reading went through WebFetch.

**Blocked:**
- `38509-ac.pdf`, `411006-ac.pdf`, `nsr-pending-permits.html`, `184403-pls-english.pdf` and the PUC `59076_176_1686197.PDF`: the permission request went unanswered.
- The airperm project reports: TCEQ's robots.txt refuses the fetch tool.

| # | Claim | Verdict | Document / section | Correction wording |
|---|---|---|---|---|
| 1 | MS SN: 73 units, 176.5 MW; coordinates | Confirmed with correction | `38509sop.pdf` (header "Initial Issuance- Effective"), Unit Summary: 2 + 28 + 6 + 20 + 16 + 1 = 73. One ID in GRP3MWCU is printed "2MW7-2" (3MW7-2 is missing). The site's lat/long (DMS) is 29°28′48″, 98°41′33″. | "73 units (O4780 Unit Summary). MW is read from unit IDs. Coordinates agree with the SOP's DMS; the Core Data Form was not re-read." PBR registration 82486 is not confirmed: the SOB gives no number. |
| 2 | CyrusOne: 32×2,499 + 3×890 kW = 82.6 MW | Confirmed with correction | `38610-ac.pdf`, Attachment B: "Number of Units: 32 generators" (2499 KW) and "3 generators" (890 KW). Attachment A Table 1 lists **30 × 16V4000G83 + 5 × 12V2000G85**. `38610sop.pdf`: effective, issued 2026-07-08. | "35 units; 82.6 MW per Attachment B. Table 1 of the same application gives 30 + 5 (79.4 MW)." |
| 3 | Compass 390; QTS 120 + 4; TX11 86; TX2 65 | Confirmed with correction | Compass: `37072-ac.pdf` OP-SUM, EMGEN1–EMGEN390 (p. 12 of 23); the SOB states no count. QTS: `38315sob.pdf`, "One hundred twenty… emergency generators (EGEN1–EGEN120), four… house generators". TX11: `38602sob.pdf`. TX2: `38600sob.pdf`, "At full build-out… sixty-five". Both `38600sop.pdf` and `38602sop.pdf` are "Initial Issuance - Draft" with no issuance date. | Label TX2 "O4790 draft". |
| 4 | Meta El Paso | Partly confirmed | City of El Paso release of 2026-06-18: "366-megawatt natural gas facility"; "Wurldwide (Meta)". The release does not say "subsidiary", gives no 813 × 450 kW, never uses "exclusively", and gives no docket number. | "…is intended to serve the Wurldwide (Meta) data center during a bridge period of up to five years (City release). Inside Climate News reports 813 × 450 kW and exclusive supply. Docket 59076 is not confirmed (file name only)." |
| 5 | Governor's pause directive; APD-CERTs kept issuing | Directive confirmed. APD-CERTs not confirmed. | Governor's letter of 2026-09-21 to Kelly Keel (`gov.texas.gov/uploads/files/press/TCEQ_Data_Center.pdf`): "I direct the TCEQ to pause the issuance of all permits related to data center projects until ERCOT completes its review." It does not mention PBRs or certifications. TCEQ's reply of 2026-10-19 says it is screening and suspending "claimed authorizations" where possible. Only the FracTracker article says "seven emission-limit certifications… recorded as 'issued'". TCEQ told 404 Media it "has not issued any permits related to data centers." | "FracTracker reports seven emission-limit certifications recorded as issued after 2026-09-21; TCEQ disputes issuing data-center permits; not checked against TCEQ records." |
| 6 | ROMAN / IP Roman III Gas / Alphabet | ROMAN: not confirmed. Alphabet: confirmed with correction. | All TCEQ ROMAN pages were blocked. Alphabet's own announcement (abc.xyz): "Intersect's existing operating assets in Texas… will not be part of the acquisition… continue to operate as an independent company." Closed 2026-03-10 (Cleary Gottlieb). | "IP Roman III Gas LLC (Intersect Power; Alphabet acquired Intersect but not its existing operating Texas assets). The link to Google's Project Roman is a name match only." |
| 7 | VoltaGrid ABI-1 | Confirmed with correction | `182467-pls-english.pdf`: CN606076008, RN112247101, "299 Farm to Market 604, Abilene, Shackelford County", Jenbacher J620/J624, no counts or MW. It says "a nearby data center" and never names Vantage. | "…serving a nearby data center (TCEQ); identified as Vantage Frontier by FracTracker." |
| 8 | Helios APD-CERT 185449/185450 issued 2026-09-23 | Not confirmed (primary record) | Airperm 415287 and 415288 are blocked. Only FracTracker's spreadsheet (tab "TCEQ actions after the order") lists both as "Emission-limit certification issued", Sep 23, 2026. | "…recorded as issued 2026-09-23 per FracTracker; the TCEQ record was not checked." |
| 9 | Arithmetic and counts table | Sums confirmed; "22 issued" contradicted | 176.5 MW / 73 units and 82.638 MW / 35 units are correct (the 30/5 split gives 79.42 MW). These rows match the CSV and the summary file: 129, 109, 38 (19 with coordinates), 7, 3, 8, 82, 1, and 55 Comptroller ids (34 high / 21 medium). **22 issued** can't be derived: the script's own rule gives 13 facilities (17 counting the ICIS-only sites), and `tx_fetch_summary.json` gives 15. The 22 counts the two draft Vantage permits, plus QTS, which has only an SOB. | "…of which issued or in force: at most 20 (O4790 and O4791 are drafts); 14 with coordinates." |

**Other statements that go beyond their sources:**
- **Lines 10 and 84**, "Google's Project Roman gas plant" and "Google Project Roman's ROMAN Energy Center": these are name matches only. The CSV's "(Intersect Power, Alphabet-owned)" ignores the Texas carve-out.
- **Line 13**, "MW appears only where a document states unit kW": Meta's 366 MW is a plant total, and its unit kW comes only from press.
- **Line 53**, "exclusively": the CSV and SOURCES.md also call Wurldwide a "Meta subsidiary", but that word comes only from press.
- **Line 47**: TX2 (O4790) is not marked as a draft.
- **Line 92**: the APD-CERT finding is FracTracker's, not shown in Public Citizen's work. TCEQ's denial is left out.
- **Line 7 and SOURCES.md §3**, "TCEQ links listed by FracTracker": the spreadsheet as rendered shows no URLs, so the project numbers are FracTracker's own transcription.
- **Line 42**: PBR registration 82486 comes from an application that wasn't re-read; the SOB lists no registration number.

Sources (non-TCEQ):
- [Governor's letter](https://gov.texas.gov/uploads/files/press/TCEQ_Data_Center.pdf) and [press release](https://gov.texas.gov/news/post/governor-abbott-directs-tceq-to-halt-data-center-permits)
- [TCEQ response](https://www.tceq.texas.gov/downloads/response/tceq-response-gov-abbott-dc-directive.pdf)
- [FracTracker](https://fractracker.org/2026/10/texas-data-center-permits-after-governor-halt/) and [its spreadsheet](https://docs.google.com/spreadsheets/d/1O8F1erF3yiHnDjWpXgC5GI5bp66H-kAYqyXAatxw4lE/edit#gid=1531514719)
- [404 Media](https://404media.co/it-aint-right-texas-said-it-would-halt-data-center-permits-the-state-is-pushing-ahead-anyway)
- [Inside Climate News: Meta](https://insideclimatenews.org/news/24092026/el-paso-electric-only-considered-gas-to-power-meta-data-center/) and [Inside Climate News: permits](https://insideclimatenews.org/?p=115152)
- [City of El Paso release](https://www.elpasotexas.gov/assets/Press-Releases/2026.06.18-NEWS-RELEASE_City-Opposes-Proposed-McCloud-Generation-CCN-Cites-Deficient-Analysis-and-Risks-to-Ratepayers.pdf)
- [Alphabet announcement](https://abc.xyz/investor/news/news-details/2025/Alphabet-Announces-Agreement-to-Acquire-Intersect-to-Advance-U-S--Energy-Innovation-2025-DVIuVDM9wW/) and [Cleary Gottlieb](https://www.clearygottlieb.com/news-and-insights/news-listing/alphabet-completes-4-75-billion-acquisition-of-intersect-power)
- [Bracewell](https://www.bracewell.com/resources/governor-abbott-orders-tceq-to-pause-all-permit-issuance-for-data-center-projects/)
