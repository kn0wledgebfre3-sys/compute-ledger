#!/usr/bin/env python3
"""Build sites/ireland_sites.{json,csv} from records gathered 2026-10-20/21.
All values are embedded; coordinates are converted here from Irish Grid (EPSG:29903) or
Irish Transverse Mercator (EPSG:2157) values quoted in EPA documents.
"""
import csv, json, math, sys

# ---------------- coordinate conversion (no pyproj available) -----------------
def tm_inverse(E, N, a, b, lat0_deg, lon0_deg, k0, FE, FN):
    """Inverse Transverse Mercator (OS/OSi Redfearn series)."""
    lat0 = math.radians(lat0_deg); lon0 = math.radians(lon0_deg)
    e2 = (a*a - b*b)/(a*a)
    n = (a-b)/(a+b)
    def M(phi):
        return b*k0*((1+n+1.25*n*n+1.25*n**3)*(phi-lat0)
                     -(3*n+3*n*n+(21/8)*n**3)*math.sin(phi-lat0)*math.cos(phi+lat0)
                     +((15/8)*n*n+(15/8)*n**3)*math.sin(2*(phi-lat0))*math.cos(2*(phi+lat0))
                     -(35/24)*n**3*math.sin(3*(phi-lat0))*math.cos(3*(phi+lat0)))
    phi = (N-FN)/(a*k0) + lat0
    while True:
        m = M(phi)
        if abs(N-FN-m) < 1e-5: break
        phi = (N-FN-m)/(a*k0) + phi
    sp = math.sin(phi); cp = math.cos(phi); tp = math.tan(phi)
    nu = a*k0/math.sqrt(1-e2*sp*sp)
    rho = a*k0*(1-e2)/(1-e2*sp*sp)**1.5
    eta2 = nu/rho - 1
    VII = tp/(2*rho*nu)
    VIII = tp/(24*rho*nu**3)*(5+3*tp**2+eta2-9*tp**2*eta2)
    IX = tp/(720*rho*nu**5)*(61+90*tp**2+45*tp**4)
    X = 1/(cp*nu)
    XI = 1/(cp*6*nu**3)*(nu/rho+2*tp**2)
    XII = 1/(cp*120*nu**5)*(5+28*tp**2+24*tp**4)
    XIIA = 1/(cp*5040*nu**7)*(61+662*tp**2+1320*tp**4+720*tp**6)
    dE = E-FE
    lat = phi - VII*dE**2 + VIII*dE**4 - IX*dE**6
    lon = lon0 + X*dE - XI*dE**3 + XII*dE**5 - XIIA*dE**7
    return math.degrees(lat), math.degrees(lon)

def itm_to_wgs84(E, N):
    # ITM: GRS80 on ETRS89 (treated as WGS84)
    return tm_inverse(E, N, 6378137.0, 6356752.314140, 53.5, -8.0, 0.99982, 600000.0, 750000.0)

def ig_to_wgs84(E, N):
    # Irish Grid: Airy Modified on Ireland 1965 datum, then Helmert to WGS84 (OSi parameters)
    a, b = 6377340.189, 6356034.447
    lat, lon = tm_inverse(E, N, a, b, 53.5, -8.0, 1.000035, 200000.0, 250000.0)
    # geodetic -> cartesian on Airy Modified
    e2 = (a*a-b*b)/(a*a)
    p = math.radians(lat); l = math.radians(lon)
    nu = a/math.sqrt(1-e2*math.sin(p)**2)
    x = nu*math.cos(p)*math.cos(l); y = nu*math.cos(p)*math.sin(l); z = nu*(1-e2)*math.sin(p)
    # Helmert Ireland1965 -> ETRS89/WGS84 (OSi): tx=482.530 ty=-130.596 tz=564.557 rx=-1.042" ry=-0.214" rz=-0.631" s=8.150 ppm
    tx, ty, tz = 482.530, -130.596, 564.557
    rx, ry, rz = [math.radians(v/3600) for v in (-1.042, -0.214, -0.631)]
    s = 8.150e-6
    x2 = tx + (1+s)*x - rz*y + ry*z
    y2 = ty + rz*x + (1+s)*y - rx*z
    z2 = tz - ry*x + rx*y + (1+s)*z
    # cartesian -> geodetic on GRS80
    a2, b2 = 6378137.0, 6356752.314140
    e22 = (a2*a2-b2*b2)/(a2*a2)
    lon2 = math.atan2(y2, x2)
    pr = math.sqrt(x2*x2+y2*y2)
    lat2 = math.atan2(z2, pr*(1-e22))
    for _ in range(10):
        nu2 = a2/math.sqrt(1-e22*math.sin(lat2)**2)
        lat2 = math.atan2(z2+e22*nu2*math.sin(lat2), pr)
    return math.degrees(lat2), math.degrees(lon2)

def ll(sys_, E, N):
    lat, lon = itm_to_wgs84(E, N) if sys_ == "ITM" else ig_to_wgs84(E, N)
    return round(lat, 6), round(lon, 6)

# sanity check: Google row: Wikipedia 53.3201083,-6.4420639 vs GHG main entrance IG 303402,230546
_chk = ll("IG", 303402, 230546)
assert abs(_chk[0]-53.3201) < 0.01 and abs(_chk[1]+6.4420) < 0.01, _chk
# ITM/IG consistency check on the same emission point (Clonshaugh A3-1 quoted in both systems)
_a = ll("ITM", 718406, 740436); _b = ll("IG", 318465, 240412)
assert abs(_a[0]-_b[0]) < 0.0005 and abs(_a[1]-_b[1]) < 0.0005, (_a, _b)

LAST = "2026-10-20"
COLS = ["site_id","name","operator","parent_company","country","admin_region","city","lat","lon",
        "status","capacity_mw_it","capacity_source","generator_mw_permitted","cooling","first_year",
        "source_url","source_type","licence","ledger_entry_id","confidence","last_checked",
        "coord_source_url","notes","generator_mw_basis","generator_count"]

E = "https://epawebapp.epa.ie/licences/lic_eDMS/"
G = "https://www.epa.ie/publications/licensing--permitting/climate-change/"
P = "https://www.pleanala.ie/"

