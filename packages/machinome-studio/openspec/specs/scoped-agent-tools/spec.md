# scoped-agent-tools Specification

## Purpose

Define the project-scoped tool surface and isolation boundaries for persistent
Claude and OpenCode roles, including runtime provenance, backend event delivery,
and the browser behavior needed to present those deliveries reliably.
## Requirements
### Requirement: Project sandboxing
Every tool in the floor-provided MCP tool set SHALL resolve path arguments
against the active project's root and SHALL reject any resolved path that
falls outside that root.

`load_skill` is the single exception and SHALL take no path argument. It
resolves a skill name against the registry the shop supplied at launch and
reads only within that skill's directory, as `runtime-skill-loading` requires.
No other tool SHALL read a registered skill directory.

#### Scenario: Path escapes project root
- **WHEN** a tool is called with a path argument that resolves outside the
  active project's root (e.g. via `..` traversal or an absolute path elsewhere)
- **THEN** the tool call fails without performing any filesystem or process
  action

#### Scenario: Path stays within project root
- **WHEN** a tool is called with a path argument that resolves inside the
  active project's root
- **THEN** the tool call proceeds normally

#### Scenario: A registered skill directory is not a project path
- **WHEN** a path-taking tool is called with a path inside a registered skill
  directory
- **THEN** the call is rejected as outside the active project

### Requirement: Backend scope
The scoped-agent-tools capability SHALL be available on every selectable
backend. A backend SHALL be selectable only if it can open a session whose
reachable tool set is exactly the profile-declared one; a backend that retains
native file, shell, or network tools regardless of the declared policy SHALL NOT
be selectable. The `claude`, `opencode` and qualified `codex` backends satisfy this.

A scoped session SHALL run with its runtime's permission checking active. The
floor tool surface is the boundary, so no backend SHALL open a session with
permission checks disabled, and no profile declaration SHALL be able to disable
them. A backend SHALL grant the session's declared tools by name so the role
never waits for a confirmation nobody can give.

#### Scenario: Role selects a qualified backend with scoped tools
- **WHEN** a role configured for scoped tools opens on the `claude`, `opencode` or
  qualified `codex` backend
- **THEN** the session has no native file, shell, or network tool reachable,
  only its declared floor tool set

#### Scenario: A role declares fewer capabilities than the whole tool set
- **WHEN** a role's declared capabilities resolve to a proper subset of the
  floor tool set
- **THEN** the session reaches exactly that subset, and the tools outside it are
  neither advertised nor callable

#### Scenario: A scoped session keeps permission checking on
- **WHEN** any scoped role session opens
- **THEN** it runs with its runtime's permission checks active while its
  declared tools execute without confirmation

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

#### Scenario: A backend that cannot enforce tool policy is not selectable
- **WHEN** a project or maker names a backend whose sessions keep native tools
  the profile did not declare
- **THEN** the selection is rejected rather than opening a session outside the
  declared tool policy

### Requirement: Runtime location independence
The shop SHALL treat the project folder the caller supplies, by the
`--projects-dir` option or by the `projects` key of the studio configuration
file, as the exact and sole project catalogue. A folder named by the
configuration file is a declared value, not discovery: the shop SHALL NOT
derive a project folder from its working directory, its installation or Git
metadata, and SHALL NOT start when neither source supplies one. It SHALL
load trusted shop resources from the running shop package or source
worktree, SHALL invoke the machinome CLI installed in the same Python
environment as the running shop, and SHALL NOT require or discover a Git
checkout to start the hub or its backend processes.

The shop SHALL depend on the ambient `PATH` executable `openspec` and SHALL
name it as an installation prerequisite. When qualifying Codex availability, resolving an explicit Codex selection,
or provisioning its dedicated login, Studio SHALL also discover
the `codex` executable on ambient `PATH`, retain its resolved executable and
qualify it against the pinned supported contract before use. Missing or
unqualified Codex SHALL NOT prevent a project using only other backends from
opening. No other shop or backend behavior SHALL require or discover an
ambient `PATH` executable under this exception.

#### Scenario: Installed shop with an unrelated project catalogue
- **WHEN** the shop starts outside a Git repository with `--projects-dir`
  naming an arbitrary external directory
- **THEN** the hub inventories that exact directory and loads profiles,
  prompts, skills, static assets, and backend code from the running shop
  installation

#### Scenario: The project folder comes from the configuration file
- **WHEN** the shop starts outside a Git repository with no `--projects-dir`
  option and a studio configuration file whose `projects` key names an
  arbitrary external directory
