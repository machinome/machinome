# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Every `import(file = ...)` a generated `.scad` holds resolves against
disk from the directory of the `.scad` holding it -- for every leaf kind,
at every depth, whatever package the importing node is declared in
(`openspec/changes/import-the-artifact-by-path`).

`workflow/warts.md`'s Thor reproduction ("A leaf's artifact is imported
into its parent's `.scad` by bare filename...") is a cross-package parent
importing a flexible leaf; the fixture and this test also cover the rigid
and exact leaf kinds and an intermediate assembly, which the same
measurement (`evidence.md`) showed broken the other way.
"""

import os
import re

from solid_node.node import StlRenderStart

from .base import BaseNodeTest
from .cross_package_project.parts import OwnImportLeaf
from .cross_package_project.samebench import SameBench
from .cross_package_project.tools.bench import Bench
from .cross_package_project.tools.deep_bench import DeepBench

IMPORT_RE = re.compile(r'import\(file = "([^"]*)"')


def _imports(scad_text):
    """Every path an `import(file = "...")` in `scad_text` names, in the
    order OpenSCAD would read them."""
    return IMPORT_RE.findall(scad_text)


def _read(scad_file):
    with open(scad_file) as handle:
        return handle.read()


def _resolves(scad_file, imported_path):
    """Whether `imported_path` exists relative to the directory holding
    `scad_file` -- how OpenSCAD itself resolves an `import()`."""
    directory = os.path.dirname(scad_file)
    return os.path.exists(os.path.join(directory, imported_path))


def _assert_all_resolve(test, scad_file):
    text = _read(scad_file)
    imports = _imports(text)
    test.assertTrue(imports, f'{scad_file} holds no import() at all')
    for imported in imports:
        test.assertTrue(
            _resolves(scad_file, imported),
            f'{imported!r}, imported by {scad_file}, does not exist '
            f'relative to {os.path.dirname(scad_file)}')
    return text


def _build_stl(node):
    """Trigger every rigid leaf's asynchronous STL job under `node` and
    wait for it, repeating until a full walk triggers nothing -- the
    same two-step dance `tests.base.BaseNodeTest.load_solid` uses for
    one known `stl_level`, generalised to a tree whose count of
    OpenSCAD-built leaves the test does not want to hardcode."""
    for _ in range(10):
        try:
            node.trigger_stl()
        except StlRenderStart as job:
            job.wait()
        else:
            return
    raise AssertionError(f'{node} never finished triggering STL jobs')


def _forget_assembly(node):
    node._assembled = False
    for child in node.children:
        _forget_assembly(child)


class CrossPackageLeafKindsTest(BaseNodeTest):
    """`Bench`, in package `tools`, places a rigid, an exact and a
    flexible leaf all declared in the parent package -- the Thor shape.
    """

    def setUp(self):
        super().setUp()
        self.bench = Bench()
        self.bench.assemble()
        _build_stl(self.bench)
        _forget_assembly(self.bench)
        self.bench.assemble()

    def test_every_leaf_kind_resolves_from_the_parents_own_directory(self):
        text = _assert_all_resolve(self, self.bench.scad_file)
        # Three artifact-emitting leaves declared: a rigid, an exact and
        # a flexible one -- none of them inlined as raw geometry.
        self.assertEqual(len(_imports(text)), 3, text)

    def test_second_build_spells_it_the_same_way(self):
        """A fresh instance, built again with every artifact already
        current on disk, reads the same text and still resolves."""
        first_text = _read(self.bench.scad_file)

        second = Bench()
        second.assemble()
        second_text = _assert_all_resolve(self, second.scad_file)

        self.assertEqual(first_text, second_text)
        self.assertEqual(_imports(first_text), _imports(second_text))


class IntermediateAssemblyScadImportTest(BaseNodeTest):
    """`DeepBench` (root, `tools/`) places `Group` (`sub/deep/`), which
    places `RigidLeaf` (the top package): three packages, two `.scad`
    files each holding an import of the same artifact."""

    def setUp(self):
        super().setUp()
        self.deep_bench = DeepBench()
        self.deep_bench.assemble()
        _build_stl(self.deep_bench)
        _forget_assembly(self.deep_bench)
        self.deep_bench.assemble()

    def test_intermediate_assemblys_own_scad_resolves_from_its_own_directory(self):
        group = self.deep_bench.children[0]
        _assert_all_resolve(self, group.scad_file)

    def test_root_scad_over_that_intermediate_still_resolves(self):
        """Guard against fixing the intermediate end by breaking the
        root's, which has always resolved (evidence.md)."""
        _assert_all_resolve(self, self.deep_bench.scad_file)


class SamePackageControlTest(BaseNodeTest):
    """`SameBench` sits beside the leaves it places. Nothing here has
    ever needed to travel through the anchoring rule -- the guard that
    the fix leaves today's bare-basename spelling untouched."""

    def setUp(self):
        super().setUp()
        self.same_bench = SameBench()
        self.same_bench.assemble()
        _build_stl(self.same_bench)
        _forget_assembly(self.same_bench)
        self.same_bench.assemble()

    def test_bare_basenames_unchanged(self):
        text = _assert_all_resolve(self, self.same_bench.scad_file)
        for imported in _imports(text):
            self.assertEqual(
                imported, os.path.basename(imported),
                f'{imported!r} should be a bare basename, same package '
                f'as the leaf it names')


class ProjectsOwnImportTest(BaseNodeTest):
    """A leaf whose `render()` imports a file of the PROJECT's own must
    never be touched by re-anchoring -- the guard on that pass."""

    def test_own_import_reproduced_verbatim(self):
        leaf = OwnImportLeaf()
        leaf.assemble()
        text = _read(leaf.scad_file)
        self.assertIn('import(file = "vendor/external.stl"', text)
