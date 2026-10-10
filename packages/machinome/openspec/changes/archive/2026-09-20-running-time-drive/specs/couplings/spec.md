## MODIFIED Requirements

### Requirement: A relation is stated by `drives` in a class body

The system SHALL provide `drives(other, ratio=None, offset=None,
law=None)` on every declaration that can name a coordinate — a child
declaration, a port declaration, a joint declaration, a `Driver`
declaration, a `State` declaration, a path reference and a derived
coordinate, and the root's running `Time` declaration as a source under
"A running clock is a read-only source of drives" — and SHALL require no
import to use it. `drives` SHALL be
framework vocabulary and the ONLY vocabulary for relating two coordinates:
the framework SHALL look up no method, attribute or hook of any name on a
project's node class to discover what a relation means.

A `State` declaration SHALL be admitted as a SOURCE of `drives` exactly as a
`Driver` is, and SHALL be refused as the DRIVEN end, at class definition,
naming the relation and the state.

`drives` SHALL be a STATEMENT: written bare in a class body, as
`power.drives(centre, law=going_train)`, it SHALL be recorded on the
class being defined, without being assigned to a name. Assigning its
result, `great = power.drives(centre)`, SHALL additionally name the
relation, so that a test can reach it and every message about it can
say its name; the same relation SHALL be recorded once, not twice. A
named relation read off the CLASS SHALL yield the declaration with its
two ends and its law as written; read off an INSTANCE it SHALL yield
that instance's record of the relation: its two resolved coordinates,
its law, and which direction it was solved in on the last run. A
relation that resolves to SEVERAL records — a broadcast over a repeated
child — SHALL read off an instance as the tuple of those records, in
copy order.

A relation SHALL be recorded even when it is written inside a class-body
comprehension, where the executing frame reports a copy of the
declaring namespace rather than the namespace itself.

A class's relations SHALL be enumerable off the class without
constructing an instance, base-first through the inheritance chain. A
relation written as a BARE STATEMENT has no name, and a subclass ADDS
such a relation to the relations of its bases rather than overriding
them, because a statement is not a name. A relation ASSIGNED to a name
is reachable by that name, and a subclass assigning a relation to a name
one of its bases already used SHALL REPLACE the base's: the subclass
SHALL enumerate the replacing relation and NOT the replaced one, and the
replacing relation SHALL keep the POSITION the base's held in the
enumeration, so the order of the solving pass does not shift under
inheritance — the rule a redeclared joint already obeys. The base SHALL
be unaffected: it SHALL still enumerate its own relation, and an
instance of the base SHALL still resolve, solve and record it. Reading
the name off the SUBCLASS SHALL yield the replacing declaration, and off
one of its instances that instance's record of the replacing relation;
the replaced relation SHALL never be resolved or recorded for an
instance of the subclass. A subclass names an inherited declaration
through the class that declares it — `Base.rotor.spin` — because the
base's declarations are not names of the subclass's own body, and the
framework SHALL add no other vocabulary for it.

`drives` called with no node class body executing SHALL be refused by
name, saying that a relation is class metadata. A class that carries
relations and is not an assembly SHALL be refused when the class is
created, naming the class, because only an assembly has the simulate
phase a relation is solved at the end of.

Relations declared on a class SHALL apply per instance of that class:
each realized instance SHALL resolve, solve and refuse its own,
independently of every other instance of that class.

#### Scenario: A bare statement is recorded on the class

- **WHEN** a class body contains `power.drives(centre, law=going_train)`
  with no assignment
- **THEN** the class carries that relation, enumerable off the class
  with its two ends and its law, and no instance was constructed

#### Scenario: A named relation is one relation

- **WHEN** a class body contains `great = power.drives(centre)`
- **THEN** the class carries exactly one relation, it is named `great`,
  reading `great` off the class yields the declaration, and reading it
  off a realized instance yields that instance's resolved record

#### Scenario: A subclass adds to its base's relations

- **WHEN** a class declaring two relations is subclassed by a class
  declaring a third
- **THEN** the subclass enumerates all three, base's first, and the
  base still enumerates its two

#### Scenario: A relation outside a class body is refused

- **WHEN** project code calls `drives` on a port declaration at module
  scope or inside a method
- **THEN** it raises by name, saying a relation is declared in a class
  body and is class metadata

#### Scenario: A relation on a leaf is refused

- **WHEN** a class body of a node that is not an assembly states a
  relation
