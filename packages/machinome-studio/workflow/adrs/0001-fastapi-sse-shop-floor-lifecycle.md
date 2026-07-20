# ADR 0001: Use FastAPI and Server-Sent Events for shop-floor lifecycle

**Status:** Accepted

**Date:** 2026-07-19

## Context

Sprint 1 establishes shop-floor as a browser interface operated by Codex for a
maker. The first slice must let Codex open and close the local interface while
an already-open browser page visibly changes from `Shop is open` to `Shop is
closed` and back after a restart, without a page reload.

The decision must provide a stable local location for the browser and a
one-way indication that the running service is still connected. It must not
preempt later Sprint 1 work on agents, projects, design views, or maker chat.

## Decision

Shop-floor is a local FastAPI service. Codex starts and stops it through the
shop-floor lifecycle command. Its default local browser location uses port
9000, and an agent can override that port when opening the service.

The browser page maintains a Server-Sent Events connection to the service's
lifecycle endpoint. A connected stream displays `Shop is open`; a lost stream
displays `Shop is closed`. The browser's EventSource reconnection restores the
open state when Codex restarts FastAPI at the same location.

The initial page contains only this lifecycle status. Later stories own the
menu, artifact view, and foreman conversation areas.

## Consequences

- The agent—not the maker—operates the local service lifecycle.
- Shutdown must wait until the service is actually unavailable before reporting
  that it is closed, so the browser can receive the SSE disconnect.
- The lifecycle is covered by a real Playwright test that keeps one browser
  page open across shutdown and restart; failure retains a screenshot and
  trace.
- Server-Sent Events are sufficient for this one-way lifecycle signal. Later
  bidirectional maker-to-foreman interaction needs a separate decision.
