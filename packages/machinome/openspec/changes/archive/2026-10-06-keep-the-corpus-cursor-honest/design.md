## Context

### What the run records, and what a restore does to it

A running `Sim` built with `record=N` keeps three bounded rings
(`machinome/simulation/run.py:287-293`, `_ring` at `:1672-1687`): the
trajectory, the crossings and the stops. `Run.integrate` gathers one pass's
crossings and stops in fresh lists. It appends them to the rings only when
the pass commits (`:612-613`, `:737-740`). Each `Crossing` and `Stop`
carries the tick number of the pass that made it.

There are two kinds of pass. `sim.run(dt)` advances the clock and records
under the new tick number. A move with no duration settles at the CURRENT
tick, without advancing the clock (`Run.move`, `:476-480`). Its records
carry the tick number from before the step's own tick runs.

`Run.restore` (`:1571-1637`) puts the bank, the commands and `sim.tick`
back to the snapshot. Then it clears all three rings (`:1633-1636`). The
run forgets every crossing and stop it had recorded.

### How the running corpus counts a step's records

`tools/generate_running_corpus.py::run_machine` (`:370-405`) applies each
step's script actions, runs one tick, and then records:

```python
crossings = sim.crossings[crossings_seen:]
stops = sim.stops[stops_seen:]
crossings_seen = len(sim.crossings)
stops_seen = len(sim.stops)
```

A step's record is therefore everything that entered the rings since the
previous step's record. That includes a script action's own pass, such as a
move with no duration. `CorpusReplayTest.replay`
(`tests/test_running_corpus.py:66-91`) counts the same way, and compares
the slices with the fixture.

The counters are never told about a restore. After a restore the rings are
empty, but `crossings_seen` and `stops_seen` still hold the old lengths.
The step's tick appends its records from index 0. The slice starts at the
old length, so it loses as many of the new records as the old count. A
following step whose restore made no records heals by itself, because its
counter is reset to the length of the cleared rings. This is why the
committed scenarios, which all restore on a step of their own, are intact.

`tools/generate_time_drive_corpus.py::run` (`:69-92`) already handles
this. It sets both counters to `0` after a restore or a reset, with the
comment "Restore clears both rings. Do not lose a new event by slicing it
at the pre-restore cursor." The clocked corpus
(`tools/generate_clocked_corpus.py::apply_step`, `:386-455`) records each
request's own `result.stops` and `result.commits`, and keeps no counter.

### Reproduction at `298ca6b`

Interpreter check:
`env -C <bench> PYTHONPATH=<bench> .venv/bin/python -c 'import machinome; print(machinome.__file__)'`
prints `/home/asa/devel/machinome/machinome/WTs/fix-warts-3/machinome/__init__.py`.

`<scratch>/reproduce.py` wraps the generator's `Sim` to keep the instance.
It runs `run_machine` on this entry, `StopAndJump` being the corpus machine
whose single tick carries a `wrap` crossing and a stop:

```python
MOVE = {'input': 'crank', 'by': 30.0, 'duration': 0.05}
{'name': 'StopAndJump', 'dt': 0.05, 'steps': 2, 'script': [
    {'tick': 1, 'snapshot': 'a'},
    {'tick': 1, 'move': dict(MOVE), 'handle': 'h0'},
    {'tick': 2, 'restore': 'a'},
    {'tick': 2, 'move': dict(MOVE), 'handle': 'h0'},
]}
```

Output:

```
step 1 record: tick 1 crossings 1 stops 1
step 2 record: tick 1 crossings 0 stops 0
after step 2 the run holds: sim.crossings 1 [(1, 'folder.turn', 'ceil', 1.0, 0.16666666666666666)]
                            sim.stops     1 [(1, 'first.turn', 'high', 145.0, 0.5, ('crank',))]
banks equal: True
step 2 record equals step 1 record: False
zero-duration move: step 1 record tick 1 stops 1 ring ticks [0]
```

The last line comes from a third entry, `PeriodicStop` with a move to
`840.0` and no duration. Its stop is reported in the record of step 1
(tick 1), although its own `tick` field is `0`.

`<scratch>/probe_tests.py` runs both proposed tests against the
unmodified tree. It also runs them against the proposed two lines, patched
in from the script and never written to the bench:

```
one step, no restore: 1 1 1 [{'handle': 'h0', 'status': 'blocked', 'admitted': 15.0}]
generator as is: step 2 == step 1: False ; step 2 == one honest step: False
generator cursor reset: step 2 == step 1: True ; step 2 == one honest step: True
replay as is, honest entry: refused: 0 != 1 : StopAndJump tick 1
replay as is, doctored entry: accepted
replay cursor reset, honest entry: accepted
replay cursor reset, doctored entry: refused: 1 != 0 : StopAndJump tick 1
```

