# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The CAD kernels are extras, and a kernel module refuses an absent one
(OpenSpec changes `lean-install` and `mesh-engine`, capability
`kernel-extras`).

Two halves. The metadata is read from `pyproject.toml`, `requirements.txt`
and `tox.ini`: no kernel is a required dependency, each is installed by the
extra named by the last component of the address of the module that needs
it, and the development install, CI and tox install them all. The refusal
is observed in subprocesses: the workspace and CI install every kernel, so
an install without one is stood in for by the `sys.meta_path` finder of
`tests/exact_engine_absent.py`, refusing the kernel the way an interpreter
without its wheel does, or finding it and failing from inside, the way a
broken one does.
"""

import configparser
import json
import os
import tomllib
from unittest import TestCase

from packaging.requirements import Requirement

from .exact_engine_absent import run_python
from .import_probe import probe

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: The kernels no bare install carries, by distribution name.
KERNEL_DISTRIBUTIONS = ('cadquery', 'build123d', 'ocp-gordon', 'molejo',
                        'cadquery-ocp', 'manifold3d', 'solidpython2')

#: Each extra and the requirements it lists, design.md Decision 3, written
#: out here rather than read from the file under test.
EXTRAS = {
    'occt': {'cadquery-ocp>=7.8.1,<7.9'},
    'manifold': {'manifold3d'},
    'cadquery': {'cadquery==2.7.*', 'machinome[occt]'},
    'build123d': {'build123d==0.10.*', 'ocp-gordon>=0.2.2,<0.3',
                  'machinome[occt]'},
    'step': {'cadquery==2.7.*', 'machinome[occt]'},
    'molejo': {'molejo[brep]==0.2.*', 'machinome[occt]'},
    'openscad': {'solidpython2==2.1.*'},
    'solid2': {'machinome[openscad]'},
    'all': {'machinome[cadquery,build123d,step,molejo,occt,manifold,'
            'openscad,solid2]'},
}

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
    'machinome.occt.engine': (
        'occt', 'the exact engine (machinome.occt.engine)', ('OCP',)),
    'machinome.manifold.engine': (
        'manifold', 'the mesh engine (machinome.manifold.engine)',
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


def project():
    with open(os.path.join(ROOT, 'pyproject.toml'), 'rb') as stream:
        return tomllib.load(stream)['project']


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

    def test_every_kernel_extra_includes_the_occt_extra(self):
        extras = project()['optional-dependencies']

        for extra in ('cadquery', 'build123d', 'step', 'molejo'):
            with self.subTest(extra=extra):
                self.assertIn('machinome[occt]', extras[extra])

    def test_no_node_extra_includes_the_mesh_engine(self):
        extras = project()['optional-dependencies']

        for extra in ('cadquery', 'build123d', 'step', 'molejo'):
            with self.subTest(extra=extra):
                self.assertFalse(any(
                    'manifold' in Requirement(line).extras
                    for line in extras[extra]))

    def test_all_names_every_kernel_extra(self):
        (line,) = project()['optional-dependencies']['all']

        self.assertEqual(Requirement(line).extras,
                         {'cadquery', 'build123d', 'step', 'molejo', 'occt',
                          'manifold', 'openscad', 'solid2'})

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

    def test_ci_installs_every_concrete_requirement_of_all(self):
        with open(os.path.join(ROOT, 'requirements.txt')) as stream:
            listed = {line.strip() for line in stream
                      if line.strip() and not line.startswith('#')}
        concrete = {line for extra in ('occt', 'manifold', 'cadquery',
                                       'build123d', 'step', 'molejo',
                                       'openscad', 'solid2')
                    for line in EXTRAS[extra]
                    if not line.startswith('machinome[')}

        self.assertEqual(concrete - listed, set())
        self.assertIn('solidpython2==2.1.*', listed)

    def test_tox_installs_every_extra(self):
        config = configparser.ConfigParser()
        config.read(os.path.join(ROOT, 'tox.ini'))

        self.assertEqual(config['testenv'].get('extras', '').strip(), 'all')


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
                               ('machinome.manifold.engine', 'manifold3d')):
            with self.subTest(module=module):
                report, run = imported(module, broken=(kernel,),
                                       blocked=False)

                self.assertIsNotNone(report, run.output)
                self.assertEqual(report['type'], 'ImportError')
                self.assertEqual(report['message'], f'broken {kernel}')
                self.assertIsNone(report['extra'])
