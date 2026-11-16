# Note on the 2026-11-16 pull

The weekly pulls of 2 and 9 November are superseded by this one: until a pull is merged, each week compares against the same baseline, so this pull lists everything the two before it did. `SUMMARY.md` is the run's own report, kept as written. Read it with these points:

- **NEI, 1,048 rows "new to the ledger".** They are not new: they are the 71 facilities outside Virginia already added on 2026-11-02 (`sites/metered/us_nei_transcribed.csv`); the pull compared only against the Virginia file. From the next run it compares against both.
- **Irish licences not listed, 15.** Read on 2026-11-16: the profiles are EPA's licence register and settle what the reader of 2 November could not (see `review/ireland_licences_check_2026-11-02/check_result.csv`, resolutions). The seven licensed installations are now on the watch list (`scrapers/config/ie_leap_licences.json`), so their reports will be listed for reading; P1181-02 and P1186-02 are reviews already watched under their old numbers.
- **Irish reports not yet read, 3** (P1181-01 and two P1187-01 documents): not read yet.
- **Benchmarking, 9.** The nine rows left out on 2026-11-02, for the reasons in `sites/metered/benchmarking_notes.md`; the pull reports them again each week.
- **Watched pages, 1.** PJM's Load Analysis Subcommittee materials of 2 November 2026 include a review of the datacenter load forecast: not read yet.

Nothing here changes the ledger's tables until a person reads each item against its document (CONTRIBUTING.md).
