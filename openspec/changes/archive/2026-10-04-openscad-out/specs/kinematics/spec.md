## MODIFIED Requirements

### Requirement: Tri-consumer operation objects

The system SHALL represent transforms as first-class operation objects
(`Rotation(angle, axis, node)`, `Translation(vector, node)`) that each render
for three consumers: `.presented(child)` (the presentation description, which
the OpenSCAD node package writes as SCAD), `.mesh(mesh)` (trimesh
transform with animated values resolved to floats; rotation applied in
radians), and `.serialized` (standalone form `['r', angle, axis]` / `['t',
vector]`, with expression strings for scalar values). Each operation SHALL also
provide `.reversed`, and `.matrix()` — its 4×4 homogeneous world matrix, with
animated values resolved through `as_number()` at access time and never cached,
so a keyframe change is always reflected. The registry plus `unserialize()`
SHALL round-trip the standalone form. A new operation type MUST implement all
of these surfaces and register itself.

A standalone shared scalar SHALL be self-contained and compact rather than
requiring its fully expanded spelling or relying on bindings from a previous
publication. Its textual representation need not match the former expanded
string. Node-tree document producers SHALL translate such scalars into the
document's existing expression language and bindings; standalone serialization
SHALL NOT introduce a new grammar into published viewer documents.

Generating SCAD and publishing a document SHALL leave the live operation's
value unchanged. Numeric placement, operation order, reversal and keyframe
updates SHALL retain their existing behavior.

#### Scenario: Wire round-trip

- **WHEN** an operation is serialized and passed through `unserialize()`
- **THEN** an equivalent operation object is reconstructed

#### Scenario: Shared standalone scalar round-trip

- **WHEN** a rotation or translation with a shared scalar is serialized,
  reconstructed and published under the same declared inputs
- **THEN** it evaluates to the original operation's value without requiring
  external bindings from an earlier document

#### Scenario: SCAD expression is complete by itself

- **WHEN** a shared motion scalar is emitted in a SCAD operation
- **THEN** OpenSCAD can resolve it under its original input environment without
  document-global generated bindings or expanded descendant duplication

#### Scenario: Publishing does not change SCAD meaning

- **WHEN** a tree is published and its SCAD is generated again
- **THEN** publication has not mutated the operation values or their meaning
