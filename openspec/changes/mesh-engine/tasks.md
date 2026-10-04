## 1. Baseline on the unmodified tree

- [ ] 1.1 Create `openspec/changes/mesh-engine/evidence.md` in the shape of the
  archived cycles' (`2026-10-04-scad-presentation/evidence.md`), with the bench
  commit, and record there the Context facts of design.md this cycle rests on:
  the probe of Decision 6 (`trimesh.boolean` against the four engine steps:
  equal vertex and face digests, equal component count, equal intersection
  volume), the flush-contact probe of the `manifold-engine` spec (`False`,
  `0.0`), the `-X importtime` line showing `manifold3d` under
  `trimesh.boolean`, and the project counts of the proposal's Impact
  (re-checked by grep). Proves: the evidence the design cites exists in the
  change.
- [ ] 1.2 The golden of design.md Decision 12, before any source change: write
  `tests/mesh_engine_golden.py` (not collected by pytest; `--record` writes,
  `--check` compares and prints one summary line) and its fixtures, recording
  into `tests/data/mesh_engine_golden.json`, with the bench commit: the
  ordered faceted verdicts `(path, is_empty, float.hex(volume))` and test
  outcomes and failure messages of every `tests/meta_project/test_*.py`
  fixture under `--faceted --no-verdict-store` into a temporary
  `SOLID_BUILD_DIR`, recorded by wrapping `machinome.test._memoized`; the
  admission refusal messages for the holey box as a compared part and as a
  fusion child; the SHA-256 and length of a faceted `FusionNode`'s STL fusing
  three `StlNode` children (one rotated, two overlapping); for the
  `assembly_supported*.py` fixtures, the SHA-256 of the virtual floor's
  vertices and faces and of every contact list `_interface_contacts`
  returns, in order, and each assertion's outcome; `assertJoined`'s body
  counts for `welded.py`, `unwelded.py` and `cross_part_weld.py` under
  `--faceted`; the `.mesh` fallback's `(is_empty, volume hex)` for the
  `FakeNode` pairs of `tests/test_assertions.py`. Run `--record` twice in
  separate processes and record that both agree. `--check` after the change
  reports the fusion child's message (`Error.NotManifold` →
  `NotManifold`, Decision 4) and the compared part's "cannot build a Manifold"
  → "cannot build a solid" as expected differences and nothing else. Proves:
  bit identity, by construction checked.
- [ ] 1.3 Run, on the unmodified tree, one pytest process at a time:
  `tests/test_mesh_engine_dependency.py`, `test_manifold_cache.py`,
  `test_verdict_store.py`, `test_verdict_store_cli.py`,
  `test_kernel_extras.py`, `test_core_kernel_free.py`,
  `test_broad_phase_culling.py`, `test_assembly_integrity.py`,
  `test_assembly_supported.py`, `test_cli_lazy_imports.py`,
  `test_node_lazy_exports.py`, `test_vet_universe.py`,
  `test_flexible_cache_performance.py`, `test_flexible_verdict_identity.py`,
  `test_persistent_piece_facts.py`, `test_intersection_memo.py`,
  `test_exact_geometry.py`, `test_backend_neutral_materialization.py`,
  `test_face_box_culling.py`, `test_assertions.py`, `test_molejo_adapter.py`,
  `test_stl_node.py`, `test_meta.py`; record counts and wall time. Proves: the
  touched suites' green baseline.

## 2. Red tests

- [ ] 2.1 `tests/test_mesh_engine_seam.py`: `mesh_engine()` returns the module
  `machinome.manifold.engine`, whose `CONTRACT` equals
  `machinome.mesh_engine.CONTRACT == 1`; every member of the `MeshEngine`
  Protocol is a function whose `__module__` is the provider; with
  `sys.modules['machinome.manifold.engine'] = None` and the cache cleared,
  `mesh_engine()` is `None` and `require_mesh_engine('faceted fusion Bracket',
  'unioning its children')` raises `MeshEngineUnavailable` whose message is
  design.md Decision 2's, naming both arguments, "the mesh engine" and
  `pip install "machinome[manifold]"`; stub providers declaring `CONTRACT = 2`
  and none are refused by both functions with `MeshEngineIncompatible` naming
  `machinome.manifold.engine`, 1 and 2 (or "declares none"); a stub whose
  import raises `ImportError` from inside surfaces that error, not `None`;
  resolution happens once per process; the package metadata declares a
  `manifold` extra; reading any operation off `machinome.manifold` raises
  `AttributeError`. Red: `mesh_engine()` returns `(Manifold, Mesh)`, there is no
  `CONTRACT`, no provider, no extra, and every `ImportError` reads as absent.
