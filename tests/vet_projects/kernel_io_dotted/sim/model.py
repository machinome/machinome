# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

from machinome.node import AssemblyNode
import numpy as np
import trimesh
import cadquery as cq
import cadquery.importers
from build123d import import_step

from . import blueprints

TABLE = np.load('table.npy')
RANGE = np.linspace(0, 1, 5)
PIN = trimesh.creation.cylinder(radius=1, height=2)
LAYOUT = blueprints.load('layout')


def shape(path):
    return cq.importers.importStep(path)


class Machine(AssemblyNode):
    pass
