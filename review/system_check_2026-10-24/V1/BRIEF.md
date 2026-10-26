# Verification pass: entries never re-read against their primary documents

Read COMMON.md first.

Your entries are listed in V1/entries.txt (registry file and entry id, one per line; the files are under registry/). None of them has ever had a recorded second reading. Do that reading now.

For each entry:
1. Read its `record` text and list every specific fact in it: each number with its unit and period, each date, each named body, decision, document number or site.
2. Fetch each `record_sources` URL (read long documents to the end). If one fails, retry once and search for the document's current location (same publisher). For each fact, decide: confirmed (quote the line), different (quote what the document says), or not in the documents read.
3. Check that every record source is a record holder (COMMON.md), and that nothing in `record` comes only from a company, press or NGO source (those belong in `claim` or need a record).
4. Glance at `claim` and `gap`: is the claim attributed, and does the gap line say only what the records show?
5. Give a status: `verified` (every fact in `record` confirmed in a record source), `partial` (some confirmed, none contradicted, some not found), `not_found` (the primary documents could not be read), or `contradicted` (a fact in `record` is wrong). Write a one-paragraph `verification_note` in the ledger's style: what was read, on what date (2026-10-24), what was confirmed, what was not, quoting the key lines briefly.

## Output
V1/result.csv with columns: entry_id, status, verification_note, problems (each fact that differs or is unsupported, with quotes), suggested_fix. Then V1/report.md with counts by status and every problem.
