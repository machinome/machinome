"""One unchanged staged pair and one ordinary snapshot; no Studio mutations."""
from pathlib import Path
import datetime
import hashlib
import json
import sys
import importlib.metadata
import os
import shutil
import traceback
import signal
import subprocess
import time
import urllib.request

import psutil

OUT = Path(__file__).resolve().parent
WORKTREE = OUT.parents[5]
PROJECT = Path('/mnt/data/machinome-projects/enigma-i')
STAGING = Path('/tmp/capture-still-stage-root').read_text().strip()
STAGING = Path(STAGING)
EXPECTED = 'f6ffa7958cf787d2d5b06f246a11d380ef4b3851f8585756a653650629ddbf6a'
STUDIO_PID = 1575345
SESSION = '50DgDH9Okdk8Mv4RjGJnYksimqAIbm0F'
ENV = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1',
       'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1'}


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(process):
    try:
        return {'pid': process.pid, 'birth': process.create_time(),
                'ppid': process.ppid(), 'argv': process.cmdline(),
                'status': process.status()}
    except psutil.Error:
        return None


def active_jobs():
    result = []
    for p in psutil.process_iter():
        row = identity(p)
        if row and (('snapshot' in row['argv']) or
                    ('viewer' in row['argv'] and 'capture' in row['argv']) or
                    (row['ppid'] == STUDIO_PID and 'build' in row['argv'])):
            result.append(row)
    return result


def preflight(name):
    server = identity(psutil.Process(STUDIO_PID))
    jobs = active_jobs()
    row = {'at': datetime.datetime.now(datetime.UTC).isoformat(),
           'studio_server': server, 'active_jobs': jobs}
    with urllib.request.urlopen(
            f'http://127.0.0.1:9000/api/sessions/{SESSION}/stream', timeout=8) as response:
        for line in response:
            if line.startswith(b'data:'):
                run = json.loads(line[5:])['run']
                row['event_state'] = {k: run.get(k) for k in (
                    'model_building', 'model_build_error', 'latest_event_sequence')}
                break
    save(name + '-preflight.json', row)
    assert not jobs, jobs
    assert not row['event_state']['model_building'], row
    return row


def run(name, argv, cwd, budget, env):
    preflight(name)
    started = time.monotonic()
    seen = {}
    samples = []
    timed_out = False
    first_browser_elapsed = None
    snapshot_stage = None
    previous_stages = set(PROJECT.glob('_build.web-snapshot.*'))
    with (OUT / (name + '-stdout.log')).open('wb') as stdout, \
         (OUT / (name + '-stderr.log')).open('wb') as stderr:
        child = subprocess.Popen(argv, cwd=cwd, env=env, stdout=stdout,
                                 stderr=stderr, start_new_session=True)
        owner = psutil.Process(child.pid)
        owner_identity = identity(owner)
        next_sample = 0
        observer_error = None
        try:
            while child.poll() is None:
                try:
                    processes = [owner, *owner.children(recursive=True)]
                except psutil.Error:
                    processes = []
                for process in processes:
                    row = identity(process)
                    if row:
                        seen[(row['pid'], row['birth'])] = row
                elapsed = time.monotonic() - started
                if first_browser_elapsed is None and any(
                        row and any('chrome-headless-shell' in arg for arg in row['argv'])
                        for row in (identity(p) for p in processes)):
                    first_browser_elapsed = elapsed
                if name == 'ordinary' and snapshot_stage is None:
                    for stage in set(PROJECT.glob('_build.web-snapshot.*')) - previous_stages:
                        path = stage / 'viewer.json'
                        if path.exists():
                            try:
                                staged = json.loads(path.read_text())
                            except json.JSONDecodeError:
                                # The producer writes its private document once.
                                # Observe again after its write finishes.
                                continue
                            models = set()
                            pending = [staged['root']]
                            while pending:
                                node = pending.pop()
                                pending.extend(node.get('children', []))
                                if 'model' in node:
                                    models.add(node['model'])
                            asset_pins = {relative: digest(stage / relative) for relative in sorted(models)}
                            snapshot_stage = {'observed_elapsed': elapsed, 'path': str(stage),
                                              'document_sha256': digest(path), 'version': staged['version'],
                                              'artifacts': asset_pins,
                                              'publication_artifacts_match': all(
                                                  relative in pins and sha == pins[relative]['sha256']
                                                  for relative, sha in asset_pins.items())}
                            save('ordinary-staged-inputs.json', snapshot_stage)
                            break
                if elapsed >= next_sample:
                    samples.append({'elapsed': elapsed, 'owned': [identity(p) for p in processes],
                                    'other_jobs': [r for r in active_jobs()
                                                   if r['pid'] != child.pid]})
                    save(name + '-process-samples.json', samples)
                    next_sample = elapsed + 10
                if elapsed >= budget:
                    timed_out = True
                    break
                time.sleep(.2)
        except BaseException:
            observer_error = traceback.format_exc()
        finally:
            command_elapsed = time.monotonic() - started
            # Clean only exact process identities descended from this command.
            # Studio's server and its agent are never members of this set.
            for sig in (signal.SIGTERM, signal.SIGKILL):
                live = []
                for (pid, birth), row in seen.items():
                    try:
                        process = psutil.Process(pid)
                        if process.create_time() == birth and process.status() != psutil.STATUS_ZOMBIE:
                            live.append(process)
                            process.send_signal(sig)
                    except psutil.Error:
                        pass
                if not live:
                    break
                time.sleep(.3)
            code = child.wait(timeout=3)
    remaining = []
    for pid, birth in seen:
        try:
            process = psutil.Process(pid)
            if process.create_time() == birth and process.status() != psutil.STATUS_ZOMBIE:
                remaining.append(identity(process))
        except psutil.Error:
            pass
    row = {'argv': argv, 'cwd': str(cwd), 'budget': budget,
           'observer_error': observer_error,
           'first_browser_elapsed': first_browser_elapsed,
           'snapshot_stage': snapshot_stage,
           'owner': owner_identity, 'returncode': code, 'timeout': timed_out,
           'command_elapsed': command_elapsed, 'including_cleanup': time.monotonic() - started,
           'owned': list(seen.values()), 'remaining_owned': remaining,
           'studio_server_after': identity(psutil.Process(STUDIO_PID))}
    output = OUT / (name + '.png')
    if output.exists():
        from PIL import Image
        image = Image.open(output).convert('RGBA')
        row['image'] = {'path': output.name, 'bytes': output.stat().st_size,
                        'sha256': digest(output), 'size': image.size,
                        'alpha_extrema': image.getchannel('A').getextrema()}
    save(name + '-terminal.json', row)
    print(name, json.dumps({k: row[k] for k in ('returncode', 'timeout', 'command_elapsed',
                                              'remaining_owned')}), flush=True)
    assert not remaining
    assert identity(psutil.Process(STUDIO_PID))['birth'] == owner_identity_studio['birth']
    return row


