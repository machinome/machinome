# Evidence: `solve-at-the-kink`

All commands run inside
`/home/asa/devel/libresolid-studio/solid-node-viewer/WTs/curta-speed`, one
heavy job at a time. `solid_node_viewer/widget/node_modules` is the SYMLINK
to the primary checkout's own `node_modules`; it was used as is, and
neither `npm install`, `npm ci` nor `scripts/check-dist` was run anywhere
in this session. The framework worktree and
`projects/Calculators/Curta-Type-I-3x` were read only.

**The base of this cycle is `c0bb200`** — `mirror-the-kink-guard` applied
and archived, so `src/running-corpus.json` is the producer's refreshed
20-scenario corpus. Measured on the base before a line was written:

| | base |
| --- | --- |
| `npx vitest run` | 37 files, **963 tests**, 38.4 s |
| `npx tsc --noEmit` | clean |
| corpus floats not bit-identical to the producer's (of 2 018) | **9** |
| `clearing` fixture | **32 004** evaluations/tick, **342** ticks/s |
| `Clearing` / `Train` / Curta carriage | **471.1 / 31.0 / 5 913.2** evaluations/tick |
| the operating Curta, idle / crank | **20 718 / 268 968** evaluations/tick, digest `7f7bc77a…` |

## §0 — the proposal-time measurements

0.1 and 0.3-0.8 were taken as given: they are `tasks.md`'s own record,
produced before this session. Where this session could re-derive one on
the real implementation rather than on the prototype it did, and every
such number is reported below beside the proposal's. **Every one of them
reproduced exactly**: 9 → 0 corpus floats, 73 and 815 flags with zero
disagreements, 32 004 → 2 724 evaluations/tick on the `clearing` fixture,
471.1 / 31.0 / 5 913.2 unmoved, the Curta unmoved to the unit, and the
kink levels 960 of 2 724 in 96 calls.

## Task 1 — the classification (D1)

- **1.1 RED, the contract test.** Written first, in
  `src/run/program.test.ts` (`the classification agrees with the published
  flag (D6)`): every law driven end and every jump level of the 20 corpus
  documents and of the five committed run fixtures (`pascaline`, `lock`,
  `clearing`, `carriage`, `touched`), the viewer's derived shape against
  the published `affine` flag. Red before the loader carried a shape at
  all:

  ```
  FAIL  src/run/program.test.ts > the classification agrees with the
        published flag (D6) > finds constant or affine EXACTLY where the
        corpus publishes affine
  TypeError: Cannot read properties of undefined (reading '0')
   ❯ src/run/program.test.ts:1775:26
      1775|           if (solved(one.shapes[index]) !== one.affine[index]) {
  ```

  (`tsc --noEmit` cannot be the red here: `tsconfig.json` excludes
  `src/**/*.test.ts`, so a test naming a field that does not exist fails
  at run time and not at type-check time.)

  GREEN, and the count is asserted in the test itself: **39 driven ends +
  34 jump levels = 73** corpus flags, **zero** disagreements; the
  fixtures add **47 ends + 110 levels = 157** flags, **zero**
  disagreements.

- **1.2 the classification** in `src/expressions.ts`: `PathShape`,
  `shapeOf(root, constants, bindings)`, the design D1 table row for row,
  over the interned DAG, walking INTO the bindings table exactly as
  `PathValue.childrenOf` does. A call with no argument, `$t`, a cyclic
  binding and every unlisted operator are unclassified. It mints no node
  and holds no expression text.
- **1.3 the unit tests** (`src/expressions.test.ts`, describe
  `shapeOf (design D1)`): a literal and a sum of literals constant; a
  source name affine; a placeholder constant alone and inside a product;
  `min(max((x - a) / b, 0), 1)` and `abs(x)` kinked; `2 * kinked + 3`,
  `-abs(x)`, `abs(x) - y` and `abs(x) / 4` kinked; `kinked * moving`, a
  moving divisor, a power and a comparison unclassified; `max(0, sin(x))`
  and `min(x, y * x)` unclassified; a kink reached only through a binding
  kinked; `$t` and a cyclic table unclassified.
