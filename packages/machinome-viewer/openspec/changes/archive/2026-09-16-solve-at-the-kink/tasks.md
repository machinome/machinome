## 0. Before anything else — measured on the base, at proposal time

- [x] 0.1 The base, recorded. Worktree `solid-node-viewer/WTs/curta-speed`,
      branch `curta-speed`, head `a35957d` (ADR-060 Accepted; package
      `0.2.0` unreleased, `solidNodeViewerApi: 16`,
      `solidNodeDocumentVersions: [1..7]`, highest ADR 060). `npx vitest
      run` → 37 files, 962 tests, 37.3 s; `npx tsc --noEmit` clean.

      **This cycle stacks on `mirror-the-kink-guard`** and is applied
      AFTER it: `KinkedStop` is the scenario whose float this change
      moves, and the census must already be right.

      **Environment note:** `solid_node_viewer/widget/node_modules` is a
      SYMLINK to the primary checkout's. NEVER run `npm ci`,
      `npm install` or `scripts/check-dist` here — through that symlink
      they empty the primary's. `npx vitest run` and `npx tsc --noEmit`
      are safe. `dist/solid-widget.js` is gitignored and kept current by
      the package itself (ADR-059): there is no bundle to commit.
- [x] 0.2 The classification mirrored and VALIDATED against the only
      external check there is — the published flag:

      | document | published `affine` flags | disagreements |
      | --- | --- | --- |
      | the refreshed corpus's 20 documents | 39 ends + 34 levels = 73 | **0** |
      | the operating Curta, version 7 | 268 ends + 547 levels = **815** | **0** |

      and the Curta census reproduces the producer's published one
      exactly: 28 kinked plan-bearing skeletons, 41 unclassified, 183
      affine and 16 kinked plan-less laws, 532 affine and 15 kinked jump
      levels.
- [x] 0.3 The static corpus audit. SEVEN driven ends of the refreshed
      corpus become KINKED — `Captured` `p1.lift`/`p2.lift`, `CarryLead`
      `tens.turn`, `KinkedStop` `slide.travel`, `Remainder`
      `pinion.turn`, `Train` `slide.travel`, `Window` `pinion.turn` —
      **no jump level in the corpus is kinked at all**, and **none of the
      seven is a self-read**. A reclassified end is observable only
      through `run.ts`'s `locate`; the corpus records ten stops and
      exactly one is on one of the seven, `KinkedStop`'s at `0.478125`.
      So exactly one recorded float can move.
- [x] 0.4 The dynamic corpus audit, over the prototype: of the **2 018**
      floats the refreshed corpus records, the base disagrees with the
      producer on **9** and the prototype on **0**. The nine are
      `KinkedStop`'s stop fraction (`0.47812500000009095` against
      `0.478125`), its `lever` bank value on all four ticks
      (`119.12500000000364` against `119.125`) and `h0`'s admitted travel
      on all four (`19.125000000003638` against `19.125`).
- [x] 0.5 What it buys, and what it must not cost, measured on the
      prototype (`scratchpad/spikes-bc/proto`, three runs each):

      | | base | prototype |
      | --- | --- | --- |
      | `clearing` fixture evaluations/tick | 32 004 | **2 724** |
      | `clearing` fixture ticks/s | 297 / 303 / 308 | **1 233 / 1 254 / 1 216** |
      | `Clearing` evaluations/tick | 471.1 | 471.1 |
      | `Train` evaluations/tick | 31.0 | 31.0 |
      | the Curta carriage evaluations/tick | 5 913.2 | 5 913.2 |

      `run/cost.test.ts` elsewhere: `Train` 159-169k → 160-179k ticks/s,
      the Pascaline 30-36k → 32-36k, `CarryLead` 83-90k → 80-94k,
      `Clearing` 12.8-13.5k → 13.8-14.1k, `ShiftedCarry` quiet 9.7-10.0k
      → 9.8-10.2k, the Curta carriage 736-754 → 741-762, the lock
      advancing the key 133-135 → 132-143, `RangedBlock`'s searched stop
      220-231 → 245-263. All inside their own spread.
- [x] 0.6 The operating Curta, unchanged: idle 20 718 and crank 260 306
      evaluations/tick before and after, to the unit; 10.1-11.0 → 11.1 ms
      idle and 41.3 → 42.2 ms crank; and the bank, crossings and stops
      after 70 ticks byte-identical. This cycle is exactness and
      generality, not Curta speed.
- [x] 0.7 The structural constraint that decides where the kink level is
      evaluated: `src/run/edges.test.ts` asserts that `program.ts` is the
      ONLY module under `src/run/` calling `valueOf` or `evalExpr`. The
      prototype tripped it and the evaluation moved beside
      `evaluateExpression`. Do not fight it.
