## MODIFIED Requirements

### Requirement: Template-method render lifecycle

The system SHALL control preparation, validation, native artifact production
and placement through a framework-owned lifecycle. Users SHALL NOT override
that lifecycle. Native geometry consumers SHALL NOT require `present()` or
any presentation to prepare the tree or produce its native artifacts.
Public `assemble()` SHALL remain the presentation entry point over the same
prepared tree: it composes the node's presentation description
(`machinome.node.presentation`) through each node's `present()`, preserves
optimized imports and colours, applies queued operations in their existing
order, and returns that description. It SHALL write no artifact of a
presentation: no `.scad` for any node, and SHALL require no node package. A
node's `.scad` is written only by the OpenSCAD node package, under the
`openscad-node` and `backend-neutral-materialization` capabilities.

A rigid leaf whose STL is still not current after its materialization SHALL be
refused when its STL is generated, before any process is launched, with an
error naming the node, its own class and its STL path: `node {name} ({class})
produced no STL: its materialization published nothing at {stl_file}`. The core
SHALL NOT hand such a leaf to another tool.
`assemble()` SHALL be idempotent — the result is memoized and `render()` is
called at most once per instance. On an assembly the framework SHALL run
`simulate()` after `render()` ONCE PER ENUMERATION of the tree, under the
current binding: the `render()` that begins an enumeration drives the
simulate phase of every assembly in the subtree it renders, parents
before children, before it returns, and a later `render()` reached by the
walk's own descent within that same enumeration SHALL return the
children at rest without running that assembly's phase again. Every
assembly's motion is therefore in place before the walk reads any of the
tree's geometry. Users override `render()` and `simulate()`, never
`assemble()` or the framework's preparation lifecycle. The same simulation
ordering SHALL hold for native preparation and SCAD compatibility consumers.

#### Scenario: Assemble is memoized

- **WHEN** `assemble()` is called twice on the same instance
- **THEN** `render()` runs only once and the cached result is returned

#### Scenario: Optimized import of cached STL

- **WHEN** a node has `optimize = True`, is rigid, and its STL is up to date
- **THEN** `assemble()` presents an import of the STL artifact instead of
  inlining the SCAD model, and queued operations are applied after the import

#### Scenario: An up-to-date leaf is not rendered

- **WHEN** a rigid optimizing leaf's artifact is up to date and `assemble()` runs
- **THEN** the node's `render()` is not called and no CAD geometry is computed

#### Scenario: A stale leaf is rendered

- **WHEN** any file tracked for that leaf has changed since its artifact was written
- **THEN** `assemble()` renders the node and regenerates the artifact

#### Scenario: Simulate follows render

- **WHEN** an assembly defining both `render()` and `simulate()` is
  assembled
- **THEN** `render()` has run before `simulate()`, and the queued
  operations applied include those `simulate()` produced

#### Scenario: Every phase precedes the first geometry read

- **WHEN** a root with two subtrees is assembled
- **THEN** both subtrees' `simulate()` methods ran before the first
  subtree's geometry was composed, so a coordinate bound while the
  second subtree simulated still moves a body in the first

#### Scenario: Assemble writes no SCAD

- **WHEN** `assemble()` is called with the OpenSCAD node package installed on
  an assembly of a B-rep leaf and a `Solid2Node` leaf whose artifacts are
  current
- **THEN** it returns the presentation description and no `.scad` file is
  written or rewritten, the assembly's included

#### Scenario: Assemble without the OpenSCAD engine

- **WHEN** `assemble()` is called on an assembly of native artifact-owning
  leaves with SolidPython and the OpenSCAD node package absent
- **THEN** it renders, validates, links, simulates and prepares exactly as with
  them, returns the same presentation description, writes no `.scad`, and
  imports no module of the package

#### Scenario: A leaf that produced no STL is refused

- **WHEN** a `LeafNode` subclass whose `materialize()` returns without
  publishing its STL is built, with an `openscad` executable on the PATH
