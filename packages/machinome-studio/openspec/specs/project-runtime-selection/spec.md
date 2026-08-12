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

### Requirement: A project declares its default runtime profile
The `[tool.solid-node-studio]` table SHALL admit a `profile` key whose value is a
string naming a runtime profile. That value SHALL select the profile for every
session of that project.

A value that is not a well-formed lowercase kebab-case profile ID SHALL be
rejected whenever that project is read, because it cannot name a profile. A
well-formed value that does not resolve to a profile beneath the shop's
`profiles/` directory SHALL be rejected when that project is opened, and the
session SHALL NOT fall back to the default profile. Every such rejection SHALL
identify the project file and the offending value, and SHALL leave the shop and
every other project available.

A project that declares no `profile` key, no `[tool.solid-node-studio]` table, or
no `pyproject.toml` at all SHALL be opened under the shop default.

Creating a project SHALL write the `profile` key the maker chose for it, so a
project created by the shop declares its profile from its first state.

#### Scenario: A project declares its profile
- **WHEN** a project's `pyproject.toml` declares `profile = "fordesmac"` and it is opened
- **THEN** the session opens the `fordesmac` roster

#### Scenario: A project declares no profile
- **WHEN** a project declares no `profile` key and it is opened
- **THEN** the session opens the shop default profile

#### Scenario: A malformed profile value is always rejected
- **WHEN** a project's `profile` value is not lowercase kebab-case, such as a path or a value containing a separator
- **THEN** the shop refuses to open that project, naming the project file and the value, before any project or backend side effect, and remains available for every other project

#### Scenario: An unresolvable declared profile is rejected rather than replaced
- **WHEN** a project declares a well-formed profile that no `profiles/<profile-id>/profile.toml` provides
- **THEN** the shop refuses to open that project, naming the project file and the value, rather than opening the default profile

#### Scenario: A created project declares its chosen profile
- **WHEN** the maker creates a project and chooses a profile for it
- **THEN** the created project's `pyproject.toml` declares that profile, and opening it again later uses that declaration without the maker choosing again

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
SHALL be ignored rather than rejected, because a project's declared profile may
change over its life while selections for its former roster remain in the file.
The shop SHALL report every key it ignored so a misspelled agent ID is visible
rather than silently inert. An agent key that is not a well-formed lowercase
kebab-case agent ID SHALL be rejected.

#### Scenario: A project carries selections for two rosters
- **WHEN** a project declares selections for both `builder` and the Fordesmac specialists and declares the profile `builder`
- **THEN** the Builder selection applies, the Fordesmac keys are ignored, and the ignored keys are reported

#### Scenario: A project changes its declared profile
- **WHEN** a project that declared `fordesmac` with selections for its specialists is changed to declare `builder` and is opened
- **THEN** the session opens `builder`, the specialist keys are ignored rather than rejected, and they are reported

#### Scenario: An agent ID is misspelled
- **WHEN** a project declares a selection for an agent key absent from the active roster
- **THEN** the session opens without applying it and reports that the key was ignored

#### Scenario: An agent key is malformed
- **WHEN** an agent key is not lowercase kebab-case
- **THEN** the shop refuses to open that project before any project or backend side effect

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
continue to resolve from the active profile alone. Declaring a `profile` key
SHALL select one repository-owned profile package in its entirety and SHALL NOT
make any policy that package carries project-authored: a project SHALL NOT
select, widen, narrow, or otherwise state tool or permission policy
independently of the profile it names. A `[tool.solid-node-studio]` table SHALL
reject keys other than those this capability defines rather than ignoring them,
so a reasoning level SHALL be selectable only as a segment of an agent's runtime
value and never as a key of its own.

#### Scenario: A project attempts to widen tool policy
- **WHEN** a project's runtime table declares a tool or permission key
- **THEN** the run exits with an error identifying the unsupported key

#### Scenario: A reasoning level is declared as a separate key
- **WHEN** a project's runtime table declares an `effort` key beside an agent's runtime value
- **THEN** the run exits with an error identifying the unsupported key

#### Scenario: A selected model keeps profile tools and permission
- **WHEN** a project selects a Claude model and reasoning level for an agent
- **THEN** the agent opens with the project's model and reasoning level and the profile's tool policy and permission

#### Scenario: A declared profile carries its own policy unchanged
- **WHEN** a project declares a profile and the run opens under it
- **THEN** every agent resolves the tool and permission policy that profile declares, unmodified by anything else in the project file

### Requirement: An idle session may override its selected model and reasoning
The maker MAY replace one manifested agent's model and reasoning level for its
current session when the agent is authoritatively idle. When its backend and
provider remain unchanged, the shop SHALL apply both values as one validated
runtime value to the existing persistent session only when that backend proves
the change preserves context. Before the role has accepted any message,
delivery, or assignment or produced any activity, the maker MAY instead select
a different backend or provider together with its model and reasoning; the shop
SHALL immediately replace that unused standing session without migrating
context. First use SHALL permanently end backend/provider replacement for that
role even after it becomes idle again. The shop SHALL NOT offer a queued or
next-assignment runtime mode.

#### Scenario: An idle Codex agent changes model
- **WHEN** the maker applies a supported Codex model and reasoning level to an idle Codex agent
- **THEN** that agent's next turn uses both new values in its existing persistent thread

