# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A decided verdict is kept between runs of a project.

The finding (`workflow/warts.md`, "3DPrintedClocks wall clock 02 and
strandbeest (2026-09-29, verdict memo across runs)"): at framework `main`
bf24687, `machinome test wall_clock_02` took 1348.9 s cold, 95% of it inside
verdict-memo misses (1138 misses, 643 OCCT booleans at 1.93 s each), and
18.35 s with the memo already warm, every one of its 4238 asks served and
the same 16 passed and 6 failed. strandbeest's walking demo took 246.9 s
cold (92% in misses, 1055 booleans) and 11.97 s warm. The ADR-070 memo dies
with the process, and the studio floor starts a fresh `machinome test`
process for every run, so every floor run was cold.

The persistent tier sits beneath that memo. These tests pin what it must do
and, paired with every "served" assertion, what it must never do: serve a
changed artifact's old verdict, serve across a quantum, a stamp or a
corrupt file, keep what the memo refuses to key, or lose a record to a
concurrent writer or compaction.

The framework's own suite runs with the store off (`tests/conftest.py`).
Every case here switches it on explicitly, on a temporary build root, and
`fresh_process()` drops exactly what a new interpreter would not have.
"""

import hashlib
import io
import multiprocessing
import os
import shutil
import stat
import struct
import tempfile
import time
from argparse import Namespace
from contextlib import chdir, contextmanager, redirect_stderr, redirect_stdout
from unittest import TestCase, skipIf
from unittest.mock import patch

import cadquery as cq
import numpy as np
from trimesh.creation import box

import machinome
import machinome.test as test_module
from machinome import _verdict_store as store
from machinome import exact_cache
from machinome._artifact import VERDICT_STORE_DIRECTORY, observe_artifact
from machinome.core.builder import unanchor_build_dir
from machinome.exact_artifacts import write_brep
from machinome.exact_engine import ExactCommonInconsistency
from machinome.occt import engine as occt_engine
from machinome.node import base as base_module
from machinome.node.operations import Translation

from . import verdict_store_workers as workers
from .exact_test_support import clear_exact_shape_caches
from .import_probe import probe
from .test_assembly_integrity import Assembly, RigidNode
from .test_intersection_memo import ExactFakeNode, FakeNode, MeshOnlyNode
from .test_named_models import NamedProjectTest


asserter = test_module.TestCase()

KERNEL_MODULES = ('cadquery', 'OCP', 'manifold3d', 'trimesh', 'molejo')

#: A mesh engine identity, as a faceted verdict's key carries one.
ENGINE = ('manifold3d', '3.5.2')


def bits(value):
    """A float's IEEE-754 bytes: what 'bit for bit' compares."""
    return struct.pack('<d', value)


def forget_process_state():
    """Drop everything a fresh interpreter would not have: the in-process
    memo and its observations, the store's loaded index, pending records,
    digest memo and stamp, the exact shape cache and the mesh-solid, bounds
    and base-mesh caches."""
    store._reset()
    test_module._verdict_cache.clear()
    test_module._verdict_observations.clear()
    test_module._mesh_solid_cache.clear()
    test_module._bounds_cache.clear()
    test_module._flexible_mesh_solid_cache.clear()
    base_module._base_mesh_cache.clear()
    clear_exact_shape_caches()


class Counter:

    def __init__(self, *mocks):
        self.mocks = mocks

    @property
    def count(self):
        return sum(mock.call_count for mock in self.mocks)


class StoreTestCase(TestCase):
    """A temporary project with an absolute build root and the store on."""

    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix='machinome-verdicts-')
        self.addCleanup(directory.cleanup)
        self.scratch = os.path.realpath(directory.name)
        self.project = os.path.join(self.scratch, 'project')
        self.build_root = os.path.join(self.project, '_build')
        os.makedirs(self.build_root)
        environment = patch.dict(os.environ,
                                 {'SOLID_BUILD_DIR': self.build_root})
        environment.start()
        self.addCleanup(environment.stop)
        self.addCleanup(unanchor_build_dir)
        # tests/conftest.py suspends the store for the whole framework
        # suite; these cases switch it on explicitly.
        switched_on = patch.object(store, '_suspended', False)
        switched_on.start()
        self.addCleanup(switched_on.stop)
        forget_process_state()
        self.addCleanup(forget_process_state)
        self.set_policy()
        self.addCleanup(test_module.set_comparison_policy, None)

    # -- the run -------------------------------------------------------

    def set_policy(self, kernel='exact', epsilon=0.0,
                   quantum=test_module.DEFAULT_PLACEMENT_QUANTUM,
                   verdict_store=True):
        test_module.set_comparison_policy(test_module.ComparisonPolicy(
            kernel, epsilon, quantum, verdict_store))

    def fresh_process(self):
        """End this 'process' as a run does, flushing, and start another."""
        store.flush()
        forget_process_state()

    @contextmanager
    def counted(self):
        """Count verdict computations on either path: a served verdict
        never reaches the helper that decides a pair."""
        with patch.object(test_module, '_exact_verdict',
                          wraps=test_module._exact_verdict) as exact, \
                patch.object(test_module, '_faceted_verdict',
                             wraps=test_module._faceted_verdict) as faceted:
            yield Counter(exact, faceted)

    # -- artifacts -----------------------------------------------------

    def artifact_path(self, name, extension):
        directory = os.path.join(self.build_root, 'parts')
        os.makedirs(directory, exist_ok=True)
        return os.path.join(directory, f'{name}.{extension}')

    def stl(self, name, mesh):
        path = self.artifact_path(name, 'stl')
        mesh.export(path)
        return path

    def brep(self, name, size=(1, 1, 1), offset=(0, 0, 0)):
        path = self.artifact_path(name, 'brep')
        write_brep(cq.Workplane('XY').box(*size).translate(offset).val()
                   .wrapped, path, 1 * 10 ** 9)
        return path

    def faceted(self, name, path, translation=(0, 0, 0)):
        node = FakeNode(name, path)
        node.operations.append(Translation(list(translation), node))
        return node

    def exact(self, name, path, translation=(0, 0, 0)):
        node = ExactFakeNode(name, path)
        node.operations.append(Translation(list(translation), node))
        return node

    def faceted_pair(self, first, second, offset):
        return (self.faceted('First', first),
                self.faceted('Second', second, offset))

    def exact_pair(self, first, second, offset):
        return (self.exact('First', first),
                self.exact('Second', second, offset))

    # -- the store on disk ---------------------------------------------

    @property
    def store_directory(self):
        return os.path.join(self.build_root, VERDICT_STORE_DIRECTORY)

    def segments(self, directory=None):
        directory = directory or self.store_directory
        if not os.path.isdir(directory):
            return []
        return sorted(os.path.join(directory, name)
                      for name in os.listdir(directory)
                      if store.SEGMENT_NAME.match(name))

    def stored_records(self, directory=None):
        records = []
        for path in self.segments(directory):
            read = store.read_segment(path)
            self.assertIsNotNone(read, f'{path} did not validate')
            records.extend(read)
        return records

    def store_bytes(self, directory):
        data = b''
        for folder, _, names in os.walk(directory):
            for name in names:
                with open(os.path.join(folder, name), 'rb') as handle:
                    data += handle.read()
        return data

    def assertBitIdentical(self, served, decided):
        self.assertIsInstance(served, test_module.IntersectionStats)
        self.assertEqual((served.is_empty, served.exact),
                         (decided.is_empty, decided.exact))
        self.assertEqual(bits(served.volume), bits(decided.volume))

    def assertNothingKept(self):
        current = store._current
        pending = {} if current is None else current.pending
        self.assertEqual(len(pending), 0, 'a record was queued')
        store.flush()
        self.assertEqual(self.stored_records(), [], 'a record was kept')

    # -- rewrites --------------------------------------------------------

    def rewrite_identically(self, path):
        """The same bytes under a new inode and a new mtime -- what a
        rebuild that reproduces its artifact leaves behind."""
        before = os.stat(path)
        with open(path, 'rb') as handle:
            data = handle.read()
        temporary = f'{path}.rewritten'
        with open(temporary, 'wb') as handle:
            handle.write(data)
        os.replace(temporary, path)
        os.utime(path, ns=(before.st_atime_ns,
                           before.st_mtime_ns + 7 * 10 ** 9))
        after = os.stat(path)
        self.assertNotEqual(after.st_ino, before.st_ino)
        self.assertNotEqual(after.st_mtime_ns, before.st_mtime_ns)

    def rewrite_under_preserved_timestamp(self, path, data, same_size=True):
        """New content written in place, then the old mtime restored."""
        before = os.stat(path)
        if same_size:
            self.assertEqual(len(data), before.st_size,
                             'the scenario needs a same-size rewrite')
        with open(path, 'r+b') as handle:
            handle.write(data)
            handle.truncate()
        os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
        after = os.stat(path)
        self.assertEqual(after.st_mtime_ns, before.st_mtime_ns)
        if same_size:
            self.assertEqual(after.st_size, before.st_size)


