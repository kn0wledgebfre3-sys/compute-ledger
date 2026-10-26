# Reviewer C: audit of the registry entries

Read COMMON.md first.

## Your files
crypto_mining.json, nuclear.json, paper_layer.json, people_land_money.json, minerals_ewaste.json, supply_chain.json (113 entries) (under registry/). Each is a JSON list of entries with: id, country, region, site_or_subject, operator, lat, lon, category, record, record_sources, claim, claim_sources, gap, confidence, verification_status, verification_note, last_checked. The ledger page shows `record`, `claim` and `gap` side by side for each entry. Read every entry in your files in full.

## Check each entry for
1. **Records vs claims.** Is everything in `record` from a record holder (see COMMON.md)? Is any company statement, press report or advocacy group finding sitting in `record`? Are `record_sources` actually record holders (look at each URL's domain and title: a company site, a newspaper or an NGO is not a record holder, though an NGO-hosted copy of a regulator's document can be)? Is a claim attributed to who made it?
2. **Internal consistency.** Do numbers, dates and names in `record` match each other and the `claim` and `gap`? Is `verification_status` consistent with `verification_note` (e.g. "verified" but the note says a document could not be read)? Is `confidence` sensible? Is `last_checked` a real date not after 2026-10-24? Any date in the text after 2026-10-24 stated as past?
3. **Across entries.** The same site, figure or event described differently in two entries (in your files, or against the other registry files, which you may grep). Duplicate entries. Coordinates far from the stated place (check lat/lon against the country and region; flag anything in the wrong country or ocean).
4. **Against the measurements table.** data/climate_trace_seed/measurements.csv holds figures read from these entries (feed `registry/...`, `entry_id` = the entry id). For each of your entries, check that the rows' `value_as_published`, unit, period and side agree with the entry text (quick check with python: group rows by entry_id).
5. **Tone and fairness.** Anything that villainises a company, person or community, speculates about motives, or presents a gap as wrongdoing. Good-practice cases should read as such. Loaded adjectives.
6. **Sources.** URLs that look malformed, placeholders, search-result or login pages, or duplicates of each other; a `record` that cites no URL for a specific figure. Spot-fetch at most 10 record sources where something looks wrong (not a full re-read).

## Output
C2/result.csv with columns: entry_id, field, quoted_text, severity, problem, suggested_fix. Then C2/report.md: counts by severity, the worst ten, patterns. Read files with python/json in large chunks rather than many small reads.
