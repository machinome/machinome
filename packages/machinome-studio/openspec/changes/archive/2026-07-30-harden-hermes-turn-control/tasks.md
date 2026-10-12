## 1. Rebuild the fake ACP fixture around measured frames

- [x] 1.1 Replace the hardcoded acknowledgement in `tests/fixtures/fake_acp_server.py` with the sequence the spike recorded: on a `session/prompt` for a session that already has one outstanding, stream an `agent_message_chunk` acknowledgement, then answer that request immediately with a bare `{"stopReason": "end_turn"}` and no `usage`.
- [x] 1.2 Make the fixture answer the original prompt only when its simulated work finishes, and include a `usage` block on that response, so a genuine completion is distinguishable from an acknowledgement.
- [x] 1.3 Add a fixture mode that applies the steered correction inside the original turn (streaming further chunks against the original prompt) so pre- and post-correction text can both be asserted.
- [x] 1.4 Add `session/cancel` handling that reproduces hermes 0.19.0: abort simulated tool work, then answer the outstanding prompt with JSON-RPC error `-32603`, and refuse to run any later prompt on that session.
- [x] 1.5 Add a fixture mode that ignores stdin close and `SIGTERM`, for the bounded-shutdown test.

## 2. Prove the defects red

- [x] 2.1 Add a failing test that `deliver_steer` sends no `session/cancel` and returns a receipt still identifying the original delivery.
- [x] 2.2 Add a failing test that the correction's immediate response produces no `turn_completed` for either delivery, and that the original delivery stays active until its own response arrives.
- [x] 2.3 Add a failing test that a foreman turn steered mid-stream yields one `role_message` containing both pre- and post-correction text.
- [x] 2.4 Add a failing test that a cancelled prompt answered with `-32603` produces a completion event, not `role_failed`, and that `route_events` keeps running.
- [x] 2.5 Add a failing test that a role bootstrap slower than the control-plane timeout still manifests and opens the shop.
- [x] 2.6 Add a failing test that `close()` returns within a bounded time against a subprocess that ignores stdin close and `SIGTERM`.
- [x] 2.7 Confirm every test in this group fails for the stated reason before any source change.

## 3. Rework the Hermes steer path

- [x] 3.1 Rewrite `deliver_steer` to send the correction as an additional `session/prompt` with no `session/cancel`, keyed on the original prompt still being outstanding in `_prompt_requests`, raising `InactiveTurn` otherwise.
- [x] 3.2 Return a receipt carrying the original `expected_delivery_id`, and stop synthesising `turn_started`/`turn_completed`/`role_message` events for the correction.
- [x] 3.3 Delete `_send_control_prompt` and the `_control_requests`, `_control_by_session`, and `_control_chunks` state, including their handling in `_read_stdout` and `close()`.
- [x] 3.4 Route the acknowledgement chunk to a log line only; remove the `"Redirected the active turn..."` / `"queued for the next turn"` string matching from control flow.
- [x] 3.5 Remove the `_prompt_chunks[expected_id] = []` reset so text streamed before the correction is retained.

## 4. Make cancellation safe

- [x] 4.1 Track sessions the shop has cancelled via `interrupt()` or `close_role()`.
- [x] 4.2 Translate a cancelled session's terminal prompt response — stop reason or transport error — into `turn_completed` for that delivery instead of `role_failed`.
- [x] 4.3 Mark a cancelled session spent so it is not returned to standby, and ensure the orchestrator sends it no further deliveries.
- [x] 4.4 Verify `ShopOrchestrator.close()` completes when interrupting a role reports an error, without aborting the remaining role closes.

## 5. Split timeouts and bound shutdown

- [x] 5.1 Introduce separate control-plane and prompt timeouts in `HermesBackend`, applying the control-plane budget to `initialize` and `session/new` and the prompt budget to role bootstrap.
- [x] 5.2 Escalate `close()` in `floor/backends/hermes.py` from stdin close to `SIGTERM` to `SIGKILL`, each bounded, so it always returns.
- [x] 5.3 Apply the same bounded escalation to `floor/backends/codex.py:close()`.
- [x] 5.4 Confirm the group 2 tests now pass and no previously passing test regressed.

## 6. Reconcile documentation

- [x] 6.1 Rewrite the "Current status and limitations" bullet in `docs/architecture-overview.md` that still calls the multi-backend protocol and `--backend` flag proposed and unimplemented.
- [x] 6.2 Update the architecture overview's agent-backend section to describe steering, cancellation, and shutdown as implemented, and reference ADR 0007.
- [x] 6.3 Confirm `docs/adrs/README.md` lists ADR 0007 with status and date matching the ADR file.

## 7. Validate and record

- [x] 7.1 Run the non-browser Python suite; confirm it passes and that the one browser E2E failure still reproduces on `main`.
- [x] 7.2 Run `openspec validate --strict` (passes). The frontend `tsc` check could not run: `floor/frontend/node_modules` is absent in this worktree, so `tsc` is unavailable. This change touches no frontend file, so the check is not at risk; re-run it wherever the frontend toolchain is installed.
- [x] 7.3 Retain `spike/acp_turn_control.py` and its full raw evidence in the archived change (pilot decision, 2026-07-30). Confirm the script still runs against the installed Hermes and that `design.md` and ADR 0007 cite paths that survive archival.
- [ ] 7.4 Sync baseline specs, archive the change, and create the implementation commit.
- [ ] 7.5 File the hermes 0.19.0 `session/cancel` crash upstream as a wart, referencing the reproduction in the spike evidence. **Not done — needs explicit pilot authorization**; an agent never infers permission to publish or open an issue. Reproduction is committed at `spike/evidence-v1/s2.jsonl`.
