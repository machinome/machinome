## Why

ADR 0005 established one deterministic orchestrator owning one Codex
app-server. The pilot now wants the shop to support Hermes Agent as a second
agent backend so the same harness can drive mechanical work through either
Codex or Hermes. Making the backend pluggable keeps the broker portable and
the role contracts shared while letting each backend own its native protocol
and configuration surface.

## What Changes

- Introduce an `AgentBackend` protocol as the portable seam between the shop
  orchestrator and any agent runtime. Extract the current Codex-specific logic
  into a backend that implements it.
- Add a `--backend` flag to the orchestrator CLI (`codex` | `hermes`) with
  `codex` as the default.
- Extract `CodexAppServer` from `floor/orchestrator.py` into
  `floor/backends/codex.py` and make it implement `AgentBackend`.
- Add `floor/backends/hermes.py` implementing `AgentBackend` over the
  installed Hermes ACP protocol.
- Keep the broker, role cards, skills, product pipeline, preparation,
  functional-model boundary, and browser UI unchanged.
- Keep the existing `fake_codex_app_server.py` test fixture and acceptance
  tests passing through the portable protocol.

## Capabilities

### New Capabilities

- `shop-agent-backend`: Pluggable agent backend selected by `--backend`;
  `AgentBackend` protocol with role-level operations and vendor-neutral events.

### Modified Capabilities

- `shop-floor-lifecycle`: Opening and closing the shop now starts and stops
  the selected backend rather than hard-coding a Codex app-server.
- `shop-agent-lifecycle`: Manifested agents come from backend sessions; the
  broker is unchanged.
- `shop-agent-messaging`: Same ordered delivery, tool-boundary injection,
  and event-driven standby, now routed through `AgentBackend` rather than
  Codex-specific turn operations.

## Impact

- `floor/orchestrator.py` — `ShopOrchestrator` depends on `AgentBackend`
  instead of `CodexControl`; `CodexAppServer` extracted.
- `floor/backends/__init__.py` — backend factory (`new --backend` flag).
- `floor/backends/base.py` — `AgentBackend`, `RoleHandle`, `RoleContext`,
  `BackendEvent`, `DeliveryReceipt`.
- `floor/backends/codex.py` — extracted `CodexBackend` (formerly
  `CodexAppServer`).
- `floor/backends/hermes.py` — `HermesBackend` over `hermes acp`.
- `tests/fixtures/fake_codex_app_server.py` — already exercises the Codex
  protocol surface; wire through `AgentBackend`.
- `docs/architecture-overview.md` — already updated to reflect the four-layer
  multi-backend architecture (this change).
- `docs/adrs/0005-*.md` — status updated to Superseded by 0006.
- `docs/adrs/0006-*.md` — new ADR (this change).
- Broker, role cards, skills, product pipeline, preparation, browser UI —
  no changes.
