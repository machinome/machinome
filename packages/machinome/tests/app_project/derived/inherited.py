# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A subclass in another directory that declares nothing: its app is its
base's, relative to the file that declared it, `../calculator_app.py`."""

from tests.app_project.calculator_app import CalculatorApp


class InheritedApp(CalculatorApp):
    """`CalculatorApp` under another name and in another directory."""
