import json, os, sys
ROOT = os.getcwd(); sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tools.generate_running_corpus import _selection, _member_of, document_of, run_machine
from order import in_block_gates

doc = document_of('ShiftedCarry')
prog = doc['program']
bindings = {i['name']: i['expression'] for i in doc.get('bindings', ())}
print('edge kinds:', [(i, e['kind'], e['gives']) for i, e in enumerate(prog['edges'])])
gives, selectors = _selection(prog, bindings)
print('gives:', gives)
print('selectors:', selectors)
print('gates:', json.dumps({str(k): sorted(v) for k, v in in_block_gates(doc).items()}, indent=1))
for i, e in enumerate(prog['edges']):
    for plan in e.get('plans') or ():
        if plan is None: continue
        for j in plan['jumps']:
            print(' edge', i, e['gives'], 'jump', j['name'], j['primitive'], '|', j['level'])
cand = {'name':'ShiftedCarry','dt':0.05,'steps':20,'script':[
  {'tick':1,'move':{'input':'crank','by':2.0,'duration':0.3},'handle':'h0'},
  {'tick':8,'move':{'input':'shift','by':1.0,'duration':0.2},'handle':'h1'},
  {'tick':14,'move':{'input':'crank','by':2.0,'duration':0.3},'handle':'h2'}]}
ticks = run_machine(cand)
for t in ticks:
    for c in t['crossings']:
        print('tick', t['tick'], c, 'member=', _member_of(prog, c['coordinate']))
