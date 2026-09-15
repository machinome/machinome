# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The same plate, declaring no marking.

`plain_plate.stl` is a byte-for-byte copy of `plate.stl`: the two parts
must produce the same artifact, and an `StlNode`'s artifact basename is
derived from the mesh file it names, so the twin needs a file of its own
to have an artifact path of its own.
"""

from solid_node.node import StlNode


class Plate(StlNode):
    """`plate.Plate` without its decals."""

    stl_source = 'plain_plate.stl'