rows = []
def add(site_id, name, operator, parent, region, city, coord, status, gen_mw, basis, gen_n, cooling,
        source_url, source_type, conf, notes, first_year=None, cap_it=None, cap_src=None,
        ledger=None, coord_src=None, coord_reason=None, licence="public_record"):
    lat = lon = None
    if coord:
        lat, lon = coord
    r = dict(site_id=site_id, name=name, operator=operator, parent_company=parent, country="IRL",
             admin_region=region, city=city, lat=lat, lon=lon, status=status, capacity_mw_it=cap_it,
             capacity_source=cap_src, generator_mw_permitted=gen_mw, cooling=cooling, first_year=first_year,
             source_url=source_url, source_type=source_type, licence=licence, ledger_entry_id=ledger,
             confidence=conf, last_checked=LAST,
             coord_source_url=(coord_src if coord else None),
             notes=(notes if coord else ("NO COORDINATE: " + coord_reason + " | " + notes)),
             generator_mw_basis=basis, generator_count=gen_n)
    rows.append(dict((k, r[k]) for k in COLS))

# ---------------------------------------------------------------- AMAZON (EPA IE licences)
add("irl-amazon-grange-castle-south-abc-p1170",
    "Amazon Grange Castle South data storage campus (Buildings A-C; GHG 'DUB 69')",
    "Amazon Data Services Ireland Ltd", "Amazon.com Inc. (AWS)", "Dublin", "Clondalkin (Baldonnel Road, Dublin 22)",
    ll("IG", 303185, 230885), "operating", 460.87, "MWth rated thermal input, sum of units (inspector's report); licence Schedule A.1 caps simultaneous operation at 421.93 MWth", 73,
    "evaporative", E+"090151b28087f7ae.pdf", "permit", "high",
    "IE licence P1170-01 granted 6 Jul 2023 (application LA007494, received 17 Jan 2022). Inspector's report (29 May 2023): 70 x 6.49 MWth + 3 x 2.19 MWth diesel generators, 2 x 0.57 MWth fire pumps, 16.5 ha, Eircode D22 E7C9. Cooling: AHU free cooling, evaporative (mains water) above 30C, residual water to foul sewer. GHG permit IE-GHG203-03 (15 Aug 2025) 'Data Processing Centre - DUB 69' lists 70 x 6.49 MW + 3 x 2.19 MW + 4 roll-up units (~477.9 MW) at the same address; HVO added as fuel. Townlands Milltown, Ballybane, Aungierstown and Ballybane.",
    coord_src=E+"090151b2807f5a31.pdf (application form LA007494, site centre Irish Grid E303185 N230885)")

add("irl-amazon-grange-castle-south-cyrusone-plot-p1184",
    "Amazon Grange Castle South data storage installation (16-generator building on CyrusOne-leased plot)",
    "Amazon Data Services Ireland Ltd", "Amazon.com Inc. (AWS); landlord CyrusOne Irish Datacentres Holdings Ltd", "Dublin", "Clondalkin (Baldonnel Road, Dublin 22)",
    ll("ITM", 702828, 730760), "operating", 103.84, "MWth rated thermal input, sum of units (16 x 6.49 MWth); licence cap figure OCR-garbled (~90.86 MWth)", 16,
    "closed_loop", E+"090151b28087c6c5.pdf", "permit", "high",
    "IE licence P1184-01 granted 20 Jun 2023 (application LA009979, received 26 May 2022). Site c. 2.16 ha leased from CyrusOne Irish Datacentres Holdings Ltd (planning SD18A/0134 = ABP-302813-18 third-party appeal, 32 containerised generators, 32 chillers; and SD20A/0295). Operational report: closed-loop chilled water (20% glycol) with free coolers and R134a chillers. Eircode D22 T2P7. This is the CyrusOne Dublin campus.",
    coord_src=E+"090151b280821e25.pdf (attachment 7.4.2, emission point A3-01 E702828 N730760, values are ITM despite 'Irish National Grid' label)")

add("irl-amazon-airton-road-tallaght-dub56-p1173",
    "Amazon Airton Road data storage campus, Tallaght (GHG 'DUB 56')",
    "Amazon Data Services Ireland Ltd", "Amazon.com Inc. (AWS)", "Dublin", "Tallaght (Airton Road / Belgard Road, Dublin 24)",
    ll("ITM", 708808, 728572), "operating", 343.16, "MWth rated thermal input, sum of units (27 x 6.46 + 26 x 6.49); licence Schedule A.1 cap 317.26 MWth", 53,
    "evaporative", E+"090151b28087b246.pdf", "permit", "high",
    "IE licence P1173-01 granted 13 Jun 2023 (received 3 Mar 2022); Eircode D24 DA27; 8.12 ha; Buildings A and B; evaporative cooling in AHUs (closed loop, discharge at 1,500 uS/cm to storm network -> Tymon River). GHG permit IE-GHG184-10508-4 (29 Jan 2020) 'DUB 56 Data Processing Centre, Belgard Road, Tallaght' lists 54 emergency generators + 4 fire pumps, main entrance Irish Grid 308852/228212 (c. 340 m from the A3-1 stack), treated as the same campus. Ledger entry ie-tallaght-heatworks records an Amazon Tallaght data centre feeding the Tallaght District Heating Scheme; the SEAI record does not say which Amazon Tallaght campus.",
    coord_src=E+"090151b28080aa77.pdf (attachment 7.4.2 LA009874, emission point A3-1 E708808 N728572, ITM)")

add("irl-amazon-greenhills-road-tallaght-p1177",
    "Amazon Hibernian Industrial Estate data storage campus, Greenhills Road, Tallaght",
    "Amazon Data Services Ireland Ltd", "Amazon.com Inc. (AWS)", "Dublin", "Tallaght (Greenhills Road, Dublin 24)",
    ll("ITM", 709922, 728392), "operating", 251.43, "MWth rated thermal input, sum of units (37 x 5.19 + 9 x 6.60); licence Schedule A.1 cap 251.43 MWth", 46,
    "evaporative", E+"090151b28087b563.pdf", "permit", "high",
    "IE licence P1177-01 granted 14 Jun 2023 (application LA009911, received 26 Mar 2022); 7.72 ha; Buildings A (24 gens), B (13), C (9) plus 4 x 0.42 MWth fire pumps; AHU free cooling with evaporative (mains water) mode, closed loop. Already in seed_sites_unlocated backlog as ie-epa-P1177-01.",
    coord_src=E+"090151b2808106c0.pdf (attachment 7.4.2 LA009911, emission point A3-1 E709922 N728392, ITM)")

