# Brief: second reading of group links

You are the second reader for a public ledger built only from public documents. A first reader found, for each pair of organisations in `tasks_groups_second.csv` (this folder), a document at `url` that is said to state how the two are related (one owns the other, is a subsidiary or project company of it, acts for it, or was renamed as it). You are not shown what the first reader found. Open the document yourself and write down what it states.

For each task, record:
- `relation_stated`: one of owned_by, subsidiary_of, project_company_of, acts_for, renamed_as, joint_venture_of, other, not_stated — what the document says the first-named organisation (`entity`) is to the second (`related`);
- `as_of_date`: the date the document gives for it, if any;
- `short_quote`: at most 25 words, copied exactly, that states the relationship;
- `notes`: anything that changes the reading (a former owner, a share less than all, a different entity of a similar name).

If the document does not state a relationship between the two, write not_stated. If it cannot be opened, write "could not open" in `relation_stated` and do not use another source. You should need no web searches. Neutral wording. Write `second_groups.csv` here with Python's csv module, columns:
`task_id, relation_stated, as_of_date, short_quote, notes`

Then reply with a short summary: how many links the documents state, and any that look wrong.
