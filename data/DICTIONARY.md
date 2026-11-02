# Data dictionary

Generated from `data/datapackage.json` by `pipeline/build_data_package.py`; do not edit by hand. Every table below is checked against this schema on every build. Controlled values for `metric`, `unit`, `basis` and `relation` are listed, with definitions, in `pipeline/measurement_vocab.json`.

## `data/climate_trace_seed/measurements.csv` (3,899 rows)

Every figure in the ledger, one row each: permits, metered loads, filed demand, company statements, computed values. Start here.

| Column | Type | Required | Values | Meaning |
|---|---|---|---|---|
| `measurement_id` | string | yes |  | Content hash of feed, subject, metric, metric_detail, period, value_as_published, source_url, side and entry_id. It changes when any of those change (a corrected figure gets a new id); see CHANGELOG.md. |
| `subject_type` | string | yes | `site`, `entity`, `entry` | What the figure is about: a site (site_register), an entity such as a utility (entity_register), or a ledger entry as a whole (entries). |
| `subject_id` | string | yes |  | The site_id, entity_id or entry id. |
| `entry_id` | string |  |  | The ledger entry the figure belongs to, if any. |
| `metric` | string | yes | key of `metrics` in the vocabulary | What is measured, from pipeline/measurement_vocab.json (e.g. electricity_consumed, permitted_standby_generation). |
| `metric_detail` | string |  |  | What exactly the figure counts, in words: scope, fuel, building, part of the site. |
| `value` | number | yes |  | The figure in its published unit (the low end for a range). |
| `value_high` | number |  |  | The high end of a range, if the source gives one. |
| `unit` | string | yes | key of `units` in the vocabulary | The published unit, from the vocabulary (e.g. GJ, MW, short_ton, m3). |
| `value_canonical` | number |  |  | The value converted to one unit per dimension (MWh, MW, MWth, t, m3, m3/day, ha, h). Empty where the unit has no fixed conversion. |
| `value_high_canonical` | number |  |  | value_high converted the same way. |
| `canonical_unit` | string |  |  | The unit of value_canonical. |
| `value_as_published` | string | yes |  | The figure exactly as written in the text it was taken from: the document's line or cell, or for registry figures the entry's own sentence. |
| `qualifier` | string |  | `approximate`, `lower_bound`, `upper_bound` or empty | Read from the words around the figure ('about', 'at least', 'up to'). |
| `period_start` | date |  |  | First day the figure covers (ISO date). Empty if the source gives no period. |
| `period_end` | date |  |  | Last day the figure covers. |
| `basis` | string | yes | key of `bases` in the vocabulary | What kind of document the figure rests on (metered, permitted, filed, company_statement, press_report, derived...). |
| `side` | string | yes | `record`, `claim` | record: a regulator, court, grid operator, utility, statistics office, auditor, registry or government decision. claim: what a company, applicant or government says or plans. |
| `source_url` | string | yes |  | Link to the document. |
| `source_title` | string |  |  | Title of the document, with page or table where known. |
| `source_publisher` | string |  |  | Who published it. |
| `source_date` | string |  |  | Date of the document as known (ISO date, year-month or year). Empty if not known. |
| `feed` | string | yes |  | The file in this repository the row was built from. To correct a figure, edit that file and run ./rebuild.sh. |
| `extraction` | string | yes | `registry_prose`, `hand_transcribed`, `api_query`, `pipeline_and_second_reading` | How the figure was taken from its source. |
| `second_read` | string | yes | `yes`, `no` | yes if a second reading, by a different method or person, confirmed it against the document. |
| `notes` | string |  |  | What a reader needs to know to use the figure: caveats, conversions, part years. |

## `data/climate_trace_seed/measurement_id_aliases.csv` (12 rows)

Figures whose id changed because their wording or value was corrected: the retired id, the id that replaced it, when and why. A citation of a retired id resolves here.

| Column | Type | Required | Values | Meaning |
|---|---|---|---|---|
| `retired_measurement_id` | string | yes |  | The id no longer in measurements.csv. |
| `measurement_id` | string | yes |  | The id of the corrected figure in measurements.csv. |
| `date` | date | yes |  | Date of the correction. |
| `reason` | string | yes |  | What was corrected. |

## `data/climate_trace_seed/site_register.csv` (917 rows)

Every site the ledger has figures or links for: datacenters, buildings that file as datacenters, crypto mining sites, nuclear plants, chip fabs, smelters and refiners. One page each on the website.

