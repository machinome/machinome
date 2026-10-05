# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

import os
import tempfile
import json
import warnings
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock, patch

import cadquery as cq
import numpy as np
import trimesh
from solid2 import cube

from machinome.node import (
    Build123dNode,
    CadQueryNode,
    FusionNode,
    JScadNode,
    MolejoNode,
    OpenScadNode,
    Solid2Node,
)
from machinome.brep_artifacts import write_brep, write_stl
from machinome.brep_cache import (_placement_cache, _shape_cache,
                                   cached_placement, cached_shape)
from machinome.engine.brep import placed_shape, solid_count, solid_volume
from machinome.node.base import StlRenderStart
import machinome.test as test_module
from machinome.test import TestCase as GeometryTestCase, _intersection_stats
from machinome.core.builder import Builder
from tests.brep_test_support import clear_exact_shape_caches
from tests.stand_in import StandIn


class Box(CadQueryNode):

    def __init__(self, size=2, **kwargs):
        self.size = size
        super().__init__(size, **kwargs)

    def render(self):
        return cq.Workplane("XY").box(self.size, self.size, self.size)


class Ring(CadQueryNode):

    def render(self):
        return cq.Workplane("XY").circle(2).circle(1).extrude(2)


class Shaft(CadQueryNode):

    def render(self):
        return cq.Workplane("XY").circle(1).extrude(2)


class Solid2Box(Solid2Node):

    def render(self):
        return cube(2)


class ExactFusion(FusionNode):

    def __init__(self):
        self.ring = Ring()
        self.shaft = Shaft()
        super().__init__()

    def render(self):
        return [self.ring, self.shaft]


class MixedFusion(FusionNode):

    def __init__(self):
        self.exact_child = Box()
        self.faceted_child = Solid2Box()
        super().__init__()

    def render(self):
        return [self.exact_child, self.faceted_child]


class ShapeNode(StandIn):
    rigid = True
    brep = True
    children = ()

    def __init__(self, shape, name, *, matrix_parent=None):
        # `shape()` returns the exact engine's currency, as every exact
        # node's does; a fixture built with CadQuery is unwrapped here.
        self._shape = getattr(shape, 'wrapped', shape)
        self.name = name
        self.operations = []
        self._parent = matrix_parent

    def shape(self):
        return self._shape

    def as_number(self, value):
        return float(value)


class MeshShapeNode(ShapeNode):

    def __init__(self, shape, mesh, name, *, brep=True):
        super().__init__(shape, name)
        self._mesh = mesh
        self.brep = brep

    @property
    def mesh(self):
        mesh = self._mesh.copy()
        for operation in self.operations:
            operation.mesh(mesh)
        return mesh


asserter = GeometryTestCase()


class NodeExactnessTest(TestCase):

    @staticmethod
    def uninitialized(node_type):
        return object.__new__(node_type)

    def test_leaf_exactness_is_derived_from_adapter_type(self):
        self.assertTrue(self.uninitialized(CadQueryNode).brep)
        self.assertTrue(self.uninitialized(Build123dNode).brep)
        # A flexible leaf's exact geometry is per-instant, but WHETHER it
        # has any is fixed by adapter type like every other adapter's.
        self.assertTrue(self.uninitialized(MolejoNode).brep)
        self.assertFalse(self.uninitialized(Solid2Node).brep)
        self.assertFalse(self.uninitialized(OpenScadNode).brep)
        self.assertFalse(self.uninitialized(JScadNode).brep)

    def test_exactness_does_not_require_one_backend(self):
        """Every exact adapter yields the same boundary representation, so a
        mixture of them composes exactly with no backend-agreement rule."""
        fusion = self.uninitialized(FusionNode)
        fusion.children = [self.uninitialized(CadQueryNode),
                           self.uninitialized(Build123dNode)]

        self.assertTrue(fusion.brep)

    def test_fusion_exactness_composes_from_children(self):
        exact = self.uninitialized(CadQueryNode)
        faceted = self.uninitialized(Solid2Node)

        exact_fusion = self.uninitialized(FusionNode)
        exact_fusion.children = [exact]
        self.assertTrue(exact_fusion.brep)

        mixed_fusion = self.uninitialized(FusionNode)
        mixed_fusion.children = [exact, faceted]
        self.assertFalse(mixed_fusion.brep)

    def test_unassembled_internal_node_refuses_vacuous_exactness(self):
        fusion = self.uninitialized(FusionNode)
        fusion.name = "unassembled"

        with self.assertRaisesRegex(RuntimeError, "unassembled"):
            _ = fusion.brep


