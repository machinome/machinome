# Evidence — `exact-engine`

The first cycle of the lean-core campaign (`workflow/ongoing/lean-core.md`,
item 3 of "What it takes"). Worktree `machinome/WTs/v0.8-exact-engine`,
branch `v0.8-exact-engine`, cut from `v0.8` at feb23f2. Planning commit
8c146a7. Every command below ran from inside the worktree with
`PYTHONPATH=<worktree>` and the workspace venv; `machinome.__file__`
resolved to `<worktree>/machinome/__init__.py`.

## 1. Baseline on the unmodified tree

### 1.1 The golden fixtures

`tests/exact_engine_golden.py` was written before any source change and run
twice, in two separate processes, on the unmodified tree at 8c146a7, reading
volume, solid count, bounding box and face boxes through the then-current
`machinome.exact` (`cached_bounding_box`'s `BoundBox` read as
`((xmin, ymin, zmin), (xmax, ymax, zmax))`, the molejo solid written with
`BRepTools.Write_s(shape.wrapped, …)`):

```
env -C <worktree> PYTHONPATH=<worktree> .venv/bin/python tests/exact_engine_golden.py --out <scratch>/golden_run1.json
env -C <worktree> PYTHONPATH=<worktree> .venv/bin/python tests/exact_engine_golden.py --out <scratch>/golden_run2.json
cmp golden_run1.json golden_run2.json  ->  IDENTICAL
```

The first run is `tests/data/exact_engine_golden.json`, which records
`"bench_commit": "8c146a7165b529c8b4be6cb82de6d963865e1c22"`. Its rows
(solids, volume, face-box array shape, BREP and STL SHA-256 prefixes):

| fixture | solids | volume | face boxes | `.brep` | `.stl` |
|---|---|---|---|---|---|
| CadQuery box less a bore | 1 | 3497.3451754256325 | (7, 2, 3) | `0ae8a99bf686bf5a` | `94624c82a5eb078e` |
| the same part in build123d | 1 | 3497.345175425631 | (7, 2, 3) | `e1126d6c20cd38f3` | `7c2d8b23c7f91243` |
| `Build123dSheetNode` panel | 1 | 3364.3805509807644 | (7, 2, 3) | `ad4dc517d0eaa90c` | `c56509d6b75c2369` |
| `StepNode` (`tests/step_project` `WrappedSinglePart`) | 1 | 216.0 | (6, 2, 3) | `202b835527f4241a` | `5c54ec16656bdf79` |
| exact fusion, shaft into an equal bore | 1 | 1244.0706908215589 | (6, 2, 3) | `1867a326ee1d9464` | `f6c311c891adf148` |
| fusion of a CadQuery and a build123d child | 2 | 3648.1416227979425 | (10, 2, 3) | `41d2b8fd409930aa` | `a4a57ac3e200fa20` |
| `MolejoNode` spring at lift 4.0 | 1 | 7205.1728234619995 | (3, 2, 3) | `203e22d67025fa7e` | `b82876ab2a660824` |

The mixed fusion's build123d peg stands inside the block's bore without
touching it, so the fuse is a two-solid compound; it is kept as the
compound case. The molejo row's `.stl` is the binding's snapshot STL, which
molejo's mesh evaluator writes; its `.brep` is the solid `shape()` returned.

### 1.2 Probes and counts

**Bytes (design.md Decision 4).** `<scratch>/probe_bytes.py`: a CadQuery
10 mm box fused with an r = 4 mm, 15 mm cylinder through the then-current
`machinome.exact.fuse_shapes`, written either by CadQuery's `exportBrep` and
`exportStl(tolerance=0.1, angularTolerance=0.1)` or by the raw calls
`BRepTools.Write_s`, `BRepMesh_IncrementalMesh(s, 0.1, True, 0.1, True)`,
`StlAPI_Writer` with `ASCIIMode = False`. Four separate processes, alternating:

```
cadquery brep 11f404441cb7f5aae05e35c2e9318b983836c1819c2483d0de90cdd0dc3bdc33 stl 50f4a2f7d397c86ef164b614bd927ff2773922d6d2920fe586b8aef034a923e1 volume 1502.6548245743668 solids 1
ocp brep 11f404441cb7f5aae05e35c2e9318b983836c1819c2483d0de90cdd0dc3bdc33 stl 50f4a2f7d397c86ef164b614bd927ff2773922d6d2920fe586b8aef034a923e1 volume 1502.6548245743668 solids 1
cadquery brep 11f404441cb7f5aae05e35c2e9318b983836c1819c2483d0de90cdd0dc3bdc33 stl 50f4a2f7d397c86ef164b614bd927ff2773922d6d2920fe586b8aef034a923e1 volume 1502.6548245743668 solids 1
ocp brep 11f404441cb7f5aae05e35c2e9318b983836c1819c2483d0de90cdd0dc3bdc33 stl 50f4a2f7d397c86ef164b614bd927ff2773922d6d2920fe586b8aef034a923e1 volume 1502.6548245743668 solids 1
```

