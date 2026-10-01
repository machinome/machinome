## Context

`render` (`src/render.mjs`) records two Git heads. Before capture it builds
`captureProvenance` (`workflowHead`, `projectHead`, the input hashes and the
common key), which every shot generation it captures keeps as
`index.provenance` (`src/shot-cache.mjs`), and which the manifest repeats
per shot as `cache.shots[].origin`. After the encode it reads both heads
again for the manifest's `provenance`. Neither reading looks at the work
tree: a head is recorded whatever is modified or untracked beside it. The
review pack (`src/review-pack.mjs`) restates no provenance; its index is
bound to the manifest by SHA-256. `preview` records no head at all. `check`
(`bin/videomaker.mjs`) prints `Stage: … (sha256 <12>)` from the bundle's
`sha256`, the script's; the bundle (`src/stage-build.mjs`) already returns
`cssSha256`, and the render manifest records it as `stageCssSha256`.

The Curta film was rendered with its whole source uncommitted, and the
manifest named the commit before it.

## Goals / Non-Goals

Goals: every record that names a head says whether its tree was dirty when
the frames were made; the three commands say it in words; a film made from
a dirty tree is not release-ready, with the reason; the `Stage:` line moves
when the stylesheet does. Non-goals: those of the proposal.

## Decisions

### D1. What "dirty" is

A work tree is dirty when `git status --porcelain=v1
--untracked-files=normal` lists anything: a tracked file modified, added,
deleted or renamed, staged or not, or an untracked path Git does not
ignore. The command runs with `--no-optional-locks`, so reading the state
never writes the index of a tree another process may be using. An ignored
path (a build directory, an ignored export) is not dirt. The paths are
kept as Git prints them, an untracked directory collapsed to its name, for
the report; the records keep a boolean.

No path is judged more or less important than another: an untracked note
beside the film is dirt as much as an edited `stage.css`, because the head
does not contain it either way. The line names the paths so the author can
commit, ignore or remove them.

### D2. Two trees, read once, before the first frame

The two trees are the ones whose heads the records already carry: the
project repository (`film.paths.repository`) and Videomaker's own checkout
(the directory above `src/`). `src/provenance.mjs` reads one tree
(`treeState(cwd)` → `{head, dirty, changes}`) and words it (`treeLine`,
`treeReleaseIssue`); it locates nothing itself, its callers pass the
directories.

`preview` and `render` read both trees once, before the browser session
opens, after the film is loaded and its takes re-read, and use that one
reading everywhere: `render` in every captured shot's `index.provenance`
and in the manifest's `provenance` (the second reading of the heads after
the encode goes); `preview` in its `report.json`. A tree changed during a
render is not caught; what was loaded was read before this reading, and a
second one after the encode would only add a disagreement to explain. `check`
reads both trees when it has finished its checks and prints them last.

### D3. The records

Beside each head, its dirt: `provenance.projectDirty` and
`provenance.workflowDirty` in the render manifest, the same two fields in
each captured shot's `index.provenance` (and so in `cache.shots[].origin`),
and `provenance: {workflowHead, workflowDirty, projectHead, projectDirty}`
in the preview's `report.json`. Field names follow the existing
`workflowHead` and `projectHead`; the words say "Videomaker tree" for the
first, since "workflow" is the field's history, not a name a reader knows.

A shot generation is verified for reuse as before: the new fields are not
required, so a generation captured before this change stays reusable, and
its origin then says nothing of its tree. The render's own `provenance` is
the record of the film.

### D4. A dirty tree is not release-ready, either tree

`releaseReady` was the conjunction of a description template, two public
links and no picture issue, with only the picture issues written down. The
manifest gains `releaseIssues`: every reason, in words, in a fixed order:

    no release.descriptionTemplate: description.md is not written
    release.simulationUrl is unresolved
    release.sourceUrl is unresolved
    <each entry of pictureReleaseIssues>
    project tree dirty at render: 2 paths differ from projectHead 23c9e6f1a2b3 (notes.txt, stage.css)
    Videomaker tree dirty at render: 1 path differs from workflowHead 54d64d8e0f1a (src/render.mjs)

