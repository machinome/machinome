# simulation Specification

## Purpose
The stepped simulation layer over the node model (ADR-056): stateless
class-level driver declarations, per-simulation state advanced by
deterministic programs, design-unit instructions, a fixed-dt stepping
loop binding qualified snapshots and the global `time` clock through
`set_state`, tree-wide qualified driver enumeration, and scenario
tests that run under both pytest and the `machinome test` runner. State
lives in drivers; geometry stays a pure function of the bound
snapshot.
## Requirements

### Requirement: An absolute move preserves its stated terminal coordinate

For `move(input, to=target, duration=...)`, the running simulation SHALL preserve the once-converted native target independently of the travel `target - current`. At the full terminal admission, the input SHALL stand at that exact native target, including its signed-zero bit, and its determined coordinates and numeric Bounds SHALL see the corresponding terminal endpoint before stop detection and commit. An exact endpoint on an inclusive bound SHALL complete without a stop. This SHALL hold for zero- and positive-duration moves, after snapshot/restore, and in both rounding directions, without changing the motion at earlier fractions or the semantics of `move(by=...)` and `rate(...)`. A current snapshot of an active absolute move SHALL retain the target separately and restore SHALL validate its numeric finite form atomically; a legacy snapshot without this added internal field SHALL not be guessed into a different target. A request that genuinely travels beyond a bound SHALL still stop and report its actually admitted travel; the system SHALL not relabel a blocked result after committing an overshoot or introduce a clearance tolerance.

#### Scenario: A rounded travel does not turn an exact upper landing into a stop
- **WHEN** a driver at the binary64 value immediately above `-4.9425` drives a Prismatic joint whose inclusive upper bound is `3.9075`, and `move(to=3.9075)` is requested
- **THEN** both input and directly determined joint end at exactly `3.9075`, the handle reports `completed`, and no upper stop is recorded, even though adding the rounded travel to the starting value would have produced `3.9075000000000006`

#### Scenario: A read-dependent bound agrees at its endpoint
- **WHEN** the same move meets an upper `Bound` reading a standing coordinate at `3.9075`
- **THEN** the bound's terminal sample sees the exact target and the move completes without changing the existing interior samples or search rule

#### Scenario: An actual crossing is not hidden
- **WHEN** the same mechanism requests a target strictly beyond the stated upper bound
- **THEN** it reports `blocked`, commits at the physical stop under the existing rule and does not silently land the requested endpoint

#### Scenario: Timed target survives restore
- **WHEN** a positive-duration absolute move is snapshotted before its final tick and replayed after restore
- **THEN** both runs admit the same intermediate travel and finish with the same exact target, status, bank and stop records

#### Scenario: A malformed saved target cannot partly restore
- **WHEN** a snapshot's optional active absolute target is a nonnumeric value or a nonfinite float
- **THEN** restore refuses it before changing the current run, while a legacy snapshot without that optional field retains its old record interpretation without inventing an endpoint

#### Scenario: Relative and signed-zero semantics remain distinct
- **WHEN** an otherwise identical `move(by=...)` is issued, or an absolute target is negative zero
- **THEN** the relative request retains additive travel semantics, while the absolute request retains the requested native endpoint bit on completion

### Requirement: Driver declarations separate from simulation state

The system SHALL let an assembly declare its drivers as stateless
class attributes: `Driver(default, range=None, unit=None, dtype=None,
scale=None)`, where `dtype=int` marks a discrete device whose state is
integer-typed and `scale` declares design units per native unit. A
declared `range` SHALL be expressed in design units — the units a
maker thinks and instruction targets are stated in — regardless of
`scale`; it is presentation metadata and never a clamp. A node class's
declared drivers SHALL be discoverable by name off the class without
instantiating it. Mutable driver state SHALL live only in a running
simulation, never on the declaration and never shared between node
instances or between simulations.

#### Scenario: Declarations carry no state

- **WHEN** two simulations run over nodes of the same class, stepping
  the same declared driver differently
- **THEN** each simulation observes only its own state trajectory and
  the class declaration is unchanged

#### Scenario: Declared drivers are discoverable

- **WHEN** a consumer inspects an assembly class declaring
  `x = Driver(default=100, range=(0, 200), unit='mm')`
- **THEN** it can enumerate the driver with its default, range, unit,
  dtype, and scale without constructing the assembly

#### Scenario: A scaled driver's range reads in design units

- **WHEN** an axis declares
  `motor = Driver(default=0, range=(0, 100), unit='ustep', dtype=int, scale=0.0125)`
- **THEN** the range means 0 to 100 design units of travel — 0 to 8000
  native microsteps — and a presenter converts through `scale` to
  relate it to native state, while nothing anywhere clamps state to it

### Requirement: Programs advance driver state deterministically

The system SHALL advance driver state only through programs. A program
SHALL be a pure function of the tick number and its captured start
state. `RampProgram` SHALL distribute a delta over n ticks; for an
integer-typed driver the distribution SHALL be integer-exact
(`start + (delta * k) // n`), landing exactly on `start + delta` at
`k == n`, after which the program completes. A driver with no active
program SHALL hold its state.

#### Scenario: Integer ramp lands exactly

- **WHEN** a ramp moves an integer driver from 8000 to 0 over 100
  ticks
- **THEN** the state at tick 100 is exactly 0 and every intermediate
  state is an integer

#### Scenario: Determinism is exact

- **WHEN** the same scenario script is run twice in fresh simulations
- **THEN** the recorded state trajectories compare exactly equal

### Requirement: Instructions carry design-unit targets

The system SHALL let an assembly declare named instructions:
`Instruction(targets, duration)` with targets keyed by driver name and
expressed in design units, or `Instruction(by=..., duration)` with
RELATIVE travel keyed the same way and expressed in the same units. An
instruction SHALL state exactly one of `targets` and `by`; both, or
neither, SHALL be refused at declaration naming the rule, and the one
given SHALL read back off the declaration with the other reading `None`.
An instruction duration SHALL be a finite real
number of seconds greater than or equal to zero. Instructions declared on any
node in the tree SHALL be discoverable and triggerable through the simulation
by qualified name — the declaring node's instance path joined with the
instruction name, with root-declared instructions keeping their bare names —
and each instruction's local target names SHALL resolve to the declaring
node's qualified driver ids. Triggering an instruction SHALL convert each
target, or each relative travel, to native driver state through that
driver's declared scale (rounding
to the nearest native unit for an integer-typed driver; a driver with no scale
takes the value verbatim) and start a ramp program over the instruction's
duration: a `targets=` ramp lands on the converted target, a `by=` ramp
lands on the driver's current value plus the converted travel, and either
replaces whatever ramp the driver was running. Under a root declaring
`Time.running()` triggering SHALL instead issue the run's own commands —
`targets=` as a move TO each target and `by=` as a move BY each travel,
under the requirement "Commands have one owner per input and report their
outcome" — claiming every input the instruction names before starting
any, so an ownership conflict refuses the whole instruction and starts
nothing. A zero-duration instruction SHALL reach every target and bind the
complete node snapshot immediately at the current tick, without advancing the
clock or adding a trajectory entry. Triggering an unknown name SHALL fail
listing the known qualified instruction names. Instruction semantics are held
to target-plus-duration and travel-plus-duration linear ramps; sequencing
and richer programs are explicitly out of scope. The serialized document's
instructions table SHALL OMIT a relative instruction until a later change
publishes the compiled program under a new schema version, because the
shipped viewer reads `targets` off every entry; a root whose instructions
are all relative SHALL publish an empty table, and the rest of the
document SHALL be unchanged.

Under a CLOCKED root triggering SHALL instead make ONE REQUEST, under the
requirement "A clocked simulation solves a request path event by event":
`targets=` a `move` TO the named driver's target and `by=` a `move` BY its
travel, both in design units, and `trigger` SHALL RETURN that request's own
value object, so a caller that presses a button holds exactly what a caller
that moved the input holds. An instruction under a clocked root SHALL name
EXACTLY ONE driver: a request names exactly one moving input, an instruction
naming two would be a SEQUENCE, and sequencing is a program and out of scope
for an instruction under every base. An instruction that names none, or more
than one, SHALL be refused where the clocked machine is COMPILED — at
simulation construction, and therefore before any document exists — by name,
naming the instruction, the inputs it names and the rule; an instruction
naming a STATE SHALL remain refused in the same place. The instruction's
`duration` SHALL be carried and given NO meaning by the machine: a request
is a path and not an interval, so a clocked `trigger` SHALL make the same
request and the same bank whatever the declared duration, and what the
duration says is how long a CONSUMER draws the transition. Triggering an
unknown name under a clocked root SHALL fail listing the known qualified
instruction names, exactly as it does under every other base.

#### Scenario: Millimetre target reaches a microstep driver

- **WHEN** an instruction targets `x=0` (mm) for a driver declared
  with `scale` millimetres-per-microstep and dtype `int`
- **THEN** the ramp's native target is 0 microsteps and intermediate
  states are whole microsteps

#### Scenario: A child's instruction homes only that child

- **WHEN** both axis instances declare `'Home': Instruction({'motor':
  0.0}, duration=2.0)` and the scenario triggers `x_axis.Home`
- **THEN** only `x_axis.motor` ramps to its native target while
  `y_axis.motor` holds its state

#### Scenario: A zero-duration instruction settles now

- **WHEN** an instruction with duration zero is triggered at tick 20
- **THEN** its targets are immediately visible in `sim.state`, the bound node,
  and a later deferred action at tick 20
- **AND** the simulation remains at tick 20 with no new trajectory entry

#### Scenario: An invalid instruction duration is refused

- **WHEN** an instruction is declared with a negative, infinite, NaN,
  boolean, or non-numeric duration
- **THEN** construction raises `ValueError` naming the duration

#### Scenario: A relative instruction ramps from where the driver stands

- **WHEN** an untimed root declares
  `'Advance': Instruction(by={'motor': 10.0}, duration=1.0)` over a scaled
  integer driver and the scenario triggers it twice, one second apart
- **THEN** after two seconds the driver stands at its start plus twice the
  travel converted through its scale, every intermediate state a whole
  native unit, and `Instruction.by` reads `{'motor': 10.0}` while
  `Instruction.targets` reads `None`

#### Scenario: An instruction names exactly one of targets and by

- **WHEN** an instruction is declared with both `targets` and `by`, or with
  neither
- **THEN** declaration raises naming the rule

#### Scenario: Under a running root an instruction is a move

- **WHEN** a root declaring `Time.running()` declares
  `'Park': Instruction({'crank': 40.0}, duration=0.5)` and
  `'Advance': Instruction(by={'crank': 10.0}, duration=0.5)`, and the
  simulation triggers `Park` and then, once it completes, `Advance`
- **THEN** the crank moves from its committed value to `40` over the first
  half second and from `40` to `50` over the next, every joint coordinate
  its relations reach follows by increments, and each trigger issued one
  command whose handle reports `completed`

#### Scenario: A relative instruction is not yet published

- **WHEN** a root declares `'Advance': Instruction(by={'crank': 10.0}, duration=0.5)`
  beside `'Park': Instruction({'crank': 40.0}, duration=0.5)` and is
  serialized
- **THEN** the instructions table carries `Park` with its targets and no
  entry for `Advance`, and the document is otherwise the one the root
  publishes without `Advance`

#### Scenario: An instruction whose input is owned starts nothing

- **WHEN** a rate command is active on `crank` and an instruction naming
  `crank` and a second input is triggered
- **THEN** the trigger is refused naming `crank` and the owning command,
  and no command was started on either input

#### Scenario: Under a clocked root an instruction is a request

- **WHEN** a clocked root declaring `'Stroke': Instruction(by={'crank': 360.0},
  duration=2.0)` over a register whose stroke commits at every completed
  revolution triggers `Stroke` from rest
- **THEN** `trigger` returns the request `sim.move('crank', by=360.0)` returns
  from the same bank — the same events in the same path order, the same
  admitted travel and the same two ends — and the bank after it is the same
  bank, entry for entry

#### Scenario: A clocked instruction lands an absolute target

- **WHEN** the same root declares `'Set four': Instruction({'operand': 4},
  duration=0.5)` over an integer driver and triggers it
- **THEN** the request is the one `sim.move('operand', to=4)` makes, the
  driver stands at its converted native target, and `trigger` reports it

#### Scenario: The declared duration does not reach the machine

- **WHEN** one clocked root declares an instruction with `duration=2.0` and an
  otherwise identical root declares it with `duration=0.0`, and each is
  triggered from rest
- **THEN** both requests are equal value for value and both banks are equal
  entry for entry: nothing in the machine reads the duration

#### Scenario: A clocked instruction naming two drivers is refused

- **WHEN** a clocked root declares `Instruction(by={'crank': 360.0, 'ring':
  90.0}, duration=1.0)`, or one whose `by` names no driver at all
- **THEN** simulation construction is refused naming the instruction, the
  inputs it names and the one-input rule, and the model publishes no document

#### Scenario: An unknown instruction is refused by name under a clocked root

- **WHEN** a clocked simulation triggers a name nothing declares
- **THEN** it fails listing the declared qualified instruction names, and the
  bank and the tree stand exactly as they did

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
`trigger` and `crossings` — each by name, saying a clocked model has
no clock. `stops` SHALL NOT be among them: a clocked root ADMITS it as the
bounded ring of the bounds its requests stopped at, under the requirement
"A bound stops a clocked request on its path". `sim.running` SHALL remain
`False` over a clocked root, which declares no time base.

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
### Requirement: Scenario testing

The system SHALL provide a scenario test base extending the existing
CAD `TestCase`: a scenario method builds the node once (assembling and
generating STLs where mesh assertions need them), obtains a fresh
simulation per scenario, scripts events and assertions against it, and
runs a bounded time slice. Scenario tests SHALL pass under the plain
pytest suite and under the `machinome test` runner without modification to
either runner.

#### Scenario: A homing scenario asserts along the way

- **WHEN** a scenario triggers a homing instruction at t=0, registers
  an interference assertion at a 0.1 s cadence, checks the terminal
  state with a deferred action, and runs 3.0 s
- **THEN** the assertions execute at their scheduled ticks and the
  test passes exactly when every one holds

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

### Requirement: A driver states a relation to a coordinate

The system SHALL give every `Driver` declaration the verb that states a
relation between two coordinates, so a root class body may write
`art3.drives(shoulder.art2.art3.elbow)` and a driver reach a joint or a
port at any depth without every class between them declaring and
forwarding one. The driver's value SHALL be what reaches the relation:
the bound number under `set_state`, the test runner and the stepped
simulation, and the driver's symbolic token when nothing is bound, so
the relation publishes an expression in that driver's qualified id.

A driver SHALL be a SOURCE only. A `Driver` named as the DRIVEN end of
a relation SHALL be refused at class definition, naming the driver and
saying that its value belongs to the bound snapshot and is set with
`set_state`, which is the rule an assignment to a driver already
states.

A driver's declared range SHALL remain presentation metadata and never
a clamp; a relation SHALL NOT read it and SHALL NOT check against it.
A range declared by a joint the relation drives SHALL apply to the
value that reaches that joint, exactly as it does for a hand binding.

Reaching a driver sideways — reading one off a child declaration in a
class body — SHALL be refused, because a driver is addressed by the
qualified id its position in the tree gives it and a second address for
one value is what that qualification exists to prevent.

#### Scenario: A driver reaches a deep joint

- **WHEN** a root declares `art3 = Driver(...)`, three levels of
  children below it, and states
  `art3.drives(shoulder.art2.art3.elbow)`
- **THEN** the elbow coordinate holds the driver's value on every run,
  the forearm is placed by it, and no intermediate class declares a
  port for it

#### Scenario: A driver drives through a ratio

- **WHEN** a root states `art1.drives(base.pinion.turn, ratio=5.0)` and
  binds `art1` to `12` with `set_state`
- **THEN** the pinion's coordinate reads `60`

#### Scenario: A driver's symbolic read rides through a relation

- **WHEN** the same tree is serialized with nothing bound
- **THEN** the pinion's operation carries an expression in the driver's
  qualified id, and `set_state` makes it numeric

#### Scenario: A driver cannot be driven

- **WHEN** a class body states `some_port.drives(art3)` where `art3` is
  a `Driver` declaration
- **THEN** class definition raises naming the driver and pointing at
  `set_state`

#### Scenario: A driver read off a declaration is refused

- **WHEN** a class body reads a `Driver` off a child declaration
- **THEN** class definition raises, naming the declaration and the
  driver, and the driver's qualified id remains its one address

### Requirement: A running root's simulation owns every driver and joint coordinate

Under a root assembly declaring `time = Time.running()` the simulation
SHALL own a BANK holding every driver AND every joint coordinate of the
linked tree — on assemblies and leaves alike, class-declared and
site-declared joints alike — keyed by the qualified id the driver
enumeration and the port enumeration produce: the instance path joined
with the driver's name, the joint's name, or `<joint>.<coordinate>` for a
joint owning several. `sim.state` SHALL return the whole bank by id, as a
fresh mapping. Plain ports and derived coordinates SHALL NOT be in the
bank: they are computed by the ordinary enumeration from the bank on
every tick. There SHALL be no separate memory bank, and the author SHALL
declare no state. An id two declarations of one node would both claim
SHALL be refused at construction naming both.

The initial bank SHALL be the untimed rest pose at the requested driver
values: construction SHALL bind the driver values (the declared defaults,
overridden by `state=`) with `time` at zero, enumerate the tree once
exactly as an untimed root is enumerated — the author's `simulate()` and
every relation solving as they do today, except a relation that reads its
own driven end, which binds NOTHING at rest under the requirement "A law
may read the coordinate it drives", and a relation the system has
recognized as a member of a BLOCK, which binds NOTHING at rest under the
requirement "A selection decides which sources a law reads" — and read
every joint coordinate off the tree. A joint coordinate that rest render leaves unbound SHALL be
refused at construction naming the node path and the coordinate and
saying that the run owns every joint coordinate and needs a rest value for
each.

From the moment construction completes, every bank coordinate SHALL be
bound by the run — through `set_state` with the whole bank and `time`,
the run recorded as the binder — so that `render()` and `simulate()` stay
pure functions of the bound snapshot: rendering, inspecting, or binding
the same snapshot again SHALL advance nothing and change no value. An
author's `simulate()` that binds a run-owned coordinate SHALL be refused
as doubly bound naming the class and the coordinate, at construction; a
binding written under a guard that finds the coordinate already bound is
not a binding and SHALL keep working.

`sim.time` SHALL remain `tick * dt`, and every instant, duration and
period SHALL keep the whole-tick rule.

ONE simulation SHALL own a tree at a time, and the newest SHALL take it.
Constructing a simulation over a tree a previous run owns SHALL RELEASE that
ownership before the rest render: the run's claim on the tree and on every
joint coordinate it bound is dropped, so the rest render finds a tree no run
owns and poses it exactly as it would a tree no run ever touched. A released
run SHALL REFUSE to advance, naming both simulations and saying its bank no
longer describes the tree, rather than binding over the simulation that now
owns it. This is what makes a fresh simulation per call possible over a node
built once and shared — the contract the scenario base states — and it does
not weaken the doubly-bound refusal: an author's `simulate()` binding of a
run-owned coordinate is still refused, because a release happens only before
the rest render of a NEW simulation and never during one.

A declared driver or joint coordinate whose qualified id is `time` SHALL be
REFUSED at construction, naming the id and the reservation: `time` is the one
snapshot entry that is global by contract, the run binds it beside the whole
bank on every tick, and a bank entry under that id would be silently
overwritten.

#### Scenario: The bank lists joint coordinates by qualified id

- **WHEN** a simulation is constructed over a running root declaring
  drivers `crank` and `lever`, its own joint `spindle` wired into a
  child's plain port `wheel.turn`, children `first` and `second` each
  owning a `turn` joint on a leaf, and a child `slide` owning a `travel`
  joint
- **THEN** `sim.state` has exactly the keys `crank`, `lever`, `spindle`,
  `first.turn`, `second.turn` and `slide.travel` — the plain port
  `wheel.turn` among them nowhere

#### Scenario: The initial bank is the rest pose

- **WHEN** the same root states `crank.drives(first.turn, ratio=2.0)`,
  `first.turn.drives(second.turn, ratio=-1.5)` and
  `lever.drives(slide.travel, law=tooth_window)`, and the simulation is
  constructed with `state={'crank': 10.0}`
- **THEN** the initial bank reads `first.turn == 20.0`,
  `second.turn == -30.0` and `slide.travel` equal to the law at the
  lever's default — the values the untimed root poses at

#### Scenario: Rendering and rebinding advance nothing

