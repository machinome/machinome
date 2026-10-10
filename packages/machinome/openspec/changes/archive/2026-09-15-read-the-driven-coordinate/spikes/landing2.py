"""Spike 7: the FAR-SIDE LANDING, over the framework's own classes.

`snap.py` measured two candidate commit rules with hand-written
arithmetic and concluded that nothing should be snapped.  That
conclusion does not survive: the segment's own arithmetic leaves the
gate ENGAGED after a crossing often enough to drive a wheel straight
through its gap, and across ticks the run commits `value + delta`, where
`x + (y - x) != y` for about six pairs in a hundred.

This spike measures the rule the design now states instead, and it
measures it through `Sim`, `Run.integrate` and `Edge.increments` --
not through a re-implementation of the arithmetic:

    after a self-read cut the driven coordinate is placed at the
    representable float NEAREST the surface among those at which the
    crossing node's level reads the FAR-SIDE branch, and the run commits
    THAT float rather than `value + delta`.

The walk itself is prototyped here as a monkeypatch over
`Edge.increments`, because the framework refuses the declaration
outright; `Run.integrate` is wrapped so the landing it reports is what
the bank commits, which is the increments-protocol extension the design
asks for.  Everything else -- the class body, realization, the rest
render, the compile, the segment loop, the plan, the branch reading, the
crossing search -- is the framework's own.

Run from a directory holding a solid-node manifest:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=<worktree> \
        python landing2.py [trials] [combinations]
"""

import json
import math
import random
import struct
import sys
import time

from solid_node.motion import couplings

couplings._refuse_shared_coordinate = lambda a, b: None

_step = couplings._step_relation


def _is_self_read(record):
    driven = {id(end.slot) for end in record.driven_ends
              if end.slot is not None}
    return any(end.slot is not None and id(end.slot) in driven
               for end in record.driver_ends)


def _patched_step(record, claimed, bound):
    """The rest rule: a self-read relation binds NOTHING at rest and is
    recorded solved forward."""
    if _is_self_read(record):
        if record.direction is None:
            record.direction = 'forward'
            return True
        return False
    return _step(record, claimed, bound)


couplings._step_relation = _patched_step

from solid_node.simulation import program as P            # noqa: E402
from solid_node.simulation.program import (               # noqa: E402
    Crossing, Edge, JumpPlan, TooManyCrossings, UnsupportedLaw,
    _CROSSING_TOLERANCE, _MAX_CROSSINGS, _SUBDIVISIONS, _affine_in_sources,
    _along, _branch_of, _surfaces)
from solid_node.expression_graph import free_names        # noqa: E402
from solid_node.scad_expression import as_node            # noqa: E402

_ordered = P._ordered


def _ordered_patched(kept, nodes):
    """Kahn, ignoring a need an edge itself gives."""
    class _Shim:
        def __init__(self, edge):
            self.edge = edge
            self.needs = tuple(k for k in edge.needs if k not in edge.gives)
            self.gives = edge.gives
            self.description = edge.description
            self.kind = edge.kind

    shims = [_Shim(edge) for edge in kept]
    return [shim.edge for shim in _ordered(shims, nodes)]


P._ordered = _ordered_patched


##############################################
# The walk

LAND = True             # False reproduces the segment-arithmetic rule
LANDINGS = {}
STATS = {'cuts': 0, 'walk steps': 0, 'level evaluations': 0,
         'already far': 0, 'searched cuts': 0}


def _ordinal(x):
    i = struct.unpack('<q', struct.pack('<d', x))[0]
    return i if i >= 0 else -(2 ** 63) - i


def _from_ordinal(k):
    i = k if k >= 0 else -(2 ** 63) - k
    return struct.unpack('<d', struct.pack('<q', i))[0]


def _dependence(plan, own):
    """Which jump nodes DEPEND on the driven coordinate: their argument
    names it, or names the placeholder of a node that does. Equivalent
    to `own` being a free name of the node's argument subtree in the
    ORIGINAL graph."""
    found = {}
    for jump in plan.jumps:
        names = free_names(as_node(jump.argument))
        found[jump.placeholder] = (own in names
                                   or any(found.get(name, False)
                                          for name in names))
    return found


