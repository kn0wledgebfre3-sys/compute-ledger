# Brief: independent check of the browser-fetch changes (24 October 2026)

You did not do this work. Check the changes applied today against the documents and report errors; do not edit the repository.

1. Virginia: registrations 71804, 73370, 73670 and 73717 in `data/climate_trace_seed/va_permits_resolved.csv` (unit count, standby MW, permit date) against the later permits, and the dates of 74156, 74190 and 74265 against their files; the statewide sums.
2. The registry entries changed today: every number taken from today's documents, against the document; whether each fact is on the right side (record: a regulator, court, registry, grid operator, statistics office, auditor or government decision; claim: what a company, applicant or government says or plans); the tone (no adjectives in the gap, no accusation).
3. The new measurement rows for those entries: value, unit, period, basis, side.
4. Benchmarking: a random sample of 12 of the rows added for California and Portland, against the spreadsheets, and whether the kinds the builder assigned look right.
5. The outward text (brief, READMEs, package notes, themes, standards note, emails): any count or statement about the changed entries that no longer matches the data.

Output: `check_result.csv` (file, location, what is wrong, evidence, suggested fix, severity: error, inconsistency or weak). The `resolution` column was added when the findings were applied.