add("irl-amazon-blanchardstown-snugborough-road-p1172",
    "Amazon Blanchardstown Industrial Park data storage campus, Snugborough Road",
    "Amazon Data Services Ireland Ltd", "Amazon.com Inc. (AWS)", "Dublin", "Blanchardstown (Snugborough Road, Dublin 15)",
    ll("ITM", 708769.7, 740534.3), "operating", 416.52, "MWth total rated thermal input per inspector's report (70 generators 5.59/6.33/6.49 MWth + 2 x 0.42 MWth fire pumps); licence Schedule A.1 cap 374.17 MWth", 70,
    "evaporative", E+"090151b280882214.pdf", "permit", "high",
    "IE licence P1172-01 granted 19 Jul 2023 (application LA009828, received 24 Feb 2022); Eircode D15 V978; Buildings A-D; evaporative cooling in AHUs with recirculated mains water (~5 days/yr above 30C), UV disinfection.",
    coord_src=E+"090151b28080aae1.pdf (attachment 7.4.2 LA009828, emission point A3-01 E708769.7 N740534.3, ITM)")

add("irl-amazon-cruiserath-road-dub58-p1182",
    "Amazon Cruiserath Road data storage campus, Dublin 15 (GHG 'DUB 58')",
    "Amazon Data Services Ireland Ltd", "Amazon.com Inc. (AWS)", "Dublin", "Mulhuddart / Cruiserath (Dublin 15)",
    ll("IG", 307625, 242020), "operating", 432.72, "MWth rated thermal input, sum of units (66 x 6.49 + 2 x 2.19); licence Schedule A.1 cap 393.78 MWth", 68,
    "evaporative", E+"090151b28087cade.pdf", "permit", "high",
    "IE licence P1182-01 granted 21 Jun 2023 (received 19 Apr 2022); three two-storey buildings A-C; evaporative cooling (public water, closed loop, ~107 m3/day discharge to storm network -> Ballycoolen Stream). Planning FW19A/0087 (MIK Developments LLC, Buildings B and C, 24 generators each, granted 24 Jul 2019). GHG permit IE-GHG197-10524-1 (7 Apr 2020) 'DUB 58, Cruiserath' 27 generators + 2 fire pumps, main entrance Irish Grid 307625/242020. Expansion Buildings E/F/G: see row irl-amazon-cruiserath-buildings-efg-abp318180.",
    coord_src=G+"IE-GHG197-10524-1.pdf (GHG permit, site main entrance Irish Grid 307625/242020)")

add("irl-amazon-cruiserath-buildings-efg-abp318180",
    "Amazon (Universal Developers LLC) Cruiserath Road Buildings E, F and G - permitted expansion",
    "Universal Developers LLC (for Amazon Web Services)", "Amazon.com Inc. (AWS)", "Dublin", "Mulhuddart / Cruiserath (Dublin 15)",
    ll("IG", 307625, 242020), "permitted", None, "generator MW not stated in inspector's report (39 diesel emergency generators)", 39,
    "unknown", P+"anbordpleanala/media/abp/cases/reports/318/r318180.pdf", "register", "medium",
    "ABP-318180-23 (Fingal FW22A/0308): third-party appeals; Board granted with revised conditions 19 Dec 2025. 13.14 ha within 26.14 ha landholding; Buildings F and G 21,582 sq m GFA each + Building E 1,425 sq m; 39 diesel generators (HVO 'subject to availability'), 285 rooftop PV modules; existing 2017 grid connection agreement from Cruiserath 220 kV substation with incremental ramp to 2029; appellants cite an additional constant load of 73 MW. Coordinate is the existing campus main entrance from the DUB 58 GHG permit, not the new buildings; same campus as irl-amazon-cruiserath-road-dub58-p1182 (do not double count).",
    coord_src=G+"IE-GHG197-10524-1.pdf (campus main entrance, Irish Grid 307625/242020)")

add("irl-amazon-clonshaugh-buildings-uvwxy-p1186",
    "Amazon Clonshaugh Business & Technology Park data storage campus (Buildings W, X, Y; U and V under licence review)",
    "Amazon Data Services Ireland Ltd", "Amazon.com Inc. (AWS)", "Dublin", "Clonshaugh (Dublin 17)",
    ll("ITM", 718406, 740436), "operating", 288.29, "MWth rated thermal input, sum of units in review application LA011866 (40 x 5.44 + 10 x 6.49 + 2.19 + 3.6); original licence cap 190.40 MWth for 40 generators", 52,
    "evaporative", E+"090151b28087b810.pdf", "permit", "high",
    "IE licence P1186-01 granted 15 Jun 2023 (application LA009940, 7.9 ha, 40 x 5.44 MWth generators in Buildings W/X/Y); review P1186-02 (LA011866, received 31 Jul 2024; EPA RFI 22 Aug 2025) adds Building U (10 x 6.49 + 2.19 MWth) and Building V (3.6 MWth). Evaporative (adiabatic) cooling with mains water in hot periods, free cooling otherwise. Attachment 7.4.2 gives both ITM (718406/740436) and Irish Grid (318465/240412) for stack A3-1.",
    coord_src=E+"090151b28093e01c.pdf (attachment 7.4.2 LA011866, emission point A3-1 E718406 N740436, ITM)")

add("irl-amazon-clonshaugh-campus-p1171",
    "Amazon Clonshaugh Business & Technology Park data storage campus (planning 3634/15; 105-generator licence application)",
    "Amazon Data Services Ireland Ltd", "Amazon.com Inc. (AWS)", "Dublin", "Clonshaugh (Dublin 17)",
    ll("ITM", 718047, 741136), "operating", None, "per-unit ratings not given in attachment 7.4.2 except 2 x 2.19 MWth backup units; 105 generator stacks listed", 105,
    "unknown", E+"090151b28086263e.pdf", "permit", "low",
    "IE licence application P1171-01 (LA007495, received 21 Jan 2022; EPA RFI 3 Feb 2023 requesting EIAR non-technical summary and Dublin City Council permission 3634/15; register circulated to DCC 11 May 2023). Public notice gives Irish Grid E318313 N241343 and Eircode D17 V088; attachment 7.4.2 lists stacks A3-1..A3-105 (103 emergency + 2 x 2.19 MWth backup) at ITM 718047/741136, c. 700 m NW of the P1186 campus. Grant of the licence not confirmed in documents retrieved. Status 'operating' inferred from the licence being sought for an existing campus permitted under 3634/15; verify.",
    coord_src=E+"090151b2807ff5d3.pdf (attachment 7.4.2 LA007495, emission point A3-1 E718047 N741136, ITM)")

