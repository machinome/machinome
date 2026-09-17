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
import struct
from dataclasses import dataclass, replace

from solid2.core.object_base import OpenSCADConstant

from solid_node import math as motion_math
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

# The KINKS: the CONTINUOUS SELECTIONS of `SYMBOLIC_BUILTINS`. Each
# returns ONE OF ITS OPERANDS EXACTLY -- `abs(x)` is `x` or `-x`,
# `min(a, b)` and `max(a, b)` are `a` or `b`, bit for bit -- and is
# continuous where the operands meet, so a quantity built over them is
# PIECEWISE AFFINE wherever its operands are, and its pieces are solved
# rather than searched. They are not jumps: a kink RECORDS NOTHING, and
# its breakpoints only sub-divide a solve (design.md section 4.3).
# `clamp`, `clamp01`, `ramp` and `piecewise` are compositions of these.
_KINK_CALLS = ('abs', 'min', 'max')

# The shapes a followed quantity can have. `'kinked'` is the one this
# cycle adds, and it is INTERNAL: the published `affine` flag stays the
# two-valued statement the export spec defines, so a kinked quantity
# publishes `false`.
_MOVABLE = ('constant', 'affine', 'kinked')
_AFFINE = ('constant', 'affine')

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

# How far the far-side landing walks out from the segment's own
# arithmetic before it gives up, with the stride DOUBLING from one ulp:
# 200 doublings cover every distance a double can express, so this is the
# safety net and never the working number (a solved crossing is a couple
# of ulps out, a searched one up to `_CROSSING_TOLERANCE` of the piece's
# travel).
_WALK_STRIDES = 200

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


class LandingInvariantError(RuntimeError):
    """A self-read cut placed the driven coordinate nowhere.

    The landing is bracketed by stepping out from the segment's own
    arithmetic with the stride doubling from one ulp, and `_WALK_STRIDES`
    doublings cover every distance a double can express. A cut exists
    because the level crossed the surface, so the branch differs
    somewhere on either side of it and a bracket is found by
    construction. This is therefore a broken invariant of the run rather
    than a dt that is too coarse -- the `StopInvariantError` it is
    modelled on says the same of a stop -- and it is raised rather than
    committing a value the design says is never committed. The tick
    committed nothing.
    """


class MembershipInvariantError(RuntimeError):
    """The two readings of one tree disagreed about what a block holds.

    An INTERNAL invariant of the compile, not a model's mistake: the
    construction pre-pass decides which relations bind nothing at rest
    and the compile decides which are ordered per piece, and they agree
    by construction -- the pre-pass keeps only a cycle holding a banked
    driven end, and a block whose gives hold an intermediate is refused
    before this is reached. It is raised where a landing invariant is
    raised, and for the same reason: an impossible reading is reported
    rather than rendered. It happens at CONSTRUCTION, where there is no
    tick to commit or refuse, which is why it is its own kind.
    """


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

    __slots__ = ('primitive', 'placeholder', 'argument', 'shape', 'affine',
                 'kinks')

    def __init__(self, primitive, placeholder, argument, shape):
        self.primitive = primitive
        self.placeholder = placeholder
        self.argument = argument
        # The level quantity's SHAPE, which decides how its crossings are
        # located: solved from a piece's two ends when affine, solved on
        # each sub-interval between its kinks when kinked, sampled
        # otherwise.
        self.shape = shape
        # The TWO-VALUED statement the export spec defines and
        # `_published_plan` carries: a kinked level publishes `False`,
        # because a consumer that has not learned to cut at a kink must
        # go on searching it rather than interpolating THROUGH it.
        self.affine = shape in _AFFINE
        self.kinks = _KinkCuts(argument) if shape == 'kinked' else None

    def __repr__(self):
        return (f'<{self.primitive} jump on {self.argument} '
                f'{self.shape or "searched"}>')


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
                  crossings=None, tick=0, forced=None):
        """The CONTINUOUS part of this law's change over one tick.

        `forced` is the one thing a BLOCK adds: a map from a SELECTOR's
        placeholder to the branch the block read at that piece's
        midpoint. A forced node is a CONSTANT here -- its crossings were
        located by the block over the whole stretch and are not located
        again, and every reading of its branch is the number the block
        substituted -- so the order the block chose and the branch this
        member reads cannot disagree (design.md section 3).
        """
        if not any(delta.values()):
            # A zero-length path contributes zero without evaluating
            # anything -- and must never reach the sum below, where a
            # one-point piece would read as minus a jump.
            return 0.0
        paths = _LevelPaths(_moving_names(delta))
        cuts = self._partition(start, delta, described, coordinate,
                               crossings, tick, forced, paths)
        total = 0.0
        for left, right in zip(cuts, cuts[1:]):
            branches = self._branches(start, delta, (left + right) / 2.0,
                                      len(self.jumps), described, coordinate,
                                      forced, paths)
            total += (self._substituted(start, delta, right, branches)
                      - self._substituted(start, delta, left, branches))
        return total

    def _substituted(self, start, delta, t, branches):
        values = _along(start, delta, t)
        values.update(branches)
        return self.skeleton.evaluate(values)

    def _branches(self, start, delta, t, count, described, coordinate,
                  forced=None, paths=None):
        """Every jump node's branch at one point of the path, in
        postorder, so a node nested inside another's argument is
        determined first.

        A node the caller FORCED reads the branch it was given and its
        level is never evaluated: one of the two places a block's
        selector is read. This is a ONE-SHOT point -- every jump here is
        asked its branch exactly once for this `t` -- so `paths`, when
        given, still shares a jump's decided STRUCTURE with any other use
        of it in the same scope, but always binds.
        """
        values = _along(start, delta, t)
        found = {}
        piece = paths.new_piece() if paths is not None else None
        for jump in self.jumps[:count]:
            if forced is not None and jump.placeholder in forced:
                branch = forced[jump.placeholder]
            elif paths is not None:
                level = paths.value(jump, piece, values, described,
                                    coordinate)
                branch = _branch_of(jump, level)
            else:
                level = self._level(jump, values, described, coordinate)
                branch = _branch_of(jump, level)
            found[jump.placeholder] = branch
            values[jump.placeholder] = branch
        return found

    def _level(self, jump, values, described, coordinate):
        return _leveled(lambda: jump.argument.evaluate(values),
                        jump, described, coordinate)

    ##############################################
    # The partition

    def cuts(self, start, delta, described, coordinate, forced=None):
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
                                     None, 0, forced))

    def retained(self, own):
        """This plan read in TWO LAYERS, for a driven end whose own law
        reads it: the jump nodes that do not depend on `own` keep the
        partition below, and the ones that do are walked inside each of
        its pieces (`_Retained`)."""
        return _Retained(self, own)

    def _partition(self, start, delta, described, coordinate,
                   crossings, tick, forced=None, paths=None):
        """The tick's path, cut at every crossing of every jump surface.

        The jump nodes are taken in POSTORDER, so a node's level
        quantity is asked where it crosses only once every jump node
        inside it has already cut the path: on each pair of consecutive
        cuts those inner branches are constant, which is what makes the
        level quantity a continuous function of `t` there and the search
        below well-posed.

        `paths` is this call's own level path values (design.md section
        3.3): built here when a caller does not already hold one for a
        wider scope, one per jump, and re-bound every piece on `inner`.
        """
        if paths is None:
            paths = _LevelPaths(_moving_names(delta))
        cuts = [0.0, 1.0]
        located = []
        for index, jump in enumerate(self.jumps):
            if forced is not None and jump.placeholder in forced:
                # The block located this node's crossings over the WHOLE
                # stretch already, and its branch is a constant on this
                # piece: re-locating it here is the second reading this
                # design exists to remove.
                continue
            found = []
            for left, right in zip(cuts, cuts[1:]):
                inner = self._branches(start, delta, (left + right) / 2.0,
                                       index, described, coordinate, forced,
                                       paths)
                piece = paths.new_piece()
                found.extend(self._crossings_of(
                    jump, start, delta, inner, left, right,
                    described, coordinate, paths, piece))
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
                      described, coordinate, paths=None, piece=None):
        """Where `jump` reaches one of its surfaces between two cuts."""
        if jump.affine:
            return self._solved(jump, start, delta, inner, left, right,
                                described, coordinate, paths=paths,
                                piece=piece)
        if jump.shape == 'kinked':
            # A KINKED level is affine on each sub-interval between its
            # own kinks, so the piece is cut there -- recording nothing,
            # counting toward nothing -- and each sub-piece is solved.
            # The kink's own LEVEL is a DIFFERENT sub-graph (`_kink_level`
            # builds a fresh `a - b` node for `min`/`max`) and stays on
            # `GraphValue.evaluate` this cycle (design.md section 3.3).
            def at(t):
                values = _along(start, delta, t)
                values.update(inner)
                return values

            breaks = jump.kinks.between(at, left, right)
            if not breaks:
                # No kink is reached inside this piece, so the level IS
                # affine over the whole of it.
                return self._solved(jump, start, delta, inner, left, right,
                                    described, coordinate, paths=paths,
                                    piece=piece)
            edges = (left,) + breaks + (right,)
            found = []
            for index, (low_t, high_t) in enumerate(zip(edges, edges[1:])):
                # The right end is INCLUSIVE for every sub-piece but the
                # last, so a surface lying exactly on an interior
                # breakpoint is not lost between the two sub-pieces that
                # meet there; `_deduplicated` is what stops it being
                # taken twice, and it exists for exactly this. Every
                # sub-piece here still shares ONE `inner` (the SAME
                # branches, and so the SAME piece token): only the
                # kink's own level, left on `GraphValue.evaluate`,
                # distinguishes them.
                found.extend(self._solved(
                    jump, start, delta, inner, low_t, high_t, described,
                    coordinate, closed=index < len(edges) - 2, paths=paths,
                    piece=piece))
            return _deduplicated(found)
        return self._searched(jump, start, delta, inner, left, right,
                              described, coordinate, paths, piece)

    def _solved(self, jump, start, delta, inner, left, right,
                described, coordinate, closed=False, paths=None,
                piece=None):
        """An AFFINE stretch of the level quantity: determined everywhere
        on it by its two endpoint values, so every surface between them
        is SOLVED -- all of them, which is what makes a crank that passes
        three tooth windows in one tick add three throws rather than one.

        `closed` takes the stretch's RIGHT end inclusively, for a
        sub-piece another sub-piece continues from. The LEFT end is
        exclusive either way: at the piece's own left end that surface is
        not one the piece crosses, and at an interior breakpoint it was
        reached by the sub-piece before.
        """
        low = self._level_at(jump, start, delta, left, inner,
                             described, coordinate, paths, piece)
        high = self._level_at(jump, start, delta, right, inner,
                              described, coordinate, paths, piece)
        if high == low:
            return []
        found = []
        for level in _surfaces(jump, low, high, described, coordinate,
                               inclusive=closed):
            if closed and level == low:
                continue
            found.append((left + (right - left)
                          * (level - low) / (high - low), level))
        return found

    def _searched(self, jump, start, delta, inner, left, right,
                  described, coordinate, paths=None, piece=None):
        """Anything else: sampled, bracketed and bisected."""
        width = (right - left) / _SUBDIVISIONS
        points = [left + width * step for step in range(_SUBDIVISIONS)]
        points.append(right)
        levels = [self._level_at(jump, start, delta, where, inner,
                                 described, coordinate, paths, piece)
                 for where in points]
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
                        points[step + 1], described, coordinate, paths,
                        piece), level))
            if len(found) > _MAX_CROSSINGS:
                break
        return found

    def _bisect(self, jump, start, delta, inner, level, low, high,
                described, coordinate, paths=None, piece=None):
        below = self._level_at(jump, start, delta, low, inner,
                               described, coordinate, paths, piece) - level
        for _round in range(_BISECTION_ROUNDS):
            if high - low <= _CROSSING_TOLERANCE:
                break
            middle = (low + high) / 2.0
            here = self._level_at(jump, start, delta, middle, inner,
                                  described, coordinate, paths, piece) - level
            if here == 0.0 or (here < 0.0) != (below < 0.0):
                high = middle
            else:
                low, below = middle, here
        return (low + high) / 2.0

    def _level_at(self, jump, start, delta, t, inner, described, coordinate,
                  paths=None, piece=None):
        values = _along(start, delta, t)
        values.update(inner)
        if paths is None:
            return self._level(jump, values, described, coordinate)
        return paths.value(jump, piece, values, described, coordinate)


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


