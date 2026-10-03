"""Source-bound wrapper identity, including bounded real native caches."""

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import shutil
from unittest import TestCase
from unittest.mock import patch

import cadquery as cq
import trimesh

from machinome.node.base import _canonical_serialization, _build_uniq_id


class ExternalWrapperIdentityTest(TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / 'pyproject.toml').write_text(
            '[tool.machinome]\nmodel = "first:Wrapper"\n')
        (self.root / 'asset.scad').write_text('module asset() { cube(2); }\n')
        (self.root / 'asset.js').write_text('exports.main = () => {};\n')
        self.environment = patch.dict(os.environ, {
            'SOLID_BUILD_DIR': str(self.root / '_build')})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.modules = []
        self.addCleanup(self._remove_modules)

    def _remove_modules(self):
        for name in self.modules:
            sys.modules.pop(name, None)

    def load(self, filename, source, alias=None):
        path = self.root / filename
        path.write_text(source)
        return self.import_path(path, alias)

    def import_path(self, path, alias=None):
        name = alias or f'_wrapper_identity_{id(self)}_{len(self.modules)}'
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        self.modules.append(name)
        # Execute the fixture's current bytes, not timestamp/size-valid .pyc
        # from a prior same-size source-edit case.
        exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
        return module

    def wrapper(self, kind, filename, adjustment='', extra=''):
        source_attribute = {'StepNode': 'step_source', 'StlNode': 'stl_source',
                            'OpenScadNode': 'scad_source',
                            'JScadNode': 'jscad_source'}[kind]
        suffix = {'StepNode': 'step', 'StlNode': 'stl',
                  'OpenScadNode': 'scad', 'JScadNode': 'js'}[kind]
        return self.load(filename,
            f'from machinome.node import {kind}\n'
            f'class Wrapper({kind}):\n'
            f'    {source_attribute} = "asset.{suffix}"\n'
            '    color = "#123456"\n' + extra + adjustment).Wrapper

    def native_asset(self, kind):
        if kind == 'StepNode':
            cq.exporters.export(cq.Workplane('XY').box(2, 3, 4),
                                str(self.root / 'asset.step'))
        else:
            trimesh.creation.box(extents=(2, 3, 4)).export(
                self.root / 'asset.stl')

    def assert_current(self, node):
        self.assertTrue(node._up_to_date(node.stl_file))
        if node.exact:
            self.assertTrue(node._up_to_date(node.brep_file))

    def test_same_named_native_wrappers_keep_their_own_adjusted_geometry(self):
        for kind in ('StepNode', 'StlNode'):
            with self.subTest(kind=kind):
                self.native_asset(kind)
                adjustment = ('    def adjust(self, shape):\n'
                              '        return shape.scale(2)\n' if kind == 'StepNode'
                              else '    def adjust(self, mesh):\n'
                                   '        mesh.apply_scale(2)\n'
                                   '        return mesh\n')
                first = self.wrapper(kind, 'first.py')()
                second = self.wrapper(kind, 'second.py', adjustment)()
                first.assemble()
                second.assemble()
                # Read the cached artifacts, not the freshly adjusted render.
                first_mesh = trimesh.load(first.stl_file, force='mesh')
                second_mesh = trimesh.load(second.stl_file, force='mesh')
                self.assertAlmostEqual(abs(first_mesh.volume), 24, places=4)
                self.assertAlmostEqual(abs(second_mesh.volume), 192, places=4)
                if kind == 'StepNode':
                    from machinome.exact_cache import cached_shape
                    self.assertAlmostEqual(cq.Shape.cast(
                        cached_shape(first.brep_file)).Volume(), 24)
                    self.assertAlmostEqual(cq.Shape.cast(
                        cached_shape(second.brep_file)).Volume(), 192)
                self.assertNotEqual(first.stl_file, second.stl_file)
                self.assert_current(first)
                self.assert_current(second)
                from machinome.exact_artifacts import _atomic_export
                # An StlNode's mesh is produced only inside the writer it
                # hands `publish_artifact`, whose first step reads the
                # source mesh (leaf-contract).
                from machinome.node.stl import _load_source_mesh
                with patch('machinome.exact_artifacts._atomic_export',
                           wraps=_atomic_export) as exact_producer, \
                     patch('machinome.node.stl._load_source_mesh',
                           wraps=_load_source_mesh) as mesh_producer:
                    rebuilt = (type(first)(), type(second)())
                    for node in rebuilt:
                        node.assemble()
                        node.build_stls()
                    self.assertEqual(exact_producer.call_count, 0)
                    self.assertEqual(mesh_producer.call_count, 0)
                    for node in rebuilt:
                        self.assert_current(node)

    def test_real_step_cache_settles_both_source_closures_in_bounded_passes(self):
        self.native_asset('StepNode')
        first_class = self.wrapper('StepNode', 'first.py',
            '    def adjust(self, shape):\n        return shape.scale(1.25)\n')
        # Same inherited correction, different defining module/source closure.
        second_class = self.load('second.py',
            f'from {first_class.__module__} import Wrapper as Original\n'
            'class Wrapper(Original):\n    pass\n').Wrapper
        os.utime(self.root / 'first.py', ns=(1_790_100_303_329848018,) * 2)
        os.utime(self.root / 'second.py', ns=(1_790_509_484_210848006,) * 2)
        for _ in range(4):
            # Fresh instances force a real build pass, not assemble's memoized
            # result on an already assembled object.
            first, second = first_class(), second_class()
            for node in (first, second):
                node.assemble()
                node.build_stls()
            if all(node._up_to_date(node.stl_file)
                   and node._up_to_date(node.brep_file)
                   for node in (first, second)):
                break
        else:
            self.fail('native cached build did not settle within four passes')
        from machinome.exact_cache import cached_shape
        for node in (first, second):
            self.assertAlmostEqual(
                cq.Shape.cast(cached_shape(node.brep_file)).Volume(),
                24 * 1.25 ** 3)
        from machinome.exact_artifacts import _atomic_export
        with patch('machinome.exact_artifacts._atomic_export', wraps=_atomic_export) as producer:
            first, second = first_class(), second_class()
            for node in (first, second):
                node.assemble()
                node.build_stls()
        self.assertEqual(producer.call_count, 0)
        self.assert_current(first)
        self.assert_current(second)

    def test_all_four_source_bound_adapters_distinguish_defining_modules(self):
        for kind in ('StepNode', 'StlNode', 'OpenScadNode', 'JScadNode'):
            with self.subTest(kind=kind):
                if kind in ('StepNode', 'StlNode'):
                    self.native_asset(kind)
                first = self.wrapper(kind, 'first.py')()
                second = self.wrapper(kind, 'second.py')()
                self.assertNotEqual(first.uniq_id, second.uniq_id)
                self.assertEqual(first.build_dir, second.build_dir)
                self.assertLessEqual(len(first.uniq_id), 73)

    def test_ordinary_canonical_bytes_do_not_change(self):
        class Ordinary:
            # Coincidentally named author attributes are NOT adapters.
            step_source = 'asset.step'
            stl_source = 'asset.stl'
        expected = Ordinary.__qualname__ + ',3,a=2,z=1'
        self.assertEqual(_canonical_serialization(Ordinary, (3,), {'z': 1, 'a': 2}),
                         expected)
        import hashlib
        self.assertTrue(_build_uniq_id(Ordinary, (3,), {'a': 2, 'z': 1}).endswith(
            hashlib.sha256(expected.encode()).hexdigest()[:12]))

    def test_import_alias_and_cwd_do_not_change_wrapper_identity(self):
        first_class = self.wrapper('OpenScadNode', 'first.py')
        original = first_class()
        previous = os.getcwd()
        try:
            os.chdir(self.root)
            aliased = self.import_path(
                self.root / 'first.py', '_alternate_wrapper_name').Wrapper()
        finally:
            os.chdir(previous)
        self.assertEqual(original.uniq_id, aliased.uniq_id)

    def test_project_relocation_and_symlink_alias_keep_relative_artifact_paths(self):
        original = self.wrapper('OpenScadNode', 'first.py')()
        with tempfile.TemporaryDirectory() as relocated:
            destination = Path(relocated) / 'project'
            shutil.copytree(self.root, destination)
            moved_class = self.import_path(destination / 'first.py').Wrapper
            with patch.dict(os.environ, {'SOLID_BUILD_DIR': '_build'}):
                moved = moved_class()
            self.assertEqual(original.uniq_id, moved.uniq_id)
            self.assertEqual(os.path.relpath(original.stl_file, self.root),
                             os.path.relpath(moved.stl_file, destination))
            alias = Path(relocated) / 'alias.py'
            alias.symlink_to(destination / 'first.py')
            # The external asset is resolved against the module's directory;
            # use an absolute asset to isolate the defining-source alias.
            (destination / 'first.py').write_text(
                (destination / 'first.py').read_text().replace(
                    '"asset.scad"', repr(str(destination / 'asset.scad'))))
            via_alias = self.import_path(alias).Wrapper()
            self.assertEqual(moved.uniq_id, via_alias.uniq_id)

    def test_wrapper_without_manifest_remains_accepted_for_project_asset(self):
        with tempfile.TemporaryDirectory() as outside:
            path = Path(outside) / 'wrapper.py'
            path.write_text(
                'from machinome.node import OpenScadNode\n'
                'class Wrapper(OpenScadNode):\n'
                f'    scad_source = {str(self.root / "asset.scad")!r}\n')
            node = self.import_path(path).Wrapper()
            self.assertEqual(node._project_root, str(self.root))
            self.assertTrue(node._external_identity_origin(self.root).startswith('..'))

    def test_complete_parameters_and_names_keep_their_identity_contract(self):
        klass = self.wrapper('OpenScadNode', 'first.py')
        shared = klass(1, width=2, name='first')
        self.assertEqual(shared.uniq_id, klass(1, width=2, name='second').uniq_id)
        self.assertNotEqual(shared.uniq_id, klass(2, width=2).uniq_id)
        self.assertNotEqual(shared.uniq_id, klass(1, width=3).uniq_id)
        self.assertEqual(klass(a=1, z=2).uniq_id, klass(z=2, a=1).uniq_id)
        self.assertNotEqual(klass(long='a' * 100 + 'x').uniq_id,
                            klass(long='a' * 100 + 'y').uniq_id)
        module = self.load('declared.py',
            'from machinome.node import StlNode\n'
            'from machinome.parameters import Length\n'
            'class Wrapper(StlNode):\n'
            '    stl_source = "asset.stl"\n'
            '    width = Length(default=2)\n'
            'class Other(Wrapper):\n    pass\n')
        self.native_asset('StlNode')
        self.assertEqual(module.Wrapper().uniq_id, module.Wrapper(width=2).uniq_id)
        self.assertNotEqual(module.Wrapper().uniq_id, module.Wrapper(width=3).uniq_id)
        self.assertNotEqual(module.Wrapper().uniq_id, module.Other().uniq_id)

    def test_site_joints_and_fresh_mates_keep_author_geometry_identity(self):
        for kind, attribute, suffix in (
                ('StlNode', 'stl_source', 'stl'),
                ('StepNode', 'step_source', 'step'),
                ('OpenScadNode', 'scad_source', 'scad'),
                ('JScadNode', 'jscad_source', 'js')):
            with self.subTest(kind=kind):
                if kind in ('StlNode', 'StepNode'):
                    self.native_asset(kind)
                module = self.load('sites.py',
                    f'from machinome.node import {kind}, AssemblyNode, Frame\n'
                    'from machinome.motion.joints import Revolute\n'
                    f'class Wrapper({kind}):\n'
                    f'    {attribute} = "asset.{suffix}"\n'
                    '    axle = Frame()\n'
                    'class Sites(AssemblyNode):\n'
                    '    seat = Frame()\n'
                    '    jointed = Wrapper(turn=Revolute(axis=(0, 0, 1)))\n'
                    '    mated = Wrapper()\n'
                    '    mount = mated.axle.on(seat, Revolute())\n')
                original = module.Wrapper()
                sites = module.Sites()
                for child in (sites.jointed, sites.mated):
                    self.assertEqual(original.uniq_id, child.uniq_id)
                    self.assertEqual(original.stl_file, child.stl_file)
                    self.assertEqual(original._external_identity_origin(self.root),
                                     child._external_identity_origin(self.root))
                self.assertNotEqual(sites.jointed.name, sites.mated.name)

    def test_wrapper_and_helper_edits_change_currency_not_keys(self):
        self.native_asset('StlNode')
        helper = self.load('helper.py', 'SCALE = 1\n')
        wrapper_source = (
            'from machinome.node import StlNode\n'
            f'from {helper.__name__} import SCALE\n'
            'class Wrapper(StlNode):\n'
            '    stl_source = "asset.stl"\n'
            '    def adjust(self, mesh):\n'
            '        mesh.apply_scale(SCALE)\n'
            '        return mesh\n')
        klass = self.load('first.py', wrapper_source).Wrapper
        node = klass()
        node.assemble()
        key = node.uniq_id
        for filename in ('first.py', 'helper.py'):
            with self.subTest(filename=filename):
                path = self.root / filename
                old = path.read_text()
                path.write_text(old.replace('SCALE = 1', 'SCALE = 2')
                                if filename == 'helper.py' else
                                old.replace('apply_scale(SCALE)',
                                            'apply_scale(SCALE * 2)'))
                self.import_path(self.root / 'helper.py', helper.__name__)
                edited = self.import_path(self.root / 'first.py').Wrapper()
                self.assertEqual(key, edited.uniq_id)
                self.assertFalse(edited._up_to_date(edited.stl_file))
                edited.assemble()
                self.assertAlmostEqual(abs(trimesh.load(
                    edited.stl_file, force='mesh').volume), 192, places=4)
                self.assert_current(edited)
                path.write_text(old)
                self.import_path(self.root / 'helper.py', helper.__name__)
                restored = self.import_path(self.root / 'first.py').Wrapper()
                restored.assemble()
                self.assert_current(restored)
