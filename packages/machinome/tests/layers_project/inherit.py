# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Layers over the class hierarchy: a subclass and a plain mixin add."""

from solid2 import cube

from machinome.node.solid2 import Solid2Node

from .layers import ELECTRICAL, MECHANICAL


class Base(Solid2Node):
    layers = ELECTRICAL

    def render(self):
        return cube(2)


class Derived(Base):
    layers = MECHANICAL


class Copper:
    layers = ELECTRICAL


class Mixed(Copper, Solid2Node):
    layers = MECHANICAL

    def render(self):
        return cube(2)


class Plain(Copper, Solid2Node):
    def render(self):
        return cube(2)
