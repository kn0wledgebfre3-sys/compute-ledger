# Organisations: how names become organisations

The organisations themselves are in `sites/entity_register.csv` (id, name, kind, country, notes). The files here say which names, as the ledger's sources print them, refer to which organisation. Each is read by `pipeline/build_graph.py`; a name not listed links to nothing, and the build lists it in `data/graph/summary.json`.

| File | Columns | What it does |
|---|---|---|
| `operator_names.csv` | `name_as_listed, entity_id, role, note` | Every operator name in the site register, exactly as the site's list prints it, and the organisation it names. One name can name two (a joint venture, a holder named with its group); then it has two rows. `role` says how the listing names it (operator, permit holder, applicant, occupant per the Comptroller, a share). An empty `entity_id` means the name names no organisation, and `note` says why. |
| `named_parties.csv` | `name_as_written, entity_id, note` | Parties that a chain link names in words (from or to type `named` in `sites/chain/edges.csv`) and that are an organisation in the register. The chain table itself is not changed. |
| `entry_organisations.csv` | `entry_id, entity_id, name_as_written` | The organisations each entry's operator field names. A name inside a longer name (Amazon inside Amazon Data Services Ireland) counts only as the longer one. |
| `publisher_names.csv` | `publisher_as_written, entity_id` | Publisher names, as the ledger recorded them, that are the organisation itself (its filings, reports and pages). |
| `identifiers.csv` | `entity_id, scheme, identifier, legal_name_on_page, source_url, read_on, second_read, note` | Wikidata items, LEIs and SEC CIKs, each from the page it was read on. |

## The rules

- A name maps to an organisation only when it names that organisation. Names that differ only in legal form (Inc., LLC), punctuation, case or an obvious typing slip are the same organisation.
- A differently named legal entity (a national subsidiary such as Amazon Data Services Ireland Ltd, a project company such as QTS Investment Properties Ashburn, LLC) is its own organisation. It is linked to its group only by a row of `sites/chain/edges.csv` (leg `ownership`, relation `owns`, `acts_for` or `renamed_as`) with a document and the line that states it.
- Brand names a site list uses for a group (Google, Microsoft, Amazon Web Services) map to the group, as the register already names it (Alphabet Inc. (Google)).
- A facility name, a fragment of permit text, "unknown", and a private person named as an applicant are not organisations. The ledger makes no pages for private individuals.
- An organisation's `country` in the register is filled only where a document read gives where it is registered or headquartered. It is never inferred from where its sites are.
