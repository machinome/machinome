## ADDED Requirements

### Requirement: Project sandboxing
Every tool in the floor-provided MCP tool set SHALL resolve path arguments
against the active project's root and SHALL reject any resolved path that
falls outside that root.

#### Scenario: Path escapes project root
- **WHEN** a tool is called with a path argument that resolves outside the
  active project's root (e.g. via `..` traversal or an absolute path elsewhere)
- **THEN** the tool call fails without performing any filesystem or process
  action

#### Scenario: Path stays within project root
- **WHEN** a tool is called with a path argument that resolves inside the
  active project's root
- **THEN** the tool call proceeds normally

### Requirement: Backend scope
The scoped-agent-tools capability SHALL be available to the `claude` and
`opencode` backends and SHALL NOT be offered on the `codex` backend.

#### Scenario: Role selects claude or opencode with scoped tools
- **WHEN** a role configured for scoped tools opens on the `claude` or
  `opencode` backend
- **THEN** the session has no native file, shell, or network tool reachable,
  only the floor-provided MCP tool set

#### Scenario: Role selects codex
- **WHEN** a role opens on the `codex` backend
- **THEN** the session runs with codex's existing full native tool access,
  and scoped-agent-tools is not applied

### Requirement: Filesystem read tools
The tool set SHALL provide `list_dir`, `find_files`, `search_content`,
`read_file`, and `stat` for read-only inspection of the project.

#### Scenario: Reading a text file
- **WHEN** `read_file` is called on a text file within the project
- **THEN** it returns the file's text content, honoring an optional
  offset/limit line range

#### Scenario: Reading a raster image file
- **WHEN** `read_file` is called on a PNG, JPG, GIF, or WEBP file within the
  project
- **THEN** it returns image content directly, viewable by the calling model,
  rather than raw bytes rendered as text

#### Scenario: Reading an SVG file
- **WHEN** `read_file` is called on an `.svg` file
- **THEN** it returns the file's text/markup content, not rendered image
  content

### Requirement: Filesystem write tools
The tool set SHALL provide `write_file`, `edit_file`, `apply_patch`,
`delete_file`, `move_file`, and `make_dir` for modifying project files.

#### Scenario: Targeted edit
- **WHEN** `edit_file` is called with an old and new string that match
  exactly once in the target file
- **THEN** the file is updated with the replacement and no other content
  changes

#### Scenario: Unified diff patch
- **WHEN** `apply_patch` is called with a unified diff against a file in the
  project
- **THEN** the file is updated to match the diff's result

### Requirement: Git tools
The tool set SHALL provide `git_status`, `git_diff`, `git_log`, `git_show`,
`git_rev_parse_toplevel`, `git_merge_base_is_ancestor`, `git_head`,
`git_add`, and `git_commit`, and SHALL NOT provide `push`, `reset`,
`checkout`, `branch`, or `rebase` operations.

#### Scenario: Reporting HEAD after a commit
- **WHEN** `git_commit` completes successfully
- **THEN** `git_head` returns the resulting commit sha and current branch

#### Scenario: Verifying drawing ancestry
- **WHEN** `git_merge_base_is_ancestor` is called with a previously released
  drawing commit
- **THEN** it reports whether that commit is an ancestor of the current HEAD
  (or of a given ref)

#### Scenario: No destructive git operation is exposed
- **WHEN** an agent attempts to call a push, reset, checkout, branch, or
  rebase operation through the tool set
- **THEN** no such tool exists to call

### Requirement: solid-node build and test tools
The tool set SHALL provide `solid_build` and `solid_test`, matching the
`solid build` and `solid test` CLI commands' arguments and exit semantics.

#### Scenario: Build failure is reported, not swallowed
- **WHEN** `solid_build` is called against a project whose model fails to
  build
- **THEN** the tool reports nonzero/failed status and the failure detail,
  without publishing a broken model over a previous good one

### Requirement: solid-node snapshot tool returns image content directly
The tool set SHALL provide `solid_snapshot`, accepting the same rendering
options as the `solid snapshot` CLI command, returning the rendered image as
direct tool output, and SHALL NOT leave any generated file inside the project
tree.

#### Scenario: Snapshot does not appear in git status
- **WHEN** `solid_snapshot` is called against a project with a clean working
  tree
- **THEN** the tool returns the rendered image content, and `git_status`
  afterward still reports a clean working tree

#### Scenario: No output-path argument
- **WHEN** `solid_snapshot` is called
- **THEN** it accepts rendering options (time, camera, image size,
  projection, color scheme, view flags, autocenter/viewall) but no `-o`/output
  path argument
