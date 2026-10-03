# Evidence — `leaf-contract`

The second cycle of the lean-core campaign (`workflow/ongoing/lean-core.md`,
item 1 of "What it takes"). Worktree `machinome/WTs/v0.8-leaf-contract`,
branch `v0.8-leaf-contract`, cut from `v0.8` at 5c163ea. Planning commit
159cf78. Every command below ran from inside the worktree with
`PYTHONPATH=<worktree>` and the workspace venv; `machinome.__file__`
resolved to `<worktree>/machinome/__init__.py`. Pytest ran one process at a
time, never in parallel.

## 1. Baseline on the unmodified tree

### 1.1 The first cycle's golden pin

```
env -C <worktree> PYTHONPATH=<worktree> .venv/bin/python tests/exact_engine_golden.py --check
golden comparison: 7 fixtures, 0 differences
```

### 1.2 The leaf-contract golden

`tests/leaf_contract_golden.py` was written before any source change. Its
fixtures live in project packages, never in the script, so no digest
depends on the script's own bytes: `tests/markings_project/plate.py`
`Plate` (an `StlNode` wearing two markings), `tests/markings_project/dial.py`
`Dial` (a `CadQueryNode` wearing one, the exact leaf with a marking),
`tests/sheet_project/frame_panel.py` `FramePanel` (a `Build123dSheetNode`),
`tests/flexible_project/spring.py` `Valvetrain` at `lift=4.0` (the
`MolejoNode` snapshot), and a new fixture package
`tests/leaf_contract_project/` holding `Washer` (`Solid2Node`), `Block`
(`OpenScadNode`, `block.scad`) and `JsBlock` (`JScadNode`, `block.js`).
For every artifact a node owns it records the SHA-256 of the bytes, the
record version and digest of the source record, whether the recorded
fingerprint equals the node's fingerprint over the artifact's tracked set
in the same run, and whether the stamp equals the node's mtime over that
set; for every node its `uniq_id`.

`jscad` is not on the PATH of this machine, so the `JScadNode` row records
`skipped: jscad is not on the PATH`; `JScadNode`'s publication is unchanged
by design (Decision 5) and its identity is covered by
`tests/test_external_wrapper_identity.py`.

**One departure in what is digested.** The DXF's bytes are not
reproducible: ezdxf 1.4.4 writes `$TDCREATE`/`$TDUPDATE` from the clock,
two fresh GUIDs, `1.4.4 @ <UTC time>` writer stamps, and an OBJECTS section
whose order follows Python's hash seed (two builds of the same panel in
two processes differed on lines 1330-1348, `ACDBPLACEHOLDER` and `LAYOUT`
swapped). The golden therefore records `entities_sha256` for a `.dxf`, the
SHA-256 of its ENTITIES section (the cut geometry), which was identical in
eleven builds across processes; every other artifact is digested whole.

Three runs in three processes, then the check:

```
tests/leaf_contract_golden.py --out <scratch>/lc_run{1,2,3}.json
cmp lc_run1.json lc_run2.json && cmp lc_run1.json lc_run3.json  ->  ALL-IDENTICAL
cp lc_run1.json tests/data/leaf_contract_golden.json   (bench_commit 159cf78d9b7d)
tests/leaf_contract_golden.py --check
golden comparison: 7 fixtures, 97 values, 0 differences
```

