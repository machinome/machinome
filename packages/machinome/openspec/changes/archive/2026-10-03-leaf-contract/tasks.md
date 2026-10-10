## 1. Baseline on the unmodified tree

- [x] 1.1 Run `tests/exact_engine_golden.py --check` on the unmodified bench and
  record the result in the cycle's evidence file
  (`openspec/changes/leaf-contract/evidence.md`); it must pass before and after
  (the pin that no exact artifact's bytes change).
- [x] 1.2 Write `tests/leaf_contract_golden.py`, a characterization script in
  the shape of `exact_engine_golden.py`, that builds in a temporary build
  directory: an `StlNode` from an existing STL fixture, a `Build123dSheetNode`
  panel (its `.dxf`), a `MolejoNode` snapshot at one binding, a `Solid2Node`,
  an `OpenScadNode` and a `JScadNode` if `jscad` is on the PATH (record when
  it is not). For each artifact it records the SHA-256 of the bytes, the
  recorded digest and record version from the source record, whether the
  recorded fingerprint equals the node's `source_fingerprint` in the same run,
  and the node's `uniq_id`; it writes `tests/data/leaf_contract_golden.json`
  with the bench commit. Run it twice in separate processes, record that both
  agree. Green before and after by design.
- [x] 1.3 Record in the evidence the probe of design.md Decision 3 (equal
  float-mtime keys and unequal observations for a replacement under the same
  stamp; 0 equal of 200 pairs on virtiofs; the in-place `copy2` case; the
  3.4 µs and 128.8 µs costs), re-run in the bench from a script under
  `openspec/changes/leaf-contract/` and removed afterwards.

## 2. Red tests

- [x] 2.1 The stand-in exact leaf, outside the adapters:
  `tests/contract_package/` (a directory outside `machinome/`, imported by the
  tests as a package) holds `exact_stand_in.py` with `NativeSolid(ExactLeafNode)`
  declaring `leaf_contract = 1`, no `namespace`, a `source_recipe` read from a
  module-level variable, and a `render()` that reads BREP bytes with
  `BRepTools.Read_s` into a bare `TopoDS_Shape`, exactly as machinome-freecad
  does; and a project fusing it with a `CadQueryNode` leaf and comparing them
  by an exact assertion. `tests/test_leaf_contract_exact.py` builds and tests
  it in a subprocess and asserts: the `.brep`/`.stl` and the fusion are
  written; the verdict is reached; `cadquery` is not imported by the stand-in
  module; `isinstance` distinctness against `CadQueryNode` and `Build123dNode`
  (the node-model scenario); changing the module variable (the recipe) alone
  makes `_up_to_date` false for both artifacts and a rebuild records the new
  digest; and an `NativeSolid` variant rendering an `int` is refused naming
  the node and `int`. Red: `source_recipe` has no effect and the refusal names
  only the type; the rest is a characterization, green before.
- [x] 2.2 The stand-in faceted leaf: `tests/contract_package/faceted_stand_in.py`
  with `MeshPart(ExternalSourceIdentity, LeafNode)` declaring `leaf_contract
  = 1`, a `mesh_source` file resolved and checked with `require_source_file`
  before `super().__init__`, `get_source_file()` returning it, `render()`
  returning self, and `materialize()` calling
  `self.publish_artifact(self.stl_file, write)` with `write` exporting the
  mesh with trimesh; no `as_scad`. `tests/test_leaf_contract_faceted.py`:
  a project of it builds with no `openscad` on the PATH, the STL and its record
  are written, a second build in a fresh process does not call `write` (a
  counter file), `assemble()` presents the artifact, and
  `assertNotIntersecting` decides on it. Red: `publish_artifact` and
  `ExternalSourceIdentity` do not exist.
- [x] 2.3 Replacement under an unchanged mtime, `tests/test_shape_cache_observation.py`:
  (a) `write_brep(box1, path, stamp)`, `cached_shape(path)`, then
  `write_brep(box2, path, stamp)` with the same stamp: the second
  `cached_shape(path)` has box2's volume (through
  `machinome.occt.engine.solid_volume`), and the old entry's bounds, face boxes
  and placements are gone; (b) the node-level form: an exact stand-in whose
  `source_recipe` changes between two constructions in one process, built,
  `shape()` read, rebuilt, `shape()` read again, returns the new geometry
  with no eviction call; (c) a repeated `cached_shape` with nothing replaced
  returns the same object without calling `engine.read_brep` (patched
  counter); (d) `shape_load_observation(shape_identity(shape))` is the
  `observe_artifact` of the file. Red: (a) and (b) return the stale shape.
