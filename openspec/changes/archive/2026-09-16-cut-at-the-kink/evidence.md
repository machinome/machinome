# Evidence: applying `cut-at-the-kink`

Framework worktree `solid-node/WTs/curta-speed`, branch `curta-speed`,
planning commit `03e2b2d` over base `d3c2242` and the carried docs commit
`f310a3c`. Every measurement was taken here, with
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1` and ONE job at a time.

Python: `PYTHONPATH="$PWD" ../../../.venv/bin/python`.
Probes: `WT="$PWD" OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
PYTHONPATH="$PWD" ../../../.venv/bin/python
openspec/changes/cut-at-the-kink/spikes/<probe>.py`.

## Group 0 — the suite BEFORE any change

```
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH="$PWD" \
    ../../../.venv/bin/python -m pytest tests -q -p no:cacheprovider
```

```text
3005 passed, 4 skipped, 53 warnings, 1679 subtests passed in 327.65s (0:05:27)
```

## Group 1 — red: the finding reproduced on this tree

### 1.1 / 1.2 RED (cost) — `spikes/kink_baseline.py 5`

```text
Train            ticks   10  best      4.61 ms  median      4.66 ms    2171.0 ticks/s  80 evaluations = 8.0/tick
Clearing         ticks   10  best      7.01 ms  median      7.40 ms    1427.5 ticks/s  986 evaluations = 98.6/tick
CurtaInterface   ticks   60  best   2159.34 ms  median   2260.04 ms      27.8 ticks/s  171681 evaluations = 2861.3/tick
```

The three EVALUATION counts are the proposal's exactly — 8.0, 98.6,
2 861.3. The wall-clock figures sit a little under design.md §2 A's
(2 171 against 2 288, 1 428 against 1 528, 27.8 against 28.2): the same
machine under a different load, and the ratio is unchanged. The
evaluation counts, not the milliseconds, are what the acceptance pins
exactly.

### 1.3 RED (attribution) — `spikes/attribute_fixtures.py`

```text
== CurtaInterface, 60 ticks
total evaluations 171681  (2861/tick)
       97476 ( 56.8%) in    756 calls  walk crossing | skeleton kinked | level affine
       47610 ( 27.7%) in    726 calls  jump crossing | skeleton n/a | level kinked
       26595 ( 15.5%) elsewhere
== Clearing, 10 ticks
total evaluations 986  (99/tick)
         986 (100.0%) elsewhere
```

84.5 % of `CurtaInterface`'s evaluations are in the two call sites this
change replaces, at 129.0 and 65.6 evaluations per call. `Clearing`
charges 0 % to either.

### 1.1 classification — `spikes/classify_fixtures.py`

```text
--- Train
   law without a plan   affine     3
   law without a plan   kinked     1
--- Clearing
   jump level           affine     3
   jump level           constant   1
   skeleton             affine     1
--- CurtaInterface
   jump level           affine     12
   jump level           kinked     12
   skeleton             kinked     6
--- ShiftedCarry
   jump level           affine     9
   skeleton             affine     3
--- RangedBlock
   jump level           affine     5
   law without a plan   affine     1
   skeleton             affine     2
--- CurtaCarriage
   jump level           affine     80
   law without a plan   affine     2
   skeleton             affine     7
```

`Clearing`'s skeleton is affine and stays solved; `CurtaInterface`'s six
skeletons and twelve of its jump levels are kinked. `ShiftedCarry`,
`RangedBlock` and `CurtaCarriage` carry no kink at all in any followed
quantity, which is why §7's block numbers cannot move.

### 1.4 RED (exactness) — `spikes/exactness.py`

```text
exact control at reach == 0 : 0.26833333333333337
tick 17 exact t 0.10000000000000231
  recorded     >= level      0.0 t 0.09999999999990905  error -9.325873406851315e-14
```

`9.33e-14` out, against a float spacing of `1.4e-17` at `0.1`.

### 1.5 RED (blast radius) — `spikes/corpus_flip.py`

```text
Captured:
   skeleton/graph now kinked: key.travel drives p1.lift
   skeleton/graph now kinked: key.travel drives p2.lift
CarryLead:
   skeleton/graph now kinked: (tens_entry, units.turn) drives tens.turn
Remainder:
   skeleton/graph now kinked: crank drives pinion.turn
Train:
   skeleton/graph now kinked: lever drives slide.travel
