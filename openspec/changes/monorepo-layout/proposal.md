## Why

The pilot set the direction of Machinome 0.9 on 10 October 2026: the
machinome repository becomes a monorepo of several packages, every one under
the one licence the framework carries, and the first step is the cut of the
framework's own modules into the ten extension packages the lean-core
campaign locked (`workflow/ongoing/monorepo-0.9.md`, "What 0.9 is" and
"Decisions accepted by the pilot"). The cut needs a layout to cut into: a
directory per distribution under `packages/`, the repository's own record at
the root, one licence stated once, and a uv workspace that installs the set.
The plan's decision 4 moves today's tree in this first cycle, so each later
cycle founds a sibling directory and each later join is a plain move. Today
the framework's tree is the repository root: there is no place for a second
distribution, and the licence, the history, the CI and the record of a
campaign that spans packages have no home that is not the framework's.

## What Changes

- **The framework's tree moves under `packages/machinome/` unchanged**,
  with `git mv`: the import package `machinome/`, `tests/`, `docs/` with
  `.readthedocs.yaml` beside it, `openspec/` (this change included),
  `workflow/` (all but the campaign note), `tools/`, `spike/`,
  `pyproject.toml`, `setup.cfg`, `tox.ini`, `Makefile`, `MANIFEST.in`,
  `requirements.txt`, `requirements_dev.txt`, `README.rst`, `CREDITS.md` and
  `.gitignore`. No module, test fixture, manual page or manifest changes
  for the move itself (design.md, Decision 1).
- **The root becomes the repository's.** It keeps `LICENSE` and `LICENSES/`
  (unchanged), `CONTRIBUTING.rst`, `AI-USE.md` and `HISTORY.rst` (now the
  repository's), `context7.json` (its excluded folders prefixed with the
  package directory), `.github/` (the workflow's jobs run from the package
  directory, and a `dist` job runs `scripts/check-dist` after `test` and
  `docs`), `.editorconfig` and `.claude/` (untouched); and gains a
  `README.md` (the monorepo: what it is, its packages, its licence), a
  `pyproject.toml` that is a uv workspace with the one member and no
  distribution of its own, `uv.lock`, a `.gitignore` for the repository's
  leavings, `scripts/check-dist`, and `workflow/` holding the campaign note
  `ongoing/monorepo-0.9.md` and a `README.md` stating that the root's record
  is the repository's and each product's is in its directory.
- **One licence, stated once.** `packages/machinome/LICENSE`, `LICENSES`,
  `HISTORY.rst`, `CONTRIBUTING.rst` and `AI-USE.md` are relative symlinks
  to the root's files, so the sdist and the wheel carry them as before:
  archives built from the moved tree list the same files with the same
  bytes as archives built from today's (design.md, Context, probe 3).
- **A uv workspace at the root.** `uv lock` and `uv sync --python 3.12` at
  the root install the framework editable in compat mode with its `dev`
  extra, which installs every kernel; the root names the two products no
  index can serve today, `machinome-studio` (unpublished) and
  `machinome-viewer` at the `viewer` extra's floor 0.8.1 (not uploaded), as
  excluded from the lock (design.md, Decision 3).
- **`scripts/check-dist`, founded.** For every member of the workspace it
  builds the sdist and the wheel outside the repository, runs
  `twine check --strict`, checks that the sdist carries each symlinked file
  as a regular file with the root's bytes, installs the wheels into a
  throwaway environment (the core with its `openscad` and `stl` extras),
  imports and smokes them there, lists the licence files of the installed
  metadata, and uploads nothing.
- **The gate, red first** (`tests/test_repository_layout.py`): the
  repository root is two levels above the test and holds
  `packages/machinome`; the five shared files are symlinks resolving to the
  root's; the root manifest is a workspace naming the member and declaring
  no project; `context7.json` is at the root and every folder it excludes
  exists; the CI workflow is at the root, its jobs run from the package
  directory and its `dist` job runs `scripts/check-dist`; `MANIFEST.in`
  still names the five files; the framework's entries are absent from the
  root; every link from `README.rst`, the root `README.md` and
  `CONTRIBUTING.rst` into the repository resolves.
- **The tests that read a moved file read it where it is now:**
  `test_docs_exports.py` reads the workflow at the repository root and pins
  the Read the Docs configuration's repository-relative paths;
  `test_release_records.py` reads `context7.json` at the root. Measured on
  a scratch copy of the moved tree, the move alone turns exactly these four
  tests red among the 41 path-reading test files (design.md, Context,
  probe 4).
