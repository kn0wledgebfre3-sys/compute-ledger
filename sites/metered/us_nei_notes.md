# EPA National Emissions Inventory outside Virginia (2 November 2026)

Files: `us_nei_transcribed.csv` (the figures, one row per facility, inventory year and pollutant) and `us_nei_facilities.csv` (what and where each facility is, one row per facility). Built into the measurements table by `feed_us_nei` in `pipeline/build_measurements.py`; the entry is `us-nei-datacenter-facilities-2020-2023`. Virginia stays in `va_nei_transcribed.csv` (see `va_nei_notes.md`).

## Where the figures come from

The weekly pull of 26 October 2026 (`scrapers/pull_nei.py`, output in `data/pulls/2026-10-26/nei/`) queried EPA's Envirofacts facility-summary views for the 2020 and 2023 inventories, state by state, for facilities with NAICS code 518210 and criteria pollutants:

`https://data.epa.gov/dmapservice/nei.vw_facility_summaries_<year>/state_abbr/equals/<ST>/naics_code/equals/518210/pollutant_type/equals/CAP/1:5000/CSV`

`us_nei_transcribed.csv` is the pull's rows for the 13 states other than Virginia, unchanged: 1,048 rows, 71 facilities. Each row keeps the query it came from. These are first readings by script; nothing was re-queried, because EPA's service could not be reached from where this was done. A second reading means re-running a facility's query (or `.../eis_facility_id/equals/<id>/pollutant_type/equals/CAP/1:200/CSV`) and comparing.

- The view gives annual facility-wide totals per pollutant, in US short tons (`uom` TON). No unit, process, hours or fuel.
- The builder takes NOx, CO, VOC, SO2, PM10-PRI and PM25-PRI. It leaves out PM-CON, PM10-FIL and PM25-FIL (the condensable and filterable parts of the primary figures, so adding them would count twice) and NH3 (not in the vocabulary yet).
- The service returned an empty file for Arizona and Washington in both years and Georgia in 2020: no facility under 518210 there, not a failure. Datacenters under other codes are not found by this query (in Virginia, 4 of 27 were under other codes).

## What and where each facility is

`us_nei_facilities.csv` columns: `include` (yes for all 71: nothing found shows any is something else), `site_id`, `name` (the inventory's name with its address, or its county where the address is a mailing address), `operator` (only where a record names the holder or operator), `kind`, `locality`, `permit_or_registration`, `identity_source_url` and `identity_source_type` (record, company or press; where nothing else was found, the inventory's own classification), `identity_note`, and `second_reading` (what the reader found, in brief).

The readers' work is in `review/us_nei_identity_check_2026-11-02/`. In short:

- 31 identified from a regulator's or other public body's document (state air permits, county records, a city plan commission, a state fire marshal's tank register, EPA's facility registry for Texas), 16 from company or press material only, 24 not yet.
- Six inventory street addresses are an owner's mailing address in another state (Apple's Cupertino address for its Prineville facility; a Kennewick, Washington address for three Amazon facilities in Morrow County, Oregon; Mountain View, California for two facilities in Wasco County, Oregon). The inventory's coordinates are at the sites, so the sites are placed by them and named by county.
- Nine facilities are sites the ledger already listed: four in Texas (EPA's facility registry lists the inventory id or the same street address) and five Google sites (Storey County and Henderson, Nevada; Papillion, Nebraska; New Albany, Ohio; Berkeley County, South Carolina). Other listed sites within 2 km (Google in Council Bluffs, Lenoir, Clarksville and The Dalles) are named in the notes and kept apart until a document says they are the same.
- Three are typed as buildings that contain a datacenter: CSL Behring, King of Prussia, and 401 City Avenue, Bala Cynwyd (documents describe office buildings), and ADP, Elk Grove Village (press describes an office building; in the 2020 inventory only).
