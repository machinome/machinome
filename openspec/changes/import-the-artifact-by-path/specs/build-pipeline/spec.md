## ADDED Requirements

### Requirement: Generated SCAD imports resolve from the file that holds them

Every import of a build artifact that the system writes into a generated
`.scad` SHALL name that artifact by a path which resolves, from the
directory holding that `.scad` file, to the artifact itself — because that
is how OpenSCAD resolves an `import()`. This SHALL hold for every leaf kind
that presents its geometry as an artifact (`Solid2Node`, the exact adapters,
`StlNode`, `JScadNode`, and a flexible leaf's per-binding snapshot), for a
node at any depth of the tree, whether or not the artifact was already
current when the tree was assembled, and whatever package the importing node
is declared in relative to the node whose artifact it names. An assembly
declared in a different package from a part it places SHALL therefore
render exactly the geometry it renders when the two are declared together.

A path a project itself wrote — a call to `import_stl` inside a project's
own `render()` — SHALL be reproduced exactly as the project wrote it. The
rule governs the artifact imports the framework emits and nothing else.

Where a node's own `.scad` and an ancestor's `.scad` both hold the same
artifact import, each SHALL hold the spelling that resolves from its own
directory; the two files SHALL NOT be required to hold the same text.

#### Scenario: A parent in another package imports every leaf kind

- **WHEN** an assembly declared in `sim/tools/` places a rigid leaf, an
  exact leaf and a flexible leaf all declared in `sim/`, and the model is
  built
- **THEN** every `import(file = …)` in the assembly's generated `.scad`
  names a file that exists relative to that `.scad`'s own directory

#### Scenario: The second build spells it the same way

- **WHEN** that model is built again with every artifact already current
- **THEN** each import in the assembly's generated `.scad` still resolves
  from that `.scad`'s directory, and the geometry the document presents is
  unchanged

#### Scenario: An intermediate assembly's own SCAD resolves from its own directory

- **WHEN** a root in `sim/tools/` places an assembly declared in
  `sim/sub/deep/` which places a leaf declared in `sim/`, and the model is
  built
- **THEN** the import in the intermediate assembly's own generated `.scad`
  resolves from `sim/sub/deep`'s build directory, and the import in the
  root's generated `.scad` resolves from the root's build directory

#### Scenario: A project's own import is reproduced verbatim

- **WHEN** a leaf's `render()` imports a file of the project's own by a
  relative path
- **THEN** the generated `.scad` holds that path exactly as written, with
  no anchoring applied to it

#### Scenario: A parent beside its parts is unchanged

- **WHEN** an assembly and the leaves it places are declared in one package
  and the model is built
- **THEN** each leaf artifact is imported by its bare basename, exactly as
  before this rule was stated
