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
external rendering. A node that has B-rep geometry under the `brep-geometry` capability
SHALL additionally write
`.brep`, holding that node's unplaced B-rep geometry under the same basename.
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

- **WHEN** a B-rep rigid node is built
- **THEN** a `.brep` artifact sits beside its `.stl` under the same basename

#### Scenario: A faceted node writes no exact artifact

- **WHEN** a rigid node that has no B-rep geometry is built
- **THEN** no `.brep` artifact is written for it

#### Scenario: Published documents do not name exact geometry

- **WHEN** a build publishes its viewer snapshot for a project of B-rep nodes
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

- **WHEN** a project holding an assembly, a mesh fusion, a flexible leaf,
  a B-rep leaf and a `Solid2Node` leaf is built with the OpenSCAD node
  package installed
- **THEN** the only `.scad` under its build directory is the `Solid2Node`
  leaf's, beside that leaf's `.stl` under the same basename, and no
  per-binding snapshot of the flexible leaf is written

#### Scenario: A build without the OpenSCAD engine writes no SCAD

- **WHEN** a project of B-rep and imported STL leaves is built with
  SolidPython and the OpenSCAD node package absent
- **THEN** its `.stl`, `.brep` and `viewer.json` are written as with them, no
  `.scad` exists under its build directory, and nothing is logged about SCAD

### Requirement: External wrappers own independent current artifacts

Different source-bound wrapper classes distinguished by their defining Python
source and qualname SHALL own independent cached artifacts even when they
refer to the same external asset with identical parameters. A build containing
those wrappers SHALL terminate with each wrapper's geometry and currency
record current simultaneously, rather than repeatedly overwriting and
invalidating another wrapper's artifact. Artifact layout and existing source
and producer-recipe currency checks SHALL otherwise remain unchanged.

#### Scenario: Different STL adjustments remain independently cached

- **WHEN** two same-qualname wrappers defined in different Python files import
  one STL, apply different geometry adjustments and have different tracked
  source mtimes and digests, and a model containing both is built
- **THEN** the build terminates, each cached STL contains its own adjusted
  geometry, and both artifacts and currency records are current together
- **AND** rebuilding the unchanged model does not regenerate either STL

#### Scenario: STEP wrappers retain both exact and faceted artifacts

- **WHEN** two same-qualname wrappers defined in different Python files select
  one STEP source and apply different adjustments, and both are built
- **THEN** each wrapper has its own correct STL and BREP artifacts, each pair
  is current together, and rebuilding does not regenerate either pair

#### Scenario: Source edits still invalidate through ordinary currency

- **WHEN** one wrapper's geometry-affecting Python source or tracked helper is
  edited after both wrappers' artifacts are current
- **THEN** its existing key is unchanged and its affected artifacts rebuild
  according to existing source currency, without accepting the old geometry
- **AND** the other wrapper is invalidated only if its tracked sources or
  recipe changed under those same existing rules

### Requirement: Mtime-equality caching

Subject to the producer recipe identity requirement below, the system SHALL
treat an artifact as up to date on its metadata-only path iff it exists,
its mtime equals the node's `mtime`, and its recorded source-set
fingerprint equals the current fingerprint of every file tracked for the node
(`node.files`, aggregated recursively from children). `node.mtime` remains the
maximum source-file mtime across that set. After generating an artifact the
system SHALL back-date its mtime to the source mtime via `os.utime`. A change
observable in any contributing source's recorded metadata SHALL invalidate the
metadata-only path and all ancestor artifacts even when the maximum source
mtime is unchanged.

The source-set fingerprint SHALL cover a deterministic, sorted sequence of
project-relative real path, filesystem identity, byte size, integer-nanosecond
mtime, and integer-nanosecond change time for every tracked source. It SHALL
detect ordinary replacement, same-size rewrites, and content rewrites whose
mtime is restored. A filesystem or privileged external operation that changes
bytes while exposing the same path identity, size, mtime, and change time is
outside the guarantees of the metadata-only path; callers operating under that
condition MUST explicitly invalidate the artifact or its currency record.

