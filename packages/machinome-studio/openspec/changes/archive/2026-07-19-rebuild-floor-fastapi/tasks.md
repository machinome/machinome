## 1. FastAPI application boundary

- [x] 1.1 Create the `floor` Python package and `python -m floor` entry point
  with port 9000 as its default and documented configuration.
- [x] 1.2 Move the existing React/Vite source and production assets under
  `floor/`, preserving its TypeScript behavior and FastAPI-served page.
- [x] 1.3 Add Python unit tests that first demonstrate missing or incorrect
  FastAPI lifecycle, port, and static-page behavior.

## 2. Preserve broker behavior

- [x] 2.1 Implement lifecycle HTTP/SSE behavior in FastAPI without changing
  the visible open, closed, and reconnect behavior.
- [x] 2.2 Implement the active-run roster and manifest, assignment,
  acknowledgement, completion, and stop transitions in FastAPI.
- [x] 2.3 Add Python route/state/SSE tests covering valid transitions and
  ignored invalid reports.

## 3. Browser proof

- [x] 3.1 Retain and adapt Python Playwright E2E tests so they launch
  `python -m floor` and exercise the page FastAPI serves.
- [x] 3.2 Demonstrate the browser tests fail before FastAPI supplies the
  lifecycle and roster behavior, then pass after implementation.

## 4. Migration and hygiene

- [x] 4.1 Remove the superseded Go implementation, its module metadata, and
  Go-only tests/build scripts after replacement coverage passes.
- [x] 4.2 Amend ADR 0001 and ADR 0002 in place to reflect FastAPI and the
  preserved Python E2E boundary.
- [x] 4.3 Run Python tests, Python Playwright E2E, frontend TypeScript/build
  checks, OpenSpec strict validation, and whitespace validation.
- [x] 4.4 Manually verify the browser on default port 9000 through open,
  close, restart, and agent roster transitions.
