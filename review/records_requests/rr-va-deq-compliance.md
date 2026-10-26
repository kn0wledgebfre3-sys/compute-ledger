# rr-va-deq-compliance: Virginia DEQ, generator run-hour records and compliance certifications for 20 data-center permits

Two portal submissions: the CSV names the Northern Regional Office, but 4 of the 20 permits are in Mecklenburg and Henrico counties. DEQ's page says to file with the regional office that oversees each facility, and the repository's DEQ permit table (`data/climate_trace_seed/va_permits.csv`) lists those four under Piedmont. DEQ's page does not name Mecklenburg County in its examples, so check the Piedmont department description in the portal.

| Field | Detail |
|---|---|
| Addressee | Virginia Department of Environmental Quality: Northern Regional Office (16 permits) and Piedmont Regional Office (4 permits) |
| Statute | Virginia Freedom of Information Act, Va. Code § 2.2-3700 et seq. |
| How to file | **DEQ NextRequest portal: https://vadeq.nextrequest.com/**. Set the Department field to "Northern" for request A and "Piedmont" for request B. DEQ's page: "Please submit your request to the Department/Regional Office that oversees the facility" (Northern: Fairfax, Loudoun, Prince William; Piedmont: Chesterfield, Henrico, Hanover). |
| Source page | https://www.deq.virginia.gov/news-info/freedom-of-information-act (read 2026-10-24) |
| Deadline | § 2.2-3704(B): 5 working days to provide the records, deny or partly deny with the Code section, or say they cannot be provided in time; DEQ may then take 7 more working days (§ 2.2-3704(B)(4)). |
| Requester restriction | **Virginia citizens, and representatives of newspapers and magazines circulating in Virginia or radio and TV stations broadcasting in or into Virginia** (§ 2.2-3704(A)). DEQ may require the requester's name and legal address. The filer must be a Virginia resident or qualifying media representative. A media filer should replace the first sentence of each body with "I represent [outlet], which [circulates in / broadcasts into] Virginia." |
| Fees (DEQ page) | No charge if the request takes under 30 minutes. Otherwise actual cost: non-management staff $53.29/hour, management staff $78.10/hour, $0.10/page printing, actual cost for tangible production. Statute: you may ask for a cost estimate in advance (§ 2.2-3704(F)); DEQ may require a deposit if charges are likely to exceed $200 (§ 2.2-3704(H)). The bodies ask for an estimate. |
| Scope | The permits matched to EPA emissions-inventory facilities in `sites/metered/va_generator_hours.csv` (include = yes): 20 registrations, inventory year 2023, plus 2020 for 21527, 73370 and 73670. Registration 74120 (NTT) is left out because its permit covers VA3 to VA7 and the inventory facility is VA2 (`generator_hours_notes.md`). |
| Note | Most of these are minor NSR permits that require records kept on site, so DEQ may hold hour records only where they were submitted or reviewed at inspection; the bodies ask for inspection reports as a fallback. Only 21527 is a Title V permit with an annual compliance certification. |

## A. Northern Regional Office

### Subject

Virginia FOIA request: generator hours records and compliance reports for 16 data-center air permits

### Body

To the DEQ Northern Regional Office:

[Filer: state here only what is true, e.g. "I am a Virginia citizen" or "I represent [outlet], which circulates in Virginia". If neither applies, a Virginia resident or outlet should file instead.] Under the Virginia Freedom of Information Act, Va. Code § 2.2-3704, I request electronic copies of the following records for calendar year 2023, and also 2020 for registrations 73370 and 73670:

(a) records of hours of operation for each emergency generator (monthly and 12-month rolling totals) and of fuel use, as submitted to or obtained by DEQ under the permit;
(b) any annual compliance certification or annual or semiannual report submitted under the permit;
(c) where DEQ does not hold the hour records, DEQ's inspection reports covering those years.

Registrations: 73158 (Qwest Communications, Sterling); 73160 (Cyxtera, Sterling); 73370 (DuPont Fabros, Ashburn Corporate Campus); 73670 (Digital Loudoun Pkwy Center N); 73853 (Amazon Data Services, IAD-10); 73860 (Amazon Data Services, IAD-12/15/16/76/23); 73946 (Equinix); 74049 (Amazon Data Services, IAD-50/60); 74107 (Abteen Ventures, MCC1, Manassas); 74109 (CyrusOne, Shaw Road); 74114 (CyrusOne, 21350 Pacific Blvd); 74126 (Digital Loudoun 3 and 4); 74130 (CoreSite, Reston); 74155 (Iskandar, Jamshid, Kaveh and Lohrasp Ventures, LC1 to LC3); 74162 (Vantage Data Centers); 74181 (Amazon Data Services, IAD-146/147).

If any part is withheld, please identify it and the Code section claimed, and release the rest. Please send a cost estimate before starting work. If the request is large, I am glad to narrow it, for example to items (a) and (b).

Thank you,
[Name], [email]

## B. Piedmont Regional Office

### Subject

Virginia FOIA request: generator hours records and compliance reports for 4 data-center air permits

### Body

To the DEQ Piedmont Regional Office:

[Filer: state here only what is true, e.g. "I am a Virginia citizen" or "I represent [outlet], which circulates in Virginia". If neither applies, a Virginia resident or outlet should file instead.] Under the Virginia Freedom of Information Act, Va. Code § 2.2-3704, I request electronic copies of the following records for calendar year 2023, and also 2020 for registration 21527:

(a) records of hours of operation for each emergency generator (monthly and 12-month rolling totals) and of fuel use, as submitted to or obtained by DEQ under the permit;
(b) the Title V annual compliance certification for registration 21527, and any annual or semiannual report submitted under the other permits;
(c) where DEQ does not hold the hour records, DEQ's inspection reports covering those years.

Registrations: 21527 (Microsoft Corporation, East Coast Data Center, 101 Herbert Drive, Boydton); 51232 (Quality Investment Properties Richmond, LLC, 6000 Technology Boulevard, Sandston); 52820 (Microsoft Corporation, LVL Datacenter, 960 Prison Road, Boydton); 52903 (Microsoft Corporation, Timber Datacenter, 608 Ridge Road, Boydton).

If any part is withheld, please identify it and the Code section claimed, and release the rest. Please send a cost estimate before starting work. If the request is large, I am glad to narrow it, for example to items (a) and (b).

Thank you,
[Name], [email]