| fixture | `uniq_id` | artifacts (SHA-256 prefix, record version) | fingerprint and stamp match |
|---|---|---|---|
| `StlNode` with markings | `__Plate_,_markings_project_plate.py__-d5c4be96a4d1` | `.stl` 2d8a0cac2bd1 v2, `.scad` 3cb65464ac26 v2, `.marking-badge.stl` ff24e82d90c2 v3, `.marking-band.stl` e492ab49a5db v3 | all |
| exact leaf with a marking | `Dial-9f2c3557d753` | `.brep` eb2077fa4d22 v2, `.stl` 62f6c453fd92 v2, `.scad` a49b98617445 v2, `.marking-digits.stl` bd3dacd344bd v3 | all |
| `Build123dSheetNode` | `FramePanel-347a8fc9fd91` | `.brep` ee623ac60579 v2, `.stl` 9dc0fb2c4877 v2, `.scad` 699283c88b79 v2, `.dxf` (entities) fab024cdfcff v2 | all |
| `MolejoNode` snapshot | `Spring-db29e82a9287` | `-741c57989c14.stl` b82876ab2a66 v2, `.scad` 34d635d11dd6 v2 | all |
| `Solid2Node` | `Washer-feb6a91bcb05` | `.scad` 9425d5158ab1 v2, `.stl` 244a20775add v2 | all |
| `OpenScadNode` | `__Block_,_leaf_contract_project_parts.py__-845ed072074a` | `.scad` aa013ab2370f v2, `.stl` f0dae9212ad2 v2 | all |
| `JScadNode` | — | skipped: `jscad` is not on the PATH | — |

### 1.3 The observation probe (design.md Decision 3)

Re-run from `openspec/changes/leaf-contract/probe_observation.py` (removed
afterwards), with the bench's own `exact_artifacts._atomic_export` and
`_artifact.observe_artifact`: two publications of 100 different bytes
stamped with the same `mtime_ns`, on the bench's virtiofs (a directory
17 components deep under the worktree) and on ext4 under `/tmp`; 200
back-to-back replacement pairs on virtiofs; and an in-place
`shutil.copy2` restore of the earlier bytes over the replacement, the
FreeCAD adapter's rollback. Two runs; the second:

```
virtiofs: float-mtime keys equal=True; observations equal=False; inode 36095599->36095600; ctime 1791025364153744100->1791025364153744100
ext4 /tmp: float-mtime keys equal=True; observations equal=False; inode 174254->174380; ctime 1791025364152789328->1791025364153789365
virtiofs: 0 equal observations of 200 replacement pairs
virtiofs: in-place copy2 restore over the replacement: observation equal=False (inode kept=True, ctime equal=False)
ext4 /tmp: in-place copy2 restore over the replacement: observation equal=True (inode kept=True, ctime equal=True)
virtiofs cost: os.path.getmtime 3.9 us; observe_artifact 194.8 us (path depth 17)
```

The first run agreed in every equality (`os.path.getmtime` 3.9 µs,
`observe_artifact` 184.2 µs). Decision 3's facts hold: equal float-mtime
keys and unequal observations for a replacement under the same stamp, on
both filesystems; 0 of 200 equal on virtiofs; the in-place `copy2` keeps
the inode, and on ext4 the ctime too, so its observation is equal. The
costs measured here are 3.9 µs and 184-195 µs a call on a 17-deep path
(design.md recorded 3.4 µs and 128.8 µs); the ratio, about 50 rather than
38, strengthens the choice of one `stat` per request.

## 2. Red first (task 2.9)

The tests of tasks 2.1 to 2.8 were written before any source change and run
on the unmodified tree (159cf78 plus the golden script, its fixture package
and these tests), in one pytest process:

```
env -C <worktree> PYTHONPATH=<worktree> .venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_leaf_contract_exact.py tests/test_leaf_contract_faceted.py \
  tests/test_shape_cache_observation.py tests/test_leaf_contract_members.py \
  tests/test_leaf_contract_version.py tests/test_leaf_contract_reach.py \
  tests/test_leaf_contract_recipe.py -rA
75 failed, 18 passed, 4 warnings, 87 subtests passed in 13.35s
```

(Counts include subtests: 15 test functions failed, some through several
subtests.) What the new files hold:

- `tests/contract_package/` (outside `machinome/`, kept from pytest
  collection by `tests/conftest.py`): `exact_stand_in.py` (`NativeSolid`,
  `leaf_contract = 1`, no `namespace`, `source_recipe` read from the
  module's `RECIPE`, `render()` reading BREP bytes with `BRepTools.Read_s`
  into a bare `TopoDS_Shape`; `IntSolid` rendering `5`),
  `exact_project.py` and its solid-runner `test_exact_project.py` (the pin
  fused with a CadQuery block, and compared by three exact assertions),
  `faceted_stand_in.py` (`MeshPart(ExternalSourceIdentity, LeafNode)`,
  `publish_artifact` in `materialize`, no `as_scad`), `faceted_project.py`
  and `test_faceted_project.py`, and `cube.stl`.
