# ADR-127: A Clock Is a Banked Value, and an Event on It Is an Event

**Status:** Accepted
**Date:** 2026-09-17
**Amended:** 2026-09-20 by [ADR-133](./ADR-133-running-time-drives-retained-motion-with-independent-admissions.md) — the blanket refusal of a clock as a `drives` source is lifted for the running root's own declaration only; elapsed-clock requests and commitments remain unchanged.
**Amended:** 2026-09-17 by [ADR-128](./ADR-128-a-clocked-root-publishes-its-compiled-machine.md) — the banked clock is PUBLISHED as the free name `time` under an elapsed clocked root, and the "no tolerance reaches a clocked path" claim is CORRECTED to "introduces no NEW use": a clocked path does REACH the crossing tolerance, when a kinked event level's crossings are merged and when a jumped constraint level's cuts are folded, which is why the document publishes it under `limits`.
**Depends on:**
- [ADR-104: A third time base, elapsed seconds that never wrap](./ADR-104-a-third-time-base-elapsed-seconds-that-never-wrap.md) — the one-field `Time` declaration, its constructor-per-base shape and its `mode` property, which the third spelling takes exactly; this decision EXTENDS it and does not amend it
- [ADR-125: A state is a driver the machine writes, committed at an event](./ADR-125-a-state-is-a-driver-the-machine-writes.md) — the clocked root, its bank, its request, its exact event solve, its landing rule and its refusal temperament, all of which the clock joins unchanged; its own two-axis table is what this decision is owed by
- [ADR-107: A jump is located inside the tick and subtracted](./ADR-107-a-jump-is-located-inside-the-tick-and-subtracted.md) — the jump node, its level quantity and its surfaces, which an `at` in the clock is classified and solved by exactly as an `at` in a driver is
- [ADR-123: A kink is a cut, and a piecewise-affine quantity is solved](./ADR-123-a-kink-is-a-cut.md) — `_shape_of` and `_KinkCuts`, the structural classification the clock is added to as one more moving input
- [ADR-121: A law may read the coordinate it drives](./ADR-121-a-law-may-read-the-coordinate-it-drives.md) — `far_side_of`, the one landing walk, which lands a release on the clock as it lands one on a driver
**Cites:**
- [ADR-126: A bound stops a clocked request on its path](./ADR-126-a-bound-stops-a-clocked-request-on-its-path.md) — the clip this decision declines to give a time request, the end-of-request judgement it keeps whole, and the chain compile it TIGHTENS with the general free-name rule ADR-126 promised
- [ADR-105](./ADR-105-the-run-owns-the-coordinates-and-binds-them.md), [ADR-106](./ADR-106-one-law-two-readings.md) — the running mechanics ADR-104's base carries, which this decision deliberately does not reach
- [ADR-108](./ADR-108-a-range-is-a-physical-stop-that-stops-the-connected-group.md) — a declared range as a MECHANICAL stop, which is the reason a clock is not stopped by one
- [ADR-113](./ADR-113-a-bound-may-read-other-coordinates.md) — `reads=` names COORDINATES, and a clock is not one, so a bound's argument list is untouched
- [ADR-110](../EXPORT/ADR-110-the-compiled-program-is-published-in-the-document.md) — the version ladder that will have to carry a published clock, in the document cycle
**Amends nothing.** In particular it does **not** amend ADR-104: that decision
stands as written for the RUNNING base, and the third spelling is built beside
the second in the shape ADR-104 chose. ADR-105, ADR-106 and ADR-107 stand
whole — `Time.running()` is untouched, not its compile, not its tick, not its
document, not its meaning. ADR-125's bank, solver, landing, ordering, conflict
rule and publication refusal are joined by the clock, not rewritten; ADR-126's
clip, its threshold and its end-of-request judgement are unchanged, and the one
thing this decision changes in its implementation is the general refusal
ADR-126's own text already promised.
**OpenSpec change:** `time-without-running` (archived at
`openspec/changes/archive/2026-09-17-time-without-running/`)
**Originating project:** `projects/Calculators/Curta-Type-I-3x`, branch
`direct-operation`, HEAD `9fb725f`. **The Curta does not owe this cycle and
this cycle costs it nothing:** the machine the clocked discipline was cut from
has NO clock — it is operated, its events are located on the crank and the
clearing ring, and nothing in it is a function of elapsed seconds. What owes
this decision is ADR-125's own two-axis table, and the evidence is the pendulum
fixture built for it (`tests/clocked_project/pendulum.py`).

