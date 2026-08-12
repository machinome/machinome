## Context

The current workspace mounts Model and Code while keeping one conversation and
one session SSE connection alive. Its Agents rail item is disabled. The broker
records roster/work lifecycle and a short generic event history, while backend
adapters reduce native traffic to role messages, turn boundaries, and failures.
Resolved runtime belongs to the immutable `RuntimeProfile` created at project
open, and the backend protocol has no operation for changing it.

The Agents reference screen asks for a richer session inspector and runtime
control surface. The pilot has deliberately excluded backend/provider migration
and active-session mutation. A model choice therefore always implies a complete
runtime value on the same backend/provider, including reasoning, and is accepted
only when both broker work state and native delivery state are idle.

## Goals / Non-Goals

**Goals:**

- Implement the accepted Agents screen at the same fidelity as the existing
  Model and Code workspace areas without remounting conversation or other areas.
- Make native agent work observable through one backend-neutral activity schema
  and the existing session snapshot/SSE connection.
- Change an idle Codex or OpenCode session's next-turn model and reasoning
  without losing its conversation context.
- Persist the same atomic selection in project configuration when requested,
  with safe concurrent-edit detection and preservation of unrelated TOML.
- Enforce the idle/backend/provider boundary in the server, not only the UI.

**Non-Goals:**

- Moving a session between backends or OpenCode providers.
- Replaying context into a newly created session and calling that migration.
- Changing model or reasoning while an agent has acknowledged work, an active
  native delivery, or queued assignment work.
- Enabling Claude runtime switching until the adapter has a verified
  context-preserving mechanism.
- Making tools or Claude permission project-selectable.
- Adding polling, a second workspace stream, or persistent activity storage.

## Decisions

### D1 — One portable activity record crosses the backend boundary

`BackendEvent` gains an `activity` kind whose payload is an immutable portable
record: stable activity id, role, timestamp, category (`tool`, `file`,
`message`, or `error`), state (`running`, `completed`, or `failed`), display
name, summary, optional detail, optional path, and optional unified diff. It may
also carry token usage when a native terminal event provides it.

Adapters translate native events; the orchestrator never parses backend wire
formats. The broker assigns the public sequence, retains a bounded per-session
history, includes it in snapshots, and publishes each record on the existing
stream. Updates reuse the stable id so the browser replaces a running record
with its terminal form rather than showing duplicates.

Deriving activity solely from broker assignment events was rejected because it
cannot show tools, results, or diffs. Shipping raw backend frames was rejected
because it leaks native protocol and forces the browser to implement three
adapters.

### D2 — Backend idle and broker lifecycle jointly guard runtime mutation

`ShopOrchestrator.update_runtime()` takes the role lock already shared with
delivery. While holding it, the operation rejects a failed role, any native
`active_delivery_id`, a broker agent whose state is active, a current assignment,
or pending assignments. The API therefore cannot race an accepted delivery or
assignment acknowledgement. The browser's disabled state is explanatory only.

Treating visible `waiting` as sufficient was rejected because delegated agents
remain waiting between delivery and acknowledgement and native completion can
race the SSE update.

### D3 — Runtime updates preserve session identity and backend/provider

The portable backend protocol adds `update_runtime(handle, runtime)` and
`runtime_catalog(handle)`. The orchestrator verifies that backend and provider
match the role's current runtime and replaces model and reasoning together.

- Codex stores the new runtime and supplies `model` and `effort` on every later
  `turn/start`, which the current app-server contract defines as turn-scoped
  overrides on the existing thread.
- OpenCode replaces the runtime held for the existing session; every later
  prompt already supplies its provider/model/variant, preserving session
  history.
- Claude reports switching unsupported. Its process receives model and effort
  at launch and no verified in-session, context-preserving switch exists.

Closing and reopening Claude, or synthesizing a context summary into a fresh
process, was rejected because both lose or transform session context.

### D4 — The catalogue is backend-owned and provider-bounded

Codex returns the shop-supported model and effort sets. OpenCode queries its
live provider catalogue and filters it to the role's current provider; choices
carry the variants that provider reports. Claude may expose its current value
for display but marks mutation unsupported. The API returns catalogues per role
so the UI never constructs provider/model strings itself.

A hard-coded OpenCode model list was rejected because authenticated operators
and provider catalogues differ.

### D5 — Persistence is an explicit companion to the live update

The PATCH request carries `persist` (default `true`) and the configuration
revision displayed with the runtime controls. When true, a project-owned writer
uses `tomlkit` to update only the role key below
`[tool.solid-node-studio.agents]`, preserving comments, ordering, and unrelated
tables, and atomically replaces `pyproject.toml` only if its content revision is
unchanged. The writer records the complete backend/provider/model/reasoning
string even though backend/provider did not change.

The operation validates and prepares the new content before changing the live
runtime. It then applies the live update and atomically publishes the prepared
file. A publication failure attempts to restore the prior live runtime before
returning failure. With `persist=false`, only this ephemeral session changes;
reopening resolves from the unchanged project file.

A second sidecar settings file was rejected because project runtime already has
one durable source. Re-rendering parsed TOML with a home-grown serializer was
rejected because it would destroy maker-authored formatting and comments.

### D6 — Agents is a mounted workspace peer

The workspace area state expands to Model, Code, or Agents. Agents renders its
own roster context panel and central inspector but shares the existing title,
conversation, status bar, run state, and SSE connection. Selecting a file diff's
`Open in Code` action activates Code and opens that path through the existing
Code workspace callback. Filters and expanded rows remain local Agents state.

The central feed uses semantic buttons/details and text rather than an icon
font. Runtime controls retain an explicit Apply button, remove apply-mode
choices, and default the persistence checkbox on.

## Risks / Trade-offs

- **Native activity schemas evolve** → Keep translation defensive, preserve an
  error-free fallback summary, and cover measured fixture frames for each
  adapter.
- **Activity can consume unbounded memory** → Retain a documented bounded
  session history while continuing to stream every live record.
- **The config file changes between display and Apply** → Reject with a revision
  conflict and refresh the displayed runtime/config revision; never overwrite.
- **A live update succeeds but file publication fails** → Restore the prior
  runtime under the same role lock and report the failure.
- **OpenCode catalogues can be unavailable** → Keep the current runtime visible,
  disable Apply, and show the backend error without failing the shop session.
- **Token accounting differs by backend** → Display only native values that can
  be normalized honestly and omit the counter otherwise.
- **The wider Agents inspector crowds small desktops** → Follow the existing
  reachable-area responsive rules and allow the inspector/feed to scroll in
  their own columns.

## Migration Plan

Add the dependency and protocol first behind red fixture tests, then extend the
broker snapshot/API and adapters, and finally enable the Agents rail area. The
new snapshot fields and events are additive. Rollback removes the UI and routes;
existing project selections remain valid because persistence writes the already
accepted runtime grammar.

## Open Questions

None. The pilot resolved screen scope, atomic control semantics, idle gating,
Claude behavior, persistence default, and OpenCode catalogue behavior before
ratification.
