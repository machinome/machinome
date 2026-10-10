# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Dissolved: each leaf type is one module directly under `machinome.node`.

`machinome.node.adapters.<x>` is `machinome.node.<x>` (OpenSpec change
`lean-install`): the one-path rule puts a node type at
`machinome.node.<nodetype>`, the address its package keeps when the node
packages are cut. `build123d_sheet` is part of `machinome.node.build123d`,
beside `Build123dNode`, because both drive the one kernel.

This package holds no leaf and re-exports nothing. It exists only so that
every spelling beneath it -- `from machinome.node.adapters.step import
StepAssembly`, `from machinome.node.adapters import step`, `import
machinome.node.adapters.cadquery` -- fails at its import line naming where
the module went, which Python's own "No module named" would not say. The
root of `machinome.node` exports no class either (OpenSpec change
`root-cleanup`): each is imported from its node type's module, as
`from machinome.node.step import StepNode`.
"""

raise ImportError(
    "module 'machinome.node.adapters' was dissolved: each leaf type is now "
    "one module under 'machinome.node', so 'machinome.node.adapters.<x>' is "
    "'machinome.node.<x>' ('build123d_sheet' is part of "
    "'machinome.node.build123d'). Write, for example, "
    "`from machinome.node.step import StepAssembly`.")
