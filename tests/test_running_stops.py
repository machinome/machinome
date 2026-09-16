# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""A joint's range is a physical stop located inside the tick.

OpenSpec change ``ranges-are-stops``, cycle 3 of the open-run campaign.
Cycles 1 and 2 failed the whole tick when a banked joint coordinate would
leave its declared range. Here the range is read as the mechanical limit
it states: the run locates the fraction ``t*`` of the tick at which the
coordinate reaches its bound, commits it AT that bound, stops every input
whose movement pushes it, lets everything else run its full tick, and
retires the pushing commands ``blocked`` with the travel they actually
admitted.

The two originating mechanisms are here with their own numbers: the
Pascaline module's ratchet, whose lower bound is an expression over its
own coordinate -- the last seated tooth -- and the spike's swept stop,
where a rack stops at its limit while an unrelated motor runs on.

Nothing here changes what an untimed or looping root does, which
``UntimedControlTest`` pins directly and the untouched suites pin at
large: there a range still REFUSES a binding outside it and never clamps
or stops.
"""

from pytest import approx

from solid_node.motion.joints import JointRangeError
from solid_node.motion.ports import get_coordinate
from solid_node.simulation import (RunConflict, Sim, Stop,
                                   UnsupportedLaw)

from .base import BaseNodeTest, graph_evaluations
from .running_project.machine import (ConstantBound, UnusedRead,
                                      Captured, ClassGate, Curved, CurvedBody,
                                      DriverGate, Gate, GateWide,
                                      ImpossibleBoundBody, KinkedStop,
                                      LoopingTrain,
                                      OpenGate, OpenGateBody, OpenLowBody,
                                      PawlRatchet, PortRead, Ratchet,
                                      RatchetBody, Shared, SharedBody,
                                      StopAndJump, StopAndJumpBody,
                                      StoppedClearing,
                                      StoppedDifferential, Swept, SweptBody,
                                      SweptWide, Train, TwoStops, TwoStopsBody)


def reads(node, qualified):
    """The value a coordinate holds, by the qualified id the run banks it
    under -- pixels' own source, since the joint places the body off
    exactly this number."""
    *path, name = qualified.split('.')
    for step in path:
        node = getattr(node, step)
    return get_coordinate(node, name)._value


def key_of(program, name):
    """The program node key of a coordinate, by its qualified id."""
    for key, node in program.nodes.items():
        if node.name == name:
            return key
    raise AssertionError(f'no program node called {name}')


def sources_of(sim, name):
    """The CANDIDATE inputs the compiled program says reach `name`."""
    return sim.program.sources[key_of(sim.program, name)]


def span_names(sim, identifier, side):
    """The free names a compiled bound reads, sorted."""
    from solid_node.expression_graph import free_names
    from solid_node.scad_expression import as_node

    for entry in sim.program.spans:
        if entry[0] == identifier:
            graph = entry[1] if side == 'low' else entry[2]
            return sorted(free_names(as_node(graph)))
    raise AssertionError(f'no span for {identifier}')


class RatchetTest(BaseNodeTest):
    """(2) The worked example of design.md section 11, with its numbers.

    Forward rotation from the seated tooth is free; the reverse that
    follows blocks at the same tooth, admitting exactly what it had
    gained. That is retention.
    """

    def test_forward_from_the_seated_tooth_is_free(self):
        node = Ratchet()
        sim = Sim(node, 0.1, record=8)
        handle = sim.move('arbor', by=20.0, duration=0.1)
        sim.run(0.1)
        self.assertEqual(sim.state['wheel.turn'], 60.0)
        self.assertEqual(reads(node, 'wheel.turn'), 60.0)
        self.assertEqual(handle.status, 'completed')
        self.assertEqual(handle.admitted, 20.0)
        self.assertEqual(sim.stops, [])

    def test_a_reverse_blocks_at_the_last_seated_tooth(self):
        node = Ratchet()
        sim = Sim(node, 0.1, record=8)
        handle = sim.move('arbor', by=-10.0, duration=0.1)
        sim.run(0.1)
        self.assertEqual(sim.state['wheel.turn'], 36.0)
        self.assertEqual(sim.state['arbor'], 36.0)
        self.assertEqual(reads(node, 'wheel.turn'), 36.0)
        self.assertEqual(handle.status, 'blocked')
        self.assertEqual(handle.admitted, -4.0)
        self.assertEqual(handle.requested, -10.0)
        self.assertEqual(sim.tick, 1)
        self.assertEqual(sim.commands, ())
        stop, = sim.stops
        self.assertEqual(stop.coordinate, 'wheel.turn')
        self.assertEqual(stop.t, 0.4)

    def test_the_retention_sequence(self):
        """The last three rows of the table, read down: blocked at the
        tooth, free forward off it, blocked at it again."""
        sim = Sim(Ratchet(), 0.1, record=8)
        first = sim.move('arbor', by=-10.0, duration=0.1)
        sim.run(0.1)
        self.assertEqual((first.status, first.admitted), ('blocked', -4.0))

        again = sim.move('arbor', by=-10.0, duration=0.1)
        sim.run(0.1)
        self.assertEqual(sim.state['wheel.turn'], 36.0)
        self.assertEqual((again.status, again.admitted), ('blocked', 0.0))

        forward = sim.move('arbor', by=4.0, duration=0.1)
        sim.run(0.1)
        self.assertEqual(sim.state['wheel.turn'], 40.0)
        self.assertEqual((forward.status, forward.admitted),
                         ('completed', 4.0))

        back = sim.move('arbor', by=-10.0, duration=0.1)
        sim.run(0.1)
        self.assertEqual(sim.state['wheel.turn'], 36.0)
        self.assertEqual((back.status, back.admitted), ('blocked', -4.0))

    def test_a_push_from_the_stop_is_accepted_and_retires_at_once(self):
        """(5) A new command on a stopped input is accepted at once, and
        blocked in the tick it was issued with nothing admitted."""
        sim = Sim(Ratchet(), 0.1, record=8, state={'arbor': 36.0})
        handle = sim.move('arbor', by=-10.0, duration=0.1)
        self.assertEqual(handle.status, 'active')
        sim.run(0.1)
        self.assertEqual(handle.status, 'blocked')
        self.assertEqual(handle.admitted, 0.0)
        self.assertEqual(sim.state['wheel.turn'], 36.0)
        self.assertEqual(sim.commands, ())
        stop, = sim.stops
        self.assertEqual(stop.t, 0.0)
        # And the input is free at once: no ownership error.
        after = sim.move('arbor', by=4.0, duration=0.1)
        sim.run(0.1)
        self.assertEqual((after.status, after.admitted), ('completed', 4.0))

    def test_the_tooth_advances_with_the_arbor(self):
        sim = Sim(Ratchet(), 0.1, record=8, state={'arbor': 75.0})
        handle = sim.move('arbor', by=-10.0, duration=0.1)
        sim.run(0.1)
        self.assertEqual(sim.state['wheel.turn'], 72.0)
        self.assertEqual((handle.status, handle.admitted), ('blocked', -3.0))

    def test_a_blocked_command_never_resumes(self):
        sim = Sim(Ratchet(), 0.1, record=8)
        handle = sim.move('arbor', by=-10.0, duration=0.1)
        sim.run(0.1)
        sim.run(1.0)
        self.assertEqual(sim.state['wheel.turn'], 36.0)
        self.assertEqual(handle.status, 'blocked')
        self.assertEqual(handle.admitted, -4.0)
        self.assertEqual(sim.commands, ())
        self.assertEqual(len(sim.stops), 1)

    def test_a_reverse_rate_blocks_too(self):
        """A rate is not a promise of a total, but it is a command, and
        the run will not let a machine push silently against a stop for
        ever. (At -40 deg/s the first tick lands on exactly 36, which is
        INSIDE the inclusive bound and no stop at all; -50 overshoots
        it.)"""
        sim = Sim(Ratchet(), 0.1, record=8)
        steady = Sim(Ratchet(), 0.1, record=8)
        landing = steady.rate('arbor', -40.0)
        steady.run(0.1)
        self.assertEqual(steady.state['wheel.turn'], 36.0)
        self.assertEqual(landing.status, 'active')
        self.assertEqual(steady.stops, [])

        handle = sim.rate('arbor', -50.0)
        sim.run(0.1)
        self.assertEqual(sim.state['wheel.turn'], 36.0)
        self.assertEqual(handle.status, 'blocked')
        self.assertEqual(handle.admitted, -4.0)
        self.assertEqual(sim.commands, ())


class CadenceTest(BaseNodeTest):
    """(12) A stop admits the same travel at any cadence."""

    def test_the_same_reverse_move_at_three_cadences(self):
        for duration, ticks, blocking, fraction in ((0.1, 1, 1, 0.4),
                                                    (0.4, 4, 2, 0.6),
                                                    (4.0, 40, 17, 0.0)):
            with self.subTest(ticks=ticks):
                sim = Sim(Ratchet(), 0.1, record=64)
                handle = sim.move('arbor', by=-10.0, duration=duration)
                sim.run(duration)
                self.assertEqual(sim.state['wheel.turn'], 36.0)
                self.assertEqual(handle.status, 'blocked')
                self.assertEqual(handle.admitted, -4.0)
                stop, = sim.stops
                self.assertEqual(stop.tick, blocking)
                self.assertEqual(stop.t, fraction)

    def test_the_tick_that_lands_on_the_bound_is_ordinary(self):
        """Tick 16 of the forty-tick run lands on exactly 36, which is
        INSIDE the inclusive bound: no stop, and the command still
        active."""
        sim = Sim(Ratchet(), 0.1, record=64)
        handle = sim.move('arbor', by=-10.0, duration=4.0)
        sim.run(1.6)
        self.assertEqual(sim.tick, 16)
        self.assertEqual(sim.state['wheel.turn'], 36.0)
        self.assertEqual(handle.status, 'active')
        self.assertEqual(sim.stops, [])
        sim.run(0.1)
        self.assertEqual(handle.status, 'blocked')
        self.assertEqual(len(sim.stops), 1)


class SweptStopTest(BaseNodeTest):
    """(3) The spike's swept stop: the rack stops at its bound inside the
    tick while an independent motor runs its full tick."""

    def test_the_rack_stops_and_the_motor_continues(self):
        node = Swept()
        sim = Sim(node, 0.1, record=8)
        motor = sim.rate('motor', 90.0)
        steer = sim.move('steer', by=10.0, duration=0.1)
        sim.run(0.1)
        self.assertEqual(sim.state['rack.travel'], 50.0)
        self.assertEqual(reads(node, 'rack.travel'), 50.0)
        self.assertEqual(sim.state['wheel.turn'], 27.0)
        self.assertEqual((steer.status, steer.admitted), ('blocked', 5.0))
        self.assertEqual(motor.status, 'active')
        self.assertEqual(sim.commands, (motor,))
        stop, = sim.stops
        self.assertEqual(stop.coordinate, 'rack.travel')
        self.assertEqual(stop.t, 0.5)
        self.assertEqual(stop.inputs, ('steer',))

    def test_the_rack_holds_while_the_wheel_goes_on_turning(self):
        sim = Sim(Swept(), 0.1, record=8)
        sim.rate('motor', 90.0)
        sim.move('steer', by=10.0, duration=0.1)
        sim.run(0.1)
        sim.run(1.0)
        self.assertEqual(sim.state['rack.travel'], 50.0)
        self.assertEqual(sim.state['wheel.turn'], 297.0)
        self.assertEqual(len(sim.stops), 1)

    def test_an_instruction_reports_each_input_for_itself(self):
        sim = Sim(Swept(), 0.1, record=8)
        blocked, free = sim.trigger('Sweep')
        sim.run(0.1)
        self.assertEqual(blocked.input, 'steer')
        self.assertEqual((blocked.status, blocked.admitted), ('blocked', 5.0))
        self.assertEqual((free.status, free.admitted), ('completed', 9.0))
        self.assertEqual(sim.state['wheel.turn'], 27.0)


class SharedCoordinateTest(BaseNodeTest):
    """(6) A coordinate determined by a stopped input and a free one
    keeps moving on what the free one contributes."""

    def test_the_free_input_goes_on_contributing(self):
        sim = Sim(Shared(), 1.0, record=8)
        a_handle = sim.move('a_in', by=4.0, duration=1.0)
        b_handle = sim.move('b_in', by=6.0, duration=1.0)
        sim.run(1.0)
        self.assertEqual(sim.state['c.turn'], 10.0)
        self.assertEqual((a_handle.status, a_handle.admitted),
                         ('blocked', 2.0))
        self.assertEqual((b_handle.status, b_handle.admitted),
                         ('completed', 6.0))
        # 2*2 + 3*3 over segment A, then 3*3 over segment B: 22, not the
        # 26 an unstopped tick gives and not the 13 of segment A alone.
        self.assertEqual(sim.state['d.turn'] - 16.0, 22.0)
        stop, = sim.stops
        self.assertEqual(stop.inputs, ('a_in',))


class TwoStopsTest(BaseNodeTest):
    """(7) Two stops in one tick, taken earliest first."""

    def test_both_groups_stop_at_their_own_fraction(self):
        for order in ('lever first', 'rack first'):
            with self.subTest(order=order):
                sim = Sim(TwoStops(), 1.0, record=8)
                if order == 'lever first':
                    lever = sim.move('lever_in', by=8.0, duration=1.0)
                    rack = sim.move('steer', by=10.0, duration=1.0)
                else:
                    rack = sim.move('steer', by=10.0, duration=1.0)
                    lever = sim.move('lever_in', by=8.0, duration=1.0)
                sim.run(1.0)
                self.assertEqual(sim.state['lever.turn'], 20.0)
                self.assertEqual(sim.state['rack.travel'], 50.0)
                self.assertEqual((lever.status, lever.admitted),
                                 ('blocked', 2.0))
                self.assertEqual((rack.status, rack.admitted),
                                 ('blocked', 5.0))
                self.assertEqual([(stop.coordinate, stop.t)
                                  for stop in sim.stops],
                                 [('lever.turn', 0.25), ('rack.travel', 0.5)])


class StopAndJumpTest(BaseNodeTest):
    """(8) A stop and a jump crossing in one tick: the crossing is
    recorded at its fraction OF THE TICK, not of the segment."""

    def test_the_crossing_is_rescaled_to_the_tick(self):
        node = StopAndJump()
        sim = Sim(node, 1.0, record=8)
        handle = sim.move('crank', by=20.0, duration=1.0)
        sim.run(1.0)
        self.assertEqual(sim.state['first.turn'], 145.0)
        self.assertEqual(sim.state['folder.turn'] - 80.0, 30.0)
        self.assertEqual((handle.status, handle.admitted), ('blocked', 15.0))
        crossing, = sim.crossings
        self.assertEqual(crossing.primitive, 'ceil')
        self.assertEqual(crossing.t, approx(0.25, abs=1e-12))
        stop, = sim.stops
        self.assertEqual(stop.t, 0.75)


class CurvedStopTest(BaseNodeTest):
    """(6b) A stop on a chain that is NOT affine is found by search."""

    def test_the_searched_fraction_matches_the_computed_root(self):
        sim = Sim(Curved(), 1.0, record=8)
        handle = sim.move('crank', by=40.0, duration=1.0)
        sim.run(1.0)
        self.assertEqual(sim.state['dial.turn'], 20.0)
        # 40*sin(x) reaches 20 at x == 30 degrees, which is 30/40 of
        # the way along a tick that travels 40 degrees -- a root the
        # search has to find, because the law is not affine in x.
        stop, = sim.stops
        self.assertEqual(stop.t, approx(30.0 / 40.0, abs=1e-9))
        self.assertEqual(handle.admitted, approx(30.0, abs=1e-8))
        self.assertEqual(handle.status, 'blocked')

    def test_the_classification_is_read_off_the_edge(self):
        curved = Sim(Curved(), 1.0)
        edge = next(edge for edge in curved.program.edges
                    if edge.kind == 'law')
        self.assertEqual(edge.affine, (False,))
        affine = Sim(Swept(), 0.1)
        for edge in affine.program.edges:
            with self.subTest(edge=edge.description):
                self.assertTrue(all(edge.affine))


class GroupTest(BaseNodeTest):
    """(13) The group is the program's candidates, filtered by who
    actually pushes."""

    def test_the_candidate_table_names_the_reaching_inputs(self):
        swept = Sim(Swept(), 0.1)
        self.assertEqual(sources_of(swept, 'rack.travel'),
                         frozenset({'steer'}))
        self.assertEqual(sources_of(swept, 'wheel.turn'), frozenset({'motor'}))
        shared = Sim(Shared(), 1.0)
        self.assertEqual(sources_of(shared, 'c.turn'), frozenset({'a_in'}))
        self.assertEqual(sources_of(shared, 'd.turn'),
                         frozenset({'a_in', 'b_in'}))

    def test_a_check_edge_contributes_nothing_to_the_table(self):
        sim = Sim(StoppedDifferential(), 1.0)
        self.assertEqual(sources_of(sim, 'wrist'), frozenset({'wrist_in'}))
        self.assertEqual(sources_of(sim, 'tool'), frozenset({'wrist_in'}))

    def test_an_open_gate_does_not_stop_its_crank(self):
        node = OpenGate()
        sim = Sim(node, 1.0, record=8)
        push = sim.move('push', by=10.0, duration=1.0)
        crank = sim.move('crank', by=30.0, duration=1.0)
        sim.run(1.0)
        self.assertEqual(sim.state['wheel.turn'], 20.0)
        self.assertEqual((push.status, push.admitted), ('blocked', 5.0))
        self.assertEqual((crank.status, crank.admitted), ('completed', 30.0))
        self.assertEqual(sim.state['flywheel.turn'], 30.0)
        stop, = sim.stops
        self.assertEqual(stop.inputs, ('push',))

    def test_a_closed_gate_stops_both(self):
        sim = Sim(OpenGate(), 1.0, record=8, state={'gate': 1.0})
        push = sim.move('push', by=10.0, duration=1.0)
        crank = sim.move('crank', by=30.0, duration=1.0)
        sim.run(1.0)
        self.assertEqual(sim.state['wheel.turn'], 20.0)
        self.assertEqual((push.status, push.admitted), ('blocked', 1.25))
        self.assertEqual((crank.status, crank.admitted), ('blocked', 3.75))
        self.assertEqual(sim.state['flywheel.turn'], 3.75)
        stop, = sim.stops
        self.assertEqual(sorted(stop.inputs), ['crank', 'push'])


class AtomicTickTest(BaseNodeTest):
    """(A tick that fails after a stop commits nothing.)"""

    def test_a_conflict_in_the_second_segment_refuses_the_whole_tick(self):
        node = StoppedDifferential()
        sim = Sim(node, 1.0, record=8)
        wrist = sim.move('wrist_in', by=10.0, duration=1.0)
        total = sim.move('sum_in', by=30.0, duration=1.0)
        with self.assertRaises(RunConflict) as caught:
            sim.run(1.0)
        self.assertIn('left', str(caught.exception))
        self.assertEqual(sim.state['wrist'], 0.0)
        self.assertEqual(sim.state['tool'], 0.0)
        self.assertEqual(sim.tick, 0)
        self.assertEqual(reads(node, 'wrist'), 0.0)
        self.assertEqual(sim.stops, [])
        self.assertEqual(sim.crossings, [])
        self.assertEqual(wrist.status, 'refused')
        self.assertEqual(total.status, 'refused')


class SnapshotAcrossBlockTest(BaseNodeTest):
    """(9) A block replays identically from a snapshot."""

    def test_a_snapshot_before_the_block_replays_it(self):
        sim = Sim(Ratchet(), 0.1, record=8)
        before = sim.snapshot()
        first = sim.move('arbor', by=-10.0, duration=0.1)
        sim.run(0.1)
        recorded = list(sim.stops)

        sim.restore(before)
        again = sim.move('arbor', by=-10.0, duration=0.1)
        sim.run(0.1)
        self.assertEqual(sim.state['wheel.turn'], 36.0)
        self.assertEqual(again.admitted, first.admitted)
        self.assertEqual(again.status, 'blocked')
        self.assertEqual([(stop.coordinate, stop.t) for stop in sim.stops],
                         [(stop.coordinate, stop.t) for stop in recorded])

    def test_a_snapshot_after_the_block_carries_no_command(self):
        sim = Sim(Ratchet(), 0.1, record=8)
        handle = sim.move('arbor', by=-10.0, duration=0.1)
        sim.run(0.1)
        after = sim.snapshot()
        sim.move('arbor', by=20.0, duration=0.1)
        sim.run(0.1)

        sim.restore(after)
        self.assertEqual(sim.commands, ())
        self.assertEqual(sim.state['wheel.turn'], 36.0)
        self.assertEqual(handle.status, 'blocked')
        self.assertEqual(handle.admitted, -4.0)

    def test_reset_returns_to_the_rest_pose_and_clears_every_ring(self):
        sim = Sim(Ratchet(), 0.1, record=8)
        sim.move('arbor', by=-10.0, duration=0.1)
        sim.run(0.1)
        self.assertEqual(len(sim.stops), 1)
        sim.reset()
        self.assertEqual(sim.state['wheel.turn'], 40.0)
        self.assertEqual(sim.trajectory, [])
        self.assertEqual(sim.crossings, [])
        self.assertEqual(sim.stops, [])


class StopRecordTest(BaseNodeTest):
    """(11) The stop ring: bounded, explicit, and built only when asked."""

    def test_the_ring_keeps_the_most_recent_stops(self):
        sim = Sim(Ratchet(), 0.1, record=4)
        for _ in range(6):
            sim.move('arbor', by=-10.0, duration=0.1)
            sim.run(0.1)
        self.assertEqual(len(sim.stops), 4)
        for stop in sim.stops:
            with self.subTest(stop=stop):
                self.assertIsInstance(stop, Stop)
                self.assertEqual(stop.coordinate, 'wheel.turn')
                self.assertEqual(stop.bound, 'low')
                self.assertEqual(stop.value, 36.0)
                self.assertEqual(stop.inputs, ('arbor',))
                self.assertTrue(0.0 <= stop.t <= 1.0)
        self.assertEqual([stop.tick for stop in sim.stops], [3, 4, 5, 6])

    def test_nothing_is_recorded_without_the_option(self):
        sim = Sim(Ratchet(), 0.1)
        sim.move('arbor', by=-10.0, duration=0.1)
        sim.run(0.1)
        self.assertEqual(sim.state['wheel.turn'], 36.0)
        self.assertEqual(sim.stops, [])
        self.assertEqual(sim.trajectory, [])

    def test_a_refused_tick_records_no_stop(self):
        sim = Sim(StoppedDifferential(), 1.0, record=8)
        sim.move('wrist_in', by=10.0, duration=1.0)
        sim.move('sum_in', by=30.0, duration=1.0)
        with self.assertRaises(RunConflict):
            sim.run(1.0)
        self.assertEqual(sim.stops, [])

    def test_stops_belong_to_a_running_root(self):
        sim = Sim(LoopingTrain(), 0.1)
        with self.assertRaises(TypeError) as caught:
            sim.stops
        self.assertIn('Time.running()', str(caught.exception))


class ProgramIdentityTest(BaseNodeTest):
    """(3.5) A changed range changes the program identity a snapshot is
    checked against."""

    def test_the_span_table_is_named_in_the_identity(self):
        sim = Sim(Swept(), 0.1)
        self.assertIn('span rack.travel unbounded to 50.0 mm',
                      sim.program.described())
        ratchet = Sim(Ratchet(), 0.1)
        self.assertIn('span wheel.turn (36 * floor((wheel.turn / 36))) to '
                      'unbounded deg', ratchet.program.described())
        self.assertNotEqual(sim.program.identity, ratchet.program.identity)

    def test_a_snapshot_does_not_restore_into_moved_stops(self):
        """`SweptWide` is `Swept` with the rack's bound moved and nothing
        else: a snapshot of one must not restore into the other."""
        swept = Sim(Swept(), 0.1)
        wide = Sim(SweptWide(), 0.1)
        self.assertNotEqual(wide.program.identity, swept.program.identity)
        with self.assertRaises(ValueError) as caught:
            wide.restore(swept.snapshot())
        self.assertIn('snapshot', str(caught.exception))


class UntimedControlTest(BaseNodeTest):
    """(10) The untimed reading of every new declaration, unchanged: a
    range refuses a binding outside it and never clamps or stops."""

    def test_an_expression_bound_poses_untimed_at_any_angle(self):
        for value in (0.0, 36.0, 40.0, 359.0, -720.0):
            with self.subTest(value=value):
                node = RatchetBody()
                node.set_state(arbor=value)
                self.assertEqual(reads(node, 'wheel.turn'), value)

    def test_a_bound_no_value_satisfies_is_refused_by_name(self):
        for value in (0.0, 40.0, -5.0):
            with self.subTest(value=value):
                with self.assertRaises(JointRangeError) as caught:
                    ImpossibleBoundBody().set_state(arbor=value)
                message = str(caught.exception)
                self.assertIn('turn', message)
                self.assertIn(repr(value), message)
                self.assertIn(repr(value + 1), message)

    def test_an_open_bound_accepts_anything_on_its_side(self):
        node = OpenLowBody()
        node.set_state(arbor=10_000.0)
        self.assertEqual(reads(node, 'wheel.turn'), 10_000.0)
        with self.assertRaises(JointRangeError) as caught:
            OpenLowBody().set_state(arbor=-1.0)
        self.assertIn('-1', str(caught.exception))

    def test_the_running_fixtures_pose_untimed(self):
        cases = {
            SweptBody: ({'steer': 48.0, 'motor': 2.0}, 'rack.travel', 48.0),
            SharedBody: ({'a_in': 9.0, 'b_in': 1.0}, 'c.turn', 9.0),
            TwoStopsBody: ({'lever_in': 19.0, 'steer': 46.0},
                           'lever.turn', 19.0),
            OpenGateBody: ({'push': 12.0, 'crank': 5.0, 'gate': 0.0},
                           'wheel.turn', 12.0),
            StopAndJumpBody: ({'crank': 140.0}, 'first.turn', 140.0),
            CurvedBody: ({'crank': 10.0}, 'dial.turn', 6.945927106677224),
        }
        for cls, (state, coordinate, expected) in cases.items():
            with self.subTest(cls=cls.__name__):
                node = cls()
                node.set_state(**state)
                self.assertEqual(reads(node, coordinate), approx(expected))

    def test_an_untimed_binding_outside_a_numeric_bound_is_still_refused(self):
        with self.assertRaises(JointRangeError) as caught:
            SweptBody().set_state(steer=60.0, motor=0.0)
        message = str(caught.exception)
        self.assertIn('travel', message)
        self.assertIn('60', message)


class DeferredBoundTest(BaseNodeTest):
    """ADR-109's deferral, closed: a bound MAY name a second coordinate.

    The skip this class used to carry said the feature needed "a
    declaration object that names what it reads, resolved against the
    declarer subtree at Sim construction". That object is `Bound`, and
    this is the test the skip stood in for.
    """

    def test_a_bound_may_name_a_second_coordinate(self):
        sim = Sim(Gate(), 0.1, record=8)
        self.assertEqual(span_names(sim, 'plug.turn', 'high'),
                         ['p1.lift', 'p2.lift'])
        handle = sim.move('twist', by=30.0, duration=0.1)
        sim.run(0.1)
        self.assertEqual(handle.status, 'blocked')
        self.assertEqual(reads(sim.node, 'plug.turn'), 0.0)


##############################################
# (3) A bound that reads OTHER coordinates: the constraint

class PinCrossingTest(BaseNodeTest):
    """The lock's shape, reduced to two pins: the plug may only turn
    while every lift stands inside the shear-line window."""

    def test_the_plug_does_not_turn_while_a_pin_crosses(self):
        sim = Sim(Gate(), 0.1, record=8)
        handle = sim.move('twist', by=30.0, duration=0.1)
        sim.run(0.1)

        self.assertEqual(reads(sim.node, 'plug.turn'), 0.0)
        self.assertEqual(sim.state['twist'], 0.0)
        self.assertEqual(handle.status, 'blocked')
        self.assertEqual(handle.admitted, 0.0)
        self.assertEqual(sim.commands, ())
        self.assertEqual(len(sim.stops), 1)
        stop = sim.stops[0]
        self.assertEqual(stop.coordinate, 'plug.turn')
        self.assertEqual(stop.bound, 'high')
        self.assertEqual(stop.value, 0.0)
        self.assertEqual(stop.t, 0.0)
        self.assertEqual(stop.inputs, ('twist',))

    def test_the_plug_turns_once_every_pin_clears(self):
        sim = Sim(Gate(), 0.1, record=8)
        seat = sim.move('feed', to=20.0, duration=0.4)
        sim.run(0.4)
        self.assertEqual(seat.status, 'completed')
        self.assertEqual(sim.stops, [])

        handle = sim.move('twist', by=30.0, duration=0.1)
        sim.run(0.1)
        self.assertEqual(reads(sim.node, 'plug.turn'), approx(30.0))
        self.assertEqual(handle.status, 'completed')
        self.assertEqual(handle.admitted, approx(30.0))
        self.assertEqual(sim.stops, [])

    def test_insertion_and_turning_in_one_tick(self):
        sim = Sim(Gate(), 0.1, record=8)
        feed = sim.move('feed', by=10.0, duration=0.1)
        turn = sim.move('twist', by=30.0, duration=0.1)
        sim.run(0.1)

        self.assertEqual(reads(sim.node, 'key.travel'), approx(20.0))
        self.assertEqual(reads(sim.node, 'plug.turn'), 0.0)
        self.assertEqual(feed.status, 'completed')
        self.assertEqual(feed.admitted, approx(10.0))
        self.assertEqual(turn.status, 'blocked')
        self.assertEqual(turn.admitted, 0.0)

        again = sim.move('twist', by=30.0, duration=0.1)
        sim.run(0.1)
        self.assertEqual(again.status, 'completed')
        self.assertEqual(reads(sim.node, 'plug.turn'), approx(30.0))

    def test_withdrawing_from_a_turned_plug_stops_the_key(self):
        sim = Sim(Gate(), 0.1, record=8)
        sim.move('feed', to=20.0, duration=0.4)
        sim.run(0.4)
        sim.move('twist', by=30.0, duration=0.1)
        sim.run(0.1)
        self.assertEqual(reads(sim.node, 'plug.turn'), approx(30.0))
        seen = len(sim.stops)

        handle = sim.move('feed', by=-5.0, duration=0.1)
        sim.run(0.1)

        # The plug stands where it stood; the KEY is stopped where the
        # second pin leaves the window, inside it by at most the
        # crossing tolerance of the tick's own travel.
        self.assertEqual(reads(sim.node, 'plug.turn'), approx(30.0))
        travel = reads(sim.node, 'key.travel')
        self.assertGreaterEqual(travel, 17.95)
        self.assertLessEqual(travel, 17.95 + 5.0 * 1e-11)
        self.assertEqual(handle.status, 'blocked')
        self.assertEqual(handle.admitted, approx(travel - 20.0))

        stop = sim.stops[seen]
        self.assertEqual(stop.coordinate, 'plug.turn')
        self.assertEqual(stop.bound, 'high')
        # The bound EVALUATED at the committed state, not the value the
        # coordinate holds, which is 30.
        self.assertEqual(stop.value, 90.0)
        self.assertEqual(stop.t, approx(0.41, abs=1e-9))
        self.assertEqual(stop.inputs, ('feed',))

    def test_the_stop_admits_the_same_travel_at_any_cadence(self):
        found = []
        for ticks in (1, 4, 40):
            sim = Sim(Gate(), 0.1, record=64)
            sim.move('feed', to=20.0, duration=0.4)
            sim.run(0.4)
            sim.move('twist', by=30.0, duration=0.1)
            sim.run(0.1)
            handle = sim.move('feed', by=-5.0, duration=0.1 * ticks)
            sim.run(0.1 * ticks)
            found.append((reads(sim.node, 'key.travel'), handle.admitted,
                          handle.status))
        for travel, admitted, status in found:
            self.assertEqual(status, 'blocked')
            self.assertEqual(travel, approx(found[0][0], abs=1e-9))
            self.assertEqual(admitted, approx(found[0][1], abs=1e-9))

    def test_a_constraint_stop_replays_identically_from_a_snapshot(self):
        sim = Sim(Gate(), 0.1, record=8)
        sim.move('feed', to=20.0, duration=0.4)
        sim.run(0.4)
        sim.move('twist', by=30.0, duration=0.1)
        sim.run(0.1)
        taken = sim.snapshot()

        def blocked():
            handle = sim.move('feed', by=-5.0, duration=0.1)
            sim.run(0.1)
            return (reads(sim.node, 'key.travel'), handle.admitted,
                    sim.stops[-1])

        first = blocked()
        sim.restore(taken)
        second = blocked()
        self.assertEqual(first[0], second[0])
        self.assertEqual(first[1], second[1])
        self.assertEqual(first[2].coordinate, second[2].coordinate)
        self.assertEqual(first[2].value, second[2].value)
        self.assertEqual(first[2].t, second[2].t)
        self.assertEqual(first[2].inputs, second[2].inputs)


class CaptureTest(BaseNodeTest):
    """The capture stated the OTHER way round, on the key's own travel:
    while the plug stands turned, the key may not come back out."""

    def test_the_capture_stops_the_key_at_once(self):
        sim = Sim(Captured(), 0.1, record=8)
        sim.move('twist', by=30.0, duration=0.1)
        sim.run(0.1)
        self.assertEqual(reads(sim.node, 'plug.turn'), approx(30.0))
        seen = len(sim.stops)

        handle = sim.move('feed', by=-5.0, duration=0.1)
        sim.run(0.1)

        self.assertEqual(reads(sim.node, 'key.travel'), 20.0)
        self.assertEqual(handle.status, 'blocked')
        self.assertEqual(handle.admitted, 0.0)
        stop = sim.stops[seen]
        self.assertEqual(stop.coordinate, 'key.travel')
        self.assertEqual(stop.bound, 'low')
        self.assertEqual(stop.value, 20.0)
        self.assertEqual(stop.t, 0.0)
        self.assertEqual(stop.inputs, ('feed',))

    def test_returning_the_plug_and_withdrawing_in_one_tick(self):
        sim = Sim(Captured(), 0.1, record=8)
        sim.move('twist', by=30.0, duration=0.1)
        sim.run(0.1)

        back = sim.move('twist', by=-30.0, duration=0.1)
        out = sim.move('feed', by=-5.0, duration=0.1)
        sim.run(0.1)

        self.assertEqual(reads(sim.node, 'plug.turn'), approx(0.0, abs=1e-9))
        self.assertEqual(back.status, 'completed')
        self.assertEqual(reads(sim.node, 'key.travel'), 20.0)
        self.assertEqual(out.status, 'blocked')
        self.assertEqual(out.admitted, 0.0)

        again = sim.move('feed', by=-5.0, duration=0.1)
        sim.run(0.1)
        self.assertEqual(again.status, 'completed')
        self.assertEqual(reads(sim.node, 'key.travel'), approx(15.0))


class PawlRatchetTest(BaseNodeTest):
    """The committed tooth and the along-path pawl, together."""

    def test_a_pawl_lifting_early_releases_the_ratchet(self):
        sim = Sim(PawlRatchet(), 0.1, record=8)
        arbor = sim.move('arbor', by=-10.0, duration=0.1)
        sim.move('hoist', by=10.0 / 3.0, duration=0.1)
        sim.run(0.1)

        self.assertEqual(reads(sim.node, 'wheel.turn'), approx(30.0))
        self.assertEqual(arbor.status, 'completed')
        self.assertEqual(arbor.admitted, approx(-10.0))
        self.assertEqual(sim.stops, [])

    def test_a_pawl_lifting_late_does_not(self):
        sim = Sim(PawlRatchet(), 0.1, record=8)
        arbor = sim.move('arbor', by=-10.0, duration=0.1)
        sim.move('hoist', by=2.0, duration=0.1)
        sim.run(0.1)

        self.assertAlmostEqual(reads(sim.node, 'wheel.turn'), 36.0, places=9)
        self.assertEqual(arbor.status, 'blocked')
        self.assertAlmostEqual(arbor.admitted, -4.0, places=9)
        self.assertEqual(len(sim.stops), 1)
        stop = sim.stops[0]
        self.assertEqual(stop.coordinate, 'wheel.turn')
        self.assertEqual(stop.bound, 'low')
        self.assertEqual(stop.value, 36.0)
        self.assertAlmostEqual(stop.t, 0.4, places=9)


class ConstraintCompilationTest(BaseNodeTest):
    """What a `Bound`'s reads compile to, and what they may not be."""

    def test_a_class_declared_bound_qualifies_its_reads_under_the_node(self):
        sim = Sim(ClassGate(), 0.1)
        self.assertEqual(span_names(sim, 'plug.turn', 'high'),
                         ['plug.p1.lift', 'plug.p2.lift'])
        self.assertIn('plug.p1.lift', sim.state)
        self.assertIn('plug.turn', sim.program.described())

    def test_a_site_declared_bound_qualifies_its_reads_under_the_root(self):
        sim = Sim(Gate(), 0.1)
        # The fixture's expression ignores its own coordinate, so the
        # graph's free names are the READS: what the check admits is
        # `{own} | reads`, and what the graph carries is what the author
        # wrote.
        self.assertEqual(span_names(sim, 'plug.turn', 'high'),
                         ['p1.lift', 'p2.lift'])
        for name in span_names(sim, 'plug.turn', 'high'):
            self.assertIn(name, sim.state)

    def test_a_read_of_a_plain_port_is_refused_at_construction(self):
        with self.assertRaises(ValueError) as caught:
            Sim(PortRead(), 0.1)
        message = str(caught.exception)
        self.assertIn('dial.turn', message)
        self.assertIn('turn', message)
        self.assertIn('reads the STATE', message)

    def test_a_bound_returning_a_number_is_refused_at_construction(self):
        """A `Bound` that declares a read and returns a number reads
        nothing it declares: refused by name, never carried as a
        constraint with no expression to evaluate."""
        with self.assertRaises(ValueError) as caught:
            Sim(ConstantBound(), 0.1)
        message = str(caught.exception)
        self.assertIn('plug.turn', message)
        self.assertIn('p1.lift', message)
        self.assertIn('never reads', message)

    def test_a_read_the_expression_never_uses_is_refused_at_construction(self):
        with self.assertRaises(ValueError) as caught:
            Sim(UnusedRead(), 0.1)
        message = str(caught.exception)
        self.assertIn('plug.turn', message)
        self.assertIn('p2.lift', message)
        self.assertNotIn("'p1.lift'", message.split('never reads')[-1])
        self.assertIn('never reads', message)

    def test_a_bound_over_other_coordinates_changes_the_identity(self):
        narrow = Sim(Gate(), 0.1)
        wide = Sim(GateWide(), 0.1)
        self.assertNotEqual(narrow.program.identity, wide.program.identity)
        taken = narrow.snapshot()
        with self.assertRaises(ValueError):
            wide.restore(taken)


