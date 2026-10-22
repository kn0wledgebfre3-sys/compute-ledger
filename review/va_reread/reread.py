"""Stage 2: independent re-read of VA DEQ datacenter permits.

Two independent methods per permit:
  (a) TABLE: pdfplumber extract_tables() rows under an equipment-list header
  (b) PROSE: ordered token pairing over the equipment-list section text
plus metadata, hour/fuel limits, and any stated facility total.
No code or regexes shared with the pipeline (written blind to it).
"""
import json, os, re, glob, csv, sys
from collections import OrderedDict

RAW = "/home/claude/review/va_reread/raw"
OUT = "/home/claude/review/va_reread"

WORDNUM = {
    'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,'ten':10,
    'eleven':11,'twelve':12,'thirteen':13,'fourteen':14,'fifteen':15,'sixteen':16,'seventeen':17,
    'eighteen':18,'nineteen':19,'twenty':20,'thirty':30,'forty':40,'fifty':50,'sixty':60,
    'seventy':70,'eighty':80,'ninety':90,'hundred':100,
}
_WORDS_DESC = sorted(WORDNUM.keys(), key=len, reverse=True)
WORD1 = r'(?:' + '|'.join(_WORDS_DESC) + r')\b'
# a number phrase: word (hundred)? ((and)? word)*  e.g. "One hundred thirty two", "Twenty-nine", "Six"
WORD_RE = r'(?:' + WORD1 + r'(?:(?:[\s-]+|\s+and\s+)' + WORD1 + r'){0,3})'

def words_to_int(s):
    s = s.lower().replace('-', ' ').replace(' and ', ' ').strip()
    total = 0; cur = 0
    for p in s.split():
        if p not in WORDNUM: return None
        v = WORDNUM[p]
        if v == 100:
            cur = (cur or 1) * 100
        else:
            cur += v
    total += cur
    return total if total else None

NUM = r'(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)'
KW_RE = re.compile(NUM + r'\s*(?:e\s?kW|kWe|ekW|eKW|kW|KW|Kw|kilowatts?|kw)\b', re.I)
KW_RE2 = re.compile(NUM + r'\s*(?:e\s?kW|kWe|ekW|eKW|kW|KW|Kw|kilowatts?|kw)(?![a-z])', re.I)
BHP_RE = re.compile(NUM + r'\s*(?:bhp|b\.h\.p\.|hp|BHp|BMP|brake\s*horsepower|horsepower)\b', re.I)
MMBTU_RE = re.compile(NUM + r'\s*MMBtu', re.I)
MW_RE = re.compile(NUM + r'\s*MW\b(?!h)', re.I)

GEN_WORDS = re.compile(r'generator|gen-?set|engine', re.I)
NONGEN_WORDS = re.compile(r'boiler|water heater|fire pump|firepump|fire-pump|chiller|cooling tower|tank|furnace|heater|turbine|compressor|fuel cell|UPS|battery', re.I)
EMERG_RE = re.compile(r'non-?\s?emergency', re.I)

def to_num(s):
    return float(s.replace(',', ''))

def parse_capacity(text):
    """Return dict kw,bhp,mmbtu,mw (first value of each) from a cell/snippet."""
    out = {'kw': None, 'bhp': None, 'mmbtu': None, 'mw': None}
    t = text.replace('\n', ' ')
    m = KW_RE.search(t) or KW_RE2.search(t)
    if m: out['kw'] = to_num(m.group(1))
    m = BHP_RE.search(t)
    if m: out['bhp'] = to_num(m.group(1))
    m = MMBTU_RE.search(t)
    if m: out['mmbtu'] = to_num(m.group(1))
    m = MW_RE.search(t)
    if m: out['mw'] = to_num(m.group(1))
    return out

COUNT_WORD_RE = re.compile(r'(?<![A-Za-z])(' + WORD_RE + r')\s*(?:\((\d{1,3})\))?(?=\s*[-–]?\s*[A-Za-z(])', re.I)
COUNT_PAREN_RE = re.compile(r'(?<![\w/])\((\d{1,3})\)\s*(?=[-–]?\s*[A-Za-z])')
COUNT_NUMX_RE = re.compile(r'(?<![\w.,])(\d{1,3})\s*(?:x|X|-)\s*(?=[A-Z][a-z])')

def count_from_desc(desc):
    """Count of units from a description string. Returns (count, source)."""
    d = desc.replace('\n', ' ').strip()
    m = COUNT_PAREN_RE.search(d[:90])
    if m:
        n = int(m.group(1))
        w = COUNT_WORD_RE.search(d[:90])
        wv = words_to_int(w.group(1)) if w else None
        if wv is not None and wv != n:
            return n, f'desc-paren(word={wv} mismatch)'
        return n, 'desc-paren'
    m = COUNT_WORD_RE.search(d[:60])
    if m:
        w = words_to_int(m.group(1))
        if w is not None:
            return w, 'desc-word'
    m = COUNT_NUMX_RE.search(d[:20])
    if m:
        return int(m.group(1)), 'desc-numx'
    return None, None

