# mates Specification

## Purpose
TBD - created by archiving change place-parts-by-mate. Update Purpose after archive.
## Requirements

### Requirement: A mate attaches frames through an existing child joint

The system SHALL accept `moving_child.frame.on(fixed_frame, moving_child.joint)` in an assembly class body where the explicit declaration reference names an existing one-coordinate Revolute or Prismatic joint on that exact directly declared moving child. It SHALL accept a class-declared or declaration-site joint, including a supported inherited joint, with its existing name and unit. The mate SHALL place the frames by the existing rest-placement rule and SHALL reuse the joint rather than install, rename, replace, reorder or mutate it. Its axis, anchor, range, arguments, original class/site frame and Bound read declarer SHALL be preserved. The frame SHALL not supply axis or anchor defaults to the referenced joint. Class-shared joint metadata and existing child specialization SHALL not be changed by attachment.

The mate name SHALL name the attachment handle only and SHALL not be required to be a free attribute name on the child. Existing end scope, one mate per moving child, fixed-end, inheritance, list/repeat and render-placement restrictions SHALL remain. Strings, a bare foreign class Joint declaration, implicit whole-node selection, another child's joint, deeper descendant joints, ports, derived coordinates, Orbit, Free or components of multi-coordinate joints SHALL be refused by name. No joint_name keyword or other naming-string API SHALL be introduced.

#### Scenario: The complete declared-reference example runs

- **WHEN** the following declarations are realized and rendered

```python
from machinome.node import AssemblyNode, Frame
from machinome.motion.joints import Revolute

class Dial(AssemblyNode):
    axle = Frame()
    turn = Revolute(axis=(0, 0, 1))

class Register(AssemblyNode):
    ones_seat = Frame(at=(10, 0, 0))
    ones = Dial()
    ones_mount = ones.axle.on(ones_seat, ones.turn)
```

- **THEN** ones rests with its axle at (10, 0, 0), its original turn joint remains, and no ones_mount joint or assembly coordinate is created

#### Scenario: Sibling dials retain their repeated local names

- **WHEN** a register attaches two children with uniquely named mates referencing each child's turn joint
- **THEN** the original ones.turn and tens.turn endpoints remain distinct and neither is renamed after its mate

#### Scenario: A site joint keeps its original scope and carried line

- **WHEN** a child is declared with a site Revolute or Prismatic whose arguments and Bound read the declaring parent, then attached through that explicit child-joint reference
- **THEN** its original resolved arguments, parent frame/carry, bound reads and joint order remain unchanged and no mate-generated scope replaces them

#### Scenario: A class joint keeps its own Bound scope

- **WHEN** a class-declared joint's Bound reads that child's declared coordinate and the parent attaches its frames through that joint
- **THEN** the read still resolves in the child and a same-named parent coordinate cannot substitute for it

#### Scenario: Joint metadata stays independent of attachment sites

- **WHEN** two assemblies attach instances of the same child class at different frames and a third instance remains unattached
- **THEN** each original joint's name, owner, arguments and order are unchanged and attachment state does not leak into another instance or class

#### Scenario: An invalid joint reference is refused

- **WHEN** the attachment names another child's joint, a deeper descendant, a whole node, a string, a port, an Orbit or a Free coordinate
- **THEN** it is refused naming the reference and the requirement for an explicit scalar Revolute or Prismatic of the moving child

#### Scenario: Existing placement restrictions remain

- **WHEN** a reused-joint mate closes a second mate on the same child, uses a moving fixed sibling, or the parent render also places that child
- **THEN** the existing named refusal applies

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

When BOTH `x` and `z` are explicitly supplied, resolution SHALL preserve
full floating-point precision of the normalized `z`, projected and normalized
`x`, and cross-product `y`, without snapping direction components to `0`, `1`
or `-1`. This includes literal, parameter/formula and callable vectors, and
an explicitly supplied `z=(0, 0, 1)`. Supplying `x` while omitting `z` SHALL
retain the previous snapped path, as SHALL omitting `x` (including `x=None`).
On that path, direction components within `1e-9` of `0`, `1` or `-1` SHALL be
that integer. No new public argument SHALL select this behavior. Projection,
normalization and zero/parallel refusal thresholds SHALL remain unchanged.
This precision rule SHALL NOT alter final mate rotation-angle/axis snapping.

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

