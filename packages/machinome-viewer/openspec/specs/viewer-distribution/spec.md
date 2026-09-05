# Viewer Distribution Specification

## Purpose

How the viewer is delivered and how a framework finds it: the `solid-node-viewer`
distribution carries the built frontends, exposes one lookup and three
commands, and is installed beside solid-node as its optional `viewer` extra.
Rewritten from solid-node's `viewer-distribution` baseline when the viewer
became this package.

Code: `pyproject.toml`, `solid_node_viewer/bundle.py`,
`solid_node_viewer/packaging.py`, `solid_node_viewer/cli.py`.

## Requirements

### Requirement: Distributions carry the built frontends

Source distributions and wheels of `solid-node-viewer` SHALL contain the
built viewer bundle, the standalone export page and the built development
app. Creating a source distribution SHALL build both frontends; creating a
wheel SHALL build a frontend only when the checkout does not already contain
its output, and SHALL keep an existing one. Installing either distribution
SHALL need no npm.

#### Scenario: A source distribution is created

- **WHEN** a source distribution is built from a checkout with no built
  frontends
- **THEN** both are built during packaging and are present in the
  distribution

#### Scenario: A wheel is created from a checkout that already built the viewer

- **WHEN** a wheel is built from a checkout containing a built bundle
- **THEN** packaging does not rebuild it and the wheel contains that bundle

### Requirement: The package is licensed and versioned as one

The distribution SHALL declare `AGPL-3.0-only`, and the bundle it carries
SHALL open with a banner naming that licence, the package version, the
declared viewer API version and the source repository, and retaining the
notices of the libraries it bundles. The Python package, the widget's
`package.json` and the changelog SHALL declare one version.

#### Scenario: A conveyed bundle names its source

- **WHEN** a maker publishes an export directory or a host serves the bundle
- **THEN** the bundle's first lines name AGPL-3.0-only, the version, the API
  version and the repository the source can be obtained from

### Requirement: A framework finds the installed viewer through one entry point

The distribution SHALL register the `solid_node.viewer` entry point group
with one entry, `bundle`, resolving to a function that returns the absolute
`path` of the installed bundle, the absolute `index` of the standalone
export page, the integer `apiVersion` the widget declares and the package
`version`. Resolving it SHALL import only the standard library — no browser
bundle, no web framework — and SHALL raise, with the remedy, when the
installation carries no built bundle, so a caller never receives a path that
does not exist. `solid-node-viewer describe` SHALL print the same mapping as
one JSON object on standard output, or print nothing there, report the
remedy on standard error and exit non-zero when there is no bundle.

#### Scenario: A framework resolves the viewer without importing it

- **WHEN** solid-node loads the `solid_node.viewer` entry point and calls it
- **THEN** it obtains an existing absolute bundle path, the export page and
  the declared API version, having imported nothing of the viewer's
  rendering, serving or capturing code

#### Scenario: A program asks the command line

- **WHEN** a program runs `solid-node-viewer describe` against an
  installation with a built bundle
- **THEN** it parses one JSON object carrying the path, index, API version
  and version, and the process exits zero

#### Scenario: An installation without a built bundle

- **WHEN** the entry point or the command is asked in a source checkout that
  has not built the widget
- **THEN** the entry point raises and the command exits non-zero, both naming
  where a built bundle comes from, and standard output carries no result

### Requirement: Everything else is a process

Beyond the lookup, the framework SHALL use the viewer only through the
`solid-node-viewer` console script — `serve` for the development server and
`capture` for the snapshot — each run as a separate process on a directory
the framework prepared. This package SHALL NOT import `solid_node`, and its
distribution SHALL NOT depend on solid-node.

#### Scenario: The two packages install into one environment

- **WHEN** `pip install "solid-node[viewer]"` runs
- **THEN** solid-node-viewer installs beside solid-node with no dependency
  from the viewer back to the framework, and each package remains
  importable without the other
