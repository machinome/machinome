# Evidence — ship-the-inspector-layout

## 0. Baseline

Worktree: `/home/asa/devel/libresolid-studio/solid-node-viewer/WTs/viewer-navigator`
Branch: `viewer-navigator`
Starting head: `bbfd0bc` (the planning commit)

```
$ cd solid_node_viewer/widget && npm run typecheck
> @solid-node/widget@0.2.0 typecheck
> tsc --noEmit
(no output, exit 0)
```

```
$ npm test
 Test Files  30 passed (30)
      Tests  597 passed (597)
```

```
$ npm run build
  dist/solid-widget.js  653.9kb
⚡ Done in 143ms
```
`dist/solid-widget.js` size: 669594 bytes (653.9kb reported by esbuild).

```
$ PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest -q
85 passed, 1 skipped, 11 warnings in 58.22s
```
The one skip is `tests/test_server.py:146-147`
(`DevelopmentAppBrowserTest.setUp`'s `self.skipTest('development app not
built (npm run build)')`) — the CRA app was never built in this
environment, which is the skip this change is about to delete by making
the served page a package file rather than a build output.

## 1. The layout, in a DOM vitest can hold

Design D1-D7. The seam of design D15 (`mountInspectorWith(mountFn,
mountNavigatorFn, target, sourceUrl, options)`) is what makes this
testable without WebGL, exactly as design D15 describes.

### 1.1 Red

`src/inspector.test.ts` (jsdom): the target's only child is
`.solid-inspector`, holding a rail with the toggle, a `.solid-inspector-
sidebar` and a `.solid-inspector-viewer` -- with the stub `mount` called
on the VIEWER PANE, never the target; the toggle's `aria-expanded`,
`aria-controls` naming the sidebar's id, and its accessible name
`Assembly`; `sidebar: 'open'` starting the sidebar shown, the default
collapsed; the toggle opening/closing on a dispatched click while
`document.activeElement` stays on it; `handle.sidebarOpen()` and
`handle.setSidebar()`; nothing written to storage and no URL rewrite
across a toggle; the navigator mounted into the sidebar with
`options.navigator` passed through untouched and its `styles` defaulted
from the layout's own; the handle exposing the stub viewer and navigator
handles as fields; disposal order (navigator before viewer), idempotence
and emptying the target; one injected `#solid-node-inspector-style`
across two mounts, none under `styles: 'none'`; `className` reaching the
viewer pane's mount options and not the layout root; a rejecting stub
`mount` leaving the target empty and rethrowing the original error; and a
selector naming no element refused by name.

```
$ cd solid_node_viewer/widget && npx vitest run src/inspector.test.ts
Error: Failed to resolve import "./inspector" from "src/inspector.test.ts". Does the file exist?
 Test Files  1 failed (1)
      Tests  no tests
```
Red as expected: `src/inspector.ts` did not exist.

### 1.2 Green

`src/inspector.ts`: `InspectorOptions`, `InspectorHandle`,
`mountInspector`, `mountInspectorWith`, the `INSPECTOR_STYLESHEET`
constant (the `solid-inspector-*` class contract and the
`--solid-inspector-*` custom properties of design D6/D13, neutral
defaults), and the one-per-document injection guard. No resize handler of
any kind -- the viewer's own `ResizeObserver` (`viewer.ts:757-769`) is
the mechanism; increment 2's `test_the_toggle_opens_the_sidebar_and_the_
canvas_narrows` proves it in a browser.

```
$ npx vitest run src/inspector.test.ts
 ✓ src/inspector.test.ts (20 tests) 64ms
 Test Files  1 passed (1)
      Tests  20 passed (20)

$ npx tsc --noEmit
(no output, exit 0)
```
Green on the first pass -- no test or implementation bug surfaced.

### 1.3 The rest of the suite, untouched

```
$ npm test
 Test Files  31 passed (31)
      Tests  617 passed (617)

$ grep -rl "vitest-environment" src/
src/navigator.test.ts
src/inspector.test.ts
```
30 pre-existing files + `inspector.test.ts` = 31; only the two jsdom
files declare the pragma.

## 2. The page selects a layout

Design D8. The default stays the plain viewer.

### 2.1 Red

`src/widget.test.ts` (new, `node` environment — no DOM is needed to
decide a layout, unlike `inspector.test.ts`/`navigator.test.ts`) over a
pure `layoutChoice(dataset, search)` extracted into its own module,
`src/layout.ts` (not re-exported from `widget.ts`: esbuild's IIFE
`globalName` build puts every top-level export of `widget.ts` on the
public `SolidNodeWidget` object, and this decision is not a capability a
host calls). The table of design D8: no attribute/no query is `viewer`;
`data-solid-layout="inspector"` is `inspector`; `?layout=` overrides the
attribute in both directions; `data-solid-sidebar`/`?sidebar=` likewise;
an unrecognised value is reported as `{ unknown: value }`.

```
$ cd solid_node_viewer/widget && npx vitest run src/widget.test.ts
Error: Failed to resolve import "./layout" from "src/widget.test.ts". Does the file exist?
 Test Files  1 failed (1)
      Tests  no tests
```
Red as expected: `src/layout.ts` did not exist.

### 2.2 Green

`src/layout.ts`: `LayoutDataset`, `LayoutChoice`, `layoutChoice`.
`widget.ts`'s `autoMount` calls it per element: `mount()` for `'viewer'`,
`mountInspector()` for `'inspector'` (with `sidebar` from the choice),
and for an unknown layout `element.textContent = 'solid-widget: unknown
layout "<value>"'` in the shape the failed-mount branch already uses.
`mountInspector` and its types (`InspectorHandle`, `InspectorOptions`)
are exported on the global beside `mount` and `mountNavigator`.

```
$ npx vitest run src/widget.test.ts
 ✓ src/widget.test.ts (9 tests) 3ms
 Test Files  1 passed (1)
      Tests  9 passed (9)

$ npx tsc --noEmit
(no output, exit 0)
```

### 2.3 Red — the real bundle and the real page

`tests/test_widget_e2e.py`'s new `InspectorLayoutE2ETest` (Playwright,
against `export_with_widget`'s real `index.html` and the real bundle,
rebuilt first): the shipped page shows a collapsed sidebar and its
toggle; the toggle opens the sidebar and the canvas narrows (and closing
returns it, within 2px); `?sidebar=open` ships it open; a hand-written
page carrying only `data-solid-widget` has no `.solid-inspector` element;
an unknown `?layout=` value is refused by name in the container.

