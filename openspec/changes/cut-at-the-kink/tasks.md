## 1. Red: reproduce the finding on this tree

- [ ] 1.1 Re-run the five probes in this change's `spikes/` directory
      from the worktree root, one job at a time, with
      `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH="$PWD"` and
      `WT="$PWD"`, and paste every output into `evidence.md`:
      `kink_baseline.py 5`, `attribute_fixtures.py`, `classify.py` via
      `classify_fixtures.py`, `corpus_flip.py`, `exactness.py`. They are
      the proposal's and design.md's numbers; confirm each before
      changing a line.
- [ ] 1.2 RED (cost): `CurtaInterface` pays **2 861.3** `GraphValue`
      evaluations per tick and runs at **28.2 ticks/s**, against
      `Clearing`'s **98.6** and 1 528 and `Train`'s **8.0** and 2 288.
- [ ] 1.3 RED (attribution): **84.5 %** of `CurtaInterface`'s evaluations
      are in `_Walk._searched` under a kinked skeleton (56.8 %, 756
      calls) and `JumpPlan._searched` under a kinked level (27.7 %, 726
      calls). `Clearing` charges 0 % to either.
- [ ] 1.4 RED (exactness): the crossing of `result0`'s rack in tick 17 of
      the `CurtaInterface` sweep is recorded at `0.09999999999990905`
      where the fixture's own arithmetic gives `0.10000000000000231` —
      `9.3e-14` out, float spacing `1.4e-17`.
- [ ] 1.5 RED (blast radius): record the five corpus machines whose
      determiner is reclassified (`Captured`, `CarryLead`, `Remainder`,
      `Train`, `Window`), the ten stops the corpus records and the fact
      that none is on one of those coordinates — so
      `tests/running-corpus.json` must not change.
- [ ] 1.6 RED (the Curta): `running_probe --ticks 3` against this
      worktree from `projects/Calculators/Curta-Type-I-3x` (branch
      `direct-operation`, HEAD `9fb725f`, read-only) gives construction
      `5.300 s` and ticks `3.287 / 2.799 / 3.378 s`, with **100 %** of
      the searched evaluations under an UNCLASSIFIED skeleton and none
      under a kinked one. Record it as the number this change does NOT
      claim to move, and as the next cycle's attribution.

## 2. The classification

- [ ] 2.1 In `solid_node/simulation/program.py`, replace
      `_affine_in_sources` / `_degree_of` with a three-valued
      `_shape_of` (`'constant'` / `'affine'` / `'kinked'` / `None`) per
      design.md §4.1, keeping every existing propagation rule
      byte-for-byte and adding `'kinked'` only through `abs`, `min` and
      `max` over movable operands. Name the three kinks in a module
      constant beside `_JUMP_CALLS`, with the comment saying they are the
      CONTINUOUS selections of `SYMBOLIC_BUILTINS` and that each returns
      one of its operands exactly.
- [ ] 2.2 Keep `_affine_in_sources` as a thin "is it solvable" wrapper if
      that reads better, but every INTERNAL consumer must learn whether
      the answer needs SUB-DIVISION: `_Jump.affine` gains a companion
      (read at `program.py:481` and `:952`), `_Retained` gains one for
      the skeleton, and `Edge` carries the shape per driven end for
      `run.py:974`'s `edge.affine[index]`.
- [ ] 2.3 PUBLICATION IS NOT CHANGED. `Program._published_edge`
      (`program.py:2221`, `list(edge.affine)`) and `_published_plan`
      (`:3672`, `jump.affine`) keep emitting the TWO-valued flag the
      export spec defines, and a kinked quantity publishes `false`. If
      `Edge.affine` becomes the three-valued shape, the publication site
      maps it down explicitly, with the comment saying why (the viewer
      consumes the flag to choose solve vs search:
      `run/run.ts:851`, `run/jumps.ts:347`, `:779`). No `openspec/specs/
      export/spec.md` delta, no document field, no version bump.
