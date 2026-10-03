# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The core's symbolic value is its own type (OpenSpec change
`expression-type`, capability `motion-expression-sharing`, "A symbolic value
is the framework's own type").

Read from the source: no module outside the OpenSCAD engine's package
imports a SolidPython expression name, and the modules that still import
SolidPython at all are exactly the SCAD presentation, the two OpenSCAD leaves
and the project template, which the campaign's later cycles move. Read from
a fresh interpreter: importing the vocabulary imports no SolidPython. Read
from the values: time, a driver read and what `machinome.math` returns are
`GraphValue`s with no SolidPython class in their ancestry, and asking one
for its truth raises machinome's own refusal.
"""

import ast
import os
import re
import subprocess
import sys
from pathlib import Path
from unittest import TestCase

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'machinome'
ENGINE_PACKAGE = PACKAGE / 'openscad'
ENGINE_NAME = re.compile(r'^machinome\.openscad(\.\w+)*$')

#: The SolidPython names that make a value an expression.
EXPRESSION_NAMES = {'OpenSCADConstant', 'scad_inline', 'ScadValue',
                    'get_animation_time'}

#: Every core module that still imports SolidPython, and the campaign
#: cycle that removes it (`workflow/ongoing/lean-core.md`, "Layers").
SOLID2_IMPORTERS = {
    'machinome/node/base.py',        # cycle 6, the SCAD presentation
    'machinome/node/operations.py',  # cycle 6, the SCAD presentation
    'machinome/node/internal.py',    # cycle 6, the SCAD presentation
    'machinome/node/flexible.py',    # cycle 6, the SCAD presentation
    'machinome/node/solid2.py',      # cycle 7, the Solid2Node leaf
    'machinome/node/openscad.py',    # cycle 7, the OpenScadNode leaf
    'machinome/manager/templates/project/root/__init__.py',  # cycle 8
}

#: The core modules that reach the engine's package directly, outside the
#: seam `machinome.scad_engine`, for the OpenSCAD binary locator: the SCAD
#: presentation and the runner, which cycles 6 and 7 move behind the seam.
BINARY_REACHES = {
    'machinome/node/base.py',         # cycles 6-7
    'machinome/node/solid2.py',       # cycle 7
    'machinome/viewers/openscad.py',  # cycle 7
    'machinome/manager/snapshot.py',  # cycle 7
}


def core_modules():
    """Every module of the core: everything under `machinome/` outside the
    OpenSCAD engine's package."""
    for path in sorted(PACKAGE.rglob('*.py')):
        if ENGINE_PACKAGE in path.parents:
            continue
        yield path.relative_to(ROOT).as_posix(), ast.parse(path.read_text())


