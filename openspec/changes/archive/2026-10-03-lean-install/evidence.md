# Evidence — `lean-install`

The fourth cycle of layer 1 of the lean-core campaign
(`workflow/ongoing/lean-core.md`, "Layers (pilot, 3 October 2026)", item 4).
Worktree `machinome/WTs/v0.8-lean-install`, branch `v0.8-lean-install`, cut
from `v0.8` at 433b7b9. Planning commit ae64c2d. Every command below ran from
inside the worktree with `PYTHONPATH=<worktree>` and the workspace venv;
`machinome.__file__` resolved to `<worktree>/machinome/__init__.py` (checked
once, `env -C <worktree> PYTHONPATH=<worktree> .venv/bin/python -c 'import
machinome; print(machinome.__file__)'`). Pytest ran one process at a time,
never in parallel.

## 1. Baseline on the unmodified tree (ae64c2d)

### 1.2 The markings golden

`tests/markings_golden.py` (new, not collected) builds, under a temporary
`SOLID_BUILD_DIR`, the exact `Dial` of `tests/markings_project/dial.py` (a
`Wrapped` marking of `label.svg`, whose first region carries a hole), the
faceted `Plate` of `plate.py` (the mixin's `Flat` badge and its own `Wrapped`
band), and `ScaledPlate`, declared in the script: the `Plate` carrying one
more marking, a `Flat` marking of `label.svg` with `scale=0.5`. It records
each marking artifact's SHA-256 and, per artwork, the closed-region count read
off the reducer's INFO line, the vertex and triangle counts of
`Svg.tessellate(0.1)` and a SHA-256 of its arrays: 18 values. Run twice in
separate processes into the scratchpad, the two JSON files were
byte-identical (`cmp`), then written to `tests/data/markings_golden.json`
(bench commit ae64c2d). The three marking digests of the fixture parts
(`bd3dacd3...`, `ff24e82d...`, `e492ab49...`) are the prefixes
`test_markings.py::WindingTest::test_correct_artwork_is_untouched` already
pins. `--check` on the unmodified tree:

```
golden comparison: 18 values, 0 differences
```

### 1.3 The goldens of the earlier cycles

```
tests/exact_engine_golden.py --check    golden comparison: 7 fixtures, 0 differences
tests/leaf_contract_golden.py --check   golden comparison: 7 fixtures, 97 values, 0 differences
```

### 1.4 The files the change touches or relies on

```
env -C <worktree> PYTHONPATH=<worktree> .venv/bin/python -m pytest -q -p no:cacheprovider \
  tests/test_node_lazy_exports.py tests/test_core_kernel_free.py tests/test_exact_engine_seam.py \
  tests/test_cli_lazy_imports.py tests/test_import_step.py tests/test_markings.py \
  tests/test_vet_universe.py tests/test_machinome_identity.py tests/test_leaf_contract_reach.py
215 passed, 4 warnings, 231 subtests passed in 23.71s
wall time 25.1 s
```

### 1.5 design.md's probes, re-run from the session scratchpad

**The dissolved package.** A scratch package `pkg` whose `pkg/node/__init__.py`
defines a module `__getattr__` raising `AttributeError`. (a) With no
`pkg/node/adapters/` at all, (b) with a `pkg/node/adapters/__init__.py` that
only raises an `ImportError`. Each line is the last line of
`python -c '<spelling>'`:

```
(a) from pkg.node.adapters.cadquery import X   ModuleNotFoundError: No module named 'pkg.node.adapters'
(a) from pkg.node.adapters import step         ModuleNotFoundError: No module named 'pkg.node.adapters'
(a) import pkg.node.adapters.step              ModuleNotFoundError: No module named 'pkg.node.adapters'
(b) from pkg.node.adapters.cadquery import X   ImportError: module 'pkg.node.adapters' was dissolved: 'pkg.node.adapters.<x>' is 'pkg.node.<x>'
(b) from pkg.node.adapters import step         ImportError: module 'pkg.node.adapters' was dissolved: 'pkg.node.adapters.<x>' is 'pkg.node.<x>'
(b) import pkg.node.adapters.step              ImportError: module 'pkg.node.adapters' was dissolved: 'pkg.node.adapters.<x>' is 'pkg.node.<x>'
```

The parent's `__getattr__` is never consulted for a dotted path (a); the
refusing `__init__.py` answers all three spellings (b).

**The path extension**, in the bench:

```
sys.path has primary: True
extended: ['<worktree>/machinome', '/home/asa/devel/machinome/machinome/machinome']
machinome.exact -> /home/asa/devel/machinome/machinome/machinome/exact.py
```

The plain `pkgutil.extend_path` appends the primary checkout's package (the
venv's compat editable install puts `/home/asa/devel/machinome/machinome` on
`sys.path`), and `machinome.exact`, deleted by `exact-engine`, then resolves
to the primary's file: design.md's finding, reproduced.

**`find_spec` of the four kernels**:

```
{'cadquery': True, 'build123d': True, 'OCP': True, 'molejo': True} imported: [] find_spec 1.2 ms
```

All four found, none imported (design.md measured 2.3 ms).

## 2. Red first (task 2.10)

The tests of tasks 2.1 to 2.9 were written before any source change and run
on the unmodified source (ae64c2d plus the tests), in one pytest process:

