"""Layer 1: `python -m machinome_movie watch` evaluates a movie, then
evaluates it again each time a file of its project changes (the player-page
change). The loop is driven here with an injected listing and sleep, so no
verdict reads a clock; the command line runs once on a copy of the fixture
project, its waits bounded."""

import os
import shutil
import signal
import subprocess
import sys
import time

import pytest

from machinome_movie.watch import Watch, listing

from conftest import PROJECT, PYTHON

A = {'videos/minimal/movie.py': (120, 1_000, 7), 'models/counter.py': (300, 1_000, 8)}


def driven(listings, interval=0.25):
    """A watch over `listings` in turn, recording each evaluation (by how many
    intervals had been slept) and each sleep."""
    queue = list(listings)
    evaluations, slept = [], []
    watch = Watch(evaluate=lambda: evaluations.append(len(slept)), files=lambda: queue.pop(0),
                  sleep=slept.append, interval=interval)
    return watch, evaluations, slept


def test_it_evaluates_once_when_it_starts_and_not_while_nothing_changes():
    watch, evaluations, slept = driven([A, dict(A), dict(A), dict(A)])
    watch.start()
    assert evaluations == [0]
    assert [watch.step() for _ in range(3)] == [False, False, False]
    assert evaluations == [0]
    assert slept == [0.25, 0.25, 0.25]


def test_it_evaluates_once_after_each_change_of_size_time_or_inode():
    sized = {**A, 'videos/minimal/movie.py': (121, 1_000, 7)}
    timed = {**sized, 'videos/minimal/movie.py': (121, 2_000, 7)}
    moved = {**timed, 'videos/minimal/movie.py': (121, 2_000, 9)}
    watch, evaluations, slept = driven([A, sized, sized, timed, moved, moved])
    watch.start()
    assert [watch.step() for _ in range(5)] == [True, False, True, True, False]
    assert evaluations == [0, 1, 3, 4]
    assert slept == [0.25] * 5


def test_a_file_added_or_removed_is_a_change():
    added = {**A, 'videos/minimal/notes.txt': (4, 1_000, 10)}
    watch, evaluations, _ = driven([A, added, A])
    watch.start()
    assert [watch.step(), watch.step()] == [True, True]
    assert evaluations == [0, 1, 2]


def test_the_listing_passes_over_the_tools_products_gits_store_and_bytecode(tmp_path):
    for path in ('pyproject.toml', 'videos/minimal/movie.py', 'videos/minimal/_build/movie.json',
                 '_build/stage/stage.js', '.git/HEAD', 'models/__pycache__/counter.cpython-313.pyc',
                 'models/counter.py'):
        (tmp_path / path).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / path).write_text(path)
    found = listing(tmp_path)
    assert sorted(found) == ['models/counter.py', 'pyproject.toml', 'videos/minimal/movie.py']
    status = os.stat(tmp_path / 'pyproject.toml')
    assert found['pyproject.toml'] == (status.st_size, status.st_mtime_ns, status.st_ino)


def test_an_interval_that_is_not_a_positive_number_of_seconds_is_refused(tmp_path):
    for value in ('0', '-1', 'soon', 'nan'):
        result = subprocess.run([sys.executable, '-m', 'machinome_movie', 'watch', str(tmp_path), 'minimal',
                                 '--interval', value], capture_output=True, text=True, env=environment())
        assert result.returncode == 1, value
        assert result.stderr.startswith('machinome-movie: --interval '), result.stderr


def environment():
    # This checkout's package, not whichever one the environment installed.
    return {'PATH': '/usr/bin:/bin', 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONPATH': str(PYTHON),
            'PYTHONUNBUFFERED': '1'}


def next_line(stream, until):
    while time.monotonic() < until:
        line = stream.readline()
        if line:
            return line.rstrip('\n')
    raise AssertionError('no line before the deadline')


def test_the_command_line_evaluates_again_when_a_module_changes_and_stops_cleanly(tmp_path):
    copy = tmp_path / 'project'
    shutil.copytree(PROJECT, copy, ignore=shutil.ignore_patterns('_build', '__pycache__'))
    written = copy / 'videos' / 'minimal' / '_build' / 'movie.json'
    child = subprocess.Popen([sys.executable, '-m', 'machinome_movie', 'watch', str(copy), 'minimal',
                              '--interval', '0.1'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                             env=environment())
    try:
        until = time.monotonic() + 120
        assert next_line(child.stdout, until) == str(written)
        first = written.read_bytes()
        module = copy / 'videos' / 'minimal' / 'movie.py'
        module.write_text(module.read_text() + '\n')
        assert next_line(child.stdout, until) == str(written)
        assert written.read_bytes() == first, 'the same declarations evaluate to the same bytes'
        child.send_signal(signal.SIGINT)
        assert child.wait(timeout=30) == 0, child.stderr.read()
    finally:
        if child.poll() is None:
            child.kill()
            child.wait()
