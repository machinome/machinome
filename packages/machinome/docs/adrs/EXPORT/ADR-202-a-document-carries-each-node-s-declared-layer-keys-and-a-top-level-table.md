# ADR-202: A Document Carries Each Node's Declared Layer Keys and a Top-Level Table, Additively, Gathered Once in `document_body`

**Status:** Accepted
**Date:** 2026-11-23
**Change:** [`declare-a-parts-layers`](../../../openspec/changes/archive/2026-11-23-declare-a-parts-layers/) (design Decisions 4-6)
**Related to:**
- [ADR-201: A layer is defined once and declared on node classes as `layers`](../NODE/ADR-201-a-layer-is-defined-once-and-declared-on-node-classes-as-layers.md): the declaration this record publishes
- [ADR-034: Shared node-tree document schema](ADR-034-shared-node-tree-document-schema.md): the common document the keys join
- [ADR-197: A state color is presentation on the existing body](ADR-197-a-state-color-is-presentation-on-the-existing-body.md): the node's own `color` is the precedent for a declared value the consumer inherits
- [ADR-198: A model's app is declared on its root and bundled by the viewer beside every document](../BUILD/ADR-198-a-model-s-app-is-declared-on-its-root-and-bundled-by-the-viewer-beside-every-document.md): an additive key that moves no version
- The viewer's own decision log, `packages/machinome-viewer/workflow/adrs/`: how the viewer shows one layer

## Context

A page can show only one layer if the document says which node is on which
layer. Three producers publish a document through one walk and one body: the
build's `viewer.json`, the export's `manifest.json` and the web viewer's
capture staging. `document_body` exists "so the three producers that share
this walk cannot disagree about what they just emitted", and already
rewrites the serialized tree in place. Additive fields (`markings`, `source`,
`app`) move no version because a consumer that ignores them draws what it
drew before; a conditional `color` moved the version to 14 because ignoring
it draws a wrong colour. The viewer reads a part's layer from the same tree
walk in which it inherits `color`.

## Considered Options

1. **Each node's declared keys, and one table at the top; both gathered in
   `document_body`; absent when nothing is declared; no version move**
   (chosen)
2. Effective keys on every node: refused, it repeats an inherited fact
   thousands of times (some 50 to 120 kB on the Enigma's 24.6 MB document)
   and lets a producer publish a child that is not on its parent's layer
3. A collector threaded through `serialize_node` and handed to
   `document_body` by each producer: refused, each of three call sites, one
   in another package, must remember it, and a forgotten one publishes keys
   with no table
4. Raising the document version: refused, a consumer that ignores the fields
   draws the whole machine, a truthful picture; the gate for a page that
   needs `show` is the viewer's API, not the document's
5. A global registry of keys: refused, two objects of one key in different
   machines are not a conflict

## Decision Outcome

**Top level.** `layers`, one `{"key", "label"}` per distinct layer, in the
order a depth-first, child-ordered walk of the published tree first meets it
(each node's own keys in declaration order), after `instructions` and
`controls`, before `bindings`. **Node entry.** `layers`, the keys the node's
class declares, in declaration order and not the ones it inherits, after
`operations`, on any kind of node. Both are **absent** when nothing is
declared: no key, no empty list. A document whose tree declares no layer is
byte-identical to the one published before layers existed (pinned by a
SHA-256 recorded on the base), and `document_version` and `_warn_unreadable`
are untouched.

**Gathered once.** `serialize_node` leaves each entry's declared `Layer`
objects; `document_body` calls `_publish_layers(root)` before it binds or
versions anything. That one walk replaces each tuple by the list of keys,
builds the table, and refuses two different `Layer` objects of one key in one
tree with a `ValueError` naming the key, both objects and the root-relative
paths of the first node declaring each (`two different layers share the key
'electrical': ... define a layer once and import it where it is declared`).
A second layer with an equal label is still a second layer. In a build the
refusal is the build's failure, in an export it comes before anything is
written, and the capture staging refuses the capture. One key names one layer
in a machine; the same object in two places is one layer, and two machines
may each define one of the same key.

### Departures recorded in the change's evidence

- The P6 test (a tagged model differs from its untagged twin only by what
  layers add) normalizes module-derived artifact names, file modification
  times and the clocked machine's `identity` before comparing; it is red on
  the base, not green.
- The reviewer's planted fault that sorted a node's keys survived the first
  tests, since every fixture declared in alphabetical order; a fixture
  declared against it now pins the declaration order.

### Consequences

- Good: the whole document contract of layers lives in the one function the
  three producers share; no call site changed.
- Good: the document says what the model declares, which is what a person
  checking the tagging wants; no entry can disagree with its ancestors.
- Good: every untagged document is unchanged in every byte, from every
  producer.
- Bad: the serialized tree briefly holds `Layer` objects between
  `serialize_node` and `document_body`; an encoding that bypassed
  `document_body` would fail loudly in `json.dumps`, not silently.
- Neutral: an older viewer ignores the fields and draws the whole machine.

## References

- OpenSpec change `declare-a-parts-layers`: design Decisions 4-6 and 9; the
  capability `layers`; its `evidence.md`
- `machinome/core/serializer.py` (`serialize_node`, `document_body`,
  `_publish_layers`)
- `tests/test_layers.py` (P1-P3, P5-P7)
