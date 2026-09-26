## MODIFIED Requirements

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
The shop SHALL treat the caller-supplied `--projects-dir` as the exact and sole
project catalogue, SHALL load trusted shop resources from the running shop
package or source worktree, SHALL invoke the machinome CLI installed in the
same Python environment as the running shop, and SHALL NOT require or discover
a Git checkout to start the hub or its backend processes.

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

## ADDED Requirements

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
