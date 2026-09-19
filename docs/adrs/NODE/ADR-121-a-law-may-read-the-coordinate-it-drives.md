# ADR-121: A Law May Read the Coordinate It Drives — Retained-Angle Engagement, Integrated Piece by Piece

**Status:** Accepted
**Date:** 2026-09-15
**Depends on:**
- [ADR-105: The run owns the coordinates and binds them](./ADR-105-the-run-owns-the-coordinates-and-binds-them.md)
- [ADR-106: One law, two readings](./ADR-106-one-law-two-readings.md)
- [ADR-107: A jump is located inside the tick and subtracted](./ADR-107-a-jump-is-located-inside-the-tick-and-subtracted.md)
- [ADR-108: A range is a physical stop that stops the connected group](./ADR-108-a-range-is-a-physical-stop-that-stops-the-connected-group.md) — the "committed AT its bound exactly" this transposes
- [ADR-113: A bound may read other coordinates](./ADR-113-a-bound-may-read-other-coordinates.md) — reads evaluated along the tick's path
**Amends:**
- [ADR-100](./ADR-100-a-relation-may-name-several-coordinates-at-each-end.md) — its refusal of a coordinate named on both sides of one relation: that sentence now has a meaning, and is a READ of the driven end
- [ADR-107](./ADR-107-a-jump-is-located-inside-the-tick-and-subtracted.md) — its single partition and midpoint branch, for the jump nodes that depend on the driven coordinate: two layers, and a branch read at the piece's LEFT END
**Cites:**
- [ADR-057: The flexible leaf, whose geometry travels as a spec](./ADR-057-the-flexible-leaf-and-spec-carried-geometry.md) — the rule that a producer emits the lowest version its content needs
- [ADR-110: The compiled program is published in the document](../EXPORT/ADR-110-the-compiled-program-is-published-in-the-document.md)
- [ADR-111: A conformance corpus is the contract between the two runtimes](../EXPORT/ADR-111-a-conformance-corpus-is-the-contract-between-the-two-runtimes.md)
**OpenSpec change:** `read-the-driven-coordinate`

## Context and Problem Statement

A running law says how far a coordinate moves for its sources' movement.
Every law the framework admitted was a function of coordinates OTHER
than the one it drives, because ADR-100 gave a coordinate named on both
sides of one relation no meaning and refused it at class definition.
That covers every mechanism the campaign had met — until a mechanism's
engagement depends on where the driven part itself stands.

The originating project is `projects/Calculators/Curta-Type-I-3x`,
branch `direct-operation`, checkpoint `b285393`; the requirement is
recorded whole in `workflow/docs/curta-retained-angle-clearing.md`. The
Curta is cleared by sweeping a ring carrying two nine-tooth racks past
the register dials. A rack turns a dial only while its teeth reach it
AND the dial is not already standing at its missing-tooth zero: nine
teeth, one gap, and the gap is what lets the ring go on sweeping past a
dial that has finished while it still clears the dials beyond it.
Releasing the ring part way keeps the partial clearing; resuming
continues from there; sweeping an already-zero dial does not turn it
again. **The dial's own retained angle decides whether the rack moves
it**, so the law that moves the dial has to read where the dial stands.
The project's executable diagnostic,
`simulation/tools/direct_operation_probe.py`, was refused before a run
existed:

```text
TypeError: wheel.rotation is named as both a source and a driven end of one
relation: a coordinate is a source or a driven end of one relation, not both.
```

**Three routes through the model as it stood were measured, and each
fails in its own way.**

- **A declared range on the dial stops the RING.** A wheel declaring
  `range=(None, 360)` driven from a `ring` input by `move('ring',
  by=500)` commits the wheel at `360`, retires the ring's command
  `blocked` with `360.0` of `500` admitted, and records a stop naming
  `('ring',)`. A `Bound(..., reads=(ring,))` gives the same answer to a
  ulp. That is ADR-108 working exactly as designed and exactly against
  the mechanism: the missing tooth frees the ring, it does not hold it.
- **A gate recomputed from the ring's own travel loses the dial's
  history.** `ring.drives(wheel.turn, law=...)` over `90 * clamp01((ring
  − 100) / 90)` runs the wheel to `90` on the first sweep, back to `0`
  when the ring is returned, and to `90` again on the second — a dial
  that un-clears itself and then repeats its former contribution, and
  every dial the same rack reaches gets the same contribution whatever
  digit it stood at.
