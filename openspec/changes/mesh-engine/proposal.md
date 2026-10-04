## Why

The lean-core campaign (`workflow/ongoing/lean-core.md`) builds machinome as a
core with engine and node packages around it, for the architecture and for a
lean install that carries only what a project uses. The pilot settled on
4 October 2026 that the core stays Apache-2.0 and that the next cycle is "the
extraction of manifold3d behind the mesh seam, for the architecture alone, by
the same shape as the exact engine" (the plan, "Settled by the pilot, 4 October
2026, later the same day: the grant stays Apache-2.0"); watchdog stays as it
is. This change is that cycle, the seventh of layer 1.

The mesh engine today is the one kernel the core still calls itself:

- **The seam imports the kernel itself.** `machinome/mesh_engine.py:36` is
  `from manifold3d import Manifold, Mesh`, and `mesh_engine()` hands the two
  classes to its callers. There is no provider module, no contract version and
  no extra; its refusal says `pip install manifold3d` (`mesh_engine.py:26`).
- **The core calls manifold3d's API.** `machinome/test.py` constructs
  `Manifold(mesh=Mesh(...))` in three places (lines 354, 392, 416), reads
  `.status()` (314), places with `.transform(matrix[:3, :4])` (751, 1812,
  1813, 1433), intersects with `^` (1061, 1360, 1814), reads `.is_empty()`
  and `.volume()` (1063, 1065, 1361, 1815, 1816), meshes back with
  `.to_mesh()` (1298) and builds the statics' virtual floor with
  `Manifold.cube` (1433). `machinome/node/fusion.py` (lines 123-156) builds,
  checks, unions (`+`) and meshes back the faceted fusion the same way.
- **The core reaches the kernel through trimesh as well.** `assertJoined`'s
  faceted union (`test.py:2495`, `trimesh.boolean.union`) and the `.mesh`
  fallback of the intersection helper (`test.py:1884`,
  `trimesh.boolean.intersection`) run trimesh 4.4's `boolean_manifold`, which
  is manifold3d (read from the installed trimesh 4.4.9, 4 October 2026).
- **The verdict store names it.** `machinome/_verdict_store.py:111` stamps every
  verdict, exact ones included, with `('manifold3d', 'manifold3d')`.
- **It is a required dependency.** `pyproject.toml` lists `manifold3d` among
  the core's requirements, the last CAD kernel there since the `lean-install`
  cycle moved the other four to extras (ADR-167, which kept it required by the
  pilot's ruling of 2 October, now superseded by the 4 October decision).

## What Changes

- **The provider, at its address under the norm.** A new package
  `machinome/manifold/` whose `__init__.py` exports nothing, and its one module
  `machinome/manifold/engine.py`, Apache-2.0 like manifold3d: every operation
  the core performs on a mesh solid, each defined once, written as the code does
  them today. It refuses at import, by the `kernel-extras` rule, when
  `manifold3d` cannot be found, naming `pip install "machinome[manifold]"`.
- **The seam, of the exact engine's shape.** `machinome.mesh_engine` keeps its
  address and its three names. It declares `CONTRACT = 1`, the Protocols of the
  operations the core asks for, and `PROVIDER = 'machinome.manifold.engine'`;
  `mesh_engine()` resolves the provider once per process, compares its
  `CONTRACT` by equality (ADR-162) and answers `None` when the provider or its
  kernel is absent; any other import failure propagates.
  `require_mesh_engine(needed_by, reason)` keeps its signature and now returns
  the provider; its refusal names `pip install "machinome[manifold]"`. A new
  `MeshEngineIncompatible` refuses a contract mismatch naming both versions.
- **The core's mesh solids are opaque handles.** `test.py` and `node/fusion.py`
  keep every cache, order, cull, policy and message they hold, and ask the
  engine for each construction, admission, placement, Boolean, measurement and
  read-back. The two caches stay in the core holding handles, as
  `exact_cache.py` does for the exact engine. `assertJoined`'s faceted union
  and the `.mesh` fallback stop calling `trimesh.boolean` and run the same
  steps through the engine, so the provider is the only module that makes
  manifold3d compute anything for the core.
- **`machinome test` on the faceted kernel refuses at its start** when the mesh
  engine is absent, before any node is built, since every pair of such a run is
  compared on meshes. An exact-kernel run still refuses at the first pair the
  exact kernel does not decide, as today.
- **The verdict store takes the engine's identity from the engine.** The
  process stamp drops its `manifold3d` row; every faceted verdict's persisted key
  carries the identity (name and version) the resolved engine reports, and an
  exact verdict carries none. Every store starts afresh once (ADR-156: the
  stamp digests the package source, which this change alters).
- **BREAKING: the plain install no longer carries manifold3d.** `pyproject.toml`
  moves `manifold3d` to a new `manifold` extra (`pip install
  "machinome[manifold]"`); `all`, and through it `dev`, CI and tox, take it.
  `machinome test --faceted`, a faceted comparison (any pair that is not two
  exact nodes on the exact kernel), `assertAssemblySupported` over two or more
  solids and a stale faceted `FusionNode` now need `machinome[manifold]`, and
  refuse by that name without it.
- **`tests/mesh_engine_absent.py` takes the finder form** of
  `tests/exact_engine_absent.py`: a `sitecustomize` finder in every process of
  a run, refusing `manifold3d`, `machinome.manifold` or both, with a per-process
  log of how often each was asked for and by which module.

Not in this change, by the pilot's scope of 4 October 2026: watchdog (it
stays), any second mesh engine, any change to what an assertion means or
decides, the WebAssembly surface, and the package split (no distribution is cut
in layer 1; the later distribution `machinome-manifold` is layer 2). No
importable name moves: `machinome.mesh_engine`, `MeshEngineUnavailable`,
`require_mesh_engine` and `mesh_engine` keep their addresses, so this cycle's
`moved-names.toml` is empty.

