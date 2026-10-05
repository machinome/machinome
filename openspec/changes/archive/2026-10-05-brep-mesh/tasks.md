## 1. Evidence baseline on the unmodified tree

- [x] 1.1 Create `openspec/changes/brep-mesh/evidence.md` in the shape of the
  archived cycles' (`2026-10-04-openscad-out/evidence.md`), with the bench
  commit (faf1c80), and record there the facts design.md rests on,
  re-measured: the gate's red count (`python3
  openspec/changes/brep-mesh/gate-prototype.py .`; expected 30 modules, 548
  occurrences, and its per-module list of design.md Decision 9); the shadowing
  probe of design.md "Context" (a package whose `__init__` defines `brep()`
  loses it to its submodule `brep` at the first import); the 312 / 196 / 116
  counts of the word `exact` in the core's text; the 78 test files naming a
  moved name (77 for the split's words, `test_tutorial_counter.py` for
  `SOLID_TEST_KERNEL`). Proves: the evidence the design cites exists in the
  change.
- [x] 1.2 Run, before any source change, each in a fresh process:
  `python tests/leaf_contract_golden.py --check`,
  `python tests/scad_presentation_golden.py --check`,
  `python tests/expression_type_golden.py --check`,
  `python tests/exact_engine_golden.py --check`,
  `python tests/mesh_engine_golden.py --check`; record that each passes.
  Proves: the five goldens hold on the base.
- [x] 1.3 Run, on the unmodified tree, one pytest process at a time, the
  touched suites: the 78 test files of 1.1 and `test_kernel_extras.py`,
  `test_core_kernel_free.py`, `test_leaf_capability_set.py`,
  `test_leaf_contract_version.py`, `test_manager_test.py`,
  `test_verdict_store.py`, `test_verdict_store_cli.py`,
  `test_vet_universe.py`, `test_docs_structure.py`; record counts and wall
  time. Proves: the touched suites' green baseline.

## 2. Red tests (each red on the unmodified tree for the reason given)

- [x] 2.1 `tests/test_core_names_no_split_words.py`, the gate of design.md
  Decision 9: the rule as functions with their own unit cases (W1 to W4, the
  ordinary identifiers passing only in their module, the four ordinary
  phrases, `exact-negative`, `exactly`, `exact-bytes`, `the exact set`
  passing) and the scan of `machinome/**/*.py` reporting each offending module
  with its count and first tokens. Red: 30 modules, 548 occurrences.
- [x] 2.2 `tests/test_engine_package.py`, item 2 of design.md Decision 15:
  the seams' names and constants in `machinome.engine`, no provider imported
  with the package, the seam functions surviving their providers'
  resolution, a portion directory resolving and a second core copy refused,
  the four former addresses raising `ModuleNotFoundError`, the package holding
  no operation. Red: no package; the former modules exist.
- [x] 2.3 The three doors for each engine, item 3 of Decision 15, with
  `tests/exact_engine_absent.py` and `tests/mesh_engine_absent.py` as they are
  (their refusal targets repointed in 3.4): R5 and R1 for the B-rep engine,
  R1 from a stale B-rep fusion's build; R6, R3 and `machinome test --mesh`
  exiting 1 before building for the mesh engine; each text verbatim from
  design.md Decision 13. Red: no such modules; the texts name `occt` and
  `manifold`.
- [x] 2.4 `tests/test_kernel_extras.py`, item 4 of Decision 15. Red: the
  extras are `occt` and `manifold`.
- [x] 2.5 The leaf base and capability, item 5 of Decision 15
  (`tests/test_leaf_capability_set.py`, `tests/test_leaf_contract_version.py`):
  `BrepLeafNode`, `brep`, `CONTRACT == 3`, `leaf_contract = 2` refused naming 2
  and 3, R24. Red: `ExactLeafNode`, `exact`, 2.
- [x] 2.6 The test framework, item 6 of Decision 15
  (`tests/test_manager_test.py` and the comparison-policy tests): `ENGINES`
  and no `KERNELS` in `machinome.test`, `ComparisonPolicy.engine` and no
  `.kernel`, `resolve_comparison_policy(engine=...)` and `kernel=` refused
  by Python, the default, `--brep`/`--mesh` into `args.engine`, the former
  flags unrecognised, `SOLID_TEST_ENGINE=mesh` selecting the mesh engine,
  the former values under `SOLID_TEST_ENGINE` refused with R7, the former
  variable `SOLID_TEST_KERNEL` refused with R30 whatever its value and
  whatever the flag (and `machinome test` exiting 1 with it before
  building), R31, R8, R11, R12, `IntersectionStats.brep`. Red: today's
  flags, values and names.
- [x] 2.7 The verdict paths, item 7 of Decision 15 (`tests/test_verdict_store.py`).
  Red: the path words are `'exact'`/`'faceted'`.
- [x] 2.8 The recipe identities and what rebuilds, item 8 of Decision 15
  (`tests/test_backend_neutral_materialization.py`). Red: the former
  identities.
- [x] 2.9 The memos and publication, item 9 of Decision 15. Red: the former
  modules exist.
- [x] 2.10 Vet, item 10 of Decision 15 (`tests/test_vet_universe.py`). Red:
  the denylist names the former addresses.
- [x] 2.11 Run every test of this group and record in `evidence.md` each
  failing assertion and its message. Proves: red first.

## 3. The engine package and the providers (one step: every importer moves with it)

- [x] 3.1 Create `machinome/engine/__init__.py` per design.md Decision 2: the
  two seams joined from `machinome/exact_engine.py` and
  `machinome/mesh_engine.py`, with the names of its table, `BREP_CONTRACT =
  2`, `MESH_CONTRACT = 1`, `_brep_absent` reading `extra == 'brep'` and
  `BREP_PROVIDER`, `_mesh_absent` reading `extra == 'mesh'` and
  `MESH_PROVIDER`, R1 to R4 verbatim, importing only `functools`,
  `importlib`, `typing`, `machinome.extras` and `_namespace_portions`, and
  ending with `__path__ = _namespace_portions(__path__, __name__)`.
- [x] 3.2 `git mv machinome/occt/engine.py machinome/engine/brep.py` and
  `git mv machinome/manifold/engine.py machinome/engine/mesh.py`; in them:
  `require_extra('brep', 'the B-rep engine (machinome.engine.brep)', 'OCP')`
  and `require_extra('mesh', 'the mesh engine (machinome.engine.mesh)',
  'manifold3d')`; the B-rep provider imports `BrepCommonInconsistency` and
  `BrepCommonVerificationError` from `machinome.engine` and declares
  `CONTRACT = 2`; R26 and R27 verbatim; the docstrings name their seam and
  their role. `git rm machinome/occt/__init__.py machinome/manifold/__init__.py
  machinome/exact_engine.py machinome/mesh_engine.py`, then `git clean -fdX
  machinome/occt machinome/manifold`, since a directory left holding only its
  ignored `__pycache__` imports as an empty namespace package (the plan's
  "Update at the eighth cycle's integration").
- [x] 3.3 Repoint every importer in the core in the same step:
  `exact_cache.py`, `exact_artifacts.py`, `test.py`, `manager/test.py`,
  `node/exact_leaf.py`, `node/fusion.py`, `node/cadquery.py`, `node/step.py`,
  `node/build123d.py` (`from machinome.engine import require_brep_engine`,
  `require_mesh_engine`, `mesh_engine`, `MeshEngineUnavailable`).
- [x] 3.4 Repoint the suite's importers of the four former modules, and the
  finder helpers' default refusal targets (`machinome.engine.brep`;
  `machinome.engine.mesh` and `manifold3d`), keeping their file names until
  task 8. Proves: 2.2 and 2.3 green; the suite green but for the other red
  tests of group 2.

## 4. The memos, the publication, the leaf base and the capability

- [x] 4.1 `git mv machinome/exact_cache.py machinome/brep_cache.py` and
  `git mv machinome/exact_artifacts.py machinome/brep_artifacts.py`; repoint
  their importers in the core (`test.py`, `manager/test.py`,
  `node/exact_leaf.py`, `node/fusion.py`, `node/leaf.py:178`,
  `node/build123d.py`) and the suite; R25 verbatim. Proves: 2.9 green.
- [x] 4.2 `git mv machinome/node/exact_leaf.py machinome/node/brep_leaf.py`;
  `ExactLeafNode` → `BrepLeafNode`; repoint `node/cadquery.py`,
  `node/build123d.py`, `node/step.py`, `node/sheet_leaf.py`, `node/flexible.py`
  and the suite (`contract_package/exact_stand_in.py` and its peers keep their
  file names, design.md Decision 12).
- [x] 4.3 The declared capability `exact` → `brep`: `node/base.py`,
  `node/internal.py` (R24), `node/brep_leaf.py`, `node/molejo.py`,
  `node/fusion.py`, `node/leaf.py` (its docstring's declared members),
  `node/flexible.py` (the declared member and the private `_brep_*` and
  `_mesh_cache_snapshot` names), `core/builder.py:725`, `test.py`; the suite's
  stand-ins (`tests/stand_in.py` and its users) declare `brep`. R21, R22, R23
  verbatim.
- [x] 4.4 `machinome.node.leaf.CONTRACT = 3`, its comment recording version
  3; the suite's declarations of `leaf_contract = 2` move to 3 where they
  declare the core's version. Proves: 2.5 green.

## 5. The test framework, the verdict store and fusion

- [x] 5.1 `machinome/test.py`: `KERNELS` → `ENGINES = ('brep', 'mesh')`
  (124); `ComparisonPolicy`'s field `kernel` → `engine` (119-122);
  `resolve_comparison_policy(kernel=None, ...)` → `engine=None` (132) and its
  docstring; `SOLID_TEST_KERNEL` → `SOLID_TEST_ENGINE` (190); the former
  variable refused with R30 before the engine is read (design.md Decision
  6); `comparison_policy().kernel` → `.engine` in `_routes_brep` and
  `_engine_reason` (236, 242); the default `'brep'`; R7, R8, R10, R31; the
  comments and docstrings that say the run's kernel (83-112, 138-149, and
  the rest by design.md Decision 17's prose rows, `kernel` in its library
  sense kept); the path words in `_verdict_key`/`_record_key`
  callers, `_persistent_identity` and `_engine_identity`,
  `IntersectionStats.brep`, the private renames of design.md Decision 6, R13
  to R18 verbatim.
- [x] 5.2 `machinome/manager/test.py`: `--brep`/`--mesh` with R28's help
  (the `--placement-quantum` help's "both engines" included), the group
  variable `kernel` → `engine` and `dest='kernel'` → `dest='engine'`
  (64-71), `getattr(args, 'kernel', None)` → `getattr(args, 'engine', None)`
  (102), `self.policy.kernel` → `self.policy.engine` (110) and
  `policy.kernel` → `policy.engine` (329), the start-of-run refusal R9, the
  line R11, the summary note R12, the default policy
  `ComparisonPolicy('brep', 0.0)` (327). Proves: 2.6 green.
- [x] 5.3 `machinome/_verdict_store.py`: `_EXACT` → `_BREP` (bit 2),
  `record(..., brep)`, the index tuple, the docstrings; `FORMAT_VERSION`
  unchanged. Proves: 2.7 green; `test_verdict_store*.py` green.
- [x] 5.4 `machinome/node/fusion.py`: `geometry_recipe` returns
  `'brep-fusion-v1'` and `'mesh-fusion-v1:' + digest`;
  `_generate_faceted_stl` → `_generate_mesh_stl`; R19 and R20 verbatim.
  Proves: 2.8 green.

## 6. The extras and vet

- [x] 6.1 `pyproject.toml` per design.md Decision 10 (`brep`, `mesh`, the
  four node extras including `machinome[brep]`, `all`, the comments);
  `requirements.txt`'s comment; `setup.cfg`'s E402 ignores for
  `machinome/engine/brep.py` and `machinome/engine/mesh.py`;
  `machinome/extras.py`'s docstring. Reinstall the bench editable only if
  the metadata test reads installed metadata (record which). Proves: 2.4
  green.
- [x] 6.2 `machinome/vet/universe.toml`: the denylist's
  `machinome.brep_cache`, `machinome.brep_artifacts`,
  `machinome.engine.brep.read_brep`, `.write_brep`, `.write_stl`, and its
  comments. Proves: 2.10 green.

## 7. The wording: the gate green

- [x] 7.1 Reword every remaining offender of the gate without changing
  behaviour, from the rename table (design.md Decision 17) and the refusal
  texts (Decision 13): the docstrings and comments of every module of the
  red count, `core/processes.py` and `manager/import_step.py` without the
  library's name (Open Question 4), `simulation/__init__.py`,
  `motion/couplings.py`, `motion/joints.py` ("no B-rep stack"),
  `node/__init__.py`'s docstring (the engine package). Proves: 2.1 green.
- [x] 7.2 List every remaining word `exact` (case-insensitive, not
  `exactly`) in `machinome/` with its module, line and reading (ordinary, or
  the split's and rewritten), in `evidence.md`, and rewrite any of the
  split's that the gate does not see (design.md Decision 9, "What the gate
  does not see"). Proves: no split predicate survives the gate's blind spot.

## 8. The tests: renamed modules and repointed goldens

- [x] 8.1 `git mv` the test modules and helpers of design.md Decision 12 to
  their new names, `tests/data/exact_engine_golden.json` to
  `tests/data/brep_engine_golden.json` (bytes unchanged), the helper's
  variables `EXACT_ENGINE_ABSENT(_LOG)` to `BREP_ENGINE_ABSENT(_LOG)`; repoint
  every importer of a renamed helper. The fixture projects keep their names.
- [x] 8.2 Repoint the remaining test files of the 78 by the rename table:
  `test_core_kernel_free.py` (the providers' paths, the seam module; its own
  `KERNELS`, library names, keeps its name), `test_cli_lazy_imports.py`,
  `test_node_lazy_exports.py`, the docs tests; the run's variable and
  argument (`SOLID_TEST_KERNEL` → `SOLID_TEST_ENGINE`, `kernel=` →
  `engine=`, `.kernel` → `.engine`, `args.kernel` → `args.engine`) in
  `test_manager_test.py`, `test_verdict_store.py` (its `set_policy`),
  `test_meta.py`, `test_flexible_verdict_identity.py`, `test_markings.py`,
  `test_mesh_engine_dependency.py`, `test_exact_placement_cache.py`,
  `mesh_engine_golden.py:161` and `test_tutorial_counter.py:27` (which clear
  `SOLID_TEST_ENGINE`); and whatever else the suite's run reports.
- [x] 8.3 `tests/mesh_engine_golden.py`: its kernel loop runs `--mesh` and
  `--brep`, and its check reads the recorded `'faceted'`/`'exact'` keys and
  path words, the summary note and the mesh fusion's refusal through
  `BREP_MESH_EXPECTED` (design.md Decision 12); `brep_engine_golden.py`
  imports `machinome.engine.brep` and `machinome.brep_cache`. No JSON is
  re-recorded. Proves: the five goldens `--check` green with no difference.

## 9. Docs

- [x] 9.1 Read `skills/write-the-manual/SKILL.md` (the workspace's), then
  rewrite the pages of design.md Decision 14: `docs/architecture.md` (the
  run's engine and `SOLID_TEST_ENGINE`, 2314), the
  install, fast-tests (`SOLID_TEST_ENGINE=mesh` in `.env`, the run's engine
  wherever it says kernel), backends, fusion, imported-parts, flexible-parts,
  markings and sheet-parts how-tos, the CLI (`SOLID_TEST_ENGINE` at 159 and
  570), API and assertions references,
  the concepts and tutorial pages that use the words, `docs/why.rst`,
  `README.rst`, and `docs/project/upgrading.rst` (the flags, the variable
  `SOLID_TEST_ENGINE` and the refusal of `SOLID_TEST_KERNEL`, the extras, the
  moved names, the verdict recompute, the mesh fusion rebuild, the
  `__pycache__` cleaning, `.env` files). Proves: the docs tests and the docs
  build green; `grep -rn "machinome\.occt\|machinome\.manifold\|exact_engine\|mesh_engine\b\|--faceted\|--exact\b\|ExactLeafNode\|machinome\[occt\]\|machinome\[manifold\]\|SOLID_TEST_KERNEL" docs/ README.rst`
  outside the ADRs, `docs/releases/`, `docs/performance-improvement.md` and
  the changelog's released sections finds nothing.
- [x] 9.2 The changelog's Unreleased section: this cycle's bullet, written in
  this cycle (what is renamed, the BREAKING notes of proposal.md, the
  recompute and the rebuild), and, as Open Question 5 recommends unless the
  pilot rules otherwise at ratification, the earlier Unreleased bullets
  revised to the names 0.8 ships. Proves: the changelog test green.
- [x] 9.3 The ADR index (`docs/adrs/README.md`) gains no entry yet (task
  12.1); nothing else under `docs/adrs/` changes.

## 10. The campaign plan, and the checkpoint

- [x] 10.1 Run the whole suite, one process; record counts and time in
  `evidence.md`; run the five goldens' `--check` again; run
  `gate-prototype.py` and record zero. Proves: green, bytes unchanged.
- [x] 10.2 `workflow/ongoing/lean-core.md`: this cycle's entry under "The next
  phase" marked in progress with the evidence pointer, and the follow-ups the
  campaign owes outside the framework (the studio's `machinome_test` tool and
  skills, `SOLID_TEST_KERNEL` in its `machinome-api` skill included, the
  workspace's simulate-project skill, `brep-mesh.toml` for
  `scripts/load-projects.d/`). Proves: the plan names this cycle's state.
- [x] 10.3 **Stop before any commit and report to the orchestrator**: the
  suite result, the goldens, the gate's count (zero), the residual review of
  7.2, and the evidence file. The applier spawns no agent and runs no
  project.

## 11. Empirical validation (the orchestrator runs every leg; the applier waits)

- [x] 11.1 `Locks/Pin_tumbler_lock`, deep, design.md Decision 16: `--faceted`
  before, `--mesh` after, `--no-verdict-store`: 24 tests, 2573 verdicts
  identical but for the path word; the line and the note per R11 and R12;
  then two runs with the store on: the first serves nothing kept before the
  change, the second serves what the first kept.
- [x] 11.2 `3D-Printers/Prusa3-vanilla`, deep: 16 passed, 3 failed
  (pre-existing) before and after, 15935 verdicts identical but for the path
  word.
- [x] 11.3 OpenAstroMount, deep: `--exact` before, `--brep` after, the same
  outcomes (8/9) and verdicts but for the path word; with the mesh engine
  unfindable, the same outcomes before and after; `machinome build` after the
  change rebuilds nothing (90 STL, 90 BREP).
- [x] 11.4 One project with a mesh `FusionNode` (else the golden's `Fused`):
  the fused STL rebuilds once, byte-identical, its recorded recipe
  `mesh-fusion-v1:<same digest>`; a second build reuses it; a B-rep fusion is
  not rebuilt.
- [x] 11.5 The five goldens in fresh processes; the three doors for each
  engine with the finder helpers; a stub portion
  `machinome/engine/probe.py` importable from a temporary directory.
- [x] 11.6 The universe: `scripts/load-projects` with the eight earlier tables
  and this change's `moved-names.toml`, 300 s timeout; expected: no new
  unexpected row; every row that was `ok` and fails is `expected` by a row of
  this table, their number the grep count of 11.7; 6 no-model.
- [x] 11.7 The orchestrator's greps over `projects/` (design.md Decision 16's
  list, `.env` files included) and machinome-freecad's validation branch.
- [x] 11.8 The applier folds the orchestrator's reports into `evidence.md`.

## 12. Records, specs, archive, commit (the applier, after 11)

- [x] 12.1 ADR-180 (NODE) per design.md "ADRs", linking the archived change;
  the status lines of ADR-073 (the run's comparison kernel is its engine),
  160, 161, 162, 163, 165, 167, 176 and 178 amended ("amended by 180");
  `docs/adrs/README.md` indexed. Proves: the ADR index test green.
- [x] 12.2 `openspec validate brep-mesh --strict`; `openspec archive brep-mesh
  --yes`; then `git rm -r openspec/specs/exact-engine-dependency
  openspec/specs/exact-geometry openspec/specs/occt-engine
  openspec/specs/manifold-engine` (design.md Decision 11) and check that no
  spec under `openspec/specs/` names any of the four.
- [x] 12.3 Rename the scenario titles of `scenario-titles.tsv` (74 rows) in
  `openspec/specs/<spec>/spec.md`, each `#### Scenario: <old>` line to
  `#### Scenario: <new>`, every occurrence in its spec, by a script that
  fails when a row's old title is not found; write the Purposes of design.md
  Decision 11 (the four new specs, `kernel-extras`, `leaf-contract`,
  `mesh-engine-dependency`, `step-import`, `test-framework`); `openspec validate --specs
  --strict`. Proves: the baseline specs carry the new words and validate.
- [x] 12.4 Copy the archived `moved-names.toml` path into `evidence.md` for the
  orchestrator, who copies it to the workspace's
  `scripts/load-projects.d/brep-mesh.toml`.
- [x] 12.5 Check that `machinome/occt` and `machinome/manifold` are gone from
  the bench (task 3.2); the final suite run; the campaign plan's entry marked
  done with the evidence pointer;

  commit the completed state on the branch (no amend), and report base,
  commit, suite and validation results.
