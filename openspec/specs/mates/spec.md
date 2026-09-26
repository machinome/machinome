# mates Specification

## Purpose
TBD - created by archiving change place-parts-by-mate. Update Purpose after archive.
## Requirements
### Requirement: A part declares named frames

The system SHALL accept a **frame** as a class-body declaration on a node
class: an attribute holding `Frame(at=(0, 0, 0), z=(0, 0, 1), x=None)`,
an origin `at` and a right-handed triad whose third axis is `z`, stated
in the declaring node's OWN rest frame — the frame its own `render()`
states its geometry in, the frame a class-declared joint is read in.
`Frame` SHALL be importable from `machinome.node.frames` and SHALL also
resolve from `machinome.node`. The framework SHALL transform nothing
when it reads a frame: the numbers are the declarer's own.

A frame SHALL be declarable on any node kind — a leaf adapter, a fusion,
an imported part and an `AssemblyNode` alike — because a frame is drawn
on nothing and an assembly's frames are its connectors to the assembly
above it.

A frame SHALL take its name from the attribute it is assigned to, SHALL
be reported in declaration order by an enumerator exported beside it,
without constructing an instance, and SHALL be inherited through the
method resolution order like any class attribute — including from a
plain mixin that is not a node. A subclass assigning `None` to that
attribute SHALL declare no frame of that name.

A frame's name SHALL NOT clash with a declared parameter, a declared
child, a port, a joint coordinate, a marking or a mate of the same
class, and SHALL NOT shadow an attribute every node carries; either
clash SHALL be refused when the class is created, naming the class, the
attribute and what it collides with.

A frame SHALL NOT be a parameter, a child, a port, a joint or a part: it
SHALL contribute no solid, no operation and no artifact, and adding,
removing or changing a frame SHALL change no node's identity and no
artifact key.

#### Scenario: A part declares a connector

- **WHEN** a forearm class body assigns
  `hinge = Frame(at=(0, 0, 81.5), z=(0, 1, 0), x=(1, 0, 0))`
- **THEN** the class is created, the frame is named `hinge`, and the
  class reports one declared frame, read off the class without
  constructing an instance

#### Scenario: An assembly declares its own connector

- **WHEN** an `AssemblyNode` subclass assigns
  `elbow_pin = Frame(at=(0, 160, 68), z=(0, 0, 1))`
- **THEN** the class is created and reports the frame `elbow_pin`

#### Scenario: A frame is inherited and can be dropped

- **WHEN** a base part declares `hinge` and `foot`, and a subclass
  assigns `foot = None`
- **THEN** the base reports `hinge` then `foot`, and the subclass reports
  `hinge` alone

#### Scenario: A frame declared in a plain mixin belongs to the node

- **WHEN** a plain class that is not a node declares a frame, and a node
  class inherits it
- **THEN** the node class reports that frame

#### Scenario: A frame cannot take a declared name

- **WHEN** a part declares the parameter `hinge`, or the joint `hinge`,
  and also a frame named `hinge`
- **THEN** creating the class raises, naming the class, the attribute and
  what it collides with

#### Scenario: A frame cannot shadow a node attribute

- **WHEN** a part declares a frame named `color`
- **THEN** creating the class raises, naming the class, the attribute and
  the node attribute it would shadow

#### Scenario: A frame is not identity

- **WHEN** two otherwise identical part classes differ only in a frame
  one of them declares
- **THEN** their realized instances have the same identity and key the
  same artifacts

### Requirement: A frame resolves against its declarer at realization

Each of a frame's three arguments SHALL follow the rule a joint's
arguments follow: a sequence of three components, each a number, a token
of a parameter the declaring class declares or a formula over such
tokens; or, for the whole argument, a callable of one argument called
with the realized declaring node. A frame SHALL be resolved per instance
when its declaring node is constructed — after the node's parameters are
resolved and its `check()` has run, and before any of its children is
realized, the moment a class-declared joint's arguments are resolved —
so a frame that cannot resolve is refused naming the class, the frame
and the argument, whether or not any mate names it.

A resolved frame SHALL be an origin and three unit directions `x`, `y`,
`z`: `z` the declared `z` normalized; `x` the declared `x` with its
component along `z` removed, then normalized; `y` equal to `z × x`.
Neither `z` nor `x` need be written as a unit vector.

