# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Tick-local physical paths passed between incrementally integrated laws.

Pieces carry evaluators, not samples. Affine pieces can be interpolated
exactly; curved pieces retain their expression evaluation. Restricting a
path never spreads a landed coordinate's travel across its later dwell.
"""

from bisect import bisect_right
from copy import copy

from . import program as p


class Motion:
    def __init__(self, start, end, pieces, affine=True):
        self.start, self.end = start, end
        self.pieces = tuple(pieces)
        self.ends = tuple(piece[1] for piece in self.pieces)
        self.affine = affine
        self.cache = {0.0: start, 1.0: end}
        self.constant = (affine and start == end and
                         all(fn(a) == start and fn(b) == start
                             for a, b, fn in self.pieces))
        if self.constant:
            self.pieces = ((0.0, 1.0, lambda t: start),)
            self.ends = (1.0,)

    @classmethod
    def line(cls, start, delta):
        return cls(start, start + delta,
                   [(0.0, 1.0, lambda t: start + delta * t)])

    def at(self, t):
        if t in self.cache:
            return self.cache[t]
        index = min(bisect_right(self.ends, t), len(self.pieces) - 1)
        value = self.pieces[index][2](t)
        self.cache[t] = value
        return value

    def cuts(self, left=0.0, right=1.0):
        return tuple(t for t in self.ends if left < t < right)

    def restrict(self, left, right):
        width = right - left
        edges = (left,) + self.cuts(left, right) + (right,)
        pieces = [( (a-left)/width, (b-left)/width,
                    lambda t, left=left, width=width: self.at(left + width*t))
                  for a, b in zip(edges, edges[1:])]
        return Motion(self.at(left), self.at(right), pieces, self.affine)


class Propagation(dict):
    """One pass's delta bank and the paths determining those deltas."""

    def __init__(self, values, demanded=()):
        super().__init__(values)
        self.motions = {}
        self.demanded = frozenset(demanded)
        self.untraced = set()

    def motion(self, key, values):
        return self.motions.get(key) or Motion.line(values[key], self[key])


class Sources(dict):
    """Curved source values at a point, beside ordinary movement flags."""

    curved = True

    def __init__(self, motions):
        self.motions = dict(motions)
        super().__init__((name, motion.end - motion.start or
                         (1.0 if not motion.affine or motion.cuts() else 0.0))
                         for name, motion in motions.items())

    def along(self, start, t):
        return {name: self.motions[name].at(t) if name in self.motions
                else start[name] + self[name]*t for name in start}

    def hold(self, name):
        self.motions.pop(name, None)

    def copy(self):
        result = Sources(self.motions)
        result.update(self)
        return result


def _cuts(motions):
    result = [0.0, 1.0]
    for motion in motions.values():
        result = p._merged(result, list(motion.cuts()))
    return result


def _sources(motions, left, right):
    selected = {name: motion.restrict(left, right)
                for name, motion in motions.items()}
    start = {name: motion.start for name, motion in selected.items()}
    if all(motion.affine for motion in selected.values()):
        delta = {name: motion.end - motion.start
                 for name, motion in selected.items()}
    else:
        delta = Sources(selected)
    return start, delta


def _piece(a, b, evaluate, affine):
    """Freeze affine evaluations into a cheap exact segment."""
    if affine:
        low, high = evaluate(a), evaluate(b)
        slope = (high-low)/(b-a)
        evaluate = lambda t, low=low, slope=slope, a=a: low + slope*(t-a)
    return a, b, evaluate