- `tests/test_leaf_contract_exact.py` (2.1), `test_leaf_contract_faceted.py`
  (2.2, 2.7), `test_shape_cache_observation.py` (2.3),
  `test_leaf_contract_members.py` (2.4), `test_leaf_contract_version.py`
  (2.5), `test_leaf_contract_reach.py` (2.6), `test_leaf_contract_recipe.py`
  (2.8).

Each failure and its reason:

| task | test | red because |
|---|---|---|
| 2.1 | `test_changing_the_recipe_alone_makes_both_artifacts_stale` | `[True, True] != [False, False]`: `source_recipe` has no effect, both artifacts stay current |
| 2.1 | `test_an_unconvertible_render_is_refused_naming_the_node` | `'IntSolid' not found in 'The OCCT exact engine takes an OCP.TopoDS.TopoDS_Shape, or an object carrying one as .wrapped, not builtins.int'`: the refusal names only the type |
| 2.2 | `test_builds_without_a_cad_tool_and_reuses_its_artifact` | the `machinome test` subprocess dies importing `faceted_stand_in`: `ImportError: cannot import name 'ExternalSourceIdentity' from 'machinome.node.sources'. Did you mean: '_ExternalWrapperIdentity'?` |
| 2.7 | the four `PublishArtifactTest` scenarios, and `test_assemble_presents_the_published_artifact` | the same `ImportError` (no `ExternalSourceIdentity`; `publish_artifact` does not exist either) |
| 2.3 | `test_a_replacement_under_the_same_stamp_is_not_served_stale` | `7.999999999999998 != 27.0`: the 2 mm box is served for the 3 mm box published under the same stamp |
| 2.3 | `test_a_rebuilt_shape_is_read_with_no_eviction_by_the_node` | `565.4866776461631 != 1005.3096491487338`: the r = 3 pin is served after the recipe changed to the r = 4 one |
| 2.4 | `test_each_docstring_lists_exactly_its_declared_members` (4 subtests) | `None != {...}`: no base docstring has a "Declared members:" paragraph |
| 2.4 | `test_each_docstring_names_the_capability_and_no_base_is_internal` (4) | no docstring says "declared extension point" or names `leaf-contract`; three say "framework-internal" |
| 2.4 | `test_the_api_reference_documents_every_declared_member` (32 subtests) | e.g. `'get_source_file' not found in {'time'}`: `LeafNode` documents only `time`; `FlexibleNode` has no autoclass; the sheet hooks are underscored and undocumented |
| 2.4 | `test_every_declared_member_exists` | the `ExternalSourceIdentity` `ImportError` building the faceted stand-in instance |
| 2.5 | `test_the_core_speaks_contract_one`, `test_the_version_is_an_integer_literal_in_the_source`, `test_an_undeclared_subclass_is_not_checked` | `AttributeError: module 'machinome.node.leaf' has no attribute 'CONTRACT'` (and no literal) |
| 2.5 | `test_the_base_documents_an_undeclared_contract` | `AttributeError: type object 'LeafNode' has no attribute 'leaf_contract'` |
| 2.5 | `test_a_mismatched_declaration_is_refused_naming_both_versions` (12 subtests) | `TypeError not raised` for 2, `'1'` and `True` on each of the four bases |
| 2.6 | `test_no_stand_in_or_leaving_adapter_reaches_a_private` (3 subtests) | `build123d_sheet.py`: imports `machinome.exact_artifacts` and its private `_atomic_export`, defines `_profile_faces`, `_lies_on_xy_plane`, `_extrude`, `_write_dxf`; `step.py`: imports private `machinome.node.sources._ExternalWrapperIdentity`; `molejo.py`: defines `_shape_parameters`, `_shape_spec`, `_snapshot_shape`, `_snapshot_mesh`, `_snapshot_stl` and reads `self._shape_spec` |
| 2.6 | `test_a_leaving_adapter_imports_only_declared_core_modules` | `[('build123d_sheet.py', 'machinome.exact_artifacts', '_atomic_export')] != []` |
| 2.8 | `test_a_recipe_reaches_every_artifact` (6 subtests) | e.g. `'f5793c6b…' == 'f5793c6b…'`: a recipe set on the `Dial` leaves the digest of its `.brep`, `.stl`, `.scad` and `.marking-digits.stl` unchanged, and the `Solid2Node`'s `.scad` and `.stl` likewise |

