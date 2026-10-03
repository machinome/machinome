# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The machinome universe: a versioned declaration shipped with the
framework.

OpenSpec change ``vet-the-project`` (design D3). `machinome vet` judges a
project against this declaration and nothing else, so it is data, it
names the framework version it describes, and it ships inside the
package. Every list is spelled out here, independently of the file, so a
silent edit to the declaration fails this test rather than changing
every verdict.
"""

import configparser
import os
import tomllib
from unittest import TestCase

import machinome

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DECLARATION = os.path.join(REPO, 'machinome', 'vet', 'universe.toml')


class TheDeclarationTest(TestCase):
    """(3.3) The declaration loads and equals design.md D3 exactly."""

    def setUp(self):
        from machinome.vet import load_universe
        self.universe = load_universe()

    def test_it_names_the_universe_and_the_framework_version(self):
        self.assertEqual(self.universe.name, 'machinome')
        self.assertEqual(self.universe.version, machinome.__version__)

    def test_the_contract(self):
        self.assertEqual(self.universe.contract,
                         ('machinome', 'machinome_mechanics', 'molejo'))
        self.assertEqual(self.universe.contract_deny, (
            'machinome.cli', 'machinome.manager',
            'machinome.core.builder', 'machinome.core.processes',
            'machinome.core.loader', 'machinome.core.export',
            'machinome.core.pieces',
            'machinome.source_generation', 'machinome.viewers',
            'machinome.sphinx', 'machinome.currency', 'machinome._artifact',
            'machinome.exact_cache', 'machinome.exact_artifacts',
            'machinome.occt.engine.read_brep',
            'machinome.occt.engine.write_brep',
            'machinome.occt.engine.write_stl',
        ))

    def test_the_kernels(self):
        self.assertEqual(self.universe.kernels, (
            'cadquery', 'build123d', 'OCP', 'solid2', 'trimesh', 'numpy',
            'scipy', 'manifold3d', 'shapely'))
        self.assertEqual(self.universe.kernel_deny, (
            'cadquery.importers', 'cadquery.exporters',
            'cadquery.occ_impl.importers', 'cadquery.occ_impl.exporters',
            'build123d.importers', 'build123d.exporters',
            'build123d.exporters3d', 'build123d.mesher', 'build123d.Mesher',
            'build123d.import_brep', 'build123d.import_step',
            'build123d.import_stl', 'build123d.import_svg',
            'build123d.import_svg_as_buildline_code',
            'build123d.import_svg_document',
            'build123d.export_brep', 'build123d.export_gltf',
            'build123d.export_step', 'build123d.export_stl',
            'build123d.ExportDXF', 'build123d.ExportSVG',
            'build123d.Export2D',
            'OCP.STEPControl', 'OCP.STEPCAFControl', 'OCP.IGESControl',
            'OCP.IGESCAFControl', 'OCP.StlAPI', 'OCP.RWStl', 'OCP.RWGltf',
            'OCP.VrmlAPI', 'OCP.XSControl', 'OCP.IFSelect', 'OCP.DE',
            'OCP.OSD', 'OCP.BinTools', 'OCP.BRepTools.BRepTools.Write_s',
            'OCP.BRepTools.BRepTools.Read_s',
            'trimesh.load', 'trimesh.load_mesh', 'trimesh.load_path',
            'trimesh.load_remote', 'trimesh.exchange', 'trimesh.resources',
            'trimesh.interfaces',
            'numpy.load', 'numpy.save', 'numpy.savez',
            'numpy.savez_compressed', 'numpy.fromfile', 'numpy.loadtxt',
            'numpy.savetxt', 'numpy.genfromtxt', 'numpy.memmap',
            'numpy.fromregex', 'numpy.lib.npyio', 'numpy.lib.format',
            'numpy.ctypeslib', 'numpy.f2py',
            'scipy.io', 'scipy.datasets',
            'solid2.scad_render_to_file', 'solid2.render_to_stl_file',
        ))
        self.assertEqual(self.universe.deny_methods, (
            'export', 'exportBin', 'exportBrep', 'exportStep', 'exportStl',
            'exportSvg', 'importBin', 'importBrep', 'importStep',
            'importDXF', 'save', 'load', 'dump', 'tofile', 'save_image',
            'save_as_scad', 'save_as_stl'))

    def test_the_pure_stdlib_and_its_restriction(self):
        self.assertEqual(self.universe.stdlib, (
            'math', 'cmath', 'fractions', 'decimal', 'statistics',
            'itertools', 'functools', 'operator', 'collections',
            'dataclasses', 'enum', 'typing', 'abc', 'numbers', 're',
            'string', 'json', 'hashlib', 'struct', 'copy', 'contextlib',
            'random', 'bisect', 'heapq', 'xml.etree', '__future__', 'ast',
            'os', 'pathlib'))
        self.assertEqual(self.universe.restricted, {
            'os': ('os.path', 'os.listdir', 'os.scandir', 'os.walk')})

    def test_the_tests_tier(self):
        self.assertEqual(self.universe.tests,
                         ('unittest', 'pytest', 'logging'))

    def test_the_routes(self):
        self.assertEqual(self.universe.dynamic_builtins,
                         ('exec', 'eval', 'compile', '__import__'))
        self.assertEqual(self.universe.dynamic_modules,
                         ('importlib', 'runpy'))
        self.assertEqual(self.universe.import_system,
                         ('sys.path', 'sys.modules'))
        self.assertEqual(self.universe.dunders, (
            '__subclasses__', '__globals__', '__builtins__', '__loader__',
            '__spec__', '__code__', '__closure__', '__mro__', '__bases__',
            '__base__', '__path__'))
        self.assertEqual(len(self.universe.dunders), 11)
        self.assertEqual(self.universe.denied_builtins,
                         ('breakpoint', 'help', 'input'))
        self.assertNotIn('open', self.universe.denied_builtins)

    def test_the_writes(self):
        self.assertEqual(self.universe.open_name, 'open')
        self.assertEqual(self.universe.write_modes, ('w', 'a', 'x', '+'))
        self.assertEqual(self.universe.write_methods, (
            'write_text', 'write_bytes', 'mkdir', 'unlink', 'rmdir',
            'touch', 'chmod', 'lchmod', 'symlink_to', 'hardlink_to'))

    def test_the_source_attributes(self):
        self.assertEqual(self.universe.source_attributes,
                         ('stl_source', 'step_source', 'scad_source'))
        self.assertEqual(self.universe.refused_sources, ('jscad_source',))

    def test_membership_is_by_whole_dotted_components(self):
        member = self.universe.member
        self.assertTrue(member('xml.etree.ElementTree'))
        self.assertTrue(member('xml.etree'))
        self.assertFalse(member('xml'))
        self.assertFalse(member('xml.sax'))
        self.assertTrue(member('os'))
        self.assertTrue(member('os.path.join'))
        self.assertTrue(member('os.listdir'))
        self.assertFalse(member('os.makedirs'))
        self.assertFalse(member('os.environ'))
        self.assertTrue(member('cadquery.occ_impl.shapes'))
        self.assertFalse(member('requests'))
        self.assertFalse(member('sys'))

    def test_the_tests_tier_is_a_member_only_for_tests(self):
        self.assertFalse(self.universe.member('unittest'))
        self.assertTrue(self.universe.member('unittest', tests=True))
        self.assertTrue(self.universe.member('unittest.mock', tests=True))


class PackagingTest(TestCase):
    """(3.3, 3.4) The declaration ships, and a release rewrites it."""

    def test_the_declaration_ships_in_the_package(self):
        from machinome import vet
        self.assertEqual(
            os.path.realpath(os.path.join(os.path.dirname(vet.__file__),
                                          'universe.toml')),
            os.path.realpath(DECLARATION))
        self.assertTrue(os.path.isfile(DECLARATION))
        with open(os.path.join(REPO, 'MANIFEST.in')) as stream:
            directives = [line.split() for line in stream]
        self.assertIn(['include', 'machinome/vet/universe.toml'], directives)
        with open(os.path.join(REPO, 'pyproject.toml'), 'rb') as stream:
            project = tomllib.load(stream)
        self.assertIs(project['tool']['setuptools']['include-package-data'],
                      True)

    def test_bumpversion_rewrites_the_declared_version(self):
        config = configparser.ConfigParser(interpolation=None)
        config.read(os.path.join(REPO, 'setup.cfg'))
        section = 'bumpversion:file:machinome/vet/universe.toml'

        self.assertIn(section, config.sections())
        self.assertEqual(config[section]['search'],
                         'version = "{current_version}"')
        self.assertEqual(config[section]['replace'],
                         'version = "{new_version}"')
        with open(DECLARATION) as stream:
            text = stream.read()
        current = config['bumpversion']['current_version']
        self.assertEqual(text.count(f'version = "{current}"'), 1)

    def test_shapely_is_a_framework_dependency(self):
        with open(os.path.join(REPO, 'pyproject.toml'), 'rb') as stream:
            project = tomllib.load(stream)

        self.assertIn('shapely==2.1.*', project['project']['dependencies'])
