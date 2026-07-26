## 1. Define the AgentBackend protocol

- [ ] 1.1 Create `floor/backends/__init__.py` with `create_backend()` factory stub.
- [ ] 1.2 Create `floor/backends/base.py` with `AgentBackend` protocol,
  `RoleHandle`, `RoleContext`, `DeliveryReceipt`, and `BackendEvent` dataclasses.
- [ ] 1.3 Verify `floor/backends/base.py` imports cleanly from the shop package
  (`python -c "from floor.backends.base import AgentBackend"`).

## 2. Add red acceptance tests for backend independence

- [ ] 2.1 Create `tests/fixtures/fake_backend.py` — a minimal in-memory
  `AgentBackend` that records calls and emits configurable events.
- [ ] 2.2 Add `tests/test_orchestrator.py` test: orchestrator opens with fake
  backend, manifests all three roles, broker roster shows waiting agents.
- [ ] 2.3 Add test: direction envelope reaches backend.deliver() for correct
  role and includes the envelope body.
- [ ] 2.4 Add test: backend `role_message` event records conversation entry
  in broker.
- [ ] 2.5 Add test: orchestrator close interrupts active roles in reverse order
  then calls `backend.close()`.
- [ ] 2.6 Add test: `backend_failed` event causes orchestrator to close cleanly.
- [ ] 2.7 Run red suite: `pytest tests/test_orchestrator.py -k "fake_backend" -v`.
  Expected: tests fail because `ShopOrchestrator` still depends on `CodexControl`.

## 3. Extract CodexAppServer to CodexBackend

- [ ] 3.1 Copy `CodexAppServer` (lines 172–346) from `floor/orchestrator.py`
  into `floor/backends/codex.py` as `CodexBackend`.
- [ ] 3.2 Add `CodexBackend.events` async iterator that reads from
  `self.notifications` and translates each into a `BackendEvent`.
  Translation rules:
  - `item/completed` with `agentMessage` from foreman thread → `role_message`
  - `turn/started` → `turn_started`
  - `turn/completed` → `turn_completed`
- [ ] 3.3 Add `CodexBackend.open_role()` wrapping `start_thread()`.
  Accept a `RoleContext` and inject runtime instructions as before.
- [ ] 3.4 Add `CodexBackend.deliver()` wrapping `start_turn()`/`steer_turn()`.
  Return a `DeliveryReceipt`.
- [ ] 3.5 Add `CodexBackend.interrupt()` wrapping `interrupt_turn()`.
- [ ] 3.6 Add `CodexBackend.close_role()` wrapping `close_thread()`.
- [ ] 3.7 Keep `CodexControl` protocol, `CodexAppServer`, `InactiveTurn`,
  `BrokerControl`, `LocalBrokerControl`, `RoleRuntime` in
  `floor/orchestrator.py` unchanged. Run full test suite:
  `pytest tests/ -v`. Expected: all existing tests still green.
- [ ] 3.8 Add a smoke test that `CodexBackend` implements the `AgentBackend`
  protocol shape (structural protocol check, no real process):
  `pytest tests/test_orchestrator.py -k "codex_backend_protocol" -v`.

## 4. Switch ShopOrchestrator to AgentBackend

- [ ] 4.1 Replace `CodexControl` parameter with `AgentBackend` in
  `ShopOrchestrator.__init__`.
- [ ] 4.2 Replace `RoleRuntime.thread_id` / `active_turn_id` with
  `RoleRuntime.handle` / `active_delivery_id`.
- [ ] 4.3 Replace `self.codex.start_thread()` with
  `self.backend.open_role()`; pass `RoleContext` built from orchestrator args.
- [ ] 4.4 Replace `self.codex.start_turn()` + `self.codex.steer_turn()` with
  `self.backend.deliver()`; return `DeliveryReceipt` and use its
  `delivery_id` for completion correlation.
- [ ] 4.5 Replace `self.codex.interrupt_turn()` with
  `self.backend.interrupt()`.