```
env -C <worktree> PYTHONPATH=<worktree> .venv/bin/python -m pytest -q -p no:cacheprovider -rfp \
  tests/test_kernel_extras.py tests/test_node_lazy_exports.py tests/test_exact_engine_seam.py \
  tests/test_cli_lazy_imports.py "tests/test_import_step.py::ImportStepKernelAbsentTest" \
  "tests/test_import_step.py::ImportStepCliHelpTest" "tests/test_markings.py::ArtworkReductionTest" \
  "tests/test_markings.py::WindingTest" "tests/test_markings.py::ArtworkSeamTest" \
  "tests/test_markings.py::ArtworkReducerContractTest" tests/test_core_kernel_free.py \
  tests/test_leaf_addresses.py "tests/test_vet_assertions.py::LeafModuleTest"
77 failed, 77 passed, 4 warnings, 134 subtests passed in 37.30s
```

(Counts include subtests; 45 test functions are red.) What the new and
changed files hold:

- `tests/exact_engine_absent.py` (2.2): `run_python` and `run_machinome` take
  `absent=` (default `('machinome.occt',)`, so every existing caller is
  untouched), `broken=` and `cwd=`. The `sitecustomize` finder refuses every
  listed name and its submodules (`EXACT_ENGINE_ABSENT_NAMES`, comma
  separated); a second finder (`EXACT_ENGINE_BROKEN_NAMES`) returns a spec
  whose loader raises `ImportError('broken <name>')`.
- `tests/test_kernel_extras.py` (new; 2.1, 2.3): the metadata (eight tests)
  and the refusals by subprocess (three).
- `tests/test_node_lazy_exports.py` (2.4): `EXPECTED_EXPORTS` targets at
  `machinome.node.<x>`; `CheckCQEditor` from `machinome.node.cadquery`; the
  submodule probe reads `cadquery`; `NodePackageBrokenBackend` now holds the
  absent extra (three tests: the refusal unmodified through attribute access,
  through `from ... import`, through `hasattr`) and the broken kernel (three
  tests, under a new `CADQUERY_BROKEN` finder, spliced naming `StepNode`); the
  sentence "it is a required dependency and stays one" is gone.
- `tests/test_exact_engine_seam.py` (2.4): `AbsentKernelTest`, OCP absent and
  OCP broken.
- `tests/test_cli_lazy_imports.py` (2.4): three columns unpacked;
  `RegistryConformanceTest.test_every_needed_module_imports`;
  `CommandNeedsTest` (help without the extra, help importing no needed
  module, `viewer` importing no leaf module).
- `tests/test_import_step.py` (2.4): `test_the_kernel_missing_is_a_checked_failure`
  (it patched `_load_step_assembly`) replaced by `ImportStepKernelAbsentTest`,
  three CLI subprocess tests with `cadquery` blocked; `ImportStepCliHelpTest`
  reads three columns; the unused `from machinome.manager import import_step`
  dropped.
- `tests/test_markings.py` (2.5): the three `regions()` calls go through a
  helper importing `machinome.node.build123d.svg_regions`; `WindingTest`
  patches `machinome.node.build123d.svg_regions` (it patched `Svg.regions`);
  `ArtworkSeamTest` (three subprocess tests building the faceted fixture
  `Plate` with `build123d` blocked) and `ArtworkReducerContractTest` (two stub
  reducers and the version agreement).
- `tests/test_core_kernel_free.py` (2.6): the existing expectation names
  `machinome/node/step.py`; `KernelsOnlyInTheirModulesTest`, three AST rules.
- `tests/test_leaf_addresses.py` (new; 2.7, 2.8).
- `tests/vet_projects/leaf_modules/` and
  `tests/test_vet_assertions.py::LeafModuleTest` (2.9).

Each red test and its reason:

