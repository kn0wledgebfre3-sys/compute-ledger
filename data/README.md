# data/

| Folder | What it holds |
|---|---|
| `climate_trace_seed/` | The handover package, and the ledger's machine-readable core: `measurements.csv` (every figure, one row, one vocabulary), `site_register.csv`, `entity_register.csv`. Built by the scripts in `pipeline/`; CI fails if a committed file differs from a rebuild. |
| `YYYY-MM/` | Monthly scraper outputs (grid queues, EIA, NESO, the Climate TRACE cross-check), committed by `.github/workflows/monthly-scrape.yml`. |
| `pulls/YYYY-MM-DD/` | Weekly pulls (EPA emissions inventory, Irish annual reports, benchmarking portals, watched pages), opened as a pull request by `.github/workflows/weekly-pulls.yml` for a person to review. |
| `watch/` | What each watched page listed at the last run, so the next run reports only what is new. |
