# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The compiled program: a running root's relations as EXPRESSIONS over
coordinate ids.

Untimed and looping, a relation sets its driven coordinate to
``f(driver)``. Running, it contributes ``f(end) - f(start)`` over a tick,
from where the coordinate stood -- which is exact across the kinks of
``abs``, ``min`` and ``max`` and of the compositions built on them,
because it is the difference of two exact evaluations. Nothing about the
law changes; what changes is which of its two readings the run takes.

To take the difference of two evaluations the run has to be able to
EVALUATE the law at values of its own choosing, and a law is already an
expression builder: ``Affine.forward`` is ordinary arithmetic over
whatever it is handed, ``solid_node.math``'s primitives emit ``call``
nodes whose names are the closed list ``SYMBOLIC_BUILTINS``, and a
``symbol()`` builds the graph. So each law is applied ONCE here, to a
symbolic token per source coordinate, in the direction the REST RENDER
solved it, and the graph that application builds -- over the qualified
ids of its sources -- is what the run evaluates on every tick.

A DISCONTINUOUS primitive (``floor``, ``ceil``, ``sign``, ``%``, a
comparison) is a JUMP, and a graph carrying one is compiled a second
time, into a ``JumpPlan``: the jump nodes in the graph's postorder, each
with the LEVEL QUANTITY whose surfaces it crosses, and a SKELETON of the
whole law with every jump node replaced by a branch placeholder. Over a
tick the plan cuts the path at every crossing it meets, reads one branch
per jump node at each piece's midpoint -- which makes the law continuous
there -- and sums the branch-substituted law's change over the pieces.
So a jump never moves a part, and nothing in the sum ever spans one.

That application is also the inspection. What the expression cannot say
is refused by relation identity, at construction, rather than integrated
wrongly: a law that raises when handed a symbol, or whose graph holds
text the framework cannot evaluate, is not an expression over its
sources at all; an edge into a bank coordinate whose source nothing in
the program computes is a value stated in ``simulate()`` rather than as
a relation; a law that can move its coordinate only by JUMPING states
arithmetic rather than a mechanism; and a jumping law driving no
coordinate the run owns has nowhere to keep the history a subtracted
jump implies.

This module is imported by ``Sim.__init__`` only when the root declares
``Time.running()``, so a model that declares no running time pays for
none of it (capability ``cli-startup-cost``).
"""

import hashlib
import math
import operator
import re
from dataclasses import dataclass

from solid2.core.object_base import OpenSCADConstant

from solid_node.expression_graph import ExpressionNode, free_names, postorder
from solid_node.math import SYMBOLIC_BUILTINS
from solid_node.motion.couplings import (_solved_formulas, _wirings,
                                         CouplingError)
from solid_node.motion.joints import coordinates_of, declared_joints
from solid_node.motion.ports import CLOCK_NAME
from solid_node.node.qualified import (driver_id, instance_path,
                                       DriverIdError)
from solid_node.scad_expression import GraphValue, as_node, symbol


# The primitives that JUMP, and are therefore recognized and planned for
# rather than integrated straight through. `floor`, `ceil` and `sign`
# jump by construction; `%` jumps at every period; a comparison is a
# step. `wrap()` is built on `ceil` and integrates through this list;
# `piecewise()` is a sum of `clamp01` terms and holds no jump node at
# all.
_JUMP_CALLS = ('floor', 'ceil', 'sign')
_JUMP_OPERATORS = ('%', '<', '<=', '>', '>=', '==', '!=')

# A comparison's level quantity is `a - b` and its one surface is zero,
# so its branch is the operator read against zero -- exactly what
# `GraphValue.evaluate` computes, whose `bool` arithmetic then reads as
# 1 or 0.
_COMPARISONS = {'<': operator.lt, '<=': operator.le, '>': operator.gt,
                '>=': operator.ge, '==': operator.eq, '!=': operator.ne}

# Three tolerances, and no more (design.md section 5).
#
# `_CROSSING_TOLERANCE` is stated in `t`, the tick's own dimensionless
# fraction, so one number serves a law over several sources with several
# units: it converts to each source's units by multiplying by that
# source's travel over the tick. It is the bisection's stopping bracket
# AND the width below which two crossings are one cut. The run calls two
# increments equal within `1e-9 * max(1, |a|, |b|)`, so a crossing
# located three orders finer than that can never manufacture a
# disagreement, and bisecting further is below the resolution of `t` as a
# double over a tick of unit travel.
#
# There is deliberately NO surface tolerance. The question "is this
# coordinate ON the surface" is never asked: a branch is read at a
# piece's midpoint, which is a point genuinely inside it.
_CROSSING_TOLERANCE = 1e-12

# How finely a level quantity that is NOT affine in the sources is
# sampled before each bracketed crossing is bisected. The search resolves
# any crossing pair separated by more than 1/64 of the tick's travel; a
# level quantity that turns twice inside one sub-interval is outside the
# guarantee, and the answer to that is a smaller dt.
_SUBDIVISIONS = 64

# 40 rounds already reach 2**-40 < 1e-12 from a unit bracket; this is the
# safety net, not the working number.
_BISECTION_ROUNDS = 64

# The per-graph per-tick bound on the partition. A thousand surfaces in
# one tick is a dt that is not resolving the mechanism, and an unbounded
# partition would be an unbounded per-tick cost inside a mode whose whole
# promise is bounded memory.
_MAX_CROSSINGS = 1000


class UnsupportedLaw(CouplingError):
    """A relation cannot be compiled into the running program, or cannot
    be integrated over a tick: its law is not an expression over its
    sources, is sourced from a coordinate the run does not own and no
    edge computes, can move its coordinate only by jumping, carries a
    jump with nowhere to keep its history, or divides by zero somewhere
    on the tick's own path.

    A declared range's BOUND is compiled by exactly the same rule and
    refused by the same kind: it is applied once to a symbolic token for
    the joint's own coordinate, and what the expression cannot say is
    refused here rather than evaluated wrongly every tick.
    """


class TooManyCrossings(CouplingError):
    """One tick would cut a law's path more times than the run admits.
    The tick committed nothing."""


@dataclass(frozen=True)
class Crossing:
    """One jump surface met inside one tick.

    `level` is the surface value in the LEVEL QUANTITY's own units -- the
    integer for `floor`, `ceil` and `%`, zero for `sign` and a
    comparison -- and `t` is the fraction of the tick at which it was
    reached. `relation` and `coordinate` are computed once at compile
    time, so appending an entry costs a tuple and no formatting.
    """

    tick: int
    relation: str
    coordinate: str
    primitive: str
    level: float
    t: float


@dataclass(frozen=True)
class Constraint:
    """One bound that READS other coordinates, compiled.

    `graph` is the bound's expression over the bounded coordinate's own
    id and `reads`; `edges` is the SUB-PROGRAM -- the compiled edges
    determining the bounded coordinate and every read, in program order
    -- and `candidates` the inputs reaching any of them. The last two
    are projections of the program's own `edges` and `sources` with no
    decision in them, so a document publishes neither.
    """

    identifier: str
    side: str
    graph: object
    reads: tuple
    edges: tuple
    candidates: tuple


@dataclass(frozen=True)
class Stop:
    """One declared bound reached inside one tick.

    `bound` is `'low'` or `'high'` and `value` is that bound EVALUATED
    for this tick -- a number for a number bound, the last seated tooth
    for a ratchet. For a bound over the coordinate's own value alone it
    is also the value the coordinate now holds, exactly; for a bound
    that READS OTHER COORDINATES it is not, because there is nothing to
    snap to and the coordinate that stopped may not have moved at all.
    `t` is the fraction of the tick at which it was reached and
    `inputs` names the inputs the stop blocked, sorted.

    A stop is a BOUND OF A COORDINATE, which stops motion; a `Crossing`
    is a JUMP SURFACE of a law, which moves nothing. They answer
    different questions and live in different rings.
    """

    tick: int
    coordinate: str
    bound: str
    value: float
    t: float
    inputs: tuple


def qualified_coordinates(root):
    """Every JOINT COORDINATE in `root`'s linked tree, by qualified id.

    `{qualified_id: (node, name)}`, the id being the instance path
    joined with the name `coordinates_of` reports -- the joint's own for
    a joint owning one, `<joint>.<coordinate>` for each of a `Free`.
    Every linked node the walk reaches is visited, LEAVES INCLUDED,
    because a joint may be declared on a leaf; only an assembly has
    children to descend into, exactly as `drive_tree`'s own walk has it.

    Plain ports and derived coordinates are deliberately absent: they are
    calculations over the state, recomputed by the ordinary enumeration
    on every tick, and the run stores no calculation.
    """
    from solid_node.node.assembly import _rest_children

    found = {}

    def visit(node, path):
        for joint in declared_joints(type(node)).values():
            for name in coordinates_of(joint):
                found[driver_id(path, name)] = (node, name)
        if getattr(node, '_states', None) is None:
            return
        for child in _rest_children(node):
            visit(child, path + (child.name,))

    visit(root, ())
    return found


##############################################
# The jump plan


class _Jump:
    """One jump node of a law, as the plan carries it.

    `argument` is the node's LEVEL QUANTITY -- the continuous expression
    whose surfaces it crosses -- with every jump node INSIDE it already
    replaced by its own branch placeholder, so evaluating it on a piece
    where those branches are fixed is one ordinary evaluation.
    `placeholder` is the free name the skeleton reads this node's branch
    under.
    """

    __slots__ = ('primitive', 'placeholder', 'argument', 'affine')

    def __init__(self, primitive, placeholder, argument, affine):
        self.primitive = primitive
        self.placeholder = placeholder
        self.argument = argument
        self.affine = affine

    def __repr__(self):
        return (f'<{self.primitive} jump on {self.argument} '
                f'{"affine" if self.affine else "searched"}>')


class JumpPlan:
    """How a law that jumps is integrated over one tick.

    The tick moves the law's sources along the straight line from the
    values they hold to those values plus the increments they were
    given, parametrised by `t` in [0, 1] -- in the JOINT source space
    for a law naming several, which is what makes a gate closing while a
    shaft turns one question rather than two.

    That path is cut at every crossing of every jump surface it meets.
    On each open piece every jump node holds one BRANCH, read by
    evaluating its level quantity at the piece's MIDPOINT: a point
    genuinely inside the piece, so the value read there IS the branch,
    exactly, at any magnitude of source and from either direction of
    travel. The law with those branches substituted is continuous on the
    closed piece, so the increment is the plain sum of its change over
    the pieces -- with no epsilon, no one-sided limit rule and no
    direction test anywhere.
    """

    __slots__ = ('skeleton', 'jumps')

    def __init__(self, skeleton, jumps):
        self.skeleton = skeleton
        self.jumps = tuple(jumps)

    def __repr__(self):
        return f'<jump plan of {len(self.jumps)} nodes: {self.skeleton}>'

    ##############################################
    # The increment

    def increment(self, start, delta, described, coordinate,
                  crossings=None, tick=0):
        """The CONTINUOUS part of this law's change over one tick."""
        if not any(delta.values()):
            # A zero-length path contributes zero without evaluating
            # anything -- and must never reach the sum below, where a
            # one-point piece would read as minus a jump.
            return 0.0
        cuts = self._partition(start, delta, described, coordinate,
                               crossings, tick)
        total = 0.0
        for left, right in zip(cuts, cuts[1:]):
            branches = self._branches(start, delta, (left + right) / 2.0,
                                      len(self.jumps), described, coordinate)
            total += (self._substituted(start, delta, right, branches)
                      - self._substituted(start, delta, left, branches))
        return total

    def _substituted(self, start, delta, t, branches):
        values = _along(start, delta, t)
        values.update(branches)
        return self.skeleton.evaluate(values)

    def _branches(self, start, delta, t, count, described, coordinate):
        """Every jump node's branch at one point of the path, in
        postorder, so a node nested inside another's argument is
        determined first."""
        values = _along(start, delta, t)
        found = {}
        for jump in self.jumps[:count]:
            level = self._level(jump, values, described, coordinate)
            branch = _branch_of(jump, level)
            found[jump.placeholder] = branch
            values[jump.placeholder] = branch
        return found

    def _level(self, jump, values, described, coordinate):
        try:
            level = jump.argument.evaluate(values)
        except ZeroDivisionError:
            raise _no_level(jump, described, coordinate) from None
        if jump.primitive in ('floor', 'ceil', '%') \
                and not math.isfinite(level):
            # An integer branch cannot be read off an infinity or a nan,
            # and the arithmetic that would try raises something the
            # tick's rollback does not catch. Refuse it the same way.
            raise _no_level(jump, described, coordinate,
                            'a level quantity that is not a finite number')
        return level

    ##############################################
    # The partition

    def cuts(self, start, delta, described, coordinate):
        """The breakpoints this law's own jumps put on the tick's path.

        The partition the increment already builds, made reachable and
        recording nothing: between two consecutive cuts every jump node
        holds one branch, so a law whose SKELETON is affine has a value
        that is affine in `t` there -- which is what lets a stop on it be
        SOLVED piece by piece rather than searched (design.md section 2,
        case 2).
        """
        if not any(delta.values()):
            return (0.0, 1.0)
        return tuple(self._partition(start, delta, described, coordinate,
                                     None, 0))

    def _partition(self, start, delta, described, coordinate,
                   crossings, tick):
        """The tick's path, cut at every crossing of every jump surface.

        The jump nodes are taken in POSTORDER, so a node's level
        quantity is asked where it crosses only once every jump node
        inside it has already cut the path: on each pair of consecutive
        cuts those inner branches are constant, which is what makes the
        level quantity a continuous function of `t` there and the search
        below well-posed.
        """
        cuts = [0.0, 1.0]
        located = []
        for index, jump in enumerate(self.jumps):
            found = []
            for left, right in zip(cuts, cuts[1:]):
                inner = self._branches(start, delta, (left + right) / 2.0,
                                       index, described, coordinate)
                found.extend(self._crossings_of(
                    jump, start, delta, inner, left, right,
                    described, coordinate))
                if len(found) > _MAX_CROSSINGS:
                    raise _too_many(described, coordinate, jump, len(found))
            if not found:
                continue
            found = _deduplicated(found)
            cuts = _merged(cuts, [where for where, _level in found])
            if len(cuts) - 2 > _MAX_CROSSINGS:
                raise _too_many(described, coordinate, jump, len(cuts) - 2)
            located.extend((where, index, jump.primitive, level)
                           for where, level in found)
        if crossings is not None and located:
            # Sorted by the fraction of the tick, and by the graph's
            # postorder where two coincide, so the listing is
            # deterministic.
            located.sort(key=lambda entry: (entry[0], entry[1]))
            crossings.extend(
                Crossing(tick, described, coordinate, primitive, level, where)
                for where, _index, primitive, level in located)
        return cuts

    def _crossings_of(self, jump, start, delta, inner, left, right,
                      described, coordinate):
        """Where `jump` reaches one of its surfaces between two cuts."""
        if jump.affine:
            # An affine level quantity is determined everywhere on the
            # piece by its two endpoint values, so every surface between
            # them is SOLVED -- all of them, which is what makes a crank
            # that passes three tooth windows in one tick add three
            # throws rather than one.
            low = self._level_at(jump, start, delta, left, inner,
                                 described, coordinate)
            high = self._level_at(jump, start, delta, right, inner,
                                  described, coordinate)
            if high == low:
                return []
            found = []
            for level in _surfaces(jump, low, high, described, coordinate,
                                   inclusive=False):
                found.append((left + (right - left)
                              * (level - low) / (high - low), level))
            return found
        return self._searched(jump, start, delta, inner, left, right,
                              described, coordinate)

    def _searched(self, jump, start, delta, inner, left, right,
                  described, coordinate):
        """Anything else: sampled, bracketed and bisected."""
        width = (right - left) / _SUBDIVISIONS
        points = [left + width * step for step in range(_SUBDIVISIONS)]
        points.append(right)
        levels = [self._level_at(jump, start, delta, where, inner,
                                 described, coordinate) for where in points]
        found = []
        for step in range(_SUBDIVISIONS):
            low, high = levels[step], levels[step + 1]
            for level in _surfaces(jump, low, high, described, coordinate,
                                   inclusive=True):
                if low == level:
                    # A sample that IS on the surface is the crossing;
                    # there is nothing to bisect, and taking it exactly
                    # is what keeps the answer exact when a crossing
                    # falls on a sub-interval boundary.
                    found.append((points[step], level))
                elif high == level:
                    found.append((points[step + 1], level))
                else:
                    found.append((self._bisect(
                        jump, start, delta, inner, level, points[step],
                        points[step + 1], described, coordinate), level))
            if len(found) > _MAX_CROSSINGS:
                break
        return found

    def _bisect(self, jump, start, delta, inner, level, low, high,
                described, coordinate):
        below = self._level_at(jump, start, delta, low, inner,
                               described, coordinate) - level
        for _round in range(_BISECTION_ROUNDS):
            if high - low <= _CROSSING_TOLERANCE:
                break
            middle = (low + high) / 2.0
            here = self._level_at(jump, start, delta, middle, inner,
                                  described, coordinate) - level
            if here == 0.0 or (here < 0.0) != (below < 0.0):
                high = middle
            else:
                low, below = middle, here
        return (low + high) / 2.0

    def _level_at(self, jump, start, delta, t, inner, described, coordinate):
        values = _along(start, delta, t)
        values.update(inner)
        return self._level(jump, values, described, coordinate)