- **1.4 computed at LOAD** in `src/run/program.ts`, in one pass placed
  after the interned roots and the bindings table exist and before the
  self-read derivation. Stored on `ProgramPlan.shape/.kinks` (under the
  plan's own jump names as the constants), on `ProgramJump.shape/.kinks`,
  on `ProgramEdge.shapes[]/.kinks[]` per driven end (the plan's skeleton
  where there is a plan, the published expression where there is not,
  `'constant'` for a constant law) and on `RetainedReading.shape/.kinks`,
  which takes the FULL plan's classification — `outer` holds the same
  skeleton TEXT, and design §7's last risk is answered by construction
  rather than by a second classification. A block edge carries `null`
  shapes: the producer's own deferral.

  "Computed once per quantity and not per step" is a property of WHERE it
  is computed — the loader, before a tick exists — and is asserted
  structurally by the flag-agreement test reading `program.edges` with no
  `Run` in sight, and by the `Clearing`/`Train`/carriage
  evaluations-per-tick equalities below (a per-step classification would
  charge the resolution probe).

## Task 2 — the kink inventory and the breakpoints (D2)

- **2.1** `kinkLevels(root, bindings)` in `src/expressions.ts`: the kink
  nodes in the expression's own POSTORDER, each as the pair of operand
  node ids whose difference is its level (`abs` carrying only the first).
  Tested (`kinkLevels (design D2, tasks 2.1)`): the operand ids are the
  interned nodes themselves, the node table does NOT grow when the
  inventory is taken, `abs` has no second operand, an inner kink comes
  first, and a kink reached only through a binding is found.
- **2.2** `kinkBreaks(kinks, level, left, right, tolerance)` in
  `src/run/jumps.ts`, mirroring `_KinkCuts.between`
  (`solid_node/simulation/program.py:775-800`) line for line: postorder,
  per sub-interval, skipped where the level does not move or is not
  finite or does not straddle zero, one division, kept only strictly
  inside, folded through `merged` under the CROSSING tolerance. No new
  tolerance anywhere in this cycle.

  **Deviation from the proposal's Impact list, deliberate.** The
  proposal put "a kink inventory" in `expressions.ts` and "the skeleton
  and level cut helpers" in `jumps.ts`; the prototype instead carried a
  `KinkCuts` class in `expressions.ts` with its own INLINE copy of
  `merged`. This implementation splits it as the Impact list says: the
  inventory is `expressions.ts`'s, the breakpoint solve is `jumps.ts`'s
  and calls the one `merged` — so there is no second copy of the fold to
  drift from the first.
- **2.3 RED**, `merged` pinned to the tick's own end:

  ```
  FAIL  src/run/jumps.test.ts > merged > ends at the STRETCH's own right
        end when it is given one (openspec `solve-at-the-kink`, tasks 2.3)
  AssertionError: expected [ 0.2, 0.4, 1 ] to deeply equal [ 0.2, 0.4, 0.6 ]
  ```

  GREEN with `end = 1` as the default, so every existing caller is
  unchanged (asserted in the same test).
- **2.4** `kinkLevel(program, kink, values)` beside `evaluateExpression`
  in `src/run/program.ts` — `a` minus `b` as two evaluations of the SAME
  DAG, on the plain evaluator — because `src/run/edges.test.ts` asserts
  structurally that `program.ts` is the only module under `src/run/` that
  reaches `valueOf`. That test stayed green throughout; the constraint was
  not fought.
- **2.5 the unit tests** (`kinkBreaks (…tasks 2.5)`): the interior
  breakpoints only (a zero AT an end contributes nothing); none where the
  level stands or is infinite; two breakpoints within the crossing
  tolerance folded to one; a kink whose level is a V — equal at the
  stretch's two ends and so reaching nothing — cut TWICE once an earlier
  kink has sub-divided the stretch, and once only in the other order,
  which is what the postorder is for; and a breakpoint located inside a
  sub-stretch `[0.2, 0.6]`.

## Task 3 — a jump level's crossings (D4 (a))

- **3.1 RED.** The corpus carries no kinked jump level at all (measured
  below), so the fixture is written here: `floor` of
  `10 * clamp01((crank - 2) / 4)`, driven 0 → 8, so the window opens at
  `t = 0.25` and closes at `t = 0.75`. Red, and worse than "a few ulp
  out" — the search reported **42** crossings where the solve reports
  ten, because the level STANDS at 0 over the first quarter and an
  inclusive sample-to-sample search reports the surface 0 at every one of
  those samples:

  ```
  FAIL  src/run/jumps.test.ts > a kinked jump level is SOLVED on its own
        sub-intervals > 3.1 locates every surface at the fraction the
        SUB-PIECE's own division gives, exactly
  AssertionError: expected [ { level: +0, t: +0 }, …(41) ] to deeply equal
                            [ { level: 1, t: 0.3 }, …(9) ]
  ```

  GREEN at exactly `0.25 + (0.75 - 0.25) * level / 10` for every one of
  the ten surfaces — the closed form of the fixture's own arithmetic,
  stated in the test and never read back from the law.
- **3.2 the refactor.** `crossingsOf`'s affine body is now a local
  `solved(lowT, highT, closed)`. With `closed` false it is the previous
  body character for character plus one dead guard (`if (closed && level
  === low) continue;`) and `surfacesOf(..., closed, ...)` in place of
  `surfacesOf(..., false, ...)`, so the no-op is textual rather than
  measured. It is also measured, twice over: the whole corpus replays with
  only `KinkedStop`'s nine floats moved (task 6.1), and **no corpus
  document carries a kinked jump level at all**, so this site cannot have
  touched one.
- **3.3** the kinked branch: breakpoints under the same `values` the level
  is read at; none → the whole piece solved (tested: the same fixture
  driven entirely inside its window); otherwise each sub-piece left to
  right, `closed` for all but the last, through the existing
  `deduplicated`.
- **3.4 the boundary.** The level reaches exactly 10 at `t = 0.75`, the
  window's own closing breakpoint: asserted located ONCE, at exactly
  0.75.

## Task 4 — the self-read walk (D4 (b))

- **4.1 RED, as a cost.** `run/cost.test.ts` gained
  `evaluationsPerTick` (the engine's own resolution probe, so the number
  is the same on any host) and the assertion that the committed
  `clearing` fixture costs under 4 000 evaluations/tick. Red at **32 004**
  on the base; red still at **20 388** with task 3 landed and the walk
  untouched; **GREEN at 2 724.0**, which is the prototype's number to the
  tenth.
- **4.2** `Walk.crossing` mirrors `_crossing`
  (`program.py:1346-1379`): published-affine both → unchanged; either
  shape unclassified → searched, unchanged; otherwise the SKELETON's
  breakpoints first (`skeletonCuts`), each cut again by the LEVEL's
  (`levelCuts`, located INSIDE that skeleton sub-piece with the driven
  coordinate interpolated between its two ends), solved left to right,
  `closed` for all but the very last sub-piece of the very last skeleton
  piece. The three-way is read off the STORED shapes; no classification
  happens inside the walk.
- **4.3** `Walk.run` gained `cutting`, and the skeleton's kinks are
  pushed into the cut list only when it is set — `retainedCuts` sets it,
  `retainedIncrement` does not (`program.py:1202`'s own rule). Tested on
  a kinked-skeleton variant of the committed `clearing` bench (the
  setter's contribution clamped into a window, which is what the Curta's
  clearing interface does): the ordinary tick and the cutting call give
  the same increment, the cutting call costs strictly more resolutions,
  and the breakpoint appears in the cuts.
- **4.4** The same bench: the breakpoint the path passes appears in NO
  crossing record, and the cut list stays sorted with 0 first and 1 last.

## Task 5 — the stop (D4 (c))

- **5.1 RED, as an IDENTITY.** `KinkedStop`'s own corpus scenario, driven
  through `Run` and asserted `Object.is`-exact against the producer's
  three floats:

  ```
  FAIL  src/run/run.test.ts > a stop on a kinked determiner (design D4 (c))
        > 5.1 lands on the producer's own fraction EXACTLY
  AssertionError: expected 0.47812500000009095 to be 0.478125
  ```

  The strong trap is named in the test's comment as a NUMBER: the
  coordinate runs 4 → 76 over the tick, so an `edgeCuts` that returns
  `[]` for a plan-less law divides once and puts the stop at
  `(40 - 4) / 72 = 0.5`, where the coordinate is standing on its flat
  piece for the first 0.3375 of the tick. GREEN at exactly `0.478125`,
  with `lever` exactly `119.125` and `h0` admitting exactly `19.125`.
- **5.2** `locate` takes the solved path where the published flag is true
  OR the derived shape is `'kinked'`. A second test on a local
  `clamp(crank, 0, 100)` bench bounded at 40, starting on the flat piece:
  the stop is the breakpoint-bracketed division, to the bit, and not the
  single division's 0.6.
- **5.3** `edgeCuts` for a law with NO plan returns `kinkedEndCuts` — its
  own kinks over the tick as one piece — and `[]` where none is reached.
  The invariant "empty cuts means affine over the whole tick" has its own
  test: the same bench driven entirely inside the sloped piece stops at
  exactly `(40 - 10) / 40`.
- **5.4** `planCuts` unions the skeleton's kinks into the partition,
  located inside each piece with that piece's branches substituted.
  Tested on the corpus's own `Window` (`pinion.turn`, a `clamp01` window
  inside a `floor` partition) driven 100 → 500: the partition is
  `[0, 113.5, 124.75, 360, 473.5, 484.75, 500]` in crank, to 1e-12 — a
  reading that took the placeholder from the FIRST piece would have put
  no breakpoint in the second at all. And a tick entirely inside the
  window returns `[0, 1]`.
- **5.5** A stop on a BLOCK coordinate is still searched: `RangedBlock`'s
  loaded block edge carries `null` for every shape and `false` for every
  flag, its corpus entry replays bit for bit, and `cost.test.ts`'s
  searched-stop scenario is unmoved (261 → 269 ticks/s, inside its own
  spread).

## Task 6 — nothing else moves

- **6.1 the corpus, both ways.** `npx vitest run
  src/run/running-corpus.test.ts` green, and the float-for-float audit
  against the corpus's own recorded numbers (every banked value, every
  crossing `t` and level, every stop `t` and value, every command's
  admitted travel, over all 20 scenarios and 360 ticks):

  | | base (`c0bb200`) | this implementation |
  | --- | --- | --- |
  | floats compared | 2 018 | 2 018 |
  | not bit-identical to the producer's | **9** | **0** |

  and a direct diff of the two audit runs shows **exactly nine entries
  changed**, all `KinkedStop`'s: the stop fraction
  `0.47812500000009095` → `0.478125`, the `lever` bank value
  `119.12500000000364` → `119.125` on all four ticks and `h0`'s admitted
  travel `19.125000000003638` → `19.125` on all four. Nothing else in 360
  ticks moved by one bit, in either direction.
