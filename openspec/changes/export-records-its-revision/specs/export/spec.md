## MODIFIED Requirements

### Requirement: Manifest contract

The manifest SHALL retain the document name `manifest.json` and SHALL declare
`format: "machinome-export"`, `animation: {fps, frames}`, a
`drivers` table, an `instructions` table, and a
`root` tree with the same observable schema and child-name behavior as the
normal-build `viewer.json`. When the exported root declares a time base the
`animation` object SHALL also carry numeric `loop`, the declared seconds of
machine time one turn of `$t` covers, and SHALL omit the key otherwise; the
browser-snapshot document SHALL publish `loop` under the same rule. `loop` is
additive within the current schema version — a consumer that does not read
it plays `frames / fps` as before — and `--fps` / `--frames` keep their
meaning as the timeline's playback resolution. When the exported node's
project root is inside a Git work tree with a commit checked out the manifest
SHALL also carry a top-level `source` object, the record of the revision the
export was made from, and SHALL omit the key otherwise. A rigid node SHALL emit one
`model` reference and
stop recursion; a non-rigid node whose render result is a list or tuple SHALL
recurse into its children; a flexible leaf SHALL emit one `flexible` object
and stop recursion. Each node SHALL carry `name`, `type`, `color`,
`mtime`, and its operations as unevaluated expressions so `$t`
animation is preserved rather than baked to the constants of one instant. A
rigid model reference SHALL be derived relative to the selected build directory
that owns the artifact, SHALL remain rooted beneath the export's `models/`
directory with no parent traversal, and SHALL resolve to a copied artifact so
the export remains portable and self-contained regardless of the caller's
working directory. An artifact outside that build directory SHALL make export
fail before it creates or modifies the requested output. Changes to the shared
tree shape or operation serialization are breaking and MUST bump `version` and
update every producer and consumer of the shared schema together.

When the serialized document contains a subexpression occurring more than
once, the manifest SHALL carry a non-empty `bindings` table beside `drivers`
and `instructions`, under the shared-subexpression requirement above, and SHALL
declare `version: 4`. When it contains no such subexpression the `bindings` key
SHALL be absent and the document SHALL declare `version: 3` when the serialized
tree contains at least one flexible leaf and `version: 2` otherwise — so a
document with nothing to bind is byte-identical to the one published before
bindings existed, and an old consumer refuses only what it genuinely cannot
render.

The bump to `version: 4` SHALL NOT be treated as additive. A consumer ignoring
`bindings` would resolve a binding name to nothing and place the machine in a
wrong pose, so a consumer that cannot resolve the table SHALL refuse the
document rather than render it. Consumers SHALL accept versions 2, 3 and 4.

When the serialized root declares `time = Time.running()` the document SHALL
declare `version: 5` and SHALL carry the `program` object defined by the
requirement "A running root's document publishes the compiled program",
whatever its tree content — the version ladder below 5 is derived from the
CONTENT because flexible leaves and shared subexpressions are properties of
the tree, while a compiled program is a property of the ROOT'S DECLARATION,
and a running root with a trivial program is still a machine a version 4
consumer would animate wrongly. A root declaring no time base or a looping
one SHALL NEVER declare `version: 5`, SHALL NOT carry a `program` key, and
SHALL be byte-identical to the document published before the program existed.

The bump to `version: 5` SHALL NOT be treated as additive. A consumer
ignoring `program` would read a document whose joint placements are bare
coordinate names it can bind nothing to, so a consumer that cannot read
version 5 SHALL refuse the document by name rather than render it or animate
it as a loop.

The `instructions` table SHALL publish, under `version: 5`, EVERY declared
instruction, each entry carrying exactly one of `targets` (where the drivers
land) and `by` (how far they travel from where they stand), both keyed by
qualified driver id and both in design units, beside `duration` in seconds.
Under versions 2, 3 and 4 an instruction stating `by` SHALL continue to be
OMITTED from the table, because a consumer of those versions reads `targets`
off every entry.

A rigid node that declares markings under the `markings` capability SHALL
additionally carry a `markings` list, one entry per declared marking in
declaration order, each entry carrying the marking's `name`, a `model`
reference to its artifact under the same rules and the same portability
guarantee as the node's own `model`, its `color` in `#RRGGBB` form, and its own
`mtime` — the marking artifact's, not the node's, so a consumer that reloads on
change sees a redrawn decal without the part appearing to change. The key SHALL
be ABSENT on a node that declares no marking.

