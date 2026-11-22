# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A model whose declared app lies outside the project.

Two directories up from this file is outside the project, wherever the
project lies; the test that builds it creates that file in a temporary
copy of the project, never beside the committed one."""

from tests.clocked_project.calculator import Calculator


class Outside(Calculator):
    """Names a file beside the project's own directory."""

    app = '../../outside-app.tsx'
