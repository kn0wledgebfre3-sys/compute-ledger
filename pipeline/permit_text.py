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
    pdfplumber's extract_text() interleaves multi-line cells line by line (the rating of a row can
    come before its description's last lines, or before its count), so the equipment list is read
    twice (see read_generator_inventory, rewritten 2026-10-22 after the second read of all 183
    permits in review/va_reread/):
      - table read: pdfplumber extract_tables() cells (pdf_to_tables), rows recognised by content;
      - text read: count anchors and kW ratings paired in document order inside the equipment-list
        regions of the flattened text (the only read for OCR scans, unruled layouts and fixtures).
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
        if any(p.strip() for p in pages):
            return "\f".join(pages)
        # pdfplumber can see zero pages (or zero text) in a PDF whose page tree pypdf still reads
        # (reg 52173, a 96-page OCR scan): fall through to pypdf rather than return nothing.
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


def pdf_to_tables(path: Path, max_pages: int | None = None) -> list[dict[str, Any]]:
    """Ruled tables as pdfplumber sees them: [{"page": n, "rows": [[cell, ...], ...]}, ...].
    Cells keep their internal line breaks. Pages without ruling lines (most OCR scans) give
    nothing; the text reader covers those. Returns [] when pdfplumber is unavailable."""
    try:
        import pdfplumber
    except ImportError:
        return []
    out: list[dict[str, Any]] = []
    with pdfplumber.open(str(Path(path))) as pdf:
        for i, page in enumerate(pdf.pages):
            if max_pages and i >= max_pages:
                break
            try:
                tables = page.extract_tables()
            except Exception:  # malformed page objects: skip the page, the text reader still runs
                continue
            for t in tables:
                rows = [[c if c is None else str(c) for c in r] for r in t if r and any(c for c in r)]
                if len(rows) >= 1 and max(len(r) for r in rows) >= 2:
                    out.append({"page": i + 1, "rows": rows})
    return out


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
_UNIT_W = r"(?:nineteen|eighteen|seventeen|sixteen|fifteen|fourteen|thirteen|twelve|eleven|ten|nine|eight|seven|six|five|four|three|two|one)"
_TENS_W = r"(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)"
_BELOW_100 = rf"(?:{_TENS_W}(?:[\s-]+(?:nine|eight|seven|six|five|four|three|two|one)\b)?|{_UNIT_W})"
# "Twenty three", "Thirty-two", "One hundred ten", "One thousand three hundred and thirty-two"
SPELLED_NUM = (
    rf"(?:{_UNIT_W}\s+thousand(?:\s+(?:and\s+)?{_UNIT_W}\s+hundred)?(?:\s+(?:and\s+)?{_BELOW_100})?"
    rf"|{_UNIT_W}\s+hundred(?:\s+(?:and\s+)?{_BELOW_100})?|{_BELOW_100})"
)
SPELLED_RE = re.compile(rf"\b{SPELLED_NUM}\b", re.IGNORECASE)
WORD_NUM_RE = SPELLED_RE  # backwards-compatible name


def spelled_to_int(s: str) -> int | None:
    total = cur = 0
    seen = False
    for w in re.findall(r"[a-z]+", (s or "").lower()):
        if w in _ONES:
            cur += _ONES[w]
        elif w in _TENS:
            cur += _TENS[w]
        elif w == "hundred":
            cur = (cur or 1) * 100
        elif w == "thousand":
            total += (cur or 1) * 1000
            cur = 0
        elif w == "and":
            continue
        else:
            break
        seen = True
    n = total + cur
    return n if seen and n > 0 else None


def words_to_int(s: str) -> int | None:
    m = SPELLED_RE.search(s or "")
    return spelled_to_int(m.group(0)) if m else None


def num(s: str | None) -> float | None:
    if s is None:
        return None
    try:
        return float(str(s).replace(",", ""))
    except ValueError:
        return None


# --------------------------------------------------------------------------------------
# Unit references -> unit ids / counts. Forms seen in the 183 DEQ permits:
#   "1 through 23", "Gen21 – Gen52", "EGU1 thru EGU3", "3, 4, 17 through 20", "91 and 92", "S1",
#   "ENG46 – ENG61, ENG67 – ENG110", "ENG113 – ENG 152", "EG113-EG145", "EG01 -EG54", "1-5",
#   "101-GEN-A1 through 101-GEN-D1" (letter ranges), "Gen4101-01,-02,-03,-04,-Z", "1 through 1,332",
#   "DC5EG-A DC5EG-B DC5EG-C" (space separated), "Generator 20 through 24", "BYEG1 through BYEG60*".
# Single ids that look like ranges and are NOT: "EG2-26", "6-2", "1510-3", "4-1" (second number lower).
# --------------------------------------------------------------------------------------

_RANGE_WORD_RE = re.compile(r"\s*(?:\bthrough\b|\bthru\b|\bto\b)\s*|\s+-\s*|\s*-\s+", re.IGNORECASE)
_LIST_SEP_RE = re.compile(r"\s*(?:,|;|&|\band\b|\bor\b)\s*", re.IGNORECASE)
_HYPHEN_SAME_PREFIX_RE = re.compile(r"([A-Za-z_]*)(\d+)-\1(\d+)")


def _runs(s: str) -> list[str]:
    return re.findall(r"\d+|[A-Z]+|[^A-Z\d]", s)


def _expand_range(a: str, b: str) -> list[str] | None:
    a = re.sub(r"\s+", "", a).upper()
    b = re.sub(r"\s+", "", b).upper()
    ra, rb = _runs(a), _runs(b)
    if not ra or not rb:
        return None
    if b.isdigit() and ra[-1].isdigit() and len(ra) > 1:  # "Generator20 through 24", "EG01 - 54"
        rb = ra[:-1] + [b]
    if len(ra) != len(rb):
        return None
    diffs = [i for i, (p, q) in enumerate(zip(ra, rb)) if p != q]
    if not diffs:
        return [a]
    if len(diffs) != 1:
        return None
    i = diffs[0]
    p, q = ra[i], rb[i]
    if p.isdigit() and q.isdigit():
        x, y = int(p), int(q)
        if not (0 <= y - x < 5000):
            return None
        width = len(p) if p.startswith("0") else 0
        return ["".join(ra[:i] + [str(v).zfill(width)] + ra[i + 1:]) for v in range(x, y + 1)]
    if len(p) == 1 and len(q) == 1 and p.isalpha() and q.isalpha() and 0 <= ord(q) - ord(p) < 26:
        return ["".join(ra[:i] + [chr(c)] + ra[i + 1:]) for c in range(ord(p), ord(q) + 1)]
    return None


def _is_unit_token(t: str) -> bool:
    t = t.strip(" .:()[]")
    if not t or t.lower() in ("n/a", "na", "none", "each", "units", "unit"):
        return False
    if re.search(r"\d", t):
        return len(t) <= 24
    return bool(re.fullmatch(r"-?[A-Z]{2,5}|-[A-Z0-9]{1,3}", t))


def hyphen_ids_style(all_refs: list[str]) -> bool:
    """True when a permit numbers units "1-0", "2-1", "4-1" (hyphenated ids, second number not larger):
    then "1-2" in the same permit is one unit, not a two-unit range (73294, 73741)."""
    for r in all_refs:
        for m in re.finditer(r"(?<![\w-])(\d+)-(\d+)(?![\w-])", r or ""):
            if int(m.group(2)) <= int(m.group(1)):
                return True
    return False


def expand_refs(refs: str | None, hyphen_ranges: bool = True) -> list[str] | None:
    """Unit ids named by a 'Ref. Nos.' cell or a '(Ref. Nos. ...)' mention; None when nothing parseable."""
    if not refs:
        return None
    s = refs.replace("–", "-").replace("—", "-").replace("‐", "-").replace("‑", "-")
    s = re.sub(r"[*†‡§]", "", s)
    s = re.sub(r"\([^()]*[A-Za-z]{3,}[^()]*\)", " ", s)  # "133 (Group 3)", "(Building A)": labels, not ids
    s = re.sub(r"\bRef(?:erence)?s?\.?\s*(?:No(?:s|\(s\))?\.?|Numbers?)?\s*:?", " ", s, flags=re.IGNORECASE)
    s = re.sub(r"(\d),(\d{3})(?!\d)", r"\1\2", s)  # "1 through 1,332"
    s = re.sub(r"\b(?!(?:through|thru|to|and|or)\b)([A-Za-z]{2,})\s+(\d)", r"\1\2", s, flags=re.IGNORECASE)  # "ENG 152", "Generator 20"
    s = re.sub(r"\s+", " ", s).strip()
    ids: list[str] = []
    for item in _LIST_SEP_RE.split(s):
        item = item.strip(" .:;")
        if not item:
            continue
        parts = _RANGE_WORD_RE.split(item, maxsplit=1)
        if len(parts) == 2 and parts[0].strip() and parts[1].strip():
            left = parts[0].split()[-1]
            right = parts[1].split()[0]
            got = _expand_range(left, right)
            if got:
                ids.extend(got)
                continue
        m = _HYPHEN_SAME_PREFIX_RE.fullmatch(item.replace(" ", ""))
        if m and (hyphen_ranges or m.group(1)) and int(m.group(3)) > int(m.group(2)) and int(m.group(3)) - int(m.group(2)) < 5000:
            ids.extend(f"{m.group(1).upper()}{v}" for v in range(int(m.group(2)), int(m.group(3)) + 1))
            continue
        toks = item.split()
        if len(toks) > 1:  # "EG POD2", "Transitory Generator1": only the tokens with a number are ids
            toks = [t for t in toks if re.search(r"\d", t)]
        ids.extend(t.strip(" .:()").upper() for t in toks if _is_unit_token(t))
    return ids or None


