## 1. Baseline on the unmodified tree

- [x] 1.1 Create `openspec/changes/lean-install/evidence.md` in the shape of
  the archived cycles' (`2026-10-03-backend-switch/evidence.md`), with the
  bench commit.
- [x] 1.2 The markings golden: write `tests/markings_golden.py`, which builds
  a marking fixture of `tests/test_markings.py` (one `Wrapped` and one `Flat`
  marking with holes, one with `scale`) in a temporary build directory and
  writes `tests/data/markings_golden.json`: each marking artifact's SHA-256,
  and the region count and triangle count of each artwork. Run it twice in
  separate processes, record that both agree, record the bench commit in the
  JSON. A characterization, green before and after by design (`--check` after
  the change).
- [x] 1.3 Run the golden of the first cycle, `tests/exact_engine_golden.py
  --check`, and record it green on the unmodified tree.
- [x] 1.4 Run, on the unmodified tree, `tests/test_node_lazy_exports.py`,
  `tests/test_core_kernel_free.py`, `tests/test_exact_engine_seam.py`,
  `tests/test_cli_lazy_imports.py`, `tests/test_import_step.py`,
  `tests/test_markings.py`, `tests/test_vet_universe.py`,
  `tests/test_machinome_identity.py`, `tests/test_leaf_contract_reach.py`;
  record counts and wall time.
- [x] 1.5 Re-run design.md's probes from scratch scripts outside the bench
  (none committed): the dissolved-package probe (a scratch package: Python's
  own error without a file, the `ImportError` through a refusing
  `__init__.py` for the three spellings); the path-extension probe (in the
  bench, `pkgutil.extend_path` on `machinome.__path__` appends the primary
  checkout and `import machinome.exact` then resolves to
  `/home/asa/devel/machinome/machinome/machinome/exact.py`); `find_spec` of the
  four kernels importing none of them. Record each verbatim.

## 2. Red tests

- [x] 2.1 `tests/test_kernel_extras.py`, metadata: the required dependencies
  name none of `cadquery`, `build123d`, `ocp-gordon`, `molejo`,
  `cadquery-ocp` and still name `manifold3d` and `watchdog`; the extras
  `occt`, `cadquery`, `build123d`, `step`, `molejo`, `all` exist with the
  requirements of design.md Decision 3; each of the four kernel extras
  includes `machinome[occt]`; `all` names all five; `dev` includes
  `machinome[all]`; every requirement naming `cadquery` has the specifier
  `==2.7.*`; `requirements.txt` names every concrete requirement of `all`;
  `tox.ini`'s `[testenv]` declares `extras = all`. Red: the kernels are
  required and the extras absent.
- [x] 2.2 Generalise `tests/exact_engine_absent.py`: `run_python` and
  `run_machinome` take `absent=('machinome.occt',)`, the finder refusing every
  listed name and its submodules (environment variable, comma-separated), the
  default unchanged so every existing caller is untouched. Add a second mode,
  `broken=(...)`, whose finder returns a spec whose loader raises
  `ImportError('broken <name>')`, for the broken-kernel pins.
- [x] 2.3 In `tests/test_kernel_extras.py`, the refusals by subprocess with
  the blocker: importing `machinome.node.cadquery` with `cadquery` absent,
  `machinome.node.build123d` with `build123d` absent, `machinome.node.step`
  with `cadquery` absent and with `OCP` absent, `machinome.node.molejo` with
  `molejo` absent, `machinome.occt.engine` with `OCP` absent: each raises
  `ModuleNotFoundError` whose `name` is the blocked module, whose `extra` is
  the module's extra, and whose message is design.md Decision 4's sentence;
  importing `machinome.node.cadquery` and `machinome.node.build123d` with
  their kernels installed leaves `cadquery` and `build123d` out of
  `sys.modules`; `machinome.node.step` with `cadquery` broken raises
  `ImportError('broken cadquery')`, not the refusal. Red: the modules do not
  exist at those addresses.
