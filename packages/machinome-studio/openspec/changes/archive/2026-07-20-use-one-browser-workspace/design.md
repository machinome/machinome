## Context

The FastAPI shop floor already serves a Vite-built React page with shop
lifecycle status and a live manifested-agent roster. It currently presents
only that roster. Story 2 makes the frontend the stable application frame for
the rest of Sprint 001: Story 3 will make the foreman conversation live, and
Story 5 will make artifact inspection live.

The frame must retain the existing lifecycle and roster behavior while
avoiding a new server contract for content which does not yet exist.

## Goals / Non-Goals

**Goals:**

- Use React, built and bundled by Vite, as the shop-floor application frame.
- Show a single, full-height responsive workspace with a persistent left menu
  and a right content column split into artifact view (60%) above foreman chat
  (40%).
- Keep lifecycle state and the manifested-agent menu live through the existing
  browser APIs.
- Give unimplemented artifact and chat regions truthful, useful empty states.

**Non-Goals:**

- Sending messages to the foreman or retaining conversation history.
- Rendering, selecting, exporting, or otherwise inspecting real artifacts.
- Adding a new FastAPI API, persistence layer, or real-time transport.
- Redesigning the shop lifecycle or agent-lifecycle protocols.

## Decisions

### Keep one React + Vite application and one browser route

The existing `floor/frontend` React source remains the authoring location and
Vite remains responsible for producing the assets served by FastAPI at `/`.
The workspace is rendered by that one application rather than composing
separate server-rendered pages or creating routes for each panel. This gives
later stories a shared application shell and preserves the stable local URL.

Alternatives considered:

- Server-rendered HTML panels would duplicate browser state and make the later
  interactive surfaces harder to compose.
- Separate pages or browser tabs would not meet the one-workspace outcome.

### Establish an application shell, not three cards

The application uses the full browser viewport. A fixed-width left menu spans
the viewport height and owns the shop identity, lifecycle status, run identity,
and live roster. The remaining width is one content column, divided into a
60% artifact view above a 40% foreman-conversation pane. Borders separate
structural panes; they are not independently floating cards.

This follows the app-shell treatment in `langchain-ai/agent-chat-ui`: a
full-height, overflow-controlled workspace, an understated separated sidebar,
and content panes that dominate the screen. It does not copy that project's
components, dependencies, or chat protocol.

Until Stories 3 and 5 provide content, the view and chat panes explicitly
state that no artifact is selected and that the foreman conversation is not
yet available.

Alternatives considered:

- A top header and three equal-looking cards were rejected because they turn
  the required application frame into a dashboard and leave the artifact view
  without the visual priority it needs.
- Showing invented sample chat or artifact data would misrepresent shop state.

### Preserve the current FastAPI boundary

The React application continues to read `/events/lifecycle`,
`/api/runs/latest`, and the current run stream. The layout does not require a
new endpoint because it introduces only frame structure and empty states.

Alternatives considered:

- Adding placeholder endpoints would establish API contracts before the
  product stories that define their meaning.

## Risks / Trade-offs

- [The empty panels could be mistaken for unavailable functionality] → Label
  them as pending surfaces, not as failed loads, and preserve the working menu
  feedback.
- [The desktop split could become unusable on narrow screens] → Collapse the
  shell to a vertical sequence at the breakpoint while keeping every region
  reachable without horizontal overflow.
- [The checked-in static assets could drift from the Vite source] → Rebuild
  the frontend as an explicit implementation task and validate the served
  result in browser coverage.