- **WHEN** a running simulation has moved its crank for ten ticks and the
  caller then renders the node, reads every coordinate, and calls
  `set_state` with `sim.state` and `time=sim.time` once more
- **THEN** `sim.state`, `sim.tick` and every joint coordinate on the tree
  are unchanged, and the next tick continues from the same bank

#### Scenario: An author binding of a run-owned coordinate is refused

- **WHEN** a running root's `simulate()` binds `self.first.turn` from its
  crank unconditionally
- **THEN** construction is refused naming that class and `first.turn` as
  doubly bound, saying the running simulation owns it and a law belongs
  in a relation

#### Scenario: A guarded rest default keeps working

- **WHEN** a running root's `simulate()` reads `self.slide.travel.value`,
  finds it `None` and binds `4.0`
- **THEN** construction succeeds, the bank reads `slide.travel == 4.0`, and
  the guard never binds again while the run owns the coordinate

#### Scenario: An unbound joint coordinate is refused at construction

- **WHEN** a running root's rest render leaves a joint coordinate unbound —
  nothing drives it and no `simulate()` binds it
- **THEN** construction is refused naming its qualified id and saying the
  run needs a rest value for every joint coordinate

#### Scenario: A joint on a leaf is owned like any other

- **WHEN** the joint `turn` is declared on a leaf class held as `first`
- **THEN** `first.turn` is in the bank, the run binds it on every tick, and
  the leaf's body is placed by the bound value

#### Scenario: A second simulation over one tree starts fresh

- **WHEN** a simulation over a running root has moved its crank for twenty
  ticks and a second simulation is constructed over the SAME node
- **THEN** construction succeeds, the second simulation's bank is the rest
  pose — identical to the first's initial snapshot — and nothing is refused
  as doubly bound

#### Scenario: A released simulation refuses to advance

- **WHEN** a simulation whose tree a later simulation has taken over is
  stepped
- **THEN** it refuses naming both simulations and saying its bank no longer
  describes the tree, and the tree is left as the owning simulation posed it

#### Scenario: An author binding is still refused

- **WHEN** a running root's `simulate()` binds a run-owned coordinate
  unconditionally
- **THEN** construction is refused as doubly bound, naming the class and the
  coordinate, exactly as before

#### Scenario: A driver named for the clock is refused

- **WHEN** a running root declares a driver whose qualified id is `time`
- **THEN** construction is refused naming the id and saying `time` is
  reserved for the simulation clock

#### Scenario: A rest default under a self-read relation is the bank's value

- **WHEN** a running root states
  `(rack & wheel.turn).drives(wheel.turn, law=missing_tooth)` and the
  wheel's own `simulate()` binds `108.0` under `if ... is None`
- **THEN** construction succeeds, the initial bank reads
  `wheel.turn == 108.0`, the relation bound nothing at rest, and nothing
  is refused as doubly bound

#### Scenario: A self-read relation with no rest default is refused

- **WHEN** the same root's wheel declares no rest default, so the rest
  render leaves `wheel.turn` unbound
- **THEN** construction is refused naming that qualified id and saying
  the run needs a rest value for every joint coordinate

#### Scenario: A rest default under a block relation is the bank's value

- **WHEN** a running root states two relations whose union is cyclic and
  whose selections are mutually exclusive comparisons on a live input,
  and each driven coordinate's own `simulate()` binds a value under
  `if ... is None`
- **THEN** construction succeeds, the initial bank reads each of those
  rest values, neither relation bound anything at rest, and nothing is
  refused as doubly bound

#### Scenario: A block relation with no rest default is refused

- **WHEN** the same root's driven coordinates declare no rest default, so
  the rest render leaves them unbound
- **THEN** construction is refused naming a qualified id and saying the
  run needs a rest value for every joint coordinate

### Requirement: Qualified bank delivery is scoped to each coordinate's owner

Under a running root, binding the run's whole bank SHALL leave every qualified
joint-coordinate entry equal to its owning joint's bound value. The rendered
world pose SHALL compose those owner-specific joint placements with declared
rest placements and ancestor transforms. The result SHALL be independent of
the bank mapping's insertion order and SHALL apply equally to
single-coordinate, multi-coordinate, class-declared and site-declared joints.
Supported bare drivers and the global `time` entry SHALL retain their
established values and reach; existing qualified-name validation, ambiguity
refusals and rollback SHALL remain unchanged.

#### Scenario: Parent and descendant joints keep independent retained poses

- **WHEN** three nested nodes each own a `turn` joint, a running simulation
  moves the parent while the child and grandchild retain different values, and
  then moves the child while the other two retain theirs
- **THEN** after each request every joint's bound value equals its `sim.state`
  entry, its local joint placement represents that value, each world pose
  composes those local placements with its rest and ancestor transforms, and
  neither ancestor nor descendant receives another owner's `turn`

#### Scenario: Full-bank binding is independent of mapping order

- **WHEN** the same complete bank and `time` are rebound once in program order
  and once in reverse insertion order
- **THEN** both bindings leave every node at the same owner-specific coordinate
  and the same composed world pose, without advancing the simulation

#### Scenario: Restore and reset pose the whole nested tree from their banks

- **WHEN** a nested running mechanism takes a snapshot, moves parent and child
  coordinates independently, restores the snapshot, and then resets
- **THEN** each operation restores the bank, bound joints and rendered poses
  together, with reset returning every owner to the initial bank

#### Scenario: Every declared joint form uses the same owner boundary

- **WHEN** full-bank delivery reaches nested class-declared and site-declared
  joints, including a joint with several coordinates
- **THEN** every qualified coordinate binds only its declared owner and each
  joint is placed from its own complete coordinate set

#### Scenario: Bare drivers and time retain their established reach

- **WHEN** a running tree receives a supported bare driver, qualified drivers
  for otherwise ambiguous descendants, owner-qualified joint coordinates and
  the global `time` entry together
- **THEN** the bare driver and `time` propagate as before, each qualified entry
  reaches only its addressed owner, and an ambiguous bare driver is still
  refused rather than applied to several declarations

#### Scenario: An ambiguous bare coordinate name remains ambiguous

- **WHEN** a caller binds bare `turn` on a running tree with several nested
  owners of `turn`, or with a descendant driver of that name
- **THEN** binding is refused as ambiguous naming every matching qualified ID,
  and the complete previous bank and pose are restored

#### Scenario: Symbolic publication restores the numeric nested pose

- **WHEN** a document is published from a live running tree whose nested joints
  share local coordinate names and hold distinct retained values
- **THEN** the document's operations refer to each joint's own qualified
  coordinate, publication changes neither schema nor version, and afterward
  every bank entry, bound joint and rendered numeric pose is exactly as before
  publication

### Requirement: A continuous law is integrated over a tick and increments propagate

Under a running root the driven coordinate of a relation SHALL move BY the
change of its law along its sources' movement, from where it stood: over
one tick a CONTINUOUS law contributes exactly `f(end) − f(start)`, `f`
being the law's `forward` face — or its `inverse` face where the rest
render solved the relation backward — evaluated over the sources' values
at the start and at the end of the tick. This SHALL be exact across the
kinks of `abs`, `min` and `max` and of the compositions built on them
(`clamp`, `clamp01`, `ramp`, `piecewise`), because it is the difference
of two exact evaluations. A law whose increment is zero although its
source moved SHALL contribute nothing, which is what disengagement is.
A law whose expression contains a DISCONTINUOUS primitive SHALL
contribute the sum of its change over the continuous pieces between its
crossings, under the requirement "A jump is located inside the tick and
subtracted"; every other rule of this requirement applies to it
unchanged.

The tick SHALL be: every input's increment is the movement its active
command admits for the tick, zero with no command. In addition, explicit
time-source relations SHALL admit the elapsed interval under "Declared time
drives retain motion across operating history"; no command is required for
those sources. The same incremental reading SHALL apply to their laws, and
time SHALL remain read-only. Increments SHALL then
propagate over the relation graph in the direction each relation was
solved by the rest render — forward through a law, backward through an
invertible one, identity through a wiring into a bank coordinate,
forward or backward through a derived coordinate's linear formula —
every source of a relation naming several being determined before it
contributes. A coordinate no increment reaches SHALL HOLD its committed
value. Two increments that disagree on one coordinate — beyond
`1e-9 · max(1, |a|, |b|)` — SHALL be a CONFLICT, refused naming the
formula or relation that predicted each and the coordinate. A joint
coordinate whose new value would leave its declared range SHALL NOT
fail the tick: it SHALL STOP at its bound under the requirement "A
declared range is a physical stop located inside the tick", which
splits the tick into segments and integrates each by this requirement
unchanged. A tick that fails
SHALL commit nothing: the bank, the tick count and the bound tree stand
as before, every segment of it included, and every command that moved
an input in that tick is
retired reporting `refused`. A tick that succeeds SHALL commit the
increments, advance the tick count, bind the whole snapshot through
`set_state` with `time` at `k*dt`, record if recording is on, and only
then run due actions and cadences.

Derived coordinates and plain ports SHALL NOT be stored: the ordinary
enumeration computes them from the run-bound terms on every tick.

#### Scenario: Moves accumulate and an affine chain follows

- **WHEN** a running root states `crank.drives(first.turn, ratio=2.0)`
  and `first.turn.drives(second.turn, ratio=-1.5)`, and the simulation
  moves `crank` by `10` over one second twice
- **THEN** the bank reads `crank == 20`, `first.turn == 40` and
  `second.turn == -60`, and the leaves stand at those angles

#### Scenario: A law with a kink integrates exactly

- **WHEN** `lever.drives(slide.travel, law=tooth_window)` carries
  `4 + 72 * clamp01((angle − 113.5) / 11.25)` and `lever` moves from
  `100` to `140` in eight ticks of five degrees
- **THEN** `slide.travel` reads exactly `13.6` after the third tick,
  `45.6` after the fourth, `76.0` from the fifth on, and stays `76.0`
  while the lever goes on to `140`

#### Scenario: Backward propagation through an invertible law

- **WHEN** a running root states `crank.drives(first.turn, ratio=2.0)`
  and `second.turn.drives(first.turn, ratio=4.0)`, so the rest render
  solved the second relation backward, and `crank` moves by `10`
- **THEN** `first.turn` reads `20` and `second.turn` reads `5`, the
  inverse of the affine law having propagated the increment

#### Scenario: An undriven joint holds while an unrelated input moves

- **WHEN** the crank of the same root moves while `lever` has no command
- **THEN** `slide.travel` and `lever` read exactly what they read before
  the move, on every tick

#### Scenario: Two inputs prescribing one rigid group inconsistently are refused

- **WHEN** a running root declares `wrist` and `tool` joints,
  `left = wrist + 2 * tool`, and states `wrist_in.drives(wrist)`,
  `wrist.drives(tool, ratio=1.0)` and `sum_in.drives(left)`, and the
  simulation moves `wrist_in` by `10` while `sum_in` has no command
- **THEN** the tick is refused naming `left`, the formula, the relation
  from `sum_in` and the two increments `0` and `30`; the bank, the tick
  count and the tree are unchanged; the move's handle reports `refused`
  with no travel admitted

#### Scenario: The same group moved consistently is admitted

- **WHEN** the same simulation moves `wrist_in` by `10` and `sum_in` by
  `30` over the same duration
- **THEN** every tick is admitted and the bank reads `wrist == 10`,
  `tool == 10` and the derived `left` reads `30`

#### Scenario: A joint's range stops the tick's motion rather than failing it

- **WHEN** `first.turn` declares `range=(-90, 90)` and the crank is moved
  so that `first.turn` would reach `100`
- **THEN** the tick commits with `first.turn` at exactly `90`, the tick
  count advances, and the move's handle reports `blocked` with the
  travel it admitted

### Requirement: A relation's law is compiled to an expression over coordinate ids

At construction under a running root the system SHALL COMPILE the
relations the rest render solved into a program over the bank: each
relation's law SHALL be applied ONCE to a symbolic token per source
coordinate, in the direction the rest render solved it, and the
expression graph that application builds — over the qualified ids of
the sources — SHALL be what the run evaluates on every tick and what
the refusals below inspect. A graph containing a DISCONTINUOUS
primitive — a call to `floor`, `ceil` or `sign`, the `%` operator, or a
comparison — SHALL additionally be compiled into a JUMP PLAN: its jump
nodes in the graph's postorder, each with the level quantity whose
surfaces it crosses, the graph of that level quantity with the jump
nodes inside it replaced by branch placeholders, whether that level
quantity is AFFINE in the sources, and the SKELETON of the whole
expression with every jump node so replaced. A wiring into a bank
coordinate SHALL be an
identity edge and a derived coordinate a linear edge.

The compiled edges SHALL be ORDERED so that every edge's sources are
determined before it runs: over the DEPENDENCY GRAPH in which edge A
precedes edge B when B reads a coordinate A determines — a coordinate an
edge itself determines EXCLUDED, because that is a read of what the
coordinate holds — the edges SHALL be ordered topologically, with each
nontrivial STRONGLY CONNECTED COMPONENT of that graph contracted to ONE
entry, a BLOCK, under the requirement "A selection decides which sources
a law reads". A coordinate no edge determines SHALL be resolved from the
start: it is an input, or it HOLDS. A relation or
wiring none of whose driven ends is, or reaches through such
intermediates, a bank coordinate SHALL be left to the ordinary
enumeration, and SHALL leave nothing of itself in the program: the
program's COORDINATES SHALL be the bank's, plus exactly the ends its
compiled edges read and give. An end of a relation left to the ordinary
enumeration SHALL NOT be a coordinate of the program, SHALL NOT be
published as one, and SHALL NOT be a reason to refuse the program — the
run never computes it, and the ordinary enumeration recomputes it from
the bank on every tick exactly as it does under no time base at all.
The program SHALL have an IDENTITY derived from the root
class, the bank's ids, the inputs' declarations and every edge's ends,
direction and expression.

The system SHALL refuse, at construction and by relation identity —
naming the relation as written and the class that stated it:

- a law that cannot be applied to symbols — one that raises when handed
  a symbolic token, returns something that is neither a number nor an
  expression, or whose expression holds text the framework cannot
  evaluate or a call outside the symbolic vocabulary — saying that a
  running law is an expression over its sources;
- a relation or wiring INTO a bank coordinate whose source is a
  coordinate the run does not own and no compiled edge computes, EXCEPT
  the root's explicitly declared running time source — a
  plain port the author's `simulate()` binds — saying to state that
  value as a relation or a joint;
- a compiled law with a free clock name not declared among its sources,
  including a symbolic `owner.time` captured by a factory — naming the
  relation and showing the explicit `time` source in `drives` as the repair;
  no implicit time dependency SHALL be inferred. Any other unsupported free
  name SHALL likewise be refused as outside the declared sources. This
  does not claim to detect a Python read already reduced to a numeric
  constant before graph compilation;
- a relation naming several driven ends of which some are bank
  coordinates and some are not;
- a set of relations whose dependencies form a CYCLE that no selection
  breaks — naming every relation on the cycle and the coordinates they
  wait on, saying that a running program is ordered before it runs, and
  saying what a switch would be, in the terms the requirement "A
  selection decides which sources a law reads" defines: a source that
  folding a jump node to zero removes from the law, where that node's
  level reads no coordinate the cycle determines and its zero branch is
  one the node holds over an interval of that level — so a `sign` is not
  one;
- a law whose expression contains a DISCONTINUOUS primitive and none of
  whose driven ends is a coordinate the run owns — a plain port or a
  derived coordinate the ordinary enumeration recomputes from the bank
  on every tick — saying that a subtracted jump implies a history,
  that only a coordinate the run owns keeps one, and that the relation
  should be stated into the joint coordinate so the port follows it.

A law whose expression has no free coordinate — a constant — SHALL
compile and contribute a zero increment; a law that can move its
coordinate only by jumping SHALL be refused under the requirement "A
law that can only jump is refused as arithmetic".

#### Scenario: A running root with a floor in a law compiles

- **WHEN** a running root states `crank.drives(first.turn, law=window)`
  where the law's expression contains `floor(angle / 360)`
- **THEN** construction succeeds, the compiled graph names the source's
  qualified id, its jump plan holds one `floor` node whose level
  quantity is that qualified id divided by 360 and is AFFINE in the
  sources, and the same root without `Time.running()` poses exactly as
  before

#### Scenario: A jumping law into a plain port is refused

- **WHEN** a running root states `crank.drives(register, law=window)`
  where `register` is a plain port wired to a joint coordinate and the
  law's expression contains `floor`
- **THEN** construction is refused naming the relation and the port, and
  saying to state the relation into the joint coordinate the run owns;
  and the same relation stated into that joint coordinate compiles

#### Scenario: A law over stdlib math is refused as non-symbolic

- **WHEN** a running root's law computes `math.sin(angle)` from Python's
  standard library
- **THEN** construction is refused naming the relation and saying the law
  cannot be applied to symbols

#### Scenario: A relation sourced from an author-bound port is refused

- **WHEN** a running root's `simulate()` binds a plain port from its
  crank and a relation drives a joint from that port
- **THEN** construction is refused naming the relation and the port, and
  advising a relation or a joint

#### Scenario: A law with a kink compiles

- **WHEN** a running root's law is `4 + 72 * clamp01((angle − 113.5) / 11.25)`
- **THEN** construction succeeds and the compiled expression names the
  source's qualified id and only `min` and `max` among calls

#### Scenario: A relation the enumeration keeps leaves no coordinate in the program

- **WHEN** a running root drives the `height` port of its `.repeat()`
  children, and no relation carries those ports back to a joint
  coordinate
- **THEN** the compiled program's coordinates are the driver and the
  joint coordinates only, no copy's port is among them, the program's
  edges are unchanged, and the run poses every copy exactly as the same
  root without `Time.running()` does

#### Scenario: A part this render omits leaves no coordinate in the program

- **WHEN** a running root holds an optional part whose joint one of its
  drivers drives, and this render `omit()`s that part
- **THEN** the compiled program's coordinates are the driver and the
  joint coordinates of the parts that ARE in the machine, the omitted
  part's coordinate is not among them, and construction succeeds

#### Scenario: Two relations waiting on each other are refused

- **WHEN** a running root states `(a & b.turn).drives(c.turn, law=...)`
  and `(a & c.turn).drives(b.turn, law=...)`, neither law gating the
  other's coordinate behind a jump node
- **THEN** construction is refused naming BOTH relations and saying they
  form a cycle the run cannot order

#### Scenario: A wiring on a cycle is refused by name

- **WHEN** a running root states a cycle one of whose steps is a wiring
  or a derived coordinate rather than a law
- **THEN** construction is refused naming that wiring or derived
  coordinate and saying it carries no jump node and therefore no
  selection

#### Scenario: Captured symbolic time is not a hidden motor

- **WHEN** a compiled running law closes over symbolic `owner.time` but
  its relation names only ordinary coordinates as sources
- **THEN** construction refuses it by relation identity and explains how
  to name the root's `time` in the source group, rather than accepting a
  law whose free clock is never advanced

#### Scenario: An explicit time source is owned by the run clock

- **WHEN** a running law names the root's `time` as a source
- **THEN** compilation recognizes a read-only clock path rather than
  refusing it as an unowned port, and preserves all existing law-class
  checks, including refusal of unsupported self-read arithmetic

### Requirement: A jump is located inside the tick and subtracted

Under a running root a law whose expression contains a DISCONTINUOUS
primitive SHALL contribute, over one tick, the CONTINUOUS part of its
change: the tick's path SHALL be cut at every crossing of every jump
surface it meets, and the law's change SHALL be summed over the pieces
between those cuts, so that no jump ever moves a part.

The PATH of a tick SHALL follow each source's physical motion at the same
fraction `t` in `[0, 1]`: commanded linear motion for an input, constant motion
for a held coordinate, and law-determined motion for a driven source. Driven
sources SHALL retain dwell, kink, crossing and landing timing through ordinary
chains as well as selected blocks, rather than interpolate their net increments.
For a law naming several sources these paths SHALL be read jointly at that
same fraction. A tick in which no source moves SHALL
contribute zero without evaluating the law.

Each jump node SHALL have a LEVEL QUANTITY and a family of SURFACES:
`floor(x)` and `ceil(x)` over `x` at every integer; `sign(x)` over `x`
at zero; `a % b` over `a / b` at every NONZERO integer, the operator
being the remainder that takes the sign of the DIVIDEND and is
therefore continuous where `a / b` crosses zero; a comparison over
`a − b` at zero. `wrap()` SHALL be integrated as the `ceil` it is built
on, and `piecewise()` SHALL need nothing, being built on `clamp01`.

