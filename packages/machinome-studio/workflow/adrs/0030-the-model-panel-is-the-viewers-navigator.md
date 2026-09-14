# ADR 0030: The Model panel is the viewer's navigator

**Status:** Proposed

**Date:** 2026-09-14

**Origin:** `adopt-the-viewer-navigator`

## Context

The workspace's Model context panel showed an assembly tree the shop built
itself. `AssemblyPanel` in `floor/frontend/src/main.tsx` flattened
`viewer.assembly()` into rows, kept `active`, `focused`, `hidden` and
`expanded` in React state, reconciled all four against every republished tree,
implemented the roving tab stop and the Up/Down/Left/Right/Enter/Space contract,
and drove the renderer through `setRoot` and `setVisible`.
`floor/frontend/src/styles.css` painted it. The shop's `assembly-navigation`
capability specified every one of those behaviours.

It was built that way because the viewer had decided it should be. The browser
viewer package's ADR-042, "host-controlled assembly navigation", kept the
focused root and the hidden set inside the widget but exposed neither the state
nor a change notification, so any navigator had to be the host's, fed by the
host, and reconciled by the host.

The viewer has since reversed that. Its ADR-049 gives a mount handle
`navigation()` and `onAssemblyChange(listener)`, so a navigator holding only the
handle can draw and stay in sync with no host plumbing. Its ADR-050 ships
`SolidNodeWidget.mountNavigator(target, viewer, options)`: a React-free,
plain-DOM navigator that mounts into any element, carries the whole behaviour
the shop's capability described, and is themed through CSS custom properties on
a documented class contract. Its ADR-051 and ADR-052 additionally ship a
composed inspector layout — a collapsible sidebar, a rail and a toggle around
the viewer — for pages that have no layout of their own.

Two questions follow for this repository: which of those the studio adopts, and
what the studio still owns afterwards.

## Decision

**The Model panel mounts the viewer's navigator and specifies none of its
behaviour.**

- A small React wrapper gives `mountNavigator` a dedicated host element once a
  viewer handle exists, and disposes the returned handle when that viewer goes
  away or the component unmounts. The shop keeps no assembly state: no focused
  root, no hidden set, no expansion, no reconciliation. The `assembly` state and
  the `onAssemblyChange` plumbing through `FunctionalModel` are deleted with
  `AssemblyPanel` itself.
- **The theming seam is the viewer's published surface and nothing else.** The
  panel reproduces the reference design's Model panel by overriding the
  `--solid-nav-*` custom properties from the shop's own stylesheet, and by two
  colour rules on classes the viewer publishes for hosts to select
  (`solid-nav-badge`, `solid-nav-focus`) where one shared variable cannot carry
  two of the studio's accents. The shop does not reach into any element the
  viewer has not named, does not serve the navigator's structural CSS itself,
  and does not change the viewer to suit itself.
- **The studio does not use the viewer's inspector layout.** The studio already
  has a workspace — an activity rail, a context panel, a central area and a
  conversation column — and the inspector composes a competing one. The studio
  takes the navigator as a component and keeps its own layout; the inspector is
  for the export page, the development page, and a maker's own page.
- **"Show full assembly" is the navigator's.** The studio's header button is
  deleted rather than kept beside the navigator's own toolbar affordance.
- **The floor requires a viewer that can mount a navigator.** The preparation
  gate `REQUIRED_VIEWER_API` rises to 10 — the viewer API that introduced
  `mountNavigator`, not the newest build available — so a shop whose installed
  `solid-node-viewer` predates it refuses to open the project and names the
  required and installed versions, instead of opening onto a Model panel with
  nothing in it. The browser additionally checks the loaded bundle's
  `apiVersion` before it mounts anything.

## Consequences

- The shop is no longer a second authority for assembly-navigation behaviour.
  Its `assembly-navigation` capability shrinks to what the shop actually does:
  mount the viewer's navigator, wear the workspace's presentation, dispose it
  with the viewer, and hold no navigation state. Tree roles, colours, keyboard
  contract, checkbox semantics and reconciliation are specified once, in the
  viewer package.
- A capability the viewer adds to its navigator reaches the studio without a
  shop change — the same bargain `functional-model-inspection` already strikes
  for rendering ("solid-node improves how models are seen").
- A viewer change that alters the navigator's class contract or its custom
  properties is now a change the studio can see. Both are specified on the
  viewer's side, and the studio's stylesheet writes every value it depends on
  explicitly, including ones that currently equal the navigator's default, so a
  changed default cannot silently move the studio's look.
- The behavioural test of the Model panel can no longer run against the e2e
  fake framework's hand-written widget without testing the fake. It runs against
  a real bundle — named by `SHOP_E2E_VIEWER_BUNDLE` or discovered from the
  installed `solid_node_viewer` package — and skips, naming the reason, when
  none new enough is available. The fake keeps a minimal `mountNavigator` so
  every other end-to-end test still runs on it.
- Raising the gate to viewer API 10 is a real refusal: a workspace whose
  installed viewer is older cannot open a project until the viewer package is
  updated. That is deliberate, and it is what the shop already promises for a
  viewer it cannot use.
- Two pixel-level differences are accepted against the previous panel: the
  restore-the-full-assembly affordance sits in the navigator's toolbar above
  the tree rather than in the panel header, and the twisty column is sized from
  the same variable as the visibility chip.

## Alternatives considered

- **Keep the shop's own tree.** It works, and it would keep every pixel where it
  is. Rejected: it is 175 lines of behaviour specified twice, in two
  repositories, that can drift apart in ways only a maker would notice.
- **Adopt `mountInspector` and let the viewer own the panel's layout.**
  Rejected: the studio's workspace is its own product decision, specified by
  `shop-browser-workspace`, and the inspector's sidebar, rail and toggle would
  compete with the activity rail and context panel rather than fit inside them.
- **Mount the navigator with `styles: 'none'` and serve its whole class contract
  from the shop's stylesheet.** Rejected: it would hand the studio every pixel
  at the cost of owning a copy of the navigator's structural CSS — the same
  duplication moved to a new place, and silently stale after any viewer change.
- **Teach the e2e fake widget a navigator.** Rejected: a test asserting against
  a fixture's own tree proves nothing about the viewer the maker will run.

## References

- Viewer ADR-042 (host-controlled assembly navigation), ADR-049 (the handle
  publishes its navigation state), ADR-050 (the package mounts a navigator),
  ADR-051 and ADR-052 (the inspector layout), in the `solid-node-viewer`
  repository's own decision log.
- Viewer capabilities `viewer-assembly-navigation` and `inspector-layout`.
- Shop OpenSpec change `adopt-the-viewer-navigator`; capabilities
  `assembly-navigation`, `functional-model-inspection`,
  `shop-browser-workspace`.
- `docs/design/README.md`, "MODEL (1b)" — the reference design the panel
  reproduces, unchanged by this decision.
