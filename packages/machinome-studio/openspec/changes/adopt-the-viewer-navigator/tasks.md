## 0. Before anything else

- [ ] 0.1 Confirm the worktree: `git rev-parse --show-toplevel` names
      `/home/asa/devel/libresolid-studio/WTs/viewer-navigator` and the branch is
      `viewer-navigator`. Record the head this change starts from (the planning
      commit). Never `cd` into another checkout; the viewer worktree is read by
      absolute path only.
- [ ] 0.2 Record the baseline in `evidence.md`: for each command, the exact
      invocation and its counts.
      - `npm --prefix floor/frontend run test`
      - `npm --prefix floor/frontend run build`
      - `/home/asa/devel/libresolid-studio/.venv/bin/python -m pytest tests -q`
        (the README's own suite command is
        `python -m unittest discover -s tests`; either is acceptable as long as
        the same one is used throughout)
      Name every pre-existing skip or failure and why, so a later count is
      comparable.
- [ ] 0.3 Record the real bundle this cycle tests against: the output of
      `head -c 512 /home/asa/devel/libresolid-studio/solid-node-viewer/WTs/viewer-navigator/solid_node_viewer/widget/dist/solid-widget.js`
      (its banner names `viewer API 11`) and its size in bytes, and the output
      of `/home/asa/devel/libresolid-studio/.venv/bin/solid-node-viewer describe`
      (today API 8, from the primary checkout — which is why discovery alone
      skips).

## 1. The gate rises to the navigator API

One commit. Design D3.

- [ ] 1.1 **Red** — change the three assertions that pin the old API, and run
      them against unchanged production code:
      - `tests/test_project_open.py:128` → `viewer_api_version` is `10`
      - `tests/test_project_preparation.py:380` → `viewer_api_version` is `10`
      - `tests/test_project_preparation.py:523` → the expected message is
        `viewer API 10 is required but installed viewer API is 3`
      and add to `test_required_viewer_api_matches_the_declared_widget_interface`
      (`tests/test_project_preparation.py:538-540`) an assertion that the
      vendored declaration names `mountNavigator` and `NavigatorHandle`.
      Command:
      `/home/asa/devel/libresolid-studio/.venv/bin/python -m pytest tests/test_project_open.py tests/test_project_preparation.py -q`
      Record the failures in `evidence.md` — they must fail on the API number
      and on the missing declaration, not on an import or a fixture.
- [ ] 1.2 **Green** — `floor/preparation.py:28` becomes
      `REQUIRED_VIEWER_API = 10`, with a comment naming the capability that
      number buys (`mountNavigator`, viewer ADR-050) rather than a version for
      its own sake.
- [ ] 1.3 **Green** — re-vendor `floor/frontend/src/solid-node-widget.d.ts` from
      the viewer worktree at API 11, declaring
      `SOLID_NODE_VIEWER_API_VERSION: 10`. Copy the shapes verbatim from
      `solid_node_viewer/widget/src/viewer.ts` (`ViewerHandle` members the studio
      uses, `AssemblyNavigationState`, `AssemblyChange`, `AssemblyListener`),
      `src/tree.ts` (`AssemblyNode`, `AssemblyPath`) and `src/navigator.ts`
      (`NavigatorOptions`, `NavigatorHandle`), and add `mountNavigator` to the
      `window.SolidNodeWidget` declaration. Leave the driving, playback and run
      surfaces out (design D3). Head the file with a comment recording the
      viewer package version, viewer API version and the commit it was vendored
      from.
- [ ] 1.4 **Green** — the fakes report the new API:
      `tests/fixtures/fake_solid.py:150` defaults `viewer_api_version` to `10`
      and honours an env override `FAKE_SOLID_VIEWER_API` (design D4);
      `tests/test_project_preparation.py:727-728`'s inline fake reports
      `apiVersion:10` in its JS and defaults `FAKE_SOLID_VIEWER_API` to `10`.
- [ ] 1.5 Green run: the command from 1.1 passes, and
      `npm --prefix floor/frontend run test` still passes (the old
      `AssemblyPanel` must still type-check against the re-vendored
      declaration — if it does not, the declaration dropped something the studio
      still uses; add it back rather than editing `main.tsx` here).
- [ ] 1.6 Commit: `floor/preparation.py`,
      `floor/frontend/src/solid-node-widget.d.ts`, the two fakes and the three
      tests. One focused commit.

## 2. The Model panel mounts the viewer's navigator

One commit. Design D1, D5. The studio's `AssemblyPanel` is still in the file at
the end of this increment — it is simply no longer rendered.

- [ ] 2.1 Give the fake widget the minimal `mountNavigator` of design D5:
      `apiVersion:10` on both the global and the handle, a `navigators` array on
      `window.__solidNodeWidgetHistory`, an empty
      `div.solid-nav > div.solid-nav-tree[role=tree][aria-label]`, and a
      `dispose()` that marks the record and empties the target. No rows, no
      keyboard, no `onAssemblyChange`.
