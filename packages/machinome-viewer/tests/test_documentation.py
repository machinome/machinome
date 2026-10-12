"""Documentation is a distributed, user-facing part of the viewer.

The viewer's pages are part of the Machinome manual (change `join-viewer`):
three how-to guides and the reference section `reference/viewer/`, built
with the manual from `packages/machinome/docs/`. The package keeps its
changelog and its working record; it carries no manual of its own.
"""

from pathlib import Path
import ast
import json
import re
import tomllib

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = Path(__file__).resolve().parents[3]
MANUAL = REPOSITORY / 'packages' / 'machinome' / 'docs'
WIDGET = ROOT / 'machinome' / 'viewer' / 'web' / 'widget'
SEPARATE = 'machinome-viewer.readthedocs.io'

#: The viewer's pages of the manual.
PAGES = (
    'howto/browser-viewer.rst', 'howto/share-an-export.rst',
    'howto/embed-the-viewer.rst', 'reference/viewer/index.rst',
    'reference/viewer/mount.rst', 'reference/viewer/viewer-handle.rst',
    'reference/viewer/layouts.rst', 'reference/viewer/running.rst',
    'reference/viewer/clocked.rst', 'reference/viewer/cli.rst',
    'reference/viewer/compatibility.rst',
    'reference/viewer/troubleshooting.rst',
)


def widget():
    return json.loads((WIDGET / 'package.json').read_text())


def conf_value(name):
    conf = (MANUAL / 'conf.py').read_text()
    return re.search(rf"^{name} = '([^']*)'", conf, flags=re.M)[1]


def flat(page):
    return ' '.join((MANUAL / page).read_text().split())


def test_the_pages_are_in_the_manual():
    for name in PAGES + ('howto/embed-the-viewer/embed.html',
                         'howto/embed-the-viewer/embed.js'):
        assert (MANUAL / name).is_file(), name
    for name in ('docs', '.readthedocs.yaml'):
        assert not (ROOT / name).exists(), name
    assert (ROOT / 'workflow/documentation.md').is_file()


def test_docs_contains_no_development_records():
    assert (ROOT / 'workflow/adrs/README.md').is_file()
    assert not (ROOT / 'workflow/release-0.2.md').exists()
    assert (ROOT / 'workflow/release-0.7.md').is_file()
    assert (ROOT / 'workflow/release-0.8.md').is_file()


def test_the_manual_states_the_release():
    """0.8.1 released with Machinome 0.8.1: nothing reader-facing says otherwise."""
    for page in [MANUAL / name for name in PAGES] + [ROOT / 'README.md']:
        text = page.read_text()
        assert 'unreleased' not in text.lower(), page
        assert 'not yet published' not in text.lower(), page
    changelog = (ROOT / 'CHANGELOG.md').read_text()
    sections = re.split(r'^## ', changelog, flags=re.M)
    # A change writes its changelog entry when it lands (the pilot's
    # ruling of 29 September 2026), under ONE `Unreleased` section above
    # the release; the release is the first section after it.
    release_sections = sections[1:]
    if release_sections[0].startswith('Unreleased'):
        release_sections = release_sections[1:]
    assert not any(one.startswith('Unreleased') for one in release_sections)
    current = ' '.join(release_sections[0].split())
    assert current.startswith('0.8.1 — 10 October 2026'), current[:40]
    assert 'unreleased' not in current.lower()
    assert 'Machinome 0.8.1' in current
    assert 'published 0.8.0 renumbered' in current
    versions = widget()['machinomeDocumentVersions']
    assert f"viewer API {widget()['machinomeViewerApi']}" in current
    assert 'viewer API 29' in current
    assert f'document versions {versions[0]} through {versions[-1]}' in current
    assert 'released-viewer-api' not in (MANUAL / 'conf.py').read_text()
    project = tomllib.loads((ROOT / 'pyproject.toml').read_text())['project']
    assert project['version'] == '0.8.1'