## Context and Problem Statement

ADR-125 gave a root MEMORY with no clock, and stated the decomposition its
whole design rests on as a table of two axes — TIME BASE against STATE
DISCIPLINE. One square of that table was unsayable:

| time base | none | memory | integrated |
| --- | --- | --- | --- |
| untimed | poses today | ADR-125 | — |
| looping (`Time(loop=)`) | the clocks today | refused by name | — |
| elapsed | — | **this decision** | `Time.running()` |

**elapsed × memory** is a machine with a clock and memory and no integration,
and the requirement note names it in one sentence
(`workflow/docs/clocked-machine.md`, "Time without running"): *a pendulum is a
formula of elapsed time; a counter beside it is a state variable committed
when the pendulum's phase, an expression of time, crosses its release. Events
on time and events on inputs are the same kind of event.*

The framework could not say it, and the reason is structural rather than
accidental. ADR-104 made "elapsed seconds that never wrap" declarable only as
HALF of `Time.running()`, whose other half — ADR-105's bank of every
coordinate, ADR-106's integrated law, ADR-107's tick — is precisely the
generality the clocked discipline exists not to pay for. A project that wanted
a pendulum and a counter had to buy the run, at the cost ADR-125 already
measured on the originating machine: about 0.73 s per 0.1 s Python tick.

**A decomposition is not honest while one of its squares is unsayable.** That,
and the viewer's timeline — which is a clock, and which must be able to
execute a clocked document that has one (cycle 6) — are what this decision is
owed by. The originating project is owed nothing, and gets nothing, and is
named here so the requirement does not lose its context.

## Decision Drivers

- **The two axes must become genuinely independent, not tied at a new place.**
  ADR-125's table is the design's own claim about what a machine is; a base
  admitted only under memory, or a discipline selected by a base, would leave
  the table a coincidence.
- **`Time.running()` is untouched. That is a pilot constraint, not a
  preference.** `Time.elapsed()` must not become a route into the running
  mechanics, and nothing about the running compile, tick, document or corpus
  may move.
- **Events on time and events on inputs must be THE SAME EVENT** — one solver,
  one ordering, one conflict rule, one exactness claim — or a project learns
  two event vocabularies for one machine.
- **No new locator, no new knob, no new tolerance.** ADR-125's exactness claim
  is stronger than a run's, and a clock is exactly where a tolerance would be
  tempting.
- **A model that declares no `State` must be unchanged in behaviour, in
  published bytes and in cost**, structurally rather than hopefully — ADR-125's
  own driver, restated because a third base reaches every producer that reads
  a declaration.
- **A declaration the framework cannot follow is a mistake in the model**
  (ADR-125, ADR-126). A refusal belongs where the facts that decide it are.

## Considered Options

**How the third base is spelled.**

1. A second declaration class, `Elapsed()`. Rejected for ADR-104's own reason:
   every consumer of `declared_time(cls)` would learn a second type where a
   `mode` string costs it a comparison.
2. `Time(elapsed=True)`. Rejected for ADR-104's own reason: a flag rather than
   the thing it declares.
3. A second dataclass FIELD beside `loop`, to tell the two unwrapping bases
   apart. Rejected because `loop` is the one field every producer reads and a
   second would have to be exclusive with it and would reach all four of them.
4. `Time.elapsed()`, a constructor per base, the bases told apart by a PRIVATE
   marker read only through `mode`. Chosen.
5. Making `Time.running()` sugar for "elapsed plus integrated", as the
   requirement note floats. Rejected outright: it changes `Time.running()`,
   which is the one thing this cycle may not do.

