"""Coordinates from two federal datasets, joined by the record's own identifier, for sites that have none yet.

Run it on a computer with internet access, from the repository's top folder:

    python3 pipeline/fetch_records.py

- EPA's National Emissions Inventory: the facility summary for each Virginia site the ledger knows by its EIS facility id
  (data.epa.gov), which gives the facility's latitude and longitude.
- The US Energy Information Administration's Form EIA-860 plant file (eia.gov), which gives each power plant's latitude
  and longitude: for the nuclear plants in the ledger, matched by the plant's name and state, exactly one row each.

It writes sites/locations/records.csv. A row is accepted only when the record was found by its identifier (EIS id) or by
exactly one plant with that name in that state. The build places accepted rows for sites that have no coordinates yet.
Only the standard library is used.
"""
import csv
import io
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "sites" / "locations" / "records.csv"
COLS = ["site_id", "lat", "lon", "accepted", "reason", "dataset", "record", "name_in_record", "source_url", "note", "fetched_on"]
NEI = {"usa-va-nei-15410111": "15410111", "usa-va-nei-17632111": "17632111", "usa-va-nei-21496711": "21496711", "usa-va-nei-21508611": "21508611",
       "usa-va-nei-21510611": "21510611", "usa-va-nei-21512611": "21512611", "usa-va-nei-21512711": "21512711", "usa-va-nei-6744011": "6744011"}
NEI_URL = "https://data.epa.gov/dmapservice/nei.vw_facility_summaries_{year}/eis_facility_id/equals/{eis}/pollutant_type/equals/CAP/1:200/CSV"
# site -> (names the plant file may use, state)
PLANTS = {"usa-nuclear-beaver-valley": (["beaver valley"], "PA"), "usa-nuclear-clinton": (["clinton power station", "clinton"], "IL"),
          "usa-nuclear-crane-clean-energy-center": (["three mile island", "crane clean energy center", "christopher m crane clean energy center"], "PA"),
          "usa-nuclear-davis-besse": (["davis besse"], "OH"), "usa-nuclear-duane-arnold": (["duane arnold energy center", "duane arnold"], "IA"),
          "usa-nuclear-perry": (["perry", "perry nuclear power plant"], "OH"), "usa-nuclear-susquehanna": (["susquehanna"], "PA"),
          "usa-nuclear-north-anna": (["north anna"], "VA")}
EIA_URLS = ["https://www.eia.gov/electricity/data/eia860/xls/eia8602025.zip", "https://www.eia.gov/electricity/data/eia860/xls/eia8602024.zip"]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compute-ledger records)"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def norm(s):
    return " ".join(re.findall(r"[a-z0-9]+", (s or "").lower()))


def nei_rows():
    out = []
    for sid, eis in NEI.items():
        row = {"site_id": sid, "accepted": "no", "dataset": "EPA National Emissions Inventory", "record": f"EIS facility id {eis}", "fetched_on": date.today().isoformat()}
        for year in (2023, 2020):
            url = NEI_URL.format(year=year, eis=eis)
            try:
                rows = list(csv.DictReader(io.StringIO(get(url).decode("utf-8-sig"))))
            except Exception as e:
                row["reason"] = f"could not fetch: {e}"
                continue
            rows = [r for r in rows if str(r.get("eis_facility_id", "")).strip() == eis] or rows
            if not rows:
                row["reason"] = f"no row in the {year} inventory"
                continue
            r = rows[0]
            lat = next((r[k] for k in r if k and k.lower().startswith("lat")), "")
            lon = next((r[k] for k in r if k and k.lower().startswith(("lon", "lng"))), "")
            name = next((r[k] for k in r if k and k.lower() in ("site_name", "facility_name", "company_name")), "")
            try:
                la, lo = float(lat), float(lon)
            except ValueError:
                row["reason"] = f"no coordinates in the {year} row"
                continue
            row |= {"lat": f"{la:.6f}", "lon": f"{lo:.6f}", "accepted": "yes", "reason": f"found by EIS facility id in the {year} inventory",
                    "name_in_record": name, "source_url": url,
                    "note": f"Placed at the coordinates EPA's {year} National Emissions Inventory gives for EIS facility {eis} ('{name}'), fetched {date.today().isoformat()}."}
            break
        out.append(row)
        print(sid, row["accepted"], row.get("reason", ""))
        time.sleep(0.5)
    return out


