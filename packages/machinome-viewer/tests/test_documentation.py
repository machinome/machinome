"""Documentation is a distributed, user-facing part of the viewer."""

from pathlib import Path
import ast
import json
import re
import tomllib

ROOT = Path(__file__).resolve().parents[1]


def test_manual_and_hosting_configuration_exist():
    for name in (
        'docs/index.rst', 'docs/conf.py', 'docs/requirements.txt',
        'docs/installation.rst', 'docs/using-the-viewer.rst',
        'docs/embedding.rst', 'docs/reference/cli.rst', '.readthedocs.yaml',
        'docs/examples/embed.html', 'workflow/documentation.md',
    ):
        assert (ROOT / name).is_file(), name


def test_docs_contains_no_development_records():
    assert not (ROOT / 'docs/adrs').exists()
    assert not (ROOT / 'docs/release-0.2.md').exists()
    assert not (ROOT / 'docs/release-0.7.md').exists()
    assert (ROOT / 'workflow/adrs/README.md').is_file()
    assert not (ROOT / 'workflow/release-0.2.md').exists()
    assert (ROOT / 'workflow/release-0.7.md').is_file()


def test_the_manual_states_the_release():
    """0.7.0 released with Machinome 0.7.0: nothing reader-facing says otherwise."""
    pages = sorted((ROOT / 'docs').rglob('*.rst'))
    assert pages
    for page in pages + [ROOT / 'README.md']:
        text = page.read_text()
        assert 'unreleased' not in text.lower(), page
        assert 'not yet published' not in text.lower(), page
    changelog = (ROOT / 'CHANGELOG.md').read_text()
    sections = re.split(r'^## ', changelog, flags=re.M)
    # A new correction must not be silently attributed to the prior release.
    # Keep its historical entry intact below an explicitly pending section.
    release_sections = sections[1:]
    if release_sections[0].startswith('Unreleased\n'):
        assert 'API 24' in release_sections[0]
        release_sections = release_sections[1:]
    current = ' '.join(release_sections[0].split())
    assert current.startswith('0.7.0 — 21 September 2026'), current[:40]
    assert 'unreleased' not in current.lower()
    assert 'Machinome 0.7.0' in current
    project = tomllib.loads((ROOT / 'pyproject.toml').read_text())['project']
    assert project['version'] == '0.7.0'
    assert (ROOT / 'README.md').read_text().count('0.7.0') >= 1


def test_package_points_readers_to_manual():
    project = tomllib.loads((ROOT / 'pyproject.toml').read_text())['project']
    assert project['urls']['Documentation'] == 'https://machinome-viewer.readthedocs.io/'
    requirements = (ROOT / 'docs/requirements.txt').read_text().splitlines()
    assert project['optional-dependencies']['docs'] == requirements


def test_documentation_source_manifest():
    manifest = (ROOT / 'MANIFEST.in').read_text()
    assert 'include .readthedocs.yaml' in manifest
    assert 'recursive-include docs' in manifest
    assert 'prune docs/_build' in manifest
    assert 'prune tests/_shots' in manifest
    assert 'docs/release-0.2.md' not in manifest


def test_cli_options_are_all_documented():
    source = ast.parse((ROOT / 'machinome_viewer/cli.py').read_text())
    reference = (ROOT / 'docs/reference/cli.rst').read_text()
    options = set()
    for node in ast.walk(source):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == 'add_argument':
                options.update(argument.value for argument in node.args
                               if isinstance(argument, ast.Constant)
                               and isinstance(argument.value, str)
                               and argument.value.startswith('-'))
    assert options
    assert all(option in reference for option in options), options


def test_describe_example_matches_package_versions():
    reference = (ROOT / 'docs/reference/cli.rst').read_text()
    block = re.search(r'\.\. code-block:: json\n\n((?:   .*\n|\n)+)', reference)
    example = json.loads(block[1])
    widget = json.loads((ROOT / 'machinome_viewer/widget/package.json').read_text())
    project = tomllib.loads((ROOT / 'pyproject.toml').read_text())['project']
    assert example['version'] == project['version'] == widget['version']
    assert example['apiVersion'] == widget['machinomeViewerApi']
    assert example['documentVersions'] == widget['machinomeDocumentVersions']
