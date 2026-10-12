## MODIFIED Requirements

> **Synchronization intent:** each MODIFIED requirement in this file replaces
> its complete baseline requirement block, including its scenario set.

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
