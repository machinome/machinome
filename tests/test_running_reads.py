# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""A law may read the coordinate it drives.

OpenSpec change ``read-the-driven-coordinate``. A relation whose source
group names its own driven end READS that coordinate: what the law sees
there is the value it HOLDS at the piece's start, never a value the same
piece is computing.

The originating mechanism is the Curta's clearing ring
(``projects/Calculators/Curta-Type-I-3x``, branch ``direct-operation``,
checkpoint ``b285393``): a rack turns a register dial only while its
teeth reach it AND the dial is not already standing at its missing-tooth
zero. Releasing the ring part way keeps the partial clearing; resuming
continues from there; sweeping an already-zero dial does not turn it
again. The dial's own retained angle decides whether the rack moves it.

The tick is integrated in TWO LAYERS: ADR-107's partition over the jump
nodes that do not depend on the driven coordinate, unchanged, and inside
each of its pieces a WALK over the ones that do, their branches read at
the piece's left end from the value the coordinate retains there. After
a cut the coordinate is committed at the nearest representable value on
the FAR side of the surface, and the run commits that float.

Everything here is new behaviour: a law with no self-read takes ADR-107's
path with nothing rebuilt at all, which ``tests/test_running_jumps.py``
pins.
"""

import math

from machinome.motion.ports import get_coordinate
from machinome.simulation import (Sim, TooManyCrossings, UnsupportedLaw,
                                   RunConflict)

from .base import BaseNodeTest, expression_evaluations
from .clearing_project.machine import (CurtaInterface, ORIGIN, RESULT_START,
                                       SWEEP, TEETH, TOOTH, station)
from .running_project.machine import (GAP, BlockedRing, Clearing,
                                      ClearingRow, CrowdedClearing,
                                      HeldAngle, KnifeEdge, LatchedClearing,
                                      RangedClearing, RefusedClearing,
                                      SlidingRead)


#: The band's lower edge: where a dial swept FORWARD comes to rest, one
#: gap below the multiple of 360 it reached.
LOWER = 360.0 - GAP


def reads(node, qualified):
    """The value a coordinate holds, by the qualified id the run banks it
    under -- pixels' own source, since the joint places the body off
    exactly this number."""
    *path, name = qualified.split('.')
    for step in path:
        node = getattr(node, step)
    return get_coordinate(node, name)._value


def sweep(sim, travel, duration=1.0):
    """One clearing sweep of the ring, run to completion."""
    handle = sim.move('ring', by=travel, duration=duration)
    sim.run(duration)
    return handle


def engaged(angle):
    """Whether the fixture's gate reads ENGAGED at `angle` -- the law's
    own arithmetic, restated here so the test never calls the law."""
    shifted = angle + GAP
    return shifted - 360.0 * math.floor(shifted / 360.0) >= 2 * GAP


class ClearingTest(BaseNodeTest):
    """The mechanism: a dial cleared to its gap while the ring runs on."""

    def test_a_wheel_standing_in_its_band_does_not_move(self):
        # Both landings are INSIDE the band, which is `[-GAP, GAP)` about
        # every multiple of 360, so a dial that reached its gap holds in
        # BOTH directions: a missing tooth grips in neither.
        for digit in (360.0 - GAP, 0.0, 360.0):
            with self.subTest(digit=digit):
                self.assertFalse(engaged(digit))

    def test_a_wheel_clears_to_its_gap_and_the_ring_runs_on(self):
        node = Clearing()
        sim = Sim(node, 0.1, record=200)
        handle = sweep(sim, 600.0)

        self.assertEqual(sim.state['ring'], 600.0)
        self.assertEqual(handle.status, 'completed')
        self.assertEqual(sim.state['wheel.turn'], LOWER)
        self.assertEqual(reads(node.wheel, 'turn'), LOWER)
        self.assertFalse(engaged(sim.state['wheel.turn']))

    def test_the_cut_is_a_crossing_and_not_a_stop(self):
        sim = Sim(Clearing(), 0.1, record=200)
        sweep(sim, 600.0)

        self.assertEqual(sim.stops, [])
        gate = [entry for entry in sim.crossings
                if entry.coordinate == 'wheel.turn']
        self.assertTrue(gate)
        for entry in gate:
            with self.subTest(crossing=entry):
                self.assertEqual(entry.relation,
                                 '(setter, ring, wheel.turn) drives wheel.turn')
                self.assertTrue(0.0 <= entry.t <= 1.0)

    def test_sweeping_an_already_cleared_wheel_moves_it_by_nothing(self):
        sim = Sim(Clearing(), 0.1)
        sweep(sim, 600.0)
        landed = sim.state['wheel.turn']

        for again in range(1, 4):
            with self.subTest(sweep=again):
                handle = sweep(sim, 600.0)
                self.assertEqual(handle.status, 'completed')
                # BIT for bit: not merely within the agreement window.
                self.assertEqual(sim.state['wheel.turn'], landed)
        self.assertEqual(sim.state['ring'], 2400.0)

    def test_every_digit_clears_and_none_overruns(self):
        for step in range(10):
            digit = 36.0 * step
            with self.subTest(digit=digit):
                sim = Sim(Clearing(digit=digit), 0.1)
                sweep(sim, 600.0)
                landed = sim.state['wheel.turn']
                if digit == 0.0:
                    self.assertEqual(landed, 0.0)
                    continue
                self.assertEqual(landed, LOWER)
                self.assertFalse(engaged(landed))
                self.assertTrue(engaged(math.nextafter(landed, -math.inf)))

    def test_swept_backward_a_digit_clears_the_short_way(self):
        for step in range(10):
            digit = 36.0 * step
            with self.subTest(digit=digit):
                sim = Sim(Clearing(digit=digit), 0.1,
                          state={'ring': 600.0})
                sweep(sim, -600.0)
                landed = sim.state['wheel.turn']
                if digit == 0.0:
                    self.assertEqual(landed, 0.0)
                    continue
                self.assertLess(landed, GAP)
                self.assertGreater(landed, 0.0)
                self.assertFalse(engaged(landed))
                self.assertTrue(engaged(math.nextafter(landed, math.inf)))
                sweep(sim, -600.0)
                self.assertEqual(sim.state['wheel.turn'], landed)


class CadenceTest(BaseNodeTest):
    """The accuracy contract: one sweep, four cadences, one answer."""

    def _whole(self, dt):
        sim = Sim(Clearing(), dt, record=400)
        handle = sweep(sim, 600.0)
        return sim, handle

    def test_the_same_sweep_at_three_cadences_agrees(self):
        answers = []
        for dt in (1.0, 1.0 / 12.0, 1.0 / 240.0):
            with self.subTest(dt=dt):
                sim, handle = self._whole(dt)
                self.assertEqual(handle.status, 'completed')
                self.assertEqual(sim.stops, [])
                self.assertEqual(handle.admitted, 600.0)
                answers.append((sim.state['wheel.turn'], sim.state['ring']))
        for wheel, ring in answers[1:]:
            self.assertAlmostEqual(wheel, answers[0][0], delta=1e-9)
            self.assertAlmostEqual(ring, answers[0][1], delta=1e-9)

    def test_four_partial_commands_agree_with_one(self):
        whole, handle = self._whole(0.1)

        sim = Sim(Clearing(), 0.1, record=400)
        admitted = 0.0
        for _part in range(4):
            part = sweep(sim, 150.0)
            self.assertEqual(part.status, 'completed')
            admitted += part.admitted

        self.assertAlmostEqual(sim.state['wheel.turn'],
                               whole.state['wheel.turn'], delta=1e-9)
        self.assertAlmostEqual(sim.state['ring'], whole.state['ring'],
                               delta=1e-9)
        self.assertAlmostEqual(admitted, handle.admitted, delta=1e-9)
        self.assertEqual(sim.stops, [])


class DirectionTest(BaseNodeTest):
    """Both directions, reversal, and the rack's own station window."""

    def test_reversal_inside_the_gap_moves_nothing(self):
        sim = Sim(Clearing(), 0.1)
        sweep(sim, 600.0)
        landed = sim.state['wheel.turn']

        back = sweep(sim, -600.0)
        self.assertEqual(sim.state['wheel.turn'], landed)
        self.assertEqual(back.status, 'completed')
        forward = sweep(sim, 600.0)
        self.assertEqual(sim.state['wheel.turn'], landed)
        self.assertEqual(forward.status, 'completed')
        self.assertEqual(sim.stops, [])

    def test_reversal_while_engaged_backs_the_wheel_up(self):
        sim = Sim(Clearing(), 0.1)
        sweep(sim, 200.0)
        part = sim.state['wheel.turn']
        self.assertGreater(part, 108.0)
        self.assertLess(part, LOWER)

        sweep(sim, -100.0)
        self.assertAlmostEqual(sim.state['wheel.turn'], part - 100.0,
                               delta=1e-9)

    def test_a_sweep_short_of_the_station_does_not_touch_the_dial(self):
        sim = Sim(Clearing(), 0.1)
        handle = sweep(sim, 90.0)

        self.assertEqual(sim.state['wheel.turn'], 108.0)
        self.assertEqual(handle.status, 'completed')

    def test_the_station_window_contributes_only_the_travel_inside_it(self):
        # Layer ONE -- a jump over the ring alone -- in the same law as
        # the layer-TWO gate: the dial takes only the sweep between the
        # station's edges, and the two layers compose at any cadence.
        # The station opens at ring 100 and closes at 500.
        for start, travel, expected in ((0.0, 300.0, 200.5),
                                        (400.0, 300.0, 100.5)):
            answers = []
            for dt in (1.0, 1.0 / 12.0, 1.0 / 240.0):
                with self.subTest(start=start, dt=dt):
                    sim = Sim(Clearing(digit=0.5), dt,
                              state={'ring': start})
                    handle = sweep(sim, travel)
                    self.assertEqual(handle.status, 'completed')
                    self.assertAlmostEqual(sim.state['ring'], start + travel,
                                           delta=1e-9)
                    answers.append(sim.state['wheel.turn'])
            self.assertAlmostEqual(answers[0], expected, delta=1e-9)
            for other in answers[1:]:
                self.assertAlmostEqual(other, answers[0], delta=1e-9)


