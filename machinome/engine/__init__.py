# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The engine package: the contracts the core speaks to its two engines,
and their resolution.

Two engines do the core's geometry, each named for the representation it
consumes: the B-rep engine, over a boundary representation of parametric
surfaces, and the mesh engine, over a polyhedral triangle mesh. Each is a
conditional dependency, resolved on first use by the paths that need it,
once per process, and refused with one actionable error naming the install
when it is absent. Each provider is one known module of this package,
`BREP_PROVIDER` and `MESH_PROVIDER`, named here and nowhere else in the
core; it declares the contract version it implements, and its seam
compares it with `BREP_CONTRACT` or `MESH_CONTRACT` and refuses a mismatch
naming both.

The B-rep engine reads, places, fuses, compares, measures and writes
boundary representations. The core holds the B-rep leaf and fusion nodes,
the test framework's culling order, the memos over shape handles and
artifact files (`machinome.brep_cache`) and artifact publication
(`machinome.brep_artifacts`); every operation on a shape it asks of the
engine. To the core a B-rep shape is an opaque handle: the engine's
currency, which the core passes between nodes, caches and comparisons
without inspecting it.

The mesh engine decides mesh geometry: it builds a solid from a triangle
mesh and judges it, places, intersects and unites solids, measures them
and meshes them back. The core holds the order of culling and comparison,
the caches over solids keyed on files, observations and snapshots, the
decoding of STLs with trimesh, the statics program and the mesh fusion's
publication; every operation on a solid it asks of the engine. To the core
a mesh solid is an opaque handle. The paths that require it are: a stale
mesh `FusionNode` unioning its children's meshes; a comparison of two
nodes that do not both have B-rep geometry on the B-rep engine, or of any
two nodes on the mesh engine (the mesh fast path and the `.mesh`
fallback); `assertJoined`'s union of such a pair;
`assertAssemblySupported` over two or more solids; and `machinome test` on
the mesh engine, at its start. B-rep geometry never needs it: a model whose
every compared part has B-rep geometry is decided by the B-rep engine.
The mesh engine's library publishes no WebAssembly wheel, so on that
surface the mesh engine is not merely unwanted but unavailable.

The seams are not named like their providers: resolving
`machinome.engine.brep` binds the provider module as this package's
attribute `brep`, which would replace a seam function of that name at its
first use. This package imports neither provider and exports no
operation; a project calling a B-rep operation directly imports
`machinome.engine.brep`. A distribution cut from the core installs a
provider module here without this `__init__.py`, and the package's path
admits it (see `machinome._namespace_portions`).
"""

from functools import lru_cache
import importlib
from typing import Any, Protocol

from machinome import _namespace_portions
from machinome.extras import ExtraUnavailable


########################################
# The B-rep engine

#: The B-rep engine contract version this core speaks. A provider declares
#: the version it implements as its own `CONTRACT`; they must be equal.
BREP_CONTRACT = 2

#: The one module that provides the B-rep engine.
BREP_PROVIDER = 'machinome.engine.brep'

#: The engine's currency: whatever type the engine passes B-rep geometry
#: around as. The core never inspects it.
BrepShape = Any


class BrepCurrency(Protocol):
    """Currency I/O: what B-rep leaves, fusion, the memos and artifact
    publication ask of the engine."""

    def as_shape(self, obj: Any) -> BrepShape:
        """`obj` as the currency, rewrapped, never translated; `TypeError`
        naming its type when the engine does not admit it."""

    def compound(self, shapes: list) -> BrepShape:
        """One compound holding every shape given, in order."""

    def read_brep(self, path: str) -> BrepShape:
        """The shape a BREP file holds; `ValueError` naming the path when
        it holds none."""

    def write_brep(self, shape: BrepShape, path: str) -> None:
        """Write the shape's BREP to `path`."""

    def write_stl(self, shape: BrepShape, path: str,
                  linear_deflection: float,
                  angular_deflection: float) -> None:
        """Tessellate the shape at those deflections and write a binary
        STL to `path`, and nothing else."""


