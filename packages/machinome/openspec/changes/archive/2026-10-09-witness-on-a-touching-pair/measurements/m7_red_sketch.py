"""M7: the red test's proof, per-solid classifier counts on synthetic touching
pairs, bench against sketch (small-first)."""
import collections, sys
sys.path.insert(0, sys.argv[1])
import cadquery as cq
from unittest.mock import patch
import side as sketch
import machinome.engine.brep as brep
from OCP.BRepClass3d import BRepClass3d_SolidClassifier

asked = collections.Counter()
class Counting:
    def __init__(self, solid):
        self.native = BRepClass3d_SolidClassifier(solid)
        self.faces = len(brep._faces(solid))
    def Perform(self, point, tolerance):
        asked[self.faces] += 1; self.native.Perform(point, tolerance)
    def Rejected(self): return self.native.Rejected()
    def State(self): return self.native.State()

empty = cq.Compound.makeCompound([]).wrapped
plate = cq.Workplane().box(20, 20, 6).faces('>Z').workplane().hole(6).val().wrapped
pin = cq.Solid.makeCylinder(3, 12, cq.Vector(0, 0, -6)).wrapped
boxes = (cq.Solid.makeBox(1, 1, 1).wrapped, cq.Solid.makeBox(2, 2, 2, cq.Vector(1, 0, 0)).wrapped)
cases = {'plate, pin': (plate, pin), 'pin, plate': (pin, plate), 'box, larger box on its face': boxes}
for label, witness in (('bench', brep._false_empty_witness), ('sketch', lambda a, b: sketch.witness(a, b, 'small-first'))):
    for name, (a, b) in cases.items():
        asked.clear()
        with patch('machinome.engine.brep._boolean', return_value=empty), \
             patch('machinome.engine.brep.BRepClass3d_SolidClassifier', Counting), \
             patch('machinome.engine.brep._false_empty_witness', witness):
            result = brep.intersect_shapes(a, b, 'first', 'second')
        print(f'{label:6s} {name}: solids {len(brep._solids(result))}, classifier calls by face count {dict(asked)}')
