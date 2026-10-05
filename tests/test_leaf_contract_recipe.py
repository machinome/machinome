# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A source recipe reaches every artifact of its node, and no recipe
changes nothing (OpenSpec change `leaf-contract`, capability
`leaf-contract`, "A leaf states its source identity through declared
members").

Two of `tests/leaf_contract_golden.py`'s fixtures are built here twice:
the `Solid2Node` (`.scad`, `.stl`) and the exact leaf wearing a marking
(`.brep`, `.stl`, `.scad`, `.marking-digits.stl`). With no recipe they
record the artifacts the golden lists, recorded on the tree before
`source_recipe` existed, each with its node's plain source digest, the
digest of its tracked sources with nothing folded in; declaring one changes
the digest and fingerprint of every one of their artifacts.

The plain digest is computed in the same run rather than read from the
golden: the golden's digests are of the fixtures' sources as they were
then, and OpenSpec change `root-cleanup` moved them (design.md Decision 9,
whose expected difference `tests/leaf_contract_golden.py` reads through
`ROOT_CLEANUP_EXPECTED`).
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


def _sources_of(node, path):
    """The tracked set an artifact of `node` is recorded over, as
    `tests/leaf_contract_golden.py` reads it."""
    for name, marking in node.declared_markings().items():
        if node.marking_file(name) == path:
            return node.marking_sources(marking)
    return node.files


class SourceRecipeTest(TestCase):

    def setUp(self):
        with open(GOLDEN) as handle:
            self.golden = json.load(handle)['fixtures']

    def build(self, fixture, recipe, plain=None):
        """The `{suffix: (digest, fingerprint)}` records of one fixture
        built in a fresh build directory, declaring `recipe`; with a dict
        `plain`, each artifact's plain source digest is put in it, read
        while the build directory exists."""
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
            suffix = path[len(node.basepath):]
            records[suffix] = (
                currency.recorded_digest(path),
                currency.recorded_fingerprint(path))
            if plain is not None:
                plain[suffix] = currency.source_digest(
                    _sources_of(node, path), node._project_root, node.scope)
        return records

    def test_no_recipe_records_what_the_tree_recorded_before(self):
        for fixture in FIXTURES:
            # Re-recorded by `scad-presentation`, whose `assemble()` writes no
            # `.scad` for a leaf that is not SCAD-authored; every other
            # record is the one the tree wrote before `source_recipe`.
            golden = self.golden[fixture]['artifacts']
            plain = {}
            records = self.build(fixture, None, plain)
            with self.subTest(fixture=fixture):
                self.assertEqual(sorted(records), sorted(golden))
            for suffix, (digest, _) in records.items():
                with self.subTest(fixture=fixture, artifact=suffix):
                    self.assertIsNotNone(plain[suffix])
                    self.assertEqual(digest, plain[suffix])

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
