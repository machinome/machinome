## Context

`main` (HEAD `cba4087`) carries two working backends behind the ADR 0006
`AgentBackend` seam. Adding a third is the first real test of whether that seam
generalizes, because Claude Code differs from both existing backends on the two
properties they happened to share: one process per backend, and a
vendor-supplied turn identifier.

The spike (`spike/claude_turn_control.py`, evidence under `spike/evidence/`)
measured `claude` 2.1.220 on Sonnet 5 across six scenarios and 14 steer runs.

**s0 — baseline.** Two turns on one process; the session persists. The `result`
frame carries `session_id`, `num_turns`, `stop_reason`, `terminal_reason`,
`usage`, `uuid` and no turn identifier of any kind. Delivery correlation must
therefore be positional.

**s1/s2/s4/s5 — steering.** Two variables crossed:

| Channel from first instruction | Trust framing | Correction acted on |
|---|---|---|
| broker envelope | no | 3/4 |
| broker envelope | yes | 4/4 |
| plain prose | no | 0/3 |
| plain prose | yes | 1/3 |

In all 14 runs, regardless of outcome, the correction was absorbed into the
running turn and the exchange produced exactly one `result` frame. Transport and
compliance are independent layers, and only the second is uncertain.

**s3 — interrupt.** `control_request`/`interrupt` answered
`{"subtype":"success","response":{"still_queued":[]}}`; the turn ended with
`is_error: true`, `terminal_reason: "aborted_tools"`,
`subtype: "error_during_execution"`; no orphaned tool process; the session then
completed a further turn.

Constraint worth stating plainly: one CLI version, one model, synthetic tool
calls, and a sample where the best cell is 4 of 4 rather than a proof.

## Goals / Non-Goals

**Goals:**

- A third backend behind the unchanged `AgentBackend` protocol.
- Keep steering parity real rather than asserted, and be explicit about which
  half of it is guaranteed.
- Keep role behavior independent of the operator's machine configuration.
- Preserve the ratified close guarantee across several processes.

**Non-Goals:**

- Changing the orchestrator, broker, frontend, or role card bodies.
- Using the `claude-agent-sdk` package. The CLI's stream-json frames are simpler
  than ACP and add no dependency to a two-dependency project, matching the idiom
  of the two existing adapters.
- Routing through the ACP adapter for Claude. It would reuse the Hermes client
  but reintroduce exactly the ADR 0007 fragility this backend otherwise avoids,
  plus an npm dependency.
- Mid-run interrupt as an orchestrator behavior. The capability exists here but
  the portable contract stays where ADR 0007 left it.
- Any credential, quota, deployment-topology, or usage-policy mechanism. The
  shop invokes the operator's already-authenticated `claude`.

## Decisions

### D1: One process per role

Claude Code holds one conversation per process. Three roles mean three
processes. ADR 0006's single-process sentence is amended to an ownership
requirement.

*Alternative rejected:* multiplexing roles onto one process by prefixing
messages with a role name. It would put three role contracts in one context,
destroy the isolation the role cards depend on, and make a stuck role block the
others.

*Alternative rejected:* `--resume` against one process per delivery. Session
persistence would survive, but every delivery would pay full startup and the
session would no longer be a live standby, breaking the zero-token idle property
ADR 0006 records.

### D2: Backend-minted delivery identity, positional correlation

`deliver_start` mints an id, records it as outstanding for that role, and the
reader resolves it on the next `result` frame. Sound because the orchestrator's
per-role delivery lock (`floor/orchestrator.py:91`) guarantees at most one
outstanding delivery per role.

*Alternative rejected:* using the replayed user message `uuid` from
`--replay-user-messages`. It identifies the *input*, not the turn, and a steered
correction produces a second `uuid` inside one turn, so it cannot answer "which
delivery does this `result` complete".

### D3: `deliver_steer` never raises `InactiveTurn` here

The CLI gives no error for a correction that arrives after completion; it
silently starts a new turn. So the race is resolved by counting: if a `result`
for the outstanding delivery has not been seen, the correction was absorbed and
the delivery identity stands; if it has, the correction becomes a new delivery
with its own id.

This makes `InactiveTurn` a portable concept with three backend-specific
triggers, so it moves to `base.py`. The orchestrator's retry path
(`orchestrator.py:105-108`) stays correct and simply never fires for this
backend.

### D4: Role contract in the system prompt, and every user message an envelope

`--append-system-prompt` carries the role contract; `--model` and `--tools` come
from the role card frontmatter, which already uses Claude Code's names.

The reason this is a decision and not a convenience is D5. Bootstrapping through
an opening user turn — the Hermes shape — would make the first user message
plain prose and push every session into the 0/3 condition.

### D5: Both channel consistency and trust framing

The measured table shows neither alone is sufficient: framing alone rescues a
mismatched channel 1 time in 3, consistency alone reaches 3 of 4, both reach 4
of 4. Require both. ADR 0009 records that the compliance half is best-effort and
that no prompt work converts it into a guarantee.

*Alternative rejected:* framing only, on the theory that a strong enough system
prompt makes the channel irrelevant. Measured at 1/3.

*Alternative rejected:* disguising the correction as ordinary user input to
sidestep the model's judgment. It would work by defeating a safety behavior that
is functioning correctly, and it would break the moment the model improves.