- **6.2 the machines with no kink**, asserted in `cost.test.ts` as
  equalities and not floors: `Clearing` **471.1**, `Train` **31.0**, the
  Curta carriage **5 913.2** evaluations/tick, before and after, to the
  tenth.
- **6.3 case E.** `max(0, sin(x))` classifies as nothing
  (`expressions.test.ts` and a bench in `jumps.test.ts`), and the SAME
  call over the SAME bench costs **278** subexpression resolutions here
  and **278** on the base tree — verified by running the same test file
  against a copy of the base `src/` in the scratchpad, not by assertion.
- **6.4** `src/running-corpus.json` is untouched by this cycle:
  `git status --short` lists ten modified files and it is not among them.
- **6.5** `run/cost.test.ts`: the `clearing` fixture's floor raised from
  150 to **900** (acceptance §8's number; measured 1 312-1 324 ticks/s
  here against 342 on the base), with the old and new numbers in the
  comment beside it. Every other floor left exactly as it was. The
  scenario's title changed from "searches" to "SOLVES", which is now what
  it does.

## Task 7 — the suite, the types and the record

- **7.1** `npx tsc --noEmit` clean. `npx vitest run`: **37 files, 999
  tests, all green** (base 963; 36 new). `node build.mjs`:
  `dist/solid-widget.js`, 749.3kb — rebuilt, gitignored, nothing to
  commit there (ADR-059). No `npm ci`, no `npm install`, no
  `scripts/check-dist`.