**What the elapsed base selects.**

1. **The base selects the executor** — `Sim(model)` takes no `dt` over any
   elapsed root. It reads well ("elapsed means requests, not cadence") and was
   rejected twice over: it makes a declaration silently change the simulation
   surface of a stateless model, and it makes ADR-125's ratified sentence "no
   clocked code path is entered for a tree whose state collection is empty"
   false.
2. **Refuse `Time.elapsed()` on a stateless root, by name.** Rejected: it
   would make a base's admissibility depend on a walk of the whole tree for
   `State` declarations, would refuse a model the instant its author removed
   his last `State`, and would state a rule the two-axis decomposition has not
   got.
3. **Nothing. The state discipline alone selects the executor.** Chosen.

**How a clocked pose is given the clock.** A new `clock=` parameter on
`drive_tree` was rejected — it says in a shared walk's signature what the
walk's existing `visit` hook already says, and which the enumeration already
uses that way. `node.set_state(time=seconds)` after the walk was rejected on
cost: it re-simulates the tree, so every request would pose TWICE, which is
about a third again on the short requests a maker actually makes (measured
below).

**Whether a time request is clipped by a bound.** Admitting the clock as a
chain free name and clipping a time request like a driver request is coherent,
and it is where a later cycle goes. It was rejected HERE because it is two
changes and not one: renaming the animation symbol to a bank id is the easy
half, and the hard half is that a level moving with the clock must be
classified, solved and given a direction test, whose `h = max(0, g(0))`
reading ADR-126 already records as contested. Half of it would ship a clip
that stops a clock sometimes.

**A second verb, `sim.advance(seconds)`.** Rejected: it would carry its own
return type, ordering rules, recording and documentation, all copies of
`move`'s, and it could not say "advance to exactly `t = 10`" without a second
argument that is `to=` under another name.

## Decision

**`Time.elapsed()` is a third spelling of `Time`, and the time base and the
state discipline are INDEPENDENT AXES of which only the state discipline
selects the executor.**

### The spelling

`Time.elapsed()` is ADR-104's shape exactly: `Time` keeps its ONE field
`loop`, a constructor per base tells the bases apart, and `mode` is a
property. The elapsed declaration is a frozen instance whose `loop` is `None`
and whose `mode` reads `'elapsed'`, built without `__init__` exactly as
`running()` is and for the same reason. What distinguishes it from the running
base is a PRIVATE marker and not a field, so no producer learns anything:
`__set_name__` is untouched, and the third base obeys the same declaration
rules as the other two — the name `time`, on an `AssemblyNode`, on the root of
the tree it is read in. `Time()` with no base goes on raising its `TypeError`,
whose message now names three spellings.

**Every consumer that reads `.loop` keeps getting `None` and behaves as it
does for the running base** — `serializer.animation_block` publishes no `loop`
key, `assembly.read_time` leaves `$t` unscaled, `manager.snapshot` keyframes
the fraction. **Every consumer that reads `.mode` compares it to `'running'`**
— `serializer.running_root`, `Sim.__init__`, `couplings.run_owned`,
`assembly._coordinate_delivery`, `manager.snapshot`, and
`enumeration._decide_block_membership`, the running-only block pre-pass — so
each of them treats an elapsed root as NOT running, which is what it is. Both
lists were verified against the source rather than assumed.

Two declarations are EQUAL exactly when they declare the same base. The
dataclass's generated `__eq__` compares the one field, which is `None` for
both unwrapping bases, so `__eq__` and `__hash__` are defined explicitly over
`(loop, mode)` — in the class body, which `@dataclass` never overwrites — and
the declaration stays hashable. This is a correction made at the cycle's
review: nothing in the framework compares `Time` instances, but a test or a
consumer that did would have found two bases that mean different things
indistinguishable.

### Elapsed × none is ADMITTED and EQUIVALENT

