## Why

The Agents screen currently treats every eagerly opened standing role session as already committed to its backend, so a maker cannot correct the backend before doing any work. A still-pristine role has no conversation or assignment state to migrate, and can therefore be safely replaced while preserving the rule that used sessions never migrate between backends.

## What Changes

- Let a maker select a different backend, provider, model, and reasoning combination while the role is pristine, and apply it immediately by replacing the unused standing backend session.
- Define pristine as a permanent role-runtime state that ends on the first accepted message or delivery, assignment, or agent activity; completing that work does not make backend switching available again.
- Keep model/reasoning-only updates available under the existing idle and backend-capability rules after first use, while backend/provider controls remain locked.
- Source OpenCode provider/model combinations from its live catalogue and keep project persistence enabled by default.
- Extend the role runtime API and browser state so the Agents screen can distinguish pristine replacement from idle in-session updates.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `project-runtime-selection`: Permit atomic replacement of an unused role session across configured backends/providers and permanently lock that operation after first use.

## Impact

The broker must retain role-use history, the session/orchestrator boundary must support lazy backend ownership and atomic unused-handle replacement, backend catalogues must describe selectable backend/provider/model combinations, and the runtime API and React Agents workspace must expose and enforce the distinction. Architecture, ADR, design reference, and tests require corresponding updates.
