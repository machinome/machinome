## Why

Runtime agents opened by the shop currently run with full, unrestricted access
to their backend's native tools (shell, file read/write, network, etc.),
regardless of what a role actually needs. Confining an agent to a strictly
scoped, floor-provided toolset — access to only what it needs inside its
active project — reduces blast radius and makes role contracts enforceable in
practice rather than by prompt convention alone.

Live spikes (documented in `design.md`) established that `claude` and
`opencode` each have a real, working mechanism to restrict a session to a
floor-provided custom tool set with no native tools reachable, while `codex`
has none under its current app-server protocol. A further finding shows
`opencode` covers OpenAI subscription auth natively (ChatGPT Plus/Pro OAuth,
not a `codex` wrapper), so `codex`'s gap does not block covering both major
vendors' subscription tiers. The pilot has decided: `codex` is dropped from
this capability, and `claude`/`opencode` are the two backends it targets.

## What Changes

- Add a floor-provided MCP tool server exposing a scoped set of filesystem,
  git, solid-node CLI, and shop-broker lifecycle tools. Filesystem and process
  actions are sandboxed to the active project root; broker tools are fixed to
  the injected floor URL and active session and expose no generic HTTP client.
- Wire that tool server into the `claude` and `opencode` backends, replacing
  native tool access for a role that opts into scoped tools.
- Treat `--projects-dir` as the sole authority for the external project
  catalogue. The running shop does not discover, require, or resolve a Git
  checkout; shop code and trusted resources come from the loaded installation
  or source worktree, including in child MCP processes.
- `floor/backends/claude.py` stops unconditionally passing `--safe-mode` for
  such a role (it currently disables MCP servers outright) and waits through
  transitional MCP startup states after the first real broker envelope
  triggers Claude initialization, until the scoped server is connected or a
  separate bounded readiness deadline expires.
- `floor/backends/opencode.py` gains MCP + `tools:{...:false}` config
  generation, using the default `build` agent and a unique working directory
  per role launch, while consuming cross-directory server events so isolated
  role messages are published as their completed text parts arrive and role
  completions remain observable.
- Keep the browser transcript entirely above its persistent message composer,
  including when the optional agent-failure area is absent.
- `floor/backends/codex.py` is unaffected and undocumented for this
  capability — `codex` keeps full native tool access; roles requiring scoped
  tools should not select it.
- The librarian's tool surface is explicitly out of scope and becomes
  provisionally non-functional under this change.

## Capabilities

### New Capabilities

- `scoped-agent-tools` — a floor-provided, project-sandboxed MCP tool set
  (filesystem, git, solid-node build/test/snapshot, image viewing, and bounded
  shop-broker lifecycle calls) available to `claude` and `opencode` runtime
  agents in place of native tool access.

### Modified Capabilities

None — this is additive; nothing in an existing capability changes shape, it
becomes reachable through the new tool set instead of native tools for roles
that opt in.

## Impact

- `floor/backends/claude.py` — drop unconditional `--safe-mode` for
  scoped-tool roles; wire `--mcp-config`/`--strict-mcp-config`/`--tools`; keep
  the short process-exit grace distinct from first-delivery MCP readiness.
- `floor/backends/opencode.py` — generate `mcp` + `tools` config; unique
  per-role working directory; consume cross-directory role events and publish
  completed assistant text parts without waiting for idle.
- `floor/frontend/src/styles.css` and browser coverage — give every chat child
  an explicit grid track and prove the transcript cannot overlap the composer.
- Floor entry points and resource loading — require the caller's exact
  `--projects-dir`, remove Git-primary-checkout discovery, and load trusted
  shop resources and child modules from the running shop package/worktree.
- `floor/backends/codex.py` — no change; capability unsupported there.
- `floor/profiles.py` — the current `tools cannot be enforced` restriction
  for `codex` remains accurate and unchanged; `claude`/`opencode` tool
  declarations gain real enforcement instead of an allowlist convention.
- A new floor-owned MCP server module implementing the tool set in
  `design.md`.
- The librarian role's tool surface: provisionally non-functional until a
  follow-up change restores it under this same mechanism.
