# Irish EPA Annual Environmental Reports (AERs) for licensed datacentres - notes

Date of work: 2026-10-23. Companion file: `ireland_aer_metered.csv` (22 site-years, 11 licences, reporting years 2025 and 2024).

## Headline answers

| Figure | Carried in AER? | What is actually there |
|---|---|---|
| (a) Metered annual electricity | **Yes, but in GJ only** (no kWh/MWh anywhere in any of the 22 AERs read) | Section 3 "Energy & Water", Table 3 "Energy Used", row "Electricity", column "Quantity (GJ)", plus "% Increase/decrease on previous year" |
| (b) Water use | **Yes, m3/year** | Table 5 "Water Used", rows Groundwater / Surface Water / Public Supply / Recycled Water / Rainwater / Total Water Used, column "Quantity (m3/year)" |
| (c) Standby generator run hours | **No** - not one of the 22 AERs gives run hours, test hours or number of tests | Only text is the licence air-monitoring trigger "once every five years or when three times the permitted maximum annual operating hours have elapsed" |
| (c') Diesel consumed | **Energy only (GJ), never litres or tonnes** | Table 3 rows "Light Fuel Oil" (= diesel) and "Renewable Biomass" (= HVO, per the comment text); Equinix and Microsoft also use the "Natural Gas" row |

The CSV therefore has `electricity_mwh`, `generator_hours` and `diesel_litres_or_tonnes` = "not found" in every row, and carries the GJ values in four added columns (`electricity_gj`, `light_fuel_oil_gj`, `renewable_biomass_hvo_gj`, `natural_gas_gj`). 1 MWh = 3.6 GJ is an exact definition, but per the ledger rule no conversion was made; a checker can divide by 3.6.

## Example lines (verbatim, as read by the PDF-to-text fetch)

Electricity - P1170-01 AER 2025, Table 3 Energy Used, p.15, https://leap.epa.ie/docs/d30f01fa-7b3c-4f1d-b37d-be8909ba4629.pdf:
> "Electricity 1,586,892.15 +47.84%"  (column headers: "Energy Used | Quantity (GJ) | % Increase/ decrease on previous year")

Water - same document, Table 5 Water Used, p.17:
> "Public Supply 1,132.66 -87%" ... "Total Water Used 1,132.66 -87%"  (column header "Quantity (m3/year)"); comment: "Water use in 2025 decreased by 7,855.34 m³, representing an overall 87% reduction compared with 2024."

Generator hours - nothing to quote as a figure. The closest lines are:
> P1170-01 AER 2025 p.10: "Outside of routine testing and maintenance, the operation of these emergency back-up generators is typically only required under the following emergency circumstances:"
> P1173-01 AER 2025 p.25: "once every five years or when three times the permitted maximum annual operating hours have elapsed"
> Equinix P1168-01 AER 2024 p.9: "Ongoing delays with the site receiving full MIC, resulted in the site having to operate the generators as prime from February 2024 to November 2024 to support the IT load." (https://leap.epa.ie/docs/632e86ac-f221-47b6-b9c2-a5765cb06d09.pdf) - a period, not hours.

Diesel/HVO - P1170-01 AER 2025 Table 3 p.15:
> "Light Fuel Oil 60.20 -79.14%" and "Renewable Biomass 1,629.28 -55.64%"; comment p.16: "The backup generators on the site operate on light fuel oil (Diesel) and Renewable Biomass (Hydrotreated Vegetable Oil (HVO))."

## What an AER contains (LEAP template, identical across Amazon, Microsoft, Equinix, and non-datacentre licensees such as SSE)

Purpose of this Report; Contents; Glossary; Declaration; 1) Introduction (Contact Us); 2) How we Manage our Facility (Environmental Management System; Beyond Compliance); 3) Energy & Water (Energy: Table 3 Energy Used, Table 4 Energy Generated; Water: Table 5 Water Used); 4) Environmental Complaints; 5) Environmental Incidents; 6) Our Environmental Emissions (Storm Water; Waste Water; Air; Fugitive Solvent Emissions; Groundwater; Noise); 7) Waste (Waste Generated; Waste Accepted); 8) Financial Provision; Appendix I Class of Activity; Appendix II High Environmental Risk Categories; Appendix III Beyond Compliance.