def _is_jump(node):
    return ((node.kind == 'call' and node.op in _JUMP_CALLS)
            or (node.kind == 'binop' and node.op in _JUMP_OPERATORS))


def _along(start, delta, t):
    """The sources at `t` along the tick's straight path.

    At `t == 1` this is exactly `start + delta`, the same float the
    caller computed, because it is the same arithmetic.
    """
    return {name: start[name] + delta[name] * t for name in start}


def _branch_of(jump, level):
    """What `jump` reads on a piece whose level quantity sits at
    `level` -- design.md section 1's branch column."""
    primitive = jump.primitive
    if primitive == 'floor':
        return float(math.floor(level))
    if primitive == 'ceil':
        return float(math.ceil(level))
    if primitive == 'sign':
        return float((level > 0) - (level < 0))
    if primitive == '%':
        # Not a constant but the integer QUOTIENT: with `q` fixed the
        # node reads `a - q * b`, which is continuous in `t`.
        return float(math.trunc(level))
    return float(_COMPARISONS[primitive](level, 0.0))


def _surfaces(jump, low, high, described, coordinate, inclusive):
    """`jump`'s surfaces between two values of its level quantity."""
    if jump.primitive == 'sign' or jump.primitive in _COMPARISONS:
        first, last = (low, high) if low <= high else (high, low)
        if first < 0.0 < last or (inclusive and first <= 0.0 <= last):
            return (0.0,)
        return ()
    first, last = (low, high) if low <= high else (high, low)
    if not math.isfinite(first) or not math.isfinite(last):
        raise _no_level(jump, described, coordinate)
    span = math.ceil(last) - math.floor(first) - 1
    if span > _MAX_CROSSINGS:
        raise _too_many(described, coordinate, jump, span)
    if inclusive:
        levels = [float(whole)
                  for whole in range(math.floor(first), math.ceil(last) + 1)
                  if first <= whole <= last]
    else:
        levels = [float(whole)
                  for whole in range(math.floor(first) + 1, math.ceil(last))
                  if first < whole < last]
    if jump.primitive == '%':
        # `fmod` is `a - b * trunc(a / b)`, and `trunc` is zero on the
        # whole of (-1, 1): the operator is CONTINUOUS where `a / b`
        # crosses zero and jumps only at a nonzero integer of it.
        levels = [level for level in levels if level != 0.0]
    return levels


def _deduplicated(found):
    """One entry per surface actually reached: a crossing that falls on
    a sub-interval boundary is located twice, from either side."""
    ordered = sorted(found, key=lambda entry: (entry[0], entry[1]))
    kept = []
    for where, level in ordered:
        if kept and kept[-1][1] == level \
                and where - kept[-1][0] <= _CROSSING_TOLERANCE:
            continue
        kept.append((where, level))
    return kept


def _merged(cuts, found):
    """The partition with `found` folded in: two cuts closer than the
    tolerance are ONE, and the partition always ends at exactly 1."""
    ordered = sorted(cuts + list(found))
    kept = [ordered[0]]
    for where in ordered[1:]:
        if where - kept[-1] > _CROSSING_TOLERANCE:
            kept.append(where)
    kept[-1] = 1.0
    return kept


def _too_many(described, coordinate, jump, count):
    return TooManyCrossings(
        f'{described}: over one tick {coordinate} would cross {count} '
        f"surfaces of {jump.primitive}, more than the {_MAX_CROSSINGS} a "
        f'single law is admitted in one tick. A dt that coarse is not '
        f'resolving the mechanism: the crossings between the frames are '
        f'what a jump law is FOR. Step in smaller ticks. The tick '
        f'committed nothing: the bank, the tick count and the tree stand '
        f'as they were.')


def _no_level(jump, described, coordinate, reason=None):
    what = reason or ('a divisor of zero' if jump.primitive == '%'
                      else 'a division by zero in its level quantity')
    return UnsupportedLaw(
        f"{described}: its {jump.primitive} meets {what} somewhere on this "
        f'tick\'s path, so there is no level quantity to locate a crossing '
        f'on -- fmod(a, 0) is nan and a / 0 is nothing at all. The tick '
        f'committed nothing and {coordinate} stands where it stood: state '
        f'the relation so the divisor never reaches zero.')


##############################################
# What the program is made of


