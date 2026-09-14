## Why

Cycle 2 built a navigator and mounted it into nothing (`navigator.ts:213`,
ADR-050). The bundle now carries a tree component that no page in this
repository shows: the export page a maker opens from `solid export` still
mounts one viewer with a breadcrumb (`widget/index.html:22`), and the
development page is a Create React App shell whose whole job is to load the
bundle and call `mount` (`app/src/App.tsx:16-24`). This cycle puts the
navigator in front of a maker, and in doing so removes the last reason this
package depends on React at all.

Three things drive it:

1. **The navigator is invisible.** `mountNavigator` needs a host element
   beside the viewer, and this package ships no layout that has one. A
   maker with a `solid export` directory and no host code — the case
   ADR-020 exists for — cannot reach it.

2. **The development shell is a React application for no remaining
   reason.** ADR-036 already reduced React to "a lifecycle and
   error/reload shell" and recorded the migration debt explicitly; its own
   alternatives list "Replace the shell with a static page" and rejects it
   only because it would have expanded *that* change. Everything the shell
   does is now either in the bundle (mount, targeted update, chrome,
   navigator) or is ~150 lines of framework-free DOM (the reloader). What
   remains is `react-scripts`, a 688 kB lockfile, a second npm build at
   packaging time (`packaging.py:38`), a proxy and a second dev server in
   the Python package (`server.py:75-91`, `:194-208`), and a test that
   skips itself because none of it was built (`test_server.py:146-147`).

3. **The same layout is wanted in both places.** The development page and
   the export page want exactly one thing: the viewer, its chrome, and a
   tree beside it. Writing it once, in the bundle, is what makes the
   development page a static file at all.

The pilot decided on 2026-09-14 that the export page ships the sidebar
**collapsed**, overridable by an option, and that the development app
becomes a static page the server serves like the export, as long as partial
reload survives. Partial reload is the widget's `manifestChanged()`
(ADR-037), so it does — and this cycle proves it against the served page.

## What Changes

- **`SolidNodeWidget.mountInspector(target, sourceUrl, options?)`.** One
  async call composing, inside a single element a host supplies: a
  collapsible sidebar holding the cycle-2 navigator, and the viewer with
  its own driver chrome. It takes everything `mount` takes plus
  `sidebar: 'collapsed' | 'open'` (default `'collapsed'`) and a `navigator`
  block for the navigator's own options, and resolves to a handle that
  **exposes** the viewer handle and the navigator handle rather than
  wrapping them. No new published file: the layout and its stylesheet live
  inside `solid-widget.js`.

- **The sidebar is a disclosure, and it remembers nothing.** A labelled
  button with `aria-expanded` and `aria-controls`, reachable and operable
  from the keyboard, that opens and closes the sidebar. No `localStorage`,
  no cookie, no URL rewriting: a page ships the state its options say and
  a reload starts there again. The button lives outside the sidebar, in
  one DOM place across both states, so toggling never destroys the element
  that holds focus.

- **The viewer resizes because it already does.** The sidebar is a flex
  sibling removed from layout when collapsed, so the viewer's own element
  changes size and the `ResizeObserver` `mount()` already installs on its
  container (`viewer.ts:761-769`) recomputes the renderer and the camera.
  The layout adds no resize code of its own.

- **One injected stylesheet, the navigator's pattern.** One identifiable
  `<style id="solid-node-inspector-style">` per document, a
  `solid-inspector-*` class contract, CSS custom properties for widths,
  colours and metrics, neutral defaults legible on a light and a dark
  page, and `styles: 'none'` for a host under a policy that forbids inline
  style blocks — exactly the contract ADR-050 published for the navigator.