class DriverReadTest(BaseNodeTest):
    """A read that is a DRIVER is an input of the bank, evaluated along
    the path as its admission scaled by the fraction."""

    def test_a_gate_closing_mid_tick_stops_the_push_and_the_gate(self):
        sim = Sim(DriverGate(), 0.1, record=8)
        self.assertEqual(span_names(sim, 'spin', 'high'), ['gate'])

        push = sim.move('push', by=10.0, duration=0.1)
        gate = sim.move('gate', by=-2.0, duration=0.1)
        sim.run(0.1)

        self.assertAlmostEqual(reads(sim.node, 'spin'), 5.0, places=9)
        self.assertAlmostEqual(sim.state['gate'], 1.0, places=9)
        self.assertEqual(push.status, 'blocked')
        self.assertEqual(gate.status, 'blocked')
        stop = sim.stops[0]
        self.assertEqual(stop.coordinate, 'spin')
        self.assertEqual(stop.bound, 'high')
        self.assertAlmostEqual(stop.t, 0.5, places=9)
        self.assertEqual(stop.inputs, ('gate', 'push'))


class ConstraintCostTest(BaseNodeTest):
    """(3.3) A machine with no bound reading other coordinates pays
    nothing, and one that has such a bound pays only while something the
    bound depends on moves."""

    def graph_evaluations(self, sim, ticks):
        """How many times a compiled graph is evaluated over `ticks`."""
        return graph_evaluations(sim, ticks)

    def test_the_train_pays_what_it_always_paid(self):
        sim = Sim(Train(), 0.1)
        sim.rate('crank', 90.0)
        sim.run(0.1)
        # 8 per tick, the number the base commit 33d8bf5 measures for
        # the same probe: a machine declaring no bound that reads other
        # coordinates pays nothing new.
        self.assertEqual(self.graph_evaluations(sim, 10), 80)

    def test_a_tick_moving_only_the_bounded_coordinate_is_not_sampled(self):
        """When nothing a bound READS moves over the stretch, the bound
        is a number for that stretch -- its expression at the committed
        own value and the reads' standing values -- and the coordinate
        is stopped or freed as a bound over its own value alone is, at
        the cost of one evaluation, not `_SUBDIVISIONS` sub-program
        passes. The plug turning with the pins standing still is the
        lock's own case."""
        sim = Sim(Gate(), 0.1, record=8, state={'feed': 20.0})
        idle = self.graph_evaluations(sim, 1)
        sim.move('twist', by=30.0, duration=0.1)
        turning = self.graph_evaluations(sim, 1)
        self.assertEqual(sim.state['plug.turn'], 30.0)
        # One bound evaluation over the standing reads, and nothing
        # else beyond an idle tick.
        self.assertLessEqual(turning, idle + 2)

    def test_a_blocking_tick_of_the_gate_is_bounded(self):
        sim = Sim(Gate(), 0.1, record=8)
        sim.move('twist', by=30.0, duration=0.1)
        blocking = self.graph_evaluations(sim, 1)
        self.assertLess(blocking, 64 * 4 + 64 * 4 + 8 * 4)
        idle = self.graph_evaluations(sim, 1)
        self.assertLess(idle, blocking)


