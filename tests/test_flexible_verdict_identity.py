# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A flexible leaf's verdicts are keyed on its STATE, in both tiers.

ADR-070 kept flexible pairs out of the verdict memo "by construction": its
census keyed pairs by NAME, and two instants at one relative placement are
different questions when the flexible part's binding differs. That argument
is right about names and does not reach state. `_faceted_cache_snapshot`
already computes the leaf's full state -- technology, defining module,
source digest, structural identity, bound values, spec digest -- to key its
own Manifold cache, and `_fast_geometry` threw it away; on the exact path an
evaluated molejo solid had no `shape_identity` at all. ADR-070 measured the
cost on the v8-engine root suite: 1499 s of its 1622.8 s left after the memo
went to flexible comparisons, about 430 ms each on the exact kernel.

The persisted identity drops the two components that are not state: the
absolute source path (a moved project must keep its identity) and the
source fingerprint (metadata that a clone, a move or a touch changes). The
tests below pin that, the override rules that keep a custom evaluation seam
uncached, and the coherence rule: the identity names the geometry actually
compared.
"""

import json
import os
import shutil
import sys
from unittest.mock import PropertyMock, patch

from trimesh.creation import box

import machinome.test as test_module
from machinome.occt import engine as occt_engine
from machinome.core.loader import import_module_from_path
from machinome.node import base as base_module

from .flexible_project import spring as fixture
from .test_intersection_memo import ExactFakeNode, FakeNode
from .test_verdict_store import StoreTestCase


class ShapeOverrideSpring(fixture.Spring):
    """A project override of FlexibleNode's public exact seam."""

    def shape(self):
        return super().shape()


class TranslatedMeshSpring(fixture.Spring):
    """A project override of FlexibleNode's public faceted seam."""

    def base_mesh(self):
        mesh = super().base_mesh()
        mesh.apply_translation([0.5, 0, 0])
        return mesh


class FlexiblePairTestCase(StoreTestCase):
    """A molejo spring against a plate its first coil passes through."""

    def spring(self, lift=4.0, node_class=fixture.Spring):
        node = node_class()
        node.height.value = fixture.FREE_HEIGHT - lift
        return node

    def faceted_plate(self):
        path = self.artifact_path('plate', 'stl')
        if not os.path.exists(path):
            box((30, 30, 4)).export(path)
        return FakeNode('Plate', path)

    def exact_plate(self):
        path = self.artifact_path('plate', 'brep')
        if not os.path.exists(path):
            self.brep('plate', (30, 30, 4))
        return ExactFakeNode('Plate', path)

    def plate(self, kernel):
        return (self.exact_plate() if kernel == 'exact'
                else self.faceted_plate())

class ExactPathKeysFlexiblePairs(FlexiblePairTestCase):
    """Task 3.2: under the exact kernel the evaluated solid carries the
    state identity of the snapshot that built it."""

    def test_one_binding_runs_one_boolean_and_another_binding_another(self):
        spring = self.spring(4.0)
        plate = self.exact_plate()
        with patch.object(occt_engine, 'intersect_shapes',
                          wraps=occt_engine.intersect_shapes) as boolean:
            first = test_module._intersection_stats(spring, plate)
            second = test_module._intersection_stats(spring, plate)
            self.assertEqual(boolean.call_count, 1,
                             'the same binding ran a second OCCT boolean')
            spring.height.value = fixture.FREE_HEIGHT - 8.0
            test_module._intersection_stats(spring, plate)

        self.assertEqual(boolean.call_count, 2,
                         'a new binding was served the old verdict')
        self.assertFalse(first.is_empty)
        self.assertBitIdentical(second, first)


class AcrossAFreshProcess(FlexiblePairTestCase):
    """Task 3.3: the equal binding is served from the store, a different
    binding is computed, on both paths."""

    def test_both_paths(self):
        for kernel in ('faceted', 'exact'):
            with self.subTest(kernel=kernel):
                shutil.rmtree(self.store_directory, ignore_errors=True)
                self.fresh_process()
                self.set_policy(kernel=kernel)
                with self.counted() as computed:
                    decided = test_module._intersection_stats(
                        self.spring(4.0), self.plate(kernel))
                self.assertEqual(computed.count, 1)
                self.fresh_process()

                with self.counted() as computed:
                    served = test_module._intersection_stats(
                        self.spring(4.0), self.plate(kernel))
                    self.assertEqual(computed.count, 0,
                                     'the equal binding was not served')
                    test_module._intersection_stats(
                        self.spring(8.0), self.plate(kernel))
                self.assertEqual(computed.count, 1,
                                 'a different binding was served')
                self.assertBitIdentical(served, decided)


