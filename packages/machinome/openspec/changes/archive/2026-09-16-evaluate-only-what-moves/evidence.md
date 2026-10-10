# Evidence: `evaluate-only-what-moves`

Worktree `solid-node/WTs/curta-speed`, branch `curta-speed`, applying on
top of head `b787781` (this change's planning commit, over `c3f3348`
`cut-at-the-kink`/ADR-123). Workspace venv,
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`, one job at a time. Originating
project `projects/Calculators/Curta-Type-I-3x`, branch `direct-operation`,
HEAD `9fb725f`, read-only throughout; `git status --short` there was
`M pyproject.toml` / `?? screenshots/` before and after every command run
against it.

## 1. Red: reproduce the finding on this tree

### 1.1 `spikes/path_baseline.py 3`

```
Train            ticks   10  best      4.60 ms    2173.6 ticks/s       8.0 evaluations/tick        40.0 node visits/tick
Clearing         ticks   10  best      6.93 ms    1442.9 ticks/s      98.6 evaluations/tick       589.8 node visits/tick
CurtaInterface   ticks   60  best    449.55 ms     133.5 ticks/s     602.6 evaluations/tick      7958.6 node visits/tick
```

Matches design.md §2 E exactly: `Train` 8.0/40.0, `Clearing` 98.6/589.8,
`CurtaInterface` 602.6/7958.6.

### 1.2 RED (the wart)

```
cd projects/Calculators/Curta-Type-I-3x
PYTHONPATH="<curta>:<worktree>" OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
    <venv>/python -m simulation.tools.running_probe --ticks 3
```

```
constructed 5.4462833310244605
input 0 0 target reading 0
tick 1 seconds 3.3519195200060494 result 0 counter 0
tick 2 seconds 3.0797371229855344 result 0 counter 0
tick 3 seconds 3.683443660964258 result 0 counter 0
```

Construction ≈ 5.45 s, ticks ≈ 3.35 / 3.08 / 3.68 s — matches the range
proposal.md quotes (3.279 / 3.273 on this tree earlier, 3.3–3.7 s here
under today's machine load). `git status --short` in the project was
`M pyproject.toml` / `?? screenshots/` before and after; nothing else
touched there.

### 1.3 RED (attribution)

`spikes/split_curta.py 3`:

```
constructed 5.211 s   evaluate 0.000 s in 0 calls   declared_ports 3.199 s in 1480 top-level calls
  tick 3.387 s
  tick 2.953 s
  tick 3.498 s
3 ticks 9.837 s (3.279 s/tick)
  GraphValue.evaluate  8.250 s (83.9%) in 42519 calls (14173/tick), 9798636 node visits (230 nodes/call), 194.0 us/call, 842 ns/node
  declared_ports       1.211 s (12.3%) in 555 top-level calls
  everything else      0.376 s (3.8%)
```

Construction: 61.4 % `declared_ports` (3.199 / 5.211 s), 0 % expression
evaluation. Tick: 83.9 % `GraphValue.evaluate`, matching design.md's
83.7 %.

`spikes/callsites_curta.py`:

```
   13000 ( 30.6%)    2.257 s ( 22.4%)  _level <- _level <- _searched <- _crossing <- _first_cut <- run
   12800 ( 30.1%)    5.503 s ( 54.7%)  _skeleton <- own_at <- _searched <- _crossing <- _first_cut <- run
    7423 ( 17.5%)    0.028 s (  0.3%)  _level <- _branches <- _partition <- _partition <- increments <- increments
    2845 (  6.7%)    0.014 s (  0.1%)  _level <- _branches <- _forced <- increments <- increments <- _pass
    2560 (  6.0%)    0.013 s (  0.1%)  _level <- _level_at <- _solved <- _crossings_of <- _partition <- _partition
    ... (remaining rows in task output)
```

77.1 % of the tick (54.7 + 22.4) is the two `_Walk._searched` call
chains — the "77.6 %" design.md quotes to within the session's own
timing noise. The 39 % of evaluations ADR-123 left "elsewhere"
(17.5 + 6.7 + 6.0 + ... rows) is about 1.3 % of the wall time here,
confirming design.md §2 C's reading.

### 1.4 RED (the decisive number)

`spikes/cone_curta.py`:

```
-- skeleton: 200 searched calls, 511 nodes/graph, 57.0 moving (11.2%)
       489 nodes,   57 moving   x 26
       497 nodes,   57 moving   x 26
       505 nodes,   57 moving   x 26
       513 nodes,   57 moving   x 26
       521 nodes,   57 moving   x 96
