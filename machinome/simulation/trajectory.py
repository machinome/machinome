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
import math
import struct

from . import program as p


class Motion:
    def __init__(self, start, end, pieces, affine=True, line_delta=None):
        self.start, self.end = start, end
        self.line_delta = line_delta
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
                   [(0.0, 1.0, lambda t: start + delta * t)],
                   line_delta=delta)

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
        self.follow_cuts = {}
        self.follow_closures = {}
        # Set only for a full move(to=) terminal whose additive end loses
        # the stated target's IEEE-754 bit. Interior deltas are unchanged.
        self.terminal_keys = set()

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


def _sources(motions, left, right, exact_lines=False,
             terminal_at_end=False):
    selected = {name: motion.restrict(left, right)
                for name, motion in motions.items()}
    start = {name: motion.start for name, motion in selected.items()}
    if terminal_at_end and right == 1.0:
        # Keep authored source-line deltas for jump partitioning, but let
        # an evaluation at the full terminal fraction read Motion.at(1),
        # whose cache holds the exact `to` target. Interior fractions use
        # the original piece evaluator.
        curved = Sources(selected)
        curved.update((name, motion.line_delta)
                      for name, motion in motions.items()
                      if motion.line_delta is not None)
        return start, curved
    if all(motion.affine for motion in selected.values()):
        delta = {
            name: (motions[name].line_delta
                   if exact_lines and left == 0.0 and right == 1.0
                   and motions[name].line_delta is not None
                   else motion.end - motion.start)
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
               closed=False, exact_source_lines=False,
               terminal_at_end=False):
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
        start, delta = _sources(motions, left, right,
                                exact_lines=exact_source_lines,
                                terminal_at_end=terminal_at_end)
        found = [] if crossings is not None else None
        local = []
        if reading is not None:
            start[reading.own] = current
            walk = p._Walk(reading, start, delta, edge.description,
                           edge.driven[index], forced, edge)
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
                    return p._evaluated_law(edge, edge.driven[index], graph,
                                            values)

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
            start, delta = _sources(
                sources, left, right,
                terminal_at_end=any(key in deltas.terminal_keys
                                    for key in member.needs))
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
    terminal_sensitive = set()
    for left, right in zip(cuts, cuts[1:]):
        forced = []
        for member, plan, sources in zip(block.members, block.plans, source_maps):
            start, delta = _sources(
                sources, left, right,
                terminal_at_end=any(key in deltas.terminal_keys
                                    for key in member.needs))
            forced.append(plan._branches(start, delta, .5, len(plan.jumps),
                                          member.description, member.driven[0])
                          if plan else {})
        determined = {}
        selected_terminal = set()
        for index in block._order(forced, left, right):
            member, own = block.members[index], block.gives[index]
            if deltas.terminal_keys or selected_terminal:
                member_plan = member.plans[0] if member.plans else None
                active_names = (p._reads_under(member_plan, forced[index])
                                if member_plan else
                                p.free_names(p.as_node(member.graphs[0])))
                if any(name in active_names and
                       (key in deltas.terminal_keys or key in selected_terminal)
                       for name, key in zip(member.names, member.needs)):
                    selected_terminal.add(own)
            sources = {}
            for name, key in zip(member.names, member.needs):
                sources[name] = (determined.get(key) or Motion.line(current[key], 0)
                                 if key in current else
                                 deltas.motion(key, values).restrict(left, right))
            found = [] if crossings is not None else None
            motion, did_land = law_motion(member, 0, sources, current[own],
                                          found, tick, forced[index],
                                          closed=right < 1.0,
                                          terminal_at_end=own in selected_terminal)
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
        terminal_sensitive.update(selected_terminal)
    for key in block.gives:
        deltas.motions[key] = Motion(values[key], current[key], pieces[key], affine[key])
        needs_terminal_landing = (key in terminal_sensitive and
            struct.pack('!d', values[key] + (current[key]-values[key])) !=
            struct.pack('!d', current[key]))
        if needs_terminal_landing:
            deltas.terminal_keys.add(key)
        if landings is not None and (key in landed or needs_terminal_landing):
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


