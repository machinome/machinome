## MODIFIED Requirements

### Requirement: Distributions carry the built frontends

Source distributions and wheels of `machinome-viewer` SHALL contain the
built viewer bundle and the pages the package authors over it: the
standalone export page and the development page. The bundle SHALL be the
only built frontend: creating a source distribution SHALL build it, and
creating a wheel SHALL build it when the checkout does not already contain
its output OR when the output it contains is older than the sources it is
built from, keeping only a bundle that is current with them. The pages
SHALL be carried as they are written, needing no build step of their own.
Installing either distribution SHALL need no npm. A wheel SHALL NOT carry
the toolchain that bundles a model's app (its helper's sources and its
build script), as it carries none of the bundle's sources.

An export directory SHALL keep carrying exactly two files of the viewer's
beside the document, its models and, where the model has one, its app's
files — the standalone page and the one bundle — so a framework copying an
export copies the same two names it copies today.

#### Scenario: A source distribution is created

- **WHEN** a source distribution is built from a checkout with no built
  bundle
- **THEN** the bundle is built during packaging and is present in the
  distribution beside both pages

#### Scenario: A wheel is created from a checkout that already built the viewer

- **WHEN** a wheel is built from a checkout containing a built bundle that
  is current with its sources
- **THEN** packaging does not rebuild it, runs no second frontend build,
  and the wheel contains that bundle and both pages

#### Scenario: A wheel is created from a checkout whose bundle is stale

- **WHEN** a wheel is built from a checkout whose widget sources are newer
  than its built bundle
- **THEN** packaging rebuilds the bundle before the wheel is assembled, and
  the wheel carries a bundle built from those sources rather than the older
  one the checkout held

#### Scenario: An export directory is published

- **WHEN** a maker publishes an export directory
- **THEN** it carries exactly the standalone page and the one bundle of the
  viewer's, and the layout the page selects needs no further file of the
  viewer's

## ADDED Requirements

### Requirement: A model's app is bundled only where the viewer's toolchain is present

The web viewer SHALL bundle a model's app only where its JavaScript toolchain
is present: a source checkout of the repository whose JavaScript dependencies
are installed. React and React DOM SHALL be dependencies the widget declares,
at exact versions, and SHALL be installed by the workspace's ordinary
install; they SHALL NOT enter the viewer's own bundle. A viewer installed
without the toolchain SHALL refuse to bundle an app, saying that in this
release an app is bundled only from a source checkout with its JavaScript
dependencies installed; a checkout whose dependencies are absent SHALL
refuse naming the ones missing and the command that installs them at the
workspace's root. Neither SHALL install anything.

#### Scenario: An installed viewer is asked to bundle an app

- **WHEN** a viewer installed from its wheel is asked to bundle a model's
  app
- **THEN** it refuses with the release's limit, and writes nothing

#### Scenario: A checkout without its dependencies

- **WHEN** a source checkout whose workspace has not installed React is
  asked to bundle an app
- **THEN** it refuses naming React and `npm ci` at the workspace's root, and
  installs nothing

#### Scenario: The viewer's bundle carries no React

- **WHEN** the viewer's bundle is built in a checkout that has React
  installed
- **THEN** the bundle contains no part of React
