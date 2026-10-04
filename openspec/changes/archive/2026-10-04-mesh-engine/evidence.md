# Evidence — `mesh-engine`

The seventh cycle of layer 1 of the lean-core campaign
(`workflow/ongoing/lean-core.md`, "Settled by the pilot, 4 October 2026,
later the same day"). Worktree `machinome/WTs/v0.8-split-mesh-engine`, branch
`v0.8-split-mesh-engine`, cut from `v0.8-split` at 69c7019. Planning commit
872d8a3. Every command below ran from inside the worktree with
`PYTHONPATH=<worktree>` and the workspace venv (Python 3.12.3, trimesh
4.4.9, manifold3d 3.5.2); `machinome.__file__` resolved to
`<worktree>/machinome/__init__.py`. Pytest ran one process at a time, never
in parallel, each after the orchestrator's process guard printed nothing.

## 1. Baseline on the unmodified tree (872d8a3)

### 1.1 The Context facts the design rests on

**Decision 6's probe.** A 2 mm `trimesh.creation.box` and a radius-0.8,
height-2 `trimesh.creation.cylinder` translated 0.9 mm along X, through
`trimesh.boolean` and through the four steps of `_mesh_boolean` written
out with manifold3d (`is_volume` check; `Manifold(mesh=Mesh(float32,
uint32))` per mesh; `+` folded left or `^`; `Trimesh(vertices=
vert_properties[:, :3], faces=tri_verts)`), scratch script
`probe_1_1.py`:

```
union trimesh.boolean  vertices 82e71e19a8d8ce86 faces 0aa67edf76a8509d components 1
union four steps       vertices 82e71e19a8d8ce86 faces 0aa67edf76a8509d components 1 vert_properties shape (44, 3)
union equal True
intersection trimesh.boolean is_empty False volume np.float64(2.3157550679792225)
intersection four steps      is_empty False volume np.float64(2.3157550679792225)
```

The digests differ from design.md's quoted prefixes (`025b9e0b…`,
`5f78f12d…`, a 112-vertex result) because design.md does not record the
cylinder's height and sections; what the design rests on holds: both ways
give equal vertex and face bytes, one component, and equal intersection
volume (the design's `2.315755067979222`, here printed with its last
digit, `2.3157550679792225`). The result's `vert_properties` has three
columns.

**The flush-contact probe** of the `manifold-engine` spec: two 2 mm boxes
built from trimesh meshes, the second placed by `transform` 2 mm along X,
intersected with `^`:

```
flush contact is_empty False volume 0.0
```

**trimesh asks for manifold3d at its own import**
(`python -X importtime -c "import trimesh"`):

```
import time:      3584 |       3584 |     manifold3d
import time:       847 |     125201 |   trimesh.boolean
```

**Project counts** (re-checked 4 October 2026, `git grep` of each project
repository's tracked `*.py`, worktrees excluded). Importing `manifold3d`
(`import manifold3d` / `from manifold3d`): Curta-Type-I-3x 40,
Voron-2 3, Pascaline-module 2, hangprinter 1, snappy-reprap 1,
hexapod_spiderbot_model 1, openvmp 1 — the seven projects of the proposal;
the Curta's count is 40 tracked files where the proposal's grep counted 80
(an untracked-tree count, `_build*` directories included). Calling
`trimesh.boolean`: sixteen projects (Metamaquina2, Prusa3-vanilla,
OpenCycloid, Curta-Type-I-3x, Pascaline-module 4, science-jubilee,
Leonardo 2, Pin_tumbler_lock 2, Vault_with_combination_lock 5, SO-ARM100,
openarm, orcahand_hardware, YouCanBuildDog, dragon-r1,
lumiere-cinematographe, sandbox/gearbox), as the proposal says. No project
file names `machinome.mesh_engine`, `require_mesh_engine`,
`_manifold_cache` or `_cached_manifold` (0 files).

### 1.2 The mesh engine golden

`tests/mesh_engine_golden.py` (new, not collected) and its fixture module
`tests/mesh_engine_fixture.py` (new: a temporary project of `StlNode`
parts over meshes trimesh writes, `Shelf`, `Fused` and `HoleyFused`; the
repository carries no mesh). It records, into one temporary
`SOLID_BUILD_DIR` per invocation:

- every companion test of `tests/meta_project/` (46 fixtures) run as
  `machinome test --faceted --no-verdict-store` and as
  `machinome test --exact --no-verdict-store`, under a probe wrapping
  `machinome.test._memoized`, `_virtual_floor`, `_interface_contacts` and
  `_body_count`: each run's exit status, summary, per-test outcome and the
  first line of every exception printed; every verdict the shared helper
  returned, in order, as `(path, is_empty, volume.hex())` (faceted run:
  77 faceted and 17 unkeyed; exact run: 70 faceted, 7 exact and 17 unkeyed);
  the SHA-256 of each virtual floor's vertices and faces (15 per run) and of
  each contact list (61 per run); and each body count (6 per run, the
  `assertJoined` fixtures `welded`, `unwelded` and `cross_part_weld`);
- the refusal of a 2 mm box missing one triangle as a compared part, and
  of a 4 mm one as `HoleyFused`'s child;
- the SHA-256 and length of `Fused`'s faceted STL (`90b7df64a726ab59…`,
  3284 bytes);