- **7.2** `docs/adrs/EXPORT/ADR-061-a-kink-is-a-cut-in-the-viewer-too.md`,
  with the row added to `docs/adrs/README.md` in chronological order.
  **Deviation from tasks 7.2, on the apply briefing's instruction:** the
  ADR is **Draft**, not Accepted — this cycle's reviewer accepts it, as
  the previous cycles' reviewers did. It records, as tasks 7.2 asks, the
  one place it contradicts ADR-123's Consequences (the viewer CAN
  re-derive the shape), the 815- and 73-flag agreements, the 9 → 0 corpus
  floats, the `clearing` fixture's 11.7×, the Curta's unchanged numbers
  and the three deferrals.
- **7.3** `CHANGELOG.md`, one bullet under `0.2.0 — unreleased`.
- **7.5** `openspec validate solve-at-the-kink --strict` green. The
  change is NOT archived and nothing is committed: left for the reviewer,
  as the previous cycles left it.

## The classification, measured on real documents

The only external check on a second implementation of the producer's
classification is the flag the document already carries.

| document | driven ends | jump levels | flags | disagreements |
| --- | --- | --- | --- | --- |
| the refreshed corpus's 20 documents | 39 | 34 | **73** | **0** |
| the five committed run fixtures | 47 | 110 | **157** | **0** |
| the operating Curta (`OperatingCurta`, version 7) | 268 | 547 | **815** | **0** |

