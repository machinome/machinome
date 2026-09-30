"""Layer 1: the command line lists and evaluates the movies a project
declares in `[tool.machinome.movies]`, on a copy of the fixture project."""

import json
import shutil
import subprocess
import sys

import pytest

from conftest import FIXTURES, PROJECT


def run(*args):
    return subprocess.run([sys.executable, '-m', 'machinome_movie', *map(str, args)],
                          capture_output=True, text=True, env={'PATH': '/usr/bin:/bin',
                                                              'PYTHONDONTWRITEBYTECODE': '1'})


@pytest.fixture
def copy(tmp_path):
    target = tmp_path / 'project'
    shutil.copytree(PROJECT, target, ignore=shutil.ignore_patterns('_build', '__pycache__'))
    return target


def test_list_prints_the_table_in_order(copy):
    result = run('list', copy)
    assert result.returncode == 0, result.stderr
    assert result.stdout == ('minimal\tvideos.minimal.movie:Minimal\n'
                             'tour\tvideos.tour.movie:Tour\n')


def test_evaluate_writes_beside_the_movie(copy):
    result = run('evaluate', copy, 'minimal')
    assert result.returncode == 0, result.stderr
    written = copy / 'videos' / 'minimal' / '_build' / 'movie.json'
    assert result.stdout.strip() == str(written)
    document = json.loads(written.read_text())
    assert document['root'] == '..'
    pinned = json.loads((FIXTURES / 'documents' / 'minimal.json').read_text())
    document.pop('root'), pinned.pop('root')
    assert document == pinned


def test_evaluate_to_a_chosen_file(copy, tmp_path):
    out = tmp_path / 'out' / 'tour.json'
    result = run('evaluate', copy, 'tour', '--out', out)
    assert result.returncode == 0, result.stderr
    assert json.loads(out.read_text())['root'] == '../project/videos/tour'


def test_unknown_movie_is_refused_naming_the_table(copy):
    result = run('evaluate', copy, 'trailer')
    assert result.returncode == 1
    assert result.stderr.startswith('machinome-movie: ')
    for name in ('trailer', 'minimal', 'tour'):
        assert name in result.stderr


def test_project_without_a_movies_table(tmp_path):
    (tmp_path / 'pyproject.toml').write_text('[tool.machinome.models]\nm = "m:M"\n')
    result = run('list', tmp_path)
    assert result.returncode == 1
    assert '[tool.machinome.movies]' in result.stderr