| task | test | red because |
|---|---|---|
| 2.1 | `KernelMetadataTest` × 7 (all but the range test) | the four kernels are required (`'molejo', 'ocp-gordon', 'build123d', 'cadquery'` in the required set); the extras `cadquery`, `build123d`, `step`, `molejo`, `all` are absent; `dev` has no `machinome[all]`; `requirements.txt` lacks `cadquery-ocp>=7.8.1,<7.9`; `tox.ini` has no `extras` |
| 2.3 | `test_each_kernel_module_refuses_each_absent_kernel` (7 subtests) | `'ModuleNotFoundError' != 'ExtraUnavailable'`: Python's own error, no `extra` (no module exists at the new addresses, or `occt.engine` imports OCP unchecked) |
| 2.3 | `test_checking_does_not_import_the_kernel`, `test_a_broken_kernel_reports_its_own_failure` | `No module named 'machinome.node.cadquery'` / `'machinome.node.step'` |
| 2.4 | `NodePackageExports` (identity: 9 subtests; `CheckCQEditor`), `NodePackageSubmodules` (`cadquery` subtest) | the modules are at `machinome.node.adapters.<x>` |
| 2.4 | the three absent-extra tests of `NodePackageBrokenBackend` | the error is `ModuleNotFoundError: No module named 'cadquery' (raised resolving machinome.node.StepNode from .adapters.step)`, spliced, naming no extra |
| 2.4 | `test_the_reported_failure_names_the_requested_export` | the splice says `from .adapters.step`, not `from .step` |
| 2.4 | `AbsentKernelTest.test_an_absent_occt_binding_is_an_absent_engine` | `exact_engine()` raises `ModuleNotFoundError: No module named 'OCP'` instead of answering `None` |
| 2.4 | `test_top_level_help_lists_every_command_with_its_docstring`, `RegistryConformanceTest` × 2, `ImportStepCliHelpTest` | the table has two columns (`not enough values to unpack`) |
| 2.4 | `ImportStepKernelAbsentTest` × 2 (the command, `-h`) | stderr is `Error: import-step needs the exact-geometry kernel (cadquery, the OCP binding) to read a STEP document; install it with 'pip install cadquery'. (No module named 'cadquery')`; `-h` exits 0 with the help |
| 2.5 | `ArtworkReductionTest` × 3, `WindingTest` × 4, `test_the_reducer_speaks_the_markings_contract` | no `machinome.node.build123d` |
| 2.5 | `test_a_stale_marking_without_the_extra_is_refused` | `ModuleNotFoundError: No module named 'build123d'` from inside `Svg.regions`, naming neither the part nor the extra |
| 2.5 | `ArtworkReducerContractTest` × 2 | the stub is never consulted: `markings.py` reduces with build123d itself and has no `ArtworkReducerIncompatible` |
| 2.6 | `test_no_core_module_imports_the_kernel_or_cadquery` | the scan finds `machinome/node/adapters/step.py` |
| 2.6 | `test_kernels_are_imported_only_by_their_modules` | `machinome/node/markings.py` imports `build123d`; the kernel modules are under `adapters/` |
| 2.6 | `test_kernel_modules_are_named_only_at_the_seams` (4 subtests) | `markings.py`, `cli.py`, `import_step.py` and `step.py` name no kernel module at its final address |
| 2.6 | `test_each_kernel_module_checks_its_kernel_first` (5 subtests) | four modules are not at their addresses (`KeyError`), and `occt/engine.py` has no `require_extra` call |
| 2.7 | `LeafAddressTest` × 5 | the modules are at the old addresses; `adapters/` holds nine modules; every former spelling imports (`NO_ERROR`) |
| 2.8 | `test_a_satellite_portion_is_found` (2 subtests) | no path extension: `No module named 'machinome.node.portion'` |

