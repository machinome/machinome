# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

from machinome.test import TestCase

from .two_arbors import TwoArbors


class TwoArborsTest(TestCase):
    node = TwoArbors

    def test_no_interference(self):
        """Deliberately red: the two arbors' wheels overlap, and the
        failure must name each wheel by its path."""
        self.assertNoSolidInterference(self.node)

    def test_wheels_apart(self):
        """Deliberately red: the same pair, asked directly."""
        self.assertNotIntersecting(self.node.centre.wheel, self.node.third.wheel)
