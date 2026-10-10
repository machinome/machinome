## Why

The run locates a crossing one of two ways. Where the quantity it has to
follow is AFFINE in the sources along the tick's path, it SOLVES: two
evaluations at the ends of a piece and one division. Where it is not, it
SEARCHES: 64 samples per piece, and up to 64 bisection rounds behind each
bracket it finds. `_affine_in_sources` decides which, and it calls every
CALL non-affine — so `clamp01`, which is `min(max(x, 0), 1)`, two kinks
whose three pieces are each perfectly affine, is searched.

That is not an edge case. `clamp01` is how the framework's own
`clamp`, `ramp` and `piecewise` are built, and `piecewise` is the pose
model's normal spelling of a motion profile. It is also the shape of the
originating project's clearing interface: `projects/Calculators/Curta-Type-I-3x`,
branch `direct-operation`, HEAD `9fb725f`. The finding was filed by
`read-the-driven-coordinate` as "A kinked but piecewise-affine skeleton
falls to the 64-sample search where an exact path exists"
(`workflow/warts.md`), restated by `select-the-source` as the reason the
Curta's own migration had to write its carriage association as
comparisons instead of the pose model's `1 − clamp01(abs(…))` hat, and
recorded in `docs/architecture.md` under "Known gaps and tensions".

**Measured on this worktree** (commands and full tables in design.md §2):

| fixture | shape | ticks/s | `GraphValue` evaluations per tick |
| --- | --- | --- | --- |
| `Train` | no self-read at all | 2 288 | 8.0 |
| `Clearing` | affine skeleton, crossings SOLVED | 1 528 | 98.6 |
| `CurtaInterface` | `clamp01` window, crossings SEARCHED | 28.2 | 2 861.3 |

and **84.5 % of `CurtaInterface`'s evaluations are inside exactly two
call sites** — `_Walk._searched` under a kinked skeleton (56.8 %) and
`JumpPlan._searched` under a kinked level (27.7 %) — both of which this
change replaces with an exact solve.

The cost is not the whole of it. A searched crossing is also LESS
EXACT than a solved one, by orders of magnitude more than a float:
on `CurtaInterface`, the recorded crossing of the first result dial's
rack sits at `0.09999999999990905` where the exact solution of the same
affine level is `0.10000000000000231` — **9.3e-14 out**, against a float
spacing of 1.4e-17 there. The framework already promises exactness where
it can compute it; this shape is one where it can and does not.

## What Changes

- **A new classification.** `_affine_in_sources` becomes a three-valued
  `_shape_of`: AFFINE as today, PIECEWISE AFFINE where the only
  obstructions are KINK NODES — `abs`, `min`, `max`, the continuous
  selections of `SYMBOLIC_BUILTINS`, each of which returns one of its
  operands exactly — over operands that are themselves affine or
  piecewise affine, and unclassified otherwise. Structural, computed
  once, no new author-facing spelling and no knob.
- **A kink is located as a cut.** A kink node has a level (`x`, or
  `a − b`) and one surface, at zero. Its breakpoints over a stretch are
  solved in the graph's postorder — each kink's level being affine on the
  sub-intervals its inner kinks have already produced — with no sampling,
  no bisection and no new tolerance.
- **Three solve sites take those sub-divisions.** A jump node's crossings
  (`JumpPlan._crossings_of`), a self-read walk's crossings
  (`_Walk._crossing`), and a stop's localization (`Run._locate` /
  `_piecewise` through `Edge.cuts`, which must now yield kink breakpoints
  even for a determiner carrying no jump plan at all).
- **A kink breakpoint is not a crossing.** It is not recorded, does not
  enter the partition a law's increment is summed over, moves no
  coordinate to the far side of anything and does not count toward the
  crossing maximum. This is what keeps every existing answer identical.
- **`tests/running_project/machine.py` gains one fixture** — a range on a
  coordinate driven by a kinked law with no jump — and the corpus gains
  one scenario over it, so the new exact path is in the contract between
  the two runtimes.