- **A duplicated coordinate carrying the previous angle does not
  solve.** `wheel.turn.drives(shadow.turn)` plus `(ring &
  shadow.turn).drives(wheel.turn, law=...)` raises `UnreachedCoordinate:
  wheel.turn drives shadow.turn: nothing bound either end` — a cycle
  with no side to be read from.

**Deleting the refusal is not an implementation, and that too was
measured.** Removing `_refuse_shared_coordinate` alone refuses the
fixture `DoublyBound` at the rest render (or `UnreachedCoordinate` with
no rest default); with the rest render also made to leave the relation
alone, `_ordered` refuses it as "a cycle the run cannot order"; with the
Kahn ordering patched too, the program compiles, its listing names the
read, its skeleton is `(ring * $j1)` with both jump levels affine — and
the tick is WRONG in silence. A `500`-degree rack sweep from a dial
standing at `108` leaves the dial at `608`, and a second sweep at
`1108`, with no crossing located at all: ADR-106's `f(end) − f(start)`
put the driven coordinate at the SAME value at both ends, so the gate
was frozen open for the whole tick and the dial never disengaged.

The program could not express this because a relation's law depends on
its OWN driven coordinate — a cycle of length one. Reading ANOTHER
banked coordinate through a jump was already legal and already exact:
the `Clutch` fixture's `-2 * shaft * (sleeve > 0.5)` is a source-gated
clutch whose crossing is located inside the tick, and the Pascaline's
carry reads the column below it. The one thing missing was the
self-read, and it is exactly the retained-angle gate.

## Decision Drivers

- The retained angle is the mechanism's own history, and ADR-105's "the
  author declares no state" forbids modelling it as state disguised as a
  part, a duplicated coordinate, or per-tick project mutation.
- Three tolerances and no epsilon anybody has to justify: `_SUBDIVISIONS`,
  `_CROSSING_TOLERANCE` and `_BISECTION_ROUNDS` are the whole budget, and
  a fourth would be a number nobody can defend.
- A hold must be BIT-STABLE. A dial that reached its gap must read the
  same branch on every later tick whatever its sources do, at every `dt`,
  and across a snapshot and a restore.
- What the reading cannot support must be REFUSED by relation identity,
  at construction, as ADR-106 and ADR-107 refuse — never integrated by
  guesswork.
- Nothing about a law with no self-read may change: not its meaning, not
  its code path, not its cost, not its published document.
- A version 5 consumer must refuse such a document by name rather than
  move a part wrongly in silence (ADR-057).
- The five requirement behaviours — clearing from any digit, no repeat
  over an already-cleared dial, partial release and resume, both
  directions, several dials from one input — must follow from the RUN,
  not from project state.

## Considered Options

**The spelling.**

1. `drives(..., reads=(...))`, mirroring `Bound(expression, reads=)`.
   Rejected on three counts. A `Bound`'s expression has no other way to
   name a second coordinate — ADR-113 says so in its own first line —
   while a relation's sources already have one, so this is a second
   naming grammar for what the first grammar already says. It needs a
   second argument convention for the law (before the sources? after?
   boxed?), where the source group needs none. And it reads as a
   RELATION-level property, where the gate belongs to a TERM of a
   multi-source law: the Curta's dial is driven by the transmission AND
   by the rack, and only the rack term is gated.
2. A new verb (`wheel.turn.driven_by(...)`, `retains=`). Rejected for
   ADR-089's own reason: one verb states mechanical direction, and a
   second vocabulary for one sentence is what that decision refused.
3. **The coordinate named on BOTH sides IS the read.** Chosen.
4. Widening to the one-to-one `a.drives(a)`. Out of scope, as ADR-100
   left it: it has no second source to carry slope, so the skeleton test
   would refuse every such law anyway, and the shape still deadlocks into
   `UnreachedCoordinate` (measured).

**What the read may be.**

1. Solve the implicit law per piece (a fixed-point iteration or a small
   ODE step) and admit a continuous read. Rejected: it introduces a
   convergence tolerance — a fourth — and a per-tick iteration count,
   into a design whose whole claim is three tolerances.