- [ ] 2.2 **Red** — add `test_model_panel_mounts_and_disposes_the_viewer_navigator`
      to `tests/test_shop_lifecycle_e2e.py`: open a project, and assert
      - the `MODEL` heading is present and the tree named `Assembly` is inside
        the Model context panel;
      - `window.__solidNodeWidgetHistory.navigators` has exactly one entry whose
        `label` is `Assembly`;
      - selecting Code and returning to Model leaves
        `navigators.length === 1` and `mounts === 1` (no remount);
      - closing the project sets that record's `disposed` to `true`.
      Command:
      `/home/asa/devel/libresolid-studio/.venv/bin/python -m pytest tests/test_shop_lifecycle_e2e.py -k mounts_and_disposes -q`
      Record the failure: `navigators` is undefined because nothing calls
      `mountNavigator`.
- [ ] 2.3 **Green** — add the `AssemblyNavigator` wrapper of design D1 to
      `floor/frontend/src/main.tsx` and render it at the workspace's Model
      context panel (`main.tsx:1958`) as
      `<AssemblyNavigator viewer={viewerHandle} />`. Keep the heading `MODEL`
      and the `No model assembly is available.` empty state. The host `<div>`
      must carry no React children (the navigator empties it on dispose).
- [ ] 2.4 **Green** — `loadViewer` (`main.tsx:598`) rejects after the script
      loads when `window.SolidNodeWidget` is absent or its `apiVersion` is below
      `SOLID_NODE_VIEWER_API_VERSION`, landing on the existing
      `viewerReady === false` state. No new UI.
