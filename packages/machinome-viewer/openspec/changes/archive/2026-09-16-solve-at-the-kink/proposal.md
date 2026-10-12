## Why

The producer decided on 2026-09-16, in ADR-123 (`cut-at-the-kink`,
solid-node `c3f3348`), that **`abs`, `min` and `max` are KINKS, and a
kink is a cut**: a piecewise-affine quantity is solved on the stretches
between its own breakpoints instead of being sampled 64 times and
bisected. It deliberately left the published `affine` flag TWO-VALUED, so
a kinked quantity still publishes `affine: false`, and it named what that
leaves here:

> The two runtimes now locate a kinked crossing differently. Python
> solves it; the viewer, reading `affine: false`, still searches it. …
> A viewer that wants the solve cannot re-derive the shape from the
> document — nothing there says whether a non-affine quantity is kinked
> or curved — so it needs a new document field or a redefinition of
> `affine` under a version bump: two changes in two repositories.

**That last sentence is wrong about this viewer, and the measurement says
so.** The viewer holds the published EXPRESSION, not only the flag. The
classification ADR-123 computes at compile is STRUCTURAL — it reads the
expression tree and nothing else — so this viewer can compute the same
thing from the same text. Measured: `_shape_of` mirrored over the
published documents and their bindings tables agrees with **every one of
the 815 `affine` flags** the operating Curta's document publishes (268
driven ends, 547 jump levels) and with **all 73** the refreshed
conformance corpus publishes — zero disagreements. So no document field
is needed, no version moves, and this is ONE repository's change.

**This is not a Curta-speed cycle, and it must not be sold as one.**
ADR-060 measured, and this cycle re-measured, that 17 of the operating
Curta's 32 self-read skeletons are kinked and 15 unclassified, and that
100 % of that document's searched evaluations are under the 15 —
its dial cams carry `sin`, `cos` and `sqrt` of a moving phase. The
prototype leaves that document **exactly** where it found it: 20 718
evaluations on an idle tick and 260 306 on a crank tick, to the unit,
before and after, with the whole state digest after 70 ticks
byte-identical. The justification is EXACTNESS and GENERALITY.

### The exactness, measured on the corpus

`mirror-the-kink-guard` (the cycle this one stacks on) takes the
producer's refreshed corpus and records the gap it lands with: of the
**2 018** floats the corpus fixes — every banked value, every crossing
and its level, every stop and its value, every command's admitted travel
— this engine reproduces 2 009 bit for bit and disagrees on **9**, all of
them `KinkedStop`'s and all of them consequences of ONE searched stop:

```text
tick 1    stop slide.travel t   0.47812500000009095  corpus 0.478125
ticks 1-4 bank lever            119.12500000000364   corpus 119.125
ticks 1-4 command h0 admitted    19.125000000003638  corpus 19.125
```

9.09e-14 on the fraction — the search's own tolerance, inside the
corpus's `1e-9` window, and the same order as the 9.3e-14 ADR-123
measured before it solved. **With this change the prototype reproduces
all 2 018 floats bit for bit.** The two runtimes stop agreeing within a
window and start agreeing exactly.

### The generality

A `clamp01` window is how the framework's own `clamp`, `ramp` and
`piecewise` are built, and `piecewise` is the pose model's normal
spelling of a motion profile. Today this viewer samples every one of
them. On the committed `clearing` fixture — the Curta's clearing
interface, six self-read dials through a `clamp01` station window, the
worst case this repository has — the prototype costs **2 724
evaluations/tick against 32 004**, and runs at **1 216-1 254 ticks/s
against 297-308**: 11.7× the work removed, 4.1× the wall clock. The
producer's own fixture went 2 861 → 603 evaluations/tick and 28 → 133
ticks/s. And the machines with no kink pay nothing, measured to the
tenth: `Clearing` 471.1 → 471.1, `Train` 31.0 → 31.0, the Curta carriage
5 913.2 → 5 913.2 evaluations/tick.