2. **A SWITCH, tested on the SKELETON** — the law with every jump node
   replaced by its branch, which the jump plan already builds. Chosen:
   the test is structural and free, and it refuses a bare `%` for the
   right reason, since `_skeleton` rewrites `a % b` to `a − q·b`, which
   still carries the coordinate's slope.

**Where a dependent node's branch is read.**

1. ADR-107's MIDPOINT. Rejected: for a dependent node the coordinate's
   value at the midpoint is a consequence of the branch being asked for,
   and for a MIXED level such as `ring − wheel`, which can cross inside
   the piece by the source's motion alone, the branch read past that
   crossing is the far-side branch, under which the piece's own left half
   would be integrated.
2. **The piece's LEFT END, the coordinate at its RETAINED value and
   every other source at that same fraction.** Chosen: the one value
   known without assuming the answer, and the mechanism's own reading — a
   rack meets the tooth the wheel is standing on. Measured on a law
   carrying both kinds of jump (a station window over the ring, a band
   gate over the wheel): the dependence test sorts the plan exactly as
   required, and the two layers compose, the same `+900` sweep taken in
   1, 12 and 240 ticks leaving the wheel at `356.4` in all three —
   identical floats, not merely inside the agreement window.

A level sitting EXACTLY on a surface at a piece's left end is not an
edge case — it happens at every cut, and at a tick's start after a stop,
a restore or a rest default. Measured: a dial placed exactly at `360 +
GAP`, where the gate's `>=` sits on its surface and the operator reads
ENGAGED, swept BACKWARD finds NO crossing (the level LEAVES the surface
rather than reaching it), so without a flip the piece is integrated
engaged and the dial is carried straight through its gap. With the flip
it holds at `360.5` backward and turns to `719.5` forward.

**Where the coordinate lands after a cut.**

1. **What the segment's own arithmetic gives** (`own_left + skeleton(t*)
   − skeleton(t)`) — the first draft's rule. Rejected on measurement,
   through `Sim` over the framework's own classes: of 20 000 randomized
   crossings, **1 253 (6.3 %) leave the gate still ENGAGED** after the
   cut and another **2 541 (12.7 %) are refused `TooManyCrossings`**,
   because the walk cuts at the same surface again and again; the worst
   landing sat 1.6e9 ulps from the band's edge. Reproduced against the
   implementation at 6.2 % and the same 2 541.
2. **The level solved for the coordinate, and snapped** (`spikes/snap.py`
   rule B). Rejected, and it decides nothing either way: it takes a slope
   from two evaluations one unit apart and then divides by it, losing
   about a thousand ulps to cancellation.
3. **The FAR SIDE of the surface, at the nearest representable value.**
   Chosen. 200 000 randomized crossings in the prototype and 50 000
   against the implementation — over periods `360`, `36`, `11.25`,
   `100`, `1` and uniform draws in `[0.1, 1000]`, gap widths from `1e-9`
   to `0.1` of the period, both directions: **zero re-engagements, zero
   refusals, the landing at most 2 ulps from the band's edge**, the float
   one step back toward the surface reading ENGAGED, and the wheel
   bit-identical through three further sweeps. The walk costs **4.3 level
   evaluations per cut**, and in 58 % of cuts the segment's arithmetic
   had already landed PAST the surface, which is why it brackets in both
   directions rather than stepping one way.

**The gate's own shape, which the model states.**

1. A WHOLE-TOOTH window, `modulo(wheel, 360) >= 36`. Rejected as wrong
   for the mechanism: swept backward from digit 1 the real rack turns the
   dial one tooth to zero and only then meets the gap, while that gate
   holds it at 36 and calls a dial standing at 10° free.
2. **A symmetric BAND about the zero, of the mechanism's own stated
   clearance**, entered from either side. Chosen: with the far-side
   landing it holds from both directions at ANY positive width — the
   wheel landing at `360·q − GAP` swept forward and `360·q + GAP` swept
   backward.

**Rest.**

1. A rest value declared on the joint (`Revolute(..., rest=108)`).
   Rejected: ADR-105's "the author declares no state" is the guardrail
   the whole running mode rests on, and a rest declaration is state under
   another name.
2. **The author's own guarded rest default**, the one-line idiom the
   catalogue already writes. Chosen; measured to pose the untimed tree at
   `108.0` with nothing refused.

**The driven end's cardinality.**

1. A driven GROUP with a self-read. Refused, not deferred silently:
   `Edge.increments` walks ONE plan per driven end, and a member reading
   a sibling needs that sibling's path while the sibling's own walk is
   cutting it — a joint walk over several plans that nothing here defines
   and no mechanism in the campaign has asked for. The rest rule is
   undefined for such a group too, since one mixing a self-read end with
   a plain end would leave the plain end unbound at rest.
2. **A BROADCAST**, admitted: the source group's repeated member IS the
   broadcast the relation drives, so it resolves per copy exactly as the
   driven end does and each copy reads ITSELF. Measured implementable at
   the record level in eleven lines over `BroadcastRef.resolve_all`: four
   records, each copy reading its own slot, no two sharing one.

**Publication.**

1. A separate `Edge.reads` tuple, the shape the `Constraint` precedent
   suggests. Rejected: the export spec says in its own words that the
   free names each of an entry's expressions reads SHALL be exactly the
   ids in `needs`. A separate list makes that sentence false and forces a
   new document key. (`Constraint` carries `reads` separately because a
   bound is not an edge and has no `gives`.)
2. **`needs ∩ gives`.** Chosen: nothing published that was not published
   before, and the published rule stays true.

## Decision

**A coordinate named as a source AND as the driven end of one relation
is a READ of that relation's own driven end.** The old
`_refuse_shared_coordinate` becomes the recognition point
(`_self_read_index`, `motion/couplings.py`): the law is handed that
coordinate's owner exactly as it is handed any source's, in the position
the source group writes it, so

```python
def missing_tooth(sources, target):
    def law(ring, wheel):
        shifted = wheel + GAP          # GAP: the clearance, half the band
        return ring * (shifted - 360.0 * floor(shifted / 360.0) >= 2 * GAP)
    return law

