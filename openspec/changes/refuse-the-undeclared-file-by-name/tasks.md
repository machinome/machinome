Bench: `/home/asa/devel/machinome/machinome/WTs/fix-warts-3`, branch
`fix-warts-3`. Every framework command runs as
`env -C <bench> PYTHONPATH=<bench> /home/asa/devel/machinome/.venv/bin/<tool> ...`.
`<scratch>` is the campaign scratchpad's `cycle12/` directory
(`/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle12`),
holding `probe_construct.py` and the fixture project `probe_project/`
(`pyproject.toml`, `parts.py`, `assembly.py`, `markings_probe.py`); the
commands that run them are in design.md, Context. No catalogue project is
run or edited: this change is a framework message contract, validated on
fixture projects. One test run of ours at a time (they share
`tests/_build`). Every test marked RED in section 2 is run and seen red, for
the reason it names, before the code that turns it green. Record every
command and its result in `evidence.md` as you go, in the shape of
`openspec/changes/archive/2026-10-04-scad-presentation/evidence.md`.

## 1. Baseline on the unmodified tree

- [ ] 1.1 Create `evidence.md` with the bench commit (`git -C <bench>
  rev-parse HEAD`) and the interpreter check (`python -c 'import
  machinome; print(machinome.__file__)'` prints a path under the bench).
- [ ] 1.2 Run `pytest -q -p no:cacheprovider tests/test_missing_source_file.py
  tests/test_builder_lifecycle.py tests/test_leaf_contract_mesh.py
  tests/test_builder_reload_resilience.py` and `pytest -q -p
  no:cacheprovider tests/test_stl_node.py tests/test_step_node.py -k
  missing_declaration`; record counts and wall time (Stage P: 71 passed, 7
  subtests passed, 9.84 s; 2 passed, 96 deselected, 3.00 s).
- [ ] 1.3 Copy the sources of `<scratch>/probe_construct.py`,
  `<scratch>/probe_project/parts.py`, `assembly.py`, `markings_probe.py`
  and `pyproject.toml` into `evidence.md` (the scratchpad is not durable).
  Run `probe_construct.py`, `markings_probe.py`, and `machinome build` for
  each of `assembly:Rig`, `parts:BareStl`, `parts:BareScad`,
  `parts:BareJscad`, `parts:GhostContributor` and
  `parts:FailingPreparation`, one at a time; record each output and exit
  status. Expect design.md's Context.
- [ ] 1.4 Record the catalogue scan of design.md, "Who reads the old
  texts", rerun as written: no test or code under `projects/` asserts on,
  matches or catches an old text. If a hit appears, stop and report it
  before section 3.

## 2. Red tests

- [ ] 2.1 RED `tests/test_missing_source_file.py`, a new class
  `UndeclaredSourceTest` writing its own scratch project as
  `ForeignScratchSourceTest` does (a `pyproject.toml` with
  `[tool.machinome]`, a `leaf.py` imported under a unique module name), the
  node-model scenario "A source attribute that is not declared": for each
  of `StlNode`/`stl_source`, `StepNode`/`step_source`,
  `JScadNode`/`jscad_source` and `OpenScadNode`/`scad_source` (a subTest
  each), a subclass `Bare<kind>` declaring nothing raises an exception
  whose type IS `ValueError` (`assertIs(type(error), ValueError)`), whose
  message contains the subclass name, the attribute, the real path of the
  scratch `leaf.py` and `does not declare`, and does not contain `join()`,
  `OpenJScadNode` or `must declare`. For `OpenScadNode`, patch
  `machinome.node.openscad.coherent_read` with a `Mock` and assert it was
  not called. Red today: `StlNode` and `StepNode` lack the module path and
  `does not declare`; `JScadNode` raises `Exception`; `OpenScadNode` raises
  `TypeError`.
- [ ] 2.2 RED same class, the scenario "An empty declaration names no
  file": for each of the four, a subclass declaring the attribute as `''`
  raises exactly `ValueError` whose message contains the subclass name, the
  attribute, `= ''`, `names no file` and the module's real path, and does
  not contain `is not a file`. Red today: `StlNode`/`StepNode`/`JScadNode`
  as in 2.1; `OpenScadNode` refuses the module's directory as "not a file".
- [ ] 2.3 RED same class, the scenario "A leaf written outside the core
  refuses it the same way": `class BareMesh(MeshPart)` (importing `MeshPart`
  from `tests.contract_package.faceted_stand_in`) declaring no
  `mesh_source` raises exactly `ValueError` naming `BareMesh`, `mesh_source`
  and the real path of the module defining `BareMesh`, with `does not
  declare`. Red today: `TypeError: join() argument must be str ...`.
