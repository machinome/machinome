# Evidence: `cut-the-engines`

The second cycle of the 0.9 monorepo campaign (`workflow/ongoing/monorepo-0.9.md`
at the repository root, "The campaign: the cut", cycle 2). Worktree
`machinome/WTs/v0.9-base-cut-the-engines`, branch `v0.9-base-cut-the-engines`,
cut from the line `v0.9-base` at 6fb505ed ("Implement monorepo-layout"). Planning
commit edf88424, ratified by the orchestrator's review. Applied on 10 October
2026.

Tools: uv 0.11.8, CPython 3.12.3 (the bench venv), the OpenSpec CLI 1.6.0,
git 2.43.0. Every command ran with `env -C <dir>` and absolute paths; `<bench>`
is `/home/asa/devel/machinome/machinome/WTs/v0.9-base-cut-the-engines` and
`<scratch>` is
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C2-apply/`.
Every test ran from `<bench>/packages/machinome` on the bench venv
(`<bench>/.venv/bin/python -m pytest -q -p no:cacheprovider ...`), one pytest
process at a time. Logs are in `<scratch>`, never in the bench.

## 1. Evidence baseline

### 1.1 The base (task 1.1)

```
$ git -C <bench> log --oneline -2
edf88424 Propose cut-the-engines: the B-rep and mesh engines as the first extension packages (decided 10 October 2026)
6fb505ed Implement monorepo-layout: the framework's tree under packages/machinome, the root the repository's
$ git -C <bench> status --short | wc -l
0
```

`git status --short --ignored` showed `!! .env` alone (the bench's port file).

### 1.2 The bench venv on the base's tree (task 1.2)

```
$ env -C <bench> /home/asa/.local/bin/uv sync --python 3.12
Using CPython 3.12.3 interpreter at: /usr/bin/python3.12
Creating virtual environment at: .venv
Resolved 185 packages in 2ms
Installed 175 packages in 9.53s
$ ls <bench>/.venv/lib/python3.12/site-packages/__editable__*.pth
__editable__.machinome-0.8.1.pth
$ cat .../__editable__.machinome-0.8.1.pth
<bench>/packages/machinome
```

One `__editable__` file, holding the framework's directory, as the first
cycle's 5.2. The base suite on the same tree and recipe, recorded from the
first cycle's evidence (7.1), not rerun: `4774 passed, 20 skipped, 6799
subtests passed`.

### 1.3 The lint base (task 1.3)

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/flake8 --max-line-length=89 machinome tests | wc -l
759
```

### 1.4 The sweep base (task 1.4, recorded, not rerun)

`root-cleanup`'s counts (design.md, Decision 12): 62 repositories, 129 rows,
121 ok, 0 expected, 2 unexpected (wall_clock_41's own CadQuery error, Dum-E
without machinome-freecad), 0 timeout, 6 no-model, 2 skipped.

## 2. Red first, at the base's paths

Nothing moved in this group.

### 2.1 The layout gate (task 2.1)

`tests/test_repository_layout.py`: a new class `TheExtensionPackagesTest`
(G9) with `ENGINES = {'machinome-engine-brep': 'brep', 'machinome-engine-mesh':
'mesh'}` and six methods, the five of design.md Decision 9 and
`test_the_guide_installs_every_member_without_uv`; in `TheWorkspaceTest` (G4)
the base's `test_the_framework_is_a_workspace_source` and
`test_the_lock_records_the_member_editable` folded into
`test_every_member_is_a_workspace_source`. The source names are the
directories' names; the manifest test pins each name to its directory.

```
$ ... pytest tests/test_repository_layout.py
11 failed, 25 passed, 74 subtests passed in 1.84s
```

(`<scratch>/2.1-layout-red.txt`; 11 counts the failed methods and subtests.)

- `test_each_engine_directory_holds_only_what_distinguishes_it`, both
  subtests: `<bench>/packages/machinome-engine-brep is missing` (and `-mesh`).
- `test_each_engine_manifest_is_a_portion_of_the_set`, both:
  `FileNotFoundError` on `packages/machinome-engine-brep/pyproject.toml`
  (and `-mesh`).
- `test_each_engine_readme_names_its_install_and_the_licence`, both:
  `FileNotFoundError` on the two `README.md`.
- `test_each_provider_resolves_from_its_package`, both:
  `.../packages/machinome/machinome/engine/brep.py != .../packages/machinome-engine-brep/machinome/engine/brep.py`
  (and `mesh.py`).
- `test_the_core_engine_package_holds_only_the_seams`: `Items in the first
  set but not the second: 'mesh.py' 'brep.py'`.
