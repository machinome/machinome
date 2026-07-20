## Why

The first shop-floor slice proved the maker-visible lifecycle but implemented
the broker shell in Python. Shop-floor will grow into a local broker that
observes agents and build artifacts; rebuilding this first slice in Go gives
that broker one native runtime from the beginning while preserving its
ratified browser behavior.

## What Changes

- **BREAKING** Replace the Python/FastAPI shop-floor lifecycle service and
  agent-facing lifecycle command with a Go broker and its lifecycle command.
- Preserve the stable, configurable local browser location and its
  open/closed/reopen-without-reload behavior.
- Preserve the real browser lifecycle test, rebuilding it as a Python
  Playwright E2E test that controls the compiled Go broker through its public
  lifecycle command.
- Rebuild ADR 0001 to record the Go broker decision, and add an ADR recording
  Python as the E2E test harness.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `shop-floor-lifecycle`: remove the FastAPI implementation constraint while
  preserving the maker-visible lifecycle behavior and the agent-operated
  service contract.

## Impact

- Replaces the Python package and Uvicorn dependency with a Go module and
  compiled broker command.
- Replaces JavaScript Playwright test wiring with Python Playwright wiring;
  browser coverage remains end-to-end.
- Rebuilds the existing lifecycle ADR and adds one test-strategy ADR.
- Establishes a Go process boundary suitable for a later Codex-session and
  solid-node build observer; neither observer is introduced in this change.
