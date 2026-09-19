# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

from machinome.test import TestCase

from .assembly_integrity_triple import AssemblyIntegrityTriple


class AssemblyIntegrityTripleTest(TestCase):
    node = AssemblyIntegrityTriple

    def test_assembly_integrity(self):
        self.assertNoSolidInterference(self.node)
