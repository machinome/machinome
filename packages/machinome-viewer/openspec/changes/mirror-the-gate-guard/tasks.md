## 0. Before anything else — measured on the base, at proposal time

- [x] 0.1 The base, recorded. Worktree
      `solid-node-viewer/WTs/mirror-the-gate-guard`, branch
      `mirror-the-gate-guard`, base `5a3e1d7` (package `0.2.0`
      unreleased, `solidNodeViewerApi: 16`,
      `solidNodeDocumentVersions: [1, 2, 3, 4, 5, 6, 7]`, highest ADR 058
      in `docs/adrs/EXPORT`). Measured in that worktree, one job at a
      time:

      ```text
      $ npm test          →  Test Files  36 passed (36)
                             Tests  922 passed (922)      51.42 s
      $ npm run typecheck →  clean (tsc --noEmit, exit 0)
      $ npm run build     →  dist/solid-widget.js  723.9kb  (741,244 bytes)
      ```

      **Environment note for the applier:**
      `solid_node_viewer/widget/node_modules` is a SYMLINK to the primary
      checkout's, and at proposal time the primary's directory is EMPTY —
      nothing can run through it. Never `npm install` or `npm ci` here.
      The proposal's measurements were taken with that symlink replaced,
      in this worktree only, by a directory of symlinks to each package
      of `WTs/execute-the-selection`'s own `node_modules` (a real
      directory), so nothing was written into any other worktree; the
      original symlink was restored afterwards. Restore or re-point it
      the same way before running the suite, and report the state of the
      primary's `node_modules` rather than repairing it.
- [x] 0.2 The corpus gap, measured against the framework's file at
      `d3c2242` (`/home/asa/devel/libresolid-studio/solid-node/WTs/pin-the-block-order`,
      read-only) before anything is written. Both files: 19 scenarios, 16
      machines, 356 ticks; `generated_by`, `corpus` and `tolerance`
      equal; scenario keys `(name, dt, steps)` equal and in the same
      order. Added none, removed none, **changed exactly
      `('ShiftedCarry', 0.05, 20)`**: its script's two cranks run over
      `0.3 s` instead of `0.2 s` and 10 of its 20 ticks moved; its
      `document` is byte-identical, key order included, still
      `version: 7`. Tick 2 commits `higher.turn 0.16666666666666669`
      against the stale `0.5`, with 2 crossings against none.
- [x] 0.3 The framework's file replayed through the shipped engine on the
      base: **all 19 scenarios green**, the new `ShiftedCarry` entry
      included. And the WHOLE widget suite with that file in place:
      36 files, 922 tests, 51.02 s — so the corpus swap alone is green
      and the RED of this cycle is the guard, not the replay.
