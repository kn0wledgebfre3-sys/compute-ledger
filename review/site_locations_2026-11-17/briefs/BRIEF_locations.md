# Brief: where each site is, as an official document states it

You are a reader for a public ledger built only from public documents. The ledger holds sites that are not yet on its map: crypto-mining and datacentre sites, chip fabs, nuclear plants, and datacentres in Ireland, Singapore, the UK and Texas. Your job is to copy, for each site in your task file, where an official document places it. You are not asked to work anything out.

**For each task** (one site), open the documents listed in `documents` (separated by " ; ") and look for where they place the site, in this order of preference:

1. **coordinates**: latitude and longitude (decimal or degrees, minutes and seconds), or a grid reference, easting and northing, or UTM coordinates, with the system named if the document names it (WGS84, NAD83, British National Grid, Irish Grid, Irish Transverse Mercator, UTM zone);
2. the site's **street address** (house number, street, town, postcode or ZIP);
3. a **description** of where the site is ("5 miles north-east of Paducah on FM 1234", "Lot 12, Tuas South Avenue 3");
4. only the town or county.

**Make sure it is the site.** Documents also give a company's mailing address or head office, the address of a lawyer or consultant, a county seat, a weather station, a stack or an outfall. Record those only if nothing for the site itself is given, and then say what it is in `refers_to`. A company's head office is never the site.

**If the listed documents do not give coordinates,** or no document is listed, you may make up to two web searches (three where no document is listed) for an official record of the same site that does. That can be:
- a regulator's or agency's record: the US Nuclear Regulatory Commission; EPA, including its Facility Registry Service and ECHO facility reports; a state environmental agency such as TCEQ; a public utility commission; the US Energy Information Administration; Ireland's EPA, An Bord Pleanála or a county council; Singapore's or another government's agencies; a court;
- the operator's own filing with a securities regulator (10-K, 20-F, 40-F, annual information form, prospectus), for the site's address or coordinates only.

Do not use news reports, encyclopaedias, maps, company web pages or property listings for the location. Do not convert or estimate anything yourself. `what_the_ledger_notes` says what the ledger already knows about the site; use it to identify the site, not as a source.

**Write** `result.csv` in the folder you are told to use, with Python's csv module, one row per task (more than one only if the documents give two different locations for the site), columns:

`task_id, site_id, location_kind, coordinate_system, value_as_written, street_address, refers_to, url, page, short_quote, notes`

- `location_kind`: lat_lon, grid_reference, easting_northing, utm, street_address, description, locality_only, not_found or could_not_open.
- `coordinate_system`: as the document names it, or "not stated".
- `value_as_written`: the coordinates or description, exactly as printed.
- `street_address`: the site's street address if the document gives one, even when it also gives coordinates.
- `refers_to`: site, plant, facility, building, application site, mailing address, head office, or other (say what).
- `url`: the document you read it from. `page`: page, section or table.
- `short_quote`: at most 25 words, copied exactly, containing the value.
- `notes`: anything that would help someone check it, in plain words. Do not name software or tools.

If a document cannot be opened, try the next one; if none opens and searching finds nothing, write could_not_open or not_found. Neutral wording throughout. Then reply with a short summary: how many sites have coordinates, how many a street address only, how many a description or locality only, and how many nothing.
