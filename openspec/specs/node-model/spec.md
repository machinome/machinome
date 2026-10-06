# Node Model Specification

## Purpose

The core composite node tree that models a mechanical project: base classes,
the render lifecycle, rigid/non-rigid semantics, multi-backend leaf adapters,
and node identity/naming. Encodes ADR-001 (composite pattern), ADR-002
(template-method lifecycle), ADR-003 (rigid vs non-rigid), ADR-004 (multi-CAD
backend adapters), and ADR-026 (parameter-hashed artifact keys vs tree names).

Code: `machinome/node/` (`base.py`, `internal.py`, `leaf.py`, `fusion.py`,
`assembly.py`, `declarative.py`, and the leaf modules `cadquery.py`,
`build123d.py`, `step.py`, `molejo.py`, `solid2.py`, `openscad.py`,
`jscad.py`, `stl.py`).
## Requirements
### Requirement: Composite node tree

The system SHALL model a project as a tree of nodes rooted in
`AbstractBaseNode`, where `InternalNode` subclasses compose children and
`LeafNode` subclasses generate geometry. An `InternalNode.render()` SHALL
return a list or tuple of node instances, or `None` on a class with
declared children under the `declarative-nodes` capability, in which case
the framework substitutes the realized declared children minus the omitted
ones before any consumer sees the result. A `LeafNode.render()` SHALL
return a single geometry object, never a list and never `None`. Validation
runs during framework preparation before geometry production or SCAD
presentation. Public `assemble()` uses that same preparation and returns its
presentation description; neutral consumers compose the tree without a SCAD
union.

#### Scenario: Internal node returns children

- **WHEN** an `InternalNode` subclass's `render()` returns a list of
  `AbstractBaseNode` instances
- **THEN** preparation links and prepares each child; `assemble()` presents
  the assembly's children together, or the canonical fused geometry for a
  fusion, preserving their placements

#### Scenario: Internal node returns nothing

- **WHEN** an `InternalNode` subclass with declared children defines a
  `render()` that positions them and returns nothing
- **THEN** `assemble()` links, prepares and presents the declared children
  exactly as if `render()` had returned them in declaration order

#### Scenario: Structural contract violations are rejected

- **WHEN** an `InternalNode.render()` returns a non-list that is not the
  declarative `None`, returns an element that is not an `AbstractBaseNode`,
  or returns an instance of its own type
- **THEN** validation raises an error during `assemble()`
- **WHEN** a `LeafNode.render()` returns a list, returns `None`, or returns
  an object whose module does not start with the adapter's declared
  `namespace`
- **THEN** validation raises an error during `assemble()`

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

### Requirement: Animation-time access restrictions

The system SHALL restrict the `time` property to `AssemblyNode`. `LeafNode`
and `FusionNode` SHALL raise on `time` access, preserving the invariant that
rigid geometry is time-invariant (precondition for STL caching, ADR-003/008).

#### Scenario: Fusion cannot animate

- **WHEN** a `FusionNode` subclass reads `self.time` during `render()`
- **THEN** an exception is raised directing the user to `AssemblyNode`

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

#### Scenario: Only the B-rep backends declare `brep`

- **WHEN** `brep` is read across one instance of each adapter
- **THEN** the `CadQueryNode`, `Build123dNode`, `Build123dSheetNode`,
  `StepNode` and
  `MolejoNode` report true and the `Solid2Node`, `OpenScadNode`,
  `JScadNode` and `StlNode` report false

#### Scenario: Declaring `brep` does not disturb the SCAD path

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

### Requirement: Parameter-hashed artifact identity

The system SHALL give each node instance a `uniq_id` of the form
`<readable-prefix>-<12-hex-sha256>`, hashed over a canonical serialization of
the class `__qualname__` and the node's parameters. For an external-file
wrapper (`StlNode`, `StepNode`, `JScadNode` or `OpenScadNode`), the class
identity SHALL additionally include its defining Python source's normalized
real path relative to the project root owning the resolved external source.
It SHALL NOT depend on an absolute checkout path, module import alias,
source contents or timestamp. Ordinary Python nodes SHALL retain their
existing canonical serialization byte for byte.

