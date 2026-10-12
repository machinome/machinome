## Why

The shop built its own assembly tree because the viewer had none: ADR-042 in
the viewer package made the HOST own the navigator UI, so
`floor/frontend/src/main.tsx` grew `AssemblyPanel` (lines 267-440) and
`floor/frontend/src/styles.css` grew its `.assembly-*` rules (lines 166-191) —
roughly 175 lines of tree flattening, expansion, roving tab stops, keyboard
handling and visibility state that duplicate what the renderer already knows.

The viewer package has just taken that back. Its cycles
`observe-assembly-navigation` (ADR-049, viewer API 9) and `mount-the-navigator`
(ADR-050, viewer API 10) give a handle `navigation()` and `onAssemblyChange()`,
and ship `SolidNodeWidget.mountNavigator(target, viewer, options)` — a
React-free, plain-DOM navigator that mounts into any element, carries the whole
behaviour this shop's `assembly-navigation` spec describes, and is themed
entirely through CSS custom properties on `.solid-nav`. The shop can now show
the maker the viewer's own navigator instead of a copy of it, and stop being a
second place where a keyboard contract or a visibility rule can drift.

## What Changes

- The Model context panel mounts the viewer package's navigator through
  `window.SolidNodeWidget.mountNavigator`, inside a small React wrapper that
  owns a ref and an effect and holds no assembly state of its own.
- `AssemblyPanel`, `assemblyRows`, `allAssemblyPaths`, `pathKey`, the workspace's
  `assembly` state, the `onAssemblyChange` prop threaded through
  `FunctionalModel`, and every `.assembly-row`/`.assembly-tree`/
  `.assembly-visibility`/`.assembly-focus`/`.assembly-disclosure` rule are
  deleted.
- The panel's look is unchanged: `styles.css` reproduces today's Model panel by
  overriding the navigator's documented CSS custom properties, and never by
  reaching into its elements beyond the two colour rules its published class
  contract invites.
- `Show full assembly` becomes the navigator's own toolbar affordance
  (`fullAssembly: true`); the studio's header button goes.
- **BREAKING (for an installed viewer older than the navigator):**
  `REQUIRED_VIEWER_API` rises from 4 to 10, so a shop whose installed
  `solid-node-viewer` predates `mountNavigator` refuses to open a project and
  says so, exactly as it already does for a missing viewer.
- `floor/frontend/src/solid-node-widget.d.ts` is re-vendored from the viewer
  package at API 11 (the version built in this workspace), declaring API 10 as
  the version the studio requires: the `ViewerHandle` surface the studio uses
  plus `navigation()`, `onAssemblyChange()`, `mountNavigator`,
  `NavigatorOptions` and `NavigatorHandle`.
- The e2e fake framework's widget reports API 10 and gains a minimal
  `mountNavigator` that records the call and draws an empty labelled tree host —
  enough for every test that only needs the panel to exist, and deliberately not
  a second implementation of the tree.
- The Model-panel navigation test runs against a REAL viewer bundle, discovered
  from `SHOP_E2E_VIEWER_BUNDLE` or from the installed `solid_node_viewer`
  package, and skips with a named reason when no new-enough bundle is available.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `assembly-navigation`: the panel's own tree, keyboard contract and
  reconciliation rules are replaced by one requirement that the Model panel
  presents the viewer's navigator, themed to the reference design and disposed
  with the viewer, and one that the panel reflects the viewer after an update
  without the shop holding navigation state.
- `functional-model-inspection`: the viewer the floor requires is one that
  mounts its own assembly navigator over a mounted model.
- `shop-browser-workspace`: the Model context panel's assembly navigator is the
  viewer package's, not the shop's.

## Impact

- `floor/frontend/src/main.tsx` — `FunctionalModel` loses `onAssemblyChange`;
  `AssemblyPanel` and its helpers are replaced by an `AssemblyNavigator`
  wrapper; the workspace loses its `assembly` state; `loadViewer` gains an
  API-version check.
- `floor/frontend/src/styles.css` — the `.assembly-*` rules become the panel
  shell plus one block of `--solid-nav-*` overrides.
- `floor/frontend/src/solid-node-widget.d.ts` — re-vendored.
- `floor/preparation.py` — `REQUIRED_VIEWER_API = 10`.
- `tests/fixtures/fake_solid.py`, `tests/test_project_preparation.py`'s inline
  fake — API 10, minimal `mountNavigator`, `FAKE_SOLID_VIEWER_API` honoured.
- `tests/test_shop_lifecycle_e2e.py`, `tests/test_project_open.py`,
  `tests/test_project_preparation.py` — the Model-panel tests and the three
  API-version assertions.
- `docs/adrs/0030-the-model-panel-is-the-viewers-navigator.md` (new),
  `docs/adrs/README.md`, `docs/architecture-overview.md`.
- No framework change, no viewer change. `docs/design/README.md` does not
  change: the look is unchanged.
