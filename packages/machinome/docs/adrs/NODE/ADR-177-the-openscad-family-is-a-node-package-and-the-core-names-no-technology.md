# ADR-177: The OpenSCAD Family Is a Node Package, and the Core Names No Technology

**Status:** Accepted
**Date:** 2026-10-04
**Change:** [`openscad-out`](../../../openspec/changes/archive/2026-10-04-openscad-out/)
**Supersedes:**
- [ADR-171: The OpenSCAD engine is `machinome.openscad`](ADR-171-the-openscad-engine-is-machinome-openscad.md) — the engine package and the seam are dissolved into the family's package
**Amends:**
- [ADR-172: The core describes its SCAD presentation and the OpenSCAD engine writes it](ADR-172-the-core-describes-its-scad-presentation-and-the-openscad-engine-writes-it.md) — the writer's owner and address (`machinome.node.openscad.writer`); `_model_for_own_scad` is `presentation()`, `as_scad` is `present`
- [ADR-173: SCAD is written only where it is read](../BUILD/ADR-173-scad-is-written-only-where-it-is-read.md) — the sweep keeps by declaration (`kept_artifacts()`); its unchanged-document `.scad` rule is kept in effect by the transient record
- [ADR-086: State-dependent SCAD publishes at assembly phase completion](../BUILD/ADR-086-state-dependent-scad-publishes-at-assembly-phase-completion.md) — the coalescing is removed with its last producer
- [ADR-046: Conditional OpenSCAD dependency](ADR-046-conditional-openscad-dependency.md) — the binary contract's address is `machinome.node.openscad.binary`
- [ADR-103: The browser is the only interactive development viewer](../BUILD/ADR-103-the-browser-is-the-only-interactive-development-viewer.md) — `OpenScadRenderer` keeps its address, imports the package directly and is reached through the table of supported node types; the default renderer is unchanged
- [ADR-102: Native materialization precedes optional SCAD presentation](ADR-102-native-materialization-precedes-optional-scad-presentation.md) — no legacy SCAD-only override remains
**Related to:**
- [ADR-178: A leaf declares its kind as one set on the leaf base](ADR-178-a-leaf-declares-its-kind-as-one-set-on-the-leaf-base.md)
- [BUILD/ADR-179: The core reaches a node package's renderer and command through the table of supported node types](../BUILD/ADR-179-the-core-reaches-a-node-packages-renderer-and-command-through-the-table-of-supported-node-types.md)
- [ADR-167: A kernel is an extra, and its module refuses its absence at import](ADR-167-a-kernel-is-an-extra-and-its-module-refuses-its-absence-at-import.md) — the three doors the family's modules take
- [ADR-169: A leaf type is one module under `machinome.node`](ADR-169-a-leaf-type-is-one-module-under-machinome-node.md) — one path per name, no alias
- [MATH/ADR-170: The core's symbolic value is its own type](../MATH/ADR-170-the-core-s-symbolic-value-is-its-own-type.md)

## Context and Problem Statement

The pilot's finding of 4 October 2026 (`workflow/ongoing/lean-core.md`,
"Locked at the session's close"): the campaign's fifth and sixth cycles
(ADR-170 to 173) put SCAD *writing* behind the seam `machinome.scad_engine`,
yet the core still presented, named, swept, snapshotted and coalesced SCAD.
On the line at a16d45a the word stood in 37 of the core's Python modules, 453
times, by the token scan this change makes its gate. The ruling "Every node
type is a package" of the same day requires the OpenSCAD family to be a node
package like the others, `Solid2Node` a second package over it, and the core
to mention SCAD nowhere but in one table of supported node types.

## Decision Drivers

- No byte moves: every family `.scad`, every node's SCAD text, the OpenSCAD
  snapshot's root text and every document stay what they were.
- A plain install writes no SCAD and imports no SolidPython; the family's
  kernel is its extra, refused at the three doors of ADR-167.
- One path per name (ADR-169): nothing re-exports or aliases the removed
  modules.
- The core keeps only nameless mechanisms; the renderer architecture is the
  pilot's to revisit, so this decision does the least that gets SCAD out.

## Considered Options

1. **The family as the package `machinome.node.openscad`, `Solid2Node` at
   `machinome.node.solid2` over it, the seam dissolved, adoption a
   registered hook** (chosen)
2. Keep the seam, renamed, as the core's way to the family's writer and
   binary
3. A SolidPython-free writer in the package, so `machinome[openscad]` carries
   no Python dependency
4. Move `scad_expression` into the package
5. Have the core import `machinome.node.solid2` when SolidPython is
   importable, to keep adopting its values

## Decision Outcome

**The package.** `machinome.node.openscad`'s `__init__` calls
`require_extra('openscad', ...)` first and defines `OpenScadNode`, its
`__module__` unchanged. `leaf` holds `ScadLeafNode`, the family's leaf base:
`fn`, `scad_file`, `scad_code`, `generate_scad()`, `present` returning
what the leaf rendered, `materialize` writing its own `.scad`,
`kept_artifacts()` = `(scad_file,)` and the STL runner, moved from the node
base unchanged. `writer` holds `scad_text` (moved unchanged, still through
SolidPython), `scad_code(node)` and `generate_scad(node)`, which publishes
`<basepath>.scad` through `currency.publish_text`, reusing within a source
generation the text already published for the same full identity, and marks
it transient unless the node keeps it. `binary` holds the OpenSCAD
executable's contract, `OpenScadUnavailable` a `RuntimeError` with its
message unchanged. `machinome/openscad/` and `machinome/scad_engine.py` are
deleted; importing them fails with Python's own `ModuleNotFoundError`.

**`Solid2Node`** is `machinome.node.solid2`: `require_extra('solid2', ...)`,
`Solid2Node(ScadLeafNode)` with `as_number`, and `adopt`, registered with
`machinome.expression_graph.register_adopter` at import. `symbolic` asks the
registered adopters after numbers, `GraphValue` and `ExpressionNode`; without
one a foreign value is not an expression.

**What the core keeps is nameless.** A presentation is the core's description
(`present`, `presentation()`, `assemble()`), which an installed package may
write; `math`, `expression_graph` and `core.expressions` are machinome's
expression language, `scad_expression` renamed `closed_expression` in place
(it is the core's `str()` of a symbolic value). The build sweep keeps what a
node declares in `kept_artifacts()`; an artifact published as transient
(`currency.record(..., transient=True)`, a version-3 record carrying
`"transient": true`) is removed by every successful build, so the root
`.scad` a killed snapshot left goes with the next build, unchanged document
or not, and no rule of the sweep names a kind. The generation census stays,
its reuse record renamed `has_published` / `remember_published`; ADR-086's
coalescing goes, the assembly phase checkpointing `assembly post`.
`--renderer web` and `Sim(meshes=True)` no longer call `assemble()`. The
OpenSCAD snapshot renderer stays at `machinome/viewers/openscad.py`, importing
the package's writer and binary directly, until the viewer cycle.

**The gate.** `tests/test_core_names_no_scad.py` reads every
`machinome/**/*.py` by path and by name, string and comment token, and finds
no case-insensitive `scad` outside the package, `machinome/node/solid2.py`,
`machinome/viewers/openscad.py` and `machinome/node/supported.py`, JSCAD's
own name excepted. Red at 37 modules and 453 occurrences; green at zero.

**Extras.** `solidpython2==2.1.*` leaves the required dependencies for the
`openscad` extra; `solid2` installs `machinome[openscad]`; `all` names both.

## Ratification (4 October 2026)

The pilot ratified the change with: SolidPython kept in the writer and the
`openscad` extra (option 3 rejected); `closed_expression` stays in the core
(option 4 rejected); adoption registered by `machinome.node.solid2` (option 5
rejected); the transient record for the unchanged-document sweep; the default
renderer stays `openscad`.

## Rejected Options

- **2, a renamed seam:** its one remaining caller would be the package
  itself; the core resolves no provider of the family, so ADR-162's check moves
  nowhere.
- **3, a SolidPython-free writer:** SolidPython prefixes its process-global
  `use` registry to every rendering (a 129-byte text becomes 161 bytes after
  one `import_scad`), and `OpenScadNode`'s module call needs its SCAD parser
  (`m(3, b=4.5)` writes `m(a = 3, b = 4.5);`, a wrong arity is refused); a
  writer of its own changes bytes or behaviour.
- **4, `scad_expression` in the package:** it is the core's `str()` of every
  symbolic value, read with or without the family.
- **5, the core importing `solid2` to adopt:** the core naming a package for
  its values is the seam again.

## Consequences

- A plain `pip install machinome` carries no SolidPython; `Solid2Node` needs
  `machinome[solid2]`, `OpenScadNode` and an OpenSCAD snapshot
  `machinome[openscad]`, each refused naming its extra.
- A SolidPython value is adopted only in a process that imported
  `machinome.node.solid2`; machinome-mechanics' tests that pass
  `solid2.get_animation_time()` to machinome math move to the core's
  `get_animation_time` in mechanics' own cycle.
- The family's writer reaches two core functions not yet declared in the leaf
  contract, `currency.publish_text` and the generation's published-state
  record; declaring them is the cut's.
- Validated empirically (the change's evidence, § 12): Pin_tumbler_lock's
  `.scad`, verdict log and snapshot root text byte-identical, Prusa3-vanilla's
  15935 verdicts byte-identical, OpenAstroMount built and tested with the
  family unfindable, the universe sweep unchanged.

## References

- [`openscad-out` change](../../../openspec/changes/archive/2026-10-04-openscad-out/): proposal, design (Decisions 1 to 4, 7, 8, 11), evidence
- Specs `openscad-node`, `openscad-dependency`, `kernel-extras`, `build-pipeline`,
  `motion-expression-sharing`, `backend-neutral-materialization`
