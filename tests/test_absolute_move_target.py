"""Absolute running requests keep their terminal value, not only their travel."""

from dataclasses import replace
import math
import struct
from unittest import TestCase
import numpy as np

from machinome.motion.joints import Bound, Prismatic
from machinome.motion.ports import Time
from machinome.math import sqrt
from machinome.node import AssemblyNode
from machinome.simulation import Driver, Play, Sim

from .running_project.parts import Carriage
from .test_running_follow import TwoSurfaces
from .running_project.machine import Wrapped


HIGH = 3.9075
LOW = -5.0


class LiteralLimit(AssemblyNode):
    time = Time.running()
    lever = Driver(default=0.0, unit='mm')
    carriage = Carriage(travel=Prismatic(axis=(1, 0, 0), unit='mm',
                                         range=(LOW, HIGH)))
    lever.drives(carriage.travel, ratio=1.0)


class ReadingLimit(AssemblyNode):
    time = Time.running()
    lever = Driver(default=0.0, unit='mm')
    high = Driver(default=HIGH, unit='mm')
    carriage = Carriage(travel=Prismatic(
        axis=(1, 0, 0), unit='mm',
        range=(LOW, Bound(lambda own, high: high, reads=(high,)))))
    lever.drives(carriage.travel, ratio=1.0)


class TwoIndependentStops(AssemblyNode):
    time = Time.running()
    lever = Driver(default=0.0)
    other = Driver(default=0.0)
    carriage = Carriage(travel=Prismatic(axis=(1, 0, 0),
                                         range=(LOW, HIGH)))
    brake = Carriage(travel=Prismatic(axis=(1, 0, 0),
                                      range=(-5.0, 1.0)))
    lever.drives(carriage.travel)
    other.drives(brake.travel)


class WholeCount(AssemblyNode):
    time = Time.running()
    lever = Driver(default=0, dtype=int)


def square_root_at_endpoint(source, target):
    return lambda lever: sqrt(0.1 - lever)


class EndpointDomain(AssemblyNode):
    time = Time.running()
    lever = Driver(default=-0.2)
    carriage = Carriage(travel=Prismatic(axis=(1, 0, 0)))
    lever.drives(carriage.travel, law=square_root_at_endpoint)


def cyclic_terminal(source, target):
    return lambda feed, shift, other: feed + other*(shift > 0)


class CyclicTerminal(AssemblyNode):
    time = Time.running()
    feed = Driver(default=0.0)
    shift = Driver(default=0.0)
    first = Carriage(travel=Prismatic(axis=(1, 0, 0)))
    second = Carriage(travel=Prismatic(axis=(1, 0, 0)))
    (feed & shift & second.travel).drives(
        first.travel, law=cyclic_terminal)
    first.travel.drives(second.travel)

    def simulate(self):
        if self.first.travel.value is None:
            self.first.travel = 0.0
        if self.second.travel.value is None:
            self.second.travel = 0.0


def play_domain_law(source, target):
    return lambda ball: sqrt(0.10000000000000009-ball)


class PlayDomain(AssemblyNode):
    time = Time.running()
    feed = Driver(default=-3.9425)
    ball = Carriage(travel=Prismatic(axis=(1, 0, 0)))
    slide = Carriage(travel=Prismatic(axis=(1, 0, 0)))
    (feed & ball.travel).drives(ball.travel, law=Play(-1.0, 1.0))
    ball.travel.drives(slide.travel, law=play_domain_law)

    def simulate(self):
        if self.ball.travel.value is None:
            self.ball.travel = -4.9425


def signed_zero_selector(source, target):
    return lambda lever: lever*(lever > 1.0)


def endpoint_domain_selector(source, target):
    return lambda lever: sqrt(0.1-lever)*(lever > 0.0)


class SignedZeroSelector(AssemblyNode):
    time = Time.running()
    lever = Driver(default=0.0)
    carriage = Carriage(travel=Prismatic(axis=(1, 0, 0)))
    lever.drives(carriage.travel, law=signed_zero_selector)


class EndpointDomainSelector(AssemblyNode):
    time = Time.running()
    lever = Driver(default=-0.2)
    carriage = Carriage(travel=Prismatic(axis=(1, 0, 0)))
    lever.drives(carriage.travel, law=endpoint_domain_selector)