class LandingTest(BaseNodeTest):
    """The FAR-SIDE landing: the float the run commits."""

    def test_the_landing_is_the_nearest_far_side_float(self):
        sim = Sim(Clearing(), 0.1)
        sweep(sim, 600.0)
        landed = sim.state['wheel.turn']

        self.assertFalse(engaged(landed))
        # One float back toward the surface reads ENGAGED, so this is
        # the NEAREST representable value on the far side.
        self.assertTrue(engaged(math.nextafter(landed, -math.inf)))

    def test_the_run_commits_the_landing_and_not_value_plus_delta(self):
        sim = Sim(Clearing(), 0.1)
        sweep(sim, 600.0)
        landed = sim.state['wheel.turn']

        for again in range(3):
            with self.subTest(tick=again):
                sim.move('ring', by=60.0, duration=0.1)
                sim.run(0.1)
                self.assertEqual(sim.state['wheel.turn'], landed)

    def test_both_directions_land_on_their_own_edge_of_the_band(self):
        forward = Sim(Clearing(), 0.1)
        sweep(forward, 600.0)
        backward = Sim(Clearing(), 0.1, state={'ring': 600.0})
        sweep(backward, -600.0)

        self.assertGreater(forward.state['wheel.turn'], 360.0 - 2 * GAP)
        self.assertLess(forward.state['wheel.turn'], 360.0)
        self.assertGreater(backward.state['wheel.turn'], 0.0)
        self.assertLess(backward.state['wheel.turn'], GAP)