class Edge:
    """One step of the program: what it reads, what it determines, and
    how.

    `needs` and `gives` are keys into the program's node table. `gives`
    is empty for a CHECK, which determines nothing and only compares what
    its formula predicts with what its coordinate received -- the one
    place a conflict can be detected in this cycle.
    """

    __slots__ = ('kind', 'needs', 'gives', 'graphs', 'plans', 'driven',
                 'names', 'factors', 'constant', 'slot_key', 'description',
                 'stated_by', 'affine')

    def __init__(self, kind, needs, gives, description, stated_by,
                 graphs=(), plans=(), driven=(), names=(), factors=(),
                 constant=0.0, slot_key=None):
        self.kind = kind
        self.needs = tuple(needs)
        self.gives = tuple(gives)
        self.graphs = tuple(graphs)
        # Empty for a law with no jump in it at all, so `increments` can
        # tell the two apart in one test and a continuous law pays
        # nothing for this cycle (design.md section 12).
        self.plans = tuple(plans)
        # The driven coordinates' qualified ids, aligned with `gives`,
        # computed here so a crossing entry costs a tuple and no lookup.
        self.driven = tuple(driven)
        self.names = tuple(names)
        self.factors = tuple(factors)
        self.constant = constant
        self.slot_key = slot_key
        self.description = description
        self.stated_by = stated_by
        # One flag per DRIVEN END, aligned with `gives`: whether this
        # edge's value is affine in its sources along the tick's path, so
        # a stop on that end can be SOLVED rather than searched. A wiring
        # and a formula are linear by construction; a law is read off its
        # graph, or off its SKELETON where it carries a jump plan, whose
        # branch placeholders are constants on a piece.
        self.affine = tuple(self._affine_ends())

    def _affine_ends(self):
        if self.kind != 'law':
            return [True] * len(self.gives)
        found = []
        for index, graph in enumerate(self.graphs):
            plan = self.plans[index] if self.plans else None
            if plan is not None:
                found.append(_affine_in_sources(as_node(plan.skeleton)))
            elif graph is None:
                # A constant law has zero slope everywhere, which is
                # affine and moves nothing.
                found.append(True)
            else:
                found.append(_affine_in_sources(as_node(graph)))
        return found

    def __repr__(self):
        return f'<{self.kind} edge {self.description}>'

    ##############################################
    # Evaluation

    def _inputs(self, values, deltas=None):
        """The graph's free names bound to the values its sources hold,
        optionally advanced by the tick's increments."""
        if deltas is None:
            return {name: values[key]
                    for name, key in zip(self.names, self.needs)}
        return {name: values[key] + deltas[key]
                for name, key in zip(self.names, self.needs)}

    def values(self, values):
        """What this edge's targets hold at the committed state."""
        if self.kind == 'law':
            inputs = self._inputs(values)
            return [(key, _evaluated(graph, inputs))
                    for key, graph in zip(self.gives, self.graphs)]
        if self.kind == 'wiring':
            factor = self.factors[0]
            return [(self.gives[0], values[self.needs[0]] * factor)]
        if self.kind == 'formula':
            return [(self.gives[0], self._linear(values))]
        return []

    def increments(self, values, deltas, crossings=None, tick=0):
        """What this edge's targets MOVE BY over the tick.

        A law with no jump in it is the difference of two exact
        evaluations, which is what makes a kink exact -- and that is the
        FIRST thing tested here, so a continuous law pays nothing for
        the jump machinery. A law that jumps takes its plan, which cuts
        the tick at every crossing and sums the pieces.
        """
        if self.kind == 'law':
            start = self._inputs(values)
            if not self.plans:
                end = self._inputs(values, deltas)
                return [(key,
                         _evaluated(graph, end) - _evaluated(graph, start))
                        for key, graph in zip(self.gives, self.graphs)]
            delta = {name: deltas[key]
                     for name, key in zip(self.names, self.needs)}
            end = self._inputs(values, deltas)
            found = []
            for index, key in enumerate(self.gives):
                plan = self.plans[index]
                if plan is None:
                    graph = self.graphs[index]
                    found.append((key, _evaluated(graph, end)
                                  - _evaluated(graph, start)))
                    continue
                found.append((key, plan.increment(
                    start, delta, self.description, self.driven[index],
                    crossings, tick)))
            return found
        if self.kind == 'wiring':
            return [(self.gives[0], deltas[self.needs[0]] * self.factors[0])]
        if self.kind == 'formula':
            return [(self.gives[0], self._linear(deltas, constant=0.0))]
        return []

    def cuts(self, values, deltas, index):
        """The breakpoints of the driven end at `index` along the tick's
        path, or `()` where that end carries no jump plan."""
        if self.kind != 'law' or not self.plans:
            return ()
        plan = self.plans[index]
        if plan is None:
            return ()
        start = self._inputs(values)
        delta = {name: deltas[key]
                 for name, key in zip(self.names, self.needs)}
        return plan.cuts(start, delta, self.description, self.driven[index])

    def _linear(self, held, constant=None):
        """The linear combination this formula edge states, in the
        direction the rest render resolved it.

        Forward, that is the formula itself. Backward into one term, it
        is the formula rearranged for that term -- exact, because a
        derived coordinate is a coefficient map and a constant, not an
        expression tree.
        """
        total = self.constant if constant is None else constant
        if self.slot_key in self.gives:
            for key, factor in zip(self.needs, self.factors):
                total = total + held[key] * factor
            return total
        # Backward: `gives` is the one term the formula solves for, and
        # `needs` carries the slot first, then the other terms.
        value = held[self.slot_key] - total
        own = None
        for key, factor in zip(self.needs, self.factors):
            if key == self.slot_key:
                continue
            if key == self.gives[0]:
                own = factor
                continue
            value = value - held[key] * factor
        return value / own

    def predicts(self, held, constant=None):
        """What a CHECK edge's formula says its coordinate should hold,
        or move by."""
        total = self.constant if constant is None else constant
        for key, factor in zip(self.needs, self.factors):
            if key == self.slot_key:
                continue
            total = total + held[key] * factor
        return total


def _evaluated(graph, inputs):
    if graph is None:
        # A law whose expression has no free coordinate -- a constant --
        # has zero slope everywhere, so it contributes nothing. It moves
        # nothing by JUMPING either, and untimed it legitimately pins its
        # driven coordinate, so it is not refused: the running reading
        # (the coordinate holds where the rest render put it) is the same
        # statement.
        return 0.0
    return graph.evaluate(inputs)


