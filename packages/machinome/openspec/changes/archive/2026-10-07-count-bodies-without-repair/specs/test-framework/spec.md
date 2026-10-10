## MODIFIED Requirements

### Requirement: Connectivity assertions

The system SHALL provide two connectivity assertions:

- `assertJoined(node1, node2, min_weld_volume=0.0)` — the two nodes are
  exactly one body, so the two features are genuinely the same printed part.
  In a run on the B-rep engine, for two B-rep nodes this SHALL be
  established by fusing their shapes and requiring the fuse to yield exactly
  one solid; otherwise, and for every pair on the mesh engine, by
  requiring the union of their meshes to be exactly one connected component.
  `min_weld_volume` (mm³) additionally requires the volume they share to reach
  that value. Solids that only touch tangentially SHALL NOT count as joined.

- `assertNoDisconnectedSolids(node)` — every printed solid in the selected
  subtree is one connected body, specified above.

Neither SHALL be invoked by the framework; both run only when project test code
calls them.

`assertOneBody`, `assertBodyCount` and `assertNoDisconnectedParts` SHALL NOT be
provided. `assertBodyCount` expressed the removed `bodies` declaration's
mistake that a solid may legitimately be several disconnected pieces, and
`assertNoDisconnectedParts` swept leaves, holding a leaf to a contract that
belongs to the solid enclosing it.

On the mesh path, components SHALL be counted by splitting the union without
filtering to watertight components — a fragment that is itself closed still
counts as a body. Watertightness SHALL NOT be treated as evidence of
connectedness: a mesh of several disjoint closed shells is watertight, has
positive volume, and exports a valid STL. Both assertions SHALL count the
components of a mesh as the mesh holds them, without repairing it: no hole is
filled before or while counting, so a mesh that is not watertight is counted
with the components it has, and counting needs no package outside machinome's
core dependencies.

Connectivity is a property of geometry inside one solid, so `assertJoined`
SHALL place both nodes in the frame of their nearest enclosing rigid node,
composing operations up to that node and no further, on either path. It SHALL
NOT compose operations at or above the topmost rigid node, which are placement
of a whole body and cannot change whether two features within it meet.
Collision assertions are unaffected and continue to operate on world-space
geometry, because whether two separately placed parts clash is a world-framed,
time-dependent question.

Both nodes SHALL belong to the same solid. When two assembled nodes resolve to
different topmost rigid ancestors, `assertJoined` SHALL fail naming both nodes
and both solids, rather than comparing them: each would be placed at its own
part's origin, discarding the distance the assembly holds between the parts and
reporting two features that share nothing as welded. A node not linked into a
tree SHALL NOT be treated as evidence of a second solid, so plain mesh geometry
remains comparable.

The two assertions answer different questions and neither implies the other. A
solid can be one connected component while the two features the designer cared
about reach each other only by a detour through others; and no body count can
express a required weld volume.

#### Scenario: Features of two different parts are refused

- **WHEN** `assertJoined` runs on two nodes whose enclosing solids differ,
  however far apart the assembly holds those solids
- **THEN** the assertion fails naming both nodes and both solids, and no
  geometric comparison is made

#### Scenario: Tangential contact is not a join

- **WHEN** `assertJoined` runs on two solids that meet exactly on a face
  without overlapping
- **THEN** the assertion fails, because they are still two bodies

#### Scenario: A weld below the stated minimum

- **WHEN** two features overlap, but by less than `min_weld_volume`
- **THEN** the assertion fails naming the weld volume and the required one

#### Scenario: A one-body solid whose named pair is not joined

- **WHEN** `assertJoined` runs on two features of a fusion that is itself a
  single connected body, but which reach each other only through a third
  feature
- **THEN** the assertion fails, because those two alone are two bodies

#### Scenario: An animated part is asserted like a static one

- **WHEN** `assertJoined` runs on two features inside a solid whose enclosing
  assembly drives its placement
- **THEN** the assertion composes only the operations inside that solid and
  reaches the same verdict at every animation instant

#### Scenario: The removed assertions are gone

- **WHEN** a test calls `assertOneBody`, `assertBodyCount` or
  `assertNoDisconnectedParts`
- **THEN** the attribute does not exist on the test case

#### Scenario: Two B-rep features are joined by their fuse

- **WHEN** `assertJoined` runs on two overlapping B-rep features of one solid
- **THEN** the verdict comes from fusing their shapes and finding one solid,
  and the weld volume from their B-rep intersection

#### Scenario: A mesh run welds on meshes

- **WHEN** `assertJoined` is called on two B-rep features and the run's
  engine is `mesh`
- **THEN** the verdict comes from the union of their meshes and neither
  shape is fused

#### Scenario: An open mesh is counted without a repair

- **WHEN** `assertNoDisconnectedSolids` runs on a solid whose STL is not
  watertight, such as an `StlNode` declaring `require_watertight = False`,
  in an environment where no package outside machinome's declared
  dependencies can be imported (trimesh's optional graph library `networkx`
  among them)
- **THEN** a solid of one connected body passes and a solid of two fails
  naming two bodies, the same verdicts as where that package is installed,
  and no import error is raised
