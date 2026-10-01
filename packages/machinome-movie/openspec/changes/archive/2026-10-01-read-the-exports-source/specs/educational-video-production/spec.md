## ADDED Requirements

### Requirement: The model's revision is the one its export records

Production SHALL read the revision a model was exported from in the export
manifest's `source` record (`source.revision`, the full commit hash, and
`source.dirty`, whether the project's tree held changes when the export
started), as the framework writes it, and SHALL read no other file for it:
no `source-revision.txt` beside the manifest is read, and nothing falls
back to one. `check`, `speech`, `preview`, `render` and `build` SHALL
refuse, when they load the film and before any frame is posed:

- an export whose manifest has no `source`, naming the manifest, the
  missing field `source.revision`, and the remedy: export the model again
  with a framework that records its source, from the project's Git
  repository with a commit, since a project outside Git cannot be filmed
  with a pinned revision;
- a `source` whose `revision` is not a full commit hash, or whose `dirty`
  is not a boolean, naming the field and the value;
- a movie or YAML episode whose `model.sourceRevision` differs from
  `source.revision`, naming both values in full.

An export made from a dirty tree MUST NOT be refused.

#### Scenario: An export made before the framework recorded its source
- **WHEN** the author runs `check` on a movie whose export manifest has no
  `source` key, with a `source-revision.txt` beside it naming the movie's
  revision
- **THEN** `check` refuses, naming the manifest, `source.revision` and that
  the model must be exported again, and the sidecar is not read.

#### Scenario: A pin that differs from the export
- **WHEN** the export manifest records `source.revision` R and the movie's
  `model.sourceRevision` is another revision P
- **THEN** `check` refuses, naming `model.sourceRevision`, P and R.

#### Scenario: A YAML episode on a recorded export
- **WHEN** a YAML episode's production settings pin the revision its
  export's manifest records in `source.revision`
- **THEN** it is checked, previewed and rendered as before.

## MODIFIED Requirements

### Requirement: Provenance says whether each source tree was dirty

Wherever production records a Git head, it SHALL record beside it whether
that work tree was dirty: a tracked file changed, staged or not, or an
untracked path Git does not ignore. The trees are the project repository
(`projectHead`, `projectDirty`) and Videomaker's own checkout
(`workflowHead`, `workflowDirty`). Beside them it SHALL record the
revision the model's export was made from and whether the project's tree
was dirty when it was made, as the export's manifest records them in
`source` (`exportRevision`, `exportDirty`). `preview` and `render` SHALL
read both trees once, before the first frame, and use that reading in
every record they write: the render manifest's `provenance`, each captured
shot generation's `index.provenance`, and the preview's `report.json`.
`check`, `preview` and `render` SHALL each print a `Project tree:` and a
`Videomaker tree:` line: `clean at` the head, or `dirty at` the command,
how many paths differ from the head, at most three of them by name, and
what that means for the command's record; and, after them, an `Export:`
line: `made from` the export's revision and `clean`, or `dirty` with what
that means for the command's record. A dirty tree or a dirty export MUST
NOT be refused.

The render manifest SHALL list in `releaseIssues` every reason it is not
release-ready, in words: a missing description template, each unresolved
public link, each picture release issue, each tree dirty at render, naming
the tree, the head and the paths, and an export made from a dirty tree,
naming its revision. `releaseReady` SHALL be true exactly when
`releaseIssues` is empty. Whether a tree was dirty MUST NOT enter the shot
cache's common key or any shot's key, and neither SHALL the export's
`source` record: the manifest is served as it is and hashed for the common
key without `source`.

#### Scenario: A render from a project tree with an untracked file
- **WHEN** the author renders a film whose project tree holds an untracked,
  unignored `notes.txt`
- **THEN** `render` prints `Project tree: dirty at render, 1 path differs
  from its head <head>` naming `notes.txt`, the manifest records
  `projectDirty: true` beside `projectHead`, `releaseReady` is false and
  `releaseIssues` names the project tree, its head and `notes.txt`.

#### Scenario: A render from a clean project tree
- **WHEN** the project tree has no change and no unignored untracked path
- **THEN** `render` prints `Project tree: clean at <head>`, the manifest and
  each captured shot's provenance record `projectDirty: false`, and no
  reason in `releaseIssues` names the project tree.

#### Scenario: A tracked file changed before check and preview
- **WHEN** a tracked file of the project is modified and the author runs
  `check` and then `preview`
- **THEN** each prints `Project tree: dirty at` its command, naming the
  file, and the preview's `report.json` records `projectDirty: true`.

#### Scenario: Dirt is not a picture input
- **WHEN** a film rendered from a clean tree is rendered again, unchanged,
  after an untracked file appears in the project
- **THEN** the common key is the same, every shot is reused and no frame is
  captured, and only the provenance and the release record change.

#### Scenario: A clean export
- **WHEN** the export's manifest records `source` with `dirty: false`
- **THEN** `check`, `preview` and `render` print `Export: made from
  <revision>, clean`, the render manifest and each captured shot's
  provenance record `exportRevision` and `exportDirty: false`, and no
  reason in `releaseIssues` names the export.

#### Scenario: An export made from a dirty tree
- **WHEN** the film is rendered and previewed again from the same export
  marked `dirty: true`
- **THEN** each command prints `Export: made from <revision>, dirty` with
  what that means for its record, the manifest and the preview's
  `report.json` record `exportDirty: true`, `releaseReady` is false and
  `releaseIssues` names the export and its revision; the common key is the
  same and no frame is captured.
