## MODIFIED Requirements

### Requirement: Each end of a relation resolves to a coordinate, or to one per copy of a repeated child

The system SHALL resolve each end of a relation to a coordinate, or to
SEVERAL where the end names several — the driven end to one coordinate
PER REALIZED COPY, per named coordinate, when it passes through a
repeated child, which makes the relation a BROADCAST. The
kinds of end SHALL be:

- a PORT or JOINT declared on the class stating the relation, resolving
  to that instance's own coordinate;
- a CHILD DECLARATION, resolving to the realized child's ONE joint's
  coordinate;
- a PATH REFERENCE — `anchor.turn`, `motion_works.cannon.turn`,
  `shoulder.art2.art3.wrist` — resolving to the coordinate of the
  realized descendant the path names;
- a BROADCAST — a path one of whose segments is a REPEATED child
  declaration, `eccentric_bearings.orbit`, `column.beads.travel`,
  `legs.femur.lift` — resolving to ONE coordinate PER REALIZED COPY,
  and permitted as the DRIVEN end only, or in the source group of the
  relation that drives that same broadcast, where it is each copy's read
  of itself;
- a `Driver` declaration, resolving to the driver's value, which SHALL
  be a SOURCE only;
- a DERIVED COORDINATE of the class;
- SEVERAL of the above, written as one end.

An end MAY name SEVERAL coordinates. On the DRIVEN side they SHALL be
written as a tuple — `a.drives((b, c, d), law=...)`. On either side
they MAY be written with `&` — `(x & y & z).drives(...)` — which the
system SHALL provide on every declaration that carries `drives`, and
which SHALL group left-associatively, so three coordinates are one group
of three and not a nested pair. The SOURCE side SHALL accept only that
spelling, because a tuple written there is a tuple display and the
system cannot give it a verb. `&` applied to anything that is not a
coordinate SHALL be refused by name, and `&` applied to a RELATION SHALL
say that the parentheses are missing, because `a & b.drives(c)` states a
one-source relation before the grouping is read.

Every member of a group SHALL be an end of one of the kinds above and
SHALL be checked as one, in its own role: a repeated child named as a
SOURCE — other than the broadcast the same relation drives — a `Driver`
named as a DRIVEN end, a node whose class declares
several joints, and a path stopping on a joint that owns several
coordinates SHALL each be refused inside a group exactly as outside it.
Ends are coordinates, named ONE BY ONE. A group SHALL name at least TWO
coordinates — an empty group and a group of one SHALL be refused,
saying that one end is written without the group — and a group SHALL
NOT hold another group. A coordinate SHALL be named ONCE in a group; a
coordinate named on BOTH sides of a relation whose ends name several
coordinates SHALL be a READ of that driven end rather than a refusal,
under the requirement "A relation may name several coordinates at each
end". A group SHALL NOT be a term of a derived coordinate.

Where a DRIVEN group names a BROADCAST, every member of that group SHALL
be a broadcast over the SAME repeated segment of the same path, so the
relation resolves to one record per copy holding that copy's several
driven ends. A driven group mixing a broadcast with an end that is not
one, or naming two different repeated segments, SHALL be refused at
class definition naming both paths.

A PATH REFERENCE SHALL be read segment by segment, and a COORDINATE at
its end SHALL occupy as many TRAILING SEGMENTS as the name the port
enumerator reports it under has dot-separated parts: one for a plain port
or the coordinate of a joint that owns one, and two for a coordinate of a
joint that owns several — `chassis.pose.roll` names the realized child
`chassis` and its coordinate `pose.roll`. Every segment before those
SHALL be a child the previous segment's class declares, as it is today.

A path MAY pass through AT MOST ONE repeated child declaration, at any
position, and a path that does SHALL be a BROADCAST: it names the same
coordinate of every copy that repeat realized, in copy order. A repeated
declaration named as an end without a further segment SHALL mean the ONE
joint of the repeated class, by the same rule a child declaration does.
A path through TWO repeated declarations SHALL be refused at class
definition, naming both repeated segments and saying that a broadcast
fans out over one repeat. A path through a LIST-HELD child SHALL stay
refused as it is today, naming the list and saying that its children are
named one by one.

A BROADCAST SHALL be refused at class definition when it is named as the
SOURCE end, naming the path as written, the repeated declaration and its
class, and saying that a relation's source is one value while the copies
hold one each — with ONE exception: the very broadcast the same relation
DRIVES, which is not a second value but each copy's READ of itself, and
which SHALL resolve per copy exactly as the driven end does, under the
requirement "A relation may name several coordinates at each end". A
BROADCAST SHALL likewise be refused as a term of a derived coordinate,
naming the formula and the path.

