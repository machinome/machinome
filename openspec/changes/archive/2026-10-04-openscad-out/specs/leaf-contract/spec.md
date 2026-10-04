## MODIFIED Requirements

### Requirement: The leaf bases are declared extension points

The system SHALL declare four leaf bases as the extension points through which
a node type outside the core produces geometry, each at exactly one import
path, the module that defines it:

- `LeafNode` at `machinome.node.leaf`, for every leaf, and the base a faceted
  leaf subclasses;
- `ExactLeafNode` at `machinome.node.exact_leaf`, for a leaf whose geometry is
  exact;
- `SheetLeafNode` at `machinome.node.sheet_leaf`, for an exact leaf cut from
  sheet stock;
- `FlexibleNode` at `machinome.node.flexible`, for a leaf whose shape is a
  function of its bound ports.

Each base declares these members, in addition to those of the base it
extends:

- `LeafNode`: `render`, `validate`, `namespace`, `present`, `presentation`,
  `materialize`, `generate_stl`, `kept_artifacts`, `publish_artifact`,
  `get_source_file`, `files`, `source_recipe`, `artifact_import`, `basepath`,
  `local_stl`, `stl_file`, `model`, `rigid`, `flexible`, `exact`, `optimize`,
  `base_mesh`, `declared_markings`, `leaf_contract`, and the signal
  `StlRenderStart` (`machinome.node.base`) a leaf rendering its STL in a
  subprocess raises;
- `ExactLeafNode`: `shape_from_rendered`, `linear_deflection`,
  `angular_deflection`, `exact`, `shape`, `brep_file`;
- `SheetLeafNode`: `profile`, `profile_faces`, `lies_on_xy_plane`, `extrude`,
  `write_dxf`, `thickness`, `validated_profile`, `dxf_file`;
- `FlexibleNode`: `tech`, `shape_parameters`, `shape_spec`, `snapshot_mesh`,
  `snapshot_stl`, `snapshot_shape`, `exact`.

`files`, `basepath`, `local_stl`, `stl_file`, `brep_file`, `dxf_file` and
`model` are instance attributes set by the base's constructor; the others are
class members. No declared member names a modelling technology.

A subclass that uses only the members this capability declares SHALL be a
complete node of its kind: it SHALL take part in the tree, preparation,
artifact currency, assembly, fusion, export, the viewer document and the
test framework exactly as the core's own adapters of that kind do, with no
change to the core. The declared members are the public names this capability
lists; a member whose name begins with an underscore is never part of the
contract.

Each base's docstring SHALL state that it is a declared extension point and
name this capability, and the API reference SHALL document each base with its
declared members.

#### Scenario: A faceted leaf written outside the core

- **WHEN** a module outside `machinome/` defines a `LeafNode` subclass that
  renders from a committed mesh file, publishes its STL through
  `publish_artifact` and uses no member whose name begins with an underscore
- **THEN** a project of that leaf builds with no CAD tool on the PATH, its
  STL artifact is written with its source record, a second build reuses it
  without rendering, and the mesh-based assertions compare it like any other
  rigid leaf

#### Scenario: An exact leaf written outside the core

- **WHEN** a module outside `machinome/` defines an `ExactLeafNode` subclass
  whose `render()` returns the exact engine's currency and that declares no
  `namespace` and overrides nothing
- **THEN** it builds its `.brep` and `.stl`, its `shape()` is that solid,
  it fuses exactly with a core adapter's leaf, and an exact assertion
  reaches its verdict on it

#### Scenario: The bases document themselves as extension points

- **WHEN** the docstrings of `LeafNode`, `ExactLeafNode`, `SheetLeafNode` and
  `FlexibleNode` are read
- **THEN** each says it is a declared extension point and names the
  `leaf-contract` capability, and none says it is framework-internal

#### Scenario: Every declared member exists and is public

- **WHEN** the members this capability declares for each base are looked up
  on that base, or on an instance of it for an instance attribute
- **THEN** each exists, none of their names begins with an underscore, and
  the base's docstring lists exactly the members declared for it

### Requirement: What a leaf provides, by kind

A subclass SHALL provide its geometry through the members of its kind, and
the core SHALL do everything else:

- **Every leaf** implements `render()`, returning one geometry object, never a
  list and never `None`. It MAY extend `validate(rendered)`, calling the
  base's first. Its exactness is fixed by its type.
- **A faceted leaf** produces its own STL: it implements
  `materialize(rendered)` and writes `stl_file` through `publish_artifact`,
  or, when its tool runs as a subprocess, implements `generate_stl()` to
  start it and raise `StlRenderStart`. It need not implement `present`: the
  base presents its artifact by `artifact_import(local_stl)`, materializing it
  first when it is not current. A leaf that does implement `present` returns
  the core's description of an import of its artifact, or the object it
  authored. A leaf whose STL is still not current after its materialization
  is refused under the `node-model` capability, naming it; the core hands no
  leaf to another tool. A leaf of the OpenSCAD node family subclasses that
  package's leaf base, under the `openscad-node` capability, which writes its
  `.scad` and renders its STL with OpenSCAD.
