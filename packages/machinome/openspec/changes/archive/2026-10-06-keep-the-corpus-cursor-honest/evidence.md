# Evidence — `keep-the-corpus-cursor-honest`

Cycle 7 of the fix-warts-3 campaign (`workflow/ongoing/fix-warts-3.md`).
Bench `machinome/WTs/fix-warts-3`, branch `fix-warts-3`, planning commit
1437ed8 (`git -C <bench> rev-parse HEAD` printed
`1437ed80dd965b185dc3ebf7f2b5c482702955ba`). Every command below ran as
`env -C <bench> PYTHONPATH=<bench> /home/asa/devel/machinome/.venv/bin/<tool> ...`,
one process at a time, never in parallel. The interpreter check,
`python -c 'import machinome; print(machinome.__file__)'`, printed
`/home/asa/devel/machinome/machinome/WTs/fix-warts-3/machinome/__init__.py`.

`<scratch>` is the campaign scratchpad's `cycle7/` directory
(`/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle7/`).
It is not durable; the scripts this record depends on are copied below.

No project was run, and nothing was written in the `machinome-viewer`
checkout. No committed corpus was written: the generator ran only with an
output path under `<scratch>`.

## 1. Baseline on the unmodified tree (1437ed8)

### 1.1 The reproduction script

`<scratch>/reproduce.py`, run from the bench root:

```python
"""Reproduce the corpus cursor finding on the unmodified bench.

Run from the bench root with PYTHONPATH=<bench>.

A corpus machine (StopAndJump: a `wrap` crossing and a stop in one tick)
is scripted to snapshot, move, then restore and repeat the same move in
the SAME step. The run replays the first step exactly, so the honest
record of step 2 equals step 1's. The generator's record of step 2 is
compared with what `sim.crossings` / `sim.stops` hold after that step.
"""

import json

import tools.generate_running_corpus as gen

captured = []


class Capturing(gen.Sim):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        captured.append(self)


gen.Sim = Capturing

MOVE = {'input': 'crank', 'by': 30.0, 'duration': 0.05}
ENTRY = {'name': 'StopAndJump', 'dt': 0.05, 'steps': 2, 'script': [
    {'tick': 1, 'snapshot': 'a'},
    {'tick': 1, 'move': dict(MOVE), 'handle': 'h0'},
    {'tick': 2, 'restore': 'a'},
    {'tick': 2, 'move': dict(MOVE), 'handle': 'h0'},
]}

ticks = gen.run_machine(ENTRY)
sim = captured[-1]
first, restored = ticks
print('step 1 record: tick', first['tick'], 'crossings',
      len(first['crossings']), 'stops', len(first['stops']))
print('step 2 record: tick', restored['tick'], 'crossings',
      len(restored['crossings']), 'stops', len(restored['stops']))
print('after step 2 the run holds: sim.crossings', len(sim.crossings),
      [(c.tick, c.coordinate, c.primitive, c.level, c.t)
       for c in sim.crossings])
print('                            sim.stops    ', len(sim.stops),
      [(s.tick, s.coordinate, s.bound, s.value, s.t, s.inputs)
       for s in sim.stops])
print('banks equal:', first['bank'] == restored['bank'])
print('step 2 record equals step 1 record:', first == restored)

# The same scenario, without the same-step move: the restore on its own
# step, the move on the next (the periodic-contact corpus's shape).
ENTRY2 = {'name': 'StopAndJump', 'dt': 0.05, 'steps': 3, 'script': [
    {'tick': 1, 'snapshot': 'a'},
    {'tick': 1, 'move': dict(MOVE), 'handle': 'h0'},
    {'tick': 2, 'restore': 'a'},
    {'tick': 3, 'move': dict(MOVE), 'handle': 'h0'},
]}
ticks2 = gen.run_machine(ENTRY2)
print('restore on its own step, then move: step 3 crossings',
      len(ticks2[2]['crossings']), 'stops', len(ticks2[2]['stops']),
      'equals step 1:', ticks2[0] == ticks2[2])

# A move with no duration settles at the CURRENT tick, before sim.run:
# its records carry the previous tick number and the cursor reports them
# in the step that follows. Filtering by record tick would drop them.
ENTRY3 = {'name': 'PeriodicStop', 'dt': 0.1, 'steps': 2, 'script': [
    {'tick': 1, 'move': {'input': 'crank', 'to': 840.0},
     'handle': 'periodic0'},
]}
ticks3 = gen.run_machine(ENTRY3)
sim3 = captured[-1]
print('zero-duration move: step 1 record tick', ticks3[0]['tick'],
      'stops', len(ticks3[0]['stops']), 'ring ticks',
      [s.tick for s in sim3.stops])
print(json.dumps(restored['stops']), json.dumps(first['stops']))
```

