## Context

ADR-108 made a joint's declared `range` a physical stop under a running
root: a coordinate that would leave a bound is stopped at the fraction
`t*` of the tick at which it reaches it, every input whose own motion
pushes it is stopped for the rest of the tick, and their commands
retire `blocked` with the travel they made. ADR-109 let either bound be
a callable of the joint's OWN coordinate, compiled once at `Sim`
construction into an expression graph over that one qualified id and
evaluated once per tick, at the tick's start, from the committed bank —
which is what makes `36 * floor(turn / 36)` the last seated tooth. Both
are implemented, archived and pinned: `tests/test_running_stops.py`, the
Pascaline module's own six running scenarios, and the conformance corpus
of ADR-111 that the viewer's worker replays.

ADR-109 deferred a bound over a SECOND coordinate, naming the obstacle
precisely — "the obstacle is naming, not semantics" — and sketching
`Bound(lambda turn, lift: ..., reads=('turn', 'pawl.lift'))`, resolved
against the declarer's subtree at `Sim` construction. The pilot's brief
for this change says not to take that sketch on trust. Three of its five
questions are about semantics the sketch does not settle:

- the evaluation point. ADR-109 evaluates a bound once per tick at the
  tick's start. For the ratchet that is the whole point: a bound that
  followed the arbor along its reverse travel would never block it. For
  a bound that reads OTHER coordinates it is not enough: a tick in which
  the key withdraws by 5 mm while the plug turns by 30° would evaluate
  the plug's bound with the pins still aligned and the key's bound with
  the plug still at zero, admit both, and commit a plug turned with its
  pins misaligned and a key withdrawn from a turned plug — a whole
  tick's travel of penetration, and a different amount at every `dt`;
- what happens when what a bound reads moves so as to make a STANDING
  position invalid. The plug stands turned at 30°; the key withdraws; the
  pins would rise into the housing. Nothing in ADR-108's detection sees
  it: the plug's coordinate did not move, so by the direction test it is
  free, and the run would commit the pins moved through the plug;
- which inputs a stop stops when the coordinate that stopped is not the
  one that moved.

The originating project is the pin tumbler lock. Its measured facts, from
its own records (`docs/measurements.md`, `simulation/contact.py`,
`simulation/flexibles.py`): the key travels from −60 mm (withdrawn) to 0
(seated); five pin stations at 5.5 + 7.2·i mm; a pin's lift is the
support the key's Y = 0 envelope gives it under a 1.25 mm flat tip with
a 1.2 cone slope, relative to its source pose, plus a 0.05 mm seating
gap — piecewise linear in the key's travel; the split clears the shear
line when the lift lies in the conservative window [−0.15, 0.05] mm (the
matching key seats every pin at −0.10, the deep key at −0.85, the shallow
at +0.65); a spring's height is 17.9 − lift, its source free length 24 mm
and its source compressed reference 11 mm, so the source's own two
numbers bound a key pin's lift to [−6.1, 6.9] mm — a visualization limit
the source states, not a coil-bind or material limit, which the source
does not establish. The lock's driver pins are `DriverPin().repeat(5)`,
list-held children owning a joint, and `driver_id` refuses the segment
`drivers-0` by design; the supported naming is five attributes, as the
key pins `p1`…`p5` already are. That is the project's migration, not
this change's.

The second project that must not move is the Pascaline module: its
input arbors declare `range=(None, lambda turn: DIGIT_STEP *
ceil(turn / DIGIT_STEP))`, its six running scenarios assert the blocked
positions and admitted travel to twelve places, and its document test
asserts that no span expression names a second coordinate. All of that
stays true under this change because a one-argument callable keeps its
meaning and its code path.

## Goals / Non-Goals

**Goals:**

- One declaration form for a bound that reads other coordinates, named
  the way a relation names its ends, resolvable for a class-declared and
  a site-declared joint alike.
- A running semantics under which any combination of commands in one
  tick commits a state that satisfies every bound at the tick's end, with
  no clamp, no teleport, and no penetration beyond the crossing
  tolerance, at every `dt`.
- A stop that stops what physically carries the constraint: the inputs
  moving the bounded coordinate AND the inputs moving what the bound
  reads, so a standing coordinate is never overrun by a dependency.
