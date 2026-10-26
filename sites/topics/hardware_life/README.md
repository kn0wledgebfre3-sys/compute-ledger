# Hardware life and end of life

How long servers are kept, and where they go.

**The record.** The hyperscalers' 10-K and 10-Q notes on the useful life of servers and network equipment (accounting estimates, stated by the company: claims), R2v3 and e-Stewards certified-facility lists, Eurostat WEEE data, Basel Convention national reports.

**Figures here.** `hardware_lifetime` (years, with the asset class and the effective date in `metric_detail`), depreciation effects (`other`, money), certified-facility counts (`count_other`). Links from a company to a named recycler go to `sites/chain/edges.csv` as `receives_end_of_life_from`.

**Status.** The useful-life changes are written in the entry `us-hyperscaler-server-lifespan-circularity`; the exact 10-K quotes are to be transcribed here (`review/INTAKE.csv`).

## How rows enter

`pipeline/build_measurements.py` reads every folder in `sites/topics/`: `sites.csv` rows join the site register with their `kind`, and `figures.csv` rows become measurements. Columns, vocabulary and rules are those of `sites/topics/crypto/` (see `CONTRIBUTING.md`): `value_as_published` must appear inside `quoted_line` exactly; `basis` `company_statement` makes the row a claim; every row needs the document's URL. Links between parties (who supplies whom) go in `sites/chain/edges.csv`, not here. A row added here is a first reading until `second_read` is `yes`.