When `x` is omitted and `z` lies along a principal axis, `x` SHALL be
the next principal axis in right-hand order — the rule a wrapped
marking's derived zero follows: `+X` for `+Z`, `+Y` for `+X`, `+Z` for
`+Y`, and the negated axis for a negated `z` (`-X` for `-Z`). When `x`
is omitted and `z` does not lie along a principal axis, the frame SHALL
be refused, naming the frame and saying that `x` must be stated, because
`x` fixes the zero of a revolute mate and a derived one would be
invisible in the declaration.

A frame SHALL be refused, naming the class, the frame and the argument,
when a component does not resolve to a number, when `z` has no length,
or when `x` is parallel to `z`.

#### Scenario: A frame reads its declarer's parameters

- **WHEN** a part declaring `reach = Length(160)` and
  `pin = Frame(at=(0, reach, 68), z=(0, 0, 1))` is realized with
  `reach=150`
- **THEN** the resolved frame's origin is `(0, 150, 68)`

#### Scenario: A frame may be computed from the realized node

- **WHEN** a part declares `bore = Frame(at=lambda node: node.built.bore)`
- **THEN** each realized instance resolves the origin by calling the
  function with that instance

#### Scenario: The x axis follows the principal rule when omitted

- **WHEN** a frame declares `z=(0, 1, 0)` and no `x`
- **THEN** it resolves with `x = (0, 0, 1)` and `y = (1, 0, 0)`

#### Scenario: The x axis is squared up against z

- **WHEN** a frame declares `z=(0, 0, 2)` and `x=(1, 0, 1)`
- **THEN** it resolves with `z = (0, 0, 1)`, `x = (1, 0, 0)` and
  `y = (0, 1, 0)`

#### Scenario: A diagonal z must state x

- **WHEN** a frame declares `z=(0, 1, 1)` and no `x`
- **THEN** realizing the declaring node raises, naming the class and the
  frame and saying `x` must be stated

#### Scenario: A degenerate frame is refused

- **WHEN** a frame declares `z=(0, 0, 0)`, or `z=(0, 0, 1)` with
  `x=(0, 0, 5)`
- **THEN** realizing the declaring node raises, naming the class, the
  frame and the argument

### Requirement: An assembly mates a child's frame onto another frame

The system SHALL let an assembly relate two frames in its class body with
the statement `<moving frame>.on(<fixed frame>, <freedom>)`, called a
**mate**. The frame that speaks is the one that MOVES. The statement
SHALL be recorded on the class being defined whether or not it is
assigned; assigning it, `elbow = art3.hinge.on(elbow_pin, Revolute())`,
SHALL name the mate. A mate SHALL be enumerable off the class, in
declaration order and without constructing an instance, by an enumerator
exported from `machinome.motion.mates`, and SHALL be inherited by a
subclass.

The MOVING end SHALL be a frame declared by a child the assembly declares
directly, written `<child>.<frame>`. The FIXED end SHALL be either a
frame the declaring assembly itself declares, written by its bare name in
the class body, or a frame declared by another child the assembly
declares directly, written `<child>.<frame>`.

