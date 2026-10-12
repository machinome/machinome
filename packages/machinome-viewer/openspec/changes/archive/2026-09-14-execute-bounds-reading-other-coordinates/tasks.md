## 0. Before anything else

- [x] 0.1 Confirm the base: this worktree is `bounds-read-other-coordinates`
      off viewer main `1aefbc0`, package `0.2.0` unreleased, declared API
      version `12`, `documentVersions == [1, 2, 3, 4, 5]`. None of the
      three moves in this cycle.
- [x] 0.2 Record the baseline in
      `openspec/changes/execute-bounds-reading-other-coordinates/evidence.md`,
      measured on this base and pasted verbatim: in
      `solid_node_viewer/widget`, `npm run typecheck` clean, `npm test`
      → **732 passed**, `npm run build` writes `dist/solid-widget.js`;
      the Python suite with the workspace venv
      (`PYTHONPATH=<worktree> .venv/bin/python -m pytest`) with its
      count and everything it skips named. Never `npm ci` or
      `npm install` here — `node_modules` is a symlink to the main
      checkout's.
- [x] 0.3 Read, and keep open, the framework's own record in
      `solid-node/WTs/bounds-read-other-coordinates`:
      `docs/adrs/NODE/ADR-113-a-bound-may-read-other-coordinates.md`;
      `openspec/changes/archive/2026-09-14-bounds-read-other-coordinates/design.md`
      decisions 3–5, 7, 8, 9 and 11; `openspec/specs/simulation/spec.md`
      "A declared range is a physical stop located inside the tick";
      and the implementation this cycle mirrors —
      `solid_node/simulation/run.py` (`_reached`, `_constraint_reached`,
      `_searched_constraint`, `_constraint_level`, `_constraint_bound`,
      `_assert_inside`, `_constraint_group`, `_bounds`, and the commit
      path in `integrate`) and `solid_node/simulation/program.py`
      (`Constraint`, `Program._constraint_table`, `Program._sub_program`).
      Where this cycle and ADR-113 disagree, ADR-113 is right.
- [x] 0.4 Confirm the refusal this cycle removes is real, and paste it
      into evidence: load
      `projects/Locks/Pin_tumbler_lock/_build/viewer.json` through
      `loadProgram` on this base and capture the message naming
      `plug.key.insert` and `plug.turn`.

## 1. The corpus, red first

- [x] 1.1 Replace `solid_node_viewer/widget/src/running-corpus.json` with
      `solid-node/WTs/bounds-read-other-coordinates/tests/running-corpus.json`,
      **byte for byte** — 14 scenarios over 12 machines, 276 ticks,
      tolerance `{"float": 1e-9}`, the new machine `Captured` at
      `dt = 0.05` over 16 ticks. Verify with a digest of both files and
      paste it. Nothing here edits it and nothing here regenerates it.
- [x] 1.2 Red: `npm test -- running-corpus` fails on `Captured` and on
      nothing else. Paste the failure verbatim — it is the shape of the
      whole cycle, and a failure anywhere but `Captured` means the copy
      was not byte-identical.
- [x] 1.3 Widen the width guard in `src/run/running-corpus.test.ts` to
      the producer's list (design D7): add
      `'a bound reading another coordinate'` and `'a stop reached by the
      motion of what a bound reads'` to `REQUIRED`, and compute both the
      way `tools/generate_running_corpus.py:285-331` does — the first
      over a span side whose free names, CLOSED OVER THE FIXTURE'S OWN
      BINDINGS, hold a bank id other than the span's key; the second
      over a recorded stop whose coordinate holds the same value in the
      previous tick's bank (or in the published `initial`, on tick one)
      as in its own. Extend the "narrowed corpus is refused" case to
      name one of the two.

## 2. Reading the bound (`src/run/program.ts`, design D1–D3)

