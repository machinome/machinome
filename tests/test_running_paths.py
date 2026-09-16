# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Only what moves along a tick's path is evaluated.

OpenSpec change ``evaluate-only-what-moves``. Under a running root the
engine follows a quantity along a tick's path by evaluating its
expression graph over and over -- 64 samples per piece in a search, two
per piece in a solve. Most of that graph never changes over one path with
one branch reading: this is proved here on ``DetentReader``
(``tests/clearing_project/machine.py``), a fixture built in the shape of
the originating machine's own register dials -- a self-read law whose
SKELETON carries the real detent-cam arithmetic
(``simulation/dial_cam.py``) over a phase reaching through a chain of
sibling coordinates the tick never moves.

The originating project is the Curta:
``projects/Calculators/Curta-Type-I-3x``, branch ``direct-operation``,
HEAD ``9fb725f``, whose ``OperatingCurta`` pays 3.28 s per 0.1 s tick
because 83.7 % of it is exactly this recomputation
(``openspec/changes/evaluate-only-what-moves/proposal.md``,
``design.md``). Nothing about a crossing, a landing, a branch reading or
a committed value changes here: what falls is the cost INSIDE one
evaluation, never the count of evaluations or their answers.
"""

import math

from solid_node.simulation import Sim

from .base import BaseNodeTest, expression_evaluations, graph_node_visits
from .clearing_project.machine import DetentReader
from .running_project.machine import Clearing, Train


#: The scenario every case in this file steps: `drive` sweeps 900 wheel
#: degrees over 1.2 s, in twelve 0.1 s ticks -- `evidence.md`'s task 1.x
#: and 5.x measurements are all taken from this exact scenario.
DRIVE_SWEEP = 900.0
DRIVE_DURATION = 1.2
TICKS = 12

#: The RED node-visit count this fixture pays on the unpatched tree,
#: measured once (`evidence.md`, task 5.2) and pinned here: node visits
#: are deterministic, so this is a PIN and not a timing test. GREEN is
#: asserted under a fifth of it.
RED_NODE_VISITS_PER_TICK = 92211.25

#: The golden: the fixture's own committed crossings and its final bank,
#: taken from the UNPATCHED tree (`evidence.md`, task 5.3) before
#: `_PathValue` was used anywhere. Every entry here must stand bit for
#: bit once the mechanism is in place.
GOLDEN_CROSSING_LEVELS = (13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0,
                          21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0,
                          29.0, 30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0,
                          37.0)
GOLDEN_CROSSING_COUNT = 25
GOLDEN_WHEEL_TURN = 350.00000000000017


def _run_scenario(record=None):
    sim = Sim(DetentReader(), dt=.1, record=record)
    sim.move('drive', by=DRIVE_SWEEP, duration=DRIVE_DURATION)
    return sim


class DetentReaderNodeVisitsTest(BaseNodeTest):
    """Case A (design.md section 9 A): the fixture's node visits per
    tick fall by more than a fifth -- the unit this change actually
    moves, not the evaluation count."""

    def test_node_visits_fall_under_a_fifth(self):
        sim = _run_scenario()
        visits = graph_node_visits(sim, TICKS)
        per_tick = visits / TICKS
        self.assertLess(
            per_tick, RED_NODE_VISITS_PER_TICK / 5.0,
            f'expected fewer than a fifth of the RED {RED_NODE_VISITS_PER_TICK} '
            f'node visits/tick; got {per_tick}')


class DetentReaderGoldenTest(BaseNodeTest):
    """Case B (design.md section 9 A): nothing the fixture computes
    moves. Every recorded crossing and the final committed bank are
    asserted exactly against the golden taken from the unpatched tree."""

    def test_crossings_and_bank_are_unchanged(self):
        sim = _run_scenario(record=500)
        for _ in range(TICKS):
            sim.run(.1)
        self.assertEqual(len(sim.crossings), GOLDEN_CROSSING_COUNT)
        levels = tuple(crossing.level for crossing in sim.crossings)
        self.assertEqual(levels, GOLDEN_CROSSING_LEVELS)
        for crossing in sim.crossings:
            self.assertEqual(crossing.coordinate, 'wheel.turn')
            self.assertEqual(crossing.primitive, '%')
        self.assertEqual(len(sim.stops), 0)
        bank = dict(sim.snapshot().bank)
        self.assertEqual(bank['wheel.turn'], GOLDEN_WHEEL_TURN)
        self.assertEqual(bank['drive'], DRIVE_SWEEP)


class FixedEvaluationCountTest(BaseNodeTest):
    """Case C (design.md section 9 A, section 10): `Clearing` still
    costs exactly 98.6 evaluations a tick and `Train` 8.0 -- the pins
    `cut-at-the-kink` set -- because `expression_evaluations` counts a
    bound path value's `bind`/`at` as one evaluation each, the same as
    a whole-graph `GraphValue.evaluate` call before this cycle."""

    def test_train_evaluations_unmoved(self):
        sim = Sim(Train(), dt=.1)
        sim.move('crank', by=90.0, duration=1.0)
        self.assertAlmostEqual(expression_evaluations(sim, 10) / 10, 8.0)

    def test_clearing_evaluations_unmoved(self):
        sim = Sim(Clearing(), dt=.1)
        sim.move('ring', by=600.0, duration=1.0)
        self.assertAlmostEqual(expression_evaluations(sim, 10) / 10, 98.6)

    def test_a_probe_counting_only_graphvalue_would_fail(self):
        """The naive probe -- counting only `GraphValue.evaluate` -- no
        longer reports `Clearing`'s pinned 98.6, because most of its
        evaluations are now bound path points. This is the guard task
        5.5 asks for: an implementation that forgot to teach the probe
        about `_PathValue` would pass silently otherwise."""
        from solid_node.scad_expression import GraphValue

        sim = Sim(Clearing(), dt=.1)
        sim.move('ring', by=600.0, duration=1.0)
        original = GraphValue.evaluate
        counted = [0]

        def counting(self, inputs):
            counted[0] += 1
            return original(self, inputs)

        GraphValue.evaluate = counting
        try:
            sim.run(1.0)
        finally:
            GraphValue.evaluate = original
        naive_per_tick = counted[0] / 10
        self.assertNotAlmostEqual(naive_per_tick, 98.6, places=1)


class MovingSetGuardTest(BaseNodeTest):
    """Case D (design.md section 9 A): the moving set is right,
    everywhere. A test-only checking path value recomputes the standing
    part at every point and asserts it equals the value it cached, over
    the running fixture set -- RED against a deliberately wrong moving
    set (the driven coordinate dropped from a level's moving names) and
    green otherwise.

    This is a WHITE-BOX test of `solid_node.simulation.program._PathValue`
    directly: it is the one guard for the single mistake the mechanism
    admits (design.md section 11), and the mistake is a property of the
    CLASS, not of any one fixture's dynamics.
    """

    def _graph_and_moving(self):
        from solid_node.expression_graph import ExpressionNode as N

        # `sin(own) + sibling` -- `own` moves, `sibling` never does.
        own = N('name', text='own')
        sibling = N('name', text='sibling')
        sin_own = N('call', 'sin', (own,))
        graph = N('binop', '+', (sin_own, sibling))
        return graph, {'own'}

    def test_correct_moving_set_matches_the_whole_walk(self):
        import solid_node.simulation.program as program_module

        graph, moving = self._graph_and_moving()
        path = program_module._PathValue(graph, moving)
        points = ({'own': 0.0, 'sibling': 100.0},
                  {'own': 30.0, 'sibling': 100.0},
                  {'own': 90.0, 'sibling': 100.0})
        first, *rest = points
        got = [path.bind(first)]
        got.extend(path.at(values) for values in rest)
        expected = [math.sin(math.radians(values['own'])) + values['sibling']
                   for values in points]
        for one, other in zip(got, expected):
            self.assertAlmostEqual(one, other)

    def test_wrong_moving_set_diverges(self):
        """RED: dropping `own` from the moving names makes the bound
        path treat `sin(own)` as standing -- frozen at the FIRST point's
        value -- so a later point's answer diverges from the whole-graph
        one, exactly the silent wrong answer design.md section 11
        warns of."""
        import solid_node.simulation.program as program_module

        graph, _correct_moving = self._graph_and_moving()
        wrong_moving = set()  # `own` dropped -- the single mistake.
        path = program_module._PathValue(graph, wrong_moving)
        first = {'own': 0.0, 'sibling': 100.0}
        second = {'own': 90.0, 'sibling': 100.0}
        path.bind(first)
        got = path.at(second)
        correct = math.sin(math.radians(90.0)) + 100.0
        self.assertNotAlmostEqual(got, correct)
        # And it silently equals the FIRST point's value -- frozen.
        self.assertAlmostEqual(got, math.sin(math.radians(0.0)) + 100.0)


class BranchDoesNotLeakAcrossPiecesTest(BaseNodeTest):
    """Case section 11's second risk, task 5.6: a piece's branch reading
    must not leak into the next. A `_PathValue`'s STANDING part depends
    on the branch placeholders bound for its own piece; re-binding for a
    new piece with a DIFFERENT branch must not read back the value the
    previous piece bound.
    """

    def test_rebinding_reads_the_new_piece_not_the_old_one(self):
        import solid_node.simulation.program as program_module

        from solid_node.expression_graph import ExpressionNode as N

        # `moving_name + placeholder` -- the placeholder stands for a
        # branch read fresh each piece, exactly as a jump's substituted
        # value does in the real skeleton.
        placeholder = N('name', text='$j0')
        moving_name = N('name', text='moving_name')
        graph = N('binop', '+', (moving_name, placeholder))
        path = program_module._PathValue(graph, {'moving_name'})

        first_piece = {'moving_name': 1.0, '$j0': 10.0}
        second_piece = {'moving_name': 1.0, '$j0': 20.0}

        first = path.bind(first_piece)
        self.assertAlmostEqual(first, 11.0)
        # A further point of the SAME piece still reads the piece's own
        # placeholder.
        self.assertAlmostEqual(path.at({'moving_name': 2.0, '$j0': 10.0}),
                               12.0)

        # A NEW piece: re-binding must pick up the new placeholder, not
        # the one the first piece bound.
        second = path.bind(second_piece)
        self.assertAlmostEqual(second, 21.0)
        self.assertAlmostEqual(path.at({'moving_name': 2.0, '$j0': 20.0}),
                               22.0)
