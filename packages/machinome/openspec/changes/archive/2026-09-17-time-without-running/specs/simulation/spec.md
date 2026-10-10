## ADDED Requirements

### Requirement: An elapsed clocked root banks its clock

Under a CLOCKED root — one whose tree declares a `State` — that also declares
`time = Time.elapsed()`, the system SHALL hold `time` as a BANKED VALUE of
the simulation, in SECONDS, under the bare qualified id `time`, which is the
one global snapshot entry the state delivery already reserves. Its initial
value SHALL be `0.0`. It SHALL be settable at construction by
`Sim(model, state={'time': ...})` as session setup, SHALL appear in
`sim.state` beside the drivers and the states, SHALL be carried by
`sim.snapshot()` and put back by `sim.restore()`, and SHALL be returned to
its initial value by `sim.reset()`. `sim.time` SHALL read it.

No collision SHALL be possible and none SHALL be invented: a bare bank id
belongs only to a ROOT-declared driver or state, and a root-declared `Driver`
or `State` named `time` is already refused at class definition for shadowing
the assembly member of that name.

**The pose.** A clocked tree under the elapsed base SHALL be posed with every
driver, every state AND the clock bound, `self.time` reading the banked
number of seconds, and SHALL still be posed exactly ONCE per request. UNBOUND
— on the build path, in any document producer, in a snapshot, and in any
render outside a simulation — `self.time` SHALL read bare `$t`, exactly as it
does under `Time.running()`, so no document producer is affected by the
elapsed base and a geometry that is a formula of time animates in the untimed
preview as it does today.

**A request may move the clock.** `sim.move('time', by=seconds)` and
`sim.move('time', to=seconds)` SHALL be REQUESTS in every sense the
requirement "A clocked simulation solves a request path event by event"
states: exactly one of `by`/`to`, a straight path from the banked instant to
the requested one, every other bank value standing, events located exactly on
that path, commits ordered, the tree posed once at the end, and the whole
request ATOMIC. Seconds SHALL be both the design and the native unit of the
clock, so no conversion SHALL be applied to `by`, `to` or the admitted
travel. ONE moving input per request SHALL still hold: a request moves the
clock with every driver standing, or one driver with the clock standing.

**Elapsed seconds never run backwards.** A request whose travel is negative,
or whose `to=` lies behind the banked instant, SHALL be REFUSED by name,
naming the banked instant and the one asked for and saying that elapsed
seconds never wrap and never reverse. It SHALL be a refusal and not a stop: a
stop reports a bound the machine met, and no bound was met. A request of ZERO
seconds SHALL be ADMITTED, SHALL fire no event, SHALL commit nothing and
SHALL report an admitted travel of zero.

**Events on the clock are events.** The clock SHALL be admitted as a SOURCE
of a committing relation, in `at` and in `law` alike and exactly as a declared
driver is, and every rule the requirement "A clocked simulation solves a
request path event by event" states about an event SHALL apply unchanged: one
jump node, structural classification per moving input with an AFFINE level
solved, a KINKED level cut and a CURVED level REFUSED at construction by name,
RISING steps only, the far-side landing, ties decided by identity of that
landing with NO TOLERANCE, synchronous pre-event reads, path-ordered commits,
the same conflict refusal at one landing, and the same crossing maximum whose
refusal names the request. A committing relation whose only moving source is
the clock SHALL be admitted.

**Nothing stops a clock.** A request along the clock SHALL NOT be clipped by
any declared range: a range is a MECHANICAL stop and no interlock holds a
clock. A coordinate that a time request carries outside its declared range
SHALL be judged by the end-of-request judgement the requirement "A bound
stops a clocked request on its path" already states — over the final bank,
through the same chains — and that judgement SHALL refuse the whole request,
which commits nothing and never poses.

**A compiled chain SHALL NOT follow the clock.** Every chain that requirement
composes SHALL resolve to bank ids, and ANY free name surviving a composed
chain that is not a bank id SHALL be refused at simulation construction, by
name, naming the joint, the node, the side and the name that survived. A
relation whose law FACTORY captured the clock at realization — the one route
by which a chain can carry it, `time` being refused as a `drives` source and
a law callable receiving only its sources' values — composes the animation
symbol into such a chain and SHALL be refused there, saying that a clocked
stop is compiled over the bank and that a clock-driven coordinate is not
something a stop can hold.