class ServedAfterAFreshProcess(StoreTestCase):
    """Task 2.2: the tier's whole point."""

    def test_a_faceted_verdict_is_served_after_a_fresh_process(self):
        first = self.stl('first', box((2, 2, 2)))
        second = self.stl('second', box((2, 2, 2)))
        with self.counted() as computed:
            decided = test_module._intersection_stats(
                *self.faceted_pair(first, second, [1.5, 0, 0]))
        self.assertEqual(computed.count, 1)
        self.assertFalse(decided.is_empty)
        self.assertNotEqual(decided.volume, 0.0)

        self.fresh_process()
        with self.counted() as computed:
            served = test_module._intersection_stats(
                *self.faceted_pair(first, second, [1.5, 0, 0]))

        self.assertEqual(computed.count, 0,
                         'a decided faceted verdict was computed again')
        self.assertBitIdentical(served, decided)
        self.assertEqual(store.counters['served'], 1)

    def test_an_exact_verdict_is_served_after_a_fresh_process(self):
        first = self.brep('first')
        second = self.brep('second')
        with self.counted() as computed:
            decided = test_module._intersection_stats(
                *self.exact_pair(first, second, [0.5, 0, 0]))
        self.assertEqual(computed.count, 1)
        self.assertTrue(decided.exact)
        self.assertFalse(decided.is_empty)

        self.fresh_process()
        with self.counted() as computed, \
                patch.object(occt_engine, 'intersect_shapes',
                             side_effect=AssertionError('boolean ran')):
            served = test_module._intersection_stats(
                *self.exact_pair(first, second, [0.5, 0, 0]))

        self.assertEqual(computed.count, 0,
                         'a decided exact verdict was computed again')
        self.assertBitIdentical(served, decided)

    def test_the_in_process_memo_answers_before_the_store(self):
        first = self.stl('first', box((2, 2, 2)))
        second = self.stl('second', box((2, 2, 2)))
        pair = self.faceted_pair(first, second, [1.5, 0, 0])
        test_module._intersection_stats(*pair)
        self.fresh_process()
        pair = self.faceted_pair(first, second, [1.5, 0, 0])
        test_module._intersection_stats(*pair)
        with patch.object(store.Store, 'lookup',
                          side_effect=AssertionError('store consulted')):
            test_module._intersection_stats(*pair)
        self.assertEqual(store.counters['served'], 1)


class IdentifiedByContent(StoreTestCase):
    """Tasks 2.3 and 2.4: content, not the file's metadata, is the key."""

    def test_an_identical_rewrite_is_served(self):
        faceted_first = self.stl('first', box((2, 2, 2)))
        faceted_second = self.stl('second', box((2, 2, 2)))
        exact_first = self.brep('exact_first')
        exact_second = self.brep('exact_second')
        faceted = test_module._intersection_stats(
            *self.faceted_pair(faceted_first, faceted_second, [1.5, 0, 0]))
        exact = test_module._intersection_stats(
            *self.exact_pair(exact_first, exact_second, [0.5, 0, 0]))
        self.fresh_process()

        for path in (faceted_second, exact_second):
            self.rewrite_identically(path)
        with self.counted() as computed:
            served_faceted = test_module._intersection_stats(
                *self.faceted_pair(faceted_first, faceted_second,
                                   [1.5, 0, 0]))
            served_exact = test_module._intersection_stats(
                *self.exact_pair(exact_first, exact_second, [0.5, 0, 0]))

        self.assertEqual(computed.count, 0,
                         'an identically rebuilt artifact missed')
        self.assertBitIdentical(served_faceted, faceted)
        self.assertBitIdentical(served_exact, exact)

    def test_a_faceted_content_change_under_a_preserved_timestamp_recomputes(self):
        first = self.stl('first', box((2, 2, 2)))
        second = self.stl('second', box((2, 2, 2)))
        overlapping = test_module._intersection_stats(
            *self.faceted_pair(first, second, [1.5, 0, 0]))
        self.assertFalse(overlapping.is_empty)
        self.fresh_process()

        # A binary STL's size depends only on its face count: the same box
        # moved away is a same-size file with different geometry.
        moved = box((2, 2, 2))
        moved.apply_translation([5, 0, 0])
        replacement = os.path.join(self.scratch, 'moved.stl')
        moved.export(replacement)
        with open(replacement, 'rb') as handle:
            self.rewrite_under_preserved_timestamp(second, handle.read())

        with self.counted() as computed:
            after = test_module._intersection_stats(
                *self.faceted_pair(first, second, [1.5, 0, 0]))

        self.assertEqual(computed.count, 1,
                         'changed content was served its old verdict')
        self.assertTrue(after.is_empty,
                        'the verdict is not the new geometry\'s')

    def test_an_exact_content_change_under_a_preserved_timestamp_recomputes(self):
        first = self.brep('first')
        second = self.brep('second')
        overlapping = test_module._intersection_stats(
            *self.exact_pair(first, second, [0.5, 0, 0]))
        self.assertFalse(overlapping.is_empty)
        self.fresh_process()

        replacement = os.path.join(self.scratch, 'moved.brep')
        write_brep(cq.Workplane('XY').box(1, 1, 1).translate((5, 0, 0))
                   .val().wrapped, replacement, 1 * 10 ** 9)
        with open(replacement, 'rb') as handle:
            self.rewrite_under_preserved_timestamp(
                second, handle.read(), same_size=False)

        with self.counted() as computed:
            after = test_module._intersection_stats(
                *self.exact_pair(first, second, [0.5, 0, 0]))

        self.assertEqual(computed.count, 1,
                         'changed content was served its old verdict')
        self.assertTrue(after.is_empty,
                        'the verdict is not the new geometry\'s')