class SelfReadStopTest(BaseNodeTest):
    """A stop and a self-read crossing in one tick.

    OpenSpec change ``read-the-driven-coordinate``: a self-read crossing
    is NOT a stop -- it stops no input and retires no command -- while a
    declared range on the same coordinate still is, and wins where both
    fall in one segment.
    """

    def test_an_unrelated_stop_and_a_gate_crossing_share_one_tick(self):
        sim = Sim(StoppedClearing(), 1.0, record=8)
        ring = sim.move('ring', by=600.0, duration=1.0)
        gauge = sim.move('gauge_in', by=100.0, duration=1.0)
        sim.run(1.0)

        self.assertEqual(sim.state['gauge.turn'], 40.0)
        self.assertEqual(sim.state['wheel.turn'], 359.5)
        self.assertEqual(ring.status, 'completed')
        self.assertEqual(gauge.status, 'blocked')
        self.assertEqual([stop.coordinate for stop in sim.stops],
                         ['gauge.turn'])
        # The crossing is recorded at its fraction OF THE TICK, not of
        # the segment the stop cut the tick into.
        gate = [entry for entry in sim.crossings
                if entry.coordinate == 'wheel.turn']
        self.assertTrue(gate)
        for entry in gate:
            with self.subTest(crossing=entry):
                self.assertEqual(entry.tick, 1)
                self.assertTrue(0.0 < entry.t < 1.0)
        # The cut at which the dial reached its gap: ring 351.5 of the
        # tick's 600, which is 0.58583... of the TICK even though the
        # gauge's stop cut the tick at 0.4.
        self.assertTrue(any(abs(entry.t - 0.5858333333333333) < 1e-9
                            for entry in gate))

    def test_a_bound_wins_over_a_landing_the_same_segment_reported(self):
        sim = Sim(StoppedClearing(), 1.0, record=8)
        ring = sim.move('ring', by=600.0, duration=1.0)
        setter = sim.move('setter', by=100.0, duration=1.0)
        sim.run(1.0)

        # The gate cut the segment and placed the dial at the band's
        # edge; the setter then carried it on to its declared bound,
        # which is a bound of the coordinate itself and takes it AT the
        # bound exactly.
        self.assertEqual(sim.state['wheel.turn'], 400.0)
        self.assertEqual([stop.coordinate for stop in sim.stops],
                         ['wheel.turn'])
        self.assertEqual(sim.stops[0].value, 400.0)
        self.assertEqual(sorted(sim.stops[0].inputs), ['ring', 'setter'])
        self.assertEqual(ring.status, 'blocked')
        self.assertEqual(setter.status, 'blocked')
        gate = [entry for entry in sim.crossings
                if entry.coordinate == 'wheel.turn']
        self.assertTrue(any(entry.t < sim.stops[0].t for entry in gate))


