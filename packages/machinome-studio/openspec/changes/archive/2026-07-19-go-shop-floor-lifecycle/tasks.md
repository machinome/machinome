## 1. Go broker foundation

- [x] 1.1 Create the Go module and compiled `shop-floor` lifecycle command.
- [x] 1.2 Implement configurable-port process start, readiness, PID state,
  shutdown, and unavailability confirmation.
- [x] 1.3 Add Go unit tests that demonstrate lifecycle and port failures before
  the implementation turns them green.

## 2. Browser lifecycle service

- [x] 2.1 Serve the minimal browser page and lifecycle health endpoint from the
  Go broker.
- [x] 2.2 Implement the lifecycle SSE stream and browser open/closed/reconnect
  behavior.
- [x] 2.3 Add Go HTTP/SSE tests for the broker endpoints and configuration.

## 3. Python browser E2E

- [x] 3.1 Add Python Playwright test dependencies and test command without
  retaining JavaScript Playwright wiring.
- [x] 3.2 Rebuild the real browser lifecycle test to control the compiled
  broker through its public command and retain one page through close/reopen.
- [x] 3.3 Demonstrate the E2E test fails against incomplete behavior, then
  passes against the completed Go broker.

## 4. Migration and acceptance

- [x] 4.1 Remove the replaced Python/FastAPI service and obsolete test and
  package wiring after replacement coverage passes.
- [x] 4.2 Run Go tests, Python Playwright E2E, OpenSpec strict validation, and
  whitespace validation.
- [x] 4.3 Manually verify the browser's open, close, and reopen states on the
  default port 9000.
- [x] 4.4 Mark the rebuilt ADRs accepted after successful implementation.