def follow_increments(edge, values, deltas, landings, tick):
    """Project one retained coordinate through certified envelope pieces."""
    from .program import UnsupportedLaw

    own = edge.gives[0]
    source_keys = edge.needs[:2]
    source_names = edge.names[:2]
    sources = {}
    for name, key in zip(source_names, source_keys):
        motion = (getattr(deltas, 'motions', {}).get(key)
                  or Motion.line(values[key], deltas.get(key, 0.0)))
        if (not motion.affine or len(motion.pieces) != 1
                or motion.line_delta is None):
            raise UnsupportedLaw(
                f'{edge.description}: Follow source {name} does not have '
                f'one certified exact linear path in this stretch.')
        sources[name] = motion

    if all(motion.constant and
           (motion.start != 0.0 or
            math.copysign(1.0, motion.start) ==
            math.copysign(1.0, motion.end))
           for motion in sources.values()):
        # An unrelated tick does not reproject a free ball or change the
        # retained value's signed zero. Rest and restore already validate
        # the standing interval; no within-stretch source path exists.
        return [(own, 0.0)]

    initial = {name: motion.start for name, motion in sources.items()}
    lower_start = edge.lower_graph.evaluate(initial)
    upper_start = edge.upper_graph.evaluate(initial)
    lower, _ = law_motion(edge.lower_path, 0, sources, lower_start,
                          None, tick, exact_source_lines=True)
    upper, _ = law_motion(edge.upper_path, 0, sources, upper_start,
                          None, tick, exact_source_lines=True)
    if not lower.affine or not upper.affine:
        raise UnsupportedLaw(
            f'{edge.description}: Follow envelopes must be certified '
            f'piecewise affine over this stretch.')

    cuts = tuple(sorted({0.0, 1.0, *lower.ends, *upper.ends}))
    current = values[own]
    closures = []

    def project(low, high):
        nonlocal current
        if not all(math.isfinite(value) for value in (low, high, current)):
            raise UnsupportedLaw(
                f'{edge.description}: Follow encountered a non-finite '
                f'envelope or retained value; the tick was not committed.')
        current = max(low, min(current, high))

    def direct(t):
        arguments = {name: motion.at(t) for name, motion in sources.items()}
        return (edge.lower_graph.evaluate(arguments),
                edge.upper_graph.evaluate(arguments))

    def closure_values(at):
        # Source `Motion.at(1)` uses its absolute endpoint cache. A source
        # piece's one-sided closure can differ by a last bit, so keep its
        # own evaluator at the piece closure as well.
        return {name: motion.pieces[0][2](at)
                for name, motion in sources.items()}

    def absolute_piece(path, graph, t):
        """Evaluate an authored branch, never an increment-integrated path.

        ``law_motion`` supplies the certified partition and affine shape,
        but its piece callable carries cumulative increments across cuts.
        The envelope is an *absolute* physical clearance. Freeze the jump
        branches at the piece midpoint and evaluate its original skeleton
        with actual source values at either one-sided closure.
        """
        plan = path.plans[0] if path.plans else None
        if plan is None:
            return lambda at: graph.evaluate(closure_values(at))
        at_middle = {name: motion.at(t) for name, motion in sources.items()}
        no_change = {name: (-0.0 if value == 0.0 and
                            math.copysign(1.0, value) < 0.0 else 0.0)
                     for name, value in at_middle.items()}
        branches = plan._branches(at_middle, no_change, 0.0,
                                  len(plan.jumps),
                                  path.description, path.driven[0])
        return lambda at: plan.skeleton.evaluate({**closure_values(at),
                                                   **branches})

    project(*direct(0.0))
    for left, right in zip(cuts, cuts[1:]):
        middle = (left + right) / 2.0
        low_piece = lower.pieces[min(bisect_right(lower.ends, middle),
                                     len(lower.pieces) - 1)]
        high_piece = upper.pieces[min(bisect_right(upper.ends, middle),
                                      len(upper.pieces) - 1)]
        low_at = absolute_piece(edge.lower_path, edge.lower_graph, middle)
        high_at = absolute_piece(edge.upper_path, edge.upper_graph, middle)
        project(low_at(left), high_at(left))
        low_close, high_close = low_at(right), high_at(right)
        project(low_close, high_close)
        closures.append((right, current, low_close, high_close))
        project(*direct(right))

    if landings is not None:
        landings[own] = current
    if hasattr(deltas, 'follow_cuts') and not all(
            motion.constant for motion in sources.values()):
        deltas.follow_cuts[own] = cuts
        deltas.follow_closures[own] = tuple(closures)
    return [(own, current - values[own])]


