# ADR 0001: Use a FastAPI broker and Server-Sent Events for shop-floor lifecycle

**Status:** Accepted

**Date:** 2026-07-19

## Context

Sprint 1 establishes shop-floor as a browser interface operated by Codex for a
maker. The first slice must let Codex open and close the local interface while
an already-open browser page visibly changes from `Shop is open` to `Shop is
closed` and back after a restart, without a page reload. Shop-floor is the
beginning of a broker that will later observe agent sessions and Python
machinist build artifacts.

The decision must provide a stable local location for the browser and a
one-way indication that the running service is still connected. It must not
preempt later Sprint 1 work on agents, projects, design views, or maker chat.

## Decision

Shop-floor is a local FastAPI broker contained in `floor/`. Codex starts and
stops it with `python -m floor`. Its default local browser location uses port
9000, and an agent can override that port when opening the service.

The browser page maintains a Server-Sent Events connection to the service's
lifecycle endpoint. A connected stream displays `Shop is open`; a lost stream
displays `Shop is closed`. The browser's EventSource reconnection restores the
open state when Codex restarts the broker at the same location.

The initial page contains only this lifecycle status. Later stories own the
menu, artifact view, and foreman conversation areas.

## Consequences

- The agent—not the maker—operates the local service lifecycle.
- Shutdown must wait until the service is actually unavailable before reporting
  that it is closed, so the browser can receive the SSE disconnect.
- The FastAPI broker owns its Python unit and integration tests. A Python
  Playwright test covers the public browser lifecycle across shutdown and
  restart; failure retains browser evidence.
- Server-Sent Events are sufficient for this one-way lifecycle signal. Later
  bidirectional maker-to-foreman interaction needs a separate decision.