## Capabilities

### New Capabilities

- `manifold-engine`: the provider, `machinome.manifold.engine`. Its package
  that exports nothing, its contract declaration, what it imports and how it
  refuses an absent kernel, and each operation's semantics, written so that
  every verdict and every fused STL is the one the core computes today. It
  governs behaviour that leaves the core with the provider in layer 2 (package
  standard, section 1.3), as `occt-engine` does.

### Modified Capabilities

- `mesh-engine-dependency`: the seam resolves one known provider, declares and
  checks a contract version, reads an absent kernel as an absent engine, lets a
  broken one report itself, and names `machinome[manifold]`; the core holds no
  mesh-engine code and names the provider in one module; the requiring paths
  gain the faceted run's start, and `assertJoined`'s union and the `.mesh`
  fallback join them, leaving trimesh's own backend selection with the
  proximity queries only.
- `kernel-extras`: `manifold3d` leaves the required dependencies for the
  `manifold` extra, in `all`; `machinome.manifold.engine` is a kernel module
  refusing by its extra; the core imports `manifold3d` only there.
- `test-framework`: the `.mesh` fallback and the faceted fast path are stated
  in terms of the mesh engine's operations ("Accelerated intersection
  evaluation"), and a faceted verdict kept between runs is bound to the mesh
  engine's identity, an exact one is not ("A decided verdict is kept between
  runs of a project").

## Impact

- **Code.** New: `machinome/manifold/__init__.py`, `machinome/manifold/engine.py`.
  Changed: `machinome/mesh_engine.py`, `machinome/test.py`,
  `machinome/node/fusion.py`, `machinome/_verdict_store.py`,
  `machinome/manager/test.py`, `pyproject.toml`, `requirements.txt`;
  docstrings and comments naming a Manifold in the core
  (`machinome/node/flexible.py:375,422`, `test.py`'s own). Unchanged: `machinome/extras.py` (it holds no table by design,
  ADR-167; the provider states its own extra), `machinome/vet/universe.toml`
  (a project may still import `manifold3d` directly, and the provider writes no
  file).
- **Public interface.** No importable name moves. `require_mesh_engine` and
  `mesh_engine` return the provider module instead of the pair `(Manifold,
  Mesh)`; nothing in `projects/` calls either (grep of 4 October 2026: no project
  names `machinome.mesh_engine`, `require_mesh_engine` or any private cache of
  `machinome.test`).
- **Install.** `pip install machinome` stops installing manifold3d. Seven
  project directories import `manifold3d` themselves (grep of 4 October 2026,
  files: Curta-Type-I-3x 80, Voron-2 3, Pascaline-module 2, hangprinter 1,
  snappy-reprap 1, hexapod_spiderbot_model 1, openvmp 1) and sixteen call
  `trimesh.boolean`, which is manifold3d underneath (Prusa3-vanilla's
  `shared_volume` among them); every such project, and every project with a
  faceted part it tests, installs `machinome[manifold]`. design.md, "Migration".
- **Artifacts and verdicts.** None changes: the same manifold3d calls run on the
  same arrays in the same order, so every verdict, every refusal's status and
  every faceted fusion STL is bit-identical; a golden recorded on the unmodified
  tree proves it (tasks 1.2 and 4.8). The faceted fusion's recipe identity
  `faceted-fusion-manifold-v1` is kept, so no artifact is rebuilt. The verdict
  store starts afresh once.
- **Messages.** The two refusals name `machinome[manifold]` in place of
  `pip install manifold3d`; the faceted fusion's admission refusal says
  `manifold3d reported NotManifold` where it said `manifold3d reported
  Error.NotManifold` (design.md Decision 4).
- **Docs.** `docs/architecture.md` (the test-framework paragraphs, the source
  map), `docs/start/install.rst` (the extras table, the plain install),
  `docs/howto/fast-tests.rst` (the faceted kernel needs the extra),
  `README.rst` (the manifold3d paragraph), the changelog's Unreleased section,
  and the campaign plan `workflow/ongoing/lean-core.md`.
- **Originating evidence.** The pilot's decision of 4 October 2026 recorded in
  the plan's "Settled by the pilot, 4 October 2026, later the same day" and its
  "Struck or deferred by the pilot" paragraph ("the pilot takes manifold3d up
  next"), and the plan's "Aim" (a core with kernel packages, a project installing
  only what it needs).
