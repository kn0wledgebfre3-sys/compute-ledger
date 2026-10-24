# The chain, edge by edge

The ledger was built to trace one chain: mine, refiner, fab, chip buyer, datacenter, the power, fuel and water it draws, and the hardware's end. The figures live in `data/climate_trace_seed/measurements.csv`; the links between parties live here. One row of `edges.csv` is one link that a document states, read as "from *relation* to".

`python3 pipeline/build_chain.py` checks every row and writes `data/chain/edges.csv` (with a content-hashed `edge_id` and the side) and `data/chain/summary.json`, which lists the legs that still have no edge. CI runs it on every push.

## Columns

| Column | What goes in it |
|---|---|
| `leg` | One of: `mine_to_refiner`, `refiner_to_maker`, `fab_to_buyer`, `memory_to_maker`, `packaging_to_maker`, `assembly_to_buyer`, `chips_across_borders`, `power_to_site`, `fuel_to_site`, `water_to_site`, `site_to_tenant`, `ownership`, `hardware_to_end_of_life`. |
| `from_type`, `to_type` | `site` (an id in `data/climate_trace_seed/site_register.csv`), `entity` (an id in `sites/entity_register.csv`), `entry` (a ledger entry id), or `named` (a party not yet in a register; `*_id` empty). |
| `from_id`, `from_name`, `to_id`, `to_name` | The ids, and the names as the document gives them. |
| `relation` | From `relations` in `pipeline/measurement_vocab.json`: `mines_for`, `refines_for`, `fabricates_for`, `supplies_memory_to`, `packages_for`, `assembles_for`, `ships_to`, `supplies_power_to`, `contracts_power_from`, `supplies_water_to`, `supplies_fuel_to`, `hosts_compute_for`, `leases_site_to`, `receives_end_of_life_from`, `owns`, `operates`. |
| `period_start`, `period_end` | When the link held, if the document says; ISO dates. A planned link has none and says "planned" in notes. |
| `basis` | From the vocabulary's bases. `company_statement` makes the edge a claim; everything else is a record. |
| `document_title`, `document_url`, `publisher`, `document_date` | The document that states the link. |
| `quoted_line` | The phrase in the document that states the link, copied exactly. Required. |
| `entry_id` | The ledger entry that discusses it, if any. |
| `notes`, `second_read` | What the reader needs to know; whether a second reading confirmed it. |

## Where each leg's edges will come from

| Leg | Record | Status |
|---|---|---|
| `mine_to_refiner` | Responsible Minerals Initiative smelter lists; mine-to-smelter disclosures in conflict-minerals reports where filers give them | waiting (`review/INTAKE.csv`) |
| `refiner_to_maker` | SEC Form SD and conflict-minerals reports, which list smelters and refiners for tin, tantalum, tungsten and gold | live: 12 filers' reports as figures (`registry/supply_chain.json`); Nvidia's and Intel's tantalum and tungsten smelters as 75 sites and 139 links. The reports print no RMI smelter ids, so sites are named as printed; joining them to RMI ids needs the RMI list. |
| `fab_to_buyer` | Nvidia's, AMD's, Broadcom's and Intel's 10-Ks naming their foundries; TSMC's 20-F customer concentration (unnamed) | live: 8 links, all company statements; no filing links a buyer to a specific fab |
| `memory_to_maker` | Nvidia's 10-K naming its memory suppliers | live: 3 links (SK hynix, Micron, Samsung) |
| `packaging_to_maker` | AMD's and Broadcom's 10-Ks naming their assembly, test and packaging houses | live: 8 links |
| `assembly_to_buyer` | Chip and server makers' 10-Ks naming their contract manufacturers | live: 3 links (Hon Hai, Wistron, Fabrinet for Nvidia); Dell and Supermicro name none |
| `chips_across_borders` | Taiwan Ministry of Finance exports by destination; US imports by port. The series ends at the country and port, which is itself a finding. | waiting |
| `power_to_site` | Utility-commission decisions, utility updates, permits for on-site generation | live |
| `fuel_to_site` | Pipeline certificates (e.g. Rochester Lateral), gas supply agreements in dockets, utility updates | live: 9 links (Wisconsin's Rochester Lateral, MLGW gas to xAI, Homer City's suppliers, Energy Transfer to Meta's Louisiana plants, Equinix DB5's mains gas); most fuel permits name no supplier |
| `water_to_site` | Water-rights registers, municipal supply agreements, annual environmental reports | live: 21 links (Ireland's 11 licensed sites; Memphis, Phoenix, The Dalles, West Des Moines, Racine, Loudoun's reclaimed water, Cerrillos, Querétaro) |
| `site_to_tenant` | 10-K leases and hosting agreements (claims), interconnection records | live |
| `ownership` | Company registries, SEC exhibits | live: 2 links (AMD and Tongfu as owners of the packaging joint ventures) |
| `hardware_to_end_of_life` | R2v3 and e-Stewards facility lists, companies' circularity disclosures | waiting |