- **The export page selects the layout.** `widget/index.html` keeps
  `data-solid-widget` (the compatibility contract of ADR-035) and gains
  `data-solid-layout="inspector"`, with a query-string twin `?layout=` and
  `?sidebar=` so the Sphinx directive's channel still reaches it. **The
  default when the attribute is absent is the plain viewer**, so every
  hand-written page and every already-exported directory behaves exactly
  as before. The framework copies the same two files under the same names
  (`solid_node/sphinx.py:50`, `solid_node/core/export.py:176-178`) and
  needs no change.

- **The development page becomes a static file this package carries.**
  `solid_node_viewer/widget/develop.html`, served by `server.py` at `/`
  the way the export page is served by any static server: it checks
  `/_viewer`, loads `/_viewer/bundle.js`, and calls one published entry —
  `SolidNodeWidget.mountDevelopment(target, options?)` — which mounts the
  **inspector** on `/build/viewer.json` with animation inline and
  autoplay, names the tab from the model, and runs the reloader.

- **The reloader is ported into the bundle, unchanged in behaviour.**
  `app/src/reloader.ts` becomes `widget/src/reloader.ts` in plain
  TypeScript: the same `/ws/reload` socket with the same 2 s retry and
  two-attempt grace, the same greeting-triggered `manifestChanged()`, the
  same banner id, class and text (`solid develop is not running — model
  may be stale`), and the same `/_build_error` polling. Its jest tests
  become vitest tests in the widget suite. **Partial reload is shown
  unchanged**, and a Playwright test against the served page proves a
  republished `viewer.json` updates in place with no page load.

- **One deliberate behaviour change, stated so it can be ratified.**
  Today a build error replaces the viewer with a `<pre>`
  (`app/src/App.tsx:28`). The static page shows the error in a pane over
  a viewer that stays mounted, because tearing the viewer down discards
  the camera and a live run for an error the next save will fix, and the
  ratified requirement asks only that errors be shown "in its error
  pane". Nothing else about the reload cycle changes.

- **React and Create React App leave the package.**
  `solid_node_viewer/app/` is deleted whole — CRA, React, `react-scripts`,
  its tests and its 688 kB lockfile — and with it `packaging.py`'s second
  frontend, `MANIFEST.in`'s two `app/*` lines, `bundle.py`'s `APP_DIR` and
  `app_build_path()`, `server.py`'s `WebDevServer` and its httpx proxy,
  and the README's second `npm ci && npm run build`. The wheel needs one
  npm build, and `test_server.py`'s skipped test
  (`test_server.py:146-147`) becomes a real test of the static page.

- **`serve` keeps accepting `--dev`, `--start-frontend` and
  `--frontend-port` as no-ops with a logged notice.** The released
  framework 0.6.0's `solid develop --web-dev` appends `--start-frontend`
  (`solid_node/manager/develop.py:49-51`), and it must keep working
  against this viewer. `DEFAULT_FRONTEND_PORT` and
  `SOLID_NODE_FRONTEND_PORT` go on being read harmlessly for the same
  reason. The development-server spec states this compatibility rule so it
  is a promise rather than an accident.

- **The declared API version rises from 10 to 11.** Two capabilities a
  host may require are added — `mountInspector` and `mountDevelopment` —
  and 10 is the bundle that carries a navigator and no layout to put it
  in.

## Capabilities

### New Capabilities

- `inspector-layout`: the package mounts a composed inspector into one
  element; a maker opens and closes the assembly sidebar; the layout is
  styled by one host-themable stylesheet; the standalone page selects a
  layout and defaults to the plain viewer; the layout disposes as one.

### Modified Capabilities

- `viewer-package`: one modified requirement — the declared API version
  becomes 11, for the two capabilities added to the bundle.
- `viewer-distribution`: one modified requirement — a distribution carries
  **one** built frontend (the bundle) beside the two pages the package
  authors; installing still needs no npm.
- `development-server`: the launch contract (the three frontend flags
  accepted as no-ops), the page (a static file the package carries,
  mounting the inspector), the reload channel and the build-error surface,
  restated against a page that is no longer an application.

Capabilities needing no delta:

- `viewer-assembly-navigation`: the navigator itself is unchanged. This
  cycle mounts it; it does not alter a row, a key, a class or an option.
- `snapshot-capture`: the capture mounts the plain viewer with chrome
  suppressed (`capture.py:82-83`, `:151-174`) and mounts no navigator and
  no layout. A photograph is byte-for-byte the same picture, and a task
  confirms `capture.py` is untouched.

## Impact

- `solid_node_viewer/widget/src/inspector.ts` (new) — `mountInspector`,
  the layout DOM, the disclosure, and the injected stylesheet. Imports
  `viewer.ts` for `mount` and `navigator.ts` for `mountNavigator`.
- `solid_node_viewer/widget/src/reloader.ts` (new, ported) and
  `reloader.test.ts` (ported from `app/src/reloader.test.ts`, jest → vitest,
  jsdom per file).
- `solid_node_viewer/widget/src/develop.ts` (new) — `mountDevelopment`:
  the inspector on `/build/viewer.json`, the document title, the reloader
  and the build-error pane.
- `solid_node_viewer/widget/src/widget.ts` — `mountInspector`,
  `mountDevelopment` and their types on the global; the auto-mount path
  reads `data-solid-layout` and `?layout=`/`?sidebar=`.
- `solid_node_viewer/widget/index.html` — `data-solid-layout="inspector"`.
- `solid_node_viewer/widget/develop.html` (new) — the development page.
- `solid_node_viewer/widget/package.json` — `solidNodeViewerApi: 11`.
- `solid_node_viewer/bundle.py` — `develop_page_path()` replaces `APP_DIR`
  and `app_build_path()`.
- `solid_node_viewer/server.py` — `/` serves the static page;
  `WebDevServer`, `_setup_proxy_server` and `_proxy` deleted.
- `solid_node_viewer/cli.py` — the three flags kept, deprecated in their
  help text, logged once in `run_serve`.
- `solid_node_viewer/packaging.py`, `MANIFEST.in`, `pyproject.toml`
  (`httpx` moves to the `dev` extra with the proxy it served).
- `solid_node_viewer/app/` — **deleted**.
- `tests/test_server.py`, `tests/test_packaging.py`, `tests/test_cli.py`,
  `tests/test_widget_e2e.py`, `tests/test_bundle.py`,
  `tests/test_running_document.py`.
- `README.md`, `CHANGELOG.md`, `docs/adrs/EXPORT/ADR-051-…`,
  `docs/adrs/VIEWER-WEB/ADR-052-…` and their index rows.
- **Consumed by** `adopt-the-viewer-navigator` (shop cycle 4) only in the
  sense that it gates on API `>= 11`; the studio builds its own layout and
  mounts `mountNavigator`, not this one.

## Out of scope

- **The studio.** Cycle 4 deletes `AssemblyPanel` and mounts the
  navigator in the shop's own Model panel. Nothing here touches that
  repository, and the studio does not adopt this layout.
- **The framework.** Verified, not assumed: `solid develop` runs
  `solid-node-viewer serve --build-dir DIR` and appends `--start-frontend`
  only under `--web-dev` (`solid_node/manager/develop.py:42-52`, `:70-71`),
  which this change keeps accepting; `solid export` copies
  `bundle_path()` and `index_path()` (`solid_node/core/export.py:176-178`)
  and the Sphinx directive copies `WIDGET_FILES = ('index.html',
  'solid-widget.js')` (`solid_node/sphinx.py:50`, `:208-225`) — both
  unchanged in name, count and location. The Sphinx directive builds only
  `?t=` and `?autoplay=0` (`sphinx.py:131-135`); giving it a `:sidebar:`
  option would be a framework change and is **not** proposed.
- **The viewer's chrome.** The driver panel, the breadcrumb, the timeline
  and the run transport are untouched. The layout puts the viewer in a
  pane; it does not reach inside it.
- **The navigator.** No option, class, key or row changes.
- **The capture.** Unchanged, and asserted so.
