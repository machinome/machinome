## Context

How the viewer decides what is drawn today: one function, `WidgetTree.applyVisibility(focusedPath, hiddenPaths)` (`src/tree.ts` 752-778), writes every `visible` flag. A node's group is visible when the node is in the focused subtree or is an ancestor that carries its transform, and no explicitly hidden path covers it; its own surface (the direct `Mesh` children of its group: the model's mesh, a flexible part's mesh) and its decals are drawn only inside the focused subtree. It raises the picture first (`this.presentation.picture.raise()`, 755), so the draw-only-when-the-picture-changes rule redraws once. `AssemblyNavigation` (`src/assembly.ts` 25-80) holds the two inputs, applies them on `setRoot`, `setVisible` and `reconcile`, and reports them through `navigation()`; the handle's `setVisible` (`src/viewer.ts` 2877-2883) applies, draws (`drawPicture`) and notifies (`notifyAssemblyChange`, 549-556).

Everything else that acts on visible parts reads those flags, so it follows whatever `applyVisibility` decides: the pick (`nearestVisibleMesh`, `viewer.ts` 917-933, filtering with `visibleUpTo`, `src/partControls.ts` 668-683, because three.js's raycaster ignores `visible`), `partOnScreen` (1131-1157, the same filter), framing (`applyFrame` 1272 over `visibleBounds` 3539-3556, which skips an invisible object), the hover and the control affordance (through the pick). The highlight swaps materials and leaves visibility alone (`viewer.ts` 373-379); shared materials and geometries (`share-one-material-per-appearance`, `share-one-geometry-per-model-file`) are per mesh and are not touched by a `visible` flag. A flexible part is evaluated per frame whatever its visibility (`src/flexible.ts` reads no `visible`), as a part the navigator hides is today.

A node's colour is the precedent for something declared on a node and inherited by its subtree: the document carries the node's own `color`, and `WidgetTree` passes its own `colorSpec` to each child (`tree.ts` 294, 306, 332) and again in a reconcile (429-459, 508, 548). `assembly()` reports each node's effective colour (`tree.ts` 718-726; spec "A viewer host can inspect the rendered assembly").

The navigator (`src/navigator.ts`, rows decided in `src/navtree.ts` 80-150) follows the handle through `onAssemblyChange` and renders what `assembly()` and `navigation()` give it: a row is `hidden` by its own key and `obscured` when a proper ancestor is hidden, its visibility control keeping the node's own setting and naming the hiding ancestor (`chipState`, 163-170; style `.machinome-nav-row--obscured`, `navigator.ts` 150-151, 305). The Studio and the Enigma's public page both mount this navigator (`packages/machinome-studio/.../frontend/src/main.tsx` 305-306; `projects/enigma-i/tools/machine/page/index.html` 389-390, `sidebar: 'open'`), so on the Enigma's page the navigator stands beside the app that will switch layers.

A model's app reaches the viewer only through the mount's handle (`model-app` "An app operates the machine through the mount's handle"); the helper's `useMachine()` re-reads on every `onMachineChange`, which a republish also fires (`app/index.tsx` `MachineStore`; archived `show-a-models-own-app` design Decision 6), and refuses a model that is not a clocked machine.

Two other things in the viewer are called "layer": the spec's "focused layer" (`viewer-package` "Controls follow the focused layer": the focused assembly level whose drivers the panel presents) and the source's `controlLayer`/`clockedControlLayer` (the panel's control stack); three.js's `Object3D.layers` is a camera mask. None of them is touched or reused here; the manual says "layer" for this capability only where it means the model's declared layers.

## Goals / Non-Goals

**Goals:**

- The Enigma's app can show the whole machine, only the electrical layer or only the mechanical layer, with one call each, from objects the viewer hands it.
- A part the shown layer leaves out behaves as absent for everything the viewer does with visible parts.
- Neither the shown layer nor the navigator's focus and hiding silently overrides the other, and the navigator says which rows the shown layer leaves out.
- A document without layers is mounted exactly as today.

**Non-Goals:**

- Showing several layers at once; ghosting, dimming or any opacity; an automatic panel or any viewer-made layer control; generated typed names; a layer chosen by a rule; a movie or videomaker integration; a URL or mount option selecting a layer.

## Decisions

### 1. Reading the document's layers

The wire contract is the companion's requirement "A document carries a model's layers", restated word for word in this change's `layers` spec. Types (`src/types.ts`): `ManifestLayer { key: string; label: string }`, `Manifest.layers?: ManifestLayer[]`, `ManifestNode.layers?: string[]`.

Validation, on `assertRenderable`'s refusal surface beside the markings check (`viewer.ts` 3637-3700, called from `assertRenderableScoped` 3897): `layers`, when present, is an array of objects each with a non-empty string `key` and a non-empty string `label`, no key twice; a node's `layers`, when present, is an array of strings, none twice, each a key of the top-level list. Anything else refuses the document by name ("the document's `layers` …", "node `<path>` names the layer `x`, which the document's `layers` does not list"), because it is a producer error and not a model to show part of; a node naming a key with no top-level list at all is the same refusal. A top-level layer no node names is accepted (showing it shows nothing). The fields are gated on no document version: they are additive (companion design Decision 5), and an older viewer, which validates no unknown key (`assertRenderable`, `loadDocument`), draws the whole machine.

**Effective layers.** `WidgetTree` takes the parent's effective set beside `inheritedColor` (constructor 294-332, `prepareReconcile` 456-548) and keeps `effectiveLayers = parent ∪ own`, a `ReadonlySet<string>`, replaced on every reconcile like `colorSpec`, so a republish that changes a node's keys changes what it is on. A document with no `layers` gives every node the empty set and takes no new path.

### 2. The handle: `layers()`, `layer(key)`, `show(layer | null)`

```ts
export interface Layer { readonly key: string; readonly label: string; }

interface ViewerHandle {
  /** The document's layers, in its order; [] for a document declaring none. */
  layers(): readonly Layer[];
  /** The layer the document declares under `key`; an unknown key throws naming it. */
  layer(key: string): Layer;
  /** Show only the parts on `layer`, or the whole machine for null. */
  show(layer: Layer | null): void;
}
```

`layers()` returns a frozen array of frozen objects, the same array and objects until a document whose list differs (a key or a label, or the order) is installed, so an app that keeps one in React state or compares identities sees a change only when there is one. `layer(key)` answers from that array; an unknown key throws `Unknown layer 'x': this document declares the layers electrical, mechanical` (or `… declares no layer`), in the style of `requirePath`'s `Unknown assembly path` (`tree.ts` 735-746) and the clocked machine's refusal of an undeclared instruction. A method, not a property per key (the brief's `layers.electrical`): a property that does not exist reads `undefined` in JavaScript, which is the silent empty answer the pilot excluded, and an object that throws on an unknown property breaks every tool that probes one (React's development checks, `JSON.stringify`, debuggers).

`show(layer)`:

- `null` shows the whole machine.
- An object whose `key` is a key the loaded document declares shows only the parts on that layer. It is matched by key, not by identity, so a layer an app kept from before a republish still works while the document declares it, and `show(navigation().layer)` restores what was read (Decision 5).
- A string is refused: `show() takes a layer from layers() or layer(key), or null; it was given the string 'electrical'`; an unknown key is refused with `layer`'s sentence; before a tree is loaded the refusal is `setVisible`'s (`Viewer assembly is unavailable`). A refusal changes nothing and notifies nobody.
- An accepted call applies (Decision 4), draws (`drawPicture`) and notifies `onAssemblyChange` once, as `setVisible` does, a redundant call included (spec "A host is told when the assembly or its navigation changes": "an accepted operation that leaves the state as it found it SHALL still notify"). It does not move the camera, as hiding does not; a later framing (focusing, a reload that frames) counts only what is drawn.

### 3. One layer at a time, not a list

`show` takes one layer or `null`. The Enigma switches between three views, each one layer or the whole machine. A list would add a union to the visibility rule, a list-valued state to `navigation()` and a set to the navigator's rows, and a meaning for the empty list, none of which any page uses; it is not the same operation for free. Accepting an array later would be additive to this signature.

### 4. What is drawn: a third input to the one function that decides

`AssemblyNavigation` holds the shown layer's key (`null` by default) beside the focused path and the hidden paths, and passes it to `applyVisibility(focusedPath, hiddenPaths, layer)`. With `L` the shown key, `on(n)` "`L` is null or in `n`'s effective layers" and `holds(n)` "`on` holds for `n` or a node below it":

- a node's own surface (its direct meshes, its flexible mesh) and its decals are drawn when it is in the focused subtree **and** `on(n)`;
- its group is visible when, as today, it is in the focused subtree or carries the focused node's transform and no hidden path covers it, **and** `holds(n)`.

The second term only spares the draw a subtree with nothing on the layer: it draws the same pixels as the first alone. Because every other act on visible parts reads these flags (Context), a part off the shown layer is not drawn, carries no drawn decal, is not reached by a press, a hover or `partOnScreen`, is not counted by framing, and the picture is raised once per `show` and drawn once; a still page draws nothing. A declared control on such a part stays in `controls()` (the full listing, `viewer-package` "A host reads the controls a document's parts carry") and is not reachable on screen. Materials, shared or highlighted, and geometries are not touched. A flexible part off the layer is evaluated per frame as a hidden one is, so showing the whole machine again draws it current.

Alternatives rejected: three.js `Object3D.layers` and a camera mask (the raycaster tests `layers`, but `visibleBounds`, `partOnScreen`'s filter and the navigator read `visible`, so two mechanisms would have to agree); a second function beside `applyVisibility` (two writers of one flag, the failure the navigator's design avoided).

### 5. Composition with the navigator's focus and hiding

The three inputs are independent and the result is their conjunction: a part is drawn only when the focus includes it, no explicitly hidden path covers it, and the shown layer holds it. `show` never changes the focus or the hidden paths; `setRoot` and `setVisible` never change the shown layer. So `setVisible(path, true)` on a part the shown layer leaves out records that the maker has not hidden it and draws nothing, and `show(null)` then draws it; hiding a part under the shown layer hides it, and `show(null)` keeps it hidden. Neither can silently undo the other, and each read reports its own state:

- `navigation()` gains `layer: Layer | null` (a copy of `{key, label}`), beside `root` and `hidden`; `hidden` still lists only the explicitly hidden paths, so a part hidden by the layer is never listed there. The `AssemblyNavigationState` type gains the field; the reported layer is always a value `show` takes.
- `assembly()` reports each node's effective `layers` (keys, in the document's order), beside its effective colour.
- `onAssemblyChange` delivers both, so a listener needs no other call.

**The navigator.** A row is **outside the shown layer** when a layer is shown and neither its node nor any node below it is on that layer. Such a row is marked obscured with the class rows under a hidden ancestor already use (`.machinome-nav-row--obscured`); its visibility control keeps reporting the node's own setting and toggling it still calls `setVisible`; the control's accessible name says so: `Visibility for case (not on the shown layer Electrical path)`, after the hiding ancestor where both apply. A group whose descendants are partly on the layer is not marked. The navigator gains no control that shows or switches a layer (Decision 8), and a group's colour chip does not follow the layer, as it follows no visibility state (spec "A group's colour does not follow what is expanded, focused or hidden"). `navtree.ts` decides it from `assembly` and `navigation` alone, as it decides `obscured`.

### 6. A republish

`AssemblyNavigation.reconcile` keeps the shown key when the new document still declares it and resets it to `null` (the whole machine) otherwise, as it resets a focused root the new tree no longer has (spec "Assembly-navigation state reconciles with viewer updates"); the change is reported in the update's one notification. The effective sets are recomputed in the same reconcile (Decision 1) and applied with the reconciled state, so a part that joined or left the shown layer is drawn or hidden by the republish. On the development page an edit that adds a layer to a class therefore shows in place, the picture standing.

### 7. The helper

`useMachine()` returns `{ bank, drawing, layers }`: `layers` is `viewer.layers()` as the store last read it. `MachineStore.read()` reads it beside the bank, and `sameReading` compares it by identity, which Decision 2 makes change exactly when the list changes; `onMachineChange` already fires on a republish, so an app re-renders with a new list. Any app, clocked or not, reads `useViewer().layers()`, `layer(key)` and calls `show`; `useMachine()`'s refusal of a model that is not clocked is unchanged. The helper re-exports the `Layer` type. What the Enigma writes:

```tsx
const { layers } = useMachine();
const viewer = useViewer();
<button onClick={() => viewer.show(null)}>Whole machine</button>
{layers.map((layer) => <button key={layer.key} onClick={() => viewer.show(layer)}>{layer.label}</button>)}
```

### 8. No control of the viewer's own

The viewer presents no layer control anywhere: not in the posed, running or clocked panels, the inspector's rail or sidebar, the navigator, or the export page. A model with no app gets no layer control from this change, and a host page may call `show` itself through the handle. That is the pilot's decision: the model's app adds its own controls.

### 9. Mounts that show no app

`show` is on every handle, whatever `driverControls` says, and the default is the whole machine; an on-demand mount (`machinome snapshot --viewer web`, a movie's take) never calls it, so its picture is unchanged. Nothing in the capture or the movie is changed.

### 10. API 32

`machinomeViewerApi` becomes 32 (`widget/package.json` 4), and the manual's `source_viewer_api` with it (`packages/machinome/docs/conf.py` 47, pinned equal by `tests/test_documentation.py` 104): the handle gains members a host or an app may require. Document versions stay 1 to 14. A new requirement states the gate, as the app's and the conditional colour's did; the app's gate, which says the viewer advertises 31, is restated to "31 or later" so the two do not contradict (its scenario restated). The baseline "The viewer declares its API version", whose text still names 19, is not restated here, as the precedent did not.

### 11. Tests, red first

Widget (vitest, jsdom), run singly from `widget/`:

- `src/layers.test.ts`, on the `draw-on-change.test.ts` bench (`vi.mock('three')` counting renderer, stubbed `ResizeObserver` and `fetch`, a hand-written posed document whose tree is `case` (no layer) with a marking, `circuit` (`electrical`) holding `wire` and `lamp` (`mechanical`), `lever` (`mechanical`), `key` (`electrical`, `mechanical`), and `spring`, a flexible part under `circuit`, built as `flexible.test.ts` builds one): V1 each malformed form of Decision 1 refuses the document naming it, and a document with no `layers` mounts with today's scene; V2 `layers()` answers the list in order, frozen, the same array across a republish with an equal list and a new one when a label changes; `layer('electrical')` answers it and `layer('x')` throws the sentence; V3 `show(layer('electrical'))` leaves `circuit/wire`, `circuit/lamp`, `circuit/spring` and `key` drawn (their meshes visible up to the scene) and `case`, its decal and `lever` not drawn; `show(null)` draws all; V4 `show('electrical')` and `show({key: 'x'})` throw, change no flag and notify nobody; V5 `partOnScreen(['case'])` is null under the electrical layer and not null with the whole machine; the pick at `case`'s screen point does not answer `case`; a framing under the layer (`setRoot(null)`) places the camera as it does for the same document without `case` and `lever`; V6 the renderer draws once per `show` and not at all over the following still frames; V7 composition: `setVisible(['key'], false)` then `show(electrical)` leaves `key` undrawn and `navigation().hidden` listing it; `setVisible(['case'], true)` under the layer leaves `case` undrawn; `show(null)` restores exactly the navigator's state; `setRoot(['circuit'])` under the layer draws only `circuit`'s parts on it, and `navigation()` reports root, hidden and layer; V8 `assembly()` reports `lamp`'s layers as `electrical`, `mechanical`; V9 `onAssemblyChange` is called once per accepted `show`, a redundant one included, with the navigation carrying the layer; V10 a republish keeping `electrical` keeps it shown; one dropping it shows the whole machine and notifies once; one moving `lever` onto `electrical` draws it. Red on the base: the members do not exist (read through the namespace so the file loads).
- `src/navtree.test.ts`: N1 under the electrical layer `case`'s and `lever`'s rows are obscured with the accessible name of Decision 5, `circuit`'s and `key`'s are not, and each row's checked state is its own setting; N2 a row under a hidden ancestor and outside the layer names both; N3 with no layer shown, rows are today's.
- `app/app.test.tsx`: H7 `useMachine().layers` is the handle's list, the reading's identity unchanged on a notification that changes nothing and new when a republish changes the list.
- `src/version.test.ts`: API 32; `tests/test_documentation.py` pins the widget's `machinomeViewerApi` and the manual's `source_viewer_api` (`packages/machinome/docs/conf.py` 47), both 32.

Python (`packages/machinome-viewer/tests`): `tests/test_model_app.py` gains B7, in Chromium on a copy of the existing calculator fixture with an app (`tests/fixtures/calculator-app/`) bundled as B1 does, the copy's `viewer.json` given a `layers` list and node keys by the test: a page script calls `show(layer('…'))` through the handle, and a part off the layer has no on-screen rectangle while one on it has, then `show(null)` restores it. Skips as B1 does.

The end-to-end proof across both packages, a model declaring layers built, exported and switched in Chromium through its own app, is the companion's X1.

### 12. The manual and the changelog

Under `skills/write-the-manual/SKILL.md` (workspace): the shared how-to `packages/machinome/docs/howto/show-a-layer.rst` (the companion writes the declaration half; this change the app's buttons and what the page shows, the composition with the navigator, the republish); `docs/reference/viewer/viewer-handle.rst` (`layers()`, `layer(key)`, `show()`, the navigation state's `layer`, the assembly node's `layers`); `docs/reference/viewer/app.rst` (`useMachine().layers`); `docs/reference/viewer/layouts.rst` (the navigator's rows outside the shown layer); `docs/reference/viewer/compatibility.rst` (API 32); `docs/reference/viewer/troubleshooting.rst` (the document refusals of Decision 1 and `show`'s). The bullet under "Unreleased" in `packages/machinome-viewer/CHANGELOG.md` is written in this cycle.

## Risks / Trade-offs

- [A part off the layer keeps its flexible evaluation per frame] → the same as a part the navigator hides; correctness is unaffected, and the Enigma's flexible parts are few.
- [The navigator lists every row, the left-out ones marked, not removed] → deliberate: the tree is the model's structure and a row's own control must stay its own (Decision 5); a host that wants fewer rows can focus.
- [`show` matches by key, so a hand-written `{key: 'electrical'}` works] → harmless: the key must be one the document declares, and the manual teaches `layers()` and `layer(key)` only.
- [Two other meanings of "layer" in the viewer] → recorded in Context; this change renames nothing, and the manual's pages on this capability say "a model's layers".

## Decision record

After the implementation confirms them, ADRs in `workflow/adrs/VIEWER-WEB/` (next free number after ADR-086): the viewer shows one declared layer through the handle's `show`, as a third input to the one visibility decision, composing by conjunction with focus and hiding, reported by `navigation()` and the navigator, with no control of the viewer's own (Decisions 2-6, 8); a model's app reads the layers through the helper (Decision 7). None is written before the implementation.
