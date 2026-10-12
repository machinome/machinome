## Context

SPRINT-003's PRD names two compounding defects in the floor's model refresh.
Defect A is in `floor/frontend/src/main.tsx`: `FunctionalModel` renders either
the viewer host `<div>` or an error paragraph, so the first failed fetch
unmounts the host, `container.current` becomes `null`, and the effect's
`if (!target) return;` guard fires before `setError(null)` on every later
change — the viewer is dead until the maker reloads. Defect B was the artifact
route re-resolving the `_build` symlink mid-request; S1 dissolved it by
resolving one fixed build root at app creation, and F2 removed the symlink
entirely.

What remains is the shape of the update itself. Today an artifact event
increments `modelGeneration`, which changes the effect's dependency, which
disposes the handle and mounts a new viewer against
`/artifacts/viewer.json?generation=N`. On `v8-engine` that is 113 MB refetched
and 55 meshes re-parsed and re-uploaded per change.

F3 published the interface that replaces it. The framework viewer handle now
offers `artifactChanged(path)` and `manifestChanged()` beside `reload()`,
`dispose()` and `view()`, at `solidNodeViewerApi: 2`. It owns geometry
staleness — keyed on `(model path, mtime)` per PRD D6 — and it already promises
that a failed targeted update leaves the rendered model and camera standing.
S1 forwards one event per published file, carrying the path relative to
`_build` and nothing else, whichever publisher produced it.

The shop is therefore not implementing an update algorithm. It is deleting one
and calling the framework's.

## Goals / Non-Goals

**Goals:**

- One viewer mount per open shop floor, surviving every change and every
  failure until the page is closed.
- Each reported artifact answered by the narrowest update the viewer offers.
- A failed fetch that costs the maker the update, not the session.
- The floor refusing to open against a viewer that cannot update in place,
  rather than silently degrading to reload-per-change.

**Non-Goals:**

- Changing the event contract S1 settled. The floor still forwards published
  paths, forwards no deletions, and interprets no contents.
- Diffing, batching, or debouncing events in the browser. PRD D3 put the
  decision in the browser precisely because the browser already knows what it
  holds; per-event work is bounded by the viewer's own staleness keys.
- Anything the viewer renders. This cycle changes when and how much it
  updates.
- Retiring the `model_build_unavailable` event or the failure banner. Both are
  S1's, and both stay.

## Decisions

### D1 — The viewer handle lives in a ref, mounted by an effect that depends on nothing

`FunctionalModel` mounts once on its first commit and disposes only on unmount.
The handle goes into a ref alongside the existing `view` ref; artifact events
read it and call the matching update. The generation prop, the
`?generation=N` query, and the effect's dependency array all go.

Rejected: keeping a state variable that holds the handle. Handle arrival would
re-render the pane for no visual reason, and under `StrictMode`'s double-invoke
a state-held handle is easy to leak. A ref plus the existing `disposed` guard
is the shape the current effect already uses correctly.

Rejected: hoisting the handle into `App`. The mount target belongs to the pane;
lifting the handle out would make `App` responsible for a DOM node it does not
render. `App` instead passes the artifact path down as a prop and the pane
applies it.

### D2 — The error paragraph renders beside the host, never instead of it

The host `<div>` is unconditional. A mount or update failure renders an
additional paragraph. This is the whole of Defect A: the guard that skipped
`setError(null)` cannot fire when the target is never removed, and the fix is
by construction rather than by ordering the state updates more carefully.

This makes a live model and a failure message simultaneously visible, which is
exactly PRD D8's ratified position — a partially updated model is a legitimate
observable state, and the maker needs to be able to tell an arriving model from
a settled one.

### D3 — The browser maps the reported path to one of three actions

- `viewer.json` → `manifestChanged()`
- `errors.json` → the existing failure-banner fetch, unchanged from S1
- anything else → `artifactChanged(path)` with the path exactly as reported

The path is passed through verbatim: the floor reports it relative to `_build`,
the viewer resolves it against the `baseUrl` of `/artifacts/`, and the two
agree because the route serves that directory. No parsing, no extension test,
no membership check against the manifest — the viewer already ignores a path no
node references.

Rejected: calling `manifestChanged()` for every event. It is a 13 KB refetch
and a full tree reconcile for a change the viewer can localise from the path,
and it would make the artifact event indistinguishable from a reload.

