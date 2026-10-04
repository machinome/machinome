# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The mesh engine seam: the contract the core speaks, and its resolution.

The mesh engine decides faceted geometry: it builds a solid from a
triangle mesh and judges it, places, intersects and unites solids,
measures them and meshes them back. That is the engine's work, not the
core's. The core holds the order of culling and comparison, the caches
over solids keyed on files, observations and snapshots, the decoding of
STLs with trimesh, the statics program and the faceted fusion's
publication; every operation on a solid it asks of the engine, through
the operations this module names. To the core a mesh solid is an opaque
handle.

The engine is a conditional dependency, of the shape
`machinome.exact_engine` gives the exact engine: resolved on first use by
the paths that need it, once per process, and refused with one actionable
error naming the install when it is absent. The paths that require it are
exactly: a stale faceted `FusionNode` unioning its children's meshes; a
comparison of two nodes that are not both exact on the exact kernel, or of
any two nodes on the faceted kernel (the faceted fast path and the `.mesh`
fallback); `assertJoined`'s union of such a pair; `assertAssemblySupported`
over two or more solids; and `machinome test` on the faceted kernel, at its
start. Exact geometry never needs it: a model whose every compared part is
exact is decided by the boundary-representation kernel.

Its provider is one known module, `PROVIDER`, named here and nowhere else
in the core. The provider declares the contract version it implements; the
seam compares it with `CONTRACT` and refuses a mismatch naming both.

`manifold3d` publishes no WebAssembly wheel, so on that surface the
engine is not merely unwanted but unavailable.
"""

from functools import lru_cache
import importlib
from typing import Any, Protocol

from machinome.extras import ExtraUnavailable

#: The mesh engine contract version this core speaks. A provider declares
#: the version it implements as its own `CONTRACT`; they must be equal.
CONTRACT = 1

#: The one module that provides the mesh engine.
PROVIDER = 'machinome.manifold.engine'

#: The engine's solid: whatever type the engine passes a mesh solid
#: around as. The core never inspects it.
MeshSolid = Any


class MeshSolids(Protocol):
    """Building solids and reading them back: what the faceted caches,
    fusion, statics, `assertJoined` and the `.mesh` fallback ask of the
    engine."""

    def solid_from_mesh(self, vertices: Any, faces: Any) -> MeshSolid:
        """A solid from a triangle mesh's vertex positions and triangle
        indices."""

    def fault(self, solid: MeshSolid) -> Any:
        """`None` when the engine admits the solid it built, else the
        engine's own name for the fault."""

    def mesh_arrays(self, solid: MeshSolid) -> tuple:
        """The solid's triangle mesh, `(vertices, faces)`."""

    def centred_box(self, size: Any) -> MeshSolid:
        """A box of the three given extents, centred on the origin."""


class MeshComposition(Protocol):
    """Placing and uniting: what placement, fusion and `assertJoined` ask
    of the engine."""

    def placed_solid(self, solid: MeshSolid, matrix: Any) -> MeshSolid:
        """The solid placed by the upper three rows of the framework's
        composed 4x4 matrix, sent as their exact values."""

    def unite_solids(self, solids: list) -> MeshSolid:
        """The union of the solids, folded left in the order given; one
        solid is returned unchanged."""


class MeshComparison(Protocol):
    """Comparing and measuring: what the faceted verdicts and the statics'
    contacts ask of the engine."""

    def intersect_solids(self, first: MeshSolid,
                         second: MeshSolid) -> MeshSolid:
        """The intersection of two solids."""

    def is_empty(self, solid: MeshSolid) -> bool:
        """Whether the solid holds no geometry, as the engine reports it;
        a zero volume is never folded into emptiness."""

    def volume(self, solid: MeshSolid) -> float:
        """The solid's volume."""


class MeshIdentity(Protocol):
    """Who the engine is: what the verdict store and fusion's messages ask
    of it."""

    def identity(self) -> tuple:
        """`(name, version)`, the version `None` when it cannot be read."""


class MeshEngine(MeshSolids, MeshComposition, MeshComparison, MeshIdentity,
                 Protocol):
    """Every operation the core calls on the mesh engine."""


class MeshEngineUnavailable(RuntimeError):
    """A requested operation cannot run without the mesh engine."""

    def __init__(self, needed_by, reason):
        super().__init__(
            f'{needed_by} requires the mesh engine because {reason}; '
            f'install it with \'pip install "machinome[manifold]"\'. Exact '
            f'geometry does not need it: a model whose every compared part '
            f'is exact is decided by the boundary-representation kernel')


class MeshEngineIncompatible(RuntimeError):
    """The provider found does not implement the contract the core speaks."""

    def __init__(self, declared):
        stated = ('declares none' if declared is None
                  else f'declares contract version {declared!r}')
        super().__init__(
            f'The mesh engine {PROVIDER} {stated}, but this machinome '
            f'speaks mesh engine contract version {CONTRACT}; install the '
            f'engine released with this machinome')


def _absent(error):
    """Whether an import error means the engine is not installed, rather
    than installed and failing to import.

    Two shapes are absence: the provider module itself cannot be found, or
    it is found and refuses because the kernel its `manifold` extra
    installs cannot be found (`machinome.extras.ExtraUnavailable` naming
    that extra). A kernel that is found and fails to load is neither.
    """
    if isinstance(error, ExtraUnavailable):
        return error.extra == 'manifold'
    return (isinstance(error, ModuleNotFoundError)
            and error.name in ('machinome.manifold', PROVIDER))


@lru_cache(maxsize=1)
def mesh_engine():
    """Resolve the mesh engine once for this process, only when a path
    needs it. Returns the provider module, or ``None`` when it is not
    installed: when the provider cannot be found, or refuses because its
    `manifold` extra's kernel cannot be.

    A provider that is found but fails to import for another reason -- its
    own kernel found and failing to load -- raises that error here rather
    than being reported absent. A provider declaring another contract
    version, or none, raises `MeshEngineIncompatible`; an exception is not
    cached, so it is raised at every ask.
    """
    try:
        engine = importlib.import_module(PROVIDER)
    except ModuleNotFoundError as error:
        if _absent(error):
            return None
        raise
    declared = getattr(engine, 'CONTRACT', None)
    if declared != CONTRACT:
        raise MeshEngineIncompatible(declared)
    return engine


def require_mesh_engine(needed_by, reason):
    """Return the mesh engine or raise one actionable error."""
    engine = mesh_engine()
    if engine is None:
        raise MeshEngineUnavailable(needed_by, reason)
    return engine
