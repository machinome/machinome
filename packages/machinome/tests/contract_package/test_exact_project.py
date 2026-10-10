# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

import math

from machinome.test import TestCase

from .exact_project import ExactProject

#: The half of an r = 3 pin with x > 0, over 5 mm of its height.
HALF_PIN = math.pi * 3 ** 2 * 5 / 2


class ExactProjectTest(TestCase):
    node = ExactProject

    def test_the_probe_cuts_half_the_native_pin(self):
        self.assertIntersectVolumeAbove(
            self.exact_project.pin, self.exact_project.probe,
            HALF_PIN - 0.01)
        self.assertIntersectVolumeBelow(
            self.exact_project.pin, self.exact_project.probe,
            HALF_PIN + 0.01)

    def test_the_clamp_is_clear_of_the_native_pin(self):
        self.assertNotIntersecting(
            self.exact_project.pin, self.exact_project.clamp)

    def test_the_fused_block_is_clear_of_the_native_pin(self):
        self.assertNotIntersecting(
            self.exact_project.pinned_block, self.exact_project.pin)
