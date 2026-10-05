# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Conditional availability contract for the OpenSCAD executable.

The family's leaves render their STL with it, `Solid2Node.as_number`
evaluates a SolidPython value with it, and the OpenSCAD snapshot renderer
draws with it. Each confirms it here first, when its path is attempted, and
is refused with `OpenScadUnavailable` naming what needed it.
"""

import shutil
from functools import lru_cache


class OpenScadUnavailable(RuntimeError):
    """A requested operation cannot run without the OpenSCAD binary.

    `needed_by` and `reason` say what asked and why, and `alternative`, when
    given, another way to the same result."""

    def __init__(self, needed_by, reason, alternative=None):
        self.needed_by = needed_by
        self.reason = reason
        self.alternative = alternative
        super().__init__(self.describe())

    def describe(self):
        remedy = "install OpenSCAD and ensure 'openscad' is on PATH"
        if self.alternative:
            remedy = f'{remedy}, or {self.alternative}'
        return (f'{self.needed_by} requires the OpenSCAD binary because '
                f'{self.reason}; {remedy}')


@lru_cache(maxsize=1)
def openscad_binary():
    """Resolve OpenSCAD once for this process, only when a path needs it."""
    return shutil.which('openscad')


def require_openscad(needed_by, reason, alternative=None):
    """Return the executable path or raise one actionable dependency error."""
    binary = openscad_binary()
    if binary is None:
        raise OpenScadUnavailable(needed_by, reason, alternative)
    return binary