def _propagate(edge, values, deltas, crossings, tick, landings):
    if edge.kind == 'follow':
        deltas.untraced.update(edge.gives)
        result = follow_increments(edge, values, deltas, landings, tick)
        incoming_terminal = any(key in deltas.terminal_keys for key in edge.needs)
        for key, increment in result:
            if (incoming_terminal and landings is not None and key in landings and
                    struct.pack('!d', values[key]+increment) !=
                    struct.pack('!d', landings[key])):
                deltas.terminal_keys.add(key)
        return result
    if edge.kind == 'play':
        deltas.untraced.update(edge.gives)
        result = edge.increments(values, dict(deltas), crossings, tick, landings)
        incoming_terminal = any(key in deltas.terminal_keys for key in edge.needs)
        for key, increment in result:
            if (incoming_terminal and landings is not None and key in landings and
                    struct.pack('!d', values[key]+increment) !=
                    struct.pack('!d', landings[key])):
                deltas.terminal_keys.add(key)
        return result
    if any(key in deltas.untraced for key in edge.needs):
        # Play owns a clearance-aware prefix replay. A net displacement
        # from it is not a certified affine path, even through an affine
        # observer. Preserve that executor until it supplies a real path.
        deltas.untraced.update(edge.gives)
        if (edge.kind == 'law' and not edge.plans and not edge.retained and
                landings is not None and
                any(key in deltas.terminal_keys for key in edge.needs)):
            start = edge._inputs(values)
            end = {name: (landings[key] if key in deltas.terminal_keys
                          and key in landings else values[key]+deltas[key])
                   for name, key in zip(edge.names, edge.needs)}
            result = []
            for key, driven, graph in zip(edge.gives, edge.driven,
                                          edge.graphs):
                after = p._evaluated_law(edge, driven, graph, end)
                before = p._evaluated_law(edge, driven, graph, start)
                increment = after-before
                initial = values[key]
                aligned = (struct.pack('!d', initial) ==
                           struct.pack('!d', before))
                terminal = after if aligned else initial+increment
                if struct.pack('!d', initial+increment) != struct.pack('!d', terminal):
                    deltas.terminal_keys.add(key)
                    landings[key] = terminal
                result.append((key, increment))
            return result
        return edge.increments(values, dict(deltas), crossings, tick, landings)
    if edge.kind == 'block':
        return block_motion(edge.block, values, deltas, crossings, tick, landings)
    if edge.kind == 'law':
        sources = {name: deltas.motion(key, values)
                   for name, key in zip(edge.names, edge.needs)}
        if (not edge.plans and not edge.retained and
                all(shape in p._AFFINE for shape in edge.shapes) and
                any(key in deltas.terminal_keys for key in edge.needs)):
            # Preserve the old increment and its arithmetic at every
            # interior fraction. Only the fully admitted terminal value
            # uses the stated target through the relation graph.
            at_start = {name: motion.start for name, motion in sources.items()}
            at_end = {name: motion.end for name, motion in sources.items()}
            result = edge.increments(values, dict(deltas), crossings,
                                     tick, landings)
            for index, (key, increment) in enumerate(result):
                graph = edge.graphs[index]
                driven = edge.driven[index]
                before = p._evaluated_law(edge, driven, graph, at_start)
                after = p._evaluated_law(edge, driven, graph, at_end)
                initial = values[key]
                aligned = (struct.pack('!d', initial) ==
                           struct.pack('!d', before))
                terminal = after if aligned else initial + (after-before)
                deltas.motions[key] = Motion(
                    initial, terminal,
                    [(0.0, 1.0, lambda t, initial=initial,
                      increment=increment: initial + increment*t)],
                    affine=True, line_delta=increment)
                deltas.terminal_keys.add(key)
                if landings is not None:
                    landings[key] = terminal
            return result
        incoming_linear = all(m.affine and not m.cuts() for m in sources.values())
        if (not edge.plans and all(shape in p._AFFINE for shape in edge.shapes)
                and incoming_linear):
            # Exact endpoint propagation needs no extra evaluations or
            # re-association through the target's (possibly large) bank.
            result = edge.increments(values, dict(deltas), crossings, tick, landings)
            for key, increment in result:
                deltas.motions[key] = Motion.line(values[key], increment)
            return result
        if (incoming_linear and not any(key in deltas.demanded for key in edge.gives)
                and not any(key in deltas.terminal_keys for key in edge.needs)):
            return edge.increments(values, dict(deltas), crossings, tick, landings)
        incoming_terminal = any(need in deltas.terminal_keys
                                for need in edge.needs)
        result = []
        for index, key in enumerate(edge.gives):
            motion, landed = law_motion(edge, index, sources, values[key],
                                        crossings, tick,
                                        exact_source_lines=bool(edge.plans) and
                                        incoming_terminal,
                                        terminal_at_end=incoming_terminal)
            if (edge.plans and
                    (not edge.retained or not edge.retained[index]) and
                    incoming_terminal):
                # The jump walk used the original source line and cuts,
                # but evaluated the authored exact source at its terminal
                # end. Keep that integrated result (which may carry whole
                # turns of history); never evaluate the rounded legacy end,
                # which can even lie outside an authored domain.
                terminal = motion.end
                if terminal == 0.0:
                    # The integrated zero can lose a stated negative-zero
                    # sign. Only this case needs another authored endpoint
                    # read; all nonzero paths retain their integration.
                    exact_end = {name: source.end
                                 for name, source in sources.items()}
                    authored_exact = p._evaluated_law(
                        edge, edge.driven[index], edge.graphs[index], exact_end)
                    if (authored_exact == 0.0 and
                            struct.pack('!d', terminal) !=
                            struct.pack('!d', authored_exact)):
                        terminal = authored_exact
                        motion = Motion(values[key], terminal, motion.pieces,
                                        affine=motion.affine,
                                        line_delta=motion.line_delta)
                if (struct.pack('!d', values[key] +
                                 (terminal-values[key])) !=
                        struct.pack('!d', terminal)):
                    deltas.terminal_keys.add(key)
                    landed = True
            if (not edge.plans and incoming_terminal and
                    struct.pack('!d', values[key] +
                                (motion.end-values[key])) !=
                    struct.pack('!d', motion.end)):
                # A curved law can have an exact authored end even though
                # its bank increment cannot reconstruct that bit.
                deltas.terminal_keys.add(key)
                landed = True
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
            if any(need in deltas.terminal_keys for need in edge.needs):
                if edge.kind == 'wiring':
                    before = values[edge.needs[0]] * edge.factors[0]
                    after = sources[edge.needs[0]].end * edge.factors[0]
                else:
                    before = edge._linear(values)
                    after = edge._linear({need: source.end
                                          for need, source in sources.items()})
                initial = values[key]
                # A driven coordinate may have retained history. In that
                # case only the relation's exact terminal change is added;
                # a coordinate aligned with the relation may land exactly.
                aligned = (struct.pack('!d', initial) ==
                           struct.pack('!d', before))
                terminal = after if aligned else initial + (after-before)
                old_motion = deltas.motions[key]
                deltas.motions[key] = Motion(
                    initial, terminal, old_motion.pieces,
                    affine=old_motion.affine,
                    line_delta=(increment if old_motion.affine and
                                not old_motion.cuts() else None))
                deltas.terminal_keys.add(key)
                if landings is not None:
                    landings[key] = terminal
    return result
