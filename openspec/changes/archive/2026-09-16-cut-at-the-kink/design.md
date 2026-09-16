# Design: a kink is a cut

## 1. The finding

`solid_node/simulation/program.py` decides, once at compile, whether a
quantity it must follow along a tick's path can be SOLVED or must be
SEARCHED. The decision is `_affine_in_sources`, and its own docstring
states the gap:

> A call, a power, or a product of two moving operands is not affine, and
> falls to the search — correct but slower, which is why
> `floor(max(x, 0))` is searched although it is piecewise affine.

The vocabulary a running law may call is `solid_node.math.SYMBOLIC_BUILTINS`:

```
sin, cos, tan, asin, acos, atan, atan2, sqrt, abs, floor, ceil, sign, min, max
```

Three of those — `floor`, `ceil`, `sign` — are already JUMP nodes, planned
and located. Eight — `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2`,
`sqrt` — are genuinely curved. **The remaining three — `abs`, `min`,
`max` — are KINKS: continuous, piecewise affine, and each returns one of
its operands EXACTLY.** They are the whole of the gap. Every composition
in `solid_node/math.py` is built on them: `clamp = min(max(x, low), high)`,
`clamp01 = clamp(x, 0, 1)`, `ramp = clamp01((x − a)/(b − a))`,
`piecewise` = a sum of `clamp01` terms. (`lerp` has no kink at all;
`wrap` is built on `ceil` and is already a jump; `bump` is
`16p²(1−p)²` over `clamp01`, a genuine product of two moving operands,
and stays searched.)

So a law gated by a `clamp01` window — the framework's own recommended
spelling of a motion profile, and the shape of the originating project's
clearing interface — falls to 64 samples per piece plus up to 64
bisection rounds per bracket, where three divisions would do.

## 2. The baseline, measured on this worktree

Framework worktree `solid-node/WTs/curta-speed`, branch `curta-speed`,
head `f310a3c`; workspace venv; `OPENBLAS_NUM_THREADS=1
OMP_NUM_THREADS=1`; one job at a time.

**A. Ticks per second and `GraphValue.evaluate` calls per tick** — the
`read-the-driven-coordinate` evidence.md §14 probe, repeated (the probe
is `scratchpad/probes/kink_baseline.py`; `Clearing` sweeps `ring` by 600
over 10 ticks of `dt = 0.1`, `CurtaInterface` moves `clearing` by 1.0
over 60 ticks of `dt = 1/60`, best of 5):

| fixture | shape | best | ticks/s | evaluations/tick |
| --- | --- | --- | --- | --- |
| `Train` | no self-read | 4.37 ms | 2 288 | **8.0** |
| `Clearing` | affine skeleton, SOLVED | 6.54 ms | 1 528 | **98.6** |
| `CurtaInterface` | `clamp01` window, SEARCHED | 2 126.78 ms | 28.2 | **2 861.3** |

`Clearing`'s 98.6 and `CurtaInterface`'s 2 861.3 are the wart's own
numbers (99 and 2 861) reproduced exactly; the wall-clock figures differ
from its 1 349 / 27.2 by the machine, not by the tree.

**B. Where `CurtaInterface`'s evaluations go** — every evaluation charged
to the search call site that caused it, with the classification of the
skeleton and the level that sent it there
(`scratchpad/probes/attribute.py`):

| share | calls | site |
| --- | --- | --- |
| 56.8 % (97 476) | 756 | `_Walk._searched` — skeleton KINKED, level affine |
| 27.7 % (47 610) | 726 | `JumpPlan._searched` — level KINKED |
| 15.5 % (26 595) | — | everywhere else |

**84.5 % of the fixture's cost is in the two call sites this change
replaces**, at ~129 and ~66 evaluations per call where a solve costs a
handful. `Clearing` charges 0 % to either: it is already solved.

**C. `tools/bench_selection.py`**, `dt = 0.02`, best of 5 — the numbers
this change must leave alone, `RangedBlock` included (§7):

