# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

from machinome.test import TestCase

from .trap import Trap


class TrapTest(TestCase):
    node = Trap

    def test_cubes_do_not_intersect(self):
        self.assertNotIntersecting(self.trap.a, self.trap.b)

    def test_placed_cube_is_where_placed(self):
        self.assertAlmostEqual(
            self.trap.b.mesh.center_mass[0], 10.0, delta=0.01)
