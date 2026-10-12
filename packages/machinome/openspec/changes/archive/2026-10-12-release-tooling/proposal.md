## Why

Machinome 0.8.1 was released by hand across two repositories on 10 October
2026: the framework's sdist and wheel were built into the framework
checkout's `dist/0.8.1-2026-10-10/`, the viewer's into the viewer
checkout's own `dist/0.8.1-2026-10-10/`, two archives each, which no script
checked, installed or smoked (`scripts/check-dist` came later that day, with
the monorepo's first cycle); the steps were a checklist in
the framework's working record (`packages/machinome/workflow/ongoing/release-0.8.1.md`:
upload the viewer first, push `main` and the tag, upload the framework's
archives built at the tagged commit), and the change `release-0-8-1`
(`openspec/changes/archive/2026-10-10-release-0-8-1/`) recorded the version
moved in five files and the suite run by a recipe written into its evidence.
The repository now holds fifteen distributions (thirty archives) and will hold
seventeen with the movie and the studio; three products keep their tests in
their own directories, the movie will be a fourth with a Node suite, and the
movie's Node side will be the npm workspace's second member. A release by hand
is fifteen builds and a list of commands to remember. The pilot decided on
12 October 2026 (`workflow/ongoing/release-0.9.md` at the repository root,
decisions 2 and 10) that 0.9.0 is released with one command per step, declared
once: this change is that tooling, the third cycle of that note's road.

## What Changes

- **A `Makefile` at the repository root** with the targets `version`,
  `bump VERSION=`, `sync`, `test [PKG=]`, `lint`, `docs`, `widget`, `dist`,
  `upload`, `check` and `clean`, and `help`, the default, listing them one line
  each. It declares the repository's packages once (`PACKAGES`, every directory
  under `packages/`), the packages with tests of their own (`TESTED`) and the
  set's version, read from `current_version` of `.bumpversion.cfg`. It finds
  `uv` and `npm` on the PATH and the workspace's commands in `.venv/`; every
  target runs from a fresh clone after `make sync` (design.md, Decisions 1
  to 9).
- **The version is declared in one place**, `current_version` of the root's
  `.bumpversion.cfg`; every manifest, pin and release fact is a copy the
  release-records test holds to it. `make bump VERSION=X.Y.Z` moves every copy
  with bump2version, the root's npm lock and each npm member's own lock with
  npm, and `uv.lock` with uv, and prints what changed; it never commits and
  never tags, and `.bumpversion.cfg` loses its `commit = True` and
  `tag = True` (Decision 3). The bump to 0.9.0 itself is the road's last cycle;
  this change leaves the version at 0.8.1 and proves the bump on a copy.
- **`scripts/check-dist --out DIR`** keeps the archives it built, checked,
  installed and smoked, flat in `DIR`, once every one has passed; it refuses a
  `DIR` that exists and is not empty before it builds anything. Without the
  option it behaves as today (Decision 10). `make dist` runs it with
  `--out dist/vX.Y.Z` on a copy of the checked-out commit, refusing a
  checkout that differs from it, so no ignored build directory enters an
  archive (the 0.7.1 sdist kept in the framework's checkout carries 256 such
  entries) and `make upload` (`twine upload dist/vX.Y.Z/*`) uploads the bytes
  proved; no target runs both, and no target sweeps the projects (Decision
  7).
- **`scripts/check-dist` parses again**: the line's head (40087800) lost the
  closing brace of the viewer's smoke row when `join-skills` was merged
  beside `join-viewer`, so the script fails `SyntaxError: '{' was never
  closed` before it does anything; the brace is restored (Decision 10).
- **CI calls the targets**: each job keeps its setup steps (uv and the locked
  workspace, Node, OpenSCAD, Chromium) and runs `make lint`, `make widget`
  and `make test`, `make docs`, `make check`, and on a tag `make dist`, in
  place of the commands it spells today (Decision 11).
- **The framework's own `packages/machinome/Makefile` goes**: its `release`
  target chains a build and `twine upload dist/*`, and its other targets
  predate the monorepo (Decision 1).
- **The gates, red first** (Decision 12): the layout test holds the
  Makefile's package list to the directories of `packages/`, its tested list
  to the products, its targets and their help, `upload` reached by no other
  target, `clean`'s paths all ignored, and the workflow's jobs to the targets;
  the docs-build test reads the `docs` target; the release-records test reads
  the version from `.bumpversion.cfg`; a new test drives `scripts/check-dist
  --out` without building.
- **Records**: `CONTRIBUTING.rst` names the commands (its setup, tests and
  Deploying sections); `HISTORY.rst` gains its `Unreleased` bullet;
  `docs/architecture.md`'s repository-layout row names the Makefile; ADR-192
  records the decision; the root `.gitignore` names the docs venv (Decision
  13).

Not in this change: the bump to 0.9.0, any tag, push or upload (the pilot's);
a target for the universe sweep or the browser-snapshot capture; the
workspace's `scripts/setup` and `scripts/dev-env`, which keep their own
commands until the workspace's consistency cycle; the Read the Docs
configuration, unchanged.

## Capabilities

### New Capabilities

- `release-tooling`: the root Makefile's contract: its targets and what each
  runs, the package lists the layout gate holds, the version declared once and
  moved by `make bump`, `scripts/check-dist --out`, what `dist`, `upload` and
  `clean` never do, and CI on the targets.

### Modified Capabilities

- `framework-identity`: the requirement on the monorepo states the set's
  version as declared by `current_version` of `.bumpversion.cfg`, the root
  holding the `Makefile`, and the CI running `scripts/check-dist` through
  `make check`.
- `framework-contributor-guidance`: the contributor guide states the setup,
  the tests and the release by the Makefile's targets, and the CI scenario
  reads the targets.
- `user-documentation`: the requirement that the documentation build produces
  nothing names the Makefile's `docs` target as the CI's build, installing
  `packages/machinome/docs/requirements.txt` alone into its own environment.

The release record of 0.8.1 (`user-documentation`, "The 0.8.1 release is
recorded") states facts that stay true at 0.8.1 and is unchanged; the 0.9.0
release cycle adds its own.

## Impact

- **New files**: the root `Makefile`; `packages/machinome/tests/test_check_dist.py`;
  ADR-192 (BUILD).
- **Removed**: `packages/machinome/Makefile`.
- **Changed**: `scripts/check-dist` (the brace, `--out`, its docstring);
  `.bumpversion.cfg` (two lines out); `.github/workflows/python-app.yml`;
  `.gitignore` (`/.docs-venv/`); `tests/test_repository_layout.py`,
  `tests/test_docs_exports.py`, `tests/test_release_records.py`;
  `CONTRIBUTING.rst`, `HISTORY.rst`, `docs/architecture.md`,
  `docs/adrs/README.md` and the status lines of ADR-182 and ADR-183.
- **Unchanged**: every distribution's contents and version, every module of
  every package, the manual's pages, the Read the Docs configuration, the
  lock files (but where a probe on a copy rewrites them).
- **The movie's join** (`join-movie`) lands on the line before this change's
  implementation: the Makefile lists `machinome-movie` in `PACKAGES` and
  `TESTED`, its Node lock in the bump, and its tests in `make test`, as that
  join lands them.

Originating evidence: the pilot's decisions of 12 October 2026
(`workflow/ongoing/release-0.9.md`, 2 and 10), the 0.8.1 release's record
(`openspec/changes/archive/2026-10-10-release-0-8-1/`,
`workflow/ongoing/release-0.8.1.md`), and the probes in design.md.