A marking entry SHALL NOT publish its placement: the artifact already holds the
artwork's surface in the part's own frame, so a consumer applies the part's
operations to it exactly as it applies them to the part's model, and no
consumer reproduces the placement arithmetic. A marking SHALL NOT carry a
`piece`, and SHALL NOT appear in the piece inventory.

The `markings` list SHALL be treated as ADDITIVE and SHALL NOT bump `version`.
A consumer that ignores it renders exactly the picture it renders today,
because a marking adds no solid, enters no operation, no binding and no
program, and describes nothing the existing fields describe differently — which
is the `piece` precedent, and the standing rule that a producer emits the
lowest version its content needs. A document whose tree declares no marking
SHALL therefore be byte-identical to the document published before markings
existed.

A published marking artifact's triangles SHALL wind so that each triangle's
normal points **away from the part**: radially outward from the wrap axis for a
`Wrapped` placement, and along the declared `normal` for a `Flat` one. The
promise SHALL hold whatever orientation the drawing tool gave the regions the
artwork was read from. A consumer MAY therefore treat a decal's own vertex and
face normals as the outward direction — to lift it clear of the surface it lies
on, to offset it, or to light it — without inspecting the part the decal
belongs to, and SHALL NOT be required to infer a side from the part's geometry.
This is a promise about the ARTIFACT, not an offset: the surface still sits on
the nominal cylinder or plane with no separation of its own.

The `source` object SHALL carry exactly two keys: `revision`, the full object
name of the commit checked out in the work tree containing the project root —
the root `project_root` gives for the exported node, on which the build
directory is anchored — as `git rev-parse --verify HEAD` prints it, whether
`HEAD` is a branch or detached; and `dirty`, a boolean that SHALL be true
exactly when `git status --porcelain --untracked-files=normal` run at that
root lists anything: a tracked file modified, staged, deleted or renamed, or
an untracked file that is not ignored. A file the repository ignores SHALL
NOT make the record dirty. The record SHALL be taken once, when the export
starts and before it builds, so the export's own build artifacts cannot mark
it dirty, and Git SHALL be asked without writing anything in the repository.
The export SHALL NOT refuse, and SHALL NOT warn about, a dirty tree: exporting
work in progress is normal, and the marker leaves the decision to the
consumer. The key SHALL be ABSENT, with no warning, when the root is not
inside a Git work tree, when the repository has no commit checked out, or when
Git cannot be run; nothing beyond the revision and the marker is recorded.

The `source` object SHALL be treated as ADDITIVE and SHALL NOT bump `version`.
A consumer that ignores it renders exactly the picture it renders today,
because a source record adds no solid, enters no operation, no binding and no
program, and describes nothing the existing fields describe differently —
which is the `piece` precedent, and the standing rule that a producer emits
the lowest version its content needs. An export whose project root is not
inside a Git work tree SHALL therefore be byte-identical to the document
published before the source record existed.

#### Scenario: A running root's document declares version 5

- **WHEN** a root declaring `time = Time.running()` is exported
- **THEN** `manifest.json` declares `version: 5` and carries a `program`
  object beside `drivers`, `instructions` and `bindings`

#### Scenario: An untimed document is unchanged in every byte

- **WHEN** a root declaring no time base, and one declaring
  `time = Time(loop=2.0)`, are exported
- **THEN** neither document carries a `program` key, each declares the
  version its content already needed, and each is byte-identical to the
  document exported before this change

#### Scenario: Both instruction forms are published under version 5

- **WHEN** a running root declares `Instruction(by={'crank': 10.0},
  duration=0.5)` beside `Instruction({'crank': 40.0}, duration=0.5)`
- **THEN** the version 5 document's `instructions` table has an entry for
  each, the first carrying `by` and no `targets`, the second carrying
  `targets` and no `by`, both keyed by qualified driver id

#### Scenario: A relative instruction stays out of a version 4 table

- **WHEN** an untimed root declares only relative instructions
- **THEN** its document's `instructions` table is empty and the rest of the
  document is unchanged

#### Scenario: A declared time base is exported

- **WHEN** a root declaring `time = Time(loop=43200)` is exported
- **THEN** `manifest.json` carries `animation.loop == 43200` beside the
  requested `fps` and `frames`, its version is unchanged by the key, and its
  operations carry `$t` multiplied by the loop rather than a constant

#### Scenario: An undeclared root exports no loop

- **WHEN** a root declaring no time base is exported
- **THEN** `manifest.json`'s `animation` object has no `loop` key and is
  byte-identical to the manifest exported before this change

