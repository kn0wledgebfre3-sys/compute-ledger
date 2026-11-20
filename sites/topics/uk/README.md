# United Kingdom: sites and figures from records read twice

`sites.csv` lists the 72 UK sites the ledger holds records for: installations with an Environment Agency or Natural Resources Wales permit for their standby generators, and sites of planning decisions and applications (appeals, committee decisions, directions, and five Scottish proposals added on 20 November 2026). Each row names the operator, permit holder or applicant as the document names it, the nation (England, Wales, Scotland) and the place. 46 sites are placed on the map, each from a grid reference or an easting and northing that two readers copied from its documents, converted with `pipeline/osgb.py` (`review/uk_locations_2026-11-17/`, `review/site_locations_2_2026-11-17/`, `review/scotland_round_2026-11-20/`). The other 26 have only an address, a place, or nothing; each site's notes say which.

`figures.csv` holds 339 figures. The 322 from the UK round of 17 November 2026 were each read by two readers independently and the two agree (`review/uk_round_2026-11-17/`). Each row carries the document, the line it was read from (`quoted_line`), and `side`: record, or claim for an applicant's, a company's or a government announcement's figure. The entries that describe them are the seven `uk-` entries added on that date in `registry/europe.json`. The 17 figures for the Scottish proposals, read twice on 20 November 2026 (`review/scotland_round_2026-11-20/`), belong to the entry `uk-scotland-datacentre-directions-2026`; most are applicants' figures and so claims.

How to read them:

- `permitted_generation_thermal_input` is the aggregate rated thermal input of the standby generators (fuel in, MWth), not electrical output or IT load;
- `duration_other` rows are permit limits on hours of emergency running or testing, per installation, generator or stack as the detail says;
- `forecast_demand`, `requested_capacity` and `contracted_capacity` at national level are NESO's and Ofgem's estimates and queue data, not metered demand.
