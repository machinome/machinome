## MODIFIED Requirements

### Requirement: Build artifact layout

The system SHALL write build artifacts under a build directory, mirroring the
source file's directory, with basename `<script-name>-<uniq_id>`. The
project's **build root** is `$SOLID_BUILD_DIR` (default `_build`): a relative
value, and the default, SHALL resolve against the discovered project root and
never against the working directory, and an absolute value SHALL be used as
given.

For a project that declares no models, the build directory SHALL be the build
root itself, exactly as today. For a declared model, the build directory SHALL
be `<build root>/<name>/`, so that each declared model has its own published
`viewer.json`, its own `errors.json`, its own build lock and its own artifact
sweep, and publishing one model neither replaces nor removes another's
artifacts. A reference that is not a declared model — a sub-node named by
qualifier or path — SHALL build in the build root, as it does today, and the
build root's artifact sweep SHALL NOT descend into a declared model's
directory. A build lock file that lies inside a build directory SHALL be spared
by that directory's sweep.

Whichever directory a command was run from, a project therefore has one build
directory per model and — because the build lock is derived from it — one
build lock per model.

A build SHALL write a `.scad` (base geometry, no transforms) only for a leaf
of the OpenSCAD node family — a `Solid2Node`, an `OpenScadNode`, or another
subclass of the family's leaf base — because OpenSCAD renders that leaf's
`.stl` from it; the family leaf writes it through the OpenSCAD node package
(the `openscad-node` capability). It SHALL write no `.scad` for an assembly, a
fusion, a flexible leaf or any other leaf, whatever is installed, and SHALL log
nothing about SCAD. The root's `.scad` is written in the build directory
only by `machinome snapshot --renderer openscad`, under the `web-snapshot`
capability, which removes it once rendered; it is not a build artifact. Geometry/document-only consumers under
`backend-neutral-materialization` SHALL NOT require or generate assembly SCAD,
but SHALL still produce SCAD source when a selected backend needs it. Other
artifacts remain `.stl` (rendered) and `.stl.lock` during
external rendering. A node that is exact under the `exact-geometry` capability
SHALL additionally write
`.brep`, holding that node's unplaced exact geometry under the same basename.
World-space spatial math does not use on-disk artifacts — the `mesh`
property loads the plain `.stl` and applies operations in memory (the
`.mesh.stl` path attribute exists but is vestigial; nothing writes or reads
it). Every build directory SHALL be an ordinary directory
that every builder writes into directly; the system SHALL NOT publish through
a symlink, a versioned sibling directory, or a private candidate copy. A build
path left as a symlink by an earlier layout SHALL be converted by moving the
directory that symlink references into the ordinary build path. Build
preparation SHALL NOT remove any other path merely because its name begins
with the build directory's name and a dot.

A rigid node that declares markings under the `markings` capability SHALL
additionally write one artifact per marking under that same basename,
distinguished by the marking's own declared name, so two markings on one part
never collide and the file says which declaration produced it. Unlike the
`.brep`, a marking artifact IS named by the published document, and it is
published, coloured and copied on export like a model.

The `.brep` artifact SHALL be private to the build. No viewer snapshot, export
manifest, or other published document SHALL reference it, and its presence
SHALL NOT alter any document's schema.

#### Scenario: Custom build dir

- **WHEN** `SOLID_BUILD_DIR` is set in the environment
- **THEN** all artifacts, and `errors.json`, are written under that
  directory instead of `_build`

#### Scenario: One build directory whatever the working directory

- **WHEN** a project is built from its root and then from a subdirectory
- **THEN** both builds publish into the same build directory and contend for
  the same build lock

#### Scenario: Consumer reads through the build path

- **WHEN** a consumer opens the published viewer snapshot at the build path
- **THEN** it reads the snapshot without resolving a symlink or naming any
  other directory

#### Scenario: Project published under the previous layout

- **WHEN** a project whose build path is a symlink to a versioned directory is
  built
- **THEN** the build path becomes an ordinary directory holding the artifacts
  from the referenced directory, that referenced sibling is consumed, and
  every other sibling remains untouched

#### Scenario: Ordinary preparation preserves siblings

- **WHEN** a real build directory has sibling files or directories whose names
  begin with the build directory's name and a dot
- **THEN** preparing the build directory leaves every sibling unchanged

#### Scenario: Browser snapshot staging overlaps a build

- **WHEN** a browser snapshot stage beside the build directory remains in use
  after releasing the project build lock and another build prepares its
  directory
- **THEN** the stage and every artifact linked into it remain available to the
  capture process

