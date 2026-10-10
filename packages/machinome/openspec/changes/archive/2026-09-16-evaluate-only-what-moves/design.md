# Design: only what moves along a tick's path is evaluated

## 1. The finding

`GraphValue.evaluate` (`solid_node/scad_expression.py:48`) is the run's
one numeric evaluator. It builds a fresh operator table, walks the whole
graph in postorder, and computes every node:

```python
values = {}
for node in postorder([self._expression_node]):
    args = [values[child] for child in node.children]
    ...
    values[node] = value
return values[self._expression_node]
```

Under a running root that walk is not asked once. It is asked once per
SAMPLE. `_Walk._searched` takes `_SUBDIVISIONS = 64` samples of a piece
and evaluates, at each, the law's SKELETON (through `own_at`) and the
jump's LEVEL. `JumpPlan._partition` evaluates a level at every cut and
every midpoint. `_solved` evaluates at two ends per sub-piece.

Nothing in that loop tells the evaluator what the loop already knows:
along one tick's path, with one branch reading, **almost nothing in the
graph changes**. `_along(start, delta, t)` moves exactly the names whose
`delta` entry is non-zero; a branch placeholder is a constant of the
piece by construction (`_Jump.placeholder`, substituted in
`_branches`/`inner`); and the driven coordinate is handed its own value
explicitly. Everything else is the same float at every sample, and is
recomputed at every sample.

## 2. The baseline, measured on this worktree

Worktree `solid-node/WTs/curta-speed`, branch `curta-speed`, head
`c3f3348` (`cut-at-the-kink`, ADR-123, applied). Workspace venv,
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`, one job at a time.
Originating project `projects/Calculators/Curta-Type-I-3x`, branch
`direct-operation`, HEAD `9fb725f`, read-only, dirty exactly as it was
(`M pyproject.toml`, `?? screenshots/`).

**A. The wart reproduced.**

```
cd <curta> && PYTHONPATH="<curta>:<worktree>" OPENBLAS_NUM_THREADS=1 \
    OMP_NUM_THREADS=1 <venv>/python -m simulation.tools.running_probe --ticks 3
```

```text
constructed 5.306886620994192
tick 1 seconds 3.3022828670218587 result 0 counter 0
tick 2 seconds 2.912890661973506 result 0 counter 0
tick 3 seconds 3.357798801967874 result 0 counter 0
```

Astra's own figures were 4.973 s and 3.3797 / 2.9304 / 3.3858; ADR-123's
were 5.300 and 3.287 / 2.799 / 3.378. Unmoved, as that cycle said.

**B. Where the tick's seconds are** (`spikes/split_curta.py 3`, wall-clock
wrappers, no profiler):

```text
constructed 5.368 s   declared_ports 3.265 s in 1480 top-level calls
3 ticks 9.621 s (3.207 s/tick)
  GraphValue.evaluate  8.056 s (83.7%) in 42519 calls (14173/tick),
                       9798636 node visits (230 nodes/call),
                       189.5 us/call, 822 ns/node
  declared_ports       1.202 s (12.5%) in 555 top-level calls
  everything else      0.362 s (3.8%)
```

**Construction is 61 % `declared_ports` and 0 % evaluation. The tick is
84 % evaluation.** 822 ns to compute one node of `values[node] =
operator(args)` is the interpreter's own overhead: a generator
resumption, a `seen` set, a stack of tuples, a dict keyed by node
identity, and — for a `min`, a `max` or an `abs` — `solid_node.math`'s
three-face dispatch (`_face`, `_is_symbolic`, `_is_formula`) on two
floats. cProfile confirms the shape: of `evaluate`'s 26.7 s cumulative,
`expression_graph.postorder` is 17.5 s.

**C. Every evaluation charged to its caller** (`spikes/callsites_curta.py`,
3 ticks, 42 519 evaluations):

| evaluations | wall | call chain |
| --- | --- | --- |
| 12 800 (30.1 %) | **55.1 %** | `_skeleton <- own_at <- _searched <- _crossing <- _first_cut` |
| 13 000 (30.6 %) | **22.5 %** | `_level <- _level <- _searched <- _crossing <- _first_cut` |
| 7 423 (17.5 %) | 0.3 % | `_level <- _branches <- _partition <- _partition <- increments` |
| 2 845 (6.7 %) | 0.1 % | `_level <- _branches <- _forced <- increments` |
| 2 560 (6.0 %) | 0.1 % | `_level <- _level_at <- _solved <- _crossings_of <- _partition` |
| 1 194 (2.8 %) | 0.3 % | `_evaluated <- increments <- _pass` |
| 390 + 384 (1.8 %) | 3.0 % | `_skeleton` / `_level <- _probe <- _decide` |

This answers the 39.3 % "elsewhere" ADR-123 handed over: it is **39 % of
the evaluations and about 1 % of the seconds**. Those are the small
graphs — a two-source gate, a comparison. The seconds are in exactly two
places: **77.6 % of the whole tick is the 200 `_Walk._searched` calls**,
at 64 samples each, one skeleton and one level per sample.

**D. The decisive measurement — how much of a searched graph MOVES**
(`spikes/cone_curta.py`; a node MOVES if some name in its cone has a
non-zero `delta`, plus the driven coordinate for a level):

```text
-- skeleton: 200 searched calls, 511 nodes/graph, 57.0 moving (11.2%)
       489 nodes,   57 moving   x 26
       497 nodes,   57 moving   x 26
       505 nodes,   57 moving   x 26
       513 nodes,   57 moving   x 26
       521 nodes,   57 moving   x 96
