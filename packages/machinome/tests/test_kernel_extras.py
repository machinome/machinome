# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The CAD kernels are extras, and a kernel module refuses an absent one
(OpenSpec changes `lean-install`, `mesh-engine`, `brep-mesh`,
`cut-the-engines`, `cut-the-brep-nodes`, `cut-the-mesh-nodes` and
`join-freecad`, capability `kernel-extras`).

Two halves. The metadata is read from the manifests, the framework's
`pyproject.toml` and its extension packages' under `packages/`, the engines'
and the node packages', and from the repository's `uv.lock` and CI
workflow: no kernel is a required dependency, each is installed by the
extra named by the last component of the address of the module that needs
it, the `brep` and `mesh` extras install the engines' distributions and the
`cadquery`, `build123d`, `step`, `molejo`, `openscad`, `solid2`, `jscad`,
`stl` and `freecad` extras the node packages', which state the kernels
(SolidPython in one range wherever it is named), and the development install
and CI install them all from the lock. The refusal
is observed in subprocesses: the workspace and CI install every kernel, so
an install without one is stood in for by the `sys.meta_path` finder of
`tests/brep_engine_absent.py`, refusing the kernel the way an interpreter
without its wheel does, or finding it and failing from inside, the way a
broken one does.
"""

import json
import os
import tomllib
from pathlib import Path
from unittest import TestCase

import yaml
from packaging.requirements import Requirement

from .brep_engine_absent import run_python
from .import_probe import probe

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPOSITORY = Path(__file__).resolve().parents[3]


def project():
    with open(os.path.join(ROOT, 'pyproject.toml'), 'rb') as stream:
        return tomllib.load(stream)['project']


#: The framework's version, which every package of the set carries.
VERSION = project()['version']

#: The kernels no bare install carries, by distribution name.
KERNEL_DISTRIBUTIONS = ('cadquery', 'build123d', 'ocp-gordon', 'molejo',
                        'cadquery-ocp', 'manifold3d', 'solidpython2')

#: Each extra and the requirements it lists, design.md Decision 3, written
#: out here rather than read from the file under test.
EXTRAS = {
    # `cut-the-engines`: the engines are distributions of their own, which
    # state the kernels.
    'brep': {f'machinome-engine-brep~={VERSION}'},
    'mesh': {f'machinome-engine-mesh~={VERSION}'},
    # `cut-the-brep-nodes`: the node types over the B-rep engine are
    # distributions of their own, which state the kernels.
    'cadquery': {f'machinome-node-cadquery~={VERSION}'},
    'build123d': {f'machinome-node-build123d~={VERSION}'},
    'step': {f'machinome-node-step~={VERSION}'},
    'molejo': {f'machinome-node-molejo~={VERSION}'},
    # `cut-the-mesh-nodes`: the node types that need no B-rep engine are
    # distributions of their own, which state SolidPython or trimesh; a bare
    # install carries no node type.
    # `viewer-seam`: the OpenSCAD extras install the OpenSCAD viewer beside
    # their node packages, and it has an extra of its own.
    'openscad': {f'machinome-node-openscad~={VERSION}',
                 f'machinome-viewer-openscad~={VERSION}'},
    'viewer-openscad': {f'machinome-viewer-openscad~={VERSION}'},
    'solid2': {f'machinome-node-solid2~={VERSION}',
               f'machinome-viewer-openscad~={VERSION}'},
    'jscad': {f'machinome-node-jscad~={VERSION}'},
    'stl': {f'machinome-node-stl~={VERSION}'},
    # `join-freecad`: the FreeCAD node package, over the B-rep engine; FreeCAD
    # itself is a program no extra installs.
    'freecad': {f'machinome-node-freecad~={VERSION}'},
    # `join-skills`: the skills package, a product numbered with the set, not
    # a kernel.
    'skills': {f'machinome-skills~={VERSION}'},
    # `join-movie`: the films, a product numbered with the set, not a
    # kernel.
    'movie': {f'machinome-movie~={VERSION}'},
    # `join-studio`: the studio, a product numbered with the set, not a
    # kernel.
    'studio': {f'machinome-studio~={VERSION}'},
    'all': {'machinome[cadquery,build123d,step,molejo,brep,mesh,'
            'openscad,solid2,jscad,stl,freecad]'},
}

#: Each extension distribution and the requirements its manifest lists:
#: the framework, pinned ~= to the set's version, and its kernel; a node
#: package over the B-rep engine also the engine, pinned alike.
PACKAGE_REQUIREMENTS = {
    'machinome-engine-brep': {f'machinome~={VERSION}',
                              'cadquery-ocp>=7.8.1,<7.9', 'numpy'},
    'machinome-engine-mesh': {f'machinome~={VERSION}', 'manifold3d',
                              'numpy'},
    'machinome-node-cadquery': {f'machinome~={VERSION}', 'cadquery==2.7.*',
                                f'machinome-engine-brep~={VERSION}'},
    'machinome-node-build123d': {f'machinome~={VERSION}',
                                 'build123d==0.10.*',
                                 'ocp-gordon>=0.2.2,<0.3',
                                 f'machinome-engine-brep~={VERSION}',
                                 'numpy'},
    'machinome-node-step': {f'machinome~={VERSION}',
                            f'machinome-node-cadquery~={VERSION}',
                            'cadquery==2.7.*',
                            f'machinome-engine-brep~={VERSION}', 'numpy'},
    'machinome-node-molejo': {f'machinome~={VERSION}', 'molejo[brep]==0.2.*',
                              f'machinome-engine-brep~={VERSION}', 'trimesh'},
    'machinome-node-openscad': {f'machinome~={VERSION}',
                                'solidpython2==2.1.*'},
    'machinome-node-solid2': {f'machinome~={VERSION}',
                              f'machinome-node-openscad~={VERSION}',
                              'solidpython2==2.1.*'},
    'machinome-node-jscad': {f'machinome~={VERSION}'},
    'machinome-node-stl': {f'machinome~={VERSION}', 'trimesh'},
    'machinome-node-freecad': {f'machinome~={VERSION}',
                               f'machinome-engine-brep~={VERSION}', 'numpy',
                               'scipy'},
    # `viewer-seam`: the OpenSCAD viewer draws with the OpenSCAD node
    # family's writer and binary contract.
    'machinome-viewer-openscad': {f'machinome~={VERSION}',
                                  f'machinome-node-openscad~={VERSION}'},
}

#: The node packages among them.
NODE_PACKAGES = tuple(name for name in PACKAGE_REQUIREMENTS
                      if name.startswith('machinome-node-'))

#: The node packages over the B-rep engine, which require it.
BREP_NODE_PACKAGES = ('machinome-node-cadquery', 'machinome-node-build123d',
                      'machinome-node-step', 'machinome-node-molejo',
                      'machinome-node-freecad')

WORKFLOW = REPOSITORY / '.github' / 'workflows' / 'python-app.yml'

#: Every kernel module, the extra its address names, the node types (or the
#: engine) its refusal names, and the kernels it checks, in order.
MODULES = {
    'machinome.node.cadquery': (
        'cadquery', 'machinome.node.cadquery (CadQueryNode)', ('cadquery',)),
    'machinome.node.build123d': (
        'build123d', 'machinome.node.build123d (Build123dNode, '
        'Build123dSheetNode, the Svg artwork reducer)', ('build123d',)),
    'machinome.node.step': (
        'step', 'machinome.node.step (StepNode, StepAssembly)',
        ('cadquery', 'OCP')),
    'machinome.node.molejo': (
        'molejo', 'machinome.node.molejo (MolejoNode)', ('molejo', 'OCP')),
    'machinome.engine.brep': (
        'brep', 'the B-rep engine (machinome.engine.brep)', ('OCP',)),
    'machinome.engine.mesh': (
        'mesh', 'the mesh engine (machinome.engine.mesh)',
        ('manifold3d',)),
    'machinome.node.openscad': (
        'openscad', 'machinome.node.openscad (OpenScadNode and the OpenSCAD '
        'writer)', ('solid2',)),
    'machinome.node.solid2': (
        'solid2', 'machinome.node.solid2 (Solid2Node)', ('solid2',)),
    'machinome.node.freecad': (
        'freecad', 'machinome.node.freecad (FreeCADAssemblyNode, '
        'FreeCADJoint)', ('OCP',)),
}


def refusal(extra, needed_by, missing):
    """design.md Decision 4's sentence, spelled out independently."""
    return (f'{needed_by} needs {missing}, which is not installed; install '
            f'it with \'pip install "machinome[{extra}]"\'')


