# Classification pass: press and NGO figures shown on the record side

Read COMMON.md first.

P1/rows.csv lists figures from the ledger's measurements table whose basis is `press_report` or `ngo_report` and which are shown on the **record** side. Most come from registry entries (`entry_id`; the entries are in registry/*.json, field `record`); the rest from other feeds named in `feed`.

The project's rule (CONTRIBUTING.md): a press report *of a record* (a regulator's decision, a utility's filing, a statistics office's figure, a court's ruling, an official count) may stay on the record side with basis `press_report`, at medium confidence. A press report of **what a company, an industry body or a government says in its own voice** (an announcement, a plan, a forecast, a target, an investment figure, a design rating, a spokesperson's count) is that party's **claim**. A reporter's own unattributed figure is neither: it is weak and should say so. An NGO's documented findings (its own measurements, counts, sampling) may stay on the record side with basis `ngo_report`; its estimates or opinions may not.

For each row decide one of:
- `keep_record`: the figure reports a record (say which record: whose document or action);
- `move_to_claim`: the figure is a party's own statement (say whose);
- `unattributed`: the article gives the figure without a source (should be marked weak or dropped);
- `mislabelled_basis`: the source is not press or NGO at all (e.g. it is the regulator's own page, or the company's own release); say what the basis should be.

Decide from the entry's `record` text, the row's `metric_detail` and `notes`, and the source's title and publisher. Fetch the article only where those leave it open (at most 25 fetches); say in `how_decided` whether you read the article.

## Output
P1/result.csv with columns: measurement_id, entry_id, value_as_published, decision, whose_document_or_statement, how_decided (row text / article read), quote (from the article, if read), notes. Then a short report: counts by decision, and the entries where most rows move. Most rows can be decided from the text without fetching.
