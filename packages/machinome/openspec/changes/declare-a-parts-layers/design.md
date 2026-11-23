## Context

A node class states what a node is and carries through class-body declarations that `NodeMeta.__new__` checks where the class is written (`machinome/node/declarative.py` 1011-1088): parameters, children, ports and joints as `Declaration`s; markings and frames, duck-typed and collected off the method resolution order (`_declares_marking`, `declared_frames`); and two reserved plain names checked by form, `controls` (`_validate_controls`, 1107-1146) and `app` (`_validate_app`, 1154-1172). `color` is a plain class attribute on the node base (`node/base.py` 517-518), validated at colorization (`_colorize`, 1027-1039), published as the node's own value (`core/serializer.py` `serialize_node` 1036) and inherited by the viewer down the tree (`machinome-viewer/.../widget/src/tree.ts` 306, `this.colorSpec = data.color ?? inheritedColor`).

Three producers publish a browser document through one walk and one body: the build's `viewer.json` (`core/builder.py` 800-823), the export's `manifest.json` (`core/export.py` 240-263) and the web viewer's capture staging (`packages/machinome-viewer/machinome/viewer/web/stage.py` 78-99). Each calls `serialize_node` and then `document_body` (`core/serializer.py` 883-949), whose docstring states why it exists: "One place, so the three producers that share this walk cannot disagree about what they just emitted", and which already rewrites the serialized tree in place (its binding pass). `serialize_node` recurses through rendered children and stops at a rigid node (one `model`) or a flexible leaf (1042-1069); an omitted child is not rendered and not serialized.

How additive document fields were versioned: `markings` (node), `source` (top level) and the `app` record (top level) are additive and move no version, each because "a consumer that ignores it renders exactly the picture it renders today" (`export` spec "Manifest contract", the `markings` and `source` paragraphs; `model-app` "A build publishes the model's app beside its document": "The record SHALL be additive and SHALL NOT change the document's version"). A node's conditional `color` raised the document to version 14 because a consumer that ignored it would draw a wrong colour (`state-color`; `serializer.py` `document_version`, `_has_color_choice`). The viewer raised its API for a capability a host may require (the app: 30 to 31, companion precedent `show-a-models-own-app` design Decision 13).

The Enigma's tree (`projects/enigma-i/simulation/machine.py` 119-151): seven subsystem assemblies (`chassis`, `keyboard`, `stepping`, `scrambler`, `electrical`, `enclosure`, `annotations`), each a package of further assemblies and imported leaves; no `FusionNode` anywhere in `simulation/` (searched). Its published document is 24,599,557 bytes for 3,347 parts (companion-precedent measurement, `declare-a-models-app` design Decision 5a).

A search of every project repository under `projects/` for a node class body or instance assigning `layers` found none (the one hit, `3DPrintedClocks/clocks/utility.py` 1130, is a local variable in a function), so reserving the name breaks no project.

## Goals / Non-Goals

**Goals:**

- The Enigma's maker can say, once per layer and with no string at a use site, which parts are on the electrical path and which move the rotors, and tag whole subsystems with one line each.
- The document carries the layers and each part's membership, so the companion can show only one layer.
- Every document of a model declaring no layer is unchanged in every byte, from every producer.

**Non-Goals:**

- Showing, hiding, ghosting or any page control (the companion's, and only through a model's app).
- Removing a layer from a subtree or a subclass; selecting by rule or predicate; layers declared at a declaration site (`Child(layers=...)`) or per instance; generated typed names; any CLI flag; the movie or videomaker; `machinome vet` rules.

## Decisions

### 1. `Layer`, at `machinome.layers`

```python
# machinome/layers.py
@dataclass(frozen=True, eq=False)
class Layer:
    key: str
    label: str          # keyword-only: Layer('electrical', label='Electrical path')
```

`Layer(key, *, label)`: both required, both non-empty `str`, otherwise `TypeError` naming the argument (`Layer key must be a non-empty string, not 3`). Frozen; equality and hash are identity (`eq=False`), as `machinome.color._ColorChoice` is (`color.py` 14-15), because two objects that share a key are the conflict Decision 4 refuses, never the same layer. `repr` is `Layer('electrical', label='Electrical path')`, which every refusal quotes.

