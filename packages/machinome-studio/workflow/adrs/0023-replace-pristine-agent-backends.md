# ADR 0023: Replace a pristine agent's backend without migrating a session

**Status:** Accepted (amended by ADRs 0025 and 0032)

**Date:** 2026-08-12

**Deciders:** Pilot

**Origin:** Shop change `allow-pristine-backend-selection`

**Amends:** [ADR 0006](./0006-pluggable-agent-backend-orchestration.md),
[ADR 0017](./0017-project-selected-per-agent-runtime.md),
[ADR 0018](./0018-multi-backend-orchestration.md), and
[ADR 0022](./0022-control-idle-agent-runtimes-in-place.md)

## Context

The shop eagerly opens one standing session per role. ADR 0022 consequently
locked backend and provider as soon as a project opened, even before the role
had received a message or assignment or produced activity. An unused handle
has no conversation context to migrate, so that lock prevented correcting a
runtime selection without protecting any state.

## Decision

The broker records a monotonic pristine state for every role. It begins true
at manifestation and permanently becomes false when the role first receives a
message or assignment, accepts a delivery, or produces backend activity. Idle
is independent and reversible; pristine is not.

While a role is both pristine and idle, the Agents workspace may select a
complete backend, provider, model, and reasoning combination. The orchestrator
opens a fresh handle with profile-owned tools and permission, atomically
publishes the project runtime edit when requested, swaps ownership only after
both succeed, and closes the unused old handle. Nothing is replayed or copied.
A same-backend replacement is permitted for a pristine process-based adapter
such as Claude. After first use, ADR 0022's context-preserving same-backend,
same-provider idle update rule remains the only runtime mutation path.

Fresh-session catalogues identify complete runtime combinations. Codex and
Claude publish validated choices; OpenCode obtains providers, models, and
variants from its live catalogue. Backends not already used by the project are
created lazily, joined to event routing, and included in session cleanup.

Persistence continues to default on and writes the complete selection to the
project's `[tool.libresolid-studio.agents]` table under revision checking.

## Alternatives considered

- Treat every opened handle as used. Rejected because allocation alone creates
  no maker or agent context and caused the reported inability to correct a new
  role's backend.
- Infer pristine from `waiting` or empty visible activity. Rejected because
  completed work returns to waiting and activity history is bounded.
- Restart a used role and replay or summarize its context. Rejected because
  this is session migration with different semantics.
- Ship an OpenCode provider list. Rejected because the authenticated operator's
  catalogue is the authority.

## Consequences

### Positive

- A maker can correct backend selection before any work begins.
- The boundary against session migration remains permanent and server-enforced.
- Claude model selection is useful before first use without claiming in-process
  context preservation.

### Negative / trade-offs

- Opening runtime controls may lazily start an optional backend to obtain its
  live catalogue.
- Backend adapters now distinguish fresh-session from existing-session choices.
- A failed old-handle close after a successful swap is best-effort until normal
  backend shutdown.

### Neutral

- Tools and permissions remain profile-owned.
- No conversation or assignment state crosses backend owners.
