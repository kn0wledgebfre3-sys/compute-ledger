# Records requests: index (prepared 2026-10-24)

Twelve requests from `review/RECORDS_REQUESTS.csv`. Each file holds a header (addressee, statute, how to file and the page it came from, deadline, requester restriction, fees), then a subject and a body under 250 words signed "[Name], [email]". Two files hold more than one filing: rr-oppd-nppd-les (3 utilities) and rr-va-deq-compliance (2 DEQ regional offices), for 15 submissions in all.

| # | request_id | Addressee | How to file | Statutory deadline | Requester restriction | Do first |
|---|---|---|---|---|---|---|
| 1 | rr-tceq-pbr-files | TCEQ Public Information Officer | Online form https://www.tceq.texas.gov/goto/or-request (or openrecs@tceq.texas.gov) | Promptly; 10 business days to give a date or seek an AG ruling | None | Nothing. 10 of the 13 numbers are from FracTracker, not TCEQ; the body asks TCEQ to search by site name if one does not match. |
| 2 | rr-mlgw-xai | MLGW Public Records Coordinator | Portal https://mlgw.justfoia.com/publicportal/home/newrequest (or mlgwpublicrecords@mlgw.org per the 2021 policy) | 7 business days | **Tennessee citizens only** | **Get a Tennessee-resident filer** with a TN driver's license or TN state/city photo ID; MLGW requires proof. |
| 3 | rr-tva-xai | TVA FOIA Officer | Portal https://foia.tva.gov/ (or FOIA@tva.gov) | 20 working days (+10 in unusual circumstances) | None | Confirm the fee category in the body ("all other"; change it if the filer is news media). |
| 4 | rr-cps-energy | CPS Energy Open Records | Email open_records@cpsenergy.com; fax (210) 353-3774; mail Maildrop CT1201, P.O. Box 1771, San Antonio TX 78296 | Promptly; 10 business days to give a date or seek an AG ruling | None | Hover the email link on CPS's page to confirm the address (it was decoded from an obfuscated link). |
| 5 | rr-svp | City of Santa Clara, City Clerk | City's NextRequest portal (probably https://santaclara.nextrequest.com/; not confirmed) or in person at 1500 Warburton Ave. | 10 days to determine (+14 days) | None | Open the City Clerk page and click its "Santa Clara NextRequest webpage" link to confirm the portal. |
| 6 | rr-oppd-nppd-les | OPPD; NPPD; LES | OPPD: online form http://ww3.oppd.com/comments-requests/?cuid=Public%20Information%20Request or LegalOperations@oppd.com. NPPD and LES: **no records channel found** on their sites | 4 business days | None in statute; OPPD's 8 free staff hours apply only to Nebraska residents and media | Use a Nebraska-resident filer if possible. **Call NPPD (1-877-275-6773) and LES (402-475-4211) for the records custodian's email or address.** File three separate requests. |
| 7 | rr-srp | SRP District, public records | SRP's online form https://www.srpnet.com/about/records-request-form | "Promptly" (no fixed days) | None (state non-commercial purpose; the body does) | Open the form in a browser; its fields could not be read here. |
| 8 | rr-grant-pud | Grant PUD Public Records Officer | Portal https://grantpudwa.nextrequest.com/ | 5 business days | None | Nothing. |
| 9 | rr-chelan-pud | Chelan PUD Public Records Officer (Lyndsey Files) | Online form on https://www.chelanpud.org/about-us/contact-us/public-records-requests or lyndsey.files@chelanpud.org | 5 business days | None | Tick the form's non-commercial acknowledgment. |
| 10 | rr-wasco-pud | Northern Wasco County PUD | **Not found** on the agency's site | Acknowledge in 5 business days; complete generally within 15 business days after that | None | **Find the PUD's website or call it for the records custodian's address**; the notes' 2345 River Rd, The Dalles OR 97058 is unverified. |
| 11 | rr-va-deq-compliance | Virginia DEQ, Northern and Piedmont Regional Offices | Portal https://vadeq.nextrequest.com/ (Department: Northern for request A, Piedmont for request B) | 5 working days (+7) | **Virginia citizens or media circulating/broadcasting in Virginia** | **Get a Virginia-resident (or qualifying media) filer.** File two portal requests; check that Piedmont covers Mecklenburg County. |
| 12 | rr-puct-mining-register | Public Utility Commission of Texas | JustFOIA portal via the "Submit a PIA Request through JustFOIA" link on https://www.puc.texas.gov/agency/about/contact/pia/ ; or mail 1701 Congress Ave / PO Box 13326, Austin TX 78711-3326 (no fax) | 10 business days | None | Click through from the PUCT page; the portal URL itself could not be read. |

## What was and was not verified

- **Read on the agency's own site:** TCEQ, MLGW (portal page and 2021 policy; the newer mlgw.com/publicrecords page did not load), TVA, CPS Energy, City of Santa Clara (page read, but the portal link target was not readable), OPPD, Grant PUD, Chelan PUD, Virginia DEQ, PUCT (page read, but the JustFOIA link target was not readable).
- **Decoded from obfuscated email links on the agency's page:** FOIA@tva.gov, open_records@cpsenergy.com, lyndsey.files@chelanpud.org.
- **No records-request channel found on the agency's site:** NPPD (read nppd.com/public-documents), LES (read les.com/legal-notice), Northern Wasco County PUD (no agency website found).
- **SRP:** the form page exists, but its content renders in the browser only; no email or postal address for records was found.
- **Addresses in `public_power_notes.md` that the agencies' sites do not support,** so they are not used: CPS "openrecords@cpsenergy.com", OPPD "444 S. 16th St Mall", LES "1040 O St", Grant PUD "publicrecords@grantpud.org / P.O. Box 878 Ephrata", SRP "1500 N. Mill Ave", TVA "WT 7D".
- **Deadlines** are from the statutes cited (statute text was not re-read in this session); where an agency page states one, it agrees.

## After filing

Record `date_filed` and `due_date` for each in `review/RECORDS_REQUESTS.csv` (this package does not modify the repository).
