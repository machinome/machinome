# machinome-viewer - the browser viewer for Machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""Executable contract for the viewer's identity in the repository.

The distribution `machinome-viewer`, the package `machinome.viewer.web` at
its directory, with no `__init__.py` at the levels above it, a requirement on
the framework of its own release, and the repository's address (change
`join-viewer`). The framework finds the package at its address through its
seam of viewers, whose web provider it is: the package declares the seam's
contract version and the operations it offers, and no entry point (change
`viewer-seam`). It declares no command of its own: its verbs are the
framework's `machinome viewer` (change `viewer-command`).
"""

from pathlib import Path
import tomllib
from unittest import TestCase

from packaging.requirements import Requirement


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'machinome' / 'viewer' / 'web'


class MachinomeViewerIdentityTest(TestCase):
    def setUp(self):
        self.metadata = tomllib.loads((ROOT / 'pyproject.toml').read_text())

    def test_python_distribution_command_and_lookup_are_machinome(self):
        project = self.metadata['project']
        self.assertEqual(project['name'], 'machinome-viewer')
        self.assertNotIn('scripts', project)
        self.assertNotIn('entry-points', project)
        self.assertEqual(
            self.metadata['tool']['setuptools']['packages']['find'],
            {'include': ['machinome.viewer.web'], 'namespaces': True})

    def test_the_package_sits_at_its_address(self):
        self.assertTrue((PACKAGE / '__init__.py').is_file())
        for level in (ROOT / 'machinome', ROOT / 'machinome' / 'viewer'):
            with self.subTest(level=level.relative_to(ROOT).as_posix()):
                self.assertFalse((level / '__init__.py').exists())
        for former in ('machinome_viewer', 'solid_node_viewer'):
            with self.subTest(former=former):
                self.assertFalse((ROOT / former).exists())

    def test_the_package_is_the_web_provider_of_the_seam(self):
        import machinome.viewer as viewers
        import machinome.viewer.web as web
        self.assertIs(viewers.viewer('web'), web)
        self.assertEqual(web.CONTRACT, viewers.CONTRACT)
        self.assertEqual(web.NAME, 'web')
        self.assertEqual(web.OPERATIONS, frozenset({'present', 'capture',
                                                    'serve', 'embed'}))
        self.assertEqual(web.CAPTURE_OPTIONS,
                         frozenset({'autocenter', 'viewall'}))
        self.assertEqual(web.identity(), ('machinome-viewer', web.__version__))

    def test_an_operation_is_not_replaced_by_its_namesake_module(self):
        import importlib
        import sys
        import types
        import machinome.viewer.web as web
        module = importlib.import_module('machinome.viewer.web.capture')
        self.assertIsInstance(module, types.ModuleType)
        self.assertIs(sys.modules['machinome.viewer.web.capture'], module)
        self.assertTrue(callable(web.capture))
        self.assertNotIsInstance(web.capture, types.ModuleType)

    def test_it_requires_the_framework_of_its_own_release(self):
        project = self.metadata['project']
        (pin,) = [Requirement(line) for line in project['dependencies']
                  if Requirement(line).name == 'machinome']
        self.assertEqual(str(pin.specifier), f"~={project['version']}")

    def test_its_address_is_the_repository_s(self):
        self.assertEqual(self.metadata['project']['urls'],
                         {'Homepage': 'https://github.com/machinome/machinome'})

    def test_bundle_and_browser_global_are_machinome(self):
        build = (PACKAGE / 'widget' / 'build.mjs').read_text()
        self.assertIn('MachinomeViewer', build)
        self.assertIn('machinome-viewer.js', build)
        self.assertNotIn('SolidNodeWidget', build)

    def test_loader_accepts_current_and_legacy_formats(self):
        loader = (PACKAGE / 'widget' / 'src' / 'viewer.ts').read_text()
        self.assertIn('machinome-export', loader)
        self.assertIn('solid-node-export', loader)