On each open piece between two cuts every jump node SHALL hold one
BRANCH — the integer for `floor` and `ceil`, `-1`, `0` or `+1` for
`sign`, the integer quotient for `%` so that the node reads `a − q·b`,
and `1` or `0` for a comparison — determined by evaluating its level
quantity at the MIDPOINT of that piece, in the graph's postorder so
that a jump nested inside another's argument is determined first — with
the one amendment the requirement "A law may read the coordinate it
drives" states for a node that DEPENDS on the law's own driven
coordinate, whose value at a midpoint is a consequence of the branch
being asked for. The
law with those branches substituted SHALL be continuous on the closed
piece, and the increment SHALL be the sum, over the pieces, of that
substituted law's value at the piece's end minus its value at the
piece's start. A piece's endpoints SHALL therefore carry the one-sided
values of the law, at the tick's own start and end as well as at each
cut.

Crossings SHALL be found for every jump node of the law, in the graph's
postorder, over each piece the nodes before it have already produced,
and ALL crossings of one node inside one piece SHALL be found — not
only the difference of the piece's endpoints. Where the level quantity
is AFFINE in the sources along the path the crossings SHALL be solved
exactly, every surface between the endpoint values included. Where it is
PIECEWISE AFFINE — the requirement "A kink is a cut, and a
piecewise-affine quantity is solved" — the piece SHALL be SUB-DIVIDED at
that level's own kink breakpoints and the crossings SHALL be solved
exactly on each sub-piece, again every surface between that sub-piece's
endpoint values included. Otherwise
the piece SHALL be sampled at a fixed number of sub-intervals and each
bracketed crossing located by bisection to a stated tolerance, with the
limit of that search documented. Two crossings closer than the
tolerance SHALL be one cut, and several jump nodes crossing at one
fraction SHALL be one cut whose midpoint sample fixes every branch at
once. For a law that reads its own driven coordinate THIS partition SHALL be
built over the jump nodes that do NOT depend on that coordinate, and the
nodes that DO SHALL be walked piece by piece INSIDE each of its pieces,
under the requirement "A law may read the coordinate it drives", because
the path of that coordinate on one piece is a consequence of the
branches of the piece before it. Merging two crossings closer than the
tolerance into one cut belongs to THIS partition and SHALL NOT be
applied in that walk.

A tick that would cut one law's path more than a stated maximum number
of times SHALL be refused naming the relation, the driven coordinate,
the primitive and the count, and SHALL commit nothing — the bank, the
tick count and the bound tree standing as before and the commands that
moved an input in it retired reporting `refused` — exactly as a
conflict does. A `%` whose divisor is zero anywhere the tick evaluates
SHALL be refused the same way.

#### Scenario: A periodic window advances once per revolution

- **WHEN** a running root states
  `crank.drives(pinion.turn, law=periodic_window)` carrying
  `4 + 72 * clamp01((angle − 360 * floor(angle / 360) − 113.5) / 11.25)`,
  the crank rests at `100`, `dt` is `1/240`, and the simulation moves
  `crank` by `360` over one second, twice
- **THEN** `pinion.turn` reads `4` before the first move, `76` after it
  and `148` after the second, and the tick in which the crank passes
  `360` contributes exactly zero

#### Scenario: A tick that passes three windows adds three throws

- **WHEN** the same root is given `move('crank', by=1080, duration=0)`
  from a crank of `100`
- **THEN** `pinion.turn` reads `220`, three crossings are located inside
  that one tick, and the crank stands at `1180`

#### Scenario: A gate holds open and re-engages without a jump

- **WHEN** a running root states
  `(shaft.turn & sleeve.travel).drives(wheel.turn, law=clutch)` carrying
  `-2 * shaft * (sleeve > 0.5)`, and the shaft turns by `4` over a tick
  in which the sleeve stands at `0`, then over a tick in which it
  stands at `1`, then over a tick in which it travels from `0` to `1`
- **THEN** `wheel.turn` moves by `0`, then by `-8`, then by `-4` — the
  travel after engagement only — and never by the value the gate factor
  would have jumped to

#### Scenario: A wrapped law integrates to the unwrapped travel

- **WHEN** a running root's law is `2 * wrap(angle, 360)` and the crank
  travels `500` degrees from `100`
- **THEN** the driven coordinate gains exactly `1000`, and the two
  `ceil` crossings inside that travel contribute nothing of their own

#### Scenario: A remainder window and a floor window agree

- **WHEN** two running roots carry the same tooth window, one written
  with `angle − 360 * floor(angle / 360)` and one with `angle % 360`,
  and both cranks are moved through one revolution from `100`
- **THEN** both driven coordinates read the same value at every tick

#### Scenario: A sign that does not jump integrates as its continuous twin

- **WHEN** a running root's law is `5 * (x − 50) * sign(x − 50)` and a
  second root's is `5 * abs(x − 50)`, and both are driven across `50`
- **THEN** both driven coordinates read the same value at every tick,
  the crossing of `sign` having been located and contributed nothing

#### Scenario: A jump nested in another jump's argument

- **WHEN** a running root's law engages only on alternate revolutions,
  `72 * clamp01((angle − 360 * w − 113.5) / 11.25) * (1 − (w − 2 * floor(w / 2)))`
  with `w = floor(angle / 360)`, and the crank is moved through four
  revolutions from `100`
- **THEN** the driven coordinate reads `72` after the first revolution,
  `72` after the second, `144` after the third and `144` after the
  fourth

#### Scenario: The same movement split differently gives the same answer

- **WHEN** one running simulation takes a revolution of the crank in a
  single tick, another in twelve, and another in two hundred and forty
- **THEN** all three leave the driven coordinate at the same value

#### Scenario: A tick that would cross too many surfaces is refused

- **WHEN** a periodic law is driven far enough in one tick to cross more
  surfaces than the stated maximum
- **THEN** the tick is refused naming the relation, the coordinate, the
  primitive and the count; the bank, the tick count and the tree are
  unchanged; and the move's handle reports `refused`

### Requirement: A law that can only jump is refused as arithmetic

Under a running root the system SHALL REFUSE, at construction and by
relation identity — naming the relation as written and the class that
stated it — a law that can move its driven coordinate only by jumping:
the law's expression with every jump node, and the whole argument
subtree beneath it, replaced by a constant SHALL be examined, and a law
whose expression so reduced holds no free coordinate SHALL be refused.
The message SHALL say that every jump is subtracted, so such a law can
never move the coordinate, and that it states arithmetic rather than a
mechanism.

A law whose reduced expression still holds a free coordinate SHALL
compile, whatever else it contains.

#### Scenario: A law that is only a step counter is refused

- **WHEN** a running root states `crank.drives(dial.value, law=counter)`
  whose expression is `floor(turns)`
- **THEN** construction is refused naming that relation and saying the
  law can only jump and states arithmetic rather than a mechanism

#### Scenario: A jump beside a sloped term compiles

- **WHEN** a running root's law is `9 * enabled + floor(turns)` over two
  sources
- **THEN** construction succeeds, because `enabled` still carries slope,
  and moving `turns` alone moves the coordinate not at all

#### Scenario: A periodic window is not a law that only jumps

- **WHEN** a running root's law is
  `4 + 72 * clamp01((angle − 360 * floor(angle / 360) − 113.5) / 11.25)`
- **THEN** construction succeeds, the reduced expression still naming
  `angle`

### Requirement: Commands have one owner per input and report their outcome

Under a running root the system SHALL provide one path for every
movement request: `move(input, by=..., duration=...)`,
`move(input, to=..., duration=...)`, `rate(input, rate)` and
`trigger(name)`. `input` SHALL be the qualified id of a declared driver;
naming anything else — a joint coordinate, an unknown id — SHALL be
refused naming the id and the declared inputs. `by`, `to` and `rate` are
stated in the input's DESIGN units and converted through its declared
scale once; `rate` is design units per simulated second; `duration` is a
whole number of ticks, zero included. Exactly one of `by`/`to` SHALL be
given.

Each input SHALL have ONE OWNER at a time: a move or a rate on an input
that an active move or rate already owns SHALL be refused naming the
input and the owning command. `rate(input, 0)` SHALL release the active
rate, completing it, and SHALL be a no-op on an input no rate owns. A
REVERSE request — negative `by`, a `to` below the committed value, a
negative `rate` — SHALL be admitted and SHALL meet a declared range as
a physical stop exactly as a forward request does.

`move` and `rate` SHALL return a HANDLE reporting the input, the kind,
the status — `active`, `completed`, `blocked`, `refused` or `cancelled`
— the travel requested and the travel actually ADMITTED so far, in
design units, and offering `cancel()`. A request that fails validation SHALL
raise rather than return a handle; `refused` is the status of a command
whose tick failed, and `blocked` the status of one whose input was
stopped. Per-tick admission SHALL be a pure function of the
tick count since the command started: a move distributes its travel as
the ramp program does, integer-exact for an integer input and landing
exactly, in either direction; a rate admits the difference of its
cumulative travel at successive ticks, TRUNCATED TOWARD ZERO for an
integer input so that the two directions round alike. A zero-duration move
SHALL integrate at once at the current tick without advancing it.
A command whose input is STOPPED SHALL be retired reporting `blocked`,
with the travel it actually admitted — every completed tick's travel
plus the fraction of the stopping tick's travel it made before the
stop — and SHALL NOT resume: no travel it did not make is remembered
anywhere, and a later tick SHALL NOT continue it. A `rate` on a stopped
input SHALL be retired `blocked` in the same way. A new request on that
input SHALL be accepted at once, and SHALL be blocked again with `0`
admitted if it pushes into the same stop. A request that lands EXACTLY
on a bound SHALL report `completed`, the bounds being inclusive. Where
one instruction names several inputs, EACH command SHALL report for
itself and no instruction-level summary SHALL be owed: an instruction
one of whose inputs is stopped reports that handle `blocked` and the
others by their own outcome.

`cancel()` on a handle SHALL STOP that command where it stands. The
command SHALL be RETIRED at once, reporting `cancelled` with the travel
it had actually admitted; its input SHALL be free from the moment
`cancel()` returns, so a move or a rate on that input SHALL be accepted
at the same tick with no tick passing in between; and it SHALL admit
nothing further — every tick from the next one on admits nothing for it,
and no travel it did not make is remembered anywhere, the rule a
`blocked` command already states. This SHALL hold wherever the command
stands: before its first tick, part way through a move, and on a rate,
which has no end of its own. `cancel()` SHALL return the handle.
`cancel()` on a command ALREADY RETIRED — `completed`, `blocked`,
`refused` or `cancelled` — SHALL preserve what that handle reported and
SHALL NOT touch whatever command owns its input now, so cancelling twice
is cancelling once. Cancelling one command SHALL leave every other
command running, the sibling commands of one instruction included.
Cancellation is a caller's action AT A TICK and never a wall-clock
event: per-tick admission stays a pure function of the tick count since
the command started, so a script replayed with the same requests,
cancellations and steps in the same order SHALL admit exactly the same
travel.

`sim.commands` SHALL be the active handles; a command SHALL be RETIRED
from them the tick it completes, blocks or is refused, and the moment it
is cancelled, so a long run
accumulates no finished
commands, while the handle the caller holds keeps reporting.

#### Scenario: A rate and a move on one input are an ownership conflict

- **WHEN** `rate('crank', 90.0)` is active and `move('crank', by=10, duration=1.0)`
  is requested, or two moves are requested on `crank`
- **THEN** the second request is refused naming `crank` and the owning
  command, and the first command keeps running

#### Scenario: A rate accumulates until released

- **WHEN** `rate('crank', 90.0)` runs for two seconds and `rate('crank', 0)`
  is then called
- **THEN** the crank has moved `180` and its joints followed, the handle
  reports `completed` with `180` admitted, and `sim.commands` is empty

#### Scenario: A reverse move runs

- **WHEN** `move('crank', by=-10, duration=1.0)`, `move('crank', to=5, duration=1.0)`
  from `20`, or `rate('crank', -90.0)` is requested on a crank meeting no
  stop
- **THEN** each runs, the bank and the driven coordinates follow
  backwards through the same laws, and each handle reports `completed`
  with its travel admitted

#### Scenario: A blocked command does not resume and reports its travel

- **WHEN** a move whose input is stopped part way through a tick is
  followed by ten more ticks with no new command
- **THEN** the handle reports `blocked` with the travel made up to the
  stop, `sim.commands` is empty, the coordinate stands at its bound
  through all ten ticks, and a new move on that input is accepted at once

#### Scenario: An instruction naming two inputs reports each for itself

- **WHEN** an instruction moves a stopped input and a free one over the
  same duration
- **THEN** its handle tuple holds one `blocked` handle with the fraction
  of its travel it made and one `completed` handle with all of its own,
  and the free input was not held back

#### Scenario: Only a declared input can be moved

- **WHEN** `move('first.turn', by=10, duration=1.0)` names a joint
  coordinate
- **THEN** it is refused naming `first.turn` and listing the declared
  inputs

#### Scenario: Completed commands are retired

- **WHEN** one hundred single-tick moves are issued one after another,
  each after the previous completed
- **THEN** `sim.commands` never holds more than one entry, every handle
  reports `completed`, and the crank has moved the sum of the travels

#### Scenario: A zero-duration move integrates now

- **WHEN** `move('crank', by=10, duration=0)` is requested at tick 20
- **THEN** the bank and the tree reflect the move at tick 20, the handle
  reports `completed`, and no tick was added

#### Scenario: A failed tick retires its commands as refused

- **WHEN** a move's tick is refused as a conflict
- **THEN** the handle reports `refused` with the travel admitted before
  that tick, `sim.commands` no longer holds it, and the run continues from
  the last committed bank once a consistent command is issued

#### Scenario: A move cancelled before its first tick moves nothing

- **WHEN** `move('feed', by=5, duration=0.2)` is cancelled at the tick it
  was issued on, at `dt=0.02`, and the simulation is then stepped one
  tick
- **THEN** the handle reports `cancelled` with `0` admitted, the input
  and every coordinate it drives stand where they stood, and
  `sim.commands` is empty

#### Scenario: A move cancelled part way keeps the travel it made

- **WHEN** a ten-tick `move('feed', by=5, duration=0.2)` is stepped three
  ticks, cancelled, and the simulation is stepped seven more
- **THEN** the handle reports `cancelled` with the travel of those three
  ticks, the bank stands at that travel through all seven remaining
  ticks, and `sim.commands` is empty

#### Scenario: A cancelled rate stops

- **WHEN** `rate('feed', 10)` is stepped three ticks, cancelled, and the
  simulation is stepped three more
- **THEN** the handle reports `cancelled` with the travel of those three
  ticks and the input does not move again

#### Scenario: A cancelled command's input takes a replacement at once

- **WHEN** a move is cancelled and a new `move` on the same input is
  requested before any tick is stepped
- **THEN** the request is accepted, the new handle is the input's only
  entry in `sim.commands`, and it runs from the bank as the cancelled
  command left it

#### Scenario: Cancelling twice is cancelling once

- **WHEN** a handle is cancelled, a replacement command is issued on the
  same input, and the first handle is cancelled again
- **THEN** the first handle still reports `cancelled` with what it had
  admitted, and the replacement is still active, still owns the input
  and goes on running

#### Scenario: A retired handle keeps what it reported

- **WHEN** `cancel()` is called on a handle that already reports
  `completed`, `blocked` or `refused`
- **THEN** the handle keeps that status and its admitted travel, and
  `sim.commands` is unchanged

#### Scenario: Cancelling one command leaves the others running

- **WHEN** an instruction issues commands on two inputs over the same
  duration and one of the two handles is cancelled
- **THEN** that input stops where it stands and the other command runs
  to `completed` with all of its own travel admitted

#### Scenario: A cancelled run replays identically

- **WHEN** the same machine is stepped twice with the same requests,
  cancellations and steps in the same order
- **THEN** the bank, the tick and every handle's status and admitted
  travel are equal at every step

### Requirement: Snapshot, restore and reset act on the run's bank

Under a running root `sim.snapshot()` SHALL return a VALUE OBJECT holding
the compiled program's identity, `dt`, the tick, the whole bank and the
active commands with their progress; two snapshots of one state SHALL
compare equal. `sim.restore(snapshot)` SHALL compare the program identity
and `dt` FIRST and refuse a mismatch naming both, touching nothing; it
SHALL then replace the bank, the tick and the active commands, clear the
recording, and bind the restored bank to the tree. Handles issued before a
restore SHALL report `cancelled` with what they had admitted; the restored
commands SHALL be reachable through `sim.commands` and continue from their
recorded progress. `sim.initial` SHALL be the snapshot taken at
construction and `sim.reset()` SHALL be `restore(sim.initial)`.

#### Scenario: A snapshot restores mid-run

- **WHEN** a simulation runs five ticks of a ten-tick move, takes a
  snapshot, runs the remaining five, restores the snapshot and runs five
  again
- **THEN** after the restore the bank, the tick and the tree equal the
  snapshot's, and after the second five ticks they equal what the first
  completion produced

#### Scenario: A mismatched program or dt is refused before anything changes

- **WHEN** a snapshot taken over a different root class, or over the same
  class at a different `dt`, is restored
- **THEN** the restore is refused naming the two identities or the two
  steps, and the bank, the tick and the commands are unchanged

#### Scenario: Reset returns to the initial snapshot

- **WHEN** a simulation has run and `reset()` is called
- **THEN** `sim.snapshot() == sim.initial`, the tick is zero, the bank is
  the rest pose, no command is active and the recording is empty

#### Scenario: A cancelled command is not in the snapshot

- **WHEN** a move is stepped two ticks, cancelled, and a snapshot is then
  taken and restored after further ticks
- **THEN** the snapshot carries no command, the restore leaves
  `sim.commands` empty, and no further tick moves that input

#### Scenario: A snapshot taken before a cancel re-issues the command

- **WHEN** a snapshot is taken part way through a move, the move is
  cancelled, and the snapshot is restored
- **THEN** the cancelled handle still reports `cancelled` with what it
  had admitted, `sim.commands` holds a fresh active command for that
  input continuing from the recorded progress, and stepping on moves the
  input again

### Requirement: Recording is explicit and bounded under a running root

Under a running root the simulation SHALL keep no per-tick record unless
asked: `Sim(..., record=None)` keeps nothing and `sim.trajectory` reads
empty; `record=N`, a positive integer, keeps a ring of the most recent
`N` `(tick, bank)` entries readable oldest first; any other value SHALL
be refused naming the option. Restore and reset SHALL clear the ring.
Unbounded recording SHALL NOT be offered under a running root.

`record=N` SHALL additionally keep a SECOND ring, of the most recent
`N` CROSSINGS located inside a tick, readable through `sim.crossings`
oldest first, each entry naming the tick, the relation as written, the
driven coordinate, the primitive that jumped, the surface value in the
level quantity's own units, and the fraction of the tick at which it
was crossed. Entries SHALL be appended in order of that fraction within
a tick, in the graph's postorder where two coincide, in program
order across relations, and segment by segment where a stop split the
tick — the recorded fraction being the fraction of the TICK in every
case, whichever segment located it. `record=None` SHALL keep no
crossings and build none.

`record=N` SHALL additionally keep a THIRD ring, of the most recent `N`
STOPS, readable through `sim.stops` oldest first, each entry naming the
tick, the coordinate that stopped, which bound it reached and that
bound's evaluated value, the fraction of the tick at which it was
reached, and the inputs the stop blocked. `record=None` SHALL keep no
stops and build none. A stop SHALL be appended only when the tick
commits. Restore and reset SHALL clear all three rings.

#### Scenario: Nothing is recorded by default

- **WHEN** a running simulation steps ten thousand ticks with no `record`
  option
- **THEN** `sim.trajectory`, `sim.crossings` and `sim.stops` are all
  empty and the run's memory does not grow with the tick count

#### Scenario: The stop ring names the coordinate, the bound and the inputs

- **WHEN** `Sim(node, dt, record=8)` drives a ranged coordinate into its
  bound
- **THEN** `sim.stops` holds one entry for that tick, naming the
  coordinate, the bound it reached, the bound's value, a fraction in
  `[0, 1]` and the inputs blocked, and a tick in which a stop is refused
  for another reason adds none

#### Scenario: The crossing ring names the relation and stays bounded

- **WHEN** `Sim(node, dt, record=4)` runs a periodic law through six
  window boundaries
- **THEN** `sim.crossings` holds exactly four entries, the last four,
  each naming the relation as written, the driven coordinate, `'floor'`,
  the integer surface it crossed and a fraction in `[0, 1]`

#### Scenario: A ring keeps the most recent ticks

- **WHEN** `Sim(node, dt, record=64)` steps one hundred ticks
- **THEN** `sim.trajectory` holds exactly sixty-four entries, for ticks
  37 through 100, oldest first

#### Scenario: An invalid recording option is refused

