# Building energy benchmarking disclosures - Data Center rows (notes)

Compiled 2026-10-23; California statewide and Portland added 2026-10-24 (last section). Output table: `benchmarking_datacenters.csv` (one row per building-year as transcribed). Raw per-jurisdiction pulls are in `raw/`. Every figure in the CSV was read from the query_url shown on that row; nothing was estimated. "not found" = field empty / "Not Available" / null in the source.

## Method caveats (read first)
- Direct downloads were blocked; all data came through page fetches. Two behaviours of the fetch route shaped the queries and matter to a checker:
  1. The fetch cache is keyed on URL path only (query string ignored for ~15 min), so the same Socrata dataset was hit through alternative paths (`/resource/<id>.json`, `/resource/<id>.csv`, `/api/id/<id>.json`, `/api/id/<id>.csv`) and host-case variants (`DATA.`, `Data.`, `dAta.cityofnewyork.us`). These are equivalent endpoints; a checker can use any of them.
  2. URLs longer than ~230 characters are rejected, and some `$query`/`$select` parameters were silently dropped by the server/proxy combination (the full dataset came back). Rows were only recorded from responses where the filter demonstrably applied.
- Values were extracted from the response by the fetch tool's text extraction. For the wide NYC and Philadelphia responses, numbers were transcribed from tables; spot-check against the query_url.
- `electricity_kwh` column: kWh only where the dataset field is in kWh (NYC, Seattle, SF, DC, Montgomery, Cambridge). Chicago and Philadelphia publish electricity in kBtu only; those cells carry the kBtu field name and value and say "NOT kWh". No conversion was done.

## New York City (Local Law 84) - 137 rows (2023: 68, 2024: 69)
- Dataset: "NYC Building Energy and Water Data Disclosure for Local Law 84 2023 to Present (Data for Calendar Year 2022-Present)", id `5zyy-y8am`, https://data.cityofnewyork.us/d/5zyy-y8am (last modified 2026-04-21 per data.gov). Row counts by report_year: 2022 = 30,485; 2023 = 33,684; 2024 = 39,090 (query: `https://data.cityofnewyork.us/resource/5zyy-y8am.json?$select=report_year,count(*)&$group=report_year`). Latest year = 2024 (calendar year).
- Column dictionary: https://data.cityofnewyork.us/api/views/5zyy-y8am/columns.json (only first 44 columns read). Fields used: `report_year`, `property_id`, `property_name`, `address_1`, `primary_property_type` ("Primary Property Type - Portfolio Manager-Calculated"), `primary_property_type_self`, `property_gfa_self_reported`, `electricity_use_grid_purchase` (kBtu), `electricity_use_grid_purchase_1` (kWh - unit inferred: 288,146,294.8 / 84,450,838.1 = 3.412 on 60 Hudson 2022, and it matches `electricity_weather_normalized` kWh magnitude; the display name of `_1` was not read from the dictionary), `natural_gas_use_kbtu`, `district_steam_use_kbtu`, `site_eui_kbtu_ft`, `energy_star_score`, `list_of_all_property_use`.
- Data Center is a reportable Portfolio Manager type; dataset also carries data-center-specific fields (`data_center_pue`, `data_center_it_energy`, `alert_data_center_issue_with` ...). All were "Not Available" on the known datacenters checked.
- Threshold: LL84 covers buildings > 25,000 sq ft (not re-verified this session).
- Traps:
  - 187 rows (2022-2024) have `primary_property_type = Data Center`; most are Verizon central offices (names `CO/GLC ...` in 2022-23, `CO/VZT ...` in 2024; telecom switching buildings, 30k-300k sq ft, 1-16 GWh/yr). Also City of New York sites (DOITT Technology Center 11 Metrotech, DCAS PSAC II 350 Marconi St, OEM HQ 165 Cadman Plaza), a condo (Stella Towers, 425 W 50th - self-selected Data Center, surely wrong) and a junk record (`lgjsdliihg`, address `mm`, 2023). Type is self-selected.
  - The real carrier hotels are typed Office and report whole-building totals: 60 Hudson St (Western Union Building, property_id 2614608) IS typed Data Center: 84.45 GWh (2022), 87.18 GWh (2023), 85.54 GWh (2024; address_1 given as "56 Hudson Street" in 2024). 111 8th Ave (Office; Data Center sub-use 531k-616k sq ft): 144.7 GWh (2022), 148.1 GWh (2023), 130.8 GWh (2024). 375 Pearl St (Office; Data Center sub-use 449k-508k sq ft): 37.7 GWh (2022), two 2023 records (39.69 / 39.70 GWh, one named "375 Pearl Street - data" with 806k sq ft Office only), 41.3 GWh (2024). 85 10th Ave (Office; Data Center sub-use 61k-119k sq ft): 21.2 / 27.7 / 17.7 GWh. 325 Hudson St (Office; Data Center sub-use 34k-63k sq ft): 5.45 GWh (2023), 7.55 GWh (2024). 32 Avenue of the Americas: no row matched `upper(address_1) like '32 AVENUE%'` - not found (may be listed under another spelling).
  - 2023 has duplicate rows for property_id 4409724 (both kept, flagged). 2023 Stella Towers site_eui = 37,827.6 as given (nonsense value).
  - Older per-year datasets ("Energy and Water Data Disclosure for Local Law 84 20xx (Data for Calendar Year 20xx-1)") and `q5ew-mccs` were not used; `q5ew-mccs` returned a client error on first fetch and was not retried.

