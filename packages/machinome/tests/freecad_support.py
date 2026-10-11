# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""What the FreeCAD node package's tests share: the one guard that skips
them where no FreeCAD runtime is configured (OpenSpec change
`join-freecad`, capability `native-freecad-assembly`)."""

import os

import pytest

#: The variable naming the extracted FreeCAD 1.1.4 runtime.
RUNTIME = 'MACHINOME_FREECAD_ROOT'


def skip_without_runtime():
    """Skip the calling test module, at its import, when `RUNTIME` is not
    set."""
    if not os.environ.get(RUNTIME):
        pytest.skip(f'{RUNTIME} is not set: the FreeCAD node package\'s '
                    'tests need an extracted FreeCAD 1.1.4 runtime',
                    allow_module_level=True)
