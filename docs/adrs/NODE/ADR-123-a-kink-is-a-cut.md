# ADR-123: A Kink Is a Cut, and a Piecewise-Affine Quantity Is Solved

**Status:** Accepted
**Date:** 2026-09-16
**Depends on:**
- [ADR-107: A jump is located inside the tick and subtracted](./ADR-107-a-jump-is-located-inside-the-tick-and-subtracted.md) — the partition this sub-divides
- [ADR-108: A range is a physical stop that stops the connected group](./ADR-108-a-range-is-a-physical-stop-that-stops-the-connected-group.md) — the stop whose localization this solves
- [ADR-121: A law may read the coordinate it drives](./ADR-121-a-law-may-read-the-coordinate-it-drives.md) — the walk whose skeleton this classifies
**Amends:**
- [ADR-107](./ADR-107-a-jump-is-located-inside-the-tick-and-subtracted.md) — "solved exactly where the level quantity is affine … otherwise sampled": a PIECEWISE AFFINE level is solved too, on the pieces between its own kinks
- [ADR-108](./ADR-108-a-range-is-a-physical-stop-that-stops-the-connected-group.md) — the same sentence for a stop's localization: a kinked determiner is solved over its kink breakpoints, and a law with no jump plan now has breakpoints at all
- [ADR-121](./ADR-121-a-law-may-read-the-coordinate-it-drives.md) — the same sentence for a self-read walk: the SKELETON's kinks are what make the driven coordinate's own path affine, and the level's ride inside them
- [ADR-122](./ADR-122-a-selection-decides-which-sources-a-law-reads.md) — the same sentence for a SELECTOR's level, which is located through the jump partition like any other
**Cites:**
- [ADR-110: The compiled program is published in the document](../EXPORT/ADR-110-the-compiled-program-is-published-in-the-document.md) — the `affine` flag this deliberately leaves two-valued
- [ADR-111: A conformance corpus is the contract between the two runtimes](../EXPORT/ADR-111-a-conformance-corpus-is-the-contract-between-the-two-runtimes.md)
**OpenSpec change:** `cut-at-the-kink`

## Context and Problem Statement

Under a running root the run has to FOLLOW a quantity along each tick's
path: a jump node's LEVEL, to find where it reaches a surface; a law's
SKELETON, to know the driven coordinate's own path under a self-read; a
determiner's VALUE, to locate a declared stop. It did that one of two
ways, decided once at compile by `_affine_in_sources`. Where the
quantity was AFFINE in the sources it SOLVED — two evaluations and one
division, exact. Everywhere else it SEARCHED — 64 samples per piece and
up to 64 bisection rounds behind each bracket.

`_affine_in_sources` called every CALL non-affine. Its own docstring
said what that cost: "`floor(max(x, 0))` is searched although it is
piecewise affine". That is not an edge case. `clamp01` is
`min(max(x, 0), 1)` — two kinks whose three pieces are each perfectly
affine — and it is how the framework's own `clamp`, `ramp` and
`piecewise` are built. `piecewise` is the pose model's normal spelling
of a motion profile.

The originating project is `projects/Calculators/Curta-Type-I-3x`,
branch `direct-operation`, HEAD `9fb725f`, whose clearing interface is
exactly that shape: a ring angle
`ORIGIN + SWEEP * clamp01((control - 0.1) / 0.8)` gating six register
dials, each a self-read. The finding was filed by
`read-the-driven-coordinate` and restated by `select-the-source` as the
reason the Curta's own migration had to write its carriage association
as comparisons instead of the pose model's `1 − clamp01(abs(…))` hat.

Measured on the framework's own fixtures (`spikes/kink_baseline.py`,
`spikes/attribute_fixtures.py`):

| fixture | shape | ticks/s | evaluations/tick |
| --- | --- | --- | --- |
| `Train` | no self-read | 2 171 | 8.0 |
| `Clearing` | affine skeleton, SOLVED | 1 428 | 98.6 |
| `CurtaInterface` | `clamp01` window, SEARCHED | 27.8 | 2 861.3 |

and **84.5 % of `CurtaInterface`'s evaluations were inside exactly two
call sites** — a self-read walk's crossing under a kinked skeleton
(56.8 %) and a jump plan's crossing under a kinked level (27.7 %).

