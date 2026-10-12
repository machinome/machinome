## Why

The floor learns that the model changed by hashing `_build/viewer.json` after
its own build finishes, and then tells the browser one thing: everything is
different. That was the only signal available while a publication was an
all-or-nothing directory swap. It no longer is. F2 made the framework publish
each artifact atomically into a single `_build` directory, so the floor can now
say *which* artifact changed — which is the whole precondition for the browser
updating in place instead of refetching 113 MB and re-uploading 55 meshes
(PRD section 2.3).

Two further consequences of F2 land in the floor and cannot be deferred. The
`_build` symlink is gone, so the artifact route's three-way re-resolution —
measured cause of the 404 that permanently wedges the viewer (PRD Defect B) —
is now guarding against a hazard that no longer exists while still
manufacturing failures of its own. And a failed build now leaves a partially
updated model rather than the previous complete one (PRD D8), which the shop's
ratified specification currently promises the opposite of.

## What Changes

- The floor runs **two watchers with distinct jobs**. Source changes trigger a
  build; completed build output produces events. Today one watcher does both,
  which is why only a build the floor itself ran can ever reach the browser.
- **Neither watcher samples anything.** Both become filesystem event handlers.
  The 0.5 s poll, the source fingerprint, the snapshot hash and the two-stable-
  samples debounce are all deleted rather than carried into the new pipeline.
  This amends ADR 0010's change-detection decision, whose stated reason — that
  `watchdog` adds a dependency — no longer holds, since the floor runs only
  where solid-node is installed and solid-node depends on `watchdog`.
- **A publication is a rename, so the floor forwards renames.** F2 publishes by
  `os.replace`, which the kernel reports as one move naming the file that just
  became reachable. That single rule removes the in-flight temporary exclusion,
  the file-kind taxonomy, the deletion rule and the startup seeding step: each
  was scaffolding for reconstructing, by sampling, a fact the filesystem
  already reports.
- A change published by **anyone** — `solid build` in a terminal, `solid
  develop`, an agent, another floor-triggered build — reaches the browser,
  because the event source is observed build output rather than the floor's own
  subprocess exit.
- The floor emits **one event per completed file of the build output, carrying
  that file's path and nothing else** (PRD D3). It does not diff, does not open
  or parse what it forwards, and does not classify it — a mesh, the manifest and
  the failure record are the same kind of thing to the floor, and the browser
  decides what each means.
- **A failed build is reported by forwarding the failure record the build
  wrote**, so a failure reaches the maker whoever caused it. `model_build_failed`
  and `model_build_succeeded`, which report a verdict only for builds the floor
  itself ran, are removed for the same reason `model_changed` is.
- **Deletions are not forwarded** (PRD D4). The manifest is authoritative for
  existence and, by F2's ordering, always changes first.
- **BREAKING (shop-internal event contract):** `model_changed`,
  `model_build_failed` and `model_build_succeeded` are replaced by the
  per-artifact event, plus one narrow report that the shop could not run a build
  at all — which produces no build output and so is genuinely unobservable.
  Nothing outside the floor's own browser consumes any of them.
- The artifact route resolves the build root **once**, at startup. The
  re-resolution and containment comparison that produced spurious 404s go away
  with the symlink they were written for.
- **BREAKING (ratified behaviour):** a failed rebuild no longer guarantees that
  the last complete model stays inspectable. The specification is corrected to
  what the architecture now provides: the artifacts that were successfully
  published remain readable, and the reported failure tells the maker the model
  is mid-change (PRD D8).
- As a bridge, the browser's existing coarse reload and failure banner are
  retargeted onto the manifest and failure-record events, so the sprint branch
  shows a live model at every cycle boundary. S2 replaces the reload with the
  in-place update; S1 does not touch how the model is rendered.

## Capabilities

### New Capabilities

None. The floor's event pipeline is a change to how an existing capability
works, not a new thing the shop can do; the maker-visible new capability
arrives with S2.

### Modified Capabilities

- `functional-model-inspection`: the refresh requirement changes from "rebuild,
  then report that the complete model changed" to "observe published build
  output, then report each file that changed, whoever published it"; the
  failed-build requirement becomes an instance of that same rule rather than a
  separate channel, drops its promise that the previous complete model remains,
  and states the partial-model reality instead.

## Impact

- `floor/watcher.py` — the source watcher becomes an event handler with a settle
  timer and loses its polling loop, `_source_fingerprint`, `_changed_source`,
  `_content_hash`, `poll_interval`, `model_changed` and its model verdict. It
  retains only the report that a build could not be run, and one guard against
  paths under `_build`.
- `floor/watcher.py` (new sibling handler) — observes `_build` and publishes one
  event per rename into it.
- `floor/app.py` — one `watchdog` observer in the lifespan carrying both
  handlers; the artifact route resolves its root once; `_event_summary` gains
  the new event kinds.
- `pyproject.toml` — `watchdog` becomes a declared shop dependency instead of a
  transitive one.
- `floor/frontend/src/main.tsx` — the reload trigger moves from `model_changed`
  to the manifest artifact event (bridge only).
- `tests/test_model_watcher.py`, `tests/test_floor_api.py`,
  `tests/test_shop_lifecycle_e2e.py` — new coverage for multi-publisher events,
  one-edit-one-event, deletion silence, and the artifact route under a
  concurrent republication.
- Depends on framework `sprint-003` @ `582da89` (F2). Serves S2, which consumes
  these events.
- `docs/adrs/` — one shop ADR covering PRD D3, D4 and D8, amending ADR 0010's
  event source, its separate failure channel and its polling change detection,
  and reaffirming ADR 0004's artifact boundary unchanged.
