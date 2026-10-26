# Climate TRACE — research notes for a "datacenters" facility-type proposal

Last checked: 2026-10-20. Method: web search and page fetches only (direct downloads blocked). Direct fetches of `api.climatetrace.org`, `github.com/climatetracecoalition/*`, `zenodo.org/records/19952746`, the BigQuery guide PDF and `climatetrace.org/sectors` were intermittently blocked by the session proxy; what was and was not confirmed is stated per section and summarised at the end.

Machine-readable companion: `sites/climate_trace_schema.json`.

---

## 0. One-paragraph summary for the proposal

Climate TRACE (climatetrace.org) is a non-profit coalition, secretariat WattTime, co-founded by Gavin McCormick (WattTime) and Al Gore. Current release is **v5.11.0 (24 Sep 2026, monthly data through July 2026)**, 2,765,771 emissions sources summarised from 744,678,997 assets, CC BY 4.0. Its asset-level CSVs have a fixed 44-column emissions schema plus a 19-column ownership schema and a per-gas confidence file (ratings very high / high / medium / low / very low). There is **no datacenter or electricity-consumer subsector**; the Buildings sector covers only onsite fuel combustion, and the Power sector covers generation only. However, (a) since v5.11.0 three industrial subsectors (oil & gas production/transport, aluminium, pulp & paper) report **Scope 1 and Scope 2 separately**, so a facility-level Scope-2 attribution pattern already exists in the inventory; and (b) on 24 Apr 2026 Gavin McCormick said on the Lawfare "Scaling Laws" podcast *"in our database, we've got the world's data centers"* and *"Our hyperscaler dataset is not public yet. It will be soon."* — so an internal datacenter asset list exists and a public release has been signalled but had not appeared in any release note through v5.11.0. The published route to propose a sector is the **"Model new emissions sectors"** item on climatetrace.org/support-us → contact form at climatetrace.org/contact; data questions go to coalition@climatetrace.org; funding/partnership to gavin@ClimateTRACE.org; press to media@climatetrace.org.

---

## 1. Exact CSV schemas (release 5.11.0)

Source: "About the data" guide (Data Licensing, Schema, and Citation Guide), *Climate TRACE Inventory Sept 2026 (Version 5.11.0)*, https://media.climatetrace.org/about_the_data_latest_b6e7b8d419.pdf (linked from https://climatetrace.org/data). The guide lists metadata attributes per file in order; the column lists below are those attribute lists in document order. **I did not see a literal CSV header row** — the ZIP packages (which also contain `detailed_data_schema.csv`) could not be downloaded in this session.

### 1a. Files inside each sector download package (verbatim file-name patterns)

| File | Contents |
|---|---|
| `detailed_data_schema.csv` | "maps and explains each data column across subsectors" |
| `<subsector-name>_emissions_sources.csv` | source (asset) level emissions, monthly from 2021 |
| `<subsector-name>_country_emissions.csv` | country level, annual from 2015 |
| `<subsector-name>_emissions_sources_confidence.csv` | confidence ratings per source (the metadata section calls it `<subsector-name>_confidence.csv`; check actual name) |
| `<subsector-name>_emissions_sources_ownership.csv` | ownership tree per source |
| `ers_plan_global.zip` | emissions-reduction solutions, all subsectors |