class MovedProject(StoreTestCase):
    """Task 2.5: nothing absolute is persisted."""

    def test_a_moved_project_is_served_and_no_path_is_persisted(self):
        names = {'faceted': ('first.stl', 'second.stl'),
                 'exact': ('exact_first.brep', 'exact_second.brep')}
        self.stl('first', box((2, 2, 2)))
        self.stl('second', box((2, 2, 2)))
        self.brep('exact_first')
        self.brep('exact_second')

        def ask(build_root):
            parts = os.path.join(build_root, 'parts')
            faceted = test_module._intersection_stats(*self.faceted_pair(
                *[os.path.join(parts, name) for name in names['faceted']],
                [1.5, 0, 0]))
            exact = test_module._intersection_stats(*self.exact_pair(
                *[os.path.join(parts, name) for name in names['exact']],
                [0.5, 0, 0]))
            return faceted, exact

        decided = ask(self.build_root)
        self.fresh_process()

        old_project, old_build_root = self.project, self.build_root
        new_project = os.path.join(self.scratch, 'moved', 'elsewhere')
        shutil.copytree(old_project, new_project)
        shutil.rmtree(old_project)
        new_build_root = os.path.join(new_project, '_build')
        os.environ['SOLID_BUILD_DIR'] = new_build_root

        with self.counted() as computed:
            served = ask(new_build_root)

        self.assertEqual(computed.count, 0, 'a moved project missed')
        for served_stats, decided_stats in zip(served, decided):
            self.assertBitIdentical(served_stats, decided_stats)

        store.flush()
        persisted = self.store_bytes(
            os.path.join(new_build_root, VERDICT_STORE_DIRECTORY))
        self.assertTrue(persisted)
        for path in (old_project, old_build_root, new_project,
                     new_build_root, self.scratch):
            for spelling in (os.fsencode(path), path.encode('utf-16-le')):
                self.assertNotIn(spelling, persisted,
                                 f'{path} was persisted')


class StampInvalidates(StoreTestCase):
    """Task 2.6: framework, kernel and platform changes start afresh."""

    def decide_and_keep(self, first, second):
        with self.counted() as computed:
            test_module._intersection_stats(
                *self.faceted_pair(first, second, [1.5, 0, 0]))
        self.fresh_process()
        return computed.count

    def test_every_stamp_component_invalidates(self):
        first = self.stl('first', box((2, 2, 2)))
        second = self.stl('second', box((2, 2, 2)))
        original_token = store._distribution_token

        def kernel_upgraded(distribution, module):
            if distribution == 'cadquery-ocp':
                return 'upgraded'
            return original_token(distribution, module)

        components = {
            'machinome.__version__': lambda: patch.object(
                machinome, '__version__', machinome.__version__ + '.next'),
            'package digest': lambda: patch.object(
                store, '_package_digest', return_value=b'\x07' * 32),
            'kernel version': lambda: patch.object(
                store, '_distribution_token', side_effect=kernel_upgraded),
            'platform': lambda: patch.object(
                store, '_platform_token', return_value='another-platform'),
        }
        for component, changed in components.items():
            with self.subTest(component=component):
                shutil.rmtree(self.store_directory, ignore_errors=True)
                self.fresh_process()
                self.assertEqual(self.decide_and_keep(first, second), 1)
                kept = self.segments()
                self.assertTrue(kept)
                self.assertEqual(self.decide_and_keep(first, second), 0,
                                 'the unchanged stamp did not serve')

                with changed():
                    self.fresh_process()
                    with self.counted() as computed:
                        test_module._intersection_stats(
                            *self.faceted_pair(first, second, [1.5, 0, 0]))
                    self.assertEqual(computed.count, 1,
                                     f'a changed {component} was served')
                    self.fresh_process()

                for path in kept:
                    self.assertTrue(os.path.exists(path),
                                    'a foreign-stamp segment was deleted '
                                    'before eviction')

    def test_computing_the_stamp_imports_no_kernel(self):
        result = probe('from machinome import _verdict_store as store\n'
                       'assert len(store.stamp()) == 32\n').check()
        for module in KERNEL_MODULES:
            self.assertFalse(result.imported(module),
                             f'computing the stamp imported {module}')