Table 3 rows: Electricity / Heavy Fuel Oil / Light Fuel Oil / Natural Gas / Coal / Solid Fuel / Peat / Renewable Biomass / Renewable Energy Generated On-site / Total Energy Used. Units: GJ.
Table 5 rows: Groundwater / Surface Water / Public Supply / Recycled Water / Rainwater / Total Water Used. Units: m3/year.
AERs are filed by the end of March/April for the previous calendar year; the 2025 AERs were loaded to LEAP on 2026-04-29/30 (Amazon, Microsoft) and 2026-04-18 (Equinix).

## How to reach AERs (the pattern that worked)

The public portal https://leap.epa.ie/ is a JavaScript app and returns an empty body to a fetcher; https://epawebapp.epa.ie/licences/ and the old `terminalfour/ippc/ippc-view.jsp?regno=` URL return client errors. The working route is the LEAP Open Data API (Swagger spec at https://data.epa.ie/leap/swagger/v1/swagger.json, base https://data.epa.ie/leap):

1. `GET /api/v1/LicenceProfile/byregno?licence_reg_no=P1170-01` (or `/LicenceProfile/licenceprofilesearchlist?search_term=Amazon%20Data%20Services`) -> `licence_profile_id` and the licence GUID(s).
2. `GET /api/v1/Licence/listbyprofileid?licence_profile_id=...` when a licence has been reviewed (P1181, P1186): AERs stay attached to the **replaced -01 licence GUID**, and the new -02 GUID lists zero documents.
3. `GET /api/v1/Document/listbylicenceidfiltered?licence_id=<GUID>&classification=Annual%20Environmental%20Report` -> each record has `url` = `https://leap.epa.ie/docs/<documentid>.pdf`. (Using `search_term=Annual Environmental Report` instead of `classification` misses files not named that way, e.g. Microsoft's "AER P1187 Final 30-3-26.pdf".)
4. Fetch the PDF.

Licence GUIDs found: P1170-01 7c16b775-a4ce-4414-bd47-4a08b151fb0e; P1171-01 1e877ac9-2ef5-429c-ba36-3fb97e8ab82f; P1172-01 90c9996d-35b3-4493-b219-e5a8553654c0; P1173-01 ad7f1139-4faf-4214-933f-896c128d7656; P1177-01 4a651a23-4b4b-4165-a2dd-f95fab22e6fe; P1181-01 f4b11d36-f066-4ce6-8590-6a7b9b44233c (replaced by P1181-02 c7e72b7d-25e2-4c1b-aee8-d93231192de4 on 2026-09-24); P1182-01 58bf4842-5b97-43cd-8bc4-e1cdd5b3278d; P1184-01 795fae8d-59a0-4f01-b2f4-c5ccf35c0e79; P1186-01 6b561918-9d96-4826-aa76-2adeb9342b12 (replaced by P1186-02 db1ef714-1f26-40a7-ac33-0a5a6e56b340 on 2026-09-24); P1187-01 981477df-4508-47ea-aa73-de913da42807; P1168-01 1a296728-03f9-4ad6-8a08-852704311cc1.

## Sites reached (11 licences, 22 site-years, all 2025 + 2024)

Amazon: P1170 (Grange Castle South A-C), P1184 (Grange Castle South, CyrusOne plot), P1173 (Airton Road), P1177 (Greenhills Road), P1172 (Blanchardstown/Snugborough), P1182 (Cruiserath), P1171 (Clonshaugh campus), P1186 (Clonshaugh W/X/Y), P1181 (Drogheda). Microsoft: P1187 (DUB14/15). Equinix: P1168 (DB5 with gas-turbine plant).

AERs for 2023 also exist for all of these except P1181 (licensed Aug 2024) and were not read (budget); the 2024 AERs state the 2023 reports covered only part-years because the licences were granted mid-2023.

## Sites NOT reached and why

- 27 of the 40 input sites have **no EPA industrial emissions licence** (Google, Meta Clonee, Digital Realty DUB14, K2 x2, KDCR x2, Waspar, Vodafone, Equinix DB1/DB3/DB4, Echelon x2, EdgeConneX x2, Microsoft DB3-5 and DUB06-13 GHG-only rows, SDR4, Servecentric, OGCIO, Art, Red Admiral, Parslickstown, Vantage DUB13, Equinix DB8, Amazon Cruiserath E/F/G). They hold GHG permits (IE-GHGxxx) or only planning permissions; GHG permit holders file annual emissions reports to the EPA ETS unit, which are not published on LEAP as AERs. No AER exists for them.
- P1222-01 (Amazon Leixlip KIC B1): LEAP status "Compliance Failure/Rejected", no licence in force, no AER. Not queried further.
- P1203-01 (Vantage DUB11/12): application only; not queried (budget).
- P1238-01 (Amazon, new application LA020122, status Assessment) appeared in the LEAP profile search; not in the input list.
- Second copy of the P1181 2024 AER (https://leap.epa.ie/docs/c1c93c77-e1f3-422f-b51a-7ee363bf6704.pdf) not read; the copy read (dacb2948-...) was found misfiled in the P1170-01 document list.
- Microsoft "P1187-01 DUB14-15 AAQMR 2024 V2.pdf" and "AAQMR 2025.pdf" (ambient air quality monitoring reports, classified as AER in LEAP) not read.

URLs that failed: https://leap.epa.ie/ (empty JS shell); https://epawebapp.epa.ie/licences/ (client error); https://epawebapp.epa.ie/terminalfour/ippc/ippc-view.jsp?regno=P1170-01 (client error); https://data.epa.ie/leap/swagger (JS shell; use /swagger/v1/swagger.json). Search engines did not index the AER PDFs by licence number; the first search hit (https://leap.epa.ie/docs/ed401de3-77ab-4c57-b529-26281184578e.pdf) was an SSE power station AER, not a datacentre.

## Things that would mislead a reader

1. **Units.** Electricity is GJ, not MWh. All AERs, all years. Nothing in the documents gives kWh.
2. **Scope = licensed installation, not operator campus.** Amazon's Clonshaugh campus is two licences (P1171 and P1186) at adjacent addresses (D17 V088 and D17 V3303); Grange Castle South is two licences (P1170 and P1184). Microsoft P1187 covers DUB14/DUB15 and the "CAB building" only, not the DB3-5 or DUB06-13 blocks, which have no IE licence. Do not sum across operators' rows as if they were campuses, and do not treat one licence as the operator's Irish total.
3. **Part years.** P1181 2024 covers 8 Aug-31 Dec 2024 only. All 2023 AERs (not read) are part-years from the mid-2023 grant dates; that is why every 2024 "% change" column reads N/A.
4. **Equinix DB5 (P1168) is not a grid-fed datacentre in 2024.** It ran its gas turbines as prime power Feb-Nov 2024 (510,550 GJ natural gas vs 303,804 GJ purchased electricity). Grid electricity understates its energy use for that year. In 2025 it moved to mains (584,125 GJ electricity, 5,841 GJ gas).
5. **Equinix water.** 399,153 m3 (2025) and 103,359 m3 (2024) vs 700-21,000 m3 for Amazon sites: DB5 has evaporative cooling towers; Amazon sites use mainly air cooling with occasional evaporative use. Water figures are not comparable as a "datacentre water" benchmark without the cooling type.
6. **Percent-change columns are unreliable.** P1172 2025 Table 3 says Total Energy Used -50.0% while Electricity is -13.7% (actual arithmetic from the 2024 AER: about -13.8%). P1171 2025 Table 5 says -86% while the comment says 84%. P1186 2025 Table 5 says -70% while the comment says 84%. Microsoft 2025 comment says HVO rose 104.05% while the table says +38.23%. Equinix uses phrases like "500% reduction" and "88000% reduction". Use the absolute values from the current and prior AERs, not the % columns.
7. **Microsoft 2024 water total includes an estimate**: "approximately 20,000 m3 of the collected rainwater", so "Total Water Used 21,617" is only partly metered; the 2025 total (2,919.50) excludes the 480 m3 rainwater row.
8. **"Renewable Biomass" means HVO burned in diesel generators**, not a biomass boiler; the comment text says so in every Amazon and Microsoft AER. "Light Fuel Oil" is diesel.
9. **Generator hours per unit vs fleet** does not arise because no AER reports hours at all. Licence air-monitoring for generator stacks is triggered by cumulative operating hours ("three times the permitted maximum annual operating hours"), so the operators must hold per-unit hour logs, but they are not in the AER.
10. **LEAP document lists can be misfiled**: the P1181-01 2024 AER appears in the P1170-01 document list. Always check the licence number printed on the AER cover.
11. The P1171-01 licence shows in LEAP as "Licensed" from 2023-06-14; the input file's note that its grant was "not confirmed" can be updated.
