## MODIFIED Requirements

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
`at` SHALL be three numbers. A stated `axis` SHALL be three numbers or
one function of the assembly that states the mate (see "A mate's freedom
may be a function of the assembly that states it"). Each SHALL be read
in the MOVING CHILD's own rest frame — the frame the moving frame is
declared in and a joint the child's own class declares is read in — and
nothing SHALL be carried or inverted to read them. Each SHALL be
independent of the other: a freedom may state `axis` alone, `at` alone,
both or neither, and what it leaves out the moving frame supplies (see
"A mate gives the moving child a joint"). The freedom's `range` SHALL be
omitted, a pair of numbers, a pair whose bounds are numbers, `None`, or
functions of the coordinate's own value, or one function of the assembly
that states the mate returning such a pair.

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
  `Free` —, a freedom whose range is neither a pair nor a function, or
  holds a parameter token or a formula, or reads other coordinates, or a
  freedom already declared on some class;
- a freedom whose stated `axis` is neither three numbers nor a function,
  or whose stated `at` is not three numbers — a parameter token or a
  formula in either, which would be resolved by name against the moving
  child although it is written in the assembly, or a function in `at`,
  which this version does not accept —, or whose stated `axis` of three
  numbers has no length;
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

#### Scenario: A stated line holds no parameter

- **WHEN** an assembly declaring `lift = Length(5)` states
  `part.hinge.on(pin, Revolute(at=(0, 0, lift)))`, or
  `part.hinge.on(pin, Revolute(at=(0, 0, lift * 2)))`
- **THEN** creating the class raises, naming the class, the mate and the
  argument, and saying a mate's stated line is written in the assembly
  and read in the moving child's frame, so a parameter or a formula
  would resolve against the moving child

#### Scenario: A stated anchor is not a function

- **WHEN** an assembly states
  `part.hinge.on(pin, Revolute(at=lambda node: (0, 0, 0)))`
- **THEN** creating the class raises, naming the class, the mate and
  `at`, and saying a stated anchor is three numbers in this version

#### Scenario: A freedom's axis or range may be a function

- **WHEN** an assembly states
  `swing = part.hinge.on(pin, Revolute(axis=lambda node: (0, 0, 1)))`,
  or `swing = part.hinge.on(pin, Revolute(range=lambda node: (0, 90)))`
- **THEN** the class is created and reports one mate named `swing`

#### Scenario: A range holds no parameter

- **WHEN** an assembly declaring `limit = Angle(90)` states
  `part.hinge.on(pin, Revolute(range=(0, limit)))`
- **THEN** creating the class raises, naming the class, the mate and the
  range

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

### Requirement: A mate gives the moving child a joint

At realization the moving child SHALL move about a revolute joint whose
axis is the freedom's stated `axis` — the three numbers written, or what
its function returned for the realized assembly —, or the moving frame's
`z` when the freedom states none, and whose anchor is the freedom's
stated `at`, or the moving frame's origin when the freedom states none —
all in the child's own rest frame, where the frame was declared and a
stated line is read, so nothing is carried or inverted — carrying the
freedom's range — the range written, or what its function returned for
the realized assembly — and unit. An `at` written as `(0, 0, 0)` SHALL be the child's own origin,
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

### Requirement: A mate's ends and freedom are read off the class

A mate SHALL be readable, off the class and without constructing an
instance, as the object `declared_mates(cls)` reports under its name,
with these reads documented in the framework's API reference:

- `name`, the attribute the mate is assigned to — also the name of its
  coordinate on the assembly and of the joint it gives the child;
- `moving`, the moving end, whose `written` SHALL be
  `'<child>.<frame>'` as the class body writes it;
- `fixed`, the fixed end as the class body writes it: for a frame of a
  child, a reference whose `written` SHALL be `'<child>.<frame>'`; for a
  frame of the assembly itself, written by its bare name, that `Frame`
  declaration, whose `name` SHALL be its attribute;
- `freedom`, the `Revolute` written in the statement, whose `axis` SHALL
  be `None` when no axis is stated, the three numbers as written, not
  normalized, when numbers are stated, and the function itself, the same
  object, when a function is stated; whose `anchor_written` SHALL say
  whether `at` was written; whose `at` SHALL be the three numbers as
  written when `anchor_written` is true, and SHALL NOT be the mate's
  anchor when it is false, the anchor then being the moving frame's
  origin; whose `range` SHALL be as written — a pair, or the function
  itself, the same object — or `None`; and whose `unit` SHALL be as
  written, or `'deg'`.

When the freedom's `axis` is not a function, the line a mate turns its
child about SHALL be readable from these reads and the moving child's
resolved frames alone: `freedom.axis` when it is not `None`, else the
moving frame's resolved `z`; through `freedom.at` when `anchor_written`
is true, else through the moving frame's resolved `at`. When it is a
function, the read SHALL be that function, and the axis on a realized
machine is what the function returned for that machine's assembly; no
documented read reports it in this version. Reading any of them SHALL
change nothing and SHALL NOT call a function.

#### Scenario: Thor's elbow is read back

- **WHEN** `declared_mates` of the upper arm of "Thor's elbow is one
  statement" is read under `elbow`
- **THEN** its `name` is `elbow`, its `moving.written` is
  `'art3.hinge'`, its `fixed` is the upper arm's `elbow_pin` frame with
  `name` `elbow_pin`, and its freedom's `axis` is `None`,
  `anchor_written` false, `range` `(-135, 135)` and `unit` `'deg'`

#### Scenario: A fixed end on a child is read as written

- **WHEN** an assembly states `yaw = housing.origin.on(base.seat,
  Revolute())` and `declared_mates` is read under `yaw`
- **THEN** its `moving.written` is `'housing.origin'` and its
  `fixed.written` is `'base.seat'`

#### Scenario: A stated line is read as written

- **WHEN** the housing of "A freedom states the line across its
  attachment frame" is read under `shoulder`
- **THEN** its freedom's `axis` is `(0, 0, 1)`, `anchor_written` is true
  and `at` is `(0, 0, 0)`, the child's own origin

#### Scenario: A left-out anchor is not the child's origin

- **WHEN** an assembly states
  `swing = part.hinge.on(pin, Revolute(axis=(0, 0, 2)))`, `part`
  declaring `hinge = Frame(at=(0, 0, 5))`, and the mate is read
- **THEN** its freedom's `axis` is `(0, 0, 2)` as written and
  `anchor_written` is false, and the installed joint's anchor on a
  realized `part` is `(0, 0, 5)`, the moving frame's resolved origin,
  not `(0, 0, 0)`

#### Scenario: The reference lists the reads

- **WHEN** a reader opens the framework's API reference at "Frames and
  mates"
- **THEN** it lists `resolved_frames`, the resolved frame with
  `rotation`, and the mate with its `name`, `moving`, `fixed` and
  `freedom`, beside `Frame`, `declared_frames` and `declared_mates`


#### Scenario: A function is read as written

- **WHEN** the mount of "OpenArm's joint is one mate on both sides" is
  read under `turn`, its `axis` and `range` functions counting their
  calls
- **THEN** its freedom's `axis` and `range` are those two functions, the
  same objects, `anchor_written` is false, and neither function's count
  moves

## ADDED Requirements

### Requirement: A mate's freedom may be a function of the assembly that states it

The system SHALL accept, as a mate's freedom's `axis` and as its
`range`, each as a whole, one function of one argument — a callable that
is not a parameter token, a formula or a `Bound`. Each function SHALL be
called with the realized ASSEMBLY that states the mate — the node whose
class body the function is written in, the node a function given to a
frame that assembly declares is called with — and SHALL NOT be called
with the moving child. For a mate a subclass inherits, it SHALL be called
with the realized subclass instance.

Each function SHALL be called exactly once per realized assembly, when
that assembly realizes the moving child: after the assembly's parameters
are resolved, its `check()` has run and its joints and frames are
resolved, with every child it declares before the moving child already
realized, and before the assembly renders — the state in which a
function given to a site-declared joint is called. Binding, rendering,
reading and exporting SHALL NOT call it again. It SHALL enter no node's
identity and no artifact key.

The function's result SHALL be taken exactly as the same argument written
in numbers is taken: an `axis` SHALL be three real numbers — each an
`int` or a `float`, not a `bool` — of non-zero length, read in the moving
child's own rest frame; a `range` SHALL be a `(lo, hi)` pair whose
bounds are numbers, `None`, functions of the coordinate's own value, or
a `Bound` that reads no other coordinate. The joint the mate gives the
moving child SHALL then resolve, normalize and refuse that result as it
resolves, normalizes and refuses the same numbers written in the
freedom, so a function returning the numbers a freedom could state gives
the child the joint those numbers give.

A function that raises, or whose result is not what the numbers form
takes — a sequence of another length, a string, a `bool`, a parameter
token or a formula, a function, an axis of zero length, a range that is
not a pair or holds a bound that is not a number, `None`, a function of
the coordinate or a `Bound` reading no other coordinate — SHALL be
refused when the assembly realizes the moving child, naming the
assembly's class, the mate and the argument, and quoting what the
function returned or raised.

The frames alone SHALL fix the moving child's rest placement, as "A mate
places the moving child at rest" states, whatever the function returns.

#### Scenario: OpenArm's joint is one mate on both sides

- **WHEN** an assembly `HandedMount` declares `left = Flag(False)`,
  `pin = Frame(at=lambda node: (0, 62.5 if node.left else -62.5, 0))`
  and the child `link = HandedLink()`, `HandedLink` declaring
  `origin = Frame()` and no parameter `left`, and states
  `turn = link.origin.on(pin, Revolute(axis=lambda node: (0, 1, 0) if
  node.left else (0, -1, 0), range=lambda node: (-200, 80) if node.left
  else (-80, 200), unit='deg'))`, and it is realized once with
  `left=True` and once with `left=False`
- **THEN** the class is created; the left link's joint `turn` resolves
  with axis `(0, 1, 0)` and range `(-200, 80)` and the link rests
  translated by `(0, 62.5, 0)`; the right link's resolves with axis
  `(0, -1, 0)` and range `(-80, 200)` and it rests translated by
  `(0, -62.5, 0)`; binding the left mount's `turn` to 150 is refused
  naming the range, and binding the right mount's `turn` to 150 is
  accepted

#### Scenario: The function receives the assembly, not the moving child

- **WHEN** the moving child's class declares its own `left = Flag(True)`,
  the assembly's `left` is `False`, the child is declared without
  passing `left`, and the freedom's `axis` function records the node it
  is called with
- **THEN** it is called with the realized assembly, an instance of the
  assembly's class, and the child's joint turns about `(0, -1, 0)`, the
  assembly's side

#### Scenario: The function is called once per realized assembly

- **WHEN** functions counting their calls are given as a freedom's
  `axis` and `range`, two assemblies are realized, and each is then bound
  three times, rendered and exported
- **THEN** each function has been called twice, once for each realized
  assembly, both before the first binding

#### Scenario: The function sees the assembly as a site's function does

- **WHEN** an assembly declares a child `base` before the moving child,
  and the freedom's `axis` function reads `node.base` and
  `resolved_frames(node)`
- **THEN** both reads succeed when the moving child is realized

#### Scenario: A function's result is taken as the numbers are

- **WHEN** the freedom's `axis` function returns `(0, 1)`, `(0, 0, 0)`,
  `(0, 0, True)`, `'xyz'` or a function, or its `range` function returns
  `(0,)` or `(True, 90)` or a pair holding a `Bound` that reads another
  coordinate, or either function raises
- **THEN** creating the assembly's class succeeds, and realizing the
  assembly raises when it realizes the moving child, naming the
  assembly's class, the mate and the argument and quoting what the
  function returned or raised

#### Scenario: A returned axis is normalized as a written one

- **WHEN** the freedom's `axis` function returns `(0, 3, 0)`
- **THEN** the child's joint resolves with axis exactly `(0, 1, 0)`

#### Scenario: A handed machine publishes each side's line as operations

- **WHEN** a root declares `angle = Driver(default=30, unit='deg')`,
  `left = HandedMount(left=True)` and `right = HandedMount(left=False)`,
  states `angle.drives(left.turn)` and `angle.drives(right.turn)`, and is
  exported
- **THEN** the document declares the version a machine without mates
  declares and adds no field, and each link's operations equal, within
  `1e-9`, those of a hand-placed twin whose link class declares
  `turn = Revolute(axis=lambda node: ..., range=lambda node: ...)` over
  its own `left` flag and whose mount's `render()` translates the link
  to the same origin