add("irl-amazon-drogheda-ida-park-dub62-p1181",
    "Amazon Drogheda IDA Business & Technology Park data storage campus (GHG 'DUB 62')",
    "Amazon Data Services Ireland Ltd", "Amazon.com Inc. (AWS)", "Meath", "Drogheda (Donore Road)",
    ll("IG", 306705, 274070), "operating", 358.17, "MWth rated thermal input, sum of units in review application LA015550 (26 x 6.82 + 1.55 + 26 x 6.79 + 2.02); Building A licence cap 165.87 MWth", 54,
    "evaporative", E+"090151b2808e9fce.pdf", "permit", "high",
    "IE licence P1181-01 granted 8 Aug 2024 for Building A (27 generators); review LA015550 (Sept 2025) adds Building B. GHG permit IE-GHG200-03 (26 Sep 2025) lists 60 stacks (~374 MW) and HVO as a new fuel. Eircode A92 VX98; cooling water to storm network -> River Boyne. Already in seed_sites_unlocated backlog as ie-epa-P1181-01.",
    coord_src=E+"090151b280816141.pdf (application form LA009977, site centre Irish Grid E306705 N274070)")

add("irl-amazon-leixlip-kic-b1-p1222",
    "Amazon Data Centre Building B1, Kildare Innovation Campus, Leixlip (GHG 'KIC 1')",
    "Amazon Data Services Ireland Ltd", "Amazon.com Inc. (AWS)", "Kildare", "Leixlip (Barnhall Road)",
    ll("IG", 298631, 235069), "under_construction", 111.44, "MW rated capacity per GHG permit IE-GHG628-01 (14 x 7.73 + 2.5 + 2 x 0.36)", 15,
    "unknown", E+"090151b280921b5c.pdf", "permit", "medium",
    "IE licence application P1222-01 (LA016198, received 26 Feb 2025; decision not retrieved). GHG permit IE-GHG628-01 issued 9 Sep 2025 with estimated start February 2026 (status as of the record: not yet operating; may be operating by Oct 2026). Eircode W23 X93P.",
    coord_src=E+"090151b280921b5c.pdf (application form LA016198, site centre Irish Grid E298631 N235069)")

# ---------------------------------------------------------------- GOOGLE / MICROSOFT / META (GHG permits)
add("irl-google-grange-castle-ghg170",
    "Google Ireland Data Center, Grange Castle Business Park South",
    "Google Ireland Ltd", "Alphabet Inc.", "Dublin", "Clondalkin (Baldonnell Road, Dublin 22)",
    ll("IG", 303402, 230546), "operating", None, "individual and total generator ratings confidential in GHG permit (listed as '<200 MW')", 24,
    "unknown", G+"IE-GHG170-10431-4.pdf", "permit", "high",
    "GHG permit IE-GHG170-10431-4 sealed 3 Jul 2019 (installation 205782; earlier name 'Google Profile Park'): 24 emergency generators + 2 fire pump engines, sulphur-free diesel, Eircode D22 X602, main entrance Irish Grid 303402/230546. Wikipedia 'Google data centers' table gives 53.3201083, -6.4420639 (c. 0.7 km NE of the permit's main-entrance point, inside the same campus) and launch year 2012. Replaces the Wikipedia-sourced row in seed_sites.json. Operator list datacenters.google/locations corroborates.",
    first_year=2012,
    coord_src=G+"IE-GHG170-10431-4.pdf (GHG permit, site main entrance Irish Grid 303402/230546)")

add("irl-microsoft-grange-castle-db3-5-ghg179",
    "Microsoft Dublin Data Centre Campus DB3/DB4/DB5, Grange Castle",
    "Microsoft Ireland Operations Ltd", "Microsoft Corp.", "Dublin", "Clondalkin (Grange Castle Business Park, Dublin 22)",
    ll("IG", 303235, 231447), "operating", 212.58, "MWth standby generation capacity per IE licence application non-technical summary LA010453 (38 x 5.46 + 3 x 1.7 MWth)", 41,
    "air", G+"IE-GHG179-10502-4.pdf", "permit", "high",
    "GHG permit IE-GHG179-10502-4 (25 Jun 2021) covers DB3-13 (139 emergency generators + 3 fire pumps campus-wide, listed '<900 MW'); grid reference for DB3/4/5 block E303235 N231447. IE licence application LA010453 (NTS Nov 2022/Mar 2023; P-number not retrieved): 41 generators, 212.58 MWth, free cooling via roof AHUs in dry mode ~95% of the year, infrequent evaporative use (~2,628 m3/yr).",
    coord_src=G+"IE-GHG179-10502-4.pdf (GHG permit grid reference for DB3/4/5, Irish Grid 303235/231447)")

add("irl-microsoft-grange-castle-dub06-13-ghg179",
    "Microsoft Dublin Data Centre Campus DUB06-DUB13, Grange Castle",
    "Microsoft Ireland Operations Ltd", "Microsoft Corp.", "Dublin", "Clondalkin (Grange Castle Business Park, Dublin 22)",
    ll("IG", 304001, 231524), "operating", 579.28, "MWth standby generation capacity per IE licence application non-technical summary LA010454 (95 generators 1.29-7.51 MWth + 2 x 0.5 MWth fire pumps)", 97,
    "air", G+"IE-GHG179-10502-4.pdf", "permit", "high",
    "GHG permit IE-GHG179-10502-4 grid reference for DUB06/7/8/9/10/11/12/13 block E304001 N231524 (campus address U74/Unit 75 Grangecastle Business Park, Nangor Road). IE licence application LA010454 (NTS Dec 2022/Mar 2023; P-number not retrieved): 97 combustion units, 579.28 MWth; free cooling dry mode ~95% of year. ABP PL06S.300305 (SD17A/0318): temporary 18 MW gas-powered generator compound for DUB08, appeal invalid 22 Nov 2017.",
    coord_src=G+"IE-GHG179-10502-4.pdf (GHG permit grid reference for DUB06-13, Irish Grid 304001/231524)")

add("irl-microsoft-grange-castle-dub14-15-p1187",
    "Microsoft DUB14/DUB15 data centres with standby gas generation plant, Grange Castle South",
    "Microsoft Ireland Operations Ltd", "Microsoft Corp.", "Dublin", "Clondalkin (Grange Castle South Business Park, Dublin 22)",
    None, "operating", 342.8, "MWth sum of units in licence application NTS LA010221 (22 gas generators x 7.6 MWth = 167.2; 20 diesel x 8.66 + 1 x 2.4 MWth); the ledger's arithmetic, not a figure in the document", 43,
    "air", "https://leap.epa.ie/docs/0c36fae7-a803-44cc-b035-5d0465cf3ba4.pdf", "permit", "medium",
    "IE licence P1187-01 (application LA010221, NTS Sept 2022/Mar 2023): 22-unit standby gas generation plant (A2-1..A2-22) plus 21 emergency diesel generators (A3-1..A3-21); free cooling ~95% of year, evaporative cooling with treated rainwater; no chillers. Annual Environmental Report 2024 (LEAP) reports total energy used 402,946.82 GJ = 111.93 GWh for the campus (mainly purchased electricity). Press (DCD, Jul 2023): 170 MW gas plant permitted; Microsoft states it is for backup only. Buildings 56,246 sq m approved 2021.",
    coord_reason="no grid reference in the licence NTS or the AER; address 'Unit 75, Grange Castle Business Park, Nangor Road'; adjacent to the DB3-5 block (E303235 N231447) but not located in a record")