class ExactArtifactTest(TestCase):

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.old_build_dir = os.environ.get('SOLID_BUILD_DIR')
        os.environ['SOLID_BUILD_DIR'] = self.directory.name
        clear_exact_shape_caches()

    def tearDown(self):
        if self.old_build_dir is None:
            os.environ.pop('SOLID_BUILD_DIR', None)
        else:
            os.environ['SOLID_BUILD_DIR'] = self.old_build_dir

    def test_cadquery_build_writes_current_brep_and_shape_reuses_it(self):
        node = Box()
        node.assemble()

        self.assertTrue(node._up_to_date(node.brep_file))
        self.assertTrue(node._up_to_date(node.stl_file))
        node.model = None
        with patch.object(node, 'render', side_effect=AssertionError(
                'current BREP must avoid rerendering')):
            shape = node.shape()
        self.assertAlmostEqual(cq.Shape.cast(shape).Volume(), 8.0)

    def test_exact_fusion_recovers_native_leaf_after_brep_goes_stale(self):
        fusion = ExactFusion()
        fusion.assemble()
        self.assertTrue(fusion.ring._up_to_date(fusion.ring.brep_file))

        # Both artifacts belong to this test's temporary build directory.
        # The assembled leaf still has SCAD presentation in `.model`.
        os.remove(fusion.ring.brep_file)

        self.assertAlmostEqual(solid_volume(fusion.shape()),
                               8 * 3.141592653589793, places=5)

    def test_shape_is_local_and_does_not_apply_node_operations(self):
        node = Box()
        node.translate([20, 0, 0])
        node.assemble()

        bounds = cq.Shape.cast(node.shape()).BoundingBox()
        self.assertAlmostEqual(bounds.xmin, -1.0, places=6)
        self.assertAlmostEqual(bounds.xmax, 1.0, places=6)

    def test_shape_cache_evicts_the_previous_mtime(self):
        path = os.path.join(self.directory.name, 'shape.brep')
        first_shape = cq.Workplane('XY').box(1, 1, 1).val()
        second_shape = cq.Workplane('XY').box(2, 2, 2).val()
        write_brep(first_shape.wrapped, path, 1 * 10 ** 9)
        first = cached_shape(path)
        write_brep(second_shape.wrapped, path, 2 * 10 ** 9)
        second = cached_shape(path)

        self.assertAlmostEqual(cq.Shape.cast(first).Volume(), 1.0)
        self.assertAlmostEqual(cq.Shape.cast(second).Volume(), 8.0)
        # The key is the artifact's observation (ADR-164); the survivor is
        # the one stamped 2 s.
        self.assertEqual([(key[0], key[1][3]) for key in _shape_cache
                          if key[0] == path],
                         [(path, 2 * 10 ** 9)])

    def test_one_placement_serves_repeated_comparisons(self):
        """A placement is built once per (shape identity, matrix).

        `cached_placement` runs `BRepBuilderAPI_Transform` over the whole
        B-rep -- 6-19 ms on real parts -- and an animated assertion
        places the same solid by the same matrix at every candidate pair
        it visits. The second placement of a matrix already placed must
        cost a lookup.
        """
        path = os.path.join(self.directory.name, 'placed.brep')
        write_brep(cq.Workplane('XY').box(1, 1, 1).val().wrapped, path,
                   1 * 10 ** 9)
        shape = cached_shape(path)
        matrix = np.eye(4)
        matrix[0, 3] = 5.0

        first = cached_placement(shape, matrix)
        second = cached_placement(shape, matrix)

        self.assertIs(second, first)
        self.assertAlmostEqual(
            cq.Shape.cast(first).BoundingBox().xmin, 4.5, places=6)

    def test_a_different_matrix_builds_its_own_placement(self):
        path = os.path.join(self.directory.name, 'placed.brep')
        write_brep(cq.Workplane('XY').box(1, 1, 1).val().wrapped, path,
                   1 * 10 ** 9)
        shape = cached_shape(path)
        near, far = np.eye(4), np.eye(4)
        near[0, 3] = 5.0
        far[0, 3] = 9.0

        placed_near = cached_placement(shape, near)
        placed_far = cached_placement(shape, far)

        self.assertIsNot(placed_near, placed_far)
        self.assertAlmostEqual(
            cq.Shape.cast(placed_near).BoundingBox().xmin, 4.5, places=6)
        self.assertAlmostEqual(
            cq.Shape.cast(placed_far).BoundingBox().xmin, 8.5, places=6)

    def test_a_rebuilt_shape_is_never_served_the_old_placement(self):
        """The hazard this cache exists to avoid.

        A shape cannot be its own cache key: OCCT's sameness (`IsSame`,
        CadQuery's `Shape.__eq__`) compares the underlying TShape and
        ignores location, so a shape and a differently placed copy of it
        compare EQUAL. Nor can `id()` be one on its own, since CPython reuses an
        address after collection. The key is therefore the same
        `(file, observation)` identity `_shape_cache` uses (ADR-164), and
        a rebuild must not be served the old geometry's placement.
        """
        path = os.path.join(self.directory.name, 'rebuilt.brep')
        matrix = np.eye(4)
        matrix[0, 3] = 5.0

        write_brep(cq.Workplane('XY').box(1, 1, 1).val().wrapped, path,
                   1 * 10 ** 9)
        before = cached_placement(cached_shape(path), matrix)
        write_brep(cq.Workplane('XY').box(2, 2, 2).val().wrapped, path,
                   2 * 10 ** 9)
        after = cached_placement(cached_shape(path), matrix)

        self.assertAlmostEqual(cq.Shape.cast(before).Volume(), 1.0)
        self.assertAlmostEqual(cq.Shape.cast(after).Volume(), 8.0)
        self.assertEqual(
            {(key[0][0], key[0][1][3]) for key in _placement_cache
             if key[0][0] == path},
            {(path, 2 * 10 ** 9)},
            'a placement built from the evicted geometry survived')

    def test_a_shape_without_file_identity_is_not_cached(self):
        # A shape built on the fly -- a fusion composed for this
        # comparison, a node whose BREP is not current -- has no identity
        # to key on, so it is placed exactly as it is today.
        shape = cq.Workplane('XY').box(1, 1, 1).val().wrapped
        matrix = np.eye(4)

        first = cached_placement(shape, matrix)
        second = cached_placement(shape, matrix)

        self.assertIsNot(first, second)
        self.assertAlmostEqual(cq.Shape.cast(second).Volume(), 1.0)

    def test_fusion_composes_and_renders_exactly_without_subprocess(self):
        fusion = ExactFusion()
        fusion.assemble()

        with patch('machinome.node.openscad.leaf.Popen', side_effect=AssertionError(
                'exact fusion must not launch OpenSCAD')):
            fusion.build_stls()

        self.assertTrue(fusion._up_to_date(fusion.brep_file))
        self.assertTrue(fusion._up_to_date(fusion.stl_file))
        self.assertEqual(solid_count(fusion.shape()), 1)
        self.assertAlmostEqual(solid_volume(fusion.shape()),
                               8 * 3.141592653589793, places=5)

    def test_publication_keeps_brep_private_and_sweep_spares_it(self):
        node = Box()
        node.assemble()
        builder = Builder('unused.py', build_dir=self.directory.name,
                          watch=False)
        builder.node = node

        builder._write_viewer_snapshot()

        with open(os.path.join(self.directory.name, 'viewer.json')) as handle:
            snapshot = json.load(handle)
        self.assertNotIn('.brep', json.dumps(snapshot))
        self.assertTrue(os.path.exists(node.brep_file))

    def test_builder_requires_brep_currency_for_exact_nodes(self):
        node = Box()
        node.assemble()
        builder = Builder('unused.py', build_dir=self.directory.name,
                          watch=False)
        builder.node = node
        self.assertTrue(builder._artifacts_are_current())

        os.remove(node.brep_file)

        self.assertFalse(builder._artifacts_are_current())

    def test_mixed_fusion_uses_direct_mesh_composition(self):
        fusion = MixedFusion()
        fusion.build_stls()
        os.remove(fusion.stl_file)
        with patch('machinome.node.openscad.binary.require_openscad',
                   side_effect=AssertionError('fusion must not use OpenSCAD')), \
             patch('machinome.node.openscad.leaf.Popen',
                   side_effect=AssertionError('fusion must not launch')):
            fusion.generate_stl()
        self.assertTrue(os.path.exists(fusion.stl_file))


