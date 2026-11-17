"""Build sites/locations/address_queue.csv: the US sites without coordinates whose record gives a street address.

    python3 pipeline/address_queue.py

Sources, each the site's own record:
- the city and state energy-benchmarking filings (the address each filing prints; the city from the jurisdiction or, for New
  York City, from the property name where it gives one, since a New York street address alone can be in any borough);
- the Virginia air permits (the site address the permit's "located at" clause gives, as resolved in va_permits_resolved.csv);
- sites/locations/addresses_read.csv: street addresses read from a site's documents by two readers who agree.
A site already placed, or whose address has no house number, is left out. pipeline/geocode_addresses.py then asks the
US Census geocoder for each row.
"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "data" / "climate_trace_seed"
OUT = ROOT / "sites" / "locations" / "address_queue.csv"
COLS = ["site_id", "address_as_written", "street", "city", "state", "zip", "address_from"]
CITY = {"Philadelphia": ("Philadelphia", "PA"), "Seattle": ("Seattle", "WA"), "Chicago": ("Chicago", "IL"), "Portland OR": ("Portland", "OR"),
        "San Francisco": ("San Francisco", "CA"), "Washington DC": ("Washington", "DC"), "Cambridge MA": ("Cambridge", "MA"),
        "Kansas City, MO": ("Kansas City", "MO"), "Boston, MA": ("Boston", "MA")}
STATES = {"CA", "MA", "MD", "NY", "PA", "WA", "IL", "OR", "DC", "MO", "VA", "TX"}
# Virginia permits held back in the 2026-10-23 run (VIRGINIA.md): an address not confirmed in the permit text, a wide address
# range, a street name the geocoder altered, and a permit covering seven buildings on three streets
HELD_BACK = {"usa-va-deq-52173", "usa-va-deq-74306", "usa-va-deq-74269", "usa-va-deq-74080"}
HOUSE = re.compile(r"^\s*\d+(?:-\d+)?[A-Z]?\s+\S")


def split_address(text, default_city="", default_state=""):
    """'24 school st, Boston, MA 02108' -> street, city, state, zip"""
    parts = [p.strip() for p in text.split(",") if p.strip()]
    street, city, state, zp = parts[0] if parts else "", default_city, default_state, ""
    rest = parts[1:]
    if rest:
        m = re.search(r"\b([A-Z]{2})\b\s*(\d{5})?(?:-\d{4})?\s*$", rest[-1].upper())
        if m and m.group(1) in STATES:
            state, zp = m.group(1), m.group(2) or ""
            tail = rest[-1][:m.start()].strip()
            rest = rest[:-1] + ([tail] if tail else [])
        if rest:
            city = rest[-1]
    m = re.search(r"\b(\d{5})(?:-\d{4})?\s*$", text)
    if m and not zp:
        zp = m.group(1)
    return street, city.title() if city.isupper() or city.islower() else city, state, zp


def main():
    sites = {s["site_id"]: s for s in csv.DictReader(open(PKG / "site_register.csv", encoding="utf-8", newline=""))}
    rows, seen = [], set()

    def add(sid, written, street, city, state, zp, frm):
        if sid in seen or sid in HELD_BACK or sid not in sites or (sites[sid]["lat"] or "").strip() or not HOUSE.match(street or "") or not (city and state):
            return
        seen.add(sid)
        rows.append({"site_id": sid, "address_as_written": written, "street": street, "city": city, "state": state, "zip": zp, "address_from": frm})

    for s in sites.values():
        src = s["register_source"]
        if "benchmarking disclosure" not in src or s["country"] != "USA":
            continue
        j = s["admin_region"]
        addr = s["also_known_as"]
        frm = f"the {src}"
        if j == "New York City":
            m = re.search(r"/([A-Z .'-]+)/NY\b", s["name"]) or re.search(r",\s*(Manhattan|Brooklyn|Bronx|Queens|Staten Island|New York)\s*,\s*NY", s["name"], re.I)
            z = re.search(r"\bNY\s+(1\d{4})\b", s["name"])
            if not m:
                continue  # a New York street address without its borough or town is not unique
            city = m.group(1).strip().title()
            city = {"Manhattan": "New York"}.get(city, city)
            add(s["site_id"], addr, addr, city, "NY", z.group(1) if z else "", frm)
        elif j in CITY:
            st, c, stt, z = split_address(addr, *CITY[j])
            add(s["site_id"], addr, st, c, stt, z, frm)
        else:  # California statewide, Montgomery County MD: the address carries its city
            st, c, stt, z = split_address(addr, "", {"California (statewide)": "CA", "Montgomery County MD": "MD"}.get(j, ""))
            add(s["site_id"], addr, st, c, stt, z, frm)
    for r in csv.DictReader(open(PKG / "va_permits_resolved.csv", encoding="utf-8", newline="")):
        sid = "usa-va-deq-" + r["registration"]
        line = r["site_city_line"] or ""
        m = re.match(r"\s*([^,]+?),?\s+(?:VA|Virginia)\b\s*(\d{5})?", line)
        if r["site_street"] and m:
            add(sid, f"{r['site_street']}, {line}", r["site_street"], m.group(1).strip(), "VA", m.group(2) or "", "the site address in the Virginia DEQ air permit")
    extra = ROOT / "sites" / "locations" / "addresses_read.csv"
    if extra.exists():
        for r in csv.DictReader(open(extra, encoding="utf-8", newline="")):
            add(r["site_id"], r["address_as_written"], r["street"], r["city"], r["state"], r["zip"], r["address_from"])
    rows.sort(key=lambda r: r["site_id"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT.relative_to(ROOT)}: {len(rows)} addresses")


if __name__ == "__main__":
    main()
