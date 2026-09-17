# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The clocked executor: a request path, solved event by event.

A CLOCKED machine has a few retained values, closed-form positions
between events, and a commit of the retained values at each event. The
originating project is `projects/Calculators/Curta-Type-I-3x`, whose
crank is off rest only while its interlocks hold everything else still,
so nothing about its state changes except at the end of a stroke
(`workflow/docs/clocked-machine.md`).

This module is a CONSUMER of the running executor's locator and adds no
second one. `JumpPlan._solved` solves an affine level by one division;
`_KinkCuts` cuts a kinked one at its own breakpoints and solves each
sub-interval; `_shape_of` classifies; `far_side_of` walks the landing in
float ordinal space; `_branch_of` reads a branch. Nothing here bisects,
samples or compares a value to a surface, and **no tolerance is
introduced at all**: under a clocked root every crossing is SOLVED, so
two relations fire at one event exactly when their far-side landings are
the same float.

Three things follow from that and are worth stating before the code:

- **Only RISING steps fire.** The requirement note assumed both edges
  fire and the law neutralises the falling one; the project spike
  measured that false -- with `at = floor(crank / 360)` and no pawl,
  dragging the crank backwards commits a SECOND addition, 9 to 18. A
  mechanism that commits on the other edge negates its own level,
  `floor(-crank / 360)`, which is exact and needs no keyword.
- **A commit is evaluated at ONE POINT and never integrated**, so
  `floor` means `floor`, `%` means `%`, and a law made entirely of jumps
  is a perfectly good commit -- the asymmetry ADR-109 drew between a law
  and a bound, for the same reason.
- **A request costs no pose.** `at` and `law` read only banked values,
  so nothing between locating an event and committing it touches the
  tree; the tree is bound ONCE, at the end of the request.
"""

import hashlib
import math
from collections import deque

from solid2.core.object_base import OpenSCADConstant

from solid_node.expression_graph import ExpressionNode, free_names, postorder
from solid_node.motion.couplings import CouplingError
from solid_node.motion.ports import CLOCK_NAME, clocked_marking
from solid_node.node.qualified import (driver_id, drive_tree, instance_path)
from solid_node.scad_expression import GraphValue, as_node, symbol

from .program import (JumpPlan, TooManyCrossings, _CROSSING_TOLERANCE,
                      _KinkCuts, _MAX_CROSSINGS, _Jump, _along,
                      _argument_graph, _branch_of, _deduplicated,
                      _on_surface, _placeholder_prefix, _plan_of,
                      _published_plan, _shape_of, checked_expression,
                      far_side_of)


class ClockedError(CouplingError):
    """A clocked model, or a request over one, the framework refuses."""


class TooManyEvents(ClockedError):
    """One request would commit more events of one relation than the
    framework admits. The request committed nothing."""


#: The jump primitives an EVENT may be stated with. `%` is deliberately
#: absent: `a % b` is not integer valued, so it is not a level whose
#: steps are events, and the note's "integer-valued expression" is not a
#: structural property the framework can check without sampling.
_EVENT_CALLS = ('floor', 'ceil', 'sign')
_EVENT_OPERATORS = ('<', '<=', '>', '>=', '==', '!=')


#: How many times a clocked code path has been entered in this process.
#: The guard behind "a stateless model pays nothing" is structural -- no
#: clocked path is entered for a tree whose state table is empty -- and
#: this counter is how a test asserts it rather than hoping for it.
_ENTERED = 0


def entered():
    """How many times a clocked code path has run."""
    return _ENTERED


def _enter():
    global _ENTERED
    _ENTERED += 1


##############################################
# One compiled committing relation

class Committing:
    """One committing relation, compiled against one clocked tree.

    Holds the qualified ids its sources and targets are addressed by, the
    two callables the project wrote, and -- per DRIVER a request could
    move -- the `_Jump` whose level this relation's events are located
    on. The jump is built ONCE, here, because `_KinkCuts` compiles a
    graph and a request must cost no compile.
    """

    def __init__(self, record, source_ids, target_ids, primitive, level,
                 jumps, at, law, law_graphs=()):
        self.record = record
        self.source_ids = tuple(source_ids)
        self.target_ids = tuple(target_ids)
        self.primitive = primitive
        self.level = level
        self.jumps = jumps
        self.at = at
        self.law = law
        #: The law applied ONCE to a symbolic token per source, one
        #: graph per target in written order: what `_checked_law` has
        #: always built to check the shape, RETAINED rather than thrown
        #: away, because it is what a version 8 document publishes. A
        #: target whose law returns a plain number holds that number
        #: here (OpenSpec change ``publish-the-clocked-machine``,
        #: design section 6).
        self.law_graphs = tuple(law_graphs)
        self.described = record.described()
        #: What a message from the shared locator calls the thing being
        #: moved. A clocked event lands the INPUT, not a coordinate, so
        #: this names the input the request is on; it is set per request.
        self.coordinate = ', '.join(self.target_ids)

    def __repr__(self):
        return f'<committing {self.described}>'

    ##############################################
    # Locating

    def moves_with(self, input_id):
        """Whether this relation's level can move when `input_id`
        does."""
        return input_id in self.jumps

    def next_event(self, bank, input_id, start, delta):
        """The earliest RISING crossing of this relation's level on the
        straight path from `start` to `start + delta`, as
        `(fraction, landing)`, or None.

        `fraction` is the fraction of THIS path, which the caller
        rescales to the whole request; `landing` is the nearest
        representable value of the input on the FAR side of the surface,
        and it is the value the event both reads and resumes from, so no
        event can fire twice.
        """
        jump = self.jumps.get(input_id)
        if jump is None or delta == 0.0:
            return None
        standing = {identifier: bank[identifier]
                    for identifier in self.source_ids}
        standing[input_id] = start
        steps = {identifier: 0.0 for identifier in self.source_ids}
        steps[input_id] = delta
        found = self._located(jump, standing, steps, input_id, delta)
        if not found:
            return None
        edges = [0.0] + [where for where, _level in found] + [1.0]

        def level_at(value):
            values = dict(standing)
            values[input_id] = value
            return jump.argument.evaluate(values)

        def branch_at(value):
            return _branch_of(jump, level_at(value))

        direction = math.copysign(1.0, delta)
        endpoint = start + delta
        scale = max(abs(start), abs(endpoint))
        for index, (where, _level) in enumerate(found):
            if where == 0.0:
                # The path BEGINS on this surface, so there is no piece
                # behind it to read a branch from: the branch the
                # request stands in is read AT THE START, and the far
                # side is asked for at the NEXT REPRESENTABLE VALUE the
                # path reaches. Where that reads the same branch the
                # machine already stands on the far side -- a request
                # resuming from its own landing -- and the surface is
                # not this request's. Where it differs, the landing is
                # that value and the surface is this request's first
                # event (closure 1).
                before = branch_at(start)
                if branch_at(math.nextafter(
                        start, math.copysign(math.inf, delta))) == before:
                    continue
            else:
                before = _branch_of(jump, self._level_at(
                    jump, standing, steps, (edges[index] + where) / 2.0))
            landing = far_side_of(
                branch_at, before, start + delta * where, direction,
                lambda: _unlanded(self, jump), scale=scale)
            if direction * (landing - endpoint) > 0.0:
                # The landing lies BEYOND this request's endpoint, which
                # a STRICT comparison reached exactly does: the crossing
                # belongs to the request whose PATH CONTAINS its
                # landing, and that is the next one, which begins on
                # this surface and takes it at fraction zero.
                continue
            # RISING is read from the branch the path came from and the
            # branch AT THE LANDING -- which is the nearest point of the
            # piece the path is going into, and the only reading
            # available where the crossing is the request's own endpoint
            # (design section 6).
            if branch_at(landing) > before:
                return where, landing
        return None

    def _located(self, jump, standing, steps, input_id, delta):
        """Every crossing of this relation's level on the path, in path
        order.

        BOTH ends are taken: a request that ends exactly ON a surface
        has reached it -- `move('crank', by=360)` with `at =
        floor(crank / 360)` IS one stroke -- and a request that BEGINS
        on one has reached it too when its far side lies ahead. Which
        of the two requests a surface belongs to is decided by the
        LANDING and not here: `next_event` keeps the crossing whose
        landing its own path contains, so a request resuming from its
        own landing takes nothing and a STRICT surface reached exactly
        at an endpoint is left for the request that begins on it
        (closure 1 of ``publish-the-clocked-machine``; the fraction
        reading ADR-125 stated lost that event entirely).

        `_solved` excludes a piece's left end, which is right for an
        interior breakpoint -- the sub-piece before it reached that
        surface -- so the path's OWN opening surface is added here,
        read with `_on_surface` off the level the path starts at.
        """
        plan = JumpPlan(None, (jump,))
        inner = {}
        try:
            if jump.shape == 'kinked' and jump.kinks:
                def at(fraction):
                    return _along(standing, steps, fraction)

                breaks = jump.kinks.between(at, 0.0, 1.0)
                edges = (0.0,) + breaks + (1.0,)
                found = []
                for low, high in zip(edges, edges[1:]):
                    found.extend(plan._solved(
                        jump, standing, steps, inner, low, high,
                        self.described, self.coordinate, closed=True))
                found = _deduplicated(found)
            else:
                found = plan._solved(jump, standing, steps, inner, 0.0, 1.0,
                                     self.described, self.coordinate,
                                     closed=True)
        except TooManyCrossings as failure:
            raise _too_many_events(self, input_id, delta,
                                   getattr(failure, 'count', None)) from None
        if len(found) > _MAX_CROSSINGS:
            raise _too_many_events(self, input_id, delta, len(found))
        found = sorted(found, key=lambda entry: entry[0])
        opening = self._level_at(jump, standing, steps, 0.0)
        if _on_surface(jump, opening) and not (found and found[0][0] == 0.0):
            found.insert(0, (0.0, opening))
        return found

    def _level_at(self, jump, standing, steps, fraction):
        return jump.argument.evaluate(_along(standing, steps, fraction))

    ##############################################
    # Committing

    def commit(self, bank, input_id, landing):
        """This relation's targets and the values it writes at one
        event, read from the PRE-EVENT bank with the input at its
        landing.

        The callables are the project's own, called with the bank's
        NUMBERS positionally, in written order. No graph is walked and
        nothing is substituted: the symbolic inspection happened once,
        at construction.
        """
        values = dict(bank)
        values[input_id] = landing
        arguments = [values[identifier] for identifier in self.source_ids]
        returned = self.law(*arguments)
        if len(self.target_ids) == 1:
            returned = (returned,)
        else:
            returned = _checked_shape(self, returned)
        written = {}
        for identifier, declaration, value in zip(
                self.target_ids, self.targets, returned):
            if isinstance(value, (int, float)) and not math.isfinite(value):
                raise _not_a_value(self, identifier, value)
            written[identifier] = declaration.committed(value)
        return written


def _not_a_value(relation, identifier, value):
    """A commit that computed an infinity or a NaN.

    Judged BEFORE `State.committed` rounds, so an integer state refuses
    by the same message rather than by `round`'s own `OverflowError`,
    which names neither the relation nor the state. The REQUEST is
    refused whole and commits nothing, ADR-125's atomicity: a bank
    holding a non-finite value poses nothing, satisfies no bound and
    carries no later event.

    It is also the contract the DOCUMENT states. A document cannot
    express a raise, so the export requirement "A published commit says
    what it reads, writes and fires on" has a consumer that computes a
    non-finite commit value refuse the request rather than bank it; the
    framework is the other runtime of that contract, and the two must
    refuse the same request (ADR-128, design section 16; follow-up of
    2026-09-17).
    """
    return ClockedError(
        f'{relation.described}: the law {relation.law!r} computed '
        f"{value!r} for the state '{identifier}', which is not a value a "
        f'machine can stand at -- a bank holding it poses nothing, '
        f'satisfies no bound and carries no later event. The request '
        f'committed nothing: the bank and the tree stand as they were. A '
        f'consumer of the published document refuses such a commit for '
        f'the same reason, a document being unable to express a raise.')


def _checked_shape(relation, returned):
    length = None
    if not isinstance(returned, str):
        try:
            length = len(returned)
        except TypeError:
            length = None
    if length != len(relation.target_ids):
        raise ClockedError(
            f'{relation.described}: the law {relation.law!r} returned '
            f'{returned!r} for {len(relation.target_ids)} targets '
            f'({", ".join(relation.target_ids)}), which is not a sequence '
            f'of exactly {len(relation.target_ids)} values. A value slot '
            f'accepts whatever is put into it, and a wrong-shaped return '
            f'would be a state nobody stated.')
    return returned


def _unlanded(relation, jump):
    from .program import _unlanded as unlanded

    return unlanded(relation.described, relation.coordinate, jump)


def _two_answers(identifier, first, second, input_id, landing):
    """Two committing relations writing ONE state at ONE event.

    Several relations may write one state -- that is what a register
    digit written at a stroke end and again at a clearing reach needs --
    but at one landing there is one answer or none. The REQUEST is
    refused, naming the state, both relations and the landing, and it
    commits nothing: the class bodies are innocent, because a landing is
    not a fact a class body has (design section 3, amended 2026-09-17).
    """
    return ClockedError(
        f"the state '{identifier}' is written by two committing "
        f'relations at ONE event -- {first.described} and '
        f'{second.described} both fire at {input_id} = {landing!r}. A '
        f'state may be written at several DIFFERENT events, and has one '
        f'answer at each: fold these two laws into one, or move one '
        f"event off the other's landing. The request committed nothing.")


def _too_many_events(relation, input_id, delta, count):
    reached = 'more than' if count is None else count
    return TooManyEvents(
        f"the request move('{input_id}', by={delta!r}) would cross "
        f'{reached} surfaces of the committing relation '
        f'{relation.described}, and {_MAX_CROSSINGS} is the most one '
        f'relation is admitted on one request. The request committed '
        f'nothing: the bank and the tree stand as they were. Split it '
        f'into shorter requests.')


##############################################
# Compiling a clocked tree

def compile_clocked(root, drivers, states, instructions, clock=False):
    """Every committing relation of `root`'s tree, compiled, with every
    refusal a TREE can state.

    A class body cannot see what the whole tree writes, nor what shape an
    `at` expression has once its sources are known, so the refusals here
    are the ones whose facts first exist at simulation construction.

    `clock` says whether this root declares the ELAPSED base, and so
    whether `time` is a banked value a request can move: under it the
    clock joins the drivers in the per-input classification loop, and a
    relation the clock alone moves is admitted (OpenSpec change
    ``time-without-running``, design section 5).
    """
    _enter()
    records = _records_of(root)
    # Which states the tree writes AT ALL. Several relations may write
    # one state -- a register digit is written by the stroke that adds
    # to it and by the clearing reach that zeroes it, two events on two
    # inputs -- so this is a set and not a claim of ownership. Two
    # relations writing one state AT ONE LANDING is the conflict, and it
    # is judged by the request, which is the only place a landing exists
    # (design section 3, amended 2026-09-17).
    written = set()
    for _node, record in records:
        for target in record.targets:
            written.add(_identifier(root, target))
    for identifier in sorted(states):
        if identifier not in written:
            raise ClockedError(
                f"the state '{identifier}' is declared and nothing writes "
                f'it: no committing relation of this tree names it as a '
                f'target. A state is written by the machine at an event, '
                f'so a state with no committing relation is a value that '
                f'could never change. State the commit, or declare a '
                f'Driver instead.')
    for name, (_node, path, instruction) in sorted(instructions.items()):
        named = (instruction.by if instruction.relative
                 else instruction.targets)
        if len(named) != 1:
            # An instruction under a clocked root is ONE REQUEST, and a
            # request names exactly one moving input. Two would be a
            # SEQUENCE -- a program, and the G-code layer's job, as
            # `Instruction`'s own docstring says -- and none would be a
            # button that moves nothing. Refused HERE, where the facts
            # first exist, so no document can carry an instruction a
            # consumer cannot play (OpenSpec change
            # ``play-the-instruction``, design section 2).
            qualified = sorted('.'.join(path + (target,)) for target in named)
            raise ClockedError(
                f"the instruction '{name}' names "
                f'{len(named)} drivers'
                f'{": " + ", ".join(qualified) if qualified else ""}. '
                f'Under a CLOCKED root an instruction is ONE REQUEST, and '
                f'a request names exactly one moving input, so an '
                f'instruction here names exactly one driver. Two drivers '
                f'would be a sequence, which is a program and not an '
                f'instruction; none would move nothing. State one '
                f'instruction per driver.')
        for target in named:
            identifier = '.'.join(path + (target,))
            if identifier in states:
                raise ClockedError(
                    f"the instruction '{name}' targets '{identifier}', "
                    f'which is a State. An instruction moves a DRIVER to '
                    f'a target over a duration, and a state is written by '
                    f'the machine at an event, never ramped to a value a '
                    f'declaration names.')
    return tuple(_compiled(root, node, record, drivers, states, clock)
                 for node, record in records)


def _records_of(root, node=None, found=None):
    """Every resolved committing relation in `root`'s tree, in tree
    order, each with the ASSEMBLY that states it -- which is what a
    published commit's `stated_by` names, so a consumer's refusal names
    what a reader can find in the model.

    Walked over `_rest_children`, the linked rest structure every
    qualified pass descends -- idempotent, and already built by the
    enumeration this construction just ran, so the walk discovers
    nothing and renders nothing.
    """
    from solid_node.node.assembly import _rest_children

    if found is None:
        found = []
    node = root if node is None else node
    found.extend((node, record)
                 for record in node.__dict__.get('_commitments', ()))
    if getattr(node, '_states', None) is None:
        # A leaf holds no snapshot and no children of its own, and
        # cannot declare a state.
        return found
    for child in _rest_children(node):
        _records_of(root, child, found)
    return found


def _identifier(root, end):
    """The qualified id one end of a committing relation is addressed
    by: the same rule, and the same function, a driver's id follows."""
    return driver_id(instance_path(end.node, root), end.name)


