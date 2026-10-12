# ADR 0014: Use snapshot-first live state for the Floor browser

**Status:** Accepted

**Date:** 2026-08-09

**Origin:** `snapshot-first-live-state`

**Amends:** [ADR 0001](./0001-go-broker-sse-shop-floor-lifecycle.md)'s
separate lifecycle connection

## Context

The Floor browser learned whether the service was open from one Server-Sent
Events connection, learned run and conversation state from two request-response
endpoints every second, and received subsequent changes from another stream.
The repeated requests were also its accidental bootstrap and recovery path. A
changes-only stream could not restore an initial page or an arbitrarily stale
reconnecting page on its own.

Bounded event replay did not close that gap. `Broker.events` retains twenty
entries for a future activity display, so using it for recovery makes
correctness depend on a display-size choice. A client-held event cursor also
survives longer than the in-memory broker: after the service restarts and
sequence numbers begin at one, retaining the old higher cursor causes the
browser to discard every new event.

The browser also needs to re-read the current model after reconnecting because
model artifact events are intentionally not part of broker state. That
behaviour was attached to the separate lifecycle connection and must survive
its removal.

## Decision

The Floor browser holds one run-agnostic Server-Sent Events connection to
`/api/stream`. Every connection, including an automatic EventSource
reconnection, begins with a `snapshot` frame containing complete run state,
the full ordered conversation, and an explicit `latest_event_sequence`. Live
`shop-floor` events follow on the same connection.

The broker registers the connection's subscriber queue before it serialises
the snapshot, without yielding control between those operations. A publication
during that hand-off is therefore represented in the snapshot and queued for
live delivery. The browser assigns its last-seen sequence from each snapshot
and drops the queued overlap, applying the change exactly once. It never
maximises the snapshot position against a previous process's cursor.

The connection's `onopen` and `onerror` events own the displayed shop lifecycle.
A repeated `onopen` retains the existing model-reconnect nudge so a viewer can
re-read artifacts whose publication events occurred while disconnected.

The browser does not periodically request `/api/runs/latest` or the run's
conversation. The run-specific live-state route remains for non-browser
callers and shares the snapshot-first implementation. `/events/lifecycle`,
the `after` cursor, bounded-history replay, and the broker's long-poll signal
are removed. `Broker.events` and its bound remain an activity-display buffer,
not a recovery log.

## Alternatives rejected

- Retaining the one-second state and conversation poll keeps recovery correct
  but imposes permanent traffic and maintains two competing state paths.
- Replaying `Broker.events` after a client cursor cannot recover more changes
  than the display buffer retains and makes a service restart unsafe.
- Keeping a separate lifecycle stream adds a second connection and a second
  reconnection story for state the live-state connection already exposes.
- Sending a snapshot only on initial page load leaves reconnection as a
  different and weaker recovery mechanism.

## Consequences

- Initial load, ordinary reconnection, and service-restart recovery use the
  same snapshot-first path.
- Idle pages make no repeating run-state or conversation requests.
- Every reconnect transfers the complete conversation. This is deliberately
  accepted for the current local, single-run floor; transcript growth should
  be measured before introducing another recovery mechanism.
- The browser's sequence assignment is process-relative. Changing it back to
  a retained maximum would silently reintroduce the restart failure.
- The subscriber must be discarded for every connection termination,
  including failure while writing the first frame.
