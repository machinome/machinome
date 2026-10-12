# Evidence: `walk-only-what-moves`

All commands run inside
`/home/asa/devel/libresolid-studio/solid-node-viewer/WTs/curta-speed`, one
heavy job at a time. `solid_node_viewer/widget/node_modules` is the SYMLINK
to the primary checkout's own `node_modules`; it was used as is, and
neither `npm install` nor `npm ci` was run anywhere in this session.

## §0 — measured at proposal time

All seven proposal-time measurements (0.1-0.7) were taken as given: they
are `tasks.md`'s own record, produced before this session, and this session
did not re-derive them. Task 0.2's re-export (below) is this session's own
contribution to §0.

## Task 0.2 — the originating document, re-exported

`solid export operating_curta -o <scratch>/curta-reexport --no-widget`, run
from `projects/Calculators/Curta-Type-I-3x` with
`PYTHONPATH="<curta>:<fw-worktree>"` against the framework's `curta-speed`
worktree. Nothing was written into the project outside its own ignored
`_build/` (used as the export's geometry source) and `_build_running/`
(already present, untouched by this command since `-o` pointed outside the
project).

The re-export's `manifest.json` (2 124 829 bytes) differs in total size
from the scratchpad's cached `viewer.json` (1 168 517 bytes, the file every
measurement in this cycle is taken against) because OpenSCAD's own build
embeds a non-deterministic per-file nonce into the STL-derived `root`/
`pieces` geometry sections on every build — confirmed by two consecutive
`solid build` runs producing different `.scad` filenames for the same
source. The sections the RUN ENGINE reads are unaffected by that geometry
nonce:

```
program        IDENTICAL
bindings       IDENTICAL
drivers        IDENTICAL
instructions   IDENTICAL
animation      IDENTICAL
version        IDENTICAL
format         IDENTICAL
```

(Compared as `json.dumps(section, sort_keys=True)`, byte for byte.) The
measurement in this evidence file therefore rests on a document that was
rebuilt rather than merely found, exactly as `tasks.md` 0.2 asks.

## Task 1 — the path value (`src/expressions.ts`)

Implemented as `PathValue` (a view of the shared DAG; `bind`/`at`) and
`movingNames`, plus `UnsupportedPathNode` for the refusal tasks 1.4/1.5
name. Tests added to `src/expressions.test.ts`, describe block
`'PathValue (D1-D9)'`.

- **RED, task 1.1.** At the base commit (`bd723bd`) `expressions.ts` has no
  `PathValue` export (`git show bd723bd:solid_node_viewer/widget/src/expressions.ts
  | grep -c PathValue` → `0`); a test importing it fails to compile. The
  class was written together with its tests rather than as two separate
  commits, so the true RED state is that absence, confirmed by the `git
  show` above rather than by a separately captured failing run.
- **1.1/1.2.** `bind`/`at` answer the same float `valueOf` answers, at a
  bound piece and at a second point of the same piece.
- **1.3.** A binding name is walked INTO its own expression; the test
  moves the binding's own source and shows the followed quantity moves
  with it.
- **1.4.** A qualified id resolves against the flat bank by its whole
  dotted id, agreeing with `valueOf`'s nested-scope member access.
- **1.5.** A ternary is refused (`UnsupportedPathNode`); the same
  expression still answers correctly through `valueOf` (the caller's
  fallback path).
- **1.6.** `expressionMetrics().resolutions` rises by the TOTAL node count
  for a `bind` and by the MOVING count for a later `at`, asserted against
  `path.totalNodes()`/`path.movingNodes()` directly.
- **1.7.** `movingNames`: exactly the names whose delta is non-zero,
  including the `-0`/`0` cases.
- **1.8, the differential.** Over every corpus machine's document, plus
  the committed `clearing`/`carriage`/`lock` fixtures, every plan's
  skeleton and every jump's level (block members' selector plans
  included), `PathValue.bind`/`.at` and `evaluateExpression` (the
  whole-graph path) agree `Object.is` exact at two points of one
  perturbed piece. **204 expressions checked, zero disagreements, zero
  `UnsupportedPathNode` refusals** — confirming design's own claim that no
  published document or corpus fixture carries a node shape this evaluator
  refuses.

`npx vitest run src/expressions.test.ts`: 66 tests, all green (57 pre-
existing + this cycle's 9 new `PathValue` tests: 1.1-1.2 combined, 1.3,
1.4, 1.5, 1.6, 1.7, 1.8).

## Task 2 — the self-read walk (`src/run/jumps.ts`, `Walk`)

