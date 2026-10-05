# ADR-178: A Leaf Declares Its Kind as One Set on the Leaf Base

**Status:** Accepted; the member `exact` is `brep`, amended 2026-10-05 by [ADR-180](ADR-180-the-engines-are-named-for-the-representation-each-consumes.md)
**Date:** 2026-10-04
**Change:** [`openscad-out`](../../../openspec/changes/archive/2026-10-04-openscad-out/)
**Amends:**
- [ADR-163: The leaf bases are declared extension points](ADR-163-the-leaf-bases-are-declared-extension-points.md) — `LeafNode`'s declared members
- [ADR-165: A leaf package declares the contract version on its class](ADR-165-a-leaf-package-declares-the-contract-version-on-its-class.md) — the version's first change, 1 → 2
**Related to:**
- [ADR-177: The OpenSCAD family is a node package, and the core names no technology](ADR-177-the-openscad-family-is-a-node-package-and-the-core-names-no-technology.md)
- [ADR-166: The core recognises no node type by the spelling of its class name](ADR-166-the-core-recognises-no-node-type-by-the-spelling-of-its-class-name.md)
- [ADR-102: Native materialization precedes optional SCAD presentation](ADR-102-native-materialization-precedes-optional-scad-presentation.md)

## Context and Problem Statement

The node spine is nominal: a node type subclasses one of the four leaf bases,
whose `leaf_contract` is checked at class creation, and the core dispatches by
`isinstance` on the bases (ADR-163, 166). Every kind distinction inside it,
though, was a duck attribute the core probed with `getattr` and a default —
`exact`, `flexible`, `rigid`, `stl_file`, `base_mesh`,
`declared_markings`, `src`, `scad_authored`: fourteen sites on the line at
a16d45a. Each flag was added when a kind appeared, and that accretion is how
SCAD leaked into the core: the sweep and the renderer probed `scad_authored`,
the leaf base said a faceted leaf "presents its render as SCAD", and a rigid
leaf whose STL was not current fell through to an OpenSCAD launch (the
`backend-switch` wart). The pilot ruled on 4 October 2026 that the flags
become one declared set on the leaf base.

## Considered Options

1. **One set of members with a default on the node base, read directly; the
   suite's doubles declare it** (chosen)
2. A literal `capabilities = frozenset({...})` the core tests membership of
3. A nominal split of the test framework's input (`isinstance` of the node
   base, or mesh-only)

## Decision Outcome

The set, documented together on `LeafNode`, each member with its default on
the node base so every node answers it: `rigid`, `flexible` (class
attributes), `exact` (a property), `optimize`, `present(rendered)` (the
leaf's presentation of one render; `LeafNode`'s default materializes a stale
STL and imports it), `presentation()`, `kept_artifacts()` (the artifacts
beyond its STL, BREP and markings a build keeps for it, `()` by default),
`generate_stl()`, the artifact paths `stl_file`, `brep_file`, `basepath`,
`local_stl`, `base_mesh()` and `declared_markings()`. No member names a
technology.

The core reads them directly; a permanent test (`tests/test_leaf_capability_set.py`)
finds no `getattr(x, '<member>', <default>)` and no `hasattr(x, '<member>')`
for a member of the set under `machinome/`. The suite's node doubles derive
the set's defaults from `tests/stand_in.py` (`StandIn`, and `NodeDouble` for
a namespace double).

The STL runner leaves the node base for the OpenSCAD family's leaf base. The
base's `generate_stl` keeps its three early returns (current, not rigid,
locked) and then refuses with `ArtifactNotProduced` (a `RuntimeError`,
"node {name} ({qualname}) produced no STL: its materialization published
nothing at {stl_file}") before any process starts. `StlRenderStart` stays in
the core, the generic signal of a leaf rendering in a subprocess. The
`as_scad`/`materialize` legacy split goes: a project leaf that only overrode
`as_scad` is refused naming it, and subclasses `Solid2Node` instead.

`machinome.node.leaf.CONTRACT` is 2. Removed from `LeafNode`'s declared
members: `as_scad`, `scad_file`, `generate_scad`; added: `present`,
`presentation`, `kept_artifacts`, `generate_stl`, `rigid`, `flexible`,
`exact`, `optimize`, `base_mesh`, `declared_markings` and
`StlRenderStart`; changed: `generate_stl` hands no leaf to OpenSCAD. A class
declaring `leaf_contract = 1` is refused naming 1, 2 and `machinome.node.leaf`.

## Rejected Options

- **2:** a string registry the core would test membership of; `exact` on an
  internal node is computed from its children and `rigid` and `flexible` are
  read as attributes by the serializer, so every reader would change for no
  new guarantee.
- **3:** keeps the defaults out of the code but turns the culling and memo
  doubles that expose an `stl_file` into mesh-only ones, rewriting what those
  tests prove.

## Consequences

- A leaf written outside the core answers the whole set with the base's
  meaning by subclassing a leaf base; a double substitutes for a node because
  it declares the set, not because the core tolerates its absence.
- machinome-freecad's `lean-core-validation` branch declares
  `leaf_contract = 1` and is refused under 2, as ADR-165 intends; its retarget
  declares 2.

## References

- [`openscad-out` change](../../../openspec/changes/archive/2026-10-04-openscad-out/): design Decisions 5 and 9, the `leaf-contract` and `node-model` deltas
