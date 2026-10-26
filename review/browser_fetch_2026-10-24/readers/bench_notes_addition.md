# Third pass: downloaded spreadsheets (California statewide, Portland OR, Ontario) - proposed addition

Compiled 2026-10-24 from files downloaded in a browser (folder `fetched/from_downloads/`). Proposed rows: `bench_new_rows.csv` (217 rows, same header as `benchmarking_transcribed.csv`). Every figure was read from the spreadsheet cell named in the row's notes (file, sheet, row number). Nothing was estimated or converted in the CSV. "not found" = empty cell, "Not Available" or "Not Provided". GWh figures in this note are derived here for orientation only (kBtu / 3,412,141.6 per GWh; kWh / 1,000,000). They are not in the CSV.

## Second reading (done, no disagreements)
- First read: openpyxl (read-only, cached values). Second read, two independent methods: (1) `pandas.read_excel`, rows looked up by Portfolio Manager Property ID or Portland Building ID; (2) a raw parse of the sheet XML inside the .xlsx (zipfile + ElementTree, no openpyxl), looked up by the same ids.
- All 217 electricity cells in the CSV (including the 3 "not found") agree across all three reads. Gross floor area, property name and (Portland) the Data Center type were also re-checked: no disagreements.
- Data Center counts were re-derived with pandas value counts: California 83 (2025) and 80 (2024). These match the rows extracted.
- Builder check: the logic of `bench_kind`, `bench_building_key` and `first_number` was copied and run on the proposed rows. Every electricity cell parses to the right number and unit (kBtu for California, kWh for Portland). No two property ids share a building key, and each property id maps to one key across years. California addresses omit the ZIP code because 200 Paul Ave is filed under 94110 in 2024 and under 94124 in 2025, which would otherwise create two sites. The ZIP is kept in the notes.