Window:
   skeleton/graph now kinked: crank drives pinion.turn
```

No jump level in the corpus changes class. The corpus's 19 scenarios
record exactly TEN stops:

| scenario | tick | coordinate |
| --- | --- | --- |
| `Ratchet` dt 0.05 | 13 | `wheel.turn` |
| `Swept` dt 0.01 | 6 | `rack.travel` |
| `TwoStops` dt 0.05 | 2 | `lever.turn` |
| `TwoStops` dt 0.05 | 2 | `rack.travel` |
| `StopAndJump` dt 0.05 | 1 | `first.turn` |
| `StoppedClearing` dt 0.05 | 3 | `gauge.turn` |
| `StoppedClearing` dt 0.05 | 3 | `wheel.turn` |
| `RangedBlock` dt 0.05 | 1 | `carry.travel` |
| `RangedBlock` dt 0.05 | 4 | `carry.travel` |
| `Captured` dt 0.05 | 6 | `key.travel` |

None is on `p1.lift`, `p2.lift`, `tens.turn`, `pinion.turn` or
`slide.travel` — the five reclassified determiners — and none of those
five laws is a self-read. So `tests/running-corpus.json` must be
byte-identical for all 19 existing scenarios.

### 1.6 RED (the Curta) — the number this change does NOT claim

`projects/Calculators/Curta-Type-I-3x`, branch `direct-operation`, HEAD
`9fb725f`, read-only, against THIS worktree:

```
cd <curta> && PYTHONPATH="<curta>:<worktree>" OPENBLAS_NUM_THREADS=1 \
    OMP_NUM_THREADS=1 <venv>/python -m simulation.tools.running_probe --ticks 3
```

```text
constructed 5.268189616006566
tick 1 seconds 3.2703272310027387 result 0 counter 0
tick 2 seconds 2.9405087099876255 result 0 counter 0
tick 3 seconds 3.3605945089948364 result 0 counter 0
```

design.md §3's 5.300 / 3.287 / 2.799 / 3.378 s, within the spread.

`spikes/classify_curta.py`:

```text
--- OperatingCurta
   jump level           affine     532
   jump level           kinked     15
   law without a plan   affine     183
   law without a plan   kinked     16
   skeleton             None       41
   skeleton             kinked     28
```

`spikes/blame_curta.py`:

```text
--- blame OperatingCurta
   call:cos             17
   call:sin             17
   binop:*              16
   binop:/              8
```

`spikes/attribute_curta.py`:

```text
total evaluations 42519  (14173/tick)
       12900 ( 30.3%) in    100 calls  walk crossing | skeleton None | level affine
       12900 ( 30.3%) in    100 calls  walk crossing | skeleton None | level kinked
       16719 ( 39.3%) elsewhere
