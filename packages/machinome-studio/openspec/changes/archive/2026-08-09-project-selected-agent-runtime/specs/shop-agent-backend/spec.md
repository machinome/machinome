## REMOVED Requirements

### Requirement: The orchestrator accepts a configurable agent backend
**Reason**: Backend selection is no longer an invocation choice. It is a
property of the project, declared per agent in `[tool.solid-node-studio]` and
specified by the `project-runtime-selection` capability. A single run-wide
backend value cannot express the per-agent selection that capability requires.

**Migration**: Remove `--backend <name>` from every launcher invocation, script,
and document. Declare the equivalent selection in the project's
`pyproject.toml`: `--backend codex` becomes `<agent> = "codex:<model>"` per
agent, or nothing at all, since Codex with the profile-declared model is the
fallback for any agent a project does not name. `--backend claude` and
`--backend opencode` become `claude:<model>` and
`opencode:<provider>:<model>` selections for the agents that should use them.

## MODIFIED Requirements

### Requirement: The backend owns its agent sessions
Each standing agent SHALL be owned by the backend its resolved runtime selects.
A run MAY therefore have several backends open at once, and the orchestrator
SHALL open each distinct selected backend exactly once and close each exactly
once regardless of how many agents it owns. The orchestrator SHALL call
`open_role()` once per declared agent in profile order, on that agent's own
backend, with that agent's resolved contract; `deliver_start()` for an envelope
addressed to an idle agent; `deliver_steer()` for an envelope addressed to an
active agent; `interrupt()` on close or shutdown; and `close_role()` to release
the session. Every backend SHALL translate native events into portable
`BackendEvent` instances, and the orchestrator SHALL consume every open
backend's event stream concurrently.

A backend MAY own one process per agent session rather than one process for all
agents. Process cardinality SHALL NOT change ownership: it SHALL release every
process it starts. Unexpected exit of one process in a per-agent backend SHALL
be a failure of that agent; backend failure is reserved for a fault that ends
the run.

Interrupting an agent SHALL be reserved for closing or shutting down. A backend
whose native interrupt spends a session SHALL NOT return it to standby.

#### Scenario: Backend creates Builder profile sessions
- **WHEN** the orchestrator opens the `builder` profile
- **THEN** Builder's selected backend receives one `open_role()` call carrying Builder's resolved profile contract

#### Scenario: Backend creates Fordesmac profile sessions
- **WHEN** the orchestrator opens the `fordesmac` profile with every agent on one backend
- **THEN** that backend receives `open_role()` for Foreman, Designer, Machinist, and Librarian in profile declaration order

#### Scenario: A run opens several backends
- **WHEN** the resolved runtime selects two different backends across a profile's agents
- **THEN** each backend is instantiated once, receives `open_role()` only for the agents it owns, and has its event stream consumed alongside the other's

#### Scenario: A backend owning several agents is closed once
- **WHEN** the shop closes a run in which one backend owns three agents
- **THEN** each of those agent sessions is released and that backend is closed exactly once

#### Scenario: Backend delivers an envelope
- **WHEN** the broker emits an envelope addressed to an idle declared agent
- **THEN** the orchestrator calls `deliver_start()` on that agent's own backend with the envelope body

#### Scenario: Backend reports a role message
- **WHEN** an agent session publishes a message
- **THEN** its backend emits a `role_message` event with that stable profile agent ID

#### Scenario: Backend fails during an agent operation
- **WHEN** a backend role-open or delivery call raises an error
- **THEN** the orchestrator unwinds partial state and reports the failure

#### Scenario: A partially opened multi-process backend releases what it started
- **WHEN** opening fails on a later profile agent
- **THEN** every backend already started releases every process and session it opened before the failure is reported

#### Scenario: One role process exiting is a role failure
- **WHEN** a per-agent backend observes one declared agent process exit unexpectedly
- **THEN** it emits `role_failed` for that agent rather than `backend_failed`

