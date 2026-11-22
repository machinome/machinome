# Evidence: show-a-models-own-app

Recorded by the applying agent on 22 November 2026 in the framework worktree
`machinome/WTs/model-apps`, branch `model-apps`, planning commit `c7611f09`
above base `50bdffdf`. Tasks 8.4 (the decision record) and 8.5 (sync,
archive, commit) are the reviewer's and are not recorded here; nothing is
committed.

## The bench (tasks 1.2 and 1.3)

- `git status --short` was empty; `git rev-list --count 50bdffdf..HEAD` is 1
  (`c7611f09 plan: a model's own app in place of the automatic panel`).
- `openspec validate show-a-models-own-app --strict` (from
  `packages/machinome-viewer`): `Change 'show-a-models-own-app' is valid`;
  `openspec validate declare-a-models-app --strict` (from
  `packages/machinome`): `Change 'declare-a-models-app' is valid`.
- `node_modules` at the worktree root is a real directory, not a link
  (`test -d … && ! test -L …` held).
- Tools: Node 24.11.1, esbuild 0.24.2, vitest 3 with jsdom 29.1.1 (the
  bench's `node_modules`), Playwright with Chromium on the bench's `.venv`,
  Pygments 2.21.0 and Sphinx 9.1.0 on the same venv.
- The two `npm install` commands of task 1.3, run from the worktree root,
  added 3 packages and then the type packages. `widget/package.json` gained
  exactly `react` 19.3.0 and `react-dom` 19.3.0 under `dependencies` and
  `@types/react` 19.3.0 and `@types/react-dom` 19.3.0 under
  `devDependencies`. `package-lock.json` gained six entries and lost no line
  (`git diff package-lock.json | grep -c '^-[^-]'` is 0): `react`,
  `react-dom`, `scheduler` 0.28.0, `@types/react`, `@types/react-dom` and
  `csstype` 3.2.4, the last one the dependency of `@types/react` (a dev
  package; the task named `scheduler` only).
- **Where npm put React: nested under the widget**, not at the root:
  `require.resolve('react/package.json', {paths: [widget]})` answers
  `packages/machinome-viewer/machinome/viewer/web/widget/node_modules/react/package.json`,
  and `react-dom` likewise. The root `node_modules` holds no React.

## Red on the base (tasks 2.1 to 2.5)

Every test file below was written and run alone before any source change.

### `src/machine-change.test.ts` (2.1)

`vitest run src/machine-change.test.ts`: **11 failed of 11**, each with
`Error: the handle has no onMachineChange member` (the member is read through
the handle's namespace, so the file loads). M7 does not pass vacuously, as
the task allowed it might: its subscription goes through the same helper,
which throws on the absent member.

### `src/app.test.ts` (2.2)

`vitest run src/app.test.ts`: **25 failed, 2 passed of 27**. A1 to A5, A7
and A8 fail at their assertions (no app started: `expected [] to deeply equal
[ 'app' ]`; no notice; `promise resolved "{ apiVersion: 30, … }" instead of
rejecting` for every malformed record). A9 passes, as the task says. **A6
has two tests**: the first, "driverControls none fetches nothing of the app
and builds no viewport", passes on the base vacuously (the base never loads
an app at all); the second, added because Decision 1 says the record is
validated under `'none'` too, fails on the base (the malformed record is
accepted). The mutation sweep (6.2) shows the first one biting.

### `app/app.test.tsx` (2.3)

`vitest run app/app.test.tsx`: the file fails to load at
`Failed to resolve import "./index" from "app/app.test.tsx"`, after
`import { useState } from 'react'` and `import { flushSync } from
'react-dom'` resolved: the failure is the missing helper, not React.

### The fixture (2.4)

`tests/fixtures/calculator-app/`: `app/index.tsx`, `app/Readout.tsx`,
`app/app.css`, `app/broken.tsx`, `app/imports-three.tsx` and `README.md`,
each with the package's licence header (the README's in an HTML comment).

### `tests/test_app_bundle.py` and `tests/test_model_app.py` (2.5)

The viewer bundle built from the base source (`npm run build`):
**SHA-256 `13706c2b36206de89fdc2651465396e438d38ab26fd6f4107af62aaa8b1c07e8`**
(920.0 kB).