class Program:
    """A running root's relations, compiled once, in order.

    `identity` is what a snapshot is checked against: a digest of the
    root class, the bank's ids, the inputs' declarations and every edge's
    ends, direction and expression, so a snapshot cannot be restored into
    a tree whose kinematics have moved on.
    """

    def __init__(self, root, inputs, coordinates, nodes, edges, spans=(),
                 declared=None, bound_reads=None):
        self.root_class = type(root)
        self.inputs = tuple(inputs)
        self.coordinates = tuple(coordinates)
        # `{qualified id: (unit, domain)}` for every banked JOINT
        # coordinate, read off the port declaration once so the
        # published table needs no second walk of the tree.
        self.declared = dict(declared or {})
        # The bank plus every end a KEPT edge reads or gives --
        # `compile_program`'s only caller, already reduced to that
        # before this constructor runs. A coordinate no edge here
        # touches is not part of the program: its relation was left to
        # the ordinary enumeration, and nothing below -- `sources`,
        # `published`, `published_names`, `_refuse_unqualified` -- may
        # see it.
        self.nodes = nodes
        self.edges = tuple(edges)
        self.determiner = {key: edge for edge in self.edges
                           for key in edge.gives}
        # Every banked coordinate whose joint declares a range, each
        # bound a number, `None`, or a compiled graph over the
        # coordinate's own id.
        self.spans = tuple(spans)
        self.sources = _reaching_inputs(self.nodes, self.edges)
        # The bank's own ids, both ways. `Run` kept these; they moved
        # here with `values_of`/`deltas_of`, so the tick and the control
        # measurement address the program through one mapping.
        self.keys = {node.name: key for key, node in self.nodes.items()
                     if node.kind in ('input', 'bank')}
        self.bank_keys = frozenset(self.keys.values())
        # The compiled controls, in qualified-name order. Assigned by
        # `compile_program` after this constructor, because a control's
        # admission is checked against `sources`, which is computed
        # here. DELIBERATELY absent from `described()` below: a control
        # changes nothing the run computes, so a snapshot taken against
        # a program must not be refused because one was added or
        # removed.
        self.controls = ()
        # The CONSTRAINTS: one per bound that reads other coordinates,
        # built here because the sub-program is a filter of `self.edges`
        # and the candidates a union over `self.sources`, both of which
        # exist only now. Derived, with no decision in them, so a
        # document publishes neither (ADR-110).
        self.constraints = self._constraint_table(bound_reads or {})
        self.identity = hashlib.sha256(
            self.described().encode()).hexdigest()

    def _constraint_table(self, bound_reads):
        """`{(identifier, side): Constraint}` for every bound that reads
        other coordinates."""
        by_name = {node.name: key for key, node in self.nodes.items()}
        found = {}
        for (identifier, side), read_ids in bound_reads.items():
            graph = next(entry[1 if side == 'low' else 2]
                         for entry in self.spans if entry[0] == identifier)
            keys = [by_name[identifier]]
            keys.extend(by_name[read_id] for read_id in read_ids)
            candidates = sorted(
                frozenset().union(*(self.sources.get(key, frozenset())
                                    for key in keys)))
            found[(identifier, side)] = Constraint(
                identifier, side, graph, tuple(read_ids),
                self._sub_program(keys), tuple(candidates))
        return found

    def _sub_program(self, keys):
        """The compiled edges that determine `keys` and everything they
        need, in the program's own order: the SUB-PROGRAM a constraint's
        level is sampled over, so the sample arithmetic is the segment
        arithmetic, edge for edge."""
        needed = set(keys)
        chosen = []
        for edge in reversed(self.edges):
            if edge.kind == 'check':
                continue
            if any(key in needed for key in edge.gives):
                chosen.append(edge)
                needed.update(edge.needs)
        chosen.reverse()
        return tuple(chosen)

    def described(self):
        """The canonical listing the identity is taken of, and what a
        message about the program prints."""
        lines = [f'root {self.root_class.__module__}.'
                 f'{self.root_class.__qualname__}']
        for identifier, declaration in self.inputs:
            lines.append(f'input {identifier} dtype={declaration.dtype!r} '
                         f'scale={declaration.scale!r}')
        for identifier in self.coordinates:
            lines.append(f'coordinate {identifier}')
        for identifier, low, high, unit in self.spans:
            # A changed range changes the identity, so a snapshot cannot
            # be restored into a machine whose stops have moved.
            lines.append(f'span {identifier} {_written(low)} to '
                         f'{_written(high)} {unit or "units"}')
        for edge in self.edges:
            ends = (f'{[self.nodes[key].name for key in edge.needs]} -> '
                    f'{[self.nodes[key].name for key in edge.gives]}')
            if edge.kind == 'law':
                how = ' | '.join('constant' if graph is None else str(graph)
                                 for graph in edge.graphs)
            elif edge.kind == 'wiring':
                how = f'identity * {edge.factors[0]!r}'
            else:
                how = (f'{list(edge.factors)!r} + {edge.constant!r} '
                       f'on {self.nodes[edge.slot_key].name}')
            lines.append(f'{edge.kind} {ends} {how} [{edge.description}]')
        return '\n'.join(lines)

    ##############################################
    # The arithmetic the tick and the measurement share

    def values_of(self, bank):
        """The bank, plus every INTERMEDIATE this program computes from
        it: a plain port or a derived coordinate a compiled edge
        determines, recomputed here rather than stored.

        `Run._values`' own body, moved here so the tick and the control
        measurement have ONE implementation of "the bank plus the
        intermediates" rather than two to keep in step. The corpus
        replay is what proves the move changed nothing.
        """
        values = {self.keys[identifier]: value
                  for identifier, value in bank.items()}
        for edge in self.edges:
            if all(key in self.bank_keys for key in edge.gives):
                # Nothing this edge computes is an intermediate, so its
                # values were computed here and discarded. Skipping it is
                # behaviour-neutral and removes one graph evaluation per
                # law per tick -- and, with the refusal of a jumping law
                # that drives no owned coordinate, it means a jump graph
                # is never evaluated absolutely at all.
                continue
            for key, value in edge.values(values):
                if key not in self.bank_keys:
                    values[key] = value
        return values

    def deltas_of(self, admissions):
        """One displacement per input, zero everywhere else."""
        deltas = {key: 0.0 for key in self.nodes}
        for input_id, delta in admissions.items():
            if delta:
                deltas[self.keys[input_id]] = delta
        return deltas

    def response(self, bank, input_id, epsilon):
        """What every banked coordinate moves by when `input_id` alone
        is displaced by `epsilon` at `bank`.

        The tick's own propagation with NO command, no stop, no staging
        and no record: `values_of`, seeded with one displacement, then
        ONE ordered pass over `edge.increments`. A probe on the
        originating worktree measured it against the run itself and the
        two agree BIT FOR BIT with what
        `sim.move(input_id, by=epsilon, duration=0)` commits on a fresh
        simulation.

        Pure arithmetic over the compiled program, off the tree
        entirely, which is what the ratio measurement needs:
        `program_of` asks a LIVE run for its program rather than
        constructing one, because publication must leave a running
        simulation's ownership, bank and ability to advance intact, and
        constructing a `Sim` releases whatever run owns the tree.

        A CHECK edge determines nothing and is skipped; the conflict
        detection and the messages a failed TICK needs stay on
        `Run._pass`, which a measurement does not have and must not
        borrow.
        """
        values = self.values_of(bank)
        deltas = self.deltas_of({input_id: epsilon})
        for edge in self.edges:
            if edge.kind == 'check':
                continue
            for key, delta in edge.increments(values, deltas):
                deltas[key] = delta
        return {identifier: deltas[key]
                for identifier, key in self.keys.items()}

    ##############################################
    # Publication

    def published_controls(self, initial):
        """The version 5 document's `controls` table, keyed and ORDERED
        by qualified control name, each entry's fields in a fixed order,
        so republishing an unchanged model is byte-identical.

        `operation_span` is LAST and present only where the compiled
        control carries one, which is what keeps an entry published
        before it existed byte-identical to the one published now.

        `initial` is the REST BANK, the same one `published` takes, and
        the only thing the ratio is measured at.
        """
        table = {}
        for control in self.controls:
            entry = {'kind': control.kind, 'part': list(control.part)}
            if control.kind == 'button':
                entry['instruction'] = control.instruction
            else:
                entry['input'] = control.input
                entry['per_unit'] = self._per_unit(initial, control)
            entry['joint'] = list(control.joint)
            entry['coordinate'] = control.coordinate
            entry['axis'] = [float(component) for component in control.axis]
            entry['origin'] = [float(component)
                               for component in control.origin]
            if control.span is not None:
                entry['operation_span'] = [control.span[0], control.span[1]]
            table[control.name] = entry
        return table

    def _per_unit(self, initial, control):
        """The coordinate units the part moves per DESIGN unit the input
        travels, measured at the rest bank in BOTH directions.

        The displacement is seeded in the BANK's own units -- native,
        which for an integer driver is one whole step, because
        `Driver.native` rounds a design-unit displacement to whole
        native units ONCE and a displacement below half a step is no
        displacement at all -- and divided by what that displacement is
        worth in design units. For the ordinary unscaled driver the two
        are the same number, `2**-20`: a power of two, so the division
        is exact and an affine chain publishes `-36.0` rather than a
        rounded neighbour of it.

        Both directions are read because one number is what a gesture is
        scaled by: a law with a kink at the rest value has two, and a
        drag scaled by the other direction's would be wrong in one
        direction. The window is this module's own `_CONTROL_AGREEMENT`
        and NOT the program's `agreement`: that one is the window inside
        which two increments of ONE movement are called equal, while
        this is a two-sided finite difference over a law that is allowed
        to curve, and `1e-9` would refuse every smooth non-affine law.

        The published number is the FORWARD reading. A mean would be a
        number neither direction produced.
        """
        declaration = dict(self.inputs)[control.input]
        native, design = _control_displacement(declaration)
        forward = self.response(
            initial, control.input, native)[control.coordinate] / design
        backward = self.response(
            initial, control.input, -native)[control.coordinate] / -design
        if forward == 0.0 and backward == 0.0:
            raise ControlError(
                f"the control '{control.name}' moves "
                f"{'.'.join(control.part)} with the input "
                f"'{control.input}', and at the rest bank that part does "
                f"not move with that input at all: displacing "
                f"'{control.input}' moves the coordinate "
                f"'{control.coordinate}' by nothing in either direction. "
                f"Reaching a coordinate through the program is necessary "
                f"and not sufficient -- an input coupled only through a "
                f"law that is disengaged at rest reaches it and moves it "
                f"not at all -- so there is no scale for the gesture.")
        window = _CONTROL_AGREEMENT * max(abs(forward), abs(backward))
        if abs(forward - backward) > window:
            raise ControlError(
                f"the control '{control.name}' moves the coordinate "
                f"'{control.coordinate}' with the input '{control.input}', "
                f"and the two directions do not agree at the rest bank: "
                f"forward reads {forward!r} and backward {backward!r} "
                f"coordinate units per design unit. A law whose response "
                f"at rest is not one number gives the gesture no single "
                f"scale, and a drag scaled by one of them would be wrong "
                f"in the other direction. A law that merely CURVES agrees "
                f"well inside the window of "
                f"{_CONTROL_AGREEMENT!r} relative; this is a kink, a jump "
                f"or a one-way law at the value the part rests at.")
        return forward

    def published(self, initial):
        """The projection a version 5 document carries: what COMPILE
        TIME decided about this machine, and nothing the tick computes.

        `initial` is the REST BANK -- `dict(sim.initial.bank)` -- the one
        number a consumer cannot compute, because computing it means
        running the CAD tree's rest render.

        Every expression slot holds a native graph rather than text: the
        document's own binding pass compiles them together with the
        tree's, so a subexpression a law shares with its own plan's level
        quantity is published once and nothing carries producer-local
        `let(...)` syntax. Branch placeholders are minted HERE, across
        the whole document -- `_j0`, `_j1`, ... in edge order and then
        the graph's postorder -- because the compiler names them per plan
        and three plans calling their first jump `$j0` would let the
        binding pass share one subtree between three different jump
        nodes.
        """
        self._refuse_unqualified()
        names = self.published_names()
        placeholders = self._placeholders(names)
        return {
            'identity': self.identity,
            'clock': CLOCK_NAME,
            'coordinates': self._published_coordinates(initial),
            'intermediates': sorted(
                node.name for node in self.nodes.values()
                if node.kind == 'intermediate'),
            'edges': [self._published_edge(edge, placeholders[index])
                      for index, edge in enumerate(self.edges)],
            'spans': {identifier: {'low': _published_bound(low),
                                   'high': _published_bound(high)}
                      for identifier, low, high, _unit in self.spans},
            'sources': {self.nodes[key].name: sorted(names)
                        for key, names in sorted(
                            self.sources.items(),
                            key=lambda item: self.nodes[item[0]].name)},
            'limits': {
                'crossing_tolerance': _CROSSING_TOLERANCE,
                'subdivisions': _SUBDIVISIONS,
                'bisection_rounds': _BISECTION_ROUNDS,
                'max_crossings': _MAX_CROSSINGS,
                'agreement': _agreement(),
            },
        }

    def published_names(self):
        """Every id the published program's expressions may read: the
        inputs, the bank's coordinates and the intermediates.

        The set a minted name must not collide with, and the set the
        document's binding pass is given so it cannot mint one either.
        """
        found = {identifier for identifier, _declaration in self.inputs}
        found.update(self.coordinates)
        found.update(node.name for node in self.nodes.values())
        return found

    def _refuse_unqualified(self):
        for node in self.nodes.values():
            if node.qualified:
                continue
            raise UnsupportedLaw(
                f"the program names '{node.name}', which is a FALLBACK "
                f'derived from a class name rather than an instance '
                f'path: the node it belongs to is not linked under the '
                f'root, so its qualified id is not computable. A class '
                f'name is not unique across two instances of that class, '
                f'and publishing it would put two different coordinates '
                f'under one name in one expression scope. Hold the node '
                f'on its own attribute of its parent.')

    def _published_coordinates(self, initial):
        entries = {}
        for identifier, _declaration in self.inputs:
            entries[identifier] = {
                'kind': 'input',
                'initial': initial[identifier],
                # A driver declares no DOMAIN -- see the export spec --
                # so there is none to publish and none is invented.
                'domain': None,
            }
        for identifier in self.coordinates:
            unit, domain = self.declared.get(identifier, (None, None))
            entries[identifier] = {
                'kind': 'coordinate',
                'initial': initial[identifier],
                'unit': unit,
                'domain': domain,
            }
        return entries

    def _placeholders(self, names):
        """One `{compiler name: published name}` map per edge, in edge
        order and then the graph's postorder, under a prefix lengthened
        while any published id matches `<prefix>` followed by digits."""
        prefix = _placeholder_prefix(names)
        minted = 0
        found = []
        for edge in self.edges:
            per_edge = []
            for index in range(len(edge.gives)):
                plan = edge.plans[index] if edge.plans else None
                mapping = {}
                if plan is not None:
                    for jump in plan.jumps:
                        mapping[jump.placeholder] = f'{prefix}{minted}'
                        minted += 1
                per_edge.append(mapping)
            found.append(per_edge)
        return found

    def _published_edge(self, edge, placeholders):
        entry = {
            'kind': edge.kind,
            'needs': [self.nodes[key].name for key in edge.needs],
            'gives': [self.nodes[key].name for key in edge.gives],
            'description': edge.description,
            'stated_by': edge.stated_by,
        }
        if edge.kind == 'law':
            entry['expressions'] = list(edge.graphs)
            entry['affine'] = list(edge.affine)
            entry['plans'] = [
                _published_plan(edge.plans[index] if edge.plans else None,
                                placeholders[index])
                for index in range(len(edge.gives))]
        elif edge.kind == 'wiring':
            entry['factor'] = edge.factors[0]
        else:
            entry['factors'] = list(edge.factors)
            entry['constant'] = edge.constant
            entry['slot'] = self.nodes[edge.slot_key].name
        return entry

    def __repr__(self):
        return (f'<program of {self.root_class.__name__}: '
                f'{len(self.nodes)} coordinates, {len(self.edges)} edges>')


def _written(bound):
    """One bound as the identity prints it."""
    if bound is None:
        return 'unbounded'
    if isinstance(bound, GraphValue):
        return str(bound)
    return repr(bound)


def _reaching_inputs(nodes, edges):
    """Every INPUT that reaches each node key through the program: the
    CANDIDATE table a stop's group is filtered out of.

    One pass over the already topologically ordered edges, so it costs
    the program once and nothing per tick. A CHECK edge determines
    nothing and contributes nothing. Being reached is necessary and not
    sufficient: whether a candidate actually PUSHES a stopped coordinate
    is a property of the tick, tested there, because an input coupled
    only through a disengaged law reaches it and moves it not at all.
    """
    found = {key: (frozenset({key[1]}) if node.kind == 'input'
                   else frozenset())
             for key, node in nodes.items()}
    for edge in edges:
        if edge.kind == 'check':
            continue
        reached = frozenset().union(*(found[key] for key in edge.needs)) \
            if edge.needs else frozenset()
        for key in edge.gives:
            found[key] |= reached
    return found


class _Node:
    """One coordinate the program computes over: a bank id, or an
    INTERMEDIATE a compiled edge determines.

    `_register` mints one of these for every end of every CANDIDATE
    edge, before `_reaching_the_bank` has decided which candidates the
    program keeps -- it cannot know in advance which ends will turn out
    to belong to a relation left to the ordinary enumeration.
    `compile_program` is what makes the class docstring's "or an
    INTERMEDIATE a compiled edge determines" true of `Program.nodes`:
    it drops the ends of every candidate that did not survive.

    `qualified` is whether `name` is the instance-qualified id or the
    `<ClassName>.<name>` FALLBACK `_qualified` takes when the node is not
    linked under the root. The fallback is good enough for a message and
    is not unique across two instances of one class, so publication
    refuses it rather than putting two coordinates under one name in one
    expression scope.
    """

    __slots__ = ('key', 'name', 'kind', 'qualified')

    def __init__(self, key, name, kind, qualified=True):
        self.key = key
        self.name = name
        self.kind = kind
        self.qualified = qualified

    def __repr__(self):
        return f'<{self.kind} {self.name}>'


##############################################
# Compiling


