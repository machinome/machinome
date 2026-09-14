## 0. Before anything else

- [ ] 0.1 Confirm the worktree: `git rev-parse --show-toplevel` names
      `solid-node-viewer/WTs/viewer-navigator` and the branch is
      `viewer-navigator`. Record the head this change starts from
      (`2b0de85` plus this change's own planning commit).
- [ ] 0.2 Record the baseline in `evidence.md`: `npm run typecheck`,
      `npm test`, `npm run build` in `solid_node_viewer/widget`, and
      `PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python
      -m pytest` at the repository root — counts, bundle size in bytes,
      and what it skips and why (`tests/test_server.py:146-147`, the CRA
      app not built, is the skip this change is about to delete).

## 1. The layout, in a DOM vitest can hold

Design D1-D7. The seam of design D15 is what makes this testable without
WebGL: `inspector.ts` exports `mountInspector`, which calls an internal
`mountInspectorWith(mount, mountNavigator, target, sourceUrl, options)`;
the test calls the internal one with stubs, and nothing but `widget.ts`
sees the public one.

- [ ] 1.1 **Red** — `src/inspector.test.ts`, opening with
      `/** @vitest-environment jsdom */` (cycle 2's pragma, no
      `vitest.config.ts` change). Against a **stub `mount`** resolving to
      a stub `ViewerHandle` and a **stub `mountNavigator`** recording its
      target, viewer and options:
      - the target's only child is the layout root; it holds a rail with
        the toggle, a sidebar element, and a viewer pane; the stub `mount`
        was called with the **viewer pane** and the source URL, never with
        the target (design D5).
      - the toggle carries `aria-expanded="false"`, an `aria-controls`
        naming the sidebar's `id`, and the accessible name `Assembly`; the
        sidebar is `hidden` (design D5, D6).
      - `sidebar: 'open'` mounts with the sidebar shown and
        `aria-expanded="true"`; the default is collapsed (design D3).
      - activating the toggle by click and by keyboard opens and closes
        the sidebar, updates `aria-expanded`, and leaves
        `document.activeElement` on the toggle across both (design D5).
      - `handle.sidebarOpen()` follows the toggle, and
        `handle.setSidebar(true|false)` does exactly what the toggle does.
      - nothing is written to `localStorage` or `sessionStorage` and
        `location` is not rewritten across a toggle (design D7).
      - the navigator is mounted into the sidebar element with
        `options.navigator` passed through untouched, and its `styles`
        defaults to the layout's (design D4).
      - the handle exposes the stub viewer handle and the stub navigator
        handle as fields (design D2).
      - `dispose()` disposes the navigator **before** the viewer (assert
        the order), empties the target, and is harmless a second time.
      - two mounts in one document inject exactly one
        `#solid-node-inspector-style`; `styles: 'none'` injects neither
        the layout's nor the navigator's; `className` reaches the viewer's
        canvas option and not the layout root (design D4, D13 of ADR-050's
        pattern).
      - a stub `mount` that rejects leaves the target empty and rejects
        with the original error (design D1).
      - a selector naming no element is refused with a message naming it.
      *Goes red at module resolution: `src/inspector.ts` does not exist.*
      Command: `cd solid_node_viewer/widget && npx vitest run src/inspector.test.ts`
- [ ] 1.2 **Green** — `src/inspector.ts`: `InspectorOptions`,
      `InspectorHandle`, `mountInspector`, `mountInspectorWith`, the
      `INSPECTOR_STYLESHEET` constant (the `solid-inspector-*` class
      contract and the `--solid-inspector-*` custom properties of design
      D6/D13, neutral defaults), and the one-per-document injection guard.
      No resize handler of any kind — the viewer's own `ResizeObserver`
      (`viewer.ts:757-769`) is the mechanism, and a task in increment 5
      proves it in a browser.
- [ ] 1.3 Confirm the rest of the suite is untouched: `npm test` reports
      the 30 existing files plus this one, and only the jsdom files
      declare the pragma (`grep -rl "vitest-environment" src/`).
- [ ] Commit: `feat(inspector): compose a navigator sidebar beside the viewer`.

## 2. The page selects a layout

Design D8. The default stays the plain viewer, which is what makes every
existing export safe.

- [ ] 2.1 **Red** — `src/widget.test.ts` (new, jsdom) over the auto-mount
      decision. Extract the decision first if `autoMount` cannot be
      reached: a pure `layoutChoice(dataset, search) -> { layout:
      'viewer' | 'inspector' | { unknown: string }, sidebar?: 'open' |
      'collapsed' }` in `src/widget.ts` or a small module, tested in the
      **node** environment for the table of design D8 — no attribute and
      no query is `viewer`; `data-solid-layout="inspector"` is
      `inspector`; `?layout=` overrides the attribute in both directions;
      `data-solid-sidebar`/`?sidebar=` likewise; an unrecognised value
      reports itself by name.
      *Goes red: the function does not exist.*
      Command: `npx vitest run src/widget.test.ts`
- [ ] 2.2 **Green** — that function, plus `widget.ts:20-42` calling it:
      `mount()` for `viewer`, `mountInspector()` for `inspector`, and for
      an unknown value `element.textContent = 'solid-widget: unknown
      layout "<value>"'` in the shape of `widget.ts:37`. Export
      `mountInspector` and its types on the global beside `mount` and
      `mountNavigator` (`widget.ts:14-18`).
- [ ] 2.3 **Red** — `tests/test_widget_e2e.py`, against the real bundle
      and the real `index.html` (rebuild the bundle first so the red is a
      missing export, not a stale file):
      - `test_the_export_page_mounts_the_inspector`: the shipped page
        shows the viewer, a collapsed sidebar and its toggle.
      - `test_the_toggle_opens_the_sidebar_and_the_canvas_narrows`: read
        the canvas width, click the toggle, assert the tree is present and
        the canvas is narrower; close it and assert the canvas is back —
        this is the ResizeObserver claim of design D6, proved in a
        browser rather than asserted in prose.
      - `test_the_query_string_opens_the_sidebar`: `?sidebar=open`.
      - `test_a_page_without_a_layout_attribute_mounts_the_plain_viewer`:
        a hand-written page carrying only `data-solid-widget` has no
        `.solid-inspector` element — the compatibility promise.
      - `test_an_unknown_layout_is_refused_by_name`.
      *Red: `SolidNodeWidget.mountInspector is not a function` / the page
      carries no attribute yet.*
      Command: `PYTHONPATH="$PWD"
      /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest
      tests/test_widget_e2e.py -q -k inspector`
- [ ] 2.4 **Green** — `widget/index.html:22` gains
      `data-solid-layout="inspector"` and nothing else; `npm run build`;
      rerun 2.3. Confirm the file's name, its `<title>`, its `<style>` and
      `data-solid-widget` are unchanged (`git diff` shows one attribute).
- [ ] Commit: `feat(export): the standalone page mounts the inspector`.

## 3. The reloader, in the bundle

Design D12. Behaviour is held identical; the table in the design is the
checklist.

- [ ] 3.1 **Red** — `src/reloader.test.ts`: `app/src/reloader.test.ts`'s
      nine cases ported to vitest (`vi.useFakeTimers`, `vi.fn`) under the
      jsdom pragma, plus one new case asserting the injected
      `#solid-node-reloader-style` appears once. Assert the banner's id,
      class **and** exact text.
      *Goes red at module resolution: `src/reloader.ts` does not exist.*
      Command: `npx vitest run src/reloader.test.ts`
- [ ] 3.2 **Green** — `src/reloader.ts`: `app/src/reloader.ts` with
      `SetErrorType` replaced by `(message: string) => void` and the
      banner rule moved from `app/src/App.css` into an injected
      stylesheet. Every constant and every branch identical; diff the two
      files and record what changed in `evidence.md`.
- [ ] Commit: `feat(reloader): carry the development reload client in the bundle`.

## 4. The development page, served

Design D9, D10, D11, D13. **This increment lands before the deletion**, so
the app is still there if the page is wrong (design risk 1).

- [ ] 4.1 **Red** — `src/develop.test.ts` (jsdom) against a stub
      `mountInspector` and a stub `fetch`:
      - `mountDevelopment('#root')` mounts the inspector on
        `/build/viewer.json` with `animation: 'inline'`, `autoplay:
        true` (`app/src/viewerShell.ts:46-48`'s two options) and
        `sidebar: 'open'` (design D10, reviewer decision); `{ sidebar:
        'collapsed' }` passed through wins, and `develop.html` forwards
        `?sidebar=collapsed`.
      - `document.title` becomes the model's name, split on capitals
        exactly as `viewerShell.ts:89-93` did — assert with the same
        `SpinnerProject` → `Spinner Project` case `viewerShell.test.ts`
        used.
      - the reloader's reload calls the inspector's
        `viewer.manifestChanged()` and **not** `reload()` (ADR-037, the
        partial update).
      - a build error shows the error pane with the message and leaves the
        inspector mounted; clearing the error removes the pane (design
        D11).
      *Red: `src/develop.ts` does not exist.*
- [ ] 4.2 **Green** — `src/develop.ts`: `mountDevelopment`,
      `DevelopmentOptions`, `DevelopmentHandle`, the error pane; exported
      on the global from `widget.ts`.
- [ ] 4.3 **Red** — `tests/test_server.py`: `test_an_unbuilt_app_is_reported_not_fatal`
      becomes `test_the_development_page_is_served_from_the_package`
      (a `FileResponse` of the page, 200, carrying the bundle route and
      `mountDevelopment`), and `DevelopmentAppBrowserTest`'s `skipTest`
      (`:146-147`) is deleted so the browser test actually runs.
      *Red: `/` still serves `app/build` or a 503.*
      Command: `PYTHONPATH="$PWD" … -m pytest tests/test_server.py -q`
- [ ] 4.4 **Green** — `solid_node_viewer/widget/develop.html` (design D10:
      the availability check, the script injection, `mountDevelopment`,
      and the page's own `<style>` for `html, body, #root`);
      `bundle.py`: `develop_page_path()` added beside `index_path()`
      (`bundle.py:30-32`); `server.py._setup_frontend_server` replaced by
      a `/` that answers that file, with a 503 naming the file if it is
      absent, and **no** `StaticFiles` mount. Rerun 4.3.
- [ ] 4.5 **Red** — `tests/test_server.py`, the claim the whole cycle
      turns on: `test_a_republished_document_updates_the_page_in_place`.
      Serve a published build, open it in Playwright, stamp the page
      (`window.__pageLoad = performance.now()` or a counter installed
      after load), rewrite `viewer.json` with a changed tree, let the
      reload socket greet or trigger the same path the greeting does, and
      assert the model changed **and** the stamp survived — i.e. no page
      load happened. Follow `tests/test_widget_e2e.py:397`'s direct
      `sync_playwright` shape, because a file write lands between two
      evaluations.
      *Red before 4.4 is green; run it after to confirm it passes for the
      right reason, then break the reloader deliberately once to confirm
      the test can fail.*
- [ ] 4.6 **Green** — whatever 4.5 exposes; if nothing, record that and
      the deliberate-break check in `evidence.md`.
- [ ] Commit: `feat(develop): serve the development page from the package`.

## 5. React and Create React App leave

Only now, with a green served page behind it.

- [ ] 5.1 **Red** — `tests/test_packaging.py`:
      `test_source_distribution_builds_both_frontends` becomes
      `test_source_distribution_builds_the_one_frontend` asserting
      `[call(packaging.WIDGET)]`, and the wheel test drops
      `DEVELOPMENT_APP`. `tests/test_cli.py`'s `ServeCommandTest` gains
      `test_the_frontend_flags_are_accepted_and_do_nothing`: `serve
      --build-dir X --start-frontend --dev --frontend-port 3123` parses,
      starts **no** second process (patch `multiprocessing.Process` and
      assert it was never constructed), and reaches `WebViewer`.
      *Red against `packaging.py:38` and `cli.py:102-118`.*
- [ ] 5.2 **Green** — `packaging.py`: `FRONTENDS = (WIDGET,)`,
      `DEVELOPMENT_APP` deleted. `cli.py`: the three flags kept with
      deprecated help text; `run_serve` logs one notice per flag given and
      constructs `WebViewer` only. `server.py`: `WebDevServer`,
      `_setup_proxy_server`, `_proxy` and the `httpx` import deleted;
      `DEFAULT_FRONTEND_PORT`, `frontend_port()` and the `dev`/`frontend`
      parameters **kept** (design D13, D14) so
      `test_server.py:83-89` keeps its meaning.
- [ ] 5.3 **Green** — delete `solid_node_viewer/app/` entirely (`git rm
      -r`): CRA, React, `react-scripts`, `App.tsx`, `App.css`,
      `index.tsx`, `index.css`, `viewerShell.ts(+test)`,
      `reloader.ts(+test)`, `public/`, `tsconfig.json`, `package.json`
      and the 688 kB `package-lock.json`. `bundle.py`: `APP_DIR` and
      `app_build_path()` deleted. `MANIFEST.in:9-10` deleted. Before
      committing, `grep -rn "app_build_path\|APP_DIR\|solid_node_viewer/app"
      --include='*.py' --include='*.in' --include='*.toml' --include='*.md' .`
      returns nothing outside the changelog.
- [ ] 5.4 `pyproject.toml`: move `httpx` from `dependencies` to the `dev`
      extra (it served `_proxy` alone; `fastapi.testclient` needs it in
      the test environment). **Its own step on purpose** — reverting it is
      one line if the reviewer would rather not narrow a released
      dependency set (design §5).
- [ ] 5.5 Confirm the wheel needs one npm build and no app: build a wheel
      into a temporary directory and list its contents — `widget/dist/
      solid-widget.js`, `widget/index.html`, `widget/develop.html`
      present; no `app/`. `scripts/check-dist` is the existing tool; run
      it if the environment allows and record what it did.
- [ ] Commit: `refactor(viewer): drop Create React App and the development app`.

## 6. The declared version

- [ ] 6.1 **Red** — `src/version.test.ts:62-64` expects 11, its comment
      extending the capability history with the reason (the bundle now
      carries a layout to mount the navigator in, and a development mount
      built on it; 10 is the bundle with a navigator and nowhere to put
      it); `tests/test_widget_e2e.py:190`,
      `tests/test_running_document.py:146` and `tests/test_bundle.py:29`
      follow — four literal assertions, and `test_bundle.py`'s method
      name says the number it asserts.
      *Red against `package.json:4`, which says 10.*
      Commands: `npx vitest run src/version.test.ts` and
      `PYTHONPATH="$PWD" … -m pytest tests/test_bundle.py -q -k version`
- [ ] 6.2 **Green** — `solid_node_viewer/widget/package.json`:
      `solidNodeViewerApi: 11`. Nothing else declares it
      (`bundle.py:51-54` reads that file).
- [ ] Commit: `feat(viewer): declare API version 11`.

## 7. The records

- [ ] 7.1 `README.md`: the version table's unreleased `0.2.0` row reads
      `11`; the bullet list at the top loses "the development app" and
      names the development page; `## Reading and moving the assembly`
      gains the inspector — the `mountInspector` signature, its options,
      the handle, the `solid-inspector-*` class contract and the
      custom-property table (the published theming contract, so it
      belongs in the README), and the `data-solid-layout` /
      `?layout=` / `?sidebar=` table of design D8; `## Working on the
      viewer` drops `(cd solid_node_viewer/app && npm ci && npm run
      build)` and the Create React App paragraph, and says instead that
      `solid-node-viewer serve` serves the static development page and
      that the old frontend flags are accepted and ignored.
- [ ] 7.2 `CHANGELOG.md`: the unreleased `0.2.0` section gains entries —
      the inspector layout and the page's layout selection (with the
      plain viewer as the default); the development page becoming a
      static file with the reloader in the bundle, and the build error no
      longer tearing the viewer down; React and CRA leaving the package
      and the frontend flags kept as no-ops for a released framework; the
      API version rising to 11.
- [ ] 7.3 `docs/adrs/EXPORT/ADR-051-the-bundle-ships-an-inspector-layout.md`
      and `docs/adrs/VIEWER-WEB/ADR-052-the-development-page-is-static.md`
      move from **Proposed** to **Accepted**, and their rows in
      `docs/adrs/README.md` with them; ADR-013's status becomes
      **Superseded** by 052 and ADR-036's row gains "amended by 052", in
      the file and in the index. **The reviewer's task**: check both texts
      against what was actually built before promoting them.
- [ ] 7.4 `evidence.md`: every red output and its green counterpart, the
      final counts, and the bundle size before and after. Record the
      `reloader.ts` diff (design D12's table), the deliberate-break check
      of 4.6, and the wheel listing of 5.5.
- [ ] 7.5 At archive time (**the reviewer's**): the baseline
      `openspec/specs/development-server/spec.md` header still says
      `Code: solid_node_viewer/server.py, solid_node_viewer/app/,
      solid_node_viewer/cli.py`. A delta cannot change a Purpose block —
      correct it to `solid_node_viewer/server.py`,
      `solid_node_viewer/widget/develop.html`, `solid_node_viewer/cli.py`
      when syncing. `openspec/config.yaml`'s context paragraph names "the
      Create React App development shell (solid_node_viewer/app)" and
      needs the same correction.

## 8. The whole suite, and what must not have moved

- [ ] 8.1 `npm run typecheck`, `npm test`, `npm run build` in
      `solid_node_viewer/widget`, and `PYTHONPATH="$PWD"
      /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest` at the
      repository root. Every pre-existing test passes unedited except the
      four version assertions, the packaging and CLI tests this change
      deliberately moved, and the server tests it rewrote. **The Python
      suite reports zero skips from a missing built frontend** — the skip
      recorded in 0.2 is gone, which is one of this cycle's outcomes.
- [ ] 8.2 The capture is untouched: `git diff` shows no change to
      `solid_node_viewer/capture.py` or `tests/test_capture.py`, and
      `capture.py:82-83` still mounts with `driverControls: 'none'` and
      `capture.py:151-174` still calls `SolidNodeWidget.mount` — not the
      inspector. Run `pytest tests/test_capture.py -q` and record it.
- [ ] 8.3 The navigator is untouched: `git diff` shows no change to
      `src/navigator.ts`, `src/navtree.ts` or their tests.
- [ ] 8.4 The published file list: `dist/` still carries exactly
      `solid-widget.js`; the export directory an e2e test builds still
      carries exactly `index.html` + `solid-widget.js` beside the document
      and models; `develop.html` is served, never copied by
      `export_with_widget` (`tests/support.py:74-80`).
- [ ] 8.5 The framework needs no change, restated as a check rather than a
      claim: `solid-node-viewer serve --build-dir X --start-frontend`
      starts and serves (5.1's test), and
      `/home/asa/devel/libresolid-studio/solid-node/solid_node/sphinx.py:50`
      and `core/export.py:176-178` still name exactly the two files this
      package still publishes under those names. Read them; do not edit
      them, and do not touch the framework worktree.
- [ ] 8.6 `openspec validate ship-the-inspector-layout --strict` passes.
- [ ] Commit: `docs: record the inspector layout cycle` (records only, if
      7.x did not travel with their own increments).
