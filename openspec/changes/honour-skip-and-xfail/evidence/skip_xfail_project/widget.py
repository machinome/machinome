from solid_node.node import Solid2Node
from solid2 import cube


class Widget(Solid2Node):

    def render(self):
        return cube(10)
