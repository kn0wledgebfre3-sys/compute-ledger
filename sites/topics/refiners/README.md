# Smelters and refiners

Smelters and refiners named in conflict-minerals reports, as sites (`kind` `smelter_refiner`), with what each report says about them.

**The record.** SEC Form SD and the attached conflict-minerals report, filed each May by Nvidia, AMD, Intel, Dell, Supermicro, HPE, Apple, Microsoft and others, list the smelters and refiners in their supply chains for tin, tantalum, tungsten and gold, usually with the Responsible Minerals Initiative (RMI) smelter id and audit status. Cobalt and nickel are outside the statute; where a filer reports them voluntarily, say so.

**Figures here.** Per smelter: count of filers naming it (`count_other`), RMI audit status as a note. Per filer: number of smelters named (`count_other`), share conformant (`share_other`). The filer-to-smelter links go to `sites/chain/edges.csv` as `refines_for`.

**Site ids.** `<iso3-lowercase>-smelter-<rmi-id-or-slug>`. Coordinates only from a document that gives them.

**Status.** Waiting: see `review/INTAKE.csv`.

## How rows enter

`pipeline/build_measurements.py` reads every folder in `sites/topics/`: `sites.csv` rows join the site register with their `kind`, and `figures.csv` rows become measurements. Columns, vocabulary and rules are those of `sites/topics/crypto/` (see `CONTRIBUTING.md`): `value_as_published` must appear inside `quoted_line` exactly; `basis` `company_statement` makes the row a claim; every row needs the document's URL. Links between parties (who supplies whom) go in `sites/chain/edges.csv`, not here. A row added here is a first reading until `second_read` is `yes`.