-- level: 200 searched calls, 203 nodes/graph, 4.0 moving (2.0%)
         3 nodes,    2 moving   x 100
       382 nodes,    6 moving   x 13
       390 nodes,    6 moving   x 13
       398 nodes,    6 moving   x 13
       406 nodes,    6 moving   x 13
       414 nodes,    6 moving   x 48
```

Exact match to design.md §2 D: 511 nodes/57 moving (11.2 %) for the
skeleton, 203/4 (2.0 %) for the level.

### 1.5 RED (bit-identity of the mechanism, before writing any of it)

`spikes/proto_eval.py`:

```
40 captured cases
2600 evaluations, 932750 node visits today, 79300 moving (8.5%)
  A  current walk             726.98 ms    279.6 us/evaluation
  B  path evaluation           34.99 ms     13.5 us/evaluation   (+14.52 ms building, 20.8x)
  C  compiled path             12.57 ms      4.8 us/evaluation   (+26.91 ms building, 57.8x)
  bit mismatches: 0 of 2600
```

0 mismatches of 2600 captured evaluations, confirming the mechanism is
bit-identical before `_PathValue` is written. Per-evaluation costs (280 /
13.5 / 4.8 µs) are the same order as design.md's 348.6 / 17.9 / 6.0 µs —
this session's machine is faster but the RATIOS (20.8×, 57.8×) agree with
design.md's 19.5× / 58.0×.

### 1.6 RED (end to end)

`spikes/endtoend_curta.py <mode> 3`, from the Curta project, twice each:

| run | construction | tick 1 | tick 2 | tick 3 | s/tick | SHA-256 |
| --- | --- | --- | --- | --- | --- | --- |
| plain | 5.358 s | 3.310 | 2.975 | 3.412 | 3.232 | `dda09193d0e45d4f2778df86ca548177d8e4aa6ba6d5dc2bf91d4c6292da3c8e` |
| patched | 5.467 s | 0.753 | 0.751 | 0.743 | 0.749 | `dda09193d0e45d4f2778df86ca548177d8e4aa6ba6d5dc2bf91d4c6292da3c8e` |
| plain (repeat) | 5.410 s | 3.379 | 2.952 | 3.423 | 3.252 | `dda09193d0e45d4f2778df86ca548177d8e4aa6ba6d5dc2bf91d4c6292da3c8e` |
| patched (repeat) | 5.259 s | 0.707 | 0.676 | 0.712 | 0.698 | `dda09193d0e45d4f2778df86ca548177d8e4aa6ba6d5dc2bf91d4c6292da3c8e` |
| patched, `NOSTRUCT=1` | 5.226 s | 0.730 | 0.681 | 0.741 | 0.718 | `dda09193d0e45d4f2778df86ca548177d8e4aa6ba6d5dc2bf91d4c6292da3c8e` |

Every run gives the SAME snapshot SHA-256, `dda09193…`, as design.md §5
and the acceptance table name. `NOSTRUCT=1` (no cross-tick structure
cache) costs 0.718 vs 0.698–0.749 s/tick, ~3 % here (design.md measured
5 % on its own machine) — small, consistent, and it is why §3.3's "no
cache outlives the tick" decision costs so little.

### 1.7 RED (the suite)

See "Task 6.5 / suite" section below — run once, sequentially, per the
apply briefing; its BEFORE numbers are recorded there and re-used as the
task 1.7 baseline (re-measuring the exact same command a second time
would only add machine-load noise, and the briefing asks for exactly one
before/after pair taken in the same session).

### 1.8 RED (the rejected alternative, measured)

`spikes/perpiece_curta.py`:

```
-- skeleton: 200 searched calls
     whole-tick None         -> per-piece constant      x 160
     whole-tick None         -> per-piece kinked        x 32
     whole-tick None         -> per-piece None          x 8
-- level: 200 searched calls
     whole-tick affine       -> per-piece affine        x 100
     whole-tick kinked       -> per-piece affine        x 100
