# Climate TRACE handover: datacenters as a facility type

Prepared 2026-10-21 by the Compute Ledger. Data CC BY 4.0. Everything here traces to a public record or to a file in this folder. The package was reviewed hostilely twice before sending; both reviews are included unedited (review_of_this_handover.md, review_2_final.md) with the changes made in response.

| File | What it is |
|---|---|
| `datacenters_emissions_seed.csv`, `datacenters_ownership_seed.csv` | 96 sites in your v5.11.0 asset column order (78 with coordinates, 28 with permit MW). Emissions fields empty by design. |
| `VIRGINIA.md`, `va_permits_resolved.csv`, `va_reread_comparison.csv`, `va_reread_decisions.csv`, `VIRGINIA_REREAD_REPORT.md` | All 183 Virginia DEQ datacenter air permits, read twice by independent methods, every disagreement resolved against the text: 182 sites, 13,973 units, 33,693 MW permitted standby. `va_permits.csv` and `va_generator_rows.csv` are the superseded first reading, kept for the record. |
| `TEXAS.md`, `tx_permits.csv`, `tx_index_rows.csv`, `tx_unmatched_tceq_packages.csv` | 153 Comptroller-registered Texas sites against TCEQ's pending-application indexes: 17 verified matches, 12 with coordinates, and a finding that issued permits leave the public index. |
| `ireland_sites.csv`/`.json`, `ireland_regional_check.md` | 40 Irish sites from EPA licences, ETS permits and planning appeals, 22 located from grid references in the documents; the national metered total as a table of utilisation bounds across redundancy assumptions. |
| `dedicated_supply.csv`/`.json`, `dedicated_supply_method.md` | 43 sites or clusters: how electricity actually arrives per the record, with the operator's claim beside it. 30 rows document-grade, 13 press-only and flagged. |
| `CLIMATE_TRACE_SERIES.md`, `climate_trace_matches.csv`, `climate_trace_matched_plants_monthly.csv`, `virginia_nearest_generation.csv`, `climate_trace_top_assets.csv` | Your 5.11.0 USA estimates (pulled 21 Oct 2026, Jan 2025 to Jul 2026) matched to the plants our dockets name, with your confidence; monthly series; and for 126 Virginia permit sites the nearest asset in your inventory. |
| `attribution_method.md` | The method for your reviewers: your facility Scope 2 pattern plus one field, documented dedicated supply. |
| `datacenters_register_backlog_unlocated.csv` | Register-identified sites awaiting extraction (now superseded for Virginia). |

Repository with pipeline, registry of 117 entries in 40 countries, three receipts and method: https://github.com/kn0wledgebfre3-sys/compute-ledger
