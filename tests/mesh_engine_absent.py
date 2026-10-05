# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Run framework code in interpreters where the mesh engine is absent.

The shape of `tests/brep_engine_absent.py`, for the mesh engine of the
`mesh-engine` change: a `sys.meta_path` finder, installed by a
`sitecustomize` module on the subprocess's path, refuses `manifold3d`, the
engine's package `machinome.engine.mesh`, or both, and everything beneath
them, so every import of them raises `ModuleNotFoundError` exactly as it
would where they are not installed. Being a `sitecustomize`, it is in
every interpreter of a run from its first import: `machinome build` runs
the build in a spawned interpreter (`machinome.core.processes`), which
inherits the environment but not the parent's memory. `manifold3d` publishes
no WebAssembly wheel, so a browser runtime has none: this is that
environment, reproduced honestly rather than stubbed.

The finder refuses whichever roots a caller lists (`absent`, both by
default), and can make a listed root *broken* instead (`broken`): found,
then failing to import from inside, as an installed kernel that cannot
load does.

Every interpreter of a run appends one line to a shared log at exit: for
each refused root, the modules that asked for it, once per ask -- the
first frame on the stack outside the import system and the finder -- and
which of `machinome.engine.mesh` and `manifold3d` it imported. The
asker matters because trimesh asks for `manifold3d` at its own import
(`trimesh/boolean.py` begins `try: from manifold3d import ...`) and copes
with its absence: "manifold3d was never asked for" cannot hold in any
process that imports trimesh, and what can is "machinome.engine.mesh was
never asked for, and every ask of manifold3d was trimesh.boolean's".
"""

import json
import os
import subprocess
import sys
import tempfile
from contextlib import contextmanager


BASEDIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(BASEDIR)

SITECUSTOMIZE = '''
import atexit, importlib.machinery, json, os, sys

_LOG = os.environ['MESH_ENGINE_ABSENT_LOG']
_ASKS = {}


def _listed(variable):
    return tuple(name for name in os.environ.get(variable, '').split(',')
                 if name)


def _under(name, roots):
    return next((root for root in roots
                 if name == root or name.startswith(root + '.')), None)


def _asker():
    """The module that asked: the first frame outside the import system
    and this finder."""
    frame = sys._getframe(2)
    while frame is not None:
        module = frame.f_globals.get('__name__', '')
        if not (module == 'importlib' or module.startswith('importlib.')
                or module == 'sitecustomize'
                or frame.f_code.co_filename.startswith('<frozen importlib')):
            return module
        frame = frame.f_back
    return None


class _MeshEngineAbsent:
    """Log every ask of a listed root, and everything beneath it, and find
    nothing: the finders behind it are hidden from those names (`_Hiding`),
    so the import system answers exactly as where they are not installed --
    `importlib.util.find_spec` returns None, which trimesh's own probe at
    its import relies on, and an import raises `ModuleNotFoundError`."""

    def __init__(self, names):
        self.names = names

    def find_spec(self, name, target=None, path=None):
        root = _under(name, self.names)
        if root:
            _ASKS.setdefault(root, []).append(_asker())
        return None


class _Hiding:
    """One finder of the import system, blind to the listed roots and
    everything beneath them; everything else it answers as itself,
    distributions' metadata included."""

    def __init__(self, finder, names):
        self._finder = finder
        self._names = names

    def find_spec(self, name, path=None, target=None):
        if _under(name, self._names):
            return None
        find = getattr(self._finder, 'find_spec', None)
        return None if find is None else find(name, path, target)

    def __getattr__(self, attribute):
        return getattr(self._finder, attribute)


class _Broken:
    """Find every listed root, then fail to import it from inside, the way
    an installed kernel that cannot load does."""

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


if os.environ.get('MESH_ENGINE_ABSENT') == '1':
    _absent = _listed('MESH_ENGINE_ABSENT_NAMES')
    sys.meta_path[:] = [_MeshEngineAbsent(_absent)] + [
        _Hiding(finder, _absent) for finder in sys.meta_path]
if _listed('MESH_ENGINE_BROKEN_NAMES'):
    sys.meta_path.insert(0, _Broken(_listed('MESH_ENGINE_BROKEN_NAMES')))


def _report():
    imported = sorted(name for name in ('machinome.engine.mesh',
                                        'manifold3d')
                      if sys.modules.get(name) is not None)
    with open(_LOG, 'a') as log:
        log.write(json.dumps({'pid': os.getpid(), 'asks': _ASKS,
                              'imported': imported}) + '\\n')