def _merged(cuts, found, end=1.0):
    """The partition with `found` folded in: two cuts closer than the
    tolerance are ONE, and the partition always ends at exactly `end` --
    1 for a tick's own partition, and the bracket's right end for the
    kink breakpoints located inside one piece of it."""
    ordered = sorted(list(cuts) + list(found))
    kept = [ordered[0]]
    for where in ordered[1:]:
        if where - kept[-1] > _CROSSING_TOLERANCE:
            kept.append(where)
    kept[-1] = end
    return kept


def _kink_level(node):
    """A kink node's LEVEL QUANTITY -- the continuous quantity whose one
    surface, at zero, is where the node changes which operand it
    returns: `x` for `abs(x)`, and `a - b` for `min(a, b)` and
    `max(a, b)`."""
    if node.op == 'abs':
        return node.children[0]
    return ExpressionNode('binop', '-', (node.children[0], node.children[1]))


class _KinkCuts:
    """Where a KINKED quantity's kinks cut a stretch of the tick's path.

    Compiled once, beside the classification that found them: the kink
    nodes in the graph's POSTORDER, each as the level quantity whose zero
    is its breakpoint. A kink nested inside another's level is therefore
    cut FIRST, and on each sub-interval the earlier kinks have already
    produced, the level that follows is AFFINE in the fraction -- so its
    zero is ONE DIVISION, exactly as `JumpPlan._crossings_of` solves an
    affine level. No sampling, no bisection, no further tolerance.

    A breakpoint is NOT a crossing (design.md section 4.3): the quantity
    is continuous there, so it is recorded nowhere, enters no partition
    an increment is summed over, lands no coordinate on a far side and
    counts toward no maximum. It exists only inside a SOLVE.
    """

    __slots__ = ('levels',)

    def __init__(self, graph):
        root = as_node(graph)
        self.levels = tuple(GraphValue(_kink_level(node))
                            for node in postorder([root])
                            if node.kind == 'call'
                            and node.op in _KINK_CALLS)

    def __bool__(self):
        return bool(self.levels)

    def __repr__(self):
        return f'<{len(self.levels)} kinks>'

    def between(self, at, left, right):
        """The breakpoints STRICTLY INSIDE `[left, right]`, sorted and
        merged, where `at(t)` gives the values the levels read at `t`."""
        cuts = [left, right]
        for level in self.levels:
            found = []
            for low_t, high_t in zip(cuts, cuts[1:]):
                low = level.evaluate(at(low_t))
                high = level.evaluate(at(high_t))
                if high == low or not math.isfinite(low) \
                        or not math.isfinite(high):
                    # A level that does not MOVE over a sub-interval
                    # reaches nothing inside it, which is the same
                    # statement `_Walk._searched` makes of a jump level.
                    continue
                if not min(low, high) < 0.0 < max(low, high):
                    continue
                where = low_t + (high_t - low_t) * (0.0 - low) / (high - low)
                if low_t < where < high_t:
                    found.append(where)
            if found:
                cuts = _merged(cuts, found, right)
        return tuple(cuts[1:-1])


##############################################
# Only what moves along a tick's path is evaluated

# The same operator objects `GraphValue.evaluate` computes with -- reused
# here rather than restated, so a standing or moving node is the
# identical arithmetic either evaluator takes it through.
_PATH_OPERATORS = {'+': operator.add, '-': operator.sub, '*': operator.mul,
                   '/': operator.truediv, '%': math.fmod, '^': operator.pow,
                   '<': operator.lt, '<=': operator.le, '>': operator.gt,
                   '>=': operator.ge, '==': operator.eq, '!=': operator.ne}


def _path_node_value(node, values, computed, standing=None):
    """One node's value, read the same way `GraphValue.evaluate` reads
    it: a child already computed on THIS walk is taken from `computed`,
    and one this walk never visits -- because it stands -- is taken from
    `standing`, the piece's own bound value for it. Same operators, same
    dispatch, so the float is the one the whole-graph walk gives."""
    if node.kind == 'num':
        return float(node.text)
    if node.kind == 'name':
        if node.text not in values:
            raise ValueError(f'Unresolved motion input {node.text[:80]!r}')
        return float(values[node.text])
    args = []
    for child in node.children:
        args.append(computed[child] if child in computed else standing[child])
    if node.kind == 'binop':
        return _PATH_OPERATORS[node.op](*args)
    if node.kind == 'unary':
        return -args[0] if node.op == '-' else +args[0]
    if node.kind == 'call' and node.op in SYMBOLIC_BUILTINS:
        return getattr(motion_math, node.op)(*args)
    raise ValueError(f'Cannot numerically resolve {node!r}')


def _visited(count):
    """One `_PathValue.at` charges `count` node visits and reports them
    here -- the seam `tests.base.graph_node_visits` patches, because a
    bound path's fast walk never calls `postorder` and so is invisible to
    a probe that only counts postorder steps."""


class _PathValue:
    """One compiled graph followed along ONE tick's path.

    Built where the path is known, from the names the tick MOVES. Every
    node none of whose sources move is a constant of the path -- computed
    ONCE, from the piece's own inputs, in `bind` -- and read back at every
    later point of that piece; only the nodes that move are evaluated per
    point, in `at`. The arithmetic is unchanged, node for node and
    operator for operator, so a node's value is the SAME FLOAT whether it
    is computed once or many times.

    Structure -- which nodes move -- is decided ONCE, in the walk `bind`
    makes for the piece's own first point: the same postorder walk
    `GraphValue.evaluate` would have made anyway, so deciding it costs a
    boolean per node and nothing else. Standing VALUES are re-bound every
    piece, because a branch placeholder is a constant only there; `bind`
    is called once per piece and `at` for every later point of it. No
    cache outlives the object, and the object itself never outlives the
    tick that built it.
    """

    __slots__ = ('root', 'moving', 'order', 'standing')

    def __init__(self, graph, moving):
        self.root = as_node(graph)
        self.moving = frozenset(moving)
        self.order = None       # decided on the first `bind`; a tuple of
                                # the nodes that MOVE, in postorder.
        self.standing = {}      # this piece's non-moving node values.

    def bind(self, values):
        """A new piece: recompute the standing part under `values` --
        this piece's own branches included -- deciding, the first time
        ever, which nodes move in the very same walk. Returns the root's
        value at `values`, exactly what `GraphValue.evaluate` would have
        returned for this point."""
        computed = {}
        standing = {}
        deciding = self.order is None
        moves = {} if deciding else None
        order = [] if deciding else None
        known = None if deciding else frozenset(self.order)
        for node in postorder([self.root]):
            computed[node] = _path_node_value(node, values, computed)
            if deciding:
                if node.kind == 'name':
                    node_moves = node.text in self.moving
                else:
                    node_moves = any(moves[child] for child in node.children)
                moves[node] = node_moves
                if node_moves:
                    order.append(node)
                else:
                    standing[node] = computed[node]
            elif node not in known:
                standing[node] = computed[node]
        if deciding:
            self.order = tuple(order)
        self.standing = standing
        return computed[self.root]

    def at(self, values):
        """A later point of the SAME piece: walk only the nodes that
        move, in the same postorder `bind` decided, reading a standing
        child back from the value this piece bound. A graph with no
        moving node at all returns its standing root without walking."""
        if not self.order:
            _visited(0)
            return self.standing[self.root]
        computed = {}
        standing = self.standing
        for node in self.order:
            computed[node] = _path_node_value(node, values, computed, standing)
        _visited(len(self.order))
        return computed[self.root]


def _leveled(compute, jump, described, coordinate):
    """`JumpPlan._level`'s refusal rules, over any way of computing the
    raw level -- a plain graph evaluation or a bound path's point --
    unchanged either way: a division by zero refuses the tick, and an
    integer-branch primitive refuses a level that is not a finite
    number."""
    try:
        level = compute()
    except ZeroDivisionError:
        raise _no_level(jump, described, coordinate) from None
    if jump.primitive in ('floor', 'ceil', '%') \
            and not math.isfinite(level):
        raise _no_level(jump, described, coordinate,
                        'a level quantity that is not a finite number')
    return level


def _moving_names(delta):
    """The names a tick's path MOVES: a source whose increment is
    non-zero -- the run's own statement, never inferred."""
    return frozenset(name for name, value in delta.items() if value)


class _LevelPaths:
    """One jump plan's LEVEL path values, over one caller's own scope --
    an `increment`/`cuts` call, or the outer layer of one self-read walk.

    A jump's path value is built on its first use here and kept for the
    rest of that scope; its structure is therefore decided once even
    though the plan itself is compiled once and reused over many ticks --
    this object is not. Its standing part is re-bound whenever the piece
    identifying it changes underneath it.

    A piece is identified by a token from `new_piece`, a monotonic
    counter -- NEVER a transient dict's `id()`. A piece dict such as
    `inner` or `branches` is typically unreferenced the moment its scope
    moves to the next piece, and CPython is then free to hand an
    UNRELATED later dict the exact same address: keying a piece by
    `id()` let a stale standing value from an earlier, already-freed
    piece answer for a later one that happened to reuse its memory --
    the actual bug this class was rewritten to close (evidence.md,
    task 6.1's first red run against `Clearing`).
    """

    __slots__ = ('moving', 'paths', 'bound', 'counter')

    def __init__(self, moving):
        self.moving = frozenset(moving)
        self.paths = {}
        self.bound = {}
        self.counter = 0

    def new_piece(self):
        """A fresh token, never reused for the life of this object."""
        self.counter += 1
        return self.counter

    def value(self, jump, piece, values, described, coordinate):
        path = self.paths.get(jump.placeholder)
        if path is None:
            path = _PathValue(jump.argument, self.moving)
            self.paths[jump.placeholder] = path
        bind = self.bound.get(jump.placeholder) != piece
        if bind:
            self.bound[jump.placeholder] = piece
        return _leveled(lambda: path.bind(values) if bind else path.at(values),
                        jump, described, coordinate)


