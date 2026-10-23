#!/usr/bin/env bash
# Run the same checks as .github/workflows/validate.yml, locally, before pushing.
set -euo pipefail
cd "$(dirname "$0")"
T="$(mktemp -d)"
python3 -I site/build_page.py | tail -1
if python3 -I site/build_page.py 2>&1 | grep -q PROBLEMS; then echo "registry problems"; exit 1; fi
git diff --quiet -- docs/ site/index.html || echo "note: docs/ changed by the build; commit it"
( cd scrapers && for s in ercot_large_load pjm_queue miso_spp_nyiso_queues eia_860_923 neso_demand climate_trace_match pull_nei pull_ie_aer pull_benchmarking watch_pages; do python3 $s.py --fixture --out "$T/out" 2>/dev/null >/dev/null || { echo "scraper $s failed"; exit 1; }; done; python3 cross_check.py --fixture --out "$T/out" >/dev/null 2>&1 )
cd pipeline
./run_all.sh --fixture > /dev/null 2>&1 || { echo "run_all fixture failed"; exit 1; }
python3 tx_fetch.py --fixture --out "$T/tx" > /dev/null 2>&1
cmp "$T/tx/tx_issued_sites.csv" ../data/climate_trace_seed/tx_issued_sites.csv
cmp "$T/tx/BROWSER_LIST.csv" ../data/climate_trace_seed/tx_browser_list.csv
python3 build_handover_assets.py --out "$T/assets" > /dev/null
for f in datacenters_emissions_seed.csv datacenters_ownership_seed.csv datacenters_register_backlog_unlocated.csv assets_summary.json; do cmp "$T/assets/$f" ../data/climate_trace_seed/$f; done
python3 build_metered.py --out "$T/metered" > /dev/null
for f in ireland_aer_metered.csv va_nei_generator_emissions.csv benchmarking_datacenters.csv public_power_loads.csv va_datacenter_class_demand.csv metered_summary.json; do cmp "$T/metered/$f" ../data/climate_trace_seed/$f; done
python3 build_measurements.py --out "$T/meas" > /dev/null
for f in measurements.csv site_register.csv entity_register.csv measurements_summary.json; do cmp "$T/meas/$f" ../data/climate_trace_seed/$f; done
python3 validate_measurements.py | tail -1
echo "all checks passed"
