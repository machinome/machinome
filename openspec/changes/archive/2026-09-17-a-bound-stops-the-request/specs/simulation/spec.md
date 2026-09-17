## ADDED Requirements

### Requirement: A bound stops a clocked request on its path

Under a CLOCKED root a joint coordinate's declared `range` SHALL be a STOP on
a request path: a request that would carry the coordinate past a declared
bound SHALL admit only the travel at which every bound is still satisfied,
and SHALL NOT be refused. A `Driver`'s own declared `range` SHALL remain
presentation metadata, never a clamp and never a stop.

**The compile.** At simulation construction, for every joint coordinate of
the tree whose joint declares a `range` with a bound that is not `None`, the
system SHALL compile:

1. a CHAIN — one expression graph over the bank's qualified ids giving that
   coordinate's value — composed by SUBSTITUTION from the relations that
   determine it: each determining relation's law graph with every source
   name replaced by that source's own chain, down to declared drivers and
   declared states, which stay free names. A wiring SHALL contribute its
   ratio and offset, a derived coordinate its linear formula, and a `law=`
   relation the graph its law is inspected into, by the same inspection a
   running law is inspected by. An INTERMEDIATE PORT SHALL be traversed as
   any other link: it is a calculation composed into the chain, not a banked
   value. The composition SHALL substitute and SHALL NOT simplify, so that
   the chain performs, over the identical native values, arithmetic
   EQUIVALENT to the ordinary enumeration's — the two evaluation orders being
   free to differ by a rounding, which is why the clocked simulation and not
   the enumeration judges what it compiled;
2. the BOUND, exactly as it is compiled under a running root — a number,
   `None`, or an expression graph over the coordinate's own qualified id and
   the qualified ids its `reads` resolve to, with jumps admitted and no
   plan — and a chain as above for each read. A read SHALL be a declared
   driver, a declared STATE or a joint coordinate; a read naming a plain
   port or a derived coordinate SHALL be refused at construction by joint
   and node identity, as it is under a running root.

**The constraint level.** For each bounded side the LEVEL SHALL be the
coordinate's value minus the evaluated upper bound, or the evaluated lower
bound minus the coordinate's value, so that OUTSIDE is positive; and its
arguments SHALL be read as follows:

- the bound's OWN coordinate SHALL take the value it holds when the REQUEST
  STARTS, evaluated once from the chain over the standing bank, and SHALL
  therefore be a number for the whole request;
- every coordinate the bound READS SHALL take its value along the path,
  through its own chain;
- every declared driver but the one the request moves, and every declared
  state, SHALL be a standing number.

**The classification.** How a level moves in each driver that can move it
SHALL be decided STRUCTURALLY, once, at construction, with every free name
but that driver replaced by a standing placeholder:

- a level no driver can move SHALL not be examined for that driver, and
  SHALL cost a request that moves it nothing;
- an AFFINE level's zero SHALL be solved by one division;
- a KINKED level SHALL be cut at its own breakpoints and each sub-interval
  solved the same way;
- a level carrying JUMPS SHALL be partitioned at its own jump surfaces, each
  solved, and its SKELETON — every jump node holding one branch on a piece —
  classified and solved as above on each piece;
- a CURVED level SHALL be REFUSED at simulation construction, by name,
  naming the joint, the node, the side, the driver whose motion curves it
  and the primitive it curves through, and saying a clocked stop is solved
  and never searched.

No sampling, no bisection and NO TOLERANCE SHALL be introduced by this
requirement.

**The clip.** Before any event of the request is located, the system SHALL:

1. take, for each constraint the moving driver can move, the level it stands
   at when the request starts, and the threshold `max(0, that level)`, so
   that a coordinate standing OUTSIDE a bound may move inward and may return
   to where it stood but SHALL NOT go further outside;
2. locate the earliest point on the path at which any constraint's level
   exceeds its threshold, and take the smallest such point over all of them;
3. land the driver on the NEAREST REPRESENTABLE VALUE ON THE SATISFIED SIDE
   of that point, found by walking the solved value in float space, with
   membership decided by EVALUATING the level there and never by comparing a
   value to a bound — so that a bound met exactly at a representable value
   lands ON it, both bounds being INCLUSIVE, and a level that jumps across
   its zero lands on the last representable value before its surface;
4. truncate the request's travel to that landing.

The coordinate that stopped SHALL NOT be clamped, snapped or otherwise
written: a clocked simulation banks no joint coordinate, and the value the
coordinate holds SHALL follow from the pose of the clipped bank.

Cycle by cycle the events of the request SHALL then be located on the
CLIPPED path only, by the requirement "A clocked simulation solves a request
path event by event", unchanged in every particular.