def compile_program(root, inputs, coordinates, controls=None,
                    instructions=None):
    """The program of `root`, read off what the REST RENDER solved.

    `inputs` is `{qualified id: Driver}` and `coordinates` is
    `{qualified id: (node, name)}`; together they are the bank.

    `controls` and `instructions` are the enumerations `Sim` already
    holds -- `{qualified name: (node, path, declaration)}` each. The
    controls are compiled to the coordinate, joint, axis and origin they
    name, AFTER the program exists, because a `Turn`'s admission is
    checked against `sources`, which the program computes. Nothing about
    the program itself changes: `described()` and therefore `identity`
    never learn that a control exists.
    """
    nodes = {}
    for identifier, _declaration in inputs.items():
        nodes[('input', identifier)] = _Node(
            ('input', identifier), identifier, 'input')
    bank_keys = set(nodes)
    for identifier, (node, name) in coordinates.items():
        from solid_node.motion.ports import get_coordinate

        slot = get_coordinate(node, name)
        key = ('slot', id(slot))
        nodes[key] = _Node(key, identifier, 'bank')
        bank_keys.add(key)

    candidates = []
    for assembly, path, records, formulas, wirings in _units(root):
        for record in records:
            edge = _relation_edge(root, assembly, record, nodes, bank_keys)
            if edge is not None:
                candidates.append(edge)
        for wiring in wirings:
            edge = _wiring_edge(root, assembly, wiring, nodes)
            if edge is not None:
                candidates.append(edge)
        for formula in formulas:
            edge = _formula_edge(root, assembly, formula, nodes)
            if edge is not None:
                candidates.append(edge)

    kept = _reaching_the_bank(candidates, bank_keys)
    # `_register` made a node for every end of every CANDIDATE, before
    # `_reaching_the_bank` decided which ones survive -- it cannot know
    # a candidate will be dropped until the walk above has run. A
    # coordinate no kept edge reads or gives is not part of the
    # program: its relation is left to the ordinary enumeration, and
    # the table the rest of `Program` reads as "what this program
    # computes" must not go on carrying it.
    touched = set(bank_keys)
    for edge in kept:
        touched.update(edge.needs)
        touched.update(edge.gives)
    nodes = {key: node for key, node in nodes.items() if key in touched}
    _refuse_opaque(kept, bank_keys, nodes)
    ordered = _ordered(kept, nodes)
    spans, bound_reads = _compiled_spans(root, inputs, coordinates)
    program = Program(root, sorted(inputs.items()), sorted(coordinates),
                      nodes, ordered, spans,
                      _declared_coordinates(coordinates), bound_reads)
    if controls:
        program.controls = _compiled_controls(
            root, program, coordinates, controls, instructions or {})
    return program


##############################################
# The control table


# The window inside which the two directions of the ratio measurement
# are called one number, RELATIVE. Deliberately not the program's own
# `agreement`: that is the window inside which two increments of one
# movement are equal, and this is a two-sided finite difference over a
# law the authority explicitly permits to curve. `1e-3` catches a kink,
# a jump and a one-way law at rest, and admits curvature.
_CONTROL_AGREEMENT = 1e-3

# The displacement a ratio is measured with, in the BANK's own units. A
# power of two, so the division by it is exact and a composed affine
# chain publishes the exact product rather than a rounded neighbour.
_CONTROL_DISPLACEMENT = 2.0 ** -20


def _control_displacement(declaration):
    """`(native, design)`: how far to displace this input in the bank's
    own units, and what that displacement is worth in design units.

    An INTEGER driver counts whole native units, so it is displaced by
    one of them; anything smaller rounds to nothing and would read as a
    part that does not move. Everything else takes the power-of-two
    displacement.
    """
    native = 1.0 if declaration.dtype is int else _CONTROL_DISPLACEMENT
    design = native if declaration.scale is None \
        else native * declaration.scale
    return native, design


class _Control:
    """One control, compiled: what a consumer needs to draw the
    gesture and to issue the request.

    `part` and `joint` are TUPLES OF NODE NAMES from the document's own
    root down, because a node name is not always a legal identifier and
    a consumer walks the document's tree by name anyway; `coordinate`
    and `input` are dotted qualified ids, because they are expression
    names and must be. `axis` and `origin` are in the JOINT NODE's own
    frame, being exactly the values `Joint.place` built the placement
    from.

    `span` is the half-open pair of indices identifying that placement
    inside the joint node's own `operations`, or `None` where there is
    nothing to distinguish: a single inferred rotational joint turns its
    own axis and its own pivot into themselves, so the joint node's
    whole world matrix carries them correctly and the legacy entry says
    nothing more. A translational coordinate, and any coordinate the
    author SELECTED, needs the block named: the frame that carries the
    gesture is the parent's world matrix composed with the operations
    AFTER the block, and an inner joint's motion must never be applied
    to an outer joint's line.
    """

    __slots__ = ('kind', 'name', 'part', 'joint', 'coordinate', 'axis',
                 'origin', 'span', 'instruction', 'input')

    def __init__(self, kind, name, part, joint, coordinate, axis, origin,
                 span=None, instruction=None, input=None):
        self.kind = kind
        self.name = name
        self.part = part
        self.joint = joint
        self.coordinate = coordinate
        self.axis = axis
        self.origin = origin
        self.span = span
        self.instruction = instruction
        self.input = input

    def __repr__(self):
        return (f'<{self.kind} {self.name!r} on {".".join(self.part)} '
                f'about {self.coordinate}>')


class ControlError(ValueError):
    """A control the compiled program cannot resolve."""


def _compiled_controls(root, program, coordinates, controls, instructions):
    """Every declared control, compiled, in QUALIFIED NAME order.

    A control whose part THIS RENDER OMITTED is left out rather than
    refused: `omit()` leaves a node "not linked, built, exported, fused
    or serialized", so the document genuinely does not contain that part
    and `--set covers=false` on a machine with a control on the lid must
    still build. Every OTHER way a part could fail to resolve was
    already refused at class definition, so this cannot hide a
    misdeclaration.
    """
    owners = {}
    for identifier, (node, name) in coordinates.items():
        owners.setdefault(id(node), {})[name] = identifier
    found = []
    for name in sorted(controls):
        declaring, path, control = controls[name]
        part_node = control.part._walk(declaring)
        try:
            part_path = instance_path(part_node, root)
        except DriverIdError:
            # Not linked under the root: this render omitted it.
            continue
        if control.coordinate is None:
            joint_node, joint = _posing_joint(part_node, root, owners, name,
                                              control)
        else:
            joint_node, joint = _selected_joint(part_node, root, owners,
                                                name, control, declaring)
        coordinate = owners[id(joint_node)][coordinates_of(joint)[0]]
        axis, origin = _placed_geometry(joint_node, joint)
        entry = dict(
            kind=control.control_kind, name=name, part=part_path,
            joint=instance_path(joint_node, root), coordinate=coordinate,
            axis=axis, origin=origin,
            span=_published_span(joint_node, joint, name, control,
                                 program, coordinate))
        if control.control_kind == 'button':
            entry['instruction'] = _checked_instruction(
                name, path, control, instructions)
        else:
            entry['input'] = _checked_input(
                name, path, control, declaring, program, coordinate)
        found.append(_Control(**entry))
    return tuple(found)


def _posing_joint(part_node, root, owners, name, control):
    """The nearest ancestor-or-self of the part whose joint the run
    banks, and that joint.

    A part moved only by an author's own `render()` arithmetic over a
    plain port is refused here deliberately: a control's gesture is a
    JOINT's motion, and a hand-written rotation is not one.
    """
    current = part_node
    while True:
        owned = owners.get(id(current))
        if owned is not None:
            break
        parent = getattr(current, '_parent', None)
        if current is root or parent is None:
            raise ControlError(
                f"the control '{name}' is on "
                f"{type(part_node).__name__} '{part_node.name}' "
                f"({control.part.written}), and nothing the run owns moves "
                f"that part: no ancestor of it, and not the part itself, "
                f"declares a joint whose coordinate the run banks. A "
                f"control's gesture is a joint's motion -- a part posed by "
                f"a plain port an author's own render() turns is not one.")
        current = parent
    joints = declared_joints(type(current))
    if len(joints) > 1:
        raise ControlError(
            f"the control '{name}' is on a part posed by "
            f"{type(current).__name__} '{current.name}', which declares "
            f"{len(joints)} joints -- {', '.join(joints)} -- that compose "
            f"one motion between them. A control names ONE coordinate, and "
            f"neither of those is it: say which of them this control means "
            f"with coordinate=, or declare the control on a part posed by "
            f"a single joint.")
    joint = next(iter(joints.values()))
    owned = coordinates_of(joint)
    if len(owned) > 1:
        raise ControlError(
            f"the control '{name}' is on a part posed by the joint "
            f"'{joint.name}' of {type(current).__name__} "
            f"'{current.name}', which owns {len(owned)} coordinates -- "
            f"{', '.join(owned)}. A control names ONE coordinate, and a "
            f"free body's six are not one gesture.")
    return current, joint


def _selected_joint(part_node, root, owners, name, control, declaring):
    """The joint the author SELECTED, and the node it poses.

    Selection reaches exactly as far as inference does and no further:
    the joint must pose the touched part or one of its ancestors in this
    same tree, the run must bank its coordinate, and it must own one.
    What it adds is the CHOICE between the freedoms of one body, which
    no walk up the tree can make -- and the reach past a nearer joint to
    the one a hand actually means, which a walk up the tree would pass
    on its way and never reconsider.
    """
    joint = control.selected_declaration
    # Duck-typed on the dict of coordinates a JOINT owns, before
    # anything else: a derived coordinate of a child owns `coordinate`
    # and passes the declaration check, and asking it for the
    # coordinates a joint owns would fail as an attribute error rather
    # than as a refusal naming the control.
    owned = getattr(joint, 'coordinates', None)
    if not isinstance(owned, dict) or not owned:
        raise ControlError(
            f"the control '{name}' names '{control.selected}', which is "
            f"not a joint. A control's gesture is a JOINT's motion -- a "
            f"Revolute, a Prismatic, or another declaration that poses a "
            f"body -- and a derived coordinate, computed from the ones "
            f"that do, poses nothing.")
    node = control.selected_node(declaring)
    current = part_node
    while current is not node:
        parent = getattr(current, '_parent', None)
        if current is root or parent is None:
            raise ControlError(
                f"the control '{name}' is on "
                f"{'.'.join(instance_path(part_node, root))} "
                f"({control.part.written}) and names the coordinate "
                f"'{control.selected}', which poses neither that part nor "
                f"any ancestor of it. A control's gesture is the motion of "
                f"the part a hand takes hold of; a selection says WHICH of "
                f"that part's own freedoms is meant, and cannot reach "
                f"sideways to another mechanism.")
        current = parent
    declared = declared_joints(type(node))
    # Ownership of the written reference was checked at class definition.
    # A subclass or site may replace that named joint, just as it may
    # replace one reached by a relation. Its effective declaration owns
    # the current geometry and coordinate count, not the inherited object.
    joint = declared.get(joint.name)
    if joint is None:
        known = ', '.join(declared) or 'none'
        raise ControlError(
            f"the control '{name}' names the coordinate "
            f"'{control.selected}', which is not a joint of "
            f"{type(node).__name__} '{node.name}'. A control's gesture is "
            f"a joint's motion; {type(node).__name__} declares: {known}.")
    owned = tuple(joint.coordinates)
    if len(owned) > 1:
        raise ControlError(
            f"the control '{name}' names the joint '{control.selected}', "
            f"which owns {len(owned)} coordinates -- {', '.join(owned)}. A "
            f"control names ONE coordinate, and naming the joint a free "
            f"body floats on does not choose one of its six.")
    if owned[0] not in owners.get(id(node), {}):
        raise ControlError(
            f"the control '{name}' names the coordinate "
            f"'{control.selected}', which the run does not bank. A "
            f"control's gesture is a coordinate the run owns and commits; "
            f"nothing else poses a part.")
    return node, joint


