## Why

The episode is *Addition*, the Curta film of the curta-video campaign (the
Curta Type I 3x project, `videos/addition/`, filming the clocked model
`clocked_curta` through its export). Its finding is wart 9 of the section
"Addition (Curta, 1 October 2026)" of `workflow/warts.md`, the part of it
that is Videomaker's: `machinome export` writes no `source-revision.txt`,
yet Videomaker pins a film to its model through that file. Both runtimes
read it: `src/movie.mjs` and `src/episode.mjs` refuse a film whose
`model.sourceRevision` differs from it (and fail with a bare `ENOENT` when
it is absent), and `python/machinome_movie/evaluate.py` copies it into the
document's `model.sourceRevision` (writing `null` when it is absent). The
framework never wrote the file: one project's gallery script writes it
after exporting, and the Curta film's was typed by hand. A hand-typed file
can be wrong, stale or missing, and none of them said whether the tree
exported was the revision named. The framework filed the same finding
(its finding 3 of the Curta) and the pilot ruled on 1 October 2026 that the
export records the revision it was made from inside `manifest.json`. That
change is in the framework's `main` (096217f, its ADR-158) and installed in
the workspace: an export made inside a Git work tree with a commit carries
a top-level `source: {revision, dirty}`, `revision` the full hash of the
commit checked out, `dirty` true when Git listed anything (a tracked file
changed, or an untracked file not ignored) when the export started; the key
is absent otherwise, additive, with no version bump.

## What the film does with the result

The Curta's export is made again by `machinome export` alone (the
orchestrator does it at the campaign's close) and its hand-typed
`source-revision.txt` goes: the film is pinned to the revision the export
itself records. Until then, the untracked export predates the framework
change and has no `source`, so `check` of the film refuses it by name,
saying to export the model again; that refusal is this change's proof on
the real film. Once exported again, `check`, `preview` and `render` print
an `Export:` line saying which revision the model was exported from and
whether the project was clean then, and a render records it beside the
heads; an export made from a dirty tree (the Curta's untracked `export/`,
`CREDITS` and reference media make every export of it dirty today,
finding 17) is rendered, said and kept from release, never refused.

## What Changes

- **The revision is read from the manifest.** Both runtimes read the
  model's revision from the export manifest's `source.revision`; nothing
  reads `source-revision.txt` any more, and there is no fallback to it.
  Evaluation writes `source.revision` as the document's
  `model.sourceRevision`; `check`, `speech`, `preview`, `render` and
  `build` refuse a movie or a YAML episode whose `model.sourceRevision`
  differs from it, naming both values.
- **An export without a source is refused by name**, in both runtimes,
  naming the manifest, the missing field `source` (`source.revision`) and
  the remedy: export the model again with a framework that records its
  source, from the project's Git repository with a commit; a project
  outside Git cannot be filmed with a pinned revision, and the refusal
  says so. A `source` whose `revision` is not a full commit hash, or whose
  `dirty` is not a boolean, is refused naming the field.
- **The export's dirt is provenance.** Beside the heads, the render
  manifest's `provenance`, every captured shot generation's
  `index.provenance` and the preview's `report.json` record
  `exportRevision` and `exportDirty`. `check`, `preview` and `render` print
  an `Export:` line after the tree lines: `Export: made from <revision>,
  clean`, or `dirty` with what that means for the command's record. An
  export made from a dirty tree is a `releaseIssues` entry in words, and is
  never refused.
- **The export's source is no picture input.** The renderer serves the
  manifest as it is, and hashes it for the shot cache's common key without
  its `source` record, so an export made again with only another revision
  or another dirt reuses every verified shot.
- **The fixture project's two exports** (`counter`, `seesaw`) are made
  again with the installed framework, so their manifests carry `source`;
  their `source-revision.txt` files are deleted. They are exported from the
  fixture project's recipe commit, the revision the fixture documents
  already pin, by `scripts/pin-fixture-project.mjs`, which now makes the
  exports as well as the commit and the documents. The test doubles that
  write a synthetic export write its `source` instead of a sidecar.
- **Proofs**: layer 8, `check` of a fixture movie whose manifest has no
  `source` (refused by name) and whose `source.revision` differs from
  `model.sourceRevision` (refused naming both), and a YAML fixture project
  rendered and previewed from a clean and a dirty export (the `Export:`
  line, the provenance fields, the release issue, the same common key);
  layer 1, evaluation opens only the manifest (no sidecar) and refuses an
  export without `source`; layer 9, the manual names no sidecar.
- **Records**: ADR-019 (SOURCE); `README.md`, `docs/declaring-a-movie.md`,
  `docs/FORMAT.md` (the production `model` block), `fixtures/README.md`,
  `docs/architecture-overview.md`, `CHANGELOG.md`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `educational-video-production`: the model's pinned revision is the one
  its export records, an export without one is refused by name, and the
  export's dirt is recorded and said beside the trees' and blocks a release.
- `declarative-movie`: evaluation opens only the export's manifest of the
  export's files, writes its `source.revision`, and refuses an export
  without `source`.

## Impact

Code: `src/provenance.mjs` (the export's source read, refused and worded),
`src/movie.mjs`, `src/episode.mjs`, `src/render.mjs`, `bin/videomaker.mjs`,
`python/machinome_movie/evaluate.py`; `scripts/pin-fixture-project.mjs`;
the fixture project's exports; tests `test/pipeline/movie-pipeline.test.mjs`,
`test/pipeline/provenance.test.mjs`, `test/repository.test.mjs`,
`python/tests/test_evaluation.py`, `python/tests/test_take.py`,
`python/tests/test_repository.py`, and the helpers
`test/support/fixture-movie.mjs`, `test/support/yaml-project.mjs`,
`test/project-fixture.mjs`. No schema, stage runtime or viewer change; the
contract page `docs/movie-document.md` names no source of the revision and
is not changed. `render.mjs` is hashed into the shot cache's common key, so
this change recaptures every film once, as any renderer change does.

## Non-goals

The framework (its export is used as it is); the Curta and Leonardo
projects (their exports, gallery script and hand-typed files are the
orchestrator's and the pilot's); writing a sidecar anywhere; the viewer;
`Sim.identity` (the other half of wart 9, a later cycle once its bench is
in the framework's `main`). No judgement of an export whose revision is
not the project's head: the export says what it was made from, and the
tree lines say what the project is now. No publication, push or paid
request.