class BlockStopTest(BaseNodeTest):
    """A declared range on a coordinate a BLOCK determines, and the
    pushing test through it (OpenSpec change ``select-the-source``).

    A block's value is piecewise in the selector partition AND re-ordered
    across it, so every stop on one of its coordinates takes the SEARCHED
    path -- and `Run._pushes` runs the WHOLE block under one input's
    displacement before its `key in edge.gives` break, which is the
    granularity an inactive selection needs.
    """

    def block_edge(self, sim):
        found = [edge for edge in sim._run.program.edges
                 if edge.kind == 'block']
        self.assertEqual(len(found), 1)
        return found[0]

    def test_a_range_on_a_block_coordinate_stops_it_at_its_bound(self):
        from .carriage_project.machine import RangedBlock

        sim = Sim(RangedBlock(), 1.0, record=4, state={'shift': 1.0})
        crank = sim.move('crank', by=2.0, duration=1.0)
        sim.run(1.0)
        self.assertEqual(sim.state['carry.travel'], 0.6)
        stop, = sim.stops
        self.assertEqual(stop.coordinate, 'carry.travel')
        self.assertEqual(stop.bound, 'high')
        self.assertEqual(stop.value, 0.6)
        self.assertEqual(stop.inputs, ('crank',))
        self.assertEqual(crank.status, 'blocked')
        self.assertEqual(stop.t, approx(0.3, rel=1e-9))

    def test_a_stop_on_a_block_coordinate_is_searched_not_solved(self):
        from .carriage_project.machine import RangedBlock

        sim = Sim(RangedBlock(), 1.0, state={'shift': 1.0})
        edge = self.block_edge(sim)
        self.assertEqual(list(edge.affine), [False, False])

    def test_an_inactive_selection_does_not_block_its_input(self):
        from .carriage_project.machine import RangedBlock

        sim = Sim(RangedBlock(), 1.0, record=4, state={'shift': 1.0})
        crank = sim.move('crank', by=2.0, duration=1.0)
        spin = sim.move('spin', by=1.0, duration=1.0)
        sim.run(1.0)
        # `spin` reaches the stopped lever ONLY through the term the
        # carriage has switched out, so it is not stopped by it.
        self.assertEqual(spin.status, 'completed')
        self.assertEqual(spin.admitted, 1.0)
        self.assertEqual(sim.state['lower.turn'], 1.0)
        self.assertEqual(crank.status, 'blocked')
        self.assertEqual(sim.state['carry.travel'], 0.6)
        stop, = sim.stops
        self.assertEqual(stop.inputs, ('crank',))

    def test_the_probe_runs_the_whole_block_under_one_displacement(self):
        from .carriage_project.machine import RangedBlock

        sim = Sim(RangedBlock(), 1.0, state={'shift': 1.0})
        program = sim._run.program
        key = program.keys['carry.travel']
        edge = program.determiner[key]
        self.assertEqual(edge.kind, 'block')
        self.assertEqual([program.nodes[one].name for one in edge.gives],
                         ['higher.turn', 'carry.travel'])
        # The candidate table is deliberately over-broad -- a block is
        # ONE node in it -- and `_pushes` is what filters it per tick.
        self.assertEqual(sorted(program.sources[key]),
                         ['crank', 'shift', 'spin'])
        values = program.values_of(dict(sim.state))
        self.assertTrue(sim._run._pushes('crank', 1.0, key, values))
        self.assertFalse(sim._run._pushes('spin', 1.0, key, values))

    def test_a_probe_over_a_cyclic_piece_refuses_as_the_tick_does(self):
        from .carriage_project.machine import BothActive

        sim = Sim(BothActive(), 1.0, state={'shift': 1.0})
        program = sim._run.program
        with self.assertRaises(UnsupportedLaw) as probe:
            program.response(dict(sim.state), 'crank', 2.0 ** -20)
        sim.move('crank', by=1.0, duration=1.0)
        with self.assertRaises(UnsupportedLaw) as tick:
            sim.run(1.0)
        self.assertEqual(str(probe.exception), str(tick.exception))

    def test_a_landing_and_a_stop_in_one_segment_let_the_bound_win(self):
        from .carriage_project.machine import StoppedLanding

        sim = Sim(StoppedLanding(), 1.0, record=4, state={'shift': 1.0})
        sim.move('crank', by=2.0, duration=1.0)
        sim.move('setter', by=1.0, duration=1.0)
        sim.run(1.0)
        # The lever's own gate cuts the path at `0.5` and LANDS it there;
        # the setter then carries it past the declared `0.6`, and the
        # bound is what the tick commits.
        self.assertEqual(sim.state['carry.travel'], 0.6)
        stop, = sim.stops
        self.assertEqual((stop.coordinate, stop.value), ('carry.travel', 0.6))
        self.assertEqual(stop.inputs, ('crank', 'setter'))
        self.assertIn(('carry.travel', '<'),
                      [(one.coordinate, one.primitive)
                       for one in sim.crossings])

    def test_a_selector_crossing_and_a_stop_in_one_tick_keep_their_order(
            self):
        from .carriage_project.machine import RangedBlock

        # The STOP first: `spin` drives the lever into its bound a third
        # of the way along, and the carriage crosses its detent at the
        # half.
        sim = Sim(RangedBlock(), 1.0, record=8)
        spin = sim.move('spin', by=2.0, duration=1.0)
        sim.move('shift', by=1.0, duration=1.0)
        sim.run(1.0)
        stop, = sim.stops
        self.assertEqual(stop.t, approx(0.3, rel=1e-9))
        self.assertEqual(spin.status, 'blocked')
        selectors = [one.t for one in sim.crossings if one.t == 0.5]
        self.assertEqual(selectors, [0.5, 0.5])
        self.assertLess(stop.t, selectors[0])

        # The CROSSING first: the lower wheel barely moves, so the lever
        # reaches its bound only once the carriage has handed it to the
        # higher one.
        other = Sim(RangedBlock(), 1.0, record=8)
        other.move('spin', by=0.4, duration=1.0)
        other.move('crank', by=2.0, duration=1.0)
        other.move('shift', by=1.0, duration=1.0)
        other.run(1.0)
        stop = other.stops[0]
        self.assertEqual(stop.t, approx(0.7, rel=1e-9))
        self.assertEqual(
            sorted({one.t for one in other.crossings if one.t < stop.t}),
            [0.5])