- **WHEN** `record=0`, `record=-1`, `record=True` or `record='all'` is
  given
- **THEN** construction is refused naming `record`

### Requirement: A declared range is a physical stop located inside the tick

Under a running root a banked joint coordinate's declared `range` SHALL
be a PHYSICAL STOP rather than a refusal: when the committed value of
the coordinate at the end of the stretch of tick being integrated would
lie outside one of its bounds AND lie further outside than the value it
held at the START of that stretch, the system SHALL
LOCATE the fraction `t*` of the tick at which the coordinate reaches
that bound and SHALL truncate that tick's motion there for the
coordinate and its group. A coordinate that does not move over a
stretch SHALL NOT stop in it. The tick SHALL COMMIT and the tick count
SHALL advance. Both bounds SHALL remain INCLUSIVE, so a tick landing
exactly on a bound SHALL NOT be a stop. A bound stated as `None` SHALL
be unbounded on that side and SHALL never stop anything.

A bound that reads the joint's own coordinate alone SHALL be evaluated
ONCE PER TICK, at the tick's START, from the committed bank, so that
every segment of one tick is measured against the same number.

A bound that READS OTHER COORDINATES (a `Bound` with reads) SHALL be a
CONSTRAINT between the coordinate and what it reads, evaluated ALONG
the path of each stretch: the joint's own coordinate in the expression
SHALL take the value it holds in the tick's committed bank, and every
coordinate the bound reads SHALL take the value it has along the
stretch's path — an input its admission scaled by the fraction, a
coordinate the increment its determiner gives over the path truncated
there, computed over the SUB-PROGRAM that determines the bounded
coordinate and what the bound reads, by the same arithmetic the segment
is later committed by. The CONSTRAINT LEVEL of such a bound is the
coordinate's value minus the evaluated upper bound, or the evaluated
lower bound minus the coordinate's value; outside is a positive level.
Such a constraint SHALL be examined on a stretch only when the bounded
coordinate or a coordinate it reads has a nonzero increment over that
stretch; a stretch in which nothing the bound depends on moves SHALL
raise nothing and evaluate nothing, so a coordinate standing outside is
free until something carries it further. On a stretch in which NO READ
moves, the bound SHALL be the number its expression gives at the tick's
committed own value and the reads' standing values, evaluated once, and
the coordinate SHALL be stopped or freed exactly as a bound over its own
value alone is — the same detection, localization and commit at the
bound. When a read moves, the level SHALL be sampled at the same fixed number of sub-intervals a jump
search uses — each sample one pass over the bound's sub-program with
every admission scaled by that fraction — and the coordinate SHALL stop
in the stretch at the FIRST sample at which the level is positive AND
greater than the level at the stretch's start: carried further outside
than it stood, by whatever moved, whether the coordinate itself, what
the bound reads, or both — so a constraint violated inside a stretch and
satisfied again at its end is stopped where the violation begins, not
committed. A violation that begins and ends inside one sub-interval is
outside that guarantee, and the answer to it is a smaller `dt`.

The coordinate's value along the tick SHALL be `v(0)` plus the
increment its DETERMINER gives over the tick's path truncated at `t` —
the same path, in the same joint source space, that a law is integrated
over, so that a law which jumps contributes its subtracted-jump
increment here too. `t*` SHALL be the SMALLEST fraction at which that
value reaches the bound, and SHALL be `0` when the coordinate already
stands at or beyond it. Where the determiner is AFFINE in its sources
along the path `t*` SHALL be SOLVED exactly, over the pieces of its own
jump partition where it has one. Where the determiner is PIECEWISE
AFFINE — the requirement "A kink is a cut, and a piecewise-affine
quantity is solved" — `t*` SHALL be SOLVED exactly over those pieces
SUB-DIVIDED at the determiner's own kink breakpoints; those breakpoints
SHALL be taken even where the determiner carries no jump plan at all, a
quantity that is linear between its kinks being not linear across them.
Otherwise the value SHALL be sampled
at the same fixed number of sub-intervals a jump search uses and `t*`
bracketed and bisected to the same tolerance, with the same documented
limit. No further tolerance SHALL be introduced, and a coordinate stopped by a
bound reading its own coordinate alone SHALL be committed at its bound
EXACTLY.

For a bound that reads other coordinates `t*` SHALL be located from the
samples above: `0` when the level is already positive at the stretch's
start and the first sample is higher; otherwise the crossing bracketed
between the last sample at which the bound was satisfied and the first
at which it was not, bisected to the same tolerance with the same
documented limit, `t*` being the INSIDE end of the final bracket — the
last fraction at which the bound is satisfied.
The coordinate SHALL NOT be moved onto the bound: the segment committed
at `t*` by the same arithmetic satisfies it, and the system SHALL assert
that the level at the committed state is at most zero, refusing the
whole tick as a broken invariant otherwise.

For a program with explicit time drives, the source/group procedure below
SHALL additionally consider one independent time-drive admission per resolved
time-source relation, under "Declared time drives retain motion across
operating history". These admissions participate in the same outward-motion
tests and segmented integration as inputs but are NOT commandable inputs;
a stopped time admission holds for the remainder of that tick and is retried
from global elapsed time on the next tick. Time itself is never stopped.
All the following command-retirement rules apply only to actual commands.

The GROUP a stop stops SHALL be every INPUT that reaches the stopped
coordinate through the compiled program AND whose own movement over the
stretch changes it — tested with that input's admission alone and every
other input's set to zero — together with everything those inputs alone
determine. For a bound that reads other coordinates the candidates
SHALL be the inputs reaching the bounded coordinate OR any coordinate
the bound reads, and a candidate SHALL be in the group when its
admission alone, over the bound's sub-program, carries the constraint
level OUTWARD AT THE LOCATED CONTACT — raises it between the inside and
outside sides of that contact's search bracket. A later return to the same
or a lower level SHALL NOT cancel this pushing motion. Each candidate's
path SHALL be evaluated from the same stretch origin at those fractions,
with other admissions set to zero and the bound's own-coordinate argument
still frozen at the tick's committed value. This rule applies equally to
independent time-drive admissions. It SHALL NOT introduce a new tolerance,
a request-length cap, or additional synthetic input requests. Thus an input
moving a read coordinate so as
to make a standing position invalid is stopped where the constraint
becomes active and the standing coordinate does not move, while an
input moving a read coordinate so as to relieve the constraint runs
its full tick. An input that does not reach it, or reaches it only through
a law that contributes nothing to it over the stretch (a disengaged
coupling), SHALL run its full tick; a coordinate determined by both a stopped input and a free
one SHALL move by what the free one contributes after `t*`. The tick
SHALL therefore be integrated as SEGMENTS — `[0, t*]` with every
input's admission scaled by `t*`, then `[t*, 1]` with the stopped
inputs admitting nothing and the others scaled by `1 − t*` — each
segment by the ordinary tick procedure, its own jump partition
included.

The remaining segment SHALL then be examined for a further stop and the
process repeated, always taking the EARLIEST `t*` first. Two stops
whose fractions are within the crossing tolerance of each other SHALL
be ONE event, stopping the union of their groups at one boundary,
whether they are on one group or on two. A tick SHALL admit at most as
many stop events as it has inputs PLUS time-drive admissions admitting
travel, because each event stops at least one moving admission for the rest
of that tick.

A tick SHALL remain ATOMIC across its segments: the bank, the commands'
admitted travel and the records SHALL be staged and applied only when
every segment has succeeded, and a conflict or an unintegrable law in
any segment SHALL commit nothing and retire the commands that moved as
`refused`, exactly as an unsegmented tick does.

Untimed and looping documents SHALL be unchanged: there a declared
range REFUSES a binding outside it and never clamps or stops — a
bound reading other coordinates at the close of the enumeration, under
the joints requirement "A declared range refuses a binding outside it".

#### Scenario: A rack stops at its bound while an independent motor continues

- **WHEN** a running root drives `rack.travel`, declaring
  `range=(None, 50)` and standing at `45`, from `steer` at ratio `1.0`,
  drives an unrelated `wheel.turn` from `motor` at ratio `3.0` under
  `rate('motor', 90)`, and `move('steer', by=10, duration=0.1)` is
  requested at `dt = 0.1`
- **THEN** the tick commits with `rack.travel` at exactly `50`, the
  steering handle reports `blocked` with `5.0` admitted of `10`
  requested, the wheel gains its full `27` degrees for that tick, and
  the rack does not move on any later tick

#### Scenario: A ratchet blocks reverse at the last seated tooth

- **WHEN** an input arbor declares
  `range=(lambda turn: 36 * floor(turn / 36), None)`, stands at `40`,
  and `move('arbor', by=-10, duration=0.1)` is requested at `dt = 0.1`
- **THEN** the tick commits with the arbor at exactly `36`, the handle
  reports `blocked` with `-4` admitted, and a further
  `move('arbor', by=-10, duration=0.1)` from `36` reports `blocked` with
  `0` admitted while a `move('arbor', by=4, duration=0.1)` completes

#### Scenario: A stop admits the same travel at any cadence

- **WHEN** the same reverse move of `-10` from `40` against the same
  ratchet is taken in one tick, in four and in forty
- **THEN** all three leave the arbor at exactly `36` and all three
  handles report exactly `-4` admitted

#### Scenario: A multi-source coordinate keeps moving on its free input

- **WHEN** `a_in` drives `c.turn` at ratio `1.0` with
  `range=(None, 10)` from `8`, `(a_in & b_in).drives(d.turn, law=2a+3b)`
  is stated, and one tick moves `a_in` by `4` and `b_in` by `6`
- **THEN** `c.turn` stops at `10` with `a_in` admitting `2`, `b_in`
  admits its full `6`, and `d.turn` gains exactly `22` rather than `26`

#### Scenario: Two stops in one tick are taken earliest first

- **WHEN** one tick would take a lever past its bound at a quarter of
  the tick and a rack past its own at half of it, on two groups that
  share no input
- **THEN** both commit at their bounds, both handles report `blocked`
  with the travel each made, and `sim.stops` holds two entries with the
  two fractions in that order

#### Scenario: A stop and a jump crossing in one tick

- **WHEN** a crank at `130` drives `first.turn` at ratio `1.0` with
  `range=(None, 145)` and drives `wrapped.turn` by
  `2 * wrap(angle, 90)`, whose fold falls at `135`, and one tick would
  move the crank by `20`
- **THEN** `first.turn` stops at `145`, `wrapped.turn` gains exactly
  `30`, the `wrap` crossing is recorded at the fraction `0.25` OF THE
  TICK — not at the `1/3` it sits at within the segment — the stop at
  `0.75`, and the handle reports `blocked` with `15` admitted

#### Scenario: A block replays identically from a snapshot

- **WHEN** a snapshot taken before a blocking tick is restored and the
  same command is issued again
- **THEN** the run blocks at the same coordinate value, admits the same
  travel and records the same stop; and a snapshot taken AFTER the block
  restores a run with no command on that input

#### Scenario: A tick that fails after a stop commits nothing

- **WHEN** the segment after a stop meets a conflict
- **THEN** the bank, the tick count and the tree stand as before the
  whole tick, no stop and no crossing is recorded, and the commands that
  moved retire `refused`

#### Scenario: A disengaged coupling does not stop its input

- **WHEN** a wheel with a declared upper bound is driven by
  `(push & crank & gate)` through `push + crank * (gate > 0.5)`, `crank`
  also drives an unrelated flywheel, the gate stands at `0`, and one tick
  moves `push` past the wheel's bound while `crank` moves too
- **THEN** the wheel stops at its bound, `push`'s command is retired
  `blocked` with the travel admitted before the stop, `crank`'s command
  runs its full tick and completes, and the flywheel gains the full
  tick's travel; with the gate at `1` the same tick retires both
  commands `blocked`

#### Scenario: A plug does not turn while a pin crosses the shear line

- **WHEN** a running root drives `key.travel` from `feed` at ratio `1.0`,
  drives `p1.lift` and `p2.lift` from `key.travel` through the laws
  `5 - 5 * clamp01((travel - 10) / 5)` and
  `5 - 5 * clamp01((travel - 13) / 5)`, so the first lift enters the
  window at a travel of `14.95`, the second at `17.95`, and both stand
  at `0` from `18` on, drives
  `plug.turn` from `turn`, `plug.turn` declaring
  `range=(0, Bound(lambda turn, a, b: 90 * (abs(a) <= 0.05) * (abs(b) <= 0.05), reads=(p1.lift, p2.lift)))`,
  the key stands at `10`, and `move('turn', by=30, duration=0.1)` is
  requested at `dt = 0.1`
- **THEN** the tick commits with `plug.turn` and `turn` at exactly `0`,
  the handle reports `blocked` with `0` admitted, `sim.commands` is
  empty, and `sim.stops` holds one entry naming `plug.turn`, `high`,
  the evaluated bound `0`, the fraction `0` and the inputs `('turn',)`

#### Scenario: A plug turns once every pin clears

- **WHEN** the same root has moved `feed` to `20` over four ticks and
  `move('turn', by=30, duration=0.1)` is then requested
- **THEN** the tick commits with `plug.turn` at `30`, the handle reports
  `completed` with `30` admitted, and `sim.stops` is empty

#### Scenario: Insertion and turning in one tick

- **WHEN** the key stands at `10` and, in the same tick,
  `move('feed', by=10, duration=0.1)` and `move('turn', by=30, duration=0.1)`
  are both requested, the pins clearing at `0.8` of the tick
- **THEN** the tick commits with `key.travel` at `20` and `plug.turn` at
  `0`, the feed handle reports `completed` with `10` admitted, the turn
  handle reports `blocked` with `0` admitted, and a
  `move('turn', by=30, duration=0.1)` requested on the next tick completes

#### Scenario: Withdrawing the key from a turned plug stops the key, not the plug

- **WHEN** the key stands at `20` with the plug turned to `30` and no
  bound is declared on `key.travel`, and `move('feed', by=-5, duration=0.1)`
  is requested, the second pin's lift leaving the window at a travel of
  `17.95`
- **THEN** the tick commits with `plug.turn` at exactly `30` and
  `key.travel` within the crossing tolerance of the tick's travel below
  `17.95` and inside the window, the handle reports `blocked` with the
  travel it made, and `sim.stops` holds one entry naming `plug.turn`,
  `high`, the evaluated bound `90`, the fraction at which the pin left
  the window and the inputs `('feed',)`

#### Scenario: A declared capture stops the key at once

- **WHEN** `key.travel` additionally declares
  `range=(Bound(lambda travel, turn: 20 * (turn > 0), reads=(plug.turn,)), 20)`,
  the plug stands turned at `30` and `move('feed', by=-5, duration=0.1)`
  is requested
- **THEN** the tick commits with `key.travel` at exactly `20`, the
  handle reports `blocked` with `0` admitted, and the stop names
  `key.travel`, `low`, `20`, the fraction `0` and `('feed',)`

#### Scenario: Returning the plug and withdrawing the key in one tick

- **WHEN** the plug stands at `30`, the key at `20` with the capture
  declared, and in one tick `move('turn', by=-30, duration=0.1)` and
  `move('feed', by=-5, duration=0.1)` are both requested
- **THEN** the plug returns to `0` and its handle completes, the key
  stands at `20` and its handle reports `blocked` with `0` admitted, and
  a withdrawal requested on the next tick completes

#### Scenario: A pawl lifting during the tick releases the ratchet

- **WHEN** an arbor's wheel declares
  `range=(Bound(lambda turn, lift: 36 * floor(turn / 36) - 1000 * (lift >= 1), reads=(pawl.lift,)), None)`,
  stands at `40`, and one tick moves the arbor by `-10` while a `lift`
  input raises `pawl.lift` from `0` to `1` at `0.3` of the tick
- **THEN** the arbor completes at `30` with `-10` admitted and no stop
  is recorded; and with the pawl reaching `1` at `0.5` of the tick
  instead, the wheel stops at exactly `36` at `0.4` of the tick and the
  arbor's handle reports `blocked` with `-4` admitted

#### Scenario: A bound reading other coordinates admits the same travel at any cadence

- **WHEN** the withdrawal from the turned plug is taken in one tick, in
  four and in forty
- **THEN** all three stop the key at the same travel within the crossing
  tolerance and all three handles report the same admitted travel

#### Scenario: A constraint stop replays identically from a snapshot

- **WHEN** a snapshot taken before a tick that stops the key from a
  turned plug is restored and the same command is issued again
- **THEN** the run blocks at the same travel, admits the same travel and
  records the same stop

#### Scenario: A machine with no bound reading other coordinates pays nothing

- **WHEN** the `Train` fixture is stepped after this change
- **THEN** one tick costs what ADR-108 recorded within measurement noise
  and the deterministic count of graph evaluations per tick is unchanged

#### Scenario: A periodic lockout stops a long request at its first contact

- **WHEN** a crank at 120° drives a bell and a co-rotating drum, the bell's
  lower bound reads the drum as `-360*floor((-drum-10.8)/360)-125.22`, and
  an immediate request asks for crank 840°, crossing a sampled forbidden
  interval before ending in a later revolution's open window
- **THEN** the request reports `blocked` at crank 125.22° within the
  existing search tolerance, admitting approximately 5.22°, instead of
  raising an invariant error or passing through the first obstruction

#### Scenario: Short and long requests meet the same periodic contact

- **WHEN** the same prepared lockout receives a short immediate request to
  150°, a long immediate request to 840°, or a timed request to 840° whose
  ticks resolve that contact under the existing sampling guarantee
- **THEN** all requests stop at the same first contact within the existing
  agreement tolerance and the retained follower does not move

#### Scenario: Retrying a periodic contact does not resume hidden travel

- **WHEN** the blocked crank is requested forward again, then relieved a
  small distance backward and requested forward again
- **THEN** it blocks at the same contact, backward relief is admitted, and
  no portion of the earlier request is resumed or remembered

#### Scenario: A free periodic mechanism keeps unrestricted legal travel

- **WHEN** the actual retained follower tracks its legal indexed positions
  so the periodic bound remains satisfied over a three-turn request
- **THEN** the request completes all three turns with the expected retained
  displacement; the fix introduces no one-turn cap or artificial stop

#### Scenario: Periodic contact preserves unrelated motion and replay

- **WHEN** a periodic contact stops one admission while an independent
  admission moves, and the same operation is replayed from a snapshot
- **THEN** the independent admission completes, the pushing admission
  reports only its admitted travel, and replay reproduces the committed
  bank, stop identities, statuses and travel under the existing tolerances

### Requirement: Profile contact is a numeric term in an existing running Bound

Under a running root, a `Bound` expression SHALL accept the pointwise `profile_overlap` result as numeric `0.0` or `1.0` in ordinary arithmetic that returns an absolute lower or upper coordinate limit. It SHALL resolve the call's motion operands from the `Bound`'s declared reads, and SHALL preserve the existing frozen-own-value rule, evaluated numeric span shape, 64-subinterval search, bisection, first-error behavior, stop attribution, atomic refusal and snapshot/replay contract. A **symbolic** profile contact operation outside a supported running `Bound` SHALL be refused by name rather than emitted as an unevaluable pose, law or clocked expression. A plain numeric `profile_overlap` call SHALL remain usable for standalone probes and numeric bind-time range evaluation; the framework SHALL NOT claim to identify the origin of an ordinary numeric result.

#### Scenario: Contact selects an axial plane without becoming a bound
- **WHEN** Curta's running reverser `Bound` uses the contact flag to select an absolute held-side axial limit from its existing lower or upper plane arithmetic
- **THEN** the compiled constraint still has the ordinary numeric limit and blocks the same held coordinate through the existing search and attribution path

#### Scenario: A moving angular contact is sampled under the existing limit
- **WHEN** a moving read changes the profile flag during a tick
- **THEN** the surrounding Bound is evaluated at the same samples and bisected under the same limit and tolerance as any other dynamic Bound; no continuous collision guarantee is added

#### Scenario: A quiet bound remains quiet
- **WHEN** neither the bounded coordinate nor any declared read moves during a stretch
- **THEN** the existing quiet-stretch rule evaluates neither the bound nor the contact predicate

#### Scenario: Unsupported expression context is refused
- **WHEN** a symbolic profile operation is returned by a clocked bound, a running law, or a pose operation rather than a running Bound
- **THEN** that context refuses it by name rather than publishing or silently changing its solver

#### Scenario: Standalone numeric check is still available
- **WHEN** an author evaluates `profile_overlap` with plain numeric placements or a numeric bind-time range consumes its result
- **THEN** it returns the same numeric 0/1 predicate without a symbolic-context refusal

### Requirement: A range bound may read other coordinates

