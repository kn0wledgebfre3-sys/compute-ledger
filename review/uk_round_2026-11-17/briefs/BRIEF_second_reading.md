# Brief: second reading of UK records on datacentres

You are the second reader for a public ledger built only from public documents. A first reader found the documents listed in your task file (`tasks_N.csv` in this folder) and took figures and facts from them. You are not shown what they found: read each document yourself and write down what it states, so the two readings can be compared.

For each row (`task_id`), open the document at `url` and find the item named in `figure` (with `unit` and `period_hint` as a guide to what is meant), for the site or subject named. `where_first_reader_found_it` tells you where to look; it is not the answer. Record:
- `value_as_published`: exactly as the document prints it, with its units (for example "300.85 MWth", "69 generators", "500 hours per year", "up to 72,000 sqm GEA", "2037"). For a decision, the decision and its date as printed ("allowed, 9 July 2025"). For a permit reference, the reference as printed.
- `period` as the document gives it;
- `page_or_table`, and a `short_quote` of at most 15 words containing the figure;
- `notes`: anything that changes how the figure should be read: rated thermal input (fuel in) against electrical output; IT load against grid connection; requested against contracted against connected capacity; operational jobs at the site against construction jobs or jobs claimed for a wider area; a projection or scenario; a figure the document attributes to someone else (an applicant, a company, an industry body).

If the document does not state it, write "not stated". If the document cannot be opened, write "could not open" and do not substitute another source. Neutral wording, no adjectives about companies, councils, regulators or the government. The documents are known, so you should need no web searches: open the URLs directly, asking for the exact sentences and table rows that state each item, with page numbers. Several tasks share a document: read it once for all of them.

Write `second_N.csv` in this folder (N as in your task file) with Python's csv module, columns:
`task_id, value_as_published, period, page_or_table, short_quote, notes`

Then reply with a short summary: how many tasks you completed, how many documents could not be opened, and any item you think is easy to misread.
