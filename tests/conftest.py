# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

# The fixture projects contain test_*.py files written for the solid
# runner, some of them deliberately failing. They must only ever run
# inside the subprocess tests/test_meta.py spawns — never be collected
# by pytest itself. The vet fixture projects (tests/vet_projects/) are
# read by `machinome vet` as bytes and never imported or run at all.
collect_ignore = ['meta_project', 'vet_projects']