- `test_app_bundle.py`: **12 failed, 1 passed**. U1 to U5, U7 and U8 at
  `AttributeError: module 'machinome.viewer.web' has no attribute
  'bundle_app'`; U6 at `ModuleNotFoundError: No module named
  'machinome.viewer.web.app'` (two) and `FileNotFoundError: …/widget/app-build.mjs`
  (one); U10 at `'bundle' not found in frozenset({'embed', 'capture',
  'serve', 'present'})`. U9 passes: the base bundle carries no React.
- `test_model_app.py`: **6 failed**, B1 to B6 (six tests: B1 and B2 run
  together on the export page and on the development page), each in `setUp`
  at the same missing `bundle_app`.
- **A browser-level red as well**, recorded after task 5.3 gave the bundler:
  the base bundle above was copied back into `dist/` and `test_model_app.py`
  run against it (607 s). B1/B2 (both pages), B3 and B6 time out waiting for
  `.calculator-app .calculator-app-key`, and B4 for `.machinome-app-refusal`:
  the base viewer ignores the `app` record and builds its panel. **B5's
  browser assertions passed on the base**, as they must (the base requests
  no app under any option): B5 is red on the base only through the missing
  bundler, and the mutation sweep shows it biting. That run also showed a
  defect of the test file itself, a teardown error (`Event loop is closed!
  Is Playwright already stopped?`) on every test, because the browser was
  closed in a cleanup that ran after Playwright had stopped; the tests now
  close it inside the Playwright context (`_Browser.browsing`). The
  implementation bundle was then rebuilt from source and checked equal to
  the one recorded below.

## Green (tasks 3.1 to 5.5)

- 3.1: `tsc --noEmit` clean; `src/machine-change.test.ts` **11 passed**.
  `src/follow-the-slider.test.ts` (55) and `src/draw-on-change.test.ts` (62)
  run alone afterwards: green.
- 4.3: `tsc --noEmit` clean; `src/app.test.ts` **27 passed**;
  `src/machine-change.test.ts` 11 passed; `src/fullscreen.test.ts` 31 passed.
- 5.1: `npm run typecheck:app` clean; `app/app.test.tsx` **9 passed**.
- 5.3: `tests/test_app_bundle.py` **13 passed**, no skip (Node.js and the
  dependencies are present).
- **Bundling times (5.3)**: ten bundlings of the fixture app into ten fresh
  output directories, each timed around `bundle_app` (Node's start,
  esbuild, the writes): 0.173, 0.179, 0.185, 0.163, 0.185, 0.174, 0.182,
  0.183, 0.192, 0.160 s; **median 0.18 s, spread 0.16 to 0.19 s**. The script
  is 227,346 bytes and the stylesheet 388 bytes; the design estimated about
  150 kB for the script.
- 5.4: a wheel built with `python -m build --wheel --no-isolation` from a
  scratch copy of the package (links dereferenced, `node_modules` left out,
  modification times kept, so the frontend hook found the bundle current;
  run with `node` and `npm` off the `PATH`, so no install could have run;
  none did). The wheel's 23 files hold, under `widget/`, `develop.html`,
  `index.html`, `package.json`, `dist/machinome-viewer.js` and
  `tools/expression-pressure.ts` (the last already shipped before this
  change); `widget/app/`, `widget/app-build.mjs`, `widget/tsconfig.app.json`
  and `widget/src/` are absent; `machinome/viewer/web/app.py` is present, so
  an installed copy answers the first refusal of Decision 11. The copy was
  used so that the build wrote nothing (`build/`, the egg-info) into the
  bench.