class OnSurfaceTest(BaseNodeTest):
    """A dial standing EXACTLY on a band edge."""

    def test_a_wheel_on_a_band_edge_is_not_driven_through_it(self):
        # `360 + GAP` is the band's far edge, where the gate's own `>=`
        # sits EXACTLY on its surface and the operator reads ENGAGED.
        # Swept BACKWARD the level leaves the surface into the
        # disengaged region at once: without the flip at the piece's
        # left end there is no crossing to find -- the level leaves the
        # surface rather than reaching it -- and the piece would be
        # integrated engaged, driving the dial straight through its gap.
        edge = 360.0 + GAP
        self.assertTrue(engaged(edge))

        backward = Sim(Clearing(digit=edge), 0.1, state={'ring': 600.0})
        sweep(backward, -600.0)
        self.assertEqual(backward.state['wheel.turn'], edge)

        # Swept the other way the same dial turns, and stops at the NEXT
        # gap rather than running on.
        forward = Sim(Clearing(digit=edge), 0.1)
        sweep(forward, 600.0)
        self.assertEqual(forward.state['wheel.turn'], 720.0 - GAP)

    def test_a_rest_default_on_a_digit_boundary_holds(self):
        # The exact surface of the gate's own comparison: `wheel + GAP`
        # a whole multiple of 360, which is where a rest default landing
        # on a digit boundary puts the dial.
        sim = Sim(Clearing(digit=360.0 - GAP), 0.1)
        sweep(sim, 600.0)

        self.assertEqual(sim.state['wheel.turn'], 360.0 - GAP)

    def test_a_sliding_mode_refuses_the_tick(self):
        sim = Sim(SlidingRead(), 1.0)
        before = dict(sim.state)
        handle = sim.move('ring', by=10.0, duration=1.0)
        with self.assertRaises(UnsupportedLaw) as caught:
            sim.run(1.0)

        message = str(caught.exception)
        self.assertIn('wheel.turn', message)
        self.assertIn('>=', message)
        self.assertIn('sliding mode', message)
        self.assertEqual(sim.state, before)
        self.assertEqual(sim.tick, 0)
        self.assertEqual(handle.status, 'refused')