#### Scenario: An exact node writes exact geometry beside its mesh

- **WHEN** an exact rigid node is built
- **THEN** a `.brep` artifact sits beside its `.stl` under the same basename

#### Scenario: A faceted node writes no exact artifact

- **WHEN** a rigid node that is not exact is built
- **THEN** no `.brep` artifact is written for it

#### Scenario: Published documents do not name exact geometry

- **WHEN** a build publishes its viewer snapshot for a project of exact nodes
- **THEN** the document references only `.stl` models and names no `.brep`

#### Scenario: Two declared models publish side by side

- **WHEN** a project declares models `wall_clock_01` and `wall_clock_02` and
  both are built
- **THEN** `_build/wall_clock_01/viewer.json` and
  `_build/wall_clock_02/viewer.json` both exist, each naming only artifacts
  under its own directory, and building the second removed nothing from the
  first

#### Scenario: Declared models do not share a lock

- **WHEN** a build of `wall_clock_01` is rendering
- **THEN** a build of `wall_clock_02` in the same project acquires its own
  lock and does not wait

#### Scenario: A sub-node build does not sweep the models

- **WHEN** a project declaring models builds a sub-node by qualifier, and its
  publication into the build root sweeps unreferenced artifacts
- **THEN** every artifact under the declared models' directories is still
  there

#### Scenario: A single-model project's directory is unchanged

- **WHEN** a project that declares no models is built
- **THEN** its artifacts, `viewer.json` and `errors.json` are written in the
  build root itself, at the paths they have today

#### Scenario: A marking's artifact sits beside the part's mesh

- **WHEN** a rigid node declaring the markings `digits` and `arrows` is built
- **THEN** two marking artifacts sit beside its `.stl` under the same basename,
  one distinguished by `digits` and one by `arrows`

#### Scenario: A part declaring no marking writes no marking artifact

- **WHEN** a rigid node that declares no marking is built
- **THEN** its build directory holds exactly the artifacts it held before
  markings existed

#### Scenario: A build writes SCAD only for SCAD-authored leaves

- **WHEN** a project holding an assembly, a faceted fusion, a flexible leaf,
  an exact leaf and a `Solid2Node` leaf is built with the OpenSCAD node
  package installed
- **THEN** the only `.scad` under its build directory is the `Solid2Node`
  leaf's, beside that leaf's `.stl` under the same basename, and no
  per-binding snapshot of the flexible leaf is written

#### Scenario: A build without the OpenSCAD engine writes no SCAD

- **WHEN** a project of exact and imported STL leaves is built with
  SolidPython and the OpenSCAD node package absent
- **THEN** its `.stl`, `.brep` and `viewer.json` are written as with them, no
  `.scad` exists under its build directory, and nothing is logged about SCAD

### Requirement: Asynchronous STL render protocol

A leaf that renders its STL in a subprocess SHALL signal it by raising
`StlRenderStart` from its `generate_stl()`, carrying the process, target file,
mtime, and lock file; the leaves of the OpenSCAD node family launch OpenSCAD
renders this way (`openscad <scad> -o <stl> --export-format binstl`). The core
SHALL launch no renderer of its own: the node base's `generate_stl()` starts no
process, and a rigid leaf whose STL is still not current after its
materialization is refused under the `node-model` capability. `build_stls()` SHALL loop, waiting on each started render
(`job.wait()`), until no renders remain. Waiting SHALL inspect the subprocess
exit status before finishing the render. A zero exit status SHALL finish the
render by stamping and atomically replacing the target STL and removing the
lock. A nonzero exit status SHALL remove the temporary output and lock, SHALL
leave any previously published target and its currency record unchanged, and
SHALL raise a build failure. Non-rigid nodes SHALL be skipped.

For the OpenSCAD node family this protocol is one of the paths that require
the OpenSCAD binary under the `openscad-dependency` capability. Before launching the subprocess for a node
the system SHALL confirm the binary is available and, when it is not, SHALL
fail naming that node and why its backend needs OpenSCAD, rather than letting
the subprocess launch fail. A build that reaches no such node SHALL make no
availability check.

A `FusionNode` whose subtree is exact SHALL NOT use this protocol. It composes
its own geometry under the `exact-geometry` capability and SHALL produce its
`.stl` by tessellating that composition in process, stamping the mtime as any
other artifact producer does, without launching a subprocess and without
raising `StlRenderStart`. A fusion with any non-exact descendant SHALL
produce its artifact through direct mesh composition under
`backend-neutral-materialization`, not this OpenSCAD subprocess protocol.
Its OpenSCAD-authored children still use this protocol where required.

