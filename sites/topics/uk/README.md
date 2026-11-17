# United Kingdom: sites and figures from records read twice

`sites.csv` lists the 67 UK sites the ledger holds records for: installations with an Environment Agency or Natural Resources Wales permit for their standby generators, and sites of planning decisions (appeals, committee decisions, directions). Each row names the operator, permit holder or applicant as the document names it, the nation (England, Wales, Scotland) and the place. No site is placed on the map yet: the documents give addresses and grid references, which the ledger has not converted.

`figures.csv` holds the 322 figures from the UK round of 17 November 2026: each was read by two readers independently and the two agree (`review/uk_round_2026-11-17/`). Each row carries the document, the line it was read from (`quoted_line`), and `side`: record, or claim for an applicant's, a company's or a government announcement's figure. The entries that describe them are the seven `uk-` entries added on that date in `registry/europe.json`.

How to read them:

- `permitted_generation_thermal_input` is the aggregate rated thermal input of the standby generators (fuel in, MWth), not electrical output or IT load;
- `duration_other` rows are permit limits on hours of emergency running or testing, per installation, generator or stack as the detail says;
- `forecast_demand`, `requested_capacity` and `contracted_capacity` at national level are NESO's and Ofgem's estimates and queue data, not metered demand.