COIL_SOURCE = '''\
from molejo import Circle, Helix, P, Shape

from machinome.motion.ports import TranslationalPort
from machinome.node import MolejoNode


class Coil(MolejoNode):

    height = TranslationalPort(unit='mm')

    def render(self):
        return Shape(profile=Circle(radius=1.0),
                     path=[Helix(radius=5.0, turns=3, height=P.height)],
                     path_samples=60, profile_samples=8)
'''


class StateIdentityIsState(FlexiblePairTestCase):
    """Task 3.4: nothing absolute and no metadata; content, spec and
    values only."""

    PACKAGE = 'flexible_identity_fixture'

    def setUp(self):
        super().setUp()
        self.addCleanup(self.forget)

    def forget(self):
        for name in list(sys.modules):
            if name == self.PACKAGE or name.startswith(self.PACKAGE + '.'):
                del sys.modules[name]

    def write_project(self, root):
        package = os.path.join(root, self.PACKAGE)
        os.makedirs(package)
        with open(os.path.join(root, 'pyproject.toml'), 'w') as manifest:
            manifest.write('[tool.machinome]\n'
                           f'model = "{self.PACKAGE}.coil:Coil"\n')
        open(os.path.join(package, '__init__.py'), 'w').close()
        with open(os.path.join(package, 'coil.py'), 'w') as source:
            source.write(COIL_SOURCE)
        return os.path.join(package, 'coil.py')

    def coil(self, root, height=20.0):
        self.forget()
        module = import_module_from_path(
            os.path.join(root, self.PACKAGE, 'coil.py'), root)
        node = module.Coil()
        node.height.value = height
        return node

    def identity(self, node):
        identity, _, _ = node._state_snapshot()
        self.assertIsNotNone(identity)
        return identity

    def test_a_moved_project_keeps_its_state_identity(self):
        root = os.path.join(self.scratch, 'flex')
        self.write_project(root)
        before = self.coil(root)
        identity = self.identity(before)
        geometry_key = before._faceted_cache_snapshot()[0]

        moved = os.path.join(self.scratch, 'elsewhere', 'flex')
        os.makedirs(os.path.dirname(moved))
        os.rename(root, moved)
        after = self.coil(moved)

        self.assertEqual(self.identity(after), identity,
                         'moving the project changed the state identity')
        self.assertNotEqual(after._faceted_cache_snapshot()[0], geometry_key,
                            'the Manifold key names no absolute path, so '
                            'this move proves nothing')
        self.assertNotIn(root, json.dumps(identity))
        self.assertNotIn(moved, json.dumps(identity))

    def test_an_identical_source_rewrite_keeps_its_state_identity(self):
        root = os.path.join(self.scratch, 'flex')
        source = self.write_project(root)
        before = self.coil(root)
        identity = self.identity(before)
        fingerprint = before.source_fingerprint

        with open(source, 'rb') as handle:
            data = handle.read()
        stat = os.stat(source)
        with open(f'{source}.new', 'wb') as handle:
            handle.write(data)
        os.replace(f'{source}.new', source)
        os.utime(source, ns=(stat.st_atime_ns,
                             stat.st_mtime_ns + 5 * 10 ** 9))
        after = self.coil(root)

        self.assertNotEqual(after.source_fingerprint, fingerprint,
                            'the rewrite left the fingerprint alone; this '
                            'proves nothing')
        self.assertEqual(self.identity(after), identity)

    def test_content_spec_and_values_change_the_identity(self):
        root = os.path.join(self.scratch, 'flex')
        source = self.write_project(root)
        identity = self.identity(self.coil(root))

        self.assertNotEqual(self.identity(self.coil(root, height=21.0)),
                            identity, 'a bound value is not in the identity')

        node = self.coil(root)
        original = node._shape_spec
        with patch.object(node, '_shape_spec', side_effect=lambda rendered: {
                **original(rendered), 'revision': 'next'}):
            self.assertNotEqual(self.identity(node), identity,
                                'the spec is not in the identity')

        with open(source, 'a') as handle:
            handle.write('\n# an edit\n')
        self.assertNotEqual(self.identity(self.coil(root)), identity,
                            'the source content is not in the identity')