class QuantumInThePersistedKey(StoreTestCase):
    """Task 2.7: a verdict kept at quantum q is not served at 2q, even for
    a placement whose integer cells coincide."""

    Q = 3.0

    def test_the_quantum_is_part_of_the_persisted_key(self):
        at_q = np.eye(4)
        at_q[0, 3] = self.Q
        at_double_q = np.eye(4)
        at_double_q[0, 3] = 2 * self.Q
        identity = ('artifact', 'stl', b'\x01' * 32)

        self.set_policy(quantum=self.Q)
        key_q = test_module._verdict_key('a', np.eye(4), 'b', at_q, 'faceted')
        self.set_policy(quantum=2 * self.Q)
        key_double_q = test_module._verdict_key(
            'a', np.eye(4), 'b', at_double_q, 'faceted')
        self.assertEqual(key_q[4], key_double_q[4],
                         'the cells do not coincide; this proves nothing')

        self.assertNotEqual(
            store.persisted_key('faceted', self.Q, identity, identity,
                                key_q[4], ENGINE),
            store.persisted_key('faceted', 2 * self.Q, identity, identity,
                                key_double_q[4], ENGINE))

    def test_a_verdict_kept_at_one_quantum_is_not_served_at_another(self):
        first = self.stl('first', box((2, 2, 2)))
        second = self.stl('second', box((2, 2, 2)))
        self.set_policy(quantum=self.Q)
        test_module._intersection_stats(
            *self.faceted_pair(first, second, [self.Q, 0, 0]))
        self.fresh_process()

        self.set_policy(quantum=2 * self.Q)
        with self.counted() as computed:
            test_module._intersection_stats(
                *self.faceted_pair(first, second, [2 * self.Q, 0, 0]))
        self.assertEqual(computed.count, 1,
                         'a verdict crossed from one quantum to another')

        # The control: the same quantum and placement is served.
        self.fresh_process()
        self.set_policy(quantum=self.Q)
        with self.counted() as computed:
            test_module._intersection_stats(
                *self.faceted_pair(first, second, [self.Q, 0, 0]))
        self.assertEqual(computed.count, 0)


class FlushContactSurvivesTheStore(StoreTestCase):
    """Task 2.8: ADR-025/029's non-empty 0.0 mm³ comes back bit for bit."""

    def test_a_served_flush_contact_still_fouls(self):
        path = self.stl('box', box((2, 2, 2)))
        decided = test_module._intersection_stats(
            *self.faceted_pair(path, path, [2, 0, 0]))
        self.assertFalse(decided.is_empty,
                         'the fixture is no longer a flush contact')
        self.assertEqual(bits(decided.volume), bits(0.0))
        self.fresh_process()

        with self.counted() as computed:
            first, second = self.faceted_pair(path, path, [2, 0, 0])
            served = test_module._intersection_stats(first, second)
            with self.assertRaisesRegex(AssertionError,
                                        r'intersection volume 0\.0'):
                asserter.assertNotIntersecting(first, second)

        self.assertEqual(computed.count, 0)
        self.assertFalse(served.is_empty)
        self.assertEqual(bits(served.volume), bits(0.0))


class ExactShapeWithoutIdentity(ExactFakeNode):
    """A shape composed for one comparison: no `shape_identity`."""

    def shape(self):
        return cq.Workplane('XY').box(1, 1, 1).val().wrapped


class NothingKeptForTheUncacheable(StoreTestCase):
    """Task 2.9: the store keeps nothing the memo does not key, nothing
    whose computation raised, and nothing whose artifact changed after its
    geometry was read."""

    def test_a_mesh_only_pair_is_not_kept(self):
        moved = box((2, 2, 2))
        moved.apply_translation([1.5, 0, 0])
        test_module._intersection_stats(
            MeshOnlyNode('First', box((2, 2, 2))),
            MeshOnlyNode('Second', moved))
        self.assertNothingKept()

    def test_the_virtual_floor_is_not_kept(self):
        path = self.stl('base', box((2, 2, 2)))
        assembly = Assembly('root', [RigidNode('base', path)])
        solids = test_module._placed_assembly_solids(assembly)
        floor = test_module._virtual_floor(
            solids, np.array([0.0, 0.0, -1.0]), 1.0)
        test_module._placed_intersection(floor, solids[0])
        test_module._placed_intersection(floor, solids[0])
        self.assertNothingKept()

    def test_a_non_finite_relative_matrix_is_not_kept(self):
        path = self.stl('box', box((2, 2, 2)))
        identity = test_module._geometry_identity(path)
        non_finite = np.eye(4)
        non_finite[0, 3] = np.nan
        key = test_module._verdict_key(identity, np.eye(4), identity,
                                       non_finite, 'faceted')
        self.assertIsNone(key)
        test_module._memoized(
            key, lambda: test_module.IntersectionStats(True, 0.0, False))
        self.assertNothingKept()

    def test_a_computation_that_raises_is_not_kept(self):
        first = self.brep('first')
        second = self.brep('second')
        for error in (RuntimeError('OCCT failed'),
                      ExactCommonInconsistency('false-empty common')):
            with self.subTest(error=type(error).__name__):
                with patch.object(occt_engine, 'intersect_shapes',
                                  side_effect=error):
                    with self.assertRaises(type(error)):
                        test_module._intersection_stats(
                            *self.exact_pair(first, second, [0.5, 0, 0]))
                self.assertNothingKept()

    def test_an_exact_shape_without_identity_is_not_kept(self):
        first = ExactShapeWithoutIdentity('First', None)
        second = ExactShapeWithoutIdentity('Second', None)
        second.operations.append(Translation([0.5, 0, 0], second))
        test_module._intersection_stats(first, second)
        test_module._intersection_stats(first, second)
        self.assertNothingKept()

    def test_a_brep_rewritten_after_it_was_loaded_is_not_kept(self):
        first = self.brep('first')
        second = self.brep('second')
        pair = self.exact_pair(first, second, [0.5, 0, 0])
        loaded = pair[1].shape()

        # Different content under the key `cached_shape` takes from one
        # `stat`, so the loaded shape is still the one served: the digest
        # the store would read now names bytes the compared geometry did
        # not come from. A rename changes that key (ADR-164), so the one
        # way left to serve a loaded shape for replaced bytes -- an
        # in-place rewrite within one timestamp tick, equal in size and
        # mtime -- is held here by answering the key's `stat` as it was.
        replacement = os.path.join(self.scratch, 'other.brep')
        write_brep(cq.Workplane('XY').box(2, 2, 2).val().wrapped,
                   replacement, 1 * 10 ** 9)
        before = os.stat(second)
        os.replace(replacement, second)
        os.utime(second, ns=(before.st_atime_ns, before.st_mtime_ns))
        metadata = exact_cache._metadata
        held = (before.st_dev, before.st_ino, before.st_size,
                before.st_mtime_ns, before.st_ctime_ns)
        with patch.object(exact_cache, '_metadata', side_effect=lambda path:
                          held if path == second else metadata(path)):
            self.assertIs(pair[1].shape(), loaded)

            with self.counted() as computed:
                test_module._intersection_stats(*pair)
        self.assertEqual(computed.count, 1)
        self.assertNothingKept()

    def test_an_stl_rewritten_after_its_manifold_was_built_is_not_kept(self):
        first = self.stl('first', box((2, 2, 2)))
        second = self.stl('second', box((2, 2, 2)))
        other = os.path.join(self.scratch, 'other.stl')
        box((3, 3, 3)).export(other)
        real = test_module._cached_mesh_solid

        def built_then_rewritten(stl_file, *arguments, **keywords):
            built = real(stl_file, *arguments, **keywords)
            if stl_file == second and os.path.exists(other):
                before = os.stat(second)
                os.replace(other, second)
                os.utime(second, ns=(before.st_atime_ns,
                                     before.st_mtime_ns))
            return built

        with patch.object(test_module, '_cached_mesh_solid',
                          side_effect=built_then_rewritten):
            test_module._intersection_stats(
                *self.faceted_pair(first, second, [1.5, 0, 0]))
        self.assertFalse(os.path.exists(other), 'the rewrite never ran')
        self.assertNothingKept()