def count_from_refs(refs: str | None, hyphen_ranges: bool = True) -> int | None:
    """Number of units implied by a 'Ref. Nos.' cell. None when nothing parseable."""
    ids = expand_refs(refs, hyphen_ranges)
    return len(ids) if ids else None


# --------------------------------------------------------------------------------------
# Generator inventory. Two independent reads of the equipment list:
#   * table read  - pdfplumber's ruled-table cells (rows_from_tables): refs | description | capacity
#   * text read   - the flattened page text (find_generator_rows): count anchors and ratings paired
#                   in document order inside the equipment-list regions (works for OCR scans,
#                   unruled layouts and the text-only fixtures, where there are no cells)
# read_generator_inventory() reports the table read when there is one and uses the text read and the
# unit ids named in the permit conditions as cross-checks; confidence is high only when they agree.
# --------------------------------------------------------------------------------------

MAKERS = (
    r"Caterpillar|CAT\b|Cummins|MTU|Rolls[- ]Royce|Kohler|Generac|Detroit Diesel|Perkins|Volvo Penta|"
    r"John Deere|Mitsubishi|Hitzinger|Baudouin|Daimler|Wartsila|W[aä]rtsil[aä]|Jenbacher|Waukesha|Doosan|Scania|"
    r"Katolight|Kato|Onan|Rehlko|Solar|Cat\b"
)
MAKER_RE = re.compile(rf"({MAKERS})\s*(?:[Mm]odel\s+)?([A-Z0-9][A-Za-z0-9\-/]+)?")
GEN_KEYWORD_RE = re.compile(r"gen-?\s?sets?|generators?|engines?", re.IGNORECASE)
GENSET_RE = re.compile(r"gen-?\s?sets?\b|generators?\b|generator\s+sets?\b|gensets?\b", re.IGNORECASE)
GENSET_PLURAL_RE = re.compile(r"gen-?\s?sets\b|generators\b|generator\s+sets\b|gensets\b|engines\b", re.IGNORECASE)
GENSET_SINGULAR_RE = re.compile(r"gen-?\s?set\b|generator\b|generator\s+set\b|genset\b|engine\b", re.IGNORECASE)
# always excluded: not standby gen-sets (turbines are prime-power units; fire pumps drive pumps)
EXCLUDE_STRONG_RE = re.compile(r"fire\W+(?:\S+\W+){0,2}?pumps?\b|boilers?|turbines?|cooling\s+towers?|chillers?|\bfurnaces?|incinerat", re.IGNORECASE)
# excluded only when the row does not describe a gen-set ("... gen-set each with 2500 gallon storage tank" is a gen-set)
EXCLUDE_WEAK_RE = re.compile(r"\btanks?\b|\bheaters?\b|heating\s+units?|\bpumps?\b|\bUSTs?\b|\bASTs?\b", re.IGNORECASE)
# rows under these section titles are not part of the permitted inventory
SECTION_SKIP_RE = re.compile(r"being\s+replaced|to\s+be\s+(?:removed|replaced|decommissioned|retired)|removed\s+from\s+service|"
                             r"will\s+be\s+removed|decommissioned", re.IGNORECASE)
SECTION_TITLE_RE = re.compile(
    r"(?:Transitory\s+)?Equipment\s+(?:to\s+be\s+(?:Constructed|Operated|Installed|Removed|Replaced)|Being\s+(?:Replaced|Removed)|"
    r"Previously\s+(?:Permitted|Constructed)|Not\s+Previously\s+Permitted|Permitted\s+Prior|permitted\s+prior|"
    r"Exempt\s+from\s+Permitting|installed\s+prior|Previously\s+Installed)|Previously\s+Permitted\s+(?:Transitory\s+)?Equipment|"
    r"Transitory\s+Equipment|Exempt\s+Equipment",
    re.IGNORECASE,
)

KW_MIN, KW_MAX = 10.0, 20000.0  # plausible per-unit electrical ratings (kW)
# "2,500 ekW", "2500KW", "3,250 kWe", "2.5 MW", "1,620* ekW", "3,620 ekW*"; not "685 mkW" (mechanical),
# "kWm", "kWh", "kW-hr" or "g/kW-hr"
KW_TOKEN_RE = re.compile(
    r"(?<![\d,.])(?P<num>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)\s*[*!|]?\s*(?P<unit>ekW|kWe|kW|MWe|MW|kilowatts?|megawatts?|RW)\*?"  # RW: OCR of kW (73160)
    r"(?![A-Za-z]|\s*-\s*h(?:r|our)\b)",
    re.IGNORECASE,
)
# A unit whose number sits on the previous line of the same cell: "2848 brake / horsepower or 2000 N/A /
# EGU3 emergency generators ekW, each" (73200), "1030 Bhp (750 None ... Model KW)" (71804).
DANGLING_UNIT_RE = re.compile(r"\b(?P<unit>ekW|kWe|kW|kilowatts?)\b", re.IGNORECASE)
DANGLING_NUM_RE = re.compile(
    r"(?:(?:\bor\b|\(|/|\bgenerating\b|\brated\s+at\b)\s*(?P<num>\d{1,3}(?:,\d{3})+|\d{2,5})"
    r"|(?<![\d,.])(?P<num2>\d{1,3},\d{3}))(?=\s|$)"  # "2,750 / Emergency Diesel / EG-10 through ekW" (74242)
    r"(?!\s*(?:bhp|hp|brake|horse|gallons?|ppm|hours?|%|e?kW|kWe|MW|mkW|kilowatts?|BHP))", re.IGNORECASE)
BHP_TOKEN_RE = re.compile(r"(?<![\d,.])(\d{1,3}(?:,\d{3})+|\d{2,5})\s*(?:bhp|brake\s*horse-?\s*power|hp)\b", re.IGNORECASE)
EACH_RE = re.compile(r"\(each(?: unit| engine| gen-?set)?\)|,\s*each\b|\beach\b", re.IGNORECASE)
DERATE_RE = re.compile(r"de-?\s*rated", re.IGNORECASE)

_COUNT_WORDS = r"units?|engines?|gen-?\s?sets?|generators?|generator\s+sets?|engine[- ]generator\s+sets?"
PAREN_COUNT_RE = re.compile(
    rf"(?<![A-Za-z0-9.)])\(\s*(?P<n>\d{{1,3}}(?:,\d{{3}})+|\d{{1,4}})\s*(?P<u>{_COUNT_WORDS})?\s*\)", re.IGNORECASE)
UNITS_COUNT_RE = re.compile(
    r"(?<![\d,.\-/(])\b(?P<n>\d{1,4})\s+(?P<u>units|engines|gen-?\s?sets|generators|generator\s+sets|engine\s+gen-?sets)\b", re.IGNORECASE)
LEADING_COUNT_RE = re.compile(
    r"(?<![\d,.\-/])\b(?P<n>\d{1,3})\s+(?:new\s+)?(?:emergency|diesel|standby|non-emergency|natural\s+gas|identical)\b"
    r"[^.;()]{0,60}?\b(?:gen-?\s?sets|generators|engines|generator\s+sets)\b", re.IGNORECASE)
_SPELLED_FOLLOW_RE = re.compile(
    rf"^[\s,]*(?:\(\s*(?P<pn>\d{{1,3}}(?:,\d{{3}})+|\d{{1,4}})\s*\)\s*)?(?:new\s+|identical\s+|additional\s+)?"
    rf"(?:[A-Z][\w\-/.]*\s+){{0,2}}"  # makers not in MAKERS: "Twelve Clarke diesel ...", "Six Evolve diesel ..."
    rf"(?:{MAKERS}|emergency|non-?\s?emergency|diesel|standby|natural\s+gas|engine|gen-?\s?sets?|generators?|model|units?)",
    re.IGNORECASE)


