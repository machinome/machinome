# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

from machinome.test import TestCase

from .assembly_supported_exact import AssemblySupportedExact


class AssemblySupportedExactTest(TestCase):
    node = AssemblySupportedExact

    def test_exact_assembly_is_supported(self):
        self.assertAssemblySupported(self.node)