A request whose admitted travel is ZERO SHALL be ADMITTED: it SHALL move
nothing, commit nothing, leave the bank exactly as it stood, and report its
stop. It SHALL NOT raise.

The clip SHALL be computed ONCE, over the bank as it stands when the request
begins, and SHALL NOT be recomputed between events: the request is to a
clocked root what a tick is to a running one, which is the unit a bound is
already evaluated over.

**A ranged coordinate NOTHING binds SHALL be admitted as a CONSTANT.** Where
the rest render shows that no relation, wiring or derived formula resolved to
a bounded coordinate AND no author code bound it, the chain SHALL be the
constant value that coordinate holds at rest; the constraint SHALL then be
examined for no driver, SHALL stop no request, and SHALL NOT be a refusal,
even where that rest value lies outside the declared pair — nothing bound the
coordinate, so no binding was ever recorded for any judgement to make. A
`Bound` that READS such a coordinate SHALL take that same constant.

**What is refused at construction**, each by name, naming the joint, the
node and the side, and each saying what to state instead: a bounded
coordinate the root's own `simulate()` BINDS BY HAND, which the rest render
tells from the case above by the binding it recorded; a bounded coordinate or
a read whose chain passes through a law that is not an expression; a `Bound`
whose reads name a coordinate no chain reaches; a chain that reads the
coordinate it drives; a cyclic chain; and the curved level above. A declared
stop the framework cannot follow along a path is a stop that can never stop.

A request SHALL be refused, committing nothing, when locating a constraint's
jump surfaces exceeds the crossing maximum the framework already states for
one graph, naming the request, the joint, the side and the maximum.

**What a request reports.** The value object `move` returns SHALL carry, in
addition to the input, the requested travel and the events fired: the
ADMITTED travel in design units, and the STOPS met — each naming the bounded
coordinate by its qualified id, the side, the bound EVALUATED at the
landing, the coordinate's value there, the driver's value and the fraction
of the requested travel. Several constraints met at ONE landing SHALL be
several entries. `record=N` SHALL keep a bounded ring of those entries as
`sim.stops`, separate from the ring of commits, because a stop is a bound of
a coordinate and a commit is a value the machine wrote.

**Which authority judges what.** During a REQUEST the clocked simulation
SHALL be the SOLE AUTHORITY for the constraints it compiled: a coordinate it
compiled a constraint for SHALL NOT be judged by the enumeration at the pose
that request makes — neither at the moment of binding nor at the close of
that enumeration — because the clip located the stop and the same authority
that located it judges it, with one arithmetic.

At the END of every request the clocked simulation SHALL judge each compiled
constraint ITSELF, over the FINAL bank and THROUGH THE CHAIN, against the
same threshold the clip used. A constraint violated there — which a request
can reach only where a state an event COMMITTED moved the coordinate or moved
its bound — SHALL refuse the request, raising the joint range error and
naming the node, the joint, the side, the bound as the chain evaluates it
over that bank, and the value the chain gives the coordinate there. That
judgement SHALL be made BEFORE the tree is posed, and the refused request
SHALL commit nothing, leaving the bank, the tree and the record exactly as
they stood.

A pose that is NOT a request — construction, `state=` or `restore` — SHALL be
judged by the enumeration exactly as it is judged today: a bound violated by
such a pose remains an impossible pose and SHALL raise the joint range error,
because a machine cannot be PUT where it cannot BE. The bind-time and
close-of-enumeration judgements SHALL be unchanged in every other particular,
and SHALL be unchanged for every root that is not clocked.

**Cost.** A tree that declares no `State` SHALL compile no constraint and
SHALL enter no code path of this requirement. A clocked tree whose joints
declare no range SHALL compile no constraint and SHALL behave exactly as it
does without this requirement, its requests reporting their whole travel as
admitted and no stops. Nothing about a stop under a RUNNING root, or about
the untimed judgement of a range, SHALL change.

#### Scenario: A pawl stops a backwards request at the last seated tooth

- **WHEN** a clocked register whose crank drives a joint declaring
  `range=(lambda turn: 6 * floor(turn / 6), None)` stands at a settled state
  and receives `sim.move('crank', by=-3600)`
- **THEN** the admitted travel is exactly the travel back to that tooth, no
  event fires, the states stand, and one stop names that coordinate, `low`
  and the evaluated tooth — where the same request on the fixture without
  the pawl moves the whole travel

#### Scenario: Events are located on the clipped path only

- **WHEN** a request whose full travel would cross three event surfaces is
  clipped by a bound after the first
- **THEN** exactly one event is reported, at the same landing the shorter
  unclipped request reports it at, and the bank holds the state that one
  event committed

