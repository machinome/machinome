# Evidence: `cut-the-brep-nodes`

The third cycle of the 0.9 monorepo campaign (`workflow/ongoing/monorepo-0.9.md`
at the repository root, "The campaign: the cut", cycle 3). Worktree
`machinome/WTs/v0.9-base-cut-the-brep-nodes`, branch
`v0.9-base-cut-the-brep-nodes`, cut from the line `v0.9-base` at 84757c38
("Implement cut-the-engines"). Planning commit bdadf767, ratified by the
orchestrator's review. Applied on 10 October 2026.

Tools: uv 0.11.8, CPython 3.12.3 (the bench venv), the OpenSpec CLI 1.6.0,
git 2.43.0. Every command ran with `env -C <dir>` and absolute paths; `<bench>`
is `/home/asa/devel/machinome/machinome/WTs/v0.9-base-cut-the-brep-nodes` and
`<scratch>` is
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C3-apply/`.
Every test ran from `<bench>/packages/machinome` on the bench venv
(`<bench>/.venv/bin/python -m pytest -q -p no:cacheprovider ...`), one pytest
process at a time. Logs are in `<scratch>`, never in the bench.

## 1. Evidence baseline

### 1.1 The base (task 1.1)

```
$ git -C <bench> log --oneline -2
bdadf767 Propose cut-the-brep-nodes: the CadQuery, build123d, STEP and molejo node types as extension packages (decided 10 October 2026)
84757c38 Implement cut-the-engines: the B-rep and mesh engines as the first extension packages
$ git -C <bench> status --short | wc -l
0
```

`git status --short --ignored` showed `!! .env` alone (the bench's port file).

### 1.2 The bench venv on the base's tree (task 1.2)

```
$ env -C <bench> /home/asa/.local/bin/uv sync --python 3.12
Using CPython 3.12.3 interpreter at: /usr/bin/python3.12
Creating virtual environment at: .venv
Resolved 179 packages in 4ms
...
Installed 170 packages in 9.85s
$ uv pip list --python <bench>/.venv/bin/python | tail -n +3 | wc -l
170
```

179 resolved, 170 installed. Three `__editable__` files, one line each:

```
__editable__.machinome-0.8.1.pth: <bench>/packages/machinome
__editable__.machinome_engine_brep-0.8.1.pth: <bench>/packages/machinome-engine-brep
__editable__.machinome_engine_mesh-0.8.1.pth: <bench>/packages/machinome-engine-mesh
```

`git status --short --ignored` afterwards: `.env`, `.venv/` and the three
members' `*.egg-info/`, all ignored. The base suite on the same tree and
recipe, recorded from the second cycle's evidence (9.1), not rerun: `4786
passed, 20 skipped, 6831 subtests passed`.

### 1.3 The lint base (task 1.3)

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/flake8 --max-line-length=89 machinome tests ../machinome-engine-brep/machinome ../machinome-engine-mesh/machinome | wc -l
759
```

2 of them E402, both in `tests/test_couplings.py` (`<scratch>/1.3-lint.txt`).

### 1.4 The sweep base (task 1.4, recorded, not rerun)

The second cycle's counts (design.md, Decision 14): 63 repositories, 130
rows, 121 ok, 0 expected, 3 unexpected (wall_clock_41's own CadQuery error,
Dum-E without machinome-freecad, fender-bender without `fb_library`), 0
timeout, 6 no-model, 2 skipped.

## 2. Red first, at the base's paths

Nothing moved in this group.

### 2.1 The layout gate (task 2.1)

`tests/test_repository_layout.py`: `ENGINES` replaced by `EXTENSIONS`
(design.md Decision 10, verbatim); the group's four per-package tests renamed
and generalised (`test_each_extension_directory_holds_only_what_distinguishes_it`,
`test_each_extension_manifest_is_a_portion_of_the_set`,
`test_each_extension_readme_names_its_install_and_the_licence`,
`test_each_portion_resolves_from_its_package`, the last checking an engine's
seam only for the two engine rows); `test_the_core_node_package_holds_no_extension_module`
and `test_every_sibling_is_in_the_table` added;
`test_the_core_engine_package_holds_only_the_seams` unchanged; the module
docstring names the node packages.

```
$ ... pytest tests/test_repository_layout.py
20 failed, 28 passed, 88 subtests passed in 5.98s
```

(`<scratch>/2.1-layout-red.txt`; the 20 are subtests.)

- `test_each_extension_directory_holds_only_what_distinguishes_it`, the four
  node subtests: `<bench>/packages/machinome-node-<x> is missing`.
- `test_each_extension_manifest_is_a_portion_of_the_set`, the four:
  `FileNotFoundError` on `packages/machinome-node-<x>/pyproject.toml`.
- `test_each_extension_readme_names_its_install_and_the_licence`, the four:
  `FileNotFoundError` on the four `README.md`.
- `test_each_portion_resolves_from_its_package`, the four:
  `.../packages/machinome/machinome/node/<x>.py != .../packages/machinome-node-<x>/machinome/node/<x>.py`.
- `test_the_core_node_package_holds_no_extension_module`, the four:
  `.../packages/machinome/machinome/node/<x>.py is in the core`.

Green as expected: the engine subtests of the four per-package tests,
`test_every_sibling_is_in_the_table` (two siblings, both keys), the README
test and `test_the_guide_installs_every_member_without_uv` (no node
directory yet).

### 2.2 `tests/test_kernel_extras.py` (task 2.2)

`EXTRAS['cadquery']`, `['build123d']`, `['step']` and `['molejo']` each
`{f'machinome-node-<x>~={VERSION}'}`; `ENGINE_REQUIREMENTS` renamed
`PACKAGE_REQUIREMENTS` with the four node manifests' sets of Decision 2
(and `NODE_PACKAGES`, its four node keys); `engine_manifest` renamed
`package_manifest`, `sibling_manifests()` added (every
`packages/machinome-*/pyproject.toml` present);
`test_every_kernel_extra_includes_the_brep_extra` replaced by
`test_every_node_package_requires_the_brep_engine`;
`test_no_node_extra_includes_the_mesh_engine` also reads the node manifests
present; `test_cadquery_carries_one_range_wherever_it_is_named` reads the
core and every sibling manifest; `test_each_engine_requires_the_core_and_its_kernel`
renamed `test_each_extension_package_requires_the_core_and_its_kernel`
(departure 1); the docstring names the node manifests.

```
$ ... pytest tests/test_kernel_extras.py
13 failed, 16 passed, 40 subtests passed in 1.79s
```

- `test_each_extra_lists_what_its_module_needs`, subtests `cadquery`,
  `build123d`, `step`, `molejo`: e.g. `{'cadquery==2.7.*', 'machinome[brep]'}`
  against `{'machinome-node-cadquery~=0.8.1'}`.
- `test_each_extension_package_requires_the_core_and_its_kernel`, the four
  node subtests: `FileNotFoundError` on `packages/machinome-node-<x>/pyproject.toml`.
- `test_every_node_package_requires_the_brep_engine`, four subtests:
  `.../packages/machinome-node-<x>/pyproject.toml is missing`.