**Refusals, each where its facts exist.** A request naming `time` under a
clocked root that declares no time base SHALL be refused by name, naming
`Time.elapsed()`; `sim.time` under such a root SHALL stay refused by name,
naming `Time.elapsed()`; and the elapsed base SHALL change nothing about
`Time.running()` — not its compile, not its tick, not its document, not its
meaning — and SHALL NOT admit a `State` under it.

#### Scenario: The clock is in the bank and the session carries it

- **WHEN** a clocked root declaring `Time.elapsed()` is constructed,
  `sim.move('time', by=3.0)` is made, a snapshot is taken, the clock is moved
  again, and the snapshot is restored
- **THEN** `sim.state['time']` and `sim.time` read `0.0`, then `3.0`, then
  the later instant, then `3.0` again, and `sim.reset()` returns the clock to
  `0.0` with every state at its declared default

#### Scenario: A clocked root with no time base has no clock in its bank

- **WHEN** a clocked root that declares no time base is constructed
- **THEN** `sim.state` carries no `time` entry, `sim.time` is refused by name
  naming `Time.elapsed()`, and `sim.move('time', by=1)` is refused by name

#### Scenario: A request on the clock fires the events on it

- **WHEN** a pendulum-and-count fixture whose `at` is
  `floor((time + T / 4) / (T / 2))` receives `sim.move('time', by=40 * T)`
- **THEN** eighty events are reported in path order — the level rises TWICE
  per period, at each extreme of the swing — each at exactly the release
  instant the affine solve gives, and the count has advanced by eighty

#### Scenario: Two short time requests equal one long one

- **WHEN** one `sim.move('time', by=10 * T)` is compared with ten successive
  `sim.move('time', by=T)` from the same initial bank
- **THEN** both give the same bank, entry for entry, and the same events at
  the same instants

#### Scenario: A driver request at a standing clock fires nothing on the clock

- **WHEN** the same fixture receives `sim.move('engaged', to=0)`
- **THEN** no event is reported, the clock has not moved, the count holds,
  and a time request afterwards commits the count the disengaged law gives

#### Scenario: Time backwards is refused and zero is admitted

- **WHEN** `sim.move('time', by=-1)` and `sim.move('time', to=<an instant
  behind the bank>)` are made, and then `sim.move('time', by=0)`
- **THEN** the first two are refused by name naming both instants with the
  bank and the pose standing, and the third is admitted with no event, no
  commit and an admitted travel of zero

#### Scenario: The pose reads the banked seconds and the build path reads $t

- **WHEN** a fixture whose `simulate()` poses a part from
  `A * sin(2 * pi * self.time / T)` is moved to an instant and then the same
  tree is rendered outside any simulation
- **THEN** the posed operation is the number that instant gives, the tree was
  rendered once for the request, and the render outside the simulation
  carries `$t` in that operation exactly as it does for a root declaring no
  time base

#### Scenario: A curved event level in the clock is refused

- **WHEN** a committing relation states `at = floor(sin(time))`
- **THEN** simulation construction is refused by name, naming the relation,
  the clock as the input whose motion curves the level and the primitive, and
  saying a clocked event is solved and never searched

#### Scenario: A relation the clock alone moves is admitted

- **WHEN** a committing relation's only moving source is the clock, every
  other source being a state
- **THEN** the simulation constructs, and a time request fires its events

#### Scenario: No bound stops a time request

- **WHEN** a clocked elapsed fixture carrying a ranged joint that a driver
  moves receives a driver request past the bound and then a time request
- **THEN** the driver request is clipped at the bound and reports its stop,
  and the time request reports no stop and makes its whole travel

#### Scenario: A time request that leaves a range is refused whole

- **WHEN** a commit made by a time request carries a bounded coordinate
  outside its declared range
- **THEN** the request is refused naming the coordinate, the side and the
  bound, nothing is committed, and the bank, the record and the posed tree
  stand exactly as they stood

#### Scenario: A chain that carries the clock is refused at construction

- **WHEN** a ranged joint is driven by a relation whose law factory read the
  owner's `time` at realization and closed over it
- **THEN** simulation construction is refused by name, naming the joint, the
  node, the side and the name that survived the chain

## MODIFIED Requirements

### Requirement: A state is a value the machine writes