## What Changes

**The viewer classifies a followed quantity's SHAPE from the published
expression, and cuts a piecewise-affine one at its own kinks.**

- **The classification is the producer's, mirrored**: `constant`,
  `affine`, `kinked` or unclassified, propagating exactly where affine
  does — a unary minus, a sum, a difference, a constant multiple, a
  division by a constant — introduced only by `abs`, `min` or `max` over
  operands that are themselves movable, and conservative: `max(0,
  sin(x))` stays unclassified. It is computed once per published quantity
  at LOAD, over the same interned DAG the run already evaluates, walking
  INTO the document's bindings table exactly as `PathValue` and
  `foldedNames` already do. It never weakens the published flag: a
  quantity the producer published affine is solved over the whole stretch
  as it already was.
- **A kink's breakpoints are solved, not sampled.** A kink's level is the
  argument of `abs` and the difference of the two operands of `min` and
  `max`, with one surface at zero. Over a stretch the kinks are taken in
  the expression's postorder — a kink nested inside another's level cut
  first — and on each sub-interval the earlier kinks have produced the
  level is affine, so its zero is one division. Two breakpoints closer
  than the crossing tolerance are ONE, under the tolerance two crossings
  already share. No sampling, no bisection, **no fourth tolerance**.
- **A kink breakpoint is NOT a crossing.** It is recorded nowhere, enters
  no partition an increment is summed over, lands no coordinate on a far
  side and counts toward no limit. It exists only inside a SOLVE. This is
  what keeps every answer bit-identical, and it is the load-bearing rule.
