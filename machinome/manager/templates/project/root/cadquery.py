import cadquery as cq

from machinome.node import CadQueryNode


class DemoProject(CadQueryNode):

    def render(self):
        cube = cq.Workplane('XY').box(50, 50, 50, centered=(True, True, False))
        hole = cq.Workplane('XY').circle(10).extrude(100)
        return cube.cut(hole)