## Chicago - 10 rows (2022: 5, 2023: 5); 21 rows 2019-2023 in raw/
- Dataset: "Chicago Energy Benchmarking", id `xq83-jr8c`, https://data.cityofchicago.org/d/xq83-jr8c. Rows per data_year (group-by query): 2019 3,438; 2020 3,582; 2021 3,550; 2022 3,613; 2023 3,438. Latest = 2023. Threshold: buildings over 50,000 sq ft (dataset description).
- Fields: `data_year`, `id`, `property_name`, `reporting_status`, `address`, `primary_property_type`, `gross_floor_area_buildings_sq_ft`, `energy_star_score`, `electricity_use_kbtu`, `natural_gas_use_kbtu`, `district_steam_use_kbtu`, `district_chilled_water_use_kbtu`, `site_eui_kbtu_sq_ft`, `chicago_energy_rating`. No kWh field.
- Data Center rows: 350 E Cermak (Digital Lakeside, id 101185): 987.6 / 1,004.0 / 1,114.5 million kBtu electricity in 2020/21/22 plus 363-456 million kBtu district chilled water; 600 S Federal (Digital Printer's Row, id 168367) ~131 million kBtu; 427 S LaSalle (CoreSite CH1) 139-155 million kBtu; 601 W Polk; 1432 S Clinton (CoreSite CH2, from 2022); 725 S Wells (1547 CSR, 2023); 2800 S Ashland (CHI1 - Chicago DC1, 361 million kBtu, 2023).
- Traps: 350 E Cermak and 600 S Federal have NO 2023 row typed Data Center; `?data_year=2023&id=101185` and `&id=168367` both returned `[]`, so they appear absent from the 2023 data entirely (or under another id). 840 S Canal St was not found among Data Center rows. Rows with reporting_status "Not Submitted"/"Exempt" carry no energy fields.

## Seattle - 16 rows (2024: 4, 2025: 12); 46 rows 2015-2025 in raw/
- Dataset: "Building Energy Benchmarking Data, 2015-Present", id `teqw-tu6e`, https://cos-data.seattle.gov/d/teqw-tu6e (data.seattle.gov resolves here). Threshold: non-residential and multifamily > 20,000 sq ft (dataset description). Latest datayear = 2025 (first row of dataset is datayear 2025).
- Fields: `datayear`, `osebuildingid`, `buildingname`, `address`, `epapropertytype`, `largestpropertyusetype`, `largestpropertyusetypegfa`, `propertygfatotal`, `energystarscore`, `siteeui_kbtu_sf`, `electricity_kwh`, `electricity_kbtu`, `naturalgas_therms`, `steamuse_kbtu`, `compliancestatus`, `complianceissue`.
- Westin Building Exchange, 2001 6th Ave (osebuildingid 753): 77,368,680 kWh (2024), 73,461,520 kWh (2025); 2020 5th Ave "Data Center" (id 49780): 29.1 GWh (2024), 29.4 GWh (2025); 1122 3rd Ave Centurylink 3rd Ave 3-D: 13.9 / 13.8 GWh; UW Tower Data Center 4310 12th Ave NE: 10.2 GWh (2024; no 2025 row). 2025 adds eight Lumen/Centurylink central offices and two "WA ... W00xxx" sites typed Data Center.
- Traps: Westin was typed "Mixed Use Property" in 2019-2020 with Data Center as largest use; 2022 Westin row Not Compliant ("Missing EUI, Incomplete Natural Gas Data"). Type is self-selected.

## San Francisco - 8 rows (2024: 4, 2025: 4); 60 rows 2011-2025 in raw/
- Dataset: "Existing Buildings Energy Performance Ordinance Report", id `96ck-qcfe`, https://data.sfgov.org/d/96ck-qcfe (API redirects to https://data.sf.gov). Updated monthly; data_as_of 2026-10-08. Latest benchmark_year = 2025.
- Fields: `benchmark_year`, `parcel_number`, `building_name`, `building_address`, `category` (property type), `property_type` (Commercial/Municipal), `floor_area`, `energy_star_score`, `site_eui`, `electricity_use_grid_purchase` (no unit in name; kWh inferred from site_energy_use/electricity = 3.412 on all-electric rows), `site_energy_use` (kBtu), `benchmark_status`. No gas field.
- Data Center rows: 200 Paul Ave (Digital Realty Trust, 673,926 sq ft): 112.4 GWh (2023), 111.4 GWh (2024), 104.0 GWh (2025); 365 Main St (240,291 sq ft): 30.6 / 29.0 / 28.6 GWh; 630 3rd St: 6.1 / 6.6 / 7.2 GWh; 274 Brannan St: 1.8 / 1.6 / 1.7 GWh.
- Traps: benchmark_year is a compliance-year label ("2025 - Complied"); whether it is the calendar year of the metered data was not confirmed. Filtering by `$query` on this portal silently returned the full dataset; the simple filter `?category=Data%20Center` worked.

## Washington DC - 3 rows (2022, 2023, 2025)
- Dataset: DOEE "Building Energy Benchmarking", ArcGIS layer https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Environment_Energy_WebMercator/FeatureServer/45 (catalog: https://opendata.dc.gov / data.gov "building-energy-benchmarking"). Layer 75 is the BEPS "Building Energy Performance Data" layer (no metered fields).
- Fields: `REPORTINGYEAR`, `REPORTSTATUS`, `PMPROPERTYID`, `PROPERTYNAME`, `ADDRESSOFRECORD`, `PRIMARYPROPERTYTYPE_SELFSELECT`, `PRIMARYPROPERTYTYPE_EPACALC`, `REPORTEDBUILDINGGROSSFLOORAREA`, `ENERGYSTARSCORE`, `SITEEUI_KBTU_FT`, `ELECTRICITYUSE_GRID_KWH`, `NATURALGASUSE_THERMS`, `DISTRSTEAM_KBTU`, `DISTRCHILLEDWATER_KBTU`.
- Only 7 Data Center features in the whole layer: Northern Exchange Condominium, 1401 R St NW (2022, 2023, 2025: 5.50 / 5.01 / 4.57 GWh) and 3919 Benning Rd NE "Network Operations Center" (2012-2018, "Data Under Review by DOEE", ~3-4 GWh). No 2024 row for Northern Exchange; REPORTINGYEAR semantics (data year vs submission year) not confirmed. Threshold not read this session.

## Philadelphia - 32 rows (2023: 17, 2024: 15)
- Dataset: "Large Building Energy Benchmarking Data", https://opendataphilly.org/datasets/large-building-energy-benchmarking-data/ - one ArcGIS FeatureServer per year: `.../properties_reported_2024/FeatureServer/0` and `.../properties_reported_2023/FeatureServer/0` on services.arcgis.com/fLeGjb7u4uXqeF9q. Years 2013-2024; latest = 2024 (data_year field). Citywide reports: https://www.phila.gov/media/20260806101736/2024-Citywide-Energy-Benchmarking-Report.pdf
- Fields: `data_year`, `portfolio_manager_id`, `property_name`, `street_address`, `primary_prop_type_epa_calc`, `total_floor_area_bld_pk_ft2`, `electric_use_kbtu`, `natural_gas_use_kbtu`, `steam_use_kbtu`, `energy_star_score`, `site_eui_kbtuft2`, `benchmarking_status`, `compliance_type`. Electricity in kBtu only.
- 401 N Broad (401 North Broad Lessee LLC, 1,296,804 sq ft): 410,033,632 kBtu electricity in 2023 (= ~120 GWh if /3.412; conversion not applied in CSV); no 2024 row typed Data Center was returned. Gratz Data Center 1000 W Tabor Rd (2023). The rest are Verizon central offices (CO/GLC 2023 -> CO/VZT 2024); 900 Race St is the largest at 65-67 million kBtu.
- Traps: 2023 has "Voluntarily Complied" rows with null floor area; 401 N Broad natural_gas_use_kbtu=767.9 and steam 0 as given.

## Montgomery County MD - 4 rows
- Dataset: "2024 Energy Benchmarking All Sites", id `g6nn-rgwc`, https://data.montgomerycountymd.gov/d/g6nn-rgwc (updated 2025-09-23). Older: `izzs-2bn4` "Building Energy Benchmarking Results" (2023) - filter query returned a client error, not used.
- Fields: `reporting_year_start_date`, `benchmarking_group`, `espm_property_id`, `building_name`, `address`, `primary_property_type_self`, `primary_property_type_epa` (lower-case values), `reported_property_gross_floor`, `energy_star_score`, `site_eui`, `electricity_kwh`, `natural_gas_therms`, `benchmarking_report_status`.
- Data centers: 12401 Prosperity Dr (13.6 GWh), 11961 Bournefield Way (14.3 GWh), 20441 Century Blvd Germantown (17.7 GWh), 75 W Watkins Mill Rd (2.2 GWh). Trap: dataset has one row per site; `reporting_year_start_date` (2017/2023) looks like the first year the site reported, not the data year; the data year is taken from the dataset title (2024) - verify. energy_star_score 0 as given.

## Cambridge MA (BEUDO) - 8 rows (2023: 4, 2024: 4); 40 rows 2015-2024 in raw/
- Dataset: id `72g6-j7aq`, https://data.cambridgema.gov/d/72g6-j7aq. Fields: `data_year`, `reporting_id`, `address`, `owner`, `beudo_property_type`, `primary_property_type_self_selected`, `all_property_uses`, `property_gfa_self_reported_ft2`, `compliance_status`, `electricity_use_grid_purchase_kwh`, `electricity_use_grid_purchase_kbtu`, `natural_gas_use_therms`, `site_eui_kbtu_ft2`, `energy_star_score`.
- Data centers (all Kendall/East Cambridge): 185/205 Bent St (3.9-4.1 GWh), 89 Fulkerson St (2.7-3.1 GWh), 300 Bent St (0.2-0.3 GWh; EUI 8-11, i.e. not operating as a data center), 250 Bent St (AT&T, 138k sq ft: no energy values 2023-2024, Non-Compliant 2024; 11.6 GWh in 2022).

## Jurisdictions checked with no Data Center rows retrieved
- **Los Angeles (EBEWE)**: data.lacity.org `9yda-i4ya` ("Existing Buildings Energy & Water Efficiency (EBEWE) Program") holds only compliance status (`building_address`, `building_id`, `compliance`, `program_year`, `building_programclass`); no metered values. LADBS publishes compliance-status PDFs only (https://ladbs.org/services/green-building-sustainability/existing-buildings-energy-water-efficiency-program/ebewe-compliance-status). No public metered disclosure dataset found for 600 W 7th / 1 Wilshire / 530 W 6th.
- **Boston (BERDO)**: data.boston.gov blocks the fetch proxy (robots). Dataset page: https://data.boston.gov/dataset/b09a8b71-274b-4365-9ce6-49b8b44602ef - download needed.
- **Denver (Energize Denver)**: ArcGIS layer https://services1.arcgis.com/zdB7qR0BtYrg0Xpl/ArcGIS/rest/services/2025_Master_Data_Set/FeatureServer/0 has the right fields (`Reporting_Year`, `Primary_Property_Type_EPA_Calculated`, `Electricity_Use___Grid_Purchase__KWh_`, `Natural_Gas_Use__kBtu_`, `Site_EUI__kBtu_sq_ft_`, `Energy_Star_Score`, `Master_Sq_Ft`, target-EUI fields) but query returns error 499 "Token Required" - download via the Denver Open Data Catalog needed.
- **Portland OR**: annual Excel files only (no API): 2025 https://www.portland.gov/bps/climate-action/energy-reporting/documents/2025-energy-performance-information-individual/download ; 2024 .../2024-energy-performance-information-individual/download ; 2023 .../2023-energy-performance-information-individual/download - download needed. Threshold not stated on page.
- **California AB 802 (CEC)**: statewide disclosure files per year, format not stated on page: 2025 https://www.energy.ca.gov/media/13355 ; 2024 https://www.energy.ca.gov/media/12019 ; 2023 https://www.energy.ca.gov/media/10811 - download needed. Threshold > 50,000 sq ft (program page). Exemptions are in the Commercial fact sheet / Title 20 regs, which were not read; whether data centers are excluded was NOT determined (Santa Clara coverage unknown). Cities with exempted local ordinances (SF, LA, SJ...) report locally instead.
- **Ontario EWRB**: data.ontario.ca blocks the fetch proxy (robots). Dataset "Energy and water usage of large buildings in Ontario", resources e.g. https://data2.ontario.ca/dataset/energy-and-water-usage-of-large-buildings-in-ontario/resource/980458c7-81df-4ffe-8543-71907583cc87 and .../resource/5e273fb6-445f-4d50-bdb8-9c36e995b23f - download needed (151 Front St W, 905 King St W not checked).
- **Minneapolis**: results published as PDFs only (https://www.minneapolismn.gov/media/-www-content-assets/documents/2023-Energy-Benchmarking-Report-private-building-data.pdf) and a dashboard; not parsed.
- **San Jose**: only PDF documents on sanjoseca.gov found; no structured disclosure dataset located.
- **Atlanta**: no open disclosure dataset found via search (only compliance guides); not retrieved.
- **Austin (ECAD)**: only 2013-2016 "ECAD Commercial Reported Data" datasets found on data.gov; recent years not located.
- **Pittsburgh**: only compliance pages found; no disclosure dataset located.
- **Kansas City, St Louis, Orlando**: not checked yet.


# Second pass (Boston, Kansas City; downloads needed)

# Benchmarking portals, pass 2 — route notes (2026-10-23)

Method: page fetches and web search only (no direct downloads). Every URL below was requested exactly as written.
Observed fetcher behaviour (affects reproducibility): (a) requests over ~250 characters appear to be truncated at the query string; (b) the fetcher caches by path and ignores the query string for ~15 min, so a second query to the same `/query` or `.json` path returned the first response. Where a route is marked "query endpoint returned the HTML form", that is most likely this cache effect, not a server refusal; re-run the exact URL from a clean client.

## Boston, MA — BERDO  (ROWS: 33)
- Route that worked: ArcGIS Online feature service behind the City's "BERDO Reporting 2023 (Static)" web app.
  - Service: https://services.arcgis.com/sFnw0xNflSi8J0uh/ArcGIS/rest/services/berdo_static_2023/FeatureServer/0
  - Item metadata (boston.maps.arcgis.com search): id 3e2cf950eadb4811a90e7601a86b67c1, created 2023-11-28, snippet "BERDO reporting data for 2023 (static) used in the Building Energy Reporting web application for 2023".
  - Query used: https://services.arcgis.com/sFnw0xNflSi8J0uh/ArcGIS/rest/services/berdo_static_2023/FeatureServer/0/query?where=All_Property_Types%20LIKE%20%27%25Data%20Center%25%27&outFields=*&returnGeometry=false&f=json  -> 33 features.
- Fields: BERDO_ID, Tax_Parcel_ID, Property_Owner_Name, Building_Address, Building_Address_City, Building_Address_Zip_Code, Reported_Gross_Floor_Area__Sq_F, Largest_Property_Type, All_Property_Types, Site_EUI__Energy_Use_Intensity_ (kBtu/ft2), Energy_Star_Score, Total_Site_Energy_Usage__kBtu_, Natural_Gas_Usage__kBtu_, Electricity_Usage__kBtu_, Renewable_System_Electricity_Us, District_Hot_Water_Usage__kBtu_, District_Chilled_Water_Usage__k, District_Steam_Usage__kBtu_, Fuel_Oil_* , Propane, Diesel, Kerosene, Water_Usage_Intensity__Gallons_, Compliance_Status, BERDO_Report_Status, Estimated_Total_GHG_Emissions__ (kgCO2e), Notes. No property-name field (owner name used).
- Units: electricity is published in kBtu, not kWh.
- Threshold (dataset page): non-residential >= 20,000 sq ft; residential >= 15 units. Data Center is a reportable Portfolio Manager type; 9 rows have Largest_Property_Type = Data Center (all Verizon/New England Tel & Tel central offices), the rest list Data Center among All_Property_Types.
- Year: service is labelled "2023"; calendar year of usage not stated on the layer. (Boston's file naming on data.boston.gov labels by reporting year; e.g. the "2020 Reported Energy and Water Metrics" file is named berdo-disclosure-for-calendar-year-2019.xlsx.)
- Latest two years are NOT on any feature service found: the 2025 and 2026 disclosures exist only as XLSX ("download needed"):
  - 2026 Reported Energy and Water Metrics: https://data.boston.gov/dataset/b09a8b71-274b-4365-9ce6-49b8b44602ef/resource/c6edf41e-eb53-45a4-9c52-837b865bf19f/download/2026-berdo-data-disclosure-9.30.26.xlsx
  - 2025 Reported Energy and Water Metrics: https://data.boston.gov/dataset/b09a8b71-274b-4365-9ce6-49b8b44602ef/resource/911db0b1-437f-43ba-86bb-860cc1cd9319/download/2025-reported-energy-and-water-metrics.xlsx
  - 2024 Reported Energy and Water Metrics: https://data.boston.gov/dataset/b09a8b71-274b-4365-9ce6-49b8b44602ef/resource/87521565-7f15-4b8d-a225-ac4df9e3f309/download/2024-reported-energy-and-water-metrics-1.xlsx
  - 2024 Detailed Data Dictionary: https://data.boston.gov/dataset/b09a8b71-274b-4365-9ce6-49b8b44602ef/resource/33c4897d-59e7-4c23-9f96-4d2fbe4e8b7c/download/2024-detailed-data-dictionary.xlsx
- Blocked: data.boston.gov/api/3/action/* (package_search, datastore_search) -> robots_disallowed. The dataset HTML page (https://data.boston.gov/dataset/b09a8b71-274b-4365-9ce6-49b8b44602ef) IS readable. Resource page shows no "Data API" button, so datastore status is unknown.
- Other services on the same AGOL org (listed, not queried): berdo_static_data_23_reporting_map (2022 static, published 2023-07-06; query returned the HTML form, see fetcher note), BERDO_Reporting_2021 (CY2020 data), BERDO2020_dissolve_final2 (CY2019), BERDO_2024_Mapped_DRAFT_02272026_Export (compliance flags only, no energy fields).
- 1 Summer St: not among the 33 Data-Center-tagged rows.

## Kansas City, MO  (ROWS: 12; 2 with metrics, 10 exempt/no-submittal)
- Route: Socrata. Catalog: https://data.kcmo.org/api/views/metadata/v1?search=energy lists
  - p92b-cm6v "2023 Kansas City Energy and Water Consumption Benchmarking for Community Buildings" (dataUpdatedAt 2025-04-01)
  - 8ygr-6znk "2023 Kansas City Energy and Water Consumption Benchmarking for City Buildings" (no Data Center rows in first 3; not filtered — cache note above)
- Query: https://data.kcmo.org/resource/p92b-cm6v.json?primary_type=Data%20Center&$limit=100  -> 12 records (also confirmed via https://data.kcmo.org/resource/p92b-cm6v.csv?primary_type=Data%20Center&$limit=100 and https://data.kcmo.org/api/id/p92b-cm6v.json?primary_type=Data%20Center&$limit=100).
- Fields: benchmarking_id, building_address, building_city, building_state, building_zip, building_name, primary_type, gross_floor_area, submission_status_7, x_coordinate, y_coordinate, owner_company, compliance_required, submission_year, energy_star_score, weather_normalized_site_eui, direct_ghg_emissions_metric, indirect_ghg_emissions_metric, weather_normalized_source, indoor_water_use_all_water, outdoor_water_use_all_water, water_use_all_water_sources.
- No electricity, gas or site-energy columns are published -> electricity_kwh = "not found" for every KC row. Threshold 50,000 sq ft (kcmo.gov). Latest year found: submission_year 2023. Data Center is a reportable type.
- Note: 8 of 12 Data Center rows are AT&T/Bank of America/others marked "exempt" or "noSubmittal".

## California statewide (CEC AB 802)  — download needed
- CEC program page (readable): https://www.energy.ca.gov/programs-and-topics/programs/building-energy-benchmarking-program
  - Threshold: disclosable buildings > 50,000 sq ft GFA; commercial since 2018, multifamily (>=17 utility accounts) since 2019. Latest disclosure: 2025.
  - Files (format not stated on page; previous pass found xlsx): 2025 https://www.energy.ca.gov/media/13355 ; 2024 https://www.energy.ca.gov/media/12019 ; 2023 https://www.energy.ca.gov/media/10811 ; 2022 https://www.energy.ca.gov/media/8751 ; 2021 https://www.energy.ca.gov/media/7213 ; 2020 https://www.energy.ca.gov/media/6032 ; 2019 https://www.energy.ca.gov/media/4639 ; 2018 https://www.energy.ca.gov/media/4640
  - Tableau dashboard (interactive, not fetchable as data): https://tableau.cnra.ca.gov/t/CNRA_CEC_PUBLIC/views/EnergyEfficiencyBenchmarkingDashboard/BenchmarkingDashboard
- data.ca.gov CKAN API: robots_disallowed. No CSV twin found. The public-disclosure subpage returned client_error. Page says nothing about data centers.

## Ontario EWRB — download needed
- data.ontario.ca API: robots_disallowed. Mirror host data2.ontario.ca: dataset HTML page readable, API path returned client_error.
- Dataset page: https://data2.ontario.ca/dataset/energy-and-water-usage-of-large-buildings-in-ontario  (also on open.canada.ca: https://open.canada.ca/data/en/dataset/0eab2faf-6186-4a5b-8de1-b15872943c24)
  - Threshold: buildings > 100,000 sq ft. Years published: 2018–2022 (calendar years). Latest: 2022 English XLSX, 1.6 MiB, updated 2024-02-07. All resources are XLSX (EN/FR per year + data dictionary). Resource ids seen in search: e7292ae5-90b9-4c6c-bd7b-75f4fab48142, 980458c7-81df-4ffe-8543-71907583cc87, 74c0e959-9683-4263-ba24-d047acfef681, 5a352124-2c08-497d-ab44-b819942c3652, 61fed2e6-155e-48ab-b92f-e75c956a68d4, 5e273fb6-445f-4d50-bdb8-9c36e995b23f, bda9443d-dd2b-427f-b239-03820fa2ca3d, 065a6821-229e-4bbf-b78e-a2f63d4fd4d9 (year-to-id mapping not readable from the page; resource page pattern https://data2.ontario.ca/dataset/energy-and-water-usage-of-large-buildings-in-ontario/resource/<id>).
  - Property types follow Portfolio Manager categories (page text), so Data Center is reportable; not verified in data.
  - Toronto target addresses (151 Front St W, 905 King St W, 45 Parliament St, 20 Pullman Ct) not checked — no machine-readable route.

## Denver, CO — Energize Denver — token required
- Public FeatureServer metadata is readable: https://services1.arcgis.com/zdB7qR0BtYrg0Xpl/ArcGIS/rest/services/2025_Master_Data_Set/FeatureServer (table 0 "2025_Master_Data_Set").
- Fields: Building_ID, Compliance_Status, Property_Name, Street, Zipcode, Year_Built, Master_Property_Type, Primary_Property_Type_EPA_Calculated, Master_Sq_Ft, Reporting_Year, Energy_Star_Score, Site_Energy_Use__kBtu_, Site_EUI__kBtu_sq_ft_, Electricity_Use_Grid_Purchase_and_Onsite__KWh_, Electricity_Use___Grid_Purchase__KWh_, Electricity_Use_Onsite_Renewable__kWh_, Natural_Gas_Use__kBtu_, District_Steam_Use__kBtu_, District_Chilled_Water_Use__kBtu_, Total_GHG_Emissions__Metric_Tons_Co2e_, Baseline_EUI, target EUIs, MAI fields.
- Query https://services1.arcgis.com/zdB7qR0BtYrg0Xpl/ArcGIS/rest/services/2025_Master_Data_Set/FeatureServer/0/query?where=Primary_Property_Type_EPA_Calculated%3D%27Data%20Center%27%20OR%20Master_Property_Type%3D%27Data%20Center%27&outFields=*&f=json&resultRecordCount=100  -> error 499 "Token Required".
- denvergov.org/opendata search: robots_disallowed. No CSV found. 910 15th St / 1500 Champa St not checked.

## Portland, OR — download needed (public layer has no kWh)
- Public ArcGIS Server layers (metadata readable):
  - https://www.portlandmaps.com/arcgis/rest/services/Public/BPS_ReadOnly/MapServer/48 "Commercial Building Energy Performance Reporting Records" (current year)
  - https://www.portlandmaps.com/arcgis/rest/services/Public/BPS_ReadOnly/MapServer/64 "... Reporting Archive" (has reporting_year)
  - Fields: Property_Name, Site_Address, Site_Zip, Year_Built, Floor_Area__sf_, property_type, ENERGY_STAR_Score, Site_EUI__kBtu_sf_, site_eui_weather, Source_EUI__kBtu_sf_, source_eui_weather, electric_generated, emissions (MtCO2e), Verified, generalizedUseType, property_notes. NO electricity/gas consumption fields.
  - Every /query request (several encodings, MapServer and FeatureServer paths) returned the HTML query form — see fetcher note; re-run from a clean client: .../MapServer/64/query?where=property_type%3D%27Data%20Center%27&outFields=*&returnGeometry=false&f=json
- Threshold: 20,000 sq ft report; City publishes metrics for >= 50,000 sq ft. Latest: 2025 results posted.
- Spreadsheets (Excel): 2025 https://www.portland.gov/bps/climate-action/energy-reporting/documents/2025-energy-performance-information-individual/download ; 2024 https://www.portland.gov/bps/climate-action/energy-reporting/documents/2024-energy-performance-information-individual/download ; 2023 https://www.portland.gov/bps/climate-action/energy-reporting/documents/2023-energy-performance-information-individual/download
- Pittock Block (921 SW Washington St) not checked.

## Minneapolis, MN — PDF only / no open-data layer found
- opendata.minneapolismn.gov search API (api/search/v1 and hub api/v3/datasets?q=benchmarking) returned no Minneapolis benchmarking dataset. data.minneapolismn.gov catalog API: client_error.
- City publishes PDFs: 2023 private buildings https://www.minneapolismn.gov/media/-www-content-assets/documents/2023-Energy-Benchmarking-Report-private-building-data.pdf ; 2023 public buildings https://www.minneapolismn.gov/media/-www-content-assets/documents/2023-Energy-Benchmarking-Report-public-building-data.pdf  (download needed).
- Minnesota statewide program map: https://map.benchmarkingmn.org/ (JS app; no data endpoint visible in HTML). 511 11th Ave S not checked.

## Pittsburgh, PA — no building-level disclosure found
- data.wprdc.org API: robots_disallowed. Only WPRDC energy dataset surfaced via data.gov harvest: "Municipal Building Energy Usage" 2009-2014 (139 municipal buildings), CSV https://data.wprdc.org/dataset/7b8896c5-867d-428d-a2e3-bdb732655846/resource/90e87a5c-0cdd-4534-ab84-0cc523b110f5/download/municpal-building-energy-use-2009-2014.csv — not the benchmarking ordinance disclosure. Ordinance pages at pittsburghpa.gov found; no public dataset link found.

## St. Louis, MO — no public dataset found
- Office of Building Performance page (https://www.stlouis-mo.gov/government/departments/public-safety/building/building-performance/index.cfm): threshold 50,000 sq ft; no data/map/download links on page.

## Salt Lake City, UT — no public dataset found
- Elevate Buildings page (https://www.slc.gov/sustainability/elevate-buildings/): links only to a guide PDF, the Portfolio Manager data-request (2025 data) and a Building-ID lookup (https://buildingbenchmark.slc.gov/). No disclosure dataset/map found.

## Statewide programs
- Colorado (energyoffice.colorado.gov/bpc): covered buildings >= 50,000 sq ft; 2026 reporting window Jul 1–Nov 1; no public building-level data linked. (Denver data is the only Colorado building-level source found; token-gated.)
- Maryland (MDE BEPS): search surfaced only guidance PDFs; no statewide building-level dataset found. "2024 Energy Benchmarking All Sites" on data.gov is Montgomery County (already covered in pass 1).
- Washington State (Commerce Clean Buildings): search surfaced guides and legislation only; no statewide building-level dataset found (Seattle city dataset already covered).
- New Jersey (njcleanenergy.com/benchmarking): page lists no public dataset, threshold or years; no building-level disclosure found.

## Not reached yet
Atlanta, Austin, Orlando, Los Angeles EBEWE, San Jose, Boston 1 Summer St specifically, Toronto addresses specifically.

## 2026-10-24: California statewide, Portland OR and Ontario (spreadsheets downloaded in a browser)

**Decisions applied to the reader's proposal (2026-10-24).** The reader proposed 217 rows; 178 were added to `benchmarking_transcribed.csv`:
- Left out (7 rows): California rows in San Francisco, which the San Francisco dataset already covers (the values agree, as below), so that no building appears under two jurisdictions.
- Left out (32 rows): buildings typed otherwise (offices, laboratories, a chip campus) whose listed Data Center use is under 40% of their floor area; their whole-building electricity is mostly not datacenter load. Kept: typed-otherwise buildings whose Data Center use is at least 40% of floor area (Garland Center, Irvine Crossing, Carmel Mountain bldg 3) or whose name says data center, and CoreSite SV1.
- CoreSite SV8 (3035 Stender Way), 2024: the published electricity (413,201,894,799.9 kBtu, about 121,000 GWh) is about 1,000 times the 2025 value and is not ingested; the row keeps the published value in its notes.
- Classification: a building whose own name says data center or data centre is a datacenter whatever its type (Prime SMF01, Rancho Bernardo, the county data center, 9 First American Way); Portland's buildings filed under Lumen office names ("BELMONT CO", "ATLANTIC MAIN") are telephone exchanges (the 2023 file names three of them Centurylink). Verizon's Rocklin NEC stays a telephone exchange under the existing rule.
- Publisher: the California rows are credited to the California Energy Commission and the Portland rows to the City of Portland's Bureau of Planning and Sustainability, not to an open-data portal.
- Ontario: no row added; the 2022 file gives no address, floor area or absolute energy, so its datacenters cannot be identified.


Compiled 2026-10-24 from files downloaded in a browser (folder `fetched/from_downloads/`). Proposed rows: `bench_new_rows.csv` (217 rows, same header as `benchmarking_transcribed.csv`). Every figure was read from the spreadsheet cell named in the row's notes (file, sheet, row number). Nothing was estimated or converted in the CSV. "not found" = empty cell, "Not Available" or "Not Provided". GWh figures in this note are derived here for orientation only (kBtu / 3,412,141.6 per GWh; kWh / 1,000,000). They are not in the CSV.

### Second reading (done, no disagreements)
- First read: openpyxl (read-only, cached values). Second read, two independent methods: (1) `pandas.read_excel`, rows looked up by Portfolio Manager Property ID or Portland Building ID; (2) a raw parse of the sheet XML inside the .xlsx (zipfile + ElementTree, no openpyxl), looked up by the same ids.
- All 217 electricity cells in the CSV (including the 3 "not found") agree across all three reads. Gross floor area, property name and (Portland) the Data Center type were also re-checked: no disagreements.
- Data Center counts were re-derived with pandas value counts: California 83 (2025) and 80 (2024). These match the rows extracted.
- Builder check: the logic of `bench_kind`, `bench_building_key` and `first_number` was copied and run on the proposed rows. Every electricity cell parses to the right number and unit (kBtu for California, kWh for Portland). No two property ids share a building key, and each property id maps to one key across years. California addresses omit the ZIP code because 200 Paul Ave is filed under 94110 in 2024 and under 94124 in 2025, which would otherwise create two sites. The ZIP is kept in the notes.

### California statewide (CEC Building Energy Benchmarking Program, AB 802) - 208 rows (2024: 105, 2025: 103)
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

### Portland, OR (Commercial Building Energy Performance Reporting) - 9 rows (2025: 9; 2023: 0; 2024: 0)
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

### Ontario EWRB 2022 - 0 rows proposed
- File: `energy_large_building_energy_water_ghgs_2022.xlsx`, one sheet `ODC Final Dataset` with 6,864 rows (one per EWRB_ID) and 32 columns. Dataset: https://data2.ontario.ca/dataset/energy-and-water-usage-of-large-buildings-in-ontario (mirror https://open.canada.ca/data/en/dataset/0eab2faf-6186-4a5b-8de1-b15872943c24).
- Fields: EWRB_ID, City, Postal_Code (3-character FSA only), PrimPropTypCalc, PrimPropTypSelf, Largest_PropTyp, All_Prop_Types, Thrd_Party_Cert, WN_Sit_Elc_Int1/2, WN_Sit_Gas_Int1/2/3, water intensities, Site_EUI1/2, Source_EUI1/2, WN_Site_EUI1/2, WN_Source_EUI1/2, GHG_Emiss_Int1/2, Ener_Star_Score, Ener_Star_Certs, Data_Qual_Check, Data_Qual_Date, and "Calculated with new source factors (Y/N)".
  - **The file has no property name, street address, floor area or absolute energy use.** Electricity appears only as a weather-normalised intensity, with no unit label.
  - In every row, WN_Sit_Elc_Int2 / WN_Sit_Elc_Int1 = 25.806 and Site_EUI2 / Site_EUI1 = 25.806. That is the GJ/m² to ekWh/ft² factor, so "1" is probably GJ/m² and "2" ekWh/ft². This is inferred; the data dictionary is a separate resource and was not read.
  - No kWh figure can be transcribed, so no row could feed the electricity table.
- Year: the file does not state the year beyond its name. Data_Qual_Date is mostly April to October 2023 (3,230 "Not Available"), which fits calendar-year 2022 data reported in 2023. Threshold (from the earlier notes, dataset page): over 100,000 sq ft.
- **Data Center:** 0 rows in PrimPropTypCalc, PrimPropTypSelf or Largest_PropTyp. 89 rows list Data Center among All_Prop_Types: 82 Office, 2 Mixed Use, and 1 each Manufacturing, Convention Center, Financial Office, Other and Distribution Center. Their electricity intensities are 5-74 ekWh/ft², typical of offices with server rooms, so none is clearly a datacenter and none was added. The highest are EWRB_ID 136526 (Mississauga L5K, Office, 73.5), 101503 (Kanata, Manufacturing, 63.1) and 109797 (Markham, Office, 53.1).
- **Toronto targets: not identifiable.** There is no address field. The FSAs M5J (151 Front St W), M6K (905 King St W) and M5A (45 Parliament St) have 49, 61 and 55 rows, none typed Data Center. Their highest Site_EUI2 values are 61.99 (M5J, "Other"), 74.09 (M6K, Strip Mall) and 59.73 (M5A, Office), and none lists Data Center except ordinary offices. No row there has a datacenter-like intensity. The three buildings are either not in the published file or cannot be told apart.
- Builder trap, if Ontario rows are ever added: `feed_bench` hard-codes `country: "USA"` and `usa-bench-` site ids. Rows with address "not found" would also collapse into one site.
