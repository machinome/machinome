## Why

Videomaker's roadmap (`videomaker/workflow/ongoing/roadmap.md`,
"Viewer-dependent features", item 3) records that a film's field of view
and up direction cannot change within a shot: they are mount options only,
so every named camera of an episode shares one up and one field of view,
and a shot cannot tighten its angle of view or roll to follow a part. The
film's timeline already computes an `up` and a `fov` per frame
(`src/timeline.mjs` returns them from the camera presets), and the page
drops them because `setView` accepts only `camera` and `target`
(`src/film.js` passes them at mount). The pilot asked for this with the
annotations and highlights for the Leonardo release film *Revolutions*; of
roadmap item 3, only per-view up and field of view is taken here. Orbit
paths and "frame this part" are not proposed: no episode asks for them.

## What Changes

- `setView({camera, target, up?, fov?})`: `up` and `fov` become optional
  per call; an omitted one keeps its current value. The view is adopted and
  drawn before the call returns, as today.
- `view()` returns `{camera, target, up, fov}`: `up` a detached three.js
  vector as last adopted, `fov` the vertical field of view in degrees.
- New refusals, checked before anything changes: an `up` that is not three
  finite numbers, is zero, or is parallel to the view direction; a `fov`
  that is not a finite number strictly between 0 and 180 degrees.
- Refocusing, in-place updates and reload keep the adopted up and field of
  view instead of reverting to the mount options.
- Orbiting by pointer turns about the adopted up direction: three.js's
  orbit controls fix their axis when constructed, so the viewer replaces
  them when the up direction changes.
- Lands under viewer API 28, declared by `track-a-part-on-screen`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-package`: a scripted view change may also set the up direction
  and the field of view, and the view read back reports both.

## Impact

`machinome_viewer/widget/src/camera.ts` (`scriptedView` validates and
copies `up` and `fov`) and `camera.test.ts`; `viewer.ts` (`ViewInput`,
`View`, `applyFrame`, `captureView`, the orbit controls' replacement and
the part surface's orbit collaborator); browser tests in
`tests/test_widget_e2e.py`; `docs/reference/viewer-handle.rst`. The mount
options `up` and `fov` are unchanged. Requires `track-a-part-on-screen`
for API 28. Nothing is pushed or published.
