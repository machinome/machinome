# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The OpenSCAD node family is the package `machinome.node.openscad`, and
`Solid2Node` is `machinome.node.solid2` over it (OpenSpec change
`openscad-out`, capability `openscad-node`).

The package holds the node type `OpenScadNode` (its `__init__`), the family's
leaf base (`leaf`), the SCAD writer (`writer`) and the OpenSCAD binary
contract (`binary`). The former seam `machinome.scad_engine` and engine
package `machinome.openscad` are gone, with nothing aliasing them. SolidPython
is the family's kernel, refused at three doors; a SolidPython value is adopted
by the expression graph only through the hook `machinome.node.solid2`
registers when it is imported.

Every test of an absent SolidPython runs in a subprocess under
`tests/brep_engine_absent.py`'s finder, which refuses `solid2` the way an
interpreter without its wheel does.
"""

import ast
import importlib
import json
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from tests.brep_engine_absent import run_python

ROOT = Path(__file__).resolve().parents[1]

#: The refusals of design.md Decision 8, spelled out here rather than read
#: from the code under test.
R1 = ('machinome.node.openscad (OpenScadNode and the OpenSCAD writer) needs '
      'solid2, which is not installed; install it with '
      '\'pip install "machinome[openscad]"\'')
R2 = ('machinome.node.solid2 (Solid2Node) needs solid2, which is not '
      'installed; install it with \'pip install "machinome[solid2]"\'')

#: The modules no project without the family may load.
FAMILY_ROOTS = ('solid2', 'machinome.scad_engine', 'machinome.openscad',
                'machinome.node.openscad')

#: Import one module and report what it raised, as JSON on the last line.
IMPORT_AND_REPORT = '''
import importlib, json
try:
    {statement}
except ImportError as raised:
    print(json.dumps({{
        'type': type(raised).__name__,
        'name': raised.name,
        'extra': getattr(raised, 'extra', None),
        'message': str(raised)}}))
else:
    print(json.dumps(None))
'''


def reported(statement, **blocking):
    run = run_python(IMPORT_AND_REPORT.format(statement=statement),
                     **blocking)
    lines = run.stdout.strip().splitlines()
    assert lines, run.output
    return json.loads(lines[-1]), run


class ThePackageTest(TestCase):
    """(2.2) The family's modules, at their addresses."""

    def test_the_package_modules_import(self):
        writer = importlib.import_module('machinome.node.openscad.writer')
        binary = importlib.import_module('machinome.node.openscad.binary')
        leaf = importlib.import_module('machinome.node.openscad.leaf')
        self.assertTrue(callable(writer.scad_text))
        self.assertTrue(callable(writer.scad_code))
        self.assertTrue(callable(writer.generate_scad))
        self.assertTrue(callable(binary.require_openscad))
        self.assertTrue(callable(binary.openscad_binary))
        self.assertTrue(issubclass(binary.OpenScadUnavailable, RuntimeError))
        self.assertTrue(isinstance(leaf.ScadLeafNode, type))

    def test_the_node_type_is_defined_at_its_address(self):
        from machinome.node.openscad import OpenScadNode
        import machinome.node
        self.assertEqual(OpenScadNode.__module__, 'machinome.node.openscad')
        # The node root exports nothing (`root-cleanup`): the class name
        # read off it is refused naming the one address.
        with self.assertRaises(ImportError) as raised:
            getattr(machinome.node, 'OpenScadNode')
        self.assertIn("its module, 'machinome.node.openscad'",
                      str(raised.exception))

    def test_both_node_types_are_family_leaves(self):
        from machinome.node.openscad import OpenScadNode
        from machinome.node.openscad.leaf import ScadLeafNode
        from machinome.node.solid2 import Solid2Node
        self.assertTrue(issubclass(OpenScadNode, ScadLeafNode))
        self.assertTrue(issubclass(Solid2Node, ScadLeafNode))

    def test_the_former_addresses_are_gone(self):
        for module in ('machinome.scad_engine', 'machinome.open' 'scad',
                       'machinome.open' 'scad.binary',
                       'machinome.open' 'scad.engine'):
            with self.subTest(module=module):
                with self.assertRaises(ModuleNotFoundError):
                    importlib.import_module(module)

    def test_the_viewer_imports_neither_former_address(self):
        tree = ast.parse(
            (ROOT / 'machinome/viewers/openscad.py').read_text())
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
                imported.update(f'{node.module}.{alias.name}'
                                for alias in node.names)
        self.assertFalse(
            {name for name in imported
             if name == 'machinome.scad_engine'
             or name == 'machinome.openscad'
             or name.startswith('machinome.openscad.')})
        self.assertIn('machinome.node.openscad.writer', imported)
        self.assertIn('machinome.node.openscad.binary', imported)


