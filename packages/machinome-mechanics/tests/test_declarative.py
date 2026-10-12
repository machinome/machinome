# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Additional coverage for machinome's unreleased declarative API."""

from unittest import TestCase
import pytest

pytest.importorskip('machinome.parameters')
from machinome.node import AssemblyNode
from machinome.parameters import Angle, DimensionError
from machinome_mechanics import meshed_angle


class DeclaredFaceTest(TestCase):
    """There is no third face: a declared token reaching a law raises
    the algebra's own dimension error at class definition, and `.value`
    is the documented way through."""

    def test_a_declared_angle_is_refused(self):
        with self.assertRaises(DimensionError):
            class Pair(AssemblyNode):
                theta = Angle(10.0)
                driven = meshed_angle(theta, 12, 24)

    def test_the_escape_hatch_computes_a_static_phase(self):
        class Pair(AssemblyNode):
            theta = Angle(10.0)
            driven = meshed_angle(theta.value, 12, 24)

        self.assertAlmostEqual(Pair().driven, 175.0)