class ExactIntersectionTest(TestCase):

    def box(self, size, name):
        return ShapeNode(cq.Workplane('XY').box(*size).val(), name)

    def test_exact_intersection_reports_path_and_volume(self):
        left = self.box((2, 2, 2), 'left')
        right = self.box((2, 2, 2), 'right')
        right.operations.append(
            __import__('machinome.node.operations', fromlist=['Translation'])
            .Translation([1, 0, 0], right))

        stats = _intersection_stats(left, right)

        self.assertTrue(stats.brep)
        self.assertFalse(stats.is_empty)
        self.assertAlmostEqual(stats.volume, 4.0)

    def test_exact_boundary_contact_contains_no_solid(self):
        left = self.box((2, 2, 2), 'left')
        right = self.box((2, 2, 2), 'right')
        right.operations.append(
            __import__('machinome.node.operations', fromlist=['Translation'])
            .Translation([2, 0, 0], right))

        stats = _intersection_stats(left, right)

        self.assertTrue(stats.brep)
        self.assertTrue(stats.is_empty)
        self.assertEqual(stats.volume, 0.0)

    def test_volume_assertions_share_the_exact_helper(self):
        left = self.box((2, 2, 2), 'left')
        right = self.box((2, 2, 2), 'right')

        asserter.assertIntersectVolumeAbove(left, right, 7.9)
        asserter.assertIntersectVolumeBelow(left, right, 8.1)
        with self.assertRaises(AssertionError):
            asserter.assertNotIntersecting(left, right)

    def test_kernel_failure_names_pair_and_never_loads_mesh(self):
        left = self.box((2, 2, 2), 'left')
        right = self.box((2, 2, 2), 'right')
        failed = Mock()
        failed.IsDone.return_value = False

        with patch('machinome.engine.brep.BRepAlgoAPI_Common',
                   return_value=failed):
            with self.assertRaisesRegex(RuntimeError, 'left.*right'):
                _intersection_stats(left, right)

    def test_exact_aabb_culls_before_boolean(self):
        left = self.box((1, 1, 1), 'left')
        right = self.box((1, 1, 1), 'right')
        from machinome.node.operations import Translation
        right.operations.append(Translation([10, 0, 0], right))

        with patch('machinome.engine.brep.intersect_shapes',
                   side_effect=AssertionError('boolean must be culled')):
            stats = _intersection_stats(left, right)

        self.assertTrue(stats.brep)
        self.assertTrue(stats.is_empty)

    def test_mixed_pair_stays_on_faceted_fallback(self):
        shape = cq.Workplane('XY').box(1, 1, 1).val()
        mesh = trimesh.creation.box((1, 1, 1))
        exact = MeshShapeNode(shape, mesh, 'brep')
        faceted = MeshShapeNode(shape, mesh, 'mesh', brep=False)

        stats = _intersection_stats(exact, faceted)

        self.assertFalse(stats.brep)
        self.assertFalse(stats.is_empty)

    def test_distance_assertions_remain_mesh_based(self):
        shape = cq.Workplane('XY').box(1, 1, 1).val()
        mesh = trimesh.creation.box((1, 1, 1))
        exact = MeshShapeNode(shape, mesh, 'brep')
        other = MeshShapeNode(shape, mesh, 'other')

        with patch.object(exact, 'shape', side_effect=AssertionError(
                'distance assertions must not read exact geometry')):
            asserter.assertClose(exact, other, 0.01)
            asserter.assertFar(exact, other, 0.0)


