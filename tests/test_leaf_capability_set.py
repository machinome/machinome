# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A leaf declares its kind as one set on the leaf base (OpenSpec change
`openscad-out`, capability `leaf-contract`, design.md Decision 5).

What the core asks a node of a leaf kind is one set of members with a
default on the node base: `rigid`, `flexible`, `exact`, `optimize`,
`present`, `presentation`, `kept_artifacts`, `generate_stl`, the artifact
paths, `base_mesh` and `declared_markings`. The core reads them directly,
never through `getattr` with a default or `hasattr`, and a leaf whose STL is
still not current after its materialization is refused naming it, instead of
being handed to OpenSCAD. The leaf contract is version 2.
"""

import ast
import importlib
import os
import shutil
import tempfile
from contextlib import ExitStack
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

import trimesh

ROOT = Path(__file__).resolve().parents[1]
BASEDIR = os.path.dirname(os.path.abspath(__file__))

#: The declared set (design.md Decision 5's table).
THE_SET = frozenset((
    'rigid', 'flexible', 'exact', 'optimize', 'present', 'presentation',
    'kept_artifacts', 'generate_stl', 'stl_file', 'brep_file', 'basepath',
    'local_stl', 'base_mesh', 'declared_markings'))


def probes(root=ROOT):
    """Every `getattr(x, '<member>', <default>)` and `hasattr(x,
    '<member>')` of a member of the set in `machinome/`."""
    found = []
    for path in sorted((root / 'machinome').rglob('*.py')):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)):
                continue
            if ((node.func.id == 'getattr' and len(node.args) == 3)
                    or (node.func.id == 'hasattr' and len(node.args) == 2)):
                member = node.args[1]
                if (isinstance(member, ast.Constant)
                        and member.value in THE_SET):
                    found.append(f'{path.relative_to(root).as_posix()}:'
                                 f'{node.lineno} {ast.unparse(node)}')
    return found


class _BuildDir(TestCase):

    def setUp(self):
        self.build_dir = tempfile.mkdtemp(prefix='leaf-capability-set-')
        self.addCleanup(shutil.rmtree, self.build_dir, ignore_errors=True)
        environment = patch.dict(os.environ,
                                 {'SOLID_BUILD_DIR': self.build_dir})
        environment.start()
        self.addCleanup(environment.stop)


def _leaf_classes():
    from machinome.node.leaf import LeafNode

    class MeshBlock(LeafNode):
        """A self-materializing leaf: it publishes its own STL."""

        def render(self):
            return trimesh.creation.box((2, 2, 2))

        def materialize(self, rendered):
            self.publish_artifact(
                self.stl_file,
                lambda temporary: rendered.export(temporary,
                                                  file_type='stl'))

    class Silent(LeafNode):
        """A leaf whose materialization publishes nothing."""

        def render(self):
            return trimesh.creation.box((2, 2, 2))

        def materialize(self, rendered):
            pass

    return MeshBlock, Silent


class ContractVersionTwoTest(TestCase):

    def test_the_core_speaks_contract_two(self):
        from machinome.node import leaf
        self.assertEqual(leaf.CONTRACT, 2)

    def test_a_declaration_of_one_is_refused_naming_both_versions(self):
        from machinome.node.leaf import LeafNode
        with self.assertRaises(TypeError) as refused:
            class Old(LeafNode):
                leaf_contract = 1
        message = str(refused.exception)
        self.assertIn('leaf contract 1', message)
        self.assertIn('leaf contract 2', message)
        self.assertIn('machinome.node.leaf', message)


class TheSetHasDefaultsTest(_BuildDir):

    def test_a_self_materializing_leaf_answers_the_whole_set(self):
        MeshBlock, _ = _leaf_classes()
        node = MeshBlock()
        self.assertIs(node.rigid, True)
        self.assertIs(node.flexible, False)
        self.assertIs(node.exact, False)
        self.assertIs(node.optimize, True)
        self.assertEqual(node.kept_artifacts(), ())
        self.assertEqual(node.declared_markings(), {})
        presented = node.present(node.render())
        self.assertEqual(type(presented).__name__, 'ArtifactImport')
        self.assertEqual(presented.path,
                         node.artifact_import(node.local_stl).path)
        self.assertTrue(os.path.exists(node.stl_file))

    def test_the_node_base_keeps_no_artifact(self):
        from machinome.node.base import AbstractBaseNode
        self.assertTrue(callable(AbstractBaseNode.kept_artifacts))
        self.assertTrue(callable(AbstractBaseNode.present))
        self.assertTrue(callable(AbstractBaseNode.presentation))

    def test_a_family_leaf_keeps_its_own_scad(self):
        from tests.flat_project.simple_cylinder import SimpleCylinder
        node = SimpleCylinder()
        self.assertEqual(node.kept_artifacts(), (node.scad_file,))


class NoProbeTest(TestCase):

    def test_the_core_reads_the_set_directly(self):
        self.assertEqual(probes(), [])


class ALeafThatProducedNoStlTest(_BuildDir):
    """R7: a rigid leaf whose STL is not current after its materialization
    is refused naming it, before any process is started."""

    def test_it_is_refused_naming_the_node_and_its_stl(self):
        from machinome.node import base
        ArtifactNotProduced = getattr(base, 'ArtifactNotProduced',
                                      AssertionError)
        _, Silent = _leaf_classes()
        node = Silent(name='quiet')

        def popen(*arguments, **keywords):
            raise AssertionError('a process was started')

        with ExitStack() as patches:
            try:
                importlib.import_module('machinome.node.openscad.binary')
            except ImportError:
                pass
            else:
                patches.enter_context(patch(
                    'machinome.node.openscad.binary.openscad_binary',
                    return_value='/nonexistent/sentinel'))
            patches.enter_context(patch('subprocess.Popen', popen))
            patches.enter_context(
                patch('machinome.node.openscad.leaf.Popen', popen))
            with self.assertRaises(ArtifactNotProduced) as refused:
                node.build_stls()
        self.assertIsInstance(refused.exception, RuntimeError)
        self.assertEqual(
            str(refused.exception),
            f'node quiet ({Silent.__qualname__}) produced no STL: its '
            f'materialization published nothing at {node.stl_file}')