- `test_the_lock_installs_every_kernel`: `'machinome-node-molejo'`,
  `'machinome-node-step'`, `'machinome-node-cadquery'`,
  `'machinome-node-build123d'` not in the lock.

### 2.3 `tests/test_core_kernel_free.py` (task 2.3)

The two core censuses keep the template alone;
`test_the_engine_packages_import_only_their_kernels` renamed
`test_the_extension_packages_import_only_their_kernels`, with the five
entries (the two engines, `build123d.py: ['build123d']`, `molejo.py:
['molejo']`, `step.py: ['OCP', 'cadquery']`; `cadquery.py` imports no
kernel); `EXTRA_OF`'s four node keys and `SEAMS`' step key spelled
`machinome-node-<x>/machinome/node/<x>.py`; the seams test reads
`every_module()` and `portion_modules()`; the docstring.

```
$ ... pytest tests/test_core_kernel_free.py
9 failed, 7 passed, 17 subtests passed in 4.18s
```

- `test_no_core_module_imports_the_kernel_or_cadquery`: the census holds
  `'machinome/node/step.py': ['OCP', 'cadquery']` besides the template.
- `test_kernels_are_imported_only_by_their_modules`: it holds the
  `build123d.py`, `molejo.py` and `step.py` rows.
- `test_the_extension_packages_import_only_their_kernels`: the portion scan
  finds the two engines alone.
- `test_each_kernel_module_checks_its_kernel_first`, four subtests:
  `KeyError: 'machinome-node-<x>/machinome/node/<x>.py'`.
- `test_kernel_modules_are_named_only_at_the_seams`, two subtests: the seam
  `machinome-node-step/machinome/node/step.py` (`None !=
  {'machinome.node.cadquery'}`, the key absent from the scan), and the path
  `machinome/node/step.py` (`{'machinome.node.cadquery'} not less than or
  equal to set()`, the core's step module naming the CadQuery module under a
  key `SEAMS` no longer holds). The second is the same fact as the first,
  seen from the core's side.

### 2.4 `tests/test_leaf_contract_reach.py` (task 2.4)

`LEAVING` through `importlib.util.find_spec(f'machinome.node.{name}').origin`
(`NODE` dropped); the `ALLOWED` reasons: `step.py -> machinome.node.cadquery`
"machinome-node-step requires machinome-node-cadquery (`cut-the-brep-nodes`)",
and `require_extra` "... at the cut (`cut-the-brep-nodes`) the check stays in
the module that moved"; the docstring.

```
$ ... pytest tests/test_leaf_contract_reach.py
5 passed, 20 subtests passed in 0.26s
```

Its red without this edit is design.md probe 7 (six `FileNotFoundError` on
`packages/machinome/machinome/node/<x>.py`).

### 2.5 `tests/test_docs_structure.py` (task 2.5)

`test_the_installation_page_names_the_engine_distributions` replaced by
`test_the_installation_page_names_the_extension_distributions`, the six
names written out.

```
$ ... pytest tests/test_docs_structure.py
4 failed, 17 passed, 763 subtests passed in 0.31s
```

The four node subtests: `machinome-node-<x>` not found on `start/install.rst`.

### 2.6 `tests/test_supported_node_types.py` (task 2.6)