- [x] 2.4 The three doors and the engine:
  - `tests/test_node_lazy_exports.py`: `from machinome.node import StepNode`
    with `cadquery` absent raises the step refusal unmodified (no "raised
    resolving"), `hasattr(machinome.node, 'StepNode')` raises it; with
    `cadquery` broken the underlying error is raised spliced, naming
    `StepNode` (the `cli-startup-cost` scenarios); `EXPECTED_EXPORTS` targets
    `machinome.node.<x>`; the submodule probe reads `cadquery`;
    `CheckCQEditor` from `machinome.node.cadquery`; the test asserting that
    cadquery is a required dependency in its docstring is corrected.
  - `tests/test_exact_engine_seam.py`: with `OCP` absent (blocker),
    `exact_engine()` is `None` and `require_exact_engine('exact fusion
    Bracket', 'fusing its exact children')` raises `ExactEngineUnavailable`
    naming `pip install "machinome[occt]"`; with `OCP` broken the import
    error propagates.
  - `tests/test_cli_lazy_imports.py` and a CLI subprocess test (via
    `run_machinome(..., absent=('cadquery',))`): `machinome import-step
    <tests' simple STEP> --into <tmp>/sim` exits 1, standard error is design.md
    Decision 7's line naming `import-step` and `pip install "machinome[step]"`,
    no `Traceback`, `<tmp>/sim` not created; `machinome import-step -h` the
    same; `machinome -h` exits 0, lists `import-step`, and imports no
    `machinome.node.step`; `machinome viewer` imports no module under
    `machinome.node`; `RegistryConformanceTest` unpacks three columns and
    checks every `needs` module imports. `test_import_step.py`'s
    `test_the_kernel_missing_is_a_checked_failure` is replaced by the
    subprocess test.
  Red: the addresses, the extras and the `needs` column do not exist.
- [x] 2.5 The markings seam, `tests/test_markings.py`: with `build123d`
  absent (blocker), importing `machinome.node.markings` and creating a class
  with an `Svg` marking succeeds and imports no `build123d`; building that
  part with a stale marking raises `ModuleNotFoundError` naming the part's
  class, the attribute, the artwork file and `pip install
  "machinome[build123d]"`, writing no marking artifact; building it again
  after an unblocked build (current marking) succeeds with the artifact's
  observation unchanged; a stub `machinome.node.build123d` declaring
  `SVG_REDUCER_CONTRACT = 2`, and one declaring none, are refused naming 1,
  2 (or "none") and the module; the three `regions()` calls move to
  `machinome.node.build123d.svg_regions`. Red: `markings.py` imports
  build123d itself and has no seam.
- [x] 2.6 The AST rules, extending `tests/test_core_kernel_free.py`: imports
  of `cadquery`, `build123d`, `OCP`, `molejo`, `ocp_gordon` anywhere under
  `machinome/` only in `machinome/occt/`, `node/step.py` (`OCP`,
  `cadquery`), `node/build123d.py` (`build123d`), `node/molejo.py`
  (`molejo`); imports or string spellings of `machinome.node.{cadquery,
  build123d,step,molejo}` only where the `kernel-extras` requirement lists;
  in each of the five kernel modules a top-level `require_extra(...)` call
  precedes its first kernel import and its first import of another kernel
  module; each call's extra equals the last component of the module's
  address (`occt` for `machinome/occt/engine.py`). Red: `markings.py`
  imports build123d and the modules have no call.
- [x] 2.7 The addresses, in a new `tests/test_leaf_addresses.py`: every row
  of the `node-model` table imports from its module and is the object the
  root resolves; `machinome/node/adapters/` holds only `__init__.py`; `from
  machinome.node.adapters.step import StepAssembly`, `from
  machinome.node.adapters import step` and `import
  machinome.node.adapters.cadquery` each raise `ImportError` naming
  `machinome.node.adapters` and `machinome.node.<x>`, in a fresh interpreter
  that afterwards holds no `machinome.node.step` or `machinome.node.cadquery`;
  `Build123dNode` and `Build123dSheetNode` are not instances of each other.
  Red: the modules are at the old addresses.
- [x] 2.8 The path extension, in `tests/test_leaf_addresses.py`: in a
  subprocess whose `sys.path` carries, after the bench, a scratch directory
  holding `machinome/__init__.py`, `machinome/node/__init__.py`,
  `machinome/stray.py` and `machinome/node/stray.py` (a second copy of the
  core), `import machinome.stray` and `import machinome.node.stray` fail; a
  scratch directory holding only `machinome/node/portion.py` and
  `machinome/extra_portion/__init__.py` (a satellite's shape, no
  `machinome/__init__.py`) makes `import machinome.node.portion` and `import
  machinome.extra_portion` succeed. Red: no extension today, so the
  satellite imports fail.
- [x] 2.9 Vet, `tests/test_vet_universe.py` or the vet suite's contract
  tests: a vetted module running `from machinome.node.cadquery import
  CadQueryNode` and `from machinome.node.step import StepAssembly,
  solids_from_faces` reports nothing. A characterization (vet judges by place
  in the universe): green before and after, said so in the evidence.
- [x] 2.10 Run 2.1 to 2.9 on the unmodified tree; record each failure and
  its reason in the evidence.

## 3. The addresses

- [x] 3.1 `git mv machinome/node/adapters/{cadquery,build123d,step,molejo,
  solid2,openscad,jscad,stl}.py machinome/node/`; fold
  `adapters/build123d_sheet.py` into `machinome/node/build123d.py`
  (`_PLANE_TOLERANCE`, `_export_dxf`, `Build123dSheetNode`), `git rm` it;
  rewrite the intra-package import in `step.py` to `machinome.node.cadquery`;
  correct the moved modules' docstrings that say "adapter module" or name
  `machinome.node.adapters`.
- [x] 3.2 `machinome/node/adapters/__init__.py`: licence header, a docstring
  saying the package was dissolved and why, and the `ImportError` of design.md
  Decision 2. Nothing else.
- [x] 3.3 `machinome/node/__init__.py`: `_EXPORTS` values lose `adapters.`;
  no `_MOVED` row; the docstring says where the leaf modules are.
- [x] 3.4 `machinome/manager/import_step.py`: the docstring's address;
  `handle()` imports `StepAssembly` from `machinome.node.step` (inside
  `handle`); remove `_load_step_assembly` and its `ImportError` handler.
- [x] 3.5 Run 2.7 and 2.9 green.

## 4. The extras and the kernel checks

- [x] 4.1 Write `machinome/extras.py` (design.md Decision 4):
  `ExtraUnavailable(ModuleNotFoundError)` with `extra`, `needed_by`, `name`
  and the sentence; `require_extra(extra, needed_by, *modules)` by
  `importlib.util.find_spec`, a finder's `ModuleNotFoundError` counting as
  absent and `ValueError` as present; it imports nothing else.
- [x] 4.2 The five calls of Decision 4's table, each the module's first
  statement after its docstring and stdlib imports, before any kernel import
  and before `step.py`'s import of `machinome.node.cadquery`.
- [x] 4.3 `machinome/node/__init__.py`'s `_load`: `except ExtraUnavailable:
  raise` before the `except ImportError` splice; the docstring says an
  absent extra is not a broken install.
- [x] 4.4 `machinome/exact_engine.py`'s `_absent`: also an
  `ExtraUnavailable` whose `extra` is `occt`; its docstring and
  `exact_engine()`'s say so.
- [x] 4.5 `pyproject.toml` (Decision 3): the four requirements leave
  `dependencies` with their comments moved to the extras; the extras
  `cadquery`, `build123d`, `step`, `molejo`, `all`; `dev` gains
  `machinome[all]`; the `occt` comment no longer says the pinned cadquery
  above requires its range; the `shapely` comment reads "installs, directly
  or through an extra". `requirements.txt` (Decision 11): the new header,
  `cadquery-ocp>=7.8.1,<7.9` added, the kernel lines under a comment naming
  their extras. `tox.ini`: `extras = all` in `[testenv]`. The CI workflow is
  unchanged; record that in the evidence.
- [x] 4.6 Run 2.1, 2.3, 2.4 (its node-root and engine parts) and 2.6 green.

## 5. The command table

- [x] 5.1 `machinome/cli.py` (Decision 7): `COMMANDS` values `(module,
  class_name, needs)`, `needs` `'machinome.node.step'` for `import-step` and
  `None` elsewhere; the table's comment explains the column; in `manage()`,
  once `selected` is known and before `resolve_command`, import its `needs`
  module and on `ExtraUnavailable` write `Error: machinome <command> needs the
  <extra> extra: <refusal>` to standard error and exit 1; any other import
  error propagates; the help path imports no `needs` module.
  `resolve_command` and every reader of `COMMANDS` unpack three columns.
- [x] 5.2 Run 2.4's CLI part green.

## 6. The markings seam

- [x] 6.1 `machinome/node/build123d.py`: `SVG_REDUCER_CONTRACT = 1`,
  `svg_regions(path)` and `svg_triangles(path, tolerance)` (design.md
  Decision 8), build123d imported inside them; the log line and both
  refusals unchanged.
- [x] 6.2 `machinome/node/markings.py`: `SVG_REDUCER_CONTRACT = 1`,
  `ArtworkReducerIncompatible`, `_artwork_reducer()`; `Svg.tessellate`
  through it, applying `scale`; `Svg.regions` removed; the module docstring
  and `Svg`'s say the reduction is `machinome.node.build123d`'s and needs the
  `build123d` extra.
- [x] 6.3 `AbstractBaseNode._build_markings`: the `ExtraUnavailable` rewrap
  naming the marking, the class and the artwork (Decision 8).
- [x] 6.4 Run 2.5 green and `tests/markings_golden.py --check` green.

## 7. The path extension

- [x] 7.1 `machinome/__init__.py`: `_namespace_portions(path, name)` and
  `__path__ = _namespace_portions(__path__, __name__)` (Decision 9), with a
  comment naming the filter's reason; `machinome/node/__init__.py`: the same
  call from `machinome`. Measure `import machinome` and `import
  machinome.node` with `-X importtime` before and after; record both.
- [x] 7.2 Run 2.8 green, and re-run 1.5's path probe: the bench's extended
  paths hold the bench alone and `import machinome.exact` fails.

## 8. Existing tests, the suite, the docs build

- [x] 8.1 Repoint the suites that name a moved address, without changing any
  asserted verdict, volume or message other than this change's:
  `test_backend_neutral_materialization.py`, `test_build123d_adapter.py`,
  `test_external_wrapper_identity.py`, `test_import_step.py`,
  `test_leaf_contract_reach.py` (its `ADAPTERS` directory becomes the four
  kernel modules' paths and the stand-ins; its allowance becomes `('step.py',
  'machinome.node.cadquery', 'workplane_shape')`), `test_missing_source_file.py`,
  `test_openscad_dependency.py`, `test_sheet_leaf.py`
  (`machinome.node.build123d._export_dxf`), `test_source_generation.py`,
  `test_source_set.py`, `test_step_assembly.py`, `test_step_node.py`,
  `test_stl_node.py`, `tests/step_project/parts.py`,
  `test_core_kernel_free.py`'s expectation, and any other the full run finds.
  List each in the evidence with what changed.
- [x] 8.2 Grep `machinome/`, `tests/` and `docs/` (ADRs and archived changes
  excepted) for `node.adapters`, `node/adapters`, `adapters.` and
  `pip install cadquery`; nothing may remain but the dissolved package's own
  refusal and this change's records.
- [x] 8.3 `tests/exact_engine_golden.py --check` green.
- [x] 8.4 Run the whole suite once, alone (it shares `tests/_build`; never
  two runs at once); record counts and wall time beside the backend-switch
  cycle's. Tests that skip by name when a kernel is absent: none (Decision
  11); record that none was added.
- [x] 8.5 `flake8 --max-line-length=89 machinome tests` on the changed files.
- [x] 8.6 Build the manual as the docs job does, from an environment with
  `docs/requirements.txt`'s packages and no kernel if one is at hand,
  otherwise the workspace venv: `python -m sphinx -E -b html -W docs
  docs/_build/html`; record which environment, and that the autodoc pages of
  `CadQueryNode`, `Build123dNode`, `Build123dSheetNode`, `StepNode` and
  `MolejoNode` render.

## 9. Documentation and the plan

- [x] 9.1 Under `skills/write-the-manual/SKILL.md` (workspace): red first,
  extend `tests/test_docs_structure.py` to refuse "Everything else comes with
  the package" and `machinome.node.adapters` on every reader-facing page and
  to require the six extras on `start/install.rst`; then `start/install.rst`
  (the rule stated once, the extras, the tutorial's route
  `machinome[viewer,cadquery]`), `README.rst` (the install block and its
  "needs nothing else" sentence), `tutorial/01-part.rst` (line 57),
  `howto/imported-parts.rst` (line 177). Pending design.md Open Question 1:
  if the orchestrator rules for the release rule, the extras go to
  `project/status.rst` instead and `install.rst` waits for 0.8.
- [x] 9.2 The changelog: one bullet in `docs/project/changelog.rst`'s
  Unreleased section: the leaf modules at `machinome.node.<x>` (root
  spellings unchanged; `machinome.node.adapters` refused naming the new
  address; `Build123dSheetNode` in `machinome.node.build123d`); a bare
  install carries no CAD kernel and the extras `cadquery`, `build123d`,
  `step`, `molejo`, `occt`, `all` install them, each module refusing an
  absent kernel with its install line; `import-step` names `machinome[step]`
  when absent; `Svg` artwork needs `machinome[build123d]` to build, a
  declaration none; no artifact byte changes (ADR-167, ADR-168, ADR-169). Not
  in `HISTORY.rst`.
- [x] 9.3 Amend the campaign plan `workflow/ongoing/lean-core.md`, and
  nothing else in it: the "Layers" item 4 marked done with the date and this
  change's archived evidence path; the "Empirical validation" table gains a
  row for `lean-install` (Internal-Cycloidal-Actuator, why, the results in one
  sentence); "Import paths" gains, under its table, that `Build123dSheetNode`
  lives in `machinome.node.build123d` beside `Build123dNode` because "node
  type" names the technology (design.md Decision 1); and the sentence "A
  regular package always wins over portions found earlier on sys.path, so
  order does not matter" gains the filter and its reason (Decision 9).
- [x] 9.4 `docs/architecture.md`: the leaf-adapter paragraphs (the
  addresses, the extras, the three doors, the reducer seam, the command
  table's `needs`), and the sentence that only the STEP adapter imports OCP
  and cadquery outside the engine.

## 10. Stop and report (the applier)

- [x] 10.1 With 1 to 9 done and the suite green, stop before any commit and
  report to the orchestrator: the diff stat, the red and green results, the
  suite's counts, the import-time measurements. The applier spawns no agent
  and runs neither validation below.

## 11. Empirical validation (the orchestrator)

- [x] 11.1 **Deep, Internal-Cycloidal-Actuator,** by a validator subagent the
  orchestrator briefs and launches, once per leg, from design.md's
  "Empirical validation":
  - *Where.* `/home/asa/devel/machinome/projects/Actuators/Internal-Cycloidal-Actuator`
    (main, c12d488, clean): a branch `lean-core-validation` from `main` in a
    worktree under the project's own `WTs/`; never merged, never pushed.
    Everything with `PYTHONPATH=<bench>` and the workspace venv, from the
    worktree.
  - *Suite, two legs.* Before: after the planning commit and before the
    applier starts. After: after 10.1, the change uncommitted in the bench.
    Commands: `machinome build`, `machinome test --faceted
    simulation/actuator/test_machine.py`, `machinome test --exact
    simulation/actuator/test_machine.py`. Expected before: green. Expected
    after, before migrating: the test module fails at its import with the
    dissolved package's `ImportError`; then migrate and run again: green.
    Record counts and the first line of any failure.
  - *Migration.* `simulation/actuator/test_machine.py` only, textually:
    `from machinome.node.adapters import step as step_module` → `from
    machinome.node import step as step_module`; `from
    machinome.node.adapters.step import StepAssembly` → `from
    machinome.node.step import StepAssembly`; the docstring's
    `machinome.node.adapters.step` → `machinome.node.step`. Record the diff
    stat (expected one file); if anything else must change, stop and report.
  - *Refusal probes* (after leg only), each a subprocess with `cadquery`
    blocked by the generalised finder of `tests/exact_engine_absent.py`
    written as a `sitecustomize.py` into a scratch directory first on
    `PYTHONPATH`: `python -c 'import machinome.node.cadquery'`; `python -c
    'from machinome.node import StepNode'`; from the worktree, `machinome
    import-step <the project's vendor STEP> --into <scratch>/sim`; and
    `machinome -h`. Expected as design.md states; record each verbatim with
    its exit status, and that `<scratch>/sim` was not created.
  - *Must not change:* anything in the bench or the framework; any project
    file beyond the one migrated.
  A failed validation returns to the orchestrator with the project's output;
  nothing is fixed in the project.
- [x] 11.2 **Shallow, the universe,** run by the orchestrator from the
  workspace root: `scripts/load-projects --bench <bench> --moved
  scripts/load-projects.d/exact-engine.toml
  scripts/load-projects.d/leaf-contract.toml
  scripts/load-projects.d/backend-switch.toml
  <bench>/openspec/changes/lean-install/moved-names.toml --timeout 300 --json
  <bench>/openspec/changes/lean-install/load-projects.json`. Expected:
  `Actuators/Internal-Cycloidal-Actuator` and `Robots/openvmp` (`don1`)
  `expected` by the `machinome.node.adapters` row; carried
  `3D-Printers/Voron-2` (`expected`), `3DPrintedClocks` `wall_clock_41` and
  `Robotic-Arms/Dum-E` (`unexpected`, pre-existing), six `no-model`. Any
  other row returns to the orchestrator with its output before integration.
- [x] 11.3 The orchestrator hands both reports to the paused applier.

## 12. Records, ADRs, specs, commit (the applier, after 11)

- [x] 12.1 Fold 11.1 and 11.2 into the evidence, verbatim where they quote a
  message or a summary line.
- [x] 12.2 Write ADR-167 (`docs/adrs/NODE/`, a kernel is an extra and its
  module refuses its absence at import), ADR-168 (`docs/adrs/BUILD/`, the
  command table names the module a command needs; amends ADR-024 and
  ADR-059, which gain status lines and amendment sections), ADR-169
  (`docs/adrs/NODE/`, a leaf type is one module under `machinome.node`; the
  adapters package dissolved; the filtered path extension; amends ADR-004's
  layout); list them in `docs/adrs/README.md`.
- [x] 12.3 Sync the delta specs into `openspec/specs/` (the new
  `kernel-extras`; the `node-model`, `exact-engine-dependency`,
  `occt-engine`, `cli-startup-cost`, `cli`, `markings` and `vet` deltas); in
  `node-model`'s Purpose, the code list names the leaf modules instead of
  `adapters/`; run `openspec validate --specs --strict`; archive the change
  with its `moved-names.toml` and `load-projects.json`.
- [x] 12.4 Make the one implementation commit on `v0.8-lean-install`. The
  copy of `moved-names.toml` to the workspace's
  `scripts/load-projects.d/lean-install.toml`, the studio skill's lines and
  `scripts/setup`'s install line (design.md "Deferred") are the
  orchestrator's, outside the framework.
