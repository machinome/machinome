## Why

Shop-floor is a local, single-machine application with no demonstrated
performance bottleneck that requires Go.  Its Go broker introduces a second
application runtime and environment for a project otherwise developed in
Python.  Rebuilding the broker in FastAPI keeps the service in the project's
primary language while retaining the ratified maker-visible experience.

## What Changes

- **BREAKING** Replace the Go `shop-floor` broker and its lifecycle command
  with a FastAPI application contained in `floor/` and launched with
  `python -m floor`.
- Preserve the existing TypeScript React/Vite browser interface and its
  current lifecycle and agent-roster behavior.
- Preserve the Python Playwright E2E suite and make it exercise the FastAPI
  application through its public browser interface.
- Keep port 9000 as the default local browser location and retain explicit,
  supported port configuration.
- Amend ADR 0001 in place to record FastAPI as the broker runtime while
  retaining SSE; amend ADR 0002 in place only as needed to describe the
  FastAPI test target.  Do not create replacement ADRs.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `shop-floor-lifecycle`: make the default local browser location explicit as
  port 9000 while preserving its existing open/close behavior.

The `shop-agent-lifecycle` capability remains unchanged.

## Impact

- Removes Go source, module metadata, compiled-command assumptions, and
  Go-only tests for the shop-floor service.
- Adds the `floor` Python package, FastAPI runtime dependencies, and its
  Python test coverage.
- Moves the frontend source and its production assets into the `floor/`
  application boundary without changing its React/Vite behavior.
- Keeps Playwright Python as the browser E2E harness; Node remains a
  development-time frontend build dependency, not a second server runtime.
