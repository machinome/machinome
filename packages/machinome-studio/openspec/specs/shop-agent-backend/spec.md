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
`deliver()` for each envelope addressed to that role, `interrupt()` on shop
close or shutdown, and `close_role()` to release the session. The backend
SHALL translate its native protocol events into portable `BackendEvent`
instances consumed by the orchestrator. The Hermes backend SHALL operate a
real `hermes acp` subprocess rather than raising `NotImplementedError`.

#### Scenario: Backend creates a role session
- **WHEN** the orchestrator opens the shop
- **THEN** the backend receives `open_role()` for foreman, designer, and machinist in order

#### Scenario: Backend delivers an envelope
- **WHEN** the broker emits an envelope addressed to an idle role
- **THEN** the orchestrator calls `backend.deliver()` for that role with the envelope body

#### Scenario: Backend reports a role message
- **WHEN** an agent session publishes a message to the maker conversation
- **THEN** the backend emits a `role_message` event consumed by the orchestrator

#### Scenario: Backend fails during a role operation
- **WHEN** a backend `open_role()` or `deliver()` call raises an error
- **THEN** the orchestrator unwinds partial state and reports the failure

#### Scenario: Hermes backend is independently testable against a fake ACP fixture
- **WHEN** a fake ACP server fixture is provided as the `hermes acp` command
- **THEN** the orchestrator exercises the Hermes backend through the same `AgentBackend` operations as the Codex backend and all operations succeed without `NotImplementedError`

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

### Requirement: The Hermes backend operates a real acp subprocess
The Hermes backend SHALL launch `hermes acp` as a subprocess during `start()`.
It SHALL complete ACP `initialize` handshake before returning. It SHALL speak
the ACP JSON-RPC protocol (newline-delimited JSON over stdio) using the same
request/response and notification plumbing as the Codex backend.

#### Scenario: Hermes backend starts the acp process
- **WHEN** the orchestrator opens the shop with `--backend hermes`
- **THEN** the Hermes backend launches `hermes acp` as a subprocess and completes the `initialize` handshake

#### Scenario: Hermes backend creates role sessions
- **WHEN** `open_role("designer", context)` is called
- **THEN** the backend sends ACP `session/new` with `cwd` set to the active project and injects role context via an initial `session/prompt`

#### Scenario: Hermes backend delivers messages
- **WHEN** `deliver_start(handle, message)` is called on an idle session
- **THEN** the backend sends `session/prompt` with the message as a text content block and returns an accepted `DeliveryReceipt`

#### Scenario: Hermes backend steers active turns
- **WHEN** `deliver_steer(handle, expected_id, message)` is called on an active session
- **THEN** the backend cancels the current prompt via `session/cancel` and sends a new `session/prompt` with the correction
- **AND IF** the active prompt already completed, the backend raises `InactiveTurn`

#### Scenario: Hermes backend interrupts sessions
- **WHEN** `interrupt(handle)` is called
- **THEN** the backend sends `session/cancel` notification

### Requirement: Hermes backend translates ACP events into portable events
The Hermes backend SHALL consume ACP `session/update` notifications and
`session/prompt` responses from the subprocess and translate them into
`BackendEvent` instances consumed by the orchestrator.

#### Scenario: Foreman agent message is published to conversation
- **WHEN** the ACP subprocess emits a `session/update` notification with `agentMessage` text for the foreman session
- **THEN** the backend emits a `BackendEvent(kind="role_message", role="foreman", text=...)`

#### Scenario: Turn start is tracked
- **WHEN** a `session/prompt` request is dispatched to the subprocess
- **THEN** the backend emits a `BackendEvent(kind="turn_started", role=..., delivery_id=...)`

#### Scenario: Turn completion is tracked
- **WHEN** a `session/prompt` response with `stopReason` is received from the subprocess
- **THEN** the backend emits a `BackendEvent(kind="turn_completed", role=..., delivery_id=...)`

#### Scenario: Backend process failure is reported
- **WHEN** the `hermes acp` subprocess exits unexpectedly
- **THEN** the backend emits a `BackendEvent(kind="backend_failed", error=...)`
