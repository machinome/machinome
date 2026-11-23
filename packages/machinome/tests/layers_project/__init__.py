# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A model whose parts declare layers (OpenSpec change
`declare-a-parts-layers`).

The originating project is `projects/enigma-i`: its maker is to tag the
electrical path and the parts that move the rotors, and its page is to show
one layer at a time. Nothing here is the Enigma: `machine.py:Layered` is a
small clocked machine with a part on no layer, an assembly on one, a part on
two, a fusion, and an omitted child; the other modules are the cases the
declaration refuses or inherits. `untagged.py` is the same tree with no
declaration, for the byte pin.
"""