- The same handle vocabulary, the same admitted-travel report and the
  same no-backlog rule as ADR-108.
- An untimed meaning that refuses an impossible pose by name, a
  construction that refuses an impossible rest pose, a snapshot that
  cannot restore into a machine whose constraints changed, and a
  published program a second runtime can execute.
- The pin tumbler lock migrated, in its own repository, as the
  acceptance case, and the Pascaline module byte-for-byte unchanged.

**Non-Goals:**

- Contact, force, friction, spring stiffness, or a detent that is not a
  kinematic bound. A constraint here is a declared bound on one
  coordinate, read at a committed and along-path state.
- A general constraint solver. A bound is a function of coordinates the
  author names; the run never inverts it, never solves several
  simultaneously beyond the earliest-first segmentation ADR-108 already
  has, and never chooses between two consistent resolutions.
- A new relation verb, a new keyword beside `range=`, or a bound stated
  in the class body as an expression over tokens (ADR-109 rejected both,
  for reasons that still hold).
- Bijective sanitization of list-held child names. The lock names its
  pins; the framework's naming rule is untouched.
- The viewer's worker. Its change is one cycle in `solid-node-viewer`,
  held to the corpus this change regenerates.
- Running-command cancellation (`workflow/warts.md`, "Pin tumbler lock
  (2026-09-14, running-command cancellation)"). Independent, filed,
  untouched here.

## Decisions

### 1. The declaration: `Bound(expression, reads=(...))` inside the pair

```python
class Plug(AssemblyNode):
    p1 = Pin(depth=cut_1)
    ...
    p5 = Pin(depth=cut_5)
    turn = Revolute(
        axis=(0, 0, 1),
        range=(0, Bound(lambda turn, l1, l2, l3, l4, l5:
                        90 * clear(l1) * clear(l2) * clear(l3)
                           * clear(l4) * clear(l5),
                        reads=(p1.lift, p2.lift, p3.lift, p4.lift,
                               p5.lift))))
```

with `clear(l) = (l >= -0.15) * (l <= 0.05)` written over
`solid_node.math`'s vocabulary. `Bound` lives in
`solid_node.motion.joints` beside the joints it goes into.

`expression` is applied to the joint's own coordinate FIRST and then to
each read, in the order `reads` states them — so a one-argument callable
is the `Bound` with no reads, and a `Bound(f)` with `reads=()` means
exactly `f`. `reads` takes what a relation's end takes, through the same
`coordinate_ref`: a joint or port the class body owns (`turn`), a path
through child declarations (`p1.lift`, `pawl.lift`), or a driver of the
declaring class. What that path grammar already refuses, it refuses
here, at class definition, where the classes are known: a declaration
held in a list (`drivers-0` is not a name a class body can write), a
repeated child (a broadcast names every copy, and a bound reads one
value), a child whose class declares no joint or several, a driver read
sideways off a child. A read that resolves to the bounded coordinate
itself is refused too: the own coordinate is the first argument, and
naming it twice would give one value two positions.

**Where the checks fire.** `reads` becomes references through
`coordinate_ref` in `Bound.__init__`, and each one's own
`check('driver')` runs there — a read IS a source, so a path through a
repeated child is refused by the very message a relation's source gets
(`BroadcastRef.check`), and a declaration held in a list by
`PathRef.check`'s. Those messages read right that early because
`_DeclaringNamespace.__setitem__` names a child declaration the moment
the body assigns it, so `p1._name` is already `'p1'` while the body runs.
The two checks that need the DECLARING CLASS — `check_declared_on`, and
the refusal of a read naming the bounded coordinate itself, which needs
the joint's own name — fire where a relation's do, once the class
exists: for a CLASS-declared joint in `Joint.__set_name__`, whose
`owner` IS the declaring class; for a SITE-declared joint in
`ChildDeclaration.__set_name__`, beside `_check_wiring`, whose `owner`
is the declaring parent. A site joint's own `__set_name__` cannot serve:
`_specialize` fires it against the specialized CHILD class, which is not
the declarer and holds neither `key` nor `p1`.

*Rejected: strings, `reads=('pawl.lift',)`, as ADR-109 sketched.* A
second naming grammar beside the one relations use, with no
class-definition check — a misspelling would surface at `Sim`
construction or, untimed, at the enumeration's close. The path
references exist already, carry the check, and read the same in a
relation and in a bound.

*Rejected: a relation-shaped verb, `(p1.lift & ... ).bounds(turn,
law=...)`.* A joint would then have two places to say where it may
travel, and untimed posing would have to reconcile them — ADR-109's
reason for rejecting `detent=` applies unchanged.

*Rejected: an expression over references directly in the pair,
`range=(0, 90 * clear(p1.lift) * ...)`.* A `DerivedCoordinate` is a
coefficient map — linear by construction, so neither a comparison nor
`abs` nor `min`/`max` can be written on it — and giving references the
whole symbolic vocabulary is a far larger change than a bound needs.

### 2. Resolution: against the declarer, where the ids exist

A `Bound`'s reads are resolved against the joint's DECLARER, exactly the
instance a joint argument callable is handed (joints spec, "Joint
arguments resolve against the instance at realization"): the node itself
for a class-declared joint, and the realized declaring parent for a
site-declared one (`plug = Plug(turn=Revolute(range=(0, Bound(...,
reads=(p1.lift, ...)))))` stated in the lock's body resolves `p1.lift`
from the lock). `PathRef.resolve(declarer)` walks the realized children
the way it does for a relation and yields the owning node and the
declaration; the qualified id is `driver_id(instance_path(node, root),
name)`, the same id the bank keys by. A site joint knows it is one
(`Joint._declared_at_site`), so the declarer is the node's linked parent.

Resolution happens where the VALUES are needed, never at realization —
the subtree is not linked yet then, which is the obstacle ADR-109
recorded:

- under a running root, at `Sim` construction in `_compiled_spans`, once
  per bound, to qualified ids; a read that is not in the bank — a plain
  port, a derived coordinate — is refused by joint and node identity,
  because a bound reads the STATE and a plain port is a calculation the
  enumeration recomputes from it ("read the joint the port follows");
- untimed, at the close of the enumeration that bound the coordinate
  (decision 6), to slots, cached on the node beside the resolved joint
  arguments but in a cache OF ITS OWN, keyed by joint name — not inside
  the `_joint_arguments` tuple, which is positional (`place` unpacks the
  first three, `_refuse_out_of_range` reads index 2, an `Orbit`'s
  carried point is already index 3) and has no fourth position to
  lend.

The reach of a bound is therefore its declarer's subtree, which is the
reach of a relation stated in that body. A joint whose bound must read a
cousin is declared at the site whose subtree holds both — the lock's
`Plug` body, where the turn and the five key pins are — and that is a
statement about where the constraint belongs, not a workaround.

### 3. Evaluation under a running root: own committed, reads along the path

Let `c` be the bounded coordinate and `R` the coordinates its bound
reads. Over a stretch of tick with path `x(t)`, `t ∈ [0, 1]`, the CONSTRAINT
LEVEL of a high bound is

```text
g(t) = c(t) − hi(c₀, R(t))
```

and of a low bound `g(t) = lo(c₀, R(t)) − c(t)`, where `c₀` is the value
`c` holds in the TICK'S committed bank and `R(t)` are the values the read
coordinates take along the path. Outside is `g > 0`.

The own coordinate is read COMMITTED, as ADR-109 states: what a bound
says about the coordinate it bounds is a statement about where it stood,
and that is what makes a ratchet's tooth the tooth it started the tick
on. A read coordinate is read ALONG THE PATH: what a bound says about
another part is a statement about that part's geometry, which moves in
the same tick. The pawl fixture shows the two together — `lo = 36 *
floor(turn / 36) − 1000 * (lift >= 1)`: the tooth is the committed
arbor's, and the pawl lifting at `t = 0.3` while the arbor reverses from
40 frees it before it reaches 36 (it completes at 30), while the pawl
lifting at `t = 0.5` finds the arbor already stopped at 36 at `t = 0.4`
and the command retired `blocked` with −4 admitted.

`R(t)` is computed the way the segment will later be COMMITTED: the
inputs' admissions scaled by `t`, propagated over the edges that
determine `c` and `R` — the SUB-PROGRAM of the bound, computed once at
compile time by walking determiners back from `c ∪ R`, in program order.
That is the sample arithmetic being the segment arithmetic, edge for
edge, which is what lets the committed state at the stop satisfy the
bound by construction rather than by a snap (decision 5). For a law that
jumps, the edge's `increments` runs its plan over the truncated path,
exactly as `_along` does today.

*Rejected: freezing the reads at the tick's start, ADR-109's rule
applied to every argument.* The two-command tick above commits a
penetration one tick deep, and the pilot's brief names this as
insufficient. Also rejected because it makes the answer depend on the
caller's cadence, which ADR-108's "a stop admits the same travel at any
cadence" forbids.

*Rejected: the own coordinate along the path too.* It breaks the
ratchet: `36 * floor(turn(t) / 36)` follows the arbor down and the
reverse never blocks. The asymmetry is principled — the self-reference
is the only argument whose value is the thing being bounded, and ADR-109
made it well defined precisely by reading it committed.

*Rejected: reads on a linear chord, `R(0) + ΔR · t`, the linearization
ADR-108 accepts for a stop's OTHER coordinates.* A bound that reads other
coordinates is normally a step (a comparison, a window), and a chord
puts the step on the wrong side by the chord's error, which the pass
then commits and the enumeration's close would refuse. ADR-108 rejected
a full program pass per sample on cost — 137 ms on `Train` — and the
sub-program is the cheaper thing that is still exact: the lock's bound
reaches five edges.

### 4. Detection, localization, and what the stop stops

**Detection and localization are ONE procedure, and it looks inside
the stretch.** A constraint is examined on a stretch only when something
it depends on moves in that stretch — the bounded coordinate or any read
has a nonzero increment over it, which the pass has already computed.
Otherwise `g` is constant over the stretch, nothing is evaluated, and a
coordinate standing outside — where the localization can leave it,
within the crossing tolerance — stays free until something carries it
further. When something moves, `g` is sampled at `_SUBDIVISIONS`
fractions of the stretch, each sample one pass over the sub-program with
every admission scaled by that fraction. The constraint stops the stretch
at the FIRST sample `t_k` at which `g(t_k) > 0` and `g(t_k) > g(0)` —
outside, and carried further outside than it stood at the stretch's
start, by whatever moved. `g(0) > 0` with the first sample higher gives
`t* = 0`; otherwise the crossing is bracketed in `[t_{k−1}, t_k]`.

This is ADR-108's test made to look inside the stretch, and it has to:
a constraint that reads MOVING coordinates can be violated inside a
stretch and satisfied again at its end — the plug that turns while the
pins align in the same tick, the key that withdraws while the plug
returns, the pawl that lifts after the arbor has already met its tooth —
and a test at the ends alone commits all three (decision 11). The
end-of-stretch test stays for a bound reading its own coordinate alone,
whose `g` is monotone in `t` over an affine determiner and whose code
path this change does not touch.

**Localization.** The bracket `[t_{k−1}, t_k]` is bisected to
`_CROSSING_TOLERANCE` in at most `_BISECTION_ROUNDS` rounds, and `t*` is
the INSIDE end of the final bracket — the last `t` at which the bound is
satisfied — not its midpoint. No case is solved: a bound that
reads other coordinates carries a comparison in every sighting, and a
`g` with a jump in it is what the search is for. No fourth tolerance.
The stop is committed at `t*` and the segment `[0, t*]` is integrated by
the ordinary procedure with every admission scaled by `t*`; because the
sample and the segment are the same arithmetic on the same edges,
`g ≤ 0` holds at the committed state exactly.

**The group** a constraint stops is every input whose OWN motion over
the stretch carries `g` outward: the candidates are `Program.sources[c]`
together with `Program.sources[r]` for every `r ∈ R`, and a candidate
with a nonzero admission is in the group when, with its admission alone
applied over the sub-program and every other input's set to zero,
`g(1) − g(0) > 0`. That is ADR-108's `_pushes` with the coordinate's
increment replaced by the constraint's — one sub-program pass per
candidate, on a blocking tick only. Two consequences carry the physics:

- an input moving the bounded coordinate against the constraint is
  stopped (the `turn` input while the pins are misaligned); an input
  moving a read coordinate so as to RELIEVE the constraint is not (the
  `insertion` input aligning the pins in the same tick runs its full
  tick, and the turn is blocked at `t* = 0` with nothing admitted, to be
  asked again next tick);
- an input moving a read coordinate so as to make a STANDING position
  invalid is stopped where the constraint becomes active, and the
  standing coordinate does not move. The plug turned at 30°, the key
  withdrawing: the `insertion` input is stopped at the `t*` at which the
  first pin leaves the window, the key stands there, the plug stands at
  30, and the `insertion` command retires `blocked` with the travel it
  made. The capture is the plug's own bound read the other way; the lock
  states it a second time on the key's travel because it is a fact of
  the mechanism worth reading, and the two agree.

*Rejected: stopping only the bounded coordinate's pushers and refusing a
tick in which a dependency carries the bound over a standing coordinate
(the tick commits nothing, the commands retire `refused`, the message
says to state the reciprocal bound).* Honest, and smaller, but it makes
the run refuse where the machine has a mechanical answer, and it makes
every constraint a pair of declarations that can disagree. The pushing
test over `g` is one rule that covers both directions, and it is the
same test ADR-108 already runs, on a different increment.

*Rejected: silent penetration — the standing coordinate is free by the
direction test and the dependency moves through it.* The brief rules it
out, and it would leave the bank in a state the enumeration's own close
refuses.

**Several stops, atomicity, records.** Unchanged from ADR-108: the
earliest `t*` first, stops within the crossing tolerance one event, the
bank and admissions staged across segments, a failure anywhere
committing nothing. A `Stop` entry names the bounded coordinate, the
side, the bound's value evaluated at the committed state, the fraction
and the inputs blocked — so a stop carried by the motion of what the
bound reads records `plug.turn`, `high`, `90.0`, `t*`, `('insertion',)`,
which reads as what happened.

### 5. The commit: no snap for a bound that reads other coordinates

ADR-108 commits the stopped coordinate AT its bound exactly, because
`Run.bind()` delivers the bank through `set_state` and a joint binding
goes through the joint's own range check, so a localization a few ulps
outside would raise from the very tick that stopped it. For a `Bound`
with reads there is nothing to snap TO — the bound at `t*` is on one side
of a step or the other, and the coordinate that stopped may not have
moved at all — and nothing to snap FOR: the bind-time check defers a
`Bound` side (decision 6), and the committed state satisfies the bound by
the sample-equals-segment arithmetic of decision 3. The run asserts it
anyway: after the segment at `t*` it evaluates `g` once at the committed
state and raises `StopInvariantError` — the tick committing nothing — if
`g > 0`, so a broken invariant is loud rather than a picometre of
penetration nobody reported.

Self-only bounds keep ADR-108's snap and ADR-109's evaluation, on their
existing code path, untouched.

### 6. Untimed: judged when the enumeration closes

Under an untimed or looping root a range refuses a binding outside it,
and a callable bound is applied to the value being bound. A `Bound` with
reads cannot be applied there: the coordinates it reads are bound by the
solver in an order the author does not state, and at the moment `c` is
bound a read may hold last pass's value (swept by `clear_solved` — so in
fact `None`) or this pass's. Judging at bind time would pass or fail by
solver order.

So the binding of a coordinate whose range has a `Bound` side is
RECORDED on the open enumeration — `Enumeration` gains a third
container beside `deferred` and `reads`, of the same shape as
`note_unbound_read` — and judged at `_finish_enumeration`, after
`run_deferred` and `refuse_reads`, over the values then bound: the
reads resolved against the declarer (decision 2), the expression applied
to plain numbers, the pair ordered, and the value checked inclusive.
Outside, `JointRangeError` names the node's path, the joint, the value,
the unit, the evaluated bound, and every coordinate the bound read with
the value it read — the refusal ADR-109 said would "name the other
coordinates it read". A read that holds no value or a symbolic one at
the close is not judged, on the rule the joints spec already has for a
symbolic binding: its value is not known there. Outside any enumeration
— a hand assignment before the first render — there is nothing open to
record the binding on and no pass left to judge it at the end of,
exactly as a read of an unbound coordinate made there is not recorded
either (`note_unbound_read`): the binding places the body, and it is
judged at the close of the next enumeration that BINDS the coordinate
again — every enumeration, for a coordinate a relation drives; none, for
one only a hand ever binds.

A coordinate a RUNNING simulation owns is not judged by the enumeration
`Run.bind()` runs: the run located the stop, committed inside it and
asserted it (decision 5), and a second evaluation of the same bound by
the Python callable over floats could read a comparison at exact
equality the other way from the graph. One authority per binding: the
run for what it owns, the enumeration for the rest.

Under a running root the same declaration therefore poses and runs, as
ADR-109 required: the rest render at `Sim` construction is an untimed
enumeration, so a rest pose that violates a bound is refused at
construction by name; `solid snapshot --drive` is one too.

### 7. Compile, publish, identity, snapshot

`_compiled_spans` takes the ROOT beside the coordinate table — it has
to, because qualifying a read's owning node means
`instance_path(node, root)` — applies the callable to `symbol(own_id)`
and one `symbol(read_id)` per resolved read, walks the graph exactly as it does
for a one-argument bound, and requires its free names within
`{own} ∪ reads` — a callable that reads a name it did not declare
cannot arise, because the arguments are positional, but the check
stays. Jumps are admitted and need no plan, for ADR-109's reason: a
bound is evaluated, never integrated. `Program.spans` keeps its shape —
`(identifier, low, high, unit)`, the tuple the Pascaline's own test
unpacks — and a bound with reads is a graph in that tuple like any
other; the program ADDITIONALLY carries, per such bound, the read ids,
the sub-program edges and the candidate inputs, computed once — in
`Program.__init__`, after `self.edges` is ordered and `self.sources` is
built, since the sub-program is a filter of the first and the candidates
a union over the second.
`described()` prints the graph, so the identity changes with the reads
and a snapshot cannot restore into a machine whose constraints moved.
Snapshot and restore need nothing else: a blocked command is retired
when it blocks, and a restored bank is a committed one.

`published()` publishes the span as today, `{"expression": <graph>}`,
whose free names are the ids it reads; the sub-program and the
candidates are projections of `edges` and `sources` with no decision in
them, so by ADR-110's rule they are derived, not published. No document
version is added: the shape is unchanged, and a consumer that cannot
read a bound over several names refuses it BY NAME today (the shipped
worker's own check on a span's free names), which is the loud refusal
ADR-034 requires of a consumer that cannot read what it was given.

### 8. The corpus and the viewer cycle

`tools/generate_running_corpus.py`'s `REQUIRED` gains "a bound reading
another coordinate" (a span whose expression's free names are not its
own id alone) and "a stop reached by the motion of what a bound reads"
(a recorded stop whose coordinate holds the same value before and after
its tick). A fixture machine of the lock's shape exercises both. The
export spec lists them, so the corpus's width stays visible.

