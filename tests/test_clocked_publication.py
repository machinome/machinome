# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""A clocked model PUBLISHES -- through every producer -- and a stateless
one is unchanged in every byte and every code path.

This file was the refusal's own test. `declare-the-state` stated an owned
GAP: the document version that carries declared states did not exist, so
every producer refused a clocked model by name rather than publish one a
consumer would animate wrongly. `publish-the-clocked-machine` defines
that version, so each refusal below is INVERTED into the publication it
stood in for (design section 2, task 4.7).

What survives of the old requirement survives here: the structural check
stays in the one function every producer passes through -- now refusing a
clocked tree published WITHOUT its compiled machine, which is a PRODUCER
error -- a clocked model is still never published at a lower version with
its states rendered as their initial values, and everything that writes
no document is still untouched.
"""

import json
import logging
import os
import shutil
from unittest.mock import patch

from solid_node.core.export import export_node
from solid_node.core.serializer import (ClockedDocumentError, document_body,
                                        symbolic_document)
from solid_node.simulation import Sim
from solid_node.simulation import clocked as clocked_module
from solid_node.viewers import bundle as viewer_bundle

from .base import BaseNodeTest
from .clocked_project.counter import Counter, Stateless


def built(node):
    """`node` with its declared defaults bound and its artifacts on
    disk: what a producer is handed, and what the loader does for it."""
    from solid_node.node import StlRenderStart
    from solid_node.simulation.enumeration import bind_declared_defaults

    bind_declared_defaults(node)
    node.assemble()
    for _attempt in range(5):
        try:
            node.build_stls()
            break
        except StlRenderStart:
            continue
    return node


def unreadable():
    """An installation whose viewer renders versions 1 to 4: what every
    installation is until the viewer's own cycle learns version 8."""
    return patch.object(viewer_bundle, 'document_versions',
                        return_value=[1, 2, 3, 4])


class ProducerPublicationTest(BaseNodeTest):
    """(7.1, 7.2) Every producer that WRITES a document writes version 8
    and warns that the installed viewer cannot read it."""

    def test_export_writes_the_document_with_the_warning(self):
        node = built(Counter())
        out_dir = os.path.join(self.build_dir, 'clocked_export')
        with unreadable(), \
                patch.object(viewer_bundle, 'describe',
                             return_value={'version': '0.1.0'}), \
                self.assertLogs('core.export', level=logging.WARNING) as logs:
            export_node(node, out_dir, widget=False)
        with open(os.path.join(out_dir, 'manifest.json')) as handle:
            manifest = json.load(handle)
        self.assertEqual(manifest['version'], 8)
        self.assertIn('clocked', manifest)
        self.assertIn('states', manifest)
        self.assertEqual(len([one for one in logs.output
                              if 'document version 8' in one]), 1)

    def test_a_build_publication_writes_the_document_with_the_warning(self):
        """`solid build` and `solid develop` both publish through the
        builder, so one assertion covers them."""
        from solid_node.core.builder import Builder
        from solid_node.core.pieces import PieceInventory

        node = built(Counter())
        builder = Builder.__new__(Builder)
        builder.node = node
        builder.build_dir = os.path.join(self.build_dir, 'clocked_build')
        os.makedirs(builder.build_dir, exist_ok=True)
        with unreadable(), \
                patch.object(viewer_bundle, 'describe',
                             return_value={'version': '0.1.0'}), \
                self.assertLogs('core.builder',
                                level=logging.WARNING) as logs:
            with PieceInventory() as inventory:
                builder._write_viewer_snapshot_with_inventory(inventory)
        with open(os.path.join(builder.build_dir, 'viewer.json')) as handle:
            snapshot = json.load(handle)
        self.assertEqual(snapshot['version'], 8)
        self.assertIn('clocked', snapshot)
        self.assertEqual(len([one for one in logs.output
                              if 'document version 8' in one]), 1)


