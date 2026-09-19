## 1. Red: reproduce the finding on this tree

- [x] 1.1 Run `spikes/path_baseline.py 3` from the worktree root with
      `WT="$PWD" OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
      PYTHONPATH="$PWD"` and paste the output into `evidence.md`.
      Expect `Train` 8.0 evaluations / 40.0 node visits per tick,
      `Clearing` 98.6 / 589.8, `CurtaInterface` 602.6 / 7 958.6.
- [x] 1.2 RED (the wart): from the originating project, read-only,
      `python -m simulation.tools.running_probe --ticks 3` against this
      worktree. Expect construction ≈ 5.3 s and ticks ≈ 3.3 / 2.9 / 3.4 s.
      Confirm `git status --short` in that project is `M pyproject.toml`
      and `?? screenshots/` before and after, and never write there.
- [x] 1.3 RED (attribution): `spikes/split_curta.py 3` and
      `spikes/callsites_curta.py`. Confirm `GraphValue.evaluate` is
      **83.7 %** of the tick and `declared_ports` 12.5 %, that
      construction is 61 % `declared_ports` and 0 % evaluation, and that
      **77.6 % of the tick is the two `_Walk._searched` sites** — while
      the 39 % of EVALUATIONS that ADR-123 left as "elsewhere" is about
      1 % of the seconds.
- [x] 1.4 RED (the decisive number): `spikes/cone_curta.py`. Confirm the
      searched skeleton is 511 nodes of which **57 move (11.2 %)** and
      the searched level 203 of which **4 move (2.0 %)**.
- [x] 1.5 RED (bit-identity of the mechanism, before writing any of it):
      `spikes/proto_eval.py`. Confirm 2 600 captured evaluations of the
      Curta's own graphs agree to the BYTE across the current walk, the
      path evaluation and the compiled path, and record the per-
      evaluation figures (348.6 / 17.9 / 6.0 µs).
- [x] 1.6 RED (end to end): `spikes/endtoend_curta.py plain 3` and
      `... patched 3`, twice each. Record the tick seconds (≈ 3.27 and
      ≈ 0.727) and confirm the snapshot SHA-256 is
      `dda09193d0e45d4f2778df86ca548177d8e4aa6ba6d5dc2bf91d4c6292da3c8e`
      in every run. Run `NOSTRUCT=1 ... patched 3` too and record that
      dropping the cross-tick structure cache costs 5 % — the measurement
      design.md §3.3 rests on.
- [x] 1.7 RED (the suite): time `simulation/test_running.py` and
      `simulation/test_running_clearing.py` from the originating project
      against this worktree, with `--durations=12`, and record the total
      and the five `RunningCurtaTest` durations. This is the baseline the
      acceptance ratio is taken against, and it MUST be re-measured in
      the same session as the after run (the machine's load moved these
      numbers by 25 % during the proposal).
- [x] 1.8 RED (the rejected alternative, measured): `spikes/perpiece_curta.py`.
      Record that a per-piece classification would make **192 of 200**
      searched skeletons solvable (160 constant, 32 kinked, 8 curved),
      and that this is the number `cut-at-the-kink` design.md §8 asked
      for.

## 2. The path value

- [x] 2.1 Add `_PathValue` to `solid_node/simulation/program.py`, beside
      `_KinkCuts`, per design.md §3.1: `__slots__`, a structural stage
      built from `(graph, moving names)` and a per-piece stage that
      computes the standing nodes from that piece's inputs. `at(values)`
      walks only the moving nodes, in the SAME postorder, through the
      SAME operator objects `GraphValue.evaluate` uses, and returns the
      root's value. A graph with no moving node returns its standing root
      without walking.
- [x] 2.1a The FIRST point of a piece is the build (design.md §3.1): the
      first `at` walks the whole graph exactly as `GraphValue.evaluate`
      does, deciding each node's moving boolean and keeping each standing
      node's value in that same walk. No separate classification pass, so
      a quantity followed at one or two points is not slower for it.
      `Clearing`'s ticks/s is the pin that holds this (task 6.4).
- [x] 2.2 The docstring states the contract in the spec's words: what
      stands is computed once, the arithmetic is unchanged node for node,
      and the value is the same float the whole-graph walk gives.
- [x] 2.3 The moving set is taken from the run, never inferred: a source
      with a non-zero `delta` entry, and — stated explicitly, in one
      place, with the comment saying why — the driven coordinate for a
      SELF-READ LEVEL, which `_Walk.__init__` zeroes in `delta` on
      purpose. A branch placeholder is never in it.