The cost was not the whole of it. A searched crossing is also less
EXACT: the crossing of the first result dial's rack was recorded
9.3e-14 from the closed-form answer of the same affine level, against a
float spacing of 1.4e-17 there.

## Decision

**`abs`, `min` and `max` are KINKS, and a kink is a cut.**

They are the CONTINUOUS SELECTIONS of the symbolic vocabulary: each
returns ONE OF ITS OPERANDS EXACTLY, and is continuous where the
operands meet. Of `SYMBOLIC_BUILTINS`, three (`floor`, `ceil`, `sign`)
are already JUMP nodes, planned and located; eight (`sin`, `cos`, `tan`,
`asin`, `acos`, `atan`, `atan2`, `sqrt`) are genuinely curved; these
three are the whole of the gap.

1. **A three-valued classification.** `_affine_in_sources` becomes
   `_shape_of`, returning `'constant'`, `'affine'`, `'kinked'` or
   `None`. `'kinked'` propagates exactly where `'affine'` does — a sum,
   a difference, a unary minus, a constant multiple, a division by a
   constant — and is introduced only by a kink node over operands that
   are themselves movable. Structural, computed once at compile, no new
   author-facing spelling and NO KNOB. It is conservative: a kink over a
   CURVED operand (`max(0, sin(x))`) is not classified, even though one
   of its pieces may happen to be straight.

2. **A kink's breakpoints are solved, not sampled.** A kink node has a
   LEVEL of its own — `x` for `abs(x)`, `a − b` for `min(a, b)` and
   `max(a, b)` — and ONE surface, at zero. Over a stretch the kinks are
   taken in the graph's POSTORDER, exactly as `JumpPlan._partition`
   takes the jump nodes and for the same reason: on each sub-interval
   the kinks inside it have already produced, the level is affine, so
   its zero is one division. No sampling, no bisection, and NO FOURTH
   TOLERANCE — two breakpoints closer than the crossing tolerance are
   one, exactly as two crossings are.

3. **A kink breakpoint is NOT a crossing.** The quantity is CONTINUOUS
   there. So it is not recorded among the tick's crossings, never enters
   the partition a law's increment is summed over, never triggers the
   far-side landing, and does not count toward the crossing maximum. It
   exists only as a sub-division inside a SOLVE. **This is what keeps
   every existing answer bit-identical.**

4. **Three solve sites take the sub-division.** A jump node's crossings
   (the right end inclusive for every sub-piece but the last, so a
   surface exactly on an interior breakpoint is located once); a
   self-read walk's crossings (the SKELETON's breakpoints first, because
   they are what make the driven coordinate's own path affine at all,
   and the LEVEL's located inside each of them, because the level rides
   that path); and a stop's localization, where the edge's cuts are now
   the union of the plan's partition and the skeleton's kink
   breakpoints — computed inside each plan piece with that piece's
   branch placeholders substituted, and computed at all for a law that
   carries NO jump plan, which is the shape that previously took the
   one-division fast path straight THROUGH a kink.

5. **The published document does not change.** The document says, per
   driven end of a law and per jump, whether that quantity is AFFINE in
   its sources — a TWO-VALUED statement a consumer uses to choose
   between a solution and a search. A piecewise-affine quantity is not
   affine, so it publishes `false`, exactly as before. The third value
   is INTERNAL to the Python runtime. No document field is added, no
   version moves, and a consumer that has not learned to cut at a kink
   goes on searching such a quantity — correct, and slower.

## Considered Options

- **Rewrite a kink into a comparison-gated form** (`min(a,b)` as
  `a·(a<b) + b·(a>=b)`), reusing the jump machinery whole. Rejected: it
  turns a CONTINUOUS node into a JUMP — recorded crossings where nothing
  jumps, a far-side landing on a surface with no gap, a partition the
  increment is re-summed over, and every existing answer moved by
  rounding.
- **Make kink breakpoints ordinary cuts of the tick's partition.**
  Architecturally tidier, and it changes numbers: `f(c) − f(a) +
  f(b) − f(c)` is not `f(b) − f(a)` in floats, so every existing machine
  carrying a kink would move by ulps and the corpus would need
  regenerating for no behavioural gain. Rejected; the breakpoints stay
  inside the solve.
- **Substitute the selected branch into the skeleton per piece.**
  Unnecessary: `min` and `max` RETURN one operand exactly, so evaluating
  the node already evaluates the selected branch, bit for bit.