For a class that declares no parameters and no children under the
`declarative-nodes` capability, the parameters are the positional args in
order and the kwargs sorted by key that reach `AbstractBaseNode.__init__`,
exactly as before. For a declarative class, the parameters are the resolved,
coerced values of its declared parameters sorted by name, derived by the
framework and never forwarded by hand. The readable prefix is sanitized and
truncated to 60 characters; the hash is computed over the full untruncated
serialization. Build artifact basenames are always `<script-name>-<uniq_id>`.
The `name=` kwarg SHALL never influence `uniq_id`.

Generated declaration-site joint and fresh-mate specializations SHALL retain
the original author class's defining source and qualname for artifact identity.
Origin qualification SHALL NOT change constructor acceptance/refusal or
source-containment behavior. When an otherwise constructible wrapper is
defined outside a project, its defining source SHALL be expressed relative to
the artifact-owning project root, including parent-directory components when
needed; it SHALL NOT be newly refused for lacking its own manifest.

#### Scenario: Parameter change invalidates artifact key

- **WHEN** the same node class is instantiated with any differing parameter
  value
- **THEN** the two instances have different `uniq_id`s and separate build
  artifacts

#### Scenario: Identical instances share artifacts

- **WHEN** the same class is instantiated twice with identical args
- **THEN** both instances share one `uniq_id` and one cached artifact set

#### Scenario: Distinct no-arg classes never collide

- **WHEN** two no-arg node classes with different qualnames are built, or two
  same-qualname external wrappers defined in different Python files are built
- **THEN** their `uniq_id`s differ because their class identities differ

#### Scenario: A declarative class cannot forget a parameter

- **WHEN** a class declares six parameters and is realized twice with one
  value differing
- **THEN** the two `uniq_id`s differ without the class forwarding anything
  to `super().__init__()`

#### Scenario: A migrated class keeps its key

- **WHEN** a class that forwarded all of its kwargs to `super().__init__()`
  with float defaults is rewritten to declare exactly those parameters with
  the same defaults
- **THEN** an instance realized with defaults has the same `uniq_id` as
  before the rewrite

#### Scenario: Local wrapper identity survives project relocation and aliases

- **WHEN** the same project, external asset and project-local defining wrapper
  move together to a different absolute directory, or that class is imported
  through a different module alias, with its qualname and parameters unchanged
- **THEN** its `uniq_id` and project-relative artifact path are unchanged

#### Scenario: A specialization keeps the author's geometry key

- **WHEN** a source-bound author class is realized with declaration-site joints
  or with a fresh freedom mate's generated specialization
- **THEN** its `uniq_id` equals the author class's for the same parameters and
  no generated implementation source or joint declaration enters the key

#### Scenario: Ordinary Python nodes keep existing identity bytes

- **WHEN** an ordinary Python node is realized with unchanged class and
  parameters after external-wrapper origin qualification is introduced
- **THEN** its canonical serialization and `uniq_id` remain unchanged

#### Scenario: A nonproject defining wrapper remains constructible

- **WHEN** a wrapper defined in a module with no manifest is already
  constructible using an external file inside a discoverable project
- **THEN** identity includes its defining Python path relative to that project
  and construction remains accepted without requiring a new manifest

### Requirement: Tree naming from parent attributes

The system SHALL derive a child's tree name when it is linked: an explicit `name=` always wins; otherwise the parent attribute holding the child is used (a plain attribute wins over list membership; list members become `<attr>-<index>`; `_`-prefixed attributes and `children`, the framework's own linked list, are skipped; class name is the fallback). Where the same child is reachable through several direct attributes, the first public direct attribute in insertion order SHALL win; only when no direct attribute holds it SHALL the first public list/tuple membership in attribute and element order name it.

Naming SHALL be idempotent and used consistently by the test runner, simulation/driver enumeration, the web/document serializer, and STL child linking. A framework traversal SHALL inspect a parent's attributes and sequence contents at most once, SHALL link and name all returned siblings from that traversal-entry snapshot before recursing into any child's user code, and SHALL then perform constant-time name lookup per child. It SHALL NOT rescan a wide list once per child.

Direct reassignment, alias changes, replacement, append/removal, and same-length in-place reordering SHALL be visible on the next traversal. A mutation performed by one child during recursive user code SHALL NOT change how a later sibling is named in the parent traversal already in progress; all siblings use the same entry snapshot, and the mutation is visible when another traversal begins. Every link SHALL update the child's current parent even when its explicit name prevents derivation.

