## ADDED Requirements

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
  defined and not yet implemented.

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

### Requirement: A committing relation writes states at an event

The system SHALL provide `commits(targets, at=, law=)` as a verb in a class
body beside `drives`, available on the same ends and on the same `&` groups,
with the same flat chaining and the same missing-parentheses refusal. It
SHALL be recorded as a class attribute like a relation: read off the class it
is the declaration, read off an instance it is that instance's resolved
record.

`targets` SHALL name one `State` or several, written as a tuple or with `&`,
in order. Every target SHALL be a `State`; anything else SHALL be refused at
class definition naming what it is instead.

Every source SHALL be a `Driver` or a `State`. A port, a joint coordinate or
a derived coordinate named as a source SHALL be refused at class definition,
by name, saying to name the drivers and states the port follows. A source
group MAY name a target of the same relation, which is a READ of that
target's value.

`at` and `law` SHALL both follow the existing law-factory protocol: each is a
callable of two arguments, called exactly ONCE at realization with the
realized OWNERS — one owner for a side naming one coordinate, the tuple of
owners in written order for a side naming several — returning a callable over
the sources' VALUES, one positional argument per source in written order.
Neither SHALL be handed an event object, a runtime handle, or any mutable
per-tick state. `at` and `law` SHALL both be required; `ratio=` and `offset=`
SHALL be refused; a `.repeat()` broadcast on either side SHALL be refused by
name.

**`at` SHALL be exactly one jump node** — `floor(x)`, `ceil(x)`, `sign(x)`,
or a comparison — whose LEVEL QUANTITY and SURFACES are the ones the jump
vocabulary already defines. Any other shape, including a sum of jump nodes, a
bare arithmetic expression and `a % b`, SHALL be refused at simulation
construction, by name, saying that one event is one surface family and that
two are two committing relations.

**`law`'s returned callable SHALL be an expression over its sources**,
inspected exactly as a running law's is: applied to one symbolic token per
source's qualified id, with raw text and calls outside the symbolic
vocabulary refused naming the relation. Because a commit is evaluated at ONE
POINT and never integrated, every jump primitive in a commit law SHALL mean
what it says and nothing SHALL be subtracted: a law made entirely of jumps is
a valid commit, where a running law of that shape is refused as arithmetic.
`law` SHALL return one value for one target, or a sequence of exactly as many
values as there are targets, in written order; any other shape SHALL be
refused naming the relation, the law, the targets as written and what came
back.

A commit law SHALL read its sources as the bank holds them — in NATIVE units
— and SHALL return NATIVE values. A returned value SHALL NOT be passed
through the design-unit conversion a driver applies to a move target, which
would divide a scaled value by its scale a second time. A target declaring
`dtype=int` SHALL take the nearest whole native unit of the returned value,
rounded ONCE, at the commit; a target declaring a `scale` and no `dtype`
SHALL take the returned value unchanged.

#### Scenario: A grouped source commits two states

- **WHEN** a class body states
  `(crank & units & tens).commits((units, tens), at=strokes, law=advance)`
- **THEN** the declaration resolves on an instance with both factories called
  once, each handed the tuple of realized source owners and the tuple of
  realized target owners

#### Scenario: A target that is not a state is refused

- **WHEN** a class body states `(crank & units).commits(dial.turn, at=..., law=...)`
- **THEN** class definition fails naming the relation and `dial.turn`

#### Scenario: A port source is refused

- **WHEN** a committing relation names a plain port among its sources
- **THEN** class definition fails naming the relation and the port, and says
  to name the drivers and states the port follows

#### Scenario: A compound at is refused

- **WHEN** `at` returns `floor(a / 360) + floor(b / 360)`
- **THEN** simulation construction is refused naming the relation and saying
  one event is one surface family

#### Scenario: A commit law made of jumps is admitted

- **WHEN** `law` returns `floor(crank / 360) % 10`
- **THEN** it compiles, and committing it at an event gives the digit that
  expression evaluates to at that point