class BrowserRefusalTest(BaseNodeTest):
    """(7.3) The row that decided where the gate goes: a web snapshot
    stages a baked document from `document_body` WITHOUT entering
    `symbolic_document` at all -- and a version the installed viewer
    cannot read is refused BEFORE the browser starts."""

    def test_the_web_renderer_refuses_naming_version_eight(self):
        from solid_node.viewers import browser as browser_module
        from solid_node.viewers.browser import (BrowserRenderer,
                                                BrowserSnapshotError)

        node = built(Counter())
        renderer = BrowserRenderer()
        beside = os.path.dirname(self.build_dir)
        before = set(os.listdir(beside))
        with patch.object(browser_module.viewer_bundle, 'has_bundle',
                          return_value=True), \
                patch.object(browser_module.viewer_bundle,
                             'document_versions',
                             return_value=[1, 2, 3, 4, 5]), \
                patch.object(browser_module.viewer_bundle, 'describe',
                             return_value={'version': '0.1.0'}), \
                patch.object(browser_module, 'run') as started:
            with self.assertRaises(BrowserSnapshotError) as caught:
                renderer._stage(node, self.build_dir)
        message = str(caught.exception)
        self.assertIn('8', message)
        self.assertIn('1, 2, 3, 4, 5', message)
        self.assertIn('0.1.0', message)
        started.assert_not_called()
        # `_stage` makes its staging directory AFTER the version
        # comparison, so a refused capture leaves nothing behind.
        self.assertEqual(set(os.listdir(beside)) - before, set())

    def test_a_viewer_reporting_eight_photographs_it(self):
        from solid_node.viewers import browser as browser_module
        from solid_node.viewers.browser import BrowserRenderer

        node = built(Counter())
        renderer = BrowserRenderer()
        with patch.object(browser_module.viewer_bundle, 'has_bundle',
                          return_value=True), \
                patch.object(browser_module.viewer_bundle,
                             'document_versions',
                             return_value=[1, 2, 3, 4, 5, 8]):
            staging = renderer._stage(node, self.build_dir)
        self.addCleanup(shutil.rmtree, staging, ignore_errors=True)
        with open(os.path.join(staging, 'viewer.json')) as handle:
            document = json.load(handle)
        self.assertEqual(document['version'], 8)
        self.assertIn('clocked', document)
        self.assertEqual(sorted(document['states']), ['tens', 'units'])
        self.assertEqual(sorted(document['drivers']), ['crank'])


class ReaimedGateTest(BaseNodeTest):
    """(7.6) Each of the FOUR producers reaches the re-aimed gate: a
    clocked tree published without its compiled machine is refused, so a
    fifth producer added later cannot reach a lower-version document by
    a route nobody re-checked."""

    def refused(self, call):
        with self.assertRaises(ClockedDocumentError) as caught:
            call()
        message = str(caught.exception)
        self.assertIn('units', message)
        self.assertIn('tens', message)
        self.assertIn('without its compiled machine', message)
        return message

    def test_the_document_body_refuses_naming_the_states(self):
        node = built(Counter())
        self.refused(lambda: document_body(node, {}, {}, {}))

    def test_each_producer_reaches_it(self):
        """Every producer compiles the machine before it publishes, so
        the refusal is reached by BLINDING each one's compile -- which is
        exactly the mistake the gate is there to catch."""
        from solid_node.core import builder as builder_module
        from solid_node.core import export as export_module
        from solid_node.core.builder import Builder
        from solid_node.core.pieces import PieceInventory
        from solid_node.viewers import browser as browser_module
        from solid_node.viewers.browser import BrowserRenderer

        blind = (None, None)
        node = built(Counter())

        out_dir = os.path.join(self.build_dir, 'blind_export')
        with patch.object(export_module, 'compiled_clocked',
                          return_value=blind):
            self.refused(lambda: export_node(node, out_dir, widget=False))
        self.assertFalse(os.path.exists(os.path.join(out_dir,
                                                     'manifest.json')))

        builder = Builder.__new__(Builder)
        builder.node = node
        builder.build_dir = os.path.join(self.build_dir, 'blind_build')
        os.makedirs(builder.build_dir, exist_ok=True)
        with patch.object(builder_module, 'compiled_clocked',
                          return_value=blind):
            with PieceInventory() as inventory:
                self.refused(
                    lambda: builder._write_viewer_snapshot_with_inventory(
                        inventory))
        self.assertFalse(os.path.exists(os.path.join(builder.build_dir,
                                                     'viewer.json')))

        renderer = BrowserRenderer()
        with patch.object(browser_module, 'compiled_clocked',
                          return_value=blind), \
                patch.object(browser_module.viewer_bundle, 'has_bundle',
                             return_value=True):
            self.refused(lambda: renderer._stage(node, self.build_dir))

        from tools import generate_clocked_corpus

        with patch.object(generate_clocked_corpus, 'compiled_clocked',
                          return_value=blind):
            self.refused(lambda: generate_clocked_corpus.document_of(
                'Counter'))


