# Where the UK sites are, read twice (17 November 2026)

**What was read.** For each of the 67 UK sites, the documents the ledger already cites for it: permits and decision documents of the Environment Agency and Natural Resources Wales, planning decisions, officer reports and directions. Readers copied where each document places the site: an Ordnance Survey grid reference, an easting and northing, a latitude and longitude, or an address (`briefs/BRIEF_locations.md`, `readers/tasks_*.csv`). Where the listed documents gave no grid reference, a reader could search twice for an official record of the same site that does, such as the permit issued with a decision document. Readers were not to take a location from a news report or a company page, nor to convert or estimate anything.

**How it was checked.** Two readers read each third of the sites independently (`readers/first_reading_*.csv`, `readers/second_reading_*.csv`). A site is placed where both readings give the same point, within 100 m or within the square a shorter grid reference names. In fact, every agreed pair is the same reference character for character. Grid references and eastings and northings were converted to WGS84 by `pipeline/osgb.py`. It follows the Ordnance Survey's published method, is tested on the Ordnance Survey's worked example, and is good to about 5 m. Each point was also checked against the town its documents name.

**What entered the ledger.** 43 sites now have coordinates in `sites/topics/uk/sites.csv`, and each site's notes give the reference and the document it came from.

- 35 come from the Environment Agency's own permits, decision documents and notices.
- 5 come from the applicants' reports that the Environment Agency published with their applications: Romford, Hemel Hempstead (NTT), Hayes (Amazon), Harlow and Cheshunt. Both readers took the same reports.
- 3 come from planning records:
  - South Gyle, from the Scottish Government's appeal case page;
  - Wapseys Wood, from the applicant's request for a direction;
  - Dartford, from the applicant's supporting statement published with the direction.
- For three sites the point is a single building rather than the whole site: Equinix's Slough campus (data centre LD4), NTT's Hemel Hempstead campus (the Campus data centre) and Wapseys Wood (building DC 02). Each site's notes say which building.

**Not placed, with the reason in `check_result.csv`.**

- **Digital Realty Redhill:** both readers copied the same grid reference, TQ 52865 15146, from the decision document. It falls about 45 km from the Redhill postcode printed in the same sentence, in East Sussex, so the site is left off the map until the permit's site plan is read.
- **Manor Farm, Poyle:** only one reading found an easting and northing.
- **18 sites where the documents give an address:** the ledger does not convert addresses to coordinates. Where the address comes from the site's own permit, decision or report, it is now in the site's notes.
- **4 sites where nothing was found:** Newport (Celtic Technology Centre), whose council document could not be opened; and Elsham, Skelton Grange and Canning Town, which are known only from news reports and a landowner's announcement.

**Limits.**

- Both readers read the documents as text extracted from the PDFs, not from the printed pages.
- A grid reference marks the point the document gives, which may be the centre of the site, an installation, or one building. It is not a boundary.

**Placed later.** Digital Realty Redhill (from the applicant's application form) and Manor Farm, Poyle (from the appeal form) were placed in the second pass of `review/site_locations_2_2026-11-17/`, where both were read twice.