- [x] 2.4 Agreement, `tests/test_leaf_contract_members.py`: for each of the
  four bases, parse the "Declared members:" line of its docstring; assert the
  set equals the members the `leaf-contract` spec's first requirement lists
  for that base (read from `openspec/specs/leaf-contract/spec.md` when it
  exists, else from this change's delta), that each exists on the base or, for
  the instance attributes the spec names, on an instance of a stand-in of
  that base, that none begins with an
  underscore, that no base's docstring says "framework-internal", and that
  `docs/reference/api.rst` documents each member. Red: the docstrings say
  "framework-internal" and carry no such line; the sheet and flexible hooks
  are underscored.
- [x] 2.5 Versioning, `tests/test_leaf_contract_version.py`:
  `machinome.node.leaf.CONTRACT == 1` and is an integer literal in the source
  (AST); a class declaring `leaf_contract = 1` is created; declaring `2`, `'1'`
  or `True` raises `TypeError` naming the class, the declared value, `1` and
  `machinome.node.leaf`, on `LeafNode`, `ExactLeafNode`, `SheetLeafNode` and
  `FlexibleNode` subclasses; a subclass without a declaration (including a
  subclass of a declaring class, and a `CadQueryNode` subclass) is created
  unchecked. Red: no `CONTRACT`, no check.
- [x] 2.6 No private reach, `tests/test_leaf_contract_reach.py`: an AST scan of
  `tests/contract_package/*.py` and of `node/adapters/{cadquery,build123d,
  build123d_sheet,step,molejo}.py` (the leaves that leave at the cut) finds no
  import of a name beginning with an underscore from `machinome`, no import of
  `machinome.currency`, `machinome.exact_cache`, `machinome.exact_artifacts`
  or `machinome._artifact`, no definition of a method whose name begins with an
  underscore and is defined on any of the four bases or `AbstractBaseNode`, and
  no `self._<name>` read of such a member. Allowed exceptions, listed in the
  test with their reason: `step.py`'s import of `workplane_shape` (Deferred),
  `cadquery.py`'s `NodeMeta` (declared). Red: `build123d_sheet.py` imports
  `_atomic_export`, `step.py` imports `_ExternalWrapperIdentity`, `molejo.py`
  defines five underscore hooks.
- [x] 2.7 `publish_artifact`, in `tests/test_leaf_contract_faceted.py`: the four
  scenarios of the spec's "A leaf publishes an artifact through one call"
  (stale written and recorded; current not rewritten, observation unchanged,
  false returned; failing writer publishes nothing and leaves no temporary
  file; a path outside `basepath` refused before `write`). Red: no method.
- [x] 2.8 `source_recipe` reaches every artifact: a `Solid2Node` stand-in and an
  exact stand-in with a marking, each declaring a recipe, record digests that
  differ from the same nodes with `None`; with `None` the records equal those
  of the unmodified tree (1.2's JSON). Red: no effect.
- [x] 2.9 Run 2.1 to 2.8 on the unmodified tree; record each failure and its
  reason in the evidence.

## 3. The contract in the bases

- [x] 3.1 `machinome/node/leaf.py`: `CONTRACT = 1`; `LeafNode.__init_subclass__`
  checking an own-body `leaf_contract` (design.md Decision 9), calling super;
  `publish_artifact(path, write)` (Decision 5) built on the core's existing
  temporary-file, stamp and `currency.publish` sequence with the node's
  `mtime_ns`, `source_digest` and `source_fingerprint`; docstring with
  "Declared members:" and the spec's name.
- [x] 3.2 `machinome/node/base.py`: `source_recipe = None` on
  `AbstractBaseNode`, documented; `_tracked_digest` and `_tracked_fingerprint`
  fold a non-`None` recipe into a non-`None` result and return today's value
  otherwise (Decision 6).
- [x] 3.3 `machinome/node/exact_leaf.py`: docstring (declared, members, spec);
  the core's two calls of `shape_from_rendered` re-raise a `TypeError` naming
  the node and the result's type; nothing else changes in `materialize`.
- [x] 3.4 `machinome/node/sources.py`: rename `_ExternalWrapperIdentity` to
  `ExternalSourceIdentity` (no alias); repoint `stl.py`, `step.py`,
  `openscad.py`, `jscad.py` and the tests that name it.
- [x] 3.5 `machinome/node/sheet_leaf.py` and `node/adapters/build123d_sheet.py`:
  the four hooks public; `write_dxf(face, path)` writes to `path`; the base
  publishes the DXF with `publish_artifact(self.dxf_file, ...)`;
  `build123d_sheet` no longer imports `exact_artifacts`; docstrings.
- [x] 3.6 `machinome/node/flexible.py`, `node/adapters/molejo.py`,
  `machinome/test.py`: the five hooks public; the snapshot written with
  `publish_artifact`; docstrings.
- [x] 3.7 `node/adapters/stl.py`: materialize through `publish_artifact`;
  `_write_binary_stl` removed; `as_scad` calls `materialize` and imports the
  artifact. `JScadNode` keeps its own publication (Decision 5).
- [x] 3.8 Run 2.1, 2.2, 2.4, 2.5, 2.6, 2.7, 2.8 green.

## 4. The shape cache on the observation

- [x] 4.1 `machinome/exact_cache.py`: `cached_shape` keys on `(path, (st_dev,
  st_ino, st_size, st_mtime_ns, st_ctime_ns))` from one `os.stat`; on a miss,
  `_evict(path)`, observe, read through the engine, observe, record the load
  observation when the two agree (design.md Decision 3); module and function
  docstrings say observation, not mtime; `_evict` stays private.
- [x] 4.2 `node/adapters/step.py`: the two comments naming the cache's shape.
- [x] 4.3 Run 2.3 green; run the existing cache suites
  (`test_exact_geometry.py`, `test_face_box_culling.py`,
  `test_exact_placement_cache.py`, `test_intersection_memo.py`,
  `test_verdict_store.py`, `test_persistent_piece_facts.py`).

## 5. Existing tests repointed

- [x] 5.1 Repoint the tests that name a renamed member without changing any
  asserted value, verdict or message: `_ExternalWrapperIdentity`
  (`test_external_wrapper_identity.py`, `test_external_wrapper_review.py`),
  the sheet hooks (`test_sheet_leaf.py`), the flexible hooks
  (`test_flexible_node.py`, `test_molejo_adapter.py`,
  `test_flexible_cache_performance.py`, `test_flexible_verdict_identity.py`,
  `test_flexible_document.py`), and any other found by grep.
- [x] 5.2 The two assertions of the old key form `(path, 2.0)`
  (`test_exact_geometry.py` `test_shape_cache_evicts_the_previous_mtime`,
  `test_exact_placement_cache.py` / `test_exact_geometry.py`
  `test_a_rebuilt_shape_is_never_served_the_old_placement`) assert the
  surviving key's path and `st_mtime_ns == 2 * 10**9` instead; list every
  repointed assertion and why in the evidence.
- [x] 5.3 Run `tests/exact_engine_golden.py --check` and
  `tests/leaf_contract_golden.py --check`: every digest, record and `uniq_id`
  equal.
- [x] 5.4 Run the whole suite once, alone (it shares `tests/_build`; never two
  runs at once), and record the counts and wall time.

## 6. Documentation

- [x] 6.1 Read the workspace's `skills/write-the-manual/SKILL.md`, then update
  `docs/reference/api.rst` "Leaf nodes": a paragraph naming the declared leaf
  contract, its version `machinome.node.leaf.CONTRACT` and `leaf_contract`;
  autodoc entries for the declared members of `LeafNode`, `ExactLeafNode`,
  `SheetLeafNode` (with its public hooks) and `FlexibleNode` (with its public
  hooks), and `source_recipe`. Write no how-to page (design.md Decision 10).
- [x] 6.2 `docs/architecture.md`: the leaf-adapter paragraph (declared
  extension points, the contract version), the exact-layer cache key
  (observation), and the source map rows if they name a renamed member.
- [x] 6.3 The changelog: one bullet in `docs/project/changelog.rst`'s existing
  Unreleased section naming the declared leaf contract and its version, the
  four bases, `publish_artifact`, `source_recipe`, `ExternalSourceIdentity`,
  the renamed sheet and flexible hooks (BREAKING for subclasses of those two
  bases), the shape cache keyed on the artifact's observation, and the
  originating adapter. Not in `HISTORY.rst`.

## 7. Implementation commit

- [x] 7.1 Fill the evidence with every red and green result above, then make
  the implementation commit on `v0.8-leaf-contract` (the orchestrator's
  review precedes integration).

## 8. Deep validation: machinome-freecad, by a validator subagent

- [x] 8.1 Before the implementation commit, delegate to a fresh validator
  subagent, briefed in writing (the applier does not migrate it), with: the
  bench path; the repository `/home/asa/devel/machinome/machinome-freecad`;
  the evidence file; and this brief.
  - *Where.* A branch `lean-core-validation` of machinome-freecad, from its
    `main`, in a worktree under its own `WTs/`; never merged, never pushed.
    Run its suite against the bench with `PYTHONPATH=<bench>` and the
    workspace venv, and its documented FreeCAD runtime
    (`MACHINOME_FREECAD_ROOT`, `docs/runtime.md`); if the runtime is absent,
    record exactly which tests could not run and why.
  - *Before.* Run the suite unchanged against the bench; record pass, fail
    and error counts and each failure's first line (expected: the removed
    `machinome.exact._evict`, and CadQuery methods called on `shape()`).
  - *Change, and only this:* (1) relax `machinome==0.7.1` in `pyproject.toml`
    and remove the `version('machinome') != '0.7.1'` refusal in
    `FreeCADAssemblyNode.__init__`; (2) on `_Solid` declare `leaf_contract =
    1` and no `namespace`; `render()` returns the bare `TopoDS_Shape`, with
    the no-solid / invalid check done by `machinome.occt.engine.solid_count`
    and OCP's `BRepCheck_Analyzer(shape).IsValid()` (what CadQuery's
    `isValid` calls), and imports no cadquery; (3) in `_Solid.materialize`
    remove both `_evict` imports and calls and the `replaced` computation that
    served only them; keep the backup and restore unchanged; (4) replace
    `_NativeCurrency`'s `_tracked_fingerprint` and `_tracked_digest` overrides
    with one `source_recipe` property that calls
    `self._check_native_generation()` and returns `self._native_recipe` or
    `None` when it has none; (5) in the tests, wrap `shape()` results whose
    CadQuery methods are called in `cadquery.Shape.cast(...)`, changing no
    asserted value.
  - *Must not change:* native resolution, snapshots, joints, aliases, product
    keys and `uniq_id`s, the rollback behaviour, any test's asserted value or
    expected exception, and anything in the bench or in machinome.
  - *Record:* the after-run counts and failures; the diff stat; every member
    `_Solid` and the mixin still override or reach that the `leaf-contract`
    spec does not declare (expected: the rollback's `currency.sidecar`, and on
    the assembly side `_link_children` and `track_sources`), each with its
    reason; and whether `cadquery` is imported by `machinome_freecad` at the
    end of a build (it should not be).
  A failed validation goes back to the orchestrator with the output; nothing
  is fixed in the adapter beyond the list above.
