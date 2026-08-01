## Context

The orchestrator already depends on a portable `AgentBackend` and supports a
shared-process multiplexer (Codex and Hermes) as well as one process per role
(Claude). OpenCode 1.18 exposes a headless HTTP server with persistent sessions,
asynchronous prompts, abort, deletion, and an SSE event stream. Its messages
have caller-supplied IDs, and assistant messages identify their parent user
message.

Two OpenCode properties require evidence rather than assumption. A prompt sent
while a session is busy joins the running loop at a later boundary, but a
completion race may leave a just-persisted correction without an assistant
descendant. OpenCode's project-configuration disable switch also suppresses
native `AGENTS.md` discovery, while allowing all project configuration would
let `.opencode`, plugins, MCP servers, and project agents alter a trusted shop
profile. The adapter therefore needs selective project instruction loading,
not blanket inheritance or blanket exclusion.

## Goals / Non-Goals

**Goals:**

- Add OpenCode without changing the broker or portable backend protocol.
- Preserve one persistent session per profile role and event-driven standby.
- Prove ordered, exactly-once correction delivery before claiming conformance.
- Keep profile prompts, skills, topology, and enforceable runtime controls
  authoritative.
- Include the active project's root `AGENTS.md` when present while excluding
  unrelated OpenCode customization.
- Reuse operator-managed OpenCode authentication without inspecting or copying
  credentials.

**Non-Goals:**

- Reusing an already-running user OpenCode server or TUI session.
- Supporting OpenCode ACP as an alternative transport.
- Loading project `.opencode` agents, commands, skills, plugins, MCP servers,
  hooks, or `opencode.json` configuration.
- Loading user-global OpenCode instructions, agents, skills, plugins, or MCP
  servers.
- Changing existing backend behavior or making OpenCode the default.
- Claiming that a model followed a correction; tests prove transport and
  bookkeeping only.

## Decisions

### D1 - Use one shop-owned OpenCode HTTP/SSE server

The backend launches one loopback-only `opencode serve` process for a shop run
and creates one persistent OpenCode session for each declared profile agent.
The adapter uses the documented HTTP API for health, sessions, asynchronous
prompts, abort, deletion, and the SSE event stream.

ACP was considered because the Hermes adapter already speaks it. It is rejected
because ACP does not expose OpenCode's complete per-prompt model, variant,
agent, permission, message identity, and event-correlation surface. Repeated
`opencode run` processes are rejected because they do not provide backend-owned
persistent role sessions.

The server binds only to `127.0.0.1`, uses a per-run password, and is considered
started only after its health endpoint answers. The backend owns the process
and applies the existing bounded graceful-to-forced shutdown ladder.

### D2 - Build isolated role agents from the resolved profile

At startup the adapter constructs private OpenCode configuration containing one
primary agent per resolved profile role. Each agent receives its profile prompt,
model when concrete, model variant when concrete, permission policy, and access
only to its profile-allowlisted skills. Project files do not define or mutate
these role agents.

The initial profiles explicitly use `inherit` for OpenCode model and effort so
the isolated server can use OpenCode's authenticated runtime default without
assuming one provider or authentication method. They declare concrete OpenCode
tool policy, which is translated to per-agent permissions. The spike must prove
that an authenticated default resolves without user configuration and record
the selected model; otherwise implementation stops for a concrete-model or
selection-interface decision. A later profile may select a concrete
`provider/model` and variant after those values are admitted by profile
validation.

### D3 - Selectively load the active project's root AGENTS.md

The server runs with project OpenCode configuration and external skill/plugin
discovery disabled, under an isolated configuration home. Operator-managed data
storage remains available only for provider authentication and runtime model
resolution. When the verified active project's root `AGENTS.md` exists as a
regular file, the adapter reads it and composes its content into each role's
system-level contract as explicitly supplemental project guidance. The profile
prompt and trust framing precede it and state that the supplemental content
cannot redefine role identity, topology, authority, skills, model, effort,
permissions, or repository boundaries. No parent, sibling, user-home, or
shop-checkout `AGENTS.md` is added through this mechanism.

