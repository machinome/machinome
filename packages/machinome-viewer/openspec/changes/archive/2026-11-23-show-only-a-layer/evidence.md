# Evidence: show-only-a-layer

Applied on the bench `WTs/layers`, branch `layers`, one planning commit
(`2d81792d`) above base `cc2e661a`, clean at the start. Nothing here is
committed.

## 2.1 Red on the base (before any source change)

- `src/layers.test.ts` (new, 33 tests at that point): 32 failed, 1 passed.
  The one green is V1's "mounts a document with no layers as it mounts today".
  V1's eleven malformed forms are each accepted today (the promise
  `rejects.toThrow` fails: "promise resolved instead of rejecting"); V2 to V10
  fail with `handle.layer is not a function`, `layers is not a function` or,
  for V8, `expected undefined to deeply equal [ 'electrical' ]` (the node
  reports no `layers`).
- `src/navtree.test.ts`: 3 failed (N1 x2, N2), 55 passed (N3 and every
  existing test green).
- `app/app.test.tsx`: H7 x2 failed, 9 passed.
- `src/version.test.ts`: 1 failed ("declares a model's layers as API 32"),
  6 passed.
- `tests/test_documentation.py`: 2 failed (`machinomeViewerApi == 32` and
  `source_viewer_api == '32'`: `assert '31' == '32'`), 12 passed.
- `tests/test_model_app.py -k b7`: failed in Chromium, `TypeError:
  viewer.layers is not a function`.

## Green after the implementation

See the report of the applier for the final counts per file; the files run
singly were the ones named in task 5.4, every other widget test file one by
one (all green), `tests/test_model_app.py` 7 passed, `tests/test_draw_on_change.py`
5 passed, `tests/test_documentation.py` 15 passed, `tests/test_bundle.py` 11
passed, `tests/test_version.py` 3 passed, `tests/test_asset_load_order.py` 4
passed, `tests/test_licence.py` 6 passed, and the framework's
`tests/test_docs_structure.py` (39 passed) and
`tests/test_viewer_documentation_links.py` (15 passed). Skips: widget
`src/run/profile-contact.test.ts` 1 skipped and
`src/run/profile-installed-benchmark.test.ts` 1 skipped, both skips of the
base (not touched here).

The manual was also built with `sphinx -b html -n --keep-going` (not `-W`) on
the bench venv with `-D html_theme=alabaster`, because the venv lacks
`sphinx_rtd_theme`: no warning was printed.

## 6.1 Mutations (one at a time, each restored byte-equal, checked with `cmp`)

```
## M1 layer term dropped from the surface rule | src/layers.test.ts | Tests  33 passed (33) | restored byte-equal: True
## M2 layer written into hidden paths | src/layers.test.ts | Tests  9 failed | 24 passed (33) | restored byte-equal: True
   - V10: a republish > keeps a shown layer the new document still declares, over its new membership
   - V10: a republish > shows the whole machine, notifying once, when the layer is gone
   - V3: showing a layer shows only the parts on it > draws everything again for null
   - V3: showing a layer shows only the parts on it > draws the mechanical layer: its own parts, none of the wires
   - V5: a part off the layer is absent > has no on-screen position, is not reached, and is not framed
   - V7: the layer composes with focus and hiding > a focus under a layer draws only that subtree's parts on it, and the layer survives
   - V7: the layer composes with focus and hiding > hiding, then showing a layer, keeps the part hidden and listed
   - V7: the layer composes with focus and hiding > showing a layer leaves the focus and the hidden paths as they were
   - V7: the layer composes with focus and hiding > showing a part the layer leaves out draws nothing; the whole machine then draws it
## M3 show resets the focus | src/layers.test.ts | Tests  1 failed | 32 passed (33) | restored byte-equal: True
   - V7: the layer composes with focus and hiding > showing a layer leaves the focus and the hidden paths as they were
## M4 show does not notify | src/layers.test.ts | Tests  1 failed | 32 passed (33) | restored byte-equal: True
   - V9: every accepted show is announced once > notifies per call, a redundant one included, with the layer in the navigation
## M5 effective set from own keys only | src/layers.test.ts | Tests  5 failed | 28 passed (33) | restored byte-equal: True
   - V3: showing a layer shows only the parts on it > draws the parts on the electrical layer and no other, markings included
   - V5: a part off the layer is absent > frames what is drawn: the camera of the same machine without the case and the lever
   - V5: a part off the layer is absent > has no on-screen position, is not reached, and is not framed
   - V7: the layer composes with focus and hiding > a focus under a layer draws only that subtree's parts on it, and the layer survives
   - V8: the assembly reports each node's effective layers > lists a node's own layers and every ancestor's, in the document's order
## M6 shown key kept on a republish that dropped it | src/layers.test.ts | Tests  1 failed | 32 passed (33) | restored byte-equal: True
   - V10: a republish > shows the whole machine, notifying once, when the layer is gone
## M7 decals left to the focus alone | src/layers.test.ts | Tests  33 passed (33) | restored byte-equal: True
## M8 layer(key) answers undefined for an unknown key | src/layers.test.ts | Tests  2 failed | 31 passed (33) | restored byte-equal: True
   - V2: the handle answers the layers > answers a layer by key, and refuses an unknown key by name
   - V2: the handle answers the layers > names the absence when the document declares none
## M9 sameReading ignores layers | app/app.test.tsx | Tests  1 failed | 10 passed (11) | restored byte-equal: True
   - H7: useMachine answers the handle's layers > H7: a list that changes between the first render and the subscription is not lost
## M1 layer term dropped from the surface rule | src/layers.test.ts | Tests  2 failed | 33 passed (35) | restored byte-equal: True
   - V3: the two rules of design Decision 4, read flag by flag > a part off the layer with a part on it below it draws only the part on it
   - V3: the two rules of design Decision 4, read flag by flag > a part's own surface and its decals carry the layer term themselves
## M7 decals left to the focus alone | src/layers.test.ts | Tests  1 failed | 34 passed (35) | restored byte-equal: True
   - V3: the two rules of design Decision 4, read flag by flag > a part's own surface and its decals carry the layer term themselves
```