#### Scenario: A law returning the wrong number of values is refused

- **WHEN** a relation naming two targets has a law returning one value
- **THEN** it is refused naming the relation, the law, both targets as
  written and what came back

#### Scenario: A scaled state is committed unrescaled

- **WHEN** a committing relation targets a `State(default=0, scale=10)` and
  its law returns `4.0`
- **THEN** the state holds `4.0` and the pose reads the design value `40.0`,
  the value having been converted once and not twice

#### Scenario: An integer state rounds once at the commit

- **WHEN** a committing relation targets a `State(default=0, dtype=int)` and
  its law returns `9 - 1e-12`
- **THEN** the state reads `9`, and the same law returning the same value to
  a float state reads `9 - 1e-12`

#### Scenario: A commits without at is refused

- **WHEN** a class body states `.commits(units, law=advance)` with no `at`
- **THEN** class definition fails naming the relation and saying an event is
  required

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

`move` SHALL return a value object naming the input, the travel and the
events it fired, each entry carrying the relation as written, the fraction of
the path, the driver's value at the event, and the targets with their new
values. `record=N` SHALL keep a bounded ring of the same entries; without it
the request's own result SHALL still be complete. `sim.state` SHALL return
the whole bank by qualified id as a fresh mapping. `sim.snapshot()`,
`sim.restore()`, `sim.initial` and `sim.reset()` SHALL act on that bank,
`restore` refusing a snapshot taken over a different model before touching
anything.

A clocked simulation has no clock and no cadence: `run`, `at`, `every`,
`time`, `tick`, `rate`, `trigger`, `commands`, `program`, `crossings` and
`stops` SHALL each be refused by name.

A violated joint `range` SHALL remain what it is today — an impossible pose,
raising `JointRangeError` on the pose the request ends at, including the
close-of-enumeration judgement for a bound that reads other coordinates. A
request SHALL NOT be clipped by a bound in this capability.

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

#### Scenario: A request whose final pose is refused commits nothing

- **WHEN** a request would advance a state far enough that the joint it
  poses leaves its declared `range`
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

### Requirement: A clocked discipline costs a stateless model nothing

A tree that declares no `State` SHALL be unchanged by this capability in
behaviour, in published bytes and in cost. No additional walk of the tree
SHALL be introduced: declared states SHALL be collected in the walk the
enumeration already makes for drivers, instructions and controls. No clocked
code path SHALL be entered for a tree whose state collection is empty, and no
module this capability adds SHALL be imported by a project that names no
`State`.

#### Scenario: An existing model's document is byte-identical

- **WHEN** a published fixture that declares no `State` is serialized before
  and after this capability exists
- **THEN** the two documents are identical byte for byte

#### Scenario: A stateless tree enters no clocked path

- **WHEN** a driven, stateless model is constructed, posed, stepped with
  `Sim(node, dt)` and published
- **THEN** no clocked code path is entered at any point

## MODIFIED Requirements

### Requirement: Qualified tree-wide driver enumeration

The system SHALL provide one enumeration authority that walks a
constructed assembly's linked tree and returns its declared drivers
keyed by qualified id (dotted instance path plus local name;
root-declared drivers keep bare names). This enumeration SHALL be the
single source feeding the simulation state bank, instruction-target
resolution, build-path default binding, and the serialized document's
driver table, so the id in the document and the key in the bank are
the same string by construction. Enumeration SHALL fail loudly on a
driver reachable only through an illegal id segment, per the
qualified-identity requirement.

The same walk SHALL return every declared `State` keyed by the same rule,
from the same pass rather than an additional one, and that table SHALL be the
single source feeding the clocked bank, the refusal of a state as a
`set_state`, instruction or control target, and the publication refusal. A
qualified id SHALL name at most one declaration: an id two declarations of
one tree would both claim SHALL be refused naming both, whether the two are
two drivers, two states, or one of each.

