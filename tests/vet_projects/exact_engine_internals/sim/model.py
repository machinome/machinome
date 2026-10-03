# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

from machinome.node import AssemblyNode
from machinome.occt.engine import write_brep
import machinome.exact_artifacts
from machinome.occt.engine import intersect_shapes, placed_shape, solid_volume
from machinome.exact_engine import ExactCommonInconsistency

LOAD = machinome.exact_cache.cached_shape
OPERATIONS = (write_brep, intersect_shapes, placed_shape, solid_volume,
              ExactCommonInconsistency)


class Machine(AssemblyNode):
    pass