#### Scenario: Curta's explicit attachment directions retain precision

- **WHEN** a frame explicitly supplies
  `x=(-3.2740476996195866e-13, 3.6046641539722035e-10, 1)` and
  `z=(.9999983500045653, .0018165869499783267, -3.2740476996195866e-13)`
- **THEN** its directions are normalized, projected and crossed without
  replacing genuine tiny components by snapped integers

#### Scenario: Explicit expressions retain the same direction precision

- **WHEN** both `x` and `z` are supplied as parameter/formula vectors or
  whole-vector callables resolving to near-principal directions
- **THEN** the same unsnapped normalization/projection rule applies per instance

#### Scenario: Explicit x with default z keeps the old snapped path

- **WHEN** a frame supplies `x=(1, 3e-10, 0)` but omits `z`
- **THEN** it retains snapped directions, while explicitly supplying the same
  default `z=(0, 0, 1)` with that x retains its normalized tiny component

#### Scenario: Omitted x retains principal inference

- **WHEN** x is omitted or None and z has near-principal components inside
  the existing snap threshold
- **THEN** the prior snapped principal direction and inferred x remain, and
  nonprincipal z outside that rule is still refused for lacking x

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
and, when stated as a fresh freedom, SHALL be a `Revolute`, `Revolute(range=(lo, hi), unit='deg')`,
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

The FREEDOM SHALL also accept an explicit declaration reference to an
existing scalar Revolute or Prismatic joint of that same directly declared
moving child, under "A mate attaches frames through an existing child joint".
Such a reference reuses the joint and does not state a fresh freedom; its
original arguments and scope are preserved.

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
- a fresh freedom that is neither a `Revolute` nor a `Prismatic` — an `Orbit`
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

Matrix-to-axis-angle conversion SHALL preserve the represented rest rotation,
subject to the unchanged documented `1e-9` snap, without amplifying
cancellation residue into phantom axis components. Signed
principal rotations beyond 90 degrees SHALL retain their principal axis;
genuine small axis components outside the existing snap SHALL remain present.
Near and exact half-turn rotations SHALL remain numerically stable, and
symmetric equal-component half-turns SHALL retain equal axis components. This
SHALL NOT enlarge the snap or alter caller tolerances.

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

#### Scenario: Curta's negative principal rest rotation stays principal

- **WHEN** a mate's rest matrix is a pure Z rotation of -95.6 degrees, as in
  Curta selector 6
- **THEN** its emitted rotation has zero X/Y axis components and represents
  the same signed Z rotation, without the phantom approximately 5e-9 components
- **AND** the unchanged caller physical-basis comparison meets its existing
  tolerance

#### Scenario: Genuine small components are not erased

- **WHEN** a proper rest rotation beyond 90 degrees has a genuine small axis
  component outside the existing 1e-9 snap
- **THEN** conversion preserves that component rather than treating it as
  cancellation noise, and reconstructs the rotation within floating-point
  accuracy subject to the unchanged documented snap of axis components and angle

#### Scenario: Near and exact half turns retain their rotation

- **WHEN** rest rotations approach or reach 180 degrees about principal or
  mixed-sign oblique axes, including symmetric equal-component axes
- **THEN** the emitted rotations reconstruct the represented matrices within
  floating-point accuracy subject to the unchanged documented snap of axis
  components and angle, and preserve equal components in symmetric half turns

### Requirement: A mate gives the moving child a joint

At realization the moving child of a mate that states a fresh freedom SHALL
move about a joint of the freedom's kind — a `Revolute` for a `Revolute` freedom, turning the
child about the line, a `Prismatic` for a `Prismatic` freedom, sliding
the child along it — whose axis is the freedom's stated `axis` — the three numbers written, or what
its function returned for the realized assembly —, or, for a
`Revolute` freedom only, the moving frame's `z` when the freedom states
none, a `Prismatic` freedom always stating its axis, and whose anchor is the freedom's
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

