# Virginia, extracted and independently re-read, 2026-10-21

Source: Virginia DEQ statewide list of issued datacenter air permits (183 registrations) and each permit PDF, downloaded by browser because the DEQ site refuses scripted downloads.

## Two readings

1. The pipeline (pipeline/) read the 183 downloaded files by regex over extracted text (182 permits; one file, saved as 5.pdf, is an 'Access Denied' page): 153 sites with a generator total, summing to 19,186 MW; three permits returned impossible totals and were nulled.
2. An independent second reader, sharing no code with the pipeline, read every PDF again (table parser, prose parser, then a manual read of every permit's equipment section with hand re-summation), then compared: 24 permits agree, 22 differ slightly, 107 disagree, 29 the pipeline had nulled or missed. Every disagreement was resolved against the permit text with a one-line reason (va_reread_comparison.csv, va_reread_decisions.csv).

The pipeline was wrong, mostly low, in 129 permits. One systematic bug explains most of it: the first data row after each equipment-table header was dropped (70 permits). Others: model years in parentheses read as unit counts (the three "impossible" permits), reference-ID ranges not expanded, de-rate and alternate-model lines counted as extra units. The second reader's own traps (a comma inside parentheses, "(N units)" phrasing, a duplicate listing) were caught by hand and are documented.

## The pipeline, fixed (2026-10-22)

The extractor has since been rewritten to fix every error pattern the second reading found, generically and without special-casing any permit. Run against the 182 permit PDFs it now agrees with the resolved figures on 178 of 182 permits, with none disagreeing; all 114 permits it rates high confidence agree. The four exceptions: two scanned permits whose text layer lost a cell or row (2.3 MW between them, rated low confidence), and two that state engine horsepower but no kW, where the pipeline leaves MW blank rather than infer it. Per-permit results: va_extraction_vs_resolved.csv. Because the fix was tested against the second reading's resolved figures, this agreement shows the pipeline now reproduces them; it is not a third independent reading.

## Resolved fleet

**182 permits · 13,990 permitted standby generator units · 33,733 MW** (175 permits high confidence, 7 medium), after the later permits for 13 registrations were read on 2026-10-24 (last addendum); the 21 October reading gave 13,973 units and 33,693 MW. Two pairs of permits give the same site address (43831 Devin Shafron Drive: 73355 and 73868, the latter a 2011 permit for one 0.75 MW portable unit that may also be in 73355's inventory; 7471 Bear Wallow Road: 74198, Amazon, and 74201, Microsoft). Registration 74331 has no downloadable PDF (the list's link failed), so 182 of the list's 183 registrations are read; row '5' in the comparison files is the saved 'Access Denied' page, not a registration. Median site 129 MW; largest 1,331 MW (QTS Richmond, 544 units). Site-average unit size 0.4 to 3.7 MW, median 2.5 MW; most units are 2.0 to 3.0 MW; individual units run from 250 kW. Excluding 51 transitory units: 33,627 MW. 2,913 units are permitted as non-emergency (SCR-controlled, demand-response capable). Residual uncertainty is convention (alternates, standby vs prime rating, de-rates), giving a band of roughly 33.4 to 33.9 GW.

Dominion Energy reported about 40 GW of datacenter capacity 'in various stages of contracting' as of December 2024 (company statement, via Data Center Dynamics; not an SCC filing). Standby is sized to full design load with redundancy, so 33.7 GW permitted implies a design load of roughly 28-33 GW under N+1 and roughly 17 GW under 2N; permitted is not built, many permits cover phases not yet constructed, and the 40 GW is one utility's pipeline while DEQ permits cover the state. The two figures are of the same order; the first reading's 'half' was an artefact of the extraction bug.

## Coordinates

The 21 October run geocoded the address the first reading took from each permit (`va_geocodes.csv`). For thirteen permits that address was the permittee's mailing address (for example Amazon's at 13200 Woodland Park Road, Herndon), not the site. A site is therefore placed only where the geocoded address is the site address resolved by the second reading and the geocoder matched the address, not just the street: 102 permits. The other 80 permits, and registration 74331 whose permit could not be downloaded, went to `datacenters_register_backlog_unlocated.csv` with their resolved MW and site address; the 2026-10-23 addendum below placed 23 more, leaving 57 permits and 74331 there.

## Files

va_permits_resolved.csv (final per-registration figures, confidence, basis); va_reread_comparison.csv (both readings and the resolution per registration); va_reread_decisions.csv (the 99 hand decisions); VIRGINIA_REREAD_REPORT.md (method, error patterns, the three nulled permits, the ten spot-checks); va_permits.csv and va_generator_rows.csv (the pipeline's first, defective reading, kept for the record); va_extraction_vs_resolved.csv (the fixed pipeline against the resolved figures); va_geocodes.csv (every geocode with the address it was given); virginia_nearest_generation.csv (Climate TRACE context: for each located permit site, the nearest asset in Climate TRACE's inventory).


## Addendum, 2026-10-23: what the generators emitted