The viewer's worker widens the free-name check on a span to the bank
ids, evaluates a bound over the committed bank with the own coordinate
frozen, and reproduces decisions 3–5. That is a cycle in the viewer's
own repository, held to the regenerated corpus; until it lands, the
lock's document is refused by the shipped worker by name, and the lock's
browser acceptance waits on it.

### 9. What a tick costs

A tick in which nothing a constraint depends on moves pays nothing for
it. A tick in which something does pays up to `_SUBDIVISIONS`
sub-program passes for that constraint, whether or not it stops — the
price of looking inside the stretch — and a stop adds at most
`_BISECTION_ROUNDS` more plus one sub-program pass per candidate with a
nonzero admission. On the lock's plug bound the sub-program is about
seven edges, so an active tick costs on the order of 450 edge
evaluations for it, to be measured and recorded in the change's
evidence; a self-only bound keeps ADR-109's one evaluation per tick. A machine declaring no `Bound` with reads pays nothing: the
existing span path is untouched, and `Train` must measure what ADR-108
recorded, 1.065 ms/tick.

### 10. Decisions that become ADRs after implementation

One: "A bound may read other coordinates; a constraint stops what
carries it outward" — decisions 1–6. ADR-109's consequence "A bound may
NOT name a second coordinate in this release" is amended to point at it.
`docs/architecture.md`'s simulation section and its known-gaps list are
updated.