A mate referencing an existing child joint SHALL generate no joint and
shall not apply its mate name to the child; it SHALL preserve the original
joint under "A mate attaches frames through an existing child joint".

A child a mate moves SHALL keep its identity: it SHALL key the same
artifacts as the same child declared with no mate, and its class SHALL
report the declared class's name.

A rigid mate SHALL give the moving child no joint: the child SHALL be
realized as its declared class itself, not a specialization of it, and
its class SHALL report exactly the joints that class declares.

A mate stating a fresh freedom whose name the moving child's class already
answers to — a
parameter, a child, a port, a joint, a frame, a marking, a method or any
other attribute — SHALL be refused when the assembly's class is created,
naming the assembly, the mate, the child's class and what it already
declares. A rigid mate's name SHALL NOT be checked against the moving
child's class, since the rigid mate gives the child nothing under it.

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

#### Scenario: A finger's joint is the one the gripper writes by hand

- **WHEN** the palm of "A gripper's finger is one statement" is realized,
  and its `left_grip` is bound to 10
- **THEN** the finger's class reports a `Prismatic` joint `left_grip`
  with axis `(0, 1, 0)`, anchor `(0, 0, 0)`, range `(-11, 20)` and unit
  `'mm'`; unbound, the finger's operations are one translation
  `(81.7, 21, 0)`; at 10 they are a translation of 10 along `(0, 1, 0)`
  then that translation, equal in kind, order and value to those of a
  finger whose class declares `travel = Prismatic(axis=(0, 1, 0),
  range=(-11, 20), unit='mm')` placed by the palm's `render()` with
  `translate(81.7, 21, 0)` and bound to 10

#### Scenario: A slide states its axis

- **WHEN** a part declaring `slot = Frame(z=(0, 1, 0), x=(1, 0, 0))` is
  mated onto `seat = Frame(at=(0, 0, 5), z=(0, 1, 0), x=(1, 0, 0))` with
  `Prismatic(axis=(1, 0, 0), range=(0, 10))`, and bound to 4; and a
  freedom is written `Prismatic(range=(0, 10))`, with no axis
- **THEN** the part's joint is a `Prismatic` whose line is the stated
  axis `(1, 0, 0)`, read in the part's own rest frame, through its
  anchor, the moving frame's origin — not the moving frame's `z` — and
  its operations are a translation of 4 along `(1, 0, 0)` then the rest
  translation `(0, 0, 5)`; and `Prismatic(range=(0, 10))` is refused as
  a `Prismatic` without an axis is refused anywhere, by its constructor,
  before any mate is stated — the mate adds no refusal of its own

#### Scenario: A slide's stated anchor moves nothing

- **WHEN** a finger is mated once with `Prismatic(axis=(0, 1, 0),
  at=(0, 0, 5), range=(-11, 20))` and once with `Prismatic(axis=(0, 1,
  0), range=(-11, 20))`, and each is bound to 10
- **THEN** the first joint's anchor is `(0, 0, 5)` and the second's the
  moving frame's origin, and the two fingers' operations are equal

#### Scenario: A mate cannot hide a child's attribute

- **WHEN** the forearm root's class already declares a joint `elbow` and
  the upper arm states `elbow = art3.hinge.on(elbow_pin, Revolute())`
- **THEN** creating the upper arm's class raises, naming the upper arm,
  the mate, the forearm root's class and its joint `elbow`

#### Scenario: A mated child keys its unmated artifacts

- **WHEN** a part is realized once as a mated child and once as an
  unmated child with the same arguments
- **THEN** both realized parts have the same identity

#### Scenario: A held part gets no joint

- **WHEN** the shin of "A bought part is held by one statement" is
  realized
- **THEN** its servo is an instance of `Servo` itself, the joint
  enumerator reports for `type(shin.servo)` exactly the joints `Servo`
  declares, and the servo has the identity of a `Servo` declared with no
  mate

### Requirement: A mate owns a coordinate on the assembly

