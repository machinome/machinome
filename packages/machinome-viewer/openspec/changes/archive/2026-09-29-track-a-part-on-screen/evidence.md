# Evidence: track-a-part-on-screen

Date: 2026-09-29. Worktree `WTs/film-annotations`, branch `film-annotations`,
base viewer main `40031a5`; planning commit `955c185` (this change), with
`ab6cd51` and `8a79ba2` (the two changes applied after it on the same line).
Ratified as proposed; D9 decided by the pilot as the design describes (the
recorded 0.7.1 facts stay at API 27, no changelog section is opened).

## Base

`machinome_viewer/widget/node_modules` linked to the primary checkout's (no
`npm ci`/`npm install` anywhere). Clean base:

- `npx vitest run`: 60 files passed, 1 skipped; **1615 passed, 2 skipped**.
- `npx tsc --noEmit`: clean.
- Bundle built from the base with `npm run build`: banner `machinome-viewer
  0.7.1 - viewer API 27`.

## Red first

- `src/screen.test.ts` (9 cases) against no module:
  `FAIL src/screen.test.ts — Error: Cannot find module './screen'`.
- `src/version.test.ts` "declares film annotations as API 28":
  `AssertionError: expected 27 to be 28`.
- `src/documentation.test.ts` gained two cases by construction once the two
  members were declared on `ViewerHandle` ("documents ViewerHandle.partOnScreen",
  "documents ViewerHandle.project"); they pass only with the reference entries.
- Five browser tests in `tests/test_widget_e2e.py::ViewerMountApiTest`, run
  against the API-27 base bundle: **5 failed**, each with
  `Page.evaluate: TypeError: viewer.partOnScreen is not a function`
  (`test_a_part_is_tracked_on_screen_without_declared_controls`,
  `test_a_projected_point_lands_in_its_part`,
  `test_part_tracking_answers_nothing_or_refuses`,
  `test_reading_positions_draws_no_frame`,
  `test_a_declared_control_and_its_part_agree`).
- The two documentation pins D9 names, run unchanged (from `HEAD`) against the
  tree at API 28: **2 failed** —
  `assert 'viewer API 28' in '0.7.1 — 27 September 2026 …'` in
  `test_the_manual_states_the_release` and `assert 28 == 27` in
  `test_profile_contact_is_documented_as_part_of_the_release`. Red by
  construction, as D9 predicted; they now assert the recorded 27.

## What changed

- `src/screen.ts`: `projectToViewport`, `worldBounds`, `boundsOnScreen`,
  `searchPoint`, `POINT_GRID`, and the `Point`, `ScreenRect`, `CanvasBounds`
  types, moved from `partRect`/`partPoint` with the arithmetic unchanged
  (the in-front test is the same `z >= 0` in view space; the rectangle is the
  projected corners of the world box, unclipped; the probe order is centre,
  then the 7 x 7 grid in row order).
- `src/viewer.ts`: `pickAt` split into `nearestVisibleMesh` (no
  `partMeshes` guard) and the control mapping, which keeps its early return;
  `partRect`/`partPoint` rebuilt on `screen.ts`; `partOnScreen(path)` and
  `project(world)` on the handle (D2-D7); `PartControlView.rect`/`point`
  retyped `ScreenRect`/`Point`; `Point` and `PartRect` re-exported from
  `screen.ts` so their importers are unchanged.
- `package.json`: `machinomeViewerApi` 27 -> **28**, once, for the three
  changes on this line (D8). Document versions 1-13 unchanged. Python pins of
  the declared API (`test_bundle.py` and ten browser suites) moved to 28.
