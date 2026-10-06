## Why

The running conformance corpus can leave out a crossing or a stop that the
run it records actually made. `workflow/warts.md`, "Corpus record cursor
across restore (2026-09-20)", met while validating the Curta
(`projects/Calculators/Curta-Type-I-3x`):

> `tools/generate_running_corpus.py::run_machine` and the matching test
> replay helper retain their record-list cursors across a scripted
> `restore`, while the real run clears its record rings. If the same script
> step immediately creates a new stop, the old cursor can omit it from that
> step's corpus record. Direct runtime snapshot tests still compare the
> actual stop correctly.
>
> The periodic-contact corpus restores on its own recorded step before the
> next request, so both stops are present. No general corpus cursor repair
> is included in that cycle. A future repair should be red-first for
> restore plus an immediate same-step stop, and check crossings as well as
> stops; it should not change machine state or command semantics to repair
> evidence collection.

The generator records a step's crossings and stops as the slice of
`sim.crossings` and `sim.stops` past two counters, `crossings_seen` and
`stops_seen`, which it sets to the rings' lengths after each step.
`Run.restore` (`machinome/simulation/run.py:1633-1636`) clears both rings.
The counters keep their old values. When the step that restores also
creates a crossing or a stop before its tick ends, the slice starts past
it, so the record omits it. The suite's replay,
`CorpusReplayTest.replay` (`tests/test_running_corpus.py:66-91`), counts
the same way. It therefore agrees with the generator's omission, and
cannot catch it. The time-drive generator
(`tools/generate_time_drive_corpus.py:79-82`) already starts its counters
again after a restore or a reset. The running generator and its replay are
the two places that do not.

**Reproduced on the bench `fix-warts-3` at `298ca6b`**, with a scratch
script that runs the generator's own `run_machine` on the corpus machine
`StopAndJump` (a `wrap` crossing and a stop in one tick). The script takes a
snapshot and moves `crank` by 30 over one tick in step 1. In step 2 it
restores the snapshot and repeats the same move. The restore puts the
clock back to tick 0, so step 2 replays step 1 exactly:

```
step 1 record: tick 1 crossings 1 stops 1
step 2 record: tick 1 crossings 0 stops 0
after step 2 the run holds: sim.crossings 1 [(1, 'folder.turn', 'ceil', 1.0, 0.16666666666666666)]
                            sim.stops     1 [(1, 'first.turn', 'high', 145.0, 0.5, ('crank',))]
banks equal: True
step 2 record equals step 1 record: False
```

Both banks are equal, and the run holds the crossing and the stop of the
replayed tick. The generator's record of that tick has neither. The
replay helper accepts that empty record, and it refuses the honest one
with `0 != 1 : StopAndJump tick 1` (design.md, Context).

The committed corpora are not affected today. Regenerated into the
scratchpad with the counters started again after a restore,
`tests/running-corpus.json` has every tick's bank, crossings, stops and
commands identical to an unchanged regeneration. No step of its 28
scenarios restores and makes a record in the same step. The clocked corpus
records each request's own result and keeps no counter. The time-drive
corpus already counts correctly.

## What Changes

- **The generator counts from the cleared record after a restore.** In
  `tools/generate_running_corpus.py::run_machine`, a script action that
  restores sets `crossings_seen` and `stops_seen` to `0`, the length of
  the rings `Run.restore` has just cleared. This is what
  `tools/generate_time_drive_corpus.py` already does. A step's record
  therefore holds every crossing and stop the run made from the end of the
  previous step to the end of this step's tick. That includes those made by
  the step's own script, such as a move with no duration, which settles at
  the current tick before the tick runs. Records made before a restore in
  the same step are cleared by the run, and the corpus does not invent
  them.
- **The suite's replay counts the same way.** `CorpusReplayTest.replay`
  in `tests/test_running_corpus.py` gets the same two lines, so it
  reproduces the honest record and refuses an entry that omits one.
- **Two red tests**, in `CorpusReplayTest`, on the `StopAndJump` script
  above. One is for the generator: the restored step's record equals the
  first step's, and both carry a crossing and a stop. The other is for the
  replay: it accepts an entry whose two steps are both the honest record,
  and it refuses the same entry with the second step's crossing and stop
  removed.
