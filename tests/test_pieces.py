# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Red-first proof for openspec/changes/printed-piece-identity.

The gearbox finding (proposal.md): six differently-named bushing classes
building byte-identical geometry are six artifacts (uniq_id) but must be
reported as ONE printed piece. tests/pieces_project minimises that
reproduction: RepeatedBolt is placed three times (one part, several
poses), and BushingA/BushingB are two classes with identical render()
output (two artifacts, one piece).
"""

import json
import os
import shutil
import struct
import tempfile
from unittest import TestCase

import trimesh

from machinome.core.builder import Builder
from machinome.core.export import export_node

from .base import BaseNodeTest
from . import pieces_project


class _FingerprintNode:
    """Minimal stand-in for a rigid node: PieceInventory.register only
    reads .stl_file, .src and the node's class name off it, so a full
    AbstractBaseNode is unnecessary weight for these unit tests."""

    def __init__(self, stl_file, content, src=None):
        os.makedirs(os.path.dirname(stl_file), exist_ok=True)
        with open(stl_file, 'wb') as artifact:
            artifact.write(content)
        self.stl_file = stl_file
        self.src = src or __file__


class Bolt(_FingerprintNode):
    pass


class BushingA(_FingerprintNode):
    pass


class BushingB(_FingerprintNode):
    pass


def _box_stl_bytes(extents):
    return trimesh.creation.box(extents=extents).export(file_type='stl')


def _binary_facets(data):
    count = struct.unpack_from('<I', data, 80)[0]
    facets = []
    for index in range(count):
        values = struct.unpack_from('<12fH', data, 84 + 50 * index)
        facets.append((values[:3],
                       [values[3:6], values[6:9], values[9:12]],
                       values[12]))
    return facets


def _binary_stl(facets, header=b''):
    out = [header.ljust(80, b'\0'), struct.pack('<I', len(facets))]
    for normal, vertices, attribute in facets:
        out.append(struct.pack(
            '<12fH', *normal, *[c for v in vertices for c in v], attribute))
    return b''.join(out)


class PieceInventoryUnitTest(TestCase):
    """Direct tests of the accumulator (tasks.md 2.4): merging across
    classes, counting repeated placements, deterministic ordering, and
    ids stable regardless of artifact path or walk order."""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='machinome-pieces-')
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.box_bytes = _box_stl_bytes((1, 2, 3))
        self.other_box_bytes = _box_stl_bytes((4, 5, 6))

    def _path(self, *parts):
        return os.path.join(self.root, *parts)

    def test_repeated_placements_of_one_artifact_count_and_merge(self):
        from machinome.core.pieces import PieceInventory

        inventory = PieceInventory()
        stl_file = self._path('bolt.stl')
        with open(stl_file, 'wb') as artifact:
            artifact.write(self.box_bytes)

        ids = [
            inventory.register(Bolt(stl_file, self.box_bytes), 'bolt.stl')
            for _ in range(3)
        ]

        self.assertEqual(len(set(ids)), 1)
        pieces = inventory.pieces()
        self.assertEqual(len(pieces), 1)
        self.assertEqual(pieces[0]['count'], 3)
        self.assertEqual(pieces[0]['models'], ['bolt.stl'])

    def test_identical_content_from_different_classes_is_one_piece(self):
        from machinome.core.pieces import PieceInventory

        inventory = PieceInventory()
        a_id = inventory.register(
            BushingA(self._path('a.stl'), self.box_bytes), 'models/a.stl')
        b_id = inventory.register(
            BushingB(self._path('b.stl'), self.box_bytes), 'models/b.stl')

        self.assertEqual(a_id, b_id)
        pieces = inventory.pieces()
        self.assertEqual(len(pieces), 1)
        piece = pieces[0]
        self.assertEqual(piece['count'], 2)
        self.assertEqual(piece['models'], ['models/a.stl', 'models/b.stl'])
        self.assertIn('test_pieces.py', piece['sources'][0])

    def test_differing_content_stays_distinct(self):
        from machinome.core.pieces import PieceInventory

        inventory = PieceInventory()
        a_id = inventory.register(
            Bolt(self._path('a.stl'), self.box_bytes), 'a.stl')
        b_id = inventory.register(
            Bolt(self._path('b.stl'), self.other_box_bytes), 'b.stl')

        self.assertNotEqual(a_id, b_id)
        self.assertEqual(len(inventory.pieces()), 2)

    def test_one_triangle_set_in_another_facet_order_is_one_piece(self):
        """OpenSCAD 2021.01 writes the same triangles in a run-dependent
        order (warts: piece identity on the CI runner). The captured pair
        is one SCAD rendered twice by the same binary: identical triangle
        sets, different bytes. They are one printed piece."""
        from machinome.core.pieces import PieceInventory

        fixtures = os.path.join(
            os.path.dirname(__file__), 'pieces_project',
            'openscad_facet_order')
        renders = [
            open(os.path.join(fixtures, name), 'rb').read()
            for name in ('bushing-0e78e481b129.stl',
                         'bushing-85a25e7b22e1.stl')]
        self.assertNotEqual(renders[0], renders[1])

        inventory = PieceInventory()
        a_id = inventory.register(
            BushingA(self._path('a.stl'), renders[0]), 'a.stl')
        b_id = inventory.register(
            BushingB(self._path('b.stl'), renders[1]), 'b.stl')

        self.assertEqual(a_id, b_id)
        self.assertEqual(len(inventory.pieces()), 1)
        self.assertEqual(inventory.pieces()[0]['count'], 2)

    def test_header_normals_attributes_and_vertex_rotation_are_not_content(
            self):
        """Everything a binary STL carries besides its oriented
        triangles -- the 80-byte header, the stored normals (including
        the sign of a zero), the attribute words, the facet order and
        which vertex of a facet is written first -- is encoding."""
        from machinome.core.pieces import PieceInventory

        facets = _binary_facets(self.box_bytes)
        rewritten = []
        for index, (normal, vertices, attribute) in enumerate(
                reversed(facets)):
            turn = index % 3
            vertices = vertices[turn:] + vertices[:turn]
            normal = tuple(-0.0 if value == 0 else value
                           for value in normal)
            rewritten.append((normal, vertices, 7))
        encoded = _binary_stl(rewritten, header=b'another producer')
        self.assertNotEqual(encoded, self.box_bytes)

        inventory = PieceInventory()
        a_id = inventory.register(
            BushingA(self._path('a.stl'), self.box_bytes), 'a.stl')
        b_id = inventory.register(
            BushingB(self._path('b.stl'), encoded), 'b.stl')

        self.assertEqual(a_id, b_id)

    def test_reversed_winding_and_mirroring_stay_distinct(self):
        """Canonical order must not forget orientation: the same vertex
        triples wound the other way describe an inside-out solid, and
        a mirror image is a different part."""
        from machinome.core.pieces import PieceInventory

        facets = _binary_facets(self.box_bytes)
        inverted = _binary_stl(
            [(normal, vertices[::-1], attribute)
             for normal, vertices, attribute in facets])
        mirrored = _binary_stl(
            [(normal, [(-x, y, z) for x, y, z in vertices[::-1]],
              attribute)
             for normal, vertices, attribute in facets])

        inventory = PieceInventory()
        ids = {
            inventory.register(
                Bolt(self._path(f'{name}.stl'), content), f'{name}.stl')
            for name, content in (('box', self.box_bytes),
                                  ('inverted', inverted),
                                  ('mirrored', mirrored))}

        self.assertEqual(len(ids), 3)

    def test_pieces_are_ordered_by_first_encounter(self):
        from machinome.core.pieces import PieceInventory

        inventory = PieceInventory()
        first_id = inventory.register(
            Bolt(self._path('first.stl'), self.other_box_bytes), 'first.stl')
        second_id = inventory.register(
            Bolt(self._path('second.stl'), self.box_bytes), 'second.stl')

        ids = [piece['id'] for piece in inventory.pieces()]
        self.assertEqual(ids, [first_id, second_id])

    def test_geometry_facts_read_from_the_artifacts_own_frame(self):
        from machinome.core.pieces import PieceInventory

        inventory = PieceInventory()
        inventory.register(
            Bolt(self._path('box.stl'), self.box_bytes), 'box.stl')

        piece = inventory.pieces()[0]
        self.assertAlmostEqual(piece['size'][0], 1, places=3)
        self.assertAlmostEqual(piece['size'][1], 2, places=3)
        self.assertAlmostEqual(piece['size'][2], 3, places=3)
        self.assertAlmostEqual(piece['volume'], 6, places=3)
        self.assertTrue(piece['watertight'])

    def test_ids_are_stable_regardless_of_artifact_path(self):
        from machinome.core.pieces import PieceInventory

        first = PieceInventory()
        second = PieceInventory()
        id_at_one_path = first.register(
            Bolt(self._path('somewhere', 'bolt.stl'), self.box_bytes),
            'bolt.stl')
        id_at_another_path = second.register(
            Bolt(self._path('elsewhere', 'part.stl'), self.box_bytes),
            'part.stl')

        self.assertEqual(id_at_one_path, id_at_another_path)

    def test_unreadable_artifact_is_never_identified_by_its_parameters(self):
        """Identity is content or it is nothing.

        An artifact that cannot be read gets no piece id at all: falling
        back to uniq_id would key the piece on the class and constructor
        parameters this capability exists to stop standing in for
        geometry. Publication is already gated on every artifact being
        current, so this is an internal inconsistency and belongs to the
        caller that published a tree naming the missing file.
        """
        from machinome.core.pieces import PieceInventory

        inventory = PieceInventory()
        missing = Bolt(self._path('missing.stl'), self.box_bytes)
        os.remove(missing.stl_file)

        with self.assertRaises(OSError):
            inventory.register(missing, 'missing.stl')

        self.assertEqual(inventory.pieces(), [])


class PublishedPiecesInventoryTest(BaseNodeTest):
    """A real project build (tasks.md 1.2): the published viewer.json
    must carry a pieces list, a piece id on every rigid node, one piece
    for the repeated bolt with the right count, and one merged piece for
    the two identical bushing classes naming both sources."""

    def _build(self):
        node = pieces_project.PiecesAssembly()
        node.assemble()
        node.build_stls()
        builder = Builder('model.py', build_dir=self.build_dir)
        builder.node = node
        builder._write_viewer_snapshot()
        with open(os.path.join(self.build_dir, 'viewer.json')) as snapshot:
            return json.load(snapshot)

    def test_published_document_carries_a_piece_inventory(self):
        document = self._build()

        self.assertIn('pieces', document)
        self.assertGreater(len(document['pieces']), 0)

    def test_every_rigid_node_references_a_published_piece(self):
        document = self._build()
        piece_ids = {piece['id'] for piece in document['pieces']}

        def rigid_nodes(node):
            if 'model' in node:
                yield node
                return
            for child in node.get('children', []):
                yield from rigid_nodes(child)

        rigids = list(rigid_nodes(document['root']))
        self.assertEqual(len(rigids), 5)
        for node in rigids:
            self.assertIn('piece', node)
            self.assertIn(node['piece'], piece_ids)

    def test_repeated_part_is_one_piece_with_count_three(self):
        document = self._build()
        bolt_pieces = [piece for piece in document['pieces']
                       if piece['name'] == 'RepeatedBolt']

        self.assertEqual(len(bolt_pieces), 1)
        self.assertEqual(bolt_pieces[0]['count'], 3)

    def test_identical_classes_merge_into_one_piece_naming_both_sources(self):
        document = self._build()

        bushing_pieces = [
            piece for piece in document['pieces']
            if any('bushings.py' in source for source in piece['sources'])
        ]
        self.assertEqual(len(bushing_pieces), 1)
        piece = bushing_pieces[0]
        self.assertEqual(piece['count'], 2)
        self.assertEqual(len(piece['sources']), 1,
                          'BushingA and BushingB share one source file')
        self.assertEqual(len(piece['models']), 2,
                          'each class still built its own artifact')

    def test_unchanged_rebuild_republishes_byte_identical_document(self):
        node = pieces_project.PiecesAssembly()
        node.assemble()
        node.build_stls()
        builder = Builder('model.py', build_dir=self.build_dir)
        builder.node = node
        builder._write_viewer_snapshot()
        with open(os.path.join(self.build_dir, 'viewer.json'), 'rb') as f:
            first = f.read()

        rebuild_node = pieces_project.PiecesAssembly()
        rebuild_node.assemble()
        rebuild_node.build_stls()
        rebuilder = Builder('model.py', build_dir=self.build_dir)
        rebuilder.node = rebuild_node
        republished = rebuilder._write_viewer_snapshot()
        with open(os.path.join(self.build_dir, 'viewer.json'), 'rb') as f:
            second = f.read()

        self.assertFalse(republished,
                          'an unchanged rebuild must not notify a consumer')
        self.assertEqual(first, second)

    def test_sweep_preserves_every_model_the_inventory_names(self):
        document = self._build()

        for piece in document['pieces']:
            for model in piece['models']:
                path = os.path.join(self.build_dir, model)
                self.assertTrue(os.path.isfile(path),
                                 f'{model} named by the inventory was swept')


class ExportBuildPiecesParityTest(BaseNodeTest):
    """Same model, published two ways, must agree on piece ids and
    counts (printed-pieces spec: 'The same model published two ways
    agrees')."""

    def test_export_and_build_agree_on_piece_ids_and_counts(self):
        node = pieces_project.PiecesAssembly()
        node.assemble()
        node.build_stls()
        builder = Builder('model.py', build_dir=self.build_dir)
        builder.node = node
        builder._write_viewer_snapshot()
        with open(os.path.join(self.build_dir, 'viewer.json')) as snapshot:
            build_document = json.load(snapshot)

        export_dir = os.path.join(self.build_dir, 'export_out')
        export_node_instance = pieces_project.PiecesAssembly()
        export_node_instance.assemble()
        manifest = export_node(export_node_instance, export_dir, widget=False)

        build_pieces = {piece['id']: piece for piece in build_document['pieces']}
        export_pieces = {piece['id']: piece for piece in manifest['pieces']}

        self.assertEqual(set(build_pieces), set(export_pieces))
        for piece_id, build_piece in build_pieces.items():
            self.assertEqual(build_piece['count'],
                              export_pieces[piece_id]['count'])
