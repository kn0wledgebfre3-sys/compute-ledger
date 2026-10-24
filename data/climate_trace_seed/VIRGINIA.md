# Virginia, extracted and independently re-read, 2026-10-21

Source: Virginia DEQ statewide list of issued datacenter air permits (183 registrations) and each permit PDF, downloaded by browser because the DEQ site refuses scripted downloads.

## Two readings

1. The pipeline (pipeline/) read the 183 downloaded files by regex over extracted text (182 permits; one file, saved as 5.pdf, is an 'Access Denied' page): 153 sites with a generator total, summing to 19,186 MW; three permits returned impossible totals and were nulled.
2. An independent second reader, sharing no code with the pipeline, read every PDF again (table parser, prose parser, then a manual read of every permit's equipment section with hand re-summation), then compared: 24 permits agree, 22 differ slightly, 107 disagree, 29 the pipeline had nulled or missed. Every disagreement was resolved against the permit text with a one-line reason (va_reread_comparison.csv, va_reread_decisions.csv).

The pipeline was wrong, mostly low, in 129 permits. One systematic bug explains most of it: the first data row after each equipment-table header was dropped (70 permits). Others: model years in parentheses read as unit counts (the three "impossible" permits), reference-ID ranges not expanded, de-rate and alternate-model lines counted as extra units. The second reader's own traps (a comma inside parentheses, "(N units)" phrasing, a duplicate listing) were caught by hand and are documented.

## The pipeline, fixed (2026-10-22)

The extractor has since been rewritten to fix every error pattern the second reading found, generically and without special-casing any permit. Run against the 182 permit PDFs it now agrees with the resolved figures on 178 of 182 permits, with none disagreeing; all 114 permits it rates high confidence agree. The four exceptions: two scanned permits whose text layer lost a cell or row (2.3 MW between them, rated low confidence), and two that state engine horsepower but no kW, where the pipeline leaves MW blank rather than infer it. Per-permit results: va_extraction_vs_resolved.csv. Because the fix was tested against the second reading's resolved figures, this agreement shows the pipeline now reproduces them; it is not a third independent reading.

## Resolved fleet

**182 permits · 13,973 permitted standby generator units · 33,693 MW** (177 permits high confidence, 5 medium). Two pairs of permits give the same site address (43831 Devin Shafron Drive: 73355 and 73868, the latter a 2011 permit for one 0.75 MW portable unit that may also be in 73355's inventory; 7471 Bear Wallow Road: 74198, Amazon, and 74201, Microsoft). Registration 74331 has no downloadable PDF (the list's link failed), so 182 of the list's 183 registrations are read; row '5' in the comparison files is the saved 'Access Denied' page, not a registration. Median site 129 MW; largest 1,331 MW (QTS Richmond, 544 units). Site-average unit size 0.4 to 3.7 MW, median 2.5 MW; most units are 2.0 to 3.0 MW; individual units run from 250 kW. Excluding 51 transitory units: 33,587 MW. 2,913 units are permitted as non-emergency (SCR-controlled, demand-response capable). Residual uncertainty is convention (alternates, standby vs prime rating, de-rates), giving a band of roughly 33.4 to 33.9 GW.

Dominion Energy reported about 40 GW of datacenter capacity 'in various stages of contracting' as of December 2024 (company statement, via Data Center Dynamics; not an SCC filing). Standby is sized to full design load with redundancy, so 33.7 GW permitted implies a design load of roughly 28-33 GW under N+1 and roughly 17 GW under 2N; permitted is not built, many permits cover phases not yet constructed, and the 40 GW is one utility's pipeline while DEQ permits cover the state. The two figures are of the same order; the first reading's 'half' was an artefact of the extraction bug.

## Coordinates

The 21 October run geocoded the address the first reading took from each permit (`va_geocodes.csv`). For thirteen permits that address was the permittee's mailing address (for example Amazon's at 13200 Woodland Park Road, Herndon), not the site. A site is therefore placed only where the geocoded address is the site address resolved by the second reading and the geocoder matched the address, not just the street: 102 permits. The other 81 are in `datacenters_register_backlog_unlocated.csv` with their resolved MW and site address, ready for a geocoder.

