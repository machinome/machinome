## Context

Floor obtains a run snapshot over HTTP and later opens an SSE stream for live
broker events. The stream currently starts at the instant its generator adds a
subscriber. A build publication in the interval after the snapshot is read and
before that subscription exists is neither replayed nor applied to the model.
Reloading creates a fresh viewer mount from `viewer.json`, masking the missed
event while violating STORY-007.

## Goals / Non-Goals

**Goals:**

- Deliver every broker event after the event sequence in the browser’s run
  snapshot, including a model publication in the snapshot-to-SSE hand-off.
- Preserve live event ordering and the existing one mounted viewer.
- Prove an open browser receives an assembly-to-fusion manifest update without
  navigation or a second mount.

**Non-Goals:**

- Persist events across a floor restart or serve multiple historical runs.
- Change the artifact path-only wire contract or have Floor interpret model
  contents.
- Add framework viewer behaviour; the viewer already reconciles the manifest.

## Decisions

### Sequence the run event stream

The stream accepts the latest event sequence from the run snapshot and replays
the broker’s retained events strictly after it before waiting for new events.
The broker registers the subscriber before taking the replay so a publication
cannot fall between replay and live delivery. The browser supplies the latest
sequence it observed and keeps its existing event de-duplication.

An unsequenced stream or an immediate snapshot refresh was rejected: neither
closes the hand-off race without either duplicating client-side state or
depending on request timing.

### Treat replayed events exactly like live events

The browser routes replayed `model_artifact_changed` events through the same
path-only viewer update handler as live events. It does not refetch or parse a
document merely to catch up. This preserves D3 and makes the missed
publication observable exactly once.

Polling the manifest or adding a generation/diff payload was rejected because
it recreates server/client state and violates the floor’s content-event-only
boundary.

## Risks / Trade-offs

- [The bounded broker event history may not contain an old cursor] → a client
  that falls behind the retained history reconnects from a fresh run snapshot;
  the normal initial hand-off is covered without claiming cross-restart
  persistence.
- [Replay and live delivery can overlap] → subscribe before snapshotting the
  replay and retain sequence de-duplication in the browser.
- [The browser can disconnect during catch-up] → reconnect uses its latest
  applied sequence and the mounted viewer remains intact.

## Migration Plan

Deploy the shop change with the existing framework `sprint-003` viewer API 2.
No project migration is required. If the stream implementation needs rollback,
the prior browser continues to mount a complete initial publication but loses
the no-missed-update guarantee.

## Open Questions

None.