Green before, as characterizations by design: the stand-in exact project
builds, fuses and passes its three exact assertions in a subprocess with no
cadquery imported by the stand-in module (2.1); the stand-in is neither
`CadQueryNode` nor `Build123dNode` (2.1, `node-model`); a repeated
`cached_shape` returns the same object without reading the file, and the
recorded load observation is the file's (2.3 c, d); the spec declares
public members for all four bases (2.4); a matching declaration is a plain
class attribute (2.5); the scan knows the bases' privates, each allowed
exception is real, and the stand-ins import only declared modules (2.6);
with no recipe the two fixtures' records equal the golden's (2.8).

## 3. The contract in the bases (task 3.8)

After `leaf.py` (`CONTRACT = 1`, `leaf_contract = None`,
`__init_subclass__`, `publish_artifact`), `base.py` (`source_recipe`,
folded by `_with_recipe` into `_tracked_digest`/`_tracked_fingerprint`; a
non-string recipe is refused naming the node), `exact_leaf.py` (`_converted`
re-raising the hook's `TypeError` naming the node and type, at both call
sites), `sources.py` (`ExternalSourceIdentity`, no alias; `stl`, `step`,
`openscad`, `jscad` repointed), the sheet base and `build123d_sheet.py`
(public hooks, `write_dxf(face, path)`, the DXF through `publish_artifact`,
no `exact_artifacts` import), the flexible base, `molejo.py` and `test.py`
(public hooks, snapshot through `publish_artifact`), and `stl.py`
(`publish_artifact`, `_write_binary_stl` removed, `as_scad` calls
`materialize`):

```
pytest tests/test_leaf_contract_exact.py tests/test_leaf_contract_faceted.py tests/test_leaf_contract_members.py \
       tests/test_leaf_contract_version.py tests/test_leaf_contract_reach.py tests/test_leaf_contract_recipe.py
30 failed, 30 passed, 4 warnings, 154 subtests passed in 14.89s
```

Every remaining failure was a subtest of
`test_the_api_reference_documents_every_declared_member`, which task 6.1
turns green (below). `JScadNode` keeps its own publication (Decision 5).

## 4. The shape cache on the observation (task 4.3)

`exact_cache.cached_shape` keys on `(path, _metadata(path))`, one `os.stat`
giving `(st_dev, st_ino, st_size, st_mtime_ns, st_ctime_ns)`; a miss evicts
the path's entries and loads as before, the load observation recorded only
when coherent. `step.py`'s two comments now name the observation key.

```
pytest tests/test_shape_cache_observation.py
4 passed in 2.04s
pytest tests/test_exact_geometry.py tests/test_face_box_culling.py tests/test_exact_placement_cache.py \
       tests/test_intersection_memo.py tests/test_verdict_store.py tests/test_persistent_piece_facts.py
3 failed, 170 passed, 19 subtests passed in 9.85s      (before the repointing of 5.2)
... the same six files plus test_shape_cache_observation.py, after 5.2:
177 passed, 19 subtests passed in 9.55s
```

## 5. Existing tests repointed (tasks 5.1, 5.2)

No asserted value, verdict, message or expected exception changed. Every
repointed assertion, patch target or fixture, and why:

