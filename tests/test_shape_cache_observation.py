# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The loaded-shape cache keys on the artifact's observation (OpenSpec
change `leaf-contract`, capability `exact-geometry`, ADR-164).

Every exact artifact is stamped with its source's mtime, so a `.brep`
replaced under an unchanged source -- a node whose `source_recipe`
changed -- has the stamp of the one it replaced. Keyed on the path and
that stamp, the cache served the old shape; keyed on the observation of
the file (device, inode, size, mtime, ctime), the replacement is a new
key, because the core publishes every artifact by renaming a newly
written file into place.
"""

import os
import shutil
import tempfile
from unittest import TestCase
from unittest.mock import patch

import numpy as np
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.gp import gp_Pnt

from machinome import exact_cache
from machinome._artifact import observe_artifact
from machinome.exact_artifacts import write_brep
from machinome.occt import engine

STAMP = 1_790_000_000_123_456_789


def _box(size):
    return BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), size, size, size).Shape()


class ShapeCacheObservationTest(TestCase):

    def setUp(self):
        self.directory = tempfile.mkdtemp(prefix='shape-cache-observation-')
        self.addCleanup(shutil.rmtree, self.directory, ignore_errors=True)
        self.path = os.path.join(self.directory, 'part.brep')

    def test_a_replacement_under_the_same_stamp_is_not_served_stale(self):
        write_brep(_box(2), self.path, STAMP)
        first = exact_cache.cached_shape(self.path)
        key = exact_cache.shape_identity(first)
        exact_cache.cached_bounding_box(first)
        exact_cache.cached_face_boxes(first)
        exact_cache.cached_placement(first, np.eye(4))
        self.assertIn(key, exact_cache._bounds_cache)

        write_brep(_box(3), self.path, STAMP)
        self.assertEqual(os.stat(self.path).st_mtime_ns, STAMP)
        second = exact_cache.cached_shape(self.path)

        self.assertAlmostEqual(engine.solid_volume(second), 27.0)
        self.assertIsNot(second, first)
        self.assertNotIn(key, exact_cache._shape_cache)
        self.assertNotIn(key, exact_cache._bounds_cache)
        self.assertNotIn(key, exact_cache._face_box_cache)
        self.assertEqual([placement for placement in exact_cache._placement_cache
                          if placement[0] == key], [])

    def test_a_repeated_request_reads_the_file_once(self):
        write_brep(_box(2), self.path, STAMP)
        first = exact_cache.cached_shape(self.path)

        with patch('machinome.occt.engine.read_brep',
                   wraps=engine.read_brep) as read:
            again = exact_cache.cached_shape(self.path)

        self.assertIs(again, first)
        self.assertEqual(read.call_count, 0)

    def test_the_load_observation_is_the_files(self):
        write_brep(_box(2), self.path, STAMP)
        shape = exact_cache.cached_shape(self.path)

        self.assertEqual(exact_cache.shape_load_observation(
            exact_cache.shape_identity(shape)), observe_artifact(self.path))


class RecipeReplacementTest(TestCase):
    """The node-level form: an exact leaf outside the core whose recipe
    changes between two constructions in one process."""

    def setUp(self):
        self.build_dir = tempfile.mkdtemp(prefix='shape-cache-recipe-')
        self.addCleanup(shutil.rmtree, self.build_dir, ignore_errors=True)
        environment = patch.dict(os.environ,
                                 {'SOLID_BUILD_DIR': self.build_dir})
        environment.start()
        self.addCleanup(environment.stop)
        import tests.contract_package.exact_stand_in as stand_in
        self.stand_in = stand_in
        recipe = stand_in.RECIPE
        self.addCleanup(setattr, stand_in, 'RECIPE', recipe)

    def test_a_rebuilt_shape_is_read_with_no_eviction_by_the_node(self):
        stand_in = self.stand_in
        stand_in.RECIPE = 'native-v1'
        first = stand_in.NativeSolid()
        first.assemble()
        self.assertAlmostEqual(engine.solid_volume(first.shape()),
                               np.pi * 3 ** 2 * 20, places=3)

        stand_in.RECIPE = 'native-v2'
        second = stand_in.NativeSolid()
        second.assemble()

        self.assertEqual(second.brep_file, first.brep_file)
        self.assertEqual(second.mtime_ns, first.mtime_ns)
        self.assertAlmostEqual(engine.solid_volume(second.shape()),
                               np.pi * 4 ** 2 * 20, places=3)
