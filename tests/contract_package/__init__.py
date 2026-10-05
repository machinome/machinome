# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Leaves written outside the core, against the declared leaf contract.

The stand-ins of the `leaf-contract` change: what a node package written
against `LeafNode` and `BrepLeafNode` looks like when it uses only the
members the `leaf-contract` capability declares. `exact_stand_in` mirrors
machinome-freecad's exact leaf (a bare `TopoDS_Shape` read from BREP
bytes, a native recipe deciding the geometry); `faceted_stand_in` is a
faceted leaf producing its own STL from a committed mesh. The two
projects beside them, with their solid-runner test modules, build and
test the stand-ins the way a project would; `tests/conftest.py` keeps
pytest from collecting those modules, which only ever run under
`machinome test` in a subprocess.
"""
