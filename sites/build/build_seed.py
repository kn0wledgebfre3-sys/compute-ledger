#!/usr/bin/env python3
"""Build seed_sites.csv/json and seed_sites_unlocated.csv for the datacenter facility-type seed list.
All data embedded below was obtained via WebSearch/WebFetch in the 2026-10-20 session; see seed_sites_method.md."""
import csv, json, re, sys

import os as _os
OUT_DIR = _os.environ.get("SITES_OUT") or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
TODAY = "2026-10-20"

COLS = ["site_id","name","operator","parent_company","country","admin_region","city","lat","lon","status",
        "capacity_mw_it","capacity_source","generator_mw_permitted","cooling","first_year","source_url",
        "source_type","licence","ledger_entry_id","confidence","last_checked","coord_source_url","notes"]

def dms(s):
    """Convert a Wikipedia DMS string like 38°56′35.99″N 77°31′27.61″W to (lat, lon)."""
    parts = re.findall(r"(\d+)°(\d+)′([\d.]+)″([NSEW])", s)
    if len(parts) != 2:
        parts = re.findall(r"(\d+)°(\d+)′([\d.]*)″?([NSEW])", s)
    out = []
    for d, m, sec, h in parts:
        v = int(d) + int(m)/60 + (float(sec) if sec else 0)/3600
        if h in "SW":
            v = -v
        out.append(round(v, 6))
    return out[0], out[1]

import unicodedata
def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s

rows = []
def add(**kw):
    r = {c: None for c in COLS}
    r.update(kw)
    r["last_checked"] = TODAY
    if not r.get("site_id"):
        r["site_id"] = slug(f"{r['country']}-{r['name']}")
    rows.append(r)

# ---------------------------------------------------------------------------
# 1. Google-operated sites: coordinates from the Wikipedia 'Google data centers' table
#    (CC BY-SA 4.0), existence/status corroborated by Google's own location list
#    (https://datacenters.google/locations/, operator source, used only for corroboration).
WIKI = "https://en.wikipedia.org/wiki/Google_data_centers"
GOOG = "https://datacenters.google/locations/"
google_sites = [
    # name, country, admin, city, dms, status, first_year, ledger, notes, cooling, extra
    ("Google Arcola (Loudoun County) data center", "USA", "Virginia", "Arcola", "38°56′35.99″N 77°31′27.61″W", "operating", None, None,
     "Wikipedia: announced 2017. Google list: 'Loudoun County, Virginia' (no in-development tag). Not matched to a Virginia DEQ registration name.", "unknown"),
    ("Google Douglas County (Atlanta) data center", "USA", "Georgia", "Lithia Springs", "33°44′59.04″N 84°35′5.33″W", "operating", 2003, None,
     "Google list: 'Douglas County, Georgia'.", "unknown"),
    ("Google Cerrillos data center (Dataluna)", "CHL", "Región Metropolitana", "Cerrillos", "33°31′14″S 70°43′18″W", "announced", None, "cl-cerrillos-google-water",
     "RCA Res. Ex. 127/2020 partially annulled by Segundo Tribunal Ambiental (2024-02-26); Google withdrew the approved design (Sept 2024) and said it will re-submit an air-cooled design. Not on Google's current location list.", "air"),
    ("Google Changhua County data center", "TWN", "Changhua County", "Changhua", "24°08′18.6″N 120°25′32.6″E", "operating", 2013, None,
     "Google list: 'Changhua County, Taiwan'.", "unknown"),
    ("Google Montgomery County (Clarksville) data center", "USA", "Tennessee", "Clarksville", "36°37′16″N 87°15′47″W", "operating", None, None,
     "Wikipedia: announced 2015. Google list: 'Montgomery County, Tennessee'.", "unknown"),
    ("Google Council Bluffs data center (original campus)", "USA", "Iowa", "Council Bluffs", "41°13′17.7″N 95°51′49.92″W", "operating", 2009, None,
     "Wikipedia: announced 2007, first phase 2009, expanded 2012 and 2015. Google list: 'Council Bluffs, Iowa' (note: 'some locations may have more than one site').", "unknown"),
    ("Google Council Bluffs data center (second campus)", "USA", "Iowa", "Council Bluffs", "41°10′06″N 95°47′46″W", "operating", None, None,
     "Second Wikipedia table entry for Council Bluffs (labelled 'Iowa, us-central1').", "unknown"),
    ("Google Dublin (Grange Castle) data center", "IRL", "Dublin", "Clondalkin", "53°19′12.39″N 6°26′31.43″W", "operating", 2012, None,
     "Google list: 'Dublin, Ireland'. Ireland CSO/CRU records in ledger cover the Dublin cluster, not this site.", "unknown"),
    ("Google Eemshaven data center", "NLD", "Groningen", "Eemshaven", "53°25′31″N 6°51′44″E", "operating", 2016, None,
     "Google list: 'Eemshaven, Netherlands'. Eemshaven/Het Hogeland is one of two national hyperscale-permitted areas (Barro art. 2.15.1; see ledger nl-zeewolde-meta-cancelled).", "unknown"),
    ("Google Hanau (Frankfurt) data center", "DEU", "Hessen", "Hanau", "50°07′21″N 8°58′27″E", "operating", None, None,
     "Wikipedia row 'Frankfurt, Germany' (2022 expanded); Google list: 'Hanau, Germany'.", "unknown"),
    ("Google Fredericia data center", "DNK", "Region Syddanmark", "Fredericia", "55°33′29.5″N 9°39′20.8″E", "operating", 2020, None,
     "Google list: 'Fredericia, Denmark'.", "unknown"),
    ("Google St. Ghislain (Ghlin) data center", "BEL", "Hainaut", "Ghlin", "50°28′09.6″N 3°51′55.7″E", "operating", 2010, None,
     "Google list: 'St. Ghislain, Belgium'.", "unknown"),
    ("Google Hamina data center", "FIN", "Kymenlaakso", "Hamina", "60°32′11.68″N 27°7′1.21″E", "operating", 2011, "fi-hamina-google-heat-seawater",
     "Seawater cooling (Google statement, ledger); heat recovery to Haminan Energia district heating from Q4 2025. Google list: 'Hamina, Finland'.", "seawater"),
    ("Google Henderson data center", "USA", "Nevada", "Henderson", "36°03′20″N 115°00′37″W", "operating", 2020, None,
     "Google list: 'Henderson, Nevada'.", "unknown"),
    ("Google Inzai data center", "JPN", "Chiba", "Inzai", "35°49′04″N 140°07′57″E", "operating", 2023, None,
     "Google list: 'Inzai, Japan'.", "unknown"),
    ("Google Leesburg (Loudoun County) data center", "USA", "Virginia", "Leesburg", "39°3′6.38″N 77°32′20.38″W", "operating", None, None,
     "Wikipedia: announced 2017. Google list: 'Loudoun County, Virginia'.", "unknown"),
    ("Google Lenoir data center", "USA", "North Carolina", "Lenoir", "35°53′54.78″N 81°32′50.58″W", "operating", 2009, None,
     "NC DAQ Title V permit 09733T10 (issued 2025-05-12) to Tapaha Dynamics LLC, 708 Lynhaven Drive, Lenoir: 120 existing + 43 new diesel emergency generators (new units 36x2,750 kW + 7x1,750 kW = 111.25 MW); existing-unit MW not stated. Permit review: https://www.epa.gov/system/files/documents/2025-05/aq_f_1400204_20250512_prmt_pmtrvw_t10.pdf", "unknown"),
    ("Google Lok Yang Way (Jurong) data center", "SGP", "Singapore", "Jurong West", "1°19′26″N 103°41′36″E", "operating", 2022, None,
     "Google list: 'Singapore'. IMDA DC-CFA awards (ledger sg-imda-moratorium-capacity) do not name Google.", "unknown"),
    ("Google Middenmeer (Agriport A7) data center", "NLD", "Noord-Holland", "Middenmeer", "52°47′24″N 5°01′45″E", "operating", None, None,
     "Wikipedia: announced 2019. Google list: 'Middenmeer, Netherlands'. Agriport A7 is one of two national hyperscale-permitted areas (see ledger nl-zeewolde-meta-cancelled, nl-middenmeer-microsoft-water).", "unknown"),
    ("Google Midlothian data center", "USA", "Texas", "Midlothian", "32°26′35″N 97°03′44″W", "operating", 2022, None,
     "Google list: 'Midlothian, Texas'. Texas Comptroller register lists Google-occupied projects under project-LLC names (Sharka LLC, SDC DFW VIII, etc.).", "unknown"),
    ("Google Berkeley County (Moncks Corner) data center", "USA", "South Carolina", "Moncks Corner", "33°03′50.8″N 80°02′36.1″W", "operating", 2007, None,
     "Google list: 'Berkeley County, South Carolina'.", "unknown"),
    ("Google New Albany data center", "USA", "Ohio", "New Albany", "40°03′41″N 82°45′31″W", "operating", None, None,
     "Wikipedia: announced 2019. Google list: 'New Albany, Ohio'. AEP Ohio data-center tariff (ledger us-oh-aep-ohio-data-center-tariff) applies.", "unknown"),
    ("Google Papillion data center", "USA", "Nebraska", "Papillion", "41°08′00″N 96°08′39″W", "operating", None, None,
     "Wikipedia: announced 2019. Google list: 'Papillion, Nebraska'.", "unknown"),
    ("Google Pryor Creek (Mayes County) data center", "USA", "Oklahoma", "Pryor", "36°14′28.1″N 95°19′48.22″W", "operating", None, None,
     "Wikipedia: announced 2007, expanded 2012. Google list: 'Pryor, Mayes County, Oklahoma'. Epoch AI lists 'Google Pryor (North)' among frontier AI sites.", "unknown"),
    ("Google Quilicura data center", "CHL", "Región Metropolitana", "Quilicura", "33°21′30.5″S 70°41′50.4″W", "operating", 2015, None,
     "Google list: 'Quilicura, Chile'. Chile SEA/RCA records exist (ledger cl-national-datacenter-plan context).", "unknown"),
    ("Google Storey County (Reno) data center", "USA", "Nevada", "McCarran", "39°30′04″N 119°25′46″W", "operating", None, "us-nv-google-nv-energy-clean-transition-tariff",
     "Wikipedia: approved Nov 2018. Google list: 'Storey County, Nevada'. PUCN Docket 24-06014 Clean Transition Tariff ESA (115 MW Fervo geothermal) in ledger.", "unknown"),
    ("Google The Dalles data center", "USA", "Oregon", "The Dalles", "45°37′57.04″N 121°12′8.16″W", "operating", 2006, "us-or-the-dalles-google-water-records",
     "City water records (ledger): 434.4 million gallons in 2024; cooling water use implies evaporative cooling.", "evaporative"),
    ("Google Waltham Cross data center", "GBR", "Hertfordshire", "Waltham Cross", "51°41′44″N 0°02′55″W", "operating", None, None,
     "Wikipedia: announced Jan 2024. Google list shows it without an 'in development' tag (2026-10-20).", "unknown"),
    ("Google Canelones (Parque de las Ciencias) data center", "URY", "Canelones", "Canelones", "34°48′56″S 55°59′44″W", "under_construction", None, "uy-canelones-google-water",
     "Revised EIA (Nov 2023): 32 air-cooled closed-loop chillers, 48 m3/day water. Wikipedia: construction started 2024, inauguration expected 2026. Google list: 'Canelones, Uruguay'.", "air"),
    ("Google Fort Wayne data center", "USA", "Indiana", "Fort Wayne", "41°01′59.4″N 85°03′22.6″W", "operating", 2025, None,
     "Wikipedia: first phase operational Dec 2025, construction ongoing Aug 2026. Google list: 'Fort Wayne, Indiana'.", "unknown"),
    ("Google Jackson County (Widows Creek, Bridgeport) data center", "USA", "Alabama", "Bridgeport", "34°54′48.4″N 85°44′53.1″W", "operating", None, None,
     "Wikipedia: broke ground 2018 on former TVA Widows Creek coal plant site. Google list: 'Jackson County, Alabama'.", "unknown"),
    ("Google Wenya (Jurong West) data center", "SGP", "Singapore", "Jurong West", "1°21′04.8″N 103°42′35.2″E", "operating", 2013, None,
     "Google list: 'Singapore'.", "unknown"),
]
for name, cc, adm, city, d, status, fy, ledger, notes, cooling in google_sites:
    lat, lon = dms(d)
    conf = "medium"
    add(name=name, operator="Google", parent_company="Alphabet Inc.", country=cc, admin_region=adm, city=city,
        lat=lat, lon=lon, status=status, capacity_mw_it=None, capacity_source=None, generator_mw_permitted=None,
        cooling=cooling, first_year=fy, source_url=WIKI, source_type="wikipedia", licence="CC-BY-SA-4.0",
        ledger_entry_id=ledger, confidence=conf, coord_source_url=WIKI,
        notes=f"Existence/status corroborated by operator list {GOOG}. " + notes)