- [ ] 2.2 `tests/test_manifold_engine.py`, in a fresh interpreter with arrays
  written out in numpy (no trimesh): `solid_from_mesh` of a closed cube is
  admitted (`fault` is `None`) and of the cube less one triangle is refused
  with `NotManifold`; `placed_solid` by a 4x4 translation moves its
  `mesh_arrays` by exactly that translation; two cubes sharing a face
  intersect non-empty with volume `0.0`, two overlapping by half a side give
  `volume` 4.0 within float32 rounding of the probe; `unite_solids` of three
  equals the pairwise left fold byte for byte and of one returns it unchanged;
  `centred_box((2, 4, 6))` has volume 48 and bounds ±(1, 2, 3); `mesh_arrays`
  answers three vertex columns; `identity()` is `('manifold3d',
  importlib.metadata.version('manifold3d'))`; afterwards `trimesh`, `OCP`,
  `cadquery` and `build123d` are absent from `sys.modules`; `CONTRACT` is an
  integer literal in the source (AST). Red: the module does not exist.
- [ ] 2.3 The core holds no mesh-engine code, in `tests/test_core_kernel_free.py`:
  `KERNELS` gains `manifold3d` and the import table expects
  `'machinome/manifold/engine.py': ['manifold3d']` and nothing else for it;
  `EXTRA_OF` gains `'machinome/manifold/engine.py': 'manifold'` (so the
  provider calls `require_extra('manifold', ...)` before importing its kernel);
  a new test finds no attribute chain `trimesh.boolean` in any module under
  `machinome/` (AST); another finds `machinome.manifold` imported or spelled as
  a whole string only in `machinome/mesh_engine.py` outside
  `machinome/manifold/`. In `tests/test_kernel_extras.py`: `manifold3d` is not
  required; `EXTRAS` gains `'manifold': {'manifold3d'}` and `all` becomes
  `{'machinome[cadquery,build123d,step,molejo,occt,manifold]'}`; no node
  extra includes `machinome[manifold]`; `MODULES` gains
  `'machinome.manifold.engine': ('manifold', 'the mesh engine
  (machinome.manifold.engine)', ('manifold3d',))`, so the absent-kernel and
  broken-kernel subprocess checks run for it. Red: `mesh_engine.py` imports
  `manifold3d`, `test.py` calls `trimesh.boolean` twice, `manifold3d` is
  required, no `manifold` extra, no provider.
- [ ] 2.4 `tests/mesh_engine_absent.py` in the finder form (design.md Decision
  11), with `run_python`, `run_machinome` and `mesh_engine_is_installed`;
  then `tests/test_mesh_engine_dependency.py` rewritten over it, every case
  asserting through the per-process log:
  - importing `machinome.test` with `manifold3d` and `machinome.manifold`
    absent succeeds, `machinome.manifold.engine` is not imported, zero asks of
    `machinome.manifold`, and every ask of `manifold3d` names
    `trimesh.boolean`;
  - `machinome test tests/meta_project/exact_tight_fit.py` and
    `solid_integrity_green.py` pass with both absent and zero asks of
    `machinome.manifold` in every process;
  - `assembly_integrity_contact.py` fails naming the mesh engine,
    `assertNoSolidInterference` and `pip install "machinome[manifold]"`, and
    `assembly_supported_exact.py` naming `assertAssemblySupported` and the
    same install line; neither shows `ModuleNotFoundError`;
  - the same refusal with `absent=('manifold3d',)` only (the provider present,
    its kernel absent);
  - with `manifold3d` broken (found, failing from inside), the run shows that
    import error, not "requires the mesh engine";
  - `machinome test --faceted` of `flush.py`, and `machinome test` of it with
    `SOLID_TEST_KERNEL=faceted`, with both absent: exit 1, stderr design.md
    Decision 8's refusal, the faceted kernel's line not printed, and no STL
    under the scratch build directory;
  - `machinome build` of an all-`StlNode` fixture with both absent: exit 0,
    every STL written, zero asks of `machinome.manifold`; of a stale faceted
    `FusionNode` fixture: fails naming the fusion and the install line (each
    fixture written under `tests/meta_project/` if none serves).
  `tests/test_verdict_store_cli.py`'s `WithoutTheMeshEngine` moves to the
  finder and asserts zero asks of `machinome.manifold` in both runs. Red: the
  refusals name `pip install manifold3d`; `--faceted` builds before it refuses;
  a broken `manifold3d` reads as absent.
