# ADR-057: A self-read edge is executed from the retained value, piece by piece

**Status:** Accepted

**Date:** 2026-09-15

**Change:** `execute-the-self-read`

**Extends:**
- [ADR-045: The run executes in a worker and the main thread only poses](ADR-045-the-run-executes-in-a-worker.md)
- [ADR-047: The corpus is what makes the two runtimes one algorithm](ADR-047-the-corpus-makes-the-two-runtimes-one-algorithm.md)

**Builds on:**
- [ADR-054: A constraint is derived from the published document, never published](ADR-054-a-constraint-is-derived-from-the-published-document.md)

**Consumes:**
- solid-node ADR-121: A law may read the coordinate it drives

## Context

ADR-045 mirrored `simulation/program.py` and `simulation/run.py`
function for function, and ADR-047 pinned the mirror to the producer's
own corpus. Under both, a law edge was a function of coordinates OTHER
than the one it drives: its contribution over a tick is
`f(end) − f(start)`, its jumping form is ADR-107's one partition of the
path with each piece's branches read at its MIDPOINT, and the value the
edge determines appears nowhere in what the edge reads.

solid-node's ADR-121 widened that. The coordinate a law DRIVES may now
appear among its sources, and what the law reads there is the value that
coordinate **retains**. The mechanism is the Curta's clearing rack: a
ring carrying nine-tooth racks sweeps past the register dials, and a rack
turns a dial only while its teeth reach it AND the dial is not already
standing in its missing-tooth gap — the gap being what lets the ring
sweep on past a finished dial while it still clears the dials beyond it.
The dial's own retained angle decides whether the rack moves it.

**The producer publishes that as a version 6 document and adds no key
for it.** The self-read is a law edge whose `needs` intersects its own
`gives`, which is the same question `serializer.py`'s `_reads_its_own`
asks to choose the version. The version moved because a version 5
consumer reads such an edge at both ends, freezes the branch its gate
selects for the whole tick, and moves the part by a different mechanism
in silence: the framework measured a `500`° rack sweep from a dial
standing at `108` leaving it at `608`, and a second sweep at `1108`,
with no crossing located at all.

This viewer rendered versions 1–5 and refused a version 6 document by
name, which is correct and was the last thing between the Curta and a
browser:

```text
…/viewer.json declares document version 6, which this viewer does not
render; it renders versions 1, 2, 3, 4, 5.
```

**The gap was measured before anything was written.** The committed
corpus was two framework regenerations behind, and the framework's own
file copied byte for byte over it failed exactly four tests on the base:
the census (17 scenarios where 14 were expected), and the three new
ones — `Clearing` at `dt = 0.05` committing `wheel.turn` at `408` where
the producer commits `359.5`, `Clearing` at `dt = 0.1` at `488`, and
`StoppedClearing` committing `ring` at `336.73469387755097` where the
producer commits `341.1428571428571`. Thirteen scenarios and both width
cases passed untouched. `408` against `359.5` is the gate frozen open:
the dial ran straight through its gap, exactly as the framework measured
on its own side before ADR-121.

## Decision

**The self-read is RECOGNISED as `needs ∩ gives`, and its reading is
DERIVED when the document is loaded.** `loadProgram` gives each such
edge a `retained` array parallel to `gives` — and `[]`, not `[null, …]`,
for every other edge, so the whole of this decision costs a law with no
self-read one array-length test per edge per tick. Each entry carries
what `program.py`'s `_Retained` carries: the driven id; the plan's jump
nodes that DEPEND on it, in the plan's own postorder; the INDEPENDENT
subset as a well-formed plan of its own; and whether the skeleton is
affine.

- **Dependence is asked of the published level, CLOSED OVER the
  document's bindings table**, and propagated through the placeholders
  of dependent inner nodes in the plan's order. `Clearing`'s band gate
  reaches `wheel.turn` only through `_b3 = ((wheel.turn + 0.5) / 360.0)`;
  a viewer reading raw free names would sort that node INDEPENDENT and
  integrate the whole tick under one branch. This is ADR-054's lesson a
  second time, and it reuses ADR-054's own `namesOf` rather than a
  second closure.