def _dependence(plan, own):
    """Which of a plan's jump nodes DEPEND on the driven coordinate.

    A node depends on it when that coordinate is among the free names of
    the node's ARGUMENT SUBTREE in the original graph. Read off the plan,
    where every inner jump is already a placeholder, that is: the node's
    level quantity names the driven id, OR it names the placeholder of a
    node that depends on it -- the same set, because a placeholder stands
    for exactly the subtree it replaced.

    Dependence is therefore UPWARD CLOSED along the nesting, which is
    what makes the independent nodes a well formed plan of their own.
    """
    found = {}
    for jump in plan.jumps:
        names = free_names(as_node(jump.argument))
        found[jump.placeholder] = (own in names
                                   or any(found.get(name, False)
                                          for name in names))
    return found


def _on_surface(jump, level):
    """Whether a jump node's level sits EXACTLY on one of its surfaces.

    Asked only at a piece's LEFT END under a self-read, where the value
    is the coordinate's own retained one and the question is which
    branch the piece begins under -- never of a midpoint, which is a
    point genuinely inside its piece.
    """
    if jump.primitive == 'sign' or jump.primitive in _COMPARISONS:
        return level == 0.0
    if not math.isfinite(level):
        return False
    if jump.primitive == '%' and level == 0.0:
        # `%` is continuous where `a / b` crosses zero, so zero is not
        # one of its surfaces.
        return False
    return level == math.floor(level)


def _ordinal(value):
    """A float as the integer its bits order by, so two floats can be
    bisected in FLOAT space: adjacent floats differ by one here, at any
    magnitude, with no tolerance anywhere."""
    whole = struct.unpack('<q', struct.pack('<d', value))[0]
    return whole if whole >= 0 else -(2 ** 63) - whole


def _from_ordinal(whole):
    if whole < 0:
        whole = -(2 ** 63) - whole
    return struct.unpack('<d', struct.pack('<q', whole))[0]


def _chattering(described, coordinate, jump):
    return UnsupportedLaw(
        f'{described}: {coordinate} stands exactly on a surface of its '
        f'{jump.primitive} and each branch carries the level back across '
        f'it -- a sliding mode, not a mechanism. The framework integrates '
        f'a law piece by piece, and there is no piece here to integrate. '
        f'The tick committed nothing: the bank, the tick count and the '
        f'tree stand as they were.')


class _Retained:
    """How ONE driven end whose own law READS it is integrated.

    The split is decided HERE, once, at compile time: the plan's jump
    nodes that do NOT depend on the driven coordinate keep ADR-107's
    whole partition -- built by `_partition` itself, over a plan of
    exactly that subset -- and the ones that DO are WALKED inside each of
    its pieces, their branches read at the piece's LEFT END from the
    value the coordinate RETAINS there.

    A midpoint is no use to a dependent node: the coordinate's value
    there is a consequence of the branch being asked for. The retained
    value is the one value known without assuming the answer, and it is
    the mechanism's own reading -- a rack meets the tooth the wheel is
    standing on.
    """

    __slots__ = ('plan', 'own', 'dependent', 'outer', 'shape', 'kinks')

    def __init__(self, plan, own):
        dependence = _dependence(plan, own)
        self.plan = plan
        self.own = own
        self.dependent = tuple(jump for jump in plan.jumps
                               if dependence[jump.placeholder])
        self.outer = JumpPlan(plan.skeleton,
                              [jump for jump in plan.jumps
                               if not dependence[jump.placeholder]])
        # The SKELETON's shape along the path, which is what decides
        # whether the driven coordinate's OWN path is affine in `t` on a
        # piece -- and so whether a dependent level's crossing is SOLVED
        # or searched. A KINKED skeleton is affine between its own
        # breakpoints, so the piece is cut there first and `own_at` is
        # affine inside each sub-piece.
        self.shape = _shape_of(as_node(plan.skeleton))
        self.kinks = _KinkCuts(plan.skeleton) if self.shape == 'kinked' \
            else None

    def __repr__(self):
        return (f'<retained reading of {self.own}: '
                f'{len(self.dependent)} dependent, '
                f'{len(self.outer.jumps)} independent>')

    def increment(self, start, delta, described, coordinate,
                  crossings=None, tick=0, forced=None):
        """`(increment, landing)`: what this end MOVES BY over the tick,
        and the ABSOLUTE value it holds at the tick's end where at least
        one cut placed it -- None where none did."""
        walk = _Walk(self, start, delta, described, coordinate, forced)
        increment, landing, _cuts = walk.run(crossings, tick)
        return increment, landing

    def cuts(self, start, delta, described, coordinate, forced=None):
        """The breakpoints the two layers together put on the path, the
        SKELETON's own kinks included: between two of them the driven
        coordinate's value is affine in `t`, which is what lets a stop on
        it be solved piece by piece rather than searched."""
        walk = _Walk(self, start, delta, described, coordinate, forced)
        return walk.run(None, 0, cutting=True)[2]