- **A knob** — `solve=True`, a subdivision count, a tolerance. Refused:
  the classification is structural, and an author must not have to set
  anything to get an exact answer.
- **Lower the subdivision count.** Cheaper and less exact, in a way that
  depends on sample-count luck.
- **Newton or a secant iteration on the searched path.** A fourth
  tolerance and an iteration count, which ADR-121 already rejected for
  the same reason.

## Consequences

- **Measured, on the same probes** (`spikes/kink_baseline.py 5`,
  `spikes/attribute_fixtures.py`):

  | measure | before | after |
  | --- | --- | --- |
  | `CurtaInterface` evaluations/tick | 2 861.3 | **602.6** |
  | `CurtaInterface` ticks/s | 27.8 | **132.5** |
  | its two search call sites | 84.5 % of the cost | **0 %** |
  | `Train` evaluations/tick | 8.0 | 8.0, exactly |
  | `Clearing` evaluations/tick | 98.6 | 98.6, exactly |

- **Nothing that worked before moved.** `tests/running-corpus.json` is
  byte-identical for all 19 pre-existing scenarios, although five of its
  machines have a RECLASSIFIED determiner (`Captured`, `CarryLead`,
  `Remainder`, `Train`, `Window`): none of the corpus's ten recorded
  stops is on one of those coordinates. `Train`'s published document is
  byte-identical. `tools/bench_selection.py`'s six numbers are within
  their spread, `RangedBlock`'s 16.0 ms/tick included.

- **A searched crossing was also less exact, and that improves too.**
  `CurtaInterface`'s tick-17 crossing moved from 9.3e-14 off its exact
  answer to 8.9e-16 — a hundredfold. What is left is the rounding the
  LEVEL's own evaluation carries over its span, not the localization's:
  against the exact rational solution of the same affine problem, the
  solve is 20 ulp out and the search was 6 700.

- **The two runtimes now locate a kinked crossing differently.** Python
  solves it; the viewer, reading `affine: false`, still searches it. They
  agree inside the corpus's own `1e-9` relative window, which is how the
  corpus compares a crossing's fraction, and no viewer change is
  required for CORRECTNESS. A viewer that wants the solve cannot
  re-derive the shape from the document — nothing there says whether a
  non-affine quantity is kinked or curved — so it needs a new document
  field or a redefinition of `affine` under a version bump: two changes
  in two repositories, not taken here.

- **The corpus gains one scenario**, `KinkedStop`: a coordinate
  declaring a range driven by `4 + 72 * clamp01((lever − 113.5) / 11.25)`
  with no jump node in it at all, the bound on the sloped piece and the
  tick starting on the flat one. A consumer that divides once over the
  whole tick puts the stop at half way and admits 0.875 degrees of lever
  travel that never happened. `uncovered_features` refuses a corpus
  without it, and its derivation — a stop on a law with a null plan whose
  expression calls `abs`, `min` or `max` — is reproducible from the
  document alone.

- **A stop on a BLOCK coordinate is still searched.** This ADR does not
  lift it, and the reason is that it is a different obstruction: a block
  has no single expression until a branch vector is fixed, and the ORDER
  its members run in may differ from piece to piece. Classifying a give
  would mean classifying it per branch vector AND proving the order
  stable on the piece — ADR-122's territory, not a kink in an
  expression.

- **The classification stays per EDGE, not per PIECE.** A kink can pin a
  curved subtree to a constant on one of its pieces — the Curta's detent
  cam is affine through its dwell and curved through its rise — so a
  run-time classification per piece would solve strictly more. It costs
  a classification per piece per tick instead of one per edge at
  compile, and it makes the answer depend on which piece you are in.
  Recorded as a known gap rather than taken.

- **This does not make the real `OperatingCurta` interactive, and does
  not claim to.** Measured at 3 ticks against this change: construction
  5.51 s, ticks 3.48 / 2.96 / 3.44 s — within its own spread before and
  after. Of its 69 skeletons, 28 become piecewise affine and 41 stay
  unclassified, because the dial cam laws carry `sin`, `cos` and `sqrt`
  of a moving phase; **100 % of the searched evaluations in three
  measured ticks are under one of those 41, and none under a kinked
  one.** That attribution is this cycle's contribution to the
  seconds-per-tick finding, which is a separate cycle.