(ring & wheel.rotation).drives(wheel.rotation, law=missing_tooth)
```

is written as any law is written. What the law reads there is the value
the coordinate HOLDS, never a value the same application is about to
give it. Recognition is scoped exactly as the refusal was — only where
an end names SEVERAL coordinates — because that is the check's own scope
and because a relation of several ends is FORWARD ONLY (ADR-100), which
is what a self-read must be.

**Such a relation drives exactly ONE coordinate.** A driven GROUP one of
whose members the source group names — itself or a sibling — is refused
at class definition, naming the relation and the coordinate. A BROADCAST
is admitted: each copy is its own record with one driven end reading
itself.

**The read must be a SWITCH.** With every jump node replaced by its
branch, the law must no longer name the driven coordinate; a read that
survives the skeleton enters the law continuously, which makes the
relation a differential equation that `f(end) − f(start)` does not
define, and it is refused at compile by relation identity. The driven
end must also be a coordinate the run BANKS: a retained value is a
HISTORY, and a plain port or a derived coordinate is a calculation the
ordinary enumeration recomputes from the bank on every tick, so a
relation reading one is refused by name.

**At rest such a relation binds NOTHING.** Under a running root
`_step_relation` records it solved `'forward'` and applies no law; the
driven coordinate's rest value is the author's own guarded rest default,
and the run refuses by name — *"the run needs a rest value for every
joint coordinate"* — when there is none. Under any other time base the
relation is refused by name at the close of the enumeration: it states
INCREMENTS, which only a run integrates, and standing silently inert
would leave a coordinate at its rest default in a model that renders and
publishes. Ordinary posing is untouched: `set_state` binds the bank, the
enumeration recomputes ports and derived coordinates, and the self-read
relation moves nothing.

**Over one tick the law is integrated in TWO LAYERS.** A jump node
DEPENDS on the driven coordinate when that coordinate is among the free
names of the node's argument subtree; dependence is therefore UPWARD
CLOSED along the nesting, which is what makes the independent nodes a
well formed plan of their own. The split is decided once, at compile
time (`_Retained`), and run by `_Walk`:

- **Layer one** is ADR-107's `_partition`, UNCHANGED, over the
  independent nodes alone: their crossings are found over the whole tick
  and their branches read at that partition's MIDPOINTS, valid for the
  reason ADR-107 gives, since those levels do not depend on the walk.
- **Layer two** walks the dependent nodes INSIDE each of those pieces.
  At the walk's left end the coordinate holds a known value — the tick's
  committed value at the start, and what the cuts already taken placed it
  at afterwards. Every dependent node's branch is read in the graph's
  postorder with the coordinate at that retained value and every other
  source at the piece's LEFT END. A node whose level sits exactly on a
  surface takes the branch its OPERATOR gives; if the level then LEAVES
  the surface into the region immediately on that side, the node is
  FLIPPED there — a zero-length piece — and every branch is decided
  again; a node flipped twice refuses the tick as a sliding mode,
  committing nothing. With the branches fixed the substituted skeleton
  gives the coordinate's own path as an ordinary evaluation, each
  dependent level is followed along it, and the piece is cut at the FIRST
  surface any of them reaches strictly inside it — SOLVED where the level
  and the skeleton are affine along the path, otherwise sampled at
  `_SUBDIVISIONS` and bisected to `_CROSSING_TOLERANCE`. A crossing found
  within that tolerance of the piece's left end is NOT folded into it:
  folding it would integrate the piece under the near-side branch and
  drive the part through its gap. `_MAX_CROSSINGS` bounds the whole walk,
  as it already bounds a partition.

**After a cut the driven coordinate is committed AT THE FAR SIDE of the
surface, at the nearest representable value** — ADR-108's "committed AT
its bound exactly" transposed to a surface that is not stated in the
coordinate's own units. The segment's arithmetic finds the landing; the
landing is then walked to the adjacent float, by stepping out with the
stride doubling from one ulp and bisecting the bracket in FLOAT space
until the two are adjacent. No tolerance anywhere. Where the piece did
not move the coordinate — a level that crossed by the sources' motion
while the gate held — there is nothing to walk. A cut that finds no
bracket raises `LandingInvariantError` and refuses the tick, as a broken
stop invariant does, rather than committing the one value this decision
says is never committed.

**The run commits that float.** `Edge.increments` reports, beside its
increment, the ABSOLUTE value a driven end whose walk took at least one
cut holds at the tick's end; `Run._pass` carries the report the way it
already carries crossings — caller-owned and fresh per propagation, so a
refused segment's report is dropped with it — and `Run.integrate`
applies it exactly where it already writes a stop's bound, BEFORE the
stops are located, so a stop on the same coordinate in the same segment
wins: a physical bound is a bound of the coordinate itself. Committing
`value + delta` is not enough on its own, because `x + (y − x) != y` for
about six pairs of floats in a hundred, and a ulp back toward the
surface is the ENGAGED side of the gate.

**The model must state a gate whose DISENGAGED state has WIDTH**, and
the width is the mechanism's own clearance — a symmetric band about the
zero, entered from either side, so the part stops at the band's edge it
arrives at. The framework requires no particular width: any positive one
holds from both directions.

**A self-read crossing is NOT a stop.** It stops no input, retires no
command, and records as a `Crossing`. A declared range on the driven
coordinate still stops it over this same partition and is committed at
its bound exactly.

**The self-read id is a `needs` of the edge that is also one of its
`gives`.** `_ordered` (Kahn) ignores a need an edge itself gives — a
read of what a coordinate HOLDS is not a wait on something else — and
`_reaching_inputs` needs no change, since it already reads `found[key]`
before updating it. So the published rule that an edge's expressions
read exactly the ids in `needs` stays true, and a consumer identifies
the self-read as `needs ∩ gives` with no new document key.

**A program carrying at least one self-read edge makes the document
version 6**; a program with none publishes byte-identically at 5
(ADR-057's rule: a version 5 consumer would evaluate `f(end) − f(start)`
with the read at both ends, freeze the branch and move the part by a
different mechanism in silence). The LANDING is behaviour, not a
document key, and the conformance corpus (ADR-111) is what pins it: it
gains machines exercising a self-read gate and a self-read crossing in
the same tick as a stop, and the generator refuses a corpus that carries
none.

## Consequences

- **The Curta's requirement is sayable, and the five behaviours follow
  from the run.** A dial swept from any digit runs to its gap and stops
  while the ring sweeps on; an already-cleared dial does not turn again;
  a partial sweep is retained through inspection, snapshot and restore
  and resumes; both directions clear to the edge they arrive at; and
  several dials from one input disengage independently. What the model
  owes in return is stated rather than hidden: a gate with a WIDTH, and a
  guarded rest default on every driven coordinate. The migration's own
  shape — the rack-station term and the band gate replacing
  `cycle.cleared_position` for the running model — is project work in the
  project's repository.
- **Nothing without a self-read moves.** `Train`, the pin, evaluates the
  same **80 graphs over ten ticks** before and after, at 92.8 ms against
  93.6 ms best-of-seven; a law with no self-read pays one boolean test
  per driven end per tick and is otherwise byte-for-byte ADR-107's path.
  Every existing corpus scenario is byte-identical — 14 old scenarios, 3
  added, 0 changed, 0 removed, in 17 scenarios over 14 machines and 328
  ticks — and the whole suite is green at 2 928 passed, 4 skipped,
  1 664 subtests.
- **The searched cost of a kinked skeleton is real, and the Curta pays
  it.** A self-read law whose skeleton is affine has its crossings SOLVED
  and runs at **1 349 ticks/s** on the `Clearing` fixture. The migration's
  own shape gates a `clamp01` station window, and `_affine_in_sources`
  calls a CALL non-affine, so every crossing falls to the 64-sample
  search: **24.4 ticks/s** on `CurtaInterface` (27.2 after the closure's
  fixes), about **29 times** the solved shape per tick, at 2 861 graph
  evaluations against 99. `clamp01` is two kinks whose pieces are affine,
  so a cheap exact path exists; it is a follow-up, not this decision.
- **The walk forfeits ADR-107's solve-every-surface-at-once inside a
  layer-two piece.** Correctness is unaffected — three tooth windows in
  one tick are still three throws, as three successive pieces — and the
  cost is one extra skeleton evaluation per piece plus the landing walk.
- **A knife-edge gate is documented, not refused.** A gate whose
  disengaged set is a single value of the coordinate cannot be told from
  a band structurally: the distinction is numeric, not syntactic. It held
  in every case probed — ratios `1`, `7/3`, `0.7` and `π`, digits `108`,
  `107.3` and `12.345`, both directions, two step sizes — because `_land`
  walks the crossed nodes in postorder with the others at their near-side
  branches, so coincident `floor` and comparison surfaces land the
  coordinate exactly ON the surface, where the comparison reads
  disengaged. The tests assert only that, `docs/scenarios.rst` promises
  neither the failure nor the hold, and the WIDTH obligation stands as a
  statement about the MODEL: a single float is not a gap, and nothing
  guarantees another model's numbers land on it rather than past it.
- **A version 6 document breaks every current consumer, which is the
  point.** A consumer must read `needs ∩ gives` as a read, walk the two
  layers, land on the far side and commit the absolute; one that lands a
  ulp short re-engages the gate and diverges from the fixture's bank on
  the NEXT tick, far outside the corpus's agreement window, which is
  exactly how the corpus pins it. The browser viewer executes such a
  document in its own cycle in its own repository, held to the corpus
  this change regenerates.
- **A `.repeat()` self-read cannot be a RUNNING machine today**, so the
  corpus carries none. A repeated child's JOINT coordinate has no
  qualified id the run can bank it under (`DriverIdError` on the base
  tree, with no self-read in sight) — a pre-existing limitation, not this
  decision's to lift. The couplings resolution rule is implemented and
  tested directly: four records, each copy reading its own slot.
- **The walk's rules are statements of fact, and three were learned from
  failures the prototype could not meet.** A surface EQUAL to the level
  at a sub-interval's left sample is not a crossing of that sub-interval;
  the surface the path reaches first is the one NEAREST that sample, not
  the lowest, because a descending level crosses them in the other order;
  a flipped node takes the region IMMEDIATELY on the side its level
  departs to, which is the only reading of "the other branch's region"
  for a primitive with more than two; and every crossing strictly inside
  a piece is returned, a hair from its left end included. None of them
  introduces a tolerance. They are visible only on a gate whose read
  changes the RATE rather than holding the part, which is why the design
  did not anticipate them and the corpus's own machines did not show
  them.
- **Follow-ups, recorded rather than guessed at:** a joint walk for a
  driven group with a self-read; an exact path for a kinked but
  piecewise-affine skeleton; whether a gate with no width should be
  refused; and `a.drives(a)` one-to-one, which ADR-100 declined to widen
  its refusal to and which still deadlocks into `UnreachedCoordinate`.
  ADR-113's pushing test remains net over the stretch, and a self-read
  gate makes that limit easier to reach — an input that pushes over the
  first half of a stretch and is disengaged over the second is counted as
  pushing.
