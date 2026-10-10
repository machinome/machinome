"""An UNTIMED root whose author's `simulate()` binds a joint only under
a guard: the shape Finding A of revision 1 asks about.

`gate` is a ROOT-LEVEL LEAF owning a `Prismatic`.  `Conditional.simulate()`
binds its coordinate only while `time < 0.5`, so instant 0 binds it and
instant 1 leaves it UNBOUND -- at rest -- which ADR-099's clear semantics
explicitly allow ("SHALL find the coordinate unbound on every run").
"""
from solid2 import cube

from solid_node.motion.joints import Prismatic
from solid_node.node import AssemblyNode, Solid2Node


class Gate(Solid2Node):
    travel = Prismatic(axis=(1, 0, 0), unit='mm')

    def render(self):
        return cube([10, 6, 6], center=True)


class Conditional(AssemblyNode):
    """No time base: the untimed root of decision 5."""

    gate = Gate()

    def simulate(self):
        if self.time < 0.5:
            self.gate.travel = 10.0

    def render(self):
        self.gate.translate([0.0, 0.0, 4.0])


class Wired(AssemblyNode):
    """A root wiring its own port into a leaf's JOINT coordinate."""

    from solid_node.motion.ports import TranslationalPort as _Port

    reach = _Port(unit='mm')
    gate = Gate(travel=reach)

    def simulate(self):
        self.reach = 4.0

    def render(self):
        self.gate.translate([0.0, 0.0, 4.0])


class Formula(AssemblyNode):
    """A root whose DERIVED coordinate drives a leaf's joint."""

    from solid_node.simulation import Driver as _Driver
    from solid_node.motion.ports import TranslationalPort as _P

    push = _Driver(default=3.0, range=(0.0, 20.0), unit='mm')
    left = _P(unit='mm')
    right = _P(unit='mm')
    span = left + right

    gate = Gate()

    push.drives(left)
    push.drives(right, ratio=2.0)
    span.drives(gate.travel)

    def render(self):
        self.gate.translate([0.0, 0.0, 4.0])
