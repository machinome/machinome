## Why

The broker-event menu currently grows downward in recorded order and identifies
entries only by sequence number. A maker must scroll away from the agent roster
to see the most recent activity, and cannot tell when an event occurred.

## What Changes

- Present the broker-event log newest-first, with the newest event immediately
  below the agent roster.
- Include a readable timestamp for every displayed broker event.
- Preserve the bounded event history, live updates, reload behavior, and the
  existing privacy boundary that omits instruction and report bodies.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `shop-browser-workspace`: Change the broker-event log's display order and
  require a timestamp on each event entry.

## Impact

The shop-floor broker event representation, browser event-log rendering, and
its API/browser tests will change. No external dependencies or public
transport endpoints are expected to change.
