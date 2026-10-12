# ADR-019: The model's revision is the one its export records

Status: Accepted (OpenSpec change `read-the-exports-source`, 1 October 2026)

Numbered 019 by the addition-warts campaign's plan; ADR-013, ADR-014,
ADR-017 and ADR-018 are other cycles' of the same campaign. A merge that
reorders them renumbers.

## Context

A film is pinned to the commit its model was exported from:
`model.sourceRevision` is the revision its source panels read their
excerpts at, and the commands refuse a film whose pin differs from what the
export says. The export said it in a sidecar beside its manifest,
`source-revision.txt`, which the Python evaluation copied into the
document (or wrote `null` when it was absent) and the Node loaders compared
with the pin (failing with a bare `ENOENT` when it was absent). The
framework never wrote that file: one project's gallery script wrote it
after exporting, and the Curta film *Addition* typed it by hand (finding 9
of its warts; the framework's finding 3 of the Curta). A hand-typed file
can be wrong, stale or missing, and none of them said whether the tree
exported was the revision named.

The pilot ruled on 1 October 2026 that the framework's export records its
origin inside `manifest.json`. The framework's ADR-158 does: a top-level
`source: {revision, dirty}`, the full object name of the commit checked out
in the work tree holding the project root and whether `git status`
listed anything when the export started, present when the root is in a
Git work tree with a commit, absent otherwise, additive (no version bump;
a consumer that ignores it renders the same picture).

## Decision

**The revision is the manifest's `source.revision`, and nothing else.**
Both runtimes read it there. Evaluation writes it as the document's
`model.sourceRevision`; `loadMovie` and `loadEpisode` hold the film's pin
to it. No file beside the manifest is read for it, and nothing falls back
to a sidecar: an export with a sidecar and no `source` was made before the
framework recorded it, and is exported again.

**An export without a source is refused by name**, in both runtimes,
naming the manifest, the missing field `source.revision` and the remedy:
export the model again with a framework that records it, from the
project's Git repository with a commit, since a project outside Git cannot
be filmed with a pinned revision. A `source.revision` that is not a full
SHA-1 or SHA-256 object name, or a `source.dirty` that is not a boolean,
is refused naming the field and the value. A pin that differs is refused
naming both revisions in full.

**The export's dirt is provenance.** The film carries the record it was
loaded with. `check`, `preview` and `render` print it after the tree lines
of ADR-015, `Export: made from <revision>, clean` or `dirty` with what it
means for the command's record; the render manifest's `provenance`, every
captured shot generation's `index.provenance` and the preview's
`report.json` record `exportRevision` and `exportDirty` beside the heads;
an export made from a dirty tree is a `releaseIssues` entry in words. It is
never refused.

**The export's source is no picture input.** The manifest is served and
recorded byte for byte; the shot cache's common key hashes it without its
`source` record, so an export made again from another commit, or with
other dirt, keeps the key and reuses every verified shot. The excerpts the
revision selects reach the frames' requests, which the shot keys hash.

## Options considered

- **Keep the sidecar as a fallback.** It keeps a file the framework never
  wrote as a second authority; the pilot ruled the record into the
  manifest, and a step is not a protocol.
- **Evaluate an export without `source` to an unpinned document.** The
  loaders refuse a `null` pin anyway; refusing where the export is read
  names the cause and the remedy first.
- **Refuse an export made from a dirty tree.** Exporting work in progress
  is normal and the framework allows it; the record must say so, not stop
  the rehearsal.
- **Keep `source` in the common key.** Every commit of the project and
  every untracked file would recapture a whole film whose pixels cannot have
  changed.
- **Hold the export's revision to the project's head.** An export from an
  earlier commit is legitimate; the tree lines say what the project is now.

## Consequences

- A film's pin and its export can no longer disagree silently, and no
  project writes or types a revision file; the Curta's export is made
  again by `machinome export` alone, and the gallery script that writes
  the sidecar can stop.
- Every export filmed must be made by a framework that records its source,
  from a Git repository with a commit. An export made before is refused
  until it is made again.
- A render records three revisions, each beside its dirt: the project's
  head, Videomaker's head and the export's origin.
- The fixture project's exports are made from its recipe commit by
  `scripts/pin-fixture-project.mjs`, so the framework records the revision
  the fixture documents pin.
- `render.mjs` is hashed into the common key, so this change recaptures
  every film once, as any renderer change does; after it, the export's
  `source` moves no key.