def _on_surface(jump, level):
    if jump.primitive == 'sign' or jump.primitive in ('<', '<=', '>', '>=',
                                                      '==', '!='):
        return level == 0.0
    if not math.isfinite(level):
        return False
    return level == math.floor(level) and not (jump.primitive == '%'
                                               and level == 0.0)


class _Walker:
    """One driven end's piece-by-piece walk over one tick."""

    def __init__(self, plan, start, delta, own, described, coordinate):
        self.plan = plan
        self.start = start
        self.own = own
        self.described = described
        self.coordinate = coordinate
        self.delta = dict(delta)
        self.delta[own] = 0.0
        dependence = _dependence(plan, own)
        self.dependent = [jump for jump in plan.jumps
                          if dependence[jump.placeholder]]
        self.independent = [jump for jump in plan.jumps
                            if not dependence[jump.placeholder]]
        self.outer_plan = JumpPlan(plan.skeleton, self.independent)
        self.skeleton_affine = _affine_in_sources(as_node(plan.skeleton))

    ##########################################
    # Evaluation helpers

    def _values(self, t, own_value, branches):
        values = _along(self.start, self.delta, t)
        values[self.own] = own_value
        values.update(branches)
        return values

    def _skeleton(self, t, branches):
        values = _along(self.start, self.delta, t)
        values.update(branches)
        return self.plan.skeleton.evaluate(values)

    def _level(self, jump, t, own_value, branches):
        STATS['level evaluations'] += 1
        return jump.argument.evaluate(self._values(t, own_value, branches))

    ##########################################
    # The walk

    def run(self, crossings, tick):
        moving = [value for name, value in self.delta.items()
                  if name != self.own]
        if not any(moving):
            return 0.0, None
        own0 = self.start[self.own]
        if self.independent:
            outer = self.outer_plan._partition(
                self.start, self.delta, self.described, self.coordinate,
                None, tick)
        else:
            outer = [0.0, 1.0]
        own_left = own0
        landed = False
        for left, right in zip(outer, outer[1:]):
            if self.independent:
                outer_branches = self.outer_plan._branches(
                    self.start, self.delta, (left + right) / 2.0,
                    len(self.independent), self.described, self.coordinate)
            else:
                outer_branches = {}
            t = left
            taken = 0
            while True:
                taken += 1
                if taken > _MAX_CROSSINGS:
                    raise TooManyCrossings(
                        f'{self.described}: {self.coordinate} crossed its '
                        f'own gate more than {_MAX_CROSSINGS} times.')
                branches = self._decide(t, right, own_left, outer_branches)
                base = self._skeleton(t, branches)

                def own_at(s, branches=branches, base=base,
                           own_left=own_left):
                    return own_left + self._skeleton(s, branches) - base

                cut = self._first_cut(t, right, own_left, branches, own_at)
                if cut is None:
                    own_left = own_at(right)
                    break
                where, crossed = cut
                own_star = own_at(where)
                STATS['cuts'] += 1
                own_left = self._land(crossed, where, own_left, own_star,
                                      branches)
                landed = True
                if crossings is not None:
                    for jump in crossed:
                        crossings.append(Crossing(
                            tick, self.described, self.coordinate,
                            jump.primitive, 0.0, where))
                t = where
        return own_left - own0, (own_left if landed and LAND else None)

    ##########################################
    # Rule (b)/(c): the branches at a piece's left end

    def _decide(self, t, right, own_left, outer_branches):
        """Every dependent node's branch at the piece's LEFT END, with
        the driven coordinate at its retained value and every source at
        `t`; a node sitting exactly on a surface takes the branch the
        operator gives, and is FLIPPED once if the level then leaves the
        surface into the other branch's region. A second flip of one
        node is a sliding mode and is refused."""
        forced = {}
        for _attempt in range(2 * len(self.dependent) + 1):
            branches, sitting = self._tentative(t, own_left, outer_branches,
                                                forced)
            flip = None
            for jump in self.dependent:
                if jump.placeholder not in sitting:
                    continue
                probe = self._probe(jump, sitting[jump.placeholder], t,
                                    right, own_left, branches)
                if probe is None:
                    continue
                wanted = _branch_of(jump, probe)
                if wanted != branches[jump.placeholder]:
                    flip = (jump, wanted)
                    break
            if flip is None:
                return branches
            jump, wanted = flip
            if jump.placeholder in forced:
                raise UnsupportedLaw(self._chattering(jump))
            forced[jump.placeholder] = wanted
        raise UnsupportedLaw(self._chattering(self.dependent[0]))

    def _tentative(self, t, own_left, outer_branches, forced):
        branches = dict(outer_branches)
        sitting = {}
        for jump in self.dependent:
            level = self._level(jump, t, own_left, branches)
            if _on_surface(jump, level):
                sitting[jump.placeholder] = level
            branches[jump.placeholder] = forced.get(
                jump.placeholder, _branch_of(jump, level))
        return branches, sitting

    def _chattering(self, jump):
        return (f'{self.described}: {self.coordinate} stands exactly on a '
                f'surface of its {jump.primitive} and each branch carries '
                f'the level back across it -- a sliding mode, not a '
                f'mechanism. The tick committed nothing.')

    def _probe(self, jump, surface, t, right, own_left, branches):
        """The level's value at the FIRST point of the piece where it
        differs from the surface it sits on."""
        base = self._skeleton(t, branches)
        for step in range(1, _SUBDIVISIONS + 1):
            s = t + (right - t) * step / _SUBDIVISIONS
            own = own_left + self._skeleton(s, branches) - base
            level = self._level(jump, s, own, branches)
            if level != surface:
                return level
        return None

    ##########################################
    # The first surface strictly inside the piece

    def _first_cut(self, t, right, own_left, branches, own_at):
        best = None
        for jump in self.dependent:
            where = self._crossing(jump, t, right, own_left, branches, own_at)
            if where is None:
                continue
            if best is None or where < best - _CROSSING_TOLERANCE:
                best = where
        if best is None:
            return None
        crossed = []
        for jump in self.dependent:
            where = self._crossing(jump, t, right, own_left, branches, own_at)
            if where is not None and abs(where - best) <= _CROSSING_TOLERANCE:
                crossed.append(jump)
        return best, crossed

    def _crossing(self, jump, t, right, own_left, branches, own_at):
        if jump.affine and self.skeleton_affine:
            low = self._level(jump, t, own_left, branches)
            high = self._level(jump, right, own_at(right), branches)
            if high == low:
                return None
            found = _surfaces(jump, low, high, self.described,
                              self.coordinate, inclusive=False)
            if not found:
                return None
            fractions = [t + (right - t) * (level - low) / (high - low)
                         for level in found]
            return min(fractions)
        STATS['searched cuts'] += 1
        width = (right - t) / _SUBDIVISIONS
        previous = self._level(jump, t, own_left, branches)
        for step in range(1, _SUBDIVISIONS + 1):
            s = t + width * step
            level = self._level(jump, s, own_at(s), branches)
            found = _surfaces(jump, previous, level, self.described,
                              self.coordinate, inclusive=True)
            if found:
                target = found[0]
                low, high = s - width, s
                for _round in range(64):
                    if high - low <= _CROSSING_TOLERANCE:
                        break
                    middle = (low + high) / 2.0
                    here = self._level(jump, middle, own_at(middle),
                                       branches) - target
                    if (here < 0.0) != (previous - target < 0.0):
                        high = middle
                    else:
                        low = middle
                where = (low + high) / 2.0
                if where > t + _CROSSING_TOLERANCE:
                    return where
            previous = level
        return None

    ##########################################
    # F1: the far-side landing

    def _land(self, crossed, where, own_left, own_star, branches):
        if not LAND:
            return own_star
        direction = math.copysign(1.0, own_star - own_left)
        if own_star == own_left:
            return own_star
        landing = own_star
        for jump in crossed:
            landing = self._far_side(jump, where, landing, direction,
                                     branches)
        return landing

    def _far_side(self, jump, where, own_star, direction, branches):
        near = branches[jump.placeholder]

        def branch_at(value):
            return _branch_of(jump, self._level(jump, where, value, branches))

        step = math.ulp(own_star) if own_star else 5e-324
        if branch_at(own_star) != near:
            STATS['already far'] += 1
            far, inside = own_star, None
            for power in range(200):
                STATS['walk steps'] += 1
                candidate = own_star - direction * step * (2 ** power)
                if branch_at(candidate) == near:
                    inside = candidate
                    break
            if inside is None:
                return own_star
        else:
            inside, far = own_star, None
            for power in range(200):
                STATS['walk steps'] += 1
                candidate = own_star + direction * step * (2 ** power)
                if branch_at(candidate) != near:
                    far = candidate
                    break
            if far is None:
                return own_star
        low, high = _ordinal(inside), _ordinal(far)
        while abs(high - low) > 1:
            STATS['walk steps'] += 1
            middle = (low + high) // 2
            if branch_at(_from_ordinal(middle)) == near:
                low = middle
            else:
                high = middle
        return _from_ordinal(high)