Rejected: classifying model files by suffix. S1's ADR 0013 already rejected
name-based classification in the floor for the same reason it fails here: one
rule with two named exceptions is smaller than a taxonomy, and a new artifact
kind should reach `artifactChanged()` by default.

### D4 — An update failure is reported, then forgotten on the next success

`artifactChanged()` and `manifestChanged()` return promises; a rejection sets
the same error paragraph D2 introduced, and the next update that resolves
clears it. Because the viewer guarantees the rendered model and camera survive
a failed update, there is nothing to restore — the browser only has to stop
treating failure as terminal.

The three failure channels stay distinct and stack: `model_build_unavailable`
(the shop could not run a build), the `errors.json` banner (the build failed),
and this update error (the browser could not fetch what the floor reported).
They report different actors and have different remedies.

### D5 — A floor reconnect reconciles rather than remounts

The lifecycle `EventSource` reopening currently bumps the generation to force a
remount, on the reasoning that the floor may have restarted under a changed
build. With no remount available, the reconnect calls `manifestChanged()`
instead: the document is authoritative for what exists, the viewer refetches
geometry whose `(model path, mtime)` moved, and everything else is left alone.
This is strictly cheaper than the remount it replaces and equally correct.

Rejected: `reload()` on reconnect. It rebuilds the tree from scratch while
preserving only the camera, which is the coarse behaviour this cycle exists to
remove, and `manifestChanged()` covers the same ground.

### D6 — `REQUIRED_VIEWER_API` becomes 2 and the shop's type declaration follows

`floor/preparation.py` already refuses to open against a viewer older than it
requires, with a message naming both versions. Raising the constant to 2 is the
whole enforcement; no new failure path is needed.

`floor/frontend/src/solid-node-widget.d.ts` is a shop-local declaration of the
framework's surface and is currently at version 1 without the targeted updates.
It is brought level: `artifactChanged`, `manifestChanged`, `reload`, and
`SOLID_NODE_VIEWER_API_VERSION: 2`. It stays a declaration — the shop does not
import the widget package, it loads the bundle the installed framework supplies.

### D7 — Artifact responses must revalidate

The route returns a bare `FileResponse`. Without `Cache-Control`, a browser may
apply heuristic freshness to a URL it has already fetched — and after this
cycle every artifact refetch uses the *same* URL, because the cache-busting
`?generation=N` query is gone. The route therefore sends `Cache-Control:
no-cache`, so each fetch revalidates against the `ETag` and `Last-Modified`
that `FileResponse` already derives from the file it is serving. Atomic rename
changes both.

This is the one place where removing the generation query is not free, and it
is worth naming: the query was accidentally doing cache correctness while
appearing to do remounting.

### D8 — ADR 0013 is amended, not superseded

PRD section 5 allots this sprint one shop architecture record, covering D3, D4
and D8; S1 filed it as ADR 0013. Its closing paragraph explicitly records the
coarse bridge as S1's temporary retention and names S2 as its replacement.
Discharging that sentence is an amendment to an accepted record, not a new
decision, and a second shop ADR would split one event pipeline across two
records.

## Risks / Trade-offs

- **A long-lived handle accumulates GPU resources across many updates.** →
  The viewer owns disposal of the meshes it replaces; F3's spec requires
  removed nodes and their resources to be gone after `manifestChanged()`. The
  live check on `v8-engine` watches for growth across repeated edits rather
  than trusting the promise.

- **`StrictMode` double-invokes the mount effect in development.** → The
  existing `disposed` flag and `cleanup()` already handle the mount/dispose
  race; the change keeps them and adds no second mount path. The e2e tests run
  the production bundle, so a regression here shows up in development first,
  which is the right way round.

- **An `artifactChanged()` for a path no node references is silently a no-op.**
  → That is the intended reading of PRD D4: the floor forwards publications,
  the manifest decides existence. It does mean a genuinely misreported path
  fails quietly. The e2e assertion that exactly one artifact request follows a
  one-leaf edit is what would catch it.

- **The three failure reports can be on screen at once.** → They describe
  different actors and are worded to be distinguishable. Collapsing them into
  one banner would lose the distinction between "the shop could not build",
  "the model does not build", and "the browser could not fetch".

- **Canvas identity is the sprint's load-bearing assertion.** → PRD acceptance
  criterion 2 says so explicitly: it is the only assertion that distinguishes
  in-place update from reload. It is written against the DOM node's identity
  across a real rebuild, not against a render count or a spy.
