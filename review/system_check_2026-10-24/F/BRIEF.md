# Final reviewer: does the outward text still match the corrected ledger?

Read COMMON.md first (ignore its line about the package drafts: you may read them).

Today the ledger's registry entries were corrected after an independent check: many company statements, government announcements and press figures were moved from `record` to `claim`; some entries now say "No record found yet"; statuses and confidence changed; several facts were corrected (e.g. Virginia's large-load rate class comes from the biennial review order PUR-2025-00058, not the Chesterfield order; Korea's 162 is 176; the Matheson PDF is a law firm's briefing, not the CRU decision; Middenmeer's water volumes are Microsoft's figures; TNB's 405 MW is TNB's figure relayed by ISEAS). The texts below were written before or during those corrections.

## Texts to check
1. registry/guide.json (the themes on the ledger page: every `why`, `ask` and headline reference)
2. registry/standard.json
3. site/brief.html
4. README.md and data/climate_trace_seed/README.md
5. (package drafts)/email_drafts.md and (package drafts)/other_emails.md
6. data/climate_trace_seed/METERED.md, VIRGINIA.md, ireland_regional_check.md (skim for statements about entries)

## Against
The corrected registry (registry/*.json: `record`, `claim`, `gap`, `verification_status`, `confidence`), data/climate_trace_seed/measurements.csv (`side`, `basis`), sites/dedicated_supply.csv.

## What to find
For every sentence that states a fact about an entry, a site, a company or a figure:
- does the corrected entry still support it the same way? Flag any fact now in `claim` that the text presents as a record or a finding ("the regulator found", "records show", "is", without "X says"); any figure from an entry now `not_found`/"No record found yet" that the text presents as documented; any figure the entries no longer contain or now give differently; any guide headline entry whose entry no longer shows what the headline says.
- Give the exact replacement wording (short, neutral, same length or shorter), using the entry's own corrected wording where possible.
- Ignore total counts (entries, documents, figures, sites); they are updated last.

## Output
F/result.csv with columns: file, location (key path or paragraph), quoted_text, problem, entry_id, replacement. Report: counts and every row. Use python to load the JSON and grep.
