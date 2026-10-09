import sys, time, math
from itertools import product
import machinome.engine.brep as brep
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_IN
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
S = sys.argv[1]
shell = brep.read_brep(S + '/shell.brep'); screw = brep.read_brep(S + '/screw.brep')
section = BRepAlgoAPI_Section(brep._copy(shell), brep._copy(screw), False); section.Build()
edges = brep._edges(section.Shape())
spans = []
for s in (shell, screw):
    lo, hi = brep.bounds(s); spans += [d for d in (hi[0]-lo[0], hi[1]-lo[1], hi[2]-lo[2]) if d > 0]
scale = min(spans); steps = (scale*1e-4, scale*1e-3, scale*1e-2)
dirs = [tuple(v/math.sqrt(sum(o*o for o in d)) for v in d) for d in product((-1,0,1), repeat=3) if any(d)]
c = BRepClass3d_SolidClassifier(brep._solids(shell)[0])
for st in steps:
    pts = []
    for e in edges[:8]:
        if brep._length(e) <= 0: continue
        for fr in (.25,.5,.75):
            at = brep._position_at(e, fr)
            for d in dirs: pts.append(gp_Pnt(*(at[i] + st*d[i] for i in range(3))))
    sample = pts[::6]
    t = time.perf_counter(); n_in = 0
    for p in sample:
        c.Perform(p, 0.0); n_in += (not c.Rejected() and c.State() == TopAbs_IN)
    dt = time.perf_counter() - t
    print(f'step {st:.4g} mm: {len(pts)} points, shell classify {dt/len(sample)*1e3:.0f} ms each, IN {n_in}/{len(sample)}; projected {dt/len(sample)*len(pts):.0f} s for the step')
# margins: how long does _resolved_interior cost per point on the shell
pts = []
for e in edges[:8]:
    for fr in (.25,.5,.75):
        at = brep._position_at(e, fr); pts.append(gp_Pnt(*(at[i] + steps[2]*dirs[0][i] for i in range(3))))
t = time.perf_counter(); res = [brep._resolved_interior(brep._solids(shell)[0], p) for p in pts]; dt = time.perf_counter() - t
print(f'resolved_interior on shell: {dt/len(pts)*1e3:.1f} ms per point; resolved {sum(r is not None for r in res)}/{len(pts)}')
