# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The core holds no kernel code (OpenSpec change `exact-engine`,
capability `exact-engine-dependency`), and imports a kernel only in its
kernel modules (OpenSpec change `lean-install`, capability
`kernel-extras`), and holds no mesh engine code either (OpenSpec change
`mesh-engine`, capability `mesh-engine-dependency`).

Read from the source, not from a running interpreter: the core imports
`OCP` and `cadquery` nowhere outside the engine's own package except the
STEP module (its reader and `adjust`, which move with their package), it
names the engine's package in exactly one module -- the seam -- and the
test framework binds none of the exact layer's names as its own. Every
CAD kernel is imported only by the module its extra is named for, which
checks its kernel before importing it, and a kernel module is named only
at the seams that reach it.
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
            'machinome/node/step.py': ['OCP', 'cadquery']})

    def test_the_old_exact_module_is_gone(self):
        self.assertFalse((PACKAGE / 'exact.py').exists())

    def test_the_test_framework_binds_no_exact_name(self):
        for name in ('intersect_shapes', 'fuse_shapes', 'placed_shape',
                     'solid_count', 'solid_volume', 'cached_bounding_box',
                     'cached_face_boxes', 'shape_identity',
                     'shape_load_observation'):
            with self.subTest(name):
                self.assertFalse(hasattr(machinome.test, name))


#: Every CAD kernel's top-level module.
KERNELS = {'cadquery', 'build123d', 'OCP', 'molejo', 'ocp_gordon',
           'manifold3d'}

#: The four node modules a kernel extra installs a kernel for.
KERNEL_MODULES = {'machinome.node.cadquery', 'machinome.node.build123d',
                  'machinome.node.step', 'machinome.node.molejo'}

#: Each kernel module, as a path, with the extra its address names (the
#: last component; the package's for the engine).
EXTRA_OF = {
    'machinome/node/cadquery.py': 'cadquery',
    'machinome/node/build123d.py': 'build123d',
    'machinome/node/step.py': 'step',
    'machinome/node/molejo.py': 'molejo',
    'machinome/occt/engine.py': 'occt',
    'machinome/manifold/engine.py': 'manifold',
}

#: The core modules that name a kernel module, and the ones each names
#: (`kernel-extras`, "The core imports no kernel outside its kernel
#: modules").
SEAMS = {
    'machinome/node/__init__.py': KERNEL_MODULES,
    'machinome/node/markings.py': {'machinome.node.build123d'},
    'machinome/cli.py': {'machinome.node.step'},
    'machinome/manager/import_step.py': {'machinome.node.step'},
    'machinome/node/step.py': {'machinome.node.cadquery'},
}


def every_module():
    """Every module under `machinome/`, the engine's package included."""
    for path in sorted(PACKAGE.rglob('*.py')):
        yield path.relative_to(ROOT).as_posix(), ast.parse(path.read_text())


def absolute_imports(path, tree):
    """`(line, module)` for every module an import statement names,
    relative imports resolved against the importing module's package."""
    package = path[:-len('.py')].replace('/', '.').rsplit('.', 1)[0]
    if path.endswith('/__init__.py'):
        package = path[:-len('/__init__.py')].replace('/', '.')
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield node.lineno, alias.name
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = package.rsplit('.', node.level - 1)[0]
                module = f'{base}.{node.module}' if node.module else base
            else:
                module = node.module
            yield node.lineno, module
            for alias in node.names:
                yield node.lineno, f'{module}.{alias.name}'


def kernel_modules_named(path, tree):
    """The kernel modules a module imports or spells as a whole string."""
    named = {module for _, module in absolute_imports(path, tree)
             if module in KERNEL_MODULES}
    named.update(node.value for node in ast.walk(tree)
                 if isinstance(node, ast.Constant)
                 and node.value in KERNEL_MODULES)
    return named


def require_extra_call(tree):
    """The first top-level `require_extra(...)` call: its line and its
    extra."""
    for statement in tree.body:
        if isinstance(statement, ast.Expr) \
                and isinstance(statement.value, ast.Call):
            function = statement.value.func
            name = getattr(function, 'id', getattr(function, 'attr', None))
            if name == 'require_extra':
                (extra, *_) = statement.value.args
                return statement.lineno, extra.value
    return None, None


