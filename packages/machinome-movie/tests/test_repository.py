"""Layer 9: repository pins.

The schema is the one file both runtimes read; every document Python emits
validates against it; the fixture project's revision is reproducible; the
manual page exists, is linked, and its examples are the fixture's own code.
"""

import json
import os
import re
import shutil
import subprocess
from importlib import resources

import jsonschema
import pytest

from machinome_movie import MovieError, dumps, evaluate, load_movie

from conftest import FIXTURES, PROJECT, REPOSITORY, SCHEMA

REGISTERED = json.loads((FIXTURES / 'manifest.json').read_text())['documents']


def test_the_package_ships_the_repository_schema():
    packaged = resources.files('machinome_movie').joinpath('machinome-movie-0.1.json')
    assert packaged.read_bytes() == SCHEMA.read_bytes()


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
    pinned = (PROJECT / 'export' / 'seesaw' / 'source-revision.txt').read_text().strip()
    assert head == pinned, f'export/seesaw/source-revision.txt should read {head}'


PAGE = REPOSITORY / 'docs' / 'declaring-a-movie.md'


def test_the_manual_page_exists_and_is_linked():
    assert PAGE.is_file()
    assert '](docs/declaring-a-movie.md)' in (REPOSITORY / 'README.md').read_text()


def test_the_manual_names_no_project_or_checkout():
    text = PAGE.read_text()
    for word in ('Leonardo', 'worktree', 'WTs/', 'sawmill'):
        assert word not in text, word


def test_the_manuals_examples_are_the_fixtures_code():
    text = PAGE.read_text()
    blocks = re.findall(r'```python\n(.*?)```', text, flags=re.S)
    assert blocks
    sources = '\n'.join(path.read_text() for path in PROJECT.rglob('*.py'))
    for block in blocks:
        for line in block.rstrip('\n').split('\n'):
            if line.strip() and line.strip() != '...':
                assert line in sources, f'manual line not in the fixture project: {line!r}'


def test_the_changelog_has_an_unreleased_section_with_this_change():
    text = (REPOSITORY / 'CHANGELOG.md').read_text()
    assert '## Unreleased' in text
    assert 'machinome-movie' in text
