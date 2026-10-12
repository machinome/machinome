## Why

The shop floor is meant to be event-driven end to end, but two periodic polls
survive in the live path. The browser re-fetches whole run state and the whole
conversation every second, and the model watcher walks and stats every project
`.py` file twice a second before it will consider building. The browser poll is
not merely wasteful: it is the only thing repairing state lost while the
Server-Sent Events connection was down, because that stream offers no snapshot
and no recovery. The filesystem poll costs up to ~1.5s of latency between a save
and a rebuild, and its cost grows with project size.

## What Changes

- The browser's live-state Server-Sent Events stream opens every connection with
  a snapshot frame carrying run state and the full conversation, so a connecting
  or reconnecting page needs no REST bootstrap and no reconciliation.
- The service registers a client's event subscription before serialising that
  snapshot, so no event published between the two is lost.
- The browser drops its one-second `setInterval` and its periodic
  `/api/runs/latest` and `/api/runs/{id}/conversation` fetches entirely.
- The separate `/events/lifecycle` stream is retired; the one live-state stream's
  own connection state reports whether the shop is open. **BREAKING** for any
  client depending on `/events/lifecycle`; the shop's own browser page is the
  only such client.
- The model watcher observes the project source through filesystem
  notifications instead of periodic scanning, coalescing bursts with a short
  quiet-period debounce rather than a two-scan stability rule. Where filesystem
  notification is unavailable, it falls back to scanning as a documented
  degraded mode.
- `Broker.wait_for_events`, currently unused long-poll scaffolding with no
  caller, is removed.
- `Broker.events` and its `event_history_limit` stay exactly as they are: a
  bounded activity-feed buffer for a deferred display, load-bearing for nothing.

## Capabilities

### New Capabilities

- `shop-live-state-stream`: how live shop state reaches a connected browser —
  one stream, a complete snapshot on every connection, live events thereafter,
  and the prohibition on periodic re-fetching of state the stream already
  provides.

### Modified Capabilities

- `shop-floor-lifecycle`: the requirement that the browser shows the shop
  lifecycle without a reload no longer names a dedicated lifecycle-status
  stream, and reconnection after a service restart must restore correct state
  rather than only the words `Shop is open`.
- `functional-model-inspection`: the refresh requirement gains an obligation to
  notice a model source change through filesystem notification promptly, rather
  than at the cadence of a periodic scan.

## Impact

- `floor/app.py` — snapshot frame on connect, subscription-before-snapshot
  ordering, removal of `/events/lifecycle`, removal of `wait_for_events`.
- `floor/watcher.py` — filesystem-notification observer, debounce, thread-to-loop
  bridge; the build serialisation, `_build` exclusion, and viewer snapshot
  hashing are preserved unchanged.
- `floor/frontend/src/main.tsx` — one `EventSource`, no interval, no bootstrap
  fetches, snapshot handling, and removal of the `lifecycleOpened` ref.
- `pyproject.toml` — the shop takes a direct dependency on the filesystem
  notification library the framework already uses.
- `tests/test_model_watcher.py` is written around the poll interval and must be
  retargeted to the debounce window. `tests/test_floor_api.py` covers the stream;
  `tests/test_broker.py` covers the removed `wait_for_events`.
- `docs/architecture-overview.md` describes the browser transport;
  `docs/design/README.md` already states the intended behaviour and needs no
  change.
- The REST routes `/api/runs/latest` and `/api/runs/{id}/conversation` remain for
  tests and non-browser clients; only the browser's periodic use of them ends.
