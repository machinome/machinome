# Evidence: `join-freecad`

The first cycle of the joins campaign of Machinome 0.9
(`workflow/ongoing/joins-0.9.md` at the repository root, cycle 1). Worktree
`machinome/WTs/v0.9-joins-join-freecad`, branch `v0.9-joins-join-freecad`,
cut from the line `v0.9-joins` at cf631645. Planning commit dea7d7f4,
ratified by the orchestrator on 11 October 2026; join merge commit dba7dae5,
made by the orchestrator. Applied on 11 October 2026.

Tools: uv 0.11.8, CPython 3.12.3 (the bench venv), the OpenSpec CLI 1.6.0,
OpenSCAD 2021.01 at `/usr/bin/openscad`, the official FreeCAD 1.1.4 AppImage
extracted at `projects/Robotic-Arms/Dum-E/.tools/freecad-1.1.4/squashfs-root`
(named `<freecad>`, used read-only). Every command ran with `env -C <dir>` and
absolute paths; `<bench>` is
`/home/asa/devel/machinome/machinome/WTs/v0.9-joins-join-freecad` and
`<scratch>` is
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C1-apply/`
(it also holds files of 10 October 2026 from an earlier campaign; this
cycle's are those of 11 October). Every test ran from
`<bench>/packages/machinome` on the bench venv
(`<bench>/.venv/bin/python -m pytest -q -p no:cacheprovider ...`), one pytest
process at a time. A run "with the runtime" sets
`MACHINOME_FREECAD_ROOT=<freecad>`; a run "without" removes it with
`env -u`. Logs are in `<scratch>`, never in the bench.

## 1. Evidence baseline

### 1.1 The base (task 1.1)

```
$ git -C <bench> log --oneline -3
dba7dae5 Join machinome-freecad: its whole history at its final paths
dea7d7f4 Propose join-freecad: machinome-freecad joins as the node package machinome-node-freecad
cf631645 workflow: the joins campaign plan for 0.9, the products entering the monorepo
$ git -C <bench> status --short | wc -l
0
$ git -C <bench> ls-files | wc -l
3495
$ git -C <bench> ls-files -ci --exclude-standard | wc -l
34
```

`git status --short --ignored` showed `!! .env`, `!! .venv/` and the eleven
packages' build leavings (`__pycache__/`, `*.egg-info/`).

### 1.2 The bench venv and the base's counts (task 1.2)

The orchestrator synced the venv from the lock before the join (187 packages
resolved; `uv pip list` lists 178 installed). Eleven `__editable__` files,
one line each, each holding its package directory:

```
__editable__.machinome-0.8.1.pth: <bench>/packages/machinome
__editable__.machinome_engine_brep-0.8.1.pth: <bench>/packages/machinome-engine-brep
__editable__.machinome_engine_mesh-0.8.1.pth: <bench>/packages/machinome-engine-mesh
__editable__.machinome_node_build123d-0.8.1.pth: <bench>/packages/machinome-node-build123d
__editable__.machinome_node_cadquery-0.8.1.pth: <bench>/packages/machinome-node-cadquery
__editable__.machinome_node_jscad-0.8.1.pth: <bench>/packages/machinome-node-jscad
__editable__.machinome_node_molejo-0.8.1.pth: <bench>/packages/machinome-node-molejo
__editable__.machinome_node_openscad-0.8.1.pth: <bench>/packages/machinome-node-openscad
__editable__.machinome_node_solid2-0.8.1.pth: <bench>/packages/machinome-node-solid2
__editable__.machinome_node_step-0.8.1.pth: <bench>/packages/machinome-node-step
__editable__.machinome_node_stl-0.8.1.pth: <bench>/packages/machinome-node-stl
```

The base's counts, measured by `cut-the-mesh-nodes` on the same tree and
recipe, recorded and not rerun: suite 4796 passed, 20 skipped, 7029
subtests; lint 759 lines (`flake8 --max-line-length=89 machinome tests` and
the ten `../machinome-*/machinome` paths, from the framework's directory);
sweep 63 repositories, 130 rows, 121 ok, 0 expected, 3 unexpected, 0
timeout, 6 no-model; the clean copy's framework sdist 1006 entries and wheel
114.

### 1.3 The probes this cycle relies on (task 1.3, by reference)

design.md, Probes: probe 1 (the product as it is on the line's head: 4
collection errors); probe 2 (the smallest port: 80 passed, 1 failed, 1
skipped; the seam variant `test_public.py` 31 passed); probe 3 (the port
without the runtime: 55 failed, 6 errors, 20 passed, 1 skipped); probe 4 (the
rehearsed import: 51 files, `lean-core-validation` at 7e5b228a); probe 6 (the
reds of the join); probe 7 (Dum-E on the package in scratch); probe 8 (82
passed on regenerated fixtures).

## 2. The join

### 2.1 and 2.2 The import and the merge (the orchestrator's, as measured)

- A fresh clone of `file:///home/asa/devel/machinome/machinome-freecad`
  rewritten with the command of design.md Decision 2, whose text is
  `scratchpad/C1-propose/filter-repo-command.sh`; `lean-core-validation` at
  7e5b228a, the rehearsal's hash; `git ls-tree -r --name-only` listed the 51
  paths of the rehearsal exactly (diff empty); no commit of any branch
  touches a path outside `packages/` (0).
- The merge commit dba7dae5, `git merge --allow-unrelated-histories --no-ff`
  of that branch onto dea7d7f4, no conflict; `git status --porcelain` empty
  afterwards; tracked files 3444 before, 3495 after.
