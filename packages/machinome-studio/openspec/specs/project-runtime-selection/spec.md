# project-runtime-selection Specification

## Purpose
TBD - created by archiving change project-selected-agent-runtime. Update Purpose after archive.
## Requirements
### Requirement: A project declares its own agent runtime
The active project's `pyproject.toml` SHALL be the sole source of backend,
provider, and model selection for a shop run. The shop SHALL read that
selection from a `[tool.solid-node-studio]` table, which it owns exclusively;
it SHALL NOT read or write the framework's `[tool.solid-node]` table. Runtime
selection SHALL NOT be available as a launcher option, an environment variable,
or a profile declaration for a backend the profile does not default.

#### Scenario: A project selects runtime for its agents
- **WHEN** a project's `pyproject.toml` declares `[tool.solid-node-studio]` runtime selections and the shop opens for that project
- **THEN** each named agent opens on the backend, provider, and model that table names

#### Scenario: The framework table is left alone
- **WHEN** the shop reads a project's runtime selection
- **THEN** it reads only `[tool.solid-node-studio]` and neither reads nor modifies `[tool.solid-node]`

### Requirement: Backend, provider, model, and reasoning level are one inseparable per-agent value
A runtime selection SHALL be a single string naming a backend, a provider where
the backend has more than one, a model, and an optional reasoning level, in that
order, separated by `:`. A backend with one provider SHALL be written
`backend:model`; a backend with several providers SHALL be written
`backend:provider:model`. Either form MAY carry a reasoning level as a final
segment. Codex and Claude SHALL take the single-provider form and OpenCode SHALL
take the multi-provider form, so the backend named in the first segment SHALL
determine how the remaining segments are read. The parts SHALL NOT be declarable
separately, in separate tables, or in separate files.

Selections SHALL be declared per agent under
`[tool.solid-node-studio.agents]`, keyed by profile agent ID. Different agents
in one run MAY name different backends.

A value SHALL be rejected when it names an unknown backend, carries a segment
count the named backend does not admit, names a Codex or Claude model outside
that backend's supported set, names a reasoning level outside the set that
backend supports, names a reasoning level for a backend that cannot enforce one,
or leaves any segment empty. Rejection SHALL identify the offending agent key
and value.

#### Scenario: A single-provider selection is resolved
- **WHEN** an agent is declared as `codex:gpt-5.6-terra`
- **THEN** that agent opens on the Codex backend with model `gpt-5.6-terra` and its profile-declared effort

#### Scenario: A multi-provider selection is resolved
- **WHEN** an agent is declared as `opencode:anthropic:claude-sonnet-4-5`
- **THEN** that agent opens on the OpenCode backend with provider `anthropic` and model `claude-sonnet-4-5`

#### Scenario: A reasoning level is selected
- **WHEN** an agent is declared as `codex:gpt-5.6-terra:high`
- **THEN** that agent opens on the Codex backend with model `gpt-5.6-terra` and reasoning level `high`, overriding the profile's declared effort

#### Scenario: A reasoning level is selected alongside a provider
- **WHEN** an agent is declared as `opencode:anthropic:claude-sonnet-4-5:medium`
- **THEN** that agent opens with provider `anthropic`, model `claude-sonnet-4-5`, and reasoning level `medium`

#### Scenario: One run mixes backends
- **WHEN** a project declares one agent on Codex and another on OpenCode
- **THEN** both agents open on their own selected backend within the same run

#### Scenario: A malformed selection is rejected
- **WHEN** a selection names an unknown backend, carries more or fewer segments than the named backend admits, or leaves a segment empty
- **THEN** the run exits with an error naming that agent key and value before any project or backend side effect

#### Scenario: An unsupported concrete model is rejected
- **WHEN** a Codex or Claude selection names a model outside that backend's supported set
- **THEN** the run exits with an error rather than passing the value to the backend

#### Scenario: An unsupported reasoning level is rejected
- **WHEN** a selection names a reasoning level outside the set its backend supports
- **THEN** the run exits with an error rather than passing the value to the backend

#### Scenario: A reasoning level is named for a backend that cannot enforce one
- **WHEN** a selection names a reasoning level for a backend with no enforceable reasoning control
- **THEN** the run exits with an error rather than accepting the value and ignoring it

