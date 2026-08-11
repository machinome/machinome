# Project Source Editing Specification

## Purpose

Let the maker safely browse and edit a project's Git-visible source while
preserving concurrent agent work and the existing filesystem build boundary.

## Requirements

### Requirement: The Code navigator shows the Git-visible project working set
For an open project, the shop SHALL list tracked files and untracked files not
excluded by Git's standard ignore rules beneath the verified project root. It
SHALL synthesize their directory hierarchy and SHALL NOT list `.git`, ignored
paths, build output, build staging paths, or a path outside that project.

#### Scenario: An agent creates a source file
- **WHEN** an agent creates an untracked file that is not ignored
- **THEN** the Code navigator shows that file without a page reload or agent-tool instrumentation

#### Scenario: A path is ignored
- **WHEN** a tracked directory contains an untracked file excluded by the project's Git ignore rules
- **THEN** neither that file nor a directory existing only for ignored files appears in the Code navigator

#### Scenario: The repository contains control and build data
- **WHEN** the navigator lists a project containing `.git` and `_build`
- **THEN** neither tree is included in its result

### Requirement: The source service exposes only safe bounded project text
The shop SHALL read only a Git-visible regular non-symlink file whose resolved
path remains beneath the session's verified project root. It SHALL return
bounded UTF-8 text with a content revision and SHALL reject an escaping,
symlinked, non-regular, binary, oversized, missing, ignored, or build-output
target without exposing its content. Floor SHALL treat returned source as
inert text and SHALL NOT import, interpret, or execute it.

#### Scenario: The maker opens a source file
- **WHEN** the maker opens a bounded UTF-8 file shown by the Code navigator
- **THEN** the shop returns its text and a revision derived from those exact bytes

#### Scenario: A request escapes through a symlink
- **WHEN** a requested project path is a symlink whose target is inside or outside the project
- **THEN** the shop rejects the source request without reading the target

#### Scenario: A Git-visible file is not editable text
- **WHEN** the maker opens a binary or oversized Git-visible file
- **THEN** the navigator may show the file but the source service reports that it is unavailable for editing

### Requirement: Maker saves are revision checked and atomic
The shop SHALL accept a save only for an existing editable file whose current
content revision equals the maker's expected revision. It SHALL install an
accepted UTF-8 value by atomic same-directory replacement, preserve the file's
mode, and return the installed revision. It MUST NOT modify the file when the
expected revision is stale or the target is no longer safe and Git-visible.

#### Scenario: The maker saves the current revision
- **WHEN** the maker saves edited text with the revision they opened and nobody changed the file meanwhile
- **THEN** the complete new text atomically replaces the file and the response identifies its installed revision

#### Scenario: An agent changes a dirty file before save
- **WHEN** the maker submits a save whose expected revision no longer matches the project file
- **THEN** the shop reports a conflict and leaves the agent's current file bytes unchanged

#### Scenario: A file disappears before save
- **WHEN** an agent deletes or ignores the open file before the maker saves it
- **THEN** the save is rejected and does not recreate the file

### Requirement: Open source stays synchronized without losing dirty work
The shop SHALL publish project-scoped source invalidations for file creation,
modification, movement, and deletion without claiming which agent or process
caused them. A connected Code workspace SHALL reconcile its Git-visible tree
and affected open files from the source API. It SHALL apply a new revision to a
clean buffer, preserve a dirty buffer in a conflict state, suppress its own save
echo, and perform the same reconciliation after live-stream reconnection.

#### Scenario: An agent updates a clean open file
- **WHEN** an external write changes the revision of a clean open editor buffer
- **THEN** the editor displays the new contents without a page reload and preserves that file's view state

#### Scenario: An agent updates a dirty open file
- **WHEN** an external write changes the revision of an open buffer containing unsaved maker edits
- **THEN** the editor preserves the maker's text, marks the file conflicted, and offers reload of the external value

#### Scenario: The maker's own save is observed
- **WHEN** the filesystem observer reports the atomic replacement performed by the maker's accepted save
- **THEN** the editor remains clean at the installed revision and does not report a false external conflict

#### Scenario: The stream reconnects after source changes
- **WHEN** files change while the workspace live connection is disconnected and it later reconnects
- **THEN** the navigator and open buffers reconcile to current source while preserving any dirty buffer as a conflict

### Requirement: Code provides editing without project mutation controls
The first Code increment SHALL let the maker browse, open, edit, reload, and
save existing editable files in Monaco with per-path models, tabs, dirty and
conflict indicators, and a keyboard save action. It SHALL NOT offer maker-side
create, rename, delete, Git, terminal, debugger, or language-server controls.

#### Scenario: The maker changes files and returns
- **WHEN** the maker opens several files, edits one, visits Model, and returns to Code
- **THEN** the same tabs, active file, dirty text, cursor, selection, scroll position, and undo history remain available

#### Scenario: The maker looks for file mutation controls
- **WHEN** the maker uses the first Code increment
- **THEN** no create, rename, or delete control is presented
