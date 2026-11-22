# Evidence: declare-a-models-app

Recorded by the applying agent on 22 November 2026 in the framework worktree
`machinome/WTs/model-apps`, branch `model-apps`, planning commit `c7611f09`
above base `50bdffdf`, with the companion `show-a-models-own-app`
implemented in the same worktree and uncommitted. Nothing is committed.
Task 6.7 (sync, archive, commit) is not done here; task 6.6 is recorded
under "Decision record" at the end. The observation behind design Decision 5 and its probe are in
`evidence/`, kept as they were.

## The bench (tasks 1.2 and 1.3)

- The worktree was not clean when this cycle began, by arrangement: the
  companion's implementation (viewer source, tests, React in
  `package-lock.json`, the manual pages it wrote and the framework's
  `docs/conf.py`, `docs/index.rst` and `tests/test_docs_structure.py`
  edits) stood uncommitted above the one planning commit `c7611f09`. Its
  tasks 1.3 to 5.5 were done (its `evidence.md`), so task 4's bundling ran
  through the real provider.
- Tests ran on the bench venv from `packages/machinome`, one process at a
  time; no `npm ci`/`npm install`/`scripts/check-dist`; nothing under
  `projects/` opened; port 9010 never used (every port bound free).
- Tools: Node 24.11.1 (the viewer's toolchain refusal is None), OpenSCAD on
  the PATH, Playwright's Chromium.

## Red on the base (task 2.2)

### P4's pin

`Calculator`'s `viewer.json` built on the base (an in-process
`Builder(tests/clocked_project/calculator.py:Calculator, watch=False)` into
a fresh temporary build directory, twice, identical): 9,030 bytes, raw
SHA-256 `a001c2461c1a870be585d73f96be8f73638ae9fec10e83b9dc02f21964dd6bce`
(this checkout's source mtimes). Pinned with each `"mtime": <seconds>`
written `"mtime": 0`, since a source file's modification time is a property
of the checkout: **`eb5141b77c9568e3d7d5d423ca0db8296202c672a8343f4786d634ffc479e5e6`**.

### `tests/test_model_app.py`, D/P/R/W/E (X excluded), on the base

`25 failed, 5 passed, 4 subtests passed in 99.76s`. Each failure, first
line:

- D1, six forms (42, `/abs/x.tsx`, `x.py`, `''`, `C:/x.tsx`, `app\x.tsx`):
  `AssertionError: TypeError not raised` (accepted today).
- D2 (both): `ModuleNotFoundError: No module named 'machinome.core.app'`.
- P1, P2, P3: `KeyError: 'app'` (the document has no record).
- R1-R4: `AssertionError: no logs of level ERROR or higher triggered on
  core` (nothing reads `app`; nothing refused).
- W1, W1 through a symlinked project, W2: `KeyError: 'app'`.
- W3: the app edit was not seen by anything; the thread was still
  watching at the bounded wait, `no logs of level INFO or higher triggered
  on core.builder`.
- W5: `ImportError: cannot import name 'watch_publication'`.
- E1: `KeyError: 'app'`; E2 (both), E3's `export_node` half:
  `ImportError: cannot import name 'ExportAppRefused'`; E3's CLI half:
  `AssertionError: 0 != 1 : Exported to …` (the widget-less export wrote
  its output).

Green on the base, as the design says: P4 (the pinned bytes, and no viewer
asked: `machinome.viewer.resolve` patched to fail), W4, E4, and D1's
accepted forms.

### S1, on the base

`tests/test_viewer_seam.py` with S1 and the updated pins: 3 failed, 38
passed (`OPERATIONS` lacks `bundle`; `machinome.viewer` has no `Bundler`;
`DEFAULTS` has no `bundle`, `KeyError`). The seam test **as committed at
`c7611f09`** already failed 2 tests against the companion's provider
(`web.OPERATIONS` pinned without `bundle`, and the operation-to-members map
raising `KeyError: 'bundle'`); S1 updates those pins.

### X1 and X2, on the base

`3 failed in 159.93s`:

- X1: `KeyError: 'app'` (the export's manifest has no record).
- X2, the app half: `TimeoutError` waiting for
  `.calculator-app .calculator-app-key` (no app).
- X2, the Python half: red for the reason
  `evidence/develop-reload-observation.md` records. A first run of it was
  invalid (the test waited with `time.sleep`, so Playwright dispatched no
  response events; the same test went green on the implementation only
  after the wait was made on the page). It was therefore run again on a
  true base: every framework source file this change touches put back to
  `HEAD` and `core/app.py` moved out (copies kept, restored afterwards and
  compared byte-equal): `AssertionError: … the page never read the
  published edit; it read [['Set four', 'Stroke'] × 4]` in 65.09 s, the
  fourth read being the one at the builder's respawn, before the new
  document was published, and nothing after it.

## Green (tasks 3 to 4)

- 3.1: D1, D2 `4 passed, 10 subtests passed`.
- 3.2: `tests/test_viewer_seam.py` `41 passed, 50 subtests passed`.
- 4.2: P1-P4, R1-R4, W1-W4 and W1 through a symlinked project: `13 passed`
  in 17.96 s.
- 4.2b: W5 `1 passed`.
- 4.3: E1-E4 `6 passed`.
- 4.5: X1 and both halves of X2 `3 passed`; then the whole file:
  **`27 passed, 10 subtests passed in 39.12s`**, no skip.

### X2's times (task 4.5)

From the edit to the open page showing it, on the bench, through
`machinome develop` on a scratch copy of the fixture project:

| edit | this change | the observation, at the base |
| --- | --- | --- |
| an app component's text (`Readout.tsx`) | 0.39 s and 0.49 s (two runs); no builder `START` after the edit, no `.stl` requested, the same canvas, the page not loaded again | (no app at the base) |
| the model's Python (a third instruction) | 1.12 s, 1.17 s (two runs): the page reads the published document when it is published | never: shown only at the following edit (observation: reload 0.1 s after the edit, publication about 1 s later, unannounced) |

### Timings (task 4.4)

Three `machinome build` runs each, the parts already current (one build
before them), separate build directories:

| | runs | median |
| --- | --- | --- |
| `machinome build` `Calculator` | 1.21, 1.15, 1.20 s | 1.20 s |
| `machinome build` `CalculatorApp` | 1.39, 1.38, 1.41 s | 1.39 s |
| publication alone (`_write_viewer_snapshot`, in process) `Calculator` | 0.021, 0.012, 0.011 s | 0.012 s |
| publication alone `CalculatorApp` | 0.184, 0.178, 0.194 s | 0.184 s |

The app adds about 0.17-0.19 s a publication, which is the companion's
measured bundling (median 0.18 s): Node's start, esbuild, React.

## Neighbouring suites (task 4.5)

Each run alone, from `packages/machinome`, after task 4.3: `test_web_viewer_capture.py`, `test_viewer_seam.py` (above), and every file a search for `_write_viewer_snapshot`, `export_node` or `Builder(` in `tests/` names, with `test_manager_develop.py`, `test_cli.py`, `test_build_defaults.py`, `test_build_subprocess_isolation.py` and `test_cli_lazy_imports.py`:

```
== test_web_viewer_capture: SKIPPED [1] tests/test_web_viewer_capture.py:343: set MACHINOME_WEB_SNAPSHOT_E2E=1 to photograph through the installed viewer
22 passed, 1 skipped, 2 subtests passed in 1.94s
== test_backend_neutral_materialization: 12 passed, 8 subtests passed in 3.11s
== test_brep_geometry: 65 passed in 3.28s
== test_build_lock: 16 passed in 10.22s
== test_build_publication: 13 passed, 1 warning, 2 subtests passed in 3.41s
== test_builder_lifecycle: 35 passed, 7 subtests passed in 1.13s
== test_builder_reload_resilience: 9 passed in 4.21s
== test_clocked_identity: 9 passed in 1.53s
== test_clocked_publication: 12 passed in 2.13s
== test_clocked_time: 46 passed, 20 subtests passed in 2.13s
== test_content_verified_currency: 28 passed, 4 subtests passed in 4.91s
== test_declarative_cli: 18 passed in 0.92s
== test_document_drivers: 22 passed, 3 warnings in 3.79s
== test_export: 30 passed, 1 warning, 5 subtests passed in 16.52s
== test_expression_bindings: 22 passed, 6 warnings in 9.93s
== test_expression_graphs: 15 passed, 24 subtests passed in 5.62s
== test_flexible_document: 20 passed, 2 warnings in 5.49s
== test_lazy_test_framework: 36 passed, 76 subtests passed in 30.79s
== test_markings: 109 passed, 4 warnings, 56 subtests passed in 14.89s
== test_molejo_adapter: 46 passed, 2 warnings in 9.25s
== test_named_models: 35 passed, 4 subtests passed in 3.51s
== test_persistent_piece_facts: 17 passed, 8 subtests passed in 3.10s
== test_pieces: 17 passed in 3.08s
== test_retained_builder_generation: 17 passed, 5 subtests passed in 36.68s
== test_running_document: 110 passed, 2 warnings, 93 subtests passed in 6.13s
== test_scad_presentation: 24 passed, 4 warnings, 25 subtests passed in 112.80s (0:01:52)
== test_source_generation: 14 passed in 2.82s
== test_state_color: 16 passed, 32 subtests passed in 1.53s
== test_time_base: 51 passed, 7 subtests passed in 2.18s
== test_witness_touching_pair: 7 passed, 21 subtests passed in 2.32s
== test_manager_develop: FAILED tests/test_manager_develop.py::ExplicitViewerTest::test_the_viewer_flag_names_the_viewer
FAILED tests/test_manager_develop.py::ExplicitViewerTest::test_web_dev_serves_the_page_directly_and_says_so
FAILED tests/test_manager_develop.py::ViewerSessionLifecycleTest::test_callback_is_passed_to_the_builder
FAILED tests/test_manager_develop.py::ViewerSessionLifecycleTest::test_each_rebuild_reloads_the_open_pages_in_place
FAILED tests/test_manager_develop.py::ViewerSessionLifecycleTest::test_first_builder_invocation_is_not_flagged_as_reload
FAILED tests/test_manager_develop.py::ViewerSessionLifecycleTest::test_first_run_failure_stops_the_session_and_exits
FAILED tests/test_manager_develop.py::ViewerSessionLifecycleTest::test_second_builder_invocation_is_flagged_as_reload
9 failed, 20 passed in 0.94s
== test_cli: 18 passed, 10 subtests passed in 0.87s
== test_build_defaults: 4 passed, 2 warnings in 0.95s
== test_build_subprocess_isolation: 3 passed, 2 subtests passed in 3.85s
== test_cli_lazy_imports: 25 passed, 46 subtests passed in 6.87s
```

The one failure was `test_manager_develop.py`, 9 tests: its harness serves a fake build directory `/work/project/_build`, and the new publication watch creates the directory it watches (`PermissionError: [Errno 13] Permission denied: '/work'`). The harness now patches `machinome.manager.develop.watch_publication` beside `get_build_dir` and `Process`, and `test_each_rebuild_reloads_the_open_pages_in_place` asserts the watch is started once with `(BUILD_DIR, session)` and stopped with the session: `29 passed`. The skip in `test_web_viewer_capture.py` is its existing opt-in (`set MACHINOME_WEB_SNAPSHOT_E2E=1 to photograph through the installed viewer`).

The Studio's tests that read the API skill, run alone from `packages/machinome-studio` after task 6.3: `test_scoped_tools` 23 passed, `test_runtime_profiles` 14, `test_state_color_contract` 1, `test_frame_precision_contract` 1, `test_documentation` 23.

## The mutation sweep (task 5.1)

Each mutation applied alone by a script that replaces one exact text, runs the named tests, and writes the file back, its SHA-256 compared equal afterwards (`restored byte-equal` after every one).

| mutation | tests run | result |
| --- | --- | --- |
| the form check removed (`NodeMeta` no longer calls `_validate_app`) | D1 | **red**: six `TypeError not raised` |
| the path resolved against the root's own file (`inspect.getfile(type(root))`) | D2 | **red**: `…/app_project/derived/app/index.tsx != …/app_project/app/index.tsx` |
| the sweep not sparing the app | P1, P2 | **red**: the script named is not in the build directory |
| the record written as `null` for a root with no app | P4 | **red**: `'app' unexpectedly found` |
| a refusal written to `errors.json`, placed where the app is published, before the document | R1 | **not red**: the publication's own `clear_errors` removes the file before the document is written, so the mutation cancelled itself |
| the same, placed after the document is published | R1 | **red**: `errors.json` exists |
| the watch of the inputs not scheduled | W1, W1 through a link | **red**: the app edit was not republished |
| the export bundling after `os.makedirs(output_dir)` | E2 | **red**: the output directory exists |
| an app event returning `SOURCE_CHANGED` instead of republishing in place | W1, W1 through a link, X2 | **red**: W1 not republished (the in-thread builder exits, so the count of `load_node` is not reached), X2 `2 != 1` builder `START`s |
| the byte comparison removed | W3 | **red**: the builder kept watching (`True is not false`) |
| the publication watch removed (`watch_publication` schedules nothing) | W5, X2 | **red**: W5 never counts a reload; X2's Python half reads four stale documents; X2's app half times out waiting for the edited text |
| the containment check removed from the core | R2 | **red**: `BuildOutcome.FAILED != CURRENT` (the patched seam was asked, so the core's sentence did not answer) |
| containment judged on the unresolved entry | W1 through a link | **not red** |
| both resolutions dropped: `declared_app` without `realpath` of the declaring file, and containment on the unresolved entry | W1 through a link | **not red** |

**Mutations nothing caught:** the last two. The symbolic-link test stays green with every path resolution in `core/app.py` removed, because the loader already imports a project reached through a link by its real path (`resolve_node` → `import_module_from_path` resolves the file and its project root), so the declaring class's file is real before `declared_app` reads it and the viewer answers real inputs. The test proves the end-to-end behaviour the coordinator asked for (it is red when the inputs are not watched, and when an app event rebuilds), but no resolution in `core/app.py` is load-bearing for it. The first `errors.json` placement is a mutation that could not survive the code it was put in, not a gap in R1.

## Gate

- **The whole framework suite**, one process, from `packages/machinome`
  (`pytest tests -q -rfEs`): **1 failed, 5102 passed, 9 skipped, 55
  warnings, 13516 subtests passed in 737.03 s.**
  - The failure is `tests/test_profile_documentation.py::ProfileDocumentationTest::test_released_status_changelog_and_history`:
    `'current source' unexpectedly found` in `docs/project/status.rst`,
    whose heading "Current source after this release" was written by the
    base commit `60e8efe0` (`feat: select existing body colors from model
    state`). This change does not touch `status.rst` (`git diff HEAD` of it
    is empty), and the history's "Unreleased" section, where this change's
    bullet is, holds neither phrase the test refuses. It fails on the base
    in the same way; it is not this change's, and is not fixed here.
  - The skips, each with its reason: 4 × `tests/freecad_support.py:21`
    (`MACHINOME_FREECAD_ROOT is not set: the FreeCAD node package's tests
    need an extracted FreeCAD 1.1.4 runtime`); `test_connectivity.py:314`
    (`the repairing split needs networkx, which machinome does not
    install`); `test_jscad_integration.py:25` (`jscad CLI is not
    installed`); 2 × `test_step_assembly.py` 426, 546
    (`Internal-Cycloidal-Actuator vendor STEP not present`);
    `test_web_viewer_capture.py:343` (`set MACHINOME_WEB_SNAPSHOT_E2E=1 to
    photograph through the installed viewer`). None is in this change's
    tests: `tests/test_model_app.py` ran 27 tests with no skip.
- `openspec validate declare-a-models-app --strict` (from
  `packages/machinome`): `Change 'declare-a-models-app' is valid`.
- Documentation tests (task 6.1), each alone: `test_docs_structure.py` 39
  passed, 6569 subtests; `test_manual_extras.py` 16 passed;
  `test_viewer_documentation_links.py` 15 passed; `test_release_records.py`
  21 passed. The manual's build: see "Not verified" for the theme; with the
  stock theme and `-n`, exit 0 and no warning.

## Departures from the design

None changes a requirement, a ruling or a Decision's outcome. Each is a
detail the design left open, or a choice made in the implementation.

1. **The changelog is `HISTORY.rst`.** Task 6.2 names it; the framework
   package has no `CHANGELOG.md`. `packages/machinome/HISTORY.rst` is a link
   to the repository root's `HISTORY.rst`, inside the bench, where the
   bullet was written under "Unreleased".
2. **The refusal sentences.** Decision 6's table gives the tail after
   `<Class>.app = '<path>'`. The first two rows read as the table:
   `… names <path>, which does not exist` and `… names <real path>, which is
   outside the project at <root>; an app's files are the project's own`.
   For the seam's and the viewer's sentences the connector is
   `… cannot be bundled: <sentence>`.
3. **What needs the bundle, as the seam's refusal names it:** `the build`
   for a build (the sentence Decision 2 quotes), `machinome export` for an
   export.
4. **Which refusals watch the declared file's directory.** Decision 5a
   names "a syntax error, a missing file". The directory (the nearest
   existing one) is watched where the file is missing or the viewer refused
   to bundle; not where the file lies outside the project or the viewer is
   absent or does not bundle, which no edit of the app's files repairs (a
   Python edit, or an install, rebuilds as before).
5. **A settle of 0.1 s** (`APP_SETTLE`) before an app event republishes, so
   one save writing several files is one republication and a model source
   in the same burst makes it a model change, as Decision 5a asks.
6. **The export checks early.** The entry's existence and containment and
   the bundling viewer are judged at the top of `export_node`, beside the
   embedding viewer, before `clear_keyframe` and the build; the bundling
   itself runs after `build_stls` into a temporary directory, as designed.
   The body of the export's write loop moved, unchanged but for the app's
   copies and record, into a helper `_write_export`.
7. **A malformed `[tool.machinome] viewer`** met while resolving the
   bundling viewer (`ProjectManifestError`) is a refusal too, recorded like
   the seam's others, rather than failing the publication.
8. **The fixture.** `inherited.py` is `tests/app_project/derived/inherited.py`
   (with `derived/__init__.py`): in the same directory the root's file and
   the declaring class's give the same path, and D2 could not tell them
   apart (the mutation sweep shows it does now). Every fixture module
   imports `Calculator` from `tests.clocked_project.calculator`, as task 2.1
   says; a temporary copy carries only `app_project/` and a manifest, and
   `../../outside-app.tsx` is created beside the copy.
9. **X2 is two tests**, each with its own `machinome develop`: the app half,
   and the Python half, so the Python half's red on the base could be shown
   on its own (the app half fails first there).
10. **Tests beyond Decision 10's list:** D1's accepted forms and three more
    refused forms (`''`, `C:/x.tsx`, `app\x.tsx`); D2 for an app declared on
    a child (the spec's scenario); W1 through a symbolically linked project
    (asked by the coordinator: the originating project is reached through
    `projects` → `/mnt/data/...`, and the viewer answers real paths); E2 for
    a missing file (the export spec's scenario); E3 at `export_node` as well
    as through the command.
11. **Existing tests changed:** `tests/test_viewer_seam.py`'s pins
    (`OPERATIONS`, `DEFAULTS`, the Protocols' members, the web viewer's
    operations, the operation-to-members map, the default rule), the first
    two of which already failed against the companion's provider; and
    `tests/test_manager_develop.py`'s harness (above).
12. **The Studio.** Its `workflow/warts.md` did not exist and was created;
    the sentence of its `workflow/README.md` saying it had no such log was
    changed to name it. No Studio changelog bullet was written (task 6.3
    asks for the skill and the warts entry only).
13. **The in-place republish** takes the build lock, compares the bytes,
    bundles, re-schedules the watch, writes, sweeps and notifies as
    Decision 5a says, and logs `The app was republished`; it does not clear
    `errors.json`, which the builder's own publication already cleared.
14. **The publication watch** reacts to the rename `atomic_write` makes
    (`on_moved`, destination `viewer.json`) and to nothing else; a
    `viewer.json` written in place by some other writer would not be
    announced.

## Not verified

- The Studio: nothing was run there; that it shows the app through
  `machinome build` is the design's reading (Decision 9), not observed.
- The originating project: `projects/enigma-i` was not opened, as task 1.2
  says; its model, its 3,347 parts and an app over them were not built.
- The manual's build with its own theme and `-W`: `sphinx_rtd_theme` is not
  installed in the bench venv. Built instead with
  `-b html -n --keep-going -E -D html_theme=alabaster`: exit 0, **no
  warning**; the changed pages read back from the built HTML.
- An editor that saves by writing a new file and renaming it over the old
  one: the app's inputs are watched as files, as the model's sources are,
  and such a save was not tried.
- A project declaring `viewer = "openscad"` with an app (refused by the
  seam naming the key, by reading), `--viewer` passed to `develop` reaching
  the bundling choice, and an installed (wheel) viewer's refusal reaching
  the document: not tested here (the last is the companion's U6, on the
  viewer's side).
- What remains of the reload timing (`workflow/warts.md`): a build error's
  `errors.json` still announced before it is written, by reading; not
  observed.

## Decision record (task 6.6)

The reviewer decided the implementation confirms the design. Written under
`docs/adrs/BUILD/`, with their lines in `docs/adrs/README.md`:

- ADR-198, "A model's app is declared on its root and bundled by the viewer
  beside every document" (Decisions 1-4, 7, 8, 11; departures 2, 3, 6);
  amends ADR-194.
- ADR-199, "An app that cannot be bundled is a recorded refusal, and an
  export refuses it" (Decisions 6-8 and the rulings; departures 4, 7).
- ADR-200, "A watching builder republishes an edited app in place, and
  `develop` tells open pages when the document is published" (Decision 5;
  departures 5, 14), recording two limits as known and not covered: an app
  file watched by its own path may stop being followed after an editor's
  rename-save (unverified), and the publication watch sees only
  `atomic_write`'s rename.
- ADR-194: its status line and a dated "Amendment (2026-11-22)" section
  point to ADR-198; its index line reads "amended by 198".

The three ADRs link the change at `openspec/changes/declare-a-models-app/`;
archiving it (task 6.7) moves it, and their `Change:` links follow it then.

## Validation in the originating project (reviewer, 2026-11-22)

The Enigma I (`projects/enigma-i`) declares `app = 'app/index.tsx'` on
`simulation.machine:Enigma`, with its app's sources in `simulation/app/`
(a keyboard, a case box and a rotor box). `machinome develop` from this
bench published `viewer.json` naming `app-7d76c11850b80d04.js` and
`app-1e954f201c034528.css`, and a headless Chromium on the served page
showed the app in place of the automatic panel, beside the assembly
sidebar: 37 controls, no clocked panel, no refusal. Pressing Q left only
"Release Q" and the case controls enabled and stepped the right wheel from
04 to 05; releasing restored the keyboard; "Open hood" enabled "Take rotors
out". The project is reached through a symbolic link, as the symlinked
project test covers. Screenshots after the press timed out under software
rendering in the headless browser; the state was read from the page.

The reviewer planted three faults of his own after the applier's sweep
(the app's files swept as unreferenced, the refused app's directory not
watched, the stale-publication check skipped); P1, W2 and W3 turned red.
