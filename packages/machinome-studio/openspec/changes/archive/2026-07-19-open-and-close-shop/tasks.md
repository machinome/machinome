## 1. Review and ratification

- [x] 1.1 Ratify the rewritten `shop-floor-lifecycle` behavioral specification.
- [x] 1.2 Ratify or revise the remaining minimal-browser-surface decision in `design.md`.

## 2. Independent shop-floor foundation

- [x] 2.1 Create the new FastAPI shop-floor application structure and its test setup in this worktree.
- [x] 2.2 Provide a minimal browser page that displays the current shop lifecycle state.
- [x] 2.3 Add a Server-Sent Events lifecycle-status stream that stays open while the FastAPI service is running and supplies its open state on each connection.
- [x] 2.4 Make the browser page display `Shop is closed` when its SSE connection is lost and `Shop is open` when it reconnects, without reloading.
- [x] 2.5 Add the Codex-operated command or interface that opens the FastAPI service at its stable browser location only after it is available.
- [x] 2.6 Add the Codex-operated command or interface that closes the FastAPI service.

## 3. Lifecycle evidence

- [x] 3.1 Add red-first automated coverage for successful opening, opening failure, and closing.
- [x] 3.2 Add red-first browser evidence for open, shutdown-to-closed, and restart-to-open SSE status transitions without a page reload.
- [x] 3.3 Run the project regression suite and record any environmental limitation honestly.
- [x] 3.4 Manually verify the open, shutdown-to-closed, and restart-to-open lifecycle states in one browser page.