class ExactConnectivityAndEpsilonTest(TestCase):

    def test_disconnected_exact_solid_is_counted_from_shape(self):
        first = cq.Workplane('XY').box(1, 1, 1).val()
        second = placed_shape(
            cq.Workplane('XY').box(1, 1, 1).val(),
            trimesh.transformations.translation_matrix([3, 0, 0]))
        node = ShapeNode(
            cq.Compound.makeCompound([first, cq.Shape.cast(second)]),
            'broken')

        with self.assertRaisesRegex(AssertionError, 'broken.*2'):
            asserter.assertNoDisconnectedSolids(node)

    def test_exact_join_requires_overlap_not_tangential_contact(self):
        solid = SimpleNamespace(rigid=True, _parent=None, operations=[])
        left = ShapeNode(cq.Workplane('XY').box(2, 2, 2).val(), 'left',
                         matrix_parent=solid)
        overlapping = ShapeNode(
            cq.Workplane('XY').box(2, 2, 2).val(), 'overlapping',
            matrix_parent=solid)
        touching = ShapeNode(
            cq.Workplane('XY').box(2, 2, 2).val(), 'touching',
            matrix_parent=solid)
        from machinome.node.operations import Translation
        overlapping.operations.append(Translation([1, 0, 0], overlapping))
        touching.operations.append(Translation([2, 0, 0], touching))

        asserter.assertJoined(left, overlapping, min_weld_volume=3.9)
        with self.assertRaisesRegex(AssertionError, 'one body'):
            asserter.assertJoined(left, touching)

    def test_all_exact_perturbation_warns_and_ignores_epsilon(self):
        left = ShapeNode(cq.Workplane('XY').box(1, 1, 1).val(), 'left')
        right = ShapeNode(cq.Workplane('XY').box(1, 1, 1).val(), 'right')
        from machinome.node.operations import Translation
        right.operations.append(Translation([10, 0, 0], right))

        with self.assertWarnsRegex(UserWarning, 'assertFreeWithin.*ignored'):
            asserter.assertFreeWithin(
                left, 1, right, along=[0, 1, 0], directions='forward',
                volume_epsilon=1e-6)

    def test_mixed_perturbation_keeps_epsilon_live_without_warning(self):
        shape = cq.Workplane('XY').box(1, 1, 1).val()
        mesh = trimesh.creation.box((1, 1, 1))
        exact = MeshShapeNode(shape, mesh, 'brep')
        faceted = MeshShapeNode(shape, mesh, 'mesh', brep=False)
        from machinome.node.operations import Translation
        faceted.operations.append(Translation([10, 0, 0], faceted))

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            asserter.assertFreeWithin(
                exact, 1, faceted, along=[0, 1, 0], directions='forward',
                volume_epsilon=1e-6)

        self.assertFalse(any('ignored volume_epsilon' in str(item.message)
                             for item in caught))

    def test_exact_pairwise_epsilon_cannot_hide_overlap(self):
        left = ShapeNode(cq.Workplane('XY').box(2, 2, 2).val(), 'left')
        right = ShapeNode(cq.Workplane('XY').box(2, 2, 2).val(), 'right')
        root = SimpleNamespace(rigid=False, children=(left, right),
                               operations=[], _parent=None)
        left._parent = root
        right._parent = root

        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            with self.assertRaises(AssertionError):
                asserter.assertNoPairwiseIntersections(
                    root, volume_epsilon=1000)

    def test_exact_pairwise_flush_contact_passes_and_warns(self):
        left = ShapeNode(cq.Workplane('XY').box(2, 2, 2).val(), 'left')
        right = ShapeNode(cq.Workplane('XY').box(2, 2, 2).val(), 'right')
        from machinome.node.operations import Translation
        right.operations.append(Translation([2, 0, 0], right))
        root = SimpleNamespace(rigid=False, children=(left, right),
                               operations=[], _parent=None)
        left._parent = root
        right._parent = root

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            asserter.assertNoPairwiseIntersections(
                root, volume_epsilon=1e-6)

        self.assertTrue(any('assertNoPairwiseIntersections ignored' in
                            str(item.message) for item in caught))


