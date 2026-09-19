# Evidence: cancel-stops-the-command

Everything below is run from the cycle worktree
`/home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts`, branch
`fix-warts`, at `c216cfff4c0d39bea2bbb27822b36dde594046ef` (the planning
base of this cycle), with the workspace environment:

    PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python

    $ PYTHONPATH="$PWD" .venv/bin/python -V
    Python 3.12.3
    $ PYTHONPATH="$PWD" .venv/bin/python -c "import solid_node; print(solid_node.__file__)"
    /home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts/solid_node/__init__.py

The import line is recorded because the same venv resolves `solid_node`
to the PRIMARY checkout without `PYTHONPATH`; every run below was made
against this worktree.

The probe scripts are kept beside this file under `evidence/`:
`evidence/probe.py` (the wart's own reproduction, verbatim),
`evidence/probe_scenarios.py` (the twelve scenarios the fix must cover)
and `evidence/pyproject.toml`, the `[tool.solid-node]` file the
reproduction says to put beside them. They are run from that directory.

## Baseline at the planning base

    $ PYTHONPATH="$PWD" .venv/bin/python -m pytest \
        tests/test_running_simulation.py tests/test_running_stops.py \
        tests/test_running_jumps.py tests/test_running_document.py \
        tests/test_running_corpus.py -q
    232 passed, 2 warnings, 480 subtests passed in 33.54s

The two warnings are the pre-existing `FutureWarning`s about
`Valvetrain.render()` reading a driver; they are not this change's.

## 1. The wart's reproduction, run against this worktree

`workflow/warts.md`, "Pin tumbler lock (2026-09-14, running-command
cancellation)", carries a minimal reproduction. It is `evidence/probe.py`
character for character, with the two comment lines dropped. Run:

    $ cd openspec/changes/cancel-stops-the-command/evidence
    $ PYTHONPATH=<worktree> /home/asa/devel/libresolid-studio/.venv/bin/python probe.py

