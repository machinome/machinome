## Context

The seventh cycle of layer 1 of the lean-core campaign
(`workflow/ongoing/lean-core.md`). Its scope is the pilot's decision of
4 October 2026, recorded in the plan under "Settled by the pilot, 4 October
2026, later the same day": "the extraction of manifold3d behind the mesh seam,
for the architecture alone, by the same shape as the exact engine"; watchdog
stays; the core stays Apache-2.0. The norm of "Import paths" (2 October 2026)
and the seam rules of D2 govern the names. The model is the archived
`exact-engine` cycle (`openspec/changes/archive/2026-10-03-exact-engine/`), its
seam `machinome/exact_engine.py` and provider `machinome/occt/engine.py`, and
the ADRs it and its successors produced: ADR-161 (the core holds no kernel
code), ADR-162 (a provider declares its contract version), ADR-167 (a kernel is
an extra and its module refuses its absence at import). This change amends
ADR-052 (the conditional mesh engine), which rejected an optional extra on
23 August 2026 because "every ordinary `pip install` would then produce a
silently faceted-broken installation"; Decision 8 answers that objection.

Facts below were read in the bench at 69c7019 on 4 October 2026 unless marked
*inferred*. Probes ran in the bench's interpreter (`.venv`, Python 3.12.3,
trimesh 4.4.9, manifold3d 3.5.2).

### Where the core reaches manifold3d today

Every site, by file and line, and the operation each asks of the kernel:

| site | today | what the core needs |
|---|---|---|
| `mesh_engine.py:36` | `from manifold3d import Manifold, Mesh`, returned as a pair | resolve a provider |
| `test.py:302-322` `_admitted` | `manifold.status()`, `status.name == 'NoError'` | whether the engine admits a solid it built, and its own word if not |
| `test.py:329-360` `_cached_manifold` | `Manifold(mesh=Mesh(vert_properties=float32, tri_verts=uint32))` | a solid from a mesh's vertices and faces |
| `test.py:363-425` `_flexible_manifold`, `_flexible_geometry` | the same construction, twice (392, 416) | a solid from vertices and faces |
| `test.py:727-751` `_DeferredManifold.placed` | `manifold.transform(matrix[:3, :4])` | a solid placed by a matrix |
| `test.py:1027-1068` `_placed_intersection`, faceted branch | `a ^ b`, `.is_empty()`, `.volume()` | intersection; empty or not; volume |
| `test.py:1294-1302` `_placed_mesh` | `.to_mesh()`, `vert_properties[:, :3]`, `tri_verts` | a solid's vertices and faces back out |
| `test.py:1360-1361` `_interface_contacts` | `displaced ^ supporter.manifold`, `.is_empty()` | intersection; empty or not |
| `test.py:1432-1433` `_virtual_floor` | `Manifold.cube(list(size), True).transform(matrix[:3, :4])` | a centred box; placement |
| `test.py:1799-1817` `_faceted_verdict` | two `.transform`, `^`, `.is_empty()`, `.volume()` | placement; intersection; empty or not; volume |
| `test.py:1884-1886` `.mesh` fallback | `trimesh.boolean.intersection([m1, m2])` | (through trimesh) solids from meshes, intersection, mesh back out |
| `test.py:2495-2499` `assertJoined`, faceted branch | `trimesh.boolean.union([m1, m2])` | (through trimesh) solids from meshes, union, mesh back out |
| `node/fusion.py:123-160` `_generate_faceted_stl` | construction, `status()` (as `str(status)`), left fold of `+`, `status()`, `.to_mesh()` | solids from meshes; admission; union of many in order; mesh back out |
| `_verdict_store.py:106-112` `KERNELS` | `('manifold3d', 'manifold3d')` in every process's stamp | the engine's identity |

The two trimesh rows are reaches the brief's site list did not name: trimesh
4.4's `union` and `intersection` dispatch to `boolean_manifold`, which builds
`Manifold(mesh=Mesh(np.array(vertices, float32), np.array(faces, uint32)))`
for each mesh, folds them with `+` or `^`, and returns
`Trimesh(vertices=vert_properties, faces=tri_verts)` (read from
`trimesh/boolean.py` in the venv). Nothing else in `machinome/` calls a
manifold3d API or `trimesh.boolean` (grep of `machinome/`, 4 October 2026).

### What trimesh does at import

`import trimesh` imports `trimesh.boolean`, whose first lines are
`try: from manifold3d import Manifold, Mesh` / `except BaseException`. So
every process that imports trimesh asks the import system for `manifold3d`,
and loads it when it is installed: `python -X importtime -c "import trimesh"`
shows `manifold3d` (3.2 ms) beneath `trimesh.boolean`, and after `import
trimesh` `'manifold3d' in sys.modules` is `True`. `machinome.test` imports
trimesh at its top (line 14). This is why `tests/mesh_engine_absent.py`
imports trimesh before installing its blocker (its docstring), and it shapes
Decision 11 and Open Question 1.

### Who uses manifold3d outside the core