def test_the_release_facts_are_the_widget_s():
    versions = widget()['machinomeDocumentVersions']
    assert conf_value('viewer_api') == str(widget()['machinomeViewerApi'])
    assert conf_value('document_versions') == f'{versions[0]} to {versions[-1]}'
    assert conf_value('viewer_version') == widget()['version']


def test_the_manifest_names_no_documentation_url_but_the_homepage():
    project = tomllib.loads((ROOT / 'pyproject.toml').read_text())['project']
    assert project['urls'] == {
        'Homepage': 'https://github.com/machinome/machinome'}
    assert 'docs' not in project.get('optional-dependencies', {})


def test_no_page_links_the_separate_manual():
    pages = [page for page in sorted(MANUAL.rglob('*.rst'))
             if '_build' not in page.relative_to(MANUAL).parts]
    for page in pages + [ROOT / 'README.md']:
        assert SEPARATE not in page.read_text(), page


def test_documentation_source_manifest():
    manifest = (ROOT / 'MANIFEST.in').read_text()
    assert '.readthedocs.yaml' not in manifest
    assert 'recursive-include docs' not in manifest
    assert 'prune tests/_shots' in manifest
    assert 'docs/release-0.2.md' not in manifest


def test_cli_options_are_all_documented():
    source = ast.parse((ROOT / 'machinome/viewer/web/cli.py').read_text())
    reference = (MANUAL / 'reference/viewer/cli.rst').read_text()
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
    reference = (MANUAL / 'reference/viewer/cli.rst').read_text()
    block = re.search(r'\.\. code-block:: json\n\n((?:   .*\n|\n)+)', reference)
    example = json.loads(block[1])
    project = tomllib.loads((ROOT / 'pyproject.toml').read_text())['project']
    assert example['version'] == project['version'] == widget()['version']
    assert example['apiVersion'] == widget()['machinomeViewerApi']
    assert example['documentVersions'] == widget()['machinomeDocumentVersions']
    assert '/machinome/viewer/web/widget/' in example['path']


def test_full_screen_is_documented():
    """OpenSpec `go-fullscreen`: the manual names the key and the iframe
    permission, and the changelog records the capability in the section
    D11 chose -- the 0.7.0 record."""
    manual = (MANUAL / 'howto/browser-viewer.rst').read_text()
    assert 'full screen' in manual.lower()
    assert '**f**' in manual
    assert 'Escape' in manual
    embedding = (MANUAL / 'howto/embed-the-viewer.rst').read_text()
    assert 'allowfullscreen' in embedding
    layouts = (MANUAL / 'reference/viewer/layouts.rst').read_text()
    assert 'machinome-fullscreen' in layouts
    changelog = (ROOT / 'CHANGELOG.md').read_text()
    release = changelog.split('## 0.7.0 — 23 September 2026')[1].split('\n## ')[0]
    assert 'Full screen' in release
    assert '`f` key' in release or '`f`' in release
    assert 'allowfullscreen' in release


def test_profile_contact_is_documented_as_part_of_the_release():
    # Profile contact is in every source from API 26 on; the release
    # record below pins what 0.7.0 declared (OpenSpec
    # `track-a-part-on-screen`, D9).
    assert widget()['machinomeViewerApi'] >= 27
    assert widget()['machinomeDocumentVersions'][-1] == 13
    compatibility = (MANUAL / 'reference/viewer/compatibility.rst').read_text()
    running = (MANUAL / 'reference/viewer/running.rst').read_text()
    changelog = (ROOT / 'CHANGELOG.md').read_text()
    assert 'baseline' not in (MANUAL / 'conf.py').read_text()
    assert 'API 27, the 0.7.0 release' in compatibility
    assert 'API 26 reads\nversion-13 finite convex-profile contact' in compatibility
    assert 'released-viewer-api' not in compatibility
    assert 'pointwise' in running.lower()
    assert 'continuous' in running.lower()
    release = changelog.split('## 0.7.0 — 23 September 2026')[1].split('\n## ')[0]
    assert 'profileOverlap' in release
    assert 'API 26 and\n  version 13 by finite profile contact' in release
    assert 'It declares viewer API 27' in ' '.join(release.split())


