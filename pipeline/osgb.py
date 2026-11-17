"""Ordnance Survey grid references to latitude and longitude (WGS84), without outside libraries.

The steps are those of the Ordnance Survey's "A guide to coordinate systems in Great Britain":
grid letters and digits to easting and northing; the inverse Transverse Mercator projection on
the Airy 1830 ellipsoid (OSGB36); and a Helmert transformation from OSGB36 to WGS84, which is
good to about 5 metres. A grid reference given to fewer digits names a square, not a point: the
point returned is the square's south-west corner plus half its side, and `resolution_m` is the side.

    python3 pipeline/osgb.py "TQ 07304 80166"     # prints latitude, longitude and resolution
    python3 pipeline/osgb.py --test               # the Ordnance Survey's worked example
"""
import math
import re
import sys

AIRY = (6377563.396, 6356256.909)
WGS84 = (6378137.000, 6356752.3142)
F0, LAT0, LON0, N0, E0 = 0.9996012717, math.radians(49), math.radians(-2), -100000.0, 400000.0
# OSGB36 -> WGS84: translations in metres, scale in parts per million, rotations in arc seconds
HELMERT = {"tx": 446.448, "ty": -125.157, "tz": 542.060, "s": -20.4894, "rx": 0.1502, "ry": 0.2470, "rz": 0.8421}


def grid_to_en(ref):
    """'TQ 07304 80166' -> (507304.0 + half the resolution, 180166.0 + half, resolution in metres)."""
    s = re.sub(r"\s+", "", ref.upper())
    m = re.fullmatch(r"([A-HJ-Z])([A-HJ-Z])(\d*)", s)
    if not m or len(m.group(3)) % 2 or not 2 <= len(m.group(3)) <= 10:
        raise ValueError(f"not a grid reference: {ref!r}")
    l1, l2 = ord(m.group(1)) - 65, ord(m.group(2)) - 65
    l1 -= l1 > 7
    l2 -= l2 > 7
    e100 = ((l1 - 2) % 5) * 5 + (l2 % 5)
    n100 = (19 - (l1 // 5) * 5) - (l2 // 5)
    d = m.group(3)
    k = len(d) // 2
    res = 10 ** (5 - k)
    e = e100 * 100000 + int(d[:k]) * res
    n = n100 * 100000 + int(d[k:]) * res
    half = res / 2 if res > 1 else 0
    return e + half, n + half, res


def en_to_osgb36(E, N):
    a, b = AIRY
    e2 = 1 - (b * b) / (a * a)
    n = (a - b) / (a + b)
    lat, M = LAT0, 0.0
    while True:
        lat = (N - N0 - M) / (a * F0) + lat
        Ma = (1 + n + 5 / 4 * n ** 2 + 5 / 4 * n ** 3) * (lat - LAT0)
        Mb = (3 * n + 3 * n ** 2 + 21 / 8 * n ** 3) * math.sin(lat - LAT0) * math.cos(lat + LAT0)
        Mc = (15 / 8 * n ** 2 + 15 / 8 * n ** 3) * math.sin(2 * (lat - LAT0)) * math.cos(2 * (lat + LAT0))
        Md = 35 / 24 * n ** 3 * math.sin(3 * (lat - LAT0)) * math.cos(3 * (lat + LAT0))
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
    phi = lat - VII * dE ** 2 + VIII * dE ** 4 - IX * dE ** 6
    lam = LON0 + X * dE - XI * dE ** 3 + XII * dE ** 5 - XIIA * dE ** 7
    return phi, lam


def _to_cartesian(phi, lam, ell, h=0.0):
    a, b = ell
    e2 = 1 - (b * b) / (a * a)
    nu = a / math.sqrt(1 - e2 * math.sin(phi) ** 2)
    return ((nu + h) * math.cos(phi) * math.cos(lam), (nu + h) * math.cos(phi) * math.sin(lam), ((1 - e2) * nu + h) * math.sin(phi))


def _from_cartesian(x, y, z, ell):
    a, b = ell
    e2 = 1 - (b * b) / (a * a)
    p = math.hypot(x, y)
    phi = math.atan2(z, p * (1 - e2))
    for _ in range(10):
        nu = a / math.sqrt(1 - e2 * math.sin(phi) ** 2)
        phi = math.atan2(z + e2 * nu * math.sin(phi), p)
    return phi, math.atan2(y, x)


def osgb36_to_wgs84(phi, lam):
    x, y, z = _to_cartesian(phi, lam, AIRY)
    t = HELMERT
    s = t["s"] * 1e-6
    rx, ry, rz = (math.radians(t[k] / 3600) for k in ("rx", "ry", "rz"))
    x2 = t["tx"] + (1 + s) * x - rz * y + ry * z
    y2 = t["ty"] + rz * x + (1 + s) * y - rx * z
    z2 = t["tz"] - ry * x + rx * y + (1 + s) * z
    return _from_cartesian(x2, y2, z2, WGS84)


def en_to_wgs84(E, N):
    phi, lam = osgb36_to_wgs84(*en_to_osgb36(E, N))
    return round(math.degrees(phi), 6), round(math.degrees(lam), 6)


def grid_to_wgs84(ref):
    """'TQ 07304 80166' -> (lat, lon, resolution in metres)."""
    E, N, res = grid_to_en(ref)
    return (*en_to_wgs84(E, N), res)


def _test():
    # the Ordnance Survey's worked example (guide, annexe C): E 651409.903, N 313177.270 is OSGB36 52°39'27.2531"N 1°43'4.5177"E
    phi, lam = en_to_osgb36(651409.903, 313177.270)
    assert abs(math.degrees(phi) - (52 + 39 / 60 + 27.2531 / 3600)) < 1e-7, math.degrees(phi)
    assert abs(math.degrees(lam) - (1 + 43 / 60 + 4.5177 / 3600)) < 1e-7, math.degrees(lam)
    assert grid_to_en("TG 51409 13177")[:2] == (651409, 313177)
    assert grid_to_en("TQ277380") == (527750, 138050, 100)
    assert grid_to_en("NN 166 712")[:2] == (216650, 771250)
    # the Airy meridian at Greenwich, longitude 0 in OSGB36, lies about 102 m east of the WGS84 prime meridian: 5.3" W in WGS84
    phi, lam = osgb36_to_wgs84(math.radians(51.4778), 0.0)
    assert abs(math.degrees(lam) + 0.00147) < 0.0002, math.degrees(lam)
    print("ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--test"]:
        _test()
    else:
        print(*grid_to_wgs84(" ".join(sys.argv[1:])))
