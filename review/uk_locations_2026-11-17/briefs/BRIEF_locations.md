# Brief: where each UK site is, as its documents state it

You are a reader for a public ledger built only from public documents. The ledger holds 67 UK datacentre sites, each known from an environmental permit, a planning decision or a report of one. None is on the ledger's map yet. Your job is to copy, for each site in your task file, where an official document places it. You are not asked to work anything out.

**For each task** (one site), open the documents listed in `documents` (separated by " ; ") and look for where they place the site, in this order of preference:

1. an Ordnance Survey **grid reference** (two letters and digits, such as "TQ 07304 80166" or "TQ0730480166");
2. an **easting and northing** (such as "507304, 180166" or "E 507304 N 180166");
3. **latitude and longitude**;
4. the site's **postal address with its postcode**;
5. an address without a postcode.

Permits usually give the installation's grid reference on the first pages (the permit's introductory note, a table of site details, or the decision document's description of the installation). Planning decisions and officer reports usually give an address, and sometimes a grid reference or an easting and northing in the application details.

**Make sure it is the site.** Documents also give grid references for other things: individual stacks or emission points, receptors in an air-quality assessment, a weather station or airport, a river or a protected habitat. Record those only if nothing for the site itself is given, and then say what the reference is for in `refers_to`.

**If the listed documents give no grid reference, easting and northing, or coordinates,** you may make up to two web searches for an official record of the same site that does: the Environment Agency's or Natural Resources Wales's permit documents for it, the Planning Inspectorate's case page, or the council's planning application record. Use only documents from a regulator, a council, a court or a government department. Do not use maps, encyclopaedias, company websites, property listings or news reports for the location, and do not convert or estimate anything yourself.

**Write** `result.csv` in the folder you are told to use, with Python's csv module, one row per task (more than one only if the documents give two different references for the site), columns:

`task_id, site_id, location_kind, value_as_written, postcode, refers_to, url, page, short_quote, notes`

- `location_kind`: grid_reference, easting_northing, lat_lon, address_postcode, address_only, not_found or could_not_open.
- `value_as_written`: exactly as the document prints it.
- `postcode`: if the document gives one for the site.
- `refers_to`: site, installation, site centre, application site, emission point, or other (say what).
- `url`: the document you read it from (one of the listed documents, or the official record you found).
- `page`: page or section.
- `short_quote`: at most 25 words, copied exactly, containing the value.
- `notes`: anything that would help someone check it, in plain words. Do not name software or tools.

If a document cannot be opened, try the next one listed; if none opens, write could_not_open. Neutral wording throughout. Then reply with a short summary: how many sites have a grid reference or coordinates, how many only an address, and how many nothing.
