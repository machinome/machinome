# ADR 0002: Use Python Playwright for shop-floor browser E2E tests

**Status:** Accepted

**Date:** 2026-07-19

## Context

Shop-floor's broker is implemented in Go, but its first durable promise is
what a maker sees in a real browser while the service opens, closes, and
restarts. The project already has Python expertise and the pilot wants its
browser E2E coverage to remain in Python.

## Decision

Browser end-to-end tests use Playwright's Python bindings. Tests start and
stop the compiled Go broker only through its public lifecycle command, keep
one browser page open, and assert `Shop is open`, `Shop is closed`, and
`Shop is open` again without a page reload.

Go unit and integration tests remain responsible for Go-internal lifecycle,
HTTP, SSE, configuration, and process-management behavior.

## Consequences

- The E2E test validates the compiled broker and its public lifecycle seam,
  rather than implementation internals.
- Python Playwright and its browser runtime become test-only dependencies.
- Test failures retain Playwright trace and screenshot evidence.
- The browser test runner is deliberately independent from the broker's
  implementation language.