add("irl-meta-clonee-ghg189",
    "Meta (Facebook) Clonee Data Center (CLN1-CLN3)",
    "Runways Information Services Ltd (Meta)", "Meta Platforms Inc.", "Meath", "Clonee (Sli na Chairde, Portan)",
    ll("IG", 304237, 241967), "operating", None, "generator ratings not stated in GHG permit (each '<500 MW')", 55,
    "unknown", G+"IE-GHG189-10513-1.pdf", "permit", "high",
    "GHG permit IE-GHG189-10513-1 issued 3 Sep 2018: 55 diesel emergency generators (CLN1 18, CLN2 18, CLN3 19), gas oil; Eircode D15 NN9V; main entrance Irish Grid 304237/241967.",
    coord_src=G+"IE-GHG189-10513-1.pdf (GHG permit, site main entrance Irish Grid 304237/241967)")

# ---------------------------------------------------------------- COLOCATION / OTHER (GHG permits, IE licences)
add("irl-digital-realty-dub14-profile-park-ghg190",
    "Digital Realty (Interxion) DUB14, Profile Park",
    "Digital Netherlands VIII B.V.", "Digital Realty Trust", "Dublin", "Clondalkin (Grange Castle, Nangor Road, Dublin 22)",
    ll("IG", 303909, 230335), "operating", None, "7 standby generators, each and total listed '<50 MW' (ratings confidential)", 7,
    "unknown", G+"IE-GHG190-10516-1.pdf", "permit", "high",
    "GHG permit IE-GHG190-10516-1 issued 7 Apr 2020; gas/diesel oil; main entrance Irish Grid 303909/230335.",
    coord_src=G+"IE-GHG190-10516-1.pdf (GHG permit, site main entrance Irish Grid 303909/230335)")

add("irl-k2-ballycoolin-campus-ghg202",
    "K2 Ballycoolin Dublin Campus",
    "K2 Strategic Infrastructure Ireland Ltd", "K2 Data Centres", "Dublin", "Blanchardstown (Ballycoolin Business Park, Dublin 15)",
    ll("ITM", 708793, 740973), "operating", 65.52, "MWth rated thermal input per GHG permit (8 x 8.19 MW)", 8,
    "unknown", G+"IE-GHG202-11124-1.pdf", "permit", "high",
    "GHG permit IE-GHG202-11124-1 issued 25 Jun 2021; 8 diesel generators; Eircode D15 Y3EC; site main entrance quoted as E708793 N740973 (ITM values).",
    coord_src=G+"IE-GHG202-11124-1.pdf (GHG permit, site main entrance E708793 N740973, ITM)")

add("irl-kdcr-dub2-ballycoolin-ghg196",
    "Keppel DC REIT (KDCR) Dublin 2 data centre, Ballycoolin",
    "KDCR (Ireland) 2 Ltd", "Keppel DC REIT", "Dublin", "Blanchardstown (Unit B10 Ballycoolin Business & Technology Park, Dublin 15)",
    ll("IG", 309010, 240730), "operating", None, "11 emergency generators, ratings confidential ('<50 MW' each)", 11,
    "unknown", G+"IE-GHG196-10523-2.pdf", "permit", "high",
    "GHG permit IE-GHG196-10523-2 issued 25 Jun 2021; gas oil; Eircode D15 YN9K; main entrance Irish Grid 309010/240730.",
    coord_src=G+"IE-GHG196-10523-2.pdf (GHG permit, site main entrance Irish Grid 309010/240730)")

add("irl-waspar-dub10-blanchardstown-corporate-park-ghg176",
    "Waspar Limited 'DUB10' data centre, Blanchardstown Corporate Park",
    "Waspar Ltd", None, "Dublin", "Blanchardstown (Unit 9 Blanchardstown Corporate Park, Dublin 15)",
    ll("IG", 308405, 241463), "operating", None, "5 standby generators + 2 gas boilers, each '<50 MW' (ratings not stated)", 5,
    "unknown", G+"IE-GHG176-10473-4.pdf", "permit", "medium",
    "GHG permit IE-GHG176-10473-4 (21 Apr 2021) describes a Category A combustion installation 'at a data centre'; parent company not identified in the record. Main entrance Irish Grid 308405/241463.",
    coord_src=G+"IE-GHG176-10473-4.pdf (GHG permit, site main entrance Irish Grid 308405/241463)")

add("irl-vodafone-cdc-clonshaugh-ghg181",
    "Vodafone CDC data centre, Clonshaugh Business Park",
    "Vodafone Group Services Ireland Ltd", "Vodafone Group plc", "Dublin", "Clonshaugh / Coolock (Dublin 17)",
    ll("IG", 317964, 240461), "operating", None, "9 emergency generator exhausts, ratings confidential ('<100 MW' each)", 9,
    "unknown", G+"IE-GHG181-10505-1.pdf", "permit", "high",
    "GHG permit IE-GHG181-10505-1 issued 4 Aug 2016; low-emissions installation (~300 tCO2/yr estimated); main entrance Irish Grid 317964/240461.",
    coord_src=G+"IE-GHG181-10505-1.pdf (GHG permit, site main entrance Irish Grid 317964/240461)")

add("irl-equinix-db5-blanchardstown-p1168",
    "Equinix DB5 (Equinix Hyperscale 1) with gas turbine power plant, Blanchardstown Industrial Park",
    "Equinix Hyperscale 1 (DB5) Ltd", "Equinix Inc.", "Dublin", "Blanchardstown (Snugborough Road, Dublin 15)",
    None, "operating", 167.8, "MWth, the ledger's sum of 9 dual-fuel turbine generators x 18.64 MWth (natural gas) per inspector's report; primary power plant, not standby", 9,
    "evaporative", E+"090151b280842cda.pdf", "permit", "medium",
    "IE licence P1168-01 inspector's report 30 Aug 2022 (application received 29 Nov 2021): 9 dual-fuel turbines, natural gas primary (gas oil for up to 4 turbines in first two years pending HP gas connection Q4 2023), ~112.2 million m3 gas/yr; closed-loop chilled water with 13 cooling towers and chillers (evaporative heat rejection). GHG permit IE-GHG600-01 exists (http-only link not retrievable). Status 'operating' assumed from licence stage and press; verify.",
    coord_reason="no grid reference in the inspector's report; GHG permit PDF (IE-GHG600-01, which would carry the main-entrance grid reference) is served over http only and could not be fetched")