-- level: 200 searched calls, 203 nodes/graph, 4.0 moving (2.0%)
         3 nodes,    2 moving   x 100
       382 nodes,    6 moving   x 13   (and 390 / 398 / 406 / 414 alike)
```

Every one of those 64 samples recomputes 454 standing nodes of a
skeleton and 199 of a level. The graphs are that large because
`OperatingCurta`'s laws reach through a chain of seventeen retained dials
and fifteen carry sliders; the moving cone is that small because one tick
moves the crank and almost nothing else.

**E. The framework's own fixtures, for the pins**
(`spikes/path_baseline.py 3`, from the worktree root):

```text
Train            ticks   10  2119.0 ticks/s     8.0 evaluations/tick      40.0 node visits/tick
Clearing         ticks   10  1433.2 ticks/s    98.6 evaluations/tick     589.8 node visits/tick
CurtaInterface   ticks   60   128.7 ticks/s   602.6 evaluations/tick    7958.6 node visits/tick
```

`CurtaInterface` pays 7 959 node visits a tick where the real Curta pays
**3 266 000**. No existing fixture pays what the originating machine
pays, which is why §9 adds one.

**F. The suite.** `simulation/test_running.py` and
`simulation/test_running_clearing.py` (8 tests, 340 subtests) passed in
**867.92 s** on this worktree, five `RunningCurtaTest` cases taking
263 / 146 / 144 / 143 / 115 s; `simulation/test_running_laws.py` (4
tests) took 10.36 s. Astra's 528.874 s for ten tests is the same
measurement on a quieter machine. **The suite's cost is the tick's cost**
— five tests that step the machine, not rebuilds and not snapshots: at
~3.3 s/tick those are 35 to 80 ticks each, against 5 s of construction
per test.

## 3. The mechanism

### 3.1 A path value

One new internal object in `solid_node/simulation/program.py`, beside
`_KinkCuts`:

```python
class _PathValue:
    """One compiled graph followed along ONE tick's path.

    Built where the path is known, from the names the tick MOVES.
    Every node none of whose sources move is a constant of the path and
    is evaluated ONCE, from the piece's own inputs; the rest are
    evaluated per point, in the SAME postorder and through the SAME
    operators, so each float is the one the whole-graph walk gives.
    """
    __slots__ = ('root', 'order', 'standing')