- [ ] 2.5 Delete the two tests this render swap supersedes, in this same
      increment, so no commit leaves the suite red:
      `test_model_panel_navigates_the_viewer_assembly`
      (`tests/test_shop_lifecycle_e2e.py:561-668`) and
      `test_model_panel_controls_the_supplied_framework_viewer` (`:670-704`).
      They assert a DOM the panel no longer renders
      (`.assembly-row`, `focused-root`, the studio's `Expand housing` button).
      Before deleting, list their scenarios in `evidence.md` and say for each
      one which of 2.2's assertions or 3.2's assertions carries it afterwards —
      nothing may be dropped silently.
- [ ] 2.6 Green run: 2.2's command, plus
      `npm --prefix floor/frontend run test`,
      `npm --prefix floor/frontend run build`, and the whole file
      `/home/asa/devel/libresolid-studio/.venv/bin/python -m pytest tests/test_shop_lifecycle_e2e.py -q`.
      Counts into `evidence.md`.
- [ ] 2.7 Commit: `main.tsx`, `tests/fixtures/fake_solid.py`,
      `tests/test_shop_lifecycle_e2e.py`.

## 3. The look, proved against the real bundle

One commit. Design D2, D4, D6.

- [ ] 3.1 Add the bundle-discovery helper of design D4 to
      `tests/test_shop_lifecycle_e2e.py`: `SHOP_E2E_VIEWER_BUNDLE` first (a
      value naming no file fails, it does not skip), then the installed
      `solid_node_viewer` package's `bundle.bundle_path()` /
      `bundle.api_version()` when the version is at least
      `REQUIRED_VIEWER_API`, then `skipTest` naming the env var and the version
      that was found. The test passes the bundle to the shop subprocess as
      `FAKE_SOLID_BUNDLE` and its version as `FAKE_SOLID_VIEWER_API`.
- [ ] 3.2 **Red** — write `test_model_panel_presents_the_viewer_navigator`
      against the navigator's published contract and the studio's overrides.
      The project's `.fake-solid-state.json` declares an assembly of pure
      structure — `format: "solid-node-export"`, `version: 1`, an `animation`
      block, and every node carrying `type`, `color`, `operations: []` and
      `children: []`, with NO `model` key anywhere (design D4: `operations` is
      walked unguarded and a `model` would fetch an STL the fake cannot write).
      Assert:
      - `role=tree` named `Assembly`; a row per node with `role=treeitem`;
      - the root row carries `solid-nav-row--root` and `aria-selected="true"`,
        and its computed `backgroundColor` is `rgb(28, 33, 40)`;
      - its computed `boxShadow` contains `rgb(79, 182, 184)` (the root mark);
      - `Expand housing` reveals `Visibility for pin`;
      - a coloured node's checked chip computes `rgb(204, 68, 68)`, a colourless
        one `rgb(107, 114, 128)`, and an unchecked one `rgba(0, 0, 0, 0)`;
      - `getComputedStyle(row).getPropertyValue('--solid-nav-focus-ring')` is
        `#e0a350`;
      - the keyboard contract moves and acts (Down, Right, Enter, Space) and the
        viewer follows — read it back through the page as
        `viewer.navigation()` is not reachable from the studio; assert instead on
        what the navigator redraws (`solid-nav-row--root` moving, the chip
        emptying);
      - `Show full assembly` appears in the navigator's toolbar only while a
        subtree is focused, and restores the root;
      - a republished document with a node removed leaves the panel usable and
        the removed row gone.
      Command (a skipped run is NOT evidence):
      ```
      SHOP_E2E_VIEWER_BUNDLE=/home/asa/devel/libresolid-studio/solid-node-viewer/WTs/viewer-navigator/solid_node_viewer/widget/dist/solid-widget.js \
        /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest \
        tests/test_shop_lifecycle_e2e.py -k presents_the_viewer_navigator -q
      ```
      Record the red: the colours are the navigator's neutral defaults, not the
      studio's.
- [ ] 3.3 **Green** — write the `--solid-nav-*` override block and the two
      class rules of design D2 into `floor/frontend/src/styles.css`, scoped to
      `.assembly-panel`, plus `.assembly-navigator-host { margin-top: 10px; }`.
      Every variable in D2's list is written explicitly, including ones that
      equal the navigator's current default.
- [ ] 3.4 Green run: 3.2's command with the bundle exported, and the same
      command WITHOUT it (it must skip with the message naming
      `SHOP_E2E_VIEWER_BUNDLE`, not error). Record both in `evidence.md`.
- [ ] 3.5 Take the pixel evidence the shop owes a UI change: a screenshot of the
      Model panel against the real bundle, beside one taken from the planning
      head, and say in `evidence.md` what differs (expected: the
      `Show full assembly` button moved from the header to the tree's toolbar;
      the twisty column is one pixel narrower; nothing else).
- [ ] 3.6 Commit: `styles.css` and the new e2e test.

## 4. The studio's own navigator is deleted

One commit. Nothing but removal; no behaviour may change.

- [ ] 4.1 Delete from `floor/frontend/src/main.tsx`: `AssemblyPanel`
      (`:295-440`), `assemblyRows`, `allAssemblyPaths`, `pathKey`, the
      `AssemblyRow` type, the `assembly` state (`:1710`), the
      `onAssemblyChange` prop on `FunctionalModel` and its three call sites
      (`:190`, `:219`, `:237`), and the four imports that become unused —
      `CSSProperties` and `KeyboardEvent` from `react` (`:3`, used only at
      `:395` and `:355`) and `AssemblyNode` and `AssemblyPath` from
      `./solid-node-widget` (`:10`). `ViewerHandle` and `ViewerView` stay; so do
      `AssemblyNode` and `AssemblyPath` inside the declaration file itself,
      where `ViewerHandle` needs them.
- [ ] 4.2 Delete from `floor/frontend/src/styles.css` the rules for
      `.assembly-tree`, `.assembly-row`, `.assembly-disclosure`,
      `.assembly-spacer`, `.assembly-visibility`, `.assembly-name`,
      `.assembly-root-label`, `.assembly-focus`, and `.assembly-panel > header`
      and its button rules (`:166-191`). Keep `.assembly-panel`,
      `.assembly-panel h2`, `.empty`, and increment 3's override block.
- [ ] 4.3 Confirm nothing else in the repository names the deleted DOM:
      `grep -rn "assembly-row\|assembly-tree\|focused-root\|assembly-visibility\|assembly-disclosure\|onAssemblyChange" floor tests docs`
      returns only the design reference's prose, if anything.
- [ ] 4.4 Green run: `npm --prefix floor/frontend run test`,
      `npm --prefix floor/frontend run build`, the full Python suite, and the
      real-bundle test with `SHOP_E2E_VIEWER_BUNDLE` exported. Counts in
      `evidence.md`, compared against 0.2's baseline.
- [ ] 4.5 Commit: `main.tsx`, `styles.css`, `tests/test_shop_lifecycle_e2e.py`.

## 5. The record

One commit. Design D7.

- [ ] 5.1 `docs/adrs/0030-the-model-panel-is-the-viewers-navigator.md` and its
      row in `docs/adrs/README.md` were written with the planning artifacts, at
      **Status: Proposed**. Re-read the ADR against what was actually built and
      correct any statement the implementation contradicted — its Decision and
      Consequences sections must describe the code that exists. Leave the status
      at Proposed; the reviewer promotes it.
- [ ] 5.2 If 5.1 changed the ADR's substance, say so explicitly in
      `evidence.md`, naming what the implementation contradicted.
- [ ] 5.3 Rewrite `docs/architecture-overview.md`'s Model-panel passage
      (`:459-464`, and the sentence about the Model context panel in
      `:466-480`) so it describes what is true: the browser mounts the viewer
      for the workspace AND mounts that viewer's own assembly navigator into the
      Model context panel, themed by the workspace's stylesheet through the
      viewer's published custom properties, holding no assembly state of its
      own. Rewrite the affected sentences; do not append a note.
- [ ] 5.4 `openspec validate adopt-the-viewer-navigator --strict` passes.
- [ ] 5.5 Commit: the ADR, the index row, the overview, `tasks.md` and
      `evidence.md`.

## 6. Handover

- [ ] 6.1 Do NOT sync specs, promote the ADR, archive the change, integrate the
      branch, push, or remove the worktree. Those belong to the reviewer.
- [ ] 6.2 Report: the commits made, the red-then-green evidence for each
      increment, the real-bundle run (with and without the env var), the pixel
      comparison, and anything found in the code that contradicts this plan.