- **THEN** the build fails naming the node, its class and its STL path, and no
  process is launched for it

#### Scenario: Native preparation is independent of SCAD presentation

- **WHEN** an assembly of native artifact-owning leaves is exported or built
  for geometry tests and its SCAD presentation methods are unavailable
- **THEN** structure, validation, motion, geometry and publication succeed
  without invoking those presentation methods

### Requirement: Multi-backend leaf adapters

The system SHALL provide leaf adapters for multiple CAD backends —
`Solid2Node` (solid2/SolidPython2), `CadQueryNode`, `Build123dNode`,
`OpenScadNode` (with `scad_source` and optional `module_name`), and `JScadNode`
(with `jscad_source`) — one sheet leaf kind, `Build123dSheetNode`, whose
part is authored as a profile plus thickness under the `sheet-parts`
capability, one mesh-import leaf, `StlNode` (with `stl_source`), whose
part is a committed STL mesh under the `stl-import` capability, one
solid-import leaf, `StepNode` (with `step_source` and `part`), whose part is
one product of a STEP document under the `step-import`
capability, and one
flexible leaf kind, `MolejoNode`, whose part is a molejo shape spec fed by
ports under the `flexible-parts` capability. `Solid2Node` and `OpenScadNode` are
the OpenSCAD node family, defined in `machinome.node.solid2` and the package
`machinome.node.openscad` under the `openscad-node` capability. Native adapters
SHALL provide geometry through their artifact/evaluation capability without
requiring a custom `present()` implementation. SCAD output SHALL remain
available through the OpenSCAD node package, which writes any node's
presentation. A project leaf that only overrides a method named `as_scad` is not
handed to OpenSCAD: a leaf authoring SCAD subclasses `Solid2Node`. Adapters
declaring a `namespace` (`Solid2Node`, `CadQueryNode`, `Build123dNode`,
`OpenScadNode`, `Build123dSheetNode`, `StepNode`, `MolejoNode`) get
namespace-based render
validation, while `JScadNode` and `StlNode` declare none and skip that check.

`Build123dNode` SHALL accept as a render result a build123d solid — a `Part`,
`Solid` or `Compound` — or a `BuildPart` builder, from which the finished
`.part` is taken. Because build123d's one- and two-dimensional objects share
the `build123d` namespace with its solids, namespace validation alone does not
distinguish them; the adapter SHALL therefore reject a render result that is
not a solid, naming the node and the type it produced. This rule is specific
to this adapter and SHALL NOT constrain the results of the other adapters.

`Build123dSheetNode` is not a `Build123dNode`: its extension point is
`profile()` rather than `render()`, and what its `profile()` must produce —
one planar build123d face — is specified by the `sheet-parts` capability.

`MolejoNode` is a flexible leaf, not a rigid adapter: its `render()` returns
a molejo `Shape`, its per-instant parameter values arrive through declared
ports rather than constructor arguments, and its rigidity, artifact, and
document behavior are specified by the `flexible-parts` capability.

OpenSCAD SHALL be the compilation target for the adapters that emit SCAD for
it to render: `Solid2Node` and `OpenScadNode` have their STL rendered by
OpenSCAD from the SCAD each emits, through the family's leaf base. An adapter that produces its own artifact
through another tool SHALL NOT additionally require OpenSCAD to do so —
`CadQueryNode`, `Build123dNode`, `Build123dSheetNode` and `StepNode` through
their own
kernel, `JScadNode` through the `jscad` binary, `MolejoNode` through molejo's
Python evaluator, and `StlNode` through no
external tool at all: its artifact is materialized from the committed mesh.
`StepNode` needs no external tool either: the kernel that reads its document
is the one that writes its artifacts.
Every adapter SHALL remain representable in a presentation, so the SCAD the
OpenSCAD node package writes of an assembled tree retains its existing
coverage, including the flexible-part snapshot limitations. A presentation does
not imply OpenSCAD artifact production and SHALL NOT be a prerequisite for a
native adapter's geometry.

