# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The clocked calculator, declaring its own app beside this file."""

from tests.clocked_project.calculator import Calculator


class CalculatorApp(Calculator):
    """`Calculator`, operated through `app/index.tsx`."""

    app = 'app/index.tsx'
