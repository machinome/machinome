## MODIFIED Requirements

### Requirement: Joint declarations

The system SHALL provide the one-coordinate lower pairs as declarations
exported from `machinome.motion.joints`: `Revolute(axis=None,
at=(0, 0, 0), range=None, unit='deg')`, which turns a body about a line;
`Prismatic(axis, at=(0, 0, 0), range=None, unit='mm')`, which slides a
body along one; and `Orbit(axis, at=(0, 0, 0), carries=(0, 0, 0),
range=None, unit='deg')`, which carries a point of a body round one while
the body's attitude stays fixed. A joint SHALL be declared in either of two
places: as a CLASS ATTRIBUTE of the node it moves — an assembly or a leaf
— or at a DECLARATION SITE, passed as a keyword where a parent declares
that node as a child, see "A joint declared where a child is placed". A
`Revolute` SHALL additionally be accepted as the FREEDOM of a mate, where
its `axis` and its `at` MAY each be left out, the moving frame's `z` and
origin then supplying what was left out, as the `mates` capability
specifies; the joint the mate then gives the moving child is a joint of
that child's class like any other. In
every case it SHALL be stateless declaration metadata shared by every
node the declaration realizes, exactly as a port declaration is; a site
declaration is shared by every child that site realizes, including every
copy of a `.repeat()`.

`axis` SHALL be a direction of three components and `at` an anchor point
of three components, both stated in the frame of the body the joint is
declared on; see "A joint is stated in the frame of whoever declares it".
`axis` SHALL have no named constants; it is written as a tuple.
`Revolute`'s `axis` MAY be omitted when the declaration is constructed,
and a `Revolute` without an axis SHALL be refused at class definition
wherever it is declared except as a mate's freedom — as a class
attribute, at a declaration site, or held by anything else — naming the
class, the joint and the mate as the only place an axis may be left out.
Every other joint kind's `axis`, where it has one, SHALL remain
required. A joint of such a kind written with `axis=None` — as a class
attribute, at a declaration site, or as a mate's freedom — SHALL be
refused at class definition, naming where it was written (the class and
the joint; at a declaration site the declaring class, the joint and the
child's class; as a mate's freedom the assembly that states the mate and
the mate), naming its KIND, and saying that kind's axis is required
everywhere — for a `Prismatic`, a mate's freedom included; the refusal
SHALL NOT call it a `Revolute` nor say that a moving frame supplies its
axis. `at`
SHALL default to that body's OWN origin, which is the case of a joint
whose line passes through the origin of the body it moves. `range` SHALL
be a `(lo, hi)` pair in `unit`, and `unit` SHALL be the label the
coordinate carries. An `Orbit`'s `axis` and `at` SHALL mean exactly what
a `Revolute`'s mean — a direction and a point ON the line — and its
`carries` SHALL be the point of the body that travels round that line,
stated in the same frame; see "An orbit's radius and phase are derived,
never declared".

A `Prismatic`'s `at` SHALL NOT affect its placement — a translation along
a line is the same wherever the line is taken to pass — and SHALL be
carried as the declared position of the slide, for a reader and for a
later exporter.

A class's joints SHALL be enumerable off the class by name, without
constructing an instance, by an enumerator exported beside the joint
kinds. A joint a DECLARATION SITE passed SHALL be reported by that same
enumerator for the class the site's children are realized as, in the
position "Binding a joint places the body" gives it, so one enumerator
answers for both declaration sites and no consumer needs to know which
site a freedom came from. That enumeration SHALL be ORDERED, and its order SHALL be the
class's DECLARATION order: the joints of each base class before those of
the class itself, following the class's method resolution order from the
most basic class outward; within one class body, the order the joints
were written in; and a joint that REDECLARES an inherited one SHALL keep
the position of the declaration it redeclares while taking its own
arguments. That order is the order the joints compose in — see "Binding a
joint places the body" — so a reader of a class body, or a consumer
reading the class alone, can see how its freedoms stack without running
anything.

A joint declaration SHALL NOT be reported by that enumerator as a
parameter, a driver or a child, and a name SHALL NOT be declared as both
a joint and a port on one class: such a class SHALL be refused at class
definition naming the name and both declarations.

#### Scenario: A joint is declared where the body is

- **WHEN** a forearm class declares
  `elbow = Revolute(axis=(0, 1, 0), at=(0, 0, 81.5), range=(-135, 135), unit='deg')`
- **THEN** the class carries that joint by name with its axis, anchor,
  range and unit readable off the class, no instance was constructed,
  and the axis and anchor are understood in the forearm's own frame

#### Scenario: An orbit is declared where the carried body is

- **WHEN** a connecting rod class declares
  `orbit = Orbit(axis=(1, 0, 0), carries=(0, 0, 15), unit='deg')`
- **THEN** the class carries that joint by name with its axis, its
  anchor at its own frame's origin, its carried point, its unit and no
  radius or phase readable off the class, and no instance was constructed

#### Scenario: Joints are enumerable

- **WHEN** a consumer enumerates the joints of a class declaring one
  `Revolute` and one `Prismatic`, and of a subclass that redeclares the
  `Revolute` with a different range
