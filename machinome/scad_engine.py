# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The OpenSCAD engine seam: the contract the core speaks, and its
resolution.

The OpenSCAD engine (`machinome.openscad`) is where SolidPython is known.
The core asks it, through this module, for one thing: to adopt a value
SolidPython built as the core's expression graph
(`machinome.expression_graph.symbolic`). Adoption is optional by nature --
without the engine no SolidPython value is an expression, and a path that
receives one refuses it as it refuses any other non-expression -- so no
path requires the engine and this seam raises no install refusal.

The seam has the exact engine's shape (`machinome.exact_engine`): one
known provider, named here and nowhere else in the core, resolved once per
process; the provider declares the contract version it implements, and the
seam refuses a mismatch naming both.
"""

from functools import lru_cache
import importlib

#: The OpenSCAD engine contract version this core speaks. A provider
#: declares the version it implements as its own `CONTRACT`; they must be
#: equal.
CONTRACT = 1

#: The one module that provides the OpenSCAD engine.
PROVIDER = 'machinome.openscad.engine'


class ScadEngineIncompatible(RuntimeError):
    """The provider found does not implement the contract the core speaks."""

    def __init__(self, declared):
        stated = ('declares none' if declared is None
                  else f'declares contract version {declared!r}')
        super().__init__(
            f'The OpenSCAD engine {PROVIDER} {stated}, but this machinome '
            f'speaks OpenSCAD engine contract version {CONTRACT}; install '
            f'the engine released with this machinome')


def _absent(error):
    """Whether an import error means the engine is not installed, rather
    than installed and failing to import: the engine's package or the
    provider cannot be found, or the provider is found and SolidPython,
    its kernel, cannot be. With no SolidPython installed no SolidPython
    value can exist, so there is nothing to adopt."""
    return error.name in ('machinome.openscad', PROVIDER, 'solid2')


@lru_cache(maxsize=1)
def scad_engine():
    """Resolve the OpenSCAD engine once for this process, only when a path
    asks. Returns the provider module, or ``None`` when it is not
    installed.

    A provider that is found but fails to import for another reason
    raises that error here rather than being reported absent. A provider
    declaring another contract version, or none, raises
    `ScadEngineIncompatible`; an exception is not cached, so it is raised
    at every ask.
    """
    try:
        engine = importlib.import_module(PROVIDER)
    except ModuleNotFoundError as error:
        if _absent(error):
            return None
        raise
    declared = getattr(engine, 'CONTRACT', None)
    if declared != CONTRACT:
        raise ScadEngineIncompatible(declared)
    return engine
