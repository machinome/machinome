# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

__version__ = "0.7.1"


def _namespace_portions(path, name):
    """`path` extended by every portion of package `name` found on
    `sys.path` that ships no `__init__.py` of its own.

    A distribution cut from the core later installs its modules under
    `machinome` or `machinome.node` without either package's `__init__.py`,
    so `pkgutil.extend_path` finds it and its modules resolve. The filter is
    the correction: a directory holding its own `__init__.py` is another
    copy of the core -- in a development workspace the editable primary
    checkout sits on `sys.path` behind every bench -- and admitting it would
    resolve a module the bench lacks to the other checkout's file. Nothing
    uses the extension yet; no such distribution exists (OpenSpec change
    `lean-install`).
    """
    import os
    import pkgutil

    found = pkgutil.extend_path(list(path), name)
    return [*path, *(portion for portion in found[len(path):]
                     if not os.path.isfile(os.path.join(portion,
                                                        '__init__.py')))]


__path__ = _namespace_portions(__path__, __name__)