# ---------------------------------------------------------------------------
# 2. Texas TCEQ Title V application packages (Core Data Form decimal coordinates)
TCEQ = "https://www.tceq.texas.gov/assets/public/permitting/air/reports/applications/"
add(name="Microsoft SN Campus (SN1, SN2, SN4, SN7), San Antonio", operator="Microsoft", parent_company="Microsoft Corporation",
    country="USA", admin_region="Texas", city="San Antonio", lat=29.480036, lon=-98.692555, status="operating",
    capacity_mw_it=None, capacity_source=None, generator_mw_permitted=176.5, cooling="unknown", first_year=None,
    source_url=TCEQ+"38509-ac.pdf", source_type="permit", licence="public_record", ledger_entry_id=None, confidence="high",
    coord_source_url=TCEQ+"38509-ac.pdf",
    notes="TCEQ abbreviated Title V application (2025-07-10), Reg. 82486, RN105295687, 5150 Rogers Rd, Bexar County; NAICS 518210. 73 Tier-2 diesel emergency generators: SN1 12x2.5 MW, SN2 12x2.5 MW, SN4 2x1.5+20x2+4x2.5 MW, SN7 1x0.5+16x3+6x2.5 MW = 176.5 MW (summed from OP-SUM tables). Texas Comptroller register lists 'Microsoft Corporation (SAT09-SAT13)', '(SAT 15-17)', '(SAT 80-85)', '(SAT 89-90)' and 'Microsoft San Antonio (SAT14)'.")
add(name="Childress Data Center (IREN)", operator="IE US Development Holdings 3 Inc. (IREN)", parent_company="IREN Ltd",
    country="USA", admin_region="Texas", city="Childress", lat=34.383232, lon=-100.056272, status="operating",
    capacity_mw_it=None, capacity_source=None, generator_mw_permitted=None, cooling="unknown", first_year=None,
    source_url=TCEQ+"40835-ac.pdf", source_type="permit", licence="public_record", ledger_entry_id=None, confidence="medium",
    coord_source_url=TCEQ+"40835-ac.pdf",
    notes="TCEQ Title V permit O4951 (project 40835), RN111563557, Childress County; TCEQ letters dated 2026-08-20. Coordinates from the TCEQ letter's map-marker link (marker=-100.056272,34.383232), described as a courtesy, not from the Core Data Form. Texas Comptroller register: 'Horizon' (IE US Development Holdings 3) and 'Sweetwater II' (IE US Development Holdings 7). Generator/turbine inventory not readable in fetched text.")
add(name="Compass Red Oak Datacenter (DFW III)", operator="Compass Datacenters DFW III, LLC", parent_company="Compass Datacenters (tenant: Microsoft per Texas Comptroller register)",
    country="USA", admin_region="Texas", city="Red Oak", lat=32.537981, lon=-96.804371, status="operating",
    capacity_mw_it=None, capacity_source=None, generator_mw_permitted=None, cooling="unknown", first_year=None,
    source_url=TCEQ+"37072-ac.pdf", source_type="permit", licence="public_record", ledger_entry_id=None, confidence="high",
    coord_source_url=TCEQ+"37072-ac.pdf",
    notes="TCEQ Title V application (submitted 2024-08-29), permit O4679, RN111028916, 300 Houston School Rd, Ellis County; NAICS 518210. 390 diesel emergency generators (EMGEN1-390) listed; kW ratings not in fetched text. Texas Comptroller register: 'Red Oak Texas Data Center' (effective 2022-02-14) and 'Red Oak Texas Data Center 2' (2024-03-14), occupant Microsoft Corporation.")
add(name="Alamo Mission data center, Red Oak", operator="Alamo Mission LLC", parent_company="undisclosed",
    country="USA", admin_region="Texas", city="Red Oak", lat=32.531786, lon=-96.792527, status="permitted",
    capacity_mw_it=None, capacity_source=None, generator_mw_permitted=None, cooling="unknown", first_year=None,
    source_url=TCEQ+"37459-tc.pdf", source_type="permit", licence="public_record", ledger_entry_id=None, confidence="medium",
    coord_source_url=TCEQ+"37459-tc.pdf",
    notes="TCEQ Title V permit O4709 (project 37459), RN110852753, permit area 156 N Austin Blvd / regulated entity 500 E Ovilla Rd, Red Oak, Ellis County; NAICS 518210, primary business 'DATA CENTER'; OP-1 submitted 2025-06-25. Seven generator groups (GRP-1..GRP-4A), unit counts not stated. Google's operator list names 'Red Oak, Texas' as a Google location but this registrant is not confirmed as Google.")

# ---------------------------------------------------------------------------
# 3. Sites carried from the Global AI compute ledger (coordinates = ledger entry lat/lon, 2-decimal, unverified this session)
LEDGER_NOTE = "Coordinates are the ledger entry's 2-decimal lat/lon (approx. +/-0.5 km), not re-derived this session. "
def ledger(name, operator, parent, cc, adm, city, lat, lon, status, src, stype, lic, lid, notes, cap=None, capsrc=None, gen=None, cooling="unknown", fy=None, conf="low"):
    add(name=name, operator=operator, parent_company=parent, country=cc, admin_region=adm, city=city, lat=lat, lon=lon,
        status=status, capacity_mw_it=cap, capacity_source=capsrc, generator_mw_permitted=gen, cooling=cooling, first_year=fy,
        source_url=src, source_type=stype, licence=lic, ledger_entry_id=lid, confidence=conf,
        coord_source_url=f"registry/ (ledger entry {lid})", notes=LEDGER_NOTE+notes)

ledger("xAI Colossus 1 (South Memphis)", "xAI", "xAI / SpaceXAI", "USA", "Tennessee", "Memphis", 35.05, -90.14, "operating",
       "https://interactive.localmemphis.com/pdfs/2024-08-26-Letter-to-SCHD-re-xAI-operating-without-permits.pdf", "ledger", "public_record",
       "us-tn-memphis-xai-colossus-turbines",
       "Shelby County Health Dept construction permit (2025-07-02) for 15 Solar SMT-130 gas turbines up to 247 MW (on-site generation, not diesel backup); upheld 2025-12-15. Epoch AI lists Colossus 2 (Memphis) at 946 MW IT, operational.",
       gen=247.0, fy=2024)
ledger("xAI Colossus 2 / MZX Tech Southaven turbine site", "xAI (MZX Tech)", "xAI / SpaceXAI", "USA", "Mississippi", "Southaven", 34.99, -90.0, "operating",
       "https://earthjustice.org/document/mdeq-mzx-tech-agreed-order", "permit", "public_record", "us-ms-southaven-xai-1.2gw-gas",
       "Ledger coordinate is near the TN/MS line; it may represent the Southaven permanent power-plant site (MDEQ permit for 41 gas turbines, 1.2 GW, approved ~2026-03-10) rather than the Colossus 2 data halls in Memphis. 69 temporary trailer-mounted turbines under MDEQ retirement schedule to 2027-07-14.",
       gen=1200.0, fy=2025)
ledger("Meta Hyperion data center (Holly Ridge)", "Meta (Laidley LLC)", "Meta Platforms", "USA", "Louisiana", "Holly Ridge (Richland Parish)", 32.5, -91.68, "under_construction",
       "https://lpsc.louisiana.gov/docs/minutes/August-20-2025-Minutes.pdf", "register", "public_record", "us-la-richland-meta-entergy-gas",
       "LPSC Docket U-37425 settlement (2025-08-20): three 754 MW Entergy CT plants (2,262 MW) for the site. LDEQ minor-source air permit (July 2025, amended 2026-06-06): 31 emergency diesel generators + 44 gas boilers, 96.83 tpy NOx; generator MW not stated. Epoch AI: Meta Hyperion in frontier list.")
ledger("AWS Susquehanna campus (Salem Township)", "Amazon Web Services", "Amazon.com Inc.", "USA", "Pennsylvania", "Salem Township (Luzerne County)", 41.09, -76.15, "operating",
       "https://www.power-eng.com/business/policy-and-regulation/ferc-rejects-amended-interconnection-agreement-for-amazon-data-center-at-susquehanna-nuclear-plant/", "ledger", "ledger",
       "us-pa-susquehanna-talen-aws-colocation",
       "FERC (accession 20241101-3061) rejected raising co-located load from 300 MW to 480 MW; Talen FY2025 10-K: PPA up to 1,920 MW through 2042, moving front-of-meter 2026-27. capacity_mw_it = 300 MW existing co-located ISA load (grid-side figure, not IT load).",
       cap=300.0, capsrc="register")
ledger("Homer City Energy Campus (former coal plant)", "Homer City Redevelopment / Homer City Generation LP", "Knighthead Capital (~75%)", "USA", "Pennsylvania", "Homer City (Indiana County)", 40.51, -79.2, "permitted",
       "https://files.dep.state.pa.us/regionalresources/NWRO/NWROPortalFiles/Homer-City/Air/Final-AQ-Plan-Approval/Tech%20Review%20Memo%20Signed%2020251118.pdf", "permit", "public_record",
       "us-pa-homer-city-gas-campus",
       "PA DEP Plan Approval 32-00457A (memo signed 2025-11-18): 7 GE 7HA.02 combined-cycle + 10 FT8 MOBILEPAC units = 4,678 MWe on-site gas generation for a data-center campus; power from 2027.",
       gen=4678.0)
ledger("Microsoft Fairwater (Mount Pleasant)", "Microsoft", "Microsoft Corporation", "USA", "Wisconsin", "Mount Pleasant (Racine County)", 42.72, -87.89, "operating",
       "https://psc.wi.gov/Pages/CommissionActions/CasePages/OakCreekGeneration.aspx", "register", "public_record", "us-wi-mount-pleasant-microsoft-we-energies",
       "PSC Wisconsin docket 6630-CE-317 (2025-07-02) approved 1,100 MW Oak Creek gas plant citing data-center load; Microsoft 15-year service contract signed 2026-07-16. Microsoft: closed-loop zero-water-evaporation cooling pilot 2026. Epoch AI/GDELT list 'Fairwater (Mount Pleasant)' at 300 MW current power (CC-BY, not used for capacity column).",
       cooling="closed_loop")
ledger("Microsoft Goodyear (PHX) campus", "Microsoft", "Microsoft Corporation", "USA", "Arizona", "Goodyear", 33.44, -112.36, "operating",
       "https://www.datacenterdynamics.com/en/news/microsoft-swapping-water-for-air-cooling-at-campus-in-phoenix-arizona/", "ledger", "ledger", "us-az-goodyear-mesa-water-records-vs-claims",
       "City of Goodyear amended development agreement (March 2023): discharge cap 500,000 gal/day; all buildings after PHX-12 air-cooled (earlier buildings evaporative). Maricopa County AQD permits (sources.json us-az-maricopa-aqd-records) not fetched.",
       cooling="air")
