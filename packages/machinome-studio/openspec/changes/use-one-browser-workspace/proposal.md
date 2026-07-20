## Why

The current shop floor exposes lifecycle status and the agent roster, but it
does not give a maker one durable place to orient around the shop's work.
Story 2 establishes that shared browser surface before later stories add
foreman direction and functional-model inspection.

## What Changes

- Replace the roster-only browser layout with a single, responsive shop
  workspace.
- Establish that workspace as the React + Vite application frame for the
  remaining shop-floor interface stories.
- Provide persistent, clearly named regions for the shop menu, the current
  artifact, and the foreman conversation.
- Keep the existing shop lifecycle and manifested-agent feedback visible in
  the workspace menu while the other regions show their initial empty states.

## Capabilities

### New Capabilities

- `shop-browser-workspace`: A unified browser layout that lets a maker see
  the shop menu, artifact area, and foreman-conversation area together.

### Modified Capabilities

None.

## Impact

- Affects the React + Vite shop-floor frontend, its compiled static assets,
  and browser-facing end-to-end coverage.
- Reuses the existing FastAPI lifecycle and run APIs; it introduces no new
  service endpoint, dependency, or external integration.
