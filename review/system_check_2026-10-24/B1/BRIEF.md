# Reviewer B: figures and links re-read against their documents

Read COMMON.md first.

## Your sample
- Figures: figures_1.csv (a random sample of rows from measurements.csv that no earlier check covered; sorted so rows from one document sit together).
- Links: edges_1.csv (rows from the chain table: "from <relation> to", with the document and the line that should state it).

For more context on a figure, the full row is in data/climate_trace_seed/measurements.csv (by measurement_id); `feed` names the source table it was built from (in the repository), and registry rows (feed `registry/...`) come from the entry `entry_id` in registry/*.json, whose `record` or `claim` text (column `side`) holds the figure. Site details are in site_register.csv.

## For each figure
Fetch `source_url` and find the figure. Decide:
- `found`: the document states this value (or `value_as_published` verbatim), for this subject (site, unit, company, party), this period and this unit;
- `found_different`: say exactly what differs (value, period, unit, subject, a total presented as a part, net vs gross, a target presented as an outcome, a forecast presented as actual, a different year);
- `not_in_document`; `unreachable` (say how it failed; try once more, and search for the document's current location before giving up).
Also judge the `basis` and `side`: is the document's author a record holder (record) or the company itself / the press (claim)? Is `qualifier` right (a bound read as exact, "up to" read as a value)? For `found`, quote the line.

## For each link
Fetch `document_url`; confirm the document names this supplier/party supplying or serving this site or plant as the row says, that the site id is the site the document means, that a planned link is marked planned in `notes`, and that `quoted_line` occurs in the document (verbatim or nearly; say which).

## Output
B1/result.csv with columns: kind (figure or link), id (measurement_id or edge_id), verdict, quoted_from_document, problems, severity, notes. Then B1/report.md: counts by verdict, every problem, and any pattern (e.g. one feed or one document type going wrong). Group rows by document so each document is fetched once.
