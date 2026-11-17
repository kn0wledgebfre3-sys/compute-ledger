"""Coordinates as documents print them, to latitude and longitude (WGS84), without outside libraries.

Handles the forms the ledger's documents use:
- latitude and longitude, decimal or degrees, minutes and seconds (WGS84 or NAD83, which agree to about 1-2 m in North America);
- the British National Grid (see `osgb.py`);
- the Irish Grid (TM65 on the modified Airy ellipsoid; Helmert to WGS84, good to a few metres) and Irish Transverse Mercator
  (ITM, on ETRS89, which agrees with WGS84 to within a metre);
- UTM, by zone and hemisphere (WGS84 or NAD83).
The projection is the inverse Transverse Mercator of the Ordnance Survey's guide, with each system's published constants.

    python3 pipeline/coords.py --test
"""
import math
import re
import sys

import osgb

GRS80 = (6378137.0, 6356752.314140)
AIRY_MOD = (6377340.189, 6356034.447)
# (ellipsoid, scale on the central meridian, latitude and longitude of true origin, false easting, false northing)
SYSTEMS = {
    "itm": (GRS80, 0.99982, 53.5, -8.0, 600000.0, 750000.0),
    "irish_grid": (AIRY_MOD, 1.000035, 53.5, -8.0, 200000.0, 250000.0),
}
# Ireland 1965 (TM65) -> WGS84, position-vector convention: metres, parts per million, arc seconds
HELMERT_TM65 = {"tx": 482.530, "ty": -130.596, "tz": 564.557, "s": 8.150, "rx": -1.042, "ry": -0.214, "rz": -0.631}


def tm_inverse(E, N, ell, F0, lat0_deg, lon0_deg, E0, N0):
    """easting and northing on a Transverse Mercator projection -> latitude and longitude (radians) on its own ellipsoid"""
    a, b = ell
    lat0, lon0 = math.radians(lat0_deg), math.radians(lon0_deg)
    e2 = 1 - (b * b) / (a * a)
    n = (a - b) / (a + b)
    lat, M = lat0, 0.0
    while True:
        lat = (N - N0 - M) / (a * F0) + lat
        Ma = (1 + n + 5 / 4 * n ** 2 + 5 / 4 * n ** 3) * (lat - lat0)
        Mb = (3 * n + 3 * n ** 2 + 21 / 8 * n ** 3) * math.sin(lat - lat0) * math.cos(lat + lat0)
        Mc = (15 / 8 * n ** 2 + 15 / 8 * n ** 3) * math.sin(2 * (lat - lat0)) * math.cos(2 * (lat + lat0))
        Md = 35 / 24 * n ** 3 * math.sin(3 * (lat - lat0)) * math.cos(3 * (lat + lat0))
        M = b * F0 * (Ma - Mb + Mc - Md)
        if abs(N - N0 - M) < 0.00001:
            break
    sl, cl, tl = math.sin(lat), math.cos(lat), math.tan(lat)
    nu = a * F0 / math.sqrt(1 - e2 * sl * sl)
    rho = a * F0 * (1 - e2) / (1 - e2 * sl * sl) ** 1.5
    eta2 = nu / rho - 1
    VII = tl / (2 * rho * nu)
    VIII = tl / (24 * rho * nu ** 3) * (5 + 3 * tl ** 2 + eta2 - 9 * tl ** 2 * eta2)
    IX = tl / (720 * rho * nu ** 5) * (61 + 90 * tl ** 2 + 45 * tl ** 4)
    X = 1 / (cl * nu)
    XI = 1 / (cl * 6 * nu ** 3) * (nu / rho + 2 * tl ** 2)
    XII = 1 / (cl * 120 * nu ** 5) * (5 + 28 * tl ** 2 + 24 * tl ** 4)
    XIIA = 1 / (cl * 5040 * nu ** 7) * (61 + 662 * tl ** 2 + 1320 * tl ** 4 + 720 * tl ** 6)
    dE = E - E0
    return lat - VII * dE ** 2 + VIII * dE ** 4 - IX * dE ** 6, lon0 + X * dE - XI * dE ** 3 + XII * dE ** 5 - XIIA * dE ** 7


def helmert(phi, lam, ell, t):
    x, y, z = osgb._to_cartesian(phi, lam, ell)
    s = t["s"] * 1e-6
    rx, ry, rz = (math.radians(t[k] / 3600) for k in ("rx", "ry", "rz"))
    x2 = t["tx"] + (1 + s) * x - rz * y + ry * z
    y2 = t["ty"] + rz * x + (1 + s) * y - rx * z
    z2 = t["tz"] - ry * x + rx * y + (1 + s) * z
    return osgb._from_cartesian(x2, y2, z2, osgb.WGS84)


def _deg(phi, lam):
    return round(math.degrees(phi), 6), round(math.degrees(lam), 6)


def itm_to_wgs84(E, N):
    return _deg(*tm_inverse(E, N, *SYSTEMS["itm"]))


def irish_grid_to_wgs84(E, N):
    phi, lam = tm_inverse(E, N, *SYSTEMS["irish_grid"])
    return _deg(*helmert(phi, lam, AIRY_MOD, HELMERT_TM65))


