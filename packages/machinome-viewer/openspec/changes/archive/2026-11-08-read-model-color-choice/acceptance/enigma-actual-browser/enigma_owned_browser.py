"""One owned Enigma browser allocation; descendants are tracked by PID + birth."""
import argparse
import ctypes
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import traceback

import psutil

HERE = Path(__file__).resolve().parent


def identity(process):
    try:
        return {'pid': process.pid, 'birth': process.create_time(),
                'ppid': process.ppid(), 'name': process.name(), 'status': process.status()}
    except psutil.Error:
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--oracle', required=True)
    parser.add_argument('--bundle', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = Path(args.output).resolve()
    assert output.is_relative_to(HERE), output
    output.mkdir(parents=True, exist_ok=True)
    # Adopt orphaned descendants so a double fork cannot escape accounting.
    assert ctypes.CDLL(None, use_errno=True).prctl(36, 1, 0, 0, 0) == 0
    owner = psutil.Process()
    seen, samples = {}, []
    started = time.monotonic()
    peak = 0
    reason = None
    argv = [sys.executable, str(HERE / 'enigma_browser_probe.py'),
            '--oracle', args.oracle, '--bundle', args.bundle, '--output', str(output)]
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'OMP_NUM_THREADS': '1',
           'OPENBLAS_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1'}

    def owned():
        processes = owner.children(recursive=True)
        for process in processes:
            row = identity(process)
            if row:
                seen[(row['pid'], row['birth'])] = row
        live = []
        for (pid, birth) in seen:
            try:
                process = psutil.Process(pid)
                if process.create_time() == birth and process.status() != psutil.STATUS_ZOMBIE:
                    live.append(process)
            except psutil.Error:
                pass
        return live

    with (output / 'stdout.log').open('wb') as stdout, (output / 'stderr.log').open('wb') as stderr:
        child = subprocess.Popen(argv, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
        child_identity = identity(psutil.Process(child.pid))
        try:
            while child.poll() is None:
                live = owned()
                rss = 0
                for process in live:
                    try:
                        rss += process.memory_info().rss
                    except psutil.Error:
                        pass
                peak = max(peak, rss)
                elapsed = time.monotonic() - started
                samples.append({'elapsed': elapsed, 'aggregate_rss': rss,
                                'owned': [identity(p) for p in live]})
                if rss > 4 * 1024**3:
                    reason = 'aggregate RSS exceeded 4 GiB'
                    break
                if elapsed > 290:
                    reason = '290-second work budget; 10 seconds reserved for cleanup'
                    break
                time.sleep(.2)
        except BaseException:
            reason = 'supervisor observer error: ' + traceback.format_exc()
        finally:
            for sig, grace in [(signal.SIGTERM, 2), (signal.SIGKILL, 2)]:
                live = owned()
                if not live:
                    break
                for process in live:
                    try:
                        process.send_signal(sig)
                    except psutil.Error:
                        pass
                until = time.monotonic() + grace
                while time.monotonic() < until and owned():
                    time.sleep(.1)
            code = child.wait(timeout=2)
    remaining = [identity(p) for p in owned()]
    # Reap adopted terminals only after Popen reaped its own child.
    while True:
        try:
            pid, _status = os.waitpid(-1, os.WNOHANG)
            if not pid:
                break
        except ChildProcessError:
            break
    result = {'allocation': 'root-declared-lamp-browser-20261108-01',
              'argv': argv, 'supervisor': identity(owner), 'child': child_identity,
              'returncode': code, 'stop_reason': reason, 'wall_seconds_including_cleanup': time.monotonic() - started,
              'wall_limit': 300, 'aggregate_rss_limit': 4 * 1024**3, 'peak_aggregate_rss': peak,
              'owned_identities': list(seen.values()), 'remaining_owned': remaining}
    (output / 'process-samples.json').write_text(json.dumps(samples, indent=2) + '\n')
    (output / 'terminal.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result), flush=True)
    assert not reason and code == 0 and not remaining and result['wall_seconds_including_cleanup'] < 300


if __name__ == '__main__':
    main()
