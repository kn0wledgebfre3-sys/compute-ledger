# Virginia DEQ data-center air permits: independent second read

**Scope.** 183 PDFs in `pipeline/pdfs_va/` (one per registration), re-read with a method that shares no code with the pipeline. The pipeline's regex code was not opened; its output (`pipeline/out/va_permits.csv`) was consulted only after my own figures were fixed and written to `decisions.csv`.

**Headline.** Resolved fleet: **13,973 generator units / 33,693 MW standby** across 181 readable registrations (177 high-confidence, 5 medium, 2 unreadable). The pipeline's figures agree with the text in only 24 permits; it is wrong (mostly low) in 129 and null in 29. Its summed MW over the 153 permits where it reported a number is 19,186 MW against 30,867 MW for the same permits on re-read.

## 1. Method

1. **Extraction cache.** Every PDF was opened with `pdfplumber` (`extract_text()` and `extract_tables()` with both the lines and text strategies, page by page), with `pypdf` as fallback (needed for 52173, a 96-page OCR scan). Text and tables were cached to `raw/<reg>.json`.
2. **Two automated readers**, written blind to the pipeline (`reread.py`):
   - *Table reader*: finds equipment-list tables by header (Description + Rated Capacity/Size), carries the header across page breaks, infers columns on headerless continuation tables, and reads per row: unit count (parenthetical digits > number-word phrase > "N -"/"(N units)" > reference-ID ranges such as `ENG46 – ENG61, ENG67 – ENG110`, `101-GEN-A1 through 101-GEN-D1`), kW/ekW/kWe, bhp, MMBtu/hr, emergency vs non-emergency, fuel. Boilers, fire pumps, chillers, cooling towers and tanks are excluded.
   - *Prose reader*: isolates the equipment-list section of the running text and pairs count tokens with capacity tokens in document order, independent of table geometry.
   - Classification per permit: `both-agree` (89), `both-disagree` (46), `prose` only (45), `table` only (1), `unreadable` (2).
