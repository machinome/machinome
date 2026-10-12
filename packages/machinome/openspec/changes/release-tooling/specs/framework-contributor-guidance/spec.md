## MODIFIED Requirements

### Requirement: The contributor guide states the monorepo's development setup

The contributor guide, `CONTRIBUTING.rst` at the repository root, SHALL
state the development install from the root of a clone as `make sync` (the
uv workspace's sync, the npm workspace's install and Chromium), and, for a
contributor without uv, the editable install in compat mode of every package
directory under `packages/`, the framework's with its `dev` extra; SHALL
state the repository's steps as the root Makefile's targets, `make test`
with and without `PKG=`, `make lint`, `make docs`, `make widget` and
`make check`, and a release's as `make bump VERSION=X.Y.Z`, `make dist` and
`make upload`; SHALL state that the framework's suite runs from its
directory `packages/machinome/`, where pytest runs a single test file and
the OpenSpec command runs, and that `make test PKG=<product>` runs the
mechanics helpers' tests from their own directory
`packages/machinome-mechanics/`, the browser viewer's from
`packages/machinome-viewer/` and the skills package's from
`packages/machinome-skills/`; SHALL state that Node.js 22 or newer and npm
build and test the viewer's widget, installed by one `npm ci` at the root,
which `make sync` and `make widget` run, and that the viewer's browser tests
need Chromium for the installed Playwright; and every link it makes into the
repository SHALL resolve from the root. The contributor briefing SHALL say
once that the paths it names are relative to `packages/machinome/`.

#### Scenario: A contributor sets up a clone

- **WHEN** a contributor follows `CONTRIBUTING.rst` from a fresh clone
- **THEN** it tells them to run `make sync` from the clone's root and
  `make test` to run the tests, and each link it makes into the repository
  opens a file that exists

#### Scenario: A contributor installs without uv

- **WHEN** a contributor without uv follows `CONTRIBUTING.rst`
- **THEN** the pip command it gives installs `packages/machinome-engine-brep`,
  `packages/machinome-engine-mesh`, `packages/machinome-node-cadquery`,
  `packages/machinome-node-build123d`, `packages/machinome-node-step`,
  `packages/machinome-node-molejo`, `packages/machinome-node-openscad`,
  `packages/machinome-node-solid2`, `packages/machinome-node-jscad`,
  `packages/machinome-node-stl`, `packages/machinome-node-freecad`,
  `packages/machinome-viewer`, `packages/machinome-mechanics`,
  `packages/machinome-skills` and
  `packages/machinome` with its `dev` extra, editable with
  `editable_mode=compat`, and names no tox environment or requirements file

#### Scenario: A link of the guide stops resolving

- **WHEN** a relative link in `CONTRIBUTING.rst` names a path that does not
  exist under the repository root
- **THEN** the layout test fails naming the link

#### Scenario: A contributor reads the briefing's layout

- **WHEN** a contributor reads the contributor briefing's layout section
- **THEN** it says that its paths are relative to `packages/machinome/`

#### Scenario: A contributor runs the mechanics helpers' tests

- **WHEN** a contributor looks in `CONTRIBUTING.rst` for how to run the
  mechanics helpers' tests
- **THEN** it says `make test PKG=machinome-mechanics`, which runs pytest
  from `packages/machinome-mechanics/`, and the core's suite run from
  `packages/machinome/` does not collect them

#### Scenario: A contributor builds and tests the browser viewer

- **WHEN** a contributor looks in `CONTRIBUTING.rst` for how to work on the
  browser viewer
- **THEN** it names Node.js 22 or newer and npm, `npm ci` at the repository
  root, which `make sync` and `make widget` run, `make test
  PKG=machinome-viewer`, which runs the widget's type check, tests and build
  from the root and `python -m pytest` from `packages/machinome-viewer/`,
  and the Chromium `make sync` installs for its browser tests, and the
  core's suite run from `packages/machinome/` does not collect the viewer's
  tests

#### Scenario: The CI builds the widget before the suite

- **WHEN** the CI's test job runs
- **THEN** it installs Node and runs `make widget`, which installs the npm
  workspace at the root and builds the widget's bundle, and installs
  Chromium, both before `make test`, whose rule for the viewer type-checks,
  tests and builds the widget before the viewer's Python tests, and the
  layout test fails naming the step or the rule that is missing or out of
  order

#### Scenario: A contributor runs the skills package's tests

- **WHEN** a contributor looks in `CONTRIBUTING.rst` for how to run the
  skills package's tests
- **THEN** it says `make test PKG=machinome-skills`, which runs pytest from
  `packages/machinome-skills/`, and the core's suite run from
  `packages/machinome/` does not collect them
