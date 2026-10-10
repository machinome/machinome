# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The CAD kernels are extras, and a kernel module refuses an absent one
(OpenSpec changes `lean-install`, `mesh-engine`, `brep-mesh` and
`cut-the-engines`, capability `kernel-extras`).

Two halves. The metadata is read from the manifests, the framework's
`pyproject.toml` and its engines' under `packages/`, and from the
repository's `uv.lock` and CI workflow: no kernel is a required dependency,
each is installed by the extra named by the last component of the address
of the module that needs it, the `brep` and `mesh` extras install the
engines' distributions, which state the kernels, and the development
install and CI install them all from the lock. The refusal
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
    'cadquery': {'cadquery==2.7.*', 'machinome[brep]'},
    'build123d': {'build123d==0.10.*', 'ocp-gordon>=0.2.2,<0.3',
                  'machinome[brep]'},
    'step': {'cadquery==2.7.*', 'machinome[brep]'},
    'molejo': {'molejo[brep]==0.2.*', 'machinome[brep]'},
    'openscad': {'solidpython2==2.1.*'},
    'solid2': {'machinome[openscad]'},
    # `root-cleanup` (design.md Decision 7): the node types whose module
    # needs nothing the core does not require; each extra names the node
    # type and installs nothing.
    'jscad': set(),
    'stl': set(),
    'all': {'machinome[cadquery,build123d,step,molejo,brep,mesh,'
            'openscad,solid2,jscad,stl]'},
}

#: Each engine distribution and the requirements its manifest lists: the
#: framework, pinned ~= to the set's version, and its kernel.
ENGINE_REQUIREMENTS = {
    'machinome-engine-brep': {f'machinome~={VERSION}',
                              'cadquery-ocp>=7.8.1,<7.9', 'numpy'},
    'machinome-engine-mesh': {f'machinome~={VERSION}', 'manifold3d',
                              'numpy'},
}

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
}


def refusal(extra, needed_by, missing):
    """design.md Decision 4's sentence, spelled out independently."""
    return (f'{needed_by} needs {missing}, which is not installed; install '
            f'it with \'pip install "machinome[{extra}]"\'')


def engine_manifest(name):
    path = REPOSITORY / 'packages' / name / 'pyproject.toml'
    return tomllib.loads(path.read_text())['project']


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

    def test_every_kernel_extra_includes_the_brep_extra(self):
        extras = project()['optional-dependencies']

        for extra in ('cadquery', 'build123d', 'step', 'molejo'):
            with self.subTest(extra=extra):
                self.assertIn('machinome[brep]', extras[extra])

    def test_the_former_engine_extras_are_gone(self):
        extras = project()['optional-dependencies']

        for extra in ('occt', 'manifold'):
            with self.subTest(extra=extra):
                self.assertNotIn(extra, extras)

    def test_no_node_extra_includes_the_mesh_engine(self):
        extras = project()['optional-dependencies']

        for extra in ('cadquery', 'build123d', 'step', 'molejo'):
            with self.subTest(extra=extra):
                self.assertFalse(any(
                    'mesh' in Requirement(line).extras
                    for line in extras[extra]))

    def test_all_names_every_kernel_extra(self):
        (line,) = project()['optional-dependencies']['all']

        self.assertEqual(Requirement(line).extras,
                         {'cadquery', 'build123d', 'step', 'molejo', 'brep',
                          'mesh', 'openscad', 'solid2', 'jscad', 'stl'})

    def test_every_node_type_has_the_extra_of_its_name(self):
        # `root-cleanup`: the install line a refusal or a manifest names
        # for a node type, `machinome[<key>]`, is always one pip resolves.
        from machinome.node.supported import NODE_TYPES

        extras = project()['optional-dependencies']
        for key in NODE_TYPES:
            with self.subTest(key=key):
                self.assertIn(key, extras)

    def test_the_solid2_extra_installs_the_openscad_extra(self):
        (line,) = project()['optional-dependencies']['solid2']

        self.assertEqual(Requirement(line).name, 'machinome')
        self.assertEqual(Requirement(line).extras, {'openscad'})

    def test_the_development_extra_includes_all(self):
        self.assertIn('machinome[all]',
                      project()['optional-dependencies']['dev'])

    def test_cadquery_carries_one_range_wherever_it_is_named(self):
        extras = project()['optional-dependencies']
        specifiers = {str(Requirement(line).specifier)
                      for lines in (project()['dependencies'],
                                    *extras.values())
                      for line in lines
                      if Requirement(line).name == 'cadquery'}

        self.assertEqual(specifiers, {'==2.7.*'})

    def test_each_engine_requires_the_core_and_its_kernel(self):
        for name, expected in ENGINE_REQUIREMENTS.items():
            with self.subTest(engine=name):
                self.assertEqual(set(engine_manifest(name)['dependencies']),
                                 expected)

    def test_the_occt_range_is_stated_once(self):
        core = project()
        places = [f'machinome[{extra}]'
                  for extra, lines in (('', core['dependencies']),
                                       *core['optional-dependencies'].items())
                  for line in lines
                  if Requirement(line).name == 'cadquery-ocp']
        for name in ENGINE_REQUIREMENTS:
            path = REPOSITORY / 'packages' / name / 'pyproject.toml'
            if path.is_file():
                places += [name
                           for line in engine_manifest(name)['dependencies']
                           if Requirement(line).name == 'cadquery-ocp']

        self.assertEqual(places, ['machinome-engine-brep'])

    def test_the_lock_installs_every_kernel(self):
        lock = tomllib.loads((REPOSITORY / 'uv.lock').read_text())
        locked = {package['name'] for package in lock['package']}

        self.assertEqual(
            {*KERNEL_DISTRIBUTIONS, *ENGINE_REQUIREMENTS} - locked, set())

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
