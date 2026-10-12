## 1. Implement HermesBackend JSON-RPC plumbing

- [x] 1.1 Add subprocess management to `HermesBackend`: `self.process`, `self.notifications`, `self._pending`, `self._next_id`, `self._reader_task`, `self._stderr_task`, `self._handles` (session_id → role mapping).
- [x] 1.2 Implement `_request`/`_notify`/`_read_stdout`/`_drain_stderr` JSON-RPC plumbing in `HermesBackend`.
- [x] 1.3 Add `self.events` async iterator.

## 2. Implement AgentBackend methods

- [x] 2.1 `start()`: Launch `hermes acp` subprocess with `HERMES_ACP_SKIP_CONFIGURED_MCP=1` in the environment. Send `initialize` request with protocol version and capabilities. Wait for response.
- [x] 2.2 `open_role(role, context)`: Send `session/new` with `cwd=context.active_project`. Store `session_id → (role, session_id)` in `self._handles`. Send and await an initial `session/prompt` that loads the role card, named skills, and runtime context before returning `RoleHandle(backend_id=session_id, role=role)`.
- [x] 2.3 `deliver_start(handle, message)`: Send `session/prompt` with the message as a text content block. Return `DeliveryReceipt(delivery_id=str(request_id), accepted=True)`.
- [x] 2.4 `deliver_steer(handle, expected_delivery_id, message)`: Check if `expected_delivery_id` still matches the active prompt. If not, raise `InactiveTurn`. Send `session/cancel` notification. Send new `session/prompt` with the correction. Return `DeliveryReceipt(delivery_id=str(new_request_id), accepted=True)`.
- [x] 2.5 `interrupt(handle)`: Send `session/cancel` notification.
- [x] 2.6 `close_role(handle)`: Send `session/cancel` notification (ACP sessions have no explicit close beyond cancel).
- [x] 2.7 `close()`: Close stdin, wait for process exit with timeout, terminate on timeout. Await reader/stderr tasks.

## 3. Event translation

- [x] 3.1 Translate ACP server-to-client messages and prompt responses into portable `BackendEvent` values.
- [x] 3.2 Assemble streamed `session/update` `agent_message_chunk` text for the foreman session → one `BackendEvent(kind="role_message", role="foreman", text=...)` before prompt completion.
- [x] 3.3 `session/prompt` response with `stopReason` → `BackendEvent(kind="turn_completed", role=..., delivery_id=...)`.
- [x] 3.4 `session/prompt` request dispatched → `BackendEvent(kind="turn_started", role=..., delivery_id=...)`.

## 4. Acceptance tests

- [x] 4.1 Add `HermesBackendAcceptanceTest` using the fake ACP fixture through the full role lifecycle.
- [x] 4.2 Test that all three Hermes roles manifest and the broker roster shows waiting agents.
- [x] 4.3 Test prompt delivery, streamed foreman output, completion identity, active steering, and inactive-turn races.
- [x] 4.4 Test interruption, unexpected process failure, and subprocess cleanup.
- [x] 4.5 Run the focused orchestrator suite green.

## 5. Update archived design document

- [x] 5.1 Amend the archived multi-backend design to record the completed real ACP implementation.

## 6. Verify

- [x] 6.1 Run all non-browser Python tests: 71 passed plus 23 subtests; confirm the remaining browser E2E failure reproduces on `main`.
- [x] 6.2 Run bounded live Hermes ACP initialization, role bootstrap, prompt, streamed `role_message("SMOKE_OK")`, correlated completion, and clean close.
- [x] 6.3 Commit the original Hermes ACP implementation record.