- [ ] 2.5 The verdict store, in `tests/test_verdict_store.py`: `KERNELS` names
  no `manifold3d`; with `machinome.manifold.engine.identity` patched to report
  another version, a faceted verdict kept under the real one is computed again
  and an exact verdict is served; with `mesh_engine` answering `None`, a
  faceted comparison's persisted key is `None`; the existing
  `test_computing_the_stamp_imports_no_kernel` stays green. Red: `KERNELS`
  holds the row, the provider has no `identity`, a faceted key ignores the
  engine.
- [ ] 2.6 The two former `trimesh.boolean` paths, in
  `tests/test_manifold_cache.py`: with `trimesh.boolean.union` and
  `trimesh.boolean.intersection` patched to raise, `assertJoined` on the
  faceted welded pair passes and on the unwelded pair fails with its message,
  and the `FakeNode` `.mesh` fallback returns its golden `(is_empty, volume)`;
  a counting wrapper on `machinome.manifold.engine.unite_solids` sees one call
  per `assertJoined`; a non-volume mesh still raises `ValueError('Not all
  meshes are volumes!')`. Red: both paths call `trimesh.boolean`.
- [ ] 2.7 Run 2.1 to 2.6 on the unmodified source in one pytest process;
  record in the evidence every red test and its reason, verbatim.

## 3. The provider, the seam, the extra

- [ ] 3.1 `machinome/manifold/__init__.py` (Apache-2.0 header, a docstring, no
  names) and `machinome/manifold/engine.py`: `require_extra('manifold', 'the
  mesh engine (machinome.manifold.engine)', 'manifold3d')` first; numpy and
  manifold3d imports; `CONTRACT = 1` as a literal; the ten operations of
  design.md Decision 3, each the manifold3d call the table gives; no import of
  trimesh, the seam or any core module but `machinome.extras`; no state.
  Proves: 2.2 green.
- [ ] 3.2 `machinome/mesh_engine.py`: `CONTRACT`, `PROVIDER`, `MeshSolid`, the
  Protocols `MeshSolids`, `MeshComposition`, `MeshComparison`, `MeshIdentity`
  and `MeshEngine`, `MeshEngineUnavailable` and `MeshEngineIncompatible` with
  design.md Decision 2's messages, `_absent`, `mesh_engine()` and
  `require_mesh_engine()`; the module docstring states the requiring paths and
  that the core names the provider here only. Proves: 2.1 green.
- [ ] 3.3 `pyproject.toml`: drop `manifold3d` from `dependencies` (its comment
  on kernels names it among the extras); add `manifold = ["manifold3d"]` with a
  comment naming `machinome.manifold.engine` and the rule; `all` gains
  `manifold`. `requirements.txt`: `manifold3d` under the kernel-extras comment,
  which names `manifold`. Proves: 2.3's metadata checks green.

## 4. The core over the seam

