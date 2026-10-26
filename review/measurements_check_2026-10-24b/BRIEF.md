# Independent check: water and fuel links, and generator hours

You have not seen how these rows were built. Try to break them. Today is 2026-10-24; do not write a later date. Do not modify the repository. Rules for what counts as a record or a claim: CONTRIBUTING.md.

## Part 1: 30 supply links

review/measurements_check_2026-10-24b/links.csv holds every water and fuel link in the ledger's chain table: "from <relation> to", with the document and the phrase (`quoted_line`) that should state it. For each, fetch `document_url` (read long documents to the end) and decide:
- `found` (the document states this supplier supplying this site or plant, as the row says), `found_different` (say what differs), `not_in_document`, or `unreachable` (say how).
- Is the supplier the one the document names, and is the receiving site the right one (a site id should be the site the document means, not a nearby or sister site)? Is a planned link marked planned in notes? Is the basis right for who wrote the document (regulator, utility, court, press report, company)?
For the 11 Irish rows, the document is an annual environmental report: confirm Table 5 lists a "Public Supply" row for that site and year.

## Part 2: generator hours (6 rows)

review/measurements_check_2026-10-24b/hours.csv holds 6 rows of `generator_hours` (minimum full-load-equivalent hours per generator) derived as: inventory NOx short tons x 2,000 / sum over the permit's engines of (count x NOx limit in lb/hr). The engine rows behind them are in sites/metered/va_permit_unit_rates.csv (by `registration`) and the inventory rows in sites/metered/va_nei_transcribed.csv. The permit texts are on disk: (the permit texts saved by the pipeline run) <registration>.txt. For each of the 6 registrations:
- Read the permit text yourself from scratch and list every engine group with its count and its NOx lb/hr limit (tables lost their column alignment; use the conditions to map columns to groups). Compare with va_permit_unit_rates.csv and report every difference.
- Recompute the hours. Check the inventory value against the Envirofacts URL in `source_url` if it loads.
- Is the facility in the inventory the facility the permit covers (name, address, registration)?

## Output

review/measurements_check_2026-10-24b/result.csv with columns: part (link or hours), id (edge row number in links.csv counting from 1, or registration), verdict, quoted_from_document, problems, notes. Then report.md: counts by verdict, every problem, and any pattern.
