# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The root of the SCAD presentation golden, declared in package `tools`
so that every part it places, declared in the parent package, is imported
across packages and its imports are re-anchored (ADR-116)."""

from machinome.node import AssemblyNode

from ..parts import (Block, Bracket, Coil, Empty, FineCylinder, Fused,
                     Legacy, OwnImport, Plate, Single, Unoptimized)


class Bench(AssemblyNode):

    def render(self):
        coil = Coil()
        coil.height = 12.0
        return [
            Single().rotate(30, [0, 0, 1]),
            Empty(),
            Unoptimized().translate([1, 2.5, 0]),
            FineCylinder().translate([10, 0, 0]),
            Bracket().translate([0, 20, 0]),
            Block().rotate(self.time * 360, [0, 0, 1]),
            Fused().translate([-10, 0, 0]),
            coil.translate([0, -15, 0]),
            Plate().translate([20, 20, 0]),
            Legacy().rotate(90, [1, 0, 0]),
        ]


class Loose(AssemblyNode):
    """Assembled for its SCAD and never built to STL: its one part imports
    a file of the project's own that does not exist, whose path the SCAD
    must carry exactly as written."""

    def render(self):
        return [OwnImport()]
