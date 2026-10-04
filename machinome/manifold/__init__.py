# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The manifold mesh engine.

This package exports nothing: its one module, `machinome.manifold.engine`,
is the provider the core's mesh engine seam (`machinome.mesh_engine`)
resolves. It offers no operation a project is meant to call; a project
that wants manifold3d imports it.
"""