| Column | Type | Required | Values | Meaning |
|---|---|---|---|---|
| `site_id` | string | yes |  | Stable id. Retired ids are mapped in site_id_aliases.csv. |
| `name` | string | yes |  | Name as the register or document gives it. |
| `operator` | string |  |  | Operator or permittee, where known. |
| `kind` | string | yes | `datacenter`, `telecom_exchange`, `mixed_building_with_datacenter`, `crypto_mining`, `crypto_to_ai_conversion`, `nuclear_plant`, `fab`, `smelter_refiner` | What the site is. |
| `country` | string | yes |  | ISO 3166-1 alpha-3 code. |
| `admin_region` | string |  |  | State, province or county. |
| `locality` | string |  |  | Town or address. |
| `lat` | number |  |  | Latitude, WGS84 decimal degrees. Empty if the site is not yet placed. |
| `lon` | number |  |  | Longitude, WGS84 decimal degrees. |
| `status` | string |  |  | Usually operating, permitted, under_construction, announced or refused; Texas rows carry the TCEQ project status as text. |
| `ct_source_id` | string |  |  | Climate TRACE asset id, where the site was matched to one. |
| `backlog_id` | string |  |  | Id in the unlocated-site backlog, if the site came from it. |
| `register_source` | string |  |  | The register or document the site was taken from. |
| `also_known_as` | string |  |  | Other names and ids (registration numbers, licence numbers). |
| `notes` | string |  |  | Caveats. |

## `data/climate_trace_seed/site_id_aliases.csv` (16 rows)

Site ids that were retired (merged duplicates) and the id that replaced each.

| Column | Type | Required | Values | Meaning |
|---|---|---|---|---|
| `retired_site_id` | string | yes |  | The id no longer used. |
| `site_id` | string | yes |  | The id that replaced it (in site_register.csv). |
| `reason` | string | yes |  | Why it was retired. |

## `data/climate_trace_seed/entity_register.csv` (44 rows)

Companies, utilities and registers that figures or chain links refer to.

| Column | Type | Required | Values | Meaning |
|---|---|---|---|---|
| `entity_id` | string | yes |  | Stable id. |
| `name` | string | yes |  | Name. |
| `kind` | string |  |  | Company, municipal utility, cooperative, register... |
| `country` | string |  |  | Country. |
| `notes` | string |  |  | Caveats. |

## `data/climate_trace_seed/entries.csv` (203 rows)

The ledger's entries as a flat table, built from registry/*.json: the record, the claim and the one-line gap between them.

| Column | Type | Required | Values | Meaning |
|---|---|---|---|---|
| `id` | string | yes |  | Entry id (stable). |
| `registry_file` | string | yes |  | The registry file the entry lives in; edit it there. |
| `country` | string | yes |  | Country or countries, as names; 'EU' and 'Global' for entries above country level. |
| `region` | string |  |  | Region within the country. |
| `site_or_subject` | string | yes |  | What the entry is about. |
| `operator` | string |  |  | Operator or responsible party. |
| `lat` | number |  |  | Latitude of the site or area (approximate for areas). |
| `lon` | number |  |  | Longitude. |
| `category` | string | yes | `accounting`, `circularity`, `community`, `ewaste`, `fab`, `fuel`, `grid_policy`, `heat_reuse`, `labor`, `land_biodiversity`, `minerals`, `moratorium`, `power`, `public_money`, `water` | Theme of the entry. |
| `record` | string | yes |  | What the public record says, with numbers and dates. |
| `claim` | string | yes |  | What the operator or government says in public, or 'none found'. |
| `gap` | string | yes |  | The difference between record and claim, in one line, without adjectives. |
| `confidence` | string | yes | `high`, `medium`, `low` | How firmly the record rests on record holders' documents that were read. |
| `verification_status` | string | yes | `verified`, `partial`, `not_found` | Result of the second reading of the record against its documents. |
| `verification_note` | string |  |  | What was read, when, and what was found. |
| `last_checked` | date | yes |  | Date the entry was last checked. |
| `receipt` | string |  |  | Id of the worked case in receipts/, if the entry has one. |
| `n_record_sources` | integer | yes |  | Number of record sources (listed in entry_sources.csv). |
| `n_claim_sources` | integer | yes |  | Number of claim sources. |

## `data/climate_trace_seed/entry_sources.csv` (940 rows)

