## MODIFIED Requirements

### Requirement: The orchestrator accepts a configurable agent backend
The shop orchestrator SHALL accept a `--backend` flag with values `codex`,
`claude`, and `opencode`. When omitted, the orchestrator SHALL use `codex` as
the default backend. An unknown backend value, including the retired `hermes`
value, SHALL cause the orchestrator to exit with an error before starting the
broker or any agent session.

#### Scenario: Codex backend is the default
- **WHEN** a maker opens the shop without specifying `--backend`
- **THEN** the orchestrator uses the Codex backend

#### Scenario: Claude backend is selected
- **WHEN** a maker opens the shop with `--backend claude`
- **THEN** the orchestrator uses the Claude backend

#### Scenario: OpenCode backend is selected
- **WHEN** a maker opens the shop with `--backend opencode`
- **THEN** the orchestrator uses the OpenCode backend

#### Scenario: Unknown or retired backend is rejected
- **WHEN** a maker opens the shop with `--backend unknown` or `--backend hermes`
- **THEN** the orchestrator exits with an error before starting any service or agent

### Requirement: The backend owns its agent sessions
The selected backend SHALL own the lifecycle of every standing agent session
declared by the selected profile. The orchestrator SHALL call `open_role()`
once per declared agent in profile order with that agent's resolved contract,
`deliver_start()` for an envelope addressed to an idle agent,
`deliver_steer()` for an envelope addressed to an active agent, `interrupt()`
on close or shutdown, and `close_role()` to release the session. The backend
SHALL translate native events into portable `BackendEvent` instances.

A backend MAY own one process per agent session rather than one process for all
agents. Process cardinality SHALL NOT change ownership: it SHALL release every
process it starts. Unexpected exit of one process in a per-agent backend SHALL
be a failure of that agent; backend failure is reserved for a fault that ends
the run.

Interrupting an agent SHALL be reserved for closing or shutting down. A backend
whose native interrupt spends a session SHALL NOT return it to standby.

#### Scenario: Backend creates Builder profile sessions
- **WHEN** the orchestrator opens the `builder` profile
- **THEN** the backend receives one `open_role()` call carrying Builder's resolved profile contract

#### Scenario: Backend creates Fordesmac profile sessions
- **WHEN** the orchestrator opens the `fordesmac` profile
- **THEN** the backend receives `open_role()` for Foreman, Designer, Machinist, and Librarian in profile declaration order

#### Scenario: Backend delivers an envelope
- **WHEN** the broker emits an envelope addressed to an idle declared agent
- **THEN** the orchestrator calls `backend.deliver_start()` for that agent with the envelope body

#### Scenario: Backend reports a role message
- **WHEN** an agent session publishes a message
- **THEN** the backend emits a `role_message` event with that stable profile agent ID

#### Scenario: Backend fails during an agent operation
- **WHEN** a backend role-open or delivery call raises an error
- **THEN** the orchestrator unwinds partial state and reports the failure

#### Scenario: A partially opened multi-process backend releases what it started
- **WHEN** a per-agent backend fails while opening a later profile agent
- **THEN** it releases every process it already started before reporting failure

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
backend-specific profile parsing. A backend SHALL own translation of resolved
profile controls when the profile declares controls for that backend. OpenCode
SHALL instead use the bounded adapter-owned compatibility policy defined below.

#### Scenario: Orchestrator code references no backend identifiers or role adapters
- **WHEN** the profile runtime is implemented
- **THEN** `floor/orchestrator.py` contains no Codex, Claude, or OpenCode wire identifier and no global backend role-adapter lookup

#### Scenario: Backends receive one resolved role interpretation
- **WHEN** a profile agent is opened through any backend
- **THEN** the backend receives the same validated prompt and skill paths, stable identity, and labels from the profile loader

#### Scenario: OpenCode does not add a profile policy lookup
- **WHEN** a validated existing profile is opened through OpenCode
- **THEN** the adapter applies its compatibility policy without requiring or reading an OpenCode table in that profile

## REMOVED Requirements

### Requirement: The Hermes backend operates a real acp subprocess
**Reason**: Hermes is retired as an agent backend because its tool class and
undocumented ACP behavior do not justify the integration's maintenance cost.

**Migration**: Select Codex or Claude for profile-explicit execution, or
OpenCode for the shop's multi-provider path.

### Requirement: Hermes backend translates ACP events into portable events
**Reason**: The Hermes ACP adapter and its event translation are removed with
the backend.

**Migration**: Use one of the remaining supported backends, all of which emit
the same portable `BackendEvent` contract.
