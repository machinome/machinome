"""A retained scalar follows two independently authored clearance surfaces."""

import math
import json
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from machinome.core.serializer import document_version
from machinome.math import floor, piecewise, sin
from machinome.motion.joints import Bound, JointRangeError, Prismatic
from machinome.motion.ports import Time, TranslationalPort
from machinome.node import AssemblyNode
from machinome.simulation import Driver, Follow, Sim, UnsupportedLaw


class Ball(AssemblyNode):
    slide = Prismatic(axis=(1, 0, 0))


def low_direct(low, high):
    return low


def high_direct(low, high):
    return high


class TwoSurfaces(AssemblyNode):
    time = Time.running()
    low = Driver(0.0)
    high = Driver(3.0)
    ball = Ball()
    ball.slide.constrain(range=(
        Bound(lambda travel, low: low, reads=(low,)),
        Bound(lambda travel, high: high, reads=(high,)),
    ))
    (low & high & ball.slide).drives(
        ball.slide, law=Follow(lower=low_direct, upper=high_direct))

    def simulate(self):
        if self.ball.slide.value is None:
            self.ball.slide = 0.0


class SlotSource(AssemblyNode):
    time = Time.running()
    low = Driver(0.0)
    high = Driver(3.0)
    spare = Driver(7.0)
    source = Ball()
    ball = Ball()
    low.drives(source.slide)
    ball.slide.constrain(range=(
        Bound(lambda travel, source: source,
              reads=(source.slide,)),
        Bound(lambda travel, high: high, reads=(high,)),
    ))
    (source.slide & high & ball.slide).drives(
        ball.slide, law=Follow(lower=low_direct, upper=high_direct))

    def simulate(self):
        if self.ball.slide.value is None:
            self.ball.slide = 0.0


class WiredSource(AssemblyNode):
    time = Time.running()
    low = Driver(0.0)
    high = Driver(3.0)
    relay = TranslationalPort(unit='mm')
    source = Ball(slide=relay)
    ball = Ball()
    low.drives(relay, ratio=2.0)
    ball.slide.constrain(range=(
        Bound(lambda travel, source: source, reads=(source.slide,)),
        Bound(lambda travel, high: high, reads=(high,)),
    ))
    (source.slide & high & ball.slide).drives(
        ball.slide, law=Follow(lower=low_direct, upper=high_direct))

    def simulate(self):
        if self.ball.slide.value is None:
            self.ball.slide = 0.0


PEAK = ((0.0, 0.0), (0.25, 2.0), (0.5, 0.0), (1.0, 0.0))
NARROW = ((0.0, 0.0), (0.131, 0.0), (0.133, 1.0),
          (0.135, 0.0), (1.0, 0.0))


def peak_low(low, high):
    return piecewise(low, PEAK)


def narrow_low(low, high):
    return piecewise(low, NARROW)


class InteriorPeak(AssemblyNode):
    time = Time.running()
    low = Driver(0.0)
    high = Driver(3.0)
    ball = Ball()
    ball.slide.constrain(range=(
        Bound(lambda travel, low: piecewise(low, PEAK),
              reads=(low,)),
        Bound(lambda travel, high: high, reads=(high,)),
    ))
    (low & high & ball.slide).drives(
        ball.slide, law=Follow(lower=peak_low, upper=high_direct))

    def simulate(self):
        if self.ball.slide.value is None:
            self.ball.slide = 0.0


class NarrowInversion(AssemblyNode):
    time = Time.running()
    low = Driver(0.0)
    high = Driver(0.5)
    ball = Ball()
    ball.slide.constrain(range=(
        Bound(lambda travel, low: piecewise(low, NARROW),
              reads=(low,)),
        Bound(lambda travel, high: high, reads=(high,)),
    ))
    (low & high & ball.slide).drives(
        ball.slide, law=Follow(lower=narrow_low, upper=high_direct))

    def simulate(self):
        if self.ball.slide.value is None:
            self.ball.slide = 0.0


def closure_only_low(low, high):
    return (2 * low + math.ulp(1.0)) * (low > 0) * (low < .5)