- **THEN** class creation raises naming the class and saying that a
  relation is solved at the end of a simulate phase, which only an
  assembly has

#### Scenario: Every instance solves its own relations

- **WHEN** a class stating a relation is declared twice as two children
  of one parent, and the two are bound differently
- **THEN** each instance's relation resolves and solves against its own
  coordinates, and neither reads the other's values

#### Scenario: A subclass replaces a relation of its base by name

- **WHEN** a base declares `drive = input_angle.drives(rotor.spin,
  ratio=8.0)` and a subclass declares
  `drive = free_run.drives(Base.rotor.spin, ratio=1.0)`
- **THEN** the subclass enumerates ONE relation named `drive`, the
  replacing one, at the position the base's held; an instance of the
  subclass binds `rotor.spin` from `free_run` and nothing is refused as
  doubly bound; and the base still enumerates and solves its own

#### Scenario: A bare statement stays additive

- **WHEN** a base states two bare relations and a subclass states a
  third bare one and assigns a fourth to a name no base used
- **THEN** the subclass enumerates all four, the base's first, and
  nothing was replaced

#### Scenario: A state drives a coordinate

- **WHEN** a class body states `units.drives(dial.turn, law=digit_angle)`
  where `units` is a `State`
- **THEN** the relation is recorded and solves from the state's bound value,
  exactly as it would from a driver's

### Requirement: A grouped source commits states at an event

The system SHALL provide `commits(targets, at=, law=)` beside `drives`, on
every declaration that can name a coordinate and on the `&` group built from
them, requiring no import to use it, and SHALL be a STATEMENT recorded on the
class being defined exactly as `drives` is: bare, or assigned to a name that
reaches it and appears in every message about it. Read off the CLASS a named
committing relation SHALL yield the declaration with its sources, its targets
and its two factories as written; read off an INSTANCE it SHALL yield that
instance's resolved record. `commits` called with no node class body
executing SHALL be refused by name, and a class carrying one that is not an
assembly SHALL be refused when the class is created, by the rules `drives`
already obeys.

`targets` SHALL name one `State` or several, written as a tuple or with `&`,
in the order written. Every target SHALL be a `State`. A target that is not
one, and a target named TWICE among the targets of that relation, SHALL each
be refused at class definition, naming the relation as written and the
coordinate. The duplicate judgement SHALL be made on the target's PATH AS
WRITTEN — the path to the node that declares the state plus the local name —
and never on the local name alone: two children of one class each declare
their own state, so `a.digit` and `b.digit` are two targets and one relation
MAY name both.

A `State` a SECOND committing relation also targets SHALL NOT be refused,
neither at class definition nor at simulation construction: a value the
machine writes at two different events — a register digit written by the
stroke that adds to it and by the clearing reach that zeroes it — has two
writers and exactly one answer at each event. Two relations that would write
one state AT ONE EVENT are refused as the request's own conflict, by the
simulation capability, and nothing about that judgement belongs to a class
body, which cannot see a landing.

Every source SHALL be a `Driver`, a `State`, or the root's own `Time`
declaration when that declaration is the ELAPSED base; the same `&` group
grammar
applies, flat and left-associative, with the same missing-parentheses
refusal. A port, joint coordinate or derived coordinate named as a source
SHALL be refused at class definition, by name, saying to name the drivers and
states the port follows. A source group MAY name a target of the same
relation: that is a READ of that target's value, and it SHALL be handed to
both factories in the position the group writes it.

The CLOCK named as a source SHALL be the declaration the class body holds
under the name `time`, SHALL enter the `&` group and both factories exactly
as a driver does — one positional argument in written order, carrying the
banked seconds — and SHALL be addressed by the bare qualified id `time`. It
SHALL be refused at class definition, by name and naming `Time.elapsed()`,
when the declaration it names is `Time(loop=...)` or `Time.running()`,
because an event is located on a clock that never wraps. The clock SHALL be
refused as a TARGET of `commits` and as the driven end of `drives`, at class
definition, by name: no relation writes the clock. An ELAPSED or LOOPING
clock SHALL also be refused as a source of `drives`; only the RUNNING
clock is admitted there, under "A running clock is a read-only source of
drives". The elapsed clock remains moved by requests and written by nothing.

