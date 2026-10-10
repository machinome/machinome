# Evidence — `snapshot-the-follow-prefix`

Cycle 8 of the fix-warts-3 campaign (`workflow/ongoing/fix-warts-3.md`).
Bench `machinome/WTs/fix-warts-3`, branch `fix-warts-3`, planning commit
7b56c54 (`git -C <bench> rev-parse HEAD` printed
`7b56c54ead2058cfb78d6504ce6603ad5f14a77f`). Every framework command below
ran as
`env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1 /home/asa/devel/machinome/.venv/bin/<tool> ...`,
one process at a time, never in parallel. The interpreter check,
`python -c 'import machinome; print(machinome.__file__)'`, printed
`/home/asa/devel/machinome/machinome/WTs/fix-warts-3/machinome/__init__.py`.

`<project>` is `/home/asa/devel/machinome/projects/Calculators/Curta-Type-I-3x`,
branch `main`, head `1f3dc22` (`git -C <project> rev-parse --short HEAD`).
It was read and run, never written. Every Curta command ran as
`env -C <scratch> PYTHONPATH=<bench>:<project> PYTHONDONTWRITEBYTECODE=1 SOLID_BUILD_DIR=<scratch>/build taskset -c 14 /home/asa/devel/machinome/.venv/bin/<tool> ...`,
with `-p no:cacheprovider` for pytest, so nothing was written in the
project.

`<scratch>` is the campaign scratchpad's `cycle8/` directory
(`/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle8/`).
It is not durable; the scripts this record depends on are copied below.

## 1. Baseline on the unmodified tree (7b56c54)

### 1.1 The scripts

`<scratch>/repro.py`, run from the bench root:

```python
"""Reproduce: a Follow prefix cache hit hands back a mapping proxy, a miss
a Propagation carrying its path attributes."""

import machinome
from unittest.mock import patch

from machinome.simulation import Sim
from machinome.simulation.run import Run
from machinome.simulation.trajectory import Propagation

from tests.test_running_follow import TwoSurfaces

print('machinome from', machinome.__file__)

sim = Sim(TwoSurfaces(), dt=1.0)
run = sim._run
low = run.program.constraints[('ball.slide', 'low')]
values = run.program.values_of(run.bank)
admissions = {'low': 2.0, 'high': -2.0}
print('edges', [edge.kind for edge in low.edges])

made = []
original = Run._deltas


def captured(self, admissions):
    deltas = original(self, admissions)
    made.append(deltas)
    return deltas


cache = {}
with patch.object(Run, '_deltas', captured):
    miss = run._constraint_level(low, run.bank, values, admissions, 0.5,
                                 run.bank['ball.slide'], cache)
    hit = run._constraint_level(low, run.bank, values, admissions, 0.5,
                                run.bank['ball.slide'], cache)
print('walks', len(made), 'cache entries', len(cache))
print('levels miss/hit', float(miss).hex(), float(hit).hex())
walked = made[0]
(saved_deltas, saved_landings), = cache.values()
print('miss deltas type:', type(walked).__name__,
      'follow_cuts', walked.follow_cuts,
      'follow_closures keys', list(walked.follow_closures),
      'untraced', walked.untraced, 'motions', list(walked.motions))
print('hit deltas type:', type(saved_deltas).__name__,
      'isinstance Propagation:', isinstance(saved_deltas, Propagation))
for name in ('motions', 'untraced', 'follow_cuts', 'follow_closures',
             'demanded', 'terminal_keys'):
    try:
        getattr(saved_deltas, name)
        print(name, 'present on hit')
    except AttributeError as error:
        print(name, 'AttributeError:', error)
```

`<scratch>/curta_measure.py`, run with the project on `sys.path` (only its
`bench` variant ran in this stage; the others are Stage P's measurements in
design.md):