class KernelsOnlyInTheirModulesTest(TestCase):
    """(lean-install 2.6) Each kernel is imported only by its module."""

    def test_kernels_are_imported_only_by_their_modules(self):
        importing = {}
        for path, tree in every_module():
            roots = {module.split('.')[0]
                     for _, module in absolute_imports(path, tree)}
            if roots & KERNELS:
                importing[path] = sorted(roots & KERNELS)

        self.assertEqual(importing, {
            'machinome/node/build123d.py': ['build123d'],
            'machinome/node/molejo.py': ['molejo'],
            'machinome/manifold/engine.py': ['manifold3d'],
            'machinome/node/step.py': ['OCP', 'cadquery'],
            'machinome/occt/engine.py': ['OCP'],
        })

    def test_kernel_modules_are_named_only_at_the_seams(self):
        naming = {}
        for path, tree in every_module():
            named = kernel_modules_named(path, tree)
            if named:
                naming[path] = named

        for path, named in naming.items():
            with self.subTest(path=path):
                self.assertLessEqual(named, SEAMS.get(path, set()))
        for path in ('machinome/node/markings.py', 'machinome/cli.py',
                     'machinome/manager/import_step.py',
                     'machinome/node/step.py'):
            with self.subTest(seam=path):
                self.assertEqual(naming.get(path), SEAMS[path])

    def test_each_kernel_module_checks_its_kernel_first(self):
        modules = dict(every_module())

        for path, extra in EXTRA_OF.items():
            with self.subTest(path=path):
                line, declared = require_extra_call(modules[path])
                self.assertIsNotNone(line, f'{path} calls no require_extra')
                self.assertEqual(declared, extra)
                later = [(number, module) for number, module
                         in absolute_imports(path, modules[path])
                         if module.split('.')[0] in KERNELS
                         or module in KERNEL_MODULES
                         or any(module.startswith(f'{kernel}.')
                                for kernel in KERNEL_MODULES)]
                self.assertEqual(
                    [(number, module) for number, module in later
                     if number < line], [])


MESH_PROVIDER_PACKAGE = PACKAGE / 'manifold'
MESH_PROVIDER_NAME = re.compile(r'^machinome\.manifold(\.\w+)*$')


def boolean_reaches(tree):
    """Every line of a module that reaches `trimesh.boolean`: an attribute
    chain ending `trimesh.boolean`, or an import of it."""
    lines = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == 'boolean' \
                and isinstance(node.value, ast.Name) \
                and node.value.id == 'trimesh':
            lines.append(node.lineno)
        elif isinstance(node, ast.Import):
            lines.extend(node.lineno for alias in node.names
                         if alias.name.startswith('trimesh.boolean'))
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module.startswith('trimesh.boolean') or (
                    node.module == 'trimesh' and any(
                        alias.name == 'boolean' for alias in node.names)):
                lines.append(node.lineno)
    return lines


def names_the_mesh_provider(tree):
    """Whether a module imports, or spells as a whole string,
    `machinome.manifold` or anything beneath it."""
    for name in imported_roots(tree):
        if name == 'machinome.manifold' \
                or name.startswith('machinome.manifold.'):
            return True
    return any(isinstance(node, ast.Constant) and isinstance(node.value, str)
               and MESH_PROVIDER_NAME.match(node.value)
               for node in ast.walk(tree))


class CoreHoldsNoMeshEngineTest(TestCase):
    """(mesh-engine 2.3) The core holds no mesh engine code: it reaches
    manifold3d through no module but the provider's, not even through
    trimesh, and names the provider in its seam alone."""

    def test_no_module_reaches_trimesh_boolean(self):
        reaching = {path: lines for path, tree in every_module()
                    if (lines := boolean_reaches(tree))}

        self.assertEqual(reaching, {})

    def test_the_seam_is_the_only_core_module_naming_the_provider(self):
        naming = [path for path, tree in every_module()
                  if MESH_PROVIDER_PACKAGE not in (ROOT / path).parents
                  and names_the_mesh_provider(tree)]

        self.assertEqual(naming, ['machinome/mesh_engine.py'])
