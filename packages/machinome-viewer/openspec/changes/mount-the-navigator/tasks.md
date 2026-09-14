## 0. Before anything else

- [x] 0.1 Confirm the worktree: `git rev-parse --show-toplevel` names
      `solid-node-viewer/WTs/viewer-navigator` and the branch is
      `viewer-navigator`. Record the head this change starts from.
- [x] 0.2 Record the baseline in `evidence.md`: `npm run typecheck`,
      `npm test`, `npm run build` in `solid_node_viewer/widget`, and
      `PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python
      -m pytest` at the repository root — counts, bundle size in bytes,
      and what it skips and why.

## 1. The decisions, where vitest already reaches them

No DOM in this increment: it is `controls.ts`'s pattern, and every rule
in design D3, D4, D5 and D9 is decided here so a browser never has to be
asked what the component thinks.

- [x] 1.1 **Red** — `src/navtree.test.ts` (node environment, like
      `controls.test.ts`), against hand-built `AssemblyNode` literals —
      a root with a nested child and a leaf, one coloured ancestor:
      - `navigatorRows`: the root alone when nothing is expanded; the
        root plus its children when the root's key is expanded; depth
        per level; `expandable` off a node's own children; `key` from
        `assemblyPathKey` (`tree.ts:47-49`), so it is the key the
        viewer hides by.
      - `root`: true on the depth-0 row when `navigation.root` is
        `null`, on the named row when it is a path, and on no row when
        the path is one the presented tree does not currently show.
      - `hidden` vs `obscured` (design D5): a hidden parent's row is
        `hidden`, its descendant's row is `obscured` and **not**
        `hidden`; a descendant that is itself in the hidden list is
        both; showing the parent leaves the descendant `hidden` only.
      - `keyAction` for every key of the contract, on three row shapes
        (collapsed parent, expanded parent, leaf) and at both ends of
        the list: Down/Up move or stay; Right expands then enters; Left
        collapses then leaves to the parent; Left on the root row does
        nothing; Enter yields a focus action carrying **`null` for the
        root row and the path otherwise** (design D4); Space yields a
        visibility action carrying the inverse of the row's own
        `hidden`; any other key yields nothing.
      - `reconcileLocal`: keeps expanded keys the new tree still has and
        drops the rest; keeps `active` when it survives and falls back
        to the root's key when it does not, never to `null`; expands the
        root on a first reconcile and not on a later one; reveals a
        newly focused root's ancestors, and does **not** re-expand them
        when the root did not move (design D9).
      *Goes red because `src/navtree.ts` does not exist.*
      Command: `cd solid_node_viewer/widget && npx vitest run src/navtree.test.ts`
- [x] 1.2 **Green** — `src/navtree.ts`: the types of design D3 and those
      four functions, pure, importing only `assemblyPathKey` from
      `tree.ts` and the assembly/navigation **types**. No DOM, no
      viewer import.
- [x] Commit: `feat(navigator): decide the navigator's rows and keys`.

## 2. The component, in a DOM vitest can hold