def _compiled(root, stated_by, record, drivers, states, clock=False):
    """One committing relation, compiled: its ids, its event level,
    its two callables and the assembly class that stated it."""
    source_ids = tuple(_identifier(root, end) for end in record.sources)
    target_ids = tuple(_identifier(root, end) for end in record.targets)

    def refuse(detail):
        raise ClockedError(f'{record.described()}: {detail}')

    for identifier in source_ids:
        if identifier == CLOCK_NAME and clock:
            # The root's own clock: a banked value under the elapsed
            # base, and something a request moves (design section 5).
            continue
        if identifier == CLOCK_NAME:
            refuse(f"its source '{identifier}' is this root's clock, and "
                   f'the root declares no time base. A clocked model has '
                   f'a clock only where it says so: declare '
                   f'time = Time.elapsed() on the root, elapsed seconds '
                   f'that never wrap.')
        if identifier not in drivers and identifier not in states:
            refuse(f"its source '{identifier}' is neither a declared "
                   f'driver nor a declared state of this tree.')
    tokens = [symbol(identifier) for identifier in source_ids]
    primitive, level = _event_level(record, tokens, refuse)
    law, law_graphs = _checked_law(record, tokens, target_ids, refuse)
    jumps = {}
    for identifier in source_ids:
        if identifier not in drivers and not (clock
                                              and identifier == CLOCK_NAME):
            # Only a DRIVER -- or, under the elapsed base, the CLOCK --
            # moves along a request path; a state is constant between
            # events, which is exactly why a level that reads its own
            # target is simple here (design section 8).
            continue
        shape = _shape_of(_standing_except(level, identifier))
        if shape is None:
            refuse(f"its event level curves as '{identifier}' moves: "
                   f'{_curving(level, identifier)}. A clocked event is '
                   f'SOLVED and never searched, so an event level must '
                   f'be affine in the moving driver, or kinked by abs, '
                   f'min or max over quantities that are. Restate the '
                   f'event on a level the driver enters linearly.')
        jumps[identifier] = _Jump(primitive, '$j0', GraphValue(level), shape)
    if not jumps:
        # Every source a state. A state is constant between events, so
        # nothing a request can move enters this level: it would never
        # cross anything, never fire, and sit in the model silently
        # doing nothing. Refused by name rather than left inert
        # (design section 5, added 2026-09-17).
        reach = ('a DRIVER, or the CLOCK under a root declaring '
                 'time = Time.elapsed()' if clock else 'a DRIVER')
        also = ('' if clock else
                ', nor with a clock: this root declares no time base')
        refuse(f"its event level moves with no declared driver{also}: its "
               f"sources are {', '.join(source_ids)}, and every one of "
               f'them is a state, which is constant between events. An '
               f'event is located on the motion of {reach}, so name the '
               f'input whose motion reaches this event among the '
               f'sources.')
    relation = Committing(record, source_ids, target_ids, primitive, level,
                          jumps, record.at, law, law_graphs)
    relation.targets = tuple(states[identifier]
                             for identifier in target_ids)
    relation.stated_by = type(stated_by).__name__
    return relation


