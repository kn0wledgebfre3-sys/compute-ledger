# Brief: three items to read again (Morowali, Meta, Equinix)

You are a reader for a public ledger built only from public documents. It keeps records (regulators, courts, police, statistics offices, auditors' and assurers' statements, registries) apart from claims (what companies, industry bodies and governments say). Copy what documents say; do not judge.

**1. Morowali, Indonesia: the furnace explosion at PT Indonesia Tsingshan Stainless Steel (PT ITSS), Indonesia Morowali Industrial Park (IMIP), 24 December 2023.** The ledger holds 18 deaths from IMIP's spokesperson via The Jakarta Post (27 December 2023), described as IMIP's "initial count", and 21 deaths from the Indonesian National Police (inp.polri.go.id, 4 January 2024). A check found that the first count was 13 and the 18 was a later count. Read:
- The Jakarta Post, https://www.thejakartapost.com/id/business/2023/12/27/as-death-toll-rises-morowali-blast-brings-work-safety-squarely-into-focus
- Indonesian National Police, https://inp.polri.go.id/artikel/police-investigate-furnace-explosion-at-morowali-nickel-smelter
- Any police page (Polri, Polda Sulawesi Tengah, Humas Polri), ministry page (Kemnaker, ESDM) or wire report (Antara, Reuters, AP) from 24 December 2023 to 10 January 2024 that gives a death toll.
For each document copy: each death toll it gives, who it says gave it (IMIP, police, a ministry), the date or day the toll is given for, and any nationality split or injured count. Quote at most 25 words.

**2. Meta Platforms: the assured figures for 2024, and what is now published for 2025.** The ledger read Meta's 2024 figures from the independent accountants' review report (by EY, dated 27 August 2025) at https://sustainability.atmeta.com/asset/2025-independent-accountants-review-report/ . That address now serves the review for the year ended 31 December 2025 (dated 30 October 2026).
- (a) Find a dated or archived copy of the review report for the year ended 31 December 2024 (dated 27 August 2025), for example in the Internet Archive's Wayback Machine (web.archive.org/web/2025*/sustainability.atmeta.com/asset/2025-independent-accountants-review-report*), or a dated copy on Meta's own site. Give the exact archive URL, its capture date, and copy for 2024: Scope 1; Scope 2 location-based; Scope 2 market-based; Scope 3; carbon removal (carbon credits applied); percent of electricity matched by renewable sources; the report's date and level of assurance (limited or reasonable).
- (b) Meta's 2025 environmental data index, https://sustainability.atmeta.com/asset/2025-environmental-data-index/ : copy the 2024 values for the same six figures (and the 2023 values if printed).
- (c) The review report now at the address above (year ended 31 December 2025): copy the 2025 values for the same six, the report's date and level of assurance.
- (d) Whether Meta has published a later data index or sustainability report (2026) with 2025 values; if so copy the same six for 2025 and give its URL.

**3. Equinix: a newer data summary.** The ledger read Equinix's 2024 Data Summary (values for 2023 and 2024; a verification statement by Lucideon covering 2024), copy at https://media.greenweb.org/uploads/ds_sustainability_data_en.pdf . Find Equinix's next data summary or sustainability report (published 2026, covering 2025), on equinix.com or sustainability.equinix.com, and its verification or assurance statement. Copy for each year it prints (2024 and 2025): Scope 1; Scope 2 location-based; Scope 2 market-based; Scope 3; total energy consumption; renewable energy coverage (global); and which years and figures the verification statement covers, who gave it and the level of assurance.

Copy each value exactly as printed, with the document's URL, the page, table or section, and a quote of at most 25 words containing it. If a document cannot be opened, say so and move on.

Write `first_reading.csv` in this folder with Python's csv module, columns:
`item_id, subject, field, value_as_written, unit, url, page, short_quote, kind_of_document, notes`
where `subject` is Morowali, Meta or Equinix; `field` is what the value is (death_toll, given_by, toll_as_of, injured, nationality, scope1_2024, scope2_location_2024, carbon_removal_2024, renewable_match_2024, report_date, assurance_level, archive_capture, ...); `kind_of_document` is one of: police, ministry, press, wire, assurance_statement, company_report, archive_copy. Number the items A001, A002, ...

Neutral wording; describe, do not judge. Do not name software or tools in your notes. Never record a private person's name other than as the document prints a spokesperson's role. Then reply with a short summary of what you found and what you could not open.
