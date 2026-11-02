# Brief: who and what is each facility in EPA's emissions inventory?

You are the second reader for a public ledger of datacenters built only from public documents. A script pulled EPA's
National Emissions Inventory (NEI) facility summaries for facilities that state agencies classed under NAICS 518210
("Computing Infrastructure Providers, Data Processing, Web Hosting, and Related Services"), 2020 and 2023 inventories.
The emission figures themselves are EPA's; your job is the part a script cannot check: **what each facility is and
where it is**.

Your list is in `facilities_<GROUP>.csv` (same folder as this brief). Columns: the inventory's facility id
(`eis_facility_id`), the name, address and coordinates as EPA's inventory gives them, and, where one exists, a site the
ledger already lists within 2 km (`nearby_site_already_listed`). Being close is **not** evidence that two are the same
site; treat it as a question.

For each facility, find public documents that answer:

1. **Is it a datacenter** (a building whose main use is housing servers), or something else (an office, a call centre,
   a printing plant, a payroll firm's office with a boiler)? Say what it is in a few plain words.
2. **Where is it physically?** Some inventory addresses are an owner's mailing address (for example a company
   headquarters in another state). If so, give the physical location a document gives (street, town, county).
3. **Who holds the permit or runs it, per a document?** Many datacenters are held by companies with unrelated names
   (an LLC). Only link an LLC to a better-known company when a document does so; say which document.
4. **Permit or registration number** in the state's air permit system, if a document gives it.
5. **Same site as the nearby listed site?** yes / no / unclear, and on what document.

Sources, best first: the state environmental agency's air permit or permit application, a county or city record
(planning, assessor, economic-development agreement), a utility or public-commission filing, then the operator's own
page, then press. Label each source `record` (regulator, county, court, utility, commission, registry), `company`
(the operator's own statement) or `press`. EPA's own Envirofacts/data.epa.gov service is not reachable from your tools;
do not try to reproduce the emission numbers.

Rules: quote at most a short phrase (15 words) from any source. Neutral wording, no adjectives about the companies, no
accusations: this is identification only. If you cannot find a document, say "not found" rather than guessing; an
honest "unclear" is useful. Do not use other parts of the ledger as a source.

## Output

Write `result_<GROUP>.csv` in this folder, one row per facility, with these columns:

`eis_facility_id, is_datacenter (yes|no|unclear), what_it_is, physical_location, held_or_run_by_per_document,
permit_or_registration, same_as_nearby_listed_site (yes|no|unclear|none listed), source_url, source_type
(record|company|press), source_publisher, source_date, short_quote, second_source_url, notes`

Then reply with a short summary: how many facilities you could identify from a record, how many only from company or
press material, how many not at all, and any facility that is not a datacenter or whose inventory address is not
where it is.
