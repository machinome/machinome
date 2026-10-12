# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The table of supported node types, `machinome.node.supported` (OpenSpec
change `openscad-out`, design.md Decision 6; capabilities `cli` and
`kernel-extras`).

One table names the node types the core supports: the class names the node
root resolves and the commands that need its module. Its provisional renderer
column went with the change `viewer-seam`: viewers are providers behind the
seam `machinome.viewer`, and the table names none. The node root and the CLI
read it, and no other module of the core spells a node type's module. A node
type's address and extra are not stored: they are `machinome.node.<key>` and
`machinome[<key>]`. The
FreeCAD node type, which joined the repository from a repository of its own,
is its last row (OpenSpec change `join-freecad`).
"""

import ast
import importlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
from unittest import TestCase

from tests.brep_engine_absent import run_python

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = Path(__file__).resolve().parents[3]
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
    'freecad': ('FreeCADAssemblyNode', 'FreeCADJoint'),
}

#: The modules that used to spell a node type's module, and must not.
READERS = ('machinome/cli.py', 'machinome/manager/import_step.py',
           'machinome/manager/snapshot.py', 'machinome/manager/new.py')

NODE_MODULE = re.compile(
    r'machinome\.node\.(' + '|'.join(NODE_TYPES) + r')\b')


def supported():
    return importlib.import_module('machinome.node.supported')


class TheTableTest(TestCase):

    def test_it_names_the_nine_node_types_and_their_classes(self):
        table = supported().NODE_TYPES
        self.assertEqual(list(table), list(NODE_TYPES))
        for key, classes in NODE_TYPES.items():
            with self.subTest(key=key):
                self.assertEqual(table[key].classes, classes)

    def test_the_root_refuses_each_class_naming_its_module(self):
        # The node root exports nothing (`root-cleanup`): each class name of
        # a row is defined by `machinome.node.<key>` and refused at the root
        # naming it.
        import machinome.node
        self.assertEqual(machinome.node.__all__, [])
        for key, classes in NODE_TYPES.items():
            module = importlib.import_module(f'machinome.node.{key}')
            for name in classes:
                with self.subTest(name=name):
                    # The FreeCAD package defines its classes in its module
                    # `adapter` (`join-freecad`).
                    self.assertIn(getattr(module, name).__module__,
                                  (f'machinome.node.{key}',
                                   f'machinome.node.{key}.adapter'))
                    with self.assertRaises(ImportError) as raised:
                        getattr(machinome.node, name)
                    self.assertIn(
                        f'`from machinome.node.{key} import {name}`',
                        str(raised.exception))

    def test_the_table_names_no_viewer(self):
        import dataclasses
        table = supported()
        self.assertEqual([field.name for field in
                          dataclasses.fields(table.NodeType)],
                         ['classes', 'commands'])
        self.assertFalse(hasattr(table, 'DEFAULT_RENDERER'))
        self.assertFalse(hasattr(table, 'renderer'))
        self.assertNotIn('renderer', SUPPORTED.read_text().lower())

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
        self.assertEqual(defined, {'NodeType', 'NODE_TYPES', 'absent',
                                   'load', 'needed_by'})

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
        for call in ("load('open' 's' 'cad')",):
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


#: Drop one node package's directory from the path, as an install without
#: its distribution, then pass one door and report what it raised.
ABSENT_DOOR = '''
import json, os, sys
absent = os.path.realpath({directory!r})
sys.path[:] = [entry for entry in sys.path
               if os.path.realpath(entry or os.curdir) != absent]
import machinome.node
result = None
try:
{door}
except ImportError as raised:
    print(json.dumps([type(raised).__name__, raised.name,
                      getattr(raised, 'extra', None), str(raised)]))
else:
    print(json.dumps(['passed', result]))
'''


def package_directory(key):
    """The directory of node type `key`'s distribution."""
    return REPOSITORY / 'packages' / f'machinome-node-{key}'


def refused(key):
    """What a door reports when node type `key`'s package is absent: the
    refusal built from the key, as `machinome.node.supported.absent`."""
    classes = ', '.join(NODE_TYPES[key])
    return ['ExtraUnavailable', f'machinome.node.{key}', key,
            f'the {key} node type ({classes}) needs machinome.node.{key}, '
            'which is not installed; install it with '
            f'\'pip install "machinome[{key}]"\'']


def doors(key):
    """The four doors of node type `key`: its module, its first class from
    its module, the module from the node root, and the root's attribute."""
    return {
        'import': f'import machinome.node.{key}',
        'from-module': f'from machinome.node.{key} import {NODE_TYPES[key][0]}',
        'from-root': f'from machinome.node import {key}',
        'hasattr': f"result = hasattr(machinome.node, '{key}')",
    }