```

**100 % of the searched evaluations in those three ticks are under an
UNCLASSIFIED skeleton and none under a kinked one.** This change does
not claim to move that probe; §3 says so, and task 7.4 re-measures it.

## Group 2 — the classification

`solid_node/simulation/program.py`:

- `_KINK_CALLS = ('abs', 'min', 'max')`, beside `_JUMP_CALLS`, with the
  comment saying they are the CONTINUOUS SELECTIONS of
  `SYMBOLIC_BUILTINS` and that each returns one of its operands exactly;
  `_MOVABLE` and `_AFFINE` beside it.
- `_affine_in_sources` / `_degree_of` became `_shape_of` / `_degree_of`,
  three-valued per design.md §4.1. Every existing propagation rule is
  kept: the only additions are the `call` arm (a kink over movable
  operands is `'kinked'`, anything else `None`, exactly as the fall
  through to `return None` gave before) and `_joined`, which carries
  `'kinked'` through `+`, `-`, unary `-`, a constant multiple and a
  constant divisor.
- `_affine_in_sources` itself is REMOVED rather than kept as a wrapper
  (task 2.2 offered either): with `_Jump.affine` and `Edge.affine`
  carrying the two-valued statement, nothing called it, and a helper
  nothing calls is worse than the rename. Deviation recorded here
  because task 2.1 names it.

The internal consumers (task 2.2):

| consumer | before | after |
| --- | --- | --- |
| `_Jump` | `affine` | `shape` + `kinks`, with `affine = shape in _AFFINE` kept for publication |
| `_Retained` | `affine` | `shape` + `kinks` (the skeleton's) |
| `Edge` | `affine` | `shapes` + `kinks` per driven end, with `affine = shape in _AFFINE` kept for publication |
| `run.py:974` | `edge.affine[index]` | `edge.shapes[index] is not None` |

**Publication is not changed (task 2.3).** `Program._published_edge`'s
`list(edge.affine)` and `_published_plan`'s `jump.affine` are untouched:
`affine` stayed a tuple/bool of the SAME two-valued meaning, and the
third value never reaches them. No `openspec/specs/export/spec.md`
delta, no document field, no version bump. The red for it is below.

### 2.4 The classification under direct test

`tests/test_running_jumps.py::ShapeOfTest`: the compositions of
`solid_node/math.py` (`clamp`, `clamp01`, `ramp`, `lerp`, `piecewise`,
`wrap`, `bump`), each of the fourteen `SYMBOLIC_BUILTINS`, the
arithmetic rules, a branch placeholder, and `max(0, sin(x))` — which
stays `None`.

RED, against the tree with `solid_node/simulation/{program,run}.py`
restored from `HEAD`:

```text
ImportError: cannot import name '_shape_of' from 'solid_node.simulation.program'
```

(20 subtests and `test_the_arithmetic_rules`.) GREEN after.

## Group 3 — locating the breakpoints

`_KinkCuts` (program.py), compiled beside the classification:
`self.levels` is one `GraphValue` per kink node in the graph's
POSTORDER, each the kink's own LEVEL (`_kink_level`: `x` for `abs(x)`,
`a - b` for `min`/`max`). `between(at, left, right)` walks the levels in
that order, evaluating each at the two ends of every sub-interval the
earlier ones produced, taking its zero by one division where it lies
strictly inside, and folding the result in through the EXISTING
`_merged` — which gained one parameter, `end` (default `1.0`), so a
bracket inside a piece keeps its own right end exactly. No sampling, no
bisection, no fourth tolerance (confirmed: `grep -n "1e-" program.py
run.py` shows the same three constants as before, task 4.5).

3.2 is the `if high == low` arm, with the comment naming
`_Walk._searched` as the place that already makes the statement.

3.3 is `tests/test_running_jumps.py::KinkedLevelTest::
test_a_kink_is_not_a_crossing`: the `ClampedGate` tick crosses BOTH of
its clamp's kinks and the only crossing recorded is the gate's own
comparison.

## Group 4 — the three solve sites

- **(a) `JumpPlan._crossings_of`.** The affine body moved to
  `JumpPlan._solved(..., closed=False)`, byte-equivalent at
  `closed=False`. A KINKED level sub-divides the piece at
  `jump.kinks.between(...)` and solves each sub-piece with
  `closed=True` for all but the last; `closed` takes `_surfaces`
  inclusively and then drops a surface equal to the sub-piece's own LEFT
  value, which is "left-exclusive, right-inclusive" — the convention
  design.md §4.4 (a) states. The result goes through the existing
  `_deduplicated`.
- **(b) `_Walk._crossing`.** Unchanged where both are affine. Where
  either is kinked and neither is curved, the piece is cut at
  `_skeleton_cuts` first and each skeleton sub-piece at `_level_cuts`,
  with `own_at` evaluated at the sub-piece's two ends and interpolated
  between them for the level's own breakpoint search. `_solved` keeps
  `_first_cut`'s "first surface strictly inside the piece" and the
  left-exclusive end.
- **(c) `Edge.cuts`.** Now returns the union of the plan's (or the
  walk's) cuts and the SKELETON's kink breakpoints. For a plan-less
  kinked law it returns a partition over the whole tick where a kink is
  reached and `()` where none is. For a law WITH a plan it computes the
  skeleton's breakpoints inside each plan PIECE, with that piece's
  branch placeholders substituted through `plan._branches`, and unions
  them through `_merged`. For a self-read law the union happens inside
  `_Walk.run`, which gained a `cutting=False` parameter so an ordinary
  tick pays nothing: only `_Retained.cuts` asks for them.
- **4.3** `Edge._affine_ends` became `Edge._end_shapes`; the block arm
  returns `[None] * len(gives)` with the comment saying WHY this change
  does not lift it (design.md §7).
- **4.5** `Run._locate` / `Run._piecewise` unchanged in shape; `_locate`
  reads `edge.shapes[index] is not None` instead of `edge.affine[index]`.

## Group 5 — the fixtures and the red tests

New fixtures in `tests/running_project/machine.py`: `KinkedStopBody` /
`KinkedStop` (5.1), `ClampedGateBody` / `ClampedGate` (case A) and
`CappedCountBody` / `CappedCount` (the surface-on-a-breakpoint case of
task 4.1), with `clamped_gate` and `capped_count` beside the module's
other laws. `solid_node.math.min` joined the module's imports.

`graph_evaluations` was lifted out of
`tests/test_running_stops.py::ConstraintCostTest` into `tests/base.py`
(task 5.4), where the method now delegates to it.

**Deviation, task 5.4.** The cost assertion does NOT use
`graph_evaluations`: that probe counts `program_module._evaluated`,
which a law carrying a JUMP PLAN never reaches — measured, it returns
**0** for `Clearing` and for `CurtaInterface`, so it cannot see a walk's
cost at all. The proposal's 2 861.3 was measured with a
`GraphValue.evaluate` counter (`spikes/kink_baseline.py`), so a second
shared helper, `expression_evaluations`, was added to `tests/base.py`
with that counter and the docstring saying why. `graph_evaluations` was
still lifted, as the task asks.

### 5.2 Case C — the stop on a kinked determiner with no jump plan

`tests/test_running_stops.py::KinkedDeterminerStopTest`. The expected
fraction is restated from the fixture's own arithmetic:
`(113.5 + 0.5 * 11.25 - 100.0) / 40.0 == 0.478125`.

RED 1, the SEARCHED answer on the unmodified tree:

```text
>       self.assertEqual(sim.stops[0].t, self.EXACT)
E       AssertionError: 0.47812500000009095 != 0.478125
>       self.assertEqual(sim.state['lever'], 100.0 + 40.0 * self.EXACT)
E       AssertionError: 119.12500000000364 != 119.125
>       self.assertEqual(edge.shapes[index], 'kinked')
E       AttributeError: 'Edge' object has no attribute 'shapes'
```

RED 2, the MATERIALLY WRONG one — the implementation with `Edge.cuts`
patched to keep returning `()` for a plan-less law (`return ()  # NAIVE
RED PATCH`, reverted immediately afterwards):

```text
>       self.assertEqual(sim.stops[0].t, self.EXACT)
E       AssertionError: 0.5 != 0.478125
>       self.assertEqual(sim.state['lever'], 100.0 + 40.0 * self.EXACT)
E       AssertionError: 120.0 != 119.125
>       self.assertEqual(len(across), 3)
E       AssertionError: 0 != 3
```

The stop at half way, and **0.875 degrees of lever travel admitted that
never happened**. That is the answer this test exists to catch.

GREEN: `t == 0.478125` exactly, `slide.travel == 40.0`,
`lever == 119.125`, and `Edge.cuts` empty for a tick that stays between
the kinks and `(0.0, 0.24375, 1.0)` for one that crosses the upper one
at `lever == 124.75`.

### 5.3 Case A — a kinked jump level

`tests/test_running_jumps.py::KinkedLevelTest::
test_a_clamped_gates_crossing_is_solved`. `ClampedGate`'s level is
`clamp01((lever - 10) / 20) - 0.5` and the tick carries the lever from 5
to 42, so the surface is at `lever == 20`, on the clamp's sloped piece.
Closed form: `(20.0 - 5.0) / 37.0 == 0.40540540540540543`.

RED (unmodified tree):

```text
E       AssertionError: 1.226796442210798e-14 not less than 2.220446049250313e-16
```

GREEN: `0.4054054054054054` — one unit in the last place.

And task 4.1's boundary, `CappedCount`: `min(lever, 20)` rises and then
holds, so the `floor`'s last surface, 20, is reached EXACTLY at the
kink.

RED (unmodified tree — the search reports the surface EIGHT times, none
of them at the breakpoint):

```text
E       AssertionError: Lists differ:
E       - [(20.0, 0.875), (20.0, 0.890625), (20.0, 0.90625), (20.0, 0.921875),
E          (20.0, 0.9375), (20.0, 0.953125), (20.0, 0.96875), (20.0, 0.984375)]
E       + [(16.0, 0.1), (17.0, 0.2), (18.0, 0.3), (19.0, 0.4), (20.0, 0.5)]
```

GREEN: five crossings, 20.0 located ONCE, at exactly `0.5`.

### 5.4 Case B — a kinked skeleton under a self-read

`tests/test_running_reads.py::KinkedSkeletonTest`.

RED (unmodified tree):

```text
E       AssertionError: 2861.35 not less than 900.0
```

GREEN: 602.6 expression evaluations per tick, and `Clearing`'s 986 over
ten ticks asserted EXACTLY unchanged.

The exactness half, and **a deviation from design.md §12** worth the
reviewer's judgement:

```text
spikes/exactness.py, after:
exact control at reach == 0 : 0.26833333333333337
tick 17 exact t 0.10000000000000231
  recorded >= level 0.0 t 0.10000000000000142  error -8.881784197001252e-16