Green before, as characterizations by design: `test_cadquery_carries_one_range_wherever_it_is_named`
(CadQuery is `==2.7.*` today); `NodePackageBrokenBackend`'s
`test_the_package_still_imports_without_the_exact_stack`,
`test_a_broken_backend_raises_the_underlying_import_error` and
`test_hasattr_does_not_turn_a_broken_backend_into_a_missing_name`;
`AbsentKernelTest.test_a_broken_occt_binding_reports_its_own_failure`;
`CommandNeedsTest` × 3 and `ImportStepKernelAbsentTest.test_the_command_is_still_listed`
(the help path imports no STEP reader today); `ArtworkSeamTest`'s
`test_declaring_a_marking_needs_no_kernel` and
`test_a_current_marking_needs_no_reducer` (a current marking reduces nothing
today); `PathExtensionTest`'s `test_a_second_copy_of_the_core_is_never_merged`
and `test_the_framework_resolves_from_its_own_checkout` (no extension today;
1.5's probe shows the plain `extend_path` line would turn the first red);
`LeafModuleTest` (2.9: vet judges by place in the universe, and
`machinome.node.<x>` is beneath a contract member before the change as after).

One test was first red for a wrong reason and corrected before this run:
`test_a_second_copy_of_the_core_is_never_merged` ran its subprocess with
`cwd` the scratch directory, so `-c` put the scratch copy first on `sys.path`
and it became `machinome` itself (`OK /tmp/path-extension-.../machinome/stray.py`);
the subprocess now runs from the worktree.

## 3. The change

### 3.1 The addresses (group 3)

- `git mv machinome/node/adapters/{cadquery,build123d,step,molejo,solid2,openscad,jscad,stl}.py machinome/node/`;
  `adapters/build123d_sheet.py` folded into `machinome/node/build123d.py`
  (`_PLANE_TOLERANCE`, `_export_dxf`, `Build123dSheetNode`; no name collides)
  and `git rm`ed. `build123d.py` gains a module docstring (both node types and
  the reducer share one kernel, one address, one extra); the sheet class's
  docstring no longer cites "the MRO backend walk" (removed by
  `backend-switch`) or "the other build123d adapter", and its one 102-column
  line is rewrapped. `step.py` imports `workplane_shape` from
  `machinome.node.cadquery`; `cadquery.py`'s "the adapter module does not
  load CadQuery" reads "this module".
- `machinome/node/adapters/__init__.py`: licence header, a docstring, and
  design.md Decision 2's `ImportError`, verbatim. Nothing else.
- `machinome/node/__init__.py`: `_EXPORTS` values lose `adapters.`
  (`Build123dSheetNode` → `'build123d'`); no `_MOVED` row; the docstring
  names the leaf modules and the dissolved package.
- `machinome/manager/import_step.py`: docstring address and paragraph;
  `handle()` imports `StepAssembly` from `machinome.node.step`;
  `_load_step_assembly` and its `pip install cadquery` handler removed.

3.5: `test_leaf_addresses.py::LeafAddressTest` and `LeafModuleTest`: green
but for `test_the_names_only_a_module_answers_are_there`'s three reducer
subtests, which group 6 turned green.

### 3.2 The extras and the kernel checks (group 4)

- `machinome/extras.py` (new): `ExtraUnavailable(ModuleNotFoundError)` with
  `extra`, `needed_by`, `name` and Decision 4's sentence; `require_extra` by
  `importlib.util.find_spec` (a finder's `ModuleNotFoundError` counts as
  absent, `ValueError` as present); imports only `importlib.util`.
- The five calls of Decision 4's table, verbatim in extra, `needed_by` and
  kernels. In `cadquery.py` and `build123d.py`, which import no kernel at
  their top, the call follows the module's imports; in `step.py`,
  `molejo.py` and `occt/engine.py` it follows the standard-library imports
  and precedes every kernel import (and `step.py`'s import of
  `machinome.node.cadquery`). **A departure in mechanism:** the kernel
  imports after the call are E402 for flake8; a `# noqa: E402` on each
  pushed several of them past 89 columns, so `setup.cfg`'s `[flake8]` gains
  `per-file-ignores` for E402 in those three files, with a comment giving
  the reason.
- `machinome/node/__init__.py`'s `_load`: `except ExtraUnavailable: raise`
  before the splice; its docstring says an absent extra is not a broken
  install.
- `machinome/exact_engine.py`'s `_absent`: an `ExtraUnavailable` answers
  `extra == 'occt'`; the docstrings of `_absent` and `exact_engine()` say so.
  The seam imports `ExtraUnavailable` from `machinome.extras`.
- `machinome/occt/engine.py`'s and `machinome/node/molejo.py`'s docstrings no
  longer say the engine imports only the contract module, or that molejo's
  kernel "is not optional".
- `pyproject.toml`: the four kernel requirements leave `dependencies`, a
  one-comment pointer in their place; the coupling comment moves above the
  extras, the `ocp-gordon` bound comment into `build123d`, molejo's minor-pin
  comment above `molejo`; the extras `cadquery`, `build123d`, `step`,
  `molejo`, `all` exactly as Decision 3; `dev` gains `"machinome[all]"`
  first; the `occt` comment no longer says the pinned cadquery "above"
  requires its range; the `shapely` comment reads "directly or through an
  extra". `requirements.txt`: the new header, the kernel lines with
  `cadquery-ocp>=7.8.1,<7.9` added under a comment naming the extras.
  `tox.ini`: `extras = all` in `[testenv]`. The CI workflow
  (`.github/workflows/python-app.yml`) is unchanged: its `lint`, `test`,
  `browser-snapshot` and `build` jobs still run `pip install -r
  requirements.txt -r requirements_dev.txt`, and `requirements.txt` now
  names every concrete requirement of `all`.

4.6:

```
pytest tests/test_kernel_extras.py tests/test_node_lazy_exports.py tests/test_exact_engine_seam.py \
  tests/test_core_kernel_free.py
3 failed, 62 passed, 154 subtests passed in 20.58s
```

the three being the markings and CLI seams of
`test_kernel_modules_are_named_only_at_the_seams` and
`test_kernels_are_imported_only_by_their_modules`
(`machinome/node/markings.py` still imported build123d), which groups 5 and
6 turned green.

### 3.3 The command table (group 5)

`machinome/cli.py`: `COMMANDS` values `(module, class_name, needs)`, `needs`
`'machinome.node.step'` for `import-step` and `None` elsewhere, with a
comment explaining the column; `resolve_command` unpacks three; a new
`require_needed_module(name)` imports the `needs` module and on
`ExtraUnavailable` writes `Error: machinome <command> needs the <extra>
extra: <refusal>` and exits 1, any other import error propagating; `manage()`
calls it once `selected` is known and before `resolve_command`, and the help
path calls neither. 5.2: `tests/test_cli_lazy_imports.py`,
`ImportStepKernelAbsentTest`, `ImportStepCliHelpTest`, `tests/test_cli.py`,
`tests/test_leaf_contract_reach.py`: `47 passed, 51 subtests passed in 7.75s`.

### 3.4 The markings seam (group 6)

- `machinome/node/build123d.py`: `SVG_REDUCER_CONTRACT = 1`,
  `svg_regions(path)` (today's `Svg.regions` body, the log line under the
  same logger, `node.markings`, and the same refusal) and
  `svg_triangles(path, tolerance)` (today's `Svg.tessellate` body before
  scaling), build123d imported inside both.
- `machinome/node/markings.py`: `SVG_REDUCER_CONTRACT = 1`, `SVG_REDUCER`,
  `ArtworkReducerIncompatible` (in the exact seam's words),
  `_artwork_reducer()` (an `importlib.import_module` on every use, not
  cached, so a refusal is raised at every ask); `Svg.tessellate` calls the
  reducer and applies `scale`; `Svg.regions` and the module's `logging`
  removed; the module docstring and `Marking.surface`'s say the reduction is
  `machinome.node.build123d`'s.
- `AbstractBaseNode._build_markings` (`machinome/node/base.py`): the
  `ExtraUnavailable` rewrap of Decision 8, verbatim.

6.4: `tests/test_markings.py tests/test_leaf_addresses.py
tests/test_core_kernel_free.py`: `2 failed, 123 passed, 98 subtests passed`,
the two being the path-extension subtests of group 7.
`tests/markings_golden.py --check`: `golden comparison: 18 values, 0
differences`.

The refusal, with `build123d` blocked and the faceted fixture `Plate` built
into an empty `SOLID_BUILD_DIR` (exit 1, no `*.marking-*` file written):

```
machinome.extras.ExtraUnavailable: marking badge of Plate (artwork badge.svg) needs build123d, which is not installed; install it with 'pip install "machinome[build123d]"'
```

### 3.5 The path extension (group 7)

`machinome/__init__.py`: `_namespace_portions(path, name)` (Decision 9's
filter, with a docstring naming the finding) and `__path__ =
_namespace_portions(__path__, __name__)`; `__version__` untouched for
bumpversion. `machinome/node/__init__.py`: the same call, imported from
`machinome`.

Import times, `python -X importtime -c 'import <module>'`, cumulative
microseconds, seven runs each, sorted:

```
before import machinome       357 360 440 452 464 507 717
after  import machinome       5174 5863 6291 6473 7129 7695 7821
before import machinome.node  118074 121539 124196 124365 138595 139320 142687
after  import machinome.node  114067 126675 127008 128405 129707 134182 140210
```

`import machinome` costs about 6 ms more (median 0.45 → 6.5 ms; design.md
estimated 3.6 ms for `pkgutil` and 1 ms for the scan). `pkgutil` brings
`_typing`, `collections.abc`, `contextlib`, `typing`, `typing.io`,
`typing.re` and `weakref`. `import machinome.node` is within run-to-run
noise (median 124 → 128 ms).

7.2: `tests/test_leaf_addresses.py`: `8 passed, 22 subtests passed`. 1.5's
path probe re-run:

```
sys.path has primary: True
extended: ['<worktree>/machinome']
ModuleNotFoundError: No module named 'machinome.exact'
```

## 4. Existing tests, the suite, the docs build (group 8)

### 4.1 The repointed suites (8.1)

No asserted verdict, volume or message changed other than this change's.
Every edit is an address:

| file | what changed |
|---|---|
| `test_step_node.py` | `from machinome.node import step as step_module`; `from machinome.node.step import STEPCAFControl_Reader` |
| `test_step_assembly.py` | `from machinome.node.step import STEPCAFControl_Reader, StepAssembly`; `from machinome.node import step as step_module` |
| `test_import_step.py` | the same two module-top imports; besides 2.4's changes |
| `test_source_generation.py` | `from machinome.node import step` (twice); `mock.patch('machinome.node.jscad.Popen', ...)` (twice) |
| `test_source_set.py` | `mock.patch('machinome.node.jscad.Popen')` (twice) |
| `test_openscad_dependency.py` | `patch('machinome.node.solid2.Popen', ...)`, `patch('machinome.node.jscad.Popen', ...)` |
| `test_build123d_adapter.py` | `build123d_shape` from `machinome.node.build123d`, `workplane_shape` from `machinome.node.cadquery` |
| `test_backend_neutral_materialization.py` | `CadQueryNode` from `machinome.node.cadquery` |
| `test_external_wrapper_identity.py` | `_load_source_mesh` imported and patched at `machinome.node.stl` |
| `test_stl_node.py` | `patch('machinome.node.stl._load_source_mesh', ...)` |
| `test_sheet_leaf.py` | `patch('machinome.node.build123d._export_dxf', ...)` |
| `test_missing_source_file.py` | `patch('machinome.node.openscad.coherent_read')` |
| `tests/step_project/parts.py` | `from machinome.node.step import solids_from_faces` |
| `test_leaf_contract_reach.py` | `LEAVING` is `machinome/node/{cadquery,build123d,step,molejo}.py` (the sheet node is in `build123d.py`); the allowance is `('step.py', 'machinome.node.cadquery', 'workplane_shape')`; **and, beyond task 8.1's text,** four allowances `(<module>, 'machinome.extras', 'require_extra')`, one per kernel module, with the reason "in one distribution a kernel module refuses its absent extra at import; at the cut the node package requires its kernel and the check may go with the move" -- the leaf contract's declared modules are unchanged; the docstring names the four modules |
| `test_core_kernel_free.py` | the expectation names `machinome/node/step.py` (2.6) |
| `test_node_lazy_exports.py`, `test_cli_lazy_imports.py`, `test_exact_engine_seam.py`, `test_markings.py` | as 2.4 and 2.5 record |

A targeted run of the files most exposed to the move, before the whole
suite: `test_exact_engine_dependency.py test_front_end_free_exact.py
test_leaf_contract_{exact,members,version,recipe}.py test_step_node.py
test_step_assembly.py test_import_step.py test_sheet_leaf.py
test_build123d_adapter.py test_source_generation.py test_source_set.py
test_openscad_dependency.py test_stl_node.py
test_external_wrapper_identity.py test_missing_source_file.py
test_backend_neutral_materialization.py test_vet_{assertions,universe,command,isolation,closure}.py
test_machinome_identity.py test_docs_exports.py test_mechanics_boundary.py
test_no_class_name_recognition.py test_cli.py test_named_models.py`:
`477 passed, 2 skipped, 4 warnings, 333 subtests passed in 54.78s`.

### 4.2 The grep (8.2)

```
grep -rnE --exclude-dir=_build --exclude-dir=__pycache__ --exclude-dir=adrs \
  "node\.adapters|node/adapters|adapters\.|pip install cadquery" machinome tests docs README.rst
```

`pip install cadquery`: no match. What remains: the dissolved package's own
`__init__.py` (its docstring and its refusal); the node root's docstring
sentence saying the package was dissolved; `tests/test_leaf_addresses.py`
(the former spellings it proves refused) and `tests/test_docs_structure.py`
(the spelling it refuses); `docs/architecture.md` and the changelog bullet,
which describe the dissolution; and three prose sentences ending "adapters."
(`machinome/node/solid2.py:27`, `tests/test_external_wrapper_identity.py:175`,
`tests/test_missing_source_file.py:116`) that name no address. Outside the
pattern, `docs/contributor-briefing.md`'s layout line said "`adapters/`
contains CAD backends"; it now names the leaf modules (not in the task's
list; a contributor document pointing at an empty package).

### 4.3 The goldens (8.3)

```
tests/exact_engine_golden.py --check    golden comparison: 7 fixtures, 0 differences
tests/leaf_contract_golden.py --check   golden comparison: 7 fixtures, 97 values, 0 differences
tests/markings_golden.py --check        golden comparison: 18 values, 0 differences
```

### 4.4 The whole suite (8.4)

Run once, alone, after group 9's documentation so the one run covers it (no
other pytest process; checked with `pgrep`):

