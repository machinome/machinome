## Why

The Enigma I reconstruction (`projects/enigma-i`, about 3,300 parts, root class `simulation/machine.py:Enigma`, which already declares its own page app `app = 'app/index.tsx'`, files under `simulation/app/`) is to show the path the current takes: the pilot wants its page to show only the electrical path (the copper parts and the wires, the keys and the lamps) with everything else hidden, and, as a second view, only the mechanical parts that move the rotors, switched by a widget of the page's own app between the whole machine, the electrical layer and the mechanical layer. Today nothing a model declares says which parts belong to such a view: a node class carries its parameters, children, joints, markings, frames, `color`, `controls` and `app` (`node/declarative.py` `NodeMeta.__new__`, 1011-1088), and a document's node entry carries `name`, `type`, `color`, `mtime`, `operations` and what its kind adds (`core/serializer.py` `serialize_node`, 1032-1069), so neither the framework nor the viewer can tell an electrical part from a case screw. The framework's half is that membership is a fact of the model, declared once and published in the document; showing only some layers is a decision of the page, which is the viewer's companion change `show-only-a-layer`.

## What Changes

- A public **`Layer`** object, `Layer(key, *, label)`, at its one address `machinome.layers` (the framework's rule: every name at the module that defines it; `machinome/__init__.py` re-exports nothing). A project defines each layer once in its own module and imports it wherever a part declares membership, so no use site spells a string. The key is what the document carries; the label is what a person reads. A key or a label that is not a non-empty string is refused by name.
- A node class may declare **`layers`**: one `Layer` or a non-empty tuple of them. Anything else, a repeated layer within one declaration included, is refused where the class is written, naming the class. `layers` becomes a reserved class-body name on a node class, as `controls` and `app` are. A subclass's declaration adds to its bases' (and to a plain mixin's), and there is no way to take one away. The declaration is the class's; a node instance that assigns `layers` is refused when the model is published, naming the node.
- **Inheritance down the tree:** a node is on every layer it declares and every layer any node above it in the published tree declares. A child may add layers and cannot remove one. A part may be on several layers. A node below a rigid node (a part fused into a `FusionNode`) is not published, so its declaration contributes nothing, as an `app` declared on a child contributes nothing.
- **One key, one layer:** two different `Layer` objects with the same key in one published tree are refused when the document is produced, naming the key and the two nodes that declare them.
- **The document:** the top level gains `layers`, a list of `{"key", "label"}` in the order a depth-first walk of the published tree first meets each layer; each node entry whose class declares layers gains `layers`, the list of the keys **it declares** (not its inherited ones). Both keys are absent where nothing is declared, so a model that declares no layer publishes a document byte-identical to today's, in every producer (`viewer.json`, `manifest.json` and the web viewer's capture staging). The fields are **additive**: the document version does not change (the `markings` and `source` precedent, `export` spec "Manifest contract"; the `app` record's, `model-app`), because a viewer that ignores them draws the whole machine, which is a truthful picture of it.
- The manual: a how-to on showing one layer of a machine (this change writes the declaration half, the companion the app's), the API reference for `Layer` and the reserved `layers`, and the `HISTORY.rst` bullet under "Unreleased", written in this cycle.

## Capabilities

### New Capabilities

- `layers`: a layer defined once and named by its key; a node class declares the layers it is on; membership is inherited down the published tree and never removed; one key names one layer in a machine; the document carries the layers and each node's declared keys, additively.

### Modified Capabilities

- `user-documentation`: a requirement is added for the how-to and the reference entries that state layers.

## Impact

- Source: new `machinome/layers.py` (`Layer`; imports nothing, as `machinome/parameters.py` imports nothing, so a project module and `node/declarative.py` may import it freely); `machinome/node/declarative.py` (the reserved `layers`, its form check beside `controls` and `app` at 1078-1081, and the collection over the method resolution order, kept on the class); `machinome/core/serializer.py` (`serialize_node` publishes a node's declared layers and refuses an instance's own `layers`; `document_body` writes the top-level table, gathers it and refuses two layers of one key, once for all three producers).
- Tests: new `tests/test_layers.py` and the fixture `tests/layers_project/`; the existing byte pins (`tests/base_documents/`, the markings golden documents, `tests/test_model_app.py` P4) are run again unchanged.
- Records: `HISTORY.rst` "Unreleased"; `docs/architecture.md` (the node model's declarations and the document); the new how-to and `docs/reference/api.rst`; ADRs after the implementation (design "Decision record").
- Dependencies: none.
- Companion: `packages/machinome-viewer/openspec/changes/show-only-a-layer/` (the viewer reads the layers, a model's app receives them, `viewer.show(layer)` shows only the parts on one). Neither change serves the Enigma without the other; each is tested on its own side of the document, and the end-to-end proof is this change's (design Decision 9, X1). The Studio's API shop skill (`packages/machinome-studio/machinome/studio/shop-skills/machinome-api/SKILL.md`) must state `Layer` and `layers` under the Studio's own process, a named completion dependency (tasks 6.3).
- What the originating project does with the result: the Enigma's maker defines `ELECTRICAL` and `MECHANICAL` in `simulation/layers.py`, declares them on the electrical subsystem, the rotor contacts and wiring, the keys and lamps, and the stepping parts, and adds the switching widget to `simulation/app/`. That project work is done later by someone else and is the validation of these changes, not part of them.

Standalone framework cycle in the worktree `machinome/WTs/layers`, branch `layers`, based on `main` at `cc2e661a`, paired with the viewer change in the same worktree. The pilot settled the design (the name `layers`; a `Layer` object defined once and imported; `layers = L` or a tuple; subtree inheritance with additions and no removal; several layers per part; same-key objects refused; membership a fact of the model, showing a decision of the page; the model's app adds its own controls, no automatic panel) and on 23 November 2026 authorised propose-and-apply in advance, with the orchestrating agent's adversarial review standing in for ratification. This proposal does not authorise integration into `main`, a push, publication or contact.

## Review

Reviewed on 23 November 2026 by the orchestrating agent, with the companion change, under the pilot's advance authorisation; this is an agent's review standing in for ratification, not a human reading of the finished text. Checked against the source: every caller of `serialize_node` outside the tests (the three producers and the two corpus generators reach `document_body`; `tools/check_curta_expressions.py` and `tools/generate_parity_fixture.py` do not, and serialize models that declare no layer), and the Studio precedent for the API skill (`declare-a-models-app` task 6.3). Rulings on what the proposer left open:

- A layer declaration stays inside a leaf's source currency. No measurement asks for an exclusion; the manual advises tagging assemblies.
- An instance that assigns `layers` is refused at publication. The pilot did not ask for the rule; it is kept because the alternative is an assignment silently ignored.
- A subclass adds to its bases' layers, as markings and frames are collected. The pilot ruled out removal down the tree; the same is applied to the class hierarchy.
- No finding required a revision.
