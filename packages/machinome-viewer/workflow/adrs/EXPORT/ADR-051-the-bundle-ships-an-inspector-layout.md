# ADR-051: The bundle ships an inspector layout, and the page selects it

**Status:** Accepted

**Date:** 2026-09-14

**Change:** `ship-the-inspector-layout`

**Extends:**
- [ADR-050: The assembly navigator is a component of the viewer package](ADR-050-the-navigator-is-a-component-of-the-viewer.md)
- [ADR-035: Reusable viewer core and declared API version](ADR-035-reusable-viewer-core-and-declared-api.md)
- [ADR-020: Static export and embeddable viewer widget](ADR-020-static-export-and-embeddable-viewer-widget.md)

## Context

ADR-050 put a navigator in the bundle and mounted it nowhere. It needs a
host element beside the viewer, and this package ships no page that has
one: the export page is a single full-bleed container
(`widget/index.html:22`) and the development page is a React shell whose
only job is to call `mount`. The maker ADR-020 exists for — someone with
a `solid export` directory, a browser, and no host code — still gets a
breadcrumb and no tree.

Every host that wants the tree therefore has to lay out a sidebar, a
viewer and a toggle, and get right the one thing that is easy to get
wrong: the viewer takes its container over. `mount()` sets
`position: relative` on it, appends its canvas and its chrome into it,
observes it, and calls `replaceChildren()` on it when disposed
(`viewer.ts:214`, `:225`, `:768`, `:821`). A sidebar placed in the same
element disappears the moment the viewer is disposed.

And the export page is copied verbatim by another repository: `solid
export` copies `index_path()` and `bundle_path()`
(`solid_node/core/export.py:176-178`) and the Sphinx directive completes
an export from `WIDGET_FILES = ('index.html', 'solid-widget.js')`
(`solid_node/sphinx.py:50`). Whatever the page grows must fit in those
two files, under those two names.

## Decision

**The bundle carries a layout that composes the navigator, the viewer and
its chrome into one host element, and the standalone page selects it by an
attribute whose absence means the plain viewer.**

1. **One call, one element, two handles.**
   `SolidNodeWidget.mountInspector(target, sourceUrl, options?)` is async
   like `mount`, builds a rail, a sidebar and a viewer pane inside the
   target, mounts the viewer on the **pane** and the navigator in the
   **sidebar**, and resolves to a handle that *exposes* the viewer handle
   and the navigator handle rather than wrapping them. Wrapping would
   mean forwarding a 25-member interface that grows every cycle, and a
   member forgotten is a capability a host silently cannot reach.

2. **Options extend the viewer's.** Everything `mount` takes, plus
   `sidebar: 'collapsed' | 'open'` and a nested `navigator` block. Nested,
   because `className` means the canvas to the viewer and the tree's root
   to the navigator, and one flat bag could not mean both.

3. **The sidebar is a disclosure that remembers nothing.** A labelled,
   keyboard-operable toggle with `aria-expanded` and `aria-controls`,
   living in a rail that is present in both states — so the element
   holding focus is never destroyed by using it. No storage, no cookie, no
   URL rewriting: an export directory is a static artifact, and a
   remembered sidebar in one documentation `<iframe>` would silently
   change every other embed on the same origin.

4. **Collapsing removes the sidebar from layout, and the viewer resizes
   itself.** The sidebar is a flex sibling that is hidden, not an overlay,
   so the model is never covered and the viewer's pane actually changes
   size — which fires the `ResizeObserver` `mount()` already installs on
   its container (`viewer.ts:757-769`). The layout writes no resize code,
   listens to no event and calls nothing on the handle.

5. **Styling repeats ADR-050's contract exactly.** One identifiable
   `<style>` injected once per document, a `solid-inspector-*` class
   contract, CSS custom properties for width and palette with neutral
   defaults legible on a light or a dark page, and `styles: 'none'` for a
   page under a Content-Security-Policy — which also becomes the default
   for the navigator's own stylesheet, so one option covers the page.

6. **The page selects a layout, and its absence means the plain viewer.**
   `data-solid-layout="inspector"` on the same container that carries
   `data-solid-widget`, with `?layout=` and `?sidebar=` as query-string
   twins that take precedence — the attribute is what a page ships with,
   the query string is what a link asks for, and the query string is the
   only channel a Sphinx directive or an `<iframe src>` can reach. A
   container with no selection mounts exactly what it mounts today, so
   every hand-written embed and every already-published export is
   untouched. An unrecognised value is refused by name in the container,
   never silently ignored.

7. **Nothing new is published as a file.** The layout and its stylesheet
   are inside `solid-widget.js`; `index.html` keeps its name and gains one
   attribute. The framework copies the same two files and needs no change.

8. **The declared API version rises from 10 to 11.** A capability a host
   may require is added — the composed layout — and 10 is the bundle that
   carries a navigator with nowhere to put it.

## Consequences

- A maker who opens a `solid export` directory gets the tree, with no host
  code and no framework, which is the first time that has been true.
- `data-solid-layout` joins `solid-widget.js`, `data-solid-widget`,
  `SolidNodeWidget` and the `/_viewer` and `/build/` routes as a
  compatibility name this package may not rename quietly.
- `solid-inspector-*` and its custom properties are a second theming
  surface beside the navigator's, with the same silent-breakage risk and
  the same mitigation: documented in the README, gated by the API version.
- A host wanting a different arrangement still has `mount` and
  `mountNavigator` and loses nothing; the layout is an offer, not a
  funnel. The studio, in particular, keeps its own layout.
- The bundle grows for every host, including the capture page, which
  mounts neither the layout nor the navigator. Same trade ADR-050 took: a
  second file would cost a framework change in an Apache-2.0 repository
  for an AGPL asset.
- The layout's own test needs a seam: `mount()` cannot run in jsdom, so
  the module takes `mount` and `mountNavigator` through an internal
  entry the test stubs, and the real wiring is proved in Chromium.

## Alternatives considered

**A second published page, `inspector.html`.** It would need a third name
in `WIDGET_FILES` and in `export.py` — a framework change, in another
repository, to say what one attribute says.

**Make the inspector the default and let a page opt out.** It would change
what every already-published export shows the moment someone upgrades the
viewer that completes it. The compatibility promise is worth more than the
nicer default.

**Let the viewer itself grow a sidebar** (a `navigator: 'inline' | 'none'`
option beside `driverControls`). It would put a tree inside the element
the viewer clears on dispose, make `viewer.ts` depend on `navigator.ts`
and so drag the renderer into the navigator's own test, and give a host no
way to place the tree anywhere but over the canvas.

**Wrap the handles instead of exposing them.** Rejected in decision 1.

**Let the sidebar remember its state.** Rejected in decision 3.

**Animate the collapse.** A width transition fires the ResizeObserver
dozens of times, each resizing a WebGL renderer, for a flourish nobody
asked for.

## References

- `solid_node_viewer/widget/src/inspector.ts` — `mountInspector`, the
  layout DOM and the injected stylesheet
- `solid_node_viewer/widget/src/widget.ts` — the published global and the
  auto-mount's layout selection
- `solid_node_viewer/widget/index.html` — the shipped page
- `openspec/changes/ship-the-inspector-layout/`
- [ADR-042: Host-controlled viewer assembly navigation](ADR-042-host-controlled-viewer-assembly-navigation.md)
- [ADR-049: The viewer publishes its assembly navigation state](ADR-049-the-viewer-publishes-its-navigation-state.md)
- [ADR-052: The development page is a static page over the bundle](../VIEWER-WEB/ADR-052-the-development-page-is-static.md)