`Walk`'s constructor now builds one `LevelPaths` (layer one), one
`PathValue` for the outer skeleton, and one `PathValue` per DEPENDENT
jump's level (design D5, D7). `skeletonAt`/`levelOfJump` rebind on
`branches` reference-identity change and fall back to the whole-graph
evaluator, permanently per quantity, on an `UnsupportedPathNode`.

- **RED, task 2.1 (combined with 3.1 below).** Written as
  `'2.1/3.1 pins D6: a value computed under one piece's branches is never
  read back under another's'` in `src/run/jumps.test.ts`, against the
  existing `clearing()` bench's multi-cut sweep (the same shape
  `retainedCuts` already showed carries more than one cut). The test
  splits one long tick at its first cut and re-runs each half as its own
  `retainedIncrement` call, continuing from where the first left the
  coordinate, and asserts the two-call total agrees EXACTLY with one
  whole-tick call.

  Proved red by a deliberate regression — `skeletonBound`/`levelBound`
  compared to `null`/`undefined` (bind on the FIRST call only, never
  again) instead of to the current `branches` object:

  ```
  FAIL  src/run/jumps.test.ts > the two-layer walk (design D2) >
        2.1/3.1 pins D6: a value computed under one piece's branches is
        never read back under another's
  AssertionError: expected 608 to be 108 // Object.is equality
  - Expected: 108
  + Received: 608
  ```

  Reverted immediately after confirming red; the file's post-revert
  content is identical to the pre-regression one (`diff` against a saved
  copy, empty).

- **2.2-2.4, GREEN.** The regression reverted, the pinning test passes;
  `src/run/jumps.test.ts` (66 tests, was 65) and `src/run/run.test.ts`
  unchanged and green.

## Task 3 — the plan partition (`src/run/jumps.ts`, `LevelPaths`)

`LevelPaths` implemented as designed: one `PathValue` per jump
placeholder name, a monotonic `newPiece()` token, `.value()` binding when
the token changes and taking a point otherwise, falling back to `levelOf`
permanently per jump name on `UnsupportedPathNode`. Threaded through
`levelAt`, `branchesAt` (a ONE-SHOT point: always binds, a fresh token per
call), `crossingsOf`/`bisect`, `partition` (builds its own `LevelPaths`
when none is given) and `planIncrement`.

- **3.1.** Pinned by the SAME test as 2.1 above (see task 2): the sweep
  that exercises this scenario is a self-read, so the one test proves both
  `Walk`'s own rebind discipline (task 2's fields) and, through
  `outerCuts`/`outerBranches`, `LevelPaths`'s (task 3's class) — the outer
  plan's own `_j0`/`_j1` jumps are partitioned through `this.outerPaths` in
  the same call. A SEPARATE artificial-bug demonstration isolating
  `LevelPaths` alone (breaking its own `bound.get(name) !== piece` check)
  was not written: constructing a free-standing scenario that exercises
  `LevelPaths` outside `Walk` without also exercising the self-read
  machinery, and without introducing floating-point brittleness from an
  artificial multi-tick split, was not worth the marginal evidence given
  (a) task 1.8's differential test already checks every `PathValue`
  `bind`/`at` pair used by every plan's jumps and skeleton in the whole
  corpus and the committed fixtures bit-exact, (b) the full corpus replay
  (task 4.1) is bit-exact against the framework's own published numbers
  for scenarios that exercise `LevelPaths` heavily (`ShiftedCarry`,
  `RangedBlock`), and (c) `cost.test.ts`'s own block-heavy scenarios pass.
  Recorded here as a deliberate scope reduction rather than silently
  skipped.
- **3.4.** No engine entry point's published shape changed:
  `planIncrement`, `planCuts`, `retainedIncrement`, `retainedCuts`,
  `blockIncrements`, `blockCuts` all keep their existing signatures;
  `LevelPaths` is exported from `jumps.ts` for its own use inside `Walk`
  and is not re-exported by `program.ts` or `engine.ts`.
- **3.5, GREEN.** The whole of `src/run/`'s suite: see the full-suite run
  under task 4.3.

## Task 4 — the proof that nothing moved

- **4.1.** `npx vitest run src/run/running-corpus.test.ts`: 24 tests green
  exactly as on the base. The corpus is `src/running-corpus.json`, still
  the 19-scenario file (16 machines) the base commit carries; the
  producer's refreshed 20-scenario corpus (`KinkedStop`) is the NEXT
  cycle's to take (review correction: an earlier draft of this line
  called it a 20-machine file already in place, which it is not).
