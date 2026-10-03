# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The exact engine seam: the contract the core speaks, and its resolution.

Exact geometry -- reading, placing, fusing, comparing, measuring and
writing boundary representations -- is the exact engine's work, not the
core's. The core holds the exact leaf and fusion nodes, the test
framework's culling order, the memos over shape handles and artifact files
(`machinome.exact_cache`) and artifact publication
(`machinome.exact_artifacts`); every operation on a shape it asks of the
engine, through the operations this module names. To the core an exact
shape is an opaque handle: the engine's currency, which the core passes
between nodes, caches and comparisons without inspecting it.

The engine is a conditional dependency, of the shape `machinome.mesh_engine`
gives the mesh engine: resolved on first use by the paths that need it,
once per process, and refused with one actionable error naming the install
when it is absent. Its provider is one known module, named here and nowhere
else in the core. The provider declares the contract version it
implements; the seam compares it with `CONTRACT` and refuses a mismatch
naming both.
"""

from functools import lru_cache
import importlib
from typing import Any, Protocol

#: The exact engine contract version this core speaks. A provider declares
#: the version it implements as its own `CONTRACT`; they must be equal.
CONTRACT = 1

#: The one module that provides the exact engine.
PROVIDER = 'machinome.occt.engine'

#: The engine's currency: whatever type the engine passes exact geometry
#: around as. The core never inspects it.
ExactShape = Any


class ExactCurrency(Protocol):
    """Currency I/O: what exact leaves, fusion, the memos and artifact
    publication ask of the engine."""

    def as_shape(self, obj: Any) -> ExactShape:
        """`obj` as the currency, rewrapped, never translated; `TypeError`
        naming its type when the engine does not admit it."""

    def compound(self, shapes: list) -> ExactShape:
        """One compound holding every shape given, in order."""

    def read_brep(self, path: str) -> ExactShape:
        """The shape a BREP file holds; `ValueError` naming the path when
        it holds none."""

    def write_brep(self, shape: ExactShape, path: str) -> None:
        """Write the shape's BREP to `path`."""

    def write_stl(self, shape: ExactShape, path: str,
                  linear_deflection: float,
                  angular_deflection: float) -> None:
        """Tessellate the shape at those deflections and write a binary
        STL to `path`, and nothing else."""


class ExactComposition(Protocol):
    """Composition: what fusion, the placement memo and `assertJoined` ask
    of the engine."""

    def placed_shape(self, shape: ExactShape, matrix: Any) -> ExactShape:
        """A new shape placed by the upper three rows of the framework's
        composed 4x4 matrix, sent as their exact values."""

    def fuse_shapes(self, first: ExactShape, second: ExactShape,
                    first_name: str, second_name: str) -> ExactShape:
        """The native fuse of private copies of two placed shapes;
        `RuntimeError` naming both when the kernel fails."""


class ExactComparison(Protocol):
    """Comparison and measurement: what the test framework and the memos
    ask of the engine."""

    def intersect_shapes(self, first: ExactShape, second: ExactShape,
                         first_name: str, second_name: str) -> ExactShape:
        """The native common of private copies of two placed shapes, an
        empty result verified before it is returned
        (`ExactCommonInconsistency`, `ExactCommonVerificationError`)."""

    def solid_count(self, shape: ExactShape) -> int:
        """The number of solids."""

    def solid_volume(self, shape: ExactShape) -> float:
        """The sum of the solids' volumes."""

    def bounds(self, shape: ExactShape) -> tuple:
        """The optimal axis-aligned box, `((xmin, ymin, zmin),
        (xmax, ymax, zmax))`."""

    def face_bounds(self, shape: ExactShape) -> Any:
        """One axis-aligned box per face, an `(F, 2, 3)` float64 array,
        taken from the exact surfaces and never from a triangulation."""

    def mutually_outside(self, first: ExactShape,
                         second: ExactShape) -> bool:
        """`True` only when one vertex of every solid of each placed shape
        classifies strictly outside every solid of the other; `False`,
        declining, otherwise."""


class ExactEngine(ExactCurrency, ExactComposition, ExactComparison,
                  Protocol):
    """Every operation the core calls on the exact engine."""


class ExactEngineUnavailable(RuntimeError):
    """A requested operation cannot run without the exact engine."""

    def __init__(self, needed_by, reason):
        super().__init__(
            f'{needed_by} requires the exact engine because {reason}; '
            f'install it with \'pip install "machinome[occt]"\'. A model '
            f'with no exact node never needs it')


class ExactEngineIncompatible(RuntimeError):
    """The provider found does not implement the contract the core speaks."""

    def __init__(self, declared):
        stated = ('declares none' if declared is None
                  else f'declares contract version {declared!r}')
        super().__init__(
            f'The exact engine {PROVIDER} {stated}, but this machinome '
            f'speaks exact engine contract version {CONTRACT}; install the '
            f'engine released with this machinome')


class ExactCommonInconsistency(RuntimeError):
    """An empty OCCT common contradicts a strict shared-interior point."""


class ExactCommonVerificationError(RuntimeError):
    """An empty OCCT common could not be independently checked."""


def _absent(error):
    """Whether an import error means the provider is not installed, rather
    than installed and failing to import."""
    return (isinstance(error, ModuleNotFoundError)
            and error.name in ('machinome.occt', PROVIDER))


@lru_cache(maxsize=1)
def exact_engine():
    """Resolve the exact engine once for this process, only when a path
    needs it. Returns the provider module, or ``None`` when it is not
    installed.

    A provider that is found but fails to import for another reason -- its
    own kernel failing to load -- raises that error here rather than being
    reported absent. A provider declaring another contract version, or
    none, raises `ExactEngineIncompatible`; an exception is not cached, so
    it is raised at every ask.
    """
    try:
        engine = importlib.import_module(PROVIDER)
    except ModuleNotFoundError as error:
        if _absent(error):
            return None
        raise
    declared = getattr(engine, 'CONTRACT', None)
    if declared != CONTRACT:
        raise ExactEngineIncompatible(declared)
    return engine


def require_exact_engine(needed_by, reason):
    """Return the exact engine or raise one actionable error."""
    engine = exact_engine()
    if engine is None:
        raise ExactEngineUnavailable(needed_by, reason)
    return engine