`absent` among the names `test_the_module_defines_only_the_table_and_its_readers`
expects; `AbsentPackageTest` added: each door runs in its own subprocess
(`tests/brep_engine_absent.py`'s `run_python`, nothing blocked) that drops
`<repository>/packages/machinome-node-step` from `sys.path` before importing
`machinome.node`. `test_every_door_refuses_the_absent_package_by_its_extra`
has four subtests (`import machinome.node.step`, `from machinome.node.step
import StepNode`, `from machinome.node import step`, `hasattr(machinome.node,
'step')`), each expecting `['ExtraUnavailable', 'machinome.node.step',
'step', <load's sentence>]`; `test_the_other_node_packages_still_import`
expects `machinome.node.cadquery` to import there.

```
$ ... pytest tests/test_supported_node_types.py
5 failed, 11 passed, 33 subtests passed in 12.74s
```

- `test_the_module_defines_only_the_table_and_its_readers`: `Items in the
  second set but not the first: 'absent'`.
- `test_every_door_refuses_the_absent_package_by_its_extra`, the four doors:
  `['passed', None]` for the three imports and `['passed', True]` for
  `hasattr` (the module is in the core and imports; no refusal).
- `test_the_other_node_packages_still_import`: green.

### 2.7 `tests/test_markings.py` (task 2.7)

`ArtworkSeamTest.test_a_stale_marking_without_the_reducer_package_is_refused`:
`BUILD_PLATE` behind a prelude dropping `<repository>/packages/machinome-node-build123d`
from `sys.path`, nothing blocked; it expects `ExtraUnavailable` (a
`ModuleNotFoundError`) with the message `marking badge of Plate (artwork
badge.svg) needs machinome.node.build123d, which is not installed; install
it with 'pip install "machinome[build123d]"'` and no marking artifact.

```
$ ... pytest tests/test_markings.py::ArtworkSeamTest
1 failed, 3 passed in 14.39s
```

Red: `'error' not found in {...}`: the build succeeded and wrote
`plate-...marking-badge.stl` and `plate-...marking-band.stl` (the reducer is
in the core).

### 2.8 (task 2.8)

Every red above is the one tasks.md names, with the reason it names; the
one addition is the second subtest of the seams test in 2.3, recorded there.

## 3. The cut

### 3.1 The move (task 3.1)

```
$ for x in cadquery build123d step molejo; do
    mkdir -p <bench>/packages/machinome-node-$x/machinome/node
    git -C <bench> mv packages/machinome/machinome/node/$x.py packages/machinome-node-$x/machinome/node/$x.py
  done
$ git -C <bench> diff --cached -M100% --name-status | grep ^R
R100	packages/machinome/machinome/node/build123d.py	packages/machinome-node-build123d/machinome/node/build123d.py
R100	packages/machinome/machinome/node/cadquery.py	packages/machinome-node-cadquery/machinome/node/cadquery.py
R100	packages/machinome/machinome/node/molejo.py	packages/machinome-node-molejo/machinome/node/molejo.py
R100	packages/machinome/machinome/node/step.py	packages/machinome-node-step/machinome/node/step.py
```

Four renames, no content change.

### 3.2 The links (task 3.2)

`ln -s ../../LICENSE LICENSE` and `ln -s ../../LICENSES LICENSES` in each
node directory, then `git add`:

```
$ git -C <bench> ls-files -s 'packages/machinome-node-*' | grep ^120000 | wc -l
8
```

Each `LICENSE` reads `../../LICENSE` (blob 30cff740) and each `LICENSES`
`../../LICENSES` (blob 06ad40db), the engines' blobs.

### 3.3 The moved tree before the manifests (task 3.3)

`test_leaf_contract_reach.py` cannot be collected on this tree:

```
$ ... pytest tests/test_repository_layout.py tests/test_core_kernel_free.py tests/test_leaf_contract_reach.py tests/test_supported_node_types.py
1 error in 1.26s
ERROR tests/test_leaf_contract_reach.py - AttributeError: 'NoneType' object has no attribute 'origin'
```

(`find_spec` returns `None`: the bench venv's `.pth` lines name the core and
the engines alone, so the four modules are on no path.) The three others
(`<scratch>/3.3-moved-2.txt`):

```
$ ... pytest tests/test_repository_layout.py tests/test_core_kernel_free.py tests/test_supported_node_types.py
36 failed, 46 passed, 140 subtests passed in 10.88s
```

- `test_every_member_is_a_workspace_source`: the sources lack the four
  `machinome-node-<x>` (four directories, no source).
- `test_the_members_are_the_package_directories`, four subtests:
  `<bench>/packages/machinome-node-<x> holds no pyproject.toml` (not named
  by the task; the same absence as the manifest test's).
- `test_the_readme_links_every_package_and_states_the_licence`, four:
  `'packages/machinome-node-<x>/' not found` (probe 7).
- `test_the_guide_installs_every_member_without_uv`, four:
  `CONTRIBUTING.rst does not name -e packages/machinome-node-<x>` (probe 7).
- `test_each_extension_directory_holds_only_what_distinguishes_it`, four: the
  listing is `['LICENSE', 'LICENSES', 'machinome/node/<x>.py']`, without
  `README.md` and `pyproject.toml`.
- `test_each_extension_manifest_is_a_portion_of_the_set` and
  `test_each_extension_readme_names_its_install_and_the_licence`, four each:
  `FileNotFoundError`.
- `test_each_portion_resolves_from_its_package`, four: `ModuleNotFoundError:
  No module named 'machinome.node.<x>'`.
- `test_supported_node_types.py`: the names test (`absent`);
  `test_the_root_refuses_each_class_naming_its_module` (`ModuleNotFoundError`
  for the four); `AbsentPackageTest`: the doors `import` and `from-module`
  `['ModuleNotFoundError', 'machinome.node.step', None, "No module named
  'machinome.node.step'"]`, `from-root` `['ImportError', 'machinome.node',
  None, "cannot import name 'step' ..."]`, `hasattr` `['passed', False]`;
  `test_the_other_node_packages_still_import` (`No module named
  'machinome.node.cadquery'`).

Green: `test_core_kernel_free.py` whole (it reads the source where it now
is), the node link checks, `test_the_core_node_package_holds_no_extension_module`,
`test_the_core_engine_package_holds_only_the_seams` and
`test_every_sibling_is_in_the_table`. The last one's red, shown once:

```
$ mkdir <bench>/packages/machinome-node-stray
$ ... pytest tests/test_repository_layout.py::TheExtensionPackagesTest::test_every_sibling_is_in_the_table
1 failed, 1 passed, 6 subtests passed in 0.12s
AssertionError: 'machinome-node-stray' not found in {...} : packages/machinome-node-stray is not in EXTENSIONS
$ rmdir <bench>/packages/machinome-node-stray
```

## 4. The manifests, the core's extras and the workspace

### 4.1 The manifests (task 4.1)

The four `pyproject.toml` of design.md Decision 2, verbatim; each is
byte-identical to the probed draft (`diff
<C3-propose>/drafts/machinome-node-<x>/pyproject.toml`: no output, four
times). Their dependencies, read with `tomllib`:

```
machinome-node-cadquery  ['machinome~=0.8.1', 'cadquery==2.7.*', 'machinome-engine-brep~=0.8.1']
machinome-node-build123d ['machinome~=0.8.1', 'build123d==0.10.*', 'ocp-gordon>=0.2.2,<0.3', 'machinome-engine-brep~=0.8.1', 'numpy']
machinome-node-step      ['machinome~=0.8.1', 'machinome-node-cadquery~=0.8.1', 'cadquery==2.7.*', 'machinome-engine-brep~=0.8.1', 'numpy']
machinome-node-molejo    ['machinome~=0.8.1', 'molejo[brep]==0.2.*', 'machinome-engine-brep~=0.8.1', 'trimesh']
```

```
$ ... pytest tests/test_release_records.py
4 failed, 13 passed, 83 subtests passed in 0.24s
```

The four failures are `test_the_version_is_bumped_from_the_root`'s node
subtests (`'packages/machinome-node-<x>/pyproject.toml' not found in [...]`,
no table); `test_every_member_is_numbered_with_the_core` and
`test_every_pin_between_members_is_compatible` green. The pin test's red,
shown once:

```
$ sed -i 's/"machinome-node-cadquery~=0.8.1",/"machinome-node-cadquery>=0.8.1",/' <bench>/packages/machinome-node-step/pyproject.toml
$ ... pytest tests/test_release_records.py -k test_every_pin_between_members_is_compatible
1 failed, 1 passed, 12 deselected, 12 subtests passed in 0.14s
SUBFAILED(member='machinome-node-step', requirement='machinome-node-cadquery>=0.8.1') ... AssertionError: '>=0.8.1' != '~=0.8.1'
```

The manifest restored from its copy; `diff` against the draft: no output.

### 4.2 The READMEs (task 4.2)

The four `README.md` of Decision 2, verbatim; each byte-identical to the
probed draft (`diff`: no output, four times).

### 4.3 The core's manifest (task 4.3)

`packages/machinome/pyproject.toml`: the kernel extras' block replaced by
Decision 4's, and the `dependencies` comment's first clause as Decision 4
says, the rest of it unchanged.

```
$ git -C <bench> diff packages/machinome/pyproject.toml | grep -c '^@@'
2
$ git -C <bench> diff --stat packages/machinome/pyproject.toml
 packages/machinome/pyproject.toml | 44 +++++++++++++++------------------------
```

### 4.4 The workspace (task 4.4)

The root `pyproject.toml`'s four sources of Decision 7.

```
$ env -C <bench> /home/asa/.local/bin/uv lock
Resolved 183 packages in 497ms
Added machinome-node-build123d v0.8.1
Added machinome-node-cadquery v0.8.1
Added machinome-node-molejo v0.8.1
Added machinome-node-step v0.8.1
$ grep -c '^\[\[package\]\]' <bench>/uv.lock
183
$ grep -n 'source = { editable = "packages/' <bench>/uv.lock
1806:source = { editable = "packages/machinome" }
1936:source = { editable = "packages/machinome-engine-brep" }
1953:source = { editable = "packages/machinome-engine-mesh" }
1982:source = { editable = "packages/machinome-node-build123d" }
2003:source = { editable = "packages/machinome-node-cadquery" }
2020:source = { editable = "packages/machinome-node-molejo" }
2039:source = { editable = "packages/machinome-node-step" }
```

`diff` of the lock against the base's: 124 changed lines. The step
package's entry lists `cadquery`, `machinome`, `machinome-engine-brep`,
`machinome-node-cadquery` and `numpy`, the three members `editable`.

```
$ env -C <bench> /home/asa/.local/bin/uv sync --python 3.12
Resolved 183 packages in 5ms
...
Prepared 5 packages in 1.59s
Uninstalled 1 package in 3ms
Installed 5 packages in 17ms
 ~ machinome==0.8.1
 + machinome-node-build123d==0.8.1
 + machinome-node-cadquery==0.8.1
 + machinome-node-molejo==0.8.1
 + machinome-node-step==0.8.1
$ uv pip list --python <bench>/.venv/bin/python | tail -n +3 | wc -l
174
```

Incremental on 1.2's venv; 174 in the venv, probe 1's count for a fresh
sync. The seven `__editable__` files, one line each:

```
__editable__.machinome-0.8.1.pth: <bench>/packages/machinome
__editable__.machinome_engine_brep-0.8.1.pth: <bench>/packages/machinome-engine-brep
__editable__.machinome_engine_mesh-0.8.1.pth: <bench>/packages/machinome-engine-mesh
__editable__.machinome_node_build123d-0.8.1.pth: <bench>/packages/machinome-node-build123d
__editable__.machinome_node_cadquery-0.8.1.pth: <bench>/packages/machinome-node-cadquery
__editable__.machinome_node_molejo-0.8.1.pth: <bench>/packages/machinome-node-molejo
__editable__.machinome_node_step-0.8.1.pth: <bench>/packages/machinome-node-step
```

From `/tmp`, with the venv's Python:

```
__path__ ['<bench>/packages/machinome/machinome/node', '<bench>/packages/machinome-node-build123d/machinome/node', '<bench>/packages/machinome-node-cadquery/machinome/node', '<bench>/packages/machinome-node-molejo/machinome/node', '<bench>/packages/machinome-node-step/machinome/node']
cadquery <bench>/packages/machinome-node-cadquery/machinome/node/cadquery.py
build123d <bench>/packages/machinome-node-build123d/machinome/node/build123d.py
step <bench>/packages/machinome-node-step/machinome/node/step.py
molejo <bench>/packages/machinome-node-molejo/machinome/node/molejo.py
one workplane_shape True
```

`git status --short --ignored` under `packages/machinome-node-*`: the
manifests and READMEs (then `git add`ed), and, ignored, each directory's
`*.egg-info/` and `machinome/node/__pycache__/`; nothing else.

### 4.5 Group 2's modules and the seams (task 4.5)

```
$ ... pytest tests/test_repository_layout.py tests/test_kernel_extras.py tests/test_core_kernel_free.py tests/test_leaf_contract_reach.py tests/test_docs_structure.py tests/test_supported_node_types.py tests/test_markings.py tests/test_release_records.py tests/test_node_root.py tests/test_import_step.py tests/test_manager_new.py tests/test_step_node.py tests/test_molejo_adapter.py tests/test_build123d_adapter.py tests/test_cli_lazy_imports.py
22 failed, 430 passed, 1 skipped, 6 warnings, 1335 subtests passed in 46.95s
```

The 22, each one tasks.md names:

- the layout README test and `test_the_guide_installs_every_member_without_uv`,
  four node subtests each (group 9);
- `test_the_installation_page_names_the_extension_distributions`, four
  (group 9);
- `test_the_version_is_bumped_from_the_root`, four (group 7);
- `test_the_module_defines_only_the_table_and_its_readers` (`absent`);
- `AbsentPackageTest`'s four doors, now the cut's reds: `import` and
  `from-module` `['ModuleNotFoundError', 'machinome.node.step', None, "No
  module named 'machinome.node.step'"]` (no extra), `from-root`
  `['ImportError', 'machinome.node', None, "cannot import name 'step' from
  'machinome.node' (...)"]`, `hasattr` `['passed', False]`;
- the markings test of 2.7: `ModuleNotFoundError` with the message `No module
  named 'machinome.node.build123d'`, naming neither the part, the marking,
  the artwork nor the extra, and `markings` `{}` (`pytest -l`,
  `<scratch>/4.5-markings-l.txt`).

The one skip is `test_cli_lazy_imports.py`'s viewer test, the base's. Nothing
else red.

### 4.6 The node root's text gate (task 4.6)

Planted in a comment at the end of the moved `step.py`, written with
`printf '# %s%s\n' 'from machinome.node ' 'import StepNode'`: the line `#
from machinome.node import StepNode`. The gate as it was:

```
$ ... pytest tests/test_node_root_exports_nothing.py
22 passed, 106 subtests passed in 3.01s
```

Repointed: the G2 test merges `scan(package)` of every
`packages/machinome-*`, its paths prefixed by the directory's name (and the
module docstring says so; `REPOSITORY` added). With the plant:

```
$ ... pytest tests/test_node_root_exports_nothing.py
1 failed, 21 passed, 106 subtests passed in 3.41s
machinome: 1 files, 1 offences
    1 machinome-node-step/machinome/node/step.py (932: from machinome.node import StepNode)
```

The plant removed (`git diff` of `step.py`: empty; still `R100`), then:
`22 passed, 106 subtests passed in 3.04s`.

### 4.7 The split-words gate (task 4.7)

`tests/test_core_names_no_split_words.py` unchanged. Planted with `printf
'# a %s%s plant\n' fac eted` at the end of the moved `molejo.py`:

```
$ ... pytest tests/test_core_names_no_split_words.py
1 failed, 10 passed, 56 subtests passed in 0.82s
AssertionError: {'machinome/node/molejo.py': (1, [(105, '# a faceted plant')])} != {}
```

The plant removed (`git diff` of `molejo.py`: empty), then: `11 passed, 56
subtests passed in 0.77s`.

## 5. The absent node package (design.md Decision 5)

### 5.1 The code (task 5.1)

`machinome/node/supported.py`: `absent(key)` verbatim, before `load`, and
`load`'s branch `raise absent(key) from None`. `machinome/node/__init__.py`:
`import sys as _sys` and `from importlib.machinery import ModuleSpec as
_ModuleSpec` among its imports, `_AbsentNodeType` and its installation
verbatim after `__path__ = _namespace_portions(...)`, and the docstring
sentence in "The refusals." (the paragraph's following lines rewrapped to
its width, no word changed). `git diff` of the two modules shows these and
nothing else; `flake8 --max-line-length=89` of the two: no output.

### 5.2 The tests (task 5.2)

```
$ ... pytest tests/test_supported_node_types.py tests/test_markings.py::ArtworkSeamTest
16 passed, 37 subtests passed in 9.79s
$ ... pytest tests/test_node_root.py tests/test_node_root_exports_nothing.py tests/test_cli_lazy_imports.py tests/test_import_step.py tests/test_leaf_addresses.py tests/test_manager_new.py tests/test_cli.py tests/test_kernel_extras.py
169 passed, 1 skipped, 367 subtests passed in 29.12s
```

(the skip: `test_cli_lazy_imports.py`'s viewer test, the base's.)

### 5.3 By hand, the package uninstalled (task 5.3)

A 4 x 5 x 6 box written by CadQuery to `<scratch>/5.3/box.step`; the command
run from `<scratch>/5.3/p/`, an empty directory.

```
$ uv pip uninstall --python <bench>/.venv/bin/python machinome-node-step
Uninstalled 1 package in 29ms
 - machinome-node-step==0.8.1
$ env -C <scratch>/5.3/p <bench>/.venv/bin/machinome import-step ../box.step
Error: machinome import-step needs the step extra: the step node type (StepNode) needs machinome.node.step, which is not installed; install it with 'pip install "machinome[step]"'
exit 1
$ ls -A <scratch>/5.3/p
(nothing)
```

The refusal at each door, with the package uninstalled, from `/tmp`
(`machinome.node.__path__` has four entries), after Decision 5, and before
it (the same interpreter with `_AbsentNodeType` removed from
`sys.meta_path` after importing `machinome.node`, `<scratch>/5.3/nofinder.py`;
the "before" of 4.5 was the suite's, this is by hand):

| Door | Before (the cut alone) | After (Decision 5) |
|---|---|---|
| `import machinome.node.step` | `ModuleNotFoundError`, name `machinome.node.step`, no extra, "No module named 'machinome.node.step'" | `ExtraUnavailable`, name `machinome.node.step`, extra `step`, load's sentence |
| `from machinome.node.step import StepNode` | the same `ModuleNotFoundError` | the same `ExtraUnavailable` |
| `from machinome.node import step` | `ImportError`, name `machinome.node`, "cannot import name 'step' from 'machinome.node' (...)" | the same `ExtraUnavailable` |
| `hasattr(machinome.node, 'step')` | `False` | raises the same `ExtraUnavailable` |
| `machinome import-step ../box.step` | "Error: machinome import-step needs the step extra: the step node type (StepNode) needs machinome.node.step, which is not installed; install it with 'pip install "machinome[step]"'", exit 1 | the same, exit 1 |

`type(sys.meta_path[-1]).__name__` after importing `machinome.node`:
`_AbsentNodeType`. Then `machinome-node-build123d` uninstalled too, and
`tests/markings_project`'s `Plate().assemble()` (its markings stale in a new
build directory) run from the framework's directory:

| Door | Before | After |
|---|---|---|
| the markings' artwork seam | `ModuleNotFoundError: No module named 'machinome.node.build123d'`, 0 marking artifacts | `ExtraUnavailable: marking badge of Plate (artwork badge.svg) needs machinome.node.build123d, which is not installed; install it with 'pip install "machinome[build123d]"'`, 0 marking artifacts |

```
$ env -C <bench> /home/asa/.local/bin/uv sync --python 3.12
Resolved 183 packages in 9ms
Installed 2 packages in 21ms
 + machinome-node-build123d==0.8.1
 + machinome-node-step==0.8.1
```

Two installed, since two were uninstalled (the task expects one, for the
step package alone); seven `.pth` files and 174 packages again.

## 6. The manual's path (design.md Decision 6)

### 6.1 Red first (task 6.1)

```
$ /usr/bin/python3.12 -m venv <scratch>/docs-venv
$ <scratch>/docs-venv/bin/pip install -q -r <bench>/packages/machinome/docs/requirements.txt
(Sphinx 9.1.0, sphinx_rtd_theme 3.1.0, machinome-viewer 0.8.0 from the index)
$ env -C <bench>/packages/machinome <scratch>/docs-venv/bin/python -m sphinx -b html -W --keep-going docs <scratch>/html-red
build finished with problems, 5 warnings (with warnings treated as errors).
exit 1
```

The five `autodoc: failed to import`: `cadquery.CadQueryNode`,
`build123d.Build123dNode`, `build123d.Build123dSheetNode`, `step.StepNode`
and `molejo.MolejoNode` from `machinome.node`. Each exception is the node
root's refusal, since group 5 is in the tree (probe 8 ran without it and
saw `No module named 'machinome.node.<x>'`), e.g.
`machinome.extras.ExtraUnavailable: the step node type (StepNode) needs
machinome.node.step, which is not installed; install it with 'pip install
"machinome[step]"'`.

