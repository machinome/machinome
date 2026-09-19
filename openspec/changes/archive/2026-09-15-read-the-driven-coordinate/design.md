## Context

`proposal.md` states the requirement and the three routes that fail. This
document answers the seven design questions the pilot's requirement note
left open — the spelling, the evaluation point, initialization and
posing, the interaction with stops, direction, several wheels from one
input, and what is refused — and records the alternatives rejected for
each, with the measurement that rejected them.

The ground it stands on is unchanged and is not re-argued here:

- **ADR-105** — the run owns every driver and joint coordinate, binds them
  through `set_state`, and inspecting a model advances nothing.
- **ADR-106** — a law is compiled ONCE, in the direction the rest render
  solved it, and contributes `f(end) − f(start)` over a tick.
- **ADR-107** — a law that jumps contributes the CONTINUOUS part of its
  change: the path is cut at every crossing, a branch is read at each
  piece's midpoint, and the pieces are summed. A jump never moves a part.
- **ADR-108/109/113** — a declared range is a physical stop that stops what
  pushes, and the stopped coordinate is committed AT its bound EXACTLY; a
  bound may be an expression over the coordinate's own value, evaluated
  once per tick; a bound may read other coordinates, and is then sampled
  along the stretch.
- **ADR-110/111** — Python and the browser execute one published program,
  and a conformance corpus is the contract between them.
- **ADR-057** — a producer emits the LOWEST version its content needs.

Three facts about the code as it stands are load-bearing below and were
measured on this worktree rather than read (`evidence.md`):

1. With `_refuse_shared_coordinate` removed, a self-read relation whose
   driven coordinate carries an author's rest default is refused
   `DoublyBound` at the rest render, and one with no rest default is
   refused `UnreachedCoordinate`. Neither is an implementation.
2. With the rest render also made to leave such a relation alone, the
   compile is refused by `_ordered`: *"the relations … form a cycle the
   run cannot order"*.
3. With the Kahn ordering also patched, the program compiles, its listing
   names the read, its skeleton is `(ring * $j1)` and both jump levels are
   affine — and the tick is silently wrong, because the self-read source's
   increment is zero and the gate is therefore frozen for the whole tick.

## Goals / Non-Goals

**Goals**

- One relation can state a law that reads the coordinate it drives, and
  the run integrates it correctly at any `dt`.
- The five requirement-note behaviours (retained clearing from any digit,
  no repeat over an already-cleared wheel, partial release and resume,
  both directions, several wheels from one input) follow from the run, not
  from project state.
- Nothing about a law with no self-read changes: not its meaning, not its
  code path, not its cost, not its published document.
- What the reading cannot support is refused by relation identity, at
  construction, as ADR-106 and ADR-107 refuse.

**Non-Goals** — as `proposal.md` lists them: viewer execution, the Curta's
own migration, a continuous read, a new declaration, `a.drives(a)`, a
driven GROUP with a self-read, and ADR-113's net-over-the-stretch pushing
test.

## Decisions

### 1. Spelling: the coordinate named on both sides IS the read

**Decision.** A coordinate that appears both in a relation's SOURCE group
and among its DRIVEN ends is a READ of that driven end. The law is handed
its owner exactly as it is handed any source's owner (ADR-100's shaped
argument rule, unchanged), so the Curta's law is written

```python
def missing_tooth(sources, target):
    def law(ring, wheel):
        shifted = wheel + GAP          # GAP: the clearance, half the band
        return ring * (shifted - 360.0 * floor(shifted / 360.0) >= 2 * GAP)
    return law

(ring & wheel.rotation).drives(wheel.rotation, law=missing_tooth)
```

`floor` is `solid_node.math.floor`; the framework's symbolic vocabulary
has no `modulo`, and the gate's own shape is stated in §4.

`_refuse_shared_coordinate` (`motion/couplings.py`) stops refusing and
starts recognizing: it records, on the relation, the index of the source
that names its one driven end — and refuses where the driven end is a
group (below).

Recognition is scoped exactly as the refusal is today — **only when either
end names several** — because that is the check's own scope and because a
relation naming several ends is FORWARD ONLY (ADR-100), which is what a
self-read must be.

**Alternatives rejected.**

- `drives(..., reads=(...))`, mirroring `Bound(expression, reads=)`.
  Rejected on three counts. A `Bound`'s expression has no other way to
  name a second coordinate — ADR-113 says so in its own first line — while
  a relation's sources already have one, so this adds a second naming
  grammar for a thing the first grammar already says. It needs a second
  argument convention for the law (before the sources? after? boxed?),
  where the group needs none. And it reads as a RELATION-level property,
  where the gate belongs to a TERM of a multi-source law: the Curta's dial
  is driven by the transmission AND by the rack, and only the rack term is
  gated.
- A new verb (`wheel.turn.driven_by(...)`, `retains=`). Rejected for
  ADR-089's own reason: one verb states mechanical direction, and a second
  vocabulary for one sentence is what that decision refused.
- Widening to the one-to-one `a.drives(a)`. Out of scope, as ADR-100 left
  it: it has no second source to carry slope, so the skeleton test of §2
  would refuse every such law anyway, and the shape is already refused as
  `UnreachedCoordinate`.