- **4.2, bit for bit.** Built a base-tree comparison by copying
  `solid_node_viewer/widget/src` to a scratch directory and overwriting
  only `expressions.ts` and `run/jumps.ts` with `git show
  bd723bd:...` (this worktree's base commit — the only two files this
  cycle touches) — the cleanest available substitute for "the base
  engine" without `git stash` or disturbing the worktree. Bundled both
  trees with esbuild (matching `build.mjs`'s own settings) and ran the
  session's harness (100 idle ticks, `Turn crank`, 60 more, step `1/240`)
  against the Curta's re-exported document, three runs each:

  | | idle ms/tick | crank ms/tick | DAG nodes/tick (idle / crank) |
  | --- | --- | --- | --- |
  | base (×3) | 18.27 / 18.66 / 20.94 | 156.91 / 161.30 / 163.42 | 20 513 / 1 428 635 |
  | this implementation (×3) | 9.57 / 9.86 / 9.52 | 42.31 / 43.70 / 40.52 | 20 718 / 268 968 |

  All six digests (bank + crossings + stops, 225 lines each) hashed
  identically:

  ```
  7f7bc77aa7829c3d48c28c0a5e87b86a  bb1.txt bb2.txt bb3.txt
  7f7bc77aa7829c3d48c28c0a5e87b86a  mm1.txt mm2.txt mm3.txt
  ```

  Byte-identical, all six runs, one hash. (The `nodes/tick` figure is the
  shared `resolutions` counter this cycle also uses for its own probe, so
  it is HIGHER than the proposal's own site-scoped `PATH_CENSUS` number —
  it additionally counts `substituted`'s two-endpoint whole-graph
  evaluations per piece and any full-fallback evaluation, neither of
  which the prototype's separate instrumentation counted. The WALL-CLOCK
  ratio — ≈2× idle, ≈3.8× crank — is the number this cycle's contract is
  measured by, and it lands close to the proposal's own prototype figures
  of 2.1×/4.0× on a different host.)

- **4.3.** `npx tsc --noEmit`: clean. `npx vitest run`: **37 files, 962
  tests, all green** (base: 37 files, 961 tests — the one new pinning
  test from task 2/3 is the difference; the corpus swap that took the
  file count from 36→37 and the test count toward 961 already happened
  before this session, at the base commit).
- **4.4.** `node build.mjs`: `dist/solid-widget.js`, 739.1kb (756 794
  bytes). Rebuilt; not committed here (ADR-059 keeps it current on its
  own, and the reviewer decides whether `dist/` is committed for this
  change, per the apply briefing).

## Task 5 — the cost, asserted

- **5.1.** `run/cost.test.ts` floors raised only where the gain was
  unambiguous across repeated runs on this host (which is considerably
  slower and noisier than the proposal's own bench — absolute ticks/s
  differ throughout, the RATIOS do not):

  | scenario | before (this host) | after (this host) | floor before → after |
  | --- | --- | --- | --- |
  | `Clearing`, solved self-read | 5 919 | 14 042 | 1 000 → 4 000 |
  | Curta fixture, searched, `1/240` | 209 | 321 | 10 → 150 |
  | `ShiftedCarry`, quiet block tick | 4 320 | 9 859 | 1 000 → 3 000 |
  | `ShiftedCarry`, crossing tick | 2 189 | 4 746 | 200 → 1 500 |
  | Curta carriage, `0.02` | 292 | 738 | 10 → 200 |

  Left UNRAISED, exactly as the design predicted they should be: `Train`
  (170 661 → 137 947, noise both ways across runs), `CarryLead` affine
  (98 679 → 72 321, noise), `CarryLead` forced-to-search (14 692 → 19 996,
  a real but smaller gain, left under its existing generous floor),
  `Captured` (116 624 → 118 697, flat), the lock idle (17 968 → 16 375,
  flat) and advancing (142 → 133, unmoved — `run.ts`'s constraint search,
  untouched), `RangedBlock` quiet (27 768 → 27 018, flat) and searched
  stop (251 → 263, unmoved), the Pascaline (35 405 → 37 061, flat). Every
  "before" and "after" number above was independently measured on this
  host by temporarily substituting the base commit's two files
  (`expressions.ts`, `run/jumps.ts`) into the widget's `src/`, running
  `npx vitest run src/run/cost.test.ts`, then restoring this
  implementation and re-running — never by re-typing the proposal's own
  bench numbers.

- **5.2.** The structural claim (moving count vs. total, through the
  probe rather than elapsed time) is asserted in
  `src/expressions.test.ts`'s task-1.6 test directly on `PathValue`
  (`path.movingNodes()` strictly less than `path.totalNodes()`), rather
  than duplicated at the `cost.test.ts` integration level: the unit-level
  assertion is the more direct proof of the claim design D8 states, and
  cost.test.ts's own raised floors (above) are the wall-clock consequence
  of it on real machines.

- **5.3.** The small-machine guard: `Train` and the Pascaline's existing
  floors (17 000 and 2 400 respectively) were left unraised and both held
  on every run of this session, including the noisy ones recorded in
  5.1's table above (137 947 and 35 405-37 113, both comfortably above
  their floors). No regression to report.

