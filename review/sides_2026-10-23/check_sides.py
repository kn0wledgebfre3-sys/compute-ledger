import json,csv,re,sys
S='review/sides_2026-10-23/'
B={e['id']:e for e in json.load(open(S+'entries_before.json'))}
A={e['id']:e for e in json.load(open(S+'entries_after.json'))}
notes=open(S+'notes.md').read() if __import__('os').path.exists(S+'notes.md') else ''
rows=list(csv.DictReader(open(S+'company_in_record.csv')))
P=[]
if set(A)!=set(B): P.append(f'entry ids differ: missing {set(B)-set(A)}, extra {set(A)-set(B)}')
num=lambda t: sorted(re.findall(r'\d[\d,\.]*\d|\d',t))
for i,b in B.items():
    a=A.get(i)
    if not a: continue
    for k in b:
        if k not in ('record','claim','record_sources','claim_sources','gap') and a.get(k)!=b[k]: P.append(f'{i}: field {k} changed')
    nb=num(b['record']+' '+b['claim']); na=num(a['record']+' '+a['claim'])
    for n in set(nb):
        if nb.count(n)>na.count(n): P.append(f'{i}: number {n} appears fewer times after ({na.count(n)} vs {nb.count(n)})')
    us=lambda e:sorted(s['url'] for s in e.get('record_sources',[])+e.get('claim_sources',[]))
    if set(us(b))-set(us(a)): P.append(f'{i}: sources dropped {set(us(b))-set(us(a))}')
for r in rows:
    a=A.get(r['entry_id']); v=r['value_as_published']
    if not a: continue
    if v not in a['claim'] and v not in notes: P.append(f"{r['entry_id']}: {v!r} not in the claim (and not explained in notes)")
    if v in a['record'] and v not in notes: P.append(f"{r['entry_id']}: {v!r} still in the record (and not explained in notes)")
for p in P: print(p)
print(len(P),'problems')
