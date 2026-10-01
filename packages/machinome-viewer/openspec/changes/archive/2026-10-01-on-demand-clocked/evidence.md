# Evidence: on-demand-clocked

Date: 2026-10-01. Worktree `WTs/on-demand-clocked`, branch
`on-demand-clocked`, from `main` 94cfcc0 (API 28); planning commit
`c5482ba`. Cut for Videomaker's curta-video campaign from its spike
(`videomaker/WTs/curta-video/workflow/ongoing/curta-video-campaign/spike.md`).
Implemented as designed. `node_modules` was installed in the worktree as a
real directory before this cycle and never installed again.

## Base

`npx vitest run` at 94cfcc0: 62 files passed, 1 skipped; **1670 passed,
2 skipped**. The API 28 bundle was built in the worktree (`npm run build`,
banner `machinome-viewer 0.7.1 - viewer API 28`) to run the browser tests
red. The whole Python suite was not run at the base.

## Red first

Widget, `npx vitest run src/options.test.ts src/version.test.ts`, before
any source change:

```
   × assertOnDemandDocument > accepts a clocked machine, with or without instructions 10ms
   × assertOnDemandDocument > accepts a posed document without instructions, as before 1ms
   × assertOnDemandDocument > still refuses a posed document with instructions, by the same message 3ms
   × assertOnDemandDocument > refuses a running program, naming the program and the mode 1ms
   × assertOnDemandDocument > accepts everything in continuous mode 0ms
   × assertFrameLoop > is silent in continuous mode 0ms
   × assertFrameLoop > refuses on demand, naming the verb, the mode and what to do instead 1ms
   × API_VERSION > declares on-demand clocked capture as API 29 8ms
 Test Files  2 failed (2)
      Tests  8 failed | 44 passed (52)
```

The helper cases failed with `(0 , __vite_ssr_import_1__.assertFrameLoop)
is not a function` (and the same for `assertOnDemandDocument`), the version
case with `expected 28 to be 29`. The extended `resolveOptions` case
(each of the four on-demand conditions still required) passed at red, as
it must: it pins today's behaviour.

Browser, `pytest tests/test_widget_e2e.py -k OnDemandClockedTest` against
the API 28 bundle:

```
E           AssertionError: 'on-demand rendering requires a posed document without instructions' is not None : the on-demand mount refused the regulator
E   AssertionError: 'on-demand rendering requires a posed document without instructions' is not None : the on-demand mount refused the clocked machine
E       AssertionError: 'on-demand rendering cannot run a program' not found in 'on-demand rendering requires a posed document without instructions'
E   AssertionError: 'on-demand rendering requires a posed document without instructions' is not None : the on-demand mount refused the clocked machine
E   AssertionError: 'on-demand rendering requires a posed document without instructions' is not None : the on-demand mount refused the clocked machine
E   AssertionError: 'on-demand rendering requires a posed document without instructions' is not None : the on-demand mount refused the clocked machine
FAILED tests/test_widget_e2e.py::OnDemandClockedTest::test_a_clock_does_not_play_on_demand
FAILED tests/test_widget_e2e.py::OnDemandClockedTest::test_a_clocked_machine_mounts_on_demand_and_poses_by_restore
FAILED tests/test_widget_e2e.py::OnDemandClockedTest::test_a_program_is_still_refused_on_demand
FAILED tests/test_widget_e2e.py::OnDemandClockedTest::test_an_on_demand_clocked_mount_shows_no_control
FAILED tests/test_widget_e2e.py::OnDemandClockedTest::test_on_demand_requests_answer_as_continuous
FAILED tests/test_widget_e2e.py::OnDemandClockedTest::test_trigger_is_refused_on_demand
6 failed, 60 deselected in 6.92s
```

`tests/test_documentation.py::test_on_demand_clocked_capture_is_documented`
was written with the manual pages, not run red on its own.

## What changed

- `src/options.ts`: `assertOnDemandDocument(renderMode, document)` (design
  D1) and `assertFrameLoop(renderMode, verb, advice)` (D4), pure.
- `src/viewer.ts`: the mount's and `manifestChanged`'s document check calls
  `assertOnDemandDocument`; `machine().trigger(name)` calls
  `assertFrameLoop` before `clockedPlay`; `setClockPlaying(true)` calls it
  after the no-clock refusal. The `renderMode` doc comment.
- `package.json`: `machinomeViewerApi` 29; `version.test.ts` records why.
- API pins moved to 29 in `tests/test_bundle.py`, `test_widget_e2e.py`,
  `test_calculator_document.py` (3), `test_clearing_document.py`,
  `test_carriage_document.py`, `test_curta_drawing.py` (2),
  `test_lock_document.py`, `test_regulator_document.py`,
  `test_running_document.py`, `test_profile_document.py`,
  `test_source_timing_browser.py`, `test_asset_load_order.py`, and the
  `describe` example in `docs/reference/cli.rst`. The first whole-suite
  run on the new source failed 15 tests on exactly these pins
  (`AssertionError: 29 != 28`, `Expected Viewer API 28`); they were
  missed in the first pass and moved before the final run.