class StlShapeNode(ShapeNode):
    """An exact node that also has a built STL -- what a real exact leaf
    looks like to the test framework, so a faceted run has a mesh to
    compare while `shape()` stays available to refuse."""

    def __init__(self, shape, stl_file, name, *, matrix_parent=None):
        super().__init__(shape, name, matrix_parent=matrix_parent)
        self.stl_file = stl_file

    def base_mesh(self):
        from machinome.node.base import AbstractBaseNode
        return AbstractBaseNode.base_mesh(self)

    @property
    def mesh(self):
        from machinome.node.base import AbstractBaseNode
        return AbstractBaseNode.mesh.fget(self)


def _refuse_shape(node):
    return patch.object(node, 'shape', side_effect=AssertionError(
        f'{node.name}.shape() must not be read under the faceted kernel'))


class FacetedKernelTest(TestCase):
    """Under the faceted comparison kernel an exact node is compared like
    one that is not: on its mesh, never through its shape, with the run's
    epsilon applied to every engine verdict."""

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.addCleanup(test_module.set_comparison_policy, None)
        test_module._verdict_cache.clear()
        self.unit_box = cq.Workplane('XY').box(1, 1, 1).val()

    def faceted(self, epsilon=0.0):
        test_module.set_comparison_policy(
            test_module.ComparisonPolicy('mesh', epsilon))

    def stl(self, name, mesh):
        path = os.path.join(self.directory.name, f'{name}.stl')
        mesh.export(path)
        return path

    def box_node(self, name, translation=None, size=(1, 1, 1)):
        node = StlShapeNode(
            cq.Workplane('XY').box(*size).val(),
            self.stl(name, trimesh.creation.box(size)), name)
        if translation is not None:
            from machinome.node.operations import Translation
            node.operations.append(Translation(translation, node))
        return node

    def test_two_exact_nodes_are_compared_on_their_meshes(self):
        self.faceted()
        left = self.box_node('left')
        right = self.box_node('right', [0.5, 0, 0])

        with _refuse_shape(left), _refuse_shape(right):
            stats = _intersection_stats(left, right)

        self.assertFalse(stats.brep)
        self.assertFalse(stats.is_empty)
        self.assertAlmostEqual(stats.volume, 0.5, places=6)

    def test_no_kernel_name_is_resolved(self):
        # The engine's operations and the memos over its shapes are what
        # the exact path of the test framework calls; a faceted run never
        # reaches one.
        self.faceted()
        left = self.box_node('left')
        right = self.box_node('right', [0.5, 0, 0])
        refused = {name: patch(name, side_effect=AssertionError(name))
                   for name in (
                       'machinome.engine.brep.intersect_shapes',
                       'machinome.engine.brep.placed_shape',
                       'machinome.engine.brep.fuse_shapes',
                       'machinome.engine.brep.solid_count',
                       'machinome.engine.brep.solid_volume',
                       'machinome.brep_cache.shape_identity',
                       'machinome.brep_cache.cached_bounding_box',
                       'machinome.brep_cache.cached_placement')}
        for refusal in refused.values():
            refusal.start()
            self.addCleanup(refusal.stop)

        stats = _intersection_stats(left, right)
        self.assertFalse(stats.is_empty)
        asserter.assertIntersecting(left, right)

    def test_the_model_still_reports_its_exactness(self):
        self.faceted()
        self.assertTrue(self.box_node('left').brep)

    def test_disconnected_exact_solid_is_counted_from_its_stl(self):
        self.faceted()
        two = trimesh.util.concatenate([
            trimesh.creation.box((1, 1, 1)),
            trimesh.creation.box((1, 1, 1)).apply_translation([3, 0, 0])])
        node = StlShapeNode(self.unit_box, self.stl('broken', two), 'broken')

        with _refuse_shape(node):
            with self.assertRaisesRegex(AssertionError, 'broken.*STL.*2'):
                asserter.assertNoDisconnectedSolids(node)

    def test_exact_features_are_welded_on_their_meshes(self):
        self.faceted()
        solid = SimpleNamespace(rigid=True, _parent=None, operations=[])
        left = StlShapeNode(self.unit_box,
                            self.stl('left', trimesh.creation.box((2, 2, 2))),
                            'left', matrix_parent=solid)
        overlapping = StlShapeNode(
            self.unit_box, self.stl('over', trimesh.creation.box((2, 2, 2))),
            'overlapping', matrix_parent=solid)
        from machinome.node.operations import Translation
        overlapping.operations.append(Translation([1, 0, 0], overlapping))

        with _refuse_shape(left), _refuse_shape(overlapping), patch(
                'machinome.engine.brep.fuse_shapes',
                side_effect=AssertionError('no fuse on the faceted kernel')):
            asserter.assertJoined(left, overlapping, min_weld_volume=3.9)

    def test_an_exact_assembly_is_verified_on_manifolds(self):
        self.faceted()
        apart = self.box_node('apart', [5, 0, 0])
        near = self.box_node('near')
        root = SimpleNamespace(rigid=False, children=(apart, near),
                               operations=[], _parent=None)
        apart._parent = near._parent = root

        with _refuse_shape(apart), _refuse_shape(near):
            asserter.assertNoSolidInterference(root)

        overlapping = self.box_node('overlapping', [0.5, 0, 0])
        root.children = (overlapping, near)
        overlapping._parent = root
        with _refuse_shape(overlapping), _refuse_shape(near):
            with self.assertRaisesRegex(AssertionError,
                                        'intersection volume 0.5'):
                asserter.assertNoSolidInterference(root)

    def test_the_run_epsilon_absorbs_a_sliver(self):
        self.faceted(epsilon=0.5)
        left = self.box_node('left')
        right = self.box_node('right', [0.8, 0, 0])

        stats = _intersection_stats(left, right)

        self.assertTrue(stats.is_empty)
        self.assertEqual(stats.volume, 0.0)
        asserter.assertNotIntersecting(left, right)

    def test_a_real_overlap_survives_the_run_epsilon(self):
        self.faceted(epsilon=0.5)
        left = self.box_node('left', size=(4, 4, 4))
        right = self.box_node('right', [3.25, 0, 0], size=(4, 4, 4))

        stats = _intersection_stats(left, right)

        self.assertFalse(stats.is_empty)
        self.assertAlmostEqual(stats.volume, 12.0, places=6)
        with self.assertRaisesRegex(AssertionError, 'left.*right'):
            asserter.assertNotIntersecting(left, right)

    def test_the_run_epsilon_reaches_the_assembly_assertion(self):
        self.faceted(epsilon=0.5)
        left = self.box_node('left')
        right = self.box_node('right', [0.8, 0, 0])
        root = SimpleNamespace(rigid=False, children=(left, right),
                               operations=[], _parent=None)
        left._parent = right._parent = root

        asserter.assertNoSolidInterference(root)

    def test_a_strict_faceted_run_keeps_flush_contact_fouling(self):
        # Epsilon 0.0 changes nothing: the non-empty zero-volume flush
        # contact of ADR-025/029 still fouls, as it does today.
        self.faceted(epsilon=0.0)
        left = self.box_node('left')
        right = self.box_node('right', [1.0, 0, 0])

        stats = _intersection_stats(left, right)

        self.assertEqual(stats.volume, 0.0)
        self.assertFalse(stats.is_empty)

    def test_a_perturbation_epsilon_stays_live_without_a_warning(self):
        self.faceted(epsilon=0.25)
        left = self.box_node('left')
        right = self.box_node('right', [10, 0, 0])

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            asserter.assertFreeWithin(
                left, 1, right, along=[0, 1, 0], directions='forward',
                volume_epsilon=1e-6)

        self.assertFalse(any('ignored volume_epsilon' in str(item.message)
                             for item in caught))

    def test_the_verdict_cache_holds_the_raw_verdict(self):
        self.faceted(epsilon=0.5)
        left = self.box_node('left')
        right = self.box_node('right', [0.8, 0, 0])
        self.assertTrue(_intersection_stats(left, right).is_empty)

        self.faceted(epsilon=0.0)
        stats = _intersection_stats(left, right)

        self.assertFalse(stats.is_empty)
        self.assertAlmostEqual(stats.volume, 0.2, places=6)

    def test_the_exact_kernel_is_untouched(self):
        test_module.set_comparison_policy(
            test_module.ComparisonPolicy('brep', 0.0))
        left = self.box_node('left')
        right = self.box_node('right', [0.5, 0, 0])

        stats = _intersection_stats(left, right)

        self.assertTrue(stats.brep)
        self.assertAlmostEqual(stats.volume, 0.5, places=6)


