## 1. Event-driven model watcher

- [ ] 1.1 Add `watchdog` as a direct shop dependency in `pyproject.toml`
- [ ] 1.2 Add a `FileSystemEventHandler` in `floor/watcher.py` that filters to `.py` paths surviving `_excluded_directory` / `EXCLUDED_PREFIXES` and bridges to the loop with `call_soon_threadsafe` onto an `asyncio.Queue`, handling created, modified, moved and deleted events
- [ ] 1.3 Replace `ModelWatcher.run`'s sleep-and-fingerprint loop with a queue consumer plus a re-armable quiet-period debounce (constructor parameter, default ~200ms), keeping the single-build-at-a-time and `pending` coalescing logic unchanged
- [ ] 1.4 Schedule a recursive `Observer` on `project_root` in `ModelWatcher.run`, stopping and joining it on cancellation, and keep `_snapshot_hash` / `model_changed` / `model_build_*` publishing exactly as-is
- [ ] 1.5 Fall back to `PollingObserver` when the native observer cannot start, and report the reason through the existing failure-publishing path rather than dying silently
- [ ] 1.6 Preserve a named trigger file for the log and the published event, derived from the observed path instead of `_changed_source`
- [ ] 1.7 Retarget `tests/test_model_watcher.py` from `POLL` timing to the debounce parameter, keeping the published-event assertions unchanged
- [ ] 1.8 Add a test that a write into the build tree does not trigger a rebuild, and a test that a temp-file-plus-rename save does trigger one
- [ ] 1.9 Add a test that several source files changed within one burst produce exactly one rebuild
- [ ] 1.10 Drop the now-unused `poll_interval` plumbing from `create_app` and `_serve`, or repoint it at the debounce window

## 2. Snapshot-first live-state stream

- [ ] 2.1 Add a broker snapshot value combining run state and the full ordered conversation
- [ ] 2.2 Send that value as an `event: snapshot` first frame on every `/api/runs/{id}/stream` connection
- [ ] 2.3 Register the subscriber queue in `broker.subscribers` before serialising the snapshot, so an event published in between is delivered after it rather than lost
- [ ] 2.4 Add an API test that a client connecting mid-run receives run state and every conversation entry in original order as its first frame
- [ ] 2.5 Add an API test that a conversation entry recorded while a client is disconnected appears exactly once after that client reconnects
- [ ] 2.6 Add an API test that an agent work-state change made while a client is disconnected is reflected in the snapshot on reconnection
- [ ] 2.7 Add an API test that an event published between subscription and snapshot delivery arrives exactly once, after the snapshot

## 3. Single-connection browser

- [ ] 3.1 Handle the `snapshot` event in `main.tsx`, replacing run state and conversation wholesale on every connection
- [ ] 3.2 Delete the `setInterval` and both bootstrap `fetch` calls, connecting the stream directly on mount
- [ ] 3.3 Move `shopOpen` and the reopen `modelGeneration` bump onto the live-state stream's `onopen` / `onerror`, and remove the `lifecycleOpened` ref and the `/events/lifecycle` `EventSource`
- [ ] 3.4 Verify the optimistic append in `submitUserMessage` still dedups correctly against the streamed `conversation_entry` and against a snapshot arriving mid-send
- [ ] 3.5 Rebuild the frontend bundle into `floor/static/`

## 4. Remove superseded surface and update docs

- [ ] 4.1 Remove the `/events/lifecycle` route from `floor/app.py`
- [ ] 4.2 Remove `Broker.wait_for_events` and its coverage in `tests/test_broker.py`
- [ ] 4.3 Update or remove tests referencing `/events/lifecycle` in `tests/test_floor_api.py` and `tests/test_shop_lifecycle_e2e.py`
- [ ] 4.4 Confirm `Broker.events` and `event_history_limit` are unchanged and that nothing in the recovery path reads them
- [ ] 4.5 Update `docs/architecture-overview.md` to describe one snapshot-on-connect browser stream and notification-driven model rebuilds
- [ ] 4.6 Run the full test suite and confirm no timer-driven state refresh remains in `floor/` or the frontend
