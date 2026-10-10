## MODIFIED Requirements

### Requirement: A joint is stated in the frame of whoever declares it

A joint's `axis`, its anchor `at` and every further point or direction it
declares SHALL be read in the frame of the DECLARER: the site the joint
declaration is written at decides the frame its arguments mean.

A joint declared in a CLASS BODY, as a class attribute of the node it
moves, SHALL be stated in the REST FRAME of THAT BODY: the frame the
body's own `render()` states its geometry in, which differs from the
frame its parent places it in by exactly the rest placement and by
nothing else. Because a joint's operations are placed INNERMOST, before
every rest operation, the rest frame is the frame every joint operation
of that body is read in, whatever other motion is composed outside them;
a joint's line SHALL therefore be unaffected by the body's other
freedoms and by any hand-written motion applied to it.

Its `at` SHALL default to `(0, 0, 0)`, the body's OWN ORIGIN, so a joint
whose line runs through the body's origin is written with no anchor at
all and turns that body where its parent put it. The framework SHALL NOT
transform a class-declared joint's arguments in any way before using
them: they are already in the frame the joint's operations are placed in.

A body its parent ROTATES therefore carries its joint line WITH it: the
line a class-body joint states is fixed in the body, so one class placed
at several sites, or at different attitudes, states one joint and gets
the right line at every site.

A CLASS-declared joint's arguments SHALL NOT depend on the node's rest
placement in any way: such a joint SHALL be placeable on a body whose
rest placement carries a value the framework cannot evaluate numerically,
and two instances of one class placed differently SHALL resolve identical
arguments for it.

A joint declared at a DECLARATION SITE — passed as a keyword where a
parent declares a child, see "A joint declared where a child is placed" —
SHALL be stated in the frame of the DECLARING PARENT: the frame that
parent's own `render()` states its geometry in, which is the frame the
parent's `translate` and `rotate` on that child are written in. URDF's
rule, where a `<joint><origin>` is stated in the parent link's frame.

Its `at` SHALL default to `(0, 0, 0)`, the DECLARING PARENT's own origin,
which is the same sentence as a class-declared joint's default read at
the other site. For a child the parent TRANSLATES, that default names a
line through the PARENT's origin and not through the child's, so such a
child SWINGS about the parent's origin rather than turning on its own
centre; that is the case a parent states when it declares a joint on a
child it has placed off the line.

An `Orbit` declared at a declaration site SHALL be the one exception, and
only for its `carries`, which names a point OF THE BODY rather than a
point of the line: a WRITTEN `carries` SHALL be a point of the declaring
parent's frame like `at`, and a DEFAULTED `carries` SHALL be the CHILD's
own origin. A `Free` declared at a declaration site SHALL float against
the declaring parent's frame: its three rotational directions are that
parent's x̂, ŷ, ẑ and its three translational coordinates displace along
those same directions.

The framework SHALL carry a site-declared joint's resolved directions and
points into the child's own rest frame, by inverting the child's rest
placement, at the moment of binding — because a joint's operations are
placed innermost and the arguments are stated one placement out. Where
that rest placement carries a value the framework cannot evaluate
numerically, the binding SHALL be refused by name, naming the node, the
joint and the operation at fault; a CLASS-declared joint on the same body
is unaffected, because nothing about it is carried.

The framework SHALL normalize a declared `axis` to unit length and SHALL
snap the normalized axis as a whole: an axis whose every component lies
within `1e-9` of `0`, `1` or `-1` — an axis within `1e-9` of a principal
axis — SHALL be exactly that axis, its components the integers `0`, `1`
and `-1`; in any other axis a component within `1e-9` of `0` SHALL be the
integer `0` and no component SHALL be made `1` or `-1`. The
normalization's floating-point residue therefore never reaches the
published document as an axis of `(0, 1, 6e-17)`, and an axis a few
millionths off a principal axis resolves to the unit direction it is: the
normalized declared axis SHALL be unit to within `1e-12`. An anchor SHALL
NOT be adjusted: it is published as the author stated it.

#### Scenario: A joint through the body's own origin needs no anchor

- **WHEN** a pinion class declares `turn = Revolute(axis=(0, 0, 1),
  unit='deg')`, its parent's `render()` places it with
  `translate([40, 25, 0])`, and the coordinate is bound to an angle
- **THEN** the pinion's motion is ONE rotation about `[0, 0, 1]` in its
  own frame with no centring translations, and the pinion spins on its
  own bearing where the parent put it rather than swinging about the
  parent's origin

