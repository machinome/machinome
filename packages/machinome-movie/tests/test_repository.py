"""Layer 9: repository pins.

The schema is the one file both runtimes read; every document Python emits
validates against it; the fixture project's revision is reproducible; the
manual page exists, is linked, and its examples are the fixture's own code.
The manual is the machinome framework's, which these pages joined with the
package (change `join-movie` of the machinome repository).
"""

import json
import os
import re
import shutil
import subprocess
from importlib import resources

import jsonschema
import pytest

from machinome.movie import MovieError, dumps, evaluate, load_movie

from conftest import FIXTURES, PROJECT, PYTHON, REPOSITORY, SCHEMA

REGISTERED = json.loads((FIXTURES / 'manifest.json').read_text())['documents']

#: The framework's manual, beside this package in the repository.
MANUAL = PYTHON.parent / 'machinome' / 'docs'
#: The how-to that teaches the declarations, and the pages the films fold
#: into: the guide, the command, the document and the episode format.
PAGE = MANUAL / 'howto' / 'declare-a-movie.rst'
FILM = MANUAL / 'howto' / 'film-a-movie.rst'
PAGES = [PAGE, FILM, MANUAL / 'howto' / 'draw-a-movie-stage.rst',
         *sorted((MANUAL / 'reference' / 'movie').glob('*.rst'))]


def words(path):
    return ' '.join(path.read_text().split())


def section_titles(text):
    """A reStructuredText page's section titles, in order."""
    return re.findall(r'^(\S.*)\n[=\-~]{3,}$', text, flags=re.M)


def test_the_package_ships_the_repository_schema():
    packaged = resources.files('machinome.movie').joinpath('machinome-movie-0.2.json')
    assert packaged.read_bytes() == SCHEMA.read_bytes()
    assert json.loads(SCHEMA.read_text())['title'] == 'machinome-movie/0.2'


def test_nothing_of_0_1_is_left_in_the_package_the_manual_or_the_fixtures():
    # The pilot's ruling: 0.1 was a step, not a protocol; nothing of it is kept.
    assert not (REPOSITORY / 'schema' / 'machinome-movie-0.1.json').exists()
    places = [*(PYTHON / 'machinome' / 'movie').iterdir(), PYTHON / 'README.md', PYTHON / 'pyproject.toml',
              PAGE, FIXTURES / 'README.md', FIXTURES / 'manifest.json',
              *(FIXTURES / 'documents').glob('*.json'), *(FIXTURES / 'invalid').glob('*.json')]
    for path in places:
        if path.is_file() and path.suffix in ('.py', '.md', '.rst', '.json', '.toml'):
            text = path.read_text(encoding='utf-8')
            for stale in ('machinome-movie/0.1', 'machinome-movie-0.1'):
                assert stale not in text, f'{path.relative_to(REPOSITORY)} still names {stale}'


def test_the_schema_is_a_2020_12_schema():
    schema = json.loads(SCHEMA.read_text())
    assert schema['$schema'] == 'https://json-schema.org/draft/2020-12/schema'
    jsonschema.Draft202012Validator.check_schema(schema)


@pytest.mark.parametrize('name', REGISTERED)
def test_every_emitted_document_validates(name):
    schema = json.loads(SCHEMA.read_text())
    try:
        movie = load_movie(PROJECT, name)
    except MovieError as refusal:
        # A document written by hand on the Node side has no movie to emit it
        # from; it is validated as written.
        if 'declares no movie' not in str(refusal):
            raise
        document = json.loads((FIXTURES / 'documents' / f'{name}.json').read_text(encoding='utf-8'))
    else:
        document = json.loads(dumps(evaluate(movie, name=name)))
    jsonschema.Draft202012Validator(schema).validate(document)


def test_the_schema_closes_field_lists():
    schema = json.loads(SCHEMA.read_text())
    document = json.loads((FIXTURES / 'documents' / 'minimal.json').read_text())
    document['chapters'][0]['shots'][0]['transiton'] = {'kind': 'dissolve', 'duration': 1}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(document, schema, cls=jsonschema.Draft202012Validator)


FIXED = {'GIT_AUTHOR_NAME': 'Videomaker fixture', 'GIT_AUTHOR_EMAIL': 'fixture@videomaker.invalid',
         'GIT_AUTHOR_DATE': '2026-09-30T00:00:00+00:00',
         'GIT_COMMITTER_NAME': 'Videomaker fixture', 'GIT_COMMITTER_EMAIL': 'fixture@videomaker.invalid',
         'GIT_COMMITTER_DATE': '2026-09-30T00:00:00+00:00',
         'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_NOSYSTEM': '1', 'PATH': '/usr/bin:/bin'}


