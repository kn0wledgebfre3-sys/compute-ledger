# Independent check of the Compute Ledger's measurements table

You have not seen how this table was built. Your job is to try to break it.

Table: data/climate_trace_seed/measurements.csv (one row per figure). Each row has the figure as published (`value_as_published`), its parsed `value` and `unit`, the converted `value_canonical` and `canonical_unit`, `metric`, `period_start/end`, `basis`, `side` (record or claim), and the `source_url` it should be found in. Vocabulary: pipeline/measurement_vocab.json. Registry entries: registry/*.json.

Sample file: review/measurements_check_2026-10-23/sample.csv (rows chosen at random, stratified by feed). For each sampled row:
1. Fetch `source_url` with WebFetch (the shell has no internet) and look for the figure. Use a prompt that asks for the exact sentence or table cell containing the number. If the page is long, use offset.
2. Decide: `found` (the document states this value for this subject, metric and period), `found_different` (the document states a different value, or for a different period, subject or unit: say what), `not_in_document` (the document is reachable but the figure is not in it), `unreachable` (fetch failed; say how).
3. Check the row's own logic: is `value` the number in `value_as_published` with multipliers applied? Is the unit right? Is `value_canonical` the right conversion? Is `basis` right for who produced the document (regulator, utility, company, press)? Is `side` right?

Write review/measurements_check_2026-10-23/result.csv with columns:
measurement_id, verdict, quoted_from_document, logic_problems, notes
and review/measurements_check_2026-10-23/report.md: counts by verdict, every problem found, and any pattern (a feed or a basis that is systematically wrong). Be specific and unsparing; an honest "found" is as useful as a problem.

Do not modify anything under /home/claude/repo. Budget about 90 tool calls.
