## Why

The shop's portable backend seam can support OpenCode's persistent server and
session model, giving operators another authenticated runtime without changing
broker semantics. OpenCode 1.18.11 does not expose an equivalent integration
surface for every profile-declared runtime control, so a viable first adapter
needs a narrow, explicit compatibility policy rather than new profile tables.

## What Changes

- Add `opencode` as a selectable fourth agent backend using persistent role
  sessions behind one shop-owned OpenCode server process.
- Translate OpenCode messages, session state, errors, interruption, and
  shutdown into the existing portable backend operations and events.
- Keep existing profiles unchanged and valid. OpenCode inherits the
  authenticated operator model, variant, and configuration, while its adapter
  owns temporary compatibility defaults for model/variant/tool handling and
  applies deny-by-default permissions.
- Generate one primary OpenCode adapter agent and carry each role's exact
  profile prompt and exact allowlisted skill instructions in its session
  deliveries.
- Disable native project configuration and manually append only an exact
  project-root regular, non-symlink `AGENTS.md` as subordinate guidance.
- Treat this as a bounded exception to profile-explicit runtime policy, not as
  a claim that OpenCode exposes controls equivalent to existing backends.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `shop-agent-backend`: Add OpenCode selection, persistent HTTP/SSE session
  ownership, portable event and delivery correlation, steering, interruption,
  adapter-owned compatibility defaults, generated role contracts, selective
  project `AGENTS.md` loading, inherited operator configuration, and independent
  fixture coverage.

## Impact

- Affects backend composition and CLI selection, process and HTTP/SSE lifecycle
  management, generated OpenCode configuration, and backend acceptance
  fixtures. Existing profile schemas and manifests do not change.
- Adds a local `opencode` runtime prerequisite and may add a Python HTTP client
  dependency for streaming server events.
- Updates the backend architecture decision, reference architecture, runtime
  documentation, and supported-backend matrix.
- Does not change the broker API, portable `AgentBackend` protocol, profile
  manifests or topology, default backend, or existing Codex, Claude, and Hermes
  behavior. Profile validation only admits the adapter-owned inherited runtime
  when OpenCode is selected.