Under a running root a `Bound(expression, reads=(...))` stated as either
bound of a banked joint coordinate's range SHALL be compiled once, at
simulation construction, exactly as a one-argument bound is: its reads
resolved against the joint's declarer to the qualified ids the bank keys
by, the expression applied to a symbolic token for the joint's own
coordinate and one per read in declared order, and the graph walked for
raw text and for calls outside the symbolic vocabulary. The sole added
symbolic call allowed by this change is `profile_overlap` within a running
`Bound`; it is not added to the general law, pose, clocked or SCAD vocabulary.
A read SHALL be
a coordinate the run banks — a joint coordinate or a declared input; a
read resolving to a plain port or a derived coordinate SHALL be refused
at construction by joint and node identity, saying that a bound reads the
state and naming the joint the port follows. Jumps SHALL be admitted with
no plan, because a bound is evaluated and never integrated.

The compiled program SHALL carry, for each such bound, the ids it reads,
the SUB-PROGRAM — the compiled edges that determine the bounded
coordinate and every read, in program order — and the candidate inputs
reaching any of them. `Program.spans` SHALL keep its shape, each such
bound a graph in it like any other, and the program's described listing
and therefore its identity SHALL change with the reads, so a snapshot
cannot restore into a machine whose constraints moved.

A stop located by such a bound SHALL be recorded like any other: the
bounded coordinate, the side, the bound evaluated at the committed state,
the fraction of the tick and the inputs blocked, sorted.

#### Scenario: A read is resolved to the id the bank keys by

- **WHEN** a running root's `Plug` body declares `p1 = Pin()` and
  `turn = Revolute(..., range=(0, Bound(..., reads=(p1.lift,))))` and the
  plug is held as `plug`
- **THEN** the compiled bound's graph reads `plug.p1.lift`, the same id
  `sim.state` holds, and the program's described listing names it in the
  span line

#### Scenario: A read of a plain port is refused at construction

- **WHEN** a `Bound`'s `reads` names a port an author's `simulate()`
  binds rather than a joint coordinate
- **THEN** construction is refused by joint and node identity, naming the
  port and saying a bound reads the state

#### Scenario: A read the expression never uses is refused at construction

- **WHEN** a `Bound` declares `reads=(p1.lift, p2.lift)` and its
  expression reads only the first, or returns a plain number
- **THEN** construction is refused by joint and node identity, naming
  the read the expression never uses, because a bound reads every
  coordinate it names

#### Scenario: A bound over other coordinates changes the identity

- **WHEN** two roots differ only in the window a bound reads its pins
  against
- **THEN** their program identities differ and a snapshot of one is
  refused by the other

#### Scenario: A read of a driver is an input of the bank

- **WHEN** a `Bound` on a class-declared joint reads a driver of the same
  class
- **THEN** the compiled bound's graph reads that driver's qualified id
  and evaluates it along the path as an input's admission scaled by the
  fraction

#### Scenario: Only a running Bound gains the contact call

- **WHEN** the same symbolic `profile_overlap` expression is offered to
  a running Bound and to an ordinary running law or pose expression
- **THEN** only the Bound compiles it; the other symbolic contexts refuse
  it by name, without widening the general math vocabulary

### Requirement: A control says which part a person presses or turns

The system SHALL let an assembly declare a `controls` mapping beside
`instructions`, of display name to CONTROL, stating how a person issues
a movement request by touching a part of the machine:

- `Button(part, instruction, *, coordinate=None)` — a press on `part`
  submits the named instruction;
- `Turn(part, input, *, coordinate=None)` — a drag about the selected
  rotational coordinate is a sequence of relative moves on `input`; and
- `Slide(part, input, *, coordinate=None)` — a drag along the selected
  translational coordinate is a sequence of relative moves on `input`.

A control SHALL move nothing itself. It names a request the run already
accepts, and every rule about ownership, admission, stops and outcomes
SHALL be the one `trigger`, `move` and `rate` already state. A control
SHALL carry no state and SHALL NOT repeat an instruction's definition.

`part` SHALL be a NODE, named in the class body the way a relation's
path ends are named — a declared child, or a path of declared children
and child declarations through one (`units.input.dial`). A `Turn` or `Slide` control's
`input` SHALL be a `Driver` declared on the class that declares the
control; a driver of a child is named by declaring the control on the
child, exactly as an instruction over a child's driver is.

Controls declared on any node in the tree SHALL be discoverable by
QUALIFIED name — the declaring node's instance path joined with the
declared name, a root-declared control keeping its bare name — and a
`Button`'s instruction reference SHALL qualify through that same path,
so it equals a key of the tree's instruction table by construction.

Without explicit selection, a control's COORDINATE SHALL be the one owned
by the nearest ancestor-or-self of the part that declares a joint whose
coordinate the run banks. The joint's declaring node SHALL be the node that
coordinate poses.

An explicit `coordinate` SHALL name one existing single-coordinate joint,
using its declaration or a declaration path from the class declaring the
control. The joint SHALL pose the touched part or one of its ancestors in
that same tree, and its coordinate SHALL be run-banked. Selection SHALL
permit independently controlled sliding and turning joints on the same
body without changing the body, its placement, or the run program.
`Button` SHALL accept either a translational or rotational selected joint.
Omitting selection SHALL preserve the existing ambiguity refusal.

Each of the following SHALL be REFUSED, naming the facts a reader can
find in the model:

- a `controls` value that is not a mapping of names to controls, or an
  entry that is not a control — refused AT CLASS DEFINITION naming the
  entry and the reservation of the name;
- a `part` that is not a node reference — a coordinate, a driver, a
  repeated child, a list-held child or a plain value — refused where it
  is written, naming what was written;
- a `part` whose first segment is not a child the DECLARING class
  declares — refused at class definition, naming the class and the
  control;
- a `Turn` or `Slide` whose `input` is not a `Driver` declared on the declaring
  class — refused at class definition, listing the drivers that class
  declares;
- a `Button` whose instruction is not a declared instruction — refused
  when the tree is enumerated, listing the known qualified instruction
  names;
- a part no run-owned coordinate poses — refused naming the part and
  saying nothing the run owns moves it;
- a control without explicit selection whose nearest posing node declares
  MORE THAN ONE joint, or any selected joint owning MORE THAN ONE coordinate
  — refused naming them and saying a control names one coordinate;
- an explicit coordinate that is not a joint declaration/reference, is not
  run-banked, or does not pose this part or an ancestor in this tree —
  refused naming the control, part and selected reference;
- a `Turn` whose coordinate's domain is not `rotational`, or a `Slide`
  whose coordinate's domain is not `translational` — refused naming the
  actual and required domains;
- a `Turn` or `Slide` whose `input` is not among the inputs that reach its
  coordinate through the compiled program — refused naming the
  coordinate and the inputs that DO reach it;
- a control under a root that does not declare `Time.running()` —
  refused naming the declaring class, the control and `Time.running()`.

#### Scenario: A control is declared beside the instructions

- **WHEN** a running root declares
  `instructions = {'Add one': Instruction(by={'units_entry': 1.0}, duration=1.0)}`
  and
  `controls = {'units dial': Button(units.dial, 'Add one'),
  'turn units': Turn(units.dial, units_entry)}`,
  where `units` declares `turn = Revolute(axis=(1, 0, 0))` and holds the
  leaf `dial`
- **THEN** the simulation is constructed, both controls are discovered
  under their bare names, each names the part `units.dial`, the
  coordinate `units.turn` and the joint node `units`, and nothing about
  the run's bank, edges or identity differs from the same root declaring
  no controls

#### Scenario: A control on a child qualifies through its path

- **WHEN** a running root holds `column`, an assembly that declares both
  `'Add one'` and `controls = {'dial': Button(arbor.dial, 'Add one')}`
- **THEN** the control is discovered as `column.dial`, its instruction
  reference is `column.Add one` — a key of the tree's instruction table
  — and its part is `column.arbor.dial`

#### Scenario: A misspelt part is refused where it is written

- **WHEN** a class body writes `Button(units.dail, 'Add one')` and
  `units`'s class declares no `dail`
- **THEN** class definition raises naming `units.dail`, saying that
  class declares no port, joint or child of that name, and listing what
  it does declare

#### Scenario: A part of another class is refused at class definition

- **WHEN** a class declares `controls` whose part's first segment is a
  child declaration some OTHER class holds
- **THEN** class definition raises naming the declaring class, the
  control's name, and that a control's part is walked from the assembly
  that declares it

#### Scenario: A coordinate is not a part

- **WHEN** a class body writes `Turn(units.turn, units_entry)`, naming
  the joint rather than the body it moves
- **THEN** declaration raises saying a control names a PART — a node
  whose geometry a hand touches — not a coordinate

#### Scenario: An input of another class is refused

- **WHEN** a class declares `Turn(units.dial, other_entry)` where
  `other_entry` is a `Driver` that class does not declare
- **THEN** class definition raises naming the driver and listing the
  drivers the declaring class does declare

#### Scenario: A button names an instruction that is not declared

- **WHEN** a running root declares `Button(units.dial, 'Add two')` and
  no instruction of that qualified name exists
- **THEN** construction is refused naming `Add two` and listing the
  known qualified instruction names

#### Scenario: A part nothing run-owned moves is refused

- **WHEN** a running root declares `Button(frame, 'Add one')` where
  `frame` is a leaf the root holds and no ancestor-or-self of it
  declares a joint
- **THEN** construction is refused naming `frame` and saying nothing the
  run owns moves that part

#### Scenario: A turn on a coordinate that does not turn is refused

- **WHEN** a running root declares `Turn(carriage.plate, feed)` and
  `carriage` declares `travel = Prismatic(...)`
- **THEN** construction is refused naming `carriage.travel`, its
  `translational` domain, and that a turn is about a rotational
  coordinate

#### Scenario: A turn whose input does not reach the part is refused

- **WHEN** a running root's `tens.turn` is reached by `tens_entry` and
  `units_entry` while `units.turn` is reached by `units_entry` alone,
  and the root declares `Turn(units.dial, tens_entry)`
- **THEN** construction is refused naming `units.turn` and listing
  `units_entry` as the input that reaches it

#### Scenario: A dial two inputs reach is bound to the one the author names

- **WHEN** the same root declares `Turn(tens.dial, tens_entry)`
- **THEN** it is admitted, its coordinate is `tens.turn`, and its input
  is `tens_entry` — the other input that reaches that coordinate having
  no bearing on the gesture

#### Scenario: A joint owning several coordinates is refused

- **WHEN** a running root declares a control on a part whose nearest
  posing node declares `pose = Free(...)`
- **THEN** construction is refused naming the joint, the coordinates it
  owns, and that a control names one coordinate

#### Scenario: A control without a running root is refused

- **WHEN** a root declaring no time base, or `Time(loop=2.0)`, declares
  a `controls` table and a simulation is constructed over it or its
  document is published
- **THEN** each is refused naming the declaring class, the control and
  `Time.running()`

#### Scenario: A controls attribute that is not a control table is refused

- **WHEN** a node class declares `controls = {'speed': 3}`
- **THEN** class definition raises naming the entry and saying
  `controls` names the machine's controls on a node class

#### Scenario: A selector is handled along its sliding joint

- **WHEN** a running root declares `Slide(selector.knob, setting)` and
  setting reaches the selector's single prismatic joint
- **THEN** construction admits the control with that coordinate and input,
  and the control neither moves the part nor changes the program's identity

#### Scenario: One body can be lifted and turned independently

- **WHEN** a crank declares single-coordinate revolute and prismatic joints
  and its controls explicitly select turn for a Turn and lift for a Slide
- **THEN** both controls are admitted on the same body, each resolving to its
  selected coordinate and the input that reaches it

#### Scenario: Ambiguity is not resolved by guessing

- **WHEN** the same two-joint crank declares a control without selection
- **THEN** construction is refused naming both joints and the ambiguous control

#### Scenario: A press can request movement of a sliding part

- **WHEN** a Button names a selector with one prismatic joint and a declared
  instruction requesting one detent
- **THEN** construction admits it and the instruction is the same request
  the run accepts through its normal instruction interface

#### Scenario: Selection cannot reach sideways

- **WHEN** a control on a crank explicitly selects a carriage joint that
  poses neither the crank nor any ancestor of it
- **THEN** construction refuses the control naming the part and selected joint

#### Scenario: An explicit ancestor coordinate remains reachable

- **WHEN** a touched knob sits beneath a jointed child on a carriage, and
  its Slide explicitly selects the carriage's prismatic joint
- **THEN** construction admits that ancestral coordinate instead of
  silently selecting the nearer child's different joint

#### Scenario: Selecting a joint does not unpack a multi-coordinate joint

- **WHEN** a control explicitly selects a Free joint
- **THEN** construction refuses it naming the joint and its multiple coordinates

#### Scenario: A slide cannot masquerade as a turn

- **WHEN** a Slide selects a rotational joint
- **THEN** construction is refused naming the coordinate's rotational domain
  and the required translational domain

#### Scenario: Sliding cannot bypass a stop or change another control

- **WHEN** a request submitted through a sliding control meets a declared bound
  dependent on a second mechanism
- **THEN** the run admits exactly the movement the same ordinary move request
  admits, reports the same outcome, and does not reposition that second mechanism

### Requirement: A law may read the coordinate it drives

Under a running root a relation whose source group names its own DRIVEN
end SHALL be integrated so that the law reads, on each piece of the tick,
the value that coordinate HELD at the piece's start — its RETAINED value
— and never a value the same piece is computing.

Such a relation SHALL drive exactly ONE coordinate. A relation whose
driven end is a GROUP and whose source group names any member of that
group SHALL be REFUSED at class definition, naming the relation and the
coordinate, and saying that a relation reading its own driven end drives
one coordinate — whether the member reads ITSELF or a SIBLING driven end.

**The read SHALL be a SWITCH.** The system SHALL REFUSE, at construction
and by relation identity — naming the relation as written and the class
that stated it — a law whose SKELETON, the expression with every jump
node replaced by its branch, still names the driven coordinate it reads.
A read that survives the skeleton enters the law continuously, which
makes the relation a differential equation that the difference of two
evaluations does not define. The message SHALL say that a read must pass
through a node that is piecewise constant in it — `floor`, `ceil`,
`sign` or a comparison — and that a remainder alone is not one, because
a fixed quotient leaves `a − q·b`, which still carries the coordinate's
slope.

The system SHALL likewise REFUSE, at construction and by relation
identity, a relation reading a driven end the run does not BANK — a
plain port or a derived coordinate — saying that a retained value is a
history and only a coordinate the run owns keeps one.

**Over one tick such a law SHALL be integrated PIECE BY PIECE.** A jump
node DEPENDS on the driven coordinate when that coordinate is among the
free names of the node's argument subtree. The tick's path SHALL first
be partitioned by the jump nodes that do NOT depend on it, exactly as any
other law's path is, their branches read at that partition's midpoints;
INSIDE each of its pieces the dependent nodes SHALL then be walked:

- At the walk's left end the driven coordinate holds a known value: the
  tick's committed value at the start, and the value the cuts already
  taken placed it at afterwards.
- Every dependent node's branch SHALL be determined in the graph's
  postorder, with the driven coordinate at that retained value and every
  OTHER source at the piece's LEFT END — not at its midpoint, because a
  level quantity naming both the driven coordinate and a source may cross
  inside the piece by the source's motion alone, and the branch read past
  that crossing is not the branch the piece begins under.
- A dependent node whose level sits EXACTLY on a surface at that left end
  SHALL take the branch its operator gives; if the level then LEAVES the
  surface into the other branch's region, that node SHALL be flipped to
  the other branch at the left end and every branch decided again. If the
  flipped branch carries the level back across as well, the tick SHALL be
  REFUSED naming the relation, the coordinate and the primitive, and
  SHALL commit nothing.
- With those branches fixed the substituted law SHALL be continuous on
  the piece and SHALL NOT name the driven coordinate, so that
  coordinate's own value along the piece is one ordinary evaluation.
- Each dependent node's level quantity SHALL be followed along the piece
  — through the driven coordinate's own path and through the sources —
  and the piece SHALL be CUT at the FIRST surface any of them reaches
  strictly inside it: SOLVED exactly where that level is affine along the
  path, and equally where that level and the driven coordinate's own path
  over the piece are each affine or PIECEWISE AFFINE — the requirement
  "A kink is a cut, and a piecewise-affine quantity is solved" — the
  piece being SUB-DIVIDED at the kink breakpoints of BOTH before each
  sub-piece is solved; otherwise sampled at the same fixed number of
  sub-intervals and
  bisected to the same tolerance a jump search already uses. No further
  tolerance SHALL be introduced, and a crossing found within that
  tolerance of the piece's left end SHALL NOT be merged into it.
- The piece's contribution SHALL be the substituted law's change over it,
  and the next piece SHALL be decided the same way.

A tick whose path is cut more times than the stated maximum SHALL be
refused exactly as any other over-crossed tick is.

**After a cut the driven coordinate SHALL be committed AT THE FAR SIDE OF
THE SURFACE, at the nearest representable value.** Where the piece moved
it, the coordinate SHALL be placed at the representable value NEAREST the
surface among those at which the crossing node's level — evaluated with
the driven coordinate at that value and every other source at the
crossing's own fraction — reads the branch on the side the level was
moving TOWARD. That value SHALL be what the next piece starts from, and a
tick in which at least one cut placed the coordinate SHALL COMMIT the
value the walk left it at — the last landing and whatever the pieces
after it contributed — rather than its starting value plus the
increment, exactly as a stopped coordinate is committed at its bound. Where the piece did NOT move the coordinate, it SHALL stand where
it stood. A coordinate held at a gate SHALL therefore read the same
branch on every later tick, whatever its sources do, and SHALL survive a
snapshot and a restore bit for bit.

A model SHALL state a gate whose DISENGAGED state has WIDTH — the
mechanism's own clearance — because a gate whose disengaged state is a
single value of the coordinate reads engaged on one side of it and cannot
hold when the coordinate arrives from that side. The width is the
model's to state and the system SHALL NOT require any particular one: a
band of any positive width holds from both directions.

**A self-read crossing is NOT a stop.** It SHALL stop no input, retire
no command and appear in the crossing record rather than the stop
record. A declared range on the driven coordinate SHALL stop it exactly
as it stops any other, located over this same partition, and SHALL be
committed at its bound even where a cut of the same segment placed it
elsewhere.

**At rest such a relation SHALL bind nothing.** It SHALL be recorded
solved FORWARD, its law unapplied, so the rest render poses the tree from
the author's own rest default and the run refuses by name when there is
none. Binding the whole bank again, rendering, or inspecting the tree
SHALL advance it by nothing: the relation moves its coordinate only
through a tick.

#### Scenario: A wheel clears to its gap and the ring runs on

- **WHEN** a running root states
  `(ring & wheel.turn).drives(wheel.turn, law=missing_tooth)`, whose gate
  is disengaged over a band of half-width `g` about every multiple of
  `360`, the wheel rests at `108`, and `move('ring', by=500, duration=1)`
  is run at `dt = 0.1`
- **THEN** the tick sequence commits with `ring` at `500` and its handle
  `completed`, `wheel.turn` at the band's lower edge — within `g` of
  `360`, at the nearest representable value on the disengaged side — and
  the crossing at which the wheel reached its gap recorded in
  `sim.crossings` and not in `sim.stops`

#### Scenario: Sweeping an already-cleared wheel moves it by nothing

- **WHEN** the same root is swept a second time by another
  `move('ring', by=500, duration=1)`, and a third
- **THEN** `ring` reads `1500`, `wheel.turn` holds the SAME float it
  landed on, bit for bit, after each of them, and every handle reports
  `completed`

#### Scenario: Swept backward, a digit clears to zero the short way

- **WHEN** the wheel rests at `108` and the ring is swept BACKWARD far
  enough to carry it past zero
- **THEN** the wheel ends at the band's UPPER edge — within `g` above
  `0`, at the nearest representable value on the disengaged side — having
  turned three teeth and no more, and it does not move on a further
  backward sweep

#### Scenario: Every digit clears and no digit overruns

- **WHEN** the same root is constructed ten times, its wheel resting at
  each of `0, 36, 72, … 324`, and each is given a sweep long enough to
  reach the gap
- **THEN** each wheel ends within `g` of the next multiple of `360` in
  the sweep's direction — the one it already stood on for the wheel that
  rested at `0`, which does not move at all

#### Scenario: A wheel standing exactly on a band edge is not driven through it

- **WHEN** a wheel is placed exactly at the value its own gate's surface
  sits on — the float a previous sweep landed it at — and the ring is
  swept, first in the direction that carries the level INTO the gate's
  engaged region and then in the direction that carries it away
- **THEN** it holds in the direction that would take it deeper into the
  band, turns in the direction that leaves it, and in neither case is it
  carried through the band by a piece integrated under the wrong branch

