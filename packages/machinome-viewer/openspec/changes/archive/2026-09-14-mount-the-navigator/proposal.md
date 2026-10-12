## Why

Cycle 1 published what a navigator has to read: `navigation()` and
`onAssemblyChange()` (`viewer.ts:145`, `:152`, ADR-049). Nothing reads
them yet. This cycle writes the reader — the tree a maker reads a
machine's parts off, focuses a subassembly from, and hides obstructing
parts in — as a component of **this** package, mounted from a handle and
nothing else.

The navigator exists already, in the studio
(`floor/frontend/src/main.tsx:295-434`, `styles.css:166-191`), as React
with its own `focused`/`hidden` mirror of the viewer's state. Three
things are wrong with it living there:

1. **It is a host's copy of a contract this package owns.** Colour
   inheritance, root-relative paths, the `null`-versus-`[]` root, what
   survives a targeted update — every one of those is decided here
   (`tree.ts:330-338`, `assembly.ts:64-78`, ADR-042, ADR-049) and
   re-implemented there.
2. **Only a React host can have it.** ADR-035 rejected shipping a React
   component because the consumers span React 18, React 19 and no
   framework at all; the consequence in practice is that the export page
   a maker opens from `solid export` has a breadcrumb and no tree, and
   anyone embedding the widget writes a navigator or goes without.
3. **It cannot see the widget move.** The driver chrome's breadcrumb
   moves focus from inside the widget (`viewer.ts:584-602`). Cycle 1
   made that visible; a navigator in this package is the thing that acts
   on it.

The pilot decided on 2026-09-14 that the navigator becomes this
package's. This cycle mounts it. It ships no layout and changes no
existing page: cycle 3 composes it into the export, and the shop cycle
deletes the studio's copy and mounts this one.

## What Changes

- **`SolidNodeWidget.mountNavigator(target, viewer, options?)`.** A
  React-free, plain-DOM navigator mounted into **any** element — a
  sidebar this package will ship, a studio panel, a maker's own page —
  given a target and a `ViewerHandle`. It returns its own
  `NavigatorHandle` with `dispose()`. It renders **synchronously** from
  `viewer.assembly()` and `viewer.navigation()`: no notification is
  needed to draw the first tree.

- **It carries the studio's behaviour, whole.** An accessible tree
  (`role="tree"` / `role="treeitem"`, `aria-selected`, `aria-expanded`,
  one tab stop with a roving `tabindex`); every node with its label, its
  depth and its effective colour; the selected row, the focused viewer
  root and the hidden subtrees marked separately; a visibility control
  with checkbox semantics per row — filled with the node's colour while
  shown, neutral gray when the node has no colour, empty with a border
  while hidden, the checked state and accessible name independent of
  colour; a per-row focus affordance; a "show full assembly" affordance;
  and the keyboard contract: Up/Down between rows, Right expands or
  enters, Left collapses or leaves, Enter focuses, Space toggles
  visibility.

- **It owns nothing the viewer owns.** Expansion and the active row are
  the navigator's, per mount. The focused root and the hidden set come
  **only** from `viewer.navigation()`, never from a copy the navigator
  writes beside its own calls. It subscribes with `onAssemblyChange` and
  redraws from the change payload, so a focus the breadcrumb moved, a
  host's `setRoot`, and a targeted update that reconciled state away all
  reach it by the same door. It calls back into the viewer only from a
  maker's gesture, never from inside the listener (ADR-049's rule).

- **It distinguishes hidden from obscured.** Cycle 1 published the
  *explicitly* hidden set precisely so this is possible: a node hidden
  on purpose reads unchecked and empty; a node that is invisible only
  because an ancestor is hidden keeps its own checked state and is
  marked obscured, in its class and in its accessible name.

- **One stylesheet, one class contract, CSS custom properties.** The
  bundle injects one identifiable `<style>` element per document, once,
  however many navigators mount. Every element carries a stable
  `solid-nav-*` class, and the palette and metrics are custom properties
  with a neutral default that reads on a light or a dark page. A host
  restyles by overriding variables, never by reaching into the DOM —
  which is how the studio will put its own look back on in the shop
  cycle. Not inline `cssText` (the driver chrome's way, `viewer.ts:1195`:
  it does not scale to a tree and cannot be themed) and not shadow DOM
  (it would block exactly that theming).

