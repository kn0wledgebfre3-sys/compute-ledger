# Brief: independent check of the Irish 2023 reports (2 November 2026)

You did not do this work. Check it against the documents and report errors; change nothing in the repository.

The documents: the ten 2023 Annual Environmental Reports of Ireland's licensed datacentres, a second upload of one 2024 report (P1181-01) and two ambient air quality reports filed under P1187-01, downloaded from the EPA's LEAP system. Read the tables from the rendered pages, not only from extracted text.

1. `sites/metered/ireland_aer_transcribed.csv`: the ten new 2023 rows and the new columns `period_start`, `period_basis`, `average_load_note` (also filled for P1181-01 2024). For each 2023 row check against its PDF every value from Table 3 (Energy Used) and Table 5 (Water Used), the page numbers, the period and its quotation, and every quotation in the notes and basis columns.
2. `data/climate_trace_seed/ireland_aer_metered.csv`: the 2023 rows' electricity in MWh and average load (MWh over the hours from `period_start` to 31 December), and that the Microsoft and Equinix 2023 rows have no average.
3. The statements built on it: the Ireland section of `data/climate_trace_seed/METERED.md` (the 2023 table row and the like-for-like paragraph), the last section of `sites/metered/ireland_aer_notes.md`, and the entry `ie-epa-aer-metered-2025` in `registry/europe.json`. Recompute every number and check every quotation.
4. Whether the 2023 figures are presented fairly: anything misleading about comparing a part year with full years, or any figure attributed to the wrong licence or site.

Output: `check_result.csv` with file, location, what is wrong, evidence (quote and page), suggested fix and severity (error, inconsistency, weak), and one row per figure confirmed (severity `confirmed`). The `resolution` column was added when the findings were applied.