The system SHALL provide `State(default, range=None, unit=None, dtype=None,
scale=None)`, declared as a class attribute on an assembly exactly where a
`Driver` may be declared, taking exactly `Driver`'s arguments with exactly
their meanings: `default` is the value in NATIVE units, `range` is
presentation metadata in design units that clamps nothing, `unit` names the
design unit, `dtype=int` makes the value a whole number of native units, and
`scale` states design units per native unit. A `State` SHALL be read off the
declaring node as `self.<name>` and SHALL enter an expression exactly as a
driver's value does — symbolic where a driver's is symbolic, numeric under a
bound snapshot. A declaration shadowing a node member SHALL fail at class
definition, as a driver's does.

A `State`'s public identity SHALL be its instance-qualified id, by the rule a
driver's follows: the dotted attribute path to the declaring node plus the
local name, or the bare name for a root-declared one. One enumeration
authority SHALL walk the linked tree and return every declared state by that
id, and it SHALL be the enumeration that already walks the tree for drivers,
instructions and controls rather than an additional pass.

A tree in which anything declares a `State` is a CLOCKED model. Every
ordinary enumeration of such a tree SHALL bind each state's current value —
the declared default outside a simulation, the committed value under one —
before the tree is posed, exactly as declared driver defaults are bound.

Everything that distinguishes a `State` from a `Driver` SHALL be about who
writes it, and each refusal SHALL be raised where its facts exist, naming the
state by its qualified id:

- `set_state` SHALL refuse a state by name, saying that a state is written by
  the machine at an event and naming the relation that commits it.
- An `Instruction` SHALL refuse a state among its targets, and a `Button`,
  `Turn` or `Slide` SHALL refuse a state as its input.
- A state SHALL be refused as the driven end of `drives`.
- A state MAY be the target of SEVERAL committing relations, in one class
  body or across the tree — a value a machine writes at two different events
  has two writers and one answer at each — and SHALL be refused only when
  two relations would write it AT ONE EVENT, which is a judgement of the
  request and is stated by the requirement "A clocked simulation solves a
  request path event by event".
- A target named twice among the targets of ONE committing relation SHALL be
  refused at class definition. That judgement SHALL be made on the target's
  PATH AS WRITTEN — the path to the node that declares the state plus the
  local name — and never on the local name alone, so that two children of
  one class declaring one state are two states and a relation may write
  both; the message SHALL print that path.
- A state that no committing relation targets SHALL be refused at simulation
  construction, saying that nothing writes it.
- A state SHALL be refused under a root declaring `Time(loop=)`, because a
  loop replays from zero and would replay every commit, and under a root
  declaring `Time.running()`, naming both and saying the combination is
  defined and not yet implemented. A state under a root declaring
  `Time.elapsed()` SHALL be ADMITTED: elapsed seconds never wrap, so
  nothing replays a commit, and the simulation over such a root is the
  clocked one with its clock in the bank, stated by the requirement "An
  elapsed clocked root banks its clock".

A state SHALL be settable only as session setup: `Sim(model, state={...})` by
qualified id, and `sim.restore(saved)`. A state SHALL be carried by
`sim.snapshot()` and restored by `sim.restore()` beside the drivers.

#### Scenario: A state reads like a driver

- **WHEN** a root declares `units = State(default=0, range=(0, 9), dtype=int)`
  and its `simulate()` poses a dial from `self.units`
- **THEN** the tree renders with `units` bound to `0` and the dial posed at
  the value that default gives

#### Scenario: States enumerate qualified beside drivers

- **WHEN** a root holding `bank_a` and `bank_b` instances of one class
  declaring `digit = State(default=0)` is enumerated
- **THEN** exactly `bank_a.digit` and `bank_b.digit` are returned, each
  carrying the declaration's default, range, unit, dtype and scale

#### Scenario: set_state refuses a state by name

- **WHEN** `node.set_state(units=3)` is called on a clocked root
- **THEN** it is refused naming `units` and the relation that commits it,
  and no value is bound

#### Scenario: A state is not a driven end

- **WHEN** a class body states `crank.drives(units)` where `units` is a
  `State`
- **THEN** class definition fails naming the relation and the state

#### Scenario: A state nothing writes is refused

- **WHEN** a simulation is constructed over a root declaring a `State` that
  no committing relation targets
- **THEN** construction is refused naming the state and saying nothing
  writes it

#### Scenario: Two children of one class are two states

- **WHEN** a root holds two children of one class declaring `digit` and one
  committing relation names both `a.digit` and `b.digit` among its targets
- **THEN** the class is created, the simulation constructs, and one request
  writes both digits

#### Scenario: One state written at two events is admitted

