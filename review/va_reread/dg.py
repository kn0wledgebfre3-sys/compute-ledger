import sys,re
for reg in sys.argv[1:]:
    t=open(f'digest/{reg}.txt').read()
    head,sec=t.split('--- SECTION TEXT\n')
    print(head.rstrip())
    lines=[l for l in sec.split('\n') if re.search(r'\d|generator|gen-?set|engine|Equipment|Located|Building|each|OR\b|or\b',l,re.I)]
    print('--- SECTION (compact)'); print('\n'.join(lines)[:7000])
    print('#################')
