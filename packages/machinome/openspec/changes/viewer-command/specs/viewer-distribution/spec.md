## MODIFIED Requirements

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
