## 1. Implement HermesBackend JSON-RPC plumbing

- [ ] 1.1 Add subprocess management to `HermesBackend`: `self.process`, `self.notifications`, `self._pending`, `self._next_id`, `self._reader_task`, `self._stderr_task`, `self._handles` (session_id → role mapping).
- [ ] 1.2 Copy `_request`/`_notify`/`_read_stdout`/`_drain_stderr` from `CodexBackend` into `HermesBackend`, adapting method names only.
- [ ] 1.3 Add `self.events` async iterator.

## 2. Implement AgentBackend methods

- [ ] 2.1 `start()`: Launch `hermes acp` subprocess with `HERMES_ACP_SKIP_CONFIGURED_MCP=1` in the environment. Send `initialize` request with protocol version and capabilities. Wait for response.
- [ ] 2.2 `open_role(role, context)`: Send `session/new` with `cwd=context.active_project`. Store `session_id → (role, session_id)` in `self._handles`. Send initial `session/prompt` with role card and context as a text content block (fire-and-forget, no response awaited). Return `RoleHandle(backend_id=session_id, role=role)`.
- [ ] 2.3 `deliver_start(handle, message)`: Send `session/prompt` with the message as a text content block. Return `DeliveryReceipt(delivery_id=str(request_id), accepted=True)`.
- [ ] 2.4 `deliver_steer(handle, expected_delivery_id, message)`: Check if `expected_delivery_id` still matches the active prompt. If not, raise `InactiveTurn`. Send `session/cancel` notification. Send new `session/prompt` with the correction. Return `DeliveryReceipt(delivery_id=str(new_request_id), accepted=True)`.
- [ ] 2.5 `interrupt(handle)`: Send `session/cancel` notification.
- [ ] 2.6 `close_role(handle)`: Send `session/cancel` notification (ACP sessions have no explicit close beyond cancel).
- [ ] 2.7 `close()`: Close stdin, wait for process exit with timeout, terminate on timeout. Await reader/stderr tasks.

## 3. Event translation

- [ ] 3.1 Add `_translate_notification(message)` method that maps ACP server-to-client messages to `BackendEvent`.
- [ ] 3.2 `session/update` with `agentMessage` and foreman session → `BackendEvent(kind="role_message", role="foreman", text=...)`.
- [ ] 3.3 `session/prompt` response with `stopReason` → `BackendEvent(kind="turn_completed", role=..., delivery_id=...)`.
- [ ] 3.4 `session/prompt` request dispatched → `BackendEvent(kind="turn_started", role=..., delivery_id=...)`.

## 4. Acceptance tests

- [ ] 4.1 Add `HermesBackendAcceptanceTest` to `tests/test_orchestrator.py`: create `HermesBackend` with `command=(sys.executable, str(FAKE_ACP_SERVER))`, call `start()`, `open_role()` for all three roles, `deliver()`, `close()`. Assert each operation succeeds through the fake ACP fixture.
- [ ] 4.2 Add test: `HermesBackend` with fake ACP fixture manifests all three roles and broker roster shows waiting agents.
- [ ] 4.3 Add test: direction envelope reaches `deliver()` for correct role with body.
- [ ] 4.4 Add test: `close()` interrupts active roles and terminates the subprocess.
- [ ] 4.5 Run: `pytest tests/test_orchestrator.py -v`. All existing tests green; new Hermes tests green.

## 5. Update archived design document

- [ ] 5.1 Amend `openspec/changes/archive/2026-07-26-multi-backend-orchestration/design.md` Non-Goals: remove "Implementing the full HermesBackend as a working Hermes ACP client" from non-goals. Add note that this follow-on change completes the implementation.

## 6. Verify

- [ ] 6.1 Run full Python test suite: `pytest tests/ -v`. Expected: green.
- [ ] 6.2 Manual smoke test: `python -m floor.orchestrator PROJECT --backend hermes --port 9000 --backend-command "hermes acp"` against a real Hermes process. Open shop, verify roles manifest, close shop.
- [ ] 6.3 Commit with message: `feat: implement HermesBackend ACP integration over hermes acp subprocess`