class _Walk:
    """One driven end's piece-by-piece walk over one tick."""

    __slots__ = ('reading', 'plan', 'own', 'start', 'delta', 'described',
                 'coordinate', 'taken', 'forced', '_skeleton_path',
                 '_skeleton_bound', '_level_paths', '_level_bound',
                 '_outer_paths', '_live_branches')

    def __init__(self, reading, start, delta, described, coordinate,
                 forced=None):
        self.reading = reading
        self.plan = reading.plan
        self.own = reading.own
        self.start = start
        self.delta = dict(delta)
        # The driven coordinate's own source moves by NOTHING along the
        # path: what it holds on a piece is what the pieces before it
        # produced, never an increment the tick handed it.
        self.delta[self.own] = 0.0
        self.described = described
        self.coordinate = coordinate
        # A SELECTOR's level reads no coordinate the block determines --
        # the driven end included -- so a forced node is always an
        # INDEPENDENT one in `_Retained`'s split, and forcing reaches the
        # whole walk through layer one alone.
        self.forced = forced
        self.taken = 0
        # Only what moves along this WALK's path is evaluated
        # (design.md section 3.3): the skeleton and each dependent jump's
        # level get ONE path value each, built here and re-bound per
        # piece on `branches`; the outer layer's own jump levels share
        # ONE `_LevelPaths` for the whole walk, re-bound per piece on
        # `inner`. None of this outlives the walk.
        moving = _moving_names(self.delta)
        self._skeleton_path = _PathValue(self.plan.skeleton, moving)
        self._skeleton_bound = None
        self._level_paths = {jump.placeholder:
                             _PathValue(jump.argument, moving | {self.own})
                             for jump in reading.dependent}
        self._level_bound = {}
        self._outer_paths = _LevelPaths(moving)
        # `_skeleton`/`_level` key a piece by `id(branches)`. That is
        # only safe as long as no two DIFFERENT `branches` dicts built
        # during this walk can ever share an address -- which CPython
        # would happily do the moment an earlier one is garbage
        # collected (`_tentative`'s own docstring; the bug this walk was
        # fixed for, evidence.md task 6.1). Keeping every `branches`
        # dict this walk ever builds alive here, for the walk's whole
        # life, is what makes that safe.
        self._live_branches = []

    ##############################################
    # The two layers

    def run(self, crossings, tick, cutting=False):
        own0 = self.start[self.own]
        if not any(value for name, value in self.delta.items()
                   if name != self.own):
            # A tick in which no SOURCE moves contributes zero without
            # evaluating the law, exactly as any other law's does.
            return 0.0, None, (0.0, 1.0)
        outer = self._outer(crossings, tick)
        own_left = own0
        landed = False
        cuts = [0.0]
        for left, right in zip(outer, outer[1:]):
            outer_branches = self._outer_branches(left, right)
            t = left
            while True:
                branches = self._decide(t, right, own_left, outer_branches)
                base = self._skeleton(t, branches)

                def own_at(s, branches=branches, base=base,
                           own_left=own_left):
                    """The driven coordinate's own path on this piece --
                    one ordinary evaluation, because the substituted
                    skeleton does not name it.

                    The skeleton's CHANGE is taken first. Left to right,
                    `(own_left + S) - base` rounds whenever `|S|` is
                    comparable to `|own_left|`, so a piece whose skeleton
                    does not move would still shift the coordinate by an
                    ulp; taken this way an unchanged skeleton adds a true
                    zero and the coordinate keeps the exact float it
                    held."""
                    return own_left + (self._skeleton(s, branches) - base)

                cut = self._first_cut(t, right, own_left, branches, own_at)
                if cutting and self.reading.kinks:
                    # The SKELETON's own kinks, inside the piece this
                    # branch reading holds over: between two of them the
                    # driven coordinate's value is affine in `t`. Asked
                    # only when the caller WANTS the cuts -- a stop being
                    # localized -- so an ordinary tick pays nothing for
                    # them.
                    cuts.extend(self._skeleton_cuts(
                        t, right if cut is None else cut[0], branches))
                if cut is None:
                    own_left = own_at(right)
                    break
                where, crossed = cut
                own_star = own_at(where)
                self.taken += 1
                if self.taken > _MAX_CROSSINGS:
                    raise _too_many(self.described, self.coordinate,
                                    crossed[0][1], self.taken)
                own_left = self._land(crossed, where, own_left, own_star,
                                      branches)
                landed = True
                if crossings is not None:
                    crossings.extend(
                        Crossing(tick, self.described, self.coordinate,
                                 jump.primitive, level, where)
                        for level, jump in crossed)
                cuts.append(where)
                t = where
            cuts.append(right)
        return own_left - own0, (own_left if landed else None), tuple(cuts)

    def _outer(self, crossings, tick):
        """Layer one: ADR-107's own partition, over the jump nodes that
        do not depend on the driven coordinate."""
        if not self.reading.outer.jumps:
            return (0.0, 1.0)
        return self.reading.outer._partition(
            self.start, self.delta, self.described, self.coordinate,
            crossings, tick, self.forced, self._outer_paths)

    def _outer_branches(self, left, right):
        if not self.reading.outer.jumps:
            return {}
        return self.reading.outer._branches(
            self.start, self.delta, (left + right) / 2.0,
            len(self.reading.outer.jumps), self.described, self.coordinate,
            self.forced, self._outer_paths)

    ##############################################
    # The branches at a piece's LEFT END

    def _decide(self, t, right, own_left, outer_branches):
        """Every dependent node's branch at the piece's left end, in the
        graph's postorder, with the driven coordinate at its RETAINED
        value and every other source at `t`.

        A node whose level sits exactly on a surface takes the branch its
        OPERATOR gives; if the level then LEAVES the surface into the
        other branch's region, it is flipped there -- a zero-length
        piece -- and every branch is decided again. A node flipped twice
        is a sliding mode and refuses the tick.
        """
        forced = {}
        for _attempt in range(2 * len(self.reading.dependent) + 1):
            branches, sitting = self._tentative(t, own_left, outer_branches,
                                                forced)
            flip = None
            for jump in self.reading.dependent:
                if jump.placeholder not in sitting:
                    continue
                surface = sitting[jump.placeholder]
                probe = self._probe(jump, surface, t, right, own_left,
                                    branches)
                if probe is None:
                    continue
                # The branch of the region the level leaves the surface
                # INTO -- the one immediately on that side -- and never
                # the branch at the probe itself. A `floor` whose level
                # departs downward from `k` enters `(k - 1, k)` whatever
                # the sample that showed it moving reached, and a piece
                # is integrated under the branch at its own LEFT END: on
                # a gate that changes the rate rather than holding the
                # part, that sample is several surfaces away and its
                # branch is not this piece's.
                wanted = _branch_of(jump, math.nextafter(surface, probe))
                if wanted != branches[jump.placeholder]:
                    flip = (jump, wanted)
                    break
            if flip is None:
                return branches
            jump, wanted = flip
            if jump.placeholder in forced:
                raise _chattering(self.described, self.coordinate, jump)
            forced[jump.placeholder] = wanted
        raise _chattering(self.described, self.coordinate,
                          self.reading.dependent[0])

    def _tentative(self, t, own_left, outer_branches, forced):
        branches = dict(outer_branches)
        # Kept alive for the rest of the walk (see `__init__`): its
        # `id()` is this piece's key, and that key must never be handed
        # to a later, unrelated dict.
        self._live_branches.append(branches)
        sitting = {}
        for jump in self.reading.dependent:
            level = self._level(jump, t, own_left, branches)
            if _on_surface(jump, level):
                sitting[jump.placeholder] = level
            branches[jump.placeholder] = forced.get(
                jump.placeholder, _branch_of(jump, level))
        return branches, sitting

    def _probe(self, jump, surface, t, right, own_left, branches):
        """The level's value at the FIRST point of the piece at which it
        differs from the surface it sits on -- an inequality between two
        evaluated floats, with no tolerance in it."""
        base = self._skeleton(t, branches)
        for step in range(1, _SUBDIVISIONS + 1):
            s = t + (right - t) * step / _SUBDIVISIONS
            own = own_left + (self._skeleton(s, branches) - base)
            level = self._level(jump, s, own, branches)
            if level != surface:
                return level
        return None

    ##############################################
    # The FIRST surface strictly inside the piece

    def _first_cut(self, t, right, own_left, branches, own_at):
        found = []
        for jump in self.reading.dependent:
            crossing = self._crossing(jump, t, right, own_left, branches,
                                      own_at)
            if crossing is not None:
                found.append((crossing[0], crossing[1], jump))
        if not found:
            return None
        first = min(where for where, _level, _jump in found)
        # Two dependent nodes crossing at one fraction are ONE cut, and
        # each takes its far side.
        crossed = [(level, jump) for where, level, jump in found
                   if where - first <= _CROSSING_TOLERANCE]
        return first, crossed

    def _crossing(self, jump, t, right, own_left, branches, own_at):
        if jump.affine and self.reading.shape in _AFFINE:
            return self._solved(jump, t, right, own_left, own_at(right),
                                branches)
        if jump.shape is None or self.reading.shape is None:
            return self._searched(jump, t, right, own_left, branches, own_at)
        # At least one of the two is KINKED and neither is curved, so the
        # piece is SOLVED on sub-intervals. The SKELETON's breakpoints
        # come first, because they are what make the driven coordinate's
        # own path `own_at` affine at all; the LEVEL's ride `own_at`, so
        # they are located INSIDE each skeleton sub-piece, with `own_at`
        # evaluated at that sub-piece's two ends (design.md 4.4 (b)).
        outer = (t,) + self._skeleton_cuts(t, right, branches) + (right,)
        for index, (left, stop) in enumerate(zip(outer, outer[1:])):
            own_low = own_left if left == t else own_at(left)
            own_high = own_at(stop)
            inner = (left,) + self._level_cuts(
                jump, left, stop, own_low, own_high, branches) + (stop,)
            for step, (low_t, high_t) in enumerate(zip(inner, inner[1:])):
                # Left to right, and the FIRST surface strictly inside
                # the PIECE wins -- `_first_cut`'s own rule. The right
                # end is inclusive for every sub-piece but the last, and
                # the left end is exclusive throughout, which is
                # `_searched`'s "the surface a piece STARTS on is not one
                # it crosses".
                found = self._solved(
                    jump, low_t, high_t,
                    own_low if low_t == left else own_at(low_t),
                    own_high if high_t == stop else own_at(high_t),
                    branches,
                    closed=not (index == len(outer) - 2
                                and step == len(inner) - 2))
                if found is not None:
                    return found
        return None

    def _solved(self, jump, left, right, own_low, own_high, branches,
                closed=False):
        """The first surface of `jump` an AFFINE stretch reaches, solved
        from the stretch's two endpoint values."""
        low = self._level(jump, left, own_low, branches)
        high = self._level(jump, right, own_high, branches)
        if high == low:
            # A level that does not MOVE crosses nothing.
            return None
        found = [level for level
                 in _surfaces(jump, low, high, self.described,
                              self.coordinate, inclusive=closed)
                 if not (closed and level == low)]
        if not found:
            return None
        return min(((left + (right - left) * (level - low) / (high - low),
                     level) for level in found),
                   key=lambda entry: entry[0])

    def _skeleton_cuts(self, left, right, branches):
        """The SKELETON's kink breakpoints strictly inside `[left,
        right]`, under this piece's branch reading."""
        if not self.reading.kinks:
            return ()

        def at(t):
            values = _along(self.start, self.delta, t)
            values.update(branches)
            return values

        return self.reading.kinks.between(at, left, right)

    def _level_cuts(self, jump, left, right, own_low, own_high, branches):
        """A KINKED level's own breakpoints inside ONE skeleton
        sub-piece, where the driven coordinate's path is affine and so
        reads by interpolation between its two ends."""
        if jump.kinks is None:
            return ()
        span = right - left

        def at(t):
            values = _along(self.start, self.delta, t)
            values[self.own] = (own_low if span == 0.0 else
                                own_low + (own_high - own_low)
                                * (t - left) / span)
            values.update(branches)
            return values

        return jump.kinks.between(at, left, right)

    def _searched(self, jump, t, right, own_left, branches, own_at):
        """A level that is not affine along the path: sampled, bracketed
        and bisected on the same three tolerances a jump search already
        uses, and stopped at the FIRST surface it reaches."""
        width = (right - t) / _SUBDIVISIONS
        previous = self._level(jump, t, own_left, branches)
        for step in range(1, _SUBDIVISIONS + 1):
            s = t + width * step
            level = self._level(jump, s, own_at(s), branches)
            if level == previous:
                # A level that does not MOVE crosses nothing. Worth
                # saying here and nowhere else: a dependent node whose
                # branch holds the driven coordinate still sits exactly
                # on the surface it was landed at for the whole piece,
                # and an inclusive search would report that surface as
                # reached over and over.
                continue
            found = [surface for surface
                     in _surfaces(jump, previous, level, self.described,
                                  self.coordinate, inclusive=True)
                     # The surface a sub-interval STARTS on is not one it
                     # crosses. At the piece's left end that surface is
                     # `_decide`'s to answer, and at an interior sample
                     # it was reached in the sub-interval before and
                     # reported there -- the far-side landing leaves the
                     # coordinate reading the far branch, so a level that
                     # walks on from a surface it was placed at is
                     # LEAVING it.
                     if surface != previous]
            # `_surfaces` counts upward, so the surface the path reaches
            # FIRST is the one nearest the sample it starts from:
            # `found[0]` is the LAST one a DESCENDING level crosses, and
            # cutting there would integrate everything before it under a
            # branch the path had already left.
            for surface in sorted(found,
                                  key=lambda one: abs(one - previous)):
                if level == surface:
                    # A sample that IS on the surface is the crossing,
                    # at that sample; there is nothing to bisect toward.
                    where = s
                else:
                    where = self._bisect(jump, surface, previous, s - width,
                                         s, branches, own_at)
                # Every crossing strictly inside the piece is returned,
                # one a hair from its left end included: folding that one
                # away would integrate the piece under the near-side
                # branch and drive the part through its gap, which
                # design.md section 3's rule (d) forbids and the solved
                # path never does. It is not rule (c)'s case either --
                # a dial a hair SHORT of its surface, where a rest
                # default or a restore leaves one, is not ON it, so
                # `_decide` has nothing to flip.
                if where > t:
                    return where, surface
            previous = level
        return None

    def _bisect(self, jump, level, below, low, high, branches, own_at):
        """The bracket `[low, high]` narrowed onto `level`.

        `below` is the level at `low`, and `_searched` has already
        excluded a surface EQUAL to it, so the sign test below brackets
        something: a `below` of zero would put every round in the `else`
        arm and collapse the answer onto `high`.
        """
        below = below - level
        for _round in range(_BISECTION_ROUNDS):
            if high - low <= _CROSSING_TOLERANCE:
                break
            middle = (low + high) / 2.0
            here = self._level(jump, middle, own_at(middle), branches) - level
            if here == 0.0 or (here < 0.0) != (below < 0.0):
                high = middle
            else:
                low, below = middle, here
        return (low + high) / 2.0

    ##############################################
    # The FAR-SIDE landing

    def _land(self, crossed, where, own_left, own_star, branches):
        """After a cut the driven coordinate is placed at the nearest
        representable value on the FAR side of the surface.

        ADR-108's "committed AT its bound exactly", transposed to a
        surface that is not stated in the coordinate's own units: the
        segment's arithmetic finds the landing, and the landing is then
        walked to the adjacent float. Where the piece did NOT move the
        coordinate there is nothing to walk -- the level crossed by the
        sources' motion while the gate held, and the coordinate stands
        where it stood.
        """
        if own_star == own_left:
            return own_star
        direction = math.copysign(1.0, own_star - own_left)
        landing = own_star
        for _level, jump in crossed:
            landing = self._far_side(jump, where, landing, direction,
                                     branches)
        return landing

    def _far_side(self, jump, where, own_star, direction, branches):
        near = branches[jump.placeholder]

        def branch_at(value):
            return _branch_of(jump, self._level(jump, where, value, branches))

        return far_side_of(
            branch_at, near, own_star, direction,
            lambda: _unlanded(self.described, self.coordinate, jump))

    ##############################################
    # Evaluation

    def _skeleton(self, t, branches):
        """Only what moves along this walk's path is evaluated
        (design.md section 3): the skeleton's structure is decided once,
        on this piece's first point, and every later point of the SAME
        piece -- the same `branches` dict, by identity -- walks only the
        nodes that move."""
        values = _along(self.start, self.delta, t)
        values.update(branches)
        key = id(branches)
        if self._skeleton_bound != key:
            self._skeleton_bound = key
            return self._skeleton_path.bind(values)
        return self._skeleton_path.at(values)

    def _level(self, jump, t, own_value, branches):
        """The same mechanism for a DEPENDENT jump's level: the driven
        coordinate is MOVING here (design.md section 3.2) -- it is handed
        its own value at every point -- so it is in the path value's
        moving names, added explicitly in `__init__` because `self.delta`
        deliberately zeroes it."""
        values = _along(self.start, self.delta, t)
        values[self.own] = own_value
        values.update(branches)
        path = self._level_paths[jump.placeholder]
        key = id(branches)
        bind = self._level_bound.get(jump.placeholder) != key
        if bind:
            self._level_bound[jump.placeholder] = key
        return _leveled(lambda: path.bind(values) if bind else path.at(values),
                        jump, self.described, self.coordinate)