```
Train (the control, no block):                     0.468 ms/tick
FixedZero (the frozen twin: three separate edges):  0.760 ms/tick
ShiftedCarry (one block of two, no crossing):       1.248 ms/tick
RangedBlock (a range on a block coordinate):       16.142 ms/tick
ShiftedCarry, the tick that crosses the detent:     2.374 ms/tick
CurtaCarriage (one block of seven):                 9.815 ms/tick
```

**D. Exactness, not only cost.** `CurtaInterface`'s first result dial
meshes where `ring_angle(control) = 10.5`, which is
`control = 0.1 + 0.8 · 50.5/240`, exactly `0.26833333333333337`. With
`dt = 1/60` that falls in tick 17 at `t = 0.10000000000000231`. The run
RECORDS it at `0.09999999999990905` — **9.3e-14 out**, where the float
spacing at 0.1 is 1.4e-17 (`scratchpad/probes/exactness.py`). The level
is affine on that piece (the clamp is strictly inside its window there),
so the exact answer was one division away.

## 3. The real Curta: what this fixes and what it does not

`projects/Calculators/Curta-Type-I-3x`, branch `direct-operation`, HEAD
`9fb725f`, run against THIS worktree:

```
constructed 5.300141316023655
tick 1 seconds 3.2874673350015655
tick 2 seconds 2.7987472959794104
tick 3 seconds 3.3783866980229504
```

Classifying every skeleton and every jump level of `OperatingCurta`'s
compiled program (`scratchpad/probes/classify_curta.py`):

| what | affine | kinked | unclassified |
| --- | --- | --- | --- |
| skeletons (laws with a jump plan) | 0 | **28** | **41** |
| jump levels | 532 | **15** | 0 |
| laws with no plan | 183 | 16 | 0 |

and the 41 unclassified skeletons are blamed on `cos` (17), `sin` (17), a
product of two movers (16) and a moving divisor (8) — the dial detent cam
in `simulation/dial_cam.py`:

```python
angle = max(0, abs((phase + 2) % 36 - 18) - HALF_DWELL)
horizontal = CAM_RADIUS * sin(angle)
height = CAM_RADIUS * cos(angle) + sqrt(max(0, BALL_RADIUS**2 - horizontal**2))
```

Attributing three of the Curta's own ticks
(`scratchpad/probes/attribute_curta.py`):

```
total evaluations 42519  (14173/tick)
   12900 (30.3%) in 100 calls  walk crossing | skeleton None | level affine
   12900 (30.3%) in 100 calls  walk crossing | skeleton None | level kinked
   16719 (39.3%) elsewhere
```

**Every searched evaluation in those ticks is under an UNCLASSIFIED
skeleton — none under a kinked one.** This change therefore does not make
the measured `running_probe` faster, and the proposal says so. It fixes
the kinked shape exactly and completely (the `CurtaInterface` fixture,
`piecewise` profiles, the carriage association the Curta had to write as
comparisons), and it hands the next cycle a measured attribution of where
that machine's seconds actually are: 60.6 % of a tick in `_Walk._searched`
under a cam skeleton carrying `sin`, `cos` and `sqrt` of a moving phase.
Half of that (the `level affine` row) is a level the run could solve if it
could follow the driven coordinate's own path, which it cannot while the
skeleton is curved.

## 4. The mechanism

### 4.1 The classification

`_affine_in_sources` / `_degree_of` become a three-valued `_shape_of`
returning `'constant'`, `'affine'`, `'kinked'` or `None`, with `'kinked'`
propagating exactly where `'affine'` does:

| node | shape |
| --- | --- |
| number, branch placeholder `$…` | constant |
| source name | affine |
| every child constant | constant |
| unary `-` | the child's, if movable |
| `+`, `-` | kinked if either side is, else affine |
| `*` with one CONSTANT side, `/` by a constant | the moving side's |
| `abs`, `min`, `max` over movable children | **kinked** |
| anything else | `None` |