- [ ] 4.6 Replace `self.codex.close_thread()` with
  `self.backend.close_role()`.
- [ ] 4.7 Replace `self.codex.close()` with `self.backend.close()`.
- [ ] 4.8 Move notification handling from `handle_notification` to consuming
  `self.backend.events`. Replace `item/completed` → foreman message logic
  with `role_message` event handling. Replace `turn/started` /
  `turn/completed` tracking with `turn_started` / `turn_completed` events.
- [ ] 4.9 Remove `CodexControl` protocol, `CodexAppServer`,
  `InactiveTurn` (now raised by backend.deliver(), keep the class),
  `BrokerControl` (keep `LocalBrokerControl`), and
  unused Codex imports from `floor/orchestrator.py`.
- [ ] 4.10 Run fake-backend tests: `pytest tests/test_orchestrator.py -v`.
  Expected: fake-backend tests from step 2 now green.
- [ ] 4.11 Run full test suite: `pytest tests/ -v`. Expected: all existing
  broker, CLI, E2E, and orchestrator tests still green.

## 5. Add --backend flag and factory

- [ ] 5.1 Add `--backend` argument to `main()` in `floor/orchestrator.py`
  with `choices=("codex",)`, `default="codex"`.
- [ ] 5.2 Implement `floor/backends/__init__.py`:
  `create_backend(name, *, cwd, project, broker_url, command, ...)`.
  For `"codex"`, construct and return a `CodexBackend`.
  For unknown names, raise `ValueError`.
- [ ] 5.3 Replace the hard-coded `CodexBackend(...)` construction in `_serve`
  with `create_backend(arguments.backend, ...)`.
- [ ] 5.4 Add red test: passing `--backend unknown` exits with error.
  `pytest tests/test_orchestrator.py -k "backend_unknown" -v`.
- [ ] 5.5 Add red test: `--backend codex` runs the fake Codex fixture through
  the factory.
- [ ] 5.6 Run full test suite: `pytest tests/ -v`. Expected: green.

## 6. Add HermesBackend structural outline

- [ ] 6.1 Create `floor/backends/hermes.py` with `HermesBackend` class
  implementing `AgentBackend`. Each method raises `NotImplementedError`
  with a descriptive message.
- [ ] 6.2 Add `"hermes"` to the factory in `floor/backends/__init__.py`.
- [ ] 6.3 Add `"hermes"` to the `--backend` choices in `main()`.
- [ ] 6.4 Add red test: `--backend hermes` selects the Hermes backend
  (construction only, no process).
- [ ] 6.5 Run test: `pytest tests/test_orchestrator.py -k "hermes" -v`.

## 7. Add ACP test fixture for Hermes backend testing

- [ ] 7.1 Create `tests/fixtures/fake_acp_server.py` — an asyncio-based
  fixture that speaks newline-delimited JSON-RPC matching the ACP surface
  (`session/new`, `session/prompt`, `session/cancel`).
- [ ] 7.2 Add acceptance test: orchestrator with `--backend hermes` opens and
  closes roles through the fake ACP fixture.
- [ ] 7.3 Run: `pytest tests/test_orchestrator.py -k "hermes_orchestration" -v`.

## 8. Update architecture documentation (done by this change)

- [ ] 8.1 ADR 0006: Generalize shop orchestration to a pluggable agent
  backend. ✓
- [ ] 8.2 ADR 0005: Status updated to Superseded by 0006. ✓
- [ ] 8.3 ADR index: 0006 added, 0005 updated. ✓
- [ ] 8.4 `docs/architecture-overview.md`: Four-layer multi-backend
  architecture. ✓

## 9. Verify and commit

- [ ] 9.1 Run full Python test suite: `pytest tests/ -v`.
- [ ] 9.2 Run browser E2E: `scripts/test-e2e`.
- [ ] 9.3 Manual exercise: `python -m floor.orchestrator PROJECT --backend codex --port 9000`.
  Open shop, send maker message via browser, close shop.
- [ ] 9.4 Commit with message: `feat: add pluggable agent backend protocol and --backend flag`
