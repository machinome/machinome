## Context

The shop launches runtime agents through three backends: `claude`
(`floor/backends/claude.py`, one `claude -p` process per role),
`codex` (`floor/backends/codex.py`, one `codex app-server --stdio` process
multiplexing all roles), and `opencode` (`floor/backends/opencode.py`, one
`opencode serve` HTTP/SSE server). All three currently run with full native
tool access; the `claude` backend allowlists among the CLI's own built-in
tools via `--tools`, `codex` explicitly does not enforce any tool
restriction (`floor/profiles.py` rejects a non-`inherit` value with "tools
cannot be enforced"), and `opencode` gates built-ins through a permission
block but does not register any custom tool.

Before specifying a "strictly scoped, floor-provided toolset" capability, we
needed to know, per backend and verified against the real installed CLI (not
documentation alone): can an agent be restricted to *only* a custom
floor-authored tool, with none of the backend's native tools reachable? This
document records the live spikes run to answer that, independent of the
shop's own wrapper code, using a minimal one-tool MCP server ("hello") and,
for each backend, mirroring the exact invocation shape its `floor/backends/`
module already uses.

## Goals / Non-Goals

**Goals:**
- Establish, with reproducible evidence, whether each backend can be
  restricted to a custom tool set with no native tools reachable.
- Surface backend-specific mechanics, gotchas, and constraints relevant to a
  future implementation.

**Non-Goals:**
- Deciding the shop-facing capability, its schema, or which backends it will
  support. That is deferred to a follow-up revision of this change once the
  pilot picks a direction.
- Implementing anything in `floor/`.

## Decisions

No implementation decisions are made in this document. What follows are
**findings** from live spikes (2026-08-09), each backend driven directly
through its real CLI/protocol using an isolated `venv`-installed MCP SDK and
a single-tool `hello` MCP server (`hello(name) -> "HELLO_SPIKE_RESULT: hi
{name}!"`), verified in two directions: a call that should succeed, and an
attempt to read a file that should fail with no capable tool.

### `claude` — confirmed viable

Driven via the same stdin/stdout `stream-json` protocol
`floor/backends/claude.py` uses. Command:

```
claude -p --input-format stream-json --output-format stream-json --verbose \
  --mcp-config <file> --strict-mcp-config \
  --tools mcp__hellospike__hello \
  --permission-mode bypassPermissions
```

- The session's `system/init` frame reported `"tools":
  ["mcp__hellospike__hello"]` and `"mcp_servers":[{"name":"hellospike",
  "status":"connected"}]`.
- The tool call succeeded and returned the exact expected string.
- A follow-up asking it to read a file in the same directory was correctly
  refused: "I don't have a file-reading tool available in this session... no
  Read/Bash/etc."
- **Gotcha (blocks this today):** `floor/backends/claude.py`'s
  `_role_command` always passes `--safe-mode`, and `--safe-mode` explicitly
  disables MCP servers among other customizations. With `--safe-mode` present
  alongside `--mcp-config`/`--strict-mcp-config`, the MCP server never
  connected (`"status":"pending"` then `"status":"failed"`) and the tool was
  unreachable. `--safe-mode` would need to be dropped or conditioned for this
  backend before floor-provided MCP tools could work at all.
- MCP server startup is asynchronous relative to the first turn; a session
  that sends its first message immediately after spawn can race a
  still-connecting server (`status: pending`). The real backend already has a
  `startup_grace` wait after spawn, which should be enough in practice, but
  this is worth keeping in mind if a "no tools available" failure shows up
  intermittently.

### `codex` — not viable with the current protocol

Driven via the same JSON-RPC `codex app-server --stdio` protocol
`floor/backends/codex.py` uses (`initialize` → `initialized` → `thread/start`
→ `turn/start`).

- A custom MCP server (registered via `codex mcp add`, which writes to the
  user's global `~/.codex/config.toml`) **is** callable — confirmed end to
  end, tool call succeeded with the exact expected result.
- There is no protocol-level way to remove or restrict codex's own native
  tools. The generated app-server JSON schemas (`codex app-server
  generate-json-schema`) show neither `ThreadStartParams` nor
  `TurnStartParams` has any `tools` field. A `DynamicToolSpec`/
  `DynamicToolCallParams` mechanism exists in the schema (the app-server can
  call back into its client to execute a tool), but nothing in the current
  protocol wires a per-thread tool list through `thread/start` or
  `turn/start` — it is unused surface, not a working per-agent isolation
  path.
- Sandbox modes (`read-only` / `workspace-write` / `danger-full-access`)
  constrain what the shell tool can *do*, not whether it exists. With
  `danger-full-access` (what `floor/backends/codex.py` hardcodes today) the
  model freely `cat`'d a file it was told not to touch. This matches
  `floor/profiles.py`'s existing comment that "tools cannot be enforced" for
  this backend — now confirmed against the live protocol, not just asserted.
- MCP servers registered via `codex mcp add` are **global**, not per-thread:
  starting a thread loaded every MCP server in the user's `~/.codex/
  config.toml` (`context7`, `supabase`, `langchain-docs`, plus the spike's
  own `hellospike`), not just the one relevant to that role. There is no
  per-thread scoping of which registered servers a given thread can see.

### `opencode` — confirmed viable

Driven via the same HTTP/SSE protocol `floor/backends/opencode.py` uses
(`POST /session`, `POST /session/{id}/prompt_async`, poll
`GET /session/{id}/message`), with a generated `opencode.json` pointing
`mcp.hellospike` at the same MCP server and a top-level `tools: {read:
false, write: false, edit: false, bash: false, glob: false, grep: false,
list: false, webfetch: false, websearch: false, task: false, todowrite:
false, todoread: false, patch: false}` map, no custom agent needed (default
`build` agent).

- The MCP tool is exposed to the model as `<server>_<tool>`
  (`hellospike_hello`), not the `mcp__server__tool` shape `claude` uses.
- The call succeeded (`"output": "HELLO_SPIKE_RESULT: hi Spike!"`).
- Asked to read a file, the model's own reasoning enumerated its actual
  available tools as exactly `hellospike_hello`, `question`, `skill` and
  correctly declined — no file access occurred.
- `opencode`'s SDK type definitions (`@opencode-ai/sdk` `types.gen.d.ts`)
  confirm `tools?: { [key: string]: boolean }` and `mcp?: { [key: string]:
  McpLocalConfig | McpRemoteConfig }` are real, documented config fields, not
  spike-only behavior.
- **Operational hazard found, not yet a blocker:** opencode persists session
  state keyed by working directory across separate `opencode serve` process
  launches. Reusing the same project directory across two independent spike
  runs bled conversation context between them; combined with an ambiguous
  one-word prompt, a `deepseek-v4-flash-free` session under the default
  `build` agent (which still had full native tool access in that run) wrote
  and executed its own script inside the scratch directory unprompted. No
  damage occurred outside that directory, but this means the real backend's
  per-role isolation needs either a unique working directory per launch or
  explicit verification that opencode does not carry state across restarts
  of the same project.
- A first attempt at this spike used a custom agent block with `permission:
  "deny"` plus a `tools` map, and *incorrectly* appeared to fail (the model
  couldn't see `hellospike_hello` and still described bash/file tools as
  available in its response text) — that failure was a bug in the spike's
  own agent/permission config, not a backend limitation. The version above
  (default agent + `tools` map only, no custom agent, no `permission` block)
  is the one confirmed working and should be treated as the reference
  configuration, not the first attempt.

## Risks / Trade-offs

- [`codex` cannot honor this capability at all under its current protocol] →
  Any future spec must either explicitly exclude `codex`, wait on an
  upstream codex capability, or accept full native tool access as an
  unavoidable property of choosing that backend for a role.
- [`codex`'s global MCP registration leaks unrelated servers into every
  thread] → Even if codex tool-removal shipped upstream, floor-provided tools
  would still need per-thread MCP scoping codex does not currently offer.
- [`claude`'s `--safe-mode` blocks MCP entirely] → Any implementation for
  this backend requires changing `floor/backends/claude.py` to stop
  unconditionally passing `--safe-mode`, which currently also suppresses
  other customizations (skills, plugins, hooks, custom commands/agents) —
  the trade-off of dropping it needs its own evaluation, separate from tool
  scoping.
- [`opencode` session/state bleed across process launches] → Needs a
  concrete mitigation (unique cwd, unique session id, or confirmed-safe
  reuse) before this backend's isolation can be trusted in the real shop,
  not just in a short-lived spike.

## Migration Plan

Not applicable — no implementation yet.

## Open Questions

- Does the shop want a capability that works only for `claude` and
  `opencode`, explicitly documenting `codex` as unsupported for
  tool-scoped roles?
- Is codex's missing tool-restriction capability worth raising upstream as a
  framework wart (see `file-a-wart` skill), given `solid-node-studio` already
  tracks it as a known limitation in `floor/profiles.py`?
- What should the profile-facing contract look like for declaring a role's
  scoped toolset (schema, where it lives relative to `pyproject.toml`
  runtime declarations)?
- How should `--safe-mode` removal for `claude` be reconciled with whatever
  reason it was added in the first place?