"Solvable" is `shape in ('constant', 'affine', 'kinked')`; "needs
sub-division" is `shape == 'kinked'`. This is the only change of
classification: nothing that is unclassified today becomes classified
except through a kink.

**The PUBLISHED flag is not this shape.** `Program.published()` keeps
emitting the two-valued `affine` the export spec defines, and it is
`shape == 'constant' or shape == 'affine'` — a kinked quantity publishes
`false`, exactly as today. The third value is internal (§9).

### 4.2 Locating the kink breakpoints

A kink node's LEVEL is `x` for `abs(x)` and `a − b` for `min(a, b)` and
`max(a, b)`; its one surface is zero. Breakpoints over a stretch
`[left, right]` are computed exactly as `JumpPlan._partition` computes a
jump partition, and for the same reason:

1. Take the kink nodes in the graph's POSTORDER.
2. For each, over each sub-interval the kinks before it have already
   produced, evaluate its level at the two ends. On that sub-interval the
   level is affine (its inner kinks are cut, and by classification
   nothing else in it bends), so its zero is one division:
   `left + (right − left) · (0 − low)/(high − low)`, kept only when it
   lies strictly inside.
3. Merge into the list with `_merged` — two breakpoints closer than
   `_CROSSING_TOLERANCE` are ONE, exactly as two crossings are.

No sampling, no bisection, **no fourth tolerance**. A level that does not
move over a sub-interval (`high == low`) contributes nothing, which is the
same statement `_Walk._searched` already makes.

### 4.3 A kink breakpoint is not a crossing

This is the load-bearing rule, and it is what keeps every existing answer
bit-identical. The law is CONTINUOUS at a kink. Therefore a breakpoint:

- is NOT appended to `crossings` and never appears in `sim.crossings` or
  in a corpus tick;
- never enters the partition `JumpPlan.increment` sums over, so no
  increment is re-associated and no float sum changes;
- never triggers `_Walk._land`, the far-side ulp walk — there is no gap
  to land past;
- does not count toward `_MAX_CROSSINGS`.

It exists only as a sub-division inside a SOLVE.

### 4.4 The three solve sites