Tessellation of an exact composition SHALL use the same deflection the
`CadQueryNode` adapter already uses for leaf STL export, so a fused solid's
mesh is of the same quality as the leaves around it.

#### Scenario: Full build

- **WHEN** `build_stls()` runs on a tree with several stale rigid nodes
- **THEN** each stale STL is rendered exactly once and the call returns with
  all locks removed and mtimes stamped

#### Scenario: A cold render fails

- **WHEN** OpenSCAD exits nonzero while rendering a node with no published STL
- **THEN** the build fails, the temporary STL and render lock are removed, and
  no target STL or viewer snapshot is published

#### Scenario: A replacement render fails

- **WHEN** OpenSCAD exits nonzero while rendering a replacement for a
  previously published STL
- **THEN** the build fails, the temporary STL and render lock are removed, and
  the previous target STL and viewer snapshot remain unchanged

#### Scenario: An exact fusion renders in process

- **WHEN** a `FusionNode` whose subtree is exact is built
- **THEN** its `.stl` is produced by tessellating its own composition, no
  OpenSCAD subprocess is launched for it, and `build_stls()` returns without
  waiting on a render job for that node

#### Scenario: A faceted fusion composes current child meshes

- **WHEN** a `FusionNode` holding a non-exact descendant is built
- **THEN** its child artifacts become current before the fusion unions them
  directly, and no OpenSCAD render job is launched for the fusion itself

#### Scenario: The renderer is missing for a node that needs it

- **WHEN** a stale OpenSCAD-backed leaf must be rendered and no `openscad` is on
  the PATH
- **THEN** the build fails naming that node and the reason its backend needs
  OpenSCAD, and no subprocess launch error surfaces in its place

#### Scenario: An all-exact build makes no availability check

- **WHEN** `build_stls()` completes for a tree whose every rigid node is exact
- **THEN** no OpenSCAD availability check is performed and the absence of the
  binary is never reported

#### Scenario: A leaf outside the family never starts OpenSCAD

- **WHEN** a rigid `LeafNode` subclass outside the OpenSCAD node family has no
  current STL after its materialization and `build_stls()` reaches it
- **THEN** it fails naming the node, its class and its STL path, and no
  `StlRenderStart` is raised and no subprocess is launched for it

### Requirement: A successful build sweeps unreferenced artifacts

After a successful publication of a changed document the system SHALL remove
files in the build directory that the current viewer snapshot does not
reference and that no node of the published tree keeps. A build that finds the
document it would publish already published SHALL remove only transient
artifacts (below). It SHALL NOT remove:

- the snapshot;
- the error file;
- an artifact a node of the published tree declares in `kept_artifacts()`
  (the `leaf-contract` capability), such as a family leaf's `.scad`;
- `.brep` exact geometry;
- live render lock files;
- temporaries belonging to a build in progress;
- the test framework's verdict store, the directory `.verdicts` at the top of
  the build directory, together with everything in it.

The sweep SHALL be confined to the build directory.

The verdict store is spared by location rather than by reference. It is test
state, not a build artifact, and no published document names it. It is
written by test runs that may be in progress while a build publishes.

`.brep` artifacts are spared by kind rather than by reference, because no
published document names them. A superseded one is therefore not removed by
the sweep; mtime-equality caching means a superseded artifact is never read.

A kept artifact is spared by **declaration of the tree being published**,
never by its suffix: the sweep SHALL keep every path a node of that tree
declares in `kept_artifacts()`, with its currency record, whether or not this
build rewrote it, and SHALL treat every other file as any unreferenced file: a
`.scad` an earlier build wrote for an assembly, a fusion, a flexible leaf or
another leaf, one an interrupted OpenSCAD snapshot left for a root, and one of a
family leaf no longer in the tree are removed by the next build that publishes a
changed document. No rule of the sweep SHALL name a `.scad` suffix.

A **transient** artifact is removed by **every** successful build, changed
document or not, together with its currency record: an artifact whose writer
published it for one process's own use and declared that in its record
(`machinome.currency`, `record(..., transient=True)`), such as the root
presentation the OpenSCAD viewer writes for one snapshot and removes itself.
A build that publishes an unchanged document removes nothing else. No rule of
the sweep SHALL name the kind of a transient artifact.

A **marking** artifact under the `markings` capability is spared by
**reference**, not by kind, because the published snapshot names it beside the
part's model. A marking still declared is therefore kept, and a marking
artifact whose declaration was deleted or renamed is removed by the next
successful publication, exactly as a renamed node's artifact is.

