# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Unresolved precision finding exposed after correcting landing direction."""

from machinome.simulation import Sim
from .base import BaseNodeTest
from .mixed_threshold_project import FollowingContact


class FollowingContactReproTest(BaseNodeTest):
    def test_following_a_moving_pin_is_not_an_impossible_sliding_mode(self):
        sim = Sim(FollowingContact(), .1)
        self.assertEqual(sim.move('crank', to=1).status, 'completed')
        self.assertAlmostEqual(sim.state['follower.turn'], -3.2+1/7)