add("irl-equinix-db3-northwest-business-park-ghg192",
    "Equinix DB3, Northwest Business Park", "Equinix (Ireland) Ltd", "Equinix Inc.", "Dublin",
    "Blanchardstown (Unit 2 Northwest Business Park, Dublin 15)",
    None, "operating", None, "4 standby generators + 5 diesel rotary UPS, each '<50 MW' (ratings not stated)", 9,
    "unknown", E+"090151b28092cb0f.pdf", "permit", "medium",
    "GHG permit IE-GHG192-03 issued 16 Apr 2025 (installation 210702).",
    coord_reason="GHG permit gives street address only; no grid reference in the retrieved version")

add("irl-equinix-db4-northwest-business-park-ghg630",
    "Equinix DB4, Northwest Business Park", "Equinix (Ireland) Ltd", "Equinix Inc.", "Dublin",
    "Blanchardstown (Unit 14 NW Business Park, Dublin 15, D15 E205)",
    None, "operating", 21.8, "MW capacity per GHG permit (4 x 5.45 MW)", 4,
    "unknown", E+"090151b2809694eb.pdf", "permit", "medium",
    "GHG permit IE-GHG630-01 issued 1 Dec 2025.",
    coord_reason="GHG permit gives street address and Eircode only")

add("irl-equinix-db1-citywest-ghg191",
    "Equinix DB1, Citywest Business Campus", "Equinix (DB1) Ltd", "Equinix Inc.", "Dublin",
    "Citywest (Units 4027/4029 Kingswood Road, Dublin 24, D24 E180)",
    None, "operating", 39.02, "MW total of 9 standby generators per GHG permit (3.02/4.82/4.28/5.68 MW units)", 9,
    "unknown", "https://leap.epa.ie/docs/4ae2a577-856c-4ee2-b680-d5c6c943c140.pdf", "permit", "medium",
    "GHG permit IE-GHG191-04 issued 11 Dec 2025 (installation 210704).",
    coord_reason="GHG permit gives street address and Eircode only")

add("irl-k2-dublin-21-citywest-ghg618",
    "K2 Dublin 21, Citywest Business Campus", "K2 Strategic Infrastructure Ireland Ltd", "K2 Data Centres", "Dublin",
    "Citywest (Unit 4070 Kingswood Road, Dublin 24, D24 X6FA)",
    None, "operating", 34.84, "MW total per GHG permit (4 x 8.71 MW)", 4,
    "unknown", E+"090151b2809269fd.pdf", "permit", "medium",
    "GHG permit IE-GHG618-01 issued 24 Mar 2025 (first permit; status assumed operating or commissioning).",
    coord_reason="GHG permit gives street address and Eircode only")

add("irl-kdcr-dub1-citywest-ghg195",
    "Keppel DC REIT (KDCR) Dublin 1 data centre, Citywest", "KDCR (Ireland) Ltd", "Keppel DC REIT", "Dublin",
    "Citywest (4033-4035 Citywest Avenue, Dublin 24, D24 CR70)",
    None, "operating", None, "8 emergency generators, each '<50 MW' (ratings not stated); two units removed Dec 2021", 8,
    "unknown", E+"090151b28090d932.pdf", "permit", "medium",
    "GHG permit IE-GHG195-02 issued 20 Dec 2024 (installation 214062).",
    coord_reason="GHG permit gives street address and Eircode only")

add("irl-echelon-dub10-energy-centre-crag-avenue-ghg617",
    "Echelon DUB10 data centre and Energy Centre, Crag Avenue, Clondalkin (ex-Crag Digital site)",
    "Echelon Clondalkin DC Services Ltd", "Echelon Data Centres", "Dublin", "Clondalkin (Crag Avenue, Clondalkin Industrial Estate, Dublin 22, D22 Y921)",
    None, "permitted", 490.2, "MW rated thermal input per GHG permit: 10 gas turbines (7 x 46.6 + 3 x 42.4 = 453.4 MW) + 6 black-start diesel generators x 5.9 MW + 2 fire pumps x 0.7 MW; primary on-site generation, not standby", 16,
    "unknown", E+"090151b2808f8296.pdf", "permit", "medium",
    "GHG permit IE-GHG617-01 issued 1 Oct 2024 (first permit) for 'DUB10 Energy Centre'. Planning: South Dublin SD18A/0068 (Crag Digital Ltd, data centre + CHP energy centre at 3-4 Crag Avenue; third-party appeal PL06S.303517 withdrawn 3 May 2019). Construction/operation status not established from records retrieved.",
    coord_reason="GHG permit gives street address and Eircode only; no planning file with coordinates retrieved")

add("irl-echelon-dphs-peamount-road-newcastle",
    "Echelon (Data and Power Hub Services Ltd) data centre campus and gas peaking plant, Peamount Road, Newcastle",
    "Data and Power Hub Services Ltd", "Echelon Data Centres", "Dublin", "Newcastle (Peamount Road, Co. Dublin)",
    None, "permitted", 116.0, "MW electrical output of the gas plant as reported in press (7 combustion engines); plus 36 standby generators (MW not reported)", 43,
    "unknown", "https://www.thejournal.ie/article.php?id=6825739", "press", "low",
    "The Journal (2025): EPA granted an industrial emissions licence in July 2025 for a 7-engine ~116 MW gas peaking plant and 36 standby generators at Peamount Road, Newcastle, c. 1 km from Grange Castle; Friends of the Irish Environment sought judicial review. The EPA licence number and document were not retrieved (search did not surface them). Press-sourced row: replace source_url with the EPA licence when found.",
    coord_reason="no public-record document retrieved for this site; only a press report naming Peamount Road, Newcastle",
    licence="press")