- **`HISTORY.rst` gains its `Unreleased` section**, with this entry:

  ```
  Unreleased
  ----------

  * **The framework is a PACKAGE of its repository.**
    The framework's tree moved, unchanged, under ``packages/machinome/``,
    the directory named as its distribution; the repository root holds the
    licence, stated once and reached from the package by symbolic links,
    the contributor guide, this history, the AI-use statement, the CI, a
    uv workspace with its lock, ``scripts/check-dist`` and the record of
    the campaigns that span packages. The distribution, its import
    package, its command, its extras and the contents of its archives are
    unchanged. Change ``monorepo-layout`` (ADR-182).
  ```

  Two pins refuse the word "unreleased" anywhere above the released
  version in `HISTORY.rst` (`test_release_records.py` and
  `test_profile_documentation.py`), so the section is red against them
  today; each is corrected to admit one `Unreleased` section, as the
  changelog's pin already does (design.md, Decision 7).
- **The records that name a path follow:** `CONTRIBUTING.rst` (the
  development install from the root, the suite run from the package
  directory, its links from the root), `AI-USE.md` (where the framework's
  records are), `README.rst` (one link into the repository), the
  contributor briefing (its paths are the package directory's), the
  conformance-corpus command in `docs/reference/api.rst`,
  `docs/architecture.md` (the identity paragraph, the Map, one known gap),
  the ADR index, the framework's `workflow/README.md` (where the campaign
  note went) and `.readthedocs.yaml` (Read the Docs reads every path in it
  from the repository root).

Not in this change: the extension packages (cycle `cut-the-engines` and
after), any public name, extra, version, dependency or pin, the Read the
Docs project setting (the pilot's, at release), CI on uv, the workspace's
`scripts/setup` and `scripts/dev-env` (the campaign's close, in the
workspace repository), and any push or upload.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `framework-identity`: the framework lives at `packages/machinome` of the
  repository `machinome/machinome`, a monorepo whose other directories
  under `packages/` are its sibling distributions, each named as its
  distribution; the root holds the one licence, symlinked into each package
  directory, the uv workspace and `scripts/check-dist`; paths in the
  framework's records are relative to the package directory (new
  requirement).
- `framework-contributor-guidance`: the contributor guide at the
  repository root states the development install from the root and the
  suite run from the package directory, and the contributor briefing says
  its paths are the package directory's (new requirement).
- `user-documentation`: the README is the package directory's landing page
  and the distribution's long description, the repository's being the root
  `README.md`; the Read the Docs configuration names the manual's paths
  from the repository root; work landed after a release is recorded in one
  `Unreleased` section above the released entry of `HISTORY.rst` (modified
  requirements "The README describes the package", "The documentation
  build produces nothing" and "The 0.8.1 release is recorded").

## Impact

- **Tree.** Every tracked path but `LICENSE`, `LICENSES/`,
  `CONTRIBUTING.rst`, `AI-USE.md`, `HISTORY.rst`, `context7.json`,
  `.github/`, `.editorconfig`, `.claude/` and
  `workflow/ongoing/monorepo-0.9.md` gains the prefix
  `packages/machinome/`. A clone's working copy, a bench's `.env`, a
  `tests/_build` and every path a developer types move with it.
- **Code.** None: no module under `machinome/` names a repository path
  (`grep` in design.md, Context).
- **Tests.** New: `tests/test_repository_layout.py`. Changed:
  `test_docs_exports.py`, `test_release_records.py`,
  `test_profile_documentation.py`, `test_docs_structure.py` (its
  `.gitmodules` check reads the repository root).
- **Build and CI.** The distribution is built from `packages/machinome/`;
  its archives are unchanged. The CI's jobs run from the package
  directory; a `dist` job is new. Read the Docs needs its configuration
  path set to `packages/machinome/.readthedocs.yaml` before the line is
  pushed (design.md, Open Questions).
- **Developers.** The suite runs from `packages/machinome/`. A bench is
  synced with uv at its root; the workspace venv with
  `PYTHONPATH=<bench>/packages/machinome` remains the fallback. The
  workspace's `scripts/setup` and `scripts/dev-env`, the collaborator
  guide and the operating contract's layout paragraph change at the
  campaign's close, outside this repository.
- **Records.** ADR-182 (BUILD); the three delta specs; `HISTORY.rst`.

Originating evidence: `workflow/ongoing/monorepo-0.9.md` (the plan, written
from the workspace conversation of 10 October 2026: "The rule", "The
layout", "Decisions accepted by the pilot" 1 to 4, "The campaign: the cut",
cycle 1), the workspace's package standard
(`docs/software-package-standard.md`, sections 1.4 and 1.5: `context7.json`,
the CI's `test`, `docs` and `dist` jobs, `scripts/check-dist`), and the
probes recorded in design.md.