M1 and M7 first survived the V3 as designed (the group's own visibility, the
third rule, already hides a leaf's surface and decals, so a mutant that drops
the layer term from the surface rule is invisible through `visible` up the
chain). Two tests were added (the second `V3` describe: a part's own surface
and decals read flag by flag, and a part off the layer with a part on it
below it) and both mutations then turned red, as the table shows. M7 is
observable only at the level of the decals group's own flag: for a leaf, which
is the only node that carries markings, the group's flag hides the decal in
every case.

## Departures from the design

1. `chipState`'s label for a row both under a hidden ancestor and off the
   shown layer is `Visibility for p (hidden with G, not on the shown layer
   Electrical path)`: the design says "after the hiding ancestor where both
   apply" and fixes no separator; a comma was chosen.
2. `NavigatorRow` gains `outsideLayer: string | null` (the shown layer's
   label); `obscured` is true when `hidingAncestor !== null` or
   `outsideLayer !== null`, so `hidingAncestor` stays null for a row obscured
   only by the layer.
3. `WidgetTree` takes a trailing `layerScope` (`{order, inherited}`, default
   `NO_LAYERS`) in its constructor, `reconcile` and `prepareReconcile`: the
   document's layer order is carried down with the parent's effective keys so
   each node reports its layers in the document's order, as `assembly()`
   requires. A tree built without a scope (the suite's direct constructions)
   reports `layers: []` for every node.
4. `AssemblyNavigation.reconcile(tree, layers)` takes the declared layers and
   `setLayer(tree, layer)` is the new operation (the design names `setLayer(tree,
   key | null)`); the object is held so `state()` needs no table.
5. Existing tests changed because API 31 became 32 and the reported shapes
   grew: the API 31 case of `src/version.test.ts` is now "31 or later";
   `src/assembly.test.ts` (five expectations gain `layer: null`);
   `src/tree.test.ts` (the assembly snapshot gains `layers: []`);
   `app/app.test.tsx` H1 (the reading carries `layers`) and the fake host
   answers `layers()`; the `apiVersion` pins in `tests/test_asset_load_order.py`,
   `test_bundle.py`, `test_calculator_document.py`, `test_carriage_document.py`,
   `test_clearing_document.py`, `test_curta_drawing.py`,
   `test_lock_document.py`, `test_profile_document.py`,
   `test_regulator_document.py`, `test_running_document.py` and
   `test_source_timing_browser.py` (31 to 32).
6. `tests/test_documentation.py` gains `test_layers_are_an_unreleased_source_capability`
   (the manual's pages and the changelog name the capability).
7. V5's pick check is made through `partOnScreen(...).point` (a lever standing
   inside a large case has no reachable point; with the case off the layer it
   has one): the handle has no pick-at-point of its own.
8. `useMachine()`'s reading is replaced on every notification as before (H1),
   so H7 checks the identity of the reading's `layers` list, and the
   subscription-time re-read (the only user of `sameReading`) for the
   mutation.

## Not done

- The declaration half of `docs/howto/show-a-layer.rst` is the framework
  applier's: the page carries a heading "Declare the layers" with the
  document contract only.
- The HTML manual build was not run with the project's theme (missing in the
  bench venv).
- Tasks 7.4 (ADR) and 7.5 (sync, archive, commit) are not the applier's.

## Reviewer's planted faults (republish path)

Four faults planted by the reviewer survived V1 to V10. `src/layers.test.ts`
gains V11 (five tests); each fault was applied by hand, the suite run, and the
source restored byte-equal (`cmp`).

| Fault | Test that now catches it | Result under the fault |
| --- | --- | --- |
| `tree.ts` `prepareReconcile`: existing child passes `scopeBelow(layerScope, this.layerKeys)` (the old keys) | V11 "an existing child follows an ancestor that gains a layer" and "... loses a layer" | both fail: `expected ['electrical'] to deeply equal ['electrical','mechanical']` and `... equal ['mechanical']` |
| `tree.ts`: created child passes `scopeBelow(layerScope, [])` | V11 "a new child inherits its ancestor's layers" | fails: `expected [] to deeply equal ['electrical']` |
| `assembly.ts` `AssemblyNavigation.reconcile` keeps the old shown object | V11 "a shown layer's new label replaces the old one and the layer stays shown" | fails: navigation layer keeps the old label instead of `Wiring` |
| `viewer.ts` artifact-changed path reconciles without `documentLayers` | V11 "an artifact change keeps the shown layer" | fails: `expected null to deeply equal { key: 'electrical', ... }` |

On the real source `src/layers.test.ts` passes whole (40 tests) and
`tsc --noEmit` is clean.
