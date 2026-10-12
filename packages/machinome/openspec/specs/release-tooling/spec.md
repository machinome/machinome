# release-tooling Specification

## Purpose

Give the repository's steps, of working on the set and of releasing it, one
command each, declared once in a Makefile at the root that contributors, CI
and the maintainer run alike: the set's version declared in one place and
moved without a commit or a tag, the archives a release uploads being the
archives built from its commit, checked, installed and smoked, and no target
uploading what another built.
## Requirements
### Requirement: The repository's steps are the targets of one Makefile at its root

The repository root SHALL hold a `Makefile` whose targets are the steps of
working on and releasing the set: `version`, `bump`, `sync`, `test`, `lint`,
`docs`, `widget`, `dist`, `upload`, `check` and `clean`, with `help` as the
default target, which SHALL list every target with one line saying what it
does. These SHALL be the only targets with a help line, and none of them SHALL
run the universe sweep. The Makefile SHALL declare the repository's packages
once, in a list naming every directory under `packages/`, and the packages
with tests of their own in a second list, the framework and every product
that keeps its tests in its directory. It SHALL find `uv` and `npm` on the
PATH and the workspace's commands in the root's `.venv/`, so that every
target runs from a fresh clone after `make sync` without an activated
environment, and it SHALL run one step at a time even when make is asked for
parallel jobs. The framework's directory SHALL hold no Makefile of its own.

#### Scenario: A contributor asks what the steps are

- **WHEN** a contributor runs `make` at the root of a clone
- **THEN** it prints the twelve targets, one line each with what it does, and
  runs nothing else

#### Scenario: A package directory is not in the Makefile's list

- **WHEN** a directory under `packages/` is missing from the Makefile's
  package list, or the list names a directory that does not exist
- **THEN** the layout test fails naming the directory

#### Scenario: A product's tests are not in the tested list

- **WHEN** a product that keeps its tests in its directory is missing from the
  Makefile's list of packages with tests, or has no rule that runs them
- **THEN** the layout test fails naming the product

#### Scenario: The framework keeps a Makefile of its own

- **WHEN** `packages/machinome/Makefile` exists
- **THEN** the layout test fails naming it

### Requirement: The set's version is declared once and moved by `make bump`

The set's version SHALL be declared in one place, `current_version` of the
root's `.bumpversion.cfg`; every manifest's version numbered with the set,
every pin between the set's distributions and every release fact that states
the version SHALL be a copy that the release-records test holds to that
declaration. `make version` SHALL print it. `make bump VERSION=X.Y.Z` SHALL
refuse when `VERSION` is not given, when it equals the current version, or
when a tracked file has changes, naming them; otherwise it SHALL move every
copy the configuration names with bump2version, the root npm lock's member
entries with npm, the lock each npm member keeps of its own with npm in a
copy outside the workspace, and `uv.lock`'s member entries with uv, then
print the files it changed. It SHALL NOT commit and SHALL NOT tag, and the
configuration SHALL NOT tell bump2version to commit or tag.

#### Scenario: The maintainer bumps the set

- **WHEN** `make bump VERSION=0.9.0` runs on a clean checkout at 0.8.1
- **THEN** `current_version`, every manifest's version and pin, the files that
  restate the version, the root npm lock's member entries, each member's own
  lock and `uv.lock`'s member entries read 0.9.0, the changed files are
  listed, and no commit or tag is made

#### Scenario: The bump is asked of a tree with changes

- **WHEN** `make bump VERSION=0.9.0` runs while a tracked file has changes
- **THEN** it refuses, listing the changed files, and changes nothing

#### Scenario: A copy disagrees with the declaration

- **WHEN** `current_version` says one version and a manifest, a pin or a
  release fact another
- **THEN** the release-records test fails naming the copy left behind

#### Scenario: The configuration asks to commit or tag

- **WHEN** the `[bumpversion]` section of `.bumpversion.cfg` holds a key
  other than `current_version`
- **THEN** the release-records test fails naming it

### Requirement: The workspace, the bundles, the lint and the manual have a target each

`make sync` SHALL install the uv workspace (`uv sync --python 3.12`), the npm
workspace from its lock (`npm ci`) and the Chromium the installed Playwright
uses, refusing with one line when `uv` or `npm` is not on the PATH.
`make widget` SHALL install the npm workspace from its lock and build every
member's bundle. `make lint` SHALL run black's check and flake8 with a line
length of 89 over the framework's sources and tests and every other package's
`machinome/` from the framework's directory, both always, and fail when
either does. `make docs` SHALL build the browser viewer's bundle, then build
the manual with warnings as errors from an environment of its own at the
root's `.docs-venv/`, made when absent, into which it installs
`packages/machinome/docs/requirements.txt` alone, reading every page, into
`packages/machinome/docs/_build/html`; the manual takes the repository's
viewer, which the framework finds through its seam.

#### Scenario: The manual is built as Read the Docs builds it

- **WHEN** `make docs` runs on a clone after `make sync`
- **THEN** the viewer's bundle is built, the environment the manual builds in
  holds what `packages/machinome/docs/requirements.txt` names and nothing of
  the workspace, the build fails on any warning, and the pages are written to
  `packages/machinome/docs/_build/html`

#### Scenario: The lint reports both tools

- **WHEN** black would reformat a file and flake8 reports a line
- **THEN** `make lint` prints both reports and fails

### Requirement: `make test` runs every package's tests, or one package's

`make test PKG=<package>` SHALL run the tests of that package: for the
framework, the viewer's bundle built and then the suite, `python -m pytest`
from `packages/machinome/`; for a product, `python -m pytest` from its
directory, preceded for the browser viewer by its widget's type check, tests
and bundle, and followed for the movie by the Node projects CI runs.
`make test` with no `PKG` SHALL run every package of the tested list, one
after another, stopping at the first that fails. For a package with no tests
of its own it SHALL fail, saying that the framework's suite tests it; for a
name that is not a package it SHALL fail, listing the packages.

