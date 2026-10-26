import sys,json,re
reg=sys.argv[1]; pages=[int(x) for x in sys.argv[2:]]
d=json.load(open(f'raw/{reg}.json'))
if not pages:
    # locate pages
    for p in d['pages']:
        if re.search(r'Equipment List|Equipment to be|Previously Permitted|Emission Units|Equipment at this facility',p['text']): print('candidate page',p['i'])
    sys.exit()
for i in pages:
    print(f'=========== page {i}'); print(d['pages'][i]['text'])