### D6: Bounded configuration inheritance

Open sessions with operator-machine customization disabled (`--safe-mode`, plus
`--setting-sources` and `--strict-mcp-config` as needed) so a role behaves the
same on the pilot's VM and a contributor's laptop.

*Alternative rejected:* `--bare`. It is the stronger isolation lever but skips
OAuth and keychain reads, forcing an API key and excluding the subscription
operator this backend exists for. The isolation gap between `--safe-mode` and
`--bare` is accepted and named.

### D7: An interrupted turn is a completion

Translate `is_error: true` with `terminal_reason` in
`{"aborted_streaming", "aborted_tools"}` to `turn_completed`. Untranslated it
would reach `handle_event` as `role_failed` and raise, ending the run — the ADR
0007 trap in a new wire shape.

Unlike Hermes, the session is not spent afterwards, so no session is marked
dead. The orchestrator still only calls `interrupt()` while closing.

### D8: A fixture for the transport, a live spike for the model

`tests/fixtures/fake_claude_cli.py` replays the measured frames: `system/init`,
assistant frames, tool-boundary injection of queued input, exactly one `result`
per exchange, and the interrupt sequence with its `control_response` and
`aborted_tools` result.

It cannot cover compliance, because a fake always complies. ADR 0009 names this
blind spot and makes the spike the regression check for that half.

## Risks / Trade-offs

- **Compliance is probabilistic** → the shop's contract is delivery, not
  obedience, and a refusal is visible to the maker as ordinary turn content in
  the existing conversation stream. No new mechanism, but the maker may see a
  correction declined.
- **A future non-envelope user message silently breaks steering** → the 0/3
  condition is invisible in the code that introduces it. Documented in the
  backend module and ADR 0009; a warm-up turn or health-check ping is the
  plausible way someone reintroduces it.
- **Positional correlation is weaker than an identifier** → sound only under the
  per-role delivery lock. If that lock is ever relaxed, this backend breaks
  first and silently.
- **Three processes cost three startups and three contexts** → shop open is
  slower and heavier than either existing backend.
- **`tools:` frontmatter becomes load-bearing** → a role card naming a tool
  Claude Code lacks breaks that role on this backend only.
- **`--safe-mode` is weaker isolation than `--bare`** → a hook or setting
  category that `--safe-mode` does not disable would leak in. Accepted to keep
  subscription auth working.
- **n is small and single-model** → the spike is scripted and takes minutes;
  re-run it on any upgrade before trusting the table.

## Migration Plan

No data or interface migration. The change lands on `claude-backend`, branched
from `main` at `cba4087`, and integrates back into `main`. Rollback is
discarding the branch. Existing backends are untouched apart from importing
`InactiveTurn` from its new home, which is covered by the existing suite.

## Decided by the pilot

- **2026-07-30 — `--backend claude` carries no experimental marker.** The whole
  project is pre-release; marking one backend experimental inside a pre-release
  shop would imply the others are not. The backend ships on equal footing with
  `codex` and `hermes`.

## What remains undetermined

These are open because they were not measured, not because they were judged
unimportant. Each names what to run so a later agent can close it with data
instead of re-deriving the question. `spike/claude_turn_control.py` is the tool
for the first three; it takes minutes and merges into the existing
`evidence/summary.json`.

**U1 — Compliance rates on the roles' actual models.** The whole table is Sonnet
5. `agents/foreman.md` and `agents/designer.md` declare `model: inherit`, so in a
real run they may be Opus. *To close:* `python claude_turn_control.py --only s1
--only s2 --repeat 3 --model opus` and compare against the Sonnet table in ADR
0009. If the s2 cell drops below 4/4 on the model a role actually uses, the
best-effort language in ADR 0009 becomes a stronger caveat, not a weaker one.

**U2 — Whether a correction survives a real build.** Every steer run used a
synthetic `sleep` loop, exactly as the Hermes spike did. A machinist mid-`solid
develop` has a long-running child process, a callback, and a much larger
context. *To close:* run a live Claude shop, steer the machinist during an actual
build, and record whether the correction lands and whether the callback survives.
This cannot be spiked in isolation; it needs a real project floor.

**U3 — Whether compliance degrades over a long session.** Every run steered the
first or second turn of a fresh session. A role forty turns into a build has a
large context and may weigh a mid-turn envelope differently. *To close:* extend
the spike with a scenario that runs several ordinary turns before steering.

**U4 — What `--safe-mode` actually leaves loaded.** D6 accepts weaker isolation
than `--bare` to keep subscription auth working, but the exact residue was not
enumerated. *To close:* open a role session with `--safe-mode` against a machine
carrying a project `CLAUDE.md`, user memory, hooks, and an MCP server, and read
the `system/init` frame — it reports `tools`, `mcp_servers`, `plugins`, and
`slash_commands`. Compare against the same session without `--safe-mode`.

**U5 — Whether the 0/3 mismatched-channel condition is reachable in practice.**
It requires a non-envelope user message, which the current code cannot produce.
It is guarded by a comment and by ADR 0009 rather than by a test, because no
fixture can detect it. *To close:* nothing to measure; the guard is a review
obligation. Any future warm-up turn, health check, or nudge reopens it.