| test | what changed | why |
|---|---|---|
| `test_exact_geometry.py::ExactArtifactTest::test_shape_cache_evicts_the_previous_mtime` | `[key for key ...] == [(path, 2.0)]` became `[(key[0], key[1][3]) for key ...] == [(path, 2 * 10 ** 9)]` | the key is the observation; the survivor's path and `st_mtime_ns` are asserted (task 5.2) |
| `test_exact_geometry.py::ExactArtifactTest::test_a_rebuilt_shape_is_never_served_the_old_placement` | `{key[0] ...} == {(path, 2.0)}` became `{(key[0][0], key[0][1][3]) ...} == {(path, 2 * 10 ** 9)}`; docstring "(file, mtime)" → "(file, observation)" | the same (task 5.2; the test is in `test_exact_geometry.py`, not `test_exact_placement_cache.py`, which asserts no key form) |
| `test_verdict_store.py::NothingKeptForTheUncacheable::test_a_brep_rewritten_after_it_was_loaded_is_not_kept` | **not foreseen by design.md.** Its precondition `assertIs(pair[1].shape(), loaded)` relied on the old key serving the shape after `os.replace` of the `.brep` under a restored mtime, exactly the stale serving this cycle removes; it failed with `<TopoDS_Shape …> is not <TopoDS_Shape …>`. The precondition and the comparison now run under `patch.object(exact_cache, '_metadata', ...)` answering the pre-replacement `stat` for that path, i.e. the in-place rewrite within one tick that the observation key cannot see (Decision 3's residual case). The asserted values (`assertIs`, `computed.count == 1`, nothing kept) are unchanged; new import `from machinome import exact_cache` | the guard it tests (a shape whose bytes are gone has no persistent identity) still needs a way to hold a stale shape |
| `test_stl_node.py` (current artifact not rewritten) | patch target `machinome.node.adapters.stl._write_binary_stl` → `machinome.exact_artifacts._atomic_export`, same `side_effect=AssertionError('must not rewrite artifact')` | `_write_binary_stl` removed (task 3.7); `publish_artifact` writes through `_atomic_export` |
| `test_external_wrapper_identity.py::…test_same_named_native_wrappers_keep_their_own_adjusted_geometry` | the `mesh_producer` patch target `stl._write_binary_stl` → `stl._load_source_mesh` (wraps), `call_count == 0` unchanged | the same removal; the mesh is produced only inside the writer, whose first step reads the source |
| `test_flexible_node.py` (4), `test_molejo_adapter.py` (3), `test_flexible_cache_performance.py` (34), `test_flexible_verdict_identity.py` (4) | `_shape_parameters`, `_shape_spec`, `_snapshot_mesh`, `_snapshot_stl`, `_snapshot_shape` → public names (stub overrides and `patch.object` targets) | the renames of task 3.6 |
| `tests/conftest.py` | `collect_ignore` gains `contract_package` | its solid-runner test modules run only under `machinome test` |

`test_external_wrapper_identity.py` and `test_external_wrapper_review.py`
never named `_ExternalWrapperIdentity` (they name the hook
`_external_identity_origin`, which stays private), and `test_sheet_leaf.py`
and `test_flexible_document.py` name no renamed hook; they needed no edit.
`docs/adrs/NODE/ADR-054` names `_write_binary_stl()` as history and is left.
Suites run after 5.1, one process:

```
pytest test_external_wrapper_identity test_external_wrapper_review test_sheet_leaf test_flexible_node test_molejo_adapter \
       test_flexible_cache_performance test_flexible_verdict_identity test_flexible_document test_stl_node test_generation_dedup \
       test_markings test_build123d_adapter test_jscad_integration test_backend_neutral_materialization test_step_node
427 passed, 1 skipped, 8 warnings, 86 subtests passed in 29.62s
```

### 5.3 The golden pins after the change

```
tests/exact_engine_golden.py --check
golden comparison: 7 fixtures, 0 differences
tests/leaf_contract_golden.py --check
golden comparison: 7 fixtures, 97 values, 0 differences
```

### 5.4 The whole suite

Run once, alone, after the documentation of group 6 so the one run covers
it (a departure from the task order, so the API-reference agreement test is
in the run):

```
env -C <worktree> PYTHONPATH=<worktree> .venv/bin/python -m pytest -q -p no:cacheprovider
4263 passed, 4 skipped, 53 warnings, 3291 subtests passed in 509.84s (0:08:29)
wall time 513 s
```

After the ADRs, the plan amendment and the spec sync (no source change),
the files that read specs and documentation were run alone:
`test_leaf_contract_members test_docs_structure test_docs_exports
test_release_records`: `37 passed, 4 warnings, 307 subtests passed in
3.88s` — 2.4 passes against the synced `openspec/specs/leaf-contract/spec.md`.

## 6. Documentation

- `docs/reference/api.rst`, "Leaf nodes", under the workspace's
  `skills/write-the-manual/SKILL.md`: a paragraph naming the four bases at
  their defining modules, what a subclass never overrides, and the version
  (`autodata:: machinome.node.leaf.CONTRACT`, `leaf_contract`); autoclass
  entries at the defining paths with every declared member, instance
  attributes as `.. attribute::` entries. `SheetLeafNode` and `FlexibleNode`
  are now documented at `machinome.node.sheet_leaf` / `machinome.node.flexible`
  (they were `machinome.node.SheetLeafNode` / `.FlexibleNode`; the one
  cross-reference to the old path was updated). Docstrings were added or
  rewritten where autodoc needs one: `AbstractBaseNode.render`,
  `generate_scad`, `get_source_file`, `materialize`, `ExactLeafNode.shape`
  (listed before but silently dropped for want of a docstring). No how-to
  page (Decision 10).
- `docs/architecture.md`: the leaf-adapter paragraph ("the declared base"),
  a new paragraph on the declared leaf contract and its version, the sheet
  and flexible paragraphs ("a declared base", their public hooks), the
  exact-layer description of `exact_cache` (observation key, ADR-164), the
  invariant on cache keys, and the Node-model source-map row (capability
  `leaf-contract`, ADRs 163-165).
- `docs/project/changelog.rst`: one bullet at the top of `Unreleased`.

Strict build, `python -m sphinx -b html -n -W --keep-going -q docs <scratch>`:
exit 1 before and after, on the same five pre-existing nitpicky warnings
(`AssemblyNode.simulate`, `AssemblyNode.time`, "name keyword", two
`Sim` docstring phrases); none is in the leaf section and the change adds
none. Every declared member of the four bases and `CONTRACT` has an anchor
in the built `reference/api.html`.

## 8. Deep validation: machinome-freecad (tasks 8.1, 8.2)

Run by the orchestrator's validator subagent, not by the applier (the
orchestrator's correction to the applier's brief); its report, folded in
here. Worktree `machinome-freecad/WTs/lean-core-validation`, branch
`lean-core-validation`, commit 5ed665f471aeec174ec4a48f42b6b04debfc6abb on
top of `main` b5b6233, clean, never merged or pushed. The suite ran with
`PYTHONPATH=<bench>:<adapter worktree>` and the native runtime
(`MACHINOME_FREECAD_ROOT=…/Dum-E/.tools/freecad-1.1.4/squashfs-root`,
`MACHINOME_FREECAD_DUME_SOURCE=…/Dum-E/upstream/MA_Dum_E_v2_Assembly.FCStd`),
against the bench at 159cf78 plus this change's uncommitted implementation.