def _event_level(record, tokens, refuse):
    """`at`'s ONE jump node and its level quantity.

    `at` returns exactly one jump node -- `floor(x)`, `ceil(x)`,
    `sign(x)` or a comparison -- whose LEVEL QUANTITY and SURFACES are
    the ones the jump vocabulary already defines. "Integer valued" is not
    a structural property the framework can check, and checking it by
    sampling is exactly the search a clocked event exists to avoid; one
    jump node IS checkable, and it gives the level and the surfaces for
    free.
    """
    try:
        returned = record.at(*tokens)
    except Exception as failure:
        refuse(f'the at= expression {record.at!r} cannot be applied to '
               f'symbols ({type(failure).__name__}: {failure}). An event '
               f'is an expression over its sources: it is applied once, '
               f'to a token per source, and the graph it builds is what '
               f'the solver locates crossings on. Write it with '
               f'solid_node.math, whose primitives are symbolic.')
    if isinstance(returned, (bool, int, float)):
        refuse(f'the at= expression returned {returned!r}, which is a '
               f'number and not an event: one event is one surface '
               f'family, stated as one floor, ceil, sign or comparison '
               f'over the relation\'s sources.')
    root, jumps = checked_expression(returned, refuse, 'an event')
    ours = [node for node in jumps
            if (node.kind == 'call' and node.op in _EVENT_CALLS)
            or (node.kind == 'binop' and node.op in _EVENT_OPERATORS)]
    if len(jumps) != 1 or len(ours) != 1 or jumps[0] is not root:
        written = ', '.join(sorted({node.op for node in jumps})) or 'none'
        refuse(f'its at= is not ONE jump node: one event is one surface '
               f'family, and two are two committing relations. An event '
               f'is stated as floor(x), ceil(x), sign(x) or a comparison '
               f'a < b, and this expression is rooted at '
               f'{root.op or root.kind!r} over the jump primitives '
               f'[{written}]. A remainder a % b is not admitted either: '
               f'it is not integer valued, so its steps are not events.')
    return root.op, _argument_graph(root, {})


def _checked_law(record, tokens, target_ids, refuse):
    """`law`'s callable AND its graphs, with the expression checked
    exactly as a running law's is, and with ONE difference: no jump
    plan, no skeleton and no refusal of a law made entirely of jumps.

    A commit is evaluated at a POINT and never integrated, so every jump
    primitive in it means what it says and nothing is subtracted --
    `floor(crank / 360) % 10` is a digit, where under a run it states
    arithmetic rather than a mechanism (design section 7).

    The graph is walked ONCE, here, and never again to compute a value:
    the executor calls the project's own callable with the bank's
    numbers. Checking the shape now is what stops a project from writing
    a commit law the framework accepts and the document cycle cannot
    publish -- and RETAINING what the check built is the whole of what
    the simulation layer owes the document, because the graph is what a
    version 8 document carries (OpenSpec change
    ``publish-the-clocked-machine``, design section 6).
    """
    try:
        returned = record.law(*tokens)
    except Exception as failure:
        refuse(f'the law {record.law!r} cannot be applied to symbols '
               f'({type(failure).__name__}: {failure}). A commit law is '
               f'an expression over its sources: it is applied once, to '
               f'a token per source, and the graph it builds is what the '
               f'document will carry.')
    length = None
    if not isinstance(returned, (str, bytes)):
        try:
            length = len(returned)
        except TypeError:
            length = None
    if len(target_ids) == 1:
        if length is not None:
            refuse(f'the law {record.law!r} returned {returned!r} for the '
                   f'ONE target {target_ids[0]}, which is a sequence of '
                   f'{length} values and not one value. A law returns one '
                   f'value for one target, and as many values as there '
                   f'are targets for several, in written order.')
        values = (returned,)
    else:
        if length != len(target_ids):
            refuse(f'the law {record.law!r} returned {returned!r} for '
                   f'{len(target_ids)} targets '
                   f'({", ".join(target_ids)}), which is not a sequence '
                   f'of exactly {len(target_ids)} values.')
        values = returned
    graphs = []
    for value in values:
        if isinstance(value, bool):
            refuse(f'the law returned {value!r}, which is neither a '
                   f'number nor an expression.')
        if isinstance(value, (int, float)):
            # A law returning a plain number: the commit writes that
            # value, so the graph is the literal and never an absence.
            graphs.append(float(value))
            continue
        root, _jumps = checked_expression(value, refuse, 'a commit law')
        graphs.append(root)
    return record.law, tuple(graphs)


def _standing_except(level, moving):
    """`level` with every free name but `moving` replaced by a standing
    placeholder.

    `_shape_of` reads a `$`-prefixed name as a CONSTANT on the piece
    being cut, which is exactly what every other source is along a
    request path: only one driver moves. The substitution is structural
    and carries no number, so the classification cannot depend on what
    the bank happens to hold -- which is why it is decided ONCE, at
    construction, and never again.
    """
    from solid_node.expression_graph import ExpressionNode, postorder

    replaced = {}
    for node in postorder([level]):
        if node.kind == 'name' and node.text != moving:
            replaced[node] = ExpressionNode('name', text=f'$standing')
        elif node.children:
            children = tuple(replaced.get(child, child)
                             for child in node.children)
            if children != node.children:
                replaced[node] = ExpressionNode(
                    node.kind, node.op, children, node.text)
    return replaced.get(level, level)


def _curving(level, moving):
    """How a curved level is described in its refusal: the primitives
    the moving driver passes through."""
    from solid_node.expression_graph import postorder

    names = []
    for node in postorder([level]):
        if node.kind == 'call':
            names.append(node.op)
        elif node.kind == 'binop' and node.op in ('*', '/', '^'):
            names.append(node.op)
    found = ', '.join(sorted(set(names))) or 'its arithmetic'
    return f"'{moving}' enters it through {found}"


##############################################
# One compiled constraint

#: The free name a constraint level reads the bounded coordinate's OWN
#: value under: the value it held when the REQUEST STARTED, which is
#: ADR-109's committed-state rule with the request in the tick's place.
#: A `$`-prefixed name, so `_shape_of` reads it as the constant on the
#: path it is, and so it can never collide with a qualified bank id.
_OWN = '$own'

#: What a refusal from the shared bound compile calls itself here. A
#: clocked simulation banks no joint coordinate, so a refusal raised on
#: its behalf must not say "the run".
_AUTHORITY = 'the clocked simulation'

#: The name a law's source token is applied under while its graph is
#: being composed. Substituted away before anything reads the level, and
#: deliberately NOT `$`-prefixed, so a leak would be seen as a moving
#: name rather than silently read as a constant.
_TOKEN = '__source%d__'


def _text(graph):
    """One expression graph as the document's own text.

    Used where a LISTING is taken of a graph -- the identity's canonical
    lines -- and nowhere a document is written: a published slot holds
    the native graph, which the document's binding pass compiles.
    """
    return str(GraphValue(as_node(graph)))


def _floored_remainder(graph):
    """`graph` with every `%` node replaced by the FLOORED remainder the
    clocked executor actually computes.

    The executor does not evaluate a commit law's graph at all: it calls
    the project's own Python callable with the bank's numbers, and
    Python's float `%` takes the sign of the DIVISOR. The document's `%`
    is the truncated remainder -- the sign of the DIVIDEND -- which both
    runtimes already evaluate identically (`GraphValue.evaluate` spells
    it `math.fmod`, and the viewer's is JavaScript's native `%`). So a
    law graph published as written would not mean what the executor
    computed, and the breach is INSIDE the framework rather than between
    the runtimes.

    CPython's `float_rem` is `mod = fmod(a, b); if (mod) { if ((b < 0)
    != (mod < 0)) mod += b; } else mod = copysign(0.0, b);` -- `fmod` is
    exact and the correction is a single IEEE addition -- so the
    document's own vocabulary reproduces it, with the same one rounding,
    as

        r + b * ((r != 0) * ((r < 0) != (b < 0)))

    The ONE divergence is the SIGN of a zero result under a negative
    divisor, which compares equal as a number in both runtimes and which
    nothing in the published vocabulary distinguishes.

    This applies to a LAW graph and to nothing else. An `at` cannot
    carry a `%` in any position -- `%` IS a jump and an event admits one
    jump node which must be a floor, ceil, sign or comparison -- and a
    CHAIN, a BOUND and a constraint LEVEL keep the document's `%`,
    because the framework EVALUATES those through the graph, so their
    published form already says exactly what the clip computed (design
    section 16).
    """
    root = as_node(graph)
    replaced = {}
    for node in postorder([root]):
        children = tuple(replaced.get(child, child) for child in node.children)
        if node.kind == 'binop' and node.op == '%':
            left, right = children
            remainder = _binop('%', left, right)
            correction = _binop(
                '*',
                _binop('!=', remainder, _num(0.0)),
                _binop('!=', _binop('<', remainder, _num(0.0)),
                       _binop('<', right, _num(0.0))))
            replaced[node] = _binop('+', remainder,
                                    _binop('*', right, correction))
        elif children != node.children:
            replaced[node] = ExpressionNode(node.kind, node.op, children,
                                            node.text)
    return replaced.get(root, root)


def _published_law(graph):
    """One commit law expression, as the document carries it.

    A law returning a plain NUMBER publishes the number as a literal
    expression and never a null: a commit's law IS the value written,
    so a constant is an answer and not an absence -- the asymmetry with
    a running law edge, whose `null` means "contributes no increment".
    """
    if isinstance(graph, float):
        return GraphValue(_num(graph))
    return GraphValue(_floored_remainder(graph))


def _published_bound_value(bound, own):
    """One compiled bound, as the document carries it: a NUMBER where it
    is numeric, and otherwise the graph with `$own` replaced by the
    document's published own-name.

    `$own` cannot travel: the document's expression language admits
    exactly one `$`-name, `$t` (`core/expressions.py`), so a bound
    published with it would not even tokenize (design section 8).
    """
    node = as_node(bound)
    if node.kind == 'num':
        return float(node.text)
    return GraphValue(_substituted(node, {_OWN: _free(own)}))


def _renamed_plan(plan, own):
    """`plan` with `$own` replaced by the published own-name throughout
    its skeleton and every jump's level."""
    mapping = {_OWN: _free(own)}
    return JumpPlan(
        GraphValue(_substituted(as_node(plan.skeleton), mapping)),
        tuple(_Jump(jump.primitive, jump.placeholder,
                    GraphValue(_substituted(as_node(jump.argument), mapping)),
                    jump.shape)
              for jump in plan.jumps))


def _own_name(published):
    r"""The free name a published bound reads its own coordinate under.

    `_own`, lengthened by a leading underscore for as long as some
    published id EQUALS it -- `_placeholder_prefix`'s own rule with the
    digit-suffix match replaced by equality, there being one own-name
    and not a series (design section 8).
    """
    name = '_own'
    while name in published:
        name = '_' + name
    return name


def _num(value):
    return ExpressionNode('num', text=repr(float(value)))


def _free(text):
    return ExpressionNode('name', text=text)


def _binop(op, left, right):
    return ExpressionNode('binop', op, (left, right))