- **WHEN** one class body states two committing relations both targeting
  `dial.digit`, one on a `crank` level and one on a `ring` level
- **THEN** both are recorded, the simulation constructs, and a request on
  either input fires only the relation whose level it moves

#### Scenario: A state under a looping base is refused

- **WHEN** a root declares `time = Time(loop=4)` and a `State`
- **THEN** the enumeration that binds declared defaults refuses it, naming
  the state and the base

#### Scenario: A state under a running base is refused, with its meaning named

- **WHEN** a root declares `time = Time.running()` and a `State`
- **THEN** it is refused naming both and saying the combination is defined
  and not yet implemented

#### Scenario: A state under the elapsed base is admitted

- **WHEN** a root declares `time = Time.elapsed()` and a `State` that a
  committing relation writes
- **THEN** the declared defaults bind, the tree poses, and `Sim(model)`
  constructs a clocked simulation over it

### Requirement: A clocked simulation solves a request path event by event

The system SHALL provide `Sim(model)` over a clocked root, constructed with
NO `dt`. A `dt` given over a clocked root SHALL be refused by name, saying a
state moves on requests and not on a cadence; a `dt` omitted over any other
root SHALL remain refused as it is today. `state=` SHALL accept declared
drivers AND declared states by qualified id, bound over the declared defaults
before the first render. Construction SHALL pose the tree once and hold a
BANK of every driver and every state by qualified id; joint coordinates and
ports SHALL NOT be in that bank, being what the
ordinary enumeration computes from it on every pose. `time` SHALL NOT be in
that bank under a clocked root that declares NO time base, because such a
root has no clock and a state moves on requests rather than on one; under a
clocked root declaring `Time.elapsed()` `time` SHALL be a banked value, by
the requirement "An elapsed clocked root banks its clock", and everything
this requirement says of the bank SHALL hold of it.

A clocked tree that declares no time base SHALL be posed exactly as the
build path poses a driven model
outside a simulation: every driver and every state bound to its current
value, and `time` left as the untimed symbolic animation variable through the
fallback an unbound time already takes. A `simulate()` that reads `self.time`
under such a root SHALL therefore read what it reads today under an
untimed one.

`sim.move(input_id, by=travel)` or `sim.move(input_id, to=value)` SHALL take
exactly one of `by`/`to` and SHALL name exactly ONE MOVING INPUT — one
declared driver, in design units, or, under an elapsed root, the clock — and
is a REQUEST: a straight path from the value that input
holds to the requested one, with every other bank value standing. A request
naming a state, a joint coordinate, or more than one input SHALL be refused
by name.

Before any event is located the request's path SHALL be CLIPPED by the
requirement "A bound stops a clocked request on its path": the travel
becomes the travel every declared bound admits, and every rule below
applies to the CLIPPED path. A request whose admitted travel is ZERO SHALL
fire no event, commit nothing and still be admitted.

Along that path the system SHALL locate events EXACTLY, by the tools the
running executor already owns and with no additional locator, tolerance or
knob:

1. Each committing relation's `at` level SHALL be bound at the standing
   sources and classified structurally over the one MOVING INPUT — a declared
   driver, or the clock under an elapsed root. An AFFINE
   level's surfaces SHALL be solved by division; a KINKED level SHALL be cut
   at its own breakpoints and each sub-interval solved the same way; a CURVED
   level SHALL be refused at simulation construction, by name, naming the
   relation, the input whose motion curves it and the primitive, and saying
   a clocked event is solved and never searched.
2. A crossing SHALL fire only when the step is RISING — `at`'s branch after
   the crossing greater than its branch before — the branch before read at
   the midpoint of the piece the path came from, the branch after read AT
   THE LANDING, the nearest representable point of the piece the path
   enters, which is the only reading available when the crossing is the
   request's own endpoint. A falling step SHALL fire nothing. A mechanism that
   commits on the other edge states it by negating its own level.
3. The earliest rising crossing over all committing relations SHALL be the
   next event. Two crossings SHALL be ONE event exactly when their far-side
   landings are the SAME floating-point value, and SHALL otherwise be two
   events taken in path order, the later reading what the earlier committed.
   NO TOLERANCE SHALL decide that question: a tolerance stated as a fraction
   of the request's travel would make one long request merge events that
   several short requests keep apart.