#### Scenario: An idle OpenCode agent changes model
- **WHEN** the maker applies a model and variant from the current OpenCode provider's catalogue to an idle OpenCode agent
- **THEN** that agent's next prompt uses both new values in its existing persistent session

#### Scenario: A pristine role changes backend
- **WHEN** the maker applies a supported backend, provider, model, and reasoning combination before the role has accepted a message, delivery, or assignment or produced activity
- **THEN** the shop closes the unused standing handle, immediately opens that role on the selected runtime, and migrates no session context

#### Scenario: A pristine role selects OpenCode
- **WHEN** the maker selects OpenCode for a pristine role
- **THEN** provider, model, and reasoning choices are limited to combinations in OpenCode's live catalogue

#### Scenario: A used role becomes idle again
- **WHEN** a role has accepted a message, delivery, or assignment or produced activity and later returns to an idle state
- **THEN** the shop rejects a backend or provider change without changing live or project runtime

#### Scenario: A pristine Claude role changes model
- **WHEN** the maker applies a supported Claude model and reasoning level before that role's first use
- **THEN** the shop replaces the unused Claude process and applies the selection immediately

#### Scenario: A used Claude session cannot preserve context
- **WHEN** a used Claude role is idle and the maker requests a model change
- **THEN** the workspace displays its runtime read-only and the API rejects mutation

### Requirement: Runtime controls expose provider before model
The Agents workspace SHALL present runtime selection in the order backend,
provider, model, and reasoning level. The provider control SHALL identify the
provider independently of the model control. Codex SHALL show `OpenAI` as its
single fixed provider, Claude SHALL show `Anthropic` as its single fixed
provider, and OpenCode SHALL show only the exact provider IDs in the live
endpoint's connected provider set. The shop SHALL NOT expose entries that exist
only in OpenCode's complete known-provider catalogue.

Changing a backend SHALL replace provider, model, and reasoning drafts with a
valid combination for that backend. Changing an OpenCode provider SHALL replace
the model and reasoning drafts with a valid combination for that provider. The
model control SHALL contain only models for the selected backend and provider.

The workspace SHALL NOT present profile-owned tools as a runtime-selection
control. Removing that presentation SHALL NOT make tool policy project- or
maker-selectable.

#### Scenario: A maker inspects a fixed-provider backend
- **WHEN** the maker selects the Codex or Claude backend
- **THEN** the provider control shows its single fixed OpenAI or Anthropic provider before the model control

#### Scenario: A maker selects an OpenCode provider
- **WHEN** a pristine agent's live OpenCode catalogue contains more than one connected provider and the maker selects one provider ID
- **THEN** the model control contains only models belonging to that exact connected provider ID

#### Scenario: OpenCode knows providers that are not configured
- **WHEN** OpenCode's live endpoint lists providers in its complete catalogue that are absent from its connected provider set
- **THEN** the provider control omits those unconnected providers and all of their models

#### Scenario: OpenCode has no configured provider
- **WHEN** OpenCode's live endpoint reports no connected providers
- **THEN** the OpenCode runtime catalogue is unavailable rather than exposing the complete known-provider catalogue

#### Scenario: An upstream selection changes
- **WHEN** the maker changes backend or OpenCode provider and the previous model or reasoning value is unavailable downstream
- **THEN** the workspace immediately selects a valid downstream model and reasoning combination

#### Scenario: A maker applies an OpenCode runtime
- **WHEN** the maker applies an OpenCode provider, model, and reasoning selection
- **THEN** the complete runtime mutation names the exact selected provider ID separately from its model ID

#### Scenario: Runtime tools are not presented as a choice
- **WHEN** the maker opens an agent's runtime controls
- **THEN** backend, provider, model, reasoning, and persistence are presented without a tools control

### Requirement: A live runtime update may be recorded in project configuration
The runtime control SHALL default to writing an accepted change to the active
project's `[tool.solid-node-studio.agents]` table and SHALL let the maker
explicitly uncheck that option for a session-only override. A persisted change
SHALL write the complete selected backend/provider/model/reasoning value using
the accepted grammar, preserve unrelated TOML content and comments, and
atomically replace only an unchanged configuration revision. The shop SHALL NOT
read or write `[tool.solid-node]`.

#### Scenario: The default persisted update succeeds
- **WHEN** the maker applies an idle runtime update with the default persistence option
- **THEN** the live session changes immediately and the project agent key records the same complete selection in `pyproject.toml`

#### Scenario: The maker chooses a temporary override
- **WHEN** the maker unchecks persistence and applies an idle runtime update
- **THEN** the live session changes and reopening the project again resolves from the unchanged `pyproject.toml`

#### Scenario: Project configuration changed concurrently
- **WHEN** `pyproject.toml` no longer has the revision displayed with the controls
- **THEN** the shop rejects the update without overwriting the file or changing the live runtime

#### Scenario: Project and framework tables coexist
- **WHEN** persisted runtime is written beside an existing `[tool.solid-node]` table and other project configuration
- **THEN** only the selected `[tool.solid-node-studio.agents]` key changes and all unrelated content remains semantically and textually preserved
