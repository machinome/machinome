# ADR-015: Provenance records whether each tree was dirty, and a dirty tree is not release-ready

Status: Accepted (OpenSpec change `honest-provenance`, 1 October 2026).

## Context

A render records two Git heads: `projectHead`, the project repository's,
and `workflowHead`, Videomaker's own checkout's. It wrote them in the
manifest's `provenance` and in every shot generation's `index.provenance`
(and so in the manifest's `cache.shots[].origin`); the review pack is bound
to that manifest by its SHA-256. The heads were read with `git rev-parse
HEAD` and nothing else. The Curta film *Addition* was rendered with its
whole source (`takes.py`, `movie.py`, `stage.tsx`, `stage.css`)
uncommitted, and its manifest named the commit before it as if it were the
content rendered. `preview` recorded no head at all, `check` said nothing of
either tree, and `releaseReady` was a conjunction with only its picture
reasons written down.

## Decision

1. **Dirty is what Git lists.** A tree is dirty when `git status
   --porcelain=v1 --untracked-files=normal` lists anything: a tracked file
   changed, staged or not, or an untracked path Git does not ignore. It is
   read with `--no-optional-locks`. No path is weighed: every path Git
   lists is outside the head alike. `src/provenance.mjs` reads a tree and
   words it; it locates nothing.
2. **Read once, before the first frame.** `preview` and `render` read both
   trees once, before the browser session, and use that reading in every
   record they write; `render` no longer reads the heads again after the
   encode. `check` reads them after its other checks.
3. **Recorded beside each head.** `projectDirty` and `workflowDirty` sit
   beside `projectHead` and `workflowHead` in the render manifest's
   `provenance`, in each captured shot generation's `index.provenance`, and
   in the preview's `report.json`.
4. **Said in words.** `check`, `preview` and `render` print a
   `Project tree:` and a `Videomaker tree:` line: `clean at` the head, or
   `dirty at` the command, how many paths differ, at most three by name,
   and what it means for that command's record. Nothing is refused.
5. **Either tree dirty at render blocks a release.** The manifest's
   `releaseIssues` lists every reason in words (the description template,
   each unresolved public link, each picture issue, each dirty tree with
   its head and paths), and `releaseReady` is true exactly when it is
   empty. Videomaker's tree counts as the project's does: a tool with
   uncommitted changes made pixels no recorded head can make again.
6. **Provenance, not a key.** The dirt enters neither the shot cache's
   common key nor any shot key, and a generation's reuse does not require
   the new fields. A dirty render of unchanged inputs reuses every verified
   shot.

## Options considered

- **Refuse a render from a dirty tree.** Rehearsals are made from trees
  being edited; the finding was that the record lied, not that it ran.
- **`git describe --dirty` in the head field.** It changes what a field
  compared with `git rev-parse` holds; a boolean beside it does not.
- **Hash the dirt** (the diff against the head and the untracked bytes) so
  a dirty render can be reproduced. Honest is what was asked; reproducing
  a dirty film has no episode.
- **Count only paths that reach the film.** That is the shot key's work;
  the head's truth does not depend on which file is outside it.
- **Only the project's tree blocks a release.** The manifest names the
  tool's head for the same reason it names the project's.

## Consequences

- A film rendered while its source or the tool is being edited says so in
  its manifest, its shot generations, its report lines and its release
  record; making it release-ready means committing (or ignoring) what Git
  lists and rendering again, which reuses every shot.
- A project that leaves a build product untracked and unignored (an export
  directory, a downloaded reference) is reported dirty until it ignores it.
- Videomaker's `.gitignore` ignores `WTs/`, which `AGENTS.md` already said
  it did, so the primary checkout is not dirty because a worktree exists.
- `render.mjs` is hashed into the common key, so the change itself
  recaptures every film once, as every change of the renderer does.
- The review pack is unchanged: it is bound to the manifest, which carries
  the dirt.
