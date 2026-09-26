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
required. `at`
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
