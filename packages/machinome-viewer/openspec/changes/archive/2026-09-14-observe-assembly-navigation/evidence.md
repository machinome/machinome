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

## 2. The notifier, where vitest reaches it

### 2.1 Red

Added a top-level `describe('AssemblyChangeNotifier', ...)` block to
`src/assembly.test.ts`: subscribing returns a cancel function; `notify`
calls every listener with the exact change; cancelling twice is safe; a
listener cancelled by an earlier listener in the same dispatch does not
receive it; a listener added during a dispatch does not receive that one
but hears the next; a throwing listener does not stop the others or escape
`notify` (asserted via `console.error`); `dispose()` drops every listener
and a later `notify` calls nobody.

```
$ npx vitest run src/assembly.test.ts
 FAIL  src/assembly.test.ts > AssemblyChangeNotifier > calls every subscribed listener with the exact change notified
TypeError: AssemblyChangeNotifier is not a constructor
 FAIL  src/assembly.test.ts > AssemblyChangeNotifier > subscribing returns a cancel function that stops that listener
TypeError: AssemblyChangeNotifier is not a constructor
 FAIL  src/assembly.test.ts > AssemblyChangeNotifier > cancelling twice is safe
TypeError: AssemblyChangeNotifier is not a constructor
 FAIL  src/assembly.test.ts > AssemblyChangeNotifier > a listener cancelled during a notification does not receive it
TypeError: AssemblyChangeNotifier is not a constructor
 FAIL  src/assembly.test.ts > AssemblyChangeNotifier > a listener added during a notification does not receive that one, but hears the next
TypeError: AssemblyChangeNotifier is not a constructor
 FAIL  src/assembly.test.ts > AssemblyChangeNotifier > a throwing listener does not stop the others or escape notify
TypeError: AssemblyChangeNotifier is not a constructor
 FAIL  src/assembly.test.ts > AssemblyChangeNotifier > dispose drops every listener; a later notify calls nobody
TypeError: AssemblyChangeNotifier is not a constructor

 Test Files  1 failed (1)
      Tests  7 failed | 7 passed (14)
```
Red as expected: the class did not exist.

### 2.2 Green

`src/assembly.ts`: added `AssemblyChange`, `AssemblyListener` and
`AssemblyChangeNotifier` beside `AssemblyNavigation`. `notify` iterates a
snapshot of the listener set and checks live membership before calling
each one, so a listener cancelled earlier in the same dispatch is skipped
and a listener added during the dispatch (not in the snapshot) is not
called until the next `notify`; a throwing listener is reported to
`console.error` and does not stop the loop.

```
$ npx vitest run src/assembly.test.ts
 ✓ src/assembly.test.ts (14 tests) 13ms
 Test Files  1 passed (1)
      Tests  14 passed (14)

$ npx tsc --noEmit
(no output, exit 0)

$ npm test
 Test Files  28 passed (28)
      Tests  533 passed (533)
```

## 3. The handle, proved against the real bundle

`viewer.ts`'s mount has no unit test (vitest runs here with no DOM), so
the red test for the wiring is Playwright against the real bundle.

### 3.1 / 3.2 Red

Added to `tests/test_widget_e2e.py`'s `ViewerMountApiTest`:
- a second fixture document, `nested-driven.json` (driver id `Hub.turns`,
  `Hub` a real child of the Spinner root), because `driven.json`'s
  single-segment `turns` id offers no breadcrumb descend button
  (`navigableChildren`, `controls.ts:131-146`) and three existing
  assertions read that id (`test_widget_e2e.py:289-301` at the time of
  reading, now shifted).
- `test_navigation_reads_focus_and_hidden_and_notifies_once_per_source`
- `test_a_redundant_visibility_call_still_notifies`
- `test_a_refused_focus_notifies_nobody`
- `test_cancel_and_dispose_stop_notifications`
- `test_each_explicitly_hidden_path_is_tracked_independently`
- `test_the_breadcrumb_notifies_a_subscribed_host`
- `test_a_targeted_update_notifies_once_with_reconciled_state` (direct
  `sync_playwright`, not `in_page`: a manifest.json write lands between
  two page evaluations)

Rebuilt the bundle first (`npm run build`, still only carrying increments
1-2 — `viewer.ts` unchanged) so the red is against the real handle.