def test_film_annotations_are_documented_as_part_of_the_0_8_0_release():
    """OpenSpec `track-a-part-on-screen`, as released by `release-0-8-0`:
    API 28 arrives in 0.8.0, and the recorded 0.7.1 facts stay at API 27."""
    # 28 or later: `on-demand-clocked` declares 29 on top of it.
    assert widget()['machinomeViewerApi'] >= 28
    assert widget()['machinomeDocumentVersions'] == list(range(1, 14))
    compatibility = flat('reference/viewer/compatibility.rst')
    assert 'This release declares:' in compatibility
    assert '**Viewer API** |viewer_api|' in compatibility
    assert 'API 28 and API 29, the 0.8.0 release' in compatibility
    assert 'in no published release' not in compatibility
    assert 'API 28 adds' in compatibility
    index = flat('reference/viewer/index.rst')
    assert ('declares viewer API |viewer_api| and reads document versions '
            '|document_versions|') in index
    changelog = (ROOT / 'CHANGELOG.md').read_text()
    release = changelog.split('## 0.8.0 — 5 October 2026')[1].split('\n## ')[0]
    for member in ('partOnScreen(', 'project(', 'highlight(', 'setView('):
        assert member in release, member
    assert 'API 28' in release
    # The recorded 0.7.1 facts stay at API 27.
    released = changelog.split('## 0.7.1 — 27 September 2026')[1]
    assert 'API 28' not in released
    handle = (MANUAL / 'reference/viewer/viewer-handle.rst').read_text()
    assert '.. js:method:: ViewerHandle.partOnScreen(path)' in handle
    assert '.. js:method:: ViewerHandle.project(world)' in handle
    assert 'available since API 28' in handle
    assert '.. js:method:: ViewerHandle.highlight(paths, options)' in handle
    assert ':js:meth:`ViewerHandle.highlight`' in compatibility
    assert 'Return a detached snapshot ``{camera, target, up, fov}``' in handle
    assert 'optional ``fov``' in ' '.join(handle.split())
    mount = (MANUAL / 'reference/viewer/mount.rst').read_text()
    assert '.. js:attribute:: ViewInput.up' in mount
    assert '.. js:attribute:: ViewInput.fov' in mount
    for name in PAGES:
        text = (MANUAL / name).read_text().lower()
        for word in ('videomaker', 'revolutions', 'leonardo', ' film'):
            assert word not in text, (name, word)


def test_on_demand_clocked_capture_is_documented():
    """OpenSpec `on-demand-clocked`: API 29, released in 0.8.0; the
    manual states the on-demand rules for a clocked machine, and the
    0.8.0 changelog section records it."""
    assert widget()['machinomeViewerApi'] == 29
    assert widget()['machinomeDocumentVersions'] == list(range(1, 14))
    mount = flat('reference/viewer/mount.rst')
    assert 'accepts a clocked machine' in mount
    assert 'refuses a running program' in mount
    assert 'no full-screen control' in mount
    clocked = flat('reference/viewer/clocked.rst')
    assert 'On-demand capture' in clocked
    assert 'setView(viewer.view())' in clocked
    assert "renderMode 'on-demand'" in clocked
    compatibility = flat('reference/viewer/compatibility.rst')
    assert 'API 29 adds' in compatibility
    changelog = (ROOT / 'CHANGELOG.md').read_text()
    release = changelog.split('## 0.8.0 — 5 October 2026')[1].split('\n## ')[0]
    flat_release = ' '.join(release.split())
    assert 'viewer API 29' in flat_release
    assert 'on-demand' in flat_release
    assert changelog.index('## 0.8.0') < changelog.index('## 0.7.1')
