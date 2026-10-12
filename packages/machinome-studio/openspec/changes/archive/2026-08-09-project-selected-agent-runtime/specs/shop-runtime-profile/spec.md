## MODIFIED Requirements

### Requirement: Backend runtime choices are explicit per agent
Each profile agent SHALL declare a model, effort, and tool policy for Codex and
Claude. These SHALL be defaults: they supply the model and effort for any agent
whose active-project selection does not name one, and they supply tool policy
always. Each setting SHALL be either a value the backend can enforce or the
literal `inherit`. Each Claude runtime table SHALL additionally declare
`permission` as either `manual` or `autonomous`; Codex runtime tables SHALL NOT
declare that field.

The loader SHALL validate every declared backend table on every run rather than
only the table for one selected backend, because a run may open several
backends. Validation SHALL fail if an agent lacks a Codex or Claude entry, names
an unsupported concrete value, or requests a control that backend cannot
enforce. A backend MUST NOT silently substitute an inherited or differently
configured model, effort, tool, or Claude permission policy for a concrete
resolved declaration.

A profile SHALL NOT declare an OpenCode runtime table. OpenCode has no profile
default: an agent runs on OpenCode only when the active project selects it, and
its provider and model come from that selection or from the adapter's bounded
compatibility policy. A profile SHALL reject runtime tables for unsupported or
retired backends, including Hermes and OpenCode.

Every shipped Claude role SHALL explicitly declare `permission = "autonomous"`.

#### Scenario: A complete backend mapping is selected
- **WHEN** the Builder profile is loaded and the project selects no runtime for Builder
- **THEN** Builder opens on Codex with the model, effort, and tool policy that profile declares for Codex

#### Scenario: A project model overrides a profile default
- **WHEN** the active project selects a Claude model without a reasoning level for an agent whose profile declares a different Claude model
- **THEN** the agent opens with the project's model and the profile's effort, tool policy, and permission

#### Scenario: A project reasoning level overrides a profile default
- **WHEN** the active project selects a model and reasoning level for an agent whose profile declares a different effort
- **THEN** the agent opens with the project's model and reasoning level and the profile's tool policy and permission

#### Scenario: A Claude profile selects autonomous execution
- **WHEN** a shipped profile agent resolves to the Claude backend
- **THEN** it resolves its explicit `autonomous` permission policy along with its model, effort, and available tools

#### Scenario: Every declared table is validated
- **WHEN** a profile declares an unsupported Claude value and the run selects Codex for every agent
- **THEN** profile validation fails rather than passing because no agent resolved to Claude

#### Scenario: An OpenCode table is rejected
- **WHEN** a profile agent declares an OpenCode runtime table
- **THEN** profile validation rejects the unsupported backend key

#### Scenario: OpenCode uses adapter-owned compatibility policy
- **WHEN** the active project selects OpenCode for an agent
- **THEN** the profile is valid without an OpenCode runtime table and the adapter applies its bounded compatibility policy

#### Scenario: A retired backend table is rejected
- **WHEN** a profile agent declares a Hermes runtime table
- **THEN** profile validation rejects the unsupported backend key

#### Scenario: A concrete control cannot be enforced
- **WHEN** a backend cannot enforce a concrete model, effort, tool, or Claude permission value resolved for an agent
- **THEN** the runtime rejects that combination rather than silently inheriting

#### Scenario: A Claude permission policy is omitted or invalid
- **WHEN** a Claude runtime table omits `permission` or names a value other than `manual` or `autonomous`
- **THEN** profile validation fails before any project or runtime side effect

### Requirement: Profile validation precedes every project side effect
The launcher SHALL complete profile filesystem, schema, prompt, skill, topology,
and runtime-table validation before it creates or validates a project
repository, invokes `solid`, binds an HTTP listener, or starts an agent backend.

Because runtime selection lives in the project, the launcher SHALL first perform
a bounded, side-effect-free read of the project's `pyproject.toml`: resolving
and containment-checking the project path and parsing that one file. That read
SHALL NOT create, scaffold, initialize, modify, or build anything, and SHALL
tolerate a project that does not yet exist. Profile validation and runtime
resolution SHALL both complete before any project side effect follows. A
validation error SHALL identify the profile or project file and the invalid
field or path.

#### Scenario: An invalid profile is used with a missing project
- **WHEN** the selected profile is invalid and the named project does not exist
- **THEN** the runtime reports the profile error and does not scaffold or initialize the project

#### Scenario: Reading project configuration creates nothing
- **WHEN** the launcher reads runtime selection for a project that does not yet exist
- **THEN** no directory, repository, scaffold, or build is produced by that read and resolution falls back to the profile defaults

#### Scenario: An invalid runtime selection stops the run early
- **WHEN** a project's runtime selection is malformed and the named project exists
- **THEN** the runtime reports the offending project file and value and does not invoke `solid`, bind a listener, or start a backend