class NearSurfaceTest(BaseNodeTest):
    """A dial engaged by a HAIR: a genuine crossing a float's width
    inside the piece's left end.

    A rest default, a restore, or a bound a stop committed can leave a
    dial a hair SHORT of its gap rather than exactly on it. It is not ON
    the surface, so rule (c) does not flip it, and its crossing sits at
    a fraction of the tick of the order of `1e-16`. Dropping it
    integrates the piece ENGAGED and drives the dial straight through
    its gap -- which design.md section 3's rule (d) forbids, and which
    the solved path never did.
    """

    #: Engaged by a hundred-billionth of a degree.
    HAIR = 1e-11

    def test_a_dial_engaged_by_a_hair_stops_at_its_gap(self):
        # The SEARCHED shape: the Curta's own `clamp01` window, where
        # the crossing is bisected rather than solved.
        digit = 360.0 - GAP - self.HAIR
        self.assertTrue(engaged(digit))

        sim = Sim(CurtaInterface(digit=digit), 1.0 / 60.0)
        sim.move('clearing', by=1.0, duration=1.0)
        sim.run(1.0)

        self.assertEqual(sim.state['result0.turn'], LOWER)

    def test_the_solved_shape_is_the_control(self):
        # The same hair on the affine fixture, where the crossing is
        # SOLVED: this one already held.
        digit = 360.0 - GAP - self.HAIR
        sim = Sim(Clearing(digit=digit), 0.1)
        sweep(sim, 600.0)

        self.assertEqual(sim.state['wheel.turn'], LOWER)


class CrowdedTest(BaseNodeTest):
    """A gate whose read changes the dial's RATE rather than stopping
    it.

    `crowded_gate` turns the wheel two units per unit of ring over the
    first half of every tooth and one over the second, through a
    `clamp01` window whose skeleton is NOT affine -- so every crossing
    falls to the sampled search, and the wheel crosses a surface twice
    per unit of its own travel. A mechanism that keeps moving after it
    trips is what the searched walk has to get right: no piece here ever
    stands still on the surface it was landed at.
    """

    #: Sixty of ring is eighty of wheel: half of every tooth taken at
    #: two units of ring per unit of wheel and half at one, so three
    #: quarters of a unit of ring per unit of wheel.
    TRAVEL = 80.0

    def sweep(self, by, ticks):
        sim = Sim(CrowdedClearing(), 1.0, record=4000)
        for _tick in range(ticks):
            sim.move('ring', by=by / ticks, duration=1.0)
            sim.run(1.0)
        return sim

    def test_the_same_sweep_at_two_cadences_agrees(self):
        for by in (60.0, -60.0):
            with self.subTest(by=by):
                answers = []
                for ticks in (1, 60):
                    sim = self.sweep(by, ticks)
                    self.assertAlmostEqual(sim.state['ring'], by, delta=1e-9)
                    landed = sim.state['wheel.turn']
                    self.assertAlmostEqual(landed,
                                           math.copysign(self.TRAVEL, by),
                                           delta=1e-7)
                    # Two surfaces per unit of the wheel's own travel:
                    # the floor's integer and the comparison's half.
                    cuts = [entry for entry in sim.crossings
                            if entry.coordinate == 'wheel.turn']
                    self.assertAlmostEqual(len(cuts), 2 * self.TRAVEL,
                                           delta=4)
                    answers.append(landed)
                first, second = answers
                self.assertLessEqual(
                    abs(first - second),
                    1e-9 * max(1.0, abs(first), abs(second)))

    def test_a_tick_cut_too_many_times_is_refused(self):
        sim = Sim(CrowdedClearing(), 1.0)
        before = dict(sim.state)
        # Six hundred of ring is eight hundred of wheel and sixteen
        # hundred surfaces: a dt that is not resolving the mechanism.
        handle = sim.move('ring', by=600.0, duration=1.0)
        with self.assertRaises(TooManyCrossings) as caught:
            sim.run(1.0)

        message = str(caught.exception)
        self.assertIn('wheel.turn', message)
        # The two surfaces alternate from a dial standing at zero, so
        # the thousand and first is the comparison's and not the
        # floor's.
        self.assertIn('>=', message)
        self.assertIn('1001', message)
        self.assertIn('(ring, wheel.turn) drives wheel.turn', message)
        self.assertEqual(sim.state, before)
        self.assertEqual(sim.tick, 0)
        self.assertEqual(handle.status, 'refused')


