## Context

`viewer.ts` already answers "where is this part on screen" for declared
controls (`drive-the-run-by-touch`, design D15):

- `partRect(control)` (viewer.ts, after `rebuildPartControls`) takes the
  control's meshes from `partOf`, keeps those `visibleUpTo(mesh, scene)`,
  unions each mesh's geometry bounding box transformed by `matrixWorld`,
  projects the eight corners of that world box, drops corners at or behind
  the camera plane, and returns the enclosing rectangle in viewport CSS
  pixels (`renderer.domElement.getBoundingClientRect()` offsets), or `null`
  when no mesh is visible, no corner is in front, or the rectangle lies
  wholly outside the canvas.
- `partPoint(control, rect)` tries the rectangle's centre, then a
  `POINT_GRID` x `POINT_GRID` (7 x 7) grid in row order, and accepts the
  first point inside the canvas at which `pickAt` (the nearest visible
  raycast hit) names the control.
- `partControlViews()` calls `scene.updateMatrixWorld(true)` first.

Three facts make that unreachable for a film. `partOf` holds only meshes of
declared controls. `pickAt` returns `null` at once when `partMeshes` is
empty, which it is for every document without controls. And the corner
projection is inlined, so no host can project a single point.

Videomaker (`src/film.js`) mounts with `renderMode: 'on-demand'`, external
animation, no driver or part controls, and calls `setVisible`, `setTime` and
`setView` per frame, each of which renders synchronously. The camera is not
in the scene graph, so its `matrixWorldInverse` is current only because each
of those setters renders.

## Goals / Non-Goals

**Goals:**

- A host reads the on-screen rectangle and a visible point of any assembly
  path, and the on-screen position of any world point, for the pose and
  camera it last set.
- `controls()` keeps its exact answers, now computed by the same functions.

**Non-Goals:**

- No drawing: arrows, labels and their styling are the host's. The viewer
  reports positions only.
- No change to the document format, the producer or the published schema
  versions.
- No tighter silhouette: the rectangle stays the projected world-aligned
  box, as `controls()` reports it today.
- No depth or occlusion answer for `project()`: it says where a point lands,
  not whether it is seen.

## Decisions

### D1. Two handle members, in the frame `controls()` already uses

```ts
export interface ScreenRect { x: number; y: number; width: number; height: number; }
export interface PartOnScreen { rect: ScreenRect; point: Point | null; }

interface ViewerHandle {
  partOnScreen(path: AssemblyPath): PartOnScreen | null;
  project(world: readonly [number, number, number]): Point | null;
}
```

`Point` is the existing exported `{x, y}`. Positions are viewport CSS
pixels, the frame of `PartControlView.rect` and of `page.mouse.click`, so a
host positions an absolutely placed overlay by subtracting its own
container's `getBoundingClientRect()` origin. `PartControlView.rect` is
retyped to `ScreenRect`, which is the same shape.

### D2. The path's meshes are its subtree, read at call time

`partOnScreen` resolves the path with `tree.requirePath(path)` and collects
every `THREE.Mesh` under that node's group: its own model, its descendants,
a flexible part's mesh and its decals. `[]` names the root, the whole model.
Nothing is cached, so a path is answered for whatever meshes the tree holds
at the moment; the three mesh-replacement points need no new bookkeeping.

### D3. The same rectangle and the same point rule

The corner projection, the in-front test and the off-canvas test move
unchanged from `partRect` into `screen.ts` as
`boundsOnScreen(box, camera, canvas): ScreenRect | null`, beside
`worldBounds(meshes): Box3` (the union loop) and
`searchPoint(rect, canvas, reaches): Point | null` (the centre-then-grid
search). `partRect` and `partPoint` become callers of them, and so does
`partOnScreen`. Consequently:

- `rect` is the projected world-aligned box of the visible meshes, so it
  encloses the part and may be larger than its silhouette, and it is not
  clipped to the canvas: a part partly off screen reports a rectangle that
  extends past the canvas edge. `null` only when nothing is visible or all
  of it is off screen.
- `point` is a point inside the canvas and inside `rect` at which the
  nearest visible surface belongs to the path, or `null` when no probe of
  the bounded search finds one (for example, a part wholly behind another).

