"""M2: the face-and-edge side test against the classifier readings of M1, and
the sketched witness end to end on the captured pair."""
import json, sys, time, collections
sys.path.insert(0, sys.argv[3])
import side as sketch
import machinome.engine.brep as brep
S = sys.argv[1]
shell = brep.read_brep(S + '/shell.brep'); screw = brep.read_brep(S + '/screw.brep')
points = json.load(open(sys.argv[2]))
for name, shape in (('screw', screw), ('shell', shell)):
    b = sketch.Boundary(brep._solids(shape)[0])
    t = time.perf_counter()
    for p in points: p[name + '_side2'] = b.side(p['xyz'])
    dt = time.perf_counter() - t
    print(f'{name} side test (faces and edges): {dt/len(points)*1e3:.2f} ms each;',
          dict(collections.Counter(str(p[name + "_side2"]) for p in points)))
truth = [(p['screw_side2'], p['screw_in']) for p in points]
print('screw side2 vs classifier', collections.Counter(truth))
s = [p for p in points if 'shell_in' in p]
print('shell side2 vs classifier (M1 sample)', collections.Counter((p['shell_side2'], p['shell_in']) for p in s))
both = [p for p in points if p['screw_side2'] not in ('OUT', 'ON') and p['shell_side2'] not in ('OUT', 'ON')]
print('points passing both side tests', len(both), collections.Counter((p['shell_side2'], p['screw_side2']) for p in both))
t = time.perf_counter()
w = sketch.witness(shell, screw)
print('sketch witness', w, f'{time.perf_counter() - t:.2f} s', sketch.STATS)
sketch.STATS.clear(); t = time.perf_counter()
w = sketch.witness(screw, shell)
print('sketch witness, operands swapped', w, f'{time.perf_counter() - t:.2f} s', sketch.STATS)