class TheThreeDoorsTest(TestCase):
    """(2.3) SolidPython absent: each family module refuses at its import,
    by its extra, and a project without the family loads none of it."""

    def assert_refused(self, statement, message, extra):
        report, run = reported(statement, absent=('solid2',))
        self.assertIsNotNone(report, run.output)
        self.assertEqual(report['type'], 'ExtraUnavailable', run.output)
        self.assertEqual(report['name'], 'solid2')
        self.assertEqual(report['extra'], extra)
        self.assertEqual(report['message'], message)

    def test_the_package_refuses_naming_the_openscad_extra(self):
        self.assert_refused('import machinome.node.openscad', R1, 'openscad')

    def test_the_viewer_refuses_with_the_package(self):
        self.assert_refused('import machinome.viewers.openscad', R1,
                            'openscad')

    def test_solid2_refuses_naming_the_solid2_extra(self):
        self.assert_refused('import machinome.node.solid2', R2, 'solid2')

    def test_the_class_import_carries_the_refusal(self):
        self.assert_refused('from machinome.node.solid2 import Solid2Node', R2,
                            'solid2')

    def test_the_package_door_carries_the_refusal(self):
        # The node root exports nothing (`root-cleanup`): its door is the
        # submodule, reached through the package, not the class name.
        self.assert_refused('from machinome.node import solid2', R2,
                            'solid2')

    def test_a_project_without_the_family_loads_none_of_it(self):
        import shutil
        import tempfile
        build_dir = tempfile.mkdtemp(prefix='openscad-out-free-')
        self.addCleanup(shutil.rmtree, build_dir, ignore_errors=True)
        run = run_python(
            'import sys, json\n'
            'import machinome.node, machinome.node.base\n'
            'import machinome.core.builder, machinome.test\n'
            'from tests.scad_where_read_project.native import StlBench\n'
            'node = StlBench()\n'
            'node.assemble()\n'
            'node.build_stls()\n'
            'roots = ' + repr(FAMILY_ROOTS) + '\n'
            'print(json.dumps(sorted(name for name in sys.modules\n'
            '    if any(name == root or name.startswith(root + ".")\n'
            '           for root in roots))))\n',
            blocked=False, build_dir=build_dir)
        self.assertEqual(run.returncode, 0, run.output)
        self.assertEqual(json.loads(run.stdout.strip().splitlines()[-1]),
                         [])


#: Ask the expression graph whether SolidPython's animation time is
#: symbolic, before and after importing `machinome.node.solid2`.
ADOPTION = '''
import json, solid2
import machinome.expression_graph as graph
before = graph.symbolic(solid2.get_animation_time())
import machinome.node.solid2
after = graph.symbolic(solid2.get_animation_time())
print(json.dumps([None if before is None else [before.kind, before.text],
                  None if after is None else [after.kind, after.text]]))
'''


