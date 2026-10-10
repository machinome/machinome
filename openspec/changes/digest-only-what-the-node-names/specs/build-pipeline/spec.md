## MODIFIED Requirements

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

The digest SHALL be scoped to the node, not to the file. Each tracked Python
source SHALL contribute its *retained text* for that node: the file with the
top-level definitions the node never names left out. A top-level definition is
a class statement, a function statement, an assignment or annotated assignment
whose targets are plain names, or an import statement other than a star
import. What a node retains SHALL start from its own class statement in its
own source, and an internal node's from its own and its children's, together
with every statement this requirement always retains, and SHALL grow by every
definition that retained text names until nothing more is named. Anywhere in
a retained statement:

- a bare name SHALL name every top-level definition of that name in the
  statement's own module; where an import anywhere in that module's text,
  at any depth (inside a function, a method, a conditional or a `try`
  block), binds it from a tracked module, it SHALL also name that module's
  definitions of it, followed through package re-exports; and it SHALL name
  the definitions of that name in every tracked module its own module
  star-imports;
- an attribute read rooted at a name that an import anywhere in the module's
  text binds to a tracked module SHALL name that module's definitions of the
  attribute, and where that name is also bound in the module otherwise (a
  parameter, an assignment or loop target, another import), the attribute
  name SHALL also name every top-level definition of exactly that name in
  every tracked source;
- any other attribute name, any string literal, and any name bound by an import
  the system cannot follow SHALL name every top-level definition of exactly
  that name in every tracked source;
- an import statement retained as part of a source retained whole, or
  always retained (a star import, or an import inside a statement that is not
  a definition), SHALL name the definitions every name it binds resolves to;
  an import statement retained because one of its names was named SHALL NOT
  make its other names count.

The system SHALL always retain, and count what they name: every top-level
statement that is not a definition, including expressions, conditionals,
loops, `with` and `try` blocks, assertions and assignments to attributes or
subscripts; a star import; a decorated definition other than a decorated node
class; a definition of a name that begins and ends with two underscores; a
statement that shares a line with another statement; and comments and blank
lines outside every statement. A tracked source whose retained text calls
`globals`, `locals`, `vars`, `dir`, `eval`, `exec`, `__import__`,
`import_module` or `getmembers`, or reads a `__dict__` attribute, SHALL be
retained whole together with every tracked source in its own import closure.
A retained call to `getattr`, `hasattr`, `setattr` or `delattr` whose first
argument is a name an import binds to a tracked module and whose second
argument is not a string literal SHALL retain that module whole, together with
every tracked module it star-imports.
A node's own source in which the node's class is not a top-level class
statement under its own name SHALL be retained whole. A Python file a node
tracks beyond its own source's import closure, as an imported-mesh leaf tracks
its wrapper module, SHALL be retained whole in that node's digest and in every
ancestor's; every tracked file of a node whose own source is not Python SHALL
be retained whole. A source retained whole has every statement retained, and
what each names counts.

Where the system cannot parse a file or cannot determine which of its classes
are node classes, it SHALL retain the file whole. A source that leaves nothing
out, and a non-Python source, SHALL digest byte for byte as without scoping.
The retained text is not recorded beside the artifact; a node whose retained
text changes rebuilds. The system SHALL NOT require or recommend one node per
file, or any arrangement of definitions in files, for currency. A definition
reached only through a name the source never spells, such as a name computed
at run time or a registry filled as a side effect of a definition and read
under another key, or a module reached through `sys.modules`, a variable, a
parameter or a call and read with a computed name, is outside what the digest
can see.

The metadata-only path SHALL stat tracked sources and read the artifact's
currency record, but SHALL NOT read source contents or parse them. Content
verification SHALL read only the node's tracked source files, never its
artifacts. Recording the digest and fingerprint SHALL happen wherever the
artifact is stamped, so an artifact and the record that vouches for it are
written together or not at all.

The fallback SHALL preserve the direction-of-failure guarantee: it SHALL NOT
report current an artifact whose retained source text differs, and every change
to text a node retains SHALL rebuild that node.
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

A currency record SHALL say whether its digest was taken under the retained-text
rule above. A record that does not, written by an earlier release or in the
legacy digest-only form, SHALL be verified, when the content fallback consults
it, against the digest the earlier rule gives for the sources now present: each
source holding one of the node's classes with only the other top-level node
classes that source's own retained statements never name, by identifier or
string literal, left out, and every other tracked file whole. When that digest
matches and the earlier rule left out nothing the current rule retains, the
artifact SHALL be restamped and re-recorded under the current rule without
re-deriving geometry; otherwise it SHALL be rebuilt. Such a record whose stamp
and fingerprint match SHALL keep the metadata-only path.

For a B-rep node the `.brep` artifact SHALL participate exactly as the `.stl`
does: the node's artifacts are current only when both are. A build directory
produced before the node became a B-rep therefore rebuilds once.

Mtime and source fingerprint decide source currency, never binding currency. A
flexible leaf's snapshot artifact is addressed by a name containing a hash of
its bound parameter values; within one binding it participates in this rule as
any adapter-owned artifact does.