- **A leaf that keeps an artifact beyond its STL, BREP and markings**
  declares its path in `kept_artifacts()`, and the build keeps it while the
  leaf is in the published tree.
- **An exact leaf** returns from `render()` an object its conversion hook
  `shape_from_rendered(rendered)` turns into the exact engine's currency; the
  default hook admits whatever the engine admits as its currency, and a
  subclass whose front end returns something else overrides the hook. It MAY
  declare `linear_deflection` and `angular_deflection` as class attributes.
  The core writes its `.brep` and `.stl` and serves `shape()`.
- **A sheet leaf** implements `profile()` and the four backend hooks
  `profile_faces(profile)`, `lies_on_xy_plane(face)`, `extrude(face)` and
  `write_dxf(face, path)`, the last writing the cut file to the path it is
  given. `render()` is the base's and SHALL NOT be overridden.
- **A flexible leaf** declares one port per shape parameter, declares `tech`,
  returns its backend's shape object from `render()`, and implements the five
  backend hooks `shape_parameters(rendered)`, `shape_spec(rendered)`,
  `snapshot_mesh(rendered, values)`, `snapshot_stl(rendered, values)` and,
  when it declares `exact` true, `snapshot_shape(rendered, values)`.

A subclass MAY extend `materialize(rendered)` on any base by calling the
base's implementation; the artifacts it then holds are the ones the base
published.

A subclass that declares its own metaclass SHALL derive it from the metaclass
of the base it subclasses (`NodeMeta`, at `machinome.node.declarative`).

#### Scenario: A SCAD-presented faceted leaf needs no producer of its own

- **WHEN** a subclass of the OpenSCAD node family's leaf base implements only
  `render()` returning a solid2 object, and is built with OpenSCAD available
- **THEN** its `.scad` is written by the family's leaf base and its STL is
  rendered by OpenSCAD from it, and a `LeafNode` subclass that implements only
  `render()` and an `as_scad()` method is refused for producing no STL

#### Scenario: A leaf presents its own artifact by artifact_import

- **WHEN** a `LeafNode` subclass implements `materialize()` publishing its
  STL and `present()` returning `self.artifact_import(self.local_stl)`
- **THEN** it is assembled, and when its parent's `.scad` is generated with
  the OpenSCAD node package installed, that SCAD imports the artifact by a
  path that resolves from the parent's `.scad` directory, exactly as a core
  adapter's does; a build writes no `.scad` for the leaf itself

#### Scenario: A self-materializing faceted leaf needs no SCAD hook

- **WHEN** a `LeafNode` subclass implements `render()` and `materialize()`
  publishing its STL, and no `present()`
- **THEN** it is assembled, and its presentation imports its STL artifact

#### Scenario: A sheet leaf supplies the four hooks

- **WHEN** a `SheetLeafNode` subclass implements `profile()` and the four
  backend hooks by their public names
- **THEN** it builds its STL, BREP and DXF, and the sheet rules of the
  `sheet-parts` capability refuse its authoring mistakes as they refuse
  `Build123dSheetNode`'s

#### Scenario: A flexible leaf supplies the five hooks

- **WHEN** a `FlexibleNode` subclass declares a port per parameter, its `tech`,
  and implements the five backend hooks by their public names
- **THEN** it is published in the document as a flexible object, its snapshot
  STL is written per binding, and its `shape()` is evaluated at the bound
  instant, as `MolejoNode`'s are under the `flexible-parts` capability

#### Scenario: Extending materialize keeps the base's artifacts

- **WHEN** an `ExactLeafNode` subclass extends `materialize()` and calls the
  base's implementation inside it
- **THEN** the `.brep` and `.stl` written are those the base would have
  written, with the same stamps and source records

### Requirement: What the core guarantees a leaf

For a subclass that keeps to the contract, the core SHALL guarantee:

- its artifact paths, `stl_file` and, for an exact leaf, `brep_file`, named
  from its source file and its parameter-hashed `uniq_id`, under its
  project's build directory, with `basepath` their common stem, under which a
  leaf names any other artifact it keeps, and `local_stl` the STL's name for
  an import in a presentation;
- that every artifact it declares in `kept_artifacts()` survives the build's
  sweep while it is in the published tree;
- that each artifact is produced only when it is not current, is stamped with
  the node's `mtime_ns`, carries the record of its sources, and replaces the
  previous artifact by rename, so a reader never sees a partial file;
