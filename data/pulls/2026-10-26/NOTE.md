# Note on the 2026-10-26 pull

`SUMMARY.md` is the run's own report, kept as written. Read it with these points:

- **NEI, 2026 VA and 2029 VA** under Failures: EPA has not released the 2026 or 2029 inventories, so those views do not exist yet. The pull probes for them each week. From the next run it lists them under "Notes (not failures)".
- **NEI, 2020 GA, AZ and WA, and 2023 AZ and WA** under Failures: EPA's service returned an empty file (no rows) for these queries. From the next run they are listed as notes; whether a datacenter facility should appear there is to be checked by hand.
- **NEI, 1,132 rows new to the ledger**: 83 facilities, one row per facility, inventory year and pollutant. The ledger so far holds only Virginia's 2023 figures (172 rows); this was the pull's first run across 16 states and the 2020 and 2023 inventories.
- **Watched pages**: this was the first run, so it recorded each page's current items as the baseline (`data/watch/`); new items are reported from the next run.
- The other failures are real: Philadelphia's benchmarking service rejected the query, and Virginia DEQ's permit list and SRP's datacenter page refuse scripted access (the DEQ list is read in a browser, see `review/BROWSER_FETCH_LIST.csv`; SRP's page needs the same).

Nothing here changes the ledger's tables until a person reads each item against its document (CONTRIBUTING.md).

## Read on 2 November 2026

- **NEI, 1,132 rows.** The 84 rows for 12 Virginia facilities (pollutants beside the NOx already in the ledger) were added to `sites/metered/va_nei_transcribed.csv`; the 1,048 rows for 71 facilities in 13 other states became `sites/metered/us_nei_transcribed.csv`, with what and where each facility is in `sites/metered/us_nei_facilities.csv` (checked in `review/us_nei_identity_check_2026-11-02/`). They enter the ledger as first readings by script.
- **Benchmarking, 202 rows.** 193 added to `sites/metered/benchmarking_transcribed.csv`; the nine left out, and why, are in `sites/metered/benchmarking_notes.md` (last section).
- **Irish reports, 13 first readings.** The 2023 reports, read and checked before this (`review/ireland_2023_check_2026-11-02/`).
- **Irish licences, 15 not listed.** Checked in `review/ireland_licences_check_2026-11-02/`: four appear to be licences in force since 2023 whose reports are not read yet. Adding them to `scrapers/config/ie_leap_licences.json` needs each licence's identifier, which the next pull now records.