- [ ] 4.1 `machinome/test.py` (design.md Decisions 4-6): `_mesh_engine`;
  every site of design.md's site table through the provider's operations,
  looked up at call time; `_admitted` reading `fault`; `_mesh_boolean` for
  `assertJoined`'s faceted union and the `.mesh` fallback; the private renames
  of Decision 5; docstrings and comments that say a Manifold is built, placed
  or read say the mesh engine's solid. No change to culling order, cache keys,
  limits, messages (but Decision 4's "cannot build a solid") or the statics
  program.
- [ ] 4.2 `machinome/node/fusion.py` (Decision 7): `_generate_faceted_stl`
  through `solid_from_mesh`, `fault`, `unite_solids`, `mesh_arrays`, the
  engine's name from `identity()`; `faceted-fusion-manifold-v1` kept.
- [ ] 4.3 `machinome/_verdict_store.py` (Decision 9): `KERNELS` loses the
  `manifold3d` row and its comment the faceted engine; `persisted_key` gains
  `engine`; `test.py`'s `_persisted_key` passes `mesh_engine().identity()` for a
  faceted key, `()` for an exact one, and `None` when the engine is absent or
  reports no version.
- [ ] 4.4 `machinome/manager/test.py` (Decision 8): after
  `set_comparison_policy` and before the faceted kernel's line, a faceted
  policy calls `require_mesh_engine('machinome test on the faceted kernel',
  "every pair the run compares is compared on the parts' meshes")`, a
  `MeshEngineUnavailable` going to `self.fail(str(error))`.
- [ ] 4.5 Comments naming the Manifold cache in `machinome/node/flexible.py`
  (lines 375, 422) say the faceted solid cache.
- [ ] 4.6 Run 2.3, 2.4, 2.5 and 2.6 green.

## 5. Existing tests repointed

- [ ] 5.1 Repoint without changing any asserted verdict, count or message
  other than Decision 4's two: the renamed privates (`test_flexible_cache_performance.py`,
  `test_manifold_cache.py`, `test_verdict_store.py`, `test_persistent_piece_facts.py`,
  `test_assembly_integrity.py`, `test_assembly_supported.py`,
  `test_flexible_verdict_identity.py`, `test_face_box_culling.py`,
  `test_molejo_adapter.py`, `test_intersection_memo.py`); the counting test of
  `test_manifold_cache.py` counts `machinome.manifold.engine.solid_from_mesh`
  in place of patching `require_mesh_engine` with a pair;
  `test_assembly_integrity.py`'s "no whole-assembly union" patches
  `machinome.manifold.engine.unite_solids`; `test_broad_phase_culling.py`'s
  `Placement` builds and places its cubes with the provider's `centred_box`
  and `placed_solid` and reads bounds off `mesh_arrays`, and its fixture
  placements use `placed_solid` on the handle `_fast_geometry` returns;
  `test_exact_geometry.py`'s `no_engine` patch keeps its target;
  `test_backend_neutral_materialization.py`'s fusion refusal patch keeps
  `machinome.node.fusion.require_mesh_engine`; `test_cli_lazy_imports.py`'s
  `WATCHED` adds `machinome.manifold.engine`; `test_node_lazy_exports.py`'s
  comment points at the finder form. List in the evidence every changed
  assertion target and why.
- [ ] 5.2 `tests/mesh_engine_golden.py --check`: zero unexpected differences;
  record the summary line. Proves: bit identity.
- [ ] 5.3 The whole framework suite, alone (it shares `tests/_build`); record
  counts and wall time against 1.3 and the line's last full run (4439 passed,
  4 skipped at 69c7019).

## 6. Docs

- [ ] 6.1 `docs/architecture.md`: the test-framework paragraphs that build,
  cache and intersect Manifolds (lines 2261-2300 and 2357-2391 at 69c7019) say
  the mesh engine's solids through the seam; line 69's conditional-engine
  sentence names the provider and the extra; the verdict store's stamp
  paragraph (line 2370) drops `manifold3d` and says a faceted key carries the
  engine's identity; the source map gains a row "Manifold mesh engine (leaves
  the core in layer 2) | `machinome/manifold/engine.py` | `manifold-engine` |
  176", and the test framework row names `machinome/mesh_engine.py` and
  `mesh-engine-dependency`.
- [ ] 6.2 `docs/start/install.rst`: "The package itself brings trimesh,
  SolidPython and the mesh engine" says it brings trimesh and SolidPython; the
  extras table gains `machinome[manifold]` → `machinome.manifold.engine` → "the
  mesh engine, for every comparison on meshes: a part without exact geometry,
  `machinome test --faceted`, `assertAssemblySupported`, a fusion of such
  parts"; the install section's "none for a project whose parts are all
  OpenSCAD, JSCAD or STL" becomes `machinome[manifold]` for such a project.
  `docs/howto/fast-tests.rst`: the faceted kernel needs `machinome[manifold]`
  and a faceted run without it refuses at its start. `README.rst`: the
  `manifold3d` paragraph says it is the `manifold` extra. A docs build of the
  touched pages, recorded.