class KnifeEdgeTest(BaseNodeTest):
    """A gate whose DISENGAGED state is a single value of the
    coordinate -- a gap with no width.

    This is NOT a requirement scenario: a requirement does not promise a
    failure. It pins only what the framework promises -- the dial holds
    where the far side of the surface is the disengaged region -- and
    records that the disengaged set here is ONE float, so the model has
    nothing to stand on. `docs/scenarios.rst` says a gap has WIDTH, and
    the reduced fixture of `Clearing` states one.
    """

    def test_the_disengaged_set_of_a_knife_edge_is_one_float(self):
        sim = Sim(KnifeEdge(), 0.1)
        sweep(sim, 600.0)
        landed = sim.state['wheel.turn']

        def free(angle):
            return not (angle - 360.0 * math.floor(angle / 360.0) > 0)

        self.assertTrue(free(landed))
        self.assertFalse(free(math.nextafter(landed, math.inf)))
        self.assertFalse(free(math.nextafter(landed, -math.inf)))

    def test_the_knife_edge_holds_where_its_far_side_is_disengaged(self):
        sim = Sim(KnifeEdge(), 0.1)
        sweep(sim, 600.0)
        landed = sim.state['wheel.turn']
        sweep(sim, 600.0)

        self.assertEqual(sim.state['wheel.turn'], landed)


class TickCompositionTest(BaseNodeTest):
    """Stops, constraints, several dials and a refused tick."""

    def test_a_declared_range_on_the_dial_stops_it_at_its_bound(self):
        sim = Sim(RangedClearing(), 0.1, record=200)
        handle = sweep(sim, 600.0)

        self.assertEqual(sim.state['wheel.turn'], 300.0)
        self.assertEqual(handle.status, 'blocked')
        self.assertEqual([stop.coordinate for stop in sim.stops],
                         ['wheel.turn'])
        self.assertEqual(sim.stops[0].value, 300.0)

    def test_a_declared_range_on_the_ring_still_blocks(self):
        sim = Sim(BlockedRing(), 0.1, record=200)
        handle = sim.move('crank', by=600.0, duration=1.0)
        sim.run(1.0)

        self.assertEqual(sim.state['ring.turn'], 200.0)
        self.assertEqual(handle.status, 'blocked')
        self.assertEqual(handle.admitted, 200.0)
        self.assertEqual([stop.coordinate for stop in sim.stops],
                         ['ring.turn'])
        # The dial cleared only as far as the admitted sweep carried it.
        self.assertEqual(sim.state['wheel.turn'], 308.0)

    def test_a_bound_reading_a_self_read_coordinate_samples_correctly(self):
        sim = Sim(LatchedClearing(), 0.1, record=200)
        sim.move('push', by=30.0, duration=1.0)
        sim.move('ring', by=600.0, duration=1.0)
        sim.run(1.0)

        self.assertTrue(sim.stops)
        self.assertEqual(sim.stops[0].coordinate, 'latch')
        self.assertLessEqual(sim.state['latch'], 20.0)
        self.assertLess(sim.state['wheel.turn'], 180.0 + 1e-6)

    def test_several_wheels_clear_independently_from_one_ring(self):
        sim = Sim(ClearingRow(), 0.1, record=400)
        handle = sweep(sim, 1150.0)

        self.assertEqual(handle.status, 'completed')
        self.assertEqual(sim.state['first.turn'], 0.0)
        self.assertEqual(sim.state['second.turn'], LOWER)
        self.assertEqual(sim.state['third.turn'], LOWER)
        self.assertEqual(sim.state['fourth.turn'], 324.0)
        self.assertEqual(sim.stops, [])

    def test_a_tick_that_fails_after_a_cut_commits_nothing(self):
        node = RefusedClearing()
        sim = Sim(node, 0.1, record=200)
        before = dict(sim.state)
        ring = sim.move('ring', by=600.0, duration=1.0)
        wrist = sim.move('wrist_in', by=10.0, duration=1.0)
        with self.assertRaises(RunConflict):
            sim.run(0.1)

        self.assertEqual(sim.state, before)
        self.assertEqual(sim.tick, 0)
        self.assertEqual(sim.crossings, [])
        self.assertEqual(reads(node.wheel, 'turn'), before['wheel.turn'])
        self.assertEqual(ring.status, 'refused')
        self.assertEqual(wrist.status, 'refused')


