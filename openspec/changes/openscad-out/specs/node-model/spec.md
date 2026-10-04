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
  an assembly of an exact leaf and a `Solid2Node` leaf whose artifacts are
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

An adapter whose backend is a boundary-representation kernel SHALL additionally
expose its geometry exactly, under the `exact-geometry` capability.
`CadQueryNode`, `Build123dNode`, `Build123dSheetNode`, `StepNode` and
`MolejoNode` are
such adapters: each is exact and provides `shape()`.
`Solid2Node`, `OpenScadNode`, `JScadNode` and `StlNode` produce geometry only
as meshes and are not exact. Exposing exact geometry SHALL NOT change an
adapter's presentation or its mesh artifact, so a project that never asks an
exact question is unaffected.

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

- **WHEN** `exact` is read across one instance of each adapter
- **THEN** the `CadQueryNode`, `Build123dNode`, `Build123dSheetNode`,
  `StepNode` and
  `MolejoNode` report true and the `Solid2Node`, `OpenScadNode`,
  `JScadNode` and `StlNode` report false

#### Scenario: Exactness does not disturb the SCAD path

- **WHEN** a `CadQueryNode` is assembled in a project that asks no exact
  question
- **THEN** its presentation and STL artifact are what they were before the
  adapter became exact

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

### Requirement: Each leaf type is one module under the node package

Each leaf type the core ships SHALL be defined at one address directly under
`machinome.node`, named for its technology, and imported from there: a module,
or, for the OpenSCAD node family, the package `machinome.node.openscad`, whose
`__init__` defines the node type and whose other modules are its machinery
under the `openscad-node` capability. Which node types exist, with the class
names the node root resolves for each, SHALL be stated once, in the table of
supported node types `machinome.node.supported`:

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

Every name `machinome.node` exported before this change SHALL still resolve
from `machinome.node` to the identical object, now defined in the module
above; the root's re-exports are struck only by the root cleanup.

The package `machinome.node.adapters` SHALL hold no leaf. Importing it, or any
module or name beneath it, SHALL raise `ImportError` at the import line, whose
message names `machinome.node.adapters` as dissolved, states that
`machinome.node.adapters.<x>` is now `machinome.node.<x>` with
`build123d_sheet` folded into `machinome.node.build123d`, and shows the
import to write. It SHALL NOT re-export, alias or forward any name.

#### Scenario: A leaf is imported from its module

- **WHEN** a module runs `from machinome.node.step import StepAssembly,
  StepNode` and `from machinome.node.build123d import Build123dSheetNode`
- **THEN** it receives the classes, and `StepNode` and `Build123dSheetNode`
  are the objects `machinome.node.StepNode` and
  `machinome.node.Build123dSheetNode` resolve to

#### Scenario: A former address is refused naming the new one

- **WHEN** a module runs `from machinome.node.adapters.step import
  StepAssembly`, `from machinome.node.adapters import step` or
  `import machinome.node.adapters.cadquery`
- **THEN** each raises `ImportError` whose message names
  `machinome.node.adapters`, the rule `machinome.node.<x>`, and an import
  line to write instead, and no leaf module is imported by the attempt

#### Scenario: The node root's node types come from the table

- **WHEN** the names `machinome.node` exports are compared with the names the
  table of supported node types lists, and each is resolved
- **THEN** every class name the table lists is exported and resolves to the
  class its node type's address defines, and every other export is a name the
  node root defines for something that is not a node type

#### Scenario: Two types in one module stay distinct

- **WHEN** `Build123dNode` and `Build123dSheetNode`, both defined in
  `machinome.node.build123d`, are tested against each other with
  `isinstance`
- **THEN** neither is an instance of the other

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