#### Scenario: One class, several placements, one declaration

- **WHEN** one gear class declaring `turn = Revolute(axis=(0, 0, 1),
  unit='deg')` is instantiated four times and its parent places each copy
  at a different point, and all four coordinates are bound to the same
  angle
- **THEN** every copy spins about the line through its own placed origin,
  the four resolve the same joint arguments, and no copy needed an anchor
  its class could not know

#### Scenario: The line turns with the body

- **WHEN** a body whose parent places it with `rotate(90, [1, 0, 0])`
  declares `turn = Revolute(axis=(0, 0, 1), unit='deg')` and is bound
- **THEN** the published rotation's axis is `[0, 0, 1]` exactly, and the
  body turns about the direction its own frame calls `z`, which the
  parent's placement has carried onto the parent's `-y`

#### Scenario: A rest placement the framework cannot evaluate no longer prevents a joint

- **WHEN** a node whose rest placement carries a symbolic value has a
  CLASS-declared joint bound
- **THEN** the body is placed about the line its own frame states, and
  nothing is refused

#### Scenario: A joint stated where the child is placed anchors on the parent's origin

- **WHEN** a motor drive declares
  `screws = LockScrew(orbit=Revolute(axis=(0, 0, 1), unit='deg')).repeat(2)`
  and its `render()` places the two copies at `[0, +3.9, z]` and
  `[0, -3.9, z]`, and both coordinates are bound to the same angle
- **THEN** both screws are carried round the line through the MOTOR
  DRIVE's own origin at a radius of 3.9, not turned on their own centres,
  and the declaration wrote no anchor, no sign and no index

#### Scenario: One site declaration serves opposed placements

- **WHEN** a winch declares
  `rollers = RollerBearing(spin=Revolute(axis=(0, 1, 0), at=SHAFT_POINT, unit='deg')).repeat(2)`
  and places the copies with `rotate(90, [1, 0, 0])` and
  `rotate(-90, [1, 0, 0])`, and both are bound to the same angle
- **THEN** each copy turns about the winch-frame line the declaration
  states, the two copies' own-frame axes being opposite, and one
  declaration served both placements

#### Scenario: A defaulted carried point at a site is the child's own origin

- **WHEN** a drive declares
  `disk = CycloidalDisk(orbit=Orbit(axis=(0, 0, 1), unit='deg'))` and
  places the disk at `translate([0, -2.5, 0])`, and the coordinate is
  bound
- **THEN** the disk's own origin travels the circle of radius 2.5 about
  the line through the DRIVE's origin, its attitude unchanged, and
  neither the radius nor the phase was written

#### Scenario: A site joint on a rest placement the framework cannot evaluate is refused

- **WHEN** a parent places a child with a translation carrying a symbolic
  value and binds a joint it declared at that child's declaration site
- **THEN** the binding raises naming the node, the joint and the
  operation whose value is not a number, and a class-declared joint on
  the same body still binds

#### Scenario: An axis within the snap of a principal axis resolves to exact integers

- **WHEN** a class declares `turn = Revolute(axis=(0, 0, 3), unit='deg')`
  and `tilt = Revolute(axis=(1e-12, 1, 0), unit='deg')` and an instance
  is realized
- **THEN** `turn`'s resolved axis is `(0, 0, 1)` and `tilt`'s is
  `(0, 1, 0)`, every component an integer

#### Scenario: An axis a few millionths off a principal axis resolves unit

- **WHEN** a class declares
  `turn = Revolute(axis=(0, -0.9999999999799858, 6.326794896668469e-06), unit='deg')`
  — the axis a URDF's `rpy="1.57079 0 0"` turns `z` onto — and an
  instance is realized
- **THEN** the resolved axis has length `1` within `1e-12` and equals the
  declared axis within `1e-15`, its first component is the integer `0`
  and its second is not the integer `-1`

#### Scenario: A mate's joint turns about its moving frame's z a few millionths off an axis

- **WHEN** an assembly states `turn = link.hinge.on(pin, Revolute())`,
  where the link's class declares
  `hinge = Frame(z=(0, -0.9999999999799858, 6.326794896668469e-06), x=(1, 0, 0))`,
  and the assembly is realized
- **THEN** the link's `turn` joint's resolved axis has length `1` within
  `1e-12` and equals the link's resolved `hinge` frame's `z` within
  `1e-15`, component for component
