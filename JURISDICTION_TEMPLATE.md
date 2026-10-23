# Adding a jurisdiction

How Virginia, Texas and Ireland were built, written as the checklist for the next one (Singapore, Johor and Amsterdam are next). A jurisdiction counts as covered when it has the first four parts; the fifth makes it comparable.

## 1. A site list from a register, not from press

Find the public register that names datacenters: an air-permit list (Virginia DEQ), a tax-exemption register (Texas Comptroller), an industrial-emissions licence register (Ireland's EPA), a planning portal, an allocation list (Singapore's IMDA calls). Record every row, located or not. A site without a coordinate goes into `datacenters_register_backlog_unlocated.csv` with the address the document gives; it is not dropped.

Coordinates come from the document itself where it has them (Irish licence attachments carry grid references), otherwise from a geocode of the document's site address, accepted only when the geocoder matched that address (house number and street), never the permittee's mailing address.

## 2. A capacity figure per site from a permit or licence

Generator inventories, rated thermal input, connection agreements. Each figure carries its basis (`standby MWe summed from unit ratings`, `MWth rated thermal input`, `primary on-site plant`, or `MW as stated` when the document does not say), its document URL, and the measurement vocabulary's metric. If a pipeline extracts it, the pipeline's output is a first reading: read every document a second time by a different method and resolve each disagreement against the text before publishing.

## 3. A metered or filed total the sites must respect

A statistics office's metered figure (Ireland's CSO), a regulator's per-site report (Ireland's AERs), utility filings to a regulator or grid operator (Dominion and NOVEC to PJM and the SCC), a public utility's published load. The site figures are tested against it: permitted capacity is a ceiling, the metered or filed total a bound.

## 4. The records law and the requests it allows

Name the statute (Virginia FOIA, Texas Public Information Act, Ireland's Access to Information on the Environment regulations, Singapore has none of general application) and, for each document the ledger needs and cannot fetch, the request that would obtain it: addressee, statute, the document by name. Put fetchable-by-browser documents in `review/BROWSER_FETCH_LIST.csv`.

## 5. Supply and emissions

Which plant serves each site, from a document (`sites/dedicated_supply.csv`), and the emissions inventory or ETS data that covers the site's own generators. Match Climate TRACE's plant estimates where a document names the plant.

## Files to add

- Site list builder in `sites/build/` or a pipeline script in `pipeline/`, with a `--fixture` mode and a fixture; CI runs it and compares its output.
- Transcriptions in `sites/metered/` for regulator figures read by hand, with document URL and page on every row.
- Ledger entries in `registry/<region>.json` for what a reader should see: one per finding, record and claim separated, sources listed, `verification_status` set.
- A note `data/climate_trace_seed/<JURISDICTION>.md` written like `VIRGINIA.md` and `TEXAS.md`: what was read, what was found, what is missing and why.
- If a source has an API or a page worth watching, a config entry in `scrapers/config/` so the weekly pulls cover it.
- Rebuild: `python3 pipeline/build_handover_assets.py`, `python3 pipeline/build_measurements.py`, `python3 site/build_page.py`; `python3 pipeline/validate_measurements.py` must print 0 problems.
