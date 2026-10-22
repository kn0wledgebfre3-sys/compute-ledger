# Permit-extraction pipeline: Virginia DEQ + Texas TCEQ data-center sites

Turns the 325 register-identified sites in `/home/claude/registry/seed_sites_unlocated.csv`
(173 Virginia DEQ air-permit registrations, 152 Texas Comptroller registrations) into located,
generator-rated rows in the seed_sites schema and in Climate TRACE's asset schema.

Written and fixture-tested 2026-10-20/21 from a sandbox that could **not** reach deq.virginia.gov or
tceq.texas.gov by shell. Every source format below was read with a fetch tool; **no script has run
against a live source yet.** See "Known fragilities".

## The one command

```bash
cd /home/claude/pipeline
pip install -r requirements.txt     # requests, pandas, pdfplumber (+pypdf fallback)
./run_all.sh                        # live run -> out/
./run_all.sh --fixture              # offline self-test on fixtures/ -> out_fixture/  (passes; 30 s)
```

Needs: Python 3.10+, internet (HTTPS to deq.virginia.gov, tceq.texas.gov, html.duckduckgo.com,
nominatim.openstreetmap.org, geocoding.geo.census.gov). No keys, no credentials.

Expected live runtime: **25-60 minutes**, almost all of it polite pauses:
~173 DEQ PDF downloads at 1.5 s (plus up to 3 search fallbacks per unlinked registration at 2 s),
~20 TCEQ PDFs, ~180 Nominatim queries at 1.1 s, one Census batch. Re-runs are fast: PDFs, extracted
text and geocoder answers are cached in `out/` (delete `out/` or pass `--refresh` to redo).

Smoke test first: `./run_all.sh --limit 10` (the extra args go to the Virginia step).

## Steps and outputs (all in `out/`)

| Step | Script | Needs | Writes |
|---|---|---|---|
| 1 | `va_deq_permits.py` | DEQ list page, DEQ permit PDFs | `va_permits.csv` (one row per registration, 48 columns), `va_generator_rows.csv` (every equipment-table row found, for audit), `va_pdfs/`, `va_text/`, `va_permits_summary.json` |
| 2 | `tx_permits.py` | TCEQ Title V + NSR pending-application index pages, TCEQ application PDFs | `tx_permits.csv` (one row per Comptroller registration), `tx_unmatched_tceq_packages.csv` (data-center TCEQ packages with no Comptroller row), `tx_index_rows.csv`, `tx_pdfs/`, `tx_text/`, `tx_permits_summary.json` |
| 3 | `geocode.py` | Nominatim, US Census Geocoder | `geocoded.csv`, `geocode_cache.json`, `geocode_summary.json` |
| 4 | `merge_to_handover.py` | `registry/seed_sites.json`, `scrapers/to_climate_trace.py` (column lists; embedded fallback) | `seed_sites_v2.json` + `.csv`, `climate_trace/datacenters_emissions_seed.csv` (44 cols), `climate_trace/datacenters_ownership_seed.csv` (19 cols), `handover_summary.json` |
| 5 | `validate_outputs.py` | the above | exit 1 on any invalid file |

Shared code: `permit_text.py` (PDF->text, all regexes, confidence rules; its docstring records the
real layouts seen), `_common.py` (copy of `scrapers/_common.py`: fetch with "file moved" detection,
atomic writes).

### What each field means and how confident it is

Every extracted field has a confidence column (`high|medium|low|none`) and nothing is estimated:

* **Generator count / total_standby_mw (VA)**: sum over equipment-table rows of `count x ekW`.
  Count comes from "(23)" / "(36 units)" / "Twenty three" / "26 emergency ..." and is cross-checked
  against the Ref. Nos. range ("1 through 23"): agreement = `high`, one source = `medium`,
  disagreement or either/or ratings ("2,250 ekW or 2,500 ekW") = `low` with a min-max range.
  Fire pumps, boilers and tanks are excluded. bhp-only units (no ekW) are not counted.
* **Generator count / MW (TX)**: distinct OP-SUM unit ids with form OP-UA2; kW from "2500KW" in the
  unit description. Packages that list emission groups only (Alamo Mission) or units without kW
  (Compass Red Oak, 390 units) get a count or null plus a reason.
