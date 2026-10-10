# Framework contributor guidance

## Purpose

Define the framework-owned orientation and verification guidance provided to
machinome contributors.
## Requirements
### Requirement: Framework-owned contributor briefing
The framework SHALL provide a contributor briefing that distinguishes durable
framework orientation and verification information from shop-owned development
workflow.

#### Scenario: Contributor needs framework orientation
- **WHEN** a contributor reads the framework contributor briefing
- **THEN** it identifies the relevant framework areas and points to the
  architecture synthesis, baseline specifications, and ADRs for detailed
  records.

#### Scenario: Contributor uses a shop-managed workflow
- **WHEN** the contributor briefing is read in a shop-managed framework change
- **THEN** it does not prescribe agent lifecycle, worktree, commit, or
  publication policy.

### Requirement: Framework verification guidance
The contributor briefing SHALL explain the role of direct pytest coverage and
the meta-project test harness without relying on a developer-specific path or
assistant identity.

#### Scenario: Framework behavior needs end-to-end proof
- **WHEN** a contributor changes behavior involving node loading, rendering,
  keyframes, meshes, or the `machinome test` subprocess path
- **THEN** the briefing directs them to the meta-project harness and explains
  why paired valid and adversarial-invalid fixtures provide useful evidence.

#### Scenario: Contributor prepares local verification
- **WHEN** a contributor reads the briefing's runtime prerequisites
- **THEN** it names framework-relevant tools and environment controls without
  hard-coding a local checkout or virtualenv path.

### Requirement: The contributor guide states the monorepo's development setup

The contributor guide, `CONTRIBUTING.rst` at the repository root, SHALL
state the development install from the root of a clone (the uv workspace's
sync, and, for a contributor without uv, the editable install in compat mode
of every package directory under `packages/`, the framework's with its `dev`
extra), SHALL state that the suite, the lint and the OpenSpec command run
from the framework's directory `packages/machinome/`, and every link it
makes into the repository SHALL resolve from the root. The contributor
briefing SHALL say once that the paths it names are relative to
`packages/machinome/`.

#### Scenario: A contributor sets up a clone

- **WHEN** a contributor follows `CONTRIBUTING.rst` from a fresh clone
- **THEN** it tells them to install from the clone's root and to run the
  tests from `packages/machinome/`, and each link it makes into the
  repository opens a file that exists

#### Scenario: A contributor installs without uv

- **WHEN** a contributor without uv follows `CONTRIBUTING.rst`
- **THEN** the pip command it gives installs `packages/machinome-engine-brep`,
  `packages/machinome-engine-mesh` and `packages/machinome` with its `dev`
  extra, editable with `editable_mode=compat`, and names no tox environment
  or requirements file

#### Scenario: A link of the guide stops resolving

- **WHEN** a relative link in `CONTRIBUTING.rst` names a path that does not
  exist under the repository root
- **THEN** the layout test fails naming the link

#### Scenario: A contributor reads the briefing's layout

- **WHEN** a contributor reads the contributor briefing's layout section
- **THEN** it says that its paths are relative to `packages/machinome/`