#: Each node package dropped, by its node type's key, and the doors that
#: refuse it naming that key: its own four, and, for the OpenSCAD node
#: package, the OpenSCAD viewer that draws with it, resolved through the
#: seam of viewers (`viewer-seam`), and the node type built over the package
#: (`cut-the-mesh-nodes`).
ABSENCES = {
    'step': doors('step'),
    'open' 's' 'cad': {
        **doors('open' 's' 'cad'),
        'viewer': 'import machinome.viewer as viewers\n'
                  "viewers.viewer('open' 's' 'cad')",
        'solid2': 'from machinome.node.solid2 import Solid2Node',
    },
    'solid2': doors('solid2'),
    'jscad': doors('jscad'),
    'stl': doors('stl'),
    'freecad': doors('freecad'),
}

#: A project of one SolidPython part, which `machinome snapshot` renders
#: through the OpenSCAD viewer.
PROJECT = {
    'pyproject.toml': '[tool.machinome]\nmodel = "demo:Demo"\n',
    'demo.py': textwrap.dedent('''\
        from solid2 import cube
        from machinome.node.solid2 import Solid2Node


        class Demo(Solid2Node):
            def render(self):
                return cube([2, 3, 4])
        '''),
}

#: `machinome snapshot` with one node package's directory dropped from the
#: path, as an install without its distribution; the arguments follow.
ABSENT_SNAPSHOT = '''
import os, sys
absent = os.path.realpath({directory!r})
sys.path[:] = [entry for entry in sys.path
               if os.path.realpath(entry or os.curdir) != absent]
sys.argv = ['machinome', 'snapshot', *{arguments!r}]
from machinome.cli import manage
manage()
'''


class AbsentPackageTest(TestCase):
    """(`cut-the-brep-nodes`, ADR-184; `cut-the-mesh-nodes`) A node type
    whose distribution is not installed is refused by its extra at every
    door, as an absent kernel is, and so is everything reached through it:
    the OpenSCAD viewer, the snapshot command and `Solid2Node`
    with the OpenSCAD node package absent. The absence is stood in for by
    the package's directory dropped from `sys.path` before `machinome` is
    imported, which the editable install allows; an uninstalled wheel is the
    design's probe 2.
    """

    def passed(self, key, door):
        code = ABSENT_DOOR.format(directory=str(package_directory(key)),
                                  door=textwrap.indent(door, '    '))
        run = run_python(code, blocked=False, absent=())
        self.assertEqual(run.returncode, 0, run.output)
        return json.loads(run.stdout.strip().splitlines()[-1])

    def test_every_door_refuses_the_absent_package_by_its_extra(self):
        for key, named in ABSENCES.items():
            for name, door in named.items():
                with self.subTest(package=key, door=name):
                    self.assertEqual(self.passed(key, door), refused(key))

    def test_the_other_node_packages_still_import(self):
        for key, other in (('step', 'cadquery'), ('open' 's' 'cad', 'stl')):
            with self.subTest(package=key, other=other):
                self.assertEqual(
                    self.passed(key, f'import machinome.node.{other}\n'
                                     'result = machinome.node.'
                                     f'{other}.__name__'),
                    ['passed', f'machinome.node.{other}'])

    def test_the_snapshot_refuses_an_absent_openscad_package(self):
        project = tempfile.mkdtemp(prefix='absent-snapshot-')
        self.addCleanup(shutil.rmtree, project, ignore_errors=True)
        for name, text in PROJECT.items():
            Path(project, name).write_text(text)
        image = os.path.join(project, 'x.png')
        run = run_python(
            ABSENT_SNAPSHOT.format(
                directory=str(package_directory('open' 's' 'cad')),
                arguments=['-o', image]),
            blocked=False, absent=(), cwd=project)
        self.assertEqual(run.returncode, 1, run.output)
        self.assertEqual(
            run.stderr.strip().splitlines()[-1],
            'Error: machinome snapshot --viewer open' 's' 'cad needs the '
            'open' 's' 'cad extra: ' + refused('open' 's' 'cad')[3]
            + '; or use --viewer web', run.output)
        self.assertFalse(os.path.exists(image))


class TheFreeCADTestsSkipWithoutARuntimeTest(TestCase):
    """(`join-freecad`, capability `native-freecad-assembly`) Where
    `MACHINOME_FREECAD_ROOT` is not set, a FreeCAD node package test module
    is reported skipped, naming the variable, and none of its tests fails."""

    def test_the_public_module_skips_naming_the_variable(self):
        environment = {name: value for name, value in os.environ.items()
                       if name != 'MACHINOME_FREECAD_ROOT'}
        run = subprocess.run(
            [sys.executable, '-m', 'pytest', '-q', '-rs',
             '-p', 'no:cacheprovider', 'tests/test_freecad_public.py'],
            cwd=ROOT, env=environment, capture_output=True, text=True,
            timeout=300)
        output = run.stdout + run.stderr
        # A module skipped whole collects no test, which pytest reports with
        # its exit status 5, never 1.
        self.assertIn(run.returncode, (0, 5), output)
        self.assertIn('1 skipped', output)
        self.assertIn('MACHINOME_FREECAD_ROOT', output)
        self.assertNotIn('failed', output)
        self.assertNotIn('error', output)