The artifact mtime comparison SHALL be exact equality of integer nanoseconds,
and the system SHALL read source and artifact timestamps, and stamp artifacts,
in integer nanoseconds. It SHALL NOT decide currency from a floating-point
timestamp, and SHALL NOT accept an artifact whose stamp merely approximates
the node mtime. No tolerance window exists.

The back-date SHALL be a fixed point wherever the filesystem holding the
artifacts stores timestamps at the same resolution as the filesystem holding
the sources. A project whose source files carry sub-second mtimes SHALL cache
its artifacts normally on a coarse-resolution filesystem, including one that
stores timestamps to the millisecond.

Where the system cannot store the exact stamp, the artifact SHALL fail the
metadata-only path and enter content verification. Currency SHALL fail only in
the safe direction for every observable source change.

When the producer recipe is compatible but artifact mtime equality or
source-set fingerprint equality fails, the system SHALL consult a
content-verified fallback before rebuilding. A mismatched producer recipe
SHALL NOT enter that fallback. The fallback SHALL compare a digest of the
node's tracked sources, as they are on disk now,
against the digest recorded for that artifact when it was produced. When they
agree, the system SHALL restamp the artifact to the current `node.mtime`,
record the current source-set fingerprint with the digest, and treat it as
current. When they disagree, when no digest was recorded, or when any tracked
source cannot be read, the artifact SHALL be rebuilt.

The digest SHALL be scoped to the node, not to the file. A tracked source file
that defines more than one node class contributes only the text that node can
depend on: the file with the class bodies of the other top-level node classes
removed. Imports, module-level statements, constants, functions, and non-node
classes SHALL remain in every node's digest. A node class whose name the
retained text refers to, as an identifier or string literal, SHALL remain. An
internal node's digest SHALL cover the union of its children's scopes.

Only a node class defined as a top-level statement SHALL be removable. Where
the system cannot determine which classes are node classes, or cannot parse
the file, it SHALL digest the whole file. A single-node file, a file defining
no node, and a non-Python source SHALL digest byte for byte as without scoping.
The scope is not recorded beside the artifact; a changed scope rebuilds once.
The system SHALL NOT require or recommend one node per file for currency.

The metadata-only path SHALL stat tracked sources and read the artifact's
currency record, but SHALL NOT read source contents or parse them. Content
verification SHALL read only the node's tracked source files, never its
artifacts. Recording the digest and fingerprint SHALL happen wherever the
artifact is stamped, so an artifact and the record that vouches for it are
written together or not at all.

The fallback SHALL preserve the direction-of-failure guarantee: it SHALL NOT
report current an artifact whose scoped source contents differ, and SHALL NOT
weaken any case in which a genuine observable content change already rebuilds.
Where a restamp cannot achieve equality because the artifact filesystem is
coarser, the artifact SHALL still be current for that build on the strength of
the matching digest, and the fallback SHALL be consulted again next time
rather than looping.

The currency record SHALL live inside the build directory, SHALL NOT be
referenced by the published viewer document, and SHALL NOT change publication
semantics. A successful sweep SHALL keep the record belonging to an artifact
it keeps and SHALL NOT leave one behind for an artifact it removes. For a
producer whose recipe is unchanged, the reader
SHALL accept a legacy digest-only record as having no fingerprint, validate it
through the content fallback even when artifact mtime equality succeeds, and
upgrade a matching record without re-deriving geometry. An unknown or malformed
record SHALL NOT certify an artifact.

For a B-rep node the `.brep` artifact SHALL participate exactly as the `.stl`
does: the node's artifacts are current only when both are. A build directory
produced before the node became a B-rep therefore rebuilds once.

Mtime and source fingerprint decide source currency, never binding currency. A
flexible leaf's snapshot artifact is addressed by a name containing a hash of
its bound parameter values; within one binding it participates in this rule as
any adapter-owned artifact does.

A node's tracked files SHALL include its own source together with project-local
modules it imports transitively. Modules outside the project tree SHALL NOT be
tracked. Where the contributing set cannot be determined exactly, the system
SHALL track more files rather than fewer.

#### Scenario: Source edit invalidates ancestors

- **WHEN** a leaf's source file is modified
- **THEN** the leaf's STL and every ancestor STL report not-up-to-date and are
  regenerated on the next build

#### Scenario: Imported project module edit invalidates dependants