Same BREP and STL SHA-256 both ways and across processes.

**Project counts (proposal, Impact).** Re-checked on 3 October 2026 over
`projects/` (excluding worktrees, venvs and build directories): 12 files
import `machinome.exact` — `Calculators/Curta-Type-I-3x` 11,
`OpenAstroMount/simulation` 1. The 29 files that call a CadQuery method on a
`shape()` result are the orchestrator's measurement of 2 October 2026, not
re-measured here.

**The cadquery-ocp range.** Installed metadata: cadquery 2.7.0 requires
`cadquery-ocp<7.9,>=7.8.1`; build123d 0.10.0 requires
`cadquery-ocp<7.9,>=7.8`. The venv holds cadquery-ocp 7.8.1.1.post1. The
`occt` extra is therefore `cadquery-ocp>=7.8.1,<7.9`.

## 2. Red first (task 2.8)

The tests of tasks 2.1 to 2.7 were written before any source change and run
on the unmodified tree (8c146a7 plus the golden script and these tests), in
one pytest process:

```
env -C <worktree> PYTHONPATH=<worktree> .venv/bin/python -m pytest -q -p no:cacheprovider \
  --continue-on-collection-errors tests/test_exact_engine_seam.py \
  tests/test_exact_engine_dependency.py tests/test_front_end_free_exact.py \
  tests/test_occt_engine.py tests/test_exact_currency.py tests/test_core_kernel_free.py \
  tests/test_vet_assertions.py::ExactEngineInternalTest tests/test_vet_assertions.py::FrameworkInternalTest
26 failed, 3 passed, 1 warning, 9 errors in 43.72s
```

Each failure and its reason:

| task | test | outcome on the unmodified tree | reason |
|---|---|---|---|
| 2.1 | `tests/test_exact_engine_seam.py` (all) | collection error | `ModuleNotFoundError: No module named 'machinome.exact_engine'`; no `occt` extra is declared either |
| 2.2 | `ImportLoadsNoEngineTest` | failed | `ModuleNotFoundError: No module named 'machinome.exact_cache'`. A separate probe of the existing modules: `import machinome.node.fusion` leaves `OCP`, `cadquery` and `machinome.exact` in `sys.modules` (fusion imports `machinome.exact` at module top) |
| 2.2 | `StaleFusionNamesTheInstallTest` | failed | `0 == 0`: the build of the stale fusion with `machinome.occt` refused succeeds, because nothing resolves an engine |
| 2.2 | `FacetedProjectWithoutEngineTest` | failed in this run, then passed | the first draft compared whole summary lines, which carry the run's wall time (`0.07` against `0.17 seconds`); corrected to compare the `(ran, passed, failed)` counts, it passes on the unmodified tree, as a guard: a faceted project never reached the exact stack |
| 2.2 | `CurrentFusionDoesNotResolveTheEngineTest` | passed | a guard, as the task says: the unmodified tree has no engine to resolve. Its power to fail is shown in group 4 below |
| 2.3 | `FrontEndFreeProjectTest` | failed | the bare `TopoDS_Shape` render reaches `machinome/exact.py` `write_brep`: `AttributeError: 'OCP.OCP.TopoDS.TopoDS_Shape' object has no attribute 'exportBrep'` |
| 2.4 | `EngineOperationsTest` (8 tests) | errors | the probe subprocess: `ModuleNotFoundError: No module named 'machinome.occt'` |
| 2.4 | `ContractDeclarationTest` | failed | `FileNotFoundError: …/machinome/occt/engine.py` |
| 2.5 | `CurrencyTest`, six node kinds | failed | `shape()` is a CadQuery object: `<cadquery.occ_impl.shapes.Compound …> is not an instance of <class 'OCP.OCP.TopoDS.TopoDS_Shape'>` (CadQuery, build123d, sheet, fusion, two-solid workplane), `<cadquery.occ_impl.shapes.Solid …>` (STEP, molejo) |
| 2.5 | `test_the_engine_measures_a_cadquery_shape` | failed | `ModuleNotFoundError: No module named 'machinome.occt'` |
| 2.6 | `test_no_core_module_imports_the_kernel_or_cadquery` | failed | `machinome/exact.py` (OCP, cadquery), `machinome/node/adapters/molejo.py` (cadquery), `machinome/test.py` (OCP) besides the allowed `step.py` |
| 2.6 | `test_the_old_exact_module_is_gone` | failed | `machinome/exact.py` exists |
| 2.6 | `test_the_seam_is_the_only_module_naming_the_engine` | failed | `[] != ['machinome/exact_engine.py']`: no seam |
| 2.6 | `test_the_test_framework_binds_no_exact_name` | 9 subtests failed | `machinome.test` binds all nine names through `_deferred_exact` |
| 2.7 | `ExactEngineInternalTest` | failed | vet reports none of `machinome.occt.engine.write_brep` (line 6), `machinome.exact_artifacts` (line 7), `machinome.exact_cache` (line 11): none is in the contract deny list. The two contract lines already pass |
| 2.7 | `FrameworkInternalTest` | passed | its fixture's `import machinome.exact` now reads `import machinome.occt.engine`, a contract member, as the `vet` delta's "public contract passes" scenario names |

