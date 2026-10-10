# Evidence: persistent-verdict-memo

Measured on the bench `machinome/WTs/persistent-verdict-memo` (planning
commit 6e6c0b2 on framework `main` bf24687, implementation uncommitted),
2026-09-29, with the workspace venv and the bench first on `PYTHONPATH`:

    PYTHONPATH=<bench> .venv/bin/python -c "import machinome; print(machinome.__file__)"
    -> .../WTs/persistent-verdict-memo/machinome/__init__.py 0.7.1

One CAD process at a time throughout. Every run below is one fresh process
through the counting probe at the end of this file, which wraps `_memoized`
(keyed asks, in-process hits, computations, uncacheable asks),
`intersect_shapes` (OCCT booleans) and `_faceted_verdict`, and reads the
store's private counters (store hits). "Computations" are keyed asks that
neither tier answered. Wall time is the probe's time around
`machinome.cli.manage()`; the outer process time is in the raw lines. Store
size is the sum of the files in `.verdicts` after the run. No project
repository was committed to; the `.verdicts` directories the runs left are
ignored build state and stay.

## Baselines (task 1)

Cited from `workflow/warts.md`, "3DPrintedClocks wall clock 02 and
strandbeest (2026-09-29, verdict memo across runs)", at bf24687, each suite
run twice in ONE interpreter (cold memo, then warm):

| Suite | Cold | Warm floor (every ask served in process) | Verdicts |
|---|---:|---:|---|
| 3DPrintedClocks `wall_clock_02` | 1348.9 s (4238 asks, 1138 misses, 643 booleans) | 18.35 s | 16 passed, 6 failed |
| strandbeest walking demo | 246.9 s (6635 asks, 1510 misses, 1055 booleans) | 11.97 s | 3 passed |

v8-engine slice (task 1.2), on the unmodified tree, from
`projects/Vibecoded-demos/v8-engine` at `declarative-api` fdf624b,
`machinome test v8_engine/valvetrain/test_valve_motion.py`:

    faceted (checkout .env): PROBE {"keyed_asks": 0, "inprocess_hits": 0, "computations": 0, "uncacheable": 2, "occt_booleans": 0, "faceted_verdicts": 2, "compute_s": 0.0, "store_hits": null, "wall_s": 2.22, "exit": null, "memo_entries": 0}
      Ran 8 tests in 0.61 seconds: 8 passed, 0 failed (faceted kernel, volume epsilon 0 mm³)
    --exact:                 PROBE {"keyed_asks": 0, "inprocess_hits": 0, "computations": 0, "uncacheable": 2, "occt_booleans": 1, "faceted_verdicts": 0, "compute_s": 0.59, "store_hits": null, "wall_s": 2.62, "exit": null, "memo_entries": 0}
      Ran 8 tests in 1.06 seconds: 8 passed, 0 failed

Both kernels asked 2 spring pairs and could key neither (uncacheable 2).

Import baseline (task 1.4): a fresh-interpreter `machinome build -h`
dispatch loads `importlib.metadata` and `platform`, and none of
`cadquery`, `OCP`, `manifold3d`, `trimesh`, `molejo`.

## 3DPrintedClocks `wall_clock_02` (task 9.1)

From `projects/3DPrintedClocks` (branch `solid-node-simulation` b089545),
exact kernel, `_build/.verdicts` deleted first.

| Process | Wall | Keyed asks | In-process hits | Store hits | Computations | OCCT booleans | Uncacheable | Store on disk | Verdicts |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| cold | 1255.93 s | 4238 | 3100 | 0 | 1138 | 643 | 0 | 75 segments, 62062 B | 16 passed, 6 failed |
| warm | 27.81 s | 4238 | 3100 | 1138 | 0 | 0 | 0 | 3 segments, 111776 B | 16 passed, 6 failed |

The cold process flushed every 10 s (75 segments); the warm process's load
found more than 64 and compacted them into one, then wrote its 1138 touches.
The failing tests and their messages, identical in both processes and to the
baseline's six:

```
Running WallClock02Test.test_assembly_integrity........FAIL!
AssertionError: collet should not interfere with hinge_screw (intersection volume 14.578953408065129)
Running WallClock02Test.test_movement_runs_free_through_a_swing................................................FAIL!
AssertionError: collet should not interfere with hinge_screw (intersection volume 14.578953408065129)
Running WallClock02Test.test_solid_integrity.FAIL!
AssertionError: standoffs should be one connected body, but its exact geometry contains 2 connected bodies
Running WallClock02Test.test_source_body_inventory.FAIL!
AssertionError: ['root.standoffs: standoffs should be one connected body, but its exact geometry contains 2 connected bodies', 'root.movement.pendulum.holder.collet / root.movement.pendulum.holder.hinge_screw: collet should not intersect hinge_screw (intersection volume 14.578953408065129)', 'root.movement.pendulum.holder.body / root.movement.pendulum.holder.beat_crinkle_washer: body should not intersect beat_crinkle_washer (intersection volume 1.5784731219292187)', 'root.movement.pendulum.bob.shell / root.movement.pendulum.bob.lid_screw_left: shell should not intersect lid_screw_left (intersection volume 1.7266719837120634)', 'root.movement.pendulum.bob.shell / root.movement.pendulum.bob.lid_screw_right: shell should not intersect lid_screw_right (intersection volume 1.7266719837120572)'] is not false : 
Running WallClock02Test.test_the_train_meshes_all_the_way_round................................FAIL!
AssertionError: collet should not interfere with hinge_screw (intersection volume 14.578953408065129)
Running WallClock02Test.test_the_weight_screw_engages_its_separate_nut.FAIL!
AssertionError: screw should intersect nut
```

The two processes' stdout is identical apart from the timing figure.

**Against the warm floor:** the warm process took 27.81 s where the
in-interpreter warm pass took 18.35 s, 9.46 s above the floor. A third warm
process timed the store's own work directly: the stamp 0.020 s, loading the
store 0.022 s, persisted-key derivation 0.058 s (artifact digests 0.044 s of
it), lookups 0.004 s, flushes 0.002 s, and every `_memoized` call together
0.095 s. The remaining gap is therefore not the store but per-process work
outside the memo, which a second pass in one interpreter did not repeat
(such as imports, the build's currency check, BREP and mesh loads and the
other per-process geometry caches); it was not broken down further, and no
key was widened to chase it.

    ATTRIBUTION {"manage_wall_s": 27.29, "import_machinome_test_s": 0.77, "exit": 1, "timers": {"stamp": 0.02, "store load+compaction": 0.022, "artifact digests": 0.044, "persisted keys (digests included)": 0.058, "store lookups": 0.004, "all _memoized": 0.095, "store flushes": 0.002}, "counters": {"served": 1138, "queued": 0, "touches": 1138, "flushed": 1138, "segments": 2, "loaded": 1138, "compactions": 0}}

## strandbeest walking demo (task 9.2)

From `projects/strandbeest` (`main` 4ccaa59), exact kernel. Its `.env`
sets `SOLID_BUILD_DIR=_build_delivery`, so the store is
`_build_delivery/.verdicts`, deleted first.

| Process | Wall | Keyed asks | In-process hits | Store hits | Computations | OCCT booleans | Uncacheable | Store on disk | Verdicts |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| cold | 163.51 s | 6635 | 5125 | 0 | 1510 | 1055 | 0 | 16 segments, 75334 B | 3 passed |
| warm | 10.63 s | 6635 | 5125 | 1510 | 0 | 0 | 0 | 17 segments, 149408 B | 3 passed |
| `--no-verdict-store` | 166.36 s | 6635 | 5125 | 0 | 1510 | 1055 | 0 | 17 segments, 149408 B (unchanged) | 3 passed |