### 6.2 `docs/conf.py` (task 6.2)

Its first lines as Decision 6 states, verbatim. The same build into
`<scratch>/html`:

```
build succeeded.
exit 0
```

54 HTML pages; `reference/api.html` holds one anchor each for
`machinome.node.cadquery.CadQueryNode`, `machinome.node.build123d.Build123dNode`,
`.Build123dSheetNode`, `machinome.node.step.StepNode` and
`machinome.node.molejo.MolejoNode`.

## 7. One version for the set, and the lint

### 7.1 The root `.bumpversion.cfg` (task 7.1)

The eight tables of Decision 8 after the mesh engine's, in the order
`cadquery`, `build123d`, `step`, `molejo`, no comment.

```
$ ... pytest tests/test_release_records.py
13 passed, 91 subtests passed in 0.21s
```

### 7.2 The bump on a copy (task 7.2)

The root's `.bumpversion.cfg` and the ten files its tables name copied under
`<scratch>/bump/` (their paths kept), made a git repository and committed:

```
$ env -C <scratch>/bump <bench>/.venv/bin/bump2version --no-commit --no-tag --new-version 0.9.0 patch
exit 0
$ git -C <scratch>/bump diff --stat | tail -1
 11 files changed, 28 insertions(+), 28 deletions(-)
```