- **THEN** it receives both joints of the base class by name, and the
  subclass's redeclaration for the name it redeclares

#### Scenario: The enumeration is in declaration order

- **WHEN** a base class declares `a` then `b`, and a subclass declares
  `c` and redeclares `a` with a different anchor
- **THEN** the enumeration reads `a`, `b`, `c` — base before subclass,
  written order within a class body, and the redeclared `a` in the
  position the base gave it, carrying the subclass's anchor

#### Scenario: A joint and a port cannot share a name

- **WHEN** a class body declares `turn = Revolute(axis=(0, 0, 1))` and
  `turn = RotationalPort(unit='deg')`
- **THEN** class definition raises naming the class, the name and both
  declarations

#### Scenario: One enumerator answers for both declaration sites

- **WHEN** a consumer enumerates the joints of a class declaring `spin`,
  and then the joints of the class of a realized child whose declaration
  site also passed `orbit=Orbit(...)`
- **THEN** the first reports `spin` alone and the second reports `spin`
  then `orbit`, both read off a class without constructing anything

#### Scenario: A revolute without an axis is refused outside a mate

- **WHEN** a class body declares `turn = Revolute(unit='deg')`, or a
  parent declares a child with `turn=Revolute()` at its declaration site
- **THEN** class definition raises, naming the class and the joint and
  saying an axis may be left out only in a mate's freedom

#### Scenario: A revolute with an axis is unchanged

- **WHEN** a class body declares `turn = Revolute((0, 0, 1))`, the axis
  passed by position as before this change
- **THEN** the class carries the joint with that axis, exactly as before

#### Scenario: A joint of another kind written without an axis is refused naming its kind

- **WHEN** a class `Loose` declares `slide = Prismatic(axis=None,
  unit='mm')`; or a parent `Rail` declares `car = Slider(travel=Prismatic(axis=None))`;
  or a palm `Palm` states the mate
  `grip = finger.origin.on(seat, Prismatic(axis=None, range=(-11, 20), unit='mm'))`;
  or a class declares `orbit = Orbit(axis=None, carries=(0, 0, 1))`
- **THEN** each class definition raises, naming respectively `Loose.slide`;
  `Rail`, `travel` and `Slider`; `Palm.grip` as the mate's freedom; and the
  orbit's class and `orbit` — never the moving child's class for the
  mate — naming the kind, `Prismatic` or `Orbit`, and saying its axis is
  required everywhere, for the `Prismatic` a mate's freedom included; and
  none of the messages calls the joint a `Revolute`

### Requirement: A declared range refuses a binding outside it

The system SHALL refuse, at the moment of binding, a plain numeric value
outside a joint's declared `range`, raising an error of a kind exported
from the joints module and naming the joint, the value, the range, the
unit and the node — by its path in the tree when the node is linked
under a root, and otherwise by its name and class, because a node bound
before any walker linked it has no path to name. For a joint a MATE gave
the node — the joint a fresh freedom installs on the moving child — the
error SHALL name, in place of the joint and the node, the MATE and the
assembly that states it, by that assembly's path, or its name and class
when it is the root: the mate's coordinate on that assembly is the one
place the value can be bound, and the joint on the child is written
nowhere. A child not yet linked under that assembly SHALL be named as
any unlinked node is. Every refusal of this requirement, and the clocked
simulation's refusals of a bound it compiled for such a coordinate, SHALL
name a mate's coordinate so. A binding that is not a plain
number — a symbolic expression, a driver token — SHALL NOT be checked at
bind time, because its value is not known there; a joint with no
declared range, and a bound stated as `None`, SHALL accept any binding
on that side. A `Driver` bound to a joint
SHALL keep its own declared range, which is presentation metadata and
never a clamp, and the joint's range SHALL apply to the value that
reaches the joint.

A bound stated as a CALLABLE SHALL be applied, at the moment of
binding, to THE VALUE BEING BOUND, and the binding refused when that
value lies outside the pair so evaluated — the refusal naming the
evaluated bound as well as the joint, the value, the unit and the node,
and refusing likewise when the evaluated pair is reversed or is not a
number. A bound that is not satisfied at its own argument therefore
forbids every value and says so by name at the first binding. Under a
RUNNING root the same declaration is additionally a physical stop,
evaluated once per tick from the committed state, under the simulation
requirement "A declared range is a physical stop located inside the
tick"; under a CLOCKED root it is additionally a stop on a REQUEST'S
PATH, evaluated from the state the request starts at and clipping the
travel that request admits, under the simulation requirement "A bound
stops a clocked request on its path"; under every other root a range
refuses a binding and never clamps or stops.