class RetentionTest(BaseNodeTest):
    """The retained value across inspection, snapshot and restore."""

    def test_a_partial_sweep_is_retained_and_resumes(self):
        node = Clearing()
        sim = Sim(node, 0.1, record=200)
        sweep(sim, 220.0)
        part = sim.state['wheel.turn']
        self.assertAlmostEqual(part, 228.0, delta=1e-9)

        state = sim.state
        node.render()
        snapshot = sim.snapshot()
        self.assertEqual(sim.state, state)
        sim.restore(snapshot)
        self.assertEqual(sim.state, state)

        sweep(sim, 380.0)
        self.assertEqual(sim.state['wheel.turn'], LOWER)

    def test_the_bank_value_held_at_a_gate_survives_a_restore(self):
        sim = Sim(Clearing(), 0.1, record=200)
        sweep(sim, 600.0)
        landed = sim.state['wheel.turn']
        snapshot = sim.snapshot()

        sweep(sim, 600.0)
        sim.restore(snapshot)
        self.assertEqual(sim.state['wheel.turn'], landed)

        sweep(sim, 600.0)
        self.assertEqual(sim.state['wheel.turn'], landed)

    def test_reset_returns_the_dial_to_its_rest_default(self):
        sim = Sim(Clearing(), 0.1, record=200)
        sweep(sim, 600.0)
        sim.reset()

        self.assertEqual(sim.state['wheel.turn'], 108.0)
        self.assertEqual(sim.state['ring'], 0.0)
        self.assertEqual(sim.crossings, [])


class HeldValueTest(BaseNodeTest):
    """A piece whose skeleton does not move leaves the coordinate at the
    EXACT float it held.

    The walk reads the driven end's own path as
    ``own_left + (S(s) - base)``: the difference is taken FIRST, so a
    skeleton that is unchanged over the piece adds a true zero. Read the
    other way round -- ``(own_left + S) - base``, which is how Python
    takes the expression without the parentheses -- the sum rounds
    whenever ``|S|`` is comparable to ``|own_left|``, and the coordinate
    moves by an ulp for no mechanical reason at all.
    """

    def test_a_tick_that_moves_only_an_outer_source_holds_the_angle(self):
        sim = Sim(HeldAngle(), 1.0, record=8)
        held = sim.state['wheel.turn']
        self.assertEqual(held, 71.99999999999996)

        # The lift's own comparison is an OUTER node: moving it
        # re-partitions the tick while every term of the substituted law
        # stands exactly where it stood.
        sim.move('lift', by=0.2, duration=1.0)
        sim.run(1.0)

        self.assertEqual(sim.state['wheel.turn'], held)
        self.assertEqual(reads(sim.node, 'wheel.turn'), held)