atexit.register(_report)
'''

CLI = 'from machinome.cli import manage; manage()'

#: The modules of trimesh that ask for manifold3d when trimesh is imported.
TRIMESH_PROBES = frozenset({'trimesh.boolean', 'trimesh.util'})

#: What the finder refuses unless a caller lists otherwise: the kernel and
#: the engine's package.
ABSENT = ('manifold3d', 'machinome.engine.mesh')


class Report:
    """One interpreter's exit report."""

    def __init__(self, line):
        data = json.loads(line)
        self.pid = data['pid']
        self.asks = data['asks']
        self.imported = set(data['imported'])

    def askers(self, root):
        """Every module that asked for `root`, once per ask."""
        return list(self.asks.get(root, ()))


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

    def asks(self, root):
        """How many times the run's processes asked for `root`."""
        return sum(len(report.askers(root)) for report in self.reports)

    def askers(self, root):
        """Every module any process of the run asked for `root` from."""
        return {asker for report in self.reports
                for asker in report.askers(root)}

    @property
    def imported(self):
        """Which of the engine and its kernel any process imported."""
        return set().union(*(report.imported for report in self.reports))


class Finder:
    """The finder's environment for a run made elsewhere, and its reports.

    `environment` is what a caller merges into a child's environment; its
    `PYTHONPATH` puts the `sitecustomize` before the repository.
    """

    def __init__(self, site, blocked, absent, broken):
        self.log = os.path.join(site, 'exit.log')
        self.environment = {
            'PYTHONPATH': os.pathsep.join([site, REPO_DIR]),
            'MESH_ENGINE_ABSENT': '1' if blocked else '0',
            'MESH_ENGINE_ABSENT_NAMES': ','.join(absent),
            'MESH_ENGINE_BROKEN_NAMES': ','.join(broken),
            'MESH_ENGINE_ABSENT_LOG': self.log,
        }

    def reports(self):
        """Every exit report written so far, and none consumed."""
        if not os.path.exists(self.log):
            return []
        with open(self.log) as handle:
            return [Report(line) for line in handle if line.strip()]

    def run(self, completed):
        """`completed` with every exit report written since the last
        call, which are consumed."""
        reports = self.reports()
        if os.path.exists(self.log):
            os.remove(self.log)
        if not reports:
            raise AssertionError(f'no exit report:\n{completed.stdout}\n'
                                 f'{completed.stderr}')
        return Run(completed, reports)


@contextmanager
def finder(blocked=True, absent=ABSENT, broken=()):
    """The finder, installed for every child given `environment`."""
    with tempfile.TemporaryDirectory(prefix='mesh-engine-absent-') as site:
        with open(os.path.join(site, 'sitecustomize.py'), 'w') as handle:
            handle.write(SITECUSTOMIZE)
        yield Finder(site, blocked, absent, broken)


def _run(code, arguments=(), blocked=True, build_dir=None, cwd=REPO_DIR,
         absent=ABSENT, broken=(), env=None):
    with finder(blocked, absent, broken) as installed:
        environment = dict(os.environ, **installed.environment)
        if build_dir is not None:
            environment['SOLID_BUILD_DIR'] = build_dir
        environment.update(env or {})
        completed = subprocess.run(
            [sys.executable, '-c', code, *arguments],
            cwd=cwd, env=environment, capture_output=True, text=True,
            timeout=600,
        )
        return installed.run(completed)


def run_python(snippet, blocked=True, build_dir=None, absent=ABSENT,
               broken=(), cwd=REPO_DIR, env=None):
    """Run `snippet` in a subprocess, the `absent` roots (`manifold3d` and
    `machinome.engine.mesh` by default) refused if `blocked`, and the `broken`
    ones failing to import from inside."""
    return _run(snippet, blocked=blocked, build_dir=build_dir, cwd=cwd,
                absent=absent, broken=broken, env=env)


def run_machinome(*arguments, blocked=True, build_dir=None, absent=ABSENT,
                  broken=(), cwd=REPO_DIR, env=None):
    """Run a `machinome` command, the `absent` roots refused in every
    process of it if `blocked`, and the `broken` ones failing to import
    from inside."""
    return _run(CLI, arguments, blocked=blocked, build_dir=build_dir,
                cwd=cwd, absent=absent, broken=broken, env=env)


def mesh_engine_is_installed():
    """True when this interpreter really has the mesh engine's kernel, so a
    test can state plainly that it is comparing against a genuine
    baseline."""
    try:
        import manifold3d  # noqa: F401
    except ImportError:
        return False
    return True
