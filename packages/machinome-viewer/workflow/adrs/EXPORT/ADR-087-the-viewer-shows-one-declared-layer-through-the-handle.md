# ADR-087: The viewer shows one declared layer through the handle's `show`, as a third input to the one visibility decision

**Status:** Accepted

**Date:** 2026-11-23

**Change:** [show-only-a-layer](../../../openspec/changes/archive/2026-11-23-show-only-a-layer/) (design Decisions 2-8)

**Builds on:** [ADR-084](ADR-084-a-models-app-is-a-script-the-viewer-starts-inside-mount.md)
(the app is the page's control surface), [ADR-085](ADR-085-a-clocked-machine-notifies-a-page-on-the-mount-handle.md)
(the handle notifies a page); the framework's ADR-201 and ADR-202 (what a document declares and carries)

## Context

Originating project: `projects/enigma-i`, whose app is to show the whole
machine, only the electrical path or only the parts that move the rotors. The
framework's document now carries each node's declared layer keys and a
top-level table. One function, `WidgetTree.applyVisibility`, writes every
`visible` flag, and everything that acts on visible parts reads those flags:
the pick, `partOnScreen`, framing, hover and the control affordance. The
navigator already holds two inputs to it, the focused root and the hidden
paths. The pilot ruled that the viewer presents no layer control of its own:
the model's app adds its own.

## Decision

**The handle gains `layers()`, `layer(key)` and `show(layer | null)`.**

1. **Reading.** `layers()` returns a frozen array of frozen `{key, label}`
   objects, the same array until a document whose list differs is installed;
   `[]` for a document declaring none. `layer(key)` answers from it and an
   unknown key throws naming the layers the document does declare. A method,
   not a property per key: a missing property reads `undefined`, the silent
   answer excluded, and an object that throws on a probe breaks React's
   development checks and debuggers. A malformed `layers` (a node naming a
   key the table does not list, a repeated key, an empty string) refuses the
   document by name; a top-level layer no node names is accepted.
2. **`show` takes one layer or `null`.** A layer is matched by key, so one
   kept from before a republish still works while the document declares it,
   and `show(navigation().layer)` restores what was read. A string, an
   unknown key, or a call before a tree is loaded is refused and changes and
   notifies nothing. An accepted call applies, draws once and notifies
   `onAssemblyChange` once, a redundant call included; it does not move the
   camera.
3. **A third input to the one decision.** `AssemblyNavigation` holds the
   shown key beside the focused path and the hidden paths and passes it to
   `applyVisibility(focusedPath, hiddenPaths, layer)`. A node's own surface
   and its decals are drawn when it is in the focused subtree and on the
   layer; its group is visible under today's rule and when it or a node
   below it is on the layer, which spares a subtree with nothing on it and
   draws the same pixels. A part off the layer therefore behaves as absent
   for the pick, `partOnScreen`, framing and the control affordance; its
   declared controls stay in `controls()`. A flexible part is evaluated
   whatever its visibility.
4. **Conjunction with focus and hiding.** A part is drawn only when the
   focus includes it, no hidden path covers it, and the shown layer holds
   it. `show` never changes focus or hidden paths, and `setRoot` and
   `setVisible` never change the shown layer, so neither silently undoes
   the other. `navigation()` gains `layer: Layer | null`, `hidden` still
   lists only explicitly hidden paths, `assembly()` reports each node's
   effective `layers` in the document's order, and `onAssemblyChange`
   delivers both.
5. **The navigator reports, and does not control.** A row neither of whose
   node nor descendants is on the shown layer is marked with the class of a
   row under a hidden ancestor, its visibility control keeps the node's own
   setting and its accessible name says `not on the shown layer <label>`.
   The navigator has no control that shows or switches a layer, and the
   viewer presents none anywhere (posed, running or clocked panels, the
   inspector, the export page).
6. **A republish** keeps the shown key when the new document still declares
   it and resets to the whole machine otherwise, reporting it in the one
   notification of the update; effective sets are recomputed in the same
   reconcile.
7. **The app reads the layers through the helper.** `useMachine()` returns
   `{bank, drawing, layers}`; the store reads `viewer.layers()` beside the
   bank and compares it by identity, which changes exactly when the list
   does. `useViewer()` supplies `layer(key)` and `show`, in any app, clocked
   or not; `useMachine()`'s refusal of an unclocked model is unchanged.
8. **API 32.** `machinomeViewerApi` is 32 (the app's gate restated "31 or
   later"); document versions stay 1 to 14, the fields being additive.

### Departures recorded in the change's evidence

- `WidgetTree` takes a trailing `layerScope` (`{order, inherited}`) so each
  node reports its layers in the document's order; `AssemblyNavigation`'s
  `reconcile(tree, layers)` and a new `setLayer(tree, layer)` hold the
  object, so `state()` needs no table.
- `NavigatorRow` gains `outsideLayer`; `hidingAncestor` stays null for a row
  obscured only by the layer; the label for both causes reads `hidden with
  G, not on the shown layer L`.
- V5's pick check goes through `partOnScreen(...).point`, since the handle
  has no pick-at-point.

## Alternatives

- **A list of layers to show:** adds a union rule, a list-valued state and a
  meaning for the empty list that no page uses; accepting an array later is
  additive.
- **three.js `Object3D.layers` and a camera mask:** the raycaster tests it,
  but `visibleBounds`, `partOnScreen` and the navigator read `visible`, so
  two mechanisms would have to agree.
- **A second function beside `applyVisibility`:** two writers of one flag.
- **A viewer-made layer control:** ruled out by the pilot.

## Consequences

- A page shows one layer with one call and learns it changed from the one
  notification it already receives.
- The navigator's focus and hiding and the shown layer never override each
  other, and each read reports its own state.
- Ghosting or dimming a layer, several layers at once and a layer chosen in a
  URL or mount option remain unbuilt, as no project asks for them.

## Proof

`src/layers.test.ts` (V1 to V7), `src/navtree.test.ts` (N1 to N3),
`app/app.test.tsx` (H7), `tests/test_documentation.py`.
