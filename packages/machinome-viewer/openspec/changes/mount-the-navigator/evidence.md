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