The FREEDOM SHALL be a `Revolute`: `Revolute(range=(lo, hi), unit='deg')`.
It MAY also state the line the child turns about,
`Revolute(axis=(x, y, z), at=(x, y, z), range=..., unit=...)`, because a
design's connectors are ATTACHMENT frames and the line a part turns about
need not be the moving frame's `z` nor pass through its origin. A stated
`axis` and a stated `at` SHALL each be three numbers, read in the MOVING
CHILD's own rest frame — the frame the moving frame is declared in and a
joint the child's own class declares is read in — and nothing SHALL be
carried or inverted to read them. Each SHALL be independent of the
other: a freedom may state `axis` alone, `at` alone, both or neither,
and what it leaves out the moving frame supplies (see "A mate gives the
moving child a joint"). The freedom's `range` SHALL be omitted, a pair of
numbers, or a pair whose bounds are numbers, `None`, or functions of the
coordinate's own value.

The following SHALL be refused when the declaring class is created,
naming the class, the mate and the reason:

- a mate stated on a class that is not an `AssemblyNode`;
- a moving end that is the assembly's own frame, or that is not a frame,
  or whose frame is reached through more than one child;
- a fixed end reached through more than one child;
- a fixed end on a child that can move within the assembly — one whose
  class declares a joint, including one a mate or a declaration site
  gives it — because the moving child is placed against the fixed
  child's REST placement and would not follow it;
- either end on a child held in a list or declared with `.repeat()`;
- a second mate whose moving end is a frame of a child another mate
  already places, which is a loop;
- a mate that names a child the class — or, for an inherited mate, the
  subclass — no longer declares as the one the mate was written against;
- a mate with a freedom that is left unnamed, because its coordinate is
  named after the mate;
- a freedom that is not a `Revolute` — a `Prismatic`, an `Orbit` or a
  `Free` —, a freedom whose range is a callable of the node or reads
  other coordinates, or a freedom already declared on some class;
- a freedom whose stated `axis` or `at` is not three numbers — a
  parameter token, a formula, or a callable of the node, each of which
  would be resolved against the moving child although it is written in
  the assembly —, or whose stated `axis` has no length;
- a mate stated with no freedom, the rigid mate, which this version does
  not provide.

#### Scenario: Thor's elbow is one statement

- **WHEN** an upper-arm assembly declares
  `elbow_pin = Frame(at=(0, 160, 68), z=(0, 0, 1))` and the child
  `art3 = Art3()`, `Art3` declaring
  `hinge = Frame(at=(0, 0, 81.5), z=(0, 1, 0), x=(1, 0, 0))`, and states
  `elbow = art3.hinge.on(elbow_pin, Revolute(range=(-135, 135)))`
- **THEN** the class is created and reports one mate named `elbow`,
  moving `art3.hinge` onto `elbow_pin`

#### Scenario: A mate is refused outside an assembly

- **WHEN** a leaf part's class body states a mate
- **THEN** creating the class raises, naming the class and saying a mate
  is stated on the assembly that holds both frames

#### Scenario: The moving end must be a child's own frame

- **WHEN** an assembly states `elbow_pin.on(art3.hinge, Revolute())`, or
  `art3.art4.foot.on(elbow_pin, Revolute())`
- **THEN** creating the class raises, naming the mate and saying the
  moving end is a frame declared by a directly declared child

#### Scenario: A fixed end on a moving child is refused

- **WHEN** an assembly declares children `link` and `cap`, `link` placed
  by a revolute mate, and states `cap.bottom.on(link.knee, Revolute())`
- **THEN** creating the class raises, naming the mate and `link`, and
  saying `cap` would rest against `link`'s rest placement and not follow
  it

#### Scenario: A second mate on one child is refused

- **WHEN** an assembly states two mates whose moving ends are frames of
  the same child
- **THEN** creating the class raises, naming both mates and saying a
  second mate on a placed child closes a loop

#### Scenario: A mate needs a revolute freedom

- **WHEN** an assembly states `art3.hinge.on(elbow_pin)`, or
  `art3.hinge.on(elbow_pin, Prismatic())`
- **THEN** creating the class raises, naming the mate and saying which
  freedoms a mate accepts in this version

#### Scenario: A freedom states the line across its attachment frame

- **WHEN** a housing declares `shoulder_pin = Frame(at=(0, 0, 123))`,
  its child `art2` declares
  `bore = Frame(at=(0, 0, 68), z=(0, 1, 0), x=(-1, 0, 0))` — Thor's
  shoulder connector as the design states it, its `z` across the joint
  line — and the housing states
  `shoulder = art2.bore.on(shoulder_pin, Revolute(axis=(0, 0, 1),
  at=(0, 0, 0), unit='deg'))`
- **THEN** the class is created and reports one mate named `shoulder`,
  moving `art2.bore` onto `shoulder_pin`

#### Scenario: A freedom may state its anchor alone

- **WHEN** an assembly states
  `swing = part.hinge.on(pin, Revolute(at=(0, 0, 0)))`
- **THEN** the class is created, the line keeping the moving frame's `z`
  as its direction

#### Scenario: A stated line is numbers

- **WHEN** an assembly declaring `lift = Length(5)` states
  `part.hinge.on(pin, Revolute(at=(0, 0, lift)))`, or
  `part.hinge.on(pin, Revolute(axis=lambda node: (0, 0, 1)))`
- **THEN** creating the class raises, naming the class, the mate and the
  argument, and saying a mate's stated line is written in the assembly
  and read in the moving child's frame, so it is three numbers

#### Scenario: A stated axis has a direction

- **WHEN** an assembly states
  `part.hinge.on(pin, Revolute(axis=(0, 0, 0)))`
- **THEN** creating the class raises, naming the class, the mate and
  `axis`, and saying an axis of zero length states no line

#### Scenario: A mate with a freedom has a name

- **WHEN** an assembly states `art3.hinge.on(elbow_pin, Revolute())`
  bare, without assigning it
- **THEN** creating the class raises, saying the mate's coordinate is
  named after the mate and asking for an assignment

#### Scenario: A list-held child cannot be mated

- **WHEN** an assembly declares `arms = [Arm(), Arm()]` and states a mate
  on a frame reached through `arms`
- **THEN** the statement is refused, naming the declaration and saying a
  list-held child is named one by one

### Requirement: A mate places the moving child at rest

At realization the system SHALL place the moving child, at rest, so that
its moving frame coincides with the fixed frame, whole triad onto whole
triad — origin on origin, `x` on `x`, `y` on `y` and `z` on `z`. Its rest
placement in the assembly SHALL be the fixed frame's owner placement,
composed with the fixed frame, composed with the inverse of the moving
frame, where the owner placement is the identity for a frame of the
declaring assembly and the fixed child's rest placement for a frame of a
child. `x` therefore fixes the rest attitude and the zero of the mate's
coordinate, not only its line.

The placement SHALL be applied as ordinary rest operations on the moving
child — one rotation, omitted when the rotation is the identity, then
one translation, omitted when it is zero — exactly as if the author's
`render()` had written them, after the author's `render()` has returned,
once per instance, and composing outside every joint the child's own
class declares. A rotation axis component and a rotation angle within
`1e-9` of a whole number SHALL be that whole number, as a joint's
normalized axis is snapped; the translation SHALL be what the arithmetic
gives.

A child a mate places SHALL NOT also be placed by the assembly's
`render()`: a rotation or translation the `render()` applies to it SHALL
be refused, naming the assembly, the child and the mate, because a
placement is stated once. A `render()` that re-runs on every binding
SHALL NOT accumulate a mate's placement.

A fixed child's rest placement that does not evaluate to numbers SHALL
refuse the mate at realization, naming the mate and the child.

#### Scenario: Thor's elbow rests where Thor's render puts it

- **WHEN** the upper arm of "Thor's elbow is one statement" is realized
  and rendered with its coordinate unbound
- **THEN** the forearm root's rest operations are a rotation of 90
  degrees about `(1, 0, 0)` followed by a translation of
  `(0, 241.5, 68)`, equal in kind, order and value to the operations
  Thor's hand-written `render()` applies

#### Scenario: Thor's shoulder rests where Thor's render puts it

- **WHEN** a housing declares
  `shoulder_pin = Frame(at=(0, 0, 123), z=(0, 1, 0))`, its child `art2`
  declares `bore = Frame(at=(0, 0, 68), z=(0, 0, 1), x=(0, 1, 0))`, and
  the housing states `shoulder = art2.bore.on(shoulder_pin, Revolute())`
- **THEN** the child rests turned 180 degrees about
  `(0, 0.7071…, 0.7071…)` and translated by `(0, -68, 123)`, within
  `1e-9` of Thor's hand-written placement

#### Scenario: x fixes the rest attitude

- **WHEN** the elbow of "Thor's elbow is one statement" is declared with
  the forearm root's `x` omitted
- **THEN** the two frames' `z` lines still coincide and the forearm root
  rests turned 120 degrees about `(1, 1, 1)/√3` rather than 90 degrees
  about `(1, 0, 0)`

#### Scenario: A fixed end on a still child uses the child's placement

- **WHEN** an assembly places the child `base` with `translate(0, 0, 10)`
  in `render()`, `base` declaring `seat = Frame(at=(0, 0, 79))` and no
  joint, and states `yaw = housing.origin.on(base.seat, Revolute())`
  with `housing` declaring `origin = Frame()`
- **THEN** the housing rests translated by `(0, 0, 89)`

#### Scenario: A mated child cannot be placed by hand

- **WHEN** an assembly states a mate on `art3` and its `render()` calls
  `self.art3.translate(...)`
- **THEN** rendering raises, naming the assembly, `art3` and the mate

#### Scenario: A re-running render does not stack the placement

- **WHEN** an assembly whose `render()` reads a driver states a mate, and
  it is rendered under three successive bindings
- **THEN** the moving child carries the mate's rest placement exactly
  once after each

### Requirement: A mate gives the moving child a joint

At realization the moving child SHALL move about a revolute joint whose
axis is the freedom's stated `axis`, or the moving frame's `z` when the
freedom states none, and whose anchor is the freedom's stated `at`, or
the moving frame's origin when the freedom states none — all in the
child's own rest frame, where the frame was declared and a stated line is
read, so nothing is carried or inverted — carrying the freedom's range
and unit. An `at` written as `(0, 0, 0)` SHALL be the child's own origin,
not the frame's. The frames SHALL fix the child's rest placement, and
therefore the zero of the coordinate, whatever line the freedom states;
the freedom SHALL fix only the line. Nothing SHALL check that a stated
line passes through the frames' common origin or lies along either
frame's `z`: an anchor is any point on its line, and the line is the
freedom's own.

A mate whose freedom states no line SHALL give the child exactly the
joint it gave before a freedom could state one. The joint SHALL behave as a class-declared joint of the
child in every respect: it SHALL be reported by the joint enumerator for
the class the child is realized as, under the mate's name, in a position
AFTER every joint the child's own class declares, and SHALL compose in
that position, outside the child's own freedoms and inside its rest
placement.

A child a mate moves SHALL keep its identity: it SHALL key the same
artifacts as the same child declared with no mate, and its class SHALL
report the declared class's name.

A mate whose name the moving child's class already answers to — a
parameter, a child, a port, a joint, a frame, a marking, a method or any
other attribute — SHALL be refused when the assembly's class is created,
naming the assembly, the mate, the child's class and what it already
declares.

#### Scenario: The elbow joint is the one Thor writes by hand

- **WHEN** the upper arm of "Thor's elbow is one statement" is realized
- **THEN** the forearm root's class reports a joint `elbow` with axis
  `(0, 1, 0)` and anchor `(0, 0, 81.5)`, and binding it to 30 places
  exactly the operations Thor's hand-declared `Revolute(axis=(0, 1, 0),
  at=(0, 0, 81.5))` places at 30

#### Scenario: Thor's shoulder turns about the line its freedom states

- **WHEN** the housing of "A freedom states the line across its
  attachment frame" is realized, and then bound with `shoulder` at 30
- **THEN** the upper arm's class reports a joint `shoulder` with axis
  `(0, 0, 1)` and anchor `(0, 0, 0)`; at rest the upper arm is turned
  180 degrees about `(0, 0.7071…, 0.7071…)` and translated by
  `(0, -68, 123)`, as Thor's hand-written `render()` places it; and at 30
  its operations are a turn of 30 about `(0, 0, 1)` with no centring
  pair, then that rest placement — the pose of the hand-placed arm
  jointed by `Revolute(axis=(0, 0, 1))` at 30

#### Scenario: Thor's wrist turns across its attachment frame

- **WHEN** an assembly declares `wrist_pin = Frame(at=(0, 0, 111.5))`
  and a child `art56` declaring `bore = Frame(x=(0, -1, 0))`, and states
  `wrist = art56.bore.on(wrist_pin, Revolute(axis=(1, 0, 0)))`, bound at
  30
- **THEN** the child rests turned 90 degrees about `(0, 0, 1)` and
  translated by `(0, 0, 111.5)`, and at 30 it turns 30 about `(1, 0, 0)`
  in its own frame inside that rest placement, as the hand-placed child
  jointed by `Revolute(axis=(1, 0, 0))` does

#### Scenario: A stated axis keeps the sign a reversed frame would flip

- **WHEN** an assembly declares `yaw_pin = Frame(at=(0, 0, -1))` and a
  child declaring `bore = Frame(z=(0, 0, -1))`, and states
  `yaw = child.bore.on(yaw_pin, Revolute(axis=(0, 0, 1)))`, bound at 30
- **THEN** the child's joint turns about `(0, 0, 1)`, not about the
  frame's `(0, 0, -1)`, and its pose at 30 is the hand-placed child's
  jointed by `Revolute(axis=(0, 0, 1))` at 30

#### Scenario: An anchor at the child's origin drops the centring pair

- **WHEN** Thor's shoulder is mated through a bore whose `z` is on the
  joint line, `bore = Frame(at=(0, 0, 68), z=(0, 0, 1), x=(0, 1, 0))`,
  once with `Revolute()` and once with `Revolute(at=(0, 0, 0))`, and
  each is bound at 30
- **THEN** the first joint's anchor is `(0, 0, 68)` and its operations
  carry the centring pair `∓(0, 0, 68)` around the turn, and the second
  joint's anchor is `(0, 0, 0)` and its operations are the turn alone,
  the two poses equal

#### Scenario: A mated wheel keeps its own spin inside the mate

- **WHEN** a wheel class declares `spin = Revolute(axis=(0, 0, 1))` and
  an assembly mates it with `steer = wheel.hub.on(knuckle, Revolute())`
- **THEN** the wheel's class reports `spin` then `steer`, and binding
  both applies `spin`'s operations innermost, then `steer`'s, then the
  mate's rest placement

#### Scenario: A mate cannot hide a child's attribute

- **WHEN** the forearm root's class already declares a joint `elbow` and
  the upper arm states `elbow = art3.hinge.on(elbow_pin, Revolute())`
- **THEN** creating the upper arm's class raises, naming the upper arm,
  the mate, the forearm root's class and its joint `elbow`

#### Scenario: A mated child keys its unmated artifacts

- **WHEN** a part is realized once as a mated child and once as an
  unmated child with the same arguments
- **THEN** both realized parts have the same identity

### Requirement: A mate owns a coordinate on the assembly

A mate with a freedom SHALL own one rotational coordinate on the
declaring assembly, named after the mate and carrying the freedom's
unit. It SHALL be reported by the port enumerator for the assembly's
class, SHALL read and bind on an instance as a joint's coordinate does,
and SHALL be an end of a relation, a target of a driver and a source of
a law as the `couplings` capability specifies.

Whenever the mate's coordinate is bound, the child's joint SHALL take its
value, subject to the freedom's range, by the end of the assembly's
simulate phase, and the child's body SHALL be placed exactly as a
binding of that joint places it. Whenever the mate's coordinate is
unbound, the child's joint SHALL be unbound and the child SHALL rest at
the mate's rest placement, exactly as a body with an unbound joint rests
— an unbound mate coordinate SHALL NOT be refused.

The joint a mate gives the child SHALL be bound only through the mate's
coordinate: binding it by any other route — an assignment on the child,
a relation or a driver naming it by path — SHALL be refused, naming the
mate's coordinate as the one to bind.

Reading an assembly's rigid mate is not provided in this version; the
rigid mate is refused (see "An assembly mates a child's frame onto
another frame").

#### Scenario: A driver turns Thor's elbow through the mate

- **WHEN** a root declares `angle = Driver(default=0, unit='deg')` and
  the upper arm of "Thor's elbow is one statement" as `arm`, states
  `angle.drives(arm.elbow)`, and is bound to `angle=30`
- **THEN** the forearm root's operations are exactly those of Thor's
  hand-placed, hand-jointed elbow at 30

#### Scenario: The mate's coordinate is a port of the assembly

- **WHEN** a consumer enumerates the ports of the upper arm's class
- **THEN** it receives `elbow`, a rotational coordinate in degrees

#### Scenario: A relation in the declaring body names the mate

- **WHEN** the upper arm states `elbow.drives(belt.travel, ratio=...)`
  after declaring the mate `elbow`
- **THEN** the class is created, and binding `elbow` drives the belt's
  travel as the relation states

#### Scenario: An unbound mate rests

- **WHEN** an assembly declaring a mate is rendered with nothing binding
  the mate's coordinate
- **THEN** rendering succeeds and the moving child carries only the
  mate's rest placement

#### Scenario: The installed joint has one binder

- **WHEN** an assembly declaring the mate `elbow` on `art3` binds
  `self.art3.elbow = 10` in its `simulate()`
- **THEN** the binding is refused, naming the mate's coordinate `elbow`
  as the one to bind

#### Scenario: The range belongs to the freedom

- **WHEN** the mate is declared with `Revolute(range=(-135, 135))` and
  its coordinate is bound to 150
- **THEN** the binding is refused naming the range, as a joint's range
  refuses it

### Requirement: A mate publishes nothing new

A mated machine's published document SHALL carry the mate's compiled
rest placement as ordinary operations and its coordinate as an ordinary
binding, SHALL declare the document version a machine without mates
declares, and SHALL add no field. A machine that declares no frame and
no mate SHALL publish a document byte-identical to the one it published
before frames and mates existed, and a mated machine whose mates' freedoms
state no line SHALL publish a document byte-identical to the one it
published before a freedom could state one. A mate whose freedom states
its line SHALL publish that line only as the axis and anchor of the
joint's ordinary operations.

#### Scenario: A mated machine needs no newer consumer

- **WHEN** a mated version of Thor's elbow fixture is exported
- **THEN** the document declares the same version an unmated machine
  declares, and its forearm root's operations and bindings are those of
  the hand-written elbow

#### Scenario: A machine without mates is unchanged

- **WHEN** a fixture machine that declares no frame or mate is exported
  before and after this change
- **THEN** the two documents are byte-identical

#### Scenario: A mate that states no line is unchanged

- **WHEN** a mated fixture machine whose freedoms state no line is
  exported before and after a freedom could state one
- **THEN** the two documents are byte-identical

