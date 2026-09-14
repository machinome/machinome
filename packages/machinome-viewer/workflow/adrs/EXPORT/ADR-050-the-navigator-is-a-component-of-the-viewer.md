# ADR-050: The assembly navigator is a component of the viewer package

**Status:** Accepted

**Date:** 2026-09-14

**Change:** `mount-the-navigator`

**Extends:**
- [ADR-049: The viewer publishes its assembly navigation state](ADR-049-the-viewer-publishes-its-navigation-state.md)
- [ADR-035: Reusable viewer core and declared API version](ADR-035-reusable-viewer-core-and-declared-api.md)

**Amends:**
- [ADR-042: Host-controlled viewer assembly navigation](ADR-042-host-controlled-viewer-assembly-navigation.md)

## Context

ADR-042 left the navigator to the host; ADR-049 published the state one
would need and recorded the pilot's decision that the navigator itself
becomes this package's. This record is the mechanism.

The only navigator that exists is the studio's React `AssemblyPanel`
(`floor/frontend/src/main.tsx:295-434` with `.assembly-*` in
`styles.css:166-191`), and it carries contracts this package owns:
effective colour inheritance, root-relative paths of sibling names,
`null`-versus-`[]` for the document root, and what survives a targeted
update. Every other host — the export page a maker opens from `solid
export`, a Sphinx page, anything embedding the bundle — has a breadcrumb
and no tree, and would have to write the same component again.

ADR-035 already answered the obvious shortcut: it rejected shipping a
React component "because the consumers span React 18, React 19, and no
framework at all". The widget's own chrome is therefore plain DOM
(`viewer.ts:1195-1345`) — but styled by `style.cssText` per element,
which is workable for a dozen fixed controls and not for a tree with
hover, focus, checked and per-level indent states that a host must be
able to restyle.

## Decision

**The assembly navigator ships inside the bundle as a plain-DOM
component, mounted into any host element from a viewer handle alone, and
themed by CSS custom properties behind a stable class contract.**

1. **One function, one handle.**
   `SolidNodeWidget.mountNavigator(target, viewer, options?)` draws the
   tree into an element the host supplies and returns a handle whose
   `dispose()` unsubscribes it and empties that element. It is given a
   `ViewerHandle` and nothing else: no assembly, no state, no callbacks.
   It renders synchronously — the handle can already answer every
   question, so no notification is needed to draw.

2. **It holds no copy of the viewer's state.** The focused root and the
   hidden set come only from `navigation()`, re-read from every
   `onAssemblyChange` payload. Expansion and the keyboard's active row
   are the navigator's own, per mount, because the viewer has no opinion
   about either and two navigators must be able to show different parts
   of one tree. Consequently a navigator, the widget's own breadcrumb
   and a host's own navigator can never disagree: they all read one
   published state.

3. **It observes and gestures, never both at once.** The subscription
   redraws; every call into the viewer comes from a maker's gesture.
   That is ADR-049's "a listener observes", honoured by the first
   component built on it.

4. **Hidden and obscured are different things on screen.** ADR-049
   published the *explicitly* hidden set rather than effective
   visibility; this is what that was for. A node hidden in its own right
   reads unchecked and empty; a node invisible only because an ancestor
   is hidden keeps its own checked state — so toggling it stays the
   exact inverse of what hid it — and its row is marked obscured, with
   the hiding ancestor named in the control's accessible name.

5. **Styling is a published contract, not an implementation detail.**
   One identifiable stylesheet is injected once per document; every
   element carries a stable `solid-nav-*` class; the palette and the
   metrics are CSS custom properties with a neutral default that reads
   on a light or a dark page. A host restyles by overriding properties
   and never by reaching into the DOM — which is how the studio puts its
   own look back on. A host under a policy that forbids inline style
   blocks suppresses the injection and serves the same rules itself.

6. **Not shadow DOM.** Encapsulation here would be bought by taking the
   theming away: a host's stylesheet could not reach in, every visual
   difference would need a `::part` or a property anticipated in
   advance, and the two things this component is tested on —
   `document.activeElement` and keyboard traversal — would have to cross
   a shadow boundary in every test. The class prefix is the
   encapsulation this component needs.

7. **Nothing new is published as a file.** The component and its
   stylesheet are inside `solid-widget.js`. `solid export` and the
   Sphinx directive copy the same two files, so this decision needs no
   framework change.

8. **The declared API version rises from 9 to 10.** A capability a host
   may require is added to the bundle — the navigator itself — which is
   ADR-035's rule for the number. 9 is the bundle that publishes the
   navigation state without a navigator; a host that means to present
   this package's navigator rather than build one gates on 10, and the
   studio will.

## Consequences

- Every host of the bundle gets a navigator, including the static export
  a maker opens with no host code at all — once the layout cycle mounts
  it there.
- The studio deletes `AssemblyPanel` and its CSS and mounts this one,
  keeping its look by overriding the published properties. Its
  behavioural spec shrinks to "the Model panel shows the viewer's
  navigator"; the behaviour itself is specified here.
- The class names and the custom properties are now a compatibility
  surface: renaming one breaks a host's theme silently, and the API
  version is the only thing a host can ask about it.
- The package gains a DOM test environment (jsdom, declared per test
  file) for the first time. It is scoped to the navigator's own test, so
  every other test goes on running in node.
- A component the package mounts is a component the package must keep
  accessible: tree roles, a single tab stop, a keyboard contract, and
  visibility that does not depend on colour are part of the contract,
  not of the styling.
- The bundle grows for every host, including those that never mount a
  navigator. A second published file would avoid that at the cost of a
  framework change in another repository; not worth it.

## Alternatives considered

**Ship a React component.** Rejected for ADR-035's own reason: the
consumers span React 18, React 19 and no framework at all. It would also
put the navigator out of reach of the export page, which is where a
maker with no host code meets the viewer.

**Shadow DOM for the component.** Rejected under decision 6: it blocks
the host theming that is the point of moving the navigator here, and it
complicates the focus and keyboard assertions this component lives or
dies by.

**Per-element inline styles, as the driver chrome does.** Rejected: no
`:hover`, no `:focus-visible`, no `:checked`, no per-level rule, and no
way for a host to change a colour without rewriting every element. The
chrome is not converted by this decision; it is simply not the model for
a tree.

**Leave the navigator in the host (ADR-042 unchanged).** The status quo:
one host has a navigator, everyone else writes one, and each
reimplements colour inheritance, path currency and reconciliation. The
pilot's decision settles the direction; this record settles the
mechanism.

**Publish the navigator as a second file (`solid-navigator.js` + a
`.css`).** It would keep the bundle small for hosts that do not want it,
and cost a change to what `solid export` and the Sphinx directive copy —
a framework change, in an Apache-2.0 repository, for an AGPL asset — for
a few kilobytes.

## References

- `solid_node_viewer/widget/src/navigator.ts` — `mountNavigator`, the DOM
  and the injected stylesheet
- `solid_node_viewer/widget/src/navtree.ts` — the rows, the keyboard
  transitions and the reconciliation, as pure functions
- `solid_node_viewer/widget/src/widget.ts` — the published global
- `openspec/changes/mount-the-navigator/`
- [ADR-020: Static export and embeddable, React-free viewer widget](ADR-020-static-export-and-embeddable-viewer-widget.md)
- [ADR-037: Targeted in-place viewer updates](../VIEWER-WEB/ADR-037-targeted-in-place-viewer-updates.md)
