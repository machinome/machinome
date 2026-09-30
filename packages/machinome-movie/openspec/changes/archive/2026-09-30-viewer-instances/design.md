## Context

`stage/runtime.tsx` keeps `pool`, a `Map<string, PooledView>` keyed by the
view element's key (`<chapter>.<element>`). `poseViews()` mounts one viewer
instance the first time a key is placed (`mountView()`), never releases it,
detaches the hosts of the views a frame does not place and re-attaches a
host when its view returns, which is a resize, so the stage waits, bounded,
for the canvas to fill its box (the fix of 30 September for the real
viewer, which shrinks a detached host's canvas to nothing). `pose()` applies
a frame's whole view state to an instance by diffing what the instance
holds: the hidden layers (`hidden`), the standing highlight (`applied`) and
the function that restores it (`restore`); time, camera, target, and from
API 28 up and field of view are set on every frame. ADR-004's decision 3
and the contract say "one viewer instance per view element, kept across the
shots of its chapter".

The count this gives is the number of view elements in the film. The
fixture tour mounts four (one per chapter's view, two in its last chapter);
*Cut and Advance* mounts six, about 1.5 GB in Chromium, though none of its
stage frames places more than one view.

The renderer reads a view's report (`observed.elements[key]`: box, canvas,
camera, target, up, field of view, marks) and never its `instance` number;
it calls `window.film.project(key, points)` right after posing the frame
that places `key` (the lens check of `preview`). The browser tests read
`instance` and `window.film.views()`.

## Goals / Non-Goals

Goals: the count bounded by what one frame shows; every frame's pixels those
a fresh instance would draw, whatever instance serves it and whatever it
served before; nothing observable changed but the instance numbers and the
count. Non-goals: those of the proposal.

## Decisions

### D1. The lease

The runtime keeps its mounted instances in the order they mounted, each with
the key of the view element it serves, or none. For a frame whose placed
view elements are `placed` (the slots' keys of kind `view`, in the frame's
slot order, each once):

1. **Keep.** A placed view element whose key an instance serves keeps that
   instance.
2. **Release.** Every other instance serves nothing from this frame on: its
   host is detached from the page and hidden, as a view that left is today.
3. **Lease.** Each placed view element without an instance, in `placed`
   order, takes the lowest-numbered free instance it can be given (D3); when
   there is none, a new instance mounts for it, exactly as `mountView()`
   mounts today (in the element's box, with the frame's time, camera, up and
   field of view).

A released instance may be leased in the same frame. The decision is a pure
function, `leaseViews(tenancies, placed)`, exported from the runtime beside
`measureElement` and tested at layer 4; `poseViews` applies it.

Why the count is bounded: after rule 1 and 2, the instances serving
`placed` are distinct, and a new instance mounts only when every instance is
serving an element of this frame (below API 28: every instance of that
lens, D3). So after any frame, the number of instances is at most the
largest number of view elements a frame posed so far placed.

Which free instance is taken is history-dependent (lowest-numbered free);
that is allowed because nothing an instance draws depends on which instance
it is (D2). The instance number still appears in the page: the mark layer's
clip-path ids carry it (`uid`), which keeps two views of one frame apart.
Two frames that differ only in which instance serves a view therefore
differ in content, and `pose-repaints`' rule repaints the second; its pixels
are those of a whole-page raster either way.

### D2. The instance's state travels with it

`hidden`, `applied`, `restore` and `size` are fields of the instance, not of
the view element, and are not reset by a lease. `pose()` is unchanged: it
restores a standing highlight that differs from the frame's (the previous
tenant's included), shows the layers the instance hides and hides the
frame's, applies the frame's highlight, and sets time and camera, and from
API 28 up and field of view. So after a pose the instance holds exactly the
frame's state, whatever it held before, which is what a fresh instance
posed with that state holds. `mountView()` is unchanged in what it mounts.

A re-leased instance's host moves into another element's box, which
`poseViews` already treats as a resize ("placed again"): the canvas wait
runs before anything is posed or measured, and `pose-repaints` repaints the
page. The canvas wait is unchanged.

### D3. Below API 28 an instance keeps its lens

`pose()` sets up and field of view only from API 28; below it `setView`
takes camera and target, and the lens is the one the instance mounted with.
A movie document needs API 28 only when a view element *moves* to a camera
whose lens differs from its own (`movieViewerApi`), so two view elements
with different lenses, each keeping its own, need only API 21. Leasing such
an instance from one to the other would draw the second through the
first's lens, and below 28 the renderer does not check the lens. So an
instance whose viewer declares an API below 28 records the lens it mounted
with (its up and field of view), and is leased only to a view element whose
frame state has the same up and field of view; an instance at API 28 or
later records none and is leased to any. A view element that finds no
instance of its lens mounts a new one. The bound of D1 then holds per lens
for such a viewer, and exactly for a viewer at 28 or later. YAML episodes
need API 28 for any lens other than their first camera's, so every view of
an episode below 28 has one lens.

### D4. What `window.film` reports

- `views()` lists every mounted instance, in mount order, as `{key,
  instance, visible}`, where `key` is the view element the instance serves,
  or `null` when it is free, and `visible` is as today.
- `project(key, points)` projects through the instance `key` holds; a key
  that holds none (the last frame did not place it) is refused as today,
  `No viewer instance for view <key>`.
- `viewer` and `apiVersion` stay those of the first instance mounted.
- A view's report keeps its fields; its `instance` is the number of the
  instance that drew it.

### D5. How it is observed

At layer 5, with the viewer double: `window.viewerInstances` (one entry per
mount, the double's own record), `window.film.views()`, the reports'
`instance`, the double's recorded `highlight` and `restore` calls, the
`setVisible` calls recorded by wrapping the instance's method in the page
(the double's `setVisible` records nothing, and its mount is not changed),
and screenshots. At layer 4, `leaseViews` over every sequence of frames
drawn from four frames (A alone, B alone, A and B, none), and the lens rule.

### D6. The refusal words

None: the change adds no refusal and changes none. `No viewer instance for
view <key>` names the key as before.

## Alternatives considered

- **Dispose an instance when its chapter ends.** Bounds nothing a frame does
  not already bound, needs a disposal the viewer's handle does not declare,
  and a chapter's view that returns after another chapter would mount again.
  Out by the brief.
- **One pool per chapter** (keep the rule, free a chapter's instances when
  the chapter ends). It needs the disposal above, and a join poses the
  outgoing chapter's frames after the incoming one's have started, so
  "ended" is not a property of a frame; the lease needs neither.
- **One instance for the whole film.** Wrong for a frame placing two views
  side by side.
- **Prefer the instance a returning view last held.** Not needed: which
  instance serves a view does not change what it draws (D2), and the lowest
  free instance is simpler to state and test.
- **Ignore the lens below API 28**, or require API 28 whenever two views'
  lenses differ. The first draws a view through another's lens without any
  check noticing; the second changes the document contract's rule for the
  required API (`docs/movie-document.md`, the orchestrator's) to serve a
  runtime choice. D3 keeps both the contract and the pixels.

## Risks / Trade-offs

- [A viewer state the stage does not set on every frame would leak from one
  tenant to the next] → the stage sets time, camera, target, up and field of
  view (from 28) on every frame and diffs visibility and highlight; the
  navigation it reports is read, never set. The same assumption already
  held within a chapter, where one instance served one view through moves,
  highlights and hidden layers; the lease extends it across view elements.
  The pixel proofs (A-B-A across a lease, the six orders, preview's
  replays, incremental equals cold) are the judge on the double; the real
  viewer's evidence is the orchestrator's re-render.
- [A join between two chapters' views now alternates one instance between
  them] → each alternation moves the host, so the canvas wait runs, as it
  did before when each view's host was detached and re-attached in turn;
  the cost is unchanged.
- [The count's bound below API 28 is per lens] → stated in the contract;
  no episode or fixture below 28 has two lenses.

## Migration Plan

The stage bundle changes, so every film recaptures once. Rollback is
reverting the commit.

## Open Questions

None.