def _substituted(root, mapping):
    """`root` with every free name in `mapping` replaced by the SUBTREE
    it stands for.

    Composition is substitution and NEVER simplification: the graph goes
    on performing the arithmetic the enumeration performs, over the
    identical native values, which is what makes the clocked simulation
    fit to judge its own constraints (design sections 2 and 10).
    """
    if not mapping:
        return root
    replaced = {}
    for node in postorder([root]):
        if node.kind == 'name' and node.text in mapping:
            replaced[node] = mapping[node.text]
        elif node.children:
            children = tuple(replaced.get(child, child)
                             for child in node.children)
            if children != node.children:
                replaced[node] = ExpressionNode(
                    node.kind, node.op, children, node.text)
    return replaced.get(root, root)


def _slot_name(root, slot):
    from solid_node.node.qualified import DriverIdError

    try:
        return driver_id(instance_path(slot.node, root), slot.name)
    except DriverIdError:
        return f'{type(slot.node).__name__}.{slot.name}'


class _Chains:
    """Every bounded coordinate, and every coordinate a bound reads,
    composed into ONE expression graph over the bank.

    A relation's untimed meaning is absolute -- the driven end IS the law
    applied to its sources -- so composing is SUBSTITUTION: the
    determining relation's law graph, with each source name replaced by
    that source's own graph, down to the bank's ids, which stay free
    names. A wiring contributes its scale, a derived coordinate its
    linear formula, a `law=` relation its inspected graph, and an
    INTERMEDIATE PORT is composed through and never stored -- which is
    exactly how the Curta's selectors are wired.

    What the bank cannot reach this way is refused BY NAME, naming the
    joint, the node, the side and where the chain broke: a stop that can
    never stop is a mistake in the model (design section 3).
    """

    def __init__(self, root, bank, coordinates):
        from solid_node.motion.joints import declared_joints
        from solid_node.motion.ports import get_coordinate

        from .program import _units

        self.root = root
        self.bank = bank
        self.slots = {}
        self.joints = {}
        for identifier, (node, name) in coordinates.items():
            self.slots[identifier] = get_coordinate(node, name)
            for joint in declared_joints(type(node)).values():
                if name in joint.coordinates:
                    self.joints[identifier] = (node, joint)
                    break
        # What the REST RENDER solved, read off its own records: the one
        # authority on which relation, wiring or formula determines each
        # coordinate, and in which direction.
        self.determined = {}
        for assembly, _path, records, formulas, wirings in _units(root):
            for record in records:
                if record.direction == 'forward':
                    targets = record.driven_ends
                elif record.direction == 'backward':
                    targets = record.driver_ends
                else:
                    continue
                for index, end in enumerate(targets):
                    if end.slot is not None:
                        self.determined[id(end.slot)] = (
                            'law', assembly, record, index)
            for wiring in wirings:
                self.determined[id(wiring.target)] = (
                    'wiring', assembly, wiring, 0)
            for formula in formulas:
                slot = formula.slot_of(assembly)
                if slot.binder is formula:
                    self.determined[id(slot)] = (
                        'formula', assembly, formula, -1)
                    continue
                for index, (end, _factor) in enumerate(
                        formula.resolved_terms(assembly)):
                    if end.slot is not None and end.slot.binder is formula:
                        self.determined[id(end.slot)] = (
                            'formula', assembly, formula, index)
        self.cache = {}

    ##############################################
    # The chain

    def of(self, identifier, refuse, what):
        """`identifier`'s chain: a bank id is a free NAME, and a joint
        coordinate is the composition that determines it."""
        if identifier in self.bank:
            return _free(identifier)
        slot = self.slots.get(identifier)
        if slot is None:
            refuse(f'{what} is neither a declared input of this tree nor '
                   f'one of its joint coordinates, so the bank cannot '
                   f'reach it at all.')
        return self._of_slot(slot, refuse, what, ())

    def _of_end(self, end, refuse, what, seen):
        if end.slot is None:
            from .program import _qualified

            identifier, qualified = _qualified(self.root, end)
            if not qualified or identifier not in self.bank:
                refuse(f"{what} is determined by '{identifier}', which is "
                       f'neither a declared driver nor a declared state of '
                       f'this tree, so the bank cannot reach it.')
            return _free(identifier)
        return self._of_slot(end.slot, refuse, what, seen)

    def _of_slot(self, slot, refuse, what, seen):
        key = id(slot)
        found = self.cache.get(key)
        if found is not None:
            return found
        if key in seen:
            refuse(f'{what} is determined by a CYCLE the rest render left '
                   f'standing: {_slot_name(self.root, slot)} is reached '
                   f'from itself. A clocked pose retains nothing between '
                   f'requests, so there is no value to break the cycle '
                   f'with.')
        binder = getattr(slot, 'binder', None)
        if binder is None:
            if getattr(slot, '_value', None) is None:
                # NOTHING determines it -- no relation, no wiring, no
                # derived formula and no author code -- so it is a
                # DECORATIVE range on a part that rests, and the chain is
                # the constant it stands at (design section 3).
                self.cache[key] = found = _num(0.0)
                return found
            # The assembly whose OWN simulate phase bound it, which the
            # rest render recorded -- not the node the slot belongs to,
            # which is typically the child being posed.
            author = getattr(slot, '_bound_by', None) or slot.node
            refuse(f'{what} is bound BY HAND, in '
                   f'{type(author).__name__}.simulate(): its value is '
                   f'whatever that code computes, from whatever it reads, '
                   f'so nothing can follow it along a request path. State '
                   f'the relation that moves '
                   f"'{_slot_name(self.root, slot)}', or drop the range.")
        entry = self.determined.get(key)
        if entry is None:
            refuse(f'{what} is bound by {binder!r}, for which the rest '
                   f'render recorded no chain, so the bank cannot reach '
                   f'it.')
        kind, assembly, obj, index = entry
        seen = seen + (key,)
        if kind == 'law':
            graph = self._law(assembly, obj, index, refuse, what, seen)
        elif kind == 'wiring':
            graph = self._of_slot(obj.slot, refuse, what, seen)
        else:
            graph = self._formula(assembly, obj, index, refuse, what, seen)
        if getattr(slot, 'scale', None) is not None:
            # The one conversion the binding path applies, applied here
            # as well: `ports.bind` multiplies by the sink's declared
            # scale, so a chain that skipped it would disagree with the
            # pose it has to agree with (design section 10).
            graph = _binop('*', graph, _num(slot.scale))
        self.cache[key] = graph
        return graph

    def _law(self, assembly, record, index, refuse, what, seen):
        described = (f'{record.described()}, stated by '
                     f'{type(assembly).__name__}')
        if record.relation.self_read is not None:
            refuse(f'{what} is driven by {described}, whose law READS the '
                   f'coordinate it drives. A retained read is a HISTORY, '
                   f'and a clocked pose retains nothing between requests: '
                   f'there is no value to read.')
        if record.direction == 'forward':
            sources, targets = record.driver_ends, record.driven_ends
        else:
            sources, targets = record.driven_ends, record.driver_ends
        tokens = [symbol(_TOKEN % position)
                  for position in range(len(sources))]
        try:
            if record.direction == 'backward':
                returned = record.law.inverse(tokens[0])
            else:
                returned = record.law.forward(*tokens)
        except Exception as failure:
            refuse(f'{what} is driven by {described}, whose law '
                   f'{record.law!r} cannot be applied to symbols '
                   f'({type(failure).__name__}: {failure}). A chain from '
                   f'the bank to a bounded coordinate is an expression '
                   f'over the bank: write the law with solid_node.math, '
                   f'whose primitives are symbolic.')
        if len(targets) == 1:
            values = (returned,)
        else:
            try:
                length = len(returned)
            except TypeError:
                length = None
            if length != len(targets):
                refuse(f'{what} is driven by {described}, whose law '
                       f'returned {returned!r} for {len(targets)} driven '
                       f'ends, which is not a sequence of exactly '
                       f'{len(targets)} values.')
            values = returned
        graph = self._expression(values[index], refuse, what, described)
        names = free_names(graph)
        mapping = {}
        for position, end in enumerate(sources):
            token = _TOKEN % position
            if token in names:
                mapping[token] = self._of_end(end, refuse, what, seen)
        return _substituted(graph, mapping)

    def _formula(self, assembly, formula, index, refuse, what, seen):
        described = (f"the derived coordinate '{formula.described()}' "
                     f'({formula.written})')
        terms = formula.resolved_terms(assembly)
        constant = float(formula.resolved_constant(assembly))
        if index < 0:
            total = _num(constant)
            for end, factor in terms:
                total = _binop('+', total, _binop(
                    '*', self._of_end(end, refuse, what, seen),
                    _num(factor)))
            return total
        # Solved BACKWARD into one term, exactly as `Edge._linear` states
        # it: a derived coordinate is a coefficient map and a constant,
        # so the rearrangement is exact.
        own = float(terms[index][1])
        if own == 0.0:
            refuse(f'{what} is solved from {described}, in which its own '
                   f'coefficient is zero, so the formula does not '
                   f'determine it.')
        value = _binop('-', self._of_slot(
            formula.slot_of(assembly), refuse, what, seen), _num(constant))
        for position, (end, factor) in enumerate(terms):
            if position == index:
                continue
            value = _binop('-', value, _binop(
                '*', self._of_end(end, refuse, what, seen), _num(factor)))
        return _binop('/', value, _num(own))

    def _expression(self, value, refuse, what, described):
        """One law's return as the graph the chain composes, checked by
        the SAME walk a running law and a commit law are checked by."""
        if isinstance(value, bool):
            refuse(f'{what} is driven by {described}, whose law returned '
                   f'{value!r}, which is neither a number nor an '
                   f'expression.')
        if isinstance(value, (int, float)):
            return _num(value)
        if not isinstance(value, OpenSCADConstant):
            refuse(f'{what} is driven by {described}, whose law returned '
                   f'{value!r}, which is neither a number nor an '
                   f'expression over its sources.')

        def broke(detail):
            refuse(f'{what} is driven by {described}, and {detail}')

        root, _jumps = checked_expression(value, broke, 'a chain to a bound')
        return root


class Stop:
    """ONE bound met on a request path: what stopped, which side of its
    range, what that bound evaluated to at the landing, what the
    coordinate is worth there, where the input landed, and the fraction
    of the REQUESTED travel that was.

    ADR-108's vocabulary, and nothing is added to it. Several
    constraints met at ONE landing are several entries of one stop,
    exactly as several relations at one landing are one event.
    """

    __slots__ = ('coordinate', 'side', 'bound', 'value', 'input', 'fraction')

    def __init__(self, coordinate, side, bound, value, value_of_input,
                 fraction):
        self.coordinate = coordinate
        self.side = side
        self.bound = bound
        self.value = value
        self.input = value_of_input
        self.fraction = fraction

    def __repr__(self):
        return (f'<stop {self.coordinate} {self.side} at {self.bound} '
                f'(value {self.value}, input {self.input}, '
                f'{self.fraction:.4f})>')

    def __eq__(self, other):
        return (isinstance(other, Stop)
                and (self.coordinate, self.side, self.bound, self.value,
                     self.input, self.fraction)
                == (other.coordinate, other.side, other.bound, other.value,
                    other.input, other.fraction))


