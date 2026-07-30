## 1. Build the fake Claude CLI fixture around measured frames

- [ ] 1.1 Add `tests/fixtures/fake_claude_cli.py` speaking the stream-json frames the spike recorded: a `system/init` frame, `assistant` frames carrying text and `tool_use` blocks, `user` frames carrying `tool_result`, and one `result` frame per exchange.
- [ ] 1.2 Make the fixture hold a turn open across a simulated tool call so a correction can be sent while a delivery is outstanding.
- [ ] 1.3 Make the fixture inject queued input at the next tool boundary and answer the whole exchange with exactly one `result`, matching all 14 observed steer runs.
- [ ] 1.4 Add `control_request`/`interrupt` handling that answers `{"subtype":"success","response":{"still_queued":[]}}`, ends the turn with `is_error: true` and `terminal_reason: "aborted_tools"`, and leaves the session able to run a further turn.
- [ ] 1.5 Add a fixture mode that ignores stdin close and `SIGTERM`, for the bounded multi-process shutdown test.
- [ ] 1.6 Record in the fixture docstring that it cannot cover model compliance, and point at ADR 0009.

## 2. Prove the new behaviour red

- [ ] 2.1 Add a failing test that `--backend claude` selects the Claude backend and that an unknown backend still exits before starting anything.
- [ ] 2.2 Add a failing test that `open_role()` starts one process per role, with the active project as cwd, and that the session's first user message is a broker envelope.
- [ ] 2.3 Add a failing test that a delivery is completed under the identifier the backend minted, with no vendor turn identifier available.
- [ ] 2.4 Add a failing test that steering an outstanding delivery returns a receipt still identifying it and yields exactly one completion.
- [ ] 2.5 Add a failing test that a correction sent after completion becomes a new delivery rather than raising `InactiveTurn`.
- [ ] 2.6 Add a failing test that an interrupted turn produces a completion, not `role_failed`, and that `route_events` keeps running.
- [ ] 2.7 Add a failing test that one role process exiting yields `role_failed` for that role, not `backend_failed`.
- [ ] 2.8 Add a failing test that a failure while opening the second of three roles releases the already-started processes.
- [ ] 2.9 Add a failing test that `close()` returns within a bounded time when one of several role processes ignores stdin close and `SIGTERM`, and that the others are still released.
- [ ] 2.10 Confirm every test in this group fails for the stated reason before any source change.

## 3. Move `InactiveTurn` to the portable contract

- [ ] 3.1 Move `InactiveTurn` from `floor/backends/codex.py` to `floor/backends/base.py`.
- [ ] 3.2 Update `floor/backends/codex.py`, `floor/backends/hermes.py`, and `floor/orchestrator.py` to import it from `base`, leaving behaviour unchanged.
- [ ] 3.3 Confirm the existing Codex and Hermes suites still pass unchanged.

## 4. Implement the Claude backend

- [ ] 4.1 Add `floor/backends/claude.py` with a `ClaudeBackend` implementing `AgentBackend`, owning one `claude` subprocess per role, and register it as `claude`.
- [ ] 4.2 Launch each role with non-interactive streaming input and output, the active project as cwd, and the broker environment the other backends pass.
- [ ] 4.3 Deliver the role contract through the session's system-prompt channel, reading `model:` and `tools:` from the role card frontmatter; add no per-role adapter file.
- [ ] 4.4 Include the trust framing required by ADR 0009 in the role contract, and add a module comment recording that any non-envelope user message moves the session into the measured 0/3 condition.
- [ ] 4.5 Open sessions with operator-machine customization disabled, and record in the module why `--bare` is not used.
- [ ] 4.6 Mint delivery identifiers, correlate them positionally to `result` frames under the per-role delivery lock, and emit `turn_started`/`turn_completed` accordingly.
- [ ] 4.7 Implement `deliver_steer` as a mid-turn user frame that preserves the outstanding delivery identity and never raises `InactiveTurn`.
- [ ] 4.8 Implement `interrupt()` as a `control_request`, translating the aborted result into `turn_completed`.
- [ ] 4.9 Implement `close_role()` and `close()` with per-process escalation from stdin close to `SIGTERM` to `SIGKILL`, each bounded.
- [ ] 4.10 Emit `role_failed` for a single role process exiting and reserve `backend_failed` for a fault that ends the run.
- [ ] 4.11 Add `claude` to the `--backend` choices in `floor/orchestrator.py`.
- [ ] 4.12 Confirm the group 2 tests now pass and no previously passing test regressed.

## 5. Reconcile documentation

- [ ] 5.1 Correct the one-process-per-backend statement in `floor/backends/base.py` to the ownership requirement.
- [ ] 5.2 Rewrite the agent-backend section of `docs/architecture-overview.md` for three backends, including the differing process models, delivery-identity sources, and interrupt fidelities.
- [ ] 5.3 Add ADR 0008 and ADR 0009 to `docs/adrs/README.md` with status and date matching the ADR files, preserving chronological order.
- [ ] 5.4 Note in ADR 0006 that its process-model statement is amended by ADR 0008, without rewriting its decision.

## 6. Validate and record

- [ ] 6.1 Run the non-browser Python suite; confirm it passes and that any pre-existing browser E2E failure still reproduces on `main`.
- [ ] 6.2 Run `openspec validate --strict`.
- [ ] 6.3 Confirm `spike/claude_turn_control.py` still runs against the installed `claude`, and that `design.md`, ADR 0008, and ADR 0009 cite spike paths that survive archival.
- [ ] 6.4 Sync baseline specs, archive the change, and create the implementation commit.
- [ ] 6.5 Re-run the spike and record its table whenever the installed Claude Code version or a role's model changes. **Not a one-time task** — ADR 0009 makes this the regression check for the half the fixture cannot cover.
