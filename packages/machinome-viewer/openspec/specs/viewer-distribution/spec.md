# Viewer Distribution Specification

## Purpose

How the viewer is delivered and how a framework finds it: the `machinome-viewer`
distribution carries the built frontends, exposes one lookup and three
commands, and is installed beside machinome as its optional `viewer` extra.
Rewritten from machinome's `viewer-distribution` baseline when the viewer
became this package.

Code: `pyproject.toml`, `machinome_viewer/bundle.py`,
`machinome_viewer/packaging.py`, `machinome_viewer/cli.py`.
## Requirements
### Requirement: Distributions carry the built frontends

Source distributions and wheels of `machinome-viewer` SHALL contain the
built viewer bundle and the pages the package authors over it: the
standalone export page and the development page. The bundle SHALL be the
only built frontend: creating a source distribution SHALL build it, and
creating a wheel SHALL build it when the checkout does not already contain
its output OR when the output it contains is older than the sources it is
built from, keeping only a bundle that is current with them. The pages
SHALL be carried as they are written, needing no build step of their own.
Installing either distribution SHALL need no npm.

An export directory SHALL keep carrying exactly two files beside the
document and its models — the standalone page and the one bundle — so a
framework copying an export copies the same two names it copies today.

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
- **THEN** it carries exactly the standalone page and the one bundle, and
  the layout the page selects needs no further file

### Requirement: The package is licensed and versioned as one

The distribution SHALL declare `AGPL-3.0-or-later`, and the bundle it carries
SHALL open with a banner naming that licence, the package version, the
declared viewer API version and the source repository, and retaining the
notices of the libraries it bundles. The Python package, the widget's
`package.json` and the changelog SHALL declare one version.

#### Scenario: A conveyed bundle names its source

- **WHEN** a maker publishes an export directory or a host serves the bundle
- **THEN** the bundle's first lines name AGPL-3.0-or-later, the version, the API
  version and the repository the source can be obtained from

### Requirement: A framework finds the installed viewer through one entry point

The distribution SHALL register the `machinome.viewer` entry point group
with one entry, `bundle`, resolving to a function that returns the absolute
`path` of the installed bundle, the absolute `index` of the standalone
export page, the integer `apiVersion` the widget declares, the list of
document schema versions the widget renders as `documentVersions`, and the
package `version`. Resolving it SHALL import only the standard library — no
browser bundle, no web framework — and SHALL raise, with the remedy, when
the installation carries no built bundle, so a caller never receives a path
that does not exist. `machinome-viewer describe` SHALL print the same
mapping as one JSON object on standard output, or print nothing there,
report the remedy on standard error and exit non-zero when there is no
bundle.

`apiVersion` and `documentVersions` SHALL come from the widget package's
own single declaration of each, the same declaration the bundle is built
from, so the answer a framework reads and the versions the bundle actually
refuses can never disagree. In an installation that could hold a bundle
built from an OLDER copy of that declaration, the answer SHALL be given
only after the bundle has been made current with it, so this promise holds
of the artifact and not merely of the declaration.

Any output produced by making the bundle current SHALL NOT be written to
standard output, so a caller parsing the entry point's or the command's
answer is never given a build log to parse.

#### Scenario: A framework resolves the viewer without importing it

- **WHEN** machinome loads the `machinome.viewer` entry point and calls it
- **THEN** it obtains an existing absolute bundle path, the export page and
  the declared API version, having imported nothing of the viewer's
  rendering, serving or capturing code

#### Scenario: A program asks the command line

- **WHEN** a program runs `machinome-viewer describe` against an
  installation with a built bundle
- **THEN** it parses one JSON object carrying the path, index, API version
  and version, and the process exits zero

#### Scenario: An installation without a built bundle

- **WHEN** the entry point or the command is asked in a source checkout that
  has not built the widget
- **THEN** the entry point raises and the command exits non-zero, both naming
  where a built bundle comes from, and standard output carries no result

#### Scenario: A producer asks which documents this installation reads

- **WHEN** a framework resolves the entry point, or runs
  `machinome-viewer describe`, before publishing a document
- **THEN** the answer carries the list of document schema versions this
  build renders, and that list is the same one the bundle refuses an
  unlisted version by

#### Scenario: A producer asks a checkout that just changed

- **WHEN** a framework asks a source checkout whose widget declaration and
  sources have changed since the bundle was last built
- **THEN** the list it receives is the one the bundle it is given the path
  of actually refuses by, not the one an older bundle refuses by

#### Scenario: A rebuild does not corrupt the answer

- **WHEN** `machinome-viewer describe` rebuilds a stale bundle before
  answering