def law_motion(edge, index, motions, initial, crossings, tick, forced=None,
               closed=False):
    if all(motion.constant for motion in motions.values()):
        return Motion.line(initial, 0.0), False
    plan = edge.plans[index] if edge.plans else None
    reading = edge.retained[index] if edge.retained else None
    graph = plan.skeleton if plan else edge.graphs[index]
    standing = {name: motion.start for name, motion in motions.items()
                if motion.constant}
    standing.update(forced or {})
    shape = p._shape_of(p._folded(p.as_node(graph), standing))
    affine = shape is not None and all(m.affine for m in motions.values())
    kinks = p._KinkCuts(p.GraphValue(p._folded(p.as_node(graph), standing))) \
        if affine and shape == 'kinked' else None
    if reading is not None and affine and reading.shape != shape:
        reading = copy(reading)
        reading.shape, reading.kinks = shape, kinks
    pieces, current, landed, all_affine = [], initial, False, True
    cuts = _cuts(motions)
    for left, right in zip(cuts, cuts[1:]):
        start, delta = _sources(motions, left, right)
        found = [] if crossings is not None else None
        local = []
        if reading is not None:
            start[reading.own] = current
            walk = p._Walk(reading, start, delta, edge.description,
                           edge.driven[index], forced)
            increment, landing, _ = walk.run(found, tick, trajectory=local,
                                             closed=closed or right < 1.0)
            if not local:
                local = [(0.0, 1.0, lambda t, current=current: current, None)]
            current = current + increment if landing is None else landing
            landed |= landing is not None
        else:
            partitions = plan._partition(start, delta, edge.description,
                                         edge.driven[index], found, tick,
                                         forced, closed=closed or right < 1.0
                                         ) if plan else [0.0, 1.0]
            for low, high in zip(partitions, partitions[1:]):
                branches = plan._branches(
                    start, delta, (low+high)/2, len(plan.jumps),
                    edge.description, edge.driven[index], forced) if plan else {}

                def evaluate(t, start=start, delta=delta, branches=branches):
                    values = p._along(start, delta, t)
                    values.update(branches)
                    return p._evaluated(graph, values)

                base = evaluate(low)
                def at(t, evaluate=evaluate, base=base, current=current):
                    return current + (evaluate(t) - base)

                def values_at(t):
                    values = p._along(start, delta, t)
                    values.update(branches)
                    return values
                breaks = kinks.between(values_at, low, high) if kinks and affine else ()
                edges = (low,) + breaks + (high,)
                local.extend((a, b, at, branches) for a, b in zip(edges, edges[1:]))
                current = at(high)
        width = right-left
        for a, b, evaluate, branches in local:
            if b <= a:
                continue
            if branches is None:
                piece_shape, piece_affine, breaks = 'constant', True, ()
            else:
                folded = p._folded(p.as_node(graph), {**standing, **branches})
                piece_shape = p._shape_of(folded)
                names = p.free_names(folded)
                piece_affine = piece_shape is not None and all(
                    m.affine for name, m in motions.items() if name in names)
                def source_at(t):
                    vals = p._along(start, delta, t)
                    vals.update(branches)
                    return vals
                breaks = (p._KinkCuts(p.GraphValue(folded)).between(source_at, a, b)
                          if piece_affine and piece_shape == 'kinked' else ())
            all_affine &= piece_affine
            edges = (a,) + breaks + (b,)
            for low, high in zip(edges, edges[1:]):
                low, high, fn = _piece(low, high, evaluate, piece_affine)
                pieces.append((left + width*low, left + width*high,
                               lambda t, fn=fn, left=left, width=width:
                               fn((t-left)/width)))
        if found:
            crossings.extend(p.replace(entry, t=left+width*entry.t) for entry in found)
    return Motion(initial, current, pieces, all_affine), landed


def block_motion(block, values, deltas, crossings, tick, landings):
    first_crossing = len(crossings) if crossings is not None else 0
    source_maps = []
    for member in block.members:
        source_maps.append({name: deltas.motion(key, values)
                            if key not in block.gives else Motion.line(values[key], 0)
                            for name, key in zip(member.names, member.needs)})
    cuts = [0.0, 1.0]
    for member, plan, sources in zip(block.members, block.plans, source_maps):
        if plan is None:
            continue
        reads = set().union(*(p.free_names(p.as_node(jump.argument))
                              for jump in plan.jumps))
        outer = _cuts({name: motion for name, motion in sources.items()
                       if name in reads})
        cuts = p._merged(cuts, outer[1:-1])
        for left, right in zip(outer, outer[1:]):
            start, delta = _sources(sources, left, right)
            found = [] if crossings is not None else None
            local = plan._partition(start, delta, member.description,
                                    member.driven[0], found, tick,
                                    closed=right < 1.0)
            cuts = p._merged(cuts, [left+(right-left)*t for t in local[1:-1]])
            if found:
                crossings.extend(p.replace(entry, t=left+(right-left)*entry.t)
                                 for entry in found)
    current = {key: values[key] for key in block.gives}
    located = [] if crossings is not None else None
    pieces = {key: [] for key in block.gives}
    affine = {key: True for key in block.gives}
    landed = set()
    for left, right in zip(cuts, cuts[1:]):
        forced = []
        for member, plan, sources in zip(block.members, block.plans, source_maps):
            start, delta = _sources(sources, left, right)
            forced.append(plan._branches(start, delta, .5, len(plan.jumps),
                                          member.description, member.driven[0])
                          if plan else {})
        determined = {}
        for index in block._order(forced, left, right):
            member, own = block.members[index], block.gives[index]
            sources = {}
            for name, key in zip(member.names, member.needs):
                sources[name] = (determined.get(key) or Motion.line(current[key], 0)
                                 if key in current else
                                 deltas.motion(key, values).restrict(left, right))
            found = [] if crossings is not None else None
            motion, did_land = law_motion(member, 0, sources, current[own],
                                          found, tick, forced[index],
                                          closed=right < 1.0)
            determined[own] = motion
            current[own] = motion.end
            affine[own] &= motion.affine
            if did_land:
                landed.add(own)
            width = right-left
            pieces[own].extend((left+width*a, left+width*b,
                               lambda t, fn=fn, left=left, width=width:
                               fn((t-left)/width))
                              for a, b, fn in motion.pieces)
            if found:
                located.extend(p.replace(entry, t=left+width*entry.t) for entry in found)
    for key in block.gives:
        deltas.motions[key] = Motion(values[key], current[key], pieces[key], affine[key])
        if landings is not None and key in landed:
            landings[key] = current[key]
    if located:
        crossings.extend(located)
    if crossings is not None:
        crossings[first_crossing:] = sorted(crossings[first_crossing:],
                                            key=lambda entry: entry.t)
    return [(key, current[key]-values[key]) for key in block.gives]