The module imports nothing, like `machinome/parameters.py` (architecture "The public surface is split by concern"): it is on the import path of every project module that declares a layer and of `node/declarative.py`, which imports it to recognise one by `isinstance`. Its address is its own module because the core re-exports nothing (`machinome/__init__.py`; architecture "every name at one module", ADR-087/181). The brief's `from machinome import Layer` is therefore spelled `from machinome.layers import Layer`.

Alternatives rejected: duck typing on a `layer_kind` attribute, as controls are recognised (`declarative.py` 1112-1118), which exists so `machinome/node/` imports nothing from `machinome/simulation/`; a module that imports nothing needs no such guard. A plain string key (`layers = 'electrical'`): the pilot ruled out strings at use sites. `Layer` under `machinome.node`: a layer is not a node and the node root exports nothing.

### 2. The declaration `layers`

Where a node class body assigns `layers`, `NodeMeta.__new__` checks it beside `controls` and `app` (1078-1081): a `Layer`, or a non-empty `tuple` of `Layer`s in which no object repeats. Anything else raises `TypeError` naming the class and the form: `Contact.layers is 'electrical'. On a node class `layers` names the layers the node is on: one Layer, or a tuple of Layers, each defined once with machinome.layers.Layer and imported; the name is reserved`. A repeated layer: `Key.layers names Layer('electrical', label='Electrical path') twice`. An empty tuple is refused (it can only be written to remove something, which Decision 3 does not allow). A list is refused (the form is one tuple, as the pilot wrote it). A child declaration, a parameter or any other declaration named `layers` is refused by the same check, so `layers` is a reserved class-body name as `app` is.

**Collection.** The class's **declared layers** are the union, in order, of what every class in `reversed(cls.__mro__)` wrote in its own `__dict__` under `layers`, a plain mixin that is not a node included (as markings and frames are collected, architecture "A fourth kind of declaration"), each layer once, base before subclass. They are computed in `NodeMeta.__new__` and kept on the class (`cls._declared_layers`, a tuple), with the default `()` on the node base (`node/base.py`, beside `color` at 517-518), so a class that declares none, and the suite's node doubles (`tests/stand_in.py`), read the empty tuple directly, never through a probing `getattr` (architecture, ADR-178). A mixin's value is checked there by the same form, the refusal naming the node class and the mixin (`Contact inherits layers = 'x' from Copper; …`). A subclass that writes `layers` therefore **adds** to its bases': Python attribute lookup would replace them, and replacing would be a way to remove a layer, which the pilot excluded until the Enigma is tagged. A site-joint or mate specialization (architecture, ADR-098) is a subclass built from the written class and inherits its declared layers by the same collection.

**Only the class declares.** The serializer reads `type(node)._declared_layers`, never `node.layers`. A node instance whose own `__dict__` holds `layers` (assigned in `__init__` or `simulate()`) is refused at publication with `TypeError`: `Enigma/electrical/contact (Contact) assigns layers on the instance; a node's layers are declared in its class body`, so an instance assignment is never silently ignored. No project needs per-instance layers: every subsystem of the Enigma is its own class.

`layers` is not a `Declaration` and not a descriptor: it never reaches `identity_values` or `_build_uniq_id`, so it keys no artifact and changes no piece, exactly as a marking does not (architecture "A fourth kind of declaration").

Alternatives rejected: validating at publication only (a typo would surface only when a document is built, far from the line); reading `node.layers` (makes the instance form a second, unrefused spelling).

### 3. Membership is inherited down the published tree

A node is on its declared layers and on every layer of every node above it in the published tree; a child may add layers and none removes one; a part may be on several. The document states this without repeating it (Decision 5): it carries each node's own declared keys, and the inherited set is the union along the path from the root, which is how the viewer already inherits `color` (`tree.ts` 306, 332).

**The rigid boundary.** `serialize_node` stops at a rigid node (1042-1051): a `FusionNode` is one model, and the parts fused into it are not nodes of the document. A layer declared on a class used only inside a fusion therefore contributes nothing, and the fusion's own declaration is what the document carries for it. This follows the precedent of an `app` declared on a child, which "contributes nothing" by specification (`model-app` "A model's root declares its app"), and the manual says it. Refusing it would need a walk of every fusion's children at publication for a case no project has: the Enigma has no fusion. An omitted child is not published either, so a layer declared only below omitted children is not in the document.