```python
"""Measure the Follow prefix cache on the Curta: the bench as it is, an
exact copy of its `_constraint_level` (proxy snapshot, counted), the
candidate frozen-propagation snapshot, and no prefix cache at all.

Usage: curta_measure.py VARIANT [REPEATS]
VARIANT in bench, proxy, frozen, nocache.
Prints timings, counts and a SHA-256 of every committed bank (bit exact).
"""

import hashlib
import math
import os
import struct
import sys
import time
from types import MappingProxyType

import machinome
from machinome.simulation import Sim
from machinome.simulation.run import Run
from machinome.simulation.trajectory import Propagation

from simulation.mechanistic import MechanisticCurta, register_reading

variant = sys.argv[1]
repeats = int(sys.argv[2]) if len(sys.argv) > 2 else 1
counts = {'walks': 0, 'stores': 0, 'hits': 0, 'snapshot_s': 0.0}


class FrozenPropagation(Propagation):
    """Candidate: a completed propagation, read-only."""

    def __init__(self, propagation):
        dict.__init__(self, propagation)
        state = self.__dict__
        state['motions'] = MappingProxyType(dict(propagation.motions))
        state['demanded'] = propagation.demanded
        state['untraced'] = frozenset(propagation.untraced)
        state['follow_cuts'] = MappingProxyType(dict(propagation.follow_cuts))
        state['follow_closures'] = MappingProxyType(
            dict(propagation.follow_closures))
        state['terminal_keys'] = frozenset(propagation.terminal_keys)

    def _refuse(self, *args, **kwargs):
        raise TypeError('a reused Follow prefix is read-only')

    __setitem__ = __delitem__ = __ior__ = _refuse
    clear = pop = popitem = setdefault = update = _refuse
    __setattr__ = __delattr__ = _refuse


def proxy_snapshot(deltas, landings):
    return (MappingProxyType(dict(deltas)), MappingProxyType(dict(landings)))


def frozen_snapshot(deltas, landings):
    return (FrozenPropagation(deltas), MappingProxyType(dict(landings)))


def make_level(snapshot, continue_with_snapshot):
    def _constraint_level(self, constraint, held, values, admissions, t,
                          own, prefix_cache=None):
        eligible = (prefix_cache is not None and constraint.edges and
                    constraint.edges[-1].kind == 'follow' and
                    all(edge.kind == 'law' for edge in constraint.edges[:-1])
                    and type(t) is float and math.isfinite(t))
        cache_key = ((tuple(constraint.edges), struct.pack('!d', t))
                     if eligible else None)
        saved = prefix_cache.get(cache_key) if eligible else None
        if saved is None:
            counts['walks'] += 1
            deltas = self._deltas({input_id: delta * t
                                   for input_id, delta in admissions.items()})
            landings = {}
            for edge in constraint.edges:
                for key, increment in edge.increments(values, deltas,
                                                       landings=landings):
                    deltas[key] = increment
            if eligible:
                started = time.perf_counter()
                saved = snapshot(deltas, landings)
                counts['snapshot_s'] += time.perf_counter() - started
                counts['stores'] += 1
                prefix_cache[cache_key] = saved
                if continue_with_snapshot:
                    deltas, landings = saved
        else:
            counts['hits'] += 1
            deltas, landings = saved
        if continue_with_snapshot and eligible:
            assert type(deltas) is FrozenPropagation, type(deltas)
        arguments = {constraint.identifier: own}
        for read in constraint.reads:
            read_key = self.keys[read]
            arguments[read] = (landings[read_key]
                               if self._has_play_ancestor(read_key)
                               and read_key in landings
                               else held[read] + deltas[read_key])
        bound = constraint.graph.evaluate(arguments)
        own_key = self.keys[constraint.identifier]
        value = (landings[own_key]
                 if (self._has_play_ancestor(own_key)
                     or self.program.determiner.get(own_key, None) is not None
                     and self.program.determiner[own_key].kind == 'follow')
                 and own_key in landings
                 else held[constraint.identifier] + deltas[own_key])
        return value - bound if constraint.side == 'high' else bound - value
    return _constraint_level


if variant == 'proxy':
    Run._constraint_level = make_level(proxy_snapshot, False)
elif variant == 'frozen':
    Run._constraint_level = make_level(frozen_snapshot, True)
elif variant == 'nocache':
    searched = Run._searched_constraint

    def uncached(self, constraint, held, values, admissions, deltas=None,
                 prefix_cache=None):
        return searched(self, constraint, held, values, admissions, deltas,
                        None)
    Run._searched_constraint = uncached
elif variant != 'bench':
    raise SystemExit(f'unknown variant {variant}')

digest = hashlib.sha256()


def record(sim):
    for key in sorted(sim._run.bank):
        value = sim._run.bank[key]
        digest.update(repr(key).encode())
        digest.update(struct.pack('!d', value) if isinstance(value, float)
                      else repr(value).encode())


def scenario():
    # test_mechanistic: subtraction borrows through both registers and
    # addition undoes it -- 40 crank ticks of 0.1 s, every carry moving.
    sim = Sim(MechanisticCurta(), dt=.1)
    sim.move('digit_1', to=1)
    sim.move('crank_elevation', to=9)
    sim.move('crank_rotation', by=360, duration=2)
    started = time.perf_counter(), time.process_time()
    for _ in range(20):
        sim.run(.1)
        record(sim)
    assert register_reading(sim) == 10 ** 11 - 1
    sim.move('crank_elevation', to=0)
    sim.move('crank_rotation', by=360, duration=2)
    for _ in range(20):
        sim.run(.1)
        record(sim)
    assert register_reading(sim) == 0
    return (time.perf_counter() - started[0],
            time.process_time() - started[1])


print('machinome from', machinome.__file__, 'variant', variant,
      'cpu', sorted(os.sched_getaffinity(0)))
build = time.perf_counter()
walls, cpus = [], []
for repeat in range(repeats):
    wall, cpu = scenario()
    walls.append(wall)
    cpus.append(cpu)
    print(f'repeat {repeat}: 40 ticks wall {wall:.3f} s cpu {cpu:.3f} s')
print('wall', ' '.join(f'{w:.3f}' for w in walls),
      'min', f'{min(walls):.3f}')
print('cpu', ' '.join(f'{c:.3f}' for c in cpus), 'min', f'{min(cpus):.3f}')
print('counts per repeat', {k: (v / repeats if k != 'snapshot_s' else
                               round(v / repeats, 6))
                            for k, v in counts.items()})
print('bank sha256', digest.hexdigest())
```

