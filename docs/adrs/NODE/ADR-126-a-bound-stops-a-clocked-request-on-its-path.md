# ADR-126: A Bound Stops a Clocked Request on Its Path

**Status:** Accepted
**Date:** 2026-09-17
**Amended:** 2026-09-17 by [ADR-128](./ADR-128-a-clocked-root-publishes-its-compiled-machine.md) — every compiled constraint is PUBLISHED (chain, bound, jump plan, per-input shapes, the own-name and the consumer's own subtraction), and the landing walk is CLARIFIED: its first step is sized by the SEGMENT and never by the ulp of a coordinate standing at zero, and a level already at its limit and pushed further admits zero travel off the CROSSING rather than off the walk. The clip, its threshold, its stop report and the end-of-request judgement stand as written.
**Depends on:**
- [ADR-106: One law, two readings](./ADR-106-one-law-two-readings.md) — the symbolic inspection of a law applied to one token per source, through `program.checked_expression`, which is what turns a `law=` relation into a link of a chain
- [ADR-107: A jump is located inside the tick and subtracted](./ADR-107-a-jump-is-located-inside-the-tick-and-subtracted.md) — `JumpPlan`, its surfaces, its `cuts` partition and `_MAX_CROSSINGS`, which partition a jumped constraint level exactly as they partition an event level
- [ADR-108: A range is a physical stop that stops the connected group](./ADR-108-a-range-is-a-physical-stop-that-stops-the-connected-group.md) — the decision this one carries onto a request path: a declared range is a STOP, the stopped thing is committed at its bound and nothing is ever clamped; its `Stop` vocabulary and its separate ring
- [ADR-109: A range bound may be an expression evaluated at the committed state](./ADR-109-a-range-bound-may-be-an-expression-evaluated-at-the-committed-state.md) — the bound read ONCE per quantum from the committed state, with the REQUEST in the tick's place, and jumps in a bound admitted with no plan
- [ADR-113: A bound may read other coordinates](./ADR-113-a-bound-may-read-other-coordinates.md) — the own coordinate committed and the reads taken along the path, the close-of-enumeration judgement, and the rule this decision takes whole: ONE AUTHORITY JUDGES ONE BINDING
- [ADR-121: A law may read the coordinate it drives](./ADR-121-a-law-may-read-the-coordinate-it-drives.md) — `far_side_of`, the one ordinal walk in float space the framework has, used here mirrored onto the SATISFIED side
- [ADR-123: A kink is a cut, and a piecewise-affine quantity is solved](./ADR-123-a-kink-is-a-cut.md) — `_shape_of` and `_KinkCuts`, which classify and cut a kinked level with no sampling and no new tolerance
- [ADR-125: A state is a driver the machine writes, committed at an event](./ADR-125-a-state-is-a-driver-the-machine-writes.md) — the clocked root, its bank of drivers and states, its request, its event loop, its atomicity; cycle 1's design §11 states what this cycle owes, and its §9 was written so that this cycle's clip is a TRUNCATION of `delta` before the event loop rather than a second locator
**Cites:**
- [ADR-104](./ADR-104-a-third-time-base-elapsed-seconds-that-never-wrap.md), [ADR-105](./ADR-105-the-run-owns-the-coordinates-and-binds-them.md) — the running bank and time base, untouched
- [ADR-122](./ADR-122-a-selection-decides-which-sources-a-law-reads.md) — the `Program`/`Edge` machinery, with its blocks and its jump plans, which the chain deliberately does not reuse
- [ADR-124](./ADR-124-only-what-moves-along-a-tick-s-path-is-evaluated.md) — path evaluation, a running optimization the clip does not need: a chain evaluation is microseconds
- [ADR-110](../EXPORT/ADR-110-the-compiled-program-is-published-in-the-document.md) — the version ladder that will have to carry a published stop, in the document cycle
**Amends nothing.** In particular it does **not** amend ADR-108, ADR-109 or
ADR-113. A running tick's localization, its candidate-set/`_pushes` group
analysis, its sampling of a constraint over a stretch and its
`_CROSSING_TOLERANCE` are untouched; the untimed reading of a range — refused
at binding, judged at the close of the enumeration — is untouched; and
ADR-113's "one authority judges one binding" is not rewritten but APPLIED, the
clocked simulation taking for the constraints it compiled exactly the position
the run already holds for the coordinates it owns.
**OpenSpec change:** `a-bound-stops-the-request` (archived at
`openspec/changes/archive/2026-09-17-a-bound-stops-the-request/`)
**Originating project:** `projects/Calculators/Curta-Type-I-3x`, branch
`direct-operation`, HEAD `9fb725f`; the project-level spike is its worktree
`WTs/clocked-spike`, commits `0968563` `a56937e` `bcf2017`, recorded in
`simulation/docs/clocked-spike-2026-09-16.md`.

## Context and Problem Statement

ADR-125 made a clocked machine sayable: a bank of drivers and states, a
request that moves one driver along a straight path, events located exactly on
it, and a commit at each. What it left explicitly open is what the clocked
root does with a declared `range`. Under ADR-125 a violated `Bound` is still
an impossible POSE: the request runs to its end, poses the tree, the
enumeration refuses that pose, and the whole request — every commit it made on
the way — is thrown away.

**That is not what a stop is, and the originating project is the proof.** The
spike's finding 5 is that every interlock the Curta needs is already
expressible with no new framework idea: eight locks, each a `Bound` on a
joint, each quoted from the manufacturer's booklet. Its finding 4 is that the
framework cannot OBEY them. Three of its scenarios say it concretely:
`blocked_crank_lift` lifts the crank past its 9 mm stroke and expects the lift
to stop at 9 mm; `crank_reversal` drags the crank backwards, where the
anti-reversal pawl must hold it at the last seated tooth — without which
ADR-125's own measurement is that the additive law commits a SECOND addition,
9 → 18; `mid_stroke_carriage_shift` moves the carriage while the crank is off
rest, which the booklet forbids and the closed form gets wrong (90 against the
operating model's 9) unless the lock holds the carriage still.

A machine whose interlocks delete the stroke you were half way through is a
machine no maker can operate. The whole point of the eight locks is that the
Curta *cannot* be misused, not that misusing it destroys the work.

**The framework already knows what a stop is** — ADR-108 located one inside a
running tick, ADR-109 made a bound an expression evaluated once per tick from
the committed state, ADR-113 let it read other coordinates and decided who
judges it. None of that reaches a clocked root, for one structural reason:
**a clocked simulation banks no joint coordinate.** A joint coordinate is what
the ordinary untimed enumeration recomputes from the bank on every pose, and a
pose costs milliseconds where a commit costs microseconds (the spike measured
22 ms against 26 µs). Something had to say what a bounded coordinate is WORTH
at a driver value, along a path, without posing the tree.

## Decision Drivers

- **A clocked model's determinism claim must survive.** ADR-125 introduced no
  locator, no knob and no tolerance — every event is SOLVED. A stop that was
  searched would make the claim untrue for a model whose author cannot see
  which of his bounds curves.
- **The clip must not become a second locator.** Cycle 1's design promised
  that this cycle is a truncation of `delta` in front of the existing event
  loop, and the rising-step rule, the far-side landing, the tie-by-identity,
  the pre-event reads and the atomicity must all come through untouched.
- **One arithmetic must decide a stop.** Two judges of the same declared bound
  — a composed chain and the ordinary enumeration — evaluate the same relations
  in different orders, and floating-point addition is not associative. The
  place where an ulp matters is precisely the landing ON an inclusive bound.
- **The running and untimed readings of a range are evidence, and stay put.**
  ADR-108's tick and ADR-113's close-of-enumeration judgement are what the pin
  tumbler lock and every untimed model rest on.
- **A declaration the framework cannot follow is a mistake in the model.**
  ADR-125 set that temperament for a state nothing writes and a relation no
  driver can reach; a stop that can never stop is the same declaration.

## Considered Options

**How a bounded coordinate is valued along a path.**

1. **Pose the tree along the path.** Correct by construction and rejected on
   cost: the ratio measured on this cycle's own fixtures is one chain
   evaluation against one pose at **1:72, 1:28 and 1:36**. A clip that posed
   would cost what the running mode costs, which is the generality the clocked
   discipline exists not to pay for.
2. **A symbolic pose.** Bind the bank to symbols and pose once; the build path
   already does exactly this for the viewer, and it would compose everything
   for free, an author's hand-set joint included. Rejected because it makes
   clocked CONSTRUCTION require the whole tree to be symbolically poseable and
   to build its geometry symbolically — a far larger demand than a stop needs,
   and one ADR-125 deliberately did not make — and because what it produces is
   the model's whole geometry rather than a handful of coordinate chains.
3. **`compile_program`.** The running compile answers this question and more,
   and `Program._sub_program` already extracts "the edges that determine this
   coordinate and every read". Rejected AS A WHOLE, for two reasons that are
   about when it refuses and what it carries. `_relation_edge` refuses a law
   the run cannot integrate, a self-read into an unbanked end and a partly
   banked driven group while the edge is still a CANDIDATE, so compiling the
   program would refuse clocked models for relations no bound ever reads; and
   its `Edge`/`Program` machinery carries jump PLANS and increments, which are
   the RUNNING reading of a relation (ADR-107 subtracts a jump because the
   coordinate is retained) and not the clocked one, where a jump in a chain is
   a part that genuinely steps. What is reused is the layer below both.
4. **A composed CHAIN.** Chosen.

**Which coordinates are refused.** A first reading refused every bounded
coordinate no relation chain reaches. That swallows a third case between "no
relation determines it" and "the author binds it by hand": a DECORATIVE range
on a part that simply rests. The rest render's own records tell the three
apart with no new bookkeeping, so the constant case is admitted rather than
refused. The one cost is stated rather than hidden: an author's REST-DEFAULT
GUARD (`if self.wheel.turn is None: self.wheel.turn = 0`) is an author
binding and falls on the refused side, because the framework cannot tell a
guard's constant from a `simulate()` that computes a coordinate from three
other things.

**What a violated bound does to a request.** Leaving an uncompilable bound to
the pose, where it goes on raising `JointRangeError`, was rejected: it would
give one model two kinds of bound with two different behaviours, told apart by
nothing the author can see, and would let an interlock fail open on the day it
is first met.

**Who judges at the end of a request.** Refusing a request when chain and pose
disagree was rejected outright — it turns a legitimate stop into a runtime
failure a maker cannot fix, on a machine whose declarations are all correct.
Taking the BINDER over (as the run does) was rejected too: a clocked
simulation binds no joint coordinate, the relations do, and the binder
identity is what the double-binding rule rests on.

**Where the clip is read.** Re-computing the clip after each commit is the
finer reading and was rejected for this cycle: ADR-109 evaluates a bound once
per TICK so that every segment sees the same number, and the clocked quantum
is the REQUEST — what a maker performs, what a snapshot replays, what ADR-125
already treats as atomic.

## Decision

**A declared `range` is a STOP on a clocked request path, and the stop is a
TRUNCATION OF THE TRAVEL BEFORE ANY EVENT IS LOCATED.** `Clocked.move` gains
one step in front of ADR-125's loop: the travel is clipped to the largest
fraction at which every compiled constraint is still satisfied, the driver's
target becomes that landing, and the event loop then runs over the clipped
path exactly as it ran before — same rising-step rule, same far-side landing,
same tie by identity, same synchronous pre-event reads, same single pose at
the end, same atomicity. **Since a clocked request moves ONE driver, ADR-108's
"group of inputs that push the coordinate" IS that one driver:** the run's
candidate sets, its per-candidate sub-program pass and its `_pushes` test
answer a question a clocked request cannot ask, and are neither ported nor
needed. A clocked stop stops the request. Clipping the bounded COORDINATE and
letting the driver run on is the clamp ADR-108 refused, for ADR-108's reason:
the group's other coordinates would stand where an unstopped request put them.

**The chain: one expression graph from the bank to a bounded coordinate,
composed by SUBSTITUTION.** At simulation construction `compile_bounds`
(`simulation/clocked.py`) compiles, for every joint coordinate whose joint
declares a range and for every coordinate a `Bound` reads, ONE graph over the
bank's qualified ids. A relation's untimed meaning is absolute — the driven
end IS the law applied to the sources — so composing is substitution:
`_Chains` walks the relations the REST RENDER already resolved, in the
direction it resolved them, and replaces each source name by that source's own
graph, down to declared drivers and declared states, which stay free names. A
wiring contributes its `ratio`/`offset`, a derived coordinate its linear
formula, a `law=` relation the graph ADR-106's own `checked_expression`
inspects it into. **An INTERMEDIATE PORT is traversed like any other link** —
it is a calculation composed into the chain and never a banked value — which
is not a nicety: the Curta's selectors are wired `setting = Port()`,
`setting.drives(knob.travel, ratio=6)`, so refusing to traverse one would
refuse the originating machine's own interlock.

Three properties make this the right object, and they are the decision: it is
evaluated by ONE `GraphValue.evaluate` per point, with no tree walk and no
pose; it SUBSTITUTES and never SIMPLIFIES, so it performs over the identical
native values arithmetic EQUIVALENT to the enumeration's, which is what makes
the clocked simulation fit to judge its own constraints; and it is an
expression, which is what the document cycle must publish for a browser to
stop the same machine at the same place.

**What the bank must reach, in three cases decided by the rest render's own
records.** After construction's pose, each bounded coordinate's slot either
holds a value or does not, and `slot.binder` names what put it there:

| What the rest render recorded | What the compile does |
| --- | --- |
| the slot holds NO value — no relation, wiring or derived formula resolved to it, and no author code bound it | ADMIT it as a CONSTANT chain: the value it holds at rest |
| `slot.binder` names a relation, a wiring or a derived coordinate's formula | COMPOSE the chain through it |
| the slot holds a value and its binder is `None` — the root's own `simulate()` bound it | REFUSE at construction, by name |

A ranged coordinate NOTHING binds is therefore a decorative range on a part
that rests: its level is constant in every driver, no request examines it, it
costs nothing, and **it is not a stop that can fail even when that rest value
lies outside the declared pair** — nothing ever bound the coordinate, so the
enumeration never recorded a binding to judge, which is true today under every
root. A `Bound` may READ such a coordinate, and takes that constant.

Refused at simulation construction, by name, naming the node, the joint, the
side and where the chain broke (`ClockedError`): a bounded coordinate the
author's `simulate()` binds BY HAND; a chain through a law that is not an
expression (with `checked_expression`'s own message); a `Bound` whose `reads`
name a coordinate no chain reaches; a `Bound` reading a plain PORT (ADR-113's
existing refusal, message unchanged); a chain that reads the coordinate it
drives; a cyclic chain; and the curved level below. The refusal names the
ASSEMBLY whose `simulate()` bound the slot — `slot._bound_by`, the record the
rest render already keeps — and not the node the slot belongs to, because the
first is the class the maker has to edit.

**The level, and what each argument reads.** For each bounded side the
CONSTRAINT LEVEL is `value(t) − bound(t)` on the high side and
`bound(t) − value(t)` on the low side, so that OUTSIDE is positive. Its
arguments are read as ADR-109 and ADR-113 read them, with the REQUEST in the
tick's place:

- **the bound's OWN coordinate takes the value it holds when the request
  STARTS** — one chain evaluation, a number for the whole request;
- **each `reads=` coordinate takes its value ALONG THE PATH**, through its own
  chain, which under a clocked root costs one graph evaluation rather than a
  sub-program pass;
- **a read of a declared DRIVER or a declared STATE is admitted**, and is the
  cheapest read there is: a driver that is not moving is a standing number,
  the moving one is the path's own parameter, and a state is constant between
  events and therefore constant along a clip computed before any event.

**The own-coordinate rule is load-bearing twice, and the requirement note's
own sketch is the counter-example.** It is what makes the ratchet's lower
bound the LAST SEATED TOOTH rather than a bound that follows the arbor down
and never blocks. And it is what makes an interlock stating a FREEZE
expressible at all. The note `workflow/docs/clocked-machine.md` sketched a
Curta selector lock as

```python
setting = Prismatic(..., range=(0, Bound(
    lambda setting, crank: 54 * (phase(crank) < 1), reads=(crank_turn,))))
```

which says the selector may be anywhere between 0 and 54 while the crank
rests and must be at ZERO the moment it leaves rest — so a Curta with a
selector at 18 and the crank half way through a stroke, which is every
mid-stroke pose there is, violates it. What the mechanism says is that the
selector may not MOVE while the crank is off rest, and that is stated by
letting BOTH bounds read the coordinate's own committed value:

```python
setting = Prismatic(..., range=(
    Bound(lambda setting, crank: setting * (1 - rest(crank)), reads=(turn,)),
    Bound(lambda setting, crank: setting + (54 - setting) * rest(crank),
          reads=(turn,))))
```

At rest the pair is `(0, 54)` and the knob is free; off rest both bounds
evaluate to the value the coordinate HELD when the request started, so the
knob may not move in either direction while the crank, whose own motion leaves
the level flat at zero, runs its whole travel. The same declaration poses
(vacuously — a bound reading its own coordinate is applied at the close to the
value being judged, so `setting <= setting` passes for every value, which is
honest: a pose has no path, and a freeze is a statement about MOTION), runs
under ADR-109's committed value, and clocks. This is the shape every one of
the spike's off-rest locks takes, and it is this cycle's acceptance fixture.

**The classification is STRUCTURAL, decided once, per driver that can move the
level** — the same `_standing_except` substitution ADR-125 classifies an `at`
with:

| Shape in that driver | What the clip does |
| --- | --- |
| `constant` | the driver cannot move this level; not examined for it, costs nothing |
| `affine` | its crossing of the threshold is ONE DIVISION. Exact |
| `kinked` | cut at ADR-123's own breakpoints, each piece solved the same way. Exact, and a breakpoint is not a stop |
| carries JUMPS | the path is PARTITIONED at the level's own jump surfaces by `JumpPlan.cuts`; on each piece every jump node holds one branch, so the SKELETON classifies, affine or kinked as above. Exact |
| `None` (curved) | **REFUSED at construction**, naming the joint, the node, the side, the driver whose motion curves the level and the primitive it curves through |

**The jumped row is not decoration.** ADR-109 admits jumps in a bound — a
`floor` for a tooth, a comparison for a gate — and every one of the spike's
off-rest locks is a comparison against the crank's phase, which is itself a
`floor`. A level that STEPS ACROSS its zero has no crossing to solve, and the
partition is what makes that statable: the stop is at the end of the last
piece on which the level was satisfied, which is the landing rule with no
special case. `JumpPlan.cuts` raising `TooManyCrossings` is re-raised as the
clocked refusal (`TooManyEvents`) naming the request, the constraint and
`_MAX_CROSSINGS`; the request commits nothing.

**The landing is the last representable driver value that SATISFIES the
bound.** A solved crossing gives a fraction; the driver's value there is
walked, in float ORDINAL space, to the nearest representable value on the
SATISFIED side, through ADR-121's own `far_side_of` — so the framework still
has ONE landing walk — with membership decided by EVALUATING the level there
and never by comparing a float to a bound. This is the one place a clocked
stop and a clocked event differ, and they differ for the reason they agree
everywhere else: an event fires when the path has REACHED a surface, so it
lands beyond it; a stop is where the machine still IS, so it lands short of
it. Three cases follow and a reader can predict them: a bound met exactly at a
representable value lands ON it, bounds being INCLUSIVE as they are everywhere
in the framework; a level that JUMPS across its zero lands on the last float
before the jump's own surface; a level already at its limit and pushed further
admits ZERO travel.

**The stopped coordinate is NOT snapped onto its bound.** ADR-108 commits the
stopped coordinate at its bound exactly, because a running bank HOLDS that
coordinate and `Run.bind()` would otherwise re-judge a value a few ulps
outside. A clocked simulation banks no coordinate: it lands the DRIVER, and
the pose recomputes the coordinate from it. There is nothing to snap.

**The direction test is ONE threshold: `h = max(0, g(0))`, read at the start
of each request.** The admitted fraction is the largest at which no
constraint's level exceeds its own `h`. Standing legally, `g(0) <= 0` and
`h = 0` — the ordinary bound. Standing OUTSIDE, the machine may move freely as
long as it does not go FURTHER outside. Nothing is clamped and nothing is
silently repaired, which is ADR-108's rule exactly. A clocked bank can come to
stand outside in two ways the framework already admits: a constant chain whose
rest value lies outside the declared pair, and a `Bound` whose READS held no
value at the pose that made the bank, which the enumeration does not judge at
all (the joints capability's own rule, older than this cycle). Refusing a
request that starts outside was rejected: a pose is judged when it is made,
and a simulation standing where it was PUT must be able to move back.

**That threshold is read per request, and the cross-request consequence is
stated rather than hidden.** Once a request has carried a coordinate back
INSIDE its bound, the next request reads `h = 0` and is clipped at the bound —
so a machine that stood at 20 against a bound of 9, moved inward to 5, cannot
return to 20: it is admitted as far as 9 and no further (measured at 4 of the
15 asked for, on this cycle's `outside` fixture). The ratified design's own
planned proof asked for "a request back to exactly where it started" to be
admitted, and that cannot hold under the decision it was written for. The
DECISION is what was implemented; a threshold REMEMBERED across requests is a
different design and would need its own evidence. Recorded in
`workflow/warts.md`.

**One clip per request, computed at its start, and NOT recomputed between
events.** The coarseness is visible exactly once — for a bound that reads a
STATE a commit inside the same request writes — and it is behaviour with a
fixture of its own: on the `gate` fixture one `move('crank', by=1000)` is
clipped against the CLOSED gate and admits 300, while `move('crank', by=200)`
followed by `move('crank', by=800)` commits the event first and admits 1000.
The long request is clipped against the bank the maker performed it from; the
split pair lets the first commit move the bound before the second is clipped.
**The pawl cannot show this, and that is worth saying**, because the obvious
scenario is wrong: a one-argument bound's own coordinate is read at the
request's start, so a request dragging the crank backwards stops at the last
seated tooth, and the NEXT request starts ON that tooth, where the bound
evaluates to the tooth itself and admits NOTHING. Ten short backwards requests
give ONE tooth of backlash, exactly as one long one does — which is what a
ratchet does, and why the pawl is no evidence either way. A project that needs
the finer reading splits the request, which is exact.

**A request stopped at ZERO travel is ADMITTED.** It commits nothing, poses
nothing new, leaves the bank exactly as it stands and returns its value object
with `admitted = 0.0` and its stops. It is not an error: an interlock that
holds is the machine working. This is the single most important behavioural
difference from ADR-125, under which every attempt to move a locked part
deletes the request, and it is what makes the Curta operable.

**ONE AUTHORITY, one arithmetic.** During a REQUEST the clocked simulation is
the SOLE AUTHORITY for the constraints it compiled:

1. the pose a request ends at does NOT judge those coordinates — neither at
   bind time nor at the close of the enumeration;
2. the clocked simulation judges them ITSELF, at the end of every request,
   over the FINAL bank, THROUGH THE CHAIN, against the same thresholds the
   clip used, differing from the clip only in that the bank now carries what
   the events committed. A violation refuses the request by name, raising
   `JointRangeError` — the kind the joints capability already exports for
   exactly this — naming the node, the joint, the side, the bound as the chain
   evaluates it over the final bank, the value the chain gives the coordinate
   there, and the request. It is made BEFORE the tree is posed, so a refused
   request never poses, and ADR-125's atomicity is untouched. With the clip in
   front of the events the only way to reach it is a COMMIT: a state an event
   wrote, which the clip read at its pre-request value;
3. a pose that is NOT a request — construction, `state=`, `restore` — is judged
   by the ENUMERATION, unchanged in every particular. A `Bound` violated by
   the initial pose is an impossible pose and raises `JointRangeError`,
   because a machine cannot be PUT where it cannot BE.

**The mechanism is a MARK, not a binder.** `compile_bounds` returns, beside
the constraints, the `(id(node), joint name)` identities it compiled for;
`motion/ports.py` holds them in `_clocked_marked` for the duration of one
request's pose (`clocked_marking`, `clocked_owned`), and the two judgement
sites consult it exactly as `refuse_bounds` already consults `run_owned`:
`Joint._refuse_out_of_range` returns without judging a marked coordinate —
AFTER recording the binding, so the enumeration's list stays complete and its
close consults the same mark through its own site — and `couplings.refuse_bounds`
skips a marked coordinate beside its existing run-owned skip. `Clocked._posed`
opens and closes the mark and takes a `marked=` argument that only `move`
passes, so the working pose and the re-pose of the previous bank on a refusal
are covered and nothing outside a request is ever marked. The mark is EMPTY
everywhere else, which is why an untimed or running tree takes exactly the
branch it takes today.

**The agreement between chain and pose is a TEST, with a stated tolerance, and
never a runtime refusal.** At twenty fractions of each fixture's request path
the chain's value for every bounded coordinate is compared with the value the
POSED tree holds, by `math.isclose(rel_tol=1e-12, abs_tol=1e-12)` rather than
bit for bit — because bit-for-bit is a claim about evaluation order that
neither this decision nor ADR-113's makes. A composition that SIMPLIFIED fails
it by orders of magnitude, which is the bug it exists to catch; an ulp does
not, which is the failure it must not manufacture.

**What a request reports.** `Request` keeps ADR-125's `input`, `by`, `to` and
`commits` and gains **`admitted`**, the travel actually made in DESIGN units
(`by` stays what the caller asked for), and **`stops`**, a tuple of `Stop`,
empty exactly when the whole travel was made — each naming the bounded
coordinate by qualified id, the side (`'low'`/`'high'`), the bound EVALUATED at
the landing, the coordinate's value there, the driver's value and the fraction
of the REQUESTED travel. Several constraints met at ONE landing are several
entries, exactly as several relations at one landing are one event. `record=N`
keeps a bounded ring `sim.stops` beside `sim.commits`, which **LIFTS ADR-125's
refusal of that name**: a clocked model has no clock, but it does have stops,
and ADR-108's reason for a separate ring holds word for word — a stop is a
BOUND OF A COORDINATE and a commit is a VALUE THE MACHINE WROTE, so a reader
counting strokes must not have to filter out interlocks. The vocabulary is
ADR-108's and nothing is added to it.

## Consequences

- **The Curta's eight interlocks are answered, with no framework idea this
  decision does not state.** The crank ratchet is a one-argument bound on the
  crank's own joint, affine in the crank and SOLVED; the two lift strokes are
  plain numeric ranges; `carriage_turn_needs_lift` and
  `crank_needs_seated_carriage` are comparisons over a standing read, a
  constant or a jump depending on what moves; the four off-rest locks are the
  FREEZE above; `ring_rest_checks` is a `floor`/`ceil` over the moving driver,
  PARTITIONED and solved per piece. Which of them the Curta should actually
  declare is the project's audit, in the project's repository.
- **Measured on this cycle's own fixtures, and compared to nothing else.**
  Compiling the constraints at construction: 15.5 µs for a clocked tree with
  no ranged joint (0 constraints, the whole call being the coordinate walk),
  and 221.8–660.9 µs for the six fixtures that declare one or two.
  Composed chains are **1 to 3 nodes** and levels 3 to 18, so the risk "a
  composed chain can be large" is not reached by anything this cycle can
  write. One request, with the restore's pose subtracted: 22.3 µs with no
  constraint, 183.0 µs with one examined and not violated, 203.1 µs clipped
  affine, 263.4 µs clipped kinked, 269.1–398.9 µs clipped jumped, 391.6 µs for
  two constraints and zero travel admitted. **The ratio the whole design rests
  on** — one chain evaluation against one POSE of the same fixture — is 1.64 µs
  against 118.6 µs (1:72), 2.94 against 82.9 (1:28) and 2.94 against 104.7
  (1:36). The end-of-request judgement costs one LEVEL evaluation per compiled
  constraint, beside one for each threshold at the start: `2n` evaluations for
  `n` constraints, plus one clip per constraint the moving driver moves.
- **Zero behaviour change everywhere else, structurally.** A tree that
  declares no `State` compiles no constraint and enters no path of this
  decision, because the compile is reached from ADR-125's clocked construction
  and nowhere else. A clocked tree with no ranged joint compiles nothing: the
  span table is empty and the request is ADR-125's request, field for field,
  plus an `admitted` equal to its travel. The running executor is untouched —
  not ADR-108's localization, not ADR-113's sampling, not `Program`, not
  `Edge`, not the span table's meaning. `_compiled_spans` and `_qualified_reads`
  gained only an `authority=` argument, defaulting to `'the run'`, so that a
  clocked refusal does not say "the run"; the running messages are asserted
  unchanged character for character.
- **A refusal will reject a model somebody wrote.** A clocked project with a
  ranged joint posed by hand in `simulate()` is refused at construction, and
  an author's REST-DEFAULT GUARD falls on that side. The message names the
  joint and says to state the relation that moves it or drop the range, which
  is a one-line change in the model. The alternative is an interlock that
  fails open on the day it is first met.
- **One authority means a composition bug fails silently in the small.** A
  chain wrong by a hair clips a hair early or late instead of raising. The
  agreement test samples every fixture's whole path; the bug it cannot catch
  is one smaller than its tolerance, which is smaller than a stop is
  meaningful.
- **Two rows of the construction refusal table are unreachable, and that is
  reported rather than hidden.** A self-read chain and a cyclic chain are both
  refused EARLIER, by the relation layer, under every non-running root
  (`CouplingError` and `UnreachedCoordinate`), long before the clocked compile
  runs. The guards remain in `_Chains` as backstops; the self-read refusal
  test asserts the message a maker actually sees, and the cyclic row has no
  test at all — a structural blind spot, recorded in `workflow/warts.md`.
- **The mark is process-wide.** `_clocked_marked` is a module-level frozenset
  in `motion/ports.py`, of the shape `run_owned` already has, and it is empty
  outside one request's pose. A per-simulation mark would be cleaner and is
  recorded as a follow-up.
- **`Stop` exists twice**, in `program.py` and in `clocked.py`. The fields are
  ADR-108's in both; a reader of a clocked request meets only the clocked one,
  and a merged class would have to carry a `tick` a clocked request does not
  have.
- **A clocked model still cannot be published or viewed.** ADR-125 refuses a
  clocked document by name, and this decision adds a stop the document does
  not yet carry. The document cycle owns both, and ADR-110's ladder is why.
- **Deliberate narrowings, each recorded in `workflow/warts.md` and each cheap
  to lift:** one driver per request (widening is a change to the
  classification, not to the clip); the clip not re-computed between events; a
  bound may not read a PORT, refused with ADR-113's own message; no
  `Instruction`, no control and no `blocked` command vocabulary, a clocked
  root having no command surface and a request reporting its own stop; and a
  request does not report the constraints it EXAMINED — a maker asking "why did
  the knob not move" is answered by `stops`, one asking "which interlocks are
  live right now" is not, and that wants the cycle which gives a clocked model
  a panel.

## Promotion

Accepted 2026-09-17 at the cycle's adversarial review, which ran an
independent probe against the uncommitted implementation and returned nothing
needing closure. Two questions the implementation raised were decided there
rather than by the implementation: the direction test's contradiction is a
mis-statement in the ratified design's PLANNED PROOF and not in its decision,
so the decision stands and the proof text is what moved; and the code's names
`compile_bounds`/`Bounded` stand against the proposal's
`compile_constraints`/`Constrained`, noted as superseded in the change's
evidence rather than by editing a ratified proposal. The implementation's own
record — the red log, the deviations reported as deviations, every measurement
quoted above, and the four open design questions — is `evidence.md` inside the
archived change.