#### Scenario: A stop at zero travel is admitted

- **WHEN** an interlocked knob is asked to move while the coordinate its
  bound reads holds the interlock closed
- **THEN** the request returns with an admitted travel of zero, one stop
  naming the knob's coordinate, the side and the evaluated bound, no
  committed event, an unchanged bank, and no exception

#### Scenario: A bound reading its own committed value freezes a coordinate

- **WHEN** a knob's range is a pair of `Bound`s that evaluate to the
  coordinate's own committed value while the crank is off rest, the knob
  stands part way through its travel, and the crank is asked to turn a whole
  revolution
- **THEN** the crank admits its whole travel and reports no stop, while a
  request that would move the knob itself admits nothing

#### Scenario: A numeric range lands on the bound

- **WHEN** a lift joint declaring `range=(0, 9)` is driven by a request of
  twenty
- **THEN** the admitted travel puts the coordinate at exactly `9`, the pose
  accepts it, and the stop names `high` and `9`

#### Scenario: A level that jumps lands before its surface

- **WHEN** a bound gated by a comparison closes as the driver crosses a
  representable threshold
- **THEN** the driver lands on the last representable value at which the
  level is satisfied, which is the value below that threshold for a
  non-strict gate and the threshold itself where the gate admits it

#### Scenario: A coordinate standing outside its bound may move inward

- **WHEN** a clocked simulation is constructed standing outside a bound whose
  reads held no value for the enumeration to judge, and a request moves it
  back toward the bound
- **THEN** the request admits its whole travel, a request back to exactly
  where it stood is admitted, and a request that would carry it further
  outside admits nothing

#### Scenario: The bound's own coordinate is read at the request's start

- **WHEN** the pawled register receives one `sim.move('crank', by=-3600)`,
  and a second simulation from the same bank receives ten successive
  `sim.move('crank', by=-360)`
- **THEN** both end at the SAME value — the last seated tooth — because the
  first request stops there and every later one starts ON that tooth, where
  the bound evaluates to the tooth itself and the request admits zero travel

#### Scenario: A bound read once per request is coarser than a bound read at each event

- **WHEN** a clocked root whose bound reads a STATE an event of the same
  request writes receives one long request, and a second simulation from the
  same bank receives two requests split at that event
- **THEN** the long request admits the travel the state it STARTED at allows,
  the split pair admits the travel the committed state allows, the two
  admitted travels differ, and neither is refused

#### Scenario: A bounded coordinate the bank cannot reach is refused

- **WHEN** a clocked root declares a joint with a range and binds that
  joint's coordinate in its own `simulate()` rather than through a relation
- **THEN** simulation construction is refused, naming the node, the joint
  and the side, and saying the coordinate is not reached from the bank

#### Scenario: A ranged joint nothing binds is admitted as a constant

- **WHEN** a clocked root declares a joint with a range on a part no
  relation, no wiring and no `simulate()` of that tree ever binds
- **THEN** simulation construction succeeds, no request examines that
  constraint, every request admits its whole travel and reports no stop

#### Scenario: A chain that reads the coordinate it drives is refused

- **WHEN** a clocked root declares `range=(0, 9)` on `lift.travel` and
  determines it by a relation whose law reads `lift.travel` itself —
  `crank.turn.drives(lift.travel, law=lambda turn, travel: travel + turn)`
- **THEN** simulation construction is refused naming that relation as
  written, the node, the joint and the side, and saying a clocked request
  retains no value for a law to read back

#### Scenario: A cyclic chain is refused

- **WHEN** a clocked root declares `range=(0, 9)` on `a.travel` and states
  `a.travel.drives(b.travel, ratio=2)` together with
  `b.travel.drives(a.travel, ratio=0.5)`, so that the chain from the bank to
  `a.travel` returns to itself
- **THEN** simulation construction is refused naming both relations as
  written, the joint and the side, and saying the chain from the bank does
  not close

#### Scenario: A bound reading a port is refused

- **WHEN** a clocked root's `Bound` names a plain port among its `reads`
- **THEN** simulation construction is refused by joint and node identity,
  saying a bound reads the state and naming the joint the port follows

#### Scenario: A curved level is refused at construction

- **WHEN** a clocked root's bound evaluates `sin` of a coordinate a driver
  moves
- **THEN** simulation construction is refused naming the joint, the side,
  that driver and the primitive

#### Scenario: A commit that carries a coordinate out of range refuses the request

- **WHEN** a request's committed state carries a compiled bounded coordinate
  outside its range