`<scratch>/curta_runs.sh LABEL` ran 1.4's three Curta commands one after
another, in the background, each under `/usr/bin/time -f 'wall %e s'`:

```bash
#!/bin/bash
set -u
B=/home/asa/devel/machinome/machinome/WTs/fix-warts-3
P=/home/asa/devel/machinome/projects/Calculators/Curta-Type-I-3x
S=/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle8
V=/home/asa/devel/machinome/.venv/bin
LABEL=$1
run() {
    env -C "$S" PYTHONPATH="$B:$P" PYTHONDONTWRITEBYTECODE=1 \
        SOLID_BUILD_DIR="$S/build" taskset -c 14 "$@"
}
/usr/bin/time -f 'wall %e s' -o "$S/${LABEL}_radial.time" \
    bash -c "$(declare -f run); B=$B P=$P S=$S; run $V/pytest -p no:cacheprovider -q --durations=0 $P/simulation/test_radial_positioning_ball.py" \
    > "$S/${LABEL}_radial.txt" 2>&1
/usr/bin/time -f 'wall %e s' -o "$S/${LABEL}_mechanistic.time" \
    bash -c "$(declare -f run); B=$B P=$P S=$S; run $V/pytest -p no:cacheprovider -q --durations=0 '$P/simulation/test_mechanistic.py::MechanisticCurtaTest::test_subtraction_borrows_through_both_registers_and_addition_undoes_it'" \
    > "$S/${LABEL}_mechanistic.txt" 2>&1
/usr/bin/time -f 'wall %e s' -o "$S/${LABEL}_measure.time" \
    bash -c "$(declare -f run); B=$B P=$P S=$S; run $V/python $S/curta_measure.py bench" \
    > "$S/${LABEL}_measure.txt" 2>&1
echo done > "$S/${LABEL}_done"
```

### 1.2 The reproduction, unmodified tree

`env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1 .venv/bin/python <scratch>/repro.py`:

