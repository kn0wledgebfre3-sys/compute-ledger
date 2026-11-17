# Brief: second reading of organisation identifiers

You are the second reader for a public ledger built only from public documents. A first reader found, for each organisation in `tasks_identifiers_second.csv` (this folder), a page that gives one of its identifiers: a Legal Entity Identifier (LEI, 20 characters), an SEC Central Index Key (CIK, up to 10 digits), or a Wikidata item (Q followed by digits). You are not shown the identifier. Open the page at `url` yourself and write down what it shows.

For each task, record:
- `identifier_on_page`: the identifier of the `scheme` named, exactly as the page prints it (for a Wikidata item page, the Q-number in the page's own address or heading);
- `legal_name_on_page`: the legal name (or, for Wikidata, the item's label) as the page prints it;
- `status_on_page`: for an LEI its registration status (issued, lapsed, retired) if shown; for Wikidata, what the item is an instance of (for example "business", "enterprise", "brand") if shown;
- `notes`: anything that suggests the page is about a different entity (a subsidiary, a former name, a namesake).

If the page cannot be opened, write "could not open" and do not use another source. You should need no web searches. Write `second_identifiers.csv` here with Python's csv module, columns:
`task_id, identifier_on_page, legal_name_on_page, status_on_page, notes`

Then reply with a short summary: how many pages opened, and any identifier that looks like the wrong entity.