def test_the_fixture_revision_is_a_reproducible_commit_of_the_project(tmp_path):
    # The recipe fixtures/README.md gives: every file of the fixture project
    # but its export and build products, committed with a fixed identity,
    # date and message into a fresh repository.
    copy = tmp_path / 'project'
    shutil.copytree(PROJECT, copy, ignore=shutil.ignore_patterns('export', '_build', '__pycache__'))
    for command in (['init', '-q'], ['add', '-A'], ['commit', '-q', '-m', 'Fixture project']):
        subprocess.run(['git', *command], cwd=copy, env=FIXED, check=True)
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=copy, env=FIXED, check=True,
                          capture_output=True, text=True).stdout.strip()
    exports = sorted(path.parent.name for path in (PROJECT / 'export').glob('*/manifest.json'))
    assert exports == ['counter', 'seesaw']
    # Each export was made by the framework from that commit, which its
    # manifest records clean (scripts/pin-fixture-project.mjs); no sidecar
    # beside it names the revision.
    for name in exports:
        recorded = json.loads((PROJECT / 'export' / name / 'manifest.json').read_text()).get('source')
        assert recorded == {'revision': head, 'dirty': False}, \
            f'export/{name}/manifest.json should record source {{revision: {head}, dirty: false}}'
        assert not (PROJECT / 'export' / name / 'source-revision.txt').exists()


def test_the_counter_is_the_framework_tutorials_clocked_export():
    # The fixture's clocked machine is copied, not invented, and exported for
    # real: its manifest is a clocked root's, document version 8.
    source = (PROJECT / 'models' / 'counter.py').read_text()
    assert 'docs/tutorial/counter/' in source and 'GPL-2.0-or-later OR CERN-OHL-S-2.0-or-later' in source
    manifest = json.loads((PROJECT / 'export' / 'counter' / 'manifest.json').read_text())
    assert manifest['version'] == 8 and manifest['clocked']['identity']
    assert set(manifest['drivers']) == {'crank'} and set(manifest['states']) == {'units', 'tens'}
    notice = (PROJECT / 'NOTICE').read_text()
    assert 'models/counter.py' in notice and 'GPL-2.0-or-later OR CERN-OHL-S-2.0-or-later' in notice


def test_the_manual_page_exists_and_is_linked():
    assert PAGE.is_file()
    assert ':doc:`/howto/declare-a-movie`' in FILM.read_text()
    index = (MANUAL / 'index.rst').read_text()
    assert '   howto/declare-a-movie\n' in index
    text = words(PAGE)
    assert ':doc:`movie document </reference/movie/document>`' in text and 'machinome-movie/0.2' in text


def test_the_manual_says_the_narrator_sets_the_length_and_what_the_end_is():
    # Warts 2 and 7 of the first film declared in Python.
    text = words(PAGE)
    assert 'The narrator sets the film\'s length.' in text
    assert 'estimate a film\'s length by speaking its narration, not by counting its shots' in text
    assert '``check`` prints, for each chapter, its take, its length and its tail' in text
    assert '``lines.end()`` the end of the whole narration' in text
    assert '``{"narrationEnd": true}``' in text


def test_the_manual_names_no_project_or_checkout():
    for word in ('Leonardo', 'worktree', 'WTs/', 'sawmill'):
        assert word not in PAGE.read_text(), word
    for page in PAGES:
        text = page.read_text()
        for word in ('Leonardo', 'worktree', 'WTs/', '../projects', 'machinome_movie'):
            assert word not in text, (page.name, word)


def test_the_manuals_examples_are_the_fixtures_code():
    text = PAGE.read_text()
    blocks = re.findall(r'^\.\. code-block:: python\n\n((?:(?:   .*)?\n)+)', text, flags=re.M)
    assert blocks
    sources = '\n'.join(path.read_text() for path in PROJECT.rglob('*.py'))
    for block in blocks:
        for line in block.rstrip('\n').split('\n'):
            line = line[3:]
            if line.strip() and line.strip() != '...':
                assert line in sources, f'manual line not in the fixture project: {line!r}'


def test_the_changelog_has_an_unreleased_section_with_this_change():
    text = (PYTHON / 'CHANGELOG.md').read_text()
    assert '## Unreleased' in text
    assert 'machinome-movie' in text
    assert '(`declarative-stage`' in text
    assert '(`declare-a-take`' in text


def test_the_manual_teaches_the_clocked_take():
    titles = section_titles(PAGE.read_text())
    assert 'The take, clocked' in titles
    assert titles.index('The take') < titles.index('The take, clocked') \
        < titles.index('The template: sets')
    text = words(PAGE)
    for sentence in (
            'A clocked machine has no loop: it stands at a bank of values and moves when asked.',
            '``Move(input, to=, over=)`` or ``Move(input, by=, over=)``',
            '``Trigger(instruction)`` is drawn over the duration its instruction declares',
            'A frame is a pure function of take time.',
            'Evaluation runs the steps once through the framework\'s simulation of the model',
            '``readiness`` says what the export does and does not show'):
        assert sentence in text, sentence


def test_the_status_line_names_what_is_filmable():
    text = words(FILM)
    assert 'running machines are refused' in text
    assert 'a clocked machine\'s take' in text


def test_the_manual_and_the_command_document_the_watch():
    # The player-page change: `watch` beside `evaluate`.
    text = words(PAGE)
    assert 'machinome movie watch <project-dir> tour' in text
    for sentence in ('``watch`` evaluates the movie as ``evaluate`` does',
                     'passing over ``_build``, ``.git`` and ``__pycache__``',
                     '``--interval``'):
        assert sentence in text, sentence
    assert 'machinome movie watch PROJECT MOVIE [--out FILE] [--interval SECONDS]' in \
        (MANUAL / 'reference' / 'cli.rst').read_text()
    main = (PYTHON / 'machinome' / 'movie' / '__main__.py').read_text()
    assert 'python -m machinome.movie watch <project-dir> <movie-name> [--out FILE] [--interval SECONDS]' in main