- [x] 2.1 Red, in `src/run/program.test.ts`: a hand-written version 5
      document whose span expression names a second bank coordinate
      loads today's refusal; a second whose span reaches its read ONLY
      through the bindings table does too. Both must load once 2.2 and
      2.3 land.
- [x] 2.2 Widen the span free-name check: allowed becomes the bounded
      coordinate's id together with every key of `program.coordinates`.
      Keep the refusal for everything else, and give it the message of
      design D3 — the offending name, whether the document publishes it
      as a COMPUTED VALUE (with "a bound reads the state — read the
      joint the port follows"), what such a bound may read, the
      expression quoted and the document named. Red-first tests: a bound
      naming an intermediate; a bound naming the clock; a bound naming
      an unknown id; a bound naming a plan placeholder.
- [x] 2.3 Derive the constraint table in `loadProgram` and publish it on
      `LoadedProgram` as `constraints: ReadonlyMap<string, Constraint>`
      keyed `` `${identifier}:${side}` ``, each entry
      `{ identifier, side, expression, reads, edges, candidates }`:
      - `reads` = the bindings closure of the expression's free names
        minus the own id, SORTED (design D2);
      - `edges` = `Program._sub_program` reproduced: walk
        `program.edges` in reverse, skip `check` edges, keep any edge
        giving a needed key and add its `needs`, reverse the result;
      - `candidates` = the sorted union of `program.sources` over the
        bounded coordinate and every read.
      A side that is `null`, a number, or an expression naming the own
      id alone produces NO entry.
- [x] 2.4 Tests for 2.3: a bound whose reads arrive only through
      bindings has those coordinates as reads; a bound never naming its
      own coordinate is well formed; the sub-program holds exactly the
      determining edges in published order and never a `check`; the
      candidates are the union of the reaching-input lists; a self-only
      bound and a numeric bound make no entry at all.

## 3. Executing the bound (`src/run/run.ts`, design D4–D6)

- [x] 3.1 `boundsNow()` returns `number | null | Constraint` per side —
      `run.py:1087`'s `_bounds`, which substitutes the compiled
      constraint for that side. Widen `Reached` to
      `[identifier, side, number | Constraint, number | null]` and make
      `eventOf` use a fraction already located instead of calling
      `locate` for it.
- [x] 3.2 Red, then write `constraintLevel` (`_constraint_level`,
      `run.py:793`): a FRESH delta map from the admissions scaled by
      `t`, one `edgeIncrements(program, edge, values, deltas, null, 0)`
      per sub-program edge written back into it, the scope the own id at
      `this.bank[identifier]` plus `held[read] + deltas[read]` per read,
      and the level `value − bound` for a high side, `bound − value` for
      a low one. Test it directly: the level at `t = 0` and `t = 1` of a
      hand-built bench, and a law that jumps inside a sub-program taking
      its plan over the truncated path.
- [x] 3.3 `constraintBound` (`_constraint_bound`) — the bound evaluated
      at the committed state with the own coordinate still at
      `this.bank` — and `assertInside` (`_assert_inside`), throwing
      `StopInvariantError` with a message naming the coordinate, the
      side, the bound, the value and the amount outside.
- [x] 3.4 `constraintReached` (`_constraint_reached`) and
      `searchedConstraint` (`_searched_constraint`): examined only when
      the bounded coordinate or a read has a nonzero increment;
      `outward(h) = h > 0 && h > level(0)`; samples `k/subdivisions` for
      `k = 1 … subdivisions`; the first outward sample brackets against
      `k − 1`; bisect while `high − low > crossingTolerance` for at most
      `bisectionRounds` rounds; return the INSIDE end, `low`. A level
      already positive at the start with a higher first sample returns
      `0`.
- [x] 3.5 `reachedBounds` reproduces `_reached` (`run.py:674`) branch
      for branch: no read moving and the coordinate standing → nothing;
      no read moving and the coordinate moving → the NUMBER from the
      expression at the tick's committed own value and the reads'
      start-of-stretch values, pushed as an ordinary numeric entry that
      takes the existing solve/search/snap path; a read moving →
      `constraintReached`, pushed with the constraint and its fraction;
      and the plain numeric comparison afterwards with a constraint side
      treated as `null`, so no side is judged twice.
- [x] 3.6 `constraintGroup` (`_constraint_group`): over the
      constraint's candidates with a nonzero admission, that admission
      ALONE, `level(1) − level(0) > 0`. `held` is the stretch's start
      bank and the admissions are the stretch's `scaled`, not the
      segment's.
- [x] 3.7 The commit path in `step`: for a constraint entry, NO snap;
      the record's `value` is `constraintBound` at the committed state;
      the group is `constraintGroup`. Then, in a SECOND loop over the
      event — after every entry's group and record — `assertInside` for
      each constraint entry, because a numeric snap on another entry of
      the same event mutates `committed` (design D6,
      `run.py:583-585`). Give this its own test: one event carrying a
      numeric stop and a constraint stop within the crossing tolerance
      of each other.

## 4. The framework's own numbers, mirrored (`src/run/run.test.ts`)

Each of these is a `bench()` document reproducing the framework fixture
in `solid-node/WTs/bounds-read-other-coordinates/tests/running_project/machine.py`,
and each number is that repository's `tests/test_running_stops.py`.

- [x] 4.1 The `Gate` bench: inputs `feed` (rest `10`) and `twist` (rest
      `0`); `feed → key.travel` ratio 1; `key.travel → p1.lift` and
      `→ p2.lift` by `(5 - (5 * min(max(((key.travel - k) / 5), 0.0),
      1.0)))` for `k = 10` and `13`, `affine: false`; `twist →
      plug.turn` ratio 1; `plug.turn` span `low: 0`, `high:
      {"expression": "((90 * (abs(p1.lift) <= 0.05)) * (abs(p2.lift) <=
      0.05))"}`. `dt = 0.1`.
- [x] 4.2 The plug blocked while a pin crosses (the STATIC-READS path,
      one evaluation, the existing snap): `move('twist', by 30,
      duration 0.1)` from rest → `plug.turn` and `twist` exactly `0`,
      status `blocked`, admitted `0`, one stop
      `('plug.turn', 'high', 0.0, 0.0, ['twist'])`.
- [x] 4.3 The plug turns once every pin clears: `feed` to `20` over
      `0.4` completes with no stop; then `twist` by `30` completes with
      `30` admitted, `plug.turn == 30` to 1e-9, and no stop.
- [x] 4.4 Insertion and turning in one tick: `feed` by `10` and `twist`
      by `30` in the same tick → `key.travel == 20`, `plug.turn == 0`,
      feed `completed` with `10`, turn `blocked` with `0`; the same turn
      requested on the next tick completes at `30`.
- [x] 4.5 Withdrawing from a turned plug (the SAMPLED path, and a stop
      on a coordinate that does not move): seat to `20`, turn by `30`,
      then `feed` by `-5` over `0.1` → `plug.turn` exactly `30`;
      `key.travel` in `[17.95, 17.95 + 5.0e-11]`; `blocked` with
      `admitted == key.travel - 20`; one stop
      `('plug.turn', 'high', 90.0, t, ['feed'])` with `t ≈ 0.41` to
      1e-9. The evaluated bound is `90`, NOT the `30` the coordinate
      holds.
- [x] 4.6 The same travel at any cadence: the same withdrawal in 1, 4
      and 40 ticks agrees on the final travel and the admitted travel to
      1e-9, all three `blocked`.
- [x] 4.7 A constraint stop replays identically from a snapshot taken
      before it: same travel, same admitted, same stop record.
- [x] 4.8 The `Captured` bench — `Gate` resting seated (`feed` rest
      `20`) with the capture stated on the key's own travel,
      `key.travel` span `low: {"expression": "(20 * (plug.turn > 0))"}`,
      `high: 20`. Turn by `30`, then `feed` by `-5` → `key.travel`
      exactly `20`, `blocked` with `0` admitted, one stop
      `('key.travel', 'low', 20.0, 0.0, ['feed'])`.
- [x] 4.9 Returning the plug and withdrawing in one tick: `twist` by
      `-30` and `feed` by `-5` together → `plug.turn == 0` to 1e-9 and
      `completed`; `key.travel == 20` and `blocked` with `0`; the same
      withdrawal on the next tick completes at `15`.
- [x] 4.10 The `PawlRatchet` bench — inputs `arbor` (rest `40`) and
      `hoist` (rest `0`), both ratio 1 into `wheel.turn` and
      `pawl.lift`; `wheel.turn` span `low: {"expression": "((36 *
      floor((wheel.turn / 36))) - (1000 * (pawl.lift >= 1)))"}`,
      `high: null`. A pawl reaching `1` at `0.3` of the tick (`hoist` by
      `10/3`) releases the reverse: `wheel.turn == 30`, `arbor`
      `completed` with `-10`, no stop. A pawl reaching `1` at `0.5`
      (`hoist` by `2.0`) does not: `wheel.turn == 36.0` to 9 places,
      `arbor` `blocked` with `-4.0` to 9 places, one stop
      `('wheel.turn', 'low', 36.0, 0.4, …)` with `t == 0.4` to 9 places.
      This is the pair that proves the own coordinate is read COMMITTED
      and the reads along the path.
- [x] 4.11 A quiet bound costs nothing: a tick moving nothing a
      constraint depends on takes no sample — asserted by counting
      evaluations, not by timing — and a coordinate left standing
      outside stays free.

## 5. The corpus, green

- [x] 5.1 `npm test -- running-corpus` passes: all 14 scenarios, 276
      ticks, exactly for discrete state and within `1e-9` relative for
      floats. Paste the count.
- [x] 5.2 The width guard passes on the new corpus and fails on a
      narrowed copy naming one of the two new features.

## 6. The whole suite, and the build

- [x] 6.1 `npm run typecheck` clean, `npm test` green with its new
      count, `npm run build` writes `dist/solid-widget.js`. Paste all
      three.
- [x] 6.2 The Python suite green with the rebuilt bundle, naming every
      skip. Paste it.
- [x] 6.3 `acceptance.test.ts` — the Pascaline module — is unchanged to
      the digit: `tens.drum.turn` still `65.54` after ten `Add one`.
      A self-only bound's meaning, path and cost do not move.

## 7. The lock, in a real browser (design D8)

- [x] 7.1 Commit `tests/fixtures/lock/viewer.json`:
      `projects/Locks/Pin_tumbler_lock/_build/viewer.json`, **verbatim**
      — version 5, program identity beginning `b45402a5`, drivers
      `insertion` (mm, `[-60, 0]`) and `rotation` (deg, `[-90, 90]`),
      six instructions, sixteen coordinates, fourteen edges,
      twenty-three bindings, eleven flexible pieces, spans reading
      `plug.p1.lift … plug.p5.lift` on `plug.turn` (through `_b10`,
      `_b13`, `_b16`, `_b19`, `_b22`) and `plug.turn` on
      `plug.key.insert`. Record its byte count.
- [x] 7.2 Commit the fifteen stand-in meshes the document names, each a
      copy of the 684-byte unit cube `tests/fixtures/pascaline/vendor/`
      already carries, and write `tests/fixtures/lock/README.md` in that
      fixture's voice, saying exactly what is verbatim and what is a
      stand-in. Add `LOCK = FIXTURES / 'lock'` to `tests/support.py` and
      a plain test that every model path resolves, so a missing mesh
      fails as a missing mesh.
- [x] 7.3 A vitest case loading the lock fixture through `Engine.load`:
      it does not throw; the derived constraint table has two entries;
      `plug.turn:high` reads the five pin lifts IN SORTED ORDER with
      seven sub-program edges and both inputs as candidates;
      `plug.key.insert:low` reads `plug.turn`. This is the guard against
      a wrong closure (design, risk 2), because the corpus's `Captured`
      machine carries no bindings at all and cannot catch it.
- [x] 7.4 The browser acceptance, beside
      `tests/test_running_document.py`'s and in its shape
      (`needs_playwright`, `needs_bundle`, `serve_directory`,
      `page.evaluate` over the mounted handle), driving the machine by
      its OWN declared instructions and asserting the mechanism:
      - the document MOUNTS — no refusal, a run exists, no step taken,
        the bank at the published rest values with `plug.turn == 0` and
        `plug.key.insert == 0`;
      - the key seated (the rest pose), `Turn the plug` completes and
        `plug.turn` reaches `90`;
      - with the plug turned, `Withdraw the key` retires `blocked` with
        `0` admitted, `plug.key.insert` stands at `0`, and the stop
        names `plug.key.insert`, `low`, the evaluated bound `0`, the
        fraction `0` and `insertion` — the CAPTURE;
      - `Return the plug` completes at `0`, and `Withdraw the key` then
        completes at `-60`;
      - with the key withdrawn, `Turn the plug` retires `blocked` with
        `0` admitted, `plug.turn` stands at `0`, and the stop names
        `plug.turn`, `high`, `0`, `0` and `rotation`.
      Verify each number against the lock project's own suite before
      asserting it, and paste the measured banks into evidence rather
      than only the assertions.
- [x] 7.5 Two inspected screenshots written to `tests/_shots/`, as the
      Pascaline acceptance writes its own: the plug turned with the key
      seated, and the key stopped by the turned plug. Pixels are
      evidence.

## 8. What it costs (design D9)

- [x] 8.1 Extend `src/run/cost.test.ts` with three printed measurements,
      each floored an order of magnitude below the bench, as that file
      already does: the corpus's `Captured` machine through its blocking
      ticks; the lock fixture idle at its rest bank; and the lock
      fixture advancing the key, where five bounds sample over a
      seven-edge sub-program.
- [x] 8.2 Assert the other way too: `Train`'s existing measurement does
      not move. A machine declaring no such bound pays nothing.
- [x] 8.3 Record all three in evidence beside the framework's own
      numbers (ADR-113: `Gate` 0.36 ms quiet / 5.4 ms active / 3.3 ms
      blocking; the lock 2.9 ms idle / 4.7 ms turning / 45 ms advancing
      the key) and state whether the lock advances its key at the
      default step size of `1/240 s`. A shortfall is REPORTED to the
      pilot as a finding — never mended by widening a tolerance,
      coarsening the step size or skipping a sample.

## 9. The record

- [x] 9.1 `CHANGELOG.md`, a new bullet under `0.2.0 — unreleased`: the
      worker executes a bound that reads other coordinates; the pin
      tumbler lock's own published document mounts and runs; the corpus
      is the producer's regenerated one (14 scenarios, 276 ticks); no
      document version and no API version moves.
- [x] 9.2 `README.md` only where a statement actually changes. Check the
      run and conformance paragraphs and change nothing else.
- [x] 9.3 `docs/adrs/EXPORT/ADR-054-<slug>.md`, extracted AFTER
      implementation from what was decided and measured: a constraint is
      derived from the published document and never published, the reads
      are the bindings closure, the worker reproduces ADR-113 function
      for function, and the corpus is what holds it there. Cites
      ADR-045, ADR-047, ADR-043 and the framework's ADR-113. Update
      `docs/adrs/README.md` in its chronological order.
- [ ] 9.4 `openspec validate execute-bounds-reading-other-coordinates
      --strict` clean, the delta specs synchronized into
      `openspec/specs/viewer-package/spec.md`, and the change archived as
      `openspec/changes/archive/<date>-execute-bounds-reading-other-coordinates`
      with its evidence.
