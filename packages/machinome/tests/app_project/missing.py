# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A model whose declared app does not exist."""

from tests.clocked_project.calculator import Calculator


class Missing(Calculator):
    """Names `app/absent.tsx`, which is not there."""

    app = 'app/absent.tsx'
