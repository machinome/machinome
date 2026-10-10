## ADDED Requirements

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

- `LeafNode`: `render`, `validate`, `namespace`, `as_scad`, `materialize`,
  `publish_artifact`, `get_source_file`, `files`, `source_recipe`,
  `artifact_import`, `basepath`, `local_stl`, `scad_file`, `stl_file`,
  `model`, `generate_scad`, `leaf_contract`;
- `ExactLeafNode`: `shape_from_rendered`, `linear_deflection`,
  `angular_deflection`, `exact`, `shape`, `brep_file`;
- `SheetLeafNode`: `profile`, `profile_faces`, `lies_on_xy_plane`, `extrude`,
  `write_dxf`, `thickness`, `validated_profile`, `dxf_file`;
- `FlexibleNode`: `tech`, `shape_parameters`, `shape_spec`, `snapshot_mesh`,
  `snapshot_stl`, `snapshot_shape`, `exact`.

`files`, `basepath`, `local_stl`, `scad_file`, `stl_file`, `brep_file`,
`dxf_file` and `model` are instance attributes set by the base's constructor;
the others are class members.

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
- **A faceted leaf presented as SCAD** implements `as_scad(rendered)`,
  returning a solid2 object. The core writes that SCAD and OpenSCAD produces
  the STL from it.
- **A faceted leaf that produces its own STL** implements
  `materialize(rendered)` and writes `stl_file` through `publish_artifact`.
  It need not implement `as_scad`: the core presents its artifact.
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

- **WHEN** a `LeafNode` subclass implements only `render()` and `as_scad()`
  returning a solid2 object, and is built with OpenSCAD available
- **THEN** its `.scad` is written by the core and its STL is rendered by
  OpenSCAD from it

#### Scenario: A self-materializing faceted leaf needs no SCAD hook

- **WHEN** a `LeafNode` subclass implements `render()` and `materialize()`
  publishing its STL, and no `as_scad()`
- **THEN** it is assembled, and its SCAD presentation imports its STL artifact

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

### Requirement: The namespace guard is optional

A leaf MAY declare `namespace`, a module prefix. When it does, validation
SHALL refuse a render result whose type's module does not start with that
prefix, naming the node, the namespace and the type, before any artifact is
written. When it declares none, no module check is made.

`ExactLeafNode` SHALL declare no namespace. An exact leaf whose render returns
the engine's currency SHALL be admitted without declaring one: admission of
an exact render is the conversion hook's, under the `exact-geometry`
capability, and does not depend on the module of the kernel binding.

#### Scenario: A declared namespace refuses a foreign render

- **WHEN** a leaf declaring `namespace = 'solid2'` renders an object from
  another library
- **THEN** validation raises naming the node, `solid2` and the type, and no
  artifact is written

#### Scenario: An exact leaf rendering the engine's currency declares nothing

- **WHEN** an `ExactLeafNode` subclass with no `namespace` renders the
  engine's currency
- **THEN** it is validated, converted and built as if it had declared the
  binding's module

### Requirement: A leaf publishes an artifact through one call

`LeafNode.publish_artifact(path, write)` SHALL be the one way a leaf writes an
artifact of its own. `path` SHALL be one of the node's artifact paths: a path
beginning with the node's `basepath`; any other path SHALL be refused naming
the node and the path, before `write` is called.

When the artifact at `path` is current for the node's sources, the call SHALL
do nothing, SHALL NOT call `write`, and SHALL return false. Otherwise it SHALL
call `write` with a temporary path in the artifact's directory, then stamp
that file with the node's `mtime_ns` and put it in place of `path` together
with the record of the node's `source_digest` and `source_fingerprint`, in the
one step the core uses for every artifact, and SHALL return true. If `write`
raises, nothing SHALL be published: the previous artifact and its record stay
as they were, and the temporary file is removed.

A file published this way SHALL be byte for byte, and record for record,
what the core's own publication writes for the same content.

#### Scenario: A stale artifact is written and recorded

- **WHEN** a leaf whose STL is absent calls `publish_artifact(stl_file,
  write)`
- **THEN** `write` is called once with a temporary path, the STL is in
  place stamped with the node's `mtime_ns`, its source record names the
  node's digest and fingerprint, and the call returns true

#### Scenario: A current artifact is not rewritten

- **WHEN** a leaf whose STL is current calls `publish_artifact(stl_file,
  write)`
- **THEN** `write` is not called, the file's observation is unchanged, and
  the call returns false

#### Scenario: A failing writer publishes nothing

- **WHEN** `write` raises
- **THEN** the error propagates, the previous artifact and its record are
  unchanged, and no temporary file is left in the directory

#### Scenario: A path that is not the node's is refused

- **WHEN** a leaf calls `publish_artifact` with a path outside its
  `basepath`
