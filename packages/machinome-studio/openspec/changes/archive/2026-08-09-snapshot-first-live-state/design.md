# Design: snapshot-first live state

## Context

`floor/app.py` already pushes every published event to subscriber queues, and
`floor/frontend/src/main.tsx` already applies those events to run state, the
conversation, and the model. The live path is event-driven in both directions.
What is missing is a way for a browser to learn the *current situation*, so the
page compensates with `setInterval(load, 1_000)`: `GET /api/runs/latest`, then
`GET /api/runs/{id}/conversation`, then wholesale state replacement, once a
second, for as long as the tab is open.

Three things depend on that timer today, and all three must be answered before
it can go:

1. **Bootstrap.** `connect()` needs `run.id` to build the stream URL, and the
   agent reducer early-returns while run state is null. The first `load()` is a
   prerequisite for the stream doing anything at all.
2. **Missed events.** Reconnection replay is `wait_for_events` filtering
   `Broker.events`, a `deque(maxlen=20)`. Disconnect across more than twenty
   events and the older ones are gone.
3. **Restart.** On a floor restart the broker is new: `agents` empty,
   sequences restarting at one. The page still holds `latestEvent.current` at
   its old high value, `EventSource` reconnects to its frozen original URL, and
   the guard at `main.tsx` discards every event the new process publishes. The
   poll is the only thing that repairs this.

Sprint 003's retained branch `make-shop-floor-event-driven` (`76edeec`) answers
(1) and (2) with a snapshot frame and an atomic subscribe-then-snapshot helper.
It does not answer (3), because that branch predates the position guard: it
removed the cursor entirely, and the guard was introduced afterwards by
`reliable-live-model-event-delivery` to fix a different bug. Porting that
branch as-is onto today's code reintroduces the restart failure in a form the
poll no longer hides.

## Goals / Non-Goals

**Goals**

- No timer-driven re-requesting of state the connection already delivers.
- Correct browser state across page load, dropped connection, and floor
  restart, through one path every connection exercises.
- One live connection to the Floor, not two.

**Non-Goals**

- `floor/watcher.py` is untouched. The model path is already event-driven; the
  competing watcher rewrite on the retained branch is superseded and must not
  be ported.
- No change to the orchestrator delivery stream, the backend adapters, or
  broker profile validation.
- No persistence of broker state across restarts.
- No change to workspace layout, styling, or deferred rail areas.

## Decisions

### A snapshot on every connection, not only the first

The stream's first frame is `event: snapshot`, carrying run state and the
ordered conversation. The browser adopts it wholesale. Because `EventSource`
reconnects on its own, every reconnection re-runs the same path that a first
page load runs, so recovery is not a second mechanism that only executes when
something has already gone wrong.

This retires bounded replay as a recovery mechanism. `Broker.events` and
`event_history_limit` stay exactly as they are — a bounded activity-feed buffer
for a display that does not exist yet. Twenty is a display sizing choice. It is
not a recovery guarantee and must not be treated as one.

### Subscribe before serialising the snapshot

Establishing the connection's subscriber queue *before* reading broker state
converts the old lost-event window into a harmless duplicate: an event
published in between is already reflected in the snapshot and is also sitting
in the queue, so it arrives once more immediately after. The reverse order
drops it.

`reliable-live-model-event-delivery` ratified this guarantee against the old
two-request shape ("including one published before its live-event subscription
is established"). Snapshot-first satisfies it structurally rather than by
compensating replay, so that requirement stays true and keeps its scenario.

### The position guard is assigned from the snapshot, never maximised

The browser keeps its last-seen-event position to drop the subscribe/snapshot
overlap above. That position is **assigned** from each snapshot:

```ts
latestEvent.current = snapshot.run.latest_event_sequence;
```

not `Math.max(latestEvent.current, …)` as today. A restarted floor publishes
from sequence one; a retained higher position would make the page ignore the
new process indefinitely while looking connected. This is the failure the poll
currently masks, it is invisible to any test that does not restart the service
mid-session, and it is the single most important line in this change.

The snapshot carries `latest_event_sequence` explicitly rather than letting the
browser derive it from the last entry of the bounded `events` buffer, which is
wrong when that buffer is empty or has been trimmed.

### The `after` query parameter and its replay are removed

`after` existed to let a reconnecting browser ask for what it missed. With a
snapshot on every connection there is nothing to ask for, and keeping a
client-held cursor is what makes restart unsafe. The stream takes no cursor and
replays nothing.

### `/events/lifecycle` is retired

It answers one question — is the shop open — that the live-state connection
already answers by being connected. Retiring it removes a route, a second
`EventSource`, and a second reconnection story.

Both behaviours currently attached to it move onto the live-state connection:

- `onopen` → shop open; `onerror` → shop closed.
- **`onopen` after a previous open** bumps `modelReconnect`, which nudges the
  mounted viewer to re-read the model. This exists because artifact events
  published while the connection was down are not replayed, and the model is
  not part of broker state, so the snapshot cannot restore it. Dropping this
  when moving the handler would silently regress
  `reliable-live-model-event-delivery`.

### Bootstrap without knowing the run id

`RUN_ID` is the module constant `"shop-floor"`; `/api/runs/latest` is being
asked to report a value that cannot vary. The browser connects to a
run-agnostic `/api/stream` and learns the run identity from the snapshot.
`/api/runs/{run_id}/stream` remains for non-browser callers and shares one
implementation.

`/api/runs/latest` and `/api/runs/{id}/conversation` remain as request-response
endpoints for tests and command-line inspection. They simply stop being part of
the browser's steady state.

## Risks / Trade-offs

- **A larger first frame.** The snapshot carries the whole conversation on
  every reconnection rather than a delta. For a local single-run floor this is
  smaller than one second of the traffic it replaces, and it buys a single
  recovery path. Revisit only if transcript size becomes a measured problem.
- **Losing the poll's accidental liveness check.** The timer also happened to
  notice a wedged service. The connection's `onerror` reports that directly,
  and reports it faster.
- **Porting from a stale branch.** `76edeec` mixes the browser work with a
  superseded `watcher.py` rewrite. Cherry-picking whole commits will drag that
  in. Port the browser and stream hunks deliberately; do not merge or rebase
  the branch.

## Migration Plan

1. Add the snapshot value and subscribe-before-snapshot ordering server-side,
   with the stream still accepting today's clients.
2. Move the browser to the single connection: snapshot handler, assigned
   position, shop-open and model-reconnect handlers.
3. Delete the timer and both bootstrap requests.
4. Remove `/events/lifecycle`, `wait_for_events`, `_event_changed`, and the
   `after` replay.
5. Rebuild the bundle; update ADRs, the overview, and the design README.

## Open Questions

None blocking. `Broker.events` may later gain a real activity display; that
does not change anything decided here.
