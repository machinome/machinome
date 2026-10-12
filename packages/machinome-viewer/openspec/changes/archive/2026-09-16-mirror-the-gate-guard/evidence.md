# Evidence: `mirror-the-gate-guard`

All commands run inside
`/home/asa/devel/libresolid-studio/solid-node-viewer/WTs/mirror-the-gate-guard`,
one job at a time. `solid_node_viewer/widget/node_modules` is the SYMLINK to
the primary checkout's own `node_modules`, restored by the reviewer before
this session started; it was used as is, and neither `npm install` nor
`npm ci` was run anywhere in this session.

## §0 — measured on the base (proposal time), reproduced here

All four proposal-time measurements (0.1–0.5) were re-confirmed rather than
re-derived: the base commit (`5a3e1d7`), the corpus diff against the
producer's `d3c2242`, the green replay, the four-configuration guard table,
and the 21/0 order-discrimination figures all match the numbers already
recorded in `tasks.md`'s section 0. See "The 21-disagreement figure" below
for the one place this session's own measurement (task 4) reads narrower
than that number, and why.

## Task 1 — the corpus, replaced

- **1.1** `cp` of the producer's file over the widget's copy, byte for byte.
  MD5s after the copy:

  ```text
  7b9eb6c894c3863710cdbaac68c5fe74  solid_node_viewer/widget/src/running-corpus.json
  7b9eb6c894c3863710cdbaac68c5fe74  /home/asa/devel/libresolid-studio/solid-node/WTs/pin-the-block-order/tests/running-corpus.json
  ```

  Identical. The file this cycle replaced (this worktree's base copy) hashed
  `c682b7f2c70bc7ef4f29a610ecfa8cb5`; a copy of it was kept at
  `/tmp/claude-1000/-home-asa-devel-libresolid-studio/c8863d20-2cc0-4505-b72d-32eded8aa8a3/scratchpad/stale-running-corpus.json`
  for tasks 2.4 and 4.4's scratch comparisons (never committed, never placed
  in any worktree).

- **1.2** The census assertion (`'is the framework's own fixture, unedited'`,
  19 machines / 16 unique names / 356 ticks) was NOT touched and stayed
  green: `npx vitest run src/run/running-corpus.test.ts` → 22 tests passed
  (1 census + 19 replays + 2 width-guard tests, before task 2's new
  `REQUIRED` entry).

- **1.3** Full widget suite with the new corpus in place, engine untouched:
  **36 files, 922 tests, 51.04 s** (base: 36 files, 922 tests, 51.42 s — the
  swap alone changes nothing). No file other than `running-corpus.json` was
  touched for this task, so the six other corpus-importing test files
  (`jumps.test.ts`, `program.test.ts`, `run.test.ts`, `cost.test.ts`,
  `runtime.test.ts`, `republish.test.ts`) moved nothing, as design D1
  predicted.

## Task 2 — the guard, red first

- **2.1 RED.** Appending `'an in-block gate crossing inside a tick'` to
  `REQUIRED` with no detection written:

  ```text
  FAIL  src/run/running-corpus.test.ts > the corpus's width >
        exercises every feature the producer's generator requires
  AssertionError: expected [ Array(1) ] to deeply equal []
  - []
  + [
  +   "an in-block gate crossing inside a tick",
  + ]
  ```

  Exactly the one feature, nothing else — the stated RED.

- **2.2 / 2.3 implementation.** `inBlockNames(edge, primitive, bindings,
  gives)` mirrors `_in_block_names` (`tools/generate_running_corpus.py:
  542-574`): per plan, per jump whose `primitive` matches, its `level`
  resolved transitively through the plan's own jump names and then through
  `freeNamesOf` (the guard's existing bindings closure); a jump reaching a
  block give other than `edge`'s own is a GATE (contributes the
  intersection), one reaching none is a SELECTOR (contributes the whole
  name set), one naming only `edge`'s own driven end is neither. The tick
  rule (`uncoveredFeatures`, mirroring `tools/generate_running_corpus.py:
  445-465`) is inserted directly after the existing selection-crossing
  block: for `previous !== null`, `changed` is the set of bank ids whose
  value differs from the previous tick; a crossing with `0 < t < 1` whose
  `memberOf` index is a block member (`selectors.has(index)`) counts when
  some gate name set meets `changed` and no selector name set meets
  `changed` or reaches outside `tick.bank`.

  **Unit-level check (task 2.2's own example), measured directly**: on
  `ShiftedCarry`'s higher-wheel edge (`gives: ['higher.turn']`), the two
  jumps carrying primitive `>=` are `_j2` (`level: '_b2'`, binding
  `_b2 = (shift - 0.5)`) and `_j4` (`level: '(carry.travel - 0.5)'`).
  `inBlockNames(edge, '>=', bindings, {higher.turn, carry.travel})` returns

  ```text
  gates:     [ {"carry.travel"} ]
  selectors: [ {"shift"} ]
  ```

  — the gate `{carry.travel}` and the selector reading `shift`, exactly as
  design D3's own reading of the fixture states. (Measured with
  `inBlockNames` exported for one scratch run, then reverted to
  module-local — it has no caller outside this file.)

