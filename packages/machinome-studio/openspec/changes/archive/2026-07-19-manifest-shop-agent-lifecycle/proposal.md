## Why

The shop-floor interface needs to show the pilot which agents are present in a
run and what they are doing.  Sprint 001 does not yet give the browser a
dependable, user-visible agent roster or lifecycle.

This is the smallest next slice from Sprint 001 that makes live shop activity
legible before adding project browsing, artifact viewing, or chat.

## What Changes

- Add a menu roster that shows each manifested shop agent and removes it when
  the orchestrator reports that it has stopped.
- Show the user-visible transitions from waiting to active only after the
  agent acknowledges its assigned work, and back to waiting when it reports
  completion.
- Retain the latest roster state when the browser connects or reconnects to an
  ongoing shop run.

## Capabilities

### New Capabilities

- `shop-agent-lifecycle`: Show the lifecycle and availability of agents in an
  active shop run.

### Modified Capabilities

- None.

## Impact

- The shop-floor browser interface and its live-update path.
- A TypeScript React frontend built and served as Vite assets.
- The orchestration boundary that manifests agents and receives their lifecycle
  reports.
- Unit and browser end-to-end coverage for visible roster transitions.