def xlsx_rows(data, want):
    """the rows of the first worksheet whose name contains `want`, as lists of strings (standard library only)"""
    z = zipfile.ZipFile(io.BytesIO(data))
    inner = next(n for n in z.namelist() if want.lower() in n.lower() and n.lower().endswith(".xlsx"))
    x = zipfile.ZipFile(io.BytesIO(z.read(inner)))
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    shared = []
    if "xl/sharedStrings.xml" in x.namelist():
        for si in ET.fromstring(x.read("xl/sharedStrings.xml")).findall("m:si", ns):
            shared.append("".join(t.text or "" for t in si.iter("{%s}t" % ns["m"])))
    sheet = sorted(n for n in x.namelist() if n.startswith("xl/worksheets/sheet"))[0]
    rows = []
    for row in ET.fromstring(x.read(sheet)).iter("{%s}row" % ns["m"]):
        cells = {}
        for c in row.findall("m:c", ns):
            col = re.match(r"[A-Z]+", c.get("r")).group(0)
            v = c.find("m:v", ns)
            t = c.get("t")
            if t == "s" and v is not None:
                val = shared[int(v.text)]
            elif t == "inlineStr":
                val = "".join(tt.text or "" for tt in c.iter("{%s}t" % ns["m"]))
            else:
                val = v.text if v is not None else ""
            cells[col] = val
        idx = lambda s: sum((ord(ch) - 64) * 26 ** i for i, ch in enumerate(reversed(s))) - 1  # noqa: E731
        n = max((idx(k) for k in cells), default=-1) + 1
        out = [""] * n
        for k, v in cells.items():
            out[idx(k)] = v
        rows.append(out)
    return inner, rows


def eia_rows():
    out = []
    data, url = None, ""
    for url in EIA_URLS:
        try:
            data = get(url)
            break
        except Exception as e:
            print("could not fetch", url, e)
    if data is None:
        return [{"site_id": s, "accepted": "no", "reason": "could not fetch the EIA-860 file", "dataset": "EIA-860", "fetched_on": date.today().isoformat()} for s in PLANTS]
    inner, rows = xlsx_rows(data, "Plant_Y")
    hi = next(i for i, r in enumerate(rows[:5]) if "Plant Code" in r)
    head = rows[hi]
    col = {k: head.index(k) for k in ("Plant Code", "Plant Name", "State", "Latitude", "Longitude")}
    body = [r + [""] * (len(head) - len(r)) for r in rows[hi + 1:]]
    for sid, (names, state) in PLANTS.items():
        hits = [r for r in body if r[col["State"]] == state and norm(r[col["Plant Name"]]) in names]
        row = {"site_id": sid, "accepted": "no", "dataset": "EIA-860", "source_url": url, "fetched_on": date.today().isoformat()}
        if len(hits) != 1:
            row["reason"] = f"{len(hits)} plants with that name in {state}"
        else:
            r = hits[0]
            try:
                la, lo = float(r[col["Latitude"]]), float(r[col["Longitude"]])
                row |= {"lat": f"{la:.6f}", "lon": f"{lo:.6f}", "accepted": "yes", "reason": "one plant with that name in that state",
                        "record": f"plant code {r[col['Plant Code']]}", "name_in_record": r[col["Plant Name"]],
                        "note": f"Placed at the coordinates the US Energy Information Administration's Form EIA-860 plant file ({inner}) gives for plant {r[col['Plant Code']]} ('{r[col['Plant Name']]}', {state}), fetched {date.today().isoformat()}."}
            except ValueError:
                row["reason"] = "no coordinates in the plant's row"
        out.append(row)
        print(sid, row["accepted"], row["reason"])
    return out


def main():
    rows = nei_rows() + eia_rows()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows([{c: r.get(c, "") for c in COLS} for r in rows])
    print(f"wrote {OUT.relative_to(ROOT)}: {len(rows)} rows, {sum(1 for r in rows if r['accepted'] == 'yes')} accepted")


if __name__ == "__main__":
    main()