#### Scenario: A document with nothing shared is unchanged

- **WHEN** a tree whose expressions repeat no subexpression is exported
- **THEN** `manifest.json` has no `bindings` key, declares the version its
  content already needed, and is byte-identical to the manifest exported
  before bindings existed

#### Scenario: A document with sharing declares the new version

- **WHEN** a tree whose expressions repeat a subexpression is exported
- **THEN** `manifest.json` declares `version: 4` and carries a non-empty
  `bindings` array

#### Scenario: A flexible document with sharing declares the new version

- **WHEN** a tree holding a flexible leaf and repeating a subexpression is
  exported
- **THEN** `manifest.json` declares `version: 4` rather than `3`, and its
  flexible leaf's `params` may reference the table

#### Scenario: Export starts in a project subdirectory

- **WHEN** a project model is exported from a working directory below its
  project root to an output directory elsewhere
- **THEN** every model reference contains no parent traversal and resolves to
  its copied artifact beneath the output's `models/` directory

#### Scenario: Export uses a configured or selected build directory

- **WHEN** export uses a relative configured build root or a named model's
  selected build directory
- **THEN** model references preserve artifact paths relative to that resolved
  directory and resolve beneath the export's `models/` directory

#### Scenario: A model artifact is outside its build directory

- **WHEN** a rigid node names an STL whose canonical path is outside its
  resolved build directory
- **THEN** direct export raises `ExportModelPathError`, CLI export exits
  nonzero with that diagnostic, and the requested output is not created or
  modified

#### Scenario: A part publishes the markings it carries

- **WHEN** a rigid node declaring `digits` and then `arrows` is exported
- **THEN** its entry carries a `markings` list of two entries in that order,
  each with `name`, `model`, `color` and `mtime`, and neither carries a
  placement or a `piece`

#### Scenario: A consumer reads a decal's outward side off the decal

- **WHEN** a document publishing a wrapped marking and a flat marking is read
  and each marking artifact's face normals are computed
- **THEN** every wrapped face normal points away from its wrap axis and every
  flat face normal points along the placement's declared normal, so displacing
  each vertex along its own normal moves the decal clear of the part and never
  into it

#### Scenario: A document with no marking is unchanged in every byte

- **WHEN** a tree whose parts declare no marking is exported
- **THEN** no node's entry has a `markings` key, the document declares the
  version its content already needed, and it is byte-identical to the
  manifest exported before markings existed

#### Scenario: A marking's mtime is its own

- **WHEN** a marking's artwork is edited and the project is exported again
- **THEN** that marking entry's `mtime` has moved and the node's own `mtime`
  and `model` have not

#### Scenario: The picture is unchanged for a consumer that ignores markings

- **WHEN** a consumer written against the previous document reads a document
  whose parts carry markings
- **THEN** it finds the same `format`, `version`, `animation` and `root` tree,
  with every previously published node field unchanged

#### Scenario: The OpenSCAD renderer does not draw markings

- **WHEN** a model whose parts declare markings is photographed with the
  OpenSCAD snapshot renderer, or opened by `machinome develop` without the viewer
  extra
- **THEN** it renders exactly as the same model without the markings, and
  neither the build nor the render fails

#### Scenario: An export of a committed project records its revision

- **WHEN** a project whose root is a Git work tree with one commit and
  nothing modified or untracked is exported
- **THEN** `manifest.json` carries `source` with `revision` equal to that
  commit's full hash and `dirty` false, and declares the version its content
  already needed

#### Scenario: A modified tracked file marks the record dirty

- **WHEN** a tracked source file of that project is modified and the project
  is exported again
- **THEN** `source.revision` is the same commit and `source.dirty` is true,
  and the export is written

#### Scenario: An untracked file marks the record dirty

- **WHEN** a file that is neither tracked nor ignored is added to the
  committed project and it is exported
- **THEN** `source.dirty` is true

#### Scenario: An ignored file leaves the record clean

- **WHEN** the committed project holds only files its `.gitignore` ignores
  beside its tracked ones, including the build directory of an earlier export
- **THEN** `source.dirty` is false

#### Scenario: An export outside a repository is unchanged in every byte

- **WHEN** a project whose root is not inside any Git work tree is exported
- **THEN** `manifest.json` has no `source` key, nothing warns, and its bytes
  equal the manifest the same project exported before the source record
  existed

#### Scenario: No commit and no Git record nothing

- **WHEN** the project root is a Git repository with no commit yet, or the
  `git` executable cannot be found
- **THEN** no source record is taken and nothing warns
