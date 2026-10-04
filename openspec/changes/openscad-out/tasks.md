## 1. Evidence baseline on the unmodified tree

- [ ] 1.1 Create `openspec/changes/openscad-out/evidence.md` in the shape of the
  archived cycles' (`2026-10-04-mesh-engine/evidence.md`), with the bench
  commit, and record there the facts design.md rests on, re-measured: the
  scan's red count (run the rule of design.md Decision 1 as a script over
  `machinome/` with the four allowed zones; expected 37 modules, 453
  occurrences, and its per-module list); the fourteen probe sites of Decision 5
  (a grep for `getattr(` with three arguments and `hasattr(` naming a member of
  the set); the two SolidPython probes of Decision 2 (the 129-byte description
  text and the same text after `import_scad` with its `use` line; the
  `m(3, b=4.5)` and too-many-arguments probes of `get_scad_file_as_dict`); the
  modules left in `sys.modules` by importing `machinome.node`,
  `machinome.node.base`, `machinome.core.builder` and `machinome.test`.
  Proves: the evidence the design cites exists in the change.
- [ ] 1.2 Run, before any source change, each in a fresh process:
  `python tests/leaf_contract_golden.py --check`,
  `python tests/scad_presentation_golden.py --check`,
  `python tests/expression_type_golden.py --check`; record that each passes.
  Proves: the three byte goldens of Decision 11 hold on the base.
- [ ] 1.3 Run, on the unmodified tree, one pytest process at a time, the touched
  suites: the 48 test files design.md Decision 15 rewrites, and
  `test_kernel_extras.py`, `test_core_kernel_free.py`,
  `test_node_lazy_exports.py`, `test_cli_lazy_imports.py`,
  `test_manager_new.py`, `test_assertions.py`, `test_broad_phase_culling.py`,
  `test_intersection_memo.py`, `test_connectivity.py`,
  `test_vet_universe.py`, `test_browser_renderer.py`, `test_camera.py`; record
  counts and wall time. Proves: the touched suites' green baseline.

## 2. Red tests (each red on the unmodified tree for the reason given)

- [ ] 2.1 `tests/test_core_names_no_scad.py`, the gate of Decision 1: the rule
  as a function with its own unit cases (`jscad`, `JScadNode`,
  `OpenJScadNode`, `machinome/node/jscad.py` pass; `openscad`, `scad_file`,
  `.scad`, `cascade`, `openjscad` fail) and the scan of `machinome/**/*.py`
  outside the four allowed zones reporting each offending file with its count
  and first tokens. Red: 37 modules offend. Proves: the acceptance gate.
- [ ] 2.2 `tests/test_openscad_node.py`: the package's modules import
  (`machinome.node.openscad.writer.scad_text`, `.binary.require_openscad`,
  `.leaf.ScadLeafNode`); `OpenScadNode.__module__ == 'machinome.node.openscad'`;
  `OpenScadNode` and `Solid2Node` subclass `ScadLeafNode`; `import
  machinome.scad_engine` and `import machinome.openscad` raise
  `ModuleNotFoundError`; `machinome.viewers.openscad` imports neither of them.
  Red: no package, the old modules exist, the viewer imports the seam.
- [ ] 2.3 The three doors, with a finder blocking `solid2`: importing
  `machinome.node.openscad`, `machinome.viewers.openscad` and
  `machinome.node.solid2` raise `ExtraUnavailable` with R1, R1 and R2
  (design.md Decision 8) verbatim; `from machinome.node import Solid2Node`
  carries R2; in a fresh interpreter, importing `machinome.node`,
  `machinome.node.base`, `machinome.core.builder`, `machinome.test` and
  assembling and building an `StlNode` assembly leaves no `solid2*` module and
  no module that is or lies under `machinome.scad_engine`, `machinome.openscad`
  or `machinome.node.openscad`. Red: today a plain `ModuleNotFoundError: solid2`
  with no extra, and `machinome.scad_engine` is loaded by `node/base.py:21`.
- [ ] 2.4 `tests/test_kernel_extras.py` extended: `solidpython2` is not in the
  required dependencies; `openscad` installs `solidpython2==2.1.*`; `solid2`
  includes `machinome[openscad]`; `all` includes both; `requirements.txt` still
  names SolidPython. Red: SolidPython is required and the extras do not exist.
