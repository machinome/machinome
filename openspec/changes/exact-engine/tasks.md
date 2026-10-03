## 1. Baseline on the unmodified tree

- [ ] 1.1 Before any source change, write `tests/exact_engine_golden.py`, a
  script that builds the fixtures below in a temporary build directory with
  the current code and writes `tests/data/exact_engine_golden.json`: for each
  fixture the SHA-256 of its `.brep` and `.stl`, its volume and solid count
  (through today's `machinome.exact`), its optimal bounding box and the SHA-256
  of its `cached_face_boxes` array. Fixtures: a CadQuery box less a bore; the
  same part in build123d; a `Build123dSheetNode` panel; a `StepNode` product
  from an existing test document; an exact `FusionNode` fusing a shaft into a
  bore of equal diameter; a fusion mixing a CadQuery and a build123d child; a
  `MolejoNode` spring at one binding (its `shape()` written with
  `BRepTools.Write_s`, since it has no `.brep`). Run it twice in separate
  processes and record that both runs agree; record the bench commit in the
  JSON. This is a characterization baseline, green before and after by design;
  after the change the script reads the same measurements through
  `machinome.occt.engine` and `machinome.exact_cache`.
- [ ] 1.2 Record in the planning evidence the probe of design.md Decision 4
  (CadQuery's exporters and the raw OCP calls give the same bytes), the
  project counts of the proposal's Impact (12 importers re-checked; 29 files
  as measured by the orchestrator), and the cadquery-ocp range cadquery 2.7
  requires.

## 2. Red tests

- [ ] 2.1 `tests/test_exact_engine_seam.py`: the provider resolves and
  declares `CONTRACT == machinome.exact_engine.CONTRACT`; it carries every
  member of `ExactEngine`, each a function defined in `machinome.occt.engine`
  (`__module__` is that module); with `sys.modules['machinome.occt.engine'] =
  None` and the cache cleared, `exact_engine()` is `None` and
  `require_exact_engine('exact fusion Bracket', 'fusing its exact children')`
  raises naming both arguments, the exact engine and `pip install
  "machinome[occt]"`; a stub provider declaring `CONTRACT = 2`, and one
  declaring none, are refused by both functions naming 1, 2 (or "none") and
  `machinome.occt.engine`; a stub whose import raises `ImportError` from
  inside surfaces that error, not `None`; resolution happens once per process;
  the package metadata declares an `occt` extra. Red: the module does not
  exist and no `occt` extra is declared.
- [ ] 2.2 `tests/exact_engine_absent.py` (the shape of
  `tests/mesh_engine_absent.py`, a `sys.meta_path` finder refusing
  `machinome.occt`) and subprocess tests:
  - importing `machinome.node.fusion`, `machinome.node.exact_leaf`,
    `machinome.exact_cache`, `machinome.exact_artifacts` and `machinome.test`
    leaves `machinome.occt.engine`, `OCP` and `cadquery` out of
    `sys.modules`;
  - with the engine blocked, `machinome test` on an existing all-faceted
    meta-project fixture passes as it does unblocked;
  - with the engine blocked, building an exact fusion whose artifacts are
    stale fails naming the install;
  - "A current exact fusion does not resolve the engine": build an exact
    fusion fixture, one of whose leaves declares `optimize = False`, once
    unblocked, then build it again in a fresh process with the engine
    blocked; the second build succeeds, the fusion's and its leaves' `.brep`
    and `.stl` keep their artifact observations (inode, mtime_ns, ctime_ns),
    and `machinome.occt.engine` is absent from `sys.modules` at exit. If the
    code cannot keep this promise (some build path reaches an exact operation
    for current artifacts), stop and return the evidence, the call stack
    included, to the orchestrator rather than weaken the spec.

  Red: `node/fusion.py` imports `machinome.exact`, hence cadquery and OCP, at
  module top, so the import and blocked-engine checks fail. The current-fusion
  case cannot be red on the unmodified tree, which has no engine to resolve:
  record it as a guard, and prove it can fail by running it once against the
  rewritten tree with `ExactLeafNode.materialize` converting before its
  currency checks (design.md Decision 7's finding), then restoring the order.
- [ ] 2.3 The originating caller's stand-in: a meta-project
  `tests/meta_project/occt_only.py` with two `ExactLeafNode` subclasses
  declaring `namespace = 'OCP'` whose `render()` returns a bare
  `TopoDS_Shape` (one read from BREP bytes with `BRepTools.Read_s`, exactly as
  machinome-freecad's `render()` does before its cast, one from
  `BRepPrimAPI_MakeBox`), fused in an exact `FusionNode` and compared by
  `assertIntersectVolumeAbove` and `assertNotIntersecting`. A subprocess test
  builds and tests it and asserts the verdicts, the written `.brep`/`.stl`,
  and that `cadquery` and `build123d` are absent from `sys.modules` at exit.
  Red: today a bare render reaches `shape.exportBrep` and fails.
- [ ] 2.4 `tests/test_occt_engine.py`: a fresh interpreter imports
  `machinome.occt.engine` and runs every contract operation on a box and a
  cylinder made with `BRepPrimAPI` (read and write BREP, write STL,
  `placed_shape` by a 4×4 matrix, `fuse_shapes`, `intersect_shapes` with an
  overlap and a disjoint pair, `solid_count`, `solid_volume`, `bounds`,
  `face_bounds`, `mutually_outside` for a disjoint and a contained pair,
  `compound`, `as_shape` on a bare shape, on a `.wrapped` carrier and on an
  `int`); results are `TopoDS_Shape`s or numbers; `cadquery`, `build123d` and
  `trimesh` are absent afterwards; `machinome.occt` has no attribute
  `intersect_shapes`; `CONTRACT` is an integer literal in the source. Red: the
  module does not exist.
- [ ] 2.5 The currency: `shape()` of a `CadQueryNode`, `Build123dNode`,
  `Build123dSheetNode`, `StepNode`, `MolejoNode` at a binding and an exact
  `FusionNode` is an `OCP.TopoDS.TopoDS_Shape` and not a CadQuery or build123d
  object; `cadquery.Shape.cast(shape).Volume()` equals the golden volume;
  `machinome.occt.engine.solid_volume` accepts a CadQuery `Shape`; a two-solid
  `Workplane` becomes one compound. Red: today `shape()` is a CadQuery `Shape`.
- [ ] 2.6 The core holds no kernel code: an AST scan of `machinome/` finds
  `machinome.occt` imported only in `machinome/exact_engine.py`; `OCP` or
  `cadquery` imported nowhere outside `machinome/occt/` except
  `node/adapters/step.py` (its reader and `adjust`, deferred); no module named
  `machinome/exact.py`; and `machinome.test` has none of the attributes
  `intersect_shapes`, `fuse_shapes`, `placed_shape`, `solid_count`,
  `solid_volume`, `cached_bounding_box`, `cached_face_boxes`,
  `shape_identity`, `shape_load_observation`. Red: `exact.py` exists and it
  and `test.py` import OCP.
- [ ] 2.7 Vet: in the existing vet suite, a vetted module that runs `from
  machinome.occt.engine import write_brep`, one that names
  `machinome.exact_cache.cached_shape`, and one that imports
  `machinome.exact_artifacts` are each reported `framework-internal` naming
  the denied name; one that runs `from machinome.occt.engine import
  intersect_shapes, placed_shape, solid_volume` and one that imports
  `ExactCommonInconsistency` from `machinome.exact_engine` report nothing
  (design.md Decision 14). Red: none of the five names is in the contract
  deny list.
- [ ] 2.8 Run 2.1 to 2.7 on the unmodified tree, record each failure and its
  reason in the cycle's evidence.

## 3. The seam and the engine

- [ ] 3.1 Write `machinome/exact_engine.py`: `CONTRACT`, the three component
  Protocols and `ExactEngine` with the engine's operation names, the opaque
  `ExactShape` alias, the four error types, `exact_engine()`,
  `require_exact_engine()` (design.md Decisions 1, 5, 6).
- [ ] 3.2 Write `machinome/occt/__init__.py` (exports nothing) and
  `machinome/occt/engine.py`: `CONTRACT = 1` as a literal and the 13
  operations under the names of Decision 5, each defined once, porting
  `_boolean`, `_false_empty_witness`, `_resolved_interior`, `_place` (as
  `placed_shape(shape, matrix)`, uncached), the face boxes, the containment
  guard from `test.py` (`_mutually_outside` as `mutually_outside`,
  `_representative_points`, `_classified_out`) and the readers and writers to
  bare OCP by the table of Decision 4. The five project-facing operations
  accept what `as_shape` admits. No cadquery, build123d, trimesh,
  `machinome.currency`, `machinome._artifact` or cache import; no module state.
- [ ] 3.3 Declare `occt = ["cadquery-ocp>=7.8.1,<7.9"]` under
  `[project.optional-dependencies]` in `pyproject.toml`, with a comment that
  the range is what the pinned cadquery 2.7 already requires and that the cut
  repoints the extra at machinome-occt. Change no required dependency.
- [ ] 3.4 Run 2.1 and 2.4 green.

## 4. The core's exact path over the seam

- [ ] 4.1 Write `machinome/exact_cache.py` from `exact.py`'s caches,
  unchanged in keys, limits and semantics, resolving the engine on a miss and
  calling `read_brep`, `bounds`, `face_bounds` and `placed_shape`;
  `cached_bounding_box` returns `((xmin, ymin, zmin), (xmax, ymax, zmax))`;
  the placement memo is `cached_placement(shape, matrix)` (design.md
  Decision 9). Keep `_evict` and `_reset_placement_cache` private.
- [ ] 4.2 Write `machinome/exact_artifacts.py`: `_atomic_export`,
  `write_brep` (engine `write_brep` to the temporary path), `write_stl`
  (engine `write_stl` to the temporary path, then the trimesh cleanup),
  `deflections`.
- [ ] 4.3 Delete `machinome/exact.py`.
- [ ] 4.4 `node/exact_leaf.py`: imports from `exact_cache` and
  `exact_artifacts`; `shape_from_rendered` becomes a method whose default is
  `require_exact_engine(...).as_shape`; `materialize` converts only inside the
  branch that writes, after the `_up_to_date` checks (design.md Decision 7);
  correct the docstring's import-cost paragraph.
- [ ] 4.5 `node/adapters/cadquery.py`: `workplane_shape(rendered, engine)` and
  the `CadQueryNode` override. `node/adapters/build123d.py`: `build123d_shape`
  moves here returning `.wrapped`; validation counts solids through the
  engine. `node/adapters/step.py`: the `StepNode` override through
  `workplane_shape`; `adjust` still receives `cq.Shape.cast(...)`.
  `node/adapters/molejo.py`: return `result.solid`, drop `import cadquery`.
  `node/adapters/build123d_sheet.py`: `_atomic_export` from `exact_artifacts`.
- [ ] 4.6 `node/fusion.py`: kernel-free imports at module top; resolve the
  engine inside the exact branch with `needed_by=f'exact fusion {self.name}'`
  after the currency checks; place with `exact_cache.cached_placement` and fuse
  with `engine.fuse_shapes`; keep `exact-fusion-occt-v1`; leave
  `_generate_faceted_stl` alone.
- [ ] 4.7 `test.py`: remove `_deferred_exact` and the nine module-level
  names; call memos as attributes of `machinome.exact_cache` and operations as
  attributes of the resolved engine, at call time (design.md Decision 8);
  remove `_mutually_outside`, `_representative_points` and `_classified_out`,
  `_faces_disjoint` calling `engine.mutually_outside`; the AABB cull reads
  tuple bounds; `assertJoined` and the solid-count assertion go through
  `cached_placement` and the engine; the exact branch resolves the engine
  naming the assertion. `manager/test.py`: import `exact_cache` and reset its
  placement cache directly.
- [ ] 4.8 Correct the docstrings and comments that describe the old layer:
  `node/__init__.py`, `core/loader.py`, `simulation/__init__.py`,
  `node/adapters/{step,stl,build123d,build123d_sheet}.py`, `test.py`'s
  face-box tier comment.
- [ ] 4.9 Run 2.2, 2.3, 2.5 and 2.6 green; run the golden comparison of 1.1
  against the rewritten tree: every digest and measurement equal.
- [ ] 4.10 `machinome/vet/universe.toml`: add `machinome.exact_cache`,
  `machinome.exact_artifacts`, `machinome.occt.engine.read_brep`,
  `machinome.occt.engine.write_brep` and `machinome.occt.engine.write_stl` to
  the contract deny list, with the comment explaining the kind; run 2.7
  green.

## 5. Existing tests repointed

- [ ] 5.1 Repoint the suites that name moved internals, patch exact names on
  `machinome.test`, or expect the old type, without changing any asserted
  verdict, volume or message: `exact_test_support.py`, `conftest.py`,
  `test_exact_geometry.py`, `test_exact_placement_cache.py`,
  `test_exact_test_isolation.py`, `test_face_box_culling.py`,
  `test_exact_common_guard.py`, `test_resolved_exact_witness.py`,
  `test_exact_input_copies.py`, `test_intersection_memo.py`,
  `test_verdict_store.py`, `test_persistent_piece_facts.py`,
  `test_tessellation_precision.py`, `test_build123d_adapter.py`,
  `test_molejo_adapter.py`, `test_step_node.py`, `test_sheet_leaf.py`,
  `test_lazy_test_framework.py`, `test_node_lazy_exports.py`,
  `test_external_wrapper_identity.py`, `test_retained_builder_generation.py`,
  `test_assembly_supported.py`, `test_flexible_verdict_identity.py`. A patch
  of an engine operation targets `machinome.occt.engine`; a patch of a memo
  targets `machinome.exact_cache`. List in the evidence every assertion whose
  expected type or patch target changed, and why.
- [ ] 5.2 Run the whole suite once, alone (it shares `tests/_build`), and
  record the counts and wall time.

## 6. Documentation, plan and validation

- [ ] 6.1 `docs/architecture.md`: the exact-layer and test-kernel paragraphs,
  the seam, the core's opaque handles, the engine package, the module split,
  the currency, and the source map rows that name `machinome/exact.py`.
  `docs/reference/assertions.rst`: the direct comparison is
  `machinome.occt.engine.intersect_shapes(first, second, first_name,
  second_name)` (the page shows two arguments today; the function has always
  taken four), it takes and returns the engine's currency, and the error types
  live in `machinome.exact_engine`. The how-to pages that say "the OCCT solid"
  stay true; check them.
- [ ] 6.2 The changelog entry, one bullet in `docs/project/changelog.rst`'s
  existing Unreleased section, naming the change, the removal of
  `machinome.exact` and the new address of its operations, the currency
  (`cadquery.Shape.cast(node.shape())` for CadQuery's methods), the `occt`
  extra and the originating adapter. Not in `HISTORY.rst`: its top section is
  the released 0.7.1 and `tests/test_release_records.py` and
  `tests/test_profile_documentation.py` forbid "unreleased" above it.
- [ ] 6.3 Amend the campaign plan `workflow/ongoing/lean-core.md` in the
  implementation commit, and nothing else in it: the "machinome-occt,
  LGPL-2.1" section and the "Import paths" table gain the project-facing exact
  operations that used to be `machinome.exact` (`intersect_shapes`,
  `fuse_shapes`, `placed_shape`, `solid_count`, `solid_volume`, at
  `machinome.occt.engine`); the "Sequencing" section records that the engine
  cycle runs before the leaf-contract cycle because that contract names the
  engine's currency, and that the markings reducer waits for the cut.
- [ ] 6.4 Validate in OpenAstroMount, on a branch of that project's own
  repository: run its tests against this bench before migrating (expect the
  import of `machinome.exact` to fail), then move the three imports of
  `simulation/seats.py` (`intersect_shapes`, `placed_shape`, `solid_volume`)
  to `machinome.occt.engine` and wrap its one `shape.BoundingBox()` call with
  `cadquery.Shape.cast(...)`, run them again, and record both results.

## 7. ADRs, after implementation

- [ ] 7.1 Write the ADRs the pilot ratified from design.md's "ADRs": ADR-160
  (the engine's currency, under the engine's own ADR directory,
  `docs/adrs/OCCT/`, superseding ADR-047's chosen option and noting ADR-057's
  recast sentence as historical), ADR-161 (the core holds no kernel code; the
  seam and its address), ADR-162 (the contract declaration); mark ADR-047
  accordingly, and add them to `docs/adrs/README.md`.
- [ ] 7.2 Sync the delta specs into `openspec/specs/` (the new `occt-engine`
  and `exact-engine-dependency`, and the `exact-geometry`, `cli-startup-cost`,
  `test-framework` and `vet` deltas) and archive the change.
