# shop-agent-backend Specification

## Purpose

Define the portable runtime boundary that lets the shop orchestrator own and
route persistent role sessions through Codex app-server, Hermes ACP, Claude
Code CLI, or OpenCode without leaking backend-native identifiers into the
broker.
## Requirements
### Requirement: The orchestrator accepts a configurable agent backend
The shop orchestrator SHALL accept a `--backend` flag with values `codex`,
`hermes`, `claude`, and `opencode`. When omitted, the orchestrator SHALL use
`codex` as the default backend. An unknown backend value SHALL cause the
orchestrator to exit with an error before starting the broker or any agent
session.

#### Scenario: Codex backend is the default
- **WHEN** a maker opens the shop without specifying `--backend`
- **THEN** the orchestrator uses the Codex backend

#### Scenario: Hermes backend is selected
- **WHEN** a maker opens the shop with `--backend hermes`
- **THEN** the orchestrator uses the Hermes backend

#### Scenario: Claude backend is selected
- **WHEN** a maker opens the shop with `--backend claude`
- **THEN** the orchestrator uses the Claude backend

#### Scenario: OpenCode backend is selected
- **WHEN** a maker opens the shop with `--backend opencode`
- **THEN** the orchestrator uses the OpenCode backend

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
- **WHEN** fake Codex, Hermes, Claude, or OpenCode fixtures are selected
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
- **THEN** `floor/orchestrator.py` contains no Codex, Hermes, Claude, or OpenCode wire identifier and no global backend role-adapter lookup

#### Scenario: Backends receive one resolved role interpretation
- **WHEN** a profile agent is opened through any backend
- **THEN** the backend receives the same validated prompt and skill paths, stable identity, and labels from the profile loader

#### Scenario: OpenCode does not add a profile policy lookup
- **WHEN** a validated existing profile is opened through OpenCode
- **THEN** the adapter applies its compatibility policy without requiring or reading an OpenCode table in that profile

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

### Requirement: The OpenCode backend operates a shop-owned server and persistent role sessions
The OpenCode backend SHALL launch one loopback-only `opencode serve` subprocess,
wait for its health endpoint before opening roles, and create one persistent
OpenCode session for every profile-declared agent. It SHALL use the verified
active project as the server and session workspace and SHALL configure each
session from that agent's resolved role contract and the adapter-owned
compatibility policy.

The backend SHALL use operator-managed OpenCode provider authentication without
reading, copying, storing, or forwarding credentials. It SHALL NOT attach to an
unrelated existing OpenCode server or session.

#### Scenario: OpenCode starts one shared server
- **WHEN** either initial profile opens with OpenCode
- **THEN** the backend starts one authenticated loopback server and creates exactly one persistent session for each declared profile agent

#### Scenario: OpenCode opens a role without a bootstrap turn
- **WHEN** `open_role("designer", context)` is called
- **THEN** the backend configures Designer's generated role agent and project workspace before returning without sending a conversational user message

#### Scenario: Operator authentication remains external
- **WHEN** the OpenCode server connects to the inherited operator-selected provider
- **THEN** the shop relies on authentication already configured by the operator and does not receive the credential

### Requirement: OpenCode uses bounded adapter-owned compatibility defaults
Existing profiles SHALL remain unchanged and valid when OpenCode is selected.
The OpenCode adapter SHALL NOT require or read OpenCode model, variant, effort,
tool, or permission declarations from a profile manifest. It SHALL inherit the
authenticated operator model, variant, and configuration and SHALL own temporary
compatibility defaults for model/variant/tool handling.

The adapter SHALL generate one primary OpenCode agent shared by its persistent
role sessions and SHALL apply a deny-by-default permission policy. Every
delivery SHALL carry the target role's exact profile prompt and the exact
instructions of each profile-allowlisted skill as system context. The adapter
SHALL explicitly admit required shop tool classes while denying native
subagents, interactive questions, external directories, and native skill
discovery. This bounded exception to profile-explicit runtime policy SHALL NOT
be represented as equivalent control across backends.