- 5.5: `machinomeViewerApi` is 31. Pins updated from 30 to 31:
  `src/version.test.ts` (the test now reads "declares a model's own app as
  API 31", with a line recording what 30 declared), `tests/test_bundle.py`,
  `test_asset_load_order.py`, `test_calculator_document.py` (three),
  `test_carriage_document.py`, `test_clearing_document.py`,
  `test_curta_drawing.py` (two), `test_lock_document.py`,
  `test_profile_document.py`, `test_regulator_document.py`,
  `test_running_document.py`, `test_source_timing_browser.py` and
  `test_documentation.py`'s `machinomeViewerApi == 31`. Nothing else in them
  changed. Three more pins were found by the gate (7.1) and updated there. The manual's `conf.py` `source_viewer_api` became `'31'`, which
  `test_documentation.py` holds to the widget's number.

## The browser path (6.1)

The implementation bundle (`npm run build`): **SHA-256
`fbe1fd412abcd098130cdfae901781f0a492459b9e5ce0a5ca915ea2e6f7098f`**
(926.2 kB, `viewer API 31` in its banner, no occurrence of `react`).

- `tests/test_model_app.py`: **6 passed** in 16 s (9 deprecation warnings
  from the development server's own dependencies, `multipart` and
  `websockets.legacy`).
- `tests/test_calculator_document.py`: 16 passed.
- `tests/test_follow_the_slider.py`: 5 passed, **1 skipped**: "Playwright's
  firefox is not installed at the revision it expects
  (`…/firefox-1543/firefox/firefox` is absent)".
- `tests/test_draw_on_change.py`: 5 passed.
- `tests/test_licence.py`: 6 passed. It scans tracked files only, so the new
  files were checked by hand with the same pattern: every new source,
  test and fixture file states exactly the set's grant. Two would have
  failed the scan once tracked and were corrected: `app-build.mjs`'s banner
  (a string literal ending `…2.0+\n'`, read by the pattern as part of the
  identifier; now a template literal, as `build.mjs` writes it) and
  `test_app_bundle.py`'s expectation (an f-string; now spelled in two
  pieces).

## Mutations (6.2)

Each applied alone by an exact text replacement, the named tests run, the
file restored byte for byte (SHA-256 compared) and, where the bundle was
rebuilt for a browser test, rebuilt again from the restored source and
checked equal to `fbe1fd41…`.

| Mutation | Tests | Result |
| --- | --- | --- |
| no notification after a drawing's last frame | M2 | red (1 of 2: the trigger test; the "later gesture lands" test stays green, as it should) |
| a notification for a refused request (`machineOperation` marks on a throw) | M3 | red |
| the subscription on the machine (a new notifier each `startMachine`) | M5 | red (both) |
| the panel built when an app is refused (at the start's settlement) | A4 | red, 7 of 8; the case "refuses after it started" stays green because this mutation rebuilds the panel only when the start settles |
| the app loaded under `driverControls: 'none'` | A6, B5 | red, red (`expected [ './app.css', './app.js' ] to deeply equal []`; B5 `result['app']` True) |
| the canvas left in the container | A2, B3 | red, red (B3: the canvas is not inside the app's picture) |
| a changed record on `manifestChanged` keeping the old app | A7, B6 | red, red (B6 times out waiting for the edited label) |
| the snapshot rebuilt on every `getSnapshot` | H1 | red |
| the containment check removed | U4 | red (`ViewerError not raised`) |
| `minify` off | U7 | **red**: unminified, the two copies bundle to different names (`app-c9da…js` against `app-75bb…js`): esbuild's unminified output names modules by their paths, so minifying is what keeps the bytes path-free |
| the `react` entry removed from what the bundler provides | U1, U7, U8, B1/B2 | **nothing red** (see below) |

**The mutation that turned nothing red.** Removing `'react'` from the
specifiers the bundler resolves to the widget's files changed no output:
the fixture's own files never import `react` by name (JSX imports
`react/jsx-runtime`, still provided), and the files that do, the helper and
React DOM, are the widget's own, whose bare imports resolve by default from
the widget, to the same copy. This checkout holds no second React an app
could reach (React is nested under the widget; the other copies are nested
under the movie and the Studio frontend), so the mutation cannot produce two
copies here. Not worked around. A test that would bite: an app whose own
file imports `useState` from `react` (the mutation then refuses the import by
name), and a project carrying its own `node_modules/react` (the mutation,
had it let the import through, would bundle that copy).

## Gate (7.1)

Run one at a time, after the mutation sweep, on the implementation bundle
`fbe1fd41…` (its SHA-256 checked unchanged after the sweep).

- `vitest run` (the whole widget suite, from the widget directory):
  **80 files passed, 1 skipped; 2,186 tests passed, 2 skipped**. The two
  skips are the suite's own, gated on a document this bench lacks:
  `src/run/profile-contact.test.ts:306` (`it.skipIf(!actualCurtaDocument)`)
  and `src/run/profile-installed-benchmark.test.ts:78` (`it.skipIf(!path)`,
  the installed Curta version-13 build).
- `tsc --noEmit`: clean. `npm run typecheck:app`: clean.
- `python -m pytest tests -rs` (from `packages/machinome-viewer`): the first
  run had **3 failures**, all pins my task-5.5 search had missed because they
  were not spelled beside `apiVersion` or `machinomeViewerApi`:
  `test_asset_load_order.py:294` (`assertEqual(mounted, 30)`),
  `test_widget_e2e.py:253` (`assertEqual(result['bundle'], 30)`) and
  `test_machinome_identity.py:55` (the provider's `OPERATIONS` pinned
  without `bundle`). Updated to 31 and to the set with `bundle`, nothing
  else; the three files then passed alone (8, 4 and 66). The rerun of the
  whole suite: **324 passed, 3 skipped**, 247 subtests passed, 345 s. The
  skips: `test_curta_drawing.py:375` and `:469`, "the Curta's own builds are
  not at …/WTs/projects/Calculators/Curta-Type-I-3x/_build" (a project
  build outside this worktree, not opened), and `test_follow_the_slider.py:380`,
  "Playwright's firefox is not installed at the revision it expects". No
  browser test was skipped for a missing Chromium. The 77 warnings are
  deprecation warnings of third-party libraries (`multipart`,
  `websockets.legacy`) and of the suite's existing tests.