class ClosureOnly(AssemblyNode):
    time = Time.running()
    low = Driver(0.0)
    high = Driver(1.0)
    ball = Ball()
    ball.slide.constrain(range=(
        Bound(lambda travel, low: closure_only_low(low, 0), reads=(low,)),
        Bound(lambda travel, high: high, reads=(high,)),
    ))
    (low & high & ball.slide).drives(
        ball.slide, law=Follow(lower=closure_only_low,
                               upper=high_direct))

    def simulate(self):
        if self.ball.slide.value is None:
            self.ball.slide = 0.0


class ZeroTie(AssemblyNode):
    time = Time.running()
    low = Driver(-0.0)
    high = Driver(0.0)
    spare = Driver(0.0)
    ball = Ball()
    ball.slide.constrain(range=(
        Bound(lambda travel, low: low, reads=(low,)),
        Bound(lambda travel, high: high, reads=(high,)),
    ))
    (low & high & ball.slide).drives(
        ball.slide, law=Follow(lower=low_direct, upper=high_direct))

    def simulate(self):
        if self.ball.slide.value is None:
            self.ball.slide = 0.0


def wrapped_low(low, high):
    return low - 2 * floor(low / 2)


class WrappedEnvelope(AssemblyNode):
    time = Time.running()
    low = Driver(0.0)
    high = Driver(3.0)
    ball = Ball()
    ball.slide.constrain(range=(
        Bound(lambda travel, low: wrapped_low(low, 0), reads=(low,)),
        Bound(lambda travel, high: high, reads=(high,)),
    ))
    (low & high & ball.slide).drives(
        ball.slide, law=Follow(lower=wrapped_low, upper=high_direct))

    def simulate(self):
        if self.ball.slide.value is None:
            self.ball.slide = 0.0


class LongWrappedStop(AssemblyNode):
    time = Time.running()
    low = Driver(0.0)
    high = Driver(1.5)
    ball = Ball()
    ball.slide.constrain(range=(
        Bound(lambda travel, low: wrapped_low(low, 0), reads=(low,)),
        Bound(lambda travel, high: high, reads=(high,)),
    ))
    (low & high & ball.slide).drives(
        ball.slide, law=Follow(lower=wrapped_low, upper=high_direct))

    def simulate(self):
        if self.ball.slide.value is None:
            self.ball.slide = 0.0


def curved_low(low, high):
    return sin(low)


class CurvedEnvelope(AssemblyNode):
    time = Time.running()
    low = Driver(0.0)
    high = Driver(3.0)
    ball = Ball()
    ball.slide.constrain(range=(
        Bound(lambda travel, low: sin(low), reads=(low,)),
        Bound(lambda travel, high: high, reads=(high,)),
    ))
    (low & high & ball.slide).drives(
        ball.slide, law=Follow(lower=curved_low, upper=high_direct))

    def simulate(self):
        if self.ball.slide.value is None:
            self.ball.slide = 0.0


