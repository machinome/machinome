# ADR 0007: Depend on Hermes' off-spec second-prompt steering for active-turn corrections

**Status:** Superseded by [ADR 0016](./0016-retire-hermes-agent-backend.md)

**Date:** 2026-07-30

**Origin:** OpenSpec change `harden-hermes-turn-control`

## Context

ADR 0005 established that a maker's correction must reach a role that is already
working, and that Codex provides this through `turn/steer` on the owning
app-server: the correction is queued inside the active turn and becomes visible
at the next model boundary. ADR 0006 generalized orchestration to a pluggable
backend, which required the same guarantee from Hermes over ACP.

The Agent Client Protocol does not define a way to inject input into a running
prompt turn. Neither v1 nor the v2 draft has a steer primitive. What v1 offers is
`session/prompt` and `session/cancel`; the v2 draft adds `state_update:
running|idle` but Hermes 0.19.0 negotiates `protocolVersion: 1` even when the
client offers `2`, so v2 is unavailable.

The first implementation on `hermes-backend` sent a second concurrent
`session/prompt` and inferred what happened by matching English prose in the
reply. Its own ratified requirement, meanwhile, specified a different mechanism —
cancel the active prompt, then send the correction as a new prompt. The two
disagreed, and neither had been measured.

A spike against the installed `hermes` 0.19.0 settled it
(`openspec/changes/archive/2026-07-30-harden-hermes-turn-control/spike/`, with
raw JSON-RPC traces in both directions retained):

- A second `session/prompt` on a busy session is Hermes' steer surface. Hermes
  streams `"Redirected the active turn with your correction."` as an
  `agent_message_chunk`, answers the correction's request immediately with a bare
  `{"stopReason": "end_turn"}` carrying no `usage`, and logs `Delivered /steer to
  agent after tool batch`. The original 60-iteration tool call ran to completion,
  the correction took effect *within that same turn*, and only then did the
  original prompt respond — with `usage`. This is ADR 0005 parity.
- `session/cancel` cannot serve steering on this version. The running tool is
  aborted correctly (`exit_code 130`, no orphaned process), but the pending
  prompt fails with `-32603 Internal error: 'NoneType' object has no attribute
  'startswith'`, reproducible with `protocolVersion: 1` pinned. The session is
  then wedged — a subsequent prompt answers `"Queued for the next turn.
  (1 queued)"` and never runs.

So the ratified mechanism was harmful, and the implemented mechanism was correct
but unspecified by any protocol version.

## Decision

The Hermes backend SHALL steer an active turn by sending an additional
`session/prompt` on the same session, and SHALL NOT send `session/cancel` as
part of steering. The shop accepts a deliberate dependency on Hermes behaviour
that no ACP version specifies.

The backend SHALL NOT infer the outcome from the agent's natural-language reply.
Whether a correction steered the active turn or lost a completion race SHALL be
decided from the shop's own record of whether the original prompt is still
outstanding. The correction's immediate response is an acknowledgement, not a
turn completion: the original delivery remains the active identity until its own
response arrives.

Hermes' acknowledgement sentence MAY be matched to keep it out of the maker's
conversation, because the two streams carry no marker that separates it from
turn output. That is content filtering only, and it fails safe: an unrecognised
acknowledgement adds a stray sentence rather than losing turn output or
changing a delivery identity. It SHALL NOT influence control flow.

Cancellation SHALL be reserved for closing or shutting down the shop. A
cancelled prompt SHALL be reported as a completed turn rather than a role
failure, whether the subprocess answers with a stop reason or with a
transport-level error, so that interrupting a role can never end the run. A
cancelled Hermes session SHALL be treated as spent and never returned to
standby.

The shop remains on ACP `protocolVersion: 1`.

## Consequences

- Steering parity across both backends is real and empirically grounded, not
  asserted. A maker's correction reaches a busy Hermes role at the next
  tool-batch boundary, and the turn's work in progress survives.
- The guarantee rests on undocumented behaviour. A Hermes release could remove
  second-prompt steering without breaking ACP compliance. The fake ACP fixture
  replays the measured frame sequence — acknowledgement chunk, immediate bare
  stop reason without `usage`, then the original prompt's real completion with
  `usage` — so the suite fails loudly rather than degrading into silence.
- If that dependency does break, the fallback is delivery-after-idle: hold the
  envelope until the active turn completes and deliver it as a new turn. That
  costs correction latency but not correctness, and needs no protocol support.
- The shop has no usable mid-run interrupt on Hermes until the upstream
  cancellation crash is fixed. Interrupt is close-only. Filed upstream as a
  wart.
- Evidence is n=1 per scenario, from a synthetic long-running tool call rather
  than a live project build. The spike is scripted and cheap to re-run; timing
  conclusions should be re-checked first on any Hermes upgrade.
- Codex `turn/steer` is unchanged. The portable `deliver_steer` contract is now
  specified by outcome — the correction reaches the role and the active delivery
  identity is well-defined — rather than by mechanism, since the two backends
  achieve it differently.