```

`9.3e-14` became `8.9e-16` — a **105-fold** improvement — but that is
64 ulp of `0.1`, not the `≤ 4 ulp` §12's table states. The reason is
that **the reference in `exactness.py` and design.md §2 D is itself the
less accurate of the two numbers.** Computing the same crossing in exact
rational arithmetic from the fixture's own float constants
(`fractions.Fraction`) gives `0.10000000000000114`:

| answer | value | ulp from the rational truth |
| --- | --- | --- |
| rational exact | `0.10000000000000114` | 0 |
| the SOLVE | `0.10000000000000142` | **20** |
| `exactness.py`'s reference | `0.10000000000000231` | 84 |
| the SEARCH, before | `0.09999999999990905` | ~6 700 |

What is left in the solve's 20 ulp is the rounding the LEVEL's own
evaluation carries — `ORIGIN + SWEEP * clamp01(...) - start` over a
5-degree span at `t ≈ 0.1` — not the localization, which adds one
division. **No localization that interpolates evaluated level values can
reach 4 ulp here**, so §12's figure is not achievable by any
implementation of this design; it is a property of the reference, not of
the mechanism. The test therefore asserts against the RATIONAL exact
answer, at `< 1e-15`, and says so in its docstring. Recorded here rather
than silently widened.

### 5.5 Case E — a curved law is searched exactly as before

`KinkedLevelTest::test_a_curved_level_is_searched_exactly_as_before`:
`NonAffine`'s product-of-two-movers level reports the same nine
crossings before and after (the list was read off the UNMODIFIED tree
and asserted; it passed under both). `max(0, sin(x))` classifies `None`
in `ShapeOfTest`.

### 5.6 Case D — the numbers that must not move

`Train` 8.0 and `Clearing` 98.6 evaluations per tick are asserted in
`spikes/kink_baseline.py`'s after run (group 7) and, for `Clearing`,
directly in `KinkedSkeletonTest` (`986` over ten ticks, exactly).
`Clearing`'s committed values are pinned by its two corpus scenarios,
byte-identical below.

### 5.7 Case D — the DOCUMENT

`tests/test_running_document.py::KinkedPublicationTest`: a kinked law
with no jump publishes `affine: [false]`; a kinked jump level publishes
`affine: false`; `Train`'s `lever drives slide.travel` edge is equal to
the one in the committed base document.

RED, against the IMPLEMENTATION with the publication plumbed through to
the new shape (`affine = shape is not None`, in both `_Jump.__init__`
and `Edge.__init__`, reverted immediately afterwards):

```text
>       self.assertEqual(law[0]['affine'], [False])
E       AssertionError: Lists differ: [True] != [False]
>       self.assertFalse(jumps[0]['affine'])
E       AssertionError: True is not false
>       self.assertEqual(edge['affine'], [False])            # the pre-existing
E       AssertionError: Lists differ: [True] != [False]      # Window test
>       self.assertEqual(json.dumps(published, indent=2) + '\n', expected)
E       AssertionError: '... true ...' != '... false ...'    # ByteIdentityTest,
E                                                            # running_train.json
```

GREEN with the publication left alone: 110 passed.

## Group 6 — the corpus

6.1 `tools/generate_running_corpus.py` gains ONE scenario, `KinkedStop`
at `dt = 0.1` over 4 steps, and ONE `REQUIRED` entry, **`'a stop on a
kinked determiner inside a tick'`**, derived in `uncovered_features`
from the committed ticks by `_kinked_laws(program, bindings)`: the
coordinates a law with a NULL plan drives whose published expression
calls `abs`, `min` or `max`, resolved through the document's own
`bindings` table by a new `_calls` beside the existing `free_names`.
Reproducible from the document alone, which is what the viewer's
hand-mirrored `uncoveredFeatures` needs (task 10.2 (d)).