#### Scenario: A renamed node leaves nothing behind

- **WHEN** a node is renamed and the project is rebuilt successfully
- **THEN** the artifact under the old name is gone from the build directory and
  the artifact under the new name is present and referenced

#### Scenario: A failed build sweeps nothing

- **WHEN** a build fails
- **THEN** no artifact is removed from the build directory

#### Scenario: Exact geometry survives the sweep

- **WHEN** a build of exact nodes publishes successfully and sweeps
- **THEN** every `.brep` written for a current node is still present, though
  the published snapshot names none of them

#### Scenario: A SCAD-authored leaf's SCAD survives the sweep

- **WHEN** a project holding a `Solid2Node` leaf whose `.stl` is already
  current is rebuilt and publishes successfully
- **THEN** that leaf's `.scad` and its currency record are still present,
  though this build did not rewrite them

#### Scenario: Presentation SCAD left by an earlier build is removed

- **WHEN** a build directory holds the `.scad` files an earlier build wrote
  for the project's assemblies, fusions, flexible leaves, exact leaves and
  root, and the project is rebuilt and publishes a changed document
- **THEN** every one of them is gone with its currency record, and the only
  `.scad` files left are those the tree's family leaves declare in
  `kept_artifacts()`

#### Scenario: A renamed SCAD-authored leaf leaves no SCAD behind

- **WHEN** a `Solid2Node` leaf is renamed and the project is rebuilt
  successfully
- **THEN** the `.scad` under the old name is gone and the `.scad` under the
  new name is present

#### Scenario: A build removes any SCAD no current node writes

- **WHEN** an interrupted `machinome snapshot --renderer openscad` has left
  the root's `.scad`, published as transient, in the build directory, and the
  project is built publishing the document already published
- **THEN** that build removes the root's `.scad` and its currency record and
  nothing else: every artifact a node of the tree keeps is still present, and
  so is an `.stl` an earlier test run wrote for another parameter set

#### Scenario: The verdict store survives the sweep

- **WHEN** a project whose build directory holds a verdict store is rebuilt
  and publishes successfully
- **THEN** the `.verdicts` directory and every file in it are still present,
  and the next test run is served from them

#### Scenario: A declared marking survives the sweep

- **WHEN** a project whose parts declare markings publishes successfully and
  sweeps
- **THEN** every marking artifact the snapshot names is still present

#### Scenario: A dropped marking leaves nothing behind

- **WHEN** a marking declaration is deleted and the project is rebuilt
  successfully
- **THEN** that marking's artifact is gone from the build directory and the
  part's own artifacts are untouched

### Requirement: Stable-generation work is shared without redundant writes

Within one sealed source generation, the system SHALL maintain a request-local metadata census. One census SHALL observe each distinct tracked contributor once and SHALL serve overlapping node source-fingerprint and digest work only for that observation. A later currency or publication boundary SHALL take a fresh census before deciding that the generation is still stable. No census SHALL survive the builder process or a generation change.

A text artifact a rigid node publishes through the generation's published-state record — a family leaf's base `.scad`, under the `openscad-node` capability — SHALL be generated at most once for the currently published full source/currency identity at a canonical artifact path in a source generation, regardless of how many repeated instances reference that artifact. A different identity at the same path SHALL replace what is current; a later return to an earlier identity SHALL NOT be reused merely because that identity appeared historically. The record SHALL be named for what it records, a path's published state, and SHALL name no technology.

Every publication of a text artifact SHALL be immediate: the source phases SHALL hold no queue of deferred publications, and the assembly phase SHALL end with the same post-phase source check as every other phase. A source change detected at a phase boundary SHALL prevent viewer-document publication and end the generation source-changed.

Atomic text and currency publication (`machinome.currency.publish_text`) SHALL compare the desired state with the state on disk. When the text's bytes, timestamp, and currency record already match, the system SHALL replace none of them. When source metadata changes but node-scoped contents remain equal, the system SHALL perform the required restamp and currency-record refresh without rewriting identical bytes. Write suppression SHALL NOT bypass source-fingerprint comparison, content verification, lock ownership, generation checks, or atomic replacement of changed content.

#### Scenario: Repeated rigid parts generate one SCAD artifact

- **WHEN** many rigid instances share one artifact identity in a stable assembly
- **THEN** their one base SCAD artifact is generated at most once for that source/currency identity, while every instance retains its own tree name and placement in the published document

#### Scenario: Repeated non-rigid path publishes its final value once

