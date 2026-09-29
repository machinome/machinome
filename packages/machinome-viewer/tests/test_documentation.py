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
    """0.7.1 released with Machinome 0.7.1: nothing reader-facing says otherwise."""
    pages = sorted((ROOT / 'docs').rglob('*.rst'))
    assert pages
    for page in pages + [ROOT / 'README.md']:
        text = page.read_text()
        assert 'unreleased' not in text.lower(), page
        assert 'not yet published' not in text.lower(), page
    changelog = (ROOT / 'CHANGELOG.md').read_text()
    sections = re.split(r'^## ', changelog, flags=re.M)
    # 0.7.1 ships the current source: no pending section sits above it.
    release_sections = sections[1:]
    assert not release_sections[0].startswith('Unreleased'), release_sections[0][:40]
    current = ' '.join(release_sections[0].split())
    assert current.startswith('0.7.1 — 27 September 2026'), current[:40]
    assert 'unreleased' not in current.lower()
    assert 'Machinome 0.7.1' in current
    widget = json.loads((ROOT / 'machinome_viewer/widget/package.json').read_text())
    versions = widget['machinomeDocumentVersions']
    # The recorded release, not the live declaration: the source runs
    # ahead of it at API 28 (OpenSpec `track-a-part-on-screen`, D9).
    assert 'viewer API 27' in current
    assert f'document versions {versions[0]} through {versions[-1]}' in current
    assert 'released-viewer-api' not in (ROOT / 'docs/conf.py').read_text()
    project = tomllib.loads((ROOT / 'pyproject.toml').read_text())['project']
    assert project['version'] == '0.7.1'
    assert (ROOT / 'README.md').read_text().count('0.7.1') >= 1


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


def test_full_screen_is_documented():
    """OpenSpec `go-fullscreen`: the manual names the key and the iframe
    permission, and the changelog records the capability in the section
    D11 chose -- the 0.7.0 record, while it is at released state but not
    uploaded (see `test_the_manual_states_the_release`)."""
    manual = (ROOT / 'docs/using-the-viewer.rst').read_text()
    assert 'full screen' in manual.lower()
    assert '**f**' in manual
    assert 'Escape' in manual
    embedding = (ROOT / 'docs/embedding.rst').read_text()
    assert 'allowfullscreen' in embedding
    layouts = (ROOT / 'docs/reference/layouts.rst').read_text()
    assert 'machinome-fullscreen' in layouts
    changelog = (ROOT / 'CHANGELOG.md').read_text()
    release = changelog.split('## 0.7.0 — 23 September 2026')[1].split('\n## ')[0]
    assert 'Full screen' in release
    assert '`f` key' in release or '`f`' in release
    assert 'allowfullscreen' in release


def test_profile_contact_is_documented_as_part_of_the_release():
    widget = json.loads((ROOT / 'machinome_viewer/widget/package.json').read_text())
    # Profile contact is in every source from API 26 on; the release
    # record below pins what 0.7.0 declared (OpenSpec
    # `track-a-part-on-screen`, D9).
    assert widget['machinomeViewerApi'] >= 27
    assert widget['machinomeDocumentVersions'][-1] == 13
    compatibility = (ROOT / 'docs/compatibility.rst').read_text()
    running = (ROOT / 'docs/reference/running.rst').read_text()
    changelog = (ROOT / 'CHANGELOG.md').read_text()
    assert 'baseline' not in (ROOT / 'docs/conf.py').read_text()
    assert 'API 27, the 0.7.0 release' in compatibility
    assert 'API 26 reads\nversion-13 finite convex-profile contact' in compatibility
    assert 'released-viewer-api' not in compatibility
    assert 'pointwise' in running.lower()
    assert 'continuous' in running.lower()
    assert '## Unreleased' not in changelog
    release = changelog.split('## 0.7.0 — 23 September 2026')[1].split('\n## ')[0]
    assert 'profileOverlap' in release
    assert 'API 26 and\n  version 13 by finite profile contact' in release
    assert 'It declares viewer API 27' in ' '.join(release.split())


def test_film_annotations_are_documented_as_current_source():
    """OpenSpec `track-a-part-on-screen`, design D9: the source declares
    API 28 after 0.7.1, in no published release, and the recorded 0.7.1
    facts stay at API 27."""
    widget = json.loads((ROOT / 'machinome_viewer/widget/package.json').read_text())
    assert widget['machinomeViewerApi'] == 28
    assert widget['machinomeDocumentVersions'] == list(range(1, 14))
    compatibility = ' '.join((ROOT / 'docs/compatibility.rst').read_text().split())
    assert 'The 0.7.1 release declares:' in compatibility
    assert '**Viewer API** 27' in compatibility
    assert ('The current source, after 0.7.1 and in no published release, '
            'declares viewer API |viewer-api|') in compatibility
    assert 'API 28 adds' in compatibility
    index = ' '.join((ROOT / 'docs/index.rst').read_text().split())
    assert 'declares viewer API 27 and reads document versions' in index
    assert 'viewer API **27**' in (ROOT / 'README.md').read_text()
    changelog = (ROOT / 'CHANGELOG.md').read_text()
    assert '## Unreleased' not in changelog
    assert 'API 28' not in changelog
    handle = (ROOT / 'docs/reference/viewer-handle.rst').read_text()
    assert '.. js:method:: ViewerHandle.partOnScreen(path)' in handle
    assert '.. js:method:: ViewerHandle.project(world)' in handle
    assert 'available since API 28' in handle
    for page in sorted((ROOT / 'docs').rglob('*.rst')):
        text = page.read_text().lower()
        for word in ('videomaker', 'revolutions', 'leonardo', ' film'):
            assert word not in text, (page, word)