```
machinome from /home/asa/devel/machinome/machinome/WTs/fix-warts-3/machinome/__init__.py
edges ['follow']
walks 1 cache entries 1
levels miss/hit 0x0.0p+0 0x0.0p+0
miss deltas type: Propagation follow_cuts {('slot', 124231160468672): (0.0, 1.0)} follow_closures keys [('slot', 124231160468672)] untraced {('slot', 124231160468672)} motions []
hit deltas type: mappingproxy isinstance Propagation: False
motions AttributeError: 'mappingproxy' object has no attribute 'motions'
untraced AttributeError: 'mappingproxy' object has no attribute 'untraced'
follow_cuts AttributeError: 'mappingproxy' object has no attribute 'follow_cuts'
follow_closures AttributeError: 'mappingproxy' object has no attribute 'follow_closures'
demanded AttributeError: 'mappingproxy' object has no attribute 'demanded'
terminal_keys AttributeError: 'mappingproxy' object has no attribute 'terminal_keys'
```

As proposal.md has it: one walk, one cache entry, equal levels, a miss
`Propagation` carrying a Follow cut, its closures and an untraced key, and a
stored `mappingproxy` on which all six attributes raise `AttributeError`.

### 1.3 Focused and corpus tests, unmodified tree

`pytest -q -p no:cacheprovider tests/test_follow_prefix_cache.py
tests/test_running_follow.py tests/test_following_contact_repro.py
tests/test_running_corpus.py tests/test_clocked_corpus.py
tests/test_time_drive_corpus.py`:

```
83 passed, 241 subtests passed in 6.37s   (wall 7.44 s)
```

### 1.4 The Curta, unmodified tree

`<scratch>/curta_runs.sh before`. Before it, `ps -eo pid,args | grep
'[p]ytest\|[m]achinome test\|[m]achinome snapshot\|[m]achinome build'`
listed nothing, and no process used more than 5% of a CPU. All three ran on
CPU 14, one at a time.

- `pytest -p no:cacheprovider -q --durations=0 <project>/simulation/test_radial_positioning_ball.py`:
  `4 passed in 263.49s (0:04:23)`, wall 264.78 s. Per test (call):
  `test_long_and_short_requests_stop_at_the_same_contact` 85.87 s,
  `test_outward_bell_blocks_lift_without_turning_it_and_relief_is_explicit`
  64.43 s, `test_bell_pushes_outward_and_return_does_not_pull_the_free_ball_back`
  46.47 s, `test_raised_carriage_presses_the_ball_inward_and_blocks_the_crank`
  45.21 s.
- `pytest -p no:cacheprovider -q --durations=0 "<project>/simulation/test_mechanistic.py::MechanisticCurtaTest::test_subtraction_borrows_through_both_registers_and_addition_undoes_it"`:
  `1 passed in 210.38s (0:03:30)`, call 189.53 s, wall 211.74 s.