#### Scenario: Existing profile selects OpenCode
- **WHEN** Builder or Fordesmac is selected with `--backend opencode`
- **THEN** profile validation succeeds without an OpenCode table and the adapter supplies the compatibility defaults

#### Scenario: A role agent is generated
- **WHEN** OpenCode starts and later opens resolved profile roles
- **THEN** one generated primary agent serves their persistent sessions and each role delivery carries that role's exact profile prompt and exact allowlisted skill instructions

#### Scenario: OpenCode permissions are established
- **WHEN** the adapter generates its OpenCode agent
- **THEN** it applies deny-by-default permissions with only required shop tool classes admitted and reads no permission declarations from the profile manifest

#### Scenario: Operator runtime choices are inherited
- **WHEN** the generated role starts without adapter-selected concrete values
- **THEN** OpenCode uses the authenticated operator model, variant, and configuration and runtime evidence records the effective non-secret choices

### Requirement: OpenCode uses an explicit project-instruction boundary
The OpenCode backend SHALL include the verified active project's exact root
`AGENTS.md` as supplemental system-level session instruction only when it is a
regular non-symlink file. The composed contract SHALL place the profile prompt and explicit
precedence framing before the project guidance and SHALL state that the profile
remains authoritative for role identity, topology, authority, skills, adapter
policy, permissions, and repository boundaries.

The backend SHALL prevent automatic discovery or activation of project OpenCode
agents, commands, skills, plugins, MCP servers, hooks, configuration, and
instruction files other than that root `AGENTS.md`. It SHALL intentionally
inherit the operator's global OpenCode configuration for authentication and
default model resolution and SHALL run in pure mode so external plugins do not
execute. Other global configuration may remain visible. This does not make ordinary files beneath the active project
unreadable through profile-permitted tools. The backend SHALL NOT load an
`AGENTS.md` from the shop checkout, a parent directory, a sibling project, or
the user home through this project instruction mechanism.

#### Scenario: Active project supplies root guidance
- **WHEN** the verified active project contains a regular non-symlink root `AGENTS.md`
- **THEN** every OpenCode role session receives its exact content after profile-authority framing as supplemental project-local instruction

#### Scenario: Root guidance conflicts with the profile
- **WHEN** the active project's root `AGENTS.md` attempts to redefine a role, permission, skill, model, authority edge, or repository boundary
- **THEN** the composed system contract structurally identifies that content as subordinate guidance and retains the profile values without modification

#### Scenario: Active project has no root guidance
- **WHEN** the verified active project has no root `AGENTS.md`
- **THEN** OpenCode opens every role without fabricating project instruction or searching another repository for one

#### Scenario: Root guidance is a symlink or non-regular file
- **WHEN** the exact project-root `AGENTS.md` is a symlink or is not a regular file
- **THEN** OpenCode does not append it and does not follow it to another location

#### Scenario: Project OpenCode customization is present
- **WHEN** the active project contains OpenCode agents, skills, plugins, MCP servers, hooks, or configuration outside the generated runtime contract
- **THEN** OpenCode does not automatically discover or activate those project customizations for the shop's sessions

#### Scenario: Operator OpenCode customization is present
- **WHEN** the operator machine contains OpenCode agents, skills, plugins, MCP servers, hooks, or configuration
- **THEN** the backend inherits authentication and provider defaults, disables external plugins, and records the effective non-secret configuration in runtime evidence

### Requirement: OpenCode correlates messages and preserves active delivery identity
The OpenCode backend SHALL assign each submitted broker envelope a unique
native user-message identifier and SHALL correlate output through native
session, parent-message, assistant-message, and part identifiers rather than
agent prose or session status alone.

An idle delivery SHALL establish one portable delivery identity. Corrections
accepted while it remains active SHALL be presented once in recorded order,
SHALL retain that portable identity, and SHALL produce exactly one portable
completion after every accepted message has been processed. If the active
delivery completes before a correction is accepted, the backend SHALL report
the completion race so the orchestrator can start a new delivery.