def find_count_anchors(s: str) -> list[dict[str, Any]]:
    """Unit-count statements in a description or an equipment-list region, in document order:
    "(23)", "Twenty three (23)", "Four (4)", "(36 units)", "(1 unit)", "(1,332)", "Three Caterpillar",
    "26 emergency diesel gen-sets", "36 units". Four-digit years in parentheses ("(1987)",
    "(Manufacture Date: 2010)") and street numbers are not counts."""
    out: list[dict[str, Any]] = []
    taken: list[tuple[int, int]] = []

    def free(a: int, b: int) -> bool:
        return all(b <= x or a >= y for x, y in taken)

    spelled = [(m.start(), m.end(), spelled_to_int(m.group(0))) for m in SPELLED_RE.finditer(s)]
    for m in PAREN_COUNT_RE.finditer(s):
        n = int(m.group("n").replace(",", ""))
        if n <= 0:
            continue
        sp = next((x for x in reversed(spelled) if x[1] <= m.start() and not s[x[1]:m.start()].strip()), None)
        if sp and sp[2] != n:
            sp = None
        if not m.group("u") and 1900 <= n <= 2099 and not sp:
            continue  # a year: "Caterpillar 3516 diesel generator (1987)"
        if n >= 1900 and re.search(r"date\s*:?\s*$|manufactured?\s*(?:in)?\s*:?\s*$", s[max(0, m.start() - 25):m.start()], re.IGNORECASE):
            continue  # "Manufacture Date: (2010)" (but "... Permit Date (48) Cummins" is a count)
        if re.match(r"\s*\d{3}[-.\s]\d{4}\b", s[m.end():m.end() + 10]):
            continue  # "(804) 698-4000": a telephone area code
        start = sp[0] if sp else m.start()
        kind = "suffix" if (m.group("u") and not sp) else "prefix"
        out.append({"start": start, "end": m.end(), "n": n, "kind": kind, "src": "paren" if not m.group("u") else "paren_units"})
        taken.append((start, m.end()))
    for m in UNITS_COUNT_RE.finditer(s):
        n = int(m.group("n"))
        if n <= 0 or (1900 <= n <= 2099) or not free(m.start(), m.end()):
            continue
        if re.search(r"(?:\bthrough|\bthru|\bto|\band|[-–—,&])\s*$", s[max(0, m.start() - 12):m.start()], re.IGNORECASE):
            continue  # "... 137 through 142 engine gen-sets": a ref range, not a count
        if m.group("n").startswith("0"):
            continue  # "EG-001 through EG- / 020 engine gen-sets": a zero-padded unit id
        if re.search(r"\b[A-Z]{2,}[-\s]?$", s[max(0, m.start() - 8):m.start()]):
            continue  # "EG POD 2 engine gen-sets": the number of a unit id
        out.append({"start": m.start(), "end": m.end(), "n": n, "kind": "suffix", "src": "units"})
        taken.append((m.start(), m.end()))
    for a, b, n in spelled:
        if not n or not free(a, b):
            continue
        f = _SPELLED_FOLLOW_RE.match(s[b:b + 60])
        if not f:
            continue
        if f.group("pn") and int(f.group("pn").replace(",", "")) != n:
            continue
        out.append({"start": a, "end": b + (f.end("pn") + 1 if f.group("pn") else 0), "n": n, "kind": "prefix", "src": "spelled"})
        taken.append((a, b))
    m = re.match(r"\s*(?P<n>\d{1,4})\s*[-–—]\s*(?=[A-Z(])", s)  # "34 - MTU 20V4000G74S ... gen-set" (cell start)
    if m and free(m.start("n"), m.end("n")) and not (1900 <= int(m.group("n")) <= 2099) and int(m.group("n")) > 0:
        out.append({"start": m.start("n"), "end": m.end(), "n": int(m.group("n")), "kind": "prefix", "src": "dash"})
        taken.append((m.start("n"), m.end()))
    for m in LEADING_COUNT_RE.finditer(s):
        n = int(m.group("n"))
        if n <= 0 or not free(m.start(), m.start() + len(m.group("n"))):
            continue
        if re.search(r"(?:\bthrough|\bthru|\bto|\band|[-–—,&])\s*$", s[max(0, m.start() - 12):m.start()], re.IGNORECASE):
            continue  # the end of a ref range: "2 through 29 emergency diesel engine gen-sets"
        if m.group("n").startswith("0"):
            continue
        out.append({"start": m.start(), "end": m.start() + len(m.group("n")), "n": n, "kind": "prefix", "src": "leading"})
        taken.append((m.start(), m.end()))
    return sorted(out, key=lambda a: a["start"])


def _to_kw(value: float | None, unit: str) -> float | None:
    if value is None:
        return None
    return value * 1000.0 if unit.upper().startswith(("MW", "MEGA")) else value


def _fmt_kw(v: float) -> str:
    return str(int(v)) if v == int(v) else str(v)


def parse_capacity(s: str) -> dict[str, Any] | None:
    """Per-unit electrical rating from a capacity cell (or the text of one).
    * "de-rated to/from": the rating printed first is used, the other is noted;
    * "(2,250 ekW standby)" / "625 ekW ... (standby) 560 ekW ... (prime)": the standby rating is used;
    * alternatives for different makes ("3,353 bhp/2,250 ekW 2,633 bhp/2,500 ekW", "Cummins: ... MTU: ..."):
      the first listed is the central value, kw_min/kw_max carry the range."""
    toks = []
    for m in KW_TOKEN_RE.finditer(s or ""):
        v = _to_kw(num(m.group("num")), m.group("unit"))
        if v is not None and KW_MIN <= v <= KW_MAX:
            toks.append({"kw": v, "start": m.start(), "end": m.end()})
    if not toks:
        return None
    notes = []
    d = DERATE_RE.search(s)
    if d and any(t["end"] <= d.start() for t in toks):
        dropped = [t for t in toks if t["start"] >= d.start()]
        if dropped:
            notes.append(f"de-rate {'/'.join(_fmt_kw(t['kw']) for t in dropped)} kW printed, first-listed rating used")
        toks = [t for t in toks if t["start"] < d.start()]
    for i, t in enumerate(toks):
        nxt = toks[i + 1]["start"] if i + 1 < len(toks) else len(s)
        tail = s[t["end"]:nxt][:40]
        t["standby"] = bool(re.search(r"standby", tail, re.IGNORECASE))
    if any(t["standby"] for t in toks) and not all(t["standby"] for t in toks):
        other = [t for t in toks if not t["standby"]]
        notes.append(f"standby rating used (other rating {'/'.join(_fmt_kw(t['kw']) for t in other)} kW)")
        toks = [t for t in toks if t["standby"]]
    vals = list(dict.fromkeys(t["kw"] for t in toks))
    if len(vals) > 1:
        notes.append(f"alternative ratings {'/'.join(_fmt_kw(v) for v in vals)} kW, first listed used")
    bm = BHP_TOKEN_RE.search(s)
    return {"kw": vals[0], "kw_min": min(vals), "kw_max": max(vals), "bhp": num(bm.group(1)) if bm else None,
            "each": bool(EACH_RE.search(s)), "note": "; ".join(notes) or None}


@dataclass
class GenRow:
    refs: str | None
    count: int | None
    count_source: str  # paren|paren_units|units|spelled|leading|refs|single|inherited|none
    count_confidence: str  # high|medium|low|none
    kw_each: float | None  # central per-unit rating (first listed when alternatives are printed)
    kw_min: float | None
    kw_max: float | None
    bhp_each: float | None
    maker: str | None
    model: str | None
    each_flag: bool
    description: str
    snippet: str
    read: str = "text"  # table|text
    section: str | None = None
    note: str | None = None

    def total_kw(self) -> float | None:
        if self.count is None or self.kw_each is None:
            return None
        return self.count * self.kw_each


def _row_excluded(head: str, tail: str = "") -> bool:
    """head = description text before the rating, tail = continuation after it (cell-per-line layouts)."""
    if EXCLUDE_STRONG_RE.search(head):
        return True
    g = GENSET_RE.search(tail)
    tail_before_genset = tail[:g.start()] if g else tail
    if EXCLUDE_STRONG_RE.search(tail_before_genset) and not GENSET_RE.search(head):
        return True
    both = head + " " + tail
    return bool(EXCLUDE_WEAK_RE.search(both)) and not GENSET_RE.search(both) and not re.search(r"\bengines?\b", both, re.IGNORECASE)


