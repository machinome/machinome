## ADDED Requirements

### Requirement: A mate's coordinate is an end of a relation like a joint's

A coordinate a mate owns (see the `mates` capability) SHALL be an end of
a relation, a term of a derived coordinate, the target of a driver's
`drives` and a source a law reads, under exactly the rules a joint's
coordinate follows: named bare in the class body of the assembly that
declares the mate, as `elbow.drives(belt.travel, ratio=...)` or
`drive = shoulder + ratio * art2.elbow`, and by a path reference from any
assembly above it, as `art3.drives(shoulder.art2.elbow)`. It SHALL be
checked at class definition as a joint's coordinate is, so a relation
naming it from a class that does not declare it, or by a path that does
not reach it, SHALL be refused by the existing rules.

The joint a mate installs on the moving child SHALL NOT be a second
address for the same freedom: a relation, a driver or an author's
`simulate()` that BINDS it by a path through the child SHALL be refused
when it binds, naming the mate's coordinate as the one to bind. Reading
it as the source of a relation SHALL be allowed, as reading a wired
coordinate is.

#### Scenario: A root drives a mated freedom by path

- **WHEN** a root declares `art3 = Driver(default=0, unit='deg')` and
  states `art3.drives(shoulder.art2.elbow)`, where `elbow` is a mate
  declared by the upper arm the housing `shoulder` holds as `art2`
- **THEN** the class is created, and binding `art3=-90` turns the
  forearm root -90 degrees about the mated line

#### Scenario: A derived coordinate reads a mated freedom

- **WHEN** a housing declares the mate `shoulder` and states
  `drive = shoulder + 5.85 * art2.elbow`, `elbow` a mate of `art2`, and
  both mate coordinates are bound
- **THEN** `drive` reads the linear combination of the two bound values

#### Scenario: Binding the installed joint by path is refused

- **WHEN** a root states `angle.drives(arm.art3.elbow)`, where `elbow` is
  the joint a mate of `arm` installed on `art3`, and binds `angle`
- **THEN** the binding is refused, naming `arm.elbow` as the coordinate
  to bind
