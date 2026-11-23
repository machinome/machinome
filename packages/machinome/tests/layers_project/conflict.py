# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Two different layers sharing one key in one machine, as one tree."""

from solid2 import cube

from machinome.layers import Layer
from machinome.node.assembly import AssemblyNode
from machinome.node.solid2 import Solid2Node

from .layers import ELECTRICAL

#: A second object of the key `electrical`, with another label.
WIRES = Layer('electrical', label='Wires')

#: A second object of the key `electrical`, with an EQUAL label: still a
#: second layer, never the same one.
TWIN = Layer('electrical', label='Electrical path')


class First(Solid2Node):
    layers = ELECTRICAL

    def render(self):
        return cube(2)


class Second(Solid2Node):
    layers = WIRES

    def render(self):
        return cube(2)


class Twin(Solid2Node):
    layers = TWIN

    def render(self):
        return cube(2)


class Conflicted(AssemblyNode):
    first = First()
    second = Second()


class Twinned(AssemblyNode):
    first = First()
    twin = Twin()


class Separate(AssemblyNode):
    """The same two objects, each in its own machine: no conflict."""

    first = First()


class Elsewhere(AssemblyNode):
    """Another machine whose layer of the key `electrical` is WIRES."""

    second = Second()