def far_side_of(branch_at, near, own_star, direction, unlanded):
    """The nearest representable value on the FAR side of a surface.

    `branch_at(value)` reads the jump node's branch at one value of the
    quantity being landed; `near` is the branch on the side the value
    came from; `direction` is the sign of its travel; `unlanded` builds
    the invariant error for a bracket that cannot be found.

    Membership of a value in the far side is decided by EVALUATING the
    branch there, never by comparing the value to the surface: a solved
    value at which the branch has already changed IS the landing, a
    strict comparison against a representable threshold lands on the
    next value beyond it, and a non-strict one lands on the threshold
    itself. The bisection runs in FLOAT ORDINAL space, so adjacent
    floats differ by one at any magnitude and no tolerance is involved.

    Extracted from `_Walk._far_side`, which still calls it, so the
    clocked event solver lands a request path by the SAME walk rather
    than a second one (OpenSpec change ``declare-the-state``).
    """
    step = math.ulp(own_star) if own_star else 5e-324
    if branch_at(own_star) != near:
        # The segment's arithmetic already landed PAST the surface,
        # which it does about as often as it lands short, so the
        # bracket is sought in both directions.
        far, inside = own_star, None
        for power in range(_WALK_STRIDES):
            candidate = own_star - direction * step * (2 ** power)
            if branch_at(candidate) == near:
                inside = candidate
                break
        if inside is None:
            # Unreachable by construction, and loud rather than
            # silent because of it: the cut exists because the level
            # crossed this surface, so the branch differs somewhere
            # on either side of it, and 200 doublings of a ulp cover
            # every distance a double expresses. No test can reach
            # this; committing `own_star` instead would commit a
            # value the design says is never committed.
            raise unlanded()
    else:
        inside, far = own_star, None
        for power in range(_WALK_STRIDES):
            candidate = own_star + direction * step * (2 ** power)
            if branch_at(candidate) != near:
                far = candidate
                break
        if far is None:
            raise unlanded()
    low, high = _ordinal(inside), _ordinal(far)
    while abs(high - low) > 1:
        middle = (low + high) // 2
        if branch_at(_from_ordinal(middle)) == near:
            low = middle
        else:
            high = middle
    return _from_ordinal(high)


def _too_many(described, coordinate, jump, count):
    failure = TooManyCrossings(
        f'{described}: over one tick {coordinate} would cross {count} '
        f"surfaces of {jump.primitive}, more than the {_MAX_CROSSINGS} a "
        f'single law is admitted in one tick. A dt that coarse is not '
        f'resolving the mechanism: the crossings between the frames are '
        f'what a jump law is FOR. Step in smaller ticks. The tick '
        f'committed nothing: the bank, the tick count and the tree stand '
        f'as they were.')
    # The count travels on the error as well as in its message, so a
    # caller that states the same judgement in its OWN words -- the
    # clocked solver's request refusal -- says the number this raise
    # reached rather than guessing one.
    failure.count = count
    return failure


def _unlanded(described, coordinate, jump):
    return LandingInvariantError(
        f'{described}: {coordinate} was cut at a surface of '
        f'{jump.primitive} and no value within {_WALK_STRIDES} doublings '
        f'of a ulp of the segment\'s own arithmetic reads the other '
        f'branch, so the cut placed the coordinate nowhere. The level '
        f'crossed that surface, so this is a broken invariant of the run '
        f'rather than a dt that is too coarse. The tick committed '
        f'nothing: the bank, the tick count and the tree stand as they '
        f'were.')


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
# A selection: blocks, selectors, switched sources


# The jump primitives whose ZERO BRANCH is held over an INTERVAL of the
# level quantity, and which can therefore make a source SWITCHED: `floor`
# over `[0, 1)`, `ceil` over `(-1, 0]`, a remainder's quotient over
# `(-1, 1)` and a comparison over the whole of its false side. `sign` is
# the one that does NOT qualify -- `_branch_of` returns `0.0` for it only
# where the level is EXACTLY zero, one point and not an interval -- so a
# `sign`-gated source is never switched, and a cycle whose only gate is a
# `sign` is refused at construction rather than at the first tick
# (design.md section 2).
_FOLDABLE = ('floor', 'ceil', '%') + tuple(_COMPARISONS)


def _folded(root, substitution):
    """`root` with every placeholder in `substitution` replaced by the
    number it stands for, and the arithmetic then folded:
    `x*0 -> 0`, `0*x -> 0`, `0/x -> 0`, `0+y -> y`, `y+0 -> y`,
    `y-0 -> y`, `0-y -> -y`.

    Monotone in the set of names sent to ZERO: every rule either removes
    names or keeps exactly the names its operand had, and a call's reads
    are the union of its arguments', so zeroing one more placeholder can
    never ADD a read. That is what makes ONE all-zero fold the minimum
    over every selector assignment (design.md section 2).
    """
    replaced = {}

    def is_zero(node):
        return node.kind == 'num' and float(node.text) == 0.0

    for node in postorder([root]):
        if node.kind == 'name' and node.text in substitution:
            replaced[node] = ExpressionNode(
                'num', text=repr(float(substitution[node.text])))
            continue
        if not node.children:
            continue
        children = tuple(replaced.get(child, child) for child in node.children)
        if node.kind == 'binop' and node.op == '*' and any(map(is_zero,
                                                               children)):
            replaced[node] = _ZERO
        elif node.kind == 'binop' and node.op == '/' and is_zero(children[0]):
            replaced[node] = _ZERO
        elif node.kind == 'binop' and node.op == '+' and is_zero(children[0]):
            replaced[node] = children[1]
        elif node.kind == 'binop' and node.op in ('+', '-') \
                and is_zero(children[1]):
            replaced[node] = children[0]
        elif node.kind == 'binop' and node.op == '-' and is_zero(children[0]):
            replaced[node] = ExpressionNode('unary', '-', (children[1],))
        elif children != node.children:
            replaced[node] = ExpressionNode(node.kind, node.op, children,
                                            node.text)
    return replaced.get(root, root)


_ZERO = ExpressionNode('num', text='0')


def _reads_under(plan, substitution):
    """Every coordinate a law still READS with `substitution`'s
    placeholders holding the branches it names: the folded skeleton's
    free names, with every surviving placeholder followed into its own
    folded level quantity, transitively."""
    by_name = {jump.placeholder: jump for jump in plan.jumps}
    pending = list(free_names(_folded(as_node(plan.skeleton), substitution)))
    seen, found = set(), set()
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        seen.add(name)
        jump = by_name.get(name)
        if jump is None:
            found.add(name)
            continue
        pending.extend(free_names(
            _folded(as_node(jump.argument), substitution)))
    return found


def _selectors(plan, determined):
    """A plan's SELECTORS: the jump nodes whose LEVEL QUANTITY reads no
    coordinate in `determined` -- a placeholder standing in that level
    resolved into the jump it replaced, transitively.

    Upward closed along the nesting for `_dependence`'s own reason: a
    placeholder stands for exactly the subtree it replaced, so a node
    whose level names a non-selector placeholder is itself not one. The
    plan's jumps are in the graph's POSTORDER, so an inner node is
    decided before the node it sits in.
    """
    reaches = {}
    found = []
    for jump in plan.jumps:
        names = free_names(as_node(jump.argument))
        touches = any(name in determined for name in names) or \
            any(reaches.get(name, False) for name in names)
        reaches[jump.placeholder] = touches
        if not touches:
            found.append(jump)
    return tuple(found)