- Documentation: `docs/driving.rst` (which quantities solve and which are
  searched), `docs/architecture.md` (the Simulation section, and the
  removal of the "A kinked but piecewise-affine skeleton falls to the
  search" gap), `HISTORY.rst`, and the two `workflow/warts.md` entries.
- One ADR, **ADR-123** (NODE), extracted after implementation: a kink is
  a cut, and a piecewise-affine quantity is solved. It amends ADR-107's
  "where the level quantity is affine … otherwise sampled" and the same
  sentence as restated by ADR-108, ADR-121 and ADR-122.

### What must not move

- `Train`: 8.0 evaluations per tick, exactly.
- `Clearing`: 98.6 evaluations per tick, exactly, and every committed
  value.
- **`tests/running-corpus.json` byte-identical for all 19 existing
  scenarios.** Five corpus machines get a reclassified determiner
  (`Captured`, `CarryLead`, `Remainder`, `Train`, `Window`) and NO
  committed stop anywhere in the corpus is on one of those coordinates,
  so nothing in the file may change (design.md §6 has the audit, and it
  is a red-first task to confirm it on the implementation).
- **Every published document, byte for byte**, including its `affine`
  flags: a kinked law still publishes `affine: false` for that driven end
  and a kinked jump still publishes `affine: false`. `Program.published()`
  is not touched, and that is asserted red-first.
- `pin-the-block-order`'s discrimination of the block's listing order.
- The stop, selection, retained-state and transactional semantics, whole.

### Non-goals

- **Making the real `OperatingCurta` interactive.** Measured on this
  worktree at 3 ticks: construction 5.300 s, ticks 3.287 / 2.799 /
  3.378 s — and **none of that cost is in the path this change fixes**.
  Of its 69 skeletons, 28 become piecewise affine and 41 stay
  unclassified because the dial cam laws carry `sin`, `cos` and `sqrt` of
  a moving phase (`simulation/dial_cam.py`); 100 % of the searched
  evaluations in three measured ticks are under one of those 41
  (design.md §3). This change is the exact path for the kinked shape, not
  a speed-up of that machine; Astra's `seconds per Python tick` wart is a
  separate cycle and this one supplies its attribution.
- **A per-BRANCH classification.** A kink can pin a curved subtree to a
  constant on one of its pieces — the Curta's cam is affine (constant)
  through its dwell and curved through its rise — so classifying per
  piece at run time would solve strictly more. It costs a per-tick,
  per-piece classification instead of a compile-time flag. Recorded as
  evidence for the next cycle, deferred here (design.md §8).
- **A stop on a BLOCK coordinate.** The neighbouring wart from
  `select-the-source` is a DIFFERENT mechanism and is NOT fixed here:
  `_Block._affine_ends` returns `False` by construction not because the
  block's value is curved but because it is piecewise in the SELECTOR
  partition and RE-ORDERED across it, so affinity would have to be
  established per branch vector together with the stability of the order
  on that piece. Explicitly deferred (design.md §7); `RangedBlock`'s
  16.1 ms tick is unchanged, and the change asserts that it is.
- **A bound that reads other coordinates.** `Run._searched_constraint`
  samples by construction, because a constraint level carries a
  comparison in every sighting. Untouched, explicitly.
- **A new tolerance, a new knob, a new spelling, or a document change.**
  The published document DOES carry a classification — `affine` per
  driven end of a law and `affine` per jump, specified by
  `openspec/specs/export/spec.md` — and this change leaves that flag
  two-valued, unchanged in meaning and unchanged in value: a KINKED
  quantity keeps publishing `affine: false`, because that is what it
  means to a consumer that has not learned to cut at a kink. The
  three-valued shape is INTERNAL to the Python runtime in this cycle. So
  the document keeps its version, the five reclassified corpus machines
  publish the bytes they publish today, and the viewer keeps SEARCHING a
  kinked quantity — correct, slower, and inside the corpus's own `1e-9`
  relative window (design.md §9). A viewer that wants the solve needs the
  SHAPE in the document, which is a document field (or a redefinition of
  `affine`) under a version bump: two changes in two repositories, and a
  follow-up this change records rather than takes.

## Impact

- Deliberately UNAFFECTED specs: `export`. The published `affine` flags
  keep the meaning that spec gives them and the values they have today
  (see the last non-goal); no document field is added and no document
  version moves.
- Affected specs: `simulation` — one ADDED requirement ("A kink is a cut,
  and a piecewise-affine quantity is solved") and four MODIFIED ("A jump
  is located inside the tick and subtracted", "A declared range is a
  physical stop located inside the tick", "A law may read the coordinate
  it drives", "A selection decides which sources a law reads"), each
  taking one sentence about what is solved and what is searched.
- Affected code: `solid_node/simulation/program.py`
  (`_affine_in_sources` and `_degree_of`, `_Jump`, `JumpPlan._crossings_of`,
  `_Walk._crossing`, `Edge._affine_ends`, `Edge.cuts`) and
  `solid_node/simulation/run.py` (`Run._locate`, `Run._piecewise`).
- Affected tests: `tests/test_running_jumps.py`,
  `tests/test_running_stops.py`, `tests/test_running_reads.py`,
  `tests/test_running_corpus.py`, `tests/test_running_document.py` (the
  published `affine` flag stays two-valued and stays `false` for a kinked
  quantity), `tests/running_project/machine.py`,
  `tools/generate_running_corpus.py`, `tests/running-corpus.json`.
- Originating project: `projects/Calculators/Curta-Type-I-3x` — its
  clearing interface is the `CurtaInterface` fixture, and its carriage
  association is the shape `select-the-source` had to write as
  comparisons.
