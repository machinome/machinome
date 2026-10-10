# Evidence: `monorepo-layout`

The first cycle of the 0.9 monorepo campaign (`workflow/ongoing/monorepo-0.9.md`
at the repository root, "The campaign: the cut", cycle 1). Worktree
`machinome/WTs/v0.9-base-monorepo-layout`, branch `v0.9-base-monorepo-layout`,
cut from the line `v0.9-base` at 19c9f83b ("workflow: the 0.9 monorepo plan,
the cut of the framework's packages (pilot, 10 October 2026)"). Planning commit
257293d2, ratified by the orchestrator's review. Applied on 10 October 2026.

Tools: the workspace venv's Python 3.12.3, uv 0.11.8, the OpenSpec CLI 1.6.0,
git 2.43.0. Every command ran with `env -C <dir>` and absolute paths;
`<bench>` is `/home/asa/devel/machinome/machinome/WTs/v0.9-base-monorepo-layout`
and `<scratch>` is
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C1-apply/`.
Before the move (group 2) tests ran from `<bench>` with
`PYTHONPATH=<bench>` and the workspace venv; after it, as each section says.
pytest ran one process at a time. Probes and logs are in `<scratch>`, never in
the bench.

## 1. Evidence baseline

### 1.1 The base (task 1.1)

```
$ git -C <bench> log --oneline -2
257293d2 Propose monorepo-layout: the framework's tree under packages/machinome, the root the repository's (decided 10 October 2026)
19c9f83b workflow: the 0.9 monorepo plan, the cut of the framework's packages (pilot, 10 October 2026)
$ git -C <bench> status --short | wc -l
0
```

### 1.2 The tree (task 1.2)

```
$ git -C <bench> ls-files | wc -l
3347
```

3340 (design.md, Context) plus the seven files of this change's planning
commit (`.openspec.yaml`, `proposal.md`, `design.md`, `tasks.md` and the three
delta specs).

`git -C <bench> ls-files | cut -d/ -f1 | sort | uniq -c`: `.claude` 12,
`.editorconfig` 1, `.github` 2, `.gitignore` 1, `.readthedocs.yaml` 1,
`AI-USE.md` 1, `CONTRIBUTING.rst` 1, `CREDITS.md` 1, `HISTORY.rst` 1,
`LICENSE` 1, `LICENSES` 2, `MANIFEST.in` 1, `Makefile` 1, `README.rst` 1,
`context7.json` 1, `docs` 281, `machinome` 120, `openspec` 1928,
`pyproject.toml` 1, `requirements.txt` 1, `requirements_dev.txt` 1,
`setup.cfg` 1, `spike` 23, `tests` 683, `tools` 11, `tox.ini` 1, `workflow`
268: design.md's 27 entries and counts, `openspec` 1921 + 7.

```
$ git -C <bench> ls-files -ci --exclude-standard | wc -l
34
$ git -C <bench> ls-files -ci --exclude-standard | grep -vc '\.log$'
0
```

### 1.3 The base suite (task 1.3, recorded, not rerun)

Measured by the orchestrator on the line head 19c9f83b, the same tree, with the
workspace venv and `PYTHONPATH=<worktree>`, on 10 October 2026:

```
4768 passed, 4 skipped, 6734 subtests passed in 849.82s
```

## 2. Red first, at today's paths

### 2.1 The gate (task 2.1)

`tests/test_repository_layout.py`, new: 21 test methods in eight classes, one
class per group of design.md Decision 6 (G1 `ThePlaceTest`, G2
`TheSharedFilesTest`, G3 `TheManifestTest`, G4 `TheWorkspaceTest`, G5
`TheIndexTest`, G6 `TheContinuousIntegrationTest`, G7
`TheRootIsTheRepositorysTest`, G8 `TheLinksTest`).

```
$ env -C <bench> PYTHONPATH=<bench> <venv>/python -m pytest -q -p no:cacheprovider tests/test_repository_layout.py
27 failed, 4 passed, 24 subtests passed in 0.44s
```

(27 counts the 17 failed methods and the 10 failed subtests.) Each group's
reason, from `<scratch>/2.1-gate-red.txt`; `REPOSITORY` is the bench's parent
`machinome/WTs`:

- G1: `AssertionError: PosixPath('<bench>') != PosixPath('/home/asa/devel/machinome/machinome/WTs/packages/machinome') : the framework is at <bench>, not at packages/machinome of the repository /home/asa/devel/machinome/machinome/WTs`.
- G2: each of the five subtests, `<bench>/LICENSE is not a symbolic link`,
  and the same for `LICENSES`, `HISTORY.rst`, `CONTRIBUTING.rst`,
  `AI-USE.md`.
- G3: both tests green (they pin what the move keeps).
- G4: all six tests, `FileNotFoundError: ... 'machinome/WTs/pyproject.toml'`.
- G5: `context7.json is in the package directory`.
- G6: all four tests, `FileNotFoundError: ... 'machinome/WTs/.github/workflows/python-app.yml'`.
- G7: `test_the_repository_s_files_are_there`: four subtests
  (`README.md`, `.gitignore`, `scripts/check-dist`, `workflow/README.md`
  missing) and `scripts/check-dist is not executable`;
  `test_the_root_ignores_the_benches_and_the_venv` and
  `test_the_readme_links_every_package_and_states_the_licence`:
  `FileNotFoundError` on `machinome/WTs/.gitignore` and `README.md`.
  `test_the_framework_s_entries_are_not` is green: it is an absence check,
  and `machinome/WTs` holds none of the framework's entries. Its red is
  shown by a probe instead (`<scratch>/probe_entries.py`, the module's
  `REPOSITORY` set to the bench and `PACKAGE` to `<bench>/packages/machinome`):
  16 failures, `machinome is at the repository root` and the same for the
  other 14 entries, and `the framework's working record is not in its
  directory`.
- G8: `test_every_github_link_names_a_path_of_the_repository`:
  `README.rst links docs/tutorial/counter/readme.py, which is not a path of
  the repository`; `test_every_relative_link_resolves`: `FileNotFoundError`
  on `machinome/WTs/README.md`.

### 2.2 `tests/test_docs_exports.py` (task 2.2)

`REPO` became `PACKAGE` (`parents[1]`) beside `REPOSITORY` (`parents[2]`);
`WORKFLOW` reads `REPOSITORY`; `READTHEDOCS` stays the package's; the Read the
Docs install pin compares with `packages/machinome/docs/requirements.txt`; the
new `test_configures_the_framework_manual` pins `sphinx.configuration` to
`packages/machinome/docs/conf.py`; the CI pins keep `-r docs/requirements.txt`;
`test_no_example_is_pinned` reads `.gitmodules` at `REPOSITORY`.

```
$ env -C <bench> PYTHONPATH=<bench> <venv>/python -m pytest -q -p no:cacheprovider tests/test_docs_exports.py
5 failed, 13 passed, 10 subtests passed in 0.64s
```

- `ReadTheDocsBuildsNothingTest::test_configures_the_framework_manual`:
  `AssertionError: 'docs/conf.py' != 'packages/machinome/docs/conf.py'`.
- `ReadTheDocsBuildsNothingTest::test_installs_the_requirements_alone`:
  `Lists differ: [{'requirements': 'docs/requirements.txt'}] != [{'requirements': 'packages/machinome/docs/requirements.txt'}]`.
- `ActionsDocsJobBuildsNothingTest::test_builds_with_warnings_as_errors`,
  `::test_installs_the_requirements_alone`, `::test_no_forbidden_step`:
  `FileNotFoundError: ... 'machinome/WTs/.github/workflows/python-app.yml'`.

### 2.3 The `Unreleased` section (task 2.3)

The section and the entry of proposal.md, verbatim, written at the top of
`HISTORY.rst` above `Machinome 0.8.1 (2026-10-10)`.

```
$ env -C <bench> PYTHONPATH=<bench> <venv>/python -m pytest -q -p no:cacheprovider tests/test_release_records.py tests/test_profile_documentation.py
2 failed, 10 passed, 60 subtests passed in 0.29s
```

- `test_release_records.py::ReleaseRecordsTest::test_the_history_top_entry_is_the_released_version`:
  `AssertionError: 'unreleased' unexpectedly found in "=======\nhistory\n=======\n\nunreleased\n----------\n..."`.
- `test_profile_documentation.py::ProfileDocumentationTest::test_released_status_changelog_and_history`:
  the same, on the text before `machinome 0.7.0`.

### 2.4 `tests/test_release_records.py` (task 2.4)

`REPOSITORY = parents[2]`; `test_context7_states_the_release` reads
`REPOSITORY / 'context7.json'`; the history pin now takes the changelog pin's
shape: the first dashed title is `Unreleased` or the released entry,
`Unreleased` occurs as a dashed title exactly once if first and never
otherwise, and the text before `Machinome <version>` with its first
`\nUnreleased\n----------\n` removed does not contain `unreleased`.

```
$ env -C <bench> PYTHONPATH=<bench> <venv>/python -m pytest -q -p no:cacheprovider tests/test_release_records.py
1 failed, 9 passed, 60 subtests passed in 0.17s
```

The history pin green; `test_context7_states_the_release` red,
`FileNotFoundError: ... 'machinome/WTs/context7.json'`.

The pin's refusals, by probe (`<scratch>/probe_history_pin.py`, the test
method run on a mutated copy of the history text):

```
as written GREEN
second heading RED 2 != 1
word in an entry RED 'unreleased' unexpectedly found in "=======\nhistory\n=======\n\n\n* **the framework is a package of
heading below the release RED 2 != 1
```

### 2.5 `tests/test_profile_documentation.py` (task 2.5)

The history line takes the changelog line's
`replace('\nunreleased\n----------\n', '\n', 1)`; its comment names the
history beside the changelog.

```
$ env -C <bench> PYTHONPATH=<bench> <venv>/python -m pytest -q -p no:cacheprovider tests/test_profile_documentation.py
2 passed in 0.09s
```

## 3. The move

### 3.1 The framework's tree (task 3.1)

```
$ mkdir -p <bench>/packages/machinome
$ env -C <bench> git mv machinome tests docs openspec tools spike pyproject.toml setup.cfg tox.ini Makefile MANIFEST.in requirements.txt requirements_dev.txt README.rst CREDITS.md .gitignore .readthedocs.yaml packages/machinome/
$ git -C <bench> status --short | cut -c1-2 | sort | uniq -c
      1  M        HISTORY.rst (task 2.3)
      3 ??        .env, evidence.md, tests/test_repository_layout.py
   3053 R
      4 RM        tasks.md and the three tests edited in group 2
```

`evidence.md` and `test_repository_layout.py`, untracked at that point, moved
on disk with their directories:
`packages/machinome/openspec/changes/monorepo-layout/evidence.md` exists.
`.env` is the bench's port file, ignored by the framework's `.gitignore`
before the move and by the root's `/.env` after task 4.1.

### 3.2 The framework's working record (task 3.2)

```
$ mkdir -p <bench>/packages/machinome/workflow/ongoing
$ env -C <bench> git mv workflow/README.md workflow/warts.md workflow/archive packages/machinome/workflow/
$ env -C <bench> sh -c 'for e in workflow/ongoing/*; do [ "$e" = workflow/ongoing/monorepo-0.9.md ] || git mv "$e" packages/machinome/workflow/ongoing/ || exit 1; done'
$ git -C <bench> ls-files workflow
workflow/ongoing/monorepo-0.9.md
```

`packages/machinome/workflow/ongoing/` holds the other 15 entries.

### 3.3 The symlinks (task 3.3)

`ln -s ../../<name> <name>` in `packages/machinome/` for the five, then
`git add`:

```
$ git -C <bench> ls-files -s packages/machinome | grep ^120000
120000 aeb4891d... 0	packages/machinome/AI-USE.md
120000 e9a8ba64... 0	packages/machinome/CONTRIBUTING.rst
120000 7cc99308... 0	packages/machinome/HISTORY.rst
120000 30cff740... 0	packages/machinome/LICENSE
120000 06ad40db... 0	packages/machinome/LICENSES
```

`git cat-file -p` of the five blobs: `../../AI-USE.md`,
`../../CONTRIBUTING.rst`, `../../HISTORY.rst`, `../../LICENSE`,
`../../LICENSES`.

### 3.4 The path-reading modules on the moved tree (task 3.4)

The 42 modules of design.md, Context (the list the proposer's probe selected,
`test_meta.py` included this time), and the gate, from the package directory
with the fallback recipe:

```
$ env -C <bench>/packages/machinome PYTHONPATH=<bench>/packages/machinome <venv>/python -m pytest -q -p no:cacheprovider <42 modules> tests/test_repository_layout.py
34 failed, 622 passed, 19 warnings, 2229 subtests passed in 537.34s (0:08:57)
```

**A red that differed from the expected one, investigated.** Every
`REPOSITORY`-reading test failed, G1 included:
`AssertionError: ... <bench>/packages/machinome') != ... <bench>/packages/packages/machinome')`.
design.md (Decisions 6 and 8, tasks 2.2, 2.4 and 6.4) spells the repository
root `Path(__file__).resolve().parents[2]`. For
`packages/machinome/tests/test_x.py`, `parents[1]` is the package directory
and `parents[2]` is `packages/`; the repository root is `parents[3]`. Before
the move `parents[2]` named the bench's parent `machinome/WTs`, which is what
design.md's red reasons describe, so the slip did not show in group 2. Every
statement of the design about `REPOSITORY` (G1's `PACKAGE == REPOSITORY /
'packages' / 'machinome'`, the CI workflow, `context7.json` and
`.gitmodules` at the repository root) holds only with `parents[3]`, so the
three edited tests and the gate were corrected to
`REPOSITORY = Path(__file__).resolve().parents[3]`, and test_docs_structure's
repointing (6.4) uses the same. Before the move `parents[3]` would have named
`/home/asa/devel/machinome/machinome`, the primary checkout, whose CI
workflow and `context7.json` exist: the corrected index could not have been
red before the move for those tests. The group 2 reds above are therefore
the reds of the design's index at today's paths, and the corrected index's
reds are the ones below, on the moved tree before the root files.

The other 39 modules of the run (all but `test_docs_exports.py`,
`test_release_records.py` and the gate) read through `parents[1]` or
`dirname(BASEDIR)` and had no failure. The three were rerun with the
corrected index:

```
$ env -C <bench>/packages/machinome PYTHONPATH=<bench>/packages/machinome <venv>/python -m pytest -q -p no:cacheprovider tests/test_docs_exports.py tests/test_release_records.py tests/test_repository_layout.py
40 failed, 35 passed, 103 subtests passed in 0.87s
```

As task 3.4 expects: G1, G2 and G3 green, and G7's absence check green; G4
(six tests, `FileNotFoundError` on `<bench>/pyproject.toml`), G5 (each of
the seven unprefixed folders "neither the root workflow nor a folder of the
framework"), G6 (`working-directory` `None` for five jobs, each unprefixed
`cache-dependency-path` "not a file of the repository", `KeyError: 'dist'`),
G7 (`README.md`, `.gitignore`, `scripts/check-dist`, `workflow/README.md`
missing) and G8 (the README's link, the root `README.md` missing) red;
`test_docs_exports.py`'s two Read the Docs pins red; the three CI tests and
`test_context7_states_the_release` green (they read the root's unedited
files). (40 counts the 14 failed methods and the 26 failed subtests.)

## 4. The root files

- 4.1 `.gitignore`, 4.2 `README.md`, 4.3 `pyproject.toml`, 4.4
  `workflow/README.md`: design.md's text, verbatim. The framework's
  `packages/machinome/workflow/README.md` gains, at the end of "Where this
  fits", the sentence of Decision 10, appended to its paragraph.
- 4.5 `context7.json`: the seven `excludeFolders` prefixed with
  `packages/machinome/`, `workflow` added; nothing else changed (the file
  parses with `json.loads`).
- 4.6 `packages/machinome/.readthedocs.yaml`: `python.install` names
  `packages/machinome/docs/requirements.txt` and `sphinx.configuration`
  `packages/machinome/docs/conf.py`; a comment paragraph says the file sits
  beside the manual, that the project's configuration path is
  `packages/machinome/.readthedocs.yaml`, and that Read the Docs reads every
  path in it from the repository root.
- 4.7 `.github/workflows/python-app.yml`: job-level
  `defaults: run: working-directory: packages/machinome` on `lint`, `test`,
  `browser-snapshot`, `docs` and `build`; the five `cache-dependency-path`
  values prefixed; the `dist` job verbatim, after `docs`. Parsed:

  ```
  $ python -c "import yaml; ..."
  ['lint', 'test', 'browser-snapshot', 'docs', 'dist', 'build']
  dist: defaults None, needs ['test', 'docs']; every other job: working-directory packages/machinome
  ```
- 4.8 `scripts/check-dist`: Python, `#!/usr/bin/env python3`, the SPDX
  header, recorded mode 100755 (`git ls-files -s scripts/check-dist`).