class _Block:
    """A nontrivial strongly connected component of the program's
    dependency graph, and what a selection does to it.

    Its members are ORDINARY law edges; the block is what carries them
    through the program as ONE entry, so `_ordered` contracts the cycle
    and everything in `run.py` goes on meeting the program through the
    `Edge` interface it already calls.
    """

    __slots__ = ('members', 'gives', 'names', 'selectors', 'plans',
                 'unconditional', 'switched')

    def __init__(self, members, nodes):
        self.members = tuple(members)
        self.gives = tuple(member.gives[0] for member in self.members)
        self.names = tuple(nodes[key].name for key in self.gives)
        determined = frozenset(self.names)
        by_name = {name: key for name, key in zip(self.names, self.gives)}
        selectors, plans, unconditional, switched = [], [], [], []
        for member in self.members:
            plan = member.plans[0] if member.plans else None
            if plan is None:
                # A law with no jump in it carries no selector at all, so
                # everything it reads in the block is unconditional.
                selectors.append(())
                plans.append(None)
                own = member.gives[0]
                unconditional.append(frozenset(
                    key for key in member.needs
                    if key in self.gives and key != own))
                switched.append(frozenset())
                continue
            own = member.gives[0]
            found = _selectors(plan, determined)
            selectors.append(found)
            plans.append(JumpPlan(plan.skeleton, found))
            zero = {jump.placeholder: 0.0 for jump in found
                    if jump.primitive in _FOLDABLE}
            # A read of the member's OWN driven end is ADR-121's
            # self-read, not a wait on anything else, and is excluded
            # from both sets exactly as `_ordered` excludes it.
            whole = frozenset(by_name[name] for name in _reads_under(plan, {})
                              if name in by_name) - {own}
            least = frozenset(by_name[name] for name
                              in _reads_under(plan, zero)
                              if name in by_name) - {own}
            unconditional.append(least)
            switched.append(whole - least)
        self.selectors = tuple(selectors)
        self.plans = tuple(plans)
        self.unconditional = tuple(unconditional)
        self.switched = tuple(switched)

    def __repr__(self):
        return f'<block of {", ".join(self.names)}>'

    ##############################################
    # Construction

    def unconditional_cycle(self):
        """The members whose UNCONDITIONAL dependencies still form a
        cycle, or `()`.

        Present on every piece, so it is refused at construction with the
        message a plain cycle of two ordinary laws has always had.
        """
        remaining = list(range(len(self.members)))
        resolved = set()
        while remaining:
            ready = [index for index in remaining
                     if all(key in resolved
                            for key in self.unconditional[index]
                            if key != self.gives[index])]
            if not ready:
                return tuple(self.members[index] for index in remaining)
            for index in ready:
                resolved.add(self.gives[index])
            remaining = [index for index in remaining if index not in ready]
        return ()

    ##############################################
    # The tick

    def increments(self, values, deltas, crossings, tick, landings):
        """The block's contribution to each of its coordinates over one
        stretch: the selectors located FIRST, and then the members run
        PIECE BY PIECE in the order each piece's own selection gives
        (design.md section 3)."""
        starts, steps = [], []
        for member in self.members:
            starts.append({name: values[key] for name, key
                           in zip(member.names, member.needs)})
            steps.append({name: deltas[key] for name, key
                          in zip(member.names, member.needs)})
        located = None if crossings is None else []
        cuts = self._partition(starts, steps, located, tick)
        advanced = {key: values[key] for key in self.gives}
        total = {key: 0.0 for key in self.gives}
        landed = set()
        orders = {}
        for left, right in zip(cuts, cuts[1:]):
            forced = self._forced(starts, steps, (left + right) / 2.0)
            vector = tuple(tuple(sorted(entry.items())) for entry in forced)
            order = orders.get(vector)
            if order is None:
                order = orders[vector] = self._order(forced, left, right)
            held = dict(advanced)
            piece = {}
            for index in order:
                member = self.members[index]
                own = self.gives[index]
                start, delta = {}, {}
                for name, key in zip(member.names, member.needs):
                    if key in held:
                        start[name] = held[key]
                        delta[name] = piece.get(key, 0.0)
                    else:
                        start[name] = values[key] + deltas[key] * left
                        delta[name] = deltas[key] * (right - left)
                found = None if located is None else []
                increment, landing = _integrated(
                    member, start, delta, found, tick, forced[index])
                piece[own] = increment
                total[own] += increment
                if landing is None:
                    advanced[own] = advanced[own] + increment
                else:
                    advanced[own] = landing
                    landed.add(own)
                if found:
                    width = right - left
                    located.extend(replace(entry, t=left + entry.t * width)
                                   for entry in found)
        if located:
            # In the order the path meets them, as ADR-107's own
            # partition reports a law's: a selector's crossing is
            # located over the whole stretch and a member's own is
            # rescaled out of its piece, and the listing must not depend
            # on which of the two was computed first.
            located.sort(key=lambda entry: entry.t)
            crossings.extend(located)
        if landings is not None:
            for key in landed:
                # What the block reports is the ABSOLUTE value it has
                # advanced the coordinate to by the stretch's END -- the
                # landing plus every later piece's increment -- because
                # `Run._landed` commits a reported landing absolutely and
                # would otherwise discard the motion after it.
                landings[key] = advanced[key]
        return [(key, total[key]) for key in self.gives]

    def _partition(self, starts, steps, crossings, tick):
        """The stretch cut at every crossing of every selector of every
        member, in the members' own order and each member's postorder."""
        cuts = [0.0, 1.0]
        for index, plan in enumerate(self.plans):
            if plan is None or not plan.jumps:
                continue
            member = self.members[index]
            found = None if crossings is None else []
            located = plan._partition(starts[index], steps[index],
                                      member.description, member.driven[0],
                                      found, tick)
            if found:
                crossings.extend(found)
            if len(located) > 2:
                cuts = _merged(cuts, list(located[1:-1]))
        return cuts

    def _forced(self, starts, steps, where):
        """Every selector's branch, read at one point of the stretch."""
        found = []
        for index, plan in enumerate(self.plans):
            if plan is None or not plan.jumps:
                found.append({})
                continue
            member = self.members[index]
            found.append(plan._branches(
                starts[index], steps[index], where, len(plan.jumps),
                member.description, member.driven[0]))
        return found

    def _order(self, forced, left, right):
        """The members of this piece, ordered over the dependencies its
        own selection leaves ACTIVE."""
        active = []
        for index, member in enumerate(self.members):
            plan = member.plans[0] if member.plans else None
            if plan is None:
                active.append(self.unconditional[index])
                continue
            reads = _reads_under(plan, forced[index])
            active.append(frozenset(
                key for name, key in zip(self.names, self.gives)
                if name in reads))
        remaining = list(range(len(self.members)))
        resolved, order = set(), []
        while remaining:
            ready = [index for index in remaining
                     if all(key in resolved for key in active[index]
                            if key != self.gives[index])]
            if not ready:
                raise UnsupportedLaw(self._refused(remaining, forced,
                                                   left, right))
            for index in ready:
                order.append(index)
                resolved.add(self.gives[index])
            remaining = [index for index in remaining if index not in ready]
        return tuple(order)

    def _refused(self, remaining, forced, left, right):
        branches = []
        for index in remaining:
            for jump in self.selectors[index]:
                branches.append(f'{self.names[index]}: {jump.primitive} on '
                                f'{jump.argument} reads '
                                f'{forced[index][jump.placeholder]!r}')
        stuck = ', '.join(self.members[index].description
                          for index in remaining)
        return (f'over the piece [{left!r}, {right!r}] of this tick the '
                f'relations {stuck} form a cycle the run cannot order: each '
                f'waits on a coordinate another determines, and the '
                f'selection this piece was read under leaves every '
                f'dependency on this cycle active. The selectors read '
                f'{"; ".join(branches) or "nothing"}. The tick committed '
                f'nothing: the bank, the tick count and the tree stand as '
                f'they were.')

    def cuts(self, values, deltas, index):
        """The breakpoints a block puts on the path for one of its
        coordinates: the selector partition, with each member's own cuts
        inside each piece.

        `Run._locate` reaches this only through the AFFINE path, and a
        block's gives are never affine, so nothing calls it today. It is
        defined rather than left to raise because `_piecewise` is
        meaningful over it the day a later cycle classifies a block give
        as affine under a fixed branch vector.
        """
        starts, steps = [], []
        for member in self.members:
            starts.append({name: values[key] for name, key
                           in zip(member.names, member.needs)})
            steps.append({name: deltas[key] for name, key
                          in zip(member.names, member.needs)})
        return self._partition(starts, steps, None, 0)