add("irl-edgeconnex-grange-castle-ballymakaily-ghg621",
    "EdgeConneX Dublin campus (EDCDUB / ESSDUB97), Ballymakaily, Newcastle Road, Lucan (west of Grange Castle)",
    "EdgeConneX Ireland Ltd", "EdgeConneX (EQT)", "Dublin", "Lucan (Newcastle Road R120, Ballymakaily, K78 P3K1)",
    None, "operating", 533.6, "MW rated capacity per GHG permit IE-GHG621-01: 20 gas plants x 10.275 MW (205.5) + 48 emergency diesel generators x 6.818 MW (327.3) + 2 fire pumps", 68,
    "unknown", E+"090151b280918191.pdf", "permit", "medium",
    "GHG permit IE-GHG621-01 (30 Jan 2025) 'ESSDUB97'; earlier campus permit IE-GHG186 'EDCDUB01 (Grangecastle)'. Planning (South Dublin): SD17A/0141 and SD17A/0392 (ABP-300752-18, 3 phases, 16 standby diesel + 12 temporary gas units), SD19A/0042 (ABP-305948-19, 22.1 ha, 4 data halls 6,950 sq m each, 32 standby generators, 19-unit temporary gas plant), SD21A/0042 (three gas-engine plants of 20/20/21 units), SD22A/0333 DUB06 refused by SDCC (ABP-317802-23, 24 standby generators; outcome not retrieved). The Journal (Nov 2024): 28 emergency generators keeping three data centres online, ~130,000 tCO2 since 2017.",
    coord_reason="records name the townlands (Ballymakaily, The Grange) and R120 but give no grid reference; the townlands.ie page for Ballymakaily was not retrieved before the fetch limit")

add("irl-vantage-dub11-dub12-profile-park-p1203",
    "Vantage Data Centers DUB11/DUB12 with Multi-Fuel Generation Plant, Profile Park",
    "Vantage Data Centers DUB11 Ltd", "Vantage Data Centers (DigitalBridge)", "Dublin", "Clondalkin (Profile Park, townlands of Ballybane and Kilbride, Dublin 22, D22 X7R0)",
    (53.319722, -6.446389), "under_construction", 488.4, "MW rated thermal input per GHG permit IE-GHG620-01: 35 emergency generators (33 x 6.2 + 2 x 3.4 = 211.4) + temporary generator farm 16 x 2.6 (41.6) + MFGP 11 dual-fuel engines x 21.4 (235.4)", 62,
    "air", "https://leap.epa.ie/docs/04b63ab2-52c2-4eb6-9e26-920cf1c8df6d.pdf", "permit", "low",
    "GHG permit IE-GHG620-01 issued 10 Mar 2026. IE licence application P1203-01 (26 Jul 2023; EPA memo 14 Apr 2025 that it could not be considered under Reg. 10(2)(b)(ii)); revised application with air quality assessment Aug 2025 (AWN 257501.0276AR01). Operations report Aug 2024: MFGP gas (GNI network) or HVO, HVO expected main fuel in year 1; free-cooling magnetic-bearing chillers; heat-pump heat recovery for offices. Planning SD21A/0241 (ABP 313787 first-party appeal withdrawn 4 Jul 2022). COORDINATE IS THE BALLYBANE TOWNLAND CENTRE (53 19 11 N, 6 26 47 W from townlands.ie, OpenStreetMap-derived, ODbL), precision c. +/-1 km, not the building.",
    coord_src="https://www.townlands.ie/dublin/uppercross/clondalkin/clondalkin-ed-1901/ballybane/ (townland centre; OpenStreetMap data, ODbL)")

add("irl-vantage-dub13-profile-park-abp317446-refused",
    "Vantage DUB13 data hall, Profile Park (refused by An Bord Pleanala)",
    "Vantage Data Centers DUB11 Ltd", "Vantage Data Centers (DigitalBridge)", "Dublin", "Clondalkin (Profile Park, townlands of Ballybane and Kilbride, Dublin 22)",
    (53.32, -6.42), "refused", None, "13 emergency back-up generators (12 double-stacked + 1), MW not stated", 13,
    "unknown", P+"anbordpleanala/media/abp/cases/orders/317/d317446.pdf", "register", "low",
    "ABP-317446-23 (SD22A/0420): two-storey data centre 'Building 13', 12,893 sq m, 13 generators with 22.3 m flues, 7 hot-air exhaust vents; SDCC refused 29 May 2023, Board refused 7 Apr 2025 (no grid connection agreement; on-site gas could become primary supply). Coordinate is the ledger entry's 2-decimal lat/lon (+/-0.5 km). Same campus as irl-vantage-dub11-dub12-profile-park-p1203.",
    ledger="ie-dublin-vantage-dub13-abp-refusal",
    coord_src="registry/europe.json (ledger entry ie-dublin-vantage-dub13-abp-refusal, 2-decimal lat/lon)")

add("irl-equinix-db8-profile-park-plot100-abp317936",
    "Equinix DB8, Plot 100 Profile Park (permitted; gas power compound modification under appeal)",
    "Equinix (Ireland) Ltd", "Equinix Inc.", "Dublin", "Clondalkin (Plot 100 Profile Park, Nangor Road, Dublin 22)",
    None, "permitted", None, "9 external generators proposed (up from 5); on-site gas power compound of 10 gas-fired generators; EIA screening cites 27.48 MW facility output and a 9 MW permanent grid supply request", 19,
    "unknown", P+"anbordpleanala/media/abp/cases/reports/317/r317936.pdf", "register", "medium",
    "ABP-317936-23 (SD22A/0156): modification of permitted DB8 (SD21A/0186), c. 9,795 sq m GFA, 2.65 ha; OSPG compound 2,604 sq m intended as interim power for 6-8 years until grid connection; SDCC refused 8 Aug 2023; inspector (site visit 3 Dec 2024) leaned to a conditional grant limiting OSPG to 8 years; Board decision not retrieved.",
    coord_reason="inspector's report gives plot number and road only; no coordinates; Profile Park townland not named in the retrieved text")

add("irl-sdr4-orion-business-campus-ballycoolin-la011399",
    "South Dublin Routing 4 No. 2 Ltd data centre and energy centre, Orion Business Campus, Ballycoolin",
    "South Dublin Routing 4 No. 2 Ltd", None, "Dublin", "Blanchardstown (Orion Business Campus, Northwest Business Park, Ballycoolin, Dublin 15, D15 XE2N)",
    None, "permitted", 194.76, "MWth, the ledger's sum of 9 permanent dual-fuel engines x 21.640 MWth on gas (23.018 MWth on HVO) per operational report; plus 1.15 MWth emergency generator, 0.81 MWth fire pump and temporary 4 x 5.955 MWth gas / 4 x 6.350 MWth HVO engines (49.22 MWth)", 9,
    "closed_loop", E+"090151b2808f5072.pdf", "permit", "medium",
    "IE licence application LA011399 (revised operational report Sept 2024): permanent gas/HVO engine plant as primary power; data halls on closed-loop chilled water with free-cooling chillers (30/70 glycol), free cooling >68% of year. Planning Fingal FW26A/0021E (contribution appeal PL06F.501133 decided 24 Jul 2026). Parent company not identified in the records.",
    coord_reason="operational report and ABP case page give address/Eircode only; no grid reference")

