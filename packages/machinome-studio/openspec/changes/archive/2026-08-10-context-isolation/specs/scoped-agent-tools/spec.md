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

#### Scenario: Claude reports the floor MCP server pending before connected
- **WHEN** a scoped Claude role's first real broker envelope triggers init
  frames with the floor server `pending` before a later frame reports it
  `connected`
- **THEN** the envelope remains the session's first user message and its
  delivery waits within a separate bounded readiness deadline, succeeding only
  after the connected frame exposes exactly the expected scoped tools

#### Scenario: Claude role process waits for its first input before init
- **WHEN** a scoped Claude process stays alive but emits no init frame before
  receiving user input
- **THEN** project opening manifests the role after the bounded process-exit
  grace without a warm-up message or a readiness deadlock

#### Scenario: Claude MCP readiness never succeeds
- **WHEN** the first broker delivery triggers initialization but the Claude
  process exits, reports a terminal floor-server failure, or does not connect
  before the bounded readiness deadline
- **THEN** that delivery fails with the relevant process, MCP, or timeout
  evidence and the failed role process is stopped

#### Scenario: Role selects codex
- **WHEN** a role opens on the `codex` backend
- **THEN** the session runs with codex's existing full native tool access,
  and scoped-agent-tools is not applied

### Requirement: Runtime location independence
The shop SHALL treat the caller-supplied `--projects-dir` as the exact and sole
project catalogue, SHALL load trusted shop resources from the running shop
package or source worktree, SHALL invoke the solid-node CLI installed in the
same Python environment as the running shop, and SHALL NOT require or discover
a Git checkout or ambient `PATH` executable to start the hub or its backend
processes.

#### Scenario: Installed shop with an unrelated project catalogue
- **WHEN** the shop starts outside a Git repository with `--projects-dir`
  naming an arbitrary external directory
- **THEN** the hub inventories that exact directory and loads profiles,
  prompts, skills, static assets, and backend code from the running shop
  installation

#### Scenario: Source worktree exercises its own MCP implementation
- **WHEN** the shop is launched from a source worktree and a scoped backend
  starts an MCP process in an isolated role directory
- **THEN** the child imports the same worktree's `floor.mcp_server`
  implementation without resolving or reading a primary checkout

#### Scenario: Ambient PATH contains a different solid executable
- **WHEN** the shop's Python environment contains its selected solid-node CLI
  and an unrelated or broken `solid` executable appears earlier on `PATH`
- **THEN** project preparation and agent tools invoke the CLI from the shop's
  Python environment

### Requirement: Isolated OpenCode role events remain observable
The OpenCode backend SHALL observe completion and failure events for every
role session it creates in an isolated working directory and SHALL publish
only events belonging to its registered role sessions.

#### Scenario: Foreman completes in an isolated role directory
- **WHEN** an OpenCode Foreman session produces assistant text and becomes
  idle in its unique role working directory
- **THEN** the backend emits that text and turn completion to the shop broker

#### Scenario: Foreman sends multiple text parts before becoming idle
- **WHEN** an OpenCode Foreman session completes assistant text parts while the
  turn remains active
- **THEN** each completed text part appears in the browser when its update
  event arrives, exactly once and without waiting for the idle event

#### Scenario: Unrelated OpenCode directory emits an event
- **WHEN** the shared OpenCode server reports an event for a directory or
  session not registered by this backend
- **THEN** the backend ignores it without changing any shop role state

### Requirement: Conversation transcript remains readable above the composer
The browser SHALL keep the independently scrollable conversation transcript
within its own bounded layout region above the persistent message composer,
whether or not agent-failure notices are present.

#### Scenario: Conversation has no agent-failure notice
- **WHEN** the transcript contains enough messages to overflow its available
  height and no failure notice is rendered
- **THEN** the transcript scrolls within the space above the composer and its
  last message is not covered by the textarea

#### Scenario: Conversation has an agent-failure notice
- **WHEN** a failure notice and overflowing transcript are rendered together
- **THEN** the failure area, transcript, and composer remain in their assigned
  non-overlapping layout regions

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

### Requirement: Shop broker lifecycle tools
The tool set SHALL provide `floor_assign`, `floor_direction`,
`floor_acknowledge`, `floor_report`, and `floor_complete` as bounded wrappers
around the existing active-session broker operations, and SHALL NOT expose a
generic network or HTTP request tool.

#### Scenario: Foreman dispatches through the scoped surface
- **WHEN** the foreman calls `floor_assign` with a declared recipient,
  assignment identifier, and task text
- **THEN** the tool posts that assignment to the injected active floor session
  and returns the broker response

#### Scenario: Specialist completes the delegated lifecycle
- **WHEN** a specialist acknowledges, reports, and completes its assignment
  through the corresponding floor tools
- **THEN** each call reaches only the injected active floor session and the
  broker applies its existing identity, edge, and lifecycle validation

#### Scenario: No arbitrary network operation is exposed
- **WHEN** an agent inspects or invokes the floor-provided tool set
- **THEN** no tool accepts a URL, HTTP method, route, headers, or arbitrary
  request body
