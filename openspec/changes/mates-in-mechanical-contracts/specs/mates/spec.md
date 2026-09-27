## MODIFIED Requirements

### Requirement: An assembly mates a child's frame onto another frame

The system SHALL let an assembly relate two frames in its class body with
the statement `<moving frame>.on(<fixed frame>, <freedom>)`, called a
**mate**, or, with the freedom left out, `<moving frame>.on(<fixed
frame>)`, called a **rigid mate** (see "A mate with no freedom holds a
child where two frames meet"). The frame that speaks is the one that MOVES. The statement
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

The FREEDOM MAY be left out -- passing `None` is the same statement --
and, when stated, SHALL be a `Revolute`, `Revolute(range=(lo, hi), unit='deg')`,
the child turning about a line, or a `Prismatic`,
`Prismatic(axis=(x, y, z), range=(lo, hi), unit='mm')`, the child sliding
along one; both kinds SHALL follow every rule of this requirement alike
but one: a `Prismatic` freedom SHALL state its `axis`, as a `Prismatic`
anywhere must, and only a `Revolute` freedom MAY leave its `axis` out. A
`Prismatic` without an axis SHALL be refused by its own constructor, as
it is refused anywhere, before the mate is stated; the mate SHALL add no
refusal of its own. A `Revolute` freedom MAY also state its line,
`Revolute(axis=(x, y, z), at=(x, y, z), range=..., unit=...)`, and a
`Prismatic` freedom MAY state its anchor beside its axis,
`Prismatic(axis=(x, y, z), at=(x, y, z), range=..., unit=...)`, because
a design's connectors are ATTACHMENT frames and the line a part turns
about or slides along need not be the moving frame's `z` nor pass
through its origin. A `Prismatic` freedom's `at` places
nothing — a translation along a line is the same wherever the line is
taken to pass — and is carried as the joint's anchor, as a class-body
`Prismatic`'s is. A stated
`at` SHALL be three numbers. A stated `axis` SHALL be three numbers or
one function of the assembly that states the mate (see "A mate's freedom
may be a function of the assembly that states it"). Each SHALL be read
in the MOVING CHILD's own rest frame — the frame the moving frame is
declared in and a joint the child's own class declares is read in — and
nothing SHALL be carried or inverted to read them. Each SHALL be
independent of the other: a `Revolute` freedom may state `axis` alone,
`at` alone, both or neither, a `Prismatic` freedom `axis` alone or with
`at`, and what a freedom leaves out the moving frame supplies (see
"A mate gives the moving child a joint"). The freedom's `range` SHALL be
omitted, a pair of numbers, a pair whose bounds are numbers, `None`, or
functions of the coordinate's own value, or `Bound(expression, reads=(...))`,
or one function of the assembly that states the mate returning such a pair.
A Bound's read scope SHALL be the declaring assembly under "A moving mate's
range reads the assembly that declares it".

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
- a fixed end on a child another mate places, a rigid mate included,
  because this version places a class's mates in declaration order and
  orders no mate before another; the refusal SHALL name the mate that
  places the fixed child and SHALL NOT say that a rigidly held child
  moves;
- either end on a child held in a list or declared with `.repeat()`;
- a second mate whose moving end is a frame of a child another mate
  already places, which is a loop;
- a mate that names a child the class — or, for an inherited mate, the
  subclass — no longer declares as the one the mate was written against;
- a mate that is left unnamed -- a mate with a freedom because its
  coordinate is named after the mate, a rigid mate because a mate is
  enumerated, read and refused by its name;
- a freedom that is neither a `Revolute` nor a `Prismatic` — an `Orbit`
  or a `Free` —, a freedom whose range is neither a pair nor a function, or
  holds a parameter token or a formula, or a freedom already declared on
  some class;
- a freedom whose stated `axis` is neither three numbers nor a function,
  or whose stated `at` is not three numbers — a parameter token or a
  formula in either, which would be resolved by name against the moving
  child although it is written in the assembly, or a function in `at`,
  which this version does not accept —, or whose stated `axis` of three
  numbers has no length.

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

#### Scenario: A mate's freedom is a revolute, a prismatic or none

- **WHEN** an assembly states
  `art3.hinge.on(elbow_pin, Orbit(axis=(0, 0, 1)))`, or
  `art3.hinge.on(elbow_pin, Free())`
- **THEN** creating the class raises, naming the mate and saying which
  freedoms a mate accepts in this version: a `Revolute` or a
  `Prismatic`, or none at all for a part that is held

#### Scenario: A gripper's finger is one statement

- **WHEN** a palm declares `left_seat = Frame(at=(81.7, 21, 0))` and the
  child `left_finger = Finger()`, `Finger` declaring `origin = Frame()`,
  and states `left_grip = left_finger.origin.on(left_seat,
  Prismatic(axis=(0, 1, 0), range=(-11, 20), unit='mm'))`
- **THEN** the class is created and reports one mate named `left_grip`,
  moving `left_finger.origin` onto `left_seat`

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

#### Scenario: A bought part is held by one statement

- **WHEN** a shin assembly declares
  `servo_seat = Frame(at=(-0.98, -4, -7), z=(1, 0, 0), x=(0, 0, 1))` and
  the child `servo = Servo()`, `Servo` declaring
  `ears = Frame(at=(0, -5.5, 0))`, and states
  `bolted = servo.ears.on(servo_seat)`
- **THEN** the class is created and reports one mate named `bolted`,
  moving `servo.ears` onto `servo_seat`, with no freedom

#### Scenario: A rigid mate has a name

- **WHEN** the shin states `servo.ears.on(servo_seat)` bare, without
  assigning it
- **THEN** creating the class raises, naming the statement and asking
  for an assignment, and saying a mate is read and refused by its name

#### Scenario: A fixed end on a held sibling is refused

- **WHEN** the shin also declares `screw = Screw()`, `Screw` declaring
  `head = Frame()`, `Servo` declaring `ear_near = Frame(at=(-14, -5.5,
  0))`, and states `screwed = screw.head.on(servo.ear_near)` beside
  `bolted`
- **THEN** creating the class raises, naming `screwed`, `servo` and the
  mate `bolted` that places it, and does not say that `servo` moves

### Requirement: A mate's freedom may be a function of the assembly that states it

The system SHALL accept, as a mate's freedom's `axis` and as its
`range` — a `Revolute`'s or a `Prismatic`'s alike —, each as a whole, one function of one argument — a callable that
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
a `Bound` with reads scoped to the assembly declaring the mate. Returned
Bound reads SHALL follow "A moving mate's range reads the assembly that
declares it" without reading their values during realization. The joint the mate gives the
moving child SHALL then resolve, normalize and refuse that result as it
resolves, normalizes and refuses the same numbers written in the
freedom, so a function returning the numbers a freedom could state gives
the child the joint those numbers give.

A function that raises, or whose result is not what the numbers form
takes — a sequence of another length, a string, a `bool`, a parameter
token or a formula, a function, an axis of zero length, a range that is
not a pair or holds a bound that is not a number, `None`, a function of
the coordinate or a `Bound` — SHALL be
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
  `(0,)` or `(True, 90)` or a pair holding an invalid bound,
  or either function raises
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

#### Scenario: A sliding freedom's axis may be a function

- **WHEN** an assembly declaring `left = Flag(True)` and
  `seat = Frame(at=lambda node: (81.7, 21 if node.left else -21, 0))`
  states `grip = finger.origin.on(seat, Prismatic(axis=lambda node:
  (0, 1, 0) if node.left else (0, -1, 0), range=(-11, 20), unit='mm'))`,
  and it is realized once with `left=True` and once with `left=False`
- **THEN** each finger's joint is a `Prismatic` resolving with axis
  `(0, 1, 0)` and `(0, -1, 0)` respectively, and bound to 10 each finger
  translates 10 along its side's axis inside its side's rest translation

## ADDED Requirements

### Requirement: A moving mate's range reads the assembly that declares it

Either side of a Revolute or Prismatic mate freedom's range SHALL accept the existing Bound(expression, reads=(...)) vocabulary. The expression SHALL receive the generated joint's own coordinate first and declared reads in written order. Reads SHALL be checked within the assembly that declares the mate and resolved against that realized assembly when needed, including inherited declarations. Its axis, anchor, placement order and rest frame SHALL retain their existing meanings in the moving child's frame. This SHALL apply both to a written range pair and a pair returned by the existing whole-range function of the assembly; the function SHALL retain its once-per-instance timing. Read coordinates SHALL NOT be evaluated during child realization, so a valid read through a later declared sibling SHALL be supported. Non-mate joint declarer scopes SHALL remain unchanged.

#### Scenario: The crank freedom reads its sibling pawl

- **WHEN** a Curta-shaped assembly states a revolute crank mate with an upper Bound reading its anti-reversal pawl's turn
- **THEN** the bound uses that assembly's pawl at evaluation, the own argument is the generated crank joint's coordinate, and the existing stop and release behavior applies

#### Scenario: A range factory returns a Bound

- **WHEN** a mate's whole-range function returns a pair containing a Bound with declared assembly-scoped reads
- **THEN** the function runs once with the realized assembly, its returned reads receive the same scope and validity checks, and later bindings do not call the factory again

#### Scenario: A later sibling can be read

- **WHEN** a mate freedom's Bound names a coordinate on a sibling realized after the moving child
- **THEN** creating the child does not read the sibling's value and evaluation resolves it once the complete assembly exists

#### Scenario: Two assemblies keep independent bound reads

- **WHEN** two instances of an assembly have different pawl positions, including instances of a subclass inheriting the mate
- **THEN** each crank range reads its own assembly's pawl and no read cache or range metadata leaks between instances

#### Scenario: Invalid returned reads are refused

- **WHEN** a whole-range factory returns a Bound reading an out-of-scope declaration or the mate's own generated coordinate
- **THEN** the assembly is refused when that returned declaration becomes available, naming the mate and invalid read