`Time.elapsed()` on a root whose tree declares NO `State` is admitted and
changes nothing observable. The state discipline selects the executor and the
time base says what `time` MEANS, and those are three lines of
`simulation/sim.py`: `clocked = tree_declares_states(node)` answers the
discipline structurally before anything is bound, the running branch is taken
on `base.mode == 'running'` alone, and `if clocked:` constructs the clocked
executor. An elapsed stateless root therefore runs the ordinary fixed-`dt`
stepping loop, reads `k*dt` from `sim.time`, is bound with SECONDS as every
stepped simulation has always been, reads bare `$t` unbound exactly as a
running root and an undeclared root do, publishes the document an undeclared
root publishes BYTE FOR BYTE, and is published rather than refused — the
publication refusal is keyed on declared STATES (ADR-125) and not on the base.

What the base ADDS to such a root is a MEANING: elapsed seconds that never
wrap, which is what a machine that is operated has and a loop has not. The
table's `—` in that square was "nobody had asked", not "this cannot be", and
it is the last `—` the table had.

### The clock is a banked value

Under a CLOCKED root — one whose tree declares a `State`, ADR-125, unchanged —
that ALSO declares `Time.elapsed()`, the simulation banks `time`:

- the bank id is the bare `time`, which is `CLOCK_NAME`: the same string the
  run reserves, the same string `set_state` takes as its one global entry, and
  the same string a version 5 document publishes as a running program's clock.
  One name, from one place;
- the value is SECONDS, a float, initial `0.0`;
- `state={'time': 3.0}` at construction sets it as session setup, `sim.state`
  returns it beside the drivers and the states, `snapshot`/`restore` carry it
  because a snapshot IS the bank, and `reset` returns it to `0.0`;
- `sim.time` reads it. This is the ONE name of ADR-125's refused list that
  this decision lifts, and only under this base: under an untimed clocked root
  `sim.time` stays refused, its message improved to name `Time.elapsed()` as
  the way to have one. Every other refused name — `run`, `at`, `every`,
  `tick`, `rate`, `trigger`, `commands`, `program`, `crossings` — stays
  refused under an elapsed clocked root exactly as it is under an untimed one.

**No collision is possible and nothing new refuses one.** A bank id is bare
only for a ROOT-declared driver or state, and a root-declared `Driver` or
`State` named `time` is ALREADY refused at class definition by the
shadowing refusal `DriverDeclaration.__set_name__` raises, `AssemblyNode.time`
being a member of a base class; a child-declared one qualifies as `child.time`
and cannot collide with a bare name. The run's explicit `CLOCK_NAME`
reservation exists because a running bank also holds JOINT COORDINATES, which
qualify by a different rule; a clocked bank holds none. This is asserted by a
test rather than left a claim.

### One verb moves it

`sim.move('time', by=seconds)` and `sim.move('time', to=seconds)` — the same
verb, the same `Request` value object, the same ONE-MOVING-INPUT rule: a
request moves TIME with every driver standing, or ONE DRIVER with time
standing, and nothing moves two. Seconds are both the design unit and the
native unit, the clock having no `scale`, no `dtype` and no `range`, so no
conversion happens anywhere.

**Time never reverses.** A request whose travel is negative, or whose `to=`
lies behind the banked seconds, is REFUSED BY NAME, naming both instants and
saying that elapsed seconds never wrap and never run backwards. It is a
refusal and not a stop, and the difference is the decision: a stop reports a
bound the machine MET, and no bound was met — the request is meaningless, not
obstructed. **Zero is admitted**: `by=0`, or `to=` the banked instant, moves
nothing, fires nothing, poses what already stands and returns a `Request` with
`admitted == 0.0` and no commits, which is ADR-126's own reading of a request
stopped at zero travel and what keeps `move('time', to=t)` idempotent. A
request naming `'time'` under a clocked root that declares no elapsed base is
refused by name, naming `Time.elapsed()`.

### An event on the clock is an event

`time` is a SOURCE of a committing relation, in both factories, exactly as a
driver is:

```python
(time & engaged & count).commits(count, at=release, law=advance)
```

