# ADR-124: Only What Moves Along a Tick's Path Is Evaluated

**Status:** Accepted
**Date:** 2026-09-16
**Depends on:**
- [ADR-107: A jump is located inside the tick and subtracted](./ADR-107-a-jump-is-located-inside-the-tick-and-subtracted.md) — the partition whose crossings this amortises
- [ADR-121: A law may read the coordinate it drives](./ADR-121-a-law-may-read-the-coordinate-it-drives.md) — the two-layer self-read walk whose two evaluation sites this rewrites
- [ADR-123: A kink is a cut, and a piecewise-affine quantity is solved](./ADR-123-a-kink-is-a-cut.md) — measured the shape of this cost and stated plainly that it did not move it
**Extends (amends neither's behaviour):**
- [ADR-107](./ADR-107-a-jump-is-located-inside-the-tick-and-subtracted.md) — the tick's own integration is unchanged; only the cost of one evaluation inside it falls
- [ADR-121](./ADR-121-a-law-may-read-the-coordinate-it-drives.md) — the two-layer walk's own points and branches are unchanged; only how each is evaluated
**OpenSpec change:** `evaluate-only-what-moves`

## Context and Problem Statement

`GraphValue.evaluate` (`solid_node/scad_expression.py`) is the run's one
numeric evaluator: it builds an operator table and walks the whole graph
in postorder, computing every node. Under a running root that walk is
not asked once. `_Walk._searched` takes 64 samples of a piece and
evaluates, at each, the law's SKELETON and a dependent jump's LEVEL.
`JumpPlan._partition` evaluates a level at every cut and every midpoint.
Nothing in that loop tells the evaluator what the loop already knows:
along ONE tick's path, with ONE branch reading, almost nothing in the
graph changes. `_along(start, delta, t)` moves exactly the names whose
`delta` entry is non-zero; a branch placeholder is a constant of the
piece by construction; the driven coordinate of a self-read is handed
its own value explicitly. Everything else is the same float at every
sample, and was recomputed at every sample.

The originating project is the Curta: `projects/Calculators/Curta-Type-I-3x`,
branch `direct-operation`, HEAD `9fb725f`, whose `OperatingCurta` is
correct but not interactive — filed by `cut-at-the-kink` (ADR-123) as
"Originating Curta follow-up: seconds per Python tick". ADR-123 measured
the shape of the cost and explicitly declined to move it. Measured on
this worktree at ADR-123's own head: three 0.1-s ticks of
`simulation.tools.running_probe --ticks 3` cost 3.279 / 3.273 s, of which
83.7 % is `GraphValue.evaluate` (14 173 calls/tick, 230 nodes/call), and
77.6 % of the WHOLE TICK is two call sites — `_Walk._searched`'s
skeleton (55.1 %) and level (22.5 %) evaluations. The decisive
measurement: of a searched skeleton's 511 nodes, only 57 (11.2 %) MOVE
along the path; of a searched level's 203 nodes, only 4 (2.0 %). The run
already knows exactly which names move — it built `delta` — so 89–98 %
of every evaluation was the interpreter recomputing a number that
stands.

## Decision

A quantity followed along a tick's path, over one compiled graph
evaluated more than once with one branch reading, is evaluated as a
PATH: the part of the graph that cannot change — every node none of
whose sources move — is computed ONCE, from the piece's own inputs, and
only the moving cone is evaluated per point.

`solid_node/simulation/program.py` gains `_PathValue`, beside
`_KinkCuts`. Structure — which nodes move — is decided in the SAME
postorder walk `GraphValue.evaluate` would have made for the piece's own
first point (`bind`), so a quantity followed at one point costs what it
cost before plus a boolean per node in a walk it was going to make
anyway; every later point of the same piece (`at`) walks only the
moving nodes, reading a standing child back from the value the piece
bound. A graph with no moving node returns its standing root without
walking. Both methods dispatch through the SAME operator table
`GraphValue.evaluate` uses, so a node's value is the identical float
either evaluator gives.

The moving names are the run's own statement, never inferred: a source
whose `delta` entry is non-zero, plus — for a LEVEL only, because
`_Walk.__init__` deliberately zeroes it in `delta` — the driven
coordinate of a self-read. A branch placeholder is never in it. `_Walk`
builds one path value for the skeleton and one per dependent jump's
level, once per walk, re-bound per piece on `branches`; `JumpPlan`'s own
`_level`, `_level_at` and `_branches`, reached through a new
`_LevelPaths`, build one per jump per `increment`/`cuts` call (or per
walk, for the outer layer), re-bound per piece on `inner`. A kink's own
level (`_KinkCuts.between`) stays on `GraphValue.evaluate`: it is a
different sub-graph, on the originating machine always three nodes, and
sharing a path value with the skeleton or jump level it sits inside is a
residue recorded, not taken.

No cache outlives the tick: a `_PathValue`/`_LevelPaths` is built where
the path is known and dropped with it. Measured at 5 % on the end-to-end
prototype (disabling a cross-tick structure cache costs 0.766 s/tick
against 0.727 s with it) — cheap enough that removing every question
about when a cached structure goes stale is free.

A piece is identified by a monotonic token, never by a dict's `id()`.
The first implementation keyed a piece by `id(branches)`/`id(inner)`; a
transient piece dict is unreferenced the moment the caller moves to the
next piece, and CPython is then free to hand a LATER, unrelated piece
the exact same address once the earlier one is collected. That bug
reproduced on `Clearing`'s own corpus scenario before this ADR's
implementation was accepted, moving a committed coordinate by exactly
100. `_LevelPaths` now hands out a strictly increasing integer per
piece; `_Walk` instead keeps every `branches` dict it ever builds alive
for the walk's own lifetime, which makes `id()` safe again by
construction.

## Considered Options

- **Compile the moving cone to a Python closure** (`exec` of generated
  source). Measured 58× against the current walk on the Curta's own
  captured evaluations, bit-identical, 3× faster again than the path
  value taken here — but it puts run-time code generation into the
  engine for a term this change already leaves at under a fifth of the
  patched tick, and its own build cost needs a cross-tick cache the
  measurement above shows is unnecessary. Rejected for this cycle;
  recorded (`workflow/warts.md`) so a later one has the number.
- **Cache an evaluation by `(graph, input values)`.** Hashing the input
  dict per sample costs more than the walk it would avoid, and answers
  nothing about the standing nodes. Rejected.
- **Classify a followed quantity per PIECE rather than per tick**
  (`cut-at-the-kink` design.md §8's open question, measured here: 192 of
  200 of the Curta's searched skeletons would become solvable). Rejected:
  it MOVES a crossing located by search to the solved answer — every
  recorded crossing would move — and makes the classification depend on
  which piece you are in, which ADR-123 deliberately kept static. Its
  remaining prize after this change is small (21 % of the post-change
  tick against the port enumeration's 56 %). Recorded, not taken.
- **Lower `_SUBDIVISIONS`.** Cheaper and less exact, in a way that
  depends on sample-count luck; the pilot's own constraint and
  ADR-123's reasoning both rule it out.
- **A knob** — an opt-in, a cache size, a "fast evaluation" flag.
  Unnecessary: the moving set is structural and the run already owns
  it; forbidden by the pilot's constraint besides.

## Consequences

- Every crossing, landing, branch reading, increment, stop, refusal and
  committed value a machine gave before this ADR is the value it gives
  now, to the byte: proved on the Curta's own committed snapshot after
  three ticks (`dda09193d0e45d4f2778df86ca548177d8e4aa6ba6d5dc2bf91d4c6292da3c8e`,
  identical with and without the change) and on the whole 19-scenario
  conformance corpus (byte-identical).
- `OperatingCurta`'s tick falls from 3.279/3.273 s to 0.727/0.727 s
  (4.5×) on this worktree; the framework's own `simulation/test_running.py`
  + `test_running_clearing.py` fall from 843.18 s to 274.17 s.
  `Train` and `Clearing`'s EVALUATION COUNTS are pinned exactly (8.0 and
  98.6 per tick); their NODE VISITS fall (`Clearing` 589.8 → ~357/tick on
  this worktree's fixtures) and their ticks/s do not regress —
  `Clearing` is, if anything, faster, which is the small-machine guard
  this ADR's acceptance held it to.
- No document field, flag or version moves: the path evaluation is
  internal to the Python run and the compiled program is untouched.
- Two mechanisms remain the biggest costs after this change and are
  explicitly deferred to their own cycles: `declared_ports`'s lack of a
  per-class memo (56 % of the post-change tick) and the per-piece
  classification rejected above (21 %). Both are recorded in
  `workflow/warts.md` with their measured numbers.
- The viewer's TypeScript run has the same whole-graph-walk shape and
  would take the same win, with no document or flag change owed to it —
  a finding for solid-node-viewer, not proposed here.

## Promotion

Accepted 2026-09-16 at the cycle's adversarial review: the reviewer
re-ran the regression files, the Curta probe (0.78 / 0.73 / 0.74 s per
tick) and the end-to-end snapshot (SHA-256 identical) on the
implemented tree.
