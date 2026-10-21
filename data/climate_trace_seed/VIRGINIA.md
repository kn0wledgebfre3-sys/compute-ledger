# Virginia, extracted 2026-10-21

Source: Virginia DEQ statewide list of issued datacenter air permits (183 registrations) and each permit PDF.
Result: 153 sites with permitted standby generator capacity; fleet total 19,186 MW; median 65 MW; largest 788 MW; 154 street addresses; 127 geocoded.
Three permits returned implausible totals (>2 GW) and were nulled by validation for manual read (52221, 52403, 73860).
Dominion Energy reported about 40,000 MW of contracted datacenter capacity (SCC filings, Dec 2024). Permitted standby is sized to full site load, so the permits bound what physically exists at roughly half the contracted figure.
Climate TRACE: release 5.11.0 USA asset estimates summed to 2025, matched by name to the generators the ledger's regulatory records name (climate_trace_matches.csv); and for 175 geocoded permit sites, the nearest Climate TRACE generation asset within 15 km, 104 found (virginia_nearest_generation.csv). The second file is context, not attribution.
Files: va_permits.csv (one row per registration), va_generator_rows.csv (857 generator units), handover_summary.json.
