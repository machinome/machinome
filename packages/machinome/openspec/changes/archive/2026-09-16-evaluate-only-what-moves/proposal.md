## Why

Under a running root the engine follows a quantity along the tick's path
by evaluating its expression graph over and over: 64 samples per piece in
a search, two per piece in a solve, one per surface in a partition. Each
of those evaluations is a fresh postorder walk of the WHOLE graph
(`GraphValue.evaluate`), including every node whose value cannot possibly
have changed, because nothing it reads moves on this tick.

For a machine of a few parts that is invisible. For a machine whose laws
reach through seventeen chained dials it is the entire cost. The
originating project is the Curta: `projects/Calculators/Curta-Type-I-3x`,
branch `direct-operation`, HEAD `9fb725f`, whose `OperatingCurta` is
correct but not interactive — the finding Astra filed in
`workflow/warts.md` as "Originating Curta follow-up: seconds per Python
tick (2026-09-15)". `cut-at-the-kink` (ADR-123) measured the shape of
that cost and stated plainly that it did not claim to move it; this cycle
takes it up, with the attribution that change handed over.

**Measured on this worktree** at head `c3f3348`, three 0.1-s ticks of
`simulation.tools.running_probe --ticks 3` (commands and full tables in
design.md §2):

| where the tick's 3.27 s goes | share |
| --- | --- |
| `GraphValue.evaluate` | **83.7 %** (14 173 calls/tick, 230 nodes/call) |
| `declared_ports`, through `Run.bind` | 12.5 % |
| everything else | 3.8 % |

and inside that, 77.6 % of the whole tick is **two call sites** — the
skeleton (55.1 %) and the level (22.5 %) a self-read walk's search
evaluates, 64 samples at a time.

The decisive number is not how many evaluations there are. It is how much
of each evaluation is recomputation of a constant:

| quantity a search follows | nodes in the graph | nodes that MOVE on the path |
| --- | --- | --- |
| the walk's skeleton | 511 | **57 (11.2 %)** |
| the jump's level | 203 | **4 (2.0 %)** |

The run already knows exactly which sources move: `delta` is its own, and
a piece's branch reading is fixed by construction. So 89 % of every
skeleton evaluation and 98 % of every level evaluation is the interpreter
recomputing, sixty-four times, a number that stands.

## What Changes

**A quantity followed along a tick's path is evaluated as a PATH, not as
an expression.** Where the run must evaluate one compiled graph more than
once over one path with one branch reading, it SHALL compute the part of
that graph that cannot change — every node none of whose sources move —
ONCE, and evaluate only the moving cone per point.

- The moving names are the run's own: a source whose `delta` entry is
  non-zero, plus the driven coordinate where a self-read level is handed
  its own value per sample. Everything else — including a branch
  placeholder, which is a constant of the piece by construction — stands.
- The arithmetic is unchanged, node for node and operator for operator.
  A standing node's value is the same float whether it is computed once
  or sixty-four times, so **every answer is bit-identical**. Proved
  end-to-end: the Curta's committed snapshot after three ticks has the
  same SHA-256 with the path evaluation in place as without it
  (design.md §5, `spikes/endtoend_curta.py`).
- No new tolerance, no knob, no sampling decision, no declaration. An
  author writes nothing; a machine whose laws are small pays a
  classification walk it amortises over the same points it already
  evaluates.

### Measured result

| measure | today | with this change |
| --- | --- | --- |
| `OperatingCurta`, seconds per 0.1-s tick | 3.279 / 3.273 | **0.727 / 0.727** (**4.5×**) |
| its committed snapshot after three ticks | `dda09193…` | `dda09193…`, identical |
| `CurtaInterface` node visits per tick | 7 958.6 | falls; its 602.6 evaluations/tick do NOT |
| `Clearing` evaluations per tick | 98.6 | 98.6, exactly |
| `Train` evaluations per tick | 8.0 | 8.0, exactly |

The prototype that produced those numbers is `spikes/endtoend_curta.py`:
it replaces `_Walk`'s two evaluation sites and nothing else, and it
carries the bit-identity check across 2 600 captured evaluations of the
Curta's own graphs (`spikes/proto_eval.py`: 0 mismatches).

### What must not move

- **`tests/running-corpus.json`, byte-identical**, all 19 scenarios. No
  crossing, stop, landing or branch reading moves by a ulp: this change
  removes recomputation, it does not re-associate arithmetic.
- **Every published document, byte for byte.** No document field, no
  `affine` flag, no version. The path evaluation is internal to the
  Python run and the compiled program is not touched.
- `Train` 8.0 evaluations/tick and `Clearing` 98.6 evaluations/tick,
  **exactly** — the pins `cut-at-the-kink` set. The same samples are
  taken at the same points; only the cost of taking one falls. The
  framework's cost probe grows a companion that counts NODE VISITS, the
  unit that actually moves.
