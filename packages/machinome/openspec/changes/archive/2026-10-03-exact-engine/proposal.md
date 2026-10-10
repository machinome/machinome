## Why

The lean-core campaign (`workflow/ongoing/lean-core.md`, item 3 of "What it
takes") needs exact geometry to be a kernel package the core resolves, not a
module the core carries. Three facts make that the next step:

- **The one third-party exact leaf cannot get the engine without CadQuery.**
  machinome-freecad's adapter (`machinome_freecad/adapter.py`, `_leaf_class`)
  reads a FreeCAD BREP into a bare `TopoDS_Shape` with OCP and then imports
  cadquery for one reason: `cq.Shape.cast(shape)`, because the exact layer's
  currency is CadQuery's `Shape`. It also imports the private
  `machinome.exact._evict` twice, because the shape cache keys on
  `(path, mtime)` and the framework stamps every artifact with its source's
  mtime, so a BREP the adapter replaces under an unchanged source is served
  stale unless it reaches into the cache.
- **The exact layer is the core's only CadQuery use outside its adapters.**
  `machinome/exact.py` imports cadquery at module top for four spellings
  (`Shape.cast` four times, `Shape.importBrep`, `Compound.makeCompound`,
  `Vertex.makeVertex`) and trades in CadQuery `Shape` objects whose methods
  (`Solids`, `Faces`, `Edges`, `Vertices`, `Volume`, `BoundingBox`, `copy`,
  `exportBrep`, `exportStl`, `distance`, `positionAt`, `Length`, `toTuple`)
  it and the test kernel call; every boolean and transform already goes
  through OCP (ADR-047). Through it, `node/fusion.py` imports cadquery and
  OCP at module top.
- **The pin coupling.** cadquery 2.8 moved to cadquery-ocp 7.9 and build123d
  0.11 to cadquery-ocp-novtk; requiring both in one package blocks both
  upgrades (`pyproject.toml`, ADR-047's consequence). An engine that depends
  on cadquery-ocp alone is the precondition for letting each front end move
  on its own.

The pilot's ruling on the first draft of this change fixes its shape: an
operation on an OCCT shape is a capability of the OCCT package, not of the
core, and "a model that is purely OpenSCAD based should have no BREP". The
core therefore holds no OCCT code and defines no operation on OCCT shapes
under its own name.

## What Changes

- **An exact engine seam in the core**, of the mesh engine's shape:
  `exact_engine()` returns the engine or `None`; `require_exact_engine(needed_by,
  reason)` raises one actionable error naming `pip install "machinome[occt]"`.
  It resolves on first use by a try-import of the one known provider module,
  `machinome.occt.engine`. No entry-point group, no registry (the plan's D2).
- **A versioned engine contract.** The core declares the contract version it
  speaks and a `Protocol` naming the operations it calls, by the names the
  engine defines them under; the provider declares the version it implements;
  the seam compares them at resolve time and refuses a mismatch naming both
  versions (package standard, section 1.2).
- **The engine at its final address, holding every OCCT operation.** The OCCT
  work of `machinome/exact.py` and the containment guard of `machinome/test.py`,
  rewritten on bare OCP with no cadquery import, become
  `machinome/occt/engine.py` inside the core's tree, under a
  `machinome/occt/__init__.py` that exports nothing, so the cut cycle moves the
  directory into the machinome-occt repository unchanged. One module is both
  the provider and the project's address; each operation is defined there once
  under one name.
- **BREAKING: `machinome.exact` is removed.** Its project-facing operations,
  `intersect_shapes`, `fuse_shapes`, `placed_shape`, `solid_count` and
  `solid_volume`, are defined in `machinome.occt.engine` with the same
  signatures, and projects import them from there. They are operations, not
  node types, so the plan's rule that machinome-occt carries no node type is
  untouched. The common-guard error types move to the seam module,
  `machinome.exact_engine`.
- **The core keeps only what an abstract exact node needs**, none of it OCCT
  code: `ExactLeafNode` and the exact branch of `FusionNode`, which pass the
  engine's currency as an opaque handle; the seam and its contract; the test
  framework's exact path, which calls contract operations in its culling order;
  the memos over handles and artifact files, in `machinome/exact_cache.py`;
  artifact publication, in `machinome/exact_artifacts.py`; and the persistent
  verdict memo of ADR-156, unchanged.
- **BREAKING: `shape()` returns the engine's currency.** The core's specs name
  no OCCT type: every exact node returns the one type the engine declares, and
  a consumer that wants a front end's methods rewraps it. Which type that is
  is the engine's decision, stated in the engine's own capability and ADR, and
  put to the pilot there: the bare `OCP.TopoDS.TopoDS_Shape` is the
  recommended and expected answer (design.md Decision 3). Project code that
  calls CadQuery methods on a returned shape wraps it with
  `cadquery.Shape.cast(...)`.
- **The render-to-currency conversion moves to the adapters.** `ExactLeafNode`
  converts a render result by the engine's `as_shape`; `CadQueryNode` and
  `StepNode` add CadQuery's `Workplane`, `Build123dNode` adds build123d's
  builder. The engine knows no front end.
- **`node/fusion.py` resolves the engine lazily**; its exact recipe keeps its
  identity `exact-fusion-occt-v1`; the faceted path is untouched.
- **`MolejoNode` returns molejo's own solid** and stops importing cadquery.
- **The `occt` extra is declared.** `pyproject.toml` gains
  `occt = ["cadquery-ocp>=7.8.1,<7.9"]`, the range the core's pinned cadquery
  2.7 already resolves to, with a comment that the cut repoints it at
  machinome-occt, so the refusal's install line is true from this cycle.
- **Dependencies do not change.** cadquery, build123d, cadquery-ocp and molejo
  stay required: the CadQuery, build123d and STEP adapters still import their
  libraries. The `occt` extra is metadata naming a dependency the core already
  resolves; it changes no resolution. Removing the pins is item 4 of the plan,
  the cut cycle.

Deferred, by the orchestrator's sequencing, and recorded in design.md: the
markings SVG reducer and its refusal by extra (it waits for the cut); the
declared `LeafNode` and `ExactLeafNode` extension contract and the public
replacement for `_evict` (the next cycle, which runs after this one because
that contract names the engine's currency); the class-name switch at
`node/base.py:1262`; items 4, 5 and 6 of the plan; the studio's contract
skill.

## Capabilities

### New Capabilities

- `exact-engine-dependency`: the seam, in the core. The exact engine as a
  conditional, versioned dependency resolved through one module: which paths
  resolve it, that the core holds no kernel code and treats exact shapes as
  opaque handles, the actionable refusal when it is absent, the contract
  version check, and the one place the core names its provider.
- `occt-engine`: the engine, `machinome.occt.engine`. Its currency (the bare
  `TopoDS_Shape`, the engine's decision), each operation's semantics including
  the empty-common witness and its refusals, the five project-facing
  operations and their signatures, the contract version it declares, and what
  it imports (OCP and numpy, never cadquery, build123d or trimesh). It governs
  behaviour that leaves the core at the cut, so it leaves with the code
  (package standard, section 1.3).

### Modified Capabilities

- `exact-geometry`: `shape()` returns the exact engine's currency, one type for
  every exact node, which the core never inspects; an exact render is admitted
  by the engine's own rule; exact geometry needs no CAD front end.
- `cli-startup-cost`: "The test framework does not import the exact-geometry
  stack" is restated for the seam: importing `machinome.test` imports neither
  cadquery, OCP nor the engine, and the exact path looks each name up where it
  is defined, so a patch is applied there.
- `test-framework`: the empty-common witness requirement names
  `machinome.occt.engine.intersect_shapes` in place of
  `machinome.exact.intersect_shapes`.
- `vet`: the public contract a project may import names `machinome.occt.engine`
  in place of `machinome.exact`, and the contract denylist gains the exact
  internals `machinome.exact_cache` and `machinome.exact_artifacts` and the
  engine's file operations `read_brep`, `write_brep` and `write_stl`.

## Impact

- **Code.** New: `machinome/exact_engine.py`, `machinome/exact_cache.py`,
  `machinome/exact_artifacts.py`, `machinome/occt/__init__.py`,
  `machinome/occt/engine.py`. Removed: `machinome/exact.py`. Changed:
  `node/exact_leaf.py`, `node/fusion.py`, `node/adapters/{cadquery,build123d,
  build123d_sheet,step,molejo}.py`, `test.py`, `manager/test.py`,
  `pyproject.toml` (the `occt` extra), `vet/universe.toml` (the deny list). Docstrings that name `machinome.exact`
  (`node/__init__.py`, `core/loader.py`, `simulation/__init__.py`,
  `node/adapters/{step,stl}.py`) are corrected.
- **Public interface.** `machinome.exact` goes; its five operations are
  imported from `machinome.occt.engine`. `shape()` and those operations return
  the engine's currency. Measured over `projects/` on 2 October 2026 by the
  orchestrator, these are the rows the one-path cycle's rewrite script carries:
  12 project files import from `machinome.exact` (Curta-Type-I-3x 11,
  OpenAstroMount 1; re-checked by this revision), whose import line moves to
  `machinome.occt.engine`; and 29 project files call a CadQuery method directly
  on a `shape()` result (`translate`, `rotate`, `isValid`, `Solids`, `Volume`,
  `cut`, `Faces`, `Edges`, `tessellate`, `intersect`, `copy`, `BoundingBox`),
  which gain `cadquery.Shape.cast(...)`. The earlier figure of 263 `.shape()`
  call sites in 151 files is the upper bound of all `shape()` calls; most pass
  the shape to an assertion or an operation and need nothing. `StepNode.adjust`
  still receives a CadQuery `Shape` in this cycle.
- **Artifacts.** BREP and STL bytes are unchanged: on a fused fixture the
  raw-OCP writers produce the same SHA-256 as CadQuery's `exportBrep` and
  `exportStl`, across processes (probe of 2 October 2026). Exact fusion keeps
  `exact-fusion-occt-v1`. The verdict store starts afresh once, because its
  stamp digests the package source (ADR-156).
- **Docs.** `docs/architecture.md` (exact layer, test kernel, source map),
  `docs/reference/assertions.rst` (the direct operation's address and
  signature, the error types' module), the changelog's Unreleased section, and
  the campaign plan `workflow/ongoing/lean-core.md` (the engine's
  project-facing operations, the sequencing). The studio's contract skill is
  updated once, at the cut.
- **Downstream.** machinome-freecad's adapter keeps rendering through
  `.wrapped` and may drop its cadquery import; its `_evict` import breaks and
  is the next cycle's subject (it is pinned to 0.7.1 and does not run against
  this line anyway).
