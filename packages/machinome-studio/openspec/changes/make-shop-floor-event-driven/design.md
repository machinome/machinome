## Context

`floor/app.py` already pushes broker events to the browser over Server-Sent
Events (`/api/runs/{id}/stream`), and the orchestrator already consumes envelopes
from a queue-backed stream. The backend adapters sit on blocking read loops. The
live path is therefore event-driven everywhere except two places:

- `floor/frontend/src/main.tsx:274` runs `setInterval(load, 1_000)`, issuing
  `GET /api/runs/latest` and `GET /api/runs/{id}/conversation` every second and
  overwriting React state from those snapshots.
- `floor/watcher.py:73` sleeps `poll_interval` (0.5s), then `os.walk`s the whole
  project and `stat`s every `.py`, requiring the fingerprint to be stable across
  two consecutive scans before it will build.

The browser poll is load-bearing today. `EventSource` reconnects automatically,
but the stream sends nothing on connect and the client holds no position in the
event history, so any event published while the connection was down is lost. The
one-second re-fetch is the only thing that repairs that. Removing the poll
without adding recovery would convert a hidden inefficiency into visible dropped
conversation entries and stale agent state.

One existing structure invites misuse and is deliberately left alone.
`Broker.events` is `deque(maxlen=event_history_limit)` with a default of 20, and
`broker.run()` ships it to the browser, which mirrors the bound at
`main.tsx:230`. It is an activity-feed buffer for a panel that does not exist —
`run.events` is rendered nowhere, and `shop-browser-workspace` explicitly defers
activity transcript rows. Twenty is a display sizing choice. It is not a
recovery guarantee and must not become one.

`Broker.wait_for_events(after)` at `app.py:294` is long-poll scaffolding with no
caller.

## Goals / Non-Goals

**Goals:**

- No timer-driven re-fetching of state the stream already delivers.
- Correct browser state across disconnection, service restart, and reload, by a
  single path that every reconnection exercises.
- Model rebuild latency bounded by a debounce window rather than a scan cadence,
  and independent of project size.
- Preserve every behaviour the current watcher defends: one build at a time,
  burst coalescing, no self-triggering from the build tree, and `model_changed`
  gated on the published viewer snapshot actually changing.

**Non-Goals:**

- The framework (`solid-node/`) is untouched. `solid develop`'s own watcher is
  reference, not scope.
- No change to the orchestrator delivery stream, the backend adapters, or the
  broker's profile validation.
- No persistence of broker state across restarts.
- No incremental event replay, and no client-side event cursor. See below.
- No change to the workspace layout, styling, or deferred rail areas.

## Decisions

### Snapshot on every connection; no replay, no cursor

Every live-state connection opens with `event: snapshot` carrying run state and
the complete conversation. Reconnection is not a special case: the browser
replaces its state wholesale and continues from live events.

*Alternative considered and rejected:* sequence-labelled frames (`id:`) plus
`Last-Event-ID` replay of missed events. This was the original shape of this
design and it is worse on three counts.

First, the only retained history available to replay from is `Broker.events`,
whose bound is a display sizing choice. Building recovery on it couples
correctness to a number someone will reasonably change when they finally build
the activity panel, with nothing in the code to warn them.

Second, the arithmetic makes replay nearly vestigial. A delegated Fordesmac run
emits `assignment_available`, `envelope_delivered`, `work_acknowledged`,
`conversation_entry` and `model_build_succeeded` in quick succession; twenty
events pass in a second or two of active work. Replay would fire only for
reconnections shorter than the drop that caused them, so the recovery path that
matters most would be the one least exercised.

Third, replay needs a valid-cursor test, which needs an epoch identifier,
because `RUN_ID` is the constant `"shop-floor"` and `latest_event_sequence`
resets in memory — after a restart a stale cursor looks *ahead* of the server.
That is real machinery whose entire purpose is deciding when to fall back to the
snapshot. Since the snapshot is always correct — `broker.conversation` is an
unbounded complete list and `broker.run()` is small — the honest conclusion is
that there is no case where the snapshot is the wrong answer.

No epoch identifier is added either. Its only justification was the cursor test;
with the snapshot authoritative, a client needs nothing to distinguish floors,
because the snapshot already describes whichever floor it connected to. Adding a
field nothing consumes would repeat the `wait_for_events` mistake this change is
cleaning up.

The cost is re-sending the conversation on each reconnection. On a local
single-user shop over loopback that is tens of kilobytes on a rare event —
strictly cheaper than the poll it replaces, which sent the same conversation
every second unconditionally.

### Subscribe before serialising the snapshot

The snapshot is the stream's first frame rather than a preceding `fetch`. A
fetch-then-connect bootstrap loses anything published between the two calls.
Registering the subscriber queue in `broker.subscribers` *before* the snapshot is
serialised closes that race by construction: an event published in between lands
in the queue and is delivered after the snapshot. The client's existing
sequence-based dedup makes the overlap harmless if an event is represented in
both.

### `/events/lifecycle` is retired

