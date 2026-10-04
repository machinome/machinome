# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The table of supported node types, `machinome.node.supported` (OpenSpec
change `openscad-out`, design.md Decision 6; capabilities `cli` and
`kernel-extras`).

One table names the node types the core supports: the class names the node
root resolves, the renderer a node type contributes (a provisional column,
which the viewer cycle removes) and the commands that need its module. The
node root, the CLI and the snapshot command read it, and no other module of
the core spells a node type's module. A node type's address and extra are
not stored: they are `machinome.node.<key>` and `machinome[<key>]`.
"""

import ast
import importlib
import json
import re
from pathlib import Path
from unittest import TestCase

from tests.exact_engine_absent import run_python

ROOT = Path(__file__).resolve().parents[1]
SUPPORTED = ROOT / 'machinome' / 'node' / 'supported.py'

#: The node types and the class names each contributes, as the node root's
#: export table resolved them before the table existed (a16d45a).
NODE_TYPES = {
    'cadquery': ('CadQueryNode',),
    'build123d': ('Build123dNode', 'Build123dSheetNode'),
    'step': ('StepNode',),
    'molejo': ('MolejoNode',),
    'solid2': ('Solid2Node',),
    'openscad': ('OpenScadNode',),
    'jscad': ('JScadNode',),
    'stl': ('StlNode',),
}

#: The modules that used to spell a node type's module, and must not.
READERS = ('machinome/cli.py', 'machinome/manager/import_step.py',
           'machinome/manager/snapshot.py', 'machinome/manager/new.py')

NODE_MODULE = re.compile(
    r'machinome\.node\.(' + '|'.join(NODE_TYPES) + r')\b')


def supported():
    return importlib.import_module('machinome.node.supported')


class TheTableTest(TestCase):

    def test_it_names_the_eight_node_types_and_their_classes(self):
        table = supported().NODE_TYPES
        self.assertEqual(list(table), list(NODE_TYPES))
        for key, classes in NODE_TYPES.items():
            with self.subTest(key=key):
                self.assertEqual(table[key].classes, classes)

    def test_the_root_exports_the_same_objects(self):
        import machinome.node
        for key, classes in NODE_TYPES.items():
            module = importlib.import_module(f'machinome.node.{key}')
            for name in classes:
                with self.subTest(name=name):
                    self.assertIn(name, machinome.node.__all__)
                    self.assertIs(getattr(machinome.node, name),
                                  getattr(module, name))

    def test_one_renderer_is_contributed_and_it_is_the_default(self):
        table = supported()
        names = [name for node_type in table.NODE_TYPES.values()
                 for name, _ in node_type.renderers]
        self.assertEqual(names, ['open' 's' 'cad'])
        self.assertEqual(table.DEFAULT_RENDERER, 'open' 's' 'cad')
        renderer = table.renderer('open' 's' 'cad')
        self.assertEqual(type(renderer).__module__,
                         'machinome.viewers.open' 's' 'cad')
        self.assertTrue(callable(renderer.present))
        self.assertTrue(callable(renderer.render))

    def test_the_command_column_agrees_with_the_cli(self):
        from machinome import cli
        self.assertEqual(supported().needed_by('import-step'), 'step')
        self.assertIsNone(supported().needed_by('build'))
        self.assertEqual(cli.COMMANDS['import-step'][2], 'step')
        for name, (_, _, needs) in cli.COMMANDS.items():
            with self.subTest(command=name):
                self.assertEqual(needs, supported().needed_by(name))

    def test_no_reader_spells_a_node_types_module(self):
        for relative in READERS:
            with self.subTest(module=relative):
                text = (ROOT / relative).read_text()
                self.assertEqual(NODE_MODULE.findall(text), [])

    def test_the_module_defines_only_the_table_and_its_readers(self):
        tree = ast.parse(SUPPORTED.read_text())
        defined = set()
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                defined.add(node.name)
            elif isinstance(node, ast.Assign):
                defined.update(target.id for target in node.targets
                               if isinstance(target, ast.Name))
            elif isinstance(node, ast.AnnAssign):
                defined.add(node.target.id)
        self.assertEqual(defined, {'NodeType', 'NODE_TYPES',
                                   'DEFAULT_RENDERER', 'load', 'renderer',
                                   'needed_by'})

    def test_importing_it_imports_no_node_type(self):
        run = run_python(
            'import sys, json\n'
            'import machinome.node.supported\n'
            'print(json.dumps(sorted(name for name in sys.modules\n'
            '    if name.split(".")[:2] == ["machinome", "node"]\n'
            '    and len(name.split(".")) > 2\n'
            '    and name.split(".")[2] in ' + repr(tuple(NODE_TYPES)) +
            ')))\n', blocked=False)
        self.assertEqual(run.returncode, 0, run.output)
        self.assertEqual(json.loads(run.stdout.strip().splitlines()[-1]),
                         [])


#: Load a node type through the table and report what it raised.
LOAD = '''
import json
from machinome.node import supported
try:
    supported.{call}
except ImportError as raised:
    print(json.dumps([type(raised).__name__, raised.name,
                      getattr(raised, 'extra', None), str(raised)]))
else:
    print(json.dumps(None))
'''


class LoadRefusesTest(TestCase):

    def loaded(self, call, absent):
        run = run_python(LOAD.format(call=call), absent=absent)
        self.assertEqual(run.returncode, 0, run.output)
        return json.loads(run.stdout.strip().splitlines()[-1])

    def test_a_node_type_that_cannot_be_found_is_refused_by_its_extra(self):
        for call in ("load('open' 's' 'cad')", "renderer('open' 's' 'cad')"):
            with self.subTest(call=call):
                self.assertEqual(
                    self.loaded(call, ('machinome.node.open' 's' 'cad',)),
                    ['ExtraUnavailable', 'machinome.node.open' 's' 'cad',
                     'open' 's' 'cad',
                     'the open' 's' 'cad node type (OpenScadNode) needs '
                     'machinome.node.open' 's' 'cad, which is not '
                     'installed; install it with '
                     '\'pip install "machinome[open' 's' 'cad]"\''])

    def test_a_modules_own_refusal_passes_unmodified(self):
        self.assertEqual(
            self.loaded("load('solid2')", ('solid2',)),
            ['ExtraUnavailable', 'solid2', 'solid2',
             'machinome.node.solid2 (Solid2Node) needs solid2, which is not '
             'installed; install it with \'pip install "machinome[solid2]"\''])

    def test_a_present_node_type_is_its_module(self):
        module = supported().load('stl')
        self.assertIs(module, importlib.import_module('machinome.node.stl'))