* **Facility address (VA)**: the block after "located at" on the permit cover (`high`); otherwise the
  last Virginia address on the cover (`low`, may be the permittee's mailing address). Multi-number
  addresses ("10321, 10301, 10281, and 10261 Tanner Way") are geocoded on the first number; the full
  string is kept in `facility_address_raw`.
* **Coordinates (TX)**: Core Data Form decimal (`high`), STEERS decimal (`high`), OP-1 DMS or TCEQ
  letter map-marker (`medium`), checked against the Texas bounding box.
* **Coordinates from geocoding**: Nominatim building/house hit = `high`; Census Exact = `high`,
  Non_Exact = `medium`; Nominatim street-only = `low` and **not used** by the merge unless
  `--include-weak`; locality-level hits are discarded (null + reason).
* **TCEQ name match**: `known_documents` (8 URLs verified by hand), `titlev_index`/`nsr_index` (a
  distinctive company word shared with the applicant), `*_weak_area` (only a word in the facility
  name, e.g. "Goodnight"), `*_unverified` (one company word, TCEQ names do not say "data center";
  the NAICS 518210 check after download confirms or clears it), `ambiguous`, `none`. Weak and
  unverified matches are extracted but their coordinates are withheld in the merge unless
  `--include-weak`; they are flagged `needs_review`.
* **Hours/fuel**: distinct "hours per year" limits for maintenance/testing, all purposes and combined
  caps; fuel wording; sulfur ppm; gallons/year caps (all as found, `;`-separated when several).

## Known fragilities (read before the live run)

1. **DEQ list page links are unverified.** The fetch tool strips `<a href>`, so whether each Air Site
   Name links its permit PDF (`deq.virginia.gov/home/showpublisheddocument/<id>/<ticks>`) is inferred
   from the Virginia Mercury's write-up, not seen. The parser takes any link in a row. If the live run
   logs `rows with links = 0`, open the page in a browser: if names are links, save the page and
   re-run with `--html-file saved.html`; if not, the fallbacks are (a) the 8 registrations in
   `fixtures/va_known_documents.csv`, (b) a DuckDuckGo HTML search per registration (fragile:
   rate-limited, needs the PDF to be indexed; each hit is verified by the registration number printed
   in the PDF; `--no-search` disables it), (c) `--pdf-dir DIR` with hand-downloaded PDFs named
   `<registration>*.pdf`, (d) `--enumerate 25690-26130` which tries the tick-less document URL for
   the whole September-2024 upload batch; that URL form could not be tested tonight.
2. **The list page is server-rendered HTML (assumed).** If it became a JavaScript widget the parser
   raises `SchemaChangedError` naming the tables it did see; use `--html-file`.
3. **PDF layout variants.** Built against 8 real DEQ permits (2006-2024: "Reference No." vs "Ref.
   No(s).", "Rated Capacity" vs "Standby Rated Capacity" vs "Maximum Rated Capacity", counts as
   "(23)" / "(36 units)" / spelled / leading number, ekW before or after bhp, cell-per-line or
   row-per-line text). Untested: Title V permits (reg 21527 Microsoft), scanned/image-only PDFs
   (`text_quality=empty`, needs OCR; none of the eight were scanned), permits whose generators are
   natural-gas or dual-fuel, permits that list units only in prose. `va_generator_rows.csv` shows
   exactly which lines were counted; `va_text/<reg>.txt` is what the regexes saw.
4. **The posted PDF may not be the latest permit** (reg 73743: PDF is the 2022 permit, list says
   2025-08-04) and the list name may differ from the permittee (reg 74107 "Cloud HQ" vs "Abteen
   Ventures LLC"; reg 73200 "Equinix DC 14" vs a 2006 "Verizon Business" permit). Both are written
   out (`permit_date_list` vs `approved_on`, `facility_name_list` vs `permittee_pdf`).
5. **TCEQ indexes list pending applications only.** Issued permits drop off (Microsoft 38509 from
   2025 is already gone) though their PDFs stay online. So most of the 152 Comptroller rows will
   come back `match_method=none` with a reason; that is expected, not a bug. The Comptroller list
   has no county or address, so matching is by name only; same-company-different-site errors are
   limited by facility-code and metro-region checks (TX11 vs TX21, CyrusOne Houston vs DFW) but
   not eliminated. The Central Registry client (`--central-registry`) was written blind (the site
   is robots-blocked for the fetch tool) and should be treated as untested.
6. **Garbled TCEQ PDFs.** 40584-ac.pdf (CyrusOne DFW) extracts as glyph codes; detected and
   reported as `text_quality=garbled`, no OCR attempted.
7. **Geocoder policy.** Nominatim allows 1 request/s with an identifying User-Agent (set in
   `_common.USER_AGENT`, override with env `LEDGER_USER_AGENT`); heavy use should move to a local
   instance. Census batch endpoint sometimes times out on large batches; the script sends 1,000 at a
   time and records the failure per row.
8. **Fixtures are reassembled quotes, not PDF dumps.** The fetch tool caps verbatim quotes at ~125
   characters, so `fixtures/*.txt` are those fragments arranged in the reported layout; three rows
   are reconstructed from reported totals and are marked in `fixtures/provenance.json`. Expect the
   live extracted text to differ in whitespace and page-header noise; the regexes work on a
   whitespace-flattened copy with windows for that reason, and a fixture text rendered to PDF and
   re-extracted through pdfplumber gives the same result (checked).

## Spot-check list for a human (10 random rows against the PDFs)

Pick 10 rows at random from `out/va_permits.csv` with `text_quality=ok` (e.g.
`shuf -n 10`), open each `out/va_pdfs/<reg>.pdf`, and check:

1. `registration_no_pdf` equals the cover's "Registration No." (flag `registration_match` != match).
2. `permittee_pdf` is the company on the cover; note it against `facility_name_list`.
3. `facility_street` / `facility_city` / `facility_zip` is the address after "located at", not the
   mailing address above "Registration No." (`address_method` says which was used).
4. `generator_count` equals the number of gen-sets in the equipment tables (sum the "(n)" counts;
   include previously-permitted tables; exclude tanks and fire pumps). `va_generator_rows.csv`
   lists each row counted with its `refs` and `description`.
5. `total_standby_mw` equals sum(count x ekW)/1000; if `total_standby_mw_min` != `_max` the permit
   had an either/or rating: decide which model was built or keep the range.
6. `hours_all_purpose_per_year` / `hours_maint_per_year` match the operating-limit condition.
7. `fuel` and `fuel_sulfur_ppm` match the fuel condition.
8. `approved_on` matches "Approved on"; if it is older than `permit_date_list`, the posted PDF is
   an earlier permit and the inventory may be stale.
9. In `geocoded.csv`, `matched_address` is the same street and town as the permit; look at the
   point on a map to confirm it sits on a data-center building, not a road centroid.
10. In `seed_sites_v2.json`, the row's `notes` carry all of the above and `confidence` is `high`
    only when both the address and the geocode were `high`.

For Texas, take every row with `application_url` set (there will be ~15-25): confirm the applicant
and area name in the PDF are the same site as the Comptroller registration (owner/occupant), that
`lat/lon` match the Core Data Form or STEERS values, and that NAICS is 518210. Rows marked
`weak_area`/`unverified` need this check before `--include-weak` is used.

Also read `out/handover_summary.json`: sites, with coordinates, with generator MW, by state,
by coordinate method, and how many rows are `needs_review`.

## Fixture run (passes tonight)

`./run_all.sh --fixture` runs every step on `fixtures/` and validates all 14 output files
(`out_fixture/`). It is byte-deterministic (`retrieved_at` is null in fixture mode). What it proves:
the 8 Virginia fixtures extract the expected counts/MW (74129: 97 gen-sets, 236.3 MW; 74107: 103,
298 MW; 74274: 98, 237 MW; 74161: 159, 364-390 MW either/or; 73200 Verizon 2006 layout: 7, 14 MW),
the facility (not mailing) address, hours, fuel; the Texas fixtures give the Core Data Form and
STEERS coordinates, 73 units / 176.5 MW for Microsoft SN, groups-only and garbled cases; TCEQ name
matching accepts Vantage TX11, Aligned Plano, Nexus Hubbard and rejects Lancium Childress vs IE US
Childress, TX21-22 vs TX11, CyrusOne Houston vs DFW, Acme Brick Denton; geocoding covers rooftop,
street-only, locality-only, Census Exact/Non_Exact/No_Match/Tie; the merge updates the 8 v1 rows
that share a TCEQ URL instead of duplicating them and writes 63 Climate TRACE rows with the schema's
44/19 columns. Fixture numbers are not real totals (`fixture_warning` in every summary).

## Files

```
pipeline/
  run_all.sh  requirements.txt  README.md
  _common.py  permit_text.py
  va_deq_permits.py  tx_permits.py  geocode.py  merge_to_handover.py  validate_outputs.py
  fixtures/
    provenance.json              where every fixture came from and what is reconstructed
    va_deq_list_page.html        DEQ list table layout (real rows)
    va_known_documents.csv       20 real showpublisheddocument URLs, 8 mapped to registrations
    va_permits/<reg>.txt         8 real DEQ permit texts (fragments)
    tx_pending_titlev.html  tx_pending_nsr.html   TCEQ index layouts (real rows)
    tx_known_documents.csv       7 real TCEQ application URLs with Comptroller match regexes
    tx_applications/<id>.txt     4 real TCEQ package texts (incl. one garbled)
    geocode_responses.json       SYNTHETIC geocoder replies
    seed_sites.json              copy of registry/seed_sites.json (v1, 56 rows)
  out_fixture/                   result of ./run_all.sh --fixture
```

## Known defect in the first reading (2026-10-21), and the resolved figures

An independent second read of all 183 Virginia permits (review/va_reread/) found the regex extractor low in 98 of 107 disagreements. Dominant cause: the first data row after each equipment-table header is dropped (70 permits). Others: parenthetical model years parsed as unit counts; reference-ID ranges ("ENG46 – ENG61") not expanded; de-rate and alternate-model lines counted as units. The pipeline's 19,186 MW is superseded by the resolved 33,693 MW in data/climate_trace_seed/va_permits_resolved.csv. The extractor has not yet been patched; until it is, treat its Virginia MW output as a first pass to be checked, and use the resolved file.
