# Viewer Distribution Specification

## Purpose

Distributions deliver the built reusable viewer and expose it consistently to
the CLI, static export, and documentation embedding.
## Requirements
### Requirement: An installed framework reports its viewer

The framework SHALL report, to a program that does not import it, the
filesystem path of the installed viewer bundle and the integer API version the
viewer declares, as one machine-readable result on standard output, together
with the absolute path of the viewer's standalone export page and the
installed viewer package version. The reported paths SHALL be absolute and
SHALL exist. When no viewer is installed, the framework SHALL instead report a
failure that names the remedy — installing the `viewer` extra — and SHALL
exit non-zero.

The report SHALL also carry `documentVersions`, the list of node-tree
document schema versions the installed viewer renders, so a framework channel
that is about to publish or photograph a document can ask the fact it needs
rather than infer it from an unrelated counter. A report that does not carry
the field SHALL be read as `[1, 2, 3, 4]` — the versions every viewer
released before the field existed renders — so an older viewer beside a newer
framework keeps working and is described truthfully.

#### Scenario: The report says which documents the viewer renders

- **WHEN** a program runs the framework's viewer report against an
  installation whose viewer declares the document versions it renders
- **THEN** the result carries that list beside the bundle path, the export
  page, the API version and the package version

#### Scenario: A viewer that predates the field

- **WHEN** the framework resolves an installed viewer whose report carries no
  document-version list
- **THEN** the framework treats it as rendering versions 1 to 4, and says so
  wherever it names what the viewer can read

#### Scenario: A host asks an installed framework for the viewer

- **WHEN** a program runs the framework's viewer report against an installation
  with `machinome-viewer` installed
- **THEN** it receives, on standard output, the absolute path of an existing
  bundle file, the export page, the declared viewer API version and the viewer
  package version, and the process exits zero

#### Scenario: A host asks an installation that has no bundle

- **WHEN** a program runs the viewer report against an installation without
  `machinome-viewer`
- **THEN** the process exits non-zero, standard output carries no result, and
  the message names `pip install "machinome[viewer]"`

### Requirement: One answer about the bundle across framework channels

Every framework channel that needs the web viewer (the viewer report, static
export, documentation embedding, the development viewer, the web snapshot and
the films) SHALL resolve it through the one seam, `machinome.viewer`, at its
address `machinome.viewer.web`, and SHALL name the same remedy when it is
absent: installing the `viewer` extra. Documentation embedding SHALL continue
to resolve the bundle without loading the CAD runtime.

#### Scenario: Export and documentation embedding disagree about nothing

- **WHEN** the viewer is absent and an export and a documentation build each
  report it
- **THEN** both name the same remedy

#### Scenario: A documentation build stays free of the CAD runtime

- **WHEN** a documentation build completes an export that was made without
  viewer files
- **THEN** it copies the bundle the web viewer names without importing the
  framework's CAD runtime

### Requirement: The viewer is an optional extra

The framework SHALL declare the `viewer` extra, installing the
`machinome-viewer` distribution, and the `web-snapshot` extra, installing
`machinome-viewer[snapshot]`. The framework's own dependencies SHALL NOT
include the viewer, and every framework operation that does not open, embed
or photograph through the browser viewer SHALL work in an installation
without it. Interactive development through `machinome develop` SHALL require the
viewer extra unless the caller explicitly selects the `--no-web` watch loop.

#### Scenario: A plain installation retains non-viewer operations

- **WHEN** `pip install machinome` runs without the extra, with the extras
  the project's parts need
- **THEN** building, testing, exporting without the widget, snapshotting
  through OpenSCAD with the `openscad` extra, and developing with `--no-web`
  work, while ordinary `machinome develop` fails naming the viewer extra

#### Scenario: The extra brings the interactive viewer

- **WHEN** `pip install "machinome[viewer]"` runs
- **THEN** `machinome viewer` reports the installed bundle and `machinome develop`
  opens the browser viewer by default

### Requirement: The framework resolves the Machinome viewer

The `viewer` extra SHALL install `machinome-viewer`, the repository's
distribution whose Python package is `machinome.viewer.web`, the web provider
of the seam `machinome.viewer`, and the framework SHALL find it by importing
that address and nothing else: it SHALL read no entry point to find a viewer,
and the distribution SHALL declare none in the group `machinome.viewer`. The
framework SHALL serve, capture and embed through the provider's operations in
its own process and SHALL run no program of the viewer's. Absence and
compatibility errors SHALL name `pip install "machinome[viewer]"` as the
remedy. The distribution SHALL declare no command of its own: its verbs are the
framework's `machinome viewer describe|serve|capture`, and `python -m
machinome.viewer.web` SHALL run that command, with the same parser, by the
interpreter that runs it.

#### Scenario: A host asks an installation for its viewer

- **WHEN** `machinome viewer` runs with `machinome-viewer` installed
- **THEN** it reports the installed bundle through the web viewer's provider,
  the same object `machinome viewer describe` and `python -m
  machinome.viewer.web describe` print

#### Scenario: Interactive development lacks the viewer

- **WHEN** `machinome develop` runs without `machinome-viewer`
- **THEN** it fails naming `pip install "machinome[viewer]"`

#### Scenario: The framework runs the viewer at its address

- **WHEN** `machinome develop` serves or `machinome snapshot --viewer web`
  captures
- **THEN** the work is done by `machinome.viewer.web` in the command's own
  process, no `python -m machinome.viewer.web` process is run, and no module
  named `machinome_viewer` is imported

#### Scenario: No entry point is read

- **WHEN** the installed distributions' entry points are listed
- **THEN** none is in the group `machinome.viewer`, and every channel still
  finds the web viewer

#### Scenario: The distribution installs no command

- **WHEN** the viewer's wheel is installed into an environment
- **THEN** the distribution declares no entry point in the group
  `console_scripts`, the environment holds no `machinome-viewer` executable,
  and `machinome viewer describe` and `python -m machinome.viewer.web describe`
  exit 0

