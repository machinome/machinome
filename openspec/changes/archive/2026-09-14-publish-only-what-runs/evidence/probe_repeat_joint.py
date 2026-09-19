"""The ADDENDUM measurement, NOT this cycle's to fix: a `.repeat()`
child that owns a JOINT under a running root.

The shop's API skill records both halves of the claim -- a repeat copy
may own neither a port a relation drives (probe_repeat_port.py) nor a
joint. This probe measures the joint half, to show it is refused
somewhere else entirely, by the qualified-id GRAMMAR rather than by
publication, and therefore is not fixed by pruning the program's nodes.

Run from the worktree root with PYTHONPATH="$PWD".
"""

import traceback

from solid2 import cube

from solid_node.motion.joints import Prismatic
from solid_node.motion.ports import Time
from solid_node.node import AssemblyNode, Solid2Node
from solid_node.simulation import Driver
from solid_node.simulation.enumeration import bind_declared_defaults
from solid_node.simulation.program import program_of, qualified_coordinates


class Pin(Solid2Node):
    """A copy that owns a JOINT."""

    lift = Prismatic(axis=(0, 0, 1), unit='mm')

    def render(self):
        return cube([2, 2, 6])


class Bench(AssemblyNode):
    time = Time.running()

    key = Driver(default=0.0, unit='mm')

    pins = Pin().repeat(3)

    key.drives(pins.lift, ratio=1.0)

    def render(self):
        pass


if __name__ == '__main__':
    node = Bench()
    bind_declared_defaults(node)
    node.assemble()
    print('linked copies  ', [child.name for child in node.children])
    try:
        print('bank           ', sorted(qualified_coordinates(node)))
    except Exception:
        print('qualified_coordinates raised:')
        traceback.print_exc()
    try:
        program, initial = program_of(Bench())
    except Exception:
        print('program_of raised:')
        traceback.print_exc()