| run | result | wall |
|---|---|---|
| before, unchanged | 50 failed, 32 passed (82 tests) | 37 s |
| diagnostic: step 1 only (pin relaxed) | 6 failed, 76 passed | 140 s |
| after, full migration | 82 passed, 0 failed, 0 skipped | 146 s |

**Before.** All 50 failures have one cause, `NativeAssemblyError:
machinome-freecad requires tested machinome 0.7.1` (`adapter.py:207`): 44 as
the first line, 6 as `pytest.raises(match=...)` mismatches whose actual
message is the pin's. **Correction to design.md, Context item 4:** the pin
fired here. `importlib.metadata.version('machinome')` reads the workspace
venv's stale editable metadata, `machinome-0.7.0.dist-info`, not the bench's
`pyproject.toml` or `__version__`, so the refusal does not "pass while the
module it imports is gone" in this environment; it refuses for a reason that
has nothing to do with the contract. The conclusion stands, and is
strengthened: a release check reads whatever metadata happens to be
installed, not the code that runs, and cannot see a contract change.
ADR-165's context is worded accordingly.

**Diagnostic** (the validator's addition, disclosed): with the pin alone
relaxed, the six expected failures appeared, all `ModuleNotFoundError: No
module named 'machinome.exact'` from the `_evict` imports:
`test_native_recipe_refreshes_existing_exact_artifacts`,
`test_acceptance_recipe_alone_invalidates_existing_artifact_currency`, and
the four variants of `test_publication_source_race_publishes_no_artifact`
(in `[replace-False]` and `[delete-False]` the first line shown is the
`SourceChanged` or `FileNotFoundError` being handled). No `TopoDS_Shape`
method failure surfaced, because those tests fail at `_evict` first.

**The migration.** Diff stat `main..HEAD`: `machinome_freecad/adapter.py`
37 lines (+10/-27), `pyproject.toml` +4/-1, `tests/test_freshness.py` +5/-5,
`tests/test_public.py` +3/-2. Steps 1 to 5 of task 8.1 applied as listed:
the `machinome==0.7.1` pin relaxed and the construction-time refusal
removed; `_Solid` declares `leaf_contract = 1` and no `namespace`, and its
`render()` returns the bare `TopoDS_Shape`, checked with
`machinome.occt.engine.solid_count` and `BRepCheck_Analyzer(...).IsValid()`,
importing no cadquery; both `_evict` imports and calls and the `replaced`
computation removed from `_Solid.materialize`, the backup and restore kept;
`_NativeCurrency`'s `_tracked_fingerprint`/`_tracked_digest` overrides
replaced by one `source_recipe` property, which returns
`getattr(self, '_native_recipe', None)` after the generation check (the old
override hashed `''` before native resolution; only the moment before
`_ensure_native_assembly` differs, and the suite is green). One touch beyond
the brief: `render()` results on which CadQuery methods are called also
gained `cadquery.Shape.cast` (`test_public.py` 179-180 and 211,
`test_freshness.py` 309), since `render()` now returns the bare shape too;
`test_public.py` imports cadquery for that. No asserted value or expected
exception changed.

**Reaches outside the declared contract**, still present as expected: the
rollback inside `materialize` (`machinome.currency.sidecar`, in-place
`shutil.copy2`, `os.unlink`; Deferred, design.md); `AssemblyNode._link_children`
at two call sites and `source_generation.track_sources` on the carriers (the
assembly extension contract, Deferred); the adapter's own
`_check_native_generation`, which is the adapter's private, not the core's.
Expected but now gone: `self._up_to_date`, which served only the removed
`replaced` computation (the adapter's tests still call `leaf._up_to_date`
in `test_freshness.py`, which is test code).

**Scenario check (task 8.2).** `_Solid` defines only `render`,
`materialize`, `get_source_file` and `leaf_contract`, and inherits
`source_recipe` from the mixin: every member it overrides is declared, so
the `leaf-contract` scenario "The FreeCAD stand-in overrides only declared
members" holds.

**Findings beyond the list,** all on the carrier (assembly) side, recorded
and not fixed: `_Carrier.simulate` reads `slot._value` (`adapter.py:137`);
carriers are constructed with `object.__new__(cls)` then `cls.__init__`,
bypassing `AbstractBaseNode.__new__` (`adapter.py:275`); the undeclared
non-underscore members `self.src` (line 248) and `node.operations.append`
in `_place`; `_Solid.__qualname__` is reassigned after class creation and
`uniq_id` derives names from it (inferred: a `leaf_contract` refusal would
name `_Solid`, not the renamed class). Recorded only: adapter state kept in
underscore attributes on core instances (`_brep`, `_native_*`,
`_wrapper_source`, `_rest_coordinate`), with no collision today;
`observation_key` and `runtime._observe` imported and unused.

**cadquery at the end of a build.** A build of a copy of the adapter's
fixture through `machinome.manager.build.build_once` under the same command
wrote the leaf's `.brep` and `.stl`, and `'cadquery' in sys.modules` at exit
was False. Nothing contradicts the spec, and no test was left unable to run.

## 9. Shallow validation: the universe loaded (tasks 9.1, 9.2)

Run by the orchestrator, from the workspace root at 11:44 on 3 October 2026,
against the bench at 159cf78 plus this change's uncommitted implementation
(so before, not after, the implementation commit; the code swept is the
code committed):

```
scripts/load-projects --bench <bench> \
  --moved scripts/load-projects.d/exact-engine.toml \
  --moved <bench>/openspec/changes/leaf-contract/moved-names.toml \
  --timeout 300 --json <bench>/openspec/changes/leaf-contract/load-projects.json
62 repositories, 129 rows: 120 ok, 1 expected, 2 unexpected, 0 timeout, 6 no-model; 2 skipped
Skipped: .Trash-1000 (skip rule), sandbox (skip rule)
exit 1
```

The full table is `load-projects.json`, archived beside this file, and the
moved names the sweep was given are `moved-names.toml`. Every row that is
not `ok`:

| repository | class | cause |
|---|---|---|
| `3D-Printers/Voron-2` | expected | the first cycle's `shape()` move: `AttributeError: 'OCP.OCP.TopoDS.TopoDS_Shape' object has no attribute 'intersect'` at `simulation/switch_geometry.py` |
| `3DPrintedClocks` / `wall_clock_41` | unexpected, pre-existing | `ValueError: Workplane object must have at least one solid on the stack to union!` at `clocks/plates.py:5224`, in its own CadQuery code; it fails before the campaign too |
| `Robotic-Arms/Dum-E` | unexpected, environment | `ModuleNotFoundError: No module named 'machinome_freecad'`: the adapter is not installed in the venv; section 8 covers it |
| KZG-Marble-machine, Dummy-Robot, Primo, asimov-1, berkeley-humanoid-sim, upkie | no-model | no declared model |

Classification (task 9.2): no row names a leaf-contract move — no project
names `_ExternalWrapperIdentity`, a sheet or flexible hook, the old cache
key, or shadows one of the nine newly public names. Compared with the first
sweep at 5c163ea (119 ok, 1 timeout), the one change is a moon clock now
loading inside the 300 s timeout. Neither unexpected row is caused by this
cycle.

## 10. ADRs, plan, specs

- ADRs, under `docs/adrs/NODE/` (the subsystem of the four bases, the cache
  and ADR-162): ADR-163 (the leaf bases are declared extension points),
  ADR-164 (the loaded-shape cache keys on the artifact's observation,
  amending ADR-044), ADR-165 (a leaf package declares the contract version
  on its class, extending ADR-162). ADR-047, ADR-053 and ADR-057 carry
  "framework-internal base" superseded in part by 163 (status line and an
  inline note at the sentence); ADR-044 gains an *Amendment (2026-10-03)*
  section. `docs/adrs/README.md` lists 163-165 under NODE and updates the
  four entries. The ADRs link the change at
  `openspec/changes/archive/2026-10-03-leaf-contract/`, which resolves once
  the change is archived on that date.
- `workflow/ongoing/lean-core.md`: "What it takes" item 1, "machinome, the
  core" and the "Import paths" row amended to the four bases and the
  contract version, and the "Empirical validation" table's leaf-contract
  row is marked done with this file's archived path, after sections 8 and 9.
- Delta specs synced: `openspec/specs/leaf-contract/spec.md` created (eight
  requirements, Purpose written), `exact-geometry` ("Exact geometry is
  persisted and reloaded", "An exact render is admitted by its kernel
  object") and `node-model` ("Leaf adapters are distinct types") replaced by
  their modified text.

```
openspec validate leaf-contract --type change --strict
Change 'leaf-contract' is valid
openspec validate leaf-contract --type spec --strict      -> Specification 'leaf-contract' is valid
openspec validate exact-geometry --type spec --strict     -> valid
openspec validate node-model --type spec --strict         -> valid
```

(After the sync, `openspec validate leaf-contract --strict` without
`--type` answers "Ambiguous item 'leaf-contract' matches both a change and
a spec", so the type is given.)
