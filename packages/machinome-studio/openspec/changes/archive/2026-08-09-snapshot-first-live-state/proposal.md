# Snapshot-first live state

## Why

The Floor browser asks the service what the whole run is, once a second,
forever. `main.tsx` runs `setInterval(load, 1_000)`, and each tick issues
`GET /api/runs/latest` followed by `GET /api/runs/{id}/conversation` and
overwrites React state from the results. Every open page costs the service two
requests a second for the life of the shop.

Almost nothing it asks for can change. Of the eight fields `broker.run()`
returns, six are fixed for the life of the process — `id` is the module
constant `RUN_ID`, `status` is the literal `"running"`, and `profile_id`,
`user_label`, `user_agent` and `roster` come from the profile loaded at
startup. A seventh, `events`, is a bounded display buffer rendered nowhere.
Only `agents` varies, and every change to it already publishes an event the
live stream carries and the browser already applies.

The poll survives because the live stream reports *changes* and never reports
the *situation*. A page that has just loaded knows nothing until it asks, and
a page whose stream dropped has no way to learn what it missed. The timer is
the only thing repairing both. That is a real dependency, not an oversight,
and it is why the poll cannot simply be deleted.

Sprint 003 (`make-shop-floor-event-driven`, branch retained as reference) built
the fix and never landed it. Its browser and stream work — a snapshot frame on
connect, subscription established before the snapshot is serialised, the timer
deleted — is sound and is the basis of this change. Its `watcher.py` rewrite is
superseded by what `floor-artifact-event-pipeline` and
`reliable-live-model-event-delivery` shipped, and is explicitly out of scope
here: the model path is already event-driven and this change does not touch it.

## What Changes

- The Floor browser's live-state stream opens **every** connection with a
  snapshot frame carrying run state and the ordered conversation, so a
  connecting or reconnecting page needs no bootstrap request and no
  reconciliation pass.
- The service **registers a connection's event subscription before serialising
  that snapshot**, so an event published between the two is delivered after the
  snapshot rather than lost.
- The browser **drops its one-second `setInterval`** and its periodic
  `/api/runs/latest` and `/api/runs/{id}/conversation` requests entirely.
- The browser **resets** its last-seen-event position from each snapshot
  instead of keeping the higher of the two. A restarted floor numbers its
  events from one again; a retained position silently discards everything the
  new process publishes. See `design.md` — this is the one place where the
  retained sprint-003 work is insufficient against today's code, because that
  work predates the position guard.
- **BREAKING (shop-internal browser surface):** `/events/lifecycle` is retired.
  The live-state stream's own connection state reports whether the shop is
  open, which is what the separate stream was doing with an extra connection
  and an extra route. The Floor's own page is its only client.
- `Broker.wait_for_events` and the `_event_changed` signal are removed with the
  long-poll shape they served; the stream is driven by the per-connection
  subscriber queue the broker already fills on every publish.
- `Broker.events` and `event_history_limit` are unchanged: a bounded
  activity-feed buffer for a deferred display. They are not a recovery
  guarantee and must not become one.

## Capabilities

### New Capabilities

- `shop-live-state-stream`: how the current situation and subsequent changes
  reach a connected Floor browser — one connection, a complete snapshot on
  every connection including reconnection, live events thereafter, and the
  prohibition on periodically re-requesting state the connection already
  delivers.

### Modified Capabilities

- `shop-floor-lifecycle`: the requirement that the browser shows the shop
  lifecycle without a reload no longer names a dedicated lifecycle-status
  stream, and restoring after a service restart must restore *correct state*
  rather than only the words `Shop is open`.
- `shop-user-conversation`: surviving a browser reload is satisfied by the
  connection's snapshot rather than by a separate conversation request.

## Impact

- `floor/app.py` — snapshot value; subscription-before-snapshot ordering;
  removal of `wait_for_events`, `_event_changed`, and the `/events/lifecycle`
  route.
- `floor/frontend/src/main.tsx` — snapshot handler; position reset; deletion of
  the interval, both bootstrap requests, and the second `EventSource`.
- `floor/static/` — rebuilt bundle.
- `tests/test_broker.py`, `tests/test_floor_api.py`,
  `tests/test_orchestrator.py`, `tests/test_shop_lifecycle_e2e.py` — retarget
  coverage from the retired surfaces; add reconnection, restart, and ordering
  cases.
- `docs/adrs/` — one ADR amending ADR 0001's separate lifecycle stream.
- `docs/architecture-overview.md`, `docs/design/README.md` — the Floor's
  browser data layer is one connection, not four endpoints and two streams.
- Not in scope: `floor/watcher.py`, the orchestrator delivery stream, backend
  adapters, workspace layout or styling.
