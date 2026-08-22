## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: Runtime location independence
The shop SHALL treat the caller-supplied `--projects-dir` as the exact and sole
project catalogue, SHALL load trusted shop resources from the running shop
package or source worktree, SHALL invoke the solid-node CLI installed in the
same Python environment as the running shop, and SHALL NOT require or discover
a Git checkout to start the hub or its backend processes.

The shop SHALL depend on exactly one ambient `PATH` executable, the `openspec`
CLI, and SHALL name it as an installation prerequisite. No other shop or
backend behavior SHALL require or discover an ambient `PATH` executable.

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

#### Scenario: The OpenSpec CLI comes from the ambient environment
- **WHEN** the shop resolves the `openspec` CLI
- **THEN** it uses the executable on the ambient `PATH`, which is the only
  ambient executable the shop depends on
