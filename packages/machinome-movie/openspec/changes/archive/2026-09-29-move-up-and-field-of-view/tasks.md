## 0. Preconditions

- [x] 0.1 Pilot ratifies this proposal: presets-only (D1), the interpolation
  (D2), the refusals (D3), the cross-cut requirement (D4), and names the
  *Revolutions* shot that will use the move.
- [x] 0.2 A machinome-viewer bundle declaring API 28 with `setView` accepting
  `up`/`fov`, `view()` returning them, and `project`, exists; record its commit
  and hash. If its contract deviates from design.md's Context, stop and reconcile.

## 1. Red tests (fail before any implementation; record the failures)

- [x] 1.1 `test/workflow.test.mjs`, "constant up and field of view are
  unchanged": pin literally, before the change, the full `frameAt` objects of the
  existing fixture at 0, 0.5, 1, 1.5, 2 and 3 s (`up` `[0,1,0]`, `fov` 37); they
  must stay deep-equal after it. This one is green before and after by design:
  it is the regression pin, and its pre-change run is recorded as the baseline.
- [x] 1.2 `test/camera.test.mjs` (new, Node only):
  - a 0.3 shot from fov 37 to 20 over keys at 0 and 2 s: `frameAt(1).fov` is
    28.5 and `frameAt(0.5).fov` equals `37 - 17 * 0.15625`; after the last key
    it holds 20;
  - an up change from `[0,0,1]` to `[1,0,1]` gives unit vectors, equal to the
    normalized endpoints at the keys and a normalized mix between them;
  - refusals: 0.2 within-shot change (message now names format 0.3), opposite
    ups, an up along the viewing direction at some frame;
  - `requiredViewerApi` is 28 with reason `camera up/field of view (shot <id>)`
    for a within-shot change and for a cut between presets with different fov,
    and 21 for the existing fixture.
- [x] 1.3 `test/render.test.mjs`: a real-browser case with a viewer double at
  API 28 recording every `setView` argument and implementing `view()` and a
  pinhole `project` from the fov it was given. Preview of a fov-sweeping shot
  must pass the D5 projection check; the recorded `setView` calls carry the
  interpolated `fov`. A double that ignores `fov` must fail with a readback
  error. The existing API 27 case must record `setView` arguments with exactly
  the keys `camera` and `target`. An fov-sweeping episode against the API 27
  double is refused with `/Viewer API 28/`.

## 2. Implementation

- [x] 2.1 `src/episode.mjs`: lift the within-shot refusal for 0.3; add D3
  refusals; the shared format and requirement pieces if no sibling change has.
- [x] 2.2 `src/timeline.mjs`: D2 interpolation.
- [x] 2.3 `src/film.js`: D4 `setView` arguments by API; return read-back up/fov;
  a page helper projecting two world points for preview.
- [x] 2.4 `src/render.mjs`: up/fov readback in `pose` at API 28; the D5 check in
  preview for shots whose fov or up changes.
- [x] 2.5 `docs/FORMAT.md`: replace "This episode keeps up and field of view
  constant" and "Named cameras currently share a fixed up and FOV" with the 0.3
  rule, the D1 example and the refusals. `README.md`: Viewer API 28 for such
  episodes.
- [x] 2.6 `npm test` green; record red and green runs in `evidence.md`.

## 3. Consumer verification (implementation evidence)

- [x] 3.1 Before implementing, preview the unchanged *Revolutions* and sawmill
  episodes with the API 27 bundle and keep the stills; after implementing,
  repeat and compare byte-for-byte. Record the result.
- [ ] 3.2 In the Leonardo repository (committed there, never here), add the
  preset and author the ratified shot in format 0.3; `check`, then `preview`
  with the API 28 bundle; record the D5 measurements and stills, and the refusal
  with the API 27 bundle.
- [x] 3.3 Render a short silent clip of that shot for motion review; record its
  hash in `evidence.md`.

## 4. Human review (not claimed by automation)

- [ ] 4.1 The pilot judges whether the zoom or roll reads well in motion;
  automated checks prove only that the requested lens and orientation reached
  the picture.
- [ ] 4.2 Publication, pushing and final release renders need the pilot's
  explicit request.


Implementation note (29 September 2026): items 3.x marked done were run on a
scratch test episode against the current sawmill export, not in the Leonardo
repository, which this run was not permitted to change; see evidence.md. The
Leonardo authoring items and human review remain open.