RANGE_SPLIT = re.compile(r'\s*(?:\bthrough\b|\bthru\b|\bto\b|–|—)\s*', re.I)
HYPHEN_RANGE = re.compile(r'^([A-Za-z/#.]*?)(\d+)\s*-\s*([A-Za-z/#.]*?)(\d+)$')

def _endpoint(tok):
    """Return (letter, number) of the trailing identifier part, e.g. '101-GEN-D1' -> ('D',1), 'ENG20' -> ('',20)."""
    m = re.search(r'([A-Za-z])?(\d+)\s*$', tok.strip())
    if m: return (m.group(1) or '', int(m.group(2)))
    m = re.search(r'(?:^|[-_ ])([A-Z])\s*$', tok.strip())
    if m: return (m.group(1), 0)
    return None

def count_from_ref(ref):
    """Count units implied by a reference cell like '63 through 88', 'ENG1 – ENG11, ENG17', 'D1-D7, D18-D24', '101-GEN-A1 through 101-GEN-D1'."""
    if not ref: return None
    r = ref.replace('\n', ' ')
    r = re.sub(r'\s+and\s+', ', ', r, flags=re.I)
    r = re.sub(r'\s*;\s*', ', ', r)
    r = re.sub(r'\(each\)|\(each unit\)', '', r, flags=re.I)
    total = 0; found = False
    for item in re.split(r',', r):
        item = item.strip()
        if not item: continue
        parts = RANGE_SPLIT.split(item)
        if len(parts) == 2 and parts[0].strip() and parts[1].strip():
            a, b = _endpoint(parts[0]), _endpoint(parts[1])
            if a and b:
                if b[1] != a[1] and b[1] >= a[1] and b[1] - a[1] < 400:
                    total += b[1] - a[1] + 1; found = True; continue
                if b[1] == a[1] and a[0] and b[0] and ord(b[0].upper()) >= ord(a[0].upper()):
                    total += ord(b[0].upper()) - ord(a[0].upper()) + 1; found = True; continue
        m = HYPHEN_RANGE.match(item)
        if m:
            a, b = int(m.group(2)), int(m.group(4))
            if b >= a and b - a < 400:
                total += b - a + 1; found = True; continue
        toks = [t for t in re.split(r'\s+', item) if re.search(r'\d|_|House|Swing', t)]
        if toks:
            total += len(toks) if len(toks) <= 2 else 1; found = True
    return total if found else None

def norm(s):
    return re.sub(r'\s+', ' ', (s or '')).strip()

# ---------------- table method -----------------
def header_cols(rows):
    """Given first few rows of a table, find header columns. Returns (desc_i, cap_i, ref_i, nheader) or None."""
    for nh in (1, 2, 3, 4):
        merged = []
        ncol = max(len(r) for r in rows[:nh])
        for c in range(ncol):
            cell = ' '.join(norm(rows[k][c]) for k in range(min(nh, len(rows))) if c < len(rows[k]) and rows[k][c])
            merged.append(cell)
        joined = ' | '.join(merged).lower()
        if 'description' in joined and ('capacity' in joined or 'size' in joined or 'rated' in joined):
            desc_i = next((i for i, c in enumerate(merged) if 'description' in c.lower() and ('equipment' in c.lower() or 'emission unit' in c.lower())), None)
            if desc_i is None:
                desc_i = next((i for i, c in enumerate(merged) if 'description' in c.lower()), None)
            cap_i = next((i for i, c in enumerate(merged) if 'capacity' in c.lower() or 'size' in c.lower() or c.lower().startswith('rated')), None)
            ref_i = next((i for i, c in enumerate(merged) if re.search(r'ref|unit id|emission unit\b', c.lower()) and 'description' not in c.lower()), None)
            return desc_i, cap_i, ref_i, nh
    return None

def row_is_generator(desc, cap):
    txt = (desc or '') + ' ' + (cap or '')
    if NONGEN_WORDS.search(txt) and not GEN_WORDS.search(txt):
        return False
    if re.search(r'fire\s*pump', txt, re.I):
        return False
    if re.search(r'boiler|water heater|cooling tower|chiller', txt, re.I) and not re.search(r'generator|gen-?set', txt, re.I):
        return False
    return bool(GEN_WORDS.search(txt)) or bool(KW_RE.search(txt))

