# Evidence: `join-mechanics`

The second cycle of the joins campaign of Machinome 0.9
(`workflow/ongoing/joins-0.9.md` at the repository root, cycle 2). Worktree
`machinome/WTs/v0.9-joins-join-mechanics`, branch
`v0.9-joins-join-mechanics`, cut from the line `v0.9-joins` and
fast-forwarded to d5d194ad. Planning commit db007dd0, ratified by the
orchestrator on 12 October 2026; join merge commit 076b566d, made by the
orchestrator. Applied on 12 October 2026.

Tools: uv 0.11.8, CPython 3.12.3 (the bench venv), the OpenSpec CLI 1.6.0,
OpenSCAD 2021.01 at `/usr/bin/openscad`. Every command ran with `env -C
<dir>` and absolute paths; `<bench>` is
`/home/asa/devel/machinome/machinome/WTs/v0.9-joins-join-mechanics` and
`<scratch>` is
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C2-apply/`.
The core's tests ran from `<bench>/packages/machinome` on the bench venv
(`<bench>/.venv/bin/python -m pytest -q -p no:cacheprovider ...`); the
package's from `<bench>/packages/machinome-mechanics`; one pytest process at a
time. Logs are in `<scratch>`, never in the bench.

## 1. Evidence baseline

### 1.1 The base (task 1.1)

```
$ git -C <bench> log --oneline -4
076b566d Join machinome-mechanics: its whole history at its final paths
db007dd0 Propose join-mechanics: machinome-mechanics joins as the distribution machinome-mechanics, imported as machinome.mechanics
d5d194ad workflow: the digest note belongs under Progress
ce47cac0 workflow: the digest integration between cycles 1 and 2 of the joins
$ git -C <bench> status --short | wc -l
0
$ git -C <bench> ls-files | wc -l
3678
$ git -C <bench> ls-files -ci --exclude-standard | wc -l
34
```

`git status --short --ignored` showed `!! .env`, `!! .venv/` and the twelve
packages' build leavings (`__pycache__/`, `*.egg-info/`).

### 1.2 The bench venv and the base's counts (task 1.2)

The orchestrator synced the venv from the lock before the join. Twelve
`__editable__` files, each holding its package directory:
`__editable__.machinome-0.8.1.pth` and those of `machinome_engine_brep`,
`machinome_engine_mesh`, `machinome_node_build123d`,
`machinome_node_cadquery`, `machinome_node_freecad`, `machinome_node_jscad`,
`machinome_node_molejo`, `machinome_node_openscad`, `machinome_node_solid2`,
`machinome_node_step` and `machinome_node_stl`, all 0.8.1.
`machinome-mechanics` 0.1.0 from PyPI is installed through the dev group:
`importlib.metadata.version('machinome-mechanics')` is `0.1.0` and
`machinome_mechanics.__file__` is
`<bench>/.venv/lib/python3.12/site-packages/machinome_mechanics/__init__.py`,
beside `machinome_mechanics-0.1.0.dist-info`.

The base's counts, named by the orchestrator for d5d194ad and not rerun:
suite 4827 passed, 24 skipped at the digest integration; the lint, the sweep
of `join-freecad` (63 repositories, 130 rows, 122 ok, 0 expected, 2
unexpected, 0 timeout, 6 no-model) and the clean copy's framework sdist and
wheel as `join-freecad` recorded them.

### 1.3 The probes this cycle relies on (task 1.3, by reference)

design.md, Probes: probe 1 (the product as it is: `main` 34 failed and 2
errors, the branch 38 failed and 2 errors); probe 2 (the branch 201 passed
with fourteen lines moved); probe 3 (195 passed on published Machinome
0.8.0); probe 4 (the rehearsed import: 157 files, 45 commits, 4d3e075, the tag
`mechanics-v0.1.0`); probe 6 (the reds of the join); probe 7 (198 passed, 3
failed at the new place; the core collects none of them); probe 9 (the folded
manual: exit 1 at the join, 141 examples green after the edits); probe 10
(188 packages resolved; uv does not check the floors); probe 11 (pip chooses
the published wheel for `machinome-mechanics>=0.1.0`); probe 14 (the deltas
archive in scratch).

## 2. The join

### 2.1 and 2.2 The import and the merge (the orchestrator's, as measured)

- A fresh clone of `file:///home/asa/devel/machinome/machinome-mechanics`
  rewritten with the command of design.md Decision 2, whose text is
  `scratchpad/C2-propose/filter-repo-command.sh` (its log
  `scratchpad/C2-join/filter-repo.log`: "Parsed 46 commits");
  `v0.8-symbolic-assertions` at 4d3e075, the rehearsal's hash, 45 commits;
  `git ls-tree -r --name-only` listed the 157 paths of
  `scratchpad/C2-propose/rehearsal-ls-files.txt` exactly (diff empty; the
  list is `scratchpad/C2-join/ls-files.txt`); no path outside `packages/`
  (0); the tag `mechanics-v0.1.0` present.
- The branch and the tag fetched into the bench; the merge commit 076b566d
  (parents db007dd0 and 4d3e0758), `git merge --allow-unrelated-histories
  --no-ff` of that branch onto db007dd0, no conflict; `git status
  --porcelain` empty afterwards.

The applier re-read the facts on the bench:

```
$ git -C <bench> ls-tree -r --name-only db007dd0 | wc -l
3521
$ git -C <bench> ls-tree -r --name-only 076b566d | wc -l
3678
$ git -C <bench> diff --shortstat db007dd0 076b566d
 157 files changed, 10075 insertions(+)
$ git -C <bench> tag | grep mechanics
mechanics-v0.1.0
$ git -C <bench> log --follow --format='%h %ad %s' --date=short -- \
    packages/machinome-mechanics/machinome/mechanics/belts.py | tail -1
f8c2cefd 2026-09-20 Add pulley pitch radius with seven validated consumers
$ git -C <bench> log --format='%h %ad' --date=short -- \
    packages/machinome-mechanics/machinome/mechanics/gears.py | tail -2
8baf5658 2026-09-19
b3f5a127 2026-09-11
```

b3f5a127 is the founding commit of 11 September 2026, reached without
`--follow` through the rename of `solid_node_mechanics/`, as probe 4 found.

### 2.3 The gates red on the joined tree (task 2.3)

```
$ ... pytest tests/test_repository_layout.py tests/test_release_records.py \
    tests/test_core_names_no_scad.py tests/test_node_root_exports_nothing.py
10 failed, 67 passed, 434 subtests passed in 5.89s
```

(`<scratch>/2.3-red.txt`.) Exactly the reds of design.md probe 6, each with
its reason:

