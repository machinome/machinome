## Why

Runtime agents opened by the shop currently run with full, unrestricted access
to their backend's native tools (shell, file read/write, network, etc.),
regardless of what a role actually needs. Confining an agent to a strictly
scoped, floor-provided toolset — access to only what it needs inside its
active project — would reduce blast radius and make role contracts
enforceable in practice rather than by prompt convention alone. Before any
such capability can be specified, the shop needs to know which of its three
supported backends (`claude`, `codex`, `opencode`) can actually be restricted
this way, and how. This proposal captures that research; it does not yet
commit to an implementation.

## What Changes

**Undetermined — pending a design decision informed by the research in
`design.md`.** Live spikes (see design.md) established that:

- `claude` and `opencode` each have a real, working mechanism to restrict a
  session to a floor-provided custom tool and nothing else.
- `codex` has no such mechanism in its current app-server protocol: native
  tools cannot be removed or restricted, only the shell's sandbox policy can
  be narrowed, and MCP servers are registered globally rather than per
  session.

No decision has been made yet about whether to: implement isolation for
`claude`/`opencode` only and document `codex` as unsupported; treat the
missing codex capability as a framework gap to raise upstream; or find another
approach. This change stays open at the research stage until the pilot picks
a direction, at which point `design.md` will be extended and `specs`/`tasks`
will be written against the chosen approach.

## Capabilities

### New Capabilities

None yet. A capability such as `scoped-agent-tools` (or similar) is expected
once a direction is chosen, but is not specified here to avoid committing to
an implementation the research has not yet settled.

### Modified Capabilities

None yet.

## Impact

Research only at this stage. No code changes. The eventual implementation
would touch `floor/backends/claude.py`, `floor/backends/codex.py` (or its
removal from scope), `floor/backends/opencode.py`, and `floor/profiles.py`
(current tool-allowlist handling), plus profile-declared tool contracts.
