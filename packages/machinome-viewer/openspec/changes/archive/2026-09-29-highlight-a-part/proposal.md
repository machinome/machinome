## Why

Videomaker's roadmap (`videomaker/workflow/ongoing/roadmap.md`,
"Viewer-dependent features", item 2) records the second viewer need of its
films: tint a part so the narration can point at it, and dim or ghost the
rest, so a housing can be seen through instead of hidden. The only control
a film has today is `setVisible`, and the sawmill rehearsal hides whole
layers to show what is inside; that is the workaround this replaces. The
pilot asked for highlights for the Leonardo release film *Revolutions*.

The viewer already lifts a part's look: hovering a declared control raises
the emissive colour of the part's meshes to `HOVER_EMISSIVE` and returns a
closure that puts it back (`liftParts`, `drive-the-run-by-touch` design D7).
That lift reaches only declared controls' meshes, has one fixed colour,
leaves the other parts as they are, and restores by writing back values it
copied, so a second writer on the same material would corrupt it.

## What Changes

- Add `highlight(paths, options?)` to the viewer handle: the named parts'
  materials take an emissive tint in `options.color` (a hex colour,
  default `#ffb000`), and every other part is kept, dimmed or ghosted
  (drawn translucent so the highlighted part is seen through it) per
  `options.others` (default `'keep'`). It renders synchronously and returns
  a restore function that puts every material back exactly and renders.
- One highlight stands at a time: a second `highlight` before the first is
  restored is refused by name. Restoring twice is harmless.
- Hidden parts stay hidden; focus, visibility and the navigation state are
  untouched; nothing is notified.
- A standing highlight survives `reload()`, `manifestChanged()` and
  `artifactChanged()`: it is lifted off before meshes are replaced and put
  back on the new meshes of the same paths; a path the new tree lacks is
  dropped.
- Hover and highlight share one owner of every material's departures from
  its declared look, so their restores can never overwrite each other.
- `partOnScreen`'s point (from `track-a-part-on-screen`) sees through a
  ghosted part, as the eye does.
- Lands under viewer API 28, declared by `track-a-part-on-screen`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-package`: a host highlights parts and keeps, dims or ghosts the
  others, reversibly; a ghost does not hide a tracked part.

## Impact

A new `machinome_viewer/widget/src/presentation.ts` with
`presentation.test.ts`; `viewer.ts` (the handle member, `liftParts` moved
onto the presentation owner, the three mesh-replacement points, the point
predicate); browser tests in `tests/test_widget_e2e.py`;
`docs/reference/viewer-handle.rst`. A draft decision record,
`workflow/adrs/EXPORT/ADR-076-a-parts-presented-look-has-one-owner.md`,
Proposed. Requires `track-a-part-on-screen` (API 28 and the point
predicate). Nothing is pushed or published.