## 3. The seam and the engine (task 3.4)

`tests/test_exact_engine_seam.py tests/test_occt_engine.py` on the tree with
the seam, the engine and the `occt` extra: `20 passed, 13 subtests passed in
2.48s`.

## 4. The core's exact path over the seam

**Task 4.9.** `tests/test_exact_engine_dependency.py
tests/test_front_end_free_exact.py tests/test_exact_currency.py
tests/test_core_kernel_free.py tests/test_exact_engine_seam.py
tests/test_occt_engine.py`: `37 passed, 1 warning, 30 subtests passed in
34.48s`.

**The golden comparison** (task 1.1's script, reading the same measurements
through `machinome.occt.engine` and `machinome.exact_cache`):

```
env -C <worktree> PYTHONPATH=<worktree> .venv/bin/python tests/exact_engine_golden.py --check
golden comparison: 7 fixtures, 0 differences
```

Every `.brep` and `.stl` SHA-256, volume (compared as `repr` of the float),
solid count, bounding box and face-box array digest equals the baseline.

**The current-fusion guard can fail (task 2.2).** With
`ExactLeafNode.materialize` temporarily converting before its currency checks
(design.md Decision 7's finding), `CurrentFusionDoesNotResolveTheEngineTest`
failed:

```
E   AssertionError: 1 != 0 :  INFO -    core.builder - START
E   ERROR -    core.builder - tests/meta_project/exact_fusion_current.py:PinnedHub: failed to assemble project: exact leaf pin requires the exact engine because its render result becomes exact geometry; install it with 'pip install "machinome[occt]"'. A model with no exact node never needs it
1 failed in 16.42s
```

The order was restored (the file compared byte-equal to its saved copy) and
the test passed again (`1 passed in 17.09s`). No build path reached an exact
operation for current artifacts: the stop-and-return clause did not apply.
The fixture is built twice unblocked before the blocked build because the
first build's sweep removes the fused children's STLs, which the second
restores (pre-existing behaviour, observed and not changed here).

**Task 4.10.** With the five deny-list entries,
`tests/test_vet_assertions.py tests/test_vet_universe.py`: `40 passed, 60
subtests passed in 0.42s` (after the pin of task 5.1 below).

## 5. Existing tests repointed (task 5.1)

No asserted verdict, volume or count changed. Every change of an expected
type, a patch target or an asserted subject, and why:

- **Type of `shape()` and of engine results.** Where a test called a
  CadQuery method on a `shape()` result, a `cached_shape` load, a placement
  or a Boolean result (`Volume`, `BoundingBox`, `Solids`, `Faces`,
  `isValid`), it now wraps the value with `cq.Shape.cast(...)`, the
  values asserted unchanged: `test_exact_geometry.py` (6 sites),
  `test_exact_placement_cache.py` (2), `test_face_box_culling.py` (face
  count), `test_exact_common_guard.py` (3), `test_resolved_exact_witness.py`
  (2), `test_exact_input_copies.py` (1), `test_tessellation_precision.py`
  (2), `test_build123d_adapter.py` (7), `test_molejo_adapter.py` (1),
  `test_sheet_leaf.py` (9), `test_step_node.py` (17),
  `test_external_wrapper_identity.py` (3). Reason: the currency is the
  bare `TopoDS_Shape` (ADR-160).
- **Expected type changed:** `test_build123d_adapter.py`
  `test_build123d_solid_converts_preserving_volume` asserted
  `isinstance(shape, cq.Shape)`; it now asserts `TopoDS_Shape`, and the
  conversion is `machinome.node.adapters.build123d.build123d_shape` (the
  free `shape_from_rendered` is gone; the CadQuery conversion is
  `workplane_shape(rendered, engine)`).
- **Fixtures that stand in for an exact node now hold the currency**
  (`.val().wrapped` or `getattr(shape, 'wrapped', shape)`), since the
  engine's `bounds`, `face_bounds` and `mutually_outside` take the
  currency only: `ShapeNode` in `test_exact_geometry.py`, `ExactRigidNode`
  fixtures in `test_assembly_supported.py`, `ExactShapeWithoutIdentity` in
  `test_verdict_store.py`, the cq edge, shell and unidentified box in
  `test_face_box_culling.py`, `_exact` in `test_manifold_cache.py`, and the
  shapes handed to `_exact_verdict` and `_resolved_interior`. Artifact
  writers (`exact_artifacts.write_brep`) are handed `.wrapped`.
- **Patch targets moved to the defining module:**
  `machinome.test.intersect_shapes` → `machinome.occt.engine.intersect_shapes`
  (`test_exact_geometry`, `test_face_box_culling`, `test_intersection_memo`,
  `test_verdict_store`, `test_flexible_verdict_identity`,
  `test_assembly_supported`); `machinome.test.fuse_shapes` →
  `machinome.occt.engine.fuse_shapes`; the faceted kernel's refusal list
  now refuses `machinome.occt.engine.{intersect_shapes, placed_shape,
  fuse_shapes, solid_count, solid_volume}` and
  `machinome.exact_cache.{shape_identity, cached_bounding_box,
  cached_placement}`; `machinome.test.cached_face_boxes` →
  `machinome.exact_cache.cached_face_boxes`; `machinome.exact._boolean`,
  `.BRepAlgoAPI_Common`, `.BRepAlgoAPI_Section`,
  `.BRepClass3d_SolidClassifier`, `.BRep_Tool.Tolerance_s`,
  `._resolved_interior` → the same names on `machinome.occt.engine`;
  `OCP.BRepClass3d.BRepClass3d_SolidClassifier` (the guard imported it
  lazily) → `machinome.occt.engine.BRepClass3d_SolidClassifier`;
  `machinome.exact._place` (counted placements) →
  `machinome.occt.engine.placed_shape`; `cq.Shape.copy` →
  `machinome.occt.engine._copy`; `machinome.exact.cq.Vertex.makeVertex`
  (the face-distance failure) → `machinome.occt.engine._distance`;
  `machinome.exact._reset_placement_cache` →
  `machinome.exact_cache._reset_placement_cache`;
  `machinome.exact._atomic_export` →
  `machinome.exact_artifacts._atomic_export`;
  `machinome.node.fusion.placed_shape` / `.fuse_shapes` →
  `machinome.node.fusion.cached_placement` /
  `machinome.occt.engine.fuse_shapes`; the fake shapes with `exportStl`
  (`test_exact_geometry`, `test_tessellation_precision`) →
  a patched `machinome.occt.engine.write_stl`.
- **The guard's mutation tests** (`test_face_box_culling.py`) reimplement
  the weakened guard over the engine's helpers (`_solids`,
  `_representative_points`, `_classified_out`) and patch
  `machinome.occt.engine.mutually_outside` in place of
  `machinome.test._mutually_outside`; they still prove the mutation
  wrongly decides empty. The vertex-less decline patches
  `machinome.occt.engine._vertices` to return none in place of a duck-typed
  `FakePlaced`, which the OCP walker cannot take.