**(a) A jump node's crossings — `JumpPlan._crossings_of`.** Today: if
`jump.affine`, interpolate from the piece's two endpoint values, taking
every surface between them (`inclusive=False`); else `_searched`. New: if
the level is KINKED, sub-divide the piece at the level's breakpoints
(§4.2) and interpolate on each sub-piece in turn, concatenating the
surfaces. The boundary convention is the one subtlety: `inclusive=False`
at both ends of a sub-piece would LOSE a surface lying exactly on an
interior breakpoint, so the right end is inclusive for every sub-piece
but the last, and the result goes through the existing `_deduplicated`,
which already exists for exactly this ("a crossing that falls on a
sub-interval boundary is located twice, from either side").

**(b) A self-read walk's crossings — `_Walk._crossing`.** Today: solve
only when `jump.affine AND self.reading.affine`, because the driven
coordinate's own path over the piece is
`own_left + (skeleton(s) − base)` and is affine only when the SKELETON
is. New: solve when both are affine-or-kinked, sub-dividing the piece at
the union of the SKELETON's breakpoints and the LEVEL's — the skeleton's
first, because they are what make `own_at` affine, and the level's
inside them, because the level rides `own_at`. That ordering is an
ORDER OF COMPUTATION, not just of concatenation: the level's own
breakpoints depend on `own_at`, which is affine only WITHIN a skeleton
sub-piece, so the level's breakpoints are located per skeleton sub-piece,
with `own_at` evaluated at that sub-piece's two ends. On each sub-piece both are
affine in `t`, so the first surface is one interpolation; sub-pieces are
taken left to right and the first surface strictly inside the PIECE wins,
which is the rule `_first_cut` already states. `_searched`'s two special
rules survive unchanged in the solved path: a level that does not move
crosses nothing (`high == low`), and the surface a piece STARTS on is not
one it crosses (`inclusive=False` at the piece's own left end).

**(c) A stop's localization — `Run._locate` / `_piecewise` via
`Edge.cuts`.** `Edge._affine_ends` (and `_Block._affine_ends`, see §7)
now report the three-valued shape, so a kinked determiner becomes
solvable. `_locate` must then be given cuts, and `Edge.cuts` today
returns `()` for a law with NO jump plan — which is exactly the kinked
shape `Train`'s `lever drives slide.travel` has
(`4 + 72·clamp01((lever − 113.5)/11.25)`). Left alone, `_locate` would
take its `travel = deltas[key]; (bound − value)/travel` fast path and
interpolate straight THROUGH the kink: not a rounding error but a wrong
stop. So:

- `Edge.cuts` returns the union of the plan's (or the walk's) cuts and
  the SKELETON's kink breakpoints — computed even when there is no plan
  at all, in which case it returns a full partition `(0.0, …, 1.0)`.
  **Where** they are computed is part of the contract: a skeleton reads
  the plan's BRANCH PLACEHOLDERS (`$j…`), which are constant only within
  ONE piece of the plan's partition. So the skeleton's kink breakpoints
  are located inside each plan PIECE, with that piece's branch values
  substituted, and the per-piece lists are unioned with the plan's own
  cuts through `_merged`. A plan-less determiner has exactly one piece —
  the whole tick — and no placeholders to substitute;
- when the determiner is kinked but NO kink is crossed over this tick,
  the breakpoint list is empty and `Edge.cuts` returns `()`: the path IS
  affine over the whole tick and the one-division fast path is exact.
  That invariant — empty cuts means affine — is what makes the fast path
  safe to keep, and it is worth a test of its own;
- `_piecewise` is unchanged. It walks the cuts, brackets the bound
  between two consecutive values and divides.

### 4.5 What is deliberately NOT touched

`JumpPlan.increment`'s partition and its per-piece sum; `_Walk.run`'s own
cut list and its landing arithmetic; `_branch_of`, `_on_surface`,
`_decide`, `_far_side`; `Run._searched_constraint` and everything under
"A range bound may read other coordinates"; `_Block`'s ordering. The
change adds a sub-division to three SOLVES and changes nothing that
integrates.

## 5. Why nothing that works today may move

Because of §4.3, the only observable that can change is the LOCATION of a
crossing or a stop that was previously SEARCHED on a kinked quantity —
which is the whole point, and moves it by at most the search's own
tolerance (~1e-13 of a tick, §2 D), toward the exact answer.

- A machine with no kink in any followed quantity meets no new code: the
  classification is computed at compile and the breakpoint walk is
  skipped where the list of kinks is empty. `Train` (8.0/tick) and
  `Clearing` (98.6/tick) must be EXACTLY unchanged, and are asserted.
- A kinked quantity whose kinks are not crossed over a tick yields an
  empty breakpoint list, so the solve is the same single interpolation it
  would have been if the quantity were classified affine.
- Every retained value, landing, stop group, command status and refusal
  path is untouched.

## 6. The corpus audit

`tests/running-corpus.json` holds 19 scenarios over 16 machines. Under
the new classification, five machines get a reclassified determiner and
**no jump level in the corpus changes class at all**
(`scratchpad/probes/corpus_flip.py`):

| machine | reclassified |
| --- | --- |
| `Captured` | `key.travel drives p1.lift`, `… p2.lift` |
| `CarryLead` | `(tens_entry, units.turn) drives tens.turn` |
| `Remainder` | `crank drives pinion.turn` |
| `Train` | `lever drives slide.travel` |
| `Window` | `crank drives pinion.turn` |

A reclassified determiner is observable ONLY through `Run._locate`, and
the corpus records exactly ten stops, on `wheel.turn`, `rack.travel`,
`lever.turn`, `first.turn`, `gauge.turn`, `carry.travel` and
`key.travel` — **none of them on any of those five coordinates**. None of
the five laws is a self-read either. So `tests/running-corpus.json` must
be **byte-identical** after the change, and confirming that is task 1.5
(red-first) and task 6.2 (after).

The corpus must then GAIN the new shape, because ADR-111 makes it the
contract between the two runtimes: one scenario over a new fixture whose
kinked determiner carries a range and whose stop lands on the sloped
piece (§11 case C), plus the required-feature entry that refuses a corpus
without it, in the shape `pin-the-block-order` established.

## 7. The neighbouring wart, decided

`select-the-source` filed: *"A stop on a block coordinate is never
SOLVED. A block's gives are classified non-affine by construction
(`Edge._affine_ends`), so `Run._locate` searches every stop on one."*
Measured again here: `RangedBlock` 16.142 ms/tick against 1.248 ms for a
quiet tick of the same block.

**It is a different mechanism and it is explicitly deferred.**
`_Block._affine_ends` returns `False` not because a block's value is
curved but because "a block's value is piecewise in the SELECTOR
partition and RE-ORDERED across it". Its obstruction is not a kink in an
expression: it is that the block has no single expression until a branch
vector is fixed, and that the ORDER the members are run in may differ
from piece to piece. Classifying a give would mean classifying it per
branch vector AND proving the order stable on the piece — which is
ADR-122's territory, not this one's. Nothing in this change makes it
easier or harder, and the change asserts that `RangedBlock`'s tick cost
and its corpus entry do not move.

What DOES improve for a block, for free and by the same classifier, is a
SELECTOR whose level carries a `clamp01`: `_Block._partition` locates
selectors through `plan._partition`, so a kinked selector level is solved
like any other. That is why the "A selection decides which sources a law
reads" requirement takes the same one-sentence edit; no block in the
fixtures has one today, and the change adds no block fixture.

## 8. Deferred: classification per BRANCH

A kink can pin a CURVED subtree to a constant on one of its pieces. The
Curta's cam is the case: through the dwell, `max(0, |…| − HALF_DWELL)` is
zero, so `sin(angle)` and `cos(angle)` are constants and the whole
skeleton is affine there; through the rise it is genuinely curved. A
run-time classification per piece would solve strictly more than a
compile-time flag does.

It is deferred because it costs a classification per piece per tick
instead of one per edge at compile, because it makes the answer depend on
which piece you are in (a property the current design deliberately keeps
static), and because nothing has measured what it would buy. It is
recorded here and in `workflow/warts.md` as evidence for the cycle that
takes up Astra's seconds-per-tick wart, together with §3's attribution.

## 9. Risks

- **The published `affine` flag, and the two runtimes locating a
  crossing differently.** The document DOES carry the classification.
  `openspec/specs/export/spec.md` specifies, per driven end of a law,
  `affine` — "whether that driven end's value is affine in its sources
  along a tick's path" — and, per jump, `affine` — "whether that level
  quantity is affine in the sources". `Program._published_edge` publishes
  `list(edge.affine)` and `_published_plan` publishes `jump.affine`, and
  `tests/running-corpus.json` carries 72 of those flags inside its
  published documents. The viewer's runtime CONSUMES them to choose
  between a solve and a search:
  `solid_node_viewer/widget/src/run/run.ts:851` (`if (edge.affine[index])`
  → one division or the piecewise stop) and `run/jumps.ts:347` and `:779`
  (`if (jump.affine)`, `jump.affine && this.reading.affine` → interpolate,
  else sample and bisect).

  **Therefore the published flag stays TWO-valued and keeps its
  export-spec meaning, and a kinked quantity MUST keep publishing
  `affine: false`** — per driven end and per jump level. The three-valued
  shape is internal to the Python runtime in this cycle; the internal
  consumers that learn the third value are `run.py:974`
  (`edge.affine[index]`), `program.py:481` (`jump.affine`) and
  `program.py:952`, not `Program.published()`. Two things would break if
  a kinked quantity published `affine: true`: the viewer would
  INTERPOLATE STRAIGHT THROUGH a kink — a wrong crossing or a wrong stop
  in the browser, which is exactly the §4.4 (c) trap on the other runtime
  — and the five reclassified corpus machines (§6) would change their
  documents' bytes. §11 D carries the red test that pins both halves.

  What remains is the asymmetry: Python solves a kinked quantity where
  the viewer still searches it, so their answers differ by up to the
  search tolerance — inside the corpus's own `1e-9` relative window,
  which is how `tests/test_running_corpus.py` compares a crossing's `t`.
  The residual risk is a crossing that falls so near a surface that solve
  and search choose different BRANCHES; it is the same risk the corpus
  already carries between any two localizations, and the change does not
  widen it. No document version moves and no viewer cycle is required for
  CORRECTNESS.

  A later viewer cycle that wants the solve cannot simply re-derive the
  shape: nothing in the document says whether a non-affine quantity is
  kinked or curved. It needs either a new document field for the shape or
  a redefinition of `affine`, either of which is a document version bump
  — two changes in two repositories, the export spec's and the viewer's.
  That is recorded as a follow-up (tasks 10.2), not taken here.
- **The boundary convention of §4.4 (a).** Getting `inclusive` wrong at
  an interior breakpoint loses or doubles a surface. It is a named test.
- **`Edge.cuts` for a plan-less kinked determiner.** Forgetting it turns
  a searched-but-correct stop into a fast-path-but-wrong one. It is the
  red test of §11 case C, and the reason that case exists.
- **A kink whose level is itself unclassified.** `max(0, sin(x))` must
  stay searched; the classification is conservative and refuses to call
  it kinked, but a careless implementation could classify the kink by its
  own node type rather than by its operands.

## 10. Alternatives rejected

- **Rewrite a kink into a comparison-gated form** (`min(a,b)` as
  `a·(a<b) + b·(a>=b)`). It would reuse the jump machinery whole — and it
  would turn a continuous node into a JUMP: recorded crossings where
  nothing jumps, a far-side landing on a surface with no gap, a partition
  the increment is re-summed over, and every existing answer moved by
  rounding. Rejected outright.
- **Add the kink breakpoints to the tick's PARTITION** (make them cuts
  like jumps, uniformly). Architecturally tidier, and it changes numbers:
  `f(c) − f(a) + f(b) − f(c)` is not `f(b) − f(a)` in floats, so every
  existing machine carrying a kink would move by ulps and the corpus
  would need regenerating for no behavioural gain. Rejected; the
  breakpoints stay inside the solve.
