## ADDED Requirements

### Requirement: The orchestrator accepts a configurable agent backend
The shop orchestrator SHALL accept a `--backend` flag with values `codex` and
`hermes`. When omitted, the orchestrator SHALL use `codex` as the default
backend. An unknown backend value SHALL cause the orchestrator to exit with an
error before starting the broker or any agent session.

#### Scenario: Codex backend is the default
- **WHEN** a maker opens the shop without specifying `--backend`
- **THEN** the orchestrator uses the Codex backend

#### Scenario: Hermes backend is selected
- **WHEN** a maker opens the shop with `--backend hermes`
- **THEN** the orchestrator uses the Hermes backend

#### Scenario: Unknown backend is rejected
- **WHEN** a maker opens the shop with `--backend unknown`
- **THEN** the orchestrator exits with an error before starting any service or agent

### Requirement: The backend owns its agent sessions
The selected backend SHALL own the lifecycle of every role session it creates.
The orchestrator SHALL call `open_role()` once per role at shop open,
`deliver_start()` for an envelope addressed to an idle role, `deliver_steer()`
for an envelope addressed to an active role, `interrupt()` on shop close or
shutdown, and `close_role()` to release the session. The backend
SHALL translate its native protocol events into portable `BackendEvent`
instances consumed by the orchestrator.

#### Scenario: Backend creates a role session
- **WHEN** the orchestrator opens the shop
- **THEN** the backend receives `open_role()` for foreman, designer, and machinist in order

#### Scenario: Backend delivers an envelope
- **WHEN** the broker emits an envelope addressed to an idle role
- **THEN** the orchestrator calls `backend.deliver_start()` for that role with the envelope body

#### Scenario: Backend reports a role message
- **WHEN** an agent session publishes a message to the maker conversation
- **THEN** the backend emits a `role_message` event consumed by the orchestrator

#### Scenario: Backend fails during a role operation
- **WHEN** a backend role-open or delivery call raises an error
- **THEN** the orchestrator unwinds partial state and reports the failure

### Requirement: The orchestrator is backend-neutral
The shop orchestrator SHALL depend only on the `AgentBackend` protocol. It
SHALL NOT reference, import, or depend on any backend-specific identifier,
wire format, configuration path, or session handle. Backend-specific
configuration SHALL be owned by the backend implementation, not by the
orchestrator or broker.

#### Scenario: Orchestrator code references no backend identifiers
- **WHEN** the Codex backend is extracted to `floor/backends/codex.py`
- **THEN** `floor/orchestrator.py` contains no reference to `threadId`, `turnId`, `turn/steer`, `app-server`, Codex-specific JSON-RPC methods, or `.codex/agents/*.toml`

#### Scenario: Hermes backend is independently testable
- **WHEN** a fake ACP server fixture is provided
- **THEN** the orchestrator exercises the Hermes backend through the same `AgentBackend` operations as the Codex backend
