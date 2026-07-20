## Context

The ratified lifecycle and agent-roster specifications are implementation
neutral.  The current implementation is a Go process that serves a built
React frontend, provides HTTP/SSE lifecycle endpoints, and stores an
in-memory roster.  The project is otherwise Python-oriented, and this local
broker has no performance evidence requiring a Go runtime.

This change replaces that implementation without changing the two ratified
capabilities.  It retains the existing TypeScript React/Vite user interface
and Python Playwright tests.

## Goals / Non-Goals

**Goals:**

- Run the complete shop-floor application as `python -m floor`.
- Keep all runtime application material under `floor/`, including the built
  frontend served to the browser.
- Preserve default port 9000, supported configuration, HTTP/SSE behavior,
  and the observable agent lifecycle.
- Keep real-browser E2E coverage in Python Playwright.

**Non-Goals:**

- Changing any ratified browser behavior, roster state, or lifecycle
  semantics.
- Adding agent/session discovery, solid-node build observation, project
  browsing, artifact viewing, or chat.
- Rewriting the React interface or changing it from TypeScript/Vite.
- Providing a production deployment or multi-machine broker.

## Decisions

### Decision: FastAPI is the local broker runtime

`floor` is a Python package.  `python -m floor` starts the FastAPI shop-floor
application on port 9000 unless configured otherwise.  The app owns its HTTP
routes, SSE streams, and in-memory active-run roster.

Codex remains responsible for starting and stopping the local process when a
maker asks to open or close the shop; the application entry point itself does
not require a Go binary or Go toolchain.

Alternative considered: retain the Go broker.  Rejected because its separate
runtime is not justified for this single-machine service and imposes extra
setup on a Python project.

### Decision: The React/Vite frontend is preserved inside `floor/`

The existing TypeScript React/Vite source is moved into `floor/` unchanged in
behavior.  Its production build output is also kept under `floor/` and served
by FastAPI.  Running the built application requires Python only; Node is
needed only to rebuild frontend assets during development and tests that
validate the build.

Alternative considered: keep the frontend in a top-level `frontend/`
directory.  Rejected because the requested application boundary is `floor/`.

### Decision: SSE and the public HTTP contract stay stable

FastAPI serves the existing lifecycle and agent-roster endpoints and emits the
same browser-consumable SSE events.  The frontend therefore continues to
show open/closed state and roster changes without a page reload.  Internal
Python structure may differ from Go, but the browser and orchestration
contracts remain equivalent.

Alternative considered: change to polling or redesign the API during the
rewrite.  Rejected because neither is required for the runtime migration and
would alter ratified behavior.

### Decision: Python Playwright remains the end-to-end boundary

The existing Python Playwright tests start and stop `python -m floor`, keep a
browser page open through shutdown and restart, and verify the visible
lifecycle and agent roster.  Python unit/integration tests cover FastAPI
routes, state transitions, SSE, and port configuration.

Alternative considered: replace the E2E suite during the backend rewrite.
Rejected because Python Playwright already provides the required real-browser
proof and is independent of backend internals.

## Risks / Trade-offs

- [FastAPI development server process management differs from the Go command]
  → define and test the agent-operated start/stop procedure against
  `python -m floor`, including readiness and clean shutdown.
- [Serving stale frontend assets] → build assets as part of verification and
  test the page FastAPI actually serves.
- [Runtime migration could accidentally change browser contracts] → preserve
  public endpoint and SSE coverage, plus the existing Playwright scenarios.
- [The single in-memory roster is lost on restart] → this is unchanged from
  the current first-slice scope; reconnect restores shop availability, not
  durable agent state.

## Migration Plan

1. Create the `floor` package and migrate the existing React/Vite source and
   built assets into it.
2. Rebuild the HTTP/SSE broker and lifecycle state in FastAPI, preserving the
   public contract and default port 9000.
3. Adapt Python unit and Playwright E2E tests to launch only `python -m floor`;
   demonstrate their failures before the FastAPI behavior is complete.
4. Remove the replaced Go implementation and Go-specific test/build wiring
   only after the Python and frontend suites pass.
5. Amend ADRs 0001 and 0002 in place, then archive this OpenSpec change after
   acceptance.

## Review Status

The pilot ratified the `shop-floor-lifecycle` behavioral delta and all four
decisions in this design on 2026-07-19. ADRs 0001 and 0002 will be amended in
place after implementation and verification succeed.