## California statewide (CEC Building Energy Benchmarking Program, AB 802) - 208 rows (2024: 105, 2025: 103)
- Files: `2025_Download_ADA.xlsx` (https://www.energy.ca.gov/media/13355) and `2024_Download_ADA.xlsx` (https://www.energy.ca.gov/media/12019). Each has one sheet, `Sheet1`. Row 1 is the title, row 3 the header and data starts at row 4. Titles: "Information Reported for 2025, California Building Energy Benchmarking Program, Downloaded October 5, 2026" and "Information Reported for 2024, ..., Downloaded October 5, 2026". The 2025 file has 27,822 rows and the 2024 file 28,655, one per Portfolio Manager Property ID. The file does not say what "ADA" stands for.
- **The data are not anonymised or aggregated.** Every row is property-level: Portfolio Manager Property ID, Standard ID, Property Name (lower-cased in the file), Address 1, City, State, Postal Code, County from Geocoding, Latitude/Longitude, Property GFA - Calculated (Buildings) (ft²), Primary Property Type - Portfolio Manager-Calculated, List of All Property Use Types (GFA) (ft²), Weather Normalized Site EUI (kBtu/ft²), energy use by fuel, ENERGY STAR Score, Year Built, Report Generation Date, Used Estimated Energy Values, the meter alert, Total (Location-Based) GHG Emissions, Year Ending and Number of Buildings.
- **Electricity is published in kBtu only**, as "Electricity Use - Grid Purchase (kBtu)", plus "Electricity Use – Generated from Onsite Renewable Systems and Used Onsite (kBtu)". The CSV cell is `electricity_use_grid_purchase_kbtu=<value> (field "..."; kBtu, NOT kWh)` and every California note starts with `UNIT:`, so the builder records kBtu either way. The file has no kWh field. Other fuels go in the gas/district column under their field names: Natural Gas, District Steam, Chilled Water, Hot Water, Fuel Oil #2, Diesel and Propane, each in kBtu.
- The file has no unadjusted Site EUI. The `site_eui_kbtu_sqft` cell therefore holds the labelled "Weather Normalized Site EUI (kBtu/ft²)=...".
- Year semantics: every row in the 2025 file has Year Ending = 2025-12-31, and every row in the 2024 file has 2024-12-31. Report Generation Dates fall in 2026 for the 2025 file and in 2025 for the 2024 file. So report_year is the calendar year of the data.
- Threshold: the files do not state one. The smallest building typed Data Center is 50,000 sq ft, which fits the CEC page's "> 50,000 sq ft" (earlier notes).
- **Rows typed Data Center:** 83 in 2025 and 80 in 2024. Seven each year will classify as `telecom_exchange` under the builder's regex: five `co/vzb/...` central offices, `ntwk/vzw/2430 business park dr/vista/ca`, and `verizon nec - rocklin 2, california`. The Rocklin site is a Verizon facility typed Data Center and named "NEC", not a central office. The regex catches it because of the word "verizon", so the lead may want to override. Electricity is "not found" for 11085 sun center drive (2025) and for both NTT CA1 and CA2 (2024).
- **Typed otherwise, flagged (all classify as `mixed_building_with_datacenter`):**
  - (a) Data Center listed with 20,000 sq ft or more in "List of All Property Use Types": 19 rows in 2025 and 21 in 2024. Each note gives the Data Center sq ft and its share of non-parking GFA. All are whole-building figures.
  - (b) The property name indicates a datacenter: 2024 `prime data centers - smf01-01` (Other - Technology/Science, 228,517,117.2 kBtu ≈ 67.0 GWh), `rancho bernardo data center` (Other), `ceo/countydatacenter` (Office; typed Data Center in 2025) and `9 first american way (data center)` (Office). In 2025 only `9 first american way (data center)` qualifies. The first two are datacenters by name, but the builder keys on type, so they will classify as mixed.
  - Not added: rows listing Data Center with less than 20,000 sq ft (142 in 2025, 151 in 2024), and rows listing "Data Center (0.0)" (29 in 2025, 26 in 2024). These are offices with server rooms.
- **Largest buildings (derived GWh):**
  - 2025, typed Data Center: 2045-2055 Lafayette St (sjc17), Santa Clara 244.3; 2220 De La Cruz Blvd (sc1) 226.3; 26464 Corporate Ave, Hayward 168.8; CoreSite SV7 (3020 Coronado Dr) 154.0; NTT CA2 (1312 Striker Ave, Sacramento) 149.2; CoreSite SV8 127.0; NTT SV1 106.9; 200 Paul Ave 104.0.
  - 2024, typed Data Center: "ca1" (2880 Northwestern Pkwy, Santa Clara, 6 buildings) 419.5; sc1 256.5; "ca2" (625 Mathew St, 3 buildings) 232.1; sjc17 194.1; 26464 Corporate Ave 183.1.
  - Sum over rows typed Data Center: about 3,007 GWh in 2025 and 3,150 GWh in 2024. The 2024 sum excludes the implausible SV8 value described below.
  - Largest flagged row: intel mission campus (Mixed Use Property, 7 buildings, Data Center 100,000 of 2,215,115 sq ft) at 441.1 GWh (2024) and 473.0 GWh (2025). This is a whole campus and should not be aggregated with datacenters.
- **Traps:**
  - **CoreSite SV8, 3035 Stender Way, 2024: electricity 413,201,894,799.9 kBtu as published** (≈121,000 GWh). The same row has weather-normalised EUI 2,361,154, ENERGY STAR 1 and GHG 27,420,510 t. The 2025 file gives 433,397,253.9 kBtu. This is almost certainly a filing error. It is transcribed as published and flagged in the notes, but it should not enter the ledger without a decision.
  - Electricity changes by more than 2x between years:
    - One Wilshire: 75,511,146.7 to 255,547,951.5 kBtu.
    - 530 W 6th St: 71,268,050 to 27,290,473.6.
    - t5@sv01: 51,562,528.5 to 244,217,938.4.
    - sjc24: 38.9M to 18.8M.
    - These were not checked against anything else.
  - Present in 2024 but absent from the 2025 file (by Property ID): "ca1", "ca2", prime data centers smf01-01, rancho bernardo data center, coresite sv1 (55 S Market St, typed Office with 46,470 sq ft Data Center), rising realty - garland center (1200 W 7th St, Data Center 349,966 sq ft), 641 walsh ave, infoimage inc, china basin, marathon office building and 2525 main street. Absence from the file does not show closure.
  - Type changes between years: irvine crossing is Data Center in 2024 and Non-Refrigerated Warehouse in 2025; 250 stockton is Data Center in 2024 and Vehicle Dealership in 2025; ceo/countydatacenter is Office in 2024 and Data Center in 2025.
  - Cities with their own ordinances are in this file: San Francisco, Los Angeles and San Jose all appear. This corrects the earlier note that such cities "report locally instead".
    - For 200 Paul Ave and 365 Main St, the California kBtu values equal the San Francisco dataset's kWh x 3.412 (2024: 380,216,763.9 kBtu vs 111,435,159.4 kWh; 2025: 354,725,262.5 vs 103,964,027.7). This also shows that San Francisco's `benchmark_year` 2024 and 2025 are the calendar years of the data.
    - Keeping both sets would create duplicate sites under two jurisdictions. California GFA excludes parking (557,226 vs San Francisco's 673,926 sq ft for 200 Paul).
    - 274 Brannan St is typed Office in the California file, with no Data Center use listed, so it was not added. San Francisco types it Data Center.
    - Los Angeles: 600 W 7th St (lax10, 2025: 308,003,574.5 kBtu), One Wilshire and 530 W 6th St are all here, though the earlier notes found no Los Angeles metered source.
  - Some rows typed Data Center have very little energy, as published: 2825-2845 Lafayette St (sjc36, 306,144 sq ft, 1.86M kBtu), 3301-3307 Hillview Ave in Palo Alto (estimated values), 47913 Warm Springs Blvd, 250 Stockton and 641 Walsh (2024). The carmel mountain bldg 3 flag lists 88,000 sq ft of Data Center but uses about 0.2-0.4 GWh.
  - "Used Estimated Energy Values=True" appears on 16 rows: Intel 2024, 818 W 7th St, Verizon Rocklin, Hurricane Electric FMT2 2025, lax4-a 2025, Hillview Ave and others. It is noted per row.
  - One name contains `&amp;` as published. The Kaiser Pleasanton 2024 onsite renewable value is "-1" as published.
  - The builder sets `source_publisher` to "<jurisdiction> open data portal". For these rows the publisher is the California Energy Commission, so the lead may want to override.

## Portland, OR (Commercial Building Energy Performance Reporting) - 9 rows (2025: 9; 2023: 0; 2024: 0)
- Files and sheets:

  | File | Sheet | Rows | Last updated |
  |---|---|---|---|
  | `portlandbuildingenergydata_publication_2023_final_v11072024.xlsx` | `2023 Energy Performance Info` | 933 | 11/07/2024 |
  | `portlandbuildingenergydata_09.30.25.xlsx` | `2024 Energy Performance Info` | 918 | 09/30/2025 |
  | `2025-Energy-Performance-Information-for-Individual-Commercial-Buildings-Spreadsheet.xlsx` | `2025 Energy Performance Info` | 914 | 09/30/2026 |

  The third file is Portland's 2025 workbook, not another city's. Its Background sheet reads "City of Portland Commercial Building Energy Performance Reporting / 2025 Calendar Year Reporting Data". Each workbook also has Background, Certified Top Performers and Glossary sheets.
- Fields: Compliance Status, Building ID, Building Name, Site Address, Year Built, Floor Area (sf), Primary Property Type, ENERGY STAR Score, Certified?, Site EUI (kBtu/sf), Weather Normalized Site EUI (kBtu/sf), Natural Gas Use (therms), **Electricity Use (kWh)** (kWh per the Glossary, "Amount of energy used on site from electric utility providers"), Energy Provider, Electricity Generated from Onsite Renewable Systems (kWh), Total GHG Emissions (Metric Tons CO2e). The 2025 file adds GHG Emissions Intensity. Primary Property Type is calculated by Portfolio Manager (Glossary).
- The cited URL is the page given in the brief, https://www.portland.gov/bps/climate-action/energy-reporting/annual-data-and-results. The per-year download URLs in the earlier notes were not matched to these file names.
- Threshold: 20,000 sq ft (Background sheet). The 2024 and 2025 reports add that the rule applies where no more than 50% of the floor area is housing, parking, industrial, warehouse and similar uses.
- Year semantics: "2025 Calendar Year Reporting Data". The reports say "results for the 2025 calendar year" (`2025-Building-Energy-Performance-Reporting-Results_0.pdf`, introduction), "2024 calendar year" (`GRB_COM_..._0925.pdf`) and "calendar year 2023" (`GRB_COM_..._1024.pdf`). So report_year is the calendar year of the data.
- Compliance: 64% for 2023 (605 buildings), 79% for 2024 (822) and 83% for 2025 (863 of 1,040 expected). None of the three reports mentions data centers. The Glossary lists Data Center as an ENERGY STAR-eligible covered type, yet all 9 rows show "Not Eligible".
- **Typed Data Center:** none in 2023 or 2024; 9 in 2025, all Compliant. In GWh: Pittock Block, 921 SW Washington St (20,064,630 kWh = 20.06), PORTLAND OR SW PARK AVE CO, 310 SW Park Ave (10.33), 1225 NW 13th Ave (6.00), BELMONT CO, SE 17th Ave (3.61), ALPINE CO, 1330 NE 102nd Ave (1.98), ATLANTIC MAIN, 2923 NE 24th Ave (1.55), BUTLER CO, N Lombard and Mobile Ave (1.19), PROSPECT MAIN, 5051 SE 71st Ave (1.07), Multnomah Admin Office, 8021-8025 SW Capitol Hill Rd (0.42; site EUI 32.9, low for a data center). The total is 46.2 GWh.
- **Trap: classification.** The 2023 file names three of these Building IDs "Centurylink" or "Century Link" (310 SW Park, 5051 SE 71st and N Lombard). All eight non-Pittock IDs were typed "Other - Technology/Science" in 2023. Their 2025 names ("... CO", "... MAIN") look like telephone central office names, but none matches the builder's telecom regex. **All 9 will classify as `datacenter`.** Making them telephone exchanges needs a lead decision, for example an alias or a regex addition. The file shows no owner field, so none was written.
- **Candidates not put in the CSV.** In these years' files they are typed otherwise and show no data-center use; the evidence is the same Building ID typed Data Center in 2025:

  | Year | Building ID | Name as published | Type | Floor area | Electricity Use (kWh) | Site EUI |
  |---|---|---|---|---|---|---|
  | 2023 | 1N1E34CC-4800-B1 | Pittock Block | Office (Potential Error(s)) | 352,846 | 20,913,080 | Not Available |
  | 2023 | 1N1E34CC-3400-B1 | Centurylink (310 SW PARK AVE) | Other - Technology/Science | 235,538 | 10,717,310 | 155.3 |
  | 2023 | 1N1E33AA-1800-B1 | 1225 NW 13TH AVE | Other - Technology/Science | 57,140 | 5,661,236 | 338.0 |
  | 2023 | 1S1E02AB-14000-B1 | SE 17TH AVE | Other - Technology/Science | 65,500 | 3,928,949 | 204.7 |
  | 2023 | 1N2E34BB-2600-B1 | 1330 NE 102ND AVE | Other - Technology/Science | 53,322 | 2,128,143 | 136.2 |
  | 2023 | 1N1E26AD-500-B1 | 2923 NE 24TH AVE | Other - Technology/Science | 42,677 | 1,872,285 | 149.7 |
  | 2023 | 1N1E16AB-4101-B1 | Century Link (N Lombard and Mobile Ave) | Other - Technology/Science | 29,592 | 1,483,694 | 171.1 |
  | 2023 | 1S2E17BD-400-B1 | Centurylink (5051 WI/ SE 71ST AVE) | Other - Technology/Science | 23,938 | 1,152,859 | 164.3 |
  | 2023 | 1S1E21CB-4600-B1 | 8021-8025 SW CAPITOL HILL RD | Other - Technology/Science | 43,048 | 721,274.375 | 57.2 |
  | 2024 | 1N1E34CC-4800-B1 | Pittock Block | Office | 352,846 | 20,231,010 | 196.9 |
  | 2024 | 1N2E34BB-2600-B1 | ALPINE CO | Other - Technology/Science | 53,322 | 2,132,175 | 136.4 |

  In 2024 the other seven IDs are Non-Compliant with no data. The three rows named Centurylink in 2023 meet the "name" test only as telephone exchanges.
- Other traps: EUI and gas cells are stored as single-precision floats (149.699996948242). The CSV gives them at the sheet's display precision (#,##0.0 / #,##0). Electricity is given as stored; only Multnomah Admin Office is fractional (415494.40625, displayed 415,494). Pittock Block's floor area is 352,846 in 2023-2024 and 367,034 in 2025. Several addresses are not street addresses as published, for example "SE 17TH AVE" and "N Lombard and Mobile Ave (SE corner)".

## Ontario EWRB 2022 - 0 rows proposed
- File: `energy_large_building_energy_water_ghgs_2022.xlsx`, one sheet `ODC Final Dataset` with 6,864 rows (one per EWRB_ID) and 32 columns. Dataset: https://data2.ontario.ca/dataset/energy-and-water-usage-of-large-buildings-in-ontario (mirror https://open.canada.ca/data/en/dataset/0eab2faf-6186-4a5b-8de1-b15872943c24).
- Fields: EWRB_ID, City, Postal_Code (3-character FSA only), PrimPropTypCalc, PrimPropTypSelf, Largest_PropTyp, All_Prop_Types, Thrd_Party_Cert, WN_Sit_Elc_Int1/2, WN_Sit_Gas_Int1/2/3, water intensities, Site_EUI1/2, Source_EUI1/2, WN_Site_EUI1/2, WN_Source_EUI1/2, GHG_Emiss_Int1/2, Ener_Star_Score, Ener_Star_Certs, Data_Qual_Check, Data_Qual_Date, and "Calculated with new source factors (Y/N)".
  - **The file has no property name, street address, floor area or absolute energy use.** Electricity appears only as a weather-normalised intensity, with no unit label.
  - In every row, WN_Sit_Elc_Int2 / WN_Sit_Elc_Int1 = 25.806 and Site_EUI2 / Site_EUI1 = 25.806. That is the GJ/m² to ekWh/ft² factor, so "1" is probably GJ/m² and "2" ekWh/ft². This is inferred; the data dictionary is a separate resource and was not read.
  - No kWh figure can be transcribed, so no row could feed the electricity table.
- Year: the file does not state the year beyond its name. Data_Qual_Date is mostly April to October 2023 (3,230 "Not Available"), which fits calendar-year 2022 data reported in 2023. Threshold (from the earlier notes, dataset page): over 100,000 sq ft.
- **Data Center:** 0 rows in PrimPropTypCalc, PrimPropTypSelf or Largest_PropTyp. 89 rows list Data Center among All_Prop_Types: 82 Office, 2 Mixed Use, and 1 each Manufacturing, Convention Center, Financial Office, Other and Distribution Center. Their electricity intensities are 5-74 ekWh/ft², typical of offices with server rooms, so none is clearly a datacenter and none was added. The highest are EWRB_ID 136526 (Mississauga L5K, Office, 73.5), 101503 (Kanata, Manufacturing, 63.1) and 109797 (Markham, Office, 53.1).
- **Toronto targets: not identifiable.** There is no address field. The FSAs M5J (151 Front St W), M6K (905 King St W) and M5A (45 Parliament St) have 49, 61 and 55 rows, none typed Data Center. Their highest Site_EUI2 values are 61.99 (M5J, "Other"), 74.09 (M6K, Strip Mall) and 59.73 (M5A, Office), and none lists Data Center except ordinary offices. No row there has a datacenter-like intensity. The three buildings are either not in the published file or cannot be told apart.
- Builder trap, if Ontario rows are ever added: `feed_bench` hard-codes `country: "USA"` and `usa-bench-` site ids. Rows with address "not found" would also collapse into one site.
