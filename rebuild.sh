#!/usr/bin/env bash
# Rebuild every generated file from its sources, in dependency order, then run the checks.
set -euo pipefail
cd "$(dirname "$0")"
python3 pipeline/build_metered.py > /dev/null
python3 pipeline/build_handover_assets.py > /dev/null
python3 pipeline/build_measurements.py > /dev/null
python3 pipeline/validate_measurements.py
python3 -I pipeline/build_chain.py | tail -1
python3 -I pipeline/build_checks.py
python3 -I site/build_page.py | tail -1
python3 -I site/build_sites.py
bash ci_local.sh | tail -1