- the `.mesh` fallback's `(is_empty, volume.hex())` for five pairs of
  `tests/test_assertions.py`'s `FakeNode` (overlapping, flush, far, turned,
  nested).

Run `--record` twice in separate processes into the scratchpad (137 s
each): the two JSON files were byte-identical (`cmp`), 1095 values; the
first was copied to `tests/data/mesh_engine_golden.json` (bench commit
872d8a3). The two refusals as recorded:

```
<scratch>/holey.stl: the mesh engine refuses this mesh (NotManifold) -- cannot build a Manifold for spatial assertions; trimesh reads it as not watertight. Repair or replace the mesh; nothing is repaired here
faceted fusion HoleyFused cannot admit child holey: manifold3d reported Error.NotManifold
```

`--check` on the unmodified tree:

```
golden comparison: 1095 values, 0 differences, 0 expected (design.md Decision 4)
```

### 1.3 The files this change touches, unmodified tree

One pytest process: `test_mesh_engine_dependency.py`,
`test_manifold_cache.py`, `test_verdict_store.py`,
`test_verdict_store_cli.py`, `test_kernel_extras.py`,
`test_core_kernel_free.py`, `test_broad_phase_culling.py`,
`test_assembly_integrity.py`, `test_assembly_supported.py`,
`test_cli_lazy_imports.py`, `test_node_lazy_exports.py`,
`test_vet_universe.py`, `test_flexible_cache_performance.py`,
`test_flexible_verdict_identity.py`, `test_persistent_piece_facts.py`,
`test_intersection_memo.py`, `test_exact_geometry.py`,
`test_backend_neutral_materialization.py`, `test_face_box_culling.py`,
`test_assertions.py`, `test_molejo_adapter.py`, `test_stl_node.py`,
`test_meta.py`:

```
619 passed, 3 warnings, 247 subtests passed in 215.46s (0:03:35)   (wall 216.9 s)
```

## 2. Red tests, on the unmodified source (872d8a3)

New files: `tests/test_mesh_engine_seam.py` (2.1), `tests/test_manifold_engine.py`
(2.2). Rewritten: `tests/mesh_engine_absent.py` in the finder form (2.4,
design.md Decision 11), `tests/test_mesh_engine_dependency.py` over it (2.4).
Extended: `tests/test_core_kernel_free.py` and `tests/test_kernel_extras.py`
(2.3), `tests/test_verdict_store.py` (2.5, class
`MeshEngineIdentityBindsFacetedVerdicts`), `tests/test_verdict_store_cli.py`
(`WithoutTheMeshEngine` moved to the finder), `tests/test_manifold_cache.py`
(2.6, class `BooleansGoThroughTheMeshEngineTest`).

**What the first red runs taught the finder.** The first run of the new
finder raised `ModuleNotFoundError` from its `find_spec`, as
`tests/exact_engine_absent.py`'s does, and every process importing trimesh
died at its import: `trimesh/creation.py` probes `manifold3d` through
`trimesh.util.has_module`, that is `importlib.util.find_spec`, which does
not catch a finder's error (the old helper imported trimesh before
installing its blocker for this reason). The finder now logs the ask and
finds nothing, and every other finder of `sys.meta_path` is wrapped blind to
the listed roots (`_Hiding`, metadata lookups delegated), so the import
system answers as where they are not installed: `find_spec` returns None
and an import raises `ModuleNotFoundError`. trimesh asks for `manifold3d`
from two of its modules at import, `trimesh.boolean` and `trimesh.util`
(recorded as `TRIMESH_PROBES`), so the tests assert every ask of
`manifold3d` comes from those two, not from `trimesh.boolean` alone as
design.md Decision 11 says. The second run hung: `machinome build` in the
fixture project written moments earlier printed `START` once a second,
each generation ending `SOURCE_CHANGED` (11), killed after ten minutes
(the wart of 3 October 2026, "a `machinome build` hanging three hours in a
fresh project worktree", reproduced outside any finder:
`timeout 60 machinome build mfixture/parts.py:Shelf` exited 124 with 50
`START` lines; with the sources dated an hour back, one `START` and exit
0). `tests/mesh_engine_fixture.py` now dates every source it writes in the
past. The red run's expectation of the STL names (`parts-Block-…`) was the
fixture's error; the build names them `block-__Block_,_mfixture_parts.py__-…`,
and the test was corrected after the run below.