class BrepComposition(Protocol):
    """Composition: what fusion, the placement memo and `assertJoined` ask
    of the engine."""

    def placed_shape(self, shape: BrepShape, matrix: Any) -> BrepShape:
        """A new shape placed by the upper three rows of the framework's
        composed 4x4 matrix, sent as their IEEE-754 values unchanged."""

    def fuse_shapes(self, first: BrepShape, second: BrepShape,
                    first_name: str, second_name: str) -> BrepShape:
        """The native fuse of private copies of two placed shapes;
        `RuntimeError` naming both when the kernel fails."""


class BrepComparison(Protocol):
    """Comparison and measurement: what the test framework and the memos
    ask of the engine."""

    def intersect_shapes(self, first: BrepShape, second: BrepShape,
                         first_name: str, second_name: str) -> BrepShape:
        """The native common of private copies of two placed shapes, an
        empty result verified before it is returned
        (`BrepCommonInconsistency`, `BrepCommonVerificationError`)."""

    def solid_count(self, shape: BrepShape) -> int:
        """The number of solids."""

    def solid_volume(self, shape: BrepShape) -> float:
        """The sum of the solids' volumes."""

    def bounds(self, shape: BrepShape) -> tuple:
        """The optimal axis-aligned box, `((xmin, ymin, zmin),
        (xmax, ymax, zmax))`."""

    def face_bounds(self, shape: BrepShape) -> Any:
        """One axis-aligned box per face, an `(F, 2, 3)` float64 array,
        taken from the parametric surfaces and never from a
        triangulation."""

    def mutually_outside(self, first: BrepShape,
                         second: BrepShape) -> bool:
        """`True` only when one vertex of every solid of each placed shape
        classifies strictly outside every solid of the other; `False`,
        declining, otherwise."""


class BrepEngine(BrepCurrency, BrepComposition, BrepComparison, Protocol):
    """Every operation the core calls on the B-rep engine."""


class BrepEngineUnavailable(RuntimeError):
    """A requested operation cannot run without the B-rep engine."""

    def __init__(self, needed_by, reason):
        super().__init__(
            f'{needed_by} requires the B-rep engine because {reason}; '
            f'install it with \'pip install "machinome[brep]"\'. A model '
            f'with no B-rep node never needs it')


class BrepEngineIncompatible(RuntimeError):
    """The provider found does not implement the contract the core speaks."""

    def __init__(self, declared):
        stated = ('declares none' if declared is None
                  else f'declares contract version {declared!r}')
        super().__init__(
            f'The B-rep engine {BREP_PROVIDER} {stated}, but this machinome '
            f'speaks B-rep engine contract version {BREP_CONTRACT}; install '
            f'the engine released with this machinome')


class BrepCommonInconsistency(RuntimeError):
    """An empty B-rep common contradicts a strict shared-interior point."""


class BrepCommonVerificationError(RuntimeError):
    """An empty B-rep common could not be independently checked."""


def _brep_absent(error):
    """Whether an import error means the B-rep engine is not installed,
    rather than installed and failing to import.

    Two shapes are absence: the provider module itself cannot be found, or
    it is found and refuses because the kernel its `brep` extra installs
    cannot be found (`machinome.extras.ExtraUnavailable` naming that
    extra). A kernel that is found and fails to load is neither.
    """
    if isinstance(error, ExtraUnavailable):
        return error.extra == 'brep'
    return (isinstance(error, ModuleNotFoundError)
            and error.name == BREP_PROVIDER)


@lru_cache(maxsize=1)
def brep_engine():
    """Resolve the B-rep engine once for this process, only when a path
    needs it. Returns the provider module, or ``None`` when it is not
    installed: when the provider cannot be found, or refuses because its
    `brep` extra's kernel cannot be.

    A provider that is found but fails to import for another reason -- its
    own kernel found and failing to load -- raises that error here rather
    than being reported absent. A provider declaring another contract
    version, or none, raises `BrepEngineIncompatible`; an exception is not
    cached, so it is raised at every ask.
    """
    try:
        engine = importlib.import_module(BREP_PROVIDER)
    except ModuleNotFoundError as error:
        if _brep_absent(error):
            return None
        raise
    declared = getattr(engine, 'CONTRACT', None)
    if declared != BREP_CONTRACT:
        raise BrepEngineIncompatible(declared)
    return engine