#### Scenario: A partial sweep is retained and resumes

- **WHEN** the wheel rests at `108`, `move('ring', by=120, duration=1)`
  completes, the caller then reads `sim.state`, renders the tree, takes a
  snapshot and restores it, and only then requests another
  `move('ring', by=380, duration=1)`
- **THEN** the wheel stands at `228` after the first move and unchanged
  through every inspection, and at the band's edge after the second — no
  starting register having been supplied by the caller

#### Scenario: The same sweep at three cadences agrees

- **WHEN** one running simulation takes the whole sweep in a single
  tick, another in twelve and another in two hundred and forty, and a
  fourth takes it as four partial commands with the ring released
  between them
- **THEN** all four leave the wheel and the ring at the same values
  within the run's agreement window, no tick records a stop, no command
  is retired `blocked`, and the total travel admitted is the same

#### Scenario: A continuous read is refused

- **WHEN** a running root states
  `(ring & wheel.turn).drives(wheel.turn, law=...)` whose law is
  `ring * wheel`, or `ring * (wheel % 360)`
- **THEN** construction is refused naming the relation and the class that
  stated it, and saying the read must pass through a node that is
  piecewise constant in it and that a remainder alone is not one

#### Scenario: A self-read of a coordinate the run does not bank is refused

- **WHEN** a running root states a self-read relation whose driven end is
  a plain port rather than a joint coordinate
- **THEN** construction is refused naming the relation and the port, and
  saying that a retained value is a history and only a coordinate the run
  owns keeps one

#### Scenario: A driven group with a self-read is refused

- **WHEN** a class states
  `(crank & lever.swing & pawl.turn).drives((lever.swing, pawl.turn), law=...)`
- **THEN** class definition is refused naming the relation and the
  coordinate read, and saying that a relation reading its own driven end
  drives one coordinate

#### Scenario: Several wheels clear independently from one ring

- **WHEN** a running root drives four wheels resting at `0`, `108`, `252`
  and `324` from one `ring` input, each by its own self-read relation
  whose rack term opens over that wheel's own station, and the ring is
  swept through the first three stations only
- **THEN** the first wheel does not move, the second and third each end
  at their band's edge, the fourth is untouched, and the ring's handle
  reports `completed` with its whole travel admitted

#### Scenario: A declared range on the ring still blocks

- **WHEN** the ring's own coordinate declares `range=(None, 400)` and a
  sweep of `500` is requested
- **THEN** the ring stops at exactly `400`, its command retires
  `blocked`, `sim.stops` names the ring's coordinate, and the wheels
  cleared only as far as the admitted sweep carried their racks

#### Scenario: Reversal inside the gap moves nothing

- **WHEN** a wheel standing INSIDE its band is swept backwards and then
  forwards again
- **THEN** it does not move in either direction, both handles report
  `completed`, and no stop is recorded

#### Scenario: Reversal while engaged backs the wheel up

- **WHEN** a sweep carries a wheel from `108` part way toward its gap and
  the ring is then swept back the same distance
- **THEN** the wheel returns to `108` within the run's agreement window,
  the two increments having been the same law read in both directions

#### Scenario: A stop and a self-read crossing in one tick

- **WHEN** one tick would carry a wheel through its gap at one fraction
  and take an unrelated ranged coordinate past its bound at another
- **THEN** the ranged coordinate stops at its bound exactly, the wheel
  holds at its gap, the crossing is recorded at its fraction OF THE TICK
  rather than of the segment, and `sim.stops` names only the ranged
  coordinate

#### Scenario: A self-read law's identity names what it reads

- **WHEN** two running roots differ only in whether their law reads the
  driven coordinate
- **THEN** the program's described listing differs, their identities
  differ, and a snapshot of one is refused by the other

#### Scenario: A tick that fails after a self-read cut commits nothing

- **WHEN** a segment after a self-read cut meets a conflict
- **THEN** the bank, the tick count and the tree stand as before the
  whole tick, no crossing is recorded, the coordinate is NOT left at the
  value the cut placed it at, and the commands that moved retire
  `refused`

### Requirement: A selection decides which sources a law reads

A mechanism's dependencies may be SELECTED by where one of its own parts
stands, so that the union of what it reads over every selection is
cyclic although each selection's own dependencies are not — the same
fixed carry lever of a Curta is tripped by the dial the carriage has
brought under it and advances the dial beyond that one.

Under a running root the system SHALL admit such a union and SHALL order
it once per PIECE of a tick rather than once per program.

**A BLOCK is a nontrivial strongly connected component** of the
dependency graph the requirement "A relation's law is compiled to an
expression over coordinate ids" defines. Every coordinate a block's edges
read SHALL therefore be one the block itself determines, or one
determined UPSTREAM of it, or an input, or a coordinate that holds.

**A SELECTOR is a jump node of a block member's law whose LEVEL QUANTITY
reads no coordinate the block determines** — a placeholder standing in
that level being resolved into the jump node it replaced, transitively.
A jump node whose level reads a coordinate the block determines,
including the member's own driven end, SHALL NOT be a selector.

**FOLDING a law means setting jump placeholders to ZERO in the member's
SKELETON and simplifying**: a product or a quotient with a zero numerator
being zero, a sum or a difference with a zero operand being the other
operand (negated where it is subtracted). What the member READS under a
fold SHALL be the folded skeleton's free names, with every surviving
placeholder followed into its own folded level quantity, transitively.

**A placeholder SHALL be foldable to zero only where its primitive holds
the ZERO branch over an INTERVAL of its level quantity** — `floor` over
`[0, 1)`, `ceil` over `(-1, 0]`, a remainder's quotient over `(-1, 1)`,
a comparison over the whole of its false side. `sign` reads zero at a
single POINT of its level and SHALL NOT be foldable: a source it gates
is active on every piece of positive width, so treating it as removable
would admit at construction a machine every tick refuses.

**A member's UNCONDITIONAL dependencies SHALL be the coordinates the
block determines that it still reads with EVERY foldable selector of that
member at zero AT ONCE**, and a source it reads with nothing folded but
not under that one fold SHALL be SWITCHED. One fold SHALL decide both:
folding a further placeholder can only remove names and never add one, so
the reads under that single fold are the fewest any selection can leave.

Folding at compile time and reading a branch at run time are DIFFERENT
operations and SHALL NOT be conflated: over a piece the system substitutes
the branch values actually read, whatever they are, and keeps whatever
survives.

The system SHALL REFUSE, at construction and by relation identity —
naming the relations as written and the classes that stated them:

- a block containing a WIRING or a DERIVED COORDINATE, saying that
  neither carries a jump node and neither can therefore be switched;
- a block whose members' UNCONDITIONAL dependencies still form a cycle,
  under the refusal the compile requirement states — a cycle present on
  every piece is a cycle the run cannot order;
- a block one of whose driven ends the run does not BANK — a plain port
  or a derived coordinate — saying that a block advances its coordinates
  piece by piece and only a coordinate the run owns keeps that history,
  and to state the relation into the joint coordinate so the port follows
  it;
- a block member whose driven end is a GROUP, saying that a member of a
  block drives ONE coordinate.

**Over a stretch of a tick the block's SELECTORS SHALL be located
first.** Every selector's level SHALL be followed along the path its
coordinates take over the stretch — commanded motion for an input and
law-determined motion for a driven source, retaining its timing — and the
stretch SHALL be CUT at every surface any of them
reaches: solved exactly where that level is affine or PIECEWISE AFFINE —
the requirement "A kink is a cut, and a piecewise-affine quantity is
solved" — otherwise sampled at
the same fixed number of sub-intervals and bisected to the same tolerance
a jump crossing already uses. Two cuts within that tolerance SHALL be
ONE, a tick cut more times than the stated maximum SHALL be refused
exactly as any other over-crossed tick is, and no further tolerance SHALL
be introduced.

**On each piece the block SHALL be ORDERED and then RUN.** Every
selector's branch SHALL be read at the piece's MIDPOINT; what each member
reads with THOSE branch values substituted — not the compile's zero ones
— SHALL give the piece's ACTIVE dependencies; and the members SHALL be
ordered topologically over them.
A piece whose active dependencies are STILL CYCLIC SHALL REFUSE the tick,
naming the piece, the selector branches it was read under and the
relations on the cycle, and SHALL COMMIT NOTHING: the bank, the tick
count, the tree and the records SHALL stand as they were and the commands
that moved an input SHALL be retired refused, exactly as for a conflict.

**On a piece a selector SHALL be a CONSTANT for every member of the
block**: the branch read at the midpoint SHALL be substituted into the
member's own integration rather than re-located by it, so the order the
block chose and the branch the member reads cannot disagree. Each member
SHALL otherwise be integrated over the piece by the rules that already
govern it — the jump partition, and the walk of a law that reads the
coordinate it drives — with each active determined source following the
motion its law gives it
at the corresponding point of the request, including its dwell, crossings
and landing. This SHALL also hold for determined sources upstream of the
block. Restricting a source to a piece SHALL retain that motion's timing,
not substitute a straight line between the piece's endpoints. Inputs and
held coordinates SHALL retain their commanded and constant paths,
respectively.

The block's contribution to each of its coordinates SHALL be the sum over
the pieces. Where ANY piece's integration LANDED a coordinate at an
absolute value, the block SHALL report for that coordinate the ABSOLUTE
value it has itself advanced it to by the END of the stretch — that
landing, and every increment the later pieces gave it — and the run SHALL
commit that value exactly where it commits a landing of a law that reads
the coordinate it drives. A coordinate no piece landed SHALL be reported
as an increment only, and committed as its value plus that increment. A
landing followed by further motion SHALL therefore commit the motion:
reporting the landing alone would discard it. Every crossing a piece
reports SHALL be recorded at its fraction of the whole tick, and a
selector's own crossings SHALL be recorded as the crossings of the member
whose law states them.

A source a piece's fold switched OUT, and which the piece's order has not
yet determined, SHALL be given to the member that reads it at the value
the block has advanced it to at the piece's START, moving by nothing.

**A selector crossing is NOT a stop.** It SHALL stop no input, retire no
command, and appear in the crossing record rather than the stop record. A
DECLARED RANGE on a coordinate a block determines SHALL stop it exactly
as it stops any other, located through the block, and SHALL be committed
at its bound even where a piece of the same segment landed it elsewhere.
An input that reaches a stopped coordinate only through a selection that
is INACTIVE over the stretch SHALL NOT be stopped by it.

**At rest a block relation SHALL bind nothing.** It SHALL be recorded
solved FORWARD, its law unapplied, so the rest render poses the tree from
the author's own rest default and the run refuses by name when there is
none. Binding the whole bank again, rendering, or inspecting the tree
SHALL advance a block's coordinates by nothing.

**Membership SHALL be decided BEFORE the rest render**, over the
relations, wirings and derived coordinates of the linked tree, each read
in the direction it is DECLARED. Every relation on a dependency cycle
that determines at least one coordinate the run BANKS SHALL be so
decided, whether it names one coordinate at each end or several, so that
every such cycle reaches the compile and is answered there by name rather
than by the rest render's own refusals. A cycle that determines NO banked
coordinate SHALL be left alone and SHALL behave exactly as it does
without this requirement.

Deciding membership again over the same tree SHALL give the same answer,
and a simulation constructed over a tree a previous simulation owned
SHALL decide it afresh, so a tree posed by one run and handed to another
carries nothing of the first.

Under a root that does NOT declare `Time.running()` nothing SHALL change:
the same relations SHALL be solved, deferred and refused by the ordinary
enumeration exactly as they are without this requirement.

**A SELECTION CHANGE ALONE SHALL MOVE NOTHING.** A selector is a jump
node, and a jump never moves a part: with its sources otherwise still, a
tick in which a selection changes SHALL commit every coordinate of the
block unchanged.

A command taken in one tick, and the same command taken in many, SHALL
agree within the run's own agreement window for every coordinate and for
the travel each command admits, and EXACTLY for every command's STATUS
and for every discrete reading of a coordinate — a gate set or not, a
digit — taken where no committed value stands within that window of a
surface, a bound or a gate threshold. The travel a command admits is
accumulated once per tick and SHALL NOT be required to agree bit for bit
across two partitions of one command.

The program's IDENTITY SHALL distinguish a program carrying a block from
one that does not, and SHALL distinguish two programs whose blocks hold
different members. A block's members SHALL be listed in an order
deterministic for a given tree, and the program's listing SHALL name the
block at its position in the program's order and then carry each of its
members' own entries, so the identity covers every member's ends,
direction and expression as it does any other edge's.

Adding later stations whose active motion does not influence an earlier
carry SHALL NOT alter that carry's physical outcome. Additional internal
partition boundaries SHALL NOT re-time a source's motion. Existing
agreement windows and the status/discrete-reading rules above SHALL apply.

The source-timing guarantee SHALL apply to ordinary chains as well as
selected blocks: freezing a selection SHALL NOT change the physical timing
of the same laws. Existing exact affine propagation SHALL retain its result;
ordinary endpoint approximations that lose a dwell or landing SHALL be
corrected rather than preserved for compatibility.

#### Scenario: An ordinary frozen carry retains the same timing

- **WHEN** the existing ShiftedCarry at shift 0 and its FixedZero ordinary
  acyclic twin move crank 0..4, with a carry landing at 1 and gate at .5,
  in one move and again in sixteen portions
- **THEN** both versions finish with carry.travel 1 and higher.turn 3.5,
  commands completed with full travel admitted, rather than the old bulk
  result 2 produced by spreading the lever's stroke over the whole request

#### Scenario: A carriage selects which wheel a lever reads

- **WHEN** a running root states a lever driven by `lower.turn` gated by
  `shift < .5` and by `higher.turn` gated by `shift >= .5`, and a
  `higher.turn` driven by the crank gated by `shift >= .5` and by the
  lever gated by `shift < .5` — a union the compiler cannot order — with
  a rest default on every driven coordinate
- **THEN** construction succeeds, the program carries ONE block holding
  those two relations, and its listing names the block

#### Scenario: The carry happens at one position and not the other

- **WHEN** that root is cranked with `shift` at `0`, and again with
  `shift` at `1`
- **THEN** at `0` the lower wheel drives the lever and the lever advances
  the higher wheel, at `1` the higher wheel drives the lever and the
  higher wheel is driven by the crank directly, and each result equals
  the one the SAME laws give with `shift` frozen at that value and
  compiled as an ordinary acyclic program

#### Scenario: A selection change inside a tick moves nothing

- **WHEN** `shift` is moved from `0` to `1` in one tick, crossing both
  selectors, with every other input standing still
- **THEN** every coordinate of the block commits the float it held, the
  selector crossings are recorded in `sim.crossings`, and no stop is
  recorded

#### Scenario: A shift away and back preserves every part's state

- **WHEN** the crank is turned until the lever is set, the carriage is
  shifted to another position, the crank is turned again, and the
  carriage is shifted back
- **THEN** the lever still stands where the mechanism left it, each wheel
  holds the angle its own motion gave it, and nothing was reset by the
  shifts

#### Scenario: A finer partition agrees with a coarser one

- **WHEN** the same crank travel is requested as one tick, as twelve, and
  as two hundred and forty, each from the same restored snapshot, with
  every gate threshold and declared bound chosen away from where a tick
  ends
- **THEN** every coordinate agrees within the run's agreement window,
  every command's admitted travel agrees within that same window, and
  every command reports the same status

#### Scenario: A landing in one piece and motion in a later one commit both

- **WHEN** one tick carries a selector crossing, a coordinate the block
  drives is landed at a gate in the piece BEFORE that crossing, and the
  selection the crossing brings in drives that same coordinate further in
  the piece after it
- **THEN** the bank commits the absolute value the block advanced it to
  over the whole stretch — the landing plus the later piece's increment —
  and not the landing alone

#### Scenario: A switched-out source is handed no motion

- **WHEN** a piece's selection switches an in-block source out of a
  member's law, and the same tick is run again with that source given a
  different increment
- **THEN** the member's contribution on that piece is the same float in
  both runs

#### Scenario: A cycle with no self-read and no selection is refused by the compile

- **WHEN** a running root states an UNCONDITIONAL cycle of multi-source
  relations, none of which gates a source behind a jump node and none of
  which reads the coordinate it drives, each driven coordinate carrying
  its own guarded rest default
- **THEN** construction is refused naming the relations on the cycle and
  the coordinates they wait on — the compile's own refusal, rather than
  the rest render's refusal of a doubly bound coordinate

#### Scenario: A selected cycle with no self-read is admitted

- **WHEN** the same cycle gates each in-block source behind a comparison
  on a coordinate it does not determine, still with no relation reading
  the coordinate it drives
- **THEN** construction succeeds, the program carries one block holding
  those relations, and each driven coordinate's rest value is its own
  guarded default

#### Scenario: A cycle no selection breaks is refused at construction

- **WHEN** a running root states the same two relations with their
  selections removed, so each reads the other's coordinate
  unconditionally
- **THEN** construction is refused naming both relations and the
  coordinates they wait on

#### Scenario: A plain port among a block's driven ends is refused

- **WHEN** one of the two relations drives a plain port that a wiring
  carries into a joint coordinate, rather than the joint coordinate
  itself
- **THEN** construction is refused naming the relation and the port, and
  saying that only a coordinate the run owns keeps a block's history

#### Scenario: A piece that cannot be ordered refuses the tick

- **WHEN** a running root's two selections are written so that some
  reachable value of the selecting input leaves both dependencies active
  at once, and the input is moved to that value
- **THEN** the tick is refused naming the selector branches and the
  relations on the cycle, `sim.state` is the bank the previous tick
  committed, the tick count did not advance, and the commands that moved
  an input report `refused`

#### Scenario: An inactive association does not block an input

- **WHEN** a wheel the block drives declares a range, stands at its
  bound, and an input that reaches it ONLY through a currently inactive
  selection is moved
- **THEN** that input's command is not retired `blocked`, it admits its
  whole travel, and the stopped wheel does not move

#### Scenario: A range on a block coordinate stops it and wins over a landing

- **WHEN** a coordinate the block drives declares a range and one tick
  both lands it at a gate and carries it past that range
- **THEN** it is committed AT its bound, the stop is recorded naming the
  inputs that pushed it, and the landing does not overwrite the bound

#### Scenario: A block member that reads its own coordinate walks inside each piece

- **WHEN** one of the block's relations also reads the coordinate it
  drives through a switch — a latch set by a pin and reset by a cam — and
  one tick carries both a selector crossing and a crossing of that
  latch's own gate
- **THEN** both crossings are recorded at their own fractions of the
  tick, the latch is committed at the value its walk left it at, and the
  tick's result equals the one the same tick gives with the selection
  frozen at each of its two branches over the corresponding parts of the
  travel

#### Scenario: Later result stations preserve an earlier carry

- **WHEN** Curta's unchanged result-carry diagnostic sets digit to 0,
  height to 9, crank angle to 90 and then requests crank angle 180 in one
  unsplit move, with six, seven and eleven active result stations
- **THEN** every move completes, ones.turn ends at 724, tens.turn ends at
  704 and the first lever ends at 0 within the existing agreement window,
  with the same earlier carry in all three graphs

#### Scenario: A dwelling predecessor is not replaced by a ramp

- **WHEN** a selected carry chain contains a source which moves and then
  dwells or lands, and the same physical request is made with an additional
  station whose selection changes but cannot influence that carry
- **THEN** the earlier successor receives the same timed physical motion
  and produces the same carry whether or not the later station is present

#### Scenario: An upstream driven source retains its timing

- **WHEN** the carry's driving shaft has nonuniform motion during a
  request and the same request is executed whole or in smaller portions
- **THEN** the full bank and admitted travel agree within the existing
  window, with identical statuses and discrete readings away from the
  threshold neighborhoods defined above

#### Scenario: Observing the full result bank does not lose the carry

- **WHEN** the eleven-station Curta result-carry diagnostic makes that same
  unsplit request with its original ones and tens contact constraints
- **THEN** the crank reaches 180 with completed status and tens.turn 704,
  without disabling a constraint, reducing the bank, changing a law, or
  subdividing the pilot's request

### Requirement: A kink is a cut, and a piecewise-affine quantity is solved

Under a running root a quantity the run has to follow along a tick's path
— a jump node's LEVEL QUANTITY, a law's SKELETON, a determiner's value —
SHALL be classified from its expression alone, once, at compile:

- AFFINE in the sources: a number, a source name, a branch placeholder
  (a constant on the piece being cut), a unary minus, a sum or difference
  of affine operands, a product with a constant operand, or a quotient by
  a constant one.