class Bounded:
    """ONE compiled constraint: one side of one bounded coordinate's
    declared range, as a LEVEL over the bank and the one moving driver.

        high side:   g(t) = value(t) - bound(t)
        low  side:   g(t) = bound(t) - value(t)

    `value` is the chain `_Chains` composed; `bound` is the declared
    bound with its OWN coordinate taken at the value the request STARTED
    from (`_OWN`) and each read taken ALONG THE PATH through its own
    chain. A request admits the largest fraction at which `g` does not
    exceed `max(0, g(0))` (design sections 4 and 7).

    The classification is STRUCTURAL and decided ONCE, at construction,
    per DRIVER that can move the level -- exactly as cycle 1 classifies
    an `at`, through the same `_standing_except` substitution.
    """

    __slots__ = ('coordinate', 'side', 'node', 'joint', 'unit', 'chain',
                 'bound', 'level', 'names', 'chain_names', 'plan', 'plans',
                 'shapes', 'kinks', 'described')

    def __init__(self, coordinate, side, node, joint, unit, chain, bound,
                 level):
        self.coordinate = coordinate
        self.side = side
        self.node = node
        self.joint = joint
        self.unit = unit
        self.chain = GraphValue(chain)
        self.bound = GraphValue(bound)
        self.level = GraphValue(level)
        self.names = tuple(sorted(free_names(level) - {_OWN}))
        self.chain_names = tuple(sorted(free_names(chain)))
        #: The level's own JUMP PLAN, before any input classifies it:
        #: the skeleton and the jump nodes in the graph's postorder, as
        #: `_plan_of` built them. `None` where the level carries no
        #: jump. This is what the document publishes; `plans` below is
        #: the same plan re-shaped per moving input, which is what a
        #: request solves over (OpenSpec change
        #: ``publish-the-clocked-machine``, design section 7).
        self.plan = None
        self.plans = {}
        #: The level's SHAPE in each driver that moves it, decided once,
        #: structurally: `affine` is one division, `kinked` is cut at its
        #: own breakpoints, and a level that jumps is partitioned at its
        #: own surfaces and each piece solved by its skeleton.
        self.shapes = {}
        self.kinks = {}
        self.described = f"the {side} bound of '{coordinate}'"

    def __repr__(self):
        return f'<constraint {self.described}>'

    ##############################################
    # The level, per request

    def moves_with(self, input_id):
        """Whether this constraint's level can move when `input_id`
        does. A level no driver moves is not examined for it, and costs
        nothing."""
        return input_id in self.plans

    def standing(self, bank):
        """The values this level reads, with the OWN coordinate taken at
        the value the request STARTS from."""
        values = {name: bank[name] for name in self.names}
        values[_OWN] = self.chain.evaluate(
            {name: bank[name] for name in self.chain_names})
        return values

    def threshold(self, values):
        """`h = max(0, g(0))`: the ordinary bound where the machine
        stands legally, and where it stands where it does not. A
        simulation standing outside a bound may move as long as it does
        not go FURTHER outside, and it may return -- nothing is ever
        clamped and nothing is silently repaired (design section 7)."""
        return max(0.0, self.level.evaluate(values))

    def at(self, values, input_id, value):
        held = dict(values)
        held[input_id] = value
        return self.level.evaluate(held)

    def bound_at(self, values, input_id, value):
        held = dict(values)
        held[input_id] = value
        return self.bound.evaluate(held)

    def value_at(self, values, input_id, value):
        held = dict(values)
        held[input_id] = value
        return self.chain.evaluate(held)

    ##############################################
    # The clip

    def clip(self, values, input_id, start, delta, threshold):
        """The landing this constraint stops the path at, as
        `(fraction, landing)`, or `None` when it stops nothing.

        The path is partitioned at the level's OWN jump surfaces
        (`JumpPlan.cuts`); on each piece every jump node holds one
        branch, so the skeleton is affine or kinked there and its
        crossing of `threshold` is ONE DIVISION. The landing is then the
        nearest representable value of the input on the SATISFIED side,
        walked in float ordinal space with membership decided by
        EVALUATING the level and never by comparing a float to a bound
        (design section 6).
        """
        plan = self.plans.get(input_id)
        if plan is None or delta == 0.0:
            return None
        walk = {name: values[name] for name in self.names}
        walk[_OWN] = values[_OWN]
        walk[input_id] = start
        steps = {name: 0.0 for name in walk}
        steps[input_id] = delta
        try:
            cuts = plan.cuts(walk, steps, self.described, self.coordinate)
        except TooManyCrossings as failure:
            raise _too_many_stops(self, input_id, delta,
                                  getattr(failure, 'count', None)) from None
        crossed = None
        for left, right in zip(cuts, cuts[1:]):
            branches = plan._branches(
                walk, steps, (left + right) / 2.0, len(plan.jumps),
                self.described, self.coordinate)
            crossed = self._crossed(plan, walk, steps, branches, left, right,
                                    threshold, input_id)
            if crossed is not None:
                break
        if crossed is None:
            return None
        if crossed == 0.0:
            # A level already AT its limit and pushed FURTHER admits
            # ZERO travel: the request moves nothing, fires nothing and
            # reports its stop (design section 9). Said here, off the
            # crossing, rather than left to the walk: where the input
            # stands at a value whose ulp is finer than the LEVEL's,
            # the walk finds a landing half an ulp of the level beyond
            # the start -- a travel the level cannot express -- and the
            # low side of a bound would then admit what the high side
            # of the same bound refuses, only because the coordinate
            # happens to stand near zero (closure 1).
            return 0.0, start
        star = start + delta * crossed
        direction = math.copysign(1.0, delta)

        def satisfied(value):
            return float(self.at(values, input_id, value) <= threshold)

        landing = far_side_of(satisfied, 0.0, star, -direction,
                              lambda: _unstopped(self, input_id),
                              scale=max(abs(start), abs(start + delta)))
        fraction = (landing - start) / delta
        if fraction <= 0.0:
            # A level already at its limit and pushed further admits
            # ZERO travel: the request moves nothing, fires nothing and
            # reports its stop (design section 9).
            return 0.0, start
        if fraction >= 1.0:
            return None
        return fraction, landing

    def _crossed(self, plan, walk, steps, branches, left, right, threshold,
                 input_id):
        """Where the level first exceeds `threshold` on ONE piece of the
        partition, as a fraction of the whole path, or `None`.

        A piece whose LEFT end already exceeds it is one the level
        STEPPED across at the cut behind it: the stop is at the end of
        the last piece on which the level was satisfied, which is the
        landing rule with no special case.
        """
        edges = (left, right)
        kinks = self.kinks.get(input_id)
        if kinks:
            def at(fraction):
                held = _along(walk, steps, fraction)
                held.update(branches)
                return held

            edges = (left,) + kinks.between(at, left, right) + (right,)
        for low, high in zip(edges, edges[1:]):
            below = plan._substituted(walk, steps, low, branches)
            above = plan._substituted(walk, steps, high, branches)
            if below > threshold:
                return low
            if above <= threshold:
                continue
            if above == below:
                return high
            return low + (high - low) * (threshold - below) / (above - below)
        return None


class _Level:
    """One compiled constraint as ONE request reads it: the values its
    level stands at when the request begins, and the threshold those
    values give it. Both are read ONCE, at the request's start (design
    section 8)."""

    __slots__ = ('bounded', 'values', 'threshold')

    def __init__(self, bounded, bank):
        self.bounded = bounded
        self.values = bounded.standing(bank)
        self.threshold = bounded.threshold(self.values)


##############################################
# Compiling the bounds of a clocked tree

def compile_bounds(root, drivers, states):
    """Every declared bound of `root`'s tree, compiled into a constraint
    level over the bank -- and the coordinates the clocked simulation
    therefore judges itself.

    Returns `(constraints, marks)`, `marks` being the `(id(node), joint
    name)` identities design section 10 holds for the duration of one
    request's pose.
    """
    from .program import _compiled_spans, qualified_coordinates

    inputs = dict(drivers)
    inputs.update(states)
    coordinates = qualified_coordinates(root)
    spans, reads = _compiled_spans(root, inputs, coordinates,
                                   authority=_AUTHORITY)
    if not spans:
        # A clocked tree with no ranged joint compiles nothing and pays
        # nothing: the request is cycle 1's request, field for field.
        return (), frozenset()
    chains = _Chains(root, set(inputs), coordinates)
    found = []
    marks = set()
    for identifier, low, high, unit in spans:
        node, joint = chains.joints[identifier]
        marks.add((id(node), joint.name))
        for side, bound in (('low', low), ('high', high)):
            if bound is None:
                continue
            found.append(_constrained(
                chains, drivers, identifier, node, joint, unit, side, bound,
                reads.get((identifier, side), ())))
    return tuple(found), frozenset(marks)


def _constrained(chains, drivers, identifier, node, joint, unit, side, bound,
                 read_ids):
    """One side of one declared range, as the level a request is clipped
    against, with every refusal design section 3 and section 5 state."""
    from solid_node.motion.joints import _where

    def refuse(detail):
        raise ClockedError(
            f"{_where(node)}: joint '{joint.name}' -- the coordinate "
            f"'{identifier}' -- declares a {side} bound, and {detail}")

    chain = chains.of(identifier, refuse, f"the coordinate '{identifier}'")
    if isinstance(bound, float):
        compiled = _num(bound)
    else:
        mapping = {identifier: _free(_OWN)}
        for read_id in read_ids:
            mapping[read_id] = chains.of(
                read_id, refuse, f"its read '{read_id}'")
        compiled = _substituted(as_node(bound), mapping)
    if side == 'high':
        level = _binop('-', chain, compiled)
    else:
        level = _binop('-', compiled, chain)
    root, jumps = checked_expression(level, refuse, 'a bound')
    _over_the_bank(chains, root, refuse)
    plan = _plan_of(root, jumps)
    skeleton = as_node(plan.skeleton)
    entry = Bounded(identifier, side, node, joint, unit, chain, compiled,
                    root)
    entry.plan = plan if plan.jumps else None
    moving = free_names(root)
    for input_id in sorted(drivers):
        if input_id not in moving:
            # This driver cannot move this level at all: the constraint
            # is not examined for it, and costs nothing.
            continue
        shape = _shape_of(_standing_except(skeleton, input_id))
        if shape is None:
            refuse(_curves(level, input_id))
        planned = []
        for jump in plan.jumps:
            argument = as_node(jump.argument)
            inner = _shape_of(_standing_except(argument, input_id))
            if inner is None:
                refuse(_curves(argument, input_id))
            planned.append(_Jump(jump.primitive, jump.placeholder,
                                 jump.argument, inner))
        entry.plans[input_id] = JumpPlan(plan.skeleton, planned)
        entry.shapes[input_id] = shape
        if shape == 'kinked':
            entry.kinks[input_id] = _KinkCuts(plan.skeleton)
    return entry