- `python <scratch>/curta_measure.py bench`: forty ticks wall 177.453 s,
  CPU 177.430 s (process wall 208.19 s with the model's construction),
  bank SHA-256
  `167ea1cd4849c606a22e9457081c329495cd747f149ab19dbefa2288b18b1fcf`, the
  digest Stage P recorded.

`git -C <project> status --short` after the runs listed only the four
untracked paths it listed before them (`"3D Printed Curta Calculator
Assembly_720p.mp4"`, `CREDITS`, `curta-2x-files/`,
`screenshots/reverser_inspection.png`), none written by this cycle.

## 2. Red test, on the unmodified source

`tests/test_follow_prefix_cache.py` imports `Propagation` from
`machinome.simulation.trajectory` and gains, in `FollowPrefixCacheTest`
after `test_exact_fraction_bits_and_distinct_edges_miss`, design.md
Decision 3's `test_a_reused_prefix_is_the_propagation_its_walk_produced`,
verbatim.

`pytest -q -p no:cacheprovider "tests/test_follow_prefix_cache.py::FollowPrefixCacheTest::test_a_reused_prefix_is_the_propagation_its_walk_produced"`:

```
>       self.assertIsInstance(reused, Propagation)
E       AssertionError: mappingproxy({('input', 'low'): 1.0, ('input', 'high'): -1.0, ('slot', 135001537596544): 1.0}) is not an instance of <class 'machinome.simulation.trajectory.Propagation'>
tests/test_follow_prefix_cache.py:102: AssertionError
FAILED tests/test_follow_prefix_cache.py::FollowPrefixCacheTest::test_a_reused_prefix_is_the_propagation_its_walk_produced
1 failed in 1.06s
```

Red for the reason tasks.md names.

## 3. The change

- 3.1 `machinome/simulation/trajectory.py`: `from types import
  MappingProxyType` among the imports, and design.md Decision 1's
  `FrozenPropagation(Propagation)` after `Propagation`, verbatim.
- 3.2 `machinome/simulation/run.py`: `from .trajectory import
  FrozenPropagation` after the `.program` import; in `_constraint_level`
  the eligible branch stores `(FrozenPropagation(deltas),
  MappingProxyType(dict(landings)))` and continues with `deltas, landings
  = saved`, with Decision 2's comment. `python -c 'import
  machinome.simulation, machinome.simulation.run as r;
  print("ok", r.FrozenPropagation)'` printed `ok <class
  'machinome.simulation.trajectory.FrozenPropagation'>`.
- 3.3 Section 2's test: `1 passed, 6 subtests passed in 1.01s`. The focused
  and corpus tests (1.3's command): `84 passed, 247 subtests passed in
  6.05s` (wall 7.02 s), 1.3's counts plus the one test and its six
  attribute subtests. `git -C <bench> status --short tests/`: ` M
  tests/test_follow_prefix_cache.py` only; no corpus was written.
  `<scratch>/repro.py` on the changed tree: the stored object is now
  `FrozenPropagation`, `isinstance Propagation: True`, all six attributes
  present, levels `0x0.0p+0` as before.

## 4. The Curta after the change

`<scratch>/curta_runs.sh after`, the same three commands, one at a time, on
CPU 14 (`ps` listed no run of ours before it):

| Command | Before (7b56c54) | After |
|---|---|---|
| `test_radial_positioning_ball.py` | 4 passed in 263.49 s, wall 264.78 s | 4 passed in 260.63 s, wall 261.98 s |
| — `test_long_and_short_requests_stop_at_the_same_contact` | 85.87 s | 86.26 s |
| — `test_outward_bell_blocks_lift_without_turning_it_and_relief_is_explicit` | 64.43 s | 65.08 s |
| — `test_bell_pushes_outward_and_return_does_not_pull_the_free_ball_back` | 46.47 s | 47.02 s |
| — `test_raised_carriage_presses_the_ball_inward_and_blocks_the_crank` | 45.21 s | 41.80 s |
| `test_mechanistic.py::...::test_subtraction_borrows_through_both_registers_and_addition_undoes_it` | 1 passed in 210.38 s, call 189.53 s, wall 211.74 s | 1 passed in 206.80 s, call 186.24 s, wall 208.02 s |
| `curta_measure.py bench`, forty ticks | wall 177.453 s, CPU 177.430 s | wall 176.593 s, CPU 176.571 s |
| bank SHA-256 | `167ea1cd4849c606a22e9457081c329495cd747f149ab19dbefa2288b18b1fcf` | `167ea1cd4849c606a22e9457081c329495cd747f149ab19dbefa2288b18b1fcf` |

The banks are bit-identical. Every wall time after the change is at or
below its baseline (the largest move is the raised-carriage test, 3.4 s
faster, inside the host's spread), so no rerun was needed under 4.1's 5%
rule. `git -C <project> status --short` listed the same four untracked
paths as before; nothing was written in the project.

## 5. Changelog and manual

- 5.1 The bullet "**A reused Follow prefix carries its paths.**" was
  appended, as tasks.md gives it, after the last bullet of the one
  `Unreleased` section of `docs/project/changelog.rst`.
- 5.2 `grep -rn --exclude-dir=adrs --exclude-dir=releases
  "prefix_cache\|prefix replay\|MappingProxyType\|Propagation" docs`: two
  lines, both in `docs/architecture.md`. Line 1450, "Propagation passes
  exact absolute landings down a chain;" (Play chains, ADR-131), and line
  1643, "Play and its downstream chain retain clearance-aware prefix
  replay." Neither describes how the Follow prefix cache stores a walk; no
  page is made wrong, and no page was edited.

## 6. Warts

- 6.1 The bullet "**The Follow prefix cache stores mapping proxies where a
  propagation used to flow.**" moved from `workflow/warts.md` ("# Review
  of the cycles landed after the 0.7.0 fold (2026-09-23)") to
  `workflow/archive/fix-warts-3-2026-10-06/resolved.md` under
  `` ## `snapshot-the-follow-prefix` `` with the line `From "Review of the
  cycles landed after the 0.7.0 fold (2026-09-23)":` and a "What shipped"
  paragraph. The moved text equals lines 1344-1355 of `workflow/warts.md`
  at HEAD (`diff` of the two, no output). The section's other two bullets
  stay; `grep -c "Follow prefix cache stores" workflow/warts.md` prints
  `0`.

## 7. Checks

Run on `machinome/simulation/trajectory.py`, `machinome/simulation/run.py`
and `tests/test_follow_prefix_cache.py`, on the working tree and on the
three files as they are at HEAD (extracted with `git show HEAD:<file>` into
`<scratch>/head/`).

- `flake8 --max-line-length=89` (pyenv shim): 17 findings after, 17 at
  HEAD; with line numbers stripped the two sorted lists are identical
  (`diff` no output). All are in lines this change did not touch (E127,
  E128, E201, E306, E731, F841 in `run.py` and `trajectory.py`); the test
  file is clean at HEAD and after. No new finding.
- `black --check` (26.5.1): `trajectory.py` and `run.py` "would reformat"
  at HEAD and after, as does the test file; the repository is not
  black-formatted (CI runs both steps with `continue-on-error: true`).
  Lines `black --diff` changes: `trajectory.py` 668 at HEAD, 680 after;
  `run.py` 947 and 944; the test file 134 and 142 (the new code in the
  files' single-quote style, and the new test's `(reused, landings), =`
  unpacking, which black parenthesises).

## 8. Sync and archive

- 8.1 By hand. In `openspec/specs/simulation/spec.md`, "Equivalent Follow
  Bound prefix probes may reuse a successful propagation" takes the
  delta's added paragraph (after the "Reuse SHALL NOT change any value"
  paragraph) and the added scenario "A reused prefix carries what a replay
  carries" (after "Prefix or Bound evaluation fails"). Before the edit the
  baseline requirement diffed against the delta showed only those two
  additions; after it the requirement cut from the spec up to the next
  requirement equals the delta's text, apart from the blank line that
  separates it from the next requirement. `git diff --stat --
  openspec/specs`: `openspec/specs/simulation/spec.md | 6 ++++++`.
  `openspec validate snapshot-the-follow-prefix`: "Change
  'snapshot-the-follow-prefix' is valid". `openspec validate simulation`:
  "Specification 'simulation' is valid".
