## Why

S1 gave the browser a per-artifact event, but the browser still answers it by
tearing the whole viewer down and mounting a new one. On `v8-engine` that
refetches 113 MB and re-uploads 55 meshes to show a change that usually touches
one leaf, and the mount is fragile: a single failed fetch replaces the viewer
host with an error paragraph, so `container.current` becomes `null` and every
later change is dropped — the model never updates again without a page reload.
F3 published the viewer interface that removes both problems. This cycle is
where PRD defects A and B are finally answered.

## What Changes

- The floor's model pane mounts the framework viewer once and keeps it mounted
  for the life of the shop. It is never unmounted to show an error, and a
  change no longer remounts it.
- A `model_artifact_changed` event naming the published document calls the
  viewer handle's `manifestChanged()`; one naming the failure record keeps its
  existing banner fetch; any other artifact calls `artifactChanged(path)` with
  the path exactly as the floor reported it. That three-way mapping is the
  browser's only decision — it opens no artifact and compares nothing.
- The generation counter that forced a remount, and the
  `viewer.json?generation=N` cache-busting query it produced, are removed.
- A failed targeted update leaves the rendered model and camera standing and
  reports itself beside the model rather than in place of it; the next event
  updates normally with no page reload. **BREAKING** for anything depending on
  the model pane emptying itself on error.
- The build-failure banner is shown alongside a live model rather than instead
  of one, matching the sprint's ratified position that a partially updated
  model is a legitimate observable state.
- The floor requires viewer API 2 — the version that carries the targeted
  updates — and its widget type declaration is brought level with it.

## Capabilities

### New Capabilities

None. This cycle changes how the shop floor answers a model event; it
introduces no new area of behaviour.

### Modified Capabilities

- `functional-model-inspection`: the browser updates the displayed model in
  place from an artifact event instead of replacing the viewer; a failed
  update leaves the model standing and recovers on the next event; the
  established-viewer requirement's refresh scenario changes from "replaces the
  model tree, retaining the camera" to "updates only what changed, preserving
  the rendered canvas"; the required viewer interface is the one that offers
  targeted updates.

## Impact

- `floor/frontend/src/main.tsx` — `FunctionalModel` becomes a mount-once host
  holding the viewer handle; `App` routes artifact events to that handle
  rather than to a generation counter.
- `floor/frontend/src/solid-node-widget.d.ts` — declares `artifactChanged`,
  `manifestChanged`, `reload`, and API version 2.
- `floor/preparation.py` — `REQUIRED_VIEWER_API` becomes 2, so a shop opened
  against an older installed viewer fails preparation with the existing
  message rather than mounting a handle that cannot update.
- `floor/app.py` — the artifact route sends `Cache-Control: no-cache`, because
  every refetch now uses the artifact's own URL rather than a generation-tagged
  one and must revalidate.
- `floor/frontend/src/styles.css` — the error paragraph and the model host now
  coexist in the viewport.
- `tests/test_shop_lifecycle_e2e.py` — canvas identity across a change, and
  recovery after an induced fetch failure, are asserted in the browser.
- `docs/adrs/0013-observe-atomic-build-publications.md` — its recorded S1
  bridge is replaced by the targeted update it anticipated.
- Depends on framework `viewer-targeted-update` (F3) and
  `floor-artifact-event-pipeline` (S1), both integrated on `sprint-003`.
- No change to the floor's artifact boundary: it still imports, executes and
  serves no project Python.