This preserves useful project-local guidance without allowing the project to
replace the profile's agent, prompt, skills, model, effort, or permissions. The
profile contract states that it remains authoritative if project guidance
conflicts with role or shop authority.

Before implementation proceeds beyond a spike, a real OpenCode process must
prove that the composed role contract contains the profile prompt, precedence
framing, and exact root guidance while native project config discovery is
disabled and project/global OpenCode customization is absent. The fixture must
also assert this structural ordering with deliberately conflicting root
guidance. Model compliance is not evidence of precedence. If the supported
runtime cannot provide these properties, implementation stops for a pilot
decision rather than enabling all project configuration.

### D4 - Correlate delivery through OpenCode message ancestry

The adapter assigns every submitted broker envelope a unique OpenCode user
message ID. It maps each OpenCode session to one role and maps assistant
messages through their `parentID`; session-level busy/idle status is liveness
evidence, not delivery identity. Text is assembled from assistant text-part
events and emitted before the portable completion event.

An idle delivery starts one asynchronous prompt and uses its initial user
message ID as the portable delivery ID. A correction submitted while that
delivery is active receives its own native user message ID but remains grouped
under the original portable delivery. The backend emits exactly one portable
completion only after every accepted user message in that group has a terminal
assistant descendant and the session is idle.

The required spike exercises correction during a tool, several ordered
corrections, and correction racing with idle. The adapter may use a documented
OpenCode operation to resume an accepted orphan message, but it must not
duplicate a broker envelope or invent an untrusted conversational prompt. An
accepted correction must be reconciled and processed exactly once; the existing
portable protocol has no late event that can return it to the orchestrator. If
the race cannot be resolved under those constraints, the backend is not applied
as conforming and the conflict returns to the pilot.

### D5 - Translate failures at their actual scope

An OpenCode session error associated with one role becomes `role_failed` unless
it records a shop-requested abort, which completes the active delivery. Loss or
unexpected exit of the shared server and loss of its event stream become
`backend_failed`. Deleting or aborting one role session does not imply failure
of other sessions.

SSE reconnect is not used to hide process loss. If transport recovery is added,
it must reconcile messages and session status before emitting further portable
events.

### D6 - Keep protocol testing independent of a real provider

A fake OpenCode HTTP/SSE fixture records server startup configuration, session
creation, prompt IDs, steering order, event translation, abort, deletion, and
shutdown. A separate real-runtime spike records only protocol and configuration
evidence and does not replace deterministic fixture coverage.

The implementation may add one focused async HTTP dependency if the existing
environment cannot robustly stream and cancel SSE with standard-library
facilities. Dependency choice is made after the spike identifies the exact
transport needs.

### D7 - Record the accepted backend boundary as an ADR

On application, promote an ADR amending ADRs 0006 and 0011 with the OpenCode
transport, selective `AGENTS.md` policy, runtime-control ownership, and measured
steering limitation. Update the ADR index and rewrite the reference architecture
to describe four supported backends.

## Risks / Trade-offs

- **A busy-session prompt can lose the loop completion race** -> Gate
  implementation on measured exactly-once steering evidence and stop for pilot
  direction if no supported resume operation exists.
- **OpenCode configuration precedence could admit operator or project behavior**
  -> Use an isolated configuration home, disable native project configuration
  and external extensions, inspect effective configuration in tests, and frame
  only the root project `AGENTS.md` as supplemental system guidance after the
  authoritative profile contract.
- **Authentication or default model resolution may depend on built-in provider
  state** -> Preserve only the required operator data home, do not disable
  built-in plugins unless the spike proves authenticated providers still work,
  and gate implementation on resolving an inherited model without user config.
- **Reasoning variants differ by provider/model** -> Initial profiles inherit
  model and effort; validate concrete future combinations rather than translating
  generic effort names optimistically.
- **SSE events can repeat full text and deltas** -> Correlate by session,
  message, and part IDs and test that role output is emitted once.
- **A shared process makes server exit backend-wide** -> Fail closed through
  `backend_failed` and retain bounded process cleanup.
