## 1. Run-scoped lifecycle model

- [ ] 1.1 Add a run-scoped roster model for manifested agents, their display
  details, assignments, and waiting or active state; remove an entry when the
  orchestrator reports that the agent has stopped.
- [ ] 1.2 Add broker operations that manifest an agent, record a work
  assignment, accept an acknowledgment, and accept a completion report only
  for the matching manifested agent and assignment.
- [ ] 1.3 Publish the current roster in the active run representation and
  lifecycle updates on the live viewer stream.

## 2. Shop-floor menu

- [ ] 2.1 Scaffold a TypeScript React frontend with Vite and configure the
  shop-floor service to serve its production build.
- [ ] 2.2 Render the current agent roster in a React menu component, including
  role and waiting or active state.
- [ ] 2.3 Apply lifecycle updates to the rendered roster without reloading the
  page and recover the current state after reconnecting.

## 3. Verification

- [ ] 3.1 Add focused broker tests for manifest, stop, assignment,
  acknowledgment, completion, unknown-agent, and mismatched-completion
  behavior; demonstrate the relevant assertions fail before implementation and
  pass afterward.
- [ ] 3.2 Add browser end-to-end coverage that keeps one shop-floor page open
  while an agent appears, acknowledges work, and completes it; demonstrate the
  assertions fail before the UI and live-update implementation and pass
  afterward.
- [ ] 3.3 Run the full automated suite and record any remaining limitation for
  an active agent that has neither completed nor been reported as stopped.