A path that STOPS on a joint owning several coordinates — `chassis.pose`
— SHALL be refused at class definition naming the joint and listing its
coordinates, with the advice to name one, because a relation has one end.
A path naming a part that such a joint does not own — `chassis.pose.twist`
— SHALL be refused the same way, listing what it does own.

A child declaration named as an end SHALL mean the one joint of that
child's class. A child whose class declares NO joint, or more than one,
SHALL be refused at class definition, naming the child attribute, its
class, and the joints that class declares, with the advice to name the
coordinate. A child whose class declares exactly one joint, that joint
owning several coordinates, SHALL be refused the same way, listing that
joint's coordinates.

A relation SHALL bind either end through the SAME path an author's
assignment takes, whatever the coordinate's name is: a coordinate whose
name has more than one segment SHALL be bound through the joint that owns
it, and never by setting an attribute of that name on the node.

A `Driver` named as the DRIVEN end SHALL be refused at class
definition, naming the driver, because a driver's value belongs to the
bound snapshot and is set by `set_state`.

The ends SHALL resolve at realization, at the end of the instance's
construction and after its children are realized, since an end may be a
child or a descendant of one. Whatever the classes alone decide SHALL
be refused AT CLASS DEFINITION — an attribute no class along a path
declares, a node end with the wrong number of joints, a driver as a
driven end, a path through a list-held child, a broadcast named as the
source end of a relation that does not drive that same broadcast, a path
through two repeated children, `ratio=` or
`offset=` given together with `law=`, and every refusal a GROUP carries:
a group of fewer than two coordinates, a group inside a group, a
coordinate named twice in ONE group, a
driven group mixing a broadcast with an end that is not one or naming
two different repeated segments, a driven group one of whose members the
source group also names, a group with `ratio=`/`offset=` or with
no `law=`, `&` over something that is not a coordinate, and `&` over a
relation — and whatever depends on the
instance SHALL be refused AT REALIZATION, naming the relation, the path
as written, the node the walk stopped at and what that node declares.

#### Scenario: Several driven ends are one relation

- **WHEN** a class states
  `(stage.slide_x & stage.slide_y).drives((leg.lean, leg.tilt), law=leg_lean)`
- **THEN** the relation has two source ends and two driven ends in the
  order written, and one record holds all four

#### Scenario: Several driven ends over a repeat are one record per copy

- **WHEN** a class declaring `rods = Rod().repeat(6)` states
  `(x & y & z).drives((rods.spin, rods.lean, rods.swing, rods.rise), law=delta_rod)`
- **THEN** six records are solved, one per copy, each holding that
  copy's four driven ends; the law was called six times, once per copy;
  and reading the named relation off the instance yields six records in
  copy order

#### Scenario: A repeated source inside a group is refused

- **WHEN** a class states `(beads.travel & earth).drives(x, law=...)`
- **THEN** class definition raises with the repeated-source refusal,
  naming the path as written, the repeated declaration and its class

#### Scenario: A driven group over two different repeats is refused

- **WHEN** a class states
  `x.drives((left.beads.travel, right.beads.travel), law=...)`, or
  `x.drives((beads.travel, lid.turn), law=...)`
- **THEN** class definition raises naming both driven paths and saying
  that the driven ends of one relation fan out over one repeat together

#### Scenario: A group of one, and a group of a group, are refused

- **WHEN** a class states `x.drives((a,), law=...)`, `x.drives((), law=...)`
  or `x.drives(((a, b), c), law=...)`
- **THEN** class definition raises naming the relation, saying that a
  group names two coordinates or more and that ends are named one by one

#### Scenario: The parentheses are missing

- **WHEN** a class body writes `count & next_count.drives(pawl.swing, law=...)`
- **THEN** class definition raises naming the relation the inner call
  stated and saying that the parentheses are missing

#### Scenario: A node end is its one joint

- **WHEN** an assembly declares `power = TrainArbor(index=0)` and
  `centre = TrainArbor(index=1)`, `TrainArbor` declaring exactly one
  `Revolute` named `turn`, and states `power.drives(centre)`
- **THEN** the relation's ends are the two realized arbors' `turn`
  coordinates, and binding one places the other

#### Scenario: A node with two joints is refused

- **WHEN** a class body states `wrist.drives(tool)` where `tool`'s class
  declares two joints, or none
- **THEN** class definition raises naming the child attribute, its
  class and the joints it declares, with the advice to name the
  coordinate

#### Scenario: A path reaches a descendant's coordinate

- **WHEN** a root states `art3.drives(shoulder.art2.art3.wrist)`, three
  levels of declared children below it
- **THEN** the relation's driven end is the realized wrist coordinate
  of that descendant, and no intermediate class declared or forwarded a
  port for it

#### Scenario: A driver may not be driven

