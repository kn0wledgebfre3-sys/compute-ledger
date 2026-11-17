# Brief: the UK's public records on datacenters (common part)

You are a reader for a public ledger of what AI computing uses and emits, built only from public documents. It keeps **records** (documents from regulators, planning authorities and inspectors, courts, grid and system operators, utilities' statutory filings, statistics offices, auditors, Parliament's committees) apart from **claims** (what companies, industry bodies and government ministers say in announcements). Both are recorded, labelled. Every figure needs a URL to the document that states it.

The ledger already holds, for the UK: the Secretary of State's decision on the Abbots Langley (Bedmond Road) appeal, Hertsmere's outline permission for DC01UK at South Mimms, NESO's Demand Call for Input summary (March 2026), and Affinity Water's written evidence to Parliament (DCU0083). Do not redo those.

For each document, record each figure it states with the page, paragraph or table and a short verbatim quote (at most 15 words). Say exactly what a figure counts (for example operational jobs at the site versus jobs claimed for construction; rated thermal input versus electrical capacity; requested versus contracted grid capacity). If something is not stated, write "not stated"; do not compute or estimate. Neutral wording: no adjectives about companies, councils or the government. A news article may lead you to a document but is not the source, unless no official document exists, and then label it press.

The direct download of government sites is blocked from your environment; read documents through a text-extraction service, asking for the exact sentences and table rows that state each figure, with page numbers.

Write your result with Python's csv module, one row per figure, columns:
`topic, subject, site_name, operator_or_applicant, local_authority_or_area, document_title, publisher, document_date, url, side (record|claim), figure, value_as_published, unit, period, page_or_table, short_quote, notes`

where `figure` is a short label (for example rated_thermal_input, generator_count, it_capacity, grid_capacity_requested, floor_area, site_area, jobs_operational, jobs_construction, water_use, electricity_use, pue, investment, public_money, decision, decision_date, permit_reference, housing_delayed). Then reply with a short summary: what you found, the headline figures, and what you looked for and did not find.