Once OpenCode accepts a correction, the backend SHALL ensure it is processed
exactly once under the active delivery. It MUST NOT report a late completion
race for an accepted correction because the portable protocol cannot return an
already accepted envelope to the orchestrator.

#### Scenario: An idle role starts a delivery
- **WHEN** `deliver_start()` submits a broker envelope to an idle OpenCode role
- **THEN** the backend returns its unique delivery identity and emits matching start and completion events around the resulting exchange

#### Scenario: Direction arrives during an OpenCode tool call
- **WHEN** `deliver_steer()` accepts direction while the role is using a tool
- **THEN** OpenCode presents it once after that tool completes and before the role's next task action while preserving the active portable delivery identity

#### Scenario: Several OpenCode corrections are accepted
- **WHEN** several corrections arrive while one delivery remains active
- **THEN** the role receives each correction once in recorded order and the backend emits one completion for the grouped delivery

#### Scenario: Steering races with idle
- **WHEN** OpenCode accepts a correction while its session is transitioning to idle
- **THEN** the backend resumes or reconciles native processing so that correction is processed exactly once under the active delivery without losing or duplicating the envelope

#### Scenario: Completion wins before correction acceptance
- **WHEN** the active OpenCode delivery completes before the backend accepts a correction
- **THEN** the backend raises `InactiveTurn` so the orchestrator can submit the unchanged envelope as a new delivery

### Requirement: OpenCode translates server events and failures into portable events
The OpenCode backend SHALL consume the server's SSE stream and translate
assistant text, session state, session errors, and server loss into portable
events. It SHALL emit non-empty role output before the matching completion and
SHALL emit each text contribution once even when the native stream carries both
deltas and updated full parts.

A shop-requested abort SHALL complete the active delivery rather than fail the
role. A fault confined to one session SHALL emit `role_failed`; unexpected
shared-server exit or unrecoverable event-stream loss SHALL emit
`backend_failed`.

#### Scenario: OpenCode publishes user-facing output
- **WHEN** an assistant message for the user-facing role completes with text parts
- **THEN** the backend emits that text once as `role_message` before the matching `turn_completed`

#### Scenario: OpenCode role is interrupted during shutdown
- **WHEN** the shop aborts an active OpenCode role while closing
- **THEN** the backend emits completion for that delivery and does not report the abort as role failure

#### Scenario: One OpenCode session fails
- **WHEN** a native error is attributable to one role session
- **THEN** the backend emits `role_failed` for that role without misidentifying another session

#### Scenario: OpenCode server exits unexpectedly
- **WHEN** the shared server process exits before backend close
- **THEN** the backend emits `backend_failed` and the shop run fails closed

### Requirement: The OpenCode backend is independently testable against a fake server
A fake OpenCode HTTP/SSE fixture SHALL exercise startup, health, role sessions,
adapter-owned compatibility configuration, root `AGENTS.md` selection, prompt identity,
ordered steering, text assembly, interruption, role deletion, server failure,
and bounded shutdown without a real provider.

Real-runtime evidence SHALL additionally prove project-configuration isolation,
record inherited operator configuration, and prove correction delivery at a tool
boundary before the backend is accepted.

Fixture evidence SHALL NOT be presented as proof that a model obeyed a
correction.

#### Scenario: Fake OpenCode exercises either initial profile
- **WHEN** the fake server is selected for Builder or Fordesmac
- **THEN** every declared role is opened, delivered, steered, interrupted, and closed through the unchanged portable backend operations

#### Scenario: Real OpenCode proves selective project instruction
- **WHEN** the isolation spike opens a project containing root `AGENTS.md` and conflicting project OpenCode customization
- **THEN** observed session context contains the profile contract followed by framed root guidance while automatic project OpenCode customization remains inactive and inherited operator configuration is recorded

#### Scenario: Real OpenCode proves correction transport
- **WHEN** the steering spike submits ordered corrections during an active tool call and near idle
- **THEN** recorded native events prove each accepted envelope is processed exactly once under the active delivery