- 8.2 `openspec archive snapshot-the-follow-prefix --yes --skip-specs`
  (the spec was synced by hand in 8.1, so the CLI's own sync was skipped):
  "Change 'snapshot-the-follow-prefix' archived as
  '2026-10-07-snapshot-the-follow-prefix'". The CLI dates the archive by
  the day it runs: the cycle's runs crossed midnight UTC, so the directory
  is dated 7 October where tasks.md was written expecting 6 October;
  tasks.md and the "What shipped" paragraph in `resolved.md` name the
  directory as it is. Its warnings: the Why section's length, and 14 of 16
  tasks complete (8.2 and 8.3, done after it and ticked in the archived
  copy). `openspec validate --specs`: `Totals: 45 passed, 0 failed (45
  items)`.
- 8.3 Section 2's test: `1 passed, 6 subtests passed in 0.99s`. The focused
  and corpus tests: `84 passed, 247 subtests passed in 6.34s` (wall
  7.32 s). `git -C <bench> status --short tests/`: ` M
  tests/test_follow_prefix_cache.py` only.
- The full suite, on the final tree, alone (`ps` showed no run of ours),
  `pytest -q -p no:cacheprovider` at the bench root: exit 0, wall
  645.61 s, `4668 passed, 4 skipped, 55 warnings, 6650 subtests passed in
  643.29s (0:10:43)`. No failure, no `Too many open files`.

Nothing is committed. `git -C <bench> status --short` lists the changed
`docs/project/changelog.rst`, `machinome/simulation/run.py`,
`machinome/simulation/trajectory.py`, `openspec/specs/simulation/spec.md`,
`tests/test_follow_prefix_cache.py`, `workflow/warts.md` and
`workflow/archive/fix-warts-3-2026-10-06/resolved.md`, the change's
directory moved to `openspec/changes/archive/2026-10-07-snapshot-the-follow-prefix/`.
