#!/usr/bin/env python3
"""Geocode permit street addresses -> geocoded.csv. Never invents a coordinate.

Input rows: va_permits.csv (facility_street/city/zip, state VA) and tx_permits.csv (street/city/zip,
state TX) from --out; only rows WITH a street address and WITHOUT coordinates are queried.

Geocoders, in order:
  1. Nominatim (OpenStreetMap), https://nominatim.openstreetmap.org/search, structured query
     (street/city/state/postalcode/countrycodes=us), format=jsonv2, addressdetails=1, limit=1.
     Usage policy: max 1 request/second, a real User-Agent, results cached (out/geocode_cache.json
     is reused on re-runs, so an interrupted run resumes). Accepted only when the hit is
     building/house/place-level (match_quality rooftop or interpolated); a road-level hit is kept
     as match_quality=street with confidence low; a locality/county-level hit is rejected (null).
  2. US Census Geocoder batch, POST https://geocoding.geo.census.gov/geocoder/locations/addressbatch
     (CSV id,street,city,state,zip; benchmark=Public_AR_Current), for everything Nominatim did not
     resolve. Match/Exact -> high, Match/Non_Exact -> medium, Tie/No_Match -> null with reason.
Fixture mode replays fixtures/geocode_responses.json (SYNTHETIC responses in the real response shapes).

Output columns: row_key (backlog_id), state, query_street, query_city, query_zip, lat, lon, geocoder,
match_quality, confidence, matched_address, reason.
"""

from __future__ import annotations

import csv
import io
import json
import sys
import time
from pathlib import Path
from typing import Any

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C  # noqa: E402

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
NOMINATIM = "https://nominatim.openstreetmap.org/search"
CENSUS_BATCH = "https://geocoding.geo.census.gov/geocoder/locations/addressbatch"
NOMINATIM_PAUSE = 1.1
STATE_BBOX = {"VA": (36.5, 39.5, -83.7, -75.2), "TX": (25.6, 36.7, -106.8, -93.3)}
ACCEPT_ROOFTOP = {"building", "house", "office", "industrial", "commercial", "amenity", "yes", "warehouse", "data_center", "telecom", "landuse", "man_made"}
REJECT_PLACE = {"city", "town", "village", "hamlet", "county", "state", "postcode", "suburb", "neighbourhood", "administrative", "locality", "quarter"}

COLUMNS = ["row_key", "state", "query_street", "query_city", "query_zip", "lat", "lon", "geocoder", "match_quality",
           "confidence", "matched_address", "reason"]


def in_state(lat: float, lon: float, state: str) -> bool:
    b = STATE_BBOX.get(state)
    return b is None or (b[0] <= lat <= b[1] and b[2] <= lon <= b[3])


def cache_key(q: dict[str, str]) -> str:
    return "|".join(q.get(k, "") or "" for k in ("street", "city", "state", "postalcode")).lower()


def classify_nominatim(hit: dict[str, Any]) -> tuple[str, str]:
    """(match_quality, confidence) for one Nominatim result."""
    at = (hit.get("addresstype") or hit.get("type") or "").lower()
    cls = (hit.get("class") or "").lower()
    addr = hit.get("address") or {}
    if at in REJECT_PLACE or cls == "boundary":
        return "locality_only", "none"
    if addr.get("house_number") or at in ACCEPT_ROOFTOP or cls in ("building", "office", "industrial"):
        return "rooftop", "high"
    if at in ("road", "street", "highway") or cls == "highway":
        return "street", "low"
    return "unknown_type", "low"


def nominatim(q: dict[str, str], session) -> list[dict[str, Any]]:
    params = {"format": "jsonv2", "addressdetails": 1, "limit": 1, "countrycodes": "us", **q}
    r = session.get(NOMINATIM, params=params, timeout=60)
    r.raise_for_status()
    return r.json()


