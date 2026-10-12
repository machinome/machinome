# ADR-061: A kink is a cut in the viewer too, and the viewer derives the shape itself

**Status:** Accepted

**Date:** 2026-09-16

**Change:** `solve-at-the-kink`

**Depends on:** ADR-045 (the run this executes in) and ADR-046 (the scope
a followed point is read through), which it extends; ADR-047 (the corpus
this is proved against), ADR-057 (the self-read walk) and ADR-058 (the
block, whose stop this deliberately leaves searched), which it builds on;
and ADR-060 (only what moves along a step's path is walked), whose
evaluation sites this sub-divides. **Consumes** solid-node's ADR-123
(`cut-at-the-kink`) as the mechanism this mirrors — and contradicts one
sentence of its Consequences (below).

## Context

The producer decided on 2026-09-16, in ADR-123, that **`abs`, `min` and
`max` are KINKS, and a kink is a cut**: a quantity built over them is
PIECEWISE AFFINE, and is solved on the stretches between its own
breakpoints instead of being sampled 64 times and bisected. It
deliberately left the published `affine` flag TWO-VALUED, so a kinked
quantity still publishes `affine: false`, and it named what that leaves
here:

> The two runtimes now locate a kinked crossing differently. Python
> solves it; the viewer, reading `affine: false`, still searches it. …
> A viewer that wants the solve cannot re-derive the shape from the
> document — nothing there says whether a non-affine quantity is kinked
> or curved — so it needs a new document field or a redefinition of
> `affine` under a version bump: two changes in two repositories.

**That last sentence is wrong about this viewer.** The viewer holds the
published EXPRESSION, not only the flag — it is what `prepare` interns
and what `PathValue` and `foldedNames` already walk. The classification
ADR-123 computes at compile is STRUCTURAL: it reads the expression tree
and nothing else. So this viewer computes the same shape from the same
text, and no document field, no version bump and no second repository is
needed for it.

The only external check on a second implementation of someone else's
classification is the flag the document already carries, and it is
unanimous:

| document | published `affine` flags | disagreements |
| --- | --- | --- |
| the conformance corpus's 20 documents | 39 driven ends + 34 jump levels = **73** | **0** |
| the operating Curta (`OperatingCurta`, version 7) | 268 driven ends + 547 jump levels = **815** | **0** |

and the Curta's census reproduces the producer's own published one to the
unit: 28 kinked plan-bearing skeletons (17 of them self-read), 41
unclassified, 183 affine and 16 kinked plan-less laws, 532 affine and 15
kinked jump levels. Two independent implementations, one number.

## Decision

**The viewer classifies a followed quantity's SHAPE from the published
expression, at LOAD, and cuts a piecewise-affine one at its own kinks.**

- The classification is the producer's `_shape_of`, mirrored over the
  interned DAG: `constant`, `affine`, `kinked` or unclassified,
  propagating through a unary minus, a sum, a difference, a constant
  multiple and a division by a constant; introduced only by `abs`, `min`
  or `max` over operands that are themselves movable; walking INTO the
  document's bindings table; and conservative — `max(0, sin(x))` stays
  unclassified and goes on being searched. It is computed once per
  published quantity when the document is loaded and stored beside the
  flag the run already reads.
- It NEVER weakens the published flag: the solve for `affine: true` is
  untouched, and the shape is asked only where that flag is false. A
  contract test asserts the agreement above over every document the suite
  holds.
- A kink's breakpoints are SOLVED, never sampled: the kinks in the
  expression's own postorder, each level evaluated at the two ends of
  each sub-interval the earlier kinks produced, one division for its
  zero, folded under the crossing tolerance two crossings already share.
  No sampling, no bisection, and **no fourth tolerance**.
- **A kink breakpoint is NOT a crossing.** It is recorded nowhere, enters
  no partition an increment is summed over, lands no coordinate on a far
  side and counts toward no published limit. It exists only inside a
  SOLVE, and this is what keeps every other answer bit-identical.
- Three sites take the sub-division, mirroring ADR-123 §4.4: a jump
  node's crossings, a self-read walk's crossing (the SKELETON's
  breakpoints first, the LEVEL's located inside each of them), and a
  stop's localization — including a law with NO jump plan at all, the
  shape that otherwise divides straight THROUGH the kink.
- **No document change and no knob.** `solidNodeViewerApi` stays 16,
  `solidNodeDocumentVersions` stays `[1..7]`, nothing is added to or read
  from the document that was not already there, and nothing an author
  writes selects any of it. One repository's change.

## Consequences

**The two runtimes stop agreeing within a window and start agreeing
exactly.** Of the 2 018 floats the conformance corpus fixes — every
banked value, every crossing and its level, every stop and its value,
every command's admitted travel — this engine reproduced 2 009 bit for
bit and disagreed on 9, all of them consequences of ONE searched stop
(`KinkedStop`: the stop fraction 9.09e-14 out, the `lever` bank value and
`h0`'s admitted travel 3.6e-12 out, on all four ticks). It now reproduces
**all 2 018 bit for bit**, and nothing else in the corpus's 360 ticks
moved by one bit in either direction.

**A `clamp01` window costs a fraction of what it cost.** `clamp`, `ramp`
and `piecewise` are built on it, and `piecewise` is the pose model's
normal spelling of a motion profile. On the committed `clearing` fixture
— the Curta's clearing interface, six self-read dials through a `clamp01`
station window, the worst case this repository has — **32 004 → 2 724
evaluations per tick and 342 → 1 312 ticks/s**: 11.7× the work removed,
3.8× the wall clock.

**The operating Curta is not made faster, and this ADR does not pretend
otherwise.** 17 of its 32 self-read skeletons are kinked and 15
unclassified, and ADR-060 measured that 100 % of its searched evaluations
are under the 15: its dial cams carry `sin`, `cos` and `sqrt` of a moving
phase. Measured before and after on the same document, three runs each:
**20 718 evaluations on an idle tick and 268 968 on a crank tick, to the
unit**, and the whole state digest after 160 ticks byte-identical
(`7f7bc77a…`). What that document needs is a classification per BRANCH —
a kink can pin a curved subtree to a constant on one of its pieces, which
is exactly a cam through its dwell — and ADR-123 records that as a
deferred gap with its reasons.

**A stop on a BLOCK coordinate is still searched.** A block has no single
published expression until a branch vector is fixed, and the order its
members run in may differ from piece to piece. The producer's own
deferral, kept: `RangedBlock` carries no shape and does not move.

**The kink levels stay on the plain evaluator**, as the producer left
`_KinkCuts` on `GraphValue.evaluate`. Measured, so the next cycle has a
number: on the `clearing` fixture the kink levels are 960 of the
remaining 2 724 evaluations per tick, in 96 calls; on `Clearing`, `Train`,
the Curta carriage and every corpus machine they are zero. A path-valued
kink level is a follow-up with a document that demands it.

**A second reader of the producer's classification now exists**, and it
can drift. Mitigated by the contract test above, which is red the moment
a quantity this viewer finds constant-or-affine is one the document
publishes `affine: false`, or the reverse — without anyone running the
producer.

## Alternatives considered

- **A third value of the published flag, or a new document field.**
  Explicitly refused by ADR-123, would move the document version, and is
  unnecessary: the viewer agrees with the flag on 888 published
  quantities it derived independently.
- **Sampling the kink's own level.** It is affine between the earlier
  kinks' breakpoints, so a division is exact where a search is not; a
  fourth tolerance would have been introduced for nothing.
- **Recording a breakpoint as a crossing.** It would appear in the
  crossing record, enter the partition and count toward the published
  limit, and every answer that merely PASSES a kink would move. The
  quantity is continuous there: a breakpoint is not an event.

## Review (2026-09-16)

Accepted at the cycle's adversarial review. The reviewer checked the three sensitive sites line by line against the producer (`crossingsOf` and `Walk.crossing` boundary rules, the level cuts located inside one skeleton sub-piece, `edgeCuts` for a plan-less kinked end), re-ran the suite (37 files, 999 tests) and `tsc --noEmit`, and the operating Curta harness: 20 718 / 268 968 evaluations per idle / crank tick unchanged, digest identical (`7f7bc77a…`).