One pytest process (`test_mesh_engine_seam.py test_manifold_engine.py
test_core_kernel_free.py test_kernel_extras.py test_mesh_engine_dependency.py
test_verdict_store_cli.py test_verdict_store.py test_manifold_cache.py`):

```
45 failed, 81 passed, 10 errors, 56 subtests passed in 80.12s (0:01:20)   (wall 81.3 s)
```

and eight failing subtests. Every red test and its reason, verbatim where
quoted:

| test | reason |
|---|---|
| 2.1 `ProviderTest` (6) | `(<class 'manifold3d.Manifold'>, <class 'manifold3d.Mesh'>) is not an instance of <class 'module'>`; `module 'machinome.mesh_engine' has no attribute 'MeshEngine'`; `... has no attribute 'importlib'`; `No module named 'machinome.manifold'`; `'manifold' not found in {'dev': ...}` |
| 2.1 `AbsentEngineTest` (2) | `(<class 'manifold3d.Manifold'>, <class 'manifold3d.Mesh'>) is not None` (a `None` provider entry is not read); `MeshEngineUnavailable not raised` |
| 2.1 `ContractMismatchTest` (3) | `module 'machinome.mesh_engine' has no attribute 'MeshEngineIncompatible'` |
| 2.1 `BrokenEngineTest` | `No module named 'machinome.manifold'` |
| 2.1 `AbsentKernelTest` (3) | an absent `manifold3d`: the refusal names `pip install manifold3d` and "the manifold3d mesh engine" (`"MeshEngineUnavailable: faceted fusion Br[235 chars]rnel" != '...[237 chars]rnel'`); an absent `machinome.manifold`: `"(<class 'manifold3d.Manifold'>, <class 'manifold3d.Mesh'>)" != 'None'`; a broken `manifold3d`: `'None' != 'ImportError: broken manifold3d'` (every `ImportError` reads as absent) |
| 2.2 `EngineOperationsTest` (10 errors at setup) | `probe failed: ... ModuleNotFoundError: No module named 'machinome.manifold'` |
| 2.2 `ContractDeclarationTest` | `FileNotFoundError: ... machinome/manifold/engine.py` |
| 2.3 `test_kernels_are_imported_only_by_their_modules` | `{'machinome/mesh_engine.py': ['manifold3d'], ...} != {...}` |
| 2.3 `test_each_kernel_module_checks_its_kernel_first` (subtest `machinome/manifold/engine.py`) | `KeyError: 'machinome/manifold/engine.py'` |
| 2.3 `test_no_module_reaches_trimesh_boolean` | `{'machinome/test.py': [1884, 2495]} != {}` |
| 2.3 `test_the_seam_is_the_only_core_module_naming_the_provider` | `Lists differ: [] != ['machinome/mesh_engine.py']` |
| 2.3 `test_a_bare_install_carries_no_kernel`, `test_all_names_every_kernel_extra`, `test_each_extra_lists_what_its_module_needs` (subtests `manifold`, `all`) | `manifold3d` is required; no `manifold` extra; `all` lacks it |
| 2.3 `KernelRefusalTest` (subtests `machinome.manifold.engine`) | the module does not exist |
| 2.4 `MissingMeshEngineIsActionableTest` (4) | `'requires the mesh engine' not found in` the run's output, which reads "requires the manifold3d mesh engine ... 'pip install manifold3d'"; the broken-kernel case likewise reads as absent |
| 2.4 `FacetedRunRefusesAtItsStartTest` (2) | Decision 8's refusal not in stderr: the run built and ran, `Running FlushContactTest.test_flush_faces_pass_with_volume_epsilon.FAIL!` |
| 2.4 `test_a_stale_faceted_fusion_names_the_install` | `'requires the mesh engine' not found in` the build's output |
| 2.4 `test_a_project_of_imported_meshes_builds_without_it` | the test's own name pattern, corrected (above): `('Block', ['bar-__Bar_,_mfixture_parts.py__-9cd2d230b758.stl', 'block-__Block_,_mfixture_parts.py__-9b94f05a05b1.stl'])` |
| 2.5 `test_the_stamp_names_no_mesh_engine` | `'manifold3d' unexpectedly found in ['cadquery-ocp', 'cadquery', 'manifold3d', 'trimesh', 'molejo']` |
| 2.5 the upgrade and no-version cases (2) | `module 'machinome' has no attribute 'manifold'` |
| 2.5 `test_without_a_mesh_engine_a_faceted_key_is_not_persisted` | `<module 'machinome.test' ...> does not have the attribute 'mesh_engine'` |
| 2.6 `BooleansGoThroughTheMeshEngineTest` (4, and 3 subtests of the fallback) | `trimesh.boolean was called: the core reached the mesh engine's kernel outside the mesh engine`; `No module named 'machinome.manifold'` |

