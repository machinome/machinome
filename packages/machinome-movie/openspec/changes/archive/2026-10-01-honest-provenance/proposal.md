## Why

The episode is *Addition*, the Curta film of the curta-video campaign (the
Curta Type I 3x project, `videos/addition/`), the first film on a clocked
take. Producing it met two findings (`workflow/warts.md`, "Addition (Curta,
1 October 2026)", 5 and 6):

5. **Render provenance records `projectHead` for a dirty tree.** The film's
   source (`takes.py`, `movie.py`, `stage.tsx`, `stage.css`) was
   uncommitted at render time, and `rehearsal-manifest.json` names the last
   commit as if it were the content rendered. The same holds for
   `workflowHead`, Videomaker's own checkout: the manifest, every shot
   generation's `index.provenance` and, through the manifest it is bound
   to, the review pack say "this head" and never "this head plus changes".
6. **`check`'s `Stage:` line hashes only `stage.js`.** The film's look was
   tuned in `stage.css`; a stylesheet edit leaves the script's bytes, and
   so the line, identical, though the bundle was rebuilt and the manifest
   carries `stageCssSha256`. The author looks at the line to see that the
   change took, and it says nothing changed.

## What the film does with the result

The Curta film is re-checked from the campaign head: `check` says, in
words, whether the project tree and Videomaker's tree are clean, and, if
not, which paths differ from the head the manifest would record; its
`Stage:` line carries the stylesheet's hash beside the script's, so the
next edit of `stage.css` shows. A render of *Addition* from a dirty tree
records that it was dirty, and is not release-ready for that reason, by
name, beside the release gaps it already has.

## What Changes

- **Provenance says whether each tree was dirty.** `preview` and `render`
  read each Git work tree they record a head of, the project's and
  Videomaker's own, once before the first frame: its head and whether it
  was dirty, a tracked file changed (staged or not) or an untracked file
  Git does not ignore. Beside `projectHead` and `workflowHead`, the render
  manifest's `provenance`, every shot generation's `index.provenance` and
  the preview's `report.json` record `projectDirty` and `workflowDirty`.
  The manifest's heads are read once, with the dirt, instead of again after
  the encode.
- **The commands say it in words.** `check`, `preview` and `render` each
  print a `Project tree:` and a `Videomaker tree:` line: `clean at <head>`,
  or `dirty at <command>`, how many paths differ from the head, the first
  three of them, and what that means for the command's record.
- **A film rendered from a dirty tree is not release-ready.** The manifest
  gains `releaseIssues`, every reason `releaseReady` is false in words: the
  missing description template, an unresolved public link, the picture
  issues `pictureReleaseIssues` already lists, and a tree that was dirty at
  render. `releaseReady` is true exactly when it is empty.
- **The `Stage:` line carries both hashes**: `Stage: bundled <path>/stage.js
  (sha256 <12>) and stage.css (sha256 <12>) from <modules>; …`.
- **The dirt is provenance, not a picture input.** It does not enter the
  shot cache's common key or any shot key; a shot generation captured from
  a clean tree is reused from a dirty one, and the reverse.
- **Repository hygiene the check needs**: Videomaker's `.gitignore` ignores
  `WTs/`, as `AGENTS.md` already says it does; without it every render from
  the primary checkout that has a worktree is reported dirty.
- **Proofs**: a pipeline test renders a fixture project clean, then with an
  untracked file, then with a tracked file changed, through `check`,
  `preview` and `render` on the command line; a pipeline test changes only
  the tour's stylesheet and checks twice.
- **Records**: ADR-015 (PIPELINE); `README.md`, `docs/stage.md`,
  `docs/architecture-overview.md`, `CHANGELOG.md`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `educational-video-production`: provenance says whether each tree was
  dirty, the three commands say it, and a dirty tree blocks a release with
  its reason in `releaseIssues`.
- `react-stage`: `check` reports the bundle's stylesheet hash beside its
  script's.

## Impact

Code: `src/provenance.mjs` (new), `src/render.mjs`, `bin/videomaker.mjs`;
`.gitignore`; tests `test/pipeline/provenance.test.mjs` (new),
`test/pipeline/movie-pipeline.test.mjs`; `test/support/reach.mjs`. No
schema, contract page, Python, stage runtime or viewer change. `render.mjs`
is itself hashed into the shot cache's common key, so its edit recaptures
every film once, as any change of the renderer does; the dirt adds nothing
to that key.

## Non-goals

The framework's export provenance (a framework cycle adds the source
revision to the export manifest; a later Videomaker change reads it) and
any change to `source-revision.txt` handling. No judgement of which dirty
path matters: dirty is dirty, and the line names the paths. The review
pack is not changed: it is bound to the manifest's SHA-256, which now
records the dirt. No refusal: a dirty tree still renders a rehearsal.
No publication, push or paid request.
