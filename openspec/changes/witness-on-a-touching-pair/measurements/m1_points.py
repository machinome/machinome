"""M1: the witness stencil on the captured shell/screw pair, point by point.
Records, for every stencil point, the screw classifier (all points), the
nearest-face side test in both solids (all points), and the shell classifier
on a deterministic sample. Writes m1.json beside this script."""
import json, math, sys, time
from itertools import product
import machinome.engine.brep as brep
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape, BRepExtrema_SupportType
from OCP.BRepGProp import BRepGProp_Face
from OCP.BRep import BRep_Tool
from OCP.Extrema import Extrema_ExtFlag_MIN
from OCP.TopAbs import TopAbs_IN, TopAbs_SHELL
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Pnt, gp_Vec

S, OUT = sys.argv[1], sys.argv[2]
shell = brep.read_brep(S + '/shell.brep'); screw = brep.read_brep(S + '/screw.brep')
solids = {'shell': brep._solids(shell)[0], 'screw': brep._solids(screw)[0]}
print('faces', {k: len(brep._faces(v)) for k, v in solids.items()})
section = BRepAlgoAPI_Section(brep._copy(shell), brep._copy(screw), False); section.Build()
edges = brep._edges(section.Shape())
spans = []
for s in (shell, screw):
    lo, hi = brep.bounds(s); spans += [d for d in (hi[0]-lo[0], hi[1]-lo[1], hi[2]-lo[2]) if d > 0]
scale = min(spans); steps = (scale*1e-4, scale*1e-3, scale*1e-2)
print('section edges', len(edges), 'lengths', [round(brep._length(e), 3) for e in edges[:8]], 'scale', scale, 'steps', steps)
dirs = [tuple(v/math.sqrt(sum(o*o for o in d)) for v in d) for d in product((-1,0,1), repeat=3) if any(d)]
points = []
for ei, e in enumerate(edges[:8]):
    if brep._length(e) <= 0: continue
    for fr in (.25,.5,.75):
        at = brep._position_at(e, fr)
        for si, st in enumerate(steps):
            for di, d in enumerate(dirs):
                points.append(dict(edge=ei, fraction=fr, step=si, direction=di,
                                   xyz=tuple(at[i] + st*d[i] for i in range(3))))
print('points', len(points))

def shell_of(solid):
    ex = TopExp_Explorer(solid, TopAbs_SHELL); return TopoDS.Shell_s(ex.Current())

def side(solid, xyz):
    """Nearest boundary point by one extrema against the solid's shell; 'OUT'/'IN'
    when every nearest solution lies inside a face and beyond its tolerance and
    all agree; else 'UNDECIDED'."""
    v = BRepBuilderAPI_MakeVertex(gp_Pnt(*xyz)).Vertex()
    dss = BRepExtrema_DistShapeShape(); dss.LoadS1(v); dss.LoadS2(shell_of(solid))
    dss.SetFlag(Extrema_ExtFlag_MIN); dss.Perform()
    if not dss.IsDone(): return 'FAILED', None
    d = dss.Value(); verdicts = set()
    for n in range(1, dss.NbSolution() + 1):
        if dss.SupportTypeShape2(n) != BRepExtrema_SupportType.BRepExtrema_IsInFace:
            return 'EDGE', d
        face = TopoDS.Face_s(dss.SupportOnShape2(n))
        if d <= BRep_Tool.Tolerance_s(face): return 'ONFACE', d
        u, w = dss.ParOnFaceS2(n)
        q = gp_Pnt(); nor = gp_Vec(); BRepGProp_Face(face).Normal(u, w, q, nor)
        q = dss.PointOnShape2(n)
        pq = gp_Vec(q, gp_Pnt(*xyz))
        verdicts.add('OUT' if pq.Dot(nor) > 0 else 'IN')
    return (verdicts.pop() if len(verdicts) == 1 else 'SPLIT'), d

def classify(c, xyz):
    c.Perform(gp_Pnt(*xyz), 0.0)
    return False if c.Rejected() else c.State() == TopAbs_IN

# screw classifier on every point
c = BRepClass3d_SolidClassifier(solids['screw']); t = time.perf_counter()
for p in points: p['screw_in'] = classify(c, p['xyz'])
print(f"screw classifier: {len(points)} points in {time.perf_counter()-t:.2f} s, IN {sum(p['screw_in'] for p in points)}")
for name in ('screw', 'shell'):
    t = time.perf_counter()
    for p in points: p[name + '_side'], p[name + '_dist'] = side(solids[name], p['xyz'])
    dt = time.perf_counter() - t
    tally = {}
    for p in points: tally[p[name + '_side']] = tally.get(p[name + '_side'], 0) + 1
    print(f'{name} side test: {dt:.2f} s for {len(points)} ({dt/len(points)*1e3:.2f} ms each): {tally}')
agree = sum((p['screw_side'] == 'IN') == p['screw_in'] for p in points if p['screw_side'] in ('IN', 'OUT'))
print('screw side vs classifier agree', agree, 'of', sum(p['screw_side'] in ('IN', 'OUT') for p in points))
# shell classifier on a deterministic sample: every 9th point, plus every 9th IN-screw point
c = BRepClass3d_SolidClassifier(solids['shell'])
sample = sorted(set(list(range(0, len(points), 9)) + [i for i, p in enumerate(points) if p['screw_in']][::9]))
t = time.perf_counter()
for i in sample:
    t1 = time.perf_counter(); points[i]['shell_in'] = classify(c, points[i]['xyz']); points[i]['shell_ms'] = (time.perf_counter() - t1) * 1e3
dt = time.perf_counter() - t
print(f'shell classifier sample: {len(sample)} points in {dt:.1f} s ({dt/len(sample)*1e3:.0f} ms each), IN {sum(points[i]["shell_in"] for i in sample)}')
dec = [i for i in sample if points[i]['shell_side'] in ('IN', 'OUT')]
print('shell side vs classifier agree', sum((points[i]['shell_side'] == 'IN') == points[i]['shell_in'] for i in dec), 'of', len(dec))
print('IN both in sample', sum(points[i]['shell_in'] and points[i]['screw_in'] for i in sample))
for si in range(3):
    print('step', si, 'screw IN', sum(p['screw_in'] for p in points if p['step'] == si),
          'shell side IN', sum(p['shell_side'] == 'IN' for p in points if p['step'] == si),
          'shell side OUT among screw IN', sum(p['shell_side'] == 'OUT' for p in points if p['step'] == si and p['screw_in']))
json.dump(points, open(OUT, 'w'))