- `test_the_guide_installs_every_member_without_uv`: subtest
  `editable_mode=compat`, `CONTRIBUTING.rst does not install in compat mode`;
  subtest `\btox\b`, `CONTRIBUTING.rst names 'tox'` (`make test-all`, tox's).
  Its `machinome` subtest is green (`-e "packages/machinome[dev]"` is there);
  with one directory under `packages/` it has no engine subtest yet.
- `test_every_member_is_a_workspace_source`: green (one directory, one
  source); its red is task 3.3's.

### 2.2 `tests/test_kernel_extras.py` (task 2.2)

`REPOSITORY = parents[3]`; `VERSION` read from the framework's manifest;
`EXTRAS['brep'] = {f'machinome-engine-brep~={VERSION}'}` and `mesh` likewise;
`ENGINE_REQUIREMENTS` and `test_each_engine_requires_the_core_and_its_kernel`,
`test_the_occt_range_is_stated_once`, `test_the_lock_installs_every_kernel`,
`test_ci_syncs_the_locked_workspace` added;
`test_ci_installs_every_concrete_requirement_of_all` and
`test_tox_installs_every_extra` removed with the `configparser` import; the
docstring names the manifests, the lock and the CI workflow.

```
$ ... pytest tests/test_kernel_extras.py
9 failed, 15 passed, 41 subtests passed in 1.69s
```

- `test_each_extra_lists_what_its_module_needs`, subtests `brep` and `mesh`:
  `'cadquery-ocp>=7.8.1,<7.9'` against `'machinome-engine-brep~=0.8.1'`, and
  `'manifold3d'` against `'machinome-engine-mesh~=0.8.1'`.
- `test_each_engine_requires_the_core_and_its_kernel`, both subtests:
  `FileNotFoundError` on the two engine manifests.
- `test_the_occt_range_is_stated_once`: `['machinome[brep]'] !=
  ['machinome-engine-brep']` (named in the framework's `brep` extra).
- `test_the_lock_installs_every_kernel`: `'machinome-engine-mesh'`,
  `'machinome-engine-brep'` not in the lock.
- `test_ci_syncs_the_locked_workspace`, subtests `lint`, `test`,
  `browser-snapshot`: `0 != 1 : <job> does not run uv sync --locked`.

### 2.3 `tests/test_core_kernel_free.py` (task 2.3)

`REPOSITORY = parents[3]`; `portion_modules()` yields every module under
`packages/machinome-*/machinome/`, keyed relative to `packages/`; `PROVIDERS`,
`MESH_PROVIDER` and the two provider exclusions dropped; the core census
without the two engine rows; `test_the_engine_packages_import_only_their_kernels`
added; `EXTRA_OF`'s engine keys spelled
`machinome-engine-<x>/machinome/engine/<x>.py`; the `require_extra` test reads
`dict(every_module()) | dict(portion_modules())`. Also, beyond the design's
list, `test_no_module_reaches_trimesh_boolean` reads the portions beside the
core, so the mesh provider stays under the scan it was under at the base
(departure 2).

```
$ ... pytest tests/test_core_kernel_free.py
5 failed, 7 passed, 21 subtests passed in 5.21s
```

- `test_kernels_are_imported_only_by_their_modules`: the core census finds
  `machinome/engine/brep.py: ['OCP']` and `machinome/engine/mesh.py:
  ['manifold3d']` beyond the expected rows.
- `test_the_engine_packages_import_only_their_kernels`: `{} != {...brep.py:
  ['OCP'], ...mesh.py: ['manifold3d']}`.
- `test_each_kernel_module_checks_its_kernel_first`, subtests on the two
  portion keys: `KeyError: 'machinome-engine-brep/machinome/engine/brep.py'`
  (and mesh).
- `test_no_core_module_imports_the_kernel_or_cadquery`, the fourth red,
  which the task's list does not name: with the provider exclusion dropped
  the core's scan finds `machinome/engine/brep.py: ['OCP']`. It is the same
  fact as the census's red and goes green at the move.

### 2.4 `tests/test_release_records.py` (task 2.4)

`members()` reads `packages/*/pyproject.toml`; `VersionFilesTest` reads
`current_version` from `REPOSITORY / '.bumpversion.cfg'` in place of
`setup.cfg`; `test_every_member_is_numbered_with_the_core`,
`test_every_pin_between_members_is_compatible` and
`test_the_version_is_bumped_from_the_root` added.

```
$ ... pytest tests/test_release_records.py
2 failed, 11 passed, 57 subtests passed in 0.34s
```

- `test_every_version_file_agrees_with_pyproject` and
  `test_the_version_is_bumped_from_the_root`: `FileNotFoundError` on
  `<bench>/.bumpversion.cfg`.
- The member and pin tests green (one member, no pin); their red is 4.1's.

### 2.5 `tests/test_docs_structure.py` (task 2.5)

`KernelExtrasTest.test_the_installation_page_names_the_engine_distributions`.

```
$ ... pytest tests/test_docs_structure.py
2 failed, 17 passed, 761 subtests passed in 0.36s
```

Both subtests: `'machinome-engine-brep' not found in 'Install\n=======...`
(and `-mesh`).

### 2.6 The engine tests (task 2.6)

`ENGINE_SOURCE = Path(importlib.util.find_spec('machinome.engine.brep').origin)`
in `test_brep_engine.py`, and `.mesh` in `test_mesh_engine.py`, with
`import importlib.util`.

```
$ ... pytest tests/test_brep_engine.py tests/test_mesh_engine.py
20 passed in 2.51s
```

Green, as expected; their red without this edit is design.md probe 5
(`FileNotFoundError` on `ENGINE_SOURCE` at the move).

## 3. The cut

### 3.1 The move (task 3.1)

```
$ mkdir -p <bench>/packages/machinome-engine-brep/machinome/engine <bench>/packages/machinome-engine-mesh/machinome/engine
$ env -C <bench> git mv packages/machinome/machinome/engine/brep.py packages/machinome-engine-brep/machinome/engine/brep.py
$ env -C <bench> git mv packages/machinome/machinome/engine/mesh.py packages/machinome-engine-mesh/machinome/engine/mesh.py
$ git -C <bench> diff --cached -M --stat
 packages/{machinome => machinome-engine-brep}/machinome/engine/brep.py | 0
 packages/{machinome => machinome-engine-mesh}/machinome/engine/mesh.py | 0
```

Both renames, no content change.

### 3.2 The links (task 3.2)

`ln -s ../../LICENSE LICENSE` and `ln -s ../../LICENSES LICENSES` in each
engine directory, then `git add`:

```
$ git -C <bench> ls-files -s packages/machinome-* | grep ^120000
120000 30cff740... 0	packages/machinome-engine-brep/LICENSE
120000 06ad40db... 0	packages/machinome-engine-brep/LICENSES
120000 30cff740... 0	packages/machinome-engine-mesh/LICENSE
120000 06ad40db... 0	packages/machinome-engine-mesh/LICENSES
```

`git cat-file -p` of the blobs: `../../LICENSE`, `../../LICENSES` (the same
two blobs as the framework's own links).

### 3.3 The moved tree before the manifests (task 3.3)

The bench venv's `.pth` still names the framework's directory alone.

```
$ ... pytest tests/test_repository_layout.py tests/test_core_kernel_free.py tests/test_brep_engine.py tests/test_mesh_engine.py
2 errors in 1.43s
E   AttributeError: 'NoneType' object has no attribute 'origin'
```

The two engine modules fail at collection: `find_spec` finds no
`machinome.engine.brep` (nor `.mesh`), the provider not being on the path
until the sync of 4.5. A collection error stops the run, so the other two
modules ran apart:

```
$ ... pytest tests/test_repository_layout.py tests/test_core_kernel_free.py
17 failed, 35 passed, 96 subtests passed in 4.95s
```

(`<scratch>/3.3-moved-b.txt`.) `test_core_kernel_free.py` is green whole:
the core's census no longer finds the engines, the portion census finds
`brep.py: ['OCP']` and `mesh.py: ['manifold3d']`, and the `require_extra`
test reads both portions. The layout gate:

- `test_every_member_is_a_workspace_source`: `{'machinome': ...} !=
  {'machinome': ..., 'machinome-engine-brep': ..., 'machinome-engine-mesh':
  ...}` (two directories, no source).
- `test_the_members_are_the_package_directories`, both engine subtests:
  `<bench>/packages/machinome-engine-brep holds no pyproject.toml` (and
  `-mesh`); a G4 red the task's list does not name, for the same cause as
  the manifest test.
- `test_the_readme_links_every_package_and_states_the_licence`, both:
  `'packages/machinome-engine-brep/' not found` (probe 5).
- `test_each_engine_directory_holds_only_what_distinguishes_it`, both: the
  listing is `['LICENSE', 'LICENSES', 'machinome/engine/brep.py']`, without
  `README.md` and `pyproject.toml`. Its link and `__init__.py` checks sit in
  the same method, after the listing.
- `test_each_engine_manifest_is_a_portion_of_the_set` and
  `test_each_engine_readme_names_its_install_and_the_licence`, both
  subtests each: `FileNotFoundError` on `pyproject.toml` and `README.md`.
- `test_each_provider_resolves_from_its_package`, both:
  `ModuleNotFoundError: No module named 'machinome.engine.brep'` (and mesh).
- `test_the_guide_installs_every_member_without_uv`: `editable_mode=compat`,
  `-e packages/machinome-engine-brep`, `-e packages/machinome-engine-mesh`
  and `tox`.
- `test_the_core_engine_package_holds_only_the_seams`: green.

## 4. The manifests and the workspace

### 4.1 The manifests (task 4.1)

`packages/machinome-engine-brep/pyproject.toml` and
`packages/machinome-engine-mesh/pyproject.toml`: design.md Decision 2,
verbatim.

```
$ ... pytest tests/test_release_records.py
2 failed, 11 passed, 61 subtests passed in 0.28s
```

The two `.bumpversion.cfg` reds of 2.4 remain; the member and pin tests are
green with three members. The pin test's red, by an edit of the B-rep
manifest's pin to `machinome>=0.8.1`:

```
$ ... pytest tests/test_release_records.py::VersionFilesTest::test_every_pin_between_members_is_compatible
1 failed, 1 passed, 1 subtests passed in 0.12s
AssertionError: '>=0.8.1' != '~=0.8.1' : machinome>=0.8.1
SUBFAILED(member='machinome-engine-brep', requirement='machinome>=0.8.1')
```

The pin restored; `diff` against a copy of 4.1's text taken before the edit:
identical. The member test's red likewise, by the mesh manifest's version
edited to `0.8.2`: `AssertionError: '0.8.2' != '0.8.1'`, subtest
`member='machinome-engine-mesh'`; restored, `diff` identical.

### 4.2 The READMEs (task 4.2)

The two `README.md`: design.md Decision 2, verbatim. The four new files were
`git add`ed.

### 4.3 The framework's manifest (task 4.3)

The `brep` and `mesh` extras and their comments of Decision 3, verbatim; the
kernel extras' comment "so the OCCT range, stated once in
machinome-engine-brep, resolves one OCCT binding for several extras"; the
`dependencies` comment "the B-rep engine (the extra `brep`), the mesh engine
(the extra `mesh`)". Each comment rewrapped at the file's width; `git diff`
shows those three places alone.

### 4.4 The docstring (task 4.4)

`machinome._namespace_portions`: "Nothing uses the extension yet; no such
distribution exists (OpenSpec change `lean-install`)." became "The engines'
distributions, `machinome-engine-brep` and `machinome-engine-mesh`, are the
first such portions (OpenSpec change `cut-the-engines`)."; `git diff` of
`machinome/__init__.py` shows the docstring alone.

### 4.5 The workspace (task 4.5)

The root `pyproject.toml`'s sources of Decision 4.

```
$ env -C <bench> /home/asa/.local/bin/uv lock
Resolved 187 packages in 742ms
Added machinome-engine-brep v0.8.1
Added machinome-engine-mesh v0.8.1
$ grep -c '^\[\[package\]\]' <bench>/uv.lock
187
$ grep -n 'source = { editable = "packages/' <bench>/uv.lock
1826:source = { editable = "packages/machinome" }
1968:source = { editable = "packages/machinome-engine-brep" }
1985:source = { editable = "packages/machinome-engine-mesh" }
```

`diff` of the lock against the base's: 60 changed lines, the two new
`[[package]]` entries, the framework's extras naming the engines in place of
`cadquery-ocp` and `manifold3d`, and the two engines in the root's dev
group's closure. The lock records the engines' requirement of `machinome` as
`editable = "packages/machinome"`, the workspace source, not the `~=` pin.

```
$ env -C <bench> /home/asa/.local/bin/uv sync --python 3.12
Resolved 187 packages in 4ms
   Built machinome-engine-mesh @ file://<bench>/packages/machinome-engine-mesh
   Built machinome-engine-brep @ file://<bench>/packages/machinome-engine-brep
   Built machinome @ file://<bench>/packages/machinome
Prepared 3 packages in 1.54s
Uninstalled 1 package in 3ms
Installed 3 packages in 12ms
 ~ machinome==0.8.1
 + machinome-engine-brep==0.8.1
 + machinome-engine-mesh==0.8.1
$ uv pip list --python <bench>/.venv/bin/python | tail -n +3 | wc -l
177
```

The sync was incremental on the venv of 1.2: three installed, 177 in the
venv, design.md probe 1's count for a fresh sync. The three `.pth` files,
one line each:

```
__editable__.machinome-0.8.1.pth: <bench>/packages/machinome
__editable__.machinome_engine_brep-0.8.1.pth: <bench>/packages/machinome-engine-brep
__editable__.machinome_engine_mesh-0.8.1.pth: <bench>/packages/machinome-engine-mesh
```

From `/tmp`, with the venv's Python:

```
__path__ ['<bench>/packages/machinome/machinome/engine', '<bench>/packages/machinome-engine-brep/machinome/engine', '<bench>/packages/machinome-engine-mesh/machinome/engine']
brep <bench>/packages/machinome-engine-brep/machinome/engine/brep.py 2 2
mesh <bench>/packages/machinome-engine-mesh/machinome/engine/mesh.py 1 1
True True                 (from machinome.engine import brep, mesh: the seams' modules)
999.9999999999998         (solid_volume of a 10 mm OCCT box)
24.0 manifold3d           (volume(centred_box([2, 3, 4])), identity()[0])
```

### 4.6 The root `.gitignore` (task 4.6)

Decision 4's text, verbatim. Before it, `git status --short` listed
`packages/machinome-engine-brep/machinome_engine_brep.egg-info/` and the mesh
one as untracked; after it, neither, and `git status --short --ignored` lists
both under `!!`.

### 4.7 The split-words gate (task 4.7)

A comment `# plant: a <the mesh-quality word> run` appended to the moved
`mesh.py`. The gate as it was (scanning the framework's `machinome/` alone):

```
$ ... pytest tests/test_core_names_no_split_words.py
11 passed, 56 subtests passed in 0.88s
```

The gate repointed: `REPOSITORY = parents[3]`, the gate test scanning
`ROOT` and every `packages/machinome-*` directory; the docstring names the
extension packages.

```
$ ... pytest tests/test_core_names_no_split_words.py
1 failed, 10 passed, 56 subtests passed in 0.96s
AssertionError: {'machinome/engine/mesh.py': (1, [(131, '# plant: a ... run')])} != {}
   1 machinome/engine/mesh.py (131: '# plant: a ... run')
modules: 1  occurrences: 1
```

The plant removed (the file copied back from a copy taken before it): `git
diff` of `mesh.py` empty, `git diff --cached -M` still a rename with no
change. Then green: `11 passed, 56 subtests passed in 0.77s`.

### 4.8 Group 2's modules and the seams (task 4.8)

```
$ ... pytest tests/test_repository_layout.py tests/test_kernel_extras.py tests/test_core_kernel_free.py tests/test_release_records.py tests/test_docs_structure.py tests/test_brep_engine.py tests/test_mesh_engine.py tests/test_core_names_no_split_words.py tests/test_engine_package.py tests/test_brep_engine_seam.py tests/test_mesh_engine_seam.py tests/test_brep_engine_dependency.py tests/test_mesh_engine_dependency.py
13 failed, 166 passed, 1121 subtests passed in 64.86s
```

Every red the task expects and no other: the layout README test (two
subtests, group 8) and guide test (four subtests, group 8);
`test_kernel_extras.py`'s CI test (three subtests, group 6);
`test_release_records.py`'s two bumpversion tests (group 5);
`test_docs_structure.py`'s page test (two subtests, group 8).

## 5. One version for the set

### 5.1 The root `.bumpversion.cfg` (task 5.1)

Decision 5's text, verbatim, `git add`ed. `packages/machinome/setup.cfg` lost
its `[bumpversion]` table and its four `[bumpversion:file:...]` tables (21
lines), keeping `[flake8]` whole; `machinome/vet/universe.toml`'s comment now
reads "the root's `.bumpversion.cfg` rewrites it with the others on a
release".

### 5.2 The dry run (task 5.2)

```
$ env -C <bench> <bench>/.venv/bin/bump2version --dry-run --allow-dirty --verbose --new-version 0.9.0 patch
Reading config file .bumpversion.cfg:
...
New version will be '0.9.0'
Asserting files packages/machinome/pyproject.toml, packages/machinome/pyproject.toml, packages/machinome/machinome/__init__.py, packages/machinome/docs/conf.py, packages/machinome/machinome/vet/universe.toml, packages/machinome-engine-brep/pyproject.toml, packages/machinome-engine-brep/pyproject.toml, packages/machinome-engine-mesh/pyproject.toml, packages/machinome-engine-mesh/pyproject.toml contain the version string...
Would add changes in file 'packages/machinome/pyproject.toml' to Git   (twice: the version and the pins tables)
Would add changes in file 'packages/machinome/machinome/__init__.py' to Git
Would add changes in file 'packages/machinome/docs/conf.py' to Git
Would add changes in file 'packages/machinome/machinome/vet/universe.toml' to Git
Would add changes in file 'packages/machinome-engine-brep/pyproject.toml' to Git   (twice)
Would add changes in file 'packages/machinome-engine-mesh/pyproject.toml' to Git   (twice)
Would add changes in file '.bumpversion.cfg' to Git
Would commit to Git with message 'Bump version: 0.8.1 → 0.9.0'
Would tag 'v0.9.0' with message 'Bump version: 0.8.1 → 0.9.0' in Git and not signing
```

exit 0 (`<scratch>/5.2-bump.txt`); `git status --short` before and after:
identical, nothing written. The installed bump2version (1.0.1) prints no
per-statement diff on a dry run, so the statements were read from a real
run on a scratch copy (`<scratch>/bump/`: the seven files, a git repository,
`bump2version --no-commit --no-tag --new-version 0.9.0 patch`, exit 0), whose
`git diff -U0` moved these eleven statements of the nine tables and nothing
else in a versioned file:

```
.bumpversion.cfg                              current_version = 0.8.1 -> 0.9.0
packages/machinome/pyproject.toml             version = "0.8.1"; "machinome-engine-brep~=0.8.1"; "machinome-engine-mesh~=0.8.1"
packages/machinome/machinome/__init__.py      __version__ = "0.8.1"
packages/machinome/docs/conf.py               release = '0.8.1'
packages/machinome/machinome/vet/universe.toml version = "0.8.1"
packages/machinome-engine-brep/pyproject.toml version = "0.8.1"; "machinome~=0.8.1"
packages/machinome-engine-mesh/pyproject.toml version = "0.8.1"; "machinome~=0.8.1"
```

The viewer floors (`machinome-viewer>=0.8.1`) did not move. One more change
the real run made: bump2version rewrote `.bumpversion.cfg` through its
configuration writer and dropped the file's three-line header comment
(`git diff`: `-# One version for every package ...` and its two following
lines). design.md probe 7 reports "nothing else changed"; this run shows the
comment does not survive a real bump (departure 5).

### 5.3 (task 5.3)

```
$ ... pytest tests/test_release_records.py
13 passed, 70 subtests passed in 0.17s
```

## 6. CI, the lint and the retirements

### 6.1 The workflow (task 6.1)

`.github/workflows/python-app.yml`: the `lint`, `test` and `browser-snapshot`
jobs take the `Setup uv` and `Sync the workspace` steps of Decision 6
verbatim in place of their `actions/setup-python` step and their
requirements install (in `browser-snapshot`, at the place of its
`setup-python` step, before `actions/setup-node`); the browser-snapshot
install step and the two lint steps verbatim; the `build` job's install step
`pip install build`. Beyond Decision 6: the `build` job's `setup-python`
step lost its `cache: "pip"` and `cache-dependency-path` lines, which named
the two retired requirements files (departure 3). `docs` and `dist`
unchanged.

```
$ python -c "import yaml; ..."
['lint', 'test', 'browser-snapshot', 'docs', 'dist', 'build']
lint ['actions/checkout@v4', 'Setup uv', 'Sync the workspace', 'Black', 'Flake8']
test ['actions/checkout@v4', 'awalsh128/cache-apt-pkgs-action@latest', 'Setup uv', 'Sync the workspace', 'Run tests']
browser-snapshot ['actions/checkout@v4', 'awalsh128/cache-apt-pkgs-action@latest', 'Setup uv', 'Sync the workspace', 'actions/setup-node@v4', 'Install the browser snapshot dependencies', 'Run real browser snapshot test']
docs ['actions/checkout@v4', 'Setup Python', 'Install docs requirements', 'Build docs (fail on warnings)']
dist ['actions/checkout@v4', 'Setup Python', 'Install build and twine', 'Check the distributions']
build ['actions/checkout@v4', 'Setup Python', 'Install packaging', 'Detect package version', 'Install requirements', 'Build python package', 'Create release']
$ ... pytest tests/test_kernel_extras.py::KernelMetadataTest::test_ci_syncs_the_locked_workspace tests/test_docs_exports.py tests/test_repository_layout.py::TheContinuousIntegrationTest
23 passed, 23 subtests passed in 0.68s
```

### 6.2 The lint (task 6.2)

Before the edit, over the three packages:

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/flake8 --max-line-length=89 machinome tests ../machinome-engine-brep/machinome ../machinome-engine-mesh/machinome | wc -l
785
```

26 E402 in the two engines (24 in `brep.py`, 2 in `mesh.py`, design.md probe
6). `setup.cfg`'s two engine entries spelled
`../machinome-engine-brep/machinome/engine/brep.py:E402` and
`../machinome-engine-mesh/machinome/engine/mesh.py:E402`; the same command:

```
759
```

No line names an engine path (0 E402, 0 of any code); the sorted list equals
1.3's line for line.

### 6.3 The Makefile (task 6.3)

`test-all` and `clean-test`'s `rm -fr .tox/` removed; `lint/flake8` and
`lint/black` over `machinome tests ../machinome-*/machinome`.

```
$ env PATH=<bench>/.venv/bin:$PATH make -C <bench>/packages/machinome lint/flake8
flake8 machinome tests ../machinome-*/machinome
...
make: *** [Makefile:50: lint/flake8] Error 1
```

1510 warnings (the Makefile passes no `--max-line-length`, so flake8's 79
applies), exit 2 as before. The base's tree (`git archive 6fb505ed` of the
framework's `machinome`, `tests` and `setup.cfg`, `flake8 machinome tests`):
1510. The two lists, paths normalised for the move and line numbers
dropped, were equal once one line of this change's own
`test_kernel_extras.py` (80 columns) was rewrapped; the engines contribute
the base's two E501 lines of `brep.py`.

### 6.4 The retirements (task 6.4)

```
$ env -C <bench> git rm packages/machinome/requirements.txt packages/machinome/requirements_dev.txt packages/machinome/tox.ini
$ grep -rn "requirements_dev\|tox" <bench>/packages/machinome --include=*.py --include=*.cfg --include=*.toml --include=Makefile --include=*.yml
packages/machinome/pyproject.toml:54:    "tox>=4",
packages/machinome/tests/test_repository_layout.py:47:    'CREDITS.md', 'MANIFEST.in', 'setup.cfg', 'tox.ini', 'Makefile',
packages/machinome/tests/test_repository_layout.py:48:    'requirements.txt', 'requirements_dev.txt', '.readthedocs.yaml',
packages/machinome/tests/test_repository_layout.py:360:        for retired in (r'\btox\b', r'requirements\.txt'):
$ grep -rn "requirements_dev\|tox" <bench>/.github <bench>/CONTRIBUTING.rst <bench>/scripts
CONTRIBUTING.rst:130:    $ make test-all      # tox across supported Python versions
```

The `CONTRIBUTING.rst` line went in task 8.5 (after it: no hit). Lines 47-48
are the layout gate's list of entries the root must not hold; line 360 is the
guide test's list of what the guide must not name. The `dev` extra's
`"tox>=4"` is a hit the task does not expect: design.md Decision 3 keeps
`dev` unchanged, so it stays, and is reported (departure 4). Outside the
task's globs: `docs/project/changelog.rst:1230` (history) and the framework's
`.gitignore`'s `.tox/` line.

## 7. `scripts/check-dist`

### 7.1 Red first (task 7.1)

```
$ env -C <bench> <bench>/.venv/bin/python scripts/check-dist
check-dist failed: machinome-engine-brep has no smoke in scripts/check-dist
Nothing uploaded.
```

exit 1.

### 7.2 The rows (task 7.2)

`LICENCES`, a `string.Template` of the licence lines formatted with the
distribution's name; `ENGINE`, the template of an engine's smoke (steps 1 to
4 of Decision 7) and `ENGINE_LINE`, its one printed line; `engine_smoke()`
joining them; the rows `machinome-engine-brep` and `machinome-engine-mesh`
with `'through'`, `'extras': []`, `'commands': []`; the install building
`machinome[<through>]` for a row with `through`. `git diff -U0` of the
script: hunks at the docstring's last sentence (below), the `string` import,
the new templates, the `SMOKES` comment, the two rows after the core's, and
the install loop; no line of the core's row changed. The docstring's "which
each member's `.gitignore` ignores" became "which each member's
`.gitignore`, or the root's, ignores": the engines keep no `.gitignore`
(departure 6). `flake8 --max-line-length=89 scripts/check-dist`: 0; at 79
columns, the base's two lines of the core's row.

### 7.3 The run (task 7.3)

```
$ env -C <bench> <bench>/.venv/bin/python scripts/check-dist
Members: machinome, machinome-engine-brep, machinome-engine-mesh
... twine check --strict: six archives PASSED
   machinome-0.8.1/AI-USE.md: regular file, 5190 bytes, equal to the root's
   machinome-0.8.1/CONTRIBUTING.rst: regular file, 10453 bytes, equal to the root's
   machinome-0.8.1/HISTORY.rst: regular file, 91724 bytes, equal to the root's
   machinome-0.8.1/LICENSE: regular file, 793 bytes, equal to the root's
   machinome-0.8.1/LICENSES/CERN-OHL-S-2.0.txt: regular file, 13419 bytes, equal to the root's
   machinome-0.8.1/LICENSES/GPL-2.0-or-later.txt: regular file, 17984 bytes, equal to the root's
   machinome-0.8.1.tar.gz: 1046 entries
   machinome-0.8.1-py3-none-any.whl: 126 entries
   machinome_engine_brep-0.8.1/LICENSE: regular file, 793 bytes, equal to the root's
   machinome_engine_brep-0.8.1/LICENSES/CERN-OHL-S-2.0.txt: regular file, 13419 bytes, equal to the root's
   machinome_engine_brep-0.8.1/LICENSES/GPL-2.0-or-later.txt: regular file, 17984 bytes, equal to the root's
   machinome_engine_brep-0.8.1.tar.gz: 18 entries
   machinome_engine_brep-0.8.1-py3-none-any.whl: 8 entries
   (the mesh engine's three files likewise)
   machinome_engine_mesh-0.8.1.tar.gz: 18 entries
   machinome_engine_mesh-0.8.1-py3-none-any.whl: 8 entries
$ <tmp>/venv/bin/python -m pip install --quiet --find-links <tmp>/dist/machinome --find-links <tmp>/dist/machinome-engine-brep --find-links <tmp>/dist/machinome-engine-mesh <tmp>/dist/machinome/machinome-0.8.1-py3-none-any.whl[openscad,stl] machinome[brep] machinome[mesh]
machinome 0.8.1 from <tmp>/venv/lib/python3.12/site-packages/machinome/__init__.py
License-Expression: GPL-2.0-or-later OR CERN-OHL-S-2.0+   (and the three licence files)
   machinome --help: exit 0
License-Expression: GPL-2.0-or-later OR CERN-OHL-S-2.0+
   licenses/LICENSE
   licenses/LICENSES/CERN-OHL-S-2.0.txt
   licenses/LICENSES/GPL-2.0-or-later.txt
machinome-engine-brep 0.8.1 provider <tmp>/venv/lib/python3.12/site-packages/machinome/engine/brep.py contract 2 result 999.9999999999998
License-Expression: GPL-2.0-or-later OR CERN-OHL-S-2.0+
   (the three licence files)
machinome-engine-mesh 0.8.1 provider <tmp>/venv/lib/python3.12/site-packages/machinome/engine/mesh.py contract 1 result 24.0
Every distribution built, checked, installed and smoked; nothing uploaded.
```

exit 0 (`<scratch>/7.3-check-dist.txt`); `<tmp>` is
`/tmp/machinome-check-dist-2gouqpno`, removed at the end. The wheel counts
equal design.md probe 3's (126; 8 and 8) and so do the engines' sdists (18).
The framework's sdist holds 1046 entries on the bench, the suite's and the
earlier runs' ignored leavings under `tests/` swept in by `MANIFEST.in`, as
the first cycle's 7.4 found; the clean copy's count is 9.4's. `git status
--short --ignored` before and after the run: identical.

## 8. The records

- 8.1 `HISTORY.rst`: Decision 10's bullet, verbatim, after the first
  cycle's under `Unreleased`.
- 8.2 `docs/project/changelog.rst`: Decision 10's `Unreleased` section,
  verbatim, above `Machinome 0.8.1`.

  ```
  $ ... pytest tests/test_release_records.py tests/test_profile_documentation.py
  15 passed, 70 subtests passed in 0.22s
  ```
- 8.3 `docs/start/install.rst`: the `brep` and `mesh` rows' third cells and
  the section "Packages and licences" with its first sentence, Decision 10's
  text; each rewrapped at the page's width, the rest of the page unchanged.
  `tests/test_docs_structure.py`: `17 passed, 763 subtests passed`.
- 8.4 The root `README.md`: Decision 10's two rows after the framework's.
- 8.5 `CONTRIBUTING.rst`: the uv sentence, the sentence before the pip block
  and the block's last line (three lines, Decision 10's text), in place; the
  `make test-all` line removed. Nothing else; the Deploying section still
  reads `$ cd packages/machinome` before `$ bump2version patch` (departure
  7).

  ```
  $ ... pytest tests/test_repository_layout.py
  26 passed, 86 subtests passed in 1.86s
  ```
- 8.6 `docs/architecture.md`: the two engine rows and the "Repository
  layout" row of the Map, Decision 10's text. `grep -n "leaves the core"`
  found only those two engine rows and the OpenSCAD family's (a later
  cycle's). One more engine sentence, which that grep does not find, said
  the future: "so a provider cut from the core later installs its module
  there" (line 598) became "so each provider, shipped by its own
  distribution (`machinome-engine-brep`, `machinome-engine-mesh`, ADR-183),
  installs its module there", the paragraph's next three lines rewrapped
  (departure 8).
- 8.7 `docs/adrs/BUILD/ADR-183-an-extension-package-is-a-namespace-portion-in-its-own-distribution.md`,
  Status **Proposed**, Date 2026-10-10, Change `cut-the-engines`, amending
  ADR-167, related to ADR-182 and ADR-180; its entry under BUILD after
  ADR-182 in `docs/adrs/README.md`, and the OCCT heading "(the distribution
  `machinome-engine-brep`, ADR-183)".
- 8.8 The whole gate and the docs and release tests:

  ```
  $ ... pytest tests/test_repository_layout.py tests/test_docs_structure.py tests/test_docs_exports.py tests/test_release_records.py tests/test_profile_documentation.py
  76 passed, 933 subtests passed in 2.66s
  ```

## 9. Validation

### 9.1 The whole suite on the bench venv (task 9.1)

One process, from the framework's directory, in the background, its output
in `<scratch>/9.1-suite.txt`:

```
$ env -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python -m pytest -q -rs -p no:cacheprovider
1 failed, 4785 passed, 20 skipped, 55 warnings, 6831 subtests passed in 889.04s (0:14:49)
```

**A red the design did not foresee, investigated.**
`tests/test_vet_universe.py::PackagingTest::test_bumpversion_rewrites_the_declared_version`:
`AssertionError: 'bumpversion:file:machinome/vet/universe.toml' not found in
['flake8']`. The test reads the universe file's bumpversion table from the
framework's `setup.cfg`, which Decision 5 empties of its version tables;
design.md probe 5 ran on a tree without Decision 5, so it could not see it,
and Decision 9 does not list the module. The test was repointed, in place:
`REPOSITORY = os.path.dirname(os.path.dirname(REPO))`, the configuration
read from `REPOSITORY/.bumpversion.cfg`, the section
`bumpversion:file:packages/machinome/machinome/vet/universe.toml`; the rest of
the test unchanged (departure 1). The failing run is its red; then
`tests/test_vet_universe.py`: `14 passed, 7 subtests passed`. The whole suite
again (`<scratch>/9.1-suite-2.txt`):

```
4786 passed, 20 skipped, 55 warnings, 6831 subtests passed in 665.28s (0:11:05)
```

No failure. 4786 is the base's 4774, less the two tests removed in 2.2, plus
the sixteen this change adds (the layout gate's six G9 tests and
`test_every_member_is_a_workspace_source`; `test_kernel_extras.py`'s four;
`test_core_kernel_free.py`'s one; `test_release_records.py`'s three;
`test_docs_structure.py`'s one), less the two G4 tests folded into the
generalised one: 4774 - 2 + 16 - 2 = 4786. Subtests 6831, the base's 6799
plus 32. The 20 skips, the base's:

```
14 tests/test_browser_renderer.py: machinome-viewer not installed (pip install "machinome[viewer]")
 1 tests/test_cli_lazy_imports.py: machinome-viewer not installed
 1 tests/test_scad_presentation.py: machinome-viewer not installed (pip install "machinome[viewer]")
 1 tests/test_connectivity.py: the repairing split needs networkx, which machinome does not install
 1 tests/test_jscad_integration.py: jscad CLI is not installed
 2 tests/test_step_assembly.py: Internal-Cycloidal-Actuator vendor STEP not present
```

The fallback recipe was not run (design.md, Risks).

### 9.2 The lint on the final tree (task 9.2)

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/flake8 --max-line-length=89 machinome tests ../machinome-engine-brep/machinome ../machinome-engine-mesh/machinome | wc -l
759
```

Sorted, equal to 1.3's list line for line; no line names an engine path.

### 9.3 The manual (task 9.3)

```
$ /usr/bin/python3.12 -m venv <scratch>/docs-venv
$ <scratch>/docs-venv/bin/pip install -q -r <bench>/packages/machinome/docs/requirements.txt
(Sphinx 9.1.0, sphinx_rtd_theme 3.1.0, machinome-viewer 0.8.0 from the index)
$ env -C <bench>/packages/machinome <scratch>/docs-venv/bin/python -m sphinx -b html -W docs <scratch>/html
build succeeded.
```

54 HTML pages under `<scratch>/html`.

### 9.4 `scripts/check-dist` on the final tree and on a clean copy (task 9.4)

On the bench (`<scratch>/9.4-bench.txt`), exit 0: the three members built,
six archives `PASSED`, every linked file a regular file equal to the root's
(`CONTRIBUTING.rst` 10595 bytes and `HISTORY.rst` 92466, this change's
edits), the install line of 7.3, the three smokes and `machinome --help`
exit 0, "Every distribution built, checked, installed and smoked; nothing
uploaded."

```
   machinome-0.8.1.tar.gz: 1075 entries
   machinome-0.8.1-py3-none-any.whl: 126 entries
   machinome_engine_brep-0.8.1.tar.gz: 18 entries
   machinome_engine_brep-0.8.1-py3-none-any.whl: 8 entries
   machinome_engine_mesh-0.8.1.tar.gz: 18 entries
   machinome_engine_mesh-0.8.1-py3-none-any.whl: 8 entries
machinome-engine-brep 0.8.1 provider <tmp>/venv/lib/python3.12/site-packages/machinome/engine/brep.py contract 2 result 999.9999999999998
machinome-engine-mesh 0.8.1 provider <tmp>/venv/lib/python3.12/site-packages/machinome/engine/mesh.py contract 1 result 24.0
```

`git status --short --ignored` before and after: identical. The same script
on a clean copy of the tracked tree (`git ls-files -z | tar --null -T - -cf
-` unpacked in `<scratch>/clean/`, links kept as links;
`<scratch>/9.4-clean.txt`), exit 0, the same lines but:

```
   machinome-0.8.1.tar.gz: 1019 entries
```

1019 and 126, design.md probe 3's counts for the framework (the first
cycle's 1021 and 128 less the two modules); 18 and 8 for each engine. The
bench's 1075 is the clean 1019 plus the suite's ignored leavings under
`tests/`, which `MANIFEST.in` sweeps in.

### 9.5 The universe sweep (task 9.5)

Decision 12's command, in the background (`<scratch>/9.5-sweep.txt`, JSON
`<scratch>/load-projects.json`):

```
$ /home/asa/devel/machinome/.venv/bin/python /home/asa/devel/machinome/scripts/load-projects \
  --bench <bench>/packages/machinome --python <bench>/.venv/bin/python \
  --moved /home/asa/devel/machinome/scripts/load-projects.d/*.toml \
  --timeout 300 --json <scratch>/load-projects.json
63 repositories, 130 rows: 50 ok, 0 expected, 74 unexpected, 0 timeout, 6 no-model; 2 skipped
```

exit 1. Against `root-cleanup`'s 62 repositories, 129 rows, 121 ok, 2
unexpected, 6 no-model (its `load-projects.json` in the archive, compared
row by row):

- **One new row**, `Code-Atlanticus` model `ca1078r-sawmill` (checkout
  `main+dirty`): a repository added to the catalogue since 5 October 2026,
  not a change of this cycle. It is the 63rd repository and the 130th row.
- **72 rows ok at the base are unexpected here**, and 73 rows in all fail
  with `ModuleNotFoundError: No module named 'machinome_mechanics'`
  (wall_clock_41 among them, failing on it before its own error). The bench
  venv is the uv sync of the lock, whose default group installs the
  framework's `dev` extra; `dev` includes `all`, and `all` does not include
  the `mechanics` extra, so `machinome-mechanics` is locked but not
  installed. `root-cleanup` ran its sweep on the workspace venv, which has
  `machinome-mechanics` 0.1.0 editable from the workspace's checkout.
- The 74th unexpected row is Dum-E, the base's (`No module named
  'machinome_freecad'` at `simulation/dume.py:7`, identical).

Not worked around: the counts above are this task's result. To find whether
anything beyond the environment differs, one diagnostic run, the same
command with `PYTHONPATH=/home/asa/devel/machinome/machinome-mechanics` (the
workspace's checkout, read only; `load-projects` puts the bench first and
keeps the caller's `PYTHONPATH` after it), JSON
`<scratch>/load-projects-diag.json`:

```
63 repositories, 130 rows: 121 ok, 0 expected, 3 unexpected, 0 timeout, 6 no-model; 2 skipped
```

Row by row against the base: one row differs, `3D-Printers/fender-bender`,
ok at the base, here `ModuleNotFoundError: No module named 'fb_library'` at
`src/bender_config.py:12`. `fb-library` 0.0.41, that project's own
dependency, is installed in the workspace venv and not in the bench venv: an
environment fact again. The other two unexpected rows are the base's:
Dum-E, identical, and wall_clock_41, the same
`ValueError: Workplane object must have at least one solid on the stack to
union!`, now reported wrapped as `machinome.parameters.ParameterError:
Movement.wound_weight_seat: frame argument at -- the callable raised ...`
(the base's line was raised at `clocks/plates.py:5224`; the wrapping is the
line's, not this change's, which touches no parameter code). The new
`ca1078r-sawmill` row is ok. So, the two missing environment packages
aside, every row loads as at the base. No row names an engine module or the
moved files.

The sweep's recipe of Decision 12 does not reproduce the base's environment
on a bench venv: a project that imports `machinome_mechanics` or a
third-party package of its own fails there before the framework is
exercised (departure 9).

### 9.6 Git (task 9.6)

```
$ git -C <bench> status --short | cut -c1-2 | sort | uniq -c
     26  M
      1 ??
     10 A
      3 D
      2 R
$ git -C <bench> ls-files | wc -l
3377
$ git -C <bench> ls-files -ci --exclude-standard | wc -l
34
```

- `R`: `brep.py` and `mesh.py`, renamed with no change.
- `A`: the five files of each engine directory (`LICENSE` and `LICENSES`
  with mode 120000, `README.md`, `pyproject.toml`; the module is the rename),
  so four added in each, plus `.bumpversion.cfg` and ADR-183: 10.
- `D`: `requirements.txt`, `requirements_dev.txt`, `tox.ini`.
- ` M`: the 26 edited files: `.github/workflows/python-app.yml`, `.gitignore`,
  `CONTRIBUTING.rst`, `HISTORY.rst`, `README.md`, `pyproject.toml`,
  `uv.lock`, `scripts/check-dist`, and under `packages/machinome/`:
  `Makefile`, `pyproject.toml`, `setup.cfg`, `machinome/__init__.py`,
  `machinome/vet/universe.toml`, `docs/adrs/README.md`,
  `docs/architecture.md`, `docs/project/changelog.rst`,
  `docs/start/install.rst`, and nine tests (`test_brep_engine.py`,
  `test_core_kernel_free.py`, `test_core_names_no_split_words.py`,
  `test_docs_structure.py`, `test_kernel_extras.py`, `test_mesh_engine.py`,
  `test_release_records.py`, `test_repository_layout.py`,
  `test_vet_universe.py`).
- `??`: this `evidence.md`.

3377 is the planning commit's 3370 files plus the 10 added less the 3
deleted.

### 9.7 OpenSpec (task 9.7)

```
$ env -C <bench>/packages/machinome openspec validate cut-the-engines --strict
Change 'cut-the-engines' is valid
```

## Departures from the design, to the checkpoint (task 9.8)

1. **`tests/test_vet_universe.py` repointed** (9.1): its
   `test_bumpversion_rewrites_the_declared_version` read the universe
   file's bumpversion table from the framework's `setup.cfg`; it now reads
   the root's `.bumpversion.cfg` and the table
   `bumpversion:file:packages/machinome/machinome/vet/universe.toml`.
   Decision 9 and task 9.6's list of edited files do not name the module.
2. **`test_no_module_reaches_trimesh_boolean` reads the portions too**
   (2.3): beyond Decision 9's list, so the moved mesh provider stays under
   the `trimesh.boolean` scan it was under at the base.
3. **The CI `build` job's `setup-python` step** (6.1) lost its `cache` and
   `cache-dependency-path` lines, which named the two retired requirements
   files (the layout gate's `test_every_cache_path_names_a_file` would fail,
   and setup-python's pip cache fails with no matching file).
4. **The framework's `dev` extra still requires `"tox>=4"`** (6.4):
   Decision 3 keeps `dev` unchanged, so task 6.4's grep finds it, a hit the
   task does not expect. Removing it changes the lock (one package fewer,
   and its own dependencies); not done, for the review.
5. **A real bump drops `.bumpversion.cfg`'s header comment** (5.2):
   bump2version 1.0.1 rewrites the configuration through its writer, so the
   three comment lines of Decision 5's text do not survive a release's bump.
   The statements it moves are exactly the eleven of probe 7.
6. **`scripts/check-dist`'s docstring** (7.2): "which each member's
   `.gitignore` ignores" became "which each member's `.gitignore`, or the
   root's, ignores", the engines keeping none.
7. **`CONTRIBUTING.rst`'s Deploying section** still reads
   `$ cd packages/machinome` before `$ bump2version patch` (8.5): Decision
   10 says nothing else changes, but with the version table at the root that
   command now finds no configuration; the bump runs from the root. Left as
   designed, for the review.
8. **`docs/architecture.md` line 598** (8.6): "so a provider cut from the
   core later installs its module there" corrected to the engines'
   distributions; Decision 10's grep (`leaves the core`) does not find it.
9. **The sweep on the bench venv** (9.5): 74 unexpected rows, 73 of them
   `machinome_mechanics` missing from the bench venv, against the base's 2;
   a diagnostic run with the workspace's mechanics checkout on `PYTHONPATH`
   gives the base's counts but for fender-bender's `fb_library`, also an
   environment package.
10. Smaller, recorded in their sections: the source names in
    `test_every_member_is_a_workspace_source` are the directories' names
    (2.1); `test_the_members_are_the_package_directories` red at 3.3 besides
    the reds the task lists; `test_no_core_module_imports_the_kernel_or_cadquery`
    red at 2.3 besides the three the task lists; the sync of 4.5 was
    incremental on 1.2's venv (3 installed, 177 present); the member test's
    red shown at 4.1 besides the pin test's.

## 10. The review's corrections, and the records closing

The orchestrator's review of the checkpoint (10 October 2026) accepted the
work to task 9.8, departures 1, 2, 3, 6 and 8 included, found the sweep's
cause in the environment, not in the cut, and asked for four corrections in
this cycle before group 10, made as follows.

### The bench venv carries the mechanics package (correction 1)

Red first: the layout gate's `test_the_default_group_is_the_framework_dev_extra`
renamed `test_the_default_group_is_the_framework_dev_and_mechanics_extras`,
expecting `['machinome[dev]', 'machinome[mechanics]']`:

```
$ ... pytest tests/test_repository_layout.py
1 failed, 25 passed, 86 subtests passed in 1.97s
AssertionError: Lists differ: ['machinome[dev]'] != ['machinome[dev]', 'machinome[mechanics]']
```

The root `pyproject.toml`'s default group then became
`dev = ["machinome[dev]", "machinome[mechanics]"]`, its comment extended by
the sentence the review gave ("and the mechanics package the catalogue's
projects import, so the universe sweep reads them from this venv").

```
$ env -C <bench> /home/asa/.local/bin/uv lock
Resolved 187 packages in 747ms
```

No "Added" line: uv locks every extra of every member, so
`machinome-mechanics` 0.1.0 (`source = { registry = "https://pypi.org/simple" }`)
was already in the lock; the lock's one change is the root's dev group
naming the second entry.

```
$ env -C <bench> /home/asa/.local/bin/uv sync --python 3.12
Resolved 187 packages in 3ms
Installed 2 packages in 14ms
 ~ machinome==0.8.1
 + machinome-mechanics==0.1.0
$ env -C /tmp <bench>/.venv/bin/python -c "import machinome_mechanics ..."
<bench>/.venv/lib/python3.12/site-packages/machinome_mechanics/__init__.py 0.1.0
```

178 packages in the venv.

### `tox` out of the `dev` extra (correction 2; departure 4 closed)

`"tox>=4",` removed from the framework's `dev` extra.

```
$ env -C <bench> /home/asa/.local/bin/uv lock
Resolved 179 packages in 91ms
Removed cachetools v7.2.1
Removed distlib v0.4.3
Removed filelock v4.1.0
Removed pyproject-api v1.11.5
Removed python-discovery v1.6.2
Removed tomli-w v1.2.0
Removed tox v4.65.1
Removed virtualenv v21.14.6
$ env -C <bench> /home/asa/.local/bin/uv sync --python 3.12
Resolved 179 packages in 4ms
Uninstalled 9 packages in 101ms
Installed 1 package in 11ms
```

The eight leave, `machinome` reinstalled; 170 packages in the venv. No module
of the framework, its tests or `scripts/` imports any of the eight (`grep`
for their import names: none). Task 6.4's grep again: in the framework's
directory only the layout gate's lines 47-48 (the entries the root must not
hold) and its guide test's list of retired words (line 363); at the root,
none.

### `.bumpversion.cfg` without a comment; the Deploying section (correction 3; departures 5 and 7 closed)

`.bumpversion.cfg` lost its three-line header comment, so a real bump
produces no diff beyond the statements it moves. `CONTRIBUTING.rst`'s
Deploying section, in place: the line `$ cd packages/machinome` removed, and
"Make sure all your changes are committed (including an entry in
HISTORY.rst)." became "Make sure all your changes are committed (including
an entry in HISTORY.rst); ``.bumpversion.cfg`` at the repository root names
every package's version and every pin between them, so one run moves the
set." on its one line, as before. design.md corrected with a dated sentence
each ("Corrected at review on 10 October 2026"): Decision 5 (the file's
text without the comment, and why), Decision 10 (the Deploying section),
and, since the two corrections above make their sentences untrue, Decision
3 (`dev` drops `tox>=4`) and Decision 4 (the default group, 179 locked, 170
installed); Decision 12 below. `openspec validate cut-the-engines --strict`:
valid.

```
$ ... pytest tests/test_repository_layout.py tests/test_kernel_extras.py tests/test_release_records.py tests/test_vet_universe.py tests/test_docs_structure.py
87 passed, 974 subtests passed in 3.95s
```

### The sweep on the re-synced venv (correction 4)

Decision 12's command, unchanged, JSON `<scratch>/load-projects-2.json`:

```
63 repositories, 130 rows: 121 ok, 0 expected, 3 unexpected, 0 timeout, 6 no-model; 2 skipped
```

exit 1, for the three unexpected rows:

- `3DPrintedClocks` `wall_clock_41`: `machinome.parameters.ParameterError:
  Movement.wound_weight_seat: frame argument at -- the callable raised
  ValueError: Workplane object must have at least one solid on the stack to
  union!`: the base's own CadQuery error.
- `Robotic-Arms/Dum-E`: `ModuleNotFoundError: No module named
  'machinome_freecad'` at `simulation/dume.py:7`: the base's.
- `3D-Printers/fender-bender`: `ModuleNotFoundError: No module named
  'fb_library'` at `src/bender_config.py:12`: a dependency of that project
  alone, which the workspace venv carries and the bench venv does not.

Row by row against `root-cleanup`'s JSON: fender-bender is the one row whose
outcome differs; `Code-Atlanticus` `ca1078r-sawmill`, the catalogue's
addition since 5 October 2026, is the new row, ok. design.md Decision 12
corrected with a dated sentence: the bench venv carries the mechanics
package for the sweep, and fender-bender's own dependency is outside the
set.

### 10.1 ADR-183 accepted (task 10.1)

`docs/adrs/BUILD/ADR-183-an-extension-package-is-a-namespace-portion-in-its-own-distribution.md`:
Status **Accepted**, its Change link repointed to
`../../../openspec/changes/archive/2026-10-10-cut-the-engines/` (resolves);
its index entry under BUILD reads **Accepted**, amends 167, cites 180/182.
ADR-183 amends ADR-167 alone (it relates to ADR-180 and ADR-182 without
amending them), so ADR-167's status line gains "the `brep` and `mesh` extras
naming the engines' distributions, amended 2026-10-10 by ADR-183" and its
index line "amended by 183"; ADR-180's are unchanged. `docs/architecture.md`
checked against it: the engine-package paragraph names the two
distributions and ADR-183, and the Map's "Repository layout", B-rep engine
and mesh engine rows cite 183.

### 10.2 Archive and spec sync (task 10.2)

```
$ env -C <bench>/packages/machinome openspec archive cut-the-engines -y
Proposal warnings in proposal.md (non-blocking):
  ⚠ Why section should not exceed 1000 characters
Task status: 49/52 tasks
Warning: 3 incomplete task(s) found. Continuing due to --yes flag.
Applying changes to openspec/specs/brep-engine-dependency/spec.md:
  ~ 2 modified
Applying changes to openspec/specs/framework-contributor-guidance/spec.md:
  ~ 1 modified
Applying changes to openspec/specs/framework-identity/spec.md:
  ~ 1 modified
Applying changes to openspec/specs/kernel-extras/spec.md:
  ~ 3 modified
Applying changes to openspec/specs/mesh-engine-dependency/spec.md:
  ~ 2 modified
Totals: + 0, ~ 9, - 0, → 0
Specs updated successfully.
Change 'cut-the-engines' archived as '2026-10-10-cut-the-engines'.
```

The three incomplete tasks were 10.2 to 10.4, ticked after it. `diff -rq` of
`openspec/specs` before and after: the five named specs changed, nothing
else. `git add -A packages/machinome/openspec/changes` records the move.

```
$ env -C <bench>/packages/machinome openspec validate --specs --strict
Totals: 45 passed, 0 failed (45 items)
```

### 10.3 The plan note (task 10.3)

The root's `workflow/ongoing/monorepo-0.9.md`: cycle 2 gains its **Done**
entry (branch, planning commit edf88424, ADR-183, the bench venv as the
sweep's environment, the suite count of 9.1, the manual, `scripts/check-dist`'s
result with the clean copy's counts, the lock, the sweep's counts with its
three named rows, this evidence file).

### After the archive

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_repository_layout.py tests/test_kernel_extras.py tests/test_release_records.py tests/test_docs_structure.py
73 passed, 967 subtests passed in 3.66s
```

### 10.4 (task 10.4)

This file is complete to the implementation commit, which is the
orchestrator's; the planning commit edf88424 is not amended, and nothing is
pushed.
