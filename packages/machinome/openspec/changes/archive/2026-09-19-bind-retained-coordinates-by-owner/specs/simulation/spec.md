## ADDED Requirements

### Requirement: Qualified bank delivery is scoped to each coordinate's owner

Under a running root, binding the run's whole bank SHALL leave every qualified
joint-coordinate entry equal to its owning joint's bound value. The rendered
world pose SHALL compose those owner-specific joint placements with declared
rest placements and ancestor transforms. The result SHALL be independent of
the bank mapping's insertion order and SHALL apply equally to
single-coordinate, multi-coordinate, class-declared and site-declared joints.
Supported bare drivers and the global `time` entry SHALL retain their
established values and reach; existing qualified-name validation, ambiguity
refusals and rollback SHALL remain unchanged.

#### Scenario: Parent and descendant joints keep independent retained poses

- **WHEN** three nested nodes each own a `turn` joint, a running simulation
  moves the parent while the child and grandchild retain different values, and
  then moves the child while the other two retain theirs
- **THEN** after each request every joint's bound value equals its `sim.state`
  entry, its local joint placement represents that value, each world pose
  composes those local placements with its rest and ancestor transforms, and
  neither ancestor nor descendant receives another owner's `turn`

#### Scenario: Full-bank binding is independent of mapping order

- **WHEN** the same complete bank and `time` are rebound once in program order
  and once in reverse insertion order
- **THEN** both bindings leave every node at the same owner-specific coordinate
  and the same composed world pose, without advancing the simulation

#### Scenario: Restore and reset pose the whole nested tree from their banks

- **WHEN** a nested running mechanism takes a snapshot, moves parent and child
  coordinates independently, restores the snapshot, and then resets
- **THEN** each operation restores the bank, bound joints and rendered poses
  together, with reset returning every owner to the initial bank

#### Scenario: Every declared joint form uses the same owner boundary

- **WHEN** full-bank delivery reaches nested class-declared and site-declared
  joints, including a joint with several coordinates
- **THEN** every qualified coordinate binds only its declared owner and each
  joint is placed from its own complete coordinate set

#### Scenario: Bare drivers and time retain their established reach

- **WHEN** a running tree receives a supported bare driver, qualified drivers
  for otherwise ambiguous descendants, owner-qualified joint coordinates and
  the global `time` entry together
- **THEN** the bare driver and `time` propagate as before, each qualified entry
  reaches only its addressed owner, and an ambiguous bare driver is still
  refused rather than applied to several declarations

#### Scenario: An ambiguous bare coordinate name remains ambiguous

- **WHEN** a caller binds bare `turn` on a running tree with several nested
  owners of `turn`, or with a descendant driver of that name
- **THEN** binding is refused as ambiguous naming every matching qualified ID,
  and the complete previous bank and pose are restored

#### Scenario: Symbolic publication restores the numeric nested pose

- **WHEN** a document is published from a live running tree whose nested joints
  share local coordinate names and hold distinct retained values
- **THEN** the document's operations refer to each joint's own qualified
  coordinate, publication changes neither schema nor version, and afterward
  every bank entry, bound joint and rendered numeric pose is exactly as before
  publication