class UntouchedTest(BaseNodeTest):
    """Everything that writes no document is untouched, exactly as
    `declare-the-state` left it."""

    def test_render_assemble_and_stls_all_succeed(self):
        node = Counter()
        Sim(node)
        self.assertIsNotNone(node.render())
        node.assemble()
        node.build_stls()

    def test_the_openscad_snapshot_builds_no_document(self):
        """`manager/snapshot.py` renders the POSED node through the
        OpenSCAD renderer, so it never reaches a document body and a
        clocked model can still be photographed."""
        import inspect

        from solid_node.manager import snapshot as snapshot_module

        source = inspect.getsource(snapshot_module)
        self.assertNotIn('document_body', source)
        self.assertNotIn('symbolic_document', source)


class ZeroBehaviourChangeTest(BaseNodeTest):
    """A tree that declares no `State` pays nothing and moves no byte."""

    def test_a_stateless_tree_enters_no_clocked_path(self):
        before = clocked_module.entered()
        node = Stateless()
        node.set_state(crank=0.0, time=0.0)
        node.render()
        sim = Sim(node, 0.02)
        sim.run(0.1)
        with symbolic_document(node) as (declarations, instructions):
            self.assertIn('crank', declarations)
        from solid_node.core.serializer import (compiled_clocked,
                                                drivers_table, serialize_node)

        clocked, bank = compiled_clocked(node)
        self.assertEqual((clocked, bank), (None, None))
        with symbolic_document(node) as (declarations, instructions):
            root = serialize_node(node, lambda rigid: 'parts/dial.stl')
            drivers = drivers_table(declarations)
        document_body(node, root, drivers, {})
        self.assertEqual(clocked_module.entered(), before)

    def test_a_clocked_tree_does_enter_one(self):
        before = clocked_module.entered()
        Sim(Counter())
        self.assertGreater(clocked_module.entered(), before)

    def test_a_stateless_tree_costs_one_structural_walk(self):
        """(4.8) `document_body` asks the one structural question it has
        always asked and renders nothing for the answer."""
        from solid_node.core.serializer import (drivers_table, serialize_node)
        from solid_node.simulation import enumeration

        node = Stateless()
        node.set_state(crank=0.0, time=0.0)
        with symbolic_document(node) as (declarations, instructions):
            root = serialize_node(node, lambda rigid: 'parts/dial.stl')
            drivers = drivers_table(declarations)
        walks = []
        original = enumeration.tree_declares_states

        def counted(target, seen=None):
            if seen is None:
                # The TOP of one walk: the recursion below it descends
                # through `seen`, so this counts walks and not nodes.
                walks.append(target)
            return original(target, seen)

        with patch.object(enumeration, 'tree_declares_states',
                          side_effect=counted):
            document_body(node, root, drivers, {})
        self.assertEqual(len(walks), 1)

    #: The document a stateless model published at the base of this
    #: cycle, `81c5364`, taken by running the same three calls under that
    #: checkout and under this worktree and diffing the two (evidence.md,
    #: "Byte-identical publication"). Pinned as a literal so a later
    #: change to this capability cannot move it silently. `animation` is
    #: dropped because it carries the fps and frame count the CALLER
    #: passes, not anything this capability touches.
    RECORDED = (
        '{"drivers": {"crank": {"default": 0, "dtype": null, "range": '
        'null, "scale": null, "unit": "deg"}}, "format": '
        '"solid-node-export", "instructions": {}, "version": 2}')

    def test_a_stateless_document_is_byte_identical(self):
        from solid_node.core.serializer import drivers_table, serialize_node

        node = Stateless()
        with symbolic_document(node) as (declarations, instructions):
            root = serialize_node(node, lambda rigid: 'parts/dial.stl')
            drivers = drivers_table(declarations)
        body = document_body(node, root, drivers, {})
        body.pop('animation')
        self.assertEqual(json.dumps(body, sort_keys=True), self.RECORDED)
