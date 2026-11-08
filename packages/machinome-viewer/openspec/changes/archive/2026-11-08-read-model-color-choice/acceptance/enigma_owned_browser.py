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
    parser.add_argument('--oracle')
    parser.add_argument('--document')
    parser.add_argument('--mode', choices=['baseline', 'candidate'], default='candidate')
    parser.add_argument('--allocation', required=True)
    parser.add_argument('--wall-seconds', type=int, required=True)
    parser.add_argument('--rss-gib', type=int, default=8)
    parser.add_argument('--resume-row', type=int)
    parser.add_argument('--bundle', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = Path(args.output).resolve()
    assert output.is_relative_to(HERE), output
    output.mkdir(parents=True, exist_ok=True)
    def available():
        return next(int(line.split()[1]) * 1024 for line in Path('/proc/meminfo').read_text().splitlines()
                    if line.startswith('MemAvailable:'))
    preflight = {'mem_available': available(), 'minimum_start_available': 10 * 1024**3,
                 'allocation': args.allocation, 'heavy_jobs_excluded_by_root_coordination': True}
    (output / 'preflight.json').write_text(json.dumps(preflight, indent=2) + '\n')
    assert preflight['mem_available'] >= preflight['minimum_start_available'], preflight
    # Adopt orphaned descendants so a double fork cannot escape accounting.
    assert ctypes.CDLL(None, use_errno=True).prctl(36, 1, 0, 0, 0) == 0
    owner = psutil.Process()
    seen, samples = {}, []
    started = time.monotonic()
    peak = peak_pss = 0
    next_pss = 0
    reason = None
    argv = [sys.executable, str(HERE / 'enigma_browser_probe.py'),
            '--mode', args.mode, '--bundle', args.bundle, '--output', str(output)]
    if args.oracle:
        argv.extend(['--oracle', args.oracle])
    if args.document:
        argv.extend(['--document', args.document])
    if args.resume_row is not None:
        argv.extend(['--resume-row', str(args.resume_row)])
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
                rows = []
                elapsed = time.monotonic() - started
                sample_pss = elapsed >= next_pss
                pss_total = 0
                for process in live:
                    try:
                        row = identity(process)
                        row['rss'] = process.memory_info().rss
                        rss += row['rss']
                        if sample_pss:
                            try:
                                text = Path(f'/proc/{process.pid}/smaps_rollup').read_text()
                                row['pss'] = next(int(line.split()[1])*1024 for line in text.splitlines() if line.startswith('Pss:'))
                                pss_total += row['pss']
                            except (OSError, StopIteration):
                                row['pss'] = None
                        rows.append(row)
                    except psutil.Error:
                        pass
                peak = max(peak, rss)
                if sample_pss:
                    peak_pss = max(peak_pss, pss_total)
                    next_pss = elapsed + 1
                mem_available = available()
                samples.append({'elapsed': elapsed, 'aggregate_rss': rss,
                                'sampled_aggregate_pss': pss_total if sample_pss else None,
                                'mem_available': mem_available, 'owned': rows})
                if rss > args.rss_gib * 1024**3:
                    reason = f'aggregate RSS exceeded {args.rss_gib} GiB'
                    break
                if mem_available < 2 * 1024**3:
                    reason = 'host MemAvailable fell below 2 GiB pressure guard'
                    break
                if elapsed > args.wall_seconds - 10:
                    reason = f'{args.wall_seconds-10}-second work budget; 10 seconds reserved for cleanup'
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
    result = {'allocation': args.allocation,
              'argv': argv, 'supervisor': identity(owner), 'child': child_identity,
              'returncode': code, 'stop_reason': reason, 'wall_seconds_including_cleanup': time.monotonic() - started,
              'wall_limit': args.wall_seconds, 'aggregate_rss_limit': args.rss_gib * 1024**3,
              'peak_aggregate_rss': peak, 'peak_sampled_aggregate_pss': peak_pss, 'preflight': preflight,
              'owned_identities': list(seen.values()), 'remaining_owned': remaining}
    (output / 'process-samples.json').write_text(json.dumps(samples, indent=2) + '\n')
    (output / 'terminal.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result), flush=True)
    assert not reason and code == 0 and not remaining and result['wall_seconds_including_cleanup'] < args.wall_seconds


if __name__ == '__main__':
    main()