```
env -C <worktree> PYTHONPATH=<worktree> .venv/bin/python -m pytest -q -p no:cacheprovider -rf
25 failed, 4277 passed, 4 skipped, 53 warnings, 5 errors, 3440 subtests passed in 519.69s (0:08:39)
wall time 522 s
```

**Twenty-three failures and the five errors are environmental:** every one
is `OSError: [Errno 24] Too many open files`, or a subprocess dying in
`site` initialisation with `Fatal Python error: init_import_site` /
`error evaluating path` (the workspace's virtiofs descriptor exhaustion),
in the alphabetically last files: `test_verdict_store.py` (1),
`test_verdict_store_cli.py` (1, and the five setup errors of
`AcrossProcesses`), `test_vet_assertions.py` (4), `test_vet_command.py`
(2), `test_vet_isolation.py` (4), `test_vet_universe.py` (11). Re-run alone
afterwards, those files and `test_vet_closure.py` passed: `2 failed, 153
passed, 165 subtests passed in 92.40s`, the two being the following.

**Two failures were this change's:**
`test_lazy_test_framework.py::SimulationBrokenExport`'s
`test_reading_a_kernel_name_is_not_a_missing_attribute` (`'False'
unexpectedly found in 'PRESENT False'`) and
`test_using_a_kernel_name_raises_the_underlying_import_error` (`OTHER
ExactEngineUnavailable Comparing exact geometry requires the exact engine
... 'pip install "machinome[occt]"'`). Both refused `OCP` and pinned the
old reading, an absent OCP as a broken engine, which design.md Decision 6
reverses (an absent OCP is an absent engine, pinned by
`test_exact_engine_seam.py::AbsentKernelTest`). The trap they guard is a
*broken* kernel, so their `KERNEL_ABSENT` finder became `KERNEL_BROKEN`
(OCP found, its import raising `ImportError('broken OCP')`), the
assertions unchanged; the class docstring says why. The file:
`36 passed, 76 subtests passed in 39.05s`.

**The suite result of record** (the orchestrator's decision on 8.4): the
orchestrator ran the whole suite once, alone, on this uncommitted state at
19:34, sampling the test process's open file descriptors every 20 s:

```
4307 passed, 4 skipped, 53 warnings, 3457 subtests passed in 537.46s (0:08:57)
exit 0; no "Too many open files"; open descriptors peaked at 48 of a 65535 limit
```

The applier's run above stands as environmental: its 25 failures and 5
errors were all EMFILE or `init_import_site` in the alphabetically last
files, every one passing alone. The repointing of the two
`test_lazy_test_framework` tests was accepted as Decision 6's consequence.

Beside the backend-switch cycle's run (`4265 passed, 4 skipped, 3301
subtests passed in 512.57s`, wall 515 s): 4307 tests collected against
4269, the new and replaced tests of group 2 and group 9's two; wall time
within 7 s. Tests that skip by name when a kernel is absent: none was added
(Decision 11).

### 4.5 Lint (8.5)

`flake8 --max-line-length=89` (flake8 7.3.0) over the 46 changed or new
Python files: 104 findings, against 105 for the same files at ae64c2d
(the moved modules compared with their `adapters/` originals); none is new,
one (an E128 in `test_markings.py`) is gone. The remaining findings are the
files' pre-existing E128 and E501 lines (`step.py` 18 E128,
`import_step.py` 2 E128, `cli.py` 2 E501 help strings, the tests'). Four
introduced while writing (an E305 in `markings.py`, an E303, two W391) were
fixed before this count.

### 4.6 The manual (8.6)

No environment without the kernels was at hand, so the workspace venv:

```
env -C <worktree> PYTHONPATH=<worktree> .venv/bin/python -m sphinx -E -b html -W docs docs/_build/html
build succeeded.   (exit 0)
```

The API reference renders `machinome.node.CadQueryNode`, `Build123dNode`,
`Build123dSheetNode`, `StepNode` and `MolejoNode` (their anchors are in
`reference/api.html`). design.md's inference about Sphinx's mock finder was
then tested directly: the same build with `cadquery`, `build123d`, `OCP`
and `molejo` refused by the `sitecustomize` finder of
`tests/exact_engine_absent.py` (`EXACT_ENGINE_ABSENT_NAMES=cadquery,build123d,OCP,molejo`)
also exited 0 with the five anchors present, while `python -c 'import
machinome.node.step'` under the same finder refuses
(`machinome.extras.ExtraUnavailable: machinome.node.step (StepNode,
StepAssembly) needs cadquery, ...`): `autodoc_mock_imports`' finder answers
`find_spec` for every mocked kernel, so the documentation build passes the
check.

## 5. Empirical validation (tasks 11.1, 11.2)

Both run by the orchestrator, not by the applier; its reports, folded in
here verbatim where they quote a message or a summary line.

### 5.1 Deep: Actuators/Internal-Cycloidal-Actuator

Run in the project's own checkout
`projects/Actuators/Internal-Cycloidal-Actuator` on a branch
`lean-core-validation` from main c12d488, with
`PYTHONPATH=<bench>:<project>` and the workspace venv, faceted only (an
address move needs no certified exact run; the README's `--exact` leg was
dropped by the orchestrator). The project keeps its vendor STEP ignored, so
the usual worktree had no artifacts; see the finding below.

| leg | bench | `machinome build` | `machinome test --faceted simulation/actuator/test_machine.py` |
|---|---|---|---|
| before (18:31) | ae64c2d, unchanged code | exit 0 (artifacts reused and regenerated) | `Ran 35 tests in 56.30 seconds: 33 passed, 2 failed` |
| after (19:43) | ae64c2d plus this change, uncommitted, the project migrated | exit 0 | `Ran 35 tests in 48.33 seconds: 33 passed, 2 failed` |

The two failures, the same in both legs, are
`AttributeError: 'OCP.OCP.TopoDS.TopoDS_Shape' object has no attribute 'BoundingBox'`
and `... 'Faces'`: the first cycle's currency move (`exact-engine`), not
this cycle's.

**The migration**, three lines in `simulation/actuator/test_machine.py`:
the docstring's `machinome.node.adapters.step` → `machinome.node.step`;
`from machinome.node.adapters import step as step_module` → `from
machinome.node import step as step_module`; `from
machinome.node.adapters.step import StepAssembly` → `from
machinome.node.step import StepAssembly`. `1 file changed, 3
insertions(+), 3 deletions(-)`. Committed as b998dd0 "Validate machinome
lean-install: leaf addresses under machinome.node" on that branch; the
checkout was switched back to main, clean; the branch is never merged.

**The refusal probes** of design.md were run in the bench by the applier
(the three doors, `cadquery` blocked by the generalised finder written as a
`sitecustomize.py`) and stand as the cycle's probes; the orchestrator ran
none in the project. Each exited 1:

```
$ python -c "import machinome.node.cadquery"
machinome.extras.ExtraUnavailable: machinome.node.cadquery (CadQueryNode) needs cadquery, which is not installed; install it with 'pip install "machinome[cadquery]"'
$ python -c "from machinome.node import StepNode"
machinome.extras.ExtraUnavailable: machinome.node.step (StepNode, StepAssembly) needs cadquery, which is not installed; install it with 'pip install "machinome[step]"'
$ machinome import-step tests/step_project/import_simple.step --into <scratch>/sim     (and: machinome import-step -h)
Error: machinome import-step needs the step extra: machinome.node.step (StepNode, StepAssembly) needs cadquery, which is not installed; install it with 'pip install "machinome[step]"'
```

No traceback for the command, `<scratch>/sim` not created; `machinome -h`
exits 0 and lists `import-step`. **A departure from design.md's expected
text:** the last line of the two tracebacks names the class as Python
prints it, `machinome.extras.ExtraUnavailable:`, not `ModuleNotFoundError:`;
the class is a `ModuleNotFoundError` (its `name` the missing kernel), so the
`kernel-extras` requirement holds.

**A finding** (recorded in `workflow/warts.md`): a `machinome build` of this
project in a fresh git worktree (`WTs/lean-core-validation` under the
project, on its virtiofs path, with the ignored 35 MB vendor STEP copied
in) hung for three hours: the process alive with 4 s of CPU, an empty
`_build/actuator.lock`, no artifact and no child process; killed by the
orchestrator at 18:29. The same build in the project's primary checkout,
where artifacts exist, completed in under a minute. Not reproduced, not
triaged; the worktree was removed.

### 5.2 Shallow: the universe

From the workspace root at 19:45 (ended 20:07), bench ae64c2d plus this
change, uncommitted:

```
scripts/load-projects --bench <bench> \
  --moved scripts/load-projects.d/exact-engine.toml scripts/load-projects.d/leaf-contract.toml \
          scripts/load-projects.d/backend-switch.toml <bench>/openspec/changes/lean-install/moved-names.toml \
  --timeout 300 --json <bench>/openspec/changes/lean-install/load-projects.json
62 repositories, 129 rows: 117 ok, 4 expected, 2 unexpected, 0 timeout, 6 no-model; 2 skipped
Skipped: .Trash-1000 (skip rule), sandbox (skip rule)
exit 1
```

The full table is `load-projects.json`, archived beside this file (its
`counts` and `bench_commit` ae64c2db75c3 agree with the summary line).
Every row that is not `ok`:

| repository | class | cause |
|---|---|---|
| `3D-Printers/Voron-2` | expected, carried | the first cycle's `shape()` move |
| `Actuators/Internal-Cycloidal-Actuator` / `actuator` | expected, new | this cycle's `machinome.node.adapters` row (its main; the validation branch holds the migration) |
| `Robots/YouCanBuildDog` | expected, new | this cycle's `machinome.node.adapters` row |
| `Robots/openvmp` / `don1` | expected, new | this cycle's `machinome.node.adapters` row |
| `3DPrintedClocks` / `wall_clock_41` | unexpected, carried | its own CadQuery code |
| `Robotic-Arms/Dum-E` | unexpected, carried | the adapter not installed in the venv |
| KZG-Marble-machine, Dummy-Robot, Primo, asimov-1, berkeley-humanoid-sim, upkie | no-model | no declared model |

Against design.md's prediction (ICA and don1 expected): YouCanBuildDog's
companion test module also reaches the old address, so three new expected
rows rather than two; nothing unexpected is new. The other projects of the
fifteen files (Curta, Combination-safe-lock, OpenAstroMount,
open_robot_actuator_hardware) import the old address only in tools and
tests no model collects, which the shallow depth cannot see; they are rows
of the root cleanup's rewrite script.


## 6. ADRs, plan, warts, specs (group 12)

- **ADR-167** under `docs/adrs/NODE/`, "A kernel is an extra, and its module
  refuses its absence at import", amending ADR-161 (an absent `occt` extra
  is an absent engine) and citing ADR-046, ADR-059, ADR-162, ADR-168 and
  ADR-169. ADR-161's status line gains "absent-engine case amended
  2026-10-03 by ADR-167" and an *Amendment (2026-10-03)* section (design.md
  said ADR-167 amends ADR-161's absent-engine case; task 12.2 named only the
  other two amendments).
