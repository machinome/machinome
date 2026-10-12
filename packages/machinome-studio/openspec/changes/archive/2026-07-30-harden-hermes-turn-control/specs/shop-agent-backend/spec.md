## MODIFIED Requirements

### Requirement: The backend owns its agent sessions
The selected backend SHALL own the lifecycle of every role session it creates.
The orchestrator SHALL call `open_role()` once per role at shop open,
`deliver_start()` for an envelope addressed to an idle role, `deliver_steer()`
for an envelope addressed to an active role, `interrupt()` on shop close or
shutdown, and `close_role()` to release the session. The backend
SHALL translate its native protocol events into portable `BackendEvent`
instances consumed by the orchestrator. The Hermes backend SHALL operate a
real `hermes acp` subprocess rather than raising `NotImplementedError`.

Interrupting a role SHALL be reserved for closing or shutting down the shop. A
backend whose native interrupt leaves a session unable to accept further work
SHALL NOT return that session to standby, and the orchestrator SHALL NOT treat
an interrupted role as available for a subsequent delivery.

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

#### Scenario: An interrupted role is not returned to standby
- **WHEN** the orchestrator interrupts an active role while closing the shop
- **THEN** the orchestrator does not deliver further envelopes to that role and does not report it as waiting

#### Scenario: Hermes backend is independently testable against a fake ACP fixture
- **WHEN** a fake ACP server fixture is provided as the `hermes acp` command
- **THEN** the orchestrator exercises the Hermes backend through the same `AgentBackend` operations as the Codex backend and all operations succeed without `NotImplementedError`

### Requirement: The Hermes backend operates a real acp subprocess
The Hermes backend SHALL launch `hermes acp` as a subprocess during `start()`.
It SHALL complete ACP `initialize` handshake before returning. It SHALL speak
the ACP JSON-RPC protocol (newline-delimited JSON over stdio) using the same
request/response and notification plumbing as the Codex backend.

Steering an active Hermes turn SHALL preserve that turn. The backend SHALL NOT
send `session/cancel` as part of steering. It SHALL deliver the correction as an
additional `session/prompt` on the same session, which Hermes applies to the
turn already running.

The backend SHALL decide whether a correction steered the active turn or lost a
completion race using its own record of whether the original prompt is still
outstanding. It SHALL NOT decide this from the agent's natural-language reply.

#### Scenario: Hermes backend starts the acp process
- **WHEN** the orchestrator opens the shop with `--backend hermes`
- **THEN** the Hermes backend launches `hermes acp` as a subprocess and completes the `initialize` handshake

#### Scenario: Hermes backend creates role sessions
- **WHEN** `open_role("designer", context)` is called
- **THEN** the backend sends ACP `session/new` with `cwd` set to the active project, sends and awaits an initial `session/prompt` that loads the designer role card and named skills, and only then returns the role handle

#### Scenario: Hermes backend delivers messages
- **WHEN** `deliver_start(handle, message)` is called on an idle session
- **THEN** the backend sends `session/prompt` with the message as a text content block and returns an accepted `DeliveryReceipt`

#### Scenario: Hermes backend steers active turns
- **WHEN** `deliver_steer(handle, expected_id, message)` is called while the prompt identified by `expected_id` is still outstanding
- **THEN** the backend sends an additional `session/prompt` carrying the correction, sends no `session/cancel`, and returns a receipt that still identifies `expected_id` as the active delivery
- **AND IF** the prompt identified by `expected_id` has already responded, the backend raises `InactiveTurn`

#### Scenario: The steer acknowledgement is not a turn completion
- **WHEN** Hermes answers the correction's `session/prompt` immediately while the original prompt remains outstanding
- **THEN** the backend does not emit `turn_completed` for either delivery and the original turn remains the active delivery until its own response arrives

#### Scenario: Output produced before a correction is retained
- **WHEN** a foreman turn streams text, is then steered, and later completes
- **THEN** the assembled `role_message` contains the text streamed before the correction as well as the text streamed after it

#### Scenario: Steering loses a completion race
- **WHEN** `deliver_steer(handle, expected_id, message)` is called and the prompt identified by `expected_id` has already responded
- **THEN** the backend raises `InactiveTurn` and the orchestrator retries the envelope as a new turn on the now-idle session

#### Scenario: Hermes backend interrupts sessions
- **WHEN** `interrupt(handle)` is called
- **THEN** the backend sends `session/cancel` notification and treats that session as spent

### Requirement: Hermes backend translates ACP events into portable events
The Hermes backend SHALL consume ACP `session/update` notifications and
`session/prompt` responses from the subprocess and translate them into
`BackendEvent` instances consumed by the orchestrator.

A prompt that ends because the shop cancelled it SHALL be reported as a
completed turn rather than a role failure, whether the subprocess reports that
cancellation as a stop reason or as a transport-level error. Cancelling a role
SHALL NOT end the shop run.

#### Scenario: Foreman agent message is published to conversation
- **WHEN** the ACP subprocess streams `agent_message_chunk` updates for a foreman prompt and then completes that prompt
- **THEN** the backend emits one `BackendEvent(kind="role_message", role="foreman", text=...)` containing the assembled message before its completion event

#### Scenario: Turn start is tracked
- **WHEN** a `session/prompt` request is dispatched to the subprocess
- **THEN** the backend emits a `BackendEvent(kind="turn_started", role=..., delivery_id=...)`

#### Scenario: Turn completion is tracked
- **WHEN** a `session/prompt` response with `stopReason` is received from the subprocess
- **THEN** the backend emits a `BackendEvent(kind="turn_completed", role=..., delivery_id=...)`

#### Scenario: A cancelled turn does not end the run
- **WHEN** the shop cancels an active prompt and the subprocess answers that prompt with an error instead of a stop reason
- **THEN** the backend emits a completion event for that delivery, does not emit `role_failed`, and the orchestrator keeps routing events

#### Scenario: Backend process failure is reported
- **WHEN** the `hermes acp` subprocess exits unexpectedly
- **THEN** the backend emits a `BackendEvent(kind="backend_failed", error=...)`

## ADDED Requirements

### Requirement: A role-contract bootstrap is not bounded by the control-plane timeout
Opening a role loads that role's card and every skill it names, which is model
work whose duration is unrelated to protocol liveness. The backend SHALL bound
control-plane requests such as `initialize` and `session/new` separately from
prompt work. A role-contract bootstrap that is still progressing SHALL NOT fail
shop open because a control-plane timeout elapsed.

#### Scenario: A slow role bootstrap still opens the shop
- **WHEN** a role's bootstrap prompt takes longer than the control-plane request timeout but completes successfully
- **THEN** the role manifests and the shop opens

#### Scenario: An unresponsive control-plane request still fails fast
- **WHEN** the subprocess does not answer `initialize` or `session/new` within the control-plane timeout
- **THEN** the backend reports the failure rather than waiting for the longer prompt budget

### Requirement: Backend shutdown always releases the subprocess
Closing a backend SHALL terminate its subprocess within a bounded time. The
backend SHALL escalate from a graceful stop to a forced stop so that no close
path can wait indefinitely on a subprocess that declines to exit.

#### Scenario: A subprocess that ignores a graceful stop is forced
- **WHEN** the backend closes and its subprocess neither exits when its input is closed nor on a graceful termination signal
- **THEN** the backend forcibly terminates the subprocess and `close()` returns

#### Scenario: Closing releases resources exactly once
- **WHEN** `close()` is called on an already-closed backend
- **THEN** the call returns without error and starts no new subprocess