Green on the unmodified source, as guards: the import cases of
`AssertionModuleImportTest`, the all-exact runs of
`ExactPathWithoutMeshEngineTest` and `WithoutTheMeshEngine` (zero asks of
`machinome.manifold`, every ask of `manifold3d` one of trimesh's two
probes).

## 3-4. The provider, the seam, the extra; the core over the seam

`machinome/manifold/__init__.py` (no names) and `machinome/manifold/engine.py`
(the ten operations of design.md Decision 3, `require_extra('manifold', ...)`
before `manifold3d` is imported, `CONTRACT = 1`); `machinome/mesh_engine.py`
(`CONTRACT`, `PROVIDER`, `MeshSolid`, the four Protocols and `MeshEngine`,
`MeshEngineUnavailable`, `MeshEngineIncompatible`, `_absent`,
`mesh_engine()`, `require_mesh_engine()`); `pyproject.toml` and
`requirements.txt` (`manifold3d` moved to the `manifold` extra, in `all`);
`machinome/test.py`, `machinome/node/fusion.py`, `machinome/_verdict_store.py`,
`machinome/manager/test.py`, `machinome/node/flexible.py`'s two comments.

Two choices of implementation inside the ratified design:

- The statics paths (`_virtual_floor`, `_interface_contacts`,
  `_placed_mesh`) resolve the engine with
  `require_mesh_engine(_STATICS_NEEDED_BY, _STATICS_REASON)` directly
  (`_statics_engine`), not through `_mesh_engine`, whose reason becomes
  "the run compares on the faceted kernel" under that kernel: the floor
  required the engine that way before the change, so its refusal reads as
  it did. The deferred placement and the rigid and flexible solid caches
  keep `_engine_reason`, as `_cached_manifold` and the flexible geometry did.
- The faceted fusion reads the engine's name (`identity()[0]`) only when it
  refuses, so a fusion that unions imports no `importlib.metadata`.

### 4.6 The red tests, green

One pytest process, the eight files of 2.7:

```
1 failed, 127 passed, 84 subtests passed in 79.30s (0:01:19)   (wall 80.4 s)
```

The one failure was the test's own flush geometry:
`test_a_flush_contact_stays_non_empty_at_zero_volume`,
`Lists differ: [True, 0.0] != [False, 0.0]`. Two 2 mm boxes of the test's
own triangulation (`[0, 2]³`, the second translated 2 mm along X) come back
from manifold3d **empty**; the same contact between boxes laid out as
`trimesh.creation.box` lays one out comes back non-empty at exactly 0.0, as
the probe of 1.1 shows. Whether manifold3d reports an exact face contact
empty depends on how the shared face is triangulated; the engine reports
what manifold3d reports either way, and the faceted path's verdicts, the
flush meta fixtures among them, are pinned by the golden. The scenario was
rewritten on the probe's layout, written out in numpy (`BOX`,
`BOX_TRIANGLES`): `tests/test_manifold_engine.py`, `11 passed in 0.30s`.
The spec scenario "A flush contact stays non-empty" holds for that
geometry and is not a claim about every flush contact; the archived spec
keeps its wording, the finding recorded here.

## 5. Existing tests repointed

### 5.1 Repointed, and every changed assertion target

