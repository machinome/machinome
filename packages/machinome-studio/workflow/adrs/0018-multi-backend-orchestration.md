# ADR 0018: Let one shop floor run several agent backends at once

**Status:** Accepted (amended by ADR 0025)

**Date:** 2026-08-09

**Deciders:** Pilot

**Origin:** OpenSpec change `project-selected-agent-runtime`

**Amends:** [ADR 0006](./0006-pluggable-agent-backend-orchestration.md)
and [ADR 0008](./0008-claude-backend-one-process-per-role.md)

## Context

ADR 0006 generalized shop orchestration to a pluggable `AgentBackend` protocol,
and ADR 0008 established that a backend owns its own process cardinality — one
process for all roles in Codex app-server and OpenCode, one process per role in
Claude — while ownership of what it starts is not negotiable.

Both decisions assumed exactly one backend per run. `ShopOrchestrator` holds a
single `self.backend` and reaches for it at fourteen call sites; `_serve` builds
one adapter and consumes one `backend.events` iterator in one routing task.

ADR 0017 makes backend selection a per-agent property of the project, so a
single run may now need Designer on one backend and Machinist on another. The
single-backend assumption is the remaining obstacle, and it is structural rather
than a matter of configuration.

## Decision

A run SHALL open each distinct selected backend exactly once and route each
agent to the backend that owns it.

`ShopOrchestrator` SHALL hold a mapping from agent ID to backend instance rather
than one backend. Instantiation SHALL be per distinct backend, not per agent:
process cardinality remains each backend's own business under ADR 0008, so an
adapter that already serves several roles from one process continues to do so.

`start()` SHALL be called once per distinct backend. `close()` SHALL release
every role session and then close each distinct backend exactly once. Event
routing SHALL run one task per open backend, all feeding the single
`handle_event`, and the runtime SHALL wait on the delivery task together with
every event task.

Routing SHALL use resolved runtime data alone. The orchestrator SHALL NOT branch
on a backend name, so ADR 0006's backend-neutrality boundary is preserved: an
agent's owner is a dictionary lookup, not a conditional.

Whole-backend failure semantics SHALL NOT change under this decision.
`backend_failed` continues to end the run, as it does today.

## Alternatives considered

### Keep one backend per run and require a project to pick one

Rejected. It defeats the purpose of ADR 0017, whose motivating case is a project
that wants different agents on different models and backends.

### Instantiate one backend object per agent

Rejected. It would start one Codex app-server and one OpenCode server per role
instead of one per run, multiplying processes and authentication for no benefit,
and it would contradict ADR 0008 by taking cardinality away from the backend.

### Wrap the backends in a composite that satisfies `AgentBackend`

Rejected. A composite would have to fabricate a single `events` iterator and a
single `close()` with no honest meaning for `start()`, and it would hide which
adapter failed. Making the orchestrator's ownership explicitly per-agent is
smaller and keeps failures attributable.

### Resolve whole-backend failure semantics in this decision

Deferred by the pilot. With several backends open, ending every role because one
adapter died is probably wrong, but leaving a permanently dead role on an open
floor is a state the broker cannot currently express. The natural extension is
demoting `backend_failed` to `role_failed` for that backend's roles so the
existing recovery path re-opens them, but that changes ratified recovery
behaviour and deserves its own decision.

## Consequences

### Positive

- A floor can mix backends, which is what makes ADR 0017's per-agent selection
  executable rather than merely declarable.
- Per-agent ownership makes it explicit which adapter is responsible for a
  failing role.
- The `AgentBackend` protocol is unchanged; multi-backend support is entirely a
  property of the orchestrator's ownership model.

### Negative and trade-offs

- Shutdown and partial-open unwinding are more intricate: cleanup must release
  sessions across several adapters and close each exactly once, and a failure
  part-way through opening must release everything already started across all of
  them.
- A mixed-backend run has more failure surface, and the whole-backend case is
  knowingly left at today's conservative fatal behaviour.
- Backend-level test fixtures and hooks, including `--backend-command`, become
  per-backend.

### Neutral

- Role-scoped failure and recovery are per role already and are unaffected.
- Broker, browser workspace, role prompts, and shop skills do not change.
- ADR 0008's cardinality-versus-ownership rule is reinforced rather than
  revised: this decision adds a layer above it without reaching into it.
