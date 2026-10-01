## Context

The finding (proposal, `workflow/warts.md` "Three findings from filming the
clocked Curta (1 October 2026)", finding 3): an export says nothing about the
project revision it came from, so Videomaker pins a film to its model through
a sidecar `source-revision.txt` that the framework never writes and the Curta
film wrote by hand. The pilot's ruling (1 October 2026, recorded in
`workflow/ongoing/curta-film-findings/plan.md`): the record goes inside
`manifest.json` as a `source` object with the revision and a dirty marker,
additive as `loop` and `markings` were, so `version` does not move and the
viewer declares nothing new.

What exists today:

- `export_node` (`machinome/core/export.py`) builds the STLs under the project
  build lock, then serializes the tree and assembles the manifest from
  `document_body(...)` (shared with the build's `viewer.json` and the
  browser-snapshot capture) plus the two producer-owned keys, `root`'s model
  paths and `pieces`, and writes it with `json.dump(manifest, fh, indent=2)`.
  Key order is insertion order, so a key that is never inserted leaves every
  byte of the document as it was.
- Every node computes its project root at construction,
  `project_root(self.src)` (`machinome/manifest.py`, re-exported by
  `machinome.core.loader`), and `project_build_root(origin)` anchors a
  relative `SOLID_BUILD_DIR` (default `_build`) on the same root. A node
  cannot be constructed outside a project, so an exported node always has
  one. The root is a real path (`_find_manifest` resolves the origin).
- The framework never runs Git today. The build writes `_build/` and its lock
  beside it and records `_build*` in `.git/info/exclude` when `.git` is a real
  directory and the project's `.gitignore` does not already carry it
  (`exclude_build_from_git`); `machinome new`'s `.gitignore` template carries
  `_build*` and `__pycache__/`.

## Goals / Non-Goals

**Goals**

- An export of a committed project carries `source.revision`, the full hash
  of the commit checked out, and `source.dirty`, whether the work tree lists
  anything in `git status --porcelain`.
- Outside a Git work tree, or without `git`, the manifest is byte-identical
  to the one written before this change, and nothing warns.
- The export never refuses a dirty tree.

**Non-Goals**

- `source-revision.txt`: neither written nor read; its consumers retire it in
  their own repositories.
- The viewer, the document version, `machinome export`'s options.
- The build's `viewer.json` and the browser-snapshot document. Whether they
  should carry `source` too is a question for the evidence, not this change.
- Author, date, branch, remote, tag, or a list of the dirty paths.

## Decisions

### 1. The record is the export's own key, beside `pieces`

`source` is added by `export_node` after `pieces`, not by `document_body`. The
finding concerns the export, the artifact that travels; `document_body` is
shared with the build's `viewer.json`, rewritten on every save during
`machinome develop`, and with the browser-snapshot capture, and recording a
revision there would move those documents' bytes for a use nobody has. It is
the last key of the manifest when present, so every earlier byte is unchanged
even for a repository export.

### 2. The root asked is the node's project root

`project_root(node.src)`: the root `project_build_root` anchors the build
directory on, and the one every node already resolved at construction. Not
the working directory (a command run from a subdirectory or from elsewhere
must record the same thing) and not the build directory (a configured
absolute `SOLID_BUILD_DIR` may lie outside the project, and a named model's
build directory is a child of the build root, not of the sources).

### 3. Asked once, before the build

The record is taken after the keyframe is cleared and before `build_stls`,
outside the artifact-retry loop: it describes the tree the export started
from. The export's own writes (the build directory and its lock, ignored in a
project made by `machinome new`; the output directory) cannot mark this
export's record dirty. An output directory written inside the project and not
ignored is untracked and marks the NEXT export dirty, which is what the ruling
says it is.

### 4. Two Git commands, read-only

Run with `cwd` set to the root, output captured, never raising:

- `git rev-parse --verify HEAD`: the full object name of the checked-out
  commit (40 hex digits, 64 in a SHA-256 repository), detached or not.
- `git status --porcelain --untracked-files=normal`: dirty when it prints
  anything. `--untracked-files=normal` is explicit because a user's
  `status.showUntrackedFiles=no` would otherwise hide untracked files and make
  the marker lie. Ignored files are never listed. Status covers the whole work
  tree the root is in, whatever the cwd: the revision names the whole
  repository's commit, so `dirty` answers whether the checkout differs from
  that commit, and a project nested in a larger repository is marked dirty by
  a change outside it (conservative).
- Both run with `GIT_OPTIONAL_LOCKS=0`, so `git status` does not refresh and
  rewrite the project's index: an export writes nothing in `.git`.

### 5. Absent, silently, whenever Git cannot answer

`source` is absent when either command exits nonzero (not a work tree, a
repository with no commit yet, a bare repository, a repository Git refuses as
of dubious ownership) or cannot start (`git` not installed: `OSError`). No
warning, no log line at warning level: an export outside version control is
normal, and the document must be byte-identical to the one published before
this change. An unborn `HEAD` has no revision to record, so it is absent
rather than half-recorded.

### 6. Additive, no version, no viewer change

A consumer that ignores `source` renders exactly the picture it renders
today: the record adds no solid, enters no operation, binding or program, and
describes nothing an existing field describes. This is the `markings`, `loop`
and `piece` precedent and the standing rule that a producer emits the lowest
version its content needs, so `version` does not move and the viewer declares
nothing new.

### Refusals

None. The change adds no refusal: a dirty tree, a missing `git` and a
directory outside version control all export. The two existing export
refusals (`ExportModelPathError`, `WidgetBundleMissing`) are untouched.

### Alternatives rejected

- **A framework-written `source-revision.txt` sidecar.** The pilot ruled the
  record goes inside the manifest; a sidecar can be separated from the
  document it describes, and it is a second file a consumer must find.
- **Bumping `version`.** Nothing a consumer must understand changes; a bump
  would make every older viewer refuse an export it renders correctly.
- **A Git library (GitPython, dulwich, pygit2).** A new dependency for two
  read-only commands; the `git` executable is what a project's author already
  uses, and its absence is a supported case.
- **Refusing or warning on a dirty tree.** Exporting mid-work is normal; the
  marker lets the consumer decide.
- **`git describe --always --dirty`.** It abbreviates, prefers tags, and
  folds the marker into a string a consumer would have to parse.
- **Excluding the export's output directory or the build directory from the
  status.** The ruling defines `dirty` as anything `git status --porcelain`
  lists; a project that exports into its own tree ignores that directory the
  way it ignores `_build`. Recorded as a finding if the caller meets it.
- **Recording it in `document_body` for every producer.** See decision 1.

## Risks / Trade-offs

- Two `git` subprocesses per export: tens of milliseconds, against an export
  that builds every mesh. `git status` in a very large work tree with many
  untracked files is slower; still small beside the build.
- The framework's own suite exports fixture nodes whose project root is
  `tests/`, inside the framework repository, so those manifests now carry a
  `source`. No suite test compares an export's whole manifest; the tests that
  pin document bytes call `document_body` directly. The new non-repository
  test pins bytes against a manifest captured at the base commit.
- `dirty` is a fact about the moment the export started; a file edited during
  a long export is not seen. The build's own currency rules, not this record,
  decide which source the meshes came from.

## Migration Plan

None. A consumer that does not read `source` is unaffected; Videomaker and
the Leonardo gallery script retire `source-revision.txt` in their own
repositories after this lands in `main`.

## Open Questions

None for this change. Whether the build's `viewer.json` should carry `source`
is recorded in the evidence as a question, not decided here.
