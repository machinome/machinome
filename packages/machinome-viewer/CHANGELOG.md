# Changelog

All notable changes to Machinome Viewer. The Python package and the widget
it carries release together and share one version.

## Unreleased

- Draw a clocked handle gesture at the tempo of the first `by` instruction
  naming its input, scaled to admitted travel. Use the existing 0.2-second
  duration when no instruction declares a travel. Pressed instructions keep
  their declared duration. (ADR-073; integrated from the earlier Curta cycle.)
- Preserve source-motion timing through running chains and selected blocks,
  fixing Curta carry loss when later result stations join the graph. Range
  and moving-contact probes use the same path as the committed bank.
- Declare API 24 and document versions 1–11. Re-export running models with the
  paired corrected producer; old viewers reject v11 before operation.
- Refuse distribution builds through symlinked `node_modules` before an
  install can modify another checkout's dependencies.

## 0.7.0 — 21 September 2026

The first published release of Machinome Viewer, released with Machinome
0.7.0 and numbered with it. It declares viewer API 23 and reads document
versions 1 through 10. Install both with `pip install "machinome[viewer]"`.

### What a maker gets

- **A machine in the browser.** Orbit, pan and zoom a published model; open
  the assembly navigator to expand, focus, hide and show parts, by pointer or
  keyboard; collapse it into the inspector's sidebar. The same bundle powers
  the framework's development page, with live reload and a build-error pane
  over the last good model, the self-contained export page, custom embeds and
  headless capture.
- **Posed models.** Sliders and exact-value readouts for declared drivers,
  instruction buttons, and an animation timeline that plays a declared loop
  in real time with a speed control.
- **Running machines.** Movement and rate requests, nudge and jog, named
  instructions, and run, pause, step and reset, executed in a Web Worker in
  fixed ticks. Every request reports its outcome, completed, blocked with the
  travel admitted, refused or cancelled. Snapshot, restore and bounded
  recording. The engine executes what Machinome publishes: laws that read the
  coordinate they drive, blocks whose order a part's position selects, bounds
  that read other coordinates, `Play` clearance laws and explicit time drives
  (document versions 5 to 7, 9 and 10), reproducing the framework's
  conformance corpus bit for bit.
- **Clocked machines** (document version 8). One request per gesture, solved
  at once: stops clip the request, events commit in path order, states are
  read-only readouts. A pressed instruction is drawn over its declared
  duration, a handle gesture over a fifth of a second. A declared elapsed
  clock gets play, step and speed.
- **Touching the parts.** A model that declares `Button`, `Turn` or `Slide`
  controls makes those parts pressable and draggable, one request per
  gesture, the part following what the machine commits.
- **Markings.** Digits and other markings a part carries are drawn on its
  surface, so a calculator's dials can be read.

### What a host gets

- `MachinomeViewer.mount`, `mountInspector`, `mountNavigator` and
  `mountDevelopment`, each returning a handle with the camera, assembly,
  timeline, driver, instruction, running and clocked operations the manual
  documents, plus `setView` and an on-demand render mode for scripted stills.
  Stable CSS classes and custom properties for the navigator and inspector.
- `machinome-viewer describe|serve|capture`: the version, API and document
  versions as JSON; a development server for a published build; a headless
  PNG capture. A source checkout rebuilds a stale bundle when its build tools
  are present and refuses what it cannot repair.
- One bundle, `machinome-viewer.js`, with the browser global
  `MachinomeViewer` and the `data-machinome-widget` declarative mount. New
  documents are `machinome-export`; historical `solid-node-export` documents
  still load.

### Corrections carried into the release

- Moving-contact stops act at their first located contact, so a long request
  stops at the first obstruction rather than a later free window; a landing
  on a moving threshold follows the parts' relative motion; exact following
  contact is certified rather than rounded into a false departure.
- The navigator shows full part names on hover and keeps its scroll and
  keyboard focus while rows are toggled.
- Large control panels stay in a side rail with internal scrolling instead
  of covering the model.

### Identity and licensing

- Package `machinome-viewer`, import `machinome_viewer`, entry point
  `machinome.viewer`, licensed AGPL-3.0-only. The framework, Apache-2.0,
  reaches it only through that entry point and separate processes; neither
  package imports the other. The widget ships inside the Python
  distribution and is not published on npm.
- The version number identifies the distribution; capability is declared by
  `apiVersion` and `documentVersions` alone. Development states 0.1.0 and
  0.2.0 were never published; their detailed history is in
  [workflow/archive/changelog-before-0.7.md](workflow/archive/changelog-before-0.7.md).
