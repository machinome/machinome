## MODIFIED Requirements

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
The selected backend SHALL own the lifecycle of every role session it creates.
The orchestrator SHALL call `open_role()` once per role at shop open,
`deliver_start()` for an envelope addressed to an idle role, `deliver_steer()`
for an envelope addressed to an active role, `interrupt()` on shop close or
shutdown, and `close_role()` to release the session. The backend
SHALL translate its native protocol events into portable `BackendEvent`
instances consumed by the orchestrator. The Hermes backend SHALL operate a
real `hermes acp` subprocess rather than raising `NotImplementedError`.

A backend MAY own one external process per role session rather than a single
process for all roles. Process cardinality SHALL NOT change a backend's
obligations: it SHALL own every process it starts and SHALL release all of them
when closed. A backend that owns one process per role SHALL report the
unexpected exit of a single role process as a failure of that role, and SHALL
reserve backend failure for a fault that ends the run.

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

#### Scenario: A partially opened multi-process backend releases what it started
- **WHEN** a backend that owns one process per role fails while opening the second of three role sessions
- **THEN** it releases the processes it already started before reporting the failure

#### Scenario: One role process exiting is a role failure, not a backend failure
- **WHEN** a backend owning one process per role observes a single role process exit unexpectedly
- **THEN** it emits `role_failed` for that role rather than `backend_failed`

#### Scenario: An interrupted role is not returned to standby
- **WHEN** the orchestrator interrupts an active role while closing the shop
- **THEN** the orchestrator does not deliver further envelopes to that role and does not report it as waiting

#### Scenario: Hermes backend is independently testable against a fake ACP fixture
- **WHEN** a fake ACP server fixture is provided as the `hermes acp` command
- **THEN** the orchestrator exercises the Hermes backend through the same `AgentBackend` operations as the Codex backend and all operations succeed without `NotImplementedError`

## ADDED Requirements

### Requirement: The Claude backend operates Claude Code CLI sessions
The Claude backend SHALL launch one `claude` process per role session in
non-interactive streaming mode, exchanging newline-delimited JSON frames over
stdio. It SHALL open each session with the active project as its working
directory.

The backend SHALL deliver the role contract as session-level instructions rather
than as a conversational turn, so that the session's first user message is a
broker envelope. It SHALL read the role's model and permitted tools from that
role's card rather than from a backend-specific adapter file.

The backend SHALL open each role session with operator-machine customization
disabled, so that a role's behavior does not depend on configuration, memory,
hooks, or plugins present on the machine running the shop.

The backend SHALL NOT read, store, forward, or require any credential. It SHALL
invoke the `claude` command as the operator has already configured it.

#### Scenario: Claude backend starts a role session per role
- **WHEN** the orchestrator opens the shop with `--backend claude`
- **THEN** the backend starts one `claude` process per role with the active project as its working directory

#### Scenario: The role contract does not consume a conversational turn
- **WHEN** `open_role("designer", context)` is called
- **THEN** the role contract is delivered as session-level instructions and the session's first user message is a broker envelope

#### Scenario: Role capability comes from the role card
- **WHEN** a role session is opened
- **THEN** the model and permitted tools for that session are those named by the role card's frontmatter

#### Scenario: Operator machine configuration does not reach a role
- **WHEN** the machine running the shop has project or user-level assistant configuration, hooks, or plugins
- **THEN** a role session is opened such that none of them are loaded

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