- `test_every_member_is_a_workspace_source`: the root manifest's sources
  lack `machinome-mechanics`.
- `test_the_readme_links_every_package_and_states_the_licence`
  (`machinome-mechanics`): `'packages/machinome-mechanics/' not found` among
  the root README's links.
- `test_every_sibling_is_in_the_table`: `packages/machinome-mechanics is not
  in EXTENSIONS`.
- `test_the_guide_installs_every_member_without_uv`: `CONTRIBUTING.rst does
  not name -e packages/machinome-mechanics`.
- `test_every_member_is_numbered_with_the_core` (`machinome-mechanics`):
  `'0.1.0' != '0.8.1'`.
- `test_every_pin_between_members_is_compatible`, two subtests: the core's
  extra `machinome-mechanics` (`'' != '~=0.8.1'`) and the product's
  `machinome>=0.7.0` (`'>=0.7.0' != '~=0.8.1'`).
- `test_the_version_is_bumped_from_the_root`:
  `'packages/machinome-mechanics/pyproject.toml' not found` among
  `.bumpversion.cfg`'s files.
- `test_no_module_outside_the_allowed_zones_holds_the_word`: 2 modules, 3
  occurrences: `machinome-mechanics/machinome/mechanics/__init__.py` (2) and
  `linkages.py` (1), each in the module docstring.
- `test_no_file_of_the_three_zones_spells_a_former_root_name`: tests
  `machinome-mechanics/tests/test_declarative.py` line 10 and
  `test_motion.py` line 13, docs `howto/mechanism-formulas/gear_phase.py`
  line 1 and `slider_crank.py` line 2, each `from machinome.node import
  AssemblyNode`.

Nothing else was red.

## 3. Red first, on the joined tree

Nothing of the package changed in this group but its two rewritten pinning
tests (task 3.6).

### 3.1 `tests/test_mechanics_boundary.py` (task 3.1)

The extra expected as `["machinome-mechanics>=0.1.0"]`; the guard, now the
module constant `GUARD`, refuses a name equal to `machinome.mechanics` or
beginning `machinome.mechanics.` as well as the two former top-level names;
the new `test_the_guard_refuses_the_helpers_address`; the docstring names the
change.

