# Fabs

Chip fabrication plants as sites (`kind` `fab`), with their water, power and permits.

**The record.** Taiwan Water Resources Agency bulletins and Science Park Bureau water allocations; Arizona Department of Water Resources and City of Phoenix records for TSMC Arizona; Korean Ministry of Environment data for Samsung and SK Hynix; US CHIPS environmental assessments; the companies' own water and energy disclosures (claims unless assured).

**Figures here.** `water_withdrawn`, `water_consumed`, `water_allocation`, `electricity_consumed` per fab and period. The fab-to-buyer links (from Nvidia's 10-K and TSMC's 20-F) go to `sites/chain/edges.csv` as `fabricates_for`.

**Site ids.** `<iso3-lowercase>-fab-<operator>-<site>`.

**Status.** Three fabs are in ledger entries (TSMC Hsinchu, TSMC Phoenix, Samsung); their figures move here as they are re-read.

## How rows enter

`pipeline/build_measurements.py` reads every folder in `sites/topics/`: `sites.csv` rows join the site register with their `kind`, and `figures.csv` rows become measurements. Columns, vocabulary and rules are those of `sites/topics/crypto/` (see `CONTRIBUTING.md`): `value_as_published` must appear inside `quoted_line` exactly; `basis` `company_statement` makes the row a claim; every row needs the document's URL. Links between parties (who supplies whom) go in `sites/chain/edges.csv`, not here. A row added here is a first reading until `second_read` is `yes`.
