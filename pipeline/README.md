# Permit-extraction pipeline: Virginia DEQ + Texas TCEQ data-center sites

Turns the 325 register-identified sites in `sites/seed_sites_unlocated.csv`
(173 Virginia DEQ air-permit registrations, 152 Texas Comptroller registrations) into located,
generator-rated rows in the seed_sites schema and in Climate TRACE's asset schema.

Written and fixture-tested 2026-10-20/21. **Run live 2026-10-21** from a laptop: the DEQ site refuses
scripted PDF downloads (HTTP 403), so the list page was saved from a browser and the 183 permit PDFs
were downloaded by browser and passed with `--pdf-dir`. The Virginia extractor was then **fixed on
2026-10-22** after an independent second read (section "Fixed 2026-10-22" below): it now agrees with
the hand-resolved figures on 178 of 182 permits. Texas has a second script, `tx_fetch.py`, that works
from issued authorizations (section "Texas from issued authorizations" below).

## The one command

```bash
cd pipeline
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
| 1 | `va_deq_permits.py` | DEQ list page, DEQ permit PDFs | `va_permits.csv` (one row per registration, 51 columns), `va_generator_rows.csv` (every equipment row counted, with the read it came from, for audit), `va_pdfs/`, `va_text/` (`<reg>.txt` text layer + `<reg>.tables.json` ruled tables), `va_permits_summary.json` |
| 2 | `tx_permits.py` | TCEQ Title V + NSR pending-application index pages, TCEQ application PDFs | `tx_permits.csv` (one row per Comptroller registration), `tx_unmatched_tceq_packages.csv` (data-center TCEQ packages with no Comptroller row), `tx_index_rows.csv`, `tx_pdfs/`, `tx_text/`, `tx_permits_summary.json` |
| 3 | `geocode.py` | Nominatim, US Census Geocoder | `geocoded.csv`, `geocode_cache.json`, `geocode_summary.json` |
| 4 | `merge_to_handover.py` | `registry/seed_sites.json`, `scrapers/to_climate_trace.py` (column lists; embedded fallback) | `seed_sites_v2.json` + `.csv`, `climate_trace/datacenters_emissions_seed.csv` (44 cols), `climate_trace/datacenters_ownership_seed.csv` (19 cols), `handover_summary.json` |
| 5 | `validate_outputs.py` | the above | exit 1 on any invalid file |

Shared code: `permit_text.py` (PDF->text, all regexes, confidence rules; its docstring records the
real layouts seen), `_common.py` (copy of `scrapers/_common.py`: fetch with "file moved" detection,
atomic writes).

### What each field means and how confident it is

Every extracted field has a confidence column (`high|medium|low|none`) and nothing is estimated:

* **Generator count / total_standby_mw (VA)**: sum over equipment rows of `count x ekW`, read twice
  (`permit_text.read_generator_inventory`): a *table read* of pdfplumber's ruled-table cells and an
  independent *text read* that pairs count statements with kW ratings in document order. The table
  read is reported when the PDF has ruled tables; the text read otherwise (OCR scans, prose letters,
  fixtures). Count per row: "(23)" / "Twenty three (23)" / "(36 units)" / "(1,332)" / "34 - MTU" /
  "26 emergency ...", else the expanded Ref. Nos. ("ENG46 – ENG61", "101-GEN-A1 through 101-GEN-D1"),
  else 1 for a singular description. Conventions: where a row prints a de-rate, the rating printed
  first is used; a rating labelled "standby" is used over the other one; for either/or makes the
  first listed is the central value, and `_min`/`_max` carry the range. Fire pumps, boilers,
  turbines, cooling towers and tanks are excluded, as are units "being replaced" and units listed
  twice. bhp-only units are counted, but MW is left empty (never estimated) with a reason.
  `total_mw_confidence`: `high` only when the table read and the text read give the same count and
  MW (within 1 %); `medium` when there is one consistent read; `low` for either/or ratings, units with
  no kW in the text, or inherited/guessed rows. `generator_read` and `generator_crosscheck` say which
  read was used and what the other read found.
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
298 MW; 74274: 98, 237 MW; 74161: 159, 364.25 MW first-listed, 364-390 MW either/or; 73200 Verizon
2006 layout: 7, 14 MW; fixtures are text only, so there is no table read and MW confidence tops out
at `medium`),
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
  tests/
    test_va_extraction.py        runs the VA extractor on the 183 real permit PDFs vs review/va_reread/va_resolved.csv
    va_extraction_vs_resolved.csv  its per-permit output (status, both figures, confidence, basis)
    REMAINING_DISAGREEMENTS.md   one line per permit that still differs, with which reading is right
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

## Fixed 2026-10-22: Virginia generator inventories

An independent second read of all 183 Virginia permits (`review/va_reread/`, figures resolved by hand
against the text in `va_resolved.csv`) found the regex extractor's generator counts and MW wrong in
most permits. The extractor has been fixed and tested on all 183 permit PDFs
(`tests/test_va_extraction.py`, which runs the pipeline's own per-PDF path `extract_from_pdf`; 182
are permits, and `5.pdf` is an "Access Denied" HTML page that is skipped).

| | agree | minor | disagree | MW null | fleet MW (182 permits) | units |
|---|---|---|---|---|---|---|
| before (first reading) | 24 | 22 | 110 | 26 | 19,186.4 (+77,540 from three absurd rows) | 45,910 (incl. counts 30,002 / 6,050 / 2,081) |
| after (fixed) | **178** | **2** | **0** | **2** | **33,134.4** | **13,972** |
| resolved (second read) | | | | | 33,692.7 | 13,973 |

agree = count equal and MW within 2 %; minor = MW within 10 % and count within 2 (the rule the second
read used; the looser "MW within 10 % or count within 2" gives the same numbers after the fix). The
report's 107 disagree / 29 null split counts the three absurd results (52221: 62,954 MW; 52403:
9,386 MW; 73860: 5,199 MW) as null; the harness counts them as disagree. Run it with
`python3 tests/test_va_extraction.py` (7 minutes; `--text-cache DIR` makes reruns take seconds).

**Defects fixed** (each fixed as a pattern, with no registration special-cased):
* *First data row after a table header dropped* (70 permits). pdfplumber interleaves multi-line cells,
  so a row's description can continue after its rating, and the old reader only looked backwards from
  each rating. Two fixes: a table read of the ruled-table cells (`pdf_to_tables`, `rows_from_tables`),
  and a text read that pairs counts with ratings in document order in both directions
  (`find_generator_rows`).
* *Model years, dates, street and phone numbers read as counts*: "(1987)", "(Manufacture Date: 2010)",
  "6050 Technology Creek Drive", "(804) 698-4000", and ref-range ends ("21 through 59 emergency…",
  "EG-001 through EG- / 020 engine gen-sets").
* *Unit counts*: "(N units)" / "(1 unit)" (paired with the rating before or after); "(1,332)" with a
  thousands comma; "One thousand three hundred and thirty-two"; "34 - MTU"; and spelled counts before
  makers not on the list ("Twelve Clarke diesel …").
* *Reference-ID ranges expanded*: "ENG46 – ENG61, ENG67 – ENG110", "ENG113 – ENG 152", "EG113-EG145",
  "101-GEN-A1 through 101-GEN-D1" (letter ranges), "Gen4101-01,-02,-03,-04,-Z", "DC5EG-A DC5EG-B …",
  "1 through 1,332", ranges wrapped around the description ("Nos. 1 through … 12 Power Generators").
  Permits that number units "1-0", "2-1" treat "1-2" as one id; "(Group 3)" labels are not ids.
* *Ratings*: de-rates ("1,600 ekW – de-rated to 1,500 ekW", "3,000 ekW (de-rated from 3,250)") are
  one unit at the first-printed rating; "(2,250 ekW standby)" is used over the other rating; either/or
  makes ("and/or MTU …", "Cummins: … MTU: …", "(each Caterpillar …) … (each Kohler …)") are one unit
  with a range. Also handled: "685 mkW" (mechanical) is not ekW; "1,620* ekW", "750!kWe", "2000 RW"
  (OCR), "1000 kilowatts", and units wrapped onto the next line of a cell ("or 2000 / … ekW").
* *Rows that are not generators*: fire pumps (also "fire 2018 pump" split by an interleaved date),
  boilers, turbines (8 Solar gas turbines at 74242), cooling towers, fuel tanks, heaters,
  emission-limit tables ("750 ekW Caterpillar (Ref. Nos. …) lbs/hr"), footnotes quoting a rating,
  a note about a removed unit (73860), and units "being replaced" (73355).
* *Duplicate listing* (74262: BYEG1–BYEG120 printed under two permit dates): the same units with the
  same count and rating are counted once (and a unit id on two rows blocks a `high` count).
* *Multi-part permits* (73823 Part I / Part II): each equipment-list region is read; regions end at
  the next numbered condition, and mentions such as "(listed in the Equipment List above)" do not
  open a new one.
* *Text layer*: `pdf_to_text` falls back to pypdf when pdfplumber sees no pages (52173, a 96-page scan).
* *Rows split by a page break*, bhp-only rows, merged capacity cells (52629: one "3,000 ekW (each
  unit)" cell for two rows, low confidence), and OCR rows with no rating (counted, MW partial, low).

**Confidence is now earned.** `total_mw_confidence = high` only when the table read and the
independent text read give the same count and MW. On the 183 permits: high 114 (114 agree with the
resolved figures), medium 59 (59 agree), low 7 (5 agree, 2 minor), none 2 (bhp-only).

**Remaining differences** (`tests/REMAINING_DISAGREEMENTS.md`):
* 73717 and 73995: the OCR text layer lost a capacity cell (73717 LS1 300 ekW) or a whole row (73995
  Transitory Engine 5). The resolved figures were read from page images and are right. Together
  -2.3 MW and -1 unit; both are flagged `low`.
* 52949 and 52973 (Microsoft AVC01/AVC09) print bhp only. The pipeline counts the 63 and 129 units
  but leaves MW empty rather than estimate; the resolved 181.5 + 374.5 MW are inferred from sibling
  permits' identical models. This is 556 of the 558 MW fleet gap.

The fix was tested against the second reader's resolved figures, so the agreement shows that the
pipeline now reproduces them; it is not a third independent reading. Where the two still differ, use
the resolved file (`data/climate_trace_seed/va_permits_resolved.csv`).

## Texas from issued authorizations (`tx_fetch.py`, 2026-10-22)

`tx_permits.py` (step 2 above) can only see applications while they are pending; TCEQ drops them from
its indexes once a permit issues. `tx_fetch.py` works from records that stay public after issuance:
EPA's Facility Registry Service (ICIS-Air, TCEQ Central Registry RN, EIS and CEDRI ids, stormwater
coverage, each with a lat/lon), TCEQ Title V public-notice PDFs, and TCEQ air-permit project numbers.

```bash
python3 tx_fetch.py --fixture --out out_tx    # offline: rebuilds the 2026-10-22 outputs from fixtures/tx_issued/
python3 tx_fetch.py --out out_tx              # live: FRS, ICIS-Air, TCEQ PDFs, airperm project reports
python3 tx_fetch.py --out out_tx --psei 2024 --central-registry-coastal   # plus TCEQ emissions inventory and Central Registry file
```

Inputs: `sites/seed_sites_unlocated.csv` (Comptroller rows) and `sites/tx_site_links.csv` (the curated
joins: site to FRS ids to TCEQ authorizations to Comptroller rows; edit it to accept a candidate).
Outputs: `tx_issued_sites.csv` (129 facilities), `BROWSER_LIST.csv` (88 TCEQ Records Online searches),
`tx_fetch_summary.json`. The fixture run reproduces the files in `data/climate_trace_seed/` byte for
byte. Untested live: the airperm report parser and the ECHO SIC parameter. Report and counts:
`data/climate_trace_seed/TEXAS.md`.

## The handover's asset files (`build_handover_assets.py`, 2026-10-22)

`merge_to_handover.py` (step 4) writes Climate TRACE rows from the pipeline's own reading into
`out/climate_trace/`. The handover's files are built separately, from the reviewed sources only:

```bash
python3 build_handover_assets.py            # writes data/climate_trace_seed/datacenters_*_seed.csv, the unlocated backlog and assets_summary.json
```

Sources: `sites/seed_sites.json` (seed rows that duplicate a permit or licence row are dropped, listed
in `assets_summary.json`), `sites/ireland_sites.json`, the Virginia resolved figures
(`va_permits_resolved.csv`, coordinates from the 2026-10-21 geocode of each permit's street address,
used when the match type is rooftop or census), and `tx_issued_sites.csv`. Every generator figure
carries its basis in `other4`: standby MWe summed from a permit's unit ratings, primary on-site
generation, or an Irish licence's thermal-input figure. No local file paths reach the outputs (the
Virginia rows point to DEQ's public list page, where each permit is linked by registration number).
CI rebuilds these files and fails if they differ from the committed copies.

**Known fragility: addresses.** The 21 October geocode ran on the address the first reading took from
each permit, which for thirteen permits was the permittee's mailing address (the cover page lists it
first). `build_handover_assets.py` therefore places a Virginia site only when the geocoded address
matches the site address resolved by the second reading. The extractor's address picker itself has not
been changed; the next live run should geocode `site_street` from `va_permits_resolved.csv`.


## The measurements table (`build_measurements.py`, `validate_measurements.py`, 2026-10-23)

Every figure the ledger holds, one row each, in `data/climate_trace_seed/measurements.csv`, with the sites they belong to in `site_register.csv` and the utilities and registers in `entity_register.csv`. Columns: a content-hashed `measurement_id`; `subject_type` (site, entity or entry) and `subject_id`; the ledger `entry_id` the figure appears in; `metric`, `unit` and `basis` from `measurement_vocab.json`; `value` and `value_high` in the published unit; `value_canonical` in one unit per dimension (MWh, MW, MWth, t, m3, m3/day, ha, h) through `units.py`; `value_as_published`, the figure exactly as it is written in the text it was taken from (the document's line or cell, or for figures from the registry the entry's own sentence), plus `qualifier` (lower_bound, upper_bound, approximate) read from the words around it; the period; `side` (record or claim); the source URL, title, publisher and date; the `feed` file it came from; how it was extracted; whether it has had a second reading.

Feeds: the figures in the registry entries' text (`sites/measurements_from_registry/rows_*.csv`, each checked to occur verbatim in its entry), the Irish annual environmental reports, EPA's emissions inventory, the benchmarking portals, the utility filings (`sites/metered/filed_figures_curated.csv`, each checked against its quoted line), the Virginia permits, the Texas facilities and the Irish and seed site lists.

The site register joins everything: Virginia sites are `usa-va-deq-<registration>`, Texas `usa-tx-<facility_key>`, Irish and seed sites keep their list ids, benchmarking buildings are `usa-bench-<city>-<address>` with a `kind` (datacenter, telecom_exchange, mixed_building_with_datacenter), and NEI facilities not matched to a permit are `usa-va-nei-<EIS id>`. `ct_source_id` gives the row in Climate TRACE's seed file, `backlog_id` the row in the unlocated backlog.

`validate_measurements.py` checks the vocabulary, that each unit fits its metric's dimension, the canonical conversions, the periods, that subjects and entries exist, and, for registry figures, verbatim presence and source membership. CI rebuilds the table and fails if it differs from the committed file.