class MeshNeverJudgedOnTheExactPathTest(FacetedKernelTest):
    """Selecting a solid, placing it in the broad phase, or comparing it
    on the exact kernel never judges its mesh: only a faceted read asks
    the engine, and only the engine's own status refuses."""

    def holey_node(self, name, translation=None):
        holey = trimesh.creation.box((1, 1, 1))
        holey.faces = holey.faces[:-1]
        node = StlShapeNode(self.unit_box, self.stl(name, holey), name)
        if translation is not None:
            from machinome.node.operations import Translation
            node.operations.append(Translation(translation, node))
        return node

    def no_engine(self):
        return patch.object(test_module, 'require_mesh_engine',
                            side_effect=AssertionError('no Manifold here'))

    def test_an_exact_run_never_judges_a_mesh(self):
        left = self.holey_node('holey')
        right = self.box_node('right', [0.5, 0, 0])

        with self.no_engine():
            stats = _intersection_stats(left, right)

        self.assertTrue(stats.brep)
        self.assertFalse(stats.is_empty)
        self.assertAlmostEqual(stats.volume, 0.5, places=6)

    def test_the_broad_phase_does_not_judge_a_mesh(self):
        holey = self.holey_node('holey', [5, 0, 0])
        near = self.box_node('near')
        root = SimpleNamespace(rigid=False, children=(holey, near),
                               operations=[], _parent=None)
        holey._parent = near._parent = root

        with self.no_engine():
            asserter.assertNoSolidInterference(root)

    def test_a_faceted_run_refuses_only_what_the_engine_refuses(self):
        self.faceted()
        left = self.holey_node('holey')
        right = self.box_node('right', [0.5, 0, 0])

        with self.assertRaisesRegex(ValueError, 'holey.*NotManifold'):
            _intersection_stats(left, right)