### D4. A pick that does not need declared controls

`pickAt`'s raycast loop becomes `nearestVisibleMesh(x, y): THREE.Mesh | null`
with no `partMeshes` guard. `pickAt` keeps its early return for a document
with no controls (the hover poll must stay free there) and maps the mesh
through `partMeshes` as before. `partOnScreen`'s `reaches` asks whether
`nearestVisibleMesh` is one of the path's meshes. `highlight-a-part`
extends this predicate so that a ghosted mesh does not occlude; this change
defines the rule without ghosts.

### D5. `project` is the corner projection for one point

`projectToViewport(world, camera, canvas): Point | null` in `screen.ts`
returns `null` when the point's view-space `z >= 0` (at or behind the
camera plane, the same test `partRect` applies to a corner) and otherwise
the viewport position, which may lie outside the canvas: a host decides
what to do with an off-screen point. Coordinates are the scene's world
frame, the frame `setView`'s `camera` and `target` are given in. The
existing `toClient` (gesture geometry) keeps its behaviour and is not
routed through the null rule.

### D6. Reading never renders and needs no frame

Both members call `scene.updateMatrixWorld(true)` and
`camera.updateMatrixWorld()` before measuring. Neither calls
`renderer.render`, changes a material, a visibility or the camera, or
notifies `onAssemblyChange`. The answer is for the state the last host call
left, whether or not a frame has been drawn since, so the film may read
after `setTime`/`setView` in either render mode.

### D7. Refusals

- Unknown or ambiguous path: `requirePath`'s own error, which names the
  path (`Unknown assembly path: Water drive/Wheel`). Thrown before anything
  is measured.
- A path that is not an array of strings: throws naming `partOnScreen`.
- `world` that is not three finite numbers: throws
  `project needs three finite world coordinates`.
- A disposed viewer: both throw `<member> cannot use a disposed viewer`, as
  `setView` does.

### D8. API 28, declared once for three changes

`machinomeViewerApi` rises from 27 to 28 in `package.json` once, in this
change's tasks, covering this change, `highlight-a-part` and
`move-up-and-field-of-view`, which are applied on the same line and
integrated together. A host requiring any of the three checks
`apiVersion >= 28`. Document versions stay 1 to 13. If the pilot ratifies
fewer than three, the API-28 requirement text is trimmed to the ratified
ones before apply.

### D9. Release facts: the source runs ahead of the recorded release

`tests/test_documentation.py` pins the current changelog section (0.7.1)
to name `viewer API {machinomeViewerApi}` and pins the API to 27, and it
refuses an "Unreleased" section and the word "unreleased" on every
reader-facing page. Raising the source to 28 therefore turns those pins red
by construction, not by a documentation defect. Following the precedent of
`distinguish-same-part-joint-controls` (current-source API 27 over a
recorded API-26 release), this change keeps the recorded release facts as
they are: the 0.7.1 changelog section, README and `docs/index.rst` keep
saying API 27, and those two pins are changed to assert the recorded 27 for
the 0.7.1 section rather than the live declaration. `docs/compatibility.rst`
and the reference name API 28 as the source's API, "after 0.7.1, in no
published release". No changelog section is opened; the entry is written
when the pilot cuts the release that carries API 28. The `describe`
example in `docs/reference/cli.rst` follows `package.json` (its test pins
that). **Pilot decision requested:** confirm this, or choose an
`Unreleased` changelog section, which the current test and the
write-the-manual skill both refuse.

## Risks / Trade-offs

- [The rectangle is a box, not a silhouette] -> a long diagonal part gets a
  loose rectangle. `point` is the tight answer for an arrow's tip; the
  rectangle is for placement. Stated in the reference.
- [The point search costs up to 50 raycasts against the scene per call] ->
  bounded, and the film calls it for one or two paths per frame; `rect`
  alone costs none. Measured and recorded in evidence at apply.
- [A host reads before any frame in continuous mode] -> D6 updates matrices
  itself, so the answer does not depend on a render having happened.

## Migration Plan

Additive: no member changes shape or behaviour; `controls()` answers are
pinned by its existing tests. A host at API 27 lacks the two members and
can test `apiVersion` before calling them.

## Open Questions

- D9's release-fact handling is the pilot's call.
