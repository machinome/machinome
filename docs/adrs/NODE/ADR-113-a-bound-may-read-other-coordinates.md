# ADR-113: A Bound May Read Other Coordinates — A Constraint Stops What Carries It Outward

**Status:** Accepted, amended by ADR-134
**Date:** 2026-09-14
**Depends on:**
- [ADR-108: A range is a physical stop that stops the connected group](./ADR-108-a-range-is-a-physical-stop-that-stops-the-connected-group.md)
- [ADR-109: A range bound may be an expression evaluated at the committed state](./ADR-109-a-range-bound-may-be-an-expression-evaluated-at-the-committed-state.md)
**Amends:**
- [ADR-109](./ADR-109-a-range-bound-may-be-an-expression-evaluated-at-the-committed-state.md) — its deferral of a bound over a second coordinate
**Cites:**
- [ADR-089: `drives` relates two coordinates](./ADR-089-drives-relates-two-coordinates.md)
- [ADR-097: A joint is stated in the frame of whoever declares it](./ADR-097-a-joint-is-stated-in-the-frame-of-whoever-declares-it.md)
- [ADR-110: The compiled program is published in the document](../EXPORT/ADR-110-the-compiled-program-is-published-in-the-document.md)
- [ADR-111: A conformance corpus is the contract between the two runtimes](../EXPORT/ADR-111-a-conformance-corpus-is-the-contract-between-the-two-runtimes.md)
**OpenSpec change:** `bounds-read-other-coordinates`

## Amendment — 2026-09-20

[ADR-134](ADR-134-ancestors-add-constraints-without-replacing-joints.md)
admits an ancestor's separately stated constraint on an existing descendant
joint. Its contributions intersect with the original range rather than
competing to replace it. The original `Bound` scope and execution meanings
below remain unchanged; the separately stated form owns its own ancestor scope.

## Context and Problem Statement

ADR-109 let a range bound be a callable of the joint's OWN coordinate
and deferred, by name, a bound over a second one: "the obstacle is
naming, not semantics", because a joint is class metadata resolved
before any qualified id exists. The deferral cost the Pascaline nothing.
It cost the pin tumbler lock (`projects/Locks/Pin_tumbler_lock`) its
mechanism. The plug of a five-pin lock turns only when every one of five
splits lies at the shear line, and once turned it captures the key: two
declared ranges each of whose bound depends on OTHER coordinates — the
plug's turn on five pin lifts, the key's travel on the plug's turn. The
project modelled both as a pose with a Python state machine beside it
and the same state machine again in a browser controller, because
nothing in the framework could say them. A gated law cannot: `turn *
aligned(...)` into the plug leaves the plug still while the `turn` input
advances and its command reports `completed`, and a lock that will not
turn is a stop on the plug's coordinate that stops the input pushing it
(ADR-108).

Naming turned out to be the smaller half. The pilot's brief asked five
questions before any syntax, and three of them are about what such a
bound MEANS when the coordinates it reads move in the same tick:

- ADR-109 evaluates a bound once per tick at the tick's start. A tick
  that withdraws the key 5 mm while turning the plug 30° would evaluate
  the plug's bound with the pins still aligned and the key's with the
  plug still at zero, admit both, and commit a plug turned with its pins
  misaligned — a whole tick of penetration, and a different amount at
  every `dt`.
- The plug stands turned; the key withdraws; the pins would rise into
  the housing. ADR-108's detection sees nothing: the plug's coordinate
  did not move, so by the direction test it is free.
- When the coordinate that stopped is not the one that moved, which
  inputs does the stop stop?

## Decision Drivers

- The declaration must name what it reads the way the framework already
  names coordinates, checked where the classes are known, and must work
  for a joint declared where a child is placed (ADR-097), which is where
  a constraint over siblings has to live.
- Any combination of commands in one tick must commit a state that
  satisfies every bound at the tick's end — no clamp, no teleport, and
  no penetration beyond the crossing tolerance — at every `dt`.
- A standing coordinate must never be overrun by a dependency.
- ADR-108's vocabulary is complete: `blocked` with the admitted travel,
  no backlog, no resumption.
- One declaration poses and runs (ADR-109); the ratchet keeps retaining;
  the Pascaline's document stays byte-identical.
- Nothing about a self-only bound changes: not its meaning, not its
  code path, not its cost.

## Considered Options

**The declaration.**

1. Strings, `reads=('pawl.lift',)`, as ADR-109 sketched. Rejected: a
   second naming grammar with no class-definition check.
2. A relation-shaped verb, `(p1.lift & …).bounds(turn, law=…)`. Rejected
   for ADR-109's reason against `detent=`: two places to say where a
   coordinate may travel, to be reconciled at posing time.
