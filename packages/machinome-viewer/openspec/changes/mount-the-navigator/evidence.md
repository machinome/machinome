# Evidence — mount-the-navigator

## 0. Baseline

Worktree: `/home/asa/devel/libresolid-studio/solid-node-viewer/WTs/viewer-navigator`
Branch: `viewer-navigator`
Starting head: `991f055b299016c12b1491eeb7609abe817011dc` (the planning commit)

```
$ cd solid_node_viewer/widget && npm run typecheck
> @solid-node/widget@0.2.0 typecheck
> tsc --noEmit
(no output, exit 0)
```

```
$ npm test
 Test Files  28 passed (28)
      Tests  533 passed (533)
```

```
$ npm run build
  dist/solid-widget.js  644.4kb
⚡ Done in 154ms
```
`dist/solid-widget.js` size: 659879 bytes (644.4kb reported by esbuild).

```
$ PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest -q
80 passed, 1 skipped, 11 warnings in 52.96s
```
The one skip is `tests/test_server.py:170: development app not built (npm run
build)` — pre-existing and environment-driven (the CRA dev app, unrelated to
this change).

## 1. The decisions, where vitest already reaches them

### 1.1 Red

`src/navtree.test.ts` (node environment, `controls.test.ts`'s pattern):
`navigatorRows` (rows shown/hidden by expansion, depth, `expandable`, key
from `assemblyPathKey`, `root` on the depth-0/named/no row, `hidden` vs
`obscured` including the both-and-neither cases, effective colour passed
through unchanged), `chipState` (the five states of design D5's table),
`keyAction` (every key of the contract on collapsed/expanded/leaf rows and
both ends of the list, `null` for the root row's Left, focus carrying
`null` for the root row, visibility carrying the row's own `hidden`, an
unbound key), and `reconcileLocal` (first-render root-only expansion,
retained/dropped expansion, active fallback never `null`, revealing a
newly-moved root's ancestors, and NOT re-revealing them when the root did
not move).

```
$ cd solid_node_viewer/widget && npx vitest run src/navtree.test.ts
 FAIL  src/navtree.test.ts [ src/navtree.test.ts ]
Error: Cannot find module './navtree' imported from
'.../solid_node_viewer/widget/src/navtree.test.ts'
Caused by: Error: Failed to load url ./navtree (resolved id: ./navtree)
 Test Files  1 failed (1)
      Tests  no tests
```
Red as expected: `src/navtree.ts` did not exist.

### 1.2 Green

`src/navtree.ts`: `NavigatorLocal`, `NavigatorRow`, `NavigatorAction`,
`navigatorRows`, `chipState`, `keyAction`, `reconcileLocal` — pure,
importing only `assemblyPathKey`/`AssemblyNode`/`AssemblyPath` (as types)
from `tree.ts` and `AssemblyNavigationState` (as a type) from `assembly.ts`.
No DOM, no viewer import.

Two test bugs surfaced on the first run (both in the test, not the
implementation): "Left of a collapsed parent" had asked for `null` where
the correct action is `move` to the parent, and "Left of the root row"
had reused a fixture where the root was already expanded (so Left
correctly collapsed it) instead of one with nothing expanded. Fixed the
test, not the code, and reran:

```
$ npx vitest run src/navtree.test.ts
 ✓ src/navtree.test.ts (39 tests) 11ms
 Test Files  1 passed (1)
      Tests  39 passed (39)

$ npx tsc --noEmit
(no output, exit 0)

$ npm test
 Test Files  29 passed (29)
      Tests  572 passed (572)
```

## 2. The component, in a DOM vitest can hold

### 2.1 Red

`jsdom` added to `devDependencies` (`npm install --save-dev jsdom`,
`jsdom@29.1.1` — the lockfile change travels with this increment's
commit). `src/navigator.test.ts`, opening with

```ts
/**
 * @vitest-environment jsdom
 */
```

against a **stub handle** (`assembly`, `navigation`, `setRoot`,
`setVisible`, `onAssemblyChange` — the whole surface the navigator uses —
whose `setRoot`/`setVisible` notify synchronously, before returning, as
the real handle does): mount draws the tree before returning, roles and
ARIA (`aria-expanded` only on expandable rows, `aria-selected` on the
focused-root row), exactly one tab stop with every other focusable
element inside the tree at `tabindex="-1"`, each row's label/depth/colour,
the four chip states of design D5, every keyboard transition (with
`defaultPrevented`), the "show full assembly" affordance's presence rule
and its suppression, a pushed change the navigator never asked for
redrawing without calling the handle, reconciliation (pruned rows gone,
survivors kept, focus restored), one injected stylesheet across two
mounts, `styles: 'none'`, `className`, a synchronous redraw inside a
checkbox's own `click`, `dispose()` idempotence, a throwing `setRoot` not
escaping a click, and a selector naming no element.

```
$ cd solid_node_viewer/widget && npx vitest run src/navigator.test.ts
Error: Failed to resolve import "./navigator" from "src/navigator.test.ts". Does the file exist?
 Test Files  1 failed (1)
      Tests  no tests
```
Red as expected: `src/navigator.ts` did not exist.

### 2.2 Green

`src/navigator.ts`: `mountNavigator`, `NavigatorOptions`, `NavigatorHandle`,
the injected `NAVIGATOR_STYLESHEET` constant (the class contract and every
custom property of design D13, defaulted exactly as documented), and its
own `resolveTarget` (design D2, commented on why it duplicates
`viewer.ts`'s `resolveContainer` rather than importing it). Every type
from `viewer.ts`, `tree.ts` and `assembly.ts` arrives through `import
type`:

```
$ grep -n "^import" src/navigator.ts
import type { AssemblyChange, AssemblyListener, AssemblyNavigationState } from './assembly';
import {
import type { AssemblyNode, AssemblyPath } from './tree';
import type { ViewerHandle } from './viewer';
```
(the un-typed import is `navtree.ts`'s pure functions and types.)

First pass surfaced a real bug, in the TEST not the component: several
tests called `.focus()` directly on a row that was not the navigator's
current "active" row, to position a starting point for a keyboard
scenario. A real keyboard maker cannot do that -- Tab reaches only the
one row carrying `tabindex="0"` -- so those five failures were the test
exercising a path no keyboard user has. I first tried making the
component ITSELF follow any DOM focus event (a `focusin` listener
promoting whichever row gained focus, by any means, to "active"), which
fixed those five failures but broke the D10 synchronous-redraw test: it
made clicking a DIFFERENT row's checkbox silently move keyboard focus
there on the next redraw too, which is not what design D9's "restore
focus to the active row" means (and not what the studio's own
`AssemblyPanel` does -- its checkbox `onChange` never calls `setActive`,
only its `Focus` button does, `main.tsx:395-403`). Reverted that listener
and fixed the TESTS instead, to navigate the same way a keyboard maker
would (`Tab` to the root row, then `ArrowDown`/`ArrowRight` to the row
under test) rather than teleporting focus with `.focus()`.

```
$ npx vitest run src/navigator.test.ts
 ✓ src/navigator.test.ts (23 tests) 125ms
 Test Files  1 passed (1)
      Tests  23 passed (23)

$ npx tsc --noEmit
(no output, exit 0)
```

### 2.3 The rest of the suite, untouched

```
$ npm test
 Test Files  30 passed (30)
      Tests  595 passed (595)
```
28 pre-existing files + `navtree.test.ts` + `navigator.test.ts` = 30; only
`navigator.test.ts` declares `@vitest-environment jsdom` (confirmed by
`grep -rl "vitest-environment" src/`); `vitest.config.ts` is unchanged.

## 3. Published on the global, proved against the real bundle

### 3.1 Red

`tests/test_widget_e2e.py`'s `HARNESS_PAGE` gains a second host element,
`#navHost`, sized as a sidebar. `ViewerMountApiTest` gains five tests:
`test_the_bundle_mounts_a_navigator_from_a_handle`,
`test_the_navigator_keyboard_drives_the_viewer`,
`test_the_breadcrumb_moves_the_navigators_root`,
`test_a_targeted_update_reconciles_the_navigator` (direct
`sync_playwright`, a manifest write landing between two evaluations, like
`test_a_targeted_update_notifies_once_with_reconciled_state`), and
`test_two_navigators_agree_and_dispose_independently`.

```
$ cd solid_node_viewer/widget && npm run build
  dist/solid-widget.js  644.4kb

$ PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest \
    tests/test_widget_e2e.py -q -k navigator
FAILED tests/test_widget_e2e.py::ViewerMountApiTest::test_the_bundle_mounts_a_navigator_from_a_handle
  Error: Page.evaluate: TypeError: SolidNodeWidget.mountNavigator is not a function
FAILED tests/test_widget_e2e.py::ViewerMountApiTest::test_the_navigator_keyboard_drives_the_viewer
  Error: Page.evaluate: TypeError: SolidNodeWidget.mountNavigator is not a function
FAILED tests/test_widget_e2e.py::ViewerMountApiTest::test_the_breadcrumb_moves_the_navigators_root
  Error: Page.evaluate: TypeError: SolidNodeWidget.mountNavigator is not a function
FAILED tests/test_widget_e2e.py::ViewerMountApiTest::test_a_targeted_update_reconciles_the_navigator
  Error: Page.evaluate: TypeError: SolidNodeWidget.mountNavigator is not a function
FAILED tests/test_widget_e2e.py::ViewerMountApiTest::test_two_navigators_agree_and_dispose_independently
  Error: Page.evaluate: TypeError: SolidNodeWidget.mountNavigator is not a function
5 failed, 19 deselected in 6.51s
```
Red as expected: rebuilt against the real bundle first, which still
lacked the export.

### 3.2 Green

`src/widget.ts`: `export { mountNavigator } from './navigator';` beside
`mount`, and `export type { NavigatorHandle, NavigatorOptions }` beside
the existing type re-exports.

```
$ npx tsc --noEmit
(no output, exit 0)

$ npm run build
  dist/solid-widget.js  653.6kb
```
`dist/solid-widget.js` size: 669243 bytes (653.6kb reported by esbuild).

```
$ PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest \
    tests/test_widget_e2e.py -q -k navigator
.....
5 passed, 19 deselected in 5.90s

$ PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest tests/test_widget_e2e.py -q
........................
24 passed, 4 warnings in 27.71s
```

### Deviation

`test_a_targeted_update_reconciles_the_navigator`'s task asks to "expand
a child, write a pruned manifest.json... and assert... the surviving
expansion is kept". The Spinner fixture is flat -- `Hub`, `b0`, `b1`,
`b2` are all `LeafNode`s with no children of their own (confirmed by
reading `tests/fixtures/spinner/manifest.json`) -- so there is no child
row this harness can expand to reveal grandchildren of, the same
limitation the prior cycle's evidence recorded for its own nested
scenario (`observe-assembly-navigation`'s evidence.md, deviation 2).
Wrote the test against the only expandable row the fixture has instead
(the document root): its expansion survives the targeted update, a
removed child's row is gone, a kept child's row survives, and exactly
one row remains the keyboard stop. The stronger claim design D9 makes --
a CHILD's own expansion surviving reconciliation -- needs real nesting
and is already pinned at the unit level in `navtree.test.ts`'s
`reconcileLocal` block (increment 1) and exercised through the DOM in
`navigator.test.ts`'s "reconciles a pruned tree" test (increment 2).
