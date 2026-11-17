# Where the unplaced sites are: second pass (17 November 2026)

**What was read.** The sites the first pass (`review/site_locations_2026-11-17/`) left without coordinates, where official records usually give them:
- the 20 Texas sites, from TCEQ's permit notices, the Texas Register and Texas building-project records;
- the 19 Irish sites, from EPA licence and greenhouse-gas permit documents and An Bord Pleanála's case documents;
- the planned nuclear sites (Cascade, Hermes 2, Oklo in Ohio, Loviisa), from NRC and Finnish documents;
- second readings of the leads the first pass found once: Redhill, Manor Farm, Ebon at Louisa, and xAI's Tulane Road site.

Two readers read each site independently (`briefs/BRIEF_locations.md`, `readers/`). Each was held to two searches per site.

**What entered the ledger.** Five sites are placed where both readings give the same point:
- **Fermi America** and the **VoltaGrid ABI-1 plant at Vantage Frontier**: the map position TCEQ's air-permit notice links for each site's power plant. The notice calls the map a public courtesy, not part of the application. The point is the power plant, not the datacentre buildings, and each site's notes say so.
- **Equinix DB1** in Citywest: the main-entrance grid reference in the EPA's 2020 greenhouse-gas permit for the same installation. The permit names no grid system; the values fit the Irish Grid.
- **Digital Realty Redhill**: TQ 28670 51462, from the applicant's permit application form. The decision document prints TQ 52865 15146, which falls about 45 km away; the site's notes keep both.
- **Manor Farm, Poyle**: the easting and northing on the appeal form published by Slough Borough Council.

**Addresses.** Street addresses both readers give are added to the notes of the sites that did not already carry one (`sites/locations/addresses.csv`). Four US ones join the geocoding queue: CyrusOne DFW10 at Whitney, Stream Houston I, TRG at Spring, and Ebon at Louisa. xAI's address, 5420 Tulane Road, is printed with no town, so it is noted but not geocoded.

**From one reading only**, kept in `check_result.csv` for a later reading:
- coordinates for Cascade, from an Army Corps letter attached to Energy Northwest's NRC filing;
- coordinates for Hermes 2, from Kairos's environmental report;
- coordinates for Goodnight, from the Spanish summary of TCEQ application 182880;
- coordinates for Kilby, from TCEQ's notice for Energy Forge One;
- ITM coordinates for Red Admiral, from the substation application form.

**Not found.** The other sites' documents give a town or a description only. Many Texas projects appear only in the Comptroller's list, which has no location field.
