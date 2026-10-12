## MODIFIED Requirements

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

## ADDED Requirements

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
