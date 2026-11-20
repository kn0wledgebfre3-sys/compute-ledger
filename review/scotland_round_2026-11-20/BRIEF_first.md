# Brief: Scotland's large datacentre proposals and the Scottish Government's decisions on them

You are a reader for a public ledger built only from public documents. It keeps records (planning registers, council and appeal decisions, government directions, parliament's record, regulators' permits) apart from claims (what applicants, companies and campaigners say). It already holds one Scottish site (South Gyle, Edinburgh). Your job is to find and read the official records of Scotland's large datacentre proposals since 2023, and of the Scottish Government's decisions about them.

**1. The government's decisions.** Find the official documents (Scottish Government, Scottish Parliament) for:
- the requirement, announced in August 2026, that planning authorities notify Scottish Ministers of applications for datacentres above 50 MW (the instrument's name, its date, what it requires, the threshold, how long it lasts);
- the September 2026 pause or delay on decisions for large or hyperscale datacentres (what was decided, by whom, the vote or instrument, how long it lasts, what it applies to);
- any list the government or parliament publishes of the applications concerned.
Use the government's or parliament's own pages (gov.scot, parliament.scot, the official report, a chief planner letter, a direction). News reports may lead you to them but are not the source.

**2. The proposals.** For each proposal for a datacentre in Scotland of about 50 MW or more (start with Chapelcross near Annan by CX Tech in Dumfries and Galloway; Auchtertool in Fife; Wester Hermiston in Edinburgh; and any others the official documents name), find its official records: the council's planning register entry, committee reports, decision notices, the Planning Inspectorate's Scottish equivalent (DPEA) case pages, Scottish Ministers' call-in or EIA screening decisions, SEPA permits. For each, copy:
- site name and address or location as printed; grid reference or easting and northing if given (planning registers in Scotland often print them);
- applicant, as a company name (never record a private person's name);
- planning authority and application or case reference; date lodged; current status and decision date;
- capacity in MW, site area, floor area, investment, jobs, and who states each (an applicant's statement is a claim, even when a council report repeats it);
- power or water arrangements the documents state.

Copy each value exactly as printed, with the document's URL, the page or section, and a quote of at most 25 words containing it. If a document cannot be opened, say so and move on. Prefer the official site's own pages.

Write `first_reading.csv` in your folder with Python's csv module, columns:
`item_id, subject, field, value_as_written, unit, url, page, short_quote, kind_of_document, notes`
where `subject` is the site (or "government decision"), `field` is what the value is (status, capacity, applicant, grid_reference, address, area, investment, decision_date, instrument, threshold, ...), and `kind_of_document` is one of: council, appeal, government, parliament, regulator, applicant_document, press. Number the items S001, S002, ...

Neutral wording throughout; describe, do not judge. Do not name software or tools in your notes. Then reply with a short summary of what you found and what you could not open.
