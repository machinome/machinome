# OpenSCAD Dependency Specification

## Purpose

Defines OpenSCAD as a conditional external dependency: the exact operations
that require it, the guarantee for operations that do not, and the actionable
failure contract when the binary is unavailable.
## Requirements
### Requirement: OpenSCAD is required only by the paths that invoke it

The system SHALL treat the OpenSCAD binary as a conditional dependency of the
paths that use it, not as a blanket installation requirement.

The paths that require it are exactly:

- rendering the STL of a leaf of the OpenSCAD node family (a `Solid2Node`,
  an `OpenScadNode`, or another subclass of the family's leaf base
  `machinome.node.openscad.leaf.ScadLeafNode`), whose authored geometry is
  SCAD for OpenSCAD to render, under the `openscad-node` capability;
- evaluating a legacy `Solid2Node` symbolic value through `as_number()` when
  it needs OpenSCAD evaluation, not a natively evaluable graph value;
- rendering an image with `machinome snapshot --renderer openscad`.

A leaf outside the family is never handed to OpenSCAD: a leaf whose STL is
not current after its own materialization is refused under the `node-model`
capability, naming it, rather than rendered from a `.scad` nothing wrote.

No other operation SHALL require it. In particular, a project whose model is
entirely exact under the `exact-geometry` capability SHALL build, test, publish,
and develop through an installed browser viewer with no OpenSCAD binary on the
PATH. Adding an exact backend SHALL NOT
extend this list: `Build123dNode` writes its own STL and BREP through the same
OCCT kernel `CadQueryNode` uses, so a project of `Build123dNode` leaves — or
of `CadQueryNode` and `Build123dNode` leaves mixed — carries no OpenSCAD
dependency.

`JScadNode` is deliberately NOT among the requiring paths. Its native producer
writes its own STL through the separate `jscad` binary and stamps the mtime,
so it never launches OpenSCAD for that artifact. A `JScadNode` therefore
carries an external-binary dependency
of its own, on `jscad`, which this capability does not describe. Giving that
binary the same conditional-dependency treatment — enumeration, guarantee,
and actionable failure — is deferred to a later cycle; until then a missing
`jscad` still fails at its subprocess launch.

The retained requiring paths SHALL preserve their behavior when the binary
is present. Faceted fusion SHALL instead use its direct mesh-composition
capability, independent of OpenSCAD availability; its OpenSCAD-authored children
still require the binary when their own geometry must be produced.

#### Scenario: An all-exact project needs no OpenSCAD

- **WHEN** a project whose every node is exact is built, tested and published
  on a machine with no `openscad` on the PATH
- **THEN** the build, the test run and the publication all succeed

#### Scenario: An all-exact project develops without OpenSCAD

- **WHEN** `machinome develop` runs for an all-exact project with the browser
  viewer installed and no `openscad` on the PATH
- **THEN** the build and browser viewer run normally and no OpenSCAD
  availability check occurs

#### Scenario: A build123d project needs no OpenSCAD

- **WHEN** a project of `Build123dNode` leaves, or of `Build123dNode` and
  `CadQueryNode` leaves mixed under a fusion, is built with no `openscad` on
  the PATH
- **THEN** every leaf's STL is produced through the OCCT kernel and the build
  succeeds

#### Scenario: A mesh-backend project still requires it

- **WHEN** a project with `Solid2Node` leaves is built
- **THEN** OpenSCAD renders each of those leaves as before

#### Scenario: A JSCAD leaf does not require OpenSCAD

- **WHEN** a project of `JScadNode` leaves is built with `jscad` available
- **THEN** each leaf's STL is produced by `jscad`, the render protocol finds
  it current, and OpenSCAD is never launched for it

#### Scenario: The deferred binary still fails at its launch

- **WHEN** a `JScadNode` must be rendered and no `jscad` is on the PATH
- **THEN** the failure is the subprocess launch error, because `jscad` is not
  yet covered by this capability

#### Scenario: Presence changes nothing

- **WHEN** any of the listed paths runs on a machine where OpenSCAD is
  installed
- **THEN** its behaviour and output are what they were before the dependency
  was declared conditional

#### Scenario: Imported meshes can fuse without OpenSCAD

- **WHEN** a fusion of valid imported STL leaves is built with `manifold3d`
  available and no OpenSCAD binary
- **THEN** the fused artifact is produced without an OpenSCAD availability check

#### Scenario: Mixed fusion requires OpenSCAD only for an authored leaf

- **WHEN** a fusion has a stale `Solid2Node` child and an imported STL child
- **THEN** OpenSCAD is required for the Solid2 child's artifact, not for the
  fusion's mesh composition

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

- **WHEN** a subclass of `machinome.node.openscad.leaf.ScadLeafNode` defined
  outside `machinome/`, implementing `render()` returning a solid2 object, must
  be rendered and no `openscad` is on the PATH
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