def irish_grid_letter(ref):
    """'O 15918 34437' -> easting, northing (metres) on the Irish Grid; the letters skip I, in a 5 x 5 grid of 100 km squares"""
    s = re.sub(r"\s+", "", ref.upper())
    m = re.fullmatch(r"([A-HJ-Z])(\d+)", s)
    if not m or len(m.group(2)) % 2:
        raise ValueError(f"not an Irish grid reference: {ref!r}")
    i = ord(m.group(1)) - 65
    i -= i > 7
    e100, n100 = i % 5, 4 - i // 5
    d = m.group(2)
    k = len(d) // 2
    res = 10 ** (5 - k)
    half = res / 2 if res > 1 else 0
    return e100 * 100000 + int(d[:k]) * res + half, n100 * 100000 + int(d[k:]) * res + half, res


def utm_to_wgs84(zone, E, N, south=False):
    lon0 = zone * 6 - 183
    return _deg(*tm_inverse(E, N, osgb.WGS84, 0.9996, 0.0, lon0, 500000.0, 10000000.0 if south else 0.0))


def parse_latlon(text):
    """'29°28'25.6"N 98°40'15.4"W', 'N 29 28 25.6, W 98 40 15.4', '29.473781, -98.670945' -> (lat, lon) or None"""
    t = text.replace("\u2033", '"').replace("\u2032", "'").replace("\u2019", "'").replace("\u201d", '"').replace("\u00ba", "\u00b0").replace("''", '"')
    vals = []  # (value, hemisphere letter, label)
    pats = [
        r"(?<![A-Za-z])(?P<pre>[NSEW])?\s*(?<![\d.])(?P<d>\d{1,3}(?:\.\d+)?)\s*\u00b0\s*(?:(?P<m>\d{1,2}(?:\.\d+)?)\s*'\s*)?(?:(?P<s>\d{1,2}(?:\.\d+)?)\s*\"\s*)?(?P<post>[NSEW](?![\d.A-Za-z]))?",
        r"(?<![A-Za-z])(?P<pre>[NSEW])\s*(?P<d>\d{1,3})\s+(?P<m>\d{1,2})\s+(?P<s>\d{1,2}(?:\.\d+)?)(?P<post>)",
        r"(?<![A-Za-z])(?P<pre>[NSEW])?\s*(?<![\d.])(?P<d>-?\d{1,3}\.\d+)\s*\u00b0?\s*(?P<post>[NSEW](?![\d.A-Za-z]))?(?P<m>)(?P<s>)",
    ]
    for pat in pats:
        for m in re.finditer(pat, t):
            d = m.group("d")
            v = abs(float(d)) + (float(m.group("m")) / 60 if m.group("m") else 0) + (float(m.group("s")) / 3600 if m.group("s") else 0)
            hemi = ((m.group("pre") or "") + (m.group("post") or "")).upper()[:1]
            label = t[max(0, m.start() - 12):m.start()].lower()
            vals.append((-v if d.startswith("-") or hemi in ("S", "W") else v, hemi, "lon" if "lon" in label else "lat" if "lat" in label else ""))
        if len(vals) >= 2:
            break
        vals = []
    if len(vals) < 2:
        return None
    (a, ha, la), (b, hb, lb) = vals[0], vals[1]
    if ha in ("E", "W") or hb in ("N", "S") or la == "lon" or lb == "lat":
        a, b = b, a
    elif not -90 <= a <= 90 and -90 <= b <= 90:  # a map link that writes longitude first ("-101.5776,35.2843")
        a, b = b, a
    if not (-90 <= a <= 90 and -180 <= b <= 180):
        return None
    return round(a, 6), round(b, 6)


def _test():
    # the shared projection reproduces the Ordnance Survey's worked example
    phi, lam = tm_inverse(651409.903, 313177.270, osgb.AIRY, 0.9996012717, 49, -2, 400000, -100000)
    assert abs(math.degrees(phi) - (52 + 39 / 60 + 27.2531 / 3600)) < 1e-7 and abs(math.degrees(lam) - (1 + 43 / 60 + 4.5177 / 3600)) < 1e-7
    # each system's true origin returns its defined latitude and longitude
    assert itm_to_wgs84(600000, 750000) == (53.5, -8.0)
    phi, lam = tm_inverse(200000, 250000, *SYSTEMS["irish_grid"])
    assert abs(math.degrees(phi) - 53.5) < 1e-9 and abs(math.degrees(lam) + 8) < 1e-9
    assert utm_to_wgs84(14, 500000, 0) == (0.0, -99.0)
    # the Irish Grid's datum shift to WGS84 is tens of metres, not more
    lat, lon = irish_grid_to_wgs84(200000, 250000)
    assert abs(lat - 53.5) < 0.002 and abs(lon + 8) < 0.002, (lat, lon)
    # ITM was laid out so that ITM - Irish Grid is close to (+400 km, +500 km) across Ireland
    a, b = itm_to_wgs84(715830, 734697), irish_grid_to_wgs84(315904, 234671)
    assert abs(a[0] - b[0]) < 0.001 and abs(a[1] - b[1]) < 0.002, (a, b)
    assert irish_grid_letter("O 15918 34437")[:2] == (315918, 234437)
    assert parse_latlon("29°28'25.6\"N 98°40'15.4\"W") == (29.473778, -98.670944)
    assert parse_latlon("N 29 28 25.6, W 98 40 15.4") == (29.473778, -98.670944)
    assert parse_latlon("29.473781, -98.670945") == (29.473781, -98.670945)
    assert parse_latlon("Longitude -98.670945, Latitude 29.473781") == (29.473781, -98.670945)
    assert parse_latlon("-101.5776,35.2843") == (35.2843, -101.5776)
    print("ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--test"]:
        _test()
