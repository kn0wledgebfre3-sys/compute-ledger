# Brief: check of the ledger's links against their documents

You are an independent reader for a public ledger built only from public documents. The ledger links each figure to the site or organisation it is about, each site to the organisation its list names and the place it is in, each document to its publisher, and parties in a supply chain to each other. You did not build any of it. `tasks_graph_check.csv` (this folder) lists 52 items drawn at random; each gives a document's URL, a subject and a question.

For each task, open the document at `url` and answer the question from that document alone:
- `figure`: copy the value and unit the document gives for what is asked, for that subject, and say whether the figure is about that site or organisation;
- `operator`: say whether the document names that organisation (or a company of the same name, apart from legal form or punctuation) in connection with that site, and as what;
- `place`: give the locality, region or state, and country the document gives for the site;
- `chain`: copy the line that states what the first party does for or with the second, or say the second is not named;
- `publisher`: give the organisation that publishes the document.

Some URLs are data services that return a table (CSV or JSON) for a query; read the row for the subject. Some are lists of many permits or sites; find the subject's row. If a document cannot be opened, write "could not open" and do not use another source. You should need no web searches.

Write `result_graph_check.csv` here with Python's csv module, columns:
`task_id, answer, quote (at most 25 words, copied exactly), page_or_row, notes`

Neutral wording. Then reply with a short summary: how many documents opened, and any item where the document does not support what the subject or question implies.