```
$ cd solid_node_viewer/widget && npm run build
  dist/solid-widget.js  657.2kb

$ PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest \
    tests/test_widget_e2e.py -q -k inspector
FAILED tests/test_widget_e2e.py::InspectorLayoutE2ETest::test_the_export_page_mounts_the_inspector
  playwright._impl._errors.TimeoutError: Page.wait_for_selector: Timeout 30000ms exceeded.
  waiting for locator(".solid-inspector-sidebar") to be visible
FAILED tests/test_widget_e2e.py::InspectorLayoutE2ETest::test_the_query_string_opens_the_sidebar
FAILED tests/test_widget_e2e.py::InspectorLayoutE2ETest::test_the_toggle_opens_the_sidebar_and_the_canvas_narrows
3 failed, 2 passed, 24 deselected in 96.11s
```
Red as expected: `index.html` carried no `data-solid-layout` attribute
yet, so the export page still mounted the plain viewer. The other two
new tests already passed at this point — the auto-mount *logic* from
2.2 was already in the bundle; only the shipped page's own attribute was
still missing, which is exactly the ordering design D8 and this
increment's split are about.

### 2.4 Green

`widget/index.html:22` gains `data-solid-layout="inspector"` and
nothing else:

```
$ git diff solid_node_viewer/widget/index.html
-  <div id="solid-widget" data-solid-widget="manifest.json"></div>
+  <div id="solid-widget" data-solid-widget="manifest.json" data-solid-layout="inspector"></div>
```
One attribute. The file's name, its `<title>`, its `<style>` and
`data-solid-widget` are unchanged.

```
$ npm run build
  dist/solid-widget.js  657.2kb

$ PYTHONPATH="$PWD" … -m pytest tests/test_widget_e2e.py -q -k inspector
.....
5 passed, 24 deselected in 5.95s

$ PYTHONPATH="$PWD" … -m pytest tests/test_widget_e2e.py -q
.............................
29 passed, 4 warnings in 32.79s

$ npx tsc --noEmit
(no output, exit 0)

$ npm test
 Test Files  32 passed (32)
      Tests  626 passed (626)
```
