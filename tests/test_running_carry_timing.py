# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Physical timing and graph-extension regressions for Curta's carry."""

from machinome.simulation import Sim, TooManyCrossings
from math import sqrt
from unittest.mock import patch

from .base import BaseNodeTest
from .carriage_project.timed_carry import timed_carry, InheritedCrossings
from .carriage_project.machine import FixedZero, ShiftedCarry


def travel(model, portions=1):
    sim = Sim(model(), dt=.1)
    for portion in range(1, portions + 1):
        command = sim.move('crank', to=4 * portion / portions)
        assert command.status == 'completed'
    return dict(sim.state)


class CarryTimingTest(BaseNodeTest):
    def test_inherited_boundaries_do_not_reset_a_laws_crossing_budget(self):
        sim = Sim(InheritedCrossings(), dt=.1, record=32)
        before = dict(sim.state)
        command = sim.move('crank', to=4, duration=.1)
        with patch('machinome.simulation.program._MAX_CROSSINGS', 2):
            with self.assertRaises(TooManyCrossings):
                sim.run(.1)
        self.assertEqual(dict(sim.state), before)
        self.assertEqual(command.status, 'refused')
        self.assertEqual(sim.tick, 0)
        self.assertEqual(sim.crossings, [])

    def test_contact_samples_reuse_the_determined_paths(self):
        sim = Sim(timed_carry(contact=True)(), dt=.1, record=32)
        from machinome.simulation.run import Run
        original = Run._constraint_level
        with patch.object(Run, '_constraint_level', autospec=True,
                          side_effect=original) as replay:
            command = sim.move('crank', to=4)
        self.assertEqual(command.status, 'completed')
        self.assertAlmostEqual(sim.state['higher.turn'], 3.5, places=8)
        self.assertEqual(replay.call_count, 0)

    def test_restricted_queries_are_pure_and_repeatable(self):
        from machinome.simulation.trajectory import Motion
        calls = []
        def curved(t):
            calls.append(t)
            return t*t
        motion = Motion(0, 1, [(0, 1, curved)], affine=False)
        restricted = motion.restrict(.25, .75)
        self.assertEqual(restricted.at(.5), .25)
        count = len(calls)
        self.assertEqual(motion.at(.5), .25)
        self.assertEqual(restricted.at(.5), .25)
        self.assertEqual(len(calls), count)
        self.assertEqual(motion.at(0), 0)
        self.assertEqual(motion.at(1), 1)

    def test_landing_on_an_upstream_kink_is_recorded_once(self):
        sim = Sim(timed_carry(nonuniform=True)(), dt=.1, record=32)
        sim.move('crank', to=4)
        landings = [entry for entry in sim.crossings
                    if entry.coordinate == 'carry.travel']
        self.assertEqual(len(landings), 1)
        self.assertEqual(landings[0].primitive, '<')
        self.assertAlmostEqual(landings[0].t, .125, places=12)

    def test_curved_upstream_gate_uses_the_curve(self):
        state = travel(timed_carry(nonuniform='curved'))
        self.assertAlmostEqual(state['higher.turn'], 4-sqrt(.5), places=8)

    def test_range_uses_the_same_path_as_the_carry(self):
        sim = Sim(timed_carry(bound=2)(), dt=.1)
        command = sim.move('crank', to=4)
        self.assertEqual(command.status, 'blocked')
        self.assertAlmostEqual(command.admitted, 2.5, places=8)
        self.assertEqual(sim.state['higher.turn'], 2)
        self.assertEqual(sim.state['carry.travel'], 1)

    def test_restore_and_reverse_do_not_reuse_an_old_path(self):
        sim = Sim(timed_carry()(), dt=.1, record=32)
        initial = sim.snapshot()
        self.assertEqual(sim.move('crank', to=4).status, 'completed')
        forward = dict(sim.state)
        sim.restore(initial)
        for target in (.25, 1, 4):
            self.assertEqual(sim.move('crank', to=target).status, 'completed')
        for name in forward:
            self.assertAlmostEqual(sim.state[name], forward[name], places=8)
        self.assertEqual(sim.move('crank', to=0).status, 'completed')
        # This fixture's lever is latched; it has no reset law.
        self.assertEqual(sim.state['carry.travel'], 1)
        self.assertAlmostEqual(sim.state['higher.turn'], -.5, places=8)

    def test_ordinary_frozen_chain_has_the_same_physical_timing(self):
        for model in (FixedZero, ShiftedCarry):
            with self.subTest(model=model.__name__):
                whole, divided = travel(model), travel(model, 16)
                self.assertAlmostEqual(whole['higher.turn'], 3.5, places=8)
                for coordinate in whole:
                    self.assertAlmostEqual(whole[coordinate], divided[coordinate],
                                           places=8, msg=coordinate)

    def test_later_station_cannot_change_an_earlier_carry(self):
        original = travel(timed_carry())
        extended = travel(timed_carry(later=True))
        for coordinate in original:
            self.assertAlmostEqual(original[coordinate], extended[coordinate],
                                   places=8, msg=coordinate)

    def test_landed_lever_preserves_its_gate_time(self):
        # Lever reaches its .5 gate at crank .5, then lands at crank 1.
        # Higher follows the remaining 3.5 of crank travel, not a ramp
        # stretching the lever's one-unit stroke across all four units.
        state = travel(timed_carry())
        self.assertEqual(state['carry.travel'], 1)
        self.assertAlmostEqual(state['higher.turn'], 3.5, places=8)

    def test_nonuniform_upstream_motion_preserves_gate_time(self):
        # The upstream shaft turns twice as fast, then dwells at crank .5.
        # The lever reaches .5 at crank .25, leaving 3.75 of driven travel.
        state = travel(timed_carry(nonuniform=True))
        self.assertEqual(state['carry.travel'], 1)
        self.assertAlmostEqual(state['higher.turn'], 3.75, places=8)

    def test_whole_request_agrees_with_portions(self):
        for later in (False, True):
            for nonuniform in (False, True):
                with self.subTest(later=later, nonuniform=nonuniform):
                    model = timed_carry(later=later, nonuniform=nonuniform)
                    whole, divided = travel(model), travel(model, 16)
                    for coordinate in whole:
                        self.assertAlmostEqual(whole[coordinate], divided[coordinate],
                                               places=8, msg=coordinate)
