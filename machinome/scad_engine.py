# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The OpenSCAD engine seam: the contract the core speaks, and its
resolution.

The OpenSCAD engine (`machinome.openscad`) is where SolidPython is known.
The core asks it, through this module, for what only it can do (contract
version 2):

- `adopt(value)` (since 1): read a value SolidPython built as the core's
  expression graph (`machinome.expression_graph.symbolic`). Optional by
  nature -- without the engine no SolidPython value is an expression, and a
  path that receives one refuses it as it refuses any other non-expression;
- `scad_text(description, fn=None)`: the SCAD text of a presentation
  description the core composed (`machinome.node.presentation`). The core
  describes its SCAD presentation and never writes SCAD itself;
- `require_binary(needed_by, reason, alternative=None)`: the OpenSCAD
  executable, or the binary contract's refusal.

The paths that need SCAD text require the engine, through
`require_scad_engine`, and are refused with `ScadEngineUnavailable` naming
what needed it, the module that could not be found and its install: a
node's `scad_code` and `generate_scad()`, the materialization of a leaf
whose geometry is authored in SCAD, and the OpenSCAD snapshot renderer.
`assemble()` and an ordinary build require nothing of it.

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
CONTRACT = 2

#: The one module that provides the OpenSCAD engine.
PROVIDER = 'machinome.openscad.engine'

#: What installs each module whose absence is an absent engine, as an
#: install that works today: SolidPython is a requirement of machinome's
#: distribution, which also carries the engine's package. Neither is an
#: extra yet, and naming an install line that installs nothing would be
#: worse than naming none.
_REMEDIES = {
    'solid2': "install SolidPython with 'pip install solidpython2'",
    'machinome.openscad': ('reinstall machinome, whose distribution '
                           'carries the OpenSCAD engine'),
    PROVIDER: ('reinstall machinome, whose distribution carries the '
               'OpenSCAD engine'),
}

#: The module whose absence made the last resolution answer None.
_missing = [None]


class ScadEngineIncompatible(RuntimeError):
    """The provider found does not implement the contract the core speaks."""

    def __init__(self, declared):
        stated = ('declares none' if declared is None
                  else f'declares contract version {declared!r}')
        super().__init__(
            f'The OpenSCAD engine {PROVIDER} {stated}, but this machinome '
            f'speaks OpenSCAD engine contract version {CONTRACT}; install '
            f'the engine released with this machinome')


class ScadEngineUnavailable(RuntimeError):
    """A requested operation cannot run without the OpenSCAD engine.

    `needed_by` and `reason` say what asked and why, `missing` the module
    that could not be found, and `alternative`, when given, another way to
    the same result. The binary's refusal,
    `machinome.openscad.binary.OpenScadUnavailable`, is one of these, so a
    caller catches either through this seam.
    """

    def __init__(self, needed_by, reason, missing=None, alternative=None):
        self.needed_by = needed_by
        self.reason = reason
        self.missing = missing
        self.alternative = alternative
        super().__init__(self.describe())

    def describe(self):
        remedy = _REMEDIES.get(self.missing, _REMEDIES[PROVIDER])
        if self.alternative:
            remedy = f'{remedy}, or {self.alternative}'
        return (f'{self.needed_by} requires the OpenSCAD engine because '
                f'{self.reason}, and the module {self.missing} cannot be '
                f'found; {remedy}')


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
            _missing[0] = error.name
            return None
        raise
    declared = getattr(engine, 'CONTRACT', None)
    if declared != CONTRACT:
        raise ScadEngineIncompatible(declared)
    return engine


def require_scad_engine(needed_by, reason, alternative=None):
    """Return the OpenSCAD engine or raise one actionable error.

    Called where a path that needs SCAD text is attempted, before any file
    is written or any process launched. `needed_by` names what asked -- for
    a node, its name and its own class -- and `alternative`, when given,
    another way to the same result.
    """
    engine = scad_engine()
    if engine is None:
        raise ScadEngineUnavailable(needed_by, reason, _missing[0],
                                    alternative)
    return engine