### 1.2 The reproduction, unmodified tree

`env -C <bench> PYTHONPATH=<bench> .venv/bin/python <scratch>/reproduce.py`:

```
step 1 record: tick 1 crossings 1 stops 1
step 2 record: tick 1 crossings 0 stops 0
after step 2 the run holds: sim.crossings 1 [(1, 'folder.turn', 'ceil', 1.0, 0.16666666666666666)]
                            sim.stops     1 [(1, 'first.turn', 'high', 145.0, 0.5, ('crank',))]
banks equal: True
step 2 record equals step 1 record: False
restore on its own step, then move: step 3 crossings 1 stops 1 equals step 1: False
zero-duration move: step 1 record tick 1 stops 1 ring ticks [0]
[] [{"coordinate": "first.turn", "bound": "high", "value": 145.0, "t": 0.5, "inputs": ["crank"]}]
```

Step 2 restores and repeats step 1's move. The run holds the replayed
tick's crossing and stop, and the banks are equal, but the generator's
record of step 2 has neither. When the restore has a step of its own
(`ENTRY2`), the move's step records both; that record differs from step 1's
only by its tick number, since the restore step ran a tick of its own. The
last two lines are design.md's: a move with no duration records under the
tick before the step's own.

### 1.3 The corpus test files, unmodified tree

`pytest -q -p no:cacheprovider tests/test_running_corpus.py
tests/test_clocked_corpus.py tests/test_time_drive_corpus.py`:

```
57 passed, 241 subtests passed in 5.42s   (wall 6.43 s)
```

## 2. Red tests, on the unmodified source

`tests/test_running_corpus.py` gains, at module level, `RESTORE_MOVE`
(`{'input': 'crank', 'by': 30.0, 'duration': 0.05}`), `RESTORE_AND_STOP`
(1.1's `ENTRY`) and `ONE_STEP` (the same move with no snapshot or restore,
one step), and two tests in `CorpusReplayTest` after
`test_every_step_is_present`:

- `test_the_generator_records_a_stop_made_in_the_step_that_restores`
  (2.1): `run_machine(RESTORE_AND_STOP)` gives two ticks, the first with
  one crossing and one stop, the second equal to the first and to
  `run_machine(ONE_STEP)[0]`.
- `test_the_replay_refuses_an_entry_missing_a_record_made_after_a_restore`
  (2.2): `self.replay` of the entry whose ticks are `[once, once]`
  (`once = run_machine(ONE_STEP)[0]`) passes, and the same entry with the
  second tick's `crossings` and `stops` emptied raises
  `self.failureException`.

2.3, `pytest -q -p no:cacheprovider tests/test_running_corpus.py -k
'step_that_restores or made_after_a_restore'`, with only the tests added:

```
2 failed, 17 deselected in 1.21s
```

The generator test fails at its third assertion, the second tick's
`crossings` and `stops` being empty:

```
E       AssertionError: {'tic[85 chars]s': [], 'stops': [], 'commands': [{'handle': '[40 chars].0}]} != {'tic[85 chars]s': [{'relation': 'crank drives folder.turn', [262 chars].0}]}
E         {'bank': {'crank': 145.0, 'first.turn': 145.0, 'folder.turn': 110.0},
E          'commands': [{'admitted': 15.0, 'handle': 'h0', 'status': 'blocked'}],
E       -  'crossings': [],
E       -  'stops': [],
E       +  'crossings': [{'coordinate': 'folder.turn',
E       +                 'level': 1.0,
E       +                 'primitive': 'ceil',
E       +                 'relation': 'crank drives folder.turn',
E       +                 't': 0.16666666666666666}],
E       +  'stops': [{'bound': 'high',
E       +             'coordinate': 'first.turn',
E       +             'inputs': ['crank'],
E       +             't': 0.5,
E       +             'value': 145.0}],
E          'tick': 1}
tests/test_running_corpus.py:201: AssertionError
```

The replay test fails at the honest entry, the replay's crossing count
being `0` where the entry holds one:

```
tests/test_running_corpus.py:211:
tests/test_running_corpus.py:108: in replay
tests/test_running_corpus.py:139: in compare
E   AssertionError: 0 != 1 : StopAndJump tick 1
```

