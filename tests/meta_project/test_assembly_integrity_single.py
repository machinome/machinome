# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

from machinome.test import TestCase

from .assembly_integrity_single import AssemblyIntegritySingle


class AssemblyIntegritySingleTest(TestCase):
    node = AssemblyIntegritySingle

    def test_assembly_integrity(self):
        self.assertNoSolidInterference(self.node)
