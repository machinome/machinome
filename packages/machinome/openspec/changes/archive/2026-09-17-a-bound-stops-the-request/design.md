## Context

The originating project, the finding and the measurements are in
`proposal.md`. Three documents bind this design and all three are evidence
rather than authority:

- `workflow/docs/clocked-machine.md` — the requirement note, whose
  **candidate spelling** is explicitly a sketch. Its interlock sketch is
  measurably wrong as written, and §4 below says why and what replaces it.
- `projects/Calculators/Curta-Type-I-3x/WTs/clocked-spike`, record
  `simulation/docs/clocked-spike-2026-09-16.md` — the project spike. Its
  **finding 4** ("a stop on a request path") is the whole of this cycle, its
  **finding 5** (eight interlocks, all `Bound`s on joints, no new framework
  idea) is the requirement's shape, and its `Interlocks._apply_interlocks`
  is the behaviour this cycle moves into the framework.
- The archived cycle 1, `openspec/changes/archive/2026-09-17-declare-the-
  state` (ADR-125), whose design §11 states what this cycle owes and whose
  §9 was written so that the clip is a TRUNCATION OF `delta` BEFORE the
  event loop and not a second locator.

Three accepted decisions constrain everything here and none of them is
reopened:

- **ADR-108** — a declared range is a physical stop that stops the group of
  inputs that push the coordinate, located inside the stretch, with the
  coordinate committed AT its bound and nothing ever clamped.
- **ADR-109** — a bound may be an expression evaluated at the COMMITTED
  state, once per tick, which is what makes a ratchet's tooth the tooth the
  tick started on; jumps in a bound are admitted with no plan because a
  bound is evaluated and never integrated.
- **ADR-113** — a bound may READ other coordinates: the own coordinate takes
  its committed value, every read takes its value ALONG THE PATH, the
  constraint is examined only when something it depends on moves, and the
  untimed reading is judged at the close of the enumeration.