Renamed privates, mechanically (no assertion changed):
`_manifold_cache` → `_mesh_solid_cache`, `_cached_manifold` →
`_cached_mesh_solid`, `_flexible_manifold` / `_flexible_manifold_cache` /
`_FLEXIBLE_MANIFOLD_CACHE_LIMIT` → `_flexible_mesh_solid` /
`_flexible_mesh_solid_cache` / `_FLEXIBLE_MESH_SOLID_CACHE_LIMIT`,
`_placed_manifold` → `_placed_mesh_solid`, in
`test_flexible_cache_performance.py`, `test_manifold_cache.py`,
`test_verdict_store.py`, `test_persistent_piece_facts.py`,
`test_assembly_integrity.py`, `test_assembly_supported.py`. The four other
files the task names (`test_flexible_verdict_identity.py`,
`test_face_box_culling.py`, `test_molejo_adapter.py`,
`test_intersection_memo.py`) use none of the renamed names; only
`test_intersection_memo.py`'s docstring naming `Manifold.__xor__` was
updated. Tests that call a manifold3d method on a handle the core returned
(`.volume()` in `test_flexible_cache_performance.py` and
`test_persistent_piece_facts.py`) keep doing so: the handle is manifold3d's
own `Manifold`.

Changed assertion targets, each with its reason:

| file, test | before | after | why |
|---|---|---|---|
| `test_manifold_cache.py`, `test_repeated_assertions_build_the_manifold_once` | patched `machinome.test.require_mesh_engine` to return `(counting Manifold, Mesh)`, counted calls == 1 | wraps `machinome.manifold.engine.solid_from_mesh`, `call_count` == 1 | the seam returns the provider, not a pair; the provider's one construction operation is what counts builds |
| `test_assembly_integrity.py`, `test_no_whole_assembly_union_is_computed` | patched `mesh_engine()[0].batch_boolean` (and `machinome.test.trimesh.boolean.union`) to raise | patches `machinome.manifold.engine.unite_solids` (and the same trimesh patch) to raise | the engine's union is its `unite_solids`; `Manifold.batch_boolean` is reached by no path |
| `test_broad_phase_culling.py`, `Placement` and the fixture placements | `Manifold.cube(size, True)`, `.transform(matrix[:3, :4])`, `^`, `.is_empty()` | `engine.centred_box(size)`, `engine.placed_solid`, `engine.intersect_solids`, `engine.is_empty`; bounds still read with the solid's own `bounding_box()` (`solid_bounds`) | the test builds and places through the provider; reading bounds off `mesh_arrays` instead (first attempt) failed `test_bound_in_a_rotated_frame_encloses_the_placed_geometry` by `1.75244081e-07`, manifold3d's `to_mesh` vertices being float32 against a 1e-9 slack, so the bounds stay read from the source they were read from before (the orchestrator's direction), and no tolerance changed |
| `test_verdict_store.py`, `test_the_quantum_is_part_of_the_persisted_key` | `store.persisted_key(path, quantum, id, id, cells)` | the same with `ENGINE = ('manifold3d', '3.5.2')` as `engine` | `persisted_key` takes the engine's identity (design.md Decision 9); the assertion (the two keys differ) is unchanged |
| `test_cli_lazy_imports.py`, `VerdictStoreImportWeight.WATCHED` | 7 modules | adds `machinome.manifold.engine` | importing the store module or dispatching `build -h` must not import the provider either |
| `test_docs_structure.py`, `KernelExtrasTest.EXTRAS` | 6 extras | adds `manifold` | the installation page names every kernel extra (task 6.2) |
| `test_node_lazy_exports.py` | comment | points at the finder form of both helpers | comment only |

Unchanged as the task says: `test_exact_geometry.py`'s `no_engine` patch
(`machinome.test.require_mesh_engine`, still the module global every
resolution goes through); `test_backend_neutral_materialization.py`'s
`machinome.node.fusion.require_mesh_engine` patch and its regex
`r'right: manifold3d'` (the message now reads `... right: manifold3d
reported NotManifold`).

One pytest process, the 23 files of 1.3 with the two new test files and
`test_docs_structure.py`:

```
1 failed, 670 passed, 3 warnings, 487 subtests passed in 214.05s (0:03:34)   (wall 215.5 s)
```

the one failure the float32 bounds above; with `solid_bounds` reading the
solid's own box, `tests/test_broad_phase_culling.py` alone:
`35 passed, 1 warning, 24 subtests passed in 1.24s`.

### 5.2 The golden, after the change

```
EXPECTED: admission_compared golden='<scratch>/holey.stl: the mesh engine refuses this mesh (NotManifold) -- cannot build a Manifold for spatial assertions; trimesh reads it as not watertight. Repair or replace the mesh; nothing is repaired here' now='<scratch>/holey.stl: the mesh engine refuses this mesh (NotManifold) -- cannot build a solid for spatial assertions; trimesh reads it as not watertight. Repair or replace the mesh; nothing is repaired here'
EXPECTED: admission_fusion_child golden='faceted fusion HoleyFused cannot admit child holey: manifold3d reported Error.NotManifold' now='faceted fusion HoleyFused cannot admit child holey: manifold3d reported NotManifold'
golden comparison: 1095 values, 0 differences, 2 expected (design.md Decision 4)
```

(132 s.) Every verdict of the 46 meta fixtures on both kernels, every
floor and contact digest, every body count, every outcome and exception
line, the fused STL's SHA-256 and length and the five `.mesh` fallback
verdicts are bit-identical to the unmodified tree's.

### 5.3 The whole framework suite, alone

```
4482 passed, 4 skipped, 55 warnings, 3705 subtests passed in 704.57s (0:11:44)   (wall 707.2 s)
```

against the line's last full run at 69c7019, 4439 passed and 4 skipped: 43
tests more, the new ones of this change, and none fewer. A grep of
`machinome/` outside `machinome/manifold/` for `.to_mesh(`, `.status()`,
`Manifold` and `manifold3d` finds one line, the seam docstring's sentence
on WebAssembly.

## 6. Docs

`docs/architecture.md` (the conditional-engine sentence, the faceted fusion
sentences, the test-framework and shared-intersection paragraphs, the
verdict store's stamp and the faceted key, the flexible LRU, the map's new
"Manifold mesh engine" row and the test framework row), `docs/start/install.rst`
(the package brings trimesh and SolidPython; the `machinome[manifold]` row;
what needs it and how it refuses; `machinome[manifold]` for an all-OpenSCAD,
JSCAD or STL project), `docs/howto/fast-tests.rst` (the faceted kernel needs
the extra and refuses at its start without it), `README.rst` (the
`manifold3d` paragraph), and the changelog's Unreleased section (task 6.3's
bullet, verbatim). Not `HISTORY.rst`.

