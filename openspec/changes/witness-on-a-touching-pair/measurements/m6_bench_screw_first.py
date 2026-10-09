"""Instrument the witness on a captured pair: where the candidates go."""
import sys, time, collections
import machinome.engine.brep as brep
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
S = sys.argv[1]
first = brep.read_brep(S + '/screw.brep'); second = brep.read_brep(S + '/shell.brep')  # swapped: the cheaper classifier first
print('faces', len(brep._faces(first)), len(brep._faces(second)), 'volumes', round(brep.solid_volume(first), 3), round(brep.solid_volume(second), 3))
t = time.perf_counter(); print('distance', brep._distance(first, second), round(time.perf_counter() - t, 3), 's')
stats = collections.Counter(); timing = collections.Counter()
_cls = BRepClass3d_SolidClassifier
class Counting:
    def __init__(self, solid): self.c = _cls(solid)
    def Perform(self, p, tol):
        t = time.perf_counter(); self.c.Perform(p, tol); timing['classify'] += time.perf_counter() - t; stats['classify'] += 1
    def Rejected(self): return self.c.Rejected()
    def State(self): return self.c.State()
brep.BRepClass3d_SolidClassifier = Counting
_ri = brep._resolved_interior
def ri(solid, point):
    t = time.perf_counter()
    try: return _ri(solid, point)
    finally: timing['resolve'] += time.perf_counter() - t; stats['resolve'] += 1
brep._resolved_interior = ri
_sec = brep.BRepAlgoAPI_Section
t0 = time.perf_counter()
w = brep._false_empty_witness(first, second)
total = time.perf_counter() - t0
print('witness', w, 'total', round(total, 1), 's')
print('stats', dict(stats)); print('timing', {k: round(v, 1) for k, v in timing.items()})
