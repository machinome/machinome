## Why

The `hermes-backend` branch implements a real `hermes acp` backend, but its
active-turn steering rests on matching English prose, its ratified spec
describes a cancellation sequence that is actively harmful against the shipped
Hermes, and two lifecycle paths are unbounded. A spike against the installed
`hermes` 0.19.0 (`spike/acp_turn_control.py`, evidence under `spike/evidence/`)
measured what Hermes actually does, and the results change the design.

Three findings drive this change:

1. **Hermes really does steer.** A second `session/prompt` on an active session
   is Hermes' steer surface. Hermes streams
   `"Redirected the active turn with your correction."` as an
   `agent_message_chunk`, answers the steer request immediately with a bare
   `{"stopReason": "end_turn"}`, and its own log records
   `Delivered /steer to agent after tool batch`. The original turn continued to
   completion (all 60 tool iterations ran) and the correction took effect inside
   that same turn before its response arrived. This is the ADR 0005 Codex
   `turn/steer` behaviour, not a weaker substitute — backend parity is real and
   should be preserved, not abandoned.

2. **`session/cancel` is broken in hermes 0.19.0.** Cancellation does abort the
   running tool cleanly (`exit_code 130`, `[Command interrupted]`, no orphaned
   process), but the pending `session/prompt` then fails with JSON-RPC `-32603
   Internal error: 'NoneType' object has no attribute 'startswith'` instead of
   returning `stopReason: "cancelled"`. It reproduces with `protocolVersion: 1`
   pinned, so it is not a negotiation artifact. Worse, the session stays
   wedged: a later prompt answers `"Queued for the next turn. (1 queued)"` and
   never runs. The currently ratified requirement — steer by cancelling and
   re-prompting — would therefore destroy the turn *and* the session.

3. **A cancelled turn currently crashes the shop.** That `-32603` response is
   translated to `role_failed` (`hermes.py:523`), which
   `ShopOrchestrator.handle_event` raises as `RuntimeError`
   (`orchestrator.py:126`), killing the event routing task and taking down the
   run. `interrupt()` and `close_role()` both send `session/cancel`, so the only
   interrupt path the shop has is also a shop-killer.

The prose matcher does function today — the acknowledgement chunk arrives
*before* the request response, so the adapter does read it in time. It is
fragile rather than broken. But the steer/steer-race decision does not need
prose at all: whether the original prompt is still outstanding is state the
shop already owns.

## What Changes

- Keep the second-`session/prompt` steer mechanism. Replace the prose match
  with the authoritative signal: if the original prompt has not yet responded,
  the correction was steered into that turn and the original delivery identity
  stands. Retain Hermes' acknowledgement text as a logged corroboration only,
  never as control flow.
- **BREAKING (ratified spec)**: remove `session/cancel` from the steer path.
  The requirement at `shop-agent-backend` currently mandates cancel-then-prompt;
  the spike shows that wedges the session. Steering SHALL NOT cancel.
- Normalize a cancelled turn so it is not a role failure: a `session/cancel`
  that ends a prompt with a transport error SHALL produce a cancellation
  outcome, not `role_failed`, so interrupting a role cannot terminate the run.
  Treat a cancelled Hermes session as spent — the shop uses `interrupt()` only
  while closing, and never returns a wedged session to standby.
- Stop clearing the original turn's assembled text when steering
  (`hermes.py:207`). The spike shows the original turn keeps running, so
  discarding its accumulated chunks drops foreman output that preceded the
  correction.
- Bound subprocess shutdown in both adapters: escalate `SIGTERM` to `SIGKILL`
  after a timeout. `hermes acp` exited cleanly on stdin close in every observed
  run, so this is defensive hardening of an unbounded `await
  self.process.wait()` (`hermes.py:267`, `codex.py:215`), not a fix for a
  reproduced hang.
- Separate the control-plane request timeout from the role-bootstrap prompt
  timeout, so a slow but healthy role-contract load cannot fail shop open on the
  shared 30-second budget (`hermes.py:396`).
- Rebuild `tests/fixtures/fake_acp_server.py` to replay the frame sequence the
  spike actually recorded — acknowledgement chunk, then an immediate bare
  `{"stopReason": "end_turn"}` with no `usage`, then the original prompt's real
  completion carrying `usage` — plus the `-32603` cancellation failure. The
  current fixture emits only the string the matcher looks for, which is why a
  green suite coexisted with an unverified design.
- Correct `docs/architecture-overview.md`, whose "Current status" section still
  says the multi-backend protocol and `--backend` flag are "proposed... but not
  yet implemented", contradicting both the shipped code and its own ADR 0006
  index entry.
- File the Hermes cancellation crash upstream as a wart. The shop's workaround
  stays until a fixed Hermes ships.

Not changed: the shop keeps advertising `protocolVersion: 1`. Hermes 0.19.0
answers `1` even when the client offers `2`, so ACP v2's `state_update:
running|idle` — the one clean idle signal — is unavailable. Targeting v2 is out
of scope here.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `shop-agent-backend`: replace the cancel-then-prompt steering requirement
  with steer-without-cancel; require that the steer/completion race be decided
  by outstanding-prompt state rather than agent prose; require that a cancelled
  turn yield a cancellation outcome rather than a role failure; require that a
  role-contract bootstrap not be bounded by the control-plane timeout; require
  that backend shutdown always release the subprocess.
- `shop-floor-lifecycle`: strengthen the close requirement so closing the shop
  releases the backend process even if it does not exit on `SIGTERM`, and so
  interrupting active work cannot itself end the run.

## Impact

- `floor/backends/hermes.py` — steer discriminator, cancellation normalization,
  chunk-preservation fix, timeout split, bounded shutdown.
- `floor/backends/codex.py` — bounded shutdown only; `turn/steer` unchanged.
- `floor/orchestrator.py` — cancellation must not raise from `handle_event`.
- `tests/fixtures/fake_acp_server.py`, `tests/test_orchestrator.py` — replay
  measured frames; add cancellation, bootstrap-timeout, and shutdown coverage.
- `docs/architecture-overview.md` — correct the stale status section.
- Likely ADR: steering is portable across both backends, but only because
  Hermes implements an off-spec extension; that dependency deserves a recorded
  decision. Confirmed during design.
- Evidence retained under `openspec/changes/.../spike/`. Single-run
  observations (n=1 per scenario); the fixture encodes the frames so future
  regressions are caught without live Hermes.
- No broker, frontend, or public API changes.