#### Scenario: An interrupted role is not returned to standby
- **WHEN** the orchestrator interrupts an active agent while closing the shop
- **THEN** it delivers no further envelopes to that agent and does not report it waiting

#### Scenario: Every backend is independently testable
- **WHEN** fake Codex, Claude, or OpenCode fixtures are selected
- **THEN** each fixture opens and exercises every agent in either initial profile through the same portable backend operations

### Requirement: The orchestrator is backend-neutral
The orchestrator SHALL depend only on the portable `AgentBackend` protocol and
resolved profile/agent data. It SHALL NOT reference any backend-native
identifier, wire format, session handle, global role adapter path, or
backend-specific profile parsing. Routing an agent to its owning backend SHALL
use the resolved runtime alone and SHALL NOT branch on a backend name. A backend
SHALL own translation of the resolved runtime it is given.

#### Scenario: Orchestrator code references no backend identifiers or role adapters
- **WHEN** the profile runtime is implemented
- **THEN** `floor/orchestrator.py` contains no Codex, Claude, or OpenCode wire identifier and no global backend role-adapter lookup

#### Scenario: Agents are routed without backend branching
- **WHEN** the orchestrator delivers to an agent in a run with several open backends
- **THEN** it selects that agent's backend from resolved runtime data rather than testing which backend name it is

#### Scenario: Backends receive one resolved role interpretation
- **WHEN** a profile agent is opened through any backend
- **THEN** the backend receives the same validated prompt and skill paths, stable identity, and labels from the profile loader

#### Scenario: OpenCode does not add a profile policy lookup
- **WHEN** a validated existing profile is opened through OpenCode
- **THEN** the adapter applies its compatibility policy without requiring or reading an OpenCode table in that profile

### Requirement: OpenCode uses bounded adapter-owned compatibility defaults
The OpenCode adapter SHALL NOT require or read OpenCode declarations from a
profile manifest, and profiles SHALL remain valid without one. When the active
project selects an OpenCode provider and model for an agent, the adapter SHALL
apply exactly that provider and model to that agent's sessions. When the project
selects no OpenCode provider and model, the adapter SHALL inherit the
authenticated operator model, variant, and configuration and SHALL own temporary
compatibility defaults for model/variant/tool handling. Effort, tool, and
permission handling SHALL remain adapter-owned in both cases.

The adapter SHALL generate one primary OpenCode agent shared by its persistent
role sessions and SHALL apply a deny-by-default permission policy. Every
delivery SHALL carry the target role's exact profile prompt and the exact
instructions of each profile-allowlisted skill as system context. The adapter
SHALL explicitly admit required shop tool classes while denying native
subagents, interactive questions, external directories, and native skill
discovery. This bounded exception to profile-explicit runtime policy SHALL NOT
be represented as equivalent control across backends.

#### Scenario: A project selects an OpenCode provider and model
- **WHEN** a project declares `opencode:<provider>:<model>` for an agent
- **THEN** that agent's OpenCode sessions use exactly that provider and model rather than the operator default

#### Scenario: Existing profile selects OpenCode
- **WHEN** Builder or Fordesmac opens an agent on OpenCode and the project names no provider and model
- **THEN** profile validation succeeds without an OpenCode table and the adapter supplies the compatibility defaults

#### Scenario: A role agent is generated
- **WHEN** OpenCode starts and later opens resolved profile roles
- **THEN** one generated primary agent serves their persistent sessions and each role delivery carries that role's exact profile prompt and exact allowlisted skill instructions

#### Scenario: OpenCode permissions are established
- **WHEN** the adapter generates its OpenCode agent
- **THEN** it applies deny-by-default permissions with only required shop tool classes admitted and reads no permission declarations from the profile manifest

#### Scenario: Operator runtime choices are inherited
- **WHEN** the generated role starts without a project-selected provider and model and without adapter-selected concrete values
- **THEN** OpenCode uses the authenticated operator model, variant, and configuration
