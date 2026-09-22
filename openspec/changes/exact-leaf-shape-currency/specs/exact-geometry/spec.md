## MODIFIED Requirements

### Requirement: Exact geometry accessor

An exact node SHALL provide `shape()`, returning its geometry as an OCCT shape
in the node's own local frame — the same frame its `.stl` and its cached base
mesh use, with neither its own operations nor any ancestor's composed into it.
A node whose geometry comprises several solids SHALL return them as one
compound.

Reading `shape()` on a node that is not exact SHALL raise, naming the node.

Placement SHALL remain the caller's responsibility and SHALL use the same
composed matrices the mesh path uses, so an exact comparison and a mesh
comparison place the same node identically: world composition for collision
questions, enclosing-solid composition for connectivity questions.

When an exact leaf's BREP is current, `shape()` SHALL reuse that native
artifact. When the BREP is stale, `shape()` SHALL return native geometry
from the leaf's current render, even if SCAD presentation was previously
assembled. It SHALL NOT return a presentation import as geometry.

#### Scenario: The accessor returns unplaced geometry

- **WHEN** `shape()` is read on an exact leaf carrying placement operations
- **THEN** the returned shape is in the node's local frame, with no operation
  applied

#### Scenario: A faceted node has no exact geometry

- **WHEN** `shape()` is called on a node whose `exact` is false
- **THEN** it raises naming that node

#### Scenario: Exact and mesh placement agree

- **WHEN** the same node is placed for an exact comparison and for a mesh
  comparison at one testing instant
- **THEN** both use the same composed matrix and describe the same pose

#### Scenario: A current BREP avoids rendering

- **WHEN** an exact leaf has a current BREP and `shape()` is requested
- **THEN** it returns that native artifact without calling the adapter's render

#### Scenario: Stale BREP after SCAD assembly

- **WHEN** an exact leaf's SCAD presentation has been assembled and its BREP
  becomes stale before an exact fusion requests `shape()`
- **THEN** the fusion receives the leaf's current native shape in its local
  frame, not the SCAD artifact import
