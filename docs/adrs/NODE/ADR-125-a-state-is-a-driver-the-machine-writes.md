# ADR-125: A State Is a Driver the Machine Writes, Committed at an Event

**Status:** Accepted
**Date:** 2026-09-17
**Amended:** 2026-09-17 by [ADR-128](./ADR-128-a-clocked-root-publishes-its-compiled-machine.md) — the publication refusal is LIFTED (a clocked root publishes version 8), and the containment of a crossing in a request is CLARIFIED: "the right end is inclusive and the left end exclusive" is a reading by fraction that loses an event, and a crossing belongs to the request whose path CONTAINS its LANDING. Everything else — the bank, the request, the exact solve, the far-side landing, the tie rule, the synchronous reads, the path order, the conflict refusal, the atomicity — stands as written.
**Depends on:**
- [ADR-056: Signals, drivers, ports, and stepped simulation](./ADR-056-signals-drivers-ports-and-stepped-simulation.md) — the `Driver` declaration whose five fields, attribute read and qualified id a `State` takes unchanged
- [ADR-099: The enumeration's simulate phases are one tree pass](./ADR-099-the-enumerations-simulate-phases-are-one-tree-pass.md) — the one pass the declared states are collected in, rather than a second descent
- [ADR-106: One law, two readings](./ADR-106-one-law-two-readings.md) — the symbolic inspection of a law applied to one token per source, reused here without its integration half
- [ADR-107: A jump is located inside the tick and subtracted](./ADR-107-a-jump-is-located-inside-the-tick-and-subtracted.md) — the jump node, its level quantity, its surfaces and the exact solve an event is located by
- [ADR-109: A range bound may be an expression evaluated at the committed state](./ADR-109-a-range-bound-may-be-an-expression-evaluated-at-the-committed-state.md) — the law/bound asymmetry a commit law takes the bound's side of
- [ADR-121: A law may read the coordinate it drives](./ADR-121-a-law-may-read-the-coordinate-it-drives.md) — `far_side_of`, the landing walk this reuses, and the self-read it meets in a far simpler form
- [ADR-123: A kink is a cut, and a piecewise-affine quantity is solved](./ADR-123-a-kink-is-a-cut.md) — a kinked event level is cut at its own breakpoints and solved on each piece
**Cites:**
- [ADR-100](./ADR-100-a-relation-may-name-several-coordinates-at-each-end.md) — the `&` group, the tuple driven side and the shaped law arguments the new verb is written in
- [ADR-104](./ADR-104-a-third-time-base-elapsed-seconds-that-never-wrap.md), [ADR-105](./ADR-105-the-run-owns-the-coordinates-and-binds-them.md) — the elapsed time base and the run's own bank, neither touched here
- [ADR-110](../EXPORT/ADR-110-the-compiled-program-is-published-in-the-document.md) — the version ladder whose rule the publication refusal honours
- [ADR-124](./ADR-124-only-what-moves-along-a-tick-s-path-is-evaluated.md) — path evaluation, which a commit deliberately does not use: a commit is a Python call, not a graph walk
**Amends nothing.** In particular it does **not** amend ADR-121: a state read by the
relation that commits it is that decision's self-read met under a discipline where the
read is CONSTANT between events, so ADR-121's two-layer walk, its branch reading at a
piece's left end and its landing of the driven coordinate are all simply not reached.
The rule is unchanged; this is the easy case of it.
**OpenSpec change:** `declare-the-state` (archived at
`openspec/changes/archive/2026-09-17-declare-the-state/`)
**Originating project:** `projects/Calculators/Curta-Type-I-3x`, branch
`direct-operation`, HEAD `9fb725f`; the project-level spike is its worktree
`WTs/clocked-spike`, commits `0968563` `a56937e` `bcf2017`, recorded in
`simulation/docs/clocked-spike-2026-09-16.md`.

## Context and Problem Statement

The framework had two state disciplines and no third. An **untimed** root has no
memory at all: a pose is a function of the drivers, so a request cannot carry
anything forward and a machine that counts has to be counted for it by hand. A
**running** root (ADR-104 to ADR-109, ADR-113, ADR-121, ADR-122) retains every
coordinate of the tree and integrates every law at a fixed cadence, which is the
generality that lets a mechanism's arithmetic EMERGE from its parts — and which
costs what generality costs.

The originating project carries one machine modelled both ways.
`fast_curta` is a closed form, one expression-DAG evaluation per pose, fast in
Python and in the browser — and it does not OPERATE: turning the crank past a
revolution carries nothing, so the maker edits the registers by hand.
`operating_curta` declares `Time.running()`, operates, and produced the findings
ADR-121, ADR-123 and ADR-124 were cut from — and after the `curta-speed` campaign
it still costs about **0.73 s per 0.1 s Python tick** and about **40 ms per crank
tick in the browser**.

The requirement note `workflow/docs/clocked-machine.md` names what the machine
actually is: a **clocked** one. It has a few retained values, closed-form
positions between events, and a commit of the retained values at each event; its
interlocks hold the selectors, the carriage and the clearing ring while the crank
is off rest, so nothing about its state changes except at the end of a stroke.
The running executor pays, every tick, for a generality this machine does not use.

**A project-level spike measured that, with no framework change.** It wrapped the
fast model in an ordinary-Python harness with two committing relations in the
note's shape and replayed eighteen scenarios against a recorded `OperatingCurta`
oracle (574 ticks, 439.2 s):

- the clocked model reproduces the operating model's registers at **every stroke
  end** of every scenario in which the machine is operated as the manufacturer's
  booklet says it must be;
- fed from the committed state, the project's own `dial_positions` reproduces the
  operating model's actual dial angles **to 0.000000 digits** at every in-corpus
  read, mid-stroke reads included, except after a clearing sweep where it differs
  by 0.0139 digits — exactly the zero-capture band the project's own
  `clearing_travel` prescribes. "Between events nothing is retained" is measured,
  not assumed;
- one clockwise revolution costs the operating model 15.3 s and the clocked model
  0.438 s at the same 20 samples, a factor of **35**; one commit through the
  Curta's own `calculate` is **26 microseconds**, so the commit is not the cost —
  the pose is, and the pose is the fast model's existing per-pose cost, unchanged;
- every interlock the machine needs is a project-owned `Bound` on a joint, eight
  of them, each quoted from the booklet. The framework needs no new lock idea.

**The shape of the answer was constrained before this cycle began.** On
2026-09-13 the pilot rejected the `running(r)` / `r.state` / `r.event` / `r.equal`
protocol — a per-relation protocol with event objects handed into laws
(`workflow/open-run-simulation/design.md`, "Decision 2026-09-13"). Whatever
carried the memory had to be declared in the places the API already has, and the
author had to go on writing the closed forms they already write.

## Decision Drivers

- The machine's own decomposition is **two axes** — time base × state discipline —
  where the API tied them. Adding memory must move ONE square of that table and
  touch no other.
- A clocked model's determinism claim is STRONGER than a run's: a snapshot is
  inputs plus states, a replay is the request history, and nothing depends on a
  `dt`. Events must therefore be located EXACTLY, never searched.
- The solver must introduce **no new locator, no new knob and no new tolerance** —
  ADR-107's three tolerances are the whole budget, and a clocked path must not
  even add a use of them.
- A tree that declares no state must be unchanged in behaviour, in published
  bytes and in cost, structurally rather than hopefully.
- Nothing this cycle admits may publish a document a consumer would animate
  wrongly (ADR-110's rule).
- Running mode is the EVIDENCE mode and stays untouched: a machine whose
  arithmetic is composed from local laws can fail to add, and that is where the
  Curta's framework findings came from. Clocked is the program the pilot compiles
  from it once the parts have proven it.

## Considered Options

**What carries the memory.**

1. `r.state` / `r.event` inside a law. Rejected by the pilot on 2026-09-13, and
   not reopened: it puts a mutable protocol object into every project's laws.
2. A retained COORDINATE, i.e. tell projects to use ADR-121's self-read. It is the
   running mode, and it costs the running mode's tick. It is what the originating
   project already does and what it is too slow in.
3. **A declaration beside `Driver`, and a verb beside `.drives`.** Chosen. The
   grammar exists; what is new is a value the MACHINE writes.

**What a `State` may be declared on.** The note says "a declaration next to
`Driver` on a root assembly". Read strictly that refuses `carriage.result.units.digit`,
which is the shape the spike's per-digit clearing events need. **Any assembly, by
the driver's own qualification rule**, chosen: forcing a state to the root would
make its id lie about where the value lives. The DISCIPLINE stays a property of
the root — a tree is clocked when anything in it declares a `State`, exactly as a
tree is driven when anything in it declares a `Driver`.

**The name.** `Memory`, `Register`, `Retained` were weighed against the collision
with `set_state` and `sim.state`. `State` kept: the collision is half a feature (a
state IS in `sim.state`) and half a hazard (`set_state` refuses one), and the
hazard's right resolution is the refusal MESSAGE, not a different word.

**What `at` may be.** The note says `at` "returns an integer-valued expression".
Integer-valuedness is not a structural property the framework can check, and
checking it by sampling is the search this design exists to refuse. **ONE jump
node of ADR-107's own vocabulary** chosen — `floor`, `ceil`, `sign` or a
comparison — because it IS checkable, it yields the level quantity and the
surfaces for free, and both of the spike's relations are one node. A curved level
is REFUSED at construction rather than bisected: the run bisects to `1e-12` and
says so, while a clocked model's whole value is that its events are exact.

**Which edge fires.** The note assumed both edges fire and the law neutralises the
falling one. The spike **measured that false**: with `at = floor(crank / 360)`,
no pawl and the note's own additive law, dragging the crank backwards from one
completed revolution commits a SECOND addition, **9 → 18**. An additive law
cannot neutralise. Three alternatives were weighed and rejected — a sign handed to
the law (the rejected protocol's shape, and every law grows an argument it does
not use), a `direction=` keyword (no mechanism in the corpus discriminates it), and
relying on a project `Bound` to make the reverse unreachable (that bound is the
next cycle's, so until then the default would be measurably wrong). **Rising only**
chosen, because it is fully expressive: a mechanism that commits on the other edge
negates its own level, `floor(-crank / 360)`, which is exact and written in the
model.

**How two relations at one point are told apart.** The run merges crossings closer
than `_CROSSING_TOLERANCE`, which is stated in TICK-FRACTION units. Carried onto a
request path that tolerance would make one `move('crank', by=3600)` merge events
that ten `move('crank', by=360)` requests keep apart. **Identity of the far-side
landing float** chosen: under a clocked root there is no tick and no fraction to
scale by, every crossing is solved, and identity of a float is decidable.

**How many relations may write one state.** The first ratified draft refused a
second committing relation naming a state already written, at class definition and
again across the tree. **The originating Curta is inexpressible under that rule**,
and the review of the implementation found it: a register digit is written at the
STROKE END (the arithmetic of the crank turn) and again at the CLEARING REACH (to
zero, as the clearing ring sweeps past it) — two events, two inputs, and one
relation states one `at`. The rule's own rationale, "two answers for one value at
one event", bites only when both fire at ONE event. The design was amended on
2026-09-17 before the implementation followed it.

**Where publication is refused.** `serializer.symbolic_document` is the walk
`solid build`, `solid develop` and `solid export` pass through and where the
running-root control refusal lives — but `solid snapshot --renderer web` stages
its own baked document from `serialize_node` + `document_body` without entering it.
**`document_body`**, the one function all four producers pass through, chosen.

## Decision

**A `State` is a driver the machine writes.** `State(default, range=None,
unit=None, dtype=None, scale=None)` (`solid_node/simulation/state.py`) is declared
as a class attribute on any assembly, takes exactly `Driver`'s five arguments with
exactly their meanings — `range` is presentation metadata that clamps nothing,
`dtype=int` is a whole number of NATIVE units — is read `self.units` in
`simulate()` and in a law exactly as a driver's value is, and qualifies by exactly
a driver's rule. **A tree in which anything declares one is a CLOCKED model.**

Everything that distinguishes it from a driver is about WHO WRITES IT, and each
refusal is made where its own facts exist: `set_state` refuses one BY NAME and
names the relation that writes it; an `Instruction` target and a `Button`/`Turn`/
`Slide` input refuse one; `.drives` refuses one as its driven end; a state under
`Time(loop=)` or `Time.running()` is refused where declared defaults are bound; a
state nothing writes is refused at simulation construction. A state is settable
exactly twice, and both are session setup rather than operation — `Sim(model,
state={...})` and `sim.restore(saved)`.

**A grouped source COMMITS states at an event.**

```python
(crank & result & turns & operand & subtract & shift).commits(
    (result, turns), at=strokes, law=registers)
```

The verb lives beside `drives` on `CoordinateRef` and `Coordinates`
(`motion/couplings.py`), so the `&` group, the flat chaining, the tuple driven
side and the missing-parentheses refusal are the ones the API already has; read
off the class the declaration is a `Commitment`, read off an instance it is that
instance's `CommitmentRecord`. **Both factories follow the existing law-factory
protocol** — called exactly ONCE at realization with the realized `(sources,
targets)` owners, shaped as `_law_argument` already shapes an end, returning a
callable over the sources' VALUES, one positional per source in written order. No
event object, no `r`, no second face on a law, no mutable state in a project's
Python.

Refused at class definition, each naming the relation as written: a target that is
not a `State`; a target named twice among the targets, **decided by the reference's
own key — the child path plus the local name — and never by the local name**, which
is what makes a register of seventeen identical wheels one written line; a source
that is not a `Driver` or a `State`; `at` or `law` missing; a `ratio=`/`offset=`;
a `.repeat()` broadcast on either side.

**Sources are drivers and states, and nothing else.** A port, joint coordinate or
derived coordinate is a calculation the untimed enumeration recomputes from the
bank on every pose; reading one inside `at` would cost a pose per sample or a
compiled program over the whole tree — which is the running root's job and exactly
the generality the clocked discipline exists not to pay for. Neither of the
spike's two relations reads anything else.

**`at` is ONE jump node, and its level is SOLVED.** Along a request's path only
one input moves. The node's level graph is bound with every standing source
substituted as a number and classified by `_shape_of` over the residual: `affine`
— every surface strictly between the level's endpoint values solved by one division
(`JumpPlan._solved`); `kinked` — cut at ADR-123's own breakpoints and each piece
solved the same way; **curved** — refused at simulation construction by name,
naming the relation, the driver whose motion curves the level and the primitive.
The classification is decidable at construction precisely because only a DRIVER
can move along a request path: a state is constant between events. **A relation no
driver can reach** — every source a state, so its level table is empty and it can
never fire — is refused at construction for the same reason a state nothing writes
is: a declaration that can never do anything is a mistake in the model, not a
machine.

**Only RISING steps fire**, read from `_branch_of` at the midpoint of the piece
before the crossing and at the LANDING after it. (The after-branch is read at the
landing rather than at a right-hand midpoint because a crossing at the request's
own endpoint — the one `move('crank', by=360)` with `at = floor(crank / 360)`
must fire — has no right-hand piece; the landing is by construction the nearest
representable point of the piece the path is going into, and for a non-endpoint
crossing the two readings cannot differ.)

**The landing is ADR-121's far side, by ADR-121's own walk.** A crossing gives a
fraction `t*`; the input's value there is walked to the nearest representable
value on the FAR SIDE of the surface by `program.far_side_of` — the `_Walk` method
extracted to a free function, body unchanged line for line, so the clocked solver
lands a path by the SAME walk and not a second one. Membership of a float in the
far side is decided by EVALUATING the jump node's branch there, never by comparing
the float to the surface. That one float is used for both the event's reads and
the resumption of the remaining path, so one event can never fire twice.

**Ties are IDENTITY of the landing.** Two relations fire at one synchronous event
exactly when their far-side landings are the SAME float; otherwise they are two
events in path order, and the second reads what the first committed. Two surfaces
one ulp apart are two events. **No tolerance decides it and none is introduced:**
`_CROSSING_TOLERANCE` goes on doing inside `_solved` and `_KinkCuts` exactly what
it does today, and the clocked solver adds no new use of it.

**A commit is evaluated at ONE POINT, so a jump is a jump.** `law`'s expression is
inspected exactly as ADR-106 inspects a running law — applied to one symbolic
token per source, the graph walked for raw text and for calls outside
`SYMBOLIC_BUILTINS`, through the extracted `program.checked_expression` — with one
difference, and it is ADR-109's difference: a commit law is evaluated at a point
and never integrated, so **`floor` means `floor`, `%` means `%`, a comparison means
a comparison, and nothing is subtracted.** There is no jump plan, no skeleton and
no `_only_jumps` refusal, which is why the Curta's `calculate` — integer arithmetic
with `%` and comparisons throughout — is expressible as a commit law and is not
expressible as a running law. The inspection happens once, at realization; at
request time the executor CALLS the ordinary Python callable with the bank's
numbers, positionally, in written order. No graph evaluator, no substitution pass,
no symbolic arithmetic — that is the spike's 26 microseconds per commit. The shape
is nevertheless checked NOW because cycle 4 publishes `at` and `law` as expression
graphs, and a project must not write a law the framework accepts in Python and the
browser then cannot be given.

**Reads are SYNCHRONOUS and PRE-EVENT; commits are in PATH ORDER.** Every relation
firing at one landing reads the bank as it stood BEFORE the landing — including a
state the same event writes and a state a different relation writes at the same
event — and their targets take their results together, so the order of two
relations at one event cannot be observed at all. (Sequential evaluation in
declaration order was rejected: it makes the order of lines in a class body
load-bearing and invisible.) Between events the order is the path's: the earliest
crossing on the remaining path is taken, committed, and the solve resumes from its
landing.

**`at` may read the state it commits**, and the spike's finding 2 is not optional:
the Curta's per-digit clearing threshold is `start_p + pitch_p * (10 - digit_p)`,
a function of the committed digit, where the note's sketch writes a constant the
measured geometry does not admit. This is ADR-121's self-read in its easy form —
the read is constant BETWEEN events, so there is no dependence on a coordinate
moving along the path, no two-layer partition, no walk inside a piece and no
landing of the driven value. The event surface moves only AT the event, which is
exactly why the solver re-locates on the remaining path after each commit rather
than partitioning the whole path once.

**SEVERAL relations may write one state; two of them at ONE event may not.** A
state may be the target of several committing relations, in one class body or
across the tree — the Curta's digit, written at the stroke end and at the clearing
reach, is the evidence, and the class-definition and construction refusals of a
second writer are therefore gone. What is refused is two answers for one value at
one landing, and it is refused by the **REQUEST**, which is where a landing exists:
`Clocked.move` records per event which relation wrote which qualified id, and a
second answer raises naming the state, both relations as written and the landing.
The conflict cannot be decided earlier: whether two levels land on the same float
depends on the bank and on the path, and the same identity test decides ties and
conflicts alike.

**A clocked `Sim` takes no `dt`.** `Sim(model)`; a `dt` over a clocked root is
refused by name and its omission over any other root is still refused as it is
today. `sim.move(input, by=|to=)` moves ONE declared driver along a straight path
and returns a `Request` naming the input, the travel and the tuple of `Commit`
records it fired — each carrying the relations, the fraction of the path, the
input's value at the event and the targets with their new values (one entry per
EVENT, so relations landing on one float share one). `sim.state` is the readout;
`snapshot`/`restore`/`reset` and `state=` are the session-setup path. The cadence
surface — `run`, `at`, `every`, `time`, `tick`, `rate`, `trigger`, `crossings`,
`stops`, `commands`, `program` — is refused BY NAME over a clocked root, each
message naming the cycle that may give it meaning.

**The bank is native, and a commit rounds once.** A commit law reads native values
and RETURNS native values, and its return is NOT passed through `Driver.native()`
— which converts a DESIGN-unit target by dividing by `scale`, and would divide an
already-native value a second time. `move`'s `by=`/`to=` remain the one
design-unit surface. A `dtype=int` state is rounded to nearest ONCE, at the commit;
a state with a `scale` and no `dtype` is committed exactly as the law returned it.

**A request costs NO pose.** `at` and `law` read only banked values, so nothing
between locating the first event and the last commit touches the tree; the tree is
bound ONCE, at the end.

**A refused request commits NOTHING, and that includes the FINAL POSE.** A curved
level that escaped the construction check, more than `_MAX_CROSSINGS` events, a
law returning the wrong shape, two relations writing one state at one event, **or
a final pose the tree refuses** all leave the bank, the tree and the record exactly
as they stood. The executor poses the tree over the WORKING bank and assigns it
only if the tree accepted it, re-posing the previous bank and re-raising on
failure; `restore()` has the same shape. (The first implementation left the bank
advanced past a refused pose, so the next request would have solved its path from
a bank the geometry had already rejected.)

**Between events nothing is retained.** A pose under a clocked root is the existing
untimed enumeration over the drivers, the states and nothing else. `time` is not
in the bank: a clocked root declares no time base, so a bound pose leaves `time`
the untimed symbolic `$t` through ADR-008's fallback exactly as the build path
does, and a `simulate()` reading `self.time` sees precisely what it sees under an
untimed root today. Nothing about `time` changes, and that is the point.

**Publication is refused, loudly.** A tree that declares a `State` is refused by
name in `serializer.document_body` — the one function `solid build`, `solid
develop`, `solid export` and `solid snapshot --renderer web` all reach — naming the
states and saying the document version that carries them is not defined yet.
Publishing a version-7 document with the states rendered as their initial values
was rejected outright: the geometry would be correct only at the initial state and
would silently stop following the machine, which is precisely what ADR-110's
version ladder exists to refuse. `render()`, `assemble()`, `build_stls()`, `solid
test` and an OpenSCAD snapshot are untouched, so a clocked model can still be
tested and photographed.

**A stateless model pays nothing, structurally.** States are collected in the walk
`qualified_declarations` ALREADY makes — `drive_tree` gained a `collected=` dict and
`qualified_declarations` returns three tables instead of two — so no tree pass is
added; every clocked code path is entered only when that collection is non-empty;
and `solid_node.simulation`'s exports stay lazy, so a project that names no `State`
imports no new module.

## Consequences

- **The Curta's clocked model is sayable, and this is the cheap square of the
  table.** Time base × state discipline now reads: untimed × none is today's pose,
  untimed × **memory** is this decision, looping × memory is refused by name (a
  loop replays from zero, so it replays every commit and the state climbs across
  loops), elapsed × memory is cycle 3, and elapsed × integrated is `Time.running()`,
  untouched. What the project owes in return is stated rather than hidden: an `at`
  the framework can solve, and a model whose positions between events really are a
  closed form.
- **Measured on the fixtures this cycle built, and compared to nothing else.** One
  pose of the register fixture 60.0 us; one commit **0.9 us**, 1.5 % of a pose; a
  request with no event 81.9 us, with one event 107.1 us, with ten events 428.2 us
  — so ten events add 320 us, about 32 us per event of locating and committing, and
  **no further pose**. The design's speed claim is measured on the thing that was
  built. The spike's 26 us per commit through the Curta's own `calculate` is an
  order-of-magnitude sanity reading for that number and not a comparison, and the
  spike's factor of 35 is the project's measurement, cited as the requirement's
  evidence and deliberately not reproduced here.
- **A stateless model is indistinguishable, and its document is byte-identical.**
  Seconds per pose under the base commit `81c5364` and under the implementation:
  43.9 / 43.7 / 48.9 us against 44.8 / 42.5 / 42.0 us, the ranges overlapping and
  neither side consistently faster. The same model's document body `diff`s
  IDENTICAL, and that literal is pinned in a test so a later change cannot move it
  silently. One structural walk was added and named —
  `tree_declares_states(node)`, asked by `Sim.__init__` and `document_body`
  because a clocked root takes no `dt` and the question must be answered before
  anything is bound — of the shape `tree_declares_drivers` already has; a counter
  on `simulation.clocked` is asserted ZERO across a stateless model's
  construction, pose, `Sim(node, dt)` stepping and publication.
- **The solver is a consumer, not a second engine.** It reuses `JumpPlan._solved`
  and `_surfaces` (ADR-107), `_shape_of` and `_KinkCuts` (ADR-123), `far_side_of`
  (ADR-121), `checked_expression` and `SYMBOLIC_BUILTINS` (ADR-106) and
  `_MAX_CROSSINGS`. Three small extractions made that possible without
  duplication: `_Walk._far_side` became the free `far_side_of` (the method is now
  three lines calling it), `_graph_of`'s text-and-vocabulary walk became
  `checked_expression` (shared WITHOUT the jump plan, the skeleton or the
  `_only_jumps` refusal — which is the asymmetry itself), and `_too_many` attaches
  its count to the error it builds. **The clocked path introduces no tolerance at
  all.**
- **A `State` under `Time.running()` is DEFINED and NOT implemented.** Under a run
  a value committed at an event is a self-read law whose value changes only through
  a switch — exactly what ADR-121 admitted, and exactly how the operating Curta's
  wheels already work — so such a state compiles to that self-read switch and
  becomes one retained coordinate among all the others. It buys no speed: every
  other coordinate is still integrated at the cadence. The meaning is fixed now for
  PORTABILITY, so a project writes "this register is committed at the stroke end"
  once and has it mean the same under both roots; construction refuses the
  combination by name until a project needs it. **`Time.running()` itself is
  untouched by this decision — not its compile, not its tick, not its document.**
- **A `Bound` does not clip a request path, and that is the next cycle.** A
  violated bound stays the untimed `JointRangeError` on the pose the request ends
  at, ADR-113's close-of-enumeration judgement included. What it costs is precise:
  a request that would drive a mechanism through a stop is REFUSED WHOLE and
  commits nothing, rather than stopping where the machine stops and keeping what it
  committed on the way. The Curta's eight interlocks are all of this shape, so the
  Curta's clocked model is not complete until that cycle. The solver is written so
  the clip is a truncation of `delta` before the first location, not a second
  locator.
- **A clocked project cannot be published or viewed until cycles 4 to 6**, and the
  refusal is the honest form of that. Cycle 4 owns the document that carries a
  state, which is why `at` and `law` are checked as expression graphs now even
  though nothing in this cycle walks them to compute a value.
- **Two writers at one event are found by RUNNING, not by reading.** The conflict
  is a property of the bank and the path, so a model can carry a guaranteed
  conflict and only meet it on the request that reaches it. A structural pre-check
  — two relations on one input with the same level graph — is possible and is
  recorded as a follow-up wanting its own evidence, not as a gap this decision
  leaves open by accident.
- **Deliberate narrowings, each cheap to lift and each recorded in
  `workflow/warts.md`:** one driver per request (the exactness classification is
  stated against one moving input; the machinery integrates a joint source space
  perfectly well); no broadcast `commits` (a `.repeat()` child that owns a banked
  value is already refused under a running root, and it is that problem); no
  `Instruction` and no control under a clocked root (both state a duration or issue
  a request through the run's command surface); no port as a source; no `%`-rooted
  or compound `at`; and no fold-commit — the spike measured that per-digit
  comparison events cover partial clearing in BOTH directions with no held value,
  and that the one gap a fold would close is a rest the manufacturer's booklet
  forbids.

## Promotion

Accepted 2026-09-17 at the cycle's adversarial review. The review ran a
Curta-shaped probe — three wheels of one class, with carry and per-digit clearing —
against the uncommitted implementation and returned four findings, all closed
before acceptance: the two-writers refusal keyed on the LOCAL NAME and so refused
three children of one class (removed, and the amendment above is what replaces it);
several relations must be able to write one state (the ratified design was amended
first, then the implementation followed it red-first); atomicity must include the
final pose; and a committing relation no driver can reach must be refused rather
than left silently inert. The implementation's own record, including the red log,
the mutation evidence for ten refusals whose tests were written green, and every
measurement quoted above, is `evidence.md` inside the archived change.