def package_manifest(name):
    path = REPOSITORY / 'packages' / name / 'pyproject.toml'
    return tomllib.loads(path.read_text())['project']


def sibling_manifests():
    """Every extension package's manifest under `packages/`, by name."""
    return {path.parent.name: tomllib.loads(path.read_text())['project']
            for path in sorted(REPOSITORY.glob(
                'packages/machinome-*/pyproject.toml'))}


def names(requirements):
    return {Requirement(line).name for line in requirements}


#: A snippet that imports one module and reports what it raised, as JSON on
#: its last line.
IMPORT_AND_REPORT = '''
import importlib, json
try:
    importlib.import_module({module!r})
except ImportError as raised:
    print(json.dumps({{
        'type': type(raised).__name__,
        'mro': [cls.__name__ for cls in type(raised).__mro__],
        'name': raised.name,
        'extra': getattr(raised, 'extra', None),
        'message': str(raised)}}))
else:
    print(json.dumps(None))
'''


def imported(module, **blocking):
    run = run_python(IMPORT_AND_REPORT.format(module=module), **blocking)
    lines = run.stdout.strip().splitlines()
    assert lines, run.output
    return json.loads(lines[-1]), run


class KernelMetadataTest(TestCase):
    """(2.1) No kernel is required; each is the extra its module names."""

    def test_a_bare_install_carries_no_kernel(self):
        required = names(project()['dependencies'])

        self.assertEqual(required & set(KERNEL_DISTRIBUTIONS), set())
        self.assertNotIn('manifold3d', required)
        self.assertNotIn('solidpython2', required)
        self.assertIn('watchdog', required)

    def test_each_extra_lists_what_its_module_needs(self):
        extras = project()['optional-dependencies']

        for extra, expected in EXTRAS.items():
            with self.subTest(extra=extra):
                self.assertEqual(set(extras[extra]), expected)

    def test_every_node_package_requires_the_brep_engine(self):
        for name in BREP_NODE_PACKAGES:
            with self.subTest(package=name):
                path = REPOSITORY / 'packages' / name / 'pyproject.toml'
                self.assertTrue(path.is_file(), f'{path} is missing')
                self.assertIn(f'machinome-engine-brep~={VERSION}',
                              package_manifest(name)['dependencies'])

    def test_the_former_engine_extras_are_gone(self):
        extras = project()['optional-dependencies']

        for extra in ('occt', 'manifold'):
            with self.subTest(extra=extra):
                self.assertNotIn(extra, extras)

    def test_no_node_extra_includes_the_mesh_engine(self):
        extras = project()['optional-dependencies']

        for extra in ('cadquery', 'build123d', 'step', 'molejo', 'openscad',
                      'solid2', 'jscad', 'stl', 'freecad'):
            with self.subTest(extra=extra):
                self.assertFalse(any(
                    'mesh' in Requirement(line).extras
                    for line in extras[extra]))
        manifests = sibling_manifests()
        for name in NODE_PACKAGES:
            if name not in manifests:
                continue
            with self.subTest(package=name):
                requirements = [Requirement(line)
                                for line in manifests[name]['dependencies']]
                self.assertFalse(any(
                    requirement.name == 'machinome-engine-mesh'
                    or (requirement.name == 'machinome'
                        and 'mesh' in requirement.extras)
                    for requirement in requirements))

    def test_all_names_every_kernel_extra(self):
        (line,) = project()['optional-dependencies']['all']

        self.assertEqual(Requirement(line).extras,
                         {'cadquery', 'build123d', 'step', 'molejo', 'brep',
                          'mesh', 'openscad', 'solid2', 'jscad', 'stl',
                          'freecad'})

    def test_every_node_type_has_the_extra_of_its_name(self):
        # `root-cleanup`: the install line a refusal or a manifest names
        # for a node type, `machinome[<key>]`, is always one pip resolves.
        from machinome.node.supported import NODE_TYPES

        extras = project()['optional-dependencies']
        for key in NODE_TYPES:
            with self.subTest(key=key):
                self.assertIn(key, extras)

    def test_the_solid2_package_requires_the_openscad_package(self):
        # `cut-the-mesh-nodes`: the solid2 module imports the OpenSCAD
        # node family, so its distribution requires the family's; the core's
        # `solid2` extra names its own distribution and, since `viewer-seam`,
        # the OpenSCAD viewer.
        self.assertIn(f'machinome-node-openscad~={VERSION}',
                      package_manifest('machinome-node-solid2')['dependencies'])
        lines = project()['optional-dependencies']['solid2']

        self.assertEqual({Requirement(line).name for line in lines},
                         {'machinome-node-solid2',
                          'machinome-viewer-openscad'})

    def test_the_openscad_viewer_is_installed_by_three_extras_alone(self):
        extras = project()['optional-dependencies']
        installing = sorted(
            extra for extra, lines in extras.items()
            if any(Requirement(line).name == 'machinome-viewer-openscad'
                   for line in lines))
        self.assertEqual(installing, ['openscad', 'solid2', 'viewer-openscad'])

    def test_the_development_extra_includes_all(self):
        self.assertIn('machinome[all]',
                      project()['optional-dependencies']['dev'])

    def test_cadquery_carries_one_range_wherever_it_is_named(self):
        # `cut-the-brep-nodes`: the core and every extension manifest, since
        # the CadQuery and STEP node packages each name CadQuery.
        extras = project()['optional-dependencies']
        lists = [project()['dependencies'], *extras.values(),
                 *(manifest['dependencies']
                   for manifest in sibling_manifests().values())]
        specifiers = {str(Requirement(line).specifier)
                      for lines in lists
                      for line in lines
                      if Requirement(line).name == 'cadquery'}

        self.assertEqual(specifiers, {'==2.7.*'})

    def test_solidpython_carries_one_range_wherever_it_is_named(self):
        # `cut-the-mesh-nodes`: the OpenSCAD and SolidPython node packages
        # each name SolidPython, which their modules import; the core names
        # it nowhere.
        core = project()
        lists = {'machinome': core['dependencies'],
                 **{f'machinome[{extra}]': lines for extra, lines
                    in core['optional-dependencies'].items()},
                 **{name: manifest['dependencies']
                    for name, manifest in sibling_manifests().items()}}
        named = {place: str(Requirement(line).specifier)
                 for place, lines in lists.items()
                 for line in lines
                 if Requirement(line).name == 'solidpython2'}

        self.assertEqual(sorted(named), ['machinome-node-openscad',
                                         'machinome-node-solid2'])
        self.assertEqual(set(named.values()), {'==2.1.*'})

    def test_each_extension_package_requires_the_core_and_its_kernel(self):
        for name, expected in PACKAGE_REQUIREMENTS.items():
            with self.subTest(package=name):
                self.assertEqual(set(package_manifest(name)['dependencies']),
                                 expected)

    def test_the_occt_range_is_stated_once(self):
        core = project()
        places = [f'machinome[{extra}]'
                  for extra, lines in (('', core['dependencies']),
                                       *core['optional-dependencies'].items())
                  for line in lines
                  if Requirement(line).name == 'cadquery-ocp']
        for name in PACKAGE_REQUIREMENTS:
            path = REPOSITORY / 'packages' / name / 'pyproject.toml'
            if path.is_file():
                places += [name
                           for line in package_manifest(name)['dependencies']
                           if Requirement(line).name == 'cadquery-ocp']

        self.assertEqual(places, ['machinome-engine-brep'])

    def test_the_lock_installs_every_kernel(self):
        lock = tomllib.loads((REPOSITORY / 'uv.lock').read_text())
        locked = {package['name'] for package in lock['package']}

        self.assertEqual(
            {*KERNEL_DISTRIBUTIONS, *PACKAGE_REQUIREMENTS} - locked, set())

    def test_ci_syncs_the_locked_workspace(self):
        jobs = yaml.safe_load(WORKFLOW.read_text())['jobs']

        for name in ('lint', 'test', 'browser-snapshot'):
            with self.subTest(job=name):
                syncs = [step for step in jobs[name]['steps']
                         if 'uv sync --locked' in step.get('run', '')]
                self.assertEqual(len(syncs), 1,
                                 f'{name} does not run uv sync --locked')
                self.assertEqual(syncs[0].get('working-directory'), '.')