`<scratch>/compare_corpus.py` regenerates the whole running corpus into
the scratchpad twice, once as is and once with the counters reset after a
restore. The command takes 1.9 s. Every scenario's `name`, `dt`, `steps`,
`script` and `ticks` are identical between the two regenerations, and the
count of crossings and stops in every tick is unchanged.

Neither regeneration is identical to the committed file, for reasons that
are not this change's. Every committed document is a version 5 to 10
control, and the bench publishes version 11 with a new `program.identity`.
`tests/source_timing_compatibility.py` lets exactly that difference
through. `ShiftedCarry` (2 values) and `RangedBlock` (25 values) also
differ by at most `5.5e-13` relative, inside the corpus's `1e-9` tolerance.

The three corpus test files pass on the unmodified bench:
`pytest -q tests/test_running_corpus.py tests/test_clocked_corpus.py
tests/test_time_drive_corpus.py` reports `57 passed, 241 subtests passed in
5.22s`.

`<scratch>` is
`/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle7/`.

## Goals / Non-Goals

**Goals**

- A step's record in the running corpus holds every crossing and stop the
  run made in that step after a restore, crossings and stops alike.
- The suite's replay counts the same way, so it refuses an entry that
  omits such a record.
- Red first, on a restore followed by a stop in the same step.

**Non-Goals**

- Any change to `Sim`, `Run`, a machine, a command or a document.
- Any change to a committed corpus, or a regeneration.
- The viewer's replay, which is the viewer repository's.
- The rings' bound (Open Question 2).

## Decisions

### 1. Start the counters again after a restore

In `run_machine` and in `CorpusReplayTest.replay`, right after an action
that restores is applied:

```python
for action in script.get(step, ()):
    apply_action(sim, action, handles, snapshots)
    if 'restore' in action:
        # A restore clears the run's crossing and stop rings: count this
        # step's records from the cleared rings, or a record the step
        # makes after the restore is sliced away with the old ones.
        crossings_seen = stops_seen = 0
```

(In the replay the call is `self.apply(...)`.)

The meaning of a step's record does not change: it is still everything
recorded since the previous step's record. That includes the step's own
script, so a move with no duration is still reported in the step that
applies it. After a restore, "since" is measured from the empty rings. A
record a script action made before a restore in the same step was cleared
by the run, and the corpus does not invent it. That record is the run's
own past, which the restore abandoned. The time-drive generator already
counts this way, so the three generators now agree.

The counters are reset after the action rather than at the top of the
step. A restore can come after other actions of the same step, such as
the snapshot above, and only what follows it is in the rings.

**Alternatives considered**

- **Select each step's records by their `tick` field** (`one.tick ==
  sim.tick`). This holds across a restore without any counter. It is
  rejected because a move with no duration records under the tick BEFORE
  the step's tick (Context, `ring ticks [0]` for a record reported at
  tick 1). Filtering would move those records out of the step that applies
  them. The committed `PeriodicStop`, `OvertakenFollower`,
  `NegativeFollower`, `ObservedFollower`, `FollowingContact` and
  `StationaryFollower` scenarios all move with no duration, so their
  records would change. This alternative would change values in a
  committed corpus.
- **Take the counters as the rings' lengths after every action.** This is
  equivalent here, because only a restore shrinks a ring. It is more code
  and says less about why.
- **Share one counting helper between the generator and the replay.** The
  replay is deliberately independent ("Construct, script and step one
  machine exactly as the generator did"), so that it can catch the
  generator. The two lines are written in both.
- **Keep the rings through a restore in `Run.restore`.** This changes the
  run, which the warts entry forbids, and it would make `sim.stops` report
  a stop from a future the restore abandoned.

### 2. Tests

Both tests go in `CorpusReplayTest` (`tests/test_running_corpus.py`),
after `test_every_step_is_present`. They share one module-level script,
`RESTORE_AND_STOP`, which is the `StopAndJump` entry above. Two shapes are
built from it: the entry itself, and `ONE_STEP`, the same move with no
snapshot or restore, run for one step. `ONE_STEP` is the honest record and
does not depend on the counters.

- `test_the_generator_records_a_stop_made_in_the_step_that_restores`:
  `run_machine(RESTORE_AND_STOP)` gives two ticks. The first carries one
  crossing and one stop, so the comparison is not vacuous. The second is
  equal to the first in every key: tick, bank, crossings, stops and
  commands. It is also equal to `run_machine(ONE_STEP)[0]`. Red today,
  because the second tick's `crossings` and `stops` are `[]`.
- `test_the_replay_refuses_an_entry_missing_a_record_made_after_a_restore`:
  the expected ticks are `[once, once]`, where `once =
  run_machine(ONE_STEP)[0]`. `self.replay` of that entry passes. With the
  second tick's `crossings` and `stops` emptied, `self.replay` raises
  `self.failureException`. Red today, twice over. The honest entry is
  refused with `0 != 1 : StopAndJump tick 1`. The doctored entry is
  accepted, so `assertRaises` fails.

The tests import `run_machine` from `tools.generate_running_corpus`, as
`CoverageGuardTest` already imports `uncovered_features`.

### 3. Records

Changelog bullet, appended to the one `Unreleased` section of
`docs/project/changelog.rst`:

```rst
* **The running corpus keeps a stop made after a restore.**
  ``tools/generate_running_corpus.py``, and the suite's replay of
  ``tests/running-corpus.json``, counted a step's crossings and stops from
  where the run's record stood before a scripted restore, although the
  restore clears that record. A crossing or stop that the same step then
  made was left out of the step's entry, and the replay agreed with the
  omission. Both now count from the cleared record, as the time-drive
  generator already did. No committed corpus has such a step, and none
  changes (keep-the-corpus-cursor-honest).