def census_batch(rows: list[dict[str, str]], session) -> dict[str, dict[str, Any]]:
    """rows: id, street, city, state, zip. Returns id -> parsed result."""
    buf = io.StringIO()
    w = csv.writer(buf)
    for r in rows:
        w.writerow([r["id"], r["street"], r["city"], r["state"], r["zip"] or ""])
    files = {"addressFile": ("addresses.csv", buf.getvalue(), "text/csv")}
    r = session.post(CENSUS_BATCH, data={"benchmark": "Public_AR_Current"}, files=files, timeout=300)
    r.raise_for_status()
    return parse_census_batch(r.text)


def parse_census_batch(text: str) -> dict[str, dict[str, Any]]:
    out = {}
    for row in csv.reader(io.StringIO(text)):
        if not row:
            continue
        rid = row[0]
        rec = {"status": row[2] if len(row) > 2 else "", "match_type": row[3] if len(row) > 3 else "",
               "matched_address": row[4] if len(row) > 4 else "", "lat": None, "lon": None}
        if len(row) > 5 and row[5]:
            try:
                lon_s, lat_s = row[5].split(",")
                rec["lon"], rec["lat"] = float(lon_s), float(lat_s)
            except ValueError:
                pass
        out[rid] = rec
    return out


def collect_queries(out_dir: Path) -> list[dict[str, Any]]:
    qs = []
    va = out_dir / "va_permits.csv"
    if va.exists():
        df = pd.read_csv(va, dtype=str, keep_default_na=False)
        for _, r in df.iterrows():
            if r.get("facility_street"):
                qs.append({"row_key": r["backlog_id"], "state": "VA", "street": r["facility_street"],
                           "city": r.get("facility_city") or "", "postalcode": r.get("facility_zip") or ""})
    tx = out_dir / "tx_permits.csv"
    if tx.exists():
        df = pd.read_csv(tx, dtype=str, keep_default_na=False)
        for _, r in df.iterrows():
            if r.get("street") and not r.get("lat"):
                qs.append({"row_key": r["backlog_id"], "state": "TX", "street": r["street"].title(),
                           "city": r.get("city") or "", "postalcode": r.get("zip") or ""})
    return qs