- PIECEWISE AFFINE in the sources: the same, admitting KINK NODES whose
  operands are themselves affine or piecewise affine. The KINK NODES
  SHALL be exactly the CONTINUOUS SELECTIONS of the symbolic vocabulary —
  `abs(x)`, `min(a, b)` and `max(a, b)` — each of which returns one of
  its operands exactly and is continuous where they meet. `clamp`,
  `clamp01`, `ramp` and `piecewise` are compositions of those over their
  arguments and SHALL therefore be piecewise affine wherever their
  arguments are.
- Neither: a call outside the kinks — `sin`, `cos`, `tan`, `asin`,
  `acos`, `atan`, `atan2`, `sqrt` — a power, or a product or quotient of
  two operands that both move.

A kink node SHALL have a LEVEL of its own — `x` for `abs(x)`, `a − b` for
`min(a, b)` and `max(a, b)` — and ONE surface, at zero. Its BREAKPOINTS
over a stretch of the path SHALL be the fractions at which that level
reaches zero, computed in the graph's POSTORDER so that a kink nested
inside another's level is cut first: on each sub-interval its inner kinks
have already produced, the level is affine, and its zero SHALL be SOLVED
from the sub-interval's two endpoint values. No sampling, no bisection
and NO FURTHER TOLERANCE SHALL be introduced; two breakpoints closer than
the crossing tolerance SHALL be one, exactly as two crossings are.

**A kink breakpoint is NOT a crossing.** The quantity is CONTINUOUS
there: the breakpoint SHALL NOT be recorded among the tick's crossings,
SHALL NOT enter the jump partition a law's increment is summed over,
SHALL NOT move a coordinate to the far side of anything, and SHALL NOT
count toward the maximum number of crossings a tick admits. It is a
sub-division used to SOLVE, and a machine whose laws carry no kink SHALL
pay nothing for this requirement.

Classification SHALL be conservative and structural: a quantity the rules
above do not classify SHALL keep the sampled search unchanged, with the
same sub-interval count, the same bisection and the same documented
limit. In particular a kink over a CURVED operand — `max(0, sin(x))` —
is not piecewise affine and SHALL be searched, even though a particular
piece of it may happen to be constant.

#### Scenario: A clamped window's crossing is solved, not searched

- **WHEN** a running root's law gates on a comparison whose level reads
  `clamp01((control − 0.1) / 0.8)` of a driver, and the gate's surface is
  crossed strictly inside a tick in which the clamp itself is not at
  either of its kinks
- **THEN** the crossing is located at the fraction the affine solution
  gives, to within a few units in the last place, rather than to the
  bisection's own tolerance, and the tick evaluates the law a small
  bounded number of times rather than once per sub-interval of the search

#### Scenario: A path that crosses the kink is cut there before it is solved

- **WHEN** the same law is driven over a tick whose path takes the clamp
  from inside its window out past `1`, and the gate's surface lies beyond
  the kink
- **THEN** the crossing is located exactly on the sloped piece it
  actually lies in, and the answer equals the one the same movement gives
  when it is split into two ticks meeting at the kink

#### Scenario: A stop on a kinked determiner that carries no jump at all

- **WHEN** a coordinate declaring a range is driven by a law with no jump
  node in it whose value is `4 + 72 * clamp01((lever − 113.5) / 11.25)`,
  and one tick's path starts on the law's FLAT piece and would end past
  the bound on its SLOPED one
- **THEN** the stop is located at the fraction on the sloped piece, the
  coordinate is committed AT its bound exactly, and the answer is not the
  one a single linear division over the whole tick would give

The classification SHALL remain INTERNAL to the run. The published
document says, per driven end of a law and per jump, whether that
quantity is AFFINE in its sources — a two-valued statement a consumer
uses to choose between a solution and a search — and a PIECEWISE AFFINE
quantity is not affine. So a kinked quantity SHALL publish that flag as
FALSE, exactly as it does before this requirement exists, and no
published document SHALL change and no document version SHALL move
because a quantity is now cut at its kinks. A consumer that has not
learned to cut at a kink SHALL therefore keep searching such a quantity,
which is correct and slower.

#### Scenario: A kinked quantity still publishes itself as not affine

- **WHEN** a running root whose law has a kinked determiner, and whose
  gate has a kinked level, is exported before and after this requirement
  exists
- **THEN** both documents declare the version they always did and are
  byte-identical, the law's driven end publishing `affine` FALSE and the
  jump publishing `affine` FALSE in each

#### Scenario: A curved law is searched exactly as before

- **WHEN** a running root's law carries `sin` or `cos` of a moving
  source, or a product of two moving sources
- **THEN** its crossings and any stop on it are located by the same
  sampled search, at the same sub-interval count and tolerance, and the
  number of evaluations the tick pays is unchanged

### Requirement: Only what moves along a tick's path is evaluated

Under a running root the engine follows a quantity along a tick's path by
evaluating its expression at many points of that path: the sub-intervals
of a sampled search, the two ends of each piece of a solve, the midpoint
of each piece of a partition. Over ONE path, with ONE branch reading, the
value of a part of that expression CANNOT change — the part that reads no
source the tick moves. That part SHALL be computed ONCE and read back at
every point, and only the remainder SHALL be evaluated per point.

Which names MOVE along a path SHALL be the run's own statement and never
inferred from sampling or from a tolerance:

- a source whose increment over the tick is non-zero MOVES;
- a jump node's BRANCH, which is a constant of the piece by construction,
  STANDS;
- the coordinate a law READS AND DRIVES moves for a quantity the walk
  hands its value to per point, and stands for one that by refusal does
  not name it at all.

The arithmetic SHALL be unchanged: the same nodes, in the same order,
through the same operators, on the same operand values. A quantity's
value at any point of a path SHALL therefore be the SAME FLOAT, bit for
bit, that evaluating its whole expression at that point gives. This
requirement changes what the run COMPUTES TWICE and SHALL change no
crossing, no landing, no branch reading, no increment, no stop, no
refusal and no committed value.

The saving SHALL be structural and unconditional. No declaration, option,
tolerance, cache size or sampling count SHALL be introduced, and nothing
an author writes SHALL select it. A machine whose laws are small or whose
followed quantities move entirely SHALL be no slower for it than the cost
of deciding, once per quantity per tick, which of its nodes move.

The COUNT of evaluations a tick pays SHALL NOT change: the same points
are evaluated, and a point evaluated through a followed path SHALL be
counted as one evaluation by any probe that counts them, so the
evaluation counts other requirements pin stand unmoved. What falls is the
work inside one evaluation, and a probe that reports the run's cost SHALL
be able to report it in the unit that moves.

#### Scenario: A searched crossing evaluates only the moving part of the law

- **WHEN** a running root's law reads its own driven coordinate through a
  skeleton the run cannot classify — a detent cam carrying `sin`, `cos`
  and `sqrt` of a kinked phase — and that law also reads a chain of
  sibling coordinates that the tick does not move, so that most of the
  expression stands
- **THEN** the crossing is located by the same sampled search, at the
  same sub-interval count, the same tolerance and the same number of
  evaluations, and the work the tick does inside that search falls by
  the share of the expression that stands

#### Scenario: Every value the machine commits is unchanged

- **WHEN** that machine is stepped for a dozen ticks
- **THEN** every banked coordinate, every recorded crossing, every
  landing and every stop is the value it was before this requirement,
  bit for bit, and the conformance corpus replays byte-identical

#### Scenario: A quantity that moves entirely is evaluated whole

- **WHEN** a law's followed quantity reads only sources the tick moves,
  so that nothing in it stands
- **THEN** every point evaluates the whole expression exactly as before,
  and the tick pays the decision of which nodes move once for that
  quantity rather than once per point

#### Scenario: A branch reading holds for its own piece and no other

- **WHEN** a tick's path is cut into several pieces and a jump node reads
  a different branch on each
- **THEN** the part of the expression that stands is computed again for
  each piece, under that piece's own branches, and no value computed
  under one piece's branches is read back under another's

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
   commits on the other edge states it by negating its own level. Where the
   crossing is the path's own OPENING — the level standing exactly on a
   surface at the value the request starts from — there is no piece behind
   it, and the branch before SHALL be read AT THE START and the far side
   asked for at the next representable value the path reaches.
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
   beyond it, and a non-strict comparison lands on the threshold itself. The
   walk SHALL bracket in a first step sized by the SEGMENT it walks on — the
   larger of the landed value's own magnitude and the magnitudes of the
   path's ends — and never by the magnitude of a value that happens to be
   zero, whose own step is a denormal no segment can express.
5. **A crossing belongs to the request whose path CONTAINS its landing.** A
   landing ON the request's endpoint is that request's, so a request that
   ends exactly on a NON-STRICT surface has reached it. A landing one
   representable value BEYOND the endpoint — which a STRICT comparison
   reached exactly produces — is NOT that request's, and SHALL be fired by
   the NEXT request, which begins on that surface and whose path contains
   the landing. Containment SHALL therefore be judged by the LANDING and not
   by the fraction at which the crossing was solved: a crossing solved at
   fraction ZERO whose far side lies ahead inside the path IS an event, and
   a request resuming from its OWN landing still fires nothing, because
   there the landing IS the value the request starts from.
6. Every relation firing at that event SHALL evaluate its `at` and `law`
   callables at that input value and at the PRE-EVENT value of every state —
   including a state the same relation writes and a state another relation
   writes at the same event — and the targets SHALL take the results
   together. Declaration order SHALL NOT be observable. Two relations firing
   at one event and writing DIFFERENT states is that synchronous case; two
   firing at one event and writing the SAME state is a CONFLICT, and the
   whole REQUEST SHALL be refused, naming the state by its qualified id,
   both relations as written and the landing, and committing nothing.
7. The remaining path SHALL be solved again from the landing with the new
   bank, so an event surface that reads a committed state moves with it. The
   process SHALL repeat until the path is exhausted.

A commit value that is not a FINITE number — an infinity or a NaN — SHALL
refuse the WHOLE request, naming the relation as written, the state by its
qualified id and the value, and SHALL commit nothing: a bank holding such a
value poses nothing, satisfies no bound and carries no later event. The
judgement SHALL be made BEFORE an integer state's rounding, so a
`dtype=int` target SHALL refuse by that message rather than by the
rounding's own overflow. A document cannot express a raise, and the export
requirement "A published commit says what it reads, writes and fires on"
therefore has a CONSUMER that computes a non-finite commit value refuse the
request rather than bank it; the two runtimes refuse the same request.

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
the travel ADMITTED, BOTH ENDS OF THE PATH IT TRAVELLED, the bounds met and
the events it fired, each event entry
carrying the relation as written, the fraction of the path, the moving
input's value at the event, and the targets with their new values. The two
ENDS SHALL be the value the moving input stood at when the request began and
the value it ended at, each taken VERBATIM from the bank and therefore in the
input's own NATIVE units — the units each event entry's value speaks — so
that every event's value lies on the segment they span. Neither end SHALL be
left for a caller to recompute: the admitted travel is in DESIGN units, a
`by=` request's `by` is the ASK and not the travel, and a caller
reconstructing an end by arithmetic could land on a float the machine never
stood at and so read a fired event as unfired. The admitted
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
`commands`, `program` and `crossings`
SHALL each be refused by name, under every time base. `sim.trigger(name)`
SHALL NOT be refused: an instruction under a clocked root is ONE request and
nothing else, under the requirement "Instructions carry design-unit targets",
and it is the one verb of that list with a meaning here. `sim.time` SHALL be
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

#### Scenario: A non-finite commit refuses the request

- **WHEN** a committing relation's law computes an infinity or a NaN for a
  state it writes, whether that state declares `dtype=int` or not
- **THEN** the request is refused naming the relation, the state and the
  value, and the bank, the tree and the record stand exactly as they did
  before it

#### Scenario: A relation no driver can reach is refused

- **WHEN** a committing relation's sources are all states, so that no
  declared driver can move its event level
- **THEN** simulation construction is refused naming the relation and saying
  its event level moves with no declared driver

#### Scenario: The cadence surface is refused

- **WHEN** a clocked simulation calls `run`, `every`, `tick`, `rate` or
  `commands`, and a clocked simulation over a root declaring no time base also
  calls `time`
- **THEN** each is refused by name, saying a clocked model has no cadence,
  and the `time` refusal names `Time.elapsed()` as the way to have a clock

#### Scenario: A request ending exactly on a strict surface leaves it for the next request

- **WHEN** a committing relation states `at` as a STRICT comparison against a
  representable threshold and a request ends exactly ON that threshold
- **THEN** the request fires nothing, and the next request, beginning on that
  threshold, fires the event once at the first representable value past it,
  while the non-strict twin of the same relation fires on the FIRST request,
  at the threshold itself, and fires nothing on the one that resumes from it

#### Scenario: A stop from a coordinate standing at zero admits no travel

- **WHEN** a bank stands outside a LOW bound with the moving input at exactly
  `0.0`, and a request pushes it further outside
- **THEN** the request admits ZERO travel, fires nothing, commits nothing and
  reports its stop, exactly as the same machine's HIGH bound does from a
  coordinate whose magnitude is large

#### Scenario: A request reports both ends of its path

- **WHEN** a request is made `by=` a travel over an input standing away from
  zero, and another is CLIPPED at a declared bound
- **THEN** each request reports the value the input stood at before it and the
  value it stands at after it, both equal to the bank's own entries before and
  after, every event's value lies between them, and the clipped request's
  second end is the landing the stop gave it and not the value asked for

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

### Requirement: A running play law collects and releases a retained coordinate

For each admitted monotonic source segment ending at `x'`, a play edge with retained start `y` SHALL end at `max(x' - high, min(y, x' - low))`.  It SHALL use the run's existing bank as the only history, apply no tolerance, retain the follower throughout the clearance, collect it at either flank, and release it immediately when the source reverses away from that flank.

#### Scenario: Forward pickup and immediate reversal
- **WHEN** `Play(low=-329, high=3)` starts at source and follower zero, the source advances through `3` to `1590`, and then reverses to `1580`
- **THEN** the follower reaches `1587` and remains exactly `1587` during the reversal

#### Scenario: The opposite flank picks up after clearance
- **WHEN** the same source continues backward across the 332-degree clearance
- **THEN** the follower remains retained until `source - follower == -329` and then follows the source backward at that offset

#### Scenario: Exact and non-integer contacts need no tolerance
- **WHEN** either exact endpoint or a finite non-integer contact offset is reached and reversed in either direction under different positive `dt` values
- **THEN** collection and release follow the same projection exactly, with no epsilon-dependent branch or cadence-dependent answer

#### Scenario: Split commands equal one monotonic command
- **WHEN** one monotonic travel is issued as one request or as arbitrary consecutive partial requests with the same path
- **THEN** every final play coordinate agrees under the run's existing numeric agreement contract and snapshot replay reproduces the same bank; a follower retained without motion keeps its held float exactly

### Requirement: A play source path is proved before it runs

The compiler SHALL admit a play source only when it is a run-owned driver or the unique output of another play edge rooted transitively at one run-owned driver.  It SHALL refuse cycles, ambiguous writers, ordinary law, wiring, formula, or otherwise potentially reversing sources before a tick runs. Each coordinate SHALL source at most one play edge; ordinary downstream observers do not count as play branches.

#### Scenario: Play fan-out is refused
- **WHEN** one coordinate sources two different play edges
- **THEN** construction refuses the branching play graph by relation identity, while ordinary downstream observers remain permitted

#### Scenario: Three wheels form a play chain
- **WHEN** a driver feeds three play edges in sequence
- **THEN** compilation orders one linear chain and a monotonic driver request projects through all three edges

#### Scenario: A source can reverse inside a tick
- **WHEN** a play edge reads an ordinary law or formula whose path can rise and fall while its net increment is zero
- **THEN** simulation construction refuses the play edge by identity rather than applying its endpoint projection to the net increment

#### Scenario: An invalid initial state is not teleported
- **WHEN** simulation construction finds the retained value outside `[source-high, source-low]`
- **THEN** construction refuses with the relation, source, retained value, and admissible interval, and changes no state

### Requirement: Stops through play chains locate the originating request

A stop on a coordinate produced by a play chain SHALL be located by replaying the complete chain from the originating driver's requested path.  The run SHALL atomically commit the originating input and every play coordinate at the located fraction, block the request only when it pushes the stopped coordinate, and preserve its existing rollback on refusal.

#### Scenario: A downstream stop is located through both clearances
- **WHEN** source `x=0` drives two play gaps of `10`, `x` requests `100`, and the second follower has a high stop at `20`
- **THEN** the request stops with `x=40`, the first follower `30`, and the second follower `20`, rather than locating from the first follower's net delta

#### Scenario: A released follower does not block its source
- **WHEN** a bounded follower stands at contact and the source reverses into the clearance so that the follower remains still
- **THEN** the source request remains free and the follower's bound reports no pushing stop

#### Scenario: A refused tick is atomic
- **WHEN** play propagation or a stop invariant refuses a tick
- **THEN** the bank, tick, crossing and stop records, and posed tree remain exactly as before the tick, and commands that attempted travel retire `refused` with no travel admitted, preserving the existing running refusal contract

#### Scenario: Reset and restore retain no hidden play state
- **WHEN** a play simulation is snapshotted, advanced, restored, and reset
- **THEN** subsequent answers derive only from the restored ordinary bank and program identity and match a fresh simulation at that state

### Requirement: Declared time drives retain motion across operating history

A running simulation SHALL advance a relation explicitly sourced by its
root's time without a command, according to the existing continuous-law
increment, jump-subtraction and supported self-read rules. At tick `k`,
elapsed seconds SHALL traverse `[k*dt, (k+1)*dt]`; an instantaneous input
operation SHALL traverse no time. The first tick starts from the numeric
rest at time zero. Ordinary driver inputs SHALL still move only through
their admitted commands. A relation's value SHALL NOT be reinterpreted as
a velocity: the existing multivariate incremental law semantics SHALL apply.

A disabled relation SHALL contribute no motion when its declared law
contributes none. Its banked coordinates SHALL hold and resume from those
held values, without accumulating or recovering motion for elapsed intervals
in which the drive was disengaged. Enable discontinuities SHALL be handled
by the existing jump-subtraction rules, not by resetting the joint to an
absolute time-derived value. A nonlinear time law SHALL use current global
seconds, not a mechanism-local clock, when re-enabled.

Each resolved relation naming time SHALL have one independent time-drive
admission identity. Its multiple targets SHALL share that identity, and its
downstream relations SHALL follow the retained motion of their declared
source coordinates. Two separate time drives SHALL NOT be treated as one
physical input just because they read the same clock. Stops SHALL suppress
only the admissions the existing source-sensitive stop test identifies as
pushing the affected mechanism. Disengaged and unrelated drives SHALL
continue. Existing incompatible-writer conflicts SHALL remain atomic
refusals, not be resolved by giving one drive priority.

A stopped time admission SHALL remain suppressed through that tick's
remainder. Its time path SHALL hold at the stopping instant for that
remainder; other sources SHALL follow their remaining admitted paths.
On the next tick it SHALL attempt only that tick's elapsed interval, without
an increment for the gap since it last moved. A still-active bound SHALL
admit zero; a subsequently released constraint SHALL permit new motion
without a new command. There SHALL be no deferred travel and no hidden
restart latch. An operator command stopped by the same mechanism SHALL
still retire `blocked`; it SHALL NOT acquire automatic retry.

The global clock SHALL advance for every successful advancing tick even
when all mechanical motion stops. Failure SHALL commit neither time nor
mechanical state nor partial records. Snapshot, restore and reset SHALL
reproduce the clock, bank and subsequent time-driven behavior without extra
author-managed phase state. A non-ticking pose, render, publication or state
read SHALL leave the retained state untouched.

When recording is enabled, a running stop SHALL keep `inputs` as actual
driver IDs and SHALL additionally expose `time_drives` as a sorted tuple of
the blocked time-drive IDs, empty when none are blocked. Existing fields and
command-only serialized records SHALL retain their representation; serialized
records SHALL add `time_drives` only when nonempty. The IDs SHALL map to the
relations in the published program. Repeated attempts against a standing bound
may record a new zero-travel stop on each advancing tick, within the existing
bounded ring policy.

#### Scenario: Construction and inspection do not run a shaft

- **WHEN** an affine time-driven shaft with zero rest is constructed,
  inspected, rendered and published before any tick
- **THEN** its retained angle remains zero and no command or tick is created

#### Scenario: Seconds drive a retained shaft without a rate command

- **WHEN** `time.drives(shaft.turn, ratio=6)` starts at zero and advances
  two simulated seconds at `dt=0.02` with no commands
- **THEN** `shaft.turn` is 12 native angular units, `sim.time` is 2,
  and the command registry and declared input set remain empty

#### Scenario: Enable changes preserve accumulated angle