class DigestMemoKeysOnTheFullObservation(StoreTestCase):
    """Task 2.10: `_atomic_export` stamps an artifact with its SOURCE's
    mtime, so a rebuild can reproduce the old mtime and size with new
    bytes. A digest memoised on (path, mtime_ns, size) would then serve
    the old content's digest."""

    def test_a_same_size_rewrite_with_its_mtime_restored_is_a_new_digest(self):
        path = self.stl('box', box((2, 2, 2)))
        before = observe_artifact(path)
        first = store.artifact_digest(path, before)

        moved = box((2, 2, 2))
        moved.apply_translation([5, 0, 0])
        replacement = os.path.join(self.scratch, 'moved.stl')
        moved.export(replacement)
        os.replace(replacement, path)
        os.utime(path, ns=(before.mtime_ns, before.mtime_ns))
        after = observe_artifact(path)
        self.assertEqual((after.realpath, after.mtime_ns, after.size),
                         (before.realpath, before.mtime_ns, before.size),
                         'this scenario needs the weak key to collide')

        second = store.artifact_digest(path, after)
        with open(path, 'rb') as handle:
            expected = hashlib.sha256(handle.read()).digest()
        self.assertNotEqual(first, second)
        self.assertEqual(second, expected)
        # The older observation's entry was evicted with it.
        self.assertEqual([observation for observation in store._digests
                          if observation.realpath == after.realpath],
                         [after])

    def test_a_digest_for_bytes_no_longer_there_is_refused(self):
        path = self.stl('box', box((2, 2, 2)))
        before = observe_artifact(path)
        self.rewrite_identically(path)
        self.assertIsNone(store.artifact_digest(path, before))


class CorruptStoreIsIgnored(StoreTestCase):
    """Task 2.11: every uncertainty resolves to a computed verdict."""

    def decide(self, first, second):
        return test_module._intersection_stats(
            *self.faceted_pair(first, second, [1.5, 0, 0]))

    def corrupt_cases(self):
        stamp = store.stamp()

        def truncated(path, data):
            return data[:len(data) - 5]

        def random_bytes(path, data):
            return os.urandom(len(data))

        def wrong_magic(path, data):
            return b'NOTVERDS' + data[8:]

        def foreign_version(path, data):
            header = bytearray(data[:store.HEADER.size])
            struct.pack_into('<I', header, 8, store.FORMAT_VERSION + 1)
            body = bytes(header) + data[store.HEADER.size:-32]
            return body + hashlib.sha256(body).digest()

        def checksum_mismatch(path, data):
            corrupted = bytearray(data)
            corrupted[store.HEADER.size] ^= 0xFF
            return bytes(corrupted)

        self.assertEqual(len(stamp), 32)
        return {'truncated': truncated, 'random bytes': random_bytes,
                'wrong magic': wrong_magic,
                'foreign format version': foreign_version,
                'checksum mismatch': checksum_mismatch}

    def test_a_corrupt_segment_is_ignored_and_later_deleted(self):
        first = self.stl('first', box((2, 2, 2)))
        second = self.stl('second', box((2, 2, 2)))
        for case, corrupt in self.corrupt_cases().items():
            with self.subTest(case=case):
                shutil.rmtree(self.store_directory, ignore_errors=True)
                self.fresh_process()
                decided = self.decide(first, second)
                self.fresh_process()
                (segment,) = self.segments()
                with open(segment, 'rb') as handle:
                    data = handle.read()
                with open(segment, 'wb') as handle:
                    handle.write(corrupt(segment, data))
                stray = os.path.join(self.store_directory, 'notes.txt')
                with open(stray, 'w') as handle:
                    handle.write('not a segment')

                out, err = io.StringIO(), io.StringIO()
                with self.counted() as computed, redirect_stdout(out), \
                        redirect_stderr(err):
                    after = self.decide(first, second)
                self.assertEqual(computed.count, 1,
                                 f'a {case} segment was served')
                self.assertBitIdentical(after, decided)
                self.assertEqual((out.getvalue(), err.getvalue()), ('', ''))

                self.fresh_process()
                with patch.object(store, 'SEGMENT_LIMIT', 0):
                    store.Store(self.build_root).load()
                self.assertFalse(os.path.exists(segment),
                                 f'the {case} segment survived compaction')
                self.assertTrue(os.path.exists(stray),
                                'compaction deleted a file that is not '
                                'the store\'s own')

    def test_a_store_that_is_a_regular_file_is_ignored(self):
        first = self.stl('first', box((2, 2, 2)))
        second = self.stl('second', box((2, 2, 2)))
        with open(self.store_directory, 'w') as handle:
            handle.write('not a directory')
        out, err = io.StringIO(), io.StringIO()
        with self.counted() as computed, redirect_stdout(out), \
                redirect_stderr(err):
            first_ask = self.decide(first, second)
            store.flush()
        self.fresh_process()
        with self.counted() as again:
            second_ask = self.decide(first, second)
            store.flush()
        self.assertEqual((computed.count, again.count), (1, 1))
        self.assertBitIdentical(second_ask, first_ask)
        self.assertEqual((out.getvalue(), err.getvalue()), ('', ''))
        with open(self.store_directory) as handle:
            self.assertEqual(handle.read(), 'not a directory')

    @skipIf(os.geteuid() == 0, 'root ignores directory permissions')
    def test_a_read_only_store_is_ignored(self):
        first = self.stl('first', box((2, 2, 2)))
        second = self.stl('second', box((2, 2, 2)))
        os.makedirs(self.store_directory)
        os.chmod(self.store_directory, stat.S_IRUSR | stat.S_IXUSR)
        self.addCleanup(os.chmod, self.store_directory, stat.S_IRWXU)
        out, err = io.StringIO(), io.StringIO()
        with self.counted() as computed, redirect_stdout(out), \
                redirect_stderr(err):
            decided = self.decide(first, second)
            store.flush()
            repeated = self.decide(first, second)
            store.flush()
        self.assertEqual(computed.count, 1)
        self.assertBitIdentical(repeated, decided)
        self.assertEqual(os.listdir(self.store_directory), [])
        self.assertEqual((out.getvalue(), err.getvalue()), ('', ''))


