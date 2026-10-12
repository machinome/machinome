## MODIFIED Requirements

### Requirement: The contributor guide states the monorepo's development setup

The contributor guide, `CONTRIBUTING.rst` at the repository root, SHALL
state the development install from the root of a clone (the uv workspace's
sync, and, for a contributor without uv, the editable install in compat mode
of every package directory under `packages/`, the framework's with its `dev`
extra), SHALL state that the suite, the lint and the OpenSpec command run
from the framework's directory `packages/machinome/`, SHALL state that the
mechanics helpers' tests run from their own directory
`packages/machinome-mechanics/` and the skills package's from
`packages/machinome-skills/`, and every link it makes into the repository
SHALL resolve from the root. The contributor briefing SHALL say
once that the paths it names are relative to `packages/machinome/`.

#### Scenario: A contributor sets up a clone

- **WHEN** a contributor follows `CONTRIBUTING.rst` from a fresh clone
- **THEN** it tells them to install from the clone's root and to run the
  tests from `packages/machinome/`, and each link it makes into the
  repository opens a file that exists

#### Scenario: A contributor installs without uv

- **WHEN** a contributor without uv follows `CONTRIBUTING.rst`
- **THEN** the pip command it gives installs `packages/machinome-engine-brep`,
  `packages/machinome-engine-mesh`, `packages/machinome-node-cadquery`,
  `packages/machinome-node-build123d`, `packages/machinome-node-step`,
  `packages/machinome-node-molejo`, `packages/machinome-node-openscad`,
  `packages/machinome-node-solid2`, `packages/machinome-node-jscad`,
  `packages/machinome-node-stl`, `packages/machinome-node-freecad`,
  `packages/machinome-mechanics`, `packages/machinome-skills` and
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
- **THEN** it says to run pytest from `packages/machinome-mechanics/`, and
  the core's suite run from `packages/machinome/` does not collect them

#### Scenario: A contributor runs the skills package's tests

- **WHEN** a contributor looks in `CONTRIBUTING.rst` for how to run the
  skills package's tests
- **THEN** it says to run pytest from `packages/machinome-skills/`, and the
  core's suite run from `packages/machinome/` does not collect them