- **WHEN** the law is `6*t*(enabled > 0.5)`, it runs enabled for two
  seconds, is disabled instantaneously for two more, is enabled
  instantaneously again and runs for one more second
- **THEN** the shaft reads 12 before disabling, 12 throughout the disabled
  interval and both input changes, and 18 at time 5

#### Scenario: Winding changes reserve without rewinding the train

- **WHEN** the Astrarium-equivalent fixture uses
  `(time & enabled & wind & shaft.turn)` with the law
  `t*(enabled > 0.5)*(angle-wind < 10)`, and
  `(shaft.turn & wind)` drives a weight by `angle-wind` in range 0 to 10;
  it runs two seconds, is disabled for two, winds by 2 instantaneously,
  then is enabled and runs another second
- **THEN** the shaft reads 2 throughout stopping and winding, the weight
  moves from 2 to 0 when wound, and they end at shaft 3 and weight 1
  at time 5 without a dummy input or rate command

#### Scenario: Exhaustion and rewind resume only new motion

- **WHEN** the same fixture runs for twelve seconds, is disabled, winds
  by 5 instantaneously, is enabled and runs another second
- **THEN** exhaustion leaves shaft and weight at 10 at time 12, winding
  leaves shaft at 10 and weight at 5, and resumption ends at shaft 11 and
  weight 6, without catching up the two exhausted seconds

#### Scenario: A hard stop holds the connected train but not another time drive

- **WHEN** one time relation drives a shaft at 1 unit per second, that shaft
  drives a weight at ratio 1 bounded at 2.5, and an independent time
  relation drives another shaft at 2 units per second; four one-second
  ticks run from zero
- **THEN** the first shaft and weight end at 2.5, the independent shaft
  ends at 8 and time at 4; the first stop lies halfway through tick 3,
  and its record names the first time drive, no unrelated drive and no
  fabricated operator input

#### Scenario: Grouped targets share one physical drive

- **WHEN** one time-source relation gives two shaft coordinates and a
  downstream bound stops motion supplied by that relation
- **THEN** both targets receive only their coherent admitted prefix,
  while a separately declared unrelated time drive continues

#### Scenario: Release takes effect without restarting a rate

- **WHEN** a time-driven coordinate has stopped at a bound, a zero-duration
  operator action relieves that constraint, and one more tick runs
- **THEN** the coordinate gains only the new tick's permitted motion, no
  command is created, and elapsed time includes the stopped interval

#### Scenario: Retained phase and global time are not conflated

- **WHEN** a shaft follows the law `t*t*(enabled > 0.5)`, runs for one
  second, is disabled until time 3 and then runs enabled until time 4
- **THEN** its retained value is 1 while disabled and 8 at time 4,
  because the last interval contributes `4*4-3*3`, not a restarted age

#### Scenario: Snapshot replay and reset include autonomous motion

- **WHEN** a snapshot is taken before a sequence of running, disabling,
  winding and restarting, then restored and the same operations repeated
- **THEN** every tick's bank, time, stops and crossings agree within the
  existing numerical contract; reset returns the original bank and tick,
  after which the first tick behaves exactly like a fresh run

#### Scenario: A late failure cannot leave a partially advanced clock

- **WHEN** a segmented tick first reaches a stop and then encounters an
  existing-law conflict on an independent branch
- **THEN** neither elapsed time, any bank value nor any ring entry commits;
  actual moved commands retire as refused under the existing rule

#### Scenario: Commanded and pose-only running models remain unchanged

- **WHEN** existing commanded-driver fixtures and a root using time only
  for a plain part's absolute pose are run without declared time drives
- **THEN** their state, command outcomes, ownership checks and clock
  behavior match the pre-change fixtures

### Requirement: Ancestor constraints stop the existing mechanical coordinates

A simulation SHALL enforce constraints declared on existing descendant
joints by their ancestors through the same stop semantics as the target's
own range. The own-coordinate argument SHALL retain the existing committed
tick/request-start reading and additional reads SHALL follow the attempted
motion. A running read SHALL be an actual banked coordinate or input;
ordinary and derived ports SHALL remain refused.

Blocked commands SHALL report admitted travel on the existing inputs and
actual constrained coordinate, with no retained backlog or automatic
resumption. Motion of a read that would invalidate a standing target SHALL
be stopped according to the existing cross-coordinate constraint rule.
Relieving or unrelated motion SHALL retain its existing admissibility.
Transaction, snapshot, restore and reset behavior SHALL remain unchanged.
Clocked constraints SHALL retain the clocked solver's existing supported
expression classes and refusals.

#### Scenario: A nested crank stops against a retained shaft

- **WHEN** an existing nested crank joint is constrained by an ancestor's
  bound reading a separately nested retained shaft, and a crank request
  crosses that limit
- **THEN** the request stops at the allowed boundary, reports blocked with
  its admitted travel, and neither moves the held shaft nor completes the
  rejected remainder

#### Scenario: A moving read cannot overrun a standing target

- **WHEN** the constrained target stands still and motion of a read would
  carry its constraint outward
- **THEN** the responsible input stops through the same dependency rule as
  an ordinary joint-local `Bound`, without snapping the target

#### Scenario: A blocked request is not queued for later relief

- **WHEN** a constraint blocks a crank request and a subsequent input relieves
  the obstacle
- **THEN** the old request does not resume; a new request is needed to move
  the crank, and restoring/replaying the same history reproduces the result

#### Scenario: An added constraint stops one running-time admission

- **WHEN** a nested joint driven by running time reaches an ancestor
  constraint while another independent time drive remains free
- **THEN** only the pushing admission stops for that tick, global time and
  the independent drive continue, and later ticks retry without catch-up

#### Scenario: A clocked request consumes the same effective limit

- **WHEN** a clocked request reaches an ancestor constraint whose level is
  supported by the existing clocked bound solver
- **THEN** it admits only travel up to that limit and the final pose does
  not reject an already judged boundary through a second authority

### Requirement: Composed constraints preserve publication and replay identity

Compiled publication SHALL represent the intersection using the existing
qualified coordinate ids, span shape and expression vocabulary. Additional
constraints SHALL add no state, proxy coordinate, driver or control entry.
Equivalent effective limits SHALL execute through the existing consumer
contract without a new document version. Changing an effective constraint
SHALL change the compiled program identity and refuse an incompatible
snapshot. Models declaring no additional constraints SHALL keep their
previous program identities, published documents and stop behavior.

#### Scenario: Publication describes the real nested crank

- **WHEN** a running Curta diagnostic adds a constraint to its existing
  nested crank and publishes its compiled program
- **THEN** the span names that crank and the actual shaft read, and the
  assembly/control paths are unchanged with no new banked value

#### Scenario: An existing consumer reproduces the nested stop

- **WHEN** the installed viewer consumes the published nested diagnostic
  and receives the same crank request through its public control API
- **THEN** its committed travel and stop agree with Python under the
  existing tolerances and retain the same assembly tree

#### Scenario: An incompatible snapshot is refused

- **WHEN** a snapshot is restored into a model whose effective ancestor
  constraint differs
- **THEN** the program identity check refuses the restore without committing
  a partial bank

#### Scenario: Old models do not acquire a new format or cost path

- **WHEN** an existing model declares no ancestor constraints
- **THEN** its compiled spans, identity, document version and bytes remain
  unchanged and it executes through the existing uncontributed-range path

### Requirement: Moving engagement thresholds preserve valid running motion

A running mechanism whose engagement depends on both a driven part's retained
position and another moving part SHALL follow the relative engagement crossing,
including when the threshold overtakes the driven part. A valid request SHALL
not fail merely because that crossing direction differs from the driven part's
own displacement. The existing nearest-representable far-side, retained-state
and transactional-refusal requirements remain in force.

#### Scenario: A threshold overtakes a moving part
- **WHEN** a permitted request moves a part and its engagement threshold in
  the same direction but the threshold passes the part
- **THEN** engagement changes on the reached side of the threshold without an
  artificial stop, invented travel or landing error
- **AND** a later request and snapshot replay preserve the admitted state

#### Scenario: A restraint observes a free carry movement
- **WHEN** an ordinary crank turn moves a carry mechanism through its allowed
  engagement and a crank restraint reads that mechanism's retained position
- **THEN** the free turn completes with the same physical result as without
  that observer
- **AND** a subsequent genuinely obstructed request still stops at its first
  physical contact without automatic repositioning

#### Scenario: A genuinely invalid crossing remains transactional
- **WHEN** a requested motion has no valid engagement continuation or encounters
  a separately invalid relation
- **THEN** it is refused by the existing named failure behavior without partially
  committing the machine

#### Scenario: A part follows a moving contact
- **WHEN** a part and its contact move together with provably constant relative
  position on a continuous piece
- **THEN** rounding in point evaluations SHALL NOT invent an engagement crossing
  or cause an impossible-contact refusal
- **AND** genuine nonzero relative movement, however small, and genuine invalid
  continuation retain the existing crossing and transactional-refusal behavior

### Requirement: Source-timed execution is declared in exports and snapshots

Every newly exported running program SHALL use document version 11, including
ordinary, selected, Play and explicit-time programs. Existing fields and
expression syntax SHALL remain unchanged; posed/looping and clocked version
selection SHALL remain unchanged. A consumer supporting only versions through
10 SHALL refuse the corrected export before operation.

The running program's canonical identity SHALL include its source-timing
semantic generation. A snapshot from endpoint-era semantics SHALL refuse
restore before changing the bank, commands or records. This deliberately
supersedes earlier running identity and document-byte preservation promises
for this semantic correction, even for an affine program whose result is
unchanged. Corrected snapshots SHALL remain deterministic and replayable.

#### Scenario: Re-export protects the originating carry

- **WHEN** the unchanged Curta carry is exported by the corrected framework
- **THEN** the document is v11 and an old viewer refuses it rather than
  silently using the endpoint carry arithmetic

#### Scenario: Old arithmetic state is not restored silently

- **WHEN** an endpoint-era running snapshot is restored into the same machine
  compiled with source-timed semantics
- **THEN** the identity mismatch refuses before mutating any live state

#### Scenario: Other motion modes retain their format

- **WHEN** posed, looping and clocked models are exported by the corrected producer
- **THEN** their version selection remains unchanged
### Requirement: A selected control follows a supported joint override

A control inherited from a reusable body SHALL select the effective named
joint when a subclass or declaration site overrides that joint. Its axis,
origin, coordinate count and domain SHALL come from the effective declaration.
Selection SHALL retain its existing declaration-ownership, ancestry and input
reachability checks; matching a foreign joint's name SHALL NOT admit it.

#### Scenario: A site changes the rail direction
- **WHEN** a body with an inherited selected Slide is placed with a site
  override changing its prismatic joint's direction
- **THEN** its control constructs and publishes that effective rail direction

#### Scenario: A subclass changes a selected pivot
- **WHEN** a subclass overrides a selected revolute joint's axis or pivot
- **THEN** its inherited control constructs and uses the overridden placement

#### Scenario: An override is no longer a sliding coordinate
- **WHEN** a body carrying a selected Slide has that joint replaced by a
  revolute or multi-coordinate joint
- **THEN** the control is refused by name for the effective domain or
  coordinate count, without an attribute error or stale geometry

### Requirement: An unchanged standing constraint subgraph is not rebound on every running tick

For a sampled running constraint whose determined path is available, the run SHALL evaluate the bound at the same first point and every subsequent search point, in the same order and with the same operators and values as a complete expression walk. After one successful first-point evaluation, the run SHALL reuse the standing nodes of that bound on a later search only when the compiled graph and moving names are the same and every graph-referenced standing input has the same finite IEEE-754 value, including its sign bit. It SHALL evaluate moving nodes at the later search's first point and every required later point. If equality or safety cannot be proved, the original complete first-point evaluation SHALL occur. This reuse SHALL change no search fraction, crossing, stop, refusal, bank value, error order, document, or author declaration.

#### Scenario: Unchanged standing inputs on successive Curta crank ticks

- **WHEN** the Curta's crank constraint is searched on successive ordinary ticks while its bell turns and its other graph-referenced inputs stand at identical finite values
- **THEN** the standing portion is not numerically reevaluated at every first point, the moving portion is evaluated at the same first point and all fixed search points, and the complete coordinate bank and ordered constraint levels equal a full-bind run bit for bit

#### Scenario: A standing input changes or a branch shape changes

- **WHEN** a later search changes any graph-referenced standing input or its moving-name set
- **THEN** that search uses the complete first-point bind, preserves the first error and all later samples, and a successful bind may become the new bounded reuse entry

#### Scenario: Equality cannot establish safe numeric identity

- **WHEN** a referenced standing input is missing, nonnumeric, NaN, infinite, or differs only by the sign of zero
- **THEN** the run does not reuse the earlier standing values and observes the same value or first error as a complete bind

#### Scenario: A failed bind and a quiet or untraced search

- **WHEN** a first-point bind fails, a bound is inactive, or a determined path is unavailable and the existing prefix replay is required
- **THEN** no successful standing cache is inferred from the failure, the inactive bound remains unevaluated, and the prefix replay retains its existing evaluation and errors

#### Scenario: A restored or new run

- **WHEN** a simulation restores or resets a snapshot, or a new simulation owns the model
- **THEN** no standing value from the prior run state is trusted without a successful bind under the current run, and cache storage remains bounded by the run's compiled constraints

### Requirement: A path may reuse its immediately preceding successful identical bind

A running numeric path SHALL return its previous successful first-point value without repeating that numeric walk only when the *same path instance* receives bit-identical finite values for every graph-referenced input and its graph and moving-name set remain identical. It SHALL preserve the path's standing state and evaluate every later sample at its original point. Changed, missing, nonnumeric, custom, NaN, infinite or otherwise uncertain inputs SHALL take the complete eager bind with its original first error and operation order. A failed bind SHALL NOT seed or replace a successful entry. This reuse SHALL introduce no persistent cross-path or cross-run state and SHALL change no result, search point, crossing, stop, refusal, bank value, document or author declaration.

#### Scenario: A Curta path repeats the same first-point input

- **WHEN** one Curta crank path is rebound to the same finite input bits during the same ordinary tick
- **THEN** it returns its proven result without a second numeric walk, while all required later samples and the ordered Bound levels and full bank remain bit-identical to complete binds

#### Scenario: A source changes or returns to an earlier input

- **WHEN** the same path is rebound after any referenced input changes, including a change only in the sign of zero
- **THEN** it performs the complete eager bind and preserves the original value or first error; a later return to a previously successful input is reused only while that exact entry remains the last proven one

#### Scenario: An uncertain input or failed bind

- **WHEN** an input is missing, custom-converting or nonfinite, or a changed finite input produces an arithmetic or domain error
- **THEN** the original eager walk determines the value or earliest error, and an unsuccessful walk does not publish a new reusable result

#### Scenario: A new or restored path

- **WHEN** a new path instance is created, a run is reset or restored, or a different run owns the model
- **THEN** no prior path-instance bind result is trusted; each first successful bind establishes only that instance's bounded entry

### Requirement: Certified swept two-envelope following

A running Follow SHALL keep one banked scalar retained coordinate within the two matched authored envelopes by applying the ordered projection `max(lower, min(retained, upper))` through every certified affine piece and both numeric sides of each path join. It SHALL retain its exact landed value when a surface retreats and SHALL use the existing authored source and expression arithmetic without endpoint-only projection, changed timestep, changed uniform Bound sample count, or a new tolerance. It SHALL admit only affine source ancestry and piecewise-affine envelope paths; an unsupported or non-finite path SHALL refuse the entire tick atomically.

Only run inputs, held banked sources, and unbranched affine ordinary-law chains whose executor supplies exact linear source paths qualify as source ancestry. A wiring or formula endpoint chord SHALL NOT be substituted for its different point arithmetic.

#### Scenario: Push, release, and opposite surface
- **WHEN** a lower envelope rises past a free retained coordinate, later retreats, and an independently driven upper envelope moves inward
- **THEN** the lower pushes it out, retreat does not pull it back, and the upper pushes it inward from the retained position

#### Scenario: Interior peak survives a coarse tick
- **WHEN** a certified piecewise-affine lower envelope rises to a knot maximum and falls before a single requested tick ends
- **THEN** the retained coordinate holds the interior maximum instead of returning to the endpoint envelope value

#### Scenario: Uncertified motion refuses atomically
- **WHEN** a source path or an envelope piece is curved, unclassified, non-finite, domain-invalid, or outside the supported affine-source ancestry
- **THEN** the request refuses without changing the bank, tick, command admission, or snapshot

### Requirement: Matched Bounds stop incompatible Follow envelopes

When Follow envelopes become incompatible, its ordered projection SHALL expose a positive level to the matching dynamic Bound, and the run SHALL use the existing first-outward contact bracket, bisection tolerance, source-group attribution, absolute landing, and atomic commit rules. The Bound search SHALL retain every existing uniform probe and additionally inspect certified envelope piece boundaries and their representable cut sides. A positive one-sided closure without a representable positive probe SHALL refuse atomically instead of passing contact or inventing a stop.

#### Scenario: Curta raised carriage blocks after positive crank travel
- **WHEN** the collar holds the ball inward at 6 mm and the bell lower envelope rises through it during a coarse crank request
- **THEN** the crank stops at a positive admitted angle below one degree, the ball and sources remain within their Bounds, and lowering the carriage relieves the stop

#### Scenario: Sub-grid transient inversion
- **WHEN** two certified affine envelope paths become inverted and feasible again entirely between adjacent uniform Bound probes
- **THEN** the additional certified cut-side evidence finds the first representable outward contact and blocks the connected source rather than missing the interval

#### Scenario: Closure-only precision cannot be bracketed
- **WHEN** a one-sided affine piece closure is outside its matched Bound but the neighboring representable fractions do not expose a positive level
- **THEN** the tick refuses atomically as unsupported precision rather than waiving the violation

#### Scenario: Relief and replay are deterministic
- **WHEN** a Follow request is stopped, the run is snapshotted, restored, and the same request is replayed
- **THEN** the source admissions, stops, exact retained landing, and bank are reproduced; a later retreating or relieving request does not pull a free follower

### Requirement: Equivalent Follow Bound prefix probes may reuse a successful propagation

When running Bounds in one stretch require the same certified Follow-containing compiled prefix subprogram at the same finite IEEE-754 search fraction and fixed stretch inputs, the run SHALL be allowed to reuse the successful prefix result. Each Bound SHALL still evaluate its own expression and its original ordered search points, one-sided Follow cut evidence, crossing bracket, bisection and admission. A different subprogram, changed stretch, failed prefix or uncertain fraction SHALL use the original prefix replay. Reuse SHALL NOT change any value, earliest error, refusal, landing, stop, bank, replay, declaration or document.

#### Scenario: Paired bounds share an identical successful prefix
- **WHEN** two dynamic Bounds of a certified Follow target query the same compiled subprogram at the same finite fraction during one stretch
- **THEN** a successful prefix may be reused, while both Bounds independently evaluate their levels and produce their original bank and stop results

#### Scenario: Different fraction, subprogram, or stretch
- **WHEN** a Bound asks at a neighboring representable cut side, has a distinct compiled edge, or runs in a later tick or restored run
- **THEN** no stale prefix result is reused and the original fraction-specific propagation and Bound result are observed

#### Scenario: Prefix or Bound evaluation fails
- **WHEN** a prefix fails before completion or a Bound expression fails after a successful prefix
- **THEN** the same first error arises in the original search order; a failed prefix does not become reusable, and a successful prefix does not skip a later Bound's own evaluation

### Requirement: Equivalent running law folds share only successful tick-local structure

During one running tick, the simulator SHALL be allowed to reuse a successful immutable folded law graph only for the identical expression root and complete bit-identical finite built-in numeric substitution. The reuse SHALL be bounded and discarded at the tick boundary, including an unsuccessful tick. When identity or numeric safety cannot be established, the original fold SHALL determine the result or first error. Reuse SHALL change no expression arithmetic, sampled constraint value or order, stop, bank, refusal, snapshot, document, or author declaration.

#### Scenario: Curta repeatedly reaches the same Follow branch
- **WHEN** a Curta Follow tick folds the same root and substitution at repeated Bound probes
- **THEN** successful structure can be reused while its ordered Bound samples and final bank remain bit-identical to complete folding

#### Scenario: A distinct or uncertain substitution
- **WHEN** the root differs, any substitution differs including the sign of zero, or a value is custom, non-finite, or cannot be proved safe
- **THEN** the earlier fold is not reused and the original fold determines the value or first error

#### Scenario: Failure, eviction, and another tick or run
- **WHEN** folding fails, the bounded working set evicts an entry, a tick fails or completes, or another run begins
- **THEN** no unproven or prior-tick result is trusted and every required fold can be performed by the original path
