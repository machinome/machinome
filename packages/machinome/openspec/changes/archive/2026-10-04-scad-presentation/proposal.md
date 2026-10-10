## Why

The lean-core campaign's "Layers" ruling (pilot, 3 October 2026,
`workflow/ongoing/lean-core.md`) builds layer 1, the internal architecture of
the whole split, OpenSCAD included, before layer 2, the package split whose
requirement is that a GPL-2.0-only project imports machinome with no
Apache-2.0 code beneath it. Cycle 5 (`expression-type`, ADR-170, ADR-171) made
the symbolic value the core's own type and gave the OpenSCAD engine its
address, `machinome.openscad`, behind the seam `machinome.scad_engine`. This is
cycle 6: "the SCAD presentation behind a seam, `assemble()` no longer
requiring it, the `develop` fallback included". It completes the direction
ADR-102 set (native materialization precedes an *optional* SCAD presentation):
today the presentation is optional in when it runs, but not in what it needs,
because the node base itself composes it with SolidPython.

The originating evidence, read in the bench at a4a1f84 on 3 October 2026:

- **Four core modules compose SCAD with SolidPython** (cycle 5's AST walk):
  `node/base.py` (`scad_render`, `import_stl`, `color`: `assemble`,
  `scad_code`, `generate_scad`, `_ArtifactImport`, `_colorize`,
  `_reanchor_artifact_imports`, which walks SolidPython's private `_children`
  and `_params`), `node/operations.py` (`rotate`, `translate`:
  `Rotation.scad`, `Translation.scad`), `node/internal.py` and
  `node/flexible.py` (`union`). Because `node/base.py` imports `solid2` at
  module top, no node, and so no build, export, test or document, exists
  without SolidPython, even for a project whose every leaf is exact or STL.
- **Three core modules reach the engine's package directly** for the binary
  locator, outside the seam: `node/base.py`, `viewers/openscad.py`,
  `manager/snapshot.py` (the fourth, `node/solid2.py`, is a leaf; cycle 7).
- **`assemble()` is the most-used SCAD entry point and its SCAD is not what
  its callers want**: 210 Python files in 17 top-level project directories call
  `node.assemble()` (grep of `projects/` excluding worktrees, builds and
  archives, 3 October 2026), none uses its
  return value, and the studio's contract skill teaches `.assemble()` then
  `.build_stls()` to prepare a node "for mesh use"; no project overrides `as_scad` or calls
  `artifact_import`, `scad_code` or `generate_scad`.
- **Who reads a generated `.scad`** (design.md, "Who reads SCAD"): OpenSCAD,
  for a `Solid2Node`'s, an `OpenScadNode`'s or a legacy SCAD-only leaf's own
  STL; the OpenSCAD snapshot renderer, for the root's; a person opening it in
  the OpenSCAD GUI; and the framework's own tests. No build, published
  document, viewer, export or `machinome test` reads one. `machinome develop`
  has had no OpenSCAD fallback since ADR-103 (11 September 2026): without the
  viewer package it refuses naming the `viewer` extra, and its builder never
  presents SCAD (`scad_output=False`, ADR-102).

## What Changes

- **The core describes its SCAD presentation; the OpenSCAD engine writes it.**
  `assemble()`, `as_scad()` and the operations compose a small, immutable,
  core-owned *presentation description* (`machinome.node.presentation`): an
  import of a build artifact, a colour, a rotation, a translation, a union, and
  the opaque geometry a SCAD-presented leaf authored itself. The values a
  rotation or translation carries travel in it as the operation holds them,
  numbers or the core's symbolic values. The engine turns a description into
  SCAD text (`scad_text`) with SolidPython, byte for byte the text the core
  writes today. `node/base.py`, `operations.py`, `internal.py` and
  `flexible.py` import no SolidPython; re-anchoring an artifact import onto
  the directory of the `.scad` that holds it (ADR-116) becomes a pure function
  over the core's own description, with no walk of SolidPython's privates and
  no deep copy.
- **`assemble()` needs neither SolidPython nor the engine and writes no
  SCAD.** It prepares and links the tree as today and returns the node's
  presentation description; it writes no `.scad` at any node, with or
  without the engine.
- **A `.scad` is written only where a path reads it** (the pilot's decision,
  3 October 2026; design.md, Decision 3). A build writes the `.scad` of a
  SCAD-authored leaf (`Solid2Node`, `OpenScadNode`, a project leaf
  overriding `as_scad`), from which OpenSCAD renders its STL, and no other;
  the builder no longer presents SCAD, so `Builder`'s `scad_output` goes and
  `machinome build` and `develop`'s builder are one pipeline. `machinome
  snapshot --renderer openscad` writes the root's `.scad` on demand, through
  the seam, in the build directory at the root's own path, for the pose it
  renders, and removes it once OpenSCAD has read it, whether the render
  succeeded or failed (correction of 4 October 2026, design.md Decision 3);
  `--renderer web` writes none. With the engine absent a build
  writes no `.scad` because nothing asks for one, and a SCAD-authored leaf
  meets its existing refusal. The build sweep keeps a `.scad` by reference,
  only for a SCAD-authored leaf of the published tree, and removes every
  other, so the files earlier builds left go at the next build: on every
  successful build, also one that republishes an unchanged document, where
  the `.scad` rule alone is applied and every other artifact keeps today's
  trigger.
- **Asking for SCAD text without the engine is refused actionably.** The seam
  gains `require_scad_engine(needed_by, reason, alternative=None)` and
  `ScadEngineUnavailable`, naming what needed the engine, why, which module is
  missing and the install that provides it today (`pip install solidpython2`
  for SolidPython; reinstalling machinome for its own engine package; cycle 7
  replaces both with the `openscad` extra). `scad_code`, `generate_scad()`, a
  SCAD-authored leaf's materialization and the OpenSCAD snapshot renderer
  require it; the renderer's refusal names `--renderer web`. A build of a
  tree with no SCAD-authored leaf asks for none, so it neither requires the
  engine nor logs anything about it.
- **The seam's contract moves to 2.** `machinome.scad_engine.CONTRACT` and
  `machinome.openscad.engine.CONTRACT` are 2: `adopt` (1), `scad_text` and
  `require_binary` (2). The binary is reached through the seam by
  `node/base.py` and the snapshot renderer; `manager/snapshot.py` catches the
  seam's `ScadEngineUnavailable`, of which `OpenScadUnavailable` becomes a
  subclass with its message unchanged. Only the seam and `node/solid2.py`
  (cycle 7) still import `machinome.openscad`.
- **BREAKING (build output, for OpenSCAD users):** `machinome build` no
  longer writes the `.scad` of an assembly, of a fusion or of a flexible
  leaf (nor the import wrapper of a native leaf: exact, STEP, STL, JScad,
  sheet), nor a flexible leaf's per-binding snapshot STL, and the next build
  removes those an earlier build left. For Pin_tumbler_lock that is 3 of the
  14 files: the root's, the `Plug` assembly's and the `PenSpring`'s. A
  machine's SCAD is obtained on demand: `node.scad_code` gives any node's
  text; `machinome snapshot --renderer openscad` writes the root's only for
  OpenSCAD to draw and removes it afterwards.
- **BREAKING (framework-internal):** `assemble()` and `as_scad()` return the
  core's presentation description rather than a SolidPython object, and
  `artifact_import()` returns the description of an import; `Rotation.scad()`
  and `Translation.scad()` are removed. No project or sibling package uses any
  of them (grep, 3 October 2026). The leaf contract stays at version 1: a
  SCAD-presented leaf's `as_scad` still returns the SolidPython object it
  authored (design.md, Decision 6, accepted by the orchestrator).
- **Unchanged, byte for byte:** every `.scad` still written (a SCAD-authored
  leaf's; the root's from the OpenSCAD snapshot renderer, for the same pose),
  every node's `scad_code`, the published document, the viewer, `develop`,
  export, `machinome test`, the OpenSCAD snapshot image. One exception, by
  construction (design.md Decision 8, corrected 4 October 2026): the `.scad`
  of a SCAD-authored leaf declaring `optimize = False` and a `color` is the
  uncoloured text OpenSCAD renders its STL from, no longer overwritten with
  its coloured presentation afterwards.

Deferred, recorded in design.md: the runner (`stl_builder_command_for`,
`StlRenderStart`'s OpenSCAD command, the snapshot renderer's command line),
`Solid2Node` and `OpenScadNode` as node modules over the engine,
`Solid2Node.as_number`, the `openscad` extra and its refusal (cycle 7); the
template (cycle 8).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `scad-engine-dependency`: the contract is version 2; the seam names the
  paths that require the engine and refuses its absence actionably; the core
  reaches `machinome.openscad` only through the seam; the core composes no
  SCAD text.
- `openscad-engine`: the provider writes the SCAD text of a core presentation
  description, byte-identical to the core's former output, and locates the
  binary for the core; `CONTRACT = 2`; the solid2 importers of the framework
  are the engine package, the two OpenSCAD leaves and the template.
- `backend-neutral-materialization`: "SCAD remains a supported output and
  compatibility boundary" restated: `assemble()` returns the core's
  presentation description, requires no engine and writes no SCAD; SCAD text
  is produced only where a path reads it; OpenSCAD users obtain a machine's
  SCAD on demand.
- `node-model`: "Composite node tree" and "Template-method render
  lifecycle": `assemble()`'s result is the presentation description; it
  requests no SCAD presentation and writes no `.scad`.
- `build-pipeline`: "Build artifact layout": a build writes `.scad` only for
  SCAD-authored leaves; "A successful build sweeps unreferenced artifacts":
  a `.scad` is kept by reference, not by kind; "Generated SCAD imports
  resolve from the file that holds them": its scenarios generate the SCAD
  they read rather than finding it left by a build.
- `leaf-contract`: "What a leaf provides, by kind": the OpenSCAD engine, not
  the core, writes a SCAD-presented leaf's SCAD; `artifact_import` returns the
  core's description of an import, returned from `as_scad` as it is.
- `web-snapshot`: "The renderer is selected explicitly and never substituted":
  the OpenSCAD renderer without the engine fails naming the engine and the web
  renderer, as without the binary; added, "The OpenSCAD renderer writes the
  root's SCAD on demand": the root's `.scad` in the build directory, through
  the engine, for the snapshot's pose; the web renderer writes none.

`openscad-dependency` needs no delta: it names the paths that require the
binary, not a SCAD deliverable, and those paths are unchanged.

## Impact

- **Code.** New: `machinome/node/presentation.py`. Changed:
  `machinome/scad_engine.py` (contract 2, `require_scad_engine`,
  `ScadEngineUnavailable`, the remembered missing module),
  `machinome/openscad/engine.py` (`scad_text`, `require_binary`, `CONTRACT =
  2`), `machinome/openscad/binary.py` (`OpenScadUnavailable`'s base),
  `node/base.py`, `node/operations.py`, `node/internal.py`, `node/flexible.py`,
  `node/openscad.py` (its `scad_code` asks the engine for the text; the
  `scad_authored` predicate), `node/solid2.py` (the predicate only),
  `node/leaf.py` (the predicate for a legacy leaf), `viewers/openscad.py`,
  `manager/snapshot.py` (the root's SCAD written on demand for the OpenSCAD
  renderer), `core/builder.py` (no presentation, no `scad_output`, the sweep
  keeping `.scad` by reference, `collect_snapshots` removed),
  `manager/develop.py` (no `scad_output`). No dependency changes;
  solidpython2 stays required until cycle 7.
- **Public interface.** What a project spells does not change: no project
  overrides `as_scad`, calls `artifact_import`, `scad_code`, `generate_scad`
  or an operation's `.scad()`, or uses `assemble()`'s return value. The
  studio's contract skill names none of them. `moved-names.toml` is empty
  (no importable name moves).
- **Artifacts and documents.** No document changes and no document version
  moves. A build directory holds `.scad` only for SCAD-authored leaves (and
  the root's while an OpenSCAD snapshot draws it); a flexible
  leaf's per-binding snapshot STL is no longer written by a build. The
  persistent verdict store starts afresh once, as on every framework source
  change (ADR-156).
- **Tests.** The framework tests that render `assemble()`'s result with
  `scad_render` or patch `machinome.node.base.require_openscad` are rewritten
  onto the seam; the tests that read an assembly's or native leaf's `.scad`
  a build or `assemble()` left generate it first or assert its absence; the
  sweep test stops sparing `.scad` by kind; cycle 5's AST lists shrink.
- **Docs.** `docs/architecture.md` (the SCAD presentation paragraphs, the
  operations' consumers, ADR-116's re-anchoring, the source map),
  `docs/concepts/publishing.rst` (the build directory holds `.scad` only for
  OpenSCAD-family parts, and the root's after an OpenSCAD snapshot), the
  changelog, the API
  reference's `LeafNode.as_scad` and `artifact_import`, and the campaign plan.
- **Outside the framework (findings, not this cycle's edits).** The
  workspace contract (`CLAUDE.md`, "machinome-viewer work"), the studio's
  craft skill (`shop-skills/machinome/SKILL.md`, line 40) and contract skill
  (`shop-skills/machinome-api/SKILL.md`, lines 2475 and 2511-2513) still say
  `machinome develop` opens OpenSCAD without the viewer and list
  `--openscad`; both were removed by ADR-103 on 11 September 2026. Nothing in
  this cycle changes a line of the studio skill.
