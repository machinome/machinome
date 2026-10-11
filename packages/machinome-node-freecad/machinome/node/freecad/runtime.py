# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""Native process and immutable source-snapshot cache (not a sandbox)."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from contextlib import ExitStack

from machinome.source_generation import (SourceChanged, consumed_source,
                                         observation_key)
from .worker import ACCEPTANCE_RECIPE

class NativeAssemblyError(ValueError):
    pass

_cache = {}

def runtime():
    root = os.environ.get('MACHINOME_FREECAD_ROOT')
    if not root:
        raise NativeAssemblyError('Native FreeCAD runtime required: set '
                                  'MACHINOME_FREECAD_ROOT to an extracted '
                                  'FreeCAD 1.1.4 AppImage root (trusted sources only).')
    root = Path(root).resolve()
    launcher = root / 'AppRun'
    if not launcher.is_file():
        raise NativeAssemblyError(f'FreeCAD AppRun not found: {launcher}')
    # These files identify both native binaries and the frame-resolution recipe.
    files = [launcher, root / 'usr/Mod/Assembly/JointObject.py',
             root / 'usr/Mod/Assembly/UtilsAssembly.py']
    files.extend(sorted((root / 'usr/lib').glob('FreeCAD.so')))
    files.extend(sorted((root / 'usr/lib').glob('libFreeCADApp.so*')))
    identity = tuple((str(p), observation_key(p),
                      hashlib.sha256(p.read_bytes()).hexdigest()) for p in files)
    return root, identity

def _observe(path):
    path = Path(path)
    def fresh():
        stat = path.stat()
        return (str(path.resolve()), stat.st_dev, stat.st_ino, stat.st_size,
                stat.st_mtime_ns, stat.st_ctime_ns)
    before = fresh()
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    after = fresh()
    if before != after:
        raise SourceChanged(f'FreeCAD source changed while reading {path}')
    return before, digest

def _invoke(root, source, mode, expected=()):
    worker = Path(__file__).with_name('worker.py')
    env = dict(os.environ, PYTHONPATH=str(root / 'usr/lib'))
    with tempfile.TemporaryDirectory(prefix='machinome-freecad-') as temp:
        result = Path(temp) / 'result.json'
        request = {'source': str(source), 'mode': mode,
                   'acceptance_recipe': ACCEPTANCE_RECIPE,
                   'expected': dict(expected), 'runtime_root': str(root)}
        completed = subprocess.run(
            [str(root / 'AppRun'), 'python', str(worker), str(result),
             json.dumps(request)], env=env, text=True, capture_output=True,
            timeout=180)
        if not result.is_file():
            raise NativeAssemblyError(f'{source}: FreeCAD worker failed '
                                      f'({completed.returncode}): '
                                      f'{completed.stderr[-4000:]} '
                                      f'{completed.stdout[-2000:]}')
        data = json.loads(result.read_text())
        if completed.returncode or 'error' in data:
            raise NativeAssemblyError(f'{source}: {data.get("error", completed.stderr)}')
        return data

def load_snapshot(source):
    spelling = Path(source).absolute()
    source = spelling.resolve(strict=True)
    root, identity = runtime()
    worker_digest = hashlib.sha256(Path(__file__).with_name('worker.py').read_bytes()).hexdigest()
    key = (str(source), identity, worker_digest, ACCEPTANCE_RECIPE)
    root_before = _observe(spelling)
    # Native discovery also observes changed external-link spellings whose
    # old canonical target is still current. No XML link interpretation.
    discovery = _invoke(root, spelling, 'discover')
    if root_before != _observe(spelling):
        raise SourceChanged(f'FreeCAD root changed during discovery: {spelling}')
    previous = _cache.get(key)
    closure = tuple(discovery['files'])
    observations = tuple((p, _observe(p)) for p in closure)
    if root_before != _observe(spelling):
        raise SourceChanged(f'FreeCAD root changed during discovery: {spelling}')
    with ExitStack() as stack:
        stack.enter_context(consumed_source(spelling, 'native root spelling'))
        # Register the complete closure BEFORE the authoritative native load.
        for p in closure:
            stack.enter_context(consumed_source(p, 'native assembly resolution'))
        data = _invoke(root, spelling, 'resolve',
                       [(p, obs[1]) for p, obs in observations])
        if data.get('acceptance_recipe') != ACCEPTANCE_RECIPE:
            raise NativeAssemblyError(f'{source}: unsupported native acceptance recipe '
                                      f'{data.get("acceptance_recipe")!r}')
        if tuple(data['files']) != closure:
            raise SourceChanged('FreeCAD linked closure changed during native resolution')
        if observations != tuple((p, _observe(p)) for p in closure):
            raise SourceChanged(f'FreeCAD source changed during native resolution: {source}')
        if spelling.resolve(strict=True) != source:
            raise SourceChanged(f'FreeCAD source relinked: {spelling}')
        data['runtime_identity'] = identity
        data['_source_observations'] = dict(observations)
        data['_source_observations'][str(spelling)] = root_before
        encoded = json.dumps(data)
    # Only successful closed generations publish immutable cache data.
    # Preserve native FileName spellings, including file-level symlinks.
    # Re-resolve on every fresh construction to discover the current closure;
    # there is no fast path certified from previously observed link targets.
    # Immutable identical payloads are reused only after the full handshake.
    if previous and previous[0] == closure and previous[1] == observations and previous[2] == encoded:
        return json.loads(previous[2])
    _cache[key] = closure, observations, encoded
    return json.loads(encoded)