class FollowTest(TestCase):
    def test_periodic_long_request_cannot_alias_every_uniform_probe(self):
        sim = Sim(LongWrappedStop(), dt=1.0)
        command = sim.move('low', to=128.0)
        self.assertEqual(command.status, 'blocked')
        self.assertGreater(sim.state['low'], 1.4)
        self.assertLess(sim.state['low'], 1.6)
        self.assertLessEqual(sim.state['ball.slide'], sim.state['high'])

    def test_curved_envelope_refuses_tick_atomically(self):
        sim = Sim(CurvedEnvelope(), dt=1.0)
        before = sim.snapshot()
        with self.assertRaisesRegex(UnsupportedLaw, 'piecewise affine'):
            sim.move('low', to=1.0)
        self.assertEqual(sim.snapshot(), before)

    def test_wrap_one_sided_peak_retained_and_plan_published(self):
        sim = Sim(WrappedEnvelope(), dt=1.0)
        edge = sim.program.published(dict(sim.initial.bank))['edges'][0]
        self.assertEqual(edge['kind'], 'follow')
        self.assertEqual(edge['lower_plan']['jumps'][0]['primitive'], 'floor')
        self.assertIsNone(edge['upper_plan'])
        self.assertEqual(sim.move('low', to=3.0).status, 'completed')
        self.assertEqual(sim.state['ball.slide'], 2.0)

        from .test_running_document import document
        published = document(WrappedEnvelope())
        fixture = json.loads((Path(__file__).parent / 'fixtures' /
                              'follow_wrapped_v12.json').read_text())
        self.assertEqual(
            {key: published[key] for key in fixture}, fixture)

        corpus = json.loads((Path(__file__).parent / 'fixtures' /
                             'follow_wrapped_commands_v12.json').read_text())
        self.assertEqual(dict(Sim(WrappedEnvelope(), dt=corpus['dt']).state),
                         corpus['initial'])
        replay = Sim(WrappedEnvelope(), dt=corpus['dt'])
        for step in corpus['steps']:
            command = replay.move(step['move']['input'],
                                  to=step['move']['to'])
            self.assertEqual(command.status, step['status'])
            self.assertEqual(dict(replay.state), step['bank'])

    def test_wiring_source_is_refused_not_replaced_by_endpoint_chord(self):
        with self.assertRaisesRegex(UnsupportedLaw, 'endpoint chord'):
            Sim(WiredSource(), dt=1.0)

    def test_quiet_signed_zero_retained_value_is_not_reprojected(self):
        sim = Sim(ZeroTie(), dt=1.0)
        self.assertEqual(math.copysign(1.0, sim.state['ball.slide']), 1.0)
        self.assertEqual(sim.move('spare', to=1.0).status, 'completed')
        self.assertEqual(math.copysign(1.0, sim.state['ball.slide']), 1.0)

    def test_non_driver_source_preserves_all_driver_keys(self):
        sim = Sim(SlotSource(), dt=1.0)
        self.assertEqual(sim.state['spare'], 7.0)
        with patch('machinome.simulation.run.Run._searched_constraint',
                   side_effect=AssertionError('quiet Follow searched Bounds')):
            self.assertEqual(sim.move('spare', to=8.0).status, 'completed')
        self.assertEqual(sim.move('low', to=2.0).status, 'completed')
        self.assertEqual(sim.state['source.slide'], 2.0)
        self.assertEqual(sim.state['ball.slide'], 2.0)

    def test_version_twelve_wire_and_old_program_identity(self):
        sim = Sim(TwoSurfaces(), dt=1.0)
        edges = sim.program.published(dict(sim.initial.bank))['edges']
        self.assertEqual(edges[0]['kind'], 'follow')
        self.assertEqual(edges[0]['needs'], ['low', 'high', 'ball.slide'])
        self.assertEqual(edges[0]['gives'], ['ball.slide'])
        self.assertEqual(str(edges[0]['lower']), 'low')
        self.assertEqual(str(edges[0]['upper']), 'high')
        self.assertEqual(document_version({}, program={'edges': edges}), 12)
        self.assertIn('follow version=12', sim.program.described())

    def test_push_release_and_opposite_surface(self):
        sim = Sim(TwoSurfaces(), dt=1.0)
        self.assertEqual(sim.state['ball.slide'], 0.0)
        self.assertEqual(sim.move('low', to=2.0).status, 'completed')
        self.assertEqual(sim.state['ball.slide'], 2.0)
        self.assertEqual(sim.move('low', to=0.0).status, 'completed')
        self.assertEqual(sim.state['ball.slide'], 2.0)
        self.assertEqual(sim.move('high', to=1.0).status, 'completed')
        self.assertEqual(sim.state['ball.slide'], 1.0)

    def test_interior_peak_survives_one_coarse_tick(self):
        sim = Sim(InteriorPeak(), dt=1.0)
        command = sim.move('low', to=1.0)
        self.assertEqual(command.status, 'completed')
        self.assertEqual(sim.state['low'], 1.0)
        self.assertEqual(sim.state['ball.slide'], 2.0)

    def test_narrow_transient_inversion_stops_between_uniform_probes(self):
        sim = Sim(NarrowInversion(), dt=1.0)
        command = sim.move('low', to=1.0)
        self.assertEqual(command.status, 'blocked')
        self.assertGreater(sim.state['low'], 0.131)
        self.assertLess(sim.state['low'], 0.133)
        self.assertLessEqual(sim.state['ball.slide'], sim.state['high'])

    def test_positive_left_closure_without_positive_float_neighbor_refuses(self):
        self.assertEqual(closure_only_low(.5, 1), 0.0)
        self.assertEqual(closure_only_low(math.nextafter(.5, -math.inf), 1),
                         1.0)
        sim = Sim(ClosureOnly(), dt=1.0)
        before = sim.snapshot()
        with self.assertRaisesRegex(UnsupportedLaw, 'representable neighbor'):
            sim.move('low', to=1.0)
        self.assertEqual(sim.snapshot(), before)

    def test_opposing_sources_stop_and_replay_then_relieve(self):
        sim = Sim(TwoSurfaces(), dt=1.0)
        rest = sim.snapshot()

        def compress():
            lower = sim.move('low', to=2.0, duration=1.0)
            upper = sim.move('high', to=1.0, duration=1.0)
            sim.run(1.0)
            self.assertEqual((lower.status, upper.status),
                             ('blocked', 'blocked'))
            self.assertEqual((sim.state['low'], sim.state['high'],
                              sim.state['ball.slide']), (1.5, 1.5, 1.5))

        compress()
        stopped = sim.snapshot()
        sim.restore(rest)
        compress()
        self.assertEqual(sim.snapshot(), stopped)
        self.assertEqual(sim.move('high', to=2.0).status, 'completed')
        self.assertEqual(sim.state['ball.slide'], 1.5)
        self.assertEqual(sim.move('low', to=2.0).status, 'completed')
        self.assertEqual(sim.state['ball.slide'], 2.0)

    def test_rest_outside_interval_refuses(self):
        class Outside(TwoSurfaces):
            def simulate(self):
                if self.ball.slide.value is None:
                    self.ball.slide = 4.0

        with self.assertRaises((UnsupportedLaw, JointRangeError)):
            Sim(Outside(), dt=1.0)

    def test_inverted_rest_interval_refuses(self):
        class Inverted(AssemblyNode):
            time = Time.running()
            low = Driver(2.0)
            high = Driver(1.0)
            ball = Ball()
            ball.slide.constrain(range=(
                Bound(lambda travel, low: low, reads=(low,)),
                Bound(lambda travel, high: high, reads=(high,))))
            (low & high & ball.slide).drives(
                ball.slide, law=Follow(lower=low_direct,
                                       upper=high_direct))

            def simulate(self):
                if self.ball.slide.value is None:
                    self.ball.slide = 1.5

        with self.assertRaises((UnsupportedLaw, JointRangeError)):
            Sim(Inverted(), dt=1.0)

    def test_missing_source_refuses_relation_shape(self):
        class MissingSource(AssemblyNode):
            time = Time.running()
            low = Driver(0.0)
            ball = Ball()
            (low & ball.slide).drives(
                ball.slide, law=Follow(lower=low_direct,
                                       upper=high_direct))

            def simulate(self):
                if self.ball.slide.value is None:
                    self.ball.slide = 0.0

        with self.assertRaisesRegex(ValueError, 'Follow requires exactly'):
            Sim(MissingSource(), dt=1.0)

    def test_missing_bound_refuses(self):
        class Missing(AssemblyNode):
            time = Time.running()
            low = Driver(0.0)
            high = Driver(3.0)
            ball = Ball()
            ball.slide.constrain(range=(
                Bound(lambda travel, low: low, reads=(low,)), None))
            (low & high & ball.slide).drives(
                ball.slide, law=Follow(lower=low_direct, upper=high_direct))

            def simulate(self):
                if self.ball.slide.value is None:
                    self.ball.slide = 0.0

        with self.assertRaisesRegex(UnsupportedLaw, 'Follow|follow'):
            Sim(Missing(), dt=1.0)

    def test_mismatched_bound_refuses(self):
        class Mismatched(AssemblyNode):
            time = Time.running()
            low = Driver(0.0)
            high = Driver(3.0)
            ball = Ball()
            ball.slide.constrain(range=(
                Bound(lambda travel, low: low, reads=(low,)),
                Bound(lambda travel, high: high + 1, reads=(high,))))
            (low & high & ball.slide).drives(
                ball.slide, law=Follow(lower=low_direct,
                                       upper=high_direct))

            def simulate(self):
                if self.ball.slide.value is None:
                    self.ball.slide = 0.0

        with self.assertRaisesRegex(UnsupportedLaw, 'structurally matching'):
            Sim(Mismatched(), dt=1.0)

    def test_downstream_law_refuses_instead_of_using_endpoint_chord(self):
        class Downstream(TwoSurfaces):
            witness = Ball()
            TwoSurfaces.ball.slide.drives(witness.slide)

        with self.assertRaisesRegex(UnsupportedLaw, 'must be terminal'):
            Sim(Downstream(), dt=1.0)


if __name__ == '__main__':
    import unittest
    unittest.main()