No project names `machinome.mesh_engine`, `require_mesh_engine`, or any private
cache or helper of `machinome.test` (grep of `projects/`, 4 October 2026,
excluding worktrees). Seven project directories import `manifold3d` themselves
(files: Curta-Type-I-3x 80, Voron-2 3, Pascaline-module 2, hangprinter 1,
snappy-reprap 1, hexapod_spiderbot_model 1, openvmp 1) and sixteen call
`trimesh.boolean` (Prusa3-vanilla's `simulation/contracts.py:shared_volume`
among them, with `engine='manifold'` and an `except Exception: return 0.0`).
The only distribution in the venv requiring manifold3d is machinome itself;
trimesh names it only under its `easy` extra.

## Goals / Non-Goals

**Goals:**

- The core names manifold3d in no module but the provider's, calls no method
  of its types, and reaches it through `trimesh.boolean` nowhere.
- One seam of the exact engine's shape: a known provider resolved on first use,
  a versioned contract checked by equality, absence read from the provider's
  own refusal, one refusal naming `machinome[manifold]`.
- `manifold3d` an extra; a plain install carries none, and every path that
  needs it refuses by name.
- Unchanged results: every verdict (empty or not, volume bits), every refusal's
  status word, every fused STL byte, every candidate set and build count.
- A project whose every compared pair is exact never resolves the engine.

**Non-Goals:**

