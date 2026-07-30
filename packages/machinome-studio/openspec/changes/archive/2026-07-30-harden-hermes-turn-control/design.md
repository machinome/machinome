## Context

`hermes-backend` (HEAD `0e03a85`) ships a working `hermes acp` adapter whose own
commit message declares it not merge-ready. Verification against `main`
confirmed the procedural claims: 78 non-browser tests pass, the one browser E2E
failure reproduces on `main`, and both OpenSpec cycles are archived. The
blockers are behavioural.

A spike (`spike/acp_turn_control.py`, evidence in `spike/evidence/` and
`spike/evidence-v1/`) measured `hermes` 0.19.0 directly. It replaced guesswork
with four facts:

1. **Hermes steers, and the ACP spec does not describe how.** A second
   `session/prompt` on a busy session is Hermes' steer surface. Observed frames,
   in order and within the same 10 ms: the correction request out; an
   `agent_message_chunk` reading `"Redirected the active turn with your
   correction."`; then the correction's response, a bare
   `{"stopReason": "end_turn"}` with no `usage`. Hermes' own log later recorded
   `Delivered /steer to agent after tool batch`. The original 60-iteration tool
   call ran to completion, the correction then took effect *inside* that turn
   (`result.txt` = `REDIRECTED`), and only afterwards did the original prompt
   respond — with `usage`. This is ADR 0005 Codex `turn/steer` behaviour.

2. **`session/cancel` is unusable for steering on 0.19.0.** The tool aborts
   correctly (`exit_code 130`, `[Command interrupted]`, no orphan), but the
   pending prompt then fails with `-32603 Internal error: 'NoneType' object has
   no attribute 'startswith'`. Reproduced with `protocolVersion: 1` pinned, so
   not a negotiation artifact. The session is then wedged: the next prompt
   answers `"Queued for the next turn. (1 queued)"` and never runs.

3. **A cancelled turn currently kills the run.** `hermes.py:523` maps that error
   response to `role_failed`; `orchestrator.py:126` raises `RuntimeError` on
   `role_failed`, killing the event-routing task, which `_wait_for_runtime`
   turns into a shop failure.

4. **Hermes 0.19.0 negotiates ACP `protocolVersion: 1`** even when offered `2`.
   So v2's `state_update: running|idle` — the only clean idle signal in the
   protocol — does not exist here.

Constraint worth stating plainly: the shop's steering parity rests on
undocumented Hermes behaviour. All observations are n=1 per scenario.

## Goals / Non-Goals

**Goals:**

- Preserve Codex/Hermes steering parity, which the spike shows is real.
- Make the steer/race decision deterministic from state the shop owns.
- Ensure cancelling or interrupting a role can never end the shop run.
- Bound every close path.
- Make the ACP fixture replay measured frames so the suite can fail.

**Non-Goals:**

- Migrating to ACP v2. Hermes 0.19.0 does not offer it.
- Fixing Hermes. The cancellation crash goes upstream as a wart; the shop
  works around it.
- Restart or session recovery after a wedged session. Consistent with ADR 0005,
  losing a session closes the run rather than reattaching.
- Changing Codex `turn/steer`, the broker, or the frontend.

## Decisions

### D1: Steer by second prompt; never cancel

Send the correction as an additional `session/prompt` and send no
`session/cancel`. *Alternative rejected:* the currently ratified
cancel-then-reprompt sequence — the spike proves it destroys the turn and wedges
the session. *Alternative rejected:* declining to steer Hermes and queueing until
idle — Hermes already queues internally and applies the correction at the next
tool-batch boundary, so declining would discard a working capability.

### D2: Decide the race on outstanding-prompt state, not prose

`deliver_steer` treats the correction as steered if the original prompt is still
outstanding in `_prompt_requests`; otherwise it raises `InactiveTurn`. The
existing string match on `"Redirected the active turn..."` becomes a logged
corroboration only.

Note for the record: that matcher does *work* today — the acknowledgement chunk
is read before the response resolves, so the earlier suspicion that it could
never fire was wrong. It is replaced because it couples control flow to a
user-facing sentence, not because it is currently broken.

*Alternative rejected:* discriminating on the absent `usage` block in the steer
response. It is a real structural difference but an incidental one, undocumented
and easy for Hermes to change.

### D3: The steer response is an acknowledgement, not a completion

The correction's immediate `{"stopReason": "end_turn"}` must not produce
`turn_completed`. Only the original prompt's response ends the turn, so the
active delivery identity stays `expected_id` throughout. This drops
`_send_control_prompt` and the `_control_requests` / `_control_by_session` /
`_control_chunks` state entirely.