- **The declared API version rises from 9 to 10.** A capability a host
  may require is added — the navigator itself. The studio will gate its
  Model panel on `>= 10` in the shop cycle, and that number is what
  separates a cycle-1 bundle (state, no navigator) from this one.

- **No new published file.** `mountNavigator` and its stylesheet live
  inside `solid-widget.js`. The export directory still holds exactly
  `index.html` + `solid-widget.js`, so `solid export` and the Sphinx
  directive copy what they copy today and the framework needs no change.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-assembly-navigation`: six new requirements — the package
  mounts a navigator into any host element; a maker moves the viewer
  from it; its keyboard contract; it follows the viewer it was given;
  it disposes safely in either order; and it is styled by one
  host-themable stylesheet.
- `viewer-package`: one modified requirement — the declared API version
  becomes 10, for the capability added to the bundle.

Capabilities needing no delta:

- `viewer-distribution`: no published name, route or file changes. The
  bundle gains a global export, not a file.
- `development-server`, `snapshot-capture`: neither mounts a navigator.
  The capture page suppresses on-screen chrome deliberately
  (`capture.py:76-83`, `:153-162`) and mounts no navigator, so a photograph is
  unchanged.

## Impact

- `solid_node_viewer/widget/src/navtree.ts` (new) — the pure deciders,
  in the shape `controls.ts` established: the visible rows from an
  assembly plus an expansion set, the keyboard transition, the chip
  state of a row, and the reconciliation of navigator-local state
  against a republished tree. No DOM, so `navtree.test.ts` runs in the
  existing node environment.
- `solid_node_viewer/widget/src/navigator.ts` (new) — `mountNavigator`,
  the DOM it builds, the one injected stylesheet, and the gesture
  handlers that call the handle. Imports `viewer.ts` for **types only**,
  so its own test loads no renderer.
- `solid_node_viewer/widget/src/widget.ts` — exports `mountNavigator` on
  the `SolidNodeWidget` global beside `mount`.
- `solid_node_viewer/widget/package.json` — `solidNodeViewerApi: 10`,
  and `jsdom` as a dev dependency.
- `solid_node_viewer/widget/src/navigator.test.ts` (new) — the component
  itself, in a jsdom environment declared per file, so the existing 533
  tests keep running in node exactly as they do.
- `solid_node_viewer/widget/src/version.test.ts`,
  `tests/test_widget_e2e.py`, `tests/test_running_document.py`,
  `tests/test_bundle.py` — the four literal assertions of the API
  version.
- `tests/test_widget_e2e.py` — the keyboard scenarios, the
  breadcrumb-to-navigator agreement and a targeted update, against the
  real bundle in Chromium.
- `README.md`, `CHANGELOG.md` (the unreleased `0.2.0` row and section)
  and `docs/adrs/EXPORT/ADR-050-…` with its index row.
- **Consumed by** `ship-the-inspector-layout` (viewer cycle 3) and
  `adopt-the-viewer-navigator` (shop cycle 4). Nothing in this
  repository mounts it yet — that is cycle 3's job, and this component
  is correct or not on its own.

## Out of scope

Said plainly, because each is somebody else's cycle:

- **No layout.** No sidebar, no collapse, no composition of navigator +
  viewer + chrome in one target. Cycle 3.
- **No export-page change.** `index.html` is untouched; the page still
  mounts one viewer and shows a breadcrumb. Cycle 3.
- **No development-app change.** The CRA shell stays as it is. Cycle 3.
- **No studio change.** `AssemblyPanel` and its CSS stay where they are
  until the shop cycle deletes them.
- **No framework change.** The framework copies the same two files.
- **No new viewer handle API.** `navigation()` and `onAssemblyChange()`
  are what cycle 1 shipped; this cycle adds no method to `ViewerHandle`.
