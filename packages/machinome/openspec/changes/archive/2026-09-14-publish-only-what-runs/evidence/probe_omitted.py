"""Finding (b): a relation onto a coordinate the render OMITS makes a
running root's document unpublishable.

The fixture is the one recorded in `workflow/warts.md` under
`declare-controls-on-parts (2026-09-14)`, unchanged, re-run against this
worktree. `Machine(fitted=True)` publishes; `Machine(fitted=False)`
omits `spare`, so the relation `crank.drives(spare.turn)` reaches a node
the render never linked, `_qualified` falls back to `Arbor.turn`, and
`Program.published` refuses the whole document.

Run from the worktree root with PYTHONPATH="$PWD".
"""

from solid2 import cylinder

from solid_node.motion.joints import Revolute
from solid_node.motion.ports import Time
from solid_node.node import AssemblyNode, Solid2Node
from solid_node.parameters import Flag
from solid_node.simulation import Driver
from solid_node.simulation.enumeration import bind_declared_defaults
from solid_node.simulation.program import program_of


class Arbor(Solid2Node):
    turn = Revolute(axis=(0, 0, 1), unit='deg')

    def render(self):
        return cylinder(r=5, h=2)


class Machine(AssemblyNode):
    time = Time.running()
    fitted = Flag(True)

    crank = Driver(default=0.0, unit='deg')

    first = Arbor()
    spare = Arbor()

    crank.drives(first.turn, ratio=2.0)
    crank.drives(spare.turn, ratio=3.0)

    def render(self):
        self.spare.translate([20.0, 0.0, 0.0])
        if not self.fitted:
            self.spare.omit()


class Reader(AssemblyNode):
    """The variant a KEPT edge makes: the omitted node's coordinate is
    READ by a relation that drives a banked one, so the edge survives
    `_reaching_the_bank` and its unqualified end stays whatever the
    pruning does."""

    time = Time.running()
    fitted = Flag(True)

    crank = Driver(default=0.0, unit='deg')

    first = Arbor()
    spare = Arbor()

    crank.drives(spare.turn, ratio=3.0)
    spare.turn.drives(first.turn, ratio=2.0)

    def render(self):
        self.spare.translate([20.0, 0.0, 0.0])
        if not self.fitted:
            self.spare.omit()


class Sourced(AssemblyNode):
    """The attempted third variant: the omitted node's coordinate as a
    SOURCE nothing computes. It never reaches the program at all --
    fitted or not -- because the COUPLING layer refuses a relation
    neither of whose ends anything binds. Kept here as the measurement
    that `_refuse_opaque` is not reachable this way through `omit()`."""

    time = Time.running()
    fitted = Flag(True)

    crank = Driver(default=0.0, unit='deg')

    first = Arbor()
    second = Arbor()
    spare = Arbor()

    crank.drives(first.turn, ratio=2.0)
    spare.turn.drives(second.turn, ratio=2.0)

    def render(self):
        self.second.translate([20.0, 0.0, 0.0])
        self.spare.translate([40.0, 0.0, 0.0])
        if not self.fitted:
            self.spare.omit()


def report(label, factory):
    try:
        node = factory()
        bind_declared_defaults(node)
        program, initial = program_of(node)
    except Exception as error:
        print(f'{label}: compile -> {type(error).__name__}: {error}')
        return
    print(f'{label}: nodes  ', sorted(
        (node_.name, node_.kind, node_.qualified)
        for node_ in program.nodes.values()))
    print(f'{label}: edges  ', [edge.description for edge in program.edges])
    try:
        published = program.published(initial)
    except Exception as error:
        print(f'{label}: published -> {type(error).__name__}: {error}')
        return
    print(f'{label}: published coordinates   '
          f'{sorted(published["coordinates"])}')
    print(f'{label}: published intermediates {published["intermediates"]}')


if __name__ == '__main__':
    report('fitted=True ', lambda: Machine(fitted=True))
    report('fitted=False', lambda: Machine(fitted=False))
    report('read=True   ', lambda: Reader(fitted=True))
    report('read=False  ', lambda: Reader(fitted=False))
    report('source=True ', lambda: Sourced(fitted=True))
    report('source=False', lambda: Sourced(fitted=False))