- [ ] 2.4 RED same class, the leaf-contract scenario "A declaration given
  alone is resolved beside its module":
  `require_source_file(stl_parts.Bracket, 'stl_source', 'bracket.stl')`
  returns `os.path.realpath(os.path.join(STL_PROJECT, 'bracket.stl'))`, and
  `require_source_file(stl_parts.Bracket, 'stl_source', 'bracket.stl',
  <that path>)` returns the same path. Red today: the first raises
  `TypeError` (missing argument), the second returns `None`.
- [ ] 2.5 GUARD: every existing test of `tests/test_missing_source_file.py`
  (absent, directory, outside-the-project, symbolic link, computed and
  absolute sources, the removed-after-construction case, the artwork above
  the root) and `test_a_missing_declaration_fails_naming_the_class` in
  `tests/test_stl_node.py` and `tests/test_step_node.py` stay green before
  and after, unedited.
- [ ] 2.6 RED `tests/test_builder_lifecycle.py`, a new class
  `InitialFailureLineTest` driving `Builder('model.py', build_dir=<a
  temporary directory>, watch=False)._start()` with `asyncio.run`, as the
  class's existing failure tests do, under
  `assertLogs('core.builder', level='ERROR')`, one case per stage, each
  outcome `BuildOutcome.FAILED` and each logged ERROR line equal to:
  - load (`machinome.core.builder.load_node` patched with
    `side_effect=RuntimeError('broken model')`):
    `The model model.py could not be loaded: broken model`;
  - inspect initial sources (`load_node` returning a node whose `mtime_ns`
    raises `FileNotFoundError(errno.ENOENT, 'No such file or directory',
    '/nowhere/ghost.py')`, e.g. a `Mock` with a `PropertyMock` on its
    type): `The sources of the model model.py could not be read: [Errno 2]
    No such file or directory: '/nowhere/ghost.py'`;
  - assemble (`load_node` returning `Mock(children=())` whose `_prepare`
    raises `RuntimeError('preparation failed deliberately')`):
    `The model model.py could not be assembled: preparation failed
    deliberately`.
  Red today: `model.py: failed to load project: broken model`, `model.py:
  failed to inspect initial sources project: ...`, `model.py: failed to
  assemble project: ...`. If a stage cannot be reached with these patches,
  record why and reach it the nearest way the class's existing tests do.
- [ ] 2.7 RED `tests/test_missing_source_file.py`, a new class
  `UndeclaredNestedBuildTest`, the build-pipeline scenario "A failure at
  launch names the model and the step": the test writes a scratch project
  (`pyproject.toml` with `[tool.machinome]`; `parts.py` with
  `class BareStl(StlNode)` declaring nothing; `assembly.py` with
  `class Arm(AssemblyNode): bracket = BareStl()` and
  `class Rig(AssemblyNode): arm = Arm()`), runs `[sys.executable, '-c',
  'from machinome.cli import manage; manage()', 'build', 'assembly:Rig']`
  with `cwd=<project>` and `PYTHONPATH=<repository root>` (as
  `tests/test_tutorial_counter.py` runs the CLI, `SOLID_BUILD_DIR` and
  `SOLID_TEST_ENGINE` removed from the environment), and asserts: exit
  status 1; standard error contains `The model assembly:Rig could not be
  loaded: BareStl does not declare stl_source` and does not contain
  `failed to load project`; the project's `_build/errors.json` holds a
  traceback (confirm the path on the unmodified tree first). Red today:
  `assembly:Rig: failed to load project: BareStl is an StlNode and must
  declare ...`.
- [ ] 2.8 Run 2.1-2.7 on the unmodified tree; record 2.5 green and the
  failure line of each RED case.

## 3. The change

- [ ] 3.1 `machinome/node/sources.py`: `_undeclared(klass, attribute,
  declared, declaring)` beside `require_source_file`, and
  `require_source_file(klass, attribute, declared, path=None)` as
  design.md, Decisions 1 and 2: the undeclared refusal first, the
  resolution when `path` is `None` (`os.path.realpath(os.path.join(os.path.dirname(module.__file__), declared))`),
  containment and existence unchanged, the judged path returned. Rewrite its
  docstring for both forms, naming this change. Run 2.4: green.
- [ ] 3.2 `machinome/node/stl.py`, `step.py`, `jscad.py`,
  `openscad/__init__.py`: each constructor's own guard and join replaced by
  one resolving call (design.md, Decision 1); `StlNode`/`StepNode` keep
  `wrapper` for `source_closure`; `OpenScadNode` keeps `scad_source` as
  declared and stores the result in `openscad_source`. Run 2.1, 2.2 and
  2.5: green.
