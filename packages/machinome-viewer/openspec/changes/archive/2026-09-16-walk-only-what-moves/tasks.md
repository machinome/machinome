## 0. Before anything else — measured on the base, at proposal time

- [x] 0.1 The base, recorded. Worktree
      `solid-node-viewer/WTs/curta-speed`, branch `curta-speed`, base
      `4be96e5` (package `0.2.0` unreleased, `solidNodeViewerApi: 16`,
      `solidNodeDocumentVersions: [1..7]`, highest ADR 059 in
      `docs/adrs/EXPORT`). Node v24.11.1, vitest 3.2.7.

      **Environment note for the applier.**
      `solid_node_viewer/widget/node_modules` is a SYMLINK to the primary
      checkout's, and it is POPULATED (78 entries). NEVER run `npm ci`,
      `npm install` or `scripts/check-dist` in this worktree: through the
      symlink they EMPTY the primary's. Run the suite as
      `cd solid_node_viewer/widget && npx vitest run`, the typecheck as
      `npx tsc --noEmit`, and the bundle as `node build.mjs`.
- [x] 0.2 The originating document, copied out of the project and read
      only: `projects/Calculators/Curta-Type-I-3x` (branch
      `direct-operation`, HEAD `9fb725f`), its own
      `_build_running/viewer.json` — version 7, 1 168 517 bytes, sha256
      `16fe9ce68e34e8ef85c11788a0dc5df0f34891ec5b5e79fb29176cb45cd5a2af`,
      208 coordinates, 268 law edges, 83 intermediates, 547 branch
      placeholders, 8 594 bindings, 148 pieces, limits
      `{crossing_tolerance 1e-12, subdivisions 64, bisection_rounds 64,
      max_crossings 1000, agreement 1e-9}`. NOTHING is written into that
      project. The copy lives in the scratchpad at
      `scratchpad/spikes/curta.json`.

      Its provenance is the pilot's own export of
      `simulation.running:OperatingCurta`, dated after the project's
      HEAD, and its census matches `workflow/warts.md`'s to the unit.
      Both framework cycles state that the published document does not
      change (ADR-123 §5, ADR-124 Consequences), so it is the current
      document either way. **The applier SHALL re-export it** —
      `PYTHONPATH="<curta>:<fw-worktree>" .venv/bin/solid build
      simulation/running.py`, output left in the project's ignored
      `_build_running/` — and record whether the bytes match, so the
      measurement rests on a document that was rebuilt rather than found.
- [x] 0.3 The base's cost on that document, three runs, in-thread under
      node, step `1/240`, 100 idle ticks then the document's own
      `Turn crank` instruction and 60 more:
      idle **18.27 / 19.13 / 19.32 ms per tick** (20 513 DAG nodes
      computed per tick); crank **156.70 / 160.61 / 161.63 ms per tick**
      (1 428 635 per tick). The wart's own numbers, reproduced.
- [x] 0.4 Attribution by site, `node --cpu-prof`, nearest enclosing
      evaluation site (`scratchpad/spikes/attribute.py`):
      idle — `branchesAt` 44.4 %, `levelAt` 19.4 %, `blockIncrements`
      17.5 %, `advance` 7.2 %, the self-read walk 0.1 %, other 11.5 %;
      crank — `skeletonAt` 66.6 %, `levelOfJump` 13.1 %, `branchesAt`
      5.9 %, `blockIncrements` 2.4 %, `levelAt` 3.1 %, other 8.9 %.
      By SELF time `nest` is 40.6 % idle and 16.0 % crank; `mapsEqual`
      2.9 % and 2.9 %; `foldedNames` 9.8 % and 2.1 %.
- [x] 0.5 The structural ratio that decides the mechanism: of the
      fifteen self-read skeletons this document actually evaluates,
      **1 560 of 9 951 interned DAG nodes move** along a tick's path
      (15.7 %; 104 of 680 for the first). ADR-124's own figures on the
      Python side were 57 of 511 and 4 of 203.
- [x] 0.6 The document's own census through `loadProgram`: 223 entries,
      2 blocks, 47 members, 425 selectors, 22 free plans, 28 jumps
      outside the blocks, **32 laws that read the coordinate they
      drive**, 10 constraints, 0 published-affine plans. Over 20 crank
      ticks every skeleton evaluation (40 040), every level evaluation
      (40 624) and every search (600) is under 15 of those 32.
- [x] 0.7 The two mechanisms this cycle does NOT take, measured rather
      than assumed — ADR-123's classification re-implemented and
      validated against the producer's published census (28 kinked / 41
      unclassified, reproduced exactly), then applied: 17 of the 32
      self-read skeletons are KINKED and 15 are unclassified, and 100 %
      of the evaluations of 0.6 are under the unclassified fifteen. The
      producer's refreshed corpus adds exactly one scenario,
      `KinkedStop`, and replays GREEN through the UNCHANGED base engine.
      Both recorded in `proposal.md`'s Non-goals.

## 1. The path value (`src/expressions.ts`)