Sector ZIPs on Zenodo (v5.7.0 record, same packaging): `power.zip` 304.1 MB, `buildings.zip` 5.9 GB, `manufacturing.zip`, `fossil_fuel_operations.zip`, `mineral_extraction.zip`, `transportation.zip`, `waste.zip`, `agriculture.zip`, `forestry_and_land_use.zip`, `fluorinated_gases.zip`, `geometries.gpkg.zip`, `ers_plan_global.zip`. (https://zenodo.org/records/20830133)

### 1b. `<subsector>_emissions_sources.csv` — 44 columns, in order

```
source_id, source_name, source_type, iso3_country, sector, subsector, start_time, end_time,
lat, lon, geometry_ref, gas, emissions_quantity, temporal_granularity, activity, activity_units,
emissions_factor, emissions_factor_units, capacity, capacity_units, capacity_factor,
capacity_factor_units, other1, other1_def, other2, other2_def, other3, other3_def, other4,
other4_def, other5, other5_def, other6, other6_def, other7, other7_def, other8, other8_def,
other9, other9_def, other10, other10_def, created_date, modified_date
```

Field definitions quoted from the guide:
- `source_id` — "The internal Climate TRACE identifier for each individual source of emissions."
- `source_type` — "Description of the emission source classification."
- `geometry_ref` — "Corresponds to the reference id in the global geopackage at climatetrace.org/data." (geopackage: https://downloads.climatetrace.org/latest/reference/geometries.gpkg.zip)
- `temporal_granularity` — "Resolution of the data available."
- `emissions_factor` — "Emissions factor of reported activity."
- `capacity_factor` — "Corresponds to the ratio of the actual source output (activity) to the source capacity."
- `other1`…`other10` — each "Additional data field available for the subsector"; `otherN_def` = "Definition of reported data of OtherN field". Null/blank/"na" means no additional data.
- `created_date` — "Date emissions source was added to the Climate TRACE database."
- Gases: CO2, CH4, N2O plus CO2e (100-yr and 20-yr, IPCC AR6 GWPs); air pollutants PM2.5, black carbon, organic carbon, SO2, VOCs, CO, NH3, NOx. One row per (source, gas, period).
- Null vs 0 (from "Beyond the UI: What's in the Asset Metadata", 24 Jan 2023, https://climatetrace.org/news/beyond-the-ui-what039s-in-the-asset-metadata): null = "we believe this value to be more than 0.5% of a sector or country's emissions, but are not measuring it"; 0 = believed to be < 0.5%. Capacity = "theoretical maximum operating capacity of the asset"; capacity factor = "its estimated actual capacity factor relative to max"; activity = "the amount of emissions-causing activity used to produce Climate TRACE estimates".

Older schema note: the GEE community catalog mirror (last updated 2024-01-17, 2022-era data) has `original_inventory_sector` in place of the `sector, subsector` pair, and adds `system:time_start`, `system:time_end`. Otherwise identical column names. (https://gee-community-catalog.org/projects/climate_trace/)

### 1c. `<subsector>_emissions_sources_ownership.csv` — 19 columns, in order

```
parent_name, parent_entity_id, parent_entity_type, parent_lei, parent_permid,
parent_registration_country, parent_headquarter_country, overall_share_percent, ownership_path,
ownership_path_datasource_ids, immediate_source_owner, immediate_source_owner_entity_id,
source_operator, source_operator_id, percentage_of_operation, source_id, source_name,
source_sector, source_subsector
```

Ownership context ("Understanding and using Climate TRACE ownership data for emitting assets", Anna Mowat, 20 Apr 2026, https://climatetrace.org/news/understanding-and-using-climate-trace-ownership-data-for-emitting-assets): powered by Global Energy Monitor's Global Energy Ownership Tracker; 18 subsectors covered; full trees for assets = 32% of global emissions, immediate-owner only for a further 14%; ~14,000 parent owners; stakes > 5% included; CSV uses "shortest, but not all, paths". Ownership lead: Anna Mowat, Head of Ownership, Global Energy Monitor. Terms page lists ownership sources PermID, OpenCorporates, Wikipedia as third-party data with their own terms.

### 1d. `<subsector>_emissions_sources_confidence.csv` — columns in metadata order

```
source_id, source_name, iso3_country, sector, subsector, start_time, end_time, source_type,
capacity, capacity_factor, activity, [gas]_emissions_factor, [gas]_emissions,
total_co2e_100gwp, total_co2e_20yrgwp, created_date, modified_date
```
(`[gas]` expands per gas, e.g. `co2_emissions_factor`, `co2_emissions`, `ch4_…`, `n2o_…` — expansion pattern inferred, not seen.) Each rated field holds one of: `very high`, `high`, `medium`, `low`, `very low`.

### 1e. `<subsector>_country_emissions.csv`

```
iso3_country, start_time, end_time, sector, subsector, gas, emissions_quantity,
emissions_quantity_units, temporal_granularity, created_date, modified_date
```

### 1f. Other access paths
- BigQuery: `trace-data-383422.climate_trace` (console: https://console.cloud.google.com/bigquery?project=trace-data-383422&d=climate_trace&p=trace-data-383422&page=dataset ; guide PDF https://media.climatetrace.org/Climate_TRACE_Big_Query_Data_8713215f81.pdf — **not fetched, blocked**).
- Zenodo "previous versions": https://zenodo.org/records/19952746 (blocked); v5.7.0 record read instead: https://zenodo.org/records/20830133, DOI 10.5281/zenodo.20830133, CC BY 4.0, contributors listed as Al Gore, Carbon Yield, Carnegie Mellon University, CTrees, Duke University, Earth Genome, Global Energy Monitor, Global Fishing Watch, JHU APL, OceanMind, RMI, TransitionZero, WattTime.
- GEE: `projects/sat-io/open-datasets/CLIMATE-TRACE/EMISSIONS/<slug>_emissions-sources` (community mirror, old).
- Changelog: https://github.com/climatetracecoalition/methodology-documents/tree/main/2026/CHANGELOG (blocked this session).
- Gridded rasters (forestry 1 km, fertiliser 5 km, rice 10 m, cattle 10 km, cropland fires 11 km, **onsite building fuel use 1 km**, per-voyage ship, road-segment) on request via contact form.

### 1g. Seed-dataset template for a hypothetical `datacenters_emissions_sources.csv`

Fill the 44 columns above. Suggested mapping (ours, not theirs):
`source_type` = "data center" (or "hyperscale data center" / "colocation data center"); `sector` = "power" is wrong — propose a new sector label or place under "buildings" with `subsector` = "data-centers"; `activity` = electricity consumed (MWh), `activity_units` = "MWh"; `capacity` = critical IT load (MW), `capacity_units` = "MW"; `capacity_factor` = average IT load / critical load; `emissions_factor` = grid or marginal intensity (tCO2e/MWh), `emissions_factor_units` = "tCO2e/MWh"; `gas` = co2e_100yr (and co2 where split); `other1` = PUE (`other1_def` = "Power usage effectiveness"); `other2` = cooling type; `other3` = onsite generation fuel (gas turbines / diesel backup) so onsite Scope 1 can be separated the way v5.11.0 does for aluminium; `other4` = operator-reported hourly CFE %; `temporal_granularity` = "month". Ownership rows: `parent_name`/`parent_lei`/`parent_permid` for the hyperscaler, `source_operator` for colo operators, `percentage_of_operation` for tenanted halls. Confidence file: rate `capacity` high where permit/utility filing exists, `activity` low where inferred from capacity × assumed load factor.

---

## 2. Power / electricity-generation methodology

**Who produces it.** The sector citation in the v5.11.0 guide: *Freeman, J., Rouzbeh Kargar, A., Couture, H., Jeyaratnam, J., Lewis, J., Alvara, M., Koenig, H., Nakano, T., Davitt, A., Lewis, C., and McCormick, G. (2025). "Power sector: Emissions from Electricity Generation." WattTime, USA; Pixel Scientia Labs, USA; and Global Energy Monitor, USA, Climate TRACE Emissions Inventory.* So: **WattTime leads** (data/engineering/research people on electricity: Madison Hobbs, Jeyavinoth Jeyaratnam, Jordan Lewis, Ali Rouzbeh Kargar), with Pixel Scientia Labs (Heather Couture, research collaborator) and Global Energy Monitor (Jenny Martos, Christine Shearer, Tiffany Nakano — plant inventory). TransitionZero co-authored the underlying 2024 paper and was a founding member on the 2019 Google.org grant for power plants, but is **not** credited in the current power-sector citation; its team is now listed under manufacturing. (Team page: https://climatetrace.org/team)

**Inputs** (peer-reviewed method: Couture et al., "Estimating Carbon Dioxide Emissions from Power Plant Water Vapor Plumes Using Satellite Imagery and Machine Learning", *Remote Sensing* 16(7):1290, 6 Apr 2024, https://www.mdpi.com/2072-4292/16/7/1290):
- Plant inventory with coordinates, fuel, prime mover, cooling type, nameplate capacity (GEM trackers, WRI Global Power Plant Database, OSM — Climate TRACE ran an OSM organised-editing campaign 2020–2023 mapping power plants: https://wiki.openstreetmap.org/wiki/Organised_Editing/Activities/Climate_TRACE).
- Satellite imagery: PlanetScope (~3 m, RGB+NIR), Sentinel-2 (10–60 m, 13 bands), Landsat 8 (OLI + TIRS thermal); derived indices HOT, whiteness, NDVI, normalised-difference SWIR and TIR.
- Signal: visible water-vapour plumes from natural-draft cooling towers and wet-FGD stacks; weather screens for plume visibility.
- Models: gradient-boosted trees + CNNs. "Sounding-level" models classify on/off (>5% CF = on) and regress capacity factor per image; "generation" models aggregate to a 30-day capacity factor.
- Training: reported hourly generation from US, Europe, Australia; validation incl. Türkiye, India (US emissions via EPA CAMPD).
- Emissions = capacity × capacity_factor × country/fuel/prime-mover-specific emission factor. Reported accuracy: generation RMSE 1.75 TWh (236 plants, 17 countries, 4 yr); CO2 RMSE 2.18 Mt; Pearson r 0.80 (CF), 0.93 (generation), 0.90 (CO2). Satellite method covers plants ≈32% of global power CO2; remainder uses "non-satellite based statistical models and meta-modeling based on other inventories" (https://climatetrace.org/approach).
- Approach page QA language: "We only keep algorithms that pass our quality control measures", "measured by how accurately they predict ground truth data".

**Confidence rating.** Not a single asset score. The per-subsector confidence CSV gives a qualitative rating (very high / high / medium / low / very low) for each of: source type, capacity, capacity factor, activity, each gas's emissions factor, each gas's emissions, and CO2e totals (100-yr, 20-yr), **per source per month per gas** ("For every asset in the Climate TRACE database, we provide confidence measurements by greenhouse gas and by month"; none at country/sector/subnational level — https://c10e.org/news/what-to-know-about-climate-traces-monthly-data-updates, 27 Mar 2025). The exact rubric mapping method → rating is in the sector methodology PDFs on GitHub (not fetched).

Also relevant: the v5.7.0 Zenodo notes mention "rebaselined electricity marginal emissions" — Climate TRACE carries marginal emission rates (WattTime's core product) alongside average plant emissions.

---

## 3. Buildings / electricity consumers — what exists

**Sector list (v5.11.0 guide + sectors page), verbatim names:**
- Power: Electricity generation; Heat Plants
- Buildings: Residential and Non-Residential Onsite Fuel Usage (sectors page: "Greenhouse gas emissions from onsite fuel combustion in residential, commercial and institutional buildings." Lead: Duke University — Kyle Bradbury, Jordan Malof et al.; v5.11.0 switched building-volume input from GHSL to Microsoft TEMPO)
- Manufacturing and Industrial Processes: Iron and Steel; Cement; Aluminum; Chemicals; Pulp and Paper; Petrochemicals Steam Cracking
- Transport: Domestic and international shipping; Non-broadcasting vessels; Domestic and international aviation; Road Transportation
- Fossil Fuel Operations: Oil and gas production and transport; Oil Refining; Coal Mining (other-fossil-fuel-operations deprecated in v5.11.0)
- Mineral Extraction: Bauxite mining; copper mining; iron mining; rock and sand quarrying
- Agriculture: Rice cultivation; Enteric fermentation and Manure management (cattle feedlot / pasture / country-level); Synthetic Fertilizers, Crop Residue, Manure applied to soils; Net Soil Organic Carbon; Cropland fires
- Waste: Wastewater Treatment; Solid Waste Disposal; Biological treatment of solid waste (country); Incineration and open burning of waste (country)
- Forestry and Land Use: Water Reservoirs; Net forest, grassland and wetland emissions (forest land clearing / degradation / fires, net forest land, net shrubgrass, net wetland, shrubgrass fires, wetland fires, removals)
- Fluorinated gases: Fluorinated gases (country-level only)
- Other Sectors (country-level only): **Other energy use**; Railways; Other transportation; Other onsite fuel usage; Solid fuel transformation; Other fossil fuel operations; Other manufacturing; Other Agricultural Soil Emissions

WattTime's page says "10 sectors and 67 subsectors" (https://watttime.org/about-us/climate-trace/).

**Identifiers.** The guide gives slugs only by example (`rice-cultivation`, `copper-mining`, `other-fossil-fuel-operations`). The GEE mirror attests the kebab-case file slugs for 37 asset-level subsectors, including `electricity-generation`, `solid-waste-disposal`, `wastewater-treatment-and-discharge`, `oil-and-gas-refining`, `steel`, `cement`, `aluminum`, `pulp-and-paper`, `petrochemicals`, `chemicals`, `coal-mining`, `bauxite-mining`, `copper-mining`, `iron-mining`, `road-transportation`, `domestic-aviation`, `international-aviation`, `domestic-shipping`, `international-shipping`, `water-reservoirs`, `forest-land-clearing`, `forest-land-degradation`, `forest-land-fires`, `net-forest-land`, `net-shrubgrass`, `net-wetland`, `shrubgrass-fires`, `wetland-fires`, `removals`, `cropland-fires`, `rice-cultivation`, `synthetic-fertilizer-application`, `enteric-fermentation-cattle-feedlot`, `enteric-fermentation-cattle-pasture`, `manure-management-cattle-feedlot`, `manure-left-on-pasture-cattle`, `other-manufacturing`. Slugs for `heat-plants`, `residential-onsite-fuel-usage`, `non-residential-onsite-fuel-usage`, `other-energy-use`, `oil-and-gas-production-and-transport`, `rock-quarrying`/`sand-quarrying`, `net-soil-organic-carbon`, `fluorinated-gases`, `railways` etc. are **inferred by convention, not confirmed**. The authoritative list is `detailed_data_schema.csv` inside any package, or `GET /v7/definitions/subsectors` (unverified, see §7).

**Consumer attribution — answer:**
- No subsector represents datacenters, electricity consumers, or grid load. Power = generation; Buildings = onsite combustion only; "Other energy use" is a country-level EDGAR/FAOSTAT-derived residual, not asset-level.
- **But** v5.11.0 release notes (24 Sep 2026, https://climatetrace.org/news/climate-trace-releases-july-2026-emissions-data): "Key methodological updates include changes to the oil and gas production and transport, aluminium, and pulp and paper sectors, all which now report Scope 1 and Scope 2 emissions separately." And the June 2025 TASA case study (https://climatetrace.org/news/pedal-to-the-lower-carbon-metal): "Climate TRACE similarly offers Scope 1 and Scope 2 emissions factors for hundreds of facilities", steel factors "differentiated by regional grid electricity mix and marginal electricity emissions rate". So facility-level Scope 2 (purchased electricity attributed to the consuming asset using regional grid / marginal rates) **is already an established pattern** in three subsectors. A datacenter subsector would be Scope 2-dominant with the same mechanics, plus Scope 1 for on-site gas turbines/diesel.
- How Scope 2 appears in the CSV (which `gas` or `other` field carries it) could not be confirmed — check `detailed_data_schema.csv` for aluminium.
- FAQ has a question "Does Climate TRACE provide Scopes 1, 2 and 3 data for all emissions sources?" (answer not rendered; https://climatetrace.org/faqs).

---

## 4. Coalition structure, people, and how to propose a sector

**Structure.** "Climate TRACE is a non-profit coalition of organizations" with "over 100 collaborating nonprofits, tech companies, universities, researchers, and climate experts" (https://climatetrace.org/about). WattTime "functions as the secretariat of the coalition" (https://watttime.org/about-us/climate-trace/). Founded July 2020 after a 2019 Google.org AI Impact Challenge grant to WattTime and TransitionZero to monitor power plants from space. No published governance, membership criteria, or sector-admission criteria were found.

**Members (12, team page https://climatetrace.org/team):** Al Gore, Carbon Yield (agriculture), CREATE Lab (plumes), CTrees (forestry), Duke University (buildings), Earth Genome (engineering/product), Global Energy Monitor (asset inventories, ownership, cement/coal/steel/electricity), Johns Hopkins APL (waste, road transport, reservoirs, cross-sector), OceanMind (shipping), RMI (oil & gas, refining, fossil fuel ops), TransitionZero (manufacturing), WattTime (electricity, agriculture, waste, cross-sector).

**Leadership:** Gavin McCormick — Co-founder, WattTime executive director (gavin@ClimateTRACE.org per support-us page); Al Gore — Co-founder (funder; "At the urging of former US Vice President Al Gore" the project expanded). WattTime management: Lauren Betz, Christy Lewis, Eric Nguyen; partnerships: Bene de Gelder, Erin Green, Amy Kouch, David Younan-Montgomery; product: Anthony Russo; strategy: Ting So.

**Research collaborators** (non-member): Pixel Scientia Labs, Planet Labs, JPL/Caltech, Global Fishing Watch, Michigan State, Crosswalk Labs, Arboretica, ecoinvent, emLab UCSB, HeiGIT, Ode Partners, Open Supply Hub, RS Lab SLU, Universiti Malaysia Terengganu. **Impact collaborators:** Clarity AI, Climate Group, Climatiq, Government of Córdoba, Inflection Point Agency, Joint Impact Model, ASU Global Futures Lab, Muir AI, Open Earth Foundation, Polestar, Subnational Methane Action Coalition, Tesla. **Funders:** Al Gore, Benificus, Clean Air Fund, Generation Foundation, Google.org, Holdfast Collective, IKEA Foundation, MacArthur, Minderoo, McGovern Foundation, Rockefeller, Salesforce, Sergey Brin Family Foundation, partners of Generation Investment Management.

**Published contribution routes (https://climatetrace.org/support-us, "Contribute Data" section):**
1. "Identify facility level errors" — "share feedback" link on each emissions-source card, with supporting information.
2. **"Model new emissions sectors"** — notes railways and fluorinated gases only have national-level estimates; invites contact "about joining the coalition or supporting our work" → https://climatetrace.org/contact.
3. "Donate training or validation data" — non-public data accepted as training/validation input, via contact form.

**Contact page (https://climatetrace.org/contact):** form fields Name*, Your Email Address*, Organization Name*, Subject*, Message, privacy acknowledgement. Text: "If you still can't find what you need and are interested in helping to develop our global emissions monitoring tool or using our data, please reach out to us using the contact form below." Free technical support offered to institutions using data "for a project that is likely to significantly reduce emissions." Emails: media@climatetrace.org (press); coalition@climatetrace.org (data questions and errors, from the data guide); gavin@ClimateTRACE.org (funding/secretariat, support-us page).

**FAQ questions present** (answers collapsed, not captured): "How can I contribute to Climate TRACE data and analysis?", "How accurate is your data?", "How do I access Climate TRACE data via API?", "What data are available on the API?", "Does Climate TRACE provide Scopes 1, 2 and 3 data for all emissions sources?"

**No formal published criteria** for new sectors/members were found. Practical reading: sector methodologies are owned by a member org (one org per sector family), published as a methodology PDF on GitHub with a named author list and a sector citation; a datacenter proposal would most plausibly land with WattTime (power / marginal emissions / hyperscaler dataset) with Duke (buildings, satellite building-volume) and GEM (asset inventory + ownership) as natural partners.

---

## 5. Public statements on datacenters / AI compute

1. **Gavin McCormick, Lawfare "Scaling Laws: Facts & Myths About AI's Energy Usage", 24 Apr 2026** — https://www.lawfaremedia.org/article/scaling-laws--facts---myths-about-ai's-energy-usage-with-gavin-mccormick (auto-transcript):
   - "So in our database, we've got the world's data centers."
   - "Our hyperscaler dataset is not public yet. It will be soon."
   - "The question is how much dirty electricity people are using." / "we are gonna know because we can track this all with satellites"
   - "Apple and Microsoft and Meta now have essentially hit zero emissions from data centers"; on xAI: "they're powering Colossus 2 on gas, on fossil fuels."; "Amazon was also by far the world's largest builder of renewable energy last year for the third year in a row."
   - Caveat: spoken, auto-transcribed; "our database" may refer to WattTime's rather than the public Climate TRACE inventory. No release note through v5.11.0 (Sep 2026) mentions datacenters or a hyperscaler dataset.
2. **AFP, "Behind AI's carbon footprint, a potential climate tool", 15 Oct 2026** — https://sg.news.yahoo.com/behind-ais-carbon-footprint-potential-014807906.html (syndicated; also France24, TechXplore, Bangkok Post; featured on climatetrace.org news sidebar): McCormick: "Climate TRACE is 20 years more advanced because of AI."; "One of the things AI is very good at is forecasting." Data centres discussed only via IEA's Siddharth Singh; the article does **not** say Climate TRACE tracks datacenters.
3. **WattTime (not Climate TRACE) Meta case study, May 2025** — https://watttime.org/wp-content/uploads/2025/06/WattTime-Meta-Emissions-Accounting-Case-Study-vFinal-202505b.pdf — hourly, per-datacenter "Carbon Matching" of Meta's 2023 load against marginal emission rates; "Meta's physical emissions are likely higher than reported under Annual Matching." Shows the secretariat already has the consumption-side method and hyperscaler data relationships.
4. Searched and found **no** Climate TRACE news post, release note, or FAQ entry mentioning data centers, hyperscalers, or AI compute as a tracked source (searches: site news 2026, "hyperscaler dataset", "Climate TRACE data center", xAI/Colossus).

---

## 6. Licence and attribution (verbatim where captured)

- Data guide: "freely available under the Creative Commons Attribution 4.0 International Public License". Suggested citation: **"Climate TRACE (2026), Climate TRACE Emissions Inventory v5.11.0, https://climatetrace.org [Date Accessed]"**. Sector-specific citations must be used for sector data (power citation in §2). "Many third-party datasets are excluded from the CC BY 4.0 license and carry their own terms."
- Terms of Use (https://climatetrace.org/terms): data "made available via Climate TRACE under the Creative Commons Attribution 4.0 International License" except listed external datasets (EDGAR, FAOSTAT, European PRTR, US EPA FLIGHT, US EPA LMOP, Canada GHGRP, Israel PRTR, GADM, GHSL, PermID, OpenCorporates, Wikipedia); users may copy, modify, distribute for any purpose incl. commercial, if they attribute Climate TRACE and note changes; it is the "sole responsibility of the user to review the terms and conditions for all the above sources"; provided "as is" and "as available" without warranty; models "are expected to change over time". Citation format link points to the methodology-documents GitHub.
- Data page: "The data are licensed Creative Commons 4.0" (https://climatetrace.org/data). GEE mirror: "All Climate TRACE data is freely available under the Creative Commons Attribution 4.0 International Public License … unless otherwise noted below".
- Zenodo v5.7.0 record: licence CC BY 4.0, DOI 10.5281/zenodo.20830133.

---

## 7. API

- Data page: "Public API, in beta … availability is not guaranteed, so … keep volume low"; "The API supports search for emitting assets by sector, owner, and location." Reference: https://api.climatetrace.org/v7 . Python wrapper: https://github.com/climatetracecoalition/climate-trace-tools/tree/main/climate_trace_tools/api (package `climate-trace-tools`, not found on PyPI by search). Feedback via contact form.
- **Could not verify** `GET /v7/assets?limit=1` or any route/parameter list: `api.climatetrace.org/v7`, `/v7/assets`, `/spec.json`, and the GitHub wrapper were all blocked at the proxy. The `/v7` docs page is a JS app (title "Climate TRACE API Docs") with no server-rendered endpoint list.
- Older shape: Open Net Zero lists "ClimateTRACE API v4" — "supports searching for emitting assets by sector, owner, location", emissions and asset detail, country aggregation; Swagger at https://api.climatetrace.org/v4/swagger/index.html, spec https://api.climatetrace.org/spec.json (https://www.opennetzero.org/climate-trace/climatetrace-api-v4). The existing sources.json note says v7 is beta; prior-knowledge route family (`/v6/assets`, `/v6/assets/emissions`, `/v6/definitions/{sectors|subsectors|countries|gases|groups}`, `/v6/country/emissions`, `/v6/admins/search` with `countries`, `sectors`, `subsectors`, `continents`, `limit`, `offset`, `year`, `since`, `to`, `gas`) is **unverified for v7**.
- Third-party inventories (Jana MCP server, Apify scraper) wrap the API but do not document v7 parameters.

---

## 8. What could NOT be confirmed (explicit)

1. A literal header row from a real CSV — column lists are from the guide's metadata tables, not an opened file. `detailed_data_schema.csv` not seen.
2. Exact kebab-case ids for subsectors beyond those attested by the GEE mirror and the three examples in the guide.
3. v7 API endpoints and parameters (all api.climatetrace.org and github.com fetches blocked).
4. BigQuery table names/columns (guide PDF blocked).
5. The confidence-rating rubric (how a method maps to very high…very low) — in sector methodology PDFs on GitHub, blocked.
6. How Scope 2 values are encoded in the v5.11.0 aluminium / pulp-and-paper / oil-and-gas files.
7. FAQ answer texts (collapsed accordions).
8. Whether the "hyperscaler dataset" McCormick mentioned has been published anywhere by 2026-10-20 — no evidence found.
9. Formal written criteria for admitting a new sector or coalition member — none published.

---

## Sources

- Data Downloads — https://climatetrace.org/data
- About the data (v5.11.0 guide PDF) — https://media.climatetrace.org/about_the_data_latest_b6e7b8d419.pdf
- July 2026 data release (v5.11.0) — https://climatetrace.org/news/climate-trace-releases-july-2026-emissions-data
- May 2026 release (v5.9.0) — https://climatetrace.org/news/climate-trace-releases-may-2026-emissions-data
- January 2026 release (v5.5.0) — https://climatetrace.org/news/climate-trace-releases-january-2026-emissions-data
- H1 2026 analysis (v5.10.0) — https://climatetrace.org/news/climate-trace-data-show-marginal-increase-in-global-emissions-in-the-first-half-of-2026
- Monthly updates explainer — https://c10e.org/news/what-to-know-about-climate-traces-monthly-data-updates
- Asset metadata explainer — https://climatetrace.org/news/beyond-the-ui-what039s-in-the-asset-metadata
- Ownership data explainer — https://climatetrace.org/news/understanding-and-using-climate-trace-ownership-data-for-emitting-assets
- TASA / Scope 1+2 factors — https://climatetrace.org/news/pedal-to-the-lower-carbon-metal
- Sectors — https://climatetrace.org/sectors
- Approach — https://climatetrace.org/approach
- About — https://climatetrace.org/about
- Team + Partners — https://climatetrace.org/team
- Support Us (contribute data) — https://climatetrace.org/support-us
- Contact — https://climatetrace.org/contact
- FAQs — https://climatetrace.org/faqs
- Terms of Use — https://climatetrace.org/terms
- WattTime on Climate TRACE — https://watttime.org/about-us/climate-trace/
- Couture et al. 2024, Remote Sensing — https://www.mdpi.com/2072-4292/16/7/1290
- GEE community catalog — https://gee-community-catalog.org/projects/climate_trace/
- Zenodo v5.7.0 — https://zenodo.org/records/20830133
- Zenodo previous versions (blocked) — https://zenodo.org/records/19952746
- BigQuery guide (blocked) — https://media.climatetrace.org/Climate_TRACE_Big_Query_Data_8713215f81.pdf
- Changelog (blocked) — https://github.com/climatetracecoalition/methodology-documents/tree/main/2026/CHANGELOG
- API v7 docs (blocked) — https://api.climatetrace.org/v7
- Python wrapper (blocked) — https://github.com/climatetracecoalition/climate-trace-tools
- Open Net Zero API v4 listing — https://www.opennetzero.org/climate-trace/climatetrace-api-v4
- Lawfare podcast, 24 Apr 2026 — https://www.lawfaremedia.org/article/scaling-laws--facts---myths-about-ai's-energy-usage-with-gavin-mccormick
- AFP, 15 Oct 2026 — https://sg.news.yahoo.com/behind-ais-carbon-footprint-potential-014807906.html
- WattTime Meta case study — https://watttime.org/wp-content/uploads/2025/06/WattTime-Meta-Emissions-Accounting-Case-Study-vFinal-202505b.pdf
- OSM organised editing — https://wiki.openstreetmap.org/wiki/Organised_Editing/Activities/Climate_TRACE
- Wikipedia — https://en.wikipedia.org/wiki/Climate_TRACE