def solid2_imports(tree):
    """`(module, names)` for every import statement naming a `solid2`
    module, anywhere in the module (a lazy import included)."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == 'solid2' or alias.name.startswith('solid2.'):
                    yield alias.name, set()
        elif (isinstance(node, ast.ImportFrom) and node.level == 0
              and (node.module == 'solid2'
                   or node.module.startswith('solid2.'))):
            yield node.module, {alias.name for alias in node.names}


def names_the_engine_package(tree):
    """Whether a module imports, or spells by name, `machinome.openscad`
    or a module of it."""
    for node in ast.walk(tree):
        if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                and ENGINE_NAME.match(node.value)):
            return True
        if isinstance(node, ast.Import):
            if any(alias.name == 'machinome.openscad'
                   or alias.name.startswith('machinome.openscad.')
                   for alias in node.names):
                return True
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            if (node.module == 'machinome.openscad'
                    or node.module.startswith('machinome.openscad.')):
                return True
            if node.module == 'machinome' and any(
                    alias.name == 'openscad' for alias in node.names):
                return True
    return False


class NoExpressionImportTest(TestCase):

    def test_no_core_module_imports_a_solidpython_expression_name(self):
        offending = {}
        for path, tree in core_modules():
            for module, names in solid2_imports(tree):
                taken = names & EXPRESSION_NAMES
                if module.startswith('solid2.core.object_base'):
                    taken = taken | {module}
                if taken:
                    offending.setdefault(path, set()).update(taken)

        self.assertEqual(offending, {})

    def test_the_remaining_solid2_importers_are_presentation_leaves_and_template(self):
        importing = {path for path, tree in core_modules()
                     if any(True for _ in solid2_imports(tree))}

        self.assertEqual(importing, SOLID2_IMPORTERS)

    def test_only_presentation_and_runner_reach_the_binary_locator(self):
        reaching = {path for path, tree in core_modules()
                    if names_the_engine_package(tree)}

        self.assertEqual(reaching,
                         BINARY_REACHES | {'machinome/scad_engine.py'})


#: Import one module in a fresh interpreter and report every `solid2`
#: module it left loaded.
IMPORTS = '''
import sys
import {module}
print(sorted(name for name in sys.modules
             if name == 'solid2' or name.startswith('solid2.')))
'''


class ImportsNoSolidPythonTest(TestCase):

    def assert_no_solid2(self, module):
        completed = subprocess.run(
            [sys.executable, '-c', IMPORTS.format(module=module)],
            cwd=ROOT, capture_output=True, text=True, timeout=120,
            env=dict(os.environ, PYTHONPATH=str(ROOT)))
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout.strip().splitlines()[-1], '[]')

    def test_importing_the_vocabulary_imports_no_solidpython(self):
        self.assert_no_solid2('machinome.math')

    def test_importing_the_expression_graph_imports_no_solidpython(self):
        self.assert_no_solid2('machinome.expression_graph')


def _solid2_ancestors(value):
    return [cls for cls in type(value).__mro__
            if cls.__module__ == 'solid2' or cls.__module__.startswith('solid2.')]


class TheTypeTest(TestCase):

    def setUp(self):
        from machinome.expression_graph import GraphValue
        from tests.expression_type_project.machine import SharedMotion
        self.GraphValue = GraphValue
        self.time = SharedMotion().time

    def test_time_a_driver_and_math_are_the_cores_own_type(self):
        import machinome.math as m
        from machinome.node.qualified import DriverToken
        values = {'time': self.time, 'driver': DriverToken('drive'),
                  'sin': m.sin(self.time * 360)}
        for name, value in values.items():
            with self.subTest(name):
                self.assertIsInstance(value, self.GraphValue)
                self.assertEqual(_solid2_ancestors(value), [])

    def test_truth_is_refused_by_machinomes_own_error(self):
        from machinome.expression_graph import SymbolicTruthError
        self.assertTrue(issubclass(SymbolicTruthError, Exception))
        self.assertFalse(issubclass(SymbolicTruthError, TypeError))
        with self.assertRaises(SymbolicTruthError):
            bool(self.time < 1)
        with self.assertRaises(SymbolicTruthError):
            if self.time < 0.5:
                pass

    def test_an_except_typeerror_does_not_swallow_the_refusal(self):
        from machinome.expression_graph import SymbolicTruthError
        with self.assertRaises(SymbolicTruthError):
            try:
                bool(self.time > 0)
            except TypeError:
                pass

    def test_the_refusal_is_bounded_and_names_the_remedy(self):
        from machinome.expression_graph import SymbolicTruthError
        x = self.time
        for i in range(10000):
            x = x + i
        with self.assertRaises(SymbolicTruthError) as raised:
            bool(x < 1)
        message = str(raised.exception)
        self.assertLess(len(message), 600)
        self.assertIn('machinome.math', message)
        for remedy in ('min', 'max', 'clamp', 'sign', 'driver'):
            self.assertIn(remedy, message)

    def test_unary_plus_hash_and_iteration_raise_typeerror(self):
        t = self.time
        for name, attempt in {'+t': lambda: +t, 'hash': lambda: hash(t),
                              'iter': lambda: iter(t)}.items():
            with self.subTest(name):
                with self.assertRaises(TypeError):
                    attempt()