The 28 statements (`<scratch>/7.2-bump.diff`), each `0.8.1` to `0.9.0`:
`current_version` (`.bumpversion.cfg`); `version` in the seven manifests and
in `machinome/vet/universe.toml`; `__version__`; `release` in `docs/conf.py`;
and 17 pins: the core's six (`machinome-engine-brep`, `-engine-mesh`,
`machinome-node-cadquery`, `-build123d`, `-step`, `-molejo`), each engine's
`machinome~=`, two in the CadQuery package (`machinome`,
`machinome-engine-brep`), two in the build123d package, two in the molejo
package, three in the STEP package (`machinome`, `machinome-node-cadquery`,
`machinome-engine-brep`). Nothing else: the viewer floors
(`machinome-viewer>=0.8.1`) do not move (0 lines), and `.bumpversion.cfg`'s
only change is `current_version`. Nothing was written in the bench.

### 7.3 The lint (task 7.3)

`packages/machinome/setup.cfg`'s two per-file ignores, in place:
`../machinome-node-step/machinome/node/step.py:E402` and
`../machinome-node-molejo/machinome/node/molejo.py:E402`.

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/flake8 --max-line-length=89 machinome tests ../machinome-engine-brep/machinome ../machinome-engine-mesh/machinome ../machinome-node-cadquery/machinome ../machinome-node-build123d/machinome ../machinome-node-step/machinome ../machinome-node-molejo/machinome | wc -l
759
```

Sorted, with the `../machinome-node-<x>/` prefix stripped, equal line for
line to 1.3's list (`diff`: no output); 18 lines name a node package's path;
`grep -c E402`: 2, both `tests/test_couplings.py`, as at the base. A first
run counted 760: the docstring of `tests/test_leaf_contract_reach.py` as
edited at 2.4 held one line of 106 characters (E501); rewrapped, no word
changed, then the run above.

## 8. `scripts/check-dist`

### 8.1 Red first (task 8.1)

With the four directories founded and no rows:

```
$ env -C <bench> <bench>/.venv/bin/python scripts/check-dist
check-dist failed: machinome-node-build123d has no smoke in scripts/check-dist
Nothing uploaded.
exit 1
```

### 8.2 The rows (task 8.2)

`NODE` and `NODE_LINE` beside `ENGINE`, a `node_smoke(name, node, parts,
operation)` builder beside `engine_smoke`, and four rows keyed by the node
distributions, each `'through'` its key, `'extras': []`, `'commands': []`.
Each smoke, with the venv's `python -I`: imports `machinome.node.<x>`; asserts
its distribution's version is `metadata.version('machinome')`, its files hold
`machinome/node/<x>.py` and no `__init__.py`, `locate_file` of the module is
the module's `__file__` inside the venv, and its requirements hold
`machinome~=<version>` and `machinome-engine-brep~=<version>`; writes, in a
new `tempfile.mkdtemp` directory under the temporary directory, a
`pyproject.toml` holding `[tool.machinome]` and a `parts.py` with one class
`Part`, puts it first on `sys.path` and makes it the working directory;
renders and measures with `brep_engine().solid_volume` (the four parts and
tolerances of Decision 11, the STEP row exporting the 4 x 5 x 6 box to
`box.step` first, the molejo row checking one solid and 0.1 % of the closed
form); the licence lines; one printed line. `git diff scripts/check-dist`
shows no removed line (the core's and the engines' rows unchanged).

```
$ env -C <bench> <bench>/.venv/bin/flake8 --max-line-length=89 scripts/check-dist | wc -l
0
```

### 8.3 The run (task 8.3)

`<scratch>/8.3-check-dist.txt`, exit 0:

```
Members: machinome, machinome-engine-brep, machinome-engine-mesh, machinome-node-build123d, machinome-node-cadquery, machinome-node-molejo, machinome-node-step
   machinome-0.8.1.tar.gz: 1030 entries
   machinome-0.8.1-py3-none-any.whl: 122 entries
   machinome_engine_brep-0.8.1.tar.gz: 18 entries
   machinome_engine_brep-0.8.1-py3-none-any.whl: 8 entries
   machinome_engine_mesh-0.8.1.tar.gz: 18 entries
   machinome_engine_mesh-0.8.1-py3-none-any.whl: 8 entries
   machinome_node_build123d-0.8.1.tar.gz: 18 entries
   machinome_node_build123d-0.8.1-py3-none-any.whl: 8 entries
   machinome_node_cadquery-0.8.1.tar.gz: 18 entries
   machinome_node_cadquery-0.8.1-py3-none-any.whl: 8 entries
   machinome_node_molejo-0.8.1.tar.gz: 18 entries
   machinome_node_molejo-0.8.1-py3-none-any.whl: 8 entries
   machinome_node_step-0.8.1.tar.gz: 18 entries
   machinome_node_step-0.8.1-py3-none-any.whl: 8 entries