### 11. Correction after ratification: detection looks inside the stretch

The design as ratified stated detection at the stretch's ends —
`g(1) > 0` and `g(1) > g(0)` — the shape ADR-108 uses for a self-only
bound. The propose-phase audit of the source showed that this cannot
produce three of the scenarios ratified beside it, because `Run.integrate`
has one stretch per tick until a stop segments it and a constraint over
moving reads can be violated inside that stretch and satisfied at its
end. The arithmetic, over the fixture as stated:


  - *Insertion and turning in one tick* — key at `10`, one tick admits
    `feed +10` and `turn +30`, pins clear at `0.8`. `g(0) = 0 − 0 = 0`;
    `g(1) = 30 − 90 = −60`. Nothing is detected, and the tick would
    commit `plug.turn` at `30`; the scenario requires it blocked with
    `0` admitted. The constraint is violated throughout `[0, 0.8)` —
    `g(0.5) = +15`.
  - *Returning the plug and withdrawing the key in one tick* — plug
    `30 → 0`, key `20 → 15` with the capture bound. `g(0) = 20 − 20 =
    0`; `g(1) = 0 − 15 = −15`. Nothing is detected, and the tick would
    withdraw the key to `15`; the scenario requires the key to stand at
    `20`, blocked with `0` admitted. The plug's own high bound is not
    detected either: `g(1) = 0 − 0 = 0`.
  - *A pawl lifting during the tick releases the ratchet*, second half —
    arbor `40 → 30` while `pawl.lift` reaches `1` at `0.5`. At the
    stretch's end `lo = 36 − 1000 = −964` and `g(1) = −964 − 30 < 0`.
    Nothing is detected; the scenario requires a stop at exactly `36`,
    at `0.4` of the tick. (The first half, the pawl lifting at `0.3`,
    IS consistent: it completes at `30` with no stop.)