- **Three sites take the sub-division**, mirroring ADR-123's §4.4: a jump
  node's crossings (`crossingsOf`), where the right end is inclusive for
  every sub-piece but the last so a surface on an interior breakpoint is
  located once and `deduplicated` takes it once; a self-read walk's
  crossings (`Walk.crossing`), where the SKELETON's breakpoints come
  first because they are what make the driven coordinate's own path
  affine and the LEVEL's are located inside each of them; and a stop's
  localization (`run.ts`'s `locate` through `edgeCuts`), where a law with
  a plan unions the skeleton's kinks per piece with that piece's branches
  substituted, and a law with NO plan at all — the shape that otherwise
  divides straight THROUGH the kink — gets a partition of its own kinks
  over the whole step.
- **No document change, no knob.** `solidNodeViewerApi` stays 16,
  `solidNodeDocumentVersions` stays `[1..7]`, nothing is added to or read
  from the document that was not already there, and nothing an author
  writes selects any of it. This is one repository's change.
- **A stop on a BLOCK coordinate is still searched**, for the producer's
  own reason: a block has no single expression until a branch vector is
  fixed and its members' order may differ from piece to piece. Measured:
  `RangedBlock`'s searched stop does not move.

### What the prototype proves

A complete prototype of the above over a copy of `src/` patched at those
sites (`scratchpad/spikes-bc/proto`), against the refreshed corpus and
the committed fixtures:

| | base | prototype |
| --- | --- | --- |
| corpus floats not bit-identical to the producer's (of 2 018) | **9** | **0** |
| `clearing` fixture, evaluations/tick | 32 004 | **2 724** |
| `clearing` fixture, ticks/s (3 runs) | 297 / 303 / 308 | **1 233 / 1 254 / 1 216** |
| `Clearing`, `Train`, Curta carriage, evaluations/tick | 471.1 / 31.0 / 5 913.2 | 471.1 / 31.0 / 5 913.2 |
| operating Curta, evaluations/tick idle / crank | 20 718 / 260 306 | 20 718 / 260 306 |
| `run/` suite over the refreshed corpus | 340 | **340 green** |

`run/cost.test.ts`, three runs each, base against prototype: `Train`
159-169k → 160-179k ticks/s, the Pascaline 30-36k → 32-36k, `CarryLead`
83-90k → 80-94k, `Clearing` 12.8-13.5k → 13.8-14.1k, `ShiftedCarry` quiet
9.7-10.0k → 9.8-10.2k, the Curta carriage 736-754 → 741-762, the lock
advancing the key 133-135 → 132-143, `RangedBlock`'s searched stop
220-231 → 245-263 — every one inside its own run-to-run spread, and the
Curta fixture 297-308 → 1 216-1 254.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-package`: ONE ADDED requirement, "A piecewise-affine quantity
  is cut at its own kinks" — the classification, the breakpoint solve,
  the rule that a breakpoint is not a crossing, the stop on a kinked
  determiner, and what may not move with any of it. TWO MODIFIED
  requirements, "The step reproduces the producer's own integration" and
  "The worker executes a law that reads the coordinate it drives", whose
  present sentences say a level that is not published affine is sampled
  and would otherwise contradict it. Every existing scenario of both is
  carried unchanged under its exact title.

## Impact

- `solid_node_viewer/widget/src/expressions.ts` — the three-valued
  classification over the interned DAG, and a kink inventory; both
  exported to `src/run/` only.
- `solid_node_viewer/widget/src/run/program.ts` — the classification
  computed at load, per plan skeleton, per jump level and per plan-less
  driven end; and the kink level's evaluation beside `evaluateExpression`,
  because `edges.test.ts` asserts that no other module under `src/run/`
  reaches the evaluator.
- `solid_node_viewer/widget/src/run/jumps.ts` — the sub-divided solve in
  `crossingsOf` and in the walk, the skeleton and level cut helpers, the
  kinks unioned into `planCuts`, and `merged` gaining the stretch's right
  end.
- `solid_node_viewer/widget/src/run/edges.ts` — `edgeCuts` for a law with
  no jump plan.
- `solid_node_viewer/widget/src/run/run.ts` — `locate` solving a kinked
  determiner.
- `solid_node_viewer/widget/src/run/{jumps,run,program,expressions}.test.ts`
  and `cost.test.ts` — the red-first cases and the measured floors.
- `docs/adrs/EXPORT/ADR-061` and `docs/adrs/README.md`.
- `CHANGELOG.md` under `0.2.0 — unreleased`: one bullet.
- `openspec/specs/viewer-package/spec.md`: three requirements, through
  the delta.
- Nothing in `package.json`, nothing in `viewer.ts`'s
  `RENDERED_VERSIONS`, nothing in `src/running-corpus.json` (this cycle
  never edits the corpus), nothing in the Python package, nothing in the
  framework, and nothing in another checkout. `dist/solid-widget.js` is
  gitignored and kept current by the package itself under ADR-059, so
  there is no bundle to commit.

### Non-goals

- **Making the operating Curta faster.** It does not, and the
  measurements above say so twice. What that document needs is a
  classification per BRANCH — a kink can pin a curved subtree to a
  constant on one of its pieces, which is exactly the Curta's cam through
  its dwell — and ADR-123 records that as a deferred gap with its reasons.
- **Lifting the block's stop.** Different obstruction, the producer's own
  deferral, and `RangedBlock` is asserted not to move.
- **Touching bounds that read other coordinates.** Their sampled
  examination is a different requirement and a different sub-program;
  nothing here changes it.
- **Putting the kink levels on a path value.** The producer left
  `_KinkCuts` on its plain evaluator and this cycle does the same.
  Measured, so the next cycle has a number: on the `clearing` fixture the
  kink levels are 960 of the remaining 2 724 evaluations/tick, in 96
  calls; on every other machine measured they are zero. A path-valued
  kink level is a follow-up with a document that demands it, not a
  speculative complication of a cycle whose point is exactness.
- **Publishing a third value of the flag.** Explicitly refused by
  ADR-123, and unnecessary: the viewer derives the shape and agrees with
  the flag on 888 published quantities.
