# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The OpenSCAD engine.

This package exports nothing. `machinome.openscad.engine` is the provider
the core's OpenSCAD engine seam (`machinome.scad_engine`) resolves: it
reads a value SolidPython built as the core's expression graph.
`machinome.openscad.binary` is the conditional contract for the OpenSCAD
executable. Import each from its module.
"""