- [ ] 2.4 Unit tests over `_shape_of` directly, as a table: every
      composition in `solid_node/math.py` (`clamp`, `clamp01`, `ramp`,
      `lerp`, `piecewise`, `wrap`, `bump`), each of the fourteen
      `SYMBOLIC_BUILTINS`, a product of two movers, a moving divisor, a
      power, a branch placeholder, and a kink over a curved operand
      (`max(0, sin(x))`, which must stay unclassified).

## 3. Locating the breakpoints

- [ ] 3.1 One routine that, given a graph, the path's `start`/`delta`,
      the fixed branch values and a bracket, returns the kink
      breakpoints strictly inside it, sorted and merged through the
      existing `_merged`: kinks in POSTORDER, each level solved from the
      endpoint values of the sub-intervals the earlier kinks produced.
      No sampling, no bisection, no new tolerance (design.md §4.2).
- [ ] 3.2 A level that does not move over a sub-interval contributes no
      breakpoint, stated in the code as it is in `_Walk._searched`.
- [ ] 3.3 Breakpoints are NOT crossings: assert in tests that they are
      absent from `sim.crossings`, do not count toward `_MAX_CROSSINGS`,
      and never reach `_Walk._land` (design.md §4.3).

## 4. The three solve sites

- [ ] 4.1 `JumpPlan._crossings_of`: sub-divide a KINKED level's piece at
      its breakpoints and interpolate on each sub-piece, right end
      inclusive for every sub-piece but the last, result through
      `_deduplicated`. Test a surface landing exactly on a breakpoint —
      once, not twice and not zero times.
- [ ] 4.2 `_Walk._crossing`: solve when the level and the skeleton are
      each affine-or-kinked, sub-dividing at the union of the SKELETON's
      breakpoints and the LEVEL's, skeleton first. The LEVEL's
      breakpoints ride `own_at`, which is affine only within a skeleton
      sub-piece, so locate them PER skeleton sub-piece with `own_at`
      evaluated at that sub-piece's two ends (design.md §4.4 (b)). Keep
      `_first_cut`'s
      "first surface strictly inside the piece" and `inclusive=False` at
      the piece's own left end.
- [ ] 4.3 `Edge._affine_ends` reports the new shape; `_Block._affine_ends`
      keeps returning `False` for every give, with its comment saying WHY
      this change does not lift it (design.md §7).
- [ ] 4.4 `Edge.cuts` returns the union of the plan's (or the walk's)
      cuts and the SKELETON's kink breakpoints, computed even where the
      edge carries NO jump plan. Compute the skeleton's breakpoints
      INSIDE each plan PIECE, with that piece's branch placeholder values
      substituted — the skeleton reads `$j` placeholders, which are
      constant only per piece — then union the per-piece lists with the
      plan's own cuts through `_merged` (design.md §4.4 (c)); a plan-less
      determiner has one piece, the whole tick. Return `()` when the
      determiner is kinked and
      no kink is crossed, so `Run._locate`'s one-division fast path stays
      exact. Assert that invariant — empty cuts means affine over the
      tick — in a test of its own.
- [ ] 4.5 `Run._locate` / `Run._piecewise`: unchanged in shape, exercised
      on the new cuts. Confirm no fourth tolerance appears anywhere.

## 5. The fixtures and the red tests

- [ ] 5.1 `tests/running_project/machine.py`: a fixture whose driven
      coordinate declares a `range` and is driven by a law with NO jump
      node whose value is `4 + 72 * clamp01((lever − 113.5) / 11.25)`,
      the bound on the SLOPED piece and the tick starting on the FLAT
      one. Restate the expected fraction from the fixture's own
      arithmetic in the test, never from the law.
- [ ] 5.2 RED then green, case C: the stop's fraction and the committed
      value. Record BOTH reds — the searched answer on this tree, and the
      answer a `Edge.cuts` that still returns `()` would give (patch it
      to measure, then revert the patch) — because the second is the
      materially wrong one this test exists to catch.