class CurtaShapeTest(BaseNodeTest):
    """The originating machine's own shape, on its own numbers.

    `tests/clearing_project/machine.py` is the Curta's clearing
    interface reduced: two nine-tooth racks on opposite halves of one
    ring, the project's measured starts, pitches and stations, and the
    ring angle taken over the middle 80 % of the clearing control -- a
    `clamp01` window, so the law's skeleton is NOT affine and every
    self-read crossing here falls to the sampled search.

    The expected values are restated from the rack's own arithmetic, not
    read back from the law.
    """

    def clear(self, dt=1.0 / 60.0, by=1.0, sim=None):
        if sim is None:
            sim = Sim(CurtaInterface(), dt)
        handle = sim.move('clearing', by=by, duration=1.0)
        sim.run(1.0)
        return sim, handle

    def test_every_dial_clears_to_its_gap(self):
        sim, handle = self.clear()

        self.assertEqual(handle.status, 'completed')
        for index in range(6):
            name = ('result0', 'result1', 'result2',
                    'counter0', 'counter1', 'counter2')[index]
            with self.subTest(dial=name):
                # Nine teeth of 36 degrees is 324 degrees of travel, and
                # this dial rests at 36 * (index + 1), so the gap at 360
                # is within reach of every one of them.
                rest = TOOTH * (index + 1)
                self.assertLessEqual(360.0 - rest - GAP, TEETH * TOOTH)
                self.assertEqual(sim.state[f'{name}.turn'], 360.0 - GAP)

    def test_a_cleared_register_does_not_un_clear_when_the_ring_returns(self):
        sim, _handle = self.clear()
        cleared = dict(sim.state)

        sim, handle = self.clear(by=-1.0, sim=sim)
        self.assertEqual(handle.status, 'completed')
        for name, value in cleared.items():
            with self.subTest(coordinate=name):
                if name == 'clearing':
                    continue
                self.assertEqual(sim.state[name], value)

    def test_a_partial_sweep_is_retained_and_resumes(self):
        sim = Sim(CurtaInterface(), 1.0 / 60.0)
        sim.move('clearing', by=0.5, duration=1.0)
        sim.run(1.0)
        part = dict(sim.state)
        # The counter row's stations are the LAST the ring reaches.
        self.assertNotEqual(part['counter0.turn'], 360.0 - GAP)

        sim.move('clearing', by=0.5, duration=1.0)
        sim.run(1.0)
        for index in range(6):
            name = ('result0', 'result1', 'result2',
                    'counter0', 'counter1', 'counter2')[index]
            with self.subTest(dial=name):
                self.assertEqual(sim.state[f'{name}.turn'], 360.0 - GAP)


class BlockSelfReadTest(BaseNodeTest):
    """A BLOCK member that also reads the coordinate it drives (OpenSpec
    change ``select-the-source``).

    Three layers now, and the first two were already here: the block's
    SELECTORS, forced and constant on each piece; ADR-107's independent
    partition inside it; and the walk of the nodes that depend on the
    driven end. The split of the last two is decided ONCE at compile with
    the selectors still SYMBOLIC, so a law with no block is partitioned
    exactly as it was.
    """

    def test_a_selector_piece_and_a_self_read_cut_are_both_recorded(self):
        from .carriage_project.machine import LandedCarry

        sim = Sim(LandedCarry(), 1.0, record=8)
        sim.move('crank', by=4.0, duration=1.0)
        sim.move('shift', by=1.0, duration=1.0)
        sim.run(1.0)
        self.assertEqual(
            [(one.coordinate, one.primitive, one.t) for one in sim.crossings],
            [('carry.travel', '<', 0.25), ('higher.turn', '>=', 0.25),
             ('higher.turn', '<', 0.5), ('carry.travel', '<', 0.5)])
        # The lever's own gate cut the first piece at a quarter of the
        # tick and the carriage's detent cut the stretch at its half.
        self.assertEqual(sim.state['carry.travel'], 3.0)

    def test_the_walk_leaves_the_latch_at_its_far_side(self):
        from .carriage_project.machine import LandedCarry

        sim = Sim(LandedCarry(), 0.5, record=8)
        sim.move('crank', by=4.0, duration=1.0)
        sim.move('shift', by=1.0, duration=1.0)
        sim.run(0.5)
        # The piece before the detent lands the lever at its gate, and
        # the run commits the float the walk left it at.
        self.assertEqual(sim.state['carry.travel'], 1.0)
        self.assertEqual(reads(sim.node, 'carry.travel'), 1.0)

    def test_the_two_layer_split_is_decided_once_with_selectors_symbolic(
            self):
        from .carriage_project.machine import ShiftedCarry

        sim = Sim(ShiftedCarry(), 0.02)
        block, = [edge for edge in sim._run.program.edges
                  if edge.kind == 'block']
        wheel, lever = block.block.members
        # The wheel's own `higher.turn > 0.5` is the only DEPENDENT node;
        # its two selectors and the lever's gate are independent, which is
        # what puts a forced selector in layer one and nowhere else.
        self.assertEqual(
            [jump.placeholder for jump in wheel.retained[0].dependent],
            ['$j3'])
        self.assertEqual(
            [jump.placeholder for jump in wheel.retained[0].outer.jumps],
            ['$j0', '$j1', '$j2'])
        self.assertEqual(
            [jump.placeholder for jump in lever.retained[0].dependent],
            ['$j2'])
        self.assertEqual(
            [jump.placeholder for jump in lever.retained[0].outer.jumps],
            ['$j0', '$j1'])

    def test_a_law_with_no_block_is_partitioned_exactly_as_before(self):
        sim = Sim(CurtaInterface(), 0.05)
        edge = next(one for one in sim._run.program.edges
                    if one.kind == 'law' and 'result0.turn' in one.driven)
        reading = edge.retained[0]
        self.assertEqual(len(reading.dependent), 2)
        self.assertEqual(len(reading.outer.jumps), 2)
        self.assertEqual(
            [edge.kind for edge in sim._run.program.edges],
            ['law'] * 6)


