# Independent check of new figures and chain links in the Compute Ledger

You have not seen how these rows were built. Your job is to try to break them.

1. Figures: review/measurements_check_2026-10-24/sample_figures.csv holds 15 rows drawn at random from figures added today (chip, server and cloud companies' conflict-minerals reports; foundry customers and fabs from annual filings). Each row has the figure as published (`value_as_published`), its parsed `value` and `unit`, the converted `value_canonical`, `metric`, `qualifier`, `period_start/end`, `basis`, `side` (record or claim), and the `source_url` it should be found in. Vocabulary: pipeline/measurement_vocab.json. Rules: CONTRIBUTING.md (a company's statement is a claim wherever published; a regulator's, court's, grid operator's, statistics office's, auditor's or registry's document is a record; a press report of a document is basis press_report).
2. Chain links: review/measurements_check_2026-10-24/sample_links.csv holds 16 links drawn at random (smelter to company; foundry, memory, packaging and assembly to buyer) ("from relation to"), each with the document and the phrase (`quoted_line`) that should state it. Relations are defined under `relations` in the vocabulary.

For each figure and each link:
- Fetch `source_url` / `document_url` with WebFetch (the shell has no internet) and look for the figure or phrase. Ask for the exact sentence or table cell. If the page is long, use the `offset` parameter.
- Decide: `found` (the document states this value for this subject, metric and period, or states this link), `found_different` (say what differs), `not_in_document` (reachable, absent), `unreachable` (say how).
- Check the row's logic: is `value` the number in `value_as_published` with multipliers applied? unit right? `value_canonical` right? `qualifier` right ("at least", "up to", "about")? period right (fiscal years, as-of dates)? `basis` and `side` right for who produced the document? For a link: is the relation the right one, and are both parties the ones the document names?

Write review/measurements_check_2026-10-24/result.csv with columns: row_type (figure or link), id (measurement_id or edge_id), verdict, quoted_from_document, logic_problems, notes; and report.md: counts by verdict, every problem, and any pattern. Be specific and unsparing; an honest "found" is as useful as a problem. Today is 2026-10-24; do not write a later date.

Do not modify the repository. Budget about 50 tool calls. Also check that each smelter link's smelter appears in that company's list for the metal stated, and that each figure is attached to the right company and year.