Decision 4 was therefore corrected before commit 1: detection samples
`g` inside the stretch whenever something the constraint depends on
moves, and decision 9's cost statement follows it. The alternative — keep
the end test and drop the three scenarios — was rejected because it
leaves the two-command tick committing a penetration, which is the case
the brief names. A trigger cheaper than sampling (search only when the
bound's VALUE differs between the ends) was rejected because a bound
that flips and flips back inside a stretch reads equal at both ends. The
correction is recorded here so the ratified record and the implemented
one are the same document, and it is flagged to the pilot in the cycle
report.

## Risks / Trade-offs

- [A violation that begins and ends inside ONE sub-interval of the
  search is not seen — a step bound that flips and flips back within
  1/64 of a stretch.] → The same limit ADR-107 states for a level
  quantity that turns twice inside one sub-interval, with the same
  answer: a smaller `dt`. Stated in the spec and the ADR.
- [Every active tick of a constraint pays the sampled search, not only a
  blocking one.] → Paid only by machines declaring such a bound and only
  on ticks in which something the bound depends on moves; a self-only
  bound and a machine without one pay nothing new. Measured on the lock
  and recorded.
- [The pushing test is over the whole stretch, net, not local at `t*`; a
  candidate that first pushes and then relieves within one stretch may
  test as not pushing.] → ADR-108's `_pushes` has the same shape; the
  remainder after the stop is examined again, so the next event catches
  it; a smaller `dt` narrows the window. Stated.
- [`t*` for a bound with reads is always searched, never solved.] → Cost
  on blocking ticks only, measured and recorded; the lock's sub-program
  is five edges. A solved case for an affine `g` is a later refinement
  the design leaves room for and does not need.
- [A constraint can be carried outward by two inputs TOGETHER while
  neither input's admission alone carries it: the group is then empty
  and the run refuses the whole tick as a broken invariant
  (`_runaway`).] → The shape ADR-108's `_pushes` already has, made
  likelier by a bound over several coordinates. Loud rather than silent,
  and a smaller `dt` does not fix it — it reports that the machine needs
  a bound the run can attribute. Stated.
- [The state after a stop can stand inside the bound by up to the
  crossing tolerance of the tick's travel, not on it.] → It is inside,
  never outside; the invariant is asserted at commit; a push further out
  next tick stops at `t* = 0` with nothing admitted.
- [Two evaluators of one bound — the Python callable over floats untimed,
  the graph under the run.] → Never both on one binding (decision 6). The
  graph is what the corpus pins.
- [The viewer refuses a document with such a bound until its cycle
  lands.] → By name, as ADR-034 requires. The lock's browser acceptance
  is sequenced after the viewer cycle; its Python acceptance is not.
- [A `Bound` on a class-declared joint can only read its own subtree.] →
  A constraint is declared where its parts are; the lock's shape is the
  `Plug` body. Stated as a rule, with the site declaration as the way to
  reach a wider subtree.

## Migration Plan

**Framework.** Additive. No existing declaration changes meaning; every
existing test stays green; the corpus regenerates with one machine
added.

**Pascaline module.** Nothing. Its ratchet is a one-argument callable
and takes the untouched path; its document test still finds no second
coordinate in any span.

**Pin tumbler lock** (in its own repository, its own OpenSpec change,
against this worktree's framework — the empirical acceptance run in the
apply phase of this cycle):

1. `PinTumblerLock` declares `time = Time.running()`; the drivers become
   `insertion` (−60 to 0 mm) and `turn` (0 to 90 deg); the five `lift_n`
   drivers go.
2. The driver pins become five named children `d1`…`d5 = DriverPin()`,
   as the key pins already are; the springs stay `.repeat(5)`, because a
   port is not banked.
3. In `Plug`: the key pins are declared before the turn; each pin's lift
   is driven by the key's travel through a law `piecewise(travel,
   knots_i)` whose knots are the exact breakpoints of the project's own
   `lifts_for` for that pin, generated by project tooling and pinned
   against `lifts_for` at 601 stations to the parity test's ten places;
   `turn` declares `range=(0, Bound(..., reads=(p1.lift, …, p5.lift)))`
   with the [−0.15, 0.05] window; the key's `insert` joint declares
   `range=(Bound(lambda insert, turn: -60 + 60 * (turn > 0),
   reads=(turn,)), 0)` — the capture stated where it is read.
4. Each driver pin's lift is driven from its key pin at ratio −1 and
   declares `range=(-6.9, 6.1)` in its own frame: the source's 24 mm free
   length and 11 mm compressed reference, recorded as the source's
   visualization limits and nothing more.
5. Instructions for stepped insertion: advance and back by one pin pitch
   (7.2 mm), seat and withdraw the key, turn and return the plug.
6. Red-first running scenarios beside `SeatedScenario` in
   `simulation/test_lock.py`: the pins rise and drop over the cuts as the
   key advances (bank sampled per station against `lifts_for`); the plug
   is blocked with nothing admitted at every partial insertion and with
   the deep and shallow keys; the seated matching key turns; withdrawal
   from a turned plug is blocked at once; the plug stands and the key is
   stopped when the capture bound is removed (the derived reciprocal,
   proved in the project's own numbers); a driver pin bound to a lift
   beyond the spring's limit is refused untimed by name.
7. `simulation/contact.py` becomes the reference the laws are pinned
   against; `LockState` and `web/mechanism.mjs` retire, the browser
   acceptance following the viewer cycle.

**Viewer.** One cycle after this one, in `solid-node-viewer`, replaying
the regenerated corpus.

## Open Questions

- Whether the corpus's second new feature should be detected as "a stop
  whose coordinate did not move" or as "a stop whose blocked inputs
  include one that does not reach the coordinate" — the former is
  simpler and is what the generator will use; both describe the lock's
  capture.
- Whether a `Bound` should be admitted on an `Orbit`. Nothing forbids
  it; no sighting needs it; the joints spec's range wording covers it.
- Whether the enumeration's close should undo the refused pose. It
  mirrors the existing bind-time refusal, which leaves the tree as the
  enumeration left it; a `set_state` caller already holds no promise of
  rollback past a `JointRangeError`.
