# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from unittest.mock import patch

from machinome.core.serializer import document_version
from machinome.motion.couplings import CouplingError
from machinome.motion.joints import Revolute
from machinome.motion.ports import Time
from machinome.node import AssemblyNode
from machinome.simulation import Driver, Play, Sim
from machinome.simulation import UnsupportedLaw
from machinome.viewers.browser import BrowserRenderer, BrowserSnapshotError


class Wheel(AssemblyNode):
    turn = Revolute(axis=(1, 0, 0))


class PlayTrain(AssemblyNode):
    time = Time.running()
    x = Driver(0.0)
    y = Wheel()
    z = Wheel()
    (x & y.turn).drives(y.turn, law=Play(low=-10.0, high=10.0))
    (y.turn & z.turn).drives(z.turn, law=Play(low=-10.0, high=10.0))

    def simulate(self):
        for wheel in (self.y, self.z):
            if wheel.turn.value is None:
                wheel.turn = 0.0


class PlayTest(TestCase):
    def test_pickup_release_and_cascade(self):
        sim = Sim(PlayTrain(), 1.0)
        sim.move('x', by=100.0, duration=0)
        self.assertEqual(sim.state, {'x': 100.0, 'y.turn': 90.0,
                                     'z.turn': 80.0})
        sim.move('x', by=-5.0, duration=0)
        self.assertEqual(sim.state, {'x': 95.0, 'y.turn': 90.0,
                                     'z.turn': 80.0})

    def test_wire_shape_and_identity(self):
        sim = Sim(PlayTrain(), 1.0)
        edges = sim.program.published(dict(sim.initial.bank))['edges']
        self.assertEqual(edges[0]['kind'], 'play')
        self.assertEqual(edges[0]['needs'], ['x', 'y.turn'])
        self.assertEqual(edges[0]['gives'], ['y.turn'])
        self.assertEqual((edges[0]['low'], edges[0]['high']), (-10.0, 10.0))
        self.assertEqual(len(sim.program.identity), 64)
        self.assertEqual(document_version({}, program={'edges': edges}), 11)

    def test_an_old_viewer_refuses_version_nine(self):
        report = {'documentVersions': list(range(1, 9)), 'version': '0.1.0'}
        with patch('machinome.viewers.bundle.describe', return_value=report):
            with self.assertRaisesRegex(BrowserSnapshotError,
                                        'version 9.*1.*8'):
                BrowserRenderer().refuse_unreadable(9)

    def test_invalid_offsets(self):
        for low, high in ((0, 0), (2, 1), (float('nan'), 1),
                          (0, float('inf'))):
            with self.subTest(low=low, high=high):
                with self.assertRaisesRegex(ValueError, 'finite.*low < high'):
                    Play(low=low, high=high)

    def test_invalid_rest_is_not_projected(self):
        class Invalid(AssemblyNode):
            time = Time.running()
            x = Driver(100.0)
            wheel = Wheel()
            (x & wheel.turn).drives(wheel.turn,
                                    law=Play(low=-10.0, high=10.0))

            def simulate(self):
                if self.wheel.turn.value is None:
                    self.wheel.turn = 0.0

        with self.assertRaisesRegex(UnsupportedLaw, 'admissible interval'):
            Sim(Invalid(), 1.0)

    def test_play_fanout_is_refused(self):
        class Branched(AssemblyNode):
            time = Time.running()
            x = Driver(0.0)
            a = Wheel()
            b = Wheel()
            (x & a.turn).drives(a.turn, law=Play(-10.0, 10.0))
            (x & b.turn).drives(b.turn, law=Play(-10.0, 10.0))

            def simulate(self):
                for wheel in (self.a, self.b):
                    if wheel.turn.value is None:
                        wheel.turn = 0.0

        with self.assertRaisesRegex(UnsupportedLaw, 'fan-out'):
            Sim(Branched(), 1.0)

    def test_play_requires_running_exact_ordered_shape(self):
        class NotRunning(AssemblyNode):
            x = Driver(0.0)
            wheel = Wheel()
            (x & wheel.turn).drives(wheel.turn, law=Play(-10.0, 10.0))

        with self.assertRaisesRegex((ValueError, CouplingError),
                                    'running|Time.running'):
            Sim(NotRunning(), 1.0)

        class Reordered(AssemblyNode):
            time = Time.running()
            x = Driver(0.0)
            wheel = Wheel()
            (wheel.turn & x).drives(wheel.turn, law=Play(-10.0, 10.0))

            def simulate(self):
                if self.wheel.turn.value is None:
                    self.wheel.turn = 0.0

        with self.assertRaisesRegex(ValueError, 'Play requires exactly'):
            Sim(Reordered(), 1.0)

    def test_play_malformed_sources_are_refused_before_law_solving(self):
        class MissingRetained(AssemblyNode):
            time = Time.running()
            x = Driver(0.0)
            wheel = Wheel()
            x.drives(wheel.turn, law=Play(-10.0, 10.0))

        class DifferentTarget(AssemblyNode):
            time = Time.running()
            x = Driver(0.0)
            retained = Wheel()
            target = Wheel()
            (x & retained.turn).drives(
                target.turn, law=Play(-10.0, 10.0))

        class GroupSource(AssemblyNode):
            time = Time.running()
            x = Driver(0.0)
            retained = Wheel()
            extra = Wheel()
            (x & retained.turn & extra.turn).drives(
                retained.turn, law=Play(-10.0, 10.0))

        for declaration in (MissingRetained, DifferentTarget, GroupSource):
            with self.subTest(declaration=declaration.__name__):
                with self.assertRaisesRegex(ValueError,
                                            'Play requires exactly'):
                    Sim(declaration(), 1.0)

        with self.assertRaisesRegex(TypeError, 'named twice'):
            class SameSource(AssemblyNode):
                time = Time.running()
                wheel = Wheel()
                (wheel.turn & wheel.turn).drives(
                    wheel.turn, law=Play(-10.0, 10.0))

    def test_an_ordinary_relation_cannot_source_play(self):
        class OrdinarySource(AssemblyNode):
            time = Time.running()
            x = Driver(0.0)
            middle = Wheel()
            last = Wheel()
            x.drives(middle.turn)
            (middle.turn & last.turn).drives(
                last.turn, law=Play(-10.0, 10.0))

            def simulate(self):
                if self.last.turn.value is None:
                    self.last.turn = 0.0

        with self.assertRaisesRegex(UnsupportedLaw, 'not a run-owned driver'):
            Sim(OrdinarySource(), 1.0)