The third run is cold-like, leaves the store untouched, and its summary
reads `Ran 3 tests in 164.22 seconds: 3 passed, 0 failed (verdict store
off)`; its stdout differs from the cold run's only by that note and the
timing, and the warm run's differs from the cold run's only by the timing.

**Against the warm floor:** the warm process took 10.63 s against the
11.97 s floor; today's cold process was also faster than the baseline's
(163.51 s against 246.9 s, with the identical 1510 computations and 1055
booleans), so the machine was quicker today and the warm process is at the
floor within that variance, not below it by anything this change did.

## v8-engine flexible slice (task 9.3)

From `projects/Vibecoded-demos/v8-engine` at `declarative-api` fdf624b,
`machinome test v8_engine/valvetrain/test_valve_motion.py`, `_build/.verdicts`
deleted before each kernel's pair of runs.

Faceted (the checkout's `.env`, `SOLID_TEST_KERNEL=faceted`):

| Process | Wall | Keyed asks | In-process hits | Store hits | Computations | Faceted verdicts | Uncacheable | Store on disk | Verdicts |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| base (1.2) | 2.22 s | 0 | 0 | -- | 0 | 2 | **2** | -- | 8 passed |
| cold | 2.17 s | 2 | 0 | 0 | 2 | 2 | 0 | 1 segment, 182 B | 8 passed |
| warm | 2.13 s | 2 | 0 | 2 | 0 | 0 | 0 | 2 segments, 364 B | 8 passed |

`--exact`:

| Process | Wall | Keyed asks | In-process hits | Store hits | Computations | OCCT booleans | Uncacheable | Store on disk | Verdicts |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| base (1.2) | 2.62 s | 0 | 0 | -- | 0 | 1 | **2** | -- | 8 passed |
| cold | 2.91 s | 2 | 0 | 0 | 2 | 1 | 0 | 1 segment, 182 B | 8 passed |
| warm | 2.26 s | 2 | 0 | 2 | 0 | 0 | 0 | 2 segments, 364 B | 8 passed |

Uncacheable asks fell from 2 to 0 on both kernels: both spring pairs are now
keyed on the spring's state. Each cold run kept a verdict for each spring
pair; each warm run computed nothing, both its asks being store hits. Every
run's summary and per-test lines equal 1.2's for the same kernel, and each
warm run's stdout equals its cold run's apart from the timing figure. This
slice proves the keying; it does not re-measure ADR-070's whole-suite 1499 s.

## Verdicts

Every warm, cold and store-off process reached exactly the verdicts of its
baseline: 16 passed and 6 failed with identical messages and volumes for
the clock, 3 passed for strandbeest, 8 passed on each kernel for the
v8-engine slice.

## Raw result lines

```
bench 6e6c0b2 + uncommitted implementation; 2026-09-29T11:04:37+00:00
v8-faceted-cold exit 0 outer_wall 3.45 s: test v8_engine/valvetrain/test_valve_motion.py
PROBE {"keyed_asks": 2, "inprocess_hits": 0, "computations": 2, "uncacheable": 0, "occt_booleans": 0, "faceted_verdicts": 2, "compute_s": 0.0, "store_hits": 0, "store_counters": {"served": 0, "queued": 2, "touches": 0, "flushed": 2, "segments": 1, "loaded": 0, "compactions": 0}, "wall_s": 2.17, "exit": null, "memo_entries": 2}
Ran 8 tests in 0.56 seconds: 8 passed, 0 failed (faceted kernel, volume epsilon 0 mm³)
v8-faceted-cold store: 1 segments, 182 bytes
v8-faceted-warm exit 0 outer_wall 3.44 s: test v8_engine/valvetrain/test_valve_motion.py
PROBE {"keyed_asks": 2, "inprocess_hits": 0, "computations": 0, "uncacheable": 0, "occt_booleans": 0, "faceted_verdicts": 0, "compute_s": 0.0, "store_hits": 2, "store_counters": {"served": 2, "queued": 0, "touches": 2, "flushed": 2, "segments": 1, "loaded": 2, "compactions": 0}, "wall_s": 2.13, "exit": null, "memo_entries": 2}
Ran 8 tests in 0.56 seconds: 8 passed, 0 failed (faceted kernel, volume epsilon 0 mm³)
v8-faceted-warm store: 2 segments, 364 bytes
v8-exact-cold exit 0 outer_wall 4.19 s: test v8_engine/valvetrain/test_valve_motion.py --exact
PROBE {"keyed_asks": 2, "inprocess_hits": 0, "computations": 2, "uncacheable": 0, "occt_booleans": 1, "faceted_verdicts": 0, "compute_s": 0.61, "store_hits": 0, "store_counters": {"served": 0, "queued": 2, "touches": 0, "flushed": 2, "segments": 1, "loaded": 0, "compactions": 0}, "wall_s": 2.91, "exit": null, "memo_entries": 2}
Ran 8 tests in 1.29 seconds: 8 passed, 0 failed
v8-exact-cold store: 1 segments, 182 bytes
v8-exact-warm exit 0 outer_wall 3.54 s: test v8_engine/valvetrain/test_valve_motion.py --exact
PROBE {"keyed_asks": 2, "inprocess_hits": 0, "computations": 0, "uncacheable": 0, "occt_booleans": 0, "faceted_verdicts": 0, "compute_s": 0.0, "store_hits": 2, "store_counters": {"served": 2, "queued": 0, "touches": 2, "flushed": 2, "segments": 1, "loaded": 2, "compactions": 0}, "wall_s": 2.26, "exit": null, "memo_entries": 2}
Ran 8 tests in 0.66 seconds: 8 passed, 0 failed
v8-exact-warm store: 2 segments, 364 bytes
sb-cold exit 0 outer_wall 165.01 s: test
PROBE {"keyed_asks": 6635, "inprocess_hits": 5125, "computations": 1510, "uncacheable": 0, "occt_booleans": 1055, "faceted_verdicts": 0, "compute_s": 152.48, "store_hits": 0, "store_counters": {"served": 0, "queued": 1510, "touches": 0, "flushed": 1510, "segments": 16, "loaded": 0, "compactions": 0}, "wall_s": 163.51, "exit": null, "memo_entries": 1510}
Ran 3 tests in 161.33 seconds: 3 passed, 0 failed
sb-cold store: 16 segments, 75334 bytes
sb-warm exit 0 outer_wall 12.08 s: test
PROBE {"keyed_asks": 6635, "inprocess_hits": 5125, "computations": 0, "uncacheable": 0, "occt_booleans": 0, "faceted_verdicts": 0, "compute_s": 0.0, "store_hits": 1510, "store_counters": {"served": 1510, "queued": 0, "touches": 1510, "flushed": 1510, "segments": 1, "loaded": 1510, "compactions": 0}, "wall_s": 10.63, "exit": null, "memo_entries": 1510}
Ran 3 tests in 8.40 seconds: 3 passed, 0 failed
sb-warm store: 17 segments, 149408 bytes
sb-off exit 0 outer_wall 168.06 s: test --no-verdict-store
PROBE {"keyed_asks": 6635, "inprocess_hits": 5125, "computations": 1510, "uncacheable": 0, "occt_booleans": 1055, "faceted_verdicts": 0, "compute_s": 155.1, "store_hits": 0, "store_counters": {"served": 0, "queued": 0, "touches": 0, "flushed": 0, "segments": 0, "loaded": 0, "compactions": 0}, "wall_s": 166.36, "exit": null, "memo_entries": 1510}
Ran 3 tests in 164.22 seconds: 3 passed, 0 failed (verdict store off)
sb-off store: 17 segments, 149408 bytes
clock-cold exit 1 outer_wall 1257.79 s: test wall_clock_02
PROBE {"keyed_asks": 4238, "inprocess_hits": 3100, "computations": 1138, "uncacheable": 0, "occt_booleans": 643, "faceted_verdicts": 0, "compute_s": 1223.68, "store_hits": 0, "store_counters": {"served": 0, "queued": 1138, "touches": 0, "flushed": 1138, "segments": 75, "loaded": 0, "compactions": 0}, "wall_s": 1255.93, "exit": 1, "memo_entries": 1138}
Ran 22 tests in 1253.38 seconds: 16 passed, 6 failed
clock-cold store: 75 segments, 62062 bytes
clock-warm exit 1 outer_wall 29.34 s: test wall_clock_02
PROBE {"keyed_asks": 4238, "inprocess_hits": 3100, "computations": 0, "uncacheable": 0, "occt_booleans": 0, "faceted_verdicts": 0, "compute_s": 0.0, "store_hits": 1138, "store_counters": {"served": 1138, "queued": 0, "touches": 1138, "flushed": 1138, "segments": 2, "loaded": 1138, "compactions": 1}, "wall_s": 27.81, "exit": 1, "memo_entries": 1138}
Ran 22 tests in 25.92 seconds: 16 passed, 6 failed
clock-warm store: 3 segments, 111776 bytes
done 2026-09-29T11:32:04+00:00
```

## The probe as used

```python
"""Run one `machinome test ...` in this process and report, on stderr, one
JSON line of counts: keyed asks, in-process hits, store hits, computations,
OCCT booleans, faceted verdicts, uncacheable asks, and wall time.

Usage: python verdict_probe.py test <reference> [options]

Extends the originating measurement's memo_probe.py (design.md §12). It
never imports machinome.exact itself, so a faceted run's imports are the
run's own: the OCCT boolean is counted by patching test.py's module global
`intersect_shapes`, whose deferred wrapper then resolves on first call.
"""
import json
import sys
import time

sys.argv = ['machinome'] + sys.argv[1:]

import machinome.test as T
from machinome.cli import manage

stats = dict(keyed_asks=0, inprocess_hits=0, computations=0,
             uncacheable=0, occt_booleans=0, faceted_verdicts=0,
             compute_s=0.0)

_orig_memoized = T._memoized


def _memoized(key, compute):
    if key is None:
        stats['uncacheable'] += 1
        start = time.perf_counter()
        try:
            return compute()
        finally:
            stats['compute_s'] += time.perf_counter() - start
    stats['keyed_asks'] += 1
    if key in T._verdict_cache:
        stats['inprocess_hits'] += 1

    def counted():
        stats['computations'] += 1
        start = time.perf_counter()
        try:
            return compute()
        finally:
            stats['compute_s'] += time.perf_counter() - start

    return _orig_memoized(key, counted)


T._memoized = _memoized

_orig_intersect = T.intersect_shapes


def intersect_shapes(*args, **kwargs):
    stats['occt_booleans'] += 1
    return _orig_intersect(*args, **kwargs)


T.intersect_shapes = intersect_shapes

_orig_faceted = T._faceted_verdict


def _faceted_verdict(*args, **kwargs):
    stats['faceted_verdicts'] += 1
    return _orig_faceted(*args, **kwargs)


T._faceted_verdict = _faceted_verdict

start = time.perf_counter()
code = None
try:
    manage()
except SystemExit as stop:
    code = stop.code
wall = time.perf_counter() - start
store = sys.modules.get('machinome._verdict_store')
if store is not None:
    counters = dict(getattr(store, 'counters', {}))
    stats['store_hits'] = counters.get('served', 0)
    stats['store_counters'] = counters
else:
    stats['store_hits'] = None
stats.update(wall_s=round(wall, 2), exit=code,
             memo_entries=len(T._verdict_cache),
             compute_s=round(stats['compute_s'], 2))
sys.stderr.write('PROBE ' + json.dumps(stats) + '\n')
sys.exit(code)
```

The warm attribution run used the same technique with direct timers on
`_compute_stamp`, `Store._load`, `_persisted_key`, `artifact_digest`,
`Store.lookup`, `Store.flush` and `_memoized`.
