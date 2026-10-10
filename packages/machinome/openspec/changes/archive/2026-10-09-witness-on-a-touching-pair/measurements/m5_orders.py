"""M5: cost of the bench, side-first (d) and small-first (i) orders."""
import math, sys, time, json
sys.path.insert(0, sys.argv[1])
import cadquery as cq
import side as sketch
import machinome.engine.brep as brep
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
calls = [0]
_native = BRepClass3d_SolidClassifier
class Counting:
    def __init__(self, solid): self.c = _native(solid)
    def Perform(self, p, t): calls[0] += 1; self.c.Perform(p, t)
    def Rejected(self): return self.c.Rejected()
    def State(self): return self.c.State()
brep.BRepClass3d_SolidClassifier = Counting
def run(fn, *args):
    calls[0] = 0; sketch.STATS.clear(); t = time.perf_counter()
    try: out = fn(*args)
    except Exception as error: out = 'ERROR ' + str(error)[:80]
    return out, calls[0], time.perf_counter() - t, dict(sketch.STATS)
def box(x=0, y=0, z=0, a=1, b=1, c=1): return cq.Solid.makeBox(a, b, c, cq.Vector(x, y, z)).wrapped
def slotted(n, r=8, h=10):
    body = cq.Workplane().circle(r).extrude(h)
    for k in range(n):
        a = 2 * math.pi * k / n
        body = body.cut(cq.Workplane().box(0.3, 1.0, h + 2).translate((r * math.cos(a), r * math.sin(a), h / 2)))
    return body.val().wrapped
def polygon_prism(n, r, h, x=0):
    pts = [(x + r * math.cos(2 * math.pi * k / n), r * math.sin(2 * math.pi * k / n)) for k in range(n)]
    return cq.Workplane().polyline(pts).close().extrude(h).val().wrapped
S = sys.argv[2]
shell = brep.read_brep(S + '/shell.brep'); screw = brep.read_brep(S + '/screw.brep')
plate = cq.Workplane().box(20, 20, 6).faces('>Z').workplane().hole(6).val().wrapped
gear = slotted(60)
ring = cq.Workplane().circle(12).circle(8).extrude(10).val().wrapped
cases = {
  'touching boxes (face)': (box(), box(1)),
  'pin in hole, exact': (plate, cq.Solid.makeCylinder(3, 12, cq.Vector(0, 0, -6)).wrapped),
  '240-gon and box touching': (polygon_prism(240, 10, 5), box(10 * math.cos(math.pi / 240), -1, 0, 2, 2, 5)),
  '60-slot body and ring': (gear, ring),
  'ring and 60-slot body': (ring, gear),
  'slab 0.4 (overlap)': (box(), box(0, .6, 0)),
}
skip_bench = set(sys.argv[3:])
cases['shell, screw (captured)'] = (shell, screw)
cases['screw, shell (captured)'] = (screw, shell)
for name, (a, b) in cases.items():
    rows = []
    if not (name.endswith('(captured)') and 'bench' in skip_bench):
        rows.append(('bench', run(brep._false_empty_witness, a, b)))
    rows.append(('side-first', run(sketch.witness, a, b, 'side-first')))
    rows.append(('small-first', run(sketch.witness, a, b, 'small-first')))
    print(name, flush=True)
    for label, (out, n, dt, st) in rows:
        print(f'   {label:11s} {out} classify {n} {dt:.2f} s sides {st.get("side", 0)}', flush=True)