Every document an entry cites, one row each, with the side it supports.

| Column | Type | Required | Values | Meaning |
|---|---|---|---|---|
| `entry_id` | string | yes |  | Entry id. |
| `side` | string | yes | `record`, `claim` | Whether the document supports the record or the claim. |
| `title` | string | yes |  | Title, with page or section where given. |
| `url` | string | yes |  | Link. |
| `publisher` | string |  |  | Publisher. |
| `date` | string |  |  | Date as known. |
| `date_note` | string |  |  | Why the date is uncertain, where it is. |

## `data/chain/edges.csv` (207 rows)

Documented links in the chain from smelter to chipmaker to site and its power, fuel and water. Column guide: sites/chain/README.md.

| Column | Type | Required | Values | Meaning |
|---|---|---|---|---|
| `edge_id` | string | yes |  | Content hash of the row (notes and second_read excluded). |
| `leg` | string | yes |  | Which leg of the chain (refiner_to_maker, power_to_site, water_to_site...). |
| `from_type` | string | yes | `site`, `entity`, `entry`, `named` | site, entity, entry, or named (a party not yet in a register). |
| `from_id` | string |  |  | Id of the supplying party. |
| `from_name` | string | yes |  | Its name as the document gives it. |
| `relation` | string | yes | key of `relations` in the vocabulary | From the vocabulary: refines_for, supplies_power_to, supplies_water_to... |
| `to_type` | string | yes | `site`, `entity`, `entry`, `named` | As from_type. |
| `to_id` | string |  |  | Id of the receiving party. |
| `to_name` | string | yes |  | Its name as the document gives it. |
| `period_start` | date |  |  | When the link held, if the document says. |
| `period_end` | date |  |  | End of that period. |
| `basis` | string | yes | key of `bases` in the vocabulary | Kind of document; company_statement makes the edge a claim. |
| `side` | string | yes | `record`, `claim` | record or claim. |
| `document_title` | string | yes |  | Document that states the link. |
| `document_url` | string | yes |  | Link. |
| `publisher` | string |  |  | Publisher. |
| `document_date` | string |  |  | Date of the document. |
| `quoted_line` | string |  |  | The phrase in the document that states the link, copied exactly. |
| `entry_id` | string |  |  | The ledger entry that discusses it. |
| `notes` | string |  |  | What the reader needs to know. |
| `second_read` | string | yes |  | yes or no, with how it was confirmed. |

## `data/climate_trace_seed/checks.csv` (23 rows)

Every check run on the ledger: what was checked, how, by whom, and what it found. Built from review/CHECKS.csv and the findings files.

| Column | Type | Required | Values | Meaning |
|---|---|---|---|---|
| `check_id` | string | yes |  | Id. |
| `date` | date | yes |  | Date of the check. |
| `name` | string | yes |  | Short name. |
| `what_was_checked` | string | yes |  | Scope. |
| `method` | string | yes |  | How. |
| `checker` | string | yes |  | Who (always someone other than the person who did the work). |
| `selection` | string |  |  | How the items were chosen (all, random sample, targeted). |
| `n_checked` | string |  |  | How many items. |
| `result` | string | yes |  | What it found. |
| `findings_file` | string |  |  | The file in review/ with the findings. |
| `applied_in` | string |  |  | Where the corrections were applied. |
| `n_findings_in_table` | integer |  |  | Findings from this check in findings.csv. |
| `findings_by_severity` | string |  |  | Counts by severity. |
| `status_now` | string |  |  | What the current data show for those findings, recomputed at every build. |

## `data/climate_trace_seed/findings.csv` (1,560 rows)

Every finding from every check, with what the data show now.

| Column | Type | Required | Values | Meaning |
|---|---|---|---|---|
| `finding_id` | string | yes |  | Id. |
| `check_id` | string | yes |  | The check (checks.csv). |
| `date` | date | yes |  | Date of the check. |
| `subject_type` | string |  |  | figure, link, entry, text or other. |
| `subject_id` | string |  |  | What it concerns. |
| `entry_id` | string |  |  | Entry, if any. |
| `location` | string |  |  | Where in the file or entry. |
| `quoted` | string |  |  | The text or value as it stood when checked. |
| `finding` | string |  |  | What the checker found. |
| `severity` | string |  |  | As the checker gave it. |
| `status_now` | string |  |  | What the current data show, recomputed at every build. |