- [ ] 5.3 RED then green, case A (`tests/test_running_jumps.py`): a
      kinked jump level's crossing located within a few ulp of the
      closed-form answer.
- [ ] 5.4 RED then green, case B (`tests/test_running_reads.py`): the
      `CurtaInterface` tick-17 crossing within a few ulp, and the
      evaluations-per-tick assertion using the `graph_evaluations` probe
      already in `tests/test_running_stops.py` (lift it to a shared
      helper rather than copying it).
- [ ] 5.5 Case E: `max(0, sin(x))` and a product-of-two-movers level pay
      exactly what they pay today.
- [ ] 5.6 Case D: `Train` at exactly 8.0 evaluations/tick and `Clearing`
      at exactly 98.6, asserted, with `Clearing`'s committed values
      unchanged.
- [ ] 5.7 Case D, the DOCUMENT (`tests/test_running_document.py`),
      red-first against a plumbed-through implementation: a law with a
      kinked determiner and no jump publishes `affine: [false]`, and a
      kinked jump level publishes `affine: false`; and
      `Program.published()` for `Train` — whose `lever drives
      slide.travel` is one of the five reclassified determiners — is
      byte-identical before and after the change. This is the test that
      keeps the viewer from interpolating through a kink (design.md §9,
      §11 D).

## 6. The corpus

- [ ] 6.1 Add ONE scenario over the 5.1 fixture to
      `tools/generate_running_corpus.py`'s `CORPUS`, and one entry to
      `REQUIRED` — `'a stop on a kinked determiner inside a tick'` or
      the wording review settles — derived in `uncovered_features` from
      the committed ticks, in the shape `pin-the-block-order` used.
- [ ] 6.2 Regenerate with the tool (never by hand) and diff: expect
      `removed: []`, exactly one `added`, `changed: []`, and every
      pre-existing scenario byte-identical. If ANY existing byte moves,
      stop and report before continuing — §6 of design.md says it must
      not.
- [ ] 6.3 Confirm the new scenario's `document` publishes the version the
      tree already publishes: this change adds no document field and
      moves no version. Confirm too that its kinked law publishes
      `affine: [false]` — the new scenario is a document the viewer must
      still be able to replay by SEARCH.
- [ ] 6.4 `tests/test_running_corpus.py` still green, `BlockOrderTest`
      included.

## 7. Performance

- [ ] 7.1 Re-run `spikes/kink_baseline.py 5` and record the after table
      against design.md §12's acceptance: `CurtaInterface` ≤ 900
      evaluations/tick and ≥ 120 ticks/s; `Train` and `Clearing`
      unchanged exactly. If `CurtaInterface` lands BETWEEN 900 and
      2 861 evaluations/tick, that is neither a pass nor a fail: STOP,
      re-run `spikes/attribute_fixtures.py` for the attribution of what
      the solve now costs and where the residue is, and report both to
      the reviewer for a judgement (design.md §12). Do not adjust the
      acceptance numbers to fit the result.
- [ ] 7.2 Re-run `tools/bench_selection.py 5`: all six numbers within
      the repeats' spread, `RangedBlock`'s 16.1 ms/tick included.
- [ ] 7.3 Re-run `spikes/attribute_fixtures.py`: the two search rows are
      gone from `CurtaInterface` or reduced to the residue the solve
      leaves.
- [ ] 7.4 Re-run the Curta's `running_probe --ticks 3` against the
      implemented worktree, read-only, and record it honestly: within its
      own spread is the expected and acceptable result (design.md §3).
      Do not modify or commit anything in that project.

## 8. The suites

- [ ] 8.1 The five named regression files plus the corpus:
      `tests/test_couplings.py tests/test_running_simulation.py
      tests/test_running_jumps.py tests/test_running_stops.py
      tests/test_running_reads.py tests/test_running_document.py
      tests/test_running_corpus.py`.
- [ ] 8.2 The whole suite, sequential, one job:
      `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH="$PWD"
      python -m pytest tests -q -p no:cacheprovider`. Record counts
      against the before run.