The framework's own tools this design CONSUMES rather than reproduces:
`_compiled_spans` and `_qualified_reads` (ADR-109/113's bound compile,
including every refusal they already state); `_units`, `checked_expression`
and `_plan_of` (ADR-106/107's law inspection); `JumpPlan.cuts` and
`_branch_of` (ADR-107); `_shape_of` and `_KinkCuts` (ADR-123); and
`far_side_of`'s ordinal walk in float space (ADR-121). **No new locator, no
new law inspection, no new tolerance and no new knob. As in cycle 1, no
tolerance AT ALL:** under a clocked root every crossing is solved, so a stop
is a float and not a window.

## Goals / Non-Goals

### Goals

1. A clocked machine's declared stops STOP it. A request that would drive a
   coordinate through a bound admits the travel the machine allows, fires
   the events on that travel, and says where it stopped.
2. The stop is located EXACTLY — solved, cut or partitioned, never searched
   — so that a clocked model's determinism claim survives this cycle intact.
3. The eight interlocks the spike measured are expressible with no new
   declaration: the same `range=`, the same `Bound(..., reads=...)`, read
   the same way under a clocked root as under a running one.
4. Nothing an untimed, stateless or running root does changes.

### Non-Goals

Listed in `proposal.md`. The two a reader will look for:

- **The clip is not re-computed between events** (§8). The request is the
  quantum ADR-109's tick was.
- **The stopped coordinate is not snapped onto its bound** (§6). A clocked
  simulation banks no joint coordinate; it lands the DRIVER.

## Decisions

### 1. A clocked stop is a truncation of the request's travel

ADR-108 stops a running tick by splitting it into sub-ticks at `t*` and
zeroing the stopped group's admissions for the remainder. A clocked request
has one input and no cadence, so the same statement is simpler by everything
the run needs it for:

> The request's travel is CLIPPED to the largest fraction at which every
> compiled constraint is still satisfied. Cycle 1's event loop then runs
> over the clipped path exactly as it runs today.

`delta` is truncated once, before the first event is located. Nothing about
the event loop changes: not the rising-step rule, not the far-side landing,
not the tie rule, not the pre-event reads, not the atomicity. That is
precisely what cycle 1's §11 promised — "the solver here is written so the
clip is a truncation of `delta` before step 1, not a second locator" — and
this design keeps it literally.

**Since one driver moves, ADR-108's group is that one driver.** The run's
whole apparatus for deciding which inputs push a stopped coordinate — the
candidate sets, the per-candidate sub-program pass, the `_pushes` test —
answers a question a clocked request cannot ask. It is not ported and not
needed. A clocked stop stops the request.

*Alternative rejected:* clipping the bounded COORDINATE and letting the
driver run on. That is the clamp ADR-108 refused for the same reason: the
group's other coordinates would stand where an unstopped request put them,
so the machine would be internally inconsistent — a selector at its stop
with the knob that drives it half a step past.

### 2. The bank holds no joint coordinate, so the chain is compiled

A clocked `Sim` banks drivers and states and nothing else (cycle 1 §4, §9).
A joint coordinate is what the ordinary untimed enumeration computes from
that bank on every pose, and a pose costs milliseconds where a commit costs
microseconds — the spike measured 22 ms against 26 µs — so a stop cannot be
located by posing the tree along the path. Something must say what a bounded
coordinate is WORTH at a driver value without posing.

**Decision: at simulation construction, compile each bounded coordinate and
each coordinate a bound reads into ONE EXPRESSION GRAPH over the bank, by
composing the relations that determine it.** A relation's untimed meaning is
absolute — the driven end IS the law applied to the sources — so composing
is substitution: the determining relation's law graph, with each source name
replaced by that source's own graph, down to the bank's ids, which stay free
names. A wiring contributes its `ratio`/`offset`, a derived coordinate its
linear formula, a `law=` relation its inspected graph.

**Three properties make this the right object.** It is evaluated by ONE
`GraphValue.evaluate` call per point, with no tree walk and no pose. It is
composed by SUBSTITUTION and never simplified, so it performs arithmetic
equivalent to the enumeration's over the identical native values — which is
what §10's agreement test asserts and what makes the clocked simulation fit
to judge its own constraints. And it is an expression, which is what cycle 4 must publish for
the browser to stop the same machine at the same place.

*Alternative considered and rejected: a symbolic pose.* Binding the bank to
symbols and posing once would compose everything for free — including a
joint an author's `simulate()` sets by hand — because that is what the build
path already does for the viewer. It was rejected because it makes clocked
CONSTRUCTION require the whole tree to be symbolically poseable and to build
its geometry symbolically, which is a far larger demand than a stop needs
and which cycle 1 deliberately did not make; and because the expressions it
produces are the model's whole geometry rather than a handful of coordinate
chains.

*Alternative considered and rejected: `compile_program`.* The running
compile answers exactly this question and more, and `Program._sub_program`
already extracts "the edges that determine the bounded coordinate and every
read". It was rejected as a WHOLE because it builds its candidate edges
before it knows which ones matter: `_relation_edge` refuses a law the run
cannot integrate, a self-read into an unbanked end and a partly-banked
driven group while the edge is still a candidate, so compiling the program
would refuse clocked models for relations no bound ever reads. Its
`Edge`/`Program` machinery also carries jump PLANS and increments, which are
the running reading of a relation (ADR-107 subtracts a jump because the
coordinate is retained) and not the clocked one, where a jump in a chain is
a part that genuinely steps. What IS reused is the layer below both: the
same `_units` walk, the same `checked_expression` inspection, the same
`_shape_of`, the same `_KinkCuts`, the same `JumpPlan`.

### 3. What the bank reaches, and what is refused

A coordinate is REACHED when a chain as in §2 exists from the bank to it:
every link a relation the rest render resolved in a direction, every law an
expression in `solid_node.math`'s vocabulary, INTERMEDIATE PORTS included.
An intermediate port is not a bank value and does not have to be: it is a
calculation, composed into the chain and never stored — which is exactly how
the Curta's selectors are wired (`setting = Port()`, `setting.drives(knob.
travel, ratio=6)`), so refusing to traverse one would refuse the originating
machine's own interlock.

**Refused at simulation construction, by name, naming the joint, the node,
the side and where the chain broke:**

| Attempt | Why |
| --- | --- |
| a bounded coordinate an author's `simulate()` binds BY HAND | nothing can follow it along a path: its value is whatever that code computes, from whatever it reads |
| a bounded coordinate whose chain passes through a law that is not an expression | the same, with the law named (`checked_expression`'s own message) |
| a `Bound` whose `reads` name a coordinate that is not reached | the level cannot be evaluated without inventing a value |
| a `Bound` whose `reads` name a plain PORT | ADR-113's existing refusal, unchanged, message included |
| a chain that reads the coordinate it drives (ADR-121's self-read) | a retained read is a HISTORY, and a clocked pose retains nothing between requests: there is no value to read |
| a chain that is CYCLIC | the same, said of a cycle the rest render left |
| a level that CURVES in a driver that moves it (§5) | a clocked stop is solved and never searched |

**A ranged coordinate NOTHING binds is ADMITTED, as a constant.** Between
"no relation determines it" and "the author binds it by hand" sits a third
case the refusals above must not swallow: a decorative range on a part that
simply rests. The REST RENDER's own records tell the three apart, with no new
bookkeeping — after construction's pose, each bounded coordinate's slot either
holds a value or does not, and `slot.binder` names what put it there:

| What the rest render recorded | What the compile does |
| --- | --- |
| the slot holds NO value: no relation, wiring or derived formula resolved to it, and no author code bound it | ADMIT it as a CONSTANT chain |
| `slot.binder` names a relation, a wiring or a derived coordinate's formula | compose the chain through it (§2) |
| the slot holds a value and its binder is `None` — the author's own `simulate()` bound it | REFUSE, by the table above |

The constant is the value the coordinate holds AT REST, which for a
coordinate nothing binds is zero: an unbound coordinate is an unplaced joint,
and the part stands where the tree's rest placement puts it. Its level is
`constant` in every driver (§5), so no request ever examines it and it costs
nothing. **It is not a stop that can fail**, even when that rest value lies
outside the declared pair: nothing ever bound the coordinate, so the
enumeration never recorded a binding to judge — that is true today, under
every root, and this cycle does not start judging one. Under §7's threshold a
constant level stands at its own `h` forever and stops nothing.

A coordinate nothing binds is REACHED in the sense §3 opens with, so a
`Bound` may READ one: the read takes that constant. The refusal above is for
a read no chain reaches at all.

The one cost of drawing the line there is stated rather than hidden: an
author's REST-DEFAULT GUARD (`if self.wheel.turn is None: self.wheel.turn =
0`) is an author binding, so a ranged joint held by a guard falls on the
REFUSED side even though the value it takes is a constant. The refusal names
the joint and says to state the relation that moves it or drop the range,
which is a one-line change in the model, and the framework cannot tell a
guard's constant from a `simulate()` that computes a coordinate from three
other things.

**A stop that can never stop is a mistake in the model**, and that is the
whole justification for refusing rather than falling back. The rejected
alternative — leave an uncompilable bound to the pose, where it goes on
raising `JointRangeError` and refusing the request whole — would give one
model two kinds of bound with two different behaviours, told apart by
nothing the author can see, and would let an interlock fail open on the day
it is first met. Cycle 1 refused a state nothing writes and a committing
relation no driver can reach for exactly this reason; a bound nothing can
judge is the same declaration.

The cost is stated and accepted: a clocked project with a ranged joint it
poses by hand — a guard included — must state the relation that moves it, or
drop the range. A model that declares no range compiles nothing and pays
nothing, and a model whose ranged joint nothing binds compiles a constant and
pays nothing.

### 4. The constraint level, and what each argument reads

For each bounded coordinate `c` and each side that is not `None`, the
CONSTRAINT LEVEL is

```text
high side:   g(t) = value_c(t) - bound(t)
low  side:   g(t) = bound(t) - value_c(t)
```

`value_c(t)` is §2's chain, evaluated over the bank with the moving driver
at `start + delta·t`. `bound(t)` is the bound as `_compiled_spans` already
compiles it — a number, or a graph over the coordinate's own id and its
`reads` — with its arguments taken as ADR-109 and ADR-113 take them:

- **The own coordinate takes the value it holds when the REQUEST STARTS** —
  `value_c(0)`, a number, computed once. This is ADR-109's committed-state
  rule with the request in the tick's place, and it is load-bearing twice
  over: it is what makes the ratchet's lower bound the LAST SEATED TOOTH
  rather than a bound that follows the arbor down and never blocks, and it
  is what makes an interlock stating a FREEZE expressible at all.
- **Each read takes its value ALONG THE PATH**, through its own §2 chain.
  This is ADR-113's chosen option 4 ("own coordinate committed, reads along
  the path"), and under a clocked root it costs one graph evaluation rather
  than a sub-program pass, because the chain is already composed.
- **A read of a declared DRIVER or a declared STATE is admitted**, and is
  the cheapest read of all: a driver that is not the one moving is a
  standing number, the moving driver is the path's own parameter, and a
  state is constant between events and therefore constant along a clip that
  is computed before any event (§8). A read of a driver is already admitted
  under a running root (ADR-113's own scenario, "A read of a driver is an
  input of the bank"); a state is a driver the machine writes, so it enters
  the same way and needs no new rule.

**The note's interlock sketch is wrong, and the correction is a finding of
this cycle.** The note writes

```python
setting = Prismatic(..., range=(0, Bound(
    lambda setting, crank: 54 * (phase(crank) < 1), reads=(crank_turn,))))
