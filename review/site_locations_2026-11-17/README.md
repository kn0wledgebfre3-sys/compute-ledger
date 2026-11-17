# Where the unplaced sites are, read twice (17 November 2026)

**What was read.** 185 sites without coordinates, outside the three lists that need other routes (the US energy-benchmarking filings and Virginia permits, which give street addresses for the geocoder, and the minerals refiners, whose lists give only a country): crypto-mining and conversion sites, chip fabs, nuclear plants, and datacentres in Ireland, Singapore, the UK and Texas. For each, two readers independently read the documents the ledger cites and copied where they place the site: coordinates, a street address, a description, or only a town (`briefs/BRIEF_locations.md`, `readers/`). Readers could search for an official record of the same site with coordinates (a regulator's or agency's record, or the operator's securities filing).

**What was found.**

- **Coordinates: none that both readers found.** Most of these sites' documents are annual reports, which name a town or county ("Rockdale, Texas", "Kumamoto Prefecture"), and permits that give an address.
- **Street addresses that both readers give: 24 sites.** The ones not already in a site's notes are now added there through `sites/locations/addresses.csv` (18 sites): Irish datacentres from their EPA licences and planning cases, UK sites from their permits and decisions. One is in the US, Bitdeer's Knoxville site from the operator's 20-F. It is in `sites/locations/addresses_read.csv`, so the address script will geocode it.
- **Leads from one reading only**, kept in `check_result.csv` and the readers' files for the next round:
  - For Digital Realty Redhill, the applicant's permit form prints TQ 28670 51462, which falls in Redhill. The decision document prints TQ 52865 15146, which does not; the site's notes say so.
  - TCEQ's notice for Fermi America's power plant gives a map position, though the notice says the map is "not part of the application".
  - Memphis Light, Gas and Water gives 5420 Tulane Road for the xAI site.
  - Texas building-project records give 557 CR 3610, Whitney, for CyrusOne DFW10.
  - Kentucky Power's brief gives 23250 US Highway 23, Louisa, for the Ebon site.

**Why so little.** Many of the listed documents could not be opened directly from where the readers worked. Each could be reached only through a web search, and the searches set for the pass, shared by all the readers, ran out partway through. So most sites had no search for an official record with coordinates. That held for the 19 Texas sites with no document at all, for the nuclear plants, whose NRC documents could not be opened, and for the Virginia sites known from EPA's inventory. These are listed in `ROADMAP.md`, to be read again with fresh searches.

**Limits.**

- Several filings were read from the same document on the operator's own investor site, where the SEC copy could not be opened. Each row's url says which copy was read.
- Long filings were read in part, and each row's notes say how much.