#### Scenario: Attribute-derived name

- **WHEN** a parent stores a child as `self.wheel` and returns it from `render()`
- **THEN** the child's tree name is `wheel`

#### Scenario: A direct alias wins over list membership

- **WHEN** one unnamed child appears in a public list and is also held by a public direct attribute declared later
- **THEN** the direct attribute names it, and linking does not depend on the list scan encountering it first

#### Scenario: A wide list is indexed once per traversal

- **WHEN** one traversal links thousands of children held in a public list
- **THEN** the list is scanned once for that parent and each returned child is named by constant-time lookup, producing the same `<attr>-<index>` names as the unindexed contract

#### Scenario: Same-length mutable reorder is visible

- **WHEN** a legacy model reverses or swaps elements of a public child list without changing its length and the tree is traversed again
- **THEN** each unnamed child's derived `<attr>-<index>` name reflects its new position and each parent link is current

#### Scenario: Mid-traversal mutation waits for the next traversal

- **WHEN** the first child mutates or reorders its parent's public child list during recursive render or simulate work
- **THEN** every sibling in the current traversal keeps the name derived from the common traversal-entry snapshot, and a subsequent traversal reflects the mutated order

#### Scenario: The linked list never names

- **WHEN** an assembly's once-only `render()` returns fresh unnamed children and the tree is linked, assembled and serialized more than once
- **THEN** every link derives the same class-name fallback, never `children-<index>` from the list `present` keeps

### Requirement: An internal node's children are refused before they are linked

