# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The same plate, declaring no marking.

`plain_plate.stl` is a byte-for-byte copy of `plate.stl`: the two parts
must produce the same solid bytes and piece identity. Their external-wrapper
keys differ because their defining Python sources differ (ADR-155), independently
of the markings. The separate asset file also keeps their original mirrored
artifact locations independent.
"""

from machinome.node import StlNode


class Plate(StlNode):
    """`plate.Plate` without its decals."""

    stl_source = 'plain_plate.stl'
