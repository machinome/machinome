## MODIFIED Requirements

### Requirement: A missing OpenSCAD binary is reported actionably

When a path listed above requires the OpenSCAD binary and it cannot be found,
the system SHALL fail with an error that names what needed it, why that path
needs it, and what the user can do — installing OpenSCAD, or, for the snapshot
renderer, selecting the web renderer instead. The error SHALL NOT be a bare
subprocess launch failure.

When the path is the rendering of a node's STL, what needed it SHALL be named
as the node's name and its own class, and why SHALL be that the node's STL is
rendered from SCAD by OpenSCAD. The error SHALL NOT name a backend or any
class other than the node's own, so a leaf written outside the core is
reported in the same words as the core's own leaves.

The system SHALL NOT substitute a different renderer, a different geometry
path, or a cached artifact for the operation that could not run. This is the
same no-silent-substitution rule the web-snapshot capability already applies
in the opposite direction.

The check SHALL be made where the operation is attempted, so a project that
never reaches a requiring path is never asked for the binary.

#### Scenario: A mesh leaf cannot be rendered

- **WHEN** a `Solid2Node` subclass `FacetedBox`, named `housing`, must be
  rendered and no `openscad` is on the PATH
- **THEN** the build fails before any subprocess is launched with
  `node housing (FacetedBox) requires the OpenSCAD binary because its STL is
  rendered from SCAD by OpenSCAD; install OpenSCAD and ensure 'openscad' is
  on PATH` — not with a bare `FileNotFoundError`

#### Scenario: A SCAD-presented leaf outside the core is reported the same way

- **WHEN** a `LeafNode` subclass defined outside `machinome/`, implementing
  `render()` and `as_scad()` returning a solid2 object, must be rendered and
  no `openscad` is on the PATH
- **THEN** it fails with the same sentence as a `Solid2Node` leaf, naming its
  own node and class, before any subprocess is launched

#### Scenario: The OpenSCAD renderer cannot run

- **WHEN** `machinome snapshot --renderer openscad` runs and no `openscad` is on
  the PATH
- **THEN** it fails naming the missing binary and `--renderer web` as the
  alternative, and renders no image through the web renderer on its own

#### Scenario: A symbolic value cannot be evaluated

- **WHEN** a `Solid2Node` symbolic value must be resolved through `as_number()`
  and no `openscad` is on the PATH
- **THEN** it fails naming the node and the reason the evaluation needs
  OpenSCAD

#### Scenario: An unreached path is never checked

- **WHEN** an all-exact project is built on a machine with no `openscad`
- **THEN** no availability check fails, because no requiring path is reached
