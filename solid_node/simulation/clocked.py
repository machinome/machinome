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

import math
from collections import deque

from solid_node.motion.couplings import CouplingError
from solid_node.node.qualified import (driver_id, drive_tree, instance_path)
from solid_node.scad_expression import GraphValue, symbol

from .program import (JumpPlan, TooManyCrossings, _MAX_CROSSINGS, _Jump,
                      _along, _argument_graph, _branch_of, _deduplicated,
                      _shape_of, checked_expression, far_side_of)


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
                 jumps, at, law):
        self.record = record
        self.source_ids = tuple(source_ids)
        self.target_ids = tuple(target_ids)
        self.primitive = primitive
        self.level = level
        self.jumps = jumps
        self.at = at
        self.law = law
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
        for index, (where, _level) in enumerate(found):
            before = _branch_of(jump, self._level_at(
                jump, standing, steps, (edges[index] + where) / 2.0))
            landing = far_side_of(
                branch_at, before, start + delta * where, direction,
                lambda: _unlanded(self, jump))
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

        The right end is INCLUSIVE and the left end exclusive: a request
        that ends exactly ON a surface has reached it -- `move('crank',
        by=360)` with `at = floor(crank / 360)` IS one stroke -- and one
        that RESUMES from a landing has already taken the surface it
        stands on.
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
        return sorted(found, key=lambda entry: entry[0])

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
        return {identifier: declaration.committed(value)
                for identifier, declaration, value
                in zip(self.target_ids, self.targets, returned)}


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

def compile_clocked(root, drivers, states, instructions):
    """Every committing relation of `root`'s tree, compiled, with every
    refusal a TREE can state.

    A class body cannot see what the whole tree writes, nor what shape an
    `at` expression has once its sources are known, so the refusals here
    are the ones whose facts first exist at simulation construction.
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
    for record in records:
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
        for target in (instruction.targets or instruction.by or {}):
            identifier = '.'.join(path + (target,))
            if identifier in states:
                raise ClockedError(
                    f"the instruction '{name}' targets '{identifier}', "
                    f'which is a State. An instruction moves a DRIVER to '
                    f'a target over a duration, and a state is written by '
                    f'the machine at an event, never ramped to a value a '
                    f'declaration names.')
    return tuple(_compiled(root, record, drivers, states)
                 for record in records)


def _records_of(root, node=None, found=None):
    """Every resolved committing relation in `root`'s tree, in tree
    order.

    Walked over `_rest_children`, the linked rest structure every
    qualified pass descends -- idempotent, and already built by the
    enumeration this construction just ran, so the walk discovers
    nothing and renders nothing.
    """
    from solid_node.node.assembly import _rest_children

    if found is None:
        found = []
    node = root if node is None else node
    found.extend(node.__dict__.get('_commitments', ()))
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


def _compiled(root, record, drivers, states):
    """One committing relation, compiled: its ids, its event level and
    its two callables."""
    source_ids = tuple(_identifier(root, end) for end in record.sources)
    target_ids = tuple(_identifier(root, end) for end in record.targets)

    def refuse(detail):
        raise ClockedError(f'{record.described()}: {detail}')

    for identifier in source_ids:
        if identifier not in drivers and identifier not in states:
            refuse(f"its source '{identifier}' is neither a declared "
                   f'driver nor a declared state of this tree.')
    tokens = [symbol(identifier) for identifier in source_ids]
    primitive, level = _event_level(record, tokens, refuse)
    law = _checked_law(record, tokens, target_ids, refuse)
    jumps = {}
    for identifier in source_ids:
        if identifier not in drivers:
            # Only a DRIVER moves along a request path; a state is
            # constant between events, which is exactly why a level that
            # reads its own target is simple here (design section 8).
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
        refuse(f"its event level moves with no declared driver: its "
               f"sources are {', '.join(source_ids)}, and every one of "
               f'them is a state, which is constant between events. An '
               f'event is located on the motion of a DRIVER, so name the '
               f'input whose motion reaches this event among the '
               f'sources.')
    relation = Committing(record, source_ids, target_ids, primitive, level,
                          jumps, record.at, law)
    relation.targets = tuple(states[identifier]
                             for identifier in target_ids)
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
    """`law`'s callable, with its expression checked exactly as a
    running law's is, and with ONE difference: no jump plan, no skeleton
    and no refusal of a law made entirely of jumps.

    A commit is evaluated at a POINT and never integrated, so every jump
    primitive in it means what it says and nothing is subtracted --
    `floor(crank / 360) % 10` is a digit, where under a run it states
    arithmetic rather than a mechanism (design section 7).

    The graph is walked ONCE, here, and never again to compute a value:
    the executor calls the project's own callable with the bank's
    numbers. Checking the shape now is what stops a project from writing
    a commit law the framework accepts and the document cycle cannot
    publish.
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
    for value in values:
        if isinstance(value, bool):
            refuse(f'the law returned {value!r}, which is neither a '
                   f'number nor an expression.')
        if isinstance(value, (int, float)):
            continue
        checked_expression(value, refuse, 'a commit law')
    return record.law


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
    """What one `move` did: the input, its travel, and the events it
    fired in path order."""

    __slots__ = ('input', 'by', 'to', 'commits')

    def __init__(self, input_id, by, to, commits):
        self.input = input_id
        self.by = by
        self.to = to
        self.commits = tuple(commits)

    def __repr__(self):
        return (f"<request move('{self.input}', "
                f'{"by" if self.to is None else "to"}='
                f'{self.by if self.to is None else self.to}) '
                f'-> {len(self.commits)} commits>')


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
        self.relations = compile_clocked(node, drivers, states, instructions)
        self.bank = {identifier: declaration.default
                     for identifier, declaration in drivers.items()}
        self.bank.update({identifier: declaration.default
                          for identifier, declaration in states.items()})
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
        self.initial = ClockedSnapshot(self.model, self.bank)
        self.pose()

    ##############################################
    # The bank and the pose

    @property
    def state(self):
        return {name: value for name, value in sorted(self.bank.items())}

    @property
    def commits(self):
        return tuple(self._ring) if self._ring is not None else ()

    def pose(self, bank=None):
        """Bind `bank` -- the simulation's own by default -- over the
        tree and render it ONCE.

        Exactly as the BUILD PATH poses a driven model outside a
        simulation: every driver and every state bound to its value, and
        `time` left as the untimed symbolic animation variable through
        the fallback an unbound clock already takes. A `simulate()` that
        reads `self.time` under a clocked root therefore reads what it
        reads today under an untimed one (design section 12).
        """
        bank = self.bank if bank is None else bank
        drive_tree(self.node,
                   lambda node, path, name, declaration:
                   bank[driver_id(path, name)])

    def _posed(self, bank):
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
        try:
            self.pose(bank)
        except Exception:
            self.pose(previous)
            raise
        self.bank = bank

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
        # Nothing above touched the bank or the tree: a request that was
        # refused anywhere between here and its first event committed
        # NOTHING, exactly as a refused running tick commits nothing --
        # and the final POSE is part of the request, so it is posed
        # before the bank is assigned and its refusal leaves everything
        # standing (design section 9).
        self._posed(working)
        if self._ring is not None:
            self._ring.extend(commits)
        return Request(input_id, by, to, commits)

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
        """The declaration of the ONE driver a request may name."""
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