- [x] 2.1 **Red** — `src/navigator.test.ts`, opening with the documented
      docblock so the environment is this file's alone:
      ```ts
      /**
       * @vitest-environment jsdom
       */
      ```
      and `jsdom` added to `devDependencies` in
      `solid_node_viewer/widget/package.json` (installed with
      `npm install`), because the file cannot go red for the right
      reason in an environment that does not exist. Nothing in
      `vitest.config.ts` changes.

      Against a **stub handle** — an object literal with `assembly()`,
      `navigation()`, `setRoot()`, `setVisible()` and
      `onAssemblyChange()`, recording its calls and holding the listener
      so the test can push a change — assert:
      - mounting into a detached element draws before returning: a
        `role="tree"` with an accessible name, one `role="treeitem"` per
        presented node, `aria-expanded` only on rows with children,
        `aria-selected` on the focused-root row.
      - exactly one row has `tabindex="0"` and every other focusable
        element inside the tree has `tabindex="-1"` (design: one tab
        stop).
      - each row's label text, its `--solid-nav-depth` and
        `--solid-nav-node-color` custom properties, and the four chip
        states of design D5 — `checked`, the accessible name, and the
        `--hidden` / `--obscured` row classes.
      - Arrow keys move `document.activeElement` between rows and
        expand/collapse; `Enter` calls `setRoot` with the path — and
        with `null` on the root row; `Space` calls `setVisible` with the
        inverse of that row's own hidden state; each handled key had
        `defaultPrevented`.
      - the "show full assembly" affordance appears only when
        `navigation().root !== null`, calls `setRoot(null)`, and is
        absent under `fullAssembly: false`.
      - pushing a change through the stub's listener redraws from the
        payload — including a payload whose navigation the navigator
        never asked for — and the navigator calls **nothing** on the
        handle from inside the listener.
      - reconciliation through the listener: a pruned assembly drops its
        rows, keeps the surviving expansion, and restores keyboard focus
        to the new active row when focus was inside the tree before.
      - two mounts in one document inject exactly one
        `#solid-node-navigator-style`; `styles: 'none'` injects none;
        `className` lands on the root element.
      - a stub whose `setVisible` notifies **synchronously, before it
        returns** (as the real handle does): clicking a checkbox rebuilds
        the tree inside the click, nothing throws, the new checkbox
        reflects the pushed payload, and keyboard focus lands on the
        active row (design D10, D9).
      - `dispose()` calls the unsubscribe the stub returned, empties the
        target, and is harmless a second time; a stub whose `setRoot`
        throws does not throw out of a click (design D10).
      - a selector naming no element is refused with a message naming it.
      *Goes red at module resolution: `src/navigator.ts` does not exist.*
      Command: `cd solid_node_viewer/widget && npx vitest run src/navigator.test.ts`