- [x] 1.1 RED: a test that a `PathValue` over a real published
      expression answers, at a point of a piece it has BOUND, the same
      float `valueOf` answers for the same values — and at a point of the
      SAME piece after binding, the same float again. Fails because there
      is no `PathValue`.
- [x] 1.2 `PathValue(root, moving, bindings)`: `bind(values)` walks the
      whole graph in postorder, computing every node and storing the
      value of every node that does not move; `at(values)` walks only the
      moving nodes, in the same postorder, reading a standing child back
      from the bind. Both dispatch through the SAME `applyUnary`,
      `applyBinary`, `readMember` and OpenSCAD `context` the whole-graph
      `compute` uses (design D1). Structure is decided in the FIRST
      bind's own walk and never again (D2); a later bind re-stores the
      standing values without re-deciding.
- [x] 1.3 A name node that the bindings table defines has that binding's
      root as its ONE child, so it moves exactly when the binding does
      and its value is that root's (D3). `$t` is a constant of the run's
      scope and stands.
- [x] 1.4 A qualified id is read from `values` by its whole dotted id
      (D4). A name in neither `values` nor the bindings table falls
      through to the OpenSCAD context, exactly as `resolveName` does.
      Review amendment — state the order exactly: a name node's FIRST
      part is checked against `$t` and the bindings table as
      `resolveName` does (with a binding's root as the node's child,
      1.3); otherwise the WHOLE dotted id is looked up in `values`;
      otherwise a single-part name falls through to the OpenSCAD
      context; a multi-part name absent from `values` whose first part
      is neither `$t`, a binding nor a context name is REFUSED loudly
      (1.5) and the caller falls back — it is the one shape where flat
      and nested resolution could differ, and `assertNestable` says no
      loaded program has it. A `member` node (`expr.name`, D9) is
      refused the same way; the originating document and the corpus
      carry none, which the differential test of 1.8 confirms.
- [x] 1.5 An unsupported node kind — a ternary, an array, an object, an
      index, a short-circuit binary — is REFUSED loudly by the path value
      rather than guessed (D9), and the caller falls back to
      `evaluateExpression`. Test: the refusal names the kind; test: a
      plan whose skeleton carries one still integrates, through the
      fallback.
- [x] 1.6 Every node the path value computes charges the resolution probe
      (D8). Test: `expressionMetrics().resolutions` rises by the moving
      count for a second point of a bound piece, and by the total for the
      bind.
- [x] 1.7 `movingNames(delta)`: the names whose increment is non-zero.
      Exported beside `PathValue`; nothing else.