- [x] 0.8 The composition with ADR-060 measured: with the kink levels
      left on the plain evaluator (the producer's own choice), they are
      **960 of the prototype's 2 724 evaluations/tick on the `clearing`
      fixture, in 96 calls**, and ZERO on `Clearing`, `Train`, the Curta
      carriage and every corpus machine. Recorded as a follow-up, not
      taken (design D5).

## 1. The classification (design D1)

- [x] 1.1 RED FIRST, and it is the contract test: a test that classifies
      every law driven end and every jump level of every document the
      suite holds — the 20 corpus documents and the committed fixtures —
      and asserts that the viewer's `constant`/`affine` is exactly the
      document's `affine: true`, and that nothing it finds `kinked` or
      unclassified is published affine. Write it before the classifier
      and watch it fail to compile, then watch it pass on 73 corpus flags
      and the fixtures'.
- [x] 1.2 The three-valued classification in `src/expressions.ts`, over
      the interned DAG, with the constant set passed in (the plan's jump
      names) and the bindings roots walked INTO — the table of design D1,
      row for row. A call with no arguments, `$t`, a cyclic binding and
      every unlisted operator are unclassified.
- [x] 1.3 Unit tests for the table: `min(max((x-a)/b, 0), 1)` kinked;
      `2*kinked + 3` kinked; `kinked * moving` unclassified;
      `max(0, sin(x))` unclassified; `abs(x)/moving` unclassified;
      a placeholder alone constant; a kink reached only through a binding
      kinked; a comparison unclassified.
- [x] 1.4 Compute it at LOAD in `src/run/program.ts` — per plan skeleton,
      per jump level, per `RetainedReading` (the FULL plan's skeleton with
      the FULL plan's jump names, not the `outer` subset's), and per
      driven end of a law with no plan — and store it beside the flag the
      run already reads. Assert it is computed once per quantity and not
      per step.

## 2. The kink inventory and the breakpoints (design D2)

- [x] 2.1 The kink inventory in `src/expressions.ts`: the kink nodes of a
      root in the expression's own postorder, each as the pair of operand
      node ids whose difference is its level (`abs` carrying only the
      first). Mint no node and hold no text.
- [x] 2.2 The breakpoint solve, mirroring `_KinkCuts.between`
      (`solid_node/simulation/program.py:775-800`): postorder, per
      sub-interval, skip where the level does not move or is not finite
      or does not straddle zero, one division, keep only strictly inside,
      fold under the CROSSING tolerance. No new tolerance.
- [x] 2.3 `merged` in `src/run/jumps.ts` gains the stretch's right END
      (default 1), because a sub-division inside one piece must not be
      pinned to the tick's own end. Red-first on a sub-piece.
- [x] 2.4 The kink level's evaluation beside `evaluateExpression` in
      `src/run/program.ts` (task 0.7), on the plain evaluator, `a − b` as
      the subtraction of two evaluations of the same DAG.
- [x] 2.5 Unit tests: two breakpoints inside the crossing tolerance
      collapse to one; a kink whose level is constant over the stretch
      contributes none; a kink nested in another's level is cut first;
      the returned list is the INTERIOR breakpoints only.

## 3. A jump level's crossings (design D4 (a))

- [x] 3.1 RED (design §8 case B): a fixture whose gate's level reads a
      `clamp01` of a driver, crossed strictly inside a step with the
      clamp inside its window there, and the exact fraction stated as a
      closed form of the fixture's own arithmetic — never read back from
      the law. Fails by the search's tolerance today. The corpus carries
      no kinked jump level at all (task 0.3), so this fixture is written
      here.
- [x] 3.2 Refactor the affine body of `crossingsOf` into a local
      `solved(left, right, closed)`: `closed` takes the right end
      inclusively and drops a surface equal to the piece's own left
      value. With `closed` false everywhere this is a no-op — prove it by
      the suite before the kinked branch is added.
- [x] 3.3 The kinked branch: breakpoints under the same `values` the
      level is read at; none → solve the whole piece; otherwise each
      sub-piece left to right, `closed` for all but the last, through the
      existing `deduplicated`.
- [x] 3.4 The boundary test: a surface lying EXACTLY on an interior
      breakpoint is located once, not twice and not zero times.

## 4. The self-read walk (design D4 (b))

- [x] 4.1 RED (design §8 case C): the committed `clearing` fixture's cost
      as subexpression resolutions per tick, asserted at 32 004 today and
      under 4 000 after.
- [x] 4.2 `Walk.crossing`, mirroring `_crossing`
      (`program.py:1346-1379`): published-affine both → unchanged; either
      shape unclassified → searched, unchanged; otherwise the SKELETON's
      breakpoints first, each cut again by the LEVEL's, located inside
      that skeleton sub-piece with the driven coordinate interpolated
      between its two ends, solved left to right, `closed` for all but
      the very last sub-piece of the very last skeleton piece.
- [x] 4.3 The walk's own cuts gain the skeleton's kinks ONLY when the
      caller asked for cuts (`cutting`, mirroring `program.py:1202`), so
      an ordinary self-read tick pays nothing for them. Assert the cost
      of an ordinary tick does not move.
- [x] 4.4 Assert the cuts list stays sorted and that a breakpoint never
      reaches `crossings`, `land` or the crossing maximum (design D3).

## 5. The stop (design D4 (c))

- [x] 5.1 RED (design §8 case A), as an IDENTITY and not within the
      corpus tolerance: `KinkedStop`'s stop fraction, its `lever` bank
      value and `h0`'s admitted travel must equal `0.478125`, `119.125`
      and `19.125` EXACTLY. Fails today at 9.09e-14 / 3.6e-12 / 3.6e-12.
      Name the strong trap in the test's comment: an implementation that
      leaves `edgeCuts` returning `[]` for a plan-less law divides once
      over the whole step — write that fraction down.
- [x] 5.2 `locate` takes the solved path where the published flag is true
      OR the viewer's shape is kinked.
- [x] 5.3 `edgeCuts` for a law with NO plan: its own kinks over the step
      as one piece, `[]` where none is reached. The invariant "empty cuts
      means affine over the whole step" gets its own test.
- [x] 5.4 `planCuts` unions the skeleton's kinks into the partition,
      located inside each piece with that piece's branch readings
      substituted — a placeholder is constant only within its own piece.
      Test with a plan-bearing kinked skeleton (`Window`'s
      `pinion.turn`).
- [x] 5.5 Assert a stop on a BLOCK coordinate is STILL searched:
      `RangedBlock`'s corpus entry and its cost number do not move.

## 6. Nothing else moves (design §8 case D, E)

- [x] 6.1 The whole refreshed corpus replays, and the identity is
      asserted where the suite can: every float of `KinkedStop` equal to
      the producer's exactly (task 5.1), and every other scenario green
      under the corpus's own comparison.
- [x] 6.2 `Clearing`, `Train` and the Curta carriage cost EXACTLY 471.1,
      31.0 and 5 913.2 evaluations/tick, before and after.
- [x] 6.3 Case E: a curved quantity is still searched — `max(0, sin(x))`
      and a product of two movers classify unclassified and cost what
      they cost today. One test, named, so a later per-branch cycle has a
      starting point.
- [x] 6.4 `src/running-corpus.json` is NOT touched by this cycle: confirm
      by diff.
- [x] 6.5 `run/cost.test.ts`: raise the `clearing` fixture's floor to
      what task 0.5 measured, leave every other floor alone, and record
      the new numbers in the comments beside the old as the previous
      cycles did.

## 7. The suite, the types and the record

- [x] 7.1 `npx vitest run` and `npx tsc --noEmit` against task 0.1's
      numbers, with the new totals recorded. No `npm ci`, no
      `npm install`, no `scripts/check-dist`.
- [x] 7.2 ADR-061 in `docs/adrs/EXPORT`, `a-kink-is-a-cut-in-the-viewer-too`
      or the applier's better title: Accepted, dated, change
      `solve-at-the-kink`, extending ADR-045/046, building on 047, 057
      and 058 and on ADR-060, CONSUMING solid-node's ADR-123 — and
      recording the one place it contradicts that ADR's Consequences:
      the viewer CAN re-derive the shape, because the classification is
      structural and the document carries the expression. Carry the
      815-flag and 73-flag agreement, the 9 → 0 corpus floats, the
      11.7× on the `clearing` fixture, the Curta's unchanged numbers,
      and the two deferrals (the block's stop, the per-branch
      classification). Add the row to `docs/adrs/README.md` in
      chronological order.
- [x] 7.3 `CHANGELOG.md` under `0.2.0 — unreleased`: ONE bullet — a
      quantity built over `abs`, `min` or `max` is solved at its own
      kinks instead of searched, the viewer deriving the shape from the
      published expression, with no document or API change.
- [x] 7.4 `evidence.md`: the measurements of §0 with the after numbers
      beside them, the corpus audit both ways, any deviation from this
      design and why, and the follow-ups — the path-valued kink level
      (task 0.8's 960 of 2 724), the per-branch classification ADR-123
      defers, and the block's stop.
- [x] 7.5 `openspec validate solve-at-the-kink --strict` green, and the
      change archived under its dated name after implementation — the
      ARCHIVE left for the reviewer, as the previous cycles left it.