An adapter's native artifact producer SHALL produce an artifact only when it
is not up to date. A `present()` request SHALL reuse that same producer when
needed and SHALL return an equivalent presentation whether the artifact was
already current or just materialized. This covers every artifact
the adapter owns; the sheet adapter's
DXF is produced and guarded under the same rule, and the flexible adapter's
snapshot artifact is guarded per binding as the `flexible-parts` capability
specifies.

An adapter whose backend is a boundary-representation kernel SHALL
additionally expose its geometry as a boundary representation, under the
`brep-geometry` capability.
`CadQueryNode`, `Build123dNode`, `Build123dSheetNode`, `StepNode` and
`MolejoNode` are
such adapters: each has B-rep geometry and provides `shape()`.
`Solid2Node`, `OpenScadNode`, `JScadNode` and `StlNode` produce geometry only
as meshes and have no B-rep geometry. Exposing B-rep geometry SHALL NOT change an
adapter's presentation or its mesh artifact, so a project that never asks a
B-rep question is unaffected.

#### Scenario: OpenSCAD source adapter

- **WHEN** an `OpenScadNode` subclass declares `scad_source` and is
  instantiated with args/kwargs
- **THEN** the referenced `.scad` module is called with those args in the
  SCAD the OpenSCAD node package writes, with `module_name` defaulting to the
  file's basename

#### Scenario: CadQuery adapter routes through STL

- **WHEN** a `CadQueryNode` is assembled
- **THEN** the CadQuery object is exported to STL and its presentation is an
  import of that STL, which the SCAD output writes as `import`

#### Scenario: build123d adapter routes through STL

- **WHEN** a `Build123dNode` is assembled
- **THEN** the build123d object is exported to STL and its presentation is an
  import of that STL

#### Scenario: Sheet adapter routes through STL

- **WHEN** a `Build123dSheetNode` is assembled
- **THEN** its extruded solid is exported to STL and its presentation is an
  import of that STL, as for the other kernel-owned adapters

#### Scenario: STEP adapter routes through its own artifact

- **WHEN** a `StepNode` is assembled
- **THEN** the product it selected is exported to STL and its presentation is
  an import of that STL, as for the other kernel-owned adapters, and no
  external tool is required to produce it

#### Scenario: STL adapter routes through its materialized artifact

- **WHEN** an `StlNode` is assembled
- **THEN** its presentation is an import of its materialized artifact, as for
  the other artifact-owning adapters

#### Scenario: Flexible adapter routes through its snapshot

- **WHEN** a `MolejoNode` is assembled at a bound numeric snapshot
- **THEN** its presentation is an import of its per-binding snapshot STL, as
  the `flexible-parts` capability specifies

#### Scenario: A builder result is accepted

- **WHEN** a `Build123dNode.render()` returns a `BuildPart` builder rather
  than its finished part
- **THEN** the builder's `.part` is taken as the rendered solid and the node
  assembles as if that part had been returned

#### Scenario: A non-solid build123d result is rejected

- **WHEN** a `Build123dNode.render()` returns a build123d sketch or curve,
  which passes namespace validation
- **THEN** validation raises an error naming the node and the type it
  produced, and no geometry is produced

#### Scenario: An adapter does not rewrite a current artifact

- **WHEN** `present()` runs on a `CadQueryNode`, `Build123dNode`,
  `Build123dSheetNode`, `JScadNode`, `StlNode` or `MolejoNode` whose
  artifacts are up to date (for the flexible adapter: current for the
  unchanged binding)
- **THEN** no export or external renderer runs, and the returned presentation
  is unchanged

#### Scenario: Only the B-rep backends are exact

- **WHEN** `brep` is read across one instance of each adapter
- **THEN** the `CadQueryNode`, `Build123dNode`, `Build123dSheetNode`,
  `StepNode` and
  `MolejoNode` report true and the `Solid2Node`, `OpenScadNode`,
  `JScadNode` and `StlNode` report false

#### Scenario: Exactness does not disturb the SCAD path