#### Scenario: Drivers on descendants are enumerated qualified

- **WHEN** a driverless root holds `x_axis` and `y_axis` instances of
  one class declaring `motor = Driver(default=8000)`
- **THEN** enumeration yields exactly `x_axis.motor` and
  `y_axis.motor`, each carrying the declaration's default, range,
  unit, dtype, and scale

#### Scenario: A driver and a state claiming one id are refused

- **WHEN** one class declares a `Driver` and a `State` that qualify to the
  same id
- **THEN** the enumeration refuses naming the id and both declarations

### Requirement: Fixed-dt stepping loop with deferred actions

The system SHALL provide a simulation loop constructed over one assembly and
a fixed `dt`, which SHALL be a finite real number of seconds strictly greater
than zero and SHALL be validated before any node state is bound. On
construction it SHALL enumerate declared drivers across the whole linked tree
and bind every driver's default through `set_state` by qualified id, so a
state-consuming assembly — including one whose drivers live only on
descendants — renders under a complete snapshot from the first render.
`Sim(node, dt, meshes=False, state=None, record=None)`: `state` MAY give
initial values for declared drivers by qualified id, bound over the declared
defaults before that first render; a name in it that is not a declared driver
id SHALL be refused as `set_state` refuses it, and a joint coordinate id SHALL
be refused too, because initial coordinates come from the rest pose. Each
tick SHALL: advance every driver's program, bind the full snapshot via
`set_state` together with the global `time` entry set to the exact simulation
instant in seconds (`k*dt`, computed from the integer tick count, never
accumulated), record the tick and snapshot in a trajectory keyed by qualified
id, then run due deferred actions and cadence actions. Under a running
simulation, `self.time` therefore reads the stepped simulation clock; the
normalized symbolic `$t` animation path outside simulations is unchanged.

Under a root declaring `Time.running()` construction SHALL continue as the
requirement "A running root's simulation owns every driver and joint
coordinate" states, each tick SHALL be the tick the requirement "A
continuous law is integrated over a tick and increments propagate" states,
and the trajectory SHALL be the bounded recording the requirement
"Recording is explicit and bounded under a running root" states. Under a root
that is NEITHER running NOR clocked — a root declaring no time base, or
declaring `Time(loop=)`, and whose tree declares no `State` — `record` SHALL
be ignored, the trajectory SHALL append every tick as it does today, and the
whole running-only surface — `move`, `rate`, `commands`, `snapshot`,
`restore`, `reset`, `initial`, `program` — SHALL be refused naming
`Time.running()`; `sim.running` SHALL report which case holds.

Over a CLOCKED root — one whose tree declares a `State` — `dt` SHALL be
omitted and construction and stepping SHALL be what the requirement "A
clocked simulation solves a request path event by event" states instead. A
`dt` given over a clocked root SHALL be refused by name, and `state=` SHALL
additionally accept declared states. A clocked root SHALL ADMIT `move`,
`snapshot`, `restore`, `reset`, `initial` and `state`, whose meanings that
requirement states, and SHALL REFUSE `rate`, `commands` and `program`
together with the cadence surface — `run`, `at`, `every`, `time`, `tick`,
`trigger`, `crossings` and `stops` — each by name, saying a clocked model has
no clock. `sim.running` SHALL remain `False` over a clocked root, which
declares no time base.

Instants, cadence periods, and run durations SHALL be finite real seconds and
SHALL be validated as whole numbers of ticks (`round(t/dt)*dt == t` within
float tolerance), represented as integer tick counts rather than accumulated
floats. `run(duration)` SHALL require a nonnegative duration and SHALL reject
an invalid duration before firing actions or changing simulation state.
`at(t)` SHALL treat `t` as an absolute instant, reject a tick before the
current simulation tick, and accept the current tick, whose actions run in the
existing pre-step phase of the next `run()` including `run(0)`. Scheduled
actions SHALL be deferred callables — `at(t).trigger(name)` and
`at(t).run(fn)` where `fn` receives the simulation — never eagerly evaluated
expressions. `every(period, fn, *args)` SHALL require a positive period of at
least one whole tick, run `fn` at the declared tick cadence, and account its
cost per slot, so scenario reports can state assertion cost separately from
stepping cost.