- **THEN** the hub inventories that exact directory, and the shop's working
  directory plays no part in choosing it

#### Scenario: Source worktree exercises its own MCP implementation
- **WHEN** the shop is launched from a source worktree and a scoped backend
  starts an MCP process in an isolated role directory
- **THEN** the child imports the same worktree's `floor.mcp_server`
  implementation without resolving or reading a primary checkout

#### Scenario: Ambient PATH contains a different solid executable
- **WHEN** the shop's Python environment contains its selected machinome CLI
  and an unrelated or broken `solid` executable appears earlier on `PATH`
- **THEN** project preparation and agent tools invoke the CLI from the shop's
  Python environment

#### Scenario: The OpenSpec CLI comes from the ambient environment
- **WHEN** the shop resolves the `openspec` CLI
- **THEN** it uses the executable on the ambient `PATH` as the unconditional
  named startup prerequisite

#### Scenario: Explicit Codex discovers only a qualified executable
- **WHEN** Studio qualifies fresh Codex availability, resolves an explicit
  Codex selection, or provisions its dedicated login
- **THEN** Studio resolves `codex` from ambient `PATH`, qualifies and retains
  that executable under its pinned supported contract, and refuses unsupported
  installations without changing package/framework resource resolution

#### Scenario: Codex is absent from a non-Codex project
- **WHEN** a project selects only other backends and ambient `PATH` has no
  qualified Codex installation
- **THEN** that project opens without a Codex prerequisite

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

`apply_patch` SHALL accept a standard unified diff describing one or more
files, SHALL derive each target from the diff's own file headers, and SHALL
apply the whole diff as a single operation that either changes every file it
describes or changes none of them. Its `path` argument SHALL be optional and,
when supplied, SHALL name the only file the diff describes.

#### Scenario: Targeted edit
- **WHEN** `edit_file` is called with an old and new string that match
  exactly once in the target file
- **THEN** the file is updated with the replacement and no other content
  changes

#### Scenario: Unified diff patch
- **WHEN** `apply_patch` is called with a unified diff against a file in the
  project
- **THEN** the file is updated to match the diff's result

#### Scenario: One patch changes several files
- **WHEN** `apply_patch` is called with a diff whose headers describe several
  files in the project
- **THEN** every described file is updated to match the diff's result and the
  call reports each file it changed

#### Scenario: One file in a multi-file patch does not match
- **WHEN** `apply_patch` is called with a multi-file diff and any file's
  context does not match its current content
- **THEN** no file in the project is modified and the error names the file,
  hunk, and line that did not match

#### Scenario: A patch creates and deletes files
- **WHEN** `apply_patch` is called with a diff that adds a file from
  `/dev/null` and removes another file to `/dev/null`
- **THEN** the new file is created with the diff's content, the removed file is
  deleted, and both are reported in the result

#### Scenario: A patch comes straight from git diff
- **WHEN** `apply_patch` is called with unedited `git diff` output, including
  its `diff --git` and `index` preamble around each file
- **THEN** every file it describes is updated as the diff specifies

#### Scenario: A patch reaches outside the project
- **WHEN** `apply_patch` is called with a diff whose file header resolves
  outside the active project
- **THEN** the call is rejected and no file is modified

#### Scenario: The supplied path disagrees with the diff
- **WHEN** `apply_patch` is called with a `path` argument and a diff that
  describes a different or additional file
- **THEN** the call is rejected and no file is modified

#### Scenario: A patch uses an unsupported format
- **WHEN** `apply_patch` is called with a `*** Begin Patch` envelope rather
  than a unified diff
- **THEN** the call is rejected with an error naming the expected unified-diff
  format and no file is modified

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

### Requirement: machinome build and test tools
The tool set SHALL provide `machinome_build` and `machinome_test`, matching the
`machinome build` and `machinome test` CLI commands' arguments and exit semantics.

#### Scenario: Build failure is reported, not swallowed
- **WHEN** `machinome_build` is called against a project whose model fails to
  build
- **THEN** the tool reports nonzero/failed status and the failure detail,
  without publishing a broken model over a previous good one

### Requirement: machinome snapshot tool returns image content directly
The tool set SHALL provide `machinome_snapshot`, accepting the same rendering
options as the `machinome snapshot` CLI command, returning the rendered image as
direct tool output, and SHALL NOT leave any generated file inside the project
tree.

#### Scenario: Snapshot does not appear in git status
- **WHEN** `machinome_snapshot` is called against a project with a clean working
  tree
- **THEN** the tool returns the rendered image content, and `git_status`
  afterward still reports a clean working tree