Consequence: post-acknowledgement chunks land on the original turn's buffer,
which is now provably correct — the correction executes inside that turn. The
"misattribution leak" named in the previous proposal was a misreading and is
withdrawn.

**Amended during implementation.** The first attempt suppressed *all* chunks on
a session between sending a correction and reading its acknowledgement. A
red-first test caught that this drops genuine turn output: `turn_started` is
queued before the write is drained, so a correction can be sent while the
turn's earlier text is still unread, and session-scoped suppression eats it.
The two cannot be told apart from session state — both directions are
independent streams, so a chunk read after our write may have been emitted
before it.

The acknowledgement is therefore filtered by its known text
(`STEER_ACKNOWLEDGEMENTS`), and only while a correction is outstanding on that
session. This does use Hermes' prose, but for *content filtering*, never for
control flow, which is the line ADR 0007 draws. It also degrades in the safe
direction: if Hermes rewords the acknowledgement, a stray sentence reaches the
conversation while turn output and delivery identity stay correct. The
alternative loses real work.

### D4: Stop discarding pre-steer output

Remove the `_prompt_chunks[expected_id] = []` reset (`hermes.py:207`). It was
written on the assumption that steering replaced the turn. The turn survives, so
the reset silently drops foreman text that streamed before the correction.

### D5: Normalize cancellation instead of failing the role

A prompt that the shop itself cancelled completes its delivery, whether the
subprocess reports a stop reason or the 0.19.0 transport error. Track sessions
the shop has cancelled and translate their terminal response to `turn_completed`
rather than `role_failed`. Because a cancelled Hermes session is wedged, an
interrupted session is marked spent and never returned to standby — which is
acceptable given `interrupt()` is only called while closing.

*Alternative rejected:* matching on the `'NoneType'... startswith` error text.
That is a Hermes stack-trace detail and would silently stop matching once fixed.
Keying on "we cancelled this session" is our own state and survives the fix.

### D6: Two timeout classes

Control-plane requests (`initialize`, `session/new`) keep a short budget and
fail fast. Prompt work — the role bootstrap above all — gets a much longer,
separately configurable budget. A single 30 s budget currently governs both, and
a bootstrap that reads a role card plus every named skill will exceed it,
failing shop open.

### D7: Bounded shutdown, honestly labelled

Escalate stdin close → `SIGTERM` → `SIGKILL`, each bounded. `hermes acp` exited
rc=0 on stdin close in every observed run, including with a live tool call, so
this is defensive: the unbounded `await self.process.wait()` after `terminate()`
(`hermes.py:267`, `codex.py:215`) is a latent hazard, not a reproduced hang. The
spike's teardown probe is the regression harness for it.

### D8: Record the off-spec dependency as an ADR

Parity depends on behaviour no ACP version specifies. ADR 0007 records the
decision, what evidence supports it, and the detection strategy if a Hermes
release removes it.

## Risks / Trade-offs

- **Hermes could drop second-prompt steering in any release** → ADR 0007 records
  the dependency; the fixture replays the measured frames, so the suite fails
  loudly rather than degrading silently. Fallback is delivery-after-idle, which
  costs latency but not correctness.
- **n=1 per scenario** → the fixture encodes observed frames; a re-run of the
  spike is cheap and scripted. Timing-sensitive conclusions (acknowledgement
  chunk before response) are the ones to re-check first.
- **A wedged session after cancel is unrecoverable** → confined to close, where
  the process dies anyway. Accepted, consistent with ADR 0005's no-recovery
  stance.
- **Interrupt is now effectively close-only** → the shop loses any future
  "abort this turn and keep working" capability on Hermes until upstream is
  fixed. Named in the wart.
- **Longer bootstrap budget delays detection of a genuinely hung role** →
  control-plane liveness stays short, so only prompt work waits.

## Migration Plan

No data or interface migration. The change lands on
`hermes-backend-harden-turn-control`, branched from `hermes-backend` HEAD, and
integrates back into `hermes-backend`. Rollback is discarding the branch;
nothing outside it is touched. `main` remains unaffected, and `hermes-backend`
remains unmerged pending this work.

## Open Questions

- Should `--backend hermes` carry an explicit experimental marker at the CLI
  until the upstream cancellation bug is fixed? Deferred to the pilot; not
  required by any requirement here.
- Does the machinist's `solid develop` callback survive a steer that arrives
  mid-build? Untested — the spike used a synthetic tool call, not a real
  project. Worth a follow-up once a live Hermes shop runs.