def _count_for(desc: str, refs: str | None, hyphen_ranges: bool = True,
               refs_from_text: bool = False) -> tuple[int | None, str, str, int | None]:
    """(count, source, confidence, refcount) for one equipment row. ``refs_from_text``: the refs were cut
    from interleaved text and may belong to the neighbouring row, so a singular description wins."""
    anchors = find_count_anchors(desc)
    refcount = count_from_refs(refs, hyphen_ranges) if refs else None
    singular = bool(GENSET_SINGULAR_RE.search(desc)) and not GENSET_PLURAL_RE.search(desc)
    if refs_from_text and singular and refcount and refcount > 1 and not anchors:
        return 1, "single", "low", refcount
    if anchors:
        a = anchors[0]
        count, source = a["n"], a["src"]
        if refcount is not None:
            conf = "high" if refcount == count else "low"
        else:
            conf = "medium"
        return count, source, conf, refcount
    if refcount:
        if singular and refcount == 1:
            return 1, "refs", "high", refcount
        return refcount, "refs", "medium", refcount
    if singular or re.match(r"^\s*(?:One|A|An)\b", desc, re.IGNORECASE):
        return 1, "single", "medium", refcount
    return None, "none", "none", refcount


def _maker_model(desc: str) -> tuple[str | None, str | None]:
    mk = MAKER_RE.search(desc)
    return (mk.group(1) if mk else None), (mk.group(2) if mk and mk.group(2) else None)


# ---------------------------- table read ----------------------------------------------

_HDR_DESC_RE = re.compile(r"description", re.IGNORECASE)
_HDR_CAP_RE = re.compile(r"capacity|rated|\bsize\b|rating|maximum|standby", re.IGNORECASE)
_HDR_REF_RE = re.compile(r"\bref|unit\s*id|\bid\b|reference", re.IGNORECASE)
_NONEQUIP_TABLE_RE = re.compile(r"lbs?/hr|\btpy\b|tons?/yr|tons\s+per|g/kw|g/bhp|ppmv", re.IGNORECASE)
_POLLUTANT_COL_RE = re.compile(r"^\s*pollutants?\b", re.IGNORECASE)  # emission-limit tables: pollutant names in column 1


def _cell(c: Any) -> str:
    if c is None:
        return ""
    s = str(c).replace("\n", " ")
    s = re.sub(r"(\w)-\s+(\w)", r"\1-\2", s)  # "gen- sets", "3516C- HD", "diesel- fired"
    return re.sub(r"\s+", " ", s).strip()


def _header_roles(r: list[str]) -> dict[str, int]:
    roles: dict[str, int] = {}
    for i, c in enumerate(r):
        if not c:
            continue
        if _HDR_DESC_RE.search(c):
            roles.setdefault("desc", i)
        elif _HDR_CAP_RE.search(c) and not re.search(r"federal|permit\s+date|control|requirement", c, re.IGNORECASE):
            roles.setdefault("cap", i)
        elif _HDR_REF_RE.search(c) and not re.search(r"stack|federal|requirement", c, re.IGNORECASE):
            roles.setdefault("ref", i)
    return roles


def rows_from_tables(tables: list[dict[str, Any]] | None) -> list[GenRow]:
    """Generator rows from pdfplumber's ruled tables. Rows are recognised by content (a capacity cell
    with a kW rating and a description naming a gen-set/engine), so headerless continuation tables on
    later pages and merged header layouts are read the same way; header rows only say which column is
    which when that is ambiguous. Emission-limit tables (lbs/hr, tpy, 'Pollutant') are skipped."""
    rows: list[GenRow] = []
    seen: set[tuple] = set()
    prev_roles: dict[str, int] | None = None
    prev_ncols = None
    hyphen_ranges = not hyphen_ids_style([_cell(c) for t in tables or [] for r in t.get("rows") or [] for c in r[:3]])
    for t in tables or []:
        raw = t.get("rows") or []
        trows = [[_cell(c) for c in r] for r in raw]
        if any(_NONEQUIP_TABLE_RE.search(c) for r in trows for c in r if c) or any(r and _POLLUTANT_COL_RE.search(r[0]) for r in trows):
            continue
        ncols = max((len(r) for r in trows), default=0)
        roles = prev_roles if (prev_roles and ncols == prev_ncols) else None
        section = None
        last_cap = None
        for ri, r in enumerate(trows):
            nonempty = [c for c in r if c]
            if not nonempty:
                continue
            has_kw = [i for i, c in enumerate(r) if c and parse_capacity(c)]
            if any(_HDR_DESC_RE.search(c) for c in r) and any(_HDR_CAP_RE.search(c) for c in r) and not has_kw:
                roles = _header_roles(r)
                prev_roles, prev_ncols = roles, ncols
                continue
            uniq = list(dict.fromkeys(nonempty))
            if len(uniq) == 1 and not has_kw and not find_count_anchors(uniq[0]):
                if SECTION_TITLE_RE.search(uniq[0]) or SECTION_SKIP_RE.search(uniq[0]):
                    section = uniq[0][:120]
                continue
            # description cell: the header's column if it holds text, else the gen-set-like cell
            # ("One (1) Cummins 300 kW emergency diesel engine gen-set" names its rating too)
            desc_i = roles.get("desc") if roles else None
            if desc_i is None or desc_i >= len(r) or not r[desc_i]:
                cands = [i for i, c in enumerate(r) if c and (GEN_KEYWORD_RE.search(c) or MAKER_RE.search(c))]
                pool = [i for i in cands if i not in has_kw] or cands
                desc_i = max(pool, key=lambda i: len(r[i])) if pool else None
            if desc_i is None:
                continue
            desc = r[desc_i]
            if not (GEN_KEYWORD_RE.search(desc) or MAKER_RE.search(desc)):
                continue
            cap_cands = [i for i in has_kw if i != desc_i]
            if not cap_cands and desc_i in has_kw and find_count_anchors(desc):
                cap_cands = [desc_i]  # "One (1) Cummins 300 kW emergency diesel engine gen-set" with no capacity column
            # (a kW figure only inside a model name, "Caterpillar C18 750 ekW" in an engine-group table, is not a row)
            # a row cut by a page break: "consisting of Cummins Model C3000 ... | 3,000 ekW (each unit)"
            # at the top of the next page completes the previous row (which had bhp only)
            pre_cells = [c for c in r[:desc_i] if c]
            if re.match(r"^[a-z(]", desc) and not pre_cells and not find_count_anchors(desc):
                if cap_cands and rows and rows[-1].read == "table" and rows[-1].kw_each is None:
                    c2 = parse_capacity(r[cap_cands[0]])
                    rows[-1].kw_each, rows[-1].kw_min, rows[-1].kw_max = c2["kw"], c2["kw_min"], c2["kw_max"]
                    rows[-1].note = "kW rating from the row's continuation on the next page"
                    last_cap = c2
                continue
            cap = None
            cap_note = None
            if cap_cands:
                cap_i = roles["cap"] if roles and roles.get("cap") in cap_cands else cap_cands[0]
                cap = parse_capacity(r[cap_i])
            elif roles and roles.get("cap") is not None and roles["cap"] < len(raw[ri]) and raw[ri][roles["cap"]] is None and last_cap:
                cap, cap_note = last_cap, "capacity cell merged with the row above"
            ref_i = roles.get("ref") if roles else None
            if ref_i is None or ref_i >= len(r) or not r[ref_i] or ref_i == desc_i:
                ref_i = next((i for i in range(desc_i - 1, -1, -1) if r[i] and re.search(r"\d", r[i])), None)
            refs = r[ref_i] if ref_i is not None else None
            pre = " | ".join(c for c in r[:desc_i] if c)
            if _row_excluded(desc):
                continue
            if section and SECTION_SKIP_RE.search(section):
                continue
            if SECTION_SKIP_RE.search(desc):
                continue
            count, source, conf, _ = _count_for(desc, refs, hyphen_ranges)
            if cap is None:
                # gen-set row with no kW (bhp-only or MMBtu/hr): counted, MW unknown
                bm = BHP_TOKEN_RE.search(" ".join(r))
                if count is None or not bm:
                    continue
                if not GENSET_RE.search(desc) and not (num(bm.group(1)) >= 500 and source in ("paren", "paren_units", "spelled", "units")):
                    continue  # a bare "Diesel Engine 64 bhp" is not shown to drive a generator (FP1 fire pump, 30142)
                cap = {"kw": None, "kw_min": None, "kw_max": None, "bhp": num(bm.group(1)), "each": True,
                       "note": "no kW rating printed (bhp only)"}
            key = (re.sub(r"[\s*†‡]", "", pre).upper(), count, cap["kw"])
            if pre and ((count or 0) >= 2 or re.search(r"[A-Za-z]", refs or "")):
                if key in seen:
                    continue  # the same units listed twice (e.g. under two permit dates)
                seen.add(key)
            maker, model = _maker_model(desc)
            if cap.get("kw") is not None:
                last_cap = cap
            note = "; ".join(n for n in (cap.get("note"), cap_note) if n) or None
            if cap_note:
                conf = "low"
            rows.append(GenRow(
                refs=refs or None, count=count, count_source=source, count_confidence=conf,
                kw_each=cap["kw"], kw_min=cap["kw_min"], kw_max=cap["kw_max"], bhp_each=cap["bhp"],
                maker=maker, model=model, each_flag=bool(cap.get("each")), description=desc[:200],
                snippet=" | ".join(nonempty)[:300], read="table", section=section, note=note,
            ))
    return rows