- **WHEN** a class body states `centre.turn.drives(some_driver)`
- **THEN** class definition raises naming the driver and saying its
  value belongs to the bound snapshot

#### Scenario: A path through a repeated child is refused

- **WHEN** a class declaring `units = Unit().repeat(count)` states
  `units.turn.drives(power)`, naming the repeated child as the SOURCE
- **THEN** class definition raises naming the path as written, the
  repeated declaration and its class, and saying that a relation's source
  is one value while the copies hold one each

#### Scenario: A repeated driven end is one relation per copy

- **WHEN** a class declaring `beads = Bead().repeat(4)` and a coordinate
  `earth` states `earth.drives(beads.travel)`, and `earth` is bound
- **THEN** four relations are solved, one per realized copy, each copy's
  `travel` holds the value and each copy's body is placed by it

#### Scenario: A repeated node end is the copies' one joint

- **WHEN** the same class states `earth.drives(beads)`, `Bead` declaring
  exactly one joint
- **THEN** the relation's driven ends are the four realized copies'
  coordinates, exactly as if the joint had been named

#### Scenario: A repeat one level down is one fan-out

- **WHEN** a root declaring `column = Column()`, `Column` declaring
  `beads = Bead().repeat(4)`, states `drive.drives(column.beads.travel)`
- **THEN** class definition succeeds and four relations are solved, one
  per copy of that realized column

#### Scenario: Two repeated segments in one path are refused

- **WHEN** a class states `yaw.drives(legs.joints.spin)`, where `legs`
  and `joints` are both repeated declarations
- **THEN** class definition raises naming both repeated segments and
  saying that a broadcast fans out over one repeat

#### Scenario: A list-held child is still refused

- **WHEN** a class states `power.drives(plates)`, or
  `power.drives(frame.plates.turn)` reaching a list-held declaration one
  level down
- **THEN** class definition raises naming the list-held declaration and
  saying its children carry their own arguments and are named one by
  one, and the message is not the two-repeat one

#### Scenario: A path that does not resolve on the instance fails at realization

- **WHEN** a path names a child of a class realized through an ordinary
  constructor that does not produce it
- **THEN** realization raises naming the relation, the path as written,
  the node the walk stopped at and what that node declares

#### Scenario: A path reaches one coordinate of a multi-coordinate joint

- **WHEN** a root declaring `chassis = Chassis()`, `Chassis` declaring
  `pose = Free()`, states `tilt.drives(chassis.pose.pitch)`
- **THEN** the relation's driven end is that realized chassis's
  `pose.pitch` coordinate, binding it places the chassis, and the other
  five coordinates are untouched

#### Scenario: A path stopping on a multi-coordinate joint is refused

- **WHEN** a class body states `tilt.drives(chassis.pose)`, or
  `tilt.drives(chassis.pose.twist)`
- **THEN** class definition raises naming the joint and listing the
  coordinates it owns, with the advice to name one of them

### Requirement: A relation may name several coordinates at each end

A mechanism may read several coordinates and move several. The system
SHALL let ONE relation name several coordinates as its source, several
as its driven end, or both, and SHALL hand the whole of it to the
project's own law, which reads all the sources and returns all the
driven values in one call.

The system SHALL apply such a relation in ONE DIRECTION only: it SHALL
be applied when every source end is bound, binding every driven end
together, and SHALL NEVER be read backwards, whatever inverse its law
offers — for the reason a broadcast is never read backwards, that
recovering the sources from the driven values would mean comparing or
solving values, which the framework does not do. Asked to, the system
SHALL refuse by name.

A relation naming several coordinates at either end SHALL resolve to ONE
RECORD holding all its ends, in the order written — and, where its
driven end is a broadcast, to one such record PER REALIZED COPY, each
holding that copy's driven ends. The driven ends of one record SHALL be
bound by ONE application of one law, and SHALL NOT be bound, refused or
deferred one without the others; the system SHALL claim every one of
them before it binds any.

Such a relation SHALL take part in the solve exactly as any other does:
attempted at the end of its own instance's simulate phase, DEFERRED
while any source is unbound, applied as soon as the whole tree's
propagation binds the last of them, and refused only when nothing
changes any more. Its motion SHALL be the motion of the assembly that
stated it, tagged, swept and cleared with the rest of that assembly's
motion.

Values SHALL pass through it unresolved, exactly as through any other
relation: a law over several symbolic sources publishes several
expressions, one per driven end, and the operations they lower to are
those the same bindings written by hand would produce.