3. **`Bound(expression, reads=(...))` inside the range pair**, its reads
   the references a relation's ends are. Chosen.

**The evaluation point.**

1. Freeze every argument at the tick's start (ADR-109 extended).
   Rejected: the two-command tick above.
2. Read every argument along the path, the own coordinate included.
   Rejected: `36 * floor(turn(t) / 36)` follows the arbor down and the
   ratchet never blocks.
3. Reads on a linear chord, the linearization ADR-108 accepts for a
   stop's other coordinates. Rejected: a bound over other coordinates is
   a step in every sighting, and a chord puts the step on the wrong side
   by the chord's error.
4. **Own coordinate committed, reads along the path, computed by the
   sub-program that determines them.** Chosen.

**Detection.**

1. At the stretch's ends, `g(1) > 0` and `g(1) > g(0)` — ADR-108's test
   on the constraint level. Ratified first, and corrected before the
   planning commit: a constraint over moving reads can be violated inside
   a stretch and satisfied at its end, and the end test commits three of
   the change's own scenarios — the plug turning while the pins align,
   the key withdrawing while the plug returns, the pawl lifting after the
   arbor has met its tooth.
2. Sample only when the bound's VALUE differs between the ends.
   Rejected: a bound that flips and flips back inside a stretch reads
   equal at both ends.
3. **Sample the level inside the stretch whenever something the bound
   depends on moves.** Chosen.

**What a dependency's motion does to a standing coordinate.**

1. Nothing — the coordinate is free by the direction test. Silent
   penetration; ruled out.
2. Refuse the tick, naming the reciprocal bound the author should state.
   Honest and smaller, but a refusal where the machine has a mechanical
   answer, and every constraint becomes a pair of declarations that can
   disagree.
3. **Stop the inputs whose motion carries the constraint outward,
   through the reads as well as through the bounded coordinate.** Chosen.

## Decision

**Either bound of a joint's `(lo, hi)` `range` MAY be
`Bound(expression, reads=(...))`.** `expression` is applied to the
joint's own coordinate first and then to each read, in the order `reads`
states them, and returns an expression in `solid_node.math`'s vocabulary;
a one-argument callable is the `Bound` with no reads and keeps ADR-109's
meaning. `reads` takes what a relation's end takes, through the same
`coordinate_ref` — a joint or port the declaring body owns, a path
through child declarations, a driver of the declaring class — and is
refused at class definition by the same rules, plus one: a read naming
the bounded coordinate itself. Reads resolve against the joint's
DECLARER — the node for a class joint, the declaring parent for a site
joint — where values are needed and never at realization: at simulation
construction under a running root, and at the close of the enumeration
that bound the coordinate everywhere else. A `Bound` whose expression
returns a plain number, or never reads a coordinate it declares, is
refused at construction.

**Under a running root such a bound is a CONSTRAINT between the
coordinate and what it reads, evaluated along the stretch's path.** The
joint's own coordinate in the expression takes the value it holds in the
TICK's committed bank (ADR-109's rule, which is what makes a ratchet's
tooth the tooth it started the tick on); every read takes the value it
has along the path, computed by one pass over the bound's SUB-PROGRAM —
the compiled edges that determine the bounded coordinate and every read,
in program order — with every admission scaled by the fraction, so the
sample arithmetic is the segment arithmetic, edge for edge. The
CONSTRAINT LEVEL `g` is the coordinate's value minus the evaluated upper
bound, or the evaluated lower bound minus the value; outside is positive.

**Detection and localization are one procedure, and it looks inside the
stretch.** A constraint is examined only when something it depends on
moves in the stretch — the bounded coordinate or any read has a nonzero
increment over it — so a quiet stretch evaluates nothing and a
coordinate standing outside, where the localization may leave it within
the crossing tolerance, is free until something carries it further. When
only the bounded coordinate moves, the bound is a NUMBER for the stretch
— its expression at the tick's committed own value and the reads'
standing values, evaluated once — and the coordinate is stopped or freed
exactly as ADR-108 stops a self-only bound, solved and committed at the
bound; the plug turning with its pins standing still pays one
evaluation. When a read moves, `g` is sampled at `_SUBDIVISIONS` fractions of the
stretch; the constraint stops the stretch at the first sample at which
`g > 0` and `g > g(0)`, the crossing bracketed against the previous
sample and bisected to `_CROSSING_TOLERANCE`, and `t*` is the INSIDE end
of the final bracket — the last fraction at which the bound is
satisfied. No case is solved and no fourth tolerance is introduced. The
coordinate is NOT snapped onto the bound: there is nothing to snap to on
a step, the coordinate that stopped may not have moved, and the segment
committed at `t*` by the same arithmetic satisfies the bound by
construction — which the run asserts at commit, refusing the whole tick
as a broken invariant otherwise.