To prove the control red, the same module was run once from a scratch copy
whose guard is the former one (`<scratch>/oldguard/`, `ROOT` pointed at the
bench's framework directory):

```
$ ... pytest <scratch>/oldguard/test_mechanics_boundary_oldguard.py
2 failed, 2 passed in 0.31s
$ ... pytest tests/test_mechanics_boundary.py
1 failed, 3 passed in 0.39s
```

(`<scratch>/3.1-red-oldguard.txt`, `<scratch>/3.1-red.txt`.) Red:

- `test_only_the_mechanics_extra_installs_helpers`: `['machinome-mechanics']
  != ['machinome-mechanics>=0.1.0']`, the bare extra.
- `test_the_guard_refuses_the_helpers_address`, under the former guard only:
  `'framework imported helpers: machinome.mechanics' not found in
  '...ModuleNotFoundError: No module named 'machinome.mechanics''`. The
  former guard reads the first component, `machinome`, and lets the import
  through; it then fails otherwise, exit 1, because no installed package
  provides the address yet. Under the new guard the control is green: the
  import is refused by name.

`test_math_and_motion_work_with_helpers_refused` stays green under the new
guard.

### 3.2 `tests/test_repository_layout.py` (task 3.2)

`PRODUCTS` (Decision 6's table); the class `TheProductsTest` with five tests
(`test_each_product_directory_holds_its_package_and_its_record`,
`test_each_product_manifest_states_the_set_s_licence`,
`test_each_product_readme_names_its_install_and_the_licence`,
`test_each_product_resolves_from_its_directory`, on the interpreter running
the suite, and `test_each_product_keeps_its_tests_and_specs`);
`test_every_sibling_is_in_the_table` reads both tables;
`TheIndexTest.test_context7_is_the_repository_s` admits a folder under a
product's directory; `test_the_test_job_runs_each_product_s_tests`; the
module's docstring names the products and the change.

```
$ ... pytest tests/test_repository_layout.py
8 failed, 35 passed, 187 subtests passed in 4.69s
```

(`<scratch>/3.2-red.txt`.) `test_every_sibling_is_in_the_table` turned green
with the table; red:

- `test_each_product_directory_holds_its_package_and_its_record`: the
  entries lack `LICENSE` and `LICENSES`. design.md Decision 6 expected
  "`LICENSE` a file, no `LICENSES`"; the import dropped the product's
  `LICENSE` (Decision 2), so neither is there.
- `test_each_product_manifest_states_the_set_s_licence`: the product's
  former licence expression in place of `GPL-2.0-or-later OR
  CERN-OHL-S-2.0+` (the first assertion that fails; its `license-files` and
  `include` differ too).
- `test_each_product_readme_names_its_install_and_the_licence`: `'pip install
  "machinome[mechanics]"' not found` in the product's README.
- `test_each_product_resolves_from_its_directory`: `ModuleNotFoundError: No
  module named 'machinome.mechanics'`; the PyPI 0.1.0 provides
  `machinome_mechanics` only.
- `test_the_test_job_runs_each_product_s_tests`: `the test job runs no pytest
  from packages/machinome-mechanics`.
- and 2.3's three others of the module (workspace source, root README,
  contributor guide).

`test_each_product_keeps_its_tests_and_specs` is green at the join.

### 3.3 `tests/test_release_records.py` (task 3.3)

`OWN_VERSION = ('machinome-mechanics',)` with its comment; the two skips; the
pin test holding a floor `>=` that the required member's version satisfies
for a requirement on or from a member of its own version;
`test_a_member_of_its_own_version_is_outside_the_bump`; the docstring.

```
$ ... pytest tests/test_release_records.py
1 failed, 14 passed, 128 subtests passed in 0.23s
```

(`<scratch>/3.3-red.txt`.) Red: `test_every_pin_between_members_is_compatible`
(member `machinome`, requirement `machinome-mechanics`): `[] != ['>=']`, the
core's bare requirement is no floor. The product's `machinome>=0.7.0` passes
as a floor (0.8.1 satisfies it). `test_every_member_is_numbered_with_the_core`
and `test_the_version_is_bumped_from_the_root` are green with the skip; the
new test is green at the join (the manifest, the changelog's first release
section `0.1.0` and `mechanics_version` agree on 0.1.0, and no
`.bumpversion.cfg` table names the manifest).

### 3.4 `tests/test_vet_universe.py` (task 3.4)

`test_the_contract` expects `('machinome', 'molejo')`; the new
`test_the_mechanics_helpers_are_inside_and_their_former_name_outside` writes
two scratch projects in a temporary directory (a manifest declaring
`sim.model:Machine`, `sim/__init__.py`, and `sim/model.py` importing
`AssemblyNode` from its module and the helper) and vets each.

```
$ ... pytest tests/test_vet_universe.py
2 failed, 13 passed, 7 subtests passed in 0.15s
```

(`<scratch>/3.4-red.txt`.) Red: `test_the_contract` (`('machinome',
'machinome_mechanics', 'molejo') != ('machinome', 'molejo')`); the new test
(the project importing `machinome_mechanics` vetted pure: `Items in the second
set but not the first: ('sim/model.py', 'outside-universe',
'machinome_mechanics')`). The project importing `machinome.mechanics` is pure
already, beneath `machinome`.

### 3.5 `tests/test_docs_structure.py` (task 3.5)

`NavigationTest.test_the_mechanics_helpers_are_a_reference_section_and_a_how_to`
(the two toctrees, the section's toctree `conventions` then the nine
families); `KernelExtrasTest.STALE` gains `'machinome' '_mechanics'` and
`'machinome-mechanics.readthedocs'`, `RECORDS` admitting the former module on
`project/changelog.rst` and `project/upgrading.rst`; the distributions' test
gains `machinome-mechanics`; `ReleaseFactsTest.test_the_mechanics_version_is_the_package_s`.

```
$ ... pytest tests/test_docs_structure.py
24 failed, 19 passed, 1142 subtests passed in 0.46s
```

(`<scratch>/3.5-red.txt`.) Red:

- the new navigation test, three: the How-to toctree lacks
  `howto/mechanism-formulas`, the Reference toctree lacks
  `reference/mechanics/index`, the section's toctree is the nine families
  without `conventions`.
- `test_no_reader_page_carries_the_kernels_or_the_old_addresses`, 21
  subtests: `machinome_mechanics` on `howto/mechanism-formulas.rst`,
  `reference/api.rst`, `reference/manuals.rst` and the eleven pages of
  `reference/mechanics/`; `machinome-mechanics.readthedocs` on
  `concepts/relations.rst`, `howto/timeline.rst`, `project/upgrading.rst`,
  `reference/api.rst`, `reference/manuals.rst`, `start/install.rst` and the
  framework's `README.rst`.

Green at the join, unlike task 3.5's expectation:
`test_the_installation_page_names_the_extension_distributions` for
`machinome-mechanics`, because the page's link to the separate manual,
`machinome-mechanics.readthedocs.io`, contains the name; after task 7.4 the
page names the distribution in words. `test_the_mechanics_version_is_the_package_s`
is green (0.1.0 both).

### 3.6 The package's pinning tests (task 3.6)

`tests/test_documentation.py` and `tests/test_machinome_identity.py`
rewritten as design.md Decision 11 says (the identity test gains
`test_the_package_resolves_from_its_directory`).

```
$ env -C <bench>/packages/machinome-mechanics \
    PYTHONPATH=<bench>/packages/machinome-mechanics \
    <bench>/.venv/bin/python -m pytest -q -p no:cacheprovider \
    tests/test_documentation.py tests/test_machinome_identity.py
5 failed, 4 passed in 0.23s
```

(`<scratch>/3.6-red.txt`.) Red:

- `test_the_changelog_states_the_release`: the README states a version
  (`0.1.0`, among "Version 0.1.0 was released on 23 September 2026 with
  Machinome 0.7.0").
- `test_the_pages_link_inside_the_manual`: `reference/mechanics/conventions.rst`
  names `readthedocs.io` (the framework manual's address).
- `test_every_example_in_the_manual_runs`: `mechanism-formulas.rst`, 10
  attempted, 10 failed; the first `from slider_crank import Engine` raises
  the node root's `ImportError` for `AssemblyNode`, the nine others follow
  from it.
- `test_distribution_dependency_and_import_package`: `['machinome>=0.7.0'] !=
  ['machinome>=0.8.0']`, the first of the manifest's assertions.
- `test_formulas_use_machinome_math`: `__init__.py` and `belts.py` import
  from `machinome_mechanics`.

Green at the join: `test_every_export_has_one_reference_with_the_actual_signature`,
`test_no_reader_page_states_a_publication_caveat`,
`test_the_reference_names_no_consumer_projects` and
`test_the_package_resolves_from_its_directory`. With `PYTHONPATH` naming the
package's directory, the core's path extension admits
`packages/machinome-mechanics/machinome/` and `machinome.mechanics` resolves
from the bench's tree before the sync; its `__init__.py` then imports its
families from the PyPI 0.1.0. A probe from `/tmp` with the same `PYTHONPATH`:

```
machinome.mechanics <bench>/packages/machinome-mechanics/machinome/mechanics/__init__.py
machinome_mechanics <bench>/.venv/lib/python3.12/site-packages/machinome_mechanics/__init__.py
gears via machinome_mechanics.gears <bench>/.venv/lib/python3.12/site-packages/machinome_mechanics/gears.py
```

So the reference pages' examples, still importing `machinome_mechanics`,
passed against the PyPI 0.1.0; only the how-to's failed.

## 4. The package

### 4.1 The links (task 4.1)

```
$ env -C <bench>/packages/machinome-mechanics ln -s ../../LICENSE LICENSE
$ env -C <bench>/packages/machinome-mechanics ln -s ../../LICENSES LICENSES
$ git -C <bench> add packages/machinome-mechanics/LICENSE packages/machinome-mechanics/LICENSES
$ git -C <bench> ls-files -s packages/machinome-mechanics | grep ^120000
120000 30cff7403da04711c46979a06f6bf8eb10ee088a 0	packages/machinome-mechanics/LICENSE
120000 06ad40db40b426ca6c609aa4663782c2b8d02e92 0	packages/machinome-mechanics/LICENSES
```

The two blobs read `../../LICENSE` and `../../LICENSES`.

### 4.2 The manifest, README, `MANIFEST.in` and `.gitignore` (task 4.2)

Written verbatim from design.md Decision 3, in place of the product's.

### 4.3 The headers (task 4.3)

Nineteen `# SPDX-License-Identifier:` lines, the ten modules and the nine test
modules that carried one, now `GPL-2.0-or-later OR CERN-OHL-S-2.0+`; the
seven test modules without a header gained none. `git diff` of the package
directory `machinome/mechanics/` shows ten such lines and the edits of 4.4,
nothing else of a header.

### 4.4 The source (task 4.4)

`__init__.py`: its nine `from machinome_mechanics.<family> import` lines
become `from machinome.mechanics.<family> import` (same length, no
continuation line moved), its first two docstring paragraphs and the sentence
of "**Two faces, from `machinome.math`.**" as Decision 4 gives them, rewrapped
at the docstring's width; `belts.py`: its one import line; `linkages.py`: the
sentence, which no longer fits one line and takes two.

```
$ ... pytest tests/test_core_names_no_scad.py
5 passed, 15 subtests passed in 0.69s
```

## 5. The core and the workspace

### 5.1 The extra (task 5.1)

`packages/machinome/pyproject.toml`: one hunk, the comment of Decision 6 and
`mechanics = ["machinome-mechanics>=0.1.0"]`.

### 5.2 The workspace, the lock and the sync (task 5.2)

The root `pyproject.toml` gains `machinome-mechanics = { workspace = true }`
after `machinome-engine-mesh`.

```
$ env -C <bench> /home/asa/.local/bin/uv lock
Resolved 188 packages in 617ms
```

The lock's diff (`<scratch>/5.2-lock.diff`, 40 lines unified, 19 in the
normal format of probe 10): the root's member list gains
`machinome-mechanics`; the core's `requires-dist` line for the extra gains
`editable = "packages/machinome-mechanics"`; the package's entry changes
`source = { registry = "https://pypi.org/simple" }` and its `sdist` and
`wheels` to `source = { editable = "packages/machinome-mechanics" }` with
`[package.metadata] requires-dist = [{ name = "machinome", editable =
"packages/machinome" }]`. The new `uv.lock` is byte-identical to probe 10's
(`diff <bench>/uv.lock scratchpad/C2-propose/uv.lock.joined`: no output).

```
$ env -C <bench> /home/asa/.local/bin/uv sync --python 3.12
Resolved 188 packages in 10ms
   Building machinome @ file://<bench>/packages/machinome
   Building machinome-mechanics @ file://<bench>/packages/machinome-mechanics
...
Uninstalled 2 packages in 9ms
Installed 2 packages in 12ms
 ~ machinome==0.8.1 (from file://<bench>/packages/machinome)
 - machinome-mechanics==0.1.0
 + machinome-mechanics==0.1.0 (from file://<bench>/packages/machinome-mechanics)
```

(`<scratch>/5.2-sync.txt`.) Thirteen `__editable__` files (`<scratch>/5.2-pth.txt`),
the new one `__editable__.machinome_mechanics-0.1.0.pth` holding
`<bench>/packages/machinome-mechanics`; `site-packages/machinome_mechanics/`
is gone, only the editable `machinome_mechanics-0.1.0.dist-info` remains.

```
$ env -C /tmp <bench>/.venv/bin/python -c "import machinome.mechanics as m; print(m.__file__)"
<bench>/packages/machinome-mechanics/machinome/mechanics/__init__.py
$ env -C /tmp <bench>/.venv/bin/python -c "import machinome_mechanics"
ModuleNotFoundError: No module named 'machinome_mechanics'
```

`git -C <bench> status --short` shows no build leaving under
`packages/machinome-mechanics`; `--ignored` shows its `__pycache__/` and
`machinome_mechanics.egg-info/`, ignored by the root's `.gitignore`.

### 5.3 The vet universe (task 5.3)

`members = ["machinome", "molejo"]`. `tests/test_vet_universe.py`: 15 passed,
7 subtests passed.

### 5.4 The gates again (task 5.4)

```
$ ... pytest tests/test_mechanics_boundary.py tests/test_repository_layout.py tests/test_release_records.py
3 failed, 54 passed, 333 subtests passed in 4.20s
```

(`<scratch>/5.4.txt`.) Green but the CI step
(`test_the_test_job_runs_each_product_s_tests`), the root README
(`test_the_readme_links_every_package_and_states_the_licence`) and the
contributor guide (`test_the_guide_installs_every_member_without_uv`), each
for `machinome-mechanics`, which groups 8 and 9 turn green.

## 6. The tests at their new place

### 6.1 The imports (task 6.1)

In the fourteen formula and integration modules: `from machinome_mechanics`
to `from machinome.mechanics` (`import ...` and the family modules'
`... as family_helper`), the twelve `from solid2 import get_animation_time`
to `from machinome.expression_graph import get_animation_time`, the two
`from machinome.node import AssemblyNode` to `from machinome.node.assembly
import AssemblyNode`, and `test_mechanisms.py`'s docstring's first word.
`git diff -U0` of those modules shows those lines and the SPDX lines of 4.3,
nothing else (14 lines of the probe 2 kind).

The helper import `from tests.test_mechanisms import _eval_openscad_expr`
(nine modules): a scratch pytest plugin (`<scratch>/probe/tests_probe.py`,
loaded with `-p`, printing `sys.modules['tests']` at the session's end) shows
that under the package's pytest run (`--import-mode=importlib`, from
`packages/machinome-mechanics`) it binds the package's own:

```
PROBE tests module: <module 'tests' (namespace) from ['<bench>/packages/machinome-mechanics/tests']>
PROBE tests.test_mechanisms: <bench>/packages/machinome-mechanics/tests/test_mechanisms.py
```

(`<scratch>/6.2-probe.txt`.) Outside pytest, a plain `python -c "import
tests"` from the same directory binds the framework's regular package
`packages/machinome/tests/__init__.py`, through the core's editable line; the
package's tests are never imported that way. Nothing was changed.

### 6.2 The package's tests (task 6.2)

```
$ env -C <bench>/packages/machinome-mechanics <bench>/.venv/bin/python -m pytest -q -p no:cacheprovider
2 failed, 202 passed, 24 subtests passed in 2.36s
```

(`<scratch>/6.2.txt`.) 204 tests: 195 formula and integration tests and the
nine of the two rewritten pinning modules. The two failures are
`test_documentation.py`'s link and example tests, which group 7 turns green
(the pages still imported `machinome_mechanics`, which nothing provides after
the sync, and linked the framework's manual on Read the Docs).

### 6.3 The core collects none of them (task 6.3)

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/python -m pytest --collect-only -q -p no:cacheprovider | grep -c machinome-mechanics
0
```

(4858 tests collected; `<scratch>/6.3-collect.txt`.)

## 7. The manual

### 7.1 The build at the join (task 7.1)

A fresh venv, `<scratch>/docs-venv`, installing
`packages/machinome/docs/requirements.txt` alone (Sphinx 9.1.0,
sphinx_rtd_theme 3.1.0 and machinome-viewer 0.8.0 from PyPI):

```
$ env -C <bench>/packages/machinome <scratch>/docs-venv/bin/python -m sphinx -b html -n -W --keep-going docs <scratch>/html-red
exit 1
```

(`<scratch>/7.1-red.txt`.) 22 warnings and 31 errors, those of probe 9:
three pages in no toctree (`reference/mechanics/index.rst`,
`reference/mechanics/conventions.rst`, `howto/mechanism-formulas.rst`);
eleven `unknown document` links of the former layout (`../conventions` three
times, `reference/<family>` five times on the conventions page,
`../using-with-machinome`, `reference/index` and `reference/cranks` on the
how-to); three `Include file ... howto/examples/...` and three `download file
not readable`; the two drawings `reference/_static/*.svg` not readable; and
31 `Unknown directive type "doctest"` (linkages 6, gears 4, belts 4, screws 3,
cranks 3, rolling 2, indexing 2, deltas 2, conventions 2, the how-to 2, cams
1).

### 7.2 to 7.4 The edits (tasks 7.2, 7.3, 7.4)

- `docs/conf.py`: `'sphinx.ext.doctest'` in `extensions`;
  `mechanics_version`'s comment as Decision 10 words it, on two lines above
  the assignment. `tests/test_docs_structure.py` pins no `extensions` (the one
  `extensions` line in the suite is `test_sphinx_ext.py`'s own fixture).
  `docs/index.rst`: `howto/mechanism-formulas` after
  `howto/freecad-assemblies`, `reference/mechanics/index` after
  `reference/sphinx`.
- `reference/mechanics/index.rst`, rewritten in place: the title "Mechanics
  helpers", the landing page's two paragraphs (its link a `:doc:` link to
  `/concepts/relations`), Decision 10's sentence, the family table under its
  heading "Find the formula you need" with section-relative links, then
  `.. py:module:: machinome.mechanics` and the helper table under the heading
  "Every helper", and the toctree `conventions` and the nine families.
- The family and conventions pages: `machinome_mechanics` to
  `machinome.mechanics` (same length; no line rewrapped), the `:doc:` links
  section-relative (`conventions`, `<gears>` and the four others,
  `/howto/mechanism-formulas`), the two figures `/_static/<drawing>.svg`, the
  conventions page's assertions link `:doc:`/reference/assertions``, which
  rewraps its two lines.
- `howto/mechanism-formulas.rst`, converted in place: the title "Use a
  mechanism formula in a machine"; an opening that installs (`pip install
  "machinome[mechanics]"`, linking the section); a section "Calculate a pose"
  with the landing page's three-line example and `getting-started.rst`'s
  quarter-turn screw as doctests; then its own sections, the project manifest
  paragraph moved into "Connect an input to a joint"; the includes and
  downloads naming `mechanism-formulas/...`; the framework links `:doc:`
  links. Its two example modules import `AssemblyNode` from
  `machinome.node.assembly` and the helpers from `machinome.mechanics`.
- `start/install.rst`, `reference/api.rst`, `concepts/relations.rst`,
  `howto/timeline.rst`, `reference/manuals.rst` and `project/upgrading.rst`
  as Decision 10 words them, each rewrapped at its width.

### 7.5 The build after (task 7.5)

```
$ env -C <bench>/packages/machinome <scratch>/docs-venv/bin/python -m sphinx -b html -n -W --keep-going docs <scratch>/html
exit 0
```

No warning (`<scratch>/7.5-html.txt`). Pages looked at, screenshots by
headless Chromium (Playwright from the workspace venv,
`<scratch>/shots/shoot.py`) in `<scratch>/shots/`: the section index (title,
three paragraphs, the family table, the helper table of 24 rows), the cranks
page with `slider-crank.svg` drawn (218 by 150), the linkages page with
`circle-intersection.svg` drawn (248 by 150), and the how-to with its three
downloads (`pyproject.toml`, `slider_crank.py`, `gear_phase.py`, each under
`_downloads/`) and its literal includes.

The first build placed the section's toctree at the end of the index, which
nested the ten pages under the heading "Every helper" in the sidebar. The
toctree was moved after the opening paragraphs, marked `:hidden:` (the family
table and the conventions link already list every page), and the build
repeated: exit 0, no warning; the sidebar lists the ten pages under
"Mechanics helpers".

```
$ ... pytest tests/test_docs_structure.py tests/test_docs_exports.py tests/test_node_root_exports_nothing.py
1 failed, 60 passed, 1286 subtests passed in 4.62s
```

The one red was the framework's `README.rst` still linking the separate
manual, which task 9.4 turns green. The package's documentation test:

```
$ env -C <bench>/packages/machinome-mechanics <bench>/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_documentation.py
6 passed in 0.90s
```

Examples per page, `doctest.testfile` with Sphinx's default flags and the
example directory on the path (attempted, failed): `belts.rst` 27 0,
`cams.rst` 6 0, `conventions.rst` 6 0, `cranks.rst` 8 0, `deltas.rst` 8 0,
`gears.rst` 21 0, `index.rst` 0 0, `indexing.rst` 6 0, `linkages.rst` 28 0,
`rolling.rst` 10 0, `screws.rst` 11 0, `mechanism-formulas.rst` 18 0; 149 in
all, 141 of probe 9 and the eight of the how-to's new opening.

## 8. The version records, `scripts/check-dist` and CI

### 8.1 The bump on a copy (task 8.1)

`.bumpversion.cfg`, the 15 files its tables name and
`packages/machinome-mechanics/pyproject.toml` copied to `<scratch>/bump/`,
made a git repository and committed, then:

```
$ env -C <scratch>/bump <bench>/.venv/bin/bump2version --no-commit --no-tag --new-version 0.9.0 patch
exit 0
$ git -C <scratch>/bump diff --shortstat
 16 files changed, 45 insertions(+), 45 deletions(-)
$ git -C <scratch>/bump diff --quiet -- packages/machinome-mechanics/pyproject.toml && echo unchanged
unchanged
```

The 45 lines are `join-freecad`'s exactly (11 `machinome~=0.9.0`, 13
`version = "0.9.0"`, the extension packages' pins, `__version__`,
`current_version`, `release`); none of the mechanics manifest's lines, and
`docs/conf.py`'s `mechanics_version` is not touched. Nothing written in the
bench.

### 8.2 Red first (task 8.2)

```
$ env -C <bench> <bench>/.venv/bin/python scripts/check-dist
check-dist failed: machinome-mechanics has no smoke in scripts/check-dist
Nothing uploaded.
```

(`<scratch>/8.2-red.txt`, exit 1.)

### 8.3 The row (task 8.3)

`MECHANICS_VERSION` after `ROOT` and the row of Decision 9 after the FreeCAD
package's, verbatim; `git diff -- scripts/check-dist`: 45 insertions, no
deletion. `flake8 --max-line-length=89 scripts/check-dist`: 0 lines.

### 8.4 The run (task 8.4)

```
$ env -C <bench> <bench>/.venv/bin/python scripts/check-dist
...
machinome-mechanics 0.1.0 module /tmp/machinome-check-dist-kq5kuph2/venv/lib/python3.12/site-packages/machinome/mechanics/__init__.py numeric and symbolic
...
Every distribution built, checked, installed and smoked; nothing uploaded.
exit 0
```

(`<scratch>/8.4-check-dist.txt`.) Thirteen members built, 26 archives
`twine check --strict` PASSED; the mechanics wheel installed by its path
(`.../dist/machinome-mechanics/machinome_mechanics-0.1.0-py3-none-any.whl`
among pip's requirements, no `machinome[mechanics]`); its licence lines
`License-Expression: GPL-2.0-or-later OR CERN-OHL-S-2.0+`,
`licenses/LICENSE`, `licenses/LICENSES/CERN-OHL-S-2.0.txt`,
`licenses/LICENSES/GPL-2.0-or-later.txt`. Archive entries: `machinome` sdist
1059, wheel 114; `machinome-mechanics` sdist 213, wheel 17 (probe 11's
counts); the engines and `build123d`, `cadquery`, `jscad`, `molejo`, `solid2`,
`step`, `stl` 18 and 8 each; `freecad` 22 and 11; `openscad` 23 and 12. The
run built from the tree before the records of group 9; 10.5 repeats it on the
final tree. `git -C <bench> status --short` afterwards: no new entry.

### 8.5 CI (task 8.5)

`.github/workflows/python-app.yml`: the step of Decision 8 after "Run tests"
in the `test` job. The layout gate's CI tests green (9.4's run).

## 9. The records

### 9.1 The changelogs (task 9.1)

`HISTORY.rst` and `docs/project/changelog.rst`: Decision 12's bullets,
verbatim, at the end of `Unreleased` after the digest bullet. The package's
`CHANGELOG.md`: the two bullets under `## Unreleased` after the branch's;
the 0.1.0 identity bullet loses the licence word in place (Open Questions 5,
accepted by the orchestrator): "Package `machinome-mechanics`, import
`machinome_mechanics`, depending on `machinome>=0.7.0` ...", rewrapped over
its first two lines.

### 9.2 `CREDITS.md` (task 9.2)

Unchanged. The product's `NOTICE` at 6588f0c reads, whole: "Machinome
Mechanics - Mechanical formula helpers for Machinome projects / Copyright (C)
2023-2026 Luis Henrique Cassis Fagundes". It names the author and the
copyright alone; no third party's work is called, adapted or retained.

### 9.3 `docs/architecture.md` (task 9.3)

The section's title and first paragraph, its last sentence's import, the
extras sentence's `[mechanics]` clause and the Map row, as Decision 12 words
them.

### 9.4 The repository's records (task 9.4)

The root `README.md`'s row after the FreeCAD package's;
`packages/machinome/README.rst`'s sentence; `CONTRIBUTING.rst`'s pip block
(`-e packages/machinome-mechanics \` before the framework's line) and the
sentence after the suite's commands; `context7.json`'s three excluded folders
and the rule, before the closing rule on claims (20 rules); `AI-USE.md`'s two
edits. The gates:

```
$ ... pytest tests/test_repository_layout.py tests/test_docs_structure.py \
    tests/test_release_records.py tests/test_profile_documentation.py \
    tests/test_mechanics_boundary.py tests/test_vet_universe.py \
    tests/test_docs_exports.py tests/test_node_root_exports_nothing.py \
    tests/test_core_names_no_scad.py
136 passed, 1649 subtests passed in 6.64s
```

(`<scratch>/9-gates.txt`.)

### 9.5 ADR-187 (task 9.5)

`docs/adrs/BUILD/ADR-187-the-mechanics-helpers-are-a-portion-of-the-repository-at-their-own-version.md`,
Status Proposed, as Decision 12 outlines it (the orchestrator accepted Open
Questions 2); its index line under BUILD after ADR-183. ADR-132's status line
and index line note the import path and repository superseded by 187;
ADR-182 and ADR-183 gain the dated consequence "Neutral (2026-10-12,
`join-mechanics`): a product of a repository of its own may join with its
record in its directory and its own version (ADR-187)", and their status and
index lines "amended by 187". Every relative link of ADR-187 resolves.

### 9.6 The product's record (task 9.6)

In place: `openspec/specs/mechanisms/spec.md` (`Code: machinome/mechanics/`
and the five requirements' import); `openspec/specs/distribution/spec.md`
(Purpose, the requirement's import, licence and floor, the install
scenario's Machinome 0.8 and import; "The release pair is legible" kept);
`openspec/specs/user-documentation/spec.md` ("User documentation is readable
and independently hosted", its title kept, and its scenario);
`openspec/config.yaml`'s context; `workflow/README.md` and
`workflow/documentation.md` (the Read the Docs section gone).

```
$ env -C <bench>/packages/machinome-mechanics openspec validate --specs --strict
✓ spec/distribution
✓ spec/mechanisms
✓ spec/user-documentation
Totals: 3 passed, 0 failed (3 items)
```

### 9.7 The licences in the changed and joined files (task 9.7)

The files `git diff --name-only db007dd0` lists with the untracked ones, 192.
The product's former licence, by file and count: its archived changes
`2026-09-19-rename-mechanics-to-machinome/specs/distribution/spec.md` 1,
`2026-09-20-add-belt-tangent-points/proposal.md` 1,
`2026-09-20-add-rolling-travel/specs/distribution/spec.md` 1,
`2026-09-22-release-mechanics-with-0-7/design.md` 1 and its
`specs/distribution/spec.md` 1; its workflow notes `extraction.md` 1,
`release-0.1.md` 2 and `validation.md` 1. None in its README, manifest,
modules, tests, specs, `openspec/config.yaml`, `workflow/README.md`,
`workflow/documentation.md`, or the changelog, whose 0.1.0 bullet no longer
names it. `HISTORY.rst` holds two lines naming earlier licences in its
released sections (lines 924 and 1469), present at db007dd0 and untouched by
this change. Nothing this change wrote names the product's former licence or
the framework's former one.

## 10. Validation

### 10.1 The suite (task 10.1)

```
$ env -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH \
    <bench>/.venv/bin/python -m pytest -q -rs -p no:cacheprovider
4838 passed, 24 skipped, 55 warnings, 7505 subtests passed in 711.29s (0:11:51)
```

(`<scratch>/10.1-suite.txt`, one process.) No failure. The 24 skips are the
base's: 16 without `machinome-viewer` (14 in `test_browser_renderer.py`, 1 in
`test_cli_lazy_imports.py`, 1 in `test_scad_presentation.py`); 4 FreeCAD
modules without `MACHINOME_FREECAD_ROOT`; 2 in `test_step_assembly.py`
without the vendor STEP; 1 in `test_connectivity.py` without networkx; 1 in
`test_jscad_integration.py` without the jscad CLI. Passed: the base's 4827 and the 11 tests this
change adds: `test_the_guard_refuses_the_helpers_address`; the five tests of
`TheProductsTest` and `test_the_test_job_runs_each_product_s_tests`;
`test_a_member_of_its_own_version_is_outside_the_bump`;
`test_the_mechanics_helpers_are_inside_and_their_former_name_outside`;
`test_the_mechanics_helpers_are_a_reference_section_and_a_how_to` and
`test_the_mechanics_version_is_the_package_s`.

### 10.2 The package's tests (task 10.2)

```
$ env -C <bench>/packages/machinome-mechanics <bench>/.venv/bin/python -m pytest -q -p no:cacheprovider
204 passed, 24 subtests passed in 1.85s
```

(`<scratch>/10.2.txt`.) 195 formula and integration tests (design.md's "201"
counted the product's six former pinning tests among them, probe 3's 195
plus 6) and the nine tests of the two rewritten pinning modules.

### 10.3 The lint (task 10.3)

```
$ env -C <bench>/packages/machinome bash -c \
    '<bench>/.venv/bin/flake8 --max-line-length=89 machinome tests ../machinome-*/machinome' | wc -l
1512
```

(`<scratch>/10.3-lint.txt`.) The same command on `git archive db007dd0`
unpacked in scratch: 1507 (`<scratch>/10.3-lint-base.txt`). The 5 more are
the package's, probe 13's: `__init__.py` E127 twice and E128 once (the
import lines' continuation indents, unchanged by the same-length rename) and
`deltas.py` E501 twice. The core's new tests add none. The package's tests,
outside CI's lint paths: 47 lines.

### 10.4 The manual on the final tree (task 10.4)

The build of 7.5 into `<scratch>/html-final`: exit 0, no warning
(`<scratch>/10.4-html.txt`).

### 10.5 `check-dist` on the final tree and on a clean copy (task 10.5)

On the tree (`<scratch>/10.5-check-dist-tree.txt`) and on a clean copy
(`<scratch>/10.5-check-dist-clean.txt`): `git ls-files -z --cached --others
--exclude-standard` packed with `tar --null -T -` and unpacked under
`<scratch>/clean/` (3682 entries, links kept). Both exit 0, 26 archives
`twine check --strict` PASSED, the mechanics line "machinome-mechanics 0.1.0
module .../venv/lib/python3.12/site-packages/machinome/mechanics/__init__.py
numeric and symbolic", nothing uploaded.

| archive | tree | clean copy | base clean copy |
|---|---|---|---|
| `machinome` sdist | 1115 | 1059 | 1046 |
| `machinome` wheel | 114 | 114 | |
| `machinome-mechanics` sdist | 213 | 213 | |
| `machinome-mechanics` wheel | 17 | 17 | |
| every other member | as 8.4 | as 8.4 | |

The tree's framework sdist also carries ignored files the suite leaves under
`tests/`; the clean copy's is the release's. The base clean copy's framework
sdist was built in scratch from `git archive db007dd0`
(`<scratch>/sdist-base.txt`); the final's from `<scratch>/clean/`
(`<scratch>/sdist-final.txt`). It grows by 13 entries, none removed
(`<scratch>/sdist-added.txt`): `docs/howto/mechanism-formulas.rst`, the
directory `docs/reference/mechanics/` and its eleven pages. The two drawings
and the how-to's example project are not in it: the framework's
`MANIFEST.in` carries `docs` as `*.rst conf.py Makefile make.bat *.jpg *.png
*.gif`, which no `.svg`, `.py` or `.toml` under `docs/` matches, as the
tutorial's modules under `docs/tutorial/counter/` are not carried either.

### 10.6 Git (task 10.6)

`git -C <bench> status --short`: 86 entries, 82 modified, 2 added (the two
links), 2 untracked (ADR-187 and this file), every one an edit or addition of
groups 3 to 9. `git ls-files -ci --exclude-standard | wc -l`: 34, as at the
base. `git status --short --ignored` adds the twelve packages' and the new
package's `__pycache__/` and `*.egg-info/`, `.env`, `.venv/` and the
framework's ignored `tests/step_project/wrapped_single_part.step`, a leaving
of the suite.

### 10.7 The change validates (task 10.7)

```
$ env -C <bench>/packages/machinome openspec validate join-mechanics --strict
Change 'join-mechanics' is valid
```

## 11. The projects' move and the sweep (the orchestrator's)

Measured by the orchestrator after the review of groups 3 to 10 and recorded
here as reported; the logs are under `scratchpad/C2-join/` (its
`validate.log` names each) and `scratchpad/C2-move/`.

The orchestrator's own validation of the reviewed tree first: the whole
suite on the bench venv from `packages/machinome`, 4838 passed, 24 skipped,
7505 subtests, 697 s (`scratchpad/runs/C2-suite.log`); the manual, `sphinx -b
html -n -W --keep-going` on a `docs/requirements.txt` venv, exit 0, no
warning (`C2-join/docs-build.log`); `scripts/check-dist` on the tree, exit 0,
"Every distribution built, checked, installed and smoked; nothing uploaded"
(`C2-join/check-dist-tree.log`).

### 11.1 The sweep before the move (task 11.1)

Not run, and the workspace's moved-names file
(`scripts/load-projects.d/join-mechanics.toml`) was not written. The move's
red is the one task 5.2 records: once the sync removed the PyPI 0.1.0, the
bench venv raises `ModuleNotFoundError: No module named
'machinome_mechanics'`, which every project importing the former module
meets at its import.

### 11.2 The move (task 11.2)

The script `scratchpad/C2-move/move.py` rewrote 47 files in 26 repositories:
every `.py` and `README.md` outside `docs/`, `_build*`, `WTs`, `.git`,
`.venv`, `node_modules` and `.tools`, by the rules of design.md Decision 16
(the two import forms, the bare import, the dotted mention in docstrings and
comments, the path `machinome_mechanics/<family>.py`, and the backticked bare
name). It left science-jubilee's `simulation/tools/run_frame_audit.py`,
pinned to a framework revision, and every verification record under `docs/`.
One commit per repository on the branch each had checked out, with Decision
16's message (`scratchpad/C2-move/commits.txt`):

| repository | commit | branch | files |
|---|---|---|---|
| 3D-Printers/Metamaquina2 | b152fb5 | main | 3 |
| 3D-Printers/Prusa3-vanilla | 6421728 | frames-and-mates | 2 |
| 3D-Printers/fender-bender | 7bdb381 | main | 1 |
| 3D-Printers/hangprinter | 244bc90 | version_4 | 2 |
| 3D-Printers/kossel | 27df601 | frames-and-mates | 5 |
| 3D-Printers/snappy-reprap | c4e35b7 | master | 1 |
| 3DPrintedClocks | 235e483 | solid-node-simulation | 4 |
| Actuators/OpenCycloid | 6bd7e4b | main | 1 |
| Actuators/OpenTorque-Actuator | 05f51da | master | 1 |
| Actuators/open_robot_actuator_hardware | 90e009f | master | 1 |
| Calculators/Pascaline-module | 2a81317 | main | 1 |
| CycloidalDrive | fdc890c | main | 1 |
| Lab-Equipment/openflexure-microscope | 410b0982 | frames-and-mates | 1 |
| Leonardo | aefe269 | release-video | 3 |
| Locks/Vault_with_combination_lock | b49d9d5 | main | 1 |
| Robotic-Arms/Thor | ff8d0de | main | 6 |
| Robotic-Hands/Inmoov-sim | 04ebe44 | main | 1 |
| Robots/AlbertPro | 485a930 | frames-and-mates | 1 |
| Robots/ZeroBug | c02e431 | main | 1 |
| Robots/hexapod_spiderbot_model | 470bb33 | frames-and-mates | 1 |
| Vibecoded-demos/Deepseek/Leonardo-hydraulic-sawmill | 9444600 | main | 1 |
| Vibecoded-demos/v8-engine | 9ae9633 | declarative-api | 2 |
| dragon-r1 | d09fba7 | frames-and-mates | 3 |
| sandbox/dutch-windmill-2 | 1c9d29e | main | 1 |
| sandbox/gearbox | a28de23 | main | 1 |
| strandbeest | f7cce4a | main | 1 |

26 repositories, the design's 27 less science-jubilee, whose only mention
is the pinned tool. The workspace's venv was given the joined package
editable from the bench, so the pilot's floor keeps serving the moved
projects.

### 11.3 Three projects' tests (task 11.3)

On the bench venv with `machinome test` (the projects' companion tests are
the framework runner's, not pytest's):

- Thor: 34 tests, 29 passed, 5 failed, the same five as on the workspace venv
  before the move (`test_assembly_integrity`,
  `test_both_shoulder_pinions_clear_the_ring`,
  `test_each_shoulder_pinion_is_free_within_its_backlash`,
  `test_the_pinions_stay_in_mesh_through_the_shoulder_s_travel`,
  `test_the_demo_never_drives_a_part_through_another`: the B-rep common
  refused, "gear is inside out", unrelated to the helpers)
  (`C2-join/thor-tests.log`; baseline `C2-move/baseline-thor.log`).
- dragon-r1: 3 passed (`C2-join/dragon-tests.log`).
- 3DPrintedClocks, `wall_clock_02 --mesh`: 22 tests, 14 passed, 8 failed,
  the same eight as before the move on the pilot's dirty tree (the recorded
  pendulum-hardware and weight debts) (`C2-join/clock02-tests.log`; baseline
  `C2-move/baseline-clock02.log`).

### 11.4 The sweep after the move (task 11.4)

The command of design.md Decision 17 (`C2-join/sweep.log`,
`C2-join/load-projects.json`): 63 repositories, 130 rows, 122 ok, 0
expected, 2 unexpected (fender-bender without `fb_library`, wall_clock_41's
own error, the base's two), 0 timeout, 6 no-model, 2 skipped; identical to
`join-freecad`'s row for row, compared by project and model.

## 12. Records closing

### 12.1 ADR-187 (task 12.1)

Promoted to Accepted after the orchestrator's review of 12 October 2026: its
status line, its change link (now the archive,
`../../../openspec/changes/archive/2026-10-12-join-mechanics/`, which
resolves) and its index line in `docs/adrs/README.md` ("**Accepted**,
supersedes 132's import path and repository, amends 182/183, cites
076/149/170"). `docs/architecture.md` checked against it: the mechanics
section names `packages/machinome-mechanics/`, the import
`machinome.mechanics`, the package's own version and its record in its
directory with ADR-132 and ADR-187, and the Map row cites 022, 076, 132 and
187.

### 12.2 The archive (task 12.2)

```
$ env -C <bench>/packages/machinome openspec archive join-mechanics -y
Applying changes to openspec/specs/framework-contributor-guidance/spec.md:
  ~ 1 modified
Applying changes to openspec/specs/framework-identity/spec.md:
  ~ 2 modified
Applying changes to openspec/specs/mechanics-distribution/spec.md:
  ~ 1 modified
Applying changes to openspec/specs/user-documentation/spec.md:
  ~ 1 modified
  → 1 renamed
Applying changes to openspec/specs/vet/spec.md:
  ~ 1 modified
Totals: + 0, ~ 6, - 0, → 1
Change 'join-mechanics' archived as '2026-10-12-join-mechanics'.
$ env -C <bench>/packages/machinome openspec validate --specs --strict
Totals: 46 passed, 0 failed (46 items)
```

(`<scratch>/12.2-archive.txt`, `<scratch>/12.2-validate.txt`.) "~ 6 modified,
→ 1 renamed", as probe 14; the renamed requirement, "The mechanics helpers are
documented in the manual", stands at the end of `user-documentation`. The CLI
warned that the proposal's Why exceeds 1000 characters (non-blocking) and
that 9 tasks were open at the moment of archiving (10.8 and groups 11 and
12); `tasks.md` in the archive then ticks every task but 11.1, which was not
done (11.1 above).

### 12.3 The plan's progress (task 12.3)

The root's `workflow/ongoing/joins-0.9.md`, "Progress": entry 2,
`join-mechanics`, after the note "Between cycles 1 and 2".

### 12.4 This record (task 12.4)

Complete. The implementation commit is the orchestrator's, on top of the
merge commit 076b566d and the planning commit db007dd0, neither amended;
nothing pushed.