##############################################
# The protocol extension

_increments = Edge.increments


def _patched_increments(self, values, deltas, crossings=None, tick=0):
    if self.kind != 'law' or not self.plans:
        return _increments(self, values, deltas, crossings, tick)
    reads = {index for index, key in enumerate(self.gives)
             if key in self.needs}
    if not reads:
        return _increments(self, values, deltas, crossings, tick)
    start = self._inputs(values)
    delta = {name: deltas[key] for name, key in zip(self.names, self.needs)}
    end = self._inputs(values, deltas)
    found = []
    for index, key in enumerate(self.gives):
        plan = self.plans[index]
        if index not in reads or plan is None:
            graph = self.graphs[index]
            found.append((key, P._evaluated(graph, end)
                          - P._evaluated(graph, start)))
            continue
        walker = _Walker(plan, start, delta, self.driven[index],
                         self.description, self.driven[index])
        increment, landing = walker.run(crossings, tick)
        if landing is not None:
            LANDINGS[key] = landing
        found.append((key, increment))
    return found


Edge.increments = _patched_increments

from solid_node.simulation.run import Run                 # noqa: E402

_integrate = Run.integrate


def _patched_integrate(self, tick, advance, only=None):
    """The run commits the landing, not `value + delta` -- the
    increments-protocol extension, stood in for here by applying the
    reported landing to the committed bank.

    Faithful only for a tick of ONE segment, which is every tick of this
    spike's fixture (it declares no range, so no stop can cut it)."""
    LANDINGS.clear()
    _integrate(self, tick, advance, only)
    if LANDINGS:
        identifiers = {key: identifier
                       for identifier, key in self.keys.items()}
        bank = dict(self.bank)
        for key, value in LANDINGS.items():
            bank[identifiers[key]] = value
        self.bank = bank
        self.bind()


