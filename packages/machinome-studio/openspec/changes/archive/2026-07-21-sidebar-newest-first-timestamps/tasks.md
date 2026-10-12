## 1. Broker event timestamp

- [x] 1.1 Add a UTC publication timestamp to the broker-event browser value.
- [x] 1.2 Add broker API tests proving event snapshots and live events include
  the recorded timestamp.

## 2. Newest-first event menu

- [x] 2.1 Extend the browser event type and render each event's timestamp in a
  readable local form.
- [x] 2.2 Render the bounded event history newest-first without mutating the
  chronological broker data.

## 3. Verification

- [x] 3.1 Extend the browser lifecycle test to prove live and reloaded logs
  show the newest event first, display timestamps, retain only the configured
  bound, and omit private message text.
- [x] 3.2 Run the focused backend and browser test suites, then inspect the
  event sidebar in the browser for compactness and agent-roster adjacency.