A strict HTML build of the whole manual into the scratchpad,
`python -m sphinx -b html -q -W --keep-going docs <scratch>`: exit 0, no
warning (5 s). The three touched manual pages name `machinome[manifold]`
(install 5 times, fast-tests and the changelog once each).

## 7. The campaign plan

`workflow/ongoing/lean-core.md`: the dependency table's `manifold3d` row,
"Where the core reaches each kernel"'s mesh-engine bullet, the "Import
paths" row `the mesh engine | machinome.manifold.engine |
machinome[manifold] | machinome-manifold`, "State of the campaign"'s
extras list and its "Struck or deferred" sentence (manifold3d left the
required list on 4 October 2026 by this cycle; watchdog stays), "What
packaging does not solve", and the "Empirical validation" table's row for
this cycle, its result to be written from the orchestrator's legs (10.1).

## 8. The applier's checkpoint (8.1)

Reported to the orchestrator with 1 to 7 done: 31 tracked files changed,
1426 insertions, 546 deletions, eight new files; the results of sections 1
to 7 above. Nothing committed.

## 9. Empirical validation (run by the orchestrator)

Every leg ran one at a time, `PYTHONPATH` the bench (*after*) or the line's
bench `machinome/WTs/v0.8-split` at 69c7019 (*before*), into scratch build
directories, with the verdict recorder of tasks.md group 9
(`ptl7-recorder.py`). The blocked runs used a `sitecustomize` written from
this change's `tests/mesh_engine_absent.py` with
`MESH_ENGINE_ABSENT_NAMES=manifold3d,machinome.manifold`, and a script
(`ptl7-asks.py`) summarised every process's exit report. Logs:
`ptl7-before.log` (2026-10-04 09:31:55 to 10:15:39) and `ptl7-after.log`
(on 872d8a3 with the uncommitted implementation, 38 paths, 11:10:46 to
11:54:40), in the orchestrator's scratchpad.

### 9.1 Locks/Pin_tumbler_lock

Before and after, the recorder running `test --faceted --no-verdict-store`:

```
before: Ran 24 tests in 37.46 seconds: 24 passed, 0 failed (faceted kernel, volume epsilon 0 mm³, verdict store off)
        exit 0 in 38 s; lock verdicts logged: 2573
