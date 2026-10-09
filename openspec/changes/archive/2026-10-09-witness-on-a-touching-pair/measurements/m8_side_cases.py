"""M8: the side test on the unit cases the planned red test names."""
import sys
sys.path.insert(0, sys.argv[1])
import cadquery as cq
import side as sketch
import machinome.engine.brep as brep
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_IN
def classify(solid, c):
    k = BRepClass3d_SolidClassifier(solid); k.Perform(gp_Pnt(*c), 0.0)
    return 'IN' if (not k.Rejected() and k.State() == TopAbs_IN) else 'not IN'
box = cq.Solid.makeBox(1, 1, 1).wrapped
ell = cq.Solid.makeBox(2, 2, 1).cut(cq.Solid.makeBox(1, 1, 1, cq.Vector(1, 1, 0))).wrapped
cyl = cq.Solid.makeCylinder(1, 2).wrapped
cases = [('box', box, (.5, .5, .5)), ('box', box, (1.5, .5, .5)), ('box', box, (1.5, 1.5, .5)),
         ('box', box, (1 + 1e-9, .5, .5)), ('box', box, (1 - 1e-9, .5, .5)), ('box', box, (1.5, 1.5, 1.5)),
         ('L', ell, (.9, .9, .5)), ('L', ell, (1.1, 1.1, .5)),
         ('cylinder', cyl, (1.1, 0, 1)), ('cylinder', cyl, (.9, 0, 1)), ('cylinder', cyl, (1.1, 1e-3, 1)), ('cylinder', cyl, (0.95, -1e-3, 1))]
for name, shape, c in cases:
    sketch.STATS.clear()
    solid = brep._solids(shape)[0]
    print(name, c, sketch.Boundary(solid).side(c), classify(solid, c), dict(sketch.STATS))
