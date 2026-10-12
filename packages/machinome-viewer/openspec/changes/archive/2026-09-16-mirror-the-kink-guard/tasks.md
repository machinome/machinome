## 0. Before anything else — measured on the base, at proposal time

- [x] 0.1 The base, recorded. Worktree `solid-node-viewer/WTs/curta-speed`,
      branch `curta-speed`, head `a35957d` (`walk-only-what-moves`
      implemented, ADR-060 Accepted; package `0.2.0` unreleased,
      `solidNodeViewerApi: 16`, `solidNodeDocumentVersions: [1..7]`,
      highest ADR 060 in `docs/adrs/EXPORT`). Measured in that worktree,
      one job at a time:

      ```text
      $ npx vitest run    →  Test Files  37 passed (37)
                             Tests  962 passed (962)      37.34 s
      $ npx tsc --noEmit  →  clean (exit 0)
      ```

      **Environment note for the applier:**
      `solid_node_viewer/widget/node_modules` is a SYMLINK to the primary
      checkout's. NEVER run `npm ci`, `npm install` or
      `scripts/check-dist` here: through that symlink they empty the
      primary's `node_modules`. `npx vitest run` and `npx tsc --noEmit`
      are safe and are what the numbers above were taken with.
- [x] 0.2 The corpus gap, measured against the framework's file at
      `debd760` (`/home/asa/devel/libresolid-studio/solid-node/WTs/curta-speed`,
      read-only) before anything is written:

      | | committed here | producer's at `debd760` |
      | --- | --- | --- |
      | md5 | `7b9eb6c894c3863710cdbaac68c5fe74` | `651a3b5750c49eecad4587438dc9a85a` |
      | bytes | 263 308 | 267 185 |
      | scenarios / machines / ticks | 19 / 16 / 356 | 20 / 17 / 360 |

      `generated_by`, `corpus` and `tolerance` equal. Added exactly
      `('KinkedStop', 0.1, 4)`, appended LAST; removed none; every one of
      the 19 shared keys equal entry for entry. `KinkedStop`'s document
      is `version: 5`, one law edge `lever drives slide.travel` =
      `(4 + (72 * min(max(((lever - 113.5) / 11.25), 0.0), 1.0)))`,
      `affine: [false]`, `plans: [null]`, span `slide.travel` high `40`.
- [x] 0.3 The producer's file replayed through the SHIPPED engine on this
      base: **all 20 scenarios green**, `KinkedStop` included. The whole
      `src/run/` suite with that file in place: 14 files, 340 tests,
      **one** failure — the census assertion
      (`expected [ …(20) ] to have a length of 19`, `running-corpus.test.ts:226`)
      — and nothing else. Six other test files import the corpus and read
      only its byte-identical documents.
- [x] 0.4 The agreement measured as an IDENTITY rather than a tolerance,
      so the next cycle has a baseline: of the **2 018** floats the
      refreshed corpus records, this engine reproduces **2 009 bit for
      bit** and disagrees on **9**, all `KinkedStop`'s and all
      consequences of its one searched stop —

      ```text
      tick 1    stop slide.travel t   0.47812500000009095  corpus 0.478125
      ticks 1-4 bank lever            119.12500000000364   corpus 119.125
      ticks 1-4 command h0 admitted    19.125000000003638  corpus 19.125
      ```

      9.09e-14 on the fraction: the search's own tolerance, inside the
      corpus's `1e-9` window, and the same order as the 9.3e-14 ADR-123
      measured before it solved. NOT closed here (see `solve-at-the-kink`).
