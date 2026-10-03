# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

from machinome.test import TestCase

from .occt_only import OcctOnly


class OcctOnlyTest(TestCase):
    node = OcctOnly

    def test_the_probe_overlaps_the_fused_block(self):
        self.assertIntersectVolumeAbove(
            self.occt_only.pinned_block, self.occt_only.probe, 124.9)
        self.assertIntersectVolumeBelow(
            self.occt_only.pinned_block, self.occt_only.probe, 125.1)

    def test_the_far_part_is_clear_of_the_fused_block(self):
        self.assertNotIntersecting(
            self.occt_only.pinned_block, self.occt_only.far)
