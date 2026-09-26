# ADR 0006: Generalize shop orchestration to a pluggable agent backend

**Status:** Accepted (amended by ADRs 0008, 0011, 0012, 0016, 0018, 0025, and 0032)

**Date:** 2026-07-26

**Supersedes:** ADR 0005

**Origin:** Shop change `multi-backend-orchestration`

## Context

ADR 0005 established one deterministic shop orchestrator owning one Codex
app-server process. The builder-spike branch exercises a Codex builder role.
The pilot now wants the shop to support Hermes Agent as a second agent
backend, so Codex starts with `--backend codex` and Hermes starts with
`--backend hermes`. Both must use the same broker, the same role cards and
skills, and the same product pipeline.

Hermes is not a Codex-compatible app-server. It has its own protocol (ACP over
stdio), its own session model (one persistent ACP session per role), and its
own configuration surface (toolsets, provider, model). Mapping Hermes into the
existing `CodexControl` protocol would leak Codex concepts into a Hermes
adapter. A portable protocol that both backends implement cleanly replaces the
existing tight coupling.

The broker's role-only addressing was already the right boundary (ADR 0005).
The orchestrator's `CodexAppServer` and `CodexControl` protocol are the only
components that must become backend-neutral.

## Decision

The shop SHALL support a pluggable agent backend selected by a `--backend`
flag on the orchestrator command line:

```
python -m floor.orchestrator PROJECT --backend codex
python -m floor.orchestrator PROJECT --backend hermes
```

The default SHALL be `codex` to preserve backward compatibility.

### Portable protocol

A new `AgentBackend` protocol SHALL replace `CodexControl`. It SHALL expose
only portable operations and events — no Codex `threadId`, `turnId`,
`turn/steer`, Hermes ACP session identifiers, or provider-specific
configuration above this seam.

```python
class AgentBackend(Protocol):
    events: AsyncIterator[BackendEvent]

    async def start(self) -> None: ...
    async def open_role(self, role: str, context: RoleContext) -> RoleHandle: ...
    async def deliver(self, handle: RoleHandle, message: str) -> DeliveryReceipt: ...
    async def interrupt(self, handle: RoleHandle) -> None: ...
    async def close_role(self, handle: RoleHandle) -> None: ...
    async def close(self) -> None: ...
```

Common events:

```text
role_message(role, text)       — agent publishes to maker conversation
turn_started(role, delivery_id) — agent accepted delivered input
turn_completed(role, delivery_id) — agent finished processing
role_failed(role, error)         — role thread/session failed
backend_failed(error)            — backend process terminated unexpectedly
```

### Mapping table

| Portable operation | Codex backend | Hermes backend |
|---|---|---|
| `start()` | `codex app-server --stdio` | `hermes acp` |
| `open_role()` | `thread/start` | `session/new` + `session/prompt` |
| `deliver()` idle | `turn/start` | `session/prompt` |
| `deliver()` active | `turn/steer` | ACP active-turn redirect |
| `interrupt()` | `turn/interrupt` | `session/cancel` |
| `close_role()` | `thread/archive` | Release ACP session |
| `role_message` | `item/completed` notification | ACP `session/update` |
| completion | `turn/completed` | ACP prompt completion |

### Source layout

```text
floor/
  orchestrator.py          composition, broker routing, lifecycle
  backends/
    __init__.py            backend factory (selected by --backend)
    base.py                AgentBackend, RoleHandle, RoleContext, events
    codex.py               extracted current CodexAppServer as CodexBackend
    hermes.py              HermesBackend: ACP client + event translation
```

The current `ShopOrchestrator` SHALL depend on `AgentBackend` instead of
`CodexControl`. The current `CodexAppServer` SHALL move into
`floor/backends/codex.py` with its implementation preserved but its protocol
name generalized.

### Not delegate_task

The Hermes backend SHALL use one persistent Hermes ACP session per role —
NOT `delegate_task` children. `delegate_task` children are fresh,
result-returning, tied to a parent turn, not externally addressable, and not
steerable by the shop orchestrator. They cannot faithfully replace persistent
Codex role threads.

A separate lower-fidelity `--backend hermes-ephemeral` mode that spawns fresh
children per assignment may be added later but is out of scope for this ADR.

### Configuration ownership

Shared and authoritative:
- `agents/*.md` — role cards
- `skills/*/SKILL.md` — portable skills
- Broker role names and lifecycle rules
- Project and repository boundaries

Backend-specific (runtime knobs only):
- `.codex/agents/*.toml` — Codex model, reasoning effort
- Hermes adapter metadata — model, toolset, profile configuration
- Neither backend duplicates the role cards or skills

## Consequences

- The orchestrator no longer knows it is talking to Codex. The `--backend`
  flag selects the concrete implementation at composition time.
- The Codex path is extracted but functionally unchanged. Existing tests
  against `fake_codex_app_server.py` continue to pass.
- The Hermes path requires a running `hermes acp` process and session
  management comparable to Codex thread management.
- Vendor-specific failures (ACP protocol errors, app-server crashes) are
  translated to common `backend_failed` and `role_failed` events.
- ADR 0005's "one deterministic owner of one Codex app-server" generalizes
  to "one deterministic owner of one selected agent backend." The broker
  still speaks only role names.
- The existing `fake_codex_app_server.py` test fixture continues to
  exercise the Codex backend through the portable protocol; a corresponding
  ACP fixture exercises the Hermes backend.
- Idle agents across both backends remain event-driven with zero token
  consumption.