- `tools/bench_selection.py`'s six numbers within their repeats' spread,
  `RangedBlock`'s 16.0 ms/tick included.
- **A small machine must not pay for this.** `Clearing`'s followed graphs
  are six nodes; the first point of a piece is the build, so nothing is
  walked that would not have been walked anyway. `Train` at 2 119 ticks/s
  within its spread and `Clearing` no more than 10 % below its 1 433 are
  acceptance pins, not hopes.
- The retained-state, selection, stop, landing, refusal and transactional
  semantics, whole.

## Non-goals

- **The port enumeration, which becomes the biggest single cost once this
  lands, is a DIFFERENT mechanism and is explicitly deferred.**
  `declared_ports(node_class)` is a pure function of a class, re-walked
  from `Run.bind` every tick and from the constructor thousands of times,
  recursing through `__getattr__` on every declared child. Measured here
  because the proposal must say where the remaining seconds are:
  memoising it alone takes the Curta's construction from 5.44 s to
  **1.98 s** and its tick from 3.27 s to 2.82 s; together with this
  change the tick is **0.294 s** and construction 2.08 s. It belongs to
  `solid_node/motion/ports.py`, it needs its own answer to when a class's
  enumeration may be trusted to stand, and it is a separate cycle
  (design.md §8). Nothing here makes it easier or harder.
- **A per-PIECE classification** — `cut-at-the-kink` design.md §8, which
  recorded that "nothing has measured what it would buy". This cycle
  measures it (`spikes/perpiece_curta.py`): substituting every kink whose
  level keeps one sign over the piece would make **192 of the Curta's 200
  searched skeletons** solvable — 160 constant, 32 kinked, 8 still
  curved. It is not taken, for three stated reasons (design.md §7): it
  MOVES a crossing that is searched today to the solved answer, so it is
  not the bit-identical change this one is; it makes the classification
  depend on which piece you are in, which ADR-123 deliberately kept
  static; and **after this change its remaining prize is small** — the
  searched path is 21 % of the post-change tick, against the port
  enumeration's 56 %.
- **A stop on a BLOCK coordinate** (ADR-122's open wart). A block search
  re-runs the block's MEMBERS, not one graph along one path, so the seam
  this change adds does not reach it. `RangedBlock`'s tick cost is
  asserted unchanged.
- **The viewer.** Its TypeScript run has the same interpreter shape and
  would take the same win, but no document, no flag and no answer
  changes, so nothing is owed to it by this cycle. Recorded as a
  finding for solid-node-viewer, not proposed here.
- **Compiling a graph to a Python closure.** Measured (design.md §6 C):
  3× faster again than the path evaluation on the same graphs, still
  bit-identical — and it puts run-time `exec` of generated source into
  the engine for a term that is no longer the tick's biggest. Rejected
  for this cycle and recorded.
- **Making the Curta interactive.** 4.5× is not interactive; 0.727 s is
  still seven ticks a second. The proposal says which two mechanisms
  stand between here and there, in the order their measurements put them.

## Impact

- Affected specs: `simulation` — ONE ADDED requirement ("Only what moves
  along a tick's path is evaluated") and no MODIFIED one. Nothing an
  existing requirement promises changes: the crossings, the stops, the
  branch readings, the sub-interval count, the tolerance and even the
  COUNT of evaluations a tick pays are all unmoved, which is why the
  cost contract is a requirement of its own rather than a sentence
  amended into four others.
- Deliberately UNAFFECTED specs: `export`. No document field, no flag, no
  version; a published program is byte-identical.
- Affected code: `solid_node/simulation/program.py` — a new `_PathValue`
  beside `_KinkCuts`, and its use at `JumpPlan._level` / `_level_at` /
  `_branches` / `_searched` / `_solved` and at `_Walk._skeleton` /
  `_Walk._level` / `_skeleton_cuts` / `_level_cuts`.
- Affected tests: `tests/base.py` (a node-visit probe beside
  `expression_evaluations`), `tests/test_running_reads.py`,
  `tests/test_running_jumps.py`, `tests/test_running_stops.py`,
  `tests/clearing_project/machine.py` (one new fixture that pays what the
  Curta pays), `tests/test_running_corpus.py` (byte-identity).
- One ADR, **ADR-124** (NODE), extracted after implementation: only what
  moves along a tick's path is evaluated. It extends ADR-107's tick
  integration and ADR-121's two-layer walk without amending either's
  behaviour.
- Originating project: `projects/Calculators/Curta-Type-I-3x`, branch
  `direct-operation`, HEAD `9fb725f`, read-only throughout.