- **Affinity is READ, never recomputed.** For a plan-bearing law the
  edge's published per-end `affine` flag IS `_affine_in_sources` of the
  skeleton, so the viewer takes `edge.affine[index]` and computes
  nothing. What compile time decided is read: ADR-047's rule holding.
- **Nothing is published for any of it**, and the viewer asks for
  nothing. A derivation with no decision in it is the producer's to
  refuse (ADR-110) and this viewer's to make at load — where ADR-054 put
  the constraint table, and for the same reason.

**Three shapes are refused at load, by name.** A self-read edge that
determines more than one value, or reads more than one of them: ADR-121
refuses a driven group with a self-read at class definition, so no
published document carries one, and a member reading a sibling would
need that sibling's path while the sibling's own walk is cutting it. A
driven id the bank does not hold — a published computed value, which
keeps no history to read back. And a read that survives the SKELETON,
which makes the relation a differential equation that the difference of
two evaluations does not define; a bare remainder is not a switch,
because a fixed quotient leaves `a − q·b` and that still carries the
coordinate's slope. Where an end carries no plan at all, its EXPRESSION
is its skeleton and is judged as one — `program.py`'s own
`plan.skeleton if plan is not None else graph`, which is wider than this
cycle's ratified prose and is the reading that keeps the sentence true.
**A version 6 document with no self-read edge loads and runs**: nothing
keys off the number 6 but the rendered-version list.

**The step integrates such an edge in TWO LAYERS.** ADR-107's partition
is built first over the independent nodes ALONE — by `partition` itself,
not a copy — its crossings recorded over the whole tick, its branches
read at its midpoints, its near cuts merged and deduplicated as they
always were, which is valid precisely because those levels do not depend
on the walk. Inside each of its pieces the dependent nodes are WALKED:

- their branches are decided in the plan's postorder at the piece's
  **left end**, with the driven coordinate at the value it RETAINS there
  and every other source at that same fraction. A midpoint is no use to
  a dependent node — the coordinate's value there is a consequence of
  the branch being asked for — and for a MIXED level such as
  `ring − wheel`, which can cross inside the piece by the sources'
  motion alone, the midpoint branch is the far-side one, under which the
  piece's own left half would be integrated;
- a node sitting EXACTLY on a surface at that left end — which happens
  at every cut the walk takes, and at a tick's start after a stop, a
  restore or a rest default — takes the branch its OPERATOR gives, and
  is FLIPPED, at a zero-length piece, if the level then LEAVES the
  surface. It is flipped to `branchOf(nextAfter(surface, probe))`, the
  region immediately on the side the level departs to, and never to the
  branch at the probe: for `floor`, `ceil` and `%` a sample a whole
  tooth away names a branch the piece never enters. A node flipped twice
  is a sliding mode and refuses the tick;
- with the branches fixed the skeleton does not name the driven
  coordinate, so its path over the piece is one ordinary evaluation, and
  the piece is CUT at the FIRST surface any dependent level reaches
  strictly inside it — solved from the two endpoint values where the
  level and the skeleton are both published affine, otherwise sampled at
  the published subdivisions and bisected to the published crossing
  tolerance. Unlike `crossingsOf`, which returns every surface between
  two endpoints, the walk takes the FIRST and decides again: under a
  self-read the path is known only until the branch changes;
- **layer one's folding is not applied in layer two.** Every crossing
  strictly inside the piece is returned, one a hair from its left end
  included; folding it would integrate the piece under the near-side
  branch and drive the part through its gap;
- **the driven coordinate's own delta is ZEROED inside the walk.** Its
  id is in `needs`, so the ordinary `along()` would otherwise advance it
  by the increment the tick handed it. What it holds on a piece is what
  the pieces before it produced.

