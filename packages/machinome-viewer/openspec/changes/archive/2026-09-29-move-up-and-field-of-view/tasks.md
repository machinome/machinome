## 1. Red first

- [x] 1.1 Apply on the line that carries `track-a-part-on-screen` (API 28).
      Link the primary checkout's widget `node_modules`; never install.
      Record the base counts.
- [x] 1.2 Extend `camera.test.ts` under `describe('scriptedView')` (red: the
      fields are ignored and nothing is refused today):
      - "copies up and fov without aliasing caller state";
      - "leaves up and fov undefined when omitted";
      - "refuses a non-finite or non-three-dimensional up";
      - "refuses a zero up";
      - "refuses an up parallel or anti-parallel to the view direction"
        (and accepts one 1e-3 rad off it);
      - "refuses a fov of 0, 180, negative, NaN, Infinity or a string";
      - "does not check the omitted up against the view direction" (a camera
        straight above its target is accepted, as today).
      Add a pure helper test, "an orbit is rebuilt only when the up
      direction changes" (same direction scaled: no; opposite: yes).
- [x] 1.3 Add to `tests/test_widget_e2e.py` (spinner) and run red against the
      API-28 bundle without this change:
      - `test_setview_changes_the_field_of_view`: on-demand mount; the
        same camera and target, far enough that the model fits at both, at
        `fov` 60 then 20: the model's non-background extent in the
        screenshot grows by about tan(30 deg)/tan(10 deg); `view().fov`
        reads 20.
      - `test_setview_rolls_to_the_supplied_up`: `up` `[1, 0, 0]` then
        `[0, 1, 0]` with a camera on the Z axis: the second screenshot
        matches the first rotated a quarter turn about the canvas centre
        (Pillow `rotate`) far better than the first unrotated, the spinner
        having threefold, not fourfold, symmetry; `view().up` equals what
        was sent.
      - `test_setview_refusals_leave_the_frame`: a parallel up, a zero up,
        `fov` 0 and 180 each throw naming the value; `view()` and the
        screenshot are unchanged.
      - `test_an_adopted_view_survives_refocus_and_reload`: after `setView`
        with `up` and `fov`, `setRoot(['Hub'])` and `reload()` keep both.
      - `test_orbit_turns_about_the_adopted_up`: continuous mount, adopt a
        new up, drag horizontally with `page.mouse`; the angle between
        `camera - target` and the adopted up is unchanged within 1e-6 rad
        and `view().up` is unchanged.

## 2. Implement

- [x] 2.1 `camera.ts`: extend `scriptedView` (design D3) and export the
      orbit-axis comparison helper; keep `ViewerView` for mount and
      framing.
- [x] 2.2 `viewer.ts`: `ViewInput` and `View` shapes (D1); viewer-held `up`
      and `fov` (D2); `applyFrame` reads them; `captureView` reports them;
      orbit replacement and the delegating `orbit` collaborator (D4);
      `dispose()` disposes the current controls. Rebuild the bundle with
      `npm run build` only.

## 3. Document

- [x] 3.1 `docs/reference/viewer-handle.rst`: `view()` returns four fields;
      `setView` takes optional `up` and `fov`, omitted keeps, the refusals,
      the omitted-up parallel exception, persistence across refocus and
      reload, orbit about the adopted up, "since API 28"; the mount
      reference keeps `up`/`fov` as mount options and says a `view()`
      snapshot passed as `view` restores camera and target only. Strict
      Sphinx build.

## 4. Validate and close

- [x] 4.1 Widget suite, typecheck, Python suite (one at a time), the five
      browser tests; inspect the rolled and narrowed frames by eye; record
      the mount-option leniency finding (design, Risks) in `evidence.md`
      and in `workflow/warts.md` if the pilot wants it tracked.
- [x] 4.2 Sync the delta spec, strict-validate, archive, and commit in this
      repository only. Integration, push and publication stay with the
      pilot.