ledger("Microsoft West Des Moines (Willow Creek / Ginger East) data centers", "Microsoft", "Microsoft Corporation", "USA", "Iowa", "West Des Moines", 41.57, -93.71, "operating",
       "https://iowadnr.gov/portals/idnr/uploads/air/operpermit/draftpermits/7016d.pdf", "permit", "public_record", "us-ia-west-des-moines-microsoft-water",
       "Iowa DNR draft Title V (2024-11-07), file 77-02-040, 550 SE White Crane Rd & 1475 SE Maffitt Lake Rd; NAICS 518210; 128 diesel emergency engines, ~340.8 MW summed from permit tables (20 units assumed 3,000 kW where text truncated). Ledger coordinate is a centroid for Microsoft's five WDM sites; West Des Moines Water Works reports evaporative-cooling water use.",
       gen=340.8, cooling="evaporative")
ledger("Westin Building Exchange", "Digital Realty / Clise Properties", "Digital Realty Trust", "USA", "Washington", "Seattle", 47.61, -122.34, "operating",
       "https://www.bdcnetwork.com/energy-efficiency/article/55148128/amazon-will-heat-its-new-seattle-campus-with-waste-heat-from-next-door-data-centers", "ledger", "ledger", "us-wa-seattle-westin-amazon-heat-reuse",
       "Carrier hotel (~400,000 sq ft, 70% data center); up to 5 MW waste heat to Amazon Denny Triangle campus since Dec 2015. Included as a large urban facility, not hyperscale.")
ledger("Vantage Data Centers Profile Park campus (DUB1x; DUB13 refused)", "Vantage Data Centers", "Vantage Data Centers (DigitalBridge)", "IRL", "Dublin", "Clondalkin (Profile Park)", 53.32, -6.42, "operating",
       "https://www.pleanala.ie/anbordpleanala/media/abp/cases/orders/317/d317446.pdf", "register", "public_record", "ie-dublin-vantage-dub13-abp-refusal",
       "An Bord Pleanala ABP-317446-23 (2025) refused the DUB13 data hall (12,893 sq m, 13 backup generators) for lack of a grid connection agreement; the existing Profile Park campus is treated here as operating. Status of the wider campus not verified this session.")
ledger("Microsoft Middenmeer (Agriport A7) AMS campus", "Microsoft", "Microsoft Corporation", "NLD", "Noord-Holland", "Middenmeer (Hollands Kroon)", 52.8, 4.99, "operating",
       "https://datacenterdynamics.com/en/news/microsoft-gains-construction-permission-for-data-center-in-hollands-kroon", "ledger", "ledger", "nl-middenmeer-microsoft-water",
       "OD NZKG permit for AMS13/14 (2023); drinking-water use 84 million litres (2021) per Hollands Kroon/press; Tweede Kamer motion 2022-10-04. Agriport A7 is a nationally designated hyperscale area.")
ledger("Microsoft Kolabacken (Kirkkonummi) and Hepokorpi (Espoo) data centres", "Microsoft", "Microsoft Corporation", "FIN", "Uusimaa", "Kirkkonummi / Espoo", 60.22, 24.66, "under_construction",
       "https://www.fortum.com/media/2026/05/fortum-has-started-heat-production-two-large-data-centre-sites-finland", "ledger", "ledger", "fi-espoo-kirkkonummi-microsoft-fortum-heat",
       "Two sites represented by one ledger coordinate. Fortum heat-pump plants (180 MW district heat) started 2026-05; waste-heat recovery from the data centres phases in from 2027.")
ledger("AWS Bharat Future City / Chandanvelly campus", "Amazon Web Services", "Amazon.com Inc.", "IND", "Telangana", "Bharat Future City (near Hyderabad)", 17.1, 78.4, "under_construction",
       "https://www.datacenterdynamics.com/en/news/foundation-stone-laid-for-aws-data-center-development-in-telangana-india/", "ledger", "ledger", "in-telangana-aws-future-city",
       "Foundation stone ~2026-07-15; 300 acres (202 Future City + 98 Chandanvelly); MW not disclosed.")
ledger("Reliance-Meta Jamnagar AI data centre", "Reliance Industries / Meta", "Reliance Industries", "IND", "Gujarat", "Jamnagar", 22.47, 70.07, "announced",
       "https://superkalam.com/current-affairs/16-07-2026/green-energy-push-7-5-gw-capacity-target-gujarat-s-data-centre-policy-pg12-037f6c10-3313-4b69-8308-f866201d86b5", "ledger", "ledger", "in-gujarat-jamnagar-policy",
       "Tertiary source (citing Indian Express): 168 MW initial capacity, renewable power, desalinated seawater for cooling. Treat as unverified.")
ledger("SoftBank Tomakomai data centre", "SoftBank Corp.", "SoftBank Group", "JPN", "Hokkaido", "Tomakomai", 42.63, 141.6, "under_construction",
       "https://www.occto.or.jp/juyousoutei/2024/files/250122_juyousoutei.pdf", "ledger", "public_record", "jp-softbank-tomakomai",
       "SoftBank: 700,000 m2 site, >300 MW receiving capacity, opens FY2026, liquid cooling, 100% Hokkaido renewables (operator claim). OCCTO FY2025 demand assumption counts Hokkaido data-centre load but does not name the site.")
ledger("Scala AI City", "Scala Data Centers", "Scala Data Centers (DigitalBridge)", "BRA", "Rio Grande do Sul", "Eldorado do Sul", -30.08, -51.62, "under_construction",
       "https://www.gov.br/mme/pt-br/assuntos/secretarias/sntep/acesso-rede-basica/portarias-publicadas/2025/portaria_sntep_mme_2942", "register", "public_record", "br-eldorado-scala-ai-city",
       "MME Portaria SNTEP 2.942 (2025-05-09) recognised 525 kV access; company: 4.75 GW at full build, phase 1 ~50-54 MW IT; closed-loop cooling with initial charge only.",
       cap=54.0, capsrc="operator", cooling="closed_loop")
ledger("Data Center Pecém (Casa dos Ventos / Omnia)", "Casa dos Ventos", "Casa dos Ventos (reported client ByteDance)", "BRA", "Ceará", "Caucaia (Pecém)", -3.55, -38.8, "under_construction",
       "https://www.mpf.mp.br/o-mpf/unidades/pr-ce/noticias/mpf-e-dpu-vao-a-justica-para-impedir-operacao-de-data-center-no-complexo-do-pecem-em-caucaia-ce", "register", "public_record", "br-pecem-casadosventos-bytedance",
       "ONS connection approved 2025-05-30 (300 MW initial, up to 900 MW); Semace licences contested by MPF/DPU ACP 0080626-66.2026.4.05.8100 (2026-09-10). Closed-loop air-cooled chillers, 18-30 m3/day water.",
       cooling="air")
ledger("UAE-US AI Campus (incl. Stargate UAE 1 GW)", "G42 / Khazna", "G42", "ARE", "Abu Dhabi", "Abu Dhabi", 24.45, 54.65, "under_construction",
       "https://content.govdelivery.com/accounts/USDOC/bulletins/3e08f89", "ledger", "public_record", "ae-abudhabi-uae-us-ai-campus-5gw",
       "US Dept of Commerce release (2025-05-15): 5 GW campus; Stargate UAE first 200 MW targeted 2026. Site coordinate approximate; precise parcel not published.")
ledger("EcoCloud 'Project Eagle' (KenGen Green Energy Park, Olkaria)", "Olkaria EcoCloud Data Centre", "EcoCloud (G42 MoU partner)", "KEN", "Nakuru County", "Olkaria (Naivasha)", -0.88, 36.31, "under_construction",
       "https://datacenterdynamics.com/en/news/ground-broken-on-geothermal-powered-data-center-in-kenya", "ledger", "ledger", "ke-olkaria-ecocloud-geothermal",
       "Ground broken 2023-09-01: phase 1 24 MW IT (8 x 3 MW halls), 70 MW total draw, geothermal PPA with KenGen, air-cooled chilled water, target PUE <=1.25.",
       cap=24.0, capsrc="operator", cooling="air")
ledger("Road 1 Data Centre, Macquarie Park (Goodman)", "Goodman", "Goodman Group", "AUS", "New South Wales", "Macquarie Park (Sydney)", -33.78, 151.12, "permitted",
       "https://www.planningportal.nsw.gov.au/major-projects/projects/road-1-data-centre", "register", "public_record", "au-nsw-sydney-dc-water",
       "NSW Planning Portal SSD-80814238 approved 2026-10-01; 34.3 MW. Ledger coordinate is for the Sydney/Macquarie Park cluster, not parcel-verified.",
       cap=34.3, capsrc="register")

# ---------------------------------------------------------------------------
# sanity: dedupe site_id
seen = {}
for r in rows:
    sid = r["site_id"]
    if sid in seen:
        i = 2
        while f"{sid}-{i}" in seen: i += 1
        r["site_id"] = f"{sid}-{i}"
    seen[r["site_id"]] = 1
    assert r["lat"] is not None and r["lon"] is not None and r["source_url"], r
    assert -90 <= r["lat"] <= 90 and -180 <= r["lon"] <= 180, r

