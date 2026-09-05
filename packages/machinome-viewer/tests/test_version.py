# solid-node-viewer - the browser viewer for solid-node models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only

"""One version, declared in three places that must agree."""

import json
import re
from pathlib import Path
from unittest import TestCase

import solid_node_viewer
from solid_node_viewer.bundle import PACKAGE_JSON

ROOT = Path(__file__).resolve().parent.parent


class VersionAgreementTest(TestCase):

    def test_python_and_widget_declare_the_same_version(self):
        with open(PACKAGE_JSON) as stream:
            widget = json.load(stream)['version']
        self.assertEqual(widget, solid_node_viewer.__version__)

    def test_pyproject_declares_the_package_version(self):
        pyproject = (ROOT / 'pyproject.toml').read_text()
        declared = re.search(r'^version = "([^"]+)"', pyproject, re.MULTILINE).group(1)
        self.assertEqual(declared, solid_node_viewer.__version__)

    def test_the_changelog_opens_with_the_current_version(self):
        changelog = (ROOT / 'CHANGELOG.md').read_text()
        self.assertIn(f'## {solid_node_viewer.__version__}', changelog)