4. The moving input SHALL take the NEAREST REPRESENTABLE VALUE ON THE FAR
   SIDE of the surface, found by walking the solved value in float space, and
   that one value SHALL be used both for the event's reads and for the
   resumption of the remaining path, so no event can fire twice. Membership
   of a value in the far side SHALL be decided by evaluating the jump node's
   BRANCH at that value, never by comparing it to the surface: a solved value
   at which the branch has already changed IS the landing, a strict
   comparison against a representable threshold lands on the next value
   beyond it, and a non-strict comparison lands on the threshold itself.
5. Every relation firing at that event SHALL evaluate its `at` and `law`
   callables at that input value and at the PRE-EVENT value of every state —
   including a state the same relation writes and a state another relation
   writes at the same event — and the targets SHALL take the results
   together. Declaration order SHALL NOT be observable. Two relations firing
   at one event and writing DIFFERENT states is that synchronous case; two
   firing at one event and writing the SAME state is a CONFLICT, and the
   whole REQUEST SHALL be refused, naming the state by its qualified id,
   both relations as written and the landing, and committing nothing.
6. The remaining path SHALL be solved again from the landing with the new
   bank, so an event surface that reads a committed state moves with it. The
   process SHALL repeat until the path is exhausted.

A request SHALL NOT pose the tree between events: `at` and `law` read only
banked values, and the tree SHALL be bound exactly once, at the end of the
request. A request SHALL be ATOMIC — a refused request SHALL commit nothing
and SHALL leave the bank, the tree and the record exactly as they were. That
atomicity SHALL INCLUDE the final pose: the tree SHALL be posed over the
request's working bank BEFORE that bank becomes the simulation's, and a pose
the tree refuses SHALL leave the bank, the recorded events and the posed
tree exactly as they stood, the refusal being raised to the caller.
`restore()` SHALL behave the same way: a snapshot whose pose is refused
SHALL leave the previous bank and the previous pose standing.

A committing relation NO REQUEST can reach — one whose every source is a
state, so that its event level can never move along any request path —
SHALL be refused at simulation construction, by name, saying that its event
level moves with no declared driver and, under an elapsed root, not with
the clock either. Under an elapsed root a relation whose only moving source
is the CLOCK SHALL be admitted: the clock is something a request moves.

A request SHALL be refused when one committing relation's located events
exceed the crossing maximum the framework already states for one graph — one
thousand. The judgement SHALL be made over the events ACTUALLY LOCATED, one
by one as the path is solved, and never over a count estimated from the
travel and the surface spacing, so a level that stops crossing halfway
through a long request is not refused for a crossing it never makes. The
refusal SHALL name the request — the input and its travel — the relation as
written, the count reached and the maximum, and SHALL say that the request
can be split into shorter ones.

`move` SHALL return a value object naming the input, the travel REQUESTED,
the travel ADMITTED, the bounds met and the events it fired, each event entry
carrying the relation as written, the fraction of the path, the moving
input's value at the event, and the targets with their new values. The admitted
travel and the stops are stated by the requirement "A bound stops a clocked
request on its path"; where no bound is met the admitted travel SHALL be the
requested one and the stops SHALL be empty. `record=N` SHALL keep a bounded
ring of the same event entries, and a second bounded ring of the stops;
without it the request's own result SHALL still be complete. `sim.state` SHALL return
the whole bank by qualified id as a fresh mapping. `sim.snapshot()`,
`sim.restore()`, `sim.initial` and `sim.reset()` SHALL act on that bank,
`restore` refusing a snapshot taken over a different model before touching
anything.

A clocked simulation has no CADENCE: `run`, `at`, `every`, `tick`, `rate`,
`trigger`, `commands`, `program` and `crossings`
SHALL each be refused by name, under every time base. `sim.time` SHALL be
refused by name under a clocked root that declares NO time base, naming
`Time.elapsed()` as the way to have one, and SHALL read the banked seconds
under a clocked root that declares it. `sim.stops` SHALL NOT be refused: it
is the
bounded ring of the bounds a clocked machine met, under the requirement "A
bound stops a clocked request on its path".

A violated joint `range` SHALL be a STOP on the request's path, under the
requirement "A bound stops a clocked request on its path", which clips the
travel before any event is located, judges the constraints it compiled ITSELF
at the end of the request, and leaves every pose that is not a request to the
enumeration. A bound violated by the INITIAL pose — construction, `state=` or
`restore` — SHALL remain an impossible pose raising `JointRangeError`. Where
a request's own COMMITS carry a bounded coordinate outside its range, that
end-of-request judgement SHALL raise `JointRangeError` and refuse the whole
request, which commits nothing and never poses.