def _published_span(node, joint, name, control, program, coordinate):
    """The half-open pair of operation indices identifying this joint's
    complete placement on `node`, or `None` where the entry publishes
    none.

    An INFERRED ROTATIONAL control publishes none, and that is what
    keeps every entry published before this change byte-identical: its
    joint is the only one on its node, and a rotation carries its own
    axis and its own pivot into themselves, so the joint node's whole
    world matrix is already the gesture's frame. Everything else needs
    the block named -- a translation moves the pivot of an inner joint,
    and an inner rotation turns the line of an outer one.

    The block is read off the placement's OWN ownership marks: every
    operation a joint places carries the slot its declaration holds
    (ADR-093, ADR-114), so the indices come from the thing that placed
    them and never from searching a published expression for a
    coordinate's name. An operation a sweep or a checkpoint restore has
    dropped would leave a block that is not one contiguous run, and that
    is refused rather than published as an invented frame.
    """
    domain = program.declared.get(coordinate, (None, None))[1]
    if control.coordinate is None and domain != 'translational':
        return None
    slot = list(declared_joints(type(node))).index(joint.name)
    indices = [index for index, operation in enumerate(node.operations)
               if getattr(operation, '_motion', False)
               and getattr(operation, '_joint_slot', None) == slot]
    if not indices or indices[-1] - indices[0] + 1 != len(indices):
        found = ('places none of that node\'s operations' if not indices
                 else f'places {len(indices)} of that node\'s operations '
                      f'and they are not one contiguous run')
        raise ControlError(
            f"the control '{name}' is about the coordinate "
            f"'{coordinate}', and the placement it names cannot be "
            f"identified on {type(node).__name__} '{node.name}': its joint "
            f"'{joint.name}' {found}. A gesture's frame is the operations "
            f"OUTSIDE its own placement, so a block that is not exactly "
            f"this coordinate's is refused rather than published as an "
            f"invented frame.")
    block = [node.operations[index] for index in indices]
    if any(getattr(operation, '_joint_length', None) != len(block)
           or getattr(operation, '_joint_index', None) != offset
           for offset, operation in enumerate(block)):
        raise ControlError(
            f"the control '{name}' names the coordinate '{coordinate}', "
            f"but joint '{joint.name}' on {type(node).__name__} "
            f"'{node.name}' does not retain its complete ordered placement. "
            f"A truncated, duplicated or reordered pivot cannot publish "
            f"a gesture's frame.")
    return indices[0], indices[-1] + 1


def _placed_geometry(node, joint):
    """The axis and the point `Joint.place` turned the node about,
    both in the node's OWN frame.

    Exactly `place`'s own two lines, including the SITE carry: a joint
    stated by the declaring parent has its axis and anchor carried
    through the inverse of the node's rest placement before the
    placement is built, so publishing what the site WROTE would give a
    consumer the wrong line.
    """
    anchor = joint.arguments(node)[1]
    axes = joint.axes(node)
    points = joint.carried_points(node, anchor)
    if joint._declared_at_site:
        axes, points = joint._carry(node, axes, points)
    return tuple(axes[0]), tuple(points[0])


def _checked_instruction(name, path, control, instructions):
    """A button's instruction, qualified through the DECLARING node's
    own path -- the rule `instructions_table` already applies to a
    target name, applied to a name."""
    qualified = '.'.join(path + (control.instruction,))
    if qualified in instructions:
        return qualified
    known = ', '.join(sorted(instructions)) or 'none'
    raise ControlError(
        f"the control '{name}' is a button for the instruction "
        f"'{qualified}', which nothing in this tree declares. A button "
        f"references an instruction and never repeats its definition; the "
        f"declared instructions are: {known}.")


def _checked_input(name, path, control, declaring, program, coordinate):
    """A drag's input, qualified through the declaring node's path,
    with the two things a DRAG needs of it checked: the coordinate moves
    the way this gesture does, and this input reaches it."""
    unit, domain = program.declared.get(coordinate, (None, None))
    required = control.required_domain
    if domain != required:
        raise ControlError(
            f"the control '{name}' is a {type(control).__name__} on the "
            f"coordinate '{coordinate}', whose domain is {domain!r} and "
            f"not {required!r}. A Turn is a drag ABOUT a rotational "
            f"coordinate and a Slide is a drag ALONG a translational one; "
            f"declare the gesture the part actually makes, or name the "
            f"coordinate it is about with coordinate=.")
    identifier = driver_id(path, control.local_input_of(type(declaring)))
    reaching = program.sources.get(program.keys[coordinate], frozenset())
    if identifier not in reaching:
        reach = ', '.join(sorted(reaching)) or 'no input at all'
        raise ControlError(
            f"the control '{name}' moves the coordinate '{coordinate}' "
            f"with the input '{identifier}', which does not reach it "
            f"through the compiled program. The inputs that DO reach "
            f"'{coordinate}' are: {reach}.")
    return identifier


def _declared_coordinates(coordinates):
    """Each banked coordinate's declared `(unit, domain)`.

    Read here, once, off the port the joint owns: the document publishes
    both beside the coordinate's rest value, and a consumer's readouts
    and jog controls then need no second reading of the tree.
    """
    from solid_node.motion.ports import get_coordinate

    return {identifier: (get_coordinate(node, name).unit,
                         get_coordinate(node, name).domain)
            for identifier, (node, name) in coordinates.items()}


##############################################
# The span table


def _compiled_spans(root, inputs, coordinates):
    """`(qualified id, low, high, unit)` for every banked coordinate
    whose joint declares a range, resolved ONCE -- and, per bound that
    READS other coordinates, the ids it reads.

    Each bound is a number, `None` for unbounded on that side, or an
    expression GRAPH over the coordinate's own qualified id and, for a
    `Bound`, the qualified ids of what it reads -- compiled here exactly
    as a law is, and for the same two reasons: what the expression
    cannot say is refused now rather than every tick, and a graph is
    what a version 5 document publishes beside the coordinate table.

    `root` is here because qualifying a read's owning node means
    `instance_path(node, root)`, the same path `_qualified` takes; the
    bank ids a read may name are the inputs and the joint coordinates
    together.
    """
    from solid_node.motion.joints import Bound

    bank = set(inputs) | set(coordinates)
    found = []
    reads = {}
    for identifier, (node, name) in sorted(coordinates.items()):
        for joint in declared_joints(type(node)).values():
            if name not in joint.coordinates:
                continue
            span = joint.arguments(node)[2]
            if span is not None:
                sides = []
                for index, side in ((0, 'lower'), (1, 'upper')):
                    bound = span[index]
                    if isinstance(bound, Bound):
                        read_ids = _qualified_reads(
                            root, bank, bound, node, joint, side, identifier)
                        reads[(identifier,
                               'low' if side == 'lower' else 'high')] = \
                            read_ids
                        sides.append(_compiled_bound(
                            bound, identifier, node, joint, side, read_ids))
                    else:
                        sides.append(_compiled_bound(
                            bound, identifier, node, joint, side))
                found.append((identifier, sides[0], sides[1], joint.unit))
            break
    return tuple(found), reads


def _qualified_reads(root, bank, bound, node, joint, side, identifier):
    """A `Bound`'s reads as the qualified ids the BANK keys by.

    A read that is not a bank entry -- a plain port, a derived
    coordinate -- is refused here, by joint and node identity: a bound
    reads the STATE, and a port is a calculation the enumeration
    recomputes from it.
    """
    def refuse(detail):
        raise UnsupportedLaw(
            f"{type(node).__name__}.{joint.name}: its {side} bound -- "
            f"the range of the coordinate '{identifier}' -- {detail}")

    found = []
    for end in joint.bound_reads(node, side):
        read_id, qualified = _qualified(root, end)
        if not qualified or read_id not in bank:
            refuse(f"reads '{read_id}', which the run does not bank. A "
                   f"bound reads the STATE -- a joint coordinate or a "
                   f"declared input -- and a plain port or a derived "
                   f"coordinate is a calculation the enumeration "
                   f"recomputes from it on every tick. Read the joint "
                   f"the port follows.")
        if read_id in found:
            refuse(f"reads '{read_id}' twice, so one value would take "
                   f"two positions of the expression. Name it once.")
        found.append(read_id)
    return tuple(found)


def _compiled_bound(bound, identifier, node, joint, side, read_ids=None):
    """One declared bound as the run reads it: `None`, a float, or an
    expression graph over `identifier` and whatever it reads."""
    from solid_node.motion.joints import Bound

    def refuse(detail):
        raise UnsupportedLaw(
            f"{type(node).__name__}.{joint.name}: its {side} bound -- "
            f"the range of the coordinate '{identifier}' -- {detail}")

    if isinstance(bound, Bound):
        return _compiled_reading_bound(bound, identifier, read_ids, refuse)
    if bound is None:
        return None
    if isinstance(bound, bool):
        refuse(f'is {bound!r}, which is neither a number nor an expression.')
    if isinstance(bound, (int, float)):
        return float(bound)
    if not callable(bound):
        refuse(f'resolved to {bound!r}, which is neither a number nor a '
               f"callable of the joint's own coordinate.")
    try:
        returned = bound(symbol(identifier))
    except Exception as failure:
        refuse(f'cannot be applied to a symbol '
               f'({type(failure).__name__}: {failure}). A bound is an '
               f'expression over the joint\'s own coordinate: it is applied '
               f'once, to a token for that coordinate, and the graph it '
               f'builds is what the run evaluates at the start of every '
               f'tick. Write it with solid_node.math, whose primitives are '
               f'symbolic.')
    if isinstance(returned, bool):
        refuse(f'returned {returned!r}, which is neither a number nor an '
               f'expression.')
    if isinstance(returned, (int, float)):
        return float(returned)
    if not isinstance(returned, OpenSCADConstant):
        refuse(f'returned {returned!r}, which is neither a number nor an '
               f"expression over the joint's own coordinate.")
    root = as_node(returned)
    for item in postorder([root]):
        if item.kind == 'raw':
            refuse(f'carries the text {item.text!r}, which the framework '
                   f'cannot evaluate.')
        if item.kind == 'call' and item.op not in SYMBOLIC_BUILTINS:
            refuse(f'calls {item.op!r}, which is outside the symbolic '
                   f'vocabulary the run can evaluate.')
    names = free_names(root)
    if not names <= {identifier}:
        others = ', '.join(sorted(names - {identifier}))
        refuse(f'reads {others}, and a bound stated as a plain callable is '
               f"an expression over the joint's OWN coordinate alone. A "
               f'bound naming a second coordinate says what it reads: '
               f'Bound(expression, reads=(...)).')
    # A JUMP is admitted and needs no plan: a bound is EVALUATED at one
    # point per tick and never integrated, so `floor` means `floor` and
    # nothing is subtracted. That asymmetry with a law is the point -- a
    # law's jump would move a part, a bound's jump is the tooth pitch.
    return GraphValue(root)


