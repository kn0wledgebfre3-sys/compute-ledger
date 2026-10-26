import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_REPO = _os.path.dirname(_os.path.dirname(_HERE))
"""Stage 4: comparison with pipeline, resolution notes, resolved table."""
import pandas as pd, re
from collections import Counter
OUT = _HERE
rr = pd.read_csv(f'{OUT}/va_reread.csv', dtype={'registration': str})
cmp = pd.read_csv(f'{OUT}/cmp_raw.csv', dtype={'registration': str, 'registration_no': str})
rows = pd.read_csv(f'{OUT}/auto_rows.csv', dtype={'registration': str})

def pipe_groups(s):
    out = []
    if not isinstance(s, str): return out
    for part in s.split(';'):
        m = re.match(r'\s*(\d+)\s*x\s*([\d.]+)(?:-([\d.]+))?\s*kW\s*(.*)', part)
        if m: out.append((int(m.group(1)), float(m.group(2)), m.group(4).strip()))
    return out

def my_groups(reg):
    r = rows[rows.registration == reg]
    return [(int(x['count']) if pd.notna(x['count']) else None, float(x.kw) if pd.notna(x.kw) else None) for _, x in r.iterrows()]

def fmt(groups):
    return ', '.join(f"{c}x{int(k) if k else '?'}" for c, k in groups)

def diagnose(reg, r):
    pg = pipe_groups(r.unit_kw_list)
    mg = my_groups(reg)
    notes = []
    years = [c for c, k, _ in pg if 1900 <= c <= 2030]
    if years:
        notes.append(f"parsed model years/dates {years} as unit counts")
    small = [(c, k) for c, k, _ in pg if k <= 160]
    if small:
        notes.append(f"included fire-pump/small engines {fmt(small)}")
    if mg:
        pm = Counter((c, k) for c, k, _ in pg)
        mm = Counter((c, k) for c, k in mg if c is not None and k is not None)
        missing = list((mm - pm).elements())
        extra = list((pm - mm).elements())
        if mg and mg[0] in missing and mg[0][0] is not None:
            notes.append(f"dropped the first equipment-table row ({fmt([mg[0]])})")
            missing = [g for g in missing if g != mg[0]] + ([mg[0]] * (missing.count(mg[0]) - 1) if missing.count(mg[0]) > 1 else [])
        if missing:
            notes.append(f"missed rows {fmt(missing[:8])}{' ...' if len(missing) > 8 else ''}")
        if extra:
            notes.append(f"extra/misread rows {fmt(extra[:6])}{' ...' if len(extra) > 6 else ''}")
    else:
        notes.append(f"captured only [{str(r.unit_kw_list)[:120]}]" if isinstance(r.unit_kw_list, str) else "no units captured")
    return '; '.join(notes) if notes else 'differs from text'

SPECIAL = {
    '52221': "pipeline took the model year in parentheses '(1987)', '(2005)' etc. as the unit count of the following row (1987 x 1600 kW ...), giving ~63,000 MW; permit lists 16 single units",
    '52403': "pipeline took model years '(2020)', '(2012)', '(2017)' as unit counts (2020 x 2446 kW ...), giving ~9,400 MW; permit lists 30 units",
    '73860': "pipeline read '2015' (from 'December 15, 2015' permit date) as a count for the footnote's '2,500 ekW' removed-unit mention, giving ~5,200 MW; also dropped the first row (26x2750); permit lists 95 units",
    '74262': "pipeline double-counted BYEG1-BYEG120 which the permit lists twice (2025 and 2023 permit dates) with a footnote 'Only 120 total units'; my parsers made the same error before the footnote was read",
    '74197': "pipeline counted the 65 units twice (65 + 32) and used the 2,500 ekW prime rating; permit says '2,500 ekW (2,250 ekW standby)' so standby rating 2,250 used",
    '74216': "same count but pipeline assigned '<=560 ekW' (the single TBD house unit) to 129 units; permit gives 2,800/1,750/2,750/1,750 kW for the groups",
    '74341': "pipeline null; permit lists 1,332 x 625 ekW Volvo Penta gen-sets (my parsers also first read '(1,332)' as 1 because of the comma)",
    '74085': "permit uses '(N units)' at the end of each description ('(90 units)'); pipeline (and my automated parsers) read each as 1 unit",
    '74107': "permit uses '(N units)' style; pipeline mis-assigned counts and kW across rows",
    '74163': "pipeline dropped the 130 Volvo Penta 625 ekW units (read as '25 x 156 kW')",
    '74323': "pipeline dropped first row (26x2750) and read '130 x 1000 kW' from the ref range '55 through 130'",
    '74129': "pipeline read the fuel-tank rows ('Sixty-nine (69) ... storage tanks', 'AST 24 through 92') as 87 x 600 kW generators",
    '74171': "pipeline read '87 x 750 kW' from the ref range '66 through 87' next to the 750 kW row",
    '74052': "pipeline mis-assigned kW across rows (13x2000 should be 13x2500) and invented '59 x 2000' from the ref range '21 through 59'",
    '74115': "pipeline read '44 x 2000' from ref text and dropped the first row (21x2500)",
    '74288': "pipeline dropped first row (2x400) and added a spurious '36 x 2750' (from ref/text numbers)",
    '74114': "pipeline dropped the 73-unit prior row and read de-rate text as extra 1687.5 kW units",
    '73355': "pipeline included Generators 1R/4R (2x1825 kW) that the permit lists under 'Equipment Being Replaced'",
    '74284': "both read 77 units; pipeline used the 560 ekW figure, I used 625 ekW (permit lists both ratings for the Volvo units; 625 ekW is listed first) - ambiguous, 4.6% difference",
    '52949': "pipeline null; permit gives bhp only - kWe inferred from identical models in sibling Microsoft permits (medium confidence)",
    '52973': "pipeline null; permit gives bhp only - kWe inferred from identical models in sibling Microsoft permits (medium confidence)",
    '5': "not a permit: 5.pdf is an HTML 'Access Denied' page; registration '5' does not exist in the pipeline list either",
    '74331': "pipeline shows download_failed (SourceMovedError) for Westfax 4-5A; no PDF in pdfs_va, so neither reader could read it",
}

