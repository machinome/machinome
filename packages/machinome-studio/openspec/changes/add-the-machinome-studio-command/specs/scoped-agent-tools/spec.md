## MODIFIED Requirements

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
