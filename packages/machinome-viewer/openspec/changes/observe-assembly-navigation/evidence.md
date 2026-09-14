# Evidence — observe-assembly-navigation

## 0. Baseline

Worktree: `/home/asa/devel/libresolid-studio/solid-node-viewer/WTs/viewer-navigator`
Branch: `viewer-navigator`
Starting head: `7683c2966ca5f3484d0254c137819bf6a2cc07c7` (the planning commit)

```
$ cd solid_node_viewer/widget && npm run typecheck
> @solid-node/widget@0.2.0 typecheck
> tsc --noEmit
(no output, exit 0)
```

```
$ npm test
 Test Files  28 passed (28)
      Tests  521 passed (521)
```

```
$ npm run build
  dist/solid-widget.js  643.8kb
⚡ Done in 121ms
```
`dist/solid-widget.js` size: 659294 bytes (643.8kb reported by esbuild).

```
$ PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest -q
73 passed, 1 skipped, 11 warnings in 44.56s
```
The one skip is `tests/test_server.py:170: development app not built (npm run
build)` — pre-existing and environment-driven (the CRA dev app, unrelated to
this change).

## 1. The state, where vitest reaches it

### 1.1 Red

Added a `describe('state', ...)` block to `src/assembly.test.ts`: a fresh
`AssemblyNavigation` reports `{ root: null, hidden: [] }`; `setRoot` moves
`root`; hiding a parent lists it and not its child, and showing it again
empties the list; a state read before a later `setRoot`/`setVisible` is
unaffected by that later call (copies); and after `reconcile` drops both the
focused root and the hidden path, the state reports `root: null, hidden: []`.

```
$ npx vitest run src/assembly.test.ts
 FAIL  src/assembly.test.ts > AssemblyNavigation > state > reports the document root as null and no hidden paths, fresh
TypeError: navigation.state is not a function
 ❯ src/assembly.test.ts:71:25
 FAIL  src/assembly.test.ts > AssemblyNavigation > state > reports the focused path after setRoot
TypeError: navigation.state is not a function
 ❯ src/assembly.test.ts:80:25
 FAIL  src/assembly.test.ts > AssemblyNavigation > state > lists a hidden node and not its descendant
TypeError: navigation.state is not a function
 ❯ src/assembly.test.ts:100:25
 FAIL  src/assembly.test.ts > AssemblyNavigation > state > is a copy: a state already read is unaffected by a later change
TypeError: navigation.state is not a function
 ❯ src/assembly.test.ts:112:33
 FAIL  src/assembly.test.ts > AssemblyNavigation > state > reports root: null and no hidden path once reconcile drops both
TypeError: navigation.state is not a function
 ❯ src/assembly.test.ts:131:25

 Test Files  1 failed (1)
      Tests  5 failed | 2 passed (7)
```
Red as expected: `AssemblyNavigation` published no state snapshot before this
change (`assembly.ts:13-62`).

### 1.2 Green

`src/assembly.ts`: added the `AssemblyNavigationState` interface and a
`state()` method that copies `root()` and builds `hidden` fresh from the
map's values. `apply`, `setRoot`, `setVisible` and `reconcile` untouched.

```
$ npx vitest run src/assembly.test.ts
 ✓ src/assembly.test.ts (7 tests) 13ms
 Test Files  1 passed (1)
      Tests  7 passed (7)

$ npx tsc --noEmit
(no output, exit 0)
```