```

which says a selector may be anywhere between 0 and 54 while the crank
rests and must be at ZERO the moment it leaves rest. A Curta with a selector
set to 18 and the crank half way through a stroke — every mid-stroke pose
there is — violates it. What the mechanism actually says is that the
selector may not MOVE while the crank is off rest, and a freeze is stated by
letting the bound read its own committed value:

```python
def rest(crank):
    return crank - 360 * floor(crank / 360) < 1

setting = Prismatic(..., range=(
    Bound(lambda setting, crank: setting * (1 - rest(crank)), reads=(turn,)),
    Bound(lambda setting, crank: setting + (54 - setting) * rest(crank),
          reads=(turn,))))
```

At rest the pair is `(0, 54)` and the knob is free; off rest both bounds
evaluate to the value the coordinate HELD when the request started, so the
knob may not move in either direction and the crank, whose own motion leaves
the level flat at zero, runs free. The same declaration poses (vacuously —
§10), runs (ADR-109's committed value is the tick's) and clocks. This is the
shape every one of the spike's off-rest locks takes, and the acceptance
fixture of §17 is built on it.

### 5. Classifying the level: solved, cut, partitioned, or refused

The classification is STRUCTURAL and decided ONCE, at construction, per
DRIVER that can move the level — exactly as cycle 1 classifies an `at`,
with the same substitution (`_standing_except`: every free name but the
moving driver becomes a `$`-prefixed standing placeholder, which `_shape_of`
reads as a constant on the piece).

| Shape of the level in that driver | What the clip does |
| --- | --- |
| `constant` | the driver cannot move this level; the constraint is not examined for it, and costs nothing |
| `affine` | its zero is ONE DIVISION from the two endpoint values. Exact |
| `kinked` | `_KinkCuts` cuts the path at the kink's own breakpoints, each solved by one division, and each sub-piece solved as above (ADR-123). Exact, and a breakpoint is not a stop |
| carries JUMPS | the path is partitioned at the level's own jump surfaces by `JumpPlan.cuts`, each solved; on each piece every jump node holds one branch, so the SKELETON is what classifies, affine or kinked as above. Exact |
| `None` (curved) | **REFUSED at construction**, by name, naming the joint, the side, the driver whose motion curves the level and the primitive it curves through |

The jumped case is not decoration. A bound is admitted to contain jumps by
ADR-109 (`floor` for a tooth, a comparison for a gate) and every one of the
spike's off-rest locks is a comparison against the crank's phase, which is
itself a `floor`. A level that steps ACROSS its zero has no crossing to
solve, and the partition is what makes that statable: the stop is at the end
of the last piece on which the level is satisfied, which is §6's landing
rule with no special case.

**Why refuse a curved level rather than search it.** The run bisects a
curved level to `_CROSSING_TOLERANCE` and says so. A clocked model's whole
value is that its events and its stops are exact; admitting a searched stop
would make the claim untrue for a model whose author cannot see which of his
bounds curves. The refusal must name the driver and the primitive, because
that is the one message that tells the author what to restate.

`JumpPlan.cuts` may raise `TooManyCrossings` for a level whose surfaces a
long request crosses more than a thousand times. It is re-raised as the
clocked refusal cycle 1 already shapes for its own events, naming the
request, the joint, the side and the maximum, and the request commits
nothing.

### 6. The landing is the last representable driver value that SATISFIES the bound

A solved crossing gives a fraction `t*`; the driver's value there is
`start + delta·t*`. That float is then walked, in float ORDINAL space, to
the NEAREST REPRESENTABLE VALUE ON THE SATISFIED SIDE — the mirror of cycle
1's far-side landing, through the same ordinal bisection (`far_side_of`),
with membership decided by EVALUATING THE LEVEL there and never by comparing
a float to a bound.

This is the one place where a clocked stop and a clocked event differ, and
they differ for the same reason they agree elsewhere: an event fires when the
path has REACHED a surface, so it lands beyond it; a stop is where the
machine still IS, so it lands short of it. Evaluating rather than comparing
gives the three cases a reader should be able to predict:

- a bound met exactly at a representable value — `turn <= 9.0` reached at
  `9.0` — lands ON it, because the level is satisfied there (bounds are
  INCLUSIVE, as they are everywhere else in the framework);
- a level that JUMPS across its zero lands on the last float before the
  jump's own surface, because that is the last value at which evaluating it
  gives satisfaction;
- a level already at its limit and pushed further admits ZERO travel, which
  is §7.

**The stopped coordinate is NOT snapped onto its bound.** ADR-108 commits
the stopped coordinate at its bound exactly, because a running bank holds
that coordinate and `Run.bind()` would otherwise re-judge a value a few ulps
outside. A clocked simulation banks no coordinate: it banks the driver, and
the pose recomputes the coordinate from it. There is nothing to snap, and
landing the driver on the satisfied side is what makes the recomputed value
satisfy the bound (§10).

### 7. The direction test: the level it started at, or zero, whichever is greater

ADR-108 frees a coordinate that stands outside a bound and moves the other
way; ADR-113 stops a stretch at the first sample where `g > 0` and
`g > g(0)`. Under a clocked root both statements collapse into one, because
the level is a function of one parameter:

> Let `h = max(0, g(0))`. The admitted fraction is the largest `t` at which
> no constraint's level exceeds its own `h`.

When the machine stands legally, `g(0) <= 0` and `h = 0`: the ordinary
bound. When it stands outside it may move freely as long as it does not go
FURTHER outside, and it may return. Nothing is ever clamped and nothing is
silently repaired, which is ADR-108's rule exactly.

**A clocked bank can come to stand outside a bound in two ways, and both are
declarations the framework already admits.** A CONSTANT chain whose rest
value lies outside the declared pair (§3) stands outside forever, and its `h`
is what keeps it from stopping every request that moves anything else. And a
`Bound` whose READS held no value at the pose that made the bank is not
judged by the enumeration at all — the joints capability's own rule, older
than this cycle — so a construction or a `state=` may leave the coordinate
outside it. `h` is stated for both, and for whatever a later cycle adds.

*Alternative rejected:* refusing a request that starts outside. A pose is
judged when it is made, by the enumeration (§10); a simulation standing where
it was put must be able to move back.

### 8. One clip per request, computed at its start

The clip is computed ONCE, over the bank as it stands when the request
begins, and the events are located on the clipped path. It is not
recomputed after each commit.

**Why.** ADR-109 evaluates a bound once per TICK, at the tick's start, "so
every segment of one tick sees the same number and ADR-108's localization
has a constant to solve against". The clocked quantum is the REQUEST: it is
what a maker performs, what a snapshot replays, and what cycle 1 already
treats as atomic. Reading a bound once per request is the COARSER of the two
available readings, and it is chosen deliberately, so that what a request
admits is decided by the bank the maker performed it from and not by where
the events happen to fall inside it.

**What it costs, precisely, and where it shows.** A state committed at an
event inside the request does not move a bound the clip already read. The
coarseness is therefore VISIBLE, and exactly once: for a bound that reads a
STATE a commit inside the same request writes, one long request and the two
short requests split at that event admit DIFFERENT travels. That is stated
behaviour with a fixture of its own (§16's `gate.py`, §17), not an accident:
the long request is clipped against the state as it stood when the maker
asked, and the split pair lets the first request's commit move the bound
before the second is clipped.

**It is the pawl that CANNOT show it.** Working the ratchet through is worth
the space, because the obvious scenario is wrong. A one-argument bound's own
coordinate is read at the request's start (§4), so a request dragging the
crank backwards from `T` stops at `6·floor(T/6)`, the last seated tooth — at
most one tooth of backlash. The NEXT request starts ON that tooth, where the
bound evaluates to the tooth itself and the threshold is met at zero travel:
it admits NOTHING. Ten short backwards requests therefore give ONE tooth of
backlash, exactly as one long one does, which is what a ratchet does and is
the reason once-per-request is safe for a pawl. It is also why the pawl is
no evidence either way about this decision, and why §17 asserts the two as
EQUAL rather than different.

Where a commit does carry a compiled coordinate out of range, the clocked
simulation's own end-of-request judgement refuses the request, which commits
nothing (§10). The spike's corpus contains no such mechanism: every one of
the eight locks reads the crank, the carriage or the ring, all of them driven
by drivers, and none of them reads a register. A project that needs the finer
reading splits the request, which is exact. Recorded as an open question
rather than a gap.

### 9. The request, end to end

Cycle 1's procedure with one step in front of it:

0. **Clip.** For each compiled constraint the moving driver can move (§5),
   locate the first violation on `[0, 1]` and take the smallest admitted
   fraction over all of them. `delta` becomes `delta · t_admitted`, the
   driver's target becomes the landing of §6, and the constraints that
   landed there are the request's STOPS. When no constraint is violated,
   `t_admitted` is `1` and nothing about the request differs from cycle 1.
1.–5. **Events**, unchanged: cycle 1's levels, rising steps, ties by
   identity of the far-side landing, synchronous pre-event reads, path
   order, and the tree bound ONCE at the end.
6. **Judge.** Before that pose, the clocked simulation evaluates every
   compiled constraint over the FINAL bank, through the same chains and
   against the same thresholds the clip used (§10). A violation — reachable
   only through a COMMIT — refuses the request by name, and nothing is posed.

**A request stopped at zero travel is ADMITTED.** It commits nothing,
reports its stop, leaves the bank exactly as it stands and returns the same
value object with `admitted = 0.0`. It is not an error: an interlock that
holds is the machine working. This is the single most important behavioural
difference from cycle 1, and it is what makes the Curta operable — under
cycle 1 every attempt to move a locked part deletes the request.

**Atomicity is unchanged and still includes the final pose.** A clip changes
what a request DOES, never whether it is atomic: a refusal anywhere between
step 0 and the final pose — step 6's judgement included — leaves the bank, the
tree and the record exactly as they stood.

### 10. One authority, one arithmetic: the clocked simulation judges what it compiled

A request has TWO possible judges of the same declared bound — §2's composed
chain, which the clip solves against, and the ordinary enumeration, which
judges the pose the request ends at — and they evaluate the same relations in
DIFFERENT ORDERS: the chain in one `GraphValue.evaluate` over a substituted
graph, the enumeration by an `Affine.forward` here, a `law=` callable there, a
derived coordinate's linear formula somewhere else. Substitution keeps them
arithmetically equivalent, not bit-identical: floating-point addition is not
associative, and the two can differ by an ulp. The place where an ulp matters
is precisely the place this cycle exists for — a landing ON an inclusive bound,
`9.0` met exactly — so a design that refuses the request when the two disagree
turns a legitimate stop into a runtime failure a maker cannot fix, on a
machine whose declarations are all correct.

ADR-113 already decided this shape for the run: *one authority judges one
binding*, and `couplings.refuse_bounds` skips a coordinate the run owns
because "the run located its stop, committed inside it and asserted it". The
clocked simulation is in exactly that position for the constraints it
compiled, and takes exactly that answer.

**Decision, in three parts.**

1. **During a REQUEST the clocked simulation is the SOLE AUTHORITY for the
   constraints it compiled.** The pose a request ends at does NOT judge those
   coordinates — neither at bind time (a number bound, a one-argument bound
   applied to the value being bound) nor at the close of the enumeration (a
   `Bound` with reads). The mark covers exactly the coordinates it compiled
   — which under §3 is every ranged joint coordinate a clocked root has,
   since the rest are refused at construction — and nothing else in the
   framework changes branch.
2. **The clocked simulation judges those constraints ITSELF, at the end of
   every request, over the FINAL bank, THROUGH THE CHAIN** — the same levels,
   the same thresholds `h` of §7, the same single arithmetic the clip used,
   differing from the clip only in that the bank now carries what the events
   committed. A constraint violated there refuses the request BY NAME, and the
   request commits nothing.
3. **A pose that is NOT a request — construction, `state=`, `restore` — is
   judged by the ENUMERATION, unchanged in every particular.** Those poses
   have no path, no moving driver and no chain evaluation: a `Bound` violated
   by the initial pose is an impossible pose and raises `JointRangeError`,
   because a machine cannot be PUT where it cannot BE.

**The mechanism.** The clocked simulation MARKS the coordinates it compiled —
`(node, joint)` identities, held for the duration of one request's pose — and
the two judgement sites consult that mark exactly as they already consult
`run_owned(slot)`: `Joint._refuse_out_of_range` returns without judging a
marked coordinate, and `couplings.refuse_bounds` skips it beside its existing
`run_owned` skip. `Clocked._posed` is what opens and closes the mark, so it
covers the working pose AND the re-pose of the previous bank on a refusal, and
nothing outside a request is ever marked. A mark rather than a BINDER is what
this needs, because a clocked simulation binds no joint coordinate at all: the
relations bind them, the binder identity is what the double-binding rule
rests on, and taking it over would change what the enumeration refuses.

**What the end-of-request judgement can catch, and what it says.** With the
clip in front of the events, the only way a compiled constraint can be
violated at the end of a request is a COMMIT: a state an event wrote, which
the clip read at its pre-request value, moving a coordinate or a bound. The
refusal is raised as `JointRangeError` — the kind the joints capability
already exports for exactly this, so what the maker sees for a commit that
carries a joint out of range is cycle 1's behaviour unchanged — and names
the node, the joint, the side, the bound as the chain evaluates it over the
final bank, the value the chain gives the coordinate there, and the request.
It is made BEFORE the tree is posed, so a refused request never poses at all,
and cycle 1's atomicity is untouched.

**The chain's agreement with the pose is a TEST, not a runtime refusal.**
§2's substitution rule is what makes the two agree, and §17 asserts it
directly: at twenty fractions of each fixture's request path, the chain's
value for every bounded coordinate against the value the posed tree holds,
compared with `math.isclose(rel_tol=1e-12, abs_tol=1e-12)` rather than bit
for bit, because bit-for-bit is a claim about evaluation order that neither
this design nor ADR-113's makes. A composition that SIMPLIFIED would fail it
by orders of magnitude, which is the bug the test is there to catch; an ulp
would not, which is the failure it must not manufacture.

**A freeze's untimed judgement is vacuous, and that is fine.** A bound that
reads its own coordinate is applied at the close to the value being judged,
so `setting <= setting` passes for every value. The interlock therefore
means something under a clocked root and under a running one, and nothing
under a bare pose — which is honest: a pose has no path, and a freeze is a
statement about MOTION.

### 11. What a request reports

`Request` keeps cycle 1's `input`, `by`, `to` and `commits`, and gains:

- **`admitted`** — the travel actually made, in DESIGN units, the units
  `by=` speaks. `by` stays what the caller asked for. Cycle 1's open
  question 2 asked for exactly this field and shaped the object for it.
- **`stops`** — a tuple of `Stop`, empty when the whole travel was made.
  Each names the bounded coordinate by its qualified id, the side
  (`'low'`/`'high'`), the bound EVALUATED at the landing, the coordinate's
  own value there, the driver's value and the fraction of the REQUESTED
  travel. Several constraints met at one landing are several entries of one
  stop, exactly as several relations at one landing are one event.

`record=N` keeps a bounded ring `sim.stops` beside `sim.commits`, which
**lifts cycle 1's refusal of that name**. ADR-108's reason for a separate
ring holds here word for word: a stop is a BOUND OF A COORDINATE, which
stops motion, and a commit is a VALUE THE MACHINE WROTE; a reader counting
strokes must not have to filter out interlocks. The refusal message cycle 1
gives for `sim.stops` — "a clocked model has no clock" — is simply untrue of
stops, and leaving it in place would be the one place this cycle lied.

The vocabulary is ADR-108's and nothing is added to it: `Stop`, `low`/`high`,
the evaluated bound, the fraction.

### 12. The Curta's eight interlocks, answered

The spike's table, with what each becomes under this cycle. None needs a
framework idea this design does not already state.

| Lock | Shape | Level |
| --- | --- | --- |
| `crank_ratchet` | one-argument bound on the crank's own joint, `lambda turn: PITCH * floor((turn - RELEASE) / PITCH)` | number for the request (§4), affine in the crank: SOLVED |
| `crank_lift_stroke` (0–9 mm), `carriage_lift_travel` (0–6 mm) | plain numeric range | affine: SOLVED |
| `carriage_turn_needs_lift` | `Bound` on the carriage's turn reading its lift | comparison over a standing read: a constant, or a jump when the lift is what moves |
| `crank_lift_off_rest`, `carriage_off_rest`, `ring_off_rest`, `selectors_off_rest` | the FREEZE of §4: both bounds read the coordinate's own committed value, gated on the crank's phase | flat at zero while the crank moves; a jump to zero admitted travel while the crank stands off rest |
| `ring_rest_checks` | a bound on the ring reading the ring | `floor`/`ceil` over the moving driver: PARTITIONED, solved per piece |
| `crank_needs_seated_carriage` | `Bound` on the crank's turn reading the carriage's rotation and lift | as `carriage_turn_needs_lift` |

Two of the locks the booklet documents (`selectors_off_rest`,
`crank_needs_seated_carriage`) the spike measured as NOT demanded by its
corpus, and this cycle takes no position on whether the Curta should declare
them. That is the project's audit, in the project's repository.

### 13. Deliberate narrowings, and why each is cheap to lift

- **One driver per request**, so one input is the group (§1). Widening is a
  change to the classification, not to the clip.
- **The clip is not re-computed between events** (§8).
- **A bound may not read a PORT**, refused with ADR-113's own message. A
  port is a calculation, and a bound reads the state.
- **No `Instruction`, no control, no `blocked` command vocabulary.** A
  clocked root has no command surface (cycle 1 §14); a request reports its
  own stop and there is nothing to retire.
- **Nothing is published.** Cycle 1 refuses a clocked model publication by
  name, and this cycle adds a bound the document does not yet carry. Cycle 4
  owns both.

### 14. The ADR plan

ONE NODE ADR, candidate **ADR-126** — "A bound stops a clocked request on
its path" (ADR-125 is the highest accepted). Extracted AFTER implementation,
as the framework-change discipline requires. It will record:

- the clip as a truncation of the request's travel before event location,
  and one moving driver as ADR-108's group (§1);
- the compiled CHAIN from the bank to a bounded coordinate, composed by
  substitution, and why neither a symbolic pose nor `compile_program` is the
  vehicle (§2);
- what the bank must reach, and the refusal of a stop that can never stop
  (§3);
- the reading rule — own coordinate at the request's start, reads along the
  path, a state read admitted — with the FREEZE as the form an interlock
  actually takes and the note's sketch as the measured counter-example (§4);
- the classification, including a JUMPED level partitioned at its own
  surfaces, and the refusal of a curved one (§5);
- the landing on the SATISFIED side, decided by evaluating the level (§6),
  against cycle 1's far side, and why nothing is snapped;
- the direction test as one threshold, `max(0, g(0))` (§7);
- the request as the quantum ADR-109 gave the tick (§8);
- a zero-travel request ADMITTED (§9);
- ONE AUTHORITY for a compiled constraint — the clocked simulation judges,
  during a request, what it compiled, and judges it again over the final bank
  through the chain; a pose that is not a request is judged by the
  enumeration as before; the agreement between chain and pose is a test with
  a stated tolerance and never a runtime refusal (§10);
- `admitted`, `stops` and the lifted `sim.stops` refusal (§11).

No second ADR: nothing here changes the untimed or running reading of a
range, and the ADRs that state those stand unamended.

### 15. Zero behaviour change, as a requirement with a test

- No constraint is compiled for a tree that declares no `State`: the compile
  is entered from cycle 1's clocked construction and nowhere else, and cycle
  1's "a clocked discipline costs a stateless model nothing" already
  requires and tests that no clocked path is entered there.
- A clocked tree with no ranged joint compiles nothing: `_compiled_spans`
  returns an empty table and the request is cycle 1's request, field for
  field, plus an `admitted` equal to its travel.
- The running executor is not touched: not ADR-108's localization, not
  ADR-113's sampling, not `Program`, not `Edge`, not the span table's
  meaning. `_compiled_spans` gains only the NAME of the authority its
  refusals speak for, so that a clocked refusal does not say "the run"; the
  running messages are asserted unchanged, character for character.
- The close-of-enumeration judgement is unchanged, which is what keeps the
  pin tumbler lock and every untimed model exactly where they are.
- §10's MARK is inert everywhere but inside a clocked request's pose: no
  clocked simulation exists for an untimed or running root, nothing marks a
  coordinate there, and both judgement sites take the branch they take
  today. Asserted by the untimed and running bound tests passing unchanged,
  messages included, and by a clocked construction's own pose still raising
  `JointRangeError` for an impossible initial state.

## Risks / Trade-offs

- **A composed chain can be large.** Substitution inlines each law, so a
  long chain of laws that are themselves large produces a large graph. →
  Mitigated by compiling only what the bounds need — the bounded coordinates
  and the coordinates their bounds read, and nothing else in the tree — and
  by evaluating the graph rather than re-composing it per point. The Curta's
  own interlocks are one or two links deep. Measured in §17, and if a real
  model ever meets it, the answer is the running compile's own: keep the
  links as edges and evaluate them in order.
- **A refusal will reject a model somebody wrote.** A clocked project with a
  ranged joint posed by hand in `simulate()` — an author's rest-default
  guard included — is refused at construction (§3). → The message names the
  joint and says to state the relation or drop the range; a ranged joint
  NOTHING binds is admitted as a constant instead of refused, which is the
  decorative case the refusal would otherwise have swallowed; the population
  of clocked models is this campaign's own, and the alternative is an
  interlock that fails open.
- **The clip and the pose could disagree by a float.** → §10 removes the
  question from runtime: during a request the clocked simulation is the sole
  authority for the constraints it compiled, so an ulp of disagreement
  cannot refuse a legitimate request. What is left is a TEST with a stated
  tolerance, which catches the disagreement that matters (a composition that
  simplified) and not the one that does not.
- **One authority means a composition bug fails silently in the small.** A
  chain wrong by a hair now clips a hair early or late instead of raising. →
  The agreement test of §17 samples every fixture's whole path; the bug it
  cannot catch is one smaller than the tolerance, which is smaller than the
  stop is meaningful.
- **A bound read once per request is coarser than one read per event.** →
  §8, with the spike's evidence that no lock in the corpus reads a register,
  and the exact workaround (split the request).
- **Two `Stop` classes, one in `program.py` and one in `clocked.py`.** → The
  fields are ADR-108's in both; a reader of a clocked request meets only the
  clocked one, and a merged class would have to carry a `tick` a clocked
  request does not have.

## Open Questions

Each is recorded rather than silently decided; none blocks this cycle.

**Decided, and no longer open:** whether the clocked simulation becomes the
SOLE AUTHORITY for the bounds it compiled. It does, per §10, on ADR-113's own
ground; the agreement between the chain and the pose is a test rather than a
runtime refusal. **Also decided:** a ranged joint NOTHING binds is admitted as
a constant chain rather than refused (§3), which leaves open only the case
below.

1. **Should the clip be re-computed after each commit?** §8. The evidence
   says no mechanism in the corpus needs it; the cost of changing one's mind
   later is a loop, not a redesign. §17's GATE test states the behaviour the
   answer would change.
2. **An author's REST-DEFAULT GUARD on a ranged joint.** §3 refuses it with
   every other hand binding, because the framework cannot tell a guard's
   constant from a `simulate()` that computes the coordinate. A guard is a
   common shape and the refusal is a one-line fix in the model, so this is
   recorded rather than solved.
3. **Should a request report the constraints it EXAMINED?** A maker asking
   "why did the knob not move" is answered by `stops`; a maker asking "which
   interlocks are live right now" is not, and a readout of the evaluated
   bounds is the natural place for it. Deferred to the cycle that gives a
   clocked model a panel.

## Planned proof

### 16. Fixtures

All geometry-free — no CAD build, no `meshes = True`, a cylinder per dial —
and all beside cycle 1's under `tests/clocked_project/`. Every expected
number is computed BY HAND in the test and never by calling the law or the
bound.

- **`pawl.py` — the PAWL.** Cycle 1's register `Counter` with one addition:
  a `crank_dial` child whose `turn = Revolute(range=(lambda turn: 6 *
  floor(turn / 6), None))`, driven `crank.drives(crank_dial.turn)`. The
  committing relation and the two register dials are cycle 1's, unchanged.
- **`lock.py` — the LOCK.** A root with a `crank` driver, a `selector`
  driver, a `crank_dial` and a `knob` child whose `travel = Prismatic(
  range=(0, Bound(lambda travel, turn: 54 * (turn - 360 * floor(turn / 360)
  < 1), reads=(crank_dial.turn,))))`, with `selector.drives(knob.travel,
  ratio=6)` and `crank.drives(crank_dial.turn)`. This is the note's sketch
  as written, kept deliberately, because it is the fixture that DEMONSTRATES
  §4's correction: it stops the selector off rest AND it stops the crank
  leaving rest with the knob set, which is the behaviour the Curta must not
  have.
- **`freeze.py` — the FREEZE.** The same machine with §4's pair of bounds
  reading the knob's own committed value. It is the acceptance fixture: the
  selector is free at rest, admits ZERO travel off rest, and the crank runs
  its whole travel with the knob set.
- **`gate.py` — the STATE READ, and §8's coarseness.** A crank driving a
  `shutter.travel` affinely (`travel = crank / 100`), a committing relation
  `at = floor(crank / 200)` writing a state `opened`, and
  `range=(0, Bound(lambda travel, opened: 3 + 9 * opened, reads=(opened,)))`.
  From `crank = 0, opened = 0` one `move('crank', by=1000)` is clipped
  against the CLOSED gate and admits 300, while `move('crank', by=200)`
  followed by `move('crank', by=800)` commits the event first and admits
  1000. This is the fixture that discriminates §8 from re-clipping, which the
  PAWL cannot (§8, §17).
- **`outside.py` — a bank standing OUTSIDE a bound.** A `slide.travel`
  driven affinely from a `feed` driver, whose upper bound is
  `Bound(lambda travel, lift: 9 - lift, reads=(plate.lift,))` over a
  `plate.lift` nothing binds. The enumeration does not judge that bound (its
  read holds no value), so `Sim(model, state={'feed': ...})` may stand the
  coordinate at `20`; the chain gives the read its rest constant, so the
  clocked level is a real one. The direction fixture of §7 and §17.
- **`decorative.py` — a ranged joint NOTHING binds.** A clocked root with a
  `plate` child whose `lift = Prismatic(range=(0, 5))` is bound by nothing at
  all — no relation, no wiring, no `simulate()` assignment. Construction
  succeeds, the constraint compiles as a constant, every request admits its
  whole travel and reports no stop (§3).
- **`bounds_unsupported.py` — the refusals.** A bounded coordinate an
  author's `simulate()` binds by hand; a chain through a law that is not an
  expression; a `Bound` reading an unreached coordinate; a `Bound` reading a
  port; a self-read chain; a cyclic chain; a curved level (`range=(0,
  Bound(lambda t, c: sin(c), ...))`); a level whose jump surfaces a long
  request crosses past the maximum.

### 17. Tests, per requirement — every one RED FIRST

Run from inside the worktree with `PYTHONPATH="$PWD"` and the workspace
venv, `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`, ONE JOB AT A TIME.

- **The clip, and that it precedes the events.** The PAWL dragged backwards
  from a settled state stops at the last seated tooth: `move('crank',
  by=-3600)` admits exactly the travel to the tooth, fires NO event, and
  leaves the registers standing — where cycle 1's unpawled `Counter` moves
  the whole −3600. Cycle 1's backwards scenario is kept for the unpawled
  fixture and SUPERSEDED for the pawled one, both asserted in one test so
  the difference is the fixture and nothing else.
- **Events on the clipped path only.** A request whose travel would cross
  three surfaces but whose clip admits one and a half fires exactly ONE
  event, at the same landing the short request fires it at, and the second
  surface is never located.
- **A stop at zero travel is admitted.** The FREEZE fixture with the crank
  off rest: `move('selector', by=3)` returns `admitted == 0.0`, one `Stop`
  naming `knob.travel`, `'high'`, the evaluated bound and the driver's
  value, `commits` empty, `sim.state` identical entry for entry, and NO
  exception.
- **The freeze lets the crank run.** The same fixture with the knob at 18:
  `move('crank', by=360)` admits the whole travel, fires its event, and
  reports no stop — the assertion the note's sketch FAILS, asserted against
  the LOCK fixture in the same test, which stops the crank at phase 1.
- **A plain numeric range stops.** A lift joint declaring `range=(0, 9)`
  driven affinely: `move('lift', by=20)` admits exactly 9, lands ON the
  bound (inclusive), and the pose accepts it.
- **Exactness.** An affine level's landing is asserted against a
  hand-computed value; a KINKED level (`max`) is solved at its breakpoint
  and not searched; a JUMPED level (a comparison against `floor`) lands on
  the last float BEFORE the surface, asserted with `math.nextafter`; a bound
  met exactly at a representable value lands ON it.
- **The direction test.** The OUTSIDE fixture, constructed standing beyond
  its bound: a request inward admits its whole travel, a request back to
  exactly where it started is admitted, and a request that would carry it
  further out admits zero and reports the stop. Its snapshot restores to the
  same place.
- **The own coordinate is read at the request's START, and a ratchet gives
  ONE tooth either way.** The PAWL: a single `move('crank', by=-3600)` and
  ten successive `move('crank', by=-360)` from the same bank give the SAME
  final value — the last seated tooth, hand-computed — because the second
  short request starts ON that tooth, where the bound evaluates to the tooth
  itself and the request admits ZERO travel. Asserted with the per-request
  admissions, so the ONE-then-nine-zeros shape is visible and not inferred,
  and with a start already on a tooth, which admits nothing at all. This test
  states what §4's reading rule does; it deliberately does NOT discriminate
  §8 (that is the next bullet), and §8's rejected alternative would give the
  same answer here — which is why the pawl is not evidence about it.
- **A read moving along the path.** The LOCK: `move('crank', ...)` stops
  where the phase crosses 1, asserted against the hand-computed crank value,
  with the knob standing.
- **A state read, and the coarseness of §8 as behaviour.** The GATE: from the
  same bank, one `move('crank', by=1000)` admits 300 — clipped against the
  state the request STARTED at — while `move('crank', by=200)` then
  `move('crank', by=800)` admits 1000, the commit at the first request's
  event having opened the gate before the second was clipped. Both numbers
  hand-computed, asserted in one test, and named there as the deliberate
  coarseness of §8 rather than a defect. This is the test that discriminates
  §8 from re-clipping.
- **The chain agrees with the pose.** For each fixture, at twenty fractions
  of a request path, the compiled chain's value for every bounded coordinate
  against the value the POSED tree holds there, compared with
  `math.isclose(rel_tol=1e-12, abs_tol=1e-12)` (§10). This is the test that
  keeps the clocked simulation fit to be the sole authority, and it is the
  one that would catch a composition that simplified; it is a TEST and never
  a runtime refusal, because an ulp of disagreement is not a maker's bug.
- **One authority during a request.** A fixture whose clip lands a coordinate
  EXACTLY on an inclusive bound poses without the enumeration judging it: the
  bind-time and close-of-enumeration judgements are asserted skipped for the
  compiled coordinates (by instrumenting the two judgement sites), asserted
  NOT skipped at any pose that is not a request, and asserted NOT skipped at
  all for an untimed and a running fixture of the same shape.
- **A pose that is not a request is judged by the enumeration.** A clocked
  construction and a `state=` each placing a bounded coordinate outside its
  range raise `JointRangeError` from the enumeration, unchanged from cycle 1,
  with the bank and the tree standing. A `restore` poses a bank the same
  simulation once accepted and takes the same path; the assertion there is
  that it is judged on it, not that it fails.
- **A commit out of range refuses the request, by name, through the chain.**
  A fixture whose committed state carries a compiled coordinate outside its
  bound: `JointRangeError` naming the node, the joint, the side, the bound
  the chain evaluates over the FINAL bank and the value it gives the
  coordinate there; the tree is never posed; the bank, the tree and the
  record stand exactly as they did — cycle 1's scenario, re-asserted against
  a clipped request.
- **Reporting.** `admitted` in design units on a scaled driver; `stops`
  entries in the documented shape; two constraints met at ONE landing
  reported as two entries; `sim.stops` under `record=N`, bounded, and absent
  without it.
- **Refusals**, one test each, asserting the message names the joint, the
  side and the offending thing: each row of §3's table, plus the curved
  level and the crossing maximum of §5. Each refusal test names the offending
  DECLARATION in its assertion, so the message a maker reads is the thing
  under test.
- **A ranged joint nothing binds is ADMITTED.** The DECORATIVE fixture
  constructs, compiles its constraint as a constant, examines it for no
  driver, admits every request whole and reports no stop — including from a
  rest value the declared pair does not contain (§3).
- **Zero behaviour change.** The whole existing suite green; the running
  `Gate`/lock fixtures' stop behaviour and messages unchanged; the pin
  tumbler lock's close-of-enumeration judgement unchanged; a clocked fixture
  with no ranged joint behaving exactly as cycle 1's; a byte-identical
  document for an existing published fixture.

### 18. Measurement plan

Measured on the fixtures ONLY, reported as their own numbers and compared to
nothing:

- construction: the time to compile the constraints, and the size (nodes) of
  each composed chain;
- a request with no constraint examined, against cycle 1's recorded request;
- a request with one constraint examined and not violated;
- a request clipped: affine, kinked and jumped levels separately;
- the cost of the chain's evaluation against the cost of one pose of the
  same fixture, which is the ratio the whole design rests on;
- step 6's end-of-request judgement: one level evaluation per compiled
  constraint per request, reported beside the clip's own.

**Not claimed in this cycle:** anything about the Curta. Its clocked model
and its interlock audit are project work in the project's own repository,
and the spike's factor of 35 is that project's measurement, cited as the
requirement's evidence and not reproduced here.