A mate with a fresh freedom SHALL own one coordinate on the declaring
assembly, named after the mate, of the freedom's kind — rotational for a
`Revolute`, translational for a `Prismatic` — and carrying the freedom's
unit, `'deg'` or `'mm'` when it states none. It SHALL be reported by the port enumerator for the assembly's
class, SHALL read and bind on an instance as a joint's coordinate does,
and SHALL be an end of a relation, a target of a driver and a source of
a law as the `couplings` capability specifies.

Whenever the fresh-freedom mate's coordinate is bound, the child's joint SHALL take its
value, subject to the freedom's range, by the end of the assembly's
simulate phase, and the child's body SHALL be placed exactly as a
binding of that joint places it. Whenever the mate's coordinate is
unbound, the child's joint SHALL be unbound and the child SHALL rest at
the mate's rest placement, exactly as a body with an unbound joint rests
— an unbound mate coordinate SHALL NOT be refused.

The joint a fresh-freedom mate gives the child SHALL be bound only through the mate's
coordinate: binding it by any other route — an assignment on the child,
a relation or a driver naming it by path — SHALL be refused, naming the
mate's coordinate as the one to bind.

A mate referencing an existing joint SHALL own no assembly coordinate;
its instance reads, bindings and declaration references SHALL reach the
original child joint under "A reused-joint mate handle shares the child slot".
The fresh-freedom exclusive wiring refusal SHALL NOT apply to a reused joint.

A rigid mate SHALL own no coordinate. The port enumerator SHALL NOT
report it. Reading it on an instance SHALL yield the mate declaration,
as reading a frame on an instance yields the frame. Assigning to it on
an instance SHALL raise `AttributeError`, naming the assembly and the
mate and saying it states no freedom and owns no coordinate. Naming it
where a coordinate is named -- an end of a relation or of a derived
coordinate in the class body that states it, a wiring source, or a path
reaching it from an assembly above -- SHALL be refused where the
statement is written or when the class stating it is created, naming
the mate and saying a rigid mate owns no coordinate.

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

#### Scenario: A finger's coordinate is a translational port

- **WHEN** a consumer enumerates the ports of the palm of "A gripper's
  finger is one statement"
- **THEN** it receives `left_grip`, a translational coordinate in
  millimetres

#### Scenario: A gripper's mimic relates two mates

- **WHEN** a palm mates `left_finger` by `Prismatic(axis=(0, 1, 0),
  range=(-11, 20), unit='mm')` as `left_grip` and `right_finger` onto
  `right_seat = Frame(at=(81.7, -21, 0))` by `Prismatic(axis=(0, -1, 0),
  range=(-11, 20), unit='mm')` as `right_grip`, states
  `left_grip.drives(right_grip)`, and a root declaring
  `grip = Driver(default=0, unit='mm')` holds the palm under an
  intermediate assembly `wrist` and states
  `grip.drives(wrist.palm.left_grip)`
- **THEN** bound to `grip=10`, the left finger translates 10 along
  `(0, 1, 0)` and the right finger 10 along `(0, -1, 0)`, each inside its
  rest translation; bound to `grip=25`, the binding is refused naming
  `left_grip` and its range

#### Scenario: A rigid mate is not a port

- **WHEN** a consumer enumerates the ports of the shin of "A bought part
  is held by one statement"
- **THEN** it receives nothing for `bolted`

#### Scenario: A rigid mate is read, not bound

- **WHEN** `shin.bolted` is read on a realized shin, and then
  `shin.bolted = 10` is assigned
- **THEN** the read yields the mate `declared_mates` reports under
  `bolted`, and the assignment raises `AttributeError` naming the shin's
  class and `bolted` and saying it owns no coordinate

#### Scenario: A rigid mate is not a relation's end

- **WHEN** the shin's body states `bolted.drives(travel)` over a port
  `travel` it declares; or it declares a child `wheel =
  Wheel(spin=bolted)`, `Wheel` declaring the joint `spin`, wiring the
  mate into it; or a root declaring `angle = Driver(default=0)` and the
  child `shin = Shin()` states `angle.drives(shin.bolted)`
