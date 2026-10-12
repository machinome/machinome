# ADR 0022: Control idle agent runtimes in place and normalize native activity

**Status:** Accepted (amended by ADRs 0025 and 0032)

**Date:** 2026-08-12

**Deciders:** Pilot

**Origin:** Shop change `add-agents-workspace`

**Amends:** [ADR 0006](./0006-pluggable-agent-backend-orchestration.md),
[ADR 0012](./0012-bounded-opencode-compatibility-policy.md),
[ADR 0014](./0014-use-snapshot-first-live-state-for-the-floor-browser.md), and
[ADR 0017](./0017-project-selected-per-agent-runtime.md)

## Context

Project configuration already selects each role's backend, provider, model, and
reasoning before a session opens. The browser could show only broker lifecycle
events, while native tools, results, and file changes remained inside three
different backend protocols. Changing a selection required closing the project,
even where a backend can apply a new model to the same persistent session.

The Agents workspace needs useful live inspection and an immediate model
control without misrepresenting a restarted or replayed conversation as the
same session. It must also respect delegated broker work that can be waiting
while an assignment is already current or queued.

## Decision

The backend seam carries a portable activity record and context-preserving
runtime controls. Each adapter translates native tool and file records into a
stable role-scoped activity identity, category, running/terminal state, display
summary, optional result, path, unified diff, and token counts. Role messages
and failures are normalized at the orchestrator. The broker replaces updates by
role and activity identity, keeps a bounded session history, and publishes it
through the existing snapshot-first SSE connection.

A runtime change always replaces model and reasoning together on the role's
existing backend and provider. The orchestrator holds the role delivery lock
and requires both native-delivery and broker lifecycle state to be idle. A
current or queued assignment, active delivery, or failed role blocks the
change. This server gate is authoritative; browser disabling is explanatory.

Codex applies model and effort to later turns on the existing thread. OpenCode
applies provider/model/variant to later prompts on the existing session and
derives choices from the live catalogue of the already selected provider.
Claude reports the control unsupported because its model is process launch
configuration and no verified context-preserving in-session switch exists.

Persistence is optional and defaults on. A persisted operation prepares a
comment-preserving `pyproject.toml` edit against the displayed content revision,
then holds the same role gate while updating the backend and atomically
publishing the file. Publication failure restores the previous backend runtime
before any runtime change is published. A temporary operation changes only the
open session.

Backend and provider migration, next-assignment queues, tool selection, and
Claude permission changes are outside this decision.

## Alternatives considered

- Close a session, open a replacement on any selected backend, and replay or
  summarize its context. Rejected because the result is not the same session
  and replay changes context semantics.
- Permit changes whenever the broker displays `waiting`. Rejected because a
  native delivery, current assignment, or queued assignment can still exist.
- Hard-code OpenCode choices in the shop. Rejected because provider catalogues
  and authenticated operator access vary.
- Send raw backend frames to the browser. Rejected because it exposes native
  protocols and would require three frontend adapters.
- Persist by reserializing TOML or writing a sidecar. Rejected because it either
  damages maker-authored configuration or creates a second durable authority.
- Add a second stream or poll for Agents state. Rejected because session state
  already has one snapshot-first live boundary.

## Consequences

### Positive

- Makers can inspect comparable live work across Codex, Claude, and OpenCode.
- Supported model changes take effect on the next turn without losing session
  identity or waiting for a project reopen.
- Backend/provider invariance and joint idle gating prevent accidental session
  migration and active-work mutation.
- Temporary experimentation and durable project selection use one explicit
  control, with concurrent project edits protected by a revision check.

### Negative / trade-offs

- Native activity translation must track evolving backend event schemas.
- Claude remains read-only until its runtime supplies a verified in-session
  model switch.
- Activity is intentionally bounded and disappears when the session closes.
- The atomic config publication performs a small synchronous file replacement
  while holding the role gate.

### Neutral

- Profile-owned tool and permission policy is unchanged.
- Missing token accounting is omitted instead of estimated.
- OpenCode catalogue failure disables editing for that role but does not fail
  the session.