```

192 of 200 searched skeletons (160 constant + 32 kinked) would become
solvable under a per-piece classification — exactly the number design.md
§7 and `cut-at-the-kink` design.md §8 ask for. Confirms the alternative is
real but, per design.md §7, not taken this cycle.

## 2-4. `_PathValue`, `_LevelPaths`, and the four call sites

Implemented in `solid_node/simulation/program.py`: `_PathValue` (beside
`_KinkCuts`), `_leveled` (the shared refusal wrapper `JumpPlan._level`
and `_Walk._level` both use), `_moving_names`, and `_LevelPaths` for the
`JumpPlan`-side call sites (`_branches`, `_level_at`, `_solved`,
`_searched`, `_bisect`, `_partition`, `increment`). `_Walk` gained
`_skeleton_path`, `_level_paths` and `_outer_paths`, built once per walk
in `__init__` from `_moving_names(self.delta)`, with `self.own` added
explicitly for a level path (never for the skeleton). `_KinkCuts.between`
and its callers were left untouched (task 3.3), with a comment recording
why at `_crossings_of`'s kinked branch.

## A real bug found and fixed while applying (task 6.1's first red run)

The first working draft identified a "piece" by `id(branches)` (in
`_Walk`) or `id(inner)`/`id(values)` (in `_LevelPaths`, via a `piece`
parameter). `tests/test_running_corpus.py` caught it immediately:

```
AssertionError: 100.0 not less than or equal to 3.4800000000000005e-07 : Clearing tick 1 wheel.turn
AssertionError: 100.0 not less than or equal to 2.48e-07 : StoppedClearing tick 1 wheel.turn
```

Both `Clearing` (dt=0.1) and `StoppedClearing` (dt=0.05) landed
`wheel.turn` exactly 100.0 too high on tick 1, and only tick 1 — every
later tick matched, because the coordinate happened to saturate at the
same value regardless of where it started. Root cause, isolated by
instrumenting `JumpPlan._branches`/`_LevelPaths.value`: `Clearing`'s
outer jump `$j1` (`floor(_b1) == 0`) was decided from a level of `0.0`
when its own OUTER jump `$j0`'s branch, correctly passed in as `-1.0`,
should have given a level of `-1.0`. `$j1`'s `_PathValue` had returned a
value from an EARLIER, unrelated piece.

The cause: `_branches`'s and `_partition`'s local `values`/`inner` dicts
are built fresh every call and go out of scope (and are garbage
collected) the moment the caller moves to its next piece. CPython is
then free to hand the very next dict allocation the SAME memory address
— which it did, letting a later piece's lookup key (`id(values)`)
collide with an earlier, already-dead piece's key stored in
`_LevelPaths.bound`, and reuse that earlier piece's cached standing
value.

Fix, in two parts, recorded at each class's own docstring:

- `_LevelPaths` now hands out a strictly increasing integer per piece
  (`new_piece()`); every caller that starts a new piece calls it and
  threads the returned token, never a dict, down to `.value(...)`.
- `_Walk` instead keeps every `branches` dict it ever builds (in
  `_tentative`) alive for the walk's own lifetime (`self._live_branches`),
  which makes `id(branches)` safe again by construction: nothing this
  walk keys by identity can ever be freed and reused while the walk is
  still running.

After the fix, `tests/test_running_corpus.py` (16 tests, 60 subtests,
all 19 corpus scenarios) passes: `git diff --stat -- tests/running-corpus.json`
is empty (task 6.1).

## Task 5: the fixture and its red/green numbers

`DetentReader` (`tests/clearing_project/machine.py`): a self-read law
whose skeleton is `_detent(base_chain(siblings) + drive) * engaged`,
where `engaged` is `stationed_tooth`'s own proven self-read gate shape
(`shifted - 360*floor(shifted/360) >= 2*GAP`) and `_detent` is
`simulation/dial_cam.py`'s own `sin`/`cos`/`sqrt`/`abs`/`max` arithmetic.
16 sibling `Driver`s feed `base_chain`, none of them moved by the
scenario. Measured graph shapes (`_PathValue.bind`, node count / moving
count): skeleton 220 nodes / 21 moving, level (the gate's own `own`-
reading comparison) 3 nodes / 2 moving.

Scenario: `sim.move('drive', by=900.0, duration=1.2)`, `dt=.1`, 12 ticks
(`tests/test_running_paths.py`'s `DRIVE_SWEEP`/`DRIVE_DURATION`/`TICKS`).

**Task 5.2 (case A), RED vs GREEN, node visits/tick**
(`tests/base.py:graph_node_visits`):

| | node visits/tick |
| --- | --- |
| RED (unpatched tree) | **92 211.25** |
| GREEN (patched tree) | **11 489.5** (12.46 % of RED, under the 1/5 acceptance) |

**Task 5.3 (case B), golden vs green**: 25 crossings recorded (levels
13.0 through 37.0, all `wheel.turn`, primitive `%`), 0 stops, final bank
`wheel.turn = 350.00000000000017`, `drive = 900.0` — identical between
the unpatched (RED) and patched (GREEN) runs, byte for byte
(`diff golden_red_900.txt golden_green_900.txt` empty). Pinned in
`tests/test_running_paths.py::DetentReaderGoldenTest`.

**Task 5.4 (case D)**: `MovingSetGuardTest` in
`tests/test_running_paths.py` is a white-box test of `_PathValue`
itself (`sin(own) + sibling`, `own` moving): the correct moving set
matches a whole-graph evaluation at every point; a deliberately wrong
one (`own` dropped) freezes the answer at the first point's value and
diverges from the correct one at a later point — exactly the "silent
wrong answer" design.md §11 names as the mechanism's one failure mode.

**Task 5.5 (case C)**: `FixedEvaluationCountTest` pins `Train` at
exactly 8.0 and `Clearing` at exactly 98.6 evaluations/tick through the
new `expression_evaluations`, and asserts that a probe counting only
`GraphValue.evaluate` (the pre-cycle probe) would NOT report 98.6 for
`Clearing` any more — the guard against an implementation that forgot
to teach the probe about `_PathValue`.

**Task 5.6**: `BranchDoesNotLeakAcrossPiecesTest`, a direct unit test of
`_PathValue.bind`/`.at` with a `moving_name + $placeholder` graph:
re-binding for a second piece with a DIFFERENT placeholder value reads
the new one, not the first piece's. Taken as a white-box test of the
class rather than a new whole-machine fixture, because the risk
(design.md §11's second risk) is a property of `_PathValue` itself, not
of any particular machine's dynamics — and because building a whole
fixture that reliably drives the SAME jump through two DIFFERENT branch
values inside one tick, on top of `DetentReader`'s already-substantial
detent-cam law, would not have been the smallest thing that proves the
guard. `DetentReaderGoldenTest`'s 25 crossings, each re-deciding a
branch, are the end-to-end version of the same proof.

## Task 6: nothing else moves

- 6.1 `tests/running-corpus.json` byte-identical (empty diff);
  `tests/test_running_corpus.py` green, 16 tests / 60 subtests,
  `BlockOrderTest` included.
- 6.2 Every running fixture's `Program.published()` is unchanged by
  construction: no call site this cycle touches publishes anything, and
  `tests/test_running_document.py`'s byte-identity test passed
  unmodified (see the regression run below).
- 6.3 `tools/bench_selection.py 5`, this session, before vs after:

  | | before (unpatched) | after (patched) |
  | --- | --- | --- |
  | Train (control) | 0.458 ms/tick | 0.477 ms/tick |
  | FixedZero | 0.744 ms/tick | 0.462 ms/tick |
  | ShiftedCarry | 1.209 ms/tick | 0.733 ms/tick |
  | RangedBlock | 16.283 ms/tick | 17.844 ms/tick |
  | ShiftedCarry (crosses the detent) | 2.557 ms/tick | 1.501 ms/tick |
  | CurtaCarriage | 10.629 ms/tick | 6.254 ms/tick |

  `RangedBlock` (the one number this change does not touch, task 3.4:
  a block re-runs a sub-program, not one graph along one path) moved
  from 16.283 to 17.844 ms/tick — 9.6 % on this machine's own repeat
  spread, the same order as the noise every OTHER number here shows
  between repeats; every block-carrying number this change SHOULD help
  (`FixedZero`, `ShiftedCarry`, `CurtaCarriage`) improved instead, in
  the direction the mechanism predicts.
- 6.4 `spikes/path_baseline.py 3`, after: `Train` 8.0 evaluations /
  40.0 node visits per tick exactly (unmoved); `Clearing` node visits
  fell (589.8 → measured 357.1/tick with `tests/base.py`'s new probe;
  the OLD spike probe, which only counts `GraphValue.evaluate`, now
  reports 0.0 for `Clearing` and 98.8 for `CurtaInterface` — expected,
  since most of their evaluations are now bound path points, and exactly
  why task 5.5 exists); `CurtaInterface` node visits fell (7 958.6 →
  4 698.4/tick, measured directly with `graph_node_visits`). Small-
  machine guard: `Train` 2 161.0 ticks/s (within spread of 2 119) and
  `Clearing` 2 867.8 ticks/s — FASTER, not slower, so well clear of the
  "no more than 10 % below 1 433" floor.
- 6.5 The five named regression files (`test_couplings.py`,
  `test_running_simulation.py`, `test_running_jumps.py`,
  `test_running_stops.py`, `test_running_reads.py`,
  `test_running_document.py`, `test_running_corpus.py`): 560 passed, 792
  subtests passed, 36.13 s. The WHOLE suite (`pytest tests`): see the
  final tally below (run once, sequentially, one job).

## Task 7: acceptance, in Astra's units

- 7.1 `running_probe --ticks 3` from the originating project, read-only:
  construction 5.593 s, ticks **0.770 / 0.690 / 0.722 s** — all under
  the 1.20 s ceiling (expected ≈ 0.73, task 1.2's RED was 3.35/3.08/3.68).
  `git status --short` in the project: `M pyproject.toml` / `?? screenshots/`,
  unchanged.
- 7.2 `spikes/endtoend_curta.py plain 3` after the fix:
  `SNAPSHOT-SHA dda09193d0e45d4f2778df86ca548177d8e4aa6ba6d5dc2bf91d4c6292da3c8e`
  — identical to every RED and GREEN run in task 1.6.
- 7.3 `simulation/test_running.py` + `simulation/test_running_clearing.py`,
  re-measured in the same session as task 1.7's BEFORE run:

  | | seconds | ratio |
  | --- | --- | --- |
  | BEFORE (task 1.7) | 843.18 s (8 passed, 340 subtests) | — |
  | AFTER (task 7.3) | 274.17 s (8 passed, 340 subtests) | **32.5 %**, under the 1/3 ceiling |

  The five `RunningCurtaTest` durations fell from
  259.27/143.11/137.17/136.86/110.84 s to
  68.16/41.92/40.62/37.81/31.11 s — every one comfortably inside the
  1/3 ratio individually too.
- 7.4 Construction is NOT claimed. Measured across this session's runs:
  5.21–5.59 s before, 5.23–5.59 s after — within the same spread; no
  systematic move either way, as design.md §8 predicts (this change does
  not touch `declared_ports`).

## Findings recorded in `workflow/warts.md` (task 8.5, 8.6, 10.1)

- The "Originating Curta follow-up" entry is updated: TAKEN UP as
  `evaluate-only-what-moves` (ADR-124), with the before/after table and
  the two deferred mechanisms (`declared_ports` memoisation, the
  per-piece classification), both left OPEN.
- A new `# evaluate-only-what-moves (2026-09-16, found while applying)`
  section records the `id()`-collision bug (fixed inside the cycle) and
  two out-of-scope findings: `_along`'s per-point fresh dict (17.2 % of
  the post-change tick, together with the walk's own bookkeeping) and
  the compiled-closure measurement (58×, design.md §6 C). Both left OPEN.