6.2 Regenerated with the tool:

```
PYTHONPATH="$PWD" python tools/generate_running_corpus.py
```

```text
tests/running-corpus.json: 20 scenarios over 17 machines (…, KinkedStop, …),
360 ticks, 267185 bytes
```

Diffed against the committed file, scenario by scenario:

```text
removed: []
added: [('KinkedStop', 0.1, 4)]
changed: []
generated_by / corpus / tolerance: unchanged
```

and as bytes, `git diff --stat tests/running-corpus.json`:

```text
 tests/running-corpus.json | 167 ++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 167 insertions(+)
```

**167 insertions, 0 deletions** — a pure insertion at the end of the
file. The 19 pre-existing scenarios are byte-identical, as design.md §6
requires.

Independently, BEFORE the corpus was touched at all, the implemented
tree regenerated the 19-scenario corpus to a file that `diff` reported
IDENTICAL to the committed one.

6.3 The new scenario's document declares `"version": 5` — the version
the tree already publishes for a machine with no self-read and no block
— and its law publishes `"affine": [false]` with `"plans": [null]`. Its
one stop:

```text
tick 1  slide.travel  bound high  value 40.0  t 0.478125  inputs ['lever']
bank: lever 119.125, slide.travel 40.0
```

6.4 `tests/test_running_corpus.py` green, `BlockOrderTest` included, and
one test added beside the other coverage-guard tests:
`test_a_corpus_with_no_kinked_determiner_stop_is_refused`. Verified
directly:

