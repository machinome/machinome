## Context

`docs/product/sprints/SPRINT-001-shop-floor-interface.md` remains the source
of truth. It describes shop-floor as the browser-based broker run by Codex for
a maker. The archived lifecycle slice established the externally observable
open, close, and reconnect behavior, but selected FastAPI before the broker's
long-lived local-service role had been considered.

The broker will later observe Codex sessions and the Python machinist's
file-level build outputs. Those integrations are intentionally not part of
this first Go slice.

## Goals / Non-Goals

**Goals:**

- Rebuild the lifecycle slice as a Go broker while preserving all ratified
  maker-visible behavior.
- Keep port 9000 as the default local browser location and make it
  configurable.
- Retain an independent, real-browser E2E proof across shutdown and restart.
- Leave a clean Go boundary for future read-only observers.

**Non-Goals:**

- Discovering or controlling Codex agents.
- Reading solid-node artifacts or invoking the Python machinist.
- Implementing the sprint's menu, viewer, or chat behavior.
- Reusing the previous Python implementation as a source baseline.

## Decisions

### Decision: The shop-floor broker is a single Go process

The lifecycle server, browser page, SSE endpoint, and agent-facing lifecycle
command will be implemented in Go. The command starts a detached broker
process, records only the process identity needed for a matching close, waits
for readiness before reporting open, and waits for unavailability before
reporting closed.

Go supplies the process-lifecycle, HTTP, SSE, cancellation, and later
filesystem-observer primitives in one deployable runtime. The broker does not
embed Python or solid-node; future build observation will consume an explicit
file-level contract produced by the Python machinist.

Alternative considered: retain FastAPI and add Go only when observation is
needed. Rejected because it creates a runtime boundary at the broker's core
before any Python integration requires one.

### Decision: Server-Sent Events remain the lifecycle transport

The Go broker serves the browser page and a long-lived lifecycle SSE endpoint.
A connected stream means `Shop is open`; a lost stream means `Shop is closed`.
Native EventSource reconnection restores the open state after a broker restart
at the same browser location.

Alternative considered: polling. Rejected because the pilot requires SSE to
keep the browser's availability state open.

### Decision: Python Playwright owns browser E2E tests

The browser E2E test will run through Python Playwright. It starts and stops
the compiled broker only via its public lifecycle command, retains one page
through the shutdown/restart sequence, and asserts all three visible states.
Go unit and integration tests own broker-internal behavior.

Alternative considered: Go-only browser testing or JavaScript Playwright.
Rejected because the pilot wants Playwright E2E to remain in Python, while Go
tests are the natural home for Go-internal contracts.

## Risks / Trade-offs

- [The team is new to Go] → keep this slice to standard-library HTTP/SSE and
  small testable packages; do not introduce observers yet.
- [A detached broker can outlive its lifecycle command] → use explicit PID
  state, readiness, and unavailability checks covered by Go tests and E2E.
- [Browser tests can disagree with lifecycle tests] → E2E controls the same
  public compiled command a Codex agent will use.
- [Future observer formats can change] → keep observer interfaces separate
  from broker lifecycle and make session/file parsing an additive change.

## Migration Plan

1. Add the Go broker and equivalent lifecycle command with the same default
   port and configuration behavior.
2. Move the browser lifecycle test to Python Playwright and demonstrate the
   existing test fails before the Go behavior is complete.
3. Remove the replaced Python service and JavaScript browser-test wiring only
   after Go and Python test suites pass.
4. Roll back by restoring the prior implementation commit if the new broker
   cannot meet the lifecycle specification.

## Review Status

The pilot ratified the modified `shop-floor-lifecycle` specification and all
three decisions in this design on 2026-07-19. The ADRs remain proposed until
the corresponding implementation and verification succeed.