The test stops there, so the doctored entry is not reached on the
unmodified tree. Stage P's `<scratch>/probe_tests.py` ran the same two
replays against the unmodified helper and recorded the other half: "replay
as is, doctored entry: accepted".

## 3. The change

- 3.1 `tools/generate_running_corpus.py::run_machine`, in the action loop,
  after `apply_action(sim, action, handles, snapshots)`:

  ```python
  if 'restore' in action:
      # A restore clears the run's crossing and stop rings: count this
      # step's records from the cleared rings, or a record the step
      # makes after the restore is sliced away with the old ones.
      crossings_seen = stops_seen = 0
  ```

- 3.2 `tests/test_running_corpus.py::CorpusReplayTest.replay`: the same
  lines after `self.apply(sim, action, handles, snapshots)`, the comment
  wrapped one line longer for the deeper indent.

3.3, the two tests:

```
2 passed, 17 deselected in 1.11s
```

The three corpus test files:

```
59 passed, 241 subtests passed in 5.14s   (wall 6.12 s)
```

1.3's count plus the two tests.

## 4. The corpora after the change

4.1 `python tools/generate_running_corpus.py <scratch>/running-corpus.after.json`
(exit 0, wall 1.61 s):

```
<scratch>/running-corpus.after.json: 28 scenarios over 25 machines (Captured, CarryLead, Clearing, Clutch, FollowingContact, KinkedStop, MeasuredPlayCorpus, NegativeFollower, ObservedFollower, OvertakenFollower, PeriodicStop, PlayCorpus, RangedBlock, Ratchet, Remainder, ShiftedCarry, StationaryFollower, StopAndJump, StoppedClearing, Swept, Throwing, Train, TwoStops, Window, Wrapped), 401 ticks, 323767 bytes
```

Compared, with a `python -c` that reads the three files only, against
Stage P's `<scratch>/running-corpus.as-is.json` (the unmodified generator)
and `<scratch>/running-corpus.reset.json` (the proposed lines patched in
from a script):

```
scenarios 28 28
name/dt/steps/script/ticks identical, after vs as-is: True
same, after vs Stage P reset: True
whole document identical, after vs as-is: True
```

`cmp <scratch>/running-corpus.as-is.json <scratch>/running-corpus.after.json`:
no output, exit 0 (byte-identical). The change alters no value of the
running corpus. The difference between any regeneration and the committed
file (document version 11 against the committed version 5 to 10 controls,
and 27 floats in `ShiftedCarry` and `RangedBlock` within the `1e-9`
tolerance) is design.md's, and predates this change.

4.2 `<scratch>/reproduce.py` again:

```
step 1 record: tick 1 crossings 1 stops 1
step 2 record: tick 1 crossings 1 stops 1
after step 2 the run holds: sim.crossings 1 [(1, 'folder.turn', 'ceil', 1.0, 0.16666666666666666)]
                            sim.stops     1 [(1, 'first.turn', 'high', 145.0, 0.5, ('crank',))]
banks equal: True
step 2 record equals step 1 record: True
restore on its own step, then move: step 3 crossings 1 stops 1 equals step 1: False
zero-duration move: step 1 record tick 1 stops 1 ring ticks [0]
[{"coordinate": "first.turn", "bound": "high", "value": 145.0, "t": 0.5, "inputs": ["crank"]}] [{"coordinate": "first.turn", "bound": "high", "value": 145.0, "t": 0.5, "inputs": ["crank"]}]
```

The `ENTRY2` line is unchanged: its third step differs from its first in
the key `tick` only (2 against 1; checked with a `python -c` listing the
differing keys, `['tick']`), as before the change.

4.3 `git -C <bench> status --short tests/`:

```
 M tests/test_running_corpus.py
```

No corpus file is modified.

## 5. Changelog and manual

- 5.1 design.md Decision 3's bullet appended, verbatim, to the one
  `Unreleased` section of `docs/project/changelog.rst`, after the
  `name-solids-by-path` bullet.
- 5.2 `grep -rn 'generate_running_corpus\|running-corpus' docs
  CONTRIBUTING.rst --exclude-dir=adrs --exclude-dir=releases`, the
  changelog aside: `docs/architecture.md:3067` (the corpus is written from
  the framework's own run, exact for discrete state, refusing a corpus
  missing a feature), `docs/architecture.md:3392` (the running landing
  walk keeps `tests/running-corpus.json` byte-identical),
  `docs/reference/api.rst:838` and `:857` ("The conformance corpus": each
  tick with its bank, crossings, stops and command outcomes; the generator
  command). None says how a tick's crossings and stops are counted, and
  none is made wrong; `CONTRIBUTING.rst` has no match.