Output, verbatim:

    cancelled 0.5 {'carriage.travel': 0.5, 'feed': 0.5} 1
    Traceback (most recent call last):
      File ".../openspec/changes/cancel-stops-the-command/evidence/probe.py", line 23, in <module>
        sim.move("feed", by=1, duration=0.02)
      File ".../solid_node/simulation/sim.py", line 222, in move
        return self._running('move()').move(input_id, by=by, to=to,
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File ".../solid_node/simulation/run.py", line 395, in move
        self._claim(input_id)
      File ".../solid_node/simulation/run.py", line 448, in _claim
        raise ValueError(
    ValueError: 'feed' is already owned by <move feed cancelled: 0.5 admitted>. An input has one owner at a time: cancel that command, or release the rate with rate(input, 0), before asking for another.

(The `...` prefixes are the worktree path, elided for width; the run
itself printed the absolute paths under
`/home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts`.)

The finding reproduces exactly as filed:

- a `move` of 5 mm over 0.2 s, cancelled BEFORE the first tick, still
  admits `0.5` mm on the next tick and moves `feed` and
  `carriage.travel` with it;
- the handle reports `cancelled` and `0.5` admitted at the same time;
- `len(sim.commands) == 1` — the cancelled command is still the run's
  active command for `feed`;
- the replacement move is refused, by a message telling the caller to
  cancel the command it has already cancelled.

## 2. The twelve scenarios, before the fix

`evidence/probe_scenarios.py` runs the scenarios the proposal and the
spec delta cover, against the same worktree, on a two-input machine
(`feed`, `other`, each driving a prismatic carriage with
`range=(0, 12)`), `dt=0.02`. Output, verbatim:

    == 1. cancel before the first tick ==
    after one tick:
        <move feed cancelled: 0.5 admitted>
        state={'carriage.travel': 0.5, 'feed': 0.5, 'other': 0.0, 'second.travel': 0.0} commands=(<move feed cancelled: 0.5 admitted>,) tick=1
    == 2. cancel midway through a move ==
    three ticks, cancel, three ticks:
        <move feed cancelled: 3.0 admitted>
        state={'carriage.travel': 3.0, 'feed': 3.0, 'other': 0.0, 'second.travel': 0.0} commands=(<move feed cancelled: 3.0 admitted>,) tick=6
    == 3. cancel midway through a rate ==
    three ticks, cancel, three ticks:
        <rate feed cancelled: 1.2000000000000002 admitted>
        state={'carriage.travel': 1.2000000000000002, 'feed': 1.2000000000000002, 'other': 0.0, 'second.travel': 0.0} commands=(<rate feed cancelled: 1.2000000000000002 admitted>,) tick=6
    == 4. immediate replacement after cancel ==
        replacement refused: 'feed' is already owned by <move feed cancelled: 0 admitted>. An input has one owner at a time: cancel that command, or release the rate with rate(input, 0), before asking for another.
    == 5. repeated cancel ==
        True cancelled 1
    == 6. unrelated input continues ==
    feed cancelled, other left alone:
        <move feed completed: 5.0 admitted>
        <move other completed: 5.0 admitted>
        state={'carriage.travel': 5.0, 'feed': 5.0, 'other': 5.0, 'second.travel': 5.0} commands=() tick=10
    == 7. a blocked command cancelled ==
        <move feed blocked: 12.0 admitted> commands= ()
        after cancel: <move feed blocked: 12.0 admitted>
    == 8. a completed command cancelled ==
        <move feed completed: 5.0 admitted>
    == 9. a zero-duration move cancelled ==
        <move feed completed: 5 admitted> commands= ()
    == 10. snapshot taken AFTER a cancel, restored ==
        snapshot commands: (('feed', 'move', 5, None, 10, 0, 1.0, 'cancelled'),)
        after restore: <move feed cancelled: 2.0 admitted> (<move feed cancelled: 1.0 admitted>,) {'carriage.travel': 1.0, 'feed': 1.0, 'other': 0.0, 'second.travel': 0.0}
        two ticks past the restore: {'carriage.travel': 2.0, 'feed': 2.0, 'other': 0.0, 'second.travel': 0.0} (<move feed cancelled: 2.0 admitted>,)
    == 11. snapshot taken BEFORE a cancel, restored after it ==
        after restore: <move feed cancelled: 1.0 admitted> (<move feed active: 1.0 admitted>,) {'carriage.travel': 1.0, 'feed': 1.0, 'other': 0.0, 'second.travel': 0.0}
    == 12. determinism: the same script twice ==
        True ('cancelled', 3.5, {'carriage.travel': 3.5, 'feed': 3.5, 'other': 0.0, 'second.travel': 0.0})

What it establishes, scenario by scenario, and what the proposal says
each must become:

| # | today | after this change |
| --- | --- | --- |
| 1 | cancelled before the first tick, `0.5` admitted anyway | `0` admitted, nothing moves |
| 2 | the move is `0.5` mm a tick, so it stood at `1.5` mm when it was cancelled and at `3.0` mm three ticks later: it kept admitting right through the cancel | `1.5` mm admitted, and the bank stands there for every later tick |
| 3 | a cancelled RATE goes on accumulating | stops at the cancel, `0.6` -- the planning-stage note here first read `1.2`, a prediction error corrected in section 8 |
| 4 | the replacement is refused, naming a cancelled owner | accepted |
| 5 | `cancel()` returns the handle, is idempotent on the status, and leaves `len(sim.commands) == 1` | idempotent, and `sim.commands` is empty |
| 6 | `other` completes normally — but `feed`, cancelled before its first tick, also reaches `5.0` and reports `completed`: the cancel left no trace at all | `other` unchanged; `feed` stands at `0` reporting `cancelled` |
| 7 | a `blocked` handle cancelled keeps `blocked` — already correct | unchanged |
| 8 | a `completed` handle cancelled keeps `completed` — already correct | unchanged |
| 9 | a zero-duration move is `completed` at once and unaffected by a later cancel — already correct | unchanged |
| 10 | the cancelled command is IN the snapshot (`status 'cancelled'` in the record tuple) and a restore RESURRECTS it: `sim.commands` holds it again and the next ticks move `feed` again | the snapshot carries no command; the restore leaves `sim.commands` empty and nothing moves |
| 11 | a snapshot taken before the cancel restores a fresh `active` command from the recorded progress, the cancelled handle keeping its own report | unchanged — this is what restore already means |
| 12 | the same script replayed twice gives the same bank, tick and handle report | unchanged — admission is a function of the tick count, and this change adds no wall-clock input |

Scenarios 7, 8, 9, 11 and 12 are recorded because they are behaviour the
change must NOT alter; the spec delta pins them so a future reader knows
they were checked rather than assumed.

## 3. Where the defect is, in the code at this base

- `solid_node/simulation/run.py:158` `Command.cancel()` — sets
  `self.status = 'cancelled'` when the status is `active`, and returns.
  Nothing else.
- `solid_node/simulation/run.py:172` `Command.admits()` — a pure
  function of the tick count and the kind; it never reads `status`.
- `solid_node/simulation/run.py:471` `Run.integrate()` — at line 493 iterates
  `self.active.items()` and asks every entry for its admission.
- `solid_node/simulation/run.py:445` `Run._claim()` — refuses when
  `self.active.get(input_id)` is not `None`, whatever that command's
  status is.
- `solid_node/simulation/run.py:1115` `Run.snapshot()` — records
  `command.record()` for every command in `active`, and `record()`'s
  eighth field is the status, which is how a `cancelled` command reaches
  a snapshot (scenario 10).

The five retirement sites that DO release the input, for comparison:
`Run.rate` (line 406, `completed` for `rate(input, 0)`), the completion
loop at the end of `Run.integrate` (lines 614-617, `completed`),
`Run._block` (line 1019, `blocked`), `Run._refuse` (line 1055,
`refused`) and `Run.restore` (line 1139-1141, `cancelled`). Each sets a
status and removes the entry from `active`; `Command.cancel()` is the
only one that does the first without the second.

## 4. The new tests, RED (task 1.4)

`tests/test_running_simulation.py` gained `CancelTest` (task 1.2, eight
tests, one per bullet) and two scenarios in `SnapshotTest` (task 1.3).
Run against this worktree, still at the defect:

    $ PYTHONPATH="$PWD" .venv/bin/python -m pytest \
        tests/test_running_simulation.py -k "CancelTest or SnapshotTest" -q
    7 failed, 8 passed, 55 deselected in 1.45s

The eight that pass today are the ones the design says must NOT change
(`test_cancel_on_a_retired_handle_does_nothing`, over `completed`,
`blocked` and `refused` handles; `test_a_cancelled_run_replays_identically`,
which is deterministic whether or not the bug fires; and the five
pre-existing `SnapshotTest` scenarios plus the new
`test_a_snapshot_before_a_cancel_reissues_the_command`, which restore
behaviour the defect does not touch). The seven RED failures are the
wart's own symptom inside the suite:

    ______ SnapshotTest.test_a_snapshot_after_a_cancel_carries_no_command ______
    AssertionError: Tuples differ: (('crank', 'move', 10.0, None, 10, 0, 2.0, 'cancelled'),) != ()
    - a cancelled command is still in the snapshot.

    ____________________ CancelTest.test_a_cancelled_rate_stops ____________________
    AssertionError: {'crank': 54.0, ...} != {'crank': 27.0, ...}
    - a cancelled rate goes on accumulating for the seven ticks after the cancel.

    ______________ CancelTest.test_a_replacement_is_accepted_at_once _______________
    ValueError: 'crank' is already owned by <move crank cancelled: 3.0 admitted>.
    An input has one owner at a time: cancel that command, or release the
    rate with rate(input, 0), before asking for another.
    - the replacement is refused, naming the command it replaces.

    __________ CancelTest.test_cancel_before_the_first_tick_moves_nothing __________
    AssertionError: 1.0 != 0.0
    - a move cancelled before its first tick still admits one tick's travel.

    ____________ CancelTest.test_cancel_midway_keeps_the_travel_it_made ____________
    AssertionError: {'crank': 10.0, ...} != {'crank': 3.0, ...}
    - the move keeps running through the cancel and completes.

    _______ CancelTest.test_cancelling_one_command_leaves_the_other_running ________
    AssertionError: Tuples differ: (<move crank cancelled: 0 admitted>, <move lever active: 0 admitted>) != (<move lever active: 0 admitted>,)
    - the cancelled command is still in sim.commands.

    _____________ CancelTest.test_cancelling_twice_is_cancelling_once ______________
    ValueError: 'crank' is already owned by <move crank cancelled: 3.0 admitted>.
    An input has one owner at a time: cancel that command, or release the
    rate with rate(input, 0), before asking for another.
    - the replacement issued between the two cancels is refused for the
      same reason as above.

This is exactly the wart's own symptom (section 1 above) reproduced by
the suite: travel admitted after a cancel, and a replacement refused by
a message that tells the caller to cancel the command it already
cancelled.

## 5. The fix: one retirement path, six callers (section 2)

`solid_node/simulation/run.py`: `Command` gains a `_run` slot, set to
`None` in `__init__` and set to `self` wherever a command enters
`active` (`Run.move`, `Run.rate`, and the reconstruction loop in
`Run.restore`). `Run._retire(command, status)` is the one method every
retirement now goes through: it sets `command.status`, removes the entry
from `active` only when `self.active.get(command.input) is command`,
and drops `command._run`. `_block` calls it with `'blocked'`, `_refuse`
with `'refused'`, the completion loop at the end of `integrate` and
`rate(input, 0)` with `'completed'`, `restore` with `'cancelled'` over a
list of the pre-restore active commands, and `Command.cancel()` — which
no longer touches `self.status` directly — with `'cancelled'`, guarded
by `self.status == 'active' and self._run is not None`. `cancel()` does
not call `Run._owns()` (design decision 5) and touches no coordinate.

## 6. Green (task 2.5)

The twelve new tests (`CancelTest`, eight tests, and two added
`SnapshotTest` scenarios) against the fixed worktree:

    $ PYTHONPATH="$PWD" .venv/bin/python -m pytest \
        tests/test_running_simulation.py -k "CancelTest or SnapshotTest" -q
    15 passed, 55 deselected in 1.25s

The five running test files named in task 1.1, against the fixed
worktree:

    $ PYTHONPATH="$PWD" .venv/bin/python -m pytest \
        tests/test_running_simulation.py tests/test_running_stops.py \
        tests/test_running_jumps.py tests/test_running_document.py \
        tests/test_running_corpus.py -q
    242 passed, 2 warnings, 480 subtests passed in 31.60s

242 is the baseline's 232 plus the ten new tests (eight `CancelTest`,
two `SnapshotTest`); 480 subtests and the two pre-existing
`FutureWarning`s are exactly the baseline's — the other five
retirements, `test_running_stops.py`'s stop scenarios and the corpus
replay are unchanged.

## 7. The wart's reproduction, re-run against the fixed worktree

    $ cd openspec/changes/cancel-stops-the-command/evidence
    $ PYTHONPATH=<worktree> /home/asa/devel/libresolid-studio/.venv/bin/python probe.py

Output, verbatim:

    cancelled 0 {'carriage.travel': 0.0, 'feed': 0.0} 0

No travel admitted after the cancel, `feed` and `carriage.travel` stand
at `0.0`, `len(sim.commands) == 0`, and the final line —
`sim.move("feed", by=1, duration=0.02)` — raises nothing: the
replacement is accepted. Compare section 1's pre-fix run, which printed
`0.5` admitted travel, moved the carriage, and raised `ValueError` on
that same line.

## 8. `evidence/probe_scenarios.py`, re-run: before and after side by side

    $ PYTHONPATH=<worktree> /home/asa/devel/libresolid-studio/.venv/bin/python probe_scenarios.py

Output, verbatim:

    == 1. cancel before the first tick ==
    after one tick:
        <move feed cancelled: 0 admitted>
        state={'carriage.travel': 0.0, 'feed': 0.0, 'other': 0.0, 'second.travel': 0.0} commands=() tick=1
    == 2. cancel midway through a move ==
    three ticks, cancel, three ticks:
        <move feed cancelled: 1.5 admitted>
        state={'carriage.travel': 1.5, 'feed': 1.5, 'other': 0.0, 'second.travel': 0.0} commands=() tick=6
    == 3. cancel midway through a rate ==
    three ticks, cancel, three ticks:
        <rate feed cancelled: 0.6000000000000001 admitted>
        state={'carriage.travel': 0.6000000000000001, 'feed': 0.6000000000000001, 'other': 0.0, 'second.travel': 0.0} commands=() tick=6
    == 4. immediate replacement after cancel ==
    replacement accepted:
        <move feed cancelled: 0 admitted>
        <move feed active: 0 admitted>
        state={'carriage.travel': 0, 'feed': 0, 'other': 0, 'second.travel': 0} commands=(<move feed active: 0 admitted>,) tick=0
    == 5. repeated cancel ==
        True cancelled 0
    == 6. unrelated input continues ==
    feed cancelled, other left alone:
        <move feed cancelled: 0 admitted>
        <move other completed: 5.0 admitted>
        state={'carriage.travel': 0.0, 'feed': 0.0, 'other': 5.0, 'second.travel': 5.0} commands=() tick=10
    == 7. a blocked command cancelled ==
        <move feed blocked: 12.0 admitted> commands= ()
        after cancel: <move feed blocked: 12.0 admitted>
    == 8. a completed command cancelled ==
        <move feed completed: 5.0 admitted>
    == 9. a zero-duration move cancelled ==
        <move feed completed: 5 admitted> commands= ()
    == 10. snapshot taken AFTER a cancel, restored ==
        snapshot commands: ()
        after restore: <move feed cancelled: 1.0 admitted> () {'carriage.travel': 1.0, 'feed': 1.0, 'other': 0.0, 'second.travel': 0.0}
        two ticks past the restore: {'carriage.travel': 1.0, 'feed': 1.0, 'other': 0.0, 'second.travel': 0.0} ()
    == 11. snapshot taken BEFORE a cancel, restored after it ==
        after restore: <move feed cancelled: 1.0 admitted> (<move feed active: 1.0 admitted>,) {'carriage.travel': 1.0, 'feed': 1.0, 'other': 0.0, 'second.travel': 0.0}
    == 12. determinism: the same script twice ==
        True ('cancelled', 1.0, {'carriage.travel': 1.0, 'feed': 1.0, 'other': 0.0, 'second.travel': 0.0})

Before and after, scenario by scenario, against section 2's table:

| # | before (section 2) | after (this run) |
| --- | --- | --- |
| 1 | `0.5` admitted anyway | `0` admitted, nothing moves |
| 2 | kept admitting through the cancel, `3.0` at tick 6 | `1.5` admitted at the cancel, unchanged for the remaining three ticks |
| 3 | a cancelled rate goes on accumulating, `1.2000000000000002` at tick 6 | stops at the cancel, `0.6000000000000001` (half of the pre-fix total, the three ticks before the cancel only), unchanged for the remaining three ticks |
| 4 | refused, naming the cancelled owner | accepted |
| 5 | idempotent on the status, `len(sim.commands) == 1` | idempotent, `sim.commands` is empty |
| 6 | `feed` also reaches `5.0` and reports `completed` | `feed` stands at `0`, reporting `cancelled`; `other` unchanged |
| 7 | `blocked` handle cancelled keeps `blocked` | unchanged |
| 8 | `completed` handle cancelled keeps `completed` | unchanged |
| 9 | zero-duration move unaffected by a later cancel | unchanged |
| 10 | the cancelled command is IN the snapshot and a restore resurrects it | the snapshot carries no command (`shot.commands == ()`); the restore leaves `sim.commands` empty and two further ticks move nothing |
| 11 | a snapshot before the cancel restores a fresh `active` command from the recorded progress | unchanged |
| 12 | the same script replayed twice gives the same bank, tick and handle report | unchanged |

Row 3's pre-fix planning note in section 2 read "stops at `1.2`"; the
correct post-fix value is `0.6000000000000001` — half of the pre-fix
total, because the pre-fix run's `1.2000000000000002` is what a
still-accumulating rate reaches after all SIX ticks (three before the
cancel and three after, the bug), while the fix freezes admission at the
THREE ticks before the cancel. `CancelTest.test_a_cancelled_rate_stops`
(over `Train`'s `rate('crank', 90.0)` at `dt=0.1`, three ticks before
the cancel) pins the same arithmetic: `27.0` admitted, exactly `90.0 *
0.1 * 3`, and no more after four further ticks. That planning note was a
prediction, corrected here by the actual run; it does not reflect
anything the implementation got wrong.

Rows 7, 8, 9, 11 and 12 are unchanged, as designed: they are the
behaviour the change must not alter, pinned by the spec delta's own
scenarios and by `CancelTest.test_cancel_on_a_retired_handle_does_nothing`
and `test_a_cancelled_run_replays_identically`.