Run.integrate = _patched_integrate

from solid_node.math import floor                         # noqa: E402
from solid_node.motion.joints import Revolute             # noqa: E402
from solid_node.motion.ports import Time                  # noqa: E402
from solid_node.node import AssemblyNode                  # noqa: E402
from solid_node.simulation import Driver, Sim             # noqa: E402
from solid_node.simulation.run import RunSnapshot         # noqa: E402


##############################################
# The fixture

def build(period, half, dt=1.0):
    """A ring driving one wheel through a MISSING TOOTH: the wheel is
    disengaged over the band of half-width `half` about every multiple
    of `period`, entered from either direction."""

    def missing_tooth(sources, target):
        def law(ring, wheel):
            shifted = wheel + half
            return ring * (shifted - period * floor(shifted / period)
                           >= 2 * half)
        return law

    class Dial(AssemblyNode):
        rotation = Revolute(axis=(0, 0, 1), unit='deg')

        def simulate(self):
            if self.rotation.value is None:
                self.rotation = 0.0

        def render(self):
            pass

    class Clearing(AssemblyNode):
        time = Time.running()
        ring = Driver(default=0.0, unit='deg')
        wheel = Dial()
        (ring & wheel.rotation).drives(wheel.rotation, law=missing_tooth)

        def render(self):
            pass

    return Sim(Clearing(), dt=dt)


