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
- Show a single responsive workspace with menu, artifact, and foreman-chat
  regions at the same browser location.
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

### Establish three named regions with deferred-content states

The application renders a persistent navigation/menu region, an artifact
region, and a foreman-conversation region. The menu owns current shop status,
run identity, and the live roster. Until Stories 3 and 5 provide content, the
other regions explicitly state that no artifact is selected and that the
foreman conversation is not yet available.

Alternatives considered:

- Omitting unfinished regions would leave no durable frame for subsequent
  stories and would make the browser surface look incomplete.
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
- [A desktop three-panel layout could become unusable on narrow screens] → Use
  responsive CSS that keeps every region reachable without horizontal
  overflow.
- [The checked-in static assets could drift from the Vite source] → Rebuild
  the frontend as an explicit implementation task and validate the served
  result in browser coverage.
