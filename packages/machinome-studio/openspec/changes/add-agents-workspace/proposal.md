## Why

The workspace already exposes live agent state in its Model context panel, but
the Agents rail item remains inert and the maker cannot inspect what each
standing session is doing or tune its runtime without editing configuration and
reopening the project. The accepted Agents reference design now supplies the
missing operational view and the pilot has bounded live runtime changes to an
idle agent on its existing backend.

## What Changes

- Make Agents an interactive workspace area with the reference-design roster,
  selected-agent session header, runtime controls, filters, live activity feed,
  expandable tool results, unified file diffs, and links into the Code area.
- Publish normalized per-agent activity from Codex, Claude, and OpenCode through
  the existing session event stream, including tool starts/results, messages,
  errors, file diffs, and available token-usage metadata.
- Expose each agent's resolved backend, provider, model, reasoning level, tool
  policy, assignments, failure, and authoritative backend-idle state in the run
  snapshot and subsequent live updates.
- Let the maker atomically apply one backend-compatible model-and-reasoning
  selection to an idle agent. The backend and provider cannot change, an active
  or assigned agent is rejected server-side, and there is no queued or
  next-assignment mode.
- Preserve the existing Codex or OpenCode conversation context when applying a
  selection. Keep Claude runtime controls read-only until the adapter can prove
  a context-preserving in-backend switch.
- Offer a checked-by-default option to write the applied selection to the
  project's `[tool.solid-node-studio.agents]` table; an unchecked application is
  an explicit session-only override. Writes are revision-checked and preserve
  unrelated project configuration.
- Populate model choices from the shop's supported Codex and Claude sets and
  from the active OpenCode provider catalogue; never use the catalogue to
  change provider or backend.

## Capabilities

### New Capabilities

- `agent-activity-inspection`: The maker-facing Agents workspace, normalized
  activity records, filtering, detailed tool results and file diffs.

### Modified Capabilities

- `shop-browser-workspace`: Agents becomes a mounted interactive workspace area
  with runtime controls and Code navigation.
- `project-runtime-selection`: An idle session may receive a temporary or
  project-persisted model-and-reasoning update without changing backend or
  provider.
- `shop-agent-backend`: Backends expose authoritative idle state, normalized
  activity, catalogued models, and context-preserving runtime updates where
  supported.
- `shop-agent-lifecycle`: Assignment and delivery state jointly gate runtime
  changes so a visible waiting race cannot mutate a working agent.
- `shop-live-state-stream`: The session snapshot and existing stream carry
  resolved runtime metadata and bounded agent activity.

## Impact

The change affects `floor/app.py`, `floor/sessions.py`, `floor/orchestrator.py`,
the backend protocol and all three adapters, project runtime parsing/writing,
the React workspace and CSS, browser/backend fixtures, baseline architecture,
and a new ADR. It adds session-scoped runtime and catalogue endpoints but no
new polling channel, backend migration, provider migration, or framework
repository change.