- **`test_lazy_test_framework.py`.** The broken-install pair blocks `OCP`
  rather than `cadquery`, because the exact engine imports no CAD front
  end: using the exact path (`machinome.test._exact_engine()`) raises an
  `ImportError` naming `OCP` (was `cadquery`), and
  `machinome.exact_engine.exact_engine()` raises rather than answering
  absent (was `hasattr(machinome.test, 'intersect_shapes')`).
  `ExactNamesStayPatchable` reads the five names on `machinome.occt.engine`
  and patches them there (plus `face_bounds`, in place of a duck-typed
  `Faces()`), before and after the exact path resolved the engine. Absence
  checks of `machinome.exact` read `machinome.occt.engine`.
- **`test_node_lazy_exports.py`.** Naming `FusionNode`, `CadQueryNode`,
  `Build123dNode` or `Build123dSheetNode` no longer imports cadquery (they
  reached it only through `machinome.exact`); only `StepNode` does, and the
  test asserts exactly that. The broken-backend trio reads `StepNode` in
  place of `CadQueryNode`, the one export whose own module imports
  cadquery.
- **`test_vet_universe.py`** pins the contract deny list with the five new
  entries; the `framework_internal` vet fixture imports
  `machinome.occt.engine` in place of `machinome.exact`.

## The whole suite (task 5.2)