class KernelRefusalTest(TestCase):
    """(2.3) A kernel module refuses its absent kernel at import, by its
    extra, and reports a present but broken kernel as itself."""

    def assert_refused(self, module, missing):
        extra, needed_by, _ = MODULES[module]
        report, run = imported(module, absent=(missing,))

        self.assertIsNotNone(report, run.output)
        self.assertEqual(report['type'], 'ExtraUnavailable', run.output)
        self.assertIn('ModuleNotFoundError', report['mro'])
        self.assertEqual(report['name'], missing)
        self.assertEqual(report['extra'], extra)
        self.assertEqual(report['message'],
                         refusal(extra, needed_by, missing))

    def test_each_kernel_module_refuses_each_absent_kernel(self):
        for module, (_, _, kernels) in MODULES.items():
            for missing in kernels:
                with self.subTest(module=module, missing=missing):
                    self.assert_refused(module, missing)

    def test_checking_does_not_import_the_kernel(self):
        for module, kernel in (('machinome.node.cadquery', 'cadquery'),
                               ('machinome.node.build123d', 'build123d')):
            with self.subTest(module=module):
                result = probe(f'import {module}\n'
                               "print('DONE')\n")
                self.assertEqual(result.stdout.strip(), 'DONE',
                                 result.stderr)
                self.assertFalse(result.imported(kernel),
                                 f'importing {module} imported {kernel}')

    def test_a_broken_kernel_reports_its_own_failure(self):
        for module, kernel in (('machinome.node.step', 'cadquery'),
                               ('machinome.engine.mesh', 'manifold3d')):
            with self.subTest(module=module):
                report, run = imported(module, broken=(kernel,),
                                       blocked=False)

                self.assertIsNotNone(report, run.output)
                self.assertEqual(report['type'], 'ImportError')
                self.assertEqual(report['message'], f'broken {kernel}')
                self.assertIsNone(report['extra'])
