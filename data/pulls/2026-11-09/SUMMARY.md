# Weekly pulls, 2026-11-09

Nothing in this pull request changes the ledger's tables. Each item needs a person to read it against its document (the two-reading rule in CONTRIBUTING.md) and then edit the transcription named below; CI rebuilds everything from there.

## EPA emissions inventory: datacenter facilities new to the ledger or changed: 1048

File: `nei/nei_changes.csv`. Match each facility to a permit (site address, registration number in the name), then add it to sites/metered/va_nei_transcribed.csv.

## Irish annual environmental reports not yet read (first reading attached): 3

File: `ie_aer/ie_aer_first_reading.csv`. Open each PDF and check every value against Table 3 and Table 5 before adding the row to sites/metered/ireland_aer_transcribed.csv.

## Benchmarking rows new to the ledger or changed: 4

File: `benchmarking/benchmarking_changes.csv`. Drop telephone exchanges and mixed buildings unless named datacenters; append the rest to sites/metered/benchmarking_transcribed.csv.

## Watched pages: new items: 1

File: `watch/watch_new.csv`. Follow the action column for each item.

## Failures

- benchmarking: New York City: https://data.cityofnewyork.us/resource/5zyy-y8am.json?$where=%28primary_property_type%3D%27Data%20Center%27%29%20OR%20address_1%20in%28%27111%208th%20Avenue%27%2C%27375%20Pearl%20Street%27%2C%2785%2010th%20Avenue%27%2C%27325%20Hudson%20Street%27%2C%2760%20Hudson%20Street%27%2C%2756%20Hudson%20Street%27%2C%2732%20Avenue%20of%20the%20Americas%27%29&$limit=5000 returned HTTP 503: '{"message":"Service unavailable","errorCode":"service-unavailable","data":{}}'
- benchmarking: Chicago: https://data.cityofchicago.org/resource/xq83-jr8c.json?$where=%28primary_property_type%3D%27Data%20Center%27%29%20OR%20address%20in%28%27350%20E%20Cermak%20Rd%27%2C%27600%20S%20Federal%20St%27%2C%27427%20S%20LaSalle%20St%27%2C%27840%20S%20Canal%20St%27%29&$limit=5000 returned HTTP 503: '{"message":"Service unavailable","errorCode":"service-unavailable","data":{}}'
- benchmarking: Philadelphia: Philadelphia: ArcGIS error {'code': 400, 'message': 'Invalid URL', 'details': ['Invalid URL']}
- watch: va_deq_datacenter_permits: https://www.deq.virginia.gov/news-info/shortcuts/permits/air/issued-air-permits-for-data-centers returned HTTP 403 (access denied). The endpoint may now need a key, or blocks scripted access.

## Notes (not failures)

- nei: 2020 GA: the query returned an empty file (no rows); check by hand if a datacenter facility is expected there
- nei: 2020 AZ: the query returned an empty file (no rows); check by hand if a datacenter facility is expected there
- nei: 2020 WA: the query returned an empty file (no rows); check by hand if a datacenter facility is expected there
- nei: 2023 AZ: the query returned an empty file (no rows); check by hand if a datacenter facility is expected there
- nei: 2023 WA: the query returned an empty file (no rows); check by hand if a datacenter facility is expected there
- nei: 2026: not released by EPA yet (the 2026 view does not exist); checked again next week
- nei: 2029: not released by EPA yet (the 2029 view does not exist); checked again next week
