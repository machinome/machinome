import os, sys
ROOT = os.getcwd(); sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import order as O
from tools.generate_running_corpus import run_machine, document_of
doc = document_of('ShiftedCarry')
def probe(label, dt, duration, steps=20):
    script = [{'tick':1,'move':{'input':'crank','by':2.0,'duration':duration},'handle':'h0'},
              {'tick':8,'move':{'input':'shift','by':1.0,'duration':0.2},'handle':'h1'},
              {'tick':14,'move':{'input':'crank','by':2.0,'duration':duration},'handle':'h2'}]
    entry = {'name':'ShiftedCarry','dt':dt,'steps':steps,'script':script}
    prod = run_machine(entry)
    with O.listing():
        got = run_machine(entry)
    bad = O.compare(prod, got)
    gates = O.gate_crossings(doc, prod)
    xs = [(t['tick'], c['coordinate'], c['primitive'], round(c['t'],4)) for t in prod for c in t['crossings']]
    print(f'{label}: dt={dt} duration={duration} steps={steps} -> {len(bad)} disagreement(s), '
          f'{len(gates)} in-block gate crossing(s) inside a tick, crossings={xs}')
    if bad: print('    first:', bad[0])
    print('    final higher.turn: producer', prod[-1]['bank']['higher.turn'], '/ listing', got[-1]['bank']['higher.turn'])
probe('committed', 0.05, 0.2)
probe('chosen   ', 0.05, 0.3)
probe('alt 0.4  ', 0.05, 0.4)
probe('alt 0.15 ', 0.05, 0.15)
# the briefing's dt = 1.0 claim, one crank, no shift
entry = {'name':'ShiftedCarry','dt':1.0,'steps':2,'script':[
    {'tick':1,'move':{'input':'crank','by':2.0,'duration':1.0},'handle':'h0'}]}
prod = run_machine(entry)
with O.listing():
    got = run_machine(entry)
print('dt=1.0, crank by 2.0 over 1.0 s: producer', {k: round(v,6) for k,v in prod[0]['bank'].items()})
print('                                  listing ', {k: round(v,6) for k,v in got[0]['bank'].items()})
