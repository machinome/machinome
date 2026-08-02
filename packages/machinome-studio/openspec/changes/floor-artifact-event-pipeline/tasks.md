## 1. Artifact observation

- [ ] 1.1 Declare `watchdog` as a shop dependency in `pyproject.toml`.
- [ ] 1.2 Add `ArtifactWatcher` to `floor/watcher.py` as a
  `FileSystemEventHandler` on `_build`, recursive, acting only on
  `FileMovedEvent`. No fingerprint, no seeding, no interval, no filename
  matching.
- [ ] 1.3 Publish `model_artifact_changed` with `{"artifact": <dest_path
  relative to the build root>}`, one event per move.
- [ ] 1.4 Bridge handler-thread events onto the event loop with
  `call_soon_threadsafe`; the handler itself only publishes.
- [ ] 1.5 Test: renaming a file into the build directory produces exactly one
  event naming it, proven red before the handler exists.
- [ ] 1.6 Test: republishing one of three artifacts produces one event, not
  three (PRD acceptance 1).
- [ ] 1.7 Test: a publication no shop build triggered is reported — the watcher
  runs with no build subprocess at all.
- [ ] 1.8 Test: deleting an artifact produces no event (PRD acceptance 7).
- [ ] 1.9 Test: creating and writing a file in the build directory without
  renaming it produces no event, and the rename produces exactly one.
- [ ] 1.10 Test: `errors.json` published by the framework's own atomic write
  produces an event, with no branch in the handler naming it.
- [ ] 1.11 Test: an already-populated build directory produces no events when
  the watcher starts.

## 2. Source watcher separation

- [ ] 2.1 Replace `ModelWatcher`'s polling loop with a `FileSystemEventHandler`
  on the project root, recursive, reacting to any event on a `*.py` path;
  delete `_source_fingerprint`, `_changed_source`, `_content_hash`, the
  `poll_interval` parameter, and `EXCLUDED_DIRECTORIES`/`EXCLUDED_PREFIXES`.
- [ ] 2.2 Coalesce with a single settle timer rescheduled by each event, so an
  in-progress editor write and a multi-file save both produce one build; keep
  one build in flight with the change that arrived during it remembered.
- [ ] 2.3 Guard the source handler against paths under `_build`, so a build
  cannot trigger the build that produced it.
- [ ] 2.4 Remove `model_changed`, `model_build_succeeded`, and the model verdict
  derived from the build's exit status.
- [ ] 2.5 Replace `_publish_failure` with a single `model_build_unavailable`
  report for the case where the build command could not be run at all, carrying
  the reason; a build that ran and failed is reported by its own output.
- [ ] 2.6 Test: an editor writing a source file in several chunks produces one
  build, proven red by building on the first event.
- [ ] 2.7 Test: a multi-file save produces one build.
- [ ] 2.8 Test: writes under `_build` trigger no build.
- [ ] 2.9 Test: a build that exits non-zero after writing a failure record
  publishes no verdict event from the source watcher, while the artifact watcher
  reports the record.
- [ ] 2.10 Test: an unusable `solid` command publishes `model_build_unavailable`.
- [ ] 2.11 Test: a project source directory whose name begins `_build.` is
  watched rather than excluded.

## 3. Application wiring

- [ ] 3.1 Own one `Observer` in the lifespan with both handlers scheduled on it;
  start it on entry and stop and join it on exit. Expose both handlers on
  `app.state` for the tests.
- [ ] 3.2 Resolve the build root once in `create_app` and use that fixed root in
  the artifact route; drop the per-request re-resolution and the second
  containment comparison.
- [ ] 3.3 Add `model_artifact_changed` and `model_build_unavailable` to
  `Broker._event_summary`; remove the `model_changed`, `model_build_failed` and
  `model_build_succeeded` cases.
- [ ] 3.4 Test: the artifact route serves an artifact while another artifact of
  the same model is republished concurrently, with no 404 (PRD Defect B,
  acceptance 5); proven red against the current three-way resolution.
- [ ] 3.5 Test: a traversal path outside the build root is still refused.
- [ ] 3.6 Test: an app built without a solid command starts no source handler
  and spawns no subprocess, while build output is still observed.
- [ ] 3.7 Test: the observer is stopped and joined on shutdown, leaving no
  thread behind.

## 4. Browser bridge

- [ ] 4.1 In `floor/frontend/src/main.tsx`, increment the model generation on
  `model_artifact_changed` for `viewer.json` instead of on `model_changed`;
  leave rendering and the mount path untouched.
- [ ] 4.2 Show the build failure by fetching `/artifacts/errors.json` when an
  event names it, and clear that banner on the manifest event; drop the
  `model_build_failed` and `model_build_succeeded` handlers. Show
  `model_build_unavailable` as the distinct shop failure it is.
- [ ] 4.3 Test: a failure raised by a build the floor did not run reaches the
  banner.
- [ ] 4.4 Comment the reload bridge as S2's to remove, naming the cycle.
- [ ] 4.5 Rebuild the floor's static bundle and confirm the served asset is the
  rebuilt one, not a stale artefact.

## 5. End-to-end evidence

- [ ] 5.1 Extend `tests/test_shop_lifecycle_e2e.py`: editing one leaf of a
  multi-node project delivers an artifact event naming that leaf's artifact over
  SSE, and no event naming the untouched leaf's.
- [ ] 5.2 Test: a `solid build` run outside the floor refreshes the browser.
- [ ] 5.3 Live check against a real project with the linked framework
  `sprint-003` checkout: one-edit-one-event, an external build reaching the
  browser, and the artifact route serving throughout a republication.
- [ ] 5.4 Confirm by inspection that no sampling loop remains in the model
  pipeline: no `sleep` in `floor/watcher.py`, no interval, no fingerprint.
- [ ] 5.5 Run `pytest tests` and `tests/dev-env-test.sh` green.

## 6. Records

- [ ] 6.1 Write the shop ADR covering PRD D3, D4 and D8: amend ADR 0010's event
  source, its separate failure channel, and its polling mechanism; reaffirm ADR
  0004's artifact boundary unchanged; record the rejected alternatives
  (server-computed diff, forwarded deletions, set-atomic restore on failure,
  classifying build output by file kind, fingerprint diffing).
- [ ] 6.2 Record in that ADR that the floor observes filesystem events and
  samples nothing, and that publication is defined as a rename — so the floor's
  rule and the framework's publication protocol are one statement.
- [ ] 6.3 Update `docs/adrs/README.md` and mark ADR 0010's event-source,
  failure-reporting and change-detection sections as amended.
- [ ] 6.4 Record in the ADR consequences that a build fixing a transient failure
  without changing the manifest leaves a stale failure record, and that the
  cause is in the framework's publication path rather than the floor.
- [ ] 6.5 Sync `openspec/specs/functional-model-inspection/spec.md` from the
  ratified delta and archive the change.