def engaged(own, period, half):
    shifted = own + half
    return shifted - period * math.floor(shifted / period) >= 2 * half


def place(sim, own, ring=0.0):
    sim.restore(RunSnapshot(sim._run.program.identity, sim.dt, 0,
                            (('ring', ring), ('wheel.rotation', own)), ()))


def sweep(sim, travel):
    handle = sim.move('ring', by=travel, duration=1.0)
    sim.run(1.0)
    return handle


def main(trials, combinations):
    random.seed(20260915)
    failures = {'engaged after the cut': 0, 'moved on a later tick': 0,
                'not the nearest far-side float': 0, 'refused': 0,
                'never reached the gap': 0}
    examples = []
    worst = [0.0]
    done = 0
    started = time.perf_counter()
    for _combination in range(combinations):
        period = random.choice((360.0, 36.0, 11.25, 100.0, 1.0,
                                random.uniform(0.1, 1000.0)))
        half = period * random.choice((1e-9, 1e-6, 1e-3, 0.01, 0.1))
        sim = build(period, half)
        per = max(1, trials // combinations)
        for _trial in range(per):
            done += 1
            digit = random.uniform(2 * half, period - 2 * half)
            turns = random.randint(-3, 3)
            own = turns * period + digit
            direction = random.choice((1.0, -1.0))
            # Enough ring travel to carry the wheel past the band, and
            # then some: the mechanism's ring runs on past a wheel that
            # has finished.
            travel = direction * (period + random.uniform(0.0, 3 * period))
            try:
                place(sim, own)
                sweep(sim, travel)
                landed = sim.state['wheel.rotation']
                if engaged(landed, period, half):
                    failures['engaged after the cut'] += 1
                    if len(examples) < 4:
                        examples.append({
                            'period': period, 'half': half, 'own': own,
                            'travel': travel, 'landed': landed,
                            'residue': landed - period * round(landed / period)})
                    continue
                if landed == own:
                    failures['never reached the gap'] += 1
                    continue
                if direction > 0:
                    edge = period * round((landed + half) / period) - half
                else:
                    edge = period * round((landed - half) / period) + half
                residue = abs(landed - edge) / math.ulp(landed or 1.0)
                worst[0] = max(worst[0], residue)
                # The nearest far-side float: one float back toward the
                # surface must read ENGAGED.
                back = math.nextafter(landed, -math.inf * direction)
                if LAND and not engaged(back, period, half):
                    failures['not the nearest far-side float'] += 1
                    if len(examples) < 4:
                        examples.append({'period': period, 'half': half,
                                         'own': own, 'landed': landed,
                                         'back': back})
                # Three more ticks of ring travel, the wheel expected to
                # stand bit-identically still.
                for _again in range(3):
                    sweep(sim, travel)
                    if sim.state['wheel.rotation'] != landed:
                        failures['moved on a later tick'] += 1
                        if len(examples) < 4:
                            examples.append({
                                'period': period, 'half': half, 'own': own,
                                'landed': landed,
                                'then': sim.state['wheel.rotation']})
                        break
            except Exception as failure:                  # noqa: BLE001
                failures['refused'] += 1
                if len(examples) < 4:
                    examples.append({'error': type(failure).__name__,
                                     'message': str(failure)[:300]})
    return {'rule': 'far-side landing' if LAND else 'segment arithmetic',
            'trials': done,
            'seconds': round(time.perf_counter() - started, 1),
            'failures': failures,
            'worst distance from the band edge, in ulps': round(worst[0], 1),
            'examples': examples,
            'stats': dict(STATS)}


if __name__ == '__main__':
    green = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    combos = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    red = int(sys.argv[3]) if len(sys.argv) > 3 else green
    report = {}
    for flag, count in ((False, red), (True, green)):
        globals()['LAND'] = flag
        for key in STATS:
            STATS[key] = 0
        report['GREEN' if flag else 'RED'] = main(count, combos)
        print(json.dumps(report, indent=2, default=repr), flush=True)