After group 4, with the fallback recipe:

```
$ env -C <bench>/packages/machinome PYTHONPATH=<bench>/packages/machinome <venv>/python -m pytest -q -p no:cacheprovider tests/test_docs_exports.py tests/test_release_records.py tests/test_repository_layout.py
7 failed, 48 passed, 139 subtests passed in 0.66s
```

G6 and the three CI tests green, the two Read the Docs pins green. Left red:
G4's `test_the_lock_records_the_member_editable` (`uv.lock` missing, group
5) and G8 (the README link and the five relative links of
`CONTRIBUTING.rst`, group 6).

## 5. The workspace environment

### 5.1 The lock (task 5.1)

```
$ env -C <bench> /home/asa/.local/bin/uv lock
Using CPython 3.11.14 interpreter at: /home/asa/.pyenv/versions/3.11.14/bin/python3
Resolved 185 packages in 660ms
$ ls -l <bench>/uv.lock
961173 bytes
$ grep -c '^\[\[package\]\]' <bench>/uv.lock
185
$ grep -n 'source = { editable = "packages/machinome" }' <bench>/uv.lock
1824:source = { editable = "packages/machinome" }
```

`requires-python = ">=3.11"`. Probe 3's numbers, to the byte.

### 5.2 The sync (task 5.2)