class DegenerateTriangleExportTest(TestCase):
    """An exact artifact's mesh carries no degenerate triangles: the
    leaf export drops what OCCT tessellates with no area, as the fused
    solid's export already did."""

    def test_write_stl_drops_degenerate_triangles(self):
        box = trimesh.creation.box((2, 2, 2))
        vertices = np.vstack([box.vertices, [[5, 5, 5], [6, 6, 6]]])
        faces = np.vstack([box.faces, [[8, 8, 9]]])
        tessellated = trimesh.Trimesh(vertices, faces, process=False)

        def engine_write_stl(shape, path, linear, angular):
            tessellated.export(path, file_type='stl')

        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, 'leaf.stl')
            with patch('machinome.engine.brep.write_stl', engine_write_stl):
                write_stl(object(), path, 1 * 10 ** 9, 0.1, 0.1)
            raw = trimesh.load(path, process=False)

        self.assertEqual(len(raw.faces), 12)
        self.assertTrue(raw.nondegenerate_faces().all())
        self.assertEqual(len(raw.vertices), 36)


class FaceBoxTierAssertionTest(TestCase):
    """`assertNoSolidInterference`'s own use of the face-box tier
    (ADR-092): the assembly-level scenarios `tests/test_face_box_culling.py`
    proves at the `_faces_disjoint`/`_brep_verdict` level, reached here
    through the public assertion instead."""

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)

    def stl_for(self, shape, name):
        path = os.path.join(self.directory.name, f'{name}.stl')
        shape.exportStl(path, tolerance=0.1, angularTolerance=0.1)
        return path

    def node(self, shape, name):
        return StlShapeNode(shape, self.stl_for(shape, name), name)

    def root(self, *children):
        root = SimpleNamespace(rigid=False, children=tuple(children),
                               operations=[], _parent=None)
        for child in children:
            child._parent = root
        return root

    def _frame_and_two_wheels(self):
        plate = cq.Workplane('XY').box(20, 20, 2)
        top = plate.translate((0, 0, 11))
        bottom = plate.translate((0, 0, -11))
        pillar = (cq.Workplane('XY').center(8, 8).circle(1)
                 .extrude(22).translate((0, 0, -11)))
        frame = top.union(bottom).union(pillar).val()
        wheel_a = cq.Workplane('XY').circle(3).extrude(2) \
            .translate((-6, -6, -1)).val()
        wheel_b = cq.Workplane('XY').circle(3).extrude(2) \
            .translate((6, -6, -1)).val()
        return frame, wheel_a, wheel_b

    def test_a_three_solid_assembly_between_plates_passes_with_no_boolean(
            self):
        frame, wheel_a, wheel_b = self._frame_and_two_wheels()
        root = self.root(self.node(frame, 'frame'),
                         self.node(wheel_a, 'wheel_a'),
                         self.node(wheel_b, 'wheel_b'))

        with patch(
                'machinome.engine.brep.intersect_shapes',
                side_effect=AssertionError('boolean must be culled')):
            asserter.assertNoSolidInterference(root)

    def test_containment_still_fails_naming_both_solids_and_the_volume(self):
        big = self.node(cq.Workplane('XY').box(10, 10, 10).val(), 'big')
        small = self.node(cq.Workplane('XY').box(2, 2, 2).val(), 'small')
        root = self.root(big, small)

        with self.assertRaises(AssertionError) as failure:
            asserter.assertNoSolidInterference(root)

        message = str(failure.exception)
        self.assertIn('big', message)
        self.assertIn('small', message)
        self.assertIn('8', message)

    def test_a_solid_in_a_cavity_passes(self):
        hollow = self.node(
            cq.Workplane('XY').box(20, 20, 20)
            .faces('>Z').workplane().rect(10, 10).cutBlind(-15).val(),
            'hollow')
        inner = self.node(cq.Workplane('XY').box(2, 2, 2).val(), 'inner')
        root = self.root(hollow, inner)

        asserter.assertNoSolidInterference(root)

    def test_a_compound_with_one_component_inside_fails(self):
        outside = cq.Workplane('XY').box(2, 2, 2).translate((0, 0, 50)).val()
        inside = cq.Workplane('XY').box(2, 2, 2).val()
        compound = cq.Compound.makeCompound([outside, inside])
        compound_node = self.node(compound, 'compound')
        big = self.node(cq.Workplane('XY').box(10, 10, 10).val(), 'big')
        root = self.root(compound_node, big)

        with self.assertRaises(AssertionError) as failure:
            asserter.assertNoSolidInterference(root)

        message = str(failure.exception)
        self.assertIn('compound', message)
        self.assertIn('big', message)