- [x] 2.2 **Green** — `src/navigator.ts`: `mountNavigator`,
      `NavigatorOptions`, `NavigatorHandle`, the injected stylesheet
      constant with the class contract and custom properties of design
      D13, and its own `resolveTarget` (design D2, with the comment
      saying why it is not `viewer.ts`'s). Every type it needs from
      `viewer.ts`, `tree.ts` and `assembly.ts` comes in through
      `import type`, so this module pulls no renderer — check with
      `npx vitest run src/navigator.test.ts` staying fast and with
      `grep -n "^import" src/navigator.ts`.
- [x] 2.3 Confirm the rest of the suite is untouched by the new
      environment: `npm test` still reports 28 files plus this one, and
      the pre-existing 533 tests still run in `node`.
- [x] Commit: `feat(navigator): mount a plain-DOM assembly navigator`.

## 3. Published on the global, proved against the real bundle

- [x] 3.1 **Red** — `tests/test_widget_e2e.py`, in `ViewerMountApiTest`
      (its harness page gains a second host element for the navigator —
      `HARNESS_PAGE`, `:92-106`):
      - `test_the_bundle_mounts_a_navigator_from_a_handle`:
        `SolidNodeWidget.mountNavigator(navHost, viewer)` draws five
        rows for the Spinner fixture (root expanded, four children),
        each with its `role` and label.
      - `test_the_navigator_keyboard_drives_the_viewer`: focus the root
        row, `ArrowDown` to the first child, `Enter`, and read
        `viewer.navigation().root`; `Space`, and read
        `viewer.navigation().hidden`; `ArrowLeft` back to the parent.
        Dispatch real `KeyboardEvent`s on `document.activeElement`.
      - `test_the_breadcrumb_moves_the_navigators_root`: mount
        `nested-driven.json` with `driverControls: 'inline'` (the
        fixture cycle 1 added for exactly this, `:134-141`), click
        `.driver-descend`, and assert the navigator's `Hub` row is now
        the one marked as the focused root — with no host code between
        them.
      - `test_a_targeted_update_reconciles_the_navigator`: expand a
        child, write a pruned `manifest.json`, `await
        viewer.manifestChanged()`, and assert the removed rows are gone,
        the surviving expansion is kept and exactly one row is the
        keyboard stop. Use `sync_playwright` directly, like
        `test_a_targeted_update_notifies_once_with_reconciled_state`,
        because a file write lands between two evaluations.
      - `test_two_navigators_agree_and_dispose_independently`: two
        mounts on one handle; hide in one, read the other; dispose one
        and assert its element is empty while the other still updates;
        one `#solid-node-navigator-style` in the document.
      *All go red: `SolidNodeWidget.mountNavigator is not a function`.*
      Command: `PYTHONPATH="$PWD"
      /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest
      tests/test_widget_e2e.py -q -k navigator` (rebuild the bundle
      first, so the red is against a real bundle that simply lacks the
      export).
- [x] 3.2 **Green** — `src/widget.ts`: export `mountNavigator` beside
      `mount` (`widget.ts:14-16`) and re-export `NavigatorOptions` and
      `NavigatorHandle` as types; `npm run build`; rerun 3.1.
- [x] Commit: `feat(widget): publish mountNavigator on the global`.

## 4. The declared version

- [ ] 4.1 **Red** — `src/version.test.ts:57-59` expects 10, its comment
      extending the capability history with the reason (the bundle now
      carries a navigator a host may require, and 9 is the bundle that
      publishes the state without one); `tests/test_widget_e2e.py:188`,
      `tests/test_running_document.py:146` and `tests/test_bundle.py:28-29`
      follow — four literal assertions, and `test_bundle.py`'s method
      name says the number it asserts.
      *Red against `package.json:4`, which says 9.*
      Commands: `npx vitest run src/version.test.ts` and
      `PYTHONPATH="$PWD" … -m pytest tests/test_bundle.py -q -k version`
- [ ] 4.2 **Green** — `solid_node_viewer/widget/package.json`:
      `solidNodeViewerApi: 10`. Nothing else declares it
      (`bundle.py:54` reads that file).
- [ ] Commit: `feat(viewer): declare API version 10`.

## 5. The records

- [ ] 5.1 `README.md`: the version table's unreleased `0.2.0` row reads
      `10` (a moved row, not a new one), and the `Reading and moving the
      assembly` section gains the navigator: the `mountNavigator`
      signature, the options, the handle, the class-name contract and
      the custom-property table of design D13 — the table is the
      published theming contract, so it belongs in the README and not
      only in the change.
- [ ] 5.2 `CHANGELOG.md`: the unreleased `0.2.0` section gains an entry —
      the bundle now carries the assembly navigator itself, mounted into
      any element from a handle, themed by CSS custom properties; the
      API version rises to 10; no layout ships yet and the export page
      is unchanged.
- [ ] 5.3 `docs/adrs/EXPORT/ADR-050-the-navigator-is-a-component-of-the-viewer.md`
      moves from **Proposed** to **Accepted**, and its row in
      `docs/adrs/README.md` with it. The reviewer's task: check the text
      against what was actually built before promoting it.
- [ ] 5.4 `evidence.md`: every red output and its green counterpart, the
      final counts, and the bundle size before and after. The bundle
      grows here — a module and a stylesheet — so record the number
      rather than asserting it did not.

## 6. The whole suite

- [ ] 6.1 `npm run typecheck`, `npm test`, `npm run build` in
      `solid_node_viewer/widget`, and `PYTHONPATH="$PWD"
      /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest` at
      the repository root. Every pre-existing test passes unedited
      except the four version assertions this change deliberately moved.
- [ ] 6.2 Confirm the published file list is unchanged: `dist/` still
      carries exactly `solid-widget.js` beside the export page's
      `index.html`, so `solid export` and the Sphinx directive copy what
      they copied before and the framework needs no change. Confirm
      `index.html` itself is byte-identical.
- [ ] 6.3 Confirm nothing outside this repository changed: the studio's
      `AssemblyPanel` and its CSS are untouched, and the development app
      and capture page are untouched.
- [ ] 6.4 `openspec validate mount-the-navigator --strict` passes.
- [ ] Commit: `docs: record the navigator cycle` (records only, if 5.x
      did not travel with their own increments).
