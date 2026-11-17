# Brief: which company stands behind each name (first reading)

You are a reader for a public ledger built only from public documents. Sites in the ledger are listed under the names that permits, planning files and licences give them: often a project company, a national subsidiary or a company holding a permit for another. The ledger links such a name to a group only where a document states the link. `tasks_groups.csv` (this folder) lists each name and the link to check.

For each task, find a document that states whether the named company is owned by, is a subsidiary or project company of, acts for, or was renamed as the related organisation, and record what it says. In order of preference:
1. a register record: a national company register (Companies House, the Irish Companies Registration Office, a US state's business register), the GLEIF record of a Legal Entity Identifier, which gives direct and ultimate parents;
2. a regulator's, court's or planning authority's document that states the relationship;
3. a filing by the group itself: a subsidiaries list (for example SEC Form 10-K Exhibit 21), annual accounts, an annual report;
4. the group's own web page or press release;
5. a press report, only if nothing above exists.

Record exactly what the document says; do not infer a parent from a shared name or address. If the document says something else (another parent, a joint venture, a former owner), record that. If nothing is found, say "not found" and list what you looked at.

Write `result_groups.csv` here with Python's csv module, columns:
`task_id, entity_as_named, related_organisation, relation_stated (owned_by | subsidiary_of | project_company_of | acts_for | renamed_as | joint_venture_of | other | not_found), as_of_date, document_title, publisher, document_date, url, kind_of_document (register | regulator | court | planning | company_filing | company_page | press), short_quote, notes`

`short_quote`: at most 25 words, copied exactly, that states the link. Neutral wording, no adjectives about any company. Use web search sparingly: at most two searches a task. Then reply with a short summary: how many links were found and from which kind of document, and which were not found.