A class body that declares NO time base has no `time` name of the system's
to refuse — a class body does not read a base class's attributes — so the
system SHALL NOT claim a refusal it cannot raise there, and SHALL instead
make the `&` group's refusals SYMMETRIC. A LEFT operand of `&` that is not a
coordinate SHALL be refused by name exactly as a right operand already is,
naming the operand and saying a group is a group of coordinates; where that
operand is a MODULE the message SHALL add that the machine's clock is named
only through the root's own `time = Time.elapsed()` declaration and that a
body declaring no base has no clock to name. That refusal SHALL be reached
only where the left operand carries no `&` of its own, so every group the
system admits today SHALL be admitted unchanged. A body that binds no `time`
at all SHALL raise Python's own `NameError` before any declaration is
reached, and the system SHALL promise no message of its own there.

`at` and `law` SHALL both be required and SHALL both follow the law-factory
protocol this capability already states: a callable of two arguments, called
exactly ONCE at realization with the realized owners — one owner for a side
naming one coordinate, the tuple of owners in written order for a side naming
several — returning a callable over the sources' values, one positional
argument per source in written order. Neither SHALL receive an event object,
a runtime handle, or any mutable per-tick state, and a committing relation
SHALL add no second face to a law. `ratio=` and `offset=` SHALL be refused
with `commits`, a committing relation having no affine default; a `.repeat()`
broadcast on either side SHALL be refused by name.

Both factories SHALL read and write NATIVE values: a commit law receives its
sources as the state bank holds them and returns values in the same units,
and a returned value SHALL NOT be passed through the design-unit conversion
a driver applies to a move target. A target declaring `dtype=int` SHALL take
the nearest whole native unit, rounded once at the commit; a target declaring
a `scale` SHALL take the returned value unrescaled.

`targets` MAY name a state through a PATH to the node that declares it,
`carriage.result.units.digit`, exactly as a source may — a state belongs to
the part that holds the value, and the relation belongs to the assembly that
can see both ends.

A `State` SHALL be refused as the driven end of `drives`, at class
definition, naming the relation and the state: a state is written by its
committing relation and by nothing else. A `State` MAY be a SOURCE of
`drives`, exactly as a `Driver` may, which is how the pose is fed from the
state.

#### Scenario: A bare commits is recorded on the class

- **WHEN** a class body contains
  `(crank & units & tens).commits((units, tens), at=strokes, law=advance)`
  with no assignment
- **THEN** the class carries that committing relation, enumerable off the
  class with its sources, its targets and its two factories, and no instance
  was constructed

#### Scenario: A named committing relation resolves per instance

- **WHEN** a class body contains
  `stroke = (crank & result).commits(result, at=strokes, law=registers)` and
  two instances of that class are realized
- **THEN** reading `stroke` off the class yields the declaration, reading it
  off each instance yields that instance's own record, and each factory was
  called once per instance with that instance's realized owners

#### Scenario: A target is named through a path

- **WHEN** a root's class body states
  `(ring & dial.digit).commits(dial.digit, at=reach, law=clear)`, where
  `digit` is a `State` declared on the `dial` CHILD and not on the root
- **THEN** the relation is recorded on the root, both factories are handed
  the realized `dial`'s own `digit` owner, the state enumerates as
  `dial.digit`, and committing it writes that child's value

#### Scenario: A source group may name its own target

- **WHEN** a committing relation is written
  `(ring & digit).commits(digit, at=reach, law=clear)`
- **THEN** it is admitted, and both factories are handed the digit's owner in
  the position the group writes it

#### Scenario: Two relations may target one state

- **WHEN** one class body states two committing relations both naming
  `units` among their targets, on two different event levels
- **THEN** the class is created carrying both, and each resolves on an
  instance with its own two factories called once

#### Scenario: One relation naming one target twice is refused

- **WHEN** a class body states `.commits((a.digit, a.digit), at=..., law=...)`
- **THEN** class definition fails printing the path `a.digit` and saying a
  target is named once

#### Scenario: Two children of one class are two targets

- **WHEN** a class body states
  `(crank & a.digit & b.digit).commits((a.digit, b.digit), at=..., law=...)`
  where `a` and `b` are two children of ONE class declaring `digit`
- **THEN** the relation is recorded with two targets, and committing it
  writes each child's own value

#### Scenario: A state as a driven end is refused

- **WHEN** a class body states `crank.drives(units)` where `units` is a
  `State`
- **THEN** class definition fails naming the relation and the state, and says
  a state is written by its committing relation

#### Scenario: A ratio with commits is refused

- **WHEN** a class body states `.commits(units, ratio=2.0)`
- **THEN** class definition fails naming the relation, saying a committing
  relation has no affine default and requires `at` and `law`