- **THEN** the call raises naming the node and the path, and `write` is not
  called

### Requirement: A leaf states its source identity through declared members

A node's sources SHALL be stated through three declared members, and the
core SHALL derive every artifact's stamp and source record from them:

- `get_source_file()`: the file the node's build directory and artifact names
  are anchored on, the node's defining module by default. A leaf whose part
  comes from a file outside Python overrides it to return that file, and sets
  whatever attribute that file is declared by before calling the base's
  constructor, which reads it.
- `files`: the node's tracked source set. A subclass MAY add contributors to
  it after the base's constructor has run.
- `source_recipe`: what decides the node's artifacts beyond its tracked
  files, as a string, or `None`, the default. A node declaring one SHALL have
  it folded into the source digest and the source fingerprint of every
  artifact it publishes, so changing the recipe alone makes those artifacts
  stale. A node declaring `None` SHALL have exactly the digest and
  fingerprint it had before this member existed. `source_recipe` is read
  whenever the core computes the node's digest or fingerprint, so a node MAY
  raise `SourceChanged` from it to refuse a source generation that is no
  longer the one it was built from.

`mtime_ns`, `source_digest` and `source_fingerprint` are derived by the core
and SHALL NOT be overridden.

A leaf whose part comes from a file outside Python SHALL use, from
`machinome.node.sources`: `require_source_file` to refuse a missing or
out-of-project file at construction, under the `node-model` capability;
`source_closure` to add a wrapper module's import closure to `files`; and the
mixin `ExternalSourceIdentity`, which makes the wrapper module's
project-relative path part of the node's artifact identity, as ADR-155
specifies. A leaf that reads a foreign file while rendering SHALL tie the read
to the active source generation with `consumed_source` or `coherent_read`
from `machinome.source_generation`, and a node refusing a changed source
raises that module's `SourceChanged`. These members are declared for leaves
even though the project contract that `vet` enforces does not offer
`machinome.source_generation` to a project.

#### Scenario: A source recipe alone makes artifacts stale

- **WHEN** an exact leaf declaring a `source_recipe` is built, and is then
  constructed again with the same tracked files and a different recipe
- **THEN** its `.brep` and `.stl` are not current, and building writes them
  again with the new digest and fingerprint recorded

#### Scenario: No recipe changes nothing

- **WHEN** a node that declares no `source_recipe` is built
- **THEN** its artifacts' bytes, stamps and source records are those it had
  before `source_recipe` existed

#### Scenario: The recipe reaches every artifact of the node

- **WHEN** a node declaring a `source_recipe` publishes a `.scad`, an `.stl`,
  a `.brep` or a marking artifact
- **THEN** each artifact's recorded digest and fingerprint include the recipe

#### Scenario: An external-file leaf keeps its identity under the public mixin

- **WHEN** `StlNode`, `StepNode`, `OpenScadNode` and `JScadNode` mix in
  `ExternalSourceIdentity`
- **THEN** every artifact name they produce is the one they produced with the
  private mixin before

### Requirement: What a subclass must not override

A subclass SHALL NOT override the framework's lifecycle or currency:
`assemble()`, `shape()` on `ExactLeafNode`, `render()` on `SheetLeafNode`,
`mtime_ns`, `mtime`, `source_digest`, `source_fingerprint`, `uniq_id`,
`children`, `time`, or any member whose name begins with an underscore. What a
subclass overrides beyond the members this capability declares is outside the
contract, and the core makes no promise about it across contract versions.

#### Scenario: The FreeCAD stand-in overrides only declared members

- **WHEN** the members the validated machinome-freecad leaf defines are
  compared with this capability's declared members
- **THEN** every member it overrides is a declared one

### Requirement: What the core guarantees a leaf

For a subclass that keeps to the contract, the core SHALL guarantee:

- its artifact paths, `scad_file`, `stl_file` and, for an exact leaf,
  `brep_file`, named from its source file and its parameter-hashed
  `uniq_id`, under its project's build directory, with `basepath` their
  common stem and `local_stl` the STL's name for a SCAD import;
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
`CONTRACT` in `machinome.node.leaf`. A change to the meaning of a declared
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

- **WHEN** a `LeafNode` subclass declares `leaf_contract = 1` and the core
  speaks 1
- **THEN** the class is created and its instances build normally

#### Scenario: A mismatched declaration is refused naming both versions

- **WHEN** an `ExactLeafNode` subclass declares `leaf_contract = 2` and the
  core speaks 1
- **THEN** defining the class raises `TypeError` naming the class, 2, 1 and
  `machinome.node.leaf`

#### Scenario: A project leaf declares nothing and is not checked

- **WHEN** a project defines a `CadQueryNode` subclass with no
  `leaf_contract`
- **THEN** the class is created as before, and so is a subclass of a class
  that declared a matching version
