## Why

`machinome export` writes `manifest.json` and `models/` but no record of the
project revision the export was made from. Videomaker, filming the clocked
Curta (`projects/Calculators/Curta-Type-I-3x`, model `clocked_curta`, a
version 8 document), holds a film to the model it filmed by reading
`<export>/source-revision.txt` and refusing to render when the film's pinned
`model.sourceRevision` differs (`src/movie.mjs`, `src/episode.mjs`;
`python/machinome_movie/evaluate.py` reads it too). The framework never wrote
that file: Leonardo's own `scripts/gallery.py` writes `git rev-parse HEAD`
beside its exports, and the Curta film had to write it by hand (Videomaker's
`workflow/ongoing/curta-video-campaign/spike.md` and `PROGRESS.md`, 1 October
2026). A hand-typed file can be wrong, stale or missing, and nothing says
whether the tree the export was made from matched the revision at all.

Filed as finding 3 of "Three findings from filming the clocked Curta
(1 October 2026)" in `workflow/warts.md`; the plan is
`workflow/ongoing/curta-film-findings/plan.md`. The pilot ruled on 1 October
2026 that the record goes inside the manifest, as a `source` object carrying
the revision and a dirty marker, additive under the export spec's own rule.

What the originating caller does with the result: Videomaker reads
`manifest.source.revision` in place of `source-revision.txt` to pin a film to
its model (and may read `dirty` to refuse or flag a film of uncommitted work),
and the Curta stops writing the sidecar by hand. Both are later changes in
their own repositories.

## What Changes

- `export_node` records the project's source revision in the manifest it
  writes: a top-level `source` object, `{"revision": <full commit hash>,
  "dirty": <bool>}`, when the project root is inside a Git work tree with a
  commit checked out. The root is the project root the build directory is
  already anchored on (`project_root`, from `machinome.manifest`, re-exported
  by `machinome.core.loader`, as `project_build_root` uses it).
- `dirty` is true when `git status --porcelain` for that root lists anything:
  tracked modifications or untracked files that are not ignored. An export of
  a dirty tree is never refused.
- Git is asked through a subprocess. When the root is not inside a work tree,
  has no commit yet, or `git` is not installed, `source` is absent, nothing
  warns, and the document is byte for byte what it was before this change.
- `source` is additive: it does not move `version`, and the viewer declares
  nothing new. `machinome export`'s options are unchanged.

Out: `source-revision.txt` (Videomaker and Leonardo stop using it in their own
repositories); the viewer; the document version; refusing a dirty tree;
recording anything beyond the revision and the marker (no author, no date, no
remote, no branch); the build's `viewer.json` and the browser-snapshot
document, which the finding does not concern.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `export`: "Manifest contract" lists `source` as a conditional top-level key,
  states what it holds, when it is absent, and that it is additive within the
  current version; its scenarios pin a committed project's record, a dirty
  tree's marker, and a byte-identical document outside a repository.

## Impact

- `machinome/core/export.py`: `export_node` asks Git once, before the build,
  and adds `source` beside `pieces`.
- `machinome/manager/export.py` (`machinome export`): unchanged; it reaches
  the record through `export_node`.
- Tests: a new `tests/test_export_source.py` exporting a temporary project
  through the CLI, with a manifest pinned at the base commit for the
  non-repository case.
- Docs: `docs/concepts/publishing.rst` ("The document", "An export"),
  `docs/project/changelog.rst` under `Unreleased`; `docs/architecture.md`'s
  export section; ADR-158 (EXPORT) if implementation confirms the decision is
  architectural (a producer recording provenance outside the tree it
  serializes, and the additive rule it rests on).
- Downstream, after the merge and elsewhere: the studio's
  `shop-skills/machinome-api/SKILL.md` gains the manifest's `source`;
  Videomaker reads it; Leonardo's gallery script and the Curta drop the
  sidecar.