$ <tmp>/venv/bin/python -m pip install --quiet --find-links <tmp>/dist/machinome ... (7 --find-links) <tmp>/dist/machinome/machinome-0.8.1-py3-none-any.whl[openscad,stl] machinome[brep] machinome[mesh] machinome[build123d] machinome[cadquery] machinome[molejo] machinome[step]
machinome 0.8.1 from <tmp>/venv/lib/python3.12/site-packages/machinome/__init__.py
   machinome --help: exit 0
machinome-engine-brep 0.8.1 provider <tmp>/venv/lib/python3.12/site-packages/machinome/engine/brep.py contract 2 result 999.9999999999998
machinome-engine-mesh 0.8.1 provider <tmp>/venv/lib/python3.12/site-packages/machinome/engine/mesh.py contract 1 result 24.0
machinome-node-build123d 0.8.1 module <tmp>/venv/lib/python3.12/site-packages/machinome/node/build123d.py volume 23.999999999999996
machinome-node-cadquery 0.8.1 module <tmp>/venv/lib/python3.12/site-packages/machinome/node/cadquery.py volume 999.9999999999998
machinome-node-molejo 0.8.1 module <tmp>/venv/lib/python3.12/site-packages/machinome/node/molejo.py volume 477.8904448221108
machinome-node-step 0.8.1 module <tmp>/venv/lib/python3.12/site-packages/machinome/node/step.py volume 120.0
Every distribution built, checked, installed and smoked; nothing uploaded.
```

`twine check --strict`: 14 `PASSED`. Every member's `LICENSE` (793 bytes),
`LICENSES/CERN-OHL-S-2.0.txt` (13419) and `LICENSES/GPL-2.0-or-later.txt`
(17984), and the core's `AI-USE.md`, `CONTRIBUTING.rst` and `HISTORY.rst`, are
regular files equal to the root's. The three licence files are listed for
each of the seven (21 lines). The molejo volume 477.8904 against the closed
form 477.8895 (0.0002 %). The core's 1030 is the bench's tree with the
suite's ignored leavings under `tests/`, which `MANIFEST.in` sweeps in; the
clean copy's counts are 10.4's. `git status --short --ignored` before and
after: the same ignored entries; the only differences are the record files
edited during the run (`docs/adrs/README.md`, `docs/architecture.md`,
`docs/start/install.rst`, ADR-184), none of which the script reads after
building the core, which it builds first.

## 9. The records

- 9.1 `HISTORY.rst`: Decision 12's `Unreleased` bullet, verbatim, after the
  second cycle's.
- 9.2 `docs/project/changelog.rst`: Decision 12's bullet, verbatim, after
  the engines'.
- 9.3 `docs/start/install.rst`: the third cell of the `cadquery`,
  `build123d`, `step` and `molejo` rows begins "the package
  ``machinome-node-<x>``, with" before what it installed, each cell
  rewrapped at the table's width; the example refusal is Decision 12's;
  "Packages and licences"' first sentence is Decision 12's, rewrapped. `git
  diff --stat`: 18 insertions, 13 deletions; nothing else on the page.
- 9.4 The root `README.md`: Decision 12's four rows after the engines'.
- 9.5 `CONTRIBUTING.rst`: the pip block's middle lines as Decision 12, in
  place (its one new line is 82 characters, the design's text).
- 9.6 `docs/architecture.md`: the Map row after the mesh engine's, as
  Decision 12; the Node model row's code cell gains "the four node types
  over the B-rep engine in their own distributions, row below" and its ADRs
  184. `grep -n "leaves the core\|at the cut"` finds only the OpenSCAD
  family's row, which is not one of the four; no other sentence changed.
- 9.7 `docs/adrs/NODE/ADR-184-an-absent-node-package-is-refused-by-its-extra-at-its-import.md`,
  Status **Proposed**, Date 2026-10-10, Change `cut-the-brep-nodes`, amending
  167, 181 and 183, related to 179 and 169, with the four options of
  Decision 12; its index entry under NODE after ADR-181 in
  `docs/adrs/README.md`; ADR-183's index line names "the B-rep node packages
  second (`cut-the-brep-nodes`)". "amended by 184" on the index and status
  lines of 167, 181 and 183 is task 11.1's.

### 9.8 (task 9.8)

```
$ ... pytest tests/test_repository_layout.py tests/test_docs_structure.py tests/test_release_records.py tests/test_profile_documentation.py
60 passed, 990 subtests passed in 4.05s
```

## 10. Validation

### 10.1 The whole suite on the bench venv (task 10.1)

One process, from the framework's directory, in the background, its output
in `<scratch>/10.1-suite.txt`:

```
$ env -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python -m pytest -q -rs -p no:cacheprovider
4791 passed, 20 skipped, 55 warnings, 6914 subtests passed in 675.26s (0:11:15)
```

No failure. 4791 is the base's 4786 plus the five tests this change adds:
the layout gate's `test_the_core_node_package_holds_no_extension_module` and
`test_every_sibling_is_in_the_table`, `AbsentPackageTest`'s
`test_every_door_refuses_the_absent_package_by_its_extra` and
`test_the_other_node_packages_still_import`, and `ArtworkSeamTest`'s
`test_a_stale_marking_without_the_reducer_package_is_refused`. Renamed, not
counted: the layout gate's four `test_each_engine_*` /
`test_each_provider_resolves_from_its_package` to their `extension` and
`portion` names; `test_kernel_extras.py`'s
`test_every_kernel_extra_includes_the_brep_extra` replaced by
`test_every_node_package_requires_the_brep_engine` and
`test_each_engine_requires_the_core_and_its_kernel` renamed
`test_each_extension_package_requires_the_core_and_its_kernel`;
`test_core_kernel_free.py`'s `test_the_engine_packages_import_only_their_kernels`
to `test_the_extension_packages_import_only_their_kernels`;
`test_docs_structure.py`'s page test to `..._extension_distributions`.
Removed: none. Subtests 6914, the base's 6831 plus 83. The 20 skips, the
base's:

```
14 tests/test_browser_renderer.py: machinome-viewer not installed (pip install "machinome[viewer]")
 1 tests/test_cli_lazy_imports.py: machinome-viewer not installed
 1 tests/test_scad_presentation.py: machinome-viewer not installed (pip install "machinome[viewer]")
 1 tests/test_connectivity.py: the repairing split needs networkx, which machinome does not install
 1 tests/test_jscad_integration.py: jscad CLI is not installed
 2 tests/test_step_assembly.py: Internal-Cycloidal-Actuator vendor STEP not present
