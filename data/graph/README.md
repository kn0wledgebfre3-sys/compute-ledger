# The ledger as a graph

`pipeline/build_graph.py` writes this folder from the ledger's own tables. Nothing here is typed by hand: change the tables it reads, then run `./rebuild.sh`.

| File | What it holds |
|---|---|
| `nodes.csv` | One row per node: organisations, sites, countries, regions, documents, entries, checks, figures, and the parties a document names that are in no register yet. |
| `links.csv` | One row per link, with where it comes from: the document that states it and the line it was read from, or the table of the ledger that holds it. |
| `graph.jsonld` | The same, as JSON-LD, with a permanent address on the ledger's site for every node. |
| `vocabulary.jsonld` | The ledger's classes and relations, and its controlled lists (relations, kinds of document, metrics, kinds of site) as SKOS concept schemes. |
| `summary.json` | Counts by kind of node, relation and side, and any operator name not yet matched to an organisation. |

## The rule

A link exists only where a table of the ledger holds it, so every line on a drawing has a source behind it. Nothing is inferred from a name, an address or a shared word:

- a **site** is linked to an **organisation** through `sites/organisations/operator_names.csv`, which takes each operator name exactly as the list the site came from prints it (a permit, a planning file, a licence, a company list) and says by hand which organisation it names. Names that differ only in legal form, punctuation or a typing slip share one organisation; a differently named legal entity (a national subsidiary, a project company) is its own organisation. A facility name, a fragment of permit text, "unknown" or a private person is matched to nothing;
- an **organisation** is linked to another (owns, acts for, renamed as) only through a row of `sites/chain/edges.csv` (leg `ownership`) with a document and the quoted line;
- an **entry** names an organisation through `sites/organisations/entry_organisations.csv`, read from the entry's operator field;
- a **document** is published by an organisation through `sites/organisations/publisher_names.csv`, which matches the publisher as the ledger recorded it;
- **identifiers** (Wikidata, LEI, SEC CIK) come from `sites/organisations/identifiers.csv`, each with the page it was read on.

## Nodes

`node_id` is `type:id`. Types and their pages:

| Type | Id | Page |
|---|---|---|
| `org` | the entity id in `sites/entity_register.csv` | `org/<id>.html` |
| `site` | the site id in the site register | `sites/<id>.html` |
| `country` | ISO 3166 alpha-3 (`EUU` EU-wide, `WLD` global) | `country/<code>.html` |
| `region` | `<country>/<region>` as the site lists give it | a section of the country's page |
| `doc` | `d-` and the first ten hex digits of the SHA-1 of the URL | `doc/<id>.html` |
| `entry` | the entry id | `index.html#<id>` |
| `check` | the check id | (the checks table) |
| `figure` | the measurement id | `explore.html#<id>` |
| `party` | a slug of the name as the document gives it | `chain.html#party-<slug>` |

The IRI of a node is the page's address without `.html`, under https://kn0wledgebfre3-sys.github.io/compute-ledger/.

## Links

| Relation | From → to | Where it comes from |
|---|---|---|
| `located_in` | site → region or country; region → country | the site register |
| `listed_operator` | site → organisation | `operator_names.csv`; the note gives the role (operator, permit holder, applicant, occupant) and the name as listed |
| `based_in` | organisation → country | the entity register |
| `names` | entry → organisation | `entry_organisations.csv` |
| `cites` | entry → document | the entry's record and claim sources (`side` says which) |
| `about`, `read_from` | figure → subject; figure → document | the measurements table |
| `published_by` | document → organisation | `publisher_names.csv` |
| `examined`, `read_again` | check → subject; check → document | the checks' findings |
| chain relations (`refines_for`, `fabricates_for`, `supplies_water_to`, `contracts_power_from`, `owns`, `acts_for`, ...) | as `sites/chain/edges.csv` | a document and the quoted line; `side` is record or claim |

`side` is `record` or `claim` where a document states the link; empty where the link is the ledger's own bookkeeping (a site's country, an entry's citation).

## Standards used

- **schema.org** for organisations, places, countries and creative works (`schema:Organization`, `schema:Place`, `schema:Country`, `schema:CreativeWork`, `schema:containedInPlace`, `schema:sameAs`).
- **PROV-O** for where a statement comes from (`prov:wasDerivedFrom` on every link and figure that has a document).
- **QUDT** for units and values of figures (`qudt:numericValue`, `qudt:unit`), where the ledger's canonical unit has a QUDT unit; otherwise `cl:unitText`.
- **SKOS** for the controlled lists in `pipeline/measurement_vocab.json` and the graph's own relations.

The ledger's own terms are under `https://kn0wledgebfre3-sys.github.io/compute-ledger/vocab#` and are defined in `vocabulary.jsonld`.