# ---------------------------- text read -----------------------------------------------

REGION_START_RE = re.compile(
    r"Equipment\s+List|Equipment\s+(?:to\s+be\s+)?(?:Constructed|Operated|Installed)|Previously\s+Permitted\s+Equipment|"
    r"Equipment\s+(?:Previously\s+)?Permitted|Equipment\s+Description|Emission\s+Unit\s+Description|Transitory\s+Equipment",
    re.IGNORECASE)
REGION_END_RE = re.compile(
    r"Specifications\s+(?:included|listed|in\s+the)|equipment\s+specifications|for\s+informational\s+purposes|"
    r"PROCESS\s+REQUIREMENTS|OPERATING\s+LIMITATIONS|EMISSION\s+LIMITS|Emission\s+Controls?\s*[-–—:]|"
    r"Monitoring(?:\s+Devices?)?\s*[-–—:]|Operating\s+Hours\s*[-–—:]|Fuel\s+(?:Throughput|Specifications?)\s*[-–—:]|"
    r"\b\d{1,2}\.\s+[A-Z][A-Za-z/]+(?:\s+[A-Za-z/()]+){0,5}\s*[-–—]\s",  # the next numbered condition: "3. Operating Limitation - "
    re.IGNORECASE)
REGION_MAX = 25000

# junk that precedes a description in the text stream (trailing cells of the previous row, headers)
HEADER_JUNK_RE = re.compile(
    r"Registration\s+(?:No\.?|Number)\s*:?\s*\d+|\bPage\s+\d+(?:\s+of\s+\d+)?|\(?Last\s+amended[^)]*\)?|\b\d{5}(?:-\d{4})?\b(?=\s|$)|"
    r"\bPermit\s+No\.?\s*[A-Z0-9\-]+|\bN/?A\b",
    re.IGNORECASE,
)
DATE_RE = re.compile(
    r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s*\d{4}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b"
)
TRAILING_CELL_JUNK_RE = re.compile(
    r"\b\d{1,2}\s*VAC\s*\d+\s*-[\d\s\-.]+(?:[A-Z](?:\s*\d+)?)?|\bNone\b|\bN/?A\b|NSPS[^|]*|\bSubpart\s+\w+|40\s*CFR[^|]*|\bamended\b|\(?Original Permit Date:?\)?|Modified Permit Date:?|"
    r"\b(?:Transitory )?Equipment (?:to be Constructed|Previously Permitted|Not Previously Permitted|Previously Constructed|Exempt from Permitting)"
    r"(?:\s+at\s+[A-Z0-9][A-Z0-9\-]*(?:,\s*[A-Z0-9][A-Z0-9\-]*)*(?:,?\s+and\s+[A-Z0-9][A-Z0-9\-]*)?)?:?|\bPreviously Permitted Equipment:?|"
    r"\bat (?:IAD|MCC|DC|Building)[-\s]?\w+:?|Ref(?:erence)?\.?\s*Nos?\.?\(?s?\)?\.?|Equipment Description|\(each[^)]*\)|"
    r"(?:Standby |Maximum )?Rated Capacity(?: \(Standby\))?|Delegated Federal Requirements|Original Permit Date|Federal Requirements",
    re.IGNORECASE,
)
REF_TOKEN = r"[A-Za-z]{0,6}-?(?:\d+-)?\d+[A-Za-z]{0,2}"
_REF_SEP = r"\s*(?:through|thru|to|–|—)\s*|\s+-\s*|\s*-\s+"
REFS_RUN_RE = re.compile(
    rf"((?:{REF_TOKEN}(?:(?:{_REF_SEP}){REF_TOKEN})?)"
    rf"(?:\s*(?:,|;|\band\b|&)\s*(?:{REF_TOKEN}(?:(?:{_REF_SEP}){REF_TOKEN})?))*)\s*$",
    re.IGNORECASE,
)


def equipment_regions(flat: str) -> list[tuple[int, int]]:
    """Spans of the flattened text that hold equipment lists (one per permit part / table). An end
    marker only closes a region after at least one kW rating, because "PROCESS REQUIREMENTS" can be the
    heading just above "1. Equipment List"."""
    regions: list[tuple[int, int]] = []
    pos = 0
    while True:
        m = REGION_START_RE.search(flat, pos)
        if not m:
            break
        if re.search(r"\b(?:the|in|on|of|see|per)\s+$", flat[max(0, m.start() - 8):m.start()], re.IGNORECASE):
            pos = m.end()  # "(listed in the Equipment List above)": a mention, not the list
            continue
        s = m.start()
        limit = min(len(flat), s + REGION_MAX)
        if not (KW_TOKEN_RE.search(flat, s, limit) or _dangling_tokens(flat, s, limit, [])):
            pos = m.end()
            continue
        e = None
        for em in REGION_END_RE.finditer(flat, m.end(), limit):
            if KW_TOKEN_RE.search(flat, s, em.start()) or _dangling_tokens(flat, s, em.start(), []):
                e = em.start()
                break
        e = e if e is not None else limit
        first = KW_TOKEN_RE.search(flat, s, e)
        firsts = [x for x in ([first.start()] if first else []) + [t[0] for t in _dangling_tokens(flat, s, e, [])]]
        if firsts:
            fpos = min(firsts)
            starts_before = [mm.start() for mm in REGION_START_RE.finditer(flat, s, fpos)
                             if not re.search(r"\b(?:the|in|on|of|see|per)\s+$", flat[max(0, mm.start() - 8):mm.start()], re.IGNORECASE)]
            if starts_before:
                s = starts_before[-1]  # "equipment list on page 3" in a cover letter is not the list
        if regions and s <= regions[-1][1]:
            regions[-1] = (regions[-1][0], max(e, regions[-1][1]))
        else:
            regions.append((s, e))
        pos = e
    return regions


def _same_rating_cell(gap: str, after: str = "") -> bool:
    """Is the text between two kW ratings still the same capacity cell (alternatives, de-rate, standby)?
    ``after`` is the text just after the second rating ("... 3,000 ekW and/or Kohler KD3000 (each Kohler")."""
    if find_count_anchors(gap):
        return False
    if len(gap) <= 220 and DERATE_RE.search(gap):
        return True  # "1,600 ekW – [other cells] de-rated to [other cells] 1,500 ekW": one cell, not another unit
    if len(gap) <= 220 and (re.search(r"\band/or\b", gap, re.IGNORECASE) or re.search(rf"(?:{MAKERS})\s*:", gap)):
        return True  # alternative makes: "Cummins: 2,250 ekW 3,202 bhp ... MTU: and/or ... 2,250 ekW"
    if len(gap) <= 220 and (re.search(rf"\(each\s+(?:{MAKERS})", gap) or re.search(rf"^\s*(?:and/or\s+(?:{MAKERS})|\(each\s+(?:{MAKERS}))", after)):
        return True  # one rating per make: "3,000 ekW (each Caterpillar C175-16) ... 3,000 ekW and/or Kohler KD3000 (each Kohler"
    if (re.search(r"\b(?:None|N/?A)\b", gap) or DATE_RE.search(gap)) and (MAKER_RE.search(gap) or re.search(r"(?<![\d,./-])\b\d{1,3}\b(?![\d,./-])", gap)):
        return False  # other columns of this row, then the next row's ref/make: "2000 kW NA 2000 4 Caterpillar 3516 1750kW"
    if len(gap) <= 90 and re.search(r"de-?\s*rated|\bstandby\b|\bprime\b", gap, re.IGNORECASE):
        return True
    if len(gap) <= 160 and re.search(r"\band/or\b|\bor\b", gap, re.IGNORECASE) and not SECTION_TITLE_RE.search(gap):
        return True
    return len(gap) <= 40 and not GEN_KEYWORD_RE.search(gap)


_FOOTNOTE_RE = re.compile(r"(?<=\s)[*†‡]{1,3}\s?(?=[A-Za-z])")