- [x] 1.8 A differential test, against COMMITTED fixtures only — the
      corpus's own documents and `tests/fixtures/{clearing,carriage,
      lock}/viewer.json`, never the originating project's export: over
      every followed quantity those documents publish and a real set of
      bank values, `PathValue` and `valueOf` agree on the ROOT at every
      point of a piece, `Object.is` exact. This is the test that keeps
      the two evaluators one thing (design "Risks", last bullet), and it
      is what makes the suite's independence from the framework hold.

## 2. The self-read walk (`src/run/jumps.ts`)

- [x] 2.1 RED: a test that pins D6 — a walk asked for a point of a piece
      under one `branches` object and then under another must not read
      the first piece's standing values. Written against a corpus machine
      with more than one piece per tick (`Clearing` at `dt = 0.05`, the
      scenario that caught the producer's own `id()` bug), asserting the
      committed bank tick by tick. Prove it red by binding once and
      never re-binding.
- [x] 2.2 `Walk` builds ONE `PathValue` for `reading.outer.skeleton` over
      the walk's moving names, and one per DEPENDENT jump over those
      names PLUS the driven coordinate (D5). `skeletonAt` and
      `levelOfJump` bind when the `branches` object changes and take a
      point otherwise; the walk keeps every `branches` object it builds
      alive for its own lifetime (D6).
- [x] 2.3 `levelOfJump` keeps `levelOf`'s refusal rules unchanged: a
      non-finite level refuses the tick with the same message, whichever
      evaluator produced it.
- [x] 2.4 GREEN: 2.1, plus `run/jumps.test.ts` and `run/run.test.ts`
      unchanged and green.

## 3. The plan partition (`src/run/jumps.ts`)

- [x] 3.1 RED: a test that the level of a jump is evaluated from a
      standing part belonging to its OWN piece — the partition's
      equivalent of 2.1, against a machine whose partition has several
      pieces and whose level reads a switched source (`ShiftedCarry`).
- [x] 3.2 `LevelPaths(program, moving)`: one `PathValue` per jump
      placeholder, a monotonic `newPiece()` token, and `value(jump,
      piece, values, …)` binding when the token changed and taking a
      point otherwise (D6, D7).
- [x] 3.3 `partition` builds one when its caller does not supply one, and
      threads it through `branchesAt` (a fresh token per one-shot point),
      `crossingsOf`, `bisect` and `levelAt`. `planIncrement` builds ONE
      for its partition and its per-piece `branchesAt` together. `Walk`'s
      outer layer builds ONE for the whole walk and passes it to
      `outerCuts` and `outerBranches`.
- [x] 3.4 The signatures stay internal: `LevelPaths` is exported from
      `jumps.ts` only for its own tests, and no engine entry point
      (`planIncrement`, `planCuts`, `retainedIncrement`, `retainedCuts`,
      `blockIncrements`, `blockCuts`) changes its published shape.
- [x] 3.5 GREEN: 3.1, plus the whole of `src/run/`'s suite.

## 4. The proof that nothing moved

- [x] 4.1 The conformance corpus, replayed: every scenario of the
      COMMITTED `src/running-corpus.json` green, exactly as on the base.
      This is the contract, and a disagreement is a bug in this change.
- [x] 4.2 The originating document, bit for bit: 100 idle ticks, the
      `Turn crank` instruction, 60 more ticks; the whole bank, every
      recorded crossing and every stop written out and compared with the
      base engine's. Expected: **byte-identical, 213 lines**, on three
      runs. The prototype's own digests are in the scratchpad at
      `spikes/out/b{1,2,3}.txt` and `p{1,2,3}.txt`.
- [x] 4.3 `npm test` and `npx tsc --noEmit` in the widget: green, with
      the file and test counts recorded against the base's.
- [x] 4.4 `node build.mjs`: the bundle rebuilt and its size recorded.
      ADR-059 keeps it current; do not commit a stale one.

## 5. The cost, asserted

- [x] 5.1 `run/cost.test.ts`: the measured floors below, each an order of
      magnitude under the prototype's number so the test catches a
      tenfold regression and never a slow machine. Prototype against
      base, same bench:
      `Train` 164 138 → 182 211; the Pascaline 34 555 → 33 734;
      `CarryLead` affine 87 831 → 98 358 and forced-to-search 14 397 →
      24 216; `Captured` 123 857 → 140 186; the lock idle 18 532 →
      19 027 and advancing 148 → 150; `Clearing` 6 170 → **10 570**;
      the Curta fixture at `1/240` 211 → **300**; `ShiftedCarry` quiet
      4 375 → **7 895**, frozen twin 6 891 → **11 666**, crossing 2 208 →
      **3 822**; the Curta carriage at `0.02` 298 → **699**;
      `RangedBlock` quiet 27 333 → 26 655 and searched stop 252 → 261.
      Raise a floor ONLY where the gain is unambiguous; leave the two
      that do not move (the lock advancing, `RangedBlock`'s searched
      stop) exactly where they are — they are `run.ts`'s constraint
      search, which this cycle does not touch, and an unmoved number is
      the evidence for that.
- [x] 5.2 A test asserting the STRUCTURAL claim rather than a rate: for
      a machine with a followed quantity whose sources mostly stand, the
      node visits of a second point of a piece equal the MOVING count,
      and the moving count is a minority of the total. Through the probe,
      never through elapsed time.
- [x] 5.3 The small-machine guard, stated: `Train` and the Pascaline must
      not regress beyond this bench's spread. If either does on the
      applier's host, report it rather than lowering the floor.

## 6. The record

- [x] 6.1 `docs/adrs/EXPORT/ADR-060-only-what-moves-along-a-step-s-path-is-walked.md`:
      Accepted, dated, depending on ADR-043 (the shared DAG this is a
      view of), ADR-046 (the nested scope this steps around for a
      followed point), ADR-047/ADR-057/ADR-058 (the walk, the selection
      and the block whose evaluation sites these are), and citing
      solid-node's ADR-124 as the mechanism this mirrors and ADR-123 as
      the one it deliberately does not. Record the measured before/after,
      the moving-node ratio, the bit-identity evidence, and the three
      deferred cycles with their numbers.
- [x] 6.2 `docs/adrs/README.md`: the new row, chronological.
- [x] 6.3 `CHANGELOG.md` under `0.2.0 — unreleased`: one bullet — a
      quantity followed along a step's path is evaluated as a path, the
      operating Curta's tick falling 4× with every value unchanged.
- [x] 6.4 `workflow/warts.md`: the scope-rebuild entry gains its
      after-measurement — `nest` 40.6 % → 11.2 % of an idle tick and
      16.0 % → 3.4 % of a crank tick — and its triage moves to "largely
      retired by ADR-060; the remainder is not worth a cycle on this
      document". The entry is NOT deleted: its second cost, the abandoned
      memo across run expressions, stands.
- [x] 6.5 `evidence.md` for this change: §0's measurements with the after
      numbers beside them, the re-export of task 0.2 and whether the
      bytes matched, the digests of 4.2, any deviation from this design
      and why, and the follow-ups — the kink cut, the corpus refresh,
      `run.ts`'s constraint search, and the per-piece classification and
      compiled cone the producer holds.
- [x] 6.6 `openspec validate walk-only-what-moves --strict` green, and
      the change archived under its dated name after implementation — the
      ARCHIVE left for the reviewer, as the previous cycles left it.