3. **Manual read of every permit.** A digest (both readers' rows + the section text) was produced per permit (`digest/<reg>.txt`) and read by eye for all 183, with hand re-summation. Where OCR text was ambiguous the page was rasterised and viewed (52629, 73717, 73995). Decisions and a one-line basis per permit are in `decisions.csv` (94 permits needed an explicit decision; the other 89 are both-agree permits whose rows were scanned and accepted).
4. **Conventions.** kW/1000 = MW electrical; bhp used only when no kW is printed (none in the final figures; see 52949/52973 below); MMBtu/hr never converted. Rated/nameplate ekW is used where a de-rate is also printed (the de-rated alternative is noted in the basis). Transitory/temporary gen-sets listed in the permit are counted but also reported separately (`count_excl_transitory`, `mw_excl_transitory`). Units listed as "exempt from permitting" but present in the equipment list are counted (noted). Units the permit says are being removed or replaced are not counted.
5. **Comparison** (`finalize.py`): agree = count equal and MW within 2 %; minor = MW within 10 % or count off by 1–2; otherwise disagree; nulls flagged. Every disagree/minor was resolved against the permit text with a one-line note.

## 2. Totals

| Status | Permits | Pipeline MW | Resolved MW |
|---|---|---|---|
| agree | 24 | 3,611.5 | 3,611.5 |
| minor | 22 | 4,137.6 | 4,158.1 |
| disagree | 107 | 11,437.2 | 23,097.3 |
| pipeline-null | 29 | — | 2,825.8 |
| yours-null | 2 | — | — |
| **total** | **184** | **19,186.4** (153 non-null) | **33,692.7** (181) |

(184 rows because the pipeline list contains 74331, Westfax 4-5A, whose download failed and which has no PDF; the PDF directory contains `5.pdf`, a 479-byte "Access Denied" HTML page that is not a permit.)

- Fleet before resolution (pipeline, as summed from `va_permits.csv`): 19,186 MW; its `generator_count` column sums to 45,910 because three nulled-MW rows carry absurd counts (30002, 6050, 2081).
- Fleet after resolution: **33,692.7 MW / 13,973 units**. Excluding the 51 transitory gen-sets (106 MW): 33,586.8 MW / 13,922 units. 2,913 of the units are permitted as *non-emergency* gen-sets (SCR-controlled, demand-response capable).
- In 98 of the 107 disagreements the pipeline is low; in 9 it is high. Resolved = re-read in every case; the pipeline was not found to be right where the two differ (one genuinely ambiguous case, 74284, is a 4.6 % rating choice).
- Agree: 52820, 52903, 53071, 53072, 53086, 73162, 73240, 73294, 73363, 73567, 73643, 73813, 73946, 73954, 74049, 74156, 74162, 74172, 74205, 74260, 74332, 74333, 74335, 80941.

## 3. The three nulled permits

| Reg. | Pipeline | What the permit says | What tripped the parser |
|---|---|---|---|
| 52221 Bank of America, Villa Park (Richmond) | 62,954 MW / count 30002 | 16 single-unit rows: Bldg C Engines 1–10 (1,600/1,600/1,600/1,750/1,375/1,375/2,000×4 kW) + Bldg E Engines 1–6 (2,250×3, 3,000×3 kW) = **16 units / 33.05 MW**; two 6 MMBtu/hr boilers excluded | Each description ends with the model year in parentheses, e.g. "Caterpillar 3516 diesel generator (1987)"; in the text stream that year precedes the next row, so it was read as "1987 x 1600 kW" |
| 52403 Bank of America, Sandston | 9,386 MW / count 6050 | 6×563 (new) + 5×2,446 + 6×1,645 + 12×563 kW + exempt 250 kW = **30 units / 32.48 MW** | Model years "(2020)", "(2012)", "(2017)" read as unit counts ("2020 x 2446 kW"); the 6050 count is from "6050 Technology Creek Drive" |
| 73860 Amazon IAD-12/15/16/76/230 | 5,199 MW / count 2081 | 26×2,750 non-emergency (new) + 750 + 2,000 + 4×3,000 + 61×2,500 + 6×2,000 (T1–T6) = **95 units / 240.75 MW** | Footnote about a unit removed in 2021 ("...permit dated February 7, 2013 ... rated at 2,500 ekW") combined with a permit date "December 15, 2015" to yield "2015 x 2500 kW"; the first table row (26×2,750) was also dropped |

## 4. The ten spot-checks

| Reg. | Facility | Pipeline | Re-read / resolved | Note |
|---|---|---|---|---|
| 74173 | CyrusOne NVA9–11, Sterling | 83 / 185.75 | 82 / 183.5 | pipeline counted the "and/or MTU" alternate as an extra unit (minor) |
| 74272 | Amazon, 7961 Loisdale Rd | 1 / 1.6 | 30 / 74.1 | first row (29×2,500) dropped |
| 73823 | Level 3, 524 & 520 Van Buren St | 3 / 5.2 | 4 / 7.2 | Part II (520 Van Buren, 1,600 kW) missed |
| 53071 | Microsoft AVC43 | 42 / 125 | 42 / 125 | agree |
| 74049 | Amazon, Smith Switch Rd | 110 / 261 | 110 / 261 | agree |
| 74274 | Amazon, Quail Ridge Ln | 6 / 7 | 98 / 237 | first row (92×2,500) dropped |
| 74244 | Amazon, Beaumeade Cir | 16 / 35.2 | 40 / 95.2 | first row (24×2,500) dropped |
| 74120 | NTT VA3–VA7 | 114 / 313.7 | 109 / 306.2 | de-rate lines ("de-rated to 1,500 ekW") counted as extra units |
| 73670 | Digital Loudoun Pkwy Center N | 118 / 223.675 | 143 / 283.175 | 31-row OCR table; pipeline missed the new 19×2,500 row and the G1 building rows; hand sum matches my prose parser exactly |
| 74342 | Amazon IAD-110–113 | 104 / 274.2 | 103 / 273.45 | pipeline added a spurious 750 kW unit (minor) |

## 5. Systematic error patterns

**Pipeline (observed in its `unit_kw_list`):**
1. *First data row after the table header is dropped* — in 70 permits (e.g. 74118 lost 30×4,000 kW; 74141 lost 17×2,500 and 19×3,000; 74272/74270/74274/74277/74301/74329 kept only the house or transitory units). This is the single largest source of under-count.
2. *Model years and dates parsed as unit counts* (52221, 52403, 73860) — produced the three >2 GW results.
3. *Numbers from reference-ID ranges or neighbouring cells parsed as counts* ("59 x 2000" from "21 through 59" in 74052; "87 x 750" from "66 through 87" in 74171; "130 x 1000" in 74323; "44 x 2000" in 74115; "36 x 2750" in 74288).
4. *"(N units)" count style not recognised* (74085: 90 units read as 1; 74107).
5. *Prose-style and OCR'd legacy permits returned null or a single row* (26 permits "captured only" one row; 29 nulls, 13 of them prose-only permits).
6. *Rows that are not generators counted* — fuel-tank rows (74129: 87×600 kW), fire pumps (74221, 74236), de-rate lines (74120, 74164, 74114), replaced units (73355), alternates (74173, 73935, 74342).
7. *Duplicate listing double-counted* (74262: BYEG1–120 listed twice; footnote says 120 total).
8. *kW mis-assigned across rows* (74052, 74216 — same count, 81 MW vs 335 MW).

**My own automated readers (all caught in the manual pass; recorded so the next reader knows):**
1. Number-word alternation matched prefixes ("Nine" inside "Nineteen", "One" in "One hundred thirty two") — fixed in code before the manual pass.
2. "(1,332)" with a thousands comma read as 1 by both readers (74341) — a both-agree result that was wrong; both-agree is not proof.
3. "(N units)" suffix style (74085, 74107) read as 1 per row by both readers.
4. Cells split by wrapping (74126), headerless continuation tables (73860), truncated section boundaries (73294, 74241, 74246, 72296) and alternates with different kW (51232, 74161) needed hand resolution.
5. The duplicate BYEG listing (74262) fooled both readers until the footnote was read.
6. An asterisk on "1,620* ekW" (74154) broke the kW regex.

## 6. Confidence statement for the fleet figure

- 177 permits (32,681 MW) are **high** confidence: the count and per-unit rating are stated explicitly, the hand sum matches, and the two automated readers agree or the disagreement was resolved by reading the row.
- 5 permits (1,011 MW) are **medium**: 52949 and 52973 (Microsoft AVC01/AVC09) print bhp only — the ekW was taken from identical engine/generator models in sibling Microsoft permits (3,000 and 500 ekW; a pure bhp×0.746 conversion would add ~40 MW); 74161 (103 units are "MTU 2,250 and/or CAT 2,500 ekW" — 362–388 MW); 74284 (Volvo units carry two ratings, 625 vs 560 ekW); 11541 (fair-quality 2008 scan).
- Convention sensitivity, not reading error, is the main residual uncertainty: alternates with different kW (51232 −25 MW, 53259 −62 MW, 74161 +26 MW), standby vs prime rating (74197, 2,250 standby used; +16 MW at 2,500), fan parasitic load (74321, 689 vs 672 MW), de-rates (≈ −8 MW across ten permits), transitory units (−106 MW), natural-gas engine gen-sets counted at 74172 and 80941 (80.6 MW; flagged in `fuel`), and 8 Solar gas turbines at 74242 (132 MWe) deliberately excluded. Taken together the fleet figure sits in a band of roughly **33.4–33.9 GW**, with 33.69 GW as the stated-rating central value.
- Not counted anywhere: 74331 (Westfax 4-5A, no PDF) and the non-permit file `5.pdf`.
- Metadata columns (permittee, facility name, site address, dates, hour/fuel limits) were extracted heuristically and spot-checked, not read twice; `site_same_as_mailing` flags the 39 permits where the chosen site street also appears in the cover-letter mailing block. Hour/fuel limit columns are context snippets, not parsed limits.

## 7. Files

- `va_reread.csv` — one row per registration: my figures, confidence, basis, both automated readers' figures, method, metadata, limits.
- `va_comparison.csv` — registration, pipeline vs re-read, status, resolved figures, one-line resolution note.
- `va_resolved.csv` — final per-registration figures (replaces the pipeline's count/MW columns) with confidence and basis.
- `decisions.csv` — the 94 hand decisions with basis; `digest/` — per-permit reading digests; `raw/` — cached text/tables; `reread.py`, `assemble.py`, `finalize.py` — the independent code.