def _in_removed_unit_note(flat: str, pos: int, start: int, end: int) -> bool:
    """A rating quoted in a prose note about a unit that is gone: "The removed unit was permitted under
    a mNSR permit dated February 7, 2013 for an emergency engine gen-set (... rated at 2,500 ekW)" (73860)."""
    a = flat.rfind(". ", max(start, pos - 300), pos)
    b = flat.find(". ", pos, min(end, pos + 300))
    sent = flat[(a + 2 if a >= 0 else max(start, pos - 300)):(b if b >= 0 else min(end, pos + 300))]
    return bool(re.search(r"\b(?:was|were|has\s+been|have\s+been)\b", sent, re.IGNORECASE)
                and re.search(r"\bremoved\b|\breplaced\b|\bdecommissioned\b|\bno\s+longer\b", sent, re.IGNORECASE))


def _footnote_spans(flat: str, start: int, end: int) -> list[tuple[int, int]]:
    """Footnotes under an equipment table ("*To account for parasitic load of the fan the generator
    nameplate reads 3,620 ekW. ... 3,500 ekW."): a rating quoted there is not another row. A footnote
    runs to the next table heading, count statement or 400 characters."""
    spans = []
    for m in _FOOTNOTE_RE.finditer(flat, start, end):
        stop = min(end, m.end() + 400)
        nxt = REGION_START_RE.search(flat, m.end(), stop)
        if nxt:
            stop = nxt.start()
        an = find_count_anchors(flat[m.end():stop])
        if an:
            stop = m.end() + an[0]["start"]
        spans.append((m.start(), stop))
    return spans


def _dangling_tokens(flat: str, start: int, end: int, taken: list[tuple[int, int]]) -> list[tuple[int, int, str]]:
    out = []
    for u in DANGLING_UNIT_RE.finditer(flat, start, end):
        if any(a <= u.start() < b for a, b in taken):
            continue
        if re.search(r"\d[\d,.]*\s*\*?\s*\(?$", flat[max(start, u.start() - 12):u.start()]):
            continue  # an ordinary "2,500 ekW" (already a token, or out of range)
        lo = max(start, u.start() - 90)
        cands = [m for m in DANGLING_NUM_RE.finditer(flat, lo, u.start())]
        if not cands:
            continue
        def _g(c):
            return "num" if c.group("num") else "num2"
        cands = [c for c in cands if not re.search(r"\d{1,2}/\d{1,2}/$", flat[max(0, c.start(_g(c)) - 6):c.start(_g(c))])
                 and not re.search(r"de-?\s*rated\s+(?:from|to)\s*$", flat[max(0, c.start(_g(c)) - 22):c.start(_g(c))], re.IGNORECASE)]
        if not cands:
            continue  # "4/20/1995 ... ekW rating": a date, not a wrapped rating
        m = cands[-1]
        g = _g(m)
        v = num(m.group(g))
        if v is None or not (KW_MIN <= v <= KW_MAX) or any(a <= m.start(g) < b for a, b in taken):
            continue
        out.append((m.start(g), u.end(), f"{m.group(g)} {u.group('unit')} " + flat[u.end():u.end() + 45]))
    return out


def _rating_groups(flat: str, start: int, end: int) -> list[dict[str, Any]]:
    toks = []
    for m in KW_TOKEN_RE.finditer(flat, start, end):
        v = _to_kw(num(m.group("num")), m.group("unit"))
        if v is not None and KW_MIN <= v <= KW_MAX:
            toks.append((m.start(), m.end(), None))
    toks += _dangling_tokens(flat, start, end, [(a, b) for a, b, _ in toks])
    toks.sort()
    groups: list[dict[str, Any]] = []
    toks = [t for t in toks if not any(a <= t[0] < b for a, b in _footnote_spans(flat, start, end))]
    toks = [t for t in toks if not _in_removed_unit_note(flat, t[0], start, end)]
    for s, e, repaired in toks:
        if groups and s >= groups[-1]["end"] and _same_rating_cell(flat[groups[-1]["end"]:s], flat[e:e + 40]):
            groups[-1]["end"] = e
            groups[-1]["repaired"] = groups[-1]["repaired"] or repaired
            continue
        groups.append({"start": s, "end": e, "repaired": repaired})
    for i, g in enumerate(groups):
        nxt = groups[i + 1]["start"] if i + 1 < len(groups) else end
        g["cap"] = parse_capacity(g["repaired"] or flat[g["start"]:min(nxt, end, g["end"] + 45)])
    return [g for g in groups if g["cap"]]


def _refs_before(window: str) -> str | None:
    """The refs cell right before a description (row-per-line layouts)."""
    starts = []
    for rx in (MAKER_RE, re.compile(r"\b(?:emergency|non-emergency|diesel|standby)\b", re.IGNORECASE)):
        last = None
        for mm in rx.finditer(window):
            last = mm.start()
        if last is not None:
            starts.append(last)
    desc_start = min(starts) if starts else len(window)
    refs_clean = DATE_RE.sub(" ", window[:desc_start])
    refs_clean = HEADER_JUNK_RE.sub(" ", refs_clean)
    refs_clean = TRAILING_CELL_JUNK_RE.sub(" ", refs_clean)
    refs_clean = re.sub(r"\b\d{1,3}(?:,\d{3})+\s*(?:bhp|ekW|kW|gallon)s?\b.*?(?=\s)", " ", refs_clean)
    refs_clean = re.sub(r"[|:]", " ", refs_clean)
    refs_clean = re.sub(r"\s+", " ", refs_clean).strip(" .,;")
    rm = REFS_RUN_RE.search(refs_clean)
    return rm.group(1).strip(" ,;") if rm else None


_SPLIT_FROM_RE = re.compile(r"\b(?P<a>\d{1,4})\s+(?:through|thru)\b(?P<rest>(?:(?!\b\d+\b).){0,90})$", re.IGNORECASE)
_SPLIT_TO_RE = re.compile(r"^(?:(?!\b\d+\b).){0,60}?\b(?P<b>\d{1,4})\b(?!\s*(?:,\d|bhp|hp|e?kW|kWe|MW|gallons?|%|/))", re.IGNORECASE)


def _split_range_count(head: str, tail: str, refs: str | None = None) -> int | None:
    """A refs cell wrapped around the description in cell-per-line text: "Nos. 1 through Caterpillar
    DM8266, Electric 2500 kW each 12 Power Generators" -> 1 through 12; "EG-2 Caterpillar Model C32
    1,000 eKW ... through Manufactured February ... EG-4" -> EG-2 through EG-4."""
    m = _SPLIT_FROM_RE.search(head)
    if m:
        n = _SPLIT_TO_RE.search(tail)
        if n:
            a, b = int(m.group("a")), int(n.group("b"))
            if 0 < b - a < 2000:
                return b - a + 1
    rm = re.fullmatch(r"\s*([A-Za-z]{1,6}[-_]?)(\d{1,4})\s*", refs or "")
    if rm:
        pfx = re.escape(rm.group(1))
        t = re.search(rf"\b(?:through|thru)\b.{{0,90}}?\b{pfx}\s?(\d{{1,4}})\b", tail, re.IGNORECASE)
        if t and 0 < int(t.group(1)) - int(rm.group(2)) < 2000:
            return int(t.group(1)) - int(rm.group(2)) + 1
    return None


def _section_at(flat: str, rstart: int, pos: int) -> str | None:
    last = None
    for m in SECTION_TITLE_RE.finditer(flat, rstart, pos):
        last = m.group(0)
    return last


def _align(events: list[tuple[str, dict[str, Any]]], suffix_back: bool) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    pending = None
    for k, (kind, ev) in enumerate(events):
        if kind == "A":
            if ev["kind"] == "suffix" and pending is None and specs and specs[-1]["anchor"] is None and specs[-1]["group"]:
                nxt_r = next((e2 for k2, e2 in events[k + 1:] if k2 == "R"), None)
                back = ev["start"] - specs[-1]["group"]["end"]
                fwd = (nxt_r["start"] - ev["end"]) if nxt_r else 10 ** 9
                if back <= 400 and (suffix_back or back <= fwd):
                    specs[-1] = dict(specs[-1], anchor=ev)
                    continue
            if pending is not None:
                specs.append({"anchor": pending, "group": None})
            pending = ev
        else:
            specs.append({"anchor": pending, "group": ev})
            pending = None
    if pending is not None:
        specs.append({"anchor": pending, "group": None})
    return specs


