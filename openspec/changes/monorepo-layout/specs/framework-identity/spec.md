## ADDED Requirements

### Requirement: The framework is the package directory `packages/machinome` of a monorepo

The repository `machinome/machinome` SHALL be a monorepo whose
distributions each live in a directory under `packages/` named as the
distribution: the framework, the distribution `machinome`, SHALL live at
`packages/machinome/`, with its import package, tests, manual,
architecture synthesis, decision records, OpenSpec records and working
record, and any other directory under `packages/` SHALL be a sibling
distribution of the same repository. Paths named in the framework's specs,
decision records and manual SHALL be read relative to `packages/machinome/`
unless they name the repository root.

The repository root SHALL hold the repository's record and tooling and no
distribution of its own: the licence texts (`LICENSE`, `LICENSES/`), the
contributor guide (`CONTRIBUTING.rst`), the AI-use statement (`AI-USE.md`),
the history (`HISTORY.rst`), `README.md`, `context7.json`, the CI workflow
under `.github/workflows/`, `scripts/check-dist`, the record of the
campaigns that span packages under `workflow/`, and a `pyproject.toml` that
declares a uv workspace whose members are `packages/*`, with its `uv.lock`,
and no `[project]` table. The workspace SHALL install every member editable
in compat mode, set at the root, and its default `dev` group SHALL install
the framework's `dev` extra.

The licence SHALL be stated once, at the root. The framework's directory
SHALL reach `LICENSE`, `LICENSES`, `HISTORY.rst`, `CONTRIBUTING.rst` and
`AI-USE.md` through relative symbolic links to the root's files, and the
framework's sdist and wheel SHALL carry them as regular files with the
root's contents, so the archives a release builds are the archives it
built before the layout.

`scripts/check-dist` SHALL build the sdist and the wheel of every member of
the workspace outside the repository, check them with `twine check
--strict`, install the wheels into a throwaway environment outside the
repository, import and smoke each there, and upload nothing; the CI SHALL
run it in a `dist` job after its `test` and `docs` jobs.

#### Scenario: A contributor clones the repository

- **WHEN** a contributor clones `github.com/machinome/machinome`
- **THEN** the framework's `pyproject.toml`, `machinome/`, `tests/`,
  `docs/` and `openspec/` are under `packages/machinome/`, and the root
  holds the repository's record, the workspace manifest and its lock, and
  none of the framework's sources

#### Scenario: The licence is reached from the package directory

- **WHEN** `packages/machinome/LICENSE`, `LICENSES`, `HISTORY.rst`,
  `CONTRIBUTING.rst` or `AI-USE.md` is read
- **THEN** it is a relative symbolic link resolving to the root's file of
  the same name, and the layout test fails naming the entry if it is a
  copy or resolves elsewhere

#### Scenario: The archives carry the licence

- **WHEN** `scripts/check-dist` builds the framework from
  `packages/machinome/`
- **THEN** the sdist holds the five linked entries as regular files whose
  bytes equal the root's, the wheel's metadata holds the licence texts
  under its `licenses/` directory, the installed distribution states
  `GPL-2.0-or-later OR CERN-OHL-S-2.0+`, and nothing is uploaded

#### Scenario: A developer syncs the workspace

- **WHEN** `uv sync` runs at the repository root
- **THEN** the framework is installed editable in compat mode from
  `packages/machinome/` with its `dev` extra, and the suite runs from
  `packages/machinome/`

#### Scenario: The root manifest declares a distribution

- **WHEN** the root `pyproject.toml` gains a `[project]` table, or its
  workspace stops naming `packages/*`
- **THEN** the layout test fails naming the table
