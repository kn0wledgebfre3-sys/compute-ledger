# Brief: second reading of state evaluations of datacenter tax incentives

You are the second reader for a public ledger built only from public documents. A first reader found the documents listed in `second_reading_tasks.csv` (this folder) and took figures from them. You are not shown those figures: read each document yourself and write down what it states, so the two readings can be compared.

For each row (`task_id`), open the document at `url` and find what `what_to_find` asks for, for the period in `period_or_scope_hint` where one is given. Record:
- `value_as_published`: exactly as the document prints it (with its units, for example "$68,674,000" or "42 data centers"); for "count the rows" tasks, count the rows of the list or table yourself and say so;
- `period` and `scope` (state, local, both, or not stated) as the document gives them;
- `page_or_table`, and a `short_quote` of at most 15 words containing the figure;
- `notes`: anything that changes how the figure should be read (for example a figure that is a projection, a model estimate, a cumulative total, or a total of all employees of the participating companies rather than jobs at datacenters).

If the document does not state it, write "not stated". If the document cannot be opened, write "could not open" and do not substitute another source. Neutral wording, no adjectives about states, companies or the incentives. The documents are known, so you should need few web searches: open the URLs directly (for PDFs, take the exact sentences and table rows that state the figure, with page numbers).

Write `second_reading_result.csv` here with Python's csv module, columns:
`task_id, state, value_as_published, period, scope, page_or_table, short_quote, notes`

Then reply with a short summary: how many tasks you completed, how many documents could not be opened, and any figure that you think is easy to misread.
