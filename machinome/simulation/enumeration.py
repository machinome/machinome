# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The one authority on what drivers a machine has, and what they are
called from outside it.

`declared_drivers(cls)` answers for a single class. That was enough
while a machine declared its drivers on the root, and stops being
enough the moment a machine is built out of mechanisms: a printer's
drivers live on its axes, and the root may declare none at all. Every
flat namespace that has to name a driver -- the simulation bank, an
instruction target, the serialized document's driver table, the
loader's opening snapshot -- therefore reads THIS walk, keyed by
qualified id (`machinome.node.qualified`). One authority is the point:
the id in the document and the key in the bank are the same string
because they come from the same function, not because two
implementations agree.

The walk lives here, in the simulation layer, and freely imports the
node layer. The reverse never happens: `machinome/node/` owns the
qualification MECHANISM (it must, to deliver a qualified `set_state`
entry) and knows nothing about drivers beyond the declaration marker.
"""

from machinome.node.base import AbstractBaseNode
from machinome.node.qualified import (declared_drivers_of,
                                       declared_states_of, drive_tree)


#: Every state declared on ONE class, by class-local name -- the
#: single-class face, beside `driver.declared_drivers`. Re-exported here
#: so the two enumeration questions, "what does this class declare" and
#: "what does this tree declare", are answered from one module.
declared_states = declared_states_of


def qualified_drivers(root):
    """Every driver declared in `root`'s tree, by qualified id.

    Binding is not a side effect to apologize for: finding the children
    means rendering, and a state-consuming assembly cannot be rendered
    under no snapshot at all, so the walk binds each declaration's own
    default as it descends. The framework still invents nothing -- the
    declarations state the values, and a caller with a real snapshot
    (a simulation tick, a serialization pass) binds over them
    immediately.
    """
    return drive_tree(
        root, lambda node, path, name, declaration: declaration.default)


def qualified_states(root):
    """Every state declared in `root`'s tree, by qualified id.

    `qualified_drivers`'s twin, by the same rule and from the same walk
    machinery: the id in the clocked bank, the id a refusal names and
    the id a request is addressed by are the same string because they
    come from one function (OpenSpec change ``declare-the-state``).

    A tree that declares no state is walked exactly as `qualified_drivers`
    walks it and returns `{}`; a caller that wants BOTH tables without
    paying for two descents takes `qualified_declarations`, which
    returns the states beside the instructions and the controls.
    """
    found = {}
    drive_tree(
        root, lambda node, path, name, declaration: declaration.default,
        collected=found)
    refuse_states_under_a_clock(root, found)
    return found


def qualified_declarations(root):
    """Every INSTRUCTION, every CONTROL and every STATE declared in
    `root`'s tree, from ONE walk: `(instructions, controls, states)`.

    Both are `{qualified_name: (node, path, declaration)}`, keyed by the
    declaring node's instance path joined with the declared name -- a
    root-declared one keeping its bare name, exactly as a root-declared
    driver does. That is what makes a `Button`'s instruction reference
    equal a key of the instructions table by CONSTRUCTION: the two names
    are qualified through the same path, by the same rule, in the same
    pass.

    One walk rather than two because `drive_tree`'s `visit` exists for
    exactly this -- "a caller that also needs something else declared
    per node pays for one walk rather than two" -- and `Sim.__init__`
    needs all three. `qualified_instructions`, `qualified_controls` and
    `qualified_states` are thin faces over it.

    The STATE table is `{qualified_id: declaration}`, the shape
    `qualified_drivers` returns, and it comes from the SAME pass rather
    than an additional one -- which is what makes a clocked discipline
    cost a stateless model nothing (OpenSpec change
    ``declare-the-state``, design section 16).
    """
    instructions = {}
    controls = {}
    states = {}

    def visit(node, path, _children):
        for name, instruction in getattr(node, 'instructions', {}).items():
            instructions['.'.join(path + (name,))] = (node, path, instruction)
        for name, control in getattr(node, 'controls', {}).items():
            controls['.'.join(path + (name,))] = (node, path, control)

    drive_tree(
        root, lambda node, path, name, declaration: declaration.default,
        visit, collected=states)
    refuse_states_under_a_clock(root, states)
    return instructions, controls, states


def qualified_instructions(root):
    """Every instruction declared in `root`'s tree, by qualified name.

    `{qualified_name: (node, path, instruction)}`. An instruction is
    declared with class-local target names, so the declaring node's
    path is what turns `{'motor': 0.0}` into a target on
    `x_axis.motor`; a root-declared instruction keeps its bare name,
    exactly as a root-declared driver does.
    """
    return qualified_declarations(root)[0]


def qualified_controls(root):
    """Every control declared in `root`'s tree, by qualified name.

    `{qualified_name: (node, path, control)}`, the instruction table's
    twin and the other half of one walk.
    """
    return qualified_declarations(root)[1]


def bind_declared_defaults(root):
    """Bind every declared default across `root`'s tree, and return the
    enumeration.

    This is what the build/test loader calls so a driver-declaring
    project builds, tests and serves without binding its own defaults
    in `__init__`. A tree that declares no driver is left strictly
    alone -- not walked, not rendered -- so a driverless project loads
    exactly as it did before this existed. The structural pre-check
    below answers that question without rendering anything, which is
    the only way to answer it without already being the behaviour
    change it is guarding against.
    """
    if not tree_declares_drivers(root):
        return {}
    _decide_block_membership(root)
    states = {}
    found = drive_tree(
        root, lambda node, path, name, declaration: declaration.default,
        collected=states)
    refuse_states_under_a_clock(root, states)
    return found


def refuse_states_under_a_clock(root, states):
    """A `State` under a root declaring a TIME BASE is refused by name.

    Memory and a LOOPING base do not mix: a loop replays the timeline
    from zero, so it replays every commit and the state climbs across
    loops. Memory and a RUNNING base do mix, and their meaning is
    DEFINED -- a committed value under a run is an ADR-121 self-read law
    whose value changes only through a switch -- but it is deliberately
    not implemented in this cycle, so the combination is refused rather
    than silently given the wrong mechanics (OpenSpec change
    ``declare-the-state``, design section 12).

    Memory and the ELAPSED base are the square this refusal now leaves
    open: elapsed seconds never wrap, so nothing replays a commit, and
    the simulation over such a root is the clocked one with its clock in
    the bank (OpenSpec change ``time-without-running``, design section
    3). The elapsed base RETURNS here rather than falling through, which
    is what keeps the two refusals below exactly as they were.

    Raised where the declared defaults are bound, which is the first
    moment both facts -- the root's base and the tree's states -- are
    known together.
    """
    if not states:
        return
    from machinome.motion.ports import declared_time

    base = declared_time(type(root))
    if base is None or base.mode == 'elapsed':
        return
    named = ', '.join(sorted(states))
    if base.mode == 'loop':
        raise TypeError(
            f"{type(root).__name__} declares time = Time(loop="
            f"{base.loop!r}) and its tree declares the state(s) {named}. "
            f"A looping base replays the timeline from zero, so it would "
            f"replay every commit and the state would climb across "
            f"loops: a clocked model declares NO time base, and a state "
            f"moves on requests. Drop the loop, or drop the state.")
    raise TypeError(
        f"{type(root).__name__} declares time = Time.running() and its "
        f"tree declares the state(s) {named}. The combination is DEFINED "
        f"-- under a run a value committed at an event is a self-read "
        f"law whose value changes only through a switch, so the state "
        f"becomes one retained coordinate among all the others -- and it "
        f"is NOT implemented in this cycle. Declare no time base to get "
        f"the clocked mechanics, or drop the state and write the law the "
        f"run integrates.")


def _decide_block_membership(root):
    """Mark the relations of `root`'s tree that lie on a dependency
    cycle every selection breaks, BEFORE the enumeration below sees them
    (OpenSpec change ``select-the-source``).

    The same pre-pass `Sim` runs, at the same point relative to the first
    enumeration of the tree, because a producer binding declared defaults
    IS a rest render: without it a running root whose union is cyclic
    would be refused `DoublyBound` here and never reach the compile that
    answers it. Idempotent and confined to a running root, so a tree
    under any other time base is not walked at all.
    """
    from machinome.motion.ports import declared_time

    base = declared_time(type(root))
    if base is None or base.mode != 'running':
        return
    from .program import _block_members

    _block_members(root)


def tree_declares_states(node, seen=None):
    """Whether anything in `node`'s constructed tree declares a `State`.

    `tree_declares_drivers`'s twin, structural and never rendering, and
    asked for one reason: a clocked simulation takes NO `dt`, and every
    other one must still be refused for omitting one, so the question
    has to be answered before anything is bound.

    A tree that declares no state is walked and nothing else happens:
    the clocked module is not imported, no clocked code path is entered,
    and the simulation constructed over it is the one that was
    constructed before this existed (OpenSpec change
    ``declare-the-state``).
    """
    if seen is None:
        seen = set()
    if id(node) in seen:
        return False
    seen.add(id(node))
    if declared_states_of(type(node)):
        return True
    for value in vars(node).values():
        if isinstance(value, AbstractBaseNode):
            candidates = (value,)
        elif isinstance(value, (list, tuple)):
            candidates = [item for item in value
                          if isinstance(item, AbstractBaseNode)]
        else:
            continue
        for child in candidates:
            if tree_declares_states(child, seen):
                return True
    return False


def tree_declares_drivers(node, seen=None):
    """Whether anything in `node`'s constructed tree declares a driver.

    Structural, never rendering: it walks the node instances a parent
    already holds -- on its own attributes, in its lists and tuples,
    and in whatever a previous pass linked as `children`. That is the
    same place `_attr_name_for` derives names from, so it sees the tree
    a linked walk would see, minus children a render has yet to create.
    A false negative there costs a driver-declaring project the loud
    unbound-state error it would have had anyway; a false positive
    costs one extra walk. Neither can silently change a driverless
    project, which is what this guard is for.
    """
    if seen is None:
        seen = set()
    if id(node) in seen:
        return False
    seen.add(id(node))
    if declared_drivers_of(type(node)) or declared_states_of(type(node)):
        # A STATE is a banked value the tree cannot render without, so a
        # tree that declares one is walked exactly as a driven one is
        # even where it declares no driver at all.
        return True
    for value in vars(node).values():
        if isinstance(value, AbstractBaseNode):
            candidates = (value,)
        elif isinstance(value, (list, tuple)):
            candidates = [item for item in value
                          if isinstance(item, AbstractBaseNode)]
        else:
            continue
        for child in candidates:
            if tree_declares_drivers(child, seen):
                return True
    return False