- **WHEN** a node imports a project helper, that helper changes, and another
  tracked source retains the unchanged maximum mtime
- **THEN** the node's source-set fingerprint differs and its artifact is
  regenerated with the helper's new values

#### Scenario: Restored mtime does not hide a same-size edit

- **WHEN** a tracked source is rewritten with different same-size bytes and its
  mtime is restored to its previous value
- **THEN** its filesystem change metadata makes the fingerprint differ, content
  verification rejects the old digest, and the artifact is regenerated

#### Scenario: A timestamp moves but no content changes

- **WHEN** the producer recipe is unchanged and every source file's mtime is
  rewritten with no byte changed, as a
  clone, branch switch, stash pop, or copy can do
- **THEN** the digest match prevents geometry from being re-derived, every
  artifact is restamped and records the current fingerprint, and the published
  document differs only in its recorded source mtimes

#### Scenario: A rewritten source with different content still rebuilds

- **WHEN** a source file is rewritten with different content
- **THEN** its fingerprint leaves the metadata-only path, its digest disagrees,
  and the artifact is re-derived

#### Scenario: The fast path is not slowed

- **WHEN** the producer recipe is compatible and an artifact's mtime and
  recorded source-set fingerprint match the node's current source state
- **THEN** currency is decided without reading source bytes for a digest or
  parsing Python source

#### Scenario: A legacy digest-only record upgrades safely

- **WHEN** the producer recipe is unchanged and an artifact's mtime equals the
  node mtime but its sidecar contains a valid legacy digest with no source-set
  fingerprint
- **THEN** the digest is verified and, if it matches, the artifact is not
  re-derived and the sidecar is upgraded with the current fingerprint

#### Scenario: An artifact with no recorded digest

- **WHEN** an artifact has no recorded digest or has a malformed or unknown
  currency record
- **THEN** it is rebuilt and gains a valid current record

#### Scenario: A library change does not invalidate

- **WHEN** a node imports a module from outside the project tree
- **THEN** that module is not part of the node's tracked files or fingerprint

#### Scenario: Two node classes in one file rebuild independently

- **WHEN** a file defines two leaf node classes, both artifacts are current,
  and the body of one class is edited
- **THEN** the edited node's artifacts are re-derived and the other node's
  artifacts use their scoped digest to refresh the fingerprint without being
  re-derived

#### Scenario: Shared code in a shared file invalidates every node in it

- **WHEN** shared module-level code in a file defining two nodes is edited
- **THEN** both nodes' artifacts are re-derived

#### Scenario: A node that refers to a sibling follows it

- **WHEN** one node reaches a sibling as a base, through a helper, or by a
  string name, and the sibling's body is edited
- **THEN** the referring node's artifacts are re-derived as well

#### Scenario: A fusion sharing its children's file follows them

- **WHEN** a file defines a fusion and its leaves and one leaf's body is edited
- **THEN** the fusion and edited leaf are re-derived, while the other leaf uses
  its scoped digest without re-derivation

#### Scenario: A single-class file digests as it always has

- **WHEN** a digest is computed for a node whose tracked files each define one
  node class or none
- **THEN** every digest entry is the sha256 of that file's bytes

#### Scenario: A multi-node file rebuilds once after upgrading

- **WHEN** whole-file legacy digests are checked after touching a file that
  defines several node classes
- **THEN** nodes whose scoped digest differs rebuild once and then report
  current

#### Scenario: Unchanged sources skip rendering

- **WHEN** `generate_stl` runs, the producer recipe is compatible, and both
  the STL mtime and source-set fingerprint match
- **THEN** no OpenSCAD process is launched

#### Scenario: Missing exact geometry is not current

- **WHEN** a B-rep node's `.stl` and `.scad` are current but its `.brep` is
  absent
- **THEN** the node is rendered and produces both B-rep artifacts

#### Scenario: Sub-second source mtimes cache on a coarse-resolution filesystem

- **WHEN** a project with arbitrary sub-second source mtimes is built twice on
  a filesystem storing timestamps to the millisecond
- **THEN** the second build reports every artifact current and renders nothing

#### Scenario: Exact artifacts cache on a coarse-resolution filesystem

