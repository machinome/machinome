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
- **WHEN** the orchestrator opens the `openspec` profile
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