- **2.4 GREEN.** Over the new (committed) corpus:
  `uncoveredFeatures(fixture.machines)` → `[]` — `npx vitest run
  src/run/running-corpus.test.ts` → 22/22 green.

  Over the STALE copy (the same guard function, unexported for this
  measurement, called from a temporary scratch spec file that was removed
  before this evidence was written): `uncoveredFeatures(stale.machines)` →
  `["an in-block gate crossing inside a tick"]` — the copy this cycle
  replaces still fails to supply the feature, which is what makes task 1.1
  load-bearing rather than cosmetic.

## Task 3 — the narrowed-corpus test

- **3.1** Added the assertion `expect(uncoveredFeatures(trimmed)).toContain(
  'an in-block gate crossing inside a tick')` beside the self-read's three
  and the selection's one. `Train` states no block, so it supplies no gate
  crossing (as it supplies no selection crossing already asserted).
  Measured green immediately, as the design predicted: `npx vitest run
  src/run/running-corpus.test.ts` → 22/22.

## Task 4 — the order discrimination (design D5)

- **4.1** `loadScenario(entry, forceListingOrder)` loads the document with
  `loadProgram`, and when `forceListingOrder` is true, replaces every block
  edge's `.block` (a mutable field of a `ProgramEdge`) with a stand-in whose
  `activeReads` answers `new Set()`, keeping `members` and `gives`. No line
  under `src/run/` other than `running-corpus.test.ts` changed; `grep -n
  activeReads src/run/*.ts` still shows exactly one non-test caller
  (`jumps.ts:1145`).

- **4.2 GREEN, first try.** For `ShiftedCarry` at `dt=0.05`:

  ```text
  block.gives = ['higher.turn', 'carry.travel']
  memberOf(rawEdges, 'higher.turn') = 1, memberOf(rawEdges, 'carry.travel') = 2
  ```

  Both assertions (`exact`) passed: the block's own listing IS the document's
  own published edge order, ascending, so the forced order under the
  empty-activeReads substitute is `0, 1` by `blockOrder`'s own construction
  (every member ready in round one, pushed in `remaining`'s starting order).

- **4.3 The committed test.** `bankDisagreements(entry, forceListingOrder)`
  replays the scenario's own script and compares ONLY the bank, tick by
  tick, under the corpus's own tolerance rule (`near`) — the same scope as
  the producer's own `BlockOrderTest.disagreements` in
  `tests/test_running_corpus.py:379-390`, which also compares the bank
  alone and asserts `assertTrue(patched)` (at least one), not an exact
  count. Measured:

  ```text
  bankDisagreements(ShiftedCarry, false) → []                     (unsubstituted: reproduces the corpus)
  bankDisagreements(ShiftedCarry, true)  → 19 entries, first:
    "tick 2 higher.turn: corpus 0.16666666666666669, run 0"
  ```

  The committed assertions are `toEqual([])` for the unsubstituted replay
  and `.length).toBeGreaterThan(0)` plus the literal first-entry string for
  the substituted one — mirroring the producer's own assertion shape
  (`assertFalse`/`assertTrue`, not a count).

  **The 21-disagreement figure**, recorded in `tasks.md` 0.5 and design D5
  as "21 disagreements substituted... tick 2 crossings: corpus 2, run 1...",
  was reproduced too, as a check that this session's narrower `bank`-only
  count (19) is the same underlying divergence and not a different one: a
  scratch measurement that additionally compared `engine.crossings()`
  counts per tick gave exactly 21 — the same 19 bank entries plus two
  crossings-count entries (tick 2: corpus 2 vs run 1; tick 4: corpus 0 vs
  run 1). The producer's own `BlockOrderTest.disagreements` (read at
  `tests/test_running_corpus.py:379-390`) compares the bank alone, the same
  scope this task's committed test uses, so 19 (bank only) is the number
  this test's own comparison method produces, and 21 is what task 0.5's
  broader proposal-time measurement (bank + crossings) found on the same
  divergence. Both numbers describe the identical fault; the committed test
  asserts "at least one" either way, so this is recorded as a clarification
  of an evidence figure rather than a design contradiction — the design's
  own literal assertion text (D5: "assert at least one disagreement") is
  satisfied by 19.