and the Curta's census reproduces the producer's own published one to the
unit: 28 kinked plan-bearing skeletons (11 plain + **17 self-read**), 41
unclassified (26 + 15), 183 affine and 16 kinked plan-less laws, 532
affine and 15 kinked jump levels.

**The corpus's reclassified ends are the seven the static audit named**,
and no more: `Captured` `p1.lift`/`p2.lift`, `CarryLead` `tens.turn`,
`KinkedStop` `slide.travel`, `Remainder` `pinion.turn`, `Train`
`slide.travel`, `Window` `pinion.turn` (nine rows over 20 documents,
because three machines appear in more than one scenario). **No corpus
jump level is kinked at all**, and none of the seven is a self-read — so
exactly one recorded float could move, and exactly one did.

## The operating Curta: nothing, and the numbers

`projects/Calculators/Curta-Type-I-3x`'s own published document (the
cached `viewer.json` the previous cycle re-exported and verified section
by section), driven through this engine in node — 100 idle ticks, its own
`Turn crank`, 60 more, `dt = 1/240` — three runs of the base and three of
this implementation, bundled from the same tree with esbuild:

| | base | this implementation |
| --- | --- | --- |
| idle | 10.32 / 8.76 / 8.24 ms/tick | 8.16 / 8.64 / 8.76 ms/tick |
| crank | 44.04 / 37.10 / 39.65 ms/tick | 38.26 / 39.20 / 38.16 ms/tick |
| evaluations/tick, idle | **20 718** | **20 718** |
| evaluations/tick, crank | **268 968** | **268 968** |
| digest after 160 ticks (226 lines) | `7f7bc77a…` | `7f7bc77a…` |

All six digests hash identically. The wall clock is inside the host's own
spread in both directions: this cycle does not make that document faster
and does not claim to. (The proposal quotes 260 306 evaluations on a
crank tick from the prototype's own site-scoped instrumentation; the
number above is the shared `resolutions` probe, which also counts the
two-endpoint whole-graph evaluations per piece — the same convention
ADR-060's evidence recorded, and identical before and after.)

## Deviations from the design, and what they cost

1. **The design says the `clearing` fixture's "levels are affine" (§6
   case C). They are not: twelve of its jump levels are kinked.**
   Measured here: the fixture publishes 12 kinked levels (`_j0`, `_j1`,
   `_j4`, `_j5`, … — the `clamp01` window's own comparisons), and the
   jump-level site alone (task 3) took the fixture from 32 004 to 20 388
   evaluations/tick before the walk was touched. The design's conclusion
   is unaffected — the skeleton IS kinked, the walk IS what the rest of
   the gain comes from, and the final number is the prototype's 2 724 to
   the tenth — but the sentence attributing the whole of it to the
   skeleton is wrong, and this cycle's tests do not repeat it.
2. **The kink inventory and the breakpoint solve are split between the
   two modules the proposal's Impact list names**, rather than carried
   together in `expressions.ts` as the prototype's `KinkCuts` class did.
   The prototype's version inlined a second copy of `merged`; this one
   calls the one `merged`, which is why `merged` gained its `end`
   parameter at all (tasks 2.3).
3. **ADR-061 is Draft rather than Accepted** (apply briefing; tasks 7.2
   says Accepted).

Nothing else in the design was departed from. `closed` differs between
`crossingsOf` and `Walk.crossing` exactly as design D4 states, the level
cuts are located inside one skeleton sub-piece with the driven coordinate
interpolated between its ends, and the kink level is evaluated in
`program.ts` — the three places the apply briefing said to escalate if
they fought back, and none of them did.

## Follow-ups, with their numbers

- **A path-valued kink level.** Left on the plain evaluator, as the
  producer left `_KinkCuts` on `GraphValue.evaluate`. Re-measured here on
  the real implementation, not taken from the prototype: on the
  `clearing` fixture the kink levels are **960 of the remaining 2 724
  evaluations/tick, in 96 calls**, and **zero** on `Clearing`, `Train`,
  the Curta carriage and every corpus machine. Worth a cycle only with a
  document that demands it.
- **A classification per BRANCH.** What the operating Curta actually
  needs: a kink can pin a curved subtree to a constant on one of its
  pieces, which is exactly a cam through its dwell. ADR-123 defers it
  with its reasons; 15 of the Curta's 32 self-read skeletons and 26 of
  its 37 plan-bearing ones are unclassified today.
- **The block's stop.** A different obstruction and the producer's own
  deferral; `RangedBlock` is asserted not to move.
- **`run.ts`'s constraint search** still follows a quantity by sampling
  and is untouched by this cycle, exactly as ADR-060 left it.