class AdoptionTest(TestCase):
    """(2.10) A SolidPython value is adopted through the hook
    `machinome.node.solid2` registers, and only after it is imported."""

    def test_adoption_needs_the_solid2_module(self):
        run = run_python(ADOPTION, blocked=False)
        self.assertEqual(run.returncode, 0, run.output)
        self.assertEqual(json.loads(run.stdout.strip().splitlines()[-1]),
                         [None, ['name', '$t']])

    def test_registering_an_adopter_is_idempotent(self):
        import machinome.expression_graph as graph
        from machinome.node import solid2

        def adopter(value):
            return None

        with patch.object(graph, '_ADOPTERS', graph._ADOPTERS):
            graph.register_adopter(adopter)
            graph.register_adopter(adopter)
            graph.register_adopter(solid2.adopt)
            self.assertEqual(graph._ADOPTERS.count(adopter), 1)
            self.assertEqual(graph._ADOPTERS.count(solid2.adopt), 1)


# Merged from `tests/test_openscad_engine.py` and
# `tests/test_scad_engine_seam.py` (task 9.1): what the former engine
# provided -- adoption, the writer's text, the binary contract -- at its new
# address. The seam's resolution and contract-version cases test a seam
# that no longer exists and are not carried over.

class AdoptTest(TestCase):

    def setUp(self):
        self.adopt = importlib.import_module('machinome.node.solid2').adopt

    def test_solidpythons_animation_time_is_the_name_t(self):
        import solid2
        node = self.adopt(solid2.get_animation_time())
        self.assertEqual((node.kind, node.text), ('name', '$t'))

    def test_text_in_the_language_is_parsed(self):
        from solid2.core.object_base import scad_inline
        node = self.adopt(scad_inline('(other + 2)'))
        self.assertEqual((node.kind, node.op), ('binop', '+'))
        self.assertEqual([(child.kind, child.text) for child in node.children],
                         [('name', 'other'), ('num', '2')])

    def test_text_outside_the_language_is_carried_raw(self):
        from solid2.core.object_base import scad_inline
        node = self.adopt(scad_inline('$mystery ? 1 : 2'))
        self.assertEqual((node.kind, node.text), ('raw', '$mystery ? 1 : 2'))

    def test_anything_else_is_not_adopted(self):
        from machinome.expression_graph import ExpressionNode, symbol
        for value in (1.0, 'x', symbol('$t'), ExpressionNode('name', text='a')):
            with self.subTest(type(value).__name__):
                self.assertIsNone(self.adopt(value))


#: A SolidPython value, in a process that never imported
#: `machinome.node.solid2`, is not an expression.
SOLIDPYTHON_VALUE = '''
import sys
from solid2.core.object_base import scad_inline
import machinome.math as m
print('LOADED', 'machinome.node.solid2' in sys.modules)
try:
    m.sin(scad_inline('$t'))
except Exception as error:
    print('SIN', type(error).__name__, error)
'''


class WithoutTheAdopterTest(TestCase):

    def test_a_solidpython_value_meets_the_existing_refusal(self):
        run = run_python(SOLIDPYTHON_VALUE, blocked=False)
        self.assertEqual(run.returncode, 0, run.output)
        lines = run.stdout.splitlines()
        self.assertIn('LOADED False', lines)
        sin = next(line for line in lines if line.startswith('SIN '))
        self.assertTrue(sin.startswith('SIN TypeError must be real number'),
                        sin)


class NumbersNeverConsultAnAdopterTest(TestCase):

    def test_a_plain_number_never_consults_an_adopter(self):
        import machinome.expression_graph as graph
        import machinome.math as m
        from machinome.expression_graph import as_node, symbolic
        from tests.expression_type_project.machine import SharedMotion
        asked = []

        def counting(value):
            asked.append(value)
            return None

        t = SharedMotion().time
        with patch.object(graph, '_ADOPTERS', (counting,)):
            m.sin(1.0), m.cos(30), m.atan2(1, 2), m.min(1, 2)
            m.max(1.5, 2), m.clamp01(0.5), m.piecewise(0.5, [(0, 0), (1, 1)])
            t + 1, 2 * t, t ** 2, t / 3.0, t < 1, m.sin(t), m.min(t, 1)
            as_node(3), as_node(2.5), symbolic(1), symbolic(0.5)
            self.assertEqual(asked, [])
            # The stub is wired: anything else does consult it.
            symbolic('not a number')
            self.assertEqual(asked, ['not a number'])