## Files

va_permits_resolved.csv (final per-registration figures, confidence, basis); va_reread_comparison.csv (both readings and the resolution per registration); va_reread_decisions.csv (the 99 hand decisions); VIRGINIA_REREAD_REPORT.md (method, error patterns, the three nulled permits, the ten spot-checks); va_permits.csv and va_generator_rows.csv (the pipeline's first, defective reading, kept for the record); va_extraction_vs_resolved.csv (the fixed pipeline against the resolved figures); va_geocodes.csv (every geocode with the address it was given); virginia_nearest_generation.csv (Climate TRACE context: for each located permit site, the nearest asset in Climate TRACE's inventory).


## Addendum, 2026-10-23: what the generators emitted

EPA's 2023 National Emissions Inventory lists 27 Virginia datacenter facilities with 393 tons of NOx, 21 of them matched to a registration number in this list; it reports emissions only, not hours or fuel. The file is `va_nei_generator_emissions.csv` and the reading is in `METERED.md`. Converting tons to hours needs each permit's per-unit NOx rate, which the permits state and the extractor does not yet read (roadmap).


## Addendum, 2026-10-23: what the utilities file as actual demand

Dominion's 20-year datacenter forecast to PJM (29 September 2026): billing demand 2,767 MW (2022), 3,183 (2023), 3,636 (2024), 4,237 MW (2025), 4,838 forecast (2026); 55 companies connected, about 500 metered accounts, billing peak 4.8 GW as of August 2026, about 54 GW under contract. Its January 2026 letter to PJM: 2025 coincident peak 4 GW, 47 GW under contract. NOVEC (same date): 75% of energy sales from datacenters, 88 buildings, about 1,750 MW, coincident peak 1,384 MW in 2025. So about 5.6 GW drew power in 2025 against 33.7 GW permitted standby. No filing gives GWh; Dominion's 10-K states 28% of Virginia Power sales in 2025 (company statement). The 40 GW 'in various stages of contracting' above (December 2024) is superseded by the filed 47,045 MW (July 2025) and 'approximately 54GW' (August 2026). File: `va_datacenter_class_demand.csv`; entry `us-va-dominion-datacenter-demand-filed-2026`.

## Addendum, 2026-10-23: a second geocode run, and seven site addresses corrected

The 81 unplaced permits were geocoded again with the US Census geocoder, one address at a time, on the site address the permit's "located at" clause gives (`va_geocodes_2026-10-23.csv`, with the query and the geocoder's matched address for every row). A point is accepted under the same rule as before: the geocoder matched the site address at house-number level. 23 permits are now placed, so 125 of the 182 are located. The Census points are interpolated along the street's address range, not building points. Four matches are held back: three rated low (52173, whose site address could not be confirmed in the permit text; 74306, a wide address range; 74269, where the geocoder dropped the street's "SE") and 74080, whose permit covers seven buildings on three streets while the point places one. The other 54 permits have no accepted point: most are on new Loudoun and Prince William streets that the Census address data does not yet cover, three were rejected because the geocoder matched another street or the permit gives no street address, and four permits give no usable site address. County address points would place most of them.

Checking the addresses against the permit text found seven permits whose resolved site address was the permittee's mailing address. They are corrected in `va_permits_resolved.csv`: 52299 (8851-B Park Central Drive, Richmond, not the 8801 mailing address), 74147 (21830 Uunet Way, Ashburn), 73170 (the Exodus Communications DC1 facility in Herndon; the permit gives no street address), and four Microsoft permits in Mecklenburg County whose sites are at La Crosse (52973), 2 Butts Street, South Hill (53071), the intersection of US 58 and Ridge Road, Boydton (53072), and northwest of Highway 92 and Butler Farm Road, Chase City (53198), not Microsoft's office at 101 Herbert Drive. The permits' MW are unchanged.