def make_row(desc, cap, ref, source, section):
    cnt, csrc = count_from_desc(desc or '')
    rc = count_from_ref(ref or '')
    if cnt is None and rc is not None:
        cnt, csrc = rc, 'ref'
    if cnt is None:
        d = (desc or '')
        if re.search(r'generators|gen-?sets|engines', d, re.I):
            cnt, csrc = None, 'plural-unknown'
        else:
            cnt, csrc = 1, 'implicit-single'
    capd = parse_capacity((cap or ''))
    if capd['kw'] is None and capd['bhp'] is None and capd['mw'] is None and capd['mmbtu'] is None:
        capd = parse_capacity(desc or '')
        capsrc = 'desc'
    else:
        capsrc = 'cell'
    kind = 'non-emergency' if EMERG_RE.search((desc or '')) else ('emergency' if re.search(r'emergency|standby|stand-by', desc or '', re.I) else 'unspecified')
    fuel = 'natural gas' if re.search(r'natural gas|gas-fired|gas fired', desc or '', re.I) else ('diesel' if re.search(r'diesel|distillate', desc or '', re.I) else 'unspecified')
    each = bool(re.search(r'each', (cap or '') + ' ' + (desc or ''), re.I))
    mw = None; mwsrc = None
    if capd['kw'] is not None:
        mw = capd['kw'] / 1000.0; mwsrc = 'kW'
    elif capd['mw'] is not None:
        mw = capd['mw']; mwsrc = 'MW'
    elif capd['bhp'] is not None:
        mw = capd['bhp'] * 0.000746; mwsrc = 'bhp-mech'
    return dict(source=source, section=section, ref=norm(ref), desc=norm(desc), cap=norm(cap), count=cnt, count_src=csrc,
                ref_count=rc, kw=capd['kw'], bhp=capd['bhp'], mmbtu=capd['mmbtu'], mw_stated=capd['mw'], mw_each=mw, mw_src=mwsrc,
                kind=kind, fuel=fuel, each=each, cap_src=capsrc)

SECTION_HDR = re.compile(r'(Equipment (?:to be|previously|permitted|included|exempt|existing|list|at this)[^\n]*|Existing Equipment[^\n]*|Other permitted equipment[^\n]*|Equipment Exempt[^\n]*)', re.I)

def table_rows_for_permit(d):
    rows = []
    last_hdr = None  # (desc_i, cap_i, ref_i, ncol)
    section = ''
    last_hdr_page = -10; closed = False
    for p in d['pages']:
        text = p['text']
        for tb in p['tables']:
            if not tb or max(len(r) for r in tb) < 3:
                continue
            # section label: nearest preceding heading in page text (approximate)
            hs = SECTION_HDR.findall(text)
            if hs: section = norm(hs[0])[:60]
            hc = header_cols(tb)
            if hc:
                desc_i, cap_i, ref_i, nh = hc
                last_hdr = (desc_i, cap_i, ref_i, max(len(r) for r in tb))
                last_hdr_page = p['i']; closed = False
                data = tb[nh:]
            elif last_hdr and not closed and p['i'] <= last_hdr_page + 1 and max(len(r) for r in tb) == last_hdr[3]:
                desc_i, cap_i, ref_i, _ = last_hdr
                data = tb
            elif last_hdr and not closed and p['i'] <= last_hdr_page + 1:
                # headerless continuation table: infer columns from content
                flat = ' '.join(c for r in tb for c in r if c)
                if re.search(r'tons|lb/hr|g/hp-hr|g/kW-hr|lb/MMBtu|ppm', flat, re.I):
                    continue
                ncol = max(len(r) for r in tb)
                dscore = [0] * ncol; cscore = [0] * ncol
                for r in tb:
                    for ci, c in enumerate(r):
                        if not c: continue
                        if GEN_WORDS.search(c) and len(c) > 12: dscore[ci] += 1
                        if KW_RE.search(c) or BHP_RE.search(c) or MMBTU_RE.search(c): cscore[ci] += 1
                if max(dscore) == 0 or max(cscore) == 0:
                    continue
                desc_i = dscore.index(max(dscore)); cap_i = cscore.index(max(cscore))
                ref_i = 0 if desc_i != 0 else None
                data = tb
            else:
                continue
            for r in data:
                desc = r[desc_i] if desc_i is not None and desc_i < len(r) else None
                cap = r[cap_i] if cap_i is not None and cap_i < len(r) else None
                ref = r[ref_i] if ref_i is not None and ref_i < len(r) else None
                # pdfplumber sometimes shifts cells into None columns; recover from neighbours
                if (desc is None or not desc.strip()):
                    cand = [c for c in r if c and GEN_WORDS.search(c)]
                    if cand: desc = cand[0]
                if (cap is None or not cap.strip()):
                    cand = [c for c in r if c and (KW_RE.search(c) or BHP_RE.search(c) or MMBTU_RE.search(c))]
                    if cand: cap = cand[0]
                if not desc and not cap:
                    continue
                if re.search(r'description', (desc or ''), re.I) and re.search(r'capacity|size', (cap or ''), re.I):
                    continue  # repeated header
                if re.search(r'^\s*(Equipment|Located at|Other permitted|Existing)', desc or '', re.I) and not cap:
                    section = norm(desc)[:60]; continue
                if not row_is_generator(desc, cap):
                    continue
                rr = make_row(desc, cap, ref, 'table', section)
                if rr['kw'] is None and rr['bhp'] is None and rr['mmbtu'] is None and rr['mw_stated'] is None:
                    continue
                rows.append(rr)
        if re.search(r'Specifications included in|PROCESS REQUIREMENTS|OPERATING LIMITATIONS|EMISSION LIMITS', text):
            closed = True
    return rows