- **THEN** standard output carries exactly one JSON object and nothing the
  build printed

### Requirement: Everything else is a process

Beyond the lookup, the framework SHALL use the viewer only through the
`machinome-viewer` console script, or the same program as
`python -m machinome_viewer` through the interpreter the framework runs
under — `serve` for the development server and `capture` for the snapshot —
each run as a separate process on a directory the framework prepared. This package SHALL NOT import `machinome`, and its
distribution SHALL NOT depend on machinome.

#### Scenario: The two packages install into one environment

- **WHEN** `pip install "machinome[viewer]"` runs
- **THEN** machinome-viewer installs beside machinome with no dependency
  from the viewer back to the framework, and each package remains
  importable without the other

### Requirement: A source checkout answers from a bundle built from its sources

An installation that carries the widget's sources — a checkout, a worktree,
an editable install — SHALL NOT answer for, serve, copy or package a built
bundle older than the sources it is built from. Before the entry point
answers, before the development server serves the bundle route, and before
a capture copies the bundle into its staging directory, the package SHALL
compare the built bundle against its build inputs and SHALL rebuild it when
any input is newer.

The build inputs SHALL be every file under the widget's `src/` directory,
`package.json`, `build.mjs` and `tsconfig.json`. Currency SHALL be decided
by modification time in integer nanoseconds: the bundle is stale when the
newest input's time is strictly greater than the bundle's own, and equal
times mean current. The widget's installed dependencies SHALL NOT be an
input.

An automatic rebuild SHALL run the widget's build and SHALL NOT install or
reinstall its dependencies, so an installation whose dependency directory
is shared with another checkout is never altered by a lookup. Concurrent
rebuilds SHALL be serialized so that no caller can observe a partially
written bundle, and a caller that waits for another's rebuild SHALL NOT
rebuild again.

When the bundle is stale and cannot be rebuilt — the dependencies are
absent, the build program cannot be run, or the build fails — the package
SHALL report a stale installation naming the bundle, the input that
outdates it, why the rebuild could not happen, and the remedy, and SHALL
NOT hand out, serve or copy the stale bundle. The entry point SHALL raise,
`machinome-viewer describe` SHALL print nothing on standard output and
exit non-zero, and the capture SHALL write no image.

An installation carrying no widget sources SHALL be current by definition:
it SHALL perform no scan, SHALL never rebuild, and SHALL require no npm.

#### Scenario: A checkout is asked after its sources changed

- **WHEN** the entry point or `machinome-viewer describe` is asked in a
  checkout whose widget sources are newer than its built bundle
- **THEN** the bundle is rebuilt from those sources before the answer is
  given, and the reported API version and document schema versions are the
  ones the rebuilt bundle itself carries

#### Scenario: A checkout is asked twice with nothing changed

- **WHEN** the entry point is asked again with no source touched since the
  last build
- **THEN** no rebuild runs and the answer is the same

#### Scenario: A rebuild is needed but the dependencies are absent

- **WHEN** a checkout's bundle is stale and its widget dependencies are not
  installed
- **THEN** the entry point raises and the command exits non-zero, both
  naming the stale bundle, the newer input and the install-and-build
  remedy, standard output carries no result, and no install is attempted

#### Scenario: A lookup never installs dependencies

- **WHEN** a stale bundle is rebuilt automatically
- **THEN** only the widget's build runs; no dependency install runs, and the
  widget's dependency directory is not modified

#### Scenario: Two processes ask at once

- **WHEN** two processes find the same bundle stale at the same time
- **THEN** one rebuild runs, the other waits for it and then observes a
  current bundle without rebuilding, and neither observes a partially
  written file

#### Scenario: An installed distribution is asked

- **WHEN** the entry point is asked in an installation carrying the bundle
  but no widget sources
- **THEN** it answers without scanning for sources, without rebuilding and
  without requiring npm

### Requirement: The distribution carries one Machinome viewer identity

The distribution SHALL be named `machinome-viewer`, expose the Python package
`machinome_viewer`, register `machinome.viewer`, and provide
`machinome-viewer describe|serve|capture` plus equivalent
`python -m machinome_viewer` execution. Its source repository SHALL be
`github.com/machinome/machinome-viewer`. The built bundle, standalone page,
source banner, package metadata, diagnostics and remedies SHALL use Machinome
names. It SHALL NOT install solid-node-named Python packages, entry points or
commands.

#### Scenario: The framework resolves the viewer

- **WHEN** Machinome loads the `machinome.viewer` entry point
- **THEN** it receives the installed Machinome bundle description without
  importing rendering, serving, or capture code

#### Scenario: A program asks the command line