```text
full corpus missing: []
without KinkedStop: ['a stop on a kinked determiner inside a tick']
```

## Group 7 — performance

### 7.1 `spikes/kink_baseline.py 5`, after

```text
Train            ticks   10  best      4.64 ms  median      4.67 ms    2155.8 ticks/s  80 evaluations = 8.0/tick
Clearing         ticks   10  best      6.94 ms  median      7.01 ms    1441.3 ticks/s  986 evaluations = 98.6/tick
CurtaInterface   ticks   60  best    452.91 ms  median    454.11 ms     132.5 ticks/s  36157 evaluations = 602.6/tick
```

Against design.md §12's acceptance:

| measure | before | acceptance | after |
| --- | --- | --- | --- |
| `CurtaInterface` evaluations/tick | 2 861.3 | ≤ 900 (≈ 640 expected) | **602.6** |
| `CurtaInterface` ticks/s | 27.8 | ≥ 120 (≈ 180 expected) | **132.5** |
| `Train` evaluations/tick | 8.0 | 8.0 exactly | **8.0** |
| `Clearing` evaluations/tick | 98.6 | 98.6 exactly | **98.6** |

Both "must hit" cost figures pass on the first run; no judgement band
was entered. The ulp figure is the deviation recorded under 5.4.

### 7.2 `tools/bench_selection.py 5`

| machine | before | after |
| --- | --- | --- |
| `Train` (the control, no block) | 0.468 | 0.451 ms/tick |
| `FixedZero` | 0.760 | 0.754 ms/tick |
| `ShiftedCarry`, quiet | 1.248 | 1.242 ms/tick |
| **`RangedBlock`** | **16.142** | **16.032 ms/tick** |
| `ShiftedCarry`, the crossing tick | 2.374 | 2.613 ms/tick |
| `CurtaCarriage` | 9.815 | 10.681 ms/tick |

All within the repeats' spread; `RangedBlock` is unchanged, as §7
requires. The last two sit a little above their design.md §2 C figures
and a little below/above between repeats on a machine that also moved
`Train`'s control by 4 %; no block quantity is reclassified
(`spikes/classify_fixtures.py`: `ShiftedCarry`, `RangedBlock` and
`CurtaCarriage` carry NO kink in any followed quantity), so there is no
mechanism by which this change could cost them.

### 7.3 `spikes/attribute_fixtures.py`, after

```text
== CurtaInterface, 60 ticks
total evaluations 36157  (603/tick)
       36157 (100.0%) elsewhere
== Clearing, 10 ticks
total evaluations 986  (99/tick)
         986 (100.0%) elsewhere
```

