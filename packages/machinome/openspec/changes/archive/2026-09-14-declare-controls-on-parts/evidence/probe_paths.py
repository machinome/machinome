"""Task 0.6 (a) and (b): the two facts the declaration and the document
shape rest on, probed on this worktree before anything is changed.

(a) `Columns.units.dial`, written in a class body, is a `PathRef` whose
    terminal is a `ChildDeclaration`; `PathRef._walk(instance)` returns
    the realized leaf; and `qualified.instance_path(leaf, root)` is
    `('units', 'dial')` -- the same names the document's tree publishes.
    That is design.md section 2: a control's part is named exactly the
    way a relation's path ends already are.

(b) `Revolute(axis=(1,0,0), at=(0,3,0))` places a centring pair around
    its rotation while `Revolute(axis=(1,0,0))` places the rotation
    alone, so the point the joint turns about is NOT recoverable from
    the node's world matrix and `origin` is needed (design.md section 8).
"""

from solid2 import cube, cylinder

from solid_node.motion.couplings import PathRef
from solid_node.motion.joints import Revolute
from solid_node.motion.ports import Time
from solid_node.node import AssemblyNode, Solid2Node
from solid_node.node.declarative import ChildDeclaration
from solid_node.node.qualified import instance_path
from solid_node.simulation import Driver
from solid_node.simulation.enumeration import bind_declared_defaults


class Dial(Solid2Node):
    """A leaf with geometry and no coordinate: the part a hand touches."""

    def render(self):
        return cylinder(r=20, h=3)


class DialArbor(AssemblyNode):
    """The Pascaline's own shape: the joint at depth, the touchable leaf
    beneath it."""

    turn = Revolute(axis=(1, 0, 0), unit='deg')

    dial = Dial()

    def render(self):
        pass


class OffCentreArbor(AssemblyNode):
    turn = Revolute(axis=(1, 0, 0), at=(0, 3, 0), unit='deg')

    dial = Dial()

    def render(self):
        pass


class Columns(AssemblyNode):
    time = Time.running()

    units_entry = Driver(default=0.0, unit='digit')

    units = DialArbor()
    off = OffCentreArbor()

    units_entry.drives(units.turn, ratio=-36.0)
    units_entry.drives(off.turn, ratio=-36.0)

    def render(self):
        self.off.translate([50.0, 0.0, 0.0])


print('(a) the part reference')
ref = Columns.units.dial
print(f'    Columns.units.dial       -> {ref!r}  type={type(ref).__name__}')
print(f'    isinstance PathRef       -> {isinstance(ref, PathRef)}')
print(f'    .segments                -> {ref.segments}')
print(f'    .terminal                -> {ref.terminal!r} '
      f'(ChildDeclaration: {isinstance(ref.terminal, ChildDeclaration)})')

root = Columns()
bind_declared_defaults(root)
leaf = ref._walk(root)
print(f'    _walk(instance)          -> {leaf!r}  type={type(leaf).__name__}')
print(f'    instance_path(leaf, root)-> {instance_path(leaf, root)}')

print()
print('(b) the point the joint turns about')
for name in ('units', 'off'):
    node = getattr(root, name)
    joint = type(node).turn
    operations = [operation.serialized for operation in node.operations]
    print(f'    {type(node).__name__}.turn at={joint.at}')
    print(f'      arguments(node)[1]     -> {joint.arguments(node)[1]}')
    print(f'      axes(node)             -> {joint.axes(node)}')
    print(f'      carried_points(node,.) -> '
          f'{joint.carried_points(node, joint.arguments(node)[1])}')
    print(f'      placed operations      -> {operations}')

print()
print('(b, published) the same two nodes as the document publishes them')
from solid_node.core.serializer import serialize_node, symbolic_document

published = Columns()
bind_declared_defaults(published)
with symbolic_document(published) as (_declarations, _instructions):
    tree = serialize_node(published, lambda rigid: rigid.name,
                          graph_values=True)
for child in tree['children']:
    print(f"    {child['name']:6s} -> {child['operations']}")
