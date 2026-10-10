## ADDED Requirements

### Requirement: A failing assertion names a node by its path

Every assertion of this capability whose failure message names a node
SHALL name it by its PATH: the dotted sequence of linked child names from
the node under test down to that node, the node under test's own name
excluded. Two instances of one class under one tree SHALL therefore be
distinguishable in every failure message.

The node under test is the node the runner bound to the test case. The
path SHALL NOT depend on which node a particular assertion was called
with, so one node is named by one string throughout a test run.

The segments SHALL be the linked child names the framework already
derives, the same names in the same order that the serialized document
publishes for its tree and that a qualified driver id is built from,
joined by `.`. The system SHALL NOT introduce a second spelling of a
node's place in a tree. A segment derived for a list-held or repeated
child SHALL be printed as derived.

A node with NO path SHALL be named by its bare name, and building a
failure message SHALL NEVER itself raise. A node has no path when it is
the node under test, when it is not linked into any tree, or when it is
not a node at all. A node linked into a tree that does not hang below the
node under test, including when no node under test is bound, SHALL be
named by its path below the topmost node of its own tree.

A failure message whose named nodes are all direct children of the node
under test SHALL be unchanged.

#### Scenario: Two instances of one class are distinguished

- **WHEN** an assembly holds two instances of one class, each with a
  child held under the same attribute, and those two children interfere
- **THEN** the failure names each by its path below the node under test,
  `centre.wheel should not interfere with third.wheel`, rather than the
  same leaf name twice

#### Scenario: A direct child keeps its bare name

- **WHEN** a failing assertion names a node that is a direct child of the
  node under test
- **THEN** the message is exactly what it was before this requirement,
  the path having one segment

#### Scenario: The same node is named the same way by every assertion

- **WHEN** one test calls a whole-assembly assertion on a sub-assembly of
  the node under test and another calls a pairwise assertion on a node
  inside it
- **THEN** both messages name that node by the same path below the node
  under test

#### Scenario: A node with no path is still named

- **WHEN** a failing assertion names the node under test itself, a node
  that is not linked into any tree, or the unmodelled floor of the
  support assertion
- **THEN** the message carries that node's bare name and no exception is
  raised while building it

#### Scenario: A repeated child is named as the tree names it

- **WHEN** a failing assertion names a node below a child held in a list
  or produced by a repeated declaration
- **THEN** that child's segment is the `<attribute>-<index>` name the tree
  already gives it, printed as derived

#### Scenario: The path is the document's path

- **WHEN** a node is named in a failure message, published in the
  serialized document and on the path of a qualified driver id
- **THEN** the assertion's path, the document's tree path below the root
  and the instance path a driver id is built from are the same string

## MODIFIED Requirements

### Requirement: Mesh assertions

The system SHALL provide assertions operating on world-space geometry, each
raising `AssertionError` naming the offending nodes by their path under the
`A failing assertion names a node by its path` requirement (with
quantitative measurements where one is computed, e.g. intersection volume):
`assertNotIntersecting`, `assertIntersecting`, `assertInside`,
`assertClose(max_distance)`, `assertFar(min_distance)`,
`assertIntersectVolumeAbove(min_volume)`, and
`assertIntersectVolumeBelow(max_volume)`. Standard `unittest` assertions
remain available.

Every assertion whose question is the VOLUME of an intersection SHALL obtain
that volume from the one shared evaluation helper, so no two assertions can
disagree about the same pair. This includes
`assertIntersectVolumeAbove` and `assertIntersectVolumeBelow`, which SHALL NOT
compute a separate trimesh intersection of their own.

`assertInside`, `assertClose` and `assertFar` are distance and containment
questions rather than volume questions. They SHALL continue to sample one
node's mesh vertices against the other's mesh surface, unchanged, whether or
not the nodes have B-rep geometry.

#### Scenario: Intersection detected

- **WHEN** `assertNotIntersecting(a, b)` is called and the parts overlap
- **THEN** an `AssertionError` reports each node's path and the
  intersection volume

#### Scenario: Volume assertions agree with emptiness assertions

- **WHEN** `assertNotIntersecting` and `assertIntersectVolumeBelow` are called
  on the same pair in the same test
- **THEN** both read the same measured volume from the shared helper and
  cannot reach contradictory verdicts

#### Scenario: Distance assertions are unaffected by `brep`

- **WHEN** `assertClose` or `assertFar` is called on two B-rep nodes
- **THEN** it measures mesh vertices against a mesh surface exactly as it does
  for mesh nodes