**The cost of the choice, stated.** A reader cannot tell from the sentence
alone that one end is read rather than driven. Three places name it: the
program's `described()` listing (and therefore the identity — measured, it
already prints `['ring', 'wheel.rotation'] -> ['wheel.rotation']`), the
published edge's `needs ∩ gives`, and the documentation.

**The shapes, stated.**

- **ONE driven end.** A self-read relation drives exactly one coordinate.
  That is the shape the Curta needs — the dial driven by the transmission
  and the rack, the carry lever set by the dial and reset by the crank —
  and it is the only shape this cycle admits.
- **A driven GROUP with a self-read is REFUSED** at class definition,
  naming the relation and the coordinate, and saying that a relation that
  reads its own driven end drives ONE coordinate. This holds whether the
  member reads ITSELF or a SIBLING driven end of the same group. The
  reason is `Edge.increments`: it walks ONE plan per driven end, and a
  member that reads a sibling needs that sibling's path, which the
  sibling's own walk is cutting at its own crossings — a JOINT walk over
  several plans that nothing here defines and no mechanism in the
  campaign has asked for. The rest rule is undefined for such a group
  too: a group mixing a self-read end with a plain driven end would leave
  the plain end unbound at rest. Recorded as a follow-up in
  `proposal.md`'s non-goals.
- **A BROADCAST (`.repeat()`) with a self-read** is admitted: the source
  group's repeated member is the very broadcast the relation drives, and
  it resolves PER COPY exactly as the driven end does, so each copy reads
  ITSELF and each copy is its own record with ONE driven end. Measured
  implementable at the record level (`evidence.md` §6,
  `spikes/broadcast.py`): eleven lines over `BroadcastRef.resolve_all` and
  the ref key the two sides already share, one record per copy, the same
  slot on both sides, no two copies sharing one. A group mixing a
  broadcast with a plain end is already refused (ADR-100), unchanged.
- A read of a driven end by a relation that does NOT drive it. That is an
  ordinary source and has always been legal; nothing about it changes.
- A coordinate named twice in one group is already refused (ADR-100);
  unchanged.

### 2. The read is a SWITCH, checked on the skeleton

**Decision.** A law may read its own driven coordinate only through a node
whose output is piecewise constant in it. The test is structural and free:
the jump plan already builds a SKELETON — the law with every jump node
replaced by a branch placeholder — and the law is admitted exactly when
the driven coordinate's qualified id is NOT among that skeleton's free
names. A law with no jump node at all has the graph as its skeleton, so a
bare continuous read is refused by the same line.

This is exactly right, and `%` shows why: `_skeleton` rewrites `a % b` to
`a − q·b`, which still names `a`, so a law gated by a bare remainder is
refused — as it should be, since a remainder is continuous in its dividend
between surfaces and the relation would be an ODE.

**Why refuse rather than integrate.** On a piece the branches are fixed,
so the skeleton is a function of the moving sources alone and the driven
coordinate's own path `own(t) = own_left + skeleton(t) − skeleton(left)`
is an ordinary evaluation. If the skeleton still reads `own`, that
equation is implicit and its solution is an integration ADR-106's
two-evaluation reading does not define. Refusing by relation identity is
what ADR-106 and ADR-107 do with everything the reading cannot say.

**Alternative rejected.** Solving the implicit equation per piece (a
fixed-point iteration or a small ODE step). Rejected: it introduces a
convergence tolerance — a fourth tolerance — and a per-tick iteration
count, into a design whose whole claim is three tolerances and no epsilon
anybody has to justify.

### 3. When the read is evaluated, and how a crossing is located

A jump node **DEPENDS on the driven coordinate** when that coordinate's
qualified id is among the free names of the node's ARGUMENT SUBTREE IN THE
ORIGINAL GRAPH. Computed on the plan, where every inner jump is already a
placeholder, that is: the node's level quantity names the driven id, OR it
names the placeholder of a node that depends on it — the two readings are
the same set, because a placeholder stands for exactly the subtree it
replaced. Dependence is therefore UPWARD CLOSED along the nesting: a node
whose argument contains a dependent node is itself dependent, so the
INDEPENDENT nodes are closed under nesting, and their level quantities are
exactly the level quantities ADR-107 already reads.

**Decision — the partition is built in TWO LAYERS.**

Measured on a law carrying both kinds (`evidence.md` §8): a station
window over the ring sorts INDEPENDENT, the band gate over the wheel
DEPENDENT, and the comparison whose argument is only a placeholder sorts
with the node that placeholder stands for.

**Layer 1, the source partition.** ADR-107's `_partition`, UNCHANGED, over
the INDEPENDENT nodes alone — a plan whose jumps are that subset, which is
well formed exactly because dependence is upward closed: their crossings are found over the whole
tick, their branches are read at the MIDPOINTS of that partition, and both
are valid for the reason ADR-107 gives, since those levels do not depend
on the walk. The implementation reuses `_partition` rather than rewriting
it.

**Layer 2, the walk, INSIDE each piece of layer 1.** Within one such piece
the independent branches are fixed, and the dependent nodes are walked:

1. At the walk's current left end `t` the driven coordinate holds a known
   value `own_left` — the tick's committed value at the start, and what
   the pieces so far produced after each cut.
