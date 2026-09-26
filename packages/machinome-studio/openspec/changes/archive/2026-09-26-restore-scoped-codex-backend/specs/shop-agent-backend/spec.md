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

Project-specific Codex adapters SHALL borrow one hub-owned authenticated service
so concurrent projects share one native authentication owner. Adapter shutdown
SHALL release its own roles, workers and service reference; the final owner
SHALL release the shared process. Closing one project SHALL NOT end another
project's sessions or expose its callbacks/events.

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
- **WHEN** fake Claude, OpenCode or qualified Codex fixtures are selected
- **THEN** each fixture opens and exercises every agent in either initial profile through the same portable backend operations

#### Scenario: An unqualified Codex runtime is not selectable
- **WHEN** a surface requests Codex and the installed runtime does not satisfy its supported capability contract
- **THEN** the request fails with its qualification reason before any real role session is opened

### Requirement: A role-scoped backend failure is recoverable
After the shop has opened, a `role_failed` event SHALL NOT stop the backend event router, broker, browser service, or unaffected role sessions. The orchestrator SHALL clear the failed turn identity, retain the role's session handle for a later attempt, and treat the next envelope addressed to that role as an explicit recovery trigger delivered as a new turn.

If the retained handle rejects that recovery delivery synchronously, the orchestrator SHALL release it, open one replacement session with the same resolved role context, and retry that envelope once, unless the backend explicitly reports that the retained conversation cannot safely be restored and replacing it would discard used history. In that case the orchestrator SHALL retain the failed handle, SHALL NOT open a fresh replacement or replay its context, and SHALL report the retained-history refusal while consuming only that recovery attempt. It SHALL report the role recovered only after a delivery is accepted. If both permitted attempts fail, or retained-history refusal prevents replacement, it SHALL keep the role failed, report the latest reason, consume that delivery attempt without ending routing, and wait for a later envelope rather than polling or retrying autonomously.

`backend_failed` SHALL remain a runtime-ending fault.

#### Scenario: A quota result fails one persistent role
- **WHEN** a role reports a provider session-limit error through `role_failed` while other role sessions are open
- **THEN** the orchestrator records that role failure, clears its active delivery, and continues routing the other roles without closing the shop

#### Scenario: The retained role session accepts a later trigger
- **WHEN** an envelope is addressed to a failed role after backend access is restored and its retained session accepts a new turn
- **THEN** the orchestrator uses that session, reports the role recovered, and marks the envelope delivered

#### Scenario: A dead role process is replaced
- **WHEN** a failed role's retained handle rejects the next delivery without a retained-history refusal and a replacement session accepts it
- **THEN** the orchestrator releases the dead session, opens the same role contract once, reports recovery, and delivers that envelope once to the replacement

#### Scenario: Recovery is triggered before access returns
- **WHEN** the retained handle and its one permitted replacement both reject a recovery envelope
- **THEN** the role remains failed with the latest reason, the routing loops remain live, and no further attempt occurs until another envelope is addressed to that role

#### Scenario: Recovery would discard a used conversation
- **WHEN** the retained handle explicitly reports that recovery cannot safely restore its used conversation and a fresh replacement would discard that history
- **THEN** the orchestrator retains the failed handle, reports that refusal, consumes the recovery attempt without opening a replacement or replaying context, and continues routing unaffected roles

#### Scenario: The whole backend fails
- **WHEN** the backend emits `backend_failed`
- **THEN** the orchestrator ends the runtime and releases its resources

## ADDED Requirements

### Requirement: Codex is qualified before project work
Studio SHALL offer Codex only when its installed runtime, model and effective policy satisfy the explicitly supported contract. Qualification SHALL establish that exact declared tool authority is enforced before offering the runtime. Unsupported or conflicting runtime policy SHALL produce an actionable unavailability reason without substituting another backend or weakening permissions. Qualification SHALL leave project content untouched and SHALL complete before project preparation or real role sessions.

#### Scenario: Unsupported Codex installation
- **WHEN** the pilot explicitly selects Codex with an unsupported runtime or tool-affecting model/configuration contract
- **THEN** opening fails with the unsupported value and remedy before project preparation, and the hub and unrelated sessions remain available

#### Scenario: Qualification detects undeclared tools
- **WHEN** qualification observes an extra advertised tool or a forced undeclared call reaches execution
- **THEN** Codex remains unavailable and no real role opens

#### Scenario: A Claude-only project has no Codex
- **WHEN** the project uses only Claude and Codex is missing or unqualified
- **THEN** opening retains its Claude behavior and does not require Codex authentication or qualification

### Requirement: Codex owns persistent scoped role delivery
Codex SHALL open persistent role sessions carrying the exact resolved profile contract and skill catalogue. It SHALL deliver ordinary input, active steering and trusted notices through the existing portable delivery identity, preserving context across supported idle model changes. It SHALL NOT create a new turn for a notice or a stale steering request, and SHALL NOT replay or migrate a used role's context to another backend.

