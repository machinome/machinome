"""Finding (a): a `.repeat()` child's PORT cannot be published under a
running root.

The pin tumbler lock's spring bank, reduced: a running root whose
`.repeat()` children own a plain port a relation drives. The relation's
driven ends are ports, not bank coordinates, and nothing downstream of
them reaches the bank, so `_reaching_the_bank` drops the edge -- but
`compile_program` already registered a program node for each end, and
`Program.nodes` keeps them. Publication then refuses a coordinate the
program does not compute.

Run from the worktree root with PYTHONPATH="$PWD".
"""

from solid2 import cube, cylinder

from solid_node.motion.joints import Prismatic
from solid_node.motion.ports import Time, TranslationalPort
from solid_node.node import AssemblyNode, Solid2Node
from solid_node.simulation import Driver
from solid_node.simulation.enumeration import bind_declared_defaults
from solid_node.simulation.program import program_of


class PenSpring(Solid2Node):
    """A spring copy: a plain port, no joint."""

    height = TranslationalPort(unit='mm')

    def render(self):
        return cylinder(r=1, h=4)


class Slider(Solid2Node):
    travel = Prismatic(axis=(0, 0, 1), unit='mm')

    def render(self):
        return cube([4, 4, 2])


class Bank(AssemblyNode):
    """A running root whose repeated children own a driven PORT."""

    time = Time.running()

    lift = Driver(default=0.0, unit='mm')

    slider = Slider()
    springs = PenSpring().repeat(3)

    lift.drives(slider.travel, ratio=1.0)
    lift.drives(springs.height, ratio=-1.0)

    def render(self):
        pass


def report(label, factory):
    node = factory()
    bind_declared_defaults(node)
    program, initial = program_of(node)
    print(f'{label}: nodes  ', sorted(
        (node_.name, node_.kind, node_.qualified)
        for node_ in program.nodes.values()))
    print(f'{label}: edges  ', [edge.description for edge in program.edges])
    try:
        published = program.published(initial)
    except Exception as error:
        print(f'{label}: published -> {type(error).__name__}: {error}')
        return
    print(f'{label}: published intermediates {published["intermediates"]}')
    print(f'{label}: published sources       '
          f'{sorted(published["sources"])}')


def why_unqualified():
    """WHICH of the two refusals `_qualified` caught: the copies are
    LINKED (so `instance_path` succeeds); it is the id grammar that
    refuses their name."""
    from solid_node.node.qualified import (DriverIdError, driver_id,
                                           instance_path)

    node = Bank()
    bind_declared_defaults(node)
    node.assemble()
    copies = [child for child in node.children
              if isinstance(child, PenSpring)]
    print('linked copies  ', [copy.name for copy in copies])
    for copy in copies[:1]:
        path = instance_path(copy, node)
        print('instance_path  ', path)
        try:
            print('driver_id      ', driver_id(path, 'height'))
        except DriverIdError as error:
            print(f'driver_id      -> DriverIdError: {error}')


if __name__ == '__main__':
    report('repeat port    ', Bank)
    why_unqualified()
