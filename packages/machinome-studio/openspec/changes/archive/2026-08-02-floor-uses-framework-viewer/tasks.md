## 1. Red first: the fake framework and the failing preparation cases

- [x] 1.1 Teach `tests/fixtures/fake_solid.py` a `viewer` subcommand: tolerate a
      bare subcommand in its argument parsing, write a stub bundle file, and
      print `{"path": ..., "apiVersion": N}`.
- [x] 1.2 Extend the fixture's state file so a test can make `solid viewer` exit
      non-zero with a remedy on stderr, or report an `apiVersion` below what the
      floor requires.
- [x] 1.3 Add failing tests to `tests/test_project_preparation.py`: preparation
      fails with the framework's remedy text when no viewer is available;
      preparation fails naming required and installed versions when the reported
      `apiVersion` is too low; preparation succeeds and carries the bundle path
      and version on `PreparedProject` when the viewer is usable.
- [x] 1.4 Add a failing test to `tests/test_floor_api.py`: `GET
      /viewer/solid-widget.js` returns the prepared bundle's bytes, and returns
      404 when the app was built without one.

## 2. Preparation and the floor service

- [x] 2.1 Add `REQUIRED_VIEWER_API` and a viewer-accessor stage to
      `floor/preparation.py`, ordered before the build, reporting the
      framework's own stderr as the failure reason and naming both versions on a
      version mismatch.
- [x] 2.2 Carry `viewer_bundle` and `viewer_api_version` on `PreparedProject`.
- [x] 2.3 Add the `GET /viewer/solid-widget.js` route to `floor/app.py` behind a
      `viewer_bundle` parameter on `create_app`, serving that one file.
- [x] 2.4 Pass the prepared bundle through `floor/orchestrator.py` and
      `floor/__main__.py`.
- [x] 2.5 Confirm tasks 1.3 and 1.4 now pass.

## 3. The browser consumes the framework viewer

- [x] 3.1 Add the local type declarations for `window.SolidNodeWidget`
      (`mount`, `ViewerOptions`, `ViewerHandle`) to `floor/frontend/src/`.
- [x] 3.2 Load `/viewer/solid-widget.js` from `floor/frontend/index.html` before
      the module entry.
- [x] 3.3 Rewrite `FunctionalModel` in `floor/frontend/src/main.tsx` to mount
      through the global with the option mapping in design D5, keeping the
      remount-per-generation structure, the preserved-camera ref, the dispose on
      unmount, and the existing mount-failure message.
- [x] 3.4 Delete `floor/frontend/src/viewer.ts`.
- [x] 3.5 Remove `three`, `@types/three`, and `jokenizer` from
      `floor/frontend/package.json` and refresh `package-lock.json`.
- [x] 3.6 Run `npm --prefix floor/frontend run test` (the TypeScript check) and
      `npm --prefix floor/frontend run build`; commit the regenerated
      `floor/static`, confirming the second three.js copy is gone.

## 4. Proof

- [x] 4.1 Add a test asserting the floor's `REQUIRED_VIEWER_API` matches the
      viewer interface the local declarations describe, so a framework bump
      cannot pass silently.
- [x] 4.2 Run `scripts/test-e2e` and confirm the browser test still renders a
      model, shows the Timeline toggle for an animated model, and preserves the
      maker's camera across a rebuild.
- [x] 4.3 Run the full shop suite (`python -m pytest tests/`) and
      `bash tests/dev-env-test.sh`.
- [x] 4.4 Open a named project shop against the framework `sprint-002` worktree
      and visually confirm the model renders, the Timeline toggle behaves, and a
      rebuild keeps the camera.

## 5. Ratified records

- [x] 5.1 Amend `openspec/specs/functional-model-inspection/spec.md` from the
      delta: the `SHALL NOT use the separate export widget` mechanism is
      replaced by the outcome, and the new open-refusal requirement is added.
- [x] 5.2 Amend
      `docs/adrs/0004-static-build-artifact-boundary-for-functional-model-inspection.md`
      per design D8, and confirm `docs/adrs/README.md` still describes it
      correctly.
- [x] 5.3 Update `shop-skills/solid-node-api/SKILL.md` for the additive
      `viewer.json` `format` field, the `solid viewer` accessor, and the one
      expected content-hash refresh after a framework upgrade.
- [x] 5.4 Run `openspec validate --all --strict`.

## 6. Cycle close

- [x] 6.1 Sync the delta into the baseline spec and archive the change through
      OpenSpec.
- [x] 6.2 Record the cycle's commits and archive path in
      `docs/product/sprints/current.md`, and create the implementation commit.