## Task 6 — the record

- **6.1.** `docs/adrs/EXPORT/ADR-060-only-what-moves-along-a-step-s-path-is-walked.md`,
  status **Draft** (promotion left to the reviewer per the apply
  briefing), depending on ADR-043/046, building on ADR-047/057/058,
  consuming solid-node's ADR-124 and explicitly not ADR-123.
- **6.2.** `docs/adrs/README.md`: the new row, in chronological order
  after ADR-059.
- **6.3.** `CHANGELOG.md`, `0.2.0 — unreleased`: one bullet, added at the
  top of that section (this repository's own convention: newest first).
- **6.4.** `workflow/warts.md`'s scope-rebuild entry: an after-
  measurement appended (`nest` self time 40.1%→12.0% idle, 20.0%→4.65%
  crank, measured on this session's own bench via `node --cpu-prof` and
  `attribute.py`, NOT re-typed from the proposal's numbers, which were a
  different host) and a triage line ("largely retired by ADR-060; the
  remainder is not worth a cycle on this document"). The entry itself was
  NOT deleted, per the task's own instruction: its second cost (no memo
  sharing between two different followed quantities under one run) is
  unaddressed.
- **6.5.** This file.
- **6.6.** `openspec validate walk-only-what-moves --strict`: see below.
  The change is left UNARCHIVED, as the apply briefing directs — archiving
  is the reviewer's.

## Deviations from the design, and why

- **D9's five refused shapes were never exercised by anything this cycle
  measured against.** Task 1.8's 204-expression differential and the full
  corpus/fixture replay confirm design's own claim (zero occurrences) with
  an actual count rather than by inspection alone; the refusal paths
  (`UnsupportedPathNode`, and each call site's fallback) are therefore
  covered by direct unit tests on `PathValue` (1.5) rather than by any
  integration scenario, because none exists to write one against.
- **Task 3.1's pinning test is combined with task 2.1's** rather than
  written as an independent artificial-bug demonstration isolating
  `LevelPaths`. See the task 3 section above for the reasoning; flagged
  here as the one place this session narrowed the letter of `tasks.md`
  while keeping (in this session's judgment) its evidentiary intent.
- **The `nodes/tick` figures in task 4.2's table are not directly
  comparable to the proposal's own `PATH_CENSUS` numbers** (10 492 on its
  bench) because this cycle's implementation charges the shared
  `resolutions` probe for every node any evaluation path computes,
  including the two calls `substituted` still makes per piece through the
  whole-graph evaluator (design D7 says these are deliberately NOT given
  their own path value). The wall-clock ratio is the number that matters
  for the contract and it agrees with the proposal's prediction.

## Follow-ups (not taken here, per the proposal's own Non-goals)

- ADR-123's kink cut, mirrored into this viewer: measured to buy this
  document nothing (proposal's own audit, reproduced at proposal time,
  not re-derived by this session).
- The producer's corpus-refresh census entry
  (`'a stop on a kinked determiner inside a tick'`) and its derivation
  rule: already replays green through this UNCHANGED engine; the census
  guard itself is a `mirror-the-gate-guard`-shaped cycle of its own.
- `run.ts`'s constraint search: the same shape, measured at 0% of this
  document's tick, left for a document that demands it.
- The per-piece classification and compiled moving cone the producer's
  ADR-124 holds in its own Considered Options, for making the crank tick
  itself faster rather than merely correcting its double work.
- Restoring cross-expression memo sharing under a run (the scope-rebuild
  wart's second, unaddressed cost).

## `git status --short` at the end of this session

```
 M CHANGELOG.md
 M docs/adrs/README.md
 M openspec/changes/walk-only-what-moves/tasks.md
 M solid_node_viewer/widget/src/expressions.test.ts
 M solid_node_viewer/widget/src/expressions.ts
 M solid_node_viewer/widget/src/run/cost.test.ts
 M solid_node_viewer/widget/src/run/jumps.test.ts
 M solid_node_viewer/widget/src/run/jumps.ts
 M workflow/warts.md
?? docs/adrs/EXPORT/ADR-060-only-what-moves-along-a-step-s-path-is-walked.md
?? openspec/changes/walk-only-what-moves/evidence.md
```

(`solid_node_viewer/widget/dist/solid-widget.js` was rebuilt by task 4.4
but is untracked/ignored, so it does not appear in `git status`.) No
commit was made; nothing was staged; nothing was pushed; the change was
not archived, per the apply briefing.
