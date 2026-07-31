# shop-agent-backend Specification

## Purpose

Define the portable runtime boundary that lets the shop orchestrator own and
route persistent role sessions through either Codex app-server or Hermes ACP
without leaking backend-native identifiers into the broker.
## Requirements
### Requirement: The orchestrator accepts a configurable agent backend
The shop orchestrator SHALL accept a `--backend` flag with values `codex`,
`hermes`, and `claude`. When omitted, the orchestrator SHALL use `codex` as the
default backend. An unknown backend value SHALL cause the orchestrator to exit
with an error before starting the broker or any agent session.

#### Scenario: Codex backend is the default
- **WHEN** a maker opens the shop without specifying `--backend`
- **THEN** the orchestrator uses the Codex backend

#### Scenario: Hermes backend is selected
- **WHEN** a maker opens the shop with `--backend hermes`
- **THEN** the orchestrator uses the Hermes backend

#### Scenario: Claude backend is selected
- **WHEN** a maker opens the shop with `--backend claude`
- **THEN** the orchestrator uses the Claude backend

#### Scenario: Unknown backend is rejected
- **WHEN** a maker opens the shop with `--backend unknown`
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
- **WHEN** fake Codex, Hermes, or Claude fixtures are selected
- **THEN** each fixture opens and exercises every agent in either initial profile through the same portable backend operations

### Requirement: The orchestrator is backend-neutral
The orchestrator SHALL depend only on the portable `AgentBackend` protocol and
resolved profile/agent data. It SHALL NOT reference any backend-native
identifier, wire format, session handle, global role adapter path, or
backend-specific profile parsing. Each backend SHALL own translation of the
resolved model, effort, and tool policy into controls it actually supports.

#### Scenario: Orchestrator code references no backend identifiers or role adapters
- **WHEN** the profile runtime is implemented
- **THEN** `floor/orchestrator.py` contains no Codex/Hermes/Claude wire identifier and no `.codex/agents/<role>.toml` or global `agents/<role>.md` lookup

#### Scenario: Backends receive one resolved interpretation
- **WHEN** a profile agent is opened through any backend
- **THEN** the backend receives the same validated prompt and skill paths, stable identity, labels, and selected-backend runtime policy from the profile loader

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

### Requirement: The Claude backend operates Claude Code CLI sessions
The Claude backend SHALL launch one `claude` process per profile-declared agent
in non-interactive streaming mode, exchange newline-delimited JSON frames over
stdio, and use the active project as its working directory.

It SHALL deliver the resolved profile prompt and skills as session-level
instructions so the first user message remains a broker envelope. It SHALL use
the profile's selected Claude model, effort, and permitted tools rather than
Markdown model/tool fields or a global adapter file. It SHALL open each session
with both project-level and user-level assistant configuration, memory, hooks,
plugins, and other operator-machine customization disabled. It SHALL NOT read,
store, forward, or require a credential, and SHALL invoke the `claude` command
using authentication the operator has already configured.

#### Scenario: Claude starts one process per profile agent
- **WHEN** either initial profile opens with Claude
- **THEN** Claude starts exactly one process for every agent declared by that profile

#### Scenario: The role contract does not consume a conversational turn
- **WHEN** Claude opens a profile agent
- **THEN** prompt and skill contracts are delivered as session-level instructions and the first user message is a broker envelope

#### Scenario: Runtime capability comes from the selected profile
- **WHEN** Claude opens Designer from `fordesmac`
- **THEN** it uses the model, effort, and tool policy that profile declares for Claude, only Designer's validated profile prompt and skill paths, and no global role adapter

#### Scenario: Operator machine configuration does not reach an agent
- **WHEN** the active project or the machine has project-level or user-level assistant configuration, memory, hooks, or plugins
- **THEN** the role session is opened without loading any of them

### Requirement: The Claude backend establishes delivery identity without a vendor turn identifier
The Claude backend SHALL mint its own delivery identifier for each delivery and
correlate it with that role session's next turn-completion frame. It SHALL NOT
derive delivery identity from the session identifier, from replayed input
identifiers, or from the agent's natural-language reply.

Because the runtime provides no signal that a correction arrived after its turn
completed, the Claude backend SHALL resolve that race from its own record of
outstanding deliveries: a correction sent while a delivery is outstanding
preserves that delivery's identity, and a correction sent after it completed
becomes a new delivery.

#### Scenario: A delivery is correlated to its completion
- **WHEN** `deliver_start(handle, message)` is called and the session later reports the turn finished
- **THEN** the backend emits `turn_completed` carrying the delivery identifier it minted for that delivery

#### Scenario: Steering preserves the active delivery identity
- **WHEN** `deliver_steer(handle, expected_id, message)` is called while the delivery identified by `expected_id` is still outstanding
- **THEN** the backend returns a receipt still identifying `expected_id` and the exchange yields one turn completion, not two

#### Scenario: A correction that arrives after completion becomes a new delivery
- **WHEN** a correction is sent after the delivery identified by `expected_id` has already completed
- **THEN** the backend treats it as a new delivery with its own identifier rather than reporting a completion race

### Requirement: Corrections reach a Claude role on a channel it has trusted from the first instruction
Every user message the Claude backend sends to a role session SHALL use the
shop's broker envelope, beginning with the session's first. The role contract
SHALL state that the orchestrator is the trusted control plane for that session
and that a correction may arrive while a turn is running and may appear
alongside tool output.

The backend SHALL NOT decide any control flow from whether the agent acted on a
correction. A refusal SHALL be treated as ordinary turn content.

#### Scenario: The first user message is a broker envelope
- **WHEN** a role session receives its first user message
- **THEN** that message uses the same broker envelope format as every later message

#### Scenario: A declined correction does not change delivery bookkeeping
- **WHEN** an agent declines to act on a steered correction
- **THEN** the backend still reports the delivery as completed when its turn finishes, emits no failure, and the agent's response reaches the maker as turn content

### Requirement: An interrupted Claude turn is a completion, not a role failure
A turn that ends because the shop interrupted it SHALL be reported as a
completed turn, even though the runtime reports it as an errored result.
Interrupting a role SHALL NOT end the shop run.

#### Scenario: Interrupting a role does not end the run
- **WHEN** the shop interrupts an active Claude role and the runtime answers with an errored result carrying an aborted terminal reason
- **THEN** the backend emits a completion event for that delivery, does not emit `role_failed`, and the orchestrator keeps routing events

### Requirement: The Claude backend is independently testable against a fake CLI fixture
A fake Claude CLI fixture SHALL stand in for the `claude` command so the
orchestrator exercises the Claude backend through the same `AgentBackend`
operations as the other backends. The fixture SHALL replay the measured frame
sequence, including injection of mid-turn input at a tool boundary yielding
exactly one turn completion, and the interrupt sequence.

Whether a model acts on a delivered correction SHALL NOT be claimed as covered
by this fixture.

#### Scenario: Claude backend is exercised without the real CLI
- **WHEN** a fake Claude CLI fixture is provided as the `claude` command
- **THEN** the orchestrator opens roles, delivers, steers, interrupts, and closes through the same `AgentBackend` operations as the other backends

#### Scenario: The fixture proves the steer transport
- **WHEN** the fixture receives input while a turn is outstanding
- **THEN** it injects that input at the next tool boundary and answers the exchange with exactly one turn completion

