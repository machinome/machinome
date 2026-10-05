# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The mesh engine, on manifold3d: every operation the core performs on a
mesh solid.

The provider of the core's mesh engine contract, whose seam is
`machinome.engine.mesh_engine`: the mesh engine's role, a module of the
engine package.
Each operation is defined here once, under the name the contract uses, and
is the manifold3d call the framework made inline before the engine was a
provider: the same conversions, on the same arrays, in the same order, so
every verdict, every refusal and every fused mesh is what it was.

The solid is manifold3d's own `Manifold`. The engine adds no type around
it; the core passes it between its caches, placement records and
comparisons as an opaque handle and never inspects it.

Everything here is manifold3d and numpy: the engine imports no trimesh, no
OCCT binding and no CAD front end, and from the framework only the extras
module, for the refusal it raises before importing manifold3d when the
`mesh` extra is not installed. It reads no file, writes none and keeps
no state; caching is its caller's choice.
"""

from machinome.extras import require_extra

# manifold3d is the `mesh` extra's: refused here, before it is imported,
# by the line that installs it. The seam (`machinome.engine.mesh_engine`)
# reads this refusal as an absent engine.
require_extra('mesh', 'the mesh engine (machinome.engine.mesh)',
              'manifold3d')

import numpy as np
from manifold3d import Manifold, Mesh

#: The mesh engine contract version this engine implements.
CONTRACT = 1


########################################
# Solids


def solid_from_mesh(vertices, faces):
    """A solid from a triangle mesh: its vertex positions taken as 32-bit
    floats and its triangle indices as unsigned 32-bit integers."""
    return Manifold(mesh=Mesh(
        vert_properties=np.asarray(vertices, np.float32),
        tri_verts=np.asarray(faces, np.uint32),
    ))


def fault(solid):
    """`None` when manifold3d admits the solid it built, else manifold3d's
    own name for the fault, such as `NotManifold`."""
    status = solid.status()
    if status.name == 'NoError':
        return None
    return status.name


def mesh_arrays(solid):
    """The solid's triangle mesh as `(vertices, faces)`: the vertex
    positions and the triangle indices manifold3d returns, unconverted."""
    mesh = solid.to_mesh()
    return mesh.vert_properties[:, :3], mesh.tri_verts


def centred_box(size):
    """A box of the three given extents, centred on the origin."""
    return Manifold.cube(list(size), True)


########################################
# Composition


def placed_solid(solid, matrix):
    """The solid placed by the upper three rows of the framework's composed
    4x4 `matrix`, sent as their exact values. Nothing is re-meshed or
    re-judged."""
    return solid.transform(matrix[:3, :4])


def unite_solids(solids):
    """The union of the solids, folded left in the order given, one pair
    at a time; a single solid is returned unchanged."""
    result = solids[0]
    for solid in solids[1:]:
        result = result + solid
    return result


########################################
# Comparison


def intersect_solids(first, second):
    """The intersection of two solids."""
    return first ^ second


def is_empty(solid):
    """manifold3d's own emptiness of the solid. A flush contact is a
    non-empty solid of zero volume, and stays one."""
    return solid.is_empty()


def volume(solid):
    """manifold3d's own volume of the solid."""
    return solid.volume()


########################################
# Identity


def identity():
    """`(name, version)`: `manifold3d` and the installed distribution's
    version, read from its metadata, or `None` for the version when the
    metadata cannot be read."""
    from importlib import metadata

    try:
        version = metadata.version('manifold3d')
    except metadata.PackageNotFoundError:
        version = None
    return ('manifold3d', version)
