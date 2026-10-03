# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Run framework code in interpreters where the exact engine is absent.

The shape of `tests/mesh_engine_absent.py`, for the exact engine of the
`exact-engine` change: a `sys.meta_path` finder refuses `machinome.occt`
and everything beneath it, so every import of the engine raises
`ModuleNotFoundError` exactly as it would where the engine is not
installed.

Unlike the mesh engine's helper, the finder is installed by a
`sitecustomize` module on the subprocess's path rather than by a prelude to
`-c`: `machinome build` runs the build in a spawned interpreter
(`machinome.core.processes`), which inherits the environment but not the
parent's memory, and the engine must be absent there too.

Every interpreter of a run also appends one line to a shared log at exit:
which of the exact stack's modules it imported -- the engine, `OCP`,
`cadquery`, `build123d` -- and how many times it asked for the engine. A
test can then tell "the engine was never asked for" from "it was asked for
and the refusal was swallowed", across every process of the run.
"""

import os
import subprocess
import sys
import tempfile


BASEDIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(BASEDIR)

SITECUSTOMIZE = '''
import atexit, os, sys

_ATTEMPTS = [0]
_LOG = os.environ['EXACT_ENGINE_ABSENT_LOG']


class _ExactEngineAbsent:
    """Refuse machinome.occt the way an install without it does."""

    def find_spec(self, name, target=None, path=None):
        if name == 'machinome.occt' or name.startswith('machinome.occt.'):
            _ATTEMPTS[0] += 1
            raise ModuleNotFoundError(f"No module named {name!r}", name=name)
        return None


if os.environ.get('EXACT_ENGINE_ABSENT') == '1':
    sys.meta_path.insert(0, _ExactEngineAbsent())


def _report():
    loaded = sorted(name for name in ('machinome.occt.engine', 'OCP',
                                      'cadquery', 'build123d')
                    if name in sys.modules)
    with open(_LOG, 'a') as log:
        log.write(f"{os.getpid()} {_ATTEMPTS[0]} {','.join(loaded) or '-'}\\n")


atexit.register(_report)
'''

CLI = 'from machinome.cli import manage; manage()'


class Run:
    """One finished subprocess run, with its processes' exit reports."""

    def __init__(self, completed, reports):
        self.returncode = completed.returncode
        self.stdout = completed.stdout
        self.stderr = completed.stderr
        self.reports = reports

    @property
    def output(self):
        return self.stdout + self.stderr

    @property
    def exact_stack(self):
        """Every exact-stack module any process of the run imported."""
        return set().union(*(stack for _, stack in self.reports))

    @property
    def engine_attempts(self):
        """How many times the run's processes asked for the engine."""
        return sum(attempts for attempts, _ in self.reports)


def _run(code, arguments=(), blocked=True, build_dir=None, cwd=REPO_DIR):
    with tempfile.TemporaryDirectory(prefix='exact-engine-absent-') as site:
        with open(os.path.join(site, 'sitecustomize.py'), 'w') as handle:
            handle.write(SITECUSTOMIZE)
        log = os.path.join(site, 'exit.log')
        env = dict(os.environ,
                   PYTHONPATH=os.pathsep.join([site, REPO_DIR]),
                   EXACT_ENGINE_ABSENT='1' if blocked else '0',
                   EXACT_ENGINE_ABSENT_LOG=log)
        if build_dir is not None:
            env['SOLID_BUILD_DIR'] = build_dir
        completed = subprocess.run(
            [sys.executable, '-c', code, *arguments],
            cwd=cwd, env=env, capture_output=True, text=True, timeout=600,
        )
        reports = []
        if os.path.exists(log):
            with open(log) as handle:
                for line in handle:
                    _, attempts, stack = line.split()
                    reports.append((int(attempts), set()
                                    if stack == '-' else set(stack.split(','))))
    if not reports:
        raise AssertionError(f'no exit report:\n{completed.stdout}\n'
                             f'{completed.stderr}')
    return Run(completed, reports)


def run_python(snippet, blocked=True, build_dir=None):
    """Run `snippet` in a subprocess, the engine absent if `blocked`."""
    return _run(snippet, blocked=blocked, build_dir=build_dir)


def run_machinome(*arguments, blocked=True, build_dir=None):
    """Run a `machinome` command, the engine absent from every process of
    it if `blocked`."""
    return _run(CLI, arguments, blocked=blocked, build_dir=build_dir)