2. Every DEPENDENT node's branch is read, in the graph's postorder, with
   **the driven coordinate at `own_left` and every other source at
   `t` — the piece's LEFT END, not its midpoint.** A midpoint reading
   would be wrong for a MIXED level such as `ring − wheel`, which can
   cross inside the piece by the sources' motion alone: the branch read
   past that crossing is the far-side branch, and the piece's own left
   half would be integrated under it. A node whose level sits EXACTLY on a
   surface at the left end takes the branch the OPERATOR gives, and is
   flipped by rule (c) below if that branch is not the one the piece
   needs.
3. With every branch fixed the skeleton gives the driven coordinate's own
   path on the piece, `own(s) = own_left + skeleton(s) − skeleton(t)`,
   which by §2 is an ordinary evaluation.
4. Each dependent node's level is followed along `s` — through `own(s)`
   and through the sources — and the walk is CUT at the FIRST surface any
   of them reaches strictly inside the piece. Where that level is AFFINE
   along the path — the existing `_affine_in_sources` test on the level
   AND on the skeleton, which is what makes `own(s)` affine in `s` — the
   crossing is SOLVED; otherwise the piece is sampled at `_SUBDIVISIONS`
   and the bracket bisected to `_CROSSING_TOLERANCE`. Three tolerances, no
   fourth.
5. The piece's contribution is the substituted skeleton's change over it;
   the driven coordinate is placed by §4's landing rule; the cut is
   recorded as a `Crossing`; and the next piece is decided from `t = s*`
   and the landing, by 2 again.

Steps 1–5 repeat until the layer-1 piece is exhausted or `_MAX_CROSSINGS`
cuts have been taken, which is the existing refusal and needs no new one.

**(c) A level exactly ON a surface at a piece's left end.** This is not an
edge case: it happens at EVERY cut the walk takes, and at a tick's start
after a stop, a restore, or a rest default that lands on a digit boundary.
The old draft said the boundary operator settles it; that is wrong for the
case that matters. A wheel standing exactly at the surface with a `>=`
gate, swept in the direction that carries the level to the `<` side, reads
ENGAGED at the left end, moves, and `_surfaces(..., inclusive=False)`
finds NO crossing — because the level LEAVES the surface rather than
reaching it — so the piece is integrated engaged and the wheel drives
straight through the gap. The rule is therefore:

> At the piece's left end, a node whose level sits exactly on a surface
> takes the branch the OPERATOR gives. The level is then followed under
> the tentative branches over the piece. If it LEAVES the surface into the
> OTHER branch's region, that node is FLIPPED to the other branch at
> `left` — a zero-length piece — and every branch is decided again. If the
> flipped branch carries the level back across as well, the tick is
> REFUSED as chattering, naming the relation, the coordinate and the
> primitive, and commits nothing: a sliding mode is not a mechanism.

"Leaves the surface into the other branch's region" is read off the level
at the FIRST point of the piece at which it differs from the surface — the
piece's right end for a level affine along the path, and otherwise the
first of the `_SUBDIVISIONS` samples that differs. No tolerance is
introduced: the test is an inequality between two evaluated floats.

**(d) A crossing found within `_CROSSING_TOLERANCE` of a piece's left
end.** `_merged`'s folding of two near cuts into one, and
`_deduplicated`'s, apply to LAYER 1 — the source partition — only. In
layer 2 such a crossing is NOT folded into the left cut, because folding
it would integrate the piece under the near-side branch and drive the
wheel through the gap; it is case (c), and it is answered by flipping the
node at `left`.

**(e) After a cut.** The crossing node holds its FAR-SIDE branch by
construction, because §4 places the coordinate at a value where it reads
that branch; every other dependent node is re-read at the landing by 2 and
(c). Two dependent nodes crossing at one fraction are ONE cut, and each
takes its far side.

**Why the retained value and not the midpoint.** ADR-107 chose the
midpoint because it is a point genuinely inside the piece, so no epsilon
and no direction test is needed. That argument still holds for every
independent node, and those keep the rule in layer 1. For a dependent node
there is no midpoint to read: the coordinate's value at the midpoint is a
consequence of the branch being asked for. The retained value at the
piece's left end is the one value that is known without assuming the
answer, and it is the mechanism's own reading — a rack meets the tooth the
wheel is standing on.

**Why the first surface only, per piece.** ADR-107 solves ALL surfaces
between a piece's endpoints at once, which is what makes three tooth
windows in one tick three throws. That is sound only while the path is
known for the whole piece. Under a self-read the path is known only until
the branch changes, so the walk takes the first crossing and re-decides.
Three tooth windows in one tick still give three throws — as three
successive pieces rather than three surfaces of one solve — and the corpus
scenario proves it.

**Chattering.** Two branches that each carry the level back across the
same surface are refused by (c) where they meet at a left end, and bounded
by `_MAX_CROSSINGS` where they do not: a path cut more than that many
times refuses the tick naming the relation, the coordinate, the primitive
and the count, and commits nothing.

### 4. What the driven coordinate is committed at — and the width obligation

**Decision. After a self-read cut the driven coordinate is committed AT
THE FAR SIDE OF THE SURFACE, at the nearest representable value.** That is
ADR-108's "committed AT its bound exactly" transposed to a surface that is
not stated in the coordinate's own units: the segment arithmetic finds the
landing, and the landing is then WALKED to the adjacent float — no
tolerance anywhere.

