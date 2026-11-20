# Views: which figures are the same quantity

`same_quantity.csv` lists pairs of figures in which a record and a claim state **the same quantity** about the same subject: the same thing measured, though not always for the same period. The page `records-and-claims.html` shows them first, above the full list of subjects where both sides give the same kind of figure.

The pairs are chosen by hand. Most records and claims that share a subject and a kind of figure measure different things (several different shares, or a plant's whole capacity beside one phase), so the list is short and each pair says what both figures describe.

Columns: `record_id` and `claim_id` (`measurement_id` in `data/climate_trace_seed/measurements.csv`; a corrected figure is followed through `measurement_id_aliases.csv`), `both_describe` (what the two figures measure, in plain words) and `note` (a difference in period or scope the reader should know). The build stops if an id is missing, if the two figures are not about the same subject and metric, or if the sides are not a record (or a figure computed from records) and a claim.

The ledger does not say which figure is right. Each links to its document.