```
$ env -C <bench> /home/asa/.local/bin/uv sync --python 3.12
Using CPython 3.12.3 interpreter at: /usr/bin/python3.12
Creating virtual environment at: .venv
Resolved 185 packages in 1ms
   Built machinome @ file://<bench>/packages/machinome
Installed 175 packages in 8.96s
$ cat <bench>/.venv/lib/python3.12/site-packages/__editable__.machinome-0.8.1.pth
<bench>/packages/machinome
$ env -C /tmp <bench>/.venv/bin/python -c "import machinome, cadquery, build123d, manifold3d, molejo, solid2; print(machinome.__file__)"
<bench>/packages/machinome/machinome/__init__.py
```

(uv also warned that hardlinking from its cache failed and it copied, the
cache and the bench being on different filesystems.) `machinome`, `pytest`,
`flake8`, `twine` and `sphinx-build` are in `<bench>/.venv/bin/`; `pip` is
not (a uv venv carries none). `.venv/` is ignored (`git status --ignored`:
`!! .venv/`); `uv.lock` was `git add`ed.

### 5.3 G4 (task 5.3)

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_repository_layout.py::TheWorkspaceTest
6 passed, 1 subtests passed in 0.13s
```

## 6. The records

- 6.1 `CONTRIBUTING.rst`: the edits of Decision 9 in place: the tutorial
  path, the install paragraph (`uv sync` from the clone's root; without uv,
  `pip install -e "packages/machinome[dev]"`), the entry point's path, "run
  from the framework's directory, ``packages/machinome``" with
  `$ cd packages/machinome` first in the block, the OpenSpec directory "where
  the ``openspec`` command runs", the manual under
  ``packages/machinome/docs/``, and the five relative link targets prefixed
  (their link texts unchanged). Paragraphs rewrapped at the file's width; its
  two lines over 80 columns are the two it had before.
- 6.2 `AI-USE.md`: the one sentence of Decision 9.
- 6.3 `packages/machinome/README.rst`: the one link; `wc -w` 1422 before and
  after.
- 6.5 `docs/contributor-briefing.md`: the sentence opening "Layout".
- 6.6 `docs/reference/api.rst`: `$ cd packages/machinome` first in the
  corpus block.
- 6.7 `docs/architecture.md`: the identity sentence, the known gap ("the
  repository's `.github/workflows/python-app.yml`", rewrapped), and the Map's
  first row, "Repository layout".
- 6.8 `docs/adrs/BUILD/ADR-182-the-repository-is-a-monorepo-of-distributions-named-by-directory.md`,
  Status Proposed, and its entry under BUILD in `docs/adrs/README.md`, after
  ADR-179.

### 6.4 The `.gitmodules` checks (task 6.4)

An empty `.gitmodules` planted at `<bench>/.gitmodules`:

```
$ env -C <bench>/packages/machinome PYTHONPATH=... pytest -q tests/test_docs_structure.py::NavigationTest::test_the_examples_are_on_the_site tests/test_docs_exports.py::EmbeddedExportsAreCommittedTest::test_no_example_is_pinned
1 failed, 1 passed, 3 subtests passed in 0.17s
```

`test_docs_structure.py`'s check as it was (reading the package directory)
passed; `test_no_example_is_pinned`, repointed in 2.2, failed:
`AssertionError: True is not false : .gitmodules exists; the manual pins no
submodule`. Its version as it was, by probe (`<scratch>/probe_gitmodules_old.py`,
the module's `REPOSITORY` set to `PACKAGE`): `as it was: GREEN`. Then
`test_docs_structure.py` gained `REPOSITORY = Path(__file__).resolve().parents[3]`
and its check reads it:

```
1 failed, 3 subtests passed in 0.17s
AssertionError: True is not false : the manual pins a submodule
```

The planted file removed (`ls` reports it absent), both green: `2 passed, 3
subtests passed in 0.14s`.

### 6.9 The gate (task 6.9)

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_repository_layout.py tests/test_docs_exports.py tests/test_docs_structure.py tests/test_release_records.py tests/test_profile_documentation.py
67 passed, 906 subtests passed in 1.22s
```