- **Substitute a chosen branch into the skeleton per piece** (`min(a,b)`
  → the selected child). Unnecessary: `min` and `max` RETURN one operand
  exactly, so evaluating the node is already evaluating the selected
  branch, bit for bit. Substituting would buy nothing and would force a
  per-piece skeleton graph.
- **A knob** (`solve=True`, a subdivision count, a tolerance). Forbidden
  by the pilot's constraint and unnecessary: the classification is
  structural.
- **Lower `_SUBDIVISIONS`.** Cheaper and less exact, in a way that
  depends on sample-count luck. Against the constraint that a tick's
  answer must not depend on sampling.
- **Newton or a secant iteration on the searched path.** A fourth
  tolerance and an iteration count, which ADR-121 already rejected for
  the same reason.

## 11. The proof, red first

Three red cases, each failing on this tree for a stated reason, each
green after:

**A. Exactness of a kinked jump level (`JumpPlan`).** A running root
whose gate's level reads a `clamp01` of a driver, driven so the gate's
surface is crossed strictly inside a tick, with the clamp strictly inside
its window there. The exact crossing fraction is a closed form of the
fixture's own arithmetic (never read back from the law). RED on this
tree: `CurtaInterface`'s own tick-17 crossing sits `9.3e-14` from it
(§2 D). GREEN: within a few units in the last place.

