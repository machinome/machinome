## MODIFIED Requirements

### Requirement: Rigid vs non-rigid distinction

The system SHALL distinguish rigid nodes (`rigid = True`; can produce a cached
STL) from non-rigid nodes. Rigidity SHALL be determined by node type and SHALL
NOT be recomputed from a node's children: `LeafNode` and `FusionNode` are
rigid, `AssemblyNode` is non-rigid, and a flexible leaf (`FlexibleNode`, the
`flexible-parts` capability) is the one non-rigid leaf kind — its geometry is
a function of bound state, so it makes no time-invariance promise. Only rigid
nodes generate cached STL files.

A `FusionNode` SHALL reject a non-rigid child. Fusion combines solids into one
solid; an assembled thing cannot be fused, and neither can a part whose shape
varies with machine state. The rejection SHALL name the fusion and the
offending child and SHALL happen during render validation, before any
geometry is produced.

A **topmost rigid node** is a rigid node whose parent is non-rigid, or the root
node when the root is itself rigid. Because a fusion cannot contain an
assembly or a flexible leaf, every rigid node is either a topmost rigid node
or a descendant of exactly one. A topmost rigid node is the boundary of one
printed solid and the unit selected by whole-solid assertions; this definition
does not itself run an assertion or guarantee that the solid's geometry is
connected. A flexible leaf is never a topmost rigid node.

Rigidity is also what decides where a **marking** may be declared under the
`markings` capability. A marking is a surface feature in a part's own frame and
is carried by that part's placement, so it SHALL be declared only on a rigid
node; a marking declared on an `AssemblyNode`, on a flexible leaf, or on any
other non-rigid node SHALL be refused when the class is created, naming the
class and the attribute. A marking does not change what a node IS: it adds no
solid, no child and no printed piece, so a node carrying markings remains
exactly as rigid, as fusable and as printable as the same node without them.

#### Scenario: An assembly cannot be fused

- **WHEN** a `FusionNode` renders a child that is an `AssemblyNode`, or any
  other non-rigid node
- **THEN** an exception is raised naming the fusion and that child, and no
  geometry is produced

#### Scenario: Rigidity is not recomputed from children

- **WHEN** a `FusionNode` renders a subtree of leaves and nested fusions
- **THEN** it remains rigid, and its rigidity is its type's, not derived by
  combining its children's

#### Scenario: STL access on non-rigid node

- **WHEN** the `stl` property is read on a non-rigid node
- **THEN** an exception is raised

#### Scenario: The topmost rigid node under an assembly

- **WHEN** an `AssemblyNode` holds a `FusionNode` that itself holds leaves and
  a nested fusion
- **THEN** the outer `FusionNode` is the topmost rigid node of that branch, and
  the leaves and nested fusion are not

#### Scenario: The solid boundary does not imply a test

- **WHEN** a topmost rigid node's STL contains disconnected geometry and no
  project test calls `assertNoDisconnectedSolids`
- **THEN** its status as a topmost rigid node neither rejects the model nor
  causes a connectivity assertion to run

#### Scenario: A flexible leaf is a non-rigid leaf

- **WHEN** `rigid` is read on a flexible leaf
- **THEN** it reports `False` while the node remains a leaf, and a
  `FusionNode` rendering it raises naming both nodes

#### Scenario: Only a rigid node may carry a marking

- **WHEN** an `AssemblyNode` subclass and a flexible leaf subclass each declare
  a marking
- **THEN** creating each class raises, naming the class and the attribute,
  while the same declaration on a rigid leaf or a `FusionNode` is accepted

#### Scenario: A marking does not change what a node is

- **WHEN** a rigid leaf that declares two markings is fused into a
  `FusionNode` and the fusion is built
- **THEN** the fusion accepts it as a rigid child, the leaf remains a rigid
  leaf, and the fusion's topmost-rigid-node status is what it is without the
  markings

### Requirement: Color declaration

The system SHALL accept a class-level `color` in `#RRGGBB` form and reject
any other non-None value with `ValueError` during colorization.

A node's `color` remains one colour for the whole node and remains optional. A
**marking** declared on a rigid node under the `markings` capability carries
its own colour, validated in the same `#RRGGBB` form and rejected with the same
`ValueError`, and required rather than optional: a marking with no colour would
declare nothing. A marking's colour SHALL NOT change the node's own.

#### Scenario: Invalid color

- **WHEN** a node declares `color = 'red'`
- **THEN** assembling it raises `ValueError`

#### Scenario: A marking's colour is separate from the node's

- **WHEN** a node declaring `color = '#222831'` carries a marking declaring
  `color = '#FFFFFF'`
- **THEN** the node's published colour is `#222831` and the marking's is
  `#FFFFFF`