`releaseReady` is `releaseIssues.length === 0`. `pictureReleaseIssues`
stays as it is specified (`stills-and-clips`); its entries are repeated in
`releaseIssues`, which is the list a reader acts on.

Videomaker's tree blocks a release as the project's does. The heads are
there so that a film can be traced to what made it; a tool tree with
uncommitted changes made pixels no recorded head can make again. Rendering
from a worktree under development is a rehearsal, which is what the
record then says.

### D5. The words

Each command prints two lines, the project's first:

    Project tree: clean at 23c9e6f1a2b3
    Project tree: dirty at check, 5 paths differ from its head 23c9e6f1a2b3 (export/, CREDITS, curta-2x-files/ and 2 more); a render now records a head that is not the content rendered and is not release-ready
    Videomaker tree: dirty at preview, 1 path differs from its head 54d64d8e0f1a (src/render.mjs); the preview's workflowHead is not the tool that previewed
    Project tree: dirty at render, 1 path differs from its head 23c9e6f1a2b3 (notes.txt); the manifest's projectHead is not the content rendered, and the film is not release-ready

A head is printed to twelve hex digits, like the stage bundle's hash. At
most three paths are named, then `and N more`. `render` prints its lines
before the first frame is captured, `preview` likewise, `check` after its
other lines. Nothing is refused: a dirty tree renders a rehearsal.

### D6. The dirt is not a picture input

The flags enter no cache key: not the common key (`commonKey` hashes page
files, renderer sources, fonts, browser, style, sizes) and not a shot's
key. A render from a dirty tree whose inputs are unchanged reuses every
verified shot; the frames are the same whatever Git says about the tree.
The proof renders clean, then dirty, and asserts the same common key and no
frame captured. `render.mjs` is itself one of the common key's inputs, so
this change, like any change of the renderer, recaptures every film once;
that is the key's existing composition, not the dirt.

### D7. The `Stage:` line carries both hashes

    Stage: bundled <root>/_build/stage/stage.js (sha256 1a2b3c4d5e6f) and stage.css (sha256 e3b0c44298fc) from stage.tsx; types checked

The stylesheet is named by its file name; it lies beside the script, whose
path the line already gives. A bundle without a stylesheet writes an empty
`stage.css`, whose hash is printed as any other. The rest of the line is
unchanged.

### D8. `WTs/` is ignored

`AGENTS.md` says worktrees live under `WTs/<name>/`, "which is ignored";
the `.gitignore` did not ignore it, so the primary checkout with any
worktree lists `WTs/` as untracked, and every render made from it would be
reported dirty for a directory that is no part of the tool. The line
`/WTs/` makes the contract true.

### D9. Tests and the memo

The project's tree is the test's own: a copy committed by the fixture's
recipe, its build directory and export ignored, the viewer double written
inside the ignored export. Videomaker's tree is the checkout the suite runs
in, which is dirty while a change is made and clean when it is committed;
the memo does not key it (ADR-003: Git state recorded as provenance decides
no verdict). So no assertion reads Videomaker's dirt but for its type and
its line's shape; the clean case asserts that no reason in `releaseIssues`
but Videomaker's own remains.

## Alternatives rejected

- **Refuse to render from a dirty tree.** Every rehearsal is made from a
  tree being edited; the finding is that the record lies, not that the
  render ran.
- **`git describe --dirty`, or a `-dirty` suffix on the head.** It changes
  the meaning of a field a reader compares with `git rev-parse`; a boolean
  beside it does not.
- **Hash the dirt** (the diff against the head and the untracked files'
  bytes) so a dirty render could be reproduced. It would make the record
  reproducible rather than honest, which no film has needed; the
  framework's export provenance is a separate, later change.
- **Weigh the paths**, counting only `src/` or the movie's directory. Which
  paths reach a film is the shot key's business; the tree's dirt is about
  the head, and every path is outside it alike.
- **A dirty flag in the shot key**, so that a dirty capture is never reused
  as a clean one. The pixels do not depend on it, and the key holds only
  what pixels depend on.
- **Restating the dirt in the review pack.** Its index is bound to the
  manifest's SHA-256, and the manifest says it.