def _integrated(member, start, delta, crossings, tick, forced):
    """One block member over one piece: `(increment, landing)`, by the
    machinery that already governs it -- ADR-107's partition and
    ADR-121's walk -- with its selectors FORCED."""
    plan = member.plans[0] if member.plans else None
    if plan is None:
        graph = member.graphs[0]
        end = {name: start[name] + delta[name] for name in start}
        return (_evaluated(graph, end) - _evaluated(graph, start)), None
    reading = member.retained[0] if member.retained else None
    if reading is None:
        return plan.increment(start, delta, member.description,
                              member.driven[0], crossings, tick,
                              forced), None
    return reading.increment(start, delta, member.description,
                             member.driven[0], crossings, tick, forced)


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
                 'stated_by', 'shapes', 'kinks', 'affine', 'retained',
                 'block')

    def __init__(self, kind, needs, gives, description, stated_by,
                 graphs=(), plans=(), driven=(), names=(), factors=(),
                 constant=0.0, slot_key=None, block=None):
        self.kind = kind
        # The `_Block` reading for a compound BLOCK edge, and `None` for
        # every other kind: a block is ONE entry of the program, so
        # `_ordered` contracts the cycle and `run.py` meets it through
        # the interface it already calls.
        self.block = block
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
        # One SHAPE per DRIVEN END, aligned with `gives`: how this edge's
        # value moves in its sources along the tick's path, so a stop on
        # that end is SOLVED (affine: one division; kinked: one division
        # per sub-interval between its kinks) or searched (`None`). A
        # wiring and a formula are linear by construction; a law is read
        # off its graph, or off its SKELETON where it carries a jump
        # plan, whose branch placeholders are constants on a piece.
        self.shapes = tuple(self._end_shapes())
        # The KINKS of a KINKED driven end -- of its SKELETON where it
        # carries a jump plan, of its whole graph where it does not --
        # compiled once, for `cuts` to sub-divide a stop's localization
        # at. `None` for every end that is not kinked.
        self.kinks = tuple(self._end_kinks())
        # The TWO-VALUED flag the export spec defines and
        # `_published_edge` carries unchanged: a KINKED end publishes
        # `False`, because a consumer that has not learned to cut at a
        # kink must go on searching it rather than interpolating THROUGH
        # it. The third value never leaves this runtime.
        self.affine = tuple(shape in _AFFINE for shape in self.shapes)
        # The driven ends this edge's own law READS -- the `gives` whose
        # id is also one of its `needs` -- each with the two-layer
        # reading of its plan, decided here at compile time. EMPTY for
        # every other edge, which is the one test `increments` makes
        # before taking ADR-107's path unchanged.
        self.retained = tuple(self._retained_ends())

    def _retained_ends(self):
        if self.kind != 'law' or not self.plans:
            return ()
        found = [None] * len(self.gives)
        reads = False
        for index, key in enumerate(self.gives):
            plan = self.plans[index]
            if plan is None or key not in self.needs:
                continue
            found[index] = plan.retained(self.driven[index])
            reads = True
        return tuple(found) if reads else ()

    def _end_kinks(self):
        for index, shape in enumerate(self.shapes):
            plan = self.plans[index] if self.plans else None
            if shape != 'kinked':
                yield None
            elif plan is not None:
                yield _KinkCuts(plan.skeleton)
            elif self.graphs[index] is None:
                yield None
            else:
                yield _KinkCuts(self.graphs[index])

    def _end_shapes(self):
        if self.kind == 'block':
            # A block's value is piecewise in the SELECTOR partition and
            # RE-ORDERED across it, so a stop on one of its coordinates
            # is searched, never solved.
            #
            # `cut-at-the-kink` does NOT lift this, and the reason is
            # that it is a different obstruction: a block has no single
            # expression at all until a branch vector is fixed, and the
            # ORDER its members run in may differ from piece to piece, so
            # classifying a give would mean classifying it per branch
            # vector AND proving the order stable on the piece -- ADR-122
            # territory, not a kink in an expression (design.md 7).
            return [None] * len(self.gives)
        if self.kind != 'law':
            return ['affine'] * len(self.gives)
        found = []
        for index, graph in enumerate(self.graphs):
            plan = self.plans[index] if self.plans else None
            if plan is not None:
                found.append(_shape_of(as_node(plan.skeleton)))
            elif graph is None:
                # A constant law has zero slope everywhere, which is
                # affine and moves nothing.
                found.append('constant')
            else:
                found.append(_shape_of(as_node(graph)))
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

    def increments(self, values, deltas, crossings=None, tick=0,
                   landings=None):
        """What this edge's targets MOVE BY over the tick.

        A law with no jump in it is the difference of two exact
        evaluations, which is what makes a kink exact -- and that is the
        FIRST thing tested here, so a continuous law pays nothing for
        the jump machinery. A law that jumps takes its plan, which cuts
        the tick at every crossing and sums the pieces.

        A law that READS the coordinate it drives is walked piece by
        piece instead, and REPORTS into `landings` the absolute value
        that end holds at the tick's end where at least one cut placed
        it: the run commits that float rather than `value + delta`,
        exactly where it commits a stop at its bound.
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
            retained = self.retained
            found = []
            for index, key in enumerate(self.gives):
                plan = self.plans[index]
                if plan is None:
                    graph = self.graphs[index]
                    found.append((key, _evaluated(graph, end)
                                  - _evaluated(graph, start)))
                    continue
                reading = retained[index] if retained else None
                if reading is None:
                    found.append((key, plan.increment(
                        start, delta, self.description, self.driven[index],
                        crossings, tick)))
                    continue
                increment, landing = reading.increment(
                    start, delta, self.description, self.driven[index],
                    crossings, tick)
                if landing is not None and landings is not None:
                    landings[key] = landing
                found.append((key, increment))
            return found
        if self.kind == 'block':
            return self.block.increments(values, deltas, crossings, tick,
                                         landings)
        if self.kind == 'wiring':
            return [(self.gives[0], deltas[self.needs[0]] * self.factors[0])]
        if self.kind == 'formula':
            return [(self.gives[0], self._linear(deltas, constant=0.0))]
        return []

    def cuts(self, values, deltas, index):
        """The breakpoints of the driven end at `index` along the tick's
        path, between which its value is affine in the fraction: the jump
        plan's own partition, and the KINKS of the law's skeleton.

        `()` where the end is affine over the whole tick -- no jump plan
        and no kink reached -- which is what keeps `Run._locate`'s
        one-division fast path exact.
        """
        if self.kind == 'block':
            return self.block.cuts(values, deltas, index)
        if self.kind != 'law':
            return ()
        plan = self.plans[index] if self.plans else None
        if plan is None and self.kinks[index] is None:
            return ()
        start = self._inputs(values)
        delta = {name: deltas[key]
                 for name, key in zip(self.names, self.needs)}
        if plan is None:
            # A law with NO jump node at all: its only breakpoints are
            # its own kinks, over the whole tick as one piece. Left
            # returning `()` here, `_locate` would divide straight
            # THROUGH the kink -- not a rounding error but a wrong stop.
            return self._kink_cuts(index, start, delta)
        reading = self.retained[index] if self.retained else None
        if reading is not None:
            # The walk unions the skeleton's kinks into its own cuts, in
            # the pieces its branch readings hold over.
            return reading.cuts(start, delta, self.description,
                                self.driven[index])
        cuts = plan.cuts(start, delta, self.description, self.driven[index])
        if self.shapes[index] != 'kinked':
            return cuts
        # The skeleton reads the plan's BRANCH PLACEHOLDERS, which are
        # constant only within ONE piece of the plan's partition, so its
        # kinks are located inside each piece with that piece's branches
        # substituted, and the per-piece lists are unioned with the
        # plan's own cuts.
        kinks = self.kinks[index]
        found = []
        for left, right in zip(cuts, cuts[1:]):
            branches = plan._branches(
                start, delta, (left + right) / 2.0, len(plan.jumps),
                self.description, self.driven[index])

            def at(t, branches=branches):
                along = _along(start, delta, t)
                along.update(branches)
                return along

            found.extend(kinks.between(at, left, right))
        return tuple(_merged(list(cuts), found)) if found else cuts

    def _kink_cuts(self, index, start, delta):
        """A plan-less KINKED law's breakpoints over the whole tick."""
        found = self.kinks[index].between(
            lambda t: _along(start, delta, t), 0.0, 1.0)
        return tuple(_merged([0.0, 1.0], found)) if found else ()

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

    def listed(self):
        """`self.edges` with every BLOCK expanded into its members,
        CONTIGUOUSLY and in the block's own deterministic order.

        The listing the identity, the placeholder minting and the
        published `edges` all walk, so the three cannot disagree about
        where a member sits. A program with no block returns exactly
        `self.edges`.
        """
        found = []
        for edge in self.edges:
            if edge.kind == 'block':
                found.extend(edge.block.members)
            else:
                found.append(edge)
        return found

    def described(self):
        """The canonical listing the identity is taken of, and what a
        message about the program prints.

        A BLOCK prints one `block` line naming its members' driven ids at
        the block's own position, and then each member's ORDINARY edge
        line contiguously: so the identity covers every member's ends,
        direction and expression exactly as it covers any other edge's,
        a program whose block membership changes has a different
        identity, and a program with NO block prints what it printed
        before, character for character.
        """
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
            if edge.kind == 'block':
                lines.append(
                    'block '
                    f'{[self.nodes[key].name for key in edge.gives]}')
                members = edge.block.members
            else:
                members = (edge,)
            for one in members:
                ends = (f'{[self.nodes[key].name for key in one.needs]} -> '
                        f'{[self.nodes[key].name for key in one.gives]}')
                if one.kind == 'law':
                    how = ' | '.join('constant' if graph is None
                                     else str(graph) for graph in one.graphs)
                elif one.kind == 'wiring':
                    how = f'identity * {one.factors[0]!r}'
                else:
                    how = (f'{list(one.factors)!r} + {one.constant!r} '
                           f'on {self.nodes[one.slot_key].name}')
                lines.append(f'{one.kind} {ends} {how} [{one.description}]')
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
                      for index, edge in enumerate(self.listed())],
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
        for edge in self.listed():
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
    marked = set()
    for assembly, path, records, formulas, wirings in _units(root):
        for record in records:
            edge = _relation_edge(root, assembly, record, nodes, bank_keys)
            if edge is not None:
                candidates.append(edge)
                if record.block_member:
                    marked.update(edge.gives)
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
    grouped, blocks = _blocked(kept, nodes, bank_keys)
    _agree_on_membership(marked, blocks, nodes)
    ordered = _ordered(grouped, nodes)
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
    owned = tuple(owned)
    if len(owned) > 1:
        raise ControlError(
            f"the control '{name}' names the joint '{control.selected}', "
            f"which owns {len(owned)} coordinates -- {', '.join(owned)}. A "
            f"control names ONE coordinate, and naming the joint a free "
            f"body floats on does not choose one of its six.")
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
    if not any(joint is mine for mine in declared.values()):
        known = ', '.join(declared) or 'none'
        raise ControlError(
            f"the control '{name}' names the coordinate "
            f"'{control.selected}', which is not a joint of "
            f"{type(node).__name__} '{node.name}'. A control's gesture is "
            f"a joint's motion; {type(node).__name__} declares: {known}.")
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

    # WHICH end a relation reads is decided ONCE, at class definition, by
    # declaration identity (`_self_read_index`), and recorded on the
    # relation: the rest rule and the non-running refusal both key on
    # that answer, and only that check refuses a driven GROUP. Reading it
    # back off the record here rather than re-deriving it from the
    # resolved slots keeps ONE definition of the self-read; what remains
    # is the consistency check between the two, kept as a BACKSTOP for
    # the invariant rather than as a path a running machine takes -- a
    # coordinate spelled two ways disagrees about the read, and the rest
    # render refuses that shape before the compile is reached.
    self_read = record.relation.self_read
    if self_read is None:
        read = []
        agrees = not any(source.key == node.key
                         for node in target_nodes
                         for source in source_nodes)
    else:
        read = [0]
        agrees = (record.direction == 'forward'
                  and len(target_nodes) == 1
                  and self_read < len(source_nodes)
                  and source_nodes[self_read].key == target_nodes[0].key)
    if not agrees:
        raise UnsupportedLaw(
            f'{record.described()}, stated by {type(assembly).__name__}: '
            f'the coordinate it drives is named TWO WAYS -- the child '
            f'standing for its one joint on one side and the coordinate '
            f'on the other -- so the class definition and the resolved '
            f'slots disagree about whether the law reads the end it '
            f'drives. Spell that coordinate the same way on both sides of '
            f'the relation.')
    for index in read:
        if not banked[index]:
            # A retained value is a HISTORY, and an intermediate keeps
            # none: the ordinary enumeration recomputes it absolutely
            # from the bank on every tick, so there is nothing for the
            # law to read back.
            raise UnsupportedLaw(
                f'{record.described()}, stated by {type(assembly).__name__}: '
                f'it reads {target_nodes[index].name}, the end it drives, '
                f'which the running simulation does not own. A retained '
                f'value is a history and only a coordinate the run owns '
                f'keeps one -- a plain port and a derived coordinate are '
                f'calculations the ordinary enumeration recomputes from the '
                f'bank on every tick. State the relation into the joint '
                f'coordinate and let the port follow it.')

    compiled = _law_graphs(assembly, record, source_nodes,
                           len(target_nodes))
    for index in read:
        graph, plan = compiled[index]
        skeleton = plan.skeleton if plan is not None else graph
        own = target_nodes[index].name
        if skeleton is not None and own in free_names(as_node(skeleton)):
            # The SKELETON is the law with every jump node replaced by
            # its branch. A read that survives it enters the law
            # CONTINUOUSLY, which makes the relation a differential
            # equation that the difference of two evaluations does not
            # define.
            raise UnsupportedLaw(
                f'{record.described()}, stated by {type(assembly).__name__}: '
                f'its law reads {own}, the coordinate it drives, '
                f'CONTINUOUSLY -- with every jump node replaced by its '
                f'branch the expression still names it, so the relation is '
                f'a differential equation rather than an increment, and '
                f'f(end) - f(start) does not define one. A read must pass '
                f'through a node that is PIECEWISE CONSTANT in it: floor, '
                f'ceil, sign or a comparison. A remainder alone is not one, '
                f'because a fixed quotient leaves a - q*b, which still '
                f'carries the coordinate\'s slope.')
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
    root, jumps = checked_expression(value, refuse)
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


def checked_expression(value, refuse, kind='a running law'):
    """`value`'s graph and its JUMP NODES, or the refusal naming what the
    framework cannot evaluate.

    The text-and-vocabulary walk, shared: raw text the framework cannot
    evaluate and a call outside the symbolic vocabulary are refused here
    for a running law and for a commit law alike, because the question
    "is this an expression over its sources" has one answer. What the
    two do with the jumps afterwards is where they differ -- a running
    law is planned and a commit law is evaluated at a point (OpenSpec
    change ``declare-the-state``, design section 7).
    """
    root = as_node(value)
    jumps = []
    for item in postorder([root]):
        if item.kind == 'raw':
            refuse(f'its expression carries the text {item.text!r}, which '
                   f'the framework cannot evaluate: {kind} is an '
                   f'expression over its sources.')
        if item.kind == 'call' and item.op not in SYMBOLIC_BUILTINS:
            refuse(f'its expression calls {item.op!r}, which is outside '
                   f'the symbolic vocabulary the framework can evaluate.')
        if _is_jump(item):
            jumps.append(item)
    return root, jumps


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
                             _shape_of(argument)))
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


def _shape_of(root):
    """`root`'s SHAPE in the sources along the path: `'constant'`,
    `'affine'`, `'kinked'` or `None`.

    Structural and computed once. Numbers, source names, branch
    placeholders (constants on a piece), unary minus, `+` and `-` of
    movable operands, `*` with a constant operand and `/` by one are
    AFFINE; a KINK -- `abs`, `min`, `max`, the continuous selections of
    `_KINK_CALLS` -- over movable operands is KINKED, and so is anything
    affine built over one. Anything else -- another call, a power, a
    product of two moving operands, a moving divisor -- is `None` and
    falls to the sampled search: correct, slower, and conservative,
    which is why `max(0, sin(x))` stays searched although one of its
    pieces is constant.

    An AFFINE quantity is solved from the two endpoint values of a
    piece; a KINKED one is solved on each sub-interval between its
    breakpoints (`_KinkCuts`), with no sampling and no new tolerance.
    """
    degree = {}
    for node in postorder([root]):
        degree[node] = _degree_of(node, degree)
    return degree[root]


def _joined(*parts):
    """An affine combination of movable operands is kinked exactly when
    one of them is."""
    return 'kinked' if 'kinked' in parts else 'affine'


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
    if node.kind == 'call':
        # A kink is the ONLY call that classifies, and it classifies by
        # its OPERANDS, never by its own node type: `max(0, sin(x))` is
        # a kink over a curved operand and stays unclassified.
        if node.op in _KINK_CALLS and all(child in _MOVABLE
                                          for child in children):
            return 'kinked'
        return None
    if node.kind == 'unary':
        return children[0] if children[0] in ('affine', 'kinked') else None
    if node.kind != 'binop':
        return None
    left, right = children
    moving = _MOVABLE
    if node.op in ('+', '-'):
        return _joined(left, right) if left in moving and right in moving \
            else None
    if node.op == '*':
        if left == 'constant' and right in moving:
            return _joined(right)
        if right == 'constant' and left in moving:
            return _joined(left)
        return None
    if node.op == '/':
        return _joined(left) if right == 'constant' and left in moving \
            else None
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