def _over_the_bank(chains, level, refuse):
    """Every free name of a compiled constraint is a BANK ID, `$own`
    aside -- or the bound is refused by name (OpenSpec change
    ``time-without-running``, design section 7).

    ADR-126 promised that what the bank cannot reach through a chain is
    refused by name, and its implementation left one hole: a relation
    whose law FACTORY captured the clock at realization composes the
    ANIMATION SYMBOL into the chain, which reaches `Bounded.standing`
    and dies there with a bare `KeyError`. The rule is stated GENERALLY,
    over any name that survives, so it covers the clock and whatever
    else ever leaks.

    A clock-driven coordinate is the case that found it, and it is
    named: a clocked stop is compiled over the bank, and nothing about
    a clock is banked for a request to stop against.
    """
    unknown = sorted(name for name in free_names(level)
                     if name != _OWN and name not in chains.bank)
    if not unknown:
        return
    named = ', '.join(f"'{name}'" for name in unknown)
    clock = ''
    animation = [name for name in unknown if name.startswith('$')]
    if animation:
        clock = (f" The name '{animation[0]}' is the untimed ANIMATION "
                 f"SYMBOL an unbound read of `time` gives, so a law= "
                 f"factory that "
                 f"read the owner's time at realization and closed over "
                 f"it composed a clock into this chain: a clocked stop "
                 f"is compiled over the bank -- the drivers and the "
                 f"states -- and a clock-driven coordinate is not "
                 f"something a stop can hold. Drop the range from this "
                 f"joint, or state the relation from a declared driver "
                 f"and name '{CLOCK_NAME}' among a committing "
                 f"relation's sources instead.")
    refuse(f'the chain that reaches it carries {named}, which the bank '
           f'has not got: the bank is every declared driver and every '
           f'declared state of this tree, and a stop is judged over '
           f'it.{clock}')


def _curves(level, input_id):
    return (f"its constraint level CURVES as '{input_id}' moves: "
            f'{_curving(level, input_id)}. A clocked stop is SOLVED and '
            f'never searched, so the level a bound states -- the bounded '
            f"coordinate's chain against the bound itself -- must be "
            f'affine in the moving driver, or kinked by abs, min or max '
            f'over quantities that are. Restate the bound, or the '
            f'relations that reach it, on a level the driver enters '
            f'linearly.')


def _too_many_stops(bounded, input_id, delta, count):
    reached = 'more than' if count is None else count
    return TooManyEvents(
        f"the request move('{input_id}', by={delta!r}) would cross "
        f'{reached} surfaces of {bounded.described}, and {_MAX_CROSSINGS} '
        f'is the most one constraint is admitted on one request. The '
        f'request committed nothing: the bank and the tree stand as they '
        f'were. Split it into shorter requests.')


def _commit_out_of_range(level, held, input_id, by, to):
    """A COMMIT inside a request carried a compiled coordinate outside
    its bound, judged by the clocked simulation itself, over the final
    bank, through the same chain the clip used.

    Raised as `JointRangeError` -- the kind the joints capability
    already exports for exactly this -- so what a maker sees for a
    commit that carries a joint out of range is cycle 1's behaviour
    unchanged: the request commits NOTHING and never poses.
    """
    from solid_node.motion.joints import JointRangeError, _where

    bounded = level.bounded
    asked = f'by={by!r}' if to is None else f'to={to!r}'
    return JointRangeError(
        f"{_where(bounded.node)}: joint '{bounded.joint.name}' -- the "
        f"coordinate '{bounded.coordinate}' -- declares a {bounded.side} "
        f'bound of {bounded.bound.evaluate(held)} '
        f"{bounded.unit or 'units'}, and the request "
        f"move('{input_id}', {asked}) ends with it at "
        f'{bounded.chain.evaluate(held)}, which is outside it. The clip '
        f'read that bound over the bank the request STARTED from; an '
        f'event inside the request committed a state that moved it. The '
        f'request committed nothing: the bank, the tree and the record '
        f'stand as they were. Split the request at that event.')


def _unstopped(bounded, input_id):
    from .program import LandingInvariantError

    return LandingInvariantError(
        f'{bounded.described}: the level was crossed on this request and '
        f"no value of '{input_id}' within reach of the crossing's own "
        f'arithmetic reads the satisfied side, so the stop placed the '
        f'input nowhere. That is a broken invariant of the clocked '
        f'solver. The request committed nothing.')


##############################################
# The value objects a request reports

class Commit:
    """ONE EVENT: where on the path it happened, what the input stood at,
    which committing relation (or relations) fired there, and what they
    wrote.

    One entry per EVENT rather than per relation, because relations that
    land on one float ARE one event -- they read the same pre-event bank
    and their targets take their results together, and declaration order
    is not observable between them. `relation` is the relation as
    written where one fired, and the relations joined where several did.
    """

    __slots__ = ('relations', 'fraction', 'value', 'targets')

    def __init__(self, relations, fraction, value, targets):
        self.relations = tuple(relations)
        self.fraction = fraction
        self.value = value
        self.targets = targets

    @property
    def relation(self):
        if len(self.relations) == 1:
            return self.relations[0]
        return ' & '.join(self.relations)

    def __repr__(self):
        return (f'<commit {self.relation} at {self.value} '
                f'({self.fraction:.4f}) -> {self.targets}>')

    def __eq__(self, other):
        return (isinstance(other, Commit)
                and (self.relations, self.fraction, self.value, self.targets)
                == (other.relations, other.fraction, other.value,
                    other.targets))


class Request:
    """What one `move` did: the input, its travel, BOTH ENDS of the path
    it travelled, the events it fired in path order, how much of the
    travel the machine ADMITTED, and the bounds it STOPPED at.

    `by` stays what the caller asked for; `admitted` is what was made,
    in DESIGN units -- the units `by=` speaks -- and `stops` is empty
    exactly when the whole travel was made.

    `origin` and `end` are the value the moving input STOOD AT when the
    request began and the value it ENDED at, each taken verbatim from
    the bank and therefore in the input's own NATIVE units -- the units
    every `Commit.value` speaks, so that every event's value lies on the
    segment they span. That is a deliberate asymmetry with `admitted`,
    which speaks design units because that is what `by=` asked in.

    Neither end is left for a caller to recompute. `to` is `None` for a
    relative request, `by` is the ASK and not the travel, and a caller
    reconstructing an end as `origin + admitted / scale` can land on a
    float this machine never stood at -- and a commit landing exactly ON
    the endpoint would then read as unfired. The two floats the machine
    actually used are published instead (OpenSpec change
    ``play-the-instruction``, design section 5).
    """

    __slots__ = ('input', 'by', 'to', 'origin', 'end', 'commits',
                 'admitted', 'stops')

    def __init__(self, input_id, by, to, origin, end, commits,
                 admitted=0.0, stops=()):
        self.input = input_id
        self.by = by
        self.to = to
        self.origin = origin
        self.end = end
        self.commits = tuple(commits)
        self.admitted = admitted
        self.stops = tuple(stops)

    def __repr__(self):
        stopped = '' if not self.stops else f', {len(self.stops)} stops'
        return (f"<request move('{self.input}', "
                f'{"by" if self.to is None else "to"}='
                f'{self.by if self.to is None else self.to}) '
                f'-> {len(self.commits)} commits, '
                f'admitted {self.admitted}{stopped}>')


class _ClockInput:
    """The CLOCK as a request's moving input (OpenSpec change
    ``time-without-running``, design section 4).

    Shaped like a driver declaration where `move` reads one -- a
    `default`, a `native()` and a `scale` -- and nothing more, because
    seconds are both the design unit and the native unit of a clock: no
    conversion happens anywhere, `by=`, `to=` and `admitted` are all
    plain seconds, and the clock has no range of its own to clip
    against.
    """

    name = CLOCK_NAME
    default = 0.0
    scale = None
    unit = 's'
    dtype = None

    def native(self, value):
        return float(value)

    def __repr__(self):
        return f"<clock '{CLOCK_NAME}', in seconds>"


#: One instance is enough: the declaration carries no per-simulation
#: state, exactly as a driver declaration carries none.
_CLOCK = _ClockInput()


class ClockedSnapshot:
    """A clocked simulation's whole state as a value object: the model it
    was taken over, and the bank."""

    __slots__ = ('model', 'values')

    def __init__(self, model, values):
        self.model = model
        self.values = dict(values)

    def __repr__(self):
        return f'<clocked snapshot of {self.model}: {self.values}>'


##############################################
# The executor