A node's tracked files SHALL include its own source together with project-local
modules it imports transitively. A package's `__init__.py` SHALL be tracked,
and followed to what it imports, when a tracked module names that package in
an import and the package's directory does not contain that module: it is code
the module runs, as a library package beside the importer is. The
`__init__.py` of a package that contains the importing module SHALL NOT be
followed: Python runs it to resolve any import inside the package, and it is
conventionally the root assembly's own source, or a sub-assembly's, which
imports every node beneath it, so following it would make every node depend on
every other. Modules outside the project tree SHALL NOT be tracked. Where the
contributing set cannot be determined exactly, the system SHALL track more
files rather than fewer.

#### Scenario: Source edit invalidates ancestors

- **WHEN** a leaf's source file is modified in text the leaf retains
- **THEN** the leaf's STL and every ancestor STL report not-up-to-date and are
  regenerated on the next build

#### Scenario: Imported project module edit invalidates dependants

- **WHEN** a node reads a definition from an imported project helper, that
  definition changes, and another tracked source retains the unchanged maximum
  mtime
- **THEN** the node's source-set fingerprint differs and its artifact is
  regenerated with the helper's new values

#### Scenario: A module behind a sibling package's `__init__` is tracked

- **WHEN** a node's module imports a name from a project package whose
  directory does not contain the module, and that package's `__init__.py`
  re-exports the name from a module of the package
- **THEN** the `__init__.py` and the module that defines the name are in the
  node's tracked files, and after the node's artifacts are built an edit to
  the definition of that name makes them not-up-to-date

#### Scenario: A package containing the importer is not followed

- **WHEN** a node's module reaches a sibling module through its own package
  (`from . import dimensions`), and that package's `__init__.py` imports
  every node of the project
- **THEN** the sibling module is in the node's tracked files and the
  package's `__init__.py`, and the other nodes it imports, are not

#### Scenario: Restored mtime does not hide a same-size edit

- **WHEN** a tracked source is rewritten with different same-size bytes in text
  the node retains and its mtime is restored to its previous value
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

- **WHEN** a source file is rewritten with different content in text the node
  retains
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
- **THEN** the digest is verified under the earlier rule and, if it matches,
  the artifact is not re-derived and the sidecar is rewritten under the current
  rule with the current fingerprint

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

#### Scenario: Shared code invalidates the nodes that name it

- **WHEN** a file defines two nodes, and a module-level definition in it that
  both nodes name, and then one that only the first names, is edited
- **THEN** the first edit re-derives both nodes' artifacts, and the second
  re-derives the first node's while the second node's are restamped

#### Scenario: A node that refers to a sibling follows it

- **WHEN** one node reaches a sibling as a base, through a helper in its own
  file or in another tracked file, or by a string name, and the sibling's body
  is edited
- **THEN** the referring node's artifacts are re-derived as well

#### Scenario: A fusion sharing its children's file follows them

- **WHEN** a file defines a fusion and its leaves and one leaf's body is edited
- **THEN** the fusion and edited leaf are re-derived, while the other leaf uses
  its scoped digest without re-derivation

#### Scenario: A closure that leaves nothing out digests as it always has

- **WHEN** a digest is computed for a node whose tracked files leave nothing
  out, as a single-class file whose every definition the node names does
- **THEN** every digest entry is the sha256 of that file's bytes, and the
  digest equals the one the previous rule gives

#### Scenario: A multi-node file rebuilds once after upgrading

- **WHEN** whole-file legacy digests are checked after touching a file that
  defines several node classes
- **THEN** nodes whose scoped digest differs rebuild once and then report
  current

#### Scenario: Unchanged sources skip rendering

- **WHEN** `generate_stl` runs, the producer recipe is compatible, and both
  the STL mtime and source-set fingerprint match
- **THEN** no OpenSCAD process is launched

#### Scenario: Missing B-rep geometry is not current

- **WHEN** a B-rep node's `.stl` and `.scad` are current but its `.brep` is
  absent
- **THEN** the node is rendered and produces both B-rep artifacts

#### Scenario: Sub-second source mtimes cache on a coarse-resolution filesystem

- **WHEN** a project with arbitrary sub-second source mtimes is built twice on
  a filesystem storing timestamps to the millisecond
- **THEN** the second build reports every artifact current and renders nothing

#### Scenario: B-rep artifacts cache on a coarse-resolution filesystem

- **WHEN** a B-rep rigid node is built twice without edits on a filesystem
  storing timestamps to the millisecond
- **THEN** its `.stl` and `.brep` report current and neither is rewritten

#### Scenario: A coarse filesystem never makes a changed source look current

- **WHEN** a source is modified in text the node retains, on a filesystem
  storing millisecond timestamps
- **THEN** the changed contributor's fingerprint or digest invalidates and
  regenerates the node, regardless of sub-millisecond timestamp remainders

#### Scenario: Artifacts stamped by an earlier version rebuild once