- **THEN** each is refused, naming `bolted` and saying a rigid mate owns
  no coordinate

### Requirement: A mate publishes nothing new

A fresh-freedom mated machine's published document SHALL carry the mate's compiled
rest placement as ordinary operations and its coordinate as an ordinary
binding, SHALL declare the document version a machine without mates
declares, and SHALL add no field. A machine that declares no frame and
no mate SHALL publish a document byte-identical to the one it published
before frames and mates existed, and a mated machine whose mates' freedoms
state no line SHALL publish a document byte-identical to the one it
published before a freedom could state one. A mate whose freedom states
its line SHALL publish that line only as the axis and anchor of the
joint's ordinary operations, and a mate whose freedom is a `Prismatic`
SHALL publish its slide only as the translation of the joint's ordinary
operations. A rigid mate SHALL publish its placement only as the held
child's ordinary operations, and no binding.

An existing-joint attachment SHALL publish its frame placement as ordinary
rest operations and its original joint's existing binding under its original
qualified path. Its mate handle SHALL add no binding address, bank entry,
identity wiring, field or document version.

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

#### Scenario: A sliding mate publishes a slide as operations

- **WHEN** the root of "A gripper's mimic relates two mates" is exported,
  and so is its hand-placed twin, whose finger classes declare
  `travel = Prismatic(axis=(0, ±1, 0), range=(-11, 20), unit='mm')`,
  whose palm's `render()` translates each finger to its seat and states
  `left_finger.travel.drives(right_finger.travel)`, and whose root's
  `grip` drives the left finger's `travel`
- **THEN** the two documents declare the same version and the same
  top-level keys, no node entry of the mated document has a key the
  twin's lacks, and each finger's operations equal the twin's, the
  translation driven by `grip` included

#### Scenario: A held part publishes as operations

- **WHEN** a root turning the shin of "A bought part is held by one
  statement" by a revolute mate is exported, and so is its hand-placed
  twin, whose shin's `render()` places the servo by
  `rotate(90, [0, 1, 0])`, `rotate(180, [1, 0, 0])` and
  `translate(-0.98, -9.5, -7)`
- **THEN** the two documents declare the same version, the same
  top-level keys and the same drivers and bindings, no node entry of the
  mated document has a key the twin's lacks, and every leaf's composed
  placement equals the twin's within `1e-9`; the servo's operations
  differ from the twin's only in form -- one rotation of 180 about
  `(0.7071…, 0, 0.7071…)` where the twin writes two

### Requirement: A realized node reads its resolved frames