def spawn():
    return multiprocessing.get_context('spawn')


class ConcurrentProcesses(StoreTestCase):
    """Task 2.12: two writers lose nothing, and neither does a reader
    whose load overlaps a compaction. Synthetic records only: this machine
    must never run two CAD processes at once."""

    def keys(self, records):
        return {record[0] for record in records}

    def test_two_writers_and_a_compactor_lose_nothing(self):
        context = spawn()
        barrier = context.Barrier(3)
        processes = [
            context.Process(target=workers.write_behind_barrier,
                            args=(self.build_root, 'left', 6, 25, barrier)),
            context.Process(target=workers.write_behind_barrier,
                            args=(self.build_root, 'right', 6, 25, barrier)),
            context.Process(target=workers.compact_behind_barrier,
                            args=(self.build_root, 4, barrier)),
        ]
        for process in processes:
            process.start()
        for process in processes:
            process.join(120)
        self.assertEqual([process.exitcode for process in processes],
                         [0, 0, 0])

        expected = set()
        for seed in ('left', 'right'):
            for flush in range(6):
                expected |= self.keys(workers.synthetic_records(
                    f'{seed}:{flush}', 25))
        reader = store.Store(self.build_root)
        reader.load()
        self.assertIsNone(reader.failed)
        self.assertEqual(set(reader.index), expected)

    def prepared_store(self, segments=5, per_segment=10):
        directory = self.store_directory
        os.makedirs(directory)
        written = []
        for segment in range(segments):
            records = workers.synthetic_records(f'seed:{segment}',
                                                per_segment)
            store.write_segment(directory, records)
            written.extend(records)
        return written

    def compact_in_another_process(self):
        with spawn().Pool(1) as pool:
            return pool.apply(workers.compact, (self.build_root,))

    def test_a_reader_overlapping_a_compaction_holds_the_union(self):
        written = self.prepared_store()
        real = store._list_directory
        listings = []

        def overlapped(directory):
            names = real(directory)
            listings.append(names)
            if len(listings) == 1:
                # After the reader's first listing and before it opens any
                # listed segment, another process merges them all and
                # deletes the inputs.
                self.compact_in_another_process()
            return names

        reader = store.Store(self.build_root)
        with patch.object(store, '_list_directory', side_effect=overlapped):
            reader.load()

        self.assertIsNone(reader.failed)
        self.assertEqual(len(listings), 2, 'the reader never re-listed')
        self.assertEqual(set(reader.index), self.keys(written))

    def test_a_merged_segment_vanishing_again_costs_misses_not_errors(self):
        written = self.prepared_store()
        real = store._list_directory
        listings = []

        def overlapped_twice(directory):
            names = real(directory)
            listings.append(names)
            if len(listings) == 1:
                self.compact_in_another_process()
            elif len(listings) == 2:
                for name in set(names) - set(listings[0]):
                    if store.SEGMENT_NAME.match(name):
                        os.remove(os.path.join(directory, name))
            return names

        reader = store.Store(self.build_root)
        with patch.object(store, '_list_directory',
                          side_effect=overlapped_twice):
            reader.load()

        self.assertIsNone(reader.failed)
        self.assertEqual(len(listings), 2, 'a load re-lists at most once')
        self.assertEqual(reader.index, {})
        for key in self.keys(written):
            self.assertIsNone(reader.lookup(key))


class BoundAndEviction(StoreTestCase):
    """Task 2.13, with the record limit patched small."""

    LIMIT = 40

    def setUp(self):
        super().setUp()
        os.makedirs(self.store_directory)
        limit = patch.object(store, 'RECORD_LIMIT', self.LIMIT)
        limit.start()
        self.addCleanup(limit.stop)

    def write(self, seed, count, last_use, stamp=None, age=None):
        records = workers.synthetic_records(seed, count, last_use)
        path = store.write_segment(self.store_directory, records, stamp)
        if age is not None:
            moment = time.time() - age
            os.utime(path, (moment, moment))
        return path, records

    def test_foreign_stamps_go_first_oldest_first(self):
        foreign = b'\x0f' * 32
        oldest, _ = self.write('old', 15, 100, foreign, age=300)
        middle, _ = self.write('mid', 15, 100, foreign, age=200)
        newest, _ = self.write('new', 15, 100, foreign, age=100)
        _, current = self.write('current', 10, 100)

        loader = store.Store(self.build_root)
        loader.load()

        # 55 records against a limit of 40: foreign segments are evicted,
        # oldest first, until three quarters of the limit (30) remain.
        self.assertFalse(os.path.exists(oldest))
        self.assertFalse(os.path.exists(middle))
        self.assertTrue(os.path.exists(newest))
        self.assertEqual(set(loader.index),
                         {record[0] for record in current})

    def test_then_the_least_recently_used_current_records_go(self):
        _, older = self.write('older', 25, 1000)
        _, newer = self.write('newer', 25, 5000)

        loader = store.Store(self.build_root)
        loader.load()

        kept = int(self.LIMIT * 0.75)
        self.assertEqual(len(loader.index), kept)
        by_age = sorted(older + newer, key=lambda record: record[4])
        self.assertEqual(set(loader.index),
                         {record[0] for record in by_age[-kept:]})
        self.assertEqual(len(self.stored_records()), kept)

    def test_a_touched_record_outlives_an_untouched_older_one(self):
        touched = workers.synthetic_records('touched', 1, 100)
        untouched = workers.synthetic_records('untouched', 1, 200)
        filler = workers.synthetic_records('filler', self.LIMIT - 2, 300)
        store.write_segment(self.store_directory,
                            touched + untouched + filler)

        user = store.Store(self.build_root)
        user.load()
        self.assertIsNotNone(user.lookup(touched[0][0]))
        user.flush()
        # One more record puts the store over its limit.
        store.write_segment(self.store_directory,
                            workers.synthetic_records('extra', 2, 400))

        loader = store.Store(self.build_root)
        loader.load()
        self.assertIn(touched[0][0], loader.index)
        self.assertNotIn(untouched[0][0], loader.index)

    def test_compaction_starts_above_the_segment_limit(self):
        stray = os.path.join(self.store_directory, 'README')
        with open(stray, 'w') as handle:
            handle.write('not a segment')
        foreign, _ = self.write('foreign', 1, 100, b'\x0e' * 32)
        with patch.object(store, 'RECORD_LIMIT', 10_000):
            inputs = [self.write(f'segment-{index}', 1, 100)[0]
                      for index in range(store.SEGMENT_LIMIT)]
            loader = store.Store(self.build_root)
            loader.load()
            self.assertTrue(all(os.path.exists(path) for path in inputs),
                            'compaction ran at the segment limit itself')

            inputs.append(self.write('one-more', 1, 100)[0])
            loader = store.Store(self.build_root)
            loader.load()

        self.assertFalse(any(os.path.exists(path) for path in inputs))
        current = [path for path in self.segments()
                   if path != foreign]
        self.assertEqual(len(current), 1)
        self.assertEqual(len(store.read_segment(current[0])),
                         store.SEGMENT_LIMIT + 1)
        self.assertTrue(os.path.exists(foreign))
        self.assertTrue(os.path.exists(stray))

    def test_an_old_temporary_is_removed_and_a_fresh_one_kept(self):
        self.write('current', 1, 100)
        name = store.segment_name(store.stamp())
        old = os.path.join(self.store_directory, f'.{name}.tmp')
        fresh = os.path.join(self.store_directory,
                             f'.{store.segment_name(store.stamp())}.tmp')
        for path, age in ((old, 2 * 3600), (fresh, 60)):
            with open(path, 'wb') as handle:
                handle.write(b'partial')
            moment = time.time() - age
            os.utime(path, (moment, moment))
        with patch.object(store, 'SEGMENT_LIMIT', 0):
            store.Store(self.build_root).load()
        self.assertFalse(os.path.exists(old))
        self.assertTrue(os.path.exists(fresh))


