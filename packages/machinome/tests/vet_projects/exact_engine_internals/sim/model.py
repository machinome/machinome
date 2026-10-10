# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

from machinome.node.assembly import AssemblyNode
from machinome.engine.brep import write_brep
import machinome.brep_artifacts
from machinome.engine.brep import intersect_shapes, placed_shape, solid_volume
from machinome.engine import BrepCommonInconsistency

LOAD = machinome.brep_cache.cached_shape
OPERATIONS = (write_brep, intersect_shapes, placed_shape, solid_volume,
              BrepCommonInconsistency)


class Machine(AssemblyNode):
    pass