class Clocked:
    """One clocked simulation: the bank, the compiled relations, and the
    request path."""

    def __init__(self, sim, node, drivers, states, instructions,
                 state=None, record=None):
        _enter()
        self.sim = sim
        self.node = node
        self.drivers = drivers
        self.states = states
        # The CLOCK: a banked value of this simulation exactly when the
        # root declares the ELAPSED base, and nothing at all otherwise
        # (OpenSpec change ``time-without-running``, design section 3).
        # The two axes are independent -- the state discipline selected
        # this executor, and the time base says what `time` means.
        from solid_node.motion.ports import declared_time

        base = declared_time(type(node))
        self.clock = base is not None and base.mode == 'elapsed'
        self.relations = compile_clocked(node, drivers, states, instructions,
                                         clock=self.clock)
        # Every declared bound of the tree, compiled ONCE into a
        # constraint level over the bank, and the coordinates this
        # simulation therefore judges itself during a request (OpenSpec
        # change ``a-bound-stops-the-request``, design sections 2 and 10).
        self.bounds, self.marks = compile_bounds(node, drivers, states)
        self.bank = {identifier: declaration.default
                     for identifier, declaration in drivers.items()}
        self.bank.update({identifier: declaration.default
                          for identifier, declaration in states.items()})
        if self.clock:
            # In SECONDS, initial zero, under the bare qualified id
            # `time` -- the one global snapshot entry the state delivery
            # already reserves, so no collision with a driver or a state
            # is possible: a root-declared one of that name is already
            # refused at class definition for shadowing the assembly
            # member (design section 3).
            self.bank[CLOCK_NAME] = 0.0
        #: The free name every published bound reads its own
        #: coordinate's start-of-request value under. `$own` cannot
        #: travel -- the document's expression language admits exactly
        #: one `$`-name, `$t` -- so the name is MINTED here and
        #: DECLARED as `clocked.own`, which is `program.clock`'s pattern
        #: (design section 8).
        self.own = _own_name(set(self.bank))
        #: A digest over the canonical listing `described` writes: a
        #: bank taken against one machine is refused against another.
        self.identity = hashlib.sha256(
            self.described().encode()).hexdigest()
        self.model = (f'{type(node).__name__}'
                      f'({",".join(sorted(self.bank))})')
        for identifier, value in (state or {}).items():
            if identifier not in self.bank:
                known = ', '.join(sorted(self.bank)) or 'none'
                raise ValueError(
                    f"state={{'{identifier}': ...}} names no declared "
                    f'driver or state of {type(node).__name__}. A '
                    f'session is opened over the bank, by qualified id; '
                    f'declared: {known}.')
            self.bank[identifier] = value
        self._ring = deque(maxlen=record) if record else None
        # A stop is a BOUND OF A COORDINATE, which stops motion, and a
        # commit is a VALUE THE MACHINE WROTE: a reader counting strokes
        # must not have to filter out interlocks, so the two rings are
        # two (ADR-108's own reason, taken for the request).
        self._stops = deque(maxlen=record) if record else None
        self.initial = ClockedSnapshot(self.model, self.bank)
        self.pose()

    ##############################################
    # The bank and the pose

    @property
    def state(self):
        return {name: value for name, value in sorted(self.bank.items())}

    @property
    def time(self):
        """The instant this simulation stands at, in SECONDS, under the
        elapsed base -- and refused by name under every other clocked
        root, naming the base that would give it one.

        The ONE name of ADR-125's refused list this cycle lifts, and
        only for this base (design section 3).
        """
        if self.clock:
            return self.bank[CLOCK_NAME]
        raise TypeError(
            f'time belongs to a simulation with a CLOCK, and '
            f'{type(self.node).__name__} is CLOCKED and declares no time '
            f'base: its tree declares a State, and a state moves on '
            f'requests rather than on a cadence. Declare '
            f'time = Time.elapsed() on the root -- elapsed seconds that '
            f'never wrap -- and the clock becomes a banked value '
            f"sim.move('time', by=<seconds>) moves.")

    @property
    def commits(self):
        return tuple(self._ring) if self._ring is not None else ()

    @property
    def stops(self):
        """The bounded ring of bounds reached `record=` asked for, and
        `()` when it asked for none. A request's own result is complete
        either way."""
        return tuple(self._stops) if self._stops is not None else ()

    def pose(self, bank=None):
        """Bind `bank` -- the simulation's own by default -- over the
        tree and render it ONCE.

        Exactly as the BUILD PATH poses a driven model outside a
        simulation: every driver and every state bound to its value, and
        `time` left as the untimed symbolic animation variable through
        the fallback an unbound clock already takes. A `simulate()` that
        reads `self.time` under a clocked root that declares no time base
        therefore reads what it reads today under an untimed one (design
        section 12 of ``declare-the-state``).

        Under the ELAPSED base the banked seconds are delivered too, in
        the SAME walk and through the hook that walk already has:
        `visit(node, path, children)` is called for every assembly after
        its drivers and states are bound and BEFORE anything renders, so
        every node's `self.time` reads the instant and the tree is still
        posed ONCE per request. `drive_tree` gains no parameter, and a
        root with no clock passes no `visit` at all (OpenSpec change
        ``time-without-running``, design section 6).
        """
        bank = self.bank if bank is None else bank
        visit = None
        if self.clock:
            seconds = bank[CLOCK_NAME]

            def visit(node, path, children, seconds=seconds):
                node._states[CLOCK_NAME] = seconds

        drive_tree(self.node,
                   lambda node, path, name, declaration:
                   bank[driver_id(path, name)],
                   visit=visit)

    def _posed(self, bank, marked=False):
        """Pose `bank`, and make it the simulation's only if the tree
        ACCEPTS it.

        The pose is the last step of a request, and a `Bound` the pose
        violates refuses it -- so a refused pose is a refused request,
        and atomicity has to include it. Posing the WORKING bank first
        and assigning it second is what makes that true: on a refusal
        the previous bank is posed again and the exception is re-raised,
        so the bank, the tree and the record stand exactly as they stood
        (design section 9, amended 2026-09-17). Cycle 2 is what CLIPS a
        request at a bound instead of refusing it whole.
        """
        previous = self.bank
        with clocked_marking(self.marks if marked else ()):
            # During a REQUEST this simulation is the SOLE AUTHORITY for
            # the constraints it compiled: the pose does not judge them,
            # because it judges them in a DIFFERENT ORDER of the same
            # arithmetic and an ulp of disagreement would refuse a
            # legitimate stop. It judged them itself, over the final
            # bank, before this pose. A pose that is NOT a request --
            # construction, `state=`, `restore` -- is marked by nothing
            # and judged by the enumeration, unchanged (design
            # section 10).
            try:
                self.pose(bank)
            except Exception:
                self.pose(previous)
                raise
        self.bank = bank

    ##############################################
    # Publication

    def published_names(self):
        """Every id the published clocked object's expressions may read:
        the declared drivers, the declared states, the clock where there
        is one, and the minted OWN name.

        The set a minted name must not collide with, and the set the
        document's binding pass is given so it cannot mint one either --
        `Program.published_names`'s part, for its reason.
        """
        found = set(self.drivers) | set(self.states)
        if self.clock:
            found.add(CLOCK_NAME)
        found.add(self.own)
        return found

    def described(self):
        """The canonical listing the identity is taken of.

        `Program.described`'s shape and purpose: a bank taken against one
        machine is refused against another. A changed RANGE changes it,
        through the constraint levels below, so a snapshot cannot be
        restored into a machine whose stops have moved (design
        section 13).
        """
        klass = type(self.node)
        lines = [f'root {klass.__module__}.{klass.__qualname__}']
        for identifier, declaration in sorted(self.drivers.items()):
            lines.append(f'input {identifier} dtype={declaration.dtype!r} '
                         f'scale={declaration.scale!r}')
        for identifier, declaration in sorted(self.states.items()):
            lines.append(f'state {identifier} dtype={declaration.dtype!r} '
                         f'scale={declaration.scale!r}')
        if self.clock:
            lines.append(f'clock {CLOCK_NAME}')
        for relation in self.relations:
            laws = ' | '.join(_text(graph) for graph in relation.law_graphs)
            lines.append(
                f'commit {list(relation.source_ids)} -> '
                f'{list(relation.target_ids)} {relation.primitive} '
                f'{_text(relation.level)} | {laws}')
        for bounded in self.bounds:
            lines.append(f'bound {bounded.coordinate} {bounded.side} '
                         f'{_text(bounded.level)}')
        return '\n'.join(lines)

    def published(self, initial=None):
        """The projection a version 8 document carries: what COMPILE
        TIME decided about this machine, and nothing a request computes.

        `initial` is the machine's REST BANK, taken for
        `Program.published`'s symmetry and deliberately NOT published: a
        clocked bank holds no joint coordinate, so it is every declared
        driver and every declared state at its declared default with the
        clock at zero, and every one of those numbers is already in the
        document's own `drivers` and `states` tables. Repeating a
        declaration inside `clocked` is forbidden for the reason it is
        forbidden inside `program` (design section 4).

        Every expression slot holds a NATIVE GRAPH rather than text: the
        document's own binding pass compiles them together with the
        tree's, so a subexpression a commit law shares with the geometry
        that displays it is published ONCE and nothing carries
        producer-local `let(...)` syntax. Branch placeholders are minted
        HERE, across the whole document, because two plans naming their
        first jump alike would let the binding pass share one subtree
        between two different jump nodes.
        """
        placeholders = self._placeholders()
        return {
            'identity': self.identity,
            'clock': CLOCK_NAME if self.clock else None,
            'own': self.own,
            'commits': [self._published_commit(relation)
                        for relation in self.relations],
            'bounds': [self._published_bound(bounded, minted)
                       for bounded, minted in zip(self.bounds, placeholders)],
            'limits': {'crossing_tolerance': _CROSSING_TOLERANCE,
                       'max_crossings': _MAX_CROSSINGS},
        }

    def _placeholders(self):
        """One `{compiler name: published name}` map per compiled
        constraint, in constraint order and then the level's own
        postorder, under a prefix lengthened while any published id
        matches `<prefix>` followed by digits.

        `Program._placeholders`' rule, minted across the WHOLE document:
        two plans naming their first jump alike would let the binding
        pass share one subtree between two different jump nodes.
        """
        prefix = _placeholder_prefix(self.published_names())
        minted = 0
        found = []
        for bounded in self.bounds:
            mapping = {}
            if bounded.plan is not None:
                for jump in bounded.plan.jumps:
                    mapping[jump.placeholder] = f'{prefix}{minted}'
                    minted += 1
            found.append(mapping)
        return found

    def _published_bound(self, bounded, placeholders):
        """One compiled constraint, as the document carries it.

        `value` is the CHAIN -- one expression over the bank's ids,
        composed by substitution down to declared drivers and states,
        with every intermediate port composed THROUGH and never named.
        `bound` is the declared bound with its own coordinate read under
        the published OWN name and every `reads=` coordinate already
        substituted by its own chain; a NUMERIC bound publishes a
        number.

        The LEVEL is not published: it is `value - bound` on the high
        side and `bound - value` on the low side, `side` says which, and
        publishing it as well would publish the bound twice.

        `plan` is the level's jump plan in exactly the shape a published
        program's has, through the same `_published_plan` and the same
        `_renamed`, and `null` where the level carries no jump.
        `shapes` carries, per input that can move the level, the
        SKELETON's shape and one shape per published jump, aligned with
        `plan.jumps` (design section 7).
        """
        return {
            'coordinate': bounded.coordinate,
            'side': bounded.side,
            'unit': bounded.unit,
            'value': bounded.chain,
            'bound': _published_bound_value(bounded.bound, self.own),
            'plan': _published_plan(
                None if bounded.plan is None
                else _renamed_plan(bounded.plan, self.own), placeholders),
            'shapes': {identifier: {
                'level': shape,
                'jumps': [jump.shape
                          for jump in bounded.plans[identifier].jumps],
            } for identifier, shape in sorted(bounded.shapes.items())},
            'node': type(bounded.node).__name__,
            'joint': bounded.joint.name,
            'description': bounded.described,
        }

    def _published_commit(self, relation):
        """One committing relation, as the document carries it.

        `sources` is in WRITTEN ORDER, because that is the order the
        law's positional arguments are in; a consumer reads them by
        NAME anyway. `at` is ONE jump node and its LEVEL QUANTITY,
        whose surfaces and branch the published jump vocabulary already
        defines -- no key is added for them, exactly as the running
        document adds none. `law` is one expression per target, aligned
        with `targets`. `shapes` carries what compile time decided per
        INPUT THAT CAN MOVE the level; an input absent from it cannot
        move the level at all and is not examined for it (design
        section 6).

        The published set is the inputs whose shape is `affine` or
        `kinked`, which is NOT literally `jumps`' key set: `_compiled`
        classifies EVERY driver among the sources, and a driver the
        level does not read at all classifies `constant`. `moves_with`
        therefore answers True for such a driver and the request path
        is untouched -- it locates no crossing on a level that cannot
        move. Publishing a `constant` entry would state a third value
        the export capability does not admit, and would tell a consumer
        to examine a relation that can never fire.
        """
        return {
            'sources': list(relation.source_ids),
            'targets': list(relation.target_ids),
            'at': {'primitive': relation.primitive,
                   'level': GraphValue(relation.level)},
            'law': [_published_law(graph)
                    for graph in relation.law_graphs],
            'shapes': {identifier: jump.shape
                       for identifier, jump
                       in sorted(relation.jumps.items())
                       if jump.shape in ('affine', 'kinked')},
            'description': relation.described,
            'stated_by': relation.stated_by,
        }

    ##############################################
    # Session setup

    def snapshot(self):
        return ClockedSnapshot(self.model, self.bank)

    def restore(self, snapshot):
        if not isinstance(snapshot, ClockedSnapshot):
            raise TypeError(
                f'restore() takes a snapshot taken by sim.snapshot(), not '
                f'{snapshot!r}.')
        if snapshot.model != self.model:
            raise ValueError(
                f'that snapshot was taken over {snapshot.model} and this '
                f'simulation runs {self.model}. A snapshot restores into '
                f'the machine it was taken from: its drivers, its states '
                f'and its relations are what its bank means.')
        self._posed(dict(snapshot.values))

    def reset(self):
        self.restore(self.initial)

    ##############################################
    # A request

    def move(self, input_id, by=None, to=None):
        """Move ONE declared driver BY a travel or TO a value, in design
        units, committing every rising event on the straight path.

        The path is solved again from each landing with the new bank, so
        an event surface that reads a committed state moves with it. The
        tree is bound ONCE, at the end.

        The `Request` returned reports BOTH ENDS of the path travelled:
        `origin`, the bank entry this input stood at when the request
        began, and `end`, the CLIPPED landing the bank holds afterwards.
        Both are in the input's NATIVE units, which is what every
        `Commit.value` speaks, so every event's value lies on the
        segment between them. They are reported rather than left to a
        caller because `admitted` is in DESIGN units and a caller
        rebuilding an end through the scale can land on a float this
        machine never stood at (design section 5).
        """
        _enter()
        declaration = self._input(input_id)
        if (by is None) == (to is None):
            raise ValueError(
                f"move('{input_id}', ...) states exactly one of by= (how "
                f'far to travel) and to= (where to land), both in design '
                f'units; got by={by!r} and to={to!r}.')
        origin = self.bank[input_id]
        if to is not None:
            target = declaration.native(to)
        else:
            target = origin + declaration.native(by)
        if input_id == CLOCK_NAME and target < origin:
            # A REFUSAL and not a stop: a stop reports a bound the
            # machine met, and no bound was met. Elapsed seconds never
            # wrap and never reverse, so the request is meaningless
            # rather than obstructed (design section 4). Zero is
            # admitted: it fires nothing and poses what already stands.
            asked = f'by={by!r}' if to is None else f'to={to!r}'
            raise ValueError(
                f"move('{CLOCK_NAME}', {asked}) asks this machine's clock "
                f'to run BACKWARDS: it stands at {origin!r} seconds and '
                f'the request ends at {target!r}. Elapsed seconds never '
                f'wrap and never reverse -- no bound was met and nothing '
                f'stopped, the request has no meaning. Restore a snapshot '
                f'taken at the earlier instant, or reset the simulation, '
                f'to stand before it again.')
        # STEP 0, and the whole of this cycle: the request's travel is
        # CLIPPED to the largest fraction at which every compiled
        # constraint is still satisfied, ONCE, over the bank as it
        # stands here, BEFORE the first event is located. Cycle 1's loop
        # below then runs over the clipped path exactly as it ran
        # before (design sections 1 and 9).
        levels = [_Level(bounded, self.bank) for bounded in self.bounds]
        target, stops = self._clipped(levels, input_id, origin, target)
        working = dict(self.bank)
        commits = []
        current = origin
        span = target - origin
        while True:
            delta = target - current
            if delta == 0.0:
                break
            event = self._next_event(working, input_id, current, delta)
            if event is None:
                break
            landing, firing = event
            # SYNCHRONOUS reads: every relation firing here reads the
            # bank as it stood BEFORE the event, including a state this
            # same event writes and a state another relation writes at
            # it. Declaration order is therefore not observable.
            staged = {}
            writers = {}
            for relation in firing:
                written = relation.commit(working, input_id, landing)
                for identifier in written:
                    first = writers.get(identifier)
                    if first is not None:
                        raise _two_answers(identifier, first, relation,
                                           input_id, landing)
                    writers[identifier] = relation
                staged.update(written)
            working.update(staged)
            working[input_id] = landing
            fraction = 1.0 if span == 0.0 else (landing - origin) / span
            commits.append(Commit(
                [relation.described for relation in firing],
                fraction, landing, dict(staged)))
            current = landing
        working[input_id] = target
        # STEP 6: this simulation judges what it compiled, over the
        # FINAL bank, through the same chains and against the same
        # thresholds the clip used. With the clip in front of the
        # events, the only way a compiled constraint can be violated
        # here is a COMMIT -- a state an event wrote, which the clip
        # read at its pre-request value (design section 10).
        self._judged(levels, working, input_id, by, to)
        # Nothing above touched the bank or the tree: a request that was
        # refused anywhere between here and its first event committed
        # NOTHING, exactly as a refused running tick commits nothing --
        # and the final POSE is part of the request, so it is posed
        # before the bank is assigned and its refusal leaves everything
        # standing (design section 9).
        self._posed(working, marked=True)
        if self._ring is not None:
            self._ring.extend(commits)
            self._stops.extend(stops)
        scale = getattr(declaration, 'scale', None)
        admitted = (target - origin) * (1.0 if scale is None else scale)
        # BOTH ENDS, verbatim: `origin` is the bank entry this request
        # started from and `target` is the CLIPPED landing the bank
        # holds now. Neither is recomputed from `admitted`, which speaks
        # design units and would reintroduce the scale a consumer must
        # not divide by (design section 5).
        return Request(input_id, by, to, origin, target, commits, admitted,
                       stops)

    ##############################################
    # The clip, and the judgement that closes a request

    def _clipped(self, levels, input_id, origin, target):
        """`target` truncated to where the machine's declared stops
        allow, and the stops met there.

        A request stopped at ZERO travel is ADMITTED: it moves nothing,
        fires nothing, poses nothing new and reports its stop. That is
        what an interlock does, and it is what makes a clocked machine
        operable (design section 9).
        """
        requested = target - origin
        if not levels or requested == 0.0:
            return target, ()
        found = []
        for level in levels:
            reached = level.bounded.clip(level.values, input_id, origin,
                                         requested, level.threshold)
            if reached is not None:
                found.append((reached[0], reached[1], level))
        if not found:
            return target, ()
        landing = min(found, key=lambda entry: entry[0])[1]
        met = [level for _fraction, where, level in found if where == landing]
        stops = tuple(Stop(
            level.bounded.coordinate, level.bounded.side,
            level.bounded.bound_at(level.values, input_id, landing),
            level.bounded.value_at(level.values, input_id, landing),
            landing, (landing - origin) / requested) for level in met)
        return landing, stops

    def _judged(self, levels, bank, input_id, by, to):
        """Every compiled constraint, over the bank the request ends at.

        Made BEFORE the tree is posed, so a refused request never poses
        at all and cycle 1's atomicity is untouched.
        """
        for level in levels:
            bounded = level.bounded
            held = {name: bank[name] for name in bounded.names}
            held[_OWN] = level.values[_OWN]
            if bounded.level.evaluate(held) > level.threshold:
                raise _commit_out_of_range(level, held, input_id, by, to)

    def _next_event(self, bank, input_id, current, delta):
        """The next event on the remaining path: its landing, and every
        relation that fires there.

        Two relations are ONE event exactly when their far-side landings
        are the SAME float. No tolerance decides it: a tolerance stated
        as a fraction of the request's travel would make one long
        request merge events that several short requests keep apart.
        """
        earliest = None
        landings = {}
        for relation in self.relations:
            if not relation.moves_with(input_id):
                continue
            found = relation.next_event(bank, input_id, current, delta)
            if found is None:
                continue
            where, landing = found
            landings[id(relation)] = landing
            if earliest is None or where < earliest[0]:
                earliest = (where, landing)
        if earliest is None:
            return None
        landing = earliest[1]
        firing = [relation for relation in self.relations
                  if landings.get(id(relation)) == landing]
        return landing, firing

    def _input(self, input_id):
        """The declaration of the ONE input a request may name: a
        declared driver, or -- under the elapsed base -- the clock."""
        if input_id == CLOCK_NAME:
            if self.clock:
                return _CLOCK
            raise ValueError(
                f"move('{CLOCK_NAME}', ...) names this machine's clock, "
                f'and {type(self.node).__name__} declares no time base: a '
                f'clocked model has a clock only where it says so. '
                f'Declare time = Time.elapsed() on the root -- elapsed '
                f'seconds that never wrap -- to have one a request can '
                f'move.')
        try:
            return self.drivers[input_id]
        except KeyError:
            pass
        if input_id in self.states:
            raise ValueError(
                f"move('{input_id}', ...) names a State. A state is "
                f'written by the machine at an event, through the '
                f'committing relation that names it as a target, and a '
                f'request moves a DRIVER: name the input whose motion '
                f'the event is located on.')
        known = ', '.join(sorted(self.drivers)) or 'none'
        raise ValueError(
            f"move('{input_id}', ...) names no declared driver of "
            f'{type(self.node).__name__}. A request moves ONE declared '
            f"driver by its qualified id -- a joint coordinate's value "
            f'comes from the pose the drivers and the states produce, '
            f'never from a request; declared: {known}.')


##############################################
# What a producer takes from a clocked root


def clocked_of(root):
    """The compiled clocked machine of a clocked root and its REST BANK,
    taken WITHOUT taking the tree over.

    `program_of`'s shape: the machine is COMPILED by constructing the
    simulation, so the published machine is the simulation's by
    construction rather than by two implementations agreeing, and every
    refusal `compile_clocked` and `compile_bounds` make is made before a
    document exists. Every node's snapshot is put back and the tree
    re-rendered afterwards, so a caller that held a posed tree still
    holds one -- which is what the browser-snapshot capture needs, that
    producer arriving with the tree posed at `--drive` values.

    There is no `release_tree`: a clocked simulation does not own the
    tree the way a run does, and `Sim.__init__`'s clocked branch returns
    before any binder is installed.

    A root the simulation cannot be constructed over has no machine to
    publish, and this raises exactly what `Sim` raises.
    """
    from .program import _restore, _snapshots
    from .sim import Sim

    snapshots = _snapshots(root)
    try:
        sim = Sim(root)
        return sim._clocked, dict(sim.initial.values)
    finally:
        _restore(snapshots, root)