#### Scenario: Non-whole instants are rejected

- **WHEN** `at(0.05)` is requested on a simulation with `dt=0.02`
- **THEN** the call fails naming the instant and `dt`

#### Scenario: Defaults bind before first render

- **WHEN** a simulation is constructed over an assembly whose
  `render()` reads a declared driver
- **THEN** construction succeeds with the declared default bound, with
  no unbound-state error

#### Scenario: A driverless root with driver-declaring children simulates

- **WHEN** a driverless root holds `x_axis` and `y_axis` instances of
  one class declaring `motor`
- **THEN** construction binds both children's defaults under
  `x_axis.motor` and `y_axis.motor` and stepping addresses each
  independently

#### Scenario: Time reads the simulation clock

- **WHEN** a simulation with `dt=0.02` has advanced 125 ticks and a
  deferred action reads the assembly's `time`
- **THEN** the value is exactly the instant 2.5 seconds, not symbolic
  `$t` and not a normalized fraction

#### Scenario: Deferred action sees stepped state

- **WHEN** `at(2.5).run(fn)` is registered and the simulation runs
  past 2.5
- **THEN** `fn` is called once, at tick `2.5/dt`, observing the state
  after that tick's binding

#### Scenario: Invalid dt is refused before binding

- **WHEN** `Sim(node, dt)` receives zero, a negative value, infinity, NaN,
  a boolean, or a non-numeric value
- **THEN** construction raises `ValueError` naming `dt`
- **AND** the node has not received a simulation state binding

#### Scenario: Negative run duration has no effects

- **WHEN** a simulation with a current-tick action calls `run(-dt)`
- **THEN** `ValueError` is raised and its tick, state, trajectory, pending
  actions, and cadence counts are unchanged

#### Scenario: Past scheduling is refused

- **WHEN** a simulation at tick 10 registers an action for tick 9
- **THEN** `ValueError` is raised naming the instant and current time
- **AND** no action is registered or executed

#### Scenario: Current-tick scheduling remains valid

- **WHEN** a simulation at tick 10 registers an action for tick 10 and calls
  `run(0)`
- **THEN** that action runs once at tick 10 without adding a trajectory entry

#### Scenario: An author-bound plain port follows a run-owned coordinate

- **WHEN** an assembly under a running root binds a plain port in its
  `simulate()` from a run-owned joint coordinate it reads,
  `self.readout = self.first.turn.value`, and the simulation runs ten ticks
  of a move on the input that drives `first.turn`
- **THEN** after every tick `readout` equals `first.turn`, its binder is the
  author's and not the running simulation's, and it is cleared and rebound
  each tick rather than holding a stale value

#### Scenario: Initial driver values bind over the defaults

- **WHEN** `Sim(node, dt, state={'crank': 30.0})` is constructed over a root
  whose `crank` declares a default of `0.0`
- **THEN** `sim.state['crank']` is `30.0` before the first tick and the
  first render was posed at it

#### Scenario: The running surface is refused under a looping root

- **WHEN** a simulation over a root declaring `Time(loop=2.0)` calls
  `move`, `rate`, `snapshot`, `restore` or `reset`
- **THEN** each is refused naming `Time.running()`, `sim.running` is
  `False`, and the trajectory keeps appending every tick

#### Scenario: A dt over a clocked root is refused

- **WHEN** `Sim(node, 0.02)` is constructed over a root whose tree declares a
  `State`
- **THEN** construction is refused naming `dt`, saying a state moves on
  requests and not on a cadence, and nothing is bound
