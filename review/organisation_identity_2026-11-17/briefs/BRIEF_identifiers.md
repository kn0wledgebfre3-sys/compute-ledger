# Brief: identifiers for organisations (first reading)

You are a reader for a public ledger built only from public documents. So that people and other databases can join the ledger to theirs, each organisation should carry its standard identifiers, each with the page it was read on. `tasks_identifiers.csv` (this folder) lists the organisations.

For each organisation, find:
- its **Wikidata** item (the Q-number, from its page on wikidata.org; check the item is this organisation and not a namesake, a brand or a subsidiary);
- its **LEI** (Legal Entity Identifier, 20 characters), from the GLEIF record or another LEI register page that shows the legal name; the LEI must belong to the legal entity named (the listed parent company, not a subsidiary);
- for a company filing with the US SEC, its **CIK** number, from its EDGAR page.

Record exactly the identifier as the page prints it and the URL of that page. If an identifier is not found, write "not found". Do not take an identifier from a page that does not name the organisation.

Write `result_identifiers.csv` here with Python's csv module, one row per identifier, columns:
`task_id, ledger_id, organisation, scheme (wikidata | lei | sec_cik), identifier, legal_name_on_page, source_url, notes`

Use web search sparingly: at most two searches an organisation. Then reply with a short summary: how many identifiers were found by scheme, and any organisation where the right item was unclear.