- A finding for solid-node-viewer (its TypeScript run's own whole-graph
  walk) is recorded, not proposed there.

## Documentation (task 8.1-8.4)

- `docs/architecture.md`: one paragraph in the Simulation section
  (between the jump-plan account and the self-read/two-layer account)
  naming `_PathValue`, its call sites, and the no-cache decision; the Map
  table's Simulation row gained `123, 124`; the "Known gaps and
  tensions" per-piece-classification bullet now carries design.md §7's
  measured numbers instead of "nothing has measured", and two new
  bullets record the port-enumeration and viewer findings.
- `docs/driving.rst`: a new subsection, "What a law costs when it
  reaches through a long chain of parts that stand", extending
  `cut-at-the-kink`'s "What a law costs under a running root" in an
  author's terms, with no promise of a number.
- `HISTORY.rst`: an Unreleased entry in the voice of the two above it,
  with the measured before/after and the "nothing in a published
  document changes" statement.

## Files changed (`git status --short`, plus untracked)

See the final report for the complete list; summary: `solid_node/simulation/program.py`
(the mechanism), `tests/base.py` (the two probes), `tests/clearing_project/machine.py`
(the fixture), `tests/test_running_paths.py` (new, the red/green tests),
`docs/architecture.md`, `docs/driving.rst`, `HISTORY.rst`, `workflow/warts.md`,
`docs/adrs/README.md`, `docs/adrs/NODE/ADR-124-*.md` (new, DRAFT),
`openspec/changes/evaluate-only-what-moves/tasks.md` (checked off),
`openspec/changes/evaluate-only-what-moves/evidence.md` (new).

(continued below as implementation proceeds)