class KinkedSkeletonTest(BaseNodeTest):
    """A KINKED skeleton is cut at its kinks and solved.

    OpenSpec change ``cut-at-the-kink``, design.md section 11 case B.
    ``CurtaInterface``'s ring angle is
    ``ORIGIN + SWEEP * clamp01((control - 0.1) / 0.8)``: piecewise
    affine, three affine pieces, and until this cycle non-affine to
    ``_affine_in_sources``, so every one of its six dials' self-read
    crossings was bracketed and bisected although the level was affine
    and an exact path existed.
    """

    DT = 1.0 / 60.0

    def swept(self, record=4000):
        sim = Sim(CurtaInterface(), self.DT, record=record)
        sim.move('clearing', by=1.0, duration=1.0)
        return sim

    def test_the_first_dials_mesh_is_located_exactly(self):
        """The fixture's own arithmetic, in EXACT rational numbers:
        `result0`'s rack meshes where `ring_angle(control)` reaches the
        dial's station, which is
        `control == 0.1 + 0.8 * (start - ORIGIN) / SWEEP`. The clamp is
        strictly inside its window through the whole of that tick, so
        the level is affine there and the crossing has a closed form.

        The SEARCH reached it 9.3e-14 out -- six thousand times the
        float spacing at `0.1`. The solve reaches it to within the
        rounding the LEVEL's own evaluation carries, which is what is
        left when the localization adds nothing of its own.
        """
        from fractions import Fraction

        sim = self.swept()
        sim.run(1.0)
        start = RESULT_START + station(0, False)
        control = 0.1 + 0.8 * (start - ORIGIN) / SWEEP
        tick = int(control / self.DT) + 1
        reach = (Fraction(0.8) * (Fraction(start) - Fraction(ORIGIN))
                 / Fraction(SWEEP))
        left = Fraction(tick - 1) * Fraction(self.DT)
        exact = float((Fraction(0.1) + reach - left) / Fraction(self.DT))
        found = [one.t for one in sim.crossings
                 if one.coordinate == 'result0.turn' and one.tick == tick]
        self.assertEqual(len(found), 1)
        self.assertLess(abs(found[0] - exact), 1e-15)

    def test_the_sweep_costs_a_solve_and_not_a_search(self):
        """The cost the classification buys, in the run's own units: the
        searched kinked skeleton paid 2 861 expression evaluations per
        tick over this sweep, where `Clearing`'s affine one pays 98.6."""
        sim = self.swept(record=None)
        self.assertLess(expression_evaluations(sim, 60) / 60.0, 900.0)
        quiet = Sim(Clearing(), 0.1, record=None)
        quiet.move('ring', by=600.0, duration=1.0)
        # Exactly what an affine skeleton paid before this cycle: a
        # machine with no kink in any followed quantity meets no new
        # code at all.
        self.assertEqual(expression_evaluations(quiet, 10), 986)