- [x] 0.4 The width guard, measured in all four configurations
      (`REQUIRED` with the producer's new entry appended):

      | corpus | detection absent | detection mirrored |
      | --- | --- | --- |
      | the producer's at `d3c2242` | `['an in-block gate crossing inside a tick']` | `[]` |
      | this viewer's committed copy | same one uncovered | **same one uncovered** |

      `ShiftedCarry` is the ONLY machine of the 19 that supplies the
      feature, and the corpus trimmed to `Train` still names it.
- [x] 0.5 The order discrimination, measured through `Engine` with a
      substitute `ProgramBlock` whose `activeReads` answers the empty
      set (design D5): `ShiftedCarry` at `d3c2242` gives **21
      disagreements** under the forced listing order and **0** without
      it; the stale copy gives **0 either way**; `RangedBlock` gives its
      one crossing-count disagreement either way. First three
      disagreements on the new entry:

      ```text
      tick 2 higher.turn: corpus 0.16666666666666669, run 0
      tick 2 crossings:   corpus 2, run 1
      tick 3 higher.turn: corpus 0.5, run 0.33333333333333337
      ```

## 1. The corpus, replaced

- [ ] 1.1 Copy the framework's `tests/running-corpus.json` at `d3c2242`
      over `solid_node_viewer/widget/src/running-corpus.json`, BYTE FOR
      BYTE (`cp`, never an edit). Record the md5 of both files in
      `evidence.md`.
- [ ] 1.2 Confirm the census assertion in `run/running-corpus.test.ts`
      does NOT move: 19 scenarios, 16 unique machines, 356 ticks. It is
      already what the file says; assert it is still green without
      touching the line.
- [ ] 1.3 Run the suite and record that every one of the 19 replays is
      green and that no other test file moved — six other files import
      the corpus and read only its byte-identical documents.

## 2. The guard, red first

- [ ] 2.1 RED: add `'an in-block gate crossing inside a tick'` to
      `REQUIRED` in `run/running-corpus.test.ts`, after `'a tick carrying
      both a selection crossing and a stop'` — the producer's own
      position and spelling (`tools/generate_running_corpus.py:104`).
      The width test must FAIL, naming exactly that feature, before any
      detection is written. Record the failure text.
- [ ] 2.2 Mirror `_in_block_names`
      (`tools/generate_running_corpus.py:542-574`) as `inBlockNames`
      beside `selectionOf`: the member's jumps carrying the crossing's
      primitive, each jump's `level` resolved transitively through the
      plan's own jump names and closed over the document's bindings with
      the guard's existing `freeNamesOf`; a jump whose names reach a
      block give other than the member's own is a GATE and contributes
      that INTERSECTION, one whose names reach no block give at all is a
      SELECTOR and contributes its WHOLE name set, and one naming only
      the member's own driven end is neither. Unit-level check against
      the producer's own reading of `ShiftedCarry`: the higher wheel's
      `>=` jumps split into the gate `{carry.travel}` and the selector
      reading `shift`.
- [ ] 2.3 Mirror the tick rule
      (`tools/generate_running_corpus.py:445-465`) in
      `uncoveredFeatures`: skip the first tick of every scenario; take
      `changed` as the bank ids whose value differs from the previous
      tick's; for each crossing with `0 < t < 1` under a coordinate whose
      `memberOf` index is in the `selectionOf` map, count it when some
      gate set meets `changed` and no selector set meets `changed` or
      reaches outside the tick's bank. Through the corpus's documents and
      tick logs ONLY — never through `loadProgram`, for the reason the
      file already states.
- [ ] 2.4 GREEN over the new corpus (`[]`), and record that the same
      guard over the STALE copy still names the feature — that is what
      makes task 1.1 load-bearing rather than cosmetic.

## 3. The narrowed-corpus test

- [ ] 3.1 Add the new feature to the assertions of `'is refused when the
      corpus is narrowed'`, beside the self-read's three and the
      selection's one: `Train` states no block, so it supplies no gate
      crossing. Measured green at proposal time.

## 4. The order discrimination (design D5), mirroring `BlockOrderTest`

- [ ] 4.1 A helper in `run/running-corpus.test.ts` that loads a
      scenario's document with `loadProgram`, replaces each block edge's
      `block` with `{ members, gives, activeReads: () => new Set() }`,
      and builds the engine with `new Engine(program, dt, steps + 1)`.
      Nothing in `src/run/`'s engine source changes: `activeReads` has
      exactly one non-test caller (`jumps.ts:1145`) and the suite already
      substitutes a block this way (`jumps.test.ts:1079-1091`).
- [ ] 4.2 Assert that the substitution really forces the PUBLISHED
      LISTING order: the block's members are `['higher.turn',
      'carry.travel']` in the order those edges are published, and the
      forced order is `0, 1`. This is what keeps the test honest if the
      engine's ordering is ever cached or rewritten.
- [ ] 4.3 The test itself, in the producer's own two halves: replay
      `ShiftedCarry`'s corpus entry — its script, its `dt`, its 20 steps
      — UNSUBSTITUTED and assert ZERO disagreements against every
      committed tick's bank under the corpus's own tolerance rule; then
      replay it SUBSTITUTED and assert at least one. The first half is
      what stops the second from passing by breaking the fixture.
      Expected: 21 disagreements substituted, the first being `tick 2
      higher.turn: corpus 0.16666666666666669, run 0`.
- [ ] 4.4 RED FIRST for this test as it will be met by a future
      regression: run 4.3 against the STALE corpus (a scratch copy, not a
      commit) and record that the substituted replay gives ZERO
      disagreements there — the test fails on the old fixture and passes
      on the new one, which is exactly the finding this cycle closes.

## 5. The suite, the types and the build

- [ ] 5.1 `npm test`, `npm run typecheck`, `npm run build` — against the
      base numbers of task 0.1, with the new totals recorded. Expect the
      test count to rise by the new ordering test(s) only.
- [ ] 5.2 The Python suite is NOT run, and the reason is recorded:
      the corpus is a widget test fixture imported only by TypeScript
      test files, no `src/` module imports it so it is not in
      `dist/solid-widget.js`, and no Python module or packaged file
      references it — `bundle.py`, `server.py` and `capture.py` cannot
      observe this change. `scripts/check-dist` likewise unaffected.
      If the reviewer wants it anyway, say so rather than skipping
      silently.
- [ ] 5.3 Confirm the untouched surfaces by diff: `package.json`
      (`solidNodeViewerApi` 16, `solidNodeDocumentVersions` `[1..7]`),
      `viewer.ts`'s `RENDERED_VERSIONS`, `README.md`, `docs/adrs/`, and
      every file under `src/run/` other than `running-corpus.test.ts`.

## 6. The record

- [ ] 6.1 `CHANGELOG.md` under `0.2.0 — unreleased`: ONE bullet — the
      conformance corpus refreshed to the producer's `pin-the-block-order`
      regeneration, the width guard gaining an in-block gate crossing
      located strictly inside a step, and the suite now proving directly
      that an engine running a block's members in the published listing
      order disagrees with the corpus. No README version change.
- [ ] 6.2 `evidence.md` for this change: the measurements of §0 with the
      after numbers beside them, the md5s of both corpus files, any
      deviation from this design and why, and the follow-ups.
- [ ] 6.3 `openspec validate mirror-the-gate-guard --strict` green, and
      the change archived under its dated name after implementation —
      the ARCHIVE left for the reviewer, as the previous cycles left it.
