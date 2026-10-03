## MODIFIED Requirements

### Requirement: Exact geometry accessor

An exact node SHALL provide `shape()`, returning its geometry as the exact
engine's currency in the node's own local frame — the same frame its `.stl`
and its cached base mesh use, with neither its own operations nor any
ancestor's composed into it. A node whose geometry comprises several solids
SHALL return them as one compound.

The currency SHALL be one type for every exact node, whichever exact adapter
produced it — CadQuery, build123d, a sheet part, a STEP product, a molejo
solid at a bound snapshot — and for an exact fusion, so that a consumer
handles one type. Which type that is SHALL be the exact engine's, stated by
the `occt-engine` capability; the core passes it on without inspecting it, and
it SHALL never be a CAD front end's object. A consumer that wants a front
end's methods SHALL wrap the shape with that front end itself; the wrapping
changes no geometry.

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

#### Scenario: Every exact node returns one currency

- **WHEN** `shape()` is read on a `CadQueryNode`, a `Build123dNode`, a
  `Build123dSheetNode`, a `StepNode`, a `MolejoNode` at a bound snapshot and an
  exact `FusionNode`
- **THEN** every result is of the one type the exact engine declares as its
  currency, and none is a CadQuery or build123d object

#### Scenario: A front end rewraps the shape without changing it

- **WHEN** a consumer wraps a `CadQueryNode`'s `shape()` with CadQuery and
  reads its volume
- **THEN** the volume is the volume of the solid the node rendered

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

## ADDED Requirements

### Requirement: An exact render is admitted by its kernel object

An exact leaf SHALL convert its render result to its exact geometry at the
adapter boundary, and the conversion SHALL be a rewrap of the kernel object
the result already holds, never a translation: no tessellation, tolerance or
healing SHALL occur in it.

Every exact leaf SHALL accept a render result the exact engine admits as its
currency, by the engine's own admission rule, which the `occt-engine`
capability states. On top of that, `CadQueryNode` and `StepNode` SHALL accept
a CadQuery `Workplane`, taking its values and composing several into one
compound, and `Build123dNode` SHALL accept a build123d builder, taking its
finished part, as they do today. A result none of these describes SHALL be
refused naming the node, as today.

#### Scenario: A render in the engine's currency is accepted

- **WHEN** an exact leaf whose render returns the engine's currency itself is
  built
- **THEN** its `.brep` and `.stl` are written and its `shape()` is that solid

#### Scenario: A front-end render is rewrapped

- **WHEN** an exact leaf whose render returns a CadQuery `Shape` or a
  build123d `Part` is built
- **THEN** its `shape()` holds the very kernel object the render held, with
  the same volume

#### Scenario: A workplane of several solids becomes one compound

- **WHEN** a `CadQueryNode` renders a `Workplane` holding two disjoint solids
- **THEN** its `shape()` is one compound holding both

### Requirement: Exact geometry needs no CAD front end

The framework's exact geometry — artifact writing, `shape()`, exact fusion
and exact comparisons — SHALL depend on the exact engine alone. A project
whose exact leaves render the engine's currency directly SHALL build, fuse and
test exactly without `cadquery` or `build123d` being imported by the
framework.

#### Scenario: A front-end-free project never imports a front end

- **WHEN** a project whose exact leaves render the engine's currency
  directly, fused in an exact `FusionNode` and compared by an intersection
  assertion, is built and tested in a fresh interpreter
- **THEN** the build writes every `.brep` and `.stl`, the fusion is exact, the
  assertion reaches its exact verdict, and neither `cadquery` nor `build123d`
  is among the imported modules
