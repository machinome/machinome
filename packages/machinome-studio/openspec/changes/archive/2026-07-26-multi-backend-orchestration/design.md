## Context

`floor/orchestrator.py` currently defines a `CodexControl` protocol and a
`CodexAppServer` class that speaks newline-delimited JSON-RPC over stdio to a
`codex app-server --stdio` process. `ShopOrchestrator` is parameterized on
`CodexControl` and `BrokerControl`. The `_serve` function hard-codes a
`CodexAppServer` instance.

Making the backend pluggable requires:

1. A portable `AgentBackend` protocol that captures the operations the
   orchestrator actually needs — start, open_role, deliver, interrupt,
   close_role, close — plus an async event iterator for backend-to-orchestrator
   notifications.
2. Extracting the current `CodexAppServer` into a `CodexBackend` that
   implements `AgentBackend`.
3. Adding a `--backend` flag to the CLI and a factory to select the
   concrete implementation.
4. A `HermesBackend` that implements `AgentBackend` over `hermes acp`,
   translating between the portable events and ACP's `session/prompt`,
   `session/cancel`, and `session/update` notifications.

## Goals / Non-Goals

**Goals:**

- Replace `CodexControl` with `AgentBackend` so the orchestrator never
  references `threadId`, `turnId`, `turn/steer`, or other Codex-specific
  identifiers.
- Extract `CodexAppServer` without changing its behaviour or breaking
  existing tests.
- Add `--backend codex|hermes` flag; `codex` is the default.
- Define the common event vocabulary (`role_message`, `turn_started`,
  `turn_completed`, `role_failed`, `backend_failed`).
- Keep the existing `fake_codex_app_server.py` fixture working through the
  new protocol.
- Add a new `fake_acp_server.py` fixture for Hermes backend testing.
- Keep the broker, role cards, skills, product pipeline, preparation,
  functional-model boundary, and browser UI untouched.

**Non-Goals:**

- A `--backend hermes-ephemeral` mode using `delegate_task` children.
- Changing the broker's role set, envelope kinds, or messaging rules.
- Durable recovery of backend sessions after the shop process exits.

> **Note (2026-07-26):** The Hermes backend was initially classified as a
> non-goal (structural outline only).  The follow-on change
> `2026-07-26-implement-hermes-backend-acp-integration` completed the
> implementation — `HermesBackend` now wires to a real `hermes acp`
> subprocess and all `AgentBackend` methods are operational.

## Decisions

### AgentBackend protocol

Define in `floor/backends/base.py`:

```python
from dataclasses import dataclass
from collections.abc import AsyncIterator
from typing import Protocol

@dataclass(frozen=True)
class RoleContext:
    shop_checkout: str
    active_project: str
    model_callback_url: str | None = None

@dataclass(frozen=True)
class RoleHandle:
    backend_id: str   # opaque; never exposed above the backend
    role: str

@dataclass(frozen=True)
class DeliveryReceipt:
    delivery_id: str  # opaque; used to correlate turn_started/completed
    accepted: bool

class BackendEvent:
    kind: str  # role_message | turn_started | turn_completed |
               # role_failed | backend_failed
    role: str | None = None
    text: str | None = None
    delivery_id: str | None = None
    error: str | None = None

class AgentBackend(Protocol):
    events: AsyncIterator[BackendEvent]

    async def start(self) -> None: ...
    async def open_role(self, role: str, context: RoleContext) -> RoleHandle: ...
    async def deliver(self, handle: RoleHandle, message: str) -> DeliveryReceipt: ...
    async def interrupt(self, handle: RoleHandle) -> None: ...
    async def close_role(self, handle: RoleHandle) -> None: ...
    async def close(self) -> None: ...
```

### ShopOrchestrator changes

Replace `self.codex: CodexControl` with `self.backend: AgentBackend`.
Replace `RoleRuntime(thread_id=...)` with `RoleRuntime(handle=..., ...)`.
Replace `CodexControl` method calls with `AgentBackend` calls:

```text
codex.start()          → backend.start()
codex.start_thread(r)  → backend.open_role(r, context)
codex.start_turn(h, m) → backend.deliver(h, m)
codex.steer_turn(...)  → backend.deliver(h, m)
codex.interrupt_turn   → backend.interrupt(h)
codex.close_thread(h)  → backend.close_role(h)
codex.close()          → backend.close()
```

The `handle_notification` method that translates app-server notifications
into broker actions moves into the backend. Each backend translates its
native events into `BackendEvent` instances; the orchestrator consumes
them from `backend.events`.

### Codex extraction

