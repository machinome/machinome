"""M4: full spheres (M3 built hemispheres), Curta-like sunk balls, and the
side test's cost against a healthy classifier on many-faced solids.

As run on 9 October the rod's axis lies at z = -10, so the "into a rod"
pairs never meet and give no section; they carry no evidence."""
import math, sys, time
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

def sphere(r, c):
    return cq.Solid.makeSphere(r, cq.Vector(*c), angleDegrees1=-90, angleDegrees2=90).wrapped

def run(fn, first, second):
    calls[0] = 0; sketch.STATS.clear(); t = time.perf_counter()
    try:
        out = fn(first, second)
    except Exception as error:
        out = 'ERROR ' + str(error)[:80]
    return out, calls[0], time.perf_counter() - t

block = cq.Solid.makeBox(10, 10, 10, cq.Vector(-5, -5, -10)).wrapped
rod = cq.Solid.makeCylinder(5, 20, cq.Vector(0, 0, -10), cq.Vector(0, 1, 0)).wrapped  # axis along y, surface at z = -5..5
holder = cq.Workplane().box(30, 30, 10).faces('>Z').workplane().hole(10).val().wrapped
def slotted(n, r=8, h=10):
    body = cq.Workplane().circle(r).extrude(h)
    for k in range(n):
        a = 2 * math.pi * k / n
        body = body.cut(cq.Workplane().box(0.3, 1.0, h + 2).translate((r * math.cos(a), r * math.sin(a), h / 2)).rotate((0, 0, 0), (0, 0, 1), 0))
    return body.val().wrapped
cases = {}
for depth in (1.0, 0.5, 0.2, 0.05):
    cases[f'ball r3.75 sunk {depth} into a block'] = (block, sphere(3.75, (0, 0, 3.75 - depth)))
    cases[f'ball r3.75 sunk {depth} into a rod'] = (rod, sphere(3.75, (0, 0, 5 + 3.75 - depth)))
cases['ball r3.75 in a block, tangent'] = (block, sphere(3.75, (0, 0, 3.75)))
t = time.perf_counter(); gear = slotted(60); print(f'slotted body built {time.perf_counter()-t:.1f} s', flush=True)
cases['60-slot body (many faces) and a box touching'] = (gear, cq.Solid.makeBox(2, 2, 10, cq.Vector(8, -1, 0)).wrapped)
cases['60-slot body and a ring touching its rim'] = (gear, cq.Workplane().circle(12).circle(8).extrude(10).val().wrapped)
cases['60-slot body and a box overlapping'] = (gear, cq.Solid.makeBox(2, 2, 10, cq.Vector(7.8, -1, 0)).wrapped)
for name, (first, second) in cases.items():
    common = brep._boolean('intersection', first, second, 'a', 'b')
    bench = run(brep._false_empty_witness, first, second)
    sk = run(sketch.witness, first, second)
    print(f'{name}: faces {len(brep._faces(first))}/{len(brep._faces(second))}, native common solids {len(brep._solids(common))} volume {brep.solid_volume(common):.4g}')
    print(f'   bench  {bench[0]} classify {bench[1]} {bench[2]:.2f} s')
    print(f'   sketch {sk[0]} classify {sk[1]} {sk[2]:.2f} s {dict(sketch.STATS)} SAME={bench[0] == sk[0]}', flush=True)
