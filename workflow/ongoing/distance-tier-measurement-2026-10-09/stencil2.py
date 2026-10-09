import sys, time, math
from itertools import product
import machinome.engine.brep as brep
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_IN
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.GeomAbs import GeomAbs_SurfaceType
from OCP.BRepAdaptor import BRepAdaptor_Surface
S = sys.argv[1]
shell = brep.read_brep(S + '/shell.brep'); screw = brep.read_brep(S + '/screw.brep')
for name, s in (('shell', shell), ('screw', screw)):
    kinds = {}
    for f in brep._faces(s):
        k = BRepAdaptor_Surface(f).GetType().name; kinds[k] = kinds.get(k, 0) + 1
    print(name, 'face types', kinds, 'bounds', [tuple(round(v, 1) for v in b) for b in brep.bounds(s)])
# the same stencil points the witness walks
left, right = brep._copy(shell), brep._copy(screw)
section = BRepAlgoAPI_Section(left, right, False); section.Build()
edges = brep._edges(section.Shape()); print('section edges', len(edges))
spans = []
for s in (shell, screw):
    lo, hi = brep.bounds(s); spans += [d for d in (hi[0]-lo[0], hi[1]-lo[1], hi[2]-lo[2]) if d > 0]
scale = min(spans); steps = (scale*1e-4, scale*1e-3, scale*1e-2)
dirs = [tuple(v/math.sqrt(sum(o*o for o in d)) for v in d) for d in product((-1,0,1), repeat=3) if any(d)]
points = []
for e in edges[:8]:
    if brep._length(e) <= 0: continue
    for fr in (.25,.5,.75):
        at = brep._position_at(e, fr)
        for st in steps:
            for d in dirs: points.append(gp_Pnt(*(at[i] + st*d[i] for i in range(3))))
print('stencil points', len(points), 'scale', round(scale, 3))
for name, s in (('shell', shell), ('screw', screw)):
    for tol in (0.0, 1e-7):
        c = BRepClass3d_SolidClassifier(brep._solids(s)[0]); t = time.perf_counter(); n_in = 0
        for p in points[:200]:
            c.Perform(p, tol); n_in += (not c.Rejected() and c.State() == TopAbs_IN)
        dt = (time.perf_counter() - t) / 200
        print(f'{name} tol={tol}: {dt*1e3:.1f} ms per classification, IN {n_in}/200')
# how many points are IN the screw at all (the cheap solid first)
c = BRepClass3d_SolidClassifier(brep._solids(screw)[0]); t = time.perf_counter(); n_in = 0
for p in points:
    c.Perform(p, 0.0); n_in += (not c.Rejected() and c.State() == TopAbs_IN)
print('screw first: all', len(points), 'points in', round(time.perf_counter() - t, 2), 's; IN screw:', n_in)