- **WHEN** a B-rep rigid node is built twice without edits on a filesystem
  storing timestamps to the millisecond
- **THEN** its `.stl` and `.brep` report current and neither is rewritten

#### Scenario: A coarse filesystem never makes a changed source look current

- **WHEN** a source is modified on a filesystem storing millisecond timestamps
- **THEN** the changed contributor's fingerprint or digest invalidates and
  regenerates the node, regardless of sub-millisecond timestamp remainders

#### Scenario: Artifacts stamped by an earlier version rebuild once

- **WHEN** artifacts stamped through the previous floating-point back-date are
  built by the current version
- **THEN** they are validated or regenerated once and then report current

#### Scenario: A source edit invalidates a flexible snapshot

- **WHEN** a flexible leaf's source changes after its snapshot was written and
  the node is re-assembled at the same binding
- **THEN** the snapshot reports not-up-to-date and is re-evaluated

#### Scenario: A binding change selects a different snapshot

- **WHEN** a flexible leaf is re-assembled at a different binding with
  unmodified sources
- **THEN** a differently named snapshot is produced and prior currency remains
  untouched until sweep

### Requirement: Project build mutual exclusion

The system SHALL serialise builds of the same project across processes with an
advisory exclusive lock (`fcntl.flock`) on a lock file held beside the project's
published build directory. Every framework entry point that renders artifacts
for a project — the development watch loop, the one-shot build, the test
runner's build phase, and export — SHALL acquire that lock before any lifecycle
phase that can materialize SCAD, BREP, STL, or published documents, including
assembly, and SHALL release it as soon as that work is finished. Acquisition
SHALL block until the lock is available rather than fail or skip, and a wait
that does not resolve immediately SHALL be logged. The lock SHALL NOT be held
while a builder waits for a source change, invokes a completion callback, or
runs project test cases, and the lock file SHALL be excluded from version
control by the same rule that excludes published artifacts.

A holder that dies SHALL release the lock without any recovery step, because
the kernel releases it when the holding process ends.

#### Scenario: A second builder waits for the first

- **WHEN** a build is rendering a project and another process starts a build of
  the same project
- **THEN** the second process does not render or publish until the first has
  finished, and both report their own build outcome

#### Scenario: An assembly-time producer waits

- **WHEN** a cold B-rep or imported-file node starts through a framework entry
  point while another process holds its project build lock
- **THEN** no SCAD, BREP, or STL artifact is materialized until the lock is
  released, after which the entry point completes normally

#### Scenario: Test setup is locked and test execution is not

- **WHEN** the test runner builds a node and then executes its project test
  cases
- **THEN** keyframing, preliminary render, assembly, and STL generation occur
  while the project lock is held, and test-case execution begins after release

#### Scenario: Watching does not hold the lock

- **WHEN** a development watch loop has published a build and is waiting for the
  next source change
- **THEN** another process can acquire the project build lock immediately

#### Scenario: A killed builder leaves nothing to reap

- **WHEN** a process holding the build lock is killed
- **THEN** the next builder acquires the lock with no stale-lock detection and
  no manual cleanup

#### Scenario: Independent projects do not serialise

- **WHEN** two projects with different build directories are built at the same
  time
- **THEN** neither build waits for the other

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

A `FusionNode` whose subtree has B-rep geometry SHALL NOT use this protocol. It composes
its own geometry under the `brep-geometry` capability and SHALL produce its
`.stl` by tessellating that composition in process, stamping the mtime as any
other artifact producer does, without launching a subprocess and without
raising `StlRenderStart`. A fusion with any mesh descendant SHALL
produce its artifact through direct mesh composition under
`backend-neutral-materialization`, not this OpenSCAD subprocess protocol.
Its OpenSCAD-authored children still use this protocol where required.

Tessellation of a B-rep composition SHALL use the same deflection the
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

- **WHEN** a `FusionNode` whose subtree has B-rep geometry is built
- **THEN** its `.stl` is produced by tessellating its own composition, no
  OpenSCAD subprocess is launched for it, and `build_stls()` returns without
  waiting on a render job for that node

#### Scenario: A faceted fusion composes current child meshes

