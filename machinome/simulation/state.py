# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""A state declaration: a driver the machine writes.

The originating project is `projects/Calculators/Curta-Type-I-3x`. Its
`operating_curta` retains every coordinate and integrates every law to
carry a stroke's arithmetic forward; its `fast_curta` carries nothing at
all, so the maker edits the registers by hand. The machine between those
two is a CLOCKED one: a few retained values, closed-form positions
between events, and a commit of the retained values at each event
(`workflow/docs/clocked-machine.md`).

A `State` is the declaration of one of those retained values. It takes
exactly `Driver`'s arguments with exactly their meanings, is read
`self.units` exactly as a driver's value is, and qualifies by exactly a
driver's rule -- the dotted attribute path to the declaring node plus
the local name. A tree in which anything declares one is a CLOCKED
model.

Everything that distinguishes it from a driver is about WHO WRITES IT,
and none of that is here: `set_state` refuses one by name, an
`Instruction` and a control cannot target one, `drives` refuses one as
its driven end, and a committing relation
(`machinome.motion.couplings.commit`) is the only thing that writes
one. Each of those refusals is raised where its own facts exist.

The dependency runs one way, exactly as `driver.py`'s does: this module
imports the node layer's `StateDeclaration` marker, and
`machinome.node` imports nothing from here. A project that names no
`State` never imports this module at all, which is what makes "a
stateless model pays nothing" structural rather than hoped for.
"""

from dataclasses import dataclass

from machinome.node.qualified import StateDeclaration, declared_states_of


@dataclass(frozen=True)
class State(StateDeclaration):
    """A retained value, declared as a class attribute on an assembly.

    Frozen for `Driver`'s reason: an attribute that could be assigned
    here would be state shared by every node of the class and every
    simulation over it. The value belongs to the clocked simulation's
    BANK, and the declaration states only what it is.

    The five fields are a driver's five, and mean what they mean there:

    - `default` is the value in NATIVE units, where the machine stands
      before anything has been committed;
    - `range` is PRESENTATION metadata in design units and clamps
      nothing -- a machine driven past its declared travel is a crash a
      simulation must be able to show;
    - `unit` names the design unit;
    - `dtype=int` means the value is a whole number of NATIVE units, and
      a commit rounds to the nearest one ONCE, at the commit;
    - `scale` is design units per native unit.

    A commit law READS native values and RETURNS native values. Its
    return is deliberately NOT passed through `Driver.native()`: that
    converts a DESIGN-unit target into native state by dividing by
    `scale`, so a scaled state would lose a factor of `scale` at every
    commit.
    """

    default: object
    range: tuple = None
    unit: str = None
    dtype: type = None
    scale: float = None

    def __post_init__(self):
        if self.dtype not in (None, int, float):
            raise TypeError(
                f'state dtype must be int, float or None, not {self.dtype!r}')
        if self.dtype is int and not isinstance(self.default, int):
            raise TypeError(
                f'an integer state counts whole native units, so its '
                f'default must be an int, not {self.default!r}')

    def committed(self, value):
        """`value`, as this state holds it after a commit.

        The ONE thing that happens to a committed value: a state
        declaring `dtype=int` counts whole native units, so it takes the
        nearest one, rounded ONCE, here. A repeated rounding drifts; a
        single one does not. Nothing else is converted -- the law
        already spoke native units.
        """
        return round(value) if self.dtype is int else value


def declared_states(node_class):
    """Every state declared on `node_class`, by class-local name.

    `driver.declared_drivers`'s twin, and single-class like it: a
    machine's states live across its whole tree, and enumerating THOSE
    is `enumeration.qualified_states`, which walks the linked tree and
    keys by qualified id.
    """
    return declared_states_of(node_class)
