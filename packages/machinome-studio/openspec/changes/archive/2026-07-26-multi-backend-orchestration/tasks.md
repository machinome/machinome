## 1. Define the AgentBackend protocol

- [x] 1.1 Create `floor/backends/__init__.py` with `create_backend()` factory stub.
- [x] 1.2 Create `floor/backends/base.py` with `AgentBackend` protocol,
  `RoleHandle`, `RoleContext`, `DeliveryReceipt`, and `BackendEvent` dataclasses.
- [x] 1.3 Verify `floor/backends/base.py` imports cleanly from the shop package
  (`python -c "from floor.backends.base import AgentBackend"`).

## 2. Add red acceptance tests for backend independence

- [x] 2.1 Create `tests/fixtures/fake_backend.py` — a minimal in-memory
  `AgentBackend` that records calls and emits configurable events.
- [x] 2.2 Add `tests/test_orchestrator.py` test: orchestrator opens with fake
  backend, manifests all three roles, broker roster shows waiting agents.
- [x] 2.3 Add test: direction envelope reaches backend.deliver() for correct
  role and includes the envelope body.
- [x] 2.4 Add test: backend `role_message` event records conversation entry
  in broker.
- [x] 2.5 Add test: orchestrator close interrupts active roles in reverse order
  then calls `backend.close()`.
- [x] 2.6 Add test: `backend_failed` event causes orchestrator to close cleanly.
- [x] 2.7 Observe lifecycle regressions red during the completion pass, then
  rerun the focused orchestrator suite green after implementation.

## 3. Extract CodexAppServer to CodexBackend

- [x] 3.1 Copy `CodexAppServer` (lines 172–346) from `floor/orchestrator.py`
  into `floor/backends/codex.py` as `CodexBackend`.
- [x] 3.2 Add `CodexBackend.events` async iterator that reads from
  `self.notifications` and translates each into a `BackendEvent`.
  Translation rules:
  - `item/completed` with `agentMessage` from foreman thread → `role_message`
  - `turn/started` → `turn_started`
  - `turn/completed` → `turn_completed`
- [x] 3.3 Add `CodexBackend.open_role()` wrapping `start_thread()`.
  Accept a `RoleContext` and inject runtime instructions as before.
- [x] 3.4 Add `CodexBackend.deliver()` wrapping `start_turn()`/`steer_turn()`.
  Return a `DeliveryReceipt`.
- [x] 3.5 Add `CodexBackend.interrupt()` wrapping `interrupt_turn()`.
- [x] 3.6 Add `CodexBackend.close_role()` wrapping `close_thread()`.
- [x] 3.7 Preserve required Codex behavior while extracting the backend and
  retain compatibility shims only where acceptance tests require them.
- [x] 3.8 Add a smoke test that `CodexBackend` implements the `AgentBackend`
  protocol shape (structural protocol check, no real process):
  `pytest tests/test_orchestrator.py -k "codex_backend_protocol" -v`.

## 4. Switch ShopOrchestrator to AgentBackend

- [x] 4.1 Replace `CodexControl` parameter with `AgentBackend` in
  `ShopOrchestrator.__init__`.
- [x] 4.2 Replace `RoleRuntime.thread_id` / `active_turn_id` with
  `RoleRuntime.handle` / `active_delivery_id`.
- [x] 4.3 Replace `self.codex.start_thread()` with
  `self.backend.open_role()`; pass `RoleContext` built from orchestrator args.
- [x] 4.4 Replace `self.codex.start_turn()` + `self.codex.steer_turn()` with
  `self.backend.deliver()`; return `DeliveryReceipt` and use its
  `delivery_id` for completion correlation.
- [x] 4.5 Replace `self.codex.interrupt_turn()` with
  `self.backend.interrupt()`.
- [x] 4.6 Replace `self.codex.close_thread()` with
  `self.backend.close_role()`.
- [x] 4.7 Replace `self.codex.close()` with `self.backend.close()`.
- [x] 4.8 Move notification handling from `handle_notification` to consuming
  `self.backend.events`. Replace `item/completed` → foreman message logic
  with `role_message` event handling. Replace `turn/started` /
  `turn/completed` tracking with `turn_started` / `turn_completed` events.
- [x] 4.9 Remove `CodexControl` protocol, `CodexAppServer`,
  `InactiveTurn` (now raised by backend.deliver(), keep the class),
  `BrokerControl` (keep `LocalBrokerControl`), and
  unused Codex imports from `floor/orchestrator.py`.
- [x] 4.10 Run fake-backend tests: `pytest tests/test_orchestrator.py -v`.
  Expected: fake-backend tests from step 2 now green.
- [x] 4.11 Run all non-browser Python tests green and confirm the remaining
  browser E2E failure reproduces unchanged on `main`.

## 5. Add --backend flag and factory

- [x] 5.1 Add `--backend` argument to `main()` in `floor/orchestrator.py`
  with `choices=("codex", "hermes")`, `default="codex"`.
- [x] 5.2 Implement `floor/backends/__init__.py`:
  `create_backend(name, *, cwd, project, broker_url, command, ...)`.
  For `"codex"`, construct and return a `CodexBackend`.
  For unknown names, raise `ValueError`.
- [x] 5.3 Replace the hard-coded `CodexBackend(...)` construction in `_serve`
  with `create_backend(arguments.backend, ...)`.
- [x] 5.4 Add red test: passing `--backend unknown` exits with error.
  `pytest tests/test_orchestrator.py -k "backend_unknown" -v`.
- [x] 5.5 Add red test: `--backend codex` runs the fake Codex fixture through
  the factory.
- [x] 5.6 Run the backend and orchestrator suites green.

## 6. Add HermesBackend structural outline

- [x] 6.1 Create `floor/backends/hermes.py` with `HermesBackend` implementing
  `AgentBackend`; the archived follow-on cycle completes its ACP behavior.
- [x] 6.2 Add `"hermes"` to the factory in `floor/backends/__init__.py`.
- [x] 6.3 Add `"hermes"` to the `--backend` choices in `main()`.
- [x] 6.4 Add red test: `--backend hermes` selects the Hermes backend
  (construction only, no process).
- [x] 6.5 Run the Hermes-focused orchestrator tests green.

## 7. Add ACP test fixture for Hermes backend testing

- [x] 7.1 Create `tests/fixtures/fake_acp_server.py` — an asyncio-based
  fixture that speaks newline-delimited JSON-RPC matching the ACP surface
  (`session/new`, `session/prompt`, `session/cancel`).
- [x] 7.2 Add acceptance test: orchestrator with `--backend hermes` opens and
  closes roles through the fake ACP fixture.
- [x] 7.3 Run the Hermes acceptance tests green.

## 8. Update architecture documentation (done by this change)

- [x] 8.1 ADR 0006: Generalize shop orchestration to a pluggable agent
  backend. ✓
- [x] 8.2 ADR 0005: Status updated to Superseded by 0006. ✓
- [x] 8.3 ADR index: 0006 added, 0005 updated. ✓
- [x] 8.4 `docs/architecture-overview.md`: Four-layer multi-backend
  architecture. ✓

## 9. Verify and commit

- [x] 9.1 Run all non-browser Python tests: 71 passed plus 23 subtests.
- [x] 9.2 Confirm the browser E2E failure is a pre-existing `main` baseline,
  not introduced by this backend-only branch.
- [x] 9.3 Run a bounded live Codex backend open/prompt/event/close smoke and
  observe `turn_started`, `role_message("SMOKE_OK")`, and `turn_completed`.
- [x] 9.4 Commit the original multi-backend implementation record.
