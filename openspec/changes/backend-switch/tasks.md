## 1. Baseline on the unmodified tree

- [ ] 1.1 Create the cycle's evidence file
  `openspec/changes/backend-switch/evidence.md`, in the shape of the two
  archived cycles' (`2026-10-03-exact-engine/evidence.md`,
  `2026-10-03-leaf-contract/evidence.md`), with the bench commit.
- [ ] 1.2 Run, on the unmodified bench, `tests/test_openscad_dependency.py`,
  `tests/test_build123d_adapter.py`, `tests/test_stl_node.py`,
  `tests/test_sheet_leaf.py`, `tests/test_jscad_integration.py` and
  `tests/test_backend_neutral_materialization.py`; record counts and wall time.
- [ ] 1.3 Re-run design.md's message probe from a script under
  `openspec/changes/backend-switch/` (a throwaway project in a temporary
  directory: a named and an unnamed `Solid2Node` subclass, a SCAD-presented
  `LeafNode` subclass, and a `LeafNode` whose `materialize` publishes nothing;
  `machinome.openscad.shutil.which` patched to `None`), record the four
  messages verbatim, and remove the script afterwards.
- [ ] 1.4 Re-run design.md's two AST scans over `machinome/` and record that
  each finds exactly `machinome/node/base.py` at the switch.

## 2. Red tests

- [ ] 2.1 `tests/test_openscad_dependency.py`,
  `test_mesh_leaf_missing_binary_names_node_backend_and_remedy`: rename it
  `..._names_node_class_and_remedy` and assert the whole sentence of the
  `openscad-dependency` scenario "A mesh leaf cannot be rendered" for
  `FacetedBox(name='housing')`: `node housing (FacetedBox) requires the
  OpenSCAD binary because its STL is rendered from SCAD by OpenSCAD; install
  OpenSCAD and ensure 'openscad' is on PATH`, with `Popen` still patched to
  fail. Red: the message says `(Solid2Node backend)` and `its backend renders
  this STL through OpenSCAD`.