recs = []
for _, r in cmp.iterrows():
    reg = r.registration if isinstance(r.registration, str) else r.registration_no
    rrr = rr[rr.registration == reg]
    basis = rrr.iloc[0].reread_basis if len(rrr) else ''
    conf = rrr.iloc[0].reread_confidence if len(rrr) else 'none'
    st = r.status
    if st == 'agree':
        note = 'agree within 2%; reread verified against text'
        rc, rm, rconf = r.reread_count, r.reread_mw, 'high'
    elif st == 'yours-null':
        note = SPECIAL.get(reg, 'no readable permit')
        rc, rm, rconf = None, None, 'none'
    elif st == 'pipeline-null':
        note = 'pipeline null (' + (SPECIAL.get(reg) or 'no extraction') + '); reread figure from permit text: ' + str(basis)[:200]
        rc, rm, rconf = r.reread_count, r.reread_mw, conf
    else:
        diag = SPECIAL.get(reg) or diagnose(reg, r)
        note = f"REREAD IS RIGHT ({int(r.reread_count)} units / {r.reread_mw:g} MW, text-verified: {str(basis)[:170]}). Pipeline {int(r.generator_count)}/{r.total_standby_mw:g}: {diag}"
        rc, rm, rconf = r.reread_count, r.reread_mw, conf
    recs.append(dict(registration=reg, status=st, pipeline_count=r.generator_count, pipeline_mw=r.total_standby_mw,
                     reread_count=r.reread_count, reread_mw=r.reread_mw, resolved_count=rc, resolved_mw=rm,
                     resolution_note=note, resolved_confidence=rconf))
cm = pd.DataFrame(recs).sort_values('registration', key=lambda s: s.astype(int))
cm.to_csv(f'{OUT}/va_comparison.csv', index=False)

# resolved table
res = rr.merge(cm[['registration', 'status', 'pipeline_count', 'pipeline_mw', 'resolved_count', 'resolved_mw', 'resolved_confidence', 'resolution_note']], on='registration', how='outer')
res['generator_count'] = res.resolved_count
res['total_standby_mw'] = res.resolved_mw
res['basis'] = res.reread_basis
cols = ['registration', 'facility_name', 'permittee', 'site_street', 'site_city_line', 'site_county', 'site_same_as_mailing', 'permit_date', 'amendment', 'supersedes_date',
        'generator_count', 'total_standby_mw', 'count_excl_transitory', 'mw_excl_transitory', 'units_non_emergency', 'fuel', 'bhp_only_rating',
        'resolved_confidence', 'basis', 'status', 'pipeline_count', 'pipeline_mw', 'hour_limits', 'fuel_limits', 'stated_total_mw']
res = res[cols].sort_values('registration', key=lambda s: s.astype(int))
res.to_csv(f'{OUT}/va_resolved.csv', index=False)
print(cm.status.value_counts())
print('fleet MW pipeline:', cmp.total_standby_mw.sum(), 'reread:', rr.reread_mw.sum(), 'resolved:', res.total_standby_mw.sum())
print('units pipeline:', cmp.generator_count.sum(), 'resolved:', res.generator_count.sum())