- **4.4 RED FIRST, against the stale corpus (scratch copy, not a commit).**
  `bankDisagreements` run against the pre-task-1.1 copy (saved at
  `/tmp/claude-1000/.../scratchpad/stale-running-corpus.json`, never
  committed):

  ```text
  bankDisagreements(stale ShiftedCarry, false) → []
  bankDisagreements(stale ShiftedCarry, true)  → []
  ```

  Zero either way — the test committed in 4.3 (`substituted.length >
  0`) would FAIL on this old fixture and PASSES on the new one, which is
  exactly the finding this cycle closes, reproduced directly against this
  engine rather than only through the width guard.

All scratch `.test.ts` files used for tasks 2.4 and 4.4's stale-copy
measurements were created outside the committed diff and deleted before
this evidence was written; `git status --short` (below) shows none of them.

## Task 5 — the suite, the types, the build

| | base (task 0.1) | after this cycle |
| --- | --- | --- |
| `npm test` | 36 files, 922 tests, 51.42 s | 36 files, **924 tests**, 49.41 s |
| `npm run typecheck` | clean | clean |
| `npm run build` | `dist/solid-widget.js` 723.9kb (741,244 bytes) | `dist/solid-widget.js` 723.9kb (741,244 bytes) |

The test count rose by exactly 2 — the two new tests of task group 4 (4.2
and 4.3); every other file's test count is unchanged, and the extra 22 vs
24 tests inside `running-corpus.test.ts` itself is +1 for 2.1's `REQUIRED`
entry (no new test, an existing assertion covering more), +1 for 3.1 (same),
+2 for the new `describe` block of task 4 = the file's own count goes
22 → 24, matching the two.

The build's byte count (741,244) is IDENTICAL to the base's, confirming no
line of `src/run/`'s engine sources or any other bundled module changed —
only a test file and a JSON fixture, neither of which `build.mjs` bundles.

- **5.2** The Python suite was NOT run. Reason, checked rather than assumed:
  `grep -rn running-corpus solid_node_viewer/ --include='*.py'` and the same
  over `pyproject.toml`, `bundle.py`, `server.py`, `capture.py` all return
  nothing; the corpus is imported only from
  `solid_node_viewer/widget/src/run/running-corpus.test.ts` (a TypeScript
  test file), so no Python module or packaged file can observe this change,
  and `scripts/check-dist` (not run — instructed off-limits this session)
  builds and smokes exactly those same untouched Python artifacts.

- **5.3** Untouched surfaces, confirmed by diff rather than assumed:

  ```text
  $ git diff -- solid_node_viewer/widget/package.json | wc -l       → 0
  $ git diff -- solid_node_viewer/widget/src/viewer.ts | wc -l      → 0
  $ git diff -- README.md | wc -l                                   → 0
  $ git diff -- docs/adrs | wc -l                                   → 0
  $ git diff --stat -- solid_node_viewer/widget/src/run/ \
      | grep -v running-corpus.test.ts                              → (no output; only that file changed)
  ```

  `package.json`'s `solidNodeViewerApi` stays `16`,
  `solidNodeDocumentVersions` stays `[1, 2, 3, 4, 5, 6, 7]` (unread, because
  untouched — confirmed by the empty diff above).

## Task 6 — the record

- **6.1** One bullet added to `CHANGELOG.md` under `0.2.0 — unreleased`, at
  the top of that section (the file's own convention: newest entry first),
  naming the corpus refresh, the width guard's new feature, and the new
  direct order-discrimination test; no `README.md` change.
- **6.2** This file.
- **6.3** `openspec validate mirror-the-gate-guard --strict` — see the final
  report for the result; the archive is left for the reviewer, as the
  previous cycles left it.

## `git status --short` at the end of implementation

```text
 M CHANGELOG.md
 M openspec/changes/mirror-the-gate-guard/tasks.md
?? openspec/changes/mirror-the-gate-guard/evidence.md
 M solid_node_viewer/widget/src/run/running-corpus.test.ts
 M solid_node_viewer/widget/src/running-corpus.json
```

No other file in the worktree changed. No commit, stage, or archive was
made; those are left for the reviewer as instructed.

## Deviations from the design

None that change behaviour. The one clarification recorded is the
21-vs-19 disagreement count under task 4.3 above: the design's own literal
assertion ("assert at least one disagreement") and the producer's own
`BlockOrderTest` (bank-only comparison, `assertTrue`, no count) are both
satisfied by the 19 measured here; the 21 figure was independently
reproduced as the same fault under a wider (bank + crossings) comparison,
for the reviewer's own cross-check.

## Follow-ups (out of scope, not fixed here)

- The two `REQUIRED` lists (this file's and the producer's
  `tools/generate_running_corpus.py`) live in two repositories and can
  drift apart silently — unchanged by this cycle, and already named as a
  standing risk in the design.
- `memberOf`'s indexing over ALL published edges (checks included) versus
  `selectionOf`'s filtered indexing is a latent mismatch this cycle keeps
  deliberately (design D3): no scenario in either corpus publishes a
  `check` edge, so it is not live here, but a future corpus that does would
  need this reconciled.
