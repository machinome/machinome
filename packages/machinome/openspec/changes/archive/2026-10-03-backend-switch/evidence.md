# Evidence — `backend-switch`

The third cycle of the lean-core campaign (`workflow/ongoing/lean-core.md`,
item 2 of "What it takes"). Worktree `machinome/WTs/v0.8-backend-switch`,
branch `v0.8-backend-switch`, cut from `v0.8` at e98b74a. Planning commit
677f9c7. Every command below ran from inside the worktree with
`PYTHONPATH=<worktree>` and the workspace venv; `machinome.__file__`
resolved to `<worktree>/machinome/__init__.py`. Pytest ran one process at a
time, never in parallel.

## 1. Baseline on the unmodified tree

### 1.2 The six files the change touches or relies on

```
env -C <worktree> PYTHONPATH=<worktree> .venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_openscad_dependency.py tests/test_build123d_adapter.py tests/test_stl_node.py \
  tests/test_sheet_leaf.py tests/test_jscad_integration.py tests/test_backend_neutral_materialization.py
133 passed, 1 skipped, 4 warnings, 14 subtests passed in 6.19s
wall time 7.5 s
```

### 1.3 The message probe

Re-run from `openspec/changes/backend-switch/probe_message.py` (removed
from the change directory afterwards): a throwaway project in a temporary
directory (its own `pyproject.toml` with `[tool.machinome]`, and a module
`probe_parts.py`) holding `FacetedBox(Solid2Node)`, built once named
`housing` and once unnamed; `OutsideScadLeaf(LeafNode)` with `render()`
returning a solid2 `cube` and `as_scad()` returning it; and
`SilentProducer(LeafNode)` whose `materialize` returns without publishing.
Each node `_prepare()`d, then `generate_stl()` with
`machinome.openscad.shutil.which` patched to `None` (the `openscad_binary`
cache cleared first) and `machinome.node.base.Popen` patched to fail:

```
OpenScadUnavailable: node housing (Solid2Node backend) requires the OpenSCAD binary because its backend renders this STL through OpenSCAD; install OpenSCAD and ensure 'openscad' is on PATH
OpenScadUnavailable: node FacetedBox (Solid2Node backend) requires the OpenSCAD binary because its backend renders this STL through OpenSCAD; install OpenSCAD and ensure 'openscad' is on PATH
OpenScadUnavailable: node OutsideScadLeaf (OutsideScadLeaf backend) requires the OpenSCAD binary because its backend renders this STL through OpenSCAD; install OpenSCAD and ensure 'openscad' is on PATH
OpenScadUnavailable: node SilentProducer (SilentProducer backend) requires the OpenSCAD binary because its backend renders this STL through OpenSCAD; install OpenSCAD and ensure 'openscad' is on PATH
```

The four lines design.md recorded, verbatim. One observation beside the
probe: `SilentProducer.assemble()` (rather than `_prepare()`) raises
`NotImplementedError: LeafNode subclass <class 'probe_parts.SilentProducer'>
must be able to output scad` from `LeafNode.as_scad`, because `assemble`
presents a leaf whose STL is not current through `as_scad`; the
silent-producer finding (design.md, "Findings") is reached through
`_prepare()` then `generate_stl()`, as the probe does (and as design.md's
probe did); which build pipelines take that order was not examined here.
Not changed (Non-Goals).

### 1.4 The two AST scans

A scratch script parsed every module under `machinome/` (102 modules, 251
class names defined) and ran design.md's two scans: comparisons with a
`__name__`/`__qualname__` attribute on one side and a string literal or a
collection of them on another; and comparisons containing a string literal
spelling a class defined under `machinome/`.

```
scan 1 (__name__/__qualname__ vs string literal):
   machinome/node/base.py 1333 cls.__name__ in ('Solid2Node', 'OpenScadNode', 'FusionNode')
scan 2 (string literal spelling a machinome class):
   machinome/node/base.py 1333 cls.__name__ in ('Solid2Node', 'OpenScadNode', 'FusionNode')
```

Each finds exactly the switch.

## 2. Red first (task 2.5)

The tests of tasks 2.1 to 2.4 were written before any source change and
run on the unmodified tree (677f9c7 plus the tests), in one pytest process:

```
env -C <worktree> PYTHONPATH=<worktree> .venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_no_class_name_recognition.py \
  "tests/test_openscad_dependency.py::OpenScadDependencyTest::test_mesh_leaf_missing_binary_names_node_class_and_remedy" -rA
7 failed, 2 passed, 4 warnings, 8 subtests passed in 4.40s
```

(Counts include subtests: four test functions failed, one of them through
three subtests.) What the new and changed files hold:

- `tests/test_openscad_dependency.py`: the mesh-leaf test renamed
  `test_mesh_leaf_missing_binary_names_node_class_and_remedy`, asserting
  `OpenScadUnavailable` and its whole sentence (2.1); `Popen` still patched
  to fail.
- `tests/contract_package/scad_stand_in.py`: `MeshScad(LeafNode)`,
  `leaf_contract = 1`, `render()` returning a solid2 `cube(2)`, `as_scad()`
  returning it, no `materialize` (2.2). It imports `machinome.node.leaf`
  only, so `test_leaf_contract_reach.py`'s glob over `contract_package/`
  covers it.
- `tests/test_no_class_name_recognition.py`: the refusal tests over
  `MeshScad` and a `Solid2Node` subclass `ScadPart` (2.2); the AST rule over
  every module under `machinome/`, plus a test that each forbidden form,
  planted in a source string, is found and a displayed name or a
  comparison of two `__name__` values is not (2.3); the parametrised
  routing characterization over `CadQueryNode` (`ExactBox`),
  `Build123dNode` (`Build123dBox`), both from `test_openscad_dependency.py`,
  and `Build123dSheetNode` (`Plate`, from `test_sheet_leaf.py`) (2.4).

Each failure and its reason:

| task | test | red because |
|---|---|---|
| 2.1 | `test_mesh_leaf_missing_binary_names_node_class_and_remedy` | the sentence is `node housing (Solid2Node backend) requires the OpenSCAD binary because its backend renders this STL through OpenSCAD; ...`, not `node housing (FacetedBox) ... its STL is rendered from SCAD by OpenSCAD; ...` |
| 2.2 | `test_a_scad_presented_leaf_outside_the_core_is_reported_the_same_way` | `node MeshScad (MeshScad backend) requires ... its backend renders this STL through OpenSCAD; ...`: the outside leaf's own class called a backend |
| 2.2 | `test_a_refusal_describes_a_node_by_its_own_class_only` (subtests `ScadPart`/`Solid2Node`, `ScadPart`/`backend`, `MeshScad`/`backend`, then the prefix) | `'Solid2Node' unexpectedly found in "node sensor (Solid2Node backend) ..."`, `'backend' unexpectedly found` in both; `'node sensor (Solid2Node backend)' != 'node sensor (ScadPart)'` |
| 2.3 | `test_no_core_module_compares_a_class_name_to_a_string` | one site: `machinome/node/base.py:1333: cls.__name__ in ('Solid2Node', 'OpenScadNode', 'FusionNode')  (compares a class name with a string)` |

