# Brief: datacentre counts in a commercial directory, by country

You are a reader for a public ledger built from public documents. The ledger keeps records (permits, registers, official statistics) apart from claims (what companies and others say). It wants to show, beside the sites it can name from records, how many datacentres a commercial directory lists for each country, marked as the directory's own count, not as a record.

Open the directory's list of datacentres by country: https://www.datacentermap.com/datacenters.html

For each country in `countries.txt` (in your folder), copy the number of datacentres the page lists for it, exactly as printed. Also copy the page's total worldwide count, the number of countries it says it covers, and what it says about what the listings include and who submits them (quote the sentences). If the page gives a date or says how often it is updated, copy that. If a country is not on the page, write "not listed". If the page lists a country under another name (for example "USA", "The Netherlands"), say so in `notes`.

Write `result.csv` in your folder with Python's csv module, columns:
`country_code, country_as_listed, count_as_printed, notes`
and a second file `page.csv` with columns `item, value_as_written, short_quote` for: total, countries_covered, what_is_listed, who_submits, updated.

Read only that page. Neutral wording; do not name software or tools in your notes. Reply with a one-paragraph summary.
