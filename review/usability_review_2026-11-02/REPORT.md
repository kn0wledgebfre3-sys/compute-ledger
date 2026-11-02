# Fresh-eyes usability review: report (2 November 2026)

As written by the reviewer, except that a local file path was replaced. The brief is in `BRIEF.md`; each finding and what was done about it is in `check_result.csv`.

---

I walked each persona's path, ran `rebuild.sh` and `ci_local.sh` in a temp copy, and tried a one-number fix. The data is strong and the build reproduces byte for byte. What blocks use is the way in: no "this is the data", no release to cite, and contributor instructions that don't work.

## Verdict per persona

1. **Data analyst:** Can load the tables cleanly, but only after about an hour working out which file is canonical. There is no column dictionary, and the only fetch URL is on a moving branch inside a folder named after one recipient.
2. **Journalist:** Can get a sourced number from a site page. The ledger page and the brief make it hard: sources are listed per entry, not per figure, the brief links no sources, and one unit in the brief is wrong.
3. **Researcher:** Can reproduce from the transcriptions, but cannot cite a fixed version: there is no tag, DOI or changelog, and figure IDs change when a figure is corrected.
4. **Developer/volunteer:** Can fix a figure if they run Python locally. The README's steps fail CI, and adding a jurisdiction is undocumented.

## Problems, ranked

**Blockers**

1. **No "this is the data" entry point.** `README.md` never names `measurements.csv`, `site_register.csv` or `data/chain/edges.csv`. It calls `registry/` "the dataset", while `data/README.md` calls `data/climate_trace_seed/measurements.csv` the core. Twenty files are byte-identical copies under different names: `sites/metered/benchmarking_transcribed.csv` is `data/climate_trace_seed/benchmarking_datacenters.csv`, `review/hostile_review.md` is `review_of_this_handover.md`, and so on. There are also two unlocated backlogs (333 vs 198 rows) and five site lists, none explained. *Fix:* put a "Get the data" section at the top of the README listing 4–5 canonical files with row counts. Move them to `data/` with neutral names, build the handover as a bundle, and delete the duplicates.

2. **No column dictionary for the main tables.** The columns of `measurements.csv` are one paragraph at line 320 of `pipeline/README.md`, under a "Permit-extraction pipeline" title. `site_register.csv`, `entity_register.csv`, `checks.csv` and `findings.csv` have none. `site_register.status` mixes an enum with free text (`"185613: under review"`). The `_about` of `measurement_vocab.json` points to `data/measurements.csv` and a `unit_as_published` column, and neither exists. *Fix:* a `datapackage.json` (or `DICTIONARY.md`) with types and allowed values, validated in CI. `sites/chain/README.md` is the model to copy.

3. **Nothing to cite.** There are no git tags or releases. `CITATION.cff` says `1.0.0`, which maps to no commit, and the data changed after the "Final counts" commit. The author is "Compute Ledger contributors", with no `date-released` and no DOI. There is no "How to cite" section in the README and no CHANGELOG. Figure IDs don't survive corrections either: correcting one figure turned `m-3f842bdd95` into `m-2a764b3988`. Retired site IDs have an alias table; retired figure IDs have none. *Fix:* follow `RELEASING.md` now; add a CHANGELOG and a citation section that falls back to the commit hash; keep figure IDs stable or add `measurement_id_aliases.csv`.

4. **The README's contribution steps fail.** Editing only `registry/` text, as README step 1 says, fails validation (`'1,991 GWh' not found verbatim`). The real path also needs `sites/measurements_from_registry/rows_europe.csv` plus `rebuild.sh`, which changed 8 files: two 1 MB HTML copies (`docs/index.html` and `site/index.html`), `measurements.csv`, `findings.csv` and `checks.csv`. CI rejects any PR whose `docs/` is stale, so an edit made in the web UI can never pass. `ci_local.sh` claims to run "the same checks as CI" but only prints a note for a stale `docs/`, and passes. *Fix:* have CI rebuild generated files on merge. Until then, correct the README steps and make `ci_local.sh` fail the way CI does.

5. **A journalist can't trace a number to its source from the main pages.** The ledger page lists sources per entry, not per figure: a median of 2 and up to 14 per entry, with 28 entries above 5. `build_page.py` never reads `measurements.csv`. `docs/brief.html` has about 40 figures and 4 links, none of them to sources, and it is written to Climate TRACE ("You estimate…") rather than to a general reader. The source files keep `page_or_table`, `page_or_section` and `quoted_line`, but `measurements.csv` drops them, so the page sometimes survives only in free-text `notes`. *Fix:* render each entry's figures as a small table with source and page per figure, add `locator` and `quoted_line` columns, and link the brief's numbers.

**Serious**

6. **Wrong unit in the prose.** NEI NOx figures are US short tons but are written as "t": in the brief ("77.6 t", "28.8 t"), in `data/climate_trace_seed/README.md` ("393 t NOx") and in the `registry/north_america.json` entry. The table converts correctly (393.3 short tons = 356.8 t), so anyone copying the text is about 10% off. *Fix:* correct the text, and add a check that numbers quoted in prose match the table.

