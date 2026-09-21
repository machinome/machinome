# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

from machinome.simulation import Sim
from .base import BaseNodeTest
from .mixed_threshold_project import (OvertakenFollower, ObservedFollower,
                                      NegativeFollower, StationaryFollower)


class MixedThresholdLandingTest(BaseNodeTest):
    def test_threshold_overtakes_in_both_directions_and_under_observation(self):
        for cls, direction in ((OvertakenFollower, 1), (ObservedFollower, 1),
                               (NegativeFollower, -1)):
            with self.subTest(machine=cls.__name__):
                sim = Sim(cls(), .1, record=16)
                before = sim.snapshot()
                self.assertEqual(sim.move('crank', to=2*direction).status, 'completed')
                # q=2+x before x=1, then q=3+.5*(x-1); reflected below zero.
                self.assertAlmostEqual(sim.state['follower.turn'], 3.5*direction)
                after = sim.snapshot()
                sim.restore(before)
                self.assertEqual(sim.move('crank', to=2*direction).status, 'completed')
                self.assertEqual(sim.snapshot(), after)
                self.assertEqual(sim.move('crank', to=3*direction).status, 'completed')
                self.assertAlmostEqual(sim.state['follower.turn'], 4*direction)

    def test_source_only_crossing_does_not_reposition_a_stationary_follower(self):
        sim = Sim(StationaryFollower(), .1)
        self.assertEqual(sim.move('crank', to=1).status, 'completed')
        # Held at 2 until the threshold reaches it at x=.5, then rate 1.
        self.assertEqual(sim.state['follower.turn'], 2.5)