- [x] 2.4 NO cache outlives the tick (design.md §3.3, measured at 5 %).
      A path value is built where the tick's path is known and dropped
      with it; nothing keyed by graph identity survives an `increments`
      call.

## 3. The call sites

- [x] 3.1 `_Walk`: build the skeleton's path value and one per dependent
      jump's level once per walk; re-bind the standing values per PIECE,
      on that piece's `branches`. `_skeleton` and `_level` ask the path
      value. Keep `_level`'s `ZeroDivisionError` and non-finite refusals
      exactly where they are — `_no_level` must still be raised from the
      same place with the same message.
- [x] 3.2 `JumpPlan`: `_level`, `_level_at`, `_branches`, `_solved` and
      `_searched` take path values built once per `increment` and re-bound
      per piece on `inner`.
- [x] 3.3 `_skeleton_cuts` / `_level_cuts` (`_KinkCuts.between`) are LEFT
      on `GraphValue.evaluate` this cycle (review amendment): a kink's
      LEVEL is a separate sub-graph (`_kink_level` builds a new `a - b`
      node for `min`/`max`), so it cannot share the skeleton's or the
      jump level's path value, and on the originating machine every
      kinked level is a three-node graph. Say so in a comment at
      `_KinkCuts.between` and record the residue under task 10.1.
- [x] 3.4 Leave alone, and say so in a comment where it is not obvious:
      `_evaluated` (one evaluation per law per tick end, nothing to
      amortise), `Run._locate` / `_piecewise` / `_searched_constraint`
      (they re-run a SUB-PROGRAM, not one graph along one path),
      `_Block`'s member integration, `_land` and every landing
      arithmetic, `Program.published()` and `_along`.

## 4. The cost probe

- [x] 4.1 `tests/base.py`: `expression_evaluations` must count a path
      evaluation's point as ONE evaluation, so that `Clearing`'s 98.6 and
      `CurtaInterface`'s 602.6 per tick stand exactly. Its docstring says
      why the probe now has two things to count.
- [x] 4.2 `tests/base.py` gains `graph_node_visits(sim, ticks)` beside
      it: the postorder steps a run charges, the unit this change moves.
      Its docstring says that an evaluation count can no longer tell a
      cheap evaluation from an expensive one, and that this is the probe
      that can.

## 5. The fixture and the red tests

- [x] 5.1 `tests/clearing_project/machine.py` gains the fixture of
      design.md §9 A: a self-read law whose skeleton carries the real
      detent-cam arithmetic (`sin`, `cos`, `sqrt` of
      `max(0, abs((phase + 2) % 36 − 18) − dwell)`) over a phase that
      reads the driven coordinate AND a chain of sibling coordinates the
      tick does not move, deep enough that the skeleton is several
      hundred nodes of which a dozen move. Keep it the SMALLEST thing
      that pays what the Curta pays, and say in its docstring which
      project law it reproduces.
- [x] 5.2 RED (case A): `graph_node_visits` per tick of that fixture,
      asserted under a fifth of the number measured on this tree. Record
      the red number in `evidence.md`; node visits are deterministic, so
      this is a pin and not a timing test.
- [x] 5.3 RED (case B): a golden — the fixture's committed bank, its
      recorded crossings and its landings after a dozen ticks, taken from
      the UNPATCHED tree and asserted exactly. It must be written before
      `_PathValue` is used anywhere.
