# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

from machinome.test import TestCase

from .assembly_integrity_contained import AssemblyIntegrityContained


class AssemblyIntegrityContainedTest(TestCase):
    node = AssemblyIntegrityContained

    def test_assembly_integrity(self):
        self.assertNoSolidInterference(self.node)