after:  Ran 24 tests in 37.80 seconds: 24 passed, 0 failed (faceted kernel, volume epsilon 0 mm³, verdict store off)
        exit 0 in 39 s; verdict logs before/after: 2573/2573 lines; identical: YES
```

After, with the finder refusing `manifold3d` and `machinome.manifold`:

```
--- Pin_tumbler_lock BLOCKED (lock-test): machinome test --faceted ---
exit 1 in 2 s
Error: machinome test on the faceted kernel requires the mesh engine because every pair the run compares is compared on the parts' meshes; install it with 'pip install "machinome[manifold]"'. Exact geometry does not need it: a model whose every compared part is exact is decided by the boundary-repre
asks: processes 1; asks: manifold3d: 2 by {'trimesh.boolean': 1, 'trimesh.util': 1}; machinome.manifold: 1 by {'machinome.mesh_engine': 1}; imported: nothing
STL written by the refused faceted run: 0
--- Pin_tumbler_lock BLOCKED (lock-build): machinome build ---
exit 0 in 11 s
asks: processes 3; asks: manifold3d: 4 by {'trimesh.boolean': 2, 'trimesh.util': 2}; imported: nothing
blocked build wrote: 11 stl, viewer.json yes
```

(the refusal line is the log's, cut at its width). The refused run's one
ask of `machinome.manifold` is the seam resolving the engine at the run's
start, the refusal itself; the build never asks.

### 9.2 3D-Printers/Prusa3-vanilla

Before and after, the recorder running `test --no-verdict-store` on the
default kernel:

```
before: Ran 19 tests in 1974.46 seconds: 16 passed, 3 failed (verdict store off)
        exit 1 in 1979 s; prusa verdicts logged: 15935
after:  Ran 19 tests in 1962.72 seconds: 16 passed, 3 failed (verdict store off)
        exit 1 in 1967 s; verdict logs before/after: 15935/15935 lines; identical: YES