class Location(StoreTestCase):
    """Task 2.14: where the store lives, and who shares it."""

    def test_no_project_and_no_build_directory_means_no_store(self):
        os.environ.pop('SOLID_BUILD_DIR')
        nowhere = os.path.join(self.scratch, 'nowhere')
        os.makedirs(nowhere)
        path = os.path.join(nowhere, 'box.stl')
        box((2, 2, 2)).export(path)
        with chdir(nowhere):
            from machinome.manifest import ProjectManifestError, project_root
            with self.assertRaises(ProjectManifestError):
                project_root()
            self.assertIsNone(store.resolve_root())
            with self.counted() as computed:
                test_module._intersection_stats(
                    *self.faceted_pair(path, path, [1.5, 0, 0]))
                test_module._intersection_stats(
                    *self.faceted_pair(path, path, [1.5, 0, 0]))
            store.flush()
        self.assertEqual(computed.count, 1, 'the in-process memo is gone')
        self.assertEqual(sorted(os.listdir(nowhere)), ['box.stl'])
        for folder, directories, _ in os.walk(self.scratch):
            self.assertNotIn(VERDICT_STORE_DIRECTORY, directories)

    def test_an_absolute_build_directory_holds_the_store(self):
        first = self.stl('first', box((2, 2, 2)))
        test_module._intersection_stats(
            *self.faceted_pair(first, first, [1.5, 0, 0]))
        store.flush()
        self.assertEqual(store.resolve_root(), self.build_root)
        self.assertEqual(len(self.segments()), 1)

    def test_a_manifest_project_keeps_its_store_under_its_build_root(self):
        os.environ.pop('SOLID_BUILD_DIR')
        with open(os.path.join(self.project, 'pyproject.toml'), 'w') as handle:
            handle.write('[tool.machinome]\nmodel = "part:Part"\n')
        inside = os.path.join(self.project, 'deep', 'er')
        os.makedirs(inside)
        with chdir(inside):
            self.assertEqual(store.resolve_root(), self.build_root)


class OffMeansOff(StoreTestCase):
    """Task 4.5: with the switch off, the store is neither read nor written
    and a store left on disk is untouched."""

    def test_a_run_with_the_store_off_touches_nothing(self):
        first = self.stl('first', box((2, 2, 2)))
        second = self.stl('second', box((2, 2, 2)))
        test_module._intersection_stats(
            *self.faceted_pair(first, second, [1.5, 0, 0]))
        self.fresh_process()

        def listing():
            return {name: os.stat(os.path.join(self.store_directory,
                                               name)).st_mtime_ns
                    for name in os.listdir(self.store_directory)}

        before = listing()
        self.set_policy(verdict_store=False)
        with self.counted() as computed, \
                patch.object(store, '_list_directory',
                             side_effect=AssertionError('store read')), \
                patch.object(store, 'resolve_root',
                             side_effect=AssertionError('store located')):
            test_module._intersection_stats(
                *self.faceted_pair(first, second, [1.5, 0, 0]))
            test_module._intersection_stats(
                *self.faceted_pair(first, second, [0.5, 0, 0]))
            store.flush()
        self.assertEqual(computed.count, 2)
        self.assertEqual(listing(), before)

    def test_a_run_with_the_store_off_creates_nothing(self):
        first = self.stl('first', box((2, 2, 2)))
        self.set_policy(verdict_store=False)
        test_module._intersection_stats(
            *self.faceted_pair(first, first, [1.5, 0, 0]))
        store.flush()
        self.assertFalse(os.path.exists(self.store_directory))


PAIR = """\
import cadquery as cq

from machinome.node import CadQueryNode


class Peg(CadQueryNode):

    def render(self):
        return cq.Workplane('XY').box(2, 2, 6)


class Socket(CadQueryNode):

    def render(self):
        return cq.Workplane('XY').box(4, 4, 4)
"""

PAIRED_CLOCK = """\
from machinome.node import AssemblyNode

from ..pair import Peg, Socket


class {klass}(AssemblyNode):

    def __init__(self):
        self.peg = Peg()
        self.socket = Socket()
        super().__init__()
        self.peg.translate([0, 0, 3])

    def render(self):
        return [self.peg, self.socket]
"""

PAIRED_COMPANION = """\
from machinome.test import TestCase

from .clock import {klass}


class ClockTest(TestCase):
    node = {klass}

    def test_the_peg_enters_the_socket(self):
        self.assertIntersecting(self.node.peg, self.node.socket)
"""