def _agree_on_membership(marked, blocks, nodes):
    """The PRE-PASS's membership and the COMPILE's, asserted equal.

    They agree BY CONSTRUCTION and not by luck: the pre-pass keeps only a
    cycle holding a BANKED driven end, `_reaching_the_bank` drops a
    candidate only when NO driven end reaches the bank, and a block whose
    gives hold an intermediate is refused above. The assertion is here
    because a disagreement would be an internal error rather than a
    model's mistake, and it names both sides.
    """
    compiled = {key for block in blocks for key in block.gives}
    if marked == compiled:
        return
    def listed(keys):
        return ', '.join(sorted(nodes[key].name for key in keys
                                if key in nodes)) or 'none'
    raise MembershipInvariantError(
        f'the construction pre-pass marked the relations determining '
        f'{listed(marked)} as members of a block and the compile found '
        f'{listed(compiled)}. The two readings of one tree must agree: the '
        f'pre-pass decides what binds nothing at rest and the compile '
        f'decides what is ordered per piece. Construction refused the '
        f'model.')


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


def _components(kept):
    """The strongly connected components of the program's DEPENDENCY
    GRAPH, in the candidates' own order: edge A precedes edge B when B
    reads a coordinate A determines, with a coordinate an edge itself
    determines EXCLUDED (that is the self-read, which is not a wait on
    anything else).

    Tarjan, iterative so a deep chain cannot exhaust the interpreter's
    stack, and with every adjacency list kept in the candidates' order so
    the components and their members come out the same for a given tree
    on every run and in every process.
    """
    determiner = {}
    for index, edge in enumerate(kept):
        for key in edge.gives:
            determiner[key] = index
    after = []
    for edge in kept:
        found = []
        for key in edge.needs:
            if key in edge.gives:
                continue
            source = determiner.get(key)
            if source is not None and source not in found:
                found.append(source)
        after.append(found)
    return _strongly_connected(after)


def _blocked(kept, nodes, bank_keys):
    """`kept` with every nontrivial strongly connected component
    contracted to ONE compound `block` edge, or the refusal that names
    what cannot be one.

    The program is acyclic again afterwards, which is what keeps every
    order, every document and every tick of a program with NO block
    exactly what it was.
    """
    components = _components(kept)
    blocks = []
    contracted = []
    taken = set()
    for component in components:
        if len(component) < 2:
            continue
        members = [kept[index] for index in component]
        _refuse_unselectable(members, bank_keys, nodes)
        block = _Block(members, nodes)
        stuck = block.unconditional_cycle()
        if stuck:
            raise UnsupportedLaw(_cycle_message(stuck))
        blocks.append((component[0], block))
        taken.update(component)
    if not blocks:
        return list(kept), ()
    made = {position: _block_edge(block) for position, block in blocks}
    for index, edge in enumerate(kept):
        if index in made:
            contracted.append(made[index])
        elif index not in taken:
            contracted.append(edge)
    return contracted, tuple(block for _position, block in blocks)


def _block_edge(block):
    """One block as the single `Edge` the program carries."""
    needs = []
    for member in block.members:
        for key in member.needs:
            if key not in needs:
                needs.append(key)
    return Edge('block', needs, block.gives,
                '; '.join(member.description for member in block.members),
                ', '.join(dict.fromkeys(member.stated_by
                                        for member in block.members)),
                driven=block.names, block=block)


def _refuse_unselectable(members, bank_keys, nodes):
    """What cannot be a block member, refused by relation identity."""
    for edge in members:
        if edge.kind in ('wiring', 'formula'):
            raise UnsupportedLaw(
                f'{edge.description}, stated by {edge.stated_by}: it is on a '
                f'dependency cycle -- '
                f'{", ".join(other.description for other in members)} -- and '
                f'it carries no jump node, so no selection can switch what '
                f'it reads. A cycle is admitted only where every dependency '
                f'inside it is gated by a jump node whose level reads no '
                f'coordinate the cycle determines. State the value as a '
                f'relation whose law carries the gate.')
    for edge in members:
        if len(edge.gives) != 1:
            raise UnsupportedLaw(
                f'{edge.description}, stated by {edge.stated_by}: it drives '
                f'a GROUP and it is on a dependency cycle -- '
                f'{", ".join(other.description for other in members)}. A '
                f'member of a block drives ONE coordinate, because what a '
                f'selection switches is decided per driven end off that '
                f"end's own expression, while a group's ends are claimed "
                f'and bound together. State each end as a relation of its '
                f'own.')
    for edge in members:
        if edge.gives[0] not in bank_keys:
            raise UnsupportedLaw(
                f'{edge.description}, stated by {edge.stated_by}: it drives '
                f'{nodes[edge.gives[0]].name}, which the running simulation '
                f'does not own, and it is on a dependency cycle -- '
                f'{", ".join(other.description for other in members)}. A '
                f'block advances its coordinates PIECE BY PIECE inside a '
                f'tick, and only a coordinate the run owns keeps that '
                f'history -- a plain port and a derived coordinate are '
                f'calculations the ordinary enumeration recomputes from the '
                f'bank on every tick. State the relation into the joint '
                f'coordinate and let the port follow it.')


def _cycle_message(stuck):
    """The refusal a cycle no selection breaks has always had, with one
    sentence saying what a switch would be."""
    return (f'the relations {", ".join(edge.description for edge in stuck)} '
            f'form a cycle the run cannot order: each waits on a coordinate '
            f'another determines. A running program is acyclic, because the '
            f'rest render solved every relation in one direction. A '
            f'dependency inside a cycle is admitted only where it is '
            f'SWITCHED: a source that folding a jump node to zero removes '
            f'from the law, where that node\'s level reads no coordinate '
            f'the cycle determines and its zero branch is one the node holds '
            f'over an INTERVAL of that level -- floor, ceil, a remainder or '
            f'a comparison, and not sign, whose zero is a single point.')


def _ordered(kept, nodes):
    """The edges in an order where every edge's sources are determined
    before it runs: Kahn over the ends each edge determines.

    A coordinate no edge determines is resolved from the start -- it is
    an input, or it HOLDS -- so an edge waits only on the ends something
    else in the program moves. A need an edge itself GIVES is a READ of
    what that coordinate HOLDS, not a wait on something else, so it is
    ignored here: the edge is ready as soon as everything ELSE it reads
    is.
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
                 if all(key in resolved or key in edge.gives
                        for key in edge.needs)]
        if not ready:
            # Unreachable once every strongly connected component is
            # contracted to one entry, and kept as the backstop for that
            # invariant rather than as a path a machine takes.
            raise UnsupportedLaw(_cycle_message(remaining))
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


def _block_members(root):
    """Mark every relation record of `root`'s linked tree that lies on a
    dependency CYCLE determining at least one coordinate the run BANKS.

    Run at `Sim` construction, BEFORE the rest render, because the rest
    render is what refuses such a cycle today -- `DoublyBound` where the
    driven ends carry rest guards and `UnreachedCoordinate` where they do
    not -- so a rule only the compile knows cannot save it (design.md
    section 5). The records exist with their ends resolved at that point;
    nothing here renders, binds or poses anything.

    The graph is built over RESOLVED DRIVEN SLOTS from EVERY relation
    record, EVERY wiring and EVERY derived coordinate, each taken FORWARD
    AS DECLARED -- which for a relation of several ends and for a wiring
    is the only direction it has. A wiring and a derived coordinate are
    in the graph so the cycle is SEEN; they carry no mark, because they
    bind nothing this rule could change and the compile is what refuses
    them. An SCC determining NO banked coordinate is left alone: the
    compile drops it before it orders anything, and marking it would make
    a legitimate model bind nothing at rest for a block that is never
    compiled.

    Idempotent: it recomputes membership from the records and rewrites
    every mark, so a second simulation over a shared tree decides afresh.
    """
    from solid_node.motion.ports import get_coordinate

    banked = {id(get_coordinate(node, name))
              for _identifier, (node, name)
              in qualified_coordinates(root).items()}
    units = []
    for assembly, _path, records, formulas, wirings in _units(root):
        for record in records:
            record.block_member = False
            units.append((record,
                          [_pre_key(root, end) for end in record.driver_ends],
                          [_pre_key(root, end) for end in record.driven_ends]))
        for wiring in wirings:
            units.append((None, [('slot', id(wiring.slot))],
                          [('slot', id(wiring.target))]))
        for formula in formulas:
            slot = formula.slot_of(assembly)
            units.append((None,
                          [_pre_key(root, end) for end, _coefficient
                           in formula.resolved_terms(assembly)],
                          [('slot', id(slot))]))
    determiner = {}
    for index, (_record, _sources, driven) in enumerate(units):
        for key in driven:
            determiner[key] = index
    after = []
    for _record, sources, driven in units:
        found = []
        for key in sources:
            if key in driven:
                continue
            source = determiner.get(key)
            if source is not None and source not in found:
                found.append(source)
        after.append(found)
    for component in _strongly_connected(after):
        if len(component) < 2:
            continue
        if not any(key[0] == 'input' or key[1] in banked
                   for index in component for key in units[index][2]):
            continue
        for index in component:
            record = units[index][0]
            if record is not None:
                record.block_member = True


def _pre_key(root, end):
    """One resolved end as the pre-pass addresses it: an input by its
    qualified id, anything else by its slot's identity."""
    if end.is_driver:
        return ('input', _qualified(root, end)[0])
    return ('slot', id(end.slot))


def _strongly_connected(after):
    """Tarjan over an adjacency list, iteratively, with the components
    and their members in the list's own order."""
    index_of, low, on_stack, stack = {}, {}, set(), []
    counter = [0]
    found = []
    for root in range(len(after)):
        if root in index_of:
            continue
        work = [(root, 0)]
        while work:
            node, step = work[-1]
            if step == 0:
                index_of[node] = low[node] = counter[0]
                counter[0] += 1
                stack.append(node)
                on_stack.add(node)
            if step < len(after[node]):
                work[-1] = (node, step + 1)
                child = after[node][step]
                if child not in index_of:
                    work.append((child, 0))
                elif child in on_stack:
                    low[node] = min(low[node], index_of[child])
                continue
            work.pop()
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[node])
            if low[node] == index_of[node]:
                component = []
                while True:
                    other = stack.pop()
                    on_stack.discard(other)
                    component.append(other)
                    if other == node:
                        break
                found.append(sorted(component))
    found.sort(key=lambda component: component[0])
    return found


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
    # The BLOCK MARKS are deliberately NOT dropped here. They are a pure
    # function of the tree's declared relations rather than run state,
    # and `program_of` releases a tree it is about to RE-RENDER for the
    # producer: clearing them would leave a block's relations unmarked
    # for that render, which would then refuse the model `DoublyBound`.
    # What keeps a stale mark harmless is `_step_relation`'s running-root
    # guard -- a marked record is solved, deferred and refused exactly as
    # it is today under any other time base -- and the pre-pass's own
    # idempotence, which rewrites every mark from the records on each
    # running construction.
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
