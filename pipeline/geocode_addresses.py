"""Geocode the ledger's US site addresses with the US Census Bureau's geocoder, under the ledger's rule.

Run it on a computer with internet access, from the repository's top folder:

    python3 pipeline/geocode_addresses.py

It reads sites/locations/address_queue.csv (one row per site: the site's street address as its record prints it, split into
street, city, state and ZIP), asks the Census geocoder (https://geocoding.geo.census.gov, no key needed) for each address
once, and writes sites/locations/geocodes.csv. It can be stopped and run again: addresses already asked are skipped.

A point is accepted (accepted = yes) only when the geocoder matched the address itself: the same house number, inside the
range the geocoder holds for that street, the same street name, and the same ZIP where the queue gives one. Points from
several matches more than 250 m apart are not accepted. The Census points are interpolated along the street's address
range, not building points. The build places only accepted rows, and only for sites that have no coordinates yet.

Only the standard library is used. If the computer refuses the geocoder's certificate (some Python installs on macOS),
run the "Install Certificates" command that comes with that Python, then try again.
"""
import csv
import json
import math
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE = ROOT / "sites" / "locations" / "address_queue.csv"
OUT = ROOT / "sites" / "locations" / "geocodes.csv"
COLS = ["site_id", "address_as_written", "query", "matched_address", "lat", "lon", "n_matches", "house_number_ok", "street_ok", "zip_ok",
        "accepted", "reason", "address_from", "note", "queried_on"]
URL = "https://geocoding.geo.census.gov/geocoder/locations/address"
STREET_WORDS = {"st", "street", "ave", "avenue", "rd", "road", "dr", "drive", "blvd", "boulevard", "ln", "lane", "way", "ct", "court", "pkwy",
                "parkway", "pl", "place", "hwy", "highway", "cir", "circle", "ter", "terrace", "trl", "trail", "n", "s", "e", "w", "ne", "nw",
                "se", "sw", "north", "south", "east", "west", "the"}


def words(s):
    return {w for w in re.findall(r"[a-z0-9]+", (s or "").lower()) if w not in STREET_WORDS and not w.isdigit()}


def ask(row):
    q = {"street": row["street"], "city": row["city"], "state": row["state"], "zip": row["zip"], "benchmark": "Public_AR_Current", "format": "json"}
    q = {k: v for k, v in q.items() if v}
    url = URL + "?" + urllib.parse.urlencode(q)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "compute-ledger geocode"}), timeout=60) as r:
                return url, json.load(r)["result"]["addressMatches"]
        except Exception as e:  # network hiccup: wait and try again
            if attempt == 2:
                raise
            print("  retrying:", e)
            time.sleep(5)


def judge(row, matches):
    if not matches:
        return {"reason": "no match"}
    m = matches[0]
    lat, lon = m["coordinates"]["y"], m["coordinates"]["x"]
    far = [x for x in matches[1:] if math.hypot((x["coordinates"]["y"] - lat) * 111320, (x["coordinates"]["x"] - lon) * 111320 * math.cos(math.radians(lat))) > 250]
    num = re.match(r"\s*(\d+)", row["street"])
    comp = m.get("addressComponents", {})
    lo, hi = (comp.get("fromAddress") or ""), (comp.get("toAddress") or "")
    hn_ok = bool(num) and m["matchedAddress"].split(" ")[0] == num.group(1)
    if hn_ok and lo.isdigit() and hi.isdigit():
        hn_ok = min(int(lo), int(hi)) <= int(num.group(1)) <= max(int(lo), int(hi))
    st_ok = bool(words(comp.get("streetName")) & words(row["street"]))
    zip_ok = (not row["zip"]) or comp.get("zip", "")[:5] == row["zip"][:5]
    ok = hn_ok and st_ok and zip_ok and not far
    reason = "matched the house number, street" + (" and ZIP" if row["zip"] else "") if ok else "; ".join(
        x for x, bad in (("house number not matched", not hn_ok), ("another street", not st_ok), ("another ZIP", not zip_ok),
                         (f"{len(far) + 1} matches far apart", bool(far))) if bad)
    return {"matched_address": m["matchedAddress"], "lat": f"{lat:.6f}", "lon": f"{lon:.6f}", "n_matches": str(len(matches)),
            "house_number_ok": "yes" if hn_ok else "no", "street_ok": "yes" if st_ok else "no", "zip_ok": "yes" if zip_ok else "no",
            "accepted": "yes" if ok else "no", "reason": reason}


def main():
    queue = list(csv.DictReader(open(QUEUE, encoding="utf-8", newline="")))
    done = {}
    if OUT.exists():
        done = {r["site_id"]: r for r in csv.DictReader(open(OUT, encoding="utf-8", newline=""))}
    todo = [r for r in queue if r["site_id"] not in done]
    print(f"{len(queue)} addresses in the queue; {len(done)} already asked; asking {len(todo)}")
    rows = list(done.values())
    try:
        for i, r in enumerate(todo, 1):
            url, matches = ask(r)
            out = {c: "" for c in COLS} | {"site_id": r["site_id"], "address_as_written": r["address_as_written"], "query": url,
                                           "address_from": r["address_from"], "note": "", "queried_on": date.today().isoformat(), "accepted": "no"}
            out |= judge(r, matches)
            if out["accepted"] == "yes":
                out["note"] = (f"Placed on the address '{r['address_as_written']}' ({r['address_from']}), geocoded by the US Census Bureau "
                               f"to '{out['matched_address']}' on {out['queried_on']}; the point is interpolated along the street, not a building point.")
            rows.append(out)
            print(f"{i}/{len(todo)} {r['site_id']}: {out['accepted']} ({out['reason']})")
            time.sleep(0.4)
    finally:
        rows.sort(key=lambda x: x["site_id"])
        with open(OUT, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        n = sum(1 for x in rows if x["accepted"] == "yes")
        print(f"wrote {OUT.relative_to(ROOT)}: {len(rows)} asked, {n} accepted")


if __name__ == "__main__":
    sys.exit(main())
