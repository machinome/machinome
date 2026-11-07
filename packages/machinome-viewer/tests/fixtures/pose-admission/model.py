# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""Authored rendered-pose admission fixture. No Enigma geometry or mechanics."""

from machinome.math import floor, sqrt
from machinome.math import min as minimum
from machinome.motion.joints import Revolute
from machinome.node.assembly import AssemblyNode
from machinome.node.stl import StlNode
from machinome.simulation import Driver, Instruction, State


def events(sources, targets):
    return lambda press, count: floor(press)


def increment(sources, targets):
    return lambda press, count: count + 1


class Body(StlNode):
    stl_source = "tetrahedron.stl"
    color = "#d65b24"


class Arm(AssemblyNode):
    turn = Revolute(axis=(0, 0, 1), unit="deg")
    body = Body()

    def render(self):
        self.body.translate((5, 0, 0))


class PoseAdmission(AssemblyNode):
    press = Driver(0.0, range=(0.0, 2.0), unit="mm")
    independent = Driver(0.0, range=(-1.0, 1.0), unit="mm")
    count = State(0, dtype=int)
    earlier = Body()
    arm = Arm()
    (press & count).commits(count, at=events, law=increment)
    instructions = {"Invalid": Instruction({"press": 3.0}, duration=0.1)}

    def render(self):
        self.earlier.translate((-15, -10, 0))
        self.arm.translate((10, 10, 0))

    def simulate(self):
        shared = self.press * 10
        self.earlier.translate((shared + self.independent, 0, 0))
        self.arm.turn = shared * 3 + sqrt(
            minimum(0.0, minimum(self.press, 2.0 - self.press))
        )