- `tests/test_documentation.py`: the pins forbidding an `Unreleased`
  changelog section are relaxed to "at most one, above the release", per
  the pilot's ruling of 29 September 2026 that a change writes its entry
  when it lands; the released sections still must not mention API 28.
- Manual: `docs/reference/mount.rst` (`renderMode`), `docs/reference/clocked.rst`
  (refusal notes on `trigger` and `setClockPlaying`, new section
  "On-demand capture" with an example), `docs/compatibility.rst` (API 29),
  `docs/embedding.rst`. `CHANGELOG.md`: `## Unreleased` above 0.7.1.
- ADR-077 (`workflow/adrs/EXPORT/`), indexed.

## Green, on the final content

- `npm test`: 62 files passed, 1 skipped; **1677 passed, 2 skipped**
  (+7: five `assertOnDemandDocument`, two `assertFrameLoop`).
- `npm run typecheck` (`tsc --noEmit`): clean, exit 0.
- `npm run build`: `dist/machinome-viewer.js` 892.9 kb, banner
  `machinome-viewer 0.7.1 - viewer API 29`, sha256
  `b5fcdb8613aceb3936c09d755af41f1ceb9ad1125e4f5bc4e671a568a0920107`.
- `python -m pytest -q` (whole suite, workspace venv, worktree root, against
  that bundle): **244 passed, 57 warnings, 445 subtests passed in 340.45s**,
  0 skipped.
- Strict Sphinx build (`-n -W --keep-going`): succeeded.
- `openspec validate on-demand-clocked --strict`: valid; after archiving,
  `openspec validate viewer-package --type spec --strict`: valid.

## Measurements

Calculator fixture, 800x600, on demand (`test_a_clocked_machine_mounts_on_demand_and_poses_by_restore`):
`restore` of the mid bank (crank +190, no commit) followed by
`setView(viewer.view())` gives a frame different from the origin's; origin
again and mid again reproduce both frames byte for byte. A capture after
`restore` alone differs from the origin in 6198 pixels and from the
`setView` frame in 44: `setView` re-fits the near and far planes to the
posed bounds (`frameBounds` derives them from the visible box), which the
pose alone does not.

The Curta itself, read only: the project's untracked
`export/clocked_curta` (identity `18f8b447…d63c7`), this cycle's API 29
bundle, the stage's four mount options, 1920x1080, the spike's view
(camera `[240, -240, 300]`, target `[0, 0, 10]`, up `[0, 0, 1]`, fov 40),
Chromium with `--use-angle=swiftshader --enable-unsafe-swiftshader`, the
23 stroke posed at f = 0, 0.3, 0.5, 0.7, 1 by `restore` + `setView`, six
cycles (30 poses), load average about 4 to 5 from other work:

| measure | value |
|---|---|
| mount | accepted, API 29, no control element in the page |
| `machine().trigger('Turn crank')` | refused: `machine().trigger('Turn crank') needs the frame loop, which a renderMode 'on-demand' viewer does not run. Pose the transition bank by bank with machine().restore(), or mount with renderMode 'continuous'.` |
| median restore / setView (in page) | 14.1 ms / 2.8 ms |
| median screenshot / total per pose | **981 ms / 1004 ms** (range 981 to 2737 ms) |
| distinct pictures per fraction over 6 cycles | 1 each |
| picture hashes (sha256, 16) f = 0, 0.3, 0.5, 0.7, 1 | `da6a909a2a4e3316`, `ac2abddfdc5963bd`, `a2615f61262c129f`, `649d6d17cd1c098e`, `09bfcdf468aeb0fc` |

The five hashes are **identical** to the spike's continuous-mode captures
of the same banks and view (its section 4 table): on-demand draws the same
pixels, about twelve times faster (spike: 12.3 s median in continuous
mode). The frames were inspected by eye (contact sheet, not committed): the
crank turns through the stroke and the result dials read the committed
digits after it.

## Findings

- A capture after a pose alone keeps the clipping planes of the last
  framing (above). The manual says the frame that depends only on bank and
  view is the one after `setView`; a host posing every frame by `restore`
  then `setView` gets that.
- Under on-demand a container resize (`ResizeObserver` -> `renderer.setSize`)
  clears the canvas and nothing redraws it until the next explicit render.
  Seen while measuring: a host box with no height left a 150-pixel canvas.
  This predates the change and applies to posed documents too; a host
  should call `setView` after its box settles. Not changed here.
- The `viewer-package` requirement "The viewer declares its API version"
  still says the declared version SHALL be 19; the source has been past it
  since API 20. Not amended here.
- `CHANGELOG.md` records nothing of API 28 (`track-a-part-on-screen`,
  `highlight-a-part`, `move-up-and-field-of-view`) or of
  `deterministic-asset-load-order`, which landed before the pilot's ruling;
  the new `Unreleased` section carries only this change.

## Not done

- No drawing of a transition under on-demand and no on-demand running
  program (design non-goals); a posed document with instructions stays
  refused (D2).
- No new redraw entry on the handle (D3).
- Nothing pushed, merged or published; `scripts/check-dist` not run;
  nothing installed.
