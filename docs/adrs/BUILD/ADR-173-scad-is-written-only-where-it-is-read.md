# ADR-173: SCAD Is Written Only Where It Is Read

**Status:** Accepted
**Date:** 2026-10-04
**Change:** [`scad-presentation`](../../../openspec/changes/scad-presentation/)
**Amends:**
- [ADR-102: Native materialization precedes optional SCAD presentation](../NODE/ADR-102-native-materialization-precedes-optional-scad-presentation.md) — "ordinary builds still request that output"
- [ADR-046: Conditional OpenSCAD dependency](../NODE/ADR-046-conditional-openscad-dependency.md) — the refusal family gains the engine's
- [ADR-086: State-dependent SCAD publishes at assembly phase completion](ADR-086-state-dependent-scad-publishes-at-assembly-phase-completion.md) — its production producer is gone
**Related to:**
- [ADR-172: The core describes its SCAD presentation and the OpenSCAD engine writes it](../NODE/ADR-172-the-core-describes-its-scad-presentation-and-the-openscad-engine-writes-it.md)
- [ADR-116: An artifact import is anchored on the build directory](ADR-116-an-artifact-import-is-anchored-on-the-build-directory.md)
- [ADR-103: The browser is the only interactive development viewer](ADR-103-the-browser-is-the-only-interactive-development-viewer.md)

## Context and Problem Statement

With the presentation described by the core and written by the engine
(ADR-172), the question left is when a `.scad` is written at all. Before this
decision `machinome build` presented SCAD for every node (`Builder`'s
`scad_output`, true by default, called `assemble()`, which wrote every node's
`.scad`), `develop`'s builder did not (`scad_output=False`), and the sweep
spared every file ending `.scad`, so files of renamed or removed nodes
lingered forever.