def _compiled_reading_bound(bound, identifier, read_ids, refuse):
    """A `Bound` as one graph over the joint's own id and the ids it
    reads, applied once, in declared order.

    The same walk a one-argument bound takes -- raw text refused, calls
    outside the symbolic vocabulary refused -- with the free-name check
    widened from the own id alone to the own id and the reads. A JUMP is
    admitted and needs no plan, for the reason it is admitted there: a
    bound is EVALUATED at a point, never integrated.
    """
    tokens = [symbol(read_id) for read_id in read_ids]
    try:
        returned = bound.arguments(symbol(identifier), tokens)
    except Exception as failure:
        refuse(f'cannot be applied to symbols '
               f'({type(failure).__name__}: {failure}). A bound is an '
               f"expression over the joint's own coordinate and the "
               f'coordinates it reads: it is applied once, to a token for '
               f'each, own coordinate first and then each read in the '
               f'order reads= states them, and the graph it builds is what '
               f'the run evaluates along the tick. Write it with '
               f'solid_node.math, whose primitives are symbolic.')
    if isinstance(returned, bool):
        refuse(f'returned {returned!r}, which is neither a number nor an '
               f'expression.')
    if isinstance(returned, (int, float)):
        # A Bound that declares a read and returns a NUMBER reads
        # nothing it declares. Refused here rather than carried as a
        # constraint with no expression to evaluate along the tick.
        refuse(f'declares reads=({", ".join(read_ids)}) and returns the '
               f'number {returned!r}, so it never reads what it declares. '
               f'A bound that reads other coordinates is an expression '
               f'over them; a bound that is a number is written as one.')
    if not isinstance(returned, OpenSCADConstant):
        refuse(f'returned {returned!r}, which is neither a number nor an '
               f'expression over the coordinates it was given.')
    root = as_node(returned)
    for item in postorder([root]):
        if item.kind == 'raw':
            refuse(f'carries the text {item.text!r}, which the framework '
                   f'cannot evaluate.')
        if item.kind == 'call' and item.op not in SYMBOLIC_BUILTINS:
            refuse(f'calls {item.op!r}, which is outside the symbolic '
                   f'vocabulary the run can evaluate.')
    names = free_names(root)
    allowed = {identifier} | set(read_ids)
    if not names <= allowed:
        others = ', '.join(sorted(names - allowed))
        refuse(f'reads {others}, which is neither its own coordinate nor '
               f'one of the coordinates reads= names.')
    unused = [read_id for read_id in read_ids if read_id not in names]
    if unused:
        # The declaration says it reads what the expression does not: a
        # bound is applied to every read it names, and a read the
        # expression cannot see is a mistake in the model, not a
        # coordinate to sample along every tick for nothing.
        refuse(f'declares reads=({", ".join(read_ids)}) but its '
               f'expression never reads {", ".join(unused)}. A bound reads '
               f'every coordinate it names; drop the read, or use it.')
    return GraphValue(root)


def _units(root):
    """Every assembly of the linked tree with what its own rest render
    recorded: its relation records, the derived coordinates it solves and
    its wirings, in tree order."""
    from solid_node.node.assembly import _rest_children

    found = []

    def visit(node, path):
        if getattr(node, '_states', None) is None:
            return
        records = node.__dict__.get('_relations', ())
        found.append((node, path, records,
                      _solved_formulas(node, records), _wirings(node)))
        for child in _rest_children(node):
            visit(child, path + (child.name,))

    visit(root, ())
    return found


def _register(nodes, root, end):
    """`end`'s program node, created on first sight."""
    name, qualified = _qualified(root, end)
    if end.is_driver:
        key = ('input', name)
    else:
        key = ('slot', id(end.slot))
    found = nodes.get(key)
    if found is None:
        found = nodes[key] = _Node(key, name, 'intermediate', qualified)
    return found


def _qualified(root, end):
    """`end`'s qualified id and whether it IS one.

    The `<ClassName>.<name>` fallback names the node in a refusal; it is
    not unique across two instances of one class, which is why the flag
    travels with it.
    """
    from solid_node.node.qualified import DriverIdError

    try:
        return driver_id(instance_path(end.node, root), end.name), True
    except DriverIdError:
        return f'{type(end.node).__name__}.{end.name}', False


def _relation_edge(root, assembly, record, nodes, bank_keys):
    """One relation as an edge, in the direction the rest render solved
    it -- or `None` when the rest render left it to no one."""
    if record.direction not in ('forward', 'backward'):
        return None
    if record.direction == 'forward':
        sources, targets = record.driver_ends, record.driven_ends
    else:
        sources, targets = record.driven_ends, record.driver_ends
    source_nodes = [_register(nodes, root, end) for end in sources]
    target_nodes = [_register(nodes, root, end) for end in targets]

    banked = [node.key in bank_keys for node in target_nodes]
    if any(banked) and not all(banked):
        raise UnsupportedLaw(
            f'{record.described()}, stated by {type(assembly).__name__}: '
            f'its driven ends are '
            f'{", ".join(node.name for node in target_nodes)}, of which the '
            f'running simulation owns only some. A relation drives one '
            f'group; state the rest as joints, or as a relation of their '
            f'own.')

    compiled = _law_graphs(assembly, record, source_nodes,
                           len(target_nodes))
    graphs = [graph for graph, _plan in compiled]
    plans = [plan for _graph, plan in compiled]
    if any(plan is not None for plan in plans) and not any(banked):
        # A subtracted jump implies a HISTORY, and an intermediate keeps
        # none: the ordinary enumeration recomputes it absolutely from
        # the bank on every tick, so its value would snap by the
        # accumulated jumps while the joint behind it moved smoothly.
        raise UnsupportedLaw(
            f'{record.described()}, stated by {type(assembly).__name__}: '
            f'its law contains a jump and its driven ends are '
            f'{", ".join(node.name for node in target_nodes)}, none of '
            f'which the running simulation owns. A subtracted jump implies '
            f'a history, and only a coordinate the run owns keeps one -- a '
            f'plain port and a derived coordinate are calculations the '
            f'ordinary enumeration recomputes from the bank on every tick, '
            f'so this one would snap while the joint behind it moved '
            f'smoothly. State the relation into the joint coordinate and '
            f'let the port follow it.')
    return Edge('law', [node.key for node in source_nodes],
                [node.key for node in target_nodes],
                record.described(), type(assembly).__name__,
                graphs=graphs,
                plans=plans if any(plan is not None for plan in plans) else (),
                driven=[node.name for node in target_nodes],
                names=[node.name for node in source_nodes])


def _law_graphs(assembly, record, source_nodes, count):
    """The law applied ONCE to a symbolic token per source, checked to be
    an expression the run can evaluate, and compiled into a jump plan
    where it jumps: one `(graph, plan)` per driven end."""
    def refuse(detail):
        raise UnsupportedLaw(
            f'{record.described()}, stated by {type(assembly).__name__}: '
            f'{detail}')

    tokens = [symbol(node.name) for node in source_nodes]
    try:
        if record.direction == 'backward':
            returned = record.law.inverse(tokens[0])
        else:
            returned = record.law.forward(*tokens)
    except Exception as failure:
        refuse(f'the law {record.law!r} cannot be applied to symbols '
               f'({type(failure).__name__}: {failure}). A running law is '
               f'an expression over its sources: it is applied once, to a '
               f'token per source, and the graph it builds is what the run '
               f'integrates. Write it with solid_node.math, whose '
               f'primitives are symbolic.')

    if count == 1:
        returned = (returned,)
    else:
        try:
            length = len(returned)
        except TypeError:
            length = None
        if length != count:
            refuse(f'the law {record.law!r} returned {returned!r} for '
                   f'{count} driven ends, which is not a sequence of '
                   f'exactly {count} values.')
    return [_graph_of(value, refuse) for value in returned]


def _graph_of(value, refuse):
    """`value` as the expression graph the run evaluates and the JUMP
    PLAN beside it, `(None, None)` for a constant, or the refusal naming
    what it is instead."""
    if isinstance(value, bool):
        refuse(f'the law returned {value!r}, which is neither a number nor '
               f'an expression.')
    if isinstance(value, (int, float)):
        return None, None
    if not isinstance(value, OpenSCADConstant):
        refuse(f'the law returned {value!r}, which is neither a number nor '
               f'an expression over its sources.')
    root = as_node(value)
    jumps = []
    for item in postorder([root]):
        if item.kind == 'raw':
            refuse(f'its expression carries the text {item.text!r}, which '
                   f'the framework cannot evaluate: a running law is an '
                   f'expression over its sources.')
        if item.kind == 'call' and item.op not in SYMBOLIC_BUILTINS:
            refuse(f'its expression calls {item.op!r}, which is outside '
                   f'the symbolic vocabulary the run can evaluate.')
        if _is_jump(item):
            jumps.append(item)
    if not jumps:
        return GraphValue(root), None
    if _only_jumps(root):
        refuse('its expression can move its driven coordinate only by '
               'jumping: with every jump node and the whole argument '
               'subtree beneath it replaced by a constant, no free '
               'coordinate is left. Every jump is subtracted -- a jump '
               'never moves a part -- so this law can never move anything '
               'at all. It states arithmetic, not a mechanism: give the '
               'coordinate a relation that carries slope, or leave the '
               'count to the code that reads the machine.')
    return GraphValue(root), _plan_of(root, jumps)


def _plan_of(root, jumps):
    """The jump plan of a graph: the skeleton, and the jump nodes in the
    graph's postorder with their level quantities."""
    placeholders = {node: ExpressionNode(
        'name', text=f'${"q" if node.op == "%" else "j"}{index}')
        for index, node in enumerate(jumps)}
    skeleton = _skeleton(root, placeholders)
    planned = []
    for node in jumps:
        argument = _argument_graph(node, skeleton.replaced)
        planned.append(_Jump(node.op, placeholders[node].text,
                             GraphValue(argument),
                             _affine_in_sources(argument)))
    return JumpPlan(GraphValue(skeleton.root), planned)


class _Rewritten:
    """A graph with every jump node replaced, and the replacement map
    the argument graphs are cut from."""

    __slots__ = ('root', 'replaced')

    def __init__(self, root, replaced):
        self.root = root
        self.replaced = replaced


def _skeleton(root, placeholders):
    """`root` with every jump node replaced by its branch placeholder --
    and every `%` node by `a - q * b`, which is what a fixed quotient
    leaves of it.

    Memoised BY NODE IDENTITY, because `postorder` visits each reachable
    identity once: a subgraph two consumers share stays ONE node with one
    branch, which is the sharing ADR-080 introduced surviving into the
    plan for free.
    """
    replaced = {}
    for node in postorder([root]):
        if node in placeholders:
            if node.op == '%':
                left = replaced.get(node.children[0], node.children[0])
                right = replaced.get(node.children[1], node.children[1])
                replaced[node] = ExpressionNode('binop', '-', (
                    left, ExpressionNode('binop', '*',
                                         (placeholders[node], right))))
            else:
                replaced[node] = placeholders[node]
        elif node.children:
            children = tuple(replaced.get(child, child)
                             for child in node.children)
            if children != node.children:
                replaced[node] = ExpressionNode(
                    node.kind, node.op, children, node.text)
    return _Rewritten(replaced.get(root, root), replaced)


def _argument_graph(node, replaced):
    """`node`'s LEVEL QUANTITY -- the continuous quantity whose surfaces
    it crosses -- with the jump nodes INSIDE it already replaced."""
    parts = [replaced.get(child, child) for child in node.children]
    if node.kind == 'call':
        return parts[0]
    if node.op == '%':
        return ExpressionNode('binop', '/', (parts[0], parts[1]))
    return ExpressionNode('binop', '-', (parts[0], parts[1]))


def _affine_in_sources(root):
    """Whether `root` is AFFINE in the sources along the path, so its
    crossings can be solved rather than searched.

    Structural and computed once: numbers, source names, branch
    placeholders (constants on a piece), unary minus, `+` and `-` of
    affine operands, `*` with a constant operand and `/` by one. A call,
    a power, or a product of two moving operands is not affine, and
    falls to the search -- correct but slower, which is why
    `floor(max(x, 0))` is searched although it is piecewise affine.
    """
    degree = {}
    for node in postorder([root]):
        degree[node] = _degree_of(node, degree)
    return degree[root] in ('constant', 'affine')