- **ADR-168** under `docs/adrs/BUILD/`, "The command table names the module
  a command needs", amending ADR-024 and ADR-059, which gain status lines
  and *Amendment (2026-10-03)* sections.
- **ADR-169** under `docs/adrs/NODE/`, "A leaf type is one module under
  `machinome.node`; the adapters package is dissolved", amending ADR-004's
  module layout (status line and amendment section; its References keep the
  historical paths), citing ADR-163, ADR-165 and ADR-167.
- `docs/adrs/README.md`: ADR-167 and ADR-169 under NODE after ADR-166,
  ADR-168 under BUILD after ADR-149; ADR-004 "layout amended by 169",
  ADR-024 "amended by 119, 168", ADR-059 "amended by 168", ADR-161 "amended
  by 167". The ADRs link the change at
  `openspec/changes/archive/2026-10-03-lean-install/`, which resolves with
  this archive.
- `workflow/ongoing/lean-core.md`: "Layers" item 4 marked **Done** 3 October
  2026 with ADR-167 to 169 and this file's path; the "Empirical validation"
  table's `lean-install` row (Internal-Cycloidal-Actuator, why) carries
  "**Done** 3 October 2026: ICA 33/35 faceted before and after, the two
  failures the first cycle's currency; universe 117 ok, three new expected
  rows, nothing unexpected" and this file's path; "Import paths" gains the
  sheet node's module and its reason; the "order does not matter" sentence
  gains the filter and the finding. Nothing else in the plan changed.
