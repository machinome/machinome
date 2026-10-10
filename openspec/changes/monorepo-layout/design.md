## Context

The first cycle of the 0.9 monorepo campaign (`workflow/ongoing/monorepo-0.9.md`,
"The campaign: the cut", cycle 1), cut from the line `v0.9-base` at 19c9f83b
("workflow: the 0.9 monorepo plan, the cut of the framework's packages") on the
bench `machinome/WTs/v0.9-base-monorepo-layout`. The plan's four decisions,
accepted by the pilot on 10 October 2026, bind it: the record of an extension
package is the framework's (1); one version for the whole set (2); a uv
workspace at the root, setuptools kept, every member installed editable in
compat mode (3); today's tree moves in this cycle (4). Its rule "A record lives
with what it records" and "One licence, stated once" give the root its
contents. The workspace's package standard (`docs/software-package-standard.md`
of the workspace, sections 1.4 and 1.5) gives `context7.json`, the CI's three
jobs and `scripts/check-dist` their shape; its section 1 was written per
repository and is read here per product.

Facts below were read on the bench at 19c9f83b unless marked *inferred*.
Probes ran in the scratch directory
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C1-propose/`
(named `<scratch>` below), never in the bench, with uv 0.11.8, the workspace
venv's Python 3.12.3 and the OpenSpec CLI 1.6.0.

### The tree today

`git ls-files | cut -d/ -f1 | sort | uniq -c` on the bench: 3340 tracked files
in 27 top-level entries: `.claude` 12, `.editorconfig` 1, `.github` 2
(`ISSUE_TEMPLATE.md`, `workflows/python-app.yml`), `.gitignore` 1,
`.readthedocs.yaml` 1, `AI-USE.md` 1, `CONTRIBUTING.rst` 1, `CREDITS.md` 1,
`HISTORY.rst` 1, `LICENSE` 1, `LICENSES` 2, `MANIFEST.in` 1, `Makefile` 1,
`README.rst` 1, `context7.json` 1, `docs` 281, `machinome` 120, `openspec`
1921, `pyproject.toml` 1, `requirements.txt` 1, `requirements_dev.txt` 1,
`setup.cfg` 1, `spike` 23, `tests` 683, `tools` 11, `tox.ini` 1, `workflow`
268. Thirty-four of them are `.log` files under
`workflow/archive/due-dilligence-performance-2026-09-08/remediation/` that the
framework's `.gitignore` matches (`*.log`) and that were added by force
(`git ls-files -ci --exclude-standard | wc -l` is 34, all `.log`); `git mv`
keeps them tracked.

No module under `machinome/` names a repository path: `grep -rn` for
`github.com/machinome/machinome/(blob|tree)` finds none under `machinome/`,
and the one `sys.path` line of `docs/conf.py` (`os.path.abspath('..')`) is
relative to the manual, so it names the package directory after the move.

### The tests that read a path from the repository root

Forty-two test modules read a file through
`Path(__file__).resolve().parents[1]`, `os.path.dirname(BASEDIR)` or the
like (`grep -lE` over `tests/test_*.py` for those spellings and for
`.github`, `context7`, `HISTORY`, `CONTRIBUTING`, `AI-USE` and `LICENSE`).
After the move that root is `packages/machinome/`, which still holds every
file they read except two that become the repository's: the CI workflow
(`test_docs_exports.py`) and `context7.json` (`test_release_records.py`,
`test_context7_states_the_release`). The plan lists only the first; the
second is found here. `HISTORY.rst` is read through its symlink
(`test_release_records.py`, `test_profile_documentation.py`) and resolves.
Fixtures that climb out of a project (`tests/stl_project/parts.py` and
`tests/step_project/parts.py` naming `../../pyproject.toml`,
`test_missing_source_file.py`'s `ABOVE_ROOT`) land on
`packages/machinome/pyproject.toml`, which exists.

### Probes

1. **The root shape uv accepts** (`<scratch>/uv-probe/`, a member
   `packages/demo/` with a regular package `demo` whose `__init__.py` and
   `demo/sub/__init__.py` extend their paths with a copy of
   `machinome._namespace_portions`, and a member `packages/demo-portion/`
   shipping `demo/sub/x.py` with no `__init__.py` at either level, depending
   on `demo`; `demo` has extras `sub = ["demo-portion"]`, `all = ["demo[sub]"]`,
   `dev = ["demo[all]", "packaging"]`). `env -C <root> uv lock`:
   - a root with only `[tool.uv.workspace] members = ["packages/*"]` fails:
     "`demo-portion` is included as a workspace member, but is missing an
     entry in `tool.uv.sources`";
   - the same root with `[tool.uv.sources] demo = { workspace = true }`,
     `demo-portion = { workspace = true }` and
     `[dependency-groups] dev = ["demo[dev]"]`, and no `[project]` table:
     "Resolved 3 packages";
   - a root with a `[project]` table (`name`, `version = "0"`) and
     `[tool.uv] package = false`, same sources and group: "Resolved 4
     packages", the fourth being the root project itself.
2. **Where the editable mode is set.** `uv sync --python 3.12
   --all-packages --all-extras` on the virtual root:
   - default (setuptools' lenient mode): `import demo` gives a namespace
     package (`demo.__file__` is `None`, `demo.__version__` absent) and
     `demo.sub` resolves to the portion alone, because the portion's
     editable finder declares `demo` and `demo.sub` as namespaces through a
     path hook that `PathFinder` consults before the core's finder. The
     core's `__init__.py` never runs. This is stronger than the plan's
     reason for compat mode: the lenient finder does not merely miss a
     portion, it shadows the core;
   - `--config-setting editable_mode=compat` on the sync command: correct
     (`demo/__init__.py` and `demo/sub/__init__.py` run, `demo.sub.x` from
     the portion, `demo.sub.__path__` lists both directories); each
     `__editable__.*.pth` holds the member's directory;
   - `[tool.uv] config-settings = { editable_mode = "compat" }` in the root
     `pyproject.toml`: correct, as above;
   - the same table in each member's `pyproject.toml` and none at the root:
     the lenient result, with no warning. uv reads that setting at the
     workspace root only.
   - A plain `uv sync --python 3.12` at the virtual root (no
     `--all-packages`, no `--all-extras`) installs the default group `dev`,
     so `demo[dev]`, so the portion: correct with the root's compat setting.
3. **The real manifest** (`<scratch>/uv-real/`: the bench's `pyproject.toml`,
   `README.rst` and `machinome/__init__.py` under `packages/machinome/`, the
   licence symlinked). With the root of probe 1's virtual shape, sources
   `machinome = { workspace = true }`, the compat setting and
   `dev = ["machinome[dev]"]`, `uv lock` fails: "machinome-studio was not
   found in the package registry and machinome[studio] depends on
   machinome-studio". uv locks every extra of every member, `--all-extras`
   or not. With `exclude-dependencies = ["machinome-studio"]` it fails next
   on "only machinome-viewer<=0.8.0 is available and machinome[viewer]
   depends on machinome-viewer>=0.8.1": 0.8.1 is tagged, not uploaded. With
   `exclude-dependencies = ["machinome-studio", "machinome-viewer"]`:
   "Resolved 185 packages in 364ms", `uv.lock` 961173 bytes,
   `requires-python = ">=3.11"`, the member recorded as
   `source = { editable = "packages/machinome" }`. `uv sync --python 3.12`:
   175 packages installed; the `.pth` holds `<root>/packages/machinome`;
   `import machinome, cadquery, build123d, OCP, manifold3d, molejo, solid2,
   pytest, yaml` succeeds; `machinome`, `pytest`, `flake8`, `twine` and
   `sphinx-build` are on the venv's `bin/`. uv picks a 3.11 interpreter
   from pyenv when `--python` is not given; the lock is universal either
   way.
4. **setuptools and the symlinks** (`<scratch>/layout-probe/`: `git archive
   HEAD` of the bench, rearranged as Decision 1 states, the five shared
   files symlinked with `ln -s ../../<name>`). `python -m build --outdir
   <scratch>/layout-probe/dist` from `packages/machinome/` with the
   workspace venv: "Successfully built machinome-0.8.1.tar.gz and
   machinome-0.8.1-py3-none-any.whl". The same build from an unmoved
   `git archive` copy: the two sdists' member lists are identical (1020
   entries), `diff -r` of the two unpacked sdists is empty (the five shared
   files are regular files with the root's bytes: `AI-USE.md` 5159,
   `CONTRIBUTING.rst` 9958, `HISTORY.rst` 91102, `LICENSE` 793, `LICENSES/`
   13419 and 17984), the two wheels' member lists are identical (128 files,
   `machinome-0.8.1.dist-info/licenses/LICENSE` and
   `licenses/LICENSES/{CERN-OHL-S-2.0,GPL-2.0-or-later}.txt` among them),
   and the two `METADATA` files are identical. `twine check` passes both
   archives.
5. **The path-reading tests on the moved tree.** The 41 modules of the list
   above but `test_meta.py` (the meta-project harness, run by probe 8),
   from `<scratch>/layout-probe/repo/packages/machinome` with the workspace
   venv and `PYTHONPATH` set to that directory: `4 failed, 557 passed, 2206
   subtests passed in 392.47s`. The four:
   `test_docs_exports.py::ActionsDocsJobBuildsNothingTest::test_builds_with_warnings_as_errors`,
   `::test_installs_the_requirements_alone`, `::test_no_forbidden_step`
   (each `FileNotFoundError` on `packages/machinome/.github/workflows/python-app.yml`),
   and `test_release_records.py::ReleaseRecordsTest::test_context7_states_the_release`
   (`FileNotFoundError` on `packages/machinome/context7.json`).
6. **The archives installed.** The probe's wheel installed with
   `pip install "<wheel>[openscad,stl]"` into a fresh venv under
   `<scratch>/layout-probe/smoke/`: `python -I -c` from that directory
   imports `machinome` from the venv (version 0.8.1), `machinome.node.openscad`
   and `machinome.node.stl`; `License-Expression` is
   `GPL-2.0-or-later OR CERN-OHL-S-2.0+`; the dist-info lists the three
   licence files; `machinome --help` exits 0.
7. **Git on the moved tree.** A fresh repository of the probe's moved copy
   with a root `.gitignore` of `/WTs/`, `/.venv/`, `/.env`, `__pycache__/`,
   `*.py[cod]`: the five links are recorded with mode 120000; a root `.venv/`,
   `.env`, `WTs/` and `packages/machinome/tests/_build/` are ignored; the
   framework's `.gitignore`, now in `packages/machinome/`, still anchors its
   slash patterns (`tests/_build/`, `!tests/vet_projects/*/sim/parts/`) to
   the package directory.
8. **The whole suite on the moved tree's uv venv** (probe 4's copy made a
   workspace with Decision 2's root manifest, `uv lock`, `uv sync --python
   3.12`, then `pytest -q -rs` from `packages/machinome/` with that venv's
   Python, its `bin/` first on `PATH` and no `PYTHONPATH`): `4 failed, 4748
   passed, 20 skipped, 6724 subtests passed in 493.85s`. The four failures
   are probe 5's four, nothing else. The 20 skips: 16 "machinome-viewer not
   installed" (`test_browser_renderer.py` 14, `test_cli_lazy_imports.py` 1,
   `test_scad_presentation.py` 1), the lock excluding the viewer (Decision
   3); 1 networkx absent (`test_connectivity.py`); 1 `jscad` CLI absent; 2
   vendor STEP absent (`test_step_assembly.py`). The sync recipe therefore
   runs the whole suite; the plan's "4600 passed and 4 skipped at 0.8.1"
   was not re-measured here, and task 1.3 measures the base on the
   workspace venv.
9. **Read the Docs** (its documentation, through Context7, 10 October
   2026): a `.readthedocs.yaml` may sit in a subdirectory when the project's
   setting names its path; every path inside it is relative to the
   repository root, not to the file; the setting applies to every version
   of the project; Sphinx runs from the directory holding `conf.py`.

### The manual and the records

`grep -rnE` under `docs/` for `tests/`, `openspec/`, `tools/`, `.github`,
`HISTORY.rst`, `CONTRIBUTING`, `AI-USE`, `spike/`, `workflow/` and links into
`github.com/machinome/machinome/(blob|tree)`, excluding `docs/_build`,
`docs/_exports` and `docs/adrs/`: every hit names a path inside the package
directory and stays true read from it, except four. `docs/reference/api.rst`
shows a command a reader runs, `PYTHONPATH="$PWD" python
tools/generate_running_corpus.py`, which fails from the repository root;
`docs/architecture.md` (not the manual: the build reads `.rst` only) names
`.github/workflows/python-app.yml` in "Known gaps and tensions";
`docs/releases/release-0.5.md` and `release-0.6.md` link `../../HISTORY.rst`,
which resolves to the package directory's symlink. Outside `docs/`:
`README.rst` links `https://github.com/machinome/machinome/blob/main/docs/tutorial/counter/readme.py`;
`docs/project/contributing.rst` links `blob/main/CONTRIBUTING.rst`, which
stays at the root and stays true; `CONTRIBUTING.rst` (moving to the root's
record) installs with `pip install -e ".[dev]"` from the clone, says the
suite runs "from the repository root" and links five times into `docs/`;
`AI-USE.md` names `docs/` and `workflow/` as the framework's.

## Goals / Non-Goals

**Goals:**

- The framework's tree under `packages/machinome/`, unchanged, and the root
  holding only the repository's record and tooling.
- The distribution's archives unchanged, licence texts included, built from
  the package directory.
- One command at the bench root (`uv sync --python 3.12`) that installs the
  set for the suite, and the suite run from the package directory.
- `scripts/check-dist` and a CI `dist` job, so the archives are proved where
  CI runs.
- A gate that fails if the layout drifts, and records that say where things
  are.

**Non-Goals:**

- Any extension package, portion or extra repointing (cycle
  `cut-the-engines` and after); the root manifest is shaped for them but
  this cycle installs one member.
- Any public name, extra, version, dependency, pin, document or viewer API.
- CI on uv, a lock check in CI, the Read the Docs project setting, the
  workspace's `scripts/setup` and `scripts/dev-env`, the package
  standard's other conformance gaps (`make release` uploads, the
  `.claude/` prompts), and any push or upload.

## Decisions

### 1. The inventory: what moves, what stays, what is new

| Today's entry | Destination | Note |
|---|---|---|
| `.claude/` | stays | untouched (plan; a recorded conformance gap) |
| `.editorconfig` | stays | the repository's |
| `.github/` | stays | `ISSUE_TEMPLATE.md` unchanged; `workflows/python-app.yml` edited (Decision 4) |
| `.gitignore` | `packages/machinome/.gitignore` | its patterns are relative to its directory and keep meaning there; a new root `.gitignore` (below) |
| `.readthedocs.yaml` | `packages/machinome/.readthedocs.yaml` | beside the manual (plan); its paths prefixed (Decision 9) |
| `AI-USE.md` | stays, symlinked from the package | the repository's statement; facts edited (Decision 9) |
| `CONTRIBUTING.rst` | stays, symlinked from the package | the repository's guide; facts edited (Decision 9) |
| `CREDITS.md` | `packages/machinome/CREDITS.md` | the framework's bundled material |
| `HISTORY.rst` | stays, symlinked from the package | the set's changelog (decision 2); `Unreleased` added (Decision 7) |
| `LICENSE`, `LICENSES/` | stay, symlinked from the package | unchanged |
| `MANIFEST.in`, `Makefile`, `setup.cfg`, `tox.ini` | `packages/machinome/` | unchanged: every path in them is relative to their directory |
| `README.rst` | `packages/machinome/README.rst` | the framework's README, pinned by `ReadmeTest`; one link edited (Decision 9) |
| `context7.json` | stays | one per repository; `excludeFolders` prefixed (Decision 9) |
| `docs/`, `machinome/`, `openspec/`, `spike/`, `tests/`, `tools/` | `packages/machinome/` | unchanged but for Decisions 6, 8 and 9; this change moves with `openspec/` |
| `pyproject.toml`, `requirements.txt`, `requirements_dev.txt` | `packages/machinome/` | unchanged |
| `workflow/` | `packages/machinome/workflow/` but `ongoing/monorepo-0.9.md` | Decision 10 |

The symlinks, each relative so a clone anywhere resolves them:

| Link | Target |
|---|---|
| `packages/machinome/LICENSE` | `../../LICENSE` |
| `packages/machinome/LICENSES` | `../../LICENSES` |
| `packages/machinome/HISTORY.rst` | `../../HISTORY.rst` |
| `packages/machinome/CONTRIBUTING.rst` | `../../CONTRIBUTING.rst` |
| `packages/machinome/AI-USE.md` | `../../AI-USE.md` |

`MANIFEST.in` and `pyproject.toml`'s `license-files` are unchanged: they
name the five by their package-relative names, and probe 4 shows the
archives carry them as regular files with the root's bytes.

The new root files:

- `README.md`, exactly:

  ```markdown
  # Machinome

  [![Build status](https://github.com/machinome/machinome/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/machinome/machinome/actions/workflows/python-app.yml)

  Source code for machines. This repository holds the Machinome packages,
  each in its own directory under `packages/`, named as the distribution
  it builds.

  | Package | What it is |
  |---|---|
  | [`machinome`](packages/machinome/) | The framework: a whole machine described in Python source, its parts, dimensions, joints, relations, inputs and tests. Manual: <https://machinome.readthedocs.io>. |

  ## Licence

  Every package in this repository is licensed GPL-2.0-or-later or
  CERN-OHL-S-2.0-or-later, at the recipient's choice; see
  [LICENSE](LICENSE) and the texts in [LICENSES](LICENSES/).
  [CONTRIBUTING.rst](CONTRIBUTING.rst) says how to work on them and
  [AI-USE.md](AI-USE.md) how AI is used in their development.
  ```

  It shows the repository and adds nothing: no version, no history, no
  account of the move. It is not the framework's README, which stays the
  package's and keeps its pins.
- `pyproject.toml` and `uv.lock` (Decisions 2 and 3).
- `.gitignore`, exactly:

  ```
  # The repository's leavings. Each package keeps its own .gitignore
  # beside its sources; these are the root's.
  /WTs/
  /.venv/
  /.env
  /dist/
  __pycache__/
  *.py[cod]
  ```

  `/WTs/` holds the workspace's benches (`scripts/dev-env`), `/.venv/` the
  uv sync, `/.env` a bench's ports.
- `scripts/check-dist` (Decision 5).
- `workflow/README.md` and `workflow/ongoing/monorepo-0.9.md` (Decision 10).

### 2. The root manifest: a virtual workspace root

```toml
# The machinome repository: a uv workspace whose members are the
# distributions under packages/, each in the directory named as its
# distribution. The root is no distribution of its own.

[tool.uv.workspace]
members = ["packages/*"]

[tool.uv.sources]
machinome = { workspace = true }

[tool.uv]
# Every member installs editable in compat mode, a .pth line per package
# directory, so a namespace portion's directory is on sys.path where the
# core's path extension (machinome._namespace_portions) admits it. uv reads
# this setting here at the root and nowhere else.
config-settings = { editable_mode = "compat" }
# Two products no index serves yet: machinome-studio is unpublished, and the
# viewer and web-snapshot extras require machinome-viewer 0.8.1, which is not
# uploaded. uv locks every extra of every member, so either would fail the
# lock; each leaves this list when an index serves it.
exclude-dependencies = ["machinome-studio", "machinome-viewer"]

[dependency-groups]
# `uv sync` at the root installs this group by default: the framework's dev
# extra, which installs every kernel the suite runs.
dev = ["machinome[dev]"]
```

The virtual root (no `[project]` table) over the alternative of a
`[project]` with `[tool.uv] package = false`: both lock and sync (probe 1);
the virtual root states "no distribution of its own" by having none, needs
no invented name or version, and adds nothing to the lock. The gate asserts
the absence of `[project]`.

`uv.lock` is generated by `uv lock` at the bench root and committed; it is
not edited by hand. Probe 3 predicts 185 packages.

### 3. The sync recipe, and the setting's place

The bench's environment: `env -C <bench> uv lock`, then `env -C <bench> uv
sync --python 3.12`, which creates `<bench>/.venv`, installs the member
editable in compat mode with the `dev` group (probe 3: 175 packages). The
suite: `env -C <bench>/packages/machinome <bench>/.venv/bin/python -m
pytest`. The plan's decision 3 left the setting's place open between
`[tool.uv] config-settings` and the command's `--config-setting`; probe 2
settles it at the root's `[tool.uv]`: a command-line flag works but every
caller would have to remember it, and the member-level table is ignored
without a warning. `--all-packages` and `--all-extras` are not used: the
default group already installs what the suite needs, and `--all-extras`
would ask for the `viewer`, `web-snapshot`, `mechanics` and `studio` extras,
the first two and the last emptied by the exclusion.

The exclusion's consequence: the bench venv has no viewer, so tests that need
an installed viewer skip there, where the workspace venv (which carries the
viewer editable) runs them. The fallback recipe, the workspace venv with
`PYTHONPATH=<bench>/packages/machinome`, runs them. Probe 8 measured the
difference: 16 tests skip for the viewer on the sync recipe. The applier
records both runs' counts if the sync recipe's skips go beyond those.

### 4. The CI workflow at the root

`.github/workflows/python-app.yml` keeps its name, so the README badge's URL
and the Actions history keep theirs. Its edits, each with its reason:

- Every job but `dist` gains
  `defaults: run: working-directory: packages/machinome`: its `run` steps
  (`pip install -r requirements.txt -r requirements_dev.txt`,
  `black --check machinome tests`, `flake8 ... machinome tests`,
  `coverage run --source machinome -m pytest`, the browser-snapshot
  `pytest tests/...`, `pip install -r docs/requirements.txt`,
  `python -m sphinx -b html -W docs docs/_build`, `make dist`,
  `gh release create ... ./dist/*`) then read the package's files by the
  same relative paths as today. Job-level rather than workflow-level, so
  `dist` runs from the root.
- Every `cache-dependency-path` gains the prefix `packages/machinome/`
  (`requirements.txt`, `requirements_dev.txt`, `docs/requirements.txt`):
  `actions/setup-python` reads it from the repository root, not from the
  run default.
- A `dist` job, after `test` and `docs`:

  ```yaml
    dist:
      runs-on: ubuntu-latest
      needs: [test, docs]

      steps:
        - uses: actions/checkout@v4

        - name: Setup Python
          uses: actions/setup-python@v5
          with:
            python-version: "3.12"

        - name: Install build and twine
          run: pip install build twine

        # Builds every package of the repository, checks the archives and
        # smokes them in a throwaway environment outside the checkout.
        # Uploads nothing.
        - name: Check the distributions
          run: scripts/check-dist
  ```

- The tag-triggered `build` job keeps its shape: its `make dist` and
  `gh release create "$MACHINOME_VERSION" ./dist/*` run from the package
  directory by the job's default, so `./dist/*` is the package's. Only its
  cache paths change.

The `docs` job's pinned command and install line are unchanged
(`test_docs_exports.py` pins `-r docs/requirements.txt` and `sphinx ... -W`),
read from the package directory.

### 5. `scripts/check-dist`, in Python

Python rather than bash: it reads the workspace's members from the root
`pyproject.toml` with `tomllib`, compares the sdist's members with the
files the package directory links, and asserts on installed metadata, none
of which bash does without a second language; the mechanics package's
`check-dist` is the precedent. It runs under whatever interpreter calls it
(`#!/usr/bin/env python3`, executable bit set, the SPDX header), needs
`build` and `twine` importable there (the `dev` extra and the CI step install
both), and:

1. States at its top, in its docstring and in its last line, that it
   uploads nothing.
2. Reads `[tool.uv.workspace] members` from the root `pyproject.toml`,
   expands each glob relative to the root, keeps the directories holding a
   `pyproject.toml`, sorted. Reads each member's distribution name from its
   `[project] name`.
3. Makes a temporary directory with `tempfile.TemporaryDirectory`, and
   refuses to continue if it lies inside the repository.
4. For each member: `python -m build <member> --outdir <tmp>/dist/<name>`
   (sdist, then the wheel built from the sdist, so an sdist missing a file
   fails here); `python -m twine check --strict` on both archives; for every
   entry of the member's directory that is a symlink, the sdist holds
   `<name>-<version>/<entry>` (each file below it, for a directory) as a
   regular file whose bytes equal the link's target.
5. Creates a venv at `<tmp>/venv` with `python -m venv`, and installs every
   member's wheel into it with `pip install`, passing
   `--find-links <tmp>/dist/<name>` for every member so one member's wheel
   satisfies another's requirement, and the extras its smoke names. Today
   the one entry: `machinome` with `[openscad,stl]`.
6. Smokes each member with the venv's `python -I -c`, run in `<tmp>`, from a
   table keyed by distribution name (a member without a row fails the
   script, so the next cycle adds its row). The `machinome` row: import
   `machinome` and assert its `__file__` lies inside the venv; print its
   version; import `machinome.node.openscad` and `machinome.node.stl`;
   assert `importlib.metadata` gives `License-Expression` equal to
   `GPL-2.0-or-later OR CERN-OHL-S-2.0+`; print the dist-info files whose
   path contains `licenses/` and assert `licenses/LICENSE`,
   `licenses/LICENSES/GPL-2.0-or-later.txt` and
   `licenses/LICENSES/CERN-OHL-S-2.0.txt` are among them; then run
   `<venv>/bin/machinome --help` and require exit 0.
7. Prints "Every distribution built, checked, installed and smoked; nothing
   uploaded." Any failure exits non-zero with the command that failed.

Installing the dependencies needs an index; the script says so in its
docstring. It writes nothing inside the repository: `python -m build` with
`--outdir` writes its `build/` and `*.egg-info` scratch in the member
directory, which the package's `.gitignore` already ignores (`build/`,
`*.egg-info/`).

### 6. The gate, red first, and what `check-dist` proves instead

`packages/machinome/tests/test_repository_layout.py`, written before the move
at `tests/test_repository_layout.py`. Names: `PACKAGE =
Path(__file__).resolve().parents[1]`, `REPOSITORY = parents[2]`,
`SHARED = ('LICENSE', 'LICENSES', 'HISTORY.rst', 'CONTRIBUTING.rst',
'AI-USE.md')`. Its assertions:

- **G1, the place.** `PACKAGE == REPOSITORY / 'packages' / 'machinome'`,
  `PACKAGE.name` equals the distribution name read from
  `PACKAGE / 'pyproject.toml'`, and `(REPOSITORY / '.git')` exists.
- **G2, the shared files.** For each of `SHARED`:
  `(PACKAGE / name).is_symlink()`, `os.readlink(PACKAGE / name) ==
  f'../../{name}'`, `(PACKAGE / name).resolve() == (REPOSITORY / name)`, and
  the root's is not a symlink.
- **G3, the manifest.** `PACKAGE / 'MANIFEST.in'` holds the lines
  `include AI-USE.md`, `include CONTRIBUTING.rst`, `include HISTORY.rst`,
  `include LICENSE` and `recursive-include LICENSES *.txt`; and the
  package's `license-files` is `["LICENSE", "LICENSES/*.txt"]`.
- **G4, the workspace.** The root `pyproject.toml` has no `project` table;
  `tool.uv.workspace.members == ['packages/*']`; every directory under
  `REPOSITORY / 'packages'` holds a `pyproject.toml`;
  `tool.uv.sources.machinome == {'workspace': True}`;
  `tool.uv.config-settings == {'editable_mode': 'compat'}`;
  `dependency-groups.dev == ['machinome[dev]']`; `REPOSITORY / 'uv.lock'`
  exists and records `source = { editable = "packages/machinome" }`.
- **G5, the index.** `REPOSITORY / 'context7.json'` exists and
  `PACKAGE / 'context7.json'` does not; every entry of its
  `excludeFolders` is either `workflow` or starts with
  `packages/machinome/`, and every entry but build output (a last
  component `_build`, untracked) is a directory under `REPOSITORY`.
- **G6, the CI.** `REPOSITORY / '.github/workflows/python-app.yml'` exists
  and `PACKAGE / '.github'` does not; every job but `dist` has
  `defaults.run.working-directory == 'packages/machinome'`; every
  `cache-dependency-path` line names a file under `REPOSITORY`; the `dist`
  job needs `test` and `docs` and a step runs `scripts/check-dist`; and
  `tests.test_docs_exports.WORKFLOW` is that file.
- **G7, the root is the repository's.** `README.md`, `.gitignore`,
  `scripts/check-dist` (executable) and `workflow/README.md` exist under
  `REPOSITORY` (the campaign note is not pinned: it leaves `ongoing/` when
  the campaign is archived); none of
  `machinome`, `tests`, `docs`, `openspec`, `tools`, `spike`, `README.rst`,
  `CREDITS.md`, `MANIFEST.in`, `setup.cfg`, `tox.ini`, `Makefile`,
  `requirements.txt`, `requirements_dev.txt`, `.readthedocs.yaml` exists
  there; `PACKAGE / 'workflow' / 'warts.md'` exists; the root `.gitignore`
  names `/WTs/` and `/.venv/`; the root `README.md` links every directory
  under `packages/` as `packages/<name>/` and states
  `docs/conf.py`'s `framework_licence` (whitespace normalised, as
  `test_docs_structure.py` reads the package README).
- **G8, the links.** Every `https://github.com/machinome/machinome/blob/main/<path>`
  or `/tree/main/<path>` in `PACKAGE / 'README.rst'`, the root `README.md`,
  `CONTRIBUTING.rst` and the `.rst` pages under `PACKAGE / 'docs'` names a
  path under `REPOSITORY`; every relative link target of
  `PACKAGE / 'README.rst'` (`` `text <target>`_ ``) exists relative to
  `PACKAGE`, and every relative link target of the root `README.md`
  (`](target)`) and `CONTRIBUTING.rst` exists relative to `REPOSITORY`.

Red at 19c9f83b, before the move, with the gate at `tests/` of the bench:
`REPOSITORY` is the bench's parent `machinome/WTs`, so G1 fails naming
`PACKAGE` (the bench) against `machinome/WTs/packages/machinome`, and every
other group fails on its first missing path. That red is the honest one for
a layout gate: the repository's root is not where the layout puts it. G3
alone is green before the move, since it pins what the move must keep. The
gate is a checkout test, like `test_docs_exports.py`: an unpacked sdist has
no repository above it.

What `check-dist` proves instead: the archives' contents (the five shared
files as regular files with the root's bytes in the sdist, the licence texts
in the wheel's dist-info, the licence expression in the metadata) and that
they install and import. The gate does not build: a build takes tens of
seconds and fetches setuptools into an isolated environment, which the suite
does not do; the gate pins the tree that makes the archives right, and
`check-dist`, run locally by the applier and in CI's `dist` job, proves the
archives.

### 7. The `Unreleased` section of `HISTORY.rst`, and the two pins that refuse it

The brief and the plan say `tests/test_release_records.py` admits one
`Unreleased` section above the released version in `HISTORY.rst`. It does
not: `test_the_history_top_entry_is_the_released_version` asserts
`'unreleased' not in history.split('Machinome 0.8.1')[0].lower()`, and
`test_profile_documentation.py::test_released_status_changelog_and_history`
asserts the same before `machinome 0.7.0`. The test admits the section in
the changelog page only (`titles[0] in ('Unreleased', releases[0])`; the
profile test's `head.replace('\nunreleased\n----------\n', '\n', 1)`).
Probe: prepending the section to a copy of `HISTORY.rst` leaves the first
`Machinome X (date)` heading at 0.8.1 and makes the text before it contain
`unreleased`, so both pins go red. The pin was red the same way while
`HISTORY.rst` carried its last `Unreleased` section before 0.8.0
(`git show bd976691^:HISTORY.rst` opens with it; the pin dates from
1fa25e21, `release-0-7-1`).

The pilot's ruling of 29 September 2026, restated in the workspace's
`skills/write-the-manual/SKILL.md` ("Work after a release"), is that a pin
forbidding the word anywhere above the released section forbids recording
work and is a defect. Both pins are corrected the way the changelog's was:
before the released heading, one `Unreleased` section heading
(`Unreleased\n----------\n`) is admitted, and the word anywhere else is
still refused. In `test_release_records.py` the check becomes: the text
before the first released heading, with its first `Unreleased`/dashes
heading removed, does not contain `unreleased`, and `Unreleased` occurs as a
heading at most once. In `test_profile_documentation.py` the history line
takes the same `replace` the changelog line already has. Red first: the
section is written, both run red, then each pin is corrected (tasks 2.3 to
2.5). The entry's text names no version, so `split('Machinome 0.8.1')`
still splits at the release's heading.

The `user-documentation` requirement "The 0.8.1 release is recorded" states
`HISTORY.rst`'s "top entry" as the release's; the delta makes that the top
*release* entry, with one `Unreleased` section admitted above it. The
manual's changelog page (`docs/project/changelog.rst`) gains no entry: the
cycle changes nothing a project can use.

### 8. The tests whose paths change

| Test | Change | Red before the move, and why |
|---|---|---|
| `test_repository_layout.py` (new) | Decision 6 | G1 to G8 but G3: the bench's parent is not a repository holding `packages/machinome` |
| `test_docs_exports.py` | `PACKAGE = Path(__file__).resolve().parents[1]` (today's `REPO`) and `REPOSITORY = parents[2]`; `WORKFLOW = REPOSITORY / '.github' / 'workflows' / 'python-app.yml'`; `READTHEDOCS` stays `PACKAGE / '.readthedocs.yaml'`; the Read the Docs pins compare with the literals `packages/machinome/docs/requirements.txt` and `packages/machinome/docs/conf.py` (a new `test_configures_the_framework_manual` for `sphinx.configuration`); the CI pin keeps `-r docs/requirements.txt`; `.gitmodules` read at `REPOSITORY` | the three `ActionsDocsJobBuildsNothingTest` tests: `FileNotFoundError` on `machinome/WTs/.github/...`; the two Read the Docs pins: the configuration still says `docs/...` |
| `test_release_records.py` | `REPOSITORY = parents[2]`; `test_context7_states_the_release` reads `REPOSITORY / 'context7.json'`; the history pin of Decision 7 | `FileNotFoundError` on `machinome/WTs/context7.json`; the history pin after task 2.3 |
| `test_profile_documentation.py` | the history line admits one `Unreleased` heading (Decision 7) | after task 2.3: `unreleased` found before `machinome 0.7.0` |
| `test_docs_structure.py` | its `.gitmodules` check reads `REPOSITORY` | not red by itself: an absence check. Its blind spot is shown instead: a `.gitmodules` planted at the bench's root after the move passes today's check and fails the repointed one (task 6.4), then is removed |

Every other test reads through `parents[1]` or `dirname(BASEDIR)` and
passes on the moved tree (probe 5: 557 passed over 41 modules; probe 8 for
the rest). No fixture changes.

### 9. The records and the manual

- **`.readthedocs.yaml`** (beside the manual, as the plan says):
  `python.install` becomes `- requirements: packages/machinome/docs/requirements.txt`
  and `sphinx.configuration: packages/machinome/docs/conf.py`, because Read
  the Docs reads every path in the file from the repository root (probe 9);
  its comment says so and names the project setting the file needs
  (`packages/machinome/.readthedocs.yaml`). Nothing else in it changes, so
  `ReadTheDocsBuildsNothingTest` holds.
- **`context7.json`** (root): each of the seven `excludeFolders` prefixed
  with `packages/machinome/`, and the root `workflow` added (new in this
  cycle, a campaign note, not documentation). `folders` stays empty, so the
  root `README.md`, `CONTRIBUTING.rst` and `AI-USE.md` stay indexed. Rules
  unchanged.
- **`README.rst`** (package): the link
  `docs/tutorial/counter/readme.py <https://github.com/machinome/machinome/blob/main/docs/tutorial/counter/readme.py>`
  becomes `.../blob/main/packages/machinome/docs/tutorial/counter/readme.py`,
  its text unchanged. No other edit: its relative links (`LICENSE`,
  `AI-USE.md`, `CONTRIBUTING.rst`, `docs/contributor-briefing.md`) resolve
  from the package directory through the symlinks, and `ReadmeTest` holds
  (same sections, same word count).
- **`CONTRIBUTING.rst`** (root), facts edited in place, nothing added:
  line 91, "the tutorial's machine under ``docs/tutorial/``" becomes
  ``packages/machinome/docs/tutorial/``; lines 98-103, the paragraph and the
  block become the install from the clone's root, `$ uv sync`, "which
  installs the framework editable with its dev dependencies, every kernel
  the suite runs, into `.venv`", and, without uv, `$ python -m venv .venv`,
  `$ source .venv/bin/activate`, `$ pip install -e "packages/machinome[dev]"`;
  line 105, ``machinome/cli.py`` becomes ``packages/machinome/machinome/cli.py``;
  line 115, "run from the repository root" becomes "run from the
  framework's directory, ``packages/machinome``" with `$ cd packages/machinome`
  as the block's first line; line 180, "this repository's ``openspec/``
  directory" becomes "the framework's ``packages/machinome/openspec/``
  directory, where the ``openspec`` command runs"; line 215, "the manual
  under ``docs/``" becomes "under ``packages/machinome/docs/``"; the five
  relative links (lines 110, 142, 186, 196, 203: `docs/contributor-briefing.md`,
  `docs/adrs/README.md`, `docs/architecture.md`) gain the prefix
  `packages/machinome/`. The other double-backquoted paths (``tests/...``,
  ``tools/...``, ``openspec/specs/``, ``docs/adrs/``) stay: they follow the
  sentence that says the commands run from the package directory, and
  OpenSpec runs there.
- **`AI-USE.md`** (root), lines 58-60: "The manual under `docs/`, the
  architecture synthesis and the ADRs, the OpenSpec records and the notes
  under `workflow/` written since the line" becomes "The framework's
  manual, architecture synthesis, ADRs, OpenSpec records and working notes
  under `packages/machinome/`, and the notes under `workflow/`, written
  since the line". Nothing else.
- **`docs/contributor-briefing.md`**: its "Layout" section opens with one
  sentence, "The framework is the directory `packages/machinome/` of the
  repository; the paths below are relative to it." Its links stay
  relative and resolve.
- **`docs/reference/api.rst`**, the conformance corpus's block: a first line
  `$ cd packages/machinome` before `$ PYTHONPATH="$PWD" python
  tools/generate_running_corpus.py`. The page keeps its shape.
- **`docs/architecture.md`**: in "The big picture", the identity
  paragraph's "and the source repository is `machinome/machinome`" becomes
  "and the source repository is `machinome/machinome`, where the framework
  is the directory `packages/machinome/` (ADR-182)"; in "Known gaps and
  tensions", "(`.github/workflows/python-app.yml`)" becomes "(the
  repository's `.github/workflows/python-app.yml`)"; in the Map, a first
  row whose subsystem is "Repository layout", whose code is the repository
  root (its `pyproject.toml`, `uv.lock`, `scripts/check-dist` and CI
  workflow) and `packages/machinome/`, whose spec capability is
  `framework-identity` and whose ADR is 182.
- **`docs/adrs/README.md`**: ADR-182 under BUILD, after ADR-179.
- The `.rst` pages under `docs/` other than `api.rst` and
  `project/contributing.rst` name no repository path that leaves the
  package; `project/contributing.rst`'s link to `blob/main/CONTRIBUTING.rst`
  stays true. The write-the-manual rules hold: no page changes shape, no
  release fact moves.

### 10. `workflow/`: the repository's and the framework's

`git mv workflow packages/machinome/workflow` is wrong by one file: the
campaign note stays. The move is
`git mv workflow/README.md workflow/warts.md workflow/archive packages/machinome/workflow/`
and every entry of `workflow/ongoing/` but `monorepo-0.9.md` into
`packages/machinome/workflow/ongoing/`. The root `workflow/README.md`, new,
exactly:

```markdown
# `workflow/`: the repository's working record

The working record of what spans the repository's packages: the campaigns
that move, cut or join them, under `ongoing/` while they run and
`archive/<campaign>-<YYYY-MM-DD>/` once finished. Each product keeps its own
record in its directory: the framework's is
[`packages/machinome/workflow/`](../packages/machinome/workflow/README.md),
whose conventions this directory follows. Nothing here is ratified; a
product's specs and accepted ADRs outrank it.
```

The framework's `workflow/README.md` gains, at the end of "Where this
fits", one sentence: "A campaign that spans the repository's packages is
recorded in the repository's `workflow/` at its root, as the 0.9 monorepo
campaign is (`workflow/ongoing/monorepo-0.9.md`)." Its other statements
stay true read from the package directory. The campaign note stays where
it is and gains only the cycle's entry once the cycle is validated (tasks
8.3), as the lean-core plan recorded its cycles.

### 11. The decision record: ADR-182, BUILD

The last ADR is ADR-181 (NODE, `root-cleanup`); 182 is free in every
category (`find docs/adrs -name 'ADR-18*'`). BUILD, beside ADR-130 ("Machinome
is a clean package and command boundary"), which fixed the distribution, the
import package, the command and the repository; this one fixes where in the
repository the distribution lives and what the repository's root holds. It
crosses no process boundary (not IPC) and no node or engine (not NODE).

`docs/adrs/BUILD/ADR-182-the-repository-is-a-monorepo-of-distributions-named-by-directory.md`,
written by the applier with Status **Proposed** (task 6.8) and promoted to
**Accepted** after review (task 8.1),
Date 2026-10-10, Change `monorepo-layout`, Related to ADR-130 and ADR-018.
Context: the plan's direction of 10 October 2026 and its four decisions.
Considered options: (1) the framework under `packages/machinome/`, the root
the repository's, chosen; (2) the framework stays at the root and siblings
go under `packages/`: the root's record would be the framework's and a
second product's would sit inside it, against "a record lives with what it
records"; (3) one repository per distribution: refused by the plan ("one
product with one release"). Decision: a directory under `packages/` per
distribution, named as the distribution; the repository's record at the
root (licence, contributor guide, AI-use statement, history, CI, scripts,
campaigns that span products) and each product's in its directory; the
licence texts at the root only, reached from each package directory by
relative symlinks that setuptools carries into the archives as files; a uv
workspace at the root, virtual, with every member editable in compat mode
set in the root's `[tool.uv]`, products no index serves excluded from the
lock by name, and the `dev` group naming the core's `dev` extra; setuptools
kept as the build backend. Consequences: paths in the framework's records
are relative to `packages/machinome/`; the suite runs there; Read the Docs
reads a configuration path per project; the editable lenient mode is unfit
for portions (probe 2); a later product joins as a plain move into its
directory.

### 12. The spec deltas

- `framework-identity`: ADDED "The framework is the package directory
  `packages/machinome` of a monorepo", with scenarios for a clone's layout,
  the shared licence, the workspace sync and the archives' contents.
- `framework-contributor-guidance`: ADDED "The contributor guide states the
  monorepo's development setup".
- `user-documentation`: MODIFIED "The README describes the package" (its
  first sentence: the package directory's landing page and the
  distribution's long description; the repository's landing page is the
  root `README.md`), "The documentation build produces nothing" (the Read
  the Docs configuration beside the manual names the manual's paths from
  the repository root; the CI docs job runs from the package directory),
  and "The 0.8.1 release is recorded" (the top release entry, one
  `Unreleased` section admitted above it). Each copied whole and edited.

## Risks / Trade-offs

- [Read the Docs builds nothing from the pushed line until its project
  setting names `packages/machinome/.readthedocs.yaml`; once set, the
  setting applies to every version, and a rebuild of an older tag, which
  has no such file, fails] → Nothing is pushed by this campaign; the
  setting is the pilot's, before the line is pushed (Open Questions 1).
  Versions already built stay hosted.
- [The bench venv lacks the viewer while `machinome-viewer` is excluded from
  the lock] → The viewer-dependent tests skip there; the fallback recipe
  runs them; the exclusion leaves the list when 0.8.1 is uploaded.
- [A developer runs `pytest` from the repository root] → pytest finds no
  configuration there and collects nothing useful; `CONTRIBUTING.rst` says
  where the suite runs. Not guarded by a test.
- [A tool resolves a symlinked file differently from setuptools, for example
  an archive tool that stores links] → Probe 4 shows setuptools stores
  files; `check-dist` compares each linked file's bytes in every build.
- [Windows clones without symlink support check the links out as text
  files] → The framework's development is on Linux; recorded, not
  addressed.
- [A bench made by today's `scripts/dev-env` is the whole repository, so its
  `.env` lands at the root] → The root `.gitignore` ignores `/.env`; the
  workspace's scripts change at the campaign's close.

## Migration Plan

Within the cycle, in the order of tasks.md: red tests at today's paths; the
`HISTORY.rst` section and its two pins; the move by `git mv` (the suite
runnable from `packages/machinome/` with the fallback recipe as soon as it
lands); the symlinks; the root files; the records; the lock and the sync;
validation. Rollback is a revert of the implementation commit; nothing
outside the repository changes. After the cycle, outside it: the workspace's
`scripts/setup`, `scripts/dev-env` and `docs/collaborator-setup.md`, the
operating contract's layout paragraph, and the Read the Docs setting.

## Open Questions

1. **Where `.readthedocs.yaml` lives.** The plan keeps it beside the manual,
   and this design does. Probe 9 adds two facts the plan did not state: its
   paths are the repository root's, so it names `packages/machinome/docs/...`;
   and the project's configuration-path setting applies to every version,
   so after it is set an older tag cannot be rebuilt. The alternative is
   the root, with the same prefixed paths and no setting, older tags still
   building from their own root file. Recommendation: beside the manual, as
   the plan says, because each product joining later brings its own manual
   and Read the Docs project, and a per-product file is the shape that
   scales; the pilot sets the path before the line is pushed.
2. **Whether the `dev` extra keeps `machinome[all]`.** It does in this
   cycle: the root group names `machinome[dev]`, which brings every kernel
   the suite runs, and from cycle 2 `all` reaches the sibling packages
   through the core's extras. Recommendation: keep it; the suite runs
   against the whole set.
3. **Whether `requirements.txt` and `requirements_dev.txt` stay.** They feed
   CI's pip install and cache, `tox.ini` and
   `test_kernel_extras.py::test_ci_installs_every_concrete_requirement_of_all`.
   Recommendation: keep them in this cycle, unchanged in the package
   directory; retire them in the change that moves CI onto `uv sync
   --locked`, which also gives CI the lock check.
4. **The workflow's name.** The package standard names it `ci.yml`.
   Recommendation: keep `python-app.yml` here, since a rename moves the
   README badge, the Actions history and a pinned test path for no gain in
   this cycle; rename it, if wanted, with the change that moves CI onto uv.
5. **The viewer's exclusion from the lock.** Recommendation: keep it until
   the pilot uploads `machinome-viewer` 0.8.1, then remove it in the next
   change that touches the root manifest, so the bench venv carries the
   viewer from the index.