### Requirement: Unselected agents fall back to Codex and profile defaults
An agent the project does not name SHALL open on the Codex backend with the
model and effort its active profile declares for Codex. An agent whose selection
omits the reasoning level SHALL keep its profile-declared effort. A project with no
`[tool.solid-node-studio]` table, no `agents` table, or no `pyproject.toml` at
all SHALL open every agent that way. A project that does not exist yet SHALL be
treated as declaring nothing, and scaffolding a new project SHALL NOT write a
runtime selection.

#### Scenario: An agent is not named
- **WHEN** a project names some agents but not others
- **THEN** the unnamed agents open on Codex with their profile-declared Codex model and effort, and the named agents keep their selections

#### Scenario: A selection omits the reasoning level
- **WHEN** an agent's selection names a backend and model but no reasoning level
- **THEN** that agent opens with the selected model and its profile-declared effort

#### Scenario: A project declares nothing
- **WHEN** a project has no `[tool.solid-node-studio]` table
- **THEN** every agent opens on Codex with its profile-declared Codex model and effort

#### Scenario: A project does not exist yet
- **WHEN** the shop opens for a named project that must first be scaffolded
- **THEN** every agent opens on Codex with its profile-declared Codex model and effort, and the scaffold contains no runtime selection

### Requirement: Selections are resolved against the active profile roster
Resolution SHALL apply a selection only to an agent the active profile declares.
A syntactically valid selection keyed to an agent outside the active roster
SHALL be ignored rather than rejected, because one project may be opened under
several profiles with different rosters. The launcher SHALL report every key it
ignored so a misspelled agent ID is visible rather than silently inert. An agent
key that is not a well-formed lowercase kebab-case agent ID SHALL be rejected.

#### Scenario: A project carries selections for two rosters
- **WHEN** a project declares selections for both `builder` and the Fordesmac specialists and is opened under `builder`
- **THEN** the Builder selection applies, the Fordesmac keys are ignored, and the ignored keys are reported

#### Scenario: An agent ID is misspelled
- **WHEN** a project declares a selection for an agent key absent from the active roster
- **THEN** the run opens without applying it and reports that the key was ignored

#### Scenario: An agent key is malformed
- **WHEN** an agent key is not lowercase kebab-case
- **THEN** the run exits with an error before any project or backend side effect

### Requirement: Project configuration is trusted; project guidance text is not
Pilot-authored project configuration in `[tool.solid-node-studio]` SHALL be
trusted to select backend, provider, and model. Project guidance text, including
a project's root `AGENTS.md` carried as supplemental session instruction, SHALL
NOT redefine runtime selection, role identity, topology, authority, skills,
effort, tool permissions, or repository boundaries. A backend that states this
precedence to its role sessions SHALL state the distinction rather than
forbidding runtime selection outright.

#### Scenario: A project's guidance text names a model
- **WHEN** an active project's `AGENTS.md` instructs a role to use a different model
- **THEN** the role keeps the runtime resolved from configuration and profile, and the guidance does not change it

#### Scenario: The precedence contract is stated to a role
- **WHEN** a backend includes the supplemental-guidance precedence contract in a role's session instructions
- **THEN** that contract distinguishes pilot-authored configuration, which selects runtime, from project guidance text, which cannot

### Requirement: Tools and permission remain profile-owned
A project SHALL NOT select tool policy or Claude permission policy. Those SHALL
continue to resolve from the active profile alone. A `[tool.solid-node-studio]`
table SHALL reject keys other than those this capability defines rather than
ignoring them, so a reasoning level SHALL be selectable only as a segment of an
agent's runtime value and never as a key of its own.

#### Scenario: A project attempts to widen tool policy
- **WHEN** a project's runtime table declares a tool or permission key
- **THEN** the run exits with an error identifying the unsupported key

#### Scenario: A reasoning level is declared as a separate key
- **WHEN** a project's runtime table declares an `effort` key beside an agent's runtime value
- **THEN** the run exits with an error identifying the unsupported key

#### Scenario: A selected model keeps profile tools and permission
- **WHEN** a project selects a Claude model and reasoning level for an agent
- **THEN** the agent opens with the project's model and reasoning level and the profile's tool policy and permission

