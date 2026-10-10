from solid_node.node import Solid2Node
from solid2 import cube


class Sweeper(Solid2Node):

    def render(self):
        return cube(5)