```

The warts section "Corpus record cursor across restore (2026-09-20)" moves
verbatim to `workflow/archive/fix-warts-3-2026-10-06/resolved.md`, with a
"What shipped" paragraph. The ring-bound finding of Open Question 2 is
filed in `warts.md` under a new section, "Findings from the framework
cycle `keep-the-corpus-cursor-honest` (2026-10-06)".

## Proof plan

1. Baseline on the unmodified tree: the interpreter check, the three
   corpus test files (`57 passed, 241 subtests passed` at Stage P), and
   `reproduce.py` and `compare_corpus.py` rerun with their output
   recorded.
2. The two tests of Decision 2, seen red for the reasons given.
3. The two lines in each helper. The two tests are green, and the three
   corpus files are green with two more tests.
4. The changed generator writes into the scratchpad,
   `tools/generate_running_corpus.py <scratch>/running-corpus.after.json`,
   never over the committed file. Every scenario's `name`, `dt`, `steps`,
   `script` and `ticks` are identical to Stage P's
   `<scratch>/running-corpus.as-is.json`. `git status --short tests/`
   shows no corpus file changed. The time-drive test, which rebuilds its
   corpus from its own generator, passes unchanged.
5. `black --check` and `flake8 --max-line-length=89` on the two touched
   files, then the full suite once.

The originating project is not run: the Curta's corpus case is in the
framework's own tests, and the brief forbids running it.

## Risks / Trade-offs

- The replay helper and the generator stay two copies of one rule. This
  is deliberate (Decision 1, Alternatives), and the generator test and the
  replay test pin each copy separately.
- The viewer's replay keeps the old counting. It passes as long as the
  corpus has no step that restores and records. If such a scenario is ever
  added, the viewer must take the same two lines first.

## Open Questions

1. **Should the running corpus carry a scenario that restores and stops in
   one step?** It would make the viewer's replay meet this case. Adding it
   needs a regeneration of `tests/running-corpus.json`, which today also
   republishes every document at version 11 and rewrites 27 float values
   within tolerance. Those are changes to existing entries, beyond the
   added records. It is also new coverage the viewer must then replay.
   **Recommendation:** no, not in this change. The framework's two tests
   pin the generator and the replay. The viewer's replay is reported to
   the orchestrator, for the viewer repository to fix on its own counters.
   A scenario can be added when the corpus is next regenerated for a reason
   of its own. **Who answers:** the orchestrator; the pilot if the
   orchestrator wants the corpus widened now. Answered at review
   (6 October 2026): no scenario in this change; the viewer's replay
   is recorded for the viewer's own step.
2. **The rings are bounded in entries, not ticks.** `_ring(record)` is
   `deque(maxlen=record)` for the crossing and stop rings as well as the
   trajectory. A run with more than `record` crossings drops the oldest
   ones. A counter that has reached a full ring's length can no longer
   advance, so a corpus generated from such a run would silently record
   nothing more. The generator sizes `record` as `steps + 1`. The fullest
   committed scenario holds 3 entries in a ring of 9 (`RangedBlock`), so
   nothing is lost today. `Sim.crossings` documents "the bounded ring
   `record=` asked for", without saying what it counts. **Recommendation:**
   file it as a finding in `warts.md`, and do not repair it here. Either a
   generator guard or a change to the ring's unit is a decision of its own,
   and no scenario needs it. **Who answers:** the orchestrator's triage.
   Answered at review (6 October 2026): filed as a finding, not repaired.