An internal node's `children` SHALL be the list the framework's
preparation or presentation last assigned when it linked the node's
children, and the framework assigns it only after the tree's `render()`
and `simulate()` phases have run. Inside an assembly's `render()` or
`simulate()` phase, a read of the `children` of an internal node to which
nothing has yet been assigned — the assembly's own or any other internal
node's — SHALL be refused with a `StructureError`, at the read, naming the
assembly whose phase is running, the phase, what was read
(`self.children`, or the read node's name followed by `.children`), and
what to address instead: the node's declared children by the attributes
that declare them, or, for a node that declares none, its own `render()`,
which builds them. Such a read SHALL NOT answer an empty list.

Every other read SHALL answer as before: a read, in any phase or none,
after the node's children have been assigned SHALL answer the assigned
list; a read outside any phase before they have been assigned SHALL
answer an empty tuple; a leaf's `children` SHALL answer an empty tuple
in every phase.

#### Scenario: A simulate-phase read is refused

- **WHEN** an assembly declaring `near` and `far` reads `self.children`
  in `simulate()` to rotate each child, and the tree is enumerated for the
  first time by `set_state`, the loader, the serializer or `assemble()`
- **THEN** a `StructureError` is raised naming the assembly, `simulate()`,
  `self.children`, and `self.near` and `self.far` as what to address,
  where the read used to answer an empty list and rotate nothing

#### Scenario: A render-phase read is refused

- **WHEN** an assembly's `render()` reads `self.children` to colour its
  children, or reads the `children` of a child internal node it declares
- **THEN** a `StructureError` is raised naming the assembly, `render()`
  and the read, and naming the read node's declared attributes, or, when
  it declares none, saying that its own `render()` builds them

#### Scenario: The same loop over the declared attributes works

- **WHEN** the assembly's `simulate()` rotates `self.near` and `self.far`
  by a driver instead
- **THEN** both children carry the rotation after the first enumeration,
  and nothing is refused

#### Scenario: A read after linking, or outside any phase, is unchanged

- **WHEN** an internal node is read outside any phase before anything has
  linked it, and again after `assemble()` has linked it, both outside any
  phase and inside a later enumeration's phase
- **THEN** the first read answers an empty tuple and every later read
  answers the linked children, as before; a leaf's `children` answers an
  empty tuple inside a phase

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

#### Scenario: A shared base does not route a B-rep adapter through OpenSCAD

- **WHEN** a `CadQueryNode`, a `Build123dNode` or a `Build123dSheetNode` leaf
  is prepared and its STL generated with OpenSCAD's availability check and
  subprocess launch both made to fail
- **THEN** its STL is written and neither the check nor the launch is
  attempted

### Requirement: Empty internal composition

The system SHALL allow a non-rigid `AssemblyNode` to render an empty list or
tuple. Its ordinary assembly lifecycle SHALL complete with an empty SCAD
grouping, its linked `children` SHALL be empty, it SHALL generate no STL of its
own, and serialization SHALL include `children: []`.

A rigid `FusionNode` SHALL require at least one selected child because it
represents one solid and has no valid rigid geometry when its membership is
empty. A zero-child fusion SHALL fail during validation with a diagnostic
naming the fusion, before SCAD, BREP, or STL publication.

#### Scenario: Explicit empty assembly

- **WHEN** an `AssemblyNode.render()` explicitly returns `[]`
- **THEN** `assemble()` succeeds, the node has no linked children, and its
  serialized document contains an empty `children` array

#### Scenario: Empty fusion is refused

- **WHEN** a `FusionNode` returns an empty list or declarative selection
  removes every child
- **THEN** validation raises naming the fusion and explaining that a fusion
  requires at least one rigid child
- **AND** no SCAD, BREP, or STL artifact for that fusion is published

### Requirement: A source-bound leaf names its missing file

A leaf adapter whose part comes from a file outside Python — `StlNode`
(`stl_source`), `StepNode` (`step_source`), `JScadNode` (`jscad_source`) and
`OpenScadNode` (`scad_source`) — SHALL refuse to construct when the file it
declares is not there, and the refusal SHALL name the declaring class, the
attribute and the value declared on it, and the absolute path the framework
resolved that value to.

The refusal SHALL happen when the node is CONSTRUCTED: the same moment at
which a subclass declaring no source file at all is already refused, and the
moment at which the declaration can first be judged. A class body that writes
a child declaration constructs nothing, so declaring such a leaf inside
another node's body SHALL NOT itself fail; the failure arrives when the
parent is instantiated and realizes that child, before any geometry is read
and before any artifact is written.

A resolved path that exists but is not a regular file SHALL be refused in the
same way and SHALL say that it is not a file, rather than being handed to the
mesh or document reader.

Every one of these adapters SHALL also refuse to construct, with
`ValueError`, when the real path its source attribute resolves to is not
under the real path of the project root of the module that declares the
class, whatever expression computed the declared value and whether or not
the file exists. The project root SHALL be found through the kernel-free
manifest module from the declaring module's file, and a module that lies
in no project SHALL NOT be judged. The refusal SHALL name the class, the
attribute and its declared value, the resolved path and the project root,
and SHALL happen at construction, before any source is read or any
process is started for it.

This governs a declaration that was already wrong when the model was loaded.
It SHALL NOT change what happens to a source file that disappears after its
node was constructed: that remains a build failure raised when the node's
sources are read for freshness.

#### Scenario: A declared file that is not there

- **WHEN** a node whose adapter binds it to an external file is constructed,
  and the file that adapter's source attribute names does not exist
- **THEN** construction fails with an error naming the class, the source
  attribute and its declared value, and the absolute path resolved from it,
  and no artifact is written

#### Scenario: The failure arrives when the parent realizes the child

- **WHEN** an assembly's class body declares such a leaf as a child and the
  leaf's file is absent
- **THEN** importing the module holding that class body succeeds, and
  instantiating the assembly fails with that same error

#### Scenario: A declared source that is a directory

- **WHEN** the path a source attribute resolves to exists but is a directory
- **THEN** construction fails saying the path is not a file, naming the class
  and the attribute, rather than the mesh or document reader failing on it
  later

#### Scenario: A source removed after the node was constructed

- **WHEN** a node is constructed with its source file present and the file is
  removed before the build reads its sources for freshness
- **THEN** the build still fails on the missing source exactly as it does
  today; the construction-time check does not apply retroactively

#### Scenario: An OpenSCAD source outside the project

- **WHEN** an `OpenScadNode` subclass declares a `scad_source` that
  resolves, through `../`, to an existing file above its project root
- **THEN** construction raises `ValueError` naming the class,
  `scad_source`, the resolved path and the project root, and OpenSCAD is
  not run

#### Scenario: A JScad source outside the project

- **WHEN** a `JScadNode` subclass declares a `jscad_source` that
  resolves, through a symbolic link, to a file outside its project root
- **THEN** construction raises `ValueError` saying the source lies
  outside the project, and node is not run

#### Scenario: A class outside any project is not judged

- **WHEN** a source-bound leaf is declared in a module with no
  `[tool.machinome]` manifest above it, and its source file exists
- **THEN** construction succeeds as before

### Requirement: No node type is recognised by its class name

The core SHALL NOT decide anything about a node by the spelling of its class
name, or of any class in its method resolution order: no module under
`machinome/` SHALL compare a class's `__name__` or `__qualname__` with a
string literal, nor a string literal naming a class defined under
`machinome/` with any value. What a path needs to know about a node it SHALL
learn from members the node declares or inherits, so a node type written
outside the core is treated exactly as a core type that declares the same
members. A class name MAY be displayed, as in a refusal naming a node and its
class.

#### Scenario: No core module compares a class name to a string

- **WHEN** every module under `machinome/` is parsed and each comparison is
  examined
- **THEN** none compares a `__name__` or `__qualname__` attribute with a
  string literal or a collection of string literals, and none compares a
  string literal that spells a class defined under `machinome/`

#### Scenario: A refusal describes a node by its own class only

- **WHEN** a `Solid2Node` subclass `ScadPart` reaches STL generation with no
  `openscad` on the PATH, and a `LeafNode` subclass `MeshScad` defined outside
  `machinome/` reaches it having published no STL
- **THEN** each refusal names its own node and its own class, and neither
  names `Solid2Node`, another core class or a backend

### Requirement: Each leaf type is one module under the node package

Each leaf type the core ships SHALL be defined at one address directly under
`machinome.node`, named for its technology, and imported from there: a module,
or, for the OpenSCAD node family, the package `machinome.node.openscad`, whose
`__init__` defines the node type and whose other modules are its machinery
under the `openscad-node` capability. Which node types exist, with the class
names each node type's module defines for a project to import, SHALL be stated
once, in the table of supported node types `machinome.node.supported`:

| module | defines |
|---|---|
| `machinome.node.cadquery` | `CadQueryNode` |
| `machinome.node.build123d` | `Build123dNode`, `Build123dSheetNode`, and the reducer of `Svg` artwork |
| `machinome.node.step` | `StepNode`, `StepAssembly`, `solids_from_faces`, `cached_document` |
| `machinome.node.molejo` | `MolejoNode` |
| `machinome.node.solid2` | `Solid2Node` |
| `machinome.node.openscad` (a package) | `OpenScadNode` |
| `machinome.node.jscad` | `JScadNode` |
| `machinome.node.stl` | `StlNode` |

Each of those classes SHALL be imported from its node type's module and from
nowhere else: the node root resolves none of them, and refuses each naming its
module, under the requirement "The node package's root exports nothing".

The package `machinome.node.adapters` SHALL hold no leaf. Importing it, or any
module or name beneath it, SHALL raise `ImportError` at the import line, whose
message names `machinome.node.adapters` as dissolved, states that
`machinome.node.adapters.<x>` is now `machinome.node.<x>` with
`build123d_sheet` folded into `machinome.node.build123d`, and shows the
import to write. It SHALL NOT re-export, alias or forward any name.

#### Scenario: A leaf is imported from its module

- **WHEN** a module runs `from machinome.node.step import StepAssembly,
  StepNode` and `from machinome.node.build123d import Build123dSheetNode`
- **THEN** it receives the classes those modules define, and
  `from machinome.node import StepNode` and
  `from machinome.node import Build123dSheetNode` each raise `ImportError`
  naming `machinome.node.step` and `machinome.node.build123d` respectively

#### Scenario: A former address is refused naming the new one

- **WHEN** a module runs `from machinome.node.adapters.step import
  StepAssembly`, `from machinome.node.adapters import step` or
  `import machinome.node.adapters.cadquery`
- **THEN** each raises `ImportError` whose message names
  `machinome.node.adapters`, the rule `machinome.node.<x>`, and an import
  line to write instead, and no leaf module is imported by the attempt

#### Scenario: The node root's refusals come from the table

- **WHEN** each class name the table of supported node types lists is imported
  from `machinome.node`, and then from `machinome.node.<key>` of its row
- **THEN** the first raises `ImportError` naming `machinome.node.<key>`, the
  second returns the class that module defines, and no class name the table
  lists is in `machinome.node.__all__`

#### Scenario: Two types in one module stay distinct

- **WHEN** `Build123dNode` and `Build123dSheetNode`, both defined in
  `machinome.node.build123d`, are tested against each other with
  `isinstance`
- **THEN** neither is an instance of the other

### Requirement: The node package's root exports nothing

The package `machinome.node` SHALL resolve no name of its own: every class,
function and declaration a project imports from the node package SHALL be
imported from the module that defines it, at one address. Its `__all__` SHALL
be empty, so `from machinome.node import *` binds nothing, and the names its
module namespace binds SHALL be only its submodules, dunder metadata and
private names; it SHALL keep extending its path with node packages installed
as portions.

Each of the twenty-one names the root resolved until the OpenSpec change
`root-cleanup` SHALL be
refused, both as `from machinome.node import <name>` and as an attribute read
of `machinome.node`, with `ImportError` (not `AttributeError`, whose message
the import machinery discards), whose message is exactly

```
module 'machinome.node' has no attribute '<name>': the root of machinome.node exports nothing, and '<name>' is imported from its module, '<module>'. Write `from <module> import <name>`.
```

for the name and module of this table:

| name | module |
|---|---|
| `AssemblyNode` | `machinome.node.assembly` |
| `declared_children` | `machinome.node.declarative` |
| `FusionNode` | `machinome.node.fusion` |
| `SheetLeafNode` | `machinome.node.sheet_leaf` |
| `FlexibleNode` | `machinome.node.flexible` |
| `Marking`, `Wrapped`, `Flat`, `Svg` | `machinome.node.markings` |
| `Frame` | `machinome.node.frames` |
| `property_as_number` | `machinome.node.decorators` |
| `StlRenderStart` | `machinome.node.base` |
| each class name of a row of the table of supported node types (`CadQueryNode`, `Build123dNode`, `Build123dSheetNode`, `StepNode`, `MolejoNode`, `Solid2Node`, `OpenScadNode`, `JScadNode`, `StlNode`) | `machinome.node.<key>` of its row |

The node types' names SHALL be read from the table of supported node types,
never spelled in the root; the refusal SHALL be a lookup of the requested name,
never a comparison with a class's name, and it SHALL decide nothing but the
words of the error. Nothing SHALL alias, re-export or forward a refused name.

The root SHALL keep refusing the port and time-base names under the `ports`
capability, and the package `machinome.node.adapters` SHALL keep refusing
every spelling beneath it, each with its own message. A submodule of the
package SHALL still be reachable through it: `from machinome.node import
supported` and an attribute read `machinome.node.step` return the module, and
a submodule whose kernel is absent raises that module's own refusal,
unmodified. Any other name SHALL raise `AttributeError`.

#### Scenario: A former root name is refused naming its module

- **WHEN** a module runs `from machinome.node import AssemblyNode`
- **THEN** it raises `ImportError` whose message is the sentence above for
  `AssemblyNode` and `machinome.node.assembly`, and binds nothing

#### Scenario: Every former root name is refused

- **WHEN** each of the twenty-one names is imported from `machinome.node`, and
  read with `getattr(machinome.node, name)` and `hasattr(machinome.node, name)`
- **THEN** each raises `ImportError` naming the module of the table, and the
  same name imported from that module is the object the module defines

#### Scenario: The root binds no public name but its submodules

- **WHEN** `machinome.node` is imported and its namespace and `__all__` are read
- **THEN** `__all__` is empty, `from machinome.node import *` binds nothing,
  and every name of the namespace that does not begin with an underscore is a
  submodule of the package

#### Scenario: A submodule is still imported through the package

- **WHEN** a module runs `from machinome.node import supported, phase, step`
- **THEN** it receives the three modules, and where the `step` extra is absent
  the third raises the `step` module's own refusal naming
  `pip install "machinome[step]"`, unmodified

#### Scenario: A table row's classes are refused with their module

- **WHEN** a node type is added to the table of supported node types with its
  class names, and one of them is imported from `machinome.node`
- **THEN** the refusal names `machinome.node.<key>` of the new row, and no
  module of the core but the table spells the class name