### 4. One key names one layer in a machine

Two different `Layer` objects with the same key in one published tree are refused, because the page looks a layer up by its key (companion) and two labels for one key would make the page's buttons depend on which part was met first. The check is made where the table is gathered (Decision 6), when the document is produced, because that is the one walk that sees every published node; a class body sees only its own MRO. The refusal is a `ValueError` naming the key, both objects and the root-relative paths of the first node declaring each: `two different layers share the key 'electrical': Layer('electrical', label='Electrical path') on Enigma/electrical and Layer('electrical', label='Wires') on Enigma/keyboard; define a layer once and import it where it is declared`. In `machinome build` it is the build's failure (recorded as every publication error is); in `machinome export` the export fails before it writes; the capture staging refuses the capture.

Two objects of one key in **different** machines (two models of one project, two tests in one process) are not a conflict: nothing is registered globally.

### 5. The document: each node's declared keys, and the table at the top

```json
{ "format": "machinome-export", "version": 8, …,
  "instructions": {…},
  "layers": [ {"key": "electrical", "label": "Electrical path"},
              {"key": "mechanical", "label": "Rotor stepping"} ],
  …,
  "root": { "name": "Enigma", …, "children": [
     { "name": "electrical", …, "operations": […], "layers": ["electrical"], "children": […] },
     { "name": "keyboard", …, "children": [
        { "name": "key_q", …, "operations": […], "layers": ["electrical", "mechanical"], "model": "…" } ] } ] } }
```

- Top level: `layers`, one `{"key", "label"}` per distinct layer, in the order a depth-first, child-ordered walk of the published tree first meets it (each node's own keys in declaration order). Placed after `instructions` and `controls`, before `bindings`; key order is not part of the contract.
- Node entry: `layers`, the keys the node's class declares (Decision 2), after `operations`, on any kind of node (assembly, rigid or flexible). Absent on a node that declares none.
- Both are absent when nothing is declared: no key, no empty list.

**Declared, not effective, keys on the node.** The viewer needs each part's effective set, which it derives in the tree walk it already makes for colour (`tree.ts` 294-332, `reconcile` 429-459): the union of the node's keys and its parent's effective set. Carrying the declared keys keeps one fact in one place, as `color` does (the node's own value, inherited by the consumer): no entry can disagree with its ancestors, and the document says what the model declares, which is also what a person reading it to check the tagging wants. Size does not decide it either way: carrying effective keys would add a `"layers": [...]` of about 25 to 40 bytes to every node under a tagged subsystem, a few thousand on the Enigma, some 50 to 120 kB on a 24.6 MB document (under 0.5 %), while declared keys add a few dozen entries. Alternative rejected: effective keys on every node (repeats an inherited fact thousands of times and lets a producer bug publish a child that is not on its parent's layer).

**No version bump, no framework-side viewer gate.** The fields are additive by the `markings`/`source`/`app` rule: a viewer that ignores them draws the whole machine, which is a truthful picture of it, describes nothing an existing field describes differently, and enters no expression, binding or program. So `document_version` is untouched and `_warn_unreadable` has nothing new to say. A page that needs `show` requires the companion's viewer API (companion Decision 10); that is the viewer's gate, not the document's.

### 6. Where the table is gathered: once, in `document_body`

`serialize_node` writes a node's declared `Layer` objects into its entry (`data['layers'] = type(node)._declared_layers`, when non-empty), after refusing an instance's own `layers` (Decision 2). `document_body`, before it binds or versions anything, walks the serialized tree once (`_publish_layers(root)`): it replaces each entry's tuple by the list of its keys, gathers the table in first-met order, and refuses two objects of one key (Decision 4), naming paths built from the entries' `name`s. The table is written into the body when non-empty.

This puts the whole of the document's layer contract in the one function the three producers share, so the build, the export and the capture cannot disagree and none of their call sites changes (`builder.py` 800-823, `export.py` 240-263, `stage.py` 78-99, the last in the viewer's package). The binding and version walks read only `color`, `operations`, `flexible` and `children` (`_collect_slots` 674-689, `_tree_version` 647-653), so the objects are never seen by them. A serialized tree that never reaches `document_body` and is encoded directly fails loudly in `json.dumps` naming `Layer`, which no producer does.