#### Scenario: A broadcast commits is refused

- **WHEN** a committing relation names a path through a `.repeat()`ed child
  on either side
- **THEN** class definition fails by name

#### Scenario: The clock is a source beside a driver and a state

- **WHEN** a root declaring `time = Time.elapsed()` states
  `(time & engaged & count).commits(count, at=release, law=advance)`
- **THEN** the class carries that committing relation with three sources in
  written order, both factories are called once at realization, and each
  returned callable receives the seconds first, the driver's value second
  and the state's value third

#### Scenario: The clock as a source under another base is refused

- **WHEN** a class body declares `time = Time(loop=4)` or
  `time = Time.running()` and names `time` among a committing relation's
  sources
- **THEN** class definition fails naming the relation, the base it declared
  and `Time.elapsed()`

#### Scenario: A body that declares no base names the module, and the group refuses it

- **WHEN** a module that imported the stdlib `time` contains a class body
  declaring no time base and writing `time & engaged` among a committing
  relation's sources
- **THEN** class definition fails naming the operand, saying a group is a
  group of coordinates, and saying the machine's clock is named only through
  the root's own `time = Time.elapsed()` declaration

#### Scenario: A body that binds no time at all gets Python's own answer

- **WHEN** a class body declaring no time base names `time` in a group and
  nothing in the module or the builtins binds that name
- **THEN** `NameError` is raised before any declaration of the framework is
  reached, and no framework refusal is claimed for that case

#### Scenario: A group of coordinates is admitted unchanged

- **WHEN** any group the system admits today is written, its left operand
  being a coordinate, a declaration or a group
- **THEN** it is built exactly as it is built today, the left operand's own
  `&` answering, and the left-operand refusal is never reached

#### Scenario: The clock is not a target and not a driven end

- **WHEN** a class body states `.commits(time, at=..., law=...)` or
  `x.drives(time)` under any time base, or `time.drives(x)` under an elapsed
  or looping time base
- **THEN** each fails at class definition naming the relation and clock;
  the target refusals say no relation writes the clock and the source
  refusal names `Time.running()` as the base supporting a time drive

## ADDED Requirements

### Requirement: A running clock is a read-only source of drives

The system SHALL admit the root's declared `time = Time.running()` as a
SOURCE of `drives`, alone or among a grouped source's declarations. The
existing affine and law-factory forms SHALL apply without a new declaration
type or callback. Factories SHALL receive the realized owner of the time
declaration in its written position, exactly once per realization, and their
returned laws SHALL receive elapsed seconds in that position.

The declaration SHALL refer to the running root's own clock. A foreign or
mismatched declaration SHALL be refused by relation identity where the owner
is known; a child clock SHALL NOT create another clock or control under a
running parent. Time SHALL never be a driven end or a commandable driver.
A running-clock relation SHALL NOT solve backward into its time source.

Ordinary numeric and untimed inspection SHALL retain the existing reading
of time and relation posing. Under a running simulation the run SHALL seed
the ordinary rest at zero seconds and own the retained joints thereafter,
under the simulation capability. Merely reading, rendering or publishing
the tree SHALL NOT advance any retained coordinate.

#### Scenario: An affine time drive needs no dummy input

- **WHEN** a running root states `time.drives(shaft.turn, ratio=6)`
- **THEN** the relation is admitted without declaring an operator driver,
  and its source is the root's elapsed seconds

#### Scenario: A time source keeps its written group position

- **WHEN** a running root states
  `(enabled & time & shaft.turn).drives(shaft.turn, law=gate)`
- **THEN** the factory receives owners and the returned law receives values
  in the order enabled, elapsed seconds, retained shaft angle

#### Scenario: A foreign time declaration cannot drive this run

- **WHEN** a relation names a different root's Time declaration as its source
- **THEN** realization refuses it naming the relation and the owning-root
  mismatch, without creating a second clock or drive

#### Scenario: Reading time does not grant a second joint writer

- **WHEN** a running simulation's `simulate()` assigns `self.time` directly
  to a run-owned joint
- **THEN** the existing double-binding refusal remains, while rotating a
  plain part by `self.time` remains an admitted absolute pose expression

#### Scenario: Time is not an operating input

- **WHEN** a maker attempts a running `move("time", ...)` or
  `rate("time", ...)`
- **THEN** the existing non-driver refusal applies; the time source appears
  in no driver controls and creates no command handle