```

### 10.2 The lint on the final tree (task 10.2)

7.3's command: 759 lines, 2 E402 (`tests/test_couplings.py`), equal to 1.3's
list line for line once the `../machinome-node-<x>/` prefix is stripped
(`<scratch>/10.2-lint.txt`).

### 10.3 The manual (task 10.3)

```
$ env -C <bench>/packages/machinome <scratch>/docs-venv/bin/python -m sphinx -b html -W --keep-going docs <scratch>/html-final
build succeeded.
exit 0
```

54 HTML pages.

### 10.4 `scripts/check-dist` on the final tree and on a clean copy (task 10.4)

On the bench (`<scratch>/10.4-bench.txt`), exit 0: the seven members built,
14 archives `PASSED`, every linked file a regular file equal to the root's
(`CONTRIBUTING.rst` 10858 bytes and `HISTORY.rst` 93206, this change's
edits), the install line of 8.3, the seven smokes and `machinome --help`
exit 0, "Every distribution built, checked, installed and smoked; nothing
uploaded."; the node lines as 8.3's (volumes 23.999999999999996,
999.9999999999998, 477.8904448221108, 120.0).

```
   machinome-0.8.1.tar.gz: 1071 entries
   machinome-0.8.1-py3-none-any.whl: 122 entries
   (each engine and each node package: 18 and 8)
```

`git status --short --ignored` before and after: identical. The same script
on a clean copy of the tracked tree (`git ls-files -z | tar --null -T - -cf -`
unpacked in `<scratch>/clean/`, links kept as links;
`<scratch>/10.4-clean.txt`), exit 0, the same lines but:

```
   machinome-0.8.1.tar.gz: 1015 entries