add("irl-servecentric-blanchardstown-corporate-park-2-fw22a0038",
    "Servecentric data centre (change of use of logistics unit), Plot 3 Blanchardstown Corporate Park 2",
    "Servecentric", None, "Dublin", "Blanchardstown (Old Corduff Road, Ballycoolin, Dublin 15)",
    None, "permitted", None, "not stated in ABP case record", None,
    "unknown", P+"ga-ie/case/318790", "register", "low",
    "Fingal FW22A/0038 permitted change of use from warehouse/logistics to data centre; amendment FW23A/0184 refused by Fingal, first-party appeal PL06F.318790 withdrawn 20 May 2025. Press (DCD) reports Servecentric appealing a Dublin denial. Construction status unknown.",
    coord_reason="ABP case page gives address only; no planning drawings retrieved")

add("irl-ogcio-backweston-celbridge-abp305962",
    "Office of the Government CIO data centre, Backweston Campus, Celbridge",
    "Office of the Government Chief Information Officer", "Government of Ireland", "Kildare", "Celbridge (Backweston Campus, Ballymadeer)",
    None, "permitted", None, "not stated in ABP case record", None,
    "unknown", P+"en-ie/case/305962", "register", "low",
    "Kildare CC 19164; first-party appeal PL09.305962 granted with conditions 11 Mar 2020 (data halls, plant rooms, external plant area). Construction/operation status not established.",
    coord_reason="ABP case page gives campus name only; inspector's report not retrieved")

add("irl-art-data-centres-ennis-tooreen-abp314474",
    "Art Data Centres campus with 120 MW gas energy centre, Tooreen, Tulla Road, Ennis",
    "Art Data Centres Ltd", None, "Clare", "Ennis (Tooreen and Cahernalough townlands, R352)",
    None, "permitted", 120.0, "MW on-site generation stated by applicant for the 18-engine gas energy centre (likely electrical); plus 66 standby generators (11 per building) with MW not stated", 84,
    "unknown", P+"anbordpleanala/media/abp/cases/reports/314/r314474.pdf", "register", "medium",
    "ABP-314474-22 (Clare CC 21/757): c. 60 ha; 6 data buildings c. 19,790 sq m each (118,740 sq m); energy centre 4,674 sq m with 18 lean-burn gas engines; 110 kV substation under SID ABP-313895-22; applicant states 200 MW total (83 MW grid + 120 MW on site); adiabatic cooling with rainwater and mains (appellant estimate 907 m3/day mains). Board granted (Clare CC notice 10 Apr 2024); judicial review dismissed; Irish Times 12 Oct 2026: Supreme Court refused leave to appeal. Outside the Dublin region.",
    coord_reason="inspector's report names townlands and the R352 but no grid reference; townland centroid not retrieved")

add("irl-red-admiral-dc-rochfortbridge-westmeath",
    "Red Admiral DC six-unit data centre campus and energy park, Castlelost/Rochfortbridge",
    "Red Admiral DC Ltd", "Lumcloon Energy Group", "Westmeath", "Rochfortbridge (Gneevebane, Oldtown, Farthingstown, Castlelost, Kiltotan, Collinstown townlands)",
    None, "permitted", None, "not reported", None,
    "unknown", "https://www.westmeathexaminer.ie/?p=128147", "press", "low",
    "Westmeath Examiner (2026): Westmeath CC granted 10-year permission in June 2026 with 32 conditions for a c. EUR 1bn six-unit campus with solar farm on c. 600 acres; third-party appeals to An Coimisiun Pleanala active, decision due 27 Oct 2026. Council reference and ABP case number not retrieved. Press-sourced row.",
    coord_reason="only a press report retrieved; no planning file",
    licence="press")

add("irl-edgeconnex-dub06-ballymakaily-abp317802",
    "EdgeConneX DUB06 (two adjoined data centres), Ballymakaily - refused by South Dublin CC, under appeal",
    "EdgeConneX Ireland Ltd", "EdgeConneX (EQT)", "Dublin", "Lucan (Ballymakaily townland, west of R120 Newcastle Road)",
    None, "refused", None, "24 standby diesel generators proposed, MW not stated", 24,
    "unknown", P+"anbordpleanala/media/abp/cases/reports/317/r317802.pdf", "register", "low",
    "ABP-317802-23 (SD22A/0333): 5.14 ha; 15,274 sq m GFA (12,859 sq m data halls), rooftop mechanical cooling units, 230 sq m PV; relies on gas-engine plants permitted under SD21A/0042; SDCC refused (grid capacity, no connection agreement, reliance on gas; green infrastructure). Inspector site visit 27 Sep 2024; Board decision not retrieved. Part of the campus in row irl-edgeconnex-grange-castle-ballymakaily-ghg621.",
    coord_reason="townland named but no grid reference; townland centroid not retrieved")

add("irl-parslickstown-mulhuddart-warehouse-data-centre-abp312424",
    "Light industrial warehouse/data centre, Parslickstown, Navan Road, Mulhuddart",
    "Colm Mac Daibheid (applicant)", None, "Dublin", "Mulhuddart (Parslickstown, Navan Road, Dublin 15)",
    None, "permitted", None, "not stated", None,
    "unknown", P+"en-ie/case/312424", "register", "low",
    "Fingal FW21A/0046; third-party appeal PL06F.312424 granted with revised conditions 5 Dec 2022; small warehouse-scale facility, no EIAR. Included because it is a planning record naming a data centre; likely well under 1 MW.",
    coord_reason="ABP case page gives address only")

# ---------------------------------------------------------------- write outputs
for r in rows:
    assert set(r) == set(COLS), set(r) ^ set(COLS)
ids = [r["site_id"] for r in rows]
assert len(ids) == len(set(ids))

import os as _os
_SITES = _os.environ.get("SITES_OUT") or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
json_path = _os.path.join(_SITES, "ireland_sites.json")
csv_path = _os.path.join(_SITES, "ireland_sites.csv")
with open(json_path, "w") as f:
    json.dump(rows, f, indent=1, ensure_ascii=False)
with open(csv_path, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    for r in rows:
        w.writerow({k: ("" if v is None else v) for k, v in r.items()})

n = len(rows); nc = sum(1 for r in rows if r["lat"] is not None)
print(f"rows={n} with_coords={nc}")
for r in rows:
    print(f'{r["site_id"]:70s} {r["lat"]!s:>10} {r["lon"]!s:>10} {r["status"]:18s} {r["generator_mw_permitted"]}')