EPA's 2023 National Emissions Inventory lists 27 Virginia datacenter facilities with 393 tons of NOx, 21 of them matched to a registration number in this list, plus 74086 matched by address on 2026-10-24 (not in the hours file: its NOx limits are not yet transcribed); it reports emissions only, not hours or fuel. The file is `va_nei_generator_emissions.csv` and the reading is in `METERED.md`. Minimum generator hours have since been computed for the 20 confident matches from each permit's per-engine NOx limits (`sites/metered/va_generator_hours.csv`; NTT's 74120 is excluded as a weak match).


## Addendum, 2026-10-23: what the utilities file as actual demand

Dominion's 20-year datacenter forecast to PJM (29 September 2026): billing demand 2,767 MW (2022), 3,183 (2023), 3,636 (2024), 4,237 MW (2025), 4,838 forecast (2026); 55 companies connected, about 500 metered accounts, billing peak 4.8 GW as of August 2026, about 54 GW under contract. Its January 2026 letter to PJM: 2025 coincident peak 4 GW, 47 GW under contract. NOVEC (same date): 75% of energy sales from datacenters, 88 buildings, about 1,750 MW, coincident peak 1,384 MW in 2025. So roughly 5.4 to 5.6 GW drew power in 2025 by our sum (Dominion's coincident peak or its billing demand, plus NOVEC's coincident peak) against 33.7 GW permitted standby. No filing gives GWh; Dominion's 10-K states 28% of Virginia Power sales in 2025 (company statement). The 40 GW 'in various stages of contracting' above (December 2024) is superseded by the filed 47,045 MW (July 2025) and 'approximately 54GW' (August 2026). File: `va_datacenter_class_demand.csv`; entry `us-va-dominion-datacenter-demand-filed-2026`.

## Addendum, 2026-10-23: a second geocode run, and seven site addresses corrected

The 81 unplaced permits were geocoded again with the US Census geocoder, one address at a time, on the site address the permit's "located at" clause gives (`va_geocodes_2026-10-23.csv`, with the query and the geocoder's matched address for every row). A point is accepted under the same rule as before: the geocoder matched the site address at house-number level. 23 permits are now placed, so 125 of the 182 are located. The Census points are interpolated along the street's address range, not building points. Four matches are held back: three rated low (52173, whose site address could not be confirmed in the permit text; 74306, a wide address range; 74269, where the geocoder dropped the street's "SE") and 74080, whose permit covers seven buildings on three streets while the point places one. The other 54 permits have no accepted point: most are on new Loudoun and Prince William streets that the Census address data does not yet cover, three were rejected because the geocoder matched another street or the permit gives no street address, and four permits give no usable site address. County address points would place most of them.

Checking the addresses against the permit text found seven permits whose resolved site address was the permittee's mailing address. They are corrected in `va_permits_resolved.csv`: 52299 (8851-B Park Central Drive, Richmond, not the 8801 mailing address), 74147 (21830 Uunet Way, Ashburn), 73170 (the Exodus Communications DC1 facility in Herndon; the permit gives no street address), and four Microsoft permits in Mecklenburg County whose sites are at La Crosse (52973), 2 Butts Street, South Hill (53071), the intersection of US 58 and Ridge Road, Boydton (53072), and northwest of Highway 92 and Butler Farm Road, Chase City (53198), not Microsoft's office at 101 Herbert Drive. The permits' MW are unchanged.

## Addendum, 2026-10-24: which permit each figure comes from

DEQ serves each permit only through the links on its list of issued data-center air permits, and refuses scripted downloads, so every Virginia figure cites that list, and its title names the registration and the date of the permit read. Compared with the list as retrieved on 2026-10-21, 13 of the permits read are not the latest action on the list for their registration (52629, 71804, 73200, 73240, 73370, 73643, 73670, 73717, 73977, 74079, 74156, 74190, 74265). Their figures stand as what those permits say, each row's notes give the later date, and the later permits are on `review/BROWSER_FETCH_LIST.csv` to be read.


## Addendum, 2026-10-24 (later): the 13 later actions, read

The later documents on DEQ's list for the 13 registrations above were downloaded in a browser and read twice (text layer and page images; OCR checked against the image). Five change the figures; `va_permits_resolved.csv` now holds the registration's current total, each row's `basis` says what was read, and each figure's notes in `measurements.csv` say what the later document showed.

| Registration | Before | After | What the later document is |
|---|---|---|---|
| 71804 | 8 units, 7.35 MW (2009) | 8 units, 8.595 MW | 2016-11-09 permit: all eight engines replaced; permittee now Meridian Science 7990, LLC |
| 73370 | 147 units, 316.98 MW (2013) | 165 units, 357.48 MW | 2017-08-23 permit for a new building, ACC10 (18 units, 40.5 MW), added to the 2013 permits for ACC2-ACC7 |
| 73670 | 143 units, 283.175 MW (2017) | 139 units, 274.675 MW | renewal Title V permit effective 2025-03-14; four units of the 2017 permit are absent without explanation |
| 73717 | 5 units, 4.275 MW (2009) | 8 units, 11.025 MW | 2019-05-29 permit (Zayo Group) for EG5-EG7; the 2009 units are taken as still permitted (if not: 3 units, 6.75 MW); medium confidence |
| 52629 | 92 units, 272 MW (2018) | unchanged | 2019-06-27 permit: SCR added on 36 units, hour and fuel limits added |
| 73200, 73977 | unchanged | unchanged | amendments (opacity; emission calculations) naming the same units |
| 74156, 74190, 74265 | unchanged | unchanged | the same permits already read; the dates recorded had been the completeness date or the date superseded, and are corrected |
| 73240 | unchanged | unchanged | the file is the permit dated 2024-09-20 already read; the list's 2024-09-24 appears to be a posting date |
| 73643 | 22 units, 55 MW (2007) | unchanged, medium confidence | a 2011 DEQ letter, not a permit; it names a governing permit of 2009-08-28 (amended 2010-04-29), now on the browser fetch list |
| 74079 | 17 units, 38.25 MW (2021) | unchanged | the file downloaded was the 2021 permit again; the 2025-08-21 action is still to fetch |

Net change: +17 units and +40.0 MW, to 182 permits, 13,990 units and 33,733 MW (33,627 MW excluding 51 transitory units). The generator-hours figures for 73370 and 73670 are unchanged: they use the units permitted in the inventory years (2020, 2023), and ACC10 is on a street the inventory record does not name.