```

The same three failures both times, pre-existing on the unmodified tree,
among them `AssertionError: screw should not interfere with z_nuts-0
(intersection volume 137.64424404779797)`. Every one of the 15935 verdicts,
emptiness and volume bits, is unchanged. No slowdown: 12 s faster, within
run-to-run noise.

### 9.3 Leonardo/models, `cam_hammer` (two exact fusions)

```
before: machinome build cam_hammer   exit 0 in 10 s; cam_hammer artifacts hashed: 14
after:  machinome build cam_hammer   exit 0 in 10 s; artifact hashes before/after identical: YES (14 files)
--- Leonardo BLOCKED (leo-build): machinome build cam_hammer ---
exit 0 in 9 s
asks: processes 3; asks: manifold3d: 2 by {'trimesh.boolean': 1, 'trimesh.util': 1}; imported: nothing
blocked build hashes identical to unblocked: YES (14 files)
```

An exact fusion builds with the mesh engine absent and never asks for it.
The faceted fusion's bytes are the golden's (5.2).

### 9.4 OpenAstroMount, all exact (branch `exact-engine-validation`, read-only)

Before: unblocked `machinome build` exit 0 in 35 s; `machinome test`
`Ran 9 tests in 557.83 seconds: 8 passed, 1 failed` (the known exact-common
wart). After, blocked:

```
--- OpenAstroMount BLOCKED (oam-build): machinome build ---
exit 0 in 35 s
asks: processes 3; asks: manifold3d: 2 by {'trimesh.boolean': 1, 'trimesh.util': 1}; imported: nothing
oam blocked build: stl 90 brep 90 (before: 90/90); viewer.json yes
--- OpenAstroMount BLOCKED (oam-test): machinome test ---
exit 1 in 561 s
Ran 9 tests in 556.91 seconds: 8 passed, 1 failed
asks: processes 1; asks: manifold3d: 2 by {'trimesh.boolean': 1, 'trimesh.util': 1}; imported: nothing
```

In every process of both blocked runs: zero asks of `machinome.manifold`,
every ask of `manifold3d` made by `trimesh.boolean` or `trimesh.util`, and
neither `machinome.manifold.engine` nor `manifold3d` imported (design.md
Open Question 1, as corrected at acceptance: trimesh asks from two of its
modules). The same failure as before.

The four projects' trees were unchanged after the legs
(`Locks/Pin_tumbler_lock dirty: 0`, `3D-Printers/Prusa3-vanilla dirty: 0`,
`OpenAstroMount dirty: 0`; Leonardo's three dirty paths predate the legs).

### 9.5 The universe sweep

Run by the orchestrator from the workspace root on the bench at 872d8a3
with the uncommitted implementation: `scripts/load-projects --bench <bench>
--moved` the six earlier moved-names files and this change's (empty)
`moved-names.toml`, `--timeout 300`, JSON in `load-projects.json` beside
this file (58220 bytes):

```
62 repositories, 129 rows: 117 ok, 4 expected, 2 unexpected, 0 timeout, 6 no-model; 2 skipped
```

Row for row identical to the sixth cycle's sweep in project, model,
checkout and outcome: no row for this cycle. Carried, expected:
`3D-Printers/Voron-2`, `Actuators/Internal-Cycloidal-Actuator`,
`Robots/YouCanBuildDog`, `Robots/openvmp`. Unexpected, pre-existing:
`3DPrintedClocks` and `Robotic-Arms/Dum-E`. Skipped by rule: `.Trash-1000`,
`sandbox`. The workspace venv installs `machinome[all]`, so the extra is
present for every project.

### 9.6 Failures

None: every leg green.

## 10. Records, ADR, specs

- **The correction accepted at implementation.** design.md Decision 11 and
  Open Question 1 now record, as the orchestrator's acceptance of 4 October
  2026, that trimesh asks for `manifold3d` at import from `trimesh.boolean`
  and `trimesh.util`, and that the finder finds nothing rather than raising
  (section 2). The planning text is otherwise as ratified.
- **ADR-176** (`docs/adrs/TEST-FRAMEWORK/`), recording the ratification and
  the answers to the Open Questions and the accepted correction; status lines
  and "Amendment (2026-10-04)" sections added to ADR-052, ADR-161, ADR-156 and
  ADR-167; ADR-176 indexed in `docs/adrs/README.md` and the four amended
  entries marked.
- **Warts.** `workflow/warts.md`'s lean-install entry "A `machinome build` in
  a fresh project worktree hung for three hours" gains a paragraph dated
  4 October with section 2's reproduction, marked "Reproduced, mechanism
  found; untriaged". Nothing else filed; Prusa3-vanilla's `shared_volume`
  stays in design.md's deferred list.
- **The campaign plan.** The "No package is split" paragraph ends "starts
  only on the pilot's word, for the architecture and the lean install" (the
  licence is settled); the "Done" paragraph names this cycle; the
  empirical-validation row carries section 9's results and this archive's
  path.
- **Specs.** `openspec archive mesh-engine --yes`:

  ```
  Applying changes to openspec/specs/kernel-extras/spec.md:
    ~ 3 modified
  Applying changes to openspec/specs/manifold-engine/spec.md:
    + 6 added
  Applying changes to openspec/specs/mesh-engine-dependency/spec.md:
    + 3 added
    ~ 2 modified
  Applying changes to openspec/specs/test-framework/spec.md:
    ~ 2 modified
  Totals: + 9, ~ 7, - 0, → 0
  Specs updated successfully.
  Change 'mesh-engine' archived as '2026-10-04-mesh-engine'.
  ```

  (with `moved-names.toml` and `load-projects.json`). A copy of
  `openspec/specs/` taken before the archive was diffed against the result:
  no requirement or scenario header was removed; the removed lines are the
  old text of the modified requirements. The new capability
  `manifold-engine` was given its Purpose, and `mesh-engine-dependency`'s,
  left "TBD" since the `defer-manifold-import-to-mesh-path` archive, was
  written.

  ```
  openspec validate mesh-engine --strict   -> Change 'mesh-engine' is valid   (before the archive)
  openspec validate --specs --strict       -> Totals: 46 passed, 0 failed (46 items)
  ```

- **Commits.** Nothing on this branch is amended: the implementation and
  these records land as further commits on `v0.8-split-mesh-engine` after
  the planning commit 872d8a3. `moved-names.toml` is copied to the
  workspace's `scripts/load-projects.d/mesh-engine.toml` by the orchestrator
  after integration; the applier wrote nothing in the workspace.
- **After the archive** (no source change since the suite of 5.3), the files
  that read specs, records and documentation, with the cycle's own, alone:
  `tests/test_release_records.py tests/test_docs_structure.py
  tests/test_docs_exports.py tests/test_profile_documentation.py
  tests/test_frame_precision_docs.py tests/test_mesh_engine_seam.py
  tests/test_manifold_engine.py tests/test_kernel_extras.py
  tests/test_core_kernel_free.py`: `84 passed, 352 subtests passed in 7.09s`.