with open(f"{OUT_DIR}/seed_sites.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    for r in rows:
        w.writerow({k: ("" if v is None else v) for k, v in r.items()})
with open(f"{OUT_DIR}/seed_sites.json", "w", encoding="utf-8") as f:
    json.dump(rows, f, indent=1, ensure_ascii=False)
print("located rows:", len(rows))

# ---------------------------------------------------------------------------
# 4. Unlocated backlog: register-named sites for which no open coordinate source was reachable this session
UCOLS = ["backlog_id","register","name","operator_or_owner","occupant_or_tenant","country","admin_region","locality","record_id","record_date","program_or_type","generator_info","source_url","licence","notes"]
urows = []
DEQ = "https://www.deq.virginia.gov/news-info/shortcuts/permits/air/issued-air-permits-for-data-centers"
deq_raw = """Northrop Grumman Systems Corporation | 11541 | 05/16/2008 | Article 6 - mNSR | Russell County | Southwest
DP Facilities Inc South LLC | 11790 | 08/23/2016 | Article 6 - mNSR | Wise County | Southwest
Microsoft Corporation - East Coast Data Center | 21527 | 04/24/2024 | Article 1 - Title V | Mecklenburg County | Piedmont
Microsoft Corporation - East Coast Data Center | 21527 | 09/19/2023 | Article 6 - mNSR | Mecklenburg County | Piedmont
TECfusions Clarksville LLC | 30142 | 02/12/2025 | Article 6 - mNSR | Mecklenburg County | Piedmont
Equinix, LLC - CU 1-4 | 41064 | 08/10/2018 | Article 6 - mNSR | Culpeper County | Northern
QTS Richmond Data Center | 51232 | 06/24/2024 | Article 6 - mNSR | Henrico County | Piedmont
11751 Meadowville Owner LLC c/o GFH Capital Ltd | 52173 | 03/23/2007 | Article 6 - mNSR | Chesterfield County | Piedmont
Capital One Services Incorporated | 52281 | 07/10/2025 | Article 6 - mNSR | Henrico County | Piedmont
Peak 10 Incorporated | 52299 | 09/12/2013 | Article 6 - mNSR | Henrico County | Piedmont
Chirisa Richmond LLC | 52432 | 07/07/2025 | Article 6 - mNSR | Chesterfield County | Piedmont
Scout Development LLC | 52629 | 06/27/2019 | Article 6 - mNSR | Henrico County | Piedmont
Microsoft Corp - LVL Data Center | 52820 | 09/05/2023 | Article 6 - mNSR | Mecklenburg County | Piedmont
Microsoft Corporation - Timber Data Center | 52903 | 09/19/2023 | Article 6 - mNSR | Mecklenburg County | Piedmont
Microsoft Corporation - AVC Data Center | 52949 | 09/28/2023 | Article 6 - mNSR | Mecklenburg County | Piedmont
Microsoft Corp DCS - AVC09 Datacenter | 52973 | 07/23/2025 | Article 6 - mNSR | Mecklenburg County | Piedmont
Microsoft Corporation - AVC43 Datacenter | 53071 | 07/12/2023 | Article 6 - mNSR | Mecklenburg County | Piedmont
Microsoft Corp - LYH10 Datacenter | 53072 | 07/13/2023 | Article 6 - mNSR | Mecklenburg County | Piedmont
Microsoft Corp - AVC17 Datacenter | 53086 | 04/22/2025 | Article 6 - mNSR | Mecklenburg County | Piedmont
CLOP Ashland VA LLC | 53197 | 02/14/2025 | Article 6 - mNSR | Hanover County | Piedmont
Microsoft Corporation - LYH03 Datacenter | 53198 | 05/01/2025 | Article 6 - mNSR | Mecklenburg County | Piedmont
Sentara Healthcare | 60353 | 08/07/2015 | Article 6 - mNSR | Virginia Beach City | Tidewater
NOAA Wallops CDA Station | 61610 | 01/31/2013 | Article 6 - mNSR | Accomack County | Tidewater
Tysons Enterprise West, LLC | 71804 | 02/27/2009 | Article 5 - SOP | Fairfax County | Northern
Tysons Enterprise West, LLC | 71804 | 11/09/2016 | Article 6 - mNSR | Fairfax County | Northern
Coresite Real Estate 12100 Sunrise Valley Drive | 72296 | 01/31/2013 | Article 6 - mNSR | Fairfax County | Northern
Verizon Business Network Services, Inc. | 72367 | 02/26/2020 | Article 6 - mNSR | Loudoun County | Northern
Oath, Inc. | 72368 | 08/28/2009 | Article 6 - mNSR | Prince William County | Northern
Comcast Cablevision of Virginia Incorporated | 72374 | 03/27/2014 | Article 6 - mNSR | Prince William County | Northern
H5 Data Centers (Chantilly) | 72375 | 04/04/2014 | Article 6 - mNSR | Fairfax County | Northern
Freddie Mac Corporation | 73105 | 07/26/2007 | Article 6 - mNSR | Fairfax County | Northern
22810-22860 International Drive LLC | 73158 | 09/16/2003 | Article 6 - mNSR | Loudoun County | Northern
21110 Ridgetop Circle LLC | 73160 | 10/30/2019 | Article 6 - mNSR | Loudoun County | Northern
Digital Realty - Lemur Properties, LLC (VA3) | 73162 | 03/05/2010 | Article 6 - mNSR | Fairfax County | Northern
RREEF America REIT II Corp. VVV | 73170 | 11/22/2000 | Article 6 - mNSR | Fairfax County | Northern
Digital Realty - Porpoise Ventures LLC (VA4) | 73180 | 08/07/2008 | Article 6 - mNSR | Prince William County | Northern
Equinix LLC | 73199 | 04/28/2009 | Article 6 - mNSR | Loudoun County | Northern
Equinix, LLC - DC 14 | 73200 | 10/19/2006 | Article 6 - mNSR | Prince William County | Northern
Equinix, LLC - DC 14 | 73200 | 10/18/2007 | Article 6 - mNSR | Prince William County | Northern
Valo Park | 73230 | 01/09/2009 | Article 5 - SOP | Fairfax County | Northern
Equinix LLC | 73233 | 03/19/2024 | Article 6 - mNSR | Loudoun County | Northern
1571 Beaumeade Circle LLC | 73240 | 09/24/2024 | Article 6 - mNSR | Loudoun County | Northern
22995 Wilder Court LLC | 73293 | 08/12/2010 | Article 6 - mNSR | Loudoun County | Northern
Amazon Data Services, Inc. IAD-1 IAD-9 | 73294 | 10/11/2024 | Article 6 - mNSR | Fairfax County | Northern
Science Applications International Corp (SAIC) | 73326 | 07/14/2005 | Article 6 - mNSR | Fairfax County | Northern
VeriSign Incorporated Broad Run Facility2 | 73341 | 07/25/2008 | Article 6 - mNSR | Loudoun County | Northern
Amazon Data Services, Inc. IAD-6 IAD-13 IAD-54 | 73355 | 05/19/2025 | Article 6 - mNSR | Loudoun County | Northern
Inova Health Care Systems - IT Operations | 73363 | 07/16/2014 | Article 6 - mNSR | Loudoun County | Northern
New Dominion Technology Park II LLC | 73369 | 09/26/2007 | Article 6 - mNSR | Fairfax County | Northern
Digital Realty - Ashburn Campus | 73370 | 08/27/2013 | Article 6 - mNSR | Loudoun County | Northern
Digital Realty - Ashburn Campus | 73370 | 12/07/2016 | Article 6 - mNSR | Loudoun County | Northern
Digital Realty - Ashburn Campus | 73370 | 08/23/2017 | Article 6 - mNSR | Loudoun County | Northern
VPLS | 73567 | 11/07/2007 | Article 6 - mNSR | Fairfax County | Northern
Visa USA Incorporated | 73643 | 12/19/2007 | Article 6 - mNSR | Loudoun County | Northern
Visa USA Incorporated | 73643 | 08/28/2009 | Article 6 - mNSR | Loudoun County | Northern
Visa USA Incorporated | 73643 | 04/29/2010 | Article 6 - mNSR | Loudoun County | Northern
Visa USA Incorporated | 73643 | 10/13/2011 | Article 6 - mNSR | Loudoun County | Northern
Digital Loudoun Pkwy Center N LLC | 73670 | 10/04/2017 | Article 6 - mNSR | Loudoun County | Northern
Digital Loudoun Pkwy Center N LLC | 73670 | 03/14/2025 | Article 1 - Title V | Loudoun County | Northern
COPT - DC6 | 73683 | 08/24/2021 | Article 6 - mNSR | Prince William County | Northern
Zayo Group, LLC | 73717 | 01/15/2009 | Article 5 - SOP | Fairfax County | Northern
Zayo Group, LLC | 73717 | 05/29/2019 | Article 6 - mNSR | Fairfax County | Northern
Amazon Data Services, Inc. IAD-7 IAD-11 IAD-24 | 73741 | 05/21/2025 | Article 6 - mNSR | Prince William County | Northern
Zayo Group, LLC | 73743 | 08/04/2025 | Article 6 - mNSR | Loudoun County | Northern
QTS Dulles, LLC | 73757 | 07/30/2024 | Article 6 - mNSR | Loudoun County | Northern
Northrop Grumman Systems Corporation | 73798 | 03/02/2011 | Article 5 - SOP | Fairfax County | Northern
Verizon Services Corporation 74BXZ | 73808 | 08/30/2010 | Article 5 - SOP | Fairfax County | Northern
Equinix, LLC - DC 97 | 73809 | 06/03/2010 | Article 5 - SOP | Fairfax County | Northern
Northrop Grumman Services Corporation - Fairlakes | 73813 | 01/26/2011 | Article 5 - SOP | Fairfax County | Northern
Level 3 Communications Herndon Gateway | 73823 | 11/17/2014 | Article 6 - mNSR | Fairfax County | Northern
Amazon Data Services, Inc. IAD-10 IAD-32 IAD-98 IAD-99 IAD-118 IAD-119 IAD-129 | 73853 | 08/27/2024 | Article 6 - mNSR | Loudoun County | Northern
Amazon Data Services, Inc. IAD-12 IAD-15 IAD-16 IAD-76 | 73860 | 01/30/2025 | Article 6 - mNSR | Loudoun County | Northern
VADATA Inc MEG Four | 73868 | 04/14/2011 | Article 6 - mNSR | Loudoun County | Northern
PWCSA - L74 Neabsco Pumping Station | 73870 | 10/25/2013 | Article 6 - mNSR | Prince William | Northern
Northrop Grumman Systems Corporation | 73872 | 05/23/2011 | Article 6 - mNSR | Fairfax County | Northern
Intergate Ashburn Limited Liability Corporation | 73935 | 12/03/2024 | Article 6 - mNSR | Loudoun County | Northern
Equinix, LLC - Ashburn | 73946 | 10/01/2024 | Article 6 - mNSR | Loudoun County | Northern
George Washington University - VA Campus Bldg II | 73950 | 09/19/2011 | Article 6 - mNSR | Loudoun County | Northern
VA1 Data Center | 73954 | 11/11/2011 | Article 6 - mNSR | Loudoun County | Northern
The Aerospace Corporation | 73977 | 04/09/2012 | Article 6 - mNSR | Fairfax County | Northern
The Aerospace Corporation | 73977 | 08/19/2013 | Article 6 - mNSR | Fairfax County | Northern
Amazon Data Services, Inc. IAD-14 IAD-52 IAD-59 | 73995 | 05/08/2014 | Article 6 - mNSR | Prince William County | Northern
Freddie Mac Building - 8250 Jones Branch Drive | 74020 | 01/10/2013 | Article 6 - mNSR | Fairfax County | Northern
Amazon Data Services, Inc. IAD 50 IAD 60 IAD-71 IAD-78 IAD-79 IAD-80 | 74049 | 05/08/2024 | Article 6 - mNSR | Loudoun County | Northern
Captone Mission Ridge, LLC | 74051 | 08/08/2014 | Article 6 - mNSR | Fairfax County | Northern
Amazon Data Services, Inc. IAD-55 IAD-64 IAD-84 | 74052 | 04/25/2023 | Article 6 - mNSR | Prince William County | Northern
U.S. Customs and Border Protection | 74060 | 07/31/2014 | Article 6 - mNSR | Fairfax County | Northern
Amazon Data Services, Inc. IAD-51 IAD-56 IAD-88 IAD-89 | 74063 | 05/28/2024 | Article 6 - mNSR | Loudoun County | Northern
Amazon Data Services, Inc. IAD-57 IAD-58 | 74064 | 02/14/2014 | Article 6 - mNSR | Loudoun County | Northern
Corporate Office Properties, L.P. - Park Center | 74074 | 05/18/2022 | Article 6 - mNSR | Fairfax County | Northern
SI NVA01 ABS, LLC | 74079 | 08/21/2025 | Article 6 - mNSR | Loudoun County | Northern
Amazon Data Services, Inc. IAD-61 IAD-63 IAD-65 IAD-86 | 74080 | 01/21/2025 | Article 6 - mNSR | Loudoun County | Northern
Amazon Data Services, Inc. IAD-73 IAD-74 IAD-602 IAD-193 IAD-194 | 74081 | 07/08/2024 | Article 6 - mNSR | Prince William County | Northern
Amazon Data Services, Inc. IAD-62/68/81/83/93/609/614 | 74085 | 11/21/2022 | Article 6 - mNSR | Loudoun County | Northern
CyrusOne Loudoun Tech Center | 74086 | 11/01/2016 | Article 6 - mNSR | Loudoun County | Northern
VA2 Data Center | 74094 | 01/13/2016 | Article 6 - mNSR | Loudoun County | Northern
Cloud HQ | 74107 | 07/26/2021 | Article 6 - mNSR | Prince William County | Northern
CyrusOne Northern Virginia Data Center - Shaw Road | 74109 | 10/13/2016 | Article 6 - mNSR | Loudoun County | Northern
Iron Mountain Information Management LLC | 74112 | 10/16/2024 | Article 6 - mNSR | Prince William County | Northern
CyrusOne Kincora | 74114 | 09/06/2022 | Article 6 - mNSR | Loudoun County | Northern
Amazon Data Services, Inc. IAD-75 IAD-85 IAD-95 IAD-96 | 74115 | 10/21/2024 | Article 6 - mNSR | Prince William County | Northern
Cashvad Ventures LLC | 74118 | 10/15/2021 | Article 6 - mNSR | Manassas City | Northern
VA3 through VA6 Data Center | 74120 | 07/11/2025 | Article 6 - mNSR | Loudoun County | Northern
Amazon Data Services, Inc. IAD-90 IAD-91 IAD-92 | 74121 | 11/06/2024 | Article 6 - mNSR | Loudoun County | Northern
Digital Loudoun 3 & 4, LLC | 74126 | 10/12/2022 | Article 6 - mNSR | Loudoun County | Northern
Vint Hill Data Center LLC | 74127 | 10/06/2021 | Article 6 - mNSR | Fauquier County | Northern
Amazon Data Services, Inc. IAD-100 IAD-101 IAD-102 IAD-103 | 74129 | 06/28/2021 | Article 6 - mNSR | Prince William County | Northern
CoreSite Reston Campus | 74130 | 03/03/2022 | Article 6 - mNSR | Fairfax County | Northern
QTS Investment Properties Ashburn LLC | 74141 | 06/10/2025 | Article 6 - mNSR | Loudoun County | Northern
Equinix LLC - DC 13 | 74147 | 02/26/2020 | Article 6 - mNSR | Loudoun County | Northern
Amazon Data Services, Inc. IAD-114 IAD-115 | 74150 | 08/27/2024 | Article 6 - mNSR | Loudoun County | Northern
Wheeler Data Center | 74152 | 01/30/2024 | Article 6 - mNSR | Loudoun County | Northern
Amazon Data Services, Inc. IAD-144 IAD-145 | 74153 | 06/21/2024 | Article 6 - mNSR | Loudoun County | Northern
Aerospace Data Facility - East | 74154 | 02/21/2023 | Article 6 - mNSR | Fairfax County | Northern
LC-1 and LC-2 Data Centers | 74155 | 02/12/2025 | Article 6 - mNSR | Loudoun County | Northern
Sentinel Ashburn Nexus | 74156 | 11/08/2018 | Article 6 - mNSR | Loudoun County | Northern
Compass IAD Datacenter | 74160 | 01/20/2023 | Article 6 - mNSR | Loudoun County | Northern
QTS Investment Properties Manassas LLC | 74161 | 10/01/2024 | Article 6 - mNSR | Prince William County | Northern
Vantage Data Centers | 74162 | 04/20/2022 | Article 6 - mNSR | Loudoun County | Northern
Hayden Data Center | 74163 | 04/30/2025 | Article 6 - mNSR | Loudoun County | Northern
CyrusOne Northern Virginia Data Center - Maries Road | 74164 | 10/03/2022 | Article 6 - mNSR | Loudoun County | Northern
Amazon Data Services, Inc. IAD-132 IAD-133 | 74167 | 08/05/2022 | Article 6 - mNSR | Prince William County | Northern
Aligned Energy Data Centers (Ashburn), LLC | 74169 | 07/18/2022 | Article 6 - mNSR | Loudoun County | Northern
Amazon Data Services, Inc. IAD-116 IAD-117 | 74170 | 08/08/2025 | Article 6 - mNSR | Loudoun County | Northern
Amazon Data Services (IAD-130 and IAD-131) | 74171 | 01/27/2023 | Article 6 - mNSR | Prince William County | Northern
Remington Technology Park Limited Partnership | 74172 | 12/06/2022 | Article 6 - mNSR | Fauquier County | Northern
CyrusOne Sterling IX/X/XI | 74173 | 11/06/2025 | Article 6 - mNSR | Loudoun County | Northern
Amazon Data Services, Inc. IAD-150 IAD-151 IAD-152 | 74174 | 08/09/2019 | Article 6 - mNSR | Loudoun County | Northern
VAdata Inc IAD-146 & IAD-147 | 74181 | 03/19/2020 | Article 6 - mNSR | Loudoun County | Northern
Amazon Data Services, Inc. IAD-140/141/143 | 74184 | 08/01/2022 | Article 6 - mNSR | Loudoun County | Northern
Equinix LLC (DC-21/DC-22) | 74189 | 10/17/2025 | Article 6 - mNSR | Loudoun County | Northern
Amazon DCA-50 | 74190 | 07/16/2020 | Article 6 - mNSR | Culpeper County | Northern
QTS LLC - Ashburn-Shellhorn Data Center | 74197 | 02/04/2022 | Article 6 - mNSR | Loudoun County | Northern
Amazon Data Services - DCA-51 | 74198 | 07/16/2024 | Article 6 - mNSR | Fauquier County | Northern
Microsoft | 74201 | 02/08/2023 | Article 6 - mNSR | Fauquier County | Northern
Amazon Data Services Inc IAD-120/121/122 | 74205 | 11/15/2024 | Article 6 - mNSR | Loudoun County | Northern
Amazon DCA-54 | 74207 | 07/16/2024 | Article 6 - mNSR | Fairfax County | Northern
Digital Western Lands LLC | 74212 | 10/10/2025 | Article 6 - mNSR | Loudoun County | Northern
Amazon Data Services Inc IAD-161, IAD-162, IAD-606, IAD-285, IAD-286, IAD-299, IAD-611 | 74214 | 07/09/2024 | Article 6 - mNSR | Loudoun County | Northern
Nova Mango Farms LLC | 74216 | 02/27/2024 | Article 6 - mNSR | Prince William County | Northern
Microsoft Corp - Ashburn Data Center IAD02/IAD03 | 74220 | 03/07/2025 | Article 6 - mNSR | Loudoun County | Northern
Microsoft Corp Blue Ridge Data Center IAD11 | 74221 | 07/21/2025 | Article 6 - mNSR | Loudoun County | Northern
STACK Infrastructure NVA02D | 74224 | 10/16/2023 | Article 6 - mNSR | Prince William County | Northern
Amazon Data Services Inc - IAD-163/164/174 | 74227 | 06/21/2024 | Article 6 - mNSR | Loudoun County | Northern
ASH2 Lockridge Data Center - QTS Investment Properties Ashburn II LLC | 74232 | 08/05/2024 | Article 6 - mNSR | Loudoun County | Northern
Darab Ventures One LLC | 74234 | 10/31/2025 | Article 6 - mNSR | Loudoun County | Northern
Cologix ASH1 | 74235 | 07/23/2025 | Article 6 - mNSR | Loudoun County | Northern
Microsoft - Gainesville Data Center - MNZ03 | 74236 | 08/05/2024 | Article 6 - mNSR | Prince William County | Northern
Microsoft - Manassas Data Center - MNZ01 | 74237 | 01/17/2024 | Article 6 - mNSR | Prince William County | Northern
Amazon Data Services Inc - IAD-134/135/136 | 74239 | 09/09/2022 | Article 6 - mNSR | Fairfax County | Northern
Amazon Data Services Inc - IAD-104/105/106 | 74240 | 03/08/2024 | Article 6 - mNSR | Manassas City | Northern
Gainesville Crossing Data Campus | 74241 | 10/07/2024 | Article 6 - mNSR | Prince William County | Northern
Vantage Data Centers VA2 LLC | 74242 | 09/15/2023 | Article 6 - mNSR | Loudoun County | Northern
Amazon Data Services Inc IAD-169/179 | 74244 | 08/27/2024 | Article 6 - mNSR | Loudoun County | Northern
STACK Infrastructure NVA13 | 74246 | 02/24/2025 | Article 6 - mNSR | Manassas City | Northern
Aligned Data Centers IAD03 | 74247 | 01/06/2023 | Article 6 - mNSR | Loudoun County | Northern
Amazon Data Services Inc IAD-156 | 74250 | 06/24/2025 | Article 6 - mNSR | Loudoun County | Northern
Amazon Data Services IAD-215 | 74252 | 06/08/2023 | Article 6 - mNSR | Loudoun County | Northern
NTT Global Data Centers VA10 LLC | 74260 | 11/03/2023 | Article 6 - mNSR | Prince William County | Northern
Digital Realty - Brick Plant Data Center | 74262 | 08/29/2025 | Article 6 - mNSR | Manassas City | Northern
Digital Realty - Sterling Premiere LLC | 74264 | 09/20/2024 | Article 6 - mNSR | Loudoun County | Northern
Yondr Data Center | 74265 | 10/22/2024 | Article 6 - mNSR | Loudoun County | Northern
STACK Infrastructure - SI NVA06A LLC | 74269 | 06/18/2024 | Article 6 - mNSR | Loudoun County | Northern
Amazon Data Services Inc - DCA-060 | 74270 | 10/25/2023 | Article 6 - mNSR | Culpeper County | Northern
Amazon Data Services Inc - DCA-064 | 74272 | 10/25/2023 | Article 6 - mNSR | Fairfax County | Northern
Amazon Data Services Inc - IAD-165/166/167/168/613 | 74273 | 12/19/2023 | Article 6 - mNSR | Fairfax County | Northern
Amazon Data Services Inc IAD-124/125/126/127 | 74274 | 12/27/2023 | Article 6 - mNSR | Loudoun County | Northern
H5 Data Centers - Ashburn | 74276 | 11/13/2023 | Article 6 - mNSR | Loudoun County | Northern
Amazon Data Services Inc IAD-195/196/197/198 | 74277 | 08/21/2025 | Article 6 - mNSR | Prince William County | Northern
Amazon Data Services Inc IAD-210/211 | 74278 | 10/31/2023 | Article 6 - mNSR | Prince William County | Northern
Vantage Data Center VA3 LLC | 74284 | 03/27/2024 | Article 6 - mNSR | Loudoun County | Northern
Vantage Data Centers VA16 LLC | 74287 | 10/15/2024 | Article 6 - mNSR | Loudoun County | Northern
Amazon Data Services Inc. IAD450 Cosner Tech Campus | 74288 | 10/30/2024 | Article 6 - mNSR | Spotsylvania County | Northern
CyrusOne – NVA14 | 74290 | 11/01/2024 | Article 6 - mNSR | Loudoun County | Northern
Amazon Data Services Inc - IAD - 550 Louisa REB | 74299 | 05/22/2025 | Article 6 - mNSR | Louisa County | Northern
Amazon Data Services Inc - IAD - 500/501 | 74300 | 03/12/2025 | Article 6 - mNSR | Fairfax County | Northern
Amazon Data Services Inc - IAD-667, IAD-668, IAD-669, IAD-670, and IAD-671 | 74301 | 03/12/2025 | Article 6 - mNSR | Loudoun County | Northern
MECP1 Ashburn 2, LLC | 74306 | 09/18/2025 | Article 6 - mNSR | Loudoun County | Northern
Amazon Data Services Inc IAD-350 | 74309 | 03/27/2025 | Article 6 - mNSR | Stafford County | Northern
1501 Moran Road Development Owner, LLC | 74315 | 04/15/2025 | Article 6 - mNSR | Loudoun County | Northern
Amazon Data Services Inc IAD-205/307/317/612/612x | 74317 | 08/28/2025 | Article 6 - mNSR | Manassas City | Northern
Amazon Data Services Inc - IAD-180 | 74323 | 09/10/2025 | Article 6 - mNSR | Loudoun County | Northern
Cardinal Energy Corporation | 80941 | 10/02/2025 | Article 6 - mNSR | Frederick County | Valley
Anthem CDC 3 | 81609 | 10/24/2013 | Article 6 - mNSR | Harrisonburg City | Valley"""
deq_seen = {}
for line in deq_raw.strip().splitlines():
    name, reg, date, prog, loc, office = [x.strip() for x in line.split("|")]
    # keep one row per registration, latest permit date (dates are mm/dd/yyyy)
    key = reg
    m, d, y = date.split("/")
    iso = f"{y}-{int(m):02d}-{int(d):02d}"
    if key in deq_seen and deq_seen[key]["record_date"] >= iso:
        deq_seen[key]["program_or_type"] += f"; also {prog} {iso}"
        continue
    if key in deq_seen:
        prev = deq_seen[key]
        prog = prog + f"; also {prev['program_or_type']} {prev['record_date']}"
    op = "Amazon Data Services" if re.search(r"amazon|vadata", name, re.I) else ("Microsoft" if re.search(r"microsoft", name, re.I) else "")
    deq_seen[key] = dict(backlog_id=f"va-deq-{reg}", register="Virginia DEQ issued air permits for data centers (statewide list, as of 2025-11-17)",
        name=name, operator_or_owner=op, occupant_or_tenant="", country="USA", admin_region="Virginia", locality=loc, record_id=f"DEQ registration {reg}",
        record_date=iso, program_or_type=f"{prog} ({office} Regional Office)", generator_info="see permit PDF (generator count/kW and run-hour limits); e.g. reg 74129 = 97 diesel gensets, ~236 MW",
        source_url=DEQ, licence="public_record", notes="No coordinates or street address on the DEQ list; permit PDFs (showpublisheddocument links) carry the street address. Geocode from permit address or EPA FRS.")
    if reg == "74129":
        deq_seen[key]["generator_info"] = "Permit (amended 2021-06-28): 93x2,500 ekW CAT 3516C-HD + 3x600 ekW + 1 transitory 2,000 ekW = ~236 MW; 10261-10321 Tanner Way, Manassas 20110. https://deq.virginia.gov/home/showpublisheddocument/25843/638628762496730000"
    if reg == "74085":
        deq_seen[key]["notes"] = "EPA FRS registry_id 110069993200, 42949/42948/42800 Fadeley Lane, Sterling VA 20166 (https://data.epa.gov/efservice/frs_facility_site/primary_name/containing/IAD-62/JSON). No coordinates in that FRS table."
urows += list(deq_seen.values())

TXC = "https://comptroller.texas.gov/taxes/data-centers/data-center-lists.php"
tx_q = """1102 McKinzie LLC Data Center | 02/23/2024 | 1102 McKinzie LLC | 1102 McKinzie LLC | 1102 McKinzie LLC
1242 McKinzie LLC Data Center | 06/11/2024 | 1242 McKinzie LLC | 1242 McKinzie LLC | 1102 McKinzie LLC
3301 Hibbetts Road Data Center | 02/20/2024 |  | Coreweave, Inc. | Core Scientific, Inc.; Coreweave Compute Acquisition Co. II, LLC; CCAC IV.II, LLC
ALE60 Data Center | 01/01/2021 | COPT San Antonio LP | Amazon Data Services Inc. | Amazon Data Services Inc.
ALE61 Data Center | 01/01/2021 | Amazon Data Services Inc. | Amazon Data Services Inc. | Amazon Data Services Inc.
ALE62 Data Center | 01/01/2021 | Amazon Data Services Inc. | Amazon Data Services Inc. | Amazon Data Services Inc.
Austin Data Center 2 LLC | 01/15/2025 | Austin Data Center 2 LLC | Design, LLC | Google, LLC
Bastrop Project One | 12/06/2023 | Ocean Blockchain LLC | Ocean Blockchain LLC | Ocean Blockchain LLC
Bexar 1 | 07/24/2026 | Amazon Data Services, Inc. | Amazon Data Services, Inc. | Amazon Data Services, Inc.
C1 Dallas - Allen (LOT 1) LLC | 11/01/2024 | C1 Dallas - Allen (LOT 1) LLC | Oracle America Cloud Services LLC | C1 Dallas - Allen (LOT 1) LLC; Oracle America, Inc.
C1 Richardson LLC Data Center | 05/08/2025 | C1 Richardson LLC | Coreweave, Inc. | C1 Richardson LLC
Canadian Breaks Data Center | 09/05/2024 | Zephyr Infrastructure LLC | American Bitcoin Operating LLC | Zephyr Infrastructure LLC
Cedarvale, Barslow/Pyote TX Data Center | 01/30/2024 | Ionic Digital Cedarvale LLC | Ionic Digital Mining LLC | Ionic Digital Mining LLC
Cipher Black Pearl LLC Data Center | 02/15/2024 | Cipher Black Pearl LLC | Cipher Black Pearl LLC | Cipher Black Pearl LLC
Cipher Mining Technologies Inc. - Odessa Site | 01/24/2023 | Cipher Mining Technologies Inc. | Cipher Mining Technologies Inc. | Cipher Mining Technologies Inc.
DFW 9 | 10/01/2025 | DB Data Center Red Oak, LLC | Oracle America Cloud Services LLC | Databank Holdings LTD; Oracle America, Inc.
DFW 10 | 10/01/2025 | DB Data Center Red Oak, LLC | Oracle America Cloud Services LLC | Databank Holdings LTD; Oracle America, Inc.
DFW 11 | 10/01/2025 | DB Data Center Red Oak, LLC | Oracle America Cloud Services LLC | Databank Holdings LTD; Oracle America, Inc.
DFW 12 | 10/01/2025 | DB Data Center Red Oak, LLC | Oracle America Cloud Services LLC | Databank Holdings LTD; Oracle America, Inc.
DFW 37 | 05/14/2025 | Digital Garland Campbell, L.P. | LinkedIn Corporation | Digital Garland Campbell, L.P.
Digital Garland | 06/13/2022 | DDI Garland, LLC | Wells Fargo Bank, NA | DDI Garland, LLC
Dory Creek LLC Data Center | 04/03/2023 | Bitdeer Inc. | Dory Creek LLC | Dory Creek LLC
Fort Blocks LLC Data Center | 01/01/2022 | Fort Blocks LLC | Fort Blocks LLC | Fort Blocks LLC
Fort Haskell Data Center | 01/16/2024 | Fort Haskell LLC | Fort Haskell LLC | Fort Haskell LLC
Giga Texas Datacenter | 03/25/2024 | Tesla, Inc. | Tesla, Inc. | Tesla, Inc.
Hackberry Data Center | 12/15/2025 | Silver Basin Digital Infrastructure LLC | American Bitcoin Operating LLC | Silver Basin Digital Infrastructure LLC
HELO1 DC | 06/08/2021 | GALAXY HELIOS I | COREWEAVE, INC. | GALAXY HELIOS I; Coreweave Compute Acquisition Co. III, LLC
Hockley Data Center | 07/20/2024 | SF HOUH LLC | SF HOUH LLC | SF HOUH LLC
Independence Data Center | 08/20/2024 |  | Core42 Holding US LLC | Core42 Holding US LLC
Lancium Fort Stockton Clean Campus | 07/20/2022 | Lancium LLC | Lancium LLC | Lancium LLC
Legacy Data Center SAT-1 | 09/14/2026 | 1000 Bolton Rd Owner, LLC | 1000 Bolton Rd Owner, LLC | 1000 Bolton Rd Owner, LLC
Leon Creek | 09/09/2026 | DDH-Lonestar-1, LLC | DDH-Lonestar-1, LLC | DDH-Lonestar-1, LLC
Lewisville DFW38 | 04/01/2022 | DDI Lewisville, LLC | Wells Fargo Bank National Association | DDI Lewisville, LLC
LBB01 Data Center | 07/10/2026 | ALIGNED DATA CENTERS (ABERNATHY) PROPCO, LLC | Lambda Procurement, LLC | Lambda, Inc.
LinkedIn Richardson Texas Data Center | 02/20/2014 | Collins Technology Park Partners LLC | LinkedIn Corporation | Collins Technology Park Partners LLC
Lonestar Taproot LLC - Pyote | 02/15/2022 | Lonestar Dream Inc. | Lonestar Dream Inc. | Lonestar Dream Inc.
Lonestar Taproot LLC - Tarbush | 02/15/2022 | Lonestar Dream Inc. | Lonestar Dream Inc. | Lonestar Dream Inc.
Microsoft Corporation | 12/01/2013 | Microsoft Corporation | Microsoft Corporation | Microsoft Corporation
Microsoft San Antonio (SAT14) | 08/18/2021 | Microsoft Corporation | Microsoft Corporation | Microsoft Corporation
NADC | 09/01/2013 | Microsoft Corporation | Chevron USA Inc. | McKinstry Essention, LLC
NTT Global Data Centers Americas - Dallas TX2 | 10/20/2022 | NTT Global Data Centers TX, LLC | Amazon Data Services, Inc. | NTT Global Data Centers Americas, Inc.
NTT Global Data Centers Americas - Dallas TX3 | 10/01/2022 | NTT Global Data Centers TX, LLC | Amazon Data Services, Inc. | NTT Global Data Centers Americas, Inc.
NTT Global Data Centers Americas - Dallas TX4 | 04/18/2024 | NTT Global Data Centers TX, LLC | Amazon Data Services, Inc. | NTT Global Data Centers Americas, Inc.
Princeton ProjectCo LLC | 06/30/2026 | Princeton ProjectCo LLC | Princeton ProjectCo LLC | Princeton ProjectCo LLC
Project Dorothy 3A | 09/08/2026 | STX-01 LLC | Chronoscale Corporation | STX-01 LLC
Project Royse | 09/14/2026 | GIGA AFM LLC | The Constant Company, LLC | The Constant Company, LLC
Project Star | 05/26/2026 | 3350 Marquis LP | 3350 Marquis LP | 3350 Marquis LP
QTS Irving DC3 Data Center | 02/09/2024 | QTS Irving DC3, LLC | Microsoft Corporation | QTS Irving DC3, LLC; Quality Technology Services, LLC
Rellis Campus Data and Research Center | 09/15/2020 | Rellis Campus Data and Research Center LLC | Rellis Campus Data and Research Center LLC | Rellis Campus Data and Research Center LLC
SA01 DATA CENTER | 10/01/2026 | Decennial TX, LLC | Decennial TX, LLC | Decennial TX, LLC
San Antonio Data Center II | 05/04/2016 | CyrusOne LLC | Microsoft Corporation | CyrusOne LLC
San Antonio Data Center III | 05/25/2017 | CyrusOne LLC | Microsoft Corporation | CyrusOne LLC
SDC Austin III LLC dba SDC Austin IV LLC | 08/24/2026 | SDC Austin III LLC | JS Data Center LLC | Sabey Data Center Properties LLC
SDC - Austin Tandem Data Center | 03/13/2024 | SDC - Austin LLC | Cirrascale Cloud Services, LLC | SDC - Austin LLC
SDC DFW VIII, L.P. | 03/27/2023 | SDC DFW VIII, L.P. | GOOGLE LLC | SDC DFW VIII, L.P.; Jones Lang La Salle Americas, Inc.; Design, LLC
SDC SATB1 | 03/10/2024 | SDC SA III, L.P. | Microsoft Corporation | SDC SA III, L.P.
State Farm Richardson Data Center | 06/01/2015 | JDM III SF Dallas DC LLC | State Farm Mutual Auto Ins. Co. | State Farm Mutual Auto Ins. Co.
Stream DFW VII Data Center | 02/07/2022 | SDC DFW VII LP | OBOE LLC | SDC Technology Services, LLC
Stingray | 06/26/2026 | Cipher Stingray LLC | Amazon Data Services, Inc. | Amazon Data Services, Inc.
Switch AUS 4 | 06/26/2025 | Switch, LTD | Coreweave, Inc. | Switch, LTD; Coreweave Compute Acquistion Co. III, LLC; Coreweave Financing DDTL V-V, LLC
Temple Green Data Center | 07/23/2021 | Rowan Moriah LLC. | Rhodium Renewables LLC | Rowan Moriah LLC.
Terisys Thompsons | 09/15/2026 | Terisys LLC | Terisys LLC | Terisys LLC
TX11 Data Center | 03/06/2024 | Vantage Data Centers TX11, LLC | Microsoft Corporation | Vantage Data Centers TX11, LLC; Vantage Data Centers Management Company LLC
USBTC Pecos Data Center | 04/01/2022 | U.S. Data Lone Star, Inc. | U.S. Data Lone Star, Inc. | U.S. Data Lone Star, Inc.
Walnut Springs ProjectCo LLC | 06/30/2026 | Walnut Springs ProjectCo LLC | Walnut Springs ProjectCo LLC | Walnut Springs ProjectCo LLC
West Texas Data Center | 05/04/2022 | WTDM OZB LLC | WTDM OZB LLC | WTDM OZB LLC; TNDS US Corp
Whinstone US Data Center | 06/30/2020 | Whinstone US Inc. | Whinstone US Inc. | Whinstone US Inc."""
tx_large = """Cipher Black Pearl LLC Data Center | 01/23/2026 | Cipher Black Pearl, LLC | Amazon Data Services, Inc. | Amazon Data Services, Inc.
Clocktower Quanah | 08/24/2026 | Osprey Land Holdings LLC | Paile LLC | Paile LLC
Cottonwood Data Center | 09/12/2025 | Core Scientific Inc. | Core Scientific Inc. | Core Scientific Inc.
Cutten Data Center | 10/10/2024 | SF HOUC, LLC | SF HOUC, LLC | SF HOUC, LLC
Cyrusone LLC - Houston West III Data Center | 01/31/2022 | Cyrusone LLC | Paile LLC | Cyrusone LLC
Denton Data Center | 09/19/2024 |  | Coreweave Compute Acquisition Co V LLC | Core Scientific, Inc.; Coreweave, Inc.
DFW02 LANCASTER (STACK) | 10/31/2025 | SI DFW02A, LLC | SI DFW02A, LLC | SI DFW02A, LLC; Stack Infrastructure III TRC, LLC
DFW-04 Data Center | 01/27/2026 | Aligned Data Centers (Plano) Propco, LLC | Lambda Cloud Fund II MCI DAL, LLC | Lambda, Inc.
ECX AUS11-16 | 04/24/2026 | EdgeConnex MCN Austin Property 5, LLC | EdgeConnex MCN Austin Operations 5, LLC | EdgeConnex MCN Austin Operations 5, LLC
ECX AUS31-36 | 07/08/2026 | EdgeConnex MCN Austin Property 7, LLC | EdgeConnex MCN Austin Operations 7, LLC | EdgeConnex MCN Austin Operations 7, LLC
EDC AUSTIN, LLC | 01/09/2026 | EDC Austin, LLC | EDC Austin, LLC | EDC Austin, LLC
EDC Fort Worth, LLC | 01/09/2026 | EDC Fort Worth LLC | Oracle America Cloud Services LLC | Oracle America, Inc.; EDC Fort Worth LLC; EDC OPCO LLC; CDE Acquisitions LLC
EdgeConneX AU02 | 07/11/2025 | DFW33220N, LLC | Coreweave, Inc. | DFW33220N Operations 1, LLC
Fermi Data Center 1 | 09/05/2025 | Fermi Inc. and affiliates | Fermi Equipment Holdco, LLC | Fermi Equipment Holdco, LLC
Flamingo | 08/10/2026 | Amazon Data Services, Inc. | Amazon Data Services, Inc. | Amazon Data Services, Inc.
Fluidstack Abernathy Data Center | 01/20/2026 | FS AB LLC | Anthropic, PBC | FS AB LLC
Freestone Data Center | 03/24/2026 | C1 Freestone 1, LLC | Paile, LLC | Paile, LLC
Giga Texas Datacenter | 04/10/2024 | Tesla, Inc. | Tesla, Inc. | Tesla, Inc.
Gulf Horizon Data Center | 05/04/2026 | Amazon Data Services, Inc. | Amazon Data Services, Inc. | Amazon Data Services, Inc.
HEL02 DC | 11/07/2025 | Galaxy Helios II LLC | Coreweave, Inc. | Coreweave, Inc.; Galaxy Helios II LLC; Galaxy Power, LLC
Hicks Field Data Center | 08/18/2026 | ACS DC Hicks Field Road, LLC | Paile LLC | Vanguard US Serviceco, LLC
Hockley Data Center | 08/20/2024 | SF HOUH LLC | SF HOUH LLC | SF HOUH LLC
Horizon | 07/24/2025 | IE US Development Holdings 3 Inc. | IE US HARDWARE 3 LLC | IE US Development Holdings 3 Inc.
Hutto Data Center 3 LLC | 03/10/2025 | Hutto Data Center 3 LLC; Hutto Data Center Campus Power LLC | Google LLC | Design, LLC; Google LLC
Hutto Data Center 4 LLC | 09/11/2026 | Hutto Data Center 4 LLC; Hutto Data Center Campus Power 2 LLC | Google LLC | Design, LLC; Google LLC
Hutto Data Center Campus LLC | 03/10/2025 | Hutto Data Center 1 LLC; Hutto Data Center 2 LLC; Hutto Data Center Campus Power LLC | Google LLC | Design, LLC; Google LLC; Hutto Data Center TKD LLC
Lancium Abilene Clean Campus | 05/26/2022 | Lancium LLC; Abilene DC 1, LLC | Oracle America Cloud Services, LLC | Oracle America, Inc.; Lancium LLC; Lancium Abilene, LLC
Lancium Abilene Clean Campus II | 05/26/2022 | Abilene DC 1, LLC | Oracle America Cloud Services, LLC | Lancium Abilene, LLC; Oracle America, Inc.
Lancium Abilene Clean Campus III | 01/28/2025 | Abilene DC 3 LLC | Oracle America Cloud Services, LLC | Oracle America, Inc.; Lancium LLC; Lancium Abilene, LLC
Lancium Abilene Clean Campus IV | 03/16/2025 | Abilene DC 4, LLC | Oracle America Cloud Services, LLC | Oracle America, Inc.; Lancium LLC; Lancium Abilene, LLC
Lancium Abilene Clean Campus V | 03/16/2025 | Abilene DC 5 LLC | Oracle America Cloud Services, LLC | Oracle America, Inc.; Lancium, LLC; Lancium Abilene, LLC
Lancium Abilene Clean Campus VI | 03/16/2025 | Abilene DC 6 LLC | Oracle America Cloud Services, LLC | Oracle America, Inc.; Lancium LLC; Lancium Abilene, LLC
Lancium Abilene Clean Campus VII | 03/16/2025 | Abilene DC 7 LLC | Oracle America Cloud Services, LLC | Oracle America, Inc.; Lancium, LLC; Lancium Abilene, LLC
Lancium Abilene Clean Campus VIII | 03/16/2025 | Abilene DC 8 LLC | Oracle America Cloud Services, LLC | Oracle America, Inc.; Lancium, LLC; Lancium Abilene, LLC
Lancium Abilene Clean Campus IX | 06/17/2026 | Abilene DC 9, LLC | Abilene DC 9, LLC | Lancium LLC
Lancium Abilene Clean Campus X | 06/17/2026 | Abilene DC 10, LLC | Abilene DC 10, LLC | Lancium LLC
Lancium Clean Campus - Childress 1 | 03/25/2025 | Lancium LLC | Lancium LLC | Lancium LLC
Lancium Clean Campus - Turkey 1 | 01/25/2026 | Lancium Turkey LLC | Lancium Turkey LLC | Lancium Turkey LLC
Lincoln Rackhouse | 03/21/2023 |  | Coreweave, Inc. | Coreweave, Inc.; Coreweave Compute Acquisition Co. II, LLC
Long Draw Data Center | 04/30/2026 | DDH-LONESTAR-4, LLC | DDH-LONESTAR-4, LLC | DDH-LONESTAR-4, LLC
Meitner Data Center | 04/27/2026 | IP Meitner DTC, LLC | Google LLC | IP Meitner, LLC; Design, LLC; Google LLC
Microsoft Corporation (SAT09 - SAT13) | 12/15/2015 | Microsoft Corporation | Microsoft Corporation | Microsoft Corporation
Microsoft Corporation (SAT 15-17) | 04/04/2023 | Microsoft Corporation | Microsoft Corporation | Microsoft Corporation
Microsoft Corporation (SAT 80-85) | 03/31/2022 | Microsoft Corporation | Microsoft Corporation | Microsoft Corporation
Microsoft Corporation (SAT 89-90) | 04/04/2024 | Microsoft Corporation | Microsoft Corporation | Microsoft Corporation
Milam County Data Center | 12/09/2025 | MDC Building 1, LLC | Orion DC I, LLC | Milam County DC, LLC
Milam County Data Center Phase 2 | 06/10/2026 | MDC Building 2, LLC | Orion DC I, LLC | Milam County DC, LLC
Nexus Data Centers (Hubbard) | 07/21/2025 | Nexus Data Centers, LLC and affiliates | Anthropic, PBC | Nexus Data Centers, LLC; Nexus Operations Hubbard LLC
Pecos Ranch Data Center | 08/10/2026 | Amazon Data Services, Inc. | Amazon Data Services, Inc. | Amazon Data Services, Inc.
Polmer LLC Data Center | 02/11/2022 | Polmer LLC | Polmer LLC | Polmer LLC
Poolside Data Center, Pecos County I | 10/23/2025 | Poolside LF Phase 1 DC OPS, LLC | Poolside LF Phase 1 DC OPS, LLC | Poolside LF Phase 1 DC OPS, LLC
Poolside Data Center, Pecos County II | 03/06/2026 | Poolside LF Phase 2 DC OPS, LLC | Poolside LF Phase 2 DC OPS, LLC | Poolside LF Phase 2 DC OPS, LLC
PowerCampus Dallas by Lancaster Data Center Campus LP | 02/21/2025 | Lancaster Data Center Campus LP | Design, LLC | Google, LLC
Project Goldeneye | 08/25/2026 | Montera Infrastructure II, LLC | Montera Infrastructure II, LLC | Montera Infrastructure II, LLC
Project Goodnight | 06/20/2025 | GN DC1, LLC; GN DC2, LLC | GN DC1, LLC | GN DC1, LLC; GN DC2, LLC
Project Lightning | 06/04/2026 | Vector Lightning, LLC | Vector Lightning, LLC | Vector Lightning Energy, LLC; Vector Power US LLC
Project Watertower | 03/24/2026 | Redwood Dallas SPV, LLC | Yondr USA, LLC | Yondr USA, LLC
Project Woodrow | 04/15/2026 | Nolan Ranch DC Owner LLC | Nolan Ranch DC Owner LLC | Nolan Ranch DC Owner LLC
Pyote Data Center | 07/11/2022 | DDH (North America) Inc. | DDH (North America) Inc. | DDH (North America) Inc.
QTS Irving 1 | 02/09/2024 | QTS Irving DC3-DC6, LLC | Microsoft Corporation | QTS Irving DC3-DC6 LLC
Red Oak Texas Data Center | 02/14/2022 | Compass Datacenters DFW III and IIIA-IIIE, LLC | Microsoft Corporation | Compass Datacenters, LLC
Red Oak Texas Data Center 2 | 03/14/2024 | Compass Datacenters DFW III and IIIF-IIIJ, LLC | Microsoft Corporation | Compass Datacenters, LLC
Riot Corsicana Data Center | 08/22/2023 | Riot Corsicana, LLC | Riot Corsicana, LLC | Riot Corsicana, LLC
Riot Corsicana Data Center I | 12/12/2025 | Riot Platforms, Inc. | Riot Platforms, Inc. | Riot Platforms, Inc. and affiliates
Riot Corsicana Data Center 02 | 05/21/2026 | Riot Platforms, Inc. | Riot Platforms, Inc. | Riot Platforms, Inc. and affiliates
Riot Rockdale | 10/03/2025 | Riot Platforms, Inc. | Riot Platforms, Inc. | Riot Platforms, Inc.; Whinstone US, Inc.; Riot Data Centers, LLC
Riot Rockdale Data Center 1 | 11/18/2025 | Riot Platforms, Inc. | Riot Platforms, Inc. | Riot Platforms, Inc. and affiliates
Riot Rockdale Data Center 2 | 06/01/2026 | Riot Platforms, Inc. | Riot Platforms, Inc. | Riot Platforms, Inc. and affiliates
Rise Data Center | 08/10/2026 | Platon Investments LLC | Google LLC | Design, LLC; Google Energy LLC
ROMAN | 09/29/2026 | Google LLC | Design, LLC | Google LLC
Scurry County Data Center Building | 07/31/2026 | SDC Building 1, LLC | Scurry County DC, LLC | Scurry County DC, LLC
Scurry County Data Center Building 2 | 07/31/2026 | SDC Building 2, LLC | Scurry County DC, LLC | Scurry County DC, LLC
Sharka Data Center | 10/01/2018 | Sharka LLC | Design LLC | Google LLC
South Monahans Datacenter | 10/08/2026 | Circe Monahans, LLC | Circe Monahans, LLC | Circe Monahans, LLC
Spectrum Data Center | 05/21/2026 | Amazon Data Services, Inc. | Amazon Data Services, Inc. | Amazon Data Services, Inc.
Stampede Data Center | 05/21/2026 | Rowan Stampede LLC | Polmer LLC | Rowan Stampede LLC
STN OD1 - Project Landman | 06/18/2026 | RXT POWER, LLC; STN INCORPORATED | RXT POWER, LLC | RXT POWER, LLC
Sweetwater II | 07/15/2025 | IE US DEVELOPMENT HOLDINGS 7 INC. | IE US HARDWARE 1 INC. | IE US DEVELOPMENT HOLDINGS 7 INC.
Temple Data Center | 01/21/2026 | Rowan Temple LLC | Polmer LLC | Rowan Temple LLC
Thelma Data Center | 08/11/2026 | Homebound Group LLC | Google LLC | Google LLC; Design, LLC
TX11-12 Data Center | 11/05/2025 | Vantage Data Centers TX11, LLC; Vantage Data Centers TX12, LLC | Oracle America Cloud Services, LLC | Vantage Data Centers Management Company, LLC; Oracle America, Inc.
TX21-22 Data Center | 11/05/2025 | Vantage Data Centers TX21, LLC; Vantage Data Centers TX22, LLC | Oracle America Cloud Services, LLC | Vantage Data Centers Management Company, LLC; Oracle America, Inc.
TX 301-310 Data Centers | 10/08/2025 | Vantage Data Centers TX301-TX310, LLC | Oracle America Cloud Services LLC | Vantage Data Centers; Oracle America, Inc.
Winner LLC d/b/a Ernst LLC | 06/22/2015 | Winner LLC d/b/a Ernst LLC | Winner LLC d/b/a Ernst LLC | Winner LLC d/b/a Ernst LLC
Wurldwide LLC DBA Statue LLC | 09/17/2025 | Wurldwide LLC | Roadrunner Leap LLC | Bluebonnet Crossing LLC; Wurldwide LLC"""
def tx_rows(raw, listname):
    out = []
    for i, line in enumerate(raw.strip().splitlines()):
        name, date, owner, occ, op = [x.strip() for x in line.split("|")]
        m, d, y = date.split("/")
        out.append(dict(backlog_id=f"tx-comptroller-{slug(name)}", register=f"Texas Comptroller {listname} (Tax Code 151.359/151.3595 registrations)",
            name=name, operator_or_owner=f"owner: {owner}; operator: {op}", occupant_or_tenant=occ, country="USA", admin_region="Texas", locality="",
            record_id="", record_date=f"{y}-{int(m):02d}-{int(d):02d}", program_or_type="sales-tax exemption registration (effective date)", generator_info="",
            source_url=TXC, licence="public_record", notes="Register gives no address or county; some entries are crypto-mining sites or project-LLC names. Geocode via TCEQ Central Registry (RN) or county records."))
    return out
urows += tx_rows(tx_q, "Registered Qualifying Data Center Projects")
urows += tx_rows(tx_large, "Registered Qualifying Large Data Center Projects (rows A-'Cipher' of this list were not captured)")

urows += [
 dict(backlog_id="ie-epa-P1177-01", register="EPA Ireland Industrial Emissions licence", name="ADSIL Greenhills data storage campus (Amazon)", operator_or_owner="Amazon Data Services Ireland Limited", occupant_or_tenant="Amazon Web Services",
      country="IRL", admin_region="Dublin", locality="Hibernian Industrial Estate, Greenhills Road, Tallaght, Dublin 24", record_id="P1177-01", record_date="2023-06-14", program_or_type="IE licence (IED Annex I 1.1 combustion >=50 MWth)",
      generator_info="46 diesel generators; combined thermal input cap 251.43 MWth at any one time", source_url="https://epawebapp.epa.ie/licences/lic_eDMS/090151b28087b563.pdf", licence="public_record",
      notes="Licence PDF carries no grid reference. Application acknowledgement: https://epawebapp.epa.ie/licences/lic_eDMS/090151b28086cc5d.pdf"),
 dict(backlog_id="ie-epa-P1181-01", register="EPA Ireland Industrial Emissions licence (review application LA011550)", name="ADSIL Drogheda IDA Business and Technology Park (Amazon)", operator_or_owner="Amazon Data Services Ireland Ltd", occupant_or_tenant="Amazon Web Services",
      country="IRL", admin_region="Louth/Meath", locality="Donore Road, Drogheda", record_id="P1181-01 / LA011550", record_date="2024-09", program_or_type="IE licence review (Class 2.1 combustion)",
      generator_info="Building A: 26 x 6.82 MWth + 1 x 2.19 MWth; Building B (extension): 26 x 6.82 MWth + 1 x 2.19 MWth; stated combined thermal input 306.06 MWth", source_url="https://epawebapp.epa.ie/licences/lic_eDMS/090151b28092b24f.pdf", licence="public_record",
      notes="Non-technical summary; no grid reference in the document."),
 dict(backlog_id="tx-tceq-O4794", register="TCEQ Title V application (statement of basis 38610)", name="CyrusOne SAT2 SAT3 SAT4 data center", operator_or_owner="CyrusOne LLC", occupant_or_tenant="Microsoft Corporation (per Texas Comptroller: 'San Antonio Data Center II/III')",
      country="USA", admin_region="Texas", locality="9554 Westover Hills Blvd, San Antonio, Bexar County", record_id="RN110660743 / permit O4794", record_date="2025-07-21", program_or_type="Title V (NAICS 518210)",
      generator_info="35 diesel emergency generators: 32 x MTU 16V4000G83 (2,499 kW) + 3 x MTU 12V2000G85 (890 kW) = ~82.6 MW", source_url="https://www.tceq.texas.gov/assets/public/permitting/air/reports/applications/38610-ac.pdf", licence="public_record",
      notes="OP-1 latitude/longitude fields blank in the application; statement of basis: https://www.tceq.texas.gov/assets/public/permitting/air/publicnotice/38610sob.pdf"),
 dict(backlog_id="sc-des-CP-50000183", register="South Carolina DES air construction permit", name="Autumn Timber LLC data center (undisclosed hyperscaler)", operator_or_owner="Autumn Timber LLC", occupant_or_tenant="",
      country="USA", admin_region="South Carolina", locality="not stated", record_id="CP-50000183 v1.0", record_date="2024-11-13", program_or_type="air construction permit (new data center)",
      generator_info="quantity and size of generators held confidential at applicant's request", source_url="https://www.des.sc.gov/sites/des/files/Documents/BAQ/Autumn%20Timber/Statement%20of%20Basis%20for%20AIR-Construction%20Permit%20-%20CP-50000183%20v1.0.pdf", licence="public_record",
      notes="Statement of basis gives no county, address or coordinates."),
 dict(backlog_id="nv-ndep-AP7374-4768", register="Nevada NDEP Class I Air Quality Operating Permit to Construct (director's review)", name="Amazon Data Services, Tahoe-Reno Industrial Center", operator_or_owner="Amazon Data Services, Inc.", occupant_or_tenant="Amazon Web Services",
      country="USA", admin_region="Nevada", locality="Tahoe-Reno Industrial Center, Storey County; Sections 10, 11, 14, 15, T19N R22E, M.D.B.&M. (PLSS, convertible to coordinates via BLM PLSS)", record_id="AP7374-4768 (FIN A2648)", record_date="2026-01-30", program_or_type="Class I OPTC (new)",
      generator_info="358 standby diesel emergency generators; ratings not stated", source_url="https://www.ndep.nv.gov/uploads/documents/ap7374-4768-directors-review.pdf", licence="public_record",
      notes="Proposed action: https://www.ndep.nv.gov/uploads/documents/ap7374-4768-proposed-action.pdf. Related NDEP dockets surfaced: AP7374-4671, AP7374-4749, AP7375-3672 (not fetched)."),
 dict(backlog_id="nc-daq-09733T10", register="North Carolina DAQ Title V permit (review hosted by EPA)", name="Tapaha Dynamics LLC (Google Lenoir) - permit record", operator_or_owner="Tapaha Dynamics, LLC (Google)", occupant_or_tenant="Google",
      country="USA", admin_region="North Carolina", locality="708 Lynhaven Drive, Lenoir, Caldwell County", record_id="09733T10 (application 1400204.24A)", record_date="2025-05-12", program_or_type="Title V",
      generator_info="120 existing + 43 new diesel emergency generators (new: 36x2,750 kW + 7x1,750 kW = 111.25 MW)", source_url="https://www.epa.gov/system/files/documents/2025-05/aq_f_1400204_20250512_prmt_pmtrvw_t10.pdf", licence="public_record",
      notes="Located in seed_sites via Wikipedia coordinates (usa-google-lenoir-data-center); listed here so the permit record is tracked."),
 dict(backlog_id="sg-imda-dc-cfa-2023", register="IMDA pilot Data Centre Call for Application (2023)", name="DC-CFA pilot awards (~80 MW): AirTrunk-ByteDance, Equinix, GDS, Microsoft", operator_or_owner="AirTrunk; Equinix; GDS; Microsoft", occupant_or_tenant="",
      country="SGP", admin_region="Singapore", locality="not stated", record_id="", record_date="2023-07", program_or_type="capacity allocation award (provisional)", generator_info="",
      source_url="https://imda.gov.sg/resources/press-releases-factsheets-and-speeches/press-releases/2023/four-data-centre-proposals-selected-as-part-of-pilot-data-centre-call-for-application", licence="public_record",
      notes="Ledger entry sg-imda-moratorium-capacity. Sites not located in the award notice."),
 dict(backlog_id="sg-edb-dc-cfa2-2026", register="EDB/IMDA second Data Centre Call for Application (2026)", name="DC-CFA2 awards (200 MW, Jurong Island): Digital Realty, Equinix, Keppel, ST Telemedia GDC (50 MW each)", operator_or_owner="Digital Realty; Equinix; Keppel; ST Telemedia GDC", occupant_or_tenant="",
      country="SGP", admin_region="Singapore", locality="Jurong Island", record_id="", record_date="2026-08-21", program_or_type="capacity allocation award (provisional); >50% green energy, Green Mark DC Platinum", generator_info="",
      source_url="https://www.edb.gov.sg/content/dam/edb-en/about-edb/media-releases/news/four-data-centre-proposals-selected-as-part-of-second-data-centre/Fact%20Sheet%20-Four%20data%20centre%20proposals%20selected%20as%20part%20of%20second%20data%20centre.pdf", licence="public_record",
      notes="Ledger entry sg-imda-moratorium-capacity. Jurong Island parcels not identified."),
]
with open(f"{OUT_DIR}/seed_sites_unlocated.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=UCOLS)
    w.writeheader()
    for r in urows:
        w.writerow({k: ("" if v is None else v) for k, v in r.items()})
print("unlocated backlog rows:", len(urows))