- [ ] 2.2 The outside SCAD-presented leaf:
  `tests/contract_package/scad_stand_in.py` with `MeshScad(LeafNode)`
  declaring `leaf_contract = 1`, `render()` returning a solid2 `cube`, and
  `as_scad()` returning it; no `materialize`. In a new
  `tests/test_no_class_name_recognition.py`: prepared with no `openscad`
  (patched `which`) and `Popen` patched to fail, `generate_stl()` raises
  `OpenScadUnavailable` whose text is the 2.1 sentence with `MeshScad`'s own
  name and `(MeshScad)` (the `openscad-dependency` scenario "A SCAD-presented
  leaf outside the core is reported the same way"); and the same test for a
  `Solid2Node` subclass `ScadPart` asserts neither text contains
  `Solid2Node`, `OpenScadNode`, `FusionNode` or `backend` (the `node-model`
  scenario "A refusal describes a node by its own class only"). Red: both say
  `backend`, and `ScadPart`'s says `Solid2Node`.
- [ ] 2.3 The AST rule, in `tests/test_no_class_name_recognition.py`: parse
  every `*.py` under `machinome/`; collect every class name defined there;
  fail on any `ast.Compare` with a `__name__` or `__qualname__` attribute on
  one side and a string constant, or a tuple, list or set containing one, on
  another; on any `ast.Compare` containing a string constant equal to a
  collected class name; and on `.startswith`/`.endswith` called on a
  `__name__`/`__qualname__` attribute. No allowed exceptions. The failure
  names the file, line and source of each site and the `node-model`
  requirement. A docstring states the boundary: displaying a class name is
  not a comparison. Red: `machinome/node/base.py` at the switch.
- [ ] 2.4 The behavioural form of the retired scenario, in
  `tests/test_no_class_name_recognition.py`: one test parametrised (subTest)
  over a `CadQueryNode`, a `Build123dNode` and a `Build123dSheetNode` leaf
  (reuse the fixtures of `test_openscad_dependency.py` and
  `test_sheet_leaf.py`): prepared, then `generate_stl()` with
  `machinome.node.base.require_openscad` and `machinome.node.base.Popen`
  patched to raise `AssertionError`; the `.stl` exists (the `node-model`
  scenario "A shared base does not route an exact adapter through
  OpenSCAD"). A characterization: green before and after, said so in the
  evidence.
- [ ] 2.5 Run 2.1 to 2.4 on the unmodified tree; record each failure and its
  reason in the evidence.

## 3. The change

- [ ] 3.1 `machinome/node/base.py`, `generate_stl`: delete the `backend =
  next(...)` lookup; call `require_openscad(f'node {node_name}
  ({type(self).__qualname__})', 'its STL is rendered from SCAD by OpenSCAD')`
  (design.md Decision 1). Keep `require_openscad` imported at the module's
  top as it is (the suite patches `machinome.node.base.require_openscad`),
  and change nothing else in the method or in `machinome/openscad.py`.
- [ ] 3.2 Retire the three name-walk tests, each replaced by the behaviour
  2.4 and the existing patched tests pin:
  `test_build123d_adapter.py` `test_neither_adapter_resolves_to_a_mesh_rendering_backend`,
  `test_stl_node.py` `test_the_backend_walk_resolves_no_mesh_backend`,
  `test_sheet_leaf.py` `test_the_backend_walk_resolves_no_mesh_backend`;
  and reword the docstring of the class around the first
  (`test_build123d_adapter.py`, "which is what a project's `isinstance` check
  and the backend lookup in generate_stl both rely on") so it no longer names
  the lookup. List each in the evidence with the test that now covers it.
- [ ] 3.3 Run 2.1 to 2.4 green, then the files of 1.2 again.
- [ ] 3.4 Grep `machinome/`, `docs/` and `tests/` for `backend renders this
  STL`, `Solid2Node backend` and `backend lookup`; nothing may remain except
  this change's own records and the archived ones.
- [ ] 3.5 Run the whole suite once, alone (it shares `tests/_build`; never two
  runs at once); record counts and wall time beside the leaf-contract cycle's.

## 4. Documentation

- [ ] 4.1 The changelog: one bullet in `docs/project/changelog.rst`'s existing
  Unreleased section: the core no longer recognises a node type by its class
  name; the missing-OpenSCAD refusal for a node's STL now names the node and
  its own class and says its STL is rendered from SCAD by OpenSCAD, giving the
  before and after of the `housing (FacetedBox)` example, and a leaf written
  outside machinome is reported in the same words; no build behaviour or
  artifact changes (ADR-166). Not in `HISTORY.rst`.
- [ ] 4.2 Confirm `docs/architecture.md` needs no change (its STL-generation
  paragraph says the refusal names "the operation and remedy", which still
  holds) and `docs/reference/` names no backend label; record the check in the
  evidence.

## 5. Stop and report (the applier)

- [ ] 5.1 With 1 to 4 done and the suite green, stop before any commit and
  report to the orchestrator: the diff stat, the red and green results, the
  suite's counts. The applier spawns no agent and runs neither validation
  below.

## 6. Empirical validation (the orchestrator)

- [ ] 6.1 **Deep, splitflap,** by a validator subagent the orchestrator
  briefs and launches, once per leg. Brief:
  - *Where.* `/home/asa/devel/machinome/projects/splitflap` (master, 600f7bb,
    clean): a branch `lean-core-validation` from `master` in a worktree under
    the project's own `WTs/`; never merged, never pushed. Everything with
    `PYTHONPATH=<bench>` and the workspace venv
    (`/home/asa/devel/machinome/.venv/bin/machinome`, `.../python`), from the
    worktree.
  - *Suite, before and after.* Two legs, so that "before" is the bench
    without the change: the before leg runs after the planning commit and
    before the applier starts (the bench then holds e98b74a's code), the
    after leg after 5.1 with the change uncommitted in the bench; the same
    validator brief serves both, launched once per leg. The commands are the
    project README's: `machinome build`, `machinome test --faceted
    simulation/panels.py`, `... wheel.py`, `... splitflap.py`,
    `PYTHONPATH=. pytest -q simulation/test_layout.py`.
    Record each command's pass/fail counts and the first line of any failure.
  - *Migration.* Expected: nothing changes in the project, since none of its
    files names a backend or the message. Record the diff stat (expected
    empty); if anything must change, stop and report it rather than change
    it.
  - *The refusal.* On `SensorPcb` (`simulation/hardware.py`, a `ScadPart`,
    which is a `Solid2Node`), in a scratch build directory
    (`SOLID_BUILD_DIR` pointed at a temporary directory) so its STL is stale,
    with `openscad` removed from `PATH` (a `PATH` with only the venv's `bin`
    and `/usr/bin` minus OpenSCAD, or a temporary directory of symlinks
    excluding it; state which), call `generate_stl()` on a constructed and
    prepared instance (or run `machinome build` and read the error), before
    and after. Expected before: `node <name> (Solid2Node backend) requires the
    OpenSCAD binary because its backend renders this STL through OpenSCAD;
    install OpenSCAD and ensure 'openscad' is on PATH`; after: `node <name>
    (SensorPcb) requires the OpenSCAD binary because its STL is rendered from
    SCAD by OpenSCAD; install OpenSCAD and ensure 'openscad' is on PATH`.
    Record both verbatim.
  - *Must not change:* anything in the bench or the framework; any project
    file beyond the branch's (expected empty) diff.
  A failed validation returns to the orchestrator with the project's output;
  nothing is fixed in the project.
- [ ] 6.2 **Shallow, the universe,** run by the orchestrator from the
  workspace root: `scripts/load-projects --bench <bench> --moved
  scripts/load-projects.d/exact-engine.toml
  scripts/load-projects.d/leaf-contract.toml
  <bench>/openspec/changes/backend-switch/moved-names.toml --timeout 300
  --json <bench>/openspec/changes/backend-switch/load-projects.json`. This
  cycle's moved-names file declares `moved = []`. Expected non-ok rows, all
  carried from the leaf-contract sweep: `3D-Printers/Voron-2` (expected, the
  first cycle's `shape()` move), `3DPrintedClocks`/`wall_clock_41` and
  `Robotic-Arms/Dum-E` (unexpected, pre-existing), six no-model. Any other
  row returns to the orchestrator with its output before integration.
- [ ] 6.3 The orchestrator hands both reports to the paused applier.

## 7. Records, ADRs, specs, commit (the applier, after 6)

- [ ] 7.1 Fold 6.1 and 6.2 into the evidence, verbatim where they quote a
  message or a summary line.
- [ ] 7.2 Write ADR-166 under `docs/adrs/NODE/`, "The core recognises no
  node type by the spelling of its class name" (design.md "ADRs"); amend
  ADR-046 (status line "amended by ADR-166" and an *Amendment (2026-10-03)*
  section: what needed OpenSCAD is named as the node and its own class);
  list ADR-166 and the ADR-046 amendment in `docs/adrs/README.md`.
- [ ] 7.3 Amend the campaign plan `workflow/ongoing/lean-core.md`, and
  nothing else in it: in "Facts established on 1 October 2026", the
  class-name bullet gains "(removed by change `backend-switch`, 3 October
  2026: the refusal names the node and its class; ADR-166)"; "What it takes"
  item 2 says the same in one clause; the "Empirical validation" table's
  class-name-switch row is marked **Done** with the date, the splitflap and
  universe results in one sentence, and this change's archived evidence path.
- [ ] 7.4 Append to `workflow/warts.md` a section "Findings from the
  framework cycle `backend-switch` (3 October 2026)" with design.md's
  finding: a self-materializing leaf whose `materialize` publishes nothing
  falls through to the OpenSCAD path; `JScadNode`'s no-output branch is the
  core's one instance; no project uses `JScadNode`; untriaged.
- [ ] 7.5 Sync the delta specs into `openspec/specs/` (`node-model`,
  `openscad-dependency`), run `openspec validate --specs --strict` or the
  equivalent for the two, archive the change, and copy its
  `moved-names.toml` to the workspace's `scripts/load-projects.d/backend-switch.toml`
  only if the orchestrator asks (the workspace is not the applier's to edit).
- [ ] 7.6 Make the one implementation commit on `v0.8-backend-switch`; the
  orchestrator's review precedes integration.