- `workflow/warts.md`: a section "Findings from the framework cycle
  `lean-install` (3 October 2026)" with the three-hour hang of a fresh
  worktree build, untriaged.
- **Specs.** `openspec archive lean-install --yes` applied the deltas
  itself (no refusal, unlike the third cycle): `cli` + 1 added, ~ 1
  modified; `cli-startup-cost` ~ 2; `exact-engine-dependency` ~ 1;
  `kernel-extras` created, + 3; `markings` + 1; `node-model` + 1;
  `occt-engine` ~ 1; `vet` ~ 1; "Totals: + 6, ~ 6, - 0, → 0", archived as
  `2026-10-03-lean-install`. A copy of `openspec/specs/` taken before the
  archive was diffed against the result: the removed lines are the old text
  of the six modified requirements and nothing else. Then by hand:
  `kernel-extras`' Purpose (the archive writes "TBD") states what the
  capability is, with ADR-167 and its code; `node-model`'s Purpose code list
  names the leaf modules instead of `adapters/`.

```
openspec validate --specs --strict   -> Totals: 41 passed, 0 failed (41 items)
```

After the ADRs, the plan amendment, the warts entry, the spec sync and the
archive (no source change since the orchestrator's whole-suite run), the
files that read specs, records and documentation were run alone with the
cycle's new files: `tests/test_leaf_contract_members.py
tests/test_release_records.py tests/test_missing_source_file.py
tests/test_docs_structure.py tests/test_docs_exports.py
tests/test_scad_import_paths.py tests/test_frame_precision_docs.py
tests/test_profile_documentation.py tests/test_kernel_extras.py
tests/test_leaf_addresses.py tests/test_core_kernel_free.py`:
`99 passed, 6 warnings, 470 subtests passed in 10.64s`.
