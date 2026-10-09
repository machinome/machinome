"""M3: the bench witness against the sketch on synthetic pairs: genuine
overlaps the guard must keep refusing (same witness), touching pairs it must
keep returning, and a many-faced pair for the side test's own cost.

As run on 9 October: cq.Solid.makeSphere's default angles build the upper
hemisphere, so the "sphere into block" pairs here never meet the block and
the "ball in seat" pairs are a hemisphere standing on a face; M4 repeats the
sunk balls with full spheres. The "key ... slot" keys also overlap the
slot's floor by 0.5 mm."""
import math, sys, time
sys.path.insert(0, sys.argv[1])
import cadquery as cq
import side as sketch
import machinome.engine.brep as brep
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.gp import gp_Pnt

calls = [0]
_native = BRepClass3d_SolidClassifier
class Counting:
    def __init__(self, solid): self.c = _native(solid)
    def Perform(self, p, t): calls[0] += 1; self.c.Perform(p, t)
    def Rejected(self): return self.c.Rejected()
    def State(self): return self.c.State()
brep.BRepClass3d_SolidClassifier = Counting

def box(x=0, y=0, z=0, a=1, b=1, c=1):
    return cq.Solid.makeBox(a, b, c, cq.Vector(x, y, z)).wrapped

def run(fn, first, second):
    calls[0] = 0; sketch.STATS.clear(); t = time.perf_counter()
    try:
        out = fn(first, second)
    except Exception as error:
        out = 'ERROR ' + str(error)[:60]
    return out, calls[0], time.perf_counter() - t

def block_with_sphere(depth, radius=3.75):
    block = box(-5, -5, -10, 10, 10, 10)
    ball = cq.Solid.makeSphere(radius, cq.Vector(0, 0, radius - depth)).wrapped
    return block, ball

def pin_in_hole(interference):
    plate = cq.Workplane().box(20, 20, 6).faces('>Z').workplane().hole(6).val().wrapped
    pin = cq.Solid.makeCylinder(3 + interference, 12, cq.Vector(0, 0, -6)).wrapped
    return plate, pin

def slot_and_key(interference):
    slotted = cq.Workplane().box(10, 10, 4).faces('>Z').workplane().rect(3, 12).cutBlind(-2).val().wrapped
    key = box(-1.5 - interference, -6, -0.5, 3 + 2 * interference, 12, 2)
    return slotted, key

def ball_in_seat(gap):
    seat = cq.Workplane().box(20, 20, 10).val().cut(cq.Solid.makeSphere(4, cq.Vector(0, 0, 5))).wrapped
    ball = cq.Solid.makeSphere(4 + gap, cq.Vector(0, 0, 5)).wrapped
    return seat, ball

def polygon_prism(n, r, h, x=0):
    pts = [(x + r * math.cos(2 * math.pi * k / n), r * math.sin(2 * math.pi * k / n)) for k in range(n)]
    return cq.Workplane().polyline(pts).close().extrude(h).val().wrapped

cases = {
    'overlapping boxes (.5,.5,.5)': (box(), box(.5, .5, .5)),
    'slab 0.4': (box(), box(0, .6, 0)),
    'sphere 1.0 into block': block_with_sphere(1.0),
    'sphere 0.5 into block': block_with_sphere(0.5),
    'sphere 0.2 into block': block_with_sphere(0.2),
    'pin 0.2 interference': pin_in_hole(0.2),
    'pin 0.05 interference': pin_in_hole(0.05),
    'key 0.1 into slot': slot_and_key(0.1),
    'ball 0.2 into seat': ball_in_seat(0.2),
    'touching boxes (face)': (box(), box(1)),
    'touching boxes (edge)': (box(), box(1, 1)),
    'pin in hole, exact': pin_in_hole(0.0),
    'key in slot, exact': slot_and_key(0.0),
    'ball in seat, exact': ball_in_seat(0.0),
    'sphere on block, tangent': block_with_sphere(0.0),
    '240-gon prisms touching': (polygon_prism(240, 10, 5), polygon_prism(240, 10, 5, 20 * math.cos(math.pi / 240))),
    '240-gon prism and box touching': (polygon_prism(240, 10, 5), box(10 * math.cos(math.pi / 240), -1, 0, 2, 2, 5)),
    '240-gon prism and box overlapping': (polygon_prism(240, 10, 5), box(9.9, -1, 0, 2, 2, 5)),
}
for name, (first, second) in cases.items():
    common = brep._boolean('intersection', first, second, 'a', 'b')
    bench = run(brep._false_empty_witness, first, second)
    sk = run(sketch.witness, first, second)
    same = bench[0] == sk[0]
    print(f'{name}: faces {len(brep._faces(first))}/{len(brep._faces(second))}, native common solids {len(brep._solids(common))}, volume {brep.solid_volume(common):.4g}')
    print(f'   bench  {bench[0]} classify {bench[1]} {bench[2]:.2f} s')
    print(f'   sketch {sk[0]} classify {sk[1]} {sk[2]:.2f} s {dict(sketch.STATS)} SAME={same}', flush=True)

# does the extrema against a solid consult the classifier? (time at a slow point)
S = sys.argv[2]
shell = brep.read_brep(S + '/shell.brep')
solid = brep._solids(shell)[0]
import json
points = json.load(open(sys.argv[3]))
slow = [p for p in points if p.get('shell_ms', 0) > 150][:5]
for p in slow:
    v = BRepBuilderAPI_MakeVertex(gp_Pnt(*p['xyz'])).Vertex()
    t = time.perf_counter(); d = BRepExtrema_DistShapeShape(v, solid); dt = time.perf_counter() - t
    print(f"extrema vertex-solid at a slow point: {dt*1e3:.0f} ms, value {d.Value():.3g}, inner {d.InnerSolution()}, classifier there {p['shell_ms']:.0f} ms, shell_in {p['shell_in']}")