- [x] 5.4 RED (case D): a test-only checking path value in `tests/` —
      never a framework flag — that recomputes the standing part at every
      point and asserts it equals the cached value, run over the running
      fixture set. Prove it RED against a deliberately wrong moving set
      (drop the driven coordinate from a level's moving names) and green
      otherwise.
- [x] 5.5 RED (case C): `Clearing` at exactly 98.6 evaluations/tick and
      `Train` at exactly 8.0 through `expression_evaluations`, plus their
      node visits; assert that an implementation leaving the probe
      counting only `GraphValue.evaluate` fails them.
- [x] 5.6 A piece's branches do not leak: a fixture whose tick is cut
      into several pieces with a different branch on each, asserting the
      standing part is rebound per piece (design.md §11, second risk).

## 6. Nothing else moves

- [x] 6.1 `tests/running-corpus.json` byte-identical for all 19
      scenarios (`git diff --stat` empty), and `tests/test_running_corpus.py`
      green including `BlockOrderTest`.
- [x] 6.2 `Program.published()` byte-identical for every running fixture;
      no document field, no `affine` flag, no version.
- [x] 6.3 `tools/bench_selection.py 5`: the six numbers within their
      repeats' spread, `RangedBlock` at 16.0 ms/tick.
- [x] 6.4 `spikes/path_baseline.py 3` after: `Train` 8.0 evaluations and
      40.0 node visits per tick exactly, `Clearing` 98.6 evaluations
      exactly with its node visits fallen, `CurtaInterface` 602.6
      evaluations exactly with its node visits fallen. **And the small-
      machine guard**: `Train` at 2 119 ticks/s within the repeats'
      spread and `Clearing` no more than 10 % below its 1 433 — the pin
      that says a six-node graph did not start paying for a mechanism it
      cannot use (design.md §11).
- [x] 6.5 The five named regression files, then the whole suite,
      sequential, one job: `tests/test_couplings.py`,
      `tests/test_running_simulation.py`, `tests/test_running_jumps.py`,
      `tests/test_running_stops.py`, `tests/test_running_reads.py`,
      `tests/test_running_document.py`, `tests/test_running_corpus.py`.

## 7. Acceptance, in Astra's units

- [x] 7.1 `running_probe --ticks 3` from the originating project,
      read-only: **≤ 1.20 s per 0.1-s tick** (expected ≈ 0.73), against
      the 3.27 s of task 1.2.
- [x] 7.2 `spikes/endtoend_curta.py plain 3` after the change must give
      the SAME snapshot SHA-256 as `patched` did and as the unpatched
      tree did: `dda09193d0e45d4f2778df86ca548177d8e4aa6ba6d5dc2bf91d4c6292da3c8e`.
      If it does not, STOP: the change has moved a committed value and
      the design says it cannot.
- [x] 7.3 `simulation/test_running.py` + `simulation/test_running_clearing.py`
      re-measured in the same session as task 1.7's re-run: **≤ 1/3** of
      that baseline.
- [x] 7.4 Construction is NOT claimed: record it and say so. If it has
      moved outside its spread either way, say which way and why.

## 8. Documentation

- [x] 8.1 `docs/architecture.md`, Simulation section: one paragraph on
      what a tick evaluates and what it computes once, beside the
      jump-plan and self-read accounts. Add `_PathValue` to the Map.
- [x] 8.2 `docs/architecture.md`, "Known gaps and tensions": the
      per-PIECE classification bullet is no longer "unmeasured" — give it
      design.md §7's 192 of 200 and the reason it still waits. Add a
      bullet for the port enumeration (§8) with its numbers, and one for
      the viewer's own whole-graph walk.
- [x] 8.3 `docs/driving.rst`: extend `cut-at-the-kink`'s "What a law
      costs under a running root" with what a law costs when it reaches
      through a long chain of parts that stand — in an author's terms,
      with no promise of a number.
- [x] 8.4 `HISTORY.rst`: an Unreleased entry in the voice of the two
      above it. No breaking note; no document version moves.
- [x] 8.5 `workflow/warts.md`: Astra's "Originating Curta follow-up:
      seconds per Python tick" entry becomes **TAKEN UP as
      `evaluate-only-what-moves` (ADR-124)** with the before and after
      numbers, and records the TWO deferred mechanisms with their
      measurements — the port enumeration (§8: construction 5.46 → 1.98 s,
      tick 3.27 → 2.82 s alone, 0.294 s with both) and the per-piece
      classification (§7: 192 of 200). Both stay OPEN and named.
- [x] 8.6 A finding for solid-node-viewer: its TypeScript run has the
      same whole-graph walk and would take the same win, with no document
      change owed. Recorded in `workflow/warts.md`, not proposed here and
      not written into that repository.

## 9. The ADR

- [x] 9.1 Draft `docs/adrs/NODE/ADR-124-only-what-moves-along-a-tick-s-path-is-evaluated.md`
      and its `docs/adrs/README.md` index line, with the measured
      before/after, the bit-identity argument and its proof, the moving
      set as the run's own statement, the no-cache decision and its 5 %
      measurement, and the two deferrals. Extends ADR-107 and ADR-121;
      amends neither's behaviour.
- [x] 9.2 Promotion is the reviewer's direction: leave it a DRAFT until
      the cycle's review says so.

## 10. Findings

- [x] 10.1 Record in `workflow/warts.md`, under this cycle, anything met
      while applying that is outside the ratified scope — in particular
      the `_along` residue (a fresh source dict per point, 17 % of the
      post-change tick together with the walk's own bookkeeping) and the
      compiled-closure measurement (58×, design.md §6).
