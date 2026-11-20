# Brief: record-based counts of datacentres in the United States and England

You are a reader for a public ledger built only from public documents. It keeps records (regulators' registers and databases) apart from claims (what companies, industry bodies and directories say). Each country page shows a commercial directory's count of datacentres; the ledger wants a count from a regulator's register beside it, stated exactly for what it counts. Copy and count; do not judge.

1. **United States: the EPA's Facility Registry Service (FRS).** FRS lists facilities that are regulated or tracked by EPA and state programs, with NAICS codes. NAICS 518210 is the code for data processing and hosting (find its exact title in the NAICS edition FRS uses, from the Census Bureau's NAICS pages).
   - Count the facilities in FRS with NAICS 518210, nationally, using a public query of EPA's own data service (for example Envirofacts, https://data.epa.gov/efservice/ , or ECHO's facility search, https://echo.epa.gov/ ). Give the exact query URL, so that another reader can repeat it, the date you ran it, and the count it returns. If two services give different counts, report both and say what each counts (facilities, program records, sites with coordinates).
   - The same count for Virginia, Texas, Oregon, Arizona, Georgia and Ohio.
   - How many of the national count have coordinates (latitude and longitude), if the service says.
   - Which programs the facilities are registered under (for example air permits), as the service lists them, for the national count if available.
   - EPA's own description of what FRS is and what a NAICS code in FRS means (a quote from an EPA page), so the count can be described accurately.
2. **England: the Environment Agency's public register of environmental permits** (https://environment.data.gov.uk/public-register/ ). Determine whether the register can be searched for datacentres: by activity, by a code, or by site or operator name. If it can, count the permits whose site name or operator name contains "data centre", "datacentre" or "data center", give the exact search URL and date, and list each permit's number, site name, operator (a company) and activity as printed. Also look for an Environment Agency publication that states how many datacentres hold environmental permits (for example guidance or a statement on regulating datacentres' backup generators); copy the number and the sentence.

Copy each value exactly as printed or returned, with the URL, the section, and a quote of at most 25 words. If a service cannot be reached, say so and move on.

Write `first_reading.csv` in this folder with Python's csv module, columns:
`item_id, subject, field, value_as_written, unit, url, page, short_quote, kind_of_document, notes`
where `subject` is "EPA FRS" or "Environment Agency register"; `field` is what the value is (count_national, count_VA, count_with_coordinates, query_date, naics_title, program, definition, permit, ...); `kind_of_document` is one of: regulator_database, regulator_page, statistics_page. Number the items C001, C002, ...

Neutral wording; describe, do not judge. Do not name software or tools in your notes. Then reply with a short summary of what you found and what you could not reach.
