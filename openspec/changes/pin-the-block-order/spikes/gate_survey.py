import json, os, sys
ROOT = os.getcwd(); sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from order import gate_crossings
fixture = json.load(open(os.path.join(ROOT,'tests','running-corpus.json')))
for entry in fixture['machines']:
    found = gate_crossings(entry['document'], entry['ticks'])
    if found:
        print(entry['name'], entry['dt'], '->', [(t, c['coordinate'], c['primitive'], c['t']) for t, c in found])
print('machines supplying the feature today:',
      [e['name'] for e in fixture['machines'] if gate_crossings(e['document'], e['ticks'])])