A request along the CLOCK SHALL NOT be clipped by any bound: a declared
range is a mechanical stop and nothing holds a clock. A coordinate carried
outside its range by a time request SHALL be judged by the same
end-of-request judgement, which refuses the whole request, commits nothing
and never poses.

#### Scenario: One request fires one event

- **WHEN** a register fixture standing at `units = 0` receives
  `sim.move('crank', by=360)` with `at = floor(crank / 360)`
- **THEN** exactly one event is reported, at the fraction the solve gives,
  `sim.state['units']` is `1`, and `sim.state['crank']` is `360`

#### Scenario: Ten events in one request equal ten requests of one

- **WHEN** one `sim.move('crank', by=3600)` is compared with ten successive
  `sim.move('crank', by=360)` from the same initial bank
- **THEN** both give the same bank, entry for entry, and the same ten events
  in the same path order

#### Scenario: A backwards request fires nothing

- **WHEN** a register fixture standing at `units = 9` receives
  `sim.move('crank', by=-3600)`
- **THEN** no event is reported, `units` and `tens` hold, `crank` has moved
  the whole travel, and the pose follows the crank

#### Scenario: An event surface that reads its own state moves with it

- **WHEN** a clearing fixture whose `at` is
  `ring >= START + PITCH * (10 - digit)` sweeps its ring far enough to clear
  a dial, and then sweeps further
- **THEN** exactly one event fires on the first sweep, the digit is zero
  after it, and the second sweep fires nothing

#### Scenario: The landing is on the far side of the surface

- **WHEN** a crossing of `floor(crank / 360)` is solved at `crank = 360`
- **THEN** the law is evaluated at exactly `360.0`, the floor branch there is
  `1`, and resuming the path from that value does not fire the event again

#### Scenario: Simultaneous commits read the same pre-event state

- **WHEN** two committing relations cross at one point and each law reads a
  state the other writes
- **THEN** both read the values that stood before the event and both sets of
  targets take their results together

#### Scenario: Surfaces one ulp apart are two events

- **WHEN** two committing relations have comparison surfaces differing by one
  representable value, and one request crosses both
- **THEN** two events are reported, in path order, the second law reading
  what the first committed, and the same two events are reported whether the
  crossing happens inside one long request or inside the shorter request that
  reaches just past it

#### Scenario: Surfaces that land on one value are one event

- **WHEN** two committing relations' far-side landings are the same
  floating-point value
- **THEN** exactly one event is reported, both relations commit at it, and
  both read the bank as it stood before it

#### Scenario: A clocked pose leaves time symbolic

- **WHEN** a clocked root whose `simulate()` reads `self.time` is posed by
  `Sim(model)` and again after a request
- **THEN** `time` is the untimed symbolic animation variable in both poses,
  unchanged from the same model built outside a simulation, and `time` is
  absent from `sim.state`

#### Scenario: A curved at is refused at construction

- **WHEN** a committing relation's `at` is `floor(sin(crank))`
- **THEN** simulation construction is refused naming the relation, `crank`
  and the primitive

#### Scenario: A refused request commits nothing

- **WHEN** a request's third event evaluates a law that raises
- **THEN** the bank, the tree and the record stand exactly as they did before
  the request

#### Scenario: A request whose commit leaves a joint out of range commits nothing

- **WHEN** a request would advance a state far enough that the joint it
  would pose leaves its declared `range`
- **THEN** `JointRangeError` is raised, the bank holds the values it held
  before the request — the moving driver's included — the tree is still
  posed where it was, and the recorded events are unchanged

#### Scenario: Two relations writing one state at one event refuse the request

- **WHEN** two committing relations of one tree write the same state and
  their far-side landings on one request are the same floating-point value
- **THEN** the request is refused naming that state, both relations and the
  landing, and the bank, the tree and the record stand exactly as they did
  before it

#### Scenario: A relation no driver can reach is refused

- **WHEN** a committing relation's sources are all states, so that no
  declared driver can move its event level
- **THEN** simulation construction is refused naming the relation and saying
  its event level moves with no declared driver

#### Scenario: The cadence surface is refused

- **WHEN** a clocked simulation calls `run`, `every`, `tick`, `trigger` or
  `rate`, and a clocked simulation over a root declaring no time base also
  calls `time`
- **THEN** each is refused by name, saying a clocked model has no cadence,
  and the `time` refusal names `Time.elapsed()` as the way to have a clock