The whole gate green, `ReadmeTest` and `LicenceWordingTest` among them.

## 7. Validation

### 7.1 The whole suite on the bench venv (task 7.1)

One process, from the package directory, in the background, its output in
`<scratch>/7.1-suite.txt` (`-p no:cacheprovider` added, so no
`.pytest_cache` is written):

```
$ env -C <bench>/packages/machinome PATH=<bench>/.venv/bin:$PATH <bench>/.venv/bin/python -m pytest -q -rs -p no:cacheprovider
4774 passed, 20 skipped, 55 warnings, 6799 subtests passed in 872.54s (0:14:32)
```

No failure. 4774 is probe 8's 4748 passed, plus its four failures now green
(the three CI tests and `test_context7_states_the_release`), plus the gate's
21 tests and the new `test_configures_the_framework_manual`. The 20 skips,
each reason:

```
14 tests/test_browser_renderer.py: machinome-viewer not installed (pip install "machinome[viewer]")
 1 tests/test_cli_lazy_imports.py: machinome-viewer not installed
 1 tests/test_scad_presentation.py: machinome-viewer not installed (pip install "machinome[viewer]")
 1 tests/test_connectivity.py: the repairing split needs networkx, which machinome does not install
 1 tests/test_jscad_integration.py: jscad CLI is not installed
 2 tests/test_step_assembly.py: Internal-Cycloidal-Actuator vendor STEP not present
```