- [x] 0.5 The width guard, measured in all four configurations
      (`REQUIRED` with the producer's new entry appended):

      | corpus | detection absent | detection mirrored |
      | --- | --- | --- |
      | the producer's at `debd760` | `['a stop on a kinked determiner inside a tick']` | `[]` |
      | this viewer's committed copy | same one uncovered | **same one uncovered** |

      Three machines of the refreshed corpus carry a kinked plan-less
      determiner — `Captured` (`p1.lift`, `p2.lift`), `Train`
      (`slide.travel`), `KinkedStop` (`slide.travel`) — and `KinkedStop`
      is the ONLY one recording a stop on one with `0 < t < 1`.

## 1. The corpus, replaced

- [x] 1.1 Copy the framework's `tests/running-corpus.json` at `debd760`
      over `solid_node_viewer/widget/src/running-corpus.json`, BYTE FOR
      BYTE (`cp`, never an edit). Record the md5 of both files in
      `evidence.md` and confirm they match task 0.2's.
- [x] 1.2 RED: run `src/run/running-corpus.test.ts` and record that the
      ONLY failure is the census assertion, with its text.
- [x] 1.3 Correct the census: `toHaveLength(19)` → `20`, `.size).toBe(16)`
      → `17`, `.toBe(356)` → `360` (`running-corpus.test.ts:226-229`).
      Green again.
- [x] 1.4 Run the whole widget suite and record that every one of the 20
      replays is green and that no other test file moved.

## 2. The guard, red first

- [x] 2.1 RED: add `'a stop on a kinked determiner inside a tick'` to
      `REQUIRED` in `run/running-corpus.test.ts`, LAST — after
      `'an in-block gate crossing inside a tick'`, the producer's own
      position and spelling (`tools/generate_running_corpus.py:105`).
      The width test must FAIL naming exactly that string, before any
      detection is written. Record the failure text.
- [x] 2.2 Mirror `_calls` (`tools/generate_running_corpus.py:524-541`) as
      `callsOf(expression, bindings)` beside `freeNamesOf`: every
      function the expression calls, closed transitively over the
      document's bindings table. Design D2 recommends a test-local
      reading over extending `structureOf` (which deliberately reports a
      call's arguments and not its callee); whichever is chosen, record
      the reason in `evidence.md`. Prove on a CONSTRUCTED fixture — not
      on the corpus, whose `KinkedStop` has an empty bindings table —
      that a `min` reached only through a binding is found, and that a
      callee is never mistaken for a free name.
- [x] 2.3 Mirror `_kinked_laws` (`:503-521`) and its tick rule
      (`:491-493`) in `uncoveredFeatures`: a law edge whose `plans` entry
      for a driven end is null (an absent `plans` counting as all-null)
      and whose `expressions` entry for that end calls `abs`, `min` or
      `max` through `callsOf`, gives a KINKED DETERMINER; a recorded stop
      on one with `0 < t < 1` supplies the feature. Through the corpus's
      documents and tick logs ONLY — never through `loadProgram`, for the
      reason the file already states, and this stays true after
      `solve-at-the-kink` gives the engine a classification of its own.
- [x] 2.4 GREEN over the new corpus (`[]`), and record that the same
      guard over the STALE copy (a scratch copy, never a commit) still
      names the feature — that is what makes task 1.1 load-bearing rather
      than cosmetic.

## 3. The narrowed-corpus test

- [x] 3.1 Add the new feature to the assertions of `'is refused when the
      corpus is narrowed'`, beside the self-read's three, the selection's
      one and the block's one, with the reason stated in a comment:
      `Train` DOES carry a kinked plan-less determiner but records no
      stop on it, so trimming to `Train` loses the feature.

## 4. The suite, the types and the build

- [x] 4.1 `npx vitest run` and `npx tsc --noEmit` against task 0.1's
      numbers, with the new totals recorded. Expect the test count to
      rise by the one new replay (`KinkedStop`) plus whatever unit checks
      task 2.2 adds.
- [x] 4.2 NO bundle rebuild, and confirm by diff that none is needed: no
      `src/` module imports `running-corpus.json`, so
      `dist/solid-widget.js` cannot change. Do NOT run `npm ci`,
      `npm install` or `scripts/check-dist` (task 0.1's environment note).
- [x] 4.3 The Python suite is NOT run, and the reason is recorded: the
      corpus is a widget test fixture imported only by TypeScript test
      files, it is not packaged, and `bundle.py`, `server.py` and
      `capture.py` cannot observe this change. If the reviewer wants it
      anyway, say so rather than skipping silently.
- [x] 4.4 Confirm the untouched surfaces by diff: `package.json`
      (`solidNodeViewerApi` 16, `solidNodeDocumentVersions` `[1..7]`),
      `viewer.ts`'s `RENDERED_VERSIONS`, `README.md`, `docs/adrs/`, and
      every file under `src/run/` other than `running-corpus.test.ts`.

## 5. The record

- [x] 5.1 `CHANGELOG.md` under `0.2.0 — unreleased`: ONE bullet — the
      conformance corpus refreshed to the producer's `cut-at-the-kink`
      regeneration, and the width guard gaining a stop located strictly
      inside a step on a kinked determiner. No README version change.
- [x] 5.2 `evidence.md` for this change: the measurements of §0 with the
      after numbers beside them, the md5s of both corpus files, the
      choice made in task 2.2 and why, any deviation from this design,
      and the follow-ups — chiefly that `solve-at-the-kink` stacks on
      this cycle and closes task 0.4's nine floats.
- [x] 5.3 `openspec validate mirror-the-kink-guard --strict` green, and
      the change archived under its dated name after implementation — the
      ARCHIVE left for the reviewer, as the previous cycles left it.
