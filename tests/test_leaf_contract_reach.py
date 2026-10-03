# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""No leaf that leaves the core reaches a private of it (OpenSpec change
`leaf-contract`, capability `leaf-contract`).

Read from the source, not imported: the stand-ins of
`tests/contract_package/` and the five adapters that leave the core when
the node packages are cut (`cadquery`, `build123d`, `build123d_sheet`,
`step`, `molejo`) may not import a private name from `machinome` or one of
its internal modules, define a method that overrides a private member of
a leaf base, or read one through `self`. And a leaving adapter imports
from the core only the modules the contract declares.
"""

import ast
import glob
import os
from unittest import TestCase

BASEDIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(BASEDIR)
ADAPTERS = os.path.join(REPO_DIR, 'machinome', 'node', 'adapters')

LEAVING = [os.path.join(ADAPTERS, f'{name}.py') for name in
           ('cadquery', 'build123d', 'build123d_sheet', 'step', 'molejo')]
STAND_INS = sorted(glob.glob(os.path.join(BASEDIR, 'contract_package',
                                          '*.py')))

#: Modules no leaf outside the core may import.
INTERNAL_MODULES = {'machinome.currency', 'machinome.exact_cache',
                    'machinome.exact_artifacts', 'machinome._artifact'}

#: The core modules a leaf package imports: the four bases, and the
#: helpers and seam the contract declares.
DECLARED_MODULES = {
    'machinome.node.leaf', 'machinome.node.exact_leaf',
    'machinome.node.sheet_leaf', 'machinome.node.flexible',
    'machinome.node.sources', 'machinome.source_generation',
    'machinome.exact_engine',
}

#: Imports a leaving adapter makes from outside `DECLARED_MODULES`, each
#: with its reason. Nothing else is allowed.
ALLOWED = {
    ('cadquery.py', 'machinome.node.declarative', 'NodeMeta'):
        'declared: a leaf declaring its own metaclass derives it from '
        'NodeMeta, which lives in machinome.node.declarative, not in a base',
    ('step.py', 'machinome.node.adapters.cadquery', 'workplane_shape'):
        'Deferred (design.md): at the cut, machinome-node-step either '
        'depends on machinome-node-cadquery or keeps its own conversion',
}


def _private_base_members():
    """Every non-dunder underscore member of the four bases and of
    AbstractBaseNode."""
    from machinome.node.base import AbstractBaseNode
    from machinome.node.exact_leaf import ExactLeafNode
    from machinome.node.flexible import FlexibleNode
    from machinome.node.leaf import LeafNode
    from machinome.node.sheet_leaf import SheetLeafNode
    names = set()
    for cls in (AbstractBaseNode, LeafNode, ExactLeafNode, SheetLeafNode,
                FlexibleNode):
        names.update(name for name in vars(cls)
                     if name.startswith('_') and not name.startswith('__'))
    return names


def _reaches(path, private_members):
    """Every reach of `path`, as `(line, description)`."""
    with open(path) as handle:
        tree = ast.parse(handle.read(), path)
    reaches = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level == 0 \
                and (node.module or '').split('.')[0] == 'machinome':
            module = node.module
            if module in INTERNAL_MODULES:
                reaches.append((node.lineno, f'imports {module}'))
            for alias in node.names:
                full = f'{module}.{alias.name}'
                if alias.name.startswith('_'):
                    reaches.append((node.lineno,
                                    f'imports private {full}'))
                if full in INTERNAL_MODULES:
                    reaches.append((node.lineno, f'imports {full}'))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                private = alias.name.startswith('machinome.') and any(
                    part.startswith('_') for part in alias.name.split('.'))
                if alias.name in INTERNAL_MODULES or private:
                    reaches.append((node.lineno, f'imports {alias.name}'))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                and node.name in private_members:
            reaches.append((node.lineno,
                            f'defines private base member {node.name}'))
        elif isinstance(node, ast.Attribute) \
                and isinstance(node.value, ast.Name) \
                and node.value.id == 'self' and node.attr in private_members:
            reaches.append((node.lineno,
                            f'reads private base member self.{node.attr}'))
    return reaches


def _undeclared_imports(path):
    """A leaving adapter's imports from `machinome` outside the declared
    modules, as `(file, module, name)`."""
    with open(path) as handle:
        tree = ast.parse(handle.read(), path)
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level == 0 \
                and (node.module or '').split('.')[0] == 'machinome' \
                and node.module not in DECLARED_MODULES:
            found.extend((os.path.basename(path), node.module, alias.name)
                         for alias in node.names)
    return found


class NoPrivateReachTest(TestCase):

    def setUp(self):
        self.private_members = _private_base_members()

    def test_the_scan_sees_the_bases_privates(self):
        """The scan is only as good as its list: it must know the
        privates a leaf used to reach."""
        self.assertIn('_up_to_date', self.private_members)
        self.assertIn('_tracked_digest', self.private_members)
        self.assertIn('_tracked_fingerprint', self.private_members)

    def test_no_stand_in_or_leaving_adapter_reaches_a_private(self):
        self.assertTrue(STAND_INS)
        for path in [*STAND_INS, *LEAVING]:
            with self.subTest(path=os.path.relpath(path, REPO_DIR)):
                self.assertEqual(_reaches(path, self.private_members), [])

    def test_a_leaving_adapter_imports_only_declared_core_modules(self):
        found = [entry for path in LEAVING
                 for entry in _undeclared_imports(path)]
        self.assertEqual(sorted(set(found) - set(ALLOWED)), [])

    def test_every_allowed_exception_is_real_and_has_a_reason(self):
        found = {entry for path in LEAVING
                 for entry in _undeclared_imports(path)}
        for entry, reason in ALLOWED.items():
            with self.subTest(entry=entry):
                self.assertIn(entry, found)
                self.assertTrue(reason)

    def test_the_stand_ins_import_only_declared_core_modules(self):
        for name in ('exact_stand_in.py', 'faceted_stand_in.py'):
            path = os.path.join(BASEDIR, 'contract_package', name)
            with self.subTest(stand_in=name):
                self.assertEqual(_undeclared_imports(path), [])