Green before, as characterizations by design:
`test_no_exact_adapter_reaches_the_openscad_path` (2.4; three subtests, one
per adapter: each writes its STL with `require_openscad` and `Popen`
patched to fail), and `test_the_scan_finds_each_form_it_forbids` (the
scanner's own self-check, 2.3).

## 3. The change

### 3.1 `generate_stl`

`machinome/node/base.py`, `AbstractBaseNode.generate_stl`: the
`backend = next(...)` walk of the MRO for `'Solid2Node'`, `'OpenScadNode'`
and `'FusionNode'` deleted; `require_openscad(f'node {node_name}
({type(self).__qualname__})', 'its STL is rendered from SCAD by OpenSCAD')`.
Nothing else in the method, nor in `machinome/openscad.py`, changed;
`require_openscad` stays imported at the module's top.

### 3.2 The retired tests

| retired test | what now covers its behaviour |
|---|---|
| `test_build123d_adapter.py::ExactAdapterIdentityTest::test_neither_adapter_resolves_to_a_mesh_rendering_backend` (two subtests, `CadQueryNode`, `Build123dNode`) | `test_no_class_name_recognition.py::SharedBaseRoutingTest::test_no_exact_adapter_reaches_the_openscad_path` (subtests `CadQueryNode`, `Build123dNode`), and the existing `test_build123d_adapter.py` `test_the_stl_never_reaches_the_openscad_renderer`, `test_openscad_dependency.py` `test_build123d_leaf_never_consults_openscad` and `test_exact_fusion_never_consults_openscad` |
| `test_stl_node.py` `test_the_backend_walk_resolves_no_mesh_backend` | the existing `test_stl_node.py` `test_the_leaf_never_reaches_the_openscad_renderer` (`require_openscad` and `Popen` patched to fail; an imported mesh is not an exact adapter, so 2.4 does not list it) |
| `test_sheet_leaf.py::SheetAdapterContractTest::test_the_backend_walk_resolves_no_mesh_backend` | `SharedBaseRoutingTest` (subtest `Build123dSheetNode`), and the existing `test_sheet_leaf.py` `test_the_stl_never_reaches_the_openscad_renderer` and `test_a_sheet_leaf_builds_with_no_openscad_on_the_path` |

The docstring of `test_build123d_adapter.py::ExactAdapterIdentityTest` now
ends "which is what a project's `isinstance` check relies on", no longer
naming the lookup in `generate_stl`. Every other test in the three files is
unchanged.

### 3.3 Green

```
pytest tests/test_no_class_name_recognition.py \
  "tests/test_openscad_dependency.py::OpenScadDependencyTest::test_mesh_leaf_missing_binary_names_node_class_and_remedy"
6 passed, 4 warnings, 11 subtests passed in 4.65s
pytest tests/test_openscad_dependency.py tests/test_build123d_adapter.py tests/test_stl_node.py \
  tests/test_sheet_leaf.py tests/test_jscad_integration.py tests/test_backend_neutral_materialization.py
130 passed, 1 skipped, 4 warnings, 12 subtests passed in 6.11s
wall time 7.4 s
```

130 against 133 before: the three retired tests (12 subtests against 14:
the retired build123d test had two). Because `scad_stand_in.py` joins the
glob of `test_leaf_contract_reach.py` over `tests/contract_package/`, that
file and the other two leaf-contract files that read the stand-ins were
run as well: `tests/test_leaf_contract_reach.py
tests/test_leaf_contract_members.py tests/test_leaf_contract_version.py`:
`17 passed, 4 warnings, 159 subtests passed in 3.63s`.

The probe of 1.3, re-run on the changed tree (from the session scratchpad,
`env -C <worktree>`):

```
OpenScadUnavailable: node housing (FacetedBox) requires the OpenSCAD binary because its STL is rendered from SCAD by OpenSCAD; install OpenSCAD and ensure 'openscad' is on PATH
OpenScadUnavailable: node FacetedBox (FacetedBox) requires the OpenSCAD binary because its STL is rendered from SCAD by OpenSCAD; install OpenSCAD and ensure 'openscad' is on PATH
OpenScadUnavailable: node OutsideScadLeaf (OutsideScadLeaf) requires the OpenSCAD binary because its STL is rendered from SCAD by OpenSCAD; install OpenSCAD and ensure 'openscad' is on PATH
OpenScadUnavailable: node SilentProducer (SilentProducer) requires the OpenSCAD binary because its STL is rendered from SCAD by OpenSCAD; install OpenSCAD and ensure 'openscad' is on PATH
```

The scans of 1.4, re-run: 102 modules, 251 class names, no site in either.
The fourth line is the silent-producer finding, unchanged by design (it
still reaches the path; only its wording changed).

### 3.4 The greps

```
grep -rn --exclude-dir=_build --exclude-dir=__pycache__ '<pattern>' machinome docs tests
  'backend renders this STL'   no match
  'Solid2Node backend'         no match
  'backend lookup'             no match
```

(The new test's docstrings first said "the retired backend lookup"; they
were reworded "the retired class-name lookup" so the grep is clean.) Under
`openspec/`, the three patterns remain in this change's own `proposal.md`,
`design.md`, `tasks.md` and this file; in the archived
`2026-08-22-exact-leaf-node-base`, `2026-08-22-sheet-leaf-node` and
`2026-10-03-leaf-contract` records; and in the baseline
`openspec/specs/node-model/spec.md`, whose scenario "The backend lookup is
not confused by a shared ancestor" (line 597) this change's delta replaces
when it is synced (task 7.5).

### 3.5 The whole suite

Run once, alone, after the documentation of group 4 so the one run covers
it (no other pytest process was running; checked with `pgrep -af '[p]ytest'`):

```
env -C <worktree> PYTHONPATH=<worktree> .venv/bin/python -m pytest -q -p no:cacheprovider
4265 passed, 4 skipped, 53 warnings, 3301 subtests passed in 512.57s (0:08:32)
wall time 515 s
```

Beside the leaf-contract cycle's run (`4263 passed, 4 skipped, 53
warnings, 3291 subtests passed in 509.84s`, wall 513 s): +2 tests, the
three retired and five added (`test_no_class_name_recognition.py`; 2.1 is
a rename); +10 subtests, the retired build123d test's two out, the new
file's eleven in, and one more in `test_leaf_contract_reach.py`, whose
private-reach scan iterates over every module of `tests/contract_package/`
and now meets `scad_stand_in.py`. Wall time within 2 s.

## 4. Documentation

- `docs/project/changelog.rst`: one bullet at the top of `Unreleased`, "No
  node type is recognised by its class name", with the `housing
  (FacetedBox)` before and after, the outside leaf reported in the same
  words, and no build behaviour, artifact, record or identity changed
  (ADR-166).
- `docs/architecture.md` needs no change (task 4.2): its STL-generation
  paragraph (near line 2000) says "A missing binary raises one actionable
  error naming the operation and remedy before subprocess launch", which
  still holds, and names no backend label; its "asynchronous only at an
  actual OpenSCAD backend" (line 1972) speaks of the OpenSCAD path, not of
  a label in a message. `docs/reference/` contains no `Solid2Node backend`,
  `OpenScadNode backend` or `requires the OpenSCAD binary` text (grep).

## 6. Empirical validation (tasks 6.1, 6.2)

Both run by the orchestrator, not by the applier; its reports, folded in
here verbatim where they quote a message or a summary line.

### 6.1 Deep: splitflap

Branch `lean-core-validation` of `projects/splitflap`, a worktree at
`projects/splitflap/WTs/lean-core-validation` from master 600f7bb.
Everything with `PYTHONPATH=<bench>:<worktree>` and the workspace venv,
from the worktree. **Migration: none**; the branch holds no commit and
`git status` is clean, as expected.

| leg | bench | `machinome build` | `test --faceted panels.py` | `wheel.py` | `splitflap.py` | `pytest -q simulation/test_layout.py` |
|---|---|---|---|---|---|---|
| before (12:31) | 677f9c7, unchanged code | exit 0 | Ran 5 tests: 5 passed, 0 failed | Ran 8 tests: 8 passed, 0 failed | Ran 8 tests: 8 passed, 0 failed | 2 passed |
| after (12:47) | 677f9c7 plus the uncommitted change | exit 0 | 5 passed, 0 failed | 8 passed, 0 failed | 8 passed, 0 failed | 2 passed |

**The refusal.** `machinome build` with a `PATH` of symlinks to every
binary of `/usr/bin` and `/bin` except `openscad`, plus the venv's `bin`,
and `SOLID_BUILD_DIR` pointed at a fresh scratch directory so every STL is
stale; the first node refused:

```
before: machinome.openscad.OpenScadUnavailable: node front (Solid2Node backend) requires the OpenSCAD binary because its backend renders this STL through OpenSCAD; install OpenSCAD and ensure 'openscad' is on PATH
after:  machinome.openscad.OpenScadUnavailable: node front (FrontPanel) requires the OpenSCAD binary because its STL is rendered from SCAD by OpenSCAD; install OpenSCAD and ensure 'openscad' is on PATH
```

The node refused first is `front`, a `FrontPanel`, which is a `Solid2Node`
through the project's `ScadPart`, rather than `SensorPcb` as task 6.1
guessed; the build reaches it first. Nothing in the project changed
between the legs.

### 6.2 Shallow: the universe

Run from the workspace root at 12:48 on 3 October 2026 (ended 13:15),
against the bench at 677f9c7 plus this change's uncommitted implementation:

```
scripts/load-projects --bench <bench> \
  --moved scripts/load-projects.d/exact-engine.toml scripts/load-projects.d/leaf-contract.toml \
          <bench>/openspec/changes/backend-switch/moved-names.toml \
  --timeout 300 --json <bench>/openspec/changes/backend-switch/load-projects.json
62 repositories, 129 rows: 120 ok, 1 expected, 2 unexpected, 0 timeout, 6 no-model; 2 skipped
Skipped: .Trash-1000 (skip rule), sandbox (skip rule)
exit 1
```

The full table is `load-projects.json`, archived beside this file (its
`counts` and `bench_commit` 677f9c76e5ef agree with the summary line).
Every row that is not `ok`:

| repository | class | cause |
|---|---|---|
| `3D-Printers/Voron-2` | expected | the first cycle's `shape()` move: `AttributeError: 'OCP.OCP.TopoDS.TopoDS_Shape' object has no attribute 'intersect'` |
| `3DPrintedClocks` / `wall_clock_41` | unexpected, pre-existing | `ValueError: Workplane object must have at least one solid on the stack to union!` at `clocks/plates.py:5224` |
| `Robotic-Arms/Dum-E` | unexpected, environment | `ModuleNotFoundError: No module named 'machinome_freecad'` |
| KZG-Marble-machine, Dummy-Robot, Primo, asimov-1, berkeley-humanoid-sim, upkie | no-model | no declared model |

Identical to the leaf-contract sweep; no row names anything from this
cycle, which moved no name (`moved = []`).

## 7. ADRs, plan, warts, specs

- ADR-166 under `docs/adrs/NODE/`, "The core recognises no node type by the
  spelling of its class name", amending ADR-046 and citing ADR-004, ADR-102,
  ADR-161 and ADR-163. ADR-046's status line gains "amended 2026-10-03 by
  ADR-166" and an *Amendment (2026-10-03)* section: what needed OpenSCAD,
  for a node's STL, is the node and its own class; its Evidence sentence
  naming the `Solid2Node` backend stays as history. `docs/adrs/README.md`
  lists ADR-166 under NODE and marks ADR-046 "amended by 166". The ADR links
  the change at `openspec/changes/archive/2026-10-03-backend-switch/`, which
  resolves with this archive.
- `workflow/ongoing/lean-core.md`: the class-name bullet of "Facts
  established on 1 October 2026" and "What it takes" item 2 gain "(removed
  by change `backend-switch`, 3 October 2026: the refusal names the node and
  its class; ADR-166)"; the "Empirical validation" table's class-name-switch
  row is marked **Done** with the splitflap and universe results and this
  file's archived path. Nothing else in the plan changed.
- `workflow/warts.md`: a section "Findings from the framework cycle
  `backend-switch` (3 October 2026)" with the silent-producer fall-through,
  untriaged.
- Delta specs synced by hand into `openspec/specs/node-model/spec.md` ("Leaf
  adapters are distinct types" replaced by its modified text; "No node type
  is recognised by its class name" appended) and
  `openspec/specs/openscad-dependency/spec.md` ("A missing OpenSCAD binary
  is reported actionably" replaced). **A departure in mechanism:**
  `openspec archive backend-switch --yes` refused the sync, "node-model
  MODIFIED failed for header "### Requirement: Leaf adapters are distinct
  types" - current spec contains scenario(s) not present in the modified
  block: "The backend lookup is not confused by a shared ancestor"", and
  changed no file. Dropping that scenario is this change's design
  (Decision 3), so the requirement blocks were replaced by a script
  (modified blocks replaced whole, the added block appended), the diff
  against the pre-sync baseline read line by line, and the change archived
  with `--skip-specs`.

```
openspec validate node-model --type spec --strict           -> Specification 'node-model' is valid
openspec validate openscad-dependency --type spec --strict  -> Specification 'openscad-dependency' is valid
openspec validate backend-switch --type change --strict     -> Change 'backend-switch' is valid
```

After the ADRs, the plan amendment, the warts entry, the spec sync and the
archive (no source change since the whole-suite run), the files that read
specs, records and documentation were run alone, with the new test file:
`tests/test_leaf_contract_members.py tests/test_release_records.py
tests/test_missing_source_file.py tests/test_frame_precision_docs.py
tests/test_profile_documentation.py tests/test_docs_structure.py
tests/test_docs_exports.py tests/test_no_class_name_recognition.py`:
`70 passed, 4 warnings, 321 subtests passed in 7.85s`.