#### Scenario: No output-path argument
- **WHEN** `machinome_snapshot` is called
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

### Requirement: OpenSpec tools

The tool set SHALL provide `openspec_setup` and `openspec_run`.

`openspec_setup` SHALL establish the active project's OpenSpec record: it
initializes the record when absent, seeds the project's house rules for writing
mechanical specs, and commits that result. Against a project whose record
already exists it SHALL report that and change nothing, including its house
rules.

`openspec_run` SHALL take an argument vector, invoke the `openspec` CLI with it
in the active project's root, and return the invocation's exit status and
output. It SHALL reject an argument vector naming a subcommand that reads or
writes OpenSpec state outside the active project, including any machine-level
store, global configuration, or telemetry subcommand, and SHALL reject a
`--store` argument.

#### Scenario: A change is created in a prepared project

- **WHEN** `openspec_run` is called to create a change in a project whose
  record `openspec_setup` established
- **THEN** the change is created inside that project and the call reports the
  CLI's status and output

#### Scenario: Setup runs a second time

- **WHEN** `openspec_setup` is called against a project whose record already
  exists
- **THEN** it reports the existing record, creates no commit, and leaves the
  project's house rules unchanged

#### Scenario: A subcommand reaches outside the project

- **WHEN** `openspec_run` is called with a store, global configuration, or
  telemetry subcommand, or with a `--store` argument
- **THEN** the call is rejected and no process is started

### Requirement: OpenSpec operations are confined to the active project

`openspec_run` SHALL verify, before starting any process, that the OpenSpec
root the CLI would resolve is the active project's root. When the resolved root
is any other directory, including an ancestor of the project, the call SHALL
fail naming the resolved root and SHALL NOT create, read, or modify anything.

#### Scenario: The project has no record of its own

- **WHEN** `openspec_run` is called in a project that has no OpenSpec record
  and whose parent directories do
- **THEN** the call fails naming the ancestor root it would otherwise have
  used, and that ancestor is not modified

#### Scenario: The resolved root is the project

- **WHEN** `openspec_run` is called in a project whose own OpenSpec record
  exists
- **THEN** the resolved root is that project and the call proceeds

### Requirement: A change does not close over unfinished work

`openspec_run` SHALL refuse to archive a change whose recorded tasks are not
all complete. The refusal SHALL name the incomplete tasks. The tool SHALL make
this determination itself rather than relying on the CLI's own prompt or
confirmation flag, and SHALL provide no argument that overrides it.

#### Scenario: Archiving with tasks outstanding

- **WHEN** `openspec_run` is called to archive a change with unchecked tasks
- **THEN** the call fails naming those tasks and the change is not archived

#### Scenario: Archiving a completed change

- **WHEN** `openspec_run` is called to archive a change whose tasks are all
  complete
- **THEN** the change's specs are synced and the change is archived

### Requirement: Codex floor calls belong to their owning live role
A Codex role SHALL advertise and call exactly its resolved floor operations and skill loader. Every call SHALL be checked against the owning live project session, role and current delivery, its declared tool schema and its trusted lifecycle identity before a floor operation runs. Unknown, malformed, stale, cross-role and identity-spoofing calls SHALL fail without project or broker action. No call SHALL select its own execution root, broker endpoint, session or skill registry.

#### Scenario: A narrower role holds no write capability
- **WHEN** a Codex role without write capability attempts a write operation, even through an unadvertised call
- **THEN** no write operation runs and no project file changes

#### Scenario: A role spoofs another sender
- **WHEN** one Codex thread supplies another role as lifecycle sender or acknowledgement identity
- **THEN** the call fails before broker dispatch

#### Scenario: A stale callback outlives the session
- **WHEN** a callback names a closed session or no longer active delivery
- **THEN** no floor operation runs and no later session is reached

#### Scenario: A role requests another skill
- **WHEN** a Codex role asks its loader for a skill absent from its declared registry
- **THEN** the call fails without reading that skill

### Requirement: Codex receives floor images as usable tool output
Floor raster reads and snapshots SHALL provide image content directly to a Codex model through its tool result, preserving the existing project containment and no-snapshot-file behavior. A transport that cannot carry the declared result SHALL report that limitation rather than claiming a picture was viewed.

#### Scenario: A Codex role inspects a snapshot
- **WHEN** its declared snapshot operation succeeds
- **THEN** the model receives the resulting raster image directly and the operation leaves no snapshot file in the project tree

#### Scenario: A Codex role reads a raster
- **WHEN** its declared bounded raster read succeeds
- **THEN** the model receives the image as tool output rather than an inaccessible host path

