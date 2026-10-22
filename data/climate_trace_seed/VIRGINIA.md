# Virginia, extracted and independently re-read, 2026-10-21

Source: Virginia DEQ statewide list of issued datacenter air permits (183 registrations) and each permit PDF, downloaded by browser because the DEQ site refuses scripted downloads.

## Two readings

1. The pipeline (pipeline/) read all 183 PDFs by regex over extracted text: 153 sites with a generator total, summing to 19,186 MW; three permits returned impossible totals and were nulled.
2. An independent second reader, sharing no code with the pipeline, read every PDF again (table parser, prose parser, then a manual read of every permit's equipment section with hand re-summation), then compared: 24 permits agree, 22 differ slightly, 107 disagree, 29 the pipeline had nulled or missed. Every disagreement was resolved against the permit text with a one-line reason (va_reread_comparison.csv, va_reread_decisions.csv).

The pipeline was wrong, mostly low, in 129 permits. One systematic bug explains most of it: the first data row after each equipment-table header was dropped (70 permits). Others: model years in parentheses read as unit counts (the three "impossible" permits), reference-ID ranges not expanded, de-rate and alternate-model lines counted as extra units. The second reader's own traps (a comma inside parentheses, "(N units)" phrasing, a duplicate listing) were caught by hand and are documented.

## Resolved fleet

**182 sites · 13,973 permitted standby generator units · 33,693 MW** (177 sites high confidence, 5 medium; 2 further registrations unreadable, one of which has no PDF). Median site 129 MW; largest 1,331 MW (QTS Richmond, 544 units). Site-average unit size 0.4 to 3.7 MW, median 2.5 MW; most units are 2.0 to 3.0 MW; individual units run from 250 kW. Excluding 51 transitory units: 33,587 MW. 2,913 units are permitted as non-emergency (SCR-controlled, demand-response capable). Residual uncertainty is convention (alternates, standby vs prime rating, de-rates), giving a band of roughly 33.4 to 33.9 GW.

Dominion Energy reported about 40 GW of datacenter capacity 'in various stages of contracting' as of December 2024 (company statement, via Data Center Dynamics; not an SCC filing). Standby is sized to full design load with redundancy, so 33.7 GW permitted implies a design load of roughly 28-33 GW under N+1 and roughly 17 GW under 2N; permitted is not built, many permits cover phases not yet constructed, and the 40 GW is one utility's pipeline while DEQ permits cover the state. The two figures are of the same order; the first reading's 'half' was an artefact of the extraction bug.

## Files

va_permits_resolved.csv (final per-registration figures, confidence, basis); va_reread_comparison.csv (both readings and the resolution per registration); va_reread_decisions.csv (the 94 hand decisions); VIRGINIA_REREAD_REPORT.md (method, error patterns, the three nulled permits, the ten spot-checks); va_permits.csv and va_generator_rows.csv (the pipeline's first reading, kept for the record); climate_trace_virginia_bbox_monthly_by_fuel.csv and virginia_nearest_generation.csv (Climate TRACE context).
