# Brief: second reading (Scotland's datacentre proposals)

You are a second reader for a public ledger built from public documents. Another reader has read these documents; you are not shown what they found. `tasks.csv` (this folder) lists 93 questions, each with a document's URL, a subject (a site, or "national guidance") and what to look for.

For each task, open the document and copy what it states, exactly as printed, with the page, table or section and a quote of at most 25 words containing it. Where a question asks for a figure, give every value the document prints for it, with its label (for example two bases, or two years). If the document does not state it, write "not stated". If the document cannot be opened, write "could not open". Use only that document. Never record a private person's name; record companies and public bodies only. Many tasks share a document: open each document once and answer all its tasks.

Write `result.csv` here with Python's csv module, columns:
`task_id, value_as_written, page, short_quote, notes`

Neutral wording; do not name software or tools in your notes. Reply with a short summary: how many documents opened, and any task where the document says something different from what its question implies.