def find_generator_rows(text: str) -> list[GenRow]:
    """Text read of the generator inventory: inside each equipment-list region, pair every count
    anchor ("(23)", "Four (4)", "(36 units)" ...) with a kW rating in document order. pdfplumber emits
    multi-line cells interleaved line by line, so a row's description can continue AFTER its rating
    ("(29) Caterpillar 3516C- 2,500 ekW / ... HD emergency diesel- ... fired engine gen-sets"); pairing
    in order, rather than looking only backwards from each rating, keeps the first row of every table.
    Rows with no count anchor take their count from the refs cell or a singular description; an anchor
    with no rating of its own takes the rating of the row above (merged capacity cell, low confidence)."""
    flat = flatten(text)
    regions = equipment_regions(flat)
    prose = not regions
    if prose:
        regions = [(0, len(flat))]  # prose-only permits (letters): no table, so no merged cells
    rows: list[GenRow] = []
    for rs, re_ in regions:
        groups = _rating_groups(flat, rs, re_)
        if not groups:
            continue
        region = flat[rs:re_]
        anchors = [dict(a, start=a["start"] + rs, end=a["end"] + rs) for a in find_count_anchors(region)]
        anchors = [a for a in anchors if not any(g["start"] <= a["start"] < g["end"] for g in groups)]
        if any(a["src"] in ("paren", "paren_units", "spelled") for a in anchors):
            # a table that states counts as "(23)"/"Four (4)"/"(36 units)" does so on (almost) every row;
            # a bare "142 engine gen-sets" there is the tail of a ref range split across lines, unless the
            # complete range right before it numbers the same units ("EG2-1 through EG2-26 26 emergency")
            def _confirmed(a: dict[str, Any]) -> bool:
                rm = re.search(r"([A-Za-z]{0,6}-?\d+(?:-\d+)?\s+(?:through|thru)\s+[A-Za-z]{0,6}-?\d+(?:-\d+)?)\s*$",
                               flat[max(rs, a["start"] - 60):a["start"]])
                return bool(rm) and count_from_refs(rm.group(1)) == a["n"]
            anchors = [a for a in anchors if a["src"] in ("paren", "paren_units", "spelled") or _confirmed(a)]
        events = sorted([("A", a) for a in anchors] + [("R", g) for g in groups], key=lambda x: x[1]["start"])
        # "(N units)" ends a description: in row-per-line text it precedes its row's rating, in
        # cell-per-line text it follows it. Pair both ways and keep the pairing that leaves fewer
        # ratings without a count and counts without a rating (ties: the nearer rating).
        cands = [_align(events, suffix_back=False), _align(events, suffix_back=True)]
        specs = min(cands, key=lambda sp: sum(1 for x in sp if x["anchor"] is None or x["group"] is None))
        # A capacity cell whose first line sits above the description's first line puts the rating
        # BEFORE its row's count ("2500 kW / EG01 - (6) Cummins ... sets / each"). An anchorless
        # rating whose own stretch of text names no engine or maker belongs to the next count anchor.
        i = 0
        while i < len(specs) - 1:
            sp, nx = specs[i], specs[i + 1]
            if sp["anchor"] is None and sp["group"] and nx["anchor"] is not None and nx["anchor"]["kind"] == "prefix":
                lo = specs[i - 1]["group"]["end"] if i and specs[i - 1]["group"] else max(rs, sp["group"]["start"] - 300)
                own = flat[lo:sp["group"]["start"]] + " " + flat[sp["group"]["end"]:nx["anchor"]["start"]]
                if not (GEN_KEYWORD_RE.search(own) or MAKER_RE.search(own)) and nx["anchor"]["start"] - sp["group"]["end"] < 200:
                    specs[i] = {"anchor": nx["anchor"], "group": sp["group"]}
                    if nx["group"] is not None:
                        specs[i + 1] = {"anchor": None, "group": nx["group"]}
                    else:
                        del specs[i + 1]
                elif (nx["group"] is None and nx["anchor"]["start"] - sp["group"]["end"] < 200
                      and not re.search(r"MMBtu|Btu/hr|gallons?|\btons?\b", flat[nx["anchor"]["start"]:nx["anchor"]["end"] + 150], re.IGNORECASE)
                      and not _row_excluded(flat[nx["anchor"]["start"]:nx["anchor"]["end"] + 150])):
                    # a rating with no count followed by a count with no rating: one row
                    specs[i] = {"anchor": nx["anchor"], "group": sp["group"]}
                    del specs[i + 1]
            i += 1

        prev_end = rs
        last_cap = None
        last_maker = None
        for i, sp in enumerate(specs):
            a, g = sp["anchor"], sp["group"]
            starts = [x["start"] for x in (a, g) if x]
            ends = [x["end"] for x in (a, g) if x]
            row_start = min(starts)
            nxt_start = min((x["start"] for x in (specs[i + 1]["anchor"], specs[i + 1]["group"]) if x), default=re_) if i + 1 < len(specs) else re_
            nxt_start = min(nxt_start, max(ends) + 250)
            if g is None:  # a count with no rating of its own
                head_start = a["start"]
                head = flat[a["start"]:nxt_start]
                tail = ""
            elif a is None or a["start"] > g["start"] or a["kind"] == "suffix":
                # rating first (no count, or "(N units)" after it), or a description that ends with
                # "(36 units)" just before its rating: the description is the text before
                head_start = max(prev_end, min(g["start"], a["start"] if a else g["start"]) - 400)
                head = flat[head_start:g["start"]]
                tail = flat[g["end"]:nxt_start]
            else:  # "(23) Caterpillar ... 2,500 ekW"
                head_start = a["start"]
                head = flat[a["start"]:g["start"]]
                tail = flat[g["end"]:nxt_start]
            row_text = flat[head_start:nxt_start]
            prev_end = max(ends)
            section = _section_at(flat, rs, row_start)
            if section and SECTION_SKIP_RE.search(section):
                continue
            if g is None and not GENSET_RE.search(head) and not re.search(r"\bengines?\b", head, re.I):
                continue  # a stray number, not an equipment row
            if _row_excluded(head, tail):
                continue
            if not (GEN_KEYWORD_RE.search(row_text) or MAKER_RE.search(row_text)):
                continue
            refs = None
            if a is not None:
                count, source = a["n"], a["src"]
                conf = "medium"
                desc = row_text if (g is None or a["start"] > g["start"] or a["kind"] == "suffix") else flat[a["start"]:nxt_start]
                if g is not None and a["kind"] == "suffix" and a["start"] < g["start"]:
                    desc = flat[head_start:a["end"]]  # "... emergency gen-sets (36 units)"
            else:
                # no count anchor: refs cell + singular/plural wording next to the rating (the text further
                # back can be the previous row's description continuing in a cell-per-line layout)
                refs = _refs_before(head)
                local = head[-90:]
                local = re.sub(r"^.*?(?=\b(?:" + MAKERS + r")\b|\b(?:emergency|diesel|standby)\b)", "", local, count=1, flags=re.IGNORECASE)
                desc = (local + " " + tail[:120]).strip()
                count, source, conf, _ = _count_for(desc, refs, refs_from_text=True)
                if (source in ("none", "single") and (count is None or GENSET_PLURAL_RE.search(desc))) or (source == "refs" and count == 1):
                    split = _split_range_count(head, tail, refs)
                    if split:
                        count, source, conf = split, "refs_split", "medium"
            cap = g["cap"] if g else None
            note = None
            if cap is None:
                if prose or last_cap is None or re.search(r"\b(?:bhp|hp|horsepower|MMBtu|Btu|gallons?|gal)\b", head, re.IGNORECASE):
                    continue  # nothing to inherit, or the row has a rating of its own in other units
                mk_here, mk_above = _maker_model(desc)[0], last_maker
                if mk_here and mk_above and mk_here.lower()[:3] != mk_above.lower()[:3]:
                    # a different make cannot share the capacity cell above: the rating is missing
                    # from the text (OCR); keep the units, MW unknown
                    cap = {"kw": None, "kw_min": None, "kw_max": None, "bhp": None, "each": False,
                           "note": "no kW rating found in the text for this row"}
                    conf = "low"
                else:
                    cap, note, conf = last_cap, "no rating of its own: rating of the row above used (merged capacity cell)", "low"
                source = source if source != "none" else "inherited"
            else:
                last_cap = cap
                last_maker = _maker_model(desc)[0]
            if count is not None and count > 1 and not cap.get("each") and conf == "high":
                conf = "medium"
            maker, model = _maker_model(desc)
            if cap["kw"] is None and count is None:
                continue
            if refs is None:
                # same-prefix id ranges printed in the row ("BYEG1 through BYEG60"): used to spot a listing
                # printed twice (74262: the same 120 units under two permit dates)
                rng = []
                for m in re.finditer(r"\b([A-Z]{1,6}-?)(\d{1,4})\*?\s+(?:through|thru)\b", row_text):
                    m2 = re.search(rf"\b{re.escape(m.group(1))}(\d{{1,4}})\b", row_text[m.end():m.end() + 150])
                    if m2:  # "BYEG1 through August 29, ... BYEG60*": cells interleaved inside the range
                        rng.append(f"{m.group(1)}{m.group(2)} through {m.group(1)}{m2.group(1)}")
                if rng and count_from_refs(", ".join(rng)) == count:
                    refs = ", ".join(rng)
            rows.append(GenRow(
                refs=refs, count=count, count_source=source, count_confidence=conf,
                kw_each=cap["kw"], kw_min=cap["kw_min"], kw_max=cap["kw_max"], bhp_each=cap["bhp"],
                maker=maker, model=model, each_flag=bool(cap.get("each")), description=re.sub(r"\s+", " ", desc)[:200],
                snippet=flat[max(0, row_start - 60):min(len(flat), max(ends) + 60)], read="text", section=section,
                note="; ".join(x for x in (cap.get("note"), note) if x) or None,
            ))
    # the same units printed twice (identical refs, count and rating) are one listing
    seen = set()
    out = []
    for r in rows:
        key = (tuple(sorted(expand_refs(r.refs) or [])), r.count, r.kw_each)
        if r.refs and (r.count or 0) >= 2 and count_from_refs(r.refs) == r.count and key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


