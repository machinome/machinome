## MODIFIED Requirements

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
`machinome.node.sources`: `require_source_file` to refuse an undeclared,
missing or out-of-project file at construction, under the `node-model`
capability; `source_closure` to add a wrapper module's import closure to
`files`; and the mixin `ExternalSourceIdentity`, which makes the wrapper
module's project-relative path part of the node's artifact identity, as
ADR-155 specifies. A leaf that reads a foreign file while rendering SHALL tie
the read to the active source generation with `consumed_source` or
`coherent_read` from `machinome.source_generation`, and a node refusing a
changed source raises that module's `SourceChanged`. These members are
declared for leaves even though the project contract that `vet` enforces
does not offer `machinome.source_generation` to a project.

`require_source_file(klass, attribute, declared, path=None)` SHALL refuse a
`declared` value that names no file — `None` or an empty string — first,
before anything else, in the shape the `node-model` capability states. Called
with the declared value alone, it SHALL resolve that value against the
directory of the module defining `klass`, an absolute value resolving to
itself, judge the resolved path, and return it. Called with a `path` its
caller resolved, it SHALL judge that path as it always has and return it. A
leaf that resolves its declaration through the first form refuses an
undeclared source without joining it itself.

#### Scenario: A source recipe alone makes artifacts stale

- **WHEN** a B-rep leaf declaring a `source_recipe` is built, and is then
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

#### Scenario: A declaration given alone is resolved beside its module

- **WHEN** a leaf calls `require_source_file(type(self), 'mesh_source',
  self.mesh_source)` with `mesh_source = 'part.stl'` declared in a module
  whose directory holds `part.stl`
- **THEN** the call returns the real absolute path of that file, the path
  the four-argument call would have been given, and a subclass declaring no
  `mesh_source` is refused with `ValueError` naming it and `mesh_source`
