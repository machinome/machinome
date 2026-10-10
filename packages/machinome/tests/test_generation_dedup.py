# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Generation-local SCAD work and compare-before-replace publication.

The OpenSCAD node family's writer (`machinome.node.openscad.writer`)
publishes a node's `.scad` through `currency.publish_text`, reusing within one
source generation the text already published for the same full source
identity of a rigid node, which the generation records
(`has_published`, `remember_published`). Since `openscad-out` every
publication is immediate: ADR-086's assembly-phase coalescing went with its
one producer, and the assembly phase checkpoints as every phase does.
"""

import os
import tempfile
from types import SimpleNamespace
from unittest import TestCase, mock

from solid2 import cube

from machinome import currency
from machinome.node.solid2 import Solid2Node
from machinome.node.assembly import AssemblyNode
from machinome.node.openscad import writer
from machinome.source_generation import (
    SourceCensus, SourceGeneration,
)


class RepeatedBlock(Solid2Node):
    renders = 0

    def render(self):
        type(self).renders += 1
        return cube(4)


class ComposedBindingDependentAssembly(AssemblyNode):
    """Assembly instances whose child placement is not in artifact identity."""

    def render(self):
        return [self.part]


def desired(path, code, *, rigid=False, flexible=False, digest='digest',
            fingerprint='fingerprint', mtime_ns=1_700_000_000_123_456_789):
    """A stand-in the writer publishes: its `.scad` at `path`, its text
    `code`, keeping no artifact."""
    node = SimpleNamespace(
        basepath=path[:-len('.scad')], scad_code=code, mtime_ns=mtime_ns,
        mtime=mtime_ns / 1e9, source_digest=digest,
        source_fingerprint=fingerprint, rigid=rigid, flexible=flexible)
    node.kept_artifacts = lambda: ()
    return node


def publish(node):
    """The writer's publication of a stand-in's own text."""
    writer.generate_scad(node, lambda: node.scad_code)


class GenerationScadDedupTest(TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = self.temp.name

    def test_repeated_instances_render_user_code_but_generate_base_scad_once(self):
        with mock.patch.dict(os.environ, {'SOLID_BUILD_DIR': self.root}):
            first = RepeatedBlock().translate([1, 0, 0])
            second = RepeatedBlock().translate([2, 0, 0])
        self.assertEqual(first.scad_file, second.scad_file)
        RepeatedBlock.renders = 0

        # The SCAD text is the OpenSCAD writer's: count what is asked of it.
        with SourceGeneration(self.root) as generation, generation.phase(
                first.files | second.files, label='assembly'), \
                mock.patch.object(writer, 'scad_text',
                                  wraps=writer.scad_text) as generate:
            first_assembled = first.assemble()
            second_assembled = second.assemble()

        self.assertEqual(RepeatedBlock.renders, 2)
        self.assertEqual(generate.call_count, 1)
        self.assertNotEqual(writer.scad_text(first_assembled),
                            writer.scad_text(second_assembled))

    def test_audit_scale_repeated_instances_still_generate_one_base_scad(self):
        with mock.patch.dict(os.environ, {'SOLID_BUILD_DIR': self.root}):
            nodes = [RepeatedBlock().translate([index, 0, 0])
                     for index in range(59)]
        files = set().union(*(node.files for node in nodes))
        RepeatedBlock.renders = 0

        with SourceGeneration(self.root) as generation, generation.phase(
                files, label='assembly'), mock.patch.object(
                    writer, 'scad_text', wraps=writer.scad_text) as generate:
            assembled = [node.assemble() for node in nodes]

        self.assertEqual(RepeatedBlock.renders, 59)
        self.assertEqual(generate.call_count, 1)
        self.assertEqual(len({writer.scad_text(model)
                              for model in assembled}), 59)

    def test_same_path_with_different_full_source_identity_is_not_reused(self):
        path = os.path.join(self.root, 'shared.scad')
        first = desired(path, 'cube(1);', rigid=True, mtime_ns=10,
                        digest='digest-one', fingerprint='fingerprint-one')
        second = desired(path, 'cube(2);', rigid=True, mtime_ns=10,
                         digest='digest-two', fingerprint='fingerprint-two')

        with SourceGeneration(self.root), mock.patch.object(
                currency, 'publish_text') as write:
            publish(first)
            publish(second)

        self.assertEqual(write.call_count, 2)

    def test_alternating_full_identities_follow_current_artifact(self):
        path = os.path.join(self.root, 'shared.scad')
        nodes = [
            desired(path, code, rigid=True, mtime_ns=10, digest=digest,
                    fingerprint=fingerprint)
            for code, digest, fingerprint in (
                ('cube(1);', 'digest-one', 'fingerprint-one'),
                ('cube(2);', 'digest-two', 'fingerprint-two'),
                ('cube(1);', 'digest-one', 'fingerprint-one'),
            )
        ]

        with SourceGeneration(self.root), mock.patch.object(
                currency, 'publish_text') as write:
            for node in nodes:
                publish(node)

        self.assertEqual(write.call_count, 3)

    def test_unknown_identity_invalidates_rigid_current_artifact(self):
        path = os.path.join(self.root, 'shared.scad')
        nodes = [
            desired(path, 'cube(1);', rigid=True,
                    digest='digest-a', fingerprint='fingerprint-a'),
            desired(path, 'cube(2);', rigid=True,
                    digest=None, fingerprint=None),
            desired(path, 'cube(1);', rigid=True,
                    digest='digest-a', fingerprint='fingerprint-a'),
        ]

        with SourceGeneration(self.root), mock.patch.object(
                currency, 'publish_text') as write:
            for node in nodes:
                publish(node)

        self.assertEqual(write.call_count, 3)

    def test_non_rigid_instances_sharing_a_path_publish_each_request(self):
        """No coalescing: two non-rigid nodes sharing one path, asked for
        in an assembly phase, are each published when asked."""
        path = os.path.join(self.root, 'assembly.scad')
        nodes = [desired(path, code) for code in (
            'translate([1, 0, 0]) cube(1);', 'translate([2, 0, 0]) cube(1);')]

        with SourceGeneration(self.root) as generation, mock.patch.object(
                currency, 'publish_text') as write:
            with generation.phase((), label='assembly'):
                for index, node in enumerate(nodes, 1):
                    publish(node)
                    self.assertEqual(write.call_count, index)

    def test_binding_dependent_assemblies_keep_distinct_compositions(self):
        with mock.patch.dict(os.environ, {'SOLID_BUILD_DIR': self.root}):
            first = ComposedBindingDependentAssembly()
            first.part = RepeatedBlock().translate([1, 0, 0])
            second = ComposedBindingDependentAssembly()
            second.part = RepeatedBlock().translate([2, 0, 0])
        path = writer.scad_file(first)
        self.assertEqual(path, writer.scad_file(second))
        files = first.files | first.part.files | second.files | second.part.files

        with SourceGeneration(self.root) as generation, mock.patch.object(
                currency, 'publish_text',
                wraps=currency.publish_text) as write:
            with generation.phase(files, label='assembly'):
                compositions = [first.assemble(), second.assemble()]
                # assemble() writes no SCAD (`scad-presentation`); a caller
                # asking for both assemblies' files gets each published,
                # the last one standing.
                writer.generate_scad(first)
                writer.generate_scad(second)

        self.assertNotEqual(writer.scad_text(compositions[0]),
                            writer.scad_text(compositions[1]))
        parent_writes = [
            call for call in write.call_args_list
            if os.path.realpath(call.args[0]) == os.path.realpath(path)
        ]
        self.assertEqual(len(parent_writes), 2)
        with open(path) as published:
            self.assertEqual(published.read(), writer.scad_code(second))

    def test_publication_is_immediate_in_every_phase_and_outside_one(self):
        nodes = [
            desired(os.path.join(self.root, 'assembly.scad'), 'cube(1);'),
            desired(os.path.join(self.root, 'phase.scad'), 'cube(2);'),
            desired(os.path.join(self.root, 'direct.scad'), 'cube(3);'),
            desired(os.path.join(self.root, 'spring.scad'), 'cube(4);',
                    flexible=True),
        ]

        with SourceGeneration(self.root) as generation, mock.patch.object(
                currency, 'publish_text') as write:
            with generation.phase((), label='assembly'):
                publish(nodes[0])
                self.assertEqual(write.call_count, 1)
                publish(nodes[3])
                self.assertEqual(write.call_count, 2)
            with generation.phase((), label='artifact_pass'):
                publish(nodes[1])
                self.assertEqual(write.call_count, 3)
            publish(nodes[2])
            self.assertEqual(write.call_count, 4)

    def test_a_failed_publication_leaves_only_completed_ones(self):
        first = desired(
            os.path.join(self.root, 'one.scad'), 'cube(2);',
            digest='new-one', fingerprint='new-one-fingerprint')
        second = desired(
            os.path.join(self.root, 'two.scad'), 'sphere(2);',
            digest='new-two', fingerprint='new-two-fingerprint')
        paths = [writer.scad_file(node) for node in (first, second)]
        for path in paths:
            currency.publish_text(
                path, 'cube(1);', first.mtime_ns,
                'old-digest', 'old-fingerprint')
        real_replace = os.replace

        def fail_second_artifact(source, target):
            if os.path.realpath(target) == os.path.realpath(paths[1]):
                raise OSError('second atomic replacement failed')
            return real_replace(source, target)

        with SourceGeneration(self.root) as generation, mock.patch(
                'os.replace', side_effect=fail_second_artifact):
            with self.assertRaisesRegex(
                    OSError, 'second atomic replacement failed'):
                with generation.phase((), label='assembly'):
                    publish(first)
                    publish(second)

        with open(paths[0]) as published:
            self.assertEqual(published.read(), 'cube(2);')
        self.assertEqual(currency.recorded_digest(paths[0]), 'new-one')
        with open(paths[1]) as published:
            self.assertEqual(published.read(), 'cube(1);')
        self.assertFalse(os.path.exists(currency.sidecar(paths[1])))
        self.assertFalse(any(name.endswith('.tmp')
                             for name in os.listdir(self.root)))

    def test_three_flexible_bindings_are_never_reused_by_base_scad_path(self):
        path = os.path.join(self.root, 'spring.scad')
        nodes = [desired(path, f'import("{binding}");', flexible=True,
                         mtime_ns=10)
                 for binding in ('spring-a.stl', 'spring-b.stl',
                                 'spring-c.stl')]

        with SourceGeneration(self.root), mock.patch.object(
                currency, 'publish_text') as write:
            for node in nodes:
                publish(node)

        self.assertEqual(write.call_count, 3)

    def test_scad_reuse_does_not_survive_a_source_generation(self):
        node = desired(os.path.join(self.root, 'part.scad'), 'cube(1);',
                       rigid=True, mtime_ns=10)

        with mock.patch.object(currency, 'publish_text') as write:
            with SourceGeneration(self.root):
                publish(node)
            with SourceGeneration(self.root):
                publish(node)

        self.assertEqual(write.call_count, 2)

    def test_overlapping_currency_digests_hash_each_distinct_source_once(self):
        paths = []
        for name, content in (('one.py', b'ONE = 1\n'),
                              ('two.py', b'TWO = 2\n')):
            path = os.path.join(self.root, name)
            with open(path, 'wb') as source:
                source.write(content)
            paths.append(path)
        census = SourceCensus(self.root)
        census.include(paths)

        import machinome.source_generation as source_generation
        original = source_generation._coherent_real_source_digest
        with mock.patch.object(
                source_generation, '_coherent_real_source_digest',
                wraps=original) as hashed:
            first = currency.source_digest(paths, self.root, census=census)
            second = currency.source_digest(
                [paths[1], paths[0], paths[0]], self.root, census=census)

        self.assertEqual(first, second)
        self.assertEqual(hashed.call_count, 2)

    def test_audit_scale_closures_hash_210_sources_once_in_one_census(self):
        paths = []
        for index in range(210):
            path = os.path.join(self.root, f'source_{index}.txt')
            with open(path, 'wb') as source:
                source.write(f'source {index}\n'.encode())
            paths.append(path)
        census = SourceCensus(self.root)
        census.include(paths)

        import machinome.source_generation as source_generation
        original = source_generation._coherent_real_source_digest
        with mock.patch.object(
                source_generation, '_coherent_real_source_digest',
                wraps=original) as hashed:
            expected = currency.source_digest(
                paths, self.root, census=census)
            for _ in range(190):
                self.assertEqual(currency.source_digest(
                    reversed(paths), self.root, census=census), expected)

        self.assertEqual(hashed.call_count, 210)


class PublishedRecordTest(TestCase):
    """(`openscad-out`, 2.9) The source generation keeps a record of what is
    currently published at each path, named for what it records; the
    assembly phase coalesces nothing and checkpoints as every phase does."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = self.temp.name

    def test_a_phase_has_no_coalescing(self):
        from machinome.source_generation import SourcePhase
        for name in ('defer_scad', 'coalesces_scad', 'pending_scad_count',
                     '_flush_scad'):
            with self.subTest(name=name):
                self.assertFalse(hasattr(SourcePhase, name))
        with SourceGeneration(self.root) as generation:
            phase = generation.phase((), label='assembly')
            for name in ('coalesces_scad', '_pending_scad'):
                with self.subTest(name=name):
                    self.assertFalse(hasattr(phase, name))

    def test_the_assembly_phase_checkpoints_post(self):
        from machinome.source_generation import SourcePhase
        labels = []
        real = SourcePhase.checkpoint

        def checkpoint(phase, paths=(), label=None):
            labels.append(label)
            return real(phase, paths, label=label)

        with mock.patch.object(SourcePhase, 'checkpoint', checkpoint):
            with SourceGeneration(self.root) as generation:
                with generation.phase((), label='assembly'):
                    pass
        self.assertEqual(labels, ['assembly post'])

    def test_historical_identity_is_not_current_identity(self):
        path = os.path.join(self.root, 'shared.out')
        one = (10, 'digest-one', 'fingerprint-one')
        two = (10, 'digest-two', 'fingerprint-two')
        with SourceGeneration(self.root) as generation:
            self.assertFalse(hasattr(generation, 'has_scad_artifact'))
            self.assertFalse(generation.has_published(path, one))
            generation.remember_published(path, one)
            self.assertTrue(generation.has_published(path, one))
            generation.remember_published(path, two)
            self.assertFalse(generation.has_published(path, one))
            self.assertTrue(generation.has_published(path, two))
            generation.remember_published(path, one)
            self.assertTrue(generation.has_published(path, one))
            generation.remember_published(path, (10, None, None))
            self.assertFalse(generation.has_published(path, one))
            self.assertFalse(generation.has_published(path, (10, None, None)))