def _degree_of(node, degree):
    if node.kind == 'num':
        return 'constant'
    if node.kind == 'name':
        # A branch placeholder is a constant on the piece being cut; a
        # source name is what moves along the path.
        return 'constant' if node.text.startswith('$') else 'affine'
    if not node.children:
        return None
    children = [degree[child] for child in node.children]
    if all(child == 'constant' for child in children):
        return 'constant'
    if node.kind == 'unary':
        return children[0] if children[0] == 'affine' else None
    if node.kind != 'binop':
        return None
    left, right = children
    moving = ('constant', 'affine')
    if node.op in ('+', '-'):
        return 'affine' if left in moving and right in moving else None
    if node.op == '*':
        if (left == 'constant' and right in moving) \
                or (right == 'constant' and left in moving):
            return 'affine'
        return None
    if node.op == '/':
        return 'affine' if right == 'constant' and left in moving else None
    return None


def _only_jumps(root):
    """Whether the law's CONTINUOUS SKELETON -- every jump node reduced
    to what a FIXED BRANCH leaves of it -- has no free coordinate left.

    `floor(turns)` reduces to a constant and is refused;
    `9 * enabled + floor(turns)` keeps `enabled` and is not, because
    `enabled` still carries slope.

    Four of the five primitives reduce to a constant, so the node and
    the whole argument subtree beneath it go. `%` does not: its branch
    is the integer QUOTIENT, and with that fixed `a % b` reads
    `a - q * b`, which still carries `a`'s slope. Reducing it to a
    constant would refuse `angle % 360` -- the tooth window written with
    the operator instead of the `floor`, which design.md section 6
    requires to read the same at every tick as the `floor` spelling
    does, and which moves by far more than jumping.
    """
    constant = ExpressionNode('num', text='0')
    replaced = {}
    for node in postorder([root]):
        if _is_jump(node):
            if node.op == '%':
                left = replaced.get(node.children[0], node.children[0])
                right = replaced.get(node.children[1], node.children[1])
                replaced[node] = ExpressionNode('binop', '-', (
                    left, ExpressionNode('binop', '*', (constant, right))))
            else:
                replaced[node] = constant
        elif node.children:
            children = tuple(replaced.get(child, child)
                             for child in node.children)
            if children != node.children:
                replaced[node] = ExpressionNode(
                    node.kind, node.op, children, node.text)
    return not free_names(replaced.get(root, root))


def _wiring_edge(root, assembly, wiring, nodes):
    """A wiring as the forward-only identity edge it already is."""
    source = _slot_node(nodes, root, wiring.slot)
    target = _slot_node(nodes, root, wiring.target)
    factor = 1.0 if wiring.target.scale is None else wiring.target.scale
    return Edge('wiring', [source.key], [target.key],
                wiring.described(), type(assembly).__name__,
                factors=[factor], names=[source.name])


def _slot_node(nodes, root, slot):
    key = ('slot', id(slot))
    found = nodes.get(key)
    if found is None:
        from solid_node.node.qualified import DriverIdError

        try:
            name = driver_id(instance_path(slot.node, root), slot.name)
            qualified = True
        except DriverIdError:
            name = f'{type(slot.node).__name__}.{slot.name}'
            qualified = False
        found = nodes[key] = _Node(key, name, 'intermediate', qualified)
    return found


def _formula_edge(root, assembly, formula, nodes):
    """A derived coordinate as the LINEAR edge it is, in the direction
    the rest render resolved it -- or as a CHECK when its slot and every
    term were bound by others, which is the one place two inputs
    prescribing one rigid group can be caught."""
    slot = formula.slot_of(assembly)
    slot_node = _slot_node(nodes, root, slot)
    terms = formula.resolved_terms(assembly)
    term_nodes = [(_register(nodes, root, end), float(coefficient))
                  for end, coefficient in terms]
    constant = float(formula.resolved_constant(assembly))
    described = f"the derived coordinate '{formula.described()}' " \
                f'({formula.written})'

    if slot.binder is formula:
        return Edge('formula', [node.key for node, _ in term_nodes],
                    [slot_node.key], described, type(assembly).__name__,
                    factors=[factor for _, factor in term_nodes],
                    constant=constant, slot_key=slot_node.key)
    for (node, _factor), (end, _coefficient) in zip(term_nodes, terms):
        if end.slot is not None and end.slot.binder is formula:
            needs = [slot_node.key] + [other.key for other, _ in term_nodes
                                       if other is not node]
            factors = ([0.0] + [factor for other, factor in term_nodes
                                if other is not node])
            # The solved-for term's own coefficient travels with it, so
            # `_linear` can divide by it.
            needs.append(node.key)
            factors.append(next(factor for other, factor in term_nodes
                                if other is node))
            return Edge('formula', needs, [node.key], described,
                        type(assembly).__name__, factors=factors,
                        constant=constant, slot_key=slot_node.key)
    needs = [slot_node.key] + [node.key for node, _ in term_nodes]
    factors = [0.0] + [factor for _, factor in term_nodes]
    return Edge('check', needs, (), described, type(assembly).__name__,
                factors=factors, constant=constant, slot_key=slot_node.key)


def _reaching_the_bank(candidates, bank_keys):
    """The edges that matter: one determining a coordinate the run owns,
    one determining anything such an edge reads, and a CHECK over what
    those produce.

    A relation or wiring whose driven ends are all outside the bank and
    reach no bank coordinate -- a pulley driving a belt's plain port --
    is left to the ordinary enumeration, which recomputes it from the
    run-bound sources on every tick.
    """
    matters = set(bank_keys)
    kept = []
    changed = True
    while changed:
        changed = False
        for edge in candidates:
            if edge in kept:
                continue
            reached = (set(edge.needs) if edge.kind == 'check'
                       else set(edge.gives))
            if not (reached & matters):
                continue
            kept.append(edge)
            matters.update(edge.needs)
            matters.update(edge.gives)
            changed = True
    return kept


def _refuse_opaque(kept, bank_keys, nodes):
    """An edge reading a coordinate the run does not own and no kept edge
    computes is refused by name: a plain port the author's `simulate()`
    binds is a value stated imperatively, not a relation the run can
    integrate."""
    computed = {key for edge in kept for key in edge.gives}
    for edge in kept:
        for key in edge.needs:
            if key in bank_keys or key in computed:
                continue
            raise UnsupportedLaw(
                f'{edge.description}, stated by {edge.stated_by}: it is '
                f'sourced from {nodes[key].name}, which the running '
                f'simulation does not own and no relation computes -- a '
                f'plain port an author\'s simulate() binds. The run '
                f'integrates relations over drivers and joint '
                f'coordinates, so state that value as a relation, or give '
                f'the part a joint.')


def _ordered(kept, nodes):
    """The edges in an order where every edge's sources are determined
    before it runs: Kahn over the ends each edge determines.

    A coordinate no edge determines is resolved from the start -- it is
    an input, or it HOLDS -- so an edge waits only on the ends something
    else in the program moves.
    """
    determiner = {}
    for edge in kept:
        for key in edge.gives:
            determiner[key] = edge
    resolved = {key for key in nodes if key not in determiner}
    order = []
    remaining = list(kept)
    while remaining:
        ready = [edge for edge in remaining
                 if all(key in resolved for key in edge.needs)]
        if not ready:
            stuck = ', '.join(edge.description for edge in remaining)
            raise UnsupportedLaw(
                f'the relations {stuck} form a cycle the run cannot order: '
                f'each waits on a coordinate another determines. A running '
                f'program is acyclic, because the rest render solved every '
                f'relation in one direction.')
        for edge in ready:
            order.append(edge)
            remaining.remove(edge)
            resolved.update(edge.gives)
    return order

##############################################
# Publication helpers




def _agreement():
    """`run.py`'s `_TOLERANCE`, imported where it is read rather than at
    module scope: `run` imports THIS module."""
    from .run import _TOLERANCE

    return _TOLERANCE


def _placeholder_prefix(names):
    r"""`_j`, lengthened by a leading underscore for as long as some
    published id matches `<prefix>\d+` -- exactly as the bindings pass
    lengthens `_b`."""
    prefix = '_j'
    while any(re.fullmatch(re.escape(prefix) + r'\d+', name)
              for name in names):
        prefix = '_' + prefix
    return prefix


def _published_plan(plan, placeholders):
    if plan is None:
        return None
    return {
        'skeleton': _renamed(plan.skeleton, placeholders),
        'jumps': [{'name': placeholders[jump.placeholder],
                   'primitive': jump.primitive,
                   'level': _renamed(jump.argument, placeholders),
                   'affine': jump.affine}
                  for jump in plan.jumps],
    }


def _published_bound(bound):
    if bound is None or isinstance(bound, float):
        return bound
    return {'expression': bound}


def _renamed(graph, mapping):
    """`graph` with every branch placeholder replaced through `mapping`.

    The compiler names a placeholder `$j0` per plan, which is not a name
    in the published grammar at all; this is where it becomes one.
    """
    if graph is None:
        return None
    root = as_node(graph)
    replaced = {}
    for node in postorder([root]):
        if node.kind == 'name' and node.text in mapping:
            replaced[node] = ExpressionNode('name', text=mapping[node.text])
        elif node.children:
            children = tuple(replaced.get(child, child)
                             for child in node.children)
            if children != node.children:
                replaced[node] = ExpressionNode(
                    node.kind, node.op, children, node.text)
    return GraphValue(replaced.get(root, root))


##############################################
# What a producer takes from a running root


def owning_run(root):
    """The `Run` that currently owns `root`'s tree, or None."""
    return getattr(root.__dict__.get('_run_binder'), 'owner', None)


def release_tree(root):
    """Drop a previous run's ownership of `root`'s tree.

    ONE simulation owns a tree at a time and the NEWEST takes it: the
    run's claim on the root and on every joint coordinate it bound is
    dropped, so the rest render that follows finds a tree no run owns and
    poses it exactly as it would a tree no run ever touched. The released
    run refuses to advance afterwards (`Run._owns`), because its bank no
    longer describes the tree.
    """
    from solid_node.motion.ports import get_coordinate, run_owned

    root.__dict__.pop('_run_binder', None)
    for _identifier, (node, name) in qualified_coordinates(root).items():
        slot = get_coordinate(node, name)
        if run_owned(slot):
            slot._value = None
            slot.binder = None
            slot._enum_marker = None


def program_of(root):
    """The compiled program of a running root and its REST BANK, taken
    WITHOUT taking the tree over.

    A live run is the authority on both and is asked for them: it holds
    the program it compiled and the snapshot it took at construction, and
    a publication is a read that must leave no trace on it. With no run,
    one is constructed and released again -- the same construction, so
    the published program and identity are the run's by construction
    rather than by two implementations agreeing -- and every node's
    snapshot is put back and re-rendered, so a caller that held a posed
    tree still holds one.

    A root the run cannot be constructed over has no program to publish,
    and this raises exactly what `Sim` raises.
    """
    run = owning_run(root)
    if run is not None:
        return run.program, dict(run.initial.bank)
    from .sim import Sim

    snapshots = _snapshots(root)
    try:
        sim = Sim(root, 1.0)
        return sim.program, dict(sim.initial.bank)
    finally:
        release_tree(root)
        _restore(snapshots, root)


def _snapshots(root):
    from solid_node.node.assembly import _rest_children

    found = []

    def visit(node):
        if getattr(node, '_states', None) is None:
            return
        found.append((node, dict(node._states)))
        for child in _rest_children(node):
            visit(child)

    visit(root)
    return found


def _restore(snapshots, root):
    from solid_node.node.qualified import declared_drivers_of

    complete = True
    for node, states in snapshots:
        node._states.clear()
        node._states.update(states)
        if any(name not in states
               for name in declared_drivers_of(type(node))):
            complete = False
    if complete and getattr(root, '_states', None) is not None:
        # Re-render under the restored snapshot: an operation holds the
        # value its render computed, so nothing else would drop the
        # numbers the rest render just put there. A snapshot with holes
        # could not have been rendered before this either.
        root.render()