class BinaryTest(TestCase):

    def test_the_binary_module_imports_no_solidpython(self):
        tree = ast.parse(
            (ROOT / 'machinome/node/openscad/binary.py').read_text())
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split('.')[0]
                                for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split('.')[0])
        self.assertNotIn('solid2', imported)

    def test_the_binary_contract_refuses_unchanged(self):
        binary = importlib.import_module('machinome.node.openscad.binary')
        binary.openscad_binary.cache_clear()
        self.addCleanup(binary.openscad_binary.cache_clear)
        with patch('machinome.node.openscad.binary.shutil.which',
                   return_value=None):
            with self.assertRaises(binary.OpenScadUnavailable) as raised:
                binary.require_openscad(
                    'node housing (FacetedBox)',
                    'its STL is rendered from SCAD by OpenSCAD')
        self.assertEqual(
            str(raised.exception),
            'node housing (FacetedBox) requires the OpenSCAD binary because '
            'its STL is rendered from SCAD by OpenSCAD; install OpenSCAD and '
            "ensure 'openscad' is on PATH")

    def test_the_refusal_names_an_alternative_unchanged(self):
        from machinome.node.openscad.binary import OpenScadUnavailable
        error = OpenScadUnavailable('node housing (FacetedBox)',
                                    'its STL is rendered from SCAD by '
                                    'OpenSCAD', 'use --renderer web')
        self.assertEqual(
            str(error),
            'node housing (FacetedBox) requires the OpenSCAD binary because '
            'its STL is rendered from SCAD by OpenSCAD; install OpenSCAD and '
            "ensure 'openscad' is on PATH, or use --renderer web")


class ScadTextTest(TestCase):
    """The writer writes the SCAD text of the core's presentation
    description, exactly as SolidPython renders the calls the core used to
    make."""

    def setUp(self):
        self.writer = importlib.import_module('machinome.node.openscad.writer')
        self.p = importlib.import_module('machinome.node.presentation')

    def test_a_placed_coloured_import_is_solidpythons_rendering(self):
        from solid2 import color, import_stl, rotate, scad_render, translate
        p = self.p
        description = p.Rotate(30.0, [0, 0, 1], p.Translate(
            [1, 2.5, 0], p.Color((1.0, 0.5, 0.0), 1,
                                 p.ArtifactImport('a/b.stl'))))
        expected = scad_render(rotate(30.0, [0, 0, 1])(translate(
            [1, 2.5, 0])(color([1.0, 0.5, 0.0], 1)(import_stl('a/b.stl')))))
        self.assertEqual(self.writer.scad_text(description), expected)
        self.assertEqual(
            expected,
            'rotate(a = 30.0, v = [0, 0, 1]) {\n'
            '\ttranslate(v = [1, 2.5, 0]) {\n'
            '\t\tcolor(alpha = 1, c = [1.0, 0.5, 0.0]) {\n'
            '\t\t\timport(file = "a/b.stl", origin = [0, 0]);\n'
            '\t\t}\n\t}\n}\n')

    def test_a_symbolic_angle_is_written_as_its_closed_text(self):
        from machinome.expression_graph import get_animation_time
        p = self.p
        text = self.writer.scad_text(p.Rotate(
            get_animation_time() * 360, [0, 0, 1], p.ArtifactImport('a.stl')))
        self.assertIn('rotate(a = ($t * 360), v = [0, 0, 1])', text)

    def test_a_union_of_none_is_an_empty_union(self):
        self.assertEqual(self.writer.scad_text(self.p.Union(())),
                         'union();\n')

    def test_a_union_of_two_is_solidpythons(self):
        from solid2 import import_stl, scad_render, union
        p = self.p
        text = self.writer.scad_text(p.Union((p.ArtifactImport('a.stl'),
                                              p.ArtifactImport('b.stl'))))
        self.assertEqual(text, scad_render(union()(
            [import_stl('a.stl'), import_stl('b.stl')])))

    def test_fn_prefixes_the_text(self):
        text = self.writer.scad_text(self.p.ArtifactImport('a.stl'), fn=24)
        self.assertTrue(text.startswith('$fn = 24;\n\nimport(file = "a.stl"'),
                        text)

    def test_authored_geometry_is_written_as_authored(self):
        from solid2 import cube, import_stl, scad_render
        geometry = cube(1) + import_stl('vendor/external.stl')
        self.assertEqual(
            self.writer.scad_text(self.p.Authored(geometry)),
            scad_render(geometry))
        self.assertIn('import(file = "vendor/external.stl"',
                      self.writer.scad_text(self.p.Authored(geometry)))


