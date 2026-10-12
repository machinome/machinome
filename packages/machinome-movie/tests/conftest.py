"""Shared paths for the machinome-movie suite.

The fixture project is put on `sys.path` once, as the command line puts a
project there, so its model and its movies import by their project names.
"""

import sys
from pathlib import Path

import pytest

TESTS = Path(__file__).resolve().parent
PYTHON = TESTS.parent
# The Node side's directory inside the package, which holds the fixture
# documents and the schema both runtimes read (change `join-movie`).
REPOSITORY = PYTHON / 'machinome' / 'movie' / 'js'
PROJECT = TESTS / 'fixtures' / 'project'
FIXTURES = REPOSITORY / 'fixtures'
SCHEMA = REPOSITORY / 'schema' / 'machinome-movie-0.2.json'

if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))


@pytest.fixture
def project():
    return PROJECT