if __name__ == '__main__':
    assert WORKTREE.name == 'capture-still-without-frame-loop', WORKTREE
    preflight('freeze')
    source = PROJECT / '_build'
    document = json.loads((source / 'viewer.json').read_text())
    assert digest(source / 'viewer.json') == EXPECTED
    assert document['version'] == 4 and not document.get('instructions') and 'program' not in document
    references = set()
    todo = [document]
    while todo:
        value = todo.pop()
        if isinstance(value, dict):
            for key, item in value.items():
                if key == 'model':
                    references.add(item)
                elif isinstance(item, (dict, list)):
                    todo.append(item)
        elif isinstance(value, list):
            todo.extend(value)
    pins = {name: {'sha256': digest(source / name), 'bytes': (source / name).stat().st_size}
            for name in sorted(references)}
    candidate_package = WORKTREE / 'packages/machinome-viewer/machinome/viewer/web'
    baseline_package = STAGING / 'baseline-package/machinome/viewer/web'
    bundle_relative = 'widget/dist/machinome-viewer.js'
    assert digest(candidate_package / bundle_relative) == digest(baseline_package / bundle_relative)
    save('enigma-inputs.json', {
        'python': sys.version, 'playwright': importlib.metadata.version('playwright'),
        'bundle_sha256': digest(candidate_package / bundle_relative),
        'baseline_capture_sha256': digest(baseline_package / 'capture.py'),
        'candidate_capture_sha256': digest(candidate_package / 'capture.py'),
        'project_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=PROJECT, text=True).strip(),
        'model': 'simulation.candidate_machine:CandidateMachineInspection',
        'model_source_sha256': digest(PROJECT / 'simulation/candidate_machine.py'),
        'document_sha256': EXPECTED, 'document_bytes': (source / 'viewer.json').stat().st_size,
        'artifacts': pins, 'viewport': [1100, 800], 'time': 0,
        'camera': 'automatic fit', 'browser': 'headless Chromium, production SwiftShader arguments',
        'stage_root': str(STAGING)})
    for name in (() if os.environ.get('CAPTURE_PROBE_ONLY_ORDINARY') else ('baseline', 'candidate')):
        stage = STAGING / name
        stage.mkdir(exist_ok=True)
        shutil.copy2(source / 'viewer.json', stage / 'viewer.json')
        for relative in references:
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / relative, target)
            assert digest(target) == pins[relative]['sha256']
    owner_identity_studio = identity(psutil.Process(STUDIO_PID))
    exe = str(WORKTREE / '.venv/bin/machinome')
    results = {name: json.loads((OUT / (name + '-terminal.json')).read_text())
               for name in ('baseline', 'candidate')} if os.environ.get('CAPTURE_PROBE_ONLY_ORDINARY') else {}
    for name in (() if os.environ.get('CAPTURE_PROBE_ONLY_ORDINARY') else ('baseline', 'candidate')):
        env = dict(ENV)
        if name == 'baseline':
            env['PYTHONPATH'] = str(STAGING / 'baseline-package')
        else:
            env.pop('PYTHONPATH', None)
        argv = [exe, 'viewer', 'capture', str(STAGING / name), '-o', str(OUT / (name + '.png')),
                '--imgsize', '1100x800', '--time', '0', '--viewer', 'web']
        results[name] = run(name, argv, WORKTREE, 180, env)
    # The supported snapshot stages privately without replacing viewer.json.
    # Running it as this independent child also exercises ordinary preparation.
    env = dict(ENV)
    env.pop('PYTHONPATH', None)
    argv = [exe, 'snapshot', 'simulation.candidate_machine:CandidateMachineInspection',
            '--viewer', 'web', '-o', str(OUT / 'ordinary.png'), '--imgsize', '1100x800']
    results['ordinary'] = run('ordinary', argv, PROJECT, 240, env)
    assert digest(source / 'viewer.json') == EXPECTED
    assert all(digest(source / name) == pin['sha256'] for name, pin in pins.items())
    save('enigma-comparison.json', {name: {k: r.get(k) for k in (
        'returncode', 'timeout', 'command_elapsed', 'remaining_owned', 'image')}
        for name, r in results.items()})
