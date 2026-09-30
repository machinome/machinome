"""Layer 2: the shared fixtures pin the document.

Every document registered in fixtures/manifest.json is exactly what its
fixture movie evaluates to (or, for a document written by hand on the Node
side, is accepted by check_document), and every invalid fixture is refused
naming its `must_mention` substrings. A fixture's export manifest and source
excerpts are read through its `root`, as the Node side reads them.
"""

import json
from pathlib import Path

import pytest

from machinome_movie import MovieError, check_document, dumps, evaluate, load_movie

from conftest import FIXTURES, PROJECT

REGISTERED = json.loads((FIXTURES / 'manifest.json').read_text())['documents']
INVALID = sorted((FIXTURES / 'invalid').glob('*.json'))

#: Invalid fixtures whose fault only the Node resolver can see, because it
#: needs the resolved seconds of a spoken anchor. Name -> reason.
RESOLVER_ONLY = {}


def test_both_fixture_movies_are_registered():
    assert {'minimal', 'tour'} <= set(REGISTERED)


@pytest.mark.parametrize('name', REGISTERED)
def test_document_is_the_evaluation_of_its_movie(name):
    path = FIXTURES / 'documents' / f'{name}.json'
    try:
        movie = load_movie(PROJECT, name)
    except MovieError as refusal:
        # A document written by hand on the Node side has no fixture movie
        # here; Python then asserts that it accepts the document as written.
        if 'declares no movie' not in str(refusal):
            raise
        document = json.loads(path.read_text(encoding='utf-8'))
        check_document(document, manifest=manifest_for(document, path.parent),
                       sources=sources_for(document, path.parent))
        return
    evaluated = dumps(evaluate(movie, name=name, out=path))
    assert evaluated == path.read_text(encoding='utf-8'), (
        f'fixtures/documents/{name}.json differs from the evaluation of the fixture movie {name}')


def manifest_for(document, base):
    manifest = (base / document['root'] / document['model']['manifest']).resolve()
    return json.loads(manifest.read_text()) if manifest.is_file() else None


def sources_for(document, base):
    """The text of each source excerpt whose file is in the repository."""
    texts = {}
    for name, excerpt in document.get('sourceCode', {}).items():
        path = (base / document['root'] / excerpt['file']).resolve()
        if path.is_file():
            first, last = excerpt['lines']
            texts[name] = ''.join(path.read_text(encoding='utf-8').splitlines(True)[first - 1:last])
    return texts


@pytest.mark.parametrize('path', INVALID, ids=[p.stem for p in INVALID])
def test_invalid_fixture_is_refused_naming_its_subjects(path):
    fixture = json.loads(path.read_text(encoding='utf-8'))
    if fixture['name'] in RESOLVER_ONLY:
        pytest.skip(RESOLVER_ONLY[fixture['name']])
    document = fixture['document']
    with pytest.raises(MovieError) as refusal:
        check_document(document, manifest=manifest_for(document, path.parent),
                       sources=sources_for(document, path.parent))
    for mention in fixture['must_mention']:
        assert mention in str(refusal.value), f'{mention!r} not named in: {refusal.value}'


def test_there_are_invalid_fixtures():
    assert INVALID


def test_every_invalid_fixture_is_named_after_its_file():
    for path in INVALID:
        fixture = json.loads(path.read_text(encoding='utf-8'))
        assert fixture['name'] == path.stem
        assert fixture['must_mention'], path.name
