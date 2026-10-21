"""Text extraction and regex field extraction shared by va_deq_permits.py and tx_permits.py.

Everything here works on plain text. Live runs get that text from pdfplumber (fallback
pypdf); fixture runs read the .txt files in fixtures/. The patterns were written against
the real permit texts transcribed on 2026-10-20 (see fixtures/provenance.json):

Virginia DEQ minor-NSR permits (deq.virginia.gov/home/showpublisheddocument/...):
  * Cover page: permittee name, mailing address, "Registration No.: 74129",
    "is authorized to construct and operate", "located at", facility street line(s),
    "Manassas, VA 20110", "(Prince William County)", "Approved on: February 21, 2018".
    The FIRST Virginia address on the cover is usually the permittee's MAILING address
    (e.g. Amazon: Herndon). The facility address follows "located at".
  * Equipment tables, columns: Ref. No(s). | Equipment Description | Rated Capacity
    (or "Standby Rated Capacity", "Maximum Rated Capacity", "Rated Capacity (Standby)") |
    Delegated Federal Requirements | Original Permit Date.  Row variants seen:
      "1 through 23 | Twenty three (23) Caterpillar model 3516C-HD emergency diesel engine gen-sets | 3,634 bhp 2,500 ekW (each unit)"
      "Gen21 – Gen52 | Thirty-two (32) MTU 20V4000G64S emergency diesel engine gen-sets | 3,672 bhp 2,500 ekW (each unit)"
      "66 through 101 | Caterpillar model C175-16 diesel engine driven emergency gen-sets (36 units) | 3,000 ekW 4,423 bhp (each unit)"
      "1 through 92 | (92) Cummins Model QSK60-G26 emergency diesel engine gen-sets | 3,626 bhp 2,500 ekW (each)"
      "EGU1 thru EGU3 | Three Caterpillar model 3516B diesel engine-driven emergency generators | 2848 brake horsepower or 2000 ekW, each"
      "Gen55 – Gen159 | (105) MTU Model 16V4000G84S and/or Caterpillar 3516C ... | 3,353 bhp/2,250 ekW 2,633 bhp/2,500 ekW (each)"
      "S1 | Caterpillar model C18 emergency diesel engine gen-set | 909 bhp 600 ekW"
    pdfplumber may emit one cell per line or one row per line, so matching is done on a
    whitespace-flattened copy with windows, never on strict row regexes.
  * Hours: "shall not operate more than 100 hours per year for maintenance checks and
    readiness testing", "no more than 500 hours per year for all purposes",
    "limited to 2279 hours per year" (older permits, combined).
  * Fuel: "ultra-low sulfur diesel fuel oil", "is diesel fuel", "15 ppm",
    "consume no more than 641,268 gallons of diesel fuel per year".

TCEQ Title V application packages (tceq.texas.gov/assets/public/permitting/air/reports/applications/<id>-ac|tc.pdf):
  * Core Data Form (TCEQ-10400): "27. Latitude (N) In Decimal: 29.480036 28. Longitude (W) In Decimal: -98.692555";
    "CN 603222902 RN 105295687"; "23. Street Address of / the Regulated Entity: / (No PO Boxes)" then value line;
    "City San Antonio State TX ZIP 78251"; "24. County Bexar"; "31. Primary NAICS Code".
  * STEERS site block: "What is the Regulated Entity's Number (RN)? RN111028916";
    "Number and Street 300 HOUSTON SCHOOL RD"; "City RED OAK" / "State TX" / "ZIP 75154" / "County ELLIS";
    "Latitude (N) (##.######) 32.537981"; "Longitude (W) (-###.######) -96.804371"; "Primary NAICS Code 518210".
  * OP-1 Section X: 'G. Latitude (nearest second): 32° 32\' 10.15" N'.
  * TCEQ letters: map link "marker=-100.056272,34.383232" (lon,lat).
  * OP-SUM unit rows (run together in text): "2.5MW1-1 OP-UA2 SN1-1/ 3516C 2500KW GENERATOR-ENGINE ..." or
    "EMGEN1 OP-UA2 Emergency Generator 1 Group ENG1a ..." (no kW) or "GRP-1 OP-UA2 Engine Group 1 ..." (groups, no count).
  * Some packages (e.g. 40584-ac.pdf) extract as garbled glyph codes: detected by text_quality().
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

# --------------------------------------------------------------------------------------
# PDF -> text
# --------------------------------------------------------------------------------------


def pdf_to_text(path: Path, max_pages: int | None = None) -> str:
    """Extract text page by page. pdfplumber first (keeps table rows together better),
    pypdf as a fallback. Pages are separated by form feeds so page numbers can be recovered."""
    path = Path(path)
    try:
        import pdfplumber

        pages = []
        with pdfplumber.open(str(path)) as pdf:
            for i, page in enumerate(pdf.pages):
                if max_pages and i >= max_pages:
                    break
                pages.append(page.extract_text() or "")
        return "\f".join(pages)
    except ImportError:
        pass
    from pypdf import PdfReader  # type: ignore

    reader = PdfReader(str(path))
    pages = []
    for i, page in enumerate(reader.pages):
        if max_pages and i >= max_pages:
            break
        pages.append(page.extract_text() or "")
    return "\f".join(pages)


COMMON_WORDS = {
    "the", "of", "and", "to", "in", "for", "permit", "emergency", "generator", "generators", "engine", "site", "county",
    "name", "number", "date", "application", "form", "texas", "commission", "unit", "diesel", "fuel", "hours", "per",
    "year", "city", "state", "zip", "street", "address", "latitude", "longitude", "virginia", "department", "quality",
    "environmental", "registration", "equipment", "capacity", "shall", "operate", "this", "with", "by", "is", "or",
}


def text_quality(text: str) -> str:
    """'ok' | 'garbled' | 'empty'. Garbled = the font-encoding failure seen on TCEQ 40584-ac.pdf,
    where words come out as glyph codes like './012213424567891567:12.213'. Decided by whether
    ordinary English/permit words occur at all (tables full of unit ids are still 'ok')."""
    if not text or len(text.strip()) < 200:
        return "empty"
    words = set(w.lower() for w in re.findall(r"[A-Za-z]{2,}", text[:60000]))
    return "ok" if len(words & COMMON_WORDS) >= 8 else "garbled"


def flatten(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\f", "\n"))


# --------------------------------------------------------------------------------------
# Numbers
# --------------------------------------------------------------------------------------

_ONES = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
}
_TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
WORD_NUM_RE = re.compile(
    r"\b((?:one|two|three|four|five|six|seven|eight|nine)\s+hundred(?:\s+(?:and\s+)?)?)?"
    r"((?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)(?:[\s-]+(?:one|two|three|four|five|six|seven|eight|nine))?"
    r"|(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen))\b",
    re.IGNORECASE,
)


def words_to_int(s: str) -> int | None:
    m = WORD_NUM_RE.search(s or "")
    if not m:
        return None
    total = 0
    if m.group(1):
        total += _ONES[m.group(1).split()[0].lower()] * 100
    rest = re.split(r"[\s-]+", m.group(2).lower())
    for w in rest:
        if w in _TENS:
            total += _TENS[w]
        elif w in _ONES:
            total += _ONES[w]
    return total or None


def num(s: str | None) -> float | None:
    if s is None:
        return None
    try:
        return float(str(s).replace(",", ""))
    except ValueError:
        return None


# --------------------------------------------------------------------------------------
# Reference-number ranges -> unit counts  ("1 through 23", "Gen21 – Gen52", "EGU1 thru EGU3",
# "3, 4, 17 through 20, 34 through 36", "91 and 92", "S1", "T-1 and T-2", "EG2-1 through EG2-26")
# --------------------------------------------------------------------------------------

REF_TOKEN = r"[A-Za-z]{0,4}-?(?:\d+-)?\d+[A-Za-z]{0,2}"
_RANGE_RE = re.compile(
    rf"([A-Za-z]{{0,4}}-?(?:\d+-)?)(\d+)([A-Za-z]{{0,2}})\s*(?:through|thru|to|–|—|\s-\s)\s*([A-Za-z]{{0,4}}-?(?:\d+-)?)(\d+)([A-Za-z]{{0,2}})",
    re.IGNORECASE,
)
_HYPHEN_RANGE_RE = re.compile(r"^(\d+)-(\d+)$")  # "1-3" (letter-prefixed "EG2-26" is a single unit id)
_SINGLE_RE = re.compile(rf"(?<![A-Za-z0-9.]){REF_TOKEN}(?![A-Za-z0-9.,]\d)")
# The refs cell is the last run of ref tokens (joined by , ; and &) right before the description
REFS_RUN_RE = re.compile(
    rf"((?:{REF_TOKEN}(?:\s*(?:through|thru|to|–|—|\s-\s)\s*{REF_TOKEN})?)"
    rf"(?:\s*(?:,|;|\band\b|&)\s*(?:{REF_TOKEN}(?:\s*(?:through|thru|to|–|—|\s-\s)\s*{REF_TOKEN})?))*)\s*$",
    re.IGNORECASE,
)


def count_from_refs(refs: str) -> int | None:
    """Number of units implied by a 'Ref. Nos.' cell. None when nothing parseable."""
    if not refs:
        return None
    s = refs.replace("–", "-").replace("—", "-")
    s = re.sub(r"\bRef(?:erence)?\.?\s*Nos?\.?:?", " ", s, flags=re.IGNORECASE)
    total = 0
    parts = re.split(r"\s*(?:,|;|\band\b|&)\s*", s)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        m = _RANGE_RE.search(part)
        if m:
            a, b = int(m.group(2)), int(m.group(5))
            if b >= a and (b - a) < 2000:
                total += b - a + 1
                continue
        m = _HYPHEN_RANGE_RE.match(part)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if b >= a and (b - a) < 2000:
                total += b - a + 1
                continue
        if _SINGLE_RE.search(part):
            total += 1
    return total or None


# --------------------------------------------------------------------------------------
# Generator rows (Virginia style tables; also catches 'N x kW' prose)
# --------------------------------------------------------------------------------------

MAKERS = (
    r"Caterpillar|CAT\b|Cummins|MTU|Rolls[- ]Royce|Kohler|Generac|Detroit Diesel|Perkins|Volvo Penta|"
    r"John Deere|Mitsubishi|Hitzinger|Baudouin|Daimler|Wartsila|W[aä]rtsil[aä]|Jenbacher|Waukesha|Doosan|Scania"
)
MAKER_RE = re.compile(rf"({MAKERS})\s*(?:[Mm]odel\s+)?([A-Z0-9][A-Za-z0-9\-/]+)?")
GEN_KEYWORD_RE = re.compile(r"gen-?sets?|generator|engine", re.IGNORECASE)
EXCLUDE_KEYWORD_RE = re.compile(r"fire\s*pump|boiler|heater|chiller|cooling tower|storage tank", re.IGNORECASE)

# "3,634 bhp 2,500 ekW", "4,423 bhp; 3,000 ekW", "2848 brake horsepower or 2000 ekW", "3,353 bhp/2,250 ekW"
RATING_BHP_KW_RE = re.compile(
    r"(?P<bhp>\d{1,3}(?:,\d{3})+|\d{3,5})\s*(?:bhp|BHP|hp|HP|brake\s*horsepower)\s*(?:,|;|/|or|and|-|–)?\s*"
    r"(?P<kw>\d{1,3}(?:,\d{3})+|\d{2,5}(?:\.\d+)?)\s*(?P<unit>ekW|kWe|kW|KW|MWe|MW)(?![Hh])"
)
# "3,000 ekW 4,423 bhp", "1,500 ekW 2,220 bhp"
RATING_KW_BHP_RE = re.compile(
    r"(?P<kw>\d{1,3}(?:,\d{3})+|\d{2,5}(?:\.\d+)?)\s*(?P<unit>ekW|kWe|kW|KW|MWe|MW)(?![Hh])\s*(?:,|;|/|or|and|-|–)?\s*"
    r"(?P<bhp>\d{1,3}(?:,\d{3})+|\d{3,5})\s*(?:bhp|BHP|hp|HP|brake\s*horsepower)"
)
# bare "2,500 ekW" / "2500KW" / "2.5 MW"
RATING_KW_ONLY_RE = re.compile(
    r"(?P<kw>\d{1,3}(?:,\d{3})+|\d{2,5}(?:\.\d+)?|\d\.\d+)\s*(?P<unit>ekW|kWe|kW|KW|MWe|MW)(?![Hh/])"
)
EACH_RE = re.compile(r"\(each(?: unit| engine| gen-?set)?\)|,\s*each\b|\beach\b", re.IGNORECASE)
COUNT_PAREN_RE = re.compile(r"\((\d{1,4})\s*(?:units?|engines?|gen-?sets?)?\)")
COUNT_UNITS_RE = re.compile(r"\b(\d{1,4})\s+(?:units|engines|gen-?sets|generators)\b", re.IGNORECASE)
COUNT_LEADING_RE = re.compile(r"^\s*(\d{1,4})\s+(?:emergency|diesel|standby|natural|gen-?sets|generators|engines)\b", re.IGNORECASE)
HEADER_JUNK_RE = re.compile(
    r"Registration\s+(?:No\.?|Number)\s*:?\s*\d+|\bPage\s+\d+(?:\s+of\s+\d+)?|\(?Last\s+amended[^)]*\)?|\b\d{5}(?:-\d{4})?\b(?=\s|$)|"
    r"\bPermit\s+No\.?\s*[A-Z0-9\-]+|\bN/?A\b",
    re.IGNORECASE,
)
DATE_RE = re.compile(
    r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s*\d{4}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b"
)
TRAILING_CELL_JUNK_RE = re.compile(
    r"\bNone\b|\bN/?A\b|NSPS[^|]*|\bSubpart\s+\w+|40\s*CFR[^|]*|\bamended\b|\(?Original Permit Date:?\)?|Modified Permit Date:?|"
    r"\b(?:Transitory )?Equipment (?:to be Constructed|Previously Permitted|Not Previously Permitted|Previously Constructed|Exempt from Permitting)"
    r"(?:\s+at\s+[A-Z0-9][A-Z0-9\-]*(?:,\s*[A-Z0-9][A-Z0-9\-]*)*(?:,?\s+and\s+[A-Z0-9][A-Z0-9\-]*)?)?:?|\bPreviously Permitted Equipment:?|"
    r"\bat (?:IAD|MCC|DC|Building)[-\s]?\w+:?|Ref(?:erence)?\.?\s*Nos?\.?\(?s?\)?\.?|Equipment Description|\(each[^)]*\)|"
    r"(?:Standby |Maximum )?Rated Capacity(?: \(Standby\))?|Delegated Federal Requirements|Original Permit Date|Federal Requirements",
    re.IGNORECASE,
)


@dataclass
class GenRow:
    refs: str | None
    count: int | None
    count_source: str  # explicit_paren|explicit_units|spelled|refs|single|none
    count_confidence: str  # high|medium|low|none
    kw_each: float | None
    kw_min: float | None
    kw_max: float | None
    bhp_each: float | None
    maker: str | None
    model: str | None
    each_flag: bool
    description: str
    snippet: str

    def total_kw(self) -> float | None:
        if self.count is None or self.kw_each is None:
            return None
        return self.count * self.kw_each


def _to_kw(value: float, unit: str) -> float:
    return value * 1000.0 if unit.upper().startswith("MW") else value


def find_generator_rows(text: str) -> list[GenRow]:
    """Find every per-unit generator rating in the text and the unit count that goes with it."""
    flat = flatten(text)
    hits: list[dict[str, Any]] = []
    for rx, kind in ((RATING_BHP_KW_RE, "bhp_kw"), (RATING_KW_BHP_RE, "kw_bhp"), (RATING_KW_ONLY_RE, "kw_only")):
        for m in rx.finditer(flat):
            hits.append({"start": m.start(), "end": m.end(), "kind": kind, "m": m})
    # keep the most specific hit per text span
    hits.sort(key=lambda h: (h["start"], -(h["end"] - h["start"])))
    kept: list[dict[str, Any]] = []
    for h in hits:
        if kept and h["start"] < kept[-1]["end"]:
            continue
        kept.append(h)

    rows: list[GenRow] = []
    prev_end = 0
    for h in kept:
        m = h["m"]
        kw = _to_kw(num(m.group("kw")), m.group("unit"))
        bhp = num(m.group("bhp")) if "bhp" in m.groupdict() and m.group("bhp") else None
        win_start = max(prev_end, h["start"] - 400)
        window = flat[win_start:h["start"]]
        after = flat[h["end"]:h["end"] + 40]
        each = bool(EACH_RE.search(after)) or bool(re.search(r"\beach\b", window[-20:], re.IGNORECASE))

        # A second rating immediately after a row with no description in between is an
        # alternative rating for the same row ("3,353 bhp/2,250 ekW 2,633 bhp/2,500 ekW (each)").
        if rows and not GEN_KEYWORD_RE.search(window) and len(window.strip()) < 25:
            r = rows[-1]
            r.kw_min = min(r.kw_min or kw, kw)
            r.kw_max = max(r.kw_max or kw, kw)
            r.kw_each = None  # ambiguous: either/or models
            r.each_flag = r.each_flag or each
            prev_end = h["end"]
            continue

        if not GEN_KEYWORD_RE.search(window):
            prev_end = h["end"]
            continue

        # Row start = the LATEST plausible description start in the window (earlier matches belong
        # to cover-letter prose or table titles): "(n)", "Twenty three (23) Caterpillar", "26 emergency",
        # a maker name, or "emergency/diesel/standby".
        starts = []
        for rx in (
            re.compile(r"\((\d{1,4})\)"),
            re.compile(r"\b(?:" + "|".join(list(_ONES)[1:] + list(_TENS)) + r")\b[\w\s-]{0,20}?\(?\d*\)?\s*(?:" + MAKERS + ")", re.IGNORECASE),
            re.compile(r"\b(\d{1,4})\s+(?:emergency|diesel|standby|natural|gen-?sets|generators|engines)\b", re.IGNORECASE),
            MAKER_RE,
            re.compile(r"\b(?:emergency|diesel|standby)\b", re.IGNORECASE),
        ):
            last = None
            for mm in rx.finditer(window):
                last = mm.start()
            if last is not None:
                starts.append(last)
        desc_start = min(starts) if starts else max(0, len(window) - 120)
        description = window[desc_start:].strip()
        if EXCLUDE_KEYWORD_RE.search(description):
            prev_end = h["end"]
            continue
        refs_raw = window[:desc_start]
        # strip trailing cells of the previous row, page headers and table headings
        refs_clean = DATE_RE.sub(" ", refs_raw)
        refs_clean = HEADER_JUNK_RE.sub(" ", refs_clean)
        refs_clean = TRAILING_CELL_JUNK_RE.sub(" ", refs_clean)
        refs_clean = re.sub(r"\b\d{1,3}(?:,\d{3})+\s*(?:bhp|ekW|kW|gallon)s?\b.*?(?=\s)", " ", refs_clean)
        refs_clean = re.sub(r"[|:]", " ", refs_clean)
        refs_clean = re.sub(r"\s+", " ", refs_clean).strip(" .,;")
        rm = REFS_RUN_RE.search(refs_clean)
        refs = rm.group(1).strip(" ,;") if rm else None

        count = None
        source = "none"
        cp = COUNT_PAREN_RE.search(description)
        cu = COUNT_UNITS_RE.search(description)
        cl = COUNT_LEADING_RE.search(description)
        spelled = words_to_int(description[:60])
        refcount = count_from_refs(refs) if refs else None
        if cp:
            count, source = int(cp.group(1)), "explicit_paren"
        elif cu:
            count, source = int(cu.group(1)), "explicit_units"
        elif cl and re.search(r"gen-?sets\b|generators\b|engines\b", description, re.IGNORECASE):
            count, source = int(cl.group(1)), "explicit_leading"
        elif spelled:
            count, source = spelled, "spelled"
        elif refcount:
            count, source = refcount, "refs"
        elif re.match(r"^(?:One|A|An)\b|^(?:" + MAKERS + ")", description, re.IGNORECASE):
            count, source = 1, "single"

        singular = bool(re.search(r"gen-?set\b|generator\b|engine\b", description, re.IGNORECASE)) and not re.search(
            r"gen-?sets\b|generators\b|engines\b", description, re.IGNORECASE)
        if count is not None and refcount is not None and source != "refs":
            conf = "high" if count == refcount else "low"
        elif count is not None and source in ("explicit_paren", "explicit_units", "explicit_leading", "spelled"):
            conf = "medium"
        elif count == 1 and singular:
            conf = "high" if refs else "medium"
        elif count is not None:
            conf = "medium" if source == "refs" and refs and re.search(r"through|thru|–|-", refs) else "low"
        else:
            conf = "none"
        if count is not None and count > 1 and not each:
            conf = "low" if conf != "none" else conf

        mk = MAKER_RE.search(description)
        rows.append(
            GenRow(
                refs=refs or None,
                count=count,
                count_source=source,
                count_confidence=conf,
                kw_each=kw,
                kw_min=kw,
                kw_max=kw,
                bhp_each=bhp,
                maker=mk.group(1) if mk else None,
                model=(mk.group(2) if mk and mk.group(2) else None),
                each_flag=each,
                description=description[:200],
                snippet=flat[max(0, h["start"] - 160):h["end"] + 30],
            )
        )
        prev_end = h["end"]

    # de-duplicate: identical refs+rating+count (same row quoted twice, e.g. page-break repeats)
    seen = set()
    out = []
    for r in rows:
        key = (r.refs, r.count, r.kw_each, r.kw_min, r.kw_max, r.model)
        if r.refs and key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def summarise_generators(rows: list[GenRow]) -> dict[str, Any]:
    """Count, kW list, total MW (with min/max when ratings are either/or) and a confidence."""
    total_min = total_max = 0.0
    count = 0
    confs = []
    kw_list = []
    uncounted = 0
    for r in rows:
        if r.count is None:
            uncounted += 1
            continue
        count += r.count
        lo = r.kw_min if r.kw_min is not None else (r.kw_each or 0)
        hi = r.kw_max if r.kw_max is not None else (r.kw_each or 0)
        total_min += r.count * lo
        total_max += r.count * hi
        confs.append(r.count_confidence)
        label = f"{r.count} x {int(lo) if lo == int(lo) else lo}"
        if lo != hi:
            label += f"-{int(hi) if hi == int(hi) else hi}"
        label += " kW"
        if r.maker:
            label += f" {r.maker}" + (f" {r.model}" if r.model else "")
        kw_list.append(label)
    if not rows:
        return {
            "generator_count": None, "generator_count_confidence": "none", "unit_kw_list": None,
            "unit_kw_min": None, "unit_kw_max": None, "total_standby_mw": None, "total_standby_mw_min": None,
            "total_standby_mw_max": None, "total_mw_confidence": "none", "generator_rows_uncounted": 0,
        }
    if uncounted:
        conf = "low"
    elif all(c == "high" for c in confs):
        conf = "high"
    elif any(c == "low" for c in confs):
        conf = "low"
    else:
        conf = "medium"
    if total_min != total_max:
        conf = "low"
    kws = [k for r in rows for k in (r.kw_min, r.kw_max) if k is not None]
    return {
        "generator_count": count or None,
        "generator_count_confidence": conf if count else "none",
        "unit_kw_list": "; ".join(kw_list) if kw_list else None,
        "unit_kw_min": min(kws) if kws else None,
        "unit_kw_max": max(kws) if kws else None,
        "total_standby_mw": round((total_min + total_max) / 2000.0, 3) if count else None,
        "total_standby_mw_min": round(total_min / 1000.0, 3) if count else None,
        "total_standby_mw_max": round(total_max / 1000.0, 3) if count else None,
        "total_mw_confidence": conf if count else "none",
        "generator_rows_uncounted": uncounted,
    }


# --------------------------------------------------------------------------------------
# Hours, fuel
# --------------------------------------------------------------------------------------

HOURS_MAINT_RE = re.compile(
    r"(?:not\s+(?:to\s+)?operate\s+(?:for\s+)?more\s+than|no\s+more\s+than|operate\s+no\s+more\s+than|limited\s+to)\s+(\d{1,3}(?:,\d{3})+|\d{1,5})\s+hours\s+per\s+(?:calendar\s+)?year\s+"
    r"(?:for\s+)?(?:scheduled\s+)?(?:maintenance|readiness|testing|maintenance\s+checks)",
    re.IGNORECASE,
)
HOURS_ALL_RE = re.compile(
    r"(\d{1,3}(?:,\d{3})+|\d{1,5})\s+hours\s+per\s+(?:calendar\s+)?year\s+for\s+all\s+purposes", re.IGNORECASE
)
HOURS_COMBINED_RE = re.compile(
    r"(?:limited\s+to|not\s+exceed|no\s+more\s+than|more\s+than)\s+(\d{1,3}(?:,\d{3})+|\d{1,5})\s+hours\s+per\s+(?:calendar\s+)?year\b(?![^.]*for\s+(?:all\s+purposes|scheduled|maintenance|readiness))",
    re.IGNORECASE,
)
GALLONS_RE = re.compile(r"(\d{1,3}(?:,\d{3})+|\d{3,7})\s+gallons\s+of\s+(?:diesel|ULSD|fuel)[^.]{0,40}?per\s+(?:calendar\s+)?year", re.IGNORECASE)
SULFUR_PPM_RE = re.compile(r"(\d{1,4})\s*ppm", re.IGNORECASE)


def _distinct_ints(matches) -> list[int]:
    vals = []
    for m in matches:
        v = int(m.group(1).replace(",", ""))
        if v not in vals:
            vals.append(v)
    return vals


def extract_hours(text: str) -> dict[str, Any]:
    flat = flatten(text)
    maint = _distinct_ints(HOURS_MAINT_RE.finditer(flat))
    allp = _distinct_ints(HOURS_ALL_RE.finditer(flat))
    combined = [v for v in _distinct_ints(HOURS_COMBINED_RE.finditer(flat)) if v not in maint and v not in allp]
    conf = "high" if allp and maint else ("medium" if (allp or maint or combined) else "none")
    return {
        "hours_maint_per_year": ";".join(map(str, maint)) or None,
        "hours_all_purpose_per_year": ";".join(map(str, allp)) or None,
        "hours_combined_per_year": ";".join(map(str, combined)) or None,
        "hours_confidence": conf,
    }


def extract_fuel(text: str) -> dict[str, Any]:
    flat = flatten(text)
    low = flat.lower()
    fuel = None
    conf = "none"
    if re.search(r"ultra[-\s]?low[-\s]?sulfur diesel", low):
        fuel, conf = "ULSD (ultra-low sulfur diesel)", "high"
    elif re.search(r"approved fuel[^.]{0,120}?\bdiesel\b", low) or re.search(r"\bdiesel fuel\b", low):
        fuel, conf = "diesel", "high" if "approved fuel" in low else "medium"
    elif re.search(r"natural gas", low):
        fuel, conf = "natural gas", "medium"
    if fuel and fuel != "natural gas" and re.search(r"natural gas[- ]fired|fueled by natural gas", low):
        fuel += "; natural gas units also present"
    ppm = _distinct_ints(SULFUR_PPM_RE.finditer(flat))
    gallons = _distinct_ints(GALLONS_RE.finditer(flat))
    return {
        "fuel": fuel,
        "fuel_confidence": conf,
        "fuel_sulfur_ppm": min(ppm) if ppm else None,
        "fuel_gallons_per_year_limits": ";".join(map(str, gallons)) or None,
        "fuel_gallons_per_year_total": sum(gallons) if gallons else None,
    }


# --------------------------------------------------------------------------------------
# Virginia cover page: registration, permittee, approved date, facility address
# --------------------------------------------------------------------------------------

REG_RE = re.compile(r"Registration\s+(?:No\.?|Number)\s*:?\s*(\d{4,6})", re.IGNORECASE)
APPROVED_RE = re.compile(
    r"Approved\s+on\s*:?\s*((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s*\d{4})",
    re.IGNORECASE,
)
AMENDED_RE = re.compile(
    r"(?:Last\s+)?Amended\s*:?\s*((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s*\d{4})",
    re.IGNORECASE,
)
MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], 1)}


def us_date_to_iso(s: str | None) -> str | None:
    if not s:
        return None
    m = re.match(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})", s.strip())
    if m and m.group(1).capitalize() in MONTHS:
        return f"{m.group(3)}-{MONTHS[m.group(1).capitalize()]:02d}-{int(m.group(2)):02d}"
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{2,4})", s.strip())
    if m:
        y = int(m.group(3))
        y = y + 2000 if y < 100 else y
        return f"{y}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"
    return None


STREET_WORDS = (
    r"Road|Rd|Drive|Dr|Boulevard|Blvd|Way|Lane|Ln|Street|St|Avenue|Ave|Parkway|Pkwy|Court|Ct|Place|Pl|Circle|Cir|"
    r"Highway|Hwy|Route|Rte|Trail|Trl|Terrace|Ter|Loop|Run|Pike|Turnpike|Square|Sq|Plaza|Center Dr|Center Drive|Path|Crossing|Commons"
)
STREET_RE = re.compile(
    rf"(?P<nums>\d{{1,6}}(?:\s*,?\s*(?:and|&)?\s*\d{{1,6}})*)\s+(?P<street>[A-Z][A-Za-z0-9.'\- ]{{1,60}}?\b(?:{STREET_WORDS})\b\.?)(?:\s*(?:NW|NE|SW|SE))?",
)
VA_CITY_ZIP_RE = re.compile(
    r"^\s*\(?(?P<city>[A-Z][A-Za-z.'\- ]{1,40}?),?\s+(?:Virginia|VA)\.?\s+(?P<zip>\d{5})(?:-\d{4})?\)?\s*$", re.MULTILINE
)
COUNTY_RE = re.compile(r"\(?\b([A-Z][A-Za-z.' ]+?\s+(?:County|City))\b\)?")
VA_INDEPENDENT_CITIES = {"Manassas", "Manassas Park", "Alexandria", "Fairfax", "Falls Church", "Richmond", "Norfolk",
                         "Virginia Beach", "Chesapeake", "Suffolk", "Hampton", "Newport News", "Lynchburg", "Danville",
                         "Roanoke", "Harrisonburg", "Fredericksburg", "Charlottesville", "Petersburg", "Hopewell",
                         "Colonial Heights", "Portsmouth", "Winchester", "Staunton", "Waynesboro", "Martinsville",
                         "Bristol", "Radford", "Salem", "Poquoson", "Williamsburg", "Lexington", "Buena Vista",
                         "Covington", "Galax", "Norton", "Emporia", "Franklin"}


def extract_va_cover(text: str) -> dict[str, Any]:
    """Registration number, permittee, approval date and the FACILITY address (not the mailing one)."""
    pages = text.split("\f")
    head = "\n".join(pages[:6]) if len(pages) > 1 else text[:12000]
    out: dict[str, Any] = {
        "registration_no_pdf": None, "registration_nos_pdf_all": None, "permittee_pdf": None, "approved_on": None, "last_amended": None,
        "facility_street": None, "facility_city": None, "facility_zip": None, "facility_county_pdf": None,
        "facility_address_raw": None, "address_confidence": "none", "address_method": None,
    }
    regs = REG_RE.findall(text)
    if regs:
        out["registration_no_pdf"] = max(set(regs), key=regs.count)
        out["registration_nos_pdf_all"] = ";".join(sorted(set(regs)))
    m = APPROVED_RE.search(head)
    out["approved_on"] = us_date_to_iso(m.group(1)) if m else None
    m = AMENDED_RE.search(head)
    out["last_amended"] = us_date_to_iso(m.group(1)) if m else None

    # permittee = the non-address line just above each "Registration No." / page header "Registration Number:"
    cands = []
    lines = [l.strip() for l in head.replace("\f", "\n").split("\n")]
    for i, l in enumerate(lines):
        if REG_RE.search(l):
            for j in range(i - 1, max(-1, i - 4), -1):
                prev = lines[j]
                if not prev or VA_CITY_ZIP_RE.match(prev) or STREET_RE.search(prev) or re.search(r"\d{5}", prev):
                    continue
                if re.search(r"commonwealth|department of|permit to|stationary source|page \d", prev, re.IGNORECASE):
                    continue
                cands.append(prev)
                break
    if cands:
        out["permittee_pdf"] = max(set(cands), key=cands.count)

    # facility address: block of lines ending in a "<City>, VA <zip>" line.
    blocks = []
    for m in VA_CITY_ZIP_RE.finditer(head):
        before = head[:m.start()]
        prev_lines = [l.strip() for l in before.split("\n") if l.strip()][-8:]
        addr_lines = []
        for l in reversed(prev_lines):
            if re.search(r"located at|authorized to|gen-?sets?|generator|Registration|construct and operate|permittee", l, re.IGNORECASE):
                break
            if STREET_RE.search(l) or re.match(r"^(?:[A-Z0-9\-]+\s*[–-]\s*)?\d", l) or re.search(r"Suite|Building|Bldg", l):
                addr_lines.insert(0, l)
                continue
            if addr_lines:
                break
        tail = head[m.end():m.end() + 80]
        county = None
        cm = COUNTY_RE.search(tail) or COUNTY_RE.search("\n".join(addr_lines))
        if cm:
            county = cm.group(1).strip()
        located = bool(re.search(
            r"located\s+at|located\s+in|facility\s+location|site\s+location|authorized\s+to\s+construct", before[-450:], re.IGNORECASE))
        blocks.append({
            "lines": addr_lines, "city": m.group("city").strip(), "zip": m.group("zip"), "county": county,
            "located": located, "pos": m.start(),
        })
    chosen = None
    method = None
    for b in blocks:
        if b["located"]:
            chosen, method = b, "located_at"
            break
    if chosen is None and blocks:
        # The first VA block on the cover is normally the permittee's mailing address; the last one
        # (after "Registration No.") is more often the facility. Use the last block, low confidence.
        reg_pos = REG_RE.search(head)
        after_reg = [b for b in blocks if reg_pos and b["pos"] > reg_pos.start()]
        chosen = (after_reg or blocks)[-1]
        method = "last_va_address_block" if after_reg else "only_va_address_block"
    if chosen:
        raw = ", ".join(chosen["lines"] + [f"{chosen['city']}, VA {chosen['zip']}"])
        out["facility_address_raw"] = raw
        street = None
        for l in chosen["lines"]:
            l2 = re.sub(r"^[A-Z0-9\-]+\s*[–-]\s*", "", l)  # "MCC1 – 10880 Airman Avenue"
            sm = STREET_RE.search(l2)
            if sm:
                first_num = re.match(r"\d{1,6}", sm.group("nums")).group(0)
                street = f"{first_num} {sm.group('street').rstrip('.')}"
                break
        out["facility_street"] = street
        out["facility_city"] = chosen["city"]
        out["facility_zip"] = chosen["zip"]
        out["facility_county_pdf"] = chosen["county"]
        if street and method == "located_at":
            out["address_confidence"] = "high"
        elif street:
            out["address_confidence"] = "low"
        else:
            out["address_confidence"] = "low"
        out["address_method"] = method
    return out


# --------------------------------------------------------------------------------------
# TCEQ application packages
# --------------------------------------------------------------------------------------

TX_BBOX = (25.6, 36.7, -106.8, -93.3)  # lat_min, lat_max, lon_min, lon_max

COORD_PATTERNS = [
    # Core Data Form 27/28
    ("core_data_form_decimal", re.compile(
        r"Latitude\s*\(N\)\s*In\s*Decimal\s*:?\s*(?P<lat>-?\d{2}\.\d{3,}).{0,60}?Longitude\s*\(W\)\s*In\s*Decimal\s*:?\s*(?P<lon>-?\d{2,3}\.\d{3,})",
        re.IGNORECASE), "high"),
    # STEERS site block
    ("steers_decimal", re.compile(
        r"Latitude\s*\(N\)\s*\(#+\.#+\)\s*(?P<lat>-?\d{2}\.\d{3,}).{0,80}?Longitude\s*\(W\)\s*\(-?#+\.#+\)\s*(?P<lon>-?\d{2,3}\.\d{3,})",
        re.IGNORECASE), "high"),
    # generic decimal pair within 120 chars
    ("generic_decimal", re.compile(
        r"Latitude[^0-9\-\n]{0,40}(?P<lat>-?\d{2}\.\d{4,})[^0-9\-]{0,120}?Longitude[^0-9\-\n]{0,40}(?P<lon>-?\d{2,3}\.\d{4,})",
        re.IGNORECASE), "medium"),
    # OP-1 Section X DMS
    ("op1_dms", re.compile(
        r"Latitude\s*\(nearest\s+second\)\s*:?\s*(?P<lad>\d{1,2})\s*[°º]\s*(?P<lam>\d{1,2})\s*['’′]\s*(?P<las>\d{1,2}(?:\.\d+)?)\s*[\"”″]\s*N"
        r".{0,80}?Longitude\s*\(nearest\s+second\)\s*:?\s*(?P<lod>\d{1,3})\s*[°º]\s*(?P<lom>\d{1,2})\s*['’′]\s*(?P<los>\d{1,2}(?:\.\d+)?)\s*[\"”″]\s*W",
        re.IGNORECASE | re.DOTALL), "medium"),
    # generic DMS "29 28 48.13N -98 41 33.20W"
    ("generic_dms", re.compile(
        r"(?P<lad>\d{2})\s+(?P<lam>\d{1,2})\s+(?P<las>\d{1,2}(?:\.\d+)?)\s*N\s+-?(?P<lod>\d{2,3})\s+(?P<lom>\d{1,2})\s+(?P<los>\d{1,2}(?:\.\d+)?)\s*W"),
     "medium"),
    # TCEQ letter map link marker=lon,lat
    ("map_marker", re.compile(r"marker=(?P<lon>-?\d{2,3}\.\d{3,}),(?P<lat>-?\d{2}\.\d{3,})"), "medium"),
]


def _in_tx(lat: float, lon: float) -> bool:
    return TX_BBOX[0] <= lat <= TX_BBOX[1] and TX_BBOX[2] <= lon <= TX_BBOX[3]


def extract_tx_coordinates(text: str) -> dict[str, Any]:
    flat = flatten(text)
    for name, rx, conf in COORD_PATTERNS:
        for m in rx.finditer(flat):
            gd = m.groupdict()
            if gd.get("lat") and gd.get("lon"):
                lat, lon = float(gd["lat"]), float(gd["lon"])
            else:
                lat = float(gd["lad"]) + float(gd["lam"]) / 60 + float(gd["las"]) / 3600
                lon = -(float(gd["lod"]) + float(gd["lom"]) / 60 + float(gd["los"]) / 3600)
            if lon > 0:
                lon = -lon  # "(W)" longitudes are sometimes written unsigned
            if _in_tx(lat, lon):
                return {"lat": round(lat, 6), "lon": round(lon, 6), "coord_source": name, "coord_confidence": conf,
                        "coord_snippet": flat[max(0, m.start() - 40):m.end() + 20]}
    return {"lat": None, "lon": None, "coord_source": None, "coord_confidence": "none", "coord_snippet": None}


RN_RE = re.compile(r"\bRN\s?(\d{9})\b")
CN_RE = re.compile(r"\bCN\s?(\d{9})\b")
TX_STREET_PATTERNS = [
    re.compile(r"Number\s+and\s+Street\s+(?P<v>\d[^\n]{3,80})"),
    re.compile(r"\(No\s+PO\s+Boxes\)\s*\n\s*(?P<v>\d[^\n]{3,80})"),
    re.compile(r"Street\s+Address[^\n]{0,60}\n\s*(?P<v>\d[^\n]{3,80})"),
    re.compile(r"Physical\s+Address[^\n]{0,40}:?\s*(?P<v>\d[^\n]{3,80})"),
]
TX_CITY_PATTERNS = [
    re.compile(r"\bCity\s+(?P<city>[A-Z][A-Za-z .'\-]{1,40}?)\s+State\s+TX\s+ZIP\s+(?P<zip>\d{5})"),
    re.compile(r"\n\s*City\s+(?P<city>[A-Z][A-Za-z .'\-]{1,40}?)\s*\n(?:.*\n){0,3}?\s*ZIP\s+(?P<zip>\d{5})"),
    re.compile(r"(?P<city>[A-Z][A-Za-z .'\-]{1,40}?),\s*(?:TX|Texas)\s+(?P<zip>\d{5})"),
]
TX_COUNTY_RE = re.compile(r"(?:\b24\.\s*)?\bCounty\s*:?\s+(?P<county>[A-Z][A-Za-z .'\-]{2,30}?)(?=\s*(?:\n|\d{2}\.|Nearest|State|ZIP|$))")
NAICS_RE = re.compile(r"NAICS\s*Code[^0-9\n]{0,40}(?:\n[^0-9\n]*)?\s*(?:\d{4}\s+)?(?P<naics>\d{6})\b", re.IGNORECASE)
NAICS_ANY_RE = re.compile(r"\b518210\b")
SITE_NAME_RE = re.compile(r"Site\s+Name\s*:\s*(?P<v>[^\n]{2,100})")
RE_NAME_PATTERNS = [
    re.compile(r"name\s+of\s+the\s+Regulated\s+Entity\s*\(RE\)\?\s*(?P<v>[^\n]{2,100})", re.IGNORECASE),
    re.compile(r"Regulated\s+Entity\s+Name[^\n]*\n\s*(?P<v>[^\n]{2,100})", re.IGNORECASE),
]
SUBMITTAL_RE = re.compile(r"Submittal\s+Date\s*\(mm/dd/yyyy\)\s*:?\s*(?P<v>\d{2}/\d{2}/\d{4})")
PERMIT_NO_RE = re.compile(r"Permit\s+(?:Number|No\.?)\s*:?\s*(?P<v>O\d{4}|\d{4,6}(?:[A-Z]\d*)?)\b")
OPSUM_UNIT_RE = re.compile(
    r"(?<![\w/])(?P<uid>[A-Z0-9][A-Z0-9.\-/]{0,24})[^\S\n]+OP-UA2[^\S\n]+(?P<desc>[^\n]{0,140}?)"
    r"(?=[^\S\n][A-Z0-9][A-Z0-9.\-/]{0,24}[^\S\n]+OP-(?:UA|SUM)\w*[^\S\n]|[^\S\n]*$)",
    re.MULTILINE,
)
UNIT_KW_RE = re.compile(r"(?P<kw>\d{3,5})\s?KW\b", re.IGNORECASE)
UNIT_ID_MW_RE = re.compile(r"^(?P<mw>\d+(?:\.\d+)?)MW\d", re.IGNORECASE)


def extract_tx_fields(text: str) -> dict[str, Any]:
    """Identifiers, address, coordinates, NAICS and the OP-SUM generator inventory from a TCEQ package."""
    out: dict[str, Any] = {
        "regulated_entity_name": None, "site_name": None, "rn": None, "cn": None, "street": None, "city": None,
        "zip": None, "county": None, "naics": None, "is_datacenter_naics": None, "submittal_date": None,
        "tceq_permit_no_pdf": None,
    }
    rns = RN_RE.findall(text)
    cns = CN_RE.findall(text)
    out["rn"] = "RN" + max(set(rns), key=rns.count) if rns else None
    out["cn"] = "CN" + max(set(cns), key=cns.count) if cns else None
    for rx in RE_NAME_PATTERNS:
        m = rx.search(text)
        if m:
            out["regulated_entity_name"] = m.group("v").strip()
            break
    m = SITE_NAME_RE.search(text)
    out["site_name"] = m.group("v").strip() if m else None
    for rx in TX_STREET_PATTERNS:
        m = rx.search(text)
        if m:
            out["street"] = re.sub(r"\s+", " ", m.group("v")).strip()
            break
    for rx in TX_CITY_PATTERNS:
        m = rx.search(text)
        if m:
            out["city"] = m.group("city").strip().title()
            out["zip"] = m.group("zip")
            break
    m = TX_COUNTY_RE.search(text)
    if m:
        out["county"] = m.group("county").strip().title()
    m = NAICS_RE.search(text)
    if m:
        out["naics"] = m.group("naics")
    elif NAICS_ANY_RE.search(text):
        out["naics"] = "518210"
    out["is_datacenter_naics"] = (out["naics"] == "518210") if out["naics"] else None
    m = SUBMITTAL_RE.search(text)
    out["submittal_date"] = us_date_to_iso(m.group("v")) if m else None
    m = PERMIT_NO_RE.search(text)
    out["tceq_permit_no_pdf"] = m.group("v") if m else None
    out.update(extract_tx_coordinates(text))
    out.update(extract_tx_generators(text))
    return out


def extract_tx_generators(text: str) -> dict[str, Any]:
    lines_text = re.sub(r"[^\S\n]+", " ", text.replace("\f", "\n"))
    units: dict[str, dict[str, Any]] = {}
    groups_only = 0
    for m in OPSUM_UNIT_RE.finditer(lines_text):
        uid, desc = m.group("uid"), m.group("desc")
        if uid.upper().startswith("GRP") or uid.upper() in ("UNIT", "ID"):
            groups_only += 1
            continue
        if not re.search(r"generator|gen-?set|engine|EMGEN|GEN\d", desc + " " + uid, re.IGNORECASE):
            continue
        if re.search(r"fire\s*pump|tank|cooling|unload", desc, re.IGNORECASE):
            continue
        kw = None
        km = UNIT_KW_RE.search(desc)
        if km:
            kw = float(km.group("kw"))
        else:
            im = UNIT_ID_MW_RE.match(uid)
            if im:
                kw = float(im.group("mw")) * 1000.0
        units.setdefault(uid, {"kw": kw, "desc": desc[:80]})
    if not units:
        # Fall back to Virginia-style prose/table ratings (some TCEQ packages include permit tables)
        rows = find_generator_rows(text)
        if rows:
            s = summarise_generators(rows)
            s["generator_inventory_source"] = "rating_rows"
            return s
        return {
            "generator_count": None, "generator_count_confidence": "none", "unit_kw_list": None, "unit_kw_min": None,
            "unit_kw_max": None, "total_standby_mw": None, "total_standby_mw_min": None, "total_standby_mw_max": None,
            "total_mw_confidence": "none", "generator_rows_uncounted": groups_only,
            "generator_inventory_source": "op_sum_groups_only" if groups_only else None,
        }
    kws = [u["kw"] for u in units.values() if u["kw"]]
    with_kw = len(kws)
    total = sum(kws) if with_kw == len(units) and kws else None
    from collections import Counter

    c = Counter(int(k) for k in kws)
    kw_list = "; ".join(f"{n} x {k} kW" for k, n in sorted(c.items(), reverse=True)) or None
    if with_kw == 0:
        conf = "none"
    elif with_kw == len(units):
        conf = "high" if all(re.search(r"\d{3,5}\s?KW", u["desc"], re.IGNORECASE) for u in units.values()) else "medium"
    else:
        conf = "low"
    return {
        "generator_count": len(units),
        "generator_count_confidence": "high",
        "unit_kw_list": kw_list,
        "unit_kw_min": min(kws) if kws else None,
        "unit_kw_max": max(kws) if kws else None,
        "total_standby_mw": round(total / 1000.0, 3) if total else None,
        "total_standby_mw_min": round(total / 1000.0, 3) if total else None,
        "total_standby_mw_max": round(total / 1000.0, 3) if total else None,
        "total_mw_confidence": conf,
        "generator_rows_uncounted": len(units) - with_kw,
        "generator_inventory_source": "op_sum",
    }


def genrows_as_dicts(rows: list[GenRow]) -> list[dict[str, Any]]:
    return [asdict(r) for r in rows]