**B. Exactness of a kinked self-read crossing (`_Walk`).** The same
assertion on `CurtaInterface`, whose skeleton is kinked — the level is
affine, so it is the SKELETON's classification that sends it to the
search today. Plus the cost assertion: `GraphValue.evaluate` calls per
tick, measured by the probe `tests/test_running_stops.py` already carries
in `graph_evaluations`, RED at 2 861 and GREEN under the number §12
states.

**C. Correctness of a stop on a kinked determiner with NO jump plan.** A
new fixture beside `Train`'s `lever drives slide.travel`: the same
`4 + 72·clamp01((lever − 113.5)/11.25)` law, with a declared `range` on
the driven coordinate whose bound lies on the SLOPED piece, and a tick
whose path starts on the FLAT one. RED on this tree in the weak sense
(the searched stop is off the exact fraction by the search tolerance);
RED in the strong sense against the naive implementation (`Edge.cuts`
left returning `()` puts the stop at the fraction a single linear
division over the whole tick gives — a materially wrong answer, and the
test states the number). GREEN: the exact fraction, the coordinate
committed at its bound exactly.

**D. Nothing else moves, and the DOCUMENT least of all.** A red-first
test in `tests/test_running_document.py`: a law with a kinked determiner
and no jump publishes `affine: [false]`, and a kinked jump level
publishes `affine: false` — both asserted against the flag's export-spec
meaning, both of which a naive implementation that plumbed the new shape
through `Program.published()` would flip to `true`. With it,
`Program.published()` for `Train` (whose `lever drives slide.travel` is
one of the five reclassified determiners, §6) is byte-identical before
and after. Then: `Train` at exactly 8.0 evaluations/tick; `Clearing` at
exactly 98.6; the whole `tests/running-corpus.json` byte-identical;
`tools/bench_selection.py`'s six numbers within their spread,
`RangedBlock` included; the five named regression files and then the
whole suite green.

