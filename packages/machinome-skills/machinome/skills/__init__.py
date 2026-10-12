# Machinome Skills - The machinome skills for assistants that read Agent Skills
# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The machinome skills for assistants that read Agent Skills.

The package ships two skills as data under `agent-skills/`: `machinome`, for
building and verifying parts and assemblies, and `machinome-simulate`, for
adding a simulation layer to an existing design. Its command, `machinome
skills`, contributed through the entry-point group `machinome.commands`,
copies them where each assistant reads its skills: `install`, `update` and
`list`, over the registry of tools `tools.toml` (`machinome.skills.cli`,
`machinome.skills.installer`). The framework's `skills` extra installs the
package; the framework never imports it. Its specification is the
framework's capability `skills-distribution` (change `join-skills`).
"""
