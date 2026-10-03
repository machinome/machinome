# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The core holds no kernel code (OpenSpec change `exact-engine`,
capability `exact-engine-dependency`).

Read from the source, not from a running interpreter: the core imports
`OCP` and `cadquery` nowhere outside the engine's own package except the
STEP adapter (its reader and `adjust`, which move with their package), it
names the engine's package in exactly one module -- the seam -- and the
test framework binds none of the exact layer's names as its own.
"""

import ast
import re
from pathlib import Path
from unittest import TestCase

import machinome.test

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'machinome'
ENGINE_PACKAGE = PACKAGE / 'occt'
PROVIDER_NAME = re.compile(r'^machinome\.occt(\.\w+)*$')


def core_modules():
    for path in sorted(PACKAGE.rglob('*.py')):
        if ENGINE_PACKAGE in path.parents:
            continue
        yield path.relative_to(ROOT).as_posix(), ast.parse(path.read_text())


def imported_roots(tree):
    """The top-level package of every module an import statement names."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            yield node.module
            for alias in node.names:
                yield f'{node.module}.{alias.name}'


def names_the_provider(tree):
    """Whether a module imports, or spells by name, `machinome.occt`."""
    for name in imported_roots(tree):
        if name == 'machinome.occt' or name.startswith('machinome.occt.'):
            return True
    return any(isinstance(node, ast.Constant) and isinstance(node.value, str)
               and PROVIDER_NAME.match(node.value)
               for node in ast.walk(tree))


class CoreHoldsNoKernelTest(TestCase):

    def test_the_seam_is_the_only_module_naming_the_engine(self):
        naming = [path for path, tree in core_modules()
                  if names_the_provider(tree)]

        self.assertEqual(naming, ['machinome/exact_engine.py'])

    def test_no_core_module_imports_the_kernel_or_cadquery(self):
        importing = {}
        for path, tree in core_modules():
            roots = {name.split('.')[0] for name in imported_roots(tree)}
            kernel = roots & {'OCP', 'cadquery'}
            if kernel:
                importing[path] = sorted(kernel)

        self.assertEqual(importing, {
            'machinome/node/adapters/step.py': ['OCP', 'cadquery']})

    def test_the_old_exact_module_is_gone(self):
        self.assertFalse((PACKAGE / 'exact.py').exists())

    def test_the_test_framework_binds_no_exact_name(self):
        for name in ('intersect_shapes', 'fuse_shapes', 'placed_shape',
                     'solid_count', 'solid_volume', 'cached_bounding_box',
                     'cached_face_boxes', 'shape_identity',
                     'shape_load_observation'):
            with self.subTest(name):
                self.assertFalse(hasattr(machinome.test, name))