The system SHALL provide `resolved_frames(node)`, importable from
`machinome.node.frames` beside `declared_frames`, documented in the
framework's API reference. Given a realized node, it SHALL return a
mapping from the name of every frame the node's class declares, in
declaration order, to that frame as it resolved against the node (see "A
frame resolves against its declarer at realization"): an origin `at` and
three unit directions `x`, `y`, `z`, each a tuple of three plain
numbers in the node's own rest frame, and a `rotation()` giving the 3×3
matrix, as three rows, whose columns are `x`, `y` and `z`. `at` SHALL be
three floats. When both direction vectors were explicitly supplied, their
normalized/projected/cross-product components SHALL retain full floating-point
precision as required by frame resolution; otherwise a direction component
within `1e-9` of `0`, `1` or `-1` SHALL be that integer.

The read SHALL be exactly what a mate composes with: the same resolution
made once when the node was constructed, not a second one, so a function
of the node given as a frame argument SHALL NOT be called by the read.
Each read SHALL return a new mapping, and changing that mapping SHALL
change nothing the node or its mates use. Reading SHALL change no node,
no identity, no artifact and no published document.

A node whose class declares no frame SHALL read an empty mapping; a
frame a subclass removed by assigning `None` SHALL NOT appear. A child
placed by a mate SHALL read the frames its declared class declares.

The read SHALL be refused, raising `TypeError`:

- given a class, naming the class and saying a frame resolves against
  the instance that declares it — its arguments may read that instance's
  parameters or be a function of it — and that the declarations are read
  with `declared_frames`;
- given anything that is not a realized node — a child declaration read
  off a class body, a frame, a number —, naming its type and saying the
  read takes a realized node;
- given a realized node whose frames are not yet resolved — a read made
  from its own `check()`, or from a function given as one of its joint or
  frame arguments —, naming the class and saying a node's frames resolve
  after its `check()` and its joints. From such a function the refusal
  reaches the author as the argument rule reports any error a function
  raises, quoting it.

Reading a frame as an attribute of an instance SHALL continue to yield
the declaration.

#### Scenario: A frame's numbers are read off the instance

- **WHEN** an assembly declaring `reach = Length(160)` and
  `elbow_pin = Frame(at=(0, reach, 68), z=(0, 0, 1))` is realized with
  `reach=150`, and `resolved_frames` reads it
- **THEN** the mapping holds `elbow_pin` alone, with `at` equal to
  `(0.0, 150.0, 68.0)`, `x` to `(1, 0, 0)`, `y` to `(0, 1, 0)` and `z`
  to `(0, 0, 1)`, while `declared_frames` of the class still reports the
  declaration with its `reach` token

#### Scenario: The default x is read, not restated

- **WHEN** a part declares `bore = Frame(z=(0, 1, 0))` and
  `yaw_bore = Frame(z=(0, 0, -1))`, neither stating `x`, and a realized
  part is read
- **THEN** `bore` reads `x = (0, 0, 1)` and `y = (1, 0, 0)`, and
  `yaw_bore` reads `x = (-1, 0, 0)` and `y = (0, 1, 0)`

#### Scenario: A stated x is read squared up

- **WHEN** a part declares `pin = Frame(z=(0, 0, 2), x=(1, 0, 1))` and a
  realized part is read
- **THEN** `pin` reads `z = (0, 0, 1)`, `x = (1, 0, 0)` and
  `y = (0, 1, 0)`

#### Scenario: The read is what the mate composes

- **WHEN** an upper arm declares `reach = Length(160)`,
  `elbow_pin = Frame(at=(0, reach, 68), z=(0, 0, 1))` and the child
  `art3 = Art3()`, `Art3` declaring
  `hinge = Frame(at=(0, 0, 81.5), z=(0, 1, 0), x=(1, 0, 0))`, states
  `elbow = art3.hinge.on(elbow_pin, Revolute(range=(-135, 135)))`, is
  realized with `reach=150` and rendered with `elbow` unbound, and the
  frames of the arm and of its child `art3` are read
- **THEN** `art3` reads `hinge` with `x = (1, 0, 0)`, `y = (0, 0, -1)`
  and `z = (0, 1, 0)`, and `art3`'s rest operations — a rotation of 90
  degrees about `(1, 0, 0)` and a translation of `(0, 231.5, 68)` — are
  the placement composed from the two reads as the fixed frame times the
  inverse of the moving frame

#### Scenario: A frame computed by a function is not recomputed

- **WHEN** a part declares `bore = Frame(at=lambda node: ...)` whose
  function counts its calls, and a realized part is read twice
- **THEN** both reads give the same origin and the count is what it was
  before the first read

#### Scenario: Changing a read changes nothing

- **WHEN** a key is removed from the mapping one read returned
- **THEN** a second read of the same node returns every frame, and a
  mate placed from that node's frames rests where it rested before

#### Scenario: A node declaring no frame reads nothing

- **WHEN** a leaf declaring no frame is realized and read, and a
  subclass assigning `foot = None` under a base declaring `hinge` and
  `foot` is realized and read
- **THEN** the first reads an empty mapping and the second reads `hinge`
  alone

#### Scenario: A class has no resolved frames

- **WHEN** `resolved_frames` is given the assembly class of "A frame's
  numbers are read off the instance", or its child declaration read off
  the class body
- **THEN** it raises `TypeError`; for the class naming the class and
  `declared_frames`, for the declaration naming its type and saying a
  realized node is read

#### Scenario: Frames are not read before they resolve

- **WHEN** a part declaring a frame calls `resolved_frames(self)` in its
  `check()`
- **THEN** realizing the part raises `TypeError`, naming the class and
  saying its frames resolve after `check()` and its joints

#### Scenario: The precise readout is the basis mates actually use

- **WHEN** a realized node's frame explicitly supplies both near-principal
  directions and a mate composes it with a nonidentity moving/fixed endpoint
- **THEN** `resolved_frames` exposes the same unsnapped resolved basis used in
  that actual mate composition, not a separately prettified or recomputed one
- **AND** the emitted mate rotation retains its existing final `1e-9` snap

### Requirement: A mate's ends and freedom are read off the class

A mate SHALL be readable, off the class and without constructing an
instance, as the object `declared_mates(cls)` reports under its name,
with these reads documented in the framework's API reference:

- `name`, the attribute the mate is assigned to — for a mate stating a
  fresh freedom, also the name of its coordinate on the assembly and of the
  joint it gives the child;
- `moving`, the moving end, whose `written` SHALL be
  `'<child>.<frame>'` as the class body writes it;
- `fixed`, the fixed end as the class body writes it: for a frame of a
  child, a reference whose `written` SHALL be `'<child>.<frame>'`; for a
  frame of the assembly itself, written by its bare name, that `Frame`
  declaration, whose `name` SHALL be its attribute;
- `freedom`, the exact declared child-joint reference written for a
  reused-joint mate, `None` for a rigid mate, else the fresh `Revolute` or
  `Prismatic` written in the statement,
  whose `axis` SHALL
  be `None` when no axis is stated, which only a `Revolute` freedom may
  do, the three numbers as written, not
  normalized, when numbers are stated, and the function itself, the same
  object, when a function is stated; whose `anchor_written` SHALL say
  whether `at` was written; whose `at` SHALL be the three numbers as
  written when `anchor_written` is true, and SHALL NOT be the mate's
  anchor when it is false, the anchor then being the moving frame's
  origin; whose `range` SHALL be as written — a pair, or the function
  itself, the same object — or `None`; and whose `unit` SHALL be as
  written, or `'deg'` for a `Revolute` and `'mm'` for a `Prismatic`.

A rigid mate has no line. For an existing-joint reference, the original
joint declaration gives its line, unit and range under its original
class/site scope; the reference is read as written and the mate supplies
none of its argument defaults. When a fresh freedom is stated and its `axis` is
not a function, the line a mate turns its
child about or slides it along SHALL be readable from these reads and the moving child's
resolved frames alone: `freedom.axis` when it is not `None`, else — a
`Revolute` freedom's only — the moving frame's resolved `z`; through `freedom.at` when `anchor_written`
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

#### Scenario: A sliding freedom is read as written

- **WHEN** the palm of "A gripper's finger is one statement" is read
  under `left_grip`
- **THEN** its freedom is a `Prismatic` whose `axis` is `(0, 1, 0)`,
  `anchor_written` false, `range` `(-11, 20)` and `unit` `'mm'`

#### Scenario: A rigid mate is read with no freedom

- **WHEN** `declared_mates` of the shin of "A bought part is held by one
  statement" is read under `bolted`
- **THEN** its `name` is `bolted`, its `moving.written` is
  `'servo.ears'`, its `fixed` is the shin's `servo_seat` frame with
  `name` `servo_seat`, and its `freedom` is `None`

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

### Requirement: A mate with no freedom holds a child where two frames meet

The system SHALL accept a mate whose freedom is left out,
`<child>.<frame>.on(<fixed frame>)`, called a **rigid mate**, for a part
that is held -- bolted, pressed, seated -- rather than freed. At
realization a rigid mate SHALL place the moving child at rest exactly as
"A mate places the moving child at rest" states, from the same two
frames, by the same composition, as the same one rotation and one
translation after the author's `render()` with the same `1e-9` snap, and
SHALL compile to nothing else: no joint on the child, no coordinate on
the assembly and no wiring.

A held child SHALL move only as the assembly that declares it moves. A
part declared in the class of the part that holds it, and mated onto
that class's own frame or onto a frame of a sibling that does not move,
SHALL ride with the holding part under every joint and mate above it.
The fixed end of a rigid mate SHALL follow every rule a fixed end
follows; a fixed end on a sibling that can move, or that another mate
places, SHALL stay refused.

A held child MAY itself declare joints, children and mates of its own;
the rest placement SHALL compose outside every one of them, as any
mate's rest placement composes outside the child's own joints.

Every other rule of "An assembly mates a child's frame onto another
frame" and "A mate places the moving child at rest" SHALL hold for a
rigid mate: it is named; its ends are depth one and are refused through
a list or a `repeat()`; a second mate on the held child, rigid or not,
SHALL be refused as a loop; a `render()` that also places the held child
SHALL be refused naming the assembly, the child and the mate; and a
re-running `render()` SHALL NOT stack its placement.

#### Scenario: A servo is held at its measured seat

- **WHEN** the shin of "A bought part is held by one statement" is
  realized and rendered
- **THEN** the servo's operations are a rotation of 180 degrees about
  `(0.7071…, 0, 0.7071…)` followed by a translation of
  `(-0.98, -9.5, -7)`, and its composed placement equals, within `1e-9`,
  that of a twin shin whose `render()` places the servo with
  `rotate(90, [0, 1, 0])`, `rotate(180, [1, 0, 0])` and
  `translate(-0.98, -9.5, -7)`

#### Scenario: A held part rides with the part that holds it

- **WHEN** a leg assembly declares `knee_pin = Frame(at=(0, 8, -30),
  z=(0, 1, 0))` and the shin as `shin`, the shin declaring
  `knee_bore = Frame(z=(0, 1, 0))`, and states
  `knee = shin.knee_bore.on(knee_pin, Revolute(range=(-90, 90)))`, and a
  root declaring `angle = Driver(default=0, unit='deg')` states
  `angle.drives(leg.knee)` and is bound to `angle=30`
- **THEN** the servo's composed placement equals, within `1e-9`, that of
  the twin shin's servo in a twin leg whose shin class declares
  `knee = Revolute(axis=(0, 1, 0))`, placed by the leg's `render()` with
  `translate(0, 8, -30)` and bound to 30

#### Scenario: A held part keeps its own joints inside the placement

- **WHEN** the servo's class declares `output = Revolute(axis=(0, 1, 0))`
  and the held servo's `output` is bound to 20
- **THEN** its operations are the turn of 20 about `(0, 1, 0)`, then the
  rigid mate's rest rotation and translation

#### Scenario: A held part is held once

- **WHEN** the shin states `bolted = servo.ears.on(servo_seat)` and
  `again = servo.ears.on(other_seat)`, or `bolted` and
  `swing = servo.ears.on(other_seat, Revolute())`
- **THEN** creating the class raises, naming both mates and saying a
  second mate on a placed child closes a loop

#### Scenario: A held part is not placed by hand

- **WHEN** the shin states `bolted` and its `render()` calls
  `self.servo.translate(...)`
- **THEN** rendering raises, naming the shin, `servo` and `bolted`

### Requirement: A moving mate's range reads the assembly that declares it

Either side of a fresh Revolute or Prismatic mate freedom's range SHALL accept the existing Bound(expression, reads=(...)) vocabulary. The expression SHALL receive the generated joint's own coordinate first and declared reads in written order. Reads SHALL be checked within the assembly that declares the mate and resolved against that realized assembly when needed, including inherited declarations. Its axis, anchor, placement order and rest frame SHALL retain their existing meanings in the moving child's frame. This SHALL apply both to a written range pair and a pair returned by the existing whole-range function of the assembly; the function SHALL retain its once-per-instance timing. Read coordinates SHALL NOT be evaluated during child realization, so a valid read through a later declared sibling SHALL be supported. A reused existing joint SHALL retain its original class/site Bound declarer
scope; the attachment SHALL not make its Bounds assembly-scoped or change
the receiver or timing of its original argument functions. Non-mate joint
declarer scopes SHALL remain unchanged.

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