- [ ] 2.5 `tests/test_snapshot.py` additions: with `solid2` blocked,
  `machinome snapshot` (no `--renderer`) and `--renderer openscad` print R4,
  exit 1, and neither load the node (a patched `load_node` asserting it is not
  called) nor write a `.scad`; `--renderer` choices are `web` plus the table's
  renderer names, the default the table's `DEFAULT_RENDERER`; with
  `--renderer web`, `assemble()` is not called (patched to raise). Red: today
  the refusal is `ScadEngineUnavailable`'s text, `assemble()` is called for both
  renderers and the choices are a literal.
- [ ] 2.6 `tests/test_leaf_capability_set.py`: `machinome.node.leaf.CONTRACT ==
  2`; a class declaring `leaf_contract = 1` is refused naming 1, 2 and
  `machinome.node.leaf`; a self-materializing `LeafNode` subclass answers the
  whole set with the defaults (`rigid`, not `flexible`, not `exact`,
  `optimize`, `present` returning `artifact_import(local_stl)`,
  `kept_artifacts() == ()`); a family leaf's `kept_artifacts()` is
  `(scad_file,)`; an AST scan of `machinome/` finds no `getattr(x, '<member>',
  <default>)` and no `hasattr(x, '<member>')` for a member of the set. Red: no
  `present`, no `kept_artifacts`, `CONTRACT == 1`, fourteen probes found.
- [ ] 2.7 R7: a `LeafNode` subclass whose `materialize` publishes nothing,
  built with `build_stls()` and with `machinome.node.openscad.binary.openscad_binary`
  patched to a sentinel path and `subprocess.Popen` patched to fail the test if
  called, raises `ArtifactNotProduced` with R7's text naming the node, its class
  and its STL path. Red: today it reaches `require_binary` and `Popen`.
- [ ] 2.8 The sweep by declaration and the transient rule
  (`tests/test_build_publication.py`, `tests/test_content_verified_currency.py`):
  a tree holding a `Solid2Node` whose STL is current, rebuilt to a changed
  document, keeps its `.scad` and record; the same with the leaf's
  `kept_artifacts` patched to `()` removes them, proving no suffix rule keeps
  them; `currency.record(..., transient=True)` writes `"transient": true` and
  `recorded_transient` reads it, a record without the key answering `False`;
  a file published transient is removed, with its record, by a build that
  publishes an unchanged document, while an unreferenced file with a
  non-transient record stays; a `Solid2Node` root's own `.scad` is not
  transient after the OpenSCAD renderer's `present`; `core/builder.py`
  contains no `scad_only` and no `.scad` literal (also covered by 2.1). Red:
  today `collect_scad` keeps the file by `scad_authored` whatever
  `kept_artifacts` says, `record` takes no `transient`, and the
  unchanged-document pass removes by suffix.
- [ ] 2.9 `tests/test_generation_dedup.py` rewritten in its coalescing part:
  `SourcePhase` has no `defer_scad`, `coalesces_scad` or `pending_scad_count`;
  the `assembly` phase's checkpoints are labelled `assembly post`;
  `SourceGeneration.has_published` / `remember_published` keep the
  A → B → A semantics of "Historical identity is not current identity". Red:
  the coalescing exists and the record has its old names.
- [ ] 2.10 Adoption (`tests/test_openscad_node.py`): in a fresh interpreter,
  `machinome.expression_graph.symbolic(solid2.get_animation_time())` is `None`,
  and after `import machinome.node.solid2` is the `$t` name node;
  `register_adopter` is idempotent. Red: today the seam adopts without the
  import, and `register_adopter` does not exist.
- [ ] 2.11 `closed_expression`: `str(value) ==
  machinome.core.expressions.closed_expression(value._expression_node)` for a
  shared value with a `let` binding. Red: no such name.
- [ ] 2.12 The table (`tests/test_supported_node_types.py`): `NODE_TYPES` names
  `cadquery`, `build123d`, `step`, `molejo`, `solid2`, `openscad`, `jscad`,
  `stl`; every class name it lists is exported by `machinome.node` and resolves
  to the object the old export table resolved; `supported.needed_by('import-step')
  == 'step'` and `cli.COMMANDS['import-step'][2] == 'step'`; `cli.py`,
  `manager/import_step.py`, `manager/snapshot.py` and `manager/new.py` spell no
  `machinome.node.<type>` module; importing `machinome.node.supported` imports
  no node-type module; the module defines only the table, `DEFAULT_RENDERER`,
  `NodeType` and `load`, `renderer`, `needed_by`. Red: no module.
