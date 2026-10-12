"""Layer 9: the package at its address (change `join-movie` of the machinome
repository): its manifest, its portion of the `machinome` namespace, no module
of its former name, and a package root that loads a name's module only when
the name is used."""

import importlib.util
import json
import subprocess
import sys
import tomllib
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
FRAMEWORK = PACKAGE.parent / 'machinome' / 'pyproject.toml'


def manifest():
    return tomllib.loads((PACKAGE / 'pyproject.toml').read_text())


def fresh(code):
    """The modules a fresh interpreter holds after running `code`."""
    done = subprocess.run(
        [sys.executable, '-c',
         code + '\nimport json, sys\nprint(json.dumps(sorted(sys.modules)))'],
        capture_output=True, text=True, check=True)
    return set(json.loads(done.stdout.splitlines()[-1]))


def test_the_manifest_is_a_product_of_the_set():
    project = manifest()['project']
    version = tomllib.loads(FRAMEWORK.read_text())['project']['version']
    core = tomllib.loads(FRAMEWORK.read_text())['project']
    assert project['name'] == 'machinome-movie'
    assert project['version'] == version
    assert project['dependencies'] == [f'machinome~={version}',
                                       f'machinome-viewer~={version}',
                                       'jsonschema']
    assert project['license'] == core['license']
    assert project['license-files'] == ['LICENSE', 'LICENSES/*.txt']
    assert project['entry-points']['machinome.commands'] == {
        'movie': 'machinome.movie.cli:Movie'}
    assert manifest()['tool']['setuptools']['packages']['find'] == {
        'include': ['machinome.movie'], 'namespaces': True}


def test_the_package_is_a_portion_of_machinome():
    assert (PACKAGE / 'machinome' / 'movie' / '__init__.py').is_file()
    assert not (PACKAGE / 'machinome' / '__init__.py').exists()
    import machinome.movie
    assert Path(machinome.movie.__file__).resolve() == \
        PACKAGE / 'machinome' / 'movie' / '__init__.py'


def test_no_module_of_the_former_name_is_provided():
    assert importlib.util.find_spec('machinome' '_movie') is None


def test_the_command_s_module_loads_no_evaluation():
    loaded = fresh('import machinome.movie.cli')
    for module in ('jsonschema', 'machinome.movie.document',
                   'machinome.movie.evaluate', 'machinome.movie.take'):
        assert module not in loaded, module


def test_a_name_is_read_from_its_module_when_it_is_used():
    loaded = fresh('from machinome.movie import Movie, Take\n'
                   'from machinome.movie.movie import Movie as M\n'
                   'from machinome.movie.take import Take as T\n'
                   'assert Movie is M and Take is T')
    assert 'machinome.movie.movie' in loaded
    assert 'machinome.movie.take' in loaded
    assert 'machinome.movie.evaluate' not in loaded


def test_every_exported_name_is_its_module_s():
    import machinome.movie as package
    for name in package.__all__:
        value = getattr(package, name)
        module = importlib.import_module(value.__module__)
        assert getattr(module, name) is value, name


def test_the_function_evaluate_keeps_its_name_beside_its_module():
    # The package's name `evaluate` is the function, as the eager root bound
    # it, even after its module is imported by its own name, which binds the
    # submodule to the package's attribute of that name.
    for first in ('import machinome.movie.evaluate',
                  'from machinome.movie.evaluate import write',
                  'from machinome.movie import dumps',
                  'import machinome.movie'):
        done = subprocess.run(
            [sys.executable, '-c',
             f'{first}\nimport types\nimport machinome.movie as package\n'
             'from machinome.movie import evaluate\n'
             'assert not isinstance(evaluate, types.ModuleType), evaluate\n'
             'assert not isinstance(package.evaluate, types.ModuleType)\n'
             'assert evaluate.__module__ == "machinome.movie.evaluate"'],
            capture_output=True, text=True)
        assert done.returncode == 0, (first, done.stderr)