A coordinate named BOTH as a source and as a driven end of ONE such
relation SHALL be a READ of that driven end: the law SHALL be handed its
owner exactly as it is handed any source's owner, in the position the
source group writes it, and what the law reads there SHALL be the value
the coordinate HOLDS and never a value that same application is about to
give it. Such a relation SHALL be recognized only where an end names
SEVERAL coordinates, SHALL be applied FORWARD only like any other
relation of several ends, and SHALL be integrated under the simulation
requirement "A law may read the coordinate it drives", which is the only
reading that gives it a meaning.

Such a relation SHALL drive exactly ONE coordinate. A relation whose
driven end is a GROUP and whose source group names any member of that
group SHALL be REFUSED at class definition, naming the relation and the
coordinate, and saying that a relation reading its own driven end drives
one coordinate — whether that member reads ITSELF or a SIBLING driven end
of the same group. Where the driven end is a BROADCAST the relation still
drives one coordinate per copy, and the source group's repeated member —
the same broadcast — SHALL resolve per copy exactly as the driven end
does, so each copy reads ITSELF and each copy is its own record. A
coordinate named twice within ONE group SHALL stay refused, and a read of
a coordinate some OTHER relation drives SHALL stay the ordinary source it
has always been.

Under a root that does NOT declare `Time.running()` such a relation SHALL
be REFUSED by name at the close of the enumeration, naming the relation
and the class that stated it and saying that a relation reading its own
driven end states increments, which only a run integrates — rather than
standing silently inert over a coordinate nothing moves.

#### Scenario: A pawl deflects from two drums

- **WHEN** a position states
  `(count & next_count).drives(sautoir.pawl.swing, law=pawl_deflection)`
  and both ports are bound
- **THEN** the law was handed the tuple of the two sources' owners and
  the pawl's node, its `forward` was called with the two values in the
  order written, and the pawl's swing holds the one value it returned

#### Scenario: Three sources and four driven ends on every copy

- **WHEN** a delta printer declaring `rods = Rod().repeat(6)` states
  `(x & y & z).drives((rods.spin, rods.lean, rods.swing, rods.rise), law=delta_rod)`
  and binds its three drivers
- **THEN** each of the six rods holds its own four values, each copy's
  law was called once at realization with that copy, and each rod's body
  is placed by the four bindings exactly as if they had been written by
  hand

#### Scenario: Several sources and one driven end

- **WHEN** the same printer states
  `(x & y & z).drives(towers.height, law=delta_carriage)` over three
  repeated towers
- **THEN** each tower's height holds the value its own law returned, and
  the law returned that value rather than a sequence

#### Scenario: A relation of several ends is not applied while a source is unbound

- **WHEN** a relation of three sources has only two of them bound when
  its own instance's relations are attempted, and nothing else in the
  tree binds the third
- **THEN** nothing was bound by it, and the enumeration refuses naming
  the relation and the unbound source

#### Scenario: The driven ends of one law are bound together

- **WHEN** a relation of four driven ends is applied and one of those
  coordinates was already bound by the author's `simulate()`
- **THEN** the doubly-bound refusal names that coordinate and its two
  binders, and none of the other three was bound


#### Scenario: A coordinate named on both sides is read, not refused

- **WHEN** a class states
  `(rack & wheel.turn).drives(wheel.turn, law=missing_tooth)` on a root
  declaring `Time.running()`
- **THEN** class definition succeeds, the law is called with the rack's
  owner and the wheel's owner in that order, and the relation's one
  record names `wheel.turn` as both a source and its driven end

#### Scenario: A driven group with a self-read is refused

- **WHEN** a class states
  `(crank & lever.swing & pawl.turn).drives((lever.swing, pawl.turn), law=hysteresis)`
- **THEN** class definition raises naming the relation and the coordinate
  read, and saying that a relation reading its own driven end drives one
  coordinate

#### Scenario: Each copy of a broadcast reads itself

- **WHEN** a class declaring `wheels = Wheel().repeat(6)` states
  `(ring & wheels.turn).drives(wheels.turn, law=missing_tooth)`
- **THEN** class definition succeeds although the source group names a
  broadcast, six records are solved, one per copy, and each copy's law
  read that copy's OWN turn rather than the first copy's

#### Scenario: A coordinate named twice in one group is still refused

- **WHEN** a class states
  `(rack & wheel.turn & wheel.turn).drives(wheel.turn, law=...)`
- **THEN** class definition raises naming the relation and the
  coordinate, because one value would take two positions of the law

#### Scenario: A self-read relation under no running root is refused

- **WHEN** a root declaring no time base, or `Time(loop=4)`, states
  `(rack & wheel.turn).drives(wheel.turn, law=missing_tooth)` and the
  tree is rendered
- **THEN** the enumeration refuses at its close naming the relation and
  the class that stated it, and says that a relation reading its own
  driven end states increments, which only a run integrates, and to
  declare `time = Time.running()`