> When a piece is cut at `t*` by a node that depends on the driven
> coordinate, and the piece moved that coordinate, the coordinate is
> placed at the representable value NEAREST the surface among those at
> which the crossing node's level — evaluated with the driven coordinate
> at that value and every other source at `t*` — reads the branch on the
> side the level was moving TOWARD. That value is what the next piece
> starts from, and what the tick COMMITS.

**How the walk is done.** The segment's own arithmetic gives `own*`
(`own_left + skeleton(t*) − skeleton(t)`). From it, two floats are
bracketed — one reading the branch the piece was integrated under, one
reading anything else — by stepping out from `own*` in the direction of
travel with the stride doubling from one ulp; the bracket is then bisected
in FLOAT SPACE (the midpoint of the two values' ordinal representations)
until the two are adjacent, and the far one is taken. For a crossing that
was SOLVED the landing is a couple of ulps out and the bracket is found in
a handful of steps; for one that was SEARCHED it is up to
`_CROSSING_TOLERANCE` of the piece's travel out, and the doubling stride
absorbs that too. Measured: 4.3 evaluations per cut on average, the segment's
arithmetic having already landed PAST the surface in 58 % of cuts, so the
bracket is sought in both directions (`evidence.md` §7). Where the piece did NOT move the coordinate — a level
that crossed by the sources' motion while the gate held — there is nothing
to walk: the coordinate stands where it stood and the next piece's branch
is decided by §3's rule (c).

**The run commits that float.** The increments protocol is extended so an
edge can report, beside its increment, the ABSOLUTE value a driven end
whose walk took at least one cut holds at the tick's end — the last
landing, advanced by whatever the pieces after it contributed, which for
a wheel that came to rest in its gap is the landing itself;
`Run.integrate` applies it
exactly where it already applies a stop's bound (`committed[identifier] =
bound`). Committing `value + delta` instead is not enough on its own:
`x + (y − x) != y` for about six pairs of floats in a hundred, so an exact
landing inside the plan would still be a ulp out in the bank the next tick
starts from. The landing and the increment differ by at most the
localization's own residue, which is inside the run's agreement window
`1e-9 · max(1, |a|, |b|)`, so nothing downstream of the edge shifts.

**Why not the rules the first draft measured.** `spikes/snap.py` compared
the segment's arithmetic against "the level solved for the coordinate" and
rejected snapping on the second's error. That comparison does not decide
anything: its rule B takes a slope from two evaluations one unit apart and
then divides by it, which loses about a thousand ulps to cancellation, and
it says nothing about a landing done properly. The rule the first draft
adopted instead — "what the segment's arithmetic gives" — is the one that
fails: measured through `Sim` over the real classes, it leaves the gate
ENGAGED after the cut in 6.3 % of crossings and refuses another 12.7 % as
`TooManyCrossings`, because the walk cuts at the same surface again and
again (`evidence.md` §7, 20 000 trials). And the remedy that draft offered for the
engaged case — "cuts once more within the same tick" — is a crossing
INSIDE `_CROSSING_TOLERANCE` of the piece's left end, which §3's rule (d)
now says must never be folded away and which the old text folded into the
left cut. **With the far-side landing: 200 000 randomized crossings, zero
re-engagements, zero refusals, the landing at most 2 ulps from the band's
edge and one float from the near side, and the wheel bit-identical three
ticks later while the ring runs on.**

**The obligation this puts on the model, stated rather than hidden.** A
self-read gate's DISENGAGED state must have WIDTH, and the width is the
mechanism's own clearance. The physical fact is a gap — the Curta's
clearing gear has "eight remaining tooth tips … the two missing positions
leave a gap" — and the disengaged set of a missing tooth is a SYMMETRIC
BAND about the zero, entered from EITHER direction, so the dial stops at
the band's edge from whichever side it arrives:

```python
shifted = wheel + GAP
engaged = shifted - 360.0 * floor(shifted / 360.0) >= 2 * GAP
```

Disengaged for `wheel mod 360 ∈ [−GAP, GAP)`, where `GAP > 0` is the
stated clearance. With the far-side landing this is robust from both sides
at ANY positive `GAP`: swept forward the wheel lands at `360·q − GAP`,
where the comparison's level reads `−2·GAP`; swept backward it lands at
`360·q + GAP`, a ulp below the surface. Both are measured over the
randomized sweep, and both hold across ticks. **The obligation is
therefore "state the gap's WIDTH", not "leave a whole tooth disengaged".**
A gate written as `modulo(wheel, 360) >= 36` — disengaged over the whole
first tooth — would be wrong for the mechanism: swept backward from digit
1 the real rack turns the dial one tooth to zero and only then meets the
gap, while that gate holds it at 36 and calls a dial standing at 10° free.

**A knife-edge gate, stated plainly.** With `wheel % 360 > 0` the
disengaged set is a single point, and a single point is not a gap. Swept
forward the wheel does hold — the far-side float nearest `own / 360 = 1`
is exactly `360.0`, where `> 0` reads false — but swept so that it arrives
from ABOVE, the far side of the surface is the ENGAGED region and the
wheel runs on. That is not a numerical accident but the gate's own
definition, and the framework cannot tell a knife edge from a band
structurally: the distinction is numeric, not syntactic. So it is
documented in `docs/scenarios.rst`, pinned by a test that asserts only
what the framework promises, and recorded as an open question — never as a
requirement scenario, because a requirement does not promise a failure.

### 5. Initialization, rest and ordinary posing

**Decision.** Under a running root a self-read relation **binds nothing at
rest**. `_step_relation` records it solved `'forward'` — the direction the
program compiles it in, always, since ADR-100 makes a relation of several
ends forward-only — and applies no law. The driven coordinate's rest value
is the author's own, written as the rest-default guard the catalogue
already writes and the couplings spec already blesses:

```python
def simulate(self):
    if self.rotation.value is None:
        self.rotation = 108.0
```

Measured with the rest rule patched in: the untimed rest pose comes out at
`108.0`, nothing is refused, and the "read of a coordinate a relation
binds" rule is satisfied because the AUTHOR bound it (`evidence.md` §2).
With no such guard the coordinate is unbound when construction reads the
bank, and the run refuses by name with the message it already has — *"the
run needs a rest value for every joint coordinate"*.

**Alternative rejected: a rest value declared on the joint**
(`Revolute(..., rest=108)`). Rejected: ADR-105's "the author declares no
state" is the guardrail the whole running mode rests on, and a rest
declaration is state under another name. The guard is one line, is already
the documented idiom, and poses the model untimed as well.

**Under a non-running root.** The relation is left unsolved and `_refuse`
names it at the close of the enumeration: a relation that reads its own
driven end states INCREMENTS, which only a run integrates; declare
`time = Time.running()` on the root, or state the law over other sources.
Refusing beats standing inert, which would silently leave a coordinate at
its rest default in a model that renders and publishes.

**Ordinary posing under a running root is untouched.** `set_state` with a
snapshot binds the bank, the enumeration recomputes ports and derived
coordinates from it, and the self-read relation moves nothing — ADR-105's
"inspecting a model advances nothing", preserved literally, because the
relation is applied only by the tick's propagation.

**Snapshot, restore, reset, recording.** Unchanged. A landing is an
ordinary bank value: `snapshot` copies the float and `restore` puts the
same float back, so a wheel resting in its gap reads disengaged on the
tick after a restore exactly as it did before. The identity changes with
the read for free: `Program.described()` prints the law's graph text,
which names the driven id (measured). A snapshot taken against a program
without the read is refused by one with it.

**Transactional refusal.** Unchanged: the segment loop already stages the
bank, the admitted travel and the three rings, and a refusal anywhere
commits nothing. The walk raises the same `TooManyCrossings` and
`UnsupportedLaw` the whole-partition partition does, from inside
`Edge.increments`, so it lands in the same handler — and a landing
reported by a segment that is later refused is discarded with everything
else the segment staged.

### 6. Edges, ordering and the program

**Decision.** The self-read id is a `needs` of the edge that is also one of
its `gives`. `_ordered` (Kahn) ignores a need an edge itself gives, and
`_reaching_inputs` needs no change at all — it already reads `found[key]`
before updating it in one topological pass, so a self-need contributes the
empty set, which is correct: what reaches the wheel reaches it through the
ring.

**Alternative rejected: a separate `Edge.reads` tuple** (the shape the
`Constraint` precedent suggests). Rejected because the published contract
says, in the export spec's own words, that "the free names each of the
entry's expressions reads SHALL be exactly the ids in `needs`". A separate
list makes that sentence false and forces a new document key; keeping the
id in `needs` keeps it true and makes `needs ∩ gives` the self-read with
nothing published that was not published before. `Constraint` carries
`reads` separately because a bound is not an edge and has no `gives`.

`Edge` carries one new derived field — the set of `gives` indices whose
graph reads their own id — so `increments` can take ADR-107's unchanged
path in one test when there is no self-read.

**The increments protocol gains a LANDING.** `Edge.increments` returns
what each driven end MOVES BY, and `Run._pass` sums those into `deltas`,
which `Run.integrate` adds to the bank. A self-read edge additionally
REPORTS, for a driven end whose walk took at least one cut, the ABSOLUTE
value that end holds at the tick's end (§4). `_pass` carries the report
the way it already carries `crossings` — a caller-owned collection, fresh
per propagation, so a refused segment's report is dropped with it — and
`integrate` applies it to `committed` before `_reached` is asked, in the
one place where it already writes an absolute value for a stop. Where both
apply to one coordinate in one segment, the STOP wins: a physical bound is
a bound of the coordinate itself.

### 7. Stops and constraints in the same tick

**Decision.** A self-read crossing is NOT a stop. It stops no input,
retires no command, and appends to `sim.crossings`, not `sim.stops`. The
distinction is ADR-108's own: a stop is a bound of a coordinate, which
stops motion; a crossing is a jump surface of a law, which moves nothing.

Everything else composes without a new rule:

- **A declared range on the driven coordinate** still stops it. `_locate`
  reaches the edge through `edge.cuts(...)`, which returns the same
  two-layer partition; the affine-skeleton case is `_piecewise`,
  unchanged, and the coordinate is committed AT its bound exactly (ADR-108
  applies, because there the bound IS a number in the coordinate's units,
  and it is applied after any landing the same segment reported).
- **A stop earlier in the stretch than the gate's crossing** cuts the
  stretch at `t*`; the remaining segment re-integrates from the committed
  state, and the gate's crossing is located there and recorded at its
  fraction OF THE TICK — the rule the existing "A stop and a jump crossing
  in one tick" scenario already states.
- **A gate crossing earlier than a stop** simply happens inside the
  stretch, and the stop is then located against the coordinate's post-gate
  path, because `_locate` truncates the same partition.
- **`_event` ties** are unchanged: a self-read crossing is never in
  `reached`, so it is never an event.
- **A constraint (`Bound` with reads) whose read is a self-read driven
  coordinate** works unchanged: the sub-program's edges include the
  self-read edge, and `Edge.increments` over a scaled admission takes the
  same partition.

### 8. Direction, entry and exit

Both permitted sweep directions are the same code. The level quantity's
surfaces are crossed downward exactly as they are crossed upward — the
existing `_surfaces` handles a descending level — and the branch is read
from the retained value either way. With the BAND gate of §4 the wheel
stops at the band's edge it arrives at: the lower edge sweeping forward,
the upper edge sweeping backward. Reversal INSIDE the band holds the wheel
in both directions, which is the mechanism's own answer — a missing tooth
grips in neither direction. Reversal while ENGAGED backs the wheel up and
re-crosses the surface downward, re-engaging. Entry and exit of the rack's
own station window is a SOURCE-side jump in the same law and is ADR-107's
layer-1 partition, unchanged.

### 9. Several wheels from one input

Each wheel is its own relation (or one broadcast over a `.repeat()`), each
with its own self-read and its own walk. They are independent edges: one
wheel's disengagement cuts only its own path. An unswept register's wheels
are gated by a station term the ring never reaches, so their increment is
zero and they are untouched. A real obstruction is a declared range on the
RING, which stops as its own physical stop and blocks the inputs that push
the ring — ADR-108, unchanged.

### 10. Publication

**Decision.** A program carrying at least one self-read edge makes the
document **version 6**; a program with none publishes byte-identically at
5. ADR-057's rule decides it: a version 5 consumer reads a law edge as
`f(end) − f(start)` over `needs`, which with the driven id at both ends is
not merely imprecise but a different mechanism, applied silently.

Nothing else about the document changes. The self-read is `needs ∩ gives`;
the jump entries already publish each level's expression, so a consumer
derives "this node depends on the driven coordinate" from that
expression's free names; `limits`, `spans`, `sources` and `intermediates`
are as they were. The LANDING is behaviour, not a document key: a
consumer that lands a ulp short re-engages the gate and diverges from the
fixture's bank on the NEXT tick, far outside the corpus's agreement
window, which is exactly how the corpus pins it. The corpus gains machines
that exercise a self-read gate, a self-read crossing in the same tick as a
stop, and a self-read under `.repeat()`, and the generator refuses a
corpus without one — the contract the viewer's own cycle is held to.

### 11. Performance

A law with no self-read pays ONE boolean test per driven end per tick
(`Edge.increments` branches on the precomputed index set) and is otherwise
byte-for-byte ADR-107's path: same partition, same midpoint branches, same
evaluation count. `Train` is the pin.

A self-read law pays, per PIECE of the walk, one extra skeleton evaluation
to place `own(s)`'s endpoints, and it forfeits ADR-107's
solve-all-surfaces-at-once on the layer-2 pieces. Per CUT it pays the
far-side walk: 4.3 level evaluations on average over the randomized sweep,
bounded by the doubling stride and the 64-round float bisection behind it.
A tick in which the gate does not move — the wheel standing in its band,
or the rack out of its station window — takes the zero-delta early return
and evaluates nothing at all.

**The Curta's own shape pays the search.** Its rack-station term is a
clamp window over the ring (`clamp01`, which is `min`/`max`), and
`_affine_in_sources` calls a CALL non-affine — so the skeleton is not
affine, `own(s)` is not affine in `s`, and every self-read crossing of the
migrated model falls to the `_SUBDIVISIONS = 64` sampled search rather
than to a solve. That is correct but costs 64 level evaluations per piece
plus the bisection, and the implementation records the price: task 6.3
times the `CurtaInterface` fixture in ticks per second and evaluations per
tick, so the migration knows what it is paying. A cheap exact path for a
kinked-but-piecewise-affine skeleton (`clamp01` is two kinks, and its
pieces are affine) would remove it — a follow-up, not scope.

### 12. What the Curta must do to migrate (project work, named here)

- Every clearing dial declares its `rotation` rest default in its own
  `simulate()` guard, as the reduced fixture does.
- `cycle.cleared_position` — which takes a starting position and one
  normalized sweep — is replaced, for the running model, by a law over
  `(ring & dial.rotation)`: a rack-station term continuous in the ring
  (the measured `start` phases 9.75°/10.5° and pitches
  `degrees(3.75/52)` / `degrees(3.75/49.55)` per tooth, the stations
  `(130 if counter else 0) − 20·place`) multiplied by an engagement gate
  over the dial's own retained angle, written as §4's band with the
  MEASURED clearance of the clearing gear as its half-width.
- The pose form stays where it is used as pose.

## Risks / Trade-offs

- **A knife-edge gate is silently wrong in one direction** → documented in
  `docs/scenarios.rst`, tested for what the framework actually promises,
  and recorded as an open question. The framework cannot distinguish it
  structurally, and refusing every gate whose disengaged interval is
  narrow would need a number nobody can justify.
- **The walk forfeits solving every surface of one piece at once** →
  correctness is unaffected (it finds each surface as its own piece), and
  the cost is one extra evaluation per tooth plus the landing walk.
  Measured in the implementation's evidence against `Train` and the
  clearing fixture.
- **The landing makes the bank's value depend on a float-space walk** →
  bounded, deterministic and reproducible (no tolerance, no iteration
  count that depends on magnitude), and pinned in the corpus, which is
  what the second runtime is held to.
- **A version bump breaks every current consumer for a self-read
  document** → that is ADR-057's rule working: the alternative is a
  consumer moving a part wrongly in silence. The viewer's cycle is held to
  the regenerated corpus, and `solid build`/`develop`/`export` warn once
  naming the version written and the versions the installed viewer
  renders, exactly as they already do for 5.
- **A tick that crosses a gate many times costs many pieces** →
  `_MAX_CROSSINGS` refuses it naming the relation, the coordinate, the
  primitive and the count, which is ADR-107's existing bound.
- **A self-read law whose skeleton is not affine falls to the search** →
  correct but slower, exactly as ADR-107 already trades for a non-affine
  level quantity, and the Curta's own shape is that case (§11).
- **A driven GROUP with a self-read is refused, and a mechanism may want
  one** → the Curta does not, and the joint walk it needs is recorded as a
  follow-up rather than guessed at here.

## Open Questions

1. **Should a gate whose disengaged set is a single point be refused?** It
   cannot be told structurally from a gate with width — the distinction is
   numeric. Left documented and tested rather than refused. Filed for
   `workflow/warts.md` if the reviewer agrees.
2. **`a.drives(a)` one-to-one** still deadlocks into
   `UnreachedCoordinate` rather than naming itself. ADR-100 declined to
   widen the refusal; this cycle does not either.
3. **ADR-113's pushing test is net over the stretch, not local at `t*`.**
   A self-read gate makes that limit easier to reach — an input that
   pushes a coordinate over the first half of a stretch and is disengaged
   over the second is counted as pushing. Unchanged here, recorded.
4. **A joint walk for a driven group with a self-read** (§1). Refused in
   this cycle; the shape that would need it — several driven ends whose
   laws read each other — has no mechanism behind it yet.

## Implementation notes (2026-09-15)

Written after the adversarial review of the implementation, and recording
only what implementation found. Nothing above this heading is revised:
the decisions stand as ratified, and each note below is a correction to a
piece of PROSE or an account of a defect in the code that realized them.

**§10's "a self-read under `.repeat()`" is unattainable, and the
requirement it was evidence for is met another way.** A repeated child's
JOINT coordinate has no qualified id the run can bank it under —
`DriverIdError` on the base tree, before any self-read is in sight — so no
running corpus machine can carry one. That is a pre-existing limitation,
recorded in `workflow/warts.md` under the fix-warts campaign, and not
this cycle's to lift. The couplings resolution rule §10 leaned on is
implemented and tested directly (`SelfReadTest::
test_each_copy_of_a_broadcast_reads_itself`: four records, each copy
reading its own slot), and the export spec's generator list never named
`.repeat()`, so the ratified contract is met. Only that clause of §10's
prose is not, and `evidence.md` §17 carries the measurement.

**§4's "a knife-edge gate runs on when arriving from above" did not
survive implementation.** It does not run on in any case probed. The
reason is the landing's own shape rather than luck with the arithmetic:
`_land` walks the crossed nodes in the graph's postorder and judges each
with the OTHER nodes at the piece's NEAR-SIDE branches, so where a
`floor` surface and a comparison surface are coincident in the
coordinate — which is what a knife edge IS — the floor's far-side walk
lands the coordinate exactly ON the surface, and there the comparison's
operator reads disengaged. The gate holds from both sides. The width
obligation stands as documentation, because it is a statement about the
MODEL and not about this arithmetic: a single float is not a gap, and
nothing guarantees another model's numbers land on it rather than past
it. `KnifeEdgeTest` asserts only what holds — the disengaged set is ONE
float, and the dial holds where the far side of the surface is
disengaged — and `docs/scenarios.rst` promises neither the failure nor
the hold. Open question 1 stands unchanged.

**The searched walk reported a PHANTOM crossing and jumped a whole
surface (blocking; closed).** `_Walk._searched` asked
`_surfaces(previous, level, inclusive=True)` over each sub-interval and
took `found[0]`. After a cut the far-side landing very often puts a
`floor` node's level EXACTLY on the integer it was landed at, so at the
next sub-interval `previous` IS a surface, the inclusive search returns
it, and `_bisect` starts from a `below` of zero — never negative, so
every round takes the `else` arm and the bracket collapses onto the
sub-interval's RIGHT end. That was returned as a crossing strictly
inside the piece, and `_land`, walking outward from a value already on
the near side, carried the coordinate to the NEXT surface: a whole unit
per phantom, a thousand of them, and then a refusal. It was invisible on
a gate that HOLDS the part after landing (there `level == previous` for
the whole piece and the sub-interval is skipped), and fatal on any gate
whose read changes the RATE — a two-speed mechanism, a lever that keeps
moving after it trips. The rule now, with no tolerance in it: a surface
EQUAL to the level at a sub-interval's LEFT sample is not a crossing of
that sub-interval (at the piece's left end it is rule (c)'s, and at an
interior sample it was reached in the sub-interval before and reported
there); the surface the path reaches first is the one NEAREST that left
sample, not the lowest, because `_surfaces` counts upward and a
DESCENDING level crosses them in the other order; and a right sample
EXACTLY on a surface is the crossing at that sample, as ADR-107's own
`_searched` already treats it. `_bisect` is then bracketing a `below`
that can no longer be zero, which is what its sign test needs.

**The same gate's rule (c) flipped a node to the wrong branch (closed
with it).** `_decide` read the branch to flip to off the level at the
probe sample — "the first of the `_SUBDIVISIONS` samples that differs",
which §3 states as the test for whether the level LEAVES the surface. It
is the right test for that question and the wrong value to take a branch
from: for `floor` and `ceil` there are many other branches, and a sample
a whole tooth away names one the piece never enters. On the two-speed
gate the flip chose a branch that changed the rate, the next probe
wanted a third, and the tick was refused as a sliding mode. The branch
a flipped node takes is now the branch of the region IMMEDIATELY on the
side the level departs to — `_branch_of(nextafter(surface, probe))` —
which is unchanged for a comparison or `sign`, whose two regions are the
only ones there are. §3's rule (c) is unaltered; this is how "the OTHER
branch's region" is read for a primitive with more than two.

**A genuine crossing a hair inside a piece's left end was dropped
(blocking; closed).** `_searched` returned a crossing only
`if where > t + _CROSSING_TOLERANCE`, on the reasoning that rule (c) had
already answered anything nearer by flipping. Rule (c) flips a level
EXACTLY on a surface, and float equality is the whole of that test: a
coordinate a hair SHORT of one — where a rest default, a restore or a
bound a stop committed can leave it — is not on it, is not flipped, and
its crossing at `t*` of the order of `1e-16` was thrown away, so the
piece integrated under the near-side branch and the part drove through
its gap. That is exactly what rule (d) forbids, and the solved path
never did it, because `_crossing` returns every crossing strictly inside
the piece. With the exclusion above in place that filter has no job
left: every crossing with `where > t` is returned. A crossing that
bisects to exactly `t` is a zero-length piece whose landing moves the
coordinate to the far side and lets the walk re-decide, bounded by
`_MAX_CROSSINGS` like everything else.

**An unlanded landing is now loud (closed).** `_Walk._far_side` returned
the segment's own `own_star` unchanged when no bracket was found within
`_WALK_STRIDES` doublings — committing, in silence, the one value §4
says is never committed. It raises `LandingInvariantError` instead,
naming the relation, the coordinate and the primitive, and the run
refuses the tick with it as it refuses a broken stop invariant. No test
can reach it by construction: a cut exists because the level crossed the
surface, so the branch differs somewhere on either side of it, and 200
doublings of a ulp cover every distance a double expresses. The code
says so where it raises.

**§6's account of the new `Edge` field is not the field the code
carries.** It describes "the set of `gives` indices whose graph reads
their own id". `Edge.retained` is not a set of indices: it is a TUPLE
PARALLEL TO `gives`, holding for each driven end either the two-layer
`_Retained` reading of that end's jump plan or `None`, and it is EMPTY
where no driven end reads itself at all. The parallel shape is what lets
`increments` and `cuts` index it beside `gives` with no lookup, and the
emptiness is what §6's sentence was really about: the one test that keeps
a law with no self-read on ADR-107's unchanged path is `if retained`, not
a membership test on a set. The decision §6 states -- one derived field on
the edge, the id staying in `needs`, nothing new published -- is
unaltered; only its description of the field's shape is corrected here.

**The compile no longer decides for itself WHICH end is read.**
`_relation_edge` originally re-derived the self-read from the resolved
slots (`gives` whose key is also a `needs`), which made two definitions of
one thing: `_self_read_index` recognizes it at class definition by
DECLARATION identity, records it as `Relation.self_read`, and the rest
rule and the non-running refusal both key on that attribute -- and only
that recognition refuses a driven GROUP. The compile now reads
`record.relation.self_read` (an index into the source group, `None` for
every other relation, shared by every copy of a broadcast) and keeps the
slot comparison as a single CONSISTENCY CHECK: where the relation declares
a self-read the resolved source at that index must be the resolved one
driven end, and where it declares none no source may resolve to a driven
slot. A disagreement is a coordinate spelled two ways -- the child
standing for its one joint on one side, the coordinate on the other --
and is refused by relation identity as `UnsupportedLaw`. The check is a
BACKSTOP for the invariant rather than a path a running machine takes: the
class definition sees no self-read in that spelling, so the rest rule does
not apply and the rest render refuses the relation first
(`SelfReadRestTest::test_naming_the_driven_coordinate_two_ways_is_refused`
measures it: `DoublyBound` against the author's own guard).