- [ ] 6.3 `docs/project/changelog.rst`, one bullet under its existing
  Unreleased section:

  > **The mesh engine is a provider, installed by its extra.** manifold3d,
  > which decides every comparison on meshes, is reached only through the
  > mesh engine ``machinome.manifold.engine``, resolved by the seam
  > ``machinome.mesh_engine`` with a versioned contract, and the core calls
  > none of its API, ``assertJoined``'s union of meshes included. Verdicts,
  > refusals and fused meshes are bit for bit what they were.
  >
  > **Breaking: ``pip install machinome`` no longer installs manifold3d.**
  > Install ``machinome[manifold]`` (or ``machinome[all]``) for a project
  > that compares a part without exact geometry, runs ``machinome test
  > --faceted``, calls ``assertAssemblySupported``, fuses meshes, or imports
  > manifold3d or calls ``trimesh.boolean`` itself. Without it each of those
  > refuses naming the install line, and ``machinome test`` on the faceted
  > kernel refuses at its start, before building anything; an all-exact
  > project needs nothing new. The verdict store starts afresh once, and a
  > manifold3d upgrade no longer discards exact verdicts (ADR-176).

  Not in `HISTORY.rst` (its top section is the released 0.7.1; the release
  records tests forbid "unreleased" above it).

## 7. The campaign plan

- [ ] 7.1 `workflow/ongoing/lean-core.md`, in the implementation commit and
  nothing else in it: the dependency table's `manifold3d` row reads "the
  `manifold` extra; `machinome.manifold.engine` behind `machinome.mesh_engine`";
  "Where the core reaches each kernel"'s mesh-engine bullet says the seam
  resolves a provider; the "Import paths" table gains the row `the mesh engine
  | machinome.manifold.engine | machinome[manifold] | machinome-manifold`;
  "State of the campaign"'s "Struck or deferred" sentence records that
  manifold3d left the required list on 4 October 2026 by this cycle (watchdog
  stays); "What packaging does not solve" names `machinome[manifold]`; the
  "Empirical validation" table gains this cycle's row (projects, why, the
  result in one sentence, the evidence path).

## 8. Stop and report (the applier)

- [ ] 8.1 With 1 to 7 done and the suite green, stop before any commit and
  report to the orchestrator: the diff stat, the red and green results, the
  suite's counts and wall time, the golden's summary line. The applier spawns
  no agent and runs none of the validation below.

## 9. Empirical validation (the orchestrator runs every leg)

Each deep leg is run by the orchestrator, itself or through one validator it
briefs and launches, one at a time, with `PYTHONPATH=<bench>` and the workspace venv, into
scratch build directories, `PYTHONDONTWRITEBYTECODE=1`, never changing a
project file. *Before* means the line's bench `machinome/WTs/v0.8-split` at
69c7019, which holds this bench's unmodified source and may run at any time;
*after* means this bench after 8.1, uncommitted. The verdict recorder is one
scratch script used for both, so the two logs come from the same code:

```python
import json, sys
log = open(sys.argv.pop(1), 'w')
import machinome.test as t
inner = t._memoized
def recorded(key, compute):
    stats = inner(key, compute)
    log.write(json.dumps([None if key is None else key[2],
                          bool(stats.is_empty), float(stats.volume).hex(),
                          bool(stats.exact)]) + '\n')
    log.flush()
    return stats
t._memoized = recorded
from machinome.cli import manage
manage()
```

- [ ] 9.1 **Deep, `Locks/Pin_tumbler_lock`.** Before and after: the recorder
  running `test --faceted --no-verdict-store`. Expected: 24 tests with the
  outcomes of cycle 6's evidence (`2026-10-04-scad-presentation/evidence.md`)
  both times, and the two verdict logs identical line for line. After, with
  `tests/mesh_engine_absent.py`'s finder refusing `manifold3d` and
  `machinome.manifold`: `machinome test --faceted` exits 1 with design.md
  Decision 8's refusal before building (no new STL in the scratch directory);
  `machinome build` exits 0 with zero asks of `machinome.manifold` in every
  process. Why this project: the campaign's faceted reference, a running root
  with a flexible spring and `Solid2Node` parts, cheap.
