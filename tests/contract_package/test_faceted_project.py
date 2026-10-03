# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

from machinome.test import TestCase

from .faceted_project import FacetedProject


class FacetedProjectTest(TestCase):
    node = FacetedProject

    def test_the_two_cubes_are_apart(self):
        self.assertNotIntersecting(
            self.faceted_project.near, self.faceted_project.far)
