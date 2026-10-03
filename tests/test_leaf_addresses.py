# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Each leaf type is one module under `machinome.node` (OpenSpec change
`lean-install`, capability `node-model`), and the package extends its path
only to portions that are not a second copy of it.

The addresses are the final ones of the one-path rule: a node type at
`machinome.node.<nodetype>`. The former package, `machinome.node.adapters`,
is dissolved and refuses every spelling under it naming the rule, so a
project that has not migrated fails at its import line with the line to
write. The root's spellings (`from machinome.node import StepNode`) do not
move in this change.

The path extension is observed in subprocesses whose `sys.path` carries a
scratch directory after the framework: one holding a second copy of the
core (its own `machinome/__init__.py`), whose modules must never resolve,
and one in a satellite's shape (no `__init__.py` of the core's), whose
modules must.
"""

import importlib
import os
import subprocess
import sys
import tempfile
from unittest import TestCase

import machinome.node

from .import_probe import probe

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: The `node-model` table: each leaf module and the names it defines,
#: spelled out here rather than read from the package under test.
LEAF_MODULES = {
    'machinome.node.cadquery': ('CadQueryNode',),
    'machinome.node.build123d': ('Build123dNode', 'Build123dSheetNode'),
    'machinome.node.step': ('StepNode',),
    'machinome.node.molejo': ('MolejoNode',),
    'machinome.node.solid2': ('Solid2Node',),
    'machinome.node.openscad': ('OpenScadNode',),
    'machinome.node.jscad': ('JScadNode',),
    'machinome.node.stl': ('StlNode',),
}

#: Names a leaf module defines that the root does not export.
MODULE_ONLY = {
    'machinome.node.step': ('StepAssembly', 'solids_from_faces',
                            'cached_document'),
    'machinome.node.build123d': ('svg_regions', 'svg_triangles',
                                 'SVG_REDUCER_CONTRACT'),
}

#: Every former spelling the refusal must answer, with the module whose
#: name it must not have imported by the attempt.
FORMER = (
    'from machinome.node.adapters.step import StepAssembly',
    'from machinome.node.adapters import step',
    'import machinome.node.adapters.cadquery',
)


class LeafAddressTest(TestCase):
    """(2.7) Each leaf at its module, the root resolving the same object."""

    def test_every_leaf_is_defined_at_its_module(self):
        for module_name, names in LEAF_MODULES.items():
            module = importlib.import_module(module_name)
            for name in names:
                with self.subTest(name=name):
                    value = getattr(module, name)
                    self.assertEqual(value.__module__, module_name)
                    self.assertIs(getattr(machinome.node, name), value)

    def test_the_names_only_a_module_answers_are_there(self):
        for module_name, names in MODULE_ONLY.items():
            module = importlib.import_module(module_name)
            for name in names:
                with self.subTest(name=name):
                    self.assertTrue(hasattr(module, name))

    def test_the_former_package_holds_only_its_refusal(self):
        directory = os.path.join(ROOT, 'machinome', 'node', 'adapters')

        self.assertEqual(
            sorted(entry for entry in os.listdir(directory)
                   if entry != '__pycache__'),
            ['__init__.py'])

    def test_every_former_spelling_is_refused_naming_the_rule(self):
        for spelling in FORMER:
            with self.subTest(spelling=spelling):
                result = probe(
                    'import sys\n'
                    'try:\n'
                    f'    {spelling}\n'
                    'except ImportError as refused:\n'
                    "    print(type(refused).__name__, '|', refused)\n"
                    'else:\n'
                    "    print('NO_ERROR')\n")
                self.assertEqual(result.status, 0, result.stderr)
                reported = result.stdout.strip()
                self.assertTrue(reported.startswith('ImportError |'),
                                reported)
                self.assertIn("'machinome.node.adapters' was dissolved",
                              reported)
                self.assertIn("'machinome.node.<x>'", reported)
                self.assertIn('machinome.node.build123d', reported)
                self.assertIn(
                    '`from machinome.node.step import StepAssembly`',
                    reported)
                self.assertFalse(result.imported('machinome.node.step'))
                self.assertFalse(result.imported('machinome.node.cadquery'))

    def test_two_types_in_one_module_stay_distinct(self):
        from machinome.node.build123d import Build123dNode, Build123dSheetNode

        self.assertFalse(issubclass(Build123dNode, Build123dSheetNode))
        self.assertFalse(issubclass(Build123dSheetNode, Build123dNode))


def write(root, relative, text=''):
    path = os.path.join(root, relative)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as handle:
        handle.write(text)


def import_after(scratch, *modules):
    """Import each module in a fresh interpreter whose `sys.path` carries
    the framework, then `scratch`; report each as `OK <file>` or
    `FAILED <error>`."""
    code = ('import importlib\n'
            f'for name in {modules!r}:\n'
            '    try:\n'
            '        module = importlib.import_module(name)\n'
            '    except ImportError as failed:\n'
            "        print(name, 'FAILED', failed)\n"
            '    else:\n'
            "        print(name, 'OK', module.__file__)\n")
    completed = subprocess.run(
        [sys.executable, '-c', code], cwd=ROOT, capture_output=True,
        text=True, timeout=120,
        env=dict(os.environ, PYTHONPATH=os.pathsep.join([ROOT, scratch])))
    assert completed.returncode == 0, completed.stderr
    return dict(line.split(' ', 1) for line in completed.stdout.splitlines())


class PathExtensionTest(TestCase):
    """(2.8) `machinome` and `machinome.node` admit a portion that ships no
    `__init__.py` of their own, and never a second copy of the core."""

    def setUp(self):
        scratch = tempfile.TemporaryDirectory(prefix='path-extension-')
        self.addCleanup(scratch.cleanup)
        self.scratch = scratch.name

    def test_a_second_copy_of_the_core_is_never_merged(self):
        write(self.scratch, 'machinome/__init__.py')
        write(self.scratch, 'machinome/node/__init__.py')
        write(self.scratch, 'machinome/stray.py')
        write(self.scratch, 'machinome/node/stray.py')

        imported = import_after(self.scratch, 'machinome.stray',
                                'machinome.node.stray')

        for name in ('machinome.stray', 'machinome.node.stray'):
            with self.subTest(module=name):
                self.assertTrue(imported[name].startswith('FAILED'),
                                imported[name])

    def test_a_satellite_portion_is_found(self):
        write(self.scratch, 'machinome/node/portion.py')
        write(self.scratch, 'machinome/extra_portion/__init__.py')

        imported = import_after(self.scratch, 'machinome.node.portion',
                                'machinome.extra_portion')

        for name, relative in (
                ('machinome.node.portion', 'machinome/node/portion.py'),
                ('machinome.extra_portion',
                 'machinome/extra_portion/__init__.py')):
            with self.subTest(module=name):
                self.assertEqual(
                    imported[name],
                    'OK ' + os.path.join(self.scratch, relative))

    def test_the_framework_resolves_from_its_own_checkout(self):
        imported = import_after(self.scratch, 'machinome.node')

        self.assertEqual(
            imported['machinome.node'],
            'OK ' + os.path.join(ROOT, 'machinome', 'node', '__init__.py'))
