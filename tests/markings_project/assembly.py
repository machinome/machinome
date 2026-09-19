# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""One tree to read: the dial turning on its bearing above the plate.

The dial's own `turn` is bound from a driver, so the marking can be
asked the question it exists to answer -- turn the part and the decal
goes with it, with nothing about time or the joint in the decal itself.
`PlainBench` is the same tree built from the twins that declare no
marking, which is what the document and geometry comparisons need.
"""

from machinome.node import AssemblyNode
from machinome.simulation import Driver

from .dial import Dial
from .plain_dial import Dial as PlainDial
from .plain_plate import Plate as PlainPlate
from .plate import Plate

#: How high the dial sits above the plate.
DIAL_HEIGHT_ABOVE_PLATE = 20.0


class Bench(AssemblyNode):
    """The marked tree."""

    angle = Driver(default=0.0, unit='deg')

    def __init__(self, **kwargs):
        self.dial = Dial()
        self.plate = Plate()
        super().__init__(**kwargs)

    def render(self):
        self.dial.translate([0, 0, DIAL_HEIGHT_ABOVE_PLATE])
        return [self.dial, self.plate]

    def simulate(self):
        self.dial.turn = self.angle


class PlainBench(AssemblyNode):
    """The same tree, with no marking anywhere in it."""

    angle = Driver(default=0.0, unit='deg')

    def __init__(self, **kwargs):
        self.dial = PlainDial()
        self.plate = PlainPlate()
        super().__init__(**kwargs)

    def render(self):
        self.dial.translate([0, 0, DIAL_HEIGHT_ABOVE_PLATE])
        return [self.dial, self.plate]

    def simulate(self):
        self.dial.turn = self.angle