#### Scenario: Builder starts and completes
- **WHEN** Builder receives an ordinary direction on Codex
- **THEN** its correlated start and completion follow the existing direct-profile lifecycle and its nonempty completed message enters the maker conversation once

#### Scenario: Steering races completion
- **WHEN** steering or a trusted notice arrives after its expected Codex delivery completed
- **THEN** steering reports the inactive-delivery race and a notice remains pending without starting another turn

#### Scenario: Idle Codex model change
- **WHEN** an idle used Codex role applies a supported model and reasoning combination
- **THEN** later input uses that combination on the same conversation under the same declared tool authority

#### Scenario: Resuming after process restart
- **WHEN** supported adapter recovery resumes a retained Codex conversation
- **THEN** its next and all later deliveries retain the exact original tool authority and profile contract without introducing native execution

### Requirement: Codex errors and output remain portable
Codex SHALL normalize role messages, activity, actual token counts and failures through the existing backend contract. Tool errors SHALL be returned to the model and recorded as failed tool activity; they SHALL NOT by themselves fabricate a role failure. Empty-text or tool-only turns SHALL still complete their delivery without an empty conversation message. Duplicate or stale native events SHALL NOT repeat a mutation/message or complete newer work.

#### Scenario: A tool fails
- **WHEN** a declared floor operation returns an error
- **THEN** Codex receives the error result and the role's tool activity records that failure while the turn can continue

#### Scenario: Empty assistant output
- **WHEN** a Codex turn finishes without nonempty assistant text
- **THEN** its matching delivery completes and no empty role message is appended

#### Scenario: Late duplicate event
- **WHEN** a completed old tool/message/turn event is received again after newer work began
- **THEN** no project operation or message repeats and the newer delivery remains active

### Requirement: Codex authentication remains separate from operator configuration
Codex SHALL use a separate one-time Studio login on the operator's existing account in a durable Studio-owned native credential store. Studio SHALL provide an explicit provisioning command and SHALL NOT initiate login as a side effect of project opening. It SHALL NOT copy, read or write the operator's normal CLI credentials or inherit operator/project MCP servers, hooks, plugins, instructions or runtime settings. Unsupported authentication modes and expired or inaccessible credentials SHALL report a remedy without model/provider/backend fallback. Credentials SHALL NOT enter logs, activity, command arguments or retained evidence. One shared authenticated owner SHALL perform native refresh against the authoritative Studio store under exclusive ownership.

#### Scenario: Operator configuration grants extra tools
- **WHEN** the operator has additional MCP servers or project plugins configured
- **THEN** the Codex role receives none of those settings or tools

#### Scenario: Authentication is unavailable
- **WHEN** supported credentials are absent, expired or rejected
- **THEN** the maker receives a role-labelled authentication reason and recovery guidance without credential disclosure or fallback

#### Scenario: Studio login persists
- **WHEN** the operator provisions the dedicated Studio login and closes every project and the hub
- **THEN** its Studio credentials remain available for a later hub, normal CLI credentials remain untouched, and ended floor conversations are not restored as sessions

### Requirement: Concurrent projects share one Codex authentication owner
Simultaneously open projects in one hub SHALL be able to use Codex through one shared authenticated service with isolated per-project role routing. Starting another hub or a login mutation against its active durable store SHALL fail with an actionable exclusive-ownership reason. Native threads and project runtime state SHALL remain ephemeral even though Studio authentication is durable.

#### Scenario: Two Codex projects remain independent
- **WHEN** two projects use Codex concurrently and one closes
- **THEN** the other retains its conversation and tool work, and no event or tool call crosses their session boundaries

#### Scenario: Another hub uses the active login store
- **WHEN** a second hub or provisioning command attempts to acquire an already-owned Studio login store
- **THEN** it fails with an ownership remedy without starting another authenticated process or replacing credentials

#### Scenario: Shared Codex transport fails
- **WHEN** the shared authenticated app-server fails
- **THEN** every attached Codex role receives a role-scoped failure while unrelated backends and projects remain available

### Requirement: Codex teardown owns its tool work
Closing a Codex role or partial open SHALL stop accepting tool calls and boundedly release its active deliveries, owned tool workers and command descendants. Closing its project adapter SHALL release its shared-service reference and ephemeral native thread state. The final service owner SHALL release the app-server and private runtime state while preserving dedicated authentication. Close SHALL be idempotent and SHALL NOT return while owned project-mutating work can continue.

#### Scenario: Close during a blocked build tool
- **WHEN** a Codex role closes while its tool worker is waiting for an owned build subprocess
- **THEN** the worker and command descendants terminate before close returns and cannot modify the project afterward

#### Scenario: Partial role open fails
- **WHEN** opening a later Codex role fails
- **THEN** every resource started for that project open is released under existing partial-open semantics
