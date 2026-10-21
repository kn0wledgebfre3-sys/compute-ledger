# Climate TRACE handover: datacenters as a facility type

Prepared 2026-10-21 by the Compute Ledger. Data CC BY 4.0. Everything here traces to a public record.

| File | What it is |
|---|---|
| `datacenters_emissions_seed.csv` | Sites in your v5.11.0 asset-emissions column order. Emissions fields empty by design; `other1`-`other10` carry permit MW, cooling, status, source URL, operator claim, ledger gap. |
| `datacenters_ownership_seed.csv` | Same sites, your 19-column ownership file. |
| `ireland_sites.csv` / `.json` | 40 Irish sites from EPA licences, EU ETS permits and planning appeals; 22 located, mostly from grid references in EPA documents; 16 operating sites with permitted standby MW (licence cap and sum-of-units both carried). |
| `ireland_regional_check.md` | The metered national total (CSO, 7,663 GWh, 2025) as the test per-site estimates must pass, worked as a table of bounds across redundancy assumptions; the earlier single-factor conclusion is withdrawn and the revision is marked. |
| `dedicated_supply.csv` / `.json` | 43 sites or clusters: how their electricity is actually supplied; 30 rows on a regulator, court, grid-operator or statutory document, 13 on press or operator statements and flagged. Six rows reclassified after review (`review_note`). |
| `dedicated_supply_method.md` | Categories and the alpha rule. |
| `attribution_method.md` | The method, written for your reviewers. Your facility Scope 2 approach plus one field: documented dedicated supply. Five worked rows were drafted and withdrawn after review (see below) because they set load equal to supply MW. |
| `review_of_this_handover.md` | An independent hostile review of the package as first drafted, unedited. Changes made in response: Ireland check rewritten as bounds; six supply rows reclassified; worked rows withdrawn; brief rewritten. |
| `datacenters_register_backlog_unlocated.csv` | 325 register-identified sites (Virginia DEQ air permits, Texas Comptroller) awaiting permit extraction. A pipeline for this exists and has been tested on real permits. |

Full repository, method, sources and the ledger of 117 entries across 40 countries available on request.
