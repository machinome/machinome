## 0. Before anything else

- [x] 0.1 Confirm the worktree: `git rev-parse --show-toplevel` names
      `solid-node-viewer/WTs/viewer-navigator` and the branch is
      `viewer-navigator`. Record the head this change starts from.
- [x] 0.2 Record the baseline in `evidence.md`: `npm run typecheck`,
      `npm test`, `npm run build` in `solid_node_viewer/widget`, and the
      Python suite with the workspace venv and `PYTHONPATH="$PWD"` —
      counts, bundle size, and what it skips and why.

## 1. The state, where vitest reaches it

- [x] 1.1 **Red** — `src/assembly.test.ts`: `AssemblyNavigation` reports
      the state a host will read. `state()` (or `root()` + `hidden()`,
      whichever the implementation settles on) gives `root: null` at the
      document root and the focused path after `setRoot(tree, ['left'])`;
      `hidden` lists a hidden node's path and **not** a descendant's after
      hiding a parent; showing it again empties the list; a state read
      before a later `setRoot`/`setVisible` still reads as it did (copies,
      design D1); and after `reconcile` against a tree that dropped both,
      the state reports `root: null` and no hidden path — the assertions
      the two existing reconciliation tests make through `root()` and
      `isVisible()`, now made through the published state.
      *Goes red because `AssemblyNavigation` publishes no hidden list and
      no state snapshot today (`assembly.ts:13-62`).*
- [x] 1.2 **Green** — `src/assembly.ts`: the state read, copying both
      fields. No other behaviour changes; `applyVisibility` and
      `reconcile` are untouched.
- [x] Commit: `feat(assembly): publish focus and hidden paths as state`.

## 2. The notifier, where vitest reaches it

- [x] 2.1 **Red** — `src/assembly.test.ts`: a new `AssemblyChangeNotifier`
      block. Subscribing returns a cancel function; `notify(change)` calls
      every listener with that exact change; cancelling stops it and is
      safe twice; a listener cancelled **during** a notification does not
      receive that notification and one added during it does not either
      (design D6); a listener that throws does not stop the others and
      does not propagate out of `notify`; `dispose()` drops every listener
      and a later `notify` calls nobody.
      *Goes red because the class does not exist.*
- [x] 2.2 **Green** — `src/assembly.ts`: `AssemblyChangeNotifier` beside
      `AssemblyNavigation`, plus the `AssemblyNavigationState`,
      `AssemblyChange` and `AssemblyListener` types. It decides **when
      nothing**: it is told.
- [x] Commit: `feat(assembly): add a change notifier for navigation state`.

## 3. The handle, proved against the real bundle

`viewer.ts`'s mount has no unit test — vitest runs here with no DOM
environment — so the red test for the wiring is the Playwright one.