Everything about the event is ADR-125's, unchanged. `at` is ONE jump node
classified STRUCTURALLY per moving input — affine SOLVED by division, kinked
CUT at ADR-123's own breakpoints, curved REFUSED at construction by name, the
clock joining the drivers in that same loop under the same `_standing_except`
substitution. Only RISING steps fire; the landing is the nearest representable
value on the FAR SIDE by `far_side_of`'s ordinal walk; two relations are ONE
event exactly when their landings are the same float, by IDENTITY and not by
tolerance; commits are ordered by path, reads are synchronous and pre-event,
two relations writing one state at one landing refuse the REQUEST by name, and
`_MAX_CROSSINGS` applies unchanged with its refusal saying the request can be
split.

**A pendulum's release is AFFINE in time, and that is the evidence the
no-tolerance claim rests on.** `floor((t + T/4) / (T/2))` is a floor over a
linear function of the clock, so the fixture that proves events on time needs
no curved level and **this decision adds no tolerance at all**
(`_CROSSING_TOLERANCE` appears nowhere in `simulation/clocked.py`, asserted of
the module's own source). That level rises TWICE per period, at each extreme
of the swing, which is what a release is: a request of `by=40*T` fires EIGHTY
events, and `by=20*T` forty. The ratified scenario said forty for `by=40*T`
and was corrected at review against the level, which is the normative half.
The first landing is `0.49999999999999994` rather than `0.5`, one representable
value below the ideal instant, and that is ADR-125's landing rule working:
membership of the far side is decided by EVALUATING the level's own branch,
never by comparing a float to a surface, and `(t + T/4)` rounds up to the
surface one ulp early. Ten short requests still equal one long one exactly,
instant for instant, which is the property a tolerance would have cost.

**A relation the clock alone can move is legal.** ADR-125 refuses at
construction a committing relation whose every source is a state, because
nothing a request can move enters its level. Under an elapsed root the clock
is something a request can move, so that refusal becomes "no declared driver
AND not the clock" — a relation NO REQUEST can reach — its reason unchanged
and its message naming the clock among the inputs that would fix it.

**Where the clock may be NAMED, and the honest limit of it.** A committing
relation naming `time` is declared in the body that declares the base, because
that is the body in which the name holds the declaration object itself. Three
cases follow from ordinary Python and all three are stated:

1. the body declares `Time.elapsed()` — `time` is that frozen instance, which
   this decision gives the `&` and `commits` faces every other source kind
   carries. Admitted.
2. the body declares `Time(loop=)` or `Time.running()` — the same faces are
   reached and REFUSE AT CLASS DEFINITION, by name, saying an event is located
   on a clock that never wraps and naming `Time.elapsed()`. The facts are
   exactly there, which is ADR-125's own rule about where a refusal is raised.
3. the body declares no base — a Python class body does not see
   `AssemblyNode.time`, so the framework is not reached at all. Where the file
   imported the stdlib `time`, `time & <a declaration>` dispatches to the right
   operand's reflected `__rand__`, which no declaration kind carried. **This
   decision adds it** — one helper and one line each on the six kinds that
   already carry `&` (`Coordinate`, `CoordinateRef`, `Coordinates`,
   `DriverDeclaration` and through it `StateDeclaration`, `ChildDeclaration`,
   `RepeatDeclaration`) and on `Time` itself — so a foreign LEFT operand is
   refused by name as `group_with` already refuses a foreign right one, and
   where that operand is a MODULE the message adds the clock sentence. It is
   reached only where Python raises its operand-type line today, so no
   admitted `&` changes.

**The blind spot is recorded rather than papered over.** A body that never
bound `time` at all raises Python's own `NameError`, and no framework refusal
can improve on that: the name fails before an operator is reached. The
scenario asserts Python's answer and this decision promises no message there.

### The pose reads the banked clock, through the hook the walk already has

Under a bound clocked simulation with an elapsed base the tree is posed with
every driver, every state AND the clock bound, `self.time` a number of
seconds. Unbound — the build path, `solid build`, `solid export`, a snapshot,
any producer, any render outside a simulation — `self.time` reads bare `$t`
through the fallback an unbound clock already takes, `read_time` branching on
`base.loop is None`. **That branch needed no edit, which is why no document
producer is touched by this decision**: a `simulate()` or a law that is a
formula of time animates in the untimed preview exactly as it does today, and
is posed at `sim.time` under the simulation.

`read_time` reads each node's own snapshot entry first, so a clock bound only
on the root would leave every descendant symbolic, and the delivery is
therefore per visited assembly. **`drive_tree` gains NOTHING**: it already
calls `visit(node, path, children)` for every assembly after its drivers and
states are bound and before anything renders, and it already renders ONCE at
the end of the descent, which is what makes a request cost one pose. An
elapsed clocked pose passes a `visit` that writes the banked seconds; every
other root passes none, so the walk every other pass makes is the walk it
makes today, and "the walk is unchanged for a model with no clock" is
literally true rather than merely optional.

### Nothing stops a clock

**A request along TIME is never clipped.** ADR-126 clips by taking, for each
constraint THE MOVING DRIVER CAN MOVE, the earliest point at which its level
exceeds its threshold; constraint plans are compiled per declared driver, so
the clock has none and the clip finds nothing. The behaviour falls out of
ADR-126's own compile, and this decision states it as a PROMISE rather than
leaving it an accident, because the reason is a design decision: **a declared
range is a MECHANICAL STOP (ADR-108), and no interlock holds a clock.** A pawl
stops a crank because something is in the way; nothing is in the way of the
next second.

What happens instead is ADR-126's own end-of-request judgement, unchanged: a
coordinate that leaves its declared range at some instant is an impossible
POSE, and the request that reaches it is refused WHOLE, commits nothing and
never poses — which is exactly the untimed reading of a range.

**A compiled CHAIN may not follow the clock.** ADR-126 composes each bounded
coordinate, and each coordinate a `Bound` reads, down to the bank's ids, which
stay free names. One construction makes a chain carry the clock instead, and
it is the ordinary protocol used ordinarily: a law FACTORY is called once at
realization with the realized owners, so a factory reading `owner.time` there
captures what an UNBOUND read gives — the animation symbol — and closes over
it. That graph reaches evaluation with a free name the bank has no entry for
and dies with a bare `KeyError`. This decision refuses it AT SIMULATION
CONSTRUCTION, by name, naming the node, the joint, the side and the name that
survived, and saying that a clocked stop is compiled over the bank and that a
clock-driven coordinate is not something a stop can hold. **The rule is stated
GENERALLY — any free name surviving a composed chain that is not a bank id,
`$own` aside, is refused — so it covers the clock and whatever else ever
leaks**, and it is ADR-126's own promise ("what the bank cannot reach this way
is refused by name") made true for a case its implementation left open.

The route was EXECUTED and not merely read: the fixture's first request died
with the bare `KeyError` exactly where it was predicted, and the refusal fires
on the LOW side first because the compile takes `low` before `high`. A
`Bound`'s own expression is unchanged — `reads=` names COORDINATES (ADR-113)
and a clock is not one.

## Consequences

- **The two-axis table has one `—` left, and it is a category error rather
  than a gap.** untimed × none is today's pose, untimed × memory is ADR-125,
  looping × memory is refused by name, elapsed × none is admitted and
  equivalent, elapsed × memory is this decision, elapsed × integrated is
  `Time.running()`, and looping/untimed × integrated is what `Time.running()`
  means there being nothing else to say. A project can now state "this
  machine's time is elapsed seconds" without also stating "retain every
  coordinate and integrate every law".
- **Measured on this cycle's own fixtures, and compared to nothing else.** The
  clock costs a model that has none NOTHING: cycle 1's register fixture
  answers one stroke request in 0.107 ms before and after, and a stateless
  pose costs 0.044 ms before and after. On the pendulum: a time request with
  no event 0.062 ms, with one event 0.109 ms, with forty events 2.07 ms on a
  standing simulation (4.39 ms including construction); one pose 0.035 ms. So
  a pose is about 1.7 % of a forty-event request and about a third of a
  one-event one — **posing twice per request would have cost about a third
  again on the short requests a maker actually makes**, which is what the
  `visit` hook avoids and why it is the decision rather than a nicety. Nothing
  is claimed here about the Curta, which has no clock, and nothing comparative
  about `Time.running()`, which this decision does not touch.
- **`Time.running()` is untouched, by diff and not by intention.** No line of
  `simulation/run.py` or `simulation/program.py` changed; `tests/running-corpus.json`
  and every running fixture are byte-for-byte as they were, their per-test cost
  inside the recorded envelope; the whole existing suite is green with no
  fixture edited and no expected value moved. A `State` under `Time.running()`
  stays refused with ADR-125's message and its meaning DEFINED and not
  implemented, and `Time.elapsed()` is not a partial `Time.running()` and must
  not be described as one: it is the OTHER half of ADR-104, the base without
  the mechanics ADR-105 to ADR-107 attach to it.
- **A stateless model is indistinguishable, structurally.** The clocked
  executor is entered exactly where ADR-125 entered it — a non-empty state
  collection — so "no clocked code path is entered for a stateless tree" stays
  literally true and its counter assertion stays green for an ELAPSED
  stateless root too; `document_body`, `export_node` and the builder's viewer
  snapshot are asserted byte-identical against an undeclared twin.
- **A model with a clock-driven RANGED joint is newly refused**, at
  construction, with the joint and the one-line fix named. The shape is rare —
  a joint an author poses BY HAND from `self.time` is the ordinary way to
  write a pendulum, and ADR-126 already refuses a ranged hand-bound joint — so
  what this newly refuses is relation-driven ones. The alternative was leaving
  them to die on a bare `KeyError` at the first request.
- **A clocked model still cannot be published or viewed.** ADR-125 refuses a
  clocked document by name, and this decision adds a clock the document does
  not yet carry. The document cycle owns both, and ADR-110's ladder is why;
  what a version carrying a clocked clock publishes — the clock's name, its
  initial value, and whether a consumer advances it — is deliberately not
  presumed here.
- **The `NameError` blind spot is real and permanent under this shape.** A
  class body that binds no `time` at all gets Python's message, and a body
  that imported the stdlib `time` gets the framework's. A reader meeting the
  first will not be told about `Time.elapsed()`, and nothing short of a
  metaclass-level namespace would change that.
- **Deliberate narrowings, each recorded in `workflow/warts.md` with the shape
  a later cycle takes:** a clip in time and a chain that follows the clock (one
  piece of work, arriving together or not at all, and its first task is to
  settle ADR-126's contested direction test for a level PERIODIC in time); a
  looping root with memory; `Time.elapsed()` under a running root; an
  `Instruction`, a control or `move(duration=)` over the clock, whose shape
  depends on what the viewer cycle needs; a multi-input request moving a
  driver and the clock together (ADR-125's narrowing, whose classification is
  stated against one moving input); and `time` as the source of a `drives`
  relation, a part whose pose is a formula of time being written in
  `simulate()` as the pendulum fixture writes it.

## Promotion

Accepted 2026-09-17 at the cycle's adversarial review, which ran an
independent probe against the uncommitted implementation — an elapsed root
with two child wheels of one class, committed by clock beats AND reset by a
crank stroke, with snapshot/restore over time, descendants reading the banked
seconds, backwards refused, reset, and `state={'time': ...}` — and returned one
finding needing closure: two `Time` declarations of different bases compared
EQUAL and hashed alike, closed red-first by the explicit `__eq__`/`__hash__`
over `(loop, mode)` above. Four questions the implementation raised were
decided at that review rather than by the implementation: the eighty events of
`by=40*T` are the level working and the ratified scenario is what moved; the
one-ulp landing is ADR-125's rule working and nothing changes; the
captured-clock route stands as designed, having been executed rather than
assumed; and `enumeration._decide_block_membership` joins the list of `.mode`
consumers the design named. The implementation's own record — the red log, the
two groups of tests honestly reported as written after their own task's code,
every measurement quoted above and the four design questions — is
`evidence.md` inside the archived change.