```
$ npm run build
  dist/solid-widget.js  643.9kb

$ PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest \
    tests/test_widget_e2e.py -q -k "navigation or redundant_visibility or \
    refused_focus or cancel_and_dispose or explicitly_hidden or breadcrumb"
FAILED tests/test_widget_e2e.py::ViewerMountApiTest::test_a_redundant_visibility_call_still_notifies
  Error: Page.evaluate: TypeError: viewer.navigation is not a function
FAILED tests/test_widget_e2e.py::ViewerMountApiTest::test_a_refused_focus_notifies_nobody
  Error: Page.evaluate: TypeError: viewer.navigation is not a function
FAILED tests/test_widget_e2e.py::ViewerMountApiTest::test_cancel_and_dispose_stop_notifications
  Error: Page.evaluate: TypeError: viewer.onAssemblyChange is not a function
FAILED tests/test_widget_e2e.py::ViewerMountApiTest::test_each_explicitly_hidden_path_is_tracked_independently
  Error: Page.evaluate: TypeError: viewer.navigation is not a function
FAILED tests/test_widget_e2e.py::ViewerMountApiTest::test_navigation_reads_focus_and_hidden_and_notifies_once_per_source
  Error: Page.evaluate: TypeError: viewer.navigation is not a function
FAILED tests/test_widget_e2e.py::ViewerMountApiTest::test_the_breadcrumb_notifies_a_subscribed_host
  Error: Page.evaluate: TypeError: viewer.onAssemblyChange is not a function
6 failed, 12 deselected in 7.62s

$ PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest \
    tests/test_widget_e2e.py -q -k targeted_update
FAILED tests/test_widget_e2e.py::ViewerMountApiTest::test_a_targeted_update_notifies_once_with_reconciled_state
  Error: Page.evaluate: TypeError: viewer.onAssemblyChange is not a function
1 failed, 18 deselected in 1.42s
```
Red as expected: `navigation` and `onAssemblyChange` are not yet on the
handle (`viewer.ts:129-158`).

### 3.3 Green

`solid_node_viewer/widget/src/viewer.ts`:
- `navigation()` and `onAssemblyChange()` added to `ViewerHandle` and to
  the returned handle.
- `AssemblyChangeNotifier` created beside `assemblyNavigation`, plus a
  `notifyAssemblyChange()` helper that reads `tree.assembly()` and
  `assemblyNavigation.state()` and calls `assemblyChanges.notify(...)` --
  a no-op when `tree` is undefined, so it is safe to call unconditionally.
- One `notifyAssemblyChange()` call at the end of each of `focusOn`,
  `setVisible`, `replaceTree`, `artifactChanged` and `manifestChanged`,
  after their existing render and, for `replaceTree`, after
  `refreshControls`. Each of these already throws before reaching that
  point for a refused path (`tree.requirePath` inside
  `AssemblyNavigation.setRoot`/`setVisible`), so a refused operation
  notifies nobody with no extra guard.
- `assemblyChanges.dispose()` added to `dispose()`, beside
  `unsubscribeDrivers()`.
- `AssemblyChange`, `AssemblyListener`, `AssemblyNavigationState`
  re-exported beside `AssemblyNode`/`AssemblyPath` (`widget.ts` re-exports
  no types, so it needed no change).
- `replaceTree` runs both from `mount()`, before the handle exists, and
  from `reload()`, after it -- the same function, one notify call at its
  end. Mount notifies nobody because `assemblyChanges` has no
  subscribers yet at that point, not because of a flag; commented in
  place, matching design D5.

```
$ cd solid_node_viewer/widget && npx tsc --noEmit
(no output, exit 0)

$ npm test
 Test Files  28 passed (28)
      Tests  533 passed (533)

$ npm run build
  dist/solid-widget.js  644.4kb

$ PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest \
    tests/test_widget_e2e.py -q -k "navigation or redundant_visibility or \
    refused_focus or cancel_and_dispose or explicitly_hidden or breadcrumb or targeted_update"
.......
7 passed, 12 deselected in 8.29s

$ PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest tests/test_widget_e2e.py -q
...................
19 passed, 4 warnings in 21.91s

$ PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest -q
80 passed, 1 skipped, 11 warnings in 52.70s
```
Same one pre-existing skip as the baseline (`test_server.py:170`).

## 4. The declared version

### 4.1 Red

`src/version.test.ts:50-58` now expects 9, with the comment extending the
numbered capability history to explain why (a navigator needs
`navigation()`/`onAssemblyChange()` to exist before it can mount at all).
`tests/test_bundle.py:28-29` (renamed `test_declares_api_version_nine`),
`tests/test_widget_e2e.py:187` and `tests/test_running_document.py:146`
follow — four literal assertions.