7. **Adding a jurisdiction is undocumented.** The working route is `sites/topics/<name>/sites.csv` + `figures.csv` (Singapore did this), but `JURISDICTION_TEMPLATE.md` never mentions it. `sites/topics/singapore/README.md` says "columns as in `sites/topics/crypto/` (see CONTRIBUTING.md)"; `crypto/` has no README, and CONTRIBUTING never mentions `topics/`. Any other new source has to be coded into the 62 KB `build_measurements.py`, where every source is hard-coded. The template lists 3 build steps instead of `rebuild.sh` and still says "Singapore … next". The site-ID format is documented only in `fabs/README.md`, and `review/JURISDICTIONS.csv` is linked only from ROADMAP. *Fix:* document the topic-folder format in one place and point the template to it.

8. **Folder names mislead.** `site/` holds the page builder, `sites/` the hand-edited source data, and `docs/sites/` the generated pages. `pipeline/` is described as "Virginia and Texas permit extraction" but holds all the central builders. The README's `sites/` row omits `topics/`, `paper/`, `chain/` and `measurements_from_registry/`, which are exactly where figures are edited. Method notes are spread over four places, and `review/` is load-bearing: a pipeline test reads `review/va_reread/va_resolved.csv`. *Fix:* rename the folders and make the README table match what exists.

9. **Stale or orphaned files.**
   - `RUN_TODAY.md` is linked from nowhere. It is a 21 Oct run sheet with steps to email a named person and `git branch -M main`.
   - `ROADMAP.md` is framed around "emails go out on Monday 26 October".
   - `scrapers/README.md` says "No script has yet been run against a live source", but the weekly pulls ran on 2026-10-26.
   - `data/README.md` promises `data/YYYY-MM/` folders, and none exist.
   - `pipeline/README.md` says the fixture run "passes tonight" and refers to `registry/seed_sites.json`, which doesn't exist.
   - `scrapers/estimate_sites.py` still writes the withdrawn `worked_example_estimates.json`.

   *Fix:* delete these, or move them to `history/`.

10. **Meaning is buried in free text, which blocks analysis.**
    - 620 of the 2,984 rows (21%) use catch-all metrics (`other`, `share_other`, `count_other`, `duration_other`).
    - 44 money rows give the currency only in prose (`other_currency`).
    - 786 rows have no period and 833 no `source_date`.
    - 51% of rows have subject_type `entry`. Their country exists only in the registry JSON, as free-text names (`"United States; Netherlands; France"`), while `site_register` uses ISO3. There is no flat entries table.

    *Fix:* add a `currency` column and `country_iso3` on every row, and export `entries.csv` and `entry_sources.csv`.

11. **Licence conflict.** 30 of the 305 rows in `datacenters_emissions_seed.csv` cite Wikipedia as "the public record that establishes the site", with `other10 = CC-BY-SA-4.0`, which is not one of the values `other10_def` allows. The README says all data is CC BY 4.0. *Fix:* flag this in the licence section, or replace those sources with records.

12. **No data on the website.** Pages serves `docs/` only. There are no download links and no "cite this" on the ledger page, only "Repository and data" pointing to the repo root. *Fix:* publish versioned CSVs under `docs/data/` and as release assets.

**Polish**

13. Smaller items:
    - There are no issue or PR templates.
    - The page says "Anyone with contributor access can submit a correction"; the README says to open a GitHub issue.
    - `registry/` mixes entry files with `guide.json`, `sources.json` and `standard.json`, and is described as "one file per region" though the files are thematic.
    - Receipts are kept by hand in both `.md` and `.json`.
    - Requirements are split across two files, and the README gives no Python version and never mentions `rebuild.sh`.

## Already good — keep as is

- **Reproducible build.** `rebuild.sh` finished in 12 s on Python 3.13 with a clean `git status`. The core builders use only the standard library, and CI byte-compares every output.
- **`measurements.csv`.** All 2,984 rows have a `source_url`. Every row keeps `value_as_published`, a canonical value with its factor in the vocabulary, `basis`, the record/claim `side` and `second_read`. `feed` tells you which file to edit. It loads cleanly in pandas, and every site ID resolves to `site_register`.
- **Controlled vocabulary.** 77 metrics, 19 bases and 88 units, each with a definition.
- **Validator messages.** Every error is precise, with the line, the ID and what is missing.
- **Site pages.** Each has a figure-by-figure table with value as published, period, document type and linked source. Retired site IDs redirect.
- **`sites/chain/README.md`.** This is the model column dictionary.
- **Documentation accuracy.** The README's headline counts match the data (202 / 2,984 / 853 / 207 / 718), and only one stale path turned up in the docs.
- **`review/BROWSER_FETCH_LIST.csv`.** With its status workflow, it is a good volunteer queue.

Nothing in the repository was changed; the test runs used a throwaway copy.
