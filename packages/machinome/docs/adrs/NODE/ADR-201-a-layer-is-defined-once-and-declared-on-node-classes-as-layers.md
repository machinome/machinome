# ADR-201: A Layer Is Defined Once and Declared on Node Classes as `layers`, Collected Additively and Inherited Down the Published Tree

**Status:** Accepted
**Date:** 2026-11-23
**Change:** [`declare-a-parts-layers`](../../../openspec/changes/archive/2026-11-23-declare-a-parts-layers/) (design Decisions 1-3)
**Related to:**
- [ADR-202: A document carries each node's declared layer keys and a top-level table, gathered once in `document_body`](../EXPORT/ADR-202-a-document-carries-each-node-s-declared-layer-keys-and-a-top-level-table.md): what the declaration becomes in a document
- [ADR-061: A call in a node class body is a declaration](ADR-061-a-call-in-a-class-body-is-a-declaration.md): `layers` is checked where the class is written, as the reserved names `controls` and `app` are
- [ADR-198: A model's app is declared on its root and bundled by the viewer beside every document](../BUILD/ADR-198-a-model-s-app-is-declared-on-its-root-and-bundled-by-the-viewer-beside-every-document.md): the reserved-name precedent
- The viewer's own decision log, `packages/machinome-viewer/workflow/adrs/`: the viewer shows one declared layer (OpenSpec change `show-only-a-layer`)

## Context

Originating project: `projects/enigma-i`. Its maker wants to say once which
parts are on the electrical path and which move the rotors, tag whole
subsystems with one line each, and have the model's page show one layer at a
time. A node class already states what a node is through class-body
declarations, some checked by form where the class is written (`controls`,
`app`) and some collected off the method resolution order (markings, frames).
No declaration says which group of a machine a node belongs to. The pilot
ruled out a string at a use site, and ruled out removing a layer from a
subtree until the Enigma is tagged. No project declared a `layers` name
(every project repository was searched), so reserving it breaks none.

## Considered Options

1. **A `Layer` object defined once, declared as `layers` on a node class,
   collected additively over the class hierarchy** (chosen)
2. A plain string key (`layers = 'electrical'`): refused, a string at every
   use site, which the pilot excluded, and a typo is a new layer
3. Duck typing on a `layer_kind` attribute, as controls are recognised:
   refused, that exists so `machinome/node/` imports nothing from
   `machinome/simulation/`, and a module that imports nothing needs no guard
4. `Layer` under `machinome.node`: refused, a layer is not a node
5. Plain Python attribute lookup, so a subclass's `layers` replaces its
   base's: refused, replacing is a way to remove a layer
6. Validation at publication only: refused, a typo would surface far from
   the line that wrote it
7. Reading `node.layers` in the serializer: refused, it makes the instance
   form a second, unrefused spelling

## Decision Outcome

**The object.** `machinome.layers.Layer(key, *, label)`, a frozen dataclass,
both arguments non-empty strings or a `TypeError` naming the argument.
Equality and hash are identity (`eq=False`), as a colour choice's are: two
objects that share a key are the conflict ADR-202 refuses, never one layer.
The module imports nothing, as `machinome/parameters.py` imports nothing, and
the core re-exports nothing, so the address is `from machinome.layers import
Layer`.

**The declaration.** `layers` is a reserved class-body name. Written on a
node class it is one `Layer` or a non-empty tuple of `Layer`s in which none
repeats; a string, a list, an empty tuple, a repeat, a declaration named
`layers`, and a parameter or child so named are each refused by
`NodeMeta.__new__` naming the class and the form. It is neither a
`Declaration` nor a descriptor, so it never reaches `identity_values` or
`_build_uniq_id` and keys no artifact, piece or `uniq_id`.

**Collection, additive.** The class's declared layers are the union, each
once, of what every class of `reversed(cls.__mro__)` wrote in its own
`__dict__` under `layers`, a plain mixin that is not a node included, base
before subclass. They are kept on the class as `_declared_layers`, a tuple,
with the default `()` on the node base, so a class that declares none and
the suite's node doubles read the empty tuple directly, never through a
probing `getattr` (ADR-178). A mixin's value is checked by the same form,
the refusal naming the node class and the mixin (`Contact inherits layers =
'x' from Copper. ...`; a repeat in a mixin's tuple reads `Contact (layers
inherited from Copper) names ... twice`). A site-joint or mate
specialization inherits its declared layers by the same collection.

**Only the class declares.** The serializer reads `type(node)._declared_layers`,
never `node.layers`; a node whose own `__dict__` holds `layers` (assigned in
`__init__` or `simulate()`) is refused at publication, naming the node, so an
instance assignment is never silently ignored.

**Inherited down the published tree, no removal.** A node is on its declared
layers and on every layer of every node above it in the published tree; a
child may add and none removes. The consumer derives the inherited set as it
derives `color`. The published tree stops at a rigid node, so a layer
declared on a class used only inside a fusion contributes nothing, and an
omitted child is not published; as an `app` declared on a child contributes
nothing, the manual says so. The cost of a declaration: it is source, so
writing `layers` in a leaf's class body changes that leaf's node-scoped
digest (ADR-186) and rebuilds its artifacts once, as an edit to `color`
would; excluding it from currency is not done, no measurement asks for it,
and the manual advises tagging the subsystem assembly.

### Departures recorded in the change's evidence

- `tests/stand_in.py` gained `StandIn._declared_layers = ()`, which the
  design's own rule that doubles read the attribute directly requires.
- The mixin refusal sentences read as above (the design's elision filled in).
- The fixture gained `Bare`, `Twinned`, `Separate`, `Elsewhere`, `Plain` and
  `Mixed` for the tests of ADR-202's refusals and producers.

### Consequences

- Good: a project writes each layer once, imports it where it is declared,
  and tags a whole subsystem with one line; a typo is an `ImportError` or a
  refusal where the class is written.
- Good: no artifact key, piece or identity moves; a model declaring no layer
  is unchanged.
- Good: a node's keys are listed in the order its classes declare them,
  base before subclass, pinned by a fixture written against alphabetical
  order.
- Bad: a subclass cannot replace or drop a base's layer; revisited when the
  Enigma's tagging asks for it.
- Bad: tagging a leaf class rebuilds its artifacts once, and editing a
  `Layer`'s label rebuilds every leaf whose class names it.
- Neutral: `layers` is a reserved class-body name.

## References

- OpenSpec change `declare-a-parts-layers`: design Decisions 1-3, 7 and 9;
  the capability `layers`; its `evidence.md`
- `machinome/layers.py`, `machinome/node/declarative.py`
  (`_collect_layers`, `_layers_written`), `machinome/node/base.py`
- `tests/test_layers.py` (F1-F3, P4), `tests/layers_project/`
