# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""A clocked model is refused publication, loudly -- and a stateless one
is unchanged in every byte and every code path.

The document version that carries declared states is a later cycle's. A
tree that declares a `State` is therefore refused where a document's BODY
is assembled: the one function every producer passes through, which is
what makes the browser-renderer row below the case that decides where the
gate goes -- it stages a baked document without entering the symbolic
walk at all.

Publishing a clocked model at an existing version, with its states
rendered as their initial values, was rejected outright: the geometry
would be correct only at the initial state and would then silently stop
following the machine.

Tasks 7 and 8 of the change `declare-the-state`.
"""

import json
import os

from solid_node.core.export import export_node
from solid_node.core.serializer import (ClockedDocumentError, document_body,
                                        symbolic_document)
from solid_node.simulation import Sim
from solid_node.simulation import clocked as clocked_module

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


class PublicationRefusalTest(BaseNodeTest):
    """Task 7.1: every producer, one assertion each."""

    def _refused(self, call):
        with self.assertRaises(ClockedDocumentError) as caught:
            call()
        message = str(caught.exception)
        self.assertIn('units', message)
        self.assertIn('tens', message)
        self.assertIn('not defined yet', message)
        return message

    def test_the_document_body_refuses_naming_the_states(self):
        node = built(Counter())
        self._refused(lambda: document_body(node, {}, {}, {}))

    def test_export_is_refused_and_writes_no_manifest(self):
        node = built(Counter())
        out_dir = os.path.join(self.build_dir, 'clocked_export')
        self._refused(lambda: export_node(node, out_dir, widget=False))
        self.assertFalse(os.path.exists(os.path.join(out_dir,
                                                     'manifest.json')))

    def test_a_build_publication_is_refused(self):
        """`solid build` and `solid develop` both publish through the
        builder, so one gate covers them."""
        from solid_node.core.builder import Builder

        node = built(Counter())
        builder = Builder.__new__(Builder)
        builder.node = node
        builder.build_dir = os.path.join(self.build_dir, 'clocked_build')
        os.makedirs(builder.build_dir, exist_ok=True)
        from solid_node.core.pieces import PieceInventory

        with PieceInventory() as inventory:
            self._refused(
                lambda: builder._write_viewer_snapshot_with_inventory(
                    inventory))
        self.assertFalse(
            os.path.exists(os.path.join(builder.build_dir, 'manifest.json')))

    def test_the_browser_renderer_is_refused_without_the_symbolic_walk(self):
        """The row that decides where the gate goes: a web snapshot
        stages a baked document from `document_body` WITHOUT entering
        `symbolic_document` at all."""
        from solid_node.viewers.browser import BrowserRenderer

        node = built(Counter())
        renderer = BrowserRenderer()
        beside = os.path.dirname(self.build_dir)
        before = set(os.listdir(beside))
        self._refused(lambda: renderer._stage(node, self.build_dir))
        # `_stage` makes its staging directory AFTER the document body,
        # so a refused capture leaves nothing behind.
        self.assertEqual(set(os.listdir(beside)) - before, set())


class UntouchedTest(BaseNodeTest):
    """Task 7.1: everything that writes no document is untouched."""

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
    """Task 8: a tree that declares no `State` pays nothing."""

    def test_a_stateless_tree_enters_no_clocked_path(self):
        before = clocked_module.entered()
        node = Stateless()
        node.set_state(crank=0.0, time=0.0)
        node.render()
        sim = Sim(node, 0.02)
        sim.run(0.1)
        with symbolic_document(node) as (declarations, instructions):
            self.assertIn('crank', declarations)
        self.assertEqual(clocked_module.entered(), before)

    def test_a_clocked_tree_does_enter_one(self):
        before = clocked_module.entered()
        Sim(Counter())
        self.assertGreater(clocked_module.entered(), before)

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
