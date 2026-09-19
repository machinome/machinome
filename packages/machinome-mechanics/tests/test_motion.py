# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""An extracted nonlinear helper supplies a current machinome motion law."""

import math
import pytest

pytest.importorskip("machinome.motion")
from solid2.core.object_base import OpenSCADConstant
from machinome.core.serializer import symbolic_document
from machinome.motion.joints import Prismatic
from machinome.node import AssemblyNode
from machinome.simulation import Driver
from machinome_mechanics import piston_height


class Piston(AssemblyNode):
    rise = Prismatic(axis=(0, 0, 1), unit="mm")


def slider_crank(crank, piston):
    return lambda angle: piston_height(angle, 15, 60)


class Engine(AssemblyNode):
    crank = Driver(default=0.0, unit="deg")
    piston = Piston()
    crank.drives(piston.rise, law=slider_crank)


def test_a_helper_drives_a_joint_at_numeric_states():
    engine = Engine()
    for angle, height in [(0, 75), (90, math.sqrt(3375)), (180, 45)]:
        engine.set_state(crank=angle)
        engine.render()
        assert engine.piston.rise.value == pytest.approx(height)


def test_the_realized_law_preserves_symbolic_math():
    engine = Engine()
    engine.set_state(crank=0)
    with symbolic_document(engine):
        engine.render()
        result = engine.piston.rise.value
        assert isinstance(result, OpenSCADConstant)
        assert "crank" in str(result)
        assert "sqrt(" in str(result)
    assert engine.piston.rise.value == 75