class CompareBeforeReplaceTest(TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = os.path.join(self.temp.name, 'part.scad')
        self.stamp = 1_700_000_000_123_456_789

    def publish(self, content='cube(1);', stamp=None, digest='digest',
                fingerprint='fingerprint'):
        currency.publish_text(
            self.path, content, self.stamp if stamp is None else stamp,
            digest, fingerprint)

    def replacements(self, action):
        replaced = []
        original = os.replace

        def counting(source, target):
            replaced.append(os.path.realpath(target))
            return original(source, target)

        with mock.patch('os.replace', side_effect=counting):
            action()
        return replaced

    def test_identical_text_stamp_and_record_replace_nothing(self):
        self.publish()
        before = {
            path: os.stat(path)
            for path in (self.path, currency.sidecar(self.path))
        }

        replaced = self.replacements(self.publish)

        self.assertEqual(replaced, [])
        for path, previous in before.items():
            current = os.stat(path)
            self.assertEqual(current.st_ino, previous.st_ino)
            self.assertEqual(current.st_mtime_ns, previous.st_mtime_ns)
            self.assertEqual(current.st_ctime_ns, previous.st_ctime_ns)

    def test_equal_text_with_new_metadata_restamps_without_text_replace(self):
        self.publish()
        old_inode = os.stat(self.path).st_ino
        moved = self.stamp + 1_000_000

        replaced = self.replacements(lambda: self.publish(
            stamp=moved, fingerprint='new-fingerprint'))

        self.assertEqual(replaced, [
            os.path.realpath(currency.sidecar(self.path)),
        ])
        self.assertEqual(os.stat(self.path).st_ino, old_inode)
        self.assertEqual(os.stat(self.path).st_mtime_ns, moved)
        self.assertEqual(currency.recorded_digest(self.path), 'digest')
        self.assertEqual(currency.recorded_fingerprint(self.path),
                         'new-fingerprint')

    def test_changed_text_atomically_replaces_text_and_record(self):
        self.publish()

        replaced = self.replacements(
            lambda: self.publish(content='cube(2);', digest='new-digest'))

        self.assertEqual(replaced, [
            os.path.realpath(self.path),
            os.path.realpath(currency.sidecar(self.path)),
        ])
        with open(self.path) as source:
            self.assertEqual(source.read(), 'cube(2);')
        self.assertEqual(currency.recorded_digest(self.path), 'new-digest')
