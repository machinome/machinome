## Why

The Enigma I reconstruction (`projects/enigma-i`, about 3,300 parts, root class `simulation/machine.py:Enigma`, which already declares its own page app `app = 'app/index.tsx'`, files under `simulation/app/`) is to show the path the current takes: the pilot wants its page to show only the electrical path (the copper parts and the wires, the keys and the lamps) with everything else hidden, and, as a second view, only the mechanical parts that move the rotors, switched by a widget of the page's own app between the whole machine, the electrical layer and the mechanical layer. The framework's companion change `declare-a-parts-layers` makes membership a fact of the model, published in the document. Showing only some layers is a decision of the page, and today the page cannot make it: the app's handle can hide one assembly path at a time (`setVisible`, `src/viewer.ts` 2877-2883, through `AssemblyNavigation`, `src/assembly.ts` 25-80) but knows nothing of a part's layers, and the helper's `useMachine()` (`app/index.tsx`) answers only the bank and the drawing.

## What Changes

- The viewer reads the document's `layers` (the top-level list of `{key, label}` and each node's own keys, stated identically in the companion's `layers` spec) and gives every part its **effective** layers: its own and every ancestor's, as it already inherits a node's colour (`src/tree.ts` 306, 332). A malformed list, or a node naming a key the list does not hold, refuses the document by name, as a malformed `markings` list does. The fields are additive: an older viewer ignores them and draws the whole machine.
- The mount handle gains `layers()` (the document's layers as frozen `{key, label}` objects, `[]` for none), `layer(key)` (one of them; an unknown key is refused by name, never answered empty) and `show(layer | null)`: showing a layer shows only the parts on it and hides every other; `null` shows the whole machine. `show` takes one layer at a time, not a list (design Decision 3), and refuses a string or an unknown key by name, changing nothing.
- A part the shown layer leaves out is **absent** wherever the viewer acts on visible parts: it is not drawn, its markings are not drawn, a press, a hover or `partOnScreen` does not reach it, framing does not count it, and a still page draws nothing; shared materials and geometries are untouched, and a flexible part is evaluated as a part the navigator hides is. The camera does not move.
- **Composition with the navigator:** the shown layer is a third, independent term beside the focused root and the explicitly hidden paths. A part is drawn only when the focus includes it, no hidden path covers it, and the shown layer (if any) holds it. `show` never changes the focus or the hidden paths, and `setRoot`/`setVisible` never change the shown layer, so neither overrides the other. `navigation()` reports the shown layer beside the root and the hidden paths, `assembly()` reports each node's effective layers, `onAssemblyChange` is told of every accepted `show`, and the navigator marks the rows the shown layer leaves out as it marks rows under a hidden ancestor, each row's own visibility control unchanged. A republish keeps the shown layer while the new document still declares its key, and shows the whole machine otherwise.
- The helper: `useMachine()` answers `layers` beside `bank` and `drawing`; any app reads them through `useViewer().layers()`. The viewer adds **no control of its own** for layers: no panel, rail, navigator or inspector control shows or switches one, so a model with no app gets no layer control.
- Viewer API rises from 31 to **32**; the document versions read stay 1 to 14.
- The manual's viewer pages and the `CHANGELOG.md` bullet under "Unreleased", written in this cycle.

## Capabilities

### New Capabilities

- `layers`: the document's layers as the viewer reads them; the handle's `layers()`, `layer(key)` and `show(layer | null)`; absence of the parts the shown layer leaves out; its composition with focus and hiding; republish; the app's access; no viewer-made control; the API 32 gate.

### Modified Capabilities

- `viewer-assembly-navigation`: "A viewer host can inspect the rendered assembly" is restated so each node reports its effective layers (every baseline scenario kept, one added); "A host reads the viewer's assembly navigation state" is restated so the state reports the shown layer (every baseline scenario kept, one added); a requirement is added for the navigator's rows outside the shown layer.
- `model-app`: "The app capability has an explicit reader capability" is restated so it holds at API 31 or later (its scenario kept, restated).
- `user-documentation`: a requirement is added for the manual's pages on layers.

## Impact

- Source (widget): `src/types.ts` (`ManifestLayer`, `Manifest.layers`, `ManifestNode.layers`); `src/viewer.ts` (the document's validation beside `assertMarkings`, the handle's `layers`, `layer`, `show`, the `Layer` type, the notification); `src/tree.ts` (each node's effective layers, kept across a reconcile; `applyVisibility` gaining the shown layer; `assembly()` reporting `layers`); `src/assembly.ts` (`AssemblyNavigation` holding the shown layer, reporting and reconciling it); `src/navtree.ts` and `src/navigator.ts` (rows outside the shown layer); `app/index.tsx` (`useMachine().layers`); `package.json` (`machinomeViewerApi` 32).
- Source (Python): none. The capture staging (`machinome/viewer/web/stage.py`) is unchanged: the companion gathers the layers in the one function every producer calls.
- Tests: new `src/layers.test.ts` (vitest, jsdom, on the `draw-on-change` bench pattern); additions to `src/navtree.test.ts`, `src/version.test.ts` and `app/app.test.tsx`; one Chromium case in `tests/test_model_app.py` over a copy of the existing calculator fixture. The end-to-end proof across both packages is the companion's X1.
- Records: the `CHANGELOG.md` bullet under "Unreleased"; the manual pages of design Decision 12 (in `packages/machinome/docs/`); ADRs after the implementation (design "Decision record").
- Dependencies: none.
- Companion: `packages/machinome/openspec/changes/declare-a-parts-layers/` (the `Layer` object, the `layers` declaration, the document fields). Neither change serves the Enigma without the other.
- What the originating project does with the result: the Enigma's app gets a box of three buttons (the whole machine, the electrical path, the rotor stepping) calling `viewer.show(...)` over `useMachine().layers`. That project work is done later by someone else and is the validation of these changes, not part of them.

Standalone viewer cycle in the framework worktree `machinome/WTs/layers`, branch `layers`, based on framework `main` at `cc2e661a`. The pilot settled the design (membership a fact of the model, showing a decision of the page; the app receives the layers as objects and passes them back; `show(null)` for the whole machine; lookup by key refusing an unknown one; no automatic panel, the model's app adds its own controls; hidden parts behave as absent) and on 23 November 2026 authorised propose-and-apply in advance, with the orchestrating agent's adversarial review standing in for ratification. This proposal does not authorise integration into `main`, a push, publication or contact.

## Review

Reviewed on 23 November 2026 by the orchestrating agent, with the companion change, under the pilot's advance authorisation; this is an agent's review standing in for ratification, not a human reading of the finished text. Checked against the source: every caller of `serialize_node` outside the tests (the three producers and the two corpus generators reach `document_body`; `tools/check_curta_expressions.py` and `tools/generate_parity_fixture.py` do not, and serialize models that declare no layer), and the Studio precedent for the API skill (`declare-a-models-app` task 6.3). Rulings on what the proposer left open:

- The navigator marks the rows the shown layer leaves out, and `assembly()` and `navigation()` report layers. The pilot asked for no navigator change; it is kept because the Enigma's page and the Studio show the navigator beside the app, and without the mark its rows report undrawn parts as shown. It is the widest step beyond the pilot's words and is reported to the pilot as such.
- `show` takes one layer or `null`; the lookup is `layer(key)`, not a property per key, for the reason the design gives.
- The stale API numbers in `viewer-package` are left as they are; they are not this change's.
- No finding required a revision.
