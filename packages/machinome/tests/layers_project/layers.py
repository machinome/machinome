# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The fixture's layers, each defined once and imported where it is declared."""

from machinome.layers import Layer

ELECTRICAL = Layer('electrical', label='Electrical path')
MECHANICAL = Layer('mechanical', label='Rotor stepping')
SPARE = Layer('spare', label='Spare')
