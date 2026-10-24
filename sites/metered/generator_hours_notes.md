# From tons to hours: what the generators actually ran

EPA's emissions inventory gives each Virginia datacenter facility's NOx in tons a year (`va_nei_transcribed.csv`) but no hours. Each DEQ permit gives every generator's rating and its permitted NOx emission rate, and usually an annual hour limit per unit. Together they give the hours.

**Intake.** `va_permit_unit_rates.csv`, one row per group of identical units in a permit: count, rating each, NOx rate each (as the permit states it: g/kW-hr, g/hp-hr or lb/hr), the hour limit, the permit's URL and condition number, and the phrase quoted. The resolved permit table (`data/climate_trace_seed/va_permits_resolved.csv`) already gives counts and ratings; this file adds the rates.

**The arithmetic (basis `derived`, formula in `metric_detail`).**
full-load-equivalent hours per unit = inventory NOx (lb) / sum over units of (NOx rate x rating), with 1 short ton = 2,000 lb and 1 g = 0.0022046 lb.
It is an equivalent, not a log: generators run tests at part load, where the rate per hour differs; a facility that ran some units for long and others not at all gives the same number as all units for a short time. The row says so. Compare it with the permit's hour limit (usually 500 hours a year for emergency units, less for testing).

**Where it lands.** `metric` `generator_hours` ("at least N hours", qualifier lower_bound) and the share of the permit's facility-wide NOx limit, `subject_type` site, `basis` `derived`, period the inventory year. `pipeline/build_measurements.py` recomputes each figure from `va_permit_unit_rates.csv` and the inventory and rejects any that differ from `va_generator_hours.csv`, the reviewed table with each facility's match quality and caveats.

**Status (2026-10-24).** 21 permits transcribed (137 engine groups; counts and MW agree with `va_permits_resolved.csv`; a second reading of seven permits found no differences). 20 facilities have figures; 74120 is excluded because the permit covers VA3 to VA7 and the inventory facility is VA2. Where a permit sets two hourly limits (engines with SCR), the higher is used so the result stays a minimum. Several permits on disk predate or postdate the inventory year; the caveats give the effect. Actual run hours need DEQ's logs, by records request (`review/RECORDS_REQUESTS.csv`).
