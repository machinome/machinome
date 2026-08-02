# ADR 0013: Observe atomic build publications separately from source-triggered builds

**Status:** Accepted

**Date:** 2026-08-02

**Origin:** SPRINT-003 / `floor-artifact-event-pipeline`

**Amends:** ADR 0010's event source, failure reporting, and source-change
detection; reaffirms ADR 0004's published-artifact boundary

## Context

ADR 0010 made the floor responsible for noticing project source changes and
rebuilding the model. Its polling watcher also decided whether the model had
changed by hashing `viewer.json` after a subprocess it owned. That conflated a
build trigger with evidence that an artifact had become available, so an
external `solid build` could never reach the browser. It also treated a failed
subprocess as a privileged failure report, although framework build output is
the durable report that every publisher produces.

SPRINT-003's framework publication uses one `_build` directory and publishes
each completed file by atomic rename. The symlink swap that motivated the
floor's repeated build-root resolution no longer exists. Keeping those
resolutions can turn a concurrent publication into a false 404.

## Decision

The floor owns one `watchdog.Observer` for its lifespan and schedules two
independent handlers on it.

- A source handler watches Python source paths outside `_build`, coalesces an
  event burst with one settle timer, and triggers `solid build root`. It does
  not poll, fingerprint source, hash a manifest, or report a build verdict.
- An artifact handler watches `_build` recursively and forwards only
  `FileMovedEvent` destinations as `model_artifact_changed` events carrying
  `{"artifact": <path relative to _build>}`. A rename is publication. The
  floor does not inspect, classify, diff, or forward deletions.
- A failed build is represented by the framework's atomically published
  `errors.json`, which travels through the same artifact event path. Only an
  inability to start the build process produces the distinct
  `model_build_unavailable` event.
- The artifact route resolves its single build root when the app is created and
  checks each requested candidate against that fixed root once. Atomic rename,
  rather than route retry or symlink re-resolution, prevents torn reads.

S1 retains a browser bridge: a `viewer.json` artifact event performs the
existing coarse reload and clears an error banner; an `errors.json` event fills
the banner. S2 replaces that bridge with the framework viewer's targeted
in-place update.

## Alternatives rejected

- Server-computed artifact diffs and generations would require client-state
  baselines even though the browser already knows what it holds.
- Forwarding deletion events invites the browser to fetch a path that the
  manifest has already removed.
- Restoring set-atomic publication after a failure would undo progressive
  visibility and belongs neither in the floor nor in this event contract.
- Classifying files by name or kind creates exceptions for meshes, manifests,
  and error records where one publication rule is sufficient.
- Fingerprint polling reconstructs a filesystem fact from heuristics and needs
  startup seeding, temporary-file exclusions, and unstable-write handling.

## Consequences

- A publication by the floor, a terminal, an agent, or `solid develop` reaches
  the browser identically.
- A partially updated model is an observable, inspectable state. A build
  failure no longer promises the prior complete model remains intact.
- The floor remains within ADR 0004: it neither imports nor executes project
  Python, and it serves only the published build directory.
- A successful build that clears a transient failure without republishing
  `viewer.json` can leave a stale failure banner. The framework publication
  path owns that edge, not the floor; F2 records it as such.