Alternative rejected: a collector argument threaded through `serialize_node` and handed to `document_body` by each producer. It works, but each of the three call sites must remember it, one of them in another package; a forgotten one would publish node keys with no table, which the viewer refuses.

### 7. What a declaration costs a build

A layer is not identity (Decision 2): it keys no artifact, no piece and no `uniq_id`. It is source, though: writing `layers = ELECTRICAL` in a leaf's class body edits that leaf's tracked source, and the source digest scoped to what the node names (`machinome/currency.py` docstring, ADR-186) changes when that class or the `Layer` it names changes, so the leaf's artifacts are rebuilt once, as an edit to its `color` would. Declaring a layer on an assembly class rebuilds no part whose digest does not name that class (an assembly has no artifact of its own, and a part rarely names the assembly that holds it). The manual says so and advises tagging the subsystem assembly where the whole subsystem is on the layer. Excluding the declaration from currency is not in this change: it would be a currency rule for one attribute, asked for by no measurement (Open Questions).

### 8. The public contract outside this package

The Studio's API shop skill states every class-body declaration a maker writes (`controls`, `app` at its lines 1282-1399); `Layer` and `layers` are added there under the Studio's own process (ADR-193), changing no Studio UI, profile or orchestration (tasks 6.3).

### 9. Tests, red first

