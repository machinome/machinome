## MODIFIED Requirements

### Requirement: Backend, provider, model, and reasoning level are one inseparable per-agent value
A runtime selection SHALL be a single string naming a backend, a provider where
the backend has more than one, a model, and an optional reasoning level, in that
order, separated by `:`. A backend with one provider SHALL be written
`backend:model`; a backend with several providers SHALL be written
`backend:provider:model`. Either form MAY carry a reasoning level as a final
segment. Claude SHALL take the single-provider form and OpenCode SHALL take the
multi-provider form, so the backend named in the first segment SHALL determine
how the remaining segments are read. The parts SHALL NOT be declarable
separately, in separate tables, or in separate files.

Selections SHALL be declared per agent under
`[tool.solid-node-studio.agents]`, keyed by profile agent ID. Different agents
in one run MAY name different backends.

A value SHALL be rejected when it names an unknown or retired backend, carries a
segment count the named backend does not admit, names a Claude model outside
that backend's supported set, names a reasoning level outside the set that
backend supports, names a reasoning level for a backend that cannot enforce one,
or leaves any segment empty. Rejection SHALL identify the offending agent key
and value.

#### Scenario: A single-provider selection is resolved
- **WHEN** an agent is declared as `claude:sonnet`
- **THEN** that agent opens on the Claude backend with model `sonnet` and its profile-declared effort

#### Scenario: A multi-provider selection is resolved
- **WHEN** an agent is declared as `opencode:anthropic:claude-sonnet-4-5`
- **THEN** that agent opens on the OpenCode backend with provider `anthropic` and model `claude-sonnet-4-5`

#### Scenario: A reasoning level is selected
- **WHEN** an agent is declared as `claude:sonnet:high`
- **THEN** that agent opens on the Claude backend with model `sonnet` and reasoning level `high`, overriding the profile's declared effort

#### Scenario: A reasoning level is selected alongside a provider
- **WHEN** an agent is declared as `opencode:anthropic:claude-sonnet-4-5:medium`
- **THEN** that agent opens with provider `anthropic`, model `claude-sonnet-4-5`, and reasoning level `medium`

#### Scenario: One run mixes backends
- **WHEN** a project declares one agent on Claude and another on OpenCode
- **THEN** both agents open on their own selected backend within the same run

#### Scenario: A malformed selection is rejected
- **WHEN** a selection names an unknown backend, carries more or fewer segments than the named backend admits, or leaves a segment empty
- **THEN** the run exits with an error naming that agent key and value before any project or backend side effect

#### Scenario: A retired backend is rejected
- **WHEN** a selection names the retired `codex` backend
- **THEN** the run exits with an error naming that agent key and value rather than substituting another backend

#### Scenario: An unsupported concrete model is rejected
- **WHEN** a Claude selection names a model outside that backend's supported set
- **THEN** the run exits with an error rather than passing the value to the backend

#### Scenario: An unsupported reasoning level is rejected
- **WHEN** a selection names a reasoning level outside the set its backend supports
- **THEN** the run exits with an error rather than passing the value to the backend

#### Scenario: A reasoning level is named for a backend that cannot enforce one
- **WHEN** a selection names a reasoning level for a backend with no enforceable reasoning control
- **THEN** the run exits with an error rather than accepting the value and ignoring it

### Requirement: Runtime controls expose provider before model
The Agents workspace SHALL present runtime selection in the order backend,
provider, model, and reasoning level. The provider control SHALL identify the
provider independently of the model control. Claude SHALL show `Anthropic` as
its single fixed provider, and OpenCode SHALL show only the exact provider IDs
in the live endpoint's connected provider set. The shop SHALL NOT expose entries
that exist only in OpenCode's complete known-provider catalogue, and SHALL NOT
offer a retired backend as a choice.

Changing a backend SHALL replace provider, model, and reasoning drafts with a
valid combination for that backend. Changing an OpenCode provider SHALL replace
the model and reasoning drafts with a valid combination for that provider. The
model control SHALL contain only models for the selected backend and provider.

The workspace SHALL NOT present profile-owned tools as a runtime-selection
control. Removing that presentation SHALL NOT make tool policy project- or
maker-selectable.

#### Scenario: A maker inspects a fixed-provider backend
- **WHEN** the maker selects the Claude backend
- **THEN** the provider control shows its single fixed Anthropic provider before the model control

#### Scenario: The backend control offers only selectable backends
- **WHEN** the maker opens an agent's runtime controls
- **THEN** the backend control offers Claude and OpenCode and does not offer the retired Codex backend

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

### Requirement: Unselected agents fall back to Claude and profile defaults
An agent the project does not name SHALL open on the Claude backend with the
model and effort its active profile declares for Claude. An agent whose
selection omits the reasoning level SHALL keep its profile-declared effort. A
project with no `[tool.solid-node-studio]` table, no `agents` table, or no
`pyproject.toml` at all SHALL open every agent that way. A project that does not
exist yet SHALL be treated as declaring nothing, and scaffolding a new project
SHALL NOT write a runtime selection.

#### Scenario: An agent is not named
- **WHEN** a project names some agents but not others
- **THEN** the unnamed agents open on Claude with their profile-declared Claude model and effort, and the named agents keep their selections

#### Scenario: A selection omits the reasoning level
- **WHEN** an agent's selection names a backend and model but no reasoning level
- **THEN** that agent opens with the selected model and its profile-declared effort

#### Scenario: A project declares nothing
- **WHEN** a project has no `[tool.solid-node-studio]` table
- **THEN** every agent opens on Claude with its profile-declared Claude model and effort

#### Scenario: A project does not exist yet
- **WHEN** the shop opens for a named project that must first be scaffolded
- **THEN** every agent opens on Claude with its profile-declared Claude model and effort, and the scaffold contains no runtime selection

## RENAMED Requirements

- FROM: `### Requirement: Unselected agents fall back to Codex and profile defaults`
- TO: `### Requirement: Unselected agents fall back to Claude and profile defaults`