**E. A curved law is still searched.** `max(0, sin(x))` and a
product-of-two-movers level classify as unclassified and pay exactly what
they pay today. One test, so a later per-branch cycle has a stated
starting point.

## 12. Acceptance

Must hit:

| measure | now | after |
| --- | --- | --- |
| `CurtaInterface` evaluations/tick | 2 861.3 | **≤ 900** (expected ≈ 640) |
| `CurtaInterface` ticks/s | 28.2 | **≥ 120** (expected ≈ 180) |
| the tick-17 crossing's distance from the RATIONAL exact fraction | 9.3e-14 (the search; ~6 700 ulp) | **< 1e-15** (review amendment: the reference in §2 D is itself 84 ulp from the rational answer, and the level's own evaluation rounding over its span leaves ~20 ulp that no interpolating localization can remove; asserted against the rational answer, not the §2 D float) |

Must NOT move:

| measure | value |
| --- | --- |
| `Train` evaluations/tick | 8.0, exactly |
| `Clearing` evaluations/tick | 98.6, exactly |
| `Clearing` committed values | every one, exactly |
| every published `affine` flag | two-valued and unchanged; a kinked quantity publishes `false` |
| `tests/running-corpus.json` | byte-identical for the 19 existing scenarios |
| `RangedBlock` ms/tick | 16.1, within the repeats' spread |
| `Train` / `FixedZero` / `ShiftedCarry` ms/tick | within the repeats' spread |
| `OperatingCurta` `running_probe --ticks 3` | within its own spread — this change does not claim it (§3) |

The expected figures come from §2 B: the 756 walk calls and 726 jump
calls stay, at a handful of evaluations each instead of ~129 and ~66,
leaving the 15.5 % that is charged elsewhere (443/tick) as the floor.
