# Brief: move company statements from the record to the claim

The Compute Ledger's founding rule: a company's statement is a claim; a document from a regulator, court, grid operator, statistics office, auditor or customs authority is a record. Each entry has a `record` (what such documents say) and a `claim` (what the operator or government says), each with its own source list. A check found company figures sitting in the record of 21 entries.

Inputs (read both):
- review/sides_2026-10-23/entries_before.json: the 21 entries as they are now.
- review/sides_2026-10-23/company_in_record.csv: the 77 figures marked as company statements in the record (entry_id, value_as_published, metric_detail, source_url).

For each entry, rewrite `record` and `claim` so that:
1. Every figure listed for that entry in the CSV, with the clause that states it, moves from the record to the claim. Keep each figure's characters exactly as they are (same `value_as_published` text), and name who says it ("Fortum says...", "Samsung's sustainability report states...").
2. Everything else in the record stays word for word. Do not rephrase, shorten, or drop any other sentence or figure. If removing a clause leaves a broken sentence, make the minimum change to repair it.
3. The claim keeps everything it already says, word for word, with the moved clauses added.
4. Any source in `record_sources` that is the company's own document and now supports only the claim moves to `claim_sources` (keep its object exactly). A source that still supports something in the record stays.
5. If moving the figures changes what the `gap` sentence refers to, adjust the gap minimally so it stays true; otherwise leave it. Neutral tone, no adjectives.
6. If you judge that a listed figure is not actually a company statement (for example a regulator's document quoting it as a finding, or a statutory filing), leave it in the record and say why in your notes.

Output: review/sides_2026-10-23/entries_after.json: the same 21 entries, every field present, only record, claim, record_sources, claim_sources and gap changed. Plus notes.md listing, per entry, what moved and any figure you left in place and why.

Self-check before finishing (must pass): run
python3 -I review/sides_2026-10-23/check_sides.py
which verifies that no number was lost from record+claim, that each moved figure is now in the claim and not the record (unless you listed it in notes as left in place), and that no other field changed. Fix anything it reports. Do not modify the repository.

Note added after the rewrite: `entries_after.json` is the text applied to the registry on 2026-10-23, which includes the maintainers' adjustments described in `data/climate_trace_seed/review_5_measurements_check.md` (last section). The reviewer's own notes are `notes.md`.