`CodexAppServer` moves to `floor/backends/codex.py` as `CodexBackend`.
Its constructor, `start`, `start_thread` → `open_role`, `start_turn` +
`steer_turn` → `deliver`, `interrupt_turn` → `interrupt`, `close_thread` →
`close_role`, `close`, and its notification reader all remain functionally
identical. The internal `_request`/`_notify` methods stay private.

The notification translation (`item/completed` → `role_message`,
`turn/started` → `turn_started`, `turn/completed` → `turn_completed`) moves
from `handle_notification` into the backend's async event iterator.

`InactiveTurn` stays in the orchestrator (it is a delivery-completion-race
concept, not a Codex concept) but the orchestrator now catches it from
`backend.deliver()` rather than from `codex.steer_turn()`.

### Backend factory

`floor/backends/__init__.py` provides:

```python
def create_backend(name: str, *, cwd: Path, project: Path,
                   broker_url: str, command: str | None = None,
                   solid_command: str = "solid",
                   model_callback_url: str | None = None) -> AgentBackend:
```

The `--codex-command` flag becomes `--backend-command` (still hidden from
help). The `--backend hermes` flag selects a Hermes ACP backend.

### Hermes backend ACP implementation

`floor/backends/hermes.py` defines `HermesBackend(AgentBackend)`. Its
`start()` launches `hermes acp` as a subprocess. `open_role()` calls
`session/new` then `session/prompt` with the role card and runtime context.
`deliver()` uses `session/prompt` when idle, redirects the active prompt
when the role is busy. Events translate from ACP `session/update`
notifications.

The initial cycle introduced this boundary as a structural outline. The
archived follow-on change
`2026-07-26-implement-hermes-backend-acp-integration` completed and verified
the real ACP subprocess implementation.

### RoleContext

The orchestrator constructs `RoleContext` from its current arguments:

```python
RoleContext(
    shop_checkout=str(arguments.cwd),
    active_project=str(prepared.project_root),
    model_callback_url=callback_url if role == "machinist" else None,
)
```

The backend is responsible for injecting runtime context into the agent
session in whatever form its protocol requires (developer instructions for
Codex, initial prompt for Hermes). The orchestrator does not know how to
format these.

### Test fixtures

`tests/fixtures/fake_codex_app_server.py` already implements the Codex
JSON-RPC surface as a fixture. It is adapted to also expose `AgentBackend`
methods. `tests/fixtures/fake_acp_server.py` implements a minimal ACP
fixture for Hermes backend testing. The orchestrator's existing acceptance
tests work against either fixture through the backend factory.

## Risks / Trade-offs

- **The protocol may leak one backend's shape** → Define operations by what
  the orchestrator needs, not by what one backend already exposes. If a new
  backend cannot implement `deliver()` with start/steer semantics, revisit
  the protocol rather than forcing the backend into Codex-shaped concepts.
- **Hermes ACP may evolve independently** → Keep wire behavior contained in
  `HermesBackend`, cover it with the strict fake ACP fixture, and retain a
  bounded live-process smoke check for protocol compatibility.
- **Extraction may break subtle Codex behaviour** → Preserve the existing
  test suite. Add red-green coverage for the extraction before moving any
  code.
- **Backend startup failure is under-specified** → `AgentBackend.start()`
  raises on failure; the orchestrator unwinds partial state. The same
  fail-closed discipline applies.

## Migration Plan

1. Define `AgentBackend`, `RoleHandle`, `RoleContext`, `BackendEvent`,
   `DeliveryReceipt` in `floor/backends/base.py` — green (no code calls it).
2. Add red tests that `ShopOrchestrator` works with a fake `AgentBackend`.
3. Extract `CodexAppServer` → `CodexBackend` without changing behaviour.
   Existing `fake_codex_app_server.py` tests stay green.
4. Replace `CodexControl` with `AgentBackend` in `ShopOrchestrator`.
   Move notification translation into the backend's event iterator.
5. Add `--backend` flag and `create_backend()` factory.
6. Add `floor/backends/hermes.py` and its factory entry; complete the ACP
   implementation in the recorded follow-on cycle.
7. Add `tests/fixtures/fake_acp_server.py`.
8. Run full Python suite, browser E2E, and manual open/direct/close exercise
   with `--backend codex`.

Rollback is one revert on the hermes-backend branch. Because the Codex
extraction preserves existing tests and behaviour, no production path is
incompatible.

## Open Questions

- Should the factory accept a backend-specific config path (`.codex/agents/*`
  for Codex, a different directory for Hermes), or should the backend
  discover its own configuration from the checkout? Discover for now; config
  injection can be added when needed.
- Should the `--backend` flag appear in `--help`? Yes — it is the user-facing
  switch. `--backend-command` stays hidden.