A bound stated as a `Bound` that reads other coordinates SHALL NOT be
applied at the moment of binding, because the coordinates it reads
are bound by the solver in an order the author does not state; the
binding SHALL be recorded on the open enumeration and JUDGED WHEN THAT
ENUMERATION CLOSES, after deferred relations have propagated, over the
values then bound: the reads resolved against the declarer, the
expression applied to the bound value and the read values, the pair
ordered, and the value checked inclusive. A value outside the pair so
evaluated SHALL raise the joint range error naming the node, the joint,
the value, the unit, the evaluated bound AND every coordinate the bound
read with the value it read. A read that holds no value or a symbolic
one at the close SHALL NOT be judged, on the rule a symbolic binding
already has. A coordinate a RUNNING simulation owns SHALL NOT be judged
by the enumeration: the run located its stop and committed inside it,
and one authority judges one binding. On that same rule, a coordinate a
CLOCKED simulation compiled a constraint for SHALL NOT be judged by the
enumeration at the pose a REQUEST makes — neither at the moment of
binding nor at the close of that enumeration — because the clocked
simulation clipped the request at that bound and judges the constraint
itself, over the bank the request ends at, under the simulation
requirement "A bound stops a clocked request on its path". Every pose
that is NOT a request — construction, `state=`, `restore` — SHALL be
judged here as it is judged today. A binding made outside any
enumeration SHALL place the body and SHALL NOT be judged there, no pass
being open to record it on — exactly as a read of an unbound coordinate
made outside an enumeration is not recorded; it SHALL be judged at the
close of the next enumeration that binds the coordinate again.

#### Scenario: An out-of-range angle is refused by name

- **WHEN** a joint declaring `range=(-135, 135)` in degrees is bound to
  `170`
- **THEN** the binding raises an error naming the node's path, the
  joint, `170`, the range and `deg`, and the node carries no motion from
  that binding

#### Scenario: A symbolic binding is not checked

- **WHEN** the same joint is bound from an expression in the animation
  time whose values pass outside the range
- **THEN** the binding succeeds and publishes the expression, because
  the value is not known at bind time

#### Scenario: A binding inside the range is placed

- **WHEN** the same joint is bound to `-135` and then to `135`
- **THEN** both bindings succeed, the bounds being inclusive

#### Scenario: An open bound accepts anything on its side

- **WHEN** a joint declares `range=(0, None)` and is bound to `10000`,
  and then to `-1`
- **THEN** the first binding succeeds and the second is refused naming
  the joint, `-1` and the lower bound

#### Scenario: A bound reading other coordinates is judged when the enumeration closes

- **WHEN** an untimed root drives `plug.turn`, whose range is
  `(0, Bound(lambda turn, a, b: 90 * (abs(a) <= 0.05) * (abs(b) <= 0.05), reads=(p1.lift, p2.lift)))`,
  from a `turn` driver and the two lifts from a `feed` driver, and
  `set_state(turn=30, feed=0)` leaves a lift at `5`
- **THEN** the enumeration's close raises the joint range error naming
  `plug.turn`, `30`, the evaluated upper bound `0`, `p1.lift` and
  `p2.lift` with the values they held, whatever order the solver bound
  them in

#### Scenario: A bound reading other coordinates admits a possible pose

- **WHEN** the same root is bound with `set_state(turn=30, feed=20)`,
  which leaves both lifts at `0`
- **THEN** the enumeration closes without error and the plug's body
  carries the 30-degree turn

#### Scenario: A read holding no value is not judged

- **WHEN** a coordinate whose bound reads another is bound while that
  other coordinate is left unbound by the enumeration
- **THEN** the binding is placed and the enumeration closes without
  judging that bound

#### Scenario: A self-referential bound is evaluated at the value being bound

- **WHEN** a joint declaring
  `range=(lambda turn: 36 * floor(turn / 36), None)` is bound to `40`,
  and then to `36`, and then to `0`
- **THEN** every binding succeeds, because the lower bound evaluates to
  `36`, `36` and `0` respectively, and the body carries the motion of
  each

#### Scenario: A bound no value can satisfy is refused by name

- **WHEN** a joint declaring `range=(lambda turn: turn + 1, None)` is
  bound to any number
- **THEN** the binding is refused naming the joint, the value and the
  evaluated bound

#### Scenario: A clocked request stops at the bound instead of being refused

- **WHEN** a clocked simulation's request would carry a coordinate declaring
  `range=(0, 9)` to `20`
- **THEN** the request admits only the travel that leaves the coordinate at
  `9`, the pose binds `9` without judging it here, no joint range error is
  raised, and the request reports the bound it met

#### Scenario: A pose that is not a request is judged here as before

- **WHEN** the same clocked model is constructed with a `state=` whose bank
  poses that coordinate at `20`
- **THEN** the binding is refused here, naming the node, the joint, `20` and
  the range, because a construction has no path to clip and a machine cannot
  be put where it cannot be

#### Scenario: A range refusal on a mate's joint names the mate

- **WHEN** a root `Gripper` holds `wrist`, which holds `palm`, which
  states the mate `left_grip = left_finger.origin.on(left_seat,
  Prismatic(axis=(0, 1, 0), range=(-11, 20), unit='mm'))`, and the root's
  `grip` driver, driving `wrist.palm.left_grip`, is bound to `25`
- **THEN** the binding is refused with a message beginning
  `wrist.palm: mate 'left_grip' declares the range -11 to 20 mm`, naming
  `25`, and not naming the moving child `left_finger`