The base's 4 skips (1.3, workspace venv, which carries the viewer) are the
last four; the 16 more are the viewer's tests, which the lock excludes
(design.md, Decision 3). The skips differ from 1.3's by the viewer's tests
alone, so the fallback recipe's whole-suite run was not required and was not
made. Against the base: 4768 + 21 + 1 = 4790 tests would run on a venv
carrying the viewer; 4774 + 16 = 4790.

### 7.2 Lint (task 7.2)

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/flake8 --max-line-length=89 machinome tests | wc -l
759
```

flake8 7.4.1 on CPython 3.12.3. The base, `git archive 19c9f83b machinome
tests setup.cfg tox.ini` unpacked in `<scratch>/flake8-base/`, the same
command: 759. The two lists, compared by path and message, are identical;
none names a file this change edited or added. `scripts/check-dist`: 0.

### 7.3 The manual (task 7.3)

```
$ /usr/bin/python3.12 -m venv <scratch>/docs-venv
$ <scratch>/docs-venv/bin/pip install -q -r <bench>/packages/machinome/docs/requirements.txt
(Sphinx 9.1.0, sphinx_rtd_theme 3.1.0, machinome-viewer 0.8.0 from the index)
$ env -C <bench>/packages/machinome <scratch>/docs-venv/bin/python -m sphinx -b html -W docs <scratch>/html
build succeeded.
```

54 HTML pages under `<scratch>/html`.

### 7.4 `scripts/check-dist` (task 7.4)

```
$ env -C <bench> <bench>/.venv/bin/python scripts/check-dist
Members: machinome
... twine check --strict: both archives PASSED
   machinome-0.8.1/AI-USE.md: regular file, 5190 bytes, equal to the root's
   machinome-0.8.1/CONTRIBUTING.rst: regular file, 10394 bytes, equal to the root's
   machinome-0.8.1/HISTORY.rst: regular file, 91724 bytes, equal to the root's
   machinome-0.8.1/LICENSE: regular file, 793 bytes, equal to the root's
   machinome-0.8.1/LICENSES/CERN-OHL-S-2.0.txt: regular file, 13419 bytes, equal to the root's
   machinome-0.8.1/LICENSES/GPL-2.0-or-later.txt: regular file, 17984 bytes, equal to the root's
   machinome-0.8.1.tar.gz: 1077 entries
   machinome-0.8.1-py3-none-any.whl: 128 entries