- `git log --follow --format='%h %ad %s' --date=short --
  packages/machinome-node-freecad/machinome/node/freecad/adapter.py` lists
  7e5b228a (2026-10-03, "validate leaf-contract: migrate the exact leaf onto
  the declared contract") and fc69a67a (2026-10-01, "feat(freecad): import
  validated native assembly mechanics"), the commit that wrote it.
- `git log` on
  `packages/machinome/workflow/archive/native-freecad-assembly-2026-10-01/dume-native-freecad.md`
  reaches d08fe445 (2026-10-01, the product's first commit) without
  `--follow`.
- `git blame -L20,20` on the worker attributes `def constraint_residual(kind,
  frames, context):` to fc69a67a, Luis Fagundes, 2026-10-01.

The applier re-read the four facts on the bench and found them as stated;
`git diff --name-only dea7d7f4 dba7dae5 | wc -l` is 51.

### 2.3 The gates red on the joined tree (task 2.3)

```
$ ... pytest tests/test_repository_layout.py tests/test_release_records.py \
    tests/test_core_kernel_free.py tests/test_core_names_no_split_words.py \
    tests/test_node_root_exports_nothing.py
10 failed, 83 passed, 477 subtests passed in 8.55s
```

(`<scratch>/2.3-red.txt`.) Exactly the reds of design.md probe 6, each with
its reason:

- `test_every_member_is_a_workspace_source`: the root manifest's sources
  lack `machinome-node-freecad`.
- `test_the_readme_links_every_package_and_states_the_licence`
  (`machinome-node-freecad`): `'packages/machinome-node-freecad/' not found`
  among the root README's links.
- `test_every_sibling_is_in_the_table`: `packages/machinome-node-freecad is
  not in EXTENSIONS`.
- `test_the_guide_installs_every_member_without_uv`: `CONTRIBUTING.rst does
  not name -e packages/machinome-node-freecad`.
- `test_every_member_is_numbered_with_the_core`: `'0.1.0' != '0.8.1'`.
- `test_every_pin_between_members_is_compatible` (member
  `machinome-freecad`, requirement `machinome`): `'' != '~=0.8.1'`.
- `test_the_version_is_bumped_from_the_root`:
  `'packages/machinome-node-freecad/pyproject.toml' not found` among
  `.bumpversion.cfg`'s files.
- `test_the_extension_packages_import_only_their_kernels`: the census holds
  `'machinome-node-freecad/machinome/node/freecad/adapter.py': ['OCP']`,
  which the expectation does not.
- `test_no_module_names_the_split_but_by_its_two_words`: `adapter.py` 4
  occurrences (141 `exact_leaf`, 141 and 142 `ExactLeafNode`, 177 the
  `occt` of `machinome.occt.engine`) and `worker.py` 1 (259 `'occt'`).
- `test_no_file_of_the_three_zones_spells_a_former_root_name`: `adapter.py`
  line 17, `from machinome.node import AssemblyNode`.

Nothing else was red.

## 3. Red first, on the joined tree

Nothing of the package changed in this group.

### 3.1 `tests/test_repository_layout.py` (task 3.1)

`EXTENSIONS['machinome-node-freecad'] = ('machinome.node.freecad',
'freecad')`; `PACKAGE_PORTIONS['machinome-node-freecad'] = ('__init__',
'adapter', 'runtime', 'worker')`; the docstring names the package and the
change.

```
$ ... pytest tests/test_repository_layout.py
7 failed, 29 passed, 176 subtests passed in 2.82s
```

(`<scratch>/3.1-red.txt`.) `test_every_sibling_is_in_the_table` turned
green with the row; red:

- `test_each_extension_directory_holds_only_what_distinguishes_it`:
  `['README.md', 'machinome/node/freecad/__init__.py', ...] != ['LICENSE',
  'LICENSES', 'README.md', ...]`, no links.
- `test_each_extension_manifest_is_a_portion_of_the_set`:
  `'machinome-freecad' != 'machinome-node-freecad'`, the product's manifest.
- `test_each_extension_readme_names_its_install_and_the_licence`: `'pip
  install "machinome[freecad]"' not found` in the product's README.
- `test_each_portion_resolves_from_its_package`: `ModuleNotFoundError: No
  module named 'machinome.node.freecad'`, not installed.
- and 2.3's three others of the module (workspace source, root README,
  contributor guide).

### 3.2 `tests/test_kernel_extras.py` (task 3.2)

`EXTRAS['freecad']`, `all` with `freecad`;
`PACKAGE_REQUIREMENTS['machinome-node-freecad']`; `BREP_NODE_PACKAGES`, the
no-mesh extras list and `test_all_names_every_kernel_extra`'s set gain it;
`MODULES['machinome.node.freecad'] = ('freecad', 'machinome.node.freecad
(FreeCADAssemblyNode, FreeCADJoint)', ('OCP',))`; the docstring names the
change.

```
8 failed, 16 passed, 68 subtests passed in 1.84s
```

(`<scratch>/3.2-red.txt`.) Red: `test_all_names_every_kernel_extra` (`Items
in the second set but not the first: 'freecad'`);
`test_each_extra_lists_what_its_module_needs` for `freecad` (`KeyError`) and
`all`; `test_each_extension_package_requires_the_core_and_its_kernel` (the
product's `machinome`, unpinned, in place of the four requirements);
`test_every_node_package_requires_the_brep_engine` (`'machinome-engine-brep~=0.8.1'
not found in ['machinome']`); `test_no_node_extra_includes_the_mesh_engine`
for `freecad` (`KeyError`); `test_the_lock_installs_every_kernel`
(`machinome-node-freecad` not in `uv.lock`);
`test_each_kernel_module_refuses_each_absent_kernel` for
`machinome.node.freecad`/`OCP` (`'ModuleNotFoundError' !=
'ExtraUnavailable'`: `No module named 'machinome.node.freecad'`).

### 3.3 `tests/test_core_kernel_free.py` (task 3.3)

`KERNEL_MODULES` and `EXTENSION_MODULES` gain `machinome.node.freecad`;
`EXTRA_OF['machinome-node-freecad/machinome/node/freecad/__init__.py'] =
'freecad'`; the census expects `adapter.py`'s `['OCP']`; the docstring names
the package.

```
1 failed, 11 passed, 32 subtests passed in 4.66s
```

The census green; `test_each_kernel_module_checks_its_kernel_first` red for
the package's `__init__`: `calls no require_extra`.

### 3.4 `tests/test_supported_node_types.py` and `tests/test_node_root_exports_nothing.py` (task 3.4)

`NODE_TYPES['freecad'] = ('FreeCADAssemblyNode', 'FreeCADJoint')`, last;
`ABSENCES['freecad'] = doors('freecad')`; the table test renamed
`test_it_names_the_nine_node_types_and_their_classes`; the new class
`TheFreeCADTestsSkipWithoutARuntimeTest`; in
`test_node_root_exports_nothing.py`,
`test_the_table_lists_the_nine_classes_written_here` reads the table's former
root names apart from its new ones.

```
9 failed, 31 passed, 156 subtests passed in 9.22s
```

(`<scratch>/3.4-red.txt`.) Red:

- `test_it_names_the_nine_node_types_and_their_classes`: the table's keys end
  at `'stl'`, no `'freecad'`.
- `test_the_root_refuses_each_class_naming_its_module`:
  `ModuleNotFoundError: No module named 'machinome.node.freecad'`.
- `AbsentPackageTest.test_every_door_refuses_the_absent_package_by_its_extra`,
  the four `freecad` doors: `ModuleNotFoundError` with no extra (`import`,
  `from-module`), `ImportError` from `machinome.node` (`from-root`), and
  `['passed', False]` (`hasattr`), each in place of the `ExtraUnavailable`
  naming `machinome[freecad]`.
- `test_the_public_module_skips_naming_the_variable`: `ImportError while
  importing test module ... test_freecad_public.py` (the product's
  `machinome_freecad`), exit 2.
- `test_the_table_lists_the_nine_classes_written_here`: `[] !=
  ['FreeCADAssemblyNode', 'FreeCADJoint']`.
- `test_no_file_of_the_three_zones_spells_a_former_root_name`: 2.3's.

### 3.5 `tests/test_core_names_no_split_words.py` (task 3.5)

`ZONES` gains `machinome/node/freecad/worker.py`; the W4 sentence names it.

```
1 failed, 10 passed, 57 subtests passed in 0.83s
```

Red on `adapter.py` alone (its four occurrences of 2.3); the worker green.

### 3.6 `tests/test_docs_structure.py` (task 3.6)

`KernelExtrasTest.EXTRAS` gains `freecad`, the distributions' test
`machinome-node-freecad`, `STALE` the former module (spelled in two pieces);
the new `NavigationTest.test_the_freecad_guide_is_a_how_to`.

```
4 failed, 17 passed, 834 subtests passed in 0.37s
```

(`<scratch>/3.6-red.txt`.) Red: `test_the_freecad_guide_is_a_how_to`
(`'howto/freecad-assemblies' not found` in the How-to toctree);
`test_the_installation_page_names_every_kernel_extra` for `freecad`;
`test_the_installation_page_names_the_extension_distributions` for
`machinome-node-freecad`; and one red the task did not list,
`test_no_reader_page_carries_the_kernels_or_the_old_addresses` for
`howto/freecad-assemblies.rst` and the former module: the imported page's
example imports from it.

### 3.7 Every red of group 3 (task 3.7)

Recorded in 3.1 to 3.6.

## 4. The package

### 4.1 The links (task 4.1)

```
$ git -C <bench> ls-files -s packages/machinome-node-freecad | grep ^120000
120000 30cff7403da04711c46979a06f6bf8eb10ee088a 0	packages/machinome-node-freecad/LICENSE
120000 06ad40db40b426ca6c609aa4663782c2b8d02e92 0	packages/machinome-node-freecad/LICENSES
```

`readlink`: `../../LICENSE`, `../../LICENSES`.

### 4.2 The manifest and the README (task 4.2)

Decision 3's two files, verbatim, in place of the product's.

### 4.3 The `__init__` and the headers (task 4.3)

Decision 4's `__init__.py`, verbatim but one sentence of its docstring (see
Departures, 1): "read through the OCCT binding" reads "read through `OCP`".
`adapter.py`, `runtime.py` and `worker.py` open with the framework's three
header lines; the worker keeps its Ondsel line, and its fourth reads
`# Original Python adaptation added 2026-10-01; see the framework's
CREDITS.md.`

### 4.4 The adapter (task 4.4)

`git diff` of `adapter.py` shows the header and Decision 5's four edits and
nothing else: `from machinome.node.assembly import AssemblyNode`;
`BrepLeafNode` from `machinome.node.brep_leaf` with `leaf_contract = 3`; in
`_Solid.render`, `from machinome.engine import require_brep_engine` and
`engine = require_brep_engine(f'FreeCAD occurrence {self.name}', 'its native
solid is read')` before `if not engine.solid_count(shape) or ...`.
`runtime.py` changes its header only.

## 5. The core and the workspace

### 5.1 The row (task 5.1)

`machinome/node/supported.py`: one line,
`'freecad': NodeType(('FreeCADAssemblyNode', 'FreeCADJoint')),` after `stl`.

### 5.2 The core's manifest (task 5.2)

The `freecad` extra with its comment, `all` with `freecad`, and the
`dependencies` comment's list. `git diff` shows two hunks, not three: the
extra and `all` are adjacent lines and share one; the comment, rewrapped to
its width, is the other.

### 5.3 The workspace (task 5.3)

The root `pyproject.toml`'s source `machinome-node-freecad = { workspace =
true }` between `machinome-node-cadquery` and `machinome-node-jscad`.

```
$ env -C <bench> /home/asa/.local/bin/uv lock
Resolved 188 packages in 734ms
Added machinome-node-freecad v0.8.1
$ env -C <bench> /home/asa/.local/bin/uv sync --python 3.12
Resolved 188 packages in 10ms
...
Uninstalled 1 package in 3ms
Installed 2 packages in 13ms
 ~ machinome==0.8.1 (from file://<bench>/packages/machinome)
 + machinome-node-freecad==0.8.1 (from file://<bench>/packages/machinome-node-freecad)
```

`uv.lock` gains the member, its package entry, the `freecad` extra and its
place in `all` and `dev` (29 lines added, 2 changed); no third-party package.
Twelve `__editable__` files, the eleven of 1.2 and
`__editable__.machinome_node_freecad-0.8.1.pth:
<bench>/packages/machinome-node-freecad`. From `/tmp`:

```
$ <bench>/.venv/bin/python -c "import machinome.node.freecad as m; print(m.__file__); print(m.FreeCADAssemblyNode.__module__)"
<bench>/packages/machinome-node-freecad/machinome/node/freecad/__init__.py
machinome.node.freecad.adapter
```

`git status --short --ignored packages/machinome-node-freecad` shows the
package's edits and, ignored, `__pycache__/` and
`machinome_node_freecad.egg-info/`, no untracked leaving.

### 5.4 Group 3's modules after the package (task 5.4)

```
$ ... pytest (the eight gate modules and test_release_records.py)
9 failed, 134 passed, 1478 subtests passed in 16.12s
```

(`<scratch>/5.4.txt`.) Red as expected: the layout gate's README and guide
tests (group 9), `test_the_version_is_bumped_from_the_root` (group 8), the
four of `test_docs_structure.py` (group 7), the skip test (group 6); and,
unexpected, `test_no_module_names_the_split_but_by_its_two_words` on the new
`__init__.py` line 5, whose verbatim docstring says "OCCT" outside the zones
(Departures, 1). After the docstring's correction: 11 passed.

### 5.5 The refusal of the absent package (task 5.5)

```
$ uv pip uninstall --python <bench>/.venv/bin/python machinome-node-freecad
 - machinome-node-freecad==0.8.1 (from file://<bench>/packages/machinome-node-freecad)
$ env -C /tmp <bench>/.venv/bin/python -c "from machinome.node.freecad import FreeCADAssemblyNode"
machinome.extras.ExtraUnavailable: the freecad node type (FreeCADAssemblyNode, FreeCADJoint) needs machinome.node.freecad, which is not installed; install it with 'pip install "machinome[freecad]"'
$ env -C <bench> uv sync --python 3.12
Resolved 188 packages in 11ms
Installed 1 package in 13ms
 + machinome-node-freecad==0.8.1 (from file://<bench>/packages/machinome-node-freecad)
```

(`<scratch>/5.5.txt`.)

## 6. The tests and the fixtures

### 6.1 The guard (task 6.1)

`tests/freecad_support.py`, Decision 10's text verbatim.

### 6.2 The four modules and the three helpers (task 6.2)

Each module: the header (`test_freecad_public.py` gains it, and its
docstring), the guard after the standard-library imports
(`from tests.freecad_support import skip_without_runtime` then
`skip_without_runtime()`), the imports from `machinome.node.freecad`, `from
tests.test_freecad_public import ...` in three modules, the seven `import
machinome.node.freecad.adapter as adapter` and the relocated project's source
text in `test_freecad_freshness.py`, `FIXTURE` under `fixtures/freecad/`,
`freecad_native_reference.py`, `from tests.freecad_origin_model import
DeclaringModule`, the two relative sources `'fixtures/freecad/Assembly.FCStd'`,
and `leaf.brep`. Helpers: headers; `freecad_origin_model.py` its import and
source; `freecad_generate_fixtures.py` its `out` and its three pairs of
`License` and `LicenseURL` assignments. `grep` finds no `machinome_freecad`
and no former licence string in the seven files.

### 6.3 The fixtures (task 6.3)

The fixtures' README: its SPDX line, `../../freecad_generate_fixtures.py`,
and a closing "Regenerate" section with the recipe. The 27 documents copied to
`<scratch>/fixtures-before/` first, then:

```
$ env -C <bench>/packages/machinome MACHINOME_FREECAD_ROOT=<freecad> PYTHONPATH="<freecad>/usr/lib" "<freecad>/AppRun" python tests/freecad_generate_fixtures.py
Generated native synthetic fixtures
exit 0
```

27 `.FCBak` backups appeared (26 in `tests/fixtures/freecad/`, one in
`assembly-dir/`), all deleted; 0 left. Each document's `Document.xml` read
with `<scratch>/count_licence.py`, before and after (`<scratch>/6.3-before.txt`,
`6.3-after.txt`), identical for all 27 (`Antiparallel`, `Assembly`,
`Disabled`, `Disconnected`, `DistinctProducts`, `FixedOppositeX`,
`FixedOppositeY`, `FixedOppositeZ`, `FixedQuarterTurn`, `Loop`, `Maximum120`,
`MaximumOnly`, `MinimumOnly`, `MissingEdge`, `Offsets`, `OtherParts`, `Parts`,
`PartsTall`, `Reversed`, `ReversedBounds`, `RevoluteDisplaced`,
`RevoluteTilted`, `SecondGround`, `StaleConnectors`, `Suppressed`,
`Unsupported`, `assembly-dir/Assembly`):

| string | before | after |
|---|---|---|
| the former licence identifier | 1 | 0 |
| the former licence URL | 1 | 0 |
| the set's expression | 0 | 1 |
| the repository's `LICENSE` URL | 0 | 1 |

The former licence string, identifier and URL together, 2 before and 0
after in every document. No other member of any document names it before or
after, and no regenerated document holds an absolute path; `CreationDate`
and the object UUIDs change with the regeneration.

### 6.4 Without the runtime (task 6.4)

```
$ env -u MACHINOME_FREECAD_ROOT -C <bench>/packages/machinome <bench>/.venv/bin/python -m pytest -q -rs -p no:cacheprovider tests/test_freecad_public.py tests/test_freecad_constraints.py tests/test_freecad_diagnostics.py tests/test_freecad_freshness.py
SKIPPED [4] tests/freecad_support.py:21: MACHINOME_FREECAD_ROOT is not set: the FreeCAD node package's tests need an extracted FreeCAD 1.1.4 runtime
4 skipped in 0.32s
```

The skip test first ran red on the guarded module: pytest exits 5 when a
module skipped whole collects no test, which the test's first draft read as
a failure (Departures, 3). With the status admitted:
`tests/test_supported_node_types.py` 14 passed, 65 subtests passed in 6.08s.

### 6.5 With the runtime (task 6.5)

```
$ env -C <bench>/packages/machinome MACHINOME_FREECAD_ROOT=<freecad> MACHINOME_FREECAD_DUME_SOURCE=/home/asa/devel/machinome/projects/Robotic-Arms/Dum-E/upstream/MA_Dum_E_v2_Assembly.FCStd <bench>/.venv/bin/python -m pytest -q -rs -p no:cacheprovider --durations=0 (the four modules)
82 passed in 145.66s (0:02:25)
$ env -u MACHINOME_FREECAD_DUME_SOURCE ... MACHINOME_FREECAD_ROOT=<freecad> ... (the four modules)
SKIPPED [1] tests/test_freecad_constraints.py:105: Set MACHINOME_FREECAD_DUME_SOURCE for external untouched source refusal
81 passed, 1 skipped in 145.47s (0:02:25)
```

(`<scratch>/6.5-with-dume.txt`, `6.5-without-dume.txt`.) The Dum-E document
was read only; `git -C <Dum-E> status --short` was empty before.

## 7. The manual

### 7.1 Red first (task 7.1)

A fresh venv, `<scratch>/jf-docs-venv`, installing
`packages/machinome/docs/requirements.txt` alone (39 packages,
`machinome-viewer==0.8.0` among them):

```
$ env -C <bench>/packages/machinome <scratch>/jf-docs-venv/bin/python -m sphinx -b html -W --keep-going docs <scratch>/jf-html-red
build finished with problems, 12 warnings (with warnings treated as errors).
exit 1
```

(`<scratch>/7.1-sphinx-red.txt`.) All twelve on the imported page: nine
docutils warnings and errors on its Markdown (unclosed inline literals at
lines 7, 19, 145 and 160, unexpected indentation at 153 and 157, a block
quote at 154), and `document isn't included in any toctree`.

### 7.2 The guide (task 7.2)

`docs/howto/freecad-assemblies.rst`, converted in place, titled "Simulate a
native FreeCAD assembly", with Decision 12's sections: the opening, "Set up
FreeCAD", "Declare the assembly", "Drive a joint", "What is refused", "After
an edit", "Compare poses". `index.rst`'s How-to toctree lists it after
`howto/simulate-existing`.

### 7.3 The installation, backends and reference pages (task 7.3)

As Decision 12 says: the optional FreeCAD requirement, the
`machinome[freecad]` row and the distribution in "Packages and licences" on
`start/install.rst`; the `FreeCADAssemblyNode` row and the nine-node-types
sentence on `howto/backends.rst`; the two classes and the attribute after
`StepNode` on `reference/api.rst`.

### 7.4 The build (task 7.4)

```
$ env -C <bench>/packages/machinome <scratch>/jf-docs-venv/bin/python -m sphinx -b html -W --keep-going docs <scratch>/jf-html
exit 0
```

(`<scratch>/7.4-sphinx.txt`, no warning.) Looked at in the rendered HTML:
`howto/freecad-assemblies.html` with its title and its six section headings;
`index.html` links it; `reference/api.html` holds the anchors
`machinome.node.freecad.FreeCADAssemblyNode`,
`machinome.node.freecad.FreeCADJoint` and
`machinome.node.freecad.FreeCADAssemblyNode.freecad_source`, the class shown
with the adapter's own docstring followed by the entry's text.
`test_docs_structure.py` green (9).

## 8. One version and `scripts/check-dist`

### 8.1 The tables (task 8.1)

`.bumpversion.cfg` gains the package's `version` and `pins` tables after the
`stl` package's. `test_release_records.py` green (9).

### 8.2 The bump on a copy (task 8.2)

`.bumpversion.cfg` and the 15 files it names copied to `<scratch>/jf-bump/`,
made a git repository and committed, then:

```
$ env -C <scratch>/jf-bump <bench>/.venv/bin/bump2version --no-commit --no-tag --new-version 0.9.0 patch
exit 0
$ git -C <scratch>/jf-bump diff --shortstat
 16 files changed, 45 insertions(+), 45 deletions(-)
$ git -C <scratch>/jf-bump diff -U0 | grep '^+[^+]' | sort | uniq -c
      6 +    "machinome-engine-brep~=0.9.0",
      1 +    "machinome-engine-mesh~=0.9.0",
      1 +    "machinome-node-build123d~=0.9.0",
      2 +    "machinome-node-cadquery~=0.9.0",
      1 +    "machinome-node-freecad~=0.9.0",
      1 +    "machinome-node-jscad~=0.9.0",
      1 +    "machinome-node-molejo~=0.9.0",
      2 +    "machinome-node-openscad~=0.9.0",
      1 +    "machinome-node-solid2~=0.9.0",
      1 +    "machinome-node-step~=0.9.0",
      1 +    "machinome-node-stl~=0.9.0",
     11 +    "machinome~=0.9.0",
      1 +__version__ = "0.9.0"
      1 +current_version = 0.9.0
      1 +release = '0.9.0'
     13 +version = "0.9.0"
```

Against `cut-the-mesh-nodes`' 41 lines in 15 files: 4 more lines in one more
file, the new manifest's version and its two pins and the core's
`machinome-node-freecad~=` pin; nothing else. Nothing written in the bench.

### 8.3 Red first (task 8.3)

```
$ env -C <bench> <bench>/.venv/bin/python scripts/check-dist
check-dist failed: machinome-node-freecad has no smoke in scripts/check-dist
Nothing uploaded.
exit 1
```

### 8.4 The row (task 8.4)

Decision 9's row, verbatim, and the template function's docstring sentence,
rewrapped to its width. `git diff scripts/check-dist` changes no line of
another row. `flake8 --max-line-length=89 scripts/check-dist`: 0 lines.

### 8.5 The run (task 8.5)

Without `MACHINOME_FREECAD_ROOT` (`<scratch>/8.5-check-dist-no-runtime.txt`),
exit 0: twelve members built; 24 archives, each `twine check --strict`
PASSED; every sdist's linked files regular and equal to the root's; the set
installed through the core's extras from the built archives;

```
machinome-node-freecad 0.8.1 module /tmp/machinome-check-dist-xrbjz80p/venv/lib/python3.12/site-packages/machinome/node/freecad/__init__.py refused without MACHINOME_FREECAD_ROOT, as documented
Every distribution built, checked, installed and smoked; nothing uploaded.
```

its `License-Expression: GPL-2.0-or-later OR CERN-OHL-S-2.0+` and its
`licenses/LICENSE`, `licenses/LICENSES/CERN-OHL-S-2.0.txt` and
`licenses/LICENSES/GPL-2.0-or-later.txt` listed. With
`MACHINOME_FREECAD_ROOT=<freecad>` (`<scratch>/8.5-check-dist-runtime.txt`),
exit 0:

```
machinome-node-freecad 0.8.1 module /tmp/machinome-check-dist-flu4lz2v/venv/lib/python3.12/site-packages/machinome/node/freecad/__init__.py blocked at its enabled limit, 120 degrees, through FreeCAD
```

Archives (both runs alike): `machinome` sdist 1070 entries, wheel 114;
`machinome-node-freecad` sdist 22, wheel 11 (its four modules and seven
metadata files); `machinome-node-openscad` 23 and 12; every other member 18
and 8. `git status --short --ignored` before and after the first run
identical (`<scratch>/8.5-status-before.txt`, `8.5-status-after.txt`).

## 9. The records

### 9.1 to 9.4 (tasks 9.1 to 9.4)

The bullets of `HISTORY.rst` and `docs/project/changelog.rst`, Decision 13's
text verbatim; `CREDITS.md`'s subsection, two table rows and date; the
architecture's extras sentence and Map row; the root `README.md`'s row,
`CONTRIBUTING.rst`'s pip line and `context7.json`'s rule (valid JSON).

```
$ ... pytest tests/test_repository_layout.py tests/test_kernel_extras.py tests/test_core_kernel_free.py tests/test_supported_node_types.py tests/test_node_root_exports_nothing.py tests/test_core_names_no_split_words.py tests/test_docs_structure.py tests/test_release_records.py tests/test_profile_documentation.py tests/test_leaf_contract_reach.py
144 passed, 1508 subtests passed in 14.64s
```

(`<scratch>/9-gates.txt`.)

### 9.5 ADR-185 (task 9.5)

`docs/adrs/NODE/ADR-185-a-node-type-may-read-a-whole-assembly-through-an-external-program.md`,
Status Proposed, as Decision 13 outlines; its index line in
`docs/adrs/README.md` after ADR-184's; ADR-183's dated consequence of 11
October 2026. Its `Change` link names `openspec/changes/join-freecad/`, to
become the archive's path at 11.1.

### 9.6 The findings (task 9.6)

`workflow/warts.md`'s section of Decision 14, verbatim, at its end. The
second finding's numbers re-measured on the final adapter with the gate's own
functions: two reaches (line 148 `imports machinome.currency`, line 309
`reads private base member self._link_children`) and ten undeclared imports,
as written.

### 9.7 The licences in what this change and the join wrote (task 9.7)

Over the 82 files `git diff --name-only dea7d7f4` and the untracked new files
list, counting the case-insensitive spellings of the product's former
licence and the framework's former one (inside each FCStd document's
members too):

| file | count | what |
|---|---|---|
| `packages/machinome/CREDITS.md` | 16 | 4 written by this change, the FreeCAD and OndselSolver entries and rows; 12 the third parties' entries already there |
| `HISTORY.rst` | 2 | both older history (lines 905 and 1448), none in this change's bullet |
| `packages/machinome/openspec/specs/native-freecad-assembly/spec.md` | 3 | the joined baseline's Purpose and its last requirement's title and text, which the archive and the Purpose's hand edit replaced (11.2: 0 after) |
| `openspec/changes/archive/2026-10-01-native-freecad-assembly/` | 10 | verbatim archive (design 4, proposal 2, spec 2, tasks 2) |
| `workflow/archive/native-freecad-assembly-2026-10-01/` | 13 | verbatim archive (dume-native-freecad 6, implementation-evidence 3, adversarial review 4) |
| every other file, the 27 FCStd documents included | 0 | |

The former module's name stands in `HISTORY.rst` ("formerly"), ADR-185's
context, the warts' first finding, the baseline spec (3, replaced at 11.2) and
the two verbatim archives; the baseline spec's 3 are gone since 11.2.

## 10. Validation

### 10.1 The whole suite (task 10.1)

```
$ env -u MACHINOME_FREECAD_ROOT -u MACHINOME_FREECAD_DUME_SOURCE -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python -m pytest -q -rs -p no:cacheprovider
4798 passed, 24 skipped, 55 warnings, 7136 subtests passed in 700.45s (0:11:40)
```

(`<scratch>/10.1-suite.txt`.) No failure. The 24 skips: the base's 20
(fourteen `test_browser_renderer.py`, `test_cli_lazy_imports.py:172` and
`test_scad_presentation.py:625` without machinome-viewer, the networkx split
of `test_connectivity.py:314`, `test_jscad_integration.py:25` without the
jscad command, two `test_step_assembly.py` without the vendor STEP) and the
four FreeCAD modules, `SKIPPED [4] tests/freecad_support.py:21:
MACHINOME_FREECAD_ROOT is not set: the FreeCAD node package's tests need an
extracted FreeCAD 1.1.4 runtime`. Passed: the base's 4796 and two new tests,
`NavigationTest.test_the_freecad_guide_is_a_how_to` and
`TheFreeCADTestsSkipWithoutARuntimeTest.test_the_public_module_skips_naming_the_variable`;
one renamed, `test_it_names_the_eight_node_types_and_their_classes` to
`test_it_names_the_nine_node_types_and_their_classes`. Subtests 7136, 107
more than the base's: the `freecad` rows the gates iterate.

### 10.2 The FreeCAD modules on the final tree (task 10.2)

With the runtime and the Dum-E variable, as 6.5:

```
82 passed in 153.89s (0:02:33)
```

(`<scratch>/10.2-freecad.txt`.)

### 10.3 The lint (task 10.3)

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/flake8 --max-line-length=89 machinome tests (the ten package paths) ../machinome-node-freecad/machinome | wc -l
1508
```

(`<scratch>/10.3-lint.txt`.) 759 from the base's paths, unchanged; 113 from
the package (`adapter.py` 31, `runtime.py` 11, `worker.py` 71, `__init__.py`
0); 636 from the joined tests and helpers (`test_freecad_public.py` 133,
`test_freecad_constraints.py` 149, `test_freecad_diagnostics.py` 70,
`test_freecad_freshness.py` 139, `freecad_native_reference.py` 26,
`freecad_origin_model.py` 1, `freecad_generate_fixtures.py` 118,
`freecad_support.py` 0). The same files as joined (dba7dae5), linted in
scratch: package 116 (`__init__.py` 3, replaced), tests and helpers 614. The
22 more on the tests are E402, the imports after the guard's call in the four
modules.

### 10.4 The manual on the final tree (task 10.4)

The build of 7.4 into `<scratch>/jf-html-final`: exit 0, no warning
(`<scratch>/10.4-sphinx.txt`).

### 10.5 `check-dist` on the final tree and on a clean copy (task 10.5)

Without `MACHINOME_FREECAD_ROOT`, on the tree
(`<scratch>/10.5-check-dist-tree.txt`) and on a clean copy
(`<scratch>/10.5-check-dist-clean.txt`): `git ls-files -z --cached --others
--exclude-standard` packed with `tar --null -T -` and unpacked under
`<scratch>/jf-clean/` (3500 entries, links kept: the 3495 tracked files, the
two new links and the three new files not yet added). Both exit 0, every
archive `twine check --strict` PASSED, the FreeCAD row "refused without
MACHINOME_FREECAD_ROOT, as documented", nothing uploaded.

| archive | tree | clean copy | base clean copy |
|---|---|---|---|
| `machinome` sdist | 1118 | 1045 | 1006 |
| `machinome` wheel | 114 | 114 | 114 |
| `machinome-node-freecad` sdist | 22 | 22 | |
| `machinome-node-freecad` wheel | 11 | 11 | |
| every other member | as 8.5 | as 8.5 | |

The tree's framework sdist also carries ignored files the suite leaves under
`tests/` (1070 at 8.5, before the whole suite; 1118 after it); the clean
copy's is the release's. The framework's sdist grows by 39 entries, both
clean copies' sdists built in scratch and listed
(`<scratch>/sdist-base.txt`, `sdist-final.txt`, `sdist-added.txt`; the base
from `git archive cf631645`), none removed: the guide
`docs/howto/freecad-assemblies.rst`, the eight test modules and helpers
(`tests/test_freecad_*.py`, `tests/freecad_*.py`, `freecad_support.py`
among them), and the 27 FCStd documents, their README and the two
directories under `tests/fixtures/freecad/`. The wheel is unchanged.

### 10.6 Dum-E (task 10.6, the orchestrator's)

In Dum-E's own repository, `/home/asa/devel/machinome/projects/Robotic-Arms/Dum-E`,
edited and committed by the orchestrator as 26ae7aa ("Import the FreeCAD
adapter from machinome.node.freecad"): `simulation/dume.py`,
`simulation/test_preparation.py` and `simulation/tools/environment.py`
import from `machinome.node.freecad` (`environment.py` as `import
machinome.node.freecad as machinome_freecad`); `pyproject.toml`'s
`dependencies = ["machinome[freecad]~=0.8.1"]`; `docs/issues.md`'s DUME-006
gains a dated update with the vet result. With the bench venv first on
`PATH` and the runtime set, from the project's root:

```
$ python -m pytest -q -p no:cacheprovider simulation/test_dume.py simulation/test_preparation.py
7 passed in 37.17s
$ machinome snapshot -o <scratch>/dume-posed.png --autocenter --drive turn=70 --drive shoulder=15 --drive elbow=110 --drive wrist=-25 --imgsize 1280x960
exit 0
$ sha256sum <scratch>/dume-posed.png
40f8d56813970cbfc958c9e7e532646d2e31b20d754989271b42c20aecf3b804
$ machinome vet
simulation.dume:DumE  pure
project  pure
exit 0
```

The SHA-256 equals that of Dum-E's `snapshot-corrected-posed.png` of 1
October 2026; the image, looked at by the orchestrator, shows the arm on its
base, turned and articulated, the holder attached. `git status` in Dum-E
afterwards: the project's edits only, then committed. The vet result is the
first finding of `workflow/warts.md` (Decision 14), not a gate.

### 10.7 The universe sweep (task 10.7, the orchestrator's)

design.md Decision 17's command with the runtime set, after the Dum-E move:
63 repositories, 130 rows: 122 ok, 0 expected, 2 unexpected, 0 timeout, 6
no-model; 2 skipped by the skip rules (`.Trash-1000` and `sandbox`). Dum-E's
row ok (8.51 s, tests `simulation/test_dume.py`), where the base had it
unexpected on `No module named 'machinome_freecad'`. The 2 unexpected are
the base's: `3D-Printers/fender-bender` (`No module named 'fb_library'`, the
project's own dependency) and 3DPrintedClocks `wall_clock_41` (its own
`ParameterError`). The sweep exits 1 because unexpected rows exist, as at the
base. No other row differs.

### The orchestrator's own run of 10.1, 10.2, 10.4 and 10.5 (11 October 2026)

On the final tree, the bench venv:

- The whole suite without the runtime, one process from
  `packages/machinome`: 4798 passed, 24 skipped, 55 warnings, 7136 subtests
  passed in 677.13 s; the 24 skips the base's 20 and `SKIPPED [4]
  tests/freecad_support.py:21: MACHINOME_FREECAD_ROOT is not set ...`.
- The four FreeCAD modules with the runtime and
  `MACHINOME_FREECAD_DUME_SOURCE` set to Dum-E's
  `upstream/MA_Dum_E_v2_Assembly.FCStd`: 82 passed in 146.56 s.
- The manual, a fresh uv venv from `docs/requirements.txt` alone,
  `sphinx -b html -W --keep-going`: exit 0; `howto/freecad-assemblies.html`
  present; `reference/api.html` names `FreeCADAssemblyNode` 5 times.
- `scripts/check-dist`: on the tree without the runtime exit 0, the FreeCAD
  row "refused without MACHINOME_FREECAD_ROOT, as documented"; on the tree
  with the runtime exit 0, "blocked at its enabled limit, 120 degrees,
  through FreeCAD"; on a clean copy (`git ls-files` packed with `tar
  --null`, links kept) without the runtime exit 0, the refusal row. Nothing
  uploaded.

### 10.8 Git (task 10.8)

`git -C <bench> status --short`: 74 lines (`<scratch>/10.8-status.txt`), the
edited and added files of groups 4 to 9 and nothing else: 27 regenerated
FCStd documents, 42 other modified files, the two links added, and three new
files (`tests/freecad_support.py`, ADR-185 and this file).
`git ls-files -ci --exclude-standard | wc -l`: 34, as at the base. Ignored,
besides the base's: the suite's own leavings under `tests/` and the
package's `__pycache__/` and `egg-info/`.

### 10.9 OpenSpec (task 10.9)

```
$ env -C <bench>/packages/machinome openspec validate join-freecad --strict
Change 'join-freecad' is valid
```

## Departures from the design

1. **The package's `__init__` docstring.** Decision 4's verbatim docstring
   says the solids are "read through the OCCT binding"; the split-word gate
   (W4) refuses `OCCT` in any module outside its zones, and Decision 10 adds
   only the worker to them. The sentence reads "read through `OCP`", the
   module the check names; the zones are unchanged.
2. **`test_the_root_refuses_each_class_naming_its_module`**
   (`test_supported_node_types.py`), which Decision 10 does not name, asserts
   each class's `__module__` is `machinome.node.<key>`; the FreeCAD classes
   are defined in `machinome.node.freecad.adapter` (the `node-model` delta's
   scenario says so). The assertion admits `machinome.node.<key>.adapter`
   besides, with a comment naming the change.
3. **The skip test** admits pytest's exit status 5 as well as 0: a module
   skipped whole collects no test, and pytest reports that with 5. It still
   asserts "1 skipped", the variable's name, and no `failed` or `error`.
4. **The guide's vocabulary.** The imported `docs/api.md` says "exact
   geometry", "exact leaf" and "the framework OCCT kernel"; the guide says
   "B-rep leaf" and "the B-rep engine", the names since ADR-180. It also drops
   the product's paragraph on the untouched and corrected Dum-E sources and
   the link to the workflow archive, as Decision 12 asks.
5. **The lint** grows by 22 E402 lines the guard's placement causes (10.3);
   the design's estimate did not count them.
6. **`test_docs_structure.py`** was red at 3.6 on one more subtest than the
   task listed (the stale former module on the imported page); it is green
   since the conversion.
7. **Placements the design left open.** `CREDITS.md`'s two summary rows
   follow `manifold3d`'s, the last runtime dependency; ADR-185's index line
   follows the index's own form, its separator included; ADR-185's `Change`
   link names the change's present path, which 11.1 points at the archive.
8. **The guide's setup** names the extraction's root and its four entries but
   gives no extraction command: the AppImage's file name is not recorded
   anywhere the applier read.

## The orchestrator's review of the checkpoint (11 October 2026)

The orchestrator reviewed the checkpoint, passed it, ran its own validation
(10.1, 10.2, 10.4 and 10.5 above), performed 10.6 and 10.7, and asked for
group 11 with nothing else changed.

## 11. Records closing

### 11.1 ADR-185 (task 11.1)

`docs/adrs/NODE/ADR-185-a-node-type-may-read-a-whole-assembly-through-an-external-program.md`:
Status Accepted, its `Change` link repointed at
`openspec/changes/archive/2026-10-11-join-freecad/`. `docs/adrs/README.md`:
its line **Accepted**; ADR-183's line ends "amended by 184, amended by 185".
ADR-183's Status line gains "a product of a repository of its own joining as
an extension package, amended 2026-10-11 by ADR-185". `docs/architecture.md`
checked against it: the extras sentence names `[freecad]` and its
distribution, and the Map's FreeCAD row cites 004, 183, 184 and 185; no edit.

### 11.2 The archive (task 11.2)

`openspec/specs/` copied to `<scratch>/jf-specs-before/` first.

```
$ env -C <bench>/packages/machinome openspec archive join-freecad -y
Proposal warnings in proposal.md (non-blocking):
  ⚠ Why section should not exceed 1000 characters
  ⚠ Consider splitting changes with more than 10 deltas
Task status: 51/57 tasks
Warning: 6 incomplete task(s) found. Continuing due to --yes flag.
...
Applying changes to openspec/specs/framework-contributor-guidance/spec.md:
  ~ 1 modified
Applying changes to openspec/specs/framework-identity/spec.md:
  ~ 1 modified
Applying changes to openspec/specs/kernel-extras/spec.md:
  ~ 4 modified
Applying changes to openspec/specs/native-freecad-assembly/spec.md:
  ~ 2 modified
  → 1 renamed
Applying changes to openspec/specs/node-model/spec.md:
  ~ 1 modified
Applying changes to openspec/specs/user-documentation/spec.md:
  + 1 added
Totals: + 1, ~ 9, - 0, → 1
Specs updated successfully.
Change 'join-freecad' archived as '2026-10-11-join-freecad'.
```

(`<scratch>/11.2-archive.txt`.) The six incomplete tasks were 10.6, 10.7 and
11.1 to 11.4, ticked in the archived `tasks.md` after this section. No spec
was added or removed; the changed lines against the copy: contributor
guidance 4, framework identity 36, kernel extras 82, native FreeCAD assembly
34, node model 35, user documentation 44. Then the Purpose of
`openspec/specs/native-freecad-assembly/spec.md`, which the archive leaves,
replaced by design.md Decision 16's text, and:

```
$ env -C <bench>/packages/machinome openspec validate --specs --strict
Totals: 46 passed, 0 failed (46 items)
```

(`<scratch>/11.2-validate.txt`.) The baseline spec once more: its last
requirement is "The FreeCAD node package and its documented public
contract"; the former module (`machinome_freecad`, not the variable
`MACHINOME_FREECAD_ROOT`) 0 times, the former licences 0 times.

### 11.3 The plan (task 11.3)

`workflow/ongoing/joins-0.9.md` at the root, "Progress": the cycle's entry,
in the form `monorepo-0.9.md` records its cycles.

### 11.4 This file (task 11.4)

Complete. The implementation commit is the orchestrator's; the planning and
merge commits are untouched; nothing pushed.