- **WHEN** a `FusionNode` holding a mesh descendant is built
- **THEN** its child artifacts become current before the fusion unions them
  directly, and no OpenSCAD render job is launched for the fusion itself

#### Scenario: The renderer is missing for a node that needs it

- **WHEN** a stale OpenSCAD-backed leaf must be rendered and no `openscad` is on
  the PATH
- **THEN** the build fails naming that node and the reason its backend needs
  OpenSCAD, and no subprocess launch error surfaces in its place

#### Scenario: An all-exact build makes no availability check

- **WHEN** `build_stls()` completes for a tree whose every rigid node has B-rep geometry
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
- `.brep` B-rep geometry;
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

- **WHEN** a build of B-rep nodes publishes successfully and sweeps
- **THEN** every `.brep` written for a current node is still present, though
  the published snapshot names none of them

#### Scenario: A SCAD-authored leaf's SCAD survives the sweep

- **WHEN** a project holding a `Solid2Node` leaf whose `.stl` is already
  current is rebuilt and publishes successfully
- **THEN** that leaf's `.scad` and its currency record are still present,
  though this build did not rewrite them

#### Scenario: Presentation SCAD left by an earlier build is removed

- **WHEN** a build directory holds the `.scad` files an earlier build wrote
  for the project's assemblies, fusions, flexible leaves, B-rep leaves and
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

### Requirement: One fresh builder owns one stable source generation

The build supervisor SHALL start a builder in a fresh interpreter and SHALL allow that builder to perform every artifact pass needed to complete one stable source generation. A source generation SHALL be identified by the complete observable metadata identity of the loader entry/facade, imported project-module closure, and recursively discovered node source set, not by the maximum source mtime alone.

The loader SHALL bracket source execution: it SHALL observe the entry/facade and every project-local module before Python reads or executes it and SHALL require an uncached post-load observation to match after instantiation. A module discovered during import SHALL join through that same pre/post handshake. Project-local module execution SHALL NOT accept timestamp-and-size bytecode freshness as sufficient: it SHALL compile coherently observed source bytes or validate bytecode against a source content identity that rejects a same-size edit with restored mtime. External-library bytecode behavior is unchanged. A changed identity SHALL abandon the loaded classes and retry in a fresh interpreter; a first observation taken only after load SHALL NOT certify them.

Artifact-producing phases SHALL likewise compare an uncached observation before and after work for the contributors known to that producer. The agreed recursively assembled source set, including foreign geometry sources, SHALL then be sealed as the generation. One generation SHALL own one loaded root instance and one full assembly; retained artifact continuation SHALL resume the same memoized tree without re-import, reinstantiation, structural re-render, reassembly, or fusion reordering. The builder SHALL compare one fresh distinct-path census with that generation before every retained artifact pass, immediately before and after an asynchronous renderer wait, and immediately before publication. All node checks within one phase SHALL share its census instead of restatting the same closure per node. A changed, replaced, missing, newly selected, or newly imported contributor SHALL stop geometry work with the source-changed outcome before stale work is published. The next attempt SHALL begin in another fresh interpreter.

The project build lock SHALL continue to cover every artifact-producing phase and publication, while watches, callbacks, and project tests remain outside it. Every subprocess the supervisor does start SHALL retain the fresh-native-state and plain reconstructable-input guarantees of the build-isolation contract. A one-shot failure and an initial development failure SHALL end with their existing failed outcomes. A watch-reload failure SHALL record its error, release the build lock, perform no further geometry, wait under the existing recovery watcher, and exit source-changed after an edit so the next load is fresh; it SHALL NOT cause an immediate failed-child respawn loop.

#### Scenario: A multi-artifact generation pays one builder startup

- **WHEN** a stable cold model requires twenty-four sequential artifact render passes before its document is current
- **THEN** one spawned builder process performs those passes and reaches the complete current outcome without twenty-four fresh imports, and every published artifact equals the ordinary per-pass result

#### Scenario: A same-maximum edit ends the retained worker

- **WHEN** a contributing source is replaced during a retained builder's artifact passes while another contributor preserves the same maximum mtime
- **THEN** the per-contributor generation observation disagrees, the retained process publishes no document for its stale classes, reports source-changed, and a fresh process loads the edit

#### Scenario: Replacement during import cannot bless stale classes