- [x] 8.2 Fold the validator's report into the evidence before 7.1, and check
  the `leaf-contract` scenario "The FreeCAD stand-in overrides only declared
  members" against it.

## 9. Shallow validation: the universe loaded

- [x] 9.1 After the implementation commit and before the orchestrator's
  review, run the workspace's universe-loading script (cut in its own
  workspace cycle; the orchestrator gives its name and invocation in the
  applier's brief) against this bench, one project at a time.
- [x] 9.2 Classify every failure. Expected, from this cycle: a project that
  names `machinome.node.sources._ExternalWrapperIdentity`, a `SheetLeafNode`
  hook (`_profile_faces`, `_lies_on_xy_plane`, `_extrude`, `_write_dxf`), a
  `FlexibleNode` hook (`_shape_parameters`, `_shape_spec`, `_snapshot_mesh`,
  `_snapshot_stl`, `_snapshot_shape`), the old `(path, mtime)` shape-cache key,
  or declares an attribute shadowing one of the nine newly public hook names;
  none is expected, by grep. Expected, from the campaign line before this
  cycle: imports of the removed `machinome.exact` (Curta-Type-I-3x, 11 files;
  OpenAstroMount, 1). Anything else is unexpected and returns to the
  orchestrator with the project's output before integration. The report goes
  in the evidence.

## 10. ADRs, specs, plan

- [x] 10.1 Write the ADRs the pilot ratified from design.md's "ADRs":
  ADR-163 (the declared leaf bases), ADR-164 (the shape cache on the
  artifact's observation, amending ADR-044), ADR-165 (the leaf contract
  version on the class); mark ADR-047, ADR-053 and ADR-057's
  "framework-internal" sentences superseded in part and ADR-044 amended; add
  all to `docs/adrs/README.md`.
- [x] 10.2 Amend the campaign plan `workflow/ongoing/lean-core.md`, and nothing
  else in it: "What it takes" item 1 and "machinome, the core" name the four
  declared bases (not two) and the contract version; the "Import paths" table
  row for `ExactLeafNode` names the other three bases beside it; the
  "Empirical validation" table's leaf-contract row is marked done with the
  evidence path once 8 and 9 have run.
- [x] 10.3 Sync the delta specs into `openspec/specs/` (the new `leaf-contract`,
  the `exact-geometry` and `node-model` deltas), confirm 2.4 still passes
  against the synced spec, and archive the change.