class DeclaredModelsShareOneStore(NamedProjectTest):
    """Task 2.14: a project has one store. Two declared models that build
    one identical pair at one relative placement ask one question, so a
    verdict kept by one model's run is served to the other's."""

    def setUp(self):
        super().setUp()
        switched_on = patch.object(store, '_suspended', False)
        switched_on.start()
        self.addCleanup(switched_on.stop)
        forget_process_state()
        self.addCleanup(forget_process_state)
        self.addCleanup(test_module.set_comparison_policy, None)
        package_dir = os.path.join(self.root, self.package)
        with open(os.path.join(package_dir, 'pair.py'), 'w') as source:
            source.write(PAIR)
        for name, klass in (('a_clock', 'AClock'), ('b_clock', 'BClock')):
            model_dir = os.path.join(package_dir, name)
            with open(os.path.join(model_dir, 'clock.py'), 'w') as source:
                source.write(PAIRED_CLOCK.format(klass=klass))
            with open(os.path.join(model_dir, 'test_clock.py'),
                      'w') as source:
                source.write(PAIRED_COMPANION.format(klass=klass))
        self.forget_project()

    def fresh_process(self):
        store.flush()
        forget_process_state()
        self.forget_project()
        unanchor_build_dir()
        os.environ.pop('SOLID_BUILD_DIR', None)

    def run_tests(self, **arguments):
        from machinome.manager.test import Test
        namespace = dict(path=None, set=[], all=False, failfast=False,
                         verdict_store=True)
        namespace.update(arguments)
        stdout = io.StringIO()
        code = None
        with patch.object(test_module, '_exact_verdict',
                          wraps=test_module._exact_verdict) as exact, \
                patch.object(test_module, '_faceted_verdict',
                             wraps=test_module._faceted_verdict) as faceted, \
                chdir(self.root), redirect_stdout(stdout), \
                redirect_stderr(io.StringIO()):
            try:
                Test().handle(Namespace(**namespace))
            except SystemExit as stop:
                code = stop.code
        self.assertIsNone(code, stdout.getvalue())
        return exact.call_count + faceted.call_count, stdout.getvalue()

    def pair_artifacts(self, model):
        found = {}
        directory = os.path.join(self.build_root, model)
        for folder, _, names in os.walk(directory):
            for name in names:
                if name.endswith('.brep') and ('Peg' in name
                                               or 'Socket' in name):
                    with open(os.path.join(folder, name), 'rb') as handle:
                        found[name] = handle.read()
        return found

    def test_a_verdict_kept_by_one_model_is_served_to_another(self):
        self.publish(self.reference('a_clock'),
                     os.path.join(self.build_root, 'a_clock'))
        self.publish(self.reference('b_clock'),
                     os.path.join(self.build_root, 'b_clock'))
        self.fresh_process()
        a_pair = self.pair_artifacts('a_clock')
        self.assertEqual(len(a_pair), 2, a_pair.keys())
        self.assertEqual(a_pair, self.pair_artifacts('b_clock'),
                         'the premise: both models build the pair to '
                         'byte-identical artifacts')

        computed, _ = self.run_tests(path='a_clock')
        self.assertEqual(computed, 1)
        self.fresh_process()

        computed, output = self.run_tests(path='b_clock')
        self.assertEqual(computed, 0,
                         'model b computed a question model a decided')
        self.assertEqual(store.counters['served'], 1)
        self.assertIn('1 passed', output)
        self.fresh_process()

        computed, output = self.run_tests(all=True)
        self.assertEqual(computed, 0, '--all computed a kept question')
        self.assertIn('2 passed', output)

        self.assertTrue(os.path.isdir(os.path.join(
            self.build_root, VERDICT_STORE_DIRECTORY)))
        for model in ('a_clock', 'b_clock'):
            self.assertFalse(os.path.exists(os.path.join(
                self.build_root, model, VERDICT_STORE_DIRECTORY)),
                f'{model} kept a store of its own')


class MeshEngineIdentityBindsFacetedVerdicts(StoreTestCase):
    """OpenSpec change `mesh-engine`, design.md Decision 9: the mesh
    engine's identity leaves the process stamp for the key of the verdicts
    it decides. A faceted verdict is bound to the name and version the
    resolved engine reports of itself; an exact one is bound to no mesh
    engine at all, so computing the stamp never resolves it."""

    def test_the_stamp_names_no_mesh_engine(self):
        self.assertNotIn('manifold3d',
                         [distribution for distribution, _ in store.KERNELS])

    def test_a_mesh_engine_upgrade_recomputes_faceted_and_serves_exact(self):
        first_stl = self.stl('first', box((2, 2, 2)))
        second_stl = self.stl('second', box((2, 2, 2)))
        first_brep = self.brep('first')
        second_brep = self.brep('second')

        def ask():
            return (test_module._intersection_stats(*self.faceted_pair(
                        first_stl, second_stl, [1.5, 0, 0])),
                    test_module._intersection_stats(*self.exact_pair(
                        first_brep, second_brep, [0.5, 0, 0])))

        with self.counted() as computed:
            decided = ask()
        self.assertEqual(computed.count, 2)
        self.fresh_process()

        with patch('machinome.manifold.engine.identity',
                   return_value=('manifold3d', 'another version')), \
                self.counted() as computed:
            faceted, exact = ask()

        self.assertEqual(computed.mocks[1].call_count, 1,
                         'a faceted verdict kept under another mesh engine '
                         'version was served')
        self.assertEqual(computed.mocks[0].call_count, 0,
                         'an exact verdict was computed again for a mesh '
                         'engine upgrade')
        self.assertBitIdentical(faceted, decided[0])
        self.assertBitIdentical(exact, decided[1])

    def faceted_key(self):
        first = self.faceted('First', self.stl('first', box((2, 2, 2))))
        second = self.faceted('Second', self.stl('second', box((2, 2, 2))),
                              [1.5, 0, 0])
        _, _, first_matrix, first_identity = test_module._fast_geometry(first)
        _, _, second_matrix, second_identity = test_module._fast_geometry(
            second)
        key = test_module._verdict_key(first_identity, first_matrix,
                                       second_identity, second_matrix,
                                       'faceted')
        self.assertIsNotNone(test_module._persisted_key(key),
                             'the fixture key is not persistent at all')
        return key

    def test_without_a_mesh_engine_a_faceted_key_is_not_persisted(self):
        key = self.faceted_key()

        with patch.object(test_module, 'mesh_engine', return_value=None):
            self.assertIsNone(test_module._persisted_key(key))

    def test_an_engine_reporting_no_version_keeps_nothing(self):
        key = self.faceted_key()

        with patch('machinome.manifold.engine.identity',
                   return_value=('manifold3d', None)):
            self.assertIsNone(test_module._persisted_key(key))