- **WHEN** a project-local module is atomically replaced after Python read its old bytes but before loading and instantiation finish
- **THEN** the loader's pre/post identity handshake disagrees and the child retries fresh rather than sealing the replacement's disk identity around the old live classes

#### Scenario: Restored-mtime source cannot enter through stale bytecode

- **WHEN** a project module has a valid timestamp-and-size `.pyc` and its source is changed to different same-size bytes with restored mtime
- **THEN** the builder executes the current source or rejects the load generation, and never publishes geometry produced by the stale bytecode

#### Scenario: Artifact continuation keeps one assembled tree

- **WHEN** one stable generation needs several artifact passes
- **THEN** its root constructor, structural render, full assembly, and B-rep-fusion order occur once, and later passes continue pending artifacts on that same linked tree

#### Scenario: One-shot failure recovery gets a new interpreter

- **WHEN** a one-shot retained builder renders one artifact and a later artifact or document step fails
- **THEN** the failure is reported through the existing error outcome, the process exits, and a subsequent repair is loaded by a new spawned interpreter

#### Scenario: A watch reload failure waits instead of spinning

- **WHEN** a retained development worker fails during a reload after the initial build succeeded
- **THEN** it writes the error, releases the lock, waits without geometry for a relevant edit, exits source-changed on that edit, and causes neither an immediate respawn loop nor repeated viewer restart

#### Scenario: Lock contention does not widen

- **WHEN** a second process attempts to build while the retained worker is producing a stable generation
- **THEN** it waits on the same project lock until artifact work and publication finish, while a callback or source-change wait holds no lock

### Requirement: Producer recipe identity qualifies artifact currency

The system SHALL distinguish artifacts made by different geometry or
presentation recipes even when their project sources and parameter identity
are unchanged. A producer recipe change SHALL invalidate the affected
artifact before metadata or content-restamp reuse can certify it. A missing
legacy recipe record SHALL be incompatible for a producer changed by this
cycle, while unchanged producer recipes SHALL retain legacy source-record
compatibility.

A mesh fusion SHALL incorporate the current direct-mesh recipe and the
relevant recipes of its child geometry into its currency. Nested fusions
SHALL NOT reuse an enclosing artifact produced using superseded child
geometry recipes. Recipe identity SHALL NOT change node names, parameter
identity or artifact paths. Printed-piece identity SHALL continue to derive
from the actual produced STL bytes.

Recipe records SHALL remain private build metadata, published atomically
with the existing source-currency discipline. This qualification SHALL NOT
relax source checks, generation checks, artifact observations or publication
ordering, and SHALL NOT turn every framework edit into an all-project rebuild.

#### Scenario: An old fusion cache does not mask the new producer

- **WHEN** a project's sources are unchanged but its fusion STL was produced
  through the old OpenSCAD fusion recipe
- **THEN** the first new build recomputes that fusion by direct mesh union and
  records its new recipe, and the next unchanged build reuses it

#### Scenario: A nested fusion follows its child's recipe

- **WHEN** an enclosing fusion has a source-current artifact but a nested
  fusion's production recipe has changed
- **THEN** both affected fusion artifacts are rebuilt in dependency order

#### Scenario: Unchanged exact geometry stays cached

- **WHEN** B-rep leaf and B-rep fusion artifacts have unchanged source state
  and unchanged production recipes
- **THEN** upgrading this cycle does not re-derive their geometry merely
  because the framework version changed

#### Scenario: Content equality cannot bless the wrong recipe

- **WHEN** an artifact's project-source digest matches but its recorded
  producer recipe does not
- **THEN** the artifact is rebuilt rather than restamped as current

### Requirement: Generated SCAD imports resolve from the file that holds them

Every import of a build artifact that the system writes into a generated
`.scad` SHALL name that artifact by a path which resolves, from the
directory holding that `.scad` file, to the artifact itself — because that
is how OpenSCAD resolves an `import()`. This SHALL hold for every leaf kind
that presents its geometry as an artifact (`Solid2Node`, the B-rep adapters,
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

- **WHEN** an assembly declared in `sim/tools/` places a rigid leaf, a
  B-rep leaf and a flexible leaf all declared in `sim/`, the model is
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
