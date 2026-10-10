# ADR-158: An Export Records the Revision It Was Made From

**Status:** Accepted
**Date:** 2026-10-01
**Change:** [`export-records-its-revision`](../../../openspec/changes/archive/2026-10-01-export-records-its-revision/)
**Related to:**
- [ADR-034: Shared Node-Tree Document Schema](ADR-034-shared-node-tree-document-schema.md) — the manifest's shape; `source` is a producer-owned key beside it
- [ADR-043: Content-Derived Printed-Piece Identity](ADR-043-content-derived-printed-piece-identity.md) — the `piece` precedent for an additive key
- [ADR-051: Producer-Owned Animation Time in Node-Tree Documents](ADR-051-producer-owned-animation-time-in-node-documents.md) — a producer states its own contract
- [ADR-068: Optional Viewer Package Behind a Process Boundary](ADR-068-optional-viewer-package-behind-a-process-boundary.md) — the viewer is not changed
- [BUILD/ADR-119: Named Project Models and Per-Model Build Directories](../BUILD/ADR-119-named-project-models-and-per-model-build-directories.md) — the project root the build directory is anchored on

## Context and Problem Statement

`machinome export` wrote `manifest.json` and `models/` and nothing about
where they came from. A consumer that holds an artifact to a model — a film
of a machine, a gallery page — had to learn the project revision some other
way. Videomaker, filming the clocked Curta on 1 October 2026, pins a film to
its model through `<export>/source-revision.txt` and refuses to render when
the film's pinned revision differs; the framework never wrote that file. One
project's gallery script wrote it after exporting (`git rev-parse HEAD`), and
the Curta film's had to be written by hand. A hand-typed file can be wrong,
stale or missing, and none of them said whether the tree exported matched the
revision named.

Filed as finding 3 of "Three findings from filming the clocked Curta
(1 October 2026)" in `workflow/warts.md`. The pilot ruled the same day that
the record goes inside the manifest, as a `source` object with the revision
and a dirty marker, additive as `loop` and `markings` were.

This is the first time the framework reads version control.

## Decision Drivers

- The record must travel with the document it describes.
- Outside version control, an export must be exactly what it was.
- Exporting work in progress is normal and must not be refused.
- No consumer may need to change to keep reading exports.
- Nothing new to install.

## Considered Options

1. A `source` object inside the manifest, from the `git` executable (chosen).
2. A framework-written `source-revision.txt` sidecar.
3. A `source` key in the shared document body, so the build's `viewer.json`
   carries it too.
4. A Git library (GitPython, dulwich, pygit2) instead of the executable.
5. `git describe --always --dirty` as a single string.

## Decision Outcome

Option 1.

- `export_node` asks Git once, before the build and outside the artifact
  retry loop, at `project_root(node.src)`: the root the build directory is
  anchored on and every node resolved at construction. It runs
  `git rev-parse --verify --quiet HEAD` and
  `git status --porcelain --untracked-files=normal` with
  `GIT_OPTIONAL_LOCKS=0`.
- When both answer, the manifest gains, as its last key,
  `source: {revision: <full object name>, dirty: <status printed anything>}`.
  Ignored files never count; untracked files are listed even under a user's
  `status.showUntrackedFiles=no`; the status covers the whole work tree,
  because the revision names the whole repository's commit.
- When either cannot answer — not a work tree, no commit yet, no `git`, a
  repository Git refuses — `source` is absent and nothing is logged, so the
  manifest is byte-identical to the one written before this decision.
- A dirty tree is exported. Nothing is refused.
- `source` is additive: no `version` bump, no viewer change, no new option.

Taking the record before the build means the export's own writes cannot
mark it dirty. `GIT_OPTIONAL_LOCKS=0` keeps `git status` from refreshing and
rewriting the project's index, so recording the revision writes nothing in
`.git`. The change's test proves plain `git status` would have rewritten it.

### Why not a sidecar (option 2)

A second file can be separated from the document it describes, copied
without it or left stale beside a newer manifest, and a consumer must know to
look for it. The pilot ruled the record into the manifest.

### Why not the shared document body (option 3)

`document_body` also feeds the build's `viewer.json`, rewritten on every save
under `machinome develop`, and the browser-snapshot capture. The finding is
about the export, the artifact that leaves the project; a revision in the
live build document has no consumer, and would move its bytes on every
commit. If one appears, it is a separate decision with its own evidence.

### Why not a library (option 4)

Two read-only commands do not justify a dependency, and the absence of Git is
a supported case either way. The executable is what the project's author
already uses, with the repository formats and configuration it understands.

### Why not `git describe` (option 5)

It abbreviates the hash, prefers a tag when one exists, and folds the marker
into a string a consumer would have to parse.

## Consequences

- A consumer can hold an artifact to `manifest.source.revision` and decide
  for itself what a dirty export means. Videomaker can drop
  `source-revision.txt`, and so can the gallery script that writes it; both
  are changes in their own repositories.
- The framework now runs `git`, at export only, as a best-effort read. Its
  failure is never an export failure.
- An export written inside a project that does not ignore its output
  directory is untracked, so the next export there is dirty, as the rule
  says it is.
- The framework's own committed tutorial exports, regenerated from inside the
  framework repository, will carry the framework's revision.
- `dirty` describes the moment the export started; an edit during a long
  build is not seen. The build's currency rules, not this record, decide
  which sources the meshes came from.

## References

- OpenSpec change `export-records-its-revision`, archived 2026-10-01, with
  its evidence (the red-first run and the clocked Curta export).
- `openspec/specs/export/spec.md`, requirement "Manifest contract".
- `workflow/ongoing/curta-film-findings/plan.md`.