```

1015 and 122, design.md probe 4's counts for the core (the second cycle's
clean 1019 and 126 less the four modules); 18 and 8 for each of the six
siblings. The bench's 1071 is the clean 1015 plus the suite's ignored
leavings under `tests/` that `MANIFEST.in` sweeps in (8.3's 1030 was taken
before the whole suite ran).

### 10.5 The universe sweep (task 10.5)

Decision 14's command, in the background (`<scratch>/10.5-sweep.txt`, JSON
`<scratch>/load-projects.json`):

```
$ /home/asa/devel/machinome/.venv/bin/python /home/asa/devel/machinome/scripts/load-projects \
  --bench <bench>/packages/machinome --python <bench>/.venv/bin/python \
  --moved /home/asa/devel/machinome/scripts/load-projects.d/*.toml \
  --timeout 300 --json <scratch>/load-projects.json
63 repositories, 130 rows: 121 ok, 0 expected, 3 unexpected, 0 timeout, 6 no-model; 2 skipped
Skipped: .Trash-1000 (skip rule), sandbox (skip rule)
exit 1
```

exit 1 for the three unexpected rows, the base's. Row by row against the
second cycle's JSON (`C2-apply/load-projects-2.json`): the same 130 rows by
project and model, 0 rows whose outcome, stage or test cases differ, and
the three unexpected rows' explanations identical to the base's:

- `3D-Printers/fender-bender`: `ModuleNotFoundError: No module named
  'fb_library'` at `src/bender_config.py:12`;
- `3DPrintedClocks` `wall_clock_41`: `machinome.parameters.ParameterError:
  Movement.wound_weight_seat: frame argument at -- the callable raised
  ValueError: Workplane object must have at least one solid on the stack to
  union!`;
- `Robotic-Arms/Dum-E`: `ModuleNotFoundError: No module named
  'machinome_freecad'` at `simulation/dume.py:7`.

The catalogue's imports of the four modules resolve as portions on the bench
venv: no row differs.

### 10.6 Git (task 10.6)

```
$ git -C <bench> status --short | cut -c1-2 | sort | uniq -c
     25  M
      1 ??
     17 A
      4 R
$ git -C <bench> ls-files | wc -l
3405
$ git -C <bench> ls-files -ci --exclude-standard | wc -l
34
```

- `R`: the four modules, renamed with no change (`R100`).
- `A`: the four files of each node directory (`LICENSE` and `LICENSES` with
  mode 120000, eight links; `README.md`; `pyproject.toml`), 16, and ADR-184.
- ` M`: `.bumpversion.cfg`, `CONTRIBUTING.rst`, `HISTORY.rst`, `README.md`,
  `pyproject.toml`, `uv.lock`, `scripts/check-dist`, and under
  `packages/machinome/`: `pyproject.toml`, `setup.cfg`,
  `machinome/node/__init__.py`, `machinome/node/supported.py`,
  `docs/conf.py`, `docs/adrs/README.md`, `docs/architecture.md`,
  `docs/project/changelog.rst`, `docs/start/install.rst`, this change's
  `tasks.md`, and eight tests (`test_core_kernel_free.py`,
  `test_docs_structure.py`, `test_kernel_extras.py`,
  `test_leaf_contract_reach.py`, `test_markings.py`,
  `test_node_root_exports_nothing.py`, `test_repository_layout.py`,
  `test_supported_node_types.py`).
- `??`: this `evidence.md`.

3405 is the planning commit's 3388 files plus the 17 added.

### 10.7 OpenSpec (task 10.7)

```
$ env -C <bench>/packages/machinome openspec validate cut-the-brep-nodes --strict
Change 'cut-the-brep-nodes' is valid
```

## Departures from the design, to the checkpoint (task 10.8)

1. **`test_each_engine_requires_the_core_and_its_kernel` renamed**
   `test_each_extension_package_requires_the_core_and_its_kernel` (2.2), and
   `engine_manifest` renamed `package_manifest`, since the test now reads the
   node manifests too; Decision 10 renames `ENGINE_REQUIREMENTS` and names
   "the requirements test" without a new name.
2. **`test_no_node_extra_includes_the_mesh_engine` reads only the node
   manifests present** (2.2), so it is green at the base as task 2.2's list
   of reds implies, while `test_every_node_package_requires_the_brep_engine`
   fails on a missing manifest.
3. **`test_kernel_modules_are_named_only_at_the_seams` red twice at 2.3**:
   besides the seam subtest the task names, the path subtest
   `machinome/node/step.py` (the same fact from the core's side).
4. **3.3 ran in two calls**: `test_leaf_contract_reach.py` cannot be
   collected on the moved tree before the sync (`find_spec` returns `None`,
   `AttributeError: 'NoneType' object has no attribute 'origin'`), which
   stops the run; the other three ran in a second call.
   `test_the_members_are_the_package_directories` was red there too, which
   the task does not list.
5. **5.3's resync installed two packages**, not one, because the markings
   door was also shown by hand with `machinome-node-build123d` uninstalled;
   the "before" column of 5.3 is the same interpreter with the finder
   removed from `sys.meta_path`, not the pre-Decision-5 code.
6. **6.1's five reds carry the node root's refusal**, not probe 8's `No
   module named ...`, because Decision 5 (group 5) is applied before group 6.
7. **A docstring line of 106 characters** introduced at 2.4 in
   `tests/test_leaf_contract_reach.py` was rewrapped at 7.3 (the first lint
   run counted 760).
8. **The node root's docstring paragraph "The refusals."** was rewrapped
   after the sentence Decision 5 adds; no word of it changed.
9. **`docs/architecture.md`**: only the Map rows changed; the prose on the
   doors (around "the module's own import, however spelled") does not yet
   say what the doors do when a node package is absent. Task 11.1 checks the
   page against ADR-184.

## 11. The review, and the records closing

The orchestrator's review of the checkpoint (10 October 2026) accepted the
work to task 10.8, the two test renames and every departure above
included, and asked for one addition before group 11: in
`docs/architecture.md`, the three-doors paragraph, after the sentence saying
the root's refusal of a class name imports no node type, the sentence "A
node type of the table whose distribution is not installed is refused at
those same doors by the node root's last finder, with the table's refusal
naming its extra (ADR-184)." Added on that line; no other prose changed.

### 11.1 ADR-184 accepted (task 11.1)

`docs/adrs/NODE/ADR-184-an-absent-node-package-is-refused-by-its-extra-at-its-import.md`:
Status **Accepted**, its Change link repointed to
`../../../openspec/changes/archive/2026-10-10-cut-the-brep-nodes/` (resolves);
its index line in `docs/adrs/README.md` **Accepted**. As its Amends list
says, the status lines gain, each with a link to ADR-184:

- ADR-167: "the refusal at the import of an absent node package, the node
  root's, amended 2026-10-10 by ADR-184";
- ADR-181: "the three doors keeping their refusal when the node package is
  absent, amended 2026-10-10 by ADR-184";
- ADR-183: "a node package refused by its extra's name at its import,
  amended 2026-10-10 by ADR-184";

and their index lines "amended by 184". `docs/architecture.md` checked
against it: the Map rows of 9.6 and the sentence above.

### 11.2 Archive and spec sync (task 11.2)

```
$ env -C <bench>/packages/machinome openspec archive cut-the-brep-nodes -y
kernel-extras MODIFIED failed for header "### Requirement: The CAD kernels are extras, not required dependencies" - current spec contains scenario(s) not present in the modified block: "The installation page names the engine distributions". Refresh the change spec before archiving to avoid dropping scenarios.
Aborted. No files were changed.
exit 1
```

A departure in mechanism. The `kernel-extras` delta renames two scenarios
by design: "The installation page names the engine distributions" becomes
"... the extension distributions", and "Scanning the engine distributions
finds only their kernels" becomes "Scanning the extension distributions
...". The CLI reads a renamed scenario as a dropped one. A scan of all six
deltas against the baseline found no other scenario absent from a modified
block. As `backend-switch` did (its evidence), the deltas were applied by a
script rather than by editing the ratified delta: each MODIFIED block
replacing the baseline block of its header whole, the ADDED block
appended; then checked, per capability, that every block from the delta is
the delta's text, every other block and the preamble unchanged, and the
order kept (`cli` 1 block, 19 unchanged; `framework-contributor-guidance` 1,
2; `framework-identity` 1, 4; `kernel-extras` 2 replaced and 1 added, 2
unchanged; `markings` 1, 6; `node-model` 1, 14). The baselines before the
sync are in `<scratch>/11.2-specs-before/`.

```
$ openspec validate <capability> --type spec --strict      (each of the six)
Specification '<capability>' is valid
$ env -C <bench>/packages/machinome openspec archive cut-the-brep-nodes -y --skip-specs
Task status: 51/53 tasks
Skipping spec updates (--skip-specs flag provided).
Change 'cut-the-brep-nodes' archived as '2026-10-10-cut-the-brep-nodes'.
$ env -C <bench>/packages/machinome openspec validate --specs --strict
Totals: 45 passed, 0 failed (45 items)
```

The archive is `packages/machinome/openspec/changes/archive/2026-10-10-cut-the-brep-nodes/`;
`openspec/changes/` holds only `archive/`.

### 11.3 The plan note (task 11.3)

`workflow/ongoing/monorepo-0.9.md` at the repository root: cycle 3 marked
**Done** with its branch, the planning commit bdadf767 on 84757c38, ADR-184,
the suite count of 10.1, the manual, the check-dist result with the clean
copy's counts, the lock's 183 packages and the sweep's counts with its three
named rows, as cycles 1 and 2 are recorded.

### After the archive

```
$ ... pytest tests/test_repository_layout.py tests/test_supported_node_types.py tests/test_kernel_extras.py tests/test_release_records.py tests/test_docs_structure.py
87 passed, 1083 subtests passed in 5.66s
```

### 11.4 (task 11.4)

This file complete. The implementation commit is the orchestrator's; the
planning commit is not amended; nothing is pushed.