def _check_budget(records):
    """Inherited source pieces do not renew a law's crossing allowance."""
    by_coordinate = {}
    for entry in records:
        by_coordinate.setdefault((entry.relation, entry.coordinate), []).append(entry)
    for entries in by_coordinate.values():
        times = p._deduplicated([(entry.t, 0) for entry in entries])
        if len(times) > p._MAX_CROSSINGS:
            entry = entries[-1]
            raise p._too_many(entry.relation, entry.coordinate, entry, len(times))


def propagate(edge, values, deltas, crossings, tick, landings):
    # Count even when history is disabled or the caller is a pure probe.
    found = []
    result = _propagate(edge, values, deltas, found, tick, landings)
    _check_budget(found)
    if crossings is not None:
        crossings.extend(found)
    return result


def _propagate(edge, values, deltas, crossings, tick, landings):
    if edge.kind == 'play' or any(key in deltas.untraced for key in edge.needs):
        # Play owns a clearance-aware prefix replay. A net displacement
        # from it is not a certified affine path, even through an affine
        # observer. Preserve that executor until it supplies a real path.
        deltas.untraced.update(edge.gives)
        return edge.increments(values, dict(deltas), crossings, tick, landings)
    if edge.kind == 'block':
        return block_motion(edge.block, values, deltas, crossings, tick, landings)
    if edge.kind == 'law':
        sources = {name: deltas.motion(key, values)
                   for name, key in zip(edge.names, edge.needs)}
        incoming_linear = all(m.affine and not m.cuts() for m in sources.values())
        if (not edge.plans and all(shape in p._AFFINE for shape in edge.shapes)
                and incoming_linear):
            # Exact endpoint propagation needs no extra evaluations or
            # re-association through the target's (possibly large) bank.
            result = edge.increments(values, dict(deltas), crossings, tick, landings)
            for key, increment in result:
                deltas.motions[key] = Motion.line(values[key], increment)
            return result
        if incoming_linear and not any(key in deltas.demanded for key in edge.gives):
            return edge.increments(values, dict(deltas), crossings, tick, landings)
        result = []
        for index, key in enumerate(edge.gives):
            motion, landed = law_motion(edge, index, sources, values[key],
                                        crossings, tick)
            deltas.motions[key] = motion
            if landed and landings is not None:
                landings[key] = motion.end
            result.append((key, motion.end-values[key]))
        return result
    result = edge.increments(values, dict(deltas), crossings, tick, landings)
    if edge.kind in ('wiring', 'formula'):
        sources = {key: deltas.motion(key, values) for key in edge.needs}
        cuts = _cuts(sources)
        for key, increment in result:
            def at(t, key=key):
                local = {need: source.at(t)-values[need]
                         for need, source in sources.items()}
                return values[key] + (local[edge.needs[0]]*edge.factors[0]
                                      if edge.kind == 'wiring'
                                      else edge._linear(local, constant=0.0))
            deltas.motions[key] = Motion(values[key], values[key]+increment,
                [(a, b, at) for a, b in zip(cuts, cuts[1:])],
                all(m.affine for m in sources.values()))
    return result
