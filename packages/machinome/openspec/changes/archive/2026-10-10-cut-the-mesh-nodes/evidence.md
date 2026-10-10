# Evidence: `cut-the-mesh-nodes`

The fourth and last cycle of the cut in the 0.9 monorepo campaign
(`workflow/ongoing/monorepo-0.9.md` at the repository root, "The campaign: the
cut", cycle 4). Worktree `machinome/WTs/v0.9-base-cut-the-mesh-nodes`, branch
`v0.9-base-cut-the-mesh-nodes`, cut from the line `v0.9-base` at 10e07f8c
("Implement cut-the-brep-nodes"). Planning commit bc2eff29, ratified by the
orchestrator's review. Applied on 10 October 2026.

Tools: uv 0.11.8, CPython 3.12.3 (the bench venv), the OpenSpec CLI 1.6.0,
OpenSCAD 2021.01 at `/usr/bin/openscad`, no `jscad` command. Every command ran
with `env -C <dir>` and absolute paths; `<bench>` is
`/home/asa/devel/machinome/machinome/WTs/v0.9-base-cut-the-mesh-nodes` and
`<scratch>` is
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C4-apply/`.
Every test ran from `<bench>/packages/machinome` on the bench venv
(`<bench>/.venv/bin/python -m pytest -q -p no:cacheprovider ...`), one pytest
process at a time. Logs are in `<scratch>`, never in the bench.

## 1. Evidence baseline

### 1.1 The base (task 1.1)

```
$ git -C <bench> log --oneline -2
bc2eff29 Propose cut-the-mesh-nodes: the OpenSCAD family, solid2, jscad and stl as extension packages (decided 10 October 2026)
10e07f8c Implement cut-the-brep-nodes: the CadQuery, build123d, STEP and molejo node types as extension packages
$ git -C <bench> status --short | wc -l
0
```

`git status --short --ignored` showed `!! .env` alone (the bench's port file).

### 1.2 The bench venv on the base's tree (task 1.2)

```
$ env -C <bench> /home/asa/.local/bin/uv sync --python 3.12
Using CPython 3.12.3 interpreter at: /usr/bin/python3.12
Creating virtual environment at: .venv
Resolved 183 packages in 7ms
...
Prepared 7 packages in 1.53s
Installed 174 packages in 7.52s
$ uv pip list --python <bench>/.venv/bin/python | tail -n +3 | wc -l
174
```

183 resolved, 174 installed. Seven `__editable__` files, one line each:

```
__editable__.machinome-0.8.1.pth: <bench>/packages/machinome
__editable__.machinome_engine_brep-0.8.1.pth: <bench>/packages/machinome-engine-brep
__editable__.machinome_engine_mesh-0.8.1.pth: <bench>/packages/machinome-engine-mesh
__editable__.machinome_node_build123d-0.8.1.pth: <bench>/packages/machinome-node-build123d
__editable__.machinome_node_cadquery-0.8.1.pth: <bench>/packages/machinome-node-cadquery
__editable__.machinome_node_molejo-0.8.1.pth: <bench>/packages/machinome-node-molejo
__editable__.machinome_node_step-0.8.1.pth: <bench>/packages/machinome-node-step
```

The base suite on the same tree and recipe, recorded from the third cycle's
evidence (10.1), not rerun: `4791 passed, 20 skipped, 6914 subtests passed`.

### 1.3 The lint base (task 1.3)

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/flake8 --max-line-length=89 machinome tests ../machinome-engine-brep/machinome ../machinome-engine-mesh/machinome ../machinome-node-build123d/machinome ../machinome-node-cadquery/machinome ../machinome-node-molejo/machinome ../machinome-node-step/machinome | wc -l
759
```

2 of them E402, both in `tests/test_couplings.py` (lines 3602 and 3603);
one of them under a path this change moves:
`machinome/node/openscad/__init__.py:88:90: E501` (`<scratch>/1.3-lint.txt`).

### 1.4 The sweep base (task 1.4, recorded, not rerun)

The third cycle's counts (design.md, Decision 13): 63 repositories, 130 rows,
121 ok, 0 expected, 3 unexpected (wall_clock_41's own CadQuery error, Dum-E
without machinome-freecad, fender-bender without `fb_library`), 0 timeout, 6
no-model.

## 2. Red first, at the base's paths

Nothing moved in this group.

### 2.1 The layout gate (task 2.1)

`tests/test_repository_layout.py`: `EXTENSIONS`' four rows;
`PACKAGE_PORTIONS` and `portion_files` (design.md Decision 9, verbatim);
`test_each_extension_directory_holds_only_what_distinguishes_it` lists
`portion_files(name, address)` and admits as the only `__init__.py` under
`machinome/` a package portion's own at its address;
`test_each_extension_manifest_is_a_portion_of_the_set` expects `include` the
address itself for a package portion; `test_each_portion_resolves_from_its_package`
compares with `portion_files(name, address)[0]`;
`test_the_core_node_package_holds_no_extension_module` also refuses a
directory named for the address; the two new tests
`test_the_core_node_package_holds_no_node_type` (every key of
`machinome.node.supported.NODE_TYPES`) and
`test_the_core_viewers_hold_no_node_type_s_renderer`; the module docstring
names the four.

```
$ ... pytest tests/test_repository_layout.py
25 failed, 29 passed, 136 subtests passed in 5.81s
```

(`<scratch>/2.1-layout-red.txt`; 24 of the 25 are subtests.)

- `test_each_extension_directory_holds_only_what_distinguishes_it`, the four
  new subtests: `<bench>/packages/machinome-node-<x> is missing`.
- `test_each_extension_manifest_is_a_portion_of_the_set`, the four:
  `FileNotFoundError` on `packages/machinome-node-<x>/pyproject.toml`.
- `test_each_extension_readme_names_its_install_and_the_licence`, the four:
  `FileNotFoundError` on the four `README.md`.
- `test_each_portion_resolves_from_its_package`, the four: the module
  resolves under `packages/machinome/`, e.g.
  `.../packages/machinome/machinome/node/openscad/__init__.py != .../packages/machinome-node-openscad/machinome/node/openscad/__init__.py`
  and `.../packages/machinome/machinome/node/stl.py != .../packages/machinome-node-stl/machinome/node/stl.py`.
- `test_the_core_node_package_holds_no_extension_module`, the four:
  `.../machinome/node/jscad.py is in the core`, `solid2.py`, `stl.py`, and
  `.../machinome/node/openscad/ is in the core` (the directory check).
- `test_the_core_node_package_holds_no_node_type`, four subtests
  (`openscad`, `solid2`, `jscad`, `stl`), the same four messages.
- `test_the_core_viewers_hold_no_node_type_s_renderer`: `Items in the first
  set but not the second: 'openscad.py'`.

Green as expected: the earlier rows of the four per-package tests,
`test_every_sibling_is_in_the_table`, the README test and
`test_the_guide_installs_every_member_without_uv` (no new directory yet).

### 2.2 `tests/test_kernel_extras.py` (task 2.2)

`EXTRAS['openscad']`, `['solid2']`, `['jscad']` and `['stl']` each
`{f'machinome-node-<x>~={VERSION}'}`, the `root-cleanup` comment above `jscad`
and `stl` replaced by one naming this change; `PACKAGE_REQUIREMENTS` gains the
four sets of Decision 9; `NODE_PACKAGES` keeps every `machinome-node-*` name and
`BREP_NODE_PACKAGES` names the four over the B-rep engine, read by
`test_every_node_package_requires_the_brep_engine`;
`test_no_node_extra_includes_the_mesh_engine` reads the eight node extras;
`test_the_solid2_extra_installs_the_openscad_extra` replaced by
`test_the_solid2_package_requires_the_openscad_package`; the new
`test_solidpython_carries_one_range_wherever_it_is_named`, which reads the
core's dependencies and extras and every sibling manifest and requires the
places naming SolidPython to be the two family packages, in the range
`==2.1.*` (departure 1); the docstring.

```
$ ... pytest tests/test_kernel_extras.py
11 failed, 15 passed, 56 subtests passed in 1.60s
```

(`<scratch>/2.2-extras-red.txt`)

- `test_each_extra_lists_what_its_module_needs`, subtests `openscad`
  (`{'solidpython2==2.1.*'}` against `{'machinome-node-openscad~=0.8.1'}`),
  `solid2` (`{'machinome[openscad]'}` against
  `{'machinome-node-solid2~=0.8.1'}`), `jscad` and `stl` (the empty set
  against `{'machinome-node-<x>~=0.8.1'}`).
- `test_each_extension_package_requires_the_core_and_its_kernel`, the four
  new subtests: `FileNotFoundError` on `packages/machinome-node-<x>/pyproject.toml`.
- `test_the_solid2_package_requires_the_openscad_package`: `FileNotFoundError`
  on `packages/machinome-node-solid2/pyproject.toml`.
- `test_solidpython_carries_one_range_wherever_it_is_named`:
  `['machinome[openscad]'] != ['machinome-node-openscad', 'machinome-node-solid2']`
  (named once, in the core).
- `test_the_lock_installs_every_kernel`: `machinome-node-openscad`,
  `-solid2`, `-jscad`, `-stl` not in the lock.

Green: the earlier rows, `test_every_node_package_requires_the_brep_engine`
(four B-rep subtests), `test_no_node_extra_includes_the_mesh_engine` (eight
extras), the refusal tests.

### 2.3 `tests/test_core_kernel_free.py` (task 2.3)

`KERNELS` gains `solid2`; `KERNEL_MODULES` gains `machinome.node.openscad` and
`machinome.node.solid2`; the tuple `EXTENSION_MODULES` (the eight node modules
and the two engine providers) and the new test
`test_the_core_imports_no_node_type_and_no_engine_provider`, which expects the
two templates alone; the core census of
`test_kernels_are_imported_only_by_their_modules` expects the two templates
(`cadquery`, `solid2`); `test_the_extension_packages_import_only_their_kernels`
expects the family's three entries, each `['solid2']`; `EXTRA_OF` gains the
OpenSCAD package's `__init__.py` (`openscad`) and the solid2 module (`solid2`);
`kernel_module_of`, `own_package` and the rewritten `kernel_modules_named`
(a name beneath a kernel module counts as that module, every string constant
is read, a node package's module naming its own package is not counted);
`SEAMS` gains the solid2 module, `machinome/node/supported.py` and the template
`solid2.py`; the seams test asserts the solid2 module's and the table's entries
exactly; `TABLE_READERS` gains `machinome/manager/snapshot.py` and
`machinome/manager/new.py`; the docstring.

```
$ ... pytest tests/test_core_kernel_free.py
12 failed, 8 passed, 26 subtests passed in 4.05s
```

(`<scratch>/2.3-kernel-free-red.txt`)

- `test_kernels_are_imported_only_by_their_modules`: the census also holds
  `machinome/node/openscad/__init__.py`, `machinome/node/openscad/writer.py`
  and `machinome/node/solid2.py`, each `['solid2']`.
- `test_the_core_imports_no_node_type_and_no_engine_provider`: besides the
  two templates, the census finds `machinome/node/openscad/__init__.py`
  (`machinome.node.openscad.leaf`, `.writer`), `leaf.py`
  (`machinome.node.openscad`, `.binary`, `.writer`), `writer.py`
  (`machinome.node.openscad.leaf`), `machinome/node/solid2.py`
  (`machinome.node.openscad.binary`, `.leaf`) and `machinome/viewers/openscad.py`
  (`machinome.node.openscad`, `.binary`, `.writer`).
- `test_the_extension_packages_import_only_their_kernels`: the portion census
  holds no family module (the three expected entries missing).
- `test_each_kernel_module_checks_its_kernel_first`, two subtests: `KeyError`
  on `machinome-node-openscad/machinome/node/openscad/__init__.py` and
  `machinome-node-solid2/machinome/node/solid2.py`.
- `test_kernel_modules_are_named_only_at_the_seams`, seven subtests: the
  core's `machinome/node/openscad/__init__.py`, `leaf.py`, `writer.py`,
  `machinome/node/solid2.py` and `machinome/viewers/openscad.py`, each
  `{'machinome.node.openscad'} not less than or equal to set()`; the seam
  `machinome-node-solid2/machinome/node/solid2.py` (`None !=
  {'machinome.node.openscad'}`, the key absent); and the seam
  `machinome/node/supported.py` (`None != {'machinome.node.openscad'}`: the
  row still names `machinome.viewers.openscad.OpenScadRenderer`, until task
  4.3). The last is not among the reds tasks.md lists; it is the renderer
  row's edit seen from the census, and turns green with it (departure 2).

### 2.4 `tests/test_core_names_no_scad.py` (task 2.4)

`ALLOWED_PACKAGES` (the family's two distributions, the first spelled in
pieces), `ALLOWED_MODULES` with the table alone, `allowed` reading a path's
first component against the packages, `scan(root, prefix)`, the gate merging
`scan()` of the core with `scan(package, prefix=f'{package.name}/')` of every
`packages/machinome-*`, `test_the_allowed_zones` (the two packages' paths
allowed; the core's former zones and `machinome-node-stl/machinome/node/stl.py`
not), the docstring.

```
$ ... pytest tests/test_core_names_no_scad.py
1 failed, 4 passed, 15 subtests passed in 0.57s
  65 machinome/viewers/openscad.py
  57 machinome/node/openscad/__init__.py
  44 machinome/node/openscad/leaf.py
  33 machinome/node/openscad/writer.py
  31 machinome/node/solid2.py
  15 machinome/node/openscad/binary.py
modules: 6  occurrences: 245
```

(`<scratch>/2.4-scad-red.txt`) Probe 7's counts exactly. `TheRuleTest`'s four
tests green, `test_the_allowed_zones` included.

### 2.5 The scans that expected the viewer to reach the family (task 2.5)

Departure 3, found before editing. Design.md Decision 9 makes
`test_expression_type.py`'s `BINARY_REACHES` and `test_scad_presentation.py`'s
`ENGINE_REACHES` empty and names the tests
`test_no_core_module_reaches_the_family_package` and
`..._familys_package`. Both scans count a module that spells
`machinome.node.openscad` or a name beneath it as a string constant
(`ENGINE_NAME = ^machinome\.node\.openscad(\.\w+)*$`), so after Decision 3 the
table's renderer row `'machinome.node.openscad.renderer.OpenScadRenderer'`
reaches the family by name:

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/python -c "...names_the_engine_package(ast.parse(<supported.py with the row of Decision 3>))"
True
```

The proposer's own probe 6 log shows it (`<C4-propose>/suite-cut2.log`, lines
231-234 and 599-602): `Items in the first set but not the second:
'machinome/node/supported.py'`; design.md's "the set is now empty" misreads
it. With empty sets the two tests would stay red after the cut. Applied
instead: each set is `{'machinome/node/supported.py'}`, its comment saying no
core module imports the family's package since the renderer moved into it and
the table names the renderer's module by string in its provisional row (the
same fact `test_core_kernel_free.py`'s `SEAMS` records for the table under
Decision 9), and the tests are renamed
`test_only_the_table_reaches_the_family_package` and
`test_only_the_table_reaches_the_familys_package`.

```
$ ... pytest tests/test_expression_type.py::NoExpressionImportTest::test_only_the_table_reaches_the_family_package tests/test_scad_presentation.py::ImportersTest::test_only_the_table_reaches_the_familys_package
2 failed in 0.80s
```

Each: `Items in the first set but not the second: 'machinome/viewers/openscad.py'`
and `Items in the second set but not the first: 'machinome/node/supported.py'`
(`<scratch>/2.5-reaches-red.txt`).

### 2.6 The renderer's address in the suite (task 2.6)

`machinome.viewers.openscad` became `machinome.node.openscad.renderer` in:
`test_snapshot.py` (three imports, two `patch` strings);
`test_openscad_dependency.py` (`from machinome.node.openscad import renderer as
openscad_viewer`, the class import, one `patch` string); `test_markings.py` and
`test_build_publication.py` (one import each); `test_browser_renderer.py` (one
`patch` string); `test_openscad_node.py` (the import in `CountingWriterTest`,
the refusal door `import machinome.node.openscad.renderer` with the test
renamed `test_the_renderer_refuses_with_the_package`, the two file reads
through `importlib.util.find_spec(...).origin` with `import importlib.util`
added, the first test renamed `test_the_renderer_imports_neither_former_address`,
and the module docstring naming the `renderer` module).

```
$ grep -rn "viewers.openscad\|viewers import openscad\|viewers/openscad" <bench>/packages/machinome/tests
tests/test_snapshot.py:595:                with self.assertLogs('viewers.openscad',
tests/test_snapshot.py:670:        with self.assertLogs('viewers.openscad', level='WARNING') as logs:
tests/test_snapshot.py:683:        with self.assertLogs('viewers.openscad', level='DEBUG') as logs:
```

Only the three `assertLogs` channels remain.

```
$ ... pytest tests/test_snapshot.py tests/test_openscad_dependency.py tests/test_markings.py tests/test_build_publication.py tests/test_browser_renderer.py tests/test_openscad_node.py tests/test_no_class_name_recognition.py
4 errors in 3.11s
```

(`<scratch>/2.6-address-red.txt`) Collection errors:

- `test_snapshot.py` (line 17) and `test_markings.py` (line 48):
  `ModuleNotFoundError: No module named 'machinome.node.openscad.renderer'`.
- `test_openscad_dependency.py` (line 23) and, through it,
  `test_no_class_name_recognition.py`: `ImportError: cannot import name
  'renderer' from 'machinome.node.openscad'`. The form `from package import
  submodule` reports a missing submodule as an `ImportError` on the name, not
  as the `ModuleNotFoundError` tasks.md expects; the cause is the same.

The other three modules collected, run on their own:

```
$ ... pytest tests/test_build_publication.py tests/test_browser_renderer.py tests/test_openscad_node.py
4 failed, 50 passed, 14 skipped, 1 warning, 12 subtests passed in 8.13s
```

(`<scratch>/2.6-address-red-b.txt`)

- `test_build_publication.py`
  `SweepByDeclarationTest.test_the_renderer_marks_only_a_root_it_does_not_keep_transient`:
  `ModuleNotFoundError: No module named 'machinome.node.openscad.renderer'`.
- `test_browser_renderer.py`
  `CaptureDelegationTest.test_browser_failure_never_falls_back_to_openscad`:
  `AttributeError: module 'machinome.node.openscad' has no attribute
  'renderer'` (the `patch` string).
- `test_openscad_node.py` `ThePackageTest.test_the_renderer_imports_neither_former_address`:
  `AttributeError: 'NoneType' object has no attribute 'origin'` (no spec).
- `test_openscad_node.py`
  `CountingWriterTest.test_the_binary_for_a_stale_solid2nodes_stl_and_the_renderer`:
  `ModuleNotFoundError`.

`TheThreeDoorsTest.test_the_renderer_refuses_with_the_package` is green at the
base: with SolidPython absent, `import machinome.node.openscad.renderer` is
refused by the package's `__init__` before the submodule is looked for, with
R1. The 14 skips are `test_browser_renderer.py`'s viewer tests.

### 2.7 `tests/test_supported_node_types.py` (task 2.7)

`test_one_renderer_is_contributed_and_it_is_the_default` expects the module
`machinome.node.openscad.renderer`. `AbsentPackageTest` generalised:
`package_directory(key)`, `refused(key)` (the refusal built from the key and
the row's classes), `doors(key)` (the four doors) and the table `ABSENCES`:
the step rows as they were; the four doors of `openscad`, `solid2`, `jscad`
and `stl`; with `machinome-node-openscad` dropped also `import
machinome.node.openscad.renderer`, `supported.renderer('openscad')` and `from
machinome.node.solid2 import Solid2Node`, each expecting the `openscad`
refusal; `passed` indents a multi-line door with `textwrap.indent`;
`test_the_other_node_packages_still_import` imports `machinome.node.cadquery`
with the step package dropped and `machinome.node.stl` with the OpenSCAD
package dropped; the new `test_the_snapshot_refuses_an_absent_openscad_package`
writes a temporary project (a `pyproject.toml` naming `demo:Demo` and a
`Solid2Node` of a 2 x 3 x 4 cube), runs `machinome snapshot -o <tmp>/x.png` in
it through `run_python` with the OpenSCAD package's directory dropped and
`machinome.cli.manage()` called, and expects exit 1, the last line of standard
error the line of probe 2, and no image. The class docstring names the
change.

```
$ ... pytest tests/test_supported_node_types.py
21 failed, 11 passed, 39 subtests passed in 9.49s
```

(`<scratch>/2.7-supported-red.txt`)

- `test_one_renderer_is_contributed_and_it_is_the_default`: the module is
  `machinome.viewers.openscad`.
- `test_every_door_refuses_the_absent_package_by_its_extra`, 19 new subtests:
  `['passed', None]` for 14 import doors and `supported.renderer('openscad')`,
  `['passed', True]` for the four `hasattr` doors (the modules are in the core
  and import; no refusal), and for `import machinome.node.openscad.renderer`
  `['ModuleNotFoundError', 'machinome.node.openscad.renderer', None, "No
  module named 'machinome.node.openscad.renderer'"]` (the module does not yet
  exist, rather than a pass).
- `test_the_snapshot_refuses_an_absent_openscad_package`: `0 != 1 : Snapshot
  saved to /tmp/absent-snapshot-.../x.png`, after `viewers.openscad - Rendering
  .../_build/demo-Demo-8a2cc0673b1c.scad to .../x.png`: the command renders.

Green: the step rows of the doors test, both subtests of
`test_the_other_node_packages_still_import`, the other table tests.

### 2.8 `tests/test_docs_structure.py` (task 2.8)

`test_the_installation_page_names_the_extension_distributions` names the ten
distributions, its comment naming this change.

```
$ ... pytest tests/test_docs_structure.py
4 failed, 17 passed, 767 subtests passed in 0.31s
```

The four new subtests: `machinome-node-<x>` not found on `start/install.rst`
(`<scratch>/2.8-docs-red.txt`).

### 2.9 (task 2.9)

Every red above is the one tasks.md names, with the reason it names, except:
the seam subtest `machinome/node/supported.py` of 2.3 (an added red, the table
row's edit of task 4.3; departure 2); the two scans of 2.5, whose expected sets
hold the table (departure 3); and in 2.6 the `ImportError` form of
`from machinome.node.openscad import renderer` and the renderer door of 2.7
reporting `ModuleNotFoundError` rather than a pass, both the module not
existing yet.

## 3. The cut

### 3.1 The move (task 3.1)

```
$ for x in openscad solid2 jscad stl; do mkdir -p <bench>/packages/machinome-node-$x/machinome/node; done
$ git -C <bench> mv packages/machinome/machinome/node/openscad packages/machinome-node-openscad/machinome/node/openscad
$ git -C <bench> mv packages/machinome/machinome/viewers/openscad.py packages/machinome-node-openscad/machinome/node/openscad/renderer.py
$ for x in solid2 jscad stl; do git -C <bench> mv packages/machinome/machinome/node/$x.py packages/machinome-node-$x/machinome/node/$x.py; done
$ git -C <bench> diff --cached -M100% --name-status | grep ^R
R100	packages/machinome/machinome/node/jscad.py	packages/machinome-node-jscad/machinome/node/jscad.py
R100	packages/machinome/machinome/node/openscad/__init__.py	packages/machinome-node-openscad/machinome/node/openscad/__init__.py
R100	packages/machinome/machinome/node/openscad/binary.py	packages/machinome-node-openscad/machinome/node/openscad/binary.py
R100	packages/machinome/machinome/node/openscad/leaf.py	packages/machinome-node-openscad/machinome/node/openscad/leaf.py
R100	packages/machinome/machinome/viewers/openscad.py	packages/machinome-node-openscad/machinome/node/openscad/renderer.py
R100	packages/machinome/machinome/node/openscad/writer.py	packages/machinome-node-openscad/machinome/node/openscad/writer.py
R100	packages/machinome/machinome/node/solid2.py	packages/machinome-node-solid2/machinome/node/solid2.py
R100	packages/machinome/machinome/node/stl.py	packages/machinome-node-stl/machinome/node/stl.py
```

Eight renames, no content change. The `git mv` of the directory carried its
ignored `__pycache__/` with it; the core's `machinome/node/` holds no
`openscad` entry afterwards.

### 3.2 The links (task 3.2)

`ln -s ../../LICENSE LICENSE` and `ln -s ../../LICENSES LICENSES` in each new
directory, then `git add`:

```
$ git -C <bench> ls-files -s 'packages/machinome-node-*' | grep -c ^120000
16
```

The eight new links read `../../LICENSE` (blob 30cff740, four times) and
`../../LICENSES` (blob 06ad40db, four times), the earlier siblings' blobs.

### 3.3 The docstring (task 3.3)

The renderer bullet of Decision 1, verbatim, after the `binary` bullet, whose
closing full stop becomes a semicolon so the list reads as the others do
(departure 4: the bullet line itself is the one line of the hunk not in the
design's text).

```
$ git -C <bench> diff --cached -M --name-status | grep openscad/__init__
R095	packages/machinome/machinome/node/openscad/__init__.py	packages/machinome-node-openscad/machinome/node/openscad/__init__.py
$ git -C <bench> diff --cached -M | <the package's hunks>
@@ -10,7 +10,10 @@ every leaf authored in SCAD is built from.
-- `machinome.node.openscad.binary`: the OpenSCAD executable's contract.
+- `machinome.node.openscad.binary`: the OpenSCAD executable's contract;
+- `machinome.node.openscad.renderer`: the OpenSCAD snapshot renderer of
+  `machinome snapshot`, which the table of supported node types names
+  (`machinome.node.supported`, a provisional column).
```

`binary.py`, `leaf.py`, `renderer.py` and `writer.py` stay `similarity index
100%`; the moved file was `git add`ed so the rename shows in the index.

### 3.4 The moved tree before the manifests (task 3.4)

```
$ ... pytest tests/test_repository_layout.py tests/test_core_kernel_free.py tests/test_core_names_no_scad.py tests/test_supported_node_types.py
36 failed, 54 passed, 238 subtests passed in 8.97s
```

(`<scratch>/3.4-moved.txt`)

- `test_every_member_is_a_workspace_source`: the sources lack the four
  `machinome-node-<x>` (four directories, no source).
- `test_the_members_are_the_package_directories`, four subtests:
  `<bench>/packages/machinome-node-<x> holds no pyproject.toml`.
- `test_each_extension_directory_holds_only_what_distinguishes_it`, four: the
  listing lacks `README.md` and `pyproject.toml` (the OpenSCAD row lists
  `LICENSE`, `LICENSES` and the five package files).
- `test_each_extension_manifest_is_a_portion_of_the_set` and
  `test_each_extension_readme_names_its_install_and_the_licence`, four each:
  `FileNotFoundError`.
- `test_the_readme_links_every_package_and_states_the_licence` and
  `test_the_guide_installs_every_member_without_uv`, four each.
- `test_each_portion_resolves_from_its_package`, four: `ExtraUnavailable: the
  <key> node type (<Class>) needs machinome.node.<key>, which is not
  installed; install it with 'pip install "machinome[<key>]"'`. The bench
  venv's `.pth` lines name the core, the engines and the B-rep node packages
  alone, so the four modules are on no path, and ADR-184's finder refuses
  them.
- `test_supported_node_types.py`: `test_the_root_refuses_each_class_naming_its_module`
  and `test_one_renderer_is_contributed_and_it_is_the_default` (the same
  refusals), `LoadRefusesTest.test_a_modules_own_refusal_passes_unmodified`
  (the package's absence, `machinome.node.solid2`, is reported rather than
  the kernel's), `test_a_present_node_type_is_its_module` (`stl` refused);
  `AbsentPackageTest`'s door `solid2` with the OpenSCAD package dropped (the
  solid2 package itself is absent, so the refusal names `solid2`) and
  `test_the_other_node_packages_still_import`'s `stl` subtest (refused).
- `test_core_kernel_free.py`: the seam subtest `machinome/node/supported.py`
  alone (the row is edited in task 4.3).

Green: the core-node and viewers tests, `test_core_names_no_scad.py` whole,
`test_core_kernel_free.py`'s censuses, `AbsentPackageTest`'s other 22 door
subtests and `test_the_snapshot_refuses_an_absent_openscad_package` (every
package of the four being off the path, the absence they stand in for is
already the state of the venv). `test_every_sibling_is_in_the_table`'s red,
shown once:

```
$ mkdir <bench>/packages/machinome-node-stray
$ ... pytest tests/test_repository_layout.py::TheExtensionPackagesTest::test_every_sibling_is_in_the_table
1 failed, 1 passed, 10 subtests passed in 0.12s
AssertionError: 'machinome-node-stray' not found in {...} : packages/machinome-node-stray is not in EXTENSIONS
$ rmdir <bench>/packages/machinome-node-stray
```

## 4. The manifests, the core's extras and the workspace

### 4.1 The manifests (task 4.1)

The four `pyproject.toml` of design.md Decision 2, extracted verbatim from
design.md's blocks; each is byte-identical to the probed draft (`diff
<C4-propose>/drafts/machinome-node-<x>/pyproject.toml`: no output, four
times). Read with `tomllib`:

```
machinome-node-openscad ['machinome~=0.8.1', 'solidpython2==2.1.*'] {'include': ['machinome.node.openscad'], 'namespaces': True}
machinome-node-solid2   ['machinome~=0.8.1', 'machinome-node-openscad~=0.8.1', 'solidpython2==2.1.*'] {'include': ['machinome.node'], 'namespaces': True}
machinome-node-jscad    ['machinome~=0.8.1'] {'include': ['machinome.node'], 'namespaces': True}
machinome-node-stl      ['machinome~=0.8.1', 'trimesh'] {'include': ['machinome.node'], 'namespaces': True}
```

```
$ ... pytest tests/test_release_records.py
4 failed, 13 passed, 100 subtests passed in 0.20s
```

The four failures are `test_the_version_is_bumped_from_the_root`'s new
subtests (`'packages/machinome-node-<x>/pyproject.toml' not found in [...]`,
no table); `test_every_member_is_numbered_with_the_core` and
`test_every_pin_between_members_is_compatible` green. The pin test's red,
shown once:

```
$ sed -i 's/"machinome-node-openscad~=0.8.1",/"machinome-node-openscad>=0.8.1",/' <bench>/packages/machinome-node-solid2/pyproject.toml
$ ... pytest tests/test_release_records.py -k test_every_pin_between_members_is_compatible
1 failed, 1 passed, 12 deselected, 21 subtests passed in 0.13s
SUBFAILED(member='machinome-node-solid2', requirement='machinome-node-openscad>=0.8.1') ... AssertionError: '>=0.8.1' != '~=0.8.1'
```

The manifest restored from its copy; `diff` against the draft: no output.

### 4.2 The READMEs (task 4.2)

The four `README.md` of Decision 2, extracted verbatim from design.md (written
with the manifests, before 4.1's run); each byte-identical to the probed
draft (`diff`: no output, four times). The eight files `git add`ed.

### 4.3 The core's manifest and the renderer row (task 4.3)

`packages/machinome/pyproject.toml`: the `dependencies` comment and the block
from "# The OpenSCAD node family" to the line before `all =`, both as
Decision 4 states.

```
$ git -C <bench> diff packages/machinome/pyproject.toml | grep -c '^@@'
2
$ git -C <bench> diff --stat packages/machinome/pyproject.toml packages/machinome/machinome/node/supported.py
 packages/machinome/machinome/node/supported.py |  2 +-
 packages/machinome/pyproject.toml              | 48 ++++++++++++++++----------
$ git -C <bench> diff packages/machinome/machinome/node/supported.py | grep '^[-+] '
-        ('openscad', 'machinome.viewers.openscad.OpenScadRenderer'),)),
+        ('openscad', 'machinome.node.openscad.renderer.OpenScadRenderer'),)),
```

### 4.4 The workspace (task 4.4)

The root `pyproject.toml`'s four sources of Decision 5, so the table reads
build123d, cadquery, jscad, molejo, openscad, solid2, step, stl.

```
$ env -C <bench> /home/asa/.local/bin/uv lock
Resolved 187 packages in 506ms
Added machinome-node-jscad v0.8.1
Added machinome-node-openscad v0.8.1
Added machinome-node-solid2 v0.8.1
Added machinome-node-stl v0.8.1
$ grep -c '^\[\[package\]\]' <bench>/uv.lock
187
$ grep -n 'source = { editable = "packages/' <bench>/uv.lock
1810:source = { editable = "packages/machinome" }
1954:source = { editable = "packages/machinome-engine-brep" }
1971:source = { editable = "packages/machinome-engine-mesh" }
2000:source = { editable = "packages/machinome-node-build123d" }
2021:source = { editable = "packages/machinome-node-cadquery" }
2038:source = { editable = "packages/machinome-node-jscad" }
2049:source = { editable = "packages/machinome-node-molejo" }
2068:source = { editable = "packages/machinome-node-openscad" }
2083:source = { editable = "packages/machinome-node-solid2" }
2100:source = { editable = "packages/machinome-node-step" }
2121:source = { editable = "packages/machinome-node-stl" }
```

`diff` of the lock against the base's: 88 changed lines. The solid2 package's
entry lists `machinome`, `machinome-node-openscad` and `solidpython2`, the
two members `editable`.

```
$ env -C <bench> /home/asa/.local/bin/uv sync --python 3.12
Resolved 187 packages in 7ms
Prepared 5 packages in 1.38s
Uninstalled 1 package in 4ms
Installed 5 packages in 16ms
 ~ machinome==0.8.1
 + machinome-node-jscad==0.8.1
 + machinome-node-openscad==0.8.1
 + machinome-node-solid2==0.8.1
 + machinome-node-stl==0.8.1
$ uv pip list --python <bench>/.venv/bin/python | tail -n +3 | wc -l
178
```

Incremental on 1.2's venv; 178 in the venv, probe 1's "Installed 178
packages" for a fresh sync. The eleven `__editable__` files, one line each:

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

From `/tmp`, with the venv's Python:

```
__path__ ['<bench>/packages/machinome/machinome/node', '<bench>/packages/machinome-node-build123d/machinome/node', '<bench>/packages/machinome-node-cadquery/machinome/node', '<bench>/packages/machinome-node-jscad/machinome/node', '<bench>/packages/machinome-node-molejo/machinome/node', '<bench>/packages/machinome-node-openscad/machinome/node', '<bench>/packages/machinome-node-solid2/machinome/node', '<bench>/packages/machinome-node-step/machinome/node', '<bench>/packages/machinome-node-stl/machinome/node']
openscad <bench>/packages/machinome-node-openscad/machinome/node/openscad/__init__.py
solid2 <bench>/packages/machinome-node-solid2/machinome/node/solid2.py
jscad <bench>/packages/machinome-node-jscad/machinome/node/jscad.py
stl <bench>/packages/machinome-node-stl/machinome/node/stl.py
openscad.renderer <bench>/packages/machinome-node-openscad/machinome/node/openscad/renderer.py
renderer machinome.node.openscad.renderer
```

`git status --short --ignored` under the four new directories: the tracked
links, modules, manifests and READMEs, and, ignored, each directory's
`*.egg-info/` and its `__pycache__/`; no build leaving.

### 4.5 Group 2's modules and the family's (task 4.5)

```
$ env -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python -m pytest -q -rs -p no:cacheprovider tests/test_repository_layout.py tests/test_kernel_extras.py tests/test_core_kernel_free.py tests/test_core_names_no_scad.py tests/test_expression_type.py tests/test_scad_presentation.py tests/test_snapshot.py tests/test_openscad_dependency.py tests/test_markings.py tests/test_build_publication.py tests/test_browser_renderer.py tests/test_openscad_node.py tests/test_no_class_name_recognition.py tests/test_supported_node_types.py tests/test_docs_structure.py tests/test_release_records.py tests/test_node_root.py tests/test_scad_stl.py tests/test_stl_node.py tests/test_jscad_integration.py tests/test_manager_new.py tests/test_cli_lazy_imports.py
16 failed, 553 passed, 17 skipped, 8 warnings, 1492 subtests passed in 158.58s (0:02:38)
```

(`<scratch>/4.5-modules.txt`) The 16 are subtests, each one tasks.md names:

- `test_the_readme_links_every_package_and_states_the_licence` and
  `test_the_guide_installs_every_member_without_uv`, four new subtests each
  (group 7);
- `test_the_installation_page_names_the_extension_distributions`, four
  (group 7);
- `test_the_version_is_bumped_from_the_root`, four (group 5).

The 17 skips: 14 `test_browser_renderer.py` and one each of
`test_scad_presentation.py` and `test_cli_lazy_imports.py` (the viewer, which
the lock excludes), and `test_jscad_integration.py` (no `jscad` command).
`test_supported_node_types.py` whole is green here, `AbsentPackageTest`'s 31
door subtests, both still-import subtests and the snapshot refusal included,
with no edit to the node root's finder; so are the two scans of 2.5 with the
table as their one reach.

### 4.6 The blind spots on the moved tree (task 4.6)

Planted at the end of the moved `stl.py`, written with `printf '# %s%s\n' 's'
'cad'`:

```
$ ... pytest tests/test_core_names_no_scad.py
1 failed, 4 passed, 15 subtests passed in 0.54s
   1 machinome-node-stl/machinome/node/stl.py (247: '# scad')
modules: 1  occurrences: 1
```

The plant removed from a copy (`git diff` of `stl.py`: empty; still `R100`).
The split-words gate, unchanged, before the plant: `11 passed, 56 subtests
passed in 0.76s`. Planted at the end of the moved `jscad.py`, written with
`printf '# %s%s\n' 'fac' 'eted'`:

```
$ ... pytest tests/test_core_names_no_split_words.py
1 failed, 10 passed, 56 subtests passed in 0.73s
AssertionError: {'machinome/node/jscad.py': (1, [(84, '# faceted')])} != {}
```

The gate names the module by its path under the package directory,
`machinome/node/jscad.py`, as the design says. The plant removed (`git diff`
of `jscad.py`: empty; still `R100`).

## 5. One version for the set, and the lint

### 5.1 The version tables (task 5.1)

The root `.bumpversion.cfg` gains the eight tables of Decision 6 after the
molejo package's, in the order openscad, solid2, jscad, stl, no comment
(`git diff .bumpversion.cfg`: one hunk, `@@ -70,3 +70,35 @@`, 32 added lines).
The file equals the proposer's probe file
(`<C4-propose>/bump/.bumpversion.cfg`) but its bumped `current_version` line.

```
$ ... pytest tests/test_release_records.py
13 passed, 108 subtests passed in 0.17s
```

### 5.2 The bump on a copy (task 5.2)

The root's `.bumpversion.cfg` and the fourteen files it names copied under
`<scratch>/bump/`, made a git repository and committed, then:

```
$ env -C <scratch>/bump <bench>/.venv/bin/bump2version --no-commit --no-tag --new-version 0.9.0 patch
exit 0
$ git -C <scratch>/bump diff --shortstat
 15 files changed, 41 insertions(+), 41 deletions(-)
$ git -C <scratch>/bump diff -U0 | grep '^+[^+]' | sort | uniq -c
      5 +    "machinome-engine-brep~=0.9.0",
      1 +    "machinome-engine-mesh~=0.9.0",
      1 +    "machinome-node-build123d~=0.9.0",
      2 +    "machinome-node-cadquery~=0.9.0",
      1 +    "machinome-node-jscad~=0.9.0",
      1 +    "machinome-node-molejo~=0.9.0",
      2 +    "machinome-node-openscad~=0.9.0",
      1 +    "machinome-node-solid2~=0.9.0",
      1 +    "machinome-node-step~=0.9.0",
      1 +    "machinome-node-stl~=0.9.0",
     10 +    "machinome~=0.9.0",
      1 +__version__ = "0.9.0"
      1 +current_version = 0.9.0
      1 +release = '0.9.0'
     12 +version = "0.9.0"
```

41 lines in 15 files, 26 of them pins (`~=0.9.0`); the twelve `version` lines
are the eleven manifests' and `machinome/vet/universe.toml`'s. No viewer floor
(`machinome-viewer>=0.8.1`) moves. Nothing written in the bench
(`<scratch>/5.2-bump-diff.txt`).

### 5.3 The lint (task 5.3)

`packages/machinome/setup.cfg`'s two ignores, in place:

```
-    machinome/node/openscad/__init__.py:E402
-    machinome/node/solid2.py:E402
+    ../machinome-node-openscad/machinome/node/openscad/__init__.py:E402
+    ../machinome-node-solid2/machinome/node/solid2.py:E402
```

The first run counted 761: the two `patch` strings of task 2.6 in
`tests/test_browser_renderer.py:332` and `tests/test_snapshot.py:1269` had
grown past 89 characters (E501). Each string was split in two adjacent
literals, the same string, and then:

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/flake8 --max-line-length=89 machinome tests ../machinome-engine-brep/machinome ../machinome-engine-mesh/machinome ../machinome-node-build123d/machinome ../machinome-node-cadquery/machinome ../machinome-node-jscad/machinome ../machinome-node-molejo/machinome ../machinome-node-openscad/machinome ../machinome-node-solid2/machinome ../machinome-node-step/machinome ../machinome-node-stl/machinome | wc -l
759
```

2 E402, both in `tests/test_couplings.py`, as at the base. Read with each
moved file's new prefix mapped to its old path and sorted, the list equals
1.3's but for two line numbers: `machinome/node/openscad/__init__.py:88` is
now `:91` (the three docstring lines of 3.3), and
`tests/test_browser_renderer.py:371` F401 is now `:372` (the split string).
The one line under the four new packages is that E501 of the OpenSCAD
package's `__init__.py`, as at the base (`<scratch>/5.3-lint.txt`).

## 6. `scripts/check-dist`

### 6.1 Red first (task 6.1)

```
$ env -C <bench> <bench>/.venv/bin/python scripts/check-dist
check-dist failed: machinome-node-jscad has no smoke in scripts/check-dist
Nothing uploaded.
exit 1
```

### 6.2 The template and the four rows (task 6.2)

`MESH_NODE`, `MESH_NODE_LINE` and `mesh_node_smoke` after `node_smoke`, and the
four rows after the molejo row, each extracted verbatim from design.md
Decision 10's two blocks and inserted by exact-match anchors.

```
$ git -C <bench> diff --stat scripts/check-dist
 scripts/check-dist | 196 +++++++++++++++++++++++++++++++++++++++++++++++++++++
$ git -C <bench> diff scripts/check-dist | grep -c '^-[^-]'
0
$ git -C <bench> diff scripts/check-dist | grep '^@@'
@@ -142,6 +142,78 @@ def node_smoke(name, node, parts, operation):
@@ -297,6 +369,130 @@ assert engine.solid_count(solid) == 1, engine.solid_count(solid)
$ flake8 --max-line-length=89 scripts/check-dist | wc -l
0
```

No line of the earlier rows changed.

### 6.3 The run (task 6.3)

```
$ env -C <bench> PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python scripts/check-dist
Members: machinome, machinome-engine-brep, machinome-engine-mesh, machinome-node-build123d, machinome-node-cadquery, machinome-node-jscad, machinome-node-molejo, machinome-node-openscad, machinome-node-solid2, machinome-node-step, machinome-node-stl
...
exit 0
```

(`<scratch>/6.3-check-dist.txt`; `openscad` on the PATH at `/usr/bin/openscad`.)

- Eleven members built; `twine check --strict`: 22 `PASSED`.
- Each member's linked files in its sdist as regular files equal to the
  root's: `LICENSE` 793 bytes, `LICENSES/CERN-OHL-S-2.0.txt` 13419,
  `LICENSES/GPL-2.0-or-later.txt` 17984 for every member, and the core's
  `AI-USE.md`, `CONTRIBUTING.rst` and `HISTORY.rst` besides.
- Archive entries: `machinome-0.8.1.tar.gz` 1012 and its wheel 114 (from the
  working tree, which holds untracked and ignored files the clean copy of
  8.5 does not); `machinome_node_openscad` 23 and 12; `machinome_node_solid2`,
  `_jscad` and `_stl` 18 and 8 each; the six earlier siblings 18 and 8 each.
- The install: the core's wheel with `[openscad,stl]`, then
  `machinome[brep]`, `machinome[mesh]`, `machinome[build123d]`,
  `machinome[cadquery]`, `machinome[jscad]`, `machinome[molejo]`,
  `machinome[openscad]`, `machinome[solid2]`, `machinome[step]`,
  `machinome[stl]`, with eleven `--find-links`.
- The smoke lines, `<tmp>` the script's temporary directory:

```
machinome 0.8.1 from <tmp>/venv/lib/python3.12/site-packages/machinome/__init__.py
machinome-engine-brep 0.8.1 provider <tmp>/venv/lib/python3.12/site-packages/machinome/engine/brep.py contract 2 result 999.9999999999998
machinome-engine-mesh 0.8.1 provider <tmp>/venv/lib/python3.12/site-packages/machinome/engine/mesh.py contract 1 result 24.0
machinome-node-build123d 0.8.1 module <tmp>/venv/lib/python3.12/site-packages/machinome/node/build123d.py volume 23.999999999999996
machinome-node-cadquery 0.8.1 module <tmp>/venv/lib/python3.12/site-packages/machinome/node/cadquery.py volume 999.9999999999998
machinome-node-jscad 0.8.1 module <tmp>/venv/lib/python3.12/site-packages/machinome/node/jscad.py part over part.js; its STL is rendered by the jscad command, which no package of the set installs
machinome-node-molejo 0.8.1 module <tmp>/venv/lib/python3.12/site-packages/machinome/node/molejo.py volume 477.8904448221108
machinome-node-openscad 0.8.1 module <tmp>/venv/lib/python3.12/site-packages/machinome/node/openscad/__init__.py volume 24.0 through OpenSCAD, renderer <tmp>/venv/lib/python3.12/site-packages/machinome/node/openscad/renderer.py
machinome-node-solid2 0.8.1 module <tmp>/venv/lib/python3.12/site-packages/machinome/node/solid2.py volume 24.0 through OpenSCAD
machinome-node-step 0.8.1 module <tmp>/venv/lib/python3.12/site-packages/machinome/node/step.py volume 120.0
machinome-node-stl 0.8.1 module <tmp>/venv/lib/python3.12/site-packages/machinome/node/stl.py volume 24.0
```

- `License-Expression: GPL-2.0-or-later OR CERN-OHL-S-2.0+` printed eleven
  times, each with the three licence files; `machinome --help: exit 0`.
- Last line: `Every distribution built, checked, installed and smoked; nothing
  uploaded.`

`git status --short --ignored` afterwards: nothing new but ignored leavings
(each member's `*.egg-info/` and `__pycache__/`).

### 6.4 With no `openscad` on the PATH (task 6.4)

The PATH made: `<scratch>/nobin/`, holding the links `python3 ->
/usr/bin/python3` and `git -> /usr/bin/git`, then `<bench>/.venv/bin`; `command
-v openscad` under it finds nothing. The script needs nothing else on the PATH
(it runs `build`, `twine`, `venv` and `pip` through `sys.executable` and the
throwaway venv's Python).

```
$ env -C <bench> PATH=<scratch>/nobin:<bench>/.venv/bin <bench>/.venv/bin/python scripts/check-dist
...
machinome-node-jscad 0.8.1 module <tmp>/venv/lib/python3.12/site-packages/machinome/node/jscad.py part over part.js; its STL is rendered by the jscad command, which no package of the set installs
machinome-node-openscad 0.8.1 module <tmp>/venv/lib/python3.12/site-packages/machinome/node/openscad/__init__.py SCAD 'part();' written, no openscad on the PATH, renderer <tmp>/venv/lib/python3.12/site-packages/machinome/node/openscad/renderer.py
machinome-node-solid2 0.8.1 module <tmp>/venv/lib/python3.12/site-packages/machinome/node/solid2.py SCAD 'cube(size = [2, 3, 4]);' written, no openscad on the PATH
machinome-node-stl 0.8.1 module <tmp>/venv/lib/python3.12/site-packages/machinome/node/stl.py volume 24.0
Every distribution built, checked, installed and smoked; nothing uploaded.
exit 0
```

22 `PASSED` (`<scratch>/6.4-check-dist-noscad.txt`). The core's archives were
built before the records of group 7 were edited.

## 7. The records

### 7.1 `HISTORY.rst` (task 7.1)

The `Unreleased` bullet of Decision 11, extracted verbatim from design.md,
after the third cycle's entry (`git diff --stat`: 15 insertions).

### 7.2 The manual's changelog (task 7.2)

`docs/project/changelog.rst`: the bullet of Decision 11, verbatim, after the
B-rep node types' (7 insertions).

### 7.3 The installation and backends pages (task 7.3)

`docs/start/install.rst`: the four rows' third cells, the paragraph's first
sentence, the requirements sentence ("Its node types, the CAD kernels,
SolidPython and the engines are extras"), the install section's sentence and
example (`"machinome[stl,mesh]"`), and the first sentence of "Packages and
licences", each as Decision 11 states, rewrapped at the page's width; the
paragraph's next sentence rewrapped with it (`their meshes, by the mesh
engine, so / a project that tests them installs ``machinome[mesh]``.`), its
words unchanged. `docs/howto/backends.rst`: the two cells. (`git diff --stat`:
install.rst 43 lines, backends.rst 5.)

### 7.4 The root `README.md` (task 7.4)

The four rows of Decision 11, verbatim, after the molejo package's.

### 7.5 `CONTRIBUTING.rst` (task 7.5)

The pip block of Decision 11, in place (two lines added).

### 7.6 `docs/architecture.md` (task 7.6)

The extras sentence, the family paragraph's sentences, the Map's OpenSCAD row,
the new JSCAD and STL row after it, the Node model row ("every node type in
its own distribution, rows below") and the viewer row (`viewers/openscad.py`
dropped), each as Decision 11 states. `grep "viewers/openscad\|install
nothing"` of the page: nothing.

### 7.7 The ADR amendments (task 7.7)

- ADR-179: the section "Amendment (2026-10-10)" after the 2026-10-05 one (the
  renderer's module `machinome.node.openscad.renderer` shipped by
  `machinome-node-openscad`; the row names it; `renderer(name)` loads the node
  type first; the core imports no node package; the column stays provisional,
  the viewer cycle now moving the renderer from the OpenSCAD node package);
  its status line adds "the renderer's module moved 2026-10-10 (amendment
  below)". The section links the change's archive path
  `openspec/changes/archive/2026-10-10-cut-the-mesh-nodes/`, which exists
  once task 9.2 archives it.
- ADR-183: the consequence "Neutral (2026-10-10, `cut-the-mesh-nodes`)" of
  Decision 11, after the two Neutral consequences.
- ADR-177: its status line notes "the snapshot renderer's module moved by
  ADR-179's amendment of 2026-10-10", linked.
- `docs/adrs/README.md`: ADR-179's index line gains "renderer's module amended
  2026-10-10", ADR-181's "the `jscad` and `stl` extras install their packages
  since `cut-the-mesh-nodes`", ADR-183's "the node packages over no B-rep
  engine third (`cut-the-mesh-nodes`)".

No new ADR file.

### 7.8 The gate, the docs and the release tests (task 7.8)

```
$ ... pytest tests/test_repository_layout.py tests/test_docs_structure.py tests/test_docs_exports.py tests/test_release_records.py tests/test_profile_documentation.py tests/test_kernel_extras.py tests/test_node_root_exports_nothing.py
120 passed, 1251 subtests passed in 7.16s
```

(`<scratch>/7.8-records.txt`) The layout gate's README, guide and link tests,
the installation page's distributions test and the release records green.

## 8. Validation

### 8.1 The manual (task 8.1)

A fresh venv `<scratch>/docvenv` (`/usr/bin/python3.12 -m venv`), with
`packages/machinome/docs/requirements.txt` alone installed (`sphinx`,
`sphinx_rtd_theme`, `machinome-viewer`; exit 0), then:

```
$ env -C <bench>/packages/machinome <scratch>/docvenv/bin/python -m sphinx -b html -W --keep-going docs <scratch>/html
build succeeded.
exit 0
```

0 warnings (`<scratch>/8.1-sphinx.txt`). `reference/api.html` holds the
anchors `machinome.node.openscad.OpenScadNode`, `machinome.node.solid2.Solid2Node`,
`machinome.node.jscad.JScadNode` and `machinome.node.stl.StlNode` (the class
names occur 11, 6, 5 and 13 times). `docs/conf.py` unedited.

### 8.2 The pixels (task 8.2)

```
$ env -C <scratch>/pixels PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/machinome new demo
Created new machinome project at demo/
exit 0
$ env -C <scratch>/pixels/demo -u DISPLAY PATH=<bench>/.venv/bin:$PATH machinome snapshot -o <scratch>/demo-snapshot.png
 INFO -       node.base - <scratch>/pixels/demo/_build/demo/demo-Demo-8a2cc0673b1c.scad generated with 1791659688.8602164!
 INFO - viewers.openscad - Rendering <scratch>/pixels/demo/_build/demo/demo-Demo-8a2cc0673b1c.scad to <scratch>/demo-snapshot.png
Snapshot saved to <scratch>/demo-snapshot.png
exit 0
```

`DISPLAY` was empty, so the renderer wrapped OpenSCAD (`/usr/bin/openscad`)
in `xvfb-run -a`. The starter is the `Solid2Node` of the template: a 50 mm
cube translated by (-25, -25, 0), less a cylinder of radius 10 mm and height
100 mm. The log line comes from the logger `viewers.openscad`, its name
unchanged. `<scratch>/demo-snapshot.png`: 21440 bytes, 1920 x 1080 (read
from its header), the size probe 1 recorded. Looked at: a yellow cube in
perspective on the cream Cornfield background, its top face lit brightest
and its two visible side faces in two darker shades of ochre, with a round
bore centred on the top face whose inner wall shows in faceted green bands,
dark at the middle and lighter toward the edges; nothing else in the frame.

With the OpenSCAD package's directory dropped from `sys.path` by a wrapper
calling `machinome.cli.manage()` (`<scratch>/cli_absent.py`), in the same
project:

```
$ env -C <scratch>/pixels/demo -u DISPLAY PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python <scratch>/cli_absent.py <bench>/packages/machinome-node-openscad snapshot -o <scratch>/refused.png
Error: machinome snapshot --renderer openscad needs the openscad extra: the openscad node type (OpenScadNode) needs machinome.node.openscad, which is not installed; install it with 'pip install "machinome[openscad]"'; or use --renderer web
exit 1
```

No `<scratch>/refused.png`. The doors with the same package dropped
(`<scratch>/doors_absent.py`, `<scratch>/8.2-doors.txt`): `import
machinome.node.openscad`, `from machinome.node.openscad import OpenScadNode`,
`import machinome.node.openscad.writer`, `import
machinome.node.openscad.renderer`, `from machinome.node import openscad`,
`hasattr(machinome.node, 'openscad')`, `supported.load('openscad')`,
`supported.renderer('openscad')`, `from machinome.node.solid2 import
Solid2Node` and `supported.load('solid2')` each raise `ExtraUnavailable` with
`name` `machinome.node.openscad`, `extra` `openscad` and the message `the
openscad node type (OpenScadNode) needs machinome.node.openscad, which is not
installed; install it with 'pip install "machinome[openscad]"'`; `import
machinome.node.stl` passes.

### 8.3 The whole suite (task 8.3)

```
$ env -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python -m pytest -q -rs -p no:cacheprovider
4796 passed, 20 skipped, 55 warnings, 7029 subtests passed in 628.53s (0:10:28)
exit 0
```

(`<scratch>/8.3-suite.txt`) No failure. The 20 skips, the base's: 14
`test_browser_renderer.py`, one each of `test_cli_lazy_imports.py` and
`test_scad_presentation.py` (the viewer, which the lock excludes: 16), one
`test_connectivity.py` (networkx), one `test_jscad_integration.py` (no `jscad`
command), two `test_step_assembly.py` (the vendor STEP not present).

Passed: the base's 4791 plus 5 new tests, `test_the_core_node_package_holds_no_node_type`
and `test_the_core_viewers_hold_no_node_type_s_renderer`
(`test_repository_layout.py`), `test_solidpython_carries_one_range_wherever_it_is_named`
(`test_kernel_extras.py`), `test_the_core_imports_no_node_type_and_no_engine_provider`
(`test_core_kernel_free.py`) and `test_the_snapshot_refuses_an_absent_openscad_package`
(`test_supported_node_types.py`). Renamed, count unchanged:
`test_the_solid2_extra_installs_the_openscad_extra` to
`test_the_solid2_package_requires_the_openscad_package`;
`test_only_the_viewer_reaches_the_family_package` and
`..._familys_package` to `test_only_the_table_reaches_...` (departure 3);
`test_the_viewer_imports_neither_former_address` to
`test_the_renderer_imports_neither_former_address`;
`test_the_viewer_refuses_with_the_package` to
`test_the_renderer_refuses_with_the_package`. None removed. Subtests: 6914 to
7029 (the new rows of the layout, extras, census and absent-package tables).

### 8.4 The lint on the final tree (task 8.4)

The command of 5.3: 759 lines, 2 E402 (`tests/test_couplings.py`), the list
identical to 5.3's (`diff`: no output; `<scratch>/8.4-lint.txt`). `flake8
--max-line-length=89 scripts/check-dist`: 0.

### 8.5 `check-dist` on the final tree and on a clean copy (task 8.5)

On the bench, as in 6.3 (`<scratch>/8.5-check-dist.txt`): exit 0, eleven
members, 22 `PASSED`, every smoke line as in 6.3, the last line `Every
distribution built, checked, installed and smoked; nothing uploaded.` The
core's sdist holds 1062 entries here: the working tree's ignored files the
suite of 8.3 left (`tests/step_project/*.step`, `tests/stl_project/*.stl`,
`tests/_build_meta/` and the like) are packed by `MANIFEST.in`'s globs.

On a clean copy of the tracked tree (`git -C <bench> ls-files -z | tar -C
<bench> --null -T - -cf - | tar -C <scratch>/clean -xf -`, 25 links kept),
`env -C <scratch>/clean PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python
scripts/check-dist`: exit 0, 22 `PASSED`, the same smoke lines, nothing
uploaded (`<scratch>/8.5-check-dist-clean.txt`). Entries:

```
machinome-0.8.1.tar.gz: 1006 entries
machinome-0.8.1-py3-none-any.whl: 114 entries
machinome_engine_brep, _engine_mesh, _node_build123d, _node_cadquery, _node_molejo, _node_step: 18 and 8 each
machinome_node_jscad, _node_solid2, _node_stl: 18 and 8 each
machinome_node_openscad-0.8.1.tar.gz: 23 entries
machinome_node_openscad-0.8.1-py3-none-any.whl: 12 entries
```

The clean core's 1006 and 114 are design.md probe 3's. Built again from the
clean copy into `<scratch>/clean-sdist/`, neither the core's sdist nor its
wheel lists a file under `machinome/node/openscad/`, `machinome/node/solid2.py`,
`jscad.py` or `stl.py`; their `machinome/viewers/` hold `__init__.py`,
`browser.py` and `bundle.py` alone.

### 8.6 The universe sweep (task 8.6)

```
$ /home/asa/devel/machinome/.venv/bin/python /home/asa/devel/machinome/scripts/load-projects \
    --bench <bench>/packages/machinome --python <bench>/.venv/bin/python \
    --moved /home/asa/devel/machinome/scripts/load-projects.d/*.toml \
    --timeout 300 --json <scratch>/load-projects.json
63 repositories, 130 rows: 121 ok, 0 expected, 3 unexpected, 0 timeout, 6 no-model; 2 skipped
Skipped: .Trash-1000 (skip rule), sandbox (skip rule)
exit 1
```

(`<scratch>/8.6-sweep.txt`, `<scratch>/load-projects.json`; exit 1 because
unexpected rows exist, as at the base.) The counts are 1.4's. Read row by row
against the third cycle's `<C3-apply>/load-projects.json`: the same 130 keys
(project, model, checkout), no row's outcome or stage differs, and no row's
explanation differs. The three unexpected rows are the base's:
fender-bender (`ModuleNotFoundError: No module named 'fb_library'`),
wall_clock_41 (its own CadQuery error, `Workplane object must have at least
one solid`) and Dum-E (`No module named 'machinome_freecad'`).

### 8.7 Git (task 8.7)

`git -C <bench> status --short` (`<scratch>/8.7-status.txt`): eight renames
(`R`), the renderer's from `packages/machinome/machinome/viewers/openscad.py`
to `packages/machinome-node-openscad/machinome/node/openscad/renderer.py`;
the four new directories' four files each added (`A`: `LICENSE`,
`LICENSES`, `README.md`, `pyproject.toml`; `git ls-files -s` of the four: 8
entries of mode 120000, 16 of 100644); the edited files (` M`): the root's
`.bumpversion.cfg`, `CONTRIBUTING.rst`, `HISTORY.rst`, `README.md`,
`pyproject.toml`, `uv.lock` and `scripts/check-dist`; the framework's
`pyproject.toml`, `setup.cfg`, `machinome/node/supported.py`, the four ADR
files, `architecture.md`, `howto/backends.rst`, `project/changelog.rst`,
`start/install.rst`, this change's `tasks.md` and fourteen test modules; and
`?? .../cut-the-mesh-nodes/evidence.md`. Nothing else.

```
$ git -C <bench> ls-files -ci --exclude-standard | wc -l
34
```

A leaving, pre-existing and not this cycle's: after the whole suite of 8.3,
`packages/machinome/_build.lock` (0 bytes) exists. It is excluded by the
repository's `.git/info/exclude` (`_build*`, shared by every worktree), so
`git status --short` does not list it. The orchestrator saw the same
zero-byte `_build.lock` at the root of the primary checkout at 0.8.1, before
the campaign, and at the root of the line worktree after the baseline suite
run of 10 October 2026, before any cut. Nine modules run one at a time here
did not recreate it; its source is not hunted, and the file is left in place.

### 8.8 OpenSpec (task 8.8)

```
$ env -C <bench>/packages/machinome openspec validate cut-the-mesh-nodes --strict
Change 'cut-the-mesh-nodes' is valid
```

## Departures from the design

1. `test_solidpython_carries_one_range_wherever_it_is_named` (2.2) also
   requires the places naming SolidPython to be the two family packages, so
   it is red at the base for the reason tasks.md states ("named once, in the
   core"); a range-only test, as CadQuery's, would be green at the base.
2. The seams test's `machinome/node/supported.py` subtest (2.3) is red until
   the renderer row's edit of task 4.3, an added red tasks.md does not list.
3. `BINARY_REACHES` and `ENGINE_REACHES` hold `machinome/node/supported.py`
   rather than nothing, and the two tests are named
   `test_only_the_table_reaches_the_family_package` and
   `test_only_the_table_reaches_the_familys_package` (2.5): the table's row
   names the renderer's module as a string under the family's package, which
   both scans count; the proposer's probe 6 log shows it.
4. The OpenSCAD package's `binary` docstring bullet ends with a semicolon
   rather than a full stop, so the list with the new renderer bullet reads
   as the others do (3.3).
5. Two `patch` strings of task 2.6 were split across two literals to keep
   their lines within 89 characters (5.3).

## The orchestrator's review of the checkpoint (10 October 2026)

The checkpoint after task 8.9 was accepted, departure 3 included: the table
of supported node types is the one core module naming the renderer by
string, so the reach scans naming `machinome/node/supported.py` and the names
`test_only_the_table_reaches_...` are right, as Decision 9's `SEAMS` entry
already said. Two corrections were asked before group 9 and made:

- design.md Decision 9, the paragraph on `BINARY_REACHES` and
  `ENGINE_REACHES`, gained the dated sentence "Corrected at apply on 10
  October 2026: the sets are `{'machinome/node/supported.py'}`, the table
  naming the renderer's module by string, and the tests are named
  `test_only_the_table_reaches_the_family_package` and
  `test_only_the_table_reaches_the_familys_package`; the design's 'empty'
  misread the proposer's own log." Nothing else in the design changed.
- The `_build.lock` leaving of 8.7 is recorded there as pre-existing, from
  the orchestrator's observation; its source is not hunted.

## 9. Records closing

### 9.1 The ADR amendments (task 9.1)

Re-read against the implementation: ADR-179's amendment (the module
`machinome.node.openscad.renderer`, its logger `viewers.openscad` as in
`renderer.py` line 27, `renderer(name)` loading the node type first, the
column provisional) and its status line; ADR-183's dated Neutral consequence;
ADR-177's status line; the index lines of ADR-179, ADR-181 and ADR-183 in
`docs/adrs/README.md`. `docs/architecture.md` agrees with them: the family
paragraph names the renderer's module and the provisional column, the Map's
OpenSCAD row cites 179 and 183, the viewer row no longer names
`viewers/openscad.py`.

### 9.2 The archive (task 9.2)

```
$ env -C <bench>/packages/machinome openspec archive cut-the-mesh-nodes -y
Task status: 48/51 tasks
Warning: 3 incomplete task(s) found. Continuing due to --yes flag.
Applying changes to openspec/specs/cli/spec.md:  ~ 1 modified
Applying changes to openspec/specs/framework-contributor-guidance/spec.md:  ~ 1 modified
Applying changes to openspec/specs/framework-identity/spec.md:  ~ 1 modified
Applying changes to openspec/specs/kernel-extras/spec.md:  ~ 3 modified
Applying changes to openspec/specs/node-model/spec.md:  ~ 1 modified
Applying changes to openspec/specs/openscad-node/spec.md:  ~ 3 modified
Totals: + 0, ~ 10, - 0, → 0
Change 'cut-the-mesh-nodes' archived as '2026-10-10-cut-the-mesh-nodes'.
exit 0
$ env -C <bench>/packages/machinome openspec validate --specs --strict
Totals: 45 passed, 0 failed (45 items)
exit 0
```

The plain command archived; the three incomplete tasks were 9.2 to 9.4,
ticked afterwards in the archived `tasks.md`. `git diff --stat` of
`openspec/specs/`: 6 files, 289 insertions, 112 deletions.

### 9.3 The plan note (task 9.3)

The root's `workflow/ongoing/monorepo-0.9.md`: cycle 4 marked done in the
shape of cycles 1 to 3 (branch, planning commit bc2eff29 on 10e07f8c, ADR-179
and ADR-183 amended, the suite count, the manual, the pixels, the
`check-dist` result with the clean copy's counts, the lock's 187 packages and
the sweep's counts with its three unexpected rows), and one sentence after
the four cycles: all four are done on 10 October 2026, and the close is the
orchestrator's.

### 9.4 After the archive (task 9.4)

```
$ env -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_repository_layout.py tests/test_supported_node_types.py tests/test_kernel_extras.py tests/test_core_kernel_free.py tests/test_core_names_no_scad.py tests/test_docs_structure.py
94 passed, 1128 subtests passed in 12.92s
$ git -C <bench> status --short | wc -l
74
```

(`<scratch>/9.4-gates.txt`) The 74: the 8 renames, 16 added files of the
four packages, 39 modified files (the 33 of 8.7 less this change's
`tasks.md`, plus the root's `workflow/ongoing/monorepo-0.9.md` and the six
synced specs), the 10 deleted files of the active change
directory, and the untracked archive directory. Nothing committed; the
implementation commit is the orchestrator's, never amending the planning
commit; nothing pushed.
