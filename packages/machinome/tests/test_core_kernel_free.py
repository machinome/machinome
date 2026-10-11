# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The core holds no kernel code (OpenSpec change `exact-engine`,
capability `exact-engine-dependency`), and imports a kernel only in its
kernel modules (OpenSpec change `lean-install`, capability
`kernel-extras`), and holds no mesh engine code either (OpenSpec change
`mesh-engine`, capability `mesh-engine-dependency`). The providers are
modules of the engine package, `machinome.engine.brep` and
`machinome.engine.mesh`, and the seams its `__init__` (OpenSpec change
`brep-mesh`); each provider is shipped by its own distribution under
`packages/`, outside the core, and imports only its kernel (OpenSpec change
`cut-the-engines`), as is each node module over the B-rep engine,
`machinome.node.cadquery`, `.build123d`, `.step` and `.molejo` (OpenSpec
change `cut-the-brep-nodes`), and each node type that needs no B-rep engine,
the OpenSCAD node family `machinome.node.openscad` with its snapshot
renderer, `.solid2`, `.jscad` and `.stl` (OpenSpec change
`cut-the-mesh-nodes`), and the FreeCAD node package `machinome.node.freecad`,
whose adapter imports the OCCT binding (OpenSpec change `join-freecad`).

Read from the source, not from a running interpreter: the core imports
`OCP` and `cadquery` nowhere but the template a project copies, it names
the provider in exactly one module -- the seam -- and the test framework
binds none of the B-rep layer's names as its own. Every CAD kernel, and
SolidPython among them, is imported only by the module its extra is named
for, which checks its kernel before importing it, and a kernel module is
named only at the seams that reach it. A census of the core's import
statements finds no node type and no engine provider but in the two
templates a project copies.
"""

import ast
import re
from pathlib import Path
from unittest import TestCase

import machinome.test

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'machinome'
REPOSITORY = Path(__file__).resolve().parents[3]
PROVIDER_NAME = re.compile(r'^machinome\.engine\.brep(\.\w+)*$')


def core_modules():
    for path in sorted(PACKAGE.rglob('*.py')):
        yield path.relative_to(ROOT).as_posix(), ast.parse(path.read_text())


def portion_modules():
    """Every module of the framework's extension packages, keyed by its path
    under `packages/`: `machinome-engine-brep/machinome/engine/brep.py`."""
    packages = REPOSITORY / 'packages'
    for path in sorted(packages.glob('machinome-*/machinome/**/*.py')):
        yield path.relative_to(packages).as_posix(), \
            ast.parse(path.read_text())


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
    """Whether a module imports, or spells by name, `machinome.engine.brep`."""
    for name in imported_roots(tree):
        if name == 'machinome.engine.brep' \
                or name.startswith('machinome.engine.brep.'):
            return True
    return any(isinstance(node, ast.Constant) and isinstance(node.value, str)
               and PROVIDER_NAME.match(node.value)
               for node in ast.walk(tree))


class CoreHoldsNoKernelTest(TestCase):

    def test_the_seam_is_the_only_module_naming_the_engine(self):
        naming = [path for path, tree in core_modules()
                  if names_the_provider(tree)]

        self.assertEqual(naming, ['machinome/engine/__init__.py'])

    def test_no_core_module_imports_the_kernel_or_cadquery(self):
        importing = {}
        for path, tree in core_modules():
            roots = {name.split('.')[0] for name in imported_roots(tree)}
            kernel = roots & {'OCP', 'cadquery'}
            if kernel:
                importing[path] = sorted(kernel)

        self.assertEqual(importing, {
            # A project's file `machinome new` copies (`openscad-out`).
            'machinome/manager/templates/project/root/cadquery.py':
                ['cadquery']})

    def test_the_old_exact_module_is_gone(self):
        self.assertFalse((PACKAGE / 'exact.py').exists())

    def test_the_test_framework_binds_no_exact_name(self):
        for name in ('intersect_shapes', 'fuse_shapes', 'placed_shape',
                     'solid_count', 'solid_volume', 'cached_bounding_box',
                     'cached_face_boxes', 'shape_identity',
                     'shape_load_observation'):
            with self.subTest(name):
                self.assertFalse(hasattr(machinome.test, name))


#: Every CAD kernel's top-level module, SolidPython's (`solid2`) included.
KERNELS = {'cadquery', 'build123d', 'OCP', 'molejo', 'ocp_gordon',
           'manifold3d', 'solid2'}

#: The node modules a kernel extra installs a kernel for: the four over the
#: B-rep engine, the OpenSCAD family's two over SolidPython and the FreeCAD
#: package, whose adapter reads the OCCT binding (`join-freecad`).
KERNEL_MODULES = {'machinome.node.cadquery', 'machinome.node.build123d',
                  'machinome.node.step', 'machinome.node.molejo',
                  'machinome.node.openscad', 'machinome.node.solid2',
                  'machinome.node.freecad'}

#: Every node module and engine provider, each shipped by its own
#: distribution, which the core imports nowhere (`cut-the-mesh-nodes`).
EXTENSION_MODULES = (
    'machinome.node.cadquery', 'machinome.node.build123d',
    'machinome.node.step', 'machinome.node.molejo',
    'machinome.node.openscad', 'machinome.node.solid2',
    'machinome.node.jscad', 'machinome.node.stl',
    'machinome.node.freecad',
    'machinome.engine.brep', 'machinome.engine.mesh',
)

#: Each kernel module, as a path, with the extra its address names (the
#: last component).
EXTRA_OF = {
    'machinome-node-cadquery/machinome/node/cadquery.py': 'cadquery',
    'machinome-node-build123d/machinome/node/build123d.py': 'build123d',
    'machinome-node-step/machinome/node/step.py': 'step',
    'machinome-node-molejo/machinome/node/molejo.py': 'molejo',
    'machinome-node-openscad/machinome/node/openscad/__init__.py': 'openscad',
    'machinome-node-solid2/machinome/node/solid2.py': 'solid2',
    'machinome-node-freecad/machinome/node/freecad/__init__.py': 'freecad',
    'machinome-engine-brep/machinome/engine/brep.py': 'brep',
    'machinome-engine-mesh/machinome/engine/mesh.py': 'mesh',
}

#: The core modules that name a kernel module, and the ones each names
#: (`kernel-extras`, "The core imports no kernel outside its kernel
#: modules").
SEAMS = {
    'machinome/node/markings.py': {'machinome.node.build123d'},
    'machinome-node-step/machinome/node/step.py': {'machinome.node.cadquery'},
    # machinome-node-solid2 requires machinome-node-openscad, whose leaf
    # base and binary contract the module imports (`cut-the-mesh-nodes`).
    'machinome-node-solid2/machinome/node/solid2.py':
        {'machinome.node.openscad'},
    # The table's provisional renderer column names the OpenSCAD snapshot
    # renderer, a module of the family's package (`cut-the-mesh-nodes`).
    'machinome/node/supported.py': {'machinome.node.openscad'},
    # The project files `machinome new` copies, each of which imports its
    # node type from its module (`root-cleanup`).
    'machinome/manager/templates/project/root/cadquery.py':
        {'machinome.node.cadquery'},
    'machinome/manager/templates/project/root/solid2.py':
        {'machinome.node.solid2'},
}

#: The modules that reach a kernel module through the table of supported
#: node types (`machinome.node.supported`, `openscad-out`), naming none:
#: the node root reads it for its refusals (`root-cleanup`), and the
#: snapshot and new commands for the renderer and the starter
#: (`cut-the-mesh-nodes`).
TABLE_READERS = ('machinome/cli.py', 'machinome/manager/import_step.py',
                 'machinome/node/__init__.py', 'machinome/manager/snapshot.py',
                 'machinome/manager/new.py')


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


def kernel_module_of(name):
    """The kernel module `name` is, or is beneath, or None."""
    for module in KERNEL_MODULES:
        if name == module or name.startswith(f'{module}.'):
            return module
    return None


def own_package(path):
    """The address of the node module or package an extension package's
    module belongs to (`machinome-node-openscad/machinome/node/openscad/leaf.py`
    belongs to `machinome.node.openscad`), or None for a core module."""
    if not path.startswith('machinome-node-'):
        return None
    parts = path.split('/')[1:4]
    return '.'.join(parts).removesuffix('.py')


def kernel_modules_named(path, tree):
    """The kernel modules a module imports or spells as a string, a name
    beneath a kernel module counting as that module; a module of a node
    package naming its own package is not counted."""
    names = [module for _, module in absolute_imports(path, tree)]
    names += [node.value for node in ast.walk(tree)
              if isinstance(node, ast.Constant)
              and isinstance(node.value, str)]
    named = {kernel_module_of(name) for name in names} - {None}
    return named - {own_package(path)}


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
            # The templates `machinome new` scaffolds a CadQuery and a
            # SolidPython part from (`openscad-out`): a project's files,
            # which the core copies and never imports.
            'machinome/manager/templates/project/root/cadquery.py':
                ['cadquery'],
            'machinome/manager/templates/project/root/solid2.py':
                ['solid2'],
        })

    def test_the_core_imports_no_node_type_and_no_engine_provider(self):
        # `cut-the-mesh-nodes`: every node type and engine provider is a
        # distribution of its own; the core reaches them through the table
        # and the seams, by name, never by an import statement.
        importing = {}
        for path, tree in every_module():
            found = sorted({module for _, module in absolute_imports(path, tree)
                            if any(module == name
                                   or module.startswith(f'{name}.')
                                   for name in EXTENSION_MODULES)})
            if found:
                importing[path] = found

        self.assertEqual(importing, {
            'machinome/manager/templates/project/root/cadquery.py':
                ['machinome.node.cadquery',
                 'machinome.node.cadquery.CadQueryNode'],
            'machinome/manager/templates/project/root/solid2.py':
                ['machinome.node.solid2',
                 'machinome.node.solid2.Solid2Node'],
        })

    def test_the_extension_packages_import_only_their_kernels(self):
        importing = {}
        for path, tree in portion_modules():
            roots = {module.split('.')[0]
                     for _, module in absolute_imports(path, tree)}
            if roots & KERNELS:
                importing[path] = sorted(roots & KERNELS)

        self.assertEqual(importing, {
            'machinome-engine-brep/machinome/engine/brep.py': ['OCP'],
            'machinome-engine-mesh/machinome/engine/mesh.py': ['manifold3d'],
            'machinome-node-build123d/machinome/node/build123d.py':
                ['build123d'],
            'machinome-node-molejo/machinome/node/molejo.py': ['molejo'],
            'machinome-node-step/machinome/node/step.py': ['OCP', 'cadquery'],
            'machinome-node-openscad/machinome/node/openscad/__init__.py':
                ['solid2'],
            'machinome-node-openscad/machinome/node/openscad/writer.py':
                ['solid2'],
            'machinome-node-solid2/machinome/node/solid2.py': ['solid2'],
            'machinome-node-freecad/machinome/node/freecad/adapter.py':
                ['OCP'],
        })

    def test_kernel_modules_are_named_only_at_the_seams(self):
        naming = {}
        for path, tree in (*every_module(), *portion_modules()):
            named = kernel_modules_named(path, tree)
            if named:
                naming[path] = named

        for path, named in naming.items():
            with self.subTest(path=path):
                self.assertLessEqual(named, SEAMS.get(path, set()))
        for path in ('machinome/node/markings.py',
                     'machinome-node-step/machinome/node/step.py',
                     'machinome-node-solid2/machinome/node/solid2.py',
                     'machinome/node/supported.py'):
            with self.subTest(seam=path):
                self.assertEqual(naming.get(path), SEAMS[path])
        for path in TABLE_READERS:
            with self.subTest(reader=path):
                self.assertIsNone(naming.get(path))

    def test_each_kernel_module_checks_its_kernel_first(self):
        modules = dict(every_module()) | dict(portion_modules())

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


MESH_PROVIDER_NAME = re.compile(r'^machinome\.engine\.mesh(\.\w+)*$')


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
    `machinome.engine.mesh` or anything beneath it."""
    for name in imported_roots(tree):
        if name == 'machinome.engine.mesh' \
                or name.startswith('machinome.engine.mesh.'):
            return True
    return any(isinstance(node, ast.Constant) and isinstance(node.value, str)
               and MESH_PROVIDER_NAME.match(node.value)
               for node in ast.walk(tree))


class CoreHoldsNoMeshEngineTest(TestCase):
    """(mesh-engine 2.3) The core holds no mesh engine code: it reaches
    manifold3d through no module but the provider's, not even through
    trimesh, and names the provider in its seam alone."""

    def test_no_module_reaches_trimesh_boolean(self):
        reaching = {path: lines
                    for path, tree in (*every_module(), *portion_modules())
                    if (lines := boolean_reaches(tree))}

        self.assertEqual(reaching, {})

    def test_the_seam_is_the_only_core_module_naming_the_provider(self):
        naming = [path for path, tree in every_module()
                  if names_the_mesh_provider(tree)]

        self.assertEqual(naming, ['machinome/engine/__init__.py'])
