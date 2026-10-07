## MODIFIED Requirements

### Requirement: A family leaf writes and keeps its own SCAD and renders its STL with OpenSCAD

A family leaf's materialization SHALL write its own `.scad` (`generate_scad()`)
from what it rendered, and its `generate_stl()` SHALL render the leaf's STL from
that file with the OpenSCAD binary under the asynchronous STL render protocol of
the `build-pipeline` capability, confirming the binary first under the
`openscad-dependency` capability. It SHALL declare its `.scad` in
`kept_artifacts()`, so the build sweep keeps it while the leaf is in the
published tree. The family leaf's `present(rendered)` SHALL return what it
rendered, which the core holds as authored geometry.

A family leaf's presentation SHALL be the geometry it authored whether or not
its STL is current: when `assemble()` finds its STL current and it has not
rendered, its presentation SHALL be left to be rendered when something asks for
it, and SHALL NOT be the import of that STL. Its `scad_code`, its
`generate_scad()` and any `.scad` written from them SHALL therefore hold the
text its materialization writes, an `OpenScadNode`'s ending in its module call,
and SHALL never import the STL that OpenSCAD renders from that text.

#### Scenario: A Solid2Node leaf builds through OpenSCAD

- **WHEN** a project with a stale `Solid2Node` leaf is built with OpenSCAD
  available
- **THEN** its `.scad` is written by its materialization, OpenSCAD renders its
  `.stl` from it, and both remain after the build's sweep

#### Scenario: A current leaf keeps its SCAD

- **WHEN** a `Solid2Node` leaf whose `.stl` is current is rebuilt
- **THEN** its `.scad` and its currency record are not rewritten and are still
  present after the sweep

#### Scenario: A current leaf's SCAD text is its geometry

- **WHEN** a process that has not rendered a `Solid2Node` or an `OpenScadNode`
  leaf assembles it with its `.stl` current and asks for its `scad_code`
- **THEN** the text equals the bytes of the `.scad` its build wrote, and imports
  no STL of its own