- [ ] 2.13 `tests/test_manager_new.py`: with all extras, today's expected text
  unchanged; with `solid2` blocked, the CadQuery template; with `solid2` and
  `cadquery` blocked, R8 on standard error, exit 1, no directory created. Red:
  today always the Solid2Node template, and with SolidPython absent the command
  writes a project that cannot import.
- [ ] 2.14 `Sim(meshes=True)` does not call `assemble()` (patched to raise) and
  still builds every rigid STL. Red: it calls `assemble()`.
- [ ] 2.15 Run every test of this group and record in `evidence.md` each failing
  assertion and its message. Proves: red first.

## 3. The table and the declared set (no SCAD moves yet; the suite stays runnable)

- [ ] 3.1 `machinome/node/supported.py` per design.md Decision 6: `NodeType`,
  `NODE_TYPES`, `DEFAULT_RENDERER`, `load(key)` (refusing a module that cannot
  be found with `ExtraUnavailable(key, 'the <key> node type (<classes>)',
  'machinome.node.<key>')`, passing a module's own `ExtraUnavailable`
  unmodified), `renderer(name)` (importing the provisional column's module
  through `load`'s refusal rules) and `needed_by(command)`. Proves: 2.12's table
  part green.
- [ ] 3.2 `machinome/node/__init__.py`: the export table keeps its non-node names
  and takes each node type's class names from `NODE_TYPES`; its docstring lists
  no technology. Proves: `test_node_lazy_exports.py` green unchanged, 2.12's
  export part green.
- [ ] 3.3 Rename `as_scad` to `present` on the node base, `LeafNode`,
  `InternalNode`, `FlexibleNode` and the leaves; make `LeafNode.present` the
  default of design.md Decision 4b and delete the identical overrides in
  `exact_leaf.py`, `stl.py`, `jscad.py`; rename `_model_for_own_scad` to
  `presentation()`; add `kept_artifacts()` returning `()` on the node base;
  rename the tests' calls and overrides in the same step. Proves: the suite
  green with the renames; 2.6's `present` and `kept_artifacts` parts green.
- [ ] 3.4 Replace the fourteen probe sites of design.md Decision 5 with direct
  reads; add `tests/stand_in.py` (the set's defaults for duck-typed stand-ins)
  and derive every stand-in the suite's run reports from it
  (`test_assertions.py`, `test_broad_phase_culling.py`,
  `test_builder_lifecycle.py`, `test_connectivity.py`,
  `test_intersection_memo.py`, and whatever else fails with an
  `AttributeError` on a member of the set). Proves: 2.6's AST scan green, the
  suite green.
- [ ] 3.5 `LeafNode`'s docstring lists the declared members of the
  `leaf-contract` delta, and `CONTRACT = 2` with the comment naming what
  changed. Proves: 2.6 green; `test_leaf_contract*.py` repointed to 2.

## 4. The OpenSCAD family as a node package, and the core without it

- [ ] 4.1 Create `machinome/node/openscad/` in one step with the deletion of
  `machinome/node/openscad.py`: `__init__.py` (`require_extra('openscad',
  'machinome.node.openscad (OpenScadNode and the OpenSCAD writer)', 'solid2')`
  first, then `OpenScadNode` as today, over `ScadLeafNode`), `leaf.py`
  (`ScadLeafNode` with `fn`, `scad_file`, `scad_code`, `generate_scad()`,
  `present`, `materialize`, `generate_stl()` and `stl_builder_command(_for)`
  moved from `node/base.py`, and `kept_artifacts()`), `writer.py` (`scad_text`
  moved from `machinome/openscad/engine.py`, `scad_code(node)`,
  `generate_scad(node)` moved from `node/base.py`'s `generate_scad` and
  `_publish_scad`, without the coalescing branch), `binary.py` (moved from
  `machinome/openscad/binary.py`, `OpenScadUnavailable` deriving from
  `RuntimeError`, its message unchanged). Proves: 2.2's package part green.
- [ ] 4.2 `machinome/node/solid2.py`: `require_extra('solid2',
  'machinome.node.solid2 (Solid2Node)', 'solid2')` first; `Solid2Node` over
  `ScadLeafNode` with `as_number` on the package's binary; `adopt` moved from
  `machinome/openscad/engine.py`, registered with
  `machinome.expression_graph.register_adopter` at import. Proves: 2.3's R2
  part, 2.10 green.
- [ ] 4.3 `machinome/expression_graph.py`: `register_adopter` and the adopters
  tuple; `symbolic` asks them after numbers, `GraphValue` and `ExpressionNode`;
  no import of a seam. `machinome/math.py` unchanged in behaviour. Proves:
  2.10 green; `test_expression_type.py`, `test_math.py`, `test_expressions.py`
  green.
- [ ] 4.4 `machinome/currency.py` gains `publish_text` (moved from
  `node/base.py`'s `_atomic_write_text`, unchanged) and the transient mark:
  `record` and `publish` take `transient=False`, a transient record carries
  `"transient": true`, `_recorded_source` tolerates the key,
  `recorded_transient(artifact)` answers it, `publish_text` passes it through.
  The writer uses them.
  Proves: `test_coarse_filesystem_freshness.py` and the "Unchanged text is not
  replaced" test green.
- [ ] 4.5 `node/base.py`: the SCAD members, `fn`, `mesh_scad_file`,
  `scad_authored`, `_scad_engine_for`, `_require_scad_engine`,
  `_publish_scad`, `_uses_legacy_scad_materialization` and
  `_render_can_be_skipped` removed; `_prepare` calls `materialize` only;
  `generate_stl` keeps its three early returns and raises
  `ArtifactNotProduced` (R7). `node/leaf.py`, `node/flexible.py`,
  `node/sheet_leaf.py`: their `scad_authored`, legacy and
  `_render_can_be_skipped` members removed. `model.py:487-489`: the legacy
  branch removed. `parameters._RESERVED` drops `scad_file` and
  `mesh_scad_file`. Proves: 2.7 green; the suite green.
- [ ] 4.6 `machinome/viewers/openscad.py`: imports
  `machinome.node.openscad.writer` and `.binary` directly; `require_engine`
  removed; `present(node)` assembles the root and has the writer publish its
  `.scad`, transient unless the root lists it in `kept_artifacts()`;
  `withdraw` keeps a file the root lists in `kept_artifacts()`;
  `render` takes the OpenSCAD branch of `manager/snapshot.py:224-245` with
  its messages verbatim. Proves: `test_snapshot.py`'s renderer tests green
  repointed.
- [ ] 4.7 `core/builder.py`: `collect_scad` becomes `collect_kept` over
  `kept_artifacts()` and `children`; `scad_only` removed; the unchanged-document pass
  becomes the transient pass, run on every successful build: every file whose
  record `recorded_transient` answers is removed with its record; the
  changed-document sweep is otherwise as before. Proves: 2.8 green.
- [ ] 4.8 Delete `machinome/openscad/` and `machinome/scad_engine.py`. Proves:
  2.2 and 2.3 green; `grep -rn "scad_engine\|machinome.openscad" machinome/`
  finds only `machinome.node.openscad`.

## 5. The source generation

- [ ] 5.1 `source_generation.py`: remove `_PendingScadPublication`,
  `coalesces_scad`, `_pending_scad`, the pre-flush/post-flush branch of
  `__exit__`, `pending_scad_count`, `defer_scad`, `_flush_scad`; rename
  `_scad_artifacts`, `has_scad_artifact`, `remember_scad_artifact` to
  `_published`, `has_published`, `remember_published`; the writer uses them.
  Proves: 2.9 green; `test_source_generation.py`, `test_retained_builder_generation.py`
  green.

## 6. Commands and callers

- [ ] 6.1 `manager/snapshot.py`: `--renderer` from the table; the renderer
  resolved through `supported.renderer` before loading, R4 on `ExtraUnavailable`;
  `node.assemble()` only through the table renderer's `present`; help texts
  without the technology's name; the OpenSCAD error branch gone to the viewer
  module. Proves: 2.5 green; the snapshot suite green.
- [ ] 6.2 `simulation/sim.py:215-216, 231-232`: drop `node.assemble()`.
  Proves: 2.14 green; `test_sim*.py` green.
- [ ] 6.3 `cli.py`: `COMMANDS['import-step']`'s third column is `'step'`;
  `require_needed_module` loads it through `supported.load`, message unchanged;
  `manager/import_step.py` takes `StepAssembly` from `supported.load('step')`.
  Proves: 2.12's CLI part, `test_cli_lazy_imports.py`, `test_import_step.py`
  green.
- [ ] 6.4 `manager/new.py` and the templates: `root/__init__.py` becomes
  `root/solid2.py` (byte-identical) and `root/cadquery.py`; the command picks
  `solid2`, then `cadquery`, through `supported.load`, and refuses with R8.
  Proves: 2.13 green.
- [ ] 6.5 Repoint the goldens' scripts: `tests/scad_presentation_golden.py` and
  `tests/expression_type_golden.py` read non-family nodes' text through
  `machinome.node.openscad.writer.scad_code(node)`; their JSON files are not
  re-recorded. Proves: both `--check` green with no difference.

## 7. Dependencies

- [ ] 7.1 `pyproject.toml`: `solidpython2` leaves `dependencies`; extras
  `openscad = ["solidpython2==2.1.*"]` and `solid2 = ["machinome[openscad]"]`;
  `all` adds both; the comments name them. `setup.cfg`: E402 ignored for
  `machinome/node/openscad/__init__.py` and `machinome/node/solid2.py`.
  `requirements.txt` keeps SolidPython for CI. Reinstall the bench editable only
  if the metadata test reads installed metadata (record which). Proves: 2.4
  green.

## 8. The wording: the gate green

- [ ] 8.1 Reword every remaining offender of the gate without changing
  behaviour: `math.py`, `expression_graph.py` (its docstring as machinome's
  expression language), `core/expressions.py` (`scad_expression` →
  `closed_expression`, its two callers, the docstrings), `core/expression_parser.py`,
  `node/presentation.py`, `node/internal.py`, `node/operations.py`,
  `node/qualified.py`, `node/sources.py`, `node/assembly.py`,
  `node/build123d.py`, `node/cadquery.py`, `node/decorators.py`,
  `node/exact_leaf.py`, `node/stl.py`, `node/jscad.py`, `node/sheet_leaf.py`,
  `core/camera.py` (`OPENSCAD_FOV` → `DEFAULT_FOV`), `core/pieces.py`,
  `motion/couplings.py` (`cascade`), `motion/joints.py`, `parameters.py`,
  `test.py`, `viewers/browser.py` (its two docstrings and the suggestion read
  from `DEFAULT_RENDERER`, design.md Open Question 10), `manager/snapshot.py`'s
  remaining help and comments. Proves: 2.1 green, 2.11 green.

## 9. Test repointing

- [ ] 9.1 Repoint the 48 test files design.md Decision 15 lists (47 of the 105
  that mention the word, and `test_manager_new.py`), as that decision sorts
  them:
  `test_openscad_engine.py` and `test_scad_engine_seam.py` become
  `test_openscad_node.py` cases or are deleted where they test the seam's
  resolution, which no longer exists; the fixtures overriding `as_scad`
  (`tests/scad_where_read_project/legacy.py`,
  `tests/contract_package/scad_stand_in.py`) become `Solid2Node` subclasses or
  the R7 fixture; `test_openscad_dependency.py` keeps its messages. The 58 that
  only use `Solid2Node`/`OpenScadNode` as fixtures or mention the word stay
  unchanged. Proves: the whole suite green (task 11.1).

## 10. Docs

- [ ] 10.1 `docs/architecture.md`: the OpenSCAD family as a node package, the
  table of supported node types (provisional, the viewer cycle), the declared
  capability set, the presentation, the source map. `docs/start/install.rst`:
  SolidPython leaves the plain install; the `openscad` and `solid2` extras;
  `machinome new`'s templates; the OpenSCAD snapshot needs `[openscad]`.
  `docs/howto/backends.rst` (the node types and their extras),
  `docs/reference/cli.rst` (`snapshot`'s renderer and refusal, `new`'s
  templates), `docs/reference/api.rst` (`LeafNode`'s members,
  `machinome.node.openscad`, `machinome.node.solid2`), `docs/concepts/publishing.rst`
  (`.scad` kept by declaration), `docs/project/upgrading.rst` (the extras, the
  removed names, a leaf overriding `as_scad`), `README.rst` (the default
  template's requirement). Proves: `test_docs_exports.py` and the docs build
  test green; `grep -rn "scad_engine\|machinome.openscad\b\|as_scad" docs/`
  outside the ADRs and the changelog's history finds nothing.
- [ ] 10.2 The changelog's Unreleased section gains this cycle's bullet, written
  in this cycle: what moved, the two extras, BREAKING notes of proposal.md.
  Proves: the changelog test green.

## 11. The campaign plan, and the checkpoint

- [ ] 11.1 Run the whole suite, one process; record counts and time in
  `evidence.md`; run the three goldens' `--check` again. Proves: green, bytes
  unchanged.
- [ ] 11.2 `workflow/ongoing/lean-core.md`: the cycle's entry under "The next
  phase" and the validation table, marked in progress with the evidence
  pointer; the viewer cycle recorded as the phase's last by the pilot's
  decision. Proves: the plan names this cycle's state.
- [ ] 11.3 **Stop before any commit and report to the orchestrator**: the suite
  result, the goldens, the gate's count (zero), and the evidence file. The
  applier spawns no agent and runs no project.

## 12. Empirical validation (the orchestrator runs every leg; the applier waits)

- [ ] 12.1 `Locks/Pin_tumbler_lock`, deep: before (a16d45a) and after, fresh
  build directories: the 11 `parts-*.scad` SHA-256 identical; `machinome test
  --faceted` verdict log byte-identical (2573 verdicts, 24/24); `manifest.json`
  identical but OpenSCAD's STL noise; an OpenSCAD snapshot's root `.scad`,
  captured before removal, byte-identical (6916 bytes, 20 imports) and gone
  after; the image written.
- [ ] 12.2 `3D-Printers/Prusa3-vanilla`, deep: 16 passed, 3 failed
  (pre-existing) before and after, its 15935 verdicts byte-identical.
- [ ] 12.3 OpenAstroMount with `solid2`, `machinome.node.openscad` and
  `machinome.node.solid2` unfindable and an audit hook on imports: build writes
  90 STL, 90 BREP, zero `.scad`; no import of the three attempted; `machinome
  test` 8/9 as before; `machinome snapshot` prints R4, exit 1.
- [ ] 12.4 The three goldens in fresh processes, and `machinome new` in
  throwaway directories under all extras (Solid2Node template byte-identical,
  build and test green), `solid2` blocked (CadQuery template, build and two
  tests green with `[manifold]`), both blocked (R8, nothing created).
- [ ] 12.5 The universe: `scripts/load-projects` with the seven earlier tables
  and this change's `moved-names.toml`, 300 s timeout; expected the mesh-engine
  sweep's rows unchanged (117 ok, 4 expected, 2 unexpected pre-existing, 6
  no-model), no row for this change.
- [ ] 12.6 The orchestrator's greps over `projects/`: files importing from
  `solid2` without importing `Solid2Node`; classes declaring `fn` or
  `optimize = False` outside the family; any `as_scad`, `scad_code`,
  `generate_scad`, `scad_file`, `scad_authored`; and machinome-mechanics'
  suite on its `v0.8` branch against the bench, whose twelve SolidPython-time
  files are expected to fail as design.md Open Question 3 says.
- [ ] 12.7 The applier folds the orchestrator's reports into `evidence.md`.

## 13. Records, specs, archive, commit (the applier, after 12)

- [ ] 13.1 ADRs per design.md "ADRs": ADR-177 (NODE), ADR-178 (NODE), ADR-179
  (BUILD, provisional), each linking the archived change; the status lines of
  ADR-171 (superseded), ADR-172, 173, 086, 046, 103, 102, 163, 165, 167, 168
  amended; `docs/adrs/README.md` indexed. Proves: the ADR index test green.
- [ ] 13.2 `openspec validate openscad-out --strict`; `openspec archive
  openscad-out --yes`; then `git rm -r openspec/specs/openscad-engine
  openspec/specs/scad-engine-dependency` (design.md Decision 12) and check that
  no spec under `openspec/specs/` names either; update the `Purpose` of
  `kernel-extras` (its code list) by hand; `openspec validate --specs
  --strict`. Proves: specs synced, the two capabilities removed, validation
  green.
- [ ] 13.3 Copy the archived `moved-names.toml` path into `evidence.md` for the
  orchestrator, who copies it to the workspace's
  `scripts/load-projects.d/openscad-out.toml`. Proves: the table is where the
  next sweep reads it.
- [ ] 13.4 The campaign plan's entry marked done with the evidence pointer;
  the final suite run; commit the completed state on the branch (no amend), and
  report base, commit, suite and validation results.