Who reads a generated `.scad` (read on 3 October 2026 across the framework,
the projects, the viewer and the studio): OpenSCAD, for a `Solid2Node`'s, an
`OpenScadNode`'s or a legacy SCAD-only leaf's own STL; the OpenSCAD snapshot
renderer, for the root's; a person opening a file in the OpenSCAD GUI; the
framework's tests. No build, published document, viewer, export or `machinome
test` reads one. 210 project files call `node.assemble()`, none using its
result. `machinome develop` has had no OpenSCAD fallback since ADR-103.

Three ratified requirements kept the build's SCAD deliverables, so the choice
went to the pilot.

## Decision Drivers

- OpenSCAD's artifacts produced only where machinome itself needs them.
- A build without SolidPython or the engine completes for a project that asks
  for no SCAD, and logs nothing about SCAD.
- Every `.scad` still written is the text OpenSCAD renders from.
- No lingering presentation files.
- Absence refused where SCAD text is actually needed, naming an install that
  works today.

## Considered Options

1. **A: a `.scad` is written only where a path reads it** (chosen by the
   pilot, 3 October 2026)
2. B: every build keeps writing every node's `.scad` when the engine is
   installed, and skips with a log line when it is not

## Decision Outcome

**Where SCAD is written.** A build writes the `.scad` of a leaf whose geometry
is authored in SCAD — `scad_authored`: true on `Solid2Node` and `OpenScadNode`
by class attribute and on a project leaf whose `_uses_legacy_scad_materialization()`
holds — at its materialization, through the engine, because OpenSCAD renders
that leaf's STL from it. No assembly, fusion, flexible leaf or native leaf
(exact, STEP, STL, JSCAD, sheet) writes one. `assemble()` composes and returns
the description and writes nothing. The builder no longer presents:
`Builder._present_scad_if_requested`, its `assembly` phase and `scad_output`
(of `Builder` and `manager/develop.run_builder`) are removed, so `machinome
build` and `develop`'s builder are one pipeline, and a build no longer writes a
flexible leaf's per-binding snapshot STL. `scad_code` and `generate_scad()`
remain available to any caller.

**The OpenSCAD snapshot renderer's SCAD.** `machinome snapshot --renderer
openscad` requires the engine before the node is loaded, then, inside the
project build lock right after `assemble()`, writes the root's `.scad` at its
own `scad_file` for the snapshot's pose (`OpenScadRenderer.present`), its
imports re-anchored onto that directory (ADR-116). After OpenSCAD has read it,
whether the render succeeded or failed, the renderer removes the file and its
currency record in a `finally` (`withdraw`), unless the root is itself
SCAD-authored. The lock is not held through the OpenSCAD read; a build in that
interval may remove the file and the render fails naming it, where before the
same interval silently drew the build's pose. `--renderer web` writes and reads
no SCAD.

**The sweep keeps a `.scad` by reference.** `kept()` no longer spares `.scad`
by suffix. The sweep walks the builder's tree and keeps the `scad_file` of
every node whose `scad_authored` holds, with its record, whether or not this
build rewrote it; every other `.scad` and its record is removed. The rule holds
on every successful build: when the document is unchanged and the rest of the
sweep does not run, the `.scad` rule alone is applied
(`_sweep_unreferenced_artifacts(snapshot, scad_only=True)`), so a `.scad` no
current node writes never survives a successful build. `collect_snapshots`
goes with the builder's presentation.

**Absence is refused by name.** The seam provides `require_scad_engine(needed_by,
reason, alternative=None)` and `ScadEngineUnavailable`, naming what needed the
engine, why, the module that could not be found and its install today:
`install SolidPython with 'pip install solidpython2'` for `solid2`;
`reinstall machinome, whose distribution carries the OpenSCAD engine` for
`machinome.openscad` or the provider. No extra is named until one exists
(cycle 7). The requiring paths are exactly `scad_code`, `generate_scad()`, a
SCAD-authored leaf's materialization and the OpenSCAD snapshot renderer
(`alternative='use --renderer web'`); a node is named by its name and its own
class. `OpenScadUnavailable` derives from `ScadEngineUnavailable`, its message
unchanged.

### Why not B

It changed no ratified behaviour, but the deliverables it kept served a reader
machinome does not have: no build, document, viewer, export or test reads an
assembly's `.scad`, and the one consumer, the snapshot renderer, reads only
the root's, which it now writes for itself. Rejected by the pilot.

### The correction of 4 October 2026

The applier found that the sweep ran only when the published document changed
(`_write_viewer_snapshot_with_inventory` returned before sweeping on a
byte-identical document), so the first form of this decision ("the next build
removes the snapshot's root `.scad`") did not hold. The orchestrator decided
that the `.scad` rule alone runs on an unchanged document, leaving every other
artifact's trigger as it was (what `machinome test` writes for other parameter
sets still survives an unchanged build), and that the renderer owns its file's
lifetime.

### `assemble()` no longer rewrites a consumed `.scad`

Before this decision `assemble()` could overwrite a SCAD-authored leaf's
`.scad` after OpenSCAD had rendered the STL from it, in two shapes. Across
processes: a later process's `assemble()` of a current `Solid2Node` set its
model to an import of its own STL and wrote that over the file, so after a
build, a test and an export Pin_tumbler_lock's `parts-*.scad` were mostly
self-imports (`import(file = "parts-Core,...stl")`, 215 bytes) where the
build had written `part(cuts = [...], ...)` (237 bytes); had the STL gone
stale under the same name, OpenSCAD would have rendered an empty import.
Nothing overwrites the file now; a single-process build of the old code and a
build under this decision write the same 11 files byte for byte. Within one
process, the second shape: a `Solid2Node` declaring `optimize = False` and a
`color` materializes its
authored model, uncoloured, from which OpenSCAD renders its STL. Before this
decision `assemble()` then overwrote that file with the coloured
presentation, after the render; nothing does now. In the presentation
golden's fixture the file goes from 82 bytes (`color(...) { cylinder(...) }`)
to 24 (`cylinder(h = 5, r = 2);`), the text the STL was made from. The
parent's presentation keeps the colour. Accepted by the orchestrator as a
correction of the change's "no byte moves"; the pilot may overrule it.

## Consequences

- BREAKING for OpenSCAD users: a build writes no assembly, fusion, flexible or
  native-leaf `.scad`, and the next build removes those earlier builds left.
  A machine's SCAD text is `node.scad_code`.
- A project of exact, STEP or STL leaves builds, tests, exports and publishes
  with SolidPython or the engine absent, writing no `.scad`.
- ADR-086's assembly-phase coalescing of non-rigid SCAD has no production
  producer; its tests drive it directly. Its removal is a candidate, not this
  decision's.
- `LeafNode._render_can_be_skipped`, which consults `.scad` currency and has
  no production caller since ADR-102, is a candidate for removal.

## References

- `machinome/core/builder.py`, `machinome/manager/{snapshot,develop}.py`,
  `machinome/viewers/openscad.py`, `machinome/scad_engine.py`,
  `machinome/openscad/binary.py`
- `tests/test_scad_presentation.py`, `tests/test_builder_lifecycle.py`
- `openspec/specs/backend-neutral-materialization/spec.md`,
  `openspec/specs/build-pipeline/spec.md`, `openspec/specs/web-snapshot/spec.md`,
  `openspec/specs/scad-engine-dependency/spec.md`
