## Why

The shop runs on Codex and Hermes. The pilot wants a maker who already has
Claude Code to run the shop the same way they run Claude Code — their machine,
their credentials, their piloting — with the model and the agent conversation in
one browser surface so the technical bar is a browser rather than a terminal.

Claude Code has no app-server multiplexer, so this is not a variation on either
existing backend: one role means one `claude -p --input-format stream-json`
process. That collides with ADR 0006's assertion that a backend owns one
external process, which is a boundary in the reference architecture and needs a
recorded decision rather than a quiet amendment.

A spike measured `claude` 2.1.220 against the four questions that decide whether
the portable `AgentBackend` contract can be honored
(`spike/claude_turn_control.py`, 14 steer runs plus baseline and interrupt
scenarios, raw frames in both directions under `spike/evidence/`):

1. **Sessions persist and carry no turn identity.** A session survives across
   turns and survives interruption, but the stream exposes no per-turn
   identifier at all — `session_id` is per session. Codex supplies `turnId`;
   Hermes supplies a request id the adapter minted. Claude supplies neither, so
   the backend must mint delivery ids and correlate them to `result` frames.

2. **Mid-turn corrections are absorbed into the running turn, deterministically.**
   In 14 of 14 runs a correction sent while a tool call was running was injected
   at the next tool-batch boundary and the exchange produced exactly one
   `result`. No acknowledgement frame, no synthetic turn — none of the ADR 0007
   machinery Hermes needed.

3. **Whether the model *acts* on the correction is conditional.** Crossing
   channel consistency against system-prompt trust framing gave 3/4, 4/4, 0/3,
   and 1/3. The load-bearing variable is that the broker envelope is the format
   of every instruction including the session's first — not the system prompt.
   When a mid-turn envelope is the first message to claim broker authority, the
   model correctly refuses it as a suspected injection.

4. **Interrupt works and does not spend the session.** It is acknowledged, ends
   the turn with `terminal_reason: "aborted_tools"` and `is_error: true`, kills
   the tool's process tree with no orphans, and the session runs further turns
   afterwards. Hermes cannot do this (ADR 0007); Claude restores the capability.

Finding 3 also invalidates an earlier reading recorded during exploration, which
attributed the refusal to the absent system prompt because the first hand-run
probes moved both variables at once. The crossed design corrected it. This is
the kind of error the spike exists to catch, and the correction is why the
proposal specifies channel consistency as the requirement.

## What Changes

- Add `floor/backends/claude.py` implementing the unchanged `AgentBackend`
  protocol over `claude -p --input-format stream-json --output-format
  stream-json`, and add `claude` to the `--backend` choices.
- **Amend a ratified boundary**: a backend MAY own one process per role rather
  than one process per backend. Ownership and release obligations are unchanged;
  cardinality is not. ADR 0008 records this and amends ADR 0006.
- Mint delivery ids in the backend and correlate them positionally to `result`
  frames. `InactiveTurn` is never raised by this backend, because the CLI
  provides no signal that could raise it: a correction arriving after completion
  is silently accepted as a new turn. Move `InactiveTurn` from
  `floor/backends/codex.py` to `floor/backends/base.py`, since a third backend
  now shows it is part of the portable contract rather than a Codex detail.
- Deliver the role contract through `--append-system-prompt`, and read `model:`
  and `tools:` from the role card frontmatter, which are already written in
  Claude Code's vocabulary. No per-role adapter file is added.
- Require that every user message reaching a role session be a broker envelope,
  starting with the first, and include trust framing in the role contract. ADR
  0009 records why both are needed and that neither alone suffices.
- Open role sessions with operator-machine customization disabled so a role's
  behavior does not depend on the `CLAUDE.md`, settings, hooks, or plugins that
  happen to exist on the machine running the shop. `--bare` is deliberately not
  used: it skips OAuth entirely and would exclude the subscription operator this
  backend exists to serve.
- Translate an interrupted turn to `turn_completed`, never `role_failed` — the
  same trap ADR 0007 recorded for Hermes, in a different wire shape.
- Add a fake Claude CLI fixture beside `tests/fixtures/fake_acp_server.py` that
  replays the measured frame sequence, and record in ADR 0009 that the fixture
  provably cannot cover the model-compliance half.

Not changed: the orchestrator, the broker, the frontend, the role cards' bodies,
and both existing backends apart from `InactiveTurn`'s new home. The shop pins,
bundles, brokers, and inspects no credential; it invokes whatever `claude` the
operator has already authenticated.

## Capabilities

### New Capabilities

None. This adds a third implementation of an existing capability.

### Modified Capabilities

- `shop-agent-backend`: accept `claude` as a backend value; allow a backend to
  own one process per role while keeping its release obligations; require the
  Claude backend to mint delivery identity and resolve the steer race without an
  `InactiveTurn` signal; require the broker envelope on every user message from
  the first; require an interrupted turn to be a completion rather than a role
  failure.
- `shop-floor-lifecycle`: extend backend selection to `claude`, and extend the
  close guarantee so that a backend owning several processes releases all of
  them within the same bounded time.

## Impact

- `floor/backends/claude.py` — new.
- `floor/backends/base.py` — `InactiveTurn` moves here; the one-process
  docstring at line 80 is corrected.
- `floor/backends/codex.py`, `floor/backends/hermes.py` — import `InactiveTurn`
  from `base`; no behavior change.
- `floor/orchestrator.py` — `--backend` choices only. The seam itself is
  unchanged, which is the ADR 0006 claim this change tests.
- `tests/fixtures/fake_claude_cli.py`, `tests/test_orchestrator.py` — new
  fixture and coverage mirroring the Hermes acceptance tests.
- `docs/adrs/0008`, `docs/adrs/0009`, `docs/adrs/README.md`,
  `docs/architecture-overview.md` — three-backend architecture, not an appended
  note.
- Evidence retained under `spike/`. 14 steer runs, Sonnet 5 only, one CLI
  version, synthetic tool call. The fixture encodes the transport half so it
  regresses loudly; the model half regresses silently and is named as such.
- No broker, frontend, or public API changes.