- No second engine, no WebAssembly surface, no change to an assertion's
  meaning (the pilot's scope).
- No distribution `machinome-manifold` (layer 2); the provider ships inside the
  core's distribution, as `machinome.occt` does today.
- No change to watchdog, to the exact engine, or to the exact path's stamp rows
  (`cadquery-ocp`, `cadquery`).
- No vet change: a project may still import `manifold3d` (the universe's kernel
  tier); the provider reads and writes no file, so nothing of it needs denying.

## Decisions

### 1. Names and addresses

Under the norm of "Import paths": the seam keeps its role name in the core,
`machinome.mesh_engine`; the provider takes the technology's name, the package
`machinome.manifold` whose `__init__.py` holds a licence header and a docstring
and no names (the ports spec's sentence, as `machinome/occt/__init__.py`), and
the module `machinome/manifold/engine.py`. The extra is `manifold`, the last
component of the address (the pilot's choice "for now", 4 October 2026); the
later distribution is `machinome-manifold`. The provider's licence header is
Apache-2.0, matching manifold3d's (the policy "a package's licence matches its
provider's"; manifold3d is Apache-2.0, the plan's dependency table).

Rejected: `machinome.mesh` or `machinome.faceted` for the provider (a
capability name, so a second mesh engine would have nowhere to go: the reason
D1 gave for `machinome-occt` over `machinome-exact`); keeping manifold3d inside
`mesh_engine.py` (the seam and the kernel in one module, which ADR-161 forbids
for the exact engine).

### 2. The seam: `machinome/mesh_engine.py`

The exact seam's shape, line for line where it applies:

- `CONTRACT = 1`, the mesh engine contract version the core speaks.
- `PROVIDER = 'machinome.manifold.engine'`, the one place the core names it.
- `MeshSolid = Any`, documented as "the engine's solid; the core never inspects
  it".
- The Protocols of Decision 3, and `MeshEngine` combining them.
- `MeshEngineUnavailable(needed_by, reason)`, its message:

  ```
  {needed_by} requires the mesh engine because {reason}; install it with 'pip install "machinome[manifold]"'. Exact geometry does not need it: a model whose every compared part is exact is decided by the boundary-representation kernel
  ```

  (today's sentence with "the manifold3d mesh engine" made "the mesh engine"
  and the install line made the extra's, in the viewer's and the exact seam's
  quoted spelling).
- `MeshEngineIncompatible(declared)`, its message, `stated` being `declares
  none` or `declares contract version {declared!r}`:

  ```
  The mesh engine machinome.manifold.engine {stated}, but this machinome speaks mesh engine contract version 1; install the engine released with this machinome
  ```

- `_absent(error)`: an `ExtraUnavailable` whose `extra` is `manifold`, or a
  `ModuleNotFoundError` whose `name` is `machinome.manifold` or
  `machinome.manifold.engine`.
- `mesh_engine()`, `functools.lru_cache(maxsize=1)`:
  `importlib.import_module(PROVIDER)`; absence answers `None`; any other import
  error propagates; then the contract check. An exception is not cached, so a
  refused provider is refused at every ask. Today's `mesh_engine()` catches
  every `ImportError` (`mesh_engine.py:37`); the new one lets a broken engine
  report itself, the `cli-startup-cost` broken-installation rule ADR-161 and
  ADR-167 already apply to the exact engine.
- `require_mesh_engine(needed_by, reason)`: same signature, returns the provider
  module or raises `MeshEngineUnavailable`.

`machinome/extras.py` is not changed: it holds no table by design (ADR-167
rejected option 2, "a table in the core mapping modules to extras"); the
provider states its own extra. See Open Question 5.

### 3. The contract, version 1

Ten operations, named for what they do for the core, grouped by consumer (the
SOLID review, interface segregation). `solid` below is the engine's opaque
handle; `matrix` is the framework's composed 4x4 matrix.

**`MeshSolids`**, building solids and reading them back (the faceted caches,
fusion, statics, `assertJoined`, the `.mesh` fallback):

| operation | does | manifold3d, exactly | core sites |
|---|---|---|---|
| `solid_from_mesh(vertices, faces)` | a solid from a triangle mesh | `Manifold(mesh=Mesh(vert_properties=np.asarray(vertices, np.float32), tri_verts=np.asarray(faces, np.uint32)))` | `test.py` 354, 392, 416; `fusion.py` 131; the two former `trimesh.boolean` sites |
| `fault(solid)` | `None` when the engine admits the solid it built, else the engine's own name for the fault | `None` if `solid.status().name == 'NoError'` else `solid.status().name` | `test.py` 314 (`_admitted`); `fusion.py` 135, 145 |
| `mesh_arrays(solid)` | the solid's triangle mesh: `(vertices, faces)` | `m = solid.to_mesh()`; `(m.vert_properties[:, :3], m.tri_verts)` | `test.py` 1298 (`_placed_mesh`); `fusion.py` 151; the two former `trimesh.boolean` sites |
| `centred_box(size)` | a box of `size`, centred on the origin | `Manifold.cube(list(size), True)` | `test.py` 1433 (the virtual floor) |

**`MeshComposition`**, placing and uniting:

| operation | does | manifold3d, exactly | core sites |
|---|---|---|---|
| `placed_solid(solid, matrix)` | the solid placed by the upper three rows of `matrix`, sent as their exact values | `solid.transform(matrix[:3, :4])` | `test.py` 751, 1433, 1812, 1813 |
| `unite_solids(solids)` | the union of the solids, folded left in the order given; one solid is returned unchanged | `result = solids[0]`; `for s in solids[1:]: result = result + s` | `fusion.py` 142-144; `assertJoined` (formerly `trimesh.boolean.union`) |

**`MeshComparison`**, comparing and measuring:

| operation | does | manifold3d, exactly | core sites |
|---|---|---|---|
| `intersect_solids(first, second)` | the intersection of two solids | `first ^ second` | `test.py` 1061, 1360, 1814; the `.mesh` fallback (formerly `trimesh.boolean.intersection`) |
| `is_empty(solid)` | whether the solid holds no geometry | `solid.is_empty()` | `test.py` 1063, 1361, 1815 |
| `volume(solid)` | the solid's volume | `solid.volume()` | `test.py` 1065, 1816 |

**`MeshIdentity`**, for the verdict store and messages:

| operation | does | core sites |
|---|---|---|
| `identity()` | `(name, version)`: `('manifold3d', <the installed distribution's version from its metadata>)`, or `('manifold3d', None)` when the metadata is missing | `_verdict_store` (Decision 9); `fusion.py`'s two messages (Decision 4) |

The provider reads no file and writes none: every operation takes and returns
arrays, numbers or handles. It keeps no state. It imports numpy and manifold3d,
and from the framework only `machinome.extras`, for its import-time refusal; it
imports neither trimesh nor the seam (it raises none of the seam's errors).

`unite_solids` folds left rather than calling manifold3d's `batch_boolean`:
`fusion.py` folds left today, and trimesh's `reduce_cascade` over two meshes
is one `+`; a batch union is a different computation whose bytes are not
promised equal.

The core still holds trimesh's own work: decoding STLs, `is_volume`, splitting
components, mass properties, proximity. Those are mesh-library work, not the
mesh engine's, and stay in the core with trimesh (`cli-startup-cost`, "The
mesh library is imported by the path that reads meshes").

### 4. Admission: the engine's own word

`_admitted` keeps its message, `{what}: the mesh engine refuses this mesh
({refusal}) -- cannot build a Manifold for spatial assertions; trimesh reads it
as ...`, with `{refusal}` the engine's word (`NotManifold`), as `status.name`
is today: unchanged byte for byte. The one change of wording is the phrase
"cannot build a Manifold", which names the provider's type; it becomes "cannot
build a solid", and `tests/test_manifold_cache.py`'s two
`assertIn('NotManifold', ...)` and `tests/test_exact_geometry.py:821`'s regex
`'holey.*NotManifold'` still hold.

The faceted fusion's two messages take the engine's name from `identity()`
and its word from `fault()`: `faceted fusion {name} cannot admit child
{child}: manifold3d reported NotManifold` where today it reads `... manifold3d
reported Error.NotManifold` (`fusion.py:136` formats `str(status)`). One
format for both sites is the price of the core not parsing the engine's enum;
`tests/test_backend_neutral_materialization.py:182`'s regex `r'right:
manifold3d'` still holds. Rejected: `fault` returning `str(status)` and the
core stripping `Error.` for `_admitted` (the core parsing the provider's enum
spelling).

### 5. `test.py` over the seam

`test.py` keeps the order of every cull and comparison, both caches, the
policy, every message, and the statics' program; every operation on a solid
becomes an attribute of the provider looked up at call time, as the exact path
does (exact-engine Decision 8: a test patches an operation where it is defined,
`machinome.manifold.engine`, and every core path sees the patch).

- A helper `_mesh_engine(needed_by, reason)` beside `_exact_engine`:
  `require_mesh_engine(needed_by, _engine_reason(reason))`.
- `_cached_mesh_solid` (today `_cached_manifold`) and the flexible geometry:
  `engine.solid_from_mesh(mesh.vertices, mesh.faces)`, then `_admitted(solid,
  mesh, what, engine)` reading `engine.fault(solid)`.
- `_DeferredMeshSolid.placed` and `_faceted_verdict`: `engine.placed_solid(solid,
  matrix)`; the faceted branch of `_placed_intersection`, `_faceted_verdict` and
  `_interface_contacts`: `engine.intersect_solids`, `engine.is_empty`,
  `engine.volume`, reading `volume` only when non-empty, as today.
- `_placed_mesh`: `vertices, faces = engine.mesh_arrays(solid)` and the same
  `trimesh.Trimesh(vertices=np.asarray(vertices, float), faces=np.asarray(faces,
  np.int64), process=False)`.
- `_virtual_floor`: `engine.placed_solid(engine.centred_box(size), matrix)`.
- The up-front statics check (`test.py:2358`) is unchanged in shape.

**The caches stay in the core, holding handles**, keyed as today: the
per-observation cache (`(path, ArtifactObservation)`), the flexible LRU of 64
keyed on the leaf's snapshot. They key on files, observations and snapshots,
never on the solid, so nothing of them is the engine's (exact-engine Decision
9's principle: a memo over opaque handles stays in the core).

**Private names follow the handle.** Renamed, since after this change they
hold the engine's solid and not a manifold3d `Manifold`: `_manifold_cache` →
`_mesh_solid_cache`, `_flexible_manifold_cache` → `_flexible_mesh_solid_cache`,
`_FLEXIBLE_MANIFOLD_CACHE_LIMIT` → `_FLEXIBLE_MESH_SOLID_CACHE_LIMIT`,
`_cached_manifold` → `_cached_mesh_solid`, `_flexible_manifold` →
`_flexible_mesh_solid`, `_DeferredManifold` → `_DeferredMeshSolid`,
`_placed_manifold` → `_placed_mesh_solid`, `_Body.manifold` → `_Body.solid`.
`_faceted_verdict`, `_placed_intersection`, `IntersectionStats` and every
other name keep theirs. No project uses any of them (grep of `projects/`);
eleven test modules do and are repointed mechanically (task 5.1). Rejected:
keeping the names (cheaper, and the core would go on telling its reader it
builds Manifolds). Open Question 7.

### 6. `assertJoined`'s union and the `.mesh` fallback go through the engine

Both call `trimesh.boolean`, which is manifold3d (Context). Left as they are,
they would be the core's two remaining paths to the kernel outside the
provider: refused by trimesh's own error rather than by the seam when the extra
is absent, and bound to manifold3d whatever engine the seam resolves. Each
becomes the steps trimesh 4.4's `boolean_manifold` runs, through the engine, in
one private helper `_mesh_boolean(meshes, combine, needed_by, reason)`:

1. `if not all(mesh.is_volume for mesh in meshes): raise ValueError('Not all
   meshes are volumes!')`, trimesh's own precondition and words, kept so a mesh
   trimesh refused is still refused, with the same message;
2. `engine = _mesh_engine(needed_by, reason)`; one `engine.solid_from_mesh(mesh.vertices,
   mesh.faces)` per mesh, with no admission check (trimesh makes none);
3. `engine.unite_solids(solids)` for the union, `engine.intersect_solids(*solids)`
   for the intersection;
4. `vertices, faces = engine.mesh_arrays(result)` and
   `trimesh.Trimesh(vertices=vertices, faces=faces)`, with trimesh's default
   processing, as `boolean_manifold` builds its result.

`assertJoined` counts that mesh's components with `_body_count` as today, naming
itself as `needed_by`; the fallback reads `.is_empty` and `.volume` off it as
today.

Probe, 4 October 2026, in the bench's interpreter: a 2 mm box and a radius-0.8
cylinder offset 0.9 mm, through `trimesh.boolean.union` and through the four
steps above: vertices SHA-256 `025b9e0ba70ccd91…` and faces `5f78f12d1583ef70…`
both ways, one component both ways; through `trimesh.boolean.intersection` and
the steps: not empty, volume `2.315755067979222` both ways. `vert_properties`
of a solid built from positions has three columns (shape `(112, 3)` here), so
`[:, :3]` is the whole array, as trimesh passes it.

Rejected: resolving the seam ahead of `trimesh.boolean` and leaving trimesh to
compute (the refusal would be the seam's, but the core would still reach
manifold3d outside the provider, and a second engine would not be used there).

### 7. Fusion

`node/fusion.py` keeps its module-top imports kernel-free (it imports
`require_mesh_engine` from the seam, as now), its recipe identities and its
messages' structure. `_generate_faceted_stl`: `engine =
require_mesh_engine(...)` with today's words; for each child, the same trimesh
copy and transform, then `engine.solid_from_mesh(mesh.vertices, mesh.faces)` and
`engine.fault(...)`; `engine.unite_solids(solids)`; `engine.fault(result)`;
`vertices, faces = engine.mesh_arrays(result)` and the same
`trimesh.Trimesh(vertices=np.asarray(vertices, np.float64),
faces=np.asarray(faces, np.int64), process=False)` and publication. A current
fusion returns before resolving, as today.

The recipe identity `faceted-fusion-manifold-v1` is kept: it is an identity
recorded in every faceted fusion's artifact record, not an import, and the
bytes it names do not change; renaming it would make every faceted fusion
stale once for nothing (the exact recipe `exact-fusion-occt-v1` was kept by the
exact-engine cycle for the same reason). Open Question 9.

### 8. Three doors, and why the extra is no longer silent

ADR-167 gave every kernel three doors; the mesh engine's are:

1. **The provider refuses at import by its extra.** `machinome/manifold/engine.py`
   calls `require_extra('manifold', 'the mesh engine
   (machinome.manifold.engine)', 'manifold3d')` before it imports manifold3d:

   ```
   the mesh engine (machinome.manifold.engine) needs manifold3d, which is not installed; install it with 'pip install "machinome[manifold]"'
   ```

2. **The seam reads that refusal as absence** (Decision 2), so every requiring
   path raises `MeshEngineUnavailable` naming itself, its reason and the extra,
   at its point of use, as today.
3. **`machinome test` on the faceted kernel refuses at its start.** In
   `manager/test.py`'s `handle`, right after the policy is set and before the
   kernel line is printed or any node is loaded, a faceted policy calls
   `require_mesh_engine('machinome test on the faceted kernel', "every pair
   the run compares is compared on the parts' meshes")`, and the refusal goes
   through `self.fail`, which writes `Error: <message>` to stderr and exits 1:

   ```
   Error: machinome test on the faceted kernel requires the mesh engine because every pair the run compares is compared on the parts' meshes; install it with 'pip install "machinome[manifold]"'. Exact geometry does not need it: a model whose every compared part is exact is decided by the boundary-representation kernel
   ```

   The kernel may come from `--faceted` or `SOLID_TEST_KERNEL=faceted`; the
   words name the kernel, not the flag, so both read true. An exact-kernel
   run refuses at the first pair the exact kernel does not decide, as today: it
   may never meet one. A `ScenarioTest` under pytest has no start; it refuses at
   its first faceted comparison, as today.

ADR-052's objection to an extra, a "silently faceted-broken installation", no
longer holds: since ADR-052 every requiring path refuses by name, and this
change adds the faceted run's refusal at its start, so the first faceted thing
a project does without the extra says which line to install. ADR-167 already
made a bare install carry no kernel; manifold3d was the exception, kept on
2 October and released by the pilot on 4 October.

### 9. The verdict store: the engine's identity binds faceted verdicts

Today the process stamp (`_verdict_store._compute_stamp`) includes a
`('manifold3d', 'manifold3d')` row read from distribution metadata without
importing the kernel, so every verdict, exact ones included, is bound to the
installed manifold3d. Taking the identity from the engine, as the pilot's shape
asks, cannot happen in the process stamp: the stamp is computed at the store's
first use in every run, all-exact ones included, and asking the engine there
would resolve it in every run, which the goal "a project whose every compared
pair is exact never resolves the engine" forbids, as does the existing test
`test_computing_the_stamp_imports_no_kernel`.

So the identity moves from the stamp to the key of the verdicts it governs:

- `KERNELS` loses the `manifold3d` row; `trimesh`, `cadquery-ocp`, `cadquery`
  and `molejo` stay (the exact rows are the exact engine's to move, Deferred).
- `_verdict_store.persisted_key` gains an `engine` argument, a tuple of strings
  encoded after `path`. `test.py`'s `_persisted_key` passes, for a `faceted`
  key, `mesh_engine().identity()`; for an `exact` key, the empty tuple.
- When `mesh_engine()` answers `None`, or the identity's version is `None`,
  `_persisted_key` answers `None`: the comparison is computed and kept in the
  process only. With the engine absent the computation then raises the seam's
  refusal, exactly as a stamp mismatch led to today.

Consequences: an upgraded manifold3d no longer invalidates exact verdicts (it
never decided them); a faceted pair served from the store now resolves the
engine at its key, which costs importing `machinome.manifold.engine` (manifold3d
itself is already loaded by trimesh's import, Context). The store starts afresh
once, by the package digest. `FORMAT_VERSION` stays 1: the record and segment
layouts do not change, only what a key digests, and the stamp changes anyway.

### 10. Packaging

- `pyproject.toml`: `manifold3d` leaves `dependencies`; a new extra `manifold =
  ["manifold3d"]`, with a comment naming the module and the norm; `all` becomes
  `machinome[cadquery,build123d,step,molejo,occt,manifold]`; `dev` keeps
  `machinome[all]`. The requirement keeps the range it has today, none
  (`kernel-extras`: "Every kernel requirement SHALL keep the version range the
  framework required before"). Open Question 8.
- `requirements.txt` moves `manifold3d` under its "kernel extras" comment,
  which gains `manifold`; tox already installs `extras = all`.
- No other extra includes `manifold`: an exact project's extras (`cadquery`,
  `build123d`, `step`, `molejo`) need it only for a faceted comparison, which
  that project may never make.

### 11. `tests/mesh_engine_absent.py` in the finder form

Rewritten in the shape of `tests/exact_engine_absent.py`: a `sitecustomize`
module on the subprocess's `PYTHONPATH`, so every interpreter of a run
(`machinome build` spawns one, `machinome.core.processes`) has the finder from
its first import. It refuses whichever roots a caller lists, by default both
`manifold3d` and `machinome.manifold`, and can make a listed root *broken*
(found, then failing from inside). At exit each process appends one line to a
shared log: for each refused root, how many times it was asked for and the
module that asked (the first frame on the stack outside `importlib` and the
finder), and which of `machinome.manifold.engine` and `manifold3d` it imported.
`run_python`, `run_solid_test` (renamed `run_machinome` with the exact helper's
signature) and `mesh_engine_is_installed` keep serving their callers; `BLOCKER`,
the prelude `tests/test_verdict_store_cli.py` passes, goes, that test moving to
the finder.

Why the asker is logged: because of trimesh's import-time probe (Context),
"zero attempts on `manifold3d`" cannot hold in any process that imports
trimesh. What can hold, and what the tests and the OpenAstroMount leg assert,
is zero asks of `machinome.manifold`, and every ask of `manifold3d` made by
`trimesh.boolean`. Open Question 1.

The exact helper is not merged with this one: their logs watch different
modules, and a shared helper would be a refactor no finding asks for.

### 12. Byte identity, and the golden that proves it

The provider runs the very manifold3d calls the core runs today, on the same
arrays (the float32 and uint32 conversions move into `solid_from_mesh`
unchanged), in the same order (the left fold), with the same matrices. So every
verdict and every fused STL is the same by construction, and a golden recorded
on the unmodified tree checks it, the exact-engine cycle's
`tests/exact_engine_golden.py` being the model.

`tests/mesh_engine_golden.py` (not collected; `--record` on the unmodified tree,
`--check` after) writes `tests/data/mesh_engine_golden.json` with the bench
commit:

- **Verdicts.** For each meta-project fixture of `tests/meta_project/` whose
  companion test compares on the faceted path (every `test_*.py` there, run with
  `--faceted --no-verdict-store` into a temporary `SOLID_BUILD_DIR`, plus the
  exact ones under the exact kernel for the mixed pairs), the ordered list of
  every verdict the shared helper returned, `(path, is_empty, volume as
  float.hex())`, recorded by wrapping `machinome.test._memoized` (present on
  both trees), and each test's outcome and failure message.
- **Admission.** The refusal message for the holey mesh of
  `tests/test_exact_geometry.py`'s fixture and for a fusion child built from it,
  verbatim (the fusion's expected to differ only by `Error.`, Decision 4,
  which `--check` reports as expected).
- **Fusion.** The SHA-256 and length of the faceted `FusionNode` STL of a
  fixture fusing three `StlNode` children, one rotated and one overlapping
  (OpenSCAD's own STL is not reproducible run to run, wart of 3 October 2026,
  so no `Solid2Node` child).
- **Statics.** For `tests/meta_project/assembly_supported*.py` fixtures, the
  SHA-256 of the virtual floor's `mesh_arrays`, of every `_interface_contacts`
  result (points and normals as float64 bytes, in order), and the assertion's
  outcome.
- **`assertJoined` and the fallback.** Body counts for `welded.py`,
  `unwelded.py` and `cross_part_weld.py` under `--faceted`; `(is_empty, volume
  hex)` of the `.mesh` fallback for the `FakeNode` pairs of
  `tests/test_assertions.py`.

Run twice in separate processes on the unmodified tree, both runs agreeing,
before any source change.

### 13. Spec vocabulary

Deltas rewrite the requirements whose behaviour changes, and in them the word
"Manifold" becomes "the mesh engine's solid". The requirements of
`test-framework` whose behaviour does not change ("Whole-assembly solid
interference assertion", "Whole-assembly gravity support assertion") keep
"cached Manifolds": still true of the provider this change resolves, and
rewriting two requirements of about 230 lines each for a word is a delta no
behaviour asks for. Open Question 10.

### 14. Where the provider's records live

The `manifold-engine` capability governs behaviour that leaves the core with the
provider in layer 2, so it leaves with the code (package standard, section
1.3), as `occt-engine` will. The one ADR of this change is the core's (the seam,
the extra, the store), so it lives under `docs/adrs/TEST-FRAMEWORK/` beside
ADR-052; the provider has no decision of its own to record (its operations
reproduce manifold3d calls, no currency choice arises: the handle is
manifold3d's own `Manifold`, which no consumer outside the provider sees).

## SOLID review

**Single responsibility.** Today `test.py` orders comparisons and also builds,
judges, places, intersects, measures and meshes manifold3d solids; `fusion.py`
declares a fusion and also unions manifold3d solids; `mesh_engine.py` resolves
availability and imports the kernel; `_verdict_store.py` identifies a stored
question and also names a kernel. After: `machinome/manifold/engine.py` does mesh
solid geometry only; `mesh_engine.py` resolution, the contract and the refusal
only; `test.py` the order of culling, comparison and statics only, with its
memos; `fusion.py` the fusion's model facts and publication; the store, keys and
records, asking the engine who it is. *Bend:* `_mesh_boolean` replicates
trimesh's `is_volume` precondition and its message in the core, to keep
`assertJoined`'s and the fallback's refusals byte for byte (Decision 6).

**Open/closed.** A new faceted leaf type needs no core change: it writes an STL,
the core decodes it with trimesh and hands vertices and faces to the engine. A
second mesh engine needs one string, `PROVIDER`, changed, the accepted
compromise of D2 that the exact seam carries too. *Bend:* the provider's name
reaches messages through `identity()`, not a literal, so a second engine's
words would be its own.

**Liskov substitution.** Every handle the engine returns is accepted by every
operation that takes a solid: a placed solid, an intersection, a union and a
box are interchangeable to the core (the virtual floor shares the statics'
records with placed parts because of it, `_placed_mesh_solid` being the one
funnel). *Bend:* none found.

**Interface segregation.** Four Protocols by consumer: `MeshSolids` (the caches,
fusion, statics), `MeshComposition` (placement, fusion, `assertJoined`),
`MeshComparison` (the faceted verdicts, statics' contacts), `MeshIdentity` (the
store, fusion's messages). *Bend:* one provider module serves all four, because
the seam resolves one known provider; and the provider has no project-facing
operation, so unlike the exact engine nothing of it is a project's to call
(Open Question 6).

**Dependency inversion.** The core depends on `machinome.mesh_engine` (`CONTRACT`,
the Protocols, the errors, `mesh_engine`, `require_mesh_engine`) and never
imports manifold3d or calls `trimesh.boolean`; the provider depends on numpy,
manifold3d and `machinome.extras`, never on the core's caches, the store or
the seam. *Bends that remain:* the core's memos rely on Python object identity
of the handles the engine returns (unchanged mechanism, as for the exact
engine); trimesh itself still probes and loads manifold3d at its own import
when it is installed (outside the core's control, Context); and the verdict
store's process stamp keeps the exact path's kernel rows (Deferred).

## ADRs

Written after implementation, from what the pilot ratified; the next free
number at writing (ADR-176 at 69c7019, the highest being ADR-175):

- **ADR-176, the mesh engine is a provider behind the seam, installed by an
  extra.** Under `docs/adrs/TEST-FRAMEWORK/`. The provider
  `machinome.manifold.engine` and its package; the seam's contract (version 1,
  ten operations, four Protocols), its absence rule and its two errors; the
  core's solids as opaque handles and its caches over them; `assertJoined` and
  the `.mesh` fallback leaving `trimesh.boolean`; the `manifold` extra and the
  three doors with `--faceted` refusing at its start; the engine's identity in
  the faceted verdict key. **Amends ADR-052** (its "packaging is unchanged"
  and its rejected option "move manifold3d to an optional extra", answered by
  Decision 8; its consequence that `trimesh.boolean`'s engine selection stays
  outside the contract, now only the proximity queries), **ADR-161** (the core
  holds no kernel code now covers the mesh engine; the mesh seam takes the
  exact seam's shape, absence rule included), **ADR-156** (the stamp no longer
  carries the mesh engine; a faceted key carries the engine's identity) and
  **ADR-167** (manifold3d is no longer the required exception). Each amended ADR
  gains a status line and an amendment section. Cites ADR-029, ADR-074 (the
  engine judges its own input, unchanged), ADR-049 (statics), ADR-162.

Not architectural: the operation names, the private renames, the golden's
fixtures, the finder's log format.

## Risks / Trade-offs

- [A project testing a faceted part, or importing `manifold3d` or
  `trimesh.boolean` itself, breaks on a plain install] → every core path refuses
  naming `machinome[manifold]`; the seven importing projects and the sixteen
  `trimesh.boolean` callers are listed (Context) for the migration note;
  Prusa3-vanilla's `shared_volume` returns `0.0` silently without manifold3d
  (its own `except Exception`), a project defect this change exposes and does
  not fix (Migration).
- [A translated call differs from the inline one (dtype, slice, fold order)] →
  the golden of Decision 12, recorded before any source change; the existing
  cache, culling, statics and fusion suites.
- [Tests patch `require_mesh_engine` returning a pair, `mesh_engine()[0]`,
  `Manifold` methods, or the renamed privates] → repointed in task 5.1: a patch
  of an operation targets `machinome.manifold.engine`; a counting test counts
  `solid_from_mesh`; no asserted verdict, count or message changes except the
  two of Decision 4.
- [The faceted verdict's key now resolves the engine on a store hit] → about the
  cost of importing one module; manifold3d is already loaded by trimesh.
- [One attribute lookup and one Python call per operation on the faceted hot
  path, and an `lru_cache` hit per resolution] → *inferred* negligible against
  the Boolean each one wraps; the Prusa3-vanilla leg records the suite's wall
  time before and after, and a slowdown beyond run-to-run noise returns to the
  orchestrator.
- [`mesh_engine()` no longer swallows a broken manifold3d] → intended, the
  broken-installation rule; a test pins it.

## Migration Plan

For projects: install the extra. A project's own requirements, where it keeps
any, name `machinome[manifold]` (or `machinome[all]`) when it has a part without
exact geometry that a test compares, uses `assertAssemblySupported`, fuses a
faceted part, runs `--faceted`, or imports `manifold3d` or calls
`trimesh.boolean` itself. No source line changes: no import moves, and no
project names the seam or the core's privates. The workspace venv installs
`machinome[all]`, so no project in it notices; the studio's `machinome-api`
skill and the workspace's setup and collaborator pages learn the extra with the
other follow-ups the plan lists (outside the framework).

For the framework: a planning commit, then the implementation and its
records as further commits on `v0.8-split-mesh-engine`, nothing amended (the
pilot, 4 October 2026), fast-forwarded into `v0.8-split` by the orchestrator.
Rollback is reverting the implementation commits. No artifact is rebuilt; the
verdict store refills once.

## Deferred, recorded here so it is not lost

- The exact path's stamp rows (`cadquery-ocp`, `cadquery`) moving into exact
  keys from the exact engine's own identity, by the same reasoning as Decision
  9; the exact engine's contract has no `identity()` today.
- The distribution `machinome-manifold` and the extra's repointing at it
  (layer 2), with the `manifold-engine` spec moving into its repository.
- `test-framework`'s remaining "cached Manifolds" wording (Decision 13).
- The workspace and studio follow-ups: `scripts/setup`, `docs/collaborator-setup.md`,
  the `machinome-api` skill teaching the `manifold` extra.
- Prusa3-vanilla's `shared_volume` swallowing every exception, a finding for
  that project (the orchestrator files it if the pilot wants it filed).

## Open Questions

Settled at ratification (the orchestrator, 4 October 2026, under the pilot's
standing authority): every recommendation below is taken. In particular, the
engine's identity binds the faceted keys and not the process stamp (2); the
two `trimesh.boolean` paths go through the engine (3); the faceted fusion's
bytes are proven by the golden and `cam_hammer` shows an exact fusion never
asks (4); `machinome/extras.py` is not changed (5); no project-facing mesh
operation (6); the privates are renamed (7); the extra stays unpinned (8); the
recipe identity is kept (9); the two unchanged requirements keep their wording
(10). The admission operation is named `fault`, not `refusal`, so the word
"refusal" keeps meaning the extras' install refusal throughout the records.

### As proposed before ratification (record)

1. **The OpenAstroMount leg cannot show zero asks of `manifold3d`.** trimesh
   asks for it at its own import (Context: `trimesh/boolean.py`'s top-level
   `try: from manifold3d import ...`; `-X importtime`), and `machinome.test`
   imports trimesh. *Recommendation:* the leg and the tests assert zero asks of
   `machinome.manifold` and that every ask of `manifold3d` comes from
   `trimesh.boolean`, which copes with its absence; the finder logs the asker
   (Decision 11).
2. **The engine's identity binds faceted keys, not the process stamp.** The
   brief's shape says the store "stamps" the identity "in place of its
   hard-coded manifold3d row"; done in the stamp, every run would resolve the
   engine. *Recommendation:* Decision 9 as written.
3. **`assertJoined`'s union and the `.mesh` fallback leave `trimesh.boolean`.**
   The brief's site list did not name them; they reach manifold3d through
   trimesh. *Recommendation:* route them (Decision 6); the alternative leaves
   two kernel reaches outside the provider.
4. **No candidate project fuses faceted children.** `Leonardo/models/rack_and_pinion`
   and `cam_hammer` fuse `CadQueryNode` children and the Curta's
   `standard/printed.py` fuses `StepNode` children: all exact fusions
   (`exact-fusion-occt-v1`), which never reach the mesh engine. No project in
   the catalogue declares a faceted fusion (grep of `projects/` for
   `FusionNode`, 4 October 2026: 14 files, all over CadQuery or STEP leaves).
   *Recommendation:* the faceted fusion's bytes are proven by the golden's
   three-`StlNode` fixture (Decision 12); the project leg runs on
   `Leonardo/models/cam_hammer`, the smallest (a 184-line model with two
   fusions), to show that an exact fusion builds with the mesh engine absent and
   never asks for it, with its STL and BREP bytes equal to an unblocked build.
5. **`machinome/extras.py` "gains the row".** It holds no table by design
   (ADR-167, option 2 rejected). *Recommendation:* no change there; the provider
   calls `require_extra('manifold', ...)` and the test tables
   (`test_kernel_extras.py`'s `EXTRAS` and `MODULES`, `test_core_kernel_free.py`'s
   `KERNELS` and `EXTRA_OF`) gain the rows.
6. **Should a project be able to call the mesh engine's operations, as it calls
   the exact engine's?** None does today (it imports manifold3d directly).
   *Recommendation:* no; the provider is the core's, and nothing in vet changes.
7. **Renaming the private caches and helpers.** *Recommendation:* rename
   (Decision 5); the cost is mechanical test churn.
8. **The `manifold` extra's version range.** *Recommendation:* keep it unpinned
   as the required dependency is today; pinning manifold3d is its own decision.
9. **The recipe identity `faceted-fusion-manifold-v1`.** *Recommendation:* keep
   (Decision 7).
10. **"cached Manifolds" in two unchanged `test-framework` requirements.**
    *Recommendation:* leave (Decision 13).