def require_brep_engine(needed_by, reason):
    """Return the B-rep engine or raise one actionable error."""
    engine = brep_engine()
    if engine is None:
        raise BrepEngineUnavailable(needed_by, reason)
    return engine


########################################
# The mesh engine

#: The mesh engine contract version this core speaks. A provider declares
#: the version it implements as its own `CONTRACT`; they must be equal.
MESH_CONTRACT = 1

#: The one module that provides the mesh engine.
MESH_PROVIDER = 'machinome.engine.mesh'

#: The engine's solid: whatever type the engine passes a mesh solid
#: around as. The core never inspects it.
MeshSolid = Any


class MeshSolids(Protocol):
    """Building solids and reading them back: what the mesh caches,
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
        composed 4x4 matrix, sent as their IEEE-754 values unchanged."""

    def unite_solids(self, solids: list) -> MeshSolid:
        """The union of the solids, folded left in the order given; one
        solid is returned unchanged."""


class MeshComparison(Protocol):
    """Comparing and measuring: what the mesh verdicts and the statics'
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
            f'install it with \'pip install "machinome[mesh]"\'. B-rep '
            f'geometry does not need it: a model whose every compared part '
            f'has B-rep geometry is decided by the B-rep engine')


class MeshEngineIncompatible(RuntimeError):
    """The provider found does not implement the contract the core speaks."""

    def __init__(self, declared):
        stated = ('declares none' if declared is None
                  else f'declares contract version {declared!r}')
        super().__init__(
            f'The mesh engine {MESH_PROVIDER} {stated}, but this machinome '
            f'speaks mesh engine contract version {MESH_CONTRACT}; install '
            f'the engine released with this machinome')


def _mesh_absent(error):
    """Whether an import error means the mesh engine is not installed,
    rather than installed and failing to import.

    Two shapes are absence: the provider module itself cannot be found, or
    it is found and refuses because the kernel its `mesh` extra installs
    cannot be found (`machinome.extras.ExtraUnavailable` naming that
    extra). A kernel that is found and fails to load is neither.
    """
    if isinstance(error, ExtraUnavailable):
        return error.extra == 'mesh'
    return (isinstance(error, ModuleNotFoundError)
            and error.name == MESH_PROVIDER)


@lru_cache(maxsize=1)
def mesh_engine():
    """Resolve the mesh engine once for this process, only when a path
    needs it. Returns the provider module, or ``None`` when it is not
    installed: when the provider cannot be found, or refuses because its
    `mesh` extra's kernel cannot be.

    A provider that is found but fails to import for another reason -- its
    own kernel found and failing to load -- raises that error here rather
    than being reported absent. A provider declaring another contract
    version, or none, raises `MeshEngineIncompatible`; an exception is not
    cached, so it is raised at every ask.
    """
    try:
        engine = importlib.import_module(MESH_PROVIDER)
    except ModuleNotFoundError as error:
        if _mesh_absent(error):
            return None
        raise
    declared = getattr(engine, 'CONTRACT', None)
    if declared != MESH_CONTRACT:
        raise MeshEngineIncompatible(declared)
    return engine


def require_mesh_engine(needed_by, reason):
    """Return the mesh engine or raise one actionable error."""
    engine = mesh_engine()
    if engine is None:
        raise MeshEngineUnavailable(needed_by, reason)
    return engine


# A provider cut from the core installs its module here without this
# package's `__init__.py`; it is found as a portion of this package's path,
# and a second copy of the core never is (see `_namespace_portions`).
__path__ = _namespace_portions(__path__, __name__)