class CustomSeamsStayUncached(FlexiblePairTestCase):
    """Task 3.5: an override's geometry is not proven to be a function of
    the serialized spec, so nothing is kept for it in either tier."""

    def test_a_base_mesh_override_is_uncached_on_the_faceted_path(self):
        self.set_policy(kernel='faceted')
        spring = self.spring(4.0, TranslatedMeshSpring)
        plate = self.faceted_plate()
        with self.counted() as computed:
            test_module._intersection_stats(spring, plate)
            test_module._intersection_stats(spring, plate)
        self.assertEqual(computed.count, 2)
        self.assertEqual(len(test_module._verdict_cache), 0)
        self.assertNothingKept()

    def test_a_shape_override_is_uncached_on_the_exact_path(self):
        spring = self.spring(4.0, ShapeOverrideSpring)
        plate = self.exact_plate()
        with self.counted() as computed:
            test_module._intersection_stats(spring, plate)
            test_module._intersection_stats(spring, plate)
        self.assertEqual(computed.count, 2)
        self.assertEqual(len(test_module._verdict_cache), 0)
        self.assertNothingKept()


class IdentityNamesTheComparedGeometry(FlexiblePairTestCase):
    """Task 3.6: coherence."""

    def test_the_exact_solid_carries_the_identity_of_its_snapshot(self):
        spring = self.spring(4.0)
        snapshots = []
        real = spring._snapshot

        def recorded(*arguments, **keywords):
            snapshot = real(*arguments, **keywords)
            snapshots.append(snapshot)
            return snapshot

        with patch.object(spring, '_snapshot', side_effect=recorded), \
                patch.object(spring, 'current_shape',
                             wraps=spring.current_shape) as rendered:
            solid = spring.shape()
            again = spring.shape()

        self.assertIs(again, solid)
        self.assertEqual(rendered.call_count, 1)
        self.assertEqual(len(snapshots), 1)
        self.assertIsNotNone(snapshots[0][1])
        self.assertEqual(spring._exact_state_identity(solid),
                         snapshots[0][1])
        self.assertIsNone(spring._exact_state_identity(object()),
                          'a shape the leaf did not build carries its '
                          'identity')

    def test_a_faceted_miss_evaluates_the_one_snapshot_it_is_keyed_on(self):
        spring = self.spring(3.0)
        observed = []
        real = spring.current_shape

        def current_shape():
            rendered = real()
            observed.append(rendered)
            return rendered

        with patch.object(spring, 'current_shape',
                          side_effect=current_shape) as current, \
                patch.object(spring, '_snapshot_mesh',
                             wraps=spring._snapshot_mesh) as evaluated:
            _, _, identity = test_module._flexible_geometry(spring)

        self.assertEqual(current.call_count, 1)
        self.assertIs(evaluated.call_args.args[0], observed[0])
        expected, _, _ = self.spring(3.0)._state_snapshot()
        self.assertEqual(identity, expected)

    def test_a_shortened_binding_hash_collision_shares_no_verdict(self):
        self.set_policy(kernel='faceted')
        spring = self.spring(0.0)
        plate = self.faceted_plate()
        with patch.object(base_module, '_HASH_LEN', 0), \
                self.counted() as computed:
            first = test_module._intersection_stats(spring, plate)
            spring.height.value = fixture.FREE_HEIGHT - 5.0
            second = test_module._intersection_stats(spring, plate)
        self.assertEqual(computed.count, 2)
        self.assertNotEqual(first.volume, second.volume)

    def test_an_exact_binding_hash_collision_keeps_the_old_solids_identity(self):
        spring = self.spring(0.0)
        with patch.object(base_module, '_HASH_LEN', 0):
            first = spring.shape()
            identity = spring._exact_state_identity(first)
            spring.height.value = fixture.FREE_HEIGHT - 5.0
            second = spring.shape()
            # The collision serves the older binding's solid; the identity
            # it carries is that older binding's too, so a verdict keyed on
            # it still names the geometry compared.
            self.assertIs(second, first)
            self.assertEqual(spring._exact_state_identity(second), identity)
            current, _, _ = spring._state_snapshot()
        self.assertNotEqual(current, identity)


class UnobservableSource(FlexiblePairTestCase):
    """Task 3.7: no source digest, no identity; computed every time."""

    def test_an_unreadable_source_is_never_kept(self):
        for kernel in ('faceted', 'exact'):
            with self.subTest(kernel=kernel):
                self.fresh_process()
                self.set_policy(kernel=kernel)
                spring = self.spring(3.0)
                plate = self.plate(kernel)
                with patch.object(type(spring), 'source_digest',
                                  new_callable=PropertyMock,
                                  return_value=None), \
                        self.counted() as computed:
                    self.assertIsNone(spring._state_snapshot()[0])
                    test_module._intersection_stats(spring, plate)
                    test_module._intersection_stats(spring, plate)
                self.assertEqual(computed.count, 2)
                self.assertEqual(len(test_module._verdict_cache), 0)
                self.assertNothingKept()
