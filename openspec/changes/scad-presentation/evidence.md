# Evidence — `scad-presentation`

The sixth cycle of layer 1 of the lean-core campaign
(`workflow/ongoing/lean-core.md`, "Layers (pilot, 3 October 2026)", item 6).
Worktree `machinome/WTs/v0.8-scad-presentation`, branch
`v0.8-scad-presentation`, cut from `v0.8` at a4a1f84. Planning commit
9a894d4. Every command below ran from inside the worktree with
`PYTHONPATH=<worktree>` and the workspace venv (solidpython2 2.1.3, Python
3.12.3, OpenSCAD at `/usr/bin/openscad`); `machinome.__file__` resolved to
`<worktree>/machinome/__init__.py` and `machinome.openscad.__file__` to
`<worktree>/machinome/openscad/__init__.py` (checked once,
`env -C <worktree> PYTHONPATH=<worktree> .venv/bin/python -c 'import
machinome, machinome.openscad, solid2; ...'`). Pytest ran one process at a
time, never in parallel.

## 1. Baseline on the unmodified tree (9a894d4)

### 1.2 The presentation golden

`tests/scad_presentation_golden.py` (new, not collected) builds, under a
temporary `SOLID_BUILD_DIR`, `Bench` of the new fixture package
`tests/scad_presentation_project/` (`tools/bench.py`, the root, in package
`tools`; `parts.py`, its parts and sub-assemblies, in the parent package, so
every import is re-anchored across packages): a coloured single-child
assembly `Single` over a coloured `Solid2Node` on a rotation by `30`; an
empty assembly `Empty`; an `optimize = False` assembly `Unoptimized` inlining
a coloured `optimize = False` `Solid2Node` on a translation by
`[1, 2.5, 0]`; a `Solid2Node` declaring `fn = 24`; an `StlNode`; an exact
`CadQueryNode` on the symbolic rotation `$t * 360`; a faceted `FusionNode`
of two `Solid2Node`s; a molejo `Coil` bound to `12.0`; an `OpenScadNode`
(`plate.scad`); and `Legacy`, a project `LeafNode` overriding `as_scad`.
`Loose`, whose one `Solid2Node` renders `cube(1) + import_stl(
'vendor/external.stl')` (a project's own import), is assembled beside it and
never built to STL. The build is the one `tests/test_scad_import_paths.py`
runs: `assemble()`, every STL job (`trigger_stl`, `StlRenderStart.wait`)
until none starts, every node's memoized assembly forgotten, `assemble()`
once more with every artifact current.

It records the SHA-256 and length of every node's `scad_code` (17 nodes, by
their path of names) and of every `.scad` under the build directory after
that last `assemble()` (17 files, by path relative to the build directory),
each marked `scad_authored` when its node is a `Solid2Node`, an
`OpenScadNode` or a leaf whose `_uses_legacy_scad_materialization()` holds
(read without the change's predicate). Eight files are SCAD-authored
(`Boss`, `ColouredCube`, `FineCylinder`, `InlineCylinder`, `Legacy`, `Lug`,
`OwnImport`, `Plate`) and nine are presentation files (`Bracket`, `Block`,
`Coil`, `Empty`, `Fused`, `Single`, `Unoptimized`, the root `Bench` and
`Loose`).

Run twice in separate processes into the scratchpad, the two JSON files were
byte-identical (`cmp`); then written to
`tests/data/scad_presentation_golden.json` (bench commit 9a894d4), also
identical to both. `--check` on the unmodified tree:

```
golden comparison: 34 values, 0 differences, 0 presentation files absent as expected
```

### 1.3 The earlier goldens, unmodified tree

```
expression_type_golden.py --check  golden comparison: 17 values, 0 differences
exact_engine_golden.py --check     golden comparison: 7 fixtures, 0 differences
leaf_contract_golden.py --check    golden comparison: 7 fixtures, 97 values, 0 differences
markings_golden.py --check         golden comparison: 18 values, 0 differences
```

### 1.4 The files this change touches, unmodified tree

One pytest process: `test_expression_type.py`, `test_scad_engine_seam.py`,
`test_openscad_engine.py`, `test_openscad_dependency.py`,
`test_backend_neutral_materialization.py`, `test_scad_import_paths.py`,
`test_generation_dedup.py`, `test_snapshot.py`, `test_manager_develop.py`,
`test_flexible_node.py`, `test_stl_node.py`, `test_leaf_contract_faceted.py`,
`test_node_naming.py`, `test_builder_lifecycle.py`,
`test_build_publication.py`, `test_molejo_adapter.py`:

```
367 passed, 9 warnings, 35 subtests passed in 22.68s   (wall 24.07 s)
```

## 2. Red tests, on the unmodified source (9a894d4)

New files: `tests/test_scad_presentation.py` (2.1-2.3, 2.6-2.10), its
fixture package `tests/scad_where_read_project/` (`native.py`: an all-STL
`StlBench` and an all-exact `ExactBench` importing no SolidPython;
`legacy.py`: `LegacyBench` holding `Bracket(name='bracket')`, a project
`LeafNode` overriding `as_scad`; `machine.py`: `Machine`, an assembly
placing a sub-assembly `Group` of an exact `Block`, a faceted `Fused` of two
`StlNode`s, a molejo `Spring` bound to `12.0` and `FineCylinder`, the
golden's `Solid2Node` declared the same, turning with time; `Mixed`, one
`Solid2Node` among exact parts). Extended: `tests/test_scad_engine_seam.py`
(2.4), `tests/test_openscad_engine.py` (2.5); `tests/test_expression_type.py`'s
two AST lists shrunk to the new sets (2.1).

One pytest process (`test_scad_presentation.py test_scad_engine_seam.py
test_openscad_engine.py test_expression_type.py`):

```
41 failed, 32 passed, 2 warnings, 17 subtests passed in 49.52s   (wall 50.5 s)
```

Every red test and its reason, verbatim where quoted:

| test | reason |
|---|---|
| 2.1 `ImportersTest` (2) and `test_expression_type.py` `NoExpressionImportTest` (2) | `Items in the first set but not the second`: `node/base.py`, `node/operations.py`, `node/internal.py`, `node/flexible.py` import solid2; `node/base.py`, `viewers/openscad.py`, `manager/snapshot.py` reach `machinome.openscad` |
| 2.2 `test_native_projects_build_without_each_module` (4 subtests) | `machinome build` exits 1: `ModuleNotFoundError: No module named 'solid2'` raised at `machinome/node/base.py`, line 18 (`absent=solid2`); `No module named 'machinome.openscad'` at `node/base.py`, line 23 (`absent=machinome.openscad`), both reached from `core/loader.py` before any build |
| 2.2 `test_assemble_build_stls_and_mesh_without_each_module` (2) | the fixture's import fails the same way at `node/base.py` (`from solid2 import scad_render, import_stl, color`; `from machinome.openscad.binary import require_openscad`) |
| 2.3 `test_scad_text_is_refused_naming_the_module_and_its_install` (2) | `ImportError: cannot import name 'ScadEngineUnavailable' from 'machinome.scad_engine'` |
| 2.3 `test_a_build_holding_a_legacy_scad_leaf_is_refused_by_name` | `'node bracket (Bracket)' not found in` the output, which is the import traceback ending `No module named 'machinome.openscad'` |
| 2.3 `test_the_openscad_snapshot_renderer_is_refused_before_loading` (2) | the snapshot module does not import: `No module named 'solid2'` / `No module named 'machinome.openscad'` via `core/loader.py` |
| 2.4 `DeclarationTest`, `PackageTest` contract | `1 != 2` |
| 2.4 `ContractMismatchTest` (2) | `ScadEngineIncompatible not raised` (a provider declaring 1 is the core's own version) |
| 2.4 `RequireTest` (3) | `module 'machinome.scad_engine' has no attribute 'require_scad_engine'` / `'ScadEngineUnavailable'` |
| 2.4 `CountingProviderTest` (2) | `0 != 1` (no `scad_text` asked: the core composes SCAD itself); `Lists differ: [] != ['node FineCylinder (FineCylinder)']` (the binary is not reached through the provider) |
| 2.5 `ScadTextTest` (7) | `ModuleNotFoundError: No module named 'machinome.node.presentation'` |
| 2.6 `DescriptionTest` (4) | `No module named 'machinome.node.presentation'` |
| 2.7 `test_a_build_writes_only_the_scad_authored_leafs_scad` | `Lists differ`: the build left `machine-FineCylinder`, `machine-Fused`, `machine-Group`, `machine-Machine`, `machine-Spring` and `native-Block` `.scad` |
| 2.7 `test_the_builder_takes_no_scad_output` | `'scad_output' unexpectedly found in` `Builder`'s signature |
| 2.8 `test_presentation_scad_and_a_renamed_leafs_scad_are_swept` | `Lists differ ... First list contains 6 additional elements`: every seeded `.scad` spared by kind |
| 2.9 OpenSCAD snapshot (2) | the snapshot's `assemble()` wrote `machine-Fused`, `machine-Group`, `machine-Spring`, `native-Block` `.scad` beside the root's and the `Solid2Node`'s |
| 2.9 `test_the_web_renderer_writes_no_scad` | `Lists differ`: the web snapshot's `assemble()` wrote every node's `.scad` |

Green on the unmodified source, by design: 2.10's two characterisations
(`DevelopTest`: `Develop.handle` with `has_bundle` patched false exits 1 with
`INSTALL_REMEDY`, neither `Popen` nor `Process` called; the develop builder,
`scad_output=False` there, of `Mixed` writes exactly
`machine-FineCylinder-*.scad`), and the existing tests of the extended files.

The `.scad` files a `machinome build` of `Machine` writes into an empty build
directory, unmodified tree (a trial build into the scratchpad, 6.8 s):
`machine-FineCylinder-2111f2f9079a.scad`, `machine-Fused-8cedfb8cbef5.scad`,
`machine-Group-34ca0e766088.scad`, `machine-Machine-8f1cc42d7c1c.scad`,
`machine-Spring-db29e82a9287.scad`, `native-Block-211d0bb8cf4f.scad`, each
with its `.sources` record, and the spring's per-binding snapshot
`machine-Spring-db29e82a9287-9d687bebd44c.stl`.

## 3-6. Implementation

- `machinome/node/presentation.py` (new): `ArtifactImport`, `Color`, `Rotate`,
  `Translate`, `Union`, `Authored`, frozen dataclasses with `eq=False`
  (equality is identity, since a field may hold a symbolic value whose `==`
  is an expression); `described(value)` (a non-description held as
  `Authored`); `reanchored(description, build_dir, own_build_dir)`, a pure
  function sharing every node that holds no artifact import and never
  entering `Authored`. No import of `solid2` or of the engine.
- `node/operations.py`: `Rotation.presented(child)` /
  `Translation.presented(child)` in place of `.scad()`, holding the
  operation's own `angle`, `axis` and `translation` objects; no solid2 import.
- `machinome/scad_engine.py`: `CONTRACT = 2`; `ScadEngineUnavailable(needed_by,
  reason, missing=None, alternative=None)`; the missing module remembered at
  resolution; `require_scad_engine(needed_by, reason, alternative=None)`;
  remedies `install SolidPython with 'pip install solidpython2'` (solid2) and
  `reinstall machinome, whose distribution carries the OpenSCAD engine`
  (`machinome.openscad` or the provider); docstring listing the three
  operations and the requiring paths.
- `machinome/openscad/engine.py`: `CONTRACT = 2`; `scad_text(description,
  fn=None)` rebuilding the SolidPython calls the core made (`import_stl`,
  `color(list(rgb), alpha)`, `rotate(angle, axis)`, `translate(vector)`,
  `union()` / `union()([...])`, `Authored` content as is) and `scad_render`
  of it, `$fn` prefixed when given; `require_binary` delegating at call time
  to `machinome.openscad.binary.require_openscad`.
- `machinome/openscad/binary.py`: `OpenScadUnavailable(ScadEngineUnavailable)`,
  its message unchanged (it overrides `describe`).
- `node/base.py`: no solid2, no `machinome.openscad`, no `copy`; `assemble()`
  composes through `operation.presented`, calls `generate_scad()` nowhere and
  always returns a description; `artifact_import` returns `ArtifactImport`;
  `_colorize` returns `Color(tuple, 1, described(child))`;
  `_model_for_own_scad` uses `reanchored`; `_ArtifactImport` and
  `_reanchor_artifact_imports` removed; `scad_authored` (a property, false);
  `scad_code` is `require_scad_engine(f'node {name} ({qualname})', 'its SCAD
  text is written by the OpenSCAD engine').scad_text(_model_for_own_scad(),
  fn=self.fn)`; `generate_scad()` requires the engine first (through a
  module-level `_scad_engine_for(node)`, so the ADR-086 tests' duck-typed
  nodes keep calling `AbstractBaseNode.generate_scad` on a `SimpleNamespace`);
  `generate_stl` resolves the binary through
  `require_scad_engine(...).require_binary(...)` with today's words. The
  runner (`stl_builder_command_for`, `Popen`, `StlRenderStart`) is untouched.
- `node/internal.py`, `node/flexible.py`: `Union(...)` for `union()`; no solid2
  import; the flexible leaf's `snapshot_file` comment no longer claims the
  sweep reads it.
- `node/openscad.py`: `scad_code` from the engine's `scad_text`;
  `scad_authored = True`; its `render()` parsing stays (cycle 7).
  `node/solid2.py`: `scad_authored = True` only. `node/leaf.py`:
  `scad_authored` answers `_uses_legacy_scad_materialization()`; `as_scad`'s
  docstring. `node/exact_leaf.py`, `node/stl.py`, `node/jscad.py`: `as_scad`
  docstrings.
- `viewers/openscad.py`: `OpenScadRenderer.require_engine()`, `present(node)`
  (the root's `generate_scad()`), `withdraw(node)` and `render` resolving the
  binary through the provider; no `machinome.openscad` import.
- `manager/snapshot.py`: `self.renderer`; for the OpenSCAD renderer,
  `require_engine()` before the node is loaded (refusal printed, exit 1) and
  `present(node)` inside the build lock right after `assemble()`; catches the
  seam's `ScadEngineUnavailable`; no `machinome.openscad` import.
- `core/builder.py`: `_present_scad_if_requested`, its two calls and its
  `assembly` phase removed; `Builder` loses `scad_output`;
  `_sweep_unreferenced_artifacts` keeps a `.scad` by reference
  (`collect_scad`: the `scad_file` of every node whose `scad_authored`
  holds), `.scad` no longer spared by suffix, `collect_snapshots` removed.
  `manager/develop.py`: `run_builder` loses `scad_output`.

### The correction of Decision 3 (4 October 2026)

While making 2.9 green, `test_the_next_build_removes_the_snapshots_root_scad`
stayed red: build, OpenSCAD snapshot, build again, and the root's `.scad`
survived. The cause, read in `core/builder.py`:
`_write_viewer_snapshot_with_inventory` returns `recovered` before calling
`_sweep_unreferenced_artifacts` when the document it would publish equals
the published `viewer.json`, so a build with an unchanged document sweeps
nothing. Design.md's "the next successful build of that directory removes
it" and the lingering-files leg of Decision 11 assumed a sweep on every
successful build. Reported to the orchestrator with three options (a: sweep
everything on every build; b: apply only the `.scad` rule on an unchanged
document; c: narrow the scenario). The orchestrator decided (b), and added
that the renderer removes the root's on-demand `.scad` itself, in a
`finally`, once OpenSCAD has read it, succeeded or failed. Implemented:

- `Builder._write_viewer_snapshot_with_inventory` calls
  `_sweep_unreferenced_artifacts(snapshot, scad_only=True)` on an unchanged
  document: only `.scad` files and the records describing one are
  considered; every other artifact keeps today's trigger.
- `OpenScadRenderer.render` wraps the binary resolution and the runner in
  `try/finally: self.withdraw(node)`, which removes `node.scad_file` and its
  `.sources` record unless `node.scad_authored` holds (a `Solid2Node`
  snapshotted as the root keeps its own build artifact; this guard is the
  applier's, so the renderer never deletes a file a build keeps). The lock
  is not held through the OpenSCAD read: `manager/snapshot.py` releases
  `project_build_lock` when `_load_and_prepare_node` returns and calls
  `render` afterwards; the removal after the read stands regardless.
- Planning artifacts revised: design.md Decision 3 ("Correction, 4 October
  2026", the renderer and trade-off paragraphs), Decision 9's snapshot
  bullet, Decision 11's snapshot and lingering-files legs, Risks, Migration;
  proposal.md; the deltas `build-pipeline` (the sweep requirement's first
  paragraph, "A build removes any SCAD no current node writes" in place of
  "The next build removes the snapshot's root SCAD"), `web-snapshot` (the
  renderer removes its file; "A failed render removes the root's SCAD too";
  the pose scenario reads what OpenSCAD is given) and
  `backend-neutral-materialization` ("OpenSCAD users obtain a machine's SCAD
  on demand": `node.scad_code`); tasks.md 2.9, 6.1, 8.2, 8.3, 10.1, 11.2.
  `openspec validate scad-presentation --strict`: valid. The orchestrator
  asked for the planning commit 9a894d4 to be amended with these files only;
  the `git commit --amend` was refused by the session's permission
  classifier, so the revised planning artifacts are uncommitted beside the
  implementation and HEAD is still 9a894d4.
- Tests: 2.9 rewritten to read what OpenSCAD is given (the runner stub reads
  the `.scad` path it is handed) and to assert the file gone after a render,
  after a failed render, kept for a SCAD-authored root, and removed by a
  build that republishes the same document;
  `test_builder_lifecycle.py` gains the unchanged-document case.

## 7. Existing tests repointed

Run on the change before repointing (the 1.4 files plus every file the
greps of 7.1-7.4 named, one process): `57 failed, 595 passed, 1 skipped`.
Each change, by test, and why; no asserted SCAD text changed:

- **7.3, the binary through the seam.** 16 patches of
  `machinome.node.base.require_openscad` in `test_backend_neutral_materialization.py`
  (3), `test_build123d_adapter.py`, `test_exact_geometry.py`,
  `test_flexible_node.py`, `test_jscad_integration.py`,
  `test_no_class_name_recognition.py`, `test_openscad_dependency.py` (6),
  `test_sheet_leaf.py`, `test_stl_node.py` now patch
  `machinome.openscad.binary.require_openscad`, which the provider's
  `require_binary` calls at call time: every `side_effect=AssertionError(...)`
  and `assert_not_called()` still fails on any reach of the binary.
  (tasks.md named `openscad_binary`; `require_openscad` keeps each test's
  patch shape, a callable asserting it is never called.)
- **7.1, SCAD text through the engine.** `test_generation_dedup.py`
  `test_repeated_instances_render_user_code_but_generate_base_scad_once` and
  `test_audit_scale_repeated_instances_still_generate_one_base_scad`: the
  counted `base.scad_render` is now the engine's `scad_text` (still 1 call for
  2 and for 59 instances); `scad_render(assembled)` comparisons are
  `engine.scad_text(assembled)`. `test_source_set.py`
  `test_skipped_leaf_assembles_the_same_scad` and
  `test_cadquery_does_not_reexport_a_current_artifact`: `scad_render` ->
  `engine.scad_text`, same equalities. `test_stl_node.py`,
  `test_sheet_leaf.py`, `test_build123d_adapter.py`, `test_molejo_adapter.py`,
  `test_leaf_contract_faceted.py`, `test_backend_neutral_materialization.py`
  rendered nothing with `scad_render` (grep); nothing to change there.
- **7.2, a `.scad` only where read.**
  `test_generation_dedup.py`
  `test_binding_dependent_assemblies_keep_distinct_compositions`: the two
  assemblies' `generate_scad()` are called inside the same assembly phase
  after `assemble()`, so ADR-086's coalescing is still exercised (one parent
  write, holding the second's text). `test_scad_import_paths.py`: each setUp
  (and the second build) calls `generate_scad()` on the node whose file it
  reads (`Bench`, `Group` and `DeepBench`, `SameBench`); every resolution and
  spelling assertion unchanged. `test_two_pipes.py` `test_assemble`: the
  assembly's `.scad` is asserted absent after `assemble()`, then present
  after `generate_scad()`. `test_sheet_leaf.py`
  `test_a_current_sheet_leaf_skips_its_render_entirely` and
  `test_markings.py` `SkipDecisionTest.test_the_leaf_skip_predicates_are_not_widened`:
  `generate_scad()` after `assemble()`, because `LeafNode._render_can_be_skipped`
  (no production caller since ADR-102, design.md Deferred) still requires a
  current `.scad`. `test_markings.py`
  `OpenScadPathTest.test_the_openscad_renderer_photographs_the_marked_model`:
  `OpenScadRenderer().present(node)` before `render`, as `machinome snapshot`
  does. `test_snapshot.py`
  `SnapshotIntegrationTest.test_load_and_prepare_assembly_node`: sets
  `renderer = 'openscad'` (as `handle` does) and still asserts the root's
  `.scad`; new sibling `test_load_and_prepare_for_the_web_renderer_writes_no_root_scad`.
  `test_builder_lifecycle.py`
  `test_the_sweep_spares_inputs_locks_and_in_flight_temporaries`: `part.scad`
  is no longer spared and is asserted removed; new sibling
  `test_the_sweep_keeps_a_scad_authored_parts_scad` (kept with its record;
  another `.scad` removed on a changed document and on an unchanged one,
  where an unreferenced `.stl` stays). `test_manager_develop.py`: the seven
  expected `run_builder` argument tuples lose the trailing `scad_output`
  `False`. `test_molejo_adapter.py` `MolejoSnapshotSweepTest`, the
  `collect_snapshots` rule the design removes:
  `test_the_referenced_snapshot_survives_the_sweep` becomes
  `test_a_snapshot_an_assemble_left_is_swept` (the bound snapshot is removed
  by a sweeping publication); `test_a_binding_change_alone_republishes_nothing`
  still asserts the unchanged publication returns False and now that the
  snapshot written since survives it (the first publication removed the
  earlier one); `test_a_superseded_snapshot_is_collected` also asserts the
  bound snapshot gone.
- **Repointed by the ratified requiring paths.** `test_scad_engine_seam.py`
  `WithoutTheEngineTest.test_native_values_compose_and_publish_the_golden`
  ran the expression golden's `--check` with the provider absent. Its
  `scad_code` values and its `Solid2Node` parts' materialization now require
  the engine (scenario "SCAD text requires the OpenSCAD engine"), so it builds
  the golden's parts with the engine first, then, engine absent, compares the
  golden's operation digests and published-document digests with
  `tests/data/expression_type_golden.json` (both equal) and asserts
  `scad_code` refused: `SCAD refused node SharedMotion (SharedMotion) requires
  the OpenSCAD engine because its SCAD text is written by the OpenSCAD
  engine, and the module machinome.openscad.engine cannot be found; reinstall
  machinome, whose distribution carries the OpenSCAD engine`.
  `ContractMismatchTest`'s stubs declare 1 (the version the core no longer
  speaks); `DeclarationTest` and `PackageTest` expect 2.
- **7.4.** No test called `Rotation.scad` or `Translation.scad` (grep);
  `presented` is tested in `test_scad_presentation.py`. One docstring of
  `test_expression_bindings.py` names `operation.presented(...)`.

## 7.5 The goldens, after the change

```
expression_type_golden.py --check   golden comparison: 17 values, 0 differences
exact_engine_golden.py --check      golden comparison: 7 fixtures, 0 differences
markings_golden.py --check          golden comparison: 18 values, 0 differences
scad_presentation_golden.py --check golden comparison: 34 values, 1 differences, 9 presentation files absent as expected
leaf_contract_golden.py --check     golden comparison: 7 fixtures, 77 values, 20 differences
```

`scad_presentation_golden.py`: every node's `scad_code` (17) byte-identical;
the nine presentation files absent as Decision 3 expects; seven of the eight
SCAD-authored files byte-identical; one differs:

```
DIFFERS: file scad_presentation_project/parts-InlineCylinder-e6e368128f71.scad:
  golden={'length': 82, 'scad_authored': True, 'sha256': 'b26e0f84...'}
  now={'length': 24, 'scad_authored': True, 'sha256': 'afad8502...'}
```

`InlineCylinder` is a `Solid2Node` declaring `optimize = False` and a
`color`. Its materialization writes its authored model, uncoloured (24
bytes, `cylinder(h = 5, r = 2);`), and OpenSCAD renders its STL from that.
Before the change `assemble()`'s non-optimized branch then set `model` to
the *coloured* model and wrote it over the same file (82 bytes,
`color(...) { cylinder(...) }`); in a `machinome build` that overwrite came
after the STL render, so the file a build left was the coloured one, a
presentation artifact the STL was not made from. After the change nothing
overwrites the materialized file. Only a SCAD-authored leaf declaring both
`optimize = False` and `color` is affected; its `scad_code`, its STL's
geometry and every parent's SCAD are unchanged. Not "fixed" here: keeping
the old bytes would mean materializing the coloured model, changing what
OpenSCAD renders the STL from. Returned to the orchestrator as a departure
from Decision 8's "no difference is unavoidable".

Decided (orchestrator, 4 October 2026; the pilot may overrule before
integration): accepted as a correction of Decision 8, which now reads "one
difference, by construction". The bytes:

```
before  82 bytes  sha256 b26e0f843d0c98319f86a99d1ec781fca0de0c06a429433f65a1cce2f06e51ca
        color(alpha = 1, c = [0.0, 0.6274509803921569, 1.0]) {\n\tcylinder(h = 5, r = 2);\n}\n
after   24 bytes  sha256 afad85022194324f3b0ae3139c9dd02f5db2fb305695e297b91fc68d7af5a647
        cylinder(h = 5, r = 2);\n
```

The after hash was computed from the text alone (no build ran) and equals
the one `--check` reported. That one entry of
`tests/data/scad_presentation_golden.json` was re-recorded by hand, with a
`re_recorded` note beside `fixture` holding the old values and the reason;
`--check` reads `fixture` only. The node's own `scad_code` entry
(`Bench/Unoptimized/InlineCylinder`, 82 bytes, the coloured text) is
unchanged. The changelog sentence was corrected to match. `--check` is to
be run after the orchestrator's validation (expected: 0 differences, 9
presentation files absent as expected).

`leaf_contract_golden.py` (the second cycle's): the 20 differences are the
five recorded fields (`digest`, `fingerprint_matches`, `record_version`,
`sha256`, `stamp_matches`) of the `.scad` of four native leaves the golden
assembles (`build123d_sheet_panel`, `exact_leaf_with_marking`,
`molejo_snapshot`, `stl_node_with_markings`), now `None` because
`assemble()` writes no `.scad` for a leaf that is not SCAD-authored:
exactly the absences Decision 3 expects. Every other value of the 77 (STL,
BREP, DXF, markings, the `Solid2Node`'s and the `OpenScadNode`'s `.scad`)
is identical. The golden and its data are the earlier cycle's and are left
as they are; whether to re-record them or teach their `--check` the
expected absences is the orchestrator's call.

Decided (orchestrator, 4 October 2026): re-record
`tests/data/leaf_contract_golden.json` on the new tree after the
orchestrator's validation reports, then `--check`. Before re-recording,
the 20 differences are the five record fields (`digest`,
`fingerprint_matches`, `record_version`, `sha256`, `stamp_matches`) of the
`.scad` of `build123d_sheet_panel`, `exact_leaf_with_marking`,
`molejo_snapshot` and `stl_node_with_markings`, now `None`.

Re-recorded after the validation (bench at eebedf2): written to the
scratchpad first and compared with the recorded file value by value: 97
recorded, 77 now, 20 gone (exactly those 20), 0 added, 0 changed; the 77
remaining values were unchanged before re-recording. (The orchestrator's
"57 values" was 77 minus 20 counted twice; `--check` counts the values it
measures, 77.) Then copied over `tests/data/leaf_contract_golden.json`
(its `bench_commit` now eebedf2). `test_leaf_contract_recipe.py` compares
with the re-recorded golden directly, its special case for the dropped
`.scad` removed.

## 8. Documentation

Read first: `skills/write-the-manual/SKILL.md` (workspace). Pages changed, each
folded into the page that owns the subject:

- `docs/concepts/publishing.rst`, "The build directory": the `.scad` of
  OpenSCAD-family parts only, from `build` and `develop` alike, and every
  successful build, document changed or not, removes any `.scad` no current
  part writes; "Snapshots": the OpenSCAD renderer writes the root's `.scad`
  for its pose, has OpenSCAD draw it and removes it; the web renderer reads
  no SCAD; a machine's SCAD text is `scad_code`.
- `docs/reference/api.rst`: `LeafNode.scad_file` and `model`; `as_scad`,
  `artifact_import`, `generate_scad` and `assemble` are autodoc'd from the
  docstrings changed in `node/base.py` and `node/leaf.py`.
- `docs/project/changelog.rst`: the Unreleased bullet of tasks.md 8.3, its
  on-demand sentence as corrected on 4 October ("A machine's SCAD text is
  `node.scad_code`...; `machinome snapshot --renderer openscad` writes the
  root's `.scad` ... only while OpenSCAD draws it, and removes it
  afterwards"). Its "Every `.scad` still written is byte for byte what it
  was" holds except for the `optimize = False` coloured `Solid2Node` of 7.5.
- `docs/architecture.md` (not the manual): `assemble()` and the description,
  the adapters' SCAD paragraph, the flexible snapshot, the operations'
  consumers (`.presented()`), ADR-116's re-anchoring over the description,
  the sweep paragraph (by reference, on every successful build), the
  snapshot renderer, the source-map rows (`node/presentation.py`, the seam's
  contract 2, the engine's three operations; ADRs 172 and 173).
- `workflow/ongoing/lean-core.md`: "Where the core reaches each kernel",
  the "Import paths" OpenSCAD engine row, "Layers" item 6 marked done with
  the `develop` note, the pilot's decision (A) and the 4 October correction,
  and the "Empirical validation" row for `scad-presentation`, its result
  pending 10.1-10.3.

`python -m sphinx -b html -n -W --keep-going docs <scratch>`: exit 1 on five
warnings (`api.rst:23`, `:35`, `:76`, two `Sim` docstrings), the same five a
build of the unmodified tree (`git archive HEAD`) gives; none from this
change.

Lint: `flake8 --max-line-length=89` (7.3.0) over every changed or new Python
file, compared with the same files at HEAD: no finding added (one, in
`presentation.py`, fixed).

## 7.6 The full framework suite

Run once, alone (no other pytest process; `pgrep -af "[p]ytest"` empty
before), after 1-8:

```
env -C <worktree> PYTHONPATH=<worktree> .venv/bin/python -m pytest -q -p no:cacheprovider -rf
6 failed, 4381 passed, 4 skipped, 55 warnings, 3670 subtests passed in 646.61s (0:10:46)
exit 1; wall time 650 s; no "Too many open files"
```

Beside `expression-type`'s run of record (`4350 passed, 4 skipped, 3648
subtests passed in 526.46s`): 37 more tests (the new files). The six
failures were tests the greps of 7.1-7.4 had not named, each reading a
`.scad` that `assemble()` or a build no longer writes, or asserting the
builder assembles; repointed after the run, as 7.2 says, and those four files
re-run alone: `test_coarse_filesystem_freshness.py`,
`test_content_verified_currency.py`, `test_leaf_contract_recipe.py`,
`test_retained_builder_generation.py`: `47 passed, 14 subtests` (with one
more fix to `test_coarse_filesystem_freshness.py`, then `13 passed`).

- `test_coarse_filesystem_freshness.py`
  `test_exact_leaf_caches_on_a_millisecond_filesystem` and
  `NativeFilesystemTest.test_exact_equality_still_holds_natively`:
  `FileNotFoundError` / `False is not true` on the exact leaf's `.scad`;
  `generate_scad()` after `assemble()`, so the `.scad` stamping writer is
  still checked on the millisecond filesystem.
- `test_content_verified_currency.py`
  `test_every_published_artifact_records_its_source_fingerprint`: `None !=
  '<fingerprint>'` on the exact leaves' `.scad`; it now asserts the `.scad`
  absent and checks STL and BREP records as before.
- `test_leaf_contract_recipe.py`
  `test_no_recipe_records_what_the_tree_recorded_before`
  (`exact_leaf_with_marking`): `['.brep', '.marking-digits.stl', '.stl'] !=
  [... '.scad', ...]`; the golden's `.scad` entry for that native leaf is
  dropped from the expectation, every other record compared as before.
- `test_retained_builder_generation.py` (2): `Expected 'mock' to be called
  once. Called 0 times.` on `node.assemble`; the builder presents no SCAD,
  so they assert `_prepare` called once and `assemble` never, and the fusion
  test drives its composition from `_prepare` (one ordered composition per
  retained build, as before).

The whole suite was not run a second time after these four repoints (the
brief: once, alone). Decided (orchestrator): the applier runs the whole suite
once more, alone, before the implementation commit, and that run is the one
this section reports; the orchestrator's run on the commit is the cycle's
record.

## 11.2 ADRs (written while the orchestrator's validation runs)

- `docs/adrs/NODE/ADR-172-the-core-describes-its-scad-presentation-and-the-openscad-engine-writes-it.md`:
  the description, contract 2, expressions as values, the binary through the
  seam, the leaf contract at 1 (Decision 6, accepted by the orchestrator).
  Amends ADR-102 (the compatibility consumer), ADR-116 (the mechanism) and
  ADR-171 (contract and direct reaches), each with a status line and an
  amendment section.
- `docs/adrs/BUILD/ADR-173-scad-is-written-only-where-it-is-read.md`: the
  pilot's option A (3 October 2026), option B rejected and why, the
  renderer's on-demand SCAD and its removal, the sweep by reference on every
  successful build (the correction of 4 October 2026 with the applier's
  evidence of the trigger), `require_scad_engine` and its remedies, the one
  `.scad` whose bytes change. Amends ADR-046 (the refusal family), ADR-086
  (production producer removed) and ADR-102 (its consequences), each with a
  status line and an amendment section.
- `docs/adrs/README.md`: entries for 172 (NODE) and 173 (BUILD), and the
  amended-by notes on 046, 086, 102, 116, 171.
- Both ADRs link the change at `openspec/changes/scad-presentation/`; the
  link moves to its archive path when the change is archived.

## 11.1 Empirical validation (the orchestrator's), part one: 10.1 and 10.2

Run by the orchestrator on the bench at 9a894d4 plus this uncommitted tree
(61 paths), Locks/Pin_tumbler_lock on its branch `lean-core-validation` at
e461fba (one commit behind its main, the profile-rename commit only),
`PYTHONPATH=<bench>:<project>`, scratch build directories, one process at a
time, 4 October 2026 00:46:20 to 00:48:06. Quoted from the orchestrator's log
(`ptl6-after.log`, session scratchpad).

### 10.1 Leg 1: build, test --faceted, export

```
--- machinome build ---
exit 0 in 11 s
after build: 11 scad, non-parts: 0; PenSpring per-binding STLs: 0; PenSpring files: 0
--- machinome test --faceted ---
Ran 24 tests in 29.10 seconds: 24 passed, 0 failed (faceted kernel, volume epsilon 0 mm³)
exit 0 in 30 s
after test: 15 scad
--- machinome export --set key_delta=0 -o <scratch>/ptl6-export-after ---
exit 0 in 1 s
after 15 scad: identical-to-baseline 2, differing 13, new 0
baseline paths absent after: 9 -> {'flexibles-PenSpring': 1, 'lock-PinTumblerLock': 4, 'lock-Plug': 4}
parts-* after: 15; non-parts after: []
manifest identical: True | identical with volumes stripped: True
```

The fifth cycle's 24 `.scad` minus the 9 `lock-*` and `flexibles-*` paths
leaves 15 `parts-*`; 2 are byte-identical to that baseline and 13 differ
(`Body`, `Circlip`, `Core`, `DriverPin`, three `Key`, five `Pin`,
`SpringCover`).

**Why 13 differ: the self-import the old code wrote across processes.** The
fifth cycle's after-leg hashes were taken after three processes (build, test,
export). On a4a1f84 a later process's `assemble()` of a current `Solid2Node`
took the skip path: `model = artifact_import(local_stl)`, then
`generate_scad()`, overwriting the leaf's `.scad` with an import of its own
STL. The byte-identical write suppression does not apply (the content
differs) and the source generation's reuse is process-local. Read by the
applier in the scratch directories (the fifth cycle's after leg,
`ptl-build-after`):

```
$ wc -c ptl-build-after/simulation/parts-Core,...-38d056aa9875.scad      # a4a1f84, after three processes
215
$fn = 72;

use </mnt/data/machinome-projects/Locks/Pin_tumbler_lock/simulation/scad/part.scad>;

import(file = "parts-Core,cut_1=6,cut_2=1,cut_3=2,cut_4=5,cut_5=0,depth=0,kind=1-38d056aa9875.stl", origin = [0, 0]);

$ wc -c ptl6-build-develop/simulation/parts-Core,...-38d056aa9875.scad   # this change
237
$fn = 72;

use </mnt/data/machinome-projects/Locks/Pin_tumbler_lock/simulation/scad/part.scad>;

part(cuts = [6, 1, 2, 5, 0], depth = 0, kind = 1, svg = "/mnt/data/machinome-projects/Locks/Pin_tumbler_lock/upstream/Modified_Yale8.svg");
```

13 of the 15 `parts-*.scad` in the fifth cycle's after-leg directory are
such self-imports (`grep '^import(file = "parts-'`); the two that match are
parameter sets the test suite built once and no later process assembled. The
project's own `_build/` holds the same self-imports after many builds.

**Byte identity against the old code, single process.** The fifth cycle's
snapshot before leg ran one process on a4a1f84 into a fresh directory
(`ptl-build-snap-before`). Its 11 `parts-*.scad` are byte-identical (`cmp`)
to the 11 this change's build writes, both in the leg 1 directory
(`ptl6-build-after`) and in the develop builder's (`ptl6-build-develop`):

```
ptl6-build-after vs snap-before: identical 11, other 0
ptl6-build-develop vs snap-before: identical 11, other 0
```

So 10.1's expectation, written against the fifth cycle's three-process after
leg, was against bytes the old code produced by overwriting; against its
single-process build every `.scad` this change writes is identical. This is
the `InlineCylinder` mechanism of 7.5 at full size, `assemble()` rewriting an
artifact already consumed, and option A removes it: a current
OpenSCAD-family part's `.scad` is no longer replaced by an import of its own
STL by the next process (had its STL then gone stale under the same name,
OpenSCAD would have rendered an empty import). Fixed here; no wart.

### 10.1 Leg 2: snapshot on demand, same directory

```
--- snapshot --renderer openscad (PATH shim captures the SCAD) ---
Snapshot saved to <scratch>/ptl6-snap-after.png
exit 0 in 1 s
png bytes: 35421 (before leg: 35211)
root scad left in build dir: 0 (files); root sidecar: 0
captured root scad lock-PinTumblerLock,cut_1=6,cut_2=1,cut_3=2,cut_4=5,cut_5=0,key_d-e454063c47d0.scad: 6916 bytes sha256 d39e88107bd30ce0; imports 20, missing 0 []; "$t" occurrences 0
scad in build dir after snapshot: 15; non-parts: 0
png sizes (1920, 1080) (1920, 1080) | differing pixels 70 of 2073600 bbox (753, 112, 1237, 847)
--- machinome build ---
exit 0 in 3 s
scad after the following build: 11; non-parts: 0
--- snapshot with machinome.openscad.engine unfindable ---
exit 1 in 0 s
Error: the OpenSCAD snapshot renderer requires the OpenSCAD engine because it renders the SCAD the OpenSCAD engine writes, and the module machinome.openscad.engine cannot be found; reinstall machinome, whose distribution carries the OpenSCAD engine, or use --renderer web
refused png exists: no; root scad in build dir: 0; scad count: 11; engine attempts (exit.log): 1742672 1 -;
```

The 70 differing pixels are OpenSCAD's STL noise. The root's SCAD, as
OpenSCAD was given it (a `PATH` shim copied it), carries the snapshot's pose
numerically (no `$t`), and all 20 imports resolve from its directory; the
renderer removed it and its record afterwards.

### 10.1 Leg 3: lingering files

```
seeded: 31 scad, 31 scad records, 104 files
--- machinome build ---
exit 0 in 12 s
after build: 11 scad (11 parts-*), 11 scad records; non-parts:
records without their scad: 0; scad without record: 0
--- (b): old lock-*/flexibles-*/poses-* scad + records copied back, document unchanged, build again ---
copied back 8 files; scad now: 15
--- machinome build ---
exit 0 in 2 s
viewer.json unchanged by the rebuild: yes
after unchanged-document build: 11 scad (11 parts-*), 11 scad records; non-parts:
```

The second half exercises the correction of 4 October: a build that
republishes the same document still removes every `.scad` no current node
writes.

### 10.1 Leg 4: develop without a display

```
develop: exit 1; stderr='Error: The browser viewer is not installed. It is the separate machinome-viewer package; install it with: pip install "machinome[viewer]"'; Popen called False; Process called False
--- Builder(..., watch=False, lifecycle=True).start() in a subprocess ---
exit 0 in 10 s
develop builder wrote: 11 scad (11 parts-*); non-parts:
same scad set as machinome build: yes
```

### 10.2 OpenAstroMount, `solid2` unfindable

Branch `exact-engine-validation`, read-only:

```
exit 0 in 34 s
oam build dir: viewer.json yes; stl 90; brep 90; scad 0; exit.log: 1743248 0 OCP,cadquery,machinome.occt.engine;1743211 0 OCP,cadquery;1743247 0 -;
```

`solid2` was never asked for in any of the build's three processes. Nothing
changed in either project (`git status` clean after the legs; the lock back on
`main`).

10.3, the universe sweep: pending.

### The goldens after the validation (bench at eebedf2)

```
scad_presentation_golden.py --check   golden comparison: 34 values, 0 differences, 9 presentation files absent as expected
leaf_contract_golden.py --check       golden comparison: 7 fixtures, 77 values, 0 differences   (re-recorded)
test_leaf_contract_recipe.py          2 passed, 14 subtests passed
```

### 7.6 The full suite, run of record (bench at 63c887e)

After the orchestrator's validation and the leaf-contract golden's
re-recording, once, alone (`pgrep -af "[p]ytest"` empty before):

```
env -C <worktree> PYTHONPATH=<worktree> .venv/bin/python -m pytest -q -p no:cacheprovider -rf
4386 passed, 4 skipped, 55 warnings, 3671 subtests passed in 633.30s (0:10:33)
exit 0; wall time 635 s; no "Too many open files"
```

Beside the first run (6 failed, 4381 passed, 3670 subtests): the six
repointed tests pass and the two new tests of the repoints
(`test_load_and_prepare_for_the_web_renderer_writes_no_root_scad`, already
counted, and the four files' adjustments) bring 4386 passed. Beside
`expression-type`'s run of record (4350 passed, 3648 subtests, 526 s): 36
more tests, 23 more subtests, 107 s more wall time, the new subprocess
tests of `test_scad_presentation.py` (builds with and without each module)
among them.