Its whole payload is "connected". The live-state stream's `onopen`/`onerror`
carry the same signal, so `shopOpen` and the `modelGeneration` bump on reopen
move onto the single connection and the `lifecycleOpened` ref disappears. This
is the only external-surface removal in the change; the shop's own page is the
only client.

### Watchdog observer with a quiet-period debounce

`ModelWatcher` keeps its class, its publish contract, its `_build` exclusion
rules and its `viewer.json` content hash. Only change detection changes: a
`watchdog` `Observer` scheduled recursively on `project_root`, with a
`FileSystemEventHandler` that filters to `.py` paths surviving
`_excluded_directory`, and bridges to the loop with `call_soon_threadsafe` onto
an `asyncio.Queue`. This is the idiom the framework already uses in
`solid_node/core/builder.py` (`schedule(..., recursive=True)`,
`loop.call_soon_threadsafe`), so the shop is not inventing a second pattern.

The handler observes created, modified, moved and deleted events, not modified
alone — `builder.py` implements only `on_modified`, and an editor saving through
a temporary file and a rename produces no modify event on the target. The
current fingerprint comparison catches that case only because it compares state
rather than events, so moving to notifications without widening the event set
would be a regression.

The two-scan stability rule becomes an explicit debounce: on the first event,
arm a ~200ms timer; each further event re-arms it; build when it expires. That
preserves both properties the current comment defends — not building mid-write,
and coalescing a multi-file save — while cutting worst-case latency from ~1.5s to
~0.2s. The existing single-build-with-`pending`-coalescing loop is unchanged
downstream of the debounce.

*Alternative considered:* `inotify` directly. Rejected — `watchdog` is already a
framework dependency, is cross-platform, and handles new directories appearing
under a recursive watch.

*Fallback:* where `inotify` is unavailable (some network filesystems and
container configurations), `watchdog.observers.polling.PollingObserver` provides
today's behaviour as a documented degraded mode. The spec's obligations are
written so the fallback still satisfies them.

### The `_build` exclusion stays a correctness requirement

Under `inotify` the loop is tighter and faster than it was under polling: a
rebuild writes into the watch tree and would immediately re-arm the debounce.
The existing `EXCLUDED_DIRECTORIES` / `EXCLUDED_PREFIXES` filtering must be
applied in the handler, before anything is queued, and this is worth a dedicated
test rather than trust.

## Risks / Trade-offs

- **Dropped events become silent rather than self-healing.** Today the poll hides
  any stream gap. After this change a snapshot bug shows up as missing state with
  no second chance. → Mitigated by there being exactly one recovery path, taken
  on every connection, with direct coverage for the disconnect-during-
  conversation and disconnect-during-work-state cases.
- **Wholesale state replacement on reconnect.** The snapshot overwrites `run` and
  `conversation`, which could clobber an optimistic local append. → This is
  already how the one-second poll behaves, and the existing sequence dedup in
  `submitUserMessage` covers it; the composer draft lives in separate state and
  is untouched.
- **Conversation size on reconnect.** A very long session re-sends a large
  transcript on each reconnection. → Acceptable at shop scale and on loopback. If
  it ever matters, the fix is a bounded snapshot with an explicit "load earlier"
  request, not a replay cursor.
- **`inotify` watch limits.** A very large project tree can exhaust
  `max_user_watches`. → Surface the observer's failure as a reportable watcher
  error and fall back to `PollingObserver` rather than dying silently, matching
  how `_publish_failure` already treats an unusable `solid` command.
- **Debounce window is a guess.** Too short reintroduces mid-write builds; too
  long adds latency. → 200ms with the window as a constructor parameter, which is
  also what makes the tests deterministic.
- **Test churn.** `tests/test_model_watcher.py` is written entirely around `POLL`
  (`sleep(POLL * 4)`, `sleep(POLL * 8)`). → It is retargeted to the debounce
  parameter; the assertions about published events are unchanged, which is the
  point of keeping the publish contract stable.
- **New direct dependency.** The shop takes `watchdog` directly rather than
  inheriting it from the framework. → Intentional; the shop should declare what
  it imports.

## Migration Plan

Order matters — the frontend deletion is only safe once the snapshot exists.

1. Watcher first. Self-contained, no protocol implications, largest latency win,
   and independently shippable.
2. Server-side snapshot frame and subscribe-before-snapshot ordering. The browser
   still polls at this point, so a defect here is masked and caught by tests
   rather than by the maker.
3. Frontend: single `EventSource`, snapshot handling, delete the interval and
   the bootstrap fetches.
4. Remove `/events/lifecycle` and `wait_for_events`, and update
   `docs/architecture-overview.md`.

Rollback for step 3 is restoring the interval; steps 1 and 2 are independently
revertible. `docs/design/README.md:217` already states the target behaviour and
needs no change.

## Open Questions

None outstanding. `event_history_limit` stays at 20 and stays what it is — the
activity-feed window, free to change when that panel is built, load-bearing for
nothing.
