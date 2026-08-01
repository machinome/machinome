## Why

The shop's portable backend seam can support OpenCode's persistent server and
session model, giving operators another authenticated runtime without changing
broker semantics. OpenCode must preserve the same profile authority, steering,
and lifecycle guarantees as existing backends while still honoring the active
mechanical project's root `AGENTS.md` as project-local guidance.

## What Changes

- Add `opencode` as a selectable fourth agent backend using persistent role
  sessions behind one shop-owned OpenCode server process.
- Translate OpenCode messages, session state, errors, interruption, and
  shutdown into the existing portable backend operations and events.
- Extend runtime profiles with explicit OpenCode model, effort, and tool policy
  that the adapter can enforce without silently inheriting different values.
- Load the active project's root `AGENTS.md` when present, while excluding
  project and user OpenCode agents, plugins, MCP servers, skills, hooks, and
  other configuration that could replace or expand the selected profile.
- Require measured steering and configuration-isolation evidence before the
  backend is accepted as conforming.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `shop-agent-backend`: Add OpenCode selection, persistent HTTP/SSE session
  ownership, portable event and delivery correlation, steering, interruption,
  selective project `AGENTS.md` loading, isolation, and independent fixture
  coverage.
- `shop-runtime-profile`: Require complete, enforceable OpenCode runtime policy
  for every declared agent and make both initial profiles valid through the new
  backend.

## Impact

- Affects backend composition and CLI selection, profile validation and both
  built-in profile manifests, process and HTTP/SSE lifecycle management, and
  backend acceptance fixtures.
- Adds a local `opencode` runtime prerequisite and may add a Python HTTP client
  dependency for streaming server events.
- Updates the backend architecture decision, reference architecture, runtime
  documentation, and supported-backend matrix.
- Does not change the broker API, portable `AgentBackend` protocol, profile
  topology, default backend, or existing Codex, Claude, and Hermes behavior.