- **WHEN** it runs `machinome-viewer describe`
- **THEN** standard output contains the same JSON mapping as the entry point

#### Scenario: A source recipient follows the bundle banner

- **WHEN** a conveyed bundle's source notice is read
- **THEN** it names the AGPL licence, package/API versions, and the
  `machinome/machinome-viewer` repository

### Requirement: The viewer remains an independent process

Machinome SHALL reach the viewer only through `machinome.viewer` lookup and
the `machinome-viewer` process commands. The viewer distribution SHALL NOT
depend on or import the `machinome` Python package.

#### Scenario: The two packages install together

- **WHEN** `pip install "machinome[viewer]"` installs both distributions
- **THEN** each package remains importable without importing the other and all
  serving or capture work crosses the process boundary

### Requirement: A play-capable distribution advertises its capability

The package's single declarations SHALL set viewer API 22 and document versions 1 through 9. The built bundle, Python entry point, and `machinome-viewer describe` command SHALL report those same values, and stale-bundle currency handling SHALL rebuild before reporting them.

API 22 SHALL supersede the earlier numeric declaration under "The viewer
declares its API version", retaining that requirement's single-declaration
and capability-reporting contract.

#### Scenario: A framework asks for viewer capabilities
- **WHEN** it resolves the entry point or invokes `describe` from this source or an installed distribution
- **THEN** it receives API 22 and document versions `[1,2,3,4,5,6,7,8,9]`, matching the bundle's loader

#### Scenario: Older documents remain supported
- **WHEN** the bundle mounts any valid document version 1 through 8
- **THEN** it retains the behavior and public handle contract of API 21 for that document

### Requirement: Installed viewer support includes retained time drives

The shipped bundle and package description SHALL consistently report viewer API
23 and supported document versions 1 through 10 after retained time-drive
execution is implemented and verified. The package, its widget and the bundle
banner SHALL all carry version 0.7.0, the version released with Machinome
0.7.0; the version number identifies the distribution and does not declare a
capability, which `apiVersion` and `documentVersions` alone declare.

API 23 supersedes earlier numeric capability declarations, including "A
play-capable distribution advertises its capability", without changing their
single-source declaration, bundle-currency or legacy-compatibility guarantees.

#### Scenario: A producer discovers matching browser support

- **WHEN** a producer asks the installed viewer for its supported versions
- **THEN** it receives API 23 and v1–10 support matching the actual bundle,
  and its version-10 Astrarium document can load and run

#### Scenario: The release pair is legible

- **WHEN** a maker runs `machinome-viewer describe` or reads the bundle banner
- **THEN** both report version 0.7.0 beside API 23 and document versions 1
  through 10, matching `pyproject.toml` and the widget's `package.json`

### Requirement: Installed viewer support identifies source-timed running

After source-timed execution is implemented and verified, the package's single
capability declarations SHALL report viewer API 24 and document versions 1–11.
The built bundle, entry point, command report, browser global and handles SHALL
agree, preserving existing bundle-currency checks. These capability numbers
supersede API 23 and the v1–10 list in "Installed viewer support includes
retained time drives"; they do not authorize a package release or rewrite
historical release claims.

#### Scenario: A producer discovers the corrected consumer

- **WHEN** a producer or host reads the installed viewer's capability report
- **THEN** it receives API 24 and supported versions 1 through 11, matching
  the actual built bundle and its source-timed execution tests

#### Scenario: Unbuilt source cannot advertise an old bundle as corrected

- **WHEN** capability metadata has changed but a source checkout's bundle is stale
- **THEN** the existing currency mechanism rebuilds it or refuses by name
  rather than reporting API 24 for a bundle that still executes endpoint chords

### Requirement: Installed viewer support identifies two-envelope Follow

After version-12 Follow execution passes producer/consumer parity and browser validation, the package's single capability declarations SHALL report viewer API 25 and document versions 1–12. The built bundle, Python entry point, command report and browser global SHALL agree; stale-bundle currency checks SHALL remain effective. This capability declaration SHALL NOT imply a new package release or revise historical release claims.

#### Scenario: Producer discovers Follow support
- **WHEN** a producer or host reads the installed viewer capability report
- **THEN** it receives API 25 and supported document versions 1 through 12 matching the actual built bundle and its Follow tests

#### Scenario: An older consumer sees the new export
- **WHEN** a version-12 Follow document is offered to a viewer whose supported versions end at 11
- **THEN** that viewer refuses the document rather than silently executing its old law or Play algorithm

#### Scenario: Source bundle is stale
- **WHEN** capability metadata has changed but a source checkout's bundle is older
- **THEN** the existing currency mechanism rebuilds it or refuses by name rather than advertising Follow for an old bundle
