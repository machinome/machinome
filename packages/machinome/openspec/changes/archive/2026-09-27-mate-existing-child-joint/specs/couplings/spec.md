## MODIFIED Requirements

### Requirement: A mate's coordinate is an end of a relation like a joint's

A coordinate a fresh-freedom mate owns (see the `mates` capability) SHALL be an end of
a relation, a term of a derived coordinate, the target of a driver's
`drives` and a source a law reads, under exactly the rules a joint's
coordinate follows: named bare in the class body of the assembly that
declares the mate, as `elbow.drives(belt.travel, ratio=...)` or
`drive = shoulder + ratio * art2.elbow`, and by a path reference from any
assembly above it, as `art3.drives(shoulder.art2.elbow)`. It SHALL be
checked at class definition as a joint's coordinate is, so a relation
naming it from a class that does not declare it, or by a path that does
not reach it, SHALL be refused by the existing rules.

The joint a fresh-freedom mate installs on the moving child SHALL NOT be a second
address for the same freedom: a relation, a driver or an author's
`simulate()` that BINDS it by a path through the child SHALL be refused
when it binds, naming the mate's coordinate as the one to bind. Reading
it as the source of a relation SHALL be allowed, as reading a wired
coordinate is.

A mate referencing an existing child joint SHALL instead resolve to that
same child endpoint for every relation role and derived-coordinate term.
Its original child-joint path SHALL remain usable as a source and target,
with the same single-binder and retained self-read rules. Alias spellings
SHALL not create distinct endpoints, hide duplicate writers or create a new
identity relation. These exceptions SHALL not change fresh-freedom mates.

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

## ADDED Requirements

### Requirement: Existing-joint mate aliases obey physical endpoint identity

Bare and descendant-path references to a reused-joint mate SHALL resolve to its original child joint for sources, targets and derived-coordinate terms. Canonical endpoint comparison SHALL identify the handle, explicit child-joint path and any supported inferred-node reference as the same coordinate. Duplicate writers and repeated grouped read/target entries SHALL be refused under the existing relation rules even when their written spellings differ. A supported law reading the retained coordinate it drives SHALL retain that meaning when either side names its handle. Bound self reads SHALL remain refused rather than inherit the retained-law exception. Foreign same-name declaration references SHALL not be redirected into an unrelated tree.

#### Scenario: Mixed names do not hide two writers

- **WHEN** two relations target child.turn and its reused-joint handle
- **THEN** they are refused as writers of the same physical coordinate even when their values agree

#### Scenario: A retained law can use the handle

- **WHEN** one supported running law reads child.turn as its retained source and targets the reused-joint handle, or reads the handle and targets child.turn
- **THEN** it retains the same original endpoint and self-read integration behavior rather than creating a cycle between two values

#### Scenario: Derived expressions use the same endpoint

- **WHEN** a derived expression combines a reused-joint handle and its child-joint reference
- **THEN** both terms resolve the same original value with the original domain/unit and existing linear-expression arithmetic

#### Scenario: A wiring source can read the handle

- **WHEN** a permitted downward wiring uses a reused-joint mate handle as its source
- **THEN** it reads the original child coordinate under existing wiring ordering/unbound rules without creating an alias slot or an additional writer of the original joint

#### Scenario: Duplicate grouped aliases are refused

- **WHEN** one grouped end lists both the handle and child joint for the same physical coordinate
- **THEN** the existing duplicate-coordinate refusal identifies them rather than handing the law that coordinate twice

#### Scenario: A foreign same-name handle is not owned here

- **WHEN** a relation names a mate declaration belonging to an unrelated assembly with matching child and mate names
- **THEN** the existing ownership refusal applies before effective path resolution