**The group a constraint stops is every input whose own admission
carries `g` outward** — the candidates being the inputs reaching the
bounded coordinate or any read, each tested alone over the sub-program,
ADR-108's `_pushes` with the coordinate's increment replaced by the
constraint's. An input moving the bounded coordinate against the
constraint is stopped; an input moving a read so as to RELIEVE it runs
its full tick; an input moving a read so as to make a standing position
invalid is stopped where the constraint becomes active, and the standing
coordinate does not move. Commands on stopped inputs retire `blocked`
with the travel they admitted, nothing resumes and nothing is
remembered — ADR-108, unchanged. A `Stop` records the bounded
coordinate, the side, the bound evaluated at the committed state, the
fraction and the inputs blocked, so the key stopped by the turned plug
records `plug.turn`, `high`, `90.0`, `t*`, `('insertion',)`.

**Untimed, such a bound is judged when the enumeration closes.** The
binding of a coordinate whose range has a `Bound` side is not judged at
bind time — its reads are bound by the solver in an order the author does
not state — but recorded on the open enumeration and judged after
deferred relations have propagated, over the values then bound: outside,
`JointRangeError` names the node, the joint, the value, the unit, the
evaluated bound and every read with its value. A read holding no value
or a symbolic one is not judged, on the rule a symbolic binding already
has. A coordinate a running simulation owns is not judged by the
enumeration: the run judged it, and one authority judges one binding.

**Publication.** The span's expression names the ids it reads; the
identity changes with them; no document version is added — the shape is
unchanged and a consumer that cannot read a bound over several names
refuses it by name. The conformance corpus (ADR-111) must exercise a
bound reading another coordinate and a stop reached by the motion of
what a bound reads, so the viewer's own cycle has a fixture to be held
to.

## Consequences

- The lock's two interlocks are two declared ranges in the body where
  their parts are, and the capture follows from the plug's bound without
  a second declaration — though the lock states it a second time on the
  key's travel, because it is a fact of the mechanism worth reading, and
  the two agree.
- **Self-only bounds are untouched**, code path included: `Train`
  measures the same deterministic count of graph evaluations and the
  same wall time as before; the Pascaline module's suite and its
  published program identity are unchanged.
- **The cost is stated, and it is not ADR-109's.** A tick in which
  nothing a constraint depends on moves pays nothing for it, and one in
  which only the bounded coordinate moves pays one evaluation. A tick in
  which a READ moves pays up to `_SUBDIVISIONS` sub-program passes for
  that constraint whether or not it stops — the price of looking inside
  the stretch — and a stop adds the bisection and one pass per moving
  candidate. Measured on the lock-shaped `Gate` fixture (a four-edge
  sub-program): a quiet tick 0.36 ms and 8 graph evaluations, an active
  tick 5.4 ms and 528, a blocking tick 3.3 ms and 328. On the lock
  itself, whose plug bound reads five `piecewise` laws of 8–26 knots:
  2.9 ms idle, 4.7 ms turning the seated plug, 45 ms advancing the key
  (193 ms before the static-reads shortcut). Each sample costs about a
  program pass over the sub-program; the follow-ups a performance cycle
  would take — `f(start)` once per stretch per edge, one sampling for
  the two sides of one coordinate — are recorded in `workflow/warts.md`.
- **What is still not seen**: a violation that begins and ends inside
  ONE sub-interval of the search — ADR-107's limit for a level quantity
  that turns twice, with the same answer, a smaller `dt`. The pushing
  test is net over the stretch, not local at `t*`; the remainder is
  examined again after each event. Two inputs that carry a constraint
  outward together while neither does alone stop no one and refuse the
  tick as a broken invariant, ADR-108's own rule for a multi-source law.
- **A constraint's reach is its declarer's subtree**, which is a
  relation's reach from the same body. A joint whose bound must read a
  cousin is declared at the site whose subtree holds both — a statement
  about where the constraint belongs, not a workaround.
- **`Program.spans` keeps its shape**; the program additionally carries,
  per constraint, the read ids, the sub-program and the candidates —
  projections of `edges` and `sources` with no decision in them, derived
  rather than published (ADR-110).
- **The viewer's worker refuses the lock's document by name** until its
  own cycle widens the free-name check on a span and reproduces this
  decision; the regenerated corpus is what that cycle is held to.
- A root driver whose bare name a joint anywhere in the tree also bears
  is ambiguous under a running root, because `set_state` records both
  under the bare name. Pre-existing and not this decision's, but the lock
  meets it: its plug rotation input cannot be called `turn`.
