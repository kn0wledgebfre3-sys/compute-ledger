#!/usr/bin/env bash
# One command: ./run_all.sh            (live: fetches DEQ/TCEQ pages and PDFs, geocodes, merges, validates)
#              ./run_all.sh --fixture  (offline: runs every step on fixtures/, writes out_fixture/)
# Extra arguments after the flag are passed to va_deq_permits.py (e.g. --limit 10, --no-search, --pdf-dir DIR).
set -euo pipefail
cd "$(dirname "$0")"
MODE=live; OUT=out; FLAG=""
if [[ "${1:-}" == "--fixture" ]]; then MODE=fixture; OUT=out_fixture; FLAG="--fixture"; shift; fi
PY=${PYTHON:-python3}
echo "== mode: $MODE  out: $OUT  ($(date -u +%FT%TZ))"
$PY -c "import requests, pandas, pdfplumber" 2>/dev/null || { echo "missing packages: pip install -r requirements.txt"; exit 2; }
echo "== 1/5 Virginia DEQ permits";   $PY va_deq_permits.py   $FLAG --out "$OUT" "$@"
echo "== 2/5 Texas TCEQ permits";     $PY tx_permits.py       $FLAG --out "$OUT"
echo "== 3/5 geocode";                $PY geocode.py          $FLAG --out "$OUT"
echo "== 4/5 merge + Climate TRACE";  $PY merge_to_handover.py $FLAG --out "$OUT"
echo "== 5/5 validate";               $PY validate_outputs.py "$OUT"
echo "== done. Outputs in $OUT/: va_permits.csv tx_permits.csv geocoded.csv seed_sites_v2.json climate_trace/*.csv handover_summary.json"