def main() -> None:
    ap = C.base_parser(__doc__)
    ap.add_argument("--no-census", action="store_true", help="skip the Census batch fallback")
    args = ap.parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    queries = collect_queries(out_dir)
    C.log(f"{len(queries)} addresses to geocode")

    cache_path = out_dir / "geocode_cache.json"
    cache: dict[str, Any] = json.loads(cache_path.read_text()) if cache_path.exists() and not args.fixture else {}
    fixture_resp = json.loads((FIXTURES / "geocode_responses.json").read_text()) if args.fixture else None
    session = None
    if not args.fixture:
        import requests

        session = requests.Session()
        session.headers["User-Agent"] = C.USER_AGENT + " (contact: see README)"

    results: dict[str, dict[str, Any]] = {}
    pending_census = []
    for q in queries:
        key = cache_key({"street": q["street"], "city": q["city"], "state": q["state"], "postalcode": q["postalcode"]})
        rec = {"row_key": q["row_key"], "state": q["state"], "query_street": q["street"], "query_city": q["city"],
               "query_zip": q["postalcode"], "lat": None, "lon": None, "geocoder": None, "match_quality": None,
               "confidence": "none", "matched_address": None, "reason": None}
        hits = None
        if args.fixture:
            hits = fixture_resp["nominatim"].get(key, [])
        elif key in cache and "nominatim" in cache[key]:
            hits = cache[key]["nominatim"]
        else:
            try:
                hits = nominatim({"street": q["street"], "city": q["city"], "state": q["state"], "postalcode": q["postalcode"]}, session)
                if not hits and q["postalcode"]:  # retry without the zip (permits sometimes carry an old one)
                    time.sleep(NOMINATIM_PAUSE)
                    hits = nominatim({"street": q["street"], "city": q["city"], "state": q["state"]}, session)
            except Exception as exc:  # noqa: BLE001
                C.log(f"  nominatim error for {q['row_key']}: {exc}")
                hits = None
            cache.setdefault(key, {})["nominatim"] = hits
            cache_path.write_text(json.dumps(cache, indent=1))
            time.sleep(NOMINATIM_PAUSE)
        if hits:
            h = hits[0]
            mq, conf = classify_nominatim(h)
            lat, lon = float(h["lat"]), float(h["lon"])
            if mq != "locality_only" and in_state(lat, lon, q["state"]):
                rec.update({"lat": lat, "lon": lon, "geocoder": "nominatim", "match_quality": mq, "confidence": conf,
                            "matched_address": h.get("display_name")})
                if mq == "street":
                    rec["reason"] = "Nominatim matched the street only (no house number); coordinate is the road, not the building"
            else:
                rec["reason"] = "Nominatim returned only a locality-level or out-of-state hit; not used"
        elif hits is not None:
            rec["reason"] = "Nominatim: no result"
        else:
            rec["reason"] = "Nominatim: request failed"
        results[q["row_key"]] = rec
        if rec["lat"] is None or rec["match_quality"] == "street":
            pending_census.append({"id": q["row_key"], "street": q["street"], "city": q["city"], "state": q["state"], "zip": q["postalcode"]})

    if pending_census and not args.no_census:
        C.log(f"Census batch fallback for {len(pending_census)} addresses")
        if args.fixture:
            parsed = {k: v for k, v in fixture_resp["census_batch"].items() if k in {p["id"] for p in pending_census}}
        else:
            parsed = {}
            for i in range(0, len(pending_census), 1000):  # Census limit: 10,000 per batch; keep requests small
                try:
                    parsed.update(census_batch(pending_census[i:i + 1000], session))
                except Exception as exc:  # noqa: BLE001
                    C.log(f"  census batch error: {exc}")
        for p in pending_census:
            res = parsed.get(p["id"])
            rec = results[p["id"]]
            if not res:
                rec["reason"] = (rec["reason"] or "") + "; Census: no response row"
                continue
            if res["status"] == "Match" and res["lat"] is not None and in_state(res["lat"], res["lon"], p["state"]):
                conf = "high" if res["match_type"] == "Exact" else "medium"
                if rec["lat"] is None or rec["match_quality"] == "street":
                    rec.update({"lat": res["lat"], "lon": res["lon"], "geocoder": "census", "match_quality": f"census_{res['match_type'].lower()}",
                                "confidence": conf, "matched_address": res["matched_address"],
                                "reason": "Census street-interpolated match (TIGER); replaces Nominatim street-level hit" if rec["geocoder"] == "nominatim" else None})
            else:
                rec["reason"] = (rec["reason"] or "") + f"; Census: {res['status'] or 'no match'}{(' (' + res['match_type'] + ')') if res['match_type'] else ''}"
    df = pd.DataFrame([results[q["row_key"]] for q in queries], columns=COLUMNS)
    C.write_csv(df, out_dir / "geocoded.csv")
    summary = {
        **C.run_meta(args.fixture, [{"name": "Nominatim (OSM, ODbL)", "url": NOMINATIM}, {"name": "US Census Geocoder (public domain)", "url": CENSUS_BATCH}]),
        "addresses": len(df), "geocoded": int(df["lat"].notna().sum()),
        "by_geocoder": df["geocoder"].fillna("none").value_counts().to_dict(),
        "by_quality": df["match_quality"].fillna("none").value_counts().to_dict(),
    }
    C.write_json(summary, out_dir / "geocode_summary.json")
    C.log(f"wrote {out_dir / 'geocoded.csv'}: {summary['geocoded']}/{summary['addresses']} geocoded")


if __name__ == "__main__":
    C.run_main(main)
