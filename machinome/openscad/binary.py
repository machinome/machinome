# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Conditional availability contract for the OpenSCAD executable."""

import shutil
from functools import lru_cache

from machinome.scad_engine import ScadEngineUnavailable


class OpenScadUnavailable(ScadEngineUnavailable):
    """A requested operation cannot run without the OpenSCAD binary.

    One of the seam's `ScadEngineUnavailable`, so the core catches it
    through the seam without naming this package; its message is the
    binary's own."""

    def __init__(self, needed_by, reason, alternative=None):
        super().__init__(needed_by, reason, None, alternative)

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