## 6. Checks

6.1, on `tools/generate_running_corpus.py` and
`tests/test_running_corpus.py`, each compared with the same file at HEAD
(`git show HEAD:<file> | <tool> ... -`):

- `flake8 --max-line-length=89` (the pyenv shim): the working tree reports
  `tools/generate_running_corpus.py:144:28: E128`, `:145:28: E128` and
  `:487:90: E501`; HEAD reports the same three, the E501 at `:482` (the
  five added lines shift it). `tests/test_running_corpus.py` is clean at
  HEAD and after. No new finding.
- `black --check` (26.5.1): both files "would reformat" at HEAD and after;
  the repository is not black-formatted (CI runs both steps with
  `continue-on-error: true`). `black --diff` grows by 2 changed lines for
  the generator (the new `'restore'` literal, single-quoted as the file
  is) and by 43 for the test file (the new constants and tests, in the
  file's single-quote style).

## 7. Warts

- 7.1 The section "# Corpus record cursor across restore (2026-09-20)"
  moved verbatim (from its "**Status: observed while validating Curta;
  ..." line to "...to repair evidence collection.", its one indented line
  kept) to `workflow/archive/fix-warts-3-2026-10-06/resolved.md`, under
  `` ## `keep-the-corpus-cursor-honest` `` after `name-solids-by-path`,
  with the "From ..." line and a "What shipped" paragraph; deleted from
  `workflow/warts.md`.
- 7.2 `workflow/warts.md` gains "## Findings from the framework cycle
  `keep-the-corpus-cursor-honest` (2026-10-06)" after the
  `name-solids-by-path` findings, with the one bullet **The crossing and
  stop rings are bounded in entries, not ticks**, and the triage line.
  Its facts were checked on the bench: `run.py:287`, `:292`, `:293` build
  all three rings with `_ring(record)`, which returns
  `deque(maxlen=record)` and whose refusal message reads "record=N keeps a
  ring of the most recent N ticks"; `sim.py:447` and `:458` document "The
  bounded ring `record=` asked for"; over the committed corpus, counting
  each ring's entries from the last restore, the fullest is `RangedBlock`'s
  crossing ring, 3 entries with `record = steps + 1 = 9`.

## 8. Sync and archive

- 8.1 By hand. In `openspec/specs/export/spec.md`, "The two runtimes share
  a conformance corpus" takes the delta's added paragraph (after the
  "A sampled fixture SHALL NOT be accepted" paragraph) and the added
  scenario "A stop made in the step that restores is recorded" (after
  "Every tick is present"). Before the edit, the baseline requirement
  diffed against the delta showed only those two additions; after it, the
  requirement cut from the spec up to the next requirement equals the
  delta's text (`diff` with no output). `git diff --stat --
  openspec/specs`: `openspec/specs/export/spec.md | 19 +++`.
  `openspec validate keep-the-corpus-cursor-honest`: "Change
  'keep-the-corpus-cursor-honest' is valid". `openspec validate export`:
  "Specification 'export' is valid".
- 8.2 `openspec archive keep-the-corpus-cursor-honest --yes --skip-specs`
  (the spec was synced by hand in 8.1, so the CLI's own sync was skipped):
  "Change 'keep-the-corpus-cursor-honest' archived as
  '2026-10-06-keep-the-corpus-cursor-honest'". Its warnings: the Why
  section's length, and 18 of 21 tasks complete (6.2, 8.2 and 8.3, done
  after it and ticked in the archived copy). `openspec validate --specs`:
  `Totals: 45 passed, 0 failed (45 items)`.
- 8.3 Section 2's two tests: `2 passed, 17 deselected in 1.06s`. The three
  corpus test files: `59 passed, 241 subtests passed in 5.30s` (wall
  6.40 s).
- 6.2 The full suite, on the final tree, alone (`ps -eo pid,args | grep
  '[p]ytest\|[m]achinome test\|[m]achinome snapshot\|[m]achinome build'`
  showed no run but the checking shell itself), `pytest -q -p
  no:cacheprovider` at the bench root: exit 0, wall 654.66 s,

  ```
  4667 passed, 4 skipped, 55 warnings, 6644 subtests passed in 652.09s (0:10:52)
  ```

  The previous cycle's full run recorded `4665 passed, 4 skipped, 55
  warnings, 6644 subtests passed`; the two added tests account for the
  difference.

Nothing is committed. `git -C <bench> status --short tests/` still lists
only `tests/test_running_corpus.py`: no corpus file was written.
