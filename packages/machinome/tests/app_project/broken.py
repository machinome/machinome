# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A model whose declared app does not build."""

from tests.clocked_project.calculator import Calculator


class Broken(Calculator):
    """Names `app/broken.tsx`, an element never closed."""

    app = 'app/broken.tsx'