- **Records:** a changelog bullet under `Unreleased`. The warts entry
  moves to the campaign's `resolved.md`.

**Deliberately out**, with the reason:

- **The committed corpora are not regenerated.** The change alters no
  record of `tests/running-corpus.json`, `tests/clocked-corpus.json` or
  `tests/time-drive-corpus.json`. A regeneration would also rewrite values
  that are not this change's. The committed documents are versions 5 to 10,
  kept as controls (`tests/source_timing_compatibility.py`), and the bench
  now publishes version 11. Two scenarios, `ShiftedCarry` and
  `RangedBlock`, also differ from the committed file within the corpus's
  `1e-9` relative tolerance, by at most `5.5e-13`. Regenerating is
  therefore refused by this cycle's brief, and is not needed.
- **No new corpus scenario.** A scenario that restores and stops in one
  step would put this case in the file the viewer replays. It would also
  require a regeneration that rewrites existing values (above), and it is
  coverage the viewer must then implement. design.md Open Question 1 gives
  the recommendation: not in this change.
- **The viewer's replay.** `machinome-viewer`'s
  `machinome_viewer/widget/src/run/running-corpus.test.ts` keeps the same
  two counters across a restore, and its `Run.restore` clears its rings
  too. That is the viewer repository's change, and nothing is written
  there. With the corpus unchanged, its replay still passes.
- **The run is not changed.** `Run.restore` keeps clearing its rings, and
  no machine state or command semantics move. The finding is in evidence
  collection only, as the warts entry requires.
- **Selecting records by their `tick` field** is rejected. A move with no
  duration records at the tick before the step's own tick, and the corpus
  reports it in the step that follows. Filtering by tick would drop the
  `PeriodicStop` scenario's stops from the step they are recorded in.
  design.md, Decision 1, Alternatives, gives the evidence.
- **The rings' bound.** `record=N` bounds each of the crossing and stop
  rings to N entries, not N ticks. The generator's counter cannot advance
  past a full ring. No committed scenario comes near it: the largest fill
  is 3 entries in a ring of 9. The bound is recorded as a finding for the
  warts log, not repaired here (design.md, Open Question 2).
- **Projects.** The Curta is not run. The proof is in the framework's own
  tools and tests.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `export`: the requirement "The two runtimes share a conformance corpus"
  is modified. One paragraph is added: a tick's crossings and stops are
  every record the run made since the previous step, and after a restore
  the step counts from the cleared record, in the generator and the replay
  alike. One scenario is added, "A stop made in the step that restores is
  recorded". Every existing scenario is carried unchanged.

## Impact

- **Code:** `tools/generate_running_corpus.py`, `run_machine`
  (`:370-405`): two lines in the action loop. No other function changes,
  and `apply_action`, which `tools/generate_time_drive_corpus.py` imports,
  is untouched.
- **Tests:** `tests/test_running_corpus.py`, `CorpusReplayTest.replay`
  (`:66-91`): the same two lines. Two tests are added to
  `CorpusReplayTest`.
- **Corpora:** `tests/running-corpus.json`, `tests/clocked-corpus.json`
  and `tests/time-drive-corpus.json` are byte-identical. The viewer's
  committed copy needs no change.
- **Documents, identities, the run, projects:** unchanged.
- **Manual:** `docs/reference/api.rst` "The conformance corpus" and
  `docs/architecture.md` describe each tick's crossings and stops without
  saying how they are counted, and stay correct. The changelog gets one
  bullet.

## Authorization

The pilot's mandate of 6 October 2026 for the fix-warts-3 campaign
(`workflow/ongoing/fix-warts-3.md`, "Mandate"): "work on the items you can
autonomously, orchestrating opus subagents and using empirical evidence
from projects to validate, other than your adversarial review. if
something needs my input, record and defer, you'll go unsupervised." This
change is the campaign table's cycle 7, `keep-the-corpus-cursor-honest`.
The finding was met in Curta-Type-I-3x, and is proved in the framework's
own corpus tools and tests. design.md's two Open Questions each carry a
recommendation, and neither blocks the fix.
