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

The finder refuses whichever modules a caller lists (`absent`, the engine's
package by default), and can make a listed module *broken* instead
(`broken`): found, then failing to import from inside, as an installed
kernel that cannot load does. The `lean-install` change uses both, for an
install without a kernel extra and for one whose kernel is present and
broken.

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
import atexit, importlib.machinery, os, sys

_ATTEMPTS = [0]
_LOG = os.environ['EXACT_ENGINE_ABSENT_LOG']


def _listed(variable):
    return tuple(name for name in os.environ.get(variable, '').split(',')
                 if name)


def _under(name, roots):
    return next((root for root in roots
                 if name == root or name.startswith(root + '.')), None)


class _ExactEngineAbsent:
    """Refuse every listed module, and everything beneath it, the way an
    install without it does."""

    def __init__(self, names):
        self.names = names

    def find_spec(self, name, target=None, path=None):
        if _under(name, self.names):
            _ATTEMPTS[0] += 1
            raise ModuleNotFoundError(f"No module named {name!r}", name=name)
        return None


class _Broken:
    """Find every listed module, then fail to import it from inside, the
    way an installed kernel that cannot load does."""

    def __init__(self, names):
        self.names = names

    def find_spec(self, name, target=None, path=None):
        if _under(name, self.names):
            return importlib.machinery.ModuleSpec(name, self)
        return None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        raise ImportError(f'broken {_under(module.__name__, self.names)}')


if os.environ.get('EXACT_ENGINE_ABSENT') == '1':
    sys.meta_path.insert(0, _ExactEngineAbsent(
        _listed('EXACT_ENGINE_ABSENT_NAMES')))
if _listed('EXACT_ENGINE_BROKEN_NAMES'):
    sys.meta_path.insert(0, _Broken(_listed('EXACT_ENGINE_BROKEN_NAMES')))


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


#: What the finder refuses unless a caller lists otherwise: the engine.
ENGINE = ('machinome.occt',)


def _run(code, arguments=(), blocked=True, build_dir=None, cwd=REPO_DIR,
         absent=ENGINE, broken=()):
    with tempfile.TemporaryDirectory(prefix='exact-engine-absent-') as site:
        with open(os.path.join(site, 'sitecustomize.py'), 'w') as handle:
            handle.write(SITECUSTOMIZE)
        log = os.path.join(site, 'exit.log')
        env = dict(os.environ,
                   PYTHONPATH=os.pathsep.join([site, REPO_DIR]),
                   EXACT_ENGINE_ABSENT='1' if blocked else '0',
                   EXACT_ENGINE_ABSENT_NAMES=','.join(absent),
                   EXACT_ENGINE_BROKEN_NAMES=','.join(broken),
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


def run_python(snippet, blocked=True, build_dir=None, absent=ENGINE,
               broken=(), cwd=REPO_DIR):
    """Run `snippet` in a subprocess, the `absent` modules (the engine by
    default) refused if `blocked`, and the `broken` ones failing to import
    from inside."""
    return _run(snippet, blocked=blocked, build_dir=build_dir, cwd=cwd,
                absent=absent, broken=broken)


def run_machinome(*arguments, blocked=True, build_dir=None, absent=ENGINE,
                  broken=(), cwd=REPO_DIR):
    """Run a `machinome` command, the `absent` modules (the engine by
    default) refused in every process of it if `blocked`, and the `broken`
    ones failing to import from inside."""
    return _run(CLI, arguments, blocked=blocked, build_dir=build_dir,
                cwd=cwd, absent=absent, broken=broken)