- Manual: `docs/reference/viewer-handle.rst` "Where parts stand on screen";
  `docs/compatibility.rst` — the list is now "The 0.7.1 release declares"
  with viewer API 27 written out, followed by the current source's API 28
  "after 0.7.1 and in no published release"; the migration paragraph names
  API 28; `docs/reference/cli.rst` `describe` example at 28;
  `docs/index.rst` writes the recorded API 27 instead of the live
  substitution. `tests/test_documentation.py`: the two pins moved to the
  recorded 27 (D9) and `test_film_annotations_are_documented_as_current_source`
  added. README and CHANGELOG untouched (they already say 27; no section
  opened).

## Green

- `npx vitest run`: 61 files passed, 1 skipped; **1626 passed, 2 skipped**
  (+9 `screen.test.ts`, +2 documentation coverage). `controls.test.ts`,
  `partSurface.test.ts` and `selectedControls.test.ts` green unchanged.
- `npx tsc --noEmit`: clean.
- `python -m pytest` (whole suite, one at a time, workspace venv, from the
  worktree root so the worktree's package and bundle are the ones tested):
  **225 passed, 435 subtests passed, 0 skipped**, 323 s. Headless Chromium
  (Playwright's cached shell) ran every browser test.
- The five new browser tests: 5 passed.
- `python -m sphinx -n -W --keep-going -b html docs docs/_build/html`:
  build succeeded, no warnings. `scripts/check-docs-browser.py`: 14 pages,
  2 viewports, 208 local links, mobile menu, search, interactive and
  reference examples passed, no browser errors.
- `openspec validate track-a-part-on-screen --strict`: valid.

## Measurements

Headless Chromium, SwiftShader, 800 x 600, spinner fixture (5 meshes), mean
of 50 calls:

- `partOnScreen(['Hub'])`, point found at the centre (1 raycast): 0.15 ms;
  `partOnScreen([])`: 0.07 ms; `project`: 0.006 ms.
- Worst case, a blade seen end-on wholly behind the hub (`setTime(0.5)`,
  camera `[200, 0, 2]`): every probe misses, `point` null after 1 + 49
  raycasts: **0.5 ms** per call. `rect` alone costs no raycast.
- Zero draw calls across 150 reads between two host changes (the probe
  wrapping `drawArrays`/`drawElements` counts the frame `setTime` draws), no
  assembly notification, camera and target unchanged.

Screens inspected by eye with the rectangles, points and a projected point
drawn over them (`_build/film-annotations/track-t0.png`, `track-t0.1.png`,
regenerated by the script in this cycle, not committed): each rectangle
encloses its part, each point lies on its part's visible surface, the
rectangles of a turning blade follow it between the two times, and the
projection of the top of the hub's axis lands at the centre of its top face.

## Deviations from the design

- `searchPoint` never asks its predicate about a point outside the canvas;
  the old `partPoint` made the same check inside its predicate. Same answers.
- `project` takes exactly the array form D1 declares; a `Vector3` is refused
  like any non-array.
- One test beyond the four the tasks name,
  `test_a_declared_control_and_its_part_agree`, for the spec scenario "A
  declared control and its part agree" (touched fixture: every on-screen
  control's `rect` and `point` equal `partOnScreen(control.part)`'s). It reads
  after a drawn frame, for the finding below.
- `docs/reference/mount.rst` said the bundle's `apiVersion` was
  "|viewer-api| in this release"; at 28 that would misstate 0.7.1. It now
  says 27 in the 0.7.1 release and |viewer-api| in the current source. D9's
  intent, on a page its text did not list.

## Out of scope, found while applying

- `controls()` updates the scene's world matrices but not the camera's, so
  read in a continuous mount before the first frame is drawn (straight after
  `mount()` resolves) it answers from a camera `matrixWorldInverse` the
  framing has not yet refreshed: on the touched fixture every control's
  `rect` was null there while `partOnScreen` of the same part, which updates
  the camera itself (D6), answered. After one frame the two agree exactly.
  Not changed here: the design keeps `controls()`'s answers as they are. A
  one-line `camera.updateMatrixWorld()` in `partControlViews` would close it.

Nothing is pushed or published; integration is the pilot's.
