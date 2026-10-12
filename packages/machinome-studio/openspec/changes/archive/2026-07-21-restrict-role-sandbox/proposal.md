## Why

Live shop role threads currently run with unrestricted host access and no
approval boundary. The shop already identifies one verified project repository
for each run, so role work should be confined to that project instead.

## What Changes

- Start each Foreman, Designer, and Machinist Codex thread with the verified
  `projects/<name>` directory as its workspace-write sandbox root.
- Replace unrestricted `danger-full-access` execution with the
  `workspace-write` sandbox.
- Remove the hard-coded no-approval policy so the app-server uses the
  workspace policy's normal approval behavior for actions outside the project
  boundary.
- Prove in the live app-server adapter contract that every role receives the
  project-scoped sandbox configuration.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `shop-floor-lifecycle`: role sessions opened for a shop run are constrained
  to the verified project workspace rather than granted unrestricted host
  access.

## Impact

- `floor/orchestrator.py` app-server thread creation and its protocol tests.
- Shop-floor lifecycle specification and orchestration ADR/documentation where
  they describe role runtime ownership.
- No project repository, framework checkout, broker transport, or role
  workflow behavior changes.