class CountingWriterTest(TestCase):
    """What the family is asked for: SCAD text once per stale family leaf a
    build materializes and never for `assemble()`; the binary for a stale
    `Solid2Node`'s STL and for the snapshot renderer."""

    def setUp(self):
        import os
        import shutil
        import tempfile
        writer = importlib.import_module('machinome.node.openscad.writer')
        binary = importlib.import_module('machinome.node.openscad.binary')
        self.texts, self.binaries = [], []
        real_text, real_binary = writer.scad_text, binary.require_openscad

        def scad_text(description, fn=None):
            self.texts.append(description)
            return real_text(description, fn=fn)

        def require_openscad(needed_by, reason, alternative=None):
            self.binaries.append(needed_by)
            return real_binary(needed_by, reason, alternative)

        for patched in (patch.object(writer, 'scad_text', scad_text),
                        patch.object(binary, 'require_openscad',
                                     require_openscad)):
            patched.start()
            self.addCleanup(patched.stop)
        self.build_dir = tempfile.mkdtemp(prefix='scad-counting-')
        self.addCleanup(shutil.rmtree, self.build_dir, ignore_errors=True)
        environment = patch.dict(os.environ,
                                 {'SOLID_BUILD_DIR': self.build_dir})
        environment.start()
        self.addCleanup(environment.stop)

    def machine(self):
        from tests.scad_where_read_project.machine import Machine
        node = Machine()
        node._prepare()
        fine = next(child for child in node.children
                    if type(child).__name__ == 'FineCylinder')
        return node, fine

    def test_scad_text_once_per_stale_family_leaf_never_by_assemble(self):
        node, _ = self.machine()
        self.assertEqual(len(self.texts), 1)
        node.assemble()
        self.assertEqual(len(self.texts), 1)

    def test_the_binary_for_a_stale_solid2nodes_stl_and_the_renderer(self):
        import os
        from types import SimpleNamespace
        from unittest.mock import MagicMock
        from machinome.node.base import StlRenderStart
        from machinome.viewers.openscad import OpenScadRenderer
        node, fine = self.machine()
        with patch('machinome.node.openscad.leaf.Popen',
                   return_value=MagicMock(pid=os.getpid())):
            with self.assertRaises(StlRenderStart) as started:
                fine.generate_stl()
        started.exception._discard()
        self.assertEqual(self.binaries,
                         ['node FineCylinder (FineCylinder)'])

        args = SimpleNamespace(camera=None, autocenter=False, viewall=False,
                               imgsize='64x48', projection=None,
                               colorscheme=None, preview=False, view=None)
        runner = MagicMock(return_value=SimpleNamespace(stdout='',
                                                        stderr=''))
        OpenScadRenderer().render(node, args, 'out.png', runner)
        runner.assert_called_once()
        self.assertEqual(self.binaries[-1], 'the OpenSCAD snapshot renderer')