class AbsoluteTargetTest(TestCase):
    def test_inclusive_upper_landing_completes_with_literal_and_read_bound(self):
        for model in (LiteralLimit, ReadingLimit):
            with self.subTest(model=model.__name__):
                sim = Sim(model(), dt=1/240, meshes=False, record=8)
                first = sim.move('lever', to=math.nextafter(-4.9425, math.inf))
                self.assertEqual(first.status, 'completed')
                move = sim.move('lever', to=HIGH)
                self.assertEqual(move.status, 'completed')
                self.assertEqual(sim.state['lever'], HIGH)
                self.assertEqual(sim.state['carriage.travel'], HIGH)
                self.assertEqual(sim.stops, [])

    def test_below_rounding_direction_still_lands_exactly(self):
        sim = Sim(LiteralLimit(), dt=1/240, meshes=False)
        sim.move('lever', to=-4.9425)
        move = sim.move('lever', to=HIGH)
        self.assertEqual(move.status, 'completed')
        self.assertEqual(sim.state['lever'], HIGH)
        self.assertEqual(sim.state['carriage.travel'], HIGH)

    def test_terminal_correction_keeps_legacy_interior_law_samples(self):
        sim = Sim(LiteralLimit(), dt=1/240, meshes=False)
        sim.move('lever', to=-4.9425)
        run = sim._run
        values = run._values(run.bank, {})
        deltas = run._deltas({'lever': HIGH-run.bank['lever']})
        edge = run.program.edges[0]
        driven = edge.gives[0]
        old_increment = edge.increments(values, dict(deltas))[0][1]
        landings = {}
        run._pass(values, deltas, None, sim.tick, landings,
                  {run.keys['lever']: HIGH})
        self.assertTrue(deltas.motions[run.keys['lever']].affine)
        self.assertEqual(deltas.motions[run.keys['lever']].line_delta,
                         HIGH-run.bank['lever'])
        self.assertTrue(deltas.motions[driven].affine)
        self.assertEqual(deltas.motions[driven].line_delta, old_increment)
        for fraction in (1/64, .5, .75, 63/64):
            with self.subTest(fraction=fraction):
                old = values[driven] + old_increment*fraction
                new = deltas.motions[driven].at(fraction)
                self.assertEqual(struct.pack('!d', new),
                                 struct.pack('!d', old))
        self.assertEqual(landings[driven], HIGH)

    def test_valid_exact_endpoint_is_not_rejected_by_legacy_ulp_domain(self):
        sim = Sim(EndpointDomain(), dt=1/240, meshes=False)
        move = sim.move('lever', to=0.1)
        self.assertEqual(move.status, 'completed')
        self.assertEqual(sim.state['lever'], 0.1)
        self.assertEqual(sim.state['carriage.travel'], 0.0)

    def test_truly_invalid_authored_endpoint_still_raises(self):
        sim = Sim(EndpointDomain(), dt=1/240, meshes=False)
        before = dict(sim.state)
        with self.assertRaisesRegex(ValueError, 'math domain'):
            sim.move('lever', to=0.2)
        self.assertEqual(dict(sim.state), before)

    def test_jump_plan_keeps_old_interior_partition(self):
        sim = Sim(Wrapped(), dt=.1, meshes=False)
        run = sim._run
        values = run._values(run.bank, {})
        delta = -4.9425-run.bank['crank']
        driven = run.keys['pinion.turn']
        old = run._deltas({'crank': delta})
        old.demanded = frozenset({driven})
        run._pass(values, old, None, sim.tick, {})
        exact = run._deltas({'crank': delta})
        exact.demanded = frozenset({driven})
        landings = {}
        run._pass(values, exact, None, sim.tick, landings,
                  {run.keys['crank']: -4.9425})
        for fraction in (1/64, .25, .5, .75, 63/64):
            with self.subTest(fraction=fraction):
                self.assertEqual(
                    struct.pack('!d', exact.motions[driven].at(fraction)),
                    struct.pack('!d', old.motions[driven].at(fraction)))
        self.assertEqual(sim.move('crank', to=-4.9425).status, 'completed')
        self.assertEqual(sim.state['crank'], -4.9425)
        # This first request has no additive endpoint mismatch; its
        # historical jump integration remains byte-for-byte unchanged.
        self.assertEqual(sim.state['pinion.turn'], -9.884999999999991)
        values = run._values(run.bank, {})
        delta = HIGH-run.bank['crank']
        old = run._deltas({'crank': delta})
        old.demanded = frozenset({driven})
        run._pass(values, old, None, sim.tick, {})
        exact = run._deltas({'crank': delta})
        exact.demanded = frozenset({driven})
        run._pass(values, exact, None, sim.tick, landings,
                  {run.keys['crank']: HIGH})
        for fraction in (step/64 for step in range(1, 64)):
            with self.subTest(terminal_fraction=fraction):
                self.assertEqual(
                    struct.pack('!d', exact.motions[driven].at(fraction)),
                    struct.pack('!d', old.motions[driven].at(fraction)))

    def test_cycle_block_lands_terminal_dependency(self):
        sim = Sim(CyclicTerminal(), dt=.1, meshes=False)
        self.assertEqual(sim.move('feed', to=-4.9425).status, 'completed')
        self.assertEqual(sim.move('feed', to=HIGH).status, 'completed')
        self.assertEqual(sim.state['feed'], HIGH)
        self.assertEqual(sim.state['first.travel'], HIGH)
        self.assertEqual(sim.state['second.travel'], HIGH)

    def test_play_exact_landing_reaches_curved_domain_child(self):
        sim = Sim(PlayDomain(), dt=.1, meshes=False)
        move = sim.move('feed', to=1.1)
        self.assertEqual(move.status, 'completed')
        self.assertEqual(sim.state['ball.travel'], 0.10000000000000009)
        self.assertEqual(sim.state['slide.travel'], 0.0)

    def test_follow_still_accepts_terminal_exact_linear_source(self):
        sim = Sim(TwoSurfaces(), dt=.1, meshes=False)
        self.assertEqual(sim.move('low', to=-4.9425).status, 'completed')
        self.assertEqual(sim.move('low', to=2.9075).status, 'completed')
        self.assertEqual(sim.state['low'], 2.9075)
        self.assertEqual(sim.state['ball.slide'], 2.9075)


    def test_timed_move_retains_target_after_snapshot_restore(self):
        sim = Sim(LiteralLimit(), dt=.1, meshes=False, record=8)
        sim.move('lever', to=-4.9425)
        move = sim.move('lever', to=HIGH, duration=.2)
        sim.run(.1)
        snapshot = sim.snapshot()
        middle = sim.state['lever']
        sim.run(.1)
        first = (move.status, dict(sim.state), tuple(sim.stops))
        self.assertEqual(first[0], 'completed')
        self.assertEqual(first[1]['lever'], HIGH)
        self.assertEqual(first[1]['carriage.travel'], HIGH)
        sim.restore(snapshot)
        self.assertEqual(sim.state['lever'], middle)
        sim.run(.1)
        self.assertEqual((dict(sim.state), tuple(sim.stops)), first[1:])

    def test_timed_reverse_target_and_legacy_snapshot_form(self):
        sim = Sim(LiteralLimit(), dt=.1, meshes=False)
        move = sim.move('lever', to=-4.9425, duration=.2)
        sim.run(.1)
        current = sim.snapshot()
        self.assertEqual(len(current.targets), 1)
        legacy = replace(current, targets=())
        sim.restore(legacy)
        self.assertEqual(sim.snapshot().targets, ())
        sim.restore(current)
        sim.run(.1)
        self.assertEqual(move.status, 'cancelled')
        self.assertEqual(sim.state['lever'], -4.9425)

    def test_earlier_independent_stop_keeps_other_terminal_target(self):
        sim = Sim(TwoIndependentStops(), dt=.1, meshes=False, record=8)
        sim.move('lever', to=-4.9425)
        requested = sim.move('lever', to=HIGH, duration=.1)
        stopping = sim.move('other', to=2.0, duration=.1)
        sim.run(.1)
        self.assertEqual(requested.status, 'completed')
        self.assertEqual(stopping.status, 'blocked')
        self.assertEqual(sim.state['lever'], HIGH)
        self.assertEqual(sim.state['carriage.travel'], HIGH)
        self.assertEqual(sim.state['brake.travel'], 1.0)
        self.assertEqual(len(sim.stops), 1)
        self.assertEqual(sim.stops[0].inputs, ('other',))

    def test_independent_runs_replay_exact_target(self):
        first = Sim(LiteralLimit(), dt=.1, meshes=False)
        second = Sim(LiteralLimit(), dt=.1, meshes=False)
        for sim in (first, second):
            sim.move('lever', to=-4.9425)
            sim.move('lever', to=HIGH)
        self.assertEqual(dict(first.state), dict(second.state))
        self.assertEqual(first.snapshot().bank, second.snapshot().bank)

    def test_relative_travel_beyond_bound_still_blocks(self):
        sim = Sim(LiteralLimit(), dt=1/240, meshes=False, record=8)
        sim.move('lever', to=math.nextafter(-4.9425, math.inf))
        move = sim.move('lever', by=8.85)
        self.assertEqual(move.status, 'blocked')
        self.assertEqual(sim.state['carriage.travel'], HIGH)
        self.assertEqual(len(sim.stops), 1)

    def test_true_absolute_beyond_bound_still_blocks(self):
        sim = Sim(LiteralLimit(), dt=1/240, meshes=False, record=8)
        sim.move('lever', to=math.nextafter(-4.9425, math.inf))
        move = sim.move('lever', to=4.0)
        self.assertEqual(move.status, 'blocked')
        self.assertEqual(sim.state['carriage.travel'], HIGH)
        self.assertEqual(len(sim.stops), 1)

    def test_negative_zero_is_the_stated_terminal_bit(self):
        sim = Sim(LiteralLimit(), dt=1/240, meshes=False)
        move = sim.move('lever', to=-0.0)
        self.assertEqual(move.status, 'completed')
        self.assertEqual(math.copysign(1, sim.state['lever']), -1.0)

    def test_planned_law_receives_negative_zero_terminal_bit(self):
        sim = Sim(SignedZeroSelector(), dt=.1, meshes=False)
        move = sim.move('lever', to=-0.0)
        self.assertEqual(move.status, 'completed')
        self.assertEqual(math.copysign(1, sim.state['lever']), -1.0)
        self.assertEqual(math.copysign(1, sim.state['carriage.travel']), -1.0)

    def test_planned_law_uses_valid_exact_domain_endpoint(self):
        sim = Sim(EndpointDomainSelector(), dt=.1, meshes=False)
        move = sim.move('lever', to=0.1)
        self.assertEqual(move.status, 'completed')
        self.assertEqual(sim.state['lever'], 0.1)
        # The authored value at the target is zero, but this running law
        # retains the integrated history across its comparison cut.
        self.assertEqual(sim.state['carriage.travel'],
                         -0.31622776601690983)

    def test_malformed_optional_snapshot_target_refuses_atomically(self):
        sim = Sim(LiteralLimit(), dt=.1, meshes=False)
        sim.move('lever', to=1.0, duration=.2)
        saved = sim.snapshot()
        for bad in ('not numeric', math.inf, math.nan):
            with self.subTest(bad=bad):
                before = sim.snapshot()
                malformed = replace(saved, targets=(('lever', bad),))
                with self.assertRaises((TypeError, ValueError)):
                    sim.restore(malformed)
                self.assertEqual(sim.snapshot(), before)

    def test_snapshot_target_requires_matching_active_move_and_native_type(self):
        sim = Sim(LiteralLimit(), dt=.1, meshes=False)
        sim.rate('lever', 1.0)
        saved = sim.snapshot()
        with self.assertRaises(ValueError):
            sim.restore(replace(saved, targets=(('lever', 1.0),)))
        self.assertEqual(sim.snapshot(), saved)
        with self.assertRaises(ValueError):
            sim.restore(replace(saved, targets=(('missing', 1.0),)))
        self.assertEqual(sim.snapshot(), saved)

        counted = Sim(WholeCount(), dt=.1, meshes=False)
        counted.move('lever', to=2, duration=.2)
        before = counted.snapshot()
        with self.assertRaises(ValueError):
            counted.restore(replace(before, targets=(('lever', 2.0),)))
        self.assertEqual(counted.snapshot(), before)

    def test_own_snapshot_roundtrips_boolean_numeric_target(self):
        sim = Sim(LiteralLimit(), dt=.1, meshes=False)
        sim.move('lever', to=True, duration=.2)
        saved = sim.snapshot()
        sim.restore(saved)
        self.assertEqual(sim.snapshot(), saved)
        sim.run(.2)
        self.assertEqual(sim.state['lever'], 1.0)

    def test_non_plain_real_restore_does_not_add_an_early_rejection(self):
        sim = Sim(LiteralLimit(), dt=.1, meshes=False)
        sim.move('lever', to=np.float64(-4.9425), duration=.2)
        saved = sim.snapshot()
        sim.restore(saved)
        self.assertEqual(sim.snapshot(), saved)
        # The existing state binder rejects NumPy scalars as non-plain
        # numbers on the first partial tick; restore must not replace that
        # established error with an earlier sidecar-type error.
        with self.assertRaisesRegex(TypeError, 'plain number'):
            sim.run(.1)

    def test_integer_native_target_does_not_require_float_conversion(self):
        sim = Sim(WholeCount(), dt=.1, meshes=False)
        target = 10**400
        move = sim.move('lever', to=target)
        self.assertEqual(move.status, 'completed')
        self.assertEqual(sim.state['lever'], target)

    def test_enormous_integer_target_own_snapshot_roundtrips(self):
        sim = Sim(WholeCount(), dt=.1, meshes=False)
        sim.move('lever', to=10**400, duration=.2)
        saved = sim.snapshot()
        sim.restore(saved)
        self.assertEqual(sim.snapshot(), saved)

    def test_only_marked_internal_terminal_landing_may_be_unbanked(self):
        sim = Sim(LiteralLimit(), dt=.1, meshes=False)
        unknown = object()
        with self.assertRaises(KeyError):
            sim._run._landed({}, {unknown: 1.0})
        committed = {}
        sim._run._landed(committed, {unknown: 1.0}, {unknown})
        self.assertEqual(committed, {})