- [ ] 3.3 `tests/contract_package/faceted_stand_in.py`: `MeshPart` takes
  `self.mesh_source = require_source_file(type(self), 'mesh_source',
  self.mesh_source)`; its docstring's sentence on resolution follows. Run
  2.3 and `tests/test_leaf_contract_mesh.py`: green.
- [ ] 3.4 `machinome/core/builder.py`: `_INITIAL_FAILURE` beside
  `_on_reload_exception` and its line (design.md, Decision 4); the reload
  path untouched. Run 2.6 and 2.7: green.
- [ ] 3.5 `grep -rn 'OpenJScadNode subclass\|the path of an STL file in the same\|the path of a STEP file in the same\|failed to {stage}\|os.path.join(basedir' machinome/`
  finds nothing; `grep -rn "require_source_file(" machinome/ tests/contract_package/`
  lists the four adapters and `MeshPart` in the resolving form and
  `Svg.resolve` in the four-argument form. Record both.
- [ ] 3.6 Run the focused sets of 1.2 again; record counts. Every existing
  test passes unedited.

## 4. Framework validation

- [ ] 4.1 `black --check` and `flake8 --max-line-length=89` on every
  touched Python file.
- [ ] 4.2 Rerun 1.3's probes and the six builds, one at a time; record each
  output beside 1.3's. Expect design.md's Decision 2 and 4 shapes: every
  `Bare*`, `Empty*` and `BareMesh` refused with `ValueError` in the one
  shape; `Svg('')` refused as naming no file and `Svg(None)` unchanged; the
  six builds exit 1 with `The model ... could not be loaded`, `The sources
  of the model parts:GhostContributor could not be read` and `The model
  parts:FailingPreparation could not be assembled`.
- [ ] 4.3 Run the full suite (`pytest` at the bench root, alone); record
  counts and wall time. Run once, after section 7, so the one run also
  covers the changelog and the synced specs.

## 5. Words

- [ ] 5.1 `grep -rn "must declare\|failed to\|require_source_file\|does not declare" docs/ --include=*.rst --include=*.md`
  outside `docs/adrs/`; read each hit: none is made wrong (design.md,
  Decision 7). Change nothing unless one is.
- [ ] 5.2 `docs/project/changelog.rst`: one bullet under the existing
  `Unreleased` section naming `refuse-the-undeclared-file-by-name`: a
  source-bound leaf that declares no source file, or declares it empty, is
  refused in one shape for every adapter, `ValueError` naming the class,
  the attribute and its module, where `JScadNode` raised a bare `Exception`
  naming a class that no longer exists and `OpenScadNode` a `TypeError`;
  `require_source_file` resolves a declaration given alone; and the
  builder's line on a failed launch reads `The model <reference> could not
  be loaded: ...` (or read, or assembled). Run
  `tests/test_release_records.py`.

## 6. Findings record

- [ ] 6.1 Move, verbatim, the whole section "name-the-missing-file
  (2026-09-15, found while fixing)" of `workflow/warts.md` — its
  introduction and both entries, "The four adapters refuse a missing
  DECLARATION inconsistently." and "The builder's own wrapper text reads as
  broken English and names the model, not the node." — to
  `workflow/archive/fix-warts-3-2026-10-06/resolved.md` under the heading
  `## \`refuse-the-undeclared-file-by-name\``, with a "What shipped"
  paragraph (what changed, the red-then-green counts, the probe and build
  results, the catalogue scan), and delete the section from `warts.md`.
- [ ] 6.2 If the orchestrator answered design.md's Open Question 2 by
  asking for it, add one `warts.md` entry recording that the builder's line
  carries no exception type; otherwise nothing.
- [ ] 6.3 Update `workflow/ongoing/fix-warts-3.md`'s "Progress" with one
  line for this cycle.

## 7. Sync and archive

- [ ] 7.1 Sync the five MODIFIED requirements into
  `openspec/specs/node-model/spec.md`, `leaf-contract/spec.md`,
  `stl-import/spec.md`, `step-import/spec.md` and
  `build-pipeline/spec.md` (`openspec archive
  refuse-the-undeclared-file-by-name --yes`, or by hand and then
  `--skip-specs`); check every carried scenario is present once.
- [ ] 7.2 `openspec validate --specs` passes after the archive, and the
  archived folder is
  `openspec/changes/archive/<date>-refuse-the-undeclared-file-by-name/`.
- [ ] 7.3 Run the focused sets of 1.2 once more, then 4.3; record. Leave
  everything uncommitted and report.
