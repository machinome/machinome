## 1. Red first

- [ ] 1.1 In the apply worktree, link the primary checkout's
      `machinome_viewer/widget/node_modules` (never `npm ci` or `npm install`
      through the link) and record the clean base: `npm test` and
      `npm run typecheck` counts.
- [ ] 1.2 Add `machinome_viewer/widget/src/screen.test.ts` (red: the module
      does not exist):
      - `projectToViewport` "projects a world point to viewport pixels of an
        offset canvas" (a `PerspectiveCamera` at a known pose, a canvas rect
        with non-zero `left`/`top`; the target lands at the canvas centre);
      - "answers null for a point at or behind the camera plane";
      - `boundsOnScreen` "bounds a box by its in-front corners only" (a box
        straddling the camera plane);
      - "answers null for a box wholly behind the camera or wholly off the
        canvas", and "does not clip a box that is partly off the canvas";
      - `worldBounds` "unions each mesh's box in world coordinates";
      - `searchPoint` "tries the centre first, then the grid in row order,
        then answers null", counting probes (at most 1 + 49).
- [ ] 1.3 In `version.test.ts`, change the last case to
      "declares film annotations as API 28" expecting 28 (red at 27).
- [ ] 1.4 Add to `tests/test_widget_e2e.py` (class `ViewerMountApiTest`, the
      spinner fixture, which declares no controls) and run them red against
      a bundle built from the base (they fail on the missing members):
      - `test_a_part_is_tracked_on_screen_without_declared_controls`: mount
        on demand, `setTime`, `setView`; `partOnScreen(['Hub'])` has a
        rectangle inside the canvas and a point inside it; a screenshot's
        pixel at the point is the hub's colour, not a blade's or the
        background; after a later `setTime` a blade's rectangle moves.
      - `test_a_projected_point_lands_in_its_part`: `project` of a world
        point on the hub's axis (from the fixture's geometry) lies inside
        `partOnScreen(['Hub']).rect`; a point behind the camera answers
        `null`.
      - `test_part_tracking_answers_nothing_or_refuses`: a hidden path
        answers `null`; `[]` encloses every blade's rectangle; an unknown
        path throws naming it; a non-finite world point throws.
      - `test_reading_positions_draws_no_frame`: wrap the canvas context's
        `drawArrays`/`drawElements` after mount, read `partOnScreen` and
        `project` repeatedly, and assert zero draw calls.

## 2. Implement

- [ ] 2.1 Create `screen.ts` with `projectToViewport`, `worldBounds`,
      `boundsOnScreen`, `searchPoint` and the `ScreenRect` type, moved
      unchanged in arithmetic from `partRect`/`partPoint`.
- [ ] 2.2 In `viewer.ts`, split `pickAt` into `nearestVisibleMesh` (no
      `partMeshes` guard) and the control mapping; rebuild `partRect`,
      `partPoint` on `screen.ts`; confirm `controls.test.ts`,
      `partSurface.test.ts` and `selectedControls.test.ts` stay green
      unchanged.
- [ ] 2.3 Add `partOnScreen(path)` and `project(world)` to `ViewerHandle`
      and the returned handle (design D2, D5, D6, D7); retype
      `PartControlView.rect` as `ScreenRect`.
- [ ] 2.4 Raise `machinomeViewerApi` to 28 in `package.json` only (design
      D8); document versions unchanged. Rebuild the bundle with
      `npm run build` only.

## 3. Document

- [ ] 3.1 `docs/reference/viewer-handle.rst`: a "Where parts stand on
      screen" subsection with `partOnScreen` and `project` (pixel frame,
      box-not-silhouette, not clipped, `null` cases, errors, "renders
      nothing", "Available since API 28").
- [ ] 3.2 `docs/compatibility.rst`: API 28 as the source's API after 0.7.1,
      in no published release; the 0.7.1 facts untouched. `cli.rst`
      `describe` example to API 28.
- [ ] 3.3 `tests/test_documentation.py`: pin the 0.7.1 section and
      `test_profile_contact_is_documented_as_part_of_the_release` to the
      recorded API 27 instead of the live declaration, and add a check that
      compatibility names API 28 (design D9, subject to the pilot's
      decision). Strict Sphinx build and `scripts/check-docs-browser.py`.

## 4. Validate and close

- [ ] 4.1 Widget suite, typecheck, the Python suite (one suite at a time),
      and the four browser tests green; inspect the screenshots by eye and
      record the counts and the point-search cost per call in
      `evidence.md`.
- [ ] 4.2 Sync the delta specs, strict-validate, archive, and commit the
      implementation record in this repository only. Integration, push and
      publication stay with the pilot.