**After a cut the coordinate is placed at the nearest representable
value on the FAR SIDE of the surface, in ordinal float space.**
JavaScript has no `math.ulp`, `math.nextafter` or `math.copysign`, so
`_ordinal` and `_from_ordinal` are reproduced over a
`Float64Array`/`BigInt64Array` view of the same eight bytes — `BigInt`,
because the ordinal range is the whole of int64 — and the other three
are built on them, with Python's floor `//` reproduced where BigInt
truncates toward zero. From the value the segment's own arithmetic
gives, a bracket is grown with the stride doubling from one ulp in BOTH
directions (the arithmetic lands past the surface about as often as it
lands short) and bisected until the two ordinals are adjacent; the far
one is taken. Two nodes crossed at one fraction are ONE cut, each walked
in turn with the others at their near-side branches, which is what makes
a knife-edge gate hold from both sides. Where the piece did not move the
coordinate there is nothing to walk. **A cut that places the coordinate
nowhere within 200 doublings is LOUD**: `LandingInvariantError`, a new
refusal kind of its own, rather than committing the one value the design
says is never committed. It is unreachable by construction, and the code
says so where it throws.

**The run COMMITS that float, in both places it builds a committed state
and BEFORE the bounds are examined.** `value + delta` is not enough on
its own — `x + (y − x)` is not `y` for a substantial share of float
pairs, so an exact landing inside the plan would still be a ulp out in
the bank the next tick starts from, and a ulp back toward the surface is
the ENGAGED side of the gate. Applying it
where a stop's bound is already applied settles two questions at once: a
declared range on the same coordinate in the same segment OVERWRITES the
landing, because a physical bound is a bound of the coordinate itself
(`StoppedClearing` is the fixture), and `reachedBounds` sees the value
the tick will actually commit. **A self-read crossing is a CROSSING**:
it stops no input and retires no command.

**`documentVersions` becomes `[1, 2, 3, 4, 5, 6]` and the declared API
version rises 14 → 15.** Executing a version 6 document is a capability a
host may require BEFORE it mounts, and the precedent is exact:
`run-in-the-worker` raised the API to 8 when the document list grew to
include 5, while `drive-the-run-by-touch` and `draw-what-a-part-carries`
deliberately did not move it, because `controls` and `markings` are
additive. This is not additive — a bundle at API 14 refuses the Curta by
name and renders nothing. Two gates that tested the version NUMBER
become floors (`viewer.ts`'s program gate and `capture.py`'s
`carries_program`), since a document declaring a running version carries
a program whether or not the key is there. **`bundle.py`'s
`RELEASED_DOCUMENT_VERSIONS` does not move**: it is what a viewer that
predates the declaration is entitled to be assumed to read, and the only
released viewer is 0.1.0, which reads `[1, 2, 3, 4]`. Widening
`RefusalKind` does not move the API on its own — `kind` crosses only the
worker boundary inside the published bundle.

**The corpus is what holds the two runtimes together here too.** The
producer's regenerated fixture is committed byte for byte — 17 scenarios
over 14 machines, 328 ticks, the new `Clearing` and `StoppedClearing`
machines among them — and the width guard gains the producer's three new
required features, computed the way the generator computes them, so a
narrower corpus copied in from a future framework is loud here without
anyone running the generator.

## Alternatives weighed

- **A published `reads` array on the edge**, the shape `Constraint`
  suggests. The export spec says in its own words that the free names of
  a law edge's expressions are exactly the ids in `needs`; a separate
  list makes that sentence false and needs a document key. The framework
  rejected it on its own side for the same reason.
- **Deriving the reading per tick.** The dependence split is a function
  of the plan alone, so this recomputes a bindings closure on every step
  of every machine that carries a self-read — compile-time work on the
  producer's side, load-time work here.
- **One flat partition over all the jump nodes, with the driven
  coordinate held at its tick-start value.** That is what a version 5
  consumer effectively does, and it is what the base measures at `408`
  instead of `359.5`.
- **A second, self-read-only copy of the partition.** It would drift
  from `partition` at the first correction either file received, which
  is exactly the failure the corpus exists to prevent.
- **Committing what the segment's arithmetic gives.** The framework's
  first draft, measured out: 6.3 % of crossings left the gate ENGAGED
  and another 12.7 % were refused `TooManyCrossings`. With the far-side
  landing, 200 000 randomized crossings gave zero re-engagements and
  zero refusals.
