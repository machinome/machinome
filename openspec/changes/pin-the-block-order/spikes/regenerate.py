"""Would the new script change anything but its own entry?"""
import json, os, sys
ROOT = os.getcwd(); sys.path.insert(0, ROOT)
import tools.generate_running_corpus as gen

new = []
for entry in gen.CORPUS:
    if entry['name'] == 'ShiftedCarry':
        entry = dict(entry, script=[
            {'tick': 1, 'move': {'input': 'crank', 'by': 2.0,
                                 'duration': 0.3}, 'handle': 'h0'},
            {'tick': 8, 'move': {'input': 'shift', 'by': 1.0,
                                 'duration': 0.2}, 'handle': 'h1'},
            {'tick': 14, 'move': {'input': 'crank', 'by': 2.0,
                                  'duration': 0.3}, 'handle': 'h2'}])
    new.append(entry)
gen.CORPUS = tuple(new)
built = gen.build()
old = json.load(open(os.path.join(ROOT, 'tests', 'running-corpus.json')))
print('top-level keys identical:', sorted(built) == sorted(old))
for key in ('generated_by', 'corpus', 'tolerance'):
    print(f'  {key}: {built[key] == old[key]}')
key = lambda e: (e['name'], e['dt'], e['steps'])
a = {key(e): e for e in old['machines']}
b = {key(e): e for e in built['machines']}
print('removed:', [k for k in a if k not in b])
print('added  :', [k for k in b if k not in a])
print('changed:', [k for k in a if k in b and a[k] != b[k]])
print('order preserved:', [key(e) for e in old['machines']] ==
      [key(e) for e in built['machines']])
print('ticks:', sum(len(e['ticks']) for e in built['machines']),
      'was', sum(len(e['ticks']) for e in old['machines']))