- **WHEN** artifacts stamped through the previous floating-point back-date are
  built by the current version
- **THEN** they are validated or regenerated once and then report current

#### Scenario: A source edit invalidates a flexible snapshot

- **WHEN** text a flexible leaf retains changes after its snapshot was written
  and the node is re-assembled at the same binding
- **THEN** the snapshot reports not-up-to-date and is re-evaluated

#### Scenario: A binding change selects a different snapshot

- **WHEN** a flexible leaf is re-assembled at a different binding with
  unmodified sources
- **THEN** a differently named snapshot is produced and prior currency remains
  untouched until sweep

#### Scenario: An imported definition the node never names leaves it current

- **WHEN** a node reads one constant of an imported project module, its
  artifacts are current, and another constant of that module, which nothing
  the node retains names, is edited
- **THEN** the node's fingerprint differs, its digest matches, and its
  artifacts are restamped and re-recorded without being re-derived

#### Scenario: A definition named through a module attribute rebuilds its node

- **WHEN** a node reads `spec.X` from an imported module `spec` and `X` is
  edited
- **THEN** the node's artifacts are re-derived, and a node in the same file
  that reads only `spec.Y` is restamped

#### Scenario: A definition reached through an import, a re-export or a star import rebuilds its node

- **WHEN** a node reads a name bound by `from module import name`, by an import
  from a package whose `__init__.py` re-exports it from the defining module, or
  by a star import, and that name's definition is edited
- **THEN** the node's artifacts are re-derived

#### Scenario: A definition named by a string is retained

- **WHEN** a node reads a definition only through a string, as
  `getattr(module, 'NAME')` does, and the definition is edited
- **THEN** the node's artifacts are re-derived

#### Scenario: A statement that is not a definition is never left out

- **WHEN** a tracked module holds a top-level statement that is not a
  definition and names a constant, and that constant is edited
- **THEN** every node tracking that module is re-derived, including a node
  that does not itself name the constant

#### Scenario: A decorated definition is never left out

- **WHEN** a tracked module holds a decorated function that no node names, and
  a constant that function names is edited
- **THEN** every node tracking that module is re-derived

#### Scenario: A dynamic lookup keeps its file whole

- **WHEN** text a node retains calls `vars(module)` on a tracked module, and a
  definition of that module the node does not otherwise name is edited
- **THEN** the node's artifacts are re-derived

#### Scenario: A node class that is not a top-level class statement keeps its file whole

- **WHEN** a node's class is made by a factory function in its own source, and
  that function is edited
- **THEN** the node's artifacts are re-derived

#### Scenario: A file tracked beyond the node's own closure is retained whole

- **WHEN** a node tracks a Python file outside its own source's import closure,
  as an imported-mesh leaf tracks its wrapper module, and a definition in that
  file that nothing names is edited
- **THEN** the node's artifacts, and every ancestor's, are re-derived

#### Scenario: A record of the earlier rule is verified once and re-recorded

- **WHEN** an artifact carries a record written under the earlier rule whose
  digest matches the earlier rule's digest of the present sources, its
  timestamps are rewritten, and the earlier rule left out nothing the current
  rule retains
- **THEN** the artifact is not re-derived, its record is rewritten under the
  current rule, and a later edit to a definition the node never names leaves it
  current

#### Scenario: A record of the earlier rule is not carried past text the current rule retains

- **WHEN** an artifact carries a record written under the earlier rule whose
  digest matches, but the earlier rule left out a sibling node class that
  another tracked file names
- **THEN** the artifact is re-derived and recorded under the current rule

#### Scenario: A settled record of the earlier rule stays on the metadata-only path

- **WHEN** an artifact carries a record written under the earlier rule and its
  stamp and fingerprint match the node's current sources
- **THEN** it is current without any source being read, and its record is not
  rewritten

#### Scenario: An import inside a function or a block binds names for its module

- **WHEN** a function a node calls imports a constant with `from .spec import
  X` and reads bare `X`, or a method imports `spec` and reads `spec.X`, no
  top-level statement imports `spec`, and `X` is edited
- **THEN** the node's artifacts are re-derived

#### Scenario: Importing several names keeps only the ones a node reads

- **WHEN** a node's module imports `from .spec import X, Y`, the node reads
  only `X`, its artifacts are current, and `Y` is edited
- **THEN** the node's artifacts are restamped without being re-derived, and a
  node that reads `Y` is re-derived

#### Scenario: A computed attribute read on a module keeps the module whole

- **WHEN** text a node retains reads `getattr(spec, name)` with `spec` bound to
  a tracked module and `name` computed, and a definition of `spec` that no text
  spells, or a definition another module holds and `spec` imports by a name no
  text spells, is edited
- **THEN** the node's artifacts are re-derived

#### Scenario: The first edit after upgrading is judged by the earlier rule

- **WHEN** an artifact carries a record written under the earlier rule, and a
  definition the node never names is edited in text the earlier rule retains
- **THEN** the artifact is re-derived once and recorded under the current rule,
  and the next such edit leaves it current