# ---------------- prose method -----------------
START_RE = re.compile(r'Equipment List|Emission Units\s*\n|Process Equipment to be operated|Equipment at this facility|Equipment to be (?:modified|constructed|permitted)|installation and operation of', re.I)
END_RE = re.compile(r'Specifications included in|PROCESS REQUIREMENTS|OPERATING LIMITATIONS|OPERATING/EMISSION|EMISSION LIMITS|Emission Controls\s*[-–]|Fuel\s*[-–]\s*The approved', re.I)

def repeated_lines(d):
    from collections import Counter
    c = Counter()
    for p in d['pages']:
        for ln in set(l.strip() for l in p['text'].split('\n') if l.strip()):
            c[ln] += 1
    n = len(d['pages'])
    return {l for l, k in c.items() if k >= max(3, n // 3)}

def section_text(d):
    rep = repeated_lines(d)
    full = []
    for p in d['pages']:
        lines = [l for l in p['text'].split('\n') if l.strip() and l.strip() not in rep and not re.match(r'^Page \d+( of \d+( Pages)?)?$', l.strip())]
        full.append('\n'.join(lines))
    full = '\n'.join(full)
    m = START_RE.search(full)
    if not m:
        return '', full
    start = m.start()
    m2 = END_RE.search(full, m.end() + 50)
    end = m2.start() if m2 else min(len(full), start + 12000)
    # some permits have multiple equipment sections (new + existing) separated by conditions; extend if another header soon after
    sec = full[start:end]
    return sec, full

PROSE_COUNT_RE = re.compile(r'(?<![A-Za-z])(' + WORD_RE + r')\s*\((\d{1,3})\)|(?<![A-Za-z])(' + WORD_RE + r')(?=\s+(?:[A-Z][a-z]|Caterpillar|Cummins|MTU|Kohler|Generac|Detroit|Rolls))|(?<![\w/])\((\d{1,3})\)\s*(?=[-–]?\s*[A-Z])|(?<![\w.,])(\d{1,3})\s*(?:x|X)\s*(?=[A-Z])', re.I)

def prose_rows(sec):
    """Pair count tokens with capacity tokens in order of appearance."""
    tokens = []
    for m in PROSE_COUNT_RE.finditer(sec):
        if m.group(1):
            n = int(m.group(2)); w = words_to_int(m.group(1))
        elif m.group(3):
            n = words_to_int(m.group(3))
            # skip common false positives: 'One' at start of sentence followed by lower-case handled by regex; 'Six Evolve' ok
        elif m.group(4):
            n = int(m.group(4))
        else:
            n = int(m.group(5))
        if n is None: continue
        tokens.append(('C', m.start(), n))
    EXCL = re.compile(r'fire\s*pump|boiler|water heater|chiller|cooling tower|furnace|removed from the site', re.I)
    def excl_cap(pos):
        prev_caps_end = max([m.end() for m in KW_RE.finditer(sec, 0, pos)] + [0])
        lo = max(prev_caps_end, pos - 220)
        return bool(EXCL.search(sec[lo:pos]))
    def excl_cnt(pos):
        return bool(EXCL.search(sec[pos:pos + 90]))
    tokens = [t for t in tokens if not excl_cnt(t[1])]
    unit = 'kw'
    caps = [(m.start(), to_num(m.group(1)), 'kw') for m in KW_RE.finditer(sec) if not excl_cap(m.start())]
    if not caps:
        caps = [(m.start(), to_num(m.group(1)), 'mw') for m in MW_RE.finditer(sec)]
        unit = 'mw'
    if not caps:
        caps = [(m.start(), to_num(m.group(1)), 'bhp') for m in BHP_RE.finditer(sec)]
        unit = 'bhp'
    # collapse alternates: same value, no count token between, and text between signals an alternative
    cpos = sorted(t[1] for t in tokens)
    caps2 = []
    for c in caps:
        if caps2:
            prev = caps2[-1]
            between_txt = sec[prev[0]:c[0]]
            between = any(prev[0] < p < c[0] for p in cpos)
            if (not between and c[1] == prev[1] and len(between_txt) < 400 and
                    re.search(r'and/or|\bor\b|\b[A-Z][A-Za-z]+:\s', between_txt)):
                continue
        caps2.append(c)
    # greedy pairing: each count token takes nearest following unpaired cap within 500 chars, else nearest preceding within 250
    used = set(); rows = []
    for (_, pos, n) in tokens:
        best = None
        for i, c in enumerate(caps2):
            if i in used: continue
            dist = c[0] - pos
            if 0 <= dist < 1000:
                best = i; break
        if best is None:
            for i, c in enumerate(caps2):
                if i in used: continue
                dist = pos - c[0]
                if 0 < dist < 300:
                    best = i
        if best is not None:
            used.add(best)
            rows.append(dict(count=n, val=caps2[best][1], unit=caps2[best][2], pos=pos, count_src='prose-count'))
        else:
            rows.append(dict(count=n, val=None, unit=None, pos=pos, count_src='prose-count-nocap'))
    for i, c in enumerate(caps2):
        if i not in used:
            rows.append(dict(count=1, val=c[1], unit=c[2], pos=c[0], count_src='prose-cap-only'))
    rows.sort(key=lambda r: r['pos'])
    for r in rows:
        if r['val'] is None: r['mw_each'] = None
        elif r['unit'] == 'kw': r['mw_each'] = r['val'] / 1000.0
        elif r['unit'] == 'mw': r['mw_each'] = r['val']
        else: r['mw_each'] = r['val'] * 0.000746
    return rows

# ---------------- metadata -----------------
MONTHS = 'January|February|March|April|May|June|July|August|September|October|November|December'
DATE_RE = re.compile(r'(' + MONTHS + r')\s*(\d{1,2})(?:st|nd|rd|th)?,?\s*(\d{4})')

def metadata(d, reg_file):
    pages = [p['text'] for p in d['pages']]
    full = '\n'.join(pages)
    md = {}
    m = re.search(r'Registration\s*(?:No|Number)\.?:?\s*(?:PRO-)?\s*(\d{3,6})', full)
    md['registration_in_text'] = m.group(1) if m else ''
    md['registration_match'] = (md['registration_in_text'] == reg_file)
    nonempty = [t for t in pages if len(t.strip()) > 200]
    p0 = nonempty[0] if nonempty else (pages[0] if pages else '')
    m = DATE_RE.search(p0)
    if not m:
        for t in nonempty[1:4]:
            m = DATE_RE.search(t)
            if m: break
    md['permit_date'] = f"{m.group(1)} {m.group(2)}, {m.group(3)}" if m else ''
    cover = '\n'.join(pages[:3])
    md['amendment'] = bool(re.search(r'amendment|amended', cover, re.I))
    m = re.search(r'supersedes\s+(?:your|the|all)?\s*(?:previous\s+|minor\s+)?(?:New Source\s*\n?\s*Review\s*\(NSR\)\s*)?permit(?:s)?(?: document)?s?\s+dated\s*\n?\s*((?:' + MONTHS + r')\s*\d{1,2}(?:st|nd|rd|th)?,?\s*\d{4})', full, re.I)
    md['supersedes_date'] = norm(m.group(1)) if m else ''
    md['supersedes'] = bool(m) or bool(re.search(r'supersede', cover, re.I))
    # permittee from cover block (lines between salutation and Location:)
    m = re.search(r'\n((?:Mr|Ms|Mrs|Dr)\.?\s+[^\n]+)\n((?:[^\n]+\n){1,7}?)Location:', p0)
    permittee = ''
    if m:
        lines = [l.strip() for l in m.group(2).split('\n') if l.strip()]
        street_i = next((i for i, l in enumerate(lines) if re.match(r'^(\d|P\.?\s?O\.? Box|One |Two )', l)), None)
        if street_i is not None and street_i > 0:
            permittee = lines[street_i - 1]
        else:
            cand = [l for l in lines if re.search(r'LLC|L\.L\.C|Inc\b|Inc\.|Corp|Company|L\.?P\.?\b|Partners|Trust|Bank|Services|Properties|Holdings|Realty|Data|Ventures|Group|Ltd|Co\.|Center|Centers|Association|University|County', l)]
            permittee = cand[0] if cand else (lines[1] if len(lines) > 1 else (lines[0] if lines else ''))
    if not permittee:
        m = re.search(r'Pollution,?\s*\n([^\n]+)\n', full)
        permittee = m.group(1).strip() if m else ''
    m = re.search(r'Abatement of Air Pollution,?\s*\n([^\n]{3,80})\n([^\n]+)\n', full)
    if m and not re.search(r'^(Registration|Dear|This|In |The |Attached|Any|Words)', m.group(1)) and re.search(r'\d|P\.?O\.? Box|Suite|c/o', m.group(2) + ' ' + m.group(1)) is not None:
        cand = m.group(1).strip()
        if not re.search(r'^(c/o|Mr\.|Ms\.|Mrs\.)', cand):
            permittee = cand
    if re.search(r"Control Board|Vice President|SVP|^c/o|This permit|Regulations for|Authorized Representative|Chief |Director|Manager|President|General Counsel|Officer|Senior|^Location:", permittee):
        m2 = re.search(r'\n((?:Mr|Ms|Mrs|Dr)\.?\s+[^\n]+)\n((?:[^\n]+\n){1,7}?)Location:', p0)
        if m2:
            lines = [l.strip() for l in m2.group(2).split('\n') if l.strip()]
            cand = [l for l in lines if re.search(r'LLC|L\.L\.C|Inc\b|Inc\.|Corp|Company|L\.?P\.?\b|Partners|Trust|Bank|Services|Properties|Holdings|Realty|Data|Ventures|Group|Ltd|Co\.|Center|Centers|Association|University|County|Communications|Corporation', l) and not re.search(r'Vice President|SVP|Officer|Director|Manager|^c/o', l)]
            if cand: permittee = cand[0]
    md['permittee'] = permittee
    m = re.search(r'Location:\s*([^\n]+)', p0)
    md['location_county'] = m.group(1).strip() if m else ''
    # facility name: most common running-header line preceding "Registration Number:" on later pages
    from collections import Counter
    cnt = Counter()
    for t in pages[2:]:
        for m in re.finditer(r'^([^\n]+)\n(?:Permit )?Registration (?:Number|No\.?):', t, re.M):
            ln = m.group(1).strip()
            if not re.match(r'^(Mr|Ms|Mrs)\.', ln) and not re.search(r'\d{5}$', ln):
                cnt[ln] += 1
    fac = cnt.most_common(1)[0][0] if cnt else ''
    if not fac:
        m = re.search(r'located at\s*(?:the\s+)?([^\n]+?)(?:\s+facility)?\n', full, re.I)
        fac = m.group(1).strip() if m else ''
    md['facility_name'] = fac
    # site address: permit page "located at ... \n street \n City, Virginia ZIP"
    site = ''; city = ''
    m = re.search(r'is authorized to[^\n]*\n(?:[^\n]*\n){0,3}?located (?:at|in)[^\n]*\n((?:[^\n]+\n){1,7})', full, re.I) or \
        re.search(r'located (?:at|in)\s*\n((?:[^\n]+\n){1,6})', full, re.I)
    if m:
        lines = [l.strip() for l in m.group(1).split('\n') if l.strip()]
        lines = [l for l in lines if not re.match(r'^\(?[A-Za-z .]+ County\)?$', l)]
        streets = [l for l in lines if re.search(r'(?:^|[:\s])\d{2,6}\s+[A-Z][A-Za-z]', l) and not re.search(r'Registration|Approved on|Permit consists', l)]
        cityl = next((l for l in lines if re.search(r'(?:,|\s)\s*(?:Virginia|VA)\b', l) and re.search(r'\d{5}|Virginia|VA\b', l)), '')
        if streets:
            site = streets[0]
            site = re.sub(r'^[A-Z0-9 -]{2,12}:\s*', '', site)  # strip "IAD870:" prefixes
            if len(streets) > 1:
                site = site + ' (+%d more addresses)' % (len(streets) - 1)
            city = cityl if cityl and cityl != streets[0] else ''
            if not city and site:
                city = re.sub(r'^\d{2,6}\s+[^,]+,\s*', '', site) if ',' in site else ''
                if city == site: city = ''
        elif lines and re.search(r'Intersection|Road|Rd\b|Lane|Highway|Parkway', lines[0]):
            site = lines[0]; city = cityl
    if not site:
        m = re.search(r'(\d{2,6}\s+[^\n,]+(?:Road|Rd\.?|Drive|Dr\.?|Boulevard|Blvd\.?|Street|St\.?|Way|Lane|Ln\.?|Parkway|Pkwy\.?|Court|Ct\.?|Place|Pl\.?|Circle|Highway|Hwy\.?|Avenue|Ave\.?|Trail|Terrace|Loop|Run|Square))[^\n]*\n([^\n]*?,\s*(?:Virginia|VA)\.?\s*\d{5})', full)
        if m:
            site = m.group(1).strip(); city = m.group(2).strip()
    DEQ_OFFICES = re.compile(r'13901 Crown Court|629 East Main|4949-?A? Cox Road|1111 East Main|P\.?\s?O\.? Box 1105|7705 Timberlake|4411 Early Road|355 Deadmore', re.I)
    if site and DEQ_OFFICES.search(site):
        site = ''; city = ''
    if not site:
        # cover letter: "... at <street>, <City>, Virginia <zip>" or "located at ... in <City>"
        m = re.search(r'\bat\s+(\d{2,6}\s+[^\n,]+?),\s*\n?\s*([A-Z][A-Za-z .]+,\s*(?:Virginia|VA)\.?\s*\d{5})', full)
        if m and not DEQ_OFFICES.search(m.group(1)):
            site = m.group(1).strip(); city = m.group(2).strip()
    if not site:
        for m in re.finditer(r'(\d{2,6}\s+[^\n,]+(?:Road|Rd\.?|Drive|Dr\.?|Boulevard|Blvd\.?|Street|St\.?|Way|Lane|Ln\.?|Parkway|Pkwy\.?|Court|Ct\.?|Place|Pl\.?|Circle|Highway|Hwy\.?|Avenue|Ave\.?|Trail|Terrace|Loop|Run|Square|Plaza))[^\n]*\n([^\n]*?,\s*(?:Virginia|VA)\.?\s*\d{5})', full):
            if DEQ_OFFICES.search(m.group(1)): continue
            site = m.group(1).strip(); city = m.group(2).strip(); break
    mail = re.search(r'\n((?:Mr|Ms|Mrs|Dr)\.?\s+[^\n]+)\n((?:[^\n]+\n){1,7}?)Location:', p0)
    md['site_same_as_mailing'] = bool(mail and site and site.split(',')[0].lower()[:18] in mail.group(2).lower())
    if site and not re.search(r'\d', site) and re.match(r'^(?:[A-Z]{2,4}\d*\s+)?\d', city):
        site, city = city, ''
    md['site_street'] = site; md['site_city_line'] = city
    md['site_county'] = ''
    m = re.search(r'\(([A-Za-z .]+ (?:County|City))\)', full)
    if m: md['site_county'] = m.group(1)
    return md

def limits(full):
    hours = OrderedDict()
    for m in re.finditer(r'([^\n.]{0,160}?)(\d{1,3}(?:,\d{3})?)\s*(?:hours|hrs)\b([^\n.]{0,100})', full, re.I):
        pre, n, post = m.group(1), m.group(2), m.group(3)
        ctx = (pre + ' ' + post).lower()
        if not re.search(r'per year|per calendar|12-month|12 month|annual|per rolling|hours/yr|each year|in any', ctx) and not re.search(r'per year|12-month|annual', ctx):
            continue
        tag = []
        for k in ['non-emergency', 'maintenance', 'testing', 'readiness', 'emergency', 'demand response', 'peak', 'combined', 'each', 'per engine', 'per unit', 'total', 'storm avoidance']:
            if k in ctx: tag.append(k)
        key = n + 'h:' + ','.join(tag[:4])
        hours[key] = 1
    fuels = OrderedDict()
    for m in re.finditer(r'([^\n.]{0,120}?)(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)\s*(?:gallons|gal\.?)\b([^\n.]{0,80})', full, re.I):
        ctx = (m.group(1) + ' ' + m.group(3)).lower()
        if re.search(r'per year|12-month|12 month|annual|consecutive|calendar year', ctx) and not re.search(r'per hour|gal/hr|gallons per hour', ctx):
            tag = 'total' if 'total' in ctx or 'combined' in ctx or 'all' in ctx else ('each' if 'each' in ctx else '')
            fuels[m.group(2) + ' gal/yr ' + tag] = 1
    return '; '.join(list(hours.keys())[:12]), '; '.join(list(fuels.keys())[:8])

STATED_TOTAL_RE = re.compile(r'(?:total|combined|aggregate|cumulative|totaling|totalling)[^.\n]{0,100}?' + NUM + r'\s*(MW|ekW|kW|kWe|MWe)\b|' + NUM + r'\s*(MW|ekW|kW|kWe|MWe)\s*(?:total|combined|cumulative|aggregate|in total)', re.I)

def stated_totals(full):
    out = []
    for m in STATED_TOTAL_RE.finditer(full):
        if m.group(1):
            v, u = to_num(m.group(1)), m.group(2)
        else:
            v, u = to_num(m.group(3)), m.group(4)
        mw = v if u.lower().startswith('mw') else v / 1000.0
        ctx = norm(full[max(0, m.start() - 60):m.end() + 20])
        out.append((mw, ctx))
    return out

def summarise(rows):
    """count and MW over rows (table or prose style with count & mw_each)."""
    cnt = 0; mw = 0.0; incomplete = False; thermal = 0.0; mech = False
    for r in rows:
        c = r.get('count'); me = r.get('mw_each')
        if c is None or me is None:
            if r.get('mmbtu') and c is not None:
                thermal += c * r['mmbtu']
            incomplete = True; continue
        cnt += c; mw += c * me
        if r.get('mw_src') == 'bhp-mech' or r.get('unit') == 'bhp': mech = True
    return cnt, round(mw, 3), incomplete, thermal, mech

def process(reg):
    d = json.load(open(os.path.join(RAW, reg + '.json')))
    rec = {'registration': reg}
    if d.get('error') and not d['pages']:
        rec.update(method='unreadable', confidence='none', note=d['error'])
        return rec, [], []
    md = metadata(d, reg)
    rec.update(md)
    full = '\n'.join(p['text'] for p in d['pages'])
    rec['hour_limits'], rec['fuel_limits'] = limits(full)
    st = stated_totals(full)
    rec['stated_total_mw'] = st[0][0] if st else ''
    rec['stated_total_ctx'] = st[0][1] if st else ''
    trows = table_rows_for_permit(d)
    sec, _ = section_text(d)
    prows = prose_rows(sec) if sec else []
    tc, tmw, tinc, tth, tmech = summarise(trows)
    pc, pmw, pinc, _, pmech = summarise(prows)
    rec.update(table_count=tc if trows else '', table_mw=tmw if trows else '', table_incomplete=tinc,
               prose_count=pc if prows else '', prose_mw=pmw if prows else '', prose_incomplete=pinc,
               thermal_mmbtu=tth, bhp_only=tmech)
    # decide
    if trows and prows:
        if tc == pc and abs(tmw - pmw) <= 0.02 * max(tmw, 0.001):
            method, cnt, mw, conf = 'both-agree', tc, tmw, 'high'
        else:
            method, cnt, mw, conf = 'both-disagree', tc, tmw, 'low'
    elif trows:
        method, cnt, mw, conf = 'table', tc, tmw, ('medium' if not tinc else 'low')
    elif prows:
        method, cnt, mw, conf = 'prose', pc, pmw, ('medium' if not pinc else 'low')
    else:
        method, cnt, mw, conf = 'unreadable', '', '', 'none'
    if rec['stated_total_mw'] != '' and mw != '' and abs(float(rec['stated_total_mw']) - mw) <= 0.02 * max(mw, 0.001):
        conf = 'high'
    rec.update(method=method, generator_count=cnt, total_standby_mw=mw, confidence=conf,
               section_chars=len(sec))
    return rec, trows, prows, sec

if __name__ == '__main__':
    regs = sorted(os.path.basename(f)[:-5] for f in glob.glob(os.path.join(RAW, '*.json')))
    recs = []; allrows = []
    os.makedirs(os.path.join(OUT, 'digest'), exist_ok=True)
    for reg in regs:
        res = process(reg)
        rec = res[0]; trows = res[1]; prows = res[2]; sec = res[3] if len(res) > 3 else ''
        recs.append(rec)
        for r in trows:
            allrows.append(dict(registration=reg, **{k: v for k, v in r.items()}))
        # digest for manual read
        with open(os.path.join(OUT, 'digest', reg + '.txt'), 'w') as f:
            f.write(f"=== {reg} | {rec.get('facility_name','')} | {rec.get('permittee','')} | {rec.get('permit_date','')}\n")
            f.write(f"method={rec.get('method')} table={rec.get('table_count')}/{rec.get('table_mw')} prose={rec.get('prose_count')}/{rec.get('prose_mw')} stated={rec.get('stated_total_mw')}\n")
            f.write("--- TABLE ROWS\n")
            for r in trows:
                f.write(f"  [{r['section'][:30]}] ref={r['ref'][:40]!r} n={r['count']}({r['count_src']},ref={r['ref_count']}) kw={r['kw']} bhp={r['bhp']} mmbtu={r['mmbtu']} mw_each={r['mw_each']} {r['kind']} :: {r['desc'][:90]}\n")
            f.write("--- PROSE ROWS\n")
            for r in prows:
                f.write(f"  n={r['count']} val={r['val']}{r['unit']} ({r['count_src']})\n")
            f.write("--- SECTION TEXT\n" + sec + "\n")
    keys = ['registration', 'registration_in_text', 'registration_match', 'permittee', 'facility_name', 'site_street', 'site_city_line', 'site_county', 'location_county',
            'permit_date', 'amendment', 'supersedes', 'supersedes_date', 'site_same_as_mailing', 'generator_count', 'total_standby_mw', 'method', 'confidence',
            'table_count', 'table_mw', 'table_incomplete', 'prose_count', 'prose_mw', 'prose_incomplete', 'stated_total_mw', 'stated_total_ctx',
            'thermal_mmbtu', 'bhp_only', 'hour_limits', 'fuel_limits', 'section_chars', 'note']
    with open(os.path.join(OUT, 'auto_reread.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore'); w.writeheader()
        for r in recs: w.writerow({k: r.get(k, '') for k in keys})
    rk = ['registration', 'source', 'section', 'ref', 'desc', 'cap', 'count', 'count_src', 'ref_count', 'kw', 'bhp', 'mmbtu', 'mw_stated', 'mw_each', 'mw_src', 'kind', 'fuel', 'each', 'cap_src']
    with open(os.path.join(OUT, 'auto_rows.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=rk, extrasaction='ignore'); w.writeheader()
        for r in allrows: w.writerow({k: r.get(k, '') for k in rk})
    from collections import Counter
    print(Counter(r.get('method') for r in recs)); print(Counter(r.get('confidence') for r in recs))