```

Two stages, because they have different lifetimes:

1. **Structure** — which nodes move. A node moves iff it is a `name` in
   the moving set, or any child moves. It is a boolean decided in one
   postorder walk from `(graph, moving names)`, both of which are fixed
   for the whole tick.
2. **Standing values** — the value of every non-moving node under the
   inputs of the PIECE being followed. Fixed for one piece, because a
   branch placeholder is a constant only there.

**The first point of a piece IS the build.** A path value evaluates its
FIRST `at(values)` exactly as `GraphValue.evaluate` does — the whole
graph, in postorder — and in that same walk decides each node's moving
boolean and keeps each standing node's value. Every later point walks
only the moving nodes, reading each child from the standing map or from
the moving map it is building. A graph with no moving node at all returns
its standing root without walking.

That fusion is the difference between a mechanism that is free and one
that has to be paid for. A quantity followed at ONE point costs what it
costs today plus a boolean per node in a walk it was going to make
anyway; at two points, marginally more; at sixty-five, a ninth. There is
no threshold, no count to tune and no site that has to opt out — which is
why `_solved`'s two endpoint evaluations and `_searched`'s sixty-five can
take the same object. (The prototype of §5 built the structure in a
SEPARATE walk before the first point, which is why its build shows as
1.4 evaluations there and as nothing here.)

### 3.2 The moving set is the run's own statement

It is not inferred and it is not sampled. For a quantity followed by a
`JumpPlan` or a `_Walk` over a tick whose sources move by `delta`:

- a source name is MOVING iff `delta.get(name)` is non-zero;
- a branch placeholder (`$j…`) is STANDING — that is what a piece IS;
- the driven coordinate of a self-read is MOVING for a LEVEL (the walk
  hands it `own_at(s)` per sample) and STANDING for the SKELETON (which,
  by ADR-121's own refusal, does not name it at all).

`_Walk.__init__` already sets `self.delta[self.own] = 0.0`, so the own
name must be added explicitly for a level path rather than read off
`delta`. That is stated once, in the constructor of the level path, and
it is the one place the rule could be got wrong; §9 D is the test that
holds it.

### 3.3 Where the paths are built

| site | graph | built | re-bound |
| --- | --- | --- | --- |
| `_Walk` | the plan's skeleton | once per walk (one tick, one driven end) | per piece, on `branches` |
| `_Walk` | each dependent jump's level | once per walk | per piece, on `branches` and the piece's own value |
| `JumpPlan._partition` / `_crossings_of` | each jump's level | once per `increment` | per piece, on `inner` |

`_Walk._skeleton`, `_Walk._level`, `JumpPlan._level` and
`JumpPlan._level_at` become the four call sites that ask a path value
instead of a graph. `_skeleton_cuts` and `_level_cuts` (`_KinkCuts.between`)
stay on `GraphValue.evaluate` this cycle (review amendment): a kink's
level is its own sub-graph — `_kink_level` builds a fresh `a − b` node
for `min`/`max` — so it cannot share a path value with the skeleton or
the jump level it sits in, and on the originating machine every kinked
level is a three-node graph; giving each kink level a path value of its
own is a residue recorded, not taken.

**No cache outlives the tick.** That is a measurement, not a preference:
`spikes/endtoend_curta.py` with its cross-tick structure cache disabled
(`NOSTRUCT=1`) runs the Curta at **0.766 s/tick** against **0.727 s**
with it — 5 %. A per-tick build costs one classification walk per graph
against sixty-four evaluations of it, and it removes every question about
when a cached structure goes stale and how large the cache may grow.

### 3.4 What is deliberately NOT touched

`JumpPlan.increment`'s partition and its per-piece sum; `_Walk.run`'s cut
list and its landing arithmetic; `_land`, `_branch_of`, `_on_surface`,
`_decide`, `_far_side`; `_Block`'s ordering and its members' integration;
`Run._locate`, `_piecewise` and `_searched_constraint`, which re-run a
SUB-PROGRAM rather than one graph; `_evaluated`, which evaluates a whole
law once per tick end and has nothing to amortise; `Program.published()`
and every document field. `_along` still builds a fresh dict per point
(§8).

## 4. Why nothing that works today may move

A standing node's value is a function of inputs that are equal at every
point of the path. Computing it once and reading it back yields the
identical float — IEEE-754 arithmetic is deterministic and the operands
are the same bits. The moving nodes are then evaluated in the same
postorder, through the same operator objects, on operands that are
either those identical standing floats or moving values computed the same
way. So:

- no crossing fraction, landing, branch reading, increment or committed
  value changes by a unit in the last place;
- no partition is re-associated and no sum is re-ordered;
- no refusal path, tolerance, sub-division count or bisection round
  changes;
- a machine with no repeated evaluation along a path meets the new code
  once per graph per tick and pays a classification walk it amortises
  over the evaluations it was going to make anyway.

**This is not an argument, it is measured.** `spikes/proto_eval.py`
captures the Curta's own skeleton and level graphs at 40 real
`_searched` calls with their real 65 sample points, evaluates all 2 600
three ways and compares the `struct.pack('<d', …)` bytes:

```text
2600 evaluations, 932750 node visits today, 79300 moving (8.5%)
  A  current walk             906.42 ms    348.6 us/evaluation
  B  path evaluation           46.56 ms     17.9 us/evaluation   (19.5x)
  C  compiled path             15.64 ms      6.0 us/evaluation   (58.0x)
  bit mismatches: 0 of 2600
