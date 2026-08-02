## 1. Workspace shell and live context

- [x] 1.1 Replace the floor's stacked workspace markup with the reference 1b
  title bar, activity rail, agent panel, model viewport, chat column, and empty
  status bar while preserving semantic landmarks.
- [x] 1.2 Render the Model-selected rail and hover-only deferred rail items
  without adding navigation or unavailable panels.
- [x] 1.3 Move the profile-provided live agent roster into the agent panel and
  remove the visible broker-event log without changing broker event ingestion.

## 2. Existing capability presentation

- [x] 2.1 Re-style and position the existing functional-model viewer in the
  central viewport, preserving model rebuild, error, and viewer-control
  behaviour.
- [x] 2.2 Re-style and position the existing profile conversation in the right
  column, preserving attribution, send, newline, sending, and autoscroll
  behaviour.
- [x] 2.3 Implement responsive layout and focus/contrast treatments so all
  workspace areas remain reachable without horizontal page overflow.

## 3. Verification and evidence

- [x] 3.1 Update browser E2E tests for the new workspace landmarks, live agent
  roster, deferred rail behaviour, model viewer, and conversation behaviours.
- [x] 3.2 Run the frontend typecheck and production build, plus relevant shop
  tests.
- [x] 3.3 Capture and inspect browser screenshots at desktop and narrow widths
  to confirm the implemented slice matches the reference design and truthfully
  hides unsupported elements.