- [ ] 9.2 **Deep, `3D-Printers/Prusa3-vanilla`.** Before and after: the recorder
  running `test --no-verdict-store` on the default kernel, as the project runs
  (its parts are `Solid2Node`s but for two `Build123dNode`s and three
  `MolejoNode`s, so nearly every pair is faceted; the log records each
  verdict's path). Expected: the same outcome for every
  test both times; the two verdict logs identical line for line, so every
  `assertNotIntersecting` (63 call sites), `assertBlockedBeyond` (10),
  `assertFreeWithin` (6), `assertNoSolidInterference` (5),
  `assertNoDisconnectedSolids` (5) and `assertIntersectVolumeBelow` (4)
  verdict, empty-or-not and volume bits, is unchanged (call-site counts by grep
  of `simulation/`, 4 October 2026; its 25 `assertGap` and 3
  `assertSharesBelow` are the project's own trimesh measurements); wall times
  recorded, a slowdown beyond run-to-run noise returning to the orchestrator.
  Why: the heaviest faceted user of the catalogue.
- [ ] 9.3 **Deep, the faceted fusion and an exact fusion.** No project fuses
  faceted children (design.md Open Question 4); the fused STL's bytes are
  5.2's golden. On `Leonardo/models` (model `cam_hammer`, two exact
  `FusionNode`s over `CadQueryNode`s, the smallest candidate): after, build it
  once unblocked and once with the finder refusing `manifold3d` and
  `machinome.manifold`, into two scratch directories. Expected: both exit 0,
  the two fusions' STL and BREP SHA-256 equal across the two builds, and zero
  asks of `machinome.manifold` in the blocked build. Why: an exact fusion must
  never ask for the mesh engine.
- [ ] 9.4 **Deep, OpenAstroMount, all exact.** After, read-only on its own
  checkout, with the finder refusing `manifold3d` and `machinome.manifold`:
  `machinome build` and `machinome test` into a scratch build directory, and
  the same two unblocked into another. Expected: the blocked runs' results
  equal the unblocked ones (its known exact-common wart included, if it shows);
  in every process of the blocked runs, zero asks of `machinome.manifold`,
  every ask of `manifold3d` made by `trimesh.boolean`, and neither
  `machinome.manifold.engine` nor `manifold3d` imported (design.md Open
  Question 1).
- [ ] 9.5 **Shallow, the universe,** run by the orchestrator from the workspace
  root: `scripts/load-projects --bench <bench> --moved
  scripts/load-projects.d/exact-engine.toml
  scripts/load-projects.d/leaf-contract.toml
  scripts/load-projects.d/backend-switch.toml
  scripts/load-projects.d/lean-install.toml
  scripts/load-projects.d/expression-type.toml
  scripts/load-projects.d/scad-presentation.toml
  <bench>/openspec/changes/mesh-engine/moved-names.toml --timeout 300 --json
  <bench>/openspec/changes/mesh-engine/load-projects.json`. Expected: identical
  to the sixth cycle's sweep, no row for this cycle (its table is empty, and
  the workspace venv still installs manifold3d through `[all]`).
- [ ] 9.6 A failed validation returns to the orchestrator with the project's
  output; nothing is fixed in a project. The orchestrator hands the reports to
  the paused applier.

## 10. Records, ADR, specs, commit (the applier, after 9)

- [ ] 10.1 Fold 9.1-9.5 into the evidence, verbatim where they quote a message,
  a digest or a summary line.
- [ ] 10.2 Write ADR-176 (`docs/adrs/TEST-FRAMEWORK/`, design.md "ADRs"),
  recording the pilot's ratification and the answers to the Open Questions;
  add status lines and amendment sections to ADR-052, ADR-161, ADR-156 and
  ADR-167; add ADR-176 to `docs/adrs/README.md`.
- [ ] 10.3 Sync the four delta specs into `openspec/specs/` (the new
  `manifold-engine`, and `mesh-engine-dependency`, `kernel-extras`,
  `test-framework`), archive the change with `openspec archive mesh-engine`,
  validate `--strict`, and make the implementation commit on
  `v0.8-split-mesh-engine`. Nothing is amended, nothing is pushed, and nothing
  is written outside the bench: the copy of `moved-names.toml` to the
  workspace's `scripts/load-projects.d/mesh-engine.toml` is the orchestrator's,
  after integration.