class CarriageInterlockTest(BaseNodeTest):
    """The Curta-shaped fixture's interlock: no shift unless lifted.

    A `Bound(..., reads=)` on the carriage's own coordinate, whose
    sub-program contains no block at all -- the lift is UPSTREAM of the
    block -- so the constraint costs the block nothing.
    """

    DT = 0.02

    def setUp(self):
        super().setUp()
        from .carriage_project.machine import CurtaCarriage

        self.sim = Sim(CurtaCarriage(), self.DT, record=256)

    def step(self, name, travel, duration, ticks):
        handle = self.sim.move(name, by=travel, duration=duration)
        for _tick in range(ticks):
            self.sim.run(self.DT)
        return handle

    def test_a_shift_is_stopped_at_its_restraint_while_a_lever_stands_set(
            self):
        self.step('lift', 1.0, 0.1, 5)
        self.step('position', 1.0, 0.2, 10)
        self.step('lift', -1.0, 0.1, 5)
        self.step('crank', 36.0, 0.4, 20)
        self.assertEqual(self.sim.state['seat'], 20.0)
        self.assertEqual(self.sim.state['lever0.travel'], 1.0)
        pending = {key: self.sim.state[key] for key in self.sim.state
                   if key.startswith(('dial', 'lever'))}

        shift = self.step('position', 1.0, 0.2, 10)
        self.assertEqual(shift.status, 'blocked')
        self.assertEqual(shift.admitted, 0.0)
        self.assertEqual(self.sim.state['seat'], 20.0)
        stop = self.sim.stops[-1]
        self.assertEqual(stop.coordinate, 'seat')
        self.assertEqual(stop.inputs, ('position',))
        # Nothing discarded the pending carry and nothing finished it.
        for key, value in pending.items():
            self.assertEqual(self.sim.state[key], value, key)

    def test_the_same_shift_is_admitted_once_the_carriage_is_lifted(self):
        self.step('crank', 36.0, 0.4, 20)
        self.assertEqual(self.sim.state['lever0.travel'], 1.0)
        self.step('lift', 1.0, 0.1, 5)
        shift = self.step('position', 1.0, 0.2, 10)
        self.assertEqual(shift.status, 'completed')
        self.assertEqual(self.sim.state['seat'], 20.0)
        self.assertEqual(self.sim.state['lever0.travel'], 1.0)