```

## 5. The end-to-end proof, on the real machine

`spikes/endtoend_curta.py` replaces `_Walk._skeleton` and `_Walk._level`
with path evaluations — nothing else — and prints the SHA-256 of the
committed snapshot after three ticks:

| run | construction | s/tick | snapshot SHA-256 |
| --- | --- | --- | --- |
| `plain` | 5.464 s | 3.279 | `dda09193d0e4…` |
| `patched` | 5.227 s | **0.727** | `dda09193d0e4…` |
| `plain` (repeat) | 5.437 s | 3.273 | `dda09193d0e4…` |
| `patched` (repeat) | 5.385 s | **0.727** | `dda09193d0e4…` |
| `patched`, `NOSTRUCT=1` | 5.332 s | 0.766 | `dda09193d0e4…` |
| `plain-ports` (§8) | **1.983 s** | 2.819 | `dda09193d0e4…` |
| `patched-ports` (§8) | **2.079 s** | **0.294** | `dda09193d0e4…` |

**4.50× on the tick, and the same committed state to the byte.** Two
call sites of one class. The prototype is evidence, not the
implementation: the real change puts the seam in `program.py` and reaches
the plan's sites too.

Where the post-change tick's 0.713 s then goes
(`endtoend_curta.py patched`, its own wrappers):

| | share of the patched tick |
| --- | --- |
| `declared_ports` | **56.4 %** |
| `_PathValue.at` | 17.8 % |
| everything else (`_along`, the walk itself, `Run`) | 17.2 % |
| remaining `GraphValue.evaluate` | 5.4 % |
| building the paths | 3.2 % |

## 6. Alternatives

- **C: compile the moving cone to a Python closure** (`exec` of generated
  source, the operators bound into the closure's globals). Measured at
  **58×** per evaluation against the current walk and bit-identical over
  the same 2 600 evaluations — 3× better than B. Rejected for this cycle:
  it puts run-time code generation into the engine, its build cost is
  3.3 evaluations against B's 1.4 (so it needs a structure cache to pay,
  which §3.3 has just measured away), and it would be optimising a term
  that this change leaves at 18 % of the tick. Recorded so a later cycle
  has the number.
- **Caching an evaluation by (graph, input values).** Would need a hash
  of the input dict per sample — more expensive than the 57-node walk it
  would avoid, and it answers nothing about the 454 standing nodes.
  Rejected.
- **Sharing samples across the dials that read the same ring.** The
  measurement refuses it: the six searched skeletons are five DIFFERENT
  graphs (489 / 497 / 505 / 513 / 521 nodes, §2 D), each a longer reach
  down the same chain, so there is no shared evaluation to hoist. What
  they share is their STANDING part, which is exactly what §3 computes
  once.
- **Memoising the skeleton across the levels that ride it inside one
  search.** Already 1:1 — 12 800 skeleton evaluations against 13 000
  level evaluations over the same 200 searches (§2 C) — so there is
  nothing to share. Rejected on the measurement.
- **Lowering `_SUBDIVISIONS`.** Cheaper and less exact, in a way that
  depends on sample-count luck. Against the pilot's constraint, and
  ADR-123 rejected it for the same reason.
- **A knob** — an opt-in, a cache size, a "fast evaluation" flag.
  Forbidden by the pilot's constraint and unnecessary: the moving set is
  structural and the run already owns it.

## 7. The per-PIECE classification, measured and deferred

`cut-at-the-kink` design.md §8 deferred a run-time classification per
piece and recorded that "nothing has measured what it would buy". This
cycle measures it (`spikes/perpiece_curta.py`: at every `_searched` call,
substitute every kink whose own level keeps ONE SIGN over the piece, then
re-classify with that cycle's prototype classifier):

```text
-- skeleton: 200 searched calls
     whole-tick None  -> per-piece constant   x 160
     whole-tick None  -> per-piece kinked     x  32
     whole-tick None  -> per-piece None       x   8
-- level: 200 searched calls
     whole-tick affine -> per-piece affine    x 100
     whole-tick kinked -> per-piece affine    x 100