- **THEN** the clocked simulation's own end-of-request judgement raises the
  joint range error, naming the node, the joint, the side, the bound its
  chain evaluates over the final bank and the value that chain gives the
  coordinate there; the tree is never posed over that bank; and the bank, the
  tree and the record stand exactly as they did before the request

#### Scenario: A compiled coordinate is not judged twice

- **WHEN** a request is clipped so that a coordinate lands EXACTLY on an
  inclusive bound, and the tree is posed at the end of that request
- **THEN** the enumeration does not judge that coordinate — neither at the
  moment of binding nor at its close — the request is admitted, and the same
  tree posed by `restore` to a bank outside that bound is refused by the
  enumeration as it is today

#### Scenario: A clocked model with no ranged joint is unchanged

- **WHEN** cycle one's register fixture, whose joints declare no range, runs
  its requests
- **THEN** every request admits its whole travel, reports no stop, and gives
  the same events and the same bank as before this requirement existed

#### Scenario: A running root's stop is unchanged

- **WHEN** a running fixture reaches a declared stop, including one whose
  bound reads another coordinate
- **THEN** the tick stops, records and reports exactly as it did before this
  requirement existed, message for message

## MODIFIED Requirements

### Requirement: A clocked simulation solves a request path event by event

The system SHALL provide `Sim(model)` over a clocked root, constructed with
NO `dt`. A `dt` given over a clocked root SHALL be refused by name, saying a
state moves on requests and not on a cadence; a `dt` omitted over any other
root SHALL remain refused as it is today. `state=` SHALL accept declared
drivers AND declared states by qualified id, bound over the declared defaults
before the first render. Construction SHALL pose the tree once and hold a
BANK of every driver and every state by qualified id; joint coordinates,
ports and `time` SHALL NOT be in that bank — the first two being what the
ordinary enumeration computes from it on every pose, and `time` because a
clocked root declares no time base and a state moves on requests rather than
on a clock.

A clocked tree SHALL be posed exactly as the build path poses a driven model
outside a simulation: every driver and every state bound to its current
value, and `time` left as the untimed symbolic animation variable through the
fallback an unbound time already takes. A `simulate()` that reads `self.time`
under a clocked root SHALL therefore read what it reads today under an
untimed one.

`sim.move(input_id, by=travel)` or `sim.move(input_id, to=value)` SHALL take
exactly one of `by`/`to` and SHALL name exactly ONE declared driver, in
design units, and is a REQUEST: a straight path from the value that driver
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
   sources and classified structurally over the one moving driver. An AFFINE
   level's surfaces SHALL be solved by division; a KINKED level SHALL be cut
   at its own breakpoints and each sub-interval solved the same way; a CURVED
   level SHALL be refused at simulation construction, by name, naming the
   relation, the driver whose motion curves it and the primitive, and saying
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
4. The moving driver SHALL take the NEAREST REPRESENTABLE VALUE ON THE FAR
   SIDE of the surface, found by walking the solved value in float space, and
   that one value SHALL be used both for the event's reads and for the
   resumption of the remaining path, so no event can fire twice. Membership
   of a value in the far side SHALL be decided by evaluating the jump node's
   BRANCH at that value, never by comparing it to the surface: a solved value
   at which the branch has already changed IS the landing, a strict
   comparison against a representable threshold lands on the next value
   beyond it, and a non-strict comparison lands on the threshold itself.
5. Every relation firing at that event SHALL evaluate its `at` and `law`
   callables at that driver value and at the PRE-EVENT value of every state —
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

A committing relation NO declared driver can reach — one whose every source
is a state, so that its event level can never move along any request path —
SHALL be refused at simulation construction, by name, saying that its event
level moves with no declared driver.

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
carrying the relation as written, the fraction of the path, the driver's
value at the event, and the targets with their new values. The admitted
travel and the stops are stated by the requirement "A bound stops a clocked
request on its path"; where no bound is met the admitted travel SHALL be the
requested one and the stops SHALL be empty. `record=N` SHALL keep a bounded
ring of the same event entries, and a second bounded ring of the stops;
without it the request's own result SHALL still be complete. `sim.state` SHALL return
the whole bank by qualified id as a fresh mapping. `sim.snapshot()`,
`sim.restore()`, `sim.initial` and `sim.reset()` SHALL act on that bank,
`restore` refusing a snapshot taken over a different model before touching
anything.

A clocked simulation has no clock and no cadence: `run`, `at`, `every`,
`time`, `tick`, `rate`, `trigger`, `commands`, `program` and `crossings`
SHALL each be refused by name. `sim.stops` SHALL NOT be refused: it is the
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

- **WHEN** a clocked simulation calls `run`, `every`, `time`, `tick`,
  `trigger` or `rate`
- **THEN** each is refused by name, saying a clocked model has no clock