**Both search rows are gone.** Not reduced to a residue: no evaluation
of `CurtaInterface` reaches `_Walk._searched` or `JumpPlan._searched` at
all.

### 7.4 The Curta, re-measured read-only

```text
constructed 5.509367475984618
tick 1 seconds 3.4828962679603137
tick 2 seconds 2.9583915310213342
tick 3 seconds 3.441939388983883
```

Against the before run's 5.268 / 3.270 / 2.941 / 3.361 and design.md
§3's 5.300 / 3.287 / 2.799 / 3.378: within its own spread, which is the
expected and acceptable result. `git status --short` in that project
is unchanged (`M pyproject.toml`, `?? screenshots/`); nothing was
modified or committed there.

## Group 9 — documentation

- `docs/driving.rst`: a new section, "What a law costs under a running
  root", in an author's terms — what solves, what searches, what that
  costs, and that a profile written with `clamp01` costs almost nothing
  where the same profile written with a `sin` costs the search.
- `docs/scenarios.rst`: the "AFFINE … anything else is sampled"
  paragraph now states the piecewise-affine case; the `t*`-is-exact
  sentence and the leaves-and-returns limitation were swept and
  corrected for the same reason.
- `docs/architecture.md`: the jump-plan and stop-localization accounts
  in the Simulation section, `Edge.shapes` beside `Edge.affine`, and the
  "A kinked but piecewise-affine skeleton falls to the search" bullet
  REMOVED from "Known gaps and tensions" and replaced by the per-BRANCH
  gap (§8). The block-give bullet is left standing.
- `HISTORY.rst`: an Unreleased entry in the voice of the two above it.
  No breaking note: no document version moves.
- `workflow/warts.md`: the `read-the-driven-coordinate` entry is now
  "TAKEN UP as `cut-at-the-kink` (ADR-123)" with the after numbers; the
  `select-the-source` restatement is "FIXED by `cut-at-the-kink`"; and
  the block-give entry is left OPEN with a line saying this cycle
  examined it and found it a different mechanism.
- `docs/adrs/NODE/ADR-123-a-kink-is-a-cut.md` and its `docs/adrs/README.md`
  index line are **DRAFTS**, written because the review reads them with
  the code. Task 9.6 is the reviewer's direction.

### The ratified scenario "A path that crosses the kink is cut there before it is solved"

`tests/test_running_jumps.py::KinkedLevelTest::
test_a_path_that_crosses_the_kink_is_cut_there_first`, added because the
ADDED requirement states it as a scenario of its own. `ClampedGate`'s
lever falls from 35 — above the clamp's upper kink, where the ramp is
flat at 1 — through that kink at `lever == 30` and on to 10, with the
gate's surface at `lever == 20` on the SLOPED piece beyond it. The
crossing lands at `(35 − 20) / 25 == 0.6` to one unit in the last place,
and the same straight path taken as TWO ticks meeting at the kink gives
the same 54 degrees of `wheel.turn`, exactly on the split reading and to
one ulp on the whole one.

RED, against the tree with `solid_node/simulation/{program,run}.py`
restored from `HEAD`:

```text
>       self.assertLess(abs(whole.crossings[0].t - exact),
E       AssertionError: 9.092726571680032e-14 not less than 4.440892098500626e-16
```

## Group 8 — the suites

### 8.1 The five named regression files plus the corpus

```
PYTHONPATH="$PWD" python -m pytest tests/test_couplings.py \
    tests/test_running_simulation.py tests/test_running_jumps.py \
    tests/test_running_stops.py tests/test_running_reads.py \
    tests/test_running_document.py tests/test_running_corpus.py -q
```

```text
559 passed, 2 warnings, 792 subtests passed in 41.86s
```

### 8.2 The whole suite, sequential, one job

```
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH="$PWD" \
    python -m pytest tests -q -p no:cacheprovider
```

```text
3022 passed, 4 skipped, 53 warnings, 1718 subtests passed in 335.65s (0:05:35)
```

| | tests | skipped | subtests | time |
| --- | --- | --- | --- | --- |
| before, unmodified tree | 3 005 | 4 | 1 679 | 327.65 s |
| after | **3 022** | 4 | **1 718** | 335.65 s |

`+17` tests and `+39` subtests — the four new test classes and the two
lifted helpers — with zero failures, zero errors and no new skip.

`openspec validate cut-at-the-kink`: `Change 'cut-at-the-kink' is valid`.
