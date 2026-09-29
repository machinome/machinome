## Why

Videomaker, the local tool that renders narrated films of machinome models,
mounts this viewer in a headless page, poses it frame by frame with
`setTime`, `setView` and `setVisible`, and captures each frame. Its working
roadmap (`videomaker/workflow/ongoing/roadmap.md`, "Viewer-dependent
features", item 1) records the need: an arrow or a label that follows a
moving part needs the part's position on screen for the current pose, and
only the viewer knows it. Today the film's overlays are text at three fixed
screen positions. The originating episode is the Leonardo release film
*Revolutions*, for which the pilot asked for arrows, highlights and
transitions; the arrows are this change.

The viewer already computes exactly this, but only for a part a document
declares a control on: `controls()` reports each control's part `rect`
(`partRect`, the projected corners of the part's world bounds) and a
visible `point` on it (`partPoint`, a raycast under the nearest-visible-hit
rule). A film model declares no controls, so the listing is empty and the
computation is unreachable. A host also cannot project a single world point,
for example the tip of a blade or a joint's axis, into the frame.

## What Changes

- Add `partOnScreen(path)` to the viewer handle: for any assembly path, a
  part or a subassembly, the on-screen rectangle of its visible meshes and a
  visible point on it, in viewport CSS pixels, from the same computation
  `controls()` performs; `null` when nothing of it is visible or it is wholly
  off screen; an unknown or ambiguous path throws and names the path.
- Add `project(world)` to the viewer handle: the viewport position of one
  world-space point for the current camera, or `null` at or behind the
  camera.
- Both read the current pose and camera after the last `setTime`,
  `setView`, `setVisible`, `setRoot` or driver change, and neither renders
  or changes anything.
- Extract the projection, the box-to-rectangle and the point search out of
  `viewer.ts` into a pure module so they are tested without WebGL, and make
  `controls()` call the same functions, its answers unchanged.
- Declare viewer API 28 for this change together with `highlight-a-part`
  and `move-up-and-field-of-view`, which land with it. No document schema
  version changes.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-package`: a host reads where any assembly path and any world point
  stand on screen, without declaring controls.
- `viewer-distribution`: the package declares viewer API 28 for the three
  film-annotation capabilities, document versions 1 to 13 unchanged.
- `user-documentation`: the reference documents the two new handle members
  and compatibility names API 28 as current source, keeping the recorded
  0.7.1 release facts at API 27.

## Impact

`machinome_viewer/widget/src/viewer.ts` (two handle members; `partRect`,
`partPoint` and `pickAt` rebuilt on the extracted functions), a new
`machinome_viewer/widget/src/screen.ts` with `screen.test.ts`,
`version.test.ts` and `package.json` (`machinomeViewerApi` 28), a browser
test in `tests/test_widget_e2e.py`, `docs/reference/viewer-handle.rst`,
`docs/compatibility.rst`, `docs/reference/cli.rst` (the `describe` example)
and `tests/test_documentation.py`. The bundle is rebuilt at apply time only.
Videomaker's use of the result is proposed separately in its own
repository against the same interface. Nothing is pushed or published.