## 9. Documentation

- [ ] 9.1 `docs/driving.rst`: which quantities the run SOLVES and which
      it SEARCHES, in an author's terms — a `clamp01`, `clamp`, `ramp` or
      `piecewise` profile is solved; a `sin`, a `sqrt` or a product of two
      moving quantities is searched; and what that costs.
- [ ] 9.2 `docs/scenarios.rst`: sweep its refusal and limitation lists,
      as `read-the-driven-coordinate`'s own finding says a capability
      cycle must, and correct anything that says a kinked law is
      searched.
- [ ] 9.3 `docs/architecture.md`: the Simulation section's account of the
      affine/searched decision, and REMOVE the "A kinked but piecewise
      affine skeleton falls to the search" bullet from "Known gaps and
      tensions". Leave the block-give bullet and add the per-branch gap
      (§8) in its place.
- [ ] 9.4 `HISTORY.rst`: the Unreleased entry, in the voice of the
      self-read and selection entries above it. No breaking note: no
      document version moves.
- [ ] 9.5 `workflow/warts.md`: the `read-the-driven-coordinate` entry "A
      kinked but piecewise-affine skeleton falls to the 64-sample search"
      becomes "Taken up as `cut-at-the-kink`" with the ADR number; the
      `select-the-source` restatement of the same finding likewise; the
      block-give entry is left open with a line saying this cycle
      examined it and found it a different mechanism.
- [ ] 9.6 AFTER implementation, under the reviewer's direction and in ONE
      pass: extract **ADR-123** (NODE) — a kink is a cut, and a
      piecewise-affine quantity is solved — AMENDING ADR-107's "where the
      level quantity is affine … otherwise sampled" and that sentence as
      restated by ADR-108, ADR-121 and ADR-122; update
      `docs/adrs/README.md` keeping its chronological order.

## 10. Out of scope, recorded

- [ ] 10.1 Record in the change's report, for the reviewer to file in
      `workflow/warts.md`: (a) classification per BRANCH would solve a
      curved subtree a kink pins to a constant on a piece — the Curta's
      cam dwell — and is measured evidence for the seconds-per-tick cycle
      (design.md §8); (b) the real `OperatingCurta`'s tick is 60.6 % in
      `_Walk._searched` under a cam skeleton carrying `sin`, `cos` and
      `sqrt` of a moving phase, half of it under a level that is itself
      affine (design.md §3); (c) the block-give wart stands, with §7's
      reason; (d) `Run._searched_constraint` still samples every bound
      that reads other coordinates, untouched here.
- [ ] 10.2 Record, for the reviewer to file in `workflow/warts.md` and
      to carry to the viewer repository at integration:
      (a) the viewer is not required to change for CORRECTNESS — it keeps
      searching a kinked quantity because the published `affine` flag
      stays `false` for one — and the two runtimes stay inside the
      corpus's `1e-9` window, with the one residual risk of design.md §9;
      (b) a viewer that wants the SOLVE cannot re-derive the shape from
      the document: it needs a new document field for the shape, or a
      redefinition of `affine`, under a document version bump — two
      changes in two repositories (the framework's export spec and the
      viewer's), which this cycle does not take;
      (c) adding the corpus scenario of 6.1 makes the viewer's
      byte-for-byte copy `solid_node_viewer/widget/src/running-corpus.json`
      STALE. Refreshing it and replaying it is the viewer repository's
      follow-up at integration, and its replay must locate the new
      scenario's stop by SEARCH — which is correct, and must land inside
      the corpus's comparison window;
      (d) the viewer MIRRORS the generator's `REQUIRED` list and its
      derivation by hand, in `widget/src/run/running-corpus.test.ts`
      (the `REQUIRED` array and `uncoveredFeatures`). The new feature's
      wording and the rule that derives it from a committed tick must be
      reproducible there from the document alone — check that before the
      wording is settled — and adding both to the viewer is part of the
      same follow-up as (c).