#### Scenario: A contributor runs one product's tests

- **WHEN** a contributor runs `make test PKG=machinome-mechanics`
- **THEN** pytest runs from `packages/machinome-mechanics/` on the
  workspace's environment and nothing else runs

#### Scenario: A contributor names an extension package

- **WHEN** a contributor runs `make test PKG=machinome-engine-brep`
- **THEN** it fails, saying that the package keeps no tests of its own and
  that `make test PKG=machinome` tests it

#### Scenario: One package's tests fail

- **WHEN** `make test` runs and a package's tests fail
- **THEN** the packages after it in the list are not run and the target fails

### Requirement: `scripts/check-dist --out` keeps the archives it proved

`scripts/check-dist` SHALL accept `--out DIR`. With it, the script SHALL
refuse, before it builds anything, a `DIR` that exists and is not an empty
folder; and once every member's archives are built, checked with `twine check
--strict`, installed and smoked, it SHALL copy every sdist and wheel it built,
flat, into `DIR`, refusing two archives of one name, and print each. When any
check fails, it SHALL keep nothing. Without the option it SHALL keep nothing,
as before. It SHALL upload nothing either way.

#### Scenario: A release's archives are kept

- **WHEN** `scripts/check-dist --out dist/v0.8.1` runs on a tree of fifteen
  members and every check passes
- **THEN** `dist/v0.8.1` holds thirty archives, the sdist and the wheel of
  each member, flat, the bytes the script checked and smoked, and
  `twine check --strict dist/v0.8.1/*` passes

#### Scenario: The folder already holds archives

- **WHEN** `scripts/check-dist --out DIR` runs and `DIR` holds a file
- **THEN** it fails naming `DIR` before building any archive

#### Scenario: A smoke fails

- **WHEN** a member's build, check or smoke fails under `--out DIR`
- **THEN** the script fails and `DIR` is not created

### Requirement: A release is built by `make dist` and uploaded by `make upload` alone

`make dist` SHALL refuse outside a Git checkout and when `git status` reports
a change or an untracked file, naming them; otherwise it SHALL run
`scripts/check-dist --out dist/v<version>` on a copy of the checked-out commit
outside the repository, so the folder holds the archives of that commit and
of nothing the checkout ignores, `<version>` being `current_version`.
`make upload` SHALL upload with twine every archive of `dist/v<version>`, and
SHALL refuse when that folder is absent or empty. No target SHALL depend on
`dist` or on `upload`, `upload` SHALL have no prerequisite, and no recipe but
`upload`'s SHALL run `twine upload`. `make check` SHALL run `scripts/check-dist`
on the tree and then on a copy of the tracked files outside the repository,
removed afterwards, and keep no archive.

#### Scenario: The pilot builds a release

- **WHEN** `make dist` runs on a clean checkout of a commit whose
  `current_version` is 0.9.0
- **THEN** `dist/v0.9.0` holds every member's sdist and wheel built from that
  commit, checked and smoked, and nothing is uploaded

#### Scenario: The checkout holds a build of the manual

- **WHEN** `make dist` runs after `make docs` and the suite have written their
  ignored build directories into the checkout
- **THEN** no archive in `dist/v<version>` holds an entry from those
  directories

#### Scenario: A file is not committed

- **WHEN** `make dist` runs while `git status` lists a file
- **THEN** it refuses, naming the file, and builds nothing

#### Scenario: A target would upload what it built

- **WHEN** a rule of the Makefile names `dist` or `upload` as a prerequisite,
  `upload` gains a prerequisite, or a recipe other than `upload`'s runs
  `twine upload`
- **THEN** the layout test fails naming the rule

### Requirement: `make clean` removes only what the targets wrote

`make clean` SHALL remove the docs environment `.docs-venv/`, the manual's
build `packages/machinome/docs/_build/`, each `packages/*/build/` and the
widget's bundle, and SHALL NOT remove `.venv/`, an npm install, the release
folders under `dist/` or a tracked file. Every path it removes SHALL be one Git
ignores.

#### Scenario: The cleaned paths are all ignored

- **WHEN** the layout test reads the paths `make clean` removes
- **THEN** each is ignored by the repository's `.gitignore` files, none is
  `.venv`, `node_modules` or `dist`, and the test fails naming any other

### Requirement: CI calls the Makefile's targets

The CI workflow SHALL keep its setup steps (the checkout, OpenSCAD, uv and the
workspace synced from its lock with `uv sync --locked`, Node, Chromium) and
run the repository's steps through the Makefile at the root: the `lint` job
`make lint`; the `test` job `make widget` and, after Chromium, `make test`;
the `browser-snapshot` job `make widget` before its end-to-end capture; the
`docs` job `make docs`, with no Node and no workspace; the `dist` job, after
`test` and `docs`, `make check`; and the job of a tag `make dist` after
checking that the tag is `v` followed by `make version`'s output. No job SHALL
spell a command a target runs.

#### Scenario: A job spells a command of a target

- **WHEN** a job of the workflow runs flake8, black, Sphinx, coverage,
  `scripts/check-dist`, twine, `pip install`, an npm command or pytest
  itself, the browser-snapshot capture excepted
- **THEN** the layout test fails naming the job and the command

#### Scenario: A tag is pushed

- **WHEN** the tag `v0.9.0` is pushed and `make version` prints 0.9.0
- **THEN** the tag's job runs `make dist` and attaches `dist/v0.9.0`'s
  archives to the tag's GitHub release, and uploads nothing to a package
  index

