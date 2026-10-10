import sys, time
import machinome.engine.brep as brep
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.ShapeAnalysis import ShapeAnalysis_ShapeTolerance
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_IN, TopAbs_OUT
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE, TopAbs_VERTEX, TopAbs_SHELL, TopAbs_WIRE
S = sys.argv[1]
shell = brep.read_brep(S + '/shell.brep')
solid = brep._solids(shell)[0]
def count(kind):
    n = 0; ex = TopExp_Explorer(solid, kind)
    while ex.More(): n += 1; ex.Next()
    return n
print('shells', count(TopAbs_SHELL), 'wires', count(TopAbs_WIRE), 'edges', count(TopAbs_EDGE), 'vertices', count(TopAbs_VERTEX))
print('valid', BRepCheck_Analyzer(solid).IsValid())
tol = ShapeAnalysis_ShapeTolerance(); print('tolerance max/avg', tol.Tolerance(solid, 1), tol.Tolerance(solid, 0))
lo, hi = brep.bounds(solid); centre = gp_Pnt(*[(a+b)/2 for a, b in zip(lo, hi)])
far = gp_Pnt(hi[0] + 100, hi[1] + 100, hi[2] + 100)
c = BRepClass3d_SolidClassifier(solid)
for name, p in (('centre', centre), ('far', far), ('near corner', gp_Pnt(lo[0] + 0.01, lo[1] + 0.01, lo[2] + 0.01))):
    t = time.perf_counter(); c.Perform(p, 0.0); dt = time.perf_counter() - t
    print(f'{name}: {dt*1e3:.1f} ms state {c.State()}')
# a fresh classifier per call, as the witness does per pair
t = time.perf_counter(); c2 = BRepClass3d_SolidClassifier(solid); c2.Perform(centre, 0.0); print('fresh classifier + centre', round((time.perf_counter()-t)*1e3, 1), 'ms')
# per-face cost: time each face's parametric bounds
from OCP.BRepTools import BRepTools
from OCP.BRepAdaptor import BRepAdaptor_Surface
for f in brep._faces(solid)[:40]:
    u0, u1, v0, v1 = BRepTools.UVBounds_s(f)
    ad = BRepAdaptor_Surface(f)
    if abs(u1-u0) > 1e3 or abs(v1-v0) > 1e3: print('huge parametric face', ad.GetType().name, u0, u1, v0, v1)
