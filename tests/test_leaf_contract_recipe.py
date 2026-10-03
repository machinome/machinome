# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A source recipe reaches every artifact of its node, and no recipe
changes nothing (OpenSpec change `leaf-contract`, capability
`leaf-contract`, "A leaf states its source identity through declared
members").

Two of `tests/leaf_contract_golden.py`'s fixtures are built here twice:
the `Solid2Node` (`.scad`, `.stl`) and the exact leaf wearing a marking
(`.brep`, `.stl`, `.scad`, `.marking-digits.stl`). With no recipe their
records are the golden's, recorded on the tree before `source_recipe`
existed; declaring one changes the digest and fingerprint of every one of
their artifacts.
"""

import glob
import json
import os
import shutil
import tempfile
from unittest import TestCase
from unittest.mock import patch

from machinome import currency

BASEDIR = os.path.dirname(os.path.abspath(__file__))
GOLDEN = os.path.join(BASEDIR, 'data', 'leaf_contract_golden.json')

RECIPE = 'native-recipe-of-the-test'


def _washer():
    from tests.leaf_contract_project.parts import Washer
    return Washer()


def _dial():
    from tests.markings_project.dial import Dial
    return Dial()


FIXTURES = {'solid2_node': _washer, 'exact_leaf_with_marking': _dial}


class SourceRecipeTest(TestCase):

    def setUp(self):
        with open(GOLDEN) as handle:
            self.golden = json.load(handle)['fixtures']

    def build(self, fixture, recipe):
        """The `{suffix: (digest, fingerprint)}` records of one fixture
        built in a fresh build directory, declaring `recipe`."""
        build_dir = tempfile.mkdtemp(prefix='leaf-contract-recipe-')
        self.addCleanup(shutil.rmtree, build_dir, ignore_errors=True)
        with patch.dict(os.environ, {'SOLID_BUILD_DIR': build_dir}):
            node = FIXTURES[fixture]()
            if recipe is not None:
                node.source_recipe = recipe
            node.assemble()
            node.build_stls()
        records = {}
        for path in glob.glob(f'{glob.escape(node.basepath)}*'):
            if path.endswith(currency.SIDECAR_SUFFIX):
                continue
            records[path[len(node.basepath):]] = (
                currency.recorded_digest(path),
                currency.recorded_fingerprint(path))
        return records

    def test_no_recipe_records_what_the_tree_recorded_before(self):
        for fixture in FIXTURES:
            golden = self.golden[fixture]['artifacts']
            records = self.build(fixture, None)
            with self.subTest(fixture=fixture):
                self.assertEqual(sorted(records), sorted(golden))
            for suffix, (digest, _) in records.items():
                with self.subTest(fixture=fixture, artifact=suffix):
                    self.assertEqual(digest, golden[suffix]['digest'])

    def test_a_recipe_reaches_every_artifact(self):
        for fixture in FIXTURES:
            plain = self.build(fixture, None)
            recipe = self.build(fixture, RECIPE)
            with self.subTest(fixture=fixture):
                self.assertEqual(sorted(recipe), sorted(plain))
            for suffix in plain:
                with self.subTest(fixture=fixture, artifact=suffix):
                    self.assertIsNotNone(recipe[suffix][0])
                    self.assertNotEqual(recipe[suffix][0], plain[suffix][0])
                    self.assertNotEqual(recipe[suffix][1], plain[suffix][1])
