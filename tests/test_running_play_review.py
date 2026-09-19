# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Independent adversarial acceptance for the Vault's retained pickup.

These fixtures do not import the implementation author's fixtures or oracle.
The reference advances contact geometrically, using a branch on the gap.
"""

import copy
import json
from pathlib import Path
import random
import unittest
from unittest.mock import patch

from machinome.motion.joints import Revolute
from machinome.motion.ports import Time, get_coordinate
from machinome.node import AssemblyNode
from machinome.simulation import Driver, Play, Sim
from machinome.simulation.run import StopInvariantError


CONTACTS = ((-328.7788108, 3.2757369),
            (-237.0991722, 94.9784270),
            (-231.6311303, 100.2710715))


def contacted(source, retained, low, high):
    gap = source - retained
    if gap > high:
        return source - high
    if gap < low:
        return source - low
    return retained


def machine(contacts=CONTACTS, initial=0.0, bounded=False, observer_bound=False,
            observer_square=False, observer_mix=False):
    class Wheel(AssemblyNode):
        turn = Revolute(axis=(1, 0, 0))

    class Last(AssemblyNode):
        turn = Revolute(axis=(1, 0, 0),
                        range=(-20, 20) if bounded else None)

    class Observer(AssemblyNode):
        turn = Revolute(axis=(1, 0, 0),
                        range=((None, 400) if observer_square else
                               (-40, 40) if observer_bound else None))

    def squared(source, target):
        return lambda angle: angle * angle

    def mixed(sources, target):
        return lambda wheel, motor: wheel + motor

    class Bank(AssemblyNode):
        time = Time.running()
        dial = Driver(default=initial, unit='deg')
        motor = Driver(default=0, unit='deg')
        first = Wheel()
        second = Wheel()
        third = Last()
        cam = Wheel()
        observer = Observer()
        independent = Wheel()
        (dial & first.turn).drives(first.turn, law=Play(
            low=contacts[0][0], high=contacts[0][1]))
        (first.turn & second.turn).drives(second.turn, law=Play(
            low=contacts[1][0], high=contacts[1][1]))
        (second.turn & third.turn).drives(third.turn, law=Play(
            low=contacts[2][0], high=contacts[2][1]))
        dial.drives(cam.turn)
        if observer_mix:
            (third.turn & motor).drives(observer.turn, law=mixed)
        elif observer_square:
            third.turn.drives(observer.turn, law=squared)
        else:
            third.turn.drives(observer.turn, ratio=-2)
        motor.drives(independent.turn)

        def simulate(self):
            for wheel in (self.first, self.second, self.third):
                if wheel.turn.value is None:
                    wheel.turn = initial

    return Bank()


def move(sim, target, duration=1.0):
    command = sim.move('dial', to=target, duration=duration)
    sim.run(duration)
    return command


class PlayAdversarialReviewTest(unittest.TestCase):
    def test_corpus_refuses_removed_play_behaviors_not_just_missing_edges(self):
        from tools.generate_running_corpus import uncovered_features
        fixture = json.loads(Path(__file__).with_name(
            'running-corpus.json').read_text())['machines']
        cases = ('split play requests', 'play retention and reversal release',
                 'a downstream play stop located from its driver')
        for feature in cases:
            with self.subTest(feature=feature):
                changed = copy.deepcopy(fixture)
                for entry in changed:
                    edges = [edge for edge in entry['document'].get(
                        'program', {}).get('edges', ()) if edge['kind'] == 'play']
                    if not edges:
                        continue
                    if feature == cases[0]:
                        entry['script'] = [action for action in entry['script']
                                           if 'move' not in action]
                    elif feature == cases[1]:
                        retained = edges[0]['gives'][0]
                        for index, tick in enumerate(entry['ticks']):
                            tick['bank'][retained] += index * 0.125
                    else:
                        for tick in entry['ticks']:
                            for stop in tick['stops']:
                                stop['coordinate'] = edges[0]['needs'][0]
                self.assertIn(feature, uncovered_features(changed))

    def test_refusal_after_play_projection_leaves_no_partial_tick(self):
        node = machine()
        sim = Sim(node, dt=1, record=16)
        move(sim, 1590)
        before = (sim.state, sim.tick, list(sim.crossings), list(sim.stops),
                  list(sim.trajectory))
        command = sim.move('dial', to=2000, duration=1)
        propagate = sim._run._pass

        def refuse_after_projection(*args, **kwargs):
            propagate(*args, **kwargs)
            raise StopInvariantError('review injection after play projection')

        with patch.object(sim._run, '_pass', refuse_after_projection):
            with self.assertRaisesRegex(StopInvariantError, 'review injection'):
                sim.run(1)
        self.assertEqual((sim.state, sim.tick, list(sim.crossings),
                          list(sim.stops), list(sim.trajectory)), before)
        self.assertEqual((command.status, command.admitted), ('refused', 0))
        for name in ('first', 'second', 'third'):
            self.assertEqual(get_coordinate(getattr(node, name), 'turn')._value,
                             sim.state[name + '.turn'])

    def test_play_cycles_and_wrong_targets_are_refused(self):
        class Wheel(AssemblyNode):
            turn = Revolute(axis=(1, 0, 0))

        class Cycle(AssemblyNode):
            time = Time.running()
            a = Wheel()
            b = Wheel()
            (a.turn & b.turn).drives(b.turn, law=Play(-10, 10))
            (b.turn & a.turn).drives(a.turn, law=Play(-10, 10))

            def simulate(self):
                for wheel in (self.a, self.b):
                    if wheel.turn.value is None:
                        wheel.turn = 0

        with self.assertRaisesRegex(ValueError, 'cycle|Cycle|cyclic'):
            Sim(Cycle(), dt=1)

        class WrongTarget(AssemblyNode):
            time = Time.running()
            x = Driver(0)
            a = Wheel()
            b = Wheel()
            (x & a.turn).drives(b.turn, law=Play(-10, 10))

            def simulate(self):
                if self.a.turn.value is None:
                    self.a.turn = 0

        with self.assertRaisesRegex(ValueError, 'Play|play|running shape'):
            Sim(WrongTarget(), dt=1)

    def test_seeded_reversals_cadence_and_downstream_observers(self):
        rng = random.Random(740370)
        path = [2, 360, 1590, 1580, 672, 720, 1182, 1140]
        path += [rng.uniform(-3000, 3000) for _ in range(32)]
        for dt in (1.0, 0.1, 0.02):
            with self.subTest(dt=dt):
                node = machine()
                sim = Sim(node, dt=dt)
                held = [0.0] * 3
                for target in path:
                    source = target
                    for i, (low, high) in enumerate(CONTACTS):
                        held[i] = contacted(source, held[i], low, high)
                        source = held[i]
                    command = move(sim, target)
                    self.assertEqual(command.status, 'completed')
                    for name, wanted in zip(('first', 'second', 'third'), held):
                        self.assertAlmostEqual(sim.state[name + '.turn'],
                                               wanted, delta=1e-8)
                        self.assertEqual(
                            get_coordinate(getattr(node, name), 'turn')._value,
                            sim.state[name + '.turn'])
                    self.assertAlmostEqual(sim.state['cam.turn'], target,
                                           delta=1e-8)
                    self.assertAlmostEqual(sim.state['observer.turn'],
                                           -2 * held[-1], delta=1e-8)

    def test_third_wheel_stop_clips_only_the_pushing_input(self):
        for dt in (1.0, 0.1, 0.02):
            with self.subTest(dt=dt):
                sim = Sim(machine(((-10, 10),) * 3, bounded=True),
                          dt=dt, record=128)
                motor = sim.move('motor', by=7, duration=1)
                first = move(sim, 100)
                self.assertEqual(first.status, 'blocked')
                self.assertEqual(motor.status, 'completed')
                for key, value in (('dial', 50), ('first.turn', 40),
                                   ('second.turn', 30), ('third.turn', 20),
                                   ('cam.turn', 50), ('observer.turn', -40),
                                   ('motor', 7), ('independent.turn', 7)):
                    self.assertAlmostEqual(sim.state[key], value, delta=1e-8)
                self.assertAlmostEqual(first.admitted, 50, delta=1e-8)

                blocked = move(sim, 100)
                self.assertEqual((blocked.status, blocked.admitted),
                                 ('blocked', 0))
                released = move(sim, -9)
                self.assertEqual(released.status, 'completed')
                self.assertEqual(sim.state['third.turn'], 20)
                negative = move(sim, -100)
                self.assertEqual(negative.status, 'blocked')
                for key, value in (('dial', -50), ('first.turn', -40),
                                   ('second.turn', -30), ('third.turn', -20)):
                    self.assertAlmostEqual(sim.state[key], value, delta=1e-8)

    def test_large_offset_release_is_bit_identical(self):
        initial = 1e12
        sim = Sim(machine(((-329, 3),) * 3, initial=initial), dt=1)
        move(sim, initial + 1590)
        held = [sim.state[name + '.turn']
                for name in ('first', 'second', 'third')]
        move(sim, initial + 1580)
        self.assertEqual([sim.state[name + '.turn']
                          for name in ('first', 'second', 'third')], held)

    def test_a_wheel_still_at_its_stop_allows_recollecting_clearance(self):
        for dt in (1.0, 0.1):
            with self.subTest(dt=dt):
                sim = Sim(machine(((-10, 10),) * 3, bounded=True), dt=dt)
                move(sim, 100)
                move(sim, 40)
                self.assertEqual(sim.state['third.turn'], 20)
                recollect = move(sim, 60)
                self.assertEqual(recollect.status, 'blocked')
                self.assertAlmostEqual(recollect.admitted, 10, delta=1e-9)
                self.assertAlmostEqual(sim.state['dial'], 50, delta=1e-9)
                move(sim, -100)
                move(sim, -40)
                self.assertEqual(sim.state['third.turn'], -20)
                recollect = move(sim, -60)
                self.assertEqual(recollect.status, 'blocked')
                self.assertAlmostEqual(recollect.admitted, -10, delta=1e-9)
                self.assertAlmostEqual(sim.state['dial'], -50, delta=1e-9)

    def test_a_bounded_downstream_observer_cannot_break_the_chain_pose(self):
        for dt in (1.0, 0.1):
            with self.subTest(dt=dt):
                sim = Sim(machine(((-10, 10),) * 3, observer_bound=True), dt=dt)
                command = move(sim, 100)
                self.assertEqual(command.status, 'blocked')
                self.assertAlmostEqual(sim.state['dial'], 50, delta=1e-9)
                self.assertAlmostEqual(sim.state['third.turn'], 20, delta=1e-9)
                self.assertAlmostEqual(sim.state['observer.turn'], -40,
                                       delta=1e-9)
                move(sim, 40)
                recollect = move(sim, 100)
                self.assertEqual(recollect.status, 'blocked')
                self.assertAlmostEqual(sim.state['dial'], 50, delta=1e-9)

    def test_nonlinear_observer_can_recollect_and_move_through_its_inside(self):
        sim = Sim(machine(((-10, 10),) * 3, observer_square=True), dt=1)
        move(sim, 100)
        self.assertAlmostEqual(sim.state['dial'], 50, delta=1e-8)
        move(sim, 40)
        command = move(sim, 100)
        self.assertEqual(command.status, 'blocked')
        self.assertAlmostEqual(command.admitted, 10, delta=1e-8)
        self.assertAlmostEqual(sim.state['dial'], 50, delta=1e-8)
        # The squared observer leaves its high bound INWARD, crosses zero,
        # and reaches the same bound from the opposite direction. Neither
        # its initial plateau nor its first inward movement is a stop.
        command = move(sim, -100)
        self.assertEqual(command.status, 'blocked')
        self.assertAlmostEqual(sim.state['dial'], -50, delta=1e-8)
        self.assertAlmostEqual(sim.state['third.turn'], -20, delta=1e-8)
        self.assertEqual(sim.state['observer.turn'], 400)

    def test_large_travel_back_to_zero_keeps_chain_on_same_landings(self):
        sim = Sim(machine(((-329, 3),) * 3), dt=1)
        for destination in (1e16, 0, -1e16, 0):
            previous = [sim.state[name + '.turn']
                        for name in ('first', 'second', 'third')]
            move(sim, destination)
            source = sim.state['dial']
            for name, retained in zip(('first', 'second', 'third'), previous):
                wanted = max(source - 3, min(retained, source + 329))
                self.assertEqual(sim.state[name + '.turn'], wanted)
                source = wanted

    def test_multisource_bounded_observer_replays_the_play_prefix(self):
        sim = Sim(machine(((-10, 10),) * 3, observer_bound=True,
                          observer_mix=True), dt=1)
        sim.move('motor', by=7, duration=1)
        sim.run(1)
        command = move(sim, 100)
        self.assertEqual(command.status, 'blocked')
        self.assertAlmostEqual(sim.state['dial'], 63, delta=1e-8)
        self.assertAlmostEqual(sim.state['third.turn'], 33, delta=1e-8)
        self.assertEqual(sim.state['observer.turn'], 40)
        self.assertEqual(sim.state['motor'], 7)
        move(sim, 53)
        command = move(sim, 100)
        self.assertEqual(command.status, 'blocked')
        self.assertAlmostEqual(sim.state['dial'], 63, delta=1e-8)
        command = move(sim, -100)
        self.assertEqual(command.status, 'blocked')
        self.assertAlmostEqual(sim.state['dial'], -77, delta=1e-8)
        self.assertAlmostEqual(sim.state['third.turn'], -47, delta=1e-8)
        self.assertEqual(sim.state['observer.turn'], -40)
        self.assertEqual(sim.state['motor'], 7)

    def test_a_terminal_play_coordinate_cannot_have_another_writer(self):
        class Wheel(AssemblyNode):
            turn = Revolute(axis=(1, 0, 0))

        class Ambiguous(AssemblyNode):
            time = Time.running()
            x = Driver(default=0)
            other = Driver(default=0)
            wheel = Wheel()
            (x & wheel.turn).drives(wheel.turn, law=Play(low=-10, high=10))
            other.drives(wheel.turn)

        with self.assertRaisesRegex(ValueError, 'writer|ambiguous|Play|play'):
            Sim(Ambiguous(), dt=1)

    def test_restore_mid_command_replays_to_same_bank(self):
        sim = Sim(machine(), dt=0.1, record=64)
        sim.move('dial', by=1440, duration=1)
        sim.run(0.3)
        saved = sim.snapshot()
        sim.run(0.7)
        completed = sim.state
        sim.restore(saved)
        sim.run(0.7)
        self.assertEqual(sim.state, completed)
        sim.reset()
        self.assertEqual(sim.state['dial'], 0)
        self.assertTrue(all(value == 0 for value in sim.state.values()))

    def test_gap_offsets_are_part_of_snapshot_identity(self):
        sim = Sim(machine(), dt=1)
        move(sim, 1590)
        snapshot = sim.snapshot()
        changed = Sim(machine(((-328, 3),) * 3), dt=1)
        before = changed.snapshot()
        with self.assertRaises(ValueError):
            changed.restore(snapshot)
        self.assertEqual(changed.snapshot(), before)