```

**192 of 200 searched skeletons would become solvable** — the cam's
`max(0, |(phase+2) % 36 − 18| − HALF_DWELL)` is zero through the dwell,
so `sin` and `cos` of it are constants and the whole skeleton is
constant on that piece.

It is not taken here, for three reasons in order of weight:

1. **It moves answers.** A crossing located by the 64-sample search
   moves to the solved fraction — by up to the search's own tolerance,
   ~1e-13 of a tick (ADR-123 §2 D measured 9.3e-14 on `CurtaInterface`).
   Every Curta scenario's recorded crossings would move, and the corpus
   audit is a cycle's work of its own. This change moves nothing, which
   is why it goes first.
2. **It makes the classification depend on which piece you are in**,
   which ADR-123 deliberately kept static. That is a real architectural
   decision and belongs in its own ADR.
3. **After this change its prize is small.** The searched path is 21 %
   of the post-change tick (§5) and the port enumeration is 56 %.
   Removing 96 % of the searches would buy at most ~0.13 s/tick against
   the port memo's ~0.42 s.

Recorded in `workflow/warts.md` with these numbers, so the gap in
`docs/architecture.md` is no longer "unmeasured".

## 8. The port enumeration, measured and deferred

`declared_ports(node_class)` (`solid_node/motion/ports.py:447`) is a pure
function of a class: it walks `reversed(node_class.__mro__)`, reads
`vars(klass)`, and asks each value for `.coordinates` / `.coordinate`.
For a declarative node class that `getattr` runs `__getattr__` →
`read_through` → `_declared_places` → `declared_ports` again, so one
enumeration of a deep tree recurses: cProfile counts **133 890 calls from
1 504 primitive ones** during construction, 7.0 s of tottime inside 40.6
million `getattr`s.

Measured share: **61 % of construction** (3.265 s of 5.368 s) and
**12.5 % of a tick** (1.202 s over 3 ticks), through
`Run.bind → set_state → _receive_state → deliver → get_coordinate`.
Memoising it by class (`spikes/endtoend_curta.py`, modes `plain-ports`
and `patched-ports`) gives:

| | construction | s/tick |
| --- | --- | --- |
| today | 5.46 s | 3.279 |
| memo alone | **1.98 s** | 2.819 |
| this change alone | 5.23 s | 0.727 |
| both | **2.08 s** | **0.294** |

all four with the identical committed snapshot.

**It is a different mechanism in a different subsystem and it is
explicitly deferred to its own cycle.** It is not expression evaluation,
it is not the run, and it needs an answer this change has no business
giving: when may a class's port enumeration be trusted to stand? A class
dictionary is mutable, node classes are built dynamically by `.repeat()`
and by the declarative API, and a memo keyed by class either holds those
classes alive or needs a weak key. That is a contract to ratify, not a
dictionary to add in passing. The numbers are recorded in
`workflow/warts.md` so the pilot can order it next; on this measurement
it is the biggest remaining item and should be.

The residue after both — `_along` rebuilding a full source dict per
point, and the walk's own bookkeeping — is 17 % of the post-change tick
and is named here, not taken.

## 9. The proof, red first

Four red cases, each failing on this tree for a stated reason.

**A. A machine that pays what the Curta pays.** `tests/clearing_project/
machine.py` gains a fixture in the Curta's shape and only that shape: a
self-read law whose skeleton carries a DETENT CAM — `sin`, `cos` and
`sqrt` of `max(0, abs((phase + 2) % 36 − 18) − dwell)`, the real
`simulation/dial_cam.py` arithmetic — where `phase` reads the driven
coordinate AND a chain of standing sibling coordinates deep enough that
the skeleton is several hundred nodes of which a dozen move. The cam
makes the skeleton unclassified, so every crossing is SEARCHED, which is
the Curta's own case.

Assertion: **node visits per tick**, counted by a new probe in
`tests/base.py` beside `expression_evaluations` (it counts the postorder
steps a run charges, which is the unit that moves). RED on this tree at
the number the fixture measures; GREEN at under a fifth of it. Node
visits are deterministic, so this is a pin and not a timing test.

**B. Nothing the fixture computes moves.** The same fixture stepped a
dozen ticks, with its committed bank, its recorded crossings and its
landings asserted against the values measured on THIS tree before the
change — a golden written from the unpatched run. Red-first in the strong
sense: an implementation that got the moving set wrong changes one of
them.

**C. `Clearing` still costs exactly 98.6 evaluations a tick, and `Train`
8.0.** The pins ADR-123 set. They hold because the same points are
evaluated; `tests/base.py`'s `expression_evaluations` must therefore
count a path evaluation's `at` as one evaluation, which is a one-line
change to the probe and is asserted as part of this case. A naive
implementation that left the probe counting only `GraphValue.evaluate`
reports `Clearing` at a number that is not 98.6, and the test says so.

**D. The moving set is right, everywhere, on every fixture.** A
test-only checking path value (in `tests/`, never a framework knob) that
recomputes the STANDING part at every point and asserts it equals the
value it cached, run over the whole running fixture set. RED against a
deliberately wrong moving set (drop the driven coordinate from a level's
moving names) and green otherwise. This is the one guard against the
single mistake the mechanism admits.

**E. Nothing else moves.** `tests/running-corpus.json` byte-identical
for all 19 scenarios; `Program.published()` byte-identical for every
fixture; `tools/bench_selection.py`'s six numbers within their repeats'
spread with `RangedBlock` unchanged; the five named regression files and
then the whole suite green.

## 10. Acceptance

In Astra's own units, all measured from the originating project,
read-only, against this worktree.

**Must hit:**

| measure | today | after |
| --- | --- | --- |
| `running_probe --ticks 3`, seconds per 0.1-s tick | 3.279 / 3.273 | **≤ 1.20** (expected ≈ 0.73) |
| its committed snapshot after three ticks | `dda09193d0e45d4f2778df86ca548177d8e4aa6ba6d5dc2bf91d4c6292da3c8e` | **identical** |
| `simulation/test_running.py` + `test_running_clearing.py` | 867.9 s (this machine, 8 tests) | **≤ 1/3 of the baseline re-measured in the same session** |
| the new fixture's node visits per tick | its measured red number | **≤ 1/5** |

**Must NOT move:**

| measure | value |
| --- | --- |
| `Train` evaluations/tick | 8.0, exactly |
| `Clearing` evaluations/tick | 98.6, exactly |
| `CurtaInterface` evaluations/tick | 602.6, exactly |
| `Clearing`, `CurtaInterface` committed values | every one, exactly |
| `tests/running-corpus.json` | byte-identical, all 19 scenarios |
| every published document | byte-identical; no field, no flag, no version |
| `RangedBlock` ms/tick | 16.0, within the repeats' spread |
| `Train` / `FixedZero` / `ShiftedCarry` / `CurtaCarriage` ms/tick | within the repeats' spread |
| `Train` ticks/s | 2 119, within the repeats' spread — it meets none of the new code |
| `Clearing` ticks/s | 1 433, and **no more than 10 % below it** — the small-machine guard of §11 |
| `OperatingCurta` construction seconds | within its own spread — this change does not claim it (§8) |

## 11. Risks

- **A wrong moving set is a WRONG ANSWER, silently.** If a name that
  moves is classified standing, the run reads a stale float and commits
  a wrong value with no exception anywhere. It is the only failure mode
  the mechanism has, it has exactly one source — the driven coordinate
  of a self-read level, which `_Walk.__init__` deliberately zeroes in
  `delta` — and §9 D is the guard written for it.
- **A piece's branch reading leaking across pieces.** The standing
  values depend on the branch placeholders, which change from piece to
  piece. Binding once per WALK instead of once per PIECE would be
  exactly this bug. The structure is per tick; the standing values are
  per piece, and the two must not be confused. It is a named test.
- **A small machine paying for a mechanism it cannot use.** `Clearing`'s
  followed graphs are SIX nodes (589.8 node visits over 98.6 evaluations
  a tick) and most of its sites are `_solved`'s two endpoints. If the
  structure were built in a walk of its own, every such site would pay
  an extra whole evaluation and a machine like `Clearing` could get
  SLOWER. §3.1's fused first point is the answer, and it is not a
  detail: the acceptance pins `Clearing`'s and `Train`'s ticks per
  second, not only their evaluation counts. `_evaluated` — one
  evaluation per law per tick end, with nothing after it to amortise —
  is left alone for the same reason.
- **Growth.** No cache outlives the tick (§3.3), so there is nothing to
  bound, nothing to invalidate and nothing keeping a graph alive.
- **The two runtimes.** The viewer's TypeScript run keeps its whole-graph
  walk. It computes the same answers — this change moves no float — so
  the corpus comparison is unaffected and no document version moves. The
  same optimisation over there is a solid-node-viewer finding, recorded
  and not proposed.
