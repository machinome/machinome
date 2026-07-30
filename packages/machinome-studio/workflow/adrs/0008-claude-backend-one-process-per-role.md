# ADR 0008: Add a Claude Code backend, and let a backend own one process per role

**Status:** Accepted

**Date:** 2026-07-30

**Origin:** Shop change `add-claude-agent-backend`

**Amends:** ADR 0006

## Context

ADR 0006 generalized shop orchestration to a pluggable `AgentBackend` and
established the seam that `floor/orchestrator.py` depends on. It also asserted a
process model: *"Every backend owns one external process (`codex app-server`,
`hermes acp`, …)"* (`floor/backends/base.py:80`). Both existing backends
multiplex three role sessions through a single long-lived subprocess — Codex
through `thread/start`, Hermes through `session/new`.

The pilot wants a third backend so a maker with a Claude subscription can run
the shop the way they already run Claude Code, with the model and the agent
conversation in one browser surface. Claude Code has no equivalent multiplexer.
Its programmatic surface is `claude -p --input-format stream-json`, which is one
process holding one conversation. Three roles therefore mean three processes.

A spike against `claude` 2.1.220 measured the surface directly
(`openspec/changes/add-claude-agent-backend/spike/`, raw frames in both
directions retained). Four findings shape this ADR:

1. **A session persists across turns and survives interruption.** The process
   holds the conversation until stdin closes, so a role session is a process
   lifetime, not a request.
2. **The stream carries no turn identifier.** `session_id` identifies the
   *session*; no per-turn identity is handed to the client at all. Codex
   supplies `turnId` and Hermes supplies a request id the adapter itself minted;
   Claude supplies neither.
3. **Interrupt works and does not spend the session.** A
   `control_request`/`interrupt` is acknowledged, ends the turn with
   `terminal_reason: "aborted_tools"` and `is_error: true`, kills the tool's
   process tree, and leaves the session able to run further turns.
4. **Role configuration is already expressed in Claude Code's vocabulary.** The
   role cards' `model:` (`inherit`, `sonnet`) and `tools:` (`Bash, Read, Write,
   Edit, Glob, Grep`) frontmatter are literally `--model` and `--tools` values.
   Both existing backends ignore `tools:` entirely.

## Decision

The shop SHALL support `--backend claude`, implemented in
`floor/backends/claude.py` against the unchanged `AgentBackend` protocol.

### One process per role

A backend MAY own one external process per role session rather than one process
for the whole backend. ADR 0006's single-process statement is amended to a
requirement about *ownership*, not cardinality: a backend owns every process it
starts and SHALL release all of them on `close()`.

Consequences the implementation must carry:

- `close()` escalates stdin close → `SIGTERM` → `SIGKILL` per process, bounded,
  so the ratified guarantee that no agent subprocess outlives a close still
  holds with three ladders instead of one.
- `backend_failed` remains reserved for a fault that ends the run. A single role
  process exiting unexpectedly SHALL be reported as `role_failed` for that role.
- A partial failure while opening three processes SHALL release the processes
  already started before reporting.

### Delivery identity is minted by the backend

Because the CLI supplies no turn identifier, the Claude backend SHALL mint its
own `delivery_id` and correlate it to the next `result` frame on that role's
stream. It SHALL NOT derive delivery identity from `session_id`, from message
`uuid` values, or from the agent's prose.

`InactiveTurn` gains a third meaning and SHALL NOT be raised by this backend. On
Codex it is an error response; on Hermes it is the adapter's own outstanding-
prompt check. On Claude no such signal exists or can exist: a correction that
arrives after the turn completed is silently accepted and becomes a new turn
with its own `result`. The backend SHALL resolve that race by counting `result`
frames against outstanding deliveries, and the portable contract for
`deliver_steer` SHALL be read as specified by outcome — the correction reaches
the role and the active delivery identity is well defined — as ADR 0007 already
framed it.

`InactiveTurn` currently lives in `floor/backends/codex.py` and is imported from
there by `floor/backends/hermes.py`. It SHALL move to `floor/backends/base.py`,
since it is part of the portable contract rather than a Codex detail.

### The role contract is delivered as a system prompt

`open_role()` SHALL pass the role contract through `--append-system-prompt`.
This is system-level delivery comparable to Codex `developerInstructions`, and
unlike Hermes it costs no priming turn (`floor/backends/hermes.py:172-195`).

This choice is load-bearing for ADR 0009, not merely tidy. Delivering the role
contract as an opening *user* turn would make the session's first user message
plain prose, so the first broker envelope would arrive mid-conversation — the
condition under which the spike measured 0 of 3 corrections being acted on. The
role contract goes in the system prompt so that every user message, from the
first, is a broker envelope.

`model:` and `tools:` SHALL be read from the role card frontmatter and passed as
`--model` and `--tools`. This backend SHALL NOT introduce a per-role adapter
file: ADR 0006 placed backend runtime knobs in adapter files, and this backend
needs none because the shared role card already carries both values.

### Configuration inheritance is bounded

Claude Code auto-loads `CLAUDE.md` from the working directory and its parents,
`~/.claude` settings, hooks, plugins, and skills. The shop's contract makes the
role card the sole authority for a role and forbids foreign project context in a
product agent. A role session SHALL therefore be opened with operator-machine
customization disabled (`--safe-mode`, plus `--setting-sources` and
`--strict-mcp-config` as needed).

`--bare` is the stronger lever and is deliberately NOT used: it skips OAuth and
keychain reads entirely, so it would force an API key and exclude the
subscription operator this backend exists to serve.

This is a decision about contract integrity and reproducibility — that a role
behaves the same on the pilot's VM and on a contributor's laptop — and not about
anything else.

### Interrupt fidelity differs per backend

`interrupt()` on this backend is usable mid-run and does not spend the session.
The portable contract stays as ADR 0007 left it — the orchestrator calls
`interrupt()` only while closing — so no orchestrator behavior changes here. The
capability is recorded because it is real and because a future decision to use
it mid-run needs to know which backends can honor it.

An interrupted turn SHALL be translated to `turn_completed`, never
`role_failed`. Claude reports it as `is_error: true` with `terminal_reason:
"aborted_tools"`; treating that as a role failure would raise from
`ShopOrchestrator.handle_event` and end the run — the same trap ADR 0007
recorded for Hermes, in a different wire shape.

## Consequences

- The shop gains a backend whose steering, interrupt, and session-persistence
  behavior are the closest of the three to what ADR 0005 originally specified
  for Codex, with none of the Hermes cancellation pathology.
- ADR 0006's mapping table gains a third column and its process-model sentence
  is amended. `docs/architecture-overview.md` needs a three-backend section, not
  an appended note.
- Three processes cost more memory and more startup than one, and shop open now
  launches three CLIs. Role open is also no longer a cheap request on a warm
  connection.
- The `tools:` frontmatter becomes load-bearing for the first time. A role card
  that names a tool Claude Code does not have, or omits one the role needs, now
  breaks that role on this backend only.
- Delivery correlation is positional rather than identifier-based, which is
  weaker than both existing backends. It is sound only while one turn is
  outstanding per role process, which the orchestrator's per-role delivery lock
  (`floor/orchestrator.py:91`) already guarantees.
- The shop does not pin, bundle, broker, or inspect any credential; it invokes
  whatever `claude` the operator has already authenticated. Which plan or
  credential that is, and its terms, are between the operator and Anthropic.
- Steering on this backend carries a dependency of a different kind from the
  other two: the transport is deterministic but the model's compliance is
  conditional. ADR 0009 records it separately, along with the constraint it
  places on how the role contract is delivered.