- for an exact leaf, `exact` true, `shape()` in the node's local frame in the
  engine's currency, reloaded from a current `.brep` without rendering, and
  never a stale shape for a replaced `.brep` (the `exact-geometry`
  capability);
- its place in the tree: naming from the parent's attribute, placement
  operations, joints and frames, and its entry in the viewer document;
- that the exact engine is resolved only on the paths the
  `exact-engine-dependency` capability lists.

No subclass SHALL need to evict, invalidate or reset a core cache to keep
these guarantees.

#### Scenario: A replaced artifact needs no eviction by the subclass

- **WHEN** an exact leaf's `.brep` is replaced by the core's publication under
  an unchanged source mtime and the leaf's `shape()` is read again in the
  same process
- **THEN** the new shape is returned without the subclass calling anything to
  invalidate the old one

### Requirement: The contract is versioned and a declaration is checked

The core SHALL declare one integer, the leaf contract version it speaks, as
`CONTRACT` in `machinome.node.leaf`, which is `2`: version 2 removed `as_scad`,
`scad_file` and `generate_scad` from `LeafNode`, declared `present` and the
capability set of "A leaf declares its kind as one set on the leaf base", and
changed `generate_stl`, which no longer hands a leaf to OpenSCAD. A change to the meaning of a declared
member, or the removal of one, SHALL change that number in the same change.

A class MAY declare the version it was written against as the class attribute
`leaf_contract`, as an integer literal in its own body. When a subclass of
`LeafNode` declares `leaf_contract` in its own body, the system SHALL compare
it with `CONTRACT` when the class is created and, when they differ or the
declared value is not an integer, SHALL raise `TypeError` naming the class,
the version it declares, the version the core speaks and
`machinome.node.leaf`, so the class does not exist. A class that does not
declare `leaf_contract` in its own body is not checked; a subclass inherits
its parent's declaration without being checked again.

#### Scenario: A matching declaration is admitted

- **WHEN** a `LeafNode` subclass declares `leaf_contract = 2` and the core
  speaks 2
- **THEN** the class is created and its instances build normally

#### Scenario: A mismatched declaration is refused naming both versions

- **WHEN** an `ExactLeafNode` subclass declares `leaf_contract = 1` and the
  core speaks 2
- **THEN** defining the class raises `TypeError` naming the class, 1, 2 and
  `machinome.node.leaf`

#### Scenario: A project leaf declares nothing and is not checked

- **WHEN** a project defines a `CadQueryNode` subclass with no
  `leaf_contract`
- **THEN** the class is created as before, and so is a subclass of a class
  that declared a matching version

## ADDED Requirements

### Requirement: A leaf declares its kind as one set on the leaf base

What the core asks a node of a leaf kind SHALL be one set of members, declared
with a default on the node base so every node answers, and documented together
on `LeafNode` with this meaning:

- `rigid`, a class attribute: the node is a time-invariant solid with a cached
  STL, in the piece and artifact sets;
- `flexible`, a class attribute: its shape is a function of its bound ports;
- `exact`, a property: it exposes boundary-representation geometry through
  `shape()`;
- `optimize`, a class attribute: a presentation imports its STL when true, and
  carries what it rendered when false, in which case it is prepared on every
  build;
- `present(rendered)`: its presentation of one render; `presentation()`: its
  own presentation, its artifact imports resolving from its own build
  directory;
- `kept_artifacts()`: the paths of the artifacts beyond its STL, BREP and
  markings that a build keeps for it, `()` by default;
- `generate_stl()`: make its STL current;
- `stl_file`, `brep_file`, `basepath`, `local_stl`: its artifact paths;
- `base_mesh()`: its geometry in its own frame; `declared_markings()`: its
  declared markings.

No member of the set SHALL name a modelling technology. No module of the core
SHALL ask a node for a member of the set through `getattr` with a default or
through `hasattr`: it SHALL read the member, and a stand-in for a node, in the
framework's own suite, SHALL declare the members the code it stands in for
reads.

#### Scenario: The core reads the set directly

- **WHEN** every module under `machinome/` is parsed for calls of `getattr`
  with three arguments and of `hasattr` whose attribute is a member of the set
- **THEN** none is found

#### Scenario: A leaf written outside the core answers the whole set

- **WHEN** a `LeafNode` subclass defined outside `machinome/` that declares
  only `render()` and `materialize()` is asked each member of the set
- **THEN** each answers with the base's default meaning: rigid, not flexible,
  not exact, optimizing, presenting an import of its STL, keeping no other
  artifact

#### Scenario: A kept artifact survives the sweep by declaration

- **WHEN** a leaf whose `kept_artifacts()` names a file beside its STL is built
  and the build publishes and sweeps
- **THEN** that file is still present while the leaf is in the tree, and gone
  after a build of a tree without the leaf, with no rule of the sweep naming
  its suffix