- **WHEN** a `CadQueryNode` is assembled in a project that asks no B-rep
  question
- **THEN** its presentation and STL artifact are what they were before the
  adapter declared `brep`


#### Scenario: A B-rep adapter compiles without OpenSCAD

- **WHEN** a project of `CadQueryNode`, `Build123dNode` or
  `Build123dSheetNode` leaves is built with no `openscad` on the PATH
- **THEN** every leaf's STL is produced through its own kernel and the build
  succeeds

#### Scenario: An adapter with its own external tool does not need OpenSCAD

- **WHEN** a project of `JScadNode` leaves is built with `jscad` available and
  no `openscad` on the PATH
- **THEN** every leaf's STL is produced by `jscad` and the build succeeds

#### Scenario: The mesh-import adapter needs no renderer at all

- **WHEN** a project of `StlNode` leaves with no fusion is built with neither
  `openscad` nor any other CAD tool on the PATH
- **THEN** every leaf's STL artifact is materialized from its committed mesh
  and the build succeeds

#### Scenario: SCAD is still emitted by every adapter

- **WHEN** a `CadQueryNode` project is assembled and the OpenSCAD node package
  writes its root's SCAD
- **THEN** the text imports every leaf's STL, and no `.scad` is written by the
  build for any of its leaves

#### Scenario: Native adapter participation needs no SCAD hook

- **WHEN** a native adapter provides its validated local mesh artifact but no
  custom SCAD conversion method
- **THEN** it participates in assembly, export and geometry tests, and its
  presentation imports that artifact, which the OpenSCAD node package writes as
  SCAD when asked

#### Scenario: A legacy adapter override is honored

- **WHEN** a project supplies geometry by overriding only a method named
  `as_scad()`, including on a built-in adapter subclass
- **THEN** the core does not call it: a built-in adapter subclass keeps its
  native producer, and a `LeafNode` subclass that produces no STL is refused
  naming it, so geometry never silently comes from a hook the contract no
  longer declares

### Requirement: Leaf adapters are distinct types

Each leaf adapter SHALL be a distinct type, and no adapter SHALL be an
instance of another. Adapters that share an implementation base SHALL NOT
thereby become interchangeable to a type test: a project or a framework path
that distinguishes backends by `isinstance` or by walking the method
resolution order SHALL get the same answer whatever bases the adapters happen
to share.

This constrains how shared adapter behaviour may be factored. It does not
require any particular factoring. The shared leaf bases — `LeafNode`,
`BrepLeafNode`, `SheetLeafNode` and `FlexibleNode` — are the declared
extension points of the `leaf-contract` capability; declaring them does not
make two adapters sharing one interchangeable, and an adapter written outside
the core against one of them is as distinct a type as the core's own.

Sharing a base SHALL NOT change which framework path a leaf reaches: a B-rep
adapter, whatever bases it shares, writes its STL through the B-rep engine and
SHALL NOT reach the OpenSCAD rendering path.

#### Scenario: Adapters sharing a base stay distinct

- **WHEN** the B-rep adapters `CadQueryNode` and `Build123dNode` are tested
  against each other with `isinstance`
- **THEN** neither is an instance of the other, and each remains its own type

#### Scenario: The sheet adapter is not its backend's solid adapter

- **WHEN** `Build123dSheetNode` and `Build123dNode` are tested against each
  other with `isinstance`
- **THEN** neither is an instance of the other, though both drive build123d

#### Scenario: An adapter written outside the core is its own type

- **WHEN** an `BrepLeafNode` subclass defined outside `machinome/` is tested
  against `CadQueryNode` and `Build123dNode` with `isinstance`
- **THEN** it is an instance of neither, and neither is an instance of it

#### Scenario: A shared base does not route an exact adapter through OpenSCAD

- **WHEN** a `CadQueryNode`, a `Build123dNode` or a `Build123dSheetNode` leaf
  is prepared and its STL generated with OpenSCAD's availability check and
  subprocess launch both made to fail
- **THEN** its STL is written and neither the check nor the launch is
  attempted
