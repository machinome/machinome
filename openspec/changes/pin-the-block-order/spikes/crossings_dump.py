import json, os, sys
ROOT = os.getcwd(); sys.path.insert(0, ROOT)
from tools.generate_running_corpus import run_machine
base = [{'tick':1,'move':{'input':'crank','by':2.0,'duration':0.2},'handle':'h0'},
        {'tick':8,'move':{'input':'shift','by':1.0,'duration':0.2},'handle':'h1'},
        {'tick':14,'move':{'input':'crank','by':2.0,'duration':0.2},'handle':'h2'}]
cand = [{'tick':1,'move':{'input':'crank','by':2.0,'duration':0.3},'handle':'h0'},
        {'tick':8,'move':{'input':'shift','by':1.0,'duration':0.2},'handle':'h1'},
        {'tick':14,'move':{'input':'crank','by':2.0,'duration':0.3},'handle':'h2'}]
for label, script in (('committed 0.2', base), ('candidate 0.3', cand)):
    ticks = run_machine({'name':'ShiftedCarry','dt':0.05,'steps':20,'script':script})
    print('===', label)
    for t in ticks:
        if t['crossings'] or t['stops']:
            print(' tick', t['tick'], 'crossings=', [(c['coordinate'],c['primitive'],c['level'],round(c['t'],6)) for c in t['crossings']], 'stops=', len(t['stops']))
    print(' banks:')
    for t in ticks:
        print('   ', t['tick'], {k: round(v,6) for k,v in sorted(t['bank'].items())})