## The manual and the record (8.1, 8.2)

Red first: `packages/machinome-viewer/tests/test_documentation.py` gained
the two new pages in `PAGES` and the test `test_a_models_app_is_documented`
(the `user-documentation` delta's two scenarios and the facts the delta
names); `packages/machinome/tests/test_docs_structure.py`'s pinned viewer
toctree gained `app`, and its how-to list `howto/give-a-model-its-app`. On
the text before the pages: the viewer file **5 failed, 9 passed** (the
missing pages, and `source_viewer_api` 30 against the widget's 31); the
framework's structure test failed both subtests for the missing entries.

Written: `reference/viewer/app.rst` (new: where an app is shown, the four
names, the refusals, the contract a bundle speaks), `viewer-handle.rst`
(`onMachineChange`), `clocked.rst` (`drawing()`), `mount.rst`
(`driverControls` gates the app), `layouts.rst` (the inspector's rail and
sidebar beside an app), `compatibility.rst` (API 31, additive record),
`troubleshooting.rst` (a section with the reader's notices and the
bundling's refusals, anchored `viewer-app-refusals`),
`howto/browser-viewer.rst` and `howto/embed-the-viewer.rst` (one fact
each), and `howto/give-a-model-its-app.rst`, created here with the viewer's
half. **The framework's half is marked in the page's source** by RST
comments, invisible in the built page: one under the title describing what
the companion's task 6.1 adds, and `FRAMEWORK HALF` comments under the
sections "Declare the app" (left empty) and "Where the app appears"
(holding only the viewer's own sentences). The how-to is in the How-to
guides toctree after `howto/embed-the-viewer`, `app` in the viewer section's
toctree after `clocked`.

Green, each run alone on the bench's venv:
`packages/machinome-viewer/tests/test_documentation.py` **14 passed**;
`packages/machinome/tests/test_docs_structure.py` **39 passed** (6,569
subtests); `test_viewer_documentation_links.py` **15 passed**;
`test_manual_extras.py` **16 passed** (41 subtests). A strict build,
`python -m sphinx -b html -n -W --keep-going -D html_theme=alabaster docs
<scratch>`, exits 0 (the bench's venv has no `sphinx_rtd_theme`, so the
default theme was named; the theme draws no RST). Its first run warned once,
a `tsx` lexing failure on a TypeScript generic in a snippet with no JSX;
that block is now `typescript`.

The CHANGELOG bullet is the first under "Unreleased" in
`packages/machinome-viewer/CHANGELOG.md`.

## Departures and details settled in the implementation

None changes a requirement or a ruling. Each is a detail the design left
open or an implementation choice:

1. **How one notification per operation is made** (Decision 6). Every door
   that can change the bank or a drawing runs inside `machineOperation`,
   which nests; the pose hook marks an accepted pose that moved an id, and
   the drawing is marked where it is set (`startDrawing`) and cleared
   (`landDrawing`, `drawingFrame`'s last frame); the outermost operation
   notifies once at its end, after its panel is written. The frame loop's
   clock frame, drawing frame and slider frame are one operation, so a frame
   notifies at most once. An accepted request that moves nothing (a
   zero-travel stop, a restore to the bank standing) notifies nobody, since
   it changes neither fact.
2. **A republish that removes the machine notifies too** (`hadMachine ||
   machine !== undefined`): Decision 6 lists "builds, rebuilds or keeps";
   a page reading `machine()` after a removal reads null, which is what the
   notification exists to say. A document that never had a machine still
   never notifies.
3. **The loader's seam** is `mountAppWith(attach, request)`, `attach` being
   how an element is put in the document; `app.test.ts` mocks `./app`'s
   `mountApp` with a fake `attach` that plays the browser's events.
4. **"(<status or error>)"**: a script's `error` event carries no status, so
   after a failed load the loader fetches the file once more to name the
   HTTP status, or the fetch's own error where there is none (a `file:`
   page).
5. **The record's validation** also refuses an unknown key, a backslash and
   a stylesheet beside a refusal (Decision 3 says "anything else refuses";
   these are its instances), with sentences beginning `<url>: the
   document's `app` record …`.
6. **Two sentences the design did not spell**: a render error refuses with
   `it failed as it rendered: <message>`, and `usePlay()` on a model that is
   not clocked with `this model is not a clocked machine; usePlay() plays a
   clocked machine's instructions` (Decision 7 says "the same refusal as
   useMachine"; the second half names the hook). A refusal the helper states
   itself (`AppRefusal`) reaches the viewer verbatim; any other render
   error is prefixed. `start` forwards only the first refusal, so an app
   failing to render is not refused a second time for its missing
   `<Viewport/>`.
7. **A third helper file**, `app/host.tsx`, holds what `index.tsx` and
   `start.tsx` share and an app does not import (the host type, the context,
   `AppRefusal`, the error boundary), so the public module exports only the
   four names and their types.
8. **One React through the import plugin.** The five specifiers are resolved
   to the files the widget resolves them to by the plugin's `onResolve`,
   which also refuses every other bare import; esbuild's `alias` option is
   not used. The effect is Decision 11's.
9. **The bundler writes its own empty `tsconfig.json`** in its temporary
   directory and names it, so neither a project's tsconfig nor the
   widget's can change how an app compiles. The banner is laid out on
   several lines, with the same statements.
10. **`app.py`** takes the widget directory as a parameter (for U6), and
    imports `packaging.workspace_root` only when it names the install root
    in a refusal, because `packaging` imports setuptools; without it the
    refusal names the widget directory.
11. **`tsconfig.app.json`** includes `src/molejo.d.ts` beside `app/`: the
    helper's type-only imports from `../src/viewer` bring the viewer's
    sources into its check, and their ambient declaration with them.
12. **`vitest.config.ts`** gains `esbuild: { jsx: 'automatic' }` so the
    helper's test compiles JSX as the bundler does. It is not a bundle input.
13. **The viewport stays once made.** When a republish removes the record
    the app is taken away and the panel built, and the viewport stays in
    the container, filling it, with the canvas inside (Decision 4: "when no
    app is shown … the viewport, if it exists, is placed back in the
    container"); the corner control stays anchored on it. A document that
    never named an app never makes one (A9).
14. **B6's stylesheet**: editing `Readout.tsx` alone leaves the stylesheet's
    bytes, and therefore its name, unchanged, so the test checks that the
    previous app's `<link>` element is no longer connected and exactly one
    app stylesheet stands, rather than a changed name.
15. **A6** carries a second test, for the record's validation under
    `'none'` (see the red record above).

## The decision record (8.4)

The reviewer decided that the implementation confirms the design. Written
under `workflow/adrs/EXPORT/`, with their lines in `workflow/adrs/README.md`:
ADR-084 (a model's app is a script the viewer starts inside `mount()`),
ADR-085 (the clocked machine's notification on the mount handle) and ADR-086
(the viewer bundles a model's app with its own toolchain). They record, as
decided: the notification on a republish that removes the machine; the one
React enforced by the bundler's import plugin; the bundle path-free only
because it is minified; the record's refusal of unknown keys, backslashes
and a stylesheet beside a refusal; the viewport staying once made; and this
release's limit (the toolchain only in a source checkout, an installed
viewer refusing). Their `Change` links name the change directory as it
stands; 8.5's archive moves it.
