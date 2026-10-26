# Weekly pulls, 2026-10-26

Nothing in this pull request changes the ledger's tables. Each item needs a person to read it against its document (the two-reading rule in CONTRIBUTING.md) and then edit the transcription named below; CI rebuilds everything from there.

## EPA emissions inventory: datacenter facilities new to the ledger or changed: 1132

File: `nei/nei_changes.csv`. Match each facility to a permit (site address, registration number in the name), then add it to sites/metered/va_nei_transcribed.csv.

## Irish annual environmental reports not yet read (first reading attached): 13

File: `ie_aer/ie_aer_first_reading.csv`. Open each PDF and check every value against Table 3 and Table 5 before adding the row to sites/metered/ireland_aer_transcribed.csv.

## Benchmarking rows new to the ledger or changed: 202

File: `benchmarking/benchmarking_changes.csv`. Drop telephone exchanges and mixed buildings unless named datacenters; append the rest to sites/metered/benchmarking_transcribed.csv.

## Watched pages: new items: 0

File: `watch/watch_new.csv`. Follow the action column for each item.

## Failures

- nei: 2020 GA: https://data.epa.gov/dmapservice/nei.vw_facility_summaries_2020/state_abbr/equals/GA/naics_code/equals/518210/pollutant_type/equals/CAP/1:5000/CSV (final URL https://data.epa.gov/dmapservice/nei.vw_facility_summaries_2020/state_abbr/equals/GA/naics_code/equals/518210/pollutant_type/equals/CAP/1:5000/CSV) did not return a csv file (Content-Type 'text/csv', 0 bytes). The file has probably moved and the old URL now redirects to a web page.
- nei: 2020 AZ: https://data.epa.gov/dmapservice/nei.vw_facility_summaries_2020/state_abbr/equals/AZ/naics_code/equals/518210/pollutant_type/equals/CAP/1:5000/CSV (final URL https://data.epa.gov/dmapservice/nei.vw_facility_summaries_2020/state_abbr/equals/AZ/naics_code/equals/518210/pollutant_type/equals/CAP/1:5000/CSV) did not return a csv file (Content-Type 'text/csv', 0 bytes). The file has probably moved and the old URL now redirects to a web page.
- nei: 2020 WA: https://data.epa.gov/dmapservice/nei.vw_facility_summaries_2020/state_abbr/equals/WA/naics_code/equals/518210/pollutant_type/equals/CAP/1:5000/CSV (final URL https://data.epa.gov/dmapservice/nei.vw_facility_summaries_2020/state_abbr/equals/WA/naics_code/equals/518210/pollutant_type/equals/CAP/1:5000/CSV) did not return a csv file (Content-Type 'text/csv', 0 bytes). The file has probably moved and the old URL now redirects to a web page.
- nei: 2023 AZ: https://data.epa.gov/dmapservice/nei.vw_facility_summaries_2023/state_abbr/equals/AZ/naics_code/equals/518210/pollutant_type/equals/CAP/1:5000/CSV (final URL https://data.epa.gov/dmapservice/nei.vw_facility_summaries_2023/state_abbr/equals/AZ/naics_code/equals/518210/pollutant_type/equals/CAP/1:5000/CSV) did not return a csv file (Content-Type 'text/csv', 0 bytes). The file has probably moved and the old URL now redirects to a web page.
- nei: 2023 WA: https://data.epa.gov/dmapservice/nei.vw_facility_summaries_2023/state_abbr/equals/WA/naics_code/equals/518210/pollutant_type/equals/CAP/1:5000/CSV (final URL https://data.epa.gov/dmapservice/nei.vw_facility_summaries_2023/state_abbr/equals/WA/naics_code/equals/518210/pollutant_type/equals/CAP/1:5000/CSV) did not return a csv file (Content-Type 'text/csv', 0 bytes). The file has probably moved and the old URL now redirects to a web page.
- nei: 2026 VA: https://data.epa.gov/dmapservice/nei.vw_facility_summaries_2026/state_abbr/equals/VA/naics_code/equals/518210/pollutant_type/equals/CAP/1:5000/CSV returned HTTP 404: the file has probably moved or been renamed. Update the URL constant at the top of the script, or download the file by hand and pass it with the script's local-file option (see --help).
- nei: 2029 VA: https://data.epa.gov/dmapservice/nei.vw_facility_summaries_2029/state_abbr/equals/VA/naics_code/equals/518210/pollutant_type/equals/CAP/1:5000/CSV returned HTTP 404: the file has probably moved or been renamed. Update the URL constant at the top of the script, or download the file by hand and pass it with the script's local-file option (see --help).
- benchmarking: Philadelphia: Philadelphia: ArcGIS error {'code': 400, 'message': 'Invalid URL', 'details': ['Invalid URL']}
- watch: va_deq_datacenter_permits: https://www.deq.virginia.gov/news-info/shortcuts/permits/air/issued-air-permits-for-data-centers returned HTTP 403 (access denied). The endpoint may now need a key, or blocks scripted access.
- watch: srp_datacenter_facts: https://www.srpnet.com/about/data-center-facts returned HTTP 403 (access denied). The endpoint may now need a key, or blocks scripted access.
