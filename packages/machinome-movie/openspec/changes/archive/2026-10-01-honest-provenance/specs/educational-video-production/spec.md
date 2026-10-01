## ADDED Requirements

### Requirement: Provenance says whether each source tree was dirty

Wherever production records a Git head, it SHALL record beside it whether
that work tree was dirty: a tracked file changed, staged or not, or an
untracked path Git does not ignore. The trees are the project repository
(`projectHead`, `projectDirty`) and Videomaker's own checkout
(`workflowHead`, `workflowDirty`). `preview` and `render` SHALL read both
trees once, before the first frame, and use that reading in every record
they write: the render manifest's `provenance`, each captured shot
generation's `index.provenance`, and the preview's `report.json`. `check`,
`preview` and `render` SHALL each print a `Project tree:` and a
`Videomaker tree:` line: `clean at` the head, or `dirty at` the command,
how many paths differ from the head, at most three of them by name, and
what that means for the command's record. A dirty tree MUST NOT be refused.

The render manifest SHALL list in `releaseIssues` every reason it is not
release-ready, in words: a missing description template, each unresolved
public link, each picture release issue, and each tree dirty at render,
naming the tree, the head and the paths. `releaseReady` SHALL be true
exactly when `releaseIssues` is empty. Whether a tree was dirty MUST NOT
enter the shot cache's common key or any shot's key.

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
