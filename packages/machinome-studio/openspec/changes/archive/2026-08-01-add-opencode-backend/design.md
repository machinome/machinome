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
native `AGENTS.md` discovery, while allowing project configuration would let
`.opencode`, plugins, MCP servers, and project agents alter a trusted shop
profile. The adapter therefore needs selective project instruction loading.
OpenCode still inherits operator configuration for provider authentication and
default models, while `--pure` disables external plugin execution.
The 2026-08-01 probe against OpenCode 1.18.11 confirmed that a password-protected
loopback server becomes healthy, exposes authenticated provider defaults, and
creates a persistent project session with project configuration disabled. It
also showed that `OPENCODE_CONFIG` and `OPENCODE_CONFIG_DIR` supplement rather
than replace user-global configuration. The temporary policy must describe
that inherited boundary honestly.

## Goals / Non-Goals

**Goals:**

- Add OpenCode without changing the broker or portable backend protocol.
- Preserve one persistent session per profile role and event-driven standby.
- Prove ordered, exactly-once correction delivery before claiming conformance.
- Apply exact profile prompts and exact allowlisted skill instructions in the
  adapter's generated role contract without changing profiles.
- Apply deny-by-default OpenCode permissions and own model/variant/tool
  compatibility defaults in the adapter.
- Include the active project's root `AGENTS.md` when present while excluding
  unrelated project OpenCode customization.
- Reuse operator-managed OpenCode authentication without inspecting or copying
  credentials.

**Non-Goals:**

- Reusing an already-running user OpenCode server or TUI session.
- Supporting OpenCode ACP as an alternative transport.
- Loading project `.opencode` agents, commands, skills, plugins, MCP servers,
  hooks, or `opencode.json` configuration.
- Adding OpenCode tables or settings to profile manifests.
- Claiming that OpenCode exposes controls equivalent to the profile-explicit
  Codex, Claude, and Hermes policy surfaces.
- Isolating the runtime from all user-global OpenCode instructions, agents,
  skills, or MCP servers. Authentication and provider defaults are intentionally
  inherited, while external plugins are disabled with `--pure`.
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

### D2 - Generate role agents under an adapter-owned compatibility policy

At startup the adapter constructs generated OpenCode configuration containing
one randomly named primary agent shared by the backend's persistent role
sessions. Its permission policy denies unknown capabilities and explicitly
admits the tool classes required by shop roles while denying native subagents,
interactive questions, external directories, and native skill discovery. Every
delivery carries the session role's exact profile prompt and the exact
instructions from every profile-allowlisted skill as system context.

Existing profiles remain unchanged and valid. OpenCode selection does not ask
the profile loader for an OpenCode runtime table. The adapter inherits the
authenticated operator model, variant, and configuration and owns temporary
compatibility defaults for model/variant/tool handling. This is a bounded
exception to ADR 0011's profile-explicit runtime policy, justified by OpenCode
1.18.11's measured integration surface. It is not a claim that OpenCode exposes
equivalent controls. A future change may remove the exception only after a
concrete, enforceable OpenCode profile contract is designed and measured.

The 1.18.11 probe exposed operator defaults for `openai/gpt-5.6-terra-fast` and
`opencode/big-pickle`; those values are evidence from one authenticated
environment, not shop defaults. The adapter must record the effective selected
model and variant without credentials during real-runtime verification.

### D3 - Selectively load the active project's root AGENTS.md

The server runs with project OpenCode configuration disabled. Operator OpenCode
configuration remains intentionally available for provider authentication and
runtime model resolution; external plugins are disabled. When the verified active
project's exact root `AGENTS.md` exists as a regular non-symlink file, the
adapter reads it and composes its content into each role's system-level contract
as explicitly supplemental project guidance. The profile prompt and trust framing precede it
and state that the supplemental content cannot redefine role identity,
topology, authority, skills, adapter policy, permissions, or repository
boundaries. No parent, sibling, user-home, or shop-checkout `AGENTS.md` is
added through this mechanism.

This preserves useful project-local guidance without allowing the project to
replace the profile's agent, prompt, skills, authority, or adapter policy. The
profile contract states that it remains authoritative if project guidance
conflicts with role or shop authority.

Before implementation proceeds beyond a spike, a real OpenCode process must
prove that the composed role contract contains the profile prompt, precedence
framing, and exact root guidance while native project config discovery is
disabled. The fixture must also assert this structural ordering with
deliberately conflicting root guidance. Model compliance is not evidence of
precedence. Operator configuration is intentionally inherited and its effective
configuration must be recorded with sensitive values redacted.

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
corrections, and correction racing with idle. The adapter may resume an accepted
orphan by submitting its same native user ID with no new parts, but it must not
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

### D7 - Record the accepted compatibility exception as an ADR

On application, promote an ADR amending ADRs 0006 and 0011 with the OpenCode
transport, selective `AGENTS.md` policy, adapter-owned compatibility defaults,
and measured OpenCode 1.18.11 configuration boundary. The ADR must label the
exception temporary and bounded. Update the ADR index and rewrite the reference
architecture to describe four selectable backends.

## Risks / Trade-offs

- **A busy-session prompt can lose the loop completion race** -> Gate
  implementation on measured exactly-once steering evidence and stop for pilot
  direction if no supported resume operation exists.
- **Operator configuration can add behavior outside the profile contract**
  -> Inherit it deliberately for authentication and defaults, disable external plugins;
  record its effective non-secret configuration, disable native project
  configuration, and frame only the root project `AGENTS.md` as supplemental
  system guidance after the profile contract.
- **Authentication or default model resolution may depend on built-in provider
  state** -> Preserve the required operator data home and gate implementation on
  resolving an inherited model while external plugins remain disabled.
- **Model, variant, and tool behavior are not profile-explicit for OpenCode** ->
  Keep the exception adapter-owned and deny-by-default, expose no false equivalence,
  and require a later measured design before adding profile controls.
- **SSE events can repeat full text and deltas** -> Correlate by session,
  message, and part IDs and test that role output is emitted once.
- **A shared process makes server exit backend-wide** -> Fail closed through
  `backend_failed` and retain bounded process cleanup.
