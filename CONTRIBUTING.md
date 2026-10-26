# Contributing

## Where help matters most

In order:

1. **Fetch the originals.** Entries with `verification_status: not_found` or `partial` (counts on the ledger page); most are in Johor, India, Korea, Taiwan and China's western hubs, where the government document exists but is not online in a form a script can reach. `review/BROWSER_FETCH_LIST.csv` lists every document that needs a person with a browser, with what it should contain; take a row, set its `status` (`obtained`, `partial`, `contradicts` where the document contradicts the entry, `not_obtained`, or `blocked` where only a records request will do) with `status_date` and a one-line `result`, and open a PR with the document or a stable link.
2. **Review the weekly pull request.** Every Monday a workflow pulls the sources that have an API and checks the watched pages, and opens a pull request with anything new (`data/pulls/<date>/SUMMARY.md`). Nothing in it enters the ledger until a person has read each item against its document. This is the most useful hour anyone can give the ledger.
3. **A new jurisdiction.** Follow `JURISDICTION_TEMPLATE.md`. Singapore, Johor and Amsterdam are next; Vietnam, Thailand, the Philippines, Colombia, Poland and Switzerland have no entries at all.
4. **Receipts.** Candidates with the documents half-gathered: Chesterfield (Virginia gas peaker), Memphis (xAI turbines and TVA's load memo), Johor (water rejections), Aragón (Amazon approvals against regional consumption). Follow the structure of an existing receipt exactly.
5. **Read it as an expert.** A grid engineer, a water-rights lawyer, a journalist who has filed records requests. Open an issue for anything wrong, overstated, or missing a known document.

## How a figure enters the ledger

Every number the ledger holds ends up as one row of `data/climate_trace_seed/measurements.csv`, built by `pipeline/build_measurements.py` from these places and nowhere else:

| Where the figure is written | What it is |
|---|---|
| `registry/*.json`, in an entry's `record` or `claim` | The sentence a reader sees. Its figures are lifted into `sites/measurements_from_registry/rows_<file>.csv`, one row per figure. |
| `sites/metered/*_transcribed.csv` | Transcriptions of regulator and utility documents (Irish annual environmental reports, EPA's emissions inventory, benchmarking portals, utility filings), one row per document line, with its URL. |
| `sites/metered/filed_figures_curated.csv` | The mapping of multi-figure utility rows to the vocabulary, each `value_as_published` checked against the quoted line. |
| `data/climate_trace_seed/va_permits_resolved.csv`, `tx_issued_sites.csv`, `sites/*_sites.json` | Permit and licence figures in the site lists. |

`value_as_published` is the figure exactly as it is written in the text it was taken from: the document's line or cell for transcriptions, the entry's own sentence for figures from the registry (which paraphrases the document, so the link is what to check it against). `qualifier` records "at least", "up to", "about" and the like.

Each row uses the controlled vocabulary in `pipeline/measurement_vocab.json`: a `metric`, a `unit` and a `basis` from its lists. Units convert to one canonical unit per dimension through `pipeline/units.py`, with the factor stated in the vocabulary; money, ratios and intensities are kept as published. To add a metric, unit or basis, edit the vocabulary in the same PR and say why.

`pipeline/validate_measurements.py` runs on every push. It rejects a row whose metric, unit or basis is not in the vocabulary, whose unit does not fit its metric, whose canonical value is not what `units.py` gives, whose period is malformed, whose subject is not in `site_register.csv`, `entity_register.csv` or the registry, and, for figures from the registry, whose `value_as_published` does not occur verbatim in the entry's text or whose source is not one of the entry's sources. Every builder must also reproduce its committed output byte for byte.

## The two-reading rule

A figure extracted by a script, or transcribed once by hand, is a first reading. Before it is published as a record it is read a second time against the document by a different method or a different person, and every disagreement is resolved against the text. The second reading checks what the figure is attached to as well as the figure: which site, which unit, which company, and whether a figure for several plants or sites has been put on one. This is the rule that found the Virginia parser bug (19,186 MW first reading, 33,693 MW resolved). In the measurements table, `second_read` says whether it has been done for that figure. The weekly pulls produce first readings only.

## Rules

- A record needs a URL to the document. A press report of a document is medium confidence and says so; a press report of what a company or government says is that party's claim.
- `confidence` on an entry says how firmly its `record` rests on record holders' documents that were read: `high` only then; `medium` where it rests on press reports of records or on documents only partly read; `low` where it rests mainly on press, NGO or company material. An entry whose content is a company's own statements carries at most `medium`, whatever the care of the transcription. `verification_status` says whether a second reading against the primary documents was done: `verified`, `partial` or `not_found`; every entry has one.
- A peer-reviewed study's own measurements (basis `peer_reviewed_study`) and an NGO's documented findings (basis `ngo_report`) are kept on the record side with that basis, so they can be told apart from regulators' records and filtered out; their authors' opinions are not.
- A company's statement is a claim, wherever it was published, including SEC filings' narrative; a regulator's, court's, grid operator's, statistics office's, auditor's, registry's or customs authority's document is a record. A company figure that an independent auditor's assurance statement covers is a record with basis `assured_disclosure`, because the auditor's statement is the record; give the level (limited or reasonable) in notes. A public utility's own published figure has basis `utility_published`.
- Quote at most a short phrase; paraphrase the rest.
- No adjectives in `gap`. No accusations anywhere. If a company responded in good faith, that response is part of the record.
- Never remove an entry. If a record is superseded, add the newer document and update the entry; the older figure stays in the measurements table with its period.
- Never change or reuse an `id`: entry ids, site ids in `site_register.csv`, entity ids in `sites/entity_register.csv`. If two site ids turn out to be one site, keep one and retire the other in `RETIRED_SITE_IDS` (`pipeline/build_measurements.py`); the builder lists every retired id with the id kept in `data/climate_trace_seed/site_id_aliases.csv`, and the retired id's page sends readers to the site's page. A measurement id is a hash of the row's content, so it changes only when the figure or its source does.
- Corrections are newer documents, not rewrites. The review files in `review/` and `data/climate_trace_seed/review_*.md` stay as they were written.
- Every check is recorded. Put the brief and the findings file in a new folder under `review/`, add a row to `review/CHECKS.csv`, and add the findings file to `pipeline/build_checks.py`; the build lists every finding in `data/climate_trace_seed/findings.csv` with what the data show now, and the ledger page shows the check under How it is checked. A check that finds nothing wrong is recorded too.
- Set `last_checked` on every entry you touch, and rebuild everything with `./rebuild.sh` (it runs the builders in order and then the same checks as CI).
- When a roadmap item is done, strike it through in `ROADMAP.md` with the date and the entry ids it produced; do not delete it.
