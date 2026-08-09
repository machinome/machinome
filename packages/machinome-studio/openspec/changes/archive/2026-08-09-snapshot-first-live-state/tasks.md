# Tasks

Reference implementation: branch `make-shop-floor-event-driven`, commit
`76edeec` ("feat: make shop floor event-driven"). Read its `floor/app.py` and
`floor/frontend/src/main.tsx` hunks. **Do not merge, rebase, or cherry-pick
whole commits from it** — it is based on a pre-sprint-003 head and its
`watcher.py` rewrite is superseded by what ships today. Port the browser and
stream hunks deliberately, by hand.

## 1. Red first

- [x] 1.1 `tests/test_floor_api.py`: a client connecting to the live stream mid-run receives, as its first frame, run state and every conversation entry in original order
- [x] 1.2 `tests/test_floor_api.py`: an event published between subscription and snapshot delivery reaches the client, after the snapshot, exactly once
- [x] 1.3 `tests/test_floor_api.py`: the snapshot carries `latest_event_sequence` and it is correct when `Broker.events` is empty and when it has been trimmed past its bound
- [x] 1.4 `tests/test_shop_lifecycle_e2e.py`: a conversation entry recorded while the page's connection is down appears exactly once after it reconnects, without reload
- [x] 1.5 `tests/test_shop_lifecycle_e2e.py`: an agent manifested and set to work while the page's connection is down is shown in its current state after reconnection
- [x] 1.6 `tests/test_shop_lifecycle_e2e.py`: **restart** — with a page open, restart the floor service against the same location, publish a conversation entry and an agent change from the new process, and assert the page displays them. This is the case the removed poll was hiding; it must be red before task 3.3 and green after
- [x] 1.7 `tests/test_shop_lifecycle_e2e.py`: an idle open page issues no repeating run-state or conversation requests over an interval comfortably longer than the retired one-second period
- [x] 1.8 Confirm each of the above fails against unmodified `main` for the stated reason, and record which fail for which reason

  Red-first evidence, 2026-08-09, against implementation commit `cbf123b` beneath the ratified planning commit:

  - 1.1 failed with `404 Not Found` because `/api/stream` did not exist.
  - 1.2 and 1.3 failed because `Broker.snapshot` and `Broker.subscribe_snapshot` did not exist, and run state had no explicit latest sequence.
  - 1.4 and 1.5 timed out after legacy `/api/runs/latest` and run-specific stream recovery were disabled; the page had no snapshot-first reconnect path.
  - 1.6 timed out waiting for the already-open page to report the restarted shop open; retained run state and the old cursor prevented correct restart recovery.
  - 1.7 observed two repeated `/api/runs/latest` and two repeated conversation requests in 2.2 seconds.

## 2. Server: snapshot and ordering

- [x] 2.1 Add `Broker.snapshot()` returning run state plus the full ordered conversation, and include `latest_event_sequence` in the run value
- [x] 2.2 Add the atomic subscribe-then-snapshot helper (see `76edeec`'s `subscribe_snapshot`): register the connection's queue in `broker.subscribers`, then read state, in that order, with no `await` between them
- [x] 2.3 Rewrite `/api/runs/{run_id}/stream` to emit `event: snapshot` first and then drain that queue; keep the 15-second keepalive comment frame
- [x] 2.4 Add run-agnostic `/api/stream` sharing the same implementation
- [x] 2.5 Ensure the subscriber queue is discarded on client disconnect, including when the connection ends before the first frame is written

## 3. Browser: one connection

- [x] 3.1 Connect to `/api/stream` on mount; handle `snapshot` by replacing run state and conversation wholesale
- [x] 3.2 Move shop-open onto that connection's `onopen`/`onerror`, and preserve the existing "re-open after a previous open bumps `modelReconnect`" behaviour — it re-reads a model whose artifact events were missed while disconnected, and dropping it regresses `reliable-live-model-event-delivery`
- [x] 3.3 **Assign** `latestEvent.current` from `snapshot.run.latest_event_sequence`; do not `Math.max` it against the previous value. See `design.md`
- [x] 3.4 Delete `setInterval`, `load()`, the `/api/runs/latest` request, the `/api/runs/{id}/conversation` request, and the `/events/lifecycle` `EventSource` and its `lifecycleOpened` ref
- [x] 3.5 Verify the optimistic append in `submitUserMessage` still dedups against both the streamed `conversation_entry` and a snapshot arriving mid-send
- [x] 3.6 Rebuild the bundle into `floor/static/` and commit the built assets

## 4. Remove superseded surface

- [x] 4.1 Remove the `/events/lifecycle` route from `floor/app.py`
- [x] 4.2 Remove `Broker.wait_for_events` and the `_event_changed` signal
- [x] 4.3 Remove the `after` query parameter and its `Broker.events` replay from the stream route
- [x] 4.4 Retarget `tests/test_broker.py`'s signal-driven and timestamp coverage from `wait_for_events` onto the subscriber queue, keeping the bounded-history assertion unchanged
- [x] 4.5 Retarget `tests/test_orchestrator.py`'s `/events/lifecycle` probe onto the live-state connection
- [x] 4.6 Replace `tests/test_floor_api.py::test_run_stream_replays_a_publication_after_the_browser_snapshot` with the ordering coverage from 1.2 — the guarantee it defends is now structural, not compensating
- [x] 4.7 Retarget the `**/api/runs/latest` interception in `tests/test_shop_lifecycle_e2e.py::test_a_manifest_published_between_snapshot_and_stream_updates_without_reload`, which intercepts a request the browser no longer makes
- [x] 4.8 Confirm `Broker.events` and `event_history_limit` are unchanged and that no recovery path reads them

## 5. Records

- [x] 5.1 Write an ADR amending ADR 0001: one live connection carrying a snapshot then changes, replacing the separate lifecycle stream; record the client-held-cursor hazard as the reason recovery is snapshot-based rather than replay-based
- [x] 5.2 Update ADR 0001's status to note the amendment, and add the new ADR to `docs/adrs/README.md` in chronological order
- [x] 5.3 Rewrite the affected part of `docs/architecture-overview.md` "Floor and browser": the browser holds one live connection that opens with the current situation; it does not poll
- [x] 5.4 Update the data-layer list in `docs/design/README.md`, which still names `/api/runs/latest` and `/events/lifecycle` as part of the browser's data layer

## 6. Validation

- [x] 6.1 Full test suite green, including the Playwright e2e suite
- [x] 6.2 Open a floor, watch the service log, and confirm no repeating per-second requests from an idle page
- [x] 6.3 With that page open, restart the floor service and confirm the page recovers and then reflects new work from the new process — the 1.6 case, confirmed by hand as well as by test
- [x] 6.4 Confirm the model still updates in place on save (the sprint-003 path this change must not disturb), including after a reconnect
- [x] 6.5 `openspec validate --strict`, sync baseline specs, archive the change