# ---------------------------- combine --------------------------------------------------

COND_REF_RE = re.compile(
    r"\(\s*(?:Ref(?:erence)?\.?\s*(?:No(?:s|\(s\))?\.?|Numbers?)|Unit\s+(?:ID|Nos?)\.?)\s*:?\s*(?P<refs>[^()]{1,300})\)", re.IGNORECASE)


def condition_unit_ids(text: str) -> set[str]:
    """Unit ids the permit's conditions name, e.g. "(Ref. Nos. 1 through 96, T1, and T2)": a count
    that does not depend on reading the equipment table."""
    ids: set[str] = set()
    for m in COND_REF_RE.finditer(flatten(text)):
        got = expand_refs(m.group("refs"))
        if got and len(got) < 5000:
            ids.update(got)
    return ids


def summarise_generators(rows: list[GenRow]) -> dict[str, Any]:
    """Count, kW list, total MW (central = first-listed rating; min/max when ratings are either/or)
    and a confidence from the rows alone (read_generator_inventory adds the cross-checks)."""
    total = total_min = total_max = 0.0
    count = 0
    confs = []
    kw_list = []
    uncounted = 0
    no_kw = 0
    for r in rows:
        if r.count is None:
            uncounted += 1
            continue
        count += r.count
        confs.append(r.count_confidence)
        if r.kw_each is None:
            no_kw += r.count
            kw_list.append(f"{r.count} x ? kW (bhp only)" + (f" {r.maker}" if r.maker else ""))
            continue
        lo = r.kw_min if r.kw_min is not None else r.kw_each
        hi = r.kw_max if r.kw_max is not None else r.kw_each
        total += r.count * r.kw_each
        total_min += r.count * lo
        total_max += r.count * hi
        label = f"{r.count} x {_fmt_kw(r.kw_each)}"
        if lo != hi:
            label += f" ({_fmt_kw(lo)}-{_fmt_kw(hi)})"
        label += " kW"
        if r.maker:
            label += f" {r.maker}" + (f" {r.model}" if r.model else "")
        kw_list.append(label)
    if not rows or not count:
        return {
            "generator_count": None, "generator_count_confidence": "none", "unit_kw_list": None,
            "unit_kw_min": None, "unit_kw_max": None, "total_standby_mw": None, "total_standby_mw_min": None,
            "total_standby_mw_max": None, "total_mw_confidence": "none", "generator_rows_uncounted": uncounted,
            "generator_units_without_kw": None,
        }
    if uncounted or no_kw:
        conf = "low"
    elif all(c == "high" for c in confs):
        conf = "high"
    elif any(c in ("low", "none") for c in confs):
        conf = "low"
    else:
        conf = "medium"
    if total_min != total_max:
        conf = "low"
    kws = [k for r in rows for k in (r.kw_min, r.kw_max) if k is not None]
    has_mw = count > no_kw
    return {
        "generator_count": count,
        "generator_count_confidence": conf,
        "unit_kw_list": "; ".join(kw_list) if kw_list else None,
        "unit_kw_min": min(kws) if kws else None,
        "unit_kw_max": max(kws) if kws else None,
        "total_standby_mw": round(total / 1000.0, 3) if has_mw else None,
        "total_standby_mw_min": round(total_min / 1000.0, 3) if has_mw else None,
        "total_standby_mw_max": round(total_max / 1000.0, 3) if has_mw else None,
        "total_mw_confidence": conf if has_mw else "none",
        "generator_rows_uncounted": uncounted,
        "generator_units_without_kw": no_kw,
    }


@dataclass
class Inventory:
    rows: list[GenRow]
    summary: dict[str, Any]


def _agree(a: dict[str, Any] | None, b: dict[str, Any] | None) -> tuple[bool, bool]:
    """(counts equal, MW within 1 %)"""
    if not a or not b or not a.get("generator_count") or not b.get("generator_count"):
        return False, False
    c = a["generator_count"] == b["generator_count"]
    ma, mb = a.get("total_standby_mw"), b.get("total_standby_mw")
    m = ma is not None and mb is not None and abs(ma - mb) <= 0.01 * max(ma, mb)
    return c, m


def read_generator_inventory(text: str, tables: list[dict[str, Any]] | None = None) -> Inventory:
    """Generator count and standby MW for one permit, with honest confidence.

    The figures reported are the table read's when the PDF has ruled equipment tables (cells are not
    interleaved), otherwise the text read's (OCR scans, unruled layouts, prose letters, fixtures).

      total_mw_confidence
        high    a table read AND the independent text read give the same count and MW (within 1 %),
                with single-valued ratings and a kW rating for every unit
        medium  one read whose rows are explicit and consistent: a text-only permit, or a table read the
                text read could not reproduce (interleaved layouts the text read mis-pairs)
        low     either/or ratings (central value = first listed, see _min/_max), units without a kW
                rating in the text, ratings inherited from a merged cell, or rows with guessed counts
        none    no MW (no rows, or bhp-only ratings: MW is not estimated)
      generator_count_confidence
        high    as above for the count alone, or the unit ids on the table rows are exactly the ids the
                permit conditions name ("(Ref. Nos. 1 through 96, T1, and T2)")
        medium / low as above
    """
    table_rows = rows_from_tables(tables) if tables else []
    text_rows = find_generator_rows(text)
    t = summarise_generators(table_rows) if table_rows else None
    x = summarise_generators(text_rows) if text_rows else None
    use_table = bool(t and t["generator_count"])
    rows = table_rows if use_table else text_rows
    s = dict(t if use_table else (x or summarise_generators([])))
    other = x if use_table else None
    cond_ids = condition_unit_ids(text)
    n = s.get("generator_count")
    s["generator_read"] = ("table" if use_table else "text") if n else None
    checks = []
    if not n:
        s["generator_crosscheck"] = None
        return Inventory(rows, s)
    c_ok, m_ok = _agree(s, other)
    if use_table:
        if other and other.get("generator_count"):
            checks.append(f"text read {'agrees' if c_ok and m_ok else 'differs'}: {other['generator_count']} units / {other['total_standby_mw']} MW")
        else:
            checks.append("text read found no rows")
    else:
        checks.append("no ruled table: text read only")
    # the conditions' unit ids corroborate the count only when they are the same ids the equipment
    # rows carry (a mere equal count can be a coincidence: conditions often name a subset)
    row_ids: set[str] = set()
    ids_complete = bool(rows)
    for r in rows:
        got = expand_refs(r.refs) if r.refs else None
        if not got or len(got) != r.count:
            ids_complete = False
            break
        row_ids.update(got)
    ids_complete = ids_complete and len(row_ids) == n  # the same id on two rows is a double count
    cond_ok = use_table and ids_complete and bool(cond_ids) and row_ids == cond_ids
    if cond_ids:
        checks.append(f"conditions name {len(cond_ids)} unit ids" + (" (same ids as the equipment rows)" if cond_ok else ""))
    ranged = s.get("total_standby_mw_min") != s.get("total_standby_mw_max")
    no_kw = bool(s.get("generator_units_without_kw"))
    weak_rows = any(r.count_confidence in ("low", "none") for r in rows) or bool(s.get("generator_rows_uncounted"))
    if (use_table and c_ok) or cond_ok:
        count_conf = "high"
    elif not weak_rows:
        count_conf = "medium"  # one consistent read; a disagreeing text read lowers nothing below this
    else:
        count_conf = "low"
    if s.get("total_standby_mw") is None:
        mw_conf = "none"
    elif ranged or no_kw or count_conf == "low":
        mw_conf = "low"
    elif use_table and c_ok and m_ok:
        mw_conf = "high"
    else:
        mw_conf = "medium"
    s["generator_count_confidence"] = count_conf
    s["total_mw_confidence"] = mw_conf
    s["generator_crosscheck"] = "; ".join(checks)
    return Inventory(rows, s)


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