- **WHEN** non-rigid, non-flexible assembly instances of one class are built under one stable source generation
- **THEN** every instance contributes its own in-memory composition, no `.scad` is written for any of them, and a second and third unchanged build replace no artifact and no currency record

#### Scenario: Historical identity is not current identity

- **WHEN** one rigid canonical path is produced under full source/currency identities A, then B, then A in one generation
- **THEN** all three desired states reach publication in order and the final A is not skipped because an earlier A was remembered

#### Scenario: Coalesced publication cannot certify a changed generation

- **WHEN** assembly fails, or a contributor changes before the assembly phase's post-phase check
- **THEN** no viewer document certifies stale work, and a detected source mismatch ends the generation source-changed

#### Scenario: Flexible and direct generation remain immediate

- **WHEN** flexible bindings publish several snapshot STLs, or a caller has the OpenSCAD node package write a node's SCAD, inside or outside an assembly phase
- **THEN** each publication is immediate, and no source phase defers or folds one

#### Scenario: A shared source is observed once per census

- **WHEN** hundreds of nodes' source closures contain the same project file
- **THEN** one generation census performs one filesystem metadata observation of that file and each node receives the same observation, while the next generation boundary observes it afresh

#### Scenario: Unchanged text is not replaced

- **WHEN** a complete build computes a family leaf's SCAD bytes, timestamp, and a currency record identical to those already on disk
- **THEN** the existing SCAD and currency files retain their inode, mtime, and ctime

#### Scenario: Metadata-only source change keeps currency correct

- **WHEN** a tracked source's metadata changes while its node-scoped content stays byte-identical
- **THEN** content verification refreshes the artifact stamp and currency record as required, without rewriting byte-identical SCAD content or reporting stale geometry current

### Requirement: Generated SCAD imports resolve from the file that holds them

Every import of a build artifact that the system writes into a generated
`.scad` SHALL name that artifact by a path which resolves, from the
directory holding that `.scad` file, to the artifact itself — because that
is how OpenSCAD resolves an `import()`. This SHALL hold for every leaf kind
that presents its geometry as an artifact (`Solid2Node`, the exact adapters,
`StlNode`, `JScadNode`, and a flexible leaf's per-binding snapshot), for a
node at any depth of the tree, whether or not the artifact was already
current when the tree was assembled, whatever package the importing node
is declared in relative to the node whose artifact it names, and whichever
path wrote the `.scad`: a family leaf's materialization, the OpenSCAD
snapshot renderer's root, or a caller's
`machinome.node.openscad.writer.generate_scad(node)`. The writer SHALL take the
imports from the node's own presentation (`presentation()`), whose artifact
imports the core re-anchors onto the node's own build directory. An assembly
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
  exact leaf and a flexible leaf all declared in `sim/`, the model is
  built, and the assembly's `.scad` is then generated
- **THEN** every `import(file = …)` in the assembly's generated `.scad`
  names a file that exists relative to that `.scad`'s own directory

#### Scenario: The second build spells it the same way

- **WHEN** that model is built again with every artifact already current and
  the assembly's `.scad` is generated again
- **THEN** each import in the assembly's generated `.scad` still resolves
  from that `.scad`'s directory, and the geometry the document presents is
  unchanged

#### Scenario: An intermediate assembly's own SCAD resolves from its own directory

- **WHEN** a root in `sim/tools/` places an assembly declared in
  `sim/sub/deep/` which places a leaf declared in `sim/`, the model is
  built, and the intermediate assembly's and the root's `.scad` are then
  generated
- **THEN** the import in the intermediate assembly's own generated `.scad`
  resolves from `sim/sub/deep`'s build directory, and the import in the
  root's generated `.scad` resolves from the root's build directory

#### Scenario: The snapshot renderer's root SCAD resolves

- **WHEN** `machinome snapshot --renderer openscad` writes the root's `.scad`
  of a model whose root is declared in another package than its parts
- **THEN** every `import(file = …)` in it names a file that exists relative
  to that `.scad`'s own directory

#### Scenario: A project's own import is reproduced verbatim

- **WHEN** a leaf's `render()` imports a file of the project's own by a
  relative path
- **THEN** the generated `.scad` holds that path exactly as written, with
  no anchoring applied to it

#### Scenario: A parent beside its parts is unchanged

- **WHEN** an assembly and the leaves it places are declared in one package,
  the model is built, and the assembly's `.scad` is then generated
- **THEN** each leaf artifact is imported by its bare basename, exactly as
  before this rule was stated