class KinkedDeterminerStopTest(BaseNodeTest):
    """A stop on a determiner that is KINKED and carries no jump at all.

    OpenSpec change ``cut-at-the-kink``, design.md section 11 case C.
    ``KinkedStop`` drives its slide by the Curta bench's own
    ``4 + 72 * clamp01((lever - 113.5) / 11.25)``. The slide's bound,
    40 mm, lies on the law's SLOPED piece; the tick starts on the FLAT
    one below it. So the stop is not where a single division over the
    whole tick puts it: the path has to be cut at the kink first.
    """

    #: The fixture's own arithmetic, never the law's: the clamp is at
    #: one half where the slide reads `4 + 72 * 0.5 == 40`, which is
    #: `lever == 113.5 + 0.5 * 11.25`, and the tick carries the lever
    #: from 100 by 40.
    EXACT = (113.5 + 0.5 * 11.25 - 100.0) / 40.0

    def stopped(self):
        sim = Sim(KinkedStop(), 0.1, record=8)
        sim.move('lever', by=40.0, duration=0.1)
        sim.run(0.1)
        return sim

    def test_the_stop_is_located_on_the_sloped_piece(self):
        sim = self.stopped()
        self.assertEqual([one.coordinate for one in sim.stops],
                         ['slide.travel'])
        self.assertEqual(sim.stops[0].t, self.EXACT)
        # NOT the answer one division over the whole tick gives: the
        # slide travels 72 mm over it, so that division would put the
        # bound at exactly half way.
        self.assertNotEqual(sim.stops[0].t, 0.5)

    def test_the_coordinate_is_committed_at_its_bound(self):
        sim = self.stopped()
        self.assertEqual(sim.state['slide.travel'], 40.0)
        # And the input is admitted only as far as the stop.
        self.assertEqual(sim.state['lever'], 100.0 + 40.0 * self.EXACT)

    def test_a_kink_the_tick_does_not_reach_leaves_no_cut(self):
        """The invariant the one-division fast path rests on: where no
        kink is crossed over the tick, the determiner IS affine over the
        whole of it, so its cut list is EMPTY and `Run._locate` divides
        once.

        This tick stays entirely on the sloped piece.
        """
        sim = Sim(KinkedStop(), 0.1, record=8, state={'lever': 115.0})
        program = sim._run.program
        key = sim._run.keys['slide.travel']
        edge = program.determiner[key]
        index = edge.gives.index(key)
        self.assertEqual(edge.shapes[index], 'kinked')
        self.assertFalse(edge.affine[index])
        values = dict(sim._run._values(sim._run.bank))
        # Two ticks of the same law: one that stays between the kinks,
        # and one that crosses the upper kink at `lever == 124.75`.
        inside = edge.cuts(values, {key: 0.0,
                                    sim._run.keys['lever']: 4.0}, index)
        self.assertEqual(inside, ())
        across = edge.cuts(values, {key: 0.0,
                                    sim._run.keys['lever']: 40.0}, index)
        self.assertEqual(len(across), 3)
        self.assertEqual(across[0], 0.0)
        self.assertEqual(across[-1], 1.0)
        self.assertEqual(across[1], (124.75 - 115.0) / 40.0)