$ <tmp>/venv/bin/python -m pip install --quiet --find-links <tmp>/dist/machinome <tmp>/dist/machinome/machinome-0.8.1-py3-none-any.whl[openscad,stl]
$ <tmp>/venv/bin/python -I -c VENV = '<tmp>/venv' ...
machinome 0.8.1 from <tmp>/venv/lib/python3.12/site-packages/machinome/__init__.py
License-Expression: GPL-2.0-or-later OR CERN-OHL-S-2.0+
   licenses/LICENSE
   licenses/LICENSES/CERN-OHL-S-2.0.txt
   licenses/LICENSES/GPL-2.0-or-later.txt
$ <tmp>/venv/bin/machinome --help
   machinome --help: exit 0
Every distribution built, checked, installed and smoked; nothing uploaded.
```

exit 0. `<tmp>` is `tempfile`'s directory, `/tmp/machinome-check-dist-*`,
outside the repository and removed at the end. The three root files' sizes
differ from probe 4's by this change's own edits (the `Unreleased` section,
the CONTRIBUTING and AI-USE facts).

The bench's sdist holds 1077 entries, probe 4's 1020 plus 57: the gate's
module, and 54 files with their 2 directories that the suite of 7.1 left
under `tests/`, ignored by git and swept in by `MANIFEST.in`'s
`recursive-include tests *` (`tests/_build.lock`, `tests/_build_meta.lock`,
`tests/_build_meta/` with 28 files, 19 `tests/step_project/*.step`, 5
`tests/stl_project/` files; listed by comparing a scratch sdist's members
with `git ls-files`). A tree that has run the suite builds the same sdist at
the root of today's layout; the move does not cause it. The same script on a
clean copy of the tracked tree (`git ls-files -z | tar --null -T - -cf -`
unpacked in `<scratch>/clean/`, links kept as links):

```
   machinome-0.8.1.tar.gz: 1021 entries
   machinome-0.8.1-py3-none-any.whl: 128 entries
Every distribution built, checked, installed and smoked; nothing uploaded.
```

1021 is probe 4's 1020 plus `tests/test_repository_layout.py`; the wheel's
128 equal probe 4's.

`git -C <bench> status --short --ignored` taken before and after the bench
run: identical (the build's `packages/machinome/build/` and
`machinome.egg-info/` scratch is ignored and was already there from the
first run).

### 7.5 Git (task 7.5)

```
$ git -C <bench> status --short | cut -c1-2 | sort | uniq -c
      5  M
     12 A
      2 AM
      3 M
   3310 R
     11 RM
$ git -C <bench> ls-files | wc -l
3361
$ git -C <bench> ls-files -ci --exclude-standard | wc -l
34
```

3361 is 1.2's 3347 plus the root's `.gitignore`, `README.md`,
`pyproject.toml`, `uv.lock`, `scripts/check-dist` and `workflow/README.md`,
the five links and `tests/test_repository_layout.py` (12, task 7.5's list),
plus this change's `evidence.md` and ADR-182, which task 7.5's list does not
name. Every moved file shows as a rename (`R`/`RM`) but three: the
framework's `.gitignore`, `pyproject.toml` and `workflow/README.md` show as
added at `packages/machinome/` with the root path modified (`A` and `M`),
because a new file of the same name took the old path at the root and git
pairs the path with its new content. The 3310 plain renames and the 11
renamed-and-edited files are the rest of the tree.

### 7.6 OpenSpec (task 7.6)

```
$ env -C <bench>/packages/machinome openspec validate monorepo-layout --strict
Change 'monorepo-layout' is valid
```

## Departures from the design, to the checkpoint (task 7.7)

1. **`REPOSITORY` is `parents[3]`, not `parents[2]`** in
   `test_repository_layout.py`, `test_docs_exports.py`,
   `test_release_records.py` and `test_docs_structure.py` (3.4 above): the
   design's index names `packages/` once the tests sit in
   `packages/machinome/tests/`. Every assertion the design states about
   `REPOSITORY` is kept. Accepted by the orchestrator's review of the
   checkpoint (10 October 2026), and corrected in the ratified text as a
   dated correction: design.md Decision 6 (the names and a sentence closing
   its "Red at 19c9f83b" paragraph) and Decision 8's rows for
   `test_docs_exports.py` and `test_release_records.py`, and tasks 2.2, 2.4
   and 6.4, each now reading `parents[3]`. The spec deltas name no index.
2. **Three moved files are not renames in `git status`** (7.5 above): the
   framework's `.gitignore`, `pyproject.toml` and `workflow/README.md`.
3. **The file count is 3361, not 3359** (7.5 above): `evidence.md` and
   ADR-182 are new files task 7.5's list does not name.
4. **The bench's sdist holds 1077 entries** (7.4 above), the suite's ignored
   leavings under `tests/` included; a clean copy of the tracked tree builds
   1021.
5. **`CONTRIBUTING.rst`**: the five prefixed links keep their link texts
   (`docs/adrs/README.md` and the like), only their targets prefixed. Two
   statements the design does not list were left at the checkpoint: "as
   ``pyproject.toml`` requires" (line 69) and the "Deploying" section's
   `bump2version`, which must run from the package directory where
   `setup.cfg` and its bumpversion table are. Closed by the review: line 69
   now reads "as the framework's ``packages/machinome/pyproject.toml``
   requires", and the Deploying block opens with `$ cd packages/machinome`
   before `$ bump2version patch`; both in place, nothing added.
6. **The history pin** of `test_release_records.py` takes the changelog
   pin's whole shape: the first dashed title is `Unreleased` or the released
   entry, and `Unreleased` occurs once if first and never otherwise. That
   refuses a second `Unreleased` heading anywhere in the file, which the
   design's "at most once" also states.

## 8. Records closing (after the orchestrator's review)

The orchestrator's review of the checkpoint (10 October 2026) accepted the
work to task 7.7, the `parents[3]` correction included, and asked for three
corrections before group 8, made as follows:

- design.md and tasks.md corrected in place, dated: `parents[2]` became
  `parents[3]` in Decision 6's names, Decision 8's rows for
  `test_docs_exports.py` and `test_release_records.py`, and tasks 2.2, 2.4
  and 6.4; Decision 6's "Red at 19c9f83b" paragraph closes with the
  correction's sentence. The spec deltas name no index and are unchanged.
- `CONTRIBUTING.rst`'s two facts (departure 5 above), closed.
- ADR-182's Change link repointed to the archive (below).

### 8.1 ADR-182 accepted (task 8.1)

`docs/adrs/BUILD/ADR-182-the-repository-is-a-monorepo-of-distributions-named-by-directory.md`:
Status **Accepted**; its index entry under BUILD in `docs/adrs/README.md`
reads **Accepted**, cites 018/130. `docs/architecture.md` checked against
it: the identity sentence names `packages/machinome/` (ADR-182), the known
gap names the repository's workflow, and the Map's first row is "Repository
layout", `framework-identity`, 182.

### 8.2 Archive and spec sync (task 8.2)

```
$ env -C <bench>/packages/machinome openspec archive monorepo-layout -y
Task status: 41/44 tasks
Warning: 3 incomplete task(s) found. Continuing due to --yes flag.
Applying changes to openspec/specs/framework-contributor-guidance/spec.md:
  + 1 added
Applying changes to openspec/specs/framework-identity/spec.md:
  + 1 added
Applying changes to openspec/specs/user-documentation/spec.md:
  ~ 3 modified
Totals: + 2, ~ 3, - 0, → 0
Specs updated successfully.
Change 'monorepo-layout' archived as '2026-10-10-monorepo-layout'.
```

`-y` skips the CLI's confirmation prompt; the three incomplete tasks were
8.2 to 8.4, ticked after it. `diff -r` of `openspec/specs` before and after:
the three named specs changed, nothing else. ADR-182's Change link now names
`../../../openspec/changes/archive/2026-10-10-monorepo-layout/`, as ADR-179
and ADR-181 link theirs, and resolves.

```
$ env -C <bench>/packages/machinome openspec validate --specs --strict
Totals: 45 passed, 0 failed (45 items)
```

The archive left the change's files deleted at their old path and untracked
at the archive's; `git add -A packages/machinome/openspec/changes` records
the move.

### 8.3 The plan note (task 8.3)

The root's `workflow/ongoing/monorepo-0.9.md`: cycle 1 gains its **Done**
entry (branch, planning commit 257293d2, the `parents[3]` correction, the
suite count of 7.1, the manual, `scripts/check-dist`'s result, the lock and
the sync, this evidence file); under "Facts the campaign stands on", "4600
passed and 4 skipped at 0.8.1" became "4768 passed, 4 skipped, 6734
subtests, 14 minutes on the line head on 10 October 2026".

### After the archive

The gate and the three docs and release tests, from the package directory
on the bench venv:

```
$ env -C <bench>/packages/machinome <bench>/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_repository_layout.py tests/test_docs_exports.py tests/test_docs_structure.py tests/test_release_records.py
65 passed, 906 subtests passed in 0.93s
```

### 8.4 (task 8.4)

This file is complete to the implementation commit, which is the
orchestrator's; the planning commit 257293d2 is not amended, and nothing is
pushed.