```
$ npx vitest run src/version.test.ts
 FAIL  src/version.test.ts > API_VERSION > declares the assembly-navigation API as version 9
AssertionError: expected 8 to be 9
 Test Files  1 failed (1)
      Tests  1 failed | 5 passed (6)

$ PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest tests/test_bundle.py -q -k version
FAILED tests/test_bundle.py::BundleLookupTest::test_declares_api_version_nine
  AssertionError: 8 != 9
1 failed, 3 passed, 5 deselected

$ PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest tests/test_widget_e2e.py -q -k report_one_api_version
FAILED tests/test_widget_e2e.py::ViewerMountApiTest::test_the_bundle_and_mount_handle_report_one_api_version
  AssertionError: 8 != 9
1 failed, 18 deselected

$ PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest tests/test_running_document.py -q -k ten_add_ones
FAILED tests/test_running_document.py::RunningDocumentTest::test_ten_add_ones_accumulate_the_carry_on_the_page
  AssertionError: 8 != 9
1 failed, 5 deselected
```
Red as expected against `package.json:4`, which still said 8.

### 4.2 Green

`solid_node_viewer/widget/package.json`: `solidNodeViewerApi: 9`.

```
$ npx tsc --noEmit
(no output, exit 0)

$ npm test
 Test Files  28 passed (28)
      Tests  533 passed (533)

$ npm run build
  dist/solid-widget.js  644.4kb

$ PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest -q
80 passed, 1 skipped, 11 warnings in 52.08s
```

## 5. The records

- `README.md`: the version table's unreleased `0.2.0` row now reads `9`.
  See "Deviations" below for the section added to describe the handle's
  navigation API — no such section existed to gain a sentence.
- `CHANGELOG.md`: the unreleased `0.2.0` section gained two bullets — the
  published navigation state and its subscription, and the API version
  rising to 9 — placed before the closing "not in this release" bullet.
- `docs/adrs/EXPORT/ADR-049-…` and its `docs/adrs/README.md` row: left as
  **Proposed**, per instruction (task 5.3 is the reviewer's).

## 6. The whole suite

```
$ cd solid_node_viewer/widget && npm run typecheck && npm test && npm run build
> tsc --noEmit
(no output, exit 0)
 Test Files  28 passed (28)
      Tests  533 passed (533)
  dist/solid-widget.js  644.4kb

$ PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest -q
80 passed, 1 skipped, 11 warnings in ~52s
```

Bundle size: 659294 bytes (baseline) → 659879 bytes (final), +585 bytes —
two handle methods, the notifier class and its types, no DOM. Published
file list unchanged: `dist/` still carries exactly `solid-widget.js`
beside the export page's `index.html`.

Final counts: `npm test` 533 passed, 0 failed, 0 skipped (28 test files).
Python suite: 80 passed, 1 skipped (pre-existing, `test_server.py:170`,
the CRA dev app not built), 0 failed.

```
$ openspec validate observe-assembly-navigation --strict
Change 'observe-assembly-navigation' is valid
```

## Deviations

1. **README section.** Task 5.1 says "the section that describes the
   handle gains a sentence on the navigation state and its subscription".
   No such section existed: `assembly()`, `setRoot()` and `setVisible()`
   were never documented in `README.md` before this change (confirmed by
   grep — the words "assembly" and "navigat" appear nowhere in the file
   except an unrelated CHANGELOG entry). Rather than force the sentence
   into an unrelated section (Versions, or Driving a running machine),
   added a new `## Reading and moving the assembly` section, sized to
   match "Driving a running machine" next to it, covering `assembly()`,
   `setRoot`/`setVisible`, `navigation()` and `onAssemblyChange()`, and
   ending with the "a listener observes" caution the design's risk
   section asks for. This is more than "a sentence", but there was
   nothing to add a sentence to.

2. **The "hiding a child of a hidden node" e2e scenario.** Task 3.1's
   bullet list asks for a Playwright test where "hiding a child of an
   already hidden node lists both paths; showing the parent again leaves
   the child listed." The Spinner fixture (`tests/fixtures/spinner`) is
   flat — `Hub`, `b0`, `b1`, `b2` are all direct children of `Spinner`,
   with no nested assembly among them — so there is no real parent/child
   pair to hide in the e2e harness. Wrote
   `test_each_explicitly_hidden_path_is_tracked_independently` against
   two sibling paths instead, which still proves the WIRING claim this
   suite is responsible for (the explicit set tracks each hidden path
   independently through the real handle) and named it and commented it
   accordingly. The stronger claim design D3 actually makes — a
   descendant hidden only because an ancestor is hidden is never itself
   listed — needs real nesting and is already pinned at the unit level
   in `assembly.test.ts`'s `state` block (increment 1), against a
   purpose-built nested fixture.

3. **Test method rename.** `tests/test_bundle.py`'s
   `test_declares_api_version_eight` was renamed to
   `test_declares_api_version_nine` alongside its assertion; tasks.md did
   not ask for the rename explicitly but leaving the old name asserting a
   different number would have been a wrong test name, not a preserved
   one.

