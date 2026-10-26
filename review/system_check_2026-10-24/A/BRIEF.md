# Reviewer A: every number and factual statement in the outward-facing text

Read COMMON.md first.

## Texts to check (these are what readers and recipients will see)
1. site/brief.html (the brief; read the visible text)
2. README.md
3. data/climate_trace_seed/README.md
4. (package drafts)/email_drafts.md (emails to Climate TRACE)
5. (package drafts)/other_emails.md (eight emails to other organisations)
6. registry/guide.json (the themes on the ledger page: headline text, why it matters, what to ask)
7. sites/metered/ireland_emissions_notes.md, data/climate_trace_seed/VIRGINIA.md, data/climate_trace_seed/SINGAPORE.md

## The data to check them against
- data/climate_trace_seed/measurements.csv (every figure; `value_as_published`, `period_*`, `basis`, `side`, `source_url`, `notes`), measurements_summary.json, site_register.csv, metered_summary.json, assets_summary.json and the other CSVs in that folder
- registry/*.json (entries: `record`, `claim`, `gap`, sources)
- data/chain/edges.csv and summary.json
- sites/ (source tables), e.g. sites/metered/va_generator_hours.csv, sites/paper/company_figures.csv
- Current totals (as the build prints them today): 202 entries, 44 countries and territories, 670 distinct linked documents, 2,759 figures in measurements.csv, 767 sites in the register, 207 chain links, 71 datasets, 3 receipts. Counts that differ from these are known to be stale and will be updated in a final pass: list them in one group, but they are not the main point.

## What to do
For every number, percentage, date, count and specific factual statement in texts 1 to 7, find the row(s) in the data that support it and check:
- the number matches (allowing only honest rounding; say if rounding changes the meaning);
- the period, unit, site or party is the one the data row is attached to;
- a record is not presented as more than it is (a company figure presented as a record, a press report presented as a regulator's finding, a computed figure presented as published, a minimum presented as a measurement);
- the same fact is stated the same way everywhere it appears (e.g. permit counts, GW totals, percentages across the brief, READMEs and emails);
- nothing contradicts another entry or row.
Also flag: any first-person complaint or frustration; any claim about the sender's residency or citizenship; anything that villainises a company or person; broken or placeholder links; "[Name]" placeholders are expected and fine.

## Output
A/result.csv with columns: file, quoted_text, severity, problem, supporting_row (file and id or row), suggested_fix. Include a row for each statement you could NOT find support for (severity `weak` unless it is contradicted). Then report.md: counts by severity, the most important ten, and patterns. Prefer reading files whole and using grep/python over many small reads.