- [x] 3.1 **Red** — `tests/test_widget_e2e.py`, in `ViewerMountApiTest`
      (the existing harness, `manifest.json`, four children):
      - `navigation()` reads `{root: null, hidden: []}` on a fresh mount;
        after `setRoot(child.path)` and `setVisible(child.path, false)` it
        reads that path and that hidden entry.
      - `onAssemblyChange` returns a function; a listener recording
        `[change.navigation.root, change.assembly.children.length]` is
        notified by `setRoot`, by `setVisible`, by `reload()` and by
        `manifestChanged()`, and **once** by each — count the calls.
      - Inside the listener, `viewer.assembly()` and `viewer.navigation()`
        equal what the change carried (serialize both and compare).
      - `manifestChanged()` has already notified by the time its promise
        resolves.
      - `setVisible(path, true)` on a visible path notifies (design D4).
      - `setRoot(['missing'])` throws, notifies nobody, and leaves
        `navigation()` as it was.
      - the cancel function stops it; `dispose()` itself notifies nobody
        and stops it; calling the cancel function after `dispose()` throws
        nothing.
      - hiding a child of an already hidden node lists both paths;
        showing the parent again leaves the child listed (the explicit
        set, design D3).
      - the maker's own breadcrumb notifies: mount a driver document with
        the chrome inline, click a `.driver-descend` button (the posed
        chrome's prefix is `driver`, `viewer.ts:1165`), and assert the
        listener saw the descended path. **The harness needs one more
        fixture first**: `driven.json` declares its driver as `turns`, a
        single segment, and `navigableChildren` offers a child only for an
        id of at least `focus.length + 2` segments
        (`controls.ts:131-146`), so that document's breadcrumb has nothing
        to descend into. Write a second document beside it — same
        manifest, driver id `Hub.turns`, `Hub` being a real child of the
        Spinner fixture's root — rather than editing `driven.json`, whose
        `turns` id three existing assertions read
        (`test_widget_e2e.py:289-301`). Do not drop this scenario: a focus
        change the host did not make is the reason this change exists.
      *All go red: `navigation` and `onAssemblyChange` are not on the
      handle (`viewer.ts:129-158`).*
- [x] 3.2 **Red** — a targeted update that discards state notifies once
      with the reconciled state. Two page evaluations around a file write:
      mount, focus a child, hide another, keep the handle on `window`;
      write a pruned `manifest.json` into the served export directory that
      no longer contains either node; evaluate `manifestChanged()` and
      assert exactly one notification, `root: null`, and an empty hidden
      list. Use Playwright directly rather than `in_page`, which runs one
      script.
- [x] 3.3 **Green** — `solid_node_viewer/widget/src/viewer.ts`:
      `navigation()` and `onAssemblyChange()` on `ViewerHandle` and on the
      returned handle; the notifier created beside `assemblyNavigation`
      (`:245`) and disposed in `dispose()` (`:757-784`); one `notify(...)`
      at the end of each of `focusOn` (`:552-560`), `setVisible`
      (`:822-828`), `replaceTree` (`:487-508`), `artifactChanged`
      (`:786-791`) and `manifestChanged` (`:793-812`) — after the render,
      before the promise settles, and nowhere else. Re-export the three
      new types beside `AssemblyNode`/`AssemblyPath` (`:57`).
      Mount notifies nobody by construction: `replaceTree` runs before the
      handle exists (`:707`). Assert that in a comment, not a flag.
- [x] Commit: `feat(viewer): publish navigation state and its changes`.

## 4. The declared version

- [x] 4.1 **Red** — `src/version.test.ts:52` expects 9 instead of 8, with
      the comment saying why (a capability a host may require: the
      navigation state and its subscription, which a navigator built on
      this bundle needs to exist); `tests/test_widget_e2e.py:170`,
      `tests/test_running_document.py:146` and `tests/test_bundle.py:29`
      follow — four literal assertions, not three.
      *Red against `package.json:4`, which still says 8.*
- [x] 4.2 **Green** — `solid_node_viewer/widget/package.json`:
      `solidNodeViewerApi: 9`. Nothing else declares it; `bundle.py:54`
      reads that file.
- [x] Commit: `feat(viewer): declare API version 9`.

## 5. The records

- [ ] 5.1 `README.md`: the version table's unreleased `0.2.0` row reads
      `9` (`README.md:124` — a moved row, not a new one), and the section
      that describes the handle gains a sentence on the navigation state
      and its subscription, saying plainly that a listener observes and
      must not drive the viewer from inside itself (design §5 risk 1).
- [ ] 5.2 `CHANGELOG.md`: the same unreleased `0.2.0` section gains an
      entry — the viewer publishes what it is showing and tells a host
      when that moves, whatever moved it; the API version rises to 9; no
      navigator ships yet, and the next cycle mounts one.
- [ ] 5.3 `docs/adrs/EXPORT/ADR-049-the-viewer-publishes-its-navigation-state.md`
      moves from **Proposed** to **Accepted**, and its row in
      `docs/adrs/README.md` with it. Check its text against what was
      actually built before promoting it.
- [ ] 5.4 `evidence.md`: every red output and its green counterpart, the
      final counts, and the bundle size before and after — a bundle that
      grows by more than a few hundred bytes means something rendered,
      and nothing in this change renders.

## 6. The whole suite

- [ ] 6.1 `npm run typecheck`, `npm test`, `npm run build` in
      `solid_node_viewer/widget`, and `PYTHONPATH="$PWD"
      /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest` at the
      repository root. Every pre-existing test passes unedited except the
      three version assertions this change deliberately moved.
- [ ] 6.2 Confirm the published file list is unchanged: `dist/` still
      carries exactly `solid-widget.js` beside the export page's
      `index.html`, so `solid export` and the Sphinx directive copy what
      they copied before and the framework needs no change.
- [ ] 6.3 `openspec validate observe-assembly-navigation --strict` passes.
- [ ] Commit: `docs: record the navigation-state cycle` (records only, if
      5.x did not travel with their own increments).