- **Leaving the API version at 14 and moving only the document list.**
  It would let a host mount a bundle that refuses the machine it was
  mounted for, with nothing to check beforehand.

## Consequences

- **A version 6 document loads, runs, and agrees with the framework tick
  for tick.** The corpus went green on the FIRST run after the walk
  landed, with no adjustment to any tolerance, ordering or branch rule.
  The Curta's own clearing interface mounts in Chromium: one sweep
  leaves all six dials at exactly `359.5` — the framework's own expected
  value for the same machine — a second sweep completes its whole travel
  and moves no dial AT ALL, bit for bit, with zero crossings, and no stop
  is recorded anywhere.

- **A searched self-read is expensive, and this one does not keep up with
  a wall clock.** Measured on the bench: the corpus's `Clearing`, whose
  skeleton is affine and whose crossings are therefore SOLVED,
  **5 319 ticks/s**; the committed Curta fixture, whose `clamp01` station
  window makes all six skeletons non-affine so that every crossing falls
  to the 64-sample search and its bisection, **189 ticks/s** — against
  the 240 a second the default `1/240` s step needs, **0.79× real time**.
  It runs CORRECTLY at that step; it is not fast enough to run at it in
  real time on this machine. That is recorded as a finding, not mended by
  a coarser step, a widened tolerance or a skipped sample. (The producer's
  own figures for the same two shapes are 1 349 and 24.4 ticks/s, so this
  engine is about 3.9× and 7.7× cheaper.) The follow-up — a cheap exact
  path for a kinked-but-piecewise-affine skeleton — is the one the
  framework already named on its own side, and is neither package's.

- **A law with no self-read is untouched**: same meaning, same code path,
  same cost. The Pascaline acceptance is unchanged to the digit
  (`tens.drum.turn` still `65.54` after ten `Add one`), `Train`'s
  measurement moves only within this host's run-to-run spread, and the
  pin tumbler lock's version 5 document runs exactly as it did but for
  the API number it asserts. The bundle grows 685.7 kb → 702.5 kb.

- **The corpus catches none of the three corrections the walk's rules
  exist for.** Each was reintroduced in turn — a phantom crossing from a
  level that does not move, a flip to the branch at the probe, a genuine
  crossing folded away at a piece's left end — and all 17 scenarios
  stayed green each time, because `Clearing` solves rather than searches
  and its crossings never land a hair inside a piece. The three node
  tests in `jumps.test.ts` are the only thing in this repository that
  would catch them. The corpus pins the ALGORITHM'S ANSWERS on the
  machines it carries, not the corrections themselves, and a second
  runtime can be wrong in ways one fixture cannot see. That is a fact
  about ADR-047's guarantee, worth knowing on both sides.

- **The browser fixture's provenance is recorded rather than
  reproducible on demand.** `tests/fixtures/clearing/` is the framework's
  own `CurtaInterface` exported from a THROWAWAY copy of solid-node at
  main `8e15791`, never the pilot's checkout, with one relative import
  rewritten so the machine loads outside pytest; the published program is
  byte-identical between the two copies apart from its `identity` hash,
  and the fixture's README records both strings. Its `viewer.json` is
  verbatim; the geometry is the same 684-byte stand-in cube the Pascaline
  fixture carries, so the inspected screenshots show the mechanism
  changing the canvas rather than a legible dial. A framework finding
  falls out of this and is recorded, not acted on: **a program's
  `identity` is not invariant under the machine's import path.**

- **The numbering hazard is recorded and not acted on.** The unmerged
  branch `slide-and-turn-parts` claims API version 13 and is expected to
  take ADR-055. This cycle takes API 15 and ADR-057, which collide with
  neither whatever order they integrate in; reconciling that branch's own
  numbers is its integration's business, and the README's version table
  says so.

- **A host at API 14 and a producer at version 6 disagree silently unless
  the host checks.** That is what `documentVersions` is for, and
  `describe` reports it — which is also how the producer's export warning
  named this refusal while it stood.
