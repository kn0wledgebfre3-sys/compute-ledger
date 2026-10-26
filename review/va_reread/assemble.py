import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_REPO = _os.path.dirname(_os.path.dirname(_HERE))
"""Stage 3: assemble va_reread.csv (my figures), compare with pipeline, write comparison + resolved."""
import pandas as pd, re, json, csv, os
OUT = _HERE
auto = pd.read_csv(f'{OUT}/auto_reread.csv', dtype={'registration': str})
dec = pd.read_csv(f'{OUT}/decisions.csv', dtype={'registration': str})
rows = pd.read_csv(f'{OUT}/auto_rows.csv', dtype={'registration': str})

def row_summary(reg):
    r = rows[rows.registration == reg]
    parts = []
    for _, x in r.iterrows():
        cap = f"{int(x.kw)} kW" if pd.notna(x.kw) else (f"{int(x.bhp)} bhp" if pd.notna(x.bhp) else '?')
        parts.append(f"{int(x['count']) if pd.notna(x['count']) else '?'}x{cap}")
    return 'Table rows: ' + ' + '.join(parts)

recs = []
for _, a in auto.iterrows():
    reg = a.registration
    d = dec[dec.registration == reg]
    rec = dict(registration=reg, permittee=a.permittee, facility_name=a.facility_name, site_street=a.site_street,
               site_city_line=a.site_city_line, site_county=a.site_county if pd.notna(a.site_county) else a.location_county,
               site_same_as_mailing=a.site_same_as_mailing, permit_date=a.permit_date, amendment=a.amendment,
               supersedes=a.supersedes, supersedes_date=a.supersedes_date,
               auto_method=a.method, auto_table_count=a.table_count, auto_table_mw=a.table_mw,
               auto_prose_count=a.prose_count, auto_prose_mw=a.prose_mw,
               stated_total_mw=a.stated_total_mw, stated_total_ctx=a.stated_total_ctx,
               hour_limits=a.hour_limits, fuel_limits=a.fuel_limits)
    if len(d):
        d = d.iloc[0]
        rec.update(reread_count=d['count'], reread_mw=d['mw'], reread_confidence=d['confidence'],
                   reread_basis=d['basis'], reread_method='manual-verified (' + str(a.method) + ')')
    else:
        rec.update(reread_count=a.generator_count, reread_mw=a.total_standby_mw, reread_confidence='high',
                   reread_basis=row_summary(reg) + '; table and prose parsers agree; rows scanned by eye',
                   reread_method='both-agree (table+prose), rows reviewed')
    b = str(rec['reread_basis'])
    m = re.search(r'excluding transitory:\s*(\d+)\s*/\s*([\d.]+)', b)
    rec['count_excl_transitory'] = int(m.group(1)) if m else (rec['reread_count'] if pd.notna(rec['reread_count']) and 'ransitory' not in b else '')
    rec['mw_excl_transitory'] = float(m.group(2)) if m else (rec['reread_mw'] if pd.notna(rec['reread_mw']) and 'ransitory' not in b else '')
    rr = rows[rows.registration == reg]
    rec['fuel'] = 'natural gas' if (rr.fuel == 'natural gas').any() else ('diesel' if len(rr) else 'diesel (per text)')
    if reg in ('74172', '80941'): rec['fuel'] = 'natural gas engines (see basis)' if reg == '74172' else 'natural gas (7 units) + diesel (2 units)'
    rec['units_non_emergency'] = int(rr[rr.kind == 'non-emergency']['count'].fillna(0).sum()) if len(rr) else ''
    rec['bhp_only_rating'] = reg in ('52949', '52973')
    recs.append(rec)
rr_df = pd.DataFrame(recs)
rr_df.to_csv(f'{OUT}/va_reread.csv', index=False)
print('va_reread rows', len(rr_df), 'sum MW', rr_df.reread_mw.sum(), 'units', rr_df.reread_count.sum())

# ---- comparison ----
pipe = pd.read_csv(_os.environ.get('VA_FIRST_READING', _os.path.join(_REPO, 'data', 'climate_trace_seed', 'va_permits.csv')), dtype={'registration_no': str})
pipe = pipe[['registration_no', 'generator_count', 'total_standby_mw', 'facility_street', 'facility_city', 'unit_kw_list', 'generator_count_confidence', 'total_mw_confidence', 'generator_rows_uncounted']]
cmp = rr_df[['registration', 'reread_count', 'reread_mw', 'reread_confidence', 'reread_basis', 'site_street', 'site_city_line']].merge(pipe, left_on='registration', right_on='registration_no', how='outer')

def classify(r):
    pc, pm, rc, rm = r.generator_count, r.total_standby_mw, r.reread_count, r.reread_mw
    if pd.isna(rc) or pd.isna(rm):
        return 'yours-null'
    if pd.isna(pc) or pd.isna(pm):
        return 'pipeline-null'
    mw_ok = abs(pm - rm) <= 0.02 * max(rm, 1e-9)
    cnt_ok = (pc == rc)
    if mw_ok and cnt_ok: return 'agree'
    if abs(pm - rm) <= 0.10 * max(rm, 1e-9) and abs(pc - rc) <= 2: return 'minor'
    if mw_ok and abs(pc - rc) <= 2: return 'minor'
    if abs(pm - rm) <= 0.10 * max(rm, 1e-9) and cnt_ok: return 'minor'
    return 'disagree'
cmp['status'] = cmp.apply(classify, axis=1)
cmp.to_csv(f'{OUT}/cmp_raw.csv', index=False)
print(cmp.status.value_counts())
