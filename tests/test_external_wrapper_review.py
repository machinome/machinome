"""Independent boundary checks for source-qualified artifact identity."""

import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest import TestCase
from unittest.mock import patch


class ExternalWrapperReviewTest(TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / 'pyproject.toml').write_text(
            '[tool.machinome]\nmodel = "wrapper:Wrapper"\n')
        (self.root / 'asset.scad').write_text('module asset() { cube(2); }\n')
        environment = patch.dict(os.environ, {
            'SOLID_BUILD_DIR': str(self.root / '_build'),
        })
        environment.start()
        self.addCleanup(environment.stop)
        self.modules = []
        self.addCleanup(self.remove_modules)

    def remove_modules(self):
        for name in self.modules:
            sys.modules.pop(name, None)

    def write_wrapper(self, filename, ordinary=False):
        path = self.root / filename
        if ordinary:
            source = (
                'from machinome.node import AssemblyNode\n'
                'class Wrapper(AssemblyNode):\n'
                '    step_source = "not-a-step-file"\n'
                '    stl_source = "not-an-stl-file"\n'
                '    scad_source = "not-a-scad-file"\n'
                '    jscad_source = "not-a-js-file"\n'
                '    def render(self):\n'
                '        return []\n'
            )
        else:
            source = (
                'from machinome.node import OpenScadNode\n'
                'class Wrapper(OpenScadNode):\n'
                f'    scad_source = {str(self.root / "asset.scad")!r}\n'
            )
        path.write_text(source)
        return path

    def load(self, path):
        name = f'_external_review_{id(self)}_{len(self.modules)}'
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        self.modules.append(name)
        spec.loader.exec_module(module)
        return module.Wrapper

    def test_equal_sanitized_prefixes_do_not_erase_distinct_source_identity(self):
        first = self.load(self.write_wrapper('a b.py'))()
        second = self.load(self.write_wrapper('a+b.py'))()
        self.assertEqual(first.uniq_id.rsplit('-', 1)[0],
                         second.uniq_id.rsplit('-', 1)[0])
        self.assertNotEqual(first.uniq_id, second.uniq_id)
        self.assertNotEqual(first.stl_file, second.stl_file)

    def test_symlink_and_import_alias_reach_the_same_defining_source(self):
        original = self.write_wrapper('wrapper.py')
        alias = self.root / 'linked_wrapper.py'
        alias.symlink_to(original)
        first = self.load(original)()
        second = self.load(alias)()
        self.assertEqual(first.uniq_id, second.uniq_id)
        self.assertEqual(first.stl_file, second.stl_file)

    def test_source_named_attributes_do_not_turn_an_ordinary_node_into_a_wrapper(self):
        cls = self.load(self.write_wrapper('ordinary.py', ordinary=True))
        expected = 'Wrapper-' + hashlib.sha256(b'Wrapper').hexdigest()[:12]
        self.assertEqual(cls().uniq_id, expected)
        self.assertEqual(cls(name='separate-tree-name').uniq_id, expected)

    def test_constructing_an_openscad_wrapper_does_not_import_exact_backends(self):
        path = self.write_wrapper('wrapper.py')
        script = (
            'import importlib.util, sys\n'
            f'spec = importlib.util.spec_from_file_location("review_wrapper", {str(path)!r})\n'
            'module = importlib.util.module_from_spec(spec)\n'
            'sys.modules[spec.name] = module\n'
            'spec.loader.exec_module(module)\n'
            'node = module.Wrapper()\n'
            'unexpected = sorted(name for name in sys.modules if '
            'name.split(".")[0] in {"OCP", "cadquery", "build123d"})\n'
            'assert not unexpected, unexpected\n'
        )
        result = subprocess.run([sys.executable, '-c', script],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