The fixture `tests/layers_project/` (inside the suite's project): `__init__.py`; `layers.py` defining `ELECTRICAL = Layer('electrical', label='Electrical path')` and `MECHANICAL = Layer('mechanical', label='Rotor stepping')`; `machine.py`, solid2 cubes only, a clocked root on the pattern of `tests/color_project/model.py:Clocked` (one `State`, one committing relation, one instruction), named `Layered`, with: `case` (a part on no layer), `circuit` (an assembly declaring `ELECTRICAL`) holding `wire` and `lamp`, `lamp`'s class adding `MECHANICAL`; `lever` (a part declaring `MECHANICAL`); `key` (a part declaring `(ELECTRICAL, MECHANICAL)`); `cover`, a `FusionNode` declaring nothing whose fused child's class declares `ELECTRICAL`; `spare`, an omitted child declaring a third layer `SPARE`; and `app = 'app/index.tsx'`; `inherit.py` (a part class declaring `MECHANICAL` over a base declaring `ELECTRICAL`, and one over a plain mixin `class Copper: layers = ELECTRICAL`); `conflict.py` (a root whose second child declares another `Layer('electrical', label='Wires')`); `instance.py` (a part assigning `self.layers = ELECTRICAL` in `__init__`); `untagged.py` (the same tree as `machine.py` with no declaration, for the byte pin); `app/index.tsx`, `app/app.css` (buttons from `useMachine().layers` and a "Whole machine" button, each calling `useViewer().show(...)`, a `<Viewport/>`, selectors under `.layers-app`). In `tests/test_layers.py`, building documents through `serialize_node` and `document_body` as `tests/test_state_color.py` does (no CAD build) unless a case says otherwise:

- F1 `Layer('electrical', label='Electrical path')` reads its key and label, refuses assignment, and is equal only to itself; `Layer('', label='x')`, `Layer(3, label='x')`, `Layer('e', label='')`, `Layer('e')` are each refused naming the argument (red: no module).
- F2 class bodies `layers = 'electrical'`, `layers = [ELECTRICAL]`, `layers = ()`, `layers = (ELECTRICAL, 'x')`, `layers = (ELECTRICAL, ELECTRICAL)` and `layers = Part()` are each refused as the class is written, naming the class (red: accepted today).
- F3 the classes of `inherit.py` declare `(ELECTRICAL, MECHANICAL)` in that order; the mixin's layer is collected; a mixin `layers = 'x'` is refused naming the node class and the mixin.
- P1 `Layered`'s document: the table is `[electrical, mechanical]` with their labels in first-met order; `circuit` carries `["electrical"]`, `wire` carries no key, `lamp` carries `["mechanical"]`, `lever` `["mechanical"]`, `key` `["electrical", "mechanical"]`, `case` and the root none.
- P2 `cover`'s fused child contributes nothing (no `electrical` from it; `cover` carries no key); `spare`'s layer is not in the table.
- P3 `conflict.py`'s document is refused with the sentence of Decision 4 naming both paths (red: published).
- P4 `instance.py` is refused with the sentence of Decision 2 naming the node (red: published without it).
- P5 `untagged.py`'s `viewer.json`, built with `Builder(path, watch=False, …)` in a temporary copy of `tests/`, is byte-identical to the bytes recorded on the base (SHA256 pinned in the test and in `evidence.md`), and carries no `layers` key anywhere; the existing pins (`tests/base_documents/` through their tests, the markings golden documents, `tests/test_model_app.py` P4) pass unchanged.
- P6 `Layered`'s version equals `untagged.py`'s, and no other key of the document differs from `untagged.py`'s but the `layers` table and the node keys.
- P7 the same fixture's `viewer.json` from a build and `manifest.json` from `export_node` carry equal `layers` tables and equal node keys; where the viewer package is installed, the capture staging's document carries them too (skip, saying why, without it).
- X1, the end-to-end proof: export `Layered` with its widget into a temporary directory, serve it statically, open `index.html` in headless Chromium (launched with the arguments of `machinome.viewer.web.capture.Capture.launch`), and check through the page's handle that the app drew one button per layer and a "Whole machine" button; after clicking "Electrical path", `partOnScreen` is null for `case` and `lever` and not null for `circuit/wire` and `key`, and the handle's `navigation().layer` is that layer; after "Whole machine", `case` is on screen again. Skips, saying why, without Chromium, the viewer's JavaScript dependencies or OpenSCAD; red on the base (no `layers`, no `show`).

F1-F3, P1-P4, P7 and X1 are red on the base; P5 and P6 are green on the base (P6 trivially: no fixture declares layers there) and stay green.

### 10. The manual and the changelog

Under the workspace's `skills/write-the-manual/SKILL.md`: a new how-to `docs/howto/show-a-layer.rst`, "Show one layer of a machine" (`.. needs:: viewer`), shared with the companion change as `give-a-model-its-app.rst` was: this change writes defining layers once, declaring them on parts and subsystems, inheritance and additions, the rigid boundary, the refusals and the cost of Decision 7; the companion writes the app's buttons and what the page shows; whichever cycle reaches the page first creates it, with its toctree entry in `docs/index.rst` and a link from `docs/howto/give-a-model-its-app.rst`. `docs/reference/api.rst` gains `machinome.layers.Layer` and the reserved attribute `layers` beside `app`. `HISTORY.rst` gains one bullet under "Unreleased" in this cycle. `docs/architecture.md`'s node model gains the declaration beside markings and frames, and its export section the two fields.

## Risks / Trade-offs

- [Tagging a leaf class rebuilds its artifacts once; editing a `Layer`'s label rebuilds every leaf whose class names it] → stated in the manual with the advice to tag subsystem assemblies; for the Enigma most tagging falls on subsystem assemblies (`electrical`, the keyboard's keys, `stepping`); measured on no project before the Enigma is tagged.
- [A layer declared inside a fusion contributes nothing] → specified and documented (Decision 3); no project has the case.
- [A subclass cannot replace its base's layers] → deliberate (the pilot's no-removal rule); revisited when the Enigma's tagging asks for it.
- [The serialized tree briefly holds `Layer` objects] → only between `serialize_node` and `document_body` inside one producer; an encoding that bypassed `document_body` would fail loudly, not silently.

## Open Questions

- For the orchestrator: whether a layer declaration should be left out of a leaf's source currency, so that tagging the Enigma's leaf classes or editing a label rebuilds no part (Decision 7). Not proposed: no measurement asks for it yet, and the manual's advice (tag subsystem assemblies) avoids most of the cost.

## Decision record

After the implementation confirms them, ADRs under `docs/adrs/NODE/` and `docs/adrs/EXPORT/` (next free number after ADR-200): a layer is a `Layer` object defined once and declared on node classes as `layers`, collected additively over the class hierarchy and inherited down the published tree with no removal (Decisions 1-3); a document carries each node's declared layer keys and the top-level table, additively, gathered once in `document_body`, with one key per layer per machine (Decisions 4-6). None is written before the implementation.