Run once, alone, from the worktree at 8c146a7 plus the working tree:

```
env -C <worktree> PYTHONPATH=<worktree> .venv/bin/python -m pytest -q -p no:cacheprovider
1 failed, 4228 passed, 4 skipped, 53 warnings, 3107 subtests passed in 520.56s (0:08:40)
wall time 523 s
```

The one failure was a test double this cycle had missed:
`tests/test_manifold_cache.py::ExactAssemblyBuildsNoManifoldTest::test_no_manifold_is_built_for_an_overlapping_exact_pair`
hands a CadQuery `Solid` to the exact path, and the engine's `face_bounds`
refused it (`TypeError: MapShapes_s(): incompatible function arguments`). Its
fixture now holds `.val().wrapped` like the others; the file then passed
alone (`16 passed in 2.85s`). The whole suite was not run a second time.
After the documentation edits of group 6 the documentation suites were run
alone: `test_docs_structure test_docs_exports test_frame_precision_docs
test_mate_contract_docs test_profile_documentation test_release_records
test_viewer_documentation_links test_tutorial_counter test_mates
test_machinome_identity`: `181 passed, 590 subtests passed in 60.12s`.

## 6. Validation in OpenAstroMount (task 6.4)

`projects/OpenAstroMount`, branch `exact-engine-validation` cut from
`master`.

**Before migrating**, against this worktree
(`env -C <project> PYTHONPATH=<worktree> .venv/bin/machinome test`), exit 1
in 33.9 s:

```
  File "/mnt/data/machinome-projects/OpenAstroMount/simulation/seats.py", line 14, in <module>
    from machinome.exact import intersect_shapes, placed_shape, solid_volume
ModuleNotFoundError: No module named 'machinome.exact'
```

**The migration**, commit 485dccb on that branch: the import line names
`machinome.occt.engine`, and `_world_bounds` reads
`cadquery.Shape.cast(shape).BoundingBox()`.

**After**, against this worktree: `Ran 9 tests in 565.29 seconds: 8 passed,
1 failed` (exit 1, 9 m 29 s). The failure is
`OpenAstroMountScenarioTest.test_every_instruction_reaches_its_documented_end_state`:

```
machinome.exact_engine.ExactCommonInconsistency: Exact common of housing and rolamento_uc206_valor_predeterminado_1 was empty despite a point strictly inside both native solids: (-2.0242287706088176, 265.5583117280026, 442.97547336608244). No overlap volume was inferred.
```

**It is the project's, not this change's.** The project's `master` was run
against the unmodified framework (`git archive feb23f2 machinome` extracted
to a scratch directory and put first on `PYTHONPATH`; no worktree): `Ran 9
tests in 580.98 seconds: 8 passed, 1 failed`, the same test raising
`machinome.exact.ExactCommonInconsistency` with the same pair and the same
witness point to the last digit. The source-overlap inventory test, which
exercises the migrated `seats.py` (`intersect_shapes`, `placed_shape`,
`solid_volume`, `BoundingBox`), passes both before and after. The branch is
left checked out with the migration committed.

## 7. ADRs, specs and archive

ADR-160 (`docs/adrs/OCCT/`, a new category directory), ADR-161 and ADR-162
(`docs/adrs/NODE/`); ADR-047 marked with its chosen option superseded by
ADR-160; all three in `docs/adrs/README.md`.

Before the archive:

```
openspec validate exact-engine --strict
Change 'exact-engine' is valid
```

The delta specs were merged into `openspec/specs/` (`cli-startup-cost`,
`exact-geometry`, `test-framework` and `vet` modified; `exact-engine-dependency`
and `occt-engine` created), each main spec then valid under
`openspec validate <spec> --type spec --strict`, and the change was moved to
`openspec/changes/archive/2026-10-03-exact-engine/`.
